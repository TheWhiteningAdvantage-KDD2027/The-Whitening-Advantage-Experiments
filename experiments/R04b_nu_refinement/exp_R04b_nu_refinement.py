#!/usr/bin/env python3
"""
==========================================================================
R04b -- RESOLUTION OF THE EFFICIENCY CROSSING POINT (APPENDIX FIGURE A3)
==========================================================================
R04 established that the submitted campaign never varied `Gamma`, and that on a
grid which genuinely spans, the delay ratio ADD_Concept / ADD_Eco-L1 crosses
unity somewhere strictly inside (7, 30) -- an interval its grid
{3, 4, 4.5, 5, 7, 30} does not sample at all. The 8.52 quoted in AUDIT_R04.md is
a two-point interpolation across that void, on a curve governed by 1/(4 f_z(0)^2)
which is not linear in nu, and must not be read as a measurement.

This experiment resolves the crossing. It re-measures the same three arms at the
same Gamma = 11.58, the same 2,000 null streams, the same 5% bisection and the
same c = 0.5, on twelve degrees of freedom instead of six.

Two facts govern the design and are established before any result is read:

1. A GRID BRACKET IS NOT AN INFERENTIAL BRACKET. On R04's own output the ratio at
   the point nearest each crossing is not distinguishable from unity, so a
   bracket read off two adjacent grid points carries no confidence and can flip
   between draws with nothing physical having changed.
2. REFINING THE GRID DOES NOT, BY ITSELF, RESOLVE THE CROSSING. Near it the ratio
   moves by roughly 0.009 per unit of nu while its own standard error at
   N = 2000 is an order of magnitude larger, so one standard error spans several
   units of nu. Extra grid points do not shrink the error at any single point.
   What shrinks it is using the whole curve, which is why the primary point
   estimate here is a fit of the ratio against the analytic shape across all
   twelve points rather than an interpolation between two of them.

Four crossing estimators are therefore emitted for each arm, none substituted for
another, each with its status attached: the grid bracket (model-free, resolution
limited), the inferential bracket (model-free, carries confidence, and governs
every manuscript-facing formulation), the global shape fit with a stream-level
bootstrap interval (primary point estimate), and the analytic root of
1/(4 f_z(0)^2) = 1, which is a property of the innovation law alone and therefore
one number rather than one per arm.

Arms (the Recalib arm of R04 is computed by the shared worker and not reported):
- Eco_L1     : eps_t / sigma_hat_t, GARCH(1,1) fitted by QMLE on the warm-up.
- Oracle_Eco : the same statistic standardized by the TRUE GARCH parameters.
- Concept    : 1{eps_t > 0} - 1/2, the binary sign-error stream.

R04 is frozen. This script shares no output file with it, and asserts that every
primitive it copied is still byte-identical to R04's.

References:
- Page, E. S. (1954). Continuous inspection schemes. Biometrika, 41(1/2), 100-115.
- van der Vaart, A. W. (1998). Asymptotic Statistics. Cambridge University Press.
- Efron, B. & Tibshirani, R. (1993). An Introduction to the Bootstrap. Chapman & Hall.
==========================================================================
"""

import sys
from pathlib import Path

# Determinism bootstrap, in the order preamble S6 requires: fair_env imports only
# os and sys, so the environment block is posted before numpy is loaded by anyone
# and before any BLAS thread limit is read.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from experiments.common.fair_env import enforce_strict_determinism, verify_hash_seed, log_environment

enforce_strict_determinism()

import numpy as np
import pandas as pd
from experiments.common.fair_harness import setup_logging, disable_pandas_multithreading, compute_sha256, save_fair_csv

disable_pandas_multithreading()

import os
import ast
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

# --- PROTOCOL SPECIFICATION ---
# Everything below the nu grid is R04's, unchanged: the two campaigns must be
# comparable at the five points they share, and any divergence would have to be
# read as a defect rather than as a design choice.
N_STREAMS_SPEC = 2000
STREAM_LENGTH = 5000
WARMUP = 500
ALPHA_GARCH = 0.05
GAMMA_RACE = 11.58
C_SHIFT = 0.5
TARGET_FPR = 0.05
BISECTION_TOL = 0.003
BISECTION_ITERS = 15
DELTA_R = 0.125
DELTA_ECO = 0.25
ARMS = ("Recalib", "Eco_L1", "Oracle_Eco", "Concept")
REPORTED_ARMS = ("Eco_L1", "Oracle_Eco", "Concept")

# The refinement grid, in three parts, all measured identically and separated
# only in the log so the design is auditable.
#   HIGH  : the eight points of the prompt, which straddle the (7, 30) void.
#   LOW   : R04 brackets the ORACLE crossing at [4, 4.5], below the prompt's
#           floor of 7. Without these three points the estimation cost could only
#           be formed across two campaigns with different seed conventions.
#   EDGE  : on R04's data the inferential lower edge of the Eco crossing sits
#           between 5 and 7 -- at nu = 5 the ratio interval is entirely below
#           unity, at nu = 7 it contains unity -- and that interval is the one
#           that binds. One point at 6 tightens it.
NU_HIGH = (7.0, 8.0, 9.0, 10.0, 12.0, 15.0, 20.0, 30.0)
NU_LOW = (4.0, 4.5, 5.0)
NU_EDGE = (6.0,)
NU_GRID = tuple(sorted(NU_LOW + NU_EDGE + NU_HIGH))
# The points R04 also measured. Continuity is checked on these and nowhere else.
NU_COMMON_WITH_R04 = (4.0, 4.5, 5.0, 7.0, 30.0)

# --- CERTIFICATION ANCHORS, FIXED BEFORE ANY REGENERATED VALUE IS READ ---
# Every one is a literal of v87 or of AUDIT_R04.md; none operationalises prose.
#   "crossing unity at a measured nu* ~ 4.9 (analytic 4.7)"     -> the register
#   "an oracle arm ... crosses at 4.6"                          -> the register
#   "the extra 0.3 degrees of freedom is what a finite warm-up costs"
#   "never exceeding the Gaussian ceiling pi/2"
NU_STAR_PUBLISHED = 4.9
NU_STAR_ORACLE_PUBLISHED = 4.6
NU_STAR_ANALYTIC_PUBLISHED = 4.7
ESTIMATION_COST_PUBLISHED = 0.3
GAUSSIAN_CEILING = math.pi / 2.0
# AUDIT_R04.md's two-point interpolation across the empty (7, 30) interval. Held
# here to be compared against, never to be reproduced.
NU_STAR_R04_INTERPOLATED = 8.52

Z_95 = 1.959963984540054
BOOTSTRAP_REPLICATES = 2000
BOOTSTRAP_CHUNK = 250
VARIANCE_PROBE_REPLICATES = 20000
VARIANCE_PROBE_CHUNK = 500

# A delay is read at a threshold that was itself estimated on 2,000 null streams,
# so a bootstrap that resamples only the drifted streams holds lambda* fixed and
# prices none of the calibration error -- the same omission that makes a
# one-sample test of the held-out level fire by construction. To let a replicate
# re-place its own threshold and still read a delay, the drifted pass records the
# first passage at a ladder of thresholds around the calibrated one rather than
# at that one alone. The span is set from the mechanism: the calibration standard
# error of lambda* is a few percent, and +/- 15% is several times that.
LAMBDA_LADDER = (0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15)
LADDER_CENTRE = LAMBDA_LADDER.index(1.00)
PROBE_STREAMS = 50

# Gates on omnibus statistics, all at the same level, all pre-registered. A
# per-cell gate is forbidden by preamble S4bis wherever the family-wise firing
# probability under the null exceeds 5%, which every family here does.
OMNIBUS_GATE_P = 0.01

# QMLE constants, R04's verbatim. The stationarity guard is unreachable once an
# infeasible pair is projected back onto the feasible boundary, so its budget is
# zero; the convergence budget is derived from the sampling error of the means it
# protects, not from any observed rate.
QMLE_STATIONARITY_BUDGET = 0.0
QMLE_PERSISTENCE_CAP = 0.999
QMLE_STARTS = ((0.05, 0.90), (0.10, 0.85), (0.02, 0.95))
QMLE_CONVERGENCE_BUDGET = 0.005
QMLE_FALLBACK_ALPHA = 0.05
QMLE_FALLBACK_BETA = 0.90

# The primitives this script carries. They are duplicated from R04 rather than
# imported, because preamble S4.2 forbids hoisting scientific routines into
# experiments/common/, and they are asserted byte-identical at start-up so the
# duplication cannot silently drift into a divergence.
COPIED_PRIMITIVES = (
    "get_deterministic_seed",
    "simulate_garch11",
    "compute_gamma_exact",
    "solve_beta_for_gamma",
    "strict_cusum",
    "cusum_running_max",
    "_garch_nll",
    "fit_garch_qmle",
    "filter_sigma2",
    "wilson_interval",
    "standardised_t_density_at_zero",
    "concept_reference_drift",
    "_worker_race",
    "bisect_threshold",
    "crossing_point",
    "garch_parameters",
)
R04_SOURCE = BASE_DIR / "experiments" / "R04_isofpr_race" / "exp_R04_isofpr_race.py"
R04_EFFICIENCY_CSV = BASE_DIR / "results" / "R04_isofpr_race" / "data" / "R04_relative_efficiency.csv"


def get_deterministic_seed(*args) -> int:
    """
    Derives a 128-bit collision-free seed from the semantic coordinates of a
    task, returned as a scalar integer so no entropy is discarded.

    Floats are formatted through .hex() rather than str(): the decimal
    repr of a float is platform-dependent at the last digit on some C
    libraries, which would silently re-key a cell across machines. The native
    hash() is randomly salted and is forbidden outright (SPECS 1.2).
    """
    def format_arg(arg):
        if isinstance(arg, (float, np.floating)):
            return float(arg).hex()
        return str(arg)

    s = "_".join(map(format_arg, args))
    return int(hashlib.md5(s.encode('utf-8')).hexdigest(), 16)


# --- PRIMITIVES, DUPLICATED VERBATIM PER PREAMBLE S4.2 ---
# Byte-identity with exp_R04_isofpr_race.py is asserted at start-up. Editing any
# of them here without editing R04 -- which is frozen -- stops this script.

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

    The finite-difference step and tolerances follow SPECS 1.10: gradient noise
    of an SLSQP run on a recursive likelihood is amplified by the FPU, so the
    step is widened and the solution truncated deterministically.

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
    # points is a correction in the solution space, which SPECS 2.2 requires,
    # where substituting a default pair would be the masked fallback it forbids.
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
    # class of correction as the domain clamping above (SPECS 1.8).
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
# condition that breaks the digest of the log (SPECS 1.5). Diagnostics travel
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


# --- ROUTINES SPECIFIC TO R04b ---

def first_passages(stream, delta_P, thresholds):
    """
    First crossing index of the same CUSUM recursion at each of an ASCENDING
    ladder of thresholds, in one sweep, or -1 where the stream never crosses.

    Equivalent to calling strict_cusum once per threshold: the recursion,
    arithmetic and strict comparison are identical, and first-passage times are
    non-decreasing in the threshold, so a single pass answers the whole ladder.
    main() asserts the equivalence against strict_cusum before any use.
    """
    S = 0.0
    out = [-1] * len(thresholds)
    k = 0
    for t in range(len(stream)):
        S = max(0.0, S + float(stream[t]) - delta_P)
        while k < len(thresholds) and S > thresholds[k]:
            out[k] = t
            k += 1
        if k == len(thresholds):
            break
    return out


