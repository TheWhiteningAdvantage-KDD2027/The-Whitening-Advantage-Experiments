#!/usr/bin/env python3
"""
==========================================================================
R03 -- FALSE POSITIVE RATE EXPLOSION WITHOUT RECALIBRATION (FIGURE 3)
==========================================================================
Quantifies the cost of ignoring the heteroscedastic penalty Gamma inflicted
on any drift monitor calibrated under an i.i.d. assumption when it is run on
stationary GARCH(1,1) streams under H_0.

The remedy is detector-specific. False alarms of a CUSUM under H_0 obey a
Siegmund-type bound exp(-2 delta_P lambda / sigma_LR^2) with long-run variance
sigma_LR^2 = Gamma, so the threshold must absorb the full inflation,
lambda x Gamma. The cut statistic of ADWIN is a difference of window means, a
quantity on the scale of a standard deviation, so the correct correction is
epsilon_cut x sqrt(Gamma).

Notations:
- Gamma        : GARCH penalty factor, inflation of the variance of the partial
                 sums of the monitored stream; closed form in (alpha, beta).
- lambda_iid   : CUSUM threshold calibrated under an i.i.d. assumption, 65.0.
- delta_P      : reference drift of the CUSUM recursion, 0.5.
- FPR_raw      : false alarm rate of the i.i.d.-calibrated detector, uncorrected.
- FPR_sqrt     : same, threshold multiplied by sqrt(Gamma).
- FPR_gamma    : same, threshold multiplied by Gamma (Siegmund limit).
- FPR_recalib  : ADWIN rate obtained by the correction epsilon_cut x sqrt(Gamma).
- epsilon_cut  : ADWIN cut threshold on the difference between sub-window means.
- sigma_LR^2   : long-run variance of the monitored stream, equal to Gamma under H_0.

References:
- Page, E. S. (1954). Continuous inspection schemes. Biometrika, 41(1/2), 100-115.
- Bifet, A. & Gavalda, R. (2007). Learning from time-changing data with adaptive
  windowing. SIAM International Conference on Data Mining.
==========================================================================
"""

import sys
from pathlib import Path

# Determinism bootstrap. The repository root must be on sys.path before
# experiments.common is importable: the interpreter puts the *script* directory
# in sys.path[0] and never adds the working directory. Only sys and pathlib are
# loaded at this point, neither of which pulls in numpy, so the environment
# block below is still posted before any BLAS thread limit is read.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from experiments.common.fair_env import enforce_strict_determinism, verify_hash_seed, log_environment

enforce_strict_determinism()

import numpy as np
import pandas as pd
from experiments.common.fair_harness import setup_logging, disable_pandas_multithreading, compute_sha256, save_fair_csv, log_artifact_manifest

disable_pandas_multithreading()

import os
import time
import argparse
import hashlib
from concurrent.futures import ProcessPoolExecutor
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy.stats as stats

# --- PROTOCOL SPECIFICATION (v87, sec:fpr_explosion) ---
# Binding specification. If the script diverges from these values, the script is wrong.
N_STREAMS_SPEC = 300
STREAM_LENGTH = 5000
LAMBDA_IID = 65.0
DELTA_P = 0.5
ALPHA_GARCH = 0.08
NOMINAL_LEVEL = 0.05
BURN_IN = 1000
DELTA_MU = 2.0
GRADUAL_WIDTH = 1000

# --- CERTIFICATION THRESHOLDS AND WHERE THEY COME FROM ---
# Fixed here, before any regenerated value is read. v87 writes, in sec:fpr_explosion:
#   "fires at close to 80% or above once Gamma > 20"
#   "leaves a residual plateau near 30%"
#   "containing the FPR below 13%"
# Only the third is a literal numeral. The first two are operationalised by a rule
# stated in advance and echoed verbatim into the log:
#   "close to 80%" -> within 5% in relative terms of 0.80, hence >= 0.76
#   "near 30%"     -> within 5 percentage points of 0.30, hence [0.25, 0.35]
# The witness value 0.760000 coincides with the first floor. That is a coincidence,
# not a derivation: the floor follows from the relative rule applied to 0.80.
CUSUM_RAW_FLOOR = 0.76
CUSUM_SQRT_BAND_LOW = 0.25
CUSUM_SQRT_BAND_HIGH = 0.35
ADWIN_RECALIB_CEILING = 0.13
GAMMA_CERTIFICATION_CUT = 20.0
GAMMA_MONOTONE_CUT = 6.0
FAMILYWISE_ALPHA = 0.01

OPERATIONALISATION_RULES = (
    'v87 "close to 80% or above once Gamma > 20" -> mean FPR_raw over Gamma > 20 '
    f'>= {CUSUM_RAW_FLOOR} (0.80 less 5% in relative terms)',
    'v87 "residual plateau near 30%" -> mean FPR_sqrt over Gamma > 20 in '
    f'[{CUSUM_SQRT_BAND_LOW}, {CUSUM_SQRT_BAND_HIGH}] (0.30 plus or minus 5 percentage points)',
    'v87 "containing the FPR below 13%" -> mean FPR_recalib over the whole grid '
    f'<= {ADWIN_RECALIB_CEILING} (literal numeral, no operationalisation)',
)


def get_deterministic_seed(*args) -> tuple:
    """
    Generates a 128-bit collision-free seed tuple for np.random.default_rng.
    Enforces hex representation for floats to prevent cross-platform stringification drift.
    """
    def format_arg(arg):
        if isinstance(arg, (float, np.floating)):
            return float(arg).hex()
        return str(arg)

    s = "_".join(map(format_arg, args))
    h = hashlib.md5(s.encode('utf-8')).hexdigest()
    return tuple(int(h[i:i+8], 16) for i in range(0, 32, 8))


def simulate_garch11(n, omega, alpha, beta, nu=7.0, seed_tuple=None):
    rng = np.random.default_rng(seed_tuple)
    sigma2_unc = omega / (1.0 - alpha - beta)
    eps = np.zeros(n)
    sigma2 = np.zeros(n)
    sigma2[0] = sigma2_unc
    scale = np.sqrt((nu - 2.0) / nu)
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
    denom = 1.0 - 2.0 * alpha * beta - beta**2
    if denom <= 0: return (1.0 + phi) / (1.0 - phi)
    rho1 = alpha * (1.0 - beta * phi) / denom
    return max(1.0, 1.0 + 2.0 * rho1 / (1.0 - phi))


def solve_beta_for_gamma(alpha, target_gamma):
    if target_gamma <= 1.0: return 0.0
    lo, hi = 0.0, 1.0 - alpha - 1e-6
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if compute_gamma_exact(alpha, mid) < target_gamma: lo = mid
        else: hi = mid
    return mid


