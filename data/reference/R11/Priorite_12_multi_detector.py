#!/usr/bin/env python3
r"""
==========================================================================
EXPERIMENTAL PROTOCOLS — Mission 12 (Multi-Detector Universality & PHT)
Author: Raphaël Minato
Target: KDD 2027
==========================================================================
Exp A: Validates the Page-Hinkley Test (PHT) on the Data pipeline, proving 
       that as a cumulative statistic, it requires the Siegmund \Gamma scaling
       (where \Gamma is the GARCH penalty factor, defined as the normalized 
       spectral density at zero frequency of the monitored statistic).
Exp B: Validates the Concept Pipeline Universality across 4 detector families 
       (CUSUM, PHT, ADWIN, DDM, EDDM), demonstrating distribution-free FPR 
       and flat ADD under the Sign-Task Whitening Theorem.
Exp C: Evaluates ADWIN Blind Zone vs Concept speedup (Magnitude grid).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path
import time
import warnings
import argparse
import hashlib
from tqdm import tqdm
from joblib import Parallel, delayed

try:
    from river import drift
    RIVER_AVAILABLE = True
except ImportError:
    RIVER_AVAILABLE = False
    warnings.warn("river package not found. DDM/EDDM/ADWIN will fail.")

warnings.filterwarnings("ignore")

# --- DIRECTORY SETUP ---
# Following FAIR principles, paths are resolved relative to the script location.
BASE_DIR = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# --- PLOT FORMATTING ---
plt.rcParams.update({
    "figure.figsize": (14, 6.5), 
    "font.size": 12, 
    "figure.dpi": 200, 
    "axes.titlesize": 13,
    "axes.titleweight": "bold"
})
COLORS = {"CUSUM": "#1f77b4", "PHT": "#ff7f0e", "ADWIN": "#2ca02c", "DDM": "#d62728", "EDDM": "#9467bd"}

# --- UTILITIES ---
def get_deterministic_seed(*args):
    """
    Generates a strictly deterministic integer seed from arbitrary parameters.
    Upgraded to FAIR standards: enforces hexadecimal representation for floats 
    to prevent cross-platform stringification drift, and strict UTF-8 encoding.
    """
    def format_arg(arg):
        if isinstance(arg, (float, np.floating)):
            return float(arg).hex()
        return str(arg)
        
    s = "_".join(map(format_arg, args))
    h = hashlib.md5(s.encode('utf-8')).hexdigest()
    # Preserves 128-bit collision-free entropy via a 4x32-bit tuple for the legacy RandomState
    return tuple(int(h[i:i+8], 16) for i in range(0, 32, 8))

def wilson_interval(p, n, z=1.96):
    """Calculates the Wilson score interval for binomial proportions."""
    if n == 0: return 0.0, 0.0
    denom = 1 + z**2 / n
    center = (p + z**2 / (2*n)) / denom
    spread = z * np.sqrt(p*(1-p)/n + z**2 / (4*n**2)) / denom
    return center - spread, center + spread

# --- GARCH SIMULATORS ---
def simulate_garch11(n, omega, alpha, beta, nu=7.0, seed=42):
    # Strict temporal reproducibility: Generator algorithms mutate across NumPy versions.
    # We MUST use the legacy RandomState (MT19937) API, which is mathematically frozen.
    rng = np.random.RandomState(seed)
    sigma2_unc = omega / (1 - alpha - beta)
    eps = np.zeros(n); sigma2 = np.zeros(n)
    sigma2[0] = sigma2_unc
    scale = np.sqrt((nu - 2) / nu)
    z = rng.standard_t(df=nu, size=n) * scale
    eps[0] = np.sqrt(sigma2[0]) * z[0]
    for t in range(1, n):
        sigma2[t] = omega + alpha * eps[t-1]**2 + beta * sigma2[t-1]
        sigma2[t] = min(sigma2[t], 1e4 * sigma2_unc)
        eps[t] = np.sqrt(sigma2[t]) * z[t]
    return eps

def compute_gamma_exact(alpha, beta):
    phi = alpha + beta
    if phi >= 1.0: return np.inf
    denom = 1 - 2 * alpha * beta - beta**2
    if denom <= 0: return (1 + phi) / (1 - phi)
    rho1 = alpha * (1 - beta * phi) / denom
    return max(1.0, 1 + 2 * rho1 / (1 - phi))

def solve_beta_for_gamma(alpha, target_gamma):
    if target_gamma <= 1.0: return 0.0
    lo, hi = 0.0, 1.0 - alpha - 1e-6
    for _ in range(100):
        mid = (lo + hi) / 2
        if compute_gamma_exact(alpha, mid) < target_gamma: lo = mid
        else: hi = mid
    return mid

# --- DETECTORS ---
def strict_cusum(stream, delta, threshold):
    S = 0.0
    for t in range(len(stream)):
        S = max(0.0, S + stream[t] - delta)
        if S > threshold: return t
    return -1

def strict_pht(stream, delta, threshold, onset=0):
    m = 0.0
    M = 0.0
    mean_x = 0.0
    for t in range(len(stream)):
        val = stream[t]
        mean_x = mean_x + (val - mean_x) / (t + 1)
        m += val - mean_x - delta
        if m < M: M = m
        if m - M > threshold and t >= onset: 
            return t - onset
    return -1

def adwin_like_detector_naive(stream, delta=5e-4, gamma=1.0, min_window=30, onset=0):
    window = []
    for t in range(len(stream)):
        window.append(stream[t])
        n = len(window)
        if n < 2 * min_window: continue
        split = n // 2
        w0, w1 = np.array(window[:split]), np.array(window[split:])
        m_harm = 1.0 / (1.0/len(w0) + 1.0/len(w1))
        eps_cut = np.sqrt(2.0 * gamma * np.log(2.0 / delta) / m_harm)
        if abs(np.mean(w0) - np.mean(w1)) > eps_cut and t >= onset:
            return t - onset
    return -1

def adwin_like_detector(stream, delta=5e-4, gamma=1.0, min_window=30, onset=0):
    """Optimized prefix-sum verbatim replica of adwin_like_detector_naive (O(1) per step)."""
    N = len(stream)
    if N < 2 * min_window:
        return -1
    S_arr = np.zeros(N + 1)
    eps_factor = np.sqrt(2.0 * gamma * np.log(2.0 / delta))
    
    for t in range(N):
        S_arr[t+1] = S_arr[t] + stream[t]
        n = t + 1
        if n < 2 * min_window: continue
        
        split = n // 2
        n0 = split
        n1 = n - split
        
        mu0 = S_arr[split] / n0
        mu1 = (S_arr[n] - S_arr[split]) / n1
        
        m_harm = 1.0 / (1.0/n0 + 1.0/n1)
        eps_cut = eps_factor / np.sqrt(m_harm)
        
        if abs(mu0 - mu1) > eps_cut and t >= onset:
            return t - onset
    return -1

def test_adwin_equivalence():
    print("--- Running ADWIN Equivalence Test ---")
    rng = np.random.RandomState(42)
    for i in range(50):
        stream = rng.standard_normal(300)
        if i % 2 == 0: stream[150:] += 2.0
        res_naive = adwin_like_detector_naive(stream, onset=100)
        res_fast = adwin_like_detector(stream, onset=100)
        if res_naive != res_fast:
            raise AssertionError(f"Mismatch on stream {i}: naive={res_naive}, fast={res_fast}")
    print("SUCCESS: Prefix-sums ADWIN perfectly matches naive ADWIN.")
    return True

def get_river_detector(name, **kwargs):
    if name == "ADWIN":
        return drift.ADWIN(**kwargs)
    elif name == "DDM":
        return drift.binary.DDM(**kwargs) if hasattr(drift, 'binary') else drift.DDM(**kwargs)
    elif name == "EDDM":
        return drift.binary.EDDM(**kwargs) if hasattr(drift, 'binary') else drift.EDDM(**kwargs)
    raise ValueError(f"Unknown river detector: {name}")

def run_river_detector(name, stream, onset=0, **kwargs):
    if not RIVER_AVAILABLE:
        return -1
    det = get_river_detector(name, **kwargs)
    for t in range(onset):
        det.update(stream[t])
    for t in range(onset, len(stream)):
        det.update(stream[t])
        if det.drift_detected:
            return t - onset
    return -1

# --- EXPERIMENT A: PHT DATA SCALING ---
def calibrate_pht_iid(n_streams=2000, n_steps=5000, target_fpr=0.05, delta=0.5, stream_type='continuous', seed=42):
    rng = np.random.RandomState(seed)
    max_stats = np.zeros(n_streams)
    nu = 7.0
    scale = np.sqrt((nu - 2) / nu)
    for i in range(n_streams):
        if stream_type == 'continuous':
            z = rng.standard_t(df=nu, size=n_steps) * scale
            z_sq = z**2
            stream = (z_sq - np.mean(z_sq)) / max(np.std(z_sq), 1e-8)
        else:
            stream = (rng.uniform(size=n_steps) < 0.5).astype(int) - 0.5
        
        m = 0.0; M = 0.0; mean_x = 0.0; max_diff = 0.0
        for t in range(n_steps):
            val = stream[t]
            mean_x = mean_x + (val - mean_x) / (t + 1)
            m += val - mean_x - delta
            if m < M: M = m
            if m - M > max_diff: max_diff = m - M
        max_stats[i] = max_diff
    return np.percentile(max_stats, 100 * (1 - target_fpr))

def worker_exp_a(params):
    gamma, s, omega, alpha, beta, lambda_iid, delta = params
    seed = get_deterministic_seed("expA", gamma, s)
    eps = simulate_garch11(7000, omega, alpha, beta, seed=seed)
    
    f_warmup = eps[:2000]**2
    mu_f = np.mean(f_warmup)
    sig_f = np.std(f_warmup)
    
    e_data = (eps[2000:]**2 - mu_f) / max(sig_f, 1e-8)
    
    fp_raw = strict_pht(e_data, delta, lambda_iid) != -1
    fp_sqrt = strict_pht(e_data, delta, lambda_iid * np.sqrt(gamma)) != -1
    fp_gamma = strict_pht(e_data, delta, lambda_iid * gamma) != -1
    
    return gamma, fp_raw, fp_sqrt, fp_gamma

def run_experiment_a(n_seeds, lambda_ph_iid, alpha=0.08, delta_pht=0.5, n_jobs=-1):
    print("\n=== [1] EXPERIMENT A: PHT CALIBRATION & FPR ===")
    print(f"Calibrated PHT i.i.d. Threshold (Data Continuous): {lambda_ph_iid:.2f}")
    
    grid_a = [1.17, 6.44, 11.89, 17.33, 22.78, 28.22, 33.67, 39.11, 44.56, 50.0,
              60.0, 75.56, 91.11, 106.67, 122.22, 137.78, 153.33, 168.89, 184.44, 200.0]
    
    tasks = []
    for gamma in grid_a:
        beta = solve_beta_for_gamma(alpha, gamma)
        omega = 0.04 * (1 - alpha - beta)
        for s in range(n_seeds):
            tasks.append((gamma, s, omega, alpha, beta, lambda_ph_iid, delta_pht))
            
    res = Parallel(n_jobs=n_jobs)(delayed(worker_exp_a)(t) for t in tqdm(tasks))
    
    df_raw = pd.DataFrame(res, columns=["Gamma", "FP_raw", "FP_sqrt", "FP_gamma"])
    df = df_raw.groupby("Gamma").mean().reset_index()
    df.columns = ["Gamma", "FPR_raw", "FPR_sqrt", "FPR_gamma"]
    df.to_csv(FIGURES_DIR / "protocol_4a_pht_fpr.csv", index=False)
    
    # Certification of the theoretical claim made in the abstract
    max_fpr_raw = df["FPR_raw"].max()
    print(f"Certification: Maximum raw FPR under GARCH volatility = {max_fpr_raw:.2%}")
    if max_fpr_raw <= 0.80:
        warnings.warn(f"Abstract claim validation failed: Maximum FPR is {max_fpr_raw:.2%} (<= 80%).")
    else:
        print("SUCCESS: Abstract claim validation passed (FPR exceeds 80%).")
        
    return df

# --- EXPERIMENT B: CONCEPT UNIVERSALITY ---
def worker_exp_b_h0(params):
    gamma, s, omega, alpha, beta, lambda_ph_iid = params
    seed = get_deterministic_seed("expB_H0", gamma, s)
    eps = simulate_garch11(7000, omega, alpha, beta, seed=seed)
    
    e_bin = (eps[2000:] > 0).astype(int)
    e_bin_centered = e_bin - 0.5
    
    fp_cusum = strict_cusum(e_bin_centered, 0.1, 10.0) != -1
    fp_pht = strict_pht(e_bin_centered, 0.1, lambda_ph_iid) != -1
    fp_adwin = run_river_detector("ADWIN", e_bin, delta=0.002) != -1
    fp_ddm = run_river_detector("DDM", e_bin) != -1
    fp_eddm = run_river_detector("EDDM", e_bin) != -1
    
    return gamma, fp_cusum, fp_pht, fp_adwin, fp_ddm, fp_eddm

def worker_exp_b_h1(params):
    gamma, s, omega, alpha, beta, c, lambda_ph_iid = params
    sigma_unc = np.sqrt(omega / (1 - alpha - beta))
    Delta = c * sigma_unc
    
    seed = get_deterministic_seed("expB_H1", gamma, c, s)
    eps = simulate_garch11(7000, omega, alpha, beta, seed=seed)
    
    # CUSUM (Static known reference H0=0.0) -> Post-onset stream only
    eps_shifted_only = eps[2000:].copy() + Delta
    e_bin_centered = (eps_shifted_only > 0).astype(int) - 0.5
    al_cusum = strict_cusum(e_bin_centered, 0.1, 10.0)
    
    # Adaptive detectors (PHT, ADWIN, DDM, EDDM) -> Require full stream for H0 warmup
    eps_full = eps.copy()
    eps_full[2000:] += Delta
    e_bin_full = (eps_full > 0).astype(int)
    e_bin_full_centered = e_bin_full - 0.5
    
    al_pht = strict_pht(e_bin_full_centered, 0.1, lambda_ph_iid, onset=2000)
    al_adwin = run_river_detector("ADWIN", e_bin_full, onset=2000, delta=0.002)
    al_ddm = run_river_detector("DDM", e_bin_full, onset=2000)
    al_eddm = run_river_detector("EDDM", e_bin_full, onset=2000)
    
    return gamma, al_cusum, al_pht, al_adwin, al_ddm, al_eddm

def run_experiment_b(n_seeds, lambda_ph_iid_concept, alpha=0.08, n_jobs=-1):
    print(f"\n=== [2] EXPERIMENT B: CONCEPT UNIVERSALITY (n_seeds={n_seeds}) ===")
    print(f"Calibrated PHT i.i.d. Threshold (Concept Binary): {lambda_ph_iid_concept:.2f}")
    grid_b = [1.17, 6.44, 11.89, 17.33, 22.78, 28.22, 33.67, 39.11, 44.56, 50.0,
              60.0, 75.56, 91.11, 106.67, 122.22, 137.78, 153.33, 168.89, 184.44, 200.0]
    
    tasks_h0, tasks_h1 = [], []
    for gamma in grid_b:
        beta = solve_beta_for_gamma(alpha, gamma)
        omega = 0.04 * (1 - alpha - beta)
        for s in range(n_seeds):
            tasks_h0.append((gamma, s, omega, alpha, beta, lambda_ph_iid_concept))
            tasks_h1.append((gamma, s, omega, alpha, beta, 1.5, lambda_ph_iid_concept))
            
    res_h0 = Parallel(n_jobs=n_jobs)(delayed(worker_exp_b_h0)(t) for t in tqdm(tasks_h0))
    df_h0_raw = pd.DataFrame(res_h0, columns=["Gamma", "FP_CUSUM", "FP_PHT", "FP_ADWIN", "FP_DDM", "FP_EDDM"])
    
    h0_agg = []
    for gamma in grid_b:
        sub = df_h0_raw[df_h0_raw["Gamma"] == gamma]
        row = {"Gamma": gamma}
        for det in ["CUSUM", "PHT", "ADWIN", "DDM", "EDDM"]:
            p = sub[f"FP_{det}"].mean()
            low, high = wilson_interval(p, len(sub))
            row[f"FPR_{det}"] = p
            row[f"FPR_{det}_low"] = low
            row[f"FPR_{det}_high"] = high
        h0_agg.append(row)
    pd.DataFrame(h0_agg).to_csv(FIGURES_DIR / "protocol_4b_multiconcept_fpr.csv", index=False)

    res_h1 = Parallel(n_jobs=n_jobs)(delayed(worker_exp_b_h1)(t) for t in tqdm(tasks_h1))
    df_h1_raw = pd.DataFrame(res_h1, columns=["Gamma", "AL_CUSUM", "AL_PHT", "AL_ADWIN", "AL_DDM", "AL_EDDM"])
    
    h1_agg = []
    for gamma in grid_b:
        sub = df_h1_raw[df_h1_raw["Gamma"] == gamma]
        row = {"Gamma": gamma}
        for det in ["CUSUM", "PHT", "ADWIN", "DDM", "EDDM"]:
            als = sub[f"AL_{det}"].values
            detected = als[als != -1]
            det_rate = len(detected) / len(als)
            row[f"DetRate_{det}"] = det_rate
            row[f"ADD_{det}"] = np.mean(detected) if det_rate >= 0.5 else np.nan
            row[f"SEM_{det}"] = np.std(detected)/np.sqrt(len(detected)) if det_rate >= 0.5 else np.nan
        h1_agg.append(row)
    df_c = pd.DataFrame(h1_agg)
    df_c.to_csv(FIGURES_DIR / "protocol_4c_multiconcept_add.csv", index=False)
    return df_c

# --- EXPERIMENT C: ADWIN MAGNITUDE ---
def worker_exp_c(params):
    c, s, omega, alpha, beta, gamma = params
    sigma_unc = np.sqrt(omega / (1 - alpha - beta))
    Delta = c * sigma_unc
    seed = get_deterministic_seed("expC", c, s)
    eps = simulate_garch11(7000, omega, alpha, beta, seed=seed)
    
    f_warmup = eps[:2000]**2
    mu_f = np.mean(f_warmup)
    sig_f = np.std(f_warmup)
    
    eps_full = eps.copy()
    eps_full[2000:] += Delta
    
    e_data_full = (eps_full**2 - mu_f) / max(sig_f, 1e-8)
    e_bin_full = (eps_full > 0).astype(int)
    
    al_data = adwin_like_detector(e_data_full, delta=5e-4, gamma=gamma, min_window=30, onset=2000)
    al_concept = run_river_detector("ADWIN", e_bin_full, onset=2000, delta=0.002)
    
    return c, al_data, al_concept

def run_experiment_c(n_seeds, alpha=0.08, gamma_c=11.58, n_jobs=-1):
    print(f"\n=== [3] EXPERIMENT C: ADWIN BLIND ZONE (n_seeds={n_seeds}) ===")
    grid_c = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0]
    beta_c = solve_beta_for_gamma(alpha, gamma_c)
    omega_c = 0.04 * (1 - alpha - beta_c)
    
    tasks = []
    for c_mag in grid_c:
        for s in range(n_seeds):
            tasks.append((c_mag, s, omega_c, alpha, beta_c, gamma_c))
            
    res = Parallel(n_jobs=n_jobs)(delayed(worker_exp_c)(t) for t in tqdm(tasks))
    df_raw = pd.DataFrame(res, columns=["c", "AL_Data", "AL_Concept"])
    
    agg = []
    for c_mag in grid_c:
        sub = df_raw[df_raw["c"] == c_mag]
        d_data = sub["AL_Data"].values; d_data = d_data[d_data != -1]
        d_conc = sub["AL_Concept"].values; d_conc = d_conc[d_conc != -1]
        
        dr_data = len(d_data)/len(sub); dr_conc = len(d_conc)/len(sub)
        add_data = np.mean(d_data) if dr_data >= 0.5 else np.nan
        sem_data = np.std(d_data)/np.sqrt(len(d_data)) if dr_data >= 0.5 else np.nan
        add_conc = np.mean(d_conc) if dr_conc >= 0.5 else np.nan
        sem_conc = np.std(d_conc)/np.sqrt(len(d_conc)) if dr_conc >= 0.5 else np.nan
        
        dr_data_low, dr_data_high = wilson_interval(dr_data, len(sub))
        dr_conc_low, dr_conc_high = wilson_interval(dr_conc, len(sub))
        
        agg.append({
            "c": c_mag, 
            "DetRate_Data": dr_data, "DetRate_Data_low": dr_data_low, "DetRate_Data_high": dr_data_high,
            "ADD_Data": add_data, "SEM_Data": sem_data,
            "DetRate_Concept": dr_conc, "DetRate_Concept_low": dr_conc_low, "DetRate_Concept_high": dr_conc_high,
            "ADD_Concept": add_conc, "SEM_Concept": sem_conc,
            "Speedup": add_data/add_conc if pd.notna(add_data) and pd.notna(add_conc) else np.nan
        })
    df = pd.DataFrame(agg)
    df.to_csv(FIGURES_DIR / "protocol_4d_adwin_magnitude.csv", index=False)
    
    fpr_data_c0 = df[df["c"] == 0.0]["DetRate_Data"].values[0]
    fpr_concept_c0 = df[df["c"] == 0.0]["DetRate_Concept"].values[0]
    print(f"H0 Control (c=0.0) -> FPR_Data: {fpr_data_c0:.3f} | FPR_Concept: {fpr_concept_c0:.3f}")
    
    if not (0.02 <= fpr_data_c0 <= 0.15):
        msg = f"GATE FAILURE: FPR_Data(c=0) = {fpr_data_c0:.3f} not in [0.02, 0.15]"
        print(f"!!! {msg} !!!")
        
    return df

# --- EXPERIMENT D: DATA PIPELINE TAX ---
def worker_exp_d(params):
    gamma, s, omega, alpha, beta, lambda_cusum_iid, lambda_ph_iid = params
    sigma_unc = np.sqrt(omega / (1 - alpha - beta))
    Delta = 2.0 * sigma_unc
    
    seed = get_deterministic_seed("expD", gamma, s)
    eps_h0 = simulate_garch11(14000, omega, alpha, beta, seed=seed)
    
    f_warmup = eps_h0[:2000]**2
    mu_f = np.mean(f_warmup)
    sig_f = np.std(f_warmup)
    
    # H0 Stream
    e_data_h0 = (eps_h0**2 - mu_f) / max(sig_f, 1e-8)
    
    fp_cusum = strict_cusum(e_data_h0[2000:], delta=0.5, threshold=lambda_cusum_iid * gamma) != -1
    fp_pht = strict_pht(e_data_h0, delta=0.5, threshold=lambda_ph_iid * gamma, onset=2000) != -1
    fp_adwin = adwin_like_detector(e_data_h0, delta=5e-4, gamma=gamma, min_window=30, onset=2000) != -1
    
    # H1 Stream (c=2.0)
    eps_h1 = eps_h0.copy()
    eps_h1[2000:] += Delta
    e_data_h1 = (eps_h1**2 - mu_f) / max(sig_f, 1e-8)
    
    al_cusum = strict_cusum(e_data_h1[2000:], delta=0.5, threshold=lambda_cusum_iid * gamma)
    al_pht = strict_pht(e_data_h1, delta=0.5, threshold=lambda_ph_iid * gamma, onset=2000)
    al_adwin = adwin_like_detector(e_data_h1, delta=5e-4, gamma=gamma, min_window=30, onset=2000)
    
    return gamma, fp_cusum, fp_pht, fp_adwin, al_cusum, al_pht, al_adwin

def run_experiment_d(n_seeds, lambda_ph_iid, alpha=0.08, n_jobs=-1):
    print(f"\n=== [X] EXPERIMENT D: DATA PIPELINE TAX (n_seeds={n_seeds}) ===")
    grid_d = [1.17, 6.44, 11.89, 17.33, 22.78, 28.22, 33.67, 39.11, 44.56, 50.0,
              60.0, 75.56, 91.11, 106.67, 122.22, 137.78, 153.33, 168.89, 184.44, 200.0]
    lambda_cusum_iid = 65.0
    
    tasks = []
    for gamma in grid_d:
        beta = solve_beta_for_gamma(alpha, gamma)
        omega = 0.04 * (1 - alpha - beta)
        for s in range(n_seeds):
            tasks.append((gamma, s, omega, alpha, beta, lambda_cusum_iid, lambda_ph_iid))
            
    res = Parallel(n_jobs=n_jobs)(delayed(worker_exp_d)(t) for t in tqdm(tasks))
    df_raw = pd.DataFrame(res, columns=["Gamma", "FP_CUSUM", "FP_PHT", "FP_ADWIN", "AL_CUSUM", "AL_PHT", "AL_ADWIN"])
    
    agg = []
    for gamma in grid_d:
        sub = df_raw[df_raw["Gamma"] == gamma]
        row = {"Gamma": gamma}
        for det in ["CUSUM", "PHT", "ADWIN"]:
            fpr = sub[f"FP_{det}"].mean()
            row[f"FPR_{det}"] = fpr
            
            als = sub[f"AL_{det}"].values
            detected = als[als != -1]
            det_rate = len(detected) / len(als)
            row[f"DetRate_{det}"] = det_rate
            row[f"ADD_{det}"] = np.mean(detected) if det_rate >= 0.5 else np.nan
            row[f"SEM_{det}"] = np.std(detected)/np.sqrt(len(detected)) if det_rate >= 0.5 else np.nan
        agg.append(row)
        
    df = pd.DataFrame(agg)
    df.to_csv(FIGURES_DIR / "protocol_4e_data_add_vs_gamma.csv", index=False)
    return df

def plot_figure_20(df_data, df_concept):
    print("\n=== PLOTTING FIGURE 20 ===")
    fig, (ax1, ax2) = plt.subplots(1, 2)
    
    # Panel A: Data Pipeline
    print("Data ADD ~ Gamma slopes (OLS):")
    for det in ["CUSUM", "PHT", "ADWIN"]:
        if f"ADD_{det}" in df_data.columns:
            valid = df_data.dropna(subset=[f"ADD_{det}"])
            if len(valid) > 1:
                slope, intercept, _, _, _ = stats.linregress(valid["Gamma"], valid[f"ADD_{det}"])
                print(f"  {det}: {slope:.3f}")
            ax1.errorbar(valid["Gamma"], valid[f"ADD_{det}"], yerr=valid[f"SEM_{det}"], 
                         fmt='o-', color=COLORS.get(det, "black"), label=det, capsize=3)
            
            censored = df_data[df_data[f"DetRate_{det}"] < 0.5]
            if not censored.empty:
                ax1.scatter(censored["Gamma"], [ax1.get_ylim()[1]]*len(censored), marker='x', color=COLORS.get(det, "black"), label=f"{det} (Censored)")

    ax1.set_xlabel(r"GARCH Penalty Factor $\Gamma$")
    ax1.set_ylabel("Average Detection Delay (ADD)")
    ax1.set_title("Data Pipeline (c=2.0) - Re-calibrated Thresholds")
    ax1.grid(alpha=0.3)
    ax1.legend()
    
    # Panel B: Concept Pipeline (loaded from protocol_4c, c=1.5)
    for det in ["CUSUM", "PHT", "ADWIN", "DDM", "EDDM"]:
        if f"ADD_{det}" in df_concept.columns:
            valid = df_concept.dropna(subset=[f"ADD_{det}"])
            ax2.errorbar(valid["Gamma"], valid[f"ADD_{det}"], yerr=valid[f"SEM_{det}"], 
                         fmt='o-', color=COLORS.get(det, "black"), label=det, capsize=3)
                         
    ax2.set_xlabel(r"GARCH Penalty Factor $\Gamma$")
    ax2.set_ylabel("Average Detection Delay (ADD)")
    ax2.set_title("Concept Pipeline (c=1.5) - Immunity")
    ax2.grid(alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "Fig20_Data_vs_Concept_ADD.png")
    print(f"Figure saved to {FIGURES_DIR / 'Fig20_Data_vs_Concept_ADD.png'}")

# --- PLOTTING ---
def plot_figure_18(df_a, df_b):
    print("\n=== [4] PLOTTING FIGURE 18 ===")
    fig, (ax1, ax2) = plt.subplots(1, 2)
    
    # Panel A: PHT FPR
    ax1.plot(df_a["Gamma"], df_a["FPR_raw"], 'o-', color="#d62728", label=r"Raw $\lambda_{PH}^{iid}$")
    ax1.plot(df_a["Gamma"], df_a["FPR_sqrt"], 's-', color="#ff7f0e", label=r"Scaled $\lambda_{PH} \times \sqrt{\Gamma}$")
    ax1.plot(df_a["Gamma"], df_a["FPR_gamma"], 'D-', color="#1f77b4", label=r"Scaled $\lambda_{PH} \times \Gamma$")
    ax1.axhline(0.05, ls="--", color="black", lw=2, label="Nominal 5%")
    ax1.set_xlabel(r"GARCH Penalty Factor $\Gamma$")
    ax1.set_ylabel("False Positive Rate (H0)")
    ax1.set_title("Page-Hinkley FPR Explosion (Data Pipeline)")
    ax1.grid(alpha=0.3)
    ax1.legend(loc="center right", bbox_to_anchor=(0.95, 0.66))
    
    # Panel B: Universality ADD
    for det in ["CUSUM", "PHT", "ADWIN", "DDM", "EDDM"]:
        if f"ADD_{det}" in df_b.columns:
            valid = df_b.dropna(subset=[f"ADD_{det}"])
            ax2.errorbar(valid["Gamma"], valid[f"ADD_{det}"], yerr=valid[f"SEM_{det}"], 
                         fmt='o-', color=COLORS[det], label=det, capsize=3)
    ax2.set_xlabel(r"GARCH Penalty Factor $\Gamma$")
    ax2.set_ylabel("Average Detection Delay (ADD)")
    ax2.set_title("Universality of the Whitening Filter ($c=1.5$)")
    ax2.grid(alpha=0.3)
    ax2.legend(loc="center right", bbox_to_anchor=(0.95, 0.66))
    
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "Fig18_Multi_Detector.png")
    print(f"Figure saved to {FIGURES_DIR / 'Fig18_Multi_Detector.png'}")

# --- MAIN ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Detector GARCH Concept Drift Evaluation")
    parser.add_argument("--n_seeds_a", type=int, default=5000, help="Number of Monte-Carlo seeds for Exp A")
    parser.add_argument("--n_seeds_b", type=int, default=5000, help="Number of Monte-Carlo seeds for Exp B")
    parser.add_argument("--n_seeds_c", type=int, default=5000, help="Number of Monte-Carlo seeds for Exp C")
    parser.add_argument("--jobs", type=int, default=-1, help="Number of parallel jobs (-1 for all cores)")
    args = parser.parse_args()
    
    t0 = time.time()
    
    lambda_ph_iid_data = calibrate_pht_iid(target_fpr=0.05, delta=0.5, stream_type='continuous', seed=42)
    lambda_ph_iid_concept = calibrate_pht_iid(target_fpr=0.05, delta=0.1, stream_type='binary', seed=43)
    
    test_adwin_equivalence()

    df_a = run_experiment_a(n_seeds=args.n_seeds_a, lambda_ph_iid=lambda_ph_iid_data, n_jobs=args.jobs)
    df_b = run_experiment_b(n_seeds=args.n_seeds_b, lambda_ph_iid_concept=lambda_ph_iid_concept, n_jobs=args.jobs)
    df_c = run_experiment_c(n_seeds=args.n_seeds_c, n_jobs=args.jobs)
    
    # Execution of Experiment D is fixed to N=1000 per explicit constraint
    df_d = run_experiment_d(n_seeds=1000, lambda_ph_iid=lambda_ph_iid_data, n_jobs=args.jobs)
    
    # Direct memory transfer guarantees bit-level accuracy (avoids CSV float truncation)
    plot_figure_18(df_a, df_b)
    plot_figure_20(df_d, df_b)
    
    print(f"\nExecution completed in {time.time()-t0:.1f}s.")