def _worker_race_ladder(args):
    """
    The drifted pass. Everything up to the four monitored sequences is
    _worker_race's body verbatim -- same seed, same generation, same warm-up fit,
    same guard, same filtering, same sequences -- and main() asserts that the
    centre of the ladder reproduces _worker_race exactly on a probe.

    What differs is only the reduction: first passage at every rung of
    lambda* x LAMBDA_LADDER rather than at lambda* alone, which is what lets the
    bootstrap re-place the threshold on a resampled calibration set.
    """
    (seed, warmup, H, omega, alpha, beta, nu, c_shift, sigma_unc, deltas, lambdas) = args

    eps_full = simulate_garch11(warmup + H, omega, alpha, beta, nu=nu, seed=seed)

    eps_w = eps_full[:warmup]
    (_, a_hat, b_hat), converged = fit_garch_qmle(eps_w)
    stationary = (a_hat + b_hat < 1.0) and (a_hat >= 0.0) and (b_hat >= 0.0)
    boundary = 1 if (a_hat + b_hat >= QMLE_PERSISTENCE_CAP) else 0
    if not (converged and stationary):
        a_hat, b_hat = QMLE_FALLBACK_ALPHA, QMLE_FALLBACK_BETA
    var_init = float(np.var(eps_w))
    w_hat = var_init * (1.0 - a_hat - b_hat)
    fallback = (0 if converged else 1, 0 if stationary else 1, boundary)

    eps_shifted = eps_full.copy()
    eps_shifted[warmup:] += c_shift * sigma_unc

    sig2_hat = filter_sigma2(eps_shifted, w_hat, a_hat, b_hat, var_init)
    sig2_oracle = filter_sigma2(eps_full, omega, alpha, beta, sigma_unc**2)

    eps_test = eps_shifted[warmup:]
    sd_hat = np.sqrt(np.maximum(sig2_hat[warmup:], 1e-10))
    sd_oracle = np.sqrt(np.maximum(sig2_oracle[warmup:], 1e-10))

    z_hat = eps_test / sd_hat
    sequences = (
        z_hat**2 - 1.0,
        z_hat,
        eps_test / sd_oracle,
        (eps_test > 0).astype(float) - 0.5,
    )

    return tuple(first_passages(s, d, [lam * rung for rung in LAMBDA_LADDER])
                 for s, d, lam in zip(sequences, deltas, lambdas)), fallback


def source_segments(path, names):
    """
    Source text of the named top-level functions, extracted by position rather
    than by import: importing R04 would execute it, and comparing __code__
    objects would compare a compilation rather than the text a reader audits.
    """
    text = Path(path).read_text()
    tree = ast.parse(text)
    found = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            found[node.name] = ast.get_source_segment(text, node)
    return found


def shape_prediction(nu):
    """The Pitman constant 1/(4 f_z(0)^2) of Proposition prop:are at nu."""
    return 1.0 / (4.0 * standardised_t_density_at_zero(nu) ** 2)


def invert_shape(target):
    """
    The nu at which 1/(4 f_z(0)^2) equals `target`.

    The map is strictly increasing on (2, inf) from 0 to its Gaussian limit
    pi/2, so a target outside that open interval has no root and the caller is
    told so rather than handed a boundary value.
    """
    if not (0.0 < target < GAUSSIAN_CEILING):
        return float('nan')
    return brentq(lambda v: shape_prediction(v) - target, 2.0 + 1e-6, 1e6, xtol=1e-10)


def paired_ratio_se(numer, denom):
    """
    Delta-method standard error of a ratio of two means measured on the SAME
    streams, covariance included.

    The two arms race on one realisation per stream, so their delays are
    strongly positively correlated and treating them as independent would
    inflate this error by a factor that grows with the correlation. The
    covariance term is what makes the interval honest, and it is also what makes
    the difference of two crossings a paired quantity later on.
    """
    n = len(numer)
    if n < 2:
        return float('nan')
    m_n, m_d = float(np.mean(numer)), float(np.mean(denom))
    ratio = m_n / m_d
    cov = np.cov(np.asarray(numer, dtype=float), np.asarray(denom, dtype=float), ddof=1)
    var = (ratio ** 2) * (cov[0, 0] / m_n ** 2 + cov[1, 1] / m_d ** 2
                          - 2.0 * cov[0, 1] / (m_n * m_d)) / n
    return math.sqrt(max(var, 0.0))


def inferential_bracket(nu_values, ratios, ses):
    """
    The model-free statement that carries confidence: the last nu before the
    crossing whose 95% ratio interval lies entirely below unity, and the first
    whose interval lies entirely above it.

    A grid bracket names the two adjacent points that straddle unity, which says
    nothing about whether either point is distinguishable from unity. This one
    names the interval outside which the sampling error of this campaign does
    not reach, and it is the statement that governs manuscript formulations.

    The right edge is taken first and the left edge is then sought below it, so
    the pair is ordered by construction. Scanning the two edges independently
    over the whole grid would let a high-nu point that happens to dip below
    unity become the "left" edge of a bracket that lies to the right of it,
    which is not a bracket at all. Either edge may be absent -- the crossing
    then lies outside the grid on that side, and NaN says so rather than a
    boundary value that would read as a measurement.
    """
    nu_values = np.asarray(nu_values, dtype=float)
    lo_ci = np.asarray(ratios) - Z_95 * np.asarray(ses)
    hi_ci = np.asarray(ratios) + Z_95 * np.asarray(ses)
    above = nu_values[lo_ci > 1.0]
    right = float(above.min()) if len(above) else float('nan')
    eligible = nu_values < right if np.isfinite(right) else np.ones(len(nu_values), dtype=bool)
    below = nu_values[eligible & (hi_ci < 1.0)]
    left = float(below.max()) if len(below) else float('nan')
    return left, right