def strict_cusum(stream, delta_P, threshold):
    S = 0.0
    for t in range(len(stream)):
        S = max(0.0, S + float(stream[t]) - delta_P)
        if S > threshold: return t
    return -1


def adwin_like_detector(stream, delta=5e-4, gamma=1.0, min_window=30):
    cumsums = np.cumsum(stream)
    for n in range(2 * min_window, len(stream) + 1):
        split = n // 2
        sum_w0 = cumsums[split - 1]
        mean_w0 = sum_w0 / split

        len_w1 = n - split
        sum_w1 = cumsums[n - 1] - sum_w0
        mean_w1 = sum_w1 / len_w1

        m_harm = 1.0 / (1.0 / split + 1.0 / len_w1)
        eps_cut = np.sqrt(2.0 * gamma * np.log(2.0 / delta) / m_harm)
        if abs(mean_w0 - mean_w1) > eps_cut: return n - 1
    return -1


def standardised_squared_stream(eps, burn_in):
    """
    Builds the monitored stream: squared innovations, centred and scaled by the
    moments of the burn-in segment. Single point of construction, shared by the
    grid arms and by the i.i.d. calibration arm, so that the rates they produce
    are comparable.
    """
    x = eps**2
    mu_x, sig_x = np.mean(x[:burn_in]), np.std(x[:burn_in])
    return (x[burn_in:] - mu_x) / max(sig_x, 1e-8)


def wilson_interval(k, n, confidence=0.95):
    """Wilson score interval, clamped to the unit interval before persistence."""
    z = stats.norm.ppf(0.5 + confidence / 2.0)
    p_hat = k / n
    den = 1.0 + z * z / n
    centre = (p_hat + z * z / (2.0 * n)) / den
    half = z * np.sqrt(p_hat * (1.0 - p_hat) / n + z * z / (4.0 * n * n)) / den
    return max(0.0, min(1.0, centre - half)), max(0.0, min(1.0, centre + half))


# --- WORKERS ---

def _worker_1a(args):
    """
    One realisation evaluated at three thresholds. The three indicators returned
    share a single stream by construction, which is what makes the ordering
    FPR_gamma <= FPR_sqrt <= FPR_raw a deterministic identity rather than a
    hypothesis test. `nested` reports that property per stream so the premise is
    verified at run time instead of assumed.
    """
    s, stream_length, omega, alpha, beta, gamma_actual, lambda_iid, delta_P = args
    child_seed = get_deterministic_seed("1a", s)
    eps = simulate_garch11(stream_length + BURN_IN, omega, alpha, beta, seed_tuple=child_seed)
    z = standardised_squared_stream(eps, BURN_IN)

    raw = 1 if strict_cusum(z, delta_P, lambda_iid) >= 0 else 0
    sqrt = 1 if strict_cusum(z, delta_P, lambda_iid * np.sqrt(gamma_actual)) >= 0 else 0
    gamm = 1 if strict_cusum(z, delta_P, lambda_iid * gamma_actual) >= 0 else 0
    return {"r": raw, "sq": sqrt, "gm": gamm, "nested": int(gamm <= sqrt <= raw)}


def _worker_1b(args):
    """One realisation evaluated by ADWIN at gamma = 1 and at gamma = Gamma."""
    s, stream_length, omega, alpha, beta, gamma_actual = args
    child_seed = get_deterministic_seed("1b", s)
    eps = simulate_garch11(stream_length + BURN_IN, omega, alpha, beta, seed_tuple=child_seed)
    z = standardised_squared_stream(eps, BURN_IN)

    raw_hit = 1 if adwin_like_detector(z, delta=5e-4, gamma=1.0) >= 0 else 0
    recalib_hit = 1 if adwin_like_detector(z, delta=5e-4, gamma=gamma_actual) >= 0 else 0
    return {"r": raw_hit, "rec": recalib_hit, "nested": int(recalib_hit <= raw_hit)}


def _worker_iid_calibration(args):
    """
    Calibration arm at Gamma = 1 exactly (alpha = beta = 0). Same innovations,
    same standardisation chain and same detectors as the grid; only alpha and beta
    change. Both detectors read the same realisation, which pairs the two rates
    without altering either marginal.
    """
    s, stream_length, omega, lambda_iid, delta_P = args
    child_seed = get_deterministic_seed("iid_calib", s)
    eps = simulate_garch11(stream_length + BURN_IN, omega, 0.0, 0.0, seed_tuple=child_seed)
    z = standardised_squared_stream(eps, BURN_IN)

    cusum_hit = 1 if strict_cusum(z, delta_P, lambda_iid) >= 0 else 0
    adwin_hit = 1 if adwin_like_detector(z, delta=5e-4, gamma=1.0) >= 0 else 0
    return {"cusum": cusum_hit, "adwin": adwin_hit}


def _worker_2a(args):
    s, omega, alpha, beta, gamma_actual, lambda_iid, delta_P, delta_mu = args
    child_seed = get_deterministic_seed("2a", s)
    eps = simulate_garch11(10000, omega, alpha, beta, seed_tuple=child_seed)
    f = eps**2
    mu_f, sig_f = np.mean(f[:2000]), np.std(f[:2000])
    z = (f[2000:] - mu_f) / max(sig_f, 1e-8)
    z += delta_P + delta_mu

    al_data = strict_cusum(z, delta_P, lambda_iid * gamma_actual)
    X_concept = eps[2000:] + delta_mu
    z_e = (X_concept > 0).astype(float) - 0.5
    al_concept = strict_cusum(z_e, 0.1, 10.0)
    return {"ad_data": al_data, "ad_conc": al_concept}


def _worker_2b(args):
    w, s, n_total, omega, alpha, beta, gamma_actual, lambda_iid, delta_P, delta_mu = args
    child_seed = get_deterministic_seed("2b", s, w)
    eps = simulate_garch11(n_total, omega, alpha, beta, seed_tuple=child_seed)
    f = eps**2
    mu_f, sig_f = np.mean(f[:1500]), np.std(f[:1500])
    z = (f[2000:] - mu_f) / max(sig_f, 1e-8)
    ramp = np.array([delta_P + delta_mu * (t/w) if t <= w else delta_P + delta_mu for t in range(len(z))])
    z += ramp

    al_data = strict_cusum(z, delta_P, lambda_iid * gamma_actual)
    mu_t_concept = np.array([delta_mu * (t/w) if t <= w else delta_mu for t in range(len(z))])
    X_concept = eps[2000:] + mu_t_concept
    z_e = (X_concept > 0).astype(float) - 0.5
    al_concept = strict_cusum(z_e, 0.1, 10.0)
    return {"ad_data": al_data, "ad_conc": al_concept}


