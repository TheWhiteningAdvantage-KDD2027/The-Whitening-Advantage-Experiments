import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["PYTHONHASHSEED"] = "42"
os.environ["MKL_CBWR"] = "COMPATIBLE"

import hashlib
import numpy as np
import pandas as pd
pd.options.compute.use_bottleneck = False
pd.options.compute.use_numexpr = False

from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from tqdm import tqdm
import argparse
import sys
import logging
from time import time
from pathlib import Path

"""
NOTATIONS:
- phi (φ): AR(1) momentum coefficient injected into the conditional mean.
- n_ols: Length of the rolling window for causal OLS centering estimation.
- eta_rmse_over_sigma (η): Root mean square error of the estimated centering, relative to unconditional volatility.
- b: Injected centering bias, as a fraction of σ_unc (b > 0: over-centering; b < 0: under-centering).
- LB_p: Ljung-Box test p-value at lag 20 (Ljung & Box, 1978, Biometrika 65(2)).
- 2δ lattice: Under a bilateral CUSUM with deadband δ, increments live on {-δ, +δ}, 
  so the running maximum evolves on a discrete 2δ lattice.
- λ*: Calibrated threshold via bisection.
- P_exceed: Measured probability of exceedance.
"""

# --- DIRECTORIES ---
BASE_DIR = Path(__file__).resolve().parent if '__file__' in locals() else Path.cwd()
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def setup_logging(base_dir: Path, script_name: str):
    log_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    log_path = base_dir / f"{script_name}.log"
    file_handler = logging.FileHandler(log_path, mode='w')
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

def get_sha256(file_path: Path) -> str:
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def dump_requirements(base_dir: Path):
    import importlib.metadata
    req_path = base_dir / "requirements.txt"
    packages = ["numpy", "pandas", "scipy", "statsmodels", "matplotlib", "tqdm", "joblib"]
    lines = []
    for pkg in packages:
        try:
            version = importlib.metadata.version(pkg)
            lines.append(f"{pkg}=={version}")
        except importlib.metadata.PackageNotFoundError:
            pass
    with open(req_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    logging.info(f"requirements.txt dynamically generated.")

def wilson_ci(k: int, n: int, confidence: float = 0.95) -> tuple:
    """Asymmetric Wilson score interval for a binomial proportion."""
    if n == 0:
        return 0.0, 0.0
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt((p * (1 - p)) / n + z**2 / (4 * n**2))) / denom
    return max(0.0, center - margin), min(1.0, center + margin)

def lb_pvalue(series: np.ndarray, lag: int = 20) -> float:
    """Computes the Ljung-Box p-value for a given lag."""
    if np.std(series) < 1e-12:
        return 1.0
    res = acorr_ljungbox(series, lags=[lag], return_df=True)
    return float(res['lb_pvalue'].iloc[0])

def compute_phi_hat_naive(r: np.ndarray, n: int, t: int) -> float:
    """Naive non-anticipative OLS formulation for testing purposes."""
    r_s = r[t-n:t]
    r_s_minus_1 = r[t-n-1:t-1]
    sum_num = np.sum(r_s * r_s_minus_1)
    sum_den = np.sum(r_s_minus_1**2)
    if sum_den < 1e-12:
        return 0.0
    return sum_num / sum_den

def compute_phi_hat_vectorized(r: np.ndarray, n: int, start_t: int, end_t: int) -> np.ndarray:
    """Strictly non-anticipative vectorized OLS estimation."""
    num_array = r[1:] * r[:-1]
    den_array = r[:-1]**2
    
    cs_num = np.zeros(len(num_array) + 1)
    np.cumsum(num_array, out=cs_num[1:])
    cs_den = np.zeros(len(den_array) + 1)
    np.cumsum(den_array, out=cs_den[1:])
    
    idx_end = np.arange(start_t, end_t) - 1
    idx_start = idx_end - n
    
    sum_num = cs_num[idx_end] - cs_num[idx_start]
    sum_den = cs_den[idx_end] - cs_den[idx_start]
    
    phi_hat = np.zeros_like(sum_num)
    mask = sum_den >= 1e-12
    phi_hat[mask] = sum_num[mask] / sum_den[mask]
    return phi_hat

