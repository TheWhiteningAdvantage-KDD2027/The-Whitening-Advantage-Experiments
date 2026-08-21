"""
================================================================================
R02c - HORIZON SCALING AND OVER-REJECTION PERSISTENCE
================================================================================

Empirical investigation of Ljung-Box test over-rejection rates across increasing
horizons (n_steps) for Student t innovations with varying degrees of freedom (nu).
This experiment establishes that the eighth-moment explanation (E[eps^8] = infinity
for nu <= 8) does not survive its own witness: pooled rejection rates at nu=7
(control arm) remain calibrated at the nominal level, while nu=5 and nu=6 exhibit
significant over-rejection.

Reference: The Whitening Advantage, Section 4.3.
================================================================================
"""
import sys
import time
from pathlib import Path

# --- STRICT DETERMINISM INJECTION ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
from experiments.common.fair_env import enforce_strict_determinism

enforce_strict_determinism()

import os

if os.environ.get("PYTHONHASHSEED") != "42":
    sys.exit("FATAL: PYTHONHASHSEED is not 42. Execute via run_experiment_R02c.sh")

import hashlib
import logging
import argparse
import random

import numpy as np
import pandas as pd
from experiments.common.fair_harness import disable_pandas_multithreading, log_artifact_manifest

disable_pandas_multithreading()

import scipy.stats as stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from joblib import Parallel, delayed

from experiments.common.fair_env import verify_hash_seed, log_environment

PROJECT_ROOT = BASE_DIR
DATA_DIR = PROJECT_ROOT / "results" / "R02c_horizon_sweep" / "data"
FIGS_DIR = PROJECT_ROOT / "results" / "R02c_horizon_sweep" / "figures"
TABS_DIR = PROJECT_ROOT / "results" / "R02c_horizon_sweep" / "tables"
LOGS_DIR = PROJECT_ROOT / "logs" / "R02c_horizon_sweep"

for directory in [DATA_DIR, FIGS_DIR, TABS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

def setup_logging(log_dir: Path, script_name: str) -> logging.Logger:
    log_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(script_name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        log_path = log_dir / f"{script_name}.log"
        file_handler = logging.FileHandler(log_path, mode='w')
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)
    return logger

logger = setup_logging(LOGS_DIR, "exp_R02c_horizon_sweep")

def get_deterministic_seed(*args) -> tuple:
    def format_arg(arg):
        if isinstance(arg, (float, np.floating)):
            return float(arg).hex()
        return str(arg)
    
    s = "_".join(map(format_arg, args))
    h = hashlib.md5(s.encode('utf-8')).hexdigest()
    return int(h, 16), int(h[:8], 16)

def lb_pvalue(series: np.ndarray, lags: int = 20) -> tuple:
    n = len(series)
    mean = np.mean(series)
    denom = np.sum((series - mean) ** 2)
    if denom == 0.0:
        return 1.0, True
    r = np.zeros(lags)
    for k in range(1, lags + 1):
        num = np.sum((series[k:] - mean) * (series[:-k] - mean))
        r[k-1] = num / denom
    k_arr = np.arange(1, lags + 1)
    q_stat = n * (n + 2) * np.sum((r ** 2) / (n - k_arr))
    return float(stats.chi2.sf(q_stat, df=lags)), False

def wilson_score_interval(k: int, n: int, confidence: float = 0.95) -> tuple:
    if n == 0: 
        return 0.0, 0.0
    p_hat = k / n
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n)) / denom
    return max(0.0, float(center - margin)), min(1.0, float(center + margin))

def simulate_stream(nu: float, n_steps: int, seed_idx: int) -> tuple:
    # CONTINUITY GUARD: Forces explicit reuse of the exact state from R02b for the 8000 arm
    # to guarantee exact matching of the printed 8.8% claim.
    if n_steps == 8000:
        seed_128, legacy_seed = get_deterministic_seed("R02b", nu, seed_idx)
    else:
        seed_128, legacy_seed = get_deterministic_seed("R02c", nu, n_steps, seed_idx)
        
    np.random.seed(legacy_seed)
    random.seed(legacy_seed)
    
    ss = np.random.SeedSequence(seed_128)
    rng = np.random.default_rng(ss)
    
    z = rng.standard_t(nu, size=n_steps) * np.sqrt((nu - 2.0) / nu)
    
    p_raw, _ = lb_pvalue(z, 20)
    p_sq, _ = lb_pvalue(z**2, 20)
    
    return nu, n_steps, seed_idx, p_sq, p_raw, seed_128