def _worker_2c(args):
    lc, dc, s, w, n_total, omega, alpha, beta, delta_mu = args
    child_seed = get_deterministic_seed("2c_add", s, w)
    eps = simulate_garch11(n_total, omega, alpha, beta, seed_tuple=child_seed)
    len_z = n_total - 2000
    mu_t_concept = np.array([delta_mu * (t/w) if t <= w else delta_mu for t in range(len_z)])
    X_concept = eps[2000:] + mu_t_concept
    z_e = (X_concept > 0).astype(float) - 0.5
    al_concept = strict_cusum(z_e, dc, lc)
    return {"ad_conc": al_concept}


def _worker_2c_fpr(args):
    lc, dc, s, len_fpr, omega, alpha, beta = args
    child_seed = get_deterministic_seed("2c_fpr", s, lc, dc)
    eps = simulate_garch11(len_fpr + 1500, omega, alpha, beta, seed_tuple=child_seed)
    X_concept = eps[1500:]
    z_e = (X_concept > 0).astype(float) - 0.5
    raw = 1 if strict_cusum(z_e, dc, lc) >= 0 else 0
    return {"r": raw}


def _worker_2c_ref_fpr(args):
    s, len_fpr, omega, alpha, beta, lambda_iid, gamma_actual, delta_P = args
    child_seed = get_deterministic_seed("2c_ref_fpr", s)
    eps = simulate_garch11(len_fpr + 1500, omega, alpha, beta, seed_tuple=child_seed)
    f = eps**2
    mu_f, sig_f = np.mean(f[:1500]), np.std(f[:1500])
    z = (f[1500:] - mu_f) / max(sig_f, 1e-8)
    raw = 1 if strict_cusum(z, delta_P, lambda_iid * gamma_actual) >= 0 else 0
    return {"r": raw}


def _worker_2c_ref_add(args):
    s, w, n_total, omega, alpha, beta, lambda_iid, gamma_actual, delta_P, delta_mu = args
    child_seed = get_deterministic_seed("2c_ref_add", s, w)
    eps = simulate_garch11(n_total, omega, alpha, beta, seed_tuple=child_seed)
    f = eps**2
    mu_f, sig_f = np.mean(f[:1500]), np.std(f[:1500])
    z = (f[2000:] - mu_f) / max(sig_f, 1e-8)
    len_z = n_total - 2000
    ramp = np.array([delta_P + delta_mu * (t/w) if t <= w else delta_P + delta_mu for t in range(len_z)])
    z += ramp
    al_data = strict_cusum(z, delta_P, lambda_iid * gamma_actual)
    return {"ad_data": al_data}


# --- PROTOCOLS ---

def protocol_1a(n_streams, stream_length, alpha, lambda_iid, delta_P, executor, logger):
    logger.info("Protocol 1A: StrictCUSUM false alarm rate under H_0.")
    gamma_targets = np.concatenate([np.linspace(1.0, 50.0, 10), np.linspace(60.0, 200.0, 10)])
    results = []
    nesting_violations = 0

    for gamma in gamma_targets:
        beta = solve_beta_for_gamma(alpha, gamma)
        gamma_actual = compute_gamma_exact(alpha, beta)
        omega = 0.01 * (1.0 - alpha - beta)
        args_list = [(s, stream_length, omega, alpha, beta, gamma_actual, lambda_iid, delta_P) for s in range(n_streams)]
        f_raw, f_sqrt, f_gamma = 0, 0, 0
        for res in executor.map(_worker_1a, args_list, chunksize=10):
            f_raw += res['r']
            f_sqrt += res['sq']
            f_gamma += res['gm']
            nesting_violations += (1 - res['nested'])
        results.append({
            "Gamma": gamma_actual,
            "FPR_raw": f_raw / n_streams,
            "FPR_sqrt": f_sqrt / n_streams,
            "FPR_gamma": f_gamma / n_streams
        })
    return pd.DataFrame(results), nesting_violations


def protocol_1b(n_streams, stream_length, alpha, executor, logger):
    logger.info("Protocol 1B: ADWIN-like false alarm rate under H_0.")
    gamma_targets = np.concatenate([np.linspace(1.0, 50.0, 10), np.linspace(60.0, 200.0, 10)])
    results = []
    nesting_violations = 0

    for gamma in gamma_targets:
        beta = solve_beta_for_gamma(alpha, gamma)
        gamma_actual = compute_gamma_exact(alpha, beta)
        omega = 0.01 * (1.0 - alpha - beta)
        args_list = [(s, stream_length, omega, alpha, beta, gamma_actual) for s in range(n_streams)]
        f_raw, f_rec = 0, 0
        for res in executor.map(_worker_1b, args_list, chunksize=10):
            f_raw += res['r']
            f_rec += res['rec']
            nesting_violations += (1 - res['nested'])
        results.append({
            "Gamma": gamma_actual,
            "FPR_raw": f_raw / n_streams,
            "FPR_recalib": f_rec / n_streams
        })
    return pd.DataFrame(results), nesting_violations


def protocol_iid_calibration(n_streams, stream_length, lambda_iid, delta_P, executor, logger):
    """
    Measures the i.i.d. level of both detectors at Gamma = 1 exactly. The lowest
    grid point of protocols 1A and 1B sits at Gamma = 1.174, not at 1, so it cannot
    serve as a measurement of the i.i.d. level. This arm is the only output of the
    repository able to say whether the phrase "calibrated to a 5% nominal level"
    holds for either detector.
    """
    gamma_iid = compute_gamma_exact(0.0, 0.0)
    logger.info(f"i.i.d. calibration arm: compute_gamma_exact(0, 0) = {gamma_iid!r}")
    if gamma_iid != 1.0:
        logger.error(
            f"Closed-form penalty at alpha = beta = 0 is {gamma_iid!r}, expected exactly 1.0. "
            "Squared innovations are i.i.d. in that configuration, so their long-run variance "
            "equals their variance. A departure invalidates the whole grid, not this arm alone.")
        sys.exit(1)

    omega = 0.01 * (1.0 - 0.0 - 0.0)
    args_list = [(s, stream_length, omega, lambda_iid, delta_P) for s in range(n_streams)]
    k_cusum, k_adwin = 0, 0
    for res in executor.map(_worker_iid_calibration, args_list, chunksize=10):
        k_cusum += res['cusum']
        k_adwin += res['adwin']

    rows = []
    for name, k in (("StrictCUSUM", k_cusum), ("ADWIN", k_adwin)):
        low, high = wilson_interval(k, n_streams)
        rows.append({
            "detector": name,
            "Gamma": gamma_iid,
            "n_streams": n_streams,
            "alarms": k,
            "FPR": max(0.0, min(1.0, k / n_streams)),
            "wilson_low": low,
            "wilson_high": high,
            "contains_nominal": bool(low <= NOMINAL_LEVEL <= high)
        })
    return pd.DataFrame(rows)


