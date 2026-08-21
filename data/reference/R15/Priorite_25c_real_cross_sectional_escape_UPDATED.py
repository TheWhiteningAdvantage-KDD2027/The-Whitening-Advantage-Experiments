"""
STREAM E4 — CROSS-SECTIONAL ESCAPE EVALUATION
"""
import os
import sys

# --- DETERMINISTIC ENVIRONMENT (MUST PRECEDE IMPORTS) ---
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["PYTHONHASHSEED"] = "0"

import argparse
import logging
import hashlib
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import statsmodels.api as sm
from pathlib import Path
from tqdm import tqdm

# --- DIRECTORIES ---
BASE_DIR = Path("/home/m53/08_articleB/")
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# VERBATIM FUNCTIONS
# =============================================================================

def standardized_t(shape, nu, rng):
    x = rng.standard_t(nu, size=shape)
    return x / np.sqrt(nu/(nu-2.0))                       # unit variance

def strict_cusum(stream, delta_P, threshold):
    S=0.0
    for t in range(len(stream)):
        S=max(0.0,S+stream[t]-delta_P)
        if S>threshold: return t
    return -1

def bilateral_delay(stream, delta, thr):
    i1=strict_cusum(stream,delta,thr); i2=strict_cusum(-stream,delta,thr)
    cs=[i for i in (i1,i2) if i!=-1]; return min(cs) if cs else -1

def cusum_max_bilateral(stream, delta):
    Sp=Sn=M=0.0
    for x in stream:
        Sp=max(0.0,Sp+x-delta); Sn=max(0.0,Sn-x-delta)
        if Sp>M: M=Sp
        if Sn>M: M=Sn
    return M

def wilson_ci(k,n,conf=0.95):
    if n==0: return 0.0,0.0
    z=stats.norm.ppf(1-(1-conf)/2); p=k/n; den=1+z**2/n
    c=(p+z**2/(2*n))/den; m=(z*np.sqrt((p*(1-p))/n+z**2/(4*n**2)))/den
    return max(0.0,c-m),min(1.0,c+m)

def simulate_panel(K, n, alpha, beta, nu, rho, rng, mu_shift=0.0, onset=None):
    """K GARCH(1,1) streams, innovations cross-correlated by a common factor:
    z_{i,t} = sqrt(rho)*g_t + sqrt(1-rho)*u_{i,t}, g and u standardized-t_nu (unit var),
    so Corr(z_i,z_j)=rho and each z_i is unit-variance and symmetric. A common location
    mu_shift is added for t>=onset (H1). Returns eps[K,n]."""
    omega = 1.0*(1.0-alpha-beta)
    g = standardized_t((n,), nu, rng)
    u = standardized_t((K,n), nu, rng)
    z = np.sqrt(rho)*g[None,:] + np.sqrt(1.0-rho)*u
    eps = np.empty((K,n)); s2 = np.full(K,1.0)
    for t in range(n):
        if t>0: s2 = omega + alpha*eps[:,t-1]**2 + beta*s2
        eps[:,t] = np.sqrt(s2)*z[:,t]
    if onset is not None and mu_shift!=0.0:
        eps[:,onset:] += mu_shift
    return eps

def fraction_stream(eps):
    """Cross-sectional fraction of positive recentered signs (median=0 by symmetry)."""
    return (eps>0.0).mean(axis=0) - 0.5                   # centered: E[.]=0 under H0

# =============================================================================
# WORKER FUNCTIONS (ISOLATED SEEDS)
# =============================================================================

def worker_boot_calib(seed, K, H_ref, H_det, alpha, beta, nu, rho):
    rng = np.random.default_rng(seed)
    eps = simulate_panel(K, H_ref+H_det, alpha, beta, nu, rho, rng)
    x = fraction_stream(eps)[H_ref:]
    return cusum_max_bilateral(x, 0.0)

def worker_race_h0(seed, K, H_ref, H_det, alpha, beta, nu, rho, lam_naive, lam_boot):
    rng = np.random.default_rng(seed)
    eps = simulate_panel(K, H_ref+H_det, alpha, beta, nu, rho, rng)
    x = fraction_stream(eps)[H_ref:]
    m = cusum_max_bilateral(x, 0.0)
    return (m > lam_naive, m > lam_boot)

def worker_race_h1(seed, K, H_ref, H_det, alpha, beta, nu, rho, c, lam_boot):
    rng = np.random.default_rng(seed)
    eps = simulate_panel(K, H_ref+H_det, alpha, beta, nu, rho, rng, mu_shift=c, onset=H_ref)
    x = fraction_stream(eps)[H_ref:]
    return bilateral_delay(x, 0.0, lam_boot)

# =============================================================================
# REAL DATA LOGIC & WORKERS
# =============================================================================

YF_DATA_DIR = BASE_DIR / "Data" / "yf"

