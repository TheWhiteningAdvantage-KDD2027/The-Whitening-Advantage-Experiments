#!/usr/bin/env python3
"""
==========================================================================
EXPERIMENTAL PROTOCOLS — Mission 6 (Econometric Baseline vs ML Whitening)
Author: Raphaël Minato
Target: KDD 2027
==========================================================================
"""

import os
# Strictly enforce single-threading for BLAS/LAPACK to guarantee
# bit-for-bit floating point reproducibility in scipy optimizations across hardware.
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["PYTHONHASHSEED"] = "0"
os.environ["MKL_CBWR"] = "COMPATIBLE"

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import minimize
from pathlib import Path
import sys
import argparse
import time
import warnings

# Use statsmodels strictly for the Ljung-Box test
from statsmodels.stats.diagnostic import acorr_ljungbox

warnings.filterwarnings("ignore")

# --- DIRECTORY SETUP ---
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# --- PLOT FORMATTING ---
plt.rcParams.update({
    "figure.figsize": (18, 6), 
    "font.size": 12, 
    "figure.dpi": 200, 
    "axes.titlesize": 13,
    "axes.titleweight": "bold"
})
C_RAW = "#C45C5C"
C_RECALIB = "#2A6A7C"
C_ECO = "#4A8C5C"
C_ML = "#D4A017"

# --- CORE SIMULATORS ---
def simulate_garch11(n, omega, alpha, beta, nu=7.0, seed=42):
    """Simulates a stationary GARCH(1,1) stream with standardized Student-t7 innovations."""
    rng = np.random.default_rng(seed)
    sigma2_unc = omega / (1 - alpha - beta)
    eps = np.zeros(n)
    sigma2 = np.zeros(n)
    sigma2[0] = sigma2_unc
    scale = np.sqrt((nu - 2) / nu)
    z = rng.standard_t(df=nu, size=n) * scale
    eps[0] = np.sqrt(sigma2[0]) * z[0]
    for t in range(1, n):
        sigma2[t] = omega + alpha * eps[t-1]**2 + beta * sigma2[t-1]
        sigma2[t] = min(sigma2[t], 1e4 * sigma2_unc)
        eps[t] = np.sqrt(sigma2[t]) * z[t]
    return eps

def simulate_gjr11(n, omega, alpha, gamma_lev, beta, nu=7.0, seed=42):
    """Simulates a stationary GJR-GARCH(1,1) stream with asymmetric leverage effect."""
    rng = np.random.default_rng(seed)
    # Stationarity condition: alpha + beta + gamma_lev/2 < 1
    sigma2_unc = omega / (1 - alpha - beta - gamma_lev/2.0)
    eps = np.zeros(n)
    sigma2 = np.zeros(n)
    sigma2[0] = sigma2_unc
    scale = np.sqrt((nu - 2) / nu)
    z = rng.standard_t(df=nu, size=n) * scale
    eps[0] = np.sqrt(sigma2[0]) * z[0]
    for t in range(1, n):
        indicator = 1.0 if eps[t-1] < 0 else 0.0
        sigma2[t] = omega + (alpha + gamma_lev * indicator) * eps[t-1]**2 + beta * sigma2[t-1]
        sigma2[t] = min(sigma2[t], 1e4 * sigma2_unc)
        eps[t] = np.sqrt(sigma2[t]) * z[t]
    return eps

def compute_gamma_exact(alpha, beta):
    """Computes exact theoretical Gamma penalty factor for squared returns."""
    phi = alpha + beta
    if phi >= 1.0: return np.inf
    denom = 1 - 2 * alpha * beta - beta**2
    if denom <= 0: return (1 + phi) / (1 - phi)
    rho1 = alpha * (1 - beta * phi) / denom
    return max(1.0, 1 + 2 * rho1 / (1 - phi))

def solve_beta_for_gamma(alpha, target_gamma):
    """Finds the beta parameter corresponding to a target Gamma."""
    if target_gamma <= 1.0: return 0.0
    lo, hi = 0.0, 1.0 - alpha - 1e-6
    for _ in range(100):
        mid = (lo + hi) / 2
        if compute_gamma_exact(alpha, mid) < target_gamma: lo = mid
        else: hi = mid
    return mid

def strict_cusum(stream, delta_P, threshold):
    """One-sided Strict CUSUM detector. Returns index of crossing or -1."""
    S = 0.0
    for t in range(len(stream)):
        S = max(0.0, S + stream[t] - delta_P)
        if S > threshold: return t
    return -1

