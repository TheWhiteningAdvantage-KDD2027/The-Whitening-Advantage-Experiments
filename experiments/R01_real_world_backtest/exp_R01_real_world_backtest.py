#!/usr/bin/env python3
"""
==========================================================================
R01 — REAL WORLD BACKTEST (FirstRate Data / In-The-Wild)
Author: The-Whitening-Advantage-Experiments
Target: KDD 2027
==========================================================================
"""

import sys
from pathlib import Path
import argparse
import time

# --- STRICT DETERMINISM INJECTION ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
from experiments.common.fair_env import (
    enforce_strict_determinism,
    verify_hash_seed,
    log_environment,
)

# The bootstrap must run before NumPy is loaded, which forbids using argparse here
# (importing it is harmless, but the module-level import block below is not). The
# flag is therefore read directly from sys.argv; argparse re-parses it later and
# remains the single source of truth for every other option.
_LEGACY_BLAS = "--legacy-blas" in sys.argv
enforce_strict_determinism(legacy_blas=_LEGACY_BLAS)

from experiments.common.fair_harness import (
    disable_pandas_multithreading, 
    setup_logging, 
    compute_sha256, 
    save_fair_csv
)

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from statsmodels.stats.diagnostic import acorr_ljungbox
import warnings
import random
import logging

disable_pandas_multithreading()
warnings.filterwarnings("ignore")

# --- DIRECTORY SETUP ---
DATA_DIR = BASE_DIR / "data"
RAW_FIRSTRATE_DIR = DATA_DIR / "firstrate_etf"
DERIVED_FIRSTRATE_DIR = DATA_DIR / "derived_firstrate"
R01_DIR = BASE_DIR / "results" / "R01_real_world_backtest"
DATA_OUT_DIR = R01_DIR / "data"
FIG_OUT_DIR = R01_DIR / "figures"
TAB_OUT_DIR = R01_DIR / "tables"
LOG_DIR = BASE_DIR / "logs" / "R01_real_world_backtest"