def load_real_panel():
    df = pd.read_csv(YF_DATA_DIR / "panel_logreturns.csv", index_col="Date", parse_dates=True)
    return df.values.T, df.columns.tolist(), df.index  # shape (K_max, T)

def worker_null_window_real(seed, eps_K_full, H_ref, H_det):
    """Windowed REAL null (c=0), byte-for-byte commensurable with worker_race_h1_real:
    a random window, per-window median/std recentring on the H_ref past (non-anticipative),
    no injection. cusum_max > lambda is equivalent to bilateral_delay firing, so this null
    is the exact false-alarm construction of the H1 race pipeline at c=0."""
    rng = np.random.default_rng(seed)
    K, T_full = eps_K_full.shape
    t_start = rng.integers(0, T_full - (H_ref + H_det) + 1)
    w = eps_K_full[:, t_start:t_start + H_ref + H_det]
    med = np.median(w[:, :H_ref], axis=1, keepdims=True)
    std = np.std(w[:, :H_ref], axis=1, keepdims=True); std[std == 0] = 1.0
    z = (w - med) / std
    x = fraction_stream(z)[H_ref:]
    return cusum_max_bilateral(x, 0.0)

def worker_race_h1_real(seed, eps_K_full, H_ref, H_det, c, lam_boot):
    rng = np.random.default_rng(seed)
    K, T_full = eps_K_full.shape
    max_start = T_full - (H_ref + H_det)
    t_start = rng.integers(0, max_start + 1)
    eps_window = eps_K_full[:, t_start : t_start + H_ref + H_det]
    
    # Standardisation sur H_ref pour l'injection c*sigma
    med = np.median(eps_window[:, :H_ref], axis=1, keepdims=True)
    std = np.std(eps_window[:, :H_ref], axis=1, keepdims=True)
    std[std == 0] = 1.0
    eps_std = (eps_window - med) / std
    
    # Injection semi-réelle H1
    eps_std[:, H_ref:] += c
    
    x = fraction_stream(eps_std)[H_ref:]
    return bilateral_delay(x, 0.0, lam_boot)

