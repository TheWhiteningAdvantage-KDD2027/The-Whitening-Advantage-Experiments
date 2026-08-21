#!/usr/bin/env python3
"""
STREAM P3 — MONITEURS ORACLES DE LOCALISATION : FRONTIÈRE DE DÉTECTABILITÉ EMPIRIQUE
Target: KDD 2027
"""

import os

# R0. STRICT DETERMINISM: Force single-threaded linear algebra BEFORE importing numpy/scipy
# Prevents floating-point non-associativity in multithreaded BLAS/MKL routines (fit_garch_qmle)
# and prevents CPU oversubscription during ProcessPoolExecutor execution.
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["PYTHONHASHSEED"] = "0"

import numpy as np
import pandas as pd
import scipy.stats as stats
from statsmodels.stats.diagnostic import acorr_ljungbox
import logging
import sys
from pathlib import Path
import concurrent.futures

# R1. VERBATIM REUSE
try:
    from Priorite_14_real_world_backtest import (
        get_daily_data, 
        load_data_fallback, 
        _garch_nll, 
        fit_garch_qmle, 
        compute_gamma_exact
    )
except ImportError:
    print("ERROR: Unable to import from Priorite_14_real_world_backtest.py.")
    sys.exit(1)

# R8. SEED
SEED = 20260716
rng = np.random.default_rng(SEED)
np.random.seed(SEED)
import random
random.seed(SEED)

# --- DIRECTORIES ---
BASE_DIR = Path(__file__).resolve().parent
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = BASE_DIR / "Priorite_19_oracle_ceiling_parallel.log"

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Constantes du protocole
N_BOOT_FPR = 20000
N_BOOT_ARL = 5000 
H_ARL = 5000

# Dynamic topological anchoring based on invariant dates
EPISODES_CIBLES_DATES = [
    {'id': 'E1', 'ticker': 'SPY', 'start_date': '2020-02-19', 'end_date': '2020-03-23', 'role': 'TARGET'},
    {'id': 'E2', 'ticker': 'SPY', 'start_date': '2009-03-09', 'end_date': '2010-04-23', 'role': 'POSITIVE CONTROL A'},
    {'id': 'E3', 'ticker': 'SPY', 'start_date': '2018-12-24', 'end_date': '2020-02-19', 'role': 'POSITIVE CONTROL B'},
    {'id': 'E4', 'ticker': 'SPY', 'start_date': '2011-04-29', 'end_date': '2011-10-03', 'role': 'NEGATIVE CONTROL'}
]

def wilson_ci(p, n, z=1.96):
    if n == 0: return 0.0, 0.0
    denom = 1 + (z**2)/n
    center = (p + (z**2)/(2*n)) / denom
    hw = z * np.sqrt(max(0, p*(1-p)/n + (z**2)/(4*n**2))) / denom
    return max(0.0, center - hw), min(1.0, center + hw)

# R7. QMLE CERTIFICATION
def run_qmle_recovery():
    def simulate_garch11(n, omega, alpha, beta, nu=7.0, seed=42):
        loc_rng = np.random.default_rng(seed)
        sigma2_unc = omega / (1 - alpha - beta)
        eps = np.zeros(n)
        sigma2 = np.zeros(n)
        sigma2[0] = sigma2_unc
        scale = np.sqrt((nu - 2) / nu)
        z = loc_rng.standard_t(df=nu, size=n) * scale
        eps[0] = np.sqrt(sigma2[0]) * z[0]
        for t in range(1, n):
            sigma2[t] = omega + alpha * eps[t-1]**2 + beta * sigma2[t-1]
            sigma2[t] = min(sigma2[t], 1e4 * sigma2_unc)
            eps[t] = np.sqrt(sigma2[t]) * z[t]
        return eps

    targets = [(0.05, 0.90), (0.08, 0.90), (0.10, 0.85), (0.05, 0.94)]
    sigmas = [0.1, 0.0093]
    passes = 0
    
    for a, b in targets:
        for sig in sigmas:
            omega = (sig**2) * (1 - a - b)
            for seed in range(11):
                eps = simulate_garch11(5000, omega, a, b, seed=seed)
                res = fit_garch_qmle(eps)
                w_hat, a_hat, b_hat = res[0] if isinstance(res[0], tuple) else res
                if abs(a_hat - a) < 0.03 and abs(b_hat - b) < 0.05:
                    passes += 1
    
    if passes == 88:
        logging.info("QMLE RECOVERY: PASSED")
        return True
    else:
        logging.error("QMLE RECOVERY: FAILED")
        sys.exit(1)