# --- QMLE ESTIMATION & FILTERING ---
def _garch_nll(params, eps, var_emp):
    """Negative log-likelihood function for Gaussian QMLE GARCH(1,1) with Variance Targeting."""
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
    """
    Fits GARCH(1,1) via Quasi-Maximum Likelihood Estimation (QMLE).
    Strictly trained on in-sample data. Variance targeting applied.
    """
    var_emp = np.var(eps_warmup)
    init = [0.05, 0.90]
    bounds = [(1e-6, 0.5), (1e-6, 0.99)]
    constraints = {'type': 'ineq', 'fun': lambda x: 0.999 - (x[0] + x[1])}
    
    try:
        res = minimize(_garch_nll, init, args=(eps_warmup, var_emp), 
                       method='SLSQP', bounds=bounds, constraints=constraints)
        a, b = res.x if res.success else init
        
        # Enforce strict bounds natively to prevent divergent inference
        if a + b >= 0.999 or a < 0 or b < 0:
            a, b = init
            converged = False
        else:
            converged = res.success and max(abs(a - 0.05), abs(b - 0.90)) > 1e-6
            
        return (var_emp * (1.0 - a - b), a, b), converged
    except Exception:
        return (var_emp * (1.0 - init[0] - init[1]), init[0], init[1]), False

def filter_sigma2(eps, omega, alpha, beta, var_init):
    """
    Filters conditional variance recursively using FROZEN parameters.
    Ensures zero look-ahead by accepting var_init computed on warmup.
    """
    n = len(eps)
    sigma2 = np.zeros(n)
    sigma2[0] = var_init
    for t in range(1, n):
        sigma2[t] = omega + alpha * eps[t-1]**2 + beta * sigma2[t-1]
        if sigma2[t] < 1e-10: sigma2[t] = 1e-10
    return sigma2

# --- EXPERIMENTAL PROTOCOLS ---

def protocol_3a(n_streams=200, n_warmup=2000, n_eval=5000, alpha=0.08):
    print("\n--- PROTOCOL 3A: FPR Well-Specified (H0) ---")
    gamma_targets = [1.0, 5.0, 11.58, 30.0, 50.0, 90.0, 140.0, 200.0]
    results = []
    
    for gamma in gamma_targets:
        beta = solve_beta_for_gamma(alpha, gamma)
        gamma_actual = compute_gamma_exact(alpha, beta) if gamma > 1.0 else 1.0
        a_sim, b_sim = (alpha, beta) if gamma > 1.0 else (0.0, 0.0)
        omega = 0.01 * (1 - a_sim - b_sim)
        
        f_uncal, f_recalib, f_eco, f_ml = 0, 0, 0, 0
        
        for s in range(n_streams):
            eps = simulate_garch11(n_warmup + n_eval, omega, a_sim, b_sim, seed=s*77)
            
            # 1. Uncalibrated & 2. Recalibrated (Continuous)
            x = eps**2
            mu_x, sig_x = np.mean(x[:n_warmup]), np.std(x[:n_warmup])
            z_raw = (x[n_warmup:] - mu_x) / max(sig_x, 1e-8)
            
            if strict_cusum(z_raw, 0.5, 65.0) >= 0: f_uncal += 1
            if strict_cusum(z_raw, 0.5, 65.0 * gamma_actual) >= 0: f_recalib += 1
                
            # 3. Econometric Baseline (QMLE)
            eps_warmup = eps[:n_warmup]
            (w_h, a_h, b_h), _ = fit_garch_qmle(eps_warmup)
            
            sigma2_full = filter_sigma2(eps, w_h, a_h, b_h, np.var(eps_warmup))
            z_hat = eps / np.sqrt(sigma2_full)
            x_eco = z_hat**2
            
            mu_eco, sig_eco = np.mean(x_eco[:n_warmup]), np.std(x_eco[:n_warmup])
            z_eco = (x_eco[n_warmup:] - mu_eco) / max(sig_eco, 1e-8)
            if strict_cusum(z_eco, 0.5, 65.0) >= 0: f_eco += 1
                
            # 4. ML Sign Pipeline
            b = (eps[n_warmup:] > 0).astype(float) - 0.5
            if strict_cusum(b, 0.1, 10.0) >= 0: f_ml += 1
            
        res = {"Gamma": gamma_actual, "Uncal": f_uncal/n_streams, "Recalib": f_recalib/n_streams, 
               "Eco": f_eco/n_streams, "ML": f_ml/n_streams}
        results.append(res)
        print(f"Gamma={gamma_actual:5.1f} | Uncal: {res['Uncal']:.2f} | Recalib: {res['Recalib']:.2f} | Eco: {res['Eco']:.2f} | ML: {res['ML']:.2f}")

    df = pd.DataFrame(results)
    df.to_csv(FIGURES_DIR / "protocol_3a_fpr_baseline_v2.csv", index=False)
    return df