def protocol_2a(n_seeds, alpha, lambda_iid, delta_P, delta_mu, executor, logger):
    logger.info("Protocol 2A: detection delay against Gamma (retained, not cited in v87).")
    gamma_targets = np.linspace(1.0, 200.0, 20)
    results = []

    for gamma in gamma_targets:
        beta = solve_beta_for_gamma(alpha, gamma)
        gamma_actual = compute_gamma_exact(alpha, beta)
        omega = 0.01 * (1.0 - alpha - beta)
        args_list = [(s, omega, alpha, beta, gamma_actual, lambda_iid, delta_P, delta_mu) for s in range(n_seeds)]
        adds_data, adds_concept = [], []
        for res in executor.map(_worker_2a, args_list, chunksize=10):
            if res['ad_data'] >= 0: adds_data.append(res['ad_data'])
            if res['ad_conc'] >= 0: adds_concept.append(res['ad_conc'])

        results.append({
            "Gamma": gamma_actual,
            "ADD_Data": np.mean(adds_data) if adds_data else np.nan,
            "SEM_Data": np.std(adds_data) / np.sqrt(len(adds_data)) if adds_data else np.nan,
            "ADD_Concept": np.mean(adds_concept) if adds_concept else np.nan,
            "SEM_Concept": np.std(adds_concept) / np.sqrt(len(adds_concept)) if adds_concept else np.nan
        })
    return pd.DataFrame(results)


def protocol_2b(n_seeds, alpha, lambda_iid, delta_P, delta_mu, executor, logger):
    logger.info("Protocol 2B: detection delay against drift width (retained, not cited in v87).")
    gamma_target = 11.58
    beta = solve_beta_for_gamma(alpha, gamma_target)
    gamma_actual = compute_gamma_exact(alpha, beta)
    omega = 0.01 * (1.0 - alpha - beta)
    w_values = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]
    results = []

    for w in w_values:
        n_total = 2000 + w + 5000
        args_list = [(w, s, n_total, omega, alpha, beta, gamma_actual, lambda_iid, delta_P, delta_mu) for s in range(n_seeds)]
        adds_data, adds_concept = [], []
        for res in executor.map(_worker_2b, args_list, chunksize=10):
            if res['ad_data'] >= 0: adds_data.append(res['ad_data'])
            if res['ad_conc'] >= 0: adds_concept.append(res['ad_conc'])

        results.append({
            "w": w,
            "ADD_Data": np.mean(adds_data) if adds_data else np.nan,
            "SEM_Data": np.std(adds_data) / np.sqrt(len(adds_data)) if adds_data else np.nan,
            "ADD_Concept": np.mean(adds_concept) if adds_concept else np.nan,
            "SEM_Concept": np.std(adds_concept) / np.sqrt(len(adds_concept)) if adds_concept else np.nan
        })
    return pd.DataFrame(results)


def protocol_2c(n_seeds, alpha, lambda_iid, delta_P, delta_mu, w, executor, logger):
    logger.info("Protocol 2C: speedup sensitivity (retained, not cited in v87).")
    gamma_target = 11.58
    beta = solve_beta_for_gamma(alpha, gamma_target)
    gamma_actual = compute_gamma_exact(alpha, beta)
    omega = 0.01 * (1.0 - alpha - beta)
    n_fpr, len_fpr = (20, 5000) if n_seeds <= 10 else (1000, 5000)
    n_total = 2000 + w + 5000

    args_ref_fpr = [(s, len_fpr, omega, alpha, beta, lambda_iid, gamma_actual, delta_P) for s in range(n_fpr)]
    args_ref_add = [(s, w, n_total, omega, alpha, beta, lambda_iid, gamma_actual, delta_P, delta_mu) for s in range(n_seeds)]

    fpr_data_count = sum(res['r'] for res in executor.map(_worker_2c_ref_fpr, args_ref_fpr, chunksize=10))
    adds_data = [res['ad_data'] for res in executor.map(_worker_2c_ref_add, args_ref_add, chunksize=10) if res['ad_data'] >= 0]
    add_data_mean = np.mean(adds_data) if adds_data else np.nan
    logger.info(f"Protocol 2C reference arm: FPR_data = {fpr_data_count / n_fpr:.4f}, ADD_data = {add_data_mean:.2f}")

    lambda_c_grid = [2.0, 5.0, 10.0, 20.0, 40.0]
    delta_c_grid = [0.02, 0.05, 0.1]
    results = []

    for dc in delta_c_grid:
        for lc in lambda_c_grid:
            args_fpr = [(lc, dc, s, len_fpr, omega, alpha, beta) for s in range(n_fpr)]
            fpr_c_count = sum(res['r'] for res in executor.map(_worker_2c_fpr, args_fpr, chunksize=10))
            fpr_c = fpr_c_count / n_fpr

            args_add = [(lc, dc, s, w, n_total, omega, alpha, beta, delta_mu) for s in range(n_seeds)]
            adds_c = [res['ad_conc'] for res in executor.map(_worker_2c, args_add, chunksize=10) if res['ad_conc'] >= 0]
            add_c_mean = np.mean(adds_c) if adds_c else np.nan
            sem_c = np.std(adds_c) / np.sqrt(len(adds_c)) if adds_c else np.nan

            speedup = add_data_mean / add_c_mean if add_c_mean else np.nan
            results.append({
                "lambda_c": lc, "delta_c": dc, "FPR_concept": fpr_c,
                "ADD_concept": add_c_mean, "SEM_concept": sem_c,
                "speedup": speedup, "is_ref": (lc == 10.0 and dc == 0.1)
            })
    return pd.DataFrame(results)


# --- PLOTTING ---