def cusum_concept_fast(y_series: np.ndarray, delta: float = 0.1) -> float:
    """Calculates the maximum value M of bilateral CUSUM Concept statistic."""
    S_pos = 0.0
    S_neg = 0.0
    M = 0.0
    for y in y_series.tolist():
        d = y - 0.5
        S_pos += d - delta
        if S_pos < 0.0: S_pos = 0.0
        elif S_pos > M: M = S_pos
        
        S_neg += -d - delta
        if S_neg < 0.0: S_neg = 0.0
        elif S_neg > M: M = S_neg
        
    # NOTE: Due to floating-point representation on the 2δ lattice, 
    # M > λ effectively implements M >= λ when values accumulate ULP-level noise.
    return M

def generate_dgp(T: int, phi: float, seed_sq: np.random.SeedSequence) -> np.ndarray:
    """Generates AR(1)-GARCH(1,1) series with Student-t7 innovations."""
    rng = np.random.default_rng(seed_sq)
    z = rng.standard_t(7.0, size=T) * np.sqrt(5.0 / 7.0)
    
    alpha = 0.1058
    beta = 0.8742
    target_var = 0.04
    omega = target_var * (1.0 - alpha - beta)
    
    r = np.zeros(T)
    h = np.zeros(T)
    eps = np.zeros(T)
    
    h[0] = target_var
    eps[0] = np.sqrt(h[0]) * z[0]
    r[0] = eps[0]
    
    for t in range(1, T):
        h[t] = max(omega + alpha * (eps[t-1]**2) + beta * h[t-1], 1e-12)
        eps[t] = np.sqrt(h[t]) * z[t]
        r[t] = phi * r[t-1] + eps[t]
        
    return r

def check_anti_look_ahead() -> tuple:
    """Sanity Check (a): Validates non-anticipative constraints."""
    rng = np.random.default_rng(42)
    r = rng.standard_normal(6001)
    
    for n in [125, 250, 500, 1000]:
        t = int(rng.integers(1001, 6000))
        val_naive = compute_phi_hat_naive(r, n, t)
        val_vect = compute_phi_hat_vectorized(r, n, t, t+1)[0]
        
        if np.abs(val_naive - val_vect) >= 1e-9:
            return False, f"Mismatch vectorized vs direct sum at t={t}, n={n}."
            
        r_pt = r.copy()
        r_pt[t] += 10.0
        if compute_phi_hat_naive(r_pt, n, t) != val_naive:
            return False, "Lookahead violation: current observation modified prediction."
            
        r_pt2 = r.copy()
        r_pt2[t-1] += 10.0
        if compute_phi_hat_naive(r_pt2, n, t) == val_naive:
            return False, "Dependency violation: previous observation had no effect."
            
    return True, "Check (a) Passed: Strict non-anticipative properties validated."

def calibrate_and_validate(N_CAL: int, H: int, delta: float = 0.1) -> tuple:
    """Sanity Check (d): Exact nominal calibration on pure Bernoulli noise."""
    rng = np.random.default_rng(100)
    Ms_cal = np.zeros(N_CAL)
    for i in range(N_CAL):
        y = rng.integers(0, 2, size=H)
        Ms_cal[i] = cusum_concept_fast(y, delta)
        
    lambda_star = float(np.quantile(Ms_cal, 0.95))
    
    rng_val = np.random.default_rng(200)
    Ms_val = np.zeros(5000)
    for i in range(5000):
        y = rng_val.integers(0, 2, size=H)
        Ms_val[i] = cusum_concept_fast(y, delta)
        
    fpr_val = float(np.mean(Ms_val > lambda_star))
    success = (0.043 <= fpr_val <= 0.057)
    msg = f"Check (d) {'Passed' if success else 'Failed'}: Validation FPR = {fpr_val:.4f}."
    return success, lambda_star, fpr_val, msg