def wilson_ci(p_hat, n, z=1.96):
    if n == 0: return 0.0, 0.0
    center = (p_hat + z**2 / (2*n)) / (1 + z**2 / n)
    half_width = z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return max(0.0, center - half_width), min(1.0, center + half_width)

def protocol_3b(n_seeds=100, n_warmup=2000, n_eval=5000, alpha=0.08):
    print("\n--- PROTOCOL 3B: ADD Abrupt Shift (Commensurable) ---")
    gamma_targets = [1.0, 5.0, 11.58, 30.0, 50.0, 90.0, 140.0, 200.0]
    c_grid = [0.0, 0.5, 1.0, 2.0, 5.0, 10.0]
    results_add = []
    results_fpr = []
    
    for gamma in gamma_targets:
        beta = solve_beta_for_gamma(alpha, gamma)
        gamma_actual = compute_gamma_exact(alpha, beta) if gamma > 1.0 else 1.0
        a_sim, b_sim = (alpha, beta) if gamma > 1.0 else (0.0, 0.0)
        omega = 0.01 * (1 - a_sim - b_sim)
        sigma_unc = np.sqrt(omega / (1 - a_sim - b_sim)) if gamma > 1.0 else np.sqrt(0.01)
        
        gam_results = {c: {"adds_recalib": [], "adds_eco_l2": [], "adds_eco_l1": [], "adds_ml": []} for c in c_grid}
        
        for s in range(n_seeds):
            eps = simulate_garch11(n_warmup + n_eval, omega, a_sim, b_sim, seed=s*77 + 99)
            
            x = eps**2
            mu_x, sig_x = np.mean(x[:n_warmup]), np.std(x[:n_warmup])
            
            eps_warmup = eps[:n_warmup]
            (w_h, a_h, b_h), _ = fit_garch_qmle(eps_warmup)
            sigma2_full = filter_sigma2(eps, w_h, a_h, b_h, np.var(eps_warmup))
            
            z_hat_unshifted = eps / np.sqrt(sigma2_full)
            x_eco_unshifted = z_hat_unshifted**2
            mu_eco = np.mean(x_eco_unshifted[:n_warmup])
            sig_eco = np.std(x_eco_unshifted[:n_warmup])
            
            for c in c_grid:
                eps_shifted = eps[n_warmup:].copy() + c * sigma_unc
                
                # 1. Recalib
                z_raw = (eps_shifted**2 - mu_x) / max(sig_x, 1e-8)
                al_r = strict_cusum(z_raw, 0.5, 65.0 * gamma_actual)
                if al_r >= 0: gam_results[c]["adds_recalib"].append(al_r)
                
                # 2. Eco L2
                z_eco_hat = eps_shifted / np.sqrt(sigma2_full[n_warmup:])
                z_eco = (z_eco_hat**2 - mu_eco) / max(sig_eco, 1e-8)
                al_eco = strict_cusum(z_eco, 0.5, 65.0)
                if al_eco >= 0: gam_results[c]["adds_eco_l2"].append(al_eco)
                
                # 3. Eco L1
                al_eco_l1 = strict_cusum(z_eco_hat, 0.5, 10.0)
                if al_eco_l1 >= 0: gam_results[c]["adds_eco_l1"].append(al_eco_l1)
                
                # 4. ML
                b = (eps_shifted > 0).astype(float) - 0.5
                al_ml = strict_cusum(b, 0.1, 10.0)
                if al_ml >= 0: gam_results[c]["adds_ml"].append(al_ml)
                
        for c in c_grid:
            d = gam_results[c]
            det_r = len(d["adds_recalib"]) / n_seeds
            det_e2 = len(d["adds_eco_l2"]) / n_seeds
            det_e1 = len(d["adds_eco_l1"]) / n_seeds
            det_ml = len(d["adds_ml"]) / n_seeds
            
            ci_low_r, ci_high_r = wilson_ci(det_r, n_seeds)
            ci_low_e2, ci_high_e2 = wilson_ci(det_e2, n_seeds)
            ci_low_e1, ci_high_e1 = wilson_ci(det_e1, n_seeds)
            ci_low_ml, ci_high_ml = wilson_ci(det_ml, n_seeds)
            
            if c == 0.0:
                res_fpr = {
                    "Gamma": gamma_actual,
                    "FPR_Recalib": det_r, "CI_low_Recalib": ci_low_r, "CI_high_Recalib": ci_high_r,
                    "FPR_Eco_L2": det_e2, "CI_low_Eco_L2": ci_low_e2, "CI_high_Eco_L2": ci_high_e2,
                    "FPR_Eco_L1": det_e1, "CI_low_Eco_L1": ci_low_e1, "CI_high_Eco_L1": ci_high_e1,
                    "FPR_ML": det_ml, "CI_low_ML": ci_low_ml, "CI_high_ML": ci_high_ml
                }
                results_fpr.append(res_fpr)
                print(f"Gamma={gamma_actual:5.1f} | c=0.0 | FPR_Recalib: {det_r:.2f} | FPR_Eco_L2: {det_e2:.2f} | FPR_Eco_L1: {det_e1:.2f} | FPR_ML: {det_ml:.2f}")
            else:
                res_add = {
                    "c": c,
                    "Gamma": gamma_actual,
                    "ADD_Recalib": np.nanmean(d["adds_recalib"]) if d["adds_recalib"] else np.nan,
                    "ADD_Eco_L2": np.nanmean(d["adds_eco_l2"]) if d["adds_eco_l2"] else np.nan,
                    "ADD_Eco_L1": np.nanmean(d["adds_eco_l1"]) if d["adds_eco_l1"] else np.nan,
                    "ADD_ML": np.nanmean(d["adds_ml"]) if d["adds_ml"] else np.nan,
                    "DetRate_Recalib": det_r, "DetRate_Eco_L2": det_e2,
                    "DetRate_Eco_L1": det_e1, "DetRate_ML": det_ml
                }
                results_add.append(res_add)
                print(f"Gamma={gamma_actual:5.1f} | c={c:4.1f} | ADD_Recalib: {res_add['ADD_Recalib']:6.1f} | ADD_Eco_L2: {res_add['ADD_Eco_L2']:6.1f} | ADD_Eco_L1: {res_add['ADD_Eco_L1']:6.1f} | ADD_ML: {res_add['ADD_ML']:6.1f}")

    df_add = pd.DataFrame(results_add)
    df_add.to_csv(FIGURES_DIR / "protocol_3b_add_baseline_v2.csv", index=False)
    df_fpr = pd.DataFrame(results_fpr)
    df_fpr.to_csv(FIGURES_DIR / "protocol_3b_fpr_arms.csv", index=False)
    return df_add