for d in [RAW_FIRSTRATE_DIR, DERIVED_FIRSTRATE_DIR, DATA_OUT_DIR, FIG_OUT_DIR, TAB_OUT_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

TICKERS = ['SPY', 'PFF', 'VNQ', 'BWX']

# --- PRIMITIVES SCIENTIFIQUES (Strict verbatim enforcement) ---
def _garch_nll(params, eps, var_emp):
    alpha, beta = params
    omega = var_emp * (1.0 - alpha - beta)
    n = len(eps)
    sigma2 = np.zeros(n)
    sigma2[0] = var_emp
    for t in range(1, n):
        sigma2[t] = omega + alpha * eps[t-1]**2 + beta * sigma2[t-1]
        if sigma2[t] < 1e-10: sigma2[t] = 1e-10
    nll = 0.5 * np.sum(np.log(sigma2) + (eps**2) / sigma2)
    return nll

def fit_garch_qmle(eps_warmup):
    var_emp = np.var(eps_warmup)
    init = [0.05, 0.90]
    bounds = [(1e-6, 0.5), (1e-6, 0.99)]
    constraints = {'type': 'ineq', 'fun': lambda x: 0.999 - (x[0] + x[1])}
    try:
        res = minimize(_garch_nll, init, args=(eps_warmup, var_emp), 
                       method='SLSQP', bounds=bounds, constraints=constraints,
                       tol=1e-8, options={'maxiter': 1000, 'ftol': 1e-8, 'eps': 1e-5, 'disp': False})
        a, b = res.x if res.success else init
        a, b = round(float(a), 6), round(float(b), 6)
        converged = res.success and max(abs(a - 0.05), abs(b - 0.90)) > 1e-6
        if not converged:
            a, b = init
        return (var_emp * (1.0 - a - b), a, b), converged
    except (TypeError, np.linalg.LinAlgError) as e:
        return (var_emp * (1.0 - 0.05 - 0.90), 0.05, 0.90), False

def compute_gamma_exact(alpha, beta):
    phi = alpha + beta
    if phi >= 1.0: return np.inf
    denom = 1 - 2 * alpha * beta - beta**2
    if denom <= 0: return (1 + phi) / (1 - phi)
    rho1 = alpha * (1 - beta * phi) / denom
    return max(1.0, 1 + 2 * rho1 / (1 - phi))

def strict_cusum(stream, delta_P, threshold):
    S = 0.0
    for t in range(len(stream)):
        S = max(0.0, S + stream[t] - delta_P)
        if S > threshold: return t
    return -1

def get_multiple_alarms(stream, delta_P, threshold, bilateral=False):
    alarms = []
    idx = 0
    while idx < len(stream):
        remaining = stream[idx:]
        pos_alarm = strict_cusum(remaining, delta_P, threshold)
        if bilateral:
            neg_alarm = strict_cusum(-remaining, delta_P, threshold)
        else:
            neg_alarm = -1
        valid_alarms = [a for a in [pos_alarm, neg_alarm] if a != -1]
        if not valid_alarms:
            break
        first_alarm = min(valid_alarms)
        actual_idx = idx + first_alarm
        alarms.append(actual_idx)
        idx = actual_idx + 1
    return alarms

def get_cusum_trajectory(stream, delta_P):
    S_traj = np.zeros(len(stream))
    S = 0.0
    for t in range(len(stream)):
        S = max(0.0, S + stream[t] - delta_P)
        S_traj[t] = S
    return S_traj

def wilson_ci(p_hat, n, z=1.96):
    if n == 0: return 0.0, 0.0
    center = (p_hat + z**2 / (2*n)) / (1 + z**2 / n)
    half_width = z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return max(0.0, min(1.0, center - half_width)), max(0.0, min(1.0, center + half_width))

# --- I/O & PIPELINE ---
def ingest_firstrate(ticker: str, logger: logging.Logger) -> pd.DataFrame:
    file_path = RAW_FIRSTRATE_DIR / f"{ticker}_full_1min_adjsplitdiv.txt"
    if not file_path.exists():
        logger.error(f"[FATAL] Raw file {file_path} missing.")
        logger.error("FirstRate intraday data is strictly non-redistributable and must be provided locally.")
        logger.error("To run without local files, use derived data: --stage analyse")
        logger.error("To use public data, execute: --data-source yfinance")
        sys.exit(1)
        
    logger.info(f"Hashing raw file {file_path.name}: {compute_sha256(file_path)}")
    try:
        df = pd.read_csv(file_path, header=None)
        if df.shape[1] == 6:
            df.columns = ['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume']
        elif df.shape[1] == 5:
            df.columns = ['DateTime', 'Open', 'High', 'Low', 'Close']
        else:
            df.columns = ['DateTime', 'Open', 'High', 'Low', 'Close'] + [f"Col_{i}" for i in range(5, df.shape[1])]
            
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        df = df.set_index('DateTime')
        df = df.between_time('09:30', '16:00')
        
        daily_rows = []
        for date, group in df.groupby(df.index.date):
            if len(group) >= 50:
                daily_rows.append({'Date': date, 'Close': group['Close'].iloc[-1]})
                
        df_daily = pd.DataFrame(daily_rows).set_index('Date')
        df_daily.index = pd.to_datetime(df_daily.index)
        df_daily = df_daily[~df_daily.index.duplicated(keep='first')].sort_index()
        df_daily['log_ret'] = np.log(df_daily['Close'] / df_daily['Close'].shift(1))
        df_daily = df_daily.dropna()
        
        derived_path = DERIVED_FIRSTRATE_DIR / f"R01_daily_{ticker}.csv"
        df_daily.to_csv(derived_path)
        logger.info(f"Derived data saved to {derived_path.name}")
        return df_daily
        
    except (FileNotFoundError, pd.errors.ParserError, ValueError) as e:
        logger.error(f"[FATAL] Ingestion failed for {ticker}: {e}")
        sys.exit(1)

def load_yfinance(ticker: str, logger: logging.Logger) -> pd.DataFrame:
    import yfinance as yf
    logger.info(f"Downloading {ticker} via yfinance...")
    df = yf.download(ticker, start="2000-01-01", end="2025-07-08", progress=False, auto_adjust=False)
    if df.empty:
        logger.error(f"[FATAL] YFinance fallback failed: No data for {ticker}")
        sys.exit(1)
        
    if isinstance(df.columns, pd.MultiIndex):
        close = df['Adj Close'][ticker] if 'Adj Close' in df.columns.levels[0] else df['Close'][ticker]
    else:
        close = df['Adj Close'] if 'Adj Close' in df.columns else df['Close']
        
    df_daily = pd.DataFrame({'Close': close})
    if getattr(df_daily.index, 'tz', None) is not None:
        df_daily.index = df_daily.index.tz_localize(None)
    df_daily.index = pd.to_datetime(df_daily.index.date)
    df_daily = df_daily[~df_daily.index.duplicated(keep='first')].sort_index()
    df_daily['log_ret'] = np.log(df_daily['Close'] / df_daily['Close'].shift(1))
    return df_daily.dropna()

def run_experiment(args):
    sfx_parts = []
    if args.data_source == "yfinance":
        sfx_parts.append("yfinance")
    if args.legacy_blas:
        sfx_parts.append("legacy_blas")

    sfx = "_" + "_".join(sfx_parts) if sfx_parts else ""
    log_file = LOG_DIR / f"exp_R01_real_world_backtest{sfx}.log"
    logger = setup_logging(log_file, "R01")
    
    verify_hash_seed(logger)
    log_environment(logger, ["numpy", "pandas", "scipy", "statsmodels", "matplotlib", "yfinance"])
    
    if args.data_source == "yfinance":
        logger.info("[YFINANCE MODE] USING PUBLIC DATA. FIRSTRATE DATA IS NOT UTILIZED.")
    
    random.seed(42)
    np.random.seed(42)
    
    data_dict = {}
    for tk in TICKERS:
        if args.data_source == "yfinance":
            df = load_yfinance(tk, logger)
        else:
            derived_path = DERIVED_FIRSTRATE_DIR / f"R01_daily_{tk}.csv"
            if args.stage in ["ingest", "all"]:
                df = ingest_firstrate(tk, logger)
            else:
                if not derived_path.exists():
                    logger.error(f"[FATAL] Derived file {derived_path} missing.")
                    logger.error("Run with --stage ingest to generate derived files, or use yfinance.")
                    sys.exit(1)
                logger.info(f"Hashing derived file {derived_path.name}: {compute_sha256(derived_path)}")
                df = pd.read_csv(derived_path, index_col='Date', parse_dates=True)
                
        data_dict[tk] = df
        logger.info(f"[{tk}] Data points: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')} ({len(df)} days)")
        
    models_info = {}
    models_out = []
    
    logger.info("--- PHASE 1: WARM-UP & GATEKEEPER (2018-2019) ---")
    for tk in TICKERS:
        df = data_dict[tk]
        df_wu = df.loc["2018-01-02":"2019-12-31"]
        r_wu = df_wu['log_ret'].values
        
        mu_f = np.mean(r_wu**2)
        sig_f = np.std(r_wu**2)
        q_hat = np.mean(r_wu > 0)
        
        s_wu = (r_wu > 0).astype(float) - q_hat
        p_val = acorr_ljungbox(s_wu, lags=[20], return_df=True)['lb_pvalue'].iloc[0]
        concept_valid = (p_val >= 0.05)
        
        eps_wu = r_wu - np.mean(r_wu)
        (w, a, b), converged = fit_garch_qmle(eps_wu)
        gamma = compute_gamma_exact(a, b)
        sig2_unc = w / (1 - a - b)
        
        models_info[tk] = {
            'mu_f': mu_f, 'sig_f': sig_f, 'q_hat': q_hat,
            'gamma': gamma, 'sig_unc': np.sqrt(sig2_unc),
            'concept_valid': concept_valid, 'lb_pvalue_warmup': p_val,
        }
        
        models_out.append({
            'data_source': args.data_source, 'Ticker': tk, 'omega': w, 'alpha': a, 'beta': b,
            'gamma_hat': gamma, 'sigma_unc': np.sqrt(sig2_unc), 'q_hat': q_hat,
            'lb_pvalue_warmup': p_val, 'qmle_converged': converged,
            'data_start': df.index[0].strftime('%Y-%m-%d'), 'data_end': df.index[-1].strftime('%Y-%m-%d'),
            'n_days': len(df), 'n_truncated_windows': 0
        })
    
    save_fair_csv(pd.DataFrame(models_out), DATA_OUT_DIR / f"R01_garch_models{sfx}.csv")
    
    logger.info("--- PHASE 2: PANEL A - COVID-19 VARIANCE SHOCK (SPY) ---")
    df_spy = data_dict['SPY']
    df_covid = df_spy.loc["2020-01-02":"2020-12-31"].copy()
    r_cov = df_covid['log_ret'].values
    m_spy = models_info['SPY']
    
    e_cov = (r_cov**2 - m_spy['mu_f']) / m_spy['sig_f']
    al_idx_data = get_multiple_alarms(e_cov, delta_P=0.5, threshold=65*m_spy['gamma'], bilateral=False)
    dates_data = df_covid.index[al_idx_data]
    
    dates_concept = []
    if m_spy['concept_valid']:
        s_cov = (r_cov > 0).astype(float) - m_spy['q_hat']
        al_idx_conc = get_multiple_alarms(s_cov, delta_P=0.1, threshold=10, bilateral=True)
        dates_concept = df_covid.index[al_idx_conc]
        
    S_over_thr_Data = get_cusum_trajectory(e_cov, 0.5) / (65 * m_spy['gamma'])
    if m_spy['concept_valid']:
        S_over_thr_Concept_pos = get_cusum_trajectory(s_cov, 0.1) / 10.0
        S_over_thr_Concept_neg = get_cusum_trajectory(-s_cov, 0.1) / 10.0
        S_over_thr_Concept = np.maximum(S_over_thr_Concept_pos, S_over_thr_Concept_neg)
    else:
        S_over_thr_Concept = np.zeros(len(e_cov))

    df_traj = pd.DataFrame({
        'data_source': args.data_source, 'Date': df_covid.index,
        'S_over_thr_Data': S_over_thr_Data, 'S_over_thr_Concept': S_over_thr_Concept
    })
    save_fair_csv(df_traj, DATA_OUT_DIR / f"R01_covid_trajectories{sfx}.csv")
    
    out_a = []
    for d in dates_data: out_a.append({'data_source': args.data_source, 'Pipeline': 'Data', 'Date': d, 'Close': df_covid.loc[d, 'Close']})
    for c in dates_concept: out_a.append({'data_source': args.data_source, 'Pipeline': 'Concept', 'Date': c, 'Close': df_covid.loc[c, 'Close']})
    
    df_out_a = pd.DataFrame(out_a, columns=['data_source', 'Pipeline', 'Date', 'Close'])
    if df_out_a.empty:
        df_out_a = pd.DataFrame([{'data_source': args.data_source, 'Pipeline': float("nan"), 'Date': pd.NaT, 'Close': np.nan, 'n_alarms': 0}])
        logger.info("Concept alarms in 2020: 0")
    else:
        df_out_a['n_alarms'] = len(df_out_a)
    save_fair_csv(df_out_a, DATA_OUT_DIR / f"R01_covid_alarms{sfx}.csv")
    
    logger.info("--- PHASE 2.5: SYMMETRY 2020 ---")
    sym_2020 = []
    for tk in TICKERS:
        df_tk_cov = data_dict[tk].loc["2020-01-02":"2020-12-31"]
        if not df_tk_cov.empty:
            r_tk_cov = df_tk_cov['log_ret'].values
            q_hat_2020 = np.mean(r_tk_cov > 0)
            s_cov_tk = (r_tk_cov > 0).astype(float) - q_hat_2020
            p_val_2020 = acorr_ljungbox(s_cov_tk, lags=[20], return_df=True)['lb_pvalue'].iloc[0]
            sym_2020.append({'data_source': args.data_source, 'Ticker': tk, 'q_hat_2020': q_hat_2020, 'lb_pvalue_2020': p_val_2020, 'n_days_2020': len(df_tk_cov)})
    save_fair_csv(pd.DataFrame(sym_2020), DATA_OUT_DIR / f"R01_symmetry_2020{sfx}.csv")

    logger.info("--- PHASE 3: PANEL B - SEMI-REAL INJECTIONS (2021-2023) ---")
    panel_b_stats, placebo_stats, magnitude_stats = [], [], []
    DELTAS = [0.0, 0.5, 1.0, 1.5]
    
    for tk in TICKERS:
        df = data_dict[tk]
        m = models_info[tk]
        df_period = df.loc["2021-01-01":"2023-12-31"]
        onsets = df_period.groupby([df_period.index.year, df_period.index.month]).head(1).index
        n_onsets = len(onsets)
        
        results_by_delta = {d: {'data_alarms': [], 'concept_alarms': []} for d in DELTAS}
        for onset in onsets:
            idx = df.index.get_loc(onset)
            df_wu = df.iloc[idx-250 : idx]
            df_test = df.iloc[idx : idx+250]
            
            mu_loc = df_wu['log_ret'].pow(2).mean()
            sig_loc = max(df_wu['log_ret'].pow(2).std(), 1e-8)
            q_loc = (df_wu['log_ret'] > 0).mean()
            
            for delta_f in DELTAS:
                r_test = df_test['log_ret'].values + delta_f * m['sig_unc']
                e_test = (r_test**2 - mu_loc) / sig_loc
                d_al = strict_cusum(e_test, 0.5, 65*m['gamma'])
                if d_al != -1: results_by_delta[delta_f]['data_alarms'].append(d_al)
                    
                if m['concept_valid']:
                    s_test = (r_test > 0).astype(float) - q_loc
                    c_al_pos = strict_cusum(s_test, 0.1, 10)
                    c_al_neg = strict_cusum(-s_test, 0.1, 10)
                    valid_c = [x for x in (c_al_pos, c_al_neg) if x != -1]
                    if valid_c: results_by_delta[delta_f]['concept_alarms'].append(min(valid_c))
        
        for delta_f in DELTAS:
            add_d = results_by_delta[delta_f]['data_alarms']
            add_c = results_by_delta[delta_f]['concept_alarms']
            
            rate_d = len(add_d) / n_onsets
            ci_low_d, ci_high_d = wilson_ci(rate_d, n_onsets)
            med_d = np.median(add_d) if len(add_d) > 0 else np.nan
            add_mean_d = np.mean(add_d) if len(add_d) > 0 else np.nan
            sem_d = (np.std(add_d, ddof=1) / np.sqrt(len(add_d))) if len(add_d) > 1 else 0.0
            
            if delta_f == 0.0:
                placebo_stats.append({'data_source': args.data_source, 'ETF': tk, 'Pipeline': 'Data', 'AlarmRate': rate_d, 'CI_low': ci_low_d, 'CI_high': ci_high_d, 'N_alarms': len(add_d), 'MedianDelay': med_d})
            else:
                magnitude_stats.append({'data_source': args.data_source, 'ETF': tk, 'DeltaFactor': delta_f, 'Pipeline': 'Data', 'DetRate': rate_d, 'CI_low': ci_low_d, 'CI_high': ci_high_d, 'ADD': add_mean_d, 'SEM': sem_d})
            
            if delta_f == 1.5:
                panel_b_stats.append({'data_source': args.data_source, 'ETF': tk, 'Pipeline': 'Data', 'DetRate': rate_d, 'ADD': add_mean_d, 'SEM': sem_d})
                
            if m['concept_valid']:
                rate_c = len(add_c) / n_onsets
                ci_low_c, ci_high_c = wilson_ci(rate_c, n_onsets)
                med_c = np.median(add_c) if len(add_c) > 0 else np.nan
                add_mean_c = np.mean(add_c) if len(add_c) > 0 else np.nan
                sem_c = (np.std(add_c, ddof=1) / np.sqrt(len(add_c))) if len(add_c) > 1 else 0.0
                
                if delta_f == 0.0:
                    placebo_stats.append({'data_source': args.data_source, 'ETF': tk, 'Pipeline': 'Concept', 'AlarmRate': rate_c, 'CI_low': ci_low_c, 'CI_high': ci_high_c, 'N_alarms': len(add_c), 'MedianDelay': med_c})
                else:
                    magnitude_stats.append({'data_source': args.data_source, 'ETF': tk, 'DeltaFactor': delta_f, 'Pipeline': 'Concept', 'DetRate': rate_c, 'CI_low': ci_low_c, 'CI_high': ci_high_c, 'ADD': add_mean_c, 'SEM': sem_c})
                
                if delta_f == 1.5:
                    panel_b_stats.append({'data_source': args.data_source, 'ETF': tk, 'Pipeline': 'Concept', 'DetRate': rate_c, 'ADD': add_mean_c, 'SEM': sem_c})

    df_b = pd.DataFrame(panel_b_stats)
    save_fair_csv(df_b, DATA_OUT_DIR / f"R01_injection_summary{sfx}.csv")
    save_fair_csv(pd.DataFrame(placebo_stats), DATA_OUT_DIR / f"R01_placebo_control{sfx}.csv")
    save_fair_csv(pd.DataFrame(magnitude_stats), DATA_OUT_DIR / f"R01_magnitude_sweep{sfx}.csv")
    
    logger.info("--- GENERATING LATEX MACROS ---")
    tex_path = TAB_OUT_DIR / f"R01_claims{sfx}.tex"
    with open(tex_path, "w") as f:
        f.write("% Auto-generated by exp_R01_real_world_backtest.py -- do not edit.\n")
        
        # Models
        df_mod = pd.DataFrame(models_out).set_index('Ticker')
        for tk in TICKERS:
            f.write(f"\\newcommand{{\\ROneGammaHat{tk.capitalize()}}}{{{df_mod.loc[tk, 'gamma_hat']:.1f}}}\n")
            f.write(f"\\newcommand{{\\ROneLjungBox{tk.capitalize()}}}{{{df_mod.loc[tk, 'lb_pvalue_warmup']:.2f}}}\n")
        
        f.write(f"\\newcommand{{\\ROneGammaHatMin}}{{{df_mod['gamma_hat'].min():.1f}}}\n")
        f.write(f"\\newcommand{{\\ROneGammaHatMax}}{{{df_mod['gamma_hat'].max():.1f}}}\n")
        
        # Trajectories
        f.write(f"\\newcommand{{\\ROneCovidPeakData}}{{{df_traj['S_over_thr_Data'].max():.2f}}}\n")
        f.write(f"\\newcommand{{\\ROneCovidPeakConcept}}{{{df_traj['S_over_thr_Concept'].max():.2f}}}\n")
        
        # Threshold SPY
        spy_thr = round(65 * df_mod.loc['SPY', 'gamma_hat'])
        f.write(f"\\newcommand{{\\ROneDataThresholdSpy}}{{{spy_thr}}}\n")
        
        # Injection
        for tk in TICKERS:
            val = df_b[(df_b['Pipeline']=='Data') & (df_b['ETF']==tk)]['DetRate'].values[0] * 100
            f.write(f"\\newcommand{{\\ROneInjectionDetRateData{tk.capitalize()}}}{{{val:.1f}}}\n")
            
        # Placebo
        df_plac = pd.DataFrame(placebo_stats)
        val_pff_data = df_plac[(df_plac['Pipeline']=='Data') & (df_plac['ETF']=='PFF')]['AlarmRate'].values[0] * 100
        f.write(f"\\newcommand{{\\ROnePlaceboDataPff}}{{{val_pff_data:.1f}}}\n")
        
        plac_concept = df_plac[df_plac['Pipeline']=='Concept']['AlarmRate'] * 100
        f.write(f"\\newcommand{{\\ROnePlaceboConceptMin}}{{{plac_concept.min():.1f}}}\n")
        f.write(f"\\newcommand{{\\ROnePlaceboConceptMax}}{{{plac_concept.max():.1f}}}\n")
        
        # Concept ADD
        concept_add = df_b[df_b['Pipeline']=='Concept']['ADD']
        f.write(f"\\newcommand{{\\ROneConceptAddMin}}{{{concept_add.min():.1f}}}\n")
        f.write(f"\\newcommand{{\\ROneConceptAddMax}}{{{concept_add.max():.1f}}}\n")
        
        f.write("\\newcommand{\\ROneOnsetsPerEtf}{36}\n")
        f.write("\\newcommand{\\ROneHorizonDays}{250}\n")
    
    logger.info("--- GENERATING FIGURES ---")
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))
    
    ax1 = axes[0]
    ax1.plot(df_covid.index, S_over_thr_Data, color='blue', label='Data Pipeline (S/Threshold)')
    ax1.plot(df_covid.index, S_over_thr_Concept, color='orange', label='Concept Pipeline (S/Threshold)')
    ax1.axhline(1.0, color='red', linestyle='--', linewidth=1.5, label='Threshold Limit (y=1.0)')
    ax1.set_ylabel("CUSUM Trajectory / Threshold")
    ax1_v = ax1.twinx()
    ax1_v.plot(df_covid.index, df_covid['Close'], color='gray', alpha=0.3, label='SPY Close Price')
    ax1_v.set_ylabel("Price")
    trough_date = pd.to_datetime('2020-03-23')
    ax1.axvline(trough_date, color='gray', linestyle=':', linewidth=2, label='Trough (Mar 23)')
    
    ds_label = "[yfinance] " if args.data_source == "yfinance" else ""
    ax1.set_title(f"(A) {ds_label}COVID-19 Variance Shock & Regime Shifts (SPY, 2020)", fontweight="bold", loc="left")
    ax1.legend(loc='upper left')
    ax1_v.legend(loc='upper right')
    
    ax2 = axes[1]
    df_plot_d = df_b[df_b['Pipeline']=='Data'].set_index('ETF')
    df_plot_c = df_b[df_b['Pipeline']=='Concept'].set_index('ETF')
    x = np.arange(len(TICKERS))
    width = 0.35
    
    add_d_vals = [df_plot_d.loc[t, 'ADD'] for t in TICKERS]
    sem_d_vals = [df_plot_d.loc[t, 'SEM'] for t in TICKERS]
    detrate_d_vals = [df_plot_d.loc[t, 'DetRate'] for t in TICKERS]
    add_c_vals = [df_plot_c.loc[t, 'ADD'] if t in df_plot_c.index else 0 for t in TICKERS]
    sem_c_vals = [df_plot_c.loc[t, 'SEM'] if t in df_plot_c.index else 0 for t in TICKERS]
    detrate_c_vals = [df_plot_c.loc[t, 'DetRate'] if t in df_plot_c.index else 0.0 for t in TICKERS]
    
    bars_d = ax2.bar(x - width/2, add_d_vals, width, yerr=sem_d_vals, label='Data Pipeline', color='blue', capsize=5)
    bars_c = ax2.bar(x + width/2, add_c_vals, width, yerr=sem_c_vals, label='Concept Pipeline (Whitened)', color='orange', capsize=5)
    
    for bar, rate, sem in zip(bars_d, detrate_d_vals, sem_d_vals):
        h = bar.get_height()
        display_h = 0 if np.isnan(h) else h
        display_sem = 0 if np.isnan(sem) else sem
        ax2.text(bar.get_x() + bar.get_width()/2, display_h + display_sem + 2, f"{rate:.0%}", ha='center', va='bottom', fontsize=10, color='blue', weight='bold')
                 
    for bar, rate, sem in zip(bars_c, detrate_c_vals, sem_c_vals):
        h = bar.get_height()
        display_h = 0 if np.isnan(h) else h
        display_sem = 0 if np.isnan(sem) else sem
        ax2.text(bar.get_x() + bar.get_width()/2, display_h + display_sem + 2, f"{rate:.0%}", ha='center', va='bottom', fontsize=10, color='orange', weight='bold')
    
    ax2.set_xticks(x)
    ax2.set_xticklabels(TICKERS)
    ax2.set_ylabel("Average Detection Delay (days)")
    ax2.set_title(rf"(B) {ds_label}Injection $\Delta = 1.5\sigma_{{unc}}$ (36 onsets per ETF, 2021-2023)", fontweight="bold", loc="left")
    ax2.legend()
    
    plt.tight_layout()
    fig.savefig(FIG_OUT_DIR / f"fig02_spy_in_the_wild{sfx}.png")
    plt.close()
    logger.info("[SUCCESS] Pipeline completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="R01 Real World Backtest")
    parser.add_argument("--data-source", choices=["firstrate", "yfinance"], default="firstrate", help="Source of financial data.")
    parser.add_argument("--stage", choices=["ingest", "analyse", "all"], default="all", help="Pipeline stage (firstrate only).")
    parser.add_argument(
        "--legacy-blas",
        action="store_true",
        help="Reproduce the submitted campaign by lifting the BLAS thread pins. "
             "Output is machine-dependent and suffixed '_legacy_blas'; never use "
             "this mode to certify a result.",
    )
    args = parser.parse_args()
    
    t0 = time.time()
    run_experiment(args)
    print(f"Total Execution Time: {time.time()-t0:.1f}s")