def verify_checks(df_21a: pd.DataFrame, df_21b: pd.DataFrame) -> tuple:
    """Evaluates checks (b), (c) and (e)."""
    log_messages = []
    success = True
    
    # Check (b): Anchor on known boundary
    df_phi_15 = df_21a[df_21a['phi'] == 0.15]
    if not df_phi_15.empty:
        naive_rej = df_phi_15[df_phi_15['arm'] == 'NAIVE']['lb_reject_rate'].values[0]
        oracle_rej = df_phi_15[df_phi_15['arm'] == 'ORACLE']['lb_reject_rate'].values[0]
        if naive_rej < 0.99:
            log_messages.append(f"Check (b) Failed: NAIVE lb_reject at phi=0.15 is {naive_rej:.4f} < 0.99")
            success = False
        if not (0.02 <= oracle_rej <= 0.08):
            log_messages.append(f"Check (b) Failed: ORACLE lb_reject at phi=0.15 is {oracle_rej:.4f}")
            success = False
            
    # Check (c): Null condition validation
    df_phi_0 = df_21a[df_21a['phi'] == 0.00]
    for _, row in df_phi_0.iterrows():
        if not (0.02 <= row['lb_reject_rate'] <= 0.08):
            log_messages.append(f"Check (c) Failed: {row['arm']} lb_reject at phi=0.00 is {row['lb_reject_rate']:.4f}")
            success = False
        if not (0.03 <= row['fpr_concept'] <= 0.07):
            log_messages.append(f"Check (c) Failed: {row['arm']} FPR at phi=0.00 is {row['fpr_concept']:.4f}")
            success = False
            
    # Check (e): Data integrity
    if df_21a.isna().any().any():
        log_messages.append("Check (e) Failed: NaNs found in protocol_21a.")
        success = False
    if len(df_21a) != 42:
        log_messages.append(f"Check (e) Failed: protocol_21a has {len(df_21a)} rows (expected 42).")
        success = False
    if df_21b.isna().any().any():
        log_messages.append("Check (e) Failed: NaNs found in protocol_21b.")
        success = False
    if len(df_21b) != 28:
        log_messages.append(f"Check (e) Failed: protocol_21b has {len(df_21b)} rows (expected 28).")
        success = False
        
    return success, log_messages

def worker(phi: float, seed_sq: np.random.SeedSequence, lambda_star: float, N_OLS_GRID: list) -> list:
    """Core simulation engine operating on a single trajectory."""
    r = generate_dgp(6001, phi, seed_sq)
    r_prev = r[1000:6000]
    r_curr = r[1001:6001]
    
    res = []
    sigma_unc = np.sqrt(0.04)
    
    # NAIVE arm
    y_naive = (r_curr > 0).astype(int)
    res.append({
        'phi': phi, 'arm': 'NAIVE', 'n_ols': '',
        'lb_reject': lb_pvalue(y_naive, 20) < 0.05,
        'fpr_exceed': cusum_concept_fast(y_naive, 0.1) > lambda_star
    })
    
    # ORACLE arm
    mu_oracle = phi * r_prev
    y_oracle = (r_curr - mu_oracle > 0).astype(int)
    res.append({
        'phi': phi, 'arm': 'ORACLE', 'n_ols': '',
        'lb_reject': lb_pvalue(y_oracle, 20) < 0.05,
        'fpr_exceed': cusum_concept_fast(y_oracle, 0.1) > lambda_star
    })
    
    # OLS arms
    for n in N_OLS_GRID:
        phi_hat = compute_phi_hat_vectorized(r, n, 1001, 6001)
        mu_hat = phi_hat * r_prev
        y_ols = (r_curr - mu_hat > 0).astype(int)
        
        eta = np.sqrt(np.mean((mu_hat - mu_oracle)**2)) / sigma_unc
        
        res.append({
            'phi': phi, 'arm': f'OLS-{n}', 'n_ols': n,
            'lb_reject': lb_pvalue(y_ols, 20) < 0.05,
            'fpr_exceed': cusum_concept_fast(y_ols, 0.1) > lambda_star,
            'eta': float(eta),
            'mean_phi_hat': float(np.mean(phi_hat)),
            'sd_phi_hat': float(np.std(phi_hat, ddof=1))
        })
        
    return res

