#!/usr/bin/env python3
"""
==========================================================================
R04 -- ISO-FPR RACE AND RELATIVE EFFICIENCY (FIGURE 4, TABLE 3)
==========================================================================
Races four monitoring pipelines against one another under a location drift,
every arm calibrated by bisection to the same 5% false-alarm rate so that a
comparison of their delays is licit.

Two results are targeted. Under a location drift the squared sensor is
structurally slow, because the shift enters the squared stream only at second
order. And the delay ratio between the sign filter and the parametric route is
governed by the Pitman efficiency of the sign test, which inverts in the
heavy-tailed regime.

Arms:
- Recalib    : (eps_t / sigma_hat_t)^2 - 1, the standardized squared residual,
               a scale sensor applied to a location pathology.
- Eco_L1     : eps_t / sigma_hat_t, GARCH(1,1) fitted by QMLE on the warm-up,
               the parametric location monitor.
- Oracle_Eco : the same statistic standardized by the TRUE GARCH parameters,
               the ideal bound that isolates the estimation cost.
- Concept    : 1{eps_t > 0} - 1/2, the binary sign-error stream, a monitor that
               estimates no variance at all.

Notations (v87):
- Gamma        : GARCH penalty factor, inflation of the variance of the partial
                 sums of the monitored stream; closed form in (alpha, beta).
- c            : drift magnitude in units of the unconditional standard
                 deviation, Delta = c * sigma_unc.
- delta_R      : CUSUM reference drift of the Recalib arm, c^2/2 = 0.125.
- delta_eco    : CUSUM reference drift of the standardized arms, c/2 = 0.25.
- delta_concept: CUSUM reference drift of the sign arm, (F_nu(c/scale) - 1/2)/2.
- lambda_star  : threshold obtained by bisection so the arm reaches 5% FPR.
- f_z(0)       : standardized innovation density at zero; governs the Pitman
                 efficiency of the sign filter against the parametric monitor.
- kappa_z      : kurtosis of the standardized innovation; appears in the
                 denominator of the second-order entry of the shift into the
                 squared stream.
- nu_star      : degrees of freedom at which the delay ratio crosses unity.
- ADD          : average detection delay. DetRate : fraction of streams alarming.

References:
- Page, E. S. (1954). Continuous inspection schemes. Biometrika, 41(1/2), 100-115.
- Tartakovsky, A., Nikiforov, I. & Basseville, M. (2014). Sequential Analysis:
  Hypothesis Testing and Changepoint Detection. CRC Press.
- van der Vaart, A. W. (1998). Asymptotic Statistics. Cambridge University Press.
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
import math
import argparse
import hashlib
from concurrent.futures import ProcessPoolExecutor
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.optimize import minimize, brentq

# --- PROTOCOL SPECIFICATION (v87, sec:magnitude, fig:isofpr, tab:isofpr_race) ---
# Binding specification. If the script diverges from these values, the script is wrong.
N_STREAMS_SPEC = 2000
STREAM_LENGTH = 5000
WARMUP = 500
ALPHA_GARCH = 0.05
NU_RACE = 30.0
TARGET_FPR = 0.05
BISECTION_TOL = 0.003
BISECTION_ITERS = 15
GAMMA_GRID = (1.0, 11.58, 50.0, 200.0)
C_GRID = (0.25, 0.5, 1.0, 2.0)
NU_GRID = (3.0, 4.0, 4.5, 5.0, 7.0, 30.0)
GAMMA_RACE = 11.58
C_REFERENCE = 1.0
DELTA_R = 0.125
DELTA_ECO = 0.25
ARMS = ("Recalib", "Eco_L1", "Oracle_Eco", "Concept")
FIRST_ORDER_ARMS = ("Eco_L1", "Concept")

# M0, the constant-threshold control: the Concept CUSUM is fixed once and for
# all in v87 (sec:scaling_validation, lambda_C = 10, delta_C = 0.1) and is not
# recalibrated per Gamma. 5000 null streams, as the submitted campaign ran it.
M0_STREAMS = 5000
M0_LAMBDA = 10.0
M0_DELTA = 0.1

# M4, the family control: the ADWIN-type detector and the CUSUM are calibrated
# on i.i.d. Gaussian streams and then read across the Gamma grid.
M4_ADWIN_ITERS = 12
M4_ADWIN_LOG_LOW = 0.1
M4_ADWIN_LOG_HIGH = 10.0

# --- CERTIFICATION THRESHOLDS AND WHERE THEY COME FROM ---
# Fixed here, before any regenerated value is read. Every one is a literal of
# v87 or of the R04 prompt; none operationalises prose.
#   "all arms calibrated to 5% FPR by bisection"      -> control (c)
#   "lambda_C^star in [10.6, 10.7] across Gamma"      -> control (d), band widened
#                                                        to [10.5, 10.8] by the prompt
#   "a blind zone that persists even at Gamma = 1"    -> control (e)
#   "runs 2 to 19x behind the two first-order monitors" -> control (h)
#   "clearing the dead band delta_R = 0.125 only above c* ~ 0.43" -> control (h)
#   "crossing unity at a measured nu* ~ 4.9 (analytic 4.7)"       -> control (h)
#   "an oracle arm ... crosses at 4.6"                            -> control (h)
CONCEPT_LAMBDA_BAND = (10.5, 10.8)
BLIND_ZONE_C_CUT = 0.5
SLOWDOWN_PUBLISHED = (2, 19)
NU_STAR_PUBLISHED = 4.9
NU_STAR_ORACLE_PUBLISHED = 4.6
NU_STAR_ANALYTIC_PUBLISHED = 4.7
GAUSSIAN_CEILING = math.pi / 2.0

# QMLE fallback budget, derived from the mechanism rather than from an observed
# rate. SLSQP is run under the constraint alpha + beta <= 0.999 and the bounds
# alpha in [1e-6, 0.5], beta in [1e-6, 0.99], so any pair it returns is
# stationary and positive by construction. The stationarity guard downstream can
# therefore only fire if the optimiser violates its own feasible set, which has
# no admissible frequency at all: the budget is zero, and a single fallback is a
# structural failure to investigate rather than noise to tolerate.
#
# An earlier revision of this script guarded on alpha + beta >= 0.999 -- the same
# predicate the submitted script uses -- which does not test stationarity but
# re-tests the optimiser's constraint with a strict inequality, and so rejected
# precisely the boundary the solver is entitled to return. It fired on 1.1% of
# warm-ups overall and 5.3% at Gamma = 200, with SLSQP reporting success and
# never landing on its own initial point in 1600 diagnostic fits. That guard was
# wrong; the budget was not too tight.
# The stationarity guard is unreachable once the feasible-set projection below
# is in place, so its budget is zero: one firing is a structural failure.
QMLE_STATIONARITY_BUDGET = 0.0
QMLE_PERSISTENCE_CAP = 0.999
QMLE_STARTS = ((0.05, 0.90), (0.10, 0.85), (0.02, 0.95))

# Budget for genuine optimiser non-convergence, derived from what it protects
# rather than from what was observed. A fallback fit perturbs the detection time
# of ONE stream in one arm; the quantity at risk is a mean over N = 2000 streams,
# whose own standard error is of order 1% of its value on the fastest cells. A
# fallback rate of 0.5% cannot move such a mean by more than a fraction of its
# SEM, and therefore cannot move a value at the printing precision of Table 3.
# The measured rate sits roughly twenty times below this bound, which is the
# margin the bound is meant to have and not the reason it was chosen.
QMLE_CONVERGENCE_BUDGET = 0.005
QMLE_FALLBACK_ALPHA = 0.05
QMLE_FALLBACK_BETA = 0.90

# Printing precision of Table 3 in v87. Reverse-engineered from the twelve
# published cells and verified against all of them: three significant figures,
# floored at integer precision. 2293.457 -> 2293, 202.628 -> 203, 55.909 -> 55.9,
# 72.002 -> 72.0. A plain "%.3g" would print 2290 and 1340, which v87 does not.
TABLE_SIGNIFICANT_FIGURES = 3


def get_deterministic_seed(*args) -> int:
    """
    Derives a 128-bit collision-free seed from the semantic coordinates of a
    task, returned as a scalar integer so no entropy is discarded.

    Floats are formatted through .hex() rather than str(): the decimal
    repr of a float is platform-dependent at the last digit on some C
    libraries, which would silently re-key a cell across machines. The native
    hash() is randomly salted and is forbidden outright to ensure cross-platform reproducibility.
    """
    def format_arg(arg):
        if isinstance(arg, (float, np.floating)):
            return float(arg).hex()
        return str(arg)

    s = "_".join(map(format_arg, args))
    return int(hashlib.md5(s.encode('utf-8')).hexdigest(), 16)


# --- PRIMITIVES, DUPLICATED VERBATIM ---
# These routines are deliberately NOT hoisted into experiments/common/. The
# copies carried by the other experiments of this repository differ numerically
# from one another, and mutualising them would silently move published values.

def simulate_garch11(n, omega, alpha, beta, nu=7.0, seed=None):
    rng = np.random.default_rng(seed)
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
    """One-sided strict CUSUM. Returns the index of the first crossing, or -1."""
    S = 0.0
    for t in range(len(stream)):
        S = max(0.0, S + float(stream[t]) - delta_P)
        if S > threshold: return t
    return -1


def cusum_running_max(stream, delta_P):
    """
    Supremum of the same recursion as strict_cusum, over the same horizon.

    This is not a second detector. A stream alarms at threshold lambda if and
    only if sup_t S_t > lambda, so one pass of this function answers
    `strict_cusum(stream, delta_P, lambda) != -1` for EVERY lambda at once. The
    bisection below is therefore run in full -- same domain, same iteration
    count, same tolerance, same lambda trajectory -- against a memoised
    evaluation of its own false-alarm count rather than against a fresh sweep of
    the stream. The recursion, the arithmetic and the strict `>` comparison are
    identical to strict_cusum, so the equivalence is exact rather than
    approximate; main() asserts it on a sample before any calibration is used.
    """
    S = 0.0
    S_max = 0.0
    for t in range(len(stream)):
        S = max(0.0, S + float(stream[t]) - delta_P)
        if S > S_max: S_max = S
    return S_max


def _garch_nll(params, eps, var_emp):
    """Gaussian QMLE negative log-likelihood, GARCH(1,1) with variance targeting."""
    alpha, beta = params
    omega = var_emp * (1.0 - alpha - beta)
    n = len(eps)
    sigma2 = np.zeros(n)
    sigma2[0] = var_emp
    for t in range(1, n):
        sigma2[t] = omega + alpha * eps[t-1]**2 + beta * sigma2[t-1]
        if sigma2[t] < 1e-10: sigma2[t] = 1e-10
    return 0.5 * np.sum(np.log(sigma2) + (eps**2) / sigma2)


def fit_garch_qmle(eps_warmup):
    """
    Fits GARCH(1,1) by QMLE on the warm-up segment only, variance targeting.

    The finite-difference step and tolerances are set to account for gradient noise
    of an SLSQP run on a recursive likelihood, which is amplified by the FPU. The
    step is therefore widened and the solution truncated deterministically.

    Returns ((omega, alpha, beta), converged). `converged` is False when SLSQP
    reports failure OR when it returns its own initial point, which on this
    likelihood means it never left the starting simplex. The caller is required
    to act on the flag; it is never silently discarded.
    """
    var_emp = np.var(eps_warmup)
    bounds = [(1e-6, 0.5), (1e-6, 0.99)]
    constraints = {'type': 'ineq', 'fun': lambda x: QMLE_PERSISTENCE_CAP - (x[0] + x[1])}

    # Deterministic multistart. A single start leaves roughly two fits in ten
    # thousand on which SLSQP reports failure, scattered across the grid and
    # independent of tail weight. Restarting from a fixed ladder of interior
    # points is a correction in the solution space, where substituting a default pair
    # would be the masked fallback it forbids.
    # The ladder is fixed, ordered and short-circuited on the first success, so
    # the result is deterministic and costs nothing on the fits that converge.
    for init_a, init_b in QMLE_STARTS:
        init = [init_a, init_b]
        try:
            res = minimize(_garch_nll, init, args=(eps_warmup, var_emp), method='SLSQP',
                           bounds=bounds, constraints=constraints,
                           options={'eps': 1e-5, 'ftol': 1e-8})
        except (ValueError, FloatingPointError, np.linalg.LinAlgError):
            continue
        if not res.success:
            continue
        a, b = float(res.x[0]), float(res.x[1])
        # SLSQP enforces an inequality constraint only to a tolerance, so it can
        # terminate marginally outside alpha + beta <= 0.999 on a flat
        # likelihood. The violation is corrected in the solution space, by
        # projecting the pair along its own ray onto the feasible boundary, which
        # preserves the ratio of the two coefficients and hence the persistence
        # structure the fit found.
        total = a + b
        if total > QMLE_PERSISTENCE_CAP:
            scale = QMLE_PERSISTENCE_CAP / total
            a, b = a * scale, b * scale
        a, b = round(a, 6), round(b, 6)
        if max(abs(a - init_a), abs(b - init_b)) > 1e-6:
            return (var_emp * (1.0 - a - b), a, b), True

    fallback_a, fallback_b = QMLE_FALLBACK_ALPHA, QMLE_FALLBACK_BETA
    return (var_emp * (1.0 - fallback_a - fallback_b), fallback_a, fallback_b), False


def filter_sigma2(eps, omega, alpha, beta, var_init):
    """Filters the conditional variance with FROZEN parameters, zero look-ahead."""
    n = len(eps)
    sigma2 = np.zeros(n)
    sigma2[0] = var_init
    for t in range(1, n):
        sigma2[t] = omega + alpha * eps[t-1]**2 + beta * sigma2[t-1]
        if sigma2[t] < 1e-10: sigma2[t] = 1e-10
    return sigma2


def fast_adwin_first_alarm(stream, delta):
    """
    ADWIN-type window-mean detector on a coarse grid: window ends every 32
    steps, split points every 16. Distinct from the ADWIN variant of R03, which
    halves a growing window and uses a fixed variance proxy; that divergence is
    deliberate and the two are never merged.
    """
    N = len(stream)
    for end in range(32, N + 1, 32):
        window = stream[:end]
        n = len(window)
        cum = np.cumsum(window)
        cum_sq = np.cumsum(window**2)
        total = cum[-1]
        for i in range(16, n - 15, 16):
            n0 = i
            n1 = n - i
            mu0 = cum[i-1] / n0
            mu1 = (total - cum[i-1]) / n1
            var_W = (cum_sq[-1] / n) - (total / n)**2
            if var_W < 1e-6: var_W = 1e-6
            m = 1.0 / (1.0/n0 + 1.0/n1)
            eps_cut = np.sqrt((2 * var_W / m) * np.log(2 * n / delta)) + (2 / (3 * m)) * np.log(2 * n / delta)
            if abs(mu0 - mu1) > eps_cut:
                return end
    return -1


def wilson_interval(k, n, confidence=0.95):
    """Wilson score interval, clamped to the unit interval before persistence."""
    if n == 0: return 0.0, 0.0
    z = stats.norm.ppf(0.5 + confidence / 2.0)
    p_hat = k / n
    den = 1.0 + z * z / n
    centre = (p_hat + z * z / (2.0 * n)) / den
    half = z * np.sqrt(p_hat * (1.0 - p_hat) / n + z * z / (4.0 * n * n)) / den
    low = max(0.0, min(1.0, centre - half))
    high = max(0.0, min(1.0, centre + half))
    # The Wilson interval is the set of p whose score statistic is within z, so
    # it contains p_hat by construction. At p_hat = 1 the algebra gives
    # centre + half = 1 exactly, but in floating point it lands one ulp below and
    # the persisted interval would then exclude its own estimate. Enforcing
    # containment restores an identity that the arithmetic broke; it is the same
    # class of correction as the domain clamping above.
    return min(low, p_hat), max(high, p_hat)


def standardised_t_density_at_zero(nu):
    """f_z(0) for a Student-t scaled to unit variance."""
    return stats.t.pdf(0.0, df=nu) / np.sqrt((nu - 2.0) / nu)


def concept_reference_drift(c, nu):
    """
    CUSUM reference drift of the sign arm: half the post-change mean of the
    centred sign stream, P(eps > -c*sigma) - 1/2, under standardized t_nu.
    """
    scale = np.sqrt((nu - 2.0) / nu) if nu > 2.0 else 1.0
    return (stats.t.cdf(c / scale, df=nu) - 0.5) / 2.0


# --- WORKERS ---
# No worker logs, no worker writes: concurrent writes to one file are a race
# condition that breaks the digest of the log. Diagnostics travel
# back in the return value and are reduced in submission order by the caller.

def _worker_race(args):
    """
    One stream of the iso-FPR race: generate, fit the warm-up, filter, and
    reduce the four monitored sequences to one scalar per arm.

    With `lambdas` None the scalar is sup_t S_t, which calibrates every
    threshold at once. With `lambdas` supplied the scalar is the alarm index at
    that threshold, or -1. Both paths share one generation, so the four arms of
    a cell are always read off the same realisation and the race is paired.
    """
    (seed, warmup, H, omega, alpha, beta, nu, c_shift, sigma_unc, deltas, lambdas) = args

    eps_full = simulate_garch11(warmup + H, omega, alpha, beta, nu=nu, seed=seed)

    if warmup > 0:
        eps_w = eps_full[:warmup]
        (_, a_hat, b_hat), converged = fit_garch_qmle(eps_w)
        # The guard tests STATIONARITY, alpha + beta < 1, which is the condition
        # the filtered variance actually needs. It does not re-test the
        # optimiser's own feasibility constraint: SLSQP is constrained to
        # alpha + beta <= 0.999 and bounded below by 1e-6, so a returned pair is
        # admissible by construction and this guard is unreachable in normal
        # operation -- which is why its budget is zero rather than a fraction.
        #
        # The submitted script guarded on `a + b >= 0.999` instead, colliding
        # with the constraint boundary the optimiser is entitled to return, and
        # silently reverted those fits to (0.05, 0.90). That reversion is counted
        # separately below so its extent can be reported rather than inferred.
        stationary = (a_hat + b_hat < 1.0) and (a_hat >= 0.0) and (b_hat >= 0.0)
        boundary = 1 if (a_hat + b_hat >= QMLE_PERSISTENCE_CAP) else 0
        if not (converged and stationary):
            a_hat, b_hat = QMLE_FALLBACK_ALPHA, QMLE_FALLBACK_BETA
        var_init = float(np.var(eps_w))
        w_hat = var_init * (1.0 - a_hat - b_hat)
        fallback = (0 if converged else 1, 0 if stationary else 1, boundary)
    else:
        a_hat, b_hat, w_hat = alpha, beta, omega
        var_init = sigma_unc**2
        fallback = (0, 0, 0)

    eps_shifted = eps_full.copy()
    if c_shift != 0.0:
        eps_shifted[warmup:] += c_shift * sigma_unc

    # Estimated path: filtered from the OBSERVED stream, which after onset carries
    # the shift. That contamination is part of what the parametric route costs.
    sig2_hat = filter_sigma2(eps_shifted, w_hat, a_hat, b_hat, var_init)
    # Oracle path: the true conditional variance. The GARCH recursion is driven
    # by the innovations, not by the returns, so a location shift added to the
    # returns leaves the latent variance path untouched. Filtering the oracle
    # from the pre-shift series is therefore what the true sigma_t IS, not an
    # advantage granted to it.
    sig2_oracle = filter_sigma2(eps_full, omega, alpha, beta, sigma_unc**2)

    eps_test = eps_shifted[warmup:]
    sd_hat = np.sqrt(np.maximum(sig2_hat[warmup:], 1e-10))
    sd_oracle = np.sqrt(np.maximum(sig2_oracle[warmup:], 1e-10))

    z_hat = eps_test / sd_hat
    sequences = (
        z_hat**2 - 1.0,                             # Recalib
        z_hat,                                      # Eco_L1
        eps_test / sd_oracle,                       # Oracle_Eco
        (eps_test > 0).astype(float) - 0.5,         # Concept
    )

    if lambdas is None:
        return tuple(cusum_running_max(s, d) for s, d in zip(sequences, deltas)), fallback
    return tuple(strict_cusum(s, d, lam) for s, d, lam in zip(sequences, deltas, lambdas)), fallback


def _worker_bernoulli(args):
    """M0. One null stream monitored by the fixed Concept CUSUM."""
    seed, H, omega, alpha, beta, nu, source = args
    if source == "garch":
        eps = simulate_garch11(H, omega, alpha, beta, nu=nu, seed=seed)
        sign_stream = (eps > 0).astype(float) - 0.5
    else:
        # Direct fair coin. Corollary cor:universal of v87 states the null law of
        # any statistic built on the binary stream is universal and may be
        # obtained "by direct Monte-Carlo simulation of a fair coin". This arm
        # draws that coin, with no GARCH generator anywhere in its path.
        rng = np.random.default_rng(seed)
        sign_stream = rng.integers(0, 2, size=H).astype(float) - 0.5
    return 1 if strict_cusum(sign_stream, M0_DELTA, M0_LAMBDA) != -1 else 0


def _worker_family(args):
    """M4. One stream; returns the CUSUM supremum and the ADWIN alarm flag."""
    seed, H, omega, alpha, beta, nu, delta_adwin, source = args
    if source == "gaussian":
        stream = np.random.default_rng(seed).standard_normal(H)
    else:
        stream = simulate_garch11(H, omega, alpha, beta, nu=nu, seed=seed)
    adwin = -1 if delta_adwin is None else fast_adwin_first_alarm(stream, delta_adwin)
    return cusum_running_max(stream, DELTA_ECO), (1 if adwin != -1 else 0)


def _worker_adwin_only(args):
    """M4 ADWIN calibration. Regenerates its stream from the same key."""
    seed, H, delta = args
    stream = np.random.default_rng(seed).standard_normal(H)
    return 1 if fast_adwin_first_alarm(stream, delta) != -1 else 0


# --- CALIBRATION ---

def bisect_threshold(sup_stats, target_fpr, tol, max_iter):
    """
    The bisection of the submitted campaign, unchanged in domain, update rule,
    iteration count and tolerance. `sup_stats` is the vector of per-stream CUSUM
    suprema, so `(sup_stats > lam).mean()` is exactly the false-alarm rate the
    submitted script obtained by re-running the detector at `lam`.

    Returns the threshold, the achieved rate, the number of iterations actually
    consumed, and whether the tolerance was met.
    """
    sup = np.asarray(sup_stats, dtype=float)
    n = len(sup)
    low, high = 0.001, 1000.0
    for _ in range(10):
        if float((sup > high).sum()) / n <= target_fpr:
            break
        high *= 2.0
    lam = (low + high) / 2.0
    iters_used = max_iter
    for i in range(max_iter):
        lam = (low + high) / 2.0
        fpr = float((sup > lam).sum()) / n
        if abs(fpr - target_fpr) <= tol:
            iters_used = i + 1
            break
        if fpr > target_fpr:
            low = lam
        else:
            high = lam
    fpr = float((sup > lam).sum()) / n
    return lam, fpr, iters_used, abs(fpr - target_fpr) <= tol


def crossing_point(nu_values, ratios):
    """
    Interpolation rule of the R04 prompt section 4, fixed before any regenerated
    value was read: linear interpolation of the delay ratio between the two nu
    values that bracket the crossing of unity, on the grid as sampled.

    Returns (nu_star, nu_lower, nu_upper) so a reader can redo the interpolation
    by hand from the two bracketing rows. The bracket is the FIRST upward
    crossing of unity, scanning the grid in increasing nu.
    """
    nu_values = np.asarray(nu_values, dtype=float)
    ratios = np.asarray(ratios, dtype=float)
    order = np.argsort(nu_values)
    nu_values, ratios = nu_values[order], ratios[order]
    for i in range(len(nu_values) - 1):
        r0, r1 = ratios[i], ratios[i+1]
        if r0 < 1.0 <= r1:
            nu0, nu1 = nu_values[i], nu_values[i+1]
            return nu0 + (nu1 - nu0) * (1.0 - r0) / (r1 - r0), nu0, nu1
    return float('nan'), float('nan'), float('nan')


def garch_parameters(gamma, alpha):
    """
    (omega, beta, sigma_unc) for a target Gamma, unit unconditional variance.

    The argument order of solve_beta_for_gamma is (alpha, target_gamma) and is
    the single point where the submitted campaign failed: it called
    `solve_beta_for_gamma(gamma, alpha)`, so `target_gamma` received alpha = 0.05,
    the guard `if target_gamma <= 1.0: return 0.0` fired on the first line, and
    beta came back 0 at every grid point. main() verifies the realised Gamma
    against the target rather than trusting this call.
    """
    beta = solve_beta_for_gamma(alpha, gamma)
    omega = 1.0 * (1.0 - alpha - beta)
    sigma_unc = np.sqrt(omega / (1.0 - alpha - beta))
    return omega, beta, sigma_unc


# --- PROTOCOLS ---

def protocol_m0(n_streams, executor, logger, seed_registry):
    """Constant-threshold control: the fixed Concept CUSUM under H_0."""
    omega, beta, sigma_unc = garch_parameters(GAMMA_RACE, ALPHA_GARCH)
    rows = []
    for source in ("garch", "bernoulli_iid"):
        tasks = []
        for i in range(n_streams):
            seed = get_deterministic_seed("R04", "M0", source, i)
            seed_registry.append(seed)
            tasks.append((seed, STREAM_LENGTH, omega, ALPHA_GARCH, beta, NU_RACE, source))
        alarms = int(sum(executor.map(_worker_bernoulli, tasks, chunksize=25)))
        fpr = alarms / n_streams
        low, high = wilson_interval(alarms, n_streams)
        rows.append({
            'source': source, 'Gamma': GAMMA_RACE if source == "garch" else 1.0,
            'horizon': STREAM_LENGTH, 'N_streams': n_streams,
            'lambda_C': M0_LAMBDA, 'delta_C': M0_DELTA,
            'alarms': alarms, 'FPR': fpr, 'CI_low': low, 'CI_high': high,
        })
        logger.info(f"M0 [{source}]: FPR = {fpr:.6f} ({alarms}/{n_streams}), Wilson 95% [{low:.6f}, {high:.6f}]")
    return pd.DataFrame(rows)


def protocol_m1_m2(n_streams, executor, logger, seed_registry):
    """Iso-FPR calibration under H_0, then the delay race under a location drift."""
    res_calib, res_race = [], []
    concept_suprema = {}
    qmle = np.zeros(3, dtype=int)
    qmle_total = 0

    for gamma in GAMMA_GRID:
        omega, beta, sigma_unc = garch_parameters(gamma, ALPHA_GARCH)
        deltas = (DELTA_R, DELTA_ECO, DELTA_ECO, concept_reference_drift(0.5, NU_RACE))

        tasks = []
        for i in range(n_streams):
            seed = get_deterministic_seed("R04", "M1", "H0", gamma, i)
            seed_registry.append(seed)
            tasks.append((seed, WARMUP, STREAM_LENGTH, omega, ALPHA_GARCH, beta,
                          NU_RACE, 0.0, sigma_unc, deltas, None))
        results = list(executor.map(_worker_race, tasks, chunksize=25))
        sup = np.array([r[0] for r in results])
        qmle += np.sum([r[1] for r in results], axis=0)
        qmle_total += len(results)

        concept_suprema[gamma] = sup[:, ARMS.index("Concept")].copy()
        lambdas = []
        for j, arm in enumerate(ARMS):
            lam, fpr, iters, converged = bisect_threshold(sup[:, j], TARGET_FPR, BISECTION_TOL, BISECTION_ITERS)
            lambdas.append(lam)
            alarms = int(round(fpr * n_streams))
            low, high = wilson_interval(alarms, n_streams)
            res_calib.append({
                'Gamma': gamma, 'arm': arm, 'delta': deltas[j], 'lambda_star': lam,
                'FPR_achieved': fpr, 'CI_low': low, 'CI_high': high,
                'n_bisection_iter': iters, 'bisection_converged': converged,
            })
            logger.info(f"M1 Gamma={gamma} arm={arm:<10} lambda*={lam:.6f} FPR={fpr:.4f} "
                        f"iters={iters} converged={converged}")

        for c in C_GRID:
            tasks = []
            for i in range(n_streams):
                seed = get_deterministic_seed("R04", "M2", "H1", gamma, c, i)
                seed_registry.append(seed)
                tasks.append((seed, WARMUP, STREAM_LENGTH, omega, ALPHA_GARCH, beta,
                              NU_RACE, c, sigma_unc, deltas, tuple(lambdas)))
            results = list(executor.map(_worker_race, tasks, chunksize=25))
            idx = np.array([r[0] for r in results])
            qmle += np.sum([r[1] for r in results], axis=0)
            qmle_total += len(results)

            for j, arm in enumerate(ARMS):
                detected = idx[:, j][idx[:, j] != -1] + 1
                det_rate = len(detected) / n_streams
                low, high = wilson_interval(len(detected), n_streams)
                res_race.append({
                    'Gamma': gamma, 'arm': arm, 'c': c, 'lambda_star': lambdas[j],
                    'delta': deltas[j], 'DetRate': det_rate, 'CI_low': low, 'CI_high': high,
                    'n_detected': len(detected), 'n_censored': n_streams - len(detected),
                    'horizon': STREAM_LENGTH,
                    # Mean over the streams that alarmed within the horizon. When
                    # DetRate < 1 this is E[T | T <= H], not E[T]: it is bounded
                    # above by the horizon and biased towards the fast streams.
                    # It is never comparable across arms without DetRate.
                    'ADD_conditional': float(np.mean(detected)) if len(detected) else np.nan,
                    'SEM': float(np.std(detected, ddof=1) / np.sqrt(len(detected))) if len(detected) > 1 else np.nan,
                })
            logger.info(f"M2 Gamma={gamma} c={c}: " + ", ".join(
                f"{a}={r['ADD_conditional']:.1f}({r['DetRate']:.3f})"
                for a, r in zip(ARMS, res_race[-4:])))

    return pd.DataFrame(res_calib), pd.DataFrame(res_race), concept_suprema, qmle, qmle_total


def protocol_m3(n_streams, executor, logger, seed_registry, beta_override=None, label=""):
    """
    Relative efficiency against Student-t degrees of freedom, at matched 5% FPR.

    `beta_override` pins beta instead of solving it for GAMMA_RACE, which is how
    the counterfactual arm reproduces the process the submitted generator
    actually produced. The counterfactual reuses the SAME seed keys on purpose,
    so the two arms differ in beta and in nothing else; those seeds are therefore
    not entered in the uniqueness registry, which would otherwise flag the reuse.
    """
    omega, beta, sigma_unc = garch_parameters(GAMMA_RACE, ALPHA_GARCH)
    if beta_override is not None:
        beta = beta_override
        omega = 1.0 * (1.0 - ALPHA_GARCH - beta)
        sigma_unc = np.sqrt(omega / (1.0 - ALPHA_GARCH - beta))
    rows = []
    qmle = np.zeros(3, dtype=int)
    qmle_total = 0
    c = 0.5

    for nu in NU_GRID:
        deltas = (DELTA_R, DELTA_ECO, DELTA_ECO, concept_reference_drift(c, nu))

        tasks = []
        for i in range(n_streams):
            seed = get_deterministic_seed("R04", "M3", "H0", nu, i)
            if seed_registry is not None: seed_registry.append(seed)
            tasks.append((seed, WARMUP, STREAM_LENGTH, omega, ALPHA_GARCH, beta,
                          nu, 0.0, sigma_unc, deltas, None))
        results = list(executor.map(_worker_race, tasks, chunksize=25))
        sup = np.array([r[0] for r in results])
        qmle += np.sum([r[1] for r in results], axis=0)
        qmle_total += len(results)

        lambdas, fprs = [], []
        for j in range(len(ARMS)):
            lam, fpr, _, _ = bisect_threshold(sup[:, j], TARGET_FPR, BISECTION_TOL, BISECTION_ITERS)
            lambdas.append(lam)
            fprs.append(fpr)

        tasks = []
        for i in range(n_streams):
            seed = get_deterministic_seed("R04", "M3", "H1", nu, i)
            if seed_registry is not None: seed_registry.append(seed)
            tasks.append((seed, WARMUP, STREAM_LENGTH, omega, ALPHA_GARCH, beta,
                          nu, c, sigma_unc, deltas, tuple(lambdas)))
        results = list(executor.map(_worker_race, tasks, chunksize=25))
        idx = np.array([r[0] for r in results])
        qmle += np.sum([r[1] for r in results], axis=0)
        qmle_total += len(results)

        adds, rates = {}, {}
        for j, arm in enumerate(ARMS):
            detected = idx[:, j][idx[:, j] != -1] + 1
            adds[arm] = float(np.mean(detected)) if len(detected) else np.nan
            rates[arm] = len(detected) / n_streams

        f0 = standardised_t_density_at_zero(nu)
        rows.append({
            'nu': nu, 'f0_hat': f0, 'c': c,
            'lambda_Eco': lambdas[1], 'lambda_Oracle': lambdas[2], 'lambda_Concept': lambdas[3],
            'FPR_Eco': fprs[1], 'FPR_Oracle': fprs[2], 'FPR_Concept': fprs[3],
            'ADD_Eco_L1': adds['Eco_L1'], 'ADD_Oracle': adds['Oracle_Eco'], 'ADD_Concept': adds['Concept'],
            'DetRate_Eco_L1': rates['Eco_L1'], 'DetRate_Oracle': rates['Oracle_Eco'],
            'DetRate_Concept': rates['Concept'],
            'ratio': adds['Concept'] / adds['Eco_L1'],
            'ratio_oracle': adds['Concept'] / adds['Oracle_Eco'],
            'ratio_pred': 1.0 / (4.0 * f0**2),
        })
        logger.info(f"M3{label} nu={nu}: ADD_Eco={adds['Eco_L1']:.2f} ADD_Oracle={adds['Oracle_Eco']:.2f} "
                    f"ADD_Concept={adds['Concept']:.2f} ratio={rows[-1]['ratio']:.6f} "
                    f"ratio_oracle={rows[-1]['ratio_oracle']:.6f} pred={rows[-1]['ratio_pred']:.6f}")

    return pd.DataFrame(rows), qmle, qmle_total


def protocol_m4(n_streams, executor, logger, seed_registry):
    """
    Family control: a CUSUM and an ADWIN-type detector, both calibrated on
    i.i.d. Gaussian streams, then read across the Gamma grid on the RAW returns.

    The point is the contrast with R03. There the monitored statistic was the
    squared stream, whose long-run variance is Gamma, and the level exploded.
    Here the monitored statistic is the return itself, a martingale difference
    whose partial-sum variance is exactly n*sigma^2 for every Gamma, so the level
    should not move. That is the mean half of the variance/mean dichotomy.
    """
    tasks = []
    for i in range(n_streams):
        seed = get_deterministic_seed("R04", "M4", "calibration", i)
        seed_registry.append(seed)
        tasks.append((seed, STREAM_LENGTH, None, None, None, None, None, "gaussian"))
    results = list(executor.map(_worker_family, tasks, chunksize=25))
    sup_iid = np.array([r[0] for r in results])
    lam_c, fpr_c, iters_c, ok_c = bisect_threshold(sup_iid, TARGET_FPR, BISECTION_TOL, BISECTION_ITERS)
    logger.info(f"M4 CUSUM calibration on i.i.d. Gaussian: lambda = {lam_c:.6f}, FPR = {fpr_c:.4f}, "
                f"iters = {iters_c}, converged = {ok_c}")

    # ADWIN calibration. The search domain of the submitted script is
    # delta = 10^-x with x in [0.1, 10], i.e. delta <= 0.794, and it is retained
    # unchanged so the threshold stays comparable with the witness. What is NOT
    # retained is its silence: the submitted script assigned `best_delta` on
    # every iteration before testing the tolerance, so a search that never met
    # its target returned the last midpoint tried and reported nothing.
    calib_seeds = [t[0] for t in tasks]
    low_log, high_log = M4_ADWIN_LOG_LOW, M4_ADWIN_LOG_HIGH
    best_delta = 10.0**(-low_log)
    adwin_converged = False
    adwin_trace = []
    for _ in range(M4_ADWIN_ITERS):
        mid_log = (low_log + high_log) / 2.0
        d = 10.0**(-mid_log)
        fps = int(sum(executor.map(_worker_adwin_only,
                                   [(s, STREAM_LENGTH, d) for s in calib_seeds], chunksize=25)))
        fpr = fps / n_streams
        best_delta = d
        adwin_trace.append((d, fpr))
        if abs(fpr - TARGET_FPR) < BISECTION_TOL:
            adwin_converged = True
            break
        if fpr > TARGET_FPR:
            low_log = mid_log
        else:
            high_log = mid_log

    ceiling_delta = 10.0**(-M4_ADWIN_LOG_LOW)
    fps_ceiling = int(sum(executor.map(_worker_adwin_only,
                                       [(s, STREAM_LENGTH, ceiling_delta) for s in calib_seeds],
                                       chunksize=25)))
    fpr_ceiling = fps_ceiling / n_streams
    if not adwin_converged:
        logger.warning(
            f"M4 ADWIN calibration did NOT reach the {TARGET_FPR:.0%} target and terminated at the "
            f"boundary of its search domain. The loosest admissible delta of that domain, "
            f"{ceiling_delta:.6g}, attains only {fpr_ceiling:.6f} on i.i.d. Gaussian streams, so no "
            f"delta in (0, 1) brings this detector to the nominal level over a {STREAM_LENGTH}-step "
            f"horizon. The ADWIN column below is therefore NOT iso-FPR with the CUSUM column: it is "
            f"read at the level this detector can attain, and delta = {best_delta:.6g} is the last "
            f"midpoint the search visited, not a calibrated value. The submitted script ran the same "
            f"search and reported neither the failure nor the ceiling.")
    else:
        logger.info(f"M4 ADWIN calibration converged: delta = {best_delta:.6g}, FPR = {adwin_trace[-1][1]:.4f}")
    for d, f in adwin_trace:
        logger.info(f"  ADWIN search: delta = {d:.6g} -> FPR = {f:.6f}")

    rows = []
    for gamma in GAMMA_GRID:
        omega, beta, sigma_unc = garch_parameters(gamma, ALPHA_GARCH)
        tasks = []
        for i in range(n_streams):
            seed = get_deterministic_seed("R04", "M4", "grid", gamma, i)
            seed_registry.append(seed)
            tasks.append((seed, STREAM_LENGTH, omega, ALPHA_GARCH, beta, NU_RACE, best_delta, "garch"))
        results = list(executor.map(_worker_family, tasks, chunksize=25))
        sup = np.array([r[0] for r in results])
        alarms_cusum = int((sup > lam_c).sum())
        alarms_adwin = int(sum(r[1] for r in results))
        for detector, alarms in (("CUSUM", alarms_cusum), ("ADWIN", alarms_adwin)):
            low, high = wilson_interval(alarms, n_streams)
            rows.append({
                'Gamma': gamma, 'detector': detector, 'alarms': alarms, 'N_streams': n_streams,
                'FPR': alarms / n_streams, 'CI_low': low, 'CI_high': high,
                'threshold': lam_c if detector == "CUSUM" else best_delta,
                'iso_fpr_calibrated': True if detector == "CUSUM" else adwin_converged,
            })
        logger.info(f"M4 Gamma={gamma}: CUSUM FPR={alarms_cusum/n_streams:.4f}, "
                    f"ADWIN FPR={alarms_adwin/n_streams:.4f}")

    # Counterfactual arm, required before any causal attribution.
    # The submitted campaign reports this level as flat in Gamma. This repository
    # measures it as rising, and attributes the difference to the swapped
    # arguments that pinned beta at 0. The attribution is only admissible if the
    # flatness RETURNS when beta is pinned back to 0, so that is measured here:
    # same seeds, same thresholds, same reduction, beta forced to the value the
    # submitted generator actually produced.
    counterfactual = []
    for gamma in GAMMA_GRID:
        beta_legacy = 0.0
        omega_legacy = 1.0 * (1.0 - ALPHA_GARCH - beta_legacy)
        tasks = [(get_deterministic_seed("R04", "M4", "grid", gamma, i), STREAM_LENGTH,
                  omega_legacy, ALPHA_GARCH, beta_legacy, NU_RACE, None, "garch")
                 for i in range(n_streams)]
        sup = np.array([r[0] for r in executor.map(_worker_family, tasks, chunksize=25)])
        counterfactual.append((gamma, float((sup > lam_c).sum()) / n_streams))
    logger.info("M4 counterfactual (beta pinned to 0, as the submitted generator produced it): " +
                ", ".join(f"Gamma={g}: CUSUM FPR={f:.4f}" for g, f in counterfactual) +
                f"; spread = {max(f for _, f in counterfactual) - min(f for _, f in counterfactual):.6f}. "
                "The realised process is identical at all four labels, so a flat level here is an "
                "identity of the degraded generator and not a property of the detector.")

    return pd.DataFrame(rows), fpr_ceiling, counterfactual


# --- REPORTING ---

def format_table_cell(value):
    """
    Printing precision of Table 3 in v87: three significant figures, floored at
    integer precision. Verified against all twelve published cells.
    """
    if not np.isfinite(value):
        return "---"
    decimals = max(0, (TABLE_SIGNIFICANT_FIGURES - 1) - int(math.floor(math.log10(abs(value)))))
    return f"{value:.{decimals}f}"


def build_table3(df_race, path):
    """
    Table 3, generated row by row from the race frame. No cell is hard-coded:
    the body is a projection of R04_isofpr_race.csv at Gamma = 11.58 onto the
    three arms v87 prints, in the order v87 prints them.
    """
    block = df_race[np.isclose(df_race['Gamma'], GAMMA_RACE)]
    columns = ("Recalib", "Eco_L1", "Concept")
    lines = [
        "% Auto-generated by exp_R04_isofpr_race.py -- do not edit.",
        "\\begin{table}[h]",
        "    \\caption{Iso-FPR race under a location drift ($\\Gamma \\approx 11.6$, standardized "
        "Student-$t_{30}$ innovations, all arms calibrated to 5\\% FPR, 2,000 streams). ADD in steps; "
        "DetRate in parentheses when below 1.}",
        "    \\label{tab:isofpr_race}",
        "    \\small",
        "    \\begin{tabular}{lrrr}",
        "        \\toprule",
        "        $c$    & \\textsc{Recalib} ($(\\varepsilon/\\hat\\sigma)^2$) & "
        "\\textsc{Eco-L1} ($\\varepsilon/\\hat\\sigma$) & \\textsc{Concept} (sign) \\\\",
        "        \\midrule",
    ]
    for c in sorted(block['c'].unique()):
        cells = []
        for arm in columns:
            row = block[(block['arm'] == arm) & np.isclose(block['c'], c)].iloc[0]
            cell = f"${format_table_cell(row['ADD_conditional'])}$"
            if row['DetRate'] < 1.0:
                cell += f" \\; $({row['DetRate']:.2f})$"
            cells.append(cell)
        lines.append(f"        ${c:.2f}$ & {cells[0]} & {cells[1]} & {cells[2]} \\\\")
    lines += [
        "        \\bottomrule",
        "    \\end{tabular}",
        "\\end{table}",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def plot_fig04(df_race, df_eff, figures_dir, suffix):
    """Figure 4, drawn from the in-memory frames. No CSV is reloaded."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    block = df_race[np.isclose(df_race['Gamma'], GAMMA_RACE)]
    for arm in ARMS:
        sub = block[block['arm'] == arm].sort_values('c')
        axes[0].plot(sub['c'], sub['ADD_conditional'], marker='o', label=arm.replace("_", "-"))
    axes[0].set_xlabel("Drift magnitude $c$ (unconditional sd)")
    axes[0].set_ylabel("Detection delay (steps)")
    axes[0].set_yscale('log')
    axes[0].legend()
    axes[0].set_title(f"(A) Iso-FPR delay vs. drift magnitude, $\\Gamma \\approx {GAMMA_RACE:.1f}$",
                      fontweight="bold", loc="left")

    eff = df_eff.sort_values('nu')
    axes[1].plot(eff['nu'], eff['ratio'], marker='o', label="Measured, Concept / Eco-L1")
    axes[1].plot(eff['nu'], eff['ratio_oracle'], marker='s', label="Measured, Concept / Oracle-Eco")
    axes[1].plot(eff['nu'], eff['ratio_pred'], linestyle='--', color='crimson',
                 label=r"Predicted $1/(4 f_z(0)^2)$")
    axes[1].axhline(1.0, color='grey', linewidth=0.8, linestyle=':')
    axes[1].set_xlabel(r"Degrees of freedom $\nu$")
    axes[1].set_ylabel(r"$\mathrm{ADD}_{\mathrm{Concept}} / \mathrm{ADD}_{\mathrm{parametric}}$")
    axes[1].legend()
    axes[1].set_title("(B) Relative efficiency vs. tail weight", fontweight="bold", loc="left")

    plt.tight_layout()
    plt.savefig(figures_dir / f"fig04_isofpr_race{suffix}.png", dpi=150)
    plt.close()


def classify_deviation(published, regenerated, decimals):
    """
    Classifies one regenerated value against its witness at the printing
    precision of the manuscript. D3 is never returned here: falsification of a
    qualitative claim is decided by the blocking gates, not by a rounding
    comparison.
    """
    if published == regenerated:
        return "D0"
    if round(float(published), decimals) == round(float(regenerated), decimals):
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
    RESULTS_DIR = BASE_DIR / "results" / "R04_isofpr_race"
    DATA_DIR = RESULTS_DIR / "data"
    FIGURES_DIR = RESULTS_DIR / "figures"
    TABLES_DIR = RESULTS_DIR / "tables"
    LOGS_DIR = BASE_DIR / "logs" / "R04_isofpr_race"
    REFERENCE_DIR = BASE_DIR / "data" / "reference" / "R04"

    for d in (DATA_DIR, FIGURES_DIR, TABLES_DIR, LOGS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(LOGS_DIR / f"exp_R04_isofpr_race{suffix}.log", f"exp_R04_isofpr_race{suffix}")
    if not verify_hash_seed(logger):
        sys.exit(1)
    log_environment(logger, ["numpy", "pandas", "scipy", "matplotlib"])

    n_streams = 40 if args.fast else N_STREAMS_SPEC
    m0_streams = 40 if args.fast else M0_STREAMS

    # (a) Conformity to the v87 specification.
    if args.fast:
        logger.warning(
            "DEGRADED PATH selected by --fast: certification gates are disabled and every artefact "
            f"is stamped '{suffix}'. This path never certifies a manuscript number.")
    else:
        spec = {
            "n_streams": (n_streams, 2000),
            "target_fpr": (TARGET_FPR, 0.05),
            "bisection_tol": (BISECTION_TOL, 0.003),
            "bisection_iters": (BISECTION_ITERS, 15),
            "gamma_grid": (GAMMA_GRID, (1.0, 11.58, 50.0, 200.0)),
            "c_grid": (C_GRID, (0.25, 0.5, 1.0, 2.0)),
            "n_arms": (len(ARMS), 4),
            "stream_length": (STREAM_LENGTH, 5000),
            "warmup": (WARMUP, 500),
            "nu_race": (NU_RACE, 30.0),
        }
        for name, (observed, required) in spec.items():
            if observed != required:
                logger.error(f"Specification mismatch on {name}: {observed} != {required} (v87 sec:magnitude)")
                sys.exit(1)
        logger.info("Specification check (a): all ten protocol constants match v87. "
                    f"N = {n_streams} null streams, target FPR = {TARGET_FPR}, bisection tolerance = "
                    f"{BISECTION_TOL} over {BISECTION_ITERS} iterations, Gamma grid = {GAMMA_GRID}, "
                    f"c grid = {C_GRID}, arms = {ARMS}.")

    logger.info(
        f"Deterministic reduction: ProcessPoolExecutor with max_workers = {args.n_jobs}, executor.map in "
        "submission order, no completion-order reduction, no worker-side logging. Outputs are invariant "
        "to the worker count because every task derives its own 128-bit seed.")
    logger.info(
        "Seeding: 128-bit MD5 condensate of the semantic coordinates of each task, injected as a scalar "
        "integer. Every cell is keyed independently, including across Gamma and across c. Common random "
        "numbers are deliberately NOT used here: the claims under test are invariance claims, and sharing "
        "innovations across Gamma would make the sign stream identical by construction, turning control "
        "(d) into an identity rather than a measurement.")
    logger.info(
        f"Interpolation rule fixed before measurement: nu_star is linear interpolation of the delay ratio "
        f"between the two grid points bracketing unity, on the nu grid as sampled {NU_GRID}, reported with "
        "its bracket and rounded to one decimal for macro emission.")
    logger.info(
        f"QMLE budgets fixed before measurement: stationarity {QMLE_STATIONARITY_BUDGET:.0%} (the guard "
        f"is unreachable once an infeasible pair is projected onto alpha + beta = {QMLE_PERSISTENCE_CAP}), "
        f"non-convergence {QMLE_CONVERGENCE_BUDGET:.1%} (derived from the sampling error of the means it "
        f"protects, not from any observed rate). Multistart ladder: {QMLE_STARTS}.")

    # The Gamma grid is verified rather than assumed. This is a deterministic
    # identity with no probability of firing under any null: beta is solved for a
    # target and the closed form is then evaluated back on the solved pair. It is
    # the check the submitted campaign lacked, and the one that would have caught
    # its swapped-argument defect on the first run.
    # At alpha fixed, beta >= 0 puts a floor under Gamma: the pair (alpha, 0) is
    # an ARCH(1) process, not an i.i.d. one, so the point v87 labels Gamma = 1 is
    # not attainable and lands on that floor. R03 documents the same mislabel at
    # its own floor of 1.174. A target below the floor is therefore expected to
    # clamp; a target above it must be hit exactly.
    gamma_floor = compute_gamma_exact(ALPHA_GARCH, 0.0)
    p_homog = float('nan')
    realised = []
    for gamma in GAMMA_GRID:
        _, beta, _ = garch_parameters(gamma, ALPHA_GARCH)
        realised.append((gamma, beta, compute_gamma_exact(ALPHA_GARCH, beta)))
    logger.info(f"Gamma grid check: at alpha = {ALPHA_GARCH} the attainable floor is "
                f"Gamma(alpha, beta=0) = {gamma_floor:.6f}; " + ", ".join(
                    f"target {g} -> beta = {b:.6f} -> realised {r:.4f}" for g, b, r in realised))
    for g, b, r in realised:
        expected = max(float(g), gamma_floor)
        if abs(r - expected) > 1e-6:
            logger.error(f"Gamma grid is not realised: target {g} solved to beta = {b:.6f}, which the "
                         f"closed form maps back to {r:.6f} instead of {expected:.6f}. The grid does not "
                         "span what it claims -- this is the failure mode of the submitted campaign, "
                         "whose transposed arguments pinned beta at 0 for every target.")
            sys.exit(1)
    logger.info("Gamma grid check: every target above the floor is realised to within 1e-6, so the grid "
                f"genuinely spans Gamma from {max(GAMMA_GRID[0], gamma_floor):.4f} to {GAMMA_GRID[-1]}. "
                f"The point labelled Gamma = 1 in v87 is in fact Gamma = {gamma_floor:.4f}, an ARCH(1) "
                "stream rather than an i.i.d. one.")

    # The memoisation of the bisection's inner evaluation is asserted, not assumed.
    probe = np.random.default_rng(get_deterministic_seed("R04", "equivalence_probe")).standard_normal(STREAM_LENGTH)
    for lam_probe in (2.0, 5.0, 18.0, 40.0):
        by_detector = strict_cusum(probe, DELTA_ECO, lam_probe) != -1
        by_supremum = cusum_running_max(probe, DELTA_ECO) > lam_probe
        if by_detector != by_supremum:
            logger.error(f"cusum_running_max disagrees with strict_cusum at lambda = {lam_probe}. "
                         "The calibration memoisation is invalid and no threshold may be trusted.")
            sys.exit(1)
    logger.info("Equivalence check: sup_t S_t > lambda matches strict_cusum at four probe thresholds, "
                "so the bisection evaluates exactly the false-alarm count the submitted script computed.")

    t0 = time.time()
    seed_registry = []
    with ProcessPoolExecutor(max_workers=args.n_jobs) as executor:
        df_m0 = protocol_m0(m0_streams, executor, logger, seed_registry)
        df_calib, df_race, concept_suprema, q1, tot1 = protocol_m1_m2(n_streams, executor, logger, seed_registry)
        df_eff, q2, tot2 = protocol_m3(n_streams, executor, logger, seed_registry)
        # Counterfactual arm. This repository measures the
        # estimation cost of the parametric route an order of magnitude above the
        # 0.3 degrees of freedom v87 reports, and attributes the gap to the
        # transposed arguments that pinned beta at 0 in the submitted generator.
        # The attribution is only admissible if pinning beta back to 0 RESTORES
        # the published figure, so that is measured here on the same seeds.
        df_eff_cf, _, _ = protocol_m3(n_streams, executor, logger, None,
                                      beta_override=0.0, label=" [counterfactual beta=0]")
        df_family, adwin_ceiling_fpr, m4_counterfactual = protocol_m4(
            n_streams, executor, logger, seed_registry)
    elapsed = time.time() - t0

    # A2: uniqueness of the derived seeds, blocking. The submitted script keyed
    # its streams by arithmetic on the parameters, `20000*int(gamma) + int(c*100)`,
    # which truncates: Gamma = 11.58 and Gamma = 11.99 map to the same key. Its
    # grid escaped collision by luck, not by construction.
    n_seeds, n_unique = len(seed_registry), len(set(seed_registry))
    if n_unique != n_seeds:
        logger.error(f"Seed collision: {n_seeds - n_unique} of {n_seeds} derived seeds are not unique. "
                     "Two cells would share a realisation where the design requires independent entropy.")
        sys.exit(1)
    logger.info(f"Seed uniqueness check (A2): {n_unique} distinct 128-bit seeds over {n_seeds} tasks, "
                "zero collisions.")

    n_unconverged, n_unstationary, n_boundary = (int(v) for v in (q1 + q2))
    qmle_total = tot1 + tot2
    rate_unconverged = n_unconverged / qmle_total if qmle_total else 0.0
    rate_unstationary = n_unstationary / qmle_total if qmle_total else 0.0
    rate_boundary = n_boundary / qmle_total if qmle_total else 0.0
    logger.info(
        f"QMLE non-convergence: {n_unconverged} of {qmle_total} fitted warm-ups ({rate_unconverged:.4%}) "
        f"failed on all {len(QMLE_STARTS)} starts of the multistart ladder and reverted to "
        f"(alpha, beta) = ({QMLE_FALLBACK_ALPHA}, {QMLE_FALLBACK_BETA}); budget "
        f"{QMLE_CONVERGENCE_BUDGET:.1%}.")
    logger.info(
        f"QMLE stationarity guard: {n_unstationary} of {qmle_total} ({rate_unstationary:.4%}); budget "
        f"{QMLE_STATIONARITY_BUDGET:.0%}. The guard is unreachable once an infeasible pair is projected "
        f"back onto alpha + beta = {QMLE_PERSISTENCE_CAP}, so any firing is structural.")
    logger.info(
        f"QMLE constraint boundary: {n_boundary} of {qmle_total} warm-ups ({rate_boundary:.4%}) returned "
        f"alpha + beta >= {QMLE_PERSISTENCE_CAP}, the feasibility boundary of the optimiser. Those fits "
        f"are stationary and are KEPT here. The submitted script guarded on that same predicate and "
        f"reverted every one of them to ({QMLE_FALLBACK_ALPHA}, {QMLE_FALLBACK_BETA}) without counting "
        f"them, substituting a materially different volatility model precisely on the grid points whose "
        f"true alpha + beta lies closest to the boundary.")
    if rate_unstationary > QMLE_STATIONARITY_BUDGET:
        logger.error(f"The stationarity guard fired on {n_unstationary} warm-ups although the projection "
                     "makes it unreachable. This is a structural failure of the fit, not a tolerance to widen.")
        sys.exit(1)
    if rate_unconverged > QMLE_CONVERGENCE_BUDGET:
        logger.error(f"QMLE non-convergence rate {rate_unconverged:.4%} exceeds the budget of "
                     f"{QMLE_CONVERGENCE_BUDGET:.1%} derived from the sampling error of the means it "
                     "protects. The warm-up does not identify the model and Eco_L1 stops measuring what "
                     "it claims to measure.")
        sys.exit(1)

    outputs = {
        f"R04_bernoulli_constant{suffix}.csv": df_m0,
        f"R04_isofpr_calibration{suffix}.csv": df_calib,
        f"R04_isofpr_race{suffix}.csv": df_race,
        f"R04_relative_efficiency{suffix}.csv": df_eff,
        f"R04_cusum_vs_adwin{suffix}.csv": df_family,
    }
    for name, frame in outputs.items():
        save_fair_csv(frame, DATA_DIR / name)

    # (b) Cardinalities.
    cardinalities = {
        "R04_isofpr_calibration": (len(df_calib), len(GAMMA_GRID) * len(ARMS)),
        "R04_isofpr_race": (len(df_race), len(GAMMA_GRID) * len(C_GRID) * len(ARMS)),
        "R04_relative_efficiency": (len(df_eff), len(NU_GRID)),
        "R04_cusum_vs_adwin": (len(df_family), len(GAMMA_GRID) * 2),
    }
    for name, (observed, required) in cardinalities.items():
        if observed != required:
            logger.error(f"Cardinality error on {name}: {observed} rows, expected {required}")
            sys.exit(1)
    logger.info("Cardinality check (b): " + ", ".join(f"{k} = {v[0]}" for k, v in cardinalities.items()))

    # (c) Effective calibration. This gate is in-sample by construction:
    # the bisection selects lambda* on this very null set, so the gate has no
    # probability of firing under a null hypothesis -- it fires if and only if
    # the bisection failed to converge within its 15 iterations. It is a convergence
    # check, not a test.
    off_target = df_calib[(df_calib['FPR_achieved'] - TARGET_FPR).abs() > BISECTION_TOL]
    if not args.fast and len(off_target):
        for row in off_target.itertuples(index=False):
            logger.error(f"Calibration failed at Gamma = {row.Gamma}, arm = {row.arm}: "
                         f"FPR_achieved = {row.FPR_achieved:.6f}, off target by "
                         f"{abs(row.FPR_achieved - TARGET_FPR):.6f} > {BISECTION_TOL}")
        logger.error("The race is not iso-FPR on at least one arm, so no delay comparison in this "
                     "campaign is interpretable. Reporting stops here.")
        sys.exit(1)
    logger.info(f"Calibration check (c): all {len(df_calib)} arms within {BISECTION_TOL} of "
                f"{TARGET_FPR}; achieved rates span "
                f"[{df_calib['FPR_achieved'].min():.4f}, {df_calib['FPR_achieved'].max():.4f}].")

    # (d) Gamma-invariance of the Concept arm.
    #
    # Two statements are kept apart here. The BAND is reported and does not gate;
    # the EQUALITY OF LEVELS at a common threshold gates.
    #
    # The bisection halves [0.001, 1000] a fixed number of times, so lambda_star
    # can only land on a lattice of step 1000/2^k. At the depth this campaign
    # reaches that step is about 0.122, and the published band [10.6, 10.7] is
    # narrower than one lattice cell while the admissible band [10.5, 10.8] spans
    # barely two. A gate on band containment therefore tests which cell the
    # empirical 95th percentile of 2000 streams happens to fall into, and fires
    # with substantial probability under its own null -- precisely the binary door
    # the protocol forbids.
    #
    # What Proposition prop:whitening actually asserts is stronger and lattice-free:
    # the sign stream is i.i.d. Bernoulli(1/2) EXACTLY, for every Gamma, so the
    # null law of the CUSUM built on it does not depend on Gamma at all. Read at
    # one common threshold, the four false-alarm counts are then four draws from
    # one binomial, which a homogeneity test addresses directly.
    concept = df_calib[df_calib['arm'] == "Concept"]
    lam_min, lam_max = concept['lambda_star'].min(), concept['lambda_star'].max()
    lattice_step = (1000.0 - 0.001) / (2.0 ** concept['n_bisection_iter'].max())
    logger.info(f"Concept threshold check (d): lambda_C* in [{lam_min:.6f}, {lam_max:.6f}] over "
                f"Gamma in {GAMMA_GRID}, spanning {(lam_max - lam_min) / lattice_step:.1f} bisection "
                f"lattice steps of {lattice_step:.6f}; v87 prints [10.6, 10.7], narrower than one step. "
                f"Reported, not gated.")
    if not (CONCEPT_LAMBDA_BAND[0] <= lam_min and lam_max <= CONCEPT_LAMBDA_BAND[1]):
        logger.warning(
            f"Concept threshold (d): the span [{lam_min:.6f}, {lam_max:.6f}] leaves the admissible band "
            f"{CONCEPT_LAMBDA_BAND} by {max(CONCEPT_LAMBDA_BAND[0] - lam_min, lam_max - CONCEPT_LAMBDA_BAND[1]):.6f}, "
            f"less than one lattice step. This is the resolution of the calibration, not a movement of "
            f"the threshold -- non-blocking; the homogeneity test below carries the claim.")

    if not args.fast and concept_suprema:
        common_lambda = float(concept[np.isclose(concept['Gamma'], GAMMA_RACE)]['lambda_star'].iloc[0])
        counts = [(g, int((concept_suprema[g] > common_lambda).sum()), len(concept_suprema[g]))
                  for g in GAMMA_GRID]
        table = np.array([[k, n - k] for _, k, n in counts])
        chi2, p_homog, _, _ = stats.chi2_contingency(table)
        logger.info(
            f"Concept invariance check (d): at the common threshold lambda = {common_lambda:.6f}, "
            "false-alarm counts across the Gamma grid are " +
            ", ".join(f"Gamma={g}: {k}/{n}" for g, k, n in counts) +
            f"; chi-square homogeneity = {chi2:.4f}, p = {p_homog:.4f}. Under prop:whitening the four "
            "counts are draws from one binomial, so this tests the theorem rather than a lattice cell.")
        if p_homog <= 0.01:
            logger.error(
                f"The Concept false-alarm rate is not homogeneous across Gamma (p = {p_homog:.4f}): the "
                "sign stream would not be Bernoulli(1/2) independently of the volatility dynamics, which "
                "falsifies Proposition prop:whitening on this campaign (D3).")
            sys.exit(1)

    # (e) The blind zone of Recalib is a property of the expansion order, not of Gamma.
    blind = df_race[(df_race['arm'] == "Recalib") & (df_race['c'] < BLIND_ZONE_C_CUT)]
    logger.info("Blind-zone check (e): Recalib detection rate below c = "
                f"{BLIND_ZONE_C_CUT} at each Gamma: " +
                ", ".join(f"Gamma={r.Gamma}: {r.DetRate:.4f}" for r in blind.itertuples(index=False)))
    blind_at_one = blind[np.isclose(blind['Gamma'], 1.0)]
    if not args.fast and (blind_at_one['DetRate'] >= 1.0).any():
        logger.error("The Recalib collapse does not occur at Gamma = 1, so the blind zone would be a "
                     "GARCH effect rather than an order-of-response effect. v87 states the opposite (D3).")
        sys.exit(1)
    if not args.fast:
        logger.info(f"Blind-zone check (e): the collapse is present at Gamma = 1 "
                    f"(DetRate = {blind_at_one['DetRate'].iloc[0]:.4f}), so it is not a GARCH effect.")

    # (f) Monotonicity of the efficiency ratio in nu. Structural, and more robust
    # than the individual ratios: the Pitman constant 1/(4 f_z(0)^2) is strictly
    # increasing in nu, so any inversion is a defect and not sampling noise.
    eff_sorted = df_eff.sort_values('nu')
    diffs = eff_sorted['ratio'].diff().dropna()
    rho, rho_p = stats.spearmanr(eff_sorted['nu'], eff_sorted['ratio'])
    logger.info(f"Monotonicity check (f): {len(diffs)} consecutive differences of the ratio in nu, "
                f"most negative = {diffs.min():+.6f}, Spearman rho = {rho:.4f} (p = {rho_p:.3e}).")
    if not args.fast and (diffs < 0).any():
        logger.error("The efficiency ratio is not monotone increasing in nu, contradicting the shape of "
                     "1/(4 f_z(0)^2) that v87 reports the measurement to follow (D3).")
        sys.exit(1)

    # (g) Family control: the level of each detector across the Gamma grid.
    #
    # Reported with a verdict, and NOT blocking. The control as specified asks
    # both levels to stay flat in Gamma. On the submitted campaign they do, but
    # that campaign solved beta with its arguments transposed and therefore ran
    # every grid point at one and the same process: flatness there is an identity
    # of the generator, not a measurement of the detector. Blocking on it would
    # make reproducing that defect the only way to emit an artefact, which is the
    # mirror image of adjusting a tolerance until a control passes. The
    # counterfactual below establishes the attribution rather than asserting it.
    for detector in ("CUSUM", "ADWIN"):
        sub = df_family[df_family['detector'] == detector]
        spread = sub['FPR'].max() - sub['FPR'].min()
        logger.info(f"Family check (g): {detector} FPR over the Gamma grid = "
                    f"{[round(v, 6) for v in sub['FPR']]}, spread = {spread:.6f}")
    cf_spread = max(f for _, f in m4_counterfactual) - min(f for _, f in m4_counterfactual)
    cusum_spread = df_family[df_family['detector'] == "CUSUM"]['FPR'].max() - \
        df_family[df_family['detector'] == "CUSUM"]['FPR'].min()
    logger.warning(
        f"Family check (g) VERDICT: on a Gamma grid that is genuinely spanned, the level of a CUSUM "
        f"monitoring the RAW return stream is not flat -- spread {cusum_spread:.6f} against "
        f"{cf_spread:.6f} for the same seeds and threshold with beta pinned to 0. Uncorrelatedness of "
        f"the returns fixes the variance of their partial sums at n*sigma^2 for every Gamma, but the "
        f"supremum of a CUSUM recursion is driven by the worst volatility cluster rather than by the "
        f"aggregate variance, and clustering is exactly what Gamma measures. No theorem of v87 protects "
        f"this arm: Proposition prop:whitening protects the SIGN stream, whose invariance control (d) "
        f"measures separately and which holds. This is reported as a deviation, not reconciled.")

    # (h) Embedded certification of the numbers v87 prints.
    block = df_race[np.isclose(df_race['Gamma'], GAMMA_RACE)]
    recalib = block[block['arm'] == "Recalib"].set_index('c')['ADD_conditional']
    slowdowns = []
    for arm in FIRST_ORDER_ARMS:
        other = block[block['arm'] == arm].set_index('c')['ADD_conditional']
        for c in C_GRID:
            slowdowns.append(recalib[c] / other[c])
    slowdown_min, slowdown_max = min(slowdowns), max(slowdowns)

    kappa_z = 3.0 * (NU_RACE - 2.0) / (NU_RACE - 4.0)
    c_star = math.sqrt(DELTA_R * math.sqrt(kappa_z - 1.0))
    nu_star, nu_lo, nu_hi = crossing_point(df_eff['nu'], df_eff['ratio'])
    nu_star_oracle, nu_lo_o, nu_hi_o = crossing_point(df_eff['nu'], df_eff['ratio_oracle'])
    nu_star_analytic = brentq(lambda v: standardised_t_density_at_zero(v) - 0.5, 3.0, 20.0)
    estimation_cost = nu_star - nu_star_oracle
    eco_at_one = block[(block['arm'] == "Eco_L1") & np.isclose(block['c'], C_REFERENCE)]['ADD_conditional'].iloc[0]
    concept_at_one = block[(block['arm'] == "Concept") & np.isclose(block['c'], C_REFERENCE)]['ADD_conditional'].iloc[0]
    parametric_gain = concept_at_one / eco_at_one

    slowdown_finite = np.isfinite(slowdown_min) and np.isfinite(slowdown_max)
    logger.info(f"Certification (h): Recalib slowdown over the two first-order arms spans "
                f"[{slowdown_min:.4f}, {slowdown_max:.4f}] -> rounded "
                f"[{round(slowdown_min) if slowdown_finite else 'NaN'}, "
                f"{round(slowdown_max) if slowdown_finite else 'NaN'}]; v87 prints {SLOWDOWN_PUBLISHED}.")
    if not args.fast and not slowdown_finite:
        logger.error("The Recalib slowdown is undefined: at least one cell of the Gamma = 11.58 block "
                     "produced no detection at all, so Table 3 cannot be filled (D3).")
        sys.exit(1)
    logger.info(f"Certification (h): dead band delta_R = {DELTA_R}, kappa_z(t_{NU_RACE:.0f}) = {kappa_z:.6f}, "
                f"c* = sqrt(delta_R * sqrt(kappa_z - 1)) = {c_star:.6f}; v87 prints 0.43.")
    logger.info(f"Certification (h): nu* (Eco-L1) = {nu_star:.4f}, bracketed by nu = {nu_lo} "
                f"(ratio {df_eff.set_index('nu')['ratio'].get(nu_lo, float('nan')):.6f}) and nu = {nu_hi} "
                f"(ratio {df_eff.set_index('nu')['ratio'].get(nu_hi, float('nan')):.6f}); v87 prints "
                f"{NU_STAR_PUBLISHED}.")
    logger.info(f"Certification (h): nu* (Oracle) = {nu_star_oracle:.4f}, bracketed by nu = {nu_lo_o} "
                f"(ratio {df_eff.set_index('nu')['ratio_oracle'].get(nu_lo_o, float('nan')):.6f}) and nu = "
                f"{nu_hi_o} (ratio {df_eff.set_index('nu')['ratio_oracle'].get(nu_hi_o, float('nan')):.6f}); "
                f"v87 prints {NU_STAR_ORACLE_PUBLISHED}.")
    logger.info(f"Certification (h): analytic crossing f_z(0) = 1/2 at nu = {nu_star_analytic:.6f}; "
                f"v87 prints {NU_STAR_ANALYTIC_PUBLISHED}. Estimation cost = nu*(Eco-L1) - nu*(Oracle) = "
                f"{estimation_cost:.4f}; v87 prints 0.3.")
    logger.info(f"Certification (h): parametric gain at c = {C_REFERENCE} under t_{NU_RACE:.0f} = "
                f"{parametric_gain:.6f}; v87 prints 1.66.")

    nu_star_cf, _, _ = crossing_point(df_eff_cf['nu'], df_eff_cf['ratio'])
    nu_star_oracle_cf, _, _ = crossing_point(df_eff_cf['nu'], df_eff_cf['ratio_oracle'])
    cost_cf = nu_star_cf - nu_star_oracle_cf
    logger.info(
        f"Counterfactual on the efficiency crossing: with beta pinned to 0, as the submitted "
        f"generator produced it, and the same seeds, nu*(Eco-L1) = {nu_star_cf:.4f}, "
        f"nu*(Oracle) = {nu_star_oracle_cf:.4f}, estimation cost = {cost_cf:.4f}. On the genuinely "
        f"spanned grid the same quantities are {nu_star:.4f}, {nu_star_oracle:.4f} and "
        f"{estimation_cost:.4f}. v87 prints 4.9, 4.6 and 0.3. The published figures are recovered by "
        f"the degraded generator and not by the specified one, which locates the discrepancy in the "
        f"transposed arguments of solve_beta_for_gamma rather than in any parameter of this "
        f"reimplementation.")
    logger.info(f"Certification (h): maximum measured ratio = {df_eff['ratio'].max():.6f} against the "
                f"Gaussian ceiling pi/2 = {GAUSSIAN_CEILING:.6f}.")

    if not args.fast:
        if not math.isfinite(nu_star) or not math.isfinite(nu_star_oracle):
            logger.error("The efficiency ratio does not cross unity on the sampled nu grid, so neither "
                         "crossing point of v87 exists on this campaign (D3).")
            sys.exit(1)
        if df_eff['ratio'].max() > GAUSSIAN_CEILING:
            logger.error(f"The measured ratio {df_eff['ratio'].max():.6f} exceeds the Gaussian ceiling "
                         f"pi/2 = {GAUSSIAN_CEILING:.6f}, which Proposition prop:are forbids (D3).")
            sys.exit(1)

    # D0-D3 classification against the vendored witness of the submitted campaign.
    witness_paths = {
        "calibration": REFERENCE_DIR / "protocol_9b_isofpr_calibration.csv",
        "race": REFERENCE_DIR / "protocol_9c_isofpr_race.csv",
        "efficiency": REFERENCE_DIR / "protocol_9d_relative_efficiency.csv",
        "family": REFERENCE_DIR / "protocol_9e_cusum_vs_adwin_L1.csv",
        "bernoulli": REFERENCE_DIR / "protocol_9a_bernoulli_constant.csv",
    }
    missing = [str(p) for p in witness_paths.values() if not p.exists()]
    if missing:
        logger.error(f"Historical witness missing: {missing}. Deviation classification cannot be computed.")
        sys.exit(1)
    w = {k: pd.read_csv(p, float_precision='round_trip') for k, p in witness_paths.items()}
    w_race = w['race'][np.isclose(w['race']['Gamma'], GAMMA_RACE)]
    w_eff = w['efficiency']

    comparisons = []
    for c in C_GRID:
        for arm, label in (("Recalib", "Recalib"), ("Eco_L1", "Eco-L1"), ("Concept", "Concept")):
            pub = w_race[(w_race['arm'] == arm) & np.isclose(w_race['c'], c)]['ADD'].iloc[0]
            reg = block[(block['arm'] == arm) & np.isclose(block['c'], c)]['ADD_conditional'].iloc[0]
            dec = max(0, (TABLE_SIGNIFICANT_FIGURES - 1) - int(math.floor(math.log10(abs(pub)))))
            comparisons.append((f"Table 3 ADD {label} at c = {c}", pub, reg, dec,
                               f"protocol_9c[ADD] Gamma=11.58 arm={arm} c={c}"))
    for c in (0.25, 0.5):
        pub = w_race[(w_race['arm'] == "Recalib") & np.isclose(w_race['c'], c)]['DetRate'].iloc[0]
        reg = block[(block['arm'] == "Recalib") & np.isclose(block['c'], c)]['DetRate'].iloc[0]
        comparisons.append((f"Table 3 DetRate Recalib at c = {c}", pub, reg, 2,
                           f"protocol_9c[DetRate] Gamma=11.58 arm=Recalib c={c}"))
    for nu in NU_GRID:
        pub = w_eff[np.isclose(w_eff['nu'], nu)]['ratio'].iloc[0]
        reg = df_eff[np.isclose(df_eff['nu'], nu)]['ratio'].iloc[0]
        comparisons.append((f"Efficiency ratio at nu = {nu}", pub, reg, 6, f"protocol_9d[ratio] nu={nu}"))
    w_concept = w['calibration'][w['calibration']['arm'] == "Concept"]
    comparisons += [
        ("Concept lambda* minimum over Gamma", w_concept['lambda_star'].min(), lam_min, 1,
         "protocol_9b[lambda_star] arm=Concept"),
        ("Concept lambda* maximum over Gamma", w_concept['lambda_star'].max(), lam_max, 1,
         "protocol_9b[lambda_star] arm=Concept"),
        ("M0 constant-threshold FPR", w['bernoulli']['FPR'].iloc[0],
         df_m0[df_m0['source'] == "garch"]['FPR'].iloc[0], 3, "protocol_9a[FPR]"),
    ]
    for detector in ("CUSUM", "ADWIN"):
        pub = w['family'][w['family']['detector'] == detector]['FPR'].mean()
        reg = df_family[df_family['detector'] == detector]['FPR'].mean()
        comparisons.append((f"Family control {detector} mean FPR", pub, reg, 3,
                           f"protocol_9e[FPR] detector={detector}, 4-point mean"))

    if args.fast:
        logger.warning("Deviation classification withheld on the degraded path: forty streams compared "
                       "against a two-thousand-stream witness would yield degrees describing the sample "
                       "size, not a deviation.")
    else:
        logger.info("Deviation classification against the submitted campaign, at the printing precision "
                    "of v87 (read with float_precision='round_trip' on both sides):")
        logger.info(f"{'quantity':<38} | {'published':>12} | {'regenerated':>12} | {'degree':>6} | source cell")
        for label, pub, reg, dec, cell in comparisons:
            logger.info(f"{label:<38} | {float(pub):>12.6f} | {float(reg):>12.6f} | "
                        f"{classify_deviation(float(pub), float(reg), dec):>6} | {cell}")

    # Qualitative register. classify_deviation above ranks numerals; this block
    # ranks the CLAIMS those numerals support, which is where D3 is decided.
    if not args.fast:
        adwin_mean = df_family[df_family['detector'] == "ADWIN"]['FPR'].mean()
        cusum_mean = df_family[df_family['detector'] == "CUSUM"]['FPR'].mean()
        # Each row carries two predicates, kept apart deliberately. `numeric` asks
        # whether the printed value is reproduced at its printing precision;
        # `qualitative` asks whether the assertion the value supports still holds.
        # Numeric false with qualitative true is D2, the ordinary consequence of a
        # changed draw. Both false is D3, a falsified claim.
        verdicts = [
            ("Recalib runs 2 to 19x behind the first-order arms", "2 to 19x",
             f"{round(slowdown_min)} to {round(slowdown_max)}x",
             SLOWDOWN_PUBLISHED[0] <= round(slowdown_min) and round(slowdown_max) <= SLOWDOWN_PUBLISHED[1],
             # The stated interval is the claim: v87 quantifies the mismatch by it.
             SLOWDOWN_PUBLISHED[0] <= round(slowdown_min) and round(slowdown_max) <= SLOWDOWN_PUBLISHED[1]),
            ("Recalib blind zone persists even at the lowest Gamma", "collapse present",
             f"DetRate {blind_at_one['DetRate'].iloc[0]:.4f} at Gamma = {gamma_floor:.4f}",
             bool((blind_at_one['DetRate'] < 1.0).all()), bool((blind_at_one['DetRate'] < 1.0).all())),
            ("efficiency ratio crosses unity at nu* ~ 4.9", f"{NU_STAR_PUBLISHED}",
             f"{nu_star:.2f}", round(nu_star, 1) == NU_STAR_PUBLISHED,
             # v87 places the crossing inside the moment singularity, nu < 8, where
             # E[eps^8] diverges. A crossing above that window falsifies the reading,
             # not merely the numeral.
             nu_star < 8.0),
            ("oracle arm crosses unity at 4.6", f"{NU_STAR_ORACLE_PUBLISHED}",
             f"{nu_star_oracle:.2f}", round(nu_star_oracle, 1) == NU_STAR_ORACLE_PUBLISHED,
             # The claim is that the oracle sits ON the analytic prediction, which
             # is a statement about the gap to nu_star_analytic, not about 4.6.
             abs(nu_star_oracle - nu_star_analytic) < 0.5),
            ("finite warm-up costs 0.3 degrees of freedom", "0.3",
             f"{estimation_cost:.2f}", round(estimation_cost, 1) == 0.3,
             # "0.3" is the quantity itself; an order of magnitude is not a redraw.
             round(estimation_cost, 1) == 0.3),
            ("parametric route is 1.66x faster at c = 1", "1.66x",
             f"{parametric_gain:.2f}x", round(parametric_gain, 2) == 1.66,
             # The assertion is a bounded constant above unity, not the numeral.
             1.0 < parametric_gain <= GAUSSIAN_CEILING),
            ("ratio never exceeds the Gaussian ceiling pi/2", f"<= {GAUSSIAN_CEILING:.4f}",
             f"max {df_eff['ratio'].max():.4f}", bool(df_eff['ratio'].max() <= GAUSSIAN_CEILING),
             bool(df_eff['ratio'].max() <= GAUSSIAN_CEILING)),
            ("ratio is monotone increasing in nu", "monotone",
             f"min diff {diffs.min():+.4f}", bool((diffs >= 0).all()), bool((diffs >= 0).all())),
            ("Concept threshold is flat in Gamma", "[10.6, 10.7]",
             f"[{lam_min:.2f}, {lam_max:.2f}], homogeneity p = {p_homog:.3f}",
             bool(CONCEPT_LAMBDA_BAND[0] <= lam_min and lam_max <= CONCEPT_LAMBDA_BAND[1]),
             bool(p_homog > 0.01)),
            ("blind-zone onset c* ~ 0.43", "0.43", f"{c_star:.4f}",
             round(c_star, 2) == 0.43, round(c_star, 2) == 0.43),
            ("family control: both levels flat in Gamma", "CUSUM ~0.05, ADWIN ~0.006 flat",
             f"CUSUM {cusum_mean:.4f} spread {cusum_spread:.4f}, ADWIN {adwin_mean:.4f}", False, False),
        ]
        logger.info("Qualitative register. CONFIRMED means the printed value is reproduced at its "
                    "printing precision; D2 means the value moved while the assertion it supports still "
                    "holds; D3 means the assertion itself is falsified. No parameter, tolerance, seed or "
                    "bound was moved to change any line of this table.")
        logger.info(f"{'claim of v87':<52} | {'published':<28} | {'regenerated':<44} | verdict")
        for claim, published, regenerated, numeric_ok, qualitative_ok in verdicts:
            degree = "CONFIRMED" if numeric_ok else ("D2" if qualitative_ok else "D3 FALSIFIED")
            logger.info(f"{claim:<52} | {published:<28} | {regenerated:<44} | {degree}")
        n_d3 = sum(1 for *_, q in verdicts if not q)
        logger.warning(
            f"{n_d3} of {len(verdicts)} qualitative claims of v87 are falsified on a Gamma grid that is "
            f"genuinely spanned. The counterfactual arms above reproduce the published figures when beta "
            f"is pinned to 0, which is what the submitted generator produced, so the manuscript is "
            f"impacted and the discrepancy is not a property of this reimplementation.")

    plot_fig04(df_race, df_eff, FIGURES_DIR, suffix)
    build_table3(df_race, TABLES_DIR / f"tab03_isofpr_race{suffix}.tex")

    # Macros. Every value is computed from the in-memory objects; none is hard-coded.
    macros = [
        "% Auto-generated by exp_R04_isofpr_race.py -- do not edit.",
        f"\\newcommand{{\\RFourNullStreams}}{{{n_streams}}}",
        f"\\newcommand{{\\RFourBisectionIters}}{{{BISECTION_ITERS}}}",
        f"\\newcommand{{\\RFourBisectionTol}}{{{BISECTION_TOL}}}",
        f"\\newcommand{{\\RFourTargetFpr}}{{{TARGET_FPR*100:.0f}\\%}}",
        f"\\newcommand{{\\RFourGammaRace}}{{{GAMMA_RACE:.2f}}}",
        f"\\newcommand{{\\RFourStreamLength}}{{{STREAM_LENGTH}}}",
        f"\\newcommand{{\\RFourWarmup}}{{{WARMUP}}}",
        f"\\newcommand{{\\RFourRecalibSlowdownMin}}{{{round(slowdown_min) if slowdown_finite else 0}}}",
        f"\\newcommand{{\\RFourRecalibSlowdownMax}}{{{round(slowdown_max) if slowdown_finite else 0}}}",
        f"\\newcommand{{\\RFourDeadBand}}{{{DELTA_R}}}",
        f"\\newcommand{{\\RFourKappaZ}}{{{kappa_z:.3f}}}",
        f"\\newcommand{{\\RFourBlindZoneCStar}}{{{c_star:.2f}}}",
        f"\\newcommand{{\\RFourParametricGainAtCOne}}{{{parametric_gain:.2f}$\\times$}}",
        f"\\newcommand{{\\RFourNuStarMeasured}}{{{nu_star:.1f}}}",
        f"\\newcommand{{\\RFourNuStarLower}}{{{nu_lo:.1f}}}",
        f"\\newcommand{{\\RFourNuStarUpper}}{{{nu_hi:.1f}}}",
        f"\\newcommand{{\\RFourNuStarOracle}}{{{nu_star_oracle:.1f}}}",
        f"\\newcommand{{\\RFourNuStarOracleLower}}{{{nu_lo_o:.1f}}}",
        f"\\newcommand{{\\RFourNuStarOracleUpper}}{{{nu_hi_o:.1f}}}",
        f"\\newcommand{{\\RFourNuStarAnalytic}}{{{nu_star_analytic:.1f}}}",
        f"\\newcommand{{\\RFourEstimationCostDof}}{{{estimation_cost:.1f}}}",
        f"\\newcommand{{\\RFourConceptLambdaMin}}{{{lam_min:.1f}}}",
        f"\\newcommand{{\\RFourConceptLambdaMax}}{{{lam_max:.1f}}}",
        f"\\newcommand{{\\RFourGaussianCeiling}}{{{GAUSSIAN_CEILING:.2f}}}",
        f"\\newcommand{{\\RFourRatioMax}}{{{df_eff['ratio'].max():.2f}}}",
        f"\\newcommand{{\\RFourConstantThresholdFpr}}{{{df_m0[df_m0['source'] == 'garch']['FPR'].iloc[0]*100:.1f}\\%}}",
        f"\\newcommand{{\\RFourBernoulliFpr}}{{{df_m0[df_m0['source'] == 'bernoulli_iid']['FPR'].iloc[0]*100:.1f}\\%}}",
        f"\\newcommand{{\\RFourFamilyCusumFpr}}{{{df_family[df_family['detector'] == 'CUSUM']['FPR'].mean()*100:.1f}\\%}}",
        f"\\newcommand{{\\RFourFamilyAdwinFpr}}{{{df_family[df_family['detector'] == 'ADWIN']['FPR'].mean()*100:.1f}\\%}}",
        # The level the ADWIN arm can actually attain over this horizon within the
        # admissible domain of its confidence parameter. Not persisted anywhere
        # else, and the reason that arm is not iso-FPR with the CUSUM column.
        f"\\newcommand{{\\RFourAdwinAttainableFpr}}{{{adwin_ceiling_fpr*100:.1f}\\%}}",
    ]
    tex_name = f"R04_claims{suffix}.tex"
    with open(TABLES_DIR / tex_name, "w") as f:
        f.write("\n".join(macros) + "\n")

    # (i) Traceability of every artefact.
    for name in outputs:
        logger.info(f"SHA-256 {name} : {compute_sha256(DATA_DIR / name)}")
    for rel, path in ((f"fig04_isofpr_race{suffix}.png", FIGURES_DIR / f"fig04_isofpr_race{suffix}.png"),
                      (f"tab03_isofpr_race{suffix}.tex", TABLES_DIR / f"tab03_isofpr_race{suffix}.tex"),
                      (tex_name, TABLES_DIR / tex_name)):
        logger.info(f"SHA-256 {rel} : {compute_sha256(path)}")

    # Artifact manifest
    artifact_paths = [DATA_DIR / name for name in outputs]
    artifact_paths.extend([
        FIGURES_DIR / f"fig04_isofpr_race{suffix}.png",
        TABLES_DIR / f"tab03_isofpr_race{suffix}.tex",
        TABLES_DIR / tex_name,
    ])
    log_artifact_manifest(logger, artifact_paths, RESULTS_DIR, BASE_DIR)

    logger.info(f"Execution completed in {elapsed:.1f}s with {args.n_jobs} workers. v87 reports about "
                f"25 min for this race on 24 cores; the ratio is {1500.0/max(elapsed, 1e-9):.1f}x.")


if __name__ == "__main__":
    main()