def protocol_3c(n_streams=200, n_warmup=2000, n_eval=5000):
    # Forçage à 1000 flux pour garantir la résolution statistique du FPR
    n_streams = 1000 if n_streams < 1000 else n_streams
    print("\n--- PROTOCOL 3C: Misspecification (DGP = GJR) ---")
    alpha_dgp = 0.05
    beta_dgp = 0.80
    gamma_lev_list = [0.0, 0.10, 0.20, 0.28]
    results = []
    
    for g_lev in gamma_lev_list:
        omega_dgp = 0.01 * (1 - alpha_dgp - beta_dgp - g_lev/2.0)
        
        f_eco, f_ml = 0, 0
        lb_rejs_eco, lb_rejs_ml = [], []
        
        for s in range(n_streams):
            eps = simulate_gjr11(n_warmup + n_eval, omega_dgp, alpha_dgp, g_lev, beta_dgp, seed=s*42 + 888)
            
            # Econometric Baseline (Asymptotic Misspecified Limit per Section 5.2)
            # DO NOT FIT EMPIRICALLY. Use the symmetric population limit of the misspecified model.
            a_sym = alpha_dgp + g_lev / 2.0
            b_sym = beta_dgp
            w_sym = omega_dgp
            
            sigma2_full = filter_sigma2(eps, w_sym, a_sym, b_sym, np.var(eps[:n_warmup]))
            z_hat = eps / np.sqrt(sigma2_full)
            x_eco = z_hat**2
            
            mu_eco, sig_eco = np.mean(x_eco[:n_warmup]), np.std(x_eco[:n_warmup])
            z_eco = (x_eco[n_warmup:] - mu_eco) / max(sig_eco, 1e-8)
            
            if strict_cusum(z_eco, 0.5, 65.0) >= 0: f_eco += 1
                
            # ML Pipeline
            b_stream = (eps[n_warmup:] > 0).astype(float) - 0.5
            if strict_cusum(b_stream, 0.1, 10.0) >= 0: f_ml += 1
                
            # Ljung-Box Tests (Lag 20)
            # 1. On filtered squared residuals
            lb_eco = acorr_ljungbox(x_eco[n_warmup:], lags=[20], return_df=True)['lb_pvalue'].iloc[0]
            lb_rejs_eco.append(1.0 if lb_eco < 0.05 else 0.0)
            
            # 2. On binary errors
            lb_ml = acorr_ljungbox(b_stream, lags=[20], return_df=True)['lb_pvalue'].iloc[0]
            lb_rejs_ml.append(1.0 if lb_ml < 0.05 else 0.0)
            
        res = {"GammaLev": g_lev, 
               "FPR_Eco": f_eco/n_streams, 
               "FPR_ML": f_ml/n_streams,
               "LB_Reject_Eco": np.mean(lb_rejs_eco),
               "LB_Reject_ML": np.mean(lb_rejs_ml)}
        results.append(res)
        print(f"Lev={g_lev:.2f} | FPR Eco: {res['FPR_Eco']:.2f} | FPR ML: {res['FPR_ML']:.2f} | LB_Eco: {res['LB_Reject_Eco']:.2f} | LB_ML: {res['LB_Reject_ML']:.2f}")
        
    df = pd.DataFrame(results)
    df.to_csv(FIGURES_DIR / "protocol_3c_misspec_v2.csv", index=False)
    return df