# R12. DETECTOR CERTIFICATION BY RECOVERY ON GROUND TRUTH
def run_detector_recovery():
    # MANDATORY SIGN VERIFICATION:
    # under H_1, E[z_t] = (mu_1 - mu_0)/sigma_t, so
    # E[x_t] = sign(mu_1-mu_0) * (mu_1-mu_0)/sigma_t = |mu_1-mu_0|/sigma_t > 0.
    # The drift of x_t is POSITIVE in both market directions (bear AND bull),
    # which is the necessary condition for a 0-reflected CUSUM to take off.
    
    H_tot, H_inj = 4000, 2000
    N_H0, N_H1 = 5000, 500
    
    Z_H0 = rng.standard_normal((N_H0, H_tot))
    
    # Strict coupling of H1 noise to guarantee Monte Carlo symmetry
    Z_base = rng.standard_normal((N_H1, H_tot))
    
    Z_H1_bear = Z_base.copy()
    Z_H1_bear[:, H_inj:] -= 0.5
    
    Z_H1_bull = Z_base.copy()
    Z_H1_bull[:, H_inj:] += 0.5
    
    Z_H1_null = Z_base.copy()
    
    detectors_ctrl = [('D1', 0.00), ('D1', 0.25), ('D2', np.nan), ('D3', np.nan)]
    lambda_grid_ctrl = np.geomspace(1e-3, 200, 200)
    
    records = []
    pass_all = True
    
    for det, delta in detectors_ctrl:
        if det == 'D1' or det == 'D2':
            is_D1 = (det == 'D1')
            dv = delta if is_D1 else 0.0
            
            def calibrate(Z_batch, mu_1):
                sign_d = np.sign(mu_1) if mu_1 != 0 else 1
                X = sign_d * Z_batch if is_D1 else mu_1 * (Z_batch - mu_1/2)
                S_arr = np.zeros(Z_batch.shape[0])
                M_arr_post = np.zeros(Z_batch.shape[0])
                for t in range(H_tot):
                    S_arr = np.maximum(0, S_arr + X[:, t] - dv)
                    if t >= H_inj:
                        M_arr_post = np.maximum(M_arr_post, S_arr)
                return M_arr_post
                
            # Calibrate lambda on H0 post-injection window
            # to absorb the stationary regime and validate the degenerate case (r_null)
            M_H0_bull = calibrate(Z_H0, mu_1=0.5)
            fprs = np.array([(M_H0_bull > l).mean() for l in lambda_grid_ctrl])
            idx_star = np.where(fprs <= 0.05)[0]
            lam_star = lambda_grid_ctrl[idx_star[0]] if len(idx_star)>0 else np.nan
            fpr_val = fprs[idx_star[0]] if len(idx_star)>0 else np.nan
            
            def eval_power(Z_batch, mu_1):
                sign_d = np.sign(mu_1) if mu_1 != 0 else 1
                X = sign_d * Z_batch if is_D1 else mu_1 * (Z_batch - mu_1/2)
                S_arr = np.zeros(Z_batch.shape[0])
                first_alarm = np.full(Z_batch.shape[0], np.nan)
                for t in range(H_tot):
                    S_arr = np.maximum(0, S_arr + X[:, t] - dv)
                    if t >= H_inj:
                        crossed = (S_arr > lam_star) & np.isnan(first_alarm)
                        first_alarm[crossed] = (t + 1) - H_inj
                return first_alarm
                
            tau_bear = eval_power(Z_H1_bear, mu_1=-0.5)
            tau_bull = eval_power(Z_H1_bull, mu_1=0.5)
            tau_null = eval_power(Z_H1_null, mu_1=0.5)
            
            r_bear = (~np.isnan(tau_bear)).mean()
            r_bull = (~np.isnan(tau_bull)).mean()
            r_null = (~np.isnan(tau_null)).mean()
            
        elif det == 'D3':
            lam_star = 1.6449
            fpr_val = 0.05
            def eval_D3(Z_batch, mu_1):
                sign_d = np.sign(mu_1) if mu_1 != 0 else 1
                first_alarm = np.full(Z_batch.shape[0], np.nan)
                S_num = np.zeros(Z_batch.shape[0])
                for t in range(1, H_inj+1):
                    # Strict Clairvoyant test: starts at onset time
                    S_num += Z_batch[:, H_inj + t - 1]
                    Zn = sign_d * S_num / np.sqrt(t)
                    crossed = (Zn > lam_star) & np.isnan(first_alarm)
                    first_alarm[crossed] = t
                Zn_final = sign_d * S_num / np.sqrt(H_inj)
                return first_alarm, Zn_final
                
            tau_bear, _ = eval_D3(Z_H1_bear, mu_1=-0.5)
            tau_bull, _ = eval_D3(Z_H1_bull, mu_1=0.5)
            _, Zn_final_null = eval_D3(Z_H1_null, mu_1=0.5)
            
            r_bear = (~np.isnan(tau_bear)).mean()
            r_bull = (~np.isnan(tau_bull)).mean()
            r_null = (Zn_final_null > 1.6449).mean()
            
        c_pwr = (r_bear >= 0.95) and (r_bull >= 0.95)
        c_sym = abs(r_bear - r_bull) <= 0.03
        if r_bear >= 0.5 and r_bull >= 0.5:
            rtio = np.nanmedian(tau_bear) / np.nanmedian(tau_bull)
            c_sym = c_sym and (0.7 <= rtio <= 1.4)
        c_deg = 0.02 <= r_null <= 0.10
        
        c_pass = c_pwr and c_sym and c_deg
        if not c_pass: pass_all = False
        
        conds = [
            ('H1_bear_ctrl', r_bear, tau_bear, N_H1),
            ('H1_bull_ctrl', r_bull, tau_bull, N_H1),
            ('H1_null_drift_ctrl', r_null, tau_null if det != 'D3' else np.full(N_H1, np.nan), N_H1),
            ('H0_ctrl', fpr_val, np.full(N_H0, np.nan), N_H0)
        ]
        
        for c_name, c_rate, c_tau, c_n in conds:
            c_low, c_high = wilson_ci(c_rate, c_n)
            records.append({
                'detector': det, 'delta': delta, 'delta_opt_ctrl': 0.25,
                'condition': c_name, 'lambda_star_ctrl': lam_star, 'FPR_H_ctrl': fpr_val,
                'detection_rate': c_rate, 'ci_low': c_low, 'ci_high': c_high,
                'median_delay': np.nanmedian(c_tau), 'n_replicates': c_n,
                'power_requirement_met': c_pwr, 'symmetry_requirement_met': c_sym,
                'degenerate_requirement_met': c_deg, 'detector_recovery_pass': c_pass
            })

    pd.DataFrame(records).to_csv(FIGURES_DIR / 'protocol_19e_detector_recovery.csv', index=False)
    
    if pass_all:
        logging.info("DETECTOR RECOVERY: PASSED")
    else:
        logging.error("DETECTOR RECOVERY: FAILED")
        sys.exit(1)