def fit_wls_slope(n_steps_arr: np.ndarray, p_hat_arr: np.ndarray, n_streams: int):
    p_safe = np.clip(p_hat_arr, 1e-6, 1.0 - 1e-6)
    var = (p_safe * (1.0 - p_safe)) / float(n_streams)
    w = 1.0 / var
    
    x = np.log(n_steps_arr)
    y = p_hat_arr
    
    sum_w = np.sum(w)
    sum_wx = np.sum(w * x)
    sum_wy = np.sum(w * y)
    sum_wxx = np.sum(w * x**2)
    sum_wxy = np.sum(w * x * y)
    
    delta = sum_w * sum_wxx - sum_wx**2
    slope = (sum_w * sum_wxy - sum_wx * sum_wy) / delta
    var_slope = sum_w / delta
    
    se_slope = np.sqrt(max(0.0, float(var_slope)))
    z = stats.norm.ppf(0.975)
    
    return slope, slope - z * se_slope, slope + z * se_slope

def main():
    t0 = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--n-jobs', type=int, default=1)
    args = parser.parse_args()
    
    verify_hash_seed(logger)
    log_environment(logger, ["numpy", "pandas", "scipy", "matplotlib", "joblib"])
    
    nus = [5.0, 6.0, 7.0]
    horizons = [2000, 8000, 32000, 128000]
    n_streams = 1000
    nominal_level = 0.05
    
    logger.info(f"Executing {n_streams} streams per cell. Grids: {len(nus)} nu x {len(horizons)} horizons. {args.n_jobs} cores.")
    
    tasks = [(nu, n, idx) for nu in nus for n in horizons for idx in range(n_streams)]
    results = Parallel(n_jobs=args.n_jobs)(delayed(simulate_stream)(*t) for t in tasks)
    
    # 4(b) Seed uniqueness check
    seeds_128 = [r[5] for r in results]
    if len(set(seeds_128)) != 12000:
        logger.error(f"FATAL: Expected 12000 unique 128-bit hash seeds, got {len(set(seeds_128))}.")
        sys.exit(1)
        
    df_streams = pd.DataFrame(
        [r[:5] for r in results],
        columns=["nu", "n_steps", "seed", "p_squared", "p_raw"]
    )
    df_streams.to_csv(DATA_DIR / "R02c_streams.csv", index=False, float_format='%.17g', na_rep='NaN', lineterminator='\n')
    
    try:
        from scipy.stats import binomtest
        def _binom_pval(k, n, p):
            return binomtest(k, n, p).pvalue
    except ImportError:
        from scipy.stats import binom_test
        def _binom_pval(k, n, p):
            return binom_test(k, n, p)

    stats_rows = []
    slopes = {}
    pvals_raw_control = []
    pvals_nu7_control = []
    
    for nu in nus:
        sub_nu = df_streams[df_streams["nu"] == nu]
        
        rates_for_wls = []
        n_arr_for_wls = []
        cell_stats = []
        
        for n_steps in horizons:
            sub_cell = sub_nu[sub_nu["n_steps"] == n_steps]
            k_sq = int((sub_cell["p_squared"] < nominal_level).sum())
            k_raw = int((sub_cell["p_raw"] < nominal_level).sum())
            
            # 4(c) Continuity Control with R02b
            if nu == 5.0 and n_steps == 8000:
                if k_sq != 88 or k_raw != 57:
                    logger.error(f"FATAL: Continuity check failed. Expected k_sq=88, k_raw=57. Got k_sq={k_sq}, k_raw={k_raw}.")
                    sys.exit(1)
            
            r_sq = k_sq / n_streams
            low_sq, high_sq = wilson_score_interval(k_sq, n_streams)
            r_raw = k_raw / n_streams
            low_raw, high_raw = wilson_score_interval(k_raw, n_streams)
            
            pval_raw = _binom_pval(k_raw, n_streams, nominal_level)
            pvals_raw_control.append(pval_raw)
            pval_sq = _binom_pval(k_sq, n_streams, nominal_level)
            
            if nu == 7.0:
                pvals_nu7_control.append(pval_sq)
                
            rates_for_wls.append(r_sq)
            n_arr_for_wls.append(n_steps)
            
            cell_stats.append({
                "nu": nu,
                "n_steps": n_steps,
                "n_streams": n_streams,
                "lags": 20,
                "reject_rate_squared": r_sq,
                "wilson_low_squared": low_sq,
                "wilson_high_squared": high_sq,
                "reject_rate_raw": r_raw,
                "wilson_low_raw": low_raw,
                "wilson_high_raw": high_raw,
                "contains_nominal_squared": bool(low_sq <= nominal_level <= high_sq),
                "contains_nominal_raw": bool(low_raw <= nominal_level <= high_raw),
                "pval_binom_squared": pval_sq,
                "pval_binom_raw": pval_raw
            })
            
        slope, ci_low, ci_high = fit_wls_slope(np.array(n_arr_for_wls), np.array(rates_for_wls), n_streams)
        slopes[nu] = (slope, ci_low, ci_high)
        
        # Output evaluation log
        if ci_high < 0.0:
            logger.info(f"nu={nu}: Slope = {slope:.3e} 95% CI[{ci_low:.3e}, {ci_high:.3e}]. Significantly negative -> H1 supported.")
        elif ci_low > 0.0:
            logger.info(f"nu={nu}: Slope = {slope:.3e} 95% CI[{ci_low:.3e}, {ci_high:.3e}]. Significantly positive -> Neither supported.")
        else:
            logger.info(f"nu={nu}: Slope = {slope:.3e} 95% CI[{ci_low:.3e}, {ci_high:.3e}]. Indistinguishable from zero -> H1 refuted, H2 not refuted.")
            
        for row in cell_stats:
            row["slope_vs_log_n"] = slope
            row["slope_ci_low"] = ci_low
            row["slope_ci_high"] = ci_high
            stats_rows.append(row)

    # --- S4bis: MULTIPLE TESTING CALIBRATION ---
    m_raw = len(pvals_raw_control)
    p_fwer_raw = 1.0 - (1.0 - nominal_level) ** m_raw
    logger.info(f"Negative control (raw): m={m_raw} tests. P(at least one rejection | H0) = {p_fwer_raw:.3f}")
    if p_fwer_raw > 0.05:
        ks_stat_raw, ks_pval_raw = stats.kstest(pvals_raw_control, 'uniform')
        logger.info(f"S4bis Substituted KS test (raw): KS_stat={ks_stat_raw:.4f}, p-value={ks_pval_raw:.4f}")
        if ks_pval_raw < nominal_level:
            logger.error(f"FATAL: Negative control failed calibration (KS p-value = {ks_pval_raw:.4e}).")
            sys.exit(1)
    else:
        for p in pvals_raw_control:
            if p < nominal_level:
                logger.error("FATAL: Negative control drifted (binary gate).")
                sys.exit(1)

    m_nu7 = len(pvals_nu7_control)
    p_fwer_nu7 = 1.0 - (1.0 - nominal_level) ** m_nu7
    logger.info(f"Witness control (nu=7): m={m_nu7} tests. P(at least one rejection | H0) = {p_fwer_nu7:.3f}")
    if p_fwer_nu7 > 0.05:
        ks_stat_nu7, ks_pval_nu7 = stats.kstest(pvals_nu7_control, 'uniform')
        logger.info(f"S4bis Substituted KS test (nu=7): KS_stat={ks_stat_nu7:.4f}, p-value={ks_pval_nu7:.4f}")
        if ks_pval_nu7 < nominal_level:
            logger.error(f"FATAL: nu=7 control arm failed calibration (KS p-value = {ks_pval_nu7:.4e}).")
            sys.exit(1)
    else:
        for p in pvals_nu7_control:
            if p < nominal_level:
                logger.error("FATAL: nu=7 control arm drifted (binary gate).")
                sys.exit(1)
                
    df_stats = pd.DataFrame(stats_rows)
    df_stats.to_csv(DATA_DIR / "R02c_rejection_vs_horizon.csv", index=False, float_format='%.17g', na_rep='NaN', lineterminator='\n')
    
    # Plotting Figure A02
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    plt.rcParams.update({'font.family': 'sans-serif', 'axes.spines.top': False, 'axes.spines.right': False})
    
    titles = ["(A) nu = 5 (Heavy Tail)", "(B) nu = 6 (Intermediate)", "(C) nu = 7 (Control)"]
    for i, nu in enumerate([5.0, 6.0, 7.0]):
        ax = axes[i]
        sub = df_stats[df_stats["nu"] == nu]
        x = sub["n_steps"].values
        
        ax.plot(x, sub["reject_rate_squared"].values, marker='o', color='black', label="Reject rate (squared)")
        ax.fill_between(x, sub["wilson_low_squared"].values, sub["wilson_high_squared"].values, color='gray', alpha=0.3, label="95% CI")
        ax.axhline(nominal_level, color='red', linestyle='--', label="Nominal 5%")
        
        ax.plot(x, sub["reject_rate_raw"].values, marker='x', color='blue', linestyle=':', label="Raw (Control)")
        
        ax.set_xscale('log')
        ax.set_xticks(horizons)
        ax.get_xaxis().set_major_formatter(ticker.ScalarFormatter())
        ax.set_title(titles[i], fontweight='bold', loc='left')
        ax.set_xlabel("Horizon (n_steps)")
        ax.set_ylim(0, 0.15)
        
        if i == 0:
            ax.set_ylabel("Ljung-Box Rejection Rate (lag=20)")
            ax.legend(loc="upper right")
            
    plt.tight_layout()
    plt.savefig(FIGS_DIR / "figA02_overrejection_vs_horizon.png", dpi=300)
    plt.close()
    
    # Export for LaTeX
    nu_names = {5.0: "Five", 6.0: "Six", 7.0: "Seven"}
    with open(TABS_DIR / "R02c_claims.tex", "w") as f:
        f.write("% Auto-generated by exp_R02c_horizon_sweep.py -- do not edit.\n")
        
        span_log = np.log(max(horizons) / min(horizons))
        f.write(f"\\newcommand{{\\RTwoCSlopeSpanLog}}{{{span_log:.3f}}}\n")
        f.write(f"\\newcommand{{\\RTwoCLargestHorizon}}{{{max(horizons)}}}\n")
        
        for nu in nus:
            slope, ci_low, ci_high = slopes[nu]
            f.write(f"\\newcommand{{\\RTwoCSlopeNu{nu_names[nu]}}}{{{slope:.3e}}}\n")
            f.write(f"\\newcommand{{\\RTwoCCiLowNu{nu_names[nu]}}}{{{ci_low:.3e}}}\n")
            f.write(f"\\newcommand{{\\RTwoCCiHighNu{nu_names[nu]}}}{{{ci_high:.3e}}}\n")
            
            sub = df_stats[df_stats["nu"] == nu]
            n_total = int(sub["n_streams"].sum())
            k_total = int(round((sub["reject_rate_squared"] * sub["n_streams"]).sum()))
            
            p_pool = k_total / n_total
            low_pool, high_pool = wilson_score_interval(k_total, n_total)
            
            f.write(f"\\newcommand{{\\RTwoCPooledNu{nu_names[nu]}}}{{{p_pool*100:.2f}}}\n")
            f.write(f"\\newcommand{{\\RTwoCPooledWilsonLowNu{nu_names[nu]}}}{{{low_pool*100:.2f}}}\n")
            f.write(f"\\newcommand{{\\RTwoCPooledWilsonHighNu{nu_names[nu]}}}{{{high_pool*100:.2f}}}\n")
            
            if nu == 5.0:
                rate_largest = sub[sub["n_steps"] == max(horizons)]["reject_rate_squared"].iloc[0]
                f.write(f"\\newcommand{{\\RTwoCRateLargestHorizonNuFive}}{{{rate_largest*100:.1f}}}\n")
            
    elapsed = (time.time() - t0) / 60
    logger.info(f"Completed execution in {elapsed:.1f} minutes.")
    
    # Log artifact manifest
    artifacts = [
        DATA_DIR / "R02c_streams.csv",
        DATA_DIR / "R02c_rejection_vs_horizon.csv",
        FIGS_DIR / "figA02_overrejection_vs_horizon.png",
        TABS_DIR / "R02c_claims.tex"
    ]
    log_artifact_manifest(logger, artifacts, BASE_DIR, BASE_DIR)

if __name__ == '__main__':
    main()