def plot_results(df_21a: pd.DataFrame, PHI_GRID: list, N_OLS_GRID: list, N_SEEDS: int):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=300)
    
    styles = {
        'NAIVE': {'color': 'red', 'linewidth': 2.5, 'linestyle': '-', 'marker': 'o'},
        'ORACLE': {'color': 'black', 'linewidth': 1.5, 'linestyle': '--', 'marker': 's'},
        'OLS-125': {'color': '#99ccff', 'linewidth': 1.0, 'linestyle': '-', 'marker': '^'},
        'OLS-250': {'color': '#66a3ff', 'linewidth': 1.0, 'linestyle': '-', 'marker': '^'},
        'OLS-500': {'color': '#3377ff', 'linewidth': 1.0, 'linestyle': '-', 'marker': '^'},
        'OLS-1000': {'color': '#0044cc', 'linewidth': 1.0, 'linestyle': '-', 'marker': '^'}
    }
    arms = ['NAIVE', 'ORACLE', 'OLS-125', 'OLS-250', 'OLS-500', 'OLS-1000']
    
    # Panel (A)
    ax = axes[0]
    ax.grid(True, alpha=0.3)
    ax.axhline(0.05, color='gray', linestyle=':', label='nominal')
    
    for arm in arms:
        df_sub = df_21a[df_21a['arm'] == arm].sort_values('phi')
        if df_sub.empty: continue
        y_vals = df_sub['lb_reject_rate'].values
        err_low = np.maximum(0, y_vals - df_sub['lb_ci_low'].values)
        err_high = np.maximum(0, df_sub['lb_ci_high'].values - y_vals)
        
        s = styles[arm]
        ax.plot(df_sub['phi'], y_vals, color=s['color'], linewidth=s['linewidth'], 
                linestyle=s['linestyle'], marker=s['marker'], label=arm)
        ax.errorbar(df_sub['phi'], y_vals, yerr=[err_low, err_high], fmt='none', 
                    ecolor=s['color'], capsize=3, alpha=0.7)
        
    ax.set_xlabel('$\\phi$')
    ax.set_ylabel('Rejection Rate')
    ax.set_yscale('log')
    ax.set_xticks(PHI_GRID)
    
    # Panel (B)
    ax = axes[1]
    ax.grid(True, alpha=0.3)
    # Lattice levels read from protocol_21d_null_law_lattice.csv (2e5 fair-coin streams):
    # P(M_H > 11.2) = 0.050270 (above nominal), P(M_H > 11.4) = 0.042870 (at or below).
    # These are the two attainable levels bracketing 5%; lambda* = 11.4 is the conservative pick.
    ax.axhspan(0.042870, 0.050270, color='gray', alpha=0.2, label=r'attainable levels ($\lambda^*$=11.4 / 11.2)')
    
    for arm in arms:
        df_sub = df_21a[df_21a['arm'] == arm].sort_values('phi')
        if df_sub.empty: continue
        y_vals = df_sub['fpr_concept'].values
        err_low = np.maximum(0, y_vals - df_sub['fpr_ci_low'].values)
        err_high = np.maximum(0, df_sub['fpr_ci_high'].values - y_vals)
        
        s = styles[arm]
        ax.plot(df_sub['phi'], y_vals, color=s['color'], linewidth=s['linewidth'], 
                linestyle=s['linestyle'], marker=s['marker'], label=arm)
        ax.errorbar(df_sub['phi'], y_vals, yerr=[err_low, err_high], fmt='none', 
                    ecolor=s['color'], capsize=3, alpha=0.7)
        
    ax.set_xlabel('$\\phi$')
    ax.set_ylabel('False Positive Rate')
    ax.set_ylim(0.0, 0.25)
    ax.set_xticks(PHI_GRID)
    
    # Unique legend in Panel (A)
    handles_A, labels_A = axes[0].get_legend_handles_labels()
    handles_B, labels_B = axes[1].get_legend_handles_labels()
    
    dict_leg = dict(zip(labels_A, handles_A))
    dict_leg.update(dict(zip(labels_B, handles_B)))
    
    final_labels = ['nominal', r'attainable levels ($\lambda^*$=11.6 / 11.4)'] + arms
    final_handles = [dict_leg[k] for k in final_labels if k in dict_leg]
    actual_labels = [k for k in final_labels if k in dict_leg]
    
    axes[0].legend(final_handles, actual_labels, loc='upper left', ncol=1, frameon=False, fontsize='small')
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'Fig25_Estimated_Mean_Robustness.png')
    plt.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true")
    args = parser.parse_args()
    
    setup_logging(BASE_DIR, "Priority_21_estimated_mean_robustness")
    logging.info("NOTE: Execution order -> Priority_21_estimated_mean_robustness (21a) MUST be run FIRST.")
    
    N_SEEDS = 50 if args.fast else 10000
    N_CAL = 2000 if args.fast else 20000
    H = 5000
    PHI_GRID = [0.00, 0.02, 0.05, 0.075, 0.10, 0.125, 0.15]
    N_OLS_GRID = [125, 250, 500, 1000]
    
    logging.info(f"Execution initialized. Mode: {'FAST' if args.fast else 'STANDARD'}.")
    
    # Phase 1: Sanity checks (a) and (d)
    success_a, msg_a = check_anti_look_ahead()
    if not success_a:
        logging.error(msg_a)
        sys.exit(f"ABORT: {msg_a}")
    logging.info(msg_a)
    
    success_d, lambda_star, fpr_val, msg_d = calibrate_and_validate(N_CAL, H, 0.1)
    if not success_d:
        logging.error(msg_d)
        sys.exit(f"ABORT: {msg_d}")
    logging.info(f"Calibration completed: lambda_star = {lambda_star:.6f}. {msg_d}")
    
    # Phase 2: Parallel simulation (KDD Strict Reproducibility via SeedSequence)
    root_sq = np.random.SeedSequence(424242)
    child_sqs = root_sq.spawn(len(PHI_GRID) * N_SEEDS)
    
    # Control (a): Seed uniqueness assertion
    seed_states = [(sq.entropy, sq.spawn_key) for sq in child_sqs]
    if len(set(seed_states)) != len(child_sqs):
        logging.error("ABORT: Intra-group seed collision detected!")
        sys.exit(1)
    else:
        logging.info(f"Control (a) Passed: {len(child_sqs)} unique trajectory seeds verified without collision.")
    
    tasks = []
    task_idx = 0
    for phi_idx, phi in enumerate(PHI_GRID):
        for s in range(N_SEEDS):
            tasks.append((phi, child_sqs[task_idx], lambda_star, N_OLS_GRID))
            task_idx += 1
            
    t0 = time()
    res_list = Parallel(n_jobs=-1)(delayed(worker)(*t) for t in tqdm(tasks, desc="Simulating trajectories"))
    logging.info(f"Simulation completed in {time() - t0:.2f} seconds.")
    
    # Phase 3: Aggregation and DataFrames mapping
    flat_res = [item for sublist in res_list for item in sublist]
    df = pd.DataFrame(flat_res)
    
    records_21a = []
    for (phi, arm, n_ols), group in df.groupby(['phi', 'arm', 'n_ols']):
        n_trials = len(group)
        k_lb = int(group['lb_reject'].sum())
        k_fpr = int(group['fpr_exceed'].sum())
        
        lb_rate = k_lb / n_trials
        lb_ci_low, lb_ci_high = wilson_ci(k_lb, n_trials)
        
        fpr_rate = k_fpr / n_trials
        fpr_ci_low, fpr_ci_high = wilson_ci(k_fpr, n_trials)
        
        records_21a.append({
            'phi': phi, 'arm': arm, 'n_ols': str(n_ols), 'N_seeds': n_trials,
            'lb_reject_rate': float(lb_rate), 'lb_ci_low': float(lb_ci_low), 'lb_ci_high': float(lb_ci_high),
            'fpr_concept': float(fpr_rate), 'fpr_ci_low': float(fpr_ci_low), 'fpr_ci_high': float(fpr_ci_high)
        })
        
    df_21a = pd.DataFrame(records_21a).sort_values(['phi', 'arm', 'n_ols'])
    
    df_ols = df[df['arm'].str.startswith('OLS')].copy()
    df_ols['n_ols'] = df_ols['n_ols'].astype(int)
    df_21b = df_ols.groupby(['phi', 'n_ols']).agg(
        eta_rmse_over_sigma=('eta', 'mean'),
        mean_phi_hat=('mean_phi_hat', 'mean'),
        sd_phi_hat=('sd_phi_hat', 'mean')
    ).reset_index()
    
    # Phase 4: Final structural sanity checks (b), (c), (e)
    success_final, msg_final = verify_checks(df_21a, df_21b)
    for msg in msg_final:
        logging.error(msg)
    if not success_final:
        sys.exit("ABORT: Post-simulation checks failed. Refer to log for details.")
    logging.info("All final sanity checks passed successfully.")
    
    # Phase 5: Deliverables output
    csv_path_a = FIGURES_DIR / 'protocol_21a_estmean_lb_fpr.csv'
    csv_path_b = FIGURES_DIR / 'protocol_21b_estmean_diagnostics.csv'
    
    df_21a.to_csv(csv_path_a, index=False, float_format='%.17g', na_rep='NaN')
    df_21b.to_csv(csv_path_b, index=False, float_format='%.17g', na_rep='NaN')
    
    # Controls (b) & (c): Programmatic Certification
    tol = 1e-9
    v_0 = float(df_21a[(df_21a['phi'] == 0.0) & (df_21a['arm'] == 'NAIVE')]['lb_reject_rate'].iloc[0])
    v_075 = float(df_21a[(df_21a['phi'] == 0.075) & (df_21a['arm'] == 'NAIVE')]['lb_reject_rate'].iloc[0])
    v_015 = float(df_21a[(df_21a['phi'] == 0.15) & (df_21a['arm'] == 'NAIVE')]['lb_reject_rate'].iloc[0])
    fpr_015 = float(df_21a[(df_21a['phi'] == 0.15) & (df_21a['arm'] == 'NAIVE')]['fpr_concept'].iloc[0])
    
    if not (abs(v_0 - 0.0509) <= tol): logging.error(f"Failed Control (b): v_0 = {v_0}"); sys.exit(1)
    if not (abs(v_075 - 0.4984) <= tol): logging.error(f"Failed Control (b): v_075 = {v_075}"); sys.exit(1)
    if not (abs(v_015 - 0.9979) <= tol): logging.error(f"Failed Control (b): v_015 = {v_015}"); sys.exit(1)
    if not (abs(fpr_015 - 0.2076) <= tol): logging.error(f"Failed Control (b): fpr_015 = {fpr_015}"); sys.exit(1)
    
    ols_df = df_21a[df_21a['arm'].str.startswith('OLS')]
    min_lb = float(ols_df['lb_reject_rate'].min())
    max_lb = float(ols_df['lb_reject_rate'].max())
    min_fpr = float(ols_df['fpr_concept'].min())
    max_fpr = float(ols_df['fpr_concept'].max())
    if not (min_lb >= 0.0461 - tol and max_lb <= 0.0557 + tol): logging.error("Failed Control (b): OLS lb bounds"); sys.exit(1)
    if not (min_fpr >= 0.0428 - tol and max_fpr <= 0.0586 + tol): logging.error("Failed Control (b): OLS fpr bounds"); sys.exit(1)
    
    max_bias = (df_21b['mean_phi_hat'] - df_21b['phi']).abs().max()
    if not (max_bias < 2.9e-3): logging.error(f"Failed Control (c): max bias = {max_bias}"); sys.exit(1)
    
    logging.info("Control (b) & (c) Passed: Programmatic certification invariants strictly verified.")
    
    plot_results(df_21a, PHI_GRID, N_OLS_GRID, N_SEEDS)
    dump_requirements(BASE_DIR)
    logging.info(f"Control (f) Reproducibility SHA-256 [protocol_21a]: {get_sha256(csv_path_a)}")
    logging.info(f"Control (f) Reproducibility SHA-256 [protocol_21b]: {get_sha256(csv_path_b)}")
    logging.info("Output files generated successfully.")

if __name__ == "__main__":
    main()