def protocol_3d_warmup_sensitivity(n_streams=1000, n_eval=5000):
    print("\n--- PROTOCOL 3D: Warm-up Sensitivity ---")
    gamma_lev_list = [0.0, 0.28]
    n_warmup_list = [250, 500, 1000, 2000]
    alpha_dgp = 0.05
    beta_dgp = 0.80
    results = []
    
    for g_lev in gamma_lev_list:
        omega_dgp = 1.0 * (1 - alpha_dgp - beta_dgp - g_lev/2.0)
        
        for nw in n_warmup_list:
            f_eco = 0
            f_ml = 0
            n_fails = 0
            a_hats = []
            b_hats = []
            
            for s in range(n_streams):
                eps = simulate_gjr11(nw + n_eval, omega_dgp, alpha_dgp, g_lev, beta_dgp, seed=s*101 + nw)
                eps_wu = eps[:nw]
                eps_eval = eps[nw:]
                
                # QMLE on warmup
                (w_h, a_h, b_h), converged = fit_garch_qmle(eps_wu)
                if not converged:
                    n_fails += 1
                a_hats.append(a_h)
                b_hats.append(b_h)
                
                # Filter eval stream
                var_emp_wu = np.var(eps_wu)
                sigma2_eval = filter_sigma2(eps_eval, w_h, a_h, b_h, var_emp_wu)
                
                z_hat = eps_eval / np.sqrt(sigma2_eval)
                x_eco = z_hat**2
                
                # Standardize L2 stream
                sigma2_wu = filter_sigma2(eps_wu, w_h, a_h, b_h, var_emp_wu)
                x_eco_wu = (eps_wu / np.sqrt(sigma2_wu))**2
                mu_eco, sig_eco = np.mean(x_eco_wu), np.std(x_eco_wu)
                
                z_eco = (x_eco - mu_eco) / max(sig_eco, 1e-8)
                if strict_cusum(z_eco, 0.5, 65.0) >= 0:
                    f_eco += 1
                    
                b_stream = (eps_eval > 0).astype(float) - 0.5
                if strict_cusum(b_stream, 0.1, 10.0) >= 0:
                    f_ml += 1
                    
            res = {
                "n_warmup": nw,
                "gamma_lev": g_lev,
                "FPR_Eco": f_eco / n_streams,
                "FPR_ML": f_ml / n_streams,
                "share_nonconverged": n_fails / n_streams,
                "alpha_hat_10": np.percentile(a_hats, 10),
                "alpha_hat_50": np.percentile(a_hats, 50),
                "alpha_hat_90": np.percentile(a_hats, 90),
                "beta_hat_10": np.percentile(b_hats, 10),
                "beta_hat_50": np.percentile(b_hats, 50),
                "beta_hat_90": np.percentile(b_hats, 90),
            }
            results.append(res)
            print(f"g_lev={g_lev:.2f} | nw={nw:4d} | FPR Eco: {res['FPR_Eco']:.3f} | FPR ML: {res['FPR_ML']:.3f} | Fails: {res['share_nonconverged']:.2%}")

    df = pd.DataFrame(results)
    df.to_csv(FIGURES_DIR / "protocol_3d_warmup_sensitivity.csv", index=False)
    return df