def plot_fig03(df_cusum, df_adwin, stream_length, figures_dir, suffix):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 6.5))
    lowest_gamma = df_cusum["Gamma"].iloc[0]

    for ax, df in ((ax1, df_cusum), (ax2, df_adwin)):
        ax.axhline(y=df["FPR_raw"].iloc[0], color="#D4A017", linestyle='--', linewidth=2,
                   label=f"Measured FPR at lowest grid point ($\\Gamma$ = {lowest_gamma:.2f}): {df['FPR_raw'].iloc[0]:.3f}")
        ax.axhline(y=NOMINAL_LEVEL, color="#6E6E6E", linestyle=':', linewidth=2,
                   label=f"Nominal level declared in v87 ({NOMINAL_LEVEL:.0%})")

    ax1.plot(df_cusum["Gamma"], df_cusum["FPR_raw"], 'o-', color="#C45C5C", linewidth=2, label="Uncalibrated StrictCUSUM")
    ax1.plot(df_cusum["Gamma"], df_cusum["FPR_sqrt"], 'D-', color="#7B68AE", linewidth=2, label=r"Recalibrated $\lambda \times \sqrt{\Gamma}$")
    ax1.plot(df_cusum["Gamma"], df_cusum["FPR_gamma"], 's-', color="#2A6A7C", linewidth=2, label=r"Recalibrated $\lambda \times \Gamma$ (Siegmund limit)")
    ax1.set_title(f"(A) False Positive Rate (FPR) Explosion without Recalibration\nData Drift Pipeline (StrictCUSUM on standardized squared residuals), N={stream_length} steps", fontweight="bold", loc="left")
    ax1.set_xlabel(r"GARCH Penalty Factor $\Gamma$")
    ax1.set_ylabel("False Positive Rate (FPR) under $H_0$")
    ax1.legend(loc='center right', bbox_to_anchor=(1.0, 0.66))
    ax1.grid(alpha=0.3)

    ax2.plot(df_adwin["Gamma"], df_adwin["FPR_raw"], 'o-', color="#C45C5C", linewidth=2, label="Uncalibrated ADWIN")
    ax2.plot(df_adwin["Gamma"], df_adwin["FPR_recalib"], 's-', color="#2A6A7C", linewidth=2, label=r"Recalibrated ADWIN ($\epsilon_{\mathrm{cut}} \times \sqrt{\Gamma}$)")
    ax2.set_title(f"(B) ADWIN False Positive Rate (FPR) Explosion under GARCH\nData Drift Pipeline (NO CLASSIFIER - Applied to standardized squared residuals), N={stream_length} steps", fontweight="bold", loc="left")
    ax2.set_xlabel(r"GARCH Penalty Factor $\Gamma$")
    ax2.set_ylabel("False Positive Rate (FPR) under $H_0$")
    ax2.legend(loc='center right', bbox_to_anchor=(1.0, 0.5))
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    fig.savefig(figures_dir / f"fig03_fpr_explosion{suffix}.png", dpi=200)
    plt.close()


# --- CERTIFICATION ---

def log_aggregate_gate(logger, label, k, n, n_points, n_streams, low=None, high=None):
    """
    Evaluates one aggregate certification gate and logs the two standard errors that
    bracket its fragility. The pooled error treats the n streams as independent; the
    common-random-number error treats the n_points grid estimates as perfectly
    correlated, which they nearly are, since the seed of protocol 1A does not depend
    on Gamma and the base innovations are therefore shared across grid points. The
    truth lies between the two, and the conservative figure is the second.
    """
    p = k / n
    se_pooled = np.sqrt(p * (1.0 - p) / n)
    se_crn = np.sqrt(p * (1.0 - p) / n_streams)
    ok = True
    margins = []
    if low is not None:
        ok = ok and (p >= low)
        margins.append(f"({p - low:+.6f} above {low}, {(p - low) / se_pooled:+.1f} pooled SE, {(p - low) / se_crn:+.1f} CRN SE)")
    if high is not None:
        ok = ok and (p <= high)
        margins.append(f"({high - p:+.6f} below {high}, {(high - p) / se_pooled:+.1f} pooled SE, {(high - p) / se_crn:+.1f} CRN SE)")
    logger.info(
        f"Aggregate gate [{label}]: {p:.6f} over n = {n} ({n_points} grid points x {n_streams} streams); "
        f"SE_pooled = {se_pooled:.5f}, SE_crn = {se_crn:.5f}; " + " ".join(margins) +
        f"; verdict = {'PASS' if ok else 'FAIL'}")
    return ok, p, se_pooled, se_crn


def log_extremal_warning(logger, label, value, gamma_cell, breached, n_points, n_streams, threshold, p_bar, direction):
    """
    Non-blocking companion to an aggregate gate. Reports the literal extremal
    criterion of the original prompt together with the probability that it fires
    under H_0 with a true rate equal to the observed aggregate, computed for
    independent grid points. Common random numbers make the grid points positively
    correlated, so that probability is an upper bound.
    """
    k_threshold = threshold * n_streams
    if direction == "below":
        p_single = stats.binom.cdf(np.ceil(k_threshold) - 1, n_streams, p_bar)
    else:
        p_single = stats.binom.sf(np.floor(k_threshold), n_streams, p_bar)
    p_family = 1.0 - (1.0 - p_single) ** n_points
    message = (
        f"Extremal criterion [{label}]: observed {value:.6f} at Gamma = {gamma_cell:.4f} against "
        f"threshold {threshold}; probability of firing under H_0 at the observed aggregate rate "
        f"{p_bar:.6f} is {p_family:.3f} for {n_points} independent grid points (upper bound under CRN)")
    if breached:
        logger.warning(message + " -- BREACHED, non-blocking")
    else:
        logger.info(message + " -- not breached")
    return p_family


def classify_deviation(published, regenerated, decimals=1):
    """
    Classifies one regenerated value against its witness at the printing precision of
    the manuscript, which prints these quantities as percentages with one decimal.
    D3 is never returned here: falsification of a qualitative claim is decided by the
    blocking gates, not by a rounding comparison.
    """
    if published == regenerated:
        return "D0"
    if round(published * 100.0, decimals) == round(regenerated * 100.0, decimals):
        return "D1"
    return "D2"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true",
                        help="Degraded smoke path: fewer streams, certification disabled, outputs stamped '_fast'")
    parser.add_argument("--n-jobs", type=int, default=os.cpu_count(),
                        help="Worker processes. Outputs do not depend on this value: every task carries its own seed.")
    args = parser.parse_args()

    suffix = "_fast" if args.fast else ""
    RESULTS_DIR = BASE_DIR / "results" / "R03_fpr_explosion"
    DATA_DIR = RESULTS_DIR / "data"
    FIGURES_DIR = RESULTS_DIR / "figures"
    TABLES_DIR = RESULTS_DIR / "tables"
    LOGS_DIR = BASE_DIR / "logs" / "R03_fpr_explosion"
    REFERENCE_DIR = BASE_DIR / "data" / "reference" / "R03"

    for d in [DATA_DIR, FIGURES_DIR, TABLES_DIR, LOGS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(LOGS_DIR / f"exp_R03_fpr_explosion{suffix}.log", f"exp_R03_fpr_explosion{suffix}")
    if not verify_hash_seed(logger):
        sys.exit(1)

    log_environment(logger, ["numpy", "pandas", "scipy", "matplotlib"])

    n_streams = 10 if args.fast else N_STREAMS_SPEC
    n_seeds = 10 if args.fast else 400

    # (a) Conformity to the v87 specification.
    logger.info(
        f"Specification: n_streams = {n_streams}, stream_length = {STREAM_LENGTH}, "
        f"lambda_iid = {LAMBDA_IID}, delta_P = {DELTA_P}, alpha = {ALPHA_GARCH}")
    if args.fast:
        logger.warning(
            "DEGRADED PATH selected by --fast: certification gates are disabled and every "
            f"artefact is stamped '{suffix}'. This path never certifies a manuscript number.")
    else:
        spec = {
            "n_streams": (n_streams, N_STREAMS_SPEC),
            "stream_length": (STREAM_LENGTH, 5000),
            "lambda_iid": (LAMBDA_IID, 65.0),
            "delta_P": (DELTA_P, 0.5),
            "alpha": (ALPHA_GARCH, 0.08),
        }
        for name, (observed, required) in spec.items():
            if observed != required:
                logger.error(f"Specification mismatch on {name}: {observed} != {required} (v87 sec:fpr_explosion)")
                sys.exit(1)
        logger.info("Specification check (a): all five protocol constants match v87.")

    # (i) Deterministic reduction.
    logger.info(
        f"Deterministic reduction: ProcessPoolExecutor with max_workers = {args.n_jobs}, executor.map "
        "in submission order, chunksize = 10. No completion-order reduction, no worker-side logging. Outputs are "
        "invariant to the worker count because every task derives its own 128-bit seed.")

    for rule in OPERATIONALISATION_RULES:
        logger.info(f"Certification rule fixed before measurement: {rule}")

    t0 = time.time()

    with ProcessPoolExecutor(max_workers=args.n_jobs) as executor:
        df_cusum, nest_viol_cusum = protocol_1a(n_streams, STREAM_LENGTH, ALPHA_GARCH, LAMBDA_IID, DELTA_P, executor, logger)
        df_adwin, nest_viol_adwin = protocol_1b(n_streams, STREAM_LENGTH, ALPHA_GARCH, executor, logger)
        df_iid = protocol_iid_calibration(n_streams, STREAM_LENGTH, LAMBDA_IID, DELTA_P, executor, logger)
        df_2a = protocol_2a(n_seeds, ALPHA_GARCH, LAMBDA_IID, DELTA_P, DELTA_MU, executor, logger)
        df_2b = protocol_2b(n_seeds, ALPHA_GARCH, LAMBDA_IID, DELTA_P, DELTA_MU, executor, logger)
        df_2c = protocol_2c(n_seeds, ALPHA_GARCH, LAMBDA_IID, DELTA_P, DELTA_MU, GRADUAL_WIDTH, executor, logger)

    elapsed = time.time() - t0

    outputs = {
        f"R03_fpr_cusum{suffix}.csv": df_cusum,
        f"R03_fpr_adwin{suffix}.csv": df_adwin,
        f"R03_iid_calibration_check{suffix}.csv": df_iid,
        f"R03_add_vs_gamma{suffix}.csv": df_2a,
        f"R03_add_vs_width{suffix}.csv": df_2b,
        f"R03_sensitivity{suffix}.csv": df_2c,
    }
    for name, frame in outputs.items():
        save_fair_csv(frame, DATA_DIR / name)

    # (b) Cardinality.
    if len(df_cusum) != 20 or len(df_adwin) != 20:
        logger.error(f"Cardinality error: CUSUM = {len(df_cusum)}, ADWIN = {len(df_adwin)}, expected 20 each")
        sys.exit(1)
    logger.info("Cardinality check (b): both grid files carry 20 rows.")

    # (e) Internal consistency.
    # The shared-realisation premise is verified rather than assumed: each worker
    # reports whether its own indicators nest, so a violation count above zero means
    # the columns no longer come from one realisation evaluated at several thresholds,
    # the ordering stops being a deterministic identity, and the exemption from the
    # multiple-testing rule of the preamble no longer holds.
    logger.info(
        f"Shared-realisation verdict: per-stream nesting violations, CUSUM = {nest_viol_cusum}, "
        f"ADWIN = {nest_viol_adwin} over {len(df_cusum) * n_streams} and {len(df_adwin) * n_streams} streams. "
        "Zero violations means each row's columns are one realisation read at several thresholds, "
        "so the column ordering below is a deterministic identity and not a hypothesis test.")
    if nest_viol_cusum or nest_viol_adwin:
        logger.error(
            "Per-stream nesting is violated: the three CUSUM columns (or the two ADWIN columns) do not "
            "share a realisation. The ordering check is no longer structural and the certification "
            "design must be revisited before any value is reported.")
        sys.exit(1)

    if not (df_cusum['FPR_gamma'] <= df_cusum['FPR_sqrt']).all():
        logger.error("Consistency failed: FPR_gamma > FPR_sqrt on at least one row")
        sys.exit(1)
    if not (df_cusum['FPR_sqrt'] <= df_cusum['FPR_raw']).all():
        logger.error("Consistency failed: FPR_sqrt > FPR_raw on at least one row")
        sys.exit(1)
    if not (df_adwin['FPR_recalib'] <= df_adwin['FPR_raw']).all():
        logger.error("Consistency failed: FPR_recalib > FPR_raw on at least one row")
        sys.exit(1)
    logger.info("Consistency check (e): threshold ordering holds on all 20 rows of both files.")

    # Monotonicity of FPR_raw in Gamma beyond Gamma = 6. Unlike the ordering above this
    # is a hypothesis test, so its tolerance is derived from the sampling mechanism and
    # not from the observed departure: standard error of a difference of two binomial
    # proportions at n streams, Bonferroni-corrected one-sided over the consecutive
    # differences of the region at a family-wise level of 1%.
    df_high = df_cusum[df_cusum['Gamma'] > GAMMA_MONOTONE_CUT]
    diffs = df_high['FPR_raw'].diff().dropna()
    p_bar_high = df_high['FPR_raw'].mean()
    m_diffs = len(diffs)
    se_diff = np.sqrt(2.0 * p_bar_high * (1.0 - p_bar_high) / n_streams)
    z_bonf = stats.norm.ppf(1.0 - FAMILYWISE_ALPHA / m_diffs)
    monotone_bound = -z_bonf * se_diff
    rho, rho_p = stats.spearmanr(df_high['Gamma'], df_high['FPR_raw'])
    logger.info(
        f"Monotonicity check (e): {m_diffs} consecutive differences beyond Gamma = {GAMMA_MONOTONE_CUT}; "
        f"mechanism-derived bound = {monotone_bound:.5f} (SE_diff = {se_diff:.5f}, z_bonf = {z_bonf:.3f} at "
        f"family-wise alpha = {FAMILYWISE_ALPHA}); most negative observed difference = {diffs.min():+.6f}; "
        f"Spearman rho = {rho:.4f} (p = {rho_p:.3e}).")
    if (diffs < monotone_bound).any():
        logger.error(
            f"Monotonicity failed: a consecutive difference of {diffs.min():.6f} falls below the "
            f"mechanism-derived bound {monotone_bound:.6f}. This is a structural defect, not sampling noise.")
        sys.exit(1)

    # (f) Embedded certification on aggregate statistics.
    df_cert = df_cusum[df_cusum['Gamma'] > GAMMA_CERTIFICATION_CUT]
    n_points_cert = len(df_cert)
    n_cert = n_points_cert * n_streams
    k_raw = int(round(df_cert['FPR_raw'].sum() * n_streams))
    k_sqrt = int(round(df_cert['FPR_sqrt'].sum() * n_streams))
    k_recalib = int(round(df_adwin['FPR_recalib'].sum() * n_streams))
    n_adwin = len(df_adwin) * n_streams

    cusum_raw_mean = k_raw / n_cert
    cusum_sqrt_mean = k_sqrt / n_cert
    adwin_recalib_mean = k_recalib / n_adwin

    if args.fast:
        logger.warning("Certification (f) skipped on the degraded path; the gates are sized for 300 streams.")
    else:
        ok_raw, cusum_raw_mean, _, _ = log_aggregate_gate(
            logger, "mean FPR_raw over Gamma > 20", k_raw, n_cert, n_points_cert, n_streams, low=CUSUM_RAW_FLOOR)
        ok_sqrt, cusum_sqrt_mean, _, _ = log_aggregate_gate(
            logger, "mean FPR_sqrt over Gamma > 20", k_sqrt, n_cert, n_points_cert, n_streams,
            low=CUSUM_SQRT_BAND_LOW, high=CUSUM_SQRT_BAND_HIGH)
        ok_recalib, adwin_recalib_mean, _, _ = log_aggregate_gate(
            logger, "mean FPR_recalib over the whole grid", k_recalib, n_adwin, len(df_adwin), n_streams,
            high=ADWIN_RECALIB_CEILING)

        raw_min_cell = df_cert.loc[df_cert['FPR_raw'].idxmin()]
        sqrt_max_cell = df_cert.loc[df_cert['FPR_sqrt'].idxmax()]
        recalib_max_cell = df_adwin.loc[df_adwin['FPR_recalib'].idxmax()]
        log_extremal_warning(logger, "min FPR_raw over Gamma > 20", raw_min_cell['FPR_raw'], raw_min_cell['Gamma'],
                             raw_min_cell['FPR_raw'] < CUSUM_RAW_FLOOR, n_points_cert, n_streams,
                             CUSUM_RAW_FLOOR, cusum_raw_mean, "below")
        log_extremal_warning(logger, "max FPR_sqrt over Gamma > 20", sqrt_max_cell['FPR_sqrt'], sqrt_max_cell['Gamma'],
                             sqrt_max_cell['FPR_sqrt'] > CUSUM_SQRT_BAND_HIGH, n_points_cert, n_streams,
                             CUSUM_SQRT_BAND_HIGH, cusum_sqrt_mean, "above")
        log_extremal_warning(logger, "max FPR_recalib over the whole grid", recalib_max_cell['FPR_recalib'],
                             recalib_max_cell['Gamma'], recalib_max_cell['FPR_recalib'] > ADWIN_RECALIB_CEILING,
                             len(df_adwin), n_streams, ADWIN_RECALIB_CEILING, adwin_recalib_mean, "above")

        if not (ok_raw and ok_sqrt and ok_recalib):
            logger.error(
                "An aggregate certification gate failed. The margins are several standard errors wide, so "
                "this is not sampling noise: a qualitative claim of v87 is contradicted (D3). Reporting "
                "stops here. Neither the threshold, nor the grid region, nor the draw may be adjusted.")
            sys.exit(1)
        logger.info("Certification check (f): the three aggregate gates hold.")

    # i.i.d. calibration arm, reported without prejudging.
    for row in df_iid.itertuples(index=False):
        logger.info(
            f"i.i.d. calibration at Gamma = 1: {row.detector} FPR = {row.FPR:.6f} "
            f"({row.alarms}/{row.n_streams}), Wilson 95% [{row.wilson_low:.6f}, {row.wilson_high:.6f}], "
            f"contains the {NOMINAL_LEVEL:.0%} nominal level: {row.contains_nominal}")

    # D0-D3 classification against the vendored witness of the submitted campaign.
    # Withheld on the degraded path: comparing ten streams against a three-hundred-stream
    # witness produces degrees that describe the sample size, not a deviation.
    witness_cusum_path = REFERENCE_DIR / "protocol_1a_fpr_cusum.csv"
    witness_adwin_path = REFERENCE_DIR / "protocol_1b_fpr_adwin.csv"
    if not (witness_cusum_path.exists() and witness_adwin_path.exists()):
        logger.error(f"Historical witness missing under {REFERENCE_DIR}: deviation classification cannot be computed.")
        sys.exit(1)
    w_cusum = pd.read_csv(witness_cusum_path, float_precision='round_trip')
    w_adwin = pd.read_csv(witness_adwin_path, float_precision='round_trip')
    w_cert = w_cusum[w_cusum['Gamma'] > GAMMA_CERTIFICATION_CUT]

    comparisons = [
        ("CUSUM FPR_raw max", w_cusum['FPR_raw'].max(), df_cusum['FPR_raw'].max(),
         f"protocol_1a[FPR_raw] at Gamma = {w_cusum.loc[w_cusum['FPR_raw'].idxmax(), 'Gamma']:.4f}"),
        ("CUSUM FPR_raw min over Gamma > 20", w_cert['FPR_raw'].min(), df_cert['FPR_raw'].min(),
         f"protocol_1a[FPR_raw] at Gamma = {w_cert.loc[w_cert['FPR_raw'].idxmin(), 'Gamma']:.4f}"),
        ("CUSUM FPR_raw mean over Gamma > 20", w_cert['FPR_raw'].mean(), cusum_raw_mean,
         "protocol_1a[FPR_raw], 16-point mean"),
        ("CUSUM FPR_sqrt max", w_cusum['FPR_sqrt'].max(), df_cusum['FPR_sqrt'].max(),
         f"protocol_1a[FPR_sqrt] at Gamma = {w_cusum.loc[w_cusum['FPR_sqrt'].idxmax(), 'Gamma']:.4f}"),
        ("CUSUM FPR_sqrt mean over Gamma > 20", w_cert['FPR_sqrt'].mean(), cusum_sqrt_mean,
         "protocol_1a[FPR_sqrt], 16-point mean"),
        ("CUSUM FPR_gamma max", w_cusum['FPR_gamma'].max(), df_cusum['FPR_gamma'].max(),
         f"protocol_1a[FPR_gamma] at Gamma = {w_cusum.loc[w_cusum['FPR_gamma'].idxmax(), 'Gamma']:.4f}"),
        ("CUSUM FPR_raw at lowest Gamma", w_cusum['FPR_raw'].iloc[0], df_cusum['FPR_raw'].iloc[0],
         f"protocol_1a[FPR_raw] at Gamma = {w_cusum['Gamma'].iloc[0]:.4f}"),
        ("ADWIN FPR_raw max", w_adwin['FPR_raw'].max(), df_adwin['FPR_raw'].max(),
         f"protocol_1b[FPR_raw] at Gamma = {w_adwin.loc[w_adwin['FPR_raw'].idxmax(), 'Gamma']:.4f}"),
        ("ADWIN FPR_recalib max", w_adwin['FPR_recalib'].max(), df_adwin['FPR_recalib'].max(),
         f"protocol_1b[FPR_recalib] at Gamma = {w_adwin.loc[w_adwin['FPR_recalib'].idxmax(), 'Gamma']:.4f}"),
        ("ADWIN FPR_recalib mean", w_adwin['FPR_recalib'].mean(), adwin_recalib_mean,
         "protocol_1b[FPR_recalib], 20-point mean"),
        ("ADWIN FPR_raw at lowest Gamma", w_adwin['FPR_raw'].iloc[0], df_adwin['FPR_raw'].iloc[0],
         f"protocol_1b[FPR_raw] at Gamma = {w_adwin['Gamma'].iloc[0]:.4f}"),
    ]
    if args.fast:
        logger.warning(
            "Deviation classification withheld on the degraded path: ten streams compared against a "
            "three-hundred-stream witness would yield degrees that describe the sample size, not a deviation.")
    else:
        logger.info("Deviation classification against the submitted campaign, at the printing precision of v87:")
        logger.info(f"{'quantity':<38} | {'published':>10} | {'regenerated':>11} | {'degree':>6} | source cell")
        for label, published, regenerated, cell in comparisons:
            degree = classify_deviation(float(published), float(regenerated))
            logger.info(f"{label:<38} | {published:>10.6f} | {regenerated:>11.6f} | {degree:>6} | {cell}")

    plot_fig03(df_cusum, df_adwin, STREAM_LENGTH, FIGURES_DIR, suffix)

    # Macros. Every value is computed from the in-memory objects; none is hard-coded.
    lowest_gamma = df_cusum['Gamma'].iloc[0]
    iid_cusum = df_iid[df_iid['detector'] == "StrictCUSUM"].iloc[0]
    iid_adwin = df_iid[df_iid['detector'] == "ADWIN"].iloc[0]
    macros = [
        "% Auto-generated by exp_R03_fpr_explosion.py -- do not edit.",
        f"\\newcommand{{\\RThreeStreamsPerPoint}}{{{n_streams}}}",
        f"\\newcommand{{\\RThreeStreamLength}}{{{STREAM_LENGTH}}}",
        f"\\newcommand{{\\RThreeLambdaIid}}{{{LAMBDA_IID}}}",
        f"\\newcommand{{\\RThreeDeltaP}}{{{DELTA_P}}}",
        f"\\newcommand{{\\RThreeAlphaGarch}}{{{ALPHA_GARCH}}}",
        f"\\newcommand{{\\RThreeGammaMin}}{{{df_cusum['Gamma'].min():.2f}}}",
        f"\\newcommand{{\\RThreeGammaMax}}{{{df_cusum['Gamma'].max():.1f}}}",
        f"\\newcommand{{\\RThreeLowestGamma}}{{{lowest_gamma:.2f}}}",
        f"\\newcommand{{\\RThreeCusumFprRawMax}}{{{df_cusum['FPR_raw'].max()*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeCusumFprRawMinAboveTwenty}}{{{df_cert['FPR_raw'].min()*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeCusumFprRawMeanAboveTwenty}}{{{cusum_raw_mean*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeCusumSqrtPlateau}}{{{cusum_sqrt_mean*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeCusumSqrtPlateauMax}}{{{df_cert['FPR_sqrt'].max()*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeCusumGammaRuleMax}}{{{df_cusum['FPR_gamma'].max()*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeAdwinFprRawMax}}{{{df_adwin['FPR_raw'].max()*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeAdwinFprRecalibMax}}{{{df_adwin['FPR_recalib'].max()*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeAdwinFprRecalibMean}}{{{adwin_recalib_mean*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeCusumFprLowestGamma}}{{{df_cusum['FPR_raw'].iloc[0]*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeAdwinFprLowestGamma}}{{{df_adwin['FPR_raw'].iloc[0]*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeCusumFprIid}}{{{iid_cusum['FPR']*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeCusumFprIidWilsonLow}}{{{iid_cusum['wilson_low']*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeCusumFprIidWilsonHigh}}{{{iid_cusum['wilson_high']*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeAdwinFprIid}}{{{iid_adwin['FPR']*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeAdwinFprIidWilsonLow}}{{{iid_adwin['wilson_low']*100:.1f}\\%}}",
        f"\\newcommand{{\\RThreeAdwinFprIidWilsonHigh}}{{{iid_adwin['wilson_high']*100:.1f}\\%}}",
    ]
    tex_name = f"R03_claims{suffix}.tex"
    with open(TABLES_DIR / tex_name, "w") as f:
        f.write("\n".join(macros) + "\n")

    # Log artifact manifest
    artifact_files = [DATA_DIR / name for name in outputs] + [
        FIGURES_DIR / f"fig03_fpr_explosion{suffix}.png",
        TABLES_DIR / tex_name
    ]
    log_artifact_manifest(logger, artifact_files, BASE_DIR, BASE_DIR)

    # (g) and (h) Traceability of every artefact.
    for name in outputs:
        logger.info(f"SHA-256 {name} : {compute_sha256(DATA_DIR / name)}")
    logger.info(f"SHA-256 fig03_fpr_explosion{suffix}.png : {compute_sha256(FIGURES_DIR / f'fig03_fpr_explosion{suffix}.png')}")
    logger.info(f"SHA-256 {tex_name} : {compute_sha256(TABLES_DIR / tex_name)}")

    logger.info(f"Execution completed in {elapsed:.1f}s with {args.n_jobs} workers.")


if __name__ == "__main__":
    main()