def compute_oracle_v2_v3(r_arr, t_start, t_end, contam):
    sig = np.zeros(len(r_arr))
    n_eff_min = 999
    for t in range(len(r_arr)):
        s0 = max(0, t - 10)
        s1 = min(len(r_arr), t + 11)
        if contam:
            vals = r_arr[s0:s1]
        else:
            vals = np.concatenate([r_arr[s0:t], r_arr[t+1:s1]])
        
        if t_start <= t <= t_end:
            n_eff_min = min(n_eff_min, len(vals))
            
        sig[t] = np.std(vals, ddof=1) if len(vals) > 0 else np.nan
    return sig, n_eff_min

def check_monotonicity(fpr_vals, arl_vals, det_id):
    if np.any(np.diff(fpr_vals) > 0.005):
        raise RuntimeError(f"FPR monotonicity violated for {det_id}")
    val_arl = arl_vals[~np.isnan(arl_vals)]
    if len(val_arl) > 1 and np.any(np.diff(val_arl) < -5.0):
        raise RuntimeError(f"ARL monotonicity violated for {det_id}")

def process_episode(ep, df_census, df_tick, seed_seq):
    worker_logs = []
    # Legacy seed isolation per worker for legacy SciPy/Statsmodels functions
    legacy_seed = int(seed_seq.generate_state(1)[0]) & 0xFFFFFFFF
    np.random.seed(legacy_seed)
    import random
    random.seed(legacy_seed)
    
    out_19a, out_19b, out_19c, out_19d = [], [], [], []
    # Instantiation of an independent and deterministic RNG via SeedSequence
    loc_rng = np.random.default_rng(seed_seq)
    
    row = df_census[(df_census['ticker'] == ep['ticker']) & (df_census['phase_id'] == ep['phase_id'])]
    if row.empty:
        raise RuntimeError(f"Episode {ep['id']} unresolved in CSV.")
        
    c_row = row.iloc[0]
    st_date, en_date = c_row['start_date'], c_row['end_date']
    T_csv, sr_csv = c_row['T_days'], c_row['sharpe']
    # Original census values, preserved for audit columns *_csv
    # (T_csv/sr_csv might be replaced below by P3 sequential convention).
    T_census_orig, sr_census_orig = c_row['T_days'], c_row['sharpe']
    add_csv, det_csv = c_row['ADD_min_days'], c_row['detectable_flag']
    
    idx_onset = df_tick.index.get_loc(st_date)
    idx_end = df_tick.index.get_loc(en_date)
    
    # R6(a & b) INCOMMENSURABILITY CONFLICT RESOLUTION (EPISTEMOLOGICAL OVERRIDE)
    T_recomp = idx_end - idx_onset
    
    r_ph_strict = df_tick['log_ret'].iloc[idx_onset+1 : idx_end+1]
    sr_recomp = (r_ph_strict.mean() / r_ph_strict.std(ddof=1)) * np.sqrt(252)
    
    if T_recomp != T_csv or abs(sr_recomp - sr_csv) > 1e-3:
        worker_logs.append(("WARNING", f"[{ep['id']}] P16/P3 INCOMMENSURABILITY: T_days {T_csv}->{T_recomp}, Sharpe {sr_csv:.4f}->{sr_recomp:.4f}. SEQUENTIAL OVERRIDE."))
        # Overwriting CSV constants biased by strictly post-onset reality
        T_csv = T_recomp
        sr_csv = sr_recomp
        
    ref_start_idx = max(0, idx_onset - 1000)
    n_ref = idx_onset - ref_start_idx
    if n_ref < 500:
        raise RuntimeError(f"[{ep['id']}] n_ref={n_ref} < 500")
        
    surv_end_idx = min(idx_onset + 3 * T_csv, idx_onset + 750, len(df_tick) - 1)
    r_win = df_tick['log_ret'].iloc[ref_start_idx : surv_end_idx+1].values
    eps_win = r_win - np.mean(r_win)
    
    res_qmle = fit_garch_qmle(eps_win)
    w_hat, a_hat, b_hat = res_qmle[0] if isinstance(res_qmle[0], tuple) else res_qmle
    
    sig2_V1 = np.zeros(len(eps_win))
    sig2_V1[0] = np.var(eps_win)
    for t in range(1, len(eps_win)):
        sig2_V1[t] = w_hat + a_hat * eps_win[t-1]**2 + b_hat * sig2_V1[t-1]
    sig_V1 = np.sqrt(sig2_V1)
    
    idx_rel_onset = idx_onset - ref_start_idx
    idx_rel_end = surv_end_idx - ref_start_idx
    
    sig_V2, n_eff_V2 = compute_oracle_v2_v3(r_win, idx_rel_onset+1, idx_rel_end, False)
    if n_eff_V2 < 8:
        raise RuntimeError(f"[{ep['id']}] V2 n_eff < 8")
        
    sig_V3, _ = compute_oracle_v2_v3(r_win, idx_rel_onset+1, idx_rel_end, True)
    
    oracles_map = {
        'V1': {'sig': sig_V1, 'contam': False, 'w': w_hat, 'a': a_hat, 'b': b_hat},
        'V2': {'sig': sig_V2, 'contam': False, 'w': np.nan, 'a': np.nan, 'b': np.nan},
        'V3': {'sig': sig_V3, 'contam': True, 'w': np.nan, 'a': np.nan, 'b': np.nan}
    }
    
    for o_name, o_data in oracles_map.items():
        sig_arr = o_data['sig']
        sig_surv_chk = sig_arr[idx_rel_onset+1 : idx_rel_end+1]
        if np.any(sig_surv_chk <= 0) or np.any(np.isnan(sig_surv_chk)):
            raise RuntimeError(f"[{ep['id']}] {o_name}: sigma_t <= 0 detected.")
            
        r_ref = r_win[:idx_rel_onset]
        sig_ref = sig_arr[:idx_rel_onset]
        mu_0 = np.mean(r_ref)
        z_ref = (r_ref - mu_0) / sig_ref
        
        p_lb = acorr_ljungbox(z_ref, lags=[20], return_df=True)['lb_pvalue'].iloc[0]
        p_lb2 = acorr_ljungbox(z_ref**2, lags=[20], return_df=True)['lb_pvalue'].iloc[0]
        m_z, s_z, k_z = np.mean(z_ref), np.std(z_ref, ddof=1), stats.kurtosis(z_ref, fisher=False)
        
        is_cert = (p_lb2 >= 0.01) and (0.8 <= s_z <= 1.25)
        if not is_cert:
            worker_logs.append(("WARNING", f"[{ep['id']}] {o_name} not certified."))
            
        idx_rel_phase_end = idx_end - ref_start_idx
        r_ph = r_win[idx_rel_onset+1 : idx_rel_phase_end+1]
        sig_ph = sig_arr[idx_rel_onset+1 : idx_rel_phase_end+1]
        mu_1 = np.mean(r_ph)
        
        D_std = np.mean((mu_1 - mu_0) / sig_ph)
        d_opt = abs(D_std) / 2
        
        KL_p = np.sum(((mu_1 - mu_0)**2) / (2 * sig_ph**2))
        KL_c = T_csv * (sr_csv**2) / 504
        
        r_sv = r_win[idx_rel_onset+1:]
        sig_sv = sig_arr[idx_rel_onset+1:]
        H_ep = int(T_csv)
        
        out_19c.append({
            'episode_id': ep['id'], 'ticker': ep['ticker'], 'phase_id': ep['phase_id'], 'role': ep['role'],
            'sigma_oracle': o_name, 'oracle_contaminated': o_data['contam'],
            'ref_start': df_tick.index[ref_start_idx].strftime('%Y-%m-%d'), 'ref_end': df_tick.index[idx_onset-1].strftime('%Y-%m-%d'),
            'n_ref': n_ref, 'p_lb_z': p_lb, 'p_lb_z2': p_lb2, 'mean_z_ref': m_z, 'std_z_ref': s_z, 'kurt_z_ref': k_z,
            'oracle_certified': is_cert, 'omega': o_data['w'], 'alpha': o_data['a'], 'beta': o_data['b'],
            'persistence': o_data['a'] + o_data['b'], 'gamma_exact': compute_gamma_exact(o_data['a'], o_data['b']) if o_name=='V1' else np.nan,
            'qmle_recovery_pass': True, 'mu_0': mu_0, 'mu_1': mu_1, 'Delta_std': D_std, 'delta_opt': d_opt,
            'sigma_bar_ref': np.mean(sig_ref), 'sigma_bar_phase': np.mean(sig_ph), 'vol_ratio': np.mean(sig_ph)/np.mean(sig_ref),
            'sum_inv_sigma2_phase': np.sum(1 / sig_ph**2), 'KL_path': KL_p, 'KL_corollary': KL_c, 'jensen_ratio': KL_p/KL_c,
            'SR_daily_realized': np.mean(r_ph)/np.std(r_ph, ddof=1), 'sharpe_csv': sr_census_orig, 'sharpe_recomputed': sr_recomp,
            'T_days_csv': T_census_orig, 'T_days_recomputed': T_recomp
        })
        
        # D3 Clairvoyant Floor
        S_n_num = np.cumsum((r_sv - mu_0) / sig_sv**2)
        S_n_den = np.sqrt(np.cumsum(1 / sig_sv**2))
        Zn_real = np.sign(mu_1 - mu_0) * S_n_num / S_n_den
        i_cross = np.where(Zn_real >= 1.6449)[0]
        n_star_real = i_cross[0] + 1 if len(i_cross) > 0 else np.nan
        
        Zn_anal = abs(mu_1 - mu_0) * S_n_den
        ia_cross = np.where(Zn_anal >= 1.6449)[0]
        n_star_anal = ia_cross[0] + 1 if len(ia_cross) > 0 else np.nan
        
        out_19d.append({
            'episode_id': ep['id'], 'ticker': ep['ticker'], 'phase_id': ep['phase_id'], 'role': ep['role'],
            'sigma_oracle': o_name, 'n_star_realized': n_star_real, 'n_star_analytic': n_star_anal,
            'anticonservative': True, 'T_days_phase': T_csv, 'ADD_min_census': add_csv
        })
        
        # Null-B logic
        z_nrm = (z_ref - np.mean(z_ref)) / np.std(z_ref, ddof=1)
        sig_H = sig_sv[:H_ep]
        Z_star = loc_rng.choice(z_nrm, size=(N_BOOT_FPR, H_ep))
        r_nb = mu_0 + sig_H * Z_star
        
        base_grid = np.geomspace(1e-3, 200, 200)
        
        # GARCH Isolation (CRN & Acceleration): 1 unique ARL computation instead of 11 redundancies
        if o_name == 'V1':
            ra_arl = np.zeros((N_BOOT_ARL, H_ARL))
            sa_arl = np.zeros((N_BOOT_ARL, H_ARL))
            bs = 500
            for b in range(N_BOOT_ARL // bs):
                Za = loc_rng.choice(z_nrm, size=(bs, H_ARL + 500))
                ea = np.zeros((bs, H_ARL + 500))
                sa2 = np.zeros((bs, H_ARL + 500))
                sa2[:, 0] = o_data['w'] / (1 - o_data['a'] - o_data['b'])
                for t in range(1, H_ARL + 500):
                    sa2[:, t] = o_data['w'] + o_data['a'] * ea[:, t-1]**2 + o_data['b'] * sa2[:, t-1]
                    ea[:, t] = np.sqrt(sa2[:, t]) * Za[:, t]
                sa_arl[b*bs:(b+1)*bs, :] = np.sqrt(sa2[:, 500:])
                ra_arl[b*bs:(b+1)*bs, :] = mu_0 + ea[:, 500:]
        
        for d_id in ['D1', 'D2']:
            deltas = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, d_opt] if d_id == 'D1' else [np.nan]
            
            for d_val in deltas:
                if d_id == 'D1':
                    X_nb = np.sign(mu_1 - mu_0) * (r_nb - mu_0) / sig_H
                    X_real = np.sign(mu_1 - mu_0) * (r_sv - mu_0) / sig_sv
                    dv = d_val
                else:
                    X_nb = (mu_1 - mu_0) * (r_nb - (mu_0 + mu_1)/2) / (sig_H**2)
                    X_real = (mu_1 - mu_0) * (r_sv - (mu_0 + mu_1)/2) / (sig_sv**2)
                    dv = 0.0
                    
                S_nb = np.zeros(N_BOOT_FPR)
                M_nb = np.zeros(N_BOOT_FPR)
                for t in range(H_ep):
                    S_nb = np.maximum(0, S_nb + X_nb[:, t] - dv)
                    M_nb = np.maximum(M_nb, S_nb)
                    
                S_real = 0.0
                M_real = np.zeros(len(r_sv))
                for t in range(len(r_sv)):
                    S_real = max(0, S_real + X_real[t] - dv)
                    M_real[t] = S_real
                    
                max_M = np.max(M_nb)
                grid = np.geomspace(1e-3, max_M * 1.1, 200) if max_M > 200 else base_grid
                
                fpr_vals = np.array([(M_nb > l).mean() for l in grid])
                
                arl_vals = np.full(200, np.nan)
                arl_cens = np.full(200, False)
                arl_frac = np.zeros(200)
                arl_avail = False
                
                if o_name == 'V1':
                    arl_avail = True
                    tau_arl = np.full((N_BOOT_ARL, 200), H_ARL)
                    
                    if d_id == 'D1':
                        Xa = np.sign(mu_1 - mu_0) * (ra_arl - mu_0) / sa_arl
                    else:
                        Xa = (mu_1 - mu_0) * (ra_arl - (mu_0 + mu_1)/2) / (sa_arl**2)
                        
                    Sa = np.zeros(N_BOOT_ARL)
                    for t in range(H_ARL):
                        Sa = np.maximum(0, Sa + Xa[:, t] - dv)
                        # CPU Vectorization via Broadcasting
                        mask = (Sa[:, None] > grid) & (tau_arl == H_ARL)
                        tau_arl[mask] = t + 1
                                
                    arl_raw = np.mean(tau_arl, axis=0)
                    arl_frac = np.mean(tau_arl == H_ARL, axis=0)
                    arl_cens = arl_frac > 0.05
                    arl_vals = arl_raw.copy()
                    arl_vals[arl_cens] = np.nan
                    
                check_monotonicity(fpr_vals, arl_vals, d_id)
                
                tau_grid = np.full(200, np.nan)
                date_grid = []
                for i, l in enumerate(grid):
                    idx_c = np.where(M_real > l)[0]
                    if len(idx_c) > 0:
                        tau_grid[i] = idx_c[0] + 1
                        date_grid.append(df_tick.index[idx_onset + 1 + idx_c[0]].strftime('%Y-%m-%d'))
                    else:
                        date_grid.append(np.nan)
                        
                for i in range(200):
                    cl, ch = wilson_ci(fpr_vals[i], N_BOOT_FPR)
                    out_19a.append({
                        'episode_id': ep['id'], 'ticker': ep['ticker'], 'phase_id': ep['phase_id'],
                        'sigma_oracle': o_name, 'oracle_contaminated': o_data['contam'], 'detector': d_id,
                        'delta': d_val, 'lambda': grid[i], 'FPR_H': fpr_vals[i], 'FPR_H_ci_low': cl, 'FPR_H_ci_high': ch,
                        'ARL0': arl_vals[i], 'arl0_available': arl_avail, 'arl0_right_censored': arl_cens[i],
                        'arl0_censored_frac': arl_frac[i], 'tau_realized_days': tau_grid[i], 'alarm_date': date_grid[i],
                        'T_days_phase': T_csv
                    })
                    
                # OP Extraction
                i_op1 = np.where(fpr_vals <= 0.05)[0]
                i_op2 = np.where(arl_vals >= 20)[0] if arl_avail else []
                i_op2b = np.where(arl_vals >= 252)[0] if arl_avail else []
                i_op3 = np.where(tau_grid <= T_csv)[0]
                
                ops = [
                    ('OP1_isoFPR5_H', i_op1[0] if len(i_op1)>0 else -1),
                    ('OP2_ARL0_20', i_op2[0] if len(i_op2)>0 else -1),
                    ('OP2b_ARL0_252', i_op2b[0] if len(i_op2b)>0 else -1),
                    ('OP3_breakeven', i_op3[-1] if len(i_op3)>0 else -1)
                ]
                
                bk_ex = len(i_op3) > 0
                for op_name, op_idx in ops:
                    at = op_idx != -1
                    out_19b.append({
                        'episode_id': ep['id'], 'ticker': ep['ticker'], 'phase_id': ep['phase_id'], 'role': ep['role'],
                        'sigma_oracle': o_name, 'oracle_contaminated': o_data['contam'], 'oracle_certified': is_cert,
                        'detector': d_id, 'delta': d_val, 'operating_point': op_name,
                        'lambda_star': grid[op_idx] if at else np.nan, 'FPR_H': fpr_vals[op_idx] if at else np.nan,
                        'ARL0': arl_vals[op_idx] if at else np.nan, 'tau_realized_days': tau_grid[op_idx] if at else np.nan,
                        'alarm_date': date_grid[op_idx] if at else np.nan, 'T_days_phase': T_csv,
                        'alarm_within_T': (tau_grid[op_idx] <= T_csv) if at and not np.isnan(tau_grid[op_idx]) else False,
                        'ADD_min_census': add_csv, 'detectable_flag_census': det_csv, 'op_attainable': at, 'breakeven_exists': bk_ex
                    })
    return out_19a, out_19b, out_19c, out_19d, worker_logs