def generate_figure(df_a, df_b, df_c):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # --- PANEL A: FPR vs Gamma ---
    ax = axes[0]
    ax.axhline(0.05, color='gray', linestyle='--', linewidth=2, label="Nominal FPR (0.05)")
    ax.plot(df_a["Gamma"], df_a["Uncal"], 'o-', color=C_RAW, label="Uncalibrated")
    ax.plot(df_a["Gamma"], df_a["Recalib"], '^-', color=C_RECALIB, label=r"$\Gamma$-recalibrated")
    ax.plot(df_a["Gamma"], df_a["Eco"], 'D-', color=C_ECO, label="Econometric baseline (plain-GARCH QMLE)")
    ax.plot(df_a["Gamma"], df_a["ML"], 's-', color=C_ML, label="ML sign pipeline (frozen binarizer)")
    ax.set_title("False Positive Rate under $H_0$")
    ax.set_xlabel(r"GARCH Penalty Factor $\Gamma$")
    ax.set_ylabel("FPR")
    ax.legend()
    ax.grid(alpha=0.3)
    
    # --- PANEL B: ADD vs Gamma ---
    ax = axes[1]
    df_b_plot = df_b[df_b["c"] == 2.0] if "c" in df_b.columns else df_b
    ax.plot(df_b_plot["Gamma"], df_b_plot["ADD_Recalib"], '^-', color=C_RECALIB, label=r"$\Gamma$-recalibrated")
    ax.plot(df_b_plot["Gamma"], df_b_plot["ADD_Eco_L2"], 'D-', color=C_ECO, label="Econometric baseline L2")
    ax.plot(df_b_plot["Gamma"], df_b_plot["ADD_Eco_L1"], marker='p', linestyle='-', color='#8C4A7C', label="Econometric L1 (Standardized Residuals)")
    ax.plot(df_b_plot["Gamma"], df_b_plot["ADD_ML"], 's-', color=C_ML, label="ML sign pipeline (frozen binarizer)")
    ax.set_title("Average Detection Delay (Abrupt Shift c=2.0)")
    ax.set_xlabel(r"GARCH Penalty Factor $\Gamma$")
    ax.set_ylabel("Average Detection Delay (steps)")
    ax.legend()
    ax.grid(alpha=0.3)
    
    # --- PANEL C: Misspecification ---
    ax = axes[2]
    ax.axhline(0.05, color='gray', linestyle='--', linewidth=2, label="Nominal Rate (0.05)")
    ax.plot(df_c["GammaLev"], df_c["FPR_Eco"], 'D-', color=C_ECO, label="FPR: Econometric baseline")
    ax.plot(df_c["GammaLev"], df_c["FPR_ML"], 's-', color=C_ML, label="FPR: ML sign pipeline")
    ax.plot(df_c["GammaLev"], df_c["LB_Reject_Eco"], 'D--', color=C_ECO, alpha=0.7, label="LB Reject: Econometric baseline")
    ax.plot(df_c["GammaLev"], df_c["LB_Reject_ML"], 's--', color=C_ML, alpha=0.7, label="LB Reject: ML sign pipeline")
    ax.set_title("Robustness to GJR Misspecification")
    ax.set_xlabel(r"Leverage Parameter $\gamma_{lev}$")
    ax.set_ylabel("Rate (FPR / Ljung-Box Rejection)")
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "Fig10_Econometric_Baseline.png")
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true", help="Run with fewer streams for testing")
    args = parser.parse_args()
    
    n_str = 20 if args.fast else 200
    n_sds = 10 if args.fast else 100
    
    t0 = time.time()
    df_a = protocol_3a(n_streams=n_str)
    df_b = protocol_3b(n_seeds=n_sds)
    df_c = protocol_3c(n_streams=n_str)
    df_d = protocol_3d_warmup_sensitivity(n_streams=n_str)
    
    generate_figure(df_a, df_b, df_c)
    print(f"\nExecution completed in {time.time()-t0:.1f}s.")