def run_real_experiment(args, logger):
    logger.info(f"Execution mode: {'FAST' if args.fast else 'FULL'} (REAL DATA)")
    eps_real_full, tickers, dates = load_real_panel()
    K_max = eps_real_full.shape[0]
    T_full = eps_real_full.shape[1]
    logger.info(f"Loaded real panel: {K_max} tickers x {T_full} days.")

    if args.fast:
        K_GRID = [1, 20, K_max]
        C_GRID = [0.25, 1.0]
        N_CAL = 2000
        N_RACE = 500
    else:
        K_GRID = [1, 5, 10, 20, 30, 40, 50, 60, 75, K_max]
        C_GRID = [0.10, 0.25, 0.50, 0.75, 1.0]
        N_CAL = 20000
        N_RACE = 2000

    H_ref = 500
    H_det = 750          # finite real panel: shorter horizon => more distinct, less-overlapping windows
    TARGET_FPR = 0.05
    MASTER_SEED = 42

    res_a = []
    lambdas = {}
    rng_main = np.random.default_rng(MASTER_SEED)

    # --- Phase 1: Diagnostics & Real Calibration ---
    pbar_p1 = tqdm(total=len(K_GRID), desc="Phase 1: Real Calibration (H0)")
    
    with Parallel(n_jobs=-1) as parallel:
        for K in K_GRID:
            cell_seed_base = int(hashlib.md5(f"real_{K}_{MASTER_SEED}".encode()).hexdigest(), 16) % (2**32)
            rng_diag = np.random.default_rng(cell_seed_base)
            
            # Sous-échantillonnage déterministe
            assets_idx = rng_diag.choice(K_max, size=K, replace=False)
            eps_K_full = eps_real_full[assets_idx, :]
            
            # Recentrage sur la médiane temporelle globale pour symétrie directionnelle
            med_full = np.median(eps_K_full, axis=1, keepdims=True)
            eps_K_centered = eps_K_full - med_full
            x_diag = fraction_stream(eps_K_centered)
            
            # Mesures croisées
            rho_sign_meas = 0.0
            if K > 1:
                signs = np.sign(eps_K_centered)
                cm = np.corrcoef(signs)
                rho_sign_meas = cm[np.triu_indices(K, k=1)].mean()
                
            var_x = np.var(x_diag)
            K_eff_meas = 1.0 / (4.0 * var_x) if var_x > 0 else float('nan')
            K_eff_ana = K / (1.0 + (K - 1) * rho_sign_meas)
            
            # Contrôle (b) Blancheur temporelle sur données réelles
            lb_res = sm.stats.acorr_ljungbox(x_diag, lags=[20], return_df=True)
            p_val_lb = lb_res['lb_pvalue'].iloc[0]
            if p_val_lb < 0.05:
                logger.warning(f"Control (b) Whiteness K={K}: p-value={p_val_lb:.4e} < 0.05. Temporal whiteness degraded on real data (expected).")
            else:
                logger.info(f"Control (b) Whiteness K={K}: p-value={p_val_lb:.4e}")
                
            keff_ratio = K_eff_meas / K_eff_ana if K_eff_ana > 0 else float('nan')
            logger.info(f"Control (e) Consistency K={K}: K_eff_meas/K_eff_ana = {keff_ratio:.4f}")

            # Control (a) Non-anticipativity: a post-onset perturbation leaves the H_ref recentring unchanged
            w_chk = eps_K_full[:, :H_ref + H_det].copy()
            med0 = np.median(w_chk[:, :H_ref], axis=1); std0 = np.std(w_chk[:, :H_ref], axis=1)
            w_chk[:, H_ref:] += 1e3
            a_diff = float(np.max(np.abs(np.median(w_chk[:, :H_ref], axis=1) - med0))
                           + np.max(np.abs(np.std(w_chk[:, :H_ref], axis=1) - std0)))
            logger.info(f"Control (a) Non-anticipativity K={K}: max recentring diff = {a_diff:.2e}")
            # Control (g) Bounds: the centered fraction stays in [-0.5, 0.5], no NaN
            x_g = fraction_stream(eps_K_centered)
            logger.info(f"Control (g) Bounds K={K}: max|P_t|={np.max(np.abs(x_g)):.4f}, NaNs={bool(np.isnan(x_g).any())}")

            # Calibration Naive (independence assumption: Binomial(K,1/2))
            naive_maxes = []
            rng_naive = np.random.default_rng(cell_seed_base + 1)
            for _ in range(N_CAL):
                p_indep = rng_naive.binomial(K, 0.5, size=H_det) / K - 0.5
                naive_maxes.append(cusum_max_bilateral(p_indep, 0.0))
            lam_naive = np.quantile(naive_maxes, 1.0 - TARGET_FPR)

            # Calibration on the WINDOWED REAL null (c=0), commensurable with the H1 race
            seeds_cal = [int(hashlib.md5(f"real_cal_{K}_{MASTER_SEED}_{i}".encode()).hexdigest(), 16) % (2**32) for i in range(N_CAL)]
            cal_maxes = parallel(
                delayed(worker_null_window_real)(s, eps_K_full, H_ref, H_det) for s in seeds_cal
            )
            lam_boot = np.quantile(cal_maxes, 1.0 - TARGET_FPR)
            lambdas[K] = lam_boot

            # FPR measured on a DISJOINT set of real null windows (identical construction, c=0)
            seeds_fpr = [int(hashlib.md5(f"real_fpr_{K}_{MASTER_SEED}_{i}".encode()).hexdigest(), 16) % (2**32) for i in range(N_RACE)]
            fpr_maxes = parallel(
                delayed(worker_null_window_real)(s, eps_K_full, H_ref, H_det) for s in seeds_fpr
            )
            fpr_n = sum(1 for m in fpr_maxes if m > lam_naive) / N_RACE
            fpr_b = sum(1 for m in fpr_maxes if m > lam_boot) / N_RACE

            logger.info(f"Control (c) ISO-FPR K={K}: FPR_naive={fpr_n:.4f}, FPR_boot={fpr_b:.4f}")
            if not (0.03 <= fpr_b <= 0.07):
                logger.error(f"FAIL Control (c): FPR_boot {fpr_b:.4f} strictly out of [0.03, 0.07].")
                sys.exit(1)
                
            res_a.append({
                'K': K, 'rho_sign_meas': rho_sign_meas,
                'K_eff_meas': K_eff_meas, 'K_eff_ana': K_eff_ana,
                'ljungbox_p_Pt': p_val_lb, 'lambda_naive': lam_naive,
                'lambda_boot': lam_boot, 'FPR_naive': fpr_n, 'FPR_boot': fpr_b
            })
            pbar_p1.update(1)
    pbar_p1.close()

    df_a = pd.DataFrame(res_a)
    df_a.to_csv(FIGURES_DIR / "protocol_25c_real_panel_diagnostics_UPDATED.csv", index=False)
    
    # --- Phase 2: H1 Semi-Real Race ---
    res_b = []
    pbar_p2 = tqdm(total=len(C_GRID) * len(K_GRID), desc="Phase 2: Real Panel Race (H1)")
    
    with Parallel(n_jobs=-1) as parallel:
        for c in C_GRID:
            # 1. Extraction ADD_single de référence
            lam_b_1 = lambdas[1]
            cell_seed_base_1 = int(hashlib.md5(f"real_1_{MASTER_SEED}".encode()).hexdigest(), 16) % (2**32)
            assets_idx_1 = np.random.default_rng(cell_seed_base_1).choice(K_max, size=1, replace=False)
            eps_1_full = eps_real_full[assets_idx_1, :]
            
            seeds_h1_1 = [int(hashlib.md5(f"real_race1_1_{c}_{MASTER_SEED}_{i}".encode()).hexdigest(), 16) % (2**32) for i in range(N_RACE)]
            delays_1 = parallel(
                delayed(worker_race_h1_real)(s, eps_1_full, H_ref, H_det, c, lam_b_1) for s in seeds_h1_1
            )
            valid_delays_1 = [d for d in delays_1 if d != -1]
            add_single = np.mean(valid_delays_1) if valid_delays_1 else float('nan')
            
            # 2. Course Panel
            for K in K_GRID:
                lam_b = lambdas[K]
                cell_seed_base_K = int(hashlib.md5(f"real_{K}_{MASTER_SEED}".encode()).hexdigest(), 16) % (2**32)
                assets_idx_K = np.random.default_rng(cell_seed_base_K).choice(K_max, size=K, replace=False)
                eps_K_full = eps_real_full[assets_idx_K, :]
                
                seeds_h1 = [int(hashlib.md5(f"real_race1_{K}_{c}_{MASTER_SEED}_{i}".encode()).hexdigest(), 16) % (2**32) for i in range(N_RACE)]
                delays = parallel(
                    delayed(worker_race_h1_real)(s, eps_K_full, H_ref, H_det, c, lam_b) for s in seeds_h1
                )
                
                valid_delays = [d for d in delays if d != -1]
                det_rate = len(valid_delays) / N_RACE
                ci_low, ci_high = wilson_ci(len(valid_delays), N_RACE)
                
                add_val = np.mean(valid_delays) if valid_delays else float('nan')
                sem_val = stats.sem(valid_delays) if len(valid_delays) > 1 else float('nan')
                
                add_reliable = int(det_rate >= 0.90)
                budget_reduction = add_single / add_val if (add_reliable and not np.isnan(add_single)) else float('nan')
                
                row_a = df_a[df_a['K']==K].iloc[0]
                res_b.append({
                    'K': K, 'c': c, 'rho_sign_meas': row_a['rho_sign_meas'],
                    'K_eff_meas': row_a['K_eff_meas'], 'DetRate': det_rate,
                    'CI_low': ci_low, 'CI_high': ci_high, 'ADD': add_val,
                    'SEM': sem_val, 'ADD_single': add_single,
                    'budget_reduction': budget_reduction, 'add_reliable': add_reliable
                })
                pbar_p2.update(1)
    pbar_p2.close()
    
    df_b = pd.DataFrame(res_b)
    df_b.to_csv(FIGURES_DIR / "protocol_25d_real_cross_sectional_race_UPDATED.csv", index=False)
    
    # --- Phase 3: COVID Natural Experiment ---
    idx_onset = np.argmin(np.abs(dates - pd.to_datetime("2020-02-20")))
    end_idx = min(idx_onset + H_det, len(dates))
    
    covid_results = []
    if idx_onset - H_ref >= 0:
        logger.info("--- COVID 2020 Natural Experiment ---")
        for K in K_GRID:
            cell_seed_base_K = int(hashlib.md5(f"real_{K}_{MASTER_SEED}".encode()).hexdigest(), 16) % (2**32)
            assets_idx_K = np.random.default_rng(cell_seed_base_K).choice(K_max, size=K, replace=False)
            eps_covid = eps_real_full[assets_idx_K, idx_onset - H_ref : end_idx]
            
            # Standardization commensurable with H1 and Null windows
            med = np.median(eps_covid[:, :H_ref], axis=1, keepdims=True)
            std = np.std(eps_covid[:, :H_ref], axis=1, keepdims=True)
            std[std == 0] = 1.0
            eps_centered = (eps_covid - med) / std
            x_covid = fraction_stream(eps_centered)[H_ref:]
            
            delay_naive = bilateral_delay(x_covid, 0.0, df_a[df_a['K']==K]['lambda_naive'].iloc[0])
            delay_boot = bilateral_delay(x_covid, 0.0, lambdas[K])
            
            logger.info(f"COVID K={K}: Delay Naive = {delay_naive}, Delay Boot = {delay_boot}")
            det_date = dates[idx_onset + delay_boot].date() if delay_boot != -1 else None
            if delay_boot != -1:
                logger.info(f"   -> Detection Date (Boot): {det_date}")
                
            covid_results.append({
                'K': K,
                'delay_boot': delay_boot,
                'delay_naive': delay_naive,
                'detection_date': det_date
            })
            
        pd.DataFrame(covid_results).to_csv(FIGURES_DIR / "protocol_25e_covid_natural.csv", index=False)
    
    # --- Plotting ---
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=300)
    
    # Panel A: Rupture de Pivotalité (Real Data)
    ax = axes[0]
    ax.plot(df_a['K'], df_a['FPR_naive'], marker='o', linestyle='-', color='red', label='FPR Naive')
    ax.plot(df_a['K'], df_a['FPR_boot'], marker='x', linestyle='--', color='blue', label='FPR Boot')
    ax.axhline(0.05, color='black', linestyle=':', label='Target 5%')
    ax.set_xscale('log')
    ax.set_xlabel('Panel Size K (Real Data)')
    ax.set_ylabel('False Positive Rate')
    ax.legend(fontsize=8)
    
    # Panel B: Plafonnement de la racine carrée
    ax = axes[1]
    c_target = C_GRID[1] if len(C_GRID) > 1 else C_GRID[0]
    df_sub = df_b[df_b['c'] == c_target].sort_values('K')
    ax.plot(df_sub['K'], df_sub['budget_reduction'], marker='s', linestyle='-', color='purple', label=f'Empirical Reduction (c={c_target})')
    ax.plot(df_a['K'], np.sqrt(df_a['K_eff_meas']), marker='x', linestyle=':', color='black', linewidth=2, label=r'Measured Limit: $\sqrt{K_{eff}}$')
    # Reference naive : ce que promettrait un panneau independant. Presente dans la
    # version a 4 points, perdue dans la version dense ; c'est elle qui montre
    # l'ampleur de ce que la correlation des signes retire.
    ax.plot(df_a['K'], np.sqrt(df_a['K']), linestyle='-.', color='gray', linewidth=1.5,
            label=r'Independent panel: $\sqrt{K}$')
    # Le delai realise suit le seuil bootstrap (r >= 0.99), pas K_eff : le tracer
    # rend la dispersion lisible au lieu de la faire passer pour du bruit.
    ax2 = ax.twinx()
    ax2.plot(df_a['K'], df_a['lambda_boot'], marker='.', linestyle='--', color='darkorange',
             linewidth=1.2, alpha=0.8, label=r'Bootstrap threshold $\lambda_{\mathrm{boot}}$')
    ax2.set_ylabel(r'$\lambda_{\mathrm{boot}}$', color='darkorange')
    ax2.tick_params(axis='y', labelcolor='darkorange')
    ax.set_xscale('log')
    ax.set_xlabel('Panel Size K (Real Data)')
    ax.set_ylabel(f'Budget Reduction (c={c_target})')
    
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc='upper left', fontsize=8.5, framealpha=0.95, facecolor='white')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "Fig30_RealCrossSectional_Escape_UPDATED.png")
    plt.close()