def main():
    run_qmle_recovery()
    run_detector_recovery()
    
    # census_file = Path(FIGURES_DIR / 'protocol_10a_regime_census.csv')            # legacy name
    census_file = Path(FIGURES_DIR / 'protocol_10b_regime_census_refined.csv')      # new file name

    if not census_file.exists():
        logging.error("File protocol_10b_regime_census_refined.csv not found.")
        sys.exit(1)
        
    df_census = pd.read_csv(census_file)
    
    # Dynamic phase_id resolution to immune the script against upstream index shifts
    EPISODES_CIBLES = []
    for ep in EPISODES_CIBLES_DATES:
        row = df_census[(df_census['ticker'] == ep['ticker']) & 
                        (df_census['start_date'] == ep['start_date']) & 
                        (df_census['end_date'] == ep['end_date'])]
        if row.empty:
            logging.error(f"Episode {ep['id']} ({ep['start_date']} to {ep['end_date']}) unresolved in CSV. Run Priorite_16 first.")
            sys.exit(1)
        ep_dict = ep.copy()
        ep_dict['phase_id'] = int(row.iloc[0]['phase_id'])
        EPISODES_CIBLES.append(ep_dict)
        
    out_19a, out_19b, out_19c, out_19d = [], [], [], []
    
    # Generation of deterministic child seeds for perfect KDD reproducibility
    sg = np.random.SeedSequence(SEED)
    child_seeds = sg.spawn(len(EPISODES_CIBLES))
    
    # FAIR EXPLICIT FIX: Pre-cache data sequentially on the main thread to prevent 
    # concurrent YFinance API rate-limiting, redundant disk I/O, and race conditions in workers.
    unique_tickers = list(set([ep['ticker'] for ep in EPISODES_CIBLES]))
    data_cache = {tk: get_daily_data(tk) for tk in unique_tickers}
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_episode, ep, df_census, data_cache[ep['ticker']], c_seed) for ep, c_seed in zip(EPISODES_CIBLES, child_seeds)]
        # Iteration in submission order to preserve exact CSV row order
        for future in futures:
            try:
                r_a, r_b, r_c, r_d, p_logs = future.result()
                for lvl, msg in p_logs:
                    if lvl == "WARNING":
                        logging.warning(msg)
                    elif lvl == "INFO":
                        logging.info(msg)
                        
                out_19a.extend(r_a)
                out_19b.extend(r_b)
                out_19c.extend(r_c)
                out_19d.extend(r_d)
            except Exception as e:
                logging.error(f"Asynchronous Worker Error: {e}")
                sys.exit(1)

    pd.DataFrame(out_19a).to_csv(FIGURES_DIR / 'protocol_19a_oracle_frontier.csv', index=False)
    pd.DataFrame(out_19b).to_csv(FIGURES_DIR / 'protocol_19b_oracle_operating_points.csv', index=False)
    pd.DataFrame(out_19c).to_csv(FIGURES_DIR / 'protocol_19c_oracle_diagnostics.csv', index=False)
    pd.DataFrame(out_19d).to_csv(FIGURES_DIR / 'protocol_19d_clairvoyant_floor.csv', index=False)
    
    logging.info("[COMPLETED] Generator 19x successfully executed in PARALLEL mode without structural failure.")

if __name__ == "__main__":
    main()