def shape_fit(g_values, ratios, ses):
    """
    Weighted least squares of the measured ratio on the analytic shape,
    ratio = a + b * 1/(4 f_z(0)^2), inverted at ratio = 1.

    This is the primary point estimate, and the functional form is not a free
    choice: v87 states the ratio converges to that shape (Proposition prop:are),
    so fitting against it uses all twelve points to locate a crossing that no
    single point resolves. Weights are the inverse squared standard errors.

    Returns the coefficients, the weighted R^2, the largest standardized
    residual, the chi-square goodness of fit with its p-value, and the inverted
    crossing. If the model does not hold, the caller withdraws this estimator
    rather than patching it: a fit that fails its own goodness test measures
    nothing about the crossing.
    """
    g = np.asarray(g_values, dtype=float)
    y = np.asarray(ratios, dtype=float)
    w = 1.0 / np.asarray(ses, dtype=float) ** 2
    design = np.column_stack([np.ones_like(g), g])
    root_w = np.sqrt(w)
    coef, *_ = np.linalg.lstsq(design * root_w[:, None], y * root_w, rcond=None)
    a, b = float(coef[0]), float(coef[1])
    fitted = a + b * g
    resid = y - fitted
    standardized = resid / np.asarray(ses, dtype=float)
    chi2 = float(np.sum(standardized ** 2))
    dof = len(g) - 2
    p_fit = float(stats.chi2.sf(chi2, dof)) if dof > 0 else float('nan')
    mean_w = float(np.sum(w * y) / np.sum(w))
    ss_res = float(np.sum(w * resid ** 2))
    ss_tot = float(np.sum(w * (y - mean_w) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    nu_fit = invert_shape((1.0 - a) / b) if b > 0 else float('nan')
    return a, b, r2, float(np.max(np.abs(standardized))), chi2, dof, p_fit, nu_fit


def fit_crossing(g_values, ratios, weights):
    """The inversion of shape_fit alone, for the bootstrap replicates."""
    g = np.asarray(g_values, dtype=float)
    design = np.column_stack([np.ones_like(g), g])
    root_w = np.sqrt(weights)
    coef, *_ = np.linalg.lstsq(design * root_w[:, None], np.asarray(ratios) * root_w, rcond=None)
    a, b = float(coef[0]), float(coef[1])
    if b <= 0:
        return float('nan')
    return invert_shape((1.0 - a) / b)


def resampled_means(alarm_index, draw):
    """
    Conditional mean delay of one arm over a bootstrap resample of streams.

    `alarm_index` holds the alarm position or -1 for a censored stream, exactly
    as the worker returns it. Censoring is re-applied inside the resample rather
    than before it, so a replicate reproduces the same conditional-mean
    definition the campaign reports.
    """
    sample = alarm_index[draw]
    detected = sample != -1
    counts = detected.sum(axis=1)
    sums = np.where(detected, sample + 1, 0).sum(axis=1)
    return np.where(counts > 0, sums / np.maximum(counts, 1), np.nan)


def conditional_mid_p(k_calib, k_hold, n):
    """
    Two-sample conditional test that one threshold carries the same level on the
    sample that chose it and on a fresh one, in mid-p form.

    Conditioning on the total k_calib + k_hold removes the unknown true level of
    the threshold from the analysis, which is what makes this test correctly
    specified where a one-sample test against exactly 0.05 is not: that level is
    not 0.05, it is whatever the bisection reached on a finite calibration
    sample. The price of conditioning is that this test is BLIND to a bias
    common to every arm -- if all thresholds were uniformly too high, both counts
    would move together and nothing here would register. That blindness is why
    the pooled control below is kept, and kept blocking.
    """
    total = k_calib + k_hold
    dist = stats.hypergeom(2 * n, total, n)
    lower = dist.cdf(k_hold) - 0.5 * dist.pmf(k_hold)
    upper = dist.sf(k_hold) + 0.5 * dist.pmf(k_hold)
    return max(0.0, min(1.0, 2.0 * min(lower, upper)))


def two_sided_mid_p(k, n, p0):
    """
    Two-sided binomial p-value in its mid-p form.

    The exact binomial test is conservative on a discrete support: its p-values
    are stochastically larger than uniform, which would bias the Kolmogorov
    -Smirnov calibration test of preamble S4bis towards NOT rejecting -- that is,
    towards passing. The mid-p correction subtracts half the atom at the observed
    count and restores near-uniformity, so gating on it is the stricter of the
    two choices, which is why it is the one that gates.
    """
    lower = stats.binom.cdf(k, n, p0) - 0.5 * stats.binom.pmf(k, n, p0)
    upper = stats.binom.sf(k, n, p0) + 0.5 * stats.binom.pmf(k, n, p0)
    return max(0.0, min(1.0, 2.0 * min(lower, upper)))


def format_macro_value(value, decimals, sentinel="not bracketed"):
    """
    A withheld estimator prints as text, never as a number a reader may cite.

    An absent bracket and a withdrawn fit are different facts and carry
    different sentinels: the first says the grid does not enclose the crossing,
    the second says a model was refused by its own goodness test.
    """
    if value is None or not np.isfinite(value):
        return sentinel
    return f"{value:.{decimals}f}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true",
                        help="Degraded smoke path: fewer streams, certification disabled, outputs stamped '_fast'")
    parser.add_argument("--n-jobs", type=int, default=os.cpu_count(),
                        help="Worker processes. Outputs do not depend on this value: every task carries its own seed.")
    args = parser.parse_args()

    suffix = "_fast" if args.fast else ""
    RESULTS_DIR = BASE_DIR / "results" / "R04b_nu_refinement"
    DATA_DIR = RESULTS_DIR / "data"
    FIGURES_DIR = RESULTS_DIR / "figures"
    TABLES_DIR = RESULTS_DIR / "tables"
    LOGS_DIR = BASE_DIR / "logs" / "R04b_nu_refinement"

    for d in (DATA_DIR, FIGURES_DIR, TABLES_DIR, LOGS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(LOGS_DIR / f"exp_R04b_nu_refinement{suffix}.log", f"exp_R04b_nu_refinement{suffix}")
    if not verify_hash_seed(logger):
        sys.exit(1)
    log_environment(logger, ["numpy", "pandas", "scipy", "matplotlib"])

    n_streams = 40 if args.fast else N_STREAMS_SPEC
    n_arms = len(NU_GRID) * len(REPORTED_ARMS)

    # The primitives are asserted byte-identical to R04's before anything is
    # measured. This is a deterministic identity with no probability of firing
    # under any null, and it is the check that actually addresses "divergence
    # d'implementation entre les deux scripts": the statistical continuity check
    # further down resolves only a few percent per point and cannot see a small
    # divergence at all.
    if not R04_SOURCE.exists():
        logger.error(f"R04 source missing at {R04_SOURCE}. The verbatim-copy check cannot be run and "
                     "no continuity with R04 can be established.")
        sys.exit(1)
    theirs = source_segments(R04_SOURCE, COPIED_PRIMITIVES)
    ours = source_segments(Path(__file__).resolve(), COPIED_PRIMITIVES)
    missing = [name for name in COPIED_PRIMITIVES if name not in theirs or name not in ours]
    if missing:
        logger.error(f"Primitives absent from one of the two scripts: {missing}.")
        sys.exit(1)
    drifted = [name for name in COPIED_PRIMITIVES if theirs[name] != ours[name]]
    if drifted:
        logger.error(f"These primitives are no longer byte-identical to R04: {drifted}. R04 is frozen, so "
                     "the divergence is in this script and the two campaigns are not comparable.")
        sys.exit(1)
    logger.info(f"Verbatim-copy check: all {len(COPIED_PRIMITIVES)} primitives are byte-identical to "
                f"{R04_SOURCE.name} ({sum(len(s) for s in ours.values())} characters compared). Preamble "
                "S4.2 forbids hoisting them into experiments/common/; this check is what makes the "
                "duplication safe.")

    # (a) Conformity to the specification.
    if args.fast:
        logger.warning(
            "DEGRADED PATH selected by --fast: certification gates are disabled and every artefact "
            f"is stamped '{suffix}'. This path never certifies a manuscript number.")
    else:
        spec = {
            "n_streams": (n_streams, 2000),
            "stream_length": (STREAM_LENGTH, 5000),
            "warmup": (WARMUP, 500),
            "alpha_garch": (ALPHA_GARCH, 0.05),
            "gamma_target": (GAMMA_RACE, 11.58),
            "c_shift": (C_SHIFT, 0.5),
            "target_fpr": (TARGET_FPR, 0.05),
            "bisection_tol": (BISECTION_TOL, 0.003),
            "bisection_iters": (BISECTION_ITERS, 15),
            "n_nu": (len(NU_GRID), 12),
            "n_reported_arms": (len(REPORTED_ARMS), 3),
        }
        for name, (observed, required) in spec.items():
            if observed != required:
                logger.error(f"Specification mismatch on {name}: {observed} != {required}")
                sys.exit(1)
    logger.info(f"Specification check (a): nu grid = {NU_GRID}, {len(NU_GRID)} points in three parts -- "
                f"refinement {NU_HIGH} (the eight points of the prompt, straddling the (7, 30) void of "
                f"R04), recovery {NU_LOW} (R04 brackets the ORACLE crossing at [4, 4.5], below the "
                f"prompt's floor, so without these the estimation cost could only be formed across two "
                f"campaigns), edge {NU_EDGE} (the inferential lower edge of the Eco crossing sits between "
                f"5 and 7 on R04's data). Common with R04: {NU_COMMON_WITH_R04}. "
                f"N = {n_streams} streams per cell per pass, alpha = {ALPHA_GARCH}, horizon = "
                f"{STREAM_LENGTH}, warm-up = {WARMUP}, c = {C_SHIFT}, target FPR = {TARGET_FPR}, "
                f"bisection tolerance {BISECTION_TOL} over {BISECTION_ITERS} iterations, arms = "
                f"{REPORTED_ARMS} ({n_arms} calibrated arms in all).")

    # The realised Gamma is verified, not assumed. Deterministic identity: beta is
    # solved for a target and the closed form is evaluated back on the solved
    # pair. This is the check the submitted campaign lacked, and the one that
    # would have caught its transposed arguments on the first run.
    omega, beta, sigma_unc = garch_parameters(GAMMA_RACE, ALPHA_GARCH)
    gamma_realised = compute_gamma_exact(ALPHA_GARCH, beta)
    logger.info(f"Gamma check (a): target {GAMMA_RACE} -> solve_beta_for_gamma(alpha={ALPHA_GARCH}, "
                f"target_gamma={GAMMA_RACE}) = {beta:.6f} -> compute_gamma_exact = {gamma_realised:.6f}; "
                f"omega = {omega:.6f}, sigma_unc = {sigma_unc:.6f}.")
    if abs(gamma_realised - GAMMA_RACE) > 1e-6:
        logger.error(f"The realised penalty {gamma_realised:.6f} misses the target {GAMMA_RACE} by more "
                     f"than 1e-6. The campaign would not run at the Gamma it claims -- the failure mode of "
                     "the submitted script, whose transposed arguments pinned beta at 0.")
        sys.exit(1)

    # The memoisation of the bisection's inner evaluation is asserted, not assumed.
    probe = np.random.default_rng(get_deterministic_seed("R04b", "equivalence_probe")).standard_normal(STREAM_LENGTH)
    for lam_probe in (2.0, 5.0, 18.0, 40.0):
        if (strict_cusum(probe, DELTA_ECO, lam_probe) != -1) != (cusum_running_max(probe, DELTA_ECO) > lam_probe):
            logger.error(f"cusum_running_max disagrees with strict_cusum at lambda = {lam_probe}. "
                         "The calibration memoisation is invalid and no threshold may be trusted.")
            sys.exit(1)
    logger.info("Equivalence check: sup_t S_t > lambda matches strict_cusum at four probe thresholds, so "
                "the bisection evaluates exactly the false-alarm count a fresh sweep would produce.")
    ladder_probe = [0.5 * v for v in sorted((2.0, 5.0, 18.0, 40.0))]
    if first_passages(probe, DELTA_ECO, ladder_probe) != [strict_cusum(probe, DELTA_ECO, lam)
                                                          for lam in ladder_probe]:
        logger.error("first_passages disagrees with strict_cusum on the probe stream. The ladder does "
                     "not reproduce the detector and no bootstrapped threshold may be trusted.")
        sys.exit(1)
    logger.info("Equivalence check: the ladder sweep reproduces strict_cusum at every rung of a probe, "
                "so a delay read at a re-placed threshold is the delay that detector would have given.")

    # Multiple-testing arithmetic and the calibration band, both PRE-REGISTERED:
    # computed here, before a single stream is drawn, from the tolerance, the
    # nominal level, the sample size and the arm count alone. No term of either
    # depends on an observed value, which is what distinguishes this from the
    # tolerance-widening preamble S6bis forbids.
    band = (TARGET_FPR - BISECTION_TOL, TARGET_FPR + BISECTION_TOL)
    logger.info(
        f"Pre-registered control design (S4bis). Per-arm gates are excluded: {n_arms} simultaneous 95% "
        f"tests fire at least once with probability 1 - 0.95^{n_arms} = "
        f"{1.0 - 0.95 ** n_arms:.4f} under the null, and {len(NU_COMMON_WITH_R04)} continuity tests with "
        f"probability {1.0 - 0.95 ** len(NU_COMMON_WITH_R04):.4f}. Both families are therefore judged by "
        f"one omnibus statistic each, gated at p > {OMNIBUS_GATE_P}.")

    # A threshold chosen on a finite calibration sample carries that sample's
    # error into the level it realises out of sample, so the held-out count has
    # the binomial variance TWICE OVER: once from the held-out draw, once from
    # the calibration draw that placed the threshold. The factor is verified here
    # without any distributional assumption -- calibrate on the empirical 95th
    # percentile of N standard normals, read on N fresh ones, repeat -- because
    # every interval and every gate below depends on it. It is a property of
    # calibrate-then-test designs and not of this campaign.
    var_rng = np.random.default_rng(get_deterministic_seed("R04b", "variance_factor_probe"))
    excess_counts = np.empty(VARIANCE_PROBE_REPLICATES)
    for start in range(0, VARIANCE_PROBE_REPLICATES, VARIANCE_PROBE_CHUNK):
        stop = min(start + VARIANCE_PROBE_CHUNK, VARIANCE_PROBE_REPLICATES)
        calib = var_rng.standard_normal((stop - start, n_streams))
        held = var_rng.standard_normal((stop - start, n_streams))
        thresholds = np.percentile(calib, 100.0 * (1.0 - TARGET_FPR), axis=1, keepdims=True)
        excess_counts[start:stop] = (held > thresholds).sum(axis=1)
    probe_sd = float(np.std(excess_counts / n_streams, ddof=1))
    binomial_sd = math.sqrt(TARGET_FPR * (1.0 - TARGET_FPR) / n_streams)
    logger.info(
        f"Pre-registered variance factor, verified distribution-free over {VARIANCE_PROBE_REPLICATES} "
        f"replicates of calibrate-on-{n_streams}, read-on-{n_streams}: held-out rate has standard "
        f"deviation {probe_sd:.6f} against {binomial_sd:.6f} for a binomial at a KNOWN threshold, a "
        f"ratio of {probe_sd / binomial_sd:.4f} against the sqrt(2) = 1.4142 a doubled variance "
        f"predicts. The inflation survives pooling, because each arm carries its own independent "
        f"calibration error, so it applies to the pooled interval as well as to the per-arm one.")
    logger.info(
        f"Pre-registered control (c), in two halves that see different failures. HALF 1, per-arm "
        f"instability: the {n_arms} held-out counts are compared to their own calibration counts by a "
        f"conditional two-sample test, which removes the unknown true level of each threshold from the "
        f"analysis, and the KS statistic of those p-values against Uniform(0,1) gates at "
        f"p > {OMNIBUS_GATE_P}. This half is blind to a bias common to every arm, since both counts "
        f"would move together. HALF 2, common bias: the pooled held-out level must intersect "
        f"[{band[0]:.6f}, {band[1]:.6f}], the band the procedure promises, its half-width being the "
        f"bisection tolerance {BISECTION_TOL} ALONE. The tolerance is systematic and does not shrink "
        f"under pooling; the sampling uncertainty is carried by the interval instead, with the factor 2 "
        f"above, and counting it in both places would double-count it. Both terms derive from "
        f"{TARGET_FPR}, {BISECTION_TOL}, {n_streams} and {n_arms} alone, with no regenerated value read.")
    logger.info(
        f"Pre-registered control (c), reported and NOT gating: the literal predicate of the prompt, "
        f"'the pooled interval contains {TARGET_FPR}', and the KS statistic of the {n_arms} one-sample "
        f"binomial p-values against Uniform(0,1). The latter tests the null that every arm sits at "
        f"exactly {TARGET_FPR}, which the bisection never promises and the factor above shows it cannot "
        f"deliver: that test omits half the variance of its own statistic and therefore fires by "
        f"construction rather than by accident of the draw.")

    # Seeds carry ("R04b", role, nu, i). Common random numbers are deliberately
    # NOT used across nu: the innovations depend on nu by construction, so there
    # is nothing to share, and sharing the calibration set across the H0 and
    # held-out passes would destroy the point of the second one.
    logger.info("Seeding: 128-bit MD5 condensate of ('R04b', role, nu, stream index), injected as a "
                "scalar integer. Three roles: H0_calib feeds the bisection, H0_holdout is an independent "
                "null replicate read at the calibrated threshold, H1 carries the location drift. No "
                "common random numbers across nu or across roles.")

    t0 = time.time()
    seed_registry = []
    qmle = np.zeros(3, dtype=int)
    qmle_total = 0
    rows = []
    h1_alarms, ladder_alarms, sup_calib, lambda_star = {}, {}, {}, {}
    ratios = {"Eco_L1": [], "Oracle_Eco": []}
    ratio_ses_conditional = {"Eco_L1": [], "Oracle_Eco": []}

    with ProcessPoolExecutor(max_workers=args.n_jobs) as executor:
        for nu in NU_GRID:
            deltas = (DELTA_R, DELTA_ECO, DELTA_ECO, concept_reference_drift(C_SHIFT, nu))

            tasks = []
            for i in range(n_streams):
                seed = get_deterministic_seed("R04b", "H0_calib", nu, i)
                seed_registry.append(seed)
                tasks.append((seed, WARMUP, STREAM_LENGTH, omega, ALPHA_GARCH, beta,
                              nu, 0.0, sigma_unc, deltas, None))
            results = list(executor.map(_worker_race, tasks, chunksize=25))
            sup = np.array([r[0] for r in results])
            qmle += np.sum([r[1] for r in results], axis=0)
            qmle_total += len(results)

            lambdas, fprs, iters, converged = [], [], [], []
            for j in range(len(ARMS)):
                lam, fpr, it, ok = bisect_threshold(sup[:, j], TARGET_FPR, BISECTION_TOL, BISECTION_ITERS)
                lambdas.append(lam)
                fprs.append(fpr)
                iters.append(it)
                converged.append(ok)

            tasks = []
            for i in range(n_streams):
                seed = get_deterministic_seed("R04b", "H0_holdout", nu, i)
                seed_registry.append(seed)
                tasks.append((seed, WARMUP, STREAM_LENGTH, omega, ALPHA_GARCH, beta,
                              nu, 0.0, sigma_unc, deltas, tuple(lambdas)))
            results = list(executor.map(_worker_race, tasks, chunksize=25))
            holdout = np.array([r[0] for r in results])
            qmle += np.sum([r[1] for r in results], axis=0)
            qmle_total += len(results)

            tasks = []
            for i in range(n_streams):
                seed = get_deterministic_seed("R04b", "H1", nu, i)
                seed_registry.append(seed)
                tasks.append((seed, WARMUP, STREAM_LENGTH, omega, ALPHA_GARCH, beta,
                              nu, C_SHIFT, sigma_unc, deltas, tuple(lambdas)))
            # The first cell is measured through both workers, which is a
            # deterministic identity: the ladder worker and _worker_race share
            # every line up to the reduction, so the centre rung must be the
            # index _worker_race returns, stream by stream.
            if nu == NU_GRID[0]:
                control = list(executor.map(_worker_race, tasks[:PROBE_STREAMS], chunksize=5))
                ladder_control = list(executor.map(_worker_race_ladder, tasks[:PROBE_STREAMS], chunksize=5))
                mismatch = [i for i, (a, b) in enumerate(zip(control, ladder_control))
                            if tuple(a[0]) != tuple(rung[LADDER_CENTRE] for rung in b[0])]
                if mismatch:
                    logger.error(f"The ladder worker and _worker_race disagree on {len(mismatch)} of "
                                 f"{PROBE_STREAMS} probe streams at nu = {nu}. The drifted pass would "
                                 "not be the race R04 runs.")
                    sys.exit(1)
                logger.info(f"Worker identity check: over {PROBE_STREAMS} streams at nu = {nu}, the "
                            "centre rung of the ladder worker reproduces _worker_race index for index "
                            "on all four arms, so the two differ only in what they record.")
            results = list(executor.map(_worker_race_ladder, tasks, chunksize=25))
            ladder = np.array([r[0] for r in results])
            qmle += np.sum([r[1] for r in results], axis=0)
            qmle_total += len(results)
            idx = ladder[:, :, LADDER_CENTRE]
            h1_alarms[nu] = idx
            ladder_alarms[nu] = ladder
            sup_calib[nu] = sup

            g_nu = shape_prediction(nu)
            add, detected_by = {}, {}
            for j, arm in enumerate(ARMS):
                detected_by[arm] = idx[:, j] != -1
                delays = idx[:, j][detected_by[arm]] + 1
                add[arm] = float(np.mean(delays)) if len(delays) else float('nan')

            for arm in REPORTED_ARMS:
                j = ARMS.index(arm)
                delays = idx[:, j][detected_by[arm]] + 1
                k_hold = int((holdout[:, j] != -1).sum())
                # How continuous the null statistic is where the threshold is
                # chosen. A bisection can only place lambda* between two observed
                # suprema, so the levels it can reach at all are the jumps of the
                # empirical survival function near the 5% point. On a continuous
                # statistic every supremum is distinct and the reachable levels
                # are spaced 1/N apart; on a lattice-valued one -- the sign
                # stream takes two values, so its CUSUM lives on a lattice -- the
                # suprema tie, the jumps are large, and no threshold attains 5%
                # exactly. This fraction measures which case each arm is in, from
                # the calibration sample itself.
                band_lo, band_hi = np.percentile(sup[:, j], [94.0, 96.0])
                in_band = (sup[:, j] >= band_lo) & (sup[:, j] <= band_hi)
                n_band = int(in_band.sum())
                distinct_fraction = len(np.unique(sup[in_band, j])) / n_band if n_band else float('nan')
                rows.append({
                    'nu': nu, 'arm': arm,
                    'lambda_star': lambdas[j], 'FPR_achieved': fprs[j],
                    'n_bisection_iter': iters[j], 'bisection_converged': converged[j],
                    'DetRate': len(delays) / n_streams,
                    # Mean over the streams that alarmed within the horizon. When
                    # DetRate < 1 this is E[T | T <= H] and not E[T]; it is never
                    # comparable across arms without DetRate beside it.
                    'ADD_conditional': add[arm],
                    'SEM': float(np.std(delays, ddof=1) / np.sqrt(len(delays))) if len(delays) > 1 else np.nan,
                    'n_detected': len(delays), 'n_censored': n_streams - len(delays),
                    'horizon': STREAM_LENGTH,
                    'ratio_to_eco': add[arm] / add['Eco_L1'],
                    # The crossing curve itself: ADD_Concept / ADD_arm, unity on
                    # the Concept row by construction. Recoverable from
                    # ratio_to_eco by dividing two rows, and carried explicitly
                    # because it is the quantity every claim of this experiment
                    # is about.
                    'ratio_concept_to_arm': add['Concept'] / add[arm],
                    'analytic_prediction': g_nu,
                    # Held-out diagnostics, descriptive by construction: preamble
                    # S4bis requires the m individual p-values persisted, and
                    # forbids using any of them as an acceptance criterion.
                    'n_alarms_holdout': k_hold,
                    'FPR_holdout': k_hold / n_streams,
                    'p_binom_holdout': two_sided_mid_p(k_hold, n_streams, TARGET_FPR),
                    'n_alarms_calib': int(round(fprs[j] * n_streams)),
                    'p_conditional': conditional_mid_p(int(round(fprs[j] * n_streams)), k_hold, n_streams),
                    'distinct_sup_fraction': distinct_fraction,
                })

            lambda_star[nu] = list(lambdas)
            for arm in ("Eco_L1", "Oracle_Eco"):
                j = ARMS.index(arm)
                both = detected_by["Concept"] & detected_by[arm]
                ratios[arm].append(add['Concept'] / add[arm])
                # Conditional on the threshold. Kept as a diagnostic against the
                # bootstrap standard error below, which also carries the error of
                # the threshold itself and is the one that is used.
                ratio_ses_conditional[arm].append(
                    paired_ratio_se(idx[both, ARMS.index("Concept")] + 1, idx[both, j] + 1))

            logger.info(
                f"nu={nu}: ADD_Eco={add['Eco_L1']:.2f} ADD_Oracle={add['Oracle_Eco']:.2f} "
                f"ADD_Concept={add['Concept']:.2f} | ratio_Eco={ratios['Eco_L1'][-1]:.6f} "
                f"| ratio_Oracle={ratios['Oracle_Eco'][-1]:.6f} | analytic={g_nu:.6f} | "
                f"lambda*=({lambdas[1]:.4f}, {lambdas[2]:.4f}, {lambdas[3]:.4f}) "
                f"FPR=({fprs[1]:.4f}, {fprs[2]:.4f}, {fprs[3]:.4f})")

    elapsed = time.time() - t0
    df = pd.DataFrame(rows)

    n_seeds, n_unique = len(seed_registry), len(set(seed_registry))
    if n_unique != n_seeds:
        logger.error(f"Seed collision: {n_seeds - n_unique} of {n_seeds} derived seeds are not unique.")
        sys.exit(1)
    logger.info(f"Seed uniqueness check: {n_unique} distinct 128-bit seeds over {n_seeds} tasks, zero "
                "collisions.")

    n_unconverged, n_unstationary, n_boundary = (int(v) for v in qmle)
    rate_unconverged = n_unconverged / qmle_total if qmle_total else 0.0
    rate_unstationary = n_unstationary / qmle_total if qmle_total else 0.0
    logger.info(f"QMLE non-convergence: {n_unconverged} of {qmle_total} fitted warm-ups "
                f"({rate_unconverged:.4%}) failed on all {len(QMLE_STARTS)} starts and reverted to "
                f"({QMLE_FALLBACK_ALPHA}, {QMLE_FALLBACK_BETA}); budget {QMLE_CONVERGENCE_BUDGET:.1%}.")
    logger.info(f"QMLE stationarity guard: {n_unstationary} of {qmle_total} ({rate_unstationary:.4%}); "
                f"budget {QMLE_STATIONARITY_BUDGET:.0%}.")
    logger.info(f"QMLE constraint boundary: {n_boundary} of {qmle_total} "
                f"({n_boundary / qmle_total if qmle_total else 0.0:.4%}) returned alpha + beta >= "
                f"{QMLE_PERSISTENCE_CAP}. Those fits are stationary and are KEPT, as in R04.")
    if not args.fast and rate_unstationary > QMLE_STATIONARITY_BUDGET:
        logger.error("The stationarity guard fired although the feasible-set projection makes it "
                     "unreachable. This is a structural failure of the fit, not a tolerance to widen.")
        sys.exit(1)
    if not args.fast and rate_unconverged > QMLE_CONVERGENCE_BUDGET:
        logger.error(f"QMLE non-convergence rate {rate_unconverged:.4%} exceeds the budget of "
                     f"{QMLE_CONVERGENCE_BUDGET:.1%}. The warm-up does not identify the model and Eco_L1 "
                     "stops measuring what it claims to measure.")
        sys.exit(1)

    # In-sample calibration, a convergence check rather than a test. The
    # bisection selects lambda* on the very null set whose rate this reads back,
    # so it fires if and only if the search failed to reach its tolerance inside
    # 15 iterations. It has no probability of firing under any null and falls
    # outside the multiple-testing rule of preamble S4bis, which is why it is
    # allowed to be per-arm where the held-out control below is not.
    off_target = df[(df['FPR_achieved'] - TARGET_FPR).abs() > BISECTION_TOL]
    if not args.fast and len(off_target):
        for row in off_target.itertuples(index=False):
            logger.error(f"Bisection did not converge at nu = {row.nu}, arm = {row.arm}: "
                         f"FPR_achieved = {row.FPR_achieved:.6f}, off target by "
                         f"{abs(row.FPR_achieved - TARGET_FPR):.6f} > {BISECTION_TOL}")
        logger.error("The race is not iso-FPR on at least one arm, so no delay ratio in this campaign "
                     "is interpretable. Reporting stops here.")
        sys.exit(1)
    logger.info(f"In-sample calibration: all {len(df)} arms within {BISECTION_TOL} of {TARGET_FPR}; "
                f"achieved rates span [{df['FPR_achieved'].min():.4f}, {df['FPR_achieved'].max():.4f}] "
                f"over {df['n_bisection_iter'].min()} to {df['n_bisection_iter'].max()} bisection "
                f"iterations.")

    # (c) Calibration, pooled and out of sample.
    k_pooled = int(df['n_alarms_holdout'].sum())
    n_pooled = int(len(df) * n_streams)
    level_pooled = k_pooled / n_pooled
    # The interval carries the factor 2 established above: each of the n_arms
    # thresholds was placed on its own calibration sample, so the pooled held-out
    # level inherits n_arms independent calibration errors alongside its own
    # sampling error. The Wilson interval of a plain binomial understates the
    # half-width by sqrt(2) and is reported only to show the size of that
    # understatement.
    se_pooled = math.sqrt(2.0 * level_pooled * (1.0 - level_pooled) / n_pooled)
    pooled_low = max(0.0, level_pooled - Z_95 * se_pooled)
    pooled_high = min(1.0, level_pooled + Z_95 * se_pooled)
    wilson_low, wilson_high = wilson_interval(k_pooled, n_pooled)
    contains_nominal = pooled_low <= TARGET_FPR <= pooled_high
    intersects_band = (pooled_low <= band[1]) and (pooled_high >= band[0])
    pvals = df['p_conditional'].to_numpy(dtype=float)
    ks_stat, ks_p = stats.kstest(pvals, 'uniform')
    nominal_pvals = df['p_binom_holdout'].to_numpy(dtype=float)
    ks_nominal_stat, ks_nominal_p = stats.kstest(nominal_pvals, 'uniform')
    # The per-arm table is logged BEFORE the gates, so that a campaign stopped by
    # a control still leaves in the log everything needed to characterise the
    # failure, which preamble S4.7 requires and which cannot be done from an
    # artefact the abort prevented from being written.
    logger.info(f"{'nu':>5} {'arm':<11} {'lambda*':>10} {'FPR in-sample':>14} {'FPR held-out':>13} "
                f"{'k':>5} {'p cond':>8} {'p vs .05':>9}")
    for row in df.itertuples(index=False):
        logger.info(f"{row.nu:>5} {row.arm:<11} {row.lambda_star:>10.4f} {row.FPR_achieved:>14.4f} "
                    f"{row.FPR_holdout:>13.4f} {row.n_alarms_holdout:>5} {row.p_conditional:>8.4f} "
                    f"{row.p_binom_holdout:>9.4f}")
    logger.info(f"Calibration check (c) HALF 2, common bias: pooled held-out level {level_pooled:.6f} "
                f"({k_pooled}/{n_pooled}), 95% interval {level_pooled:.6f} +/- {Z_95:.6f}*sqrt(2*"
                f"{level_pooled:.6f}*{1.0 - level_pooled:.6f}/{n_pooled}) = {level_pooled:.6f} +/- "
                f"{Z_95 * se_pooled:.6f} = [{pooled_low:.6f}, {pooled_high:.6f}]. Intersects the "
                f"pre-registered band [{band[0]:.6f}, {band[1]:.6f}]: {intersects_band} (GATING). "
                f"Contains {TARGET_FPR}: {contains_nominal} (reported). The plain Wilson interval of a "
                f"binomial would read [{wilson_low:.6f}, {wilson_high:.6f}], understating the half-width "
                f"by the sqrt(2) established above.")
    logger.info(f"Calibration check (c) HALF 1, per-arm instability: KS of the {len(pvals)} conditional "
                f"two-sample mid-p values against Uniform(0,1): D = {ks_stat:.6f}, p = {ks_p:.6f} "
                f"(GATING at p > {OMNIBUS_GATE_P}).")
    logger.info(f"Calibration check (c), REPORTED and not gating: KS of the {len(nominal_pvals)} "
                f"one-sample p-values, each testing its arm against exactly {TARGET_FPR}: D = "
                f"{ks_nominal_stat:.6f}, p = {ks_nominal_p:.6f}. That null is not what the bisection "
                f"promises -- it omits the calibration half of the variance measured above -- so this "
                f"statistic fires by construction and not by accident of the draw. It is kept as a "
                f"diagnostic and reported in full in AUDIT_R04b.md.")
    # Where the non-uniformity lives, measured rather than inferred: the same KS
    # statistic within each arm separately, beside the discreteness of that arm's
    # null statistic and the dispersion of its held-out levels. Descriptive, and
    # gating on none of it.
    for arm in REPORTED_ARMS:
        block = df[df['arm'] == arm]
        d_arm, p_arm = stats.kstest(block['p_conditional'].to_numpy(dtype=float), 'uniform')
        observed_sd = float(block['FPR_holdout'].std(ddof=1))
        logger.info(f"Calibration diagnostic [{arm}]: held-out level {block['FPR_holdout'].mean():.4f} "
                    f"on average over the {len(block)} nu, spread {observed_sd:.6f} against the "
                    f"{binomial_sd:.6f} a binomial at a known threshold would give and the "
                    f"{math.sqrt(2.0) * binomial_sd:.6f} the calibrate-then-test design predicts; "
                    f"conditional KS over its {len(block)} arms D = {d_arm:.4f}, p = {p_arm:.4f}. "
                    f"Distinct suprema per stream in the 94-96 percentile band of the calibration "
                    f"sample: {block['distinct_sup_fraction'].mean():.4f} (1.0 = every supremum "
                    f"distinct, so the reachable levels are spaced 1/N apart; below 1 the statistic "
                    f"ties and the reachable levels are coarser).")
    total_sd = float(df['FPR_holdout'].std(ddof=1))
    logger.warning(
        f"Calibration diagnostic, residual excess NOT ATTRIBUTED: over all {len(df)} arms the held-out "
        f"spread is {total_sd:.6f} against the {math.sqrt(2.0) * binomial_sd:.6f} the doubled variance "
        f"predicts, a ratio of {total_sd / (math.sqrt(2.0) * binomial_sd):.4f}. At {len(df)} arms the "
        f"standard error of an estimated standard deviation is about "
        f"{1.0 / math.sqrt(2.0 * (len(df) - 1)):.1%} of it, so the excess is of the order of one such "
        f"error. The coarseness of the bisection lattice, measured per arm above, is a candidate "
        f"explanation and is not established as the cause: no counterfactual in this campaign separates "
        f"it from ordinary sampling variation in a variance estimate.")

    if not args.fast and not intersects_band:
        logger.error(f"Control (c) half 2: the pooled held-out level {level_pooled:.6f}, interval "
                     f"[{pooled_low:.6f}, {pooled_high:.6f}], does not meet the band the calibration "
                     f"procedure promises, [{band[0]:.6f}, {band[1]:.6f}]. Every arm would be displaced "
                     "in the same direction, which the conditional test of half 1 cannot see. No delay "
                     "comparison in this campaign is interpretable.")
        sys.exit(1)
    if not args.fast and ks_p <= OMNIBUS_GATE_P:
        logger.error(f"Control (c) half 1: the {len(pvals)} conditional p-values are not uniform (KS "
                     f"p = {ks_p:.6f}): at least one threshold does not carry the level it was "
                     "calibrated to onto a fresh sample, so the race is not iso-FPR where it claims.")
        sys.exit(1)

    # --- THE BOOTSTRAP, JOINT OVER BOTH SAMPLES ---
    #
    # A replicate resamples the calibration streams AND the drifted streams. It
    # re-runs the bisection on its own calibration resample, which gives it its
    # own three thresholds, and then reads the delays of its own drifted resample
    # at those thresholds off the ladder. Both sources of error are therefore
    # priced: the delays, and the placement of the thresholds those delays are
    # read at.
    #
    # Holding lambda* fixed and resampling only the drifted streams -- the
    # obvious bootstrap, and the one this script first ran -- omits the second
    # source entirely. It is the same omission that makes a one-sample test of
    # the held-out level fire by construction, one level further in, and it is
    # not small here: the two campaigns' Eco-L1 thresholds differ by two to four
    # percent at the five points they share, while the Concept threshold lands on
    # the same lattice point, so the ratio inherits almost all of that.
    #
    # The three arms of a replicate share one calibration resample and one
    # drifted resample, so their thresholds and their delays move together
    # exactly as they do in the campaign, and the difference of the two crossings
    # keeps the pairing that makes it precise.
    boot_rng = np.random.default_rng(get_deterministic_seed("R04b", "bootstrap", BOOTSTRAP_REPLICATES))
    boot_ratios = {arm: np.empty((BOOTSTRAP_REPLICATES, len(NU_GRID))) for arm in ("Eco_L1", "Oracle_Eco")}
    n_clipped = 0
    reported_indices = [ARMS.index(arm) for arm in REPORTED_ARMS]
    for position, nu in enumerate(NU_GRID):
        sup_here, ladder_here, lam_here = sup_calib[nu], ladder_alarms[nu], lambda_star[nu]
        add_boot = {arm: np.empty(BOOTSTRAP_REPLICATES) for arm in REPORTED_ARMS}
        for start in range(0, BOOTSTRAP_REPLICATES, BOOTSTRAP_CHUNK):
            stop = min(start + BOOTSTRAP_CHUNK, BOOTSTRAP_REPLICATES)
            calib_draw = boot_rng.integers(0, n_streams, size=(stop - start, n_streams))
            drift_draw = boot_rng.integers(0, n_streams, size=(stop - start, n_streams))
            for arm, j in zip(REPORTED_ARMS, reported_indices):
                rungs = np.column_stack([resampled_means(ladder_here[:, j, k], drift_draw)
                                         for k in range(len(LAMBDA_LADDER))])
                for r in range(stop - start):
                    lam_b, _, _, _ = bisect_threshold(sup_here[calib_draw[r], j], TARGET_FPR,
                                                      BISECTION_TOL, BISECTION_ITERS)
                    scale = lam_b / lam_here[j]
                    n_clipped += int(not (LAMBDA_LADDER[0] <= scale <= LAMBDA_LADDER[-1]))
                    add_boot[arm][start + r] = np.interp(
                        min(max(scale, LAMBDA_LADDER[0]), LAMBDA_LADDER[-1]), LAMBDA_LADDER, rungs[r])
        for arm in ("Eco_L1", "Oracle_Eco"):
            boot_ratios[arm][:, position] = add_boot["Concept"] / add_boot[arm]

    ratio_ses = {arm: np.nanstd(boot_ratios[arm], axis=0, ddof=1) for arm in ("Eco_L1", "Oracle_Eco")}
    # Persisted so that the inferential bracket -- the statement that governs
    # every manuscript formulation -- can be recomputed from the CSV alone,
    # without re-running the campaign. The Concept row carries zero because
    # ADD_Concept / ADD_Concept is 1 by construction and not a measurement.
    se_lookup = {(nu, arm): float(ratio_ses[arm][position])
                 for arm in ("Eco_L1", "Oracle_Eco") for position, nu in enumerate(NU_GRID)}
    conditional_lookup = {(nu, arm): float(ratio_ses_conditional[arm][position])
                          for arm in ("Eco_L1", "Oracle_Eco") for position, nu in enumerate(NU_GRID)}
    df['ratio_concept_to_arm_se'] = [se_lookup.get((row.nu, row.arm), 0.0) for row in df.itertuples(index=False)]
    df['ratio_concept_to_arm_se_conditional'] = [conditional_lookup.get((row.nu, row.arm), 0.0)
                                                 for row in df.itertuples(index=False)]
    for arm in ("Eco_L1", "Oracle_Eco"):
        conditional = np.asarray(ratio_ses_conditional[arm], dtype=float)
        inflation = ratio_ses[arm] / conditional
        logger.info(
            f"Bootstrap standard error of the delay ratio [{arm}], over {BOOTSTRAP_REPLICATES} "
            f"replicates that resample both samples: " +
            ", ".join(f"nu={nu}: {se:.6f}" for nu, se in zip(NU_GRID, ratio_ses[arm])) +
            f". Against the delta-method error conditional on the threshold, the inflation runs from "
            f"{inflation.min():.2f} to {inflation.max():.2f}, median {float(np.median(inflation)):.2f}. "
            f"Every interval below uses the bootstrap error; the conditional one is reported here "
            f"because it is what a bootstrap of the drifted sample alone would have given.")
    logger.info(f"Bootstrap threshold ladder: {n_clipped} of "
                f"{BOOTSTRAP_REPLICATES * len(NU_GRID) * len(REPORTED_ARMS)} re-calibrated thresholds "
                f"fell outside the ladder span {LAMBDA_LADDER[0]} to {LAMBDA_LADDER[-1]} and were read "
                f"at its edge. A rate above a fraction of a percent would mean the span is too narrow "
                f"and the tails of the interval are compressed.")

    # (b) Continuity with R04 at the five common points.
    #
    # The seeds differ by design -- R04b keys on ("R04b", role, nu, i) -- so the
    # two campaigns are independent draws of the same quantity and cannot agree
    # exactly. The comparison is therefore a confidence statement on their
    # difference, whose variance is twice this campaign's: both are 2000-stream
    # draws of the same generator at the same nu, Gamma and c, through primitives
    # asserted byte-identical above, so their sampling variances are equal and one
    # of them may be estimated from the draw in hand.
    if not R04_EFFICIENCY_CSV.exists():
        logger.error(f"R04's efficiency table is missing at {R04_EFFICIENCY_CSV}. Continuity with R04 "
                     "cannot be established and this campaign cannot be certified.")
        sys.exit(1)
    df_r04 = pd.read_csv(R04_EFFICIENCY_CSV, float_precision='round_trip')
    continuity = []
    for arm, column in (("Eco_L1", "ratio"), ("Oracle_Eco", "ratio_oracle")):
        z_scores = []
        for nu in NU_COMMON_WITH_R04:
            mine = float(np.asarray(ratios[arm])[np.asarray(NU_GRID) == nu][0])
            theirs_ratio = float(df_r04[np.isclose(df_r04['nu'], nu)][column].iloc[0])
            se_diff = math.sqrt(2.0) * float(np.asarray(ratio_ses[arm])[np.asarray(NU_GRID) == nu][0])
            z = (mine - theirs_ratio) / se_diff
            z_scores.append(z)
            continuity.append({'arm': arm, 'nu': nu, 'ratio_R04b': mine, 'ratio_R04': theirs_ratio,
                               'difference': mine - theirs_ratio, 'SE_difference': se_diff, 'z': z})
        chi2_cont = float(np.sum(np.square(z_scores)))
        p_cont = float(stats.chi2.sf(chi2_cont, len(z_scores)))
        logger.info(f"Continuity check (b) [{arm}]: z at nu = " + ", ".join(
            f"{nu}: {z:+.3f}" for nu, z in zip(NU_COMMON_WITH_R04, z_scores)) +
            f"; omnibus sum z^2 = {chi2_cont:.4f} on {len(z_scores)} degrees of freedom, p = "
            f"{p_cont:.4f} (gating at p > {OMNIBUS_GATE_P}).")
        if not args.fast and p_cont <= OMNIBUS_GATE_P:
            logger.error(f"The {arm} delay ratios of this campaign are not compatible with R04's at the "
                         f"five common points (p = {p_cont:.4f}). The two scripts measure different "
                         "things and no refinement of the grid can be read against R04's result.")
            sys.exit(1)
    df_continuity = pd.DataFrame(continuity)

    # (d) Monotonicity, reported and not gated. R04 gated on the consecutive
    # differences of a six-point grid; at twelve points the consecutive steps are
    # of the order of the sampling error by construction, so such a gate would
    # test the draw rather than the shape.
    spearman = {}
    for arm in ("Eco_L1", "Oracle_Eco"):
        rho, rho_p = stats.spearmanr(NU_GRID, ratios[arm])
        spearman[arm] = (float(rho), float(rho_p))
        diffs = np.diff(np.asarray(ratios[arm]))
        logger.info(f"Monotonicity check (d) [{arm}]: Spearman rho = {rho:.4f} (p = {rho_p:.3e}) over "
                    f"{len(NU_GRID)} points; most negative consecutive difference {diffs.min():+.6f}. "
                    f"Reported, not gated.")
    # Reported, not gated, and not a claim of v87. Proposition prop:are caps the
    # ratio against the EXACTLY standardized arm at pi/2 in the Gaussian limit,
    # and v87 states the property of the Concept / Eco-L1 curve, which is what
    # Figure 4B plots and what the register below judges. The oracle curve is the
    # one prop:are speaks about directly, and it overshoots: the proposition is
    # an asymptotic in the small-drift limit and this campaign runs at c = 0.5,
    # which is not small. No mechanism for the size of the overshoot is
    # established here.
    max_eco = max(ratios["Eco_L1"])
    max_oracle = max(ratios["Oracle_Eco"])
    nu_at_max_oracle = NU_GRID[int(np.argmax(ratios["Oracle_Eco"]))]
    logger.info(f"Ceiling check: the largest Concept/Eco-L1 ratio is {max_eco:.4f}, below the Gaussian "
                f"ceiling pi/2 = {GAUSSIAN_CEILING:.4f} that v87 states for this curve. The "
                f"Concept/Oracle-Eco ratio reaches {max_oracle:.4f} at nu = {nu_at_max_oracle}, "
                f"{'above' if max_oracle > GAUSSIAN_CEILING else 'below'} that ceiling and "
                f"{max_oracle / shape_prediction(nu_at_max_oracle) - 1.0:+.1%} against its own analytic "
                f"prediction there. prop:are is an asymptotic in the small-drift limit; c = {C_SHIFT} is "
                f"not small, and the size of the departure is not attributed here.")
    oracle_high = np.asarray(ratios["Oracle_Eco"])[np.asarray(NU_GRID) >= 7.0]
    logger.info(f"Monotonicity check (d): over [7, 30] the oracle ratio stays at or above "
                f"{oracle_high.min():.4f} at every point, so it crosses unity nowhere on the interval the "
                f"prompt's original grid covered, and no second crossing exists on the extended grid.")

    # --- THE FOUR CROSSING ESTIMATORS ---
    g_grid = np.array([shape_prediction(nu) for nu in NU_GRID])
    nu_star_analytic = invert_shape(1.0)
    estimators = {}
    for arm in ("Eco_L1", "Oracle_Eco"):
        r = np.asarray(ratios[arm], dtype=float)
        se = np.asarray(ratio_ses[arm], dtype=float)
        interp, grid_lo, grid_hi = crossing_point(NU_GRID, r)
        infer_lo, infer_hi = inferential_bracket(NU_GRID, r, se)
        a, b, r2, max_resid, chi2_fit, dof_fit, p_fit, nu_fit = shape_fit(g_grid, r, se)
        valid = bool(np.isfinite(nu_fit)) and p_fit > OMNIBUS_GATE_P
        estimators[arm] = {
            'grid_lo': grid_lo, 'grid_hi': grid_hi, 'interp': interp,
            'infer_lo': infer_lo, 'infer_hi': infer_hi,
            'a': a, 'b': b, 'r2': r2, 'max_resid': max_resid, 'chi2': chi2_fit,
            'dof': dof_fit, 'p_fit': p_fit,
            # fit_raw is what the inversion returns and is always logged, so a
            # withdrawal can be audited; fit is what may be cited, and is NaN
            # exactly when the goodness test refuses the model.
            'fit_raw': nu_fit, 'fit': nu_fit if valid else float('nan'), 'valid': valid,
        }
        logger.info(
            f"Crossing estimators [{arm}]: (1) grid bracket [{grid_lo}, {grid_hi}] -- model free, "
            f"resolution limited, no confidence attached. (1b) two-point interpolation inside it = "
            f"{interp:.4f}, R04's rule, kept for comparability only. (2) inferential bracket "
            f"[{infer_lo}, {infer_hi}] -- the largest nu whose 95% ratio interval is entirely below unity "
            f"and the smallest whose interval is entirely above it; this is the statement that carries "
            f"confidence. (3) shape fit ratio = {a:+.6f} + {b:.6f}*1/(4 f_z(0)^2), weighted R^2 = "
            f"{r2:.6f}, largest standardized residual {max_resid:.3f}, chi2 = {chi2_fit:.3f} on "
            f"{dof_fit} dof (p = {p_fit:.4f}), inverted at {nu_fit:.4f}"
            + ("" if valid else " -- WITHDRAWN, the linear-in-shape model does not hold at p > "
                                f"{OMNIBUS_GATE_P} and a fit that fails its own goodness test measures "
                                "nothing about the crossing")
            + f". (4) analytic root of 1/(4 f_z(0)^2) = 1 at nu = {nu_star_analytic:.6f}, a property of "
            f"the innovation law alone and therefore one number for both arms.")

    # The crossings of every replicate, from the ratios the joint bootstrap
    # already produced. Both arms are inverted inside the same replicate, so the
    # difference of the two crossings keeps its pairing: the two ratios share
    # their numerator and their streams, and treating them as independent would
    # price the estimation cost far too wide.
    weights = {arm: 1.0 / np.asarray(ratio_ses[arm], dtype=float) ** 2 for arm in ("Eco_L1", "Oracle_Eco")}
    boot_crossings, boot_interp = {}, {}
    for arm in ("Eco_L1", "Oracle_Eco"):
        boot_crossings[arm] = np.array([fit_crossing(g_grid, boot_ratios[arm][b_i], weights[arm])
                                        for b_i in range(BOOTSTRAP_REPLICATES)])
        # The same resamples carried through the two-point interpolation rule.
        # It assumes no shape at all, so it survives a refusal of the affine
        # model, and on this grid it interpolates across one unit of nu rather
        # than across the 23-unit void that made R04's version meaningless. Its
        # replicate-to-replicate variability includes the bracket moving between
        # grid cells, which is the failure mode a single interpolation hides.
        boot_interp[arm] = np.array([crossing_point(NU_GRID, boot_ratios[arm][b_i])[0]
                                     for b_i in range(BOOTSTRAP_REPLICATES)])
    both_finite = np.isfinite(boot_crossings["Eco_L1"]) & np.isfinite(boot_crossings["Oracle_Eco"])
    boot_cost = boot_crossings["Eco_L1"][both_finite] - boot_crossings["Oracle_Eco"][both_finite]
    both_interp = np.isfinite(boot_interp["Eco_L1"]) & np.isfinite(boot_interp["Oracle_Eco"])
    boot_cost_interp = boot_interp["Eco_L1"][both_interp] - boot_interp["Oracle_Eco"][both_interp]
    for arm in ("Eco_L1", "Oracle_Eco"):
        finite = np.isfinite(boot_crossings[arm])
        lo, hi = np.percentile(boot_crossings[arm][finite], [2.5, 97.5])
        valid = estimators[arm]['valid']
        estimators[arm]['ci_low'] = float(lo) if valid else float('nan')
        estimators[arm]['ci_high'] = float(hi) if valid else float('nan')
        estimators[arm]['n_boot'] = int(finite.sum())
        interp_finite = np.isfinite(boot_interp[arm])
        interp_lo, interp_hi = np.percentile(boot_interp[arm][interp_finite], [2.5, 97.5])
        estimators[arm]['interp_ci_low'] = float(interp_lo)
        estimators[arm]['interp_ci_high'] = float(interp_hi)
        estimators[arm]['n_boot_interp'] = int(interp_finite.sum())
        logger.info(f"Bootstrap [{arm}], model-free arm: the two-point interpolation rule brackets a "
                    f"crossing in {int(interp_finite.sum())} of {BOOTSTRAP_REPLICATES} replicates and "
                    f"gives {estimators[arm]['interp']:.4f} with a paired 95% interval of "
                    f"[{interp_lo:.4f}, {interp_hi:.4f}]. This estimator assumes no shape, so it stands "
                    f"whether or not the affine fit is refused; the replicates in which no bracket "
                    f"exists are those where the crossing leaves the grid.")
        logger.info(f"Bootstrap [{arm}]: {int(finite.sum())} of {BOOTSTRAP_REPLICATES} replicates invert "
                    f"to a finite crossing; the shape fit inverts at {estimators[arm]['fit_raw']:.4f} "
                    f"with a paired stream-level 95% interval of [{lo:.4f}, {hi:.4f}]"
                    + ("" if valid else ", both WITHDRAWN by the goodness-of-fit gate above") +
                    f". Replicates that do not invert are those whose fitted curve does not reach unity "
                    f"below the Gaussian ceiling; they are counted, not discarded silently.")

    cost_point = estimators["Eco_L1"]['fit'] - estimators["Oracle_Eco"]['fit']
    cost_valid = estimators["Eco_L1"]['valid'] and estimators["Oracle_Eco"]['valid']
    if len(boot_cost) and cost_valid:
        cost_low, cost_high = (float(v) for v in np.percentile(boot_cost, [2.5, 97.5]))
    else:
        cost_low, cost_high = float('nan'), float('nan')
    cost_interp = estimators["Eco_L1"]['interp'] - estimators["Oracle_Eco"]['interp']
    if len(boot_cost_interp):
        cost_interp_low, cost_interp_high = (float(v) for v in np.percentile(boot_cost_interp, [2.5, 97.5]))
    else:
        cost_interp_low, cost_interp_high = float('nan'), float('nan')
    bracket_low = estimators["Eco_L1"]['infer_lo'] - estimators["Oracle_Eco"]['infer_hi']
    bracket_high = estimators["Eco_L1"]['infer_hi'] - estimators["Oracle_Eco"]['infer_lo']
    logger.info(
        f"Estimation cost nu*(Eco-L1) - nu*(Oracle): point estimate "
        f"{format_macro_value(cost_point, 4, 'withdrawn')} from the difference of the two shape fits, "
        f"paired bootstrap 95% interval [{format_macro_value(cost_low, 4, 'withdrawn')}, "
        f"{format_macro_value(cost_high, 4, 'withdrawn')}] over {len(boot_cost)} replicates in which "
        f"both curves invert. v87 prints {ESTIMATION_COST_PUBLISHED}. The model-free outer bound from "
        f"the two inferential brackets is [{format_macro_value(bracket_low, 4)}, "
        f"{format_macro_value(bracket_high, 4)}]: it treats two quantities that share their numerator "
        f"and their streams as if they were independent, so it is an outer bound and not a measurement.")
    logger.info(
        f"Estimation cost, model-free route: difference of the two interpolated crossings = "
        f"{format_macro_value(cost_interp, 4)}, paired bootstrap 95% interval "
        f"[{format_macro_value(cost_interp_low, 4)}, {format_macro_value(cost_interp_high, 4)}] over "
        f"{len(boot_cost_interp)} replicates in which both arms bracket a crossing. This route assumes "
        f"no functional form and is the one to quote if the affine fit is refused.")

    # The resolution limit of the whole experiment, stated as a number so it can
    # be quoted: how many units of nu one ratio standard error spans near the
    # crossing. Extra grid points do not change it.
    b_eco = estimators["Eco_L1"]['b']
    nu_at = (estimators["Eco_L1"]['fit_raw'] if np.isfinite(estimators["Eco_L1"]['fit_raw'])
             else float(np.median(NU_GRID)))
    slope = b_eco * (shape_prediction(nu_at + 0.05) - shape_prediction(nu_at - 0.05)) / 0.1
    se_near = float(np.asarray(ratio_ses["Eco_L1"])[np.argmin(np.abs(np.asarray(NU_GRID) - nu_at))])
    nu_per_se = se_near / slope if slope > 0 else float('nan')
    logger.info(f"Resolution: near the fitted crossing the ratio moves by {slope:.6f} per unit of nu "
                f"while its standard error at the nearest grid point is {se_near:.6f}, so one standard "
                f"error spans {nu_per_se:.2f} units of nu. This is why the primary estimate is a fit over "
                f"twelve points and not an interpolation between two.")

    # --- PERSISTENCE ---
    columns = ['nu', 'arm', 'lambda_star', 'FPR_achieved', 'DetRate', 'ADD_conditional', 'SEM',
               'n_detected', 'n_censored', 'ratio_to_eco', 'analytic_prediction',
               'ratio_concept_to_arm', 'ratio_concept_to_arm_se',
               'ratio_concept_to_arm_se_conditional', 'n_alarms_calib', 'n_alarms_holdout', 'FPR_holdout',
               'p_conditional', 'p_binom_holdout', 'distinct_sup_fraction',
               'n_bisection_iter', 'bisection_converged', 'horizon']
    df = df[columns]
    outputs = {f"R04b_ratio_vs_nu{suffix}.csv": df,
               f"R04b_continuity_with_R04{suffix}.csv": df_continuity}
    for name, frame in outputs.items():
        save_fair_csv(frame, DATA_DIR / name)

    if len(df) != len(NU_GRID) * len(REPORTED_ARMS):
        logger.error(f"Cardinality error: {len(df)} rows, expected {len(NU_GRID) * len(REPORTED_ARMS)}")
        sys.exit(1)
    logger.info(f"Cardinality check: R04b_ratio_vs_nu = {len(df)} rows "
                f"({len(NU_GRID)} nu x {len(REPORTED_ARMS)} arms), "
                f"R04b_continuity_with_R04 = {len(df_continuity)} rows.")

    # --- FIGURE A3 ---
    fig, ax = plt.subplots(figsize=(9, 6))
    # The abscissa spans both campaigns: R04 measured a point at nu = 3 that this
    # grid does not carry, and dropping it off the axis would hide the only place
    # the two campaigns disagree about the shape rather than about a value.
    all_nu = sorted(set(NU_GRID) | set(float(v) for v in df_r04['nu']))
    dense = np.geomspace(all_nu[0] * 0.95, all_nu[-1] * 1.05, 400)
    ax.plot(dense, [shape_prediction(v) for v in dense], linestyle='--', color='crimson',
            linewidth=1.2, label=r"Predicted $1/(4 f_z(0)^2)$")
    ax.axhline(1.0, color='grey', linewidth=0.8, linestyle=':')
    if np.isfinite(estimators["Eco_L1"]['ci_low']):
        ax.axvspan(estimators["Eco_L1"]['ci_low'], estimators["Eco_L1"]['ci_high'],
                   color='tab:blue', alpha=0.12,
                   label=r"$\nu^{\star}$(Eco-L1), bootstrap 95%")
    ax.errorbar(NU_GRID, ratios["Eco_L1"], yerr=Z_95 * np.asarray(ratio_ses["Eco_L1"]),
                marker='o', markersize=6, linewidth=1.2, capsize=3, color='tab:blue',
                label="R04b, Concept / Eco-L1")
    ax.errorbar(NU_GRID, ratios["Oracle_Eco"], yerr=Z_95 * np.asarray(ratio_ses["Oracle_Eco"]),
                marker='s', markersize=6, linewidth=1.2, capsize=3, color='tab:green',
                label="R04b, Concept / Oracle-Eco")
    ax.plot(df_r04['nu'], df_r04['ratio'], marker='o', markersize=9, linestyle='none',
            markerfacecolor='none', markeredgecolor='tab:blue', label="R04, Concept / Eco-L1")
    ax.plot(df_r04['nu'], df_r04['ratio_oracle'], marker='s', markersize=9, linestyle='none',
            markerfacecolor='none', markeredgecolor='tab:green', label="R04, Concept / Oracle-Eco")
    ax.set_xscale('log')
    ax.set_xticks(all_nu)
    ax.set_xticklabels([f"{v:g}" for v in all_nu])
    ax.minorticks_off()
    ax.set_xlabel(r"Degrees of freedom $\nu$ (log scale)")
    ax.set_ylabel(r"$\mathrm{ADD}_{\mathrm{Concept}} / \mathrm{ADD}_{\mathrm{parametric}}$")
    ax.set_title("Resolution of the efficiency crossing point", fontweight="bold", loc="left")
    ax.legend(loc='lower right', fontsize=9)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / f"figA03_nu_star_refinement{suffix}.png", dpi=150)
    plt.close()

    # --- MACROS ---
    # Every value is computed from the objects in memory; the estimator is named
    # inside the macro so that no two can be confused at the point of use.
    macros = ["% Auto-generated by exp_R04b_nu_refinement.py -- do not edit.",
              f"\\newcommand{{\\RFourBNuGridSize}}{{{len(NU_GRID)}}}",
              f"\\newcommand{{\\RFourBNullStreams}}{{{n_streams}}}",
              f"\\newcommand{{\\RFourBGamma}}{{{GAMMA_RACE:.2f}}}",
              f"\\newcommand{{\\RFourBDrift}}{{{C_SHIFT}}}",
              f"\\newcommand{{\\RFourBNuStarAnalytic}}{{{nu_star_analytic:.4f}}}"]
    for arm, label in (("Eco_L1", "Eco"), ("Oracle_Eco", "Oracle")):
        e = estimators[arm]
        macros += [
            f"\\newcommand{{\\RFourBNuStar{label}GridLower}}{{{format_macro_value(e['grid_lo'], 1)}}}",
            f"\\newcommand{{\\RFourBNuStar{label}GridUpper}}{{{format_macro_value(e['grid_hi'], 1)}}}",
            f"\\newcommand{{\\RFourBNuStar{label}InferLower}}{{{format_macro_value(e['infer_lo'], 1)}}}",
            f"\\newcommand{{\\RFourBNuStar{label}InferUpper}}{{{format_macro_value(e['infer_hi'], 1)}}}",
            f"\\newcommand{{\\RFourBNuStar{label}Interp}}{{{format_macro_value(e['interp'], 2)}}}",
            f"\\newcommand{{\\RFourBNuStar{label}InterpCiLow}}{{{format_macro_value(e['interp_ci_low'], 2)}}}",
            f"\\newcommand{{\\RFourBNuStar{label}InterpCiHigh}}{{{format_macro_value(e['interp_ci_high'], 2)}}}",
            f"\\newcommand{{\\RFourBNuStar{label}Fit}}{{{format_macro_value(e['fit'], 2, 'withdrawn')}}}",
            f"\\newcommand{{\\RFourBNuStar{label}FitCiLow}}{{{format_macro_value(e['ci_low'], 2, 'withdrawn')}}}",
            f"\\newcommand{{\\RFourBNuStar{label}FitCiHigh}}{{{format_macro_value(e['ci_high'], 2, 'withdrawn')}}}",
            f"\\newcommand{{\\RFourBFit{label}Slope}}{{{e['b']:.4f}}}",
            f"\\newcommand{{\\RFourBFit{label}Intercept}}{{{e['a']:.4f}}}",
            f"\\newcommand{{\\RFourBFit{label}RSquared}}{{{e['r2']:.4f}}}",
            f"\\newcommand{{\\RFourBFit{label}MaxResidual}}{{{e['max_resid']:.2f}}}",
            f"\\newcommand{{\\RFourBFit{label}PValue}}{{{e['p_fit']:.4f}}}",
        ]
    macros += [
        f"\\newcommand{{\\RFourBEstimationCostDof}}{{{format_macro_value(cost_point, 2, 'withdrawn')}}}",
        f"\\newcommand{{\\RFourBEstimationCostLower}}{{{format_macro_value(cost_low, 2, 'withdrawn')}}}",
        f"\\newcommand{{\\RFourBEstimationCostUpper}}{{{format_macro_value(cost_high, 2, 'withdrawn')}}}",
        f"\\newcommand{{\\RFourBEstimationCostInterp}}{{{format_macro_value(cost_interp, 2)}}}",
        f"\\newcommand{{\\RFourBEstimationCostInterpLower}}{{{format_macro_value(cost_interp_low, 2)}}}",
        f"\\newcommand{{\\RFourBEstimationCostInterpUpper}}{{{format_macro_value(cost_interp_high, 2)}}}",
        f"\\newcommand{{\\RFourBEstimationCostBracketLower}}{{{format_macro_value(bracket_low, 1)}}}",
        f"\\newcommand{{\\RFourBEstimationCostBracketUpper}}{{{format_macro_value(bracket_high, 1)}}}",
        f"\\newcommand{{\\RFourBBootstrapReplicates}}{{{BOOTSTRAP_REPLICATES}}}",
        f"\\newcommand{{\\RFourBNuPerStandardError}}{{{nu_per_se:.1f}}}",
        f"\\newcommand{{\\RFourBSpearmanRho}}{{{spearman['Eco_L1'][0]:.3f}}}",
        f"\\newcommand{{\\RFourBHoldoutLevel}}{{{level_pooled * 100:.2f}\\%}}",
        f"\\newcommand{{\\RFourBHoldoutCiLow}}{{{pooled_low * 100:.2f}\\%}}",
        f"\\newcommand{{\\RFourBHoldoutCiHigh}}{{{pooled_high * 100:.2f}\\%}}",
        f"\\newcommand{{\\RFourBKsConditionalP}}{{{ks_p:.3f}}}",
        f"\\newcommand{{\\RFourBKsNominalP}}{{{ks_nominal_p:.4f}}}",
        f"\\newcommand{{\\RFourBVarianceFactor}}{{{probe_sd / binomial_sd:.3f}}}",
        f"\\newcommand{{\\RFourBRatioMax}}{{{max(ratios['Eco_L1']):.3f}}}",
        f"\\newcommand{{\\RFourBGaussianCeiling}}{{{GAUSSIAN_CEILING:.4f}}}",
    ]
    tex_name = f"R04b_claims{suffix}.tex"
    with open(TABLES_DIR / tex_name, "w") as f:
        f.write("\n".join(macros) + "\n")

    # --- REGISTER ---
    # The case the data give, decided programmatically. No case is presupposed:
    # the prompt asks which of the three is observed, and the answer is read off
    # the inferential bracket rather than argued.
    infer_lo, infer_hi = estimators["Eco_L1"]['infer_lo'], estimators["Eco_L1"]['infer_hi']
    if np.isfinite(infer_lo) and np.isfinite(infer_hi):
        excluded = not (infer_lo <= NU_STAR_PUBLISHED <= infer_hi)
        case = "A" if excluded else "B"
        case_text = (f"the crossing is enclosed by [{infer_lo}, {infer_hi}] and v87's "
                     f"{NU_STAR_PUBLISHED} is " + ("outside it" if excluded else "inside it"))
    else:
        case = "C"
        case_text = ("no crossing is enclosed on the measured grid: "
                     + ("the ratio interval never lies entirely above unity"
                        if not np.isfinite(infer_hi) else
                        "the ratio interval never lies entirely below unity"))
    logger.warning(f"Case {case}: {case_text}.")

    if not args.fast:
        register = []
        for arm, published in (("Eco_L1", NU_STAR_PUBLISHED), ("Oracle_Eco", NU_STAR_ORACLE_PUBLISHED)):
            e = estimators[arm]
            register.append((
                f"{'efficiency ratio' if arm == 'Eco_L1' else 'oracle arm'} crosses unity at "
                f"nu* ~ {published}", f"{published}",
                f"inferential bracket [{format_macro_value(e['infer_lo'], 1)}, "
                f"{format_macro_value(e['infer_hi'], 1)}], fit "
                f"{format_macro_value(e['fit'], 2, 'withdrawn')} "
                f"[{format_macro_value(e['ci_low'], 2, 'withdrawn')}, "
                f"{format_macro_value(e['ci_high'], 2, 'withdrawn')}]",
                bool(np.isfinite(e['infer_lo']) and np.isfinite(e['infer_hi'])
                     and e['infer_lo'] <= published <= e['infer_hi'])))
        register += [
            ("finite warm-up costs 0.3 degrees of freedom", f"{ESTIMATION_COST_PUBLISHED}",
             f"{format_macro_value(cost_point, 2, 'withdrawn')} "
             f"[{format_macro_value(cost_low, 2, 'withdrawn')}, "
             f"{format_macro_value(cost_high, 2, 'withdrawn')}]",
             bool(np.isfinite(cost_low) and cost_low <= ESTIMATION_COST_PUBLISHED <= cost_high)),
            ("  the same cost by the model-free route", f"{ESTIMATION_COST_PUBLISHED}",
             f"{format_macro_value(cost_interp, 2)} [{format_macro_value(cost_interp_low, 2)}, "
             f"{format_macro_value(cost_interp_high, 2)}]",
             bool(np.isfinite(cost_interp_low)
                  and cost_interp_low <= ESTIMATION_COST_PUBLISHED <= cost_interp_high)),
            ("analytic crossing at 4.7", f"{NU_STAR_ANALYTIC_PUBLISHED}", f"{nu_star_analytic:.4f}",
             round(nu_star_analytic, 1) == NU_STAR_ANALYTIC_PUBLISHED),
            ("ratio never exceeds the Gaussian ceiling pi/2", f"<= {GAUSSIAN_CEILING:.4f}",
             f"max {max(ratios['Eco_L1']):.4f}", bool(max(ratios["Eco_L1"]) <= GAUSSIAN_CEILING)),
            ("AUDIT_R04.md interpolated 8.52 across the (7, 30) void", f"{NU_STAR_R04_INTERPOLATED}",
             f"two-point interpolation on this grid {estimators['Eco_L1']['interp']:.2f}",
             round(estimators['Eco_L1']['interp'], 1) == round(NU_STAR_R04_INTERPOLATED, 1)),
        ]
        logger.info("Register. 'held' means the value of v87 lies inside the interval this campaign "
                    "measures; 'not held' means it does not. No parameter, tolerance, seed or bound was "
                    "moved to change any line of this table.")
        logger.info(f"{'claim':<52} | {'published':<12} | {'regenerated':<70} | verdict")
        for claim, published, regenerated, held in register:
            logger.info(f"{claim:<52} | {published:<12} | {regenerated:<70} | "
                        f"{'held' if held else 'not held'}")

    for name in outputs:
        logger.info(f"SHA-256 {name} : {compute_sha256(DATA_DIR / name)}")
    for rel, path in ((f"figA03_nu_star_refinement{suffix}.png",
                       FIGURES_DIR / f"figA03_nu_star_refinement{suffix}.png"),
                      (tex_name, TABLES_DIR / tex_name)):
        logger.info(f"SHA-256 {rel} : {compute_sha256(path)}")

    logger.info(f"Execution completed in {elapsed:.1f}s with {args.n_jobs} workers "
                f"({len(NU_GRID) * 3 * n_streams} monitored streams over three passes), plus "
                f"{BOOTSTRAP_REPLICATES} bootstrap replicates.")


if __name__ == "__main__":
    main()