# =============================================================================
# MAIN LOGIC
# =============================================================================

def setup_logger():
    """Configures a strict logging mechanism to track sanity checks and semantics."""
    logger_inst = logging.getLogger("cross_sectional_escape")
    logger_inst.setLevel(logging.INFO)
    
    if logger_inst.hasHandlers():
        logger_inst.handlers.clear()
        
    fh = logging.FileHandler(BASE_DIR / "Priorite_25c_real_cross_sectional_escape_UPDATED.log", mode='w')
    sh = logging.StreamHandler(sys.stdout)
    
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    
    logger_inst.addHandler(fh)
    logger_inst.addHandler(sh)
    return logger_inst

def run_experiment():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--source", choices=["synthetic", "real"], default="real")
    args = parser.parse_args()

    logger = setup_logger()
    # Redirection of global logging to the custom handler to preserve diff stability
    logging.info = logger.info
    logging.error = logger.error
    logging.warning = logger.warning

    if args.source == "real":
        return run_real_experiment(args, logger)

    logger.info(f"Execution mode: {'FAST' if args.fast else 'FULL'} (SYNTHETIC)")

    if args.fast:
        K_GRID = [1, 50, 200]
        RHO_GRID = [0.0, 0.20]
        C_GRID = [0.25, 1.0]
        N_CAL = 2000
        N_RACE = 500
    else:
        K_GRID = [1, 50, 100, 200, 500]
        RHO_GRID = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]
        C_GRID = [0.10, 0.25, 0.50, 1.0]
        N_CAL = 20000
        N_RACE = 2000

    alpha = 0.08
    beta = 0.90
    nu = 7.0
    H_ref = 500
    H_det = 2000
    TARGET_FPR = 0.05
    MASTER_SEED = 42

    logger.info(f"Control (f) Commensurability: H_det={H_det}, onset={H_ref}, nu={nu}, GARCH alpha={alpha}, beta={beta} strictly identical across arms.")

    # Control (a) Non-anticipativity
    try:
        rng_test_0 = np.random.default_rng(999)
        eps_0 = simulate_panel(5, 200, alpha, beta, nu, 0.1, rng_test_0, mu_shift=0.0, onset=100)
        rng_test_1 = np.random.default_rng(999)
        eps_1 = simulate_panel(5, 200, alpha, beta, nu, 0.1, rng_test_1, mu_shift=2.0, onset=100)
        diff_pre = np.max(np.abs(eps_0[:, :100] - eps_1[:, :100]))
        diff_post = np.max(np.abs(eps_0[:, 100:] - eps_1[:, 100:]))
        logger.info(f"Control (a) Non-anticipativity: Max diff pre-onset = {diff_pre:.1e}, post-onset > 0 = {diff_post > 0}")
        if diff_pre > 1e-12:
            raise RuntimeError("Anticipation detected in DGP.")
    except Exception as e:
        logger.error(f"FAIL Control (a): {e}")
        sys.exit(1)

    # --- Phase 1: Diagnostics & Calibration ---
    res_a = []
    add_single_dict = {}
    lambdas = {}
    
    rng_main = np.random.default_rng(MASTER_SEED)
    
    total_p1 = len(K_GRID) * len(RHO_GRID)
    pbar_p1 = tqdm(total=total_p1, desc="Phase 1: Calibration (H0)")

    with Parallel(n_jobs=-1) as parallel:
        for K in K_GRID:
            for rho in RHO_GRID:
                cell_seed_base = int(hashlib.md5(f"{K}_{rho}_{MASTER_SEED}".encode()).hexdigest(), 16) % (2**32)
            
                # 1. Diagnostics (Long path)
                rng_diag = np.random.default_rng(cell_seed_base)
                eps_diag = simulate_panel(K, 20000, alpha, beta, nu, rho, rng_diag)
                x_diag = fraction_stream(eps_diag)
                
                # Control (g) NaNs and bounds
                max_val = np.abs(x_diag).max()
                has_nans = np.isnan(x_diag).any()
                logger.info(f"Control (g) Bounds K={K}, rho={rho}: max|P_t|={max_val:.4f}, NaNs={has_nans}")
                if has_nans or max_val > 0.500001:
                    logger.error("FAIL Control (g): Stream bounds violated.")
                    sys.exit(1)

                # Measurements
                if K > 1:
                    signs = np.sign(eps_diag)
                    cm = np.corrcoef(signs)
                    rho_sign_meas = cm[np.triu_indices(K, k=1)].mean()
                else:
                    rho_sign_meas = 0.0

                var_x = np.var(x_diag)
                K_eff_meas = 1.0 / (4.0 * var_x) if var_x > 0 else float('nan')
                K_eff_ana = K / (1.0 + (K - 1) * rho_sign_meas)

                # Control (b) Whiteness
                lb_res = sm.stats.acorr_ljungbox(x_diag, lags=[20], return_df=True)
                p_val_lb = lb_res['lb_pvalue'].iloc[0]
                if p_val_lb < 0.05:
                    logger.warning(f"Control (b) Whiteness K={K}, rho={rho}: p-value={p_val_lb:.4e} < 0.05. Temporal whiteness degraded.")
                else:
                    logger.info(f"Control (b) Whiteness K={K}, rho={rho}: p-value={p_val_lb:.4e}")

                # Control (e) Consistency K_eff
                keff_ratio = K_eff_meas / K_eff_ana
                logger.info(f"Control (e) Consistency K={K}, rho={rho}: K_eff_meas/K_eff_ana = {keff_ratio:.4f}")
                if not (0.80 <= keff_ratio <= 1.20):
                    logger.error(f"FAIL Control (e): K_eff ratio {keff_ratio:.4f} out of bounds.")
                    res_a.append({'K': K, 'rho': rho, 'rho_sign_meas': rho_sign_meas, 'K_eff_meas': K_eff_meas, 'K_eff_ana': K_eff_ana, 'ljungbox_p_Pt': p_val_lb, 'lambda_naive': lam_naive, 'lambda_boot': float('nan'), 'FPR_naive': float('nan'), 'FPR_boot': float('nan')})
                    pd.DataFrame(res_a).to_csv(FIGURES_DIR / "protocol_25a_panel_diagnostics_UPDATED.csv", index=False)
                    sys.exit(1)

                # 2. Calibration Naive
                naive_maxes = []
                rng_naive = np.random.default_rng(cell_seed_base + 1)
                for _ in range(N_CAL):
                    p_indep = rng_naive.binomial(K, 0.5, size=H_det) / K - 0.5
                    naive_maxes.append(cusum_max_bilateral(p_indep, 0.0))
                lam_naive = np.quantile(naive_maxes, 1.0 - TARGET_FPR)

                # 3. Calibration Boot
                seeds_boot = [int(hashlib.md5(f"boot_{K}_{rho}_{MASTER_SEED}_{i}".encode()).hexdigest(), 16) % (2**32) for i in range(N_CAL)]
                boot_maxes = parallel(
                    delayed(worker_boot_calib)(s, K, H_ref, H_det, alpha, beta, nu, rho) for s in seeds_boot
                )
                lam_boot = np.quantile(boot_maxes, 1.0 - TARGET_FPR)
                lambdas[(K, rho)] = lam_boot

                # 4. H0 Race (FPR check)
                seeds_h0 = [int(hashlib.md5(f"race0_{K}_{rho}_{MASTER_SEED}_{i}".encode()).hexdigest(), 16) % (2**32) for i in range(N_RACE)]
                h0_results = parallel(
                    delayed(worker_race_h0)(s, K, H_ref, H_det, alpha, beta, nu, rho, lam_naive, lam_boot) for s in seeds_h0
                )
                fpr_n = sum(r[0] for r in h0_results) / N_RACE
                fpr_b = sum(r[1] for r in h0_results) / N_RACE

                logger.info(f"Control (c) ISO-FPR K={K}, rho={rho}: FPR_naive={fpr_n:.4f}, FPR_boot={fpr_b:.4f}")
                if not (0.03 <= fpr_b <= 0.07):
                    logger.error(f"FAIL Control (c): FPR_boot {fpr_b:.4f} strictly out of [0.03, 0.07].")
                    res_a.append({'K': K, 'rho': rho, 'rho_sign_meas': rho_sign_meas, 'K_eff_meas': K_eff_meas, 'K_eff_ana': K_eff_ana, 'ljungbox_p_Pt': p_val_lb, 'lambda_naive': lam_naive, 'lambda_boot': lam_boot, 'FPR_naive': fpr_n, 'FPR_boot': fpr_b})
                    pd.DataFrame(res_a).to_csv(FIGURES_DIR / "protocol_25a_panel_diagnostics_UPDATED.csv", index=False)
                    sys.exit(1)

                # Control (d) Sanity rho=0
                if rho == 0.0:
                    fpr_diff = abs(fpr_n - fpr_b)
                    logger.info(f"Control (d) Sanity rho=0 (K={K}): rho_sign={rho_sign_meas:.4f}, K_eff/K={K_eff_meas/K:.4f}, diff_FPR={fpr_diff:.4f}")
                    if abs(rho_sign_meas) >= 0.02 or not (0.85 <= K_eff_meas/K <= 1.15) or fpr_diff >= 0.02:
                        logger.error("FAIL Control (d): Sanity rho=0 violated.")
                        res_a.append({'K': K, 'rho': rho, 'rho_sign_meas': rho_sign_meas, 'K_eff_meas': K_eff_meas, 'K_eff_ana': K_eff_ana, 'ljungbox_p_Pt': p_val_lb, 'lambda_naive': lam_naive, 'lambda_boot': lam_boot, 'FPR_naive': fpr_n, 'FPR_boot': fpr_b})
                        pd.DataFrame(res_a).to_csv(FIGURES_DIR / "protocol_25a_panel_diagnostics_UPDATED.csv", index=False)
                        sys.exit(1)

                res_a.append({
                    'K': K, 'rho': rho, 'rho_sign_meas': rho_sign_meas,
                    'K_eff_meas': K_eff_meas, 'K_eff_ana': K_eff_ana,
                    'ljungbox_p_Pt': p_val_lb, 'lambda_naive': lam_naive,
                    'lambda_boot': lam_boot, 'FPR_naive': fpr_n, 'FPR_boot': fpr_b
                })
                pbar_p1.update(1)
    pbar_p1.close()

    df_a = pd.DataFrame(res_a)
    df_a.to_csv(FIGURES_DIR / "protocol_25a_panel_diagnostics_UPDATED.csv", index=False)

    # --- Phase 2: H1 Race ---
    res_b = []
    
    total_p2_ref = len(C_GRID) * len(RHO_GRID)
    pbar_p2_ref = tqdm(total=total_p2_ref, desc="Phase 2: Univariate Ref")
    
    with Parallel(n_jobs=-1) as parallel:
        # Pre-compute single reference (K=1) to populate add_single_dict
        for c in C_GRID:
            for rho in RHO_GRID:
                lam_b = lambdas[(1, rho)]
                seeds_h1 = [int(hashlib.md5(f"race1_1_{rho}_{c}_{MASTER_SEED}_{i}".encode()).hexdigest(), 16) % (2**32) for i in range(N_RACE)]
                delays = parallel(
                    delayed(worker_race_h1)(s, 1, H_ref, H_det, alpha, beta, nu, rho, c, lam_b) for s in seeds_h1
                )
                valid_delays = [d for d in delays if d != -1]
                if len(valid_delays) > 0:
                    add_single_dict[(rho, c)] = np.mean(valid_delays)
                else:
                    add_single_dict[(rho, c)] = float('nan')
                pbar_p2_ref.update(1)
    pbar_p2_ref.close()

    total_p2_panel = len(K_GRID) * len(RHO_GRID) * len(C_GRID)
    pbar_p2_panel = tqdm(total=total_p2_panel, desc="Phase 2: Panel Race (H1)")
    
    with Parallel(n_jobs=-1) as parallel:
        for K in K_GRID:
            for rho in RHO_GRID:
                lam_b = lambdas[(K, rho)]
                for c in C_GRID:
                    seeds_h1 = [int(hashlib.md5(f"race1_{K}_{rho}_{c}_{MASTER_SEED}_{i}".encode()).hexdigest(), 16) % (2**32) for i in range(N_RACE)]
                    delays = parallel(
                        delayed(worker_race_h1)(s, K, H_ref, H_det, alpha, beta, nu, rho, c, lam_b) for s in seeds_h1
                    )
                    
                    valid_delays = [d for d in delays if d != -1]
                    det_rate = len(valid_delays) / N_RACE
                    ci_low, ci_high = wilson_ci(len(valid_delays), N_RACE)
                    
                    add_val = np.mean(valid_delays) if valid_delays else float('nan')
                    sem_val = stats.sem(valid_delays) if len(valid_delays) > 1 else float('nan')
                    
                    add_reliable = int(det_rate >= 0.90)
                    add_single_ref = add_single_dict[(rho, c)]
                    
                    if add_reliable and not np.isnan(add_single_ref):
                        budget_reduction = add_single_ref / add_val
                    else:
                        budget_reduction = float('nan')
                        
                    row_a = df_a[(df_a['K']==K) & (df_a['rho']==rho)].iloc[0]

                    res_b.append({
                            'K': K, 'rho': rho, 'rho_sign_meas': row_a['rho_sign_meas'],
                            'K_eff_meas': row_a['K_eff_meas'], 'c': c,
                            'DetRate': det_rate, 'CI_low': ci_low, 'CI_high': ci_high,
                            'ADD': add_val, 'SEM': sem_val, 'ADD_single': add_single_ref,
                            'budget_reduction': budget_reduction, 'add_reliable': add_reliable
                        })
                    pbar_p2_panel.update(1)
    
    pbar_p2_panel.close()

    df_b = pd.DataFrame(res_b)
    df_b.to_csv(FIGURES_DIR / "protocol_25b_cross_sectional_race_UPDATED.csv", index=False)
    
    # Log budget reduction monotonicity check
    for rho in RHO_GRID:
        if rho > 0.0:
            df_sub = df_b[(df_b['rho']==rho) & (df_b['add_reliable']==1)].groupby('K')['budget_reduction'].mean()
            logger.info(f"Budget reduction for rho={rho}: {df_sub.to_dict()}")

    # --- Phase 3: Plotting ---
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=300)
    
    # Panel A: FPR naive vs boot
    ax = axes[0]
    colors = plt.cm.viridis(np.linspace(0, 1, len(K_GRID)))
    for idx, K in enumerate(K_GRID):
        df_sub = df_a[df_a['K'] == K].sort_values('rho_sign_meas')
        if len(df_sub) > 0:
            ax.plot(df_sub['rho_sign_meas'], df_sub['FPR_naive'], marker='o', linestyle='-', color=colors[idx], label=f'Naive K={K}')
            ax.plot(df_sub['rho_sign_meas'], df_sub['FPR_boot'], marker='x', linestyle='--', color=colors[idx], label=f'Boot K={K}')
    ax.axhline(0.05, color='black', linestyle=':', label='Target 5%')
    ax.set_xlabel('Measured Sign Correlation (rho_sign_meas)')
    ax.set_ylabel('False Positive Rate')
    ax.legend(fontsize=8)
    
    # Panel B: Budget Reduction vs K
    ax = axes[1]
    c_target = C_GRID[1] if len(C_GRID) > 1 else C_GRID[0]
    colors = plt.cm.plasma(np.linspace(0, 1, len(RHO_GRID)))
    for idx, rho in enumerate(RHO_GRID):
        df_sub = df_b[(df_b['rho'] == rho) & (df_b['c'] == c_target)].sort_values('K')
        df_sub_a = df_a[df_a['rho'] == rho].sort_values('K')
        if len(df_sub) > 0:
            ax.plot(df_sub['K'], df_sub['budget_reduction'], marker='s', linestyle='-', color=colors[idx], label=f'Empirical rho={rho}')
            ax.plot(df_sub_a['K'], df_sub_a['K_eff_ana'], marker='', linestyle=':', color=colors[idx], alpha=0.6)
    ax.set_xscale('log')
    ax.set_xlabel('Panel Size K (log scale)')
    ax.set_ylabel(f'Budget Reduction (c={c_target})')
    ax.legend(fontsize=8)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "Fig29_CrossSectional_Escape_UPDATED.png")
    plt.close()

if __name__ == "__main__":
    run_experiment()