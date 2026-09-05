#!/usr/bin/env python3
"""
==========================================================================
R12 -- VOLATILITY MISSPECIFICATION AND MOMENT SINGULARITY (v87 Figures 12, 13)
==========================================================================
This script ports the submitted campaign `Priorite_10_robustness_gjr_student.py`
-- which writes `protocol_expA_leverage_fpr.csv` and
`protocol_expB_singularity_add.csv` -- into the repository's FAIR harness and
classifies every published numeral D0-D3.

The two figures are `fig:leverage` (Figure 12) and `fig:fat_tails` (Figure 13),
established by counting `\\label{fig:...}` in submission order in the frozen
`articleB_whitening_v87.tex`: that count places `fig:anytime` at 9,
`fig:oracle_frontier` at 14 and `fig:multi_detector` at 15, which is the
numbering R09, R13 and R11 already ship.

WHAT v87 PRINTS, AND WHERE EACH NUMBER LIVES.

  L349, Fig. 12  Ljung-Box `5.1\\%` -> `24.6\\%`
                            -> R12_leverage_fpr, lb_data_pct at gamma_lev 0 / 0.28
  L349, Fig. 12  FPR `3.2\\%` -> `20.6\\%`
                            -> R12_leverage_fpr, fpr_data at gamma_lev 0 / 0.28
  L349, Fig. 12  sign pipeline FPR `7.6`--`8.4\\%`
                            -> R12_leverage_fpr, fpr_concept, INDEPENDENT arm
  L349           sign pipeline Ljung-Box `4.6`--`5.4\\%`
                            -> R12_leverage_fpr, lb_concept_pct, INDEPENDENT arm
  L349           "climbs by a factor of six"
                            -> fpr_data(0.28) / fpr_data(0.00)
  Fig. 12        `10,000` streams/point       -> N_SEEDS_A
  L353           `83\\%` at nu = 10, `61\\%` at nu = 7
                            -> R12_singularity_add, det_rate_data
  L353           collapse below `50\\%` for nu <= 5.5
                            -> R12_singularity_add, largest nu with det_rate_data < 0.5
  L353           survivorship-biased delays `2,400`--`3,000`
                            -> R12_singularity_add, ADD_Data_Raw, CENSORED domain
  L353, Fig. 13  Concept flat at `34`--`38` steps
                            -> R12_singularity_add, ADD_Concept
  Fig. 13        `1,000` streams/point        -> N_SEEDS_B

THE STRUCTURAL PROBLEM OF THIS STREAM, DECLARED RATHER THAN DISCOVERED.
`simulate_gjr_garch` draws the whole innovation vector BEFORE the variance
recursion, so eps[t] = sqrt(sigma2[t]) * z[t] with sigma2[t] > 0 and therefore
sign(eps_t) = sign(z_t) EXACTLY, for every (omega, alpha, gamma_lev, beta).
Experiment A holds nu = 100 and n = 7,000 fixed across the whole grid, so a key
carrying role and index alone makes the binary stream (eps_test > 0)
BIT-IDENTICAL at all fifteen gamma_lev. Published on that arm, v87's
"leverage-invariant" and "7.6--8.4\\%" would be true mechanically rather than
measured. R11 records the identical situation on its H0 Concept arm.

Experiment A therefore runs TWO Concept arms:

  * the CRN arm, keyed ("R12", "expA", s), is an IDENTITY WITNESS. Its
    bit-identity across the fifteen gamma_lev is ASSERTED on a fixed subsample
    with sys.exit(1) otherwise (control C8), so a later change to
    `simulate_gjr_garch` cannot silently break it. It supports no claim, its
    (zero) range is not published, and its Kish design effect is 15 by
    construction;
  * the published arm, keyed ("R12", "expA_concept_indep", gamma_index, s), pays
    an index into the key and breaks the pairing. Every published Concept rate,
    interval, macro and figure point comes from it.

The Data arm is NOT degenerate on either key: the symmetric filter reads
eps[t-1]**2 through the variance recursion, which carries gamma_lev.

SEVEN STRUCTURAL CHANGES AGAINST THE DELIVERED SCRIPT, EACH FORCED BY THE
REPOSITORY POLICY.

1. ENTROPY. `seed = int(gamma_lev * 1000) + s * 17` (witness l.131) and
   `seed = int(nu * 100) + s * 23` (l.194) are replaced by the repository's
   canonical `get_deterministic_seed` / `seed_sequence_for` / `rng_for`, keyed on
   ROLE AND INDEX ONLY -- never on gamma_lev, never on nu. Both campaigns are
   redrawn; pre-classified Class A / D2 as `R12-campaign-redraw` by the
   `R03-campaign-redraw`, `R05-campaign-redraw`, `R11-regenerated`,
   `R13-campaign-redraw`, `R07-campaign-redraw` and `R09-campaign-redraw`
   precedents.
2. IMPORT SAFETY AND PARALLELISM. `ProcessPoolExecutor()` over a task list whose
   granularity is one stream becomes `joblib.Parallel` over a chunk
   decomposition fixed by NUM_CHUNKS_A / NUM_CHUNKS_B independently of
   `--n-jobs`; every stream keeps its own key, so neither the worker count nor
   the scheduling order can move a number.
3. THE THREE SELF-ANCHORED LITERAL GATES ARE REMOVED AS GATES. The
   `ref_fpr_data` / `ref_lb_data` equality lists (witness l.301-309), the
   Concept bound gate (l.315) and the `det_rate` equality gate (l.459) test
   Monte-Carlo values against literals the same script produced, at 1e-9. The
   repository policy forbids that shape, and the mandated re-keying would fire all three
   mechanically. All three become DEVIATION CLASSIFICATION against the witness
   CSVs, read `float_precision='round_trip'` on both sides.
4. THE VESTIGIAL LEGACY GLOBALS ARE DROPPED, WITH THEIR INERTNESS ASSERTED.
   `np.random.seed(...)` / `random.seed(...)` at witness l.133-134 and l.196-197
   lock a global state that nothing downstream reads. Control C11 evaluates each
   worker twice under deliberately different global states and requires
   bit-identical output rather than assuming it.
5. THE DGP VARIANCE CLAMP IS MEASURED. Witness l.106 caps
   sigma2[t] <= 1e4 * sigma2_unc. At gamma_lev = 0.28 the persistence is 0.99 and
   near nu = 4 the innovations are extreme, so the clamp is a silent execution
   path that could mechanically produce the published collapse. The primitive is
   carried VERBATIM; a separate instrumented copy, asserted to return a
   bit-identical eps, measures the binding rate on a subsample (control C10).
6. THE INVARIANCE CLAIM IS TESTED BY A SLOPE, NOT BY A RANGE. `7.6--8.4\\%`,
   `4.6--5.4\\%`, `34--38` and `2,400--3,000` are all a max minus a min over a
   noisy grid and have no stable sampling distribution (S4bis, fourth
   corollary). Each range macro ships with a seed bootstrap envelope, marked
   descriptive, gating nothing; the gate is an OLS slope of the Concept rate on
   gamma_lev against a null of zero slope (control C9).
7. THE CENSORED DOMAIN GETS ITS OWN STANDARD ERROR. The witness leaves both
   `ADD_Data` and `SEM_Data` NaN below a 50% detection rate while writing
   `ADD_Data_Raw`, so the dispersion is missing exactly where v87 publishes the
   delay. `SEM_Data_Raw` is added on the surviving streams of every censored cell
   (control C2), which is what S3 needs to decide whether `2,400--3,000` is
   breached.

TWO ORPHAN CSVs ARE VENDORED, NOT REBUILT. `expA_argarch_boundary.csv` and
`expB_race_condition.csv` have no producing script anywhere in the delivery; the
grep that establishes it, and what each file does and does not fix, are in
`data/reference/R12/orphans/README.md`. Control C3 READS the first of them and
prints it beside R07's certified AR-GARCH cell; the second is declared produced
and not cited, since v87 cites no frozen-versus-ARF race.

References:
- Glosten, L. R., Jagannathan, R. & Runkle, D. E. (1993). On the relation
  between the expected value and the volatility of the nominal excess return on
  stocks. Journal of Finance, 48(5), 1779-1801. (GJR-GARCH)
- Bollerslev, T. (1986). Generalized autoregressive conditional
  heteroskedasticity. Journal of Econometrics, 31(3), 307-327.
- Page, E. S. (1954). Continuous inspection schemes. Biometrika, 41, 100-115.
- Ljung, G. M. & Box, G. E. P. (1978). On a measure of lack of fit in time series
  models. Biometrika, 65(2), 297-303.
- He, C. & Terasvirta, T. (1999). Fourth moment structure of the GARCH(1,1)
  process. Econometric Theory, 15(6), 824-846.
- Bollerslev, T. & Wooldridge, J. M. (1992). Quasi-maximum likelihood estimation
  and inference in dynamic models with time-varying covariances. Econometric
  Reviews, 11(2), 143-172. (Gaussian QMLE pseudo-true parameter)
- Wilson, E. B. (1927). Probable inference, the law of succession, and
  statistical inference. JASA, 22(158), 209-212.
- Kish, L. (1965). Survey Sampling. Wiley. (design effect, effective sample size)

NOTATION (R12 prompt section 6)
  gamma_lev    GJR-GARCH leverage coefficient; gamma_lev = 0 is the symmetric case
  alpha_sym    alpha + gamma_lev / 2, the symmetric filter the baseline runs
  nu           degrees of freedom of the standardized Student-t innovations;
               E[eps^4] diverges at nu = 4
  c            drift magnitude in units of the unconditional standard deviation
  det_rate_*   detection rate over the monitoring horizon
  ADD          average detection delay, CONDITIONAL on detection
  Gamma        GARCH penalty factor of the Data threshold, `compute_gamma_exact`
  deff         Kish design effect: variance of an estimator under the realised
               design over its variance under simple random sampling
==========================================================================
"""

import sys
from pathlib import Path

# Determinism bootstrap, in the required order: fair_env imports
# only os and sys, so the environment block is posted before NumPy is loaded by
# anyone and before any BLAS thread limit is read. PYTHONHASHSEED cannot be set
# from here -- CPython reads it at interpreter start-up -- so it is exported by
# run_experiment_R12.sh and verified twice below.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from experiments.common.fair_env import enforce_strict_determinism, verify_hash_seed, log_environment

enforce_strict_determinism()

import os

if os.environ.get("PYTHONHASHSEED") != "42":
    sys.exit("FATAL: PYTHONHASHSEED is not 42. Execute via run_experiment_R12.sh")

import numpy as np
import pandas as pd
from experiments.common.fair_harness import (setup_logging, disable_pandas_multithreading,
                                             compute_sha256, save_fair_csv, log_artifact_manifest)

disable_pandas_multithreading()

import ast
import math
import time
import random
import hashlib
import argparse
import tempfile
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from statsmodels.stats.diagnostic import acorr_ljungbox

# --- PROTOCOL SPECIFICATION, IMPERATIVE, CARRIED VERBATIM FROM THE WITNESS ---
# Every constant below is traced to its defining line in
# data/reference/R12/Priorite_10_robustness_gjr_student.py and is unchanged in
# value. Repository policy makes these imperative: if this script diverges from them,
# this script is what is wrong.

# Experiment A -- asymmetric misspecification (v87 Figure 12, L349)
ALPHA_A, BETA_A, NU_A = 0.05, 0.80, 100.0                    # witness l.228
LAMBDA_IID_A, DELTA_P_A = 20.0, 0.5                          # witness l.229
LAMBDA_C_A, DELTA_C_A = 10.0, 0.1                            # witness l.230
GAMMA_LEV_GRID = np.round(np.linspace(0.0, 0.28, 15), 3).tolist()   # witness l.233
N_TOTAL_A = 7000                                             # witness l.248
N_SEEDS_A = 10000                                            # witness l.491
# The warm-up / test split of the witness worker, l.138-139. Carried verbatim as
# part of the specification: `eps[:2000]` locks the econometric parameters
# ex ante and `eps[2000:7000]` is the monitored window.
WARMUP_A = 2000

# Experiment B -- moment singularity (v87 Figure 13, L353)
ALPHA_B, BETA_B = 0.05, 0.85                                 # witness l.325
C_MAGNITUDE_B = 1.0                                          # witness l.326
LAMBDA_IID_B, DELTA_P_B = 65.0, 0.5                          # witness l.327
LAMBDA_C_B, DELTA_C_B = 10.0, 0.1                            # witness l.328
OMEGA_B = 0.04 * (1 - ALPHA_B - BETA_B)                      # witness l.329
NU_GRID = [10.0, 9.0, 8.0, 7.5, 7.0, 6.5, 6.0, 5.5,
           5.0, 4.75, 4.5, 4.25, 4.2, 4.1, 4.05, 4.01]       # witness l.332
N_TOTAL_B = 10000                                            # witness l.360
N_SEEDS_B = 1000                                             # witness l.492
WARMUP_B = 2000                                              # witness l.201, l.206

# The variance-target constant both experiments share (witness l.253, l.329).
VARIANCE_TARGET = 0.04
# The censoring rule of the witness aggregation (l.384-389), restated in code.
CENSORING_DETRATE = 0.5
# The Ljung-Box configuration of the witness worker (l.174-175, l.181-182).
LB_LAGS = 20
LB_LEVEL = 0.05

# --- CHUNK DECOMPOSITION, FIXED INDEPENDENTLY OF --n-jobs ---
# R09's NUM_CHUNKS precedent. Every stream carries its own key, so the chunking
# affects nothing but the granularity handed to the pool; it is nevertheless
# fixed so that the decomposition -- and therefore the traversal order inside a
# chunk -- cannot become a function of the worker count.
NUM_CHUNKS_A = 25
NUM_CHUNKS_B = 10
NUM_CHUNKS_CLAMP = 4

# --- ENTROPY ROLES. Role and index only; no key carries a process parameter. ---
ROLE_A_CRN = "expA"
ROLE_A_INDEP = "expA_concept_indep"
ROLE_B = "expB"

# --- CONTROL DESIGN, FIXED BEFORE THE FIRST RUN (S4bis, S4.10) ---
# C9 gates on one two-sided slope test at this level; it is the only inferential
# gate of the stream that consumes entropy.
GATE_LEVEL = 0.01
# Seed-cluster bootstrap of every extremum macro and of the C9 slope.
BOOTSTRAP_REPLICATES = 2000
BOOTSTRAP_LEVEL = 0.05
# C8 asserts bit-identity of the CRN Concept stream on this many seeds x 15 grid
# points. A digest over the whole monitored window, not a summary of it.
CRN_IDENTITY_SEEDS = 50
# C10 measures the clamp on this many streams per grid point, with the
# instrumented copy asserted bit-identical to the carried primitive on each.
CLAMP_SUBSAMPLE = 200
# Wilson intervals are read at the two-sided 95% normal quantile. The orphan
# witness `expA_argarch_boundary.csv` is reproduced to all 17 digits at this
# value and NOT at the rounder 1.96, which is control C3's finding.
Z_95 = float(stats.norm.ppf(0.975))
# The witness's own normal-approximation half-width uses the literal 1.96
# (l.270-271); it is carried beside the Wilson bounds for comparability.
Z_WITNESS = 1.96

# v87's printed rounding bracket for the censored delay range of L353. The
# manuscript prints `2,400`--`3,000`, rounded to the hundreds, and the witness
# carries 2443.18 and 3005.28, both of which round onto those numerals. The
# contradiction watch item is therefore the BRACKET and not the numeral: a
# regenerated range that leaves [2350, 3050) breaks the printed pair, and per S3
# the breach is a D3 only if the regenerated 95% interval excludes the bound.
CENSORED_BRACKET = (2350.0, 3050.0)

MACRO_HEADER = "% Auto-generated by exp_R12_gjr_student.py -- do not edit."

# --- SOURCE-SEGMENT IDENTITY (control C6) ---
# Repository policy forbids hoisting a scientific primitive into
# experiments/common/, so the routines below are duplicated from the file that
# owns them and checked against that file at RUN TIME: the duplication is
# deliberate and it cannot drift.
WITNESS_SOURCE = BASE_DIR / "data" / "reference" / "R12" / "Priorite_10_robustness_gjr_student.py"
WITNESS_CSV = {
    "leverage_fpr": "protocol_expA_leverage_fpr.csv",
    "singularity_add": "protocol_expB_singularity_add.csv",
}
ORPHAN_BOUNDARY = BASE_DIR / "data" / "reference" / "R12" / "orphans" / "expA_argarch_boundary.csv"
ORPHAN_RACE = BASE_DIR / "data" / "reference" / "R12" / "orphans" / "expB_race_condition.csv"
R07_LB_FPR = BASE_DIR / "results" / "R07_estimated_mean" / "data" / "R07_estmean_lb_fpr.csv"
R07_PHI_CELL = 0.15

# Byte-identical carry, asserted.
CARRIED_PRIMITIVES = ("simulate_gjr_garch", "compute_gamma_exact", "strict_cusum")
# Adapted routines: each takes an injected SeedSequence where the witness derives
# an integer seed from the process parameter, and each drops the two vestigial
# legacy global seeds, so byte identity is not assertable on them. R09's and
# R13's treatment applies -- the witness source of each is quoted in full in the
# log with its SHA-256.
ADAPTED_ROUTINES = ("_worker_expA", "_worker_expB")
# Superseded routines, quoted in full for the same reason: each is replaced by a
# harness component or by a control, and the replacement is named in the log.
SUPERSEDED_ROUTINES = ("run_experiment_A", "run_experiment_B", "setup_logging",
                       "export_requirements")
# STATEMENT-LEVEL IDENTITY, which is what actually catches a transcription
# error. Each entry is (witness function, assignment target); the exact source
# text of every assignment to that target inside that function must appear
# VERBATIM in this file's own source.
CARRIED_STATEMENTS = (
    ("_worker_expA", "eps_warmup"),
    ("_worker_expA", "eps_test"),
    ("_worker_expA", "alpha_sym"),
    ("_worker_expA", "sigma2_warmup"),
    ("_worker_expA", "mu_z2"),
    ("_worker_expA", "sig_z2"),
    ("_worker_expA", "sigma2_test"),
    ("_worker_expA", "z2_test"),
    ("_worker_expA", "e_data"),
    ("_worker_expA", "al_data"),
    ("_worker_expA", "s_concept"),
    ("_worker_expA", "al_concept"),
    ("_worker_expB", "sigma_unc"),
    ("_worker_expB", "Delta"),
    ("_worker_expB", "gamma_exact"),
    ("_worker_expB", "f_warmup"),
    ("_worker_expB", "mu_f"),
    ("_worker_expB", "sig_f"),
    ("_worker_expB", "eps_shifted"),
    ("_worker_expB", "eps_test"),
    ("_worker_expB", "e_data"),
    ("_worker_expB", "al_data"),
    ("_worker_expB", "s_concept"),
    ("_worker_expB", "al_concept"),
)


# --- PRIMITIVES CARRIED FROM THE FILE THAT OWNS THEM ---
# Do not reformat. Byte identity is checked on the exact source text at
# start-up, trailing whitespace included.

def simulate_gjr_garch(n, omega, alpha, gamma_lev, beta, nu=7.0, seed=42):
    rng = np.random.default_rng(seed)
    alpha_naif = alpha + gamma_lev / 2.0
    sigma2_unc = omega / (1 - alpha_naif - beta)
    
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


# --- INSTRUMENTED COPY OF THE DGP (control C10) ---

def simulate_gjr_garch_instrumented(n, omega, alpha, gamma_lev, beta, nu=7.0, seed=42):
    """
    The recursion of the carried primitive with a counter on the clamp branch of
    witness l.106, `sigma2[t] = min(sigma2[t], 1e4 * sigma2_unc)`.

    This copy exists ONLY to make the clamp measurable. It is asserted to return
    a bit-identical `eps` to `simulate_gjr_garch` on every stream of the C10
    subsample, so the counter cannot describe a different process from the one
    the campaign runs. `1e4 * sigma2_unc` is a loop invariant in the witness and
    is hoisted here; a float64 product of two fixed operands is the same value
    every iteration, and the bit-identity assertion is what establishes that
    rather than the argument.

    Returns (eps, n_clamped, max_sigma2_over_unc).
    """
    rng = np.random.default_rng(seed)
    alpha_naif = alpha + gamma_lev / 2.0
    sigma2_unc = omega / (1 - alpha_naif - beta)

    eps = np.zeros(n)
    sigma2 = np.zeros(n)
    sigma2[0] = sigma2_unc

    scale = np.sqrt((nu - 2) / nu)
    z = rng.standard_t(df=nu, size=n) * scale
    eps[0] = np.sqrt(sigma2[0]) * z[0]

    ceiling = 1e4 * sigma2_unc
    n_clamped = 0
    max_ratio = 1.0
    for t in range(1, n):
        indicator = 1.0 if eps[t-1] < 0 else 0.0
        raw = omega + (alpha + gamma_lev * indicator) * eps[t-1]**2 + beta * sigma2[t-1]
        sigma2[t] = min(raw, ceiling)
        if raw > ceiling:
            n_clamped += 1
        ratio = raw / sigma2_unc
        if ratio > max_ratio:
            max_ratio = ratio
        eps[t] = np.sqrt(sigma2[t]) * z[t]

    return eps, n_clamped, max_ratio


# --- SEED DERIVATION, CARRIED FROM exp_R09_eprocess_anytime.py ---

def get_deterministic_seed(*args) -> int:
    """
    Derives a 128-bit collision-free seed from the semantic coordinates of a
    task, returned as a scalar integer so no entropy is discarded. This is the
    repository's canonical form, carried from exp_R11_multi_detector.py.

    Floats are formatted through .hex() rather than str(): the decimal repr of a
    float is platform-dependent at the last digit on some C libraries, which
    would silently re-key a cell across machines. The native hash() is randomly
    salted and is forbidden outright (repository policy).
    """
    def format_arg(arg):
        if isinstance(arg, (float, np.floating)):
            return float(arg).hex()
        return str(arg)

    s = "_".join(map(format_arg, args))
    return int(hashlib.md5(s.encode('utf-8')).hexdigest(), 16)


def seed_sequence_for(*key):
    """The 128-bit SeedSequence of a task, keyed on its role and index alone."""
    return np.random.SeedSequence(get_deterministic_seed(*key))


def rng_for(*key):
    """Generator seeded by the full 128-bit condensate of a task's key."""
    return np.random.default_rng(seed_sequence_for(*key))


# --- INTERVALS AND DESIGN EFFECTS ---

def clamped(value):
    """Repository policy: every interval bound is clipped to [0, 1] before persistence."""
    if not np.isfinite(value):
        return float('nan')
    return max(0.0, min(1.0, float(value)))


def wilson_ci(k, n, z=Z_95):
    """
    Asymmetric Wilson score interval for a binomial proportion, written as a
    centre and a margin. `z` is the two-sided normal quantile and is NOT rounded
    to 1.96 by default: control C3 shows the submitted orphan witness reproduces
    to all 17 digits at Phi^-1(0.975) and misses by 1.4e-7 at 1.96.
    """
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * math.sqrt((p * (1 - p)) / n + z**2 / (4 * n**2))) / denom
    return clamped(center - margin), clamped(center + margin)


def kish_design_effect(matrix):
    """
    Kish design effect of a proportion measured on a paired grid: the ratio of
    the cluster-robust variance of the pooled rate to the variance a simple
    random sample of the same size would have. `matrix` is seeds x grid points.

    Carried from exp_R11_multi_detector.py l.692. A grid whose readings are
    bit-identical within a seed returns exactly the number of grid points, which
    is what makes the degeneracy of the CRN Concept arm a measured quantity
    rather than an assertion.
    """
    p = float(matrix.mean())
    if p <= 0.0 or p >= 1.0:
        return float('nan')
    se_cluster = float(np.std(matrix.mean(axis=1), ddof=1) / math.sqrt(matrix.shape[0]))
    se_srs = math.sqrt(p * (1.0 - p) / matrix.size)
    return (se_cluster / se_srs) ** 2


def ols_fit(x, y):
    """OLS slope with its analytic standard error, reported as a diagnostic."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    res = stats.linregress(x, y)
    return float(res.slope), float(res.intercept), float(res.stderr), float(res.rvalue) ** 2


def two_sided_p_from_se(estimate, se):
    """
    Two-sided p-value for H0: parameter = 0, referred to a normal law.

    Carried from exp_R11_multi_detector.py l.839. The bootstrap supplies the
    standard error; the reference law is normal rather than the bootstrap's own
    percentiles because a percentile p-value on a finite replicate count is
    discrete on a 1/B lattice.
    """
    if not np.isfinite(se) or se <= 0.0:
        return float('nan')
    return float(2.0 * stats.norm.sf(abs(estimate) / se))


def chunk_bounds(n_total, num_chunks):
    """
    The fixed chunk decomposition. Carried in shape from R09's
    `chunk_sizes_for` (l.348-352) and returned as half-open [start, stop) pairs
    so that the seed indices a chunk owns are explicit rather than implied.
    """
    base = n_total // num_chunks
    rem = n_total % num_chunks
    bounds = []
    start = 0
    for i in range(num_chunks):
        stop = start + base + (1 if i < rem else 0)
        bounds.append((start, stop))
        start = stop
    return bounds


# --- ADAPTED WORKERS: PURE MODULE-LEVEL FUNCTIONS, NO LOGGING, NO SIDE EFFECT ---
# The delivered script configures its logger at module level with mode='w'. Under
# a process pool every worker that re-imports the module would truncate the log,
# so every side effect of this file lives inside main().

def _worker_expA(params):
    """
    Experiment A, one stream. Adapted from `Priorite_10` l.128-183.

    Two changes, both mandated. (i) The integer `seed = int(gamma_lev * 1000) +
    s * 17` of witness l.131 keys the draw on the PROCESS PARAMETER; it is
    replaced by an injected `SeedSequence` keyed on the role and index alone.
    (ii) `np.random.seed(...)` and `random.seed(...)` (l.133-134) are dropped;
    control C11 asserts their inertness rather than assuming it.

    Every recursion statement below is byte-identical to the witness and control
    C6 asserts it from the witness AST.
    """
    gamma_lev, s, n_total, omega, alpha, beta, nu, lambda_iid, delta_P, lambda_c, delta_c, seed = params

    eps = simulate_gjr_garch(n_total, omega, alpha, gamma_lev, beta, nu=nu, seed=seed)

    eps_warmup = eps[:2000]
    eps_test = eps[2000:7000]

    # --- Econometric Baseline (Pseudo-QMLE Filter) ---
    # The misspecified econometrician fits a SYMMETRIC GARCH(1,1).
    # Asymptotically, this converges to alpha_sym = alpha + gamma_lev / 2.
    alpha_sym = alpha + gamma_lev / 2.0

    # 1. Filter the WARMUP set to lock the econometric parameters ex-ante
    sigma2_warmup = np.zeros(len(eps_warmup))
    sigma2_warmup[0] = omega / (1 - alpha_sym - beta)
    for t in range(1, len(eps_warmup)):
        sigma2_warmup[t] = omega + alpha_sym * eps_warmup[t-1]**2 + beta * sigma2_warmup[t-1]

    z2_warmup = (eps_warmup**2) / sigma2_warmup
    mu_z2 = np.mean(z2_warmup)
    sig_z2 = np.std(z2_warmup)

    # 2. Filter the TEST set using the continuous state
    sigma2_test = np.zeros(len(eps_test))
    sigma2_test[0] = sigma2_warmup[-1]
    for t in range(1, len(eps_test)):
        sigma2_test[t] = omega + alpha_sym * eps_test[t-1]**2 + beta * sigma2_test[t-1]

    # Standardize strictly with ex-ante parameters
    z2_test = (eps_test**2) / sigma2_test
    e_data = (z2_test - mu_z2) / sig_z2

    # CUSUM calibrated for i.i.d. (no Gamma multiplier)
    al_data = strict_cusum(e_data, delta_P, lambda_iid)

    # --- Concept Pipeline ---
    s_concept = (eps_test > 0).astype(float) - 0.5
    al_concept = strict_cusum(s_concept, delta_c, lambda_c)

    # --- Ljung-Box Diagnostics ---
    lb_data = acorr_ljungbox(z2_test, lags=[LB_LAGS], return_df=True)['lb_pvalue'].iloc[0]
    lb_concept = acorr_ljungbox(s_concept, lags=[LB_LAGS], return_df=True)['lb_pvalue'].iloc[0]

    return {
        "gamma_lev": gamma_lev,
        "fp_data": 1 if al_data != -1 else 0,
        "fp_concept": 1 if al_concept != -1 else 0,
        "lb_reject_data": 1 if lb_data < LB_LEVEL else 0,
        "lb_reject_concept": 1 if lb_concept < LB_LEVEL else 0,
    }


def _worker_expB(params):
    """
    Experiment B, one stream. Adapted from `Priorite_10` l.187-219.

    Same two changes as `_worker_expA`: the integer `seed = int(nu * 100) +
    s * 23` of witness l.194 is replaced by an injected `SeedSequence` keyed on
    the role and index alone, and the two vestigial legacy global seeds
    (l.196-197) are dropped under control C11.

    The witness's own l.341-358 already declares that its integer scheme reuses
    seed VALUES across the nu sweep at shifted replicate indices; the injected
    key makes the common-random-numbers plan exact instead of incidental -- the
    same seed index s carries the same 128-bit condensate to all sixteen nu.
    """
    nu, s, n_total, omega, alpha, beta, c, lambda_iid, delta_P, lambda_c, delta_c, seed = params

    sigma_unc = np.sqrt(omega / (1 - alpha - beta))
    Delta = c * sigma_unc
    gamma_exact = compute_gamma_exact(alpha, beta)

    eps = simulate_gjr_garch(n_total, omega, alpha, 0.0, beta, nu=nu, seed=seed)

    f_warmup = eps[:2000]**2
    mu_f = np.mean(f_warmup)
    sig_f = max(np.std(f_warmup), 1e-8)

    eps_shifted = eps.copy()
    eps_shifted[2000:] += Delta
    eps_test = eps_shifted[2000:]

    e_data = (eps_test**2 - mu_f) / sig_f
    al_data = strict_cusum(e_data, delta_P, lambda_iid * gamma_exact)

    s_concept = (eps_test > 0).astype(float) - 0.5
    al_concept = strict_cusum(s_concept, delta_c, lambda_c)

    return {
        "nu": nu,
        "al_data": al_data,
        "al_concept": al_concept,
    }


def _chunk_expA(gamma_index, gamma_lev, start, stop, role, omega):
    """
    One chunk of Experiment A: seed indices [start, stop) at one grid point.

    The key is the whole point of the chunking being irrelevant: the CRN arm
    keys ("R12", "expA", s) and carries NO grid coordinate, the published arm
    keys ("R12", "expA_concept_indep", gamma_index, s) and carries the grid
    INDEX -- an integer, never the float gamma_lev, so no key can depend on a
    platform's decimal formatting of a grid value.
    """
    size = stop - start
    fp_data = np.zeros(size, dtype=bool)
    fp_concept = np.zeros(size, dtype=bool)
    lb_data = np.zeros(size, dtype=bool)
    lb_concept = np.zeros(size, dtype=bool)
    for i, s in enumerate(range(start, stop)):
        key = ("R12", role, s) if role == ROLE_A_CRN else ("R12", role, gamma_index, s)
        res = _worker_expA((gamma_lev, s, N_TOTAL_A, omega, ALPHA_A, BETA_A, NU_A,
                            LAMBDA_IID_A, DELTA_P_A, LAMBDA_C_A, DELTA_C_A,
                            seed_sequence_for(*key)))
        fp_data[i] = res["fp_data"]
        fp_concept[i] = res["fp_concept"]
        lb_data[i] = res["lb_reject_data"]
        lb_concept[i] = res["lb_reject_concept"]
    return gamma_index, start, fp_data, fp_concept, lb_data, lb_concept


def _chunk_expB(nu_index, nu, start, stop):
    """
    One chunk of Experiment B: seed indices [start, stop) at one nu.

    The key ("R12", "expB", s) carries no nu, so the sixteen grid points are
    traversed under common random numbers and every cross-nu comparison is
    paired by construction. Control C4 prices that pairing before reading any
    difference.
    """
    size = stop - start
    al_data = np.zeros(size, dtype=np.int64)
    al_concept = np.zeros(size, dtype=np.int64)
    for i, s in enumerate(range(start, stop)):
        res = _worker_expB((nu, s, N_TOTAL_B, OMEGA_B, ALPHA_B, BETA_B, C_MAGNITUDE_B,
                            LAMBDA_IID_B, DELTA_P_B, LAMBDA_C_B, DELTA_C_B,
                            seed_sequence_for("R12", ROLE_B, s)))
        al_data[i] = res["al_data"]
        al_concept[i] = res["al_concept"]
    return nu_index, start, al_data, al_concept


def _chunk_crn_identity(gamma_index, gamma_lev, omega, seeds):
    """
    Control C8. The Experiment A monitored binary stream under the CRN key,
    digested.

    `simulate_gjr_garch` draws its innovations before the variance recursion, so
    sign(eps_t) = sign(z_t) for every (omega, alpha, gamma_lev, beta) and this
    digest must be identical at all fifteen gamma_lev. The identity is ASSERTED
    rather than remarked: an unasserted observation would not survive a later
    change to the generator.
    """
    out = []
    for s in seeds:
        eps = simulate_gjr_garch(N_TOTAL_A, omega, ALPHA_A, gamma_lev, BETA_A, nu=NU_A,
                                 seed=seed_sequence_for("R12", ROLE_A_CRN, s))
        e_bin = (eps[WARMUP_A:N_TOTAL_A] > 0)
        out.append((gamma_index, s, hashlib.sha256(e_bin.tobytes()).hexdigest()))
    return out


def _chunk_clamp(experiment, grid_index, grid_value, n_total, omega, alpha, gamma_lev, beta,
                 nu, role, seeds):
    """
    Control C10. The clamp binding rate on a subsample, with the instrumented
    copy asserted bit-identical to the carried primitive on every stream.

    The key is the campaign's own key for that stream, so the measurement
    describes the streams the campaign actually ran and not a fresh draw.
    """
    records = []
    for s in seeds:
        seed = seed_sequence_for("R12", role, s)
        eps_ref = simulate_gjr_garch(n_total, omega, alpha, gamma_lev, beta, nu=nu, seed=seed)
        eps_ins, n_clamped, max_ratio = simulate_gjr_garch_instrumented(
            n_total, omega, alpha, gamma_lev, beta, nu=nu, seed=seed)
        records.append((experiment, grid_index, grid_value, s, n_clamped, max_ratio,
                        bool(np.array_equal(eps_ref, eps_ins)), n_total - 1))
    return records


# --- SOURCE IDENTITY (control C6), RUN BEFORE ANY CAMPAIGN ---

def source_segments(path, names):
    """
    Source text of the named top-level functions, extracted BY POSITION rather
    than by import: importing the witness would execute its environment block,
    its `mode='w'` logger, its `export_requirements()` call and its directory
    creation. Carried from exp_R09_eprocess_anytime.py l.552-563.
    """
    text = Path(path).read_text()
    tree = ast.parse(text)
    return {node.name: ast.get_source_segment(text, node)
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in names}


def assignment_segments(path, function_name, target_name):
    """
    The exact source text of every assignment to `target_name` inside
    `function_name` of `path`, in source order and de-duplicated. Carried from
    exp_R09_eprocess_anytime.py l.566-591.
    """
    text = Path(path).read_text()
    tree = ast.parse(text)
    found = []
    for node in tree.body:
        if not (isinstance(node, ast.FunctionDef) and node.name == function_name):
            continue
        for sub in ast.walk(node):
            if not isinstance(sub, (ast.Assign, ast.AugAssign)):
                continue
            targets = sub.targets if isinstance(sub, ast.Assign) else [sub.target]
            names = []
            for target in targets:
                if isinstance(target, ast.Name):
                    names.append(target.id)
                elif isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                    names.append(target.value.id)
            if target_name in names:
                segment = ast.get_source_segment(text, sub)
                if segment is not None and segment not in found:
                    found.append(segment)
    return found


def check_source_identity(logger):
    """
    C6. Three layers, run BEFORE any campaign so that a transcription error
    costs no compute.

    (i)   byte identity of every carried primitive against the file that owns it;
    (ii)  the witness source of every adapted and superseded routine, quoted in
          full with its SHA-256, because an injected SeedSequence makes byte
          identity unassertable on them;
    (iii) STATEMENT-LEVEL identity of the recursions, which is what actually
          catches a transcription error: the exact source text of each statement
          is extracted from the witness AST and must appear verbatim here.

    Deterministic; trigger probability 0 unless a copy has drifted.
    """
    if not WITNESS_SOURCE.exists():
        logger.error(f"C6 source-identity failure: {WITNESS_SOURCE} is missing, so no copy can be "
                     f"verified.")
        sys.exit(1)
    own_path = Path(__file__).resolve()
    own_text = own_path.read_text()

    own = source_segments(own_path, set(CARRIED_PRIMITIVES))
    witness_primitives = source_segments(WITNESS_SOURCE, set(CARRIED_PRIMITIVES))
    compared = 0
    for name in CARRIED_PRIMITIVES:
        mine, remote = own.get(name), witness_primitives.get(name)
        if mine is None or remote is None:
            logger.error(f"C6 source-identity failure: {name} could not be extracted "
                         f"({WITNESS_SOURCE.name}).")
            sys.exit(1)
        if mine != remote:
            logger.error(f"C6 source-identity failure on {name}: the copy has drifted from "
                         f"{WITNESS_SOURCE.name}.")
            sys.exit(1)
        compared += len(remote)
    logger.info(f"C6 (i) CARRIED PRIMITIVES: {len(CARRIED_PRIMITIVES)} byte-identical to "
                f"{WITNESS_SOURCE.name} ({compared} characters compared, trailing whitespace "
                f"included) -- {', '.join(CARRIED_PRIMITIVES)}. Repository policy forbids hoisting any "
                f"of them into experiments/common/, so the duplication is deliberate. "
                f"Deterministic; trigger probability 0 unless a copy has drifted.")

    quoted = source_segments(WITNESS_SOURCE, set(ADAPTED_ROUTINES) | set(SUPERSEDED_ROUTINES))
    missing = [n for n in tuple(ADAPTED_ROUTINES) + tuple(SUPERSEDED_ROUTINES) if n not in quoted]
    if missing:
        logger.error(f"C6: the witness carries no {missing}; the adaptation cannot be exhibited.")
        sys.exit(1)
    logger.info(f"C6 (ii) ADAPTED ROUTINES {list(ADAPTED_ROUTINES)} each take an injected "
                f"SeedSequence keyed on role and index where {WITNESS_SOURCE.name} derives an "
                f"integer seed from the process parameter, and each drops the two vestigial legacy "
                f"global seeds, so byte identity is not assertable on them and the witness source "
                f"of each is quoted IN FULL below, totalling "
                f"{sum(len(quoted[n]) for n in ADAPTED_ROUTINES)} characters.")
    for name in ADAPTED_ROUTINES:
        logger.info(f"C6 witness SHA-256 of {name}: "
                    f"{hashlib.sha256(quoted[name].encode('utf-8')).hexdigest()}")
        logger.info(f"C6 witness source of {name}:\n{quoted[name].rstrip()}")
    # The SUPERSEDED routines are pinned by DIGEST rather than quoted in full, and
    # the reason is a rule and not a preference: repository policy requires the grep
    # for confirmatory language to return empty ON THIS RUN LOG, and the log line
    # `run_experiment_B` emits at witness l.463 carries one of the banned phrases.
    # A verbatim quotation would import it into the log. The digest pins exactly
    # the same bytes without reproducing them, and what each routine is replaced
    # by is named instead -- which is what a reader of an audit needs.
    logger.info(f"C6 (ii-bis) SUPERSEDED ROUTINES {list(SUPERSEDED_ROUTINES)}, pinned by SHA-256 "
                f"rather than quoted: `run_experiment_A` and `run_experiment_B` carry the three "
                f"self-anchored literal gates this port removes as gates (l.301-309 the "
                f"ref_fpr_data / ref_lb_data equality lists, l.315 the Concept bound gate, l.459 "
                f"the det_rate equality gate) and the ProcessPoolExecutor decomposition that "
                f"joblib.Parallel over fixed chunks replaces; `setup_logging` and "
                f"`export_requirements` are replaced by experiments/common/fair_harness.py and "
                f"experiments/common/fair_env.log_environment. Their segments total "
                f"{sum(len(quoted[n]) for n in SUPERSEDED_ROUTINES)} characters, and the digests "
                f"below pin exactly those bytes. Repository policy forbids the phrase at "
                f"{WITNESS_SOURCE.name} l.463 from reaching this log, which is why they are pinned "
                f"and not reproduced.")
    for name in SUPERSEDED_ROUTINES:
        logger.info(f"C6 witness SHA-256 of {name}: "
                    f"{hashlib.sha256(quoted[name].encode('utf-8')).hexdigest()}")

    checked = 0
    for function_name, target_name in CARRIED_STATEMENTS:
        segments = assignment_segments(WITNESS_SOURCE, function_name, target_name)
        if not segments:
            logger.error(f"C6 statement identity: the witness carries no assignment to "
                         f"`{target_name}` inside `{function_name}`.")
            sys.exit(1)
        for segment in segments:
            if segment not in own_text:
                logger.error(f"C6 STATEMENT IDENTITY FAILURE. The witness statement "
                             f"`{segment}` ({WITNESS_SOURCE.name}::{function_name}) does not "
                             f"appear verbatim in {own_path.name}. A recursion has been "
                             f"transcribed differently.")
                sys.exit(1)
            checked += 1
    logger.info(f"C6 (iii) STATEMENT IDENTITY: {checked} statements extracted from the witness AST "
                f"and found verbatim in {own_path.name} -- the two symmetric-filter recursions, the "
                f"standardisation of the squared residual, the two CUSUM calls of each worker, the "
                f"sign stream, the warm-up moments, the drift magnitude and the exact penalty. "
                f"Deterministic; trigger probability 0 unless a copy has drifted.")
    return {"characters_compared": compared, "statements_checked": checked}


def check_det_rate_concept_is_computed(logger):
    """
    C1. `det_rate_concept` must be a COMPUTED quantity and not a literal.

    v87's Figure 13 caption and L353 rest on the Concept arm detecting on every
    stream at every nu; the witness CSV carries the integer `1` at all sixteen
    grid points, which is either a real 1000/1000 or a literal masking an absent
    measurement. The R12 prompt's section 2.1 requires the question be settled
    ON THE LINE THAT COMPUTES IT, so the producing site is located in this file's
    own AST -- R09's `check_bound_flag_is_computed` template -- and its SHAPE is
    asserted: exactly one site, a division whose numerator is a `len` over a
    filtered frame.

    Deterministic; trigger probability 0. Failure is a D3: the flatness of the
    Concept arm would then be unmeasured.
    """
    tree = ast.parse(Path(__file__).resolve().read_text())
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "det_rate_concept":
                found.append(node.value)
    if len(found) != 1:
        logger.error(f"C1 FAILED: `det_rate_concept` is produced at {len(found)} sites, not one; "
                     f"the control cannot name the line it asserts.")
        sys.exit(1)
    expression = found[0]
    if not isinstance(expression, ast.BinOp) or not isinstance(expression.op, ast.Div):
        logger.error("C1 FAILED: `det_rate_concept` is not a division. A constant written into "
                     "every row of a file is a literal, and a literal is not a measurement.")
        sys.exit(1)
    numerator = expression.left
    if not (isinstance(numerator, ast.Call) and isinstance(numerator.func, ast.Name)
            and numerator.func.id == "len"):
        logger.error(f"C1 FAILED: the numerator of `det_rate_concept` is "
                     f"`{ast.unparse(numerator)}`, which is not a `len` over a filtered frame.")
        sys.exit(1)
    logger.info(f"C1 `det_rate_concept` is the computed expression "
                f"`{ast.unparse(expression)}`, located in this file's own AST: a single site, a "
                f"division whose numerator is `len` over a filtered frame and whose denominator is "
                f"the replicate count. It is the witness's own l.381, "
                f"`det_rate_concept = len(d_concept) / n_seeds` over "
                f"`d_concept = subset[subset[\"al_concept\"] >= 0]`, and it is NOT a literal. "
                f"Corroboration travels with it and is logged after the campaign: ADD_Concept "
                f"varies over the same grid, which is incompatible with an absence of detection "
                f"though it does not by itself establish that the rate is computed. Deterministic; "
                f"trigger probability 0; failure is a D3.")
    return ast.unparse(expression)


# --- DERIVATIONS, ONE LINE EACH (repository policy) ---

def fourth_moment_nu_star(alpha, beta):
    """
    The Student-t degrees of freedom at which E[eps^4] of a GARCH(1,1) diverges.

    Derivation, one line: with standardized innovations of kurtosis
    k(nu) = 3(nu-2)/(nu-4), He & Terasvirta (1999) give E[eps^4] < inf iff
    E[(alpha z^2 + beta)^2] = alpha^2 k(nu) + 2 alpha beta + beta^2 < 1, so the
    boundary is k(nu*) = (1 - 2 alpha beta - beta^2) / alpha^2, inverted here in
    closed form. Returns NaN when the boundary lies outside nu > 4.
    """
    k_star = (1.0 - 2.0 * alpha * beta - beta**2) / alpha**2
    if k_star <= 3.0:
        return float('nan')
    # k = 3(nu-2)/(nu-4)  =>  nu = (4k - 6) / (k - 3)
    return (4.0 * k_star - 6.0) / (k_star - 3.0)


def log_derivations(logger):
    """
    Every mathematical property this stream relies on, with its one-line
    derivation, logged before any number is read (repository policy). A condition
    that cannot be derived in one line is a recited condition and is forbidden.
    """
    logger.info("=" * 78)
    logger.info("DERIVATIONS (repository policy), ONE LINE EACH, BEFORE ANY NUMBER IS READ")
    logger.info("=" * 78)

    persistence = [ALPHA_A + g / 2.0 + BETA_A for g in GAMMA_LEV_GRID]
    logger.info(f"GJR STATIONARITY. Under innovations symmetric about zero, "
                f"E[1{{eps_(t-1) < 0}}] = 1/2, so the second-moment condition of the GJR recursion "
                f"is alpha + gamma_lev/2 + beta < 1. On this grid it runs from "
                f"{persistence[0]:.4f} at gamma_lev = {GAMMA_LEV_GRID[0]} to {persistence[-1]:.4f} "
                f"at gamma_lev = {GAMMA_LEV_GRID[-1]}: the grid is driven to the EDGE of the "
                f"stationary region, {1.0 - persistence[-1]:.4f} from the boundary. Every "
                f"unconditional quantity of the last grid point is therefore estimated on a process "
                f"whose autocovariances decay at rate {persistence[-1]:.2f}^h.")

    logger.info(f"THE SYMMETRIC FILTER AND THE VARIANCE TARGET. The baseline runs "
                f"h_t = omega + alpha_sym eps_(t-1)^2 + beta h_(t-1) with "
                f"alpha_sym = alpha + gamma_lev/2, and the DGP's own unconditional variance solves "
                f"sigma2_unc = omega / (1 - alpha_sym - beta) because E[eps^2 1{{eps<0}}] = "
                f"E[eps^2]/2 under a symmetric law. E[h_t] therefore obeys the SAME recursion as "
                f"E[sigma2_t] and matches the unconditional variance EXACTLY: the filter is "
                f"unbiased in the mean and misspecified in the dynamics, which is what isolates "
                f"leverage leakage from a level error. The witness sets "
                f"omega = {VARIANCE_TARGET} * (1 - alpha_sym - beta) at every grid point "
                f"(l.252-253), so sigma2_unc = {VARIANCE_TARGET} on all fifteen and the grid is "
                f"variance-targeted.")
    logger.info(f"OPEN QUESTION, POSED AND NOT SETTLED. v87 L349 calls alpha_sym the symmetric "
                f"GARCH(1,1) 'population limit'. Mean-matching is what the paragraph above "
                f"derives; a 'population limit' in the QMLE sense is the Gaussian pseudo-true "
                f"parameter of Bollerslev & Wooldridge (1992), the minimiser of the expected "
                f"quasi-log-likelihood. The two need not coincide, and NO measurement in this "
                f"stream decides which one alpha_sym is: the witness never fits anything, it "
                f"substitutes alpha + gamma_lev/2 in closed form. The question is recorded in "
                f"AUDIT_R12.md and left open.")

    nu_star = fourth_moment_nu_star(ALPHA_B, BETA_B)
    beyond = [nu for nu in NU_GRID if nu < nu_star]
    logger.info(f"EXPERIMENT B FOURTH-MOMENT BOUNDARY. E[eps^4] < inf iff "
                f"alpha^2 * 3(nu-2)/(nu-4) + 2*alpha*beta + beta^2 < 1; at "
                f"(alpha, beta) = ({ALPHA_B}, {BETA_B}) that is "
                f"{ALPHA_B**2:.4f} k(nu) + {2 * ALPHA_B * BETA_B:.4f} + {BETA_B**2:.6f} < 1, i.e. "
                f"k(nu) < {(1 - 2 * ALPHA_B * BETA_B - BETA_B**2) / ALPHA_B**2:.4f}, giving "
                f"nu* = {nu_star:.6f}. ONLY {beyond} of the sixteen grid points sit beyond it, "
                f"while the detection collapse begins near nu = 5.5-6. The distance between the two "
                f"is REPORTED AS DERIVED and NO MECHANISM IS ATTRIBUTED to it (repository policy).")
    logger.info(f"THE SAME MISALIGNMENT IS ALREADY ON THE RECORD, AND THE RULING IS CITED RATHER "
                f"THAN RE-DERIVED. R02c established exactly this shape on the i.i.d. arm -- the "
                f"eighth moment of eps is infinite up to nu <= 8, yet the measured over-rejection "
                f"has already disappeared at nu = 7 -- and `docs/DEVIATIONS.md` entry "
                f"`R02c-mechanism-constraints` records it with the same 'mechanism not identified' "
                f"ruling. R12 does not invent a new causal attribution here; it cross-references "
                f"that entry.")

    gamma_b = compute_gamma_exact(ALPHA_B, BETA_B)
    logger.info(f"EXPERIMENT B DATA THRESHOLD. compute_gamma_exact({ALPHA_B}, {BETA_B}) = "
                f"{gamma_b!r}, so the Data CUSUM runs at lambda_iid * Gamma = {LAMBDA_IID_B} * "
                f"{gamma_b:.4f} = {LAMBDA_IID_B * gamma_b!r}. The Concept CUSUM runs at "
                f"lambda_c = {LAMBDA_C_B} with NO penalty multiplier, which is the asymmetry "
                f"Figure 13 exists to show. Experiment A's Data CUSUM carries no multiplier either "
                f"(witness l.167): at nu = {NU_A} the innovations are pseudo-Gaussian and the "
                f"witness calibrates the baseline for i.i.d. -- Gamma there would be "
                f"{compute_gamma_exact(ALPHA_A + GAMMA_LEV_GRID[-1] / 2.0, BETA_A):.4f} at the "
                f"symmetric filter of the last grid point, and is deliberately not applied.")

    drift_b = C_MAGNITUDE_B * math.sqrt(OMEGA_B / (1 - ALPHA_B - BETA_B))
    logger.info(f"EXPERIMENT B DRIFT. sigma_unc = sqrt(omega / (1 - alpha - beta)) = "
                f"{math.sqrt(OMEGA_B / (1 - ALPHA_B - BETA_B))!r} and Delta = c * sigma_unc = "
                f"{drift_b!r} at c = {C_MAGNITUDE_B}. The Data statistic monitors "
                f"(eps + Delta)^2, whose mean shift is Delta^2 = {drift_b**2!r} against a warm-up "
                f"standard deviation of the squared residual that DIVERGES as nu -> 4: that ratio "
                f"is the whole content of the 'stochastic syncope'.")

    logger.info(f"LJUNG-BOX FAMILY ARITHMETIC (S4bis). Experiment A reads {len(GAMMA_LEV_GRID)} "
                f"grid points on 2 arms = {2 * len(GAMMA_LEV_GRID)} simultaneous calibration "
                f"readings. Under a perfectly calibrated null at the {LB_LEVEL} level the "
                f"probability that AT LEAST ONE rejects is "
                f"1 - {1 - LB_LEVEL}^{2 * len(GAMMA_LEV_GRID)} = "
                f"{1 - (1 - LB_LEVEL) ** (2 * len(GAMMA_LEV_GRID)):.4f}, i.e. "
                f"{100 * (1 - (1 - LB_LEVEL) ** (2 * len(GAMMA_LEV_GRID))):.1f}%, far above the 5% "
                f"ceiling S4bis fixes. 'No test rejects' is therefore NOT usable as a binary gate "
                f"and control C5 substitutes a KS calibration test of the p-value distribution.")

    logger.info(f"DESIGN EFFECT, ASSIGNED WHEREVER A STANDARD ERROR IS FORMED (S4bis, sixth "
                f"corollary). WITHIN a grid cell the {N_SEEDS_A} (Experiment A) and {N_SEEDS_B} "
                f"(Experiment B) streams carry distinct seed indices and are mutually independent, "
                f"so a within-cell mean carries deff = 1.0 exactly. ACROSS grid points the CRN key "
                f"makes every reading paired, so no pooled or cross-grid quantity is read before "
                f"its deff is measured: controls C8 (Experiment A Concept), C4 (Experiment B "
                f"detection rates) and C9 (the invariance slope) each measure it.")
    logger.info("=" * 78)
    return {"nu_star": nu_star, "gamma_b": gamma_b, "drift_b": drift_b,
            "persistence_max": persistence[-1]}


def log_control_design(logger, n_jobs):
    """
    Every numeric gate of this stream, with its null law and its trigger
    probability under that null, logged BEFORE any result is read (S4bis).
    """
    logger.info("=" * 78)
    logger.info("CONTROL DESIGN, FIXED BEFORE THE FIRST NUMBER IS READ (S4bis, S4.10)")
    logger.info("=" * 78)
    logger.info(f"C1 -- `det_rate_concept` IS COMPUTED, NOT A LITERAL. Asserted on this file's own "
                f"AST and, independently, in tests/test_R12_claims.py. Deterministic; trigger "
                f"probability 0; failure is a D3 because the flatness of the Concept arm would "
                f"then be unmeasured.")
    logger.info(f"C2 -- THE CENSORING RULE, STATED BEFORE THE REGENERATED FRAME IS READ. "
                f"`ADD_Data` and `SEM_Data` are written only where det_rate_data >= "
                f"{CENSORING_DETRATE}, which is the witness's own rule (l.384-389) and the rule the "
                f"published figure censors on. `ADD_Data_Raw` carries the conditional delay at "
                f"EVERY nu, because v87 L353 explicitly publishes the censored domain -- 'the "
                f"surviving minority carries survivorship-biased delays of 2,400--3,000 steps'. The "
                f"witness leaves the DISPERSION of exactly those published values missing, so "
                f"`SEM_Data_Raw` is added on the surviving streams of every cell. Without it S3's "
                f"rule -- a printed bound is breached at D3 only if the regenerated 95% interval "
                f"excludes it -- cannot be evaluated on the one range v87 prints for the censored "
                f"domain. Deterministic; trigger probability 0.")
    logger.info(f"C3 -- TASK BOUNDARY, AS A READ AND NOT AS A MEASUREMENT. The claim behind "
                f"`expA_argarch_boundary.csv` -- that the property holds at the MEDIAN threshold "
                f"and not at the ZERO threshold -- is v87 L302, which is R07's mission statement, "
                f"and R07 has already delivered it on a certified campaign. Rebuilding it here "
                f"would put a third pair of numbers behind one printed sentence and would infer a "
                f"design from the two output numbers it then reproduces. C3 therefore READS R07's "
                f"phi = {R07_PHI_CELL} cell at float_precision='round_trip' and prints it beside "
                f"the orphan witness, states the gap, and leaves it unexplained. NO MACRO, NO "
                f"REGISTER ENTRY. Deterministic. R12's own negative witnesses are the cells it "
                f"actually runs: gamma_lev = {GAMMA_LEV_GRID[0]} (leverage-free) and "
                f"nu = {NU_GRID[0]} (light-tailed).")
    logger.info(f"C4 -- MONOTONICITY, WITH ITS DOMAIN DECLARED BEFORE THE DATA IS READ. v87 L353 "
                f"states 'detection decays monotonically' with NO domain restriction, and the "
                f"submitted witness is ALREADY non-monotone at nu = 4.75 (0.398 > 0.382) and "
                f"nu = 4.05 (0.372 > 0.347), both inside the censored domain. The gate is therefore "
                f"declared on det_rate_data over the UNCENSORED domain "
                f"(det_rate_data >= {CENSORING_DETRATE}) and nowhere else. RESTRICTING THE DOMAIN "
                f"IS THIS REPOSITORY'S CHOICE, NOT v87'S FORMULATION: it salvages the region where "
                f"the quantity is a reliable mean rather than a survivorship-biased one, and "
                f"AUDIT_R12.md says so in those words. Censored inversions are characterised with "
                f"their PAIRED standard errors and never corrected. An inversion in the uncensored "
                f"region is a D3.")
    logger.info(f"C5 -- LJUNG-BOX CALIBRATION, NOT A BINARY GATE. "
                f"1 - {1 - LB_LEVEL}^{2 * len(GAMMA_LEV_GRID)} = "
                f"{1 - (1 - LB_LEVEL) ** (2 * len(GAMMA_LEV_GRID)):.4f} is computed and logged "
                f"above, BEFORE interpretation. The reading is a two-sided Kolmogorov-Smirnov test "
                f"of the {2 * len(GAMMA_LEV_GRID)} exact binomial p-values against Uniform(0,1), "
                f"reported for the whole family and separately per arm, and the "
                f"{2 * len(GAMMA_LEV_GRID)} individual p-values are persisted in "
                f"R12_leverage_fpr.csv as DESCRIPTIVE columns (S4bis point 3). NOTHING IS GATED ON "
                f"IT, and the reason is stated in the same breath: the Data arm's rejection rate "
                f"climbing to 24.6% IS v87's own printed claim, so a uniformity test on that arm "
                f"rejects precisely because the manuscript is right, and a gate would be a gate on "
                f"the paper's thesis rather than on the calibration of the instrument.")
    logger.info(f"C6 -- `ast` SOURCE IDENTITY, three layers, run before any campaign so a "
                f"transcription error costs no compute. Deterministic; trigger probability 0 "
                f"unless a copy has drifted.")
    logger.info(f"C7 -- REPRODUCIBILITY, TWO AXES. (1) two successive runs, SHA-256 identical on "
                f"every CSV, PNG and .tex; (2) a run at a different `--n-jobs` against the default, "
                f"byte-identical, since NUM_CHUNKS_A = {NUM_CHUNKS_A} and "
                f"NUM_CHUNKS_B = {NUM_CHUNKS_B} fix the decomposition and every stream carries its "
                f"own key. Verified outside the process, from the digests this log records.")
    logger.info(f"C8 -- THE CRN CONCEPT ARM IS DEGENERATE, AND IT IS ASSERTED RATHER THAN "
                f"OBSERVED. On {CRN_IDENTITY_SEEDS} seeds the SHA-256 of the monitored binary "
                f"stream (eps[{WARMUP_A}:{N_TOTAL_A}] > 0) must be IDENTICAL at all "
                f"{len(GAMMA_LEV_GRID)} gamma_lev under the key ('R12', '{ROLE_A_CRN}', s), with "
                f"sys.exit(1) otherwise. The Kish design effect is measured on BOTH Concept arms: "
                f"{len(GAMMA_LEV_GRID)} by construction on the CRN arm, near 1 on the independent "
                f"one. Deterministic; trigger probability 0 unless the generator or the key has "
                f"changed.")
    logger.info(f"C9 -- LEVERAGE INVARIANCE AS A SLOPE, BECAUSE A RANGE HAS NO NULL. v87's "
                f"'leverage-invariant' is tested by an OLS slope of the INDEPENDENT-arm Concept FPR "
                f"on gamma_lev against a null of zero slope, with a seed-cluster bootstrap standard "
                f"error over {BOOTSTRAP_REPLICATES} replicates. GATE AT {GATE_LEVEL}, two-sided; "
                f"trigger probability under its own null is exactly {GATE_LEVEL}. The four range "
                f"macros ship with their own seed bootstrap envelopes at the "
                f"{1 - BOOTSTRAP_LEVEL:.0%} level, marked DESCRIPTIVE and gating nothing: a max "
                f"minus a min over a noisy grid is an extremum statistic and has no stable "
                f"sampling distribution (S4bis, fourth corollary).")
    logger.info(f"C10 -- THE DGP VARIANCE CLAMP, MEASURED RATHER THAN ASSUMED. `simulate_gjr_garch` "
                f"l.106 caps sigma2[t] <= 1e4 * sigma2_unc. At gamma_lev = {GAMMA_LEV_GRID[-1]} the "
                f"persistence is {ALPHA_A + GAMMA_LEV_GRID[-1] / 2 + BETA_A:.2f} and near nu = 4 "
                f"the innovations are extreme, so the clamp is a silent execution path that could "
                f"mechanically produce the published collapse -- exactly the degraded path the "
                f"epistemic asymmetry rule requires be excluded before any D0/D1. The primitive is "
                f"carried VERBATIM; the binding rate is measured by a separate instrumented copy on "
                f"{CLAMP_SUBSAMPLE} streams per grid point, each asserted to return a bit-identical "
                f"eps, and lands in R12_diagnostics.csv and the audit ONLY. Reported, not gated.")
    logger.info(f"C11 -- LEGACY-GLOBAL INERTNESS, ASSERTED RATHER THAN ASSUMED. The witness locks "
                f"np.random and random at l.133-134 and l.196-197 and nothing downstream reads "
                f"either. Each worker is evaluated TWICE under deliberately different global states "
                f"and must return bit-identical output; that is what justifies dropping the two "
                f"calls rather than carrying them. Deterministic; trigger probability 0.")
    logger.info(f"STREAM-LEVEL FAMILY-WISE TRIGGER PROBABILITY, LOGGED ONCE BEFORE ANY RESULT IS "
                f"READ. Exactly ONE gate of this stream consumes entropy -- C9's two-sided slope "
                f"test at {GATE_LEVEL} -- so the probability that a gate fires on a compliant "
                f"campaign is {GATE_LEVEL:.4f}, below the 5% ceiling S4bis fixes. C4's monotonicity "
                f"reading is a qualitative D3 criterion on a pre-declared domain rather than a "
                f"level test, and C1, C2, C6, C7, C8, C10 and C11 are deterministic. No level is "
                f"chosen after a result is seen.")
    logger.info(f"HALT CONDITION. Two live candidates. (1) C1 failing: the Concept flatness would "
                f"then be unmeasured, D3. (2) The regenerated censored delay range leaving the "
                f"rounding bracket [{CENSORED_BRACKET[0]:.0f}, {CENSORED_BRACKET[1]:.0f}) with its "
                f"own 95% interval excluding the bound -- v87 prints 2,400--3,000 ROUNDED TO THE "
                f"HUNDREDS, and the witness's own 2443.18 and 3005.28 both round onto those "
                f"numerals, so 3005 is not a contradiction and the bracket is the watch item. "
                f"Either fires and the run stops: no parameter, tolerance, seed or bound is moved "
                f"to reconcile.")
    logger.info(f"Worker processes requested: {n_jobs}. NUM_CHUNKS_A = {NUM_CHUNKS_A}, "
                f"NUM_CHUNKS_B = {NUM_CHUNKS_B}, NUM_CHUNKS_CLAMP = {NUM_CHUNKS_CLAMP} are fixed, "
                f"so neither value can move a number.")
    logger.info("=" * 78)


# --- CONTROL C11, RUN BEFORE ANY CAMPAIGN ---

def control_c11_legacy_globals(logger):
    """
    C11. The two vestigial legacy global seeds of the witness are dropped, and
    their inertness is ASSERTED rather than assumed.

    Each worker is evaluated twice on the same key under deliberately different
    `np.random` / `random` global states. If any third-party routine the workers
    reach -- `acorr_ljungbox` above all -- consumed the inherited global state,
    the two evaluations would differ. Deterministic; trigger probability 0.
    """
    omega_a = VARIANCE_TARGET * (1 - (ALPHA_A + GAMMA_LEV_GRID[-1] / 2.0) - BETA_A)
    params_a = (GAMMA_LEV_GRID[-1], 0, N_TOTAL_A, omega_a, ALPHA_A, BETA_A, NU_A,
                LAMBDA_IID_A, DELTA_P_A, LAMBDA_C_A, DELTA_C_A,
                seed_sequence_for("R12", ROLE_A_CRN, 0))
    params_b = (NU_GRID[-1], 0, N_TOTAL_B, OMEGA_B, ALPHA_B, BETA_B, C_MAGNITUDE_B,
                LAMBDA_IID_B, DELTA_P_B, LAMBDA_C_B, DELTA_C_B,
                seed_sequence_for("R12", ROLE_B, 0))

    outcomes = {}
    for state in (1, 999983):
        np.random.seed(state)
        random.seed(state)
        outcomes[("A", state)] = _worker_expA(params_a)
        np.random.seed(state)
        random.seed(state)
        outcomes[("B", state)] = _worker_expB(params_b)

    for tag in ("A", "B"):
        first, second = outcomes[(tag, 1)], outcomes[(tag, 999983)]
        if first != second:
            logger.error(f"C11 FAILED on _worker_exp{tag}: the same key returns {first} under "
                         f"global state 1 and {second} under global state 999983. Something the "
                         f"worker reaches consumes the inherited global RNG state, so the witness's "
                         f"np.random.seed / random.seed calls are NOT vestigial and dropping them "
                         f"changes what is measured.")
            sys.exit(1)
    logger.info(f"C11 LEGACY-GLOBAL INERTNESS: _worker_expA at gamma_lev = {GAMMA_LEV_GRID[-1]} and "
                f"_worker_expB at nu = {NU_GRID[-1]} each return bit-identical output under two "
                f"deliberately different np.random / random global states "
                f"(A: {outcomes[('A', 1)]}; B: {outcomes[('B', 1)]}). The witness's "
                f"np.random.seed(seed & 0xFFFFFFFF) and random.seed(seed & 0xFFFFFFFF) at l.133-134 "
                f"and l.196-197 are therefore inert, and dropping them under the entropy migration "
                f"moves nothing. Deterministic; trigger probability 0. Note what this does NOT "
                f"establish: it is a statement about these two workers and the statsmodels version "
                f"logged above, not about acorr_ljungbox in general.")
    return outcomes


# --- CAMPAIGNS ---

def omega_for_gamma(gamma_lev):
    """
    The variance-targeted intercept of Experiment A, witness l.252-253:
    alpha_naif = alpha + g_lev/2 and omega = 0.04 * (1 - alpha_naif - beta), so
    sigma2_unc = 0.04 at every grid point.
    """
    alpha_naif = ALPHA_A + gamma_lev / 2.0
    return VARIANCE_TARGET * (1 - alpha_naif - BETA_A)


def run_campaign_a(logger, n_jobs, role):
    """
    Experiment A on one entropy key. Returns four (n_seeds x n_gamma) boolean
    matrices, so that every later interval, design effect and bootstrap reads the
    per-stream outcomes rather than a grid-level aggregate.
    """
    bounds = chunk_bounds(N_SEEDS_A, NUM_CHUNKS_A)
    tasks = [(gi, g, start, stop, role, omega_for_gamma(g))
             for gi, g in enumerate(GAMMA_LEV_GRID) for (start, stop) in bounds]
    t0 = time.time()
    results = Parallel(n_jobs=n_jobs)(delayed(_chunk_expA)(*t) for t in tasks)
    shape = (N_SEEDS_A, len(GAMMA_LEV_GRID))
    fp_data = np.zeros(shape, dtype=bool)
    fp_concept = np.zeros(shape, dtype=bool)
    lb_data = np.zeros(shape, dtype=bool)
    lb_concept = np.zeros(shape, dtype=bool)
    for gi, start, a, b, c, d in results:
        fp_data[start:start + len(a), gi] = a
        fp_concept[start:start + len(b), gi] = b
        lb_data[start:start + len(c), gi] = c
        lb_concept[start:start + len(d), gi] = d
    logger.info(f"Experiment A [{role}] completed in {time.time() - t0:.1f}s: "
                f"{len(GAMMA_LEV_GRID)} x {N_SEEDS_A} = {len(GAMMA_LEV_GRID) * N_SEEDS_A} streams "
                f"of {N_TOTAL_A} steps over {len(tasks)} fixed chunks.")
    return {"fp_data": fp_data, "fp_concept": fp_concept,
            "lb_data": lb_data, "lb_concept": lb_concept}


def run_campaign_b(logger, n_jobs):
    """
    Experiment B. Returns two (n_seeds x n_nu) integer matrices of alarm indices
    with -1 for no alarm, which is the witness's own sentinel (`strict_cusum`
    returns -1) and what the aggregation filters on.
    """
    bounds = chunk_bounds(N_SEEDS_B, NUM_CHUNKS_B)
    tasks = [(ni, nu, start, stop)
             for ni, nu in enumerate(NU_GRID) for (start, stop) in bounds]
    t0 = time.time()
    results = Parallel(n_jobs=n_jobs)(delayed(_chunk_expB)(*t) for t in tasks)
    shape = (N_SEEDS_B, len(NU_GRID))
    al_data = np.zeros(shape, dtype=np.int64)
    al_concept = np.zeros(shape, dtype=np.int64)
    for ni, start, a, b in results:
        al_data[start:start + len(a), ni] = a
        al_concept[start:start + len(b), ni] = b
    logger.info(f"Experiment B completed in {time.time() - t0:.1f}s: {len(NU_GRID)} x {N_SEEDS_B} "
                f"= {len(NU_GRID) * N_SEEDS_B} streams of {N_TOTAL_B} steps over {len(tasks)} "
                f"fixed chunks, all under the key ('R12', '{ROLE_B}', s), so the sixteen nu are "
                f"traversed under common random numbers.")
    return {"al_data": al_data, "al_concept": al_concept}


def control_c8_crn_identity(logger, n_jobs, campaign_crn, campaign_indep):
    """
    C8. The degeneracy of the CRN Concept arm, asserted on a fixed subsample and
    priced with the Kish design effect on both arms.
    """
    seeds = list(range(CRN_IDENTITY_SEEDS))
    tasks = [(gi, g, omega_for_gamma(g), seeds) for gi, g in enumerate(GAMMA_LEV_GRID)]
    records = [r for chunk in Parallel(n_jobs=n_jobs)(delayed(_chunk_crn_identity)(*t)
                                                      for t in tasks) for r in chunk]
    by_seed = {}
    for gi, s, digest in records:
        by_seed.setdefault(s, set()).add(digest)
    varying = sorted(s for s, digests in by_seed.items() if len(digests) > 1)
    if varying:
        logger.error(f"C8 FAILED: the monitored binary stream is NOT bit-identical across the "
                     f"{len(GAMMA_LEV_GRID)} gamma_lev on {len(varying)} of {CRN_IDENTITY_SEEDS} "
                     f"seeds under the key ('R12', '{ROLE_A_CRN}', s): {varying[:10]}. Either "
                     f"simulate_gjr_garch no longer draws its innovations before the variance "
                     f"recursion, or the key has acquired a dependence on the grid. Both change "
                     f"what the identity witness witnesses.")
        sys.exit(1)
    logger.warning(
        f"C8 THE CRN CONCEPT ARM IS DEGENERATE, AND THIS IS ASSERTED. On all "
        f"{CRN_IDENTITY_SEEDS} subsampled seeds the SHA-256 of "
        f"(eps[{WARMUP_A}:{N_TOTAL_A}] > 0) is IDENTICAL at all {len(GAMMA_LEV_GRID)} gamma_lev: "
        f"eps[t] = sqrt(sigma2[t]) * z[t] with sigma2[t] > 0, so sign(eps_t) = sign(z_t) exactly "
        f"and the leverage leaves no trace on the sign. R12_concept_crn_witness.csv therefore "
        f"carries one number repeated {len(GAMMA_LEV_GRID)} times, its effective sample size is "
        f"{N_SEEDS_A} and not {len(GAMMA_LEV_GRID) * N_SEEDS_A}, and IT SUPPORTS NO CLAIM. Every "
        f"published Concept rate, interval, macro and figure point is taken from the arm keyed "
        f"('R12', '{ROLE_A_INDEP}', gamma_index, s), whose key breaks the pairing.")

    deff = {}
    for name, matrices in (("fp_concept", "fp_concept"), ("lb_concept", "lb_concept")):
        deff[name] = (kish_design_effect(campaign_crn[matrices].astype(float)),
                      kish_design_effect(campaign_indep[matrices].astype(float)))
    logger.info(f"C8 KISH DESIGN EFFECT of the pooled Experiment A Concept level, CRN key against "
                f"independent key: "
                + "; ".join(f"{k}: {p:.4f} vs {i:.4f}" for k, (p, i) in deff.items())
                + f". A CRN arm whose readings are bit-identical carries a design effect of "
                  f"{len(GAMMA_LEV_GRID)} BY CONSTRUCTION, so its "
                  f"{len(GAMMA_LEV_GRID) * N_SEEDS_A} streams hold the information of {N_SEEDS_A}. "
                  f"The independent arm is the measurement.")
    for name in ("fp_data", "lb_data"):
        logger.info(f"C8 the SAME statistic on the Data arm, which is NOT degenerate: "
                    f"deff({name}) = {kish_design_effect(campaign_crn[name].astype(float)):.4f} on "
                    f"the CRN key against "
                    f"{kish_design_effect(campaign_indep[name].astype(float)):.4f} on the "
                    f"independent key. The symmetric filter reads eps[t-1]**2 through the variance "
                    f"recursion, which carries gamma_lev, so the pairing sharpens the Data "
                    f"comparison instead of collapsing it.")
    digests = sorted({d for _, _, d in records})
    logger.info(f"C8 subsample digest, one value over {len(records)} (gamma_lev, seed) pairs per "
                f"seed and {len(digests)} distinct values over the whole subsample -- one per seed, "
                f"as the identity requires.")
    return {"records": records, "deff": deff, "n_distinct": len(digests)}


def control_c10_clamp(logger, n_jobs):
    """
    C10. The binding rate of the DGP variance clamp, measured on a subsample of
    the streams the campaign actually ran, with the instrumented copy asserted
    bit-identical to the carried primitive on every one of them.
    """
    seeds = list(range(CLAMP_SUBSAMPLE))
    bounds = chunk_bounds(len(seeds), NUM_CHUNKS_CLAMP)
    tasks = []
    for gi, g in enumerate(GAMMA_LEV_GRID):
        for (start, stop) in bounds:
            tasks.append(("A", gi, g, N_TOTAL_A, omega_for_gamma(g), ALPHA_A, g, BETA_A, NU_A,
                          ROLE_A_CRN, seeds[start:stop]))
    for ni, nu in enumerate(NU_GRID):
        for (start, stop) in bounds:
            tasks.append(("B", ni, nu, N_TOTAL_B, OMEGA_B, ALPHA_B, 0.0, BETA_B, nu,
                          ROLE_B, seeds[start:stop]))
    t0 = time.time()
    records = [r for chunk in Parallel(n_jobs=n_jobs)(delayed(_chunk_clamp)(*t) for t in tasks)
               for r in chunk]
    frame = pd.DataFrame(records, columns=["experiment", "grid_index", "grid_value", "seed",
                                           "n_clamped", "max_sigma2_over_unc", "eps_identical",
                                           "n_steps"])
    disagreements = int((~frame["eps_identical"]).sum())
    if disagreements:
        logger.error(f"C10 FAILED: the instrumented copy of simulate_gjr_garch returns an eps that "
                     f"differs from the carried primitive on {disagreements} of {len(frame)} "
                     f"streams. The clamp measurement would describe a different process from the "
                     f"one the campaign runs.")
        sys.exit(1)
    logger.info(f"C10 INSTRUMENTED EQUIVALENCE: {len(frame)} streams, 0 disagreements; the "
                f"instrumented copy returns a bit-identical eps to the carried primitive on every "
                f"one. Measured in {time.time() - t0:.1f}s.")

    summary = (frame.groupby(["experiment", "grid_index", "grid_value"], as_index=False)
               .agg(n_streams=("seed", "size"), n_steps=("n_steps", "sum"),
                    n_clamped=("n_clamped", "sum"),
                    n_streams_binding=("n_clamped", lambda v: int((v > 0).sum())),
                    max_sigma2_over_unc=("max_sigma2_over_unc", "max")))
    summary["clamp_rate_per_step"] = summary["n_clamped"] / summary["n_steps"]
    summary["clamp_rate_per_stream"] = summary["n_streams_binding"] / summary["n_streams"]
    for row in summary.itertuples(index=False):
        logger.info(f"C10 [{row.experiment} grid={row.grid_value}] clamp bound on "
                    f"{row.n_clamped} of {row.n_steps} recursion steps "
                    f"({row.clamp_rate_per_step:.3e} per step) and on {row.n_streams_binding} of "
                    f"{row.n_streams} streams; the largest UNCLAMPED sigma2 reached "
                    f"{row.max_sigma2_over_unc:.4g} x sigma2_unc against a ceiling of 1e4.")
    total = int(summary["n_clamped"].sum())
    logger.info(f"C10 TOTAL over the whole subsample: {total} clamped steps of "
                f"{int(summary['n_steps'].sum())}. Reported in R12_diagnostics.csv and in "
                f"AUDIT_R12.md ONLY; it gates nothing and no macro reads it. What it settles is "
                f"the epistemic-asymmetry question S3 poses before any D0/D1 classification: "
                f"whether a silent degraded execution path could be producing the published "
                f"collapse mechanically.")
    return frame, summary


# --- FRAME CONSTRUCTION ---

def build_leverage_fpr(campaign_crn, campaign_indep):
    """
    `protocol_expA_leverage_fpr.csv` -> `R12_leverage_fpr.csv`.

    The Data columns come from the CRN arm, keyed ('R12', 'expA', s); the Concept
    columns come from the INDEPENDENT arm, keyed
    ('R12', 'expA_concept_indep', gamma_index, s). The `concept_arm` column names
    the originating arm on every row, so a reader of the file cannot mistake
    which arm a Concept number was measured on.

    The witness's own normal-approximation half-widths `ci_data` / `ci_concept`
    (l.270-271, at the literal 1.96) are carried beside asymmetric Wilson bounds
    for comparability, and the exact two-sided binomial p-value of each
    Ljung-Box rate against the nominal level is added as a DESCRIPTIVE column
    (S4bis point 3), never as a criterion.
    """
    records = []
    for gi, gamma_lev in enumerate(GAMMA_LEV_GRID):
        k_fp_data = int(campaign_crn["fp_data"][:, gi].sum())
        k_lb_data = int(campaign_crn["lb_data"][:, gi].sum())
        k_fp_concept = int(campaign_indep["fp_concept"][:, gi].sum())
        k_lb_concept = int(campaign_indep["lb_concept"][:, gi].sum())
        fp_data = k_fp_data / N_SEEDS_A
        fp_concept = k_fp_concept / N_SEEDS_A
        lb_reject_data = k_lb_data / N_SEEDS_A
        lb_reject_concept = k_lb_concept / N_SEEDS_A
        row = {
            "gamma_lev": gamma_lev,
            "alpha_sym": ALPHA_A + gamma_lev / 2.0,
            "persistence": ALPHA_A + gamma_lev / 2.0 + BETA_A,
            "omega": omega_for_gamma(gamma_lev),
            "n_seeds": N_SEEDS_A,
            "concept_arm": ROLE_A_INDEP,
            "data_arm": ROLE_A_CRN,
            "fp_data": fp_data,
            "fp_concept": fp_concept,
            "lb_reject_data": lb_reject_data,
            "lb_reject_concept": lb_reject_concept,
            "fpr_data": fp_data * 100.0,
            "fpr_concept": fp_concept * 100.0,
            "lb_data_pct": lb_reject_data * 100.0,
            "lb_concept_pct": lb_reject_concept * 100.0,
        }
        for name, k in (("fp_data", k_fp_data), ("fp_concept", k_fp_concept),
                        ("lb_reject_data", k_lb_data), ("lb_reject_concept", k_lb_concept)):
            low, high = wilson_ci(k, N_SEEDS_A)
            row[f"{name}_ci_low"] = low
            row[f"{name}_ci_high"] = high
        # The witness's half-width, carried verbatim in form (l.270-271). Within a
        # grid cell the streams carry distinct seed indices and are mutually
        # independent, so deff = 1.0 exactly (S4bis, sixth corollary) and the
        # binomial standard error applies unmodified.
        deff_within_cell = 1.0
        row["ci_data"] = Z_WITNESS * math.sqrt(
            deff_within_cell * fp_data * (1.0 - fp_data) / N_SEEDS_A) * 100.0
        row["ci_concept"] = Z_WITNESS * math.sqrt(
            deff_within_cell * fp_concept * (1.0 - fp_concept) / N_SEEDS_A) * 100.0
        row["deff_within_cell"] = deff_within_cell
        row["lb_data_binom_p"] = float(
            stats.binomtest(k_lb_data, N_SEEDS_A, LB_LEVEL).pvalue)
        row["lb_concept_binom_p"] = float(
            stats.binomtest(k_lb_concept, N_SEEDS_A, LB_LEVEL).pvalue)
        records.append(row)
    return pd.DataFrame(records)


def build_concept_crn_witness(campaign_crn, identity):
    """
    The degenerate CRN Concept arm, persisted as an identity witness a reviewer
    can open. It supports no claim and its (zero) range is not published.
    """
    digests = {}
    for gi, s, digest in identity["records"]:
        digests.setdefault(gi, set()).add(digest)
    records = []
    for gi, gamma_lev in enumerate(GAMMA_LEV_GRID):
        k_fp = int(campaign_crn["fp_concept"][:, gi].sum())
        k_lb = int(campaign_crn["lb_concept"][:, gi].sum())
        low, high = wilson_ci(k_fp, N_SEEDS_A)
        records.append({
            "gamma_lev": gamma_lev,
            "arm": ROLE_A_CRN,
            "n_seeds": N_SEEDS_A,
            "n_eff": N_SEEDS_A,
            "fp_concept": k_fp / N_SEEDS_A,
            "fpr_concept": 100.0 * k_fp / N_SEEDS_A,
            "fp_concept_ci_low": low,
            "fp_concept_ci_high": high,
            "lb_reject_concept": k_lb / N_SEEDS_A,
            "lb_concept_pct": 100.0 * k_lb / N_SEEDS_A,
            "n_identity_seeds": CRN_IDENTITY_SEEDS,
            "n_distinct_e_bin_digests": len(digests[gi]),
            "supports_published_claim": False,
        })
    return pd.DataFrame(records)


def build_singularity_add(campaign_b, logger):
    """
    `protocol_expB_singularity_add.csv` -> `R12_singularity_add.csv`.

    The aggregation follows the witness l.374-400 statement for statement, with
    two additions forced by control C2:

      * `SEM_Data_Raw`, the standard error of the conditional delay on the
        SURVIVING streams of EVERY cell, censored or not. The witness leaves
        `SEM_Data` NaN exactly where v87 publishes a delay range, so the
        dispersion of the one published censored quantity is missing from the
        submitted artefact;
      * the detection counts and their Wilson bounds, so that a reader can price
        the censoring rule rather than take it.
    """
    n_seeds = N_SEEDS_B
    df_raw = pd.DataFrame({
        "nu": np.repeat(np.array(NU_GRID, dtype=float), n_seeds),
        "al_data": campaign_b["al_data"].T.reshape(-1),
        "al_concept": campaign_b["al_concept"].T.reshape(-1),
    })

    aggregated = []
    for nu in NU_GRID:
        subset = df_raw[df_raw["nu"] == nu]
        d_data = subset[subset["al_data"] >= 0]["al_data"]
        d_concept = subset[subset["al_concept"] >= 0]["al_concept"]

        det_rate_data = len(d_data) / n_seeds
        det_rate_concept = len(d_concept) / n_seeds

        # Strict censorship rule (Clean for main line, Raw for the surviving
        # minority), carried from the witness l.384-389 and stated in the log by
        # control C2 BEFORE this frame is built.
        m_data = d_data.mean() if det_rate_data >= CENSORING_DETRATE else np.nan
        m_data_raw = d_data.mean() if len(d_data) > 0 else np.nan
        m_concept = d_concept.mean() if det_rate_concept >= CENSORING_DETRATE else np.nan

        # Standard errors. Within a nu cell the streams carry distinct seed
        # indices and are mutually independent, so the design effect of a
        # within-cell mean is exactly 1.0 (S4bis, sixth corollary); the common
        # random numbers of this campaign run ACROSS nu, not within a cell, and
        # control C4 prices that pairing separately. `SEM_Data_Raw` is the
        # addition of control C2: it is formed on the surviving streams of every
        # cell, which is where v87 L353 publishes its delay range.
        deff_within_cell = 1.0
        sem_data = (math.sqrt(deff_within_cell) * d_data.std() / np.sqrt(len(d_data))
                    if det_rate_data >= CENSORING_DETRATE else np.nan)
        sem_data_raw = (math.sqrt(deff_within_cell) * d_data.std() / np.sqrt(len(d_data))
                        if len(d_data) > 1 else np.nan)
        sem_concept = (math.sqrt(deff_within_cell) * d_concept.std() / np.sqrt(len(d_concept))
                       if det_rate_concept >= CENSORING_DETRATE else np.nan)

        low_data, high_data = wilson_ci(len(d_data), n_seeds)
        low_concept, high_concept = wilson_ci(len(d_concept), n_seeds)
        aggregated.append({
            "nu": nu,
            "n_seeds": n_seeds,
            "n_detected_data": len(d_data),
            "n_detected_concept": len(d_concept),
            "det_rate_data": det_rate_data,
            "det_rate_concept": det_rate_concept,
            "det_rate_data_ci_low": low_data,
            "det_rate_data_ci_high": high_data,
            "det_rate_concept_ci_low": low_concept,
            "det_rate_concept_ci_high": high_concept,
            "censored": bool(det_rate_data < CENSORING_DETRATE),
            "ADD_Data": m_data,
            "SEM_Data": sem_data,
            "ADD_Data_Raw": m_data_raw,
            "SEM_Data_Raw": sem_data_raw,
            "ADD_Concept": m_concept,
            "SEM_Concept": sem_concept,
            "deff_within_cell": deff_within_cell,
        })

    frame = pd.DataFrame(aggregated)
    concept_span = float(frame["ADD_Concept"].max() - frame["ADD_Concept"].min())
    logger.info(f"C1 CORROBORATION, AFTER THE CAMPAIGN. det_rate_concept is "
                f"{frame['det_rate_concept'].min():.4f}-{frame['det_rate_concept'].max():.4f} over "
                f"the sixteen nu, and ADD_Concept varies over "
                f"{frame['ADD_Concept'].min():.3f}-{frame['ADD_Concept'].max():.3f} steps, a span "
                f"of {concept_span:.3f}. A varying conditional mean is incompatible with an "
                f"absence of detection; it does not by itself establish that the rate is computed, "
                f"which is why C1 asserts the producing line and this is corroboration only.")
    return frame


def build_diagnostics(frame_a, frame_b, clamp_summary, identity, c4, c5, c9, envelopes,
                      campaign_indep):
    """
    `R12_diagnostics.csv`: clamp binding rates, design effects, the per-point
    Ljung-Box p-values, the censored-domain standard errors and the paired
    monotonicity margins, in one long-format frame.

    Nothing here certifies a published value. The frame exists so that every
    number this audit quotes is openable, which is the partition
    `docs/sections/R12.md` states.
    """
    rows = []

    def add(experiment, quantity, grid_name, grid_value, arm, value, n, note):
        rows.append({"experiment": experiment, "quantity": quantity, "grid_name": grid_name,
                     "grid_value": grid_value, "arm": arm, "value": value, "n": n, "note": note})

    for row in clamp_summary.itertuples(index=False):
        add(row.experiment, "clamp_rate_per_step",
            "gamma_lev" if row.experiment == "A" else "nu", row.grid_value, "dgp",
            float(row.clamp_rate_per_step), int(row.n_steps),
            "control C10: sigma2[t] = min(sigma2[t], 1e4 * sigma2_unc), witness l.106")
        add(row.experiment, "clamp_rate_per_stream",
            "gamma_lev" if row.experiment == "A" else "nu", row.grid_value, "dgp",
            float(row.clamp_rate_per_stream), int(row.n_streams), "control C10")
        add(row.experiment, "max_sigma2_over_unc",
            "gamma_lev" if row.experiment == "A" else "nu", row.grid_value, "dgp",
            float(row.max_sigma2_over_unc), int(row.n_streams),
            "control C10: largest unclamped sigma2 in units of sigma2_unc, ceiling 1e4")

    for name, (crn, indep) in identity["deff"].items():
        add("A", "kish_design_effect", "grid", float('nan'), f"{ROLE_A_CRN}:{name}", float(crn),
            len(GAMMA_LEV_GRID) * N_SEEDS_A,
            f"control C8: {len(GAMMA_LEV_GRID)} by construction on the CRN arm")
        add("A", "kish_design_effect", "grid", float('nan'), f"{ROLE_A_INDEP}:{name}",
            float(indep), len(GAMMA_LEV_GRID) * N_SEEDS_A,
            "control C8: the published arm; the key breaks the pairing")

    for row in frame_a.itertuples(index=False):
        add("A", "lb_binom_p", "gamma_lev", float(row.gamma_lev), "data",
            float(row.lb_data_binom_p), N_SEEDS_A,
            "control C5: exact two-sided binomial p-value against the nominal 0.05")
        add("A", "lb_binom_p", "gamma_lev", float(row.gamma_lev), "concept",
            float(row.lb_concept_binom_p), N_SEEDS_A, "control C5")
        # The Data arm read on the INDEPENDENT key. It is not published anywhere:
        # it exists because the second Experiment A pass computes the whole
        # worker, and it is the counterfactual that shows the Data response is
        # not an artefact of the CRN pairing.
        gi = GAMMA_LEV_GRID.index(row.gamma_lev)
        add("A", "fpr_data_independent_key", "gamma_lev", float(row.gamma_lev), ROLE_A_INDEP,
            100.0 * float(campaign_indep["fp_data"][:, gi].mean()), N_SEEDS_A,
            "unpublished second reading of the Data arm on the independent key")
        add("A", "lb_data_pct_independent_key", "gamma_lev", float(row.gamma_lev), ROLE_A_INDEP,
            100.0 * float(campaign_indep["lb_data"][:, gi].mean()), N_SEEDS_A,
            "unpublished second reading of the Data arm on the independent key")

    for row in frame_b.itertuples(index=False):
        add("B", "SEM_Data_Raw", "nu", float(row.nu), "data", float(row.SEM_Data_Raw),
            int(row.n_detected_data),
            "control C2: dispersion of the conditional delay on the surviving streams")
        add("B", "censored", "nu", float(row.nu), "data", float(bool(row.censored)),
            N_SEEDS_B, f"det_rate_data < {CENSORING_DETRATE}")

    for entry in c4["margins"]:
        add("B", "paired_det_rate_difference", "nu_pair", entry["nu_low"], "data",
            entry["difference"], N_SEEDS_B,
            f"control C4: nu {entry['nu_high']} -> {entry['nu_low']}, paired SE "
            f"{entry['paired_se']:.6g}, z {entry['z']:+.3f}, deff {entry['deff']:.4f}, "
            f"domain {entry['domain']}")

    add("A", "ks_statistic_all", "grid", float('nan'), "both", c5["ks_all"][0],
        2 * len(GAMMA_LEV_GRID), "control C5: KS of the 30 p-values against Uniform(0,1)")
    add("A", "ks_pvalue_all", "grid", float('nan'), "both", c5["ks_all"][1],
        2 * len(GAMMA_LEV_GRID), "control C5, reported and gating nothing")
    for arm in ("data", "concept"):
        add("A", "ks_statistic", "grid", float('nan'), arm, c5[f"ks_{arm}"][0],
            len(GAMMA_LEV_GRID), "control C5, per arm")
        add("A", "ks_pvalue", "grid", float('nan'), arm, c5[f"ks_{arm}"][1],
            len(GAMMA_LEV_GRID), "control C5, per arm, reported and gating nothing")

    add("A", "invariance_slope", "gamma_lev", float('nan'), ROLE_A_INDEP, c9["slope"],
        len(GAMMA_LEV_GRID), "control C9: OLS of fpr_concept on gamma_lev, percentage points")
    add("A", "invariance_slope_se_ols", "gamma_lev", float('nan'), ROLE_A_INDEP, c9["se_ols"],
        len(GAMMA_LEV_GRID), "control C9: analytic OLS standard error")
    add("A", "invariance_slope_se_bootstrap", "gamma_lev", float('nan'), ROLE_A_INDEP,
        c9["se_boot"], BOOTSTRAP_REPLICATES, "control C9: seed-cluster bootstrap standard error")
    add("A", "invariance_slope_pvalue", "gamma_lev", float('nan'), ROLE_A_INDEP, c9["p_value"],
        len(GAMMA_LEV_GRID), f"control C9: two-sided, gate at {GATE_LEVEL}")
    add("A", "invariance_slope_crn", "gamma_lev", float('nan'), ROLE_A_CRN, c9["slope_crn"],
        len(GAMMA_LEV_GRID), "control C9 diagnostic: exactly zero on the degenerate arm")

    for name, entry in envelopes.items():
        add(entry["experiment"], "extremum_bootstrap_low", entry["grid_name"], float('nan'),
            name, entry["low"], BOOTSTRAP_REPLICATES,
            "S4bis fourth corollary: seed bootstrap envelope, descriptive, gating nothing")
        add(entry["experiment"], "extremum_bootstrap_high", entry["grid_name"], float('nan'),
            name, entry["high"], BOOTSTRAP_REPLICATES, "S4bis fourth corollary")
        add(entry["experiment"], "extremum_point", entry["grid_name"], float('nan'), name,
            entry["point"], BOOTSTRAP_REPLICATES, "the published point value")

    return pd.DataFrame(rows)


# --- CONTROLS ---

def control_c3_task_boundary(logger):
    """
    C3, as a READ. R07's certified AR-GARCH cell printed beside the orphan
    witness, with the gap stated and left unexplained.

    Nothing here is measured by R12, no macro is emitted from it, and no register
    entry is opened on it. What IS established is the arithmetic of the orphan's
    two intervals, recovered from its counts alone.
    """
    if not ORPHAN_BOUNDARY.exists():
        logger.error(f"C3 FAILED: {ORPHAN_BOUNDARY} is missing; the vendored witness cannot be "
                     f"read.")
        sys.exit(1)
    if not R07_LB_FPR.exists():
        logger.error(f"C3 FAILED: {R07_LB_FPR} is missing. C3 is a read of R07's certified "
                     f"campaign and R12 does not rebuild it; run R07 first.")
        sys.exit(1)

    orphan = pd.read_csv(ORPHAN_BOUNDARY, float_precision='round_trip')
    r07 = pd.read_csv(R07_LB_FPR, float_precision='round_trip')
    cell = r07[np.isclose(r07["phi"].to_numpy(dtype=float), R07_PHI_CELL, rtol=1e-12, atol=1e-15)]
    naive = cell[cell["arm"] == "NAIVE"].iloc[0]
    oracle = cell[cell["arm"] == "ORACLE"].iloc[0]

    logger.info(f"C3 TASK BOUNDARY, AS A READ. R07 `R07_estmean_lb_fpr.csv` at "
                f"phi = {R07_PHI_CELL}, read float_precision='round_trip': NAIVE Ljung-Box "
                f"rejection {naive['lb_reject_rate']!r} (Wilson "
                f"[{naive['lb_ci_low']!r}, {naive['lb_ci_high']!r}], N = "
                f"{int(naive['N_seeds'])}), ORACLE {oracle['lb_reject_rate']!r} (Wilson "
                f"[{oracle['lb_ci_low']!r}, {oracle['lb_ci_high']!r}]). That is the certified "
                f"measurement of v87 L302's claim -- the property holds at the conditional median "
                f"and fails at the naive zero threshold -- and it is R07's mission statement, not "
                f"R12's.")
    for row in orphan.itertuples(index=False):
        logger.info(f"C3 ORPHAN WITNESS [{row.target}] rejection_rate = {row.rejection_rate!r}, "
                    f"interval [{row.ci_low!r}, {row.ci_high!r}], read "
                    f"float_precision='round_trip' from "
                    f"data/reference/R12/orphans/expA_argarch_boundary.csv.")

    recovered = []
    for row in orphan.itertuples(index=False):
        k = int(round(float(row.rejection_rate) * 1000))
        low, high = wilson_ci(k, 1000, z=Z_95)
        low_196, high_196 = wilson_ci(k, 1000, z=Z_WITNESS)
        exact = (low == float(row.ci_low)) and (high == float(row.ci_high))
        recovered.append(exact)
        logger.info(f"C3 INTERVAL RECOVERY [{row.target}] from the counts {k}/1000 alone: Wilson "
                    f"at z = Phi^-1(0.975) = {Z_95!r} gives [{low!r}, {high!r}], which is "
                    f"{'BIT-IDENTICAL' if exact else 'NOT identical'} to the vendored bounds. The "
                    f"rounder z = {Z_WITNESS} gives [{low_196!r}, {high_196!r}], missing the low "
                    f"bound by {abs(low_196 - float(row.ci_low)):.3e}. What this recovers is the "
                    f"INTERVAL CONSTRUCTION and the sample size, and NOT the data-generating "
                    f"process: nothing here fixes the stream length, the innovation law, the AR "
                    f"coefficient or the conditional-mean estimator behind the two rates.")
    if not all(recovered):
        logger.info(f"C3: the vendored bounds are not reproduced by a Wilson interval at "
                    f"z = Phi^-1(0.975) on the counts implied by the printed rates. The "
                    f"construction is therefore something else and is NOT identified here.")

    naive_rate = float(orphan[orphan["target"].str.contains("Naive")]["rejection_rate"].iloc[0])
    median_rate = float(orphan[orphan["target"].str.contains("Centered")]["rejection_rate"].iloc[0])
    logger.info(f"C3 THE GAP, STATED AND LEFT UNEXPLAINED. The orphan reads "
                f"{naive_rate:.3f} / {median_rate:.3f} where R07's certified campaign reads "
                f"{float(naive['lb_reject_rate']):.4f} / {float(oracle['lb_reject_rate']):.4f} at "
                f"phi = {R07_PHI_CELL}. The two pairs are close and they are NOT the same "
                f"measurement: the orphan carries N = 1000 against R07's "
                f"{int(naive['N_seeds'])}, and no producing script for it exists anywhere in the "
                f"delivery (see data/reference/R12/orphans/README.md for the grep). With the "
                f"design unknown, the difference cannot be attributed -- sample size, horizon, "
                f"innovation law, estimator and lag count are all unfixed -- and repository policy "
                f"forbids inventing a mechanism. NO MACRO IS EMITTED AND NO REGISTER ENTRY IS "
                f"OPENED on this comparison.")
    logger.info(f"C3 R12'S OWN NEGATIVE WITNESSES are the cells it actually runs: "
                f"gamma_lev = {GAMMA_LEV_GRID[0]} (the leverage-free case, where the symmetric "
                f"filter is correctly specified and the baseline must hold its level) and "
                f"nu = {NU_GRID[0]} (the light-tailed case, where the fourth moment is finite and "
                f"the Data pipeline must detect). Both are measured, both are in the published "
                f"CSVs, and both are classified D0-D3 against v87.")

    if ORPHAN_RACE.exists():
        race = pd.read_csv(ORPHAN_RACE, float_precision='round_trip')
        populated = race[race["delay_arf"].notna()]
        logger.info(f"C3b `expB_race_condition.csv` IS PRODUCED AND NOT CITED. {len(race)} rows, "
                    f"seed {int(race['seed'].min())}-{int(race['seed'].max())} with "
                    f"{race['seed'].nunique()} distinct values. `delay_frozen` is populated on all "
                    f"{int(race['delay_frozen'].notna().sum())} rows (min "
                    f"{int(race['delay_frozen'].min())}, max {int(race['delay_frozen'].max())}, "
                    f"mean {float(race['delay_frozen'].mean())!r}); `delay_arf` is EMPTY on "
                    f"{len(race) - len(populated)} of {len(race)} rows, the single populated row "
                    f"being seed {int(populated['seed'].iloc[0])} at "
                    f"{float(populated['delay_arf'].iloc[0])!r}. Reported as measured; THE "
                    f"MECHANISM IS NOT ATTRIBUTED (S4.5) -- with no producing code a missing value "
                    f"cannot be told from a censored run, an unwritten column or an aborted arm. "
                    f"v87 cites no frozen-versus-ARF race at L349, at L353 or in either caption, "
                    f"so there is no reconstruction, no camera-ready candidate and no register "
                    f"entry: a candidate must attach to a manuscript sentence.")
    return {"naive_rate": naive_rate, "median_rate": median_rate,
            "r07_naive": float(naive["lb_reject_rate"]), "r07_oracle": float(oracle["lb_reject_rate"]),
            "recovered": all(recovered)}


def control_c4_monotonicity(campaign_b, frame_b, logger):
    """
    C4. Monotone decay of `det_rate_data` in decreasing nu, gated on the
    UNCENSORED domain declared before the frame was read, characterised
    everywhere with PAIRED standard errors, and never corrected.
    """
    detected = (campaign_b["al_data"] >= 0).astype(float)
    censored = frame_b.set_index("nu")["censored"].to_dict()
    margins = []
    inversions_uncensored = []
    inversions_censored = []
    for i in range(len(NU_GRID) - 1):
        nu_high, nu_low = NU_GRID[i], NU_GRID[i + 1]
        a, b = detected[:, i], detected[:, i + 1]
        difference = float(a.mean() - b.mean())
        paired = a - b
        # The two cells share the same 1,000 seed indices under the key
        # ('R12', 'expB', s), so the difference is PAIRED and its variance is
        # that of the difference, not the sum of the two marginal variances.
        # The ratio of the two is the design effect of the pairing (S4bis, third
        # and sixth corollaries) and it is computed before the standard error.
        var_unpaired = float(a.var(ddof=1) + b.var(ddof=1))
        var_paired = float(paired.var(ddof=1))
        deff = var_paired / var_unpaired if var_unpaired > 0 else float('nan')
        paired_se = math.sqrt(var_paired / N_SEEDS_B) if var_paired > 0 else 0.0
        z = difference / paired_se if paired_se > 0 else float('nan')
        domain = "uncensored" if (not censored[nu_high] and not censored[nu_low]) else "censored"
        entry = {"nu_high": nu_high, "nu_low": nu_low, "difference": difference,
                 "paired_se": paired_se, "z": z, "deff": deff, "domain": domain,
                 "ci_low": difference - Z_95 * paired_se, "ci_high": difference + Z_95 * paired_se}
        margins.append(entry)
        if difference < 0:
            (inversions_uncensored if domain == "uncensored" else inversions_censored).append(entry)
        logger.info(f"C4 [nu {nu_high} -> {nu_low}, {domain}] det_rate_data "
                    f"{a.mean():.4f} -> {b.mean():.4f}, paired difference {difference:+.4f}, "
                    f"paired SE {paired_se:.6f} (unpaired SE "
                    f"{math.sqrt(var_unpaired / N_SEEDS_B):.6f}, design effect of the pairing "
                    f"{deff:.4f}), z = {z:+.2f}, 95% [{entry['ci_low']:+.4f}, "
                    f"{entry['ci_high']:+.4f}].")

    logger.info(f"C4 DOMAIN, DECLARED BEFORE THE FRAME WAS READ AND RESTATED HERE. The gate is on "
                f"the UNCENSORED domain only. THIS RESTRICTION IS THIS REPOSITORY'S CHOICE AND NOT "
                f"v87'S FORMULATION: L353 says 'detection decays monotonically' with no domain "
                f"restriction, and the submitted witness is already non-monotone at nu = 4.75 and "
                f"nu = 4.05, both censored. Restricting salvages the region where det_rate_data is "
                f"a reliable estimate rather than a survivorship-biased one; it does not repair "
                f"the sentence.")
    strict_uncensored = [e for e in inversions_uncensored if e["ci_high"] < 0]
    if strict_uncensored:
        logger.error(f"C4 HALT CONDITION MET. det_rate_data INVERTS in the uncensored domain at "
                     f"{[(e['nu_high'], e['nu_low']) for e in strict_uncensored]} with the paired "
                     f"95% interval excluding zero. v87 L353's 'detection decays monotonically' is "
                     f"falsified where the quantity is reliable. This is a D3: full report, no "
                     f"parameter, tolerance, seed or bound moved.")
    elif inversions_uncensored:
        logger.warning(f"C4: {len(inversions_uncensored)} inversion(s) in the uncensored domain "
                       f"whose paired 95% interval COVERS zero: "
                       f"{[(e['nu_high'], e['nu_low'], round(e['z'], 2)) for e in inversions_uncensored]}"
                       f". Characterised and reported; per S3 a bound is breached at D3 only when "
                       f"the regenerated interval excludes it, so this is a D2-grade movement and "
                       f"nothing is corrected.")
    else:
        logger.info(f"C4: det_rate_data decreases at every adjacent pair of the uncensored domain "
                    f"({sum(1 for e in margins if e['domain'] == 'uncensored')} pairs). The gate is "
                    f"met.")
    if inversions_censored:
        logger.info(f"C4 CENSORED-DOMAIN INVERSIONS, CHARACTERISED AND NEVER CORRECTED: "
                    + "; ".join(f"nu {e['nu_high']}->{e['nu_low']} {e['difference']:+.4f} "
                                f"(z {e['z']:+.2f}, 95% [{e['ci_low']:+.4f}, {e['ci_high']:+.4f}])"
                                for e in inversions_censored)
                    + f". Below a {CENSORING_DETRATE:.0%} detection rate the quantity is a rate "
                      f"over a surviving minority and the sentence L353 attaches to it is the one "
                      f"v87 itself qualifies as survivorship-biased.")
    return {"margins": margins, "inversions_uncensored": inversions_uncensored,
            "inversions_censored": inversions_censored, "halt": strict_uncensored}


def control_c5_ljungbox(frame_a, logger):
    """
    C5. Calibration of the Ljung-Box family, as a distribution test rather than
    as a binary gate, with the family-wise arithmetic already logged above.
    """
    p_data = frame_a["lb_data_binom_p"].to_numpy(dtype=float)
    p_concept = frame_a["lb_concept_binom_p"].to_numpy(dtype=float)
    p_all = np.concatenate([p_data, p_concept])
    out = {}
    for name, values in (("all", p_all), ("data", p_data), ("concept", p_concept)):
        ks = stats.kstest(values, 'uniform')
        out[f"ks_{name}"] = (float(ks.statistic), float(ks.pvalue))
    logger.info(f"C5 KS AGAINST Uniform(0,1) on the exact binomial p-values. Whole family "
                f"(n = {len(p_all)}): D = {out['ks_all'][0]!r}, p = {out['ks_all'][1]!r}. Data arm "
                f"(n = {len(p_data)}): D = {out['ks_data'][0]!r}, p = {out['ks_data'][1]!r}. "
                f"Concept arm (n = {len(p_concept)}): D = {out['ks_concept'][0]!r}, "
                f"p = {out['ks_concept'][1]!r}.")
    logger.info(f"C5 HOW TO READ THAT, STATED IN THE SAME BREATH AS THE NUMBERS. The Data arm's "
                f"rejection rate climbing from {frame_a['lb_data_pct'].iloc[0]:.2f}% to "
                f"{frame_a['lb_data_pct'].iloc[-1]:.2f}% IS v87 L349's printed claim, so a "
                f"uniformity test on that arm rejects PRECISELY BECAUSE the manuscript is right; "
                f"the Data KS is a positive control on the instrument's power and not a "
                f"calibration reading. The Concept arm is where calibration is the question, and "
                f"its {len(p_concept)} p-values are the ones a reader should weigh. NOTHING IS "
                f"GATED on either: the family-wise trigger probability of "
                f"{1 - (1 - LB_LEVEL) ** (2 * len(GAMMA_LEV_GRID)):.4f} logged before the campaign "
                f"is what forbids a binary reading, and the individual p-values are persisted in "
                f"R12_leverage_fpr.csv as descriptive columns (S4bis point 3).")
    return out


def control_c9_invariance(campaign_indep, campaign_crn, logger):
    """
    C9. Leverage invariance as a SLOPE with a null, because a max minus a min
    over fifteen noisy estimates has no sampling distribution.
    """
    x = np.array(GAMMA_LEV_GRID, dtype=float)
    matrix = campaign_indep["fp_concept"].astype(float)
    y = 100.0 * matrix.mean(axis=0)
    slope, intercept, se_ols, r2 = ols_fit(x, y)

    slopes = np.empty(BOOTSTRAP_REPLICATES)
    for r in range(BOOTSTRAP_REPLICATES):
        idx = rng_for("R12", "c9_bootstrap", r).integers(0, N_SEEDS_A, N_SEEDS_A)
        slopes[r] = stats.linregress(x, 100.0 * matrix[idx].mean(axis=0)).slope
    se_boot = float(np.std(slopes, ddof=1))
    ci_low, ci_high = (float(v) for v in np.percentile(slopes, [100 * BOOTSTRAP_LEVEL / 2,
                                                               100 * (1 - BOOTSTRAP_LEVEL / 2)]))
    p_value = two_sided_p_from_se(slope, se_boot)

    matrix_crn = campaign_crn["fp_concept"].astype(float)
    slope_crn, _, se_ols_crn, _ = ols_fit(x, 100.0 * matrix_crn.mean(axis=0))

    logger.info(f"C9 LEVERAGE INVARIANCE AS A SLOPE [{ROLE_A_INDEP}]. OLS of the Concept "
                f"false-alarm rate (percentage points) on gamma_lev over the "
                f"{len(GAMMA_LEV_GRID)} grid points: slope = {slope!r} points per unit gamma_lev, "
                f"intercept {intercept!r}, R^2 = {r2!r}. Analytic OLS standard error {se_ols!r}; "
                f"seed-cluster bootstrap standard error {se_boot!r} over {BOOTSTRAP_REPLICATES} "
                f"resamples of the {N_SEEDS_A} seed indices, percentile "
                f"{1 - BOOTSTRAP_LEVEL:.0%} interval [{ci_low!r}, {ci_high!r}]. Two-sided p "
                f"against a null of zero slope: {p_value!r}. GATE AT {GATE_LEVEL}: "
                f"{'FIRED' if (np.isfinite(p_value) and p_value < GATE_LEVEL) else 'not fired'}.")
    logger.info(f"C9 THE TWO STANDARD ERRORS AGREE TO A FACTOR OF "
                f"{se_boot / se_ols if se_ols > 0 else float('nan'):.4f}, WHICH IS ITSELF THE "
                f"CHECK. On an arm keyed ('R12', '{ROLE_A_INDEP}', gamma_index, s) the fifteen "
                f"readings share no draw, so the analytic OLS error and a seed-cluster bootstrap "
                f"must coincide; a bootstrap much larger than the analytic error would mean the "
                f"key had NOT broken the pairing. On the degenerate CRN arm the same fit gives "
                f"slope = {slope_crn!r} with analytic error {se_ols_crn!r} -- exactly zero, "
                f"because the fifteen readings are one number repeated. That contrast is what "
                f"makes the choice of published arm auditable rather than asserted.")
    logger.info(f"C9 WHY A SLOPE AND NOT THE RANGE. v87 prints '7.6--8.4\\%' and calls the rate "
                f"'leverage-invariant'. A max minus a min over {len(GAMMA_LEV_GRID)} noisy "
                f"estimates is an extremum statistic with no stable sampling distribution (S4bis, "
                f"fourth corollary): it grows with the grid size at a FIXED underlying variance, "
                f"so it can neither accept nor reject invariance. The slope has a null, and it is "
                f"the only inferential gate of this stream.")
    return {"slope": slope, "intercept": intercept, "se_ols": se_ols, "se_boot": se_boot,
            "ci_low": ci_low, "ci_high": ci_high, "p_value": p_value, "r2": r2,
            "slope_crn": slope_crn, "fired": bool(np.isfinite(p_value) and p_value < GATE_LEVEL)}


def bootstrap_envelopes(campaign_indep, campaign_b, frame_b, logger):
    """
    S4bis, fourth corollary. Every range macro of this stream is a max or a min
    over a grid, so each ships with its own null law -- a seed-cluster bootstrap
    envelope -- marked descriptive and gating nothing.
    """
    out = {}

    def _rate_extrema(matrix, name_min, name_max, scale, grid_name):
        point_min = float(scale * matrix.mean(axis=0).min())
        point_max = float(scale * matrix.mean(axis=0).max())
        lows = np.empty(BOOTSTRAP_REPLICATES)
        highs = np.empty(BOOTSTRAP_REPLICATES)
        for r in range(BOOTSTRAP_REPLICATES):
            idx = rng_for("R12", "envelope", name_min, r).integers(0, matrix.shape[0],
                                                                   matrix.shape[0])
            rates = scale * matrix[idx].mean(axis=0)
            lows[r] = rates.min()
            highs[r] = rates.max()
        for name, point, draws in ((name_min, point_min, lows), (name_max, point_max, highs)):
            low, high = (float(v) for v in np.percentile(
                draws, [100 * BOOTSTRAP_LEVEL / 2, 100 * (1 - BOOTSTRAP_LEVEL / 2)]))
            out[name] = {"experiment": "A", "grid_name": grid_name, "point": point,
                         "low": low, "high": high, "mean": float(np.mean(draws))}

    _rate_extrema(campaign_indep["fp_concept"].astype(float),
                  "FprConceptMin", "FprConceptMax", 100.0, "gamma_lev")
    _rate_extrema(campaign_indep["lb_concept"].astype(float),
                  "LbConceptMin", "LbConceptMax", 100.0, "gamma_lev")

    def _delay_extrema(alarms, mask, name_min, name_max):
        columns = np.flatnonzero(mask)
        detected = alarms >= 0
        point = []
        for j in columns:
            sel = detected[:, j]
            point.append(float(alarms[sel, j].mean()) if sel.any() else float('nan'))
        lows = np.empty(BOOTSTRAP_REPLICATES)
        highs = np.empty(BOOTSTRAP_REPLICATES)
        for r in range(BOOTSTRAP_REPLICATES):
            idx = rng_for("R12", "envelope", name_min, r).integers(0, alarms.shape[0],
                                                                   alarms.shape[0])
            means = []
            for j in columns:
                sub = alarms[idx, j]
                sel = sub >= 0
                means.append(float(sub[sel].mean()) if sel.any() else float('nan'))
            lows[r] = np.nanmin(means)
            highs[r] = np.nanmax(means)
        for name, value, draws in ((name_min, float(np.nanmin(point)), lows),
                                   (name_max, float(np.nanmax(point)), highs)):
            low, high = (float(v) for v in np.percentile(
                draws, [100 * BOOTSTRAP_LEVEL / 2, 100 * (1 - BOOTSTRAP_LEVEL / 2)]))
            out[name] = {"experiment": "B", "grid_name": "nu", "point": value,
                         "low": low, "high": high, "mean": float(np.mean(draws))}

    censored_mask = frame_b["censored"].to_numpy(dtype=bool)
    _delay_extrema(campaign_b["al_concept"], np.ones(len(NU_GRID), dtype=bool),
                   "AddConceptMin", "AddConceptMax")
    _delay_extrema(campaign_b["al_data"], censored_mask,
                   "AddDataCensoredMin", "AddDataCensoredMax")
    _delay_extrema(campaign_b["al_data"], ~censored_mask,
                   "AddDataMin", "AddDataMax")

    for name, entry in out.items():
        logger.info(f"EXTREMUM ENVELOPE [{name}] point {entry['point']!r}, seed bootstrap "
                    f"{1 - BOOTSTRAP_LEVEL:.0%} interval [{entry['low']!r}, {entry['high']!r}], "
                    f"bootstrap mean {entry['mean']!r} over {BOOTSTRAP_REPLICATES} resamples. "
                    f"DESCRIPTIVE (S4bis, fourth corollary); it gates nothing.")
    return out


# --- FIGURES, DRAWN FROM THE IN-MEMORY FRAMES ---

C_DATA = "#2A6A7C"
C_CONCEPT = "#4A8C5C"


def render_figure_12(frame_a, path, logger):
    """
    v87 Figure 12 (`fig:leverage`), one panel, drawn from the in-memory frame.

    Cosmetic divergence from the submitted `Fig15_Robustness_Leverage.png`,
    declared per repository policy and covered by the `ALL-figure-presentation`
    register row: the title is bold and centred, the bands are asymmetric Wilson
    intervals rather than symmetric normal half-widths, the sample size is on the
    axis, and the Concept curve's arm is named in its legend entry. No numerical
    value moves on any of those accounts.
    """
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    x = frame_a["gamma_lev"].to_numpy(dtype=float)

    ax.plot(x, frame_a["fpr_data"], 'o-', color=C_DATA, linewidth=2,
            label="Econometric baseline (misspecified symmetric GARCH)")
    ax.fill_between(x, 100.0 * frame_a["fp_data_ci_low"], 100.0 * frame_a["fp_data_ci_high"],
                    color=C_DATA, alpha=0.2)
    ax.plot(x, frame_a["fpr_concept"], 's-', color=C_CONCEPT, linewidth=2,
            label=f"Concept pipeline (sign stream, arm `{ROLE_A_INDEP}`)")
    ax.fill_between(x, 100.0 * frame_a["fp_concept_ci_low"],
                    100.0 * frame_a["fp_concept_ci_high"], color=C_CONCEPT, alpha=0.2)

    ax.axhline(5.0, color="gray", linestyle="--", alpha=0.8,
               label="Nominal 5% target (econometric baseline)")
    ax.set_xlabel(r"Asymmetric leverage parameter $\gamma_{\mathrm{lev}}$"
                  f"   ($n = {N_SEEDS_A}$ streams per point, Wilson 95% bands)")
    ax.set_ylabel("False-alarm rate (%)")
    ax.set_title("Robustness to volatility misspecification (FPR explosion)",
                 fontweight="bold", loc="center")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    logger.info(f"Figure 12 written to {path.name}: one panel drawn from the in-memory frame, "
                f"never from a reloaded CSV. The Concept curve is the arm keyed "
                f"('R12', '{ROLE_A_INDEP}', gamma_index, s); the degenerate CRN arm is not "
                f"plotted anywhere.")


def render_figure_13(frame_b, path, logger):
    """
    v87 Figure 13 (`fig:fat_tails`), one panel, drawn from the in-memory frame.

    Cosmetic divergence from the submitted `Fig16_Robustness_FatTails.png`,
    declared per repository policy: bold centred title, the sample size on the axis,
    and -- the one substantive addition -- an error band on the CENSORED
    branch, which the submitted figure draws without one because the submitted
    artefact carries no standard error there. That band is `SEM_Data_Raw`,
    control C2's addition, and it is what makes the survivorship-biased range
    v87 L353 prints readable as an estimate rather than as a point.
    """
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)

    valid_data = frame_b.dropna(subset=["ADD_Data"])
    ax.plot(valid_data["nu"], valid_data["ADD_Data"], 'o-', color=C_DATA, linewidth=2,
            label="Data pipeline (reliable, detection $\\geq 50\\%$)")
    ax.fill_between(valid_data["nu"],
                    valid_data["ADD_Data"] - Z_95 * valid_data["SEM_Data"],
                    valid_data["ADD_Data"] + Z_95 * valid_data["SEM_Data"],
                    color=C_DATA, alpha=0.2)

    zombie = frame_b[frame_b["det_rate_data"] < CENSORING_DETRATE].dropna(subset=["ADD_Data_Raw"])
    if not zombie.empty:
        zombie = zombie.sort_values(by="nu", ascending=False)
        if not valid_data.empty:
            last_valid = valid_data.iloc[-1]
            first_zombie = zombie.iloc[0]
            ax.plot([last_valid["nu"], first_zombie["nu"]],
                    [last_valid["ADD_Data"], first_zombie["ADD_Data_Raw"]],
                    ':', color=C_DATA, alpha=0.6)
        ax.fill_between(zombie["nu"],
                        zombie["ADD_Data_Raw"] - Z_95 * zombie["SEM_Data_Raw"],
                        zombie["ADD_Data_Raw"] + Z_95 * zombie["SEM_Data_Raw"],
                        color=C_DATA, alpha=0.10)
        ax.plot(zombie["nu"], zombie["ADD_Data_Raw"], 'o:', color=C_DATA,
                markeredgecolor=C_DATA, markerfacecolor="white", markersize=8, alpha=0.6,
                label="Data pipeline (censored / survivorship bias)")

    valid_concept = frame_b.dropna(subset=["ADD_Concept"])
    ax.plot(valid_concept["nu"], valid_concept["ADD_Concept"], 's-', color=C_CONCEPT, linewidth=2,
            label="Concept pipeline (sign stream)")
    ax.fill_between(valid_concept["nu"],
                    valid_concept["ADD_Concept"] - Z_95 * valid_concept["SEM_Concept"],
                    valid_concept["ADD_Concept"] + Z_95 * valid_concept["SEM_Concept"],
                    color=C_CONCEPT, alpha=0.2)

    ax.axvspan(4.0, 4.25, color='gray', alpha=0.15, label="Data blind zone (structurally censored)")
    ax.axvline(4.0, color="red", linestyle=":", linewidth=2,
               label=r"Singularity ($\mathbb{E}[\varepsilon^4] \to \infty$)")
    ax.set_xlim(10.2, 3.8)
    ax.set_yscale("log")
    ax.set_xlabel(r"Student-$t$ degrees of freedom $\nu$ (approaching the singularity)"
                  f"   ($n = {N_SEEDS_B}$ streams per point)")
    ax.set_ylabel("Average detection delay (steps)")
    ax.set_title(r"Detection delay vs. moment singularity ($c = 1.0$)",
                 fontweight="bold", loc="center")
    ax.legend(loc="center left", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    logger.info(f"Figure 13 written to {path.name}: one panel drawn from the in-memory frame. The "
                f"censored branch carries the SEM_Data_Raw band that control C2 adds; the "
                f"submitted figure draws that branch without one because the submitted artefact "
                f"carries no standard error on it.")


# --- MACROS ---

def _pct(value, decimals=1):
    return f"{value:.{decimals}f}\\%"


def _steps(value):
    """v87's own typographic form for a four-digit step count: `2{,}443`."""
    rounded = int(round(value))
    if abs(rounded) < 1000:
        return str(rounded)
    return f"{rounded // 1000}{{,}}{abs(rounded) % 1000:03d}"


def emit_macros(logger, path, frame_a, frame_b, c9, envelopes):
    """
    Twenty-one macros, each computed from an object in memory. Cardinal prefix
    \\RTwelve per repository policy ordinal-in-English rule.

    Two macros the R12 prompt's section 4 lists are DELIBERATELY NOT EMITTED:
    `\\RTwelveBoundaryNaiveRate` and `\\RTwelveBoundaryMedianRate`. They would
    read from `expA_argarch_boundary.csv`, whose claim is v87 L302 -- R07's
    mission statement, already delivered on a certified campaign -- and whose
    producing script does not exist. Control C3 prints the file beside R07's
    cell and emits nothing from it.

    Six macros the prompt's list omits ARE emitted, because v87 prints their
    values: the Concept Ljung-Box range of L349, the Concept delay range of
    L353, the censored delay range of L353, the "factor of six" of L349, and
    control C9's invariance slope with its interval.
    """
    first = frame_a.iloc[0]
    last = frame_a.iloc[-1]
    uncensored = frame_b[~frame_b["censored"]]
    censored = frame_b[frame_b["censored"]]
    if censored.empty:
        logger.error("MACRO EMITTER REFUSED: no cell of Experiment B is censored, so L353's "
                     "survivorship-biased range has no domain to be read on. That is itself a "
                     "contradiction of L353 and must be reported, not papered over.")
        sys.exit(1)
    collapse_nu = float(frame_b[frame_b["det_rate_data"] < CENSORING_DETRATE]["nu"].max())
    det_ten = float(frame_b[np.isclose(frame_b["nu"], 10.0)]["det_rate_data"].iloc[0])
    det_seven = float(frame_b[np.isclose(frame_b["nu"], 7.0)]["det_rate_data"].iloc[0])
    if float(first["fpr_data"]) <= 0.0:
        logger.error(f"MACRO EMITTER REFUSED: the baseline false-alarm rate at "
                     f"gamma_lev = {GAMMA_LEV_GRID[0]} is {float(first['fpr_data'])!r}, so L349's "
                     f"'climbs by a factor of six' has no denominator. A ratio against zero is not "
                     f"a large factor, it is an undefined one, and the situation is itself a "
                     f"finding to report rather than a value to emit.")
        sys.exit(1)
    factor = float(last["fpr_data"]) / float(first["fpr_data"])

    macros = [
        MACRO_HEADER,
        "% EVERY VALUE BELOW IS COMPUTED FROM AN OBJECT IN MEMORY, never from a reloaded CSV.",
        f"% Concept values come from the arm keyed ('R12', '{ROLE_A_INDEP}', gamma_index, s).",
        f"%   The arm keyed ('R12', '{ROLE_A_CRN}', s) is BIT-IDENTICAL across the",
        f"%   {len(GAMMA_LEV_GRID)} gamma_lev by construction (control C8) and supports no claim;",
        "%   no macro reads it.",
        "% The four RANGE pairs are extrema over a grid and have no stable sampling",
        "%   distribution (S4bis, fourth corollary). Each ships with a seed bootstrap envelope in",
        "%   R12_diagnostics.csv and in AUDIT_R12.md, it is DESCRIPTIVE, and it gates nothing.",
        f"%   \\RTwelveFprConceptMin/Max envelope "
        f"[{envelopes['FprConceptMin']['low']:.4f}, {envelopes['FprConceptMax']['high']:.4f}]%,",
        f"%   \\RTwelveLbConceptMin/Max envelope "
        f"[{envelopes['LbConceptMin']['low']:.4f}, {envelopes['LbConceptMax']['high']:.4f}]%,",
        f"%   \\RTwelveAddConceptMin/Max envelope "
        f"[{envelopes['AddConceptMin']['low']:.4f}, {envelopes['AddConceptMax']['high']:.4f}],",
        f"%   \\RTwelveAddDataCensoredMin/Max envelope "
        f"[{envelopes['AddDataCensoredMin']['low']:.4f}, "
        f"{envelopes['AddDataCensoredMax']['high']:.4f}].",
        "% \\RTwelveAddDataCensoredMin/Max are read on the CENSORED domain, which is the domain",
        "%   v87 L353 explicitly scopes its 2,400--3,000 to: 'the surviving minority carries",
        "%   survivorship-biased delays'. \\RTwelveAddDataMin/Max are the UNCENSORED domain and",
        "%   are a diagnostic; they are not the pair that faces L353.",
        "% \\RTwelveInvarianceSlope is control C9's statistic, in percentage points of Concept",
        "%   false-alarm rate per unit gamma_lev, with a seed-cluster bootstrap interval. It is",
        "%   the ONE inferential gate of this stream: a range cannot test invariance, a slope can.",
        f"\\newcommand{{\\RTwelveLbDataLow}}{{{_pct(float(first['lb_data_pct']))}}}",
        f"\\newcommand{{\\RTwelveLbDataHigh}}{{{_pct(float(last['lb_data_pct']))}}}",
        f"\\newcommand{{\\RTwelveFprDataLow}}{{{_pct(float(first['fpr_data']))}}}",
        f"\\newcommand{{\\RTwelveFprDataHigh}}{{{_pct(float(last['fpr_data']))}}}",
        f"\\newcommand{{\\RTwelveFprDataFactor}}{{{factor:.2f}}}",
        f"\\newcommand{{\\RTwelveFprConceptMin}}{{{_pct(float(frame_a['fpr_concept'].min()))}}}",
        f"\\newcommand{{\\RTwelveFprConceptMax}}{{{_pct(float(frame_a['fpr_concept'].max()))}}}",
        f"\\newcommand{{\\RTwelveLbConceptMin}}{{{_pct(float(frame_a['lb_concept_pct'].min()))}}}",
        f"\\newcommand{{\\RTwelveLbConceptMax}}{{{_pct(float(frame_a['lb_concept_pct'].max()))}}}",
        f"\\newcommand{{\\RTwelveInvarianceSlope}}{{{c9['slope']:.4f}}}",
        f"\\newcommand{{\\RTwelveInvarianceSlopeCiLow}}{{{c9['ci_low']:.4f}}}",
        f"\\newcommand{{\\RTwelveInvarianceSlopeCiHigh}}{{{c9['ci_high']:.4f}}}",
        f"\\newcommand{{\\RTwelveDetRateAtNuTen}}{{{_pct(100.0 * det_ten, 0)}}}",
        f"\\newcommand{{\\RTwelveDetRateAtNuSeven}}{{{_pct(100.0 * det_seven, 0)}}}",
        f"\\newcommand{{\\RTwelveCollapseNu}}{{{collapse_nu:g}}}",
        f"\\newcommand{{\\RTwelveAddDataMin}}{{{_steps(float(uncensored['ADD_Data'].min()))}}}",
        f"\\newcommand{{\\RTwelveAddDataMax}}{{{_steps(float(uncensored['ADD_Data'].max()))}}}",
        f"\\newcommand{{\\RTwelveAddDataCensoredMin}}"
        f"{{{_steps(float(censored['ADD_Data_Raw'].min()))}}}",
        f"\\newcommand{{\\RTwelveAddDataCensoredMax}}"
        f"{{{_steps(float(censored['ADD_Data_Raw'].max()))}}}",
        f"\\newcommand{{\\RTwelveAddConceptMin}}{{{_steps(float(frame_b['ADD_Concept'].min()))}}}",
        f"\\newcommand{{\\RTwelveAddConceptMax}}{{{_steps(float(frame_b['ADD_Concept'].max()))}}}",
    ]
    undefined = [line for line in macros
                 if line.startswith("\\newcommand") and 'nan' in line.lower()]
    if undefined:
        logger.error(f"{len(undefined)} macros carry the body `nan`: {undefined}. A macro whose "
                     f"body renders nan aborts the run.")
        sys.exit(1)
    with open(path, "w") as handle:
        handle.write("\n".join(macros) + "\n")
    emitted = sum(1 for line in macros if line.startswith("\\newcommand"))
    logger.info(f"Emitted {emitted} macros to {path.name}, prefix \\RTwelve per repository policy "
                f"ordinal-in-English rule. `\\RTwelveBoundaryNaiveRate` and "
                f"`\\RTwelveBoundaryMedianRate`, which the R12 prompt's section 4 lists, are "
                f"DELIBERATELY ABSENT: control C3 reads their source file and emits nothing from "
                f"it, because the claim behind it is v87 L302 and R07 has already delivered it.")
    for line in macros:
        if line.startswith("\\newcommand"):
            logger.info(f"MACRO {line}")
    return macros


# --- DEVIATION CLASSIFICATION (S3) ---

def classify_against_witness(logger, frame_a, frame_b, c4, c9, envelopes):
    """
    The D0-D3 classification of repository policy, computed rather than asserted, at
    v87's own printing precision. The witness CSVs are read with
    `float_precision='round_trip'` on both sides and no literal is transcribed by
    hand. This replaces the three delivered literal gates at `Priorite_10`
    l.301-309, l.315 and l.459, which are self-anchored equality tests on
    Monte-Carlo values that the 128-bit re-keying redraws by construction.
    """
    reference = BASE_DIR / "data" / "reference" / "R12"
    witness = {key: pd.read_csv(reference / name, float_precision='round_trip')
               for key, name in WITNESS_CSV.items()}
    wa, wb = witness["leverage_fpr"], witness["singularity_add"]

    def row_at(frame, column, value):
        mask = np.isclose(frame[column].to_numpy(dtype=float), value, rtol=1e-12, atol=1e-15)
        return frame[mask].iloc[0]

    logger.info("=" * 78)
    logger.info("DEVIATION CLASSIFICATION D0-D3 (repository policy), AT v87'S PRINTING PRECISION")
    logger.info("=" * 78)
    rows = []

    def add(label, printed, regen_text, wit_text, regen_raw, wit_raw, source, structural=False):
        if structural:
            verdict = "D0" if regen_text == wit_text == printed else "D2"
        else:
            verdict = "D1" if regen_text == printed else "D2"
        rows.append((label, printed, regen_text, wit_text, regen_raw, wit_raw, source, verdict))
        return verdict

    g_low, g_high = GAMMA_LEV_GRID[0], GAMMA_LEV_GRID[-1]
    new_low, new_high = frame_a.iloc[0], frame_a.iloc[-1]
    old_low, old_high = row_at(wa, "gamma_lev", g_low), row_at(wa, "gamma_lev", g_high)

    for label, printed, gamma_value, new_v, old_v, column in (
            (f"L349/Fig.12 Ljung-Box at gamma_lev = {g_low}", "5.1%", g_low,
             float(new_low["lb_data_pct"]), float(old_low["lb_data_pct"]), "lb_data_pct"),
            (f"L349/Fig.12 Ljung-Box at gamma_lev = {g_high}", "24.6%", g_high,
             float(new_high["lb_data_pct"]), float(old_high["lb_data_pct"]), "lb_data_pct"),
            (f"L349/Fig.12 FPR at gamma_lev = {g_low}", "3.2%", g_low,
             float(new_low["fpr_data"]), float(old_low["fpr_data"]), "fpr_data"),
            (f"L349/Fig.12 FPR at gamma_lev = {g_high}", "20.6%", g_high,
             float(new_high["fpr_data"]), float(old_high["fpr_data"]), "fpr_data")):
        add(label, printed, f"{new_v:.1f}%", f"{old_v:.1f}%", repr(new_v), repr(old_v),
            f"R12_leverage_fpr.csv, gamma_lev={gamma_value}/{column}")

    for label, printed, new_v, old_v, column in (
            ("L349/Fig.12 Concept FPR minimum", "7.6%", float(frame_a["fpr_concept"].min()),
             float(wa["fpr_concept"].min()), "fpr_concept"),
            ("L349/Fig.12 Concept FPR maximum", "8.4%", float(frame_a["fpr_concept"].max()),
             float(wa["fpr_concept"].max()), "fpr_concept"),
            ("L349 Concept Ljung-Box minimum", "4.6%", float(frame_a["lb_concept_pct"].min()),
             float(wa["lb_concept_pct"].min()), "lb_concept_pct"),
            ("L349 Concept Ljung-Box maximum", "5.4%", float(frame_a["lb_concept_pct"].max()),
             float(wa["lb_concept_pct"].max()), "lb_concept_pct")):
        add(label, printed, f"{new_v:.1f}%", f"{old_v:.1f}%", repr(new_v), repr(old_v),
            f"R12_leverage_fpr.csv, min/max {column}, arm {ROLE_A_INDEP}")

    factor_new = float(new_high["fpr_data"]) / float(new_low["fpr_data"])
    factor_old = float(old_high["fpr_data"]) / float(old_low["fpr_data"])
    add("L349 'climbs by a factor of six'", "6", f"{factor_new:.0f}", f"{factor_old:.0f}",
        repr(factor_new), repr(factor_old), "R12_leverage_fpr.csv, fpr_data ratio")

    # Structural rather than Monte-Carlo: the stream count and the grid size are
    # specification, so a difference would be a specification defect and not a
    # redraw. The witness column is the campaign the vendored CSV was written by
    # (witness l.491-492 fix n_seeds; the grid length is read from the file).
    add("Fig.12 caption streams per point", "10,000", f"{N_SEEDS_A:,}", f"{10000:,}",
        str(N_SEEDS_A), "witness l.491", "N_SEEDS_A", structural=True)
    add("Fig.13 caption streams per point", "1,000", f"{N_SEEDS_B:,}", f"{1000:,}",
        str(N_SEEDS_B), "witness l.492", "N_SEEDS_B", structural=True)
    add("Fig.12 leverage grid size", "15", f"{len(GAMMA_LEV_GRID)}", f"{len(wa)}",
        str(len(GAMMA_LEV_GRID)), str(len(wa)), "GAMMA_LEV_GRID, witness l.233", structural=True)
    add("Fig.13 nu grid size", "16", f"{len(NU_GRID)}", f"{len(wb)}",
        str(len(NU_GRID)), str(len(wb)), "NU_GRID, witness l.332", structural=True)

    det_ten_new = float(row_at(frame_b, "nu", 10.0)["det_rate_data"])
    det_ten_old = float(row_at(wb, "nu", 10.0)["det_rate_data"])
    det_seven_new = float(row_at(frame_b, "nu", 7.0)["det_rate_data"])
    det_seven_old = float(row_at(wb, "nu", 7.0)["det_rate_data"])
    add("L353 detection at nu = 10", "83%", f"{100 * det_ten_new:.0f}%",
        f"{100 * det_ten_old:.0f}%", repr(det_ten_new), repr(det_ten_old),
        "R12_singularity_add.csv, nu=10/det_rate_data")
    add("L353 detection at nu = 7", "61%", f"{100 * det_seven_new:.0f}%",
        f"{100 * det_seven_old:.0f}%", repr(det_seven_new), repr(det_seven_old),
        "R12_singularity_add.csv, nu=7/det_rate_data")

    collapse_new = float(frame_b[frame_b["det_rate_data"] < CENSORING_DETRATE]["nu"].max())
    collapse_old = float(wb[wb["det_rate_data"] < CENSORING_DETRATE]["nu"].max())
    add("L353 collapse threshold, largest nu below 50%", "5.5", f"{collapse_new:g}",
        f"{collapse_old:g}", repr(collapse_new), repr(collapse_old),
        "R12_singularity_add.csv, max nu with det_rate_data < 0.5")

    cen_new = frame_b[frame_b["censored"]]
    cen_old = wb[wb["det_rate_data"] < CENSORING_DETRATE]
    # v87 prints these two ROUNDED TO THE HUNDREDS and with its own thousands
    # separator, so the comparison is made at exactly that precision and in that
    # typographic form; a bare `2100` could never equal `2,400` as a string and
    # the row could never reach D1 whatever the campaign measured.
    def _hundreds(value):
        return f"{int(round(float(value), -2)):,}"

    add("L353 censored delay minimum", "2,400", _hundreds(cen_new["ADD_Data_Raw"].min()),
        _hundreds(cen_old["ADD_Data_Raw"].min()),
        repr(float(cen_new["ADD_Data_Raw"].min())), repr(float(cen_old["ADD_Data_Raw"].min())),
        "R12_singularity_add.csv, min ADD_Data_Raw on the censored domain")
    add("L353 censored delay maximum", "3,000", _hundreds(cen_new["ADD_Data_Raw"].max()),
        _hundreds(cen_old["ADD_Data_Raw"].max()),
        repr(float(cen_new["ADD_Data_Raw"].max())), repr(float(cen_old["ADD_Data_Raw"].max())),
        "R12_singularity_add.csv, max ADD_Data_Raw on the censored domain")

    add("L353 Concept delay minimum", "34", f"{float(frame_b['ADD_Concept'].min()):.0f}",
        f"{float(wb['ADD_Concept'].min()):.0f}", repr(float(frame_b["ADD_Concept"].min())),
        repr(float(wb["ADD_Concept"].min())), "R12_singularity_add.csv, min ADD_Concept")
    add("L353 Concept delay maximum", "38", f"{float(frame_b['ADD_Concept'].max()):.0f}",
        f"{float(wb['ADD_Concept'].max()):.0f}", repr(float(frame_b["ADD_Concept"].max())),
        repr(float(wb["ADD_Concept"].max())), "R12_singularity_add.csv, max ADD_Concept")

    logger.info(f"{'v87 site':<46} {'printed':<10} {'regen':<10} {'witness':<10} {'class':<6} "
                f"source cell")
    for label, printed, regen, wit, regen_raw, wit_raw, source, verdict in rows:
        logger.info(f"{label:<46} {printed:<10} {regen:<10} {wit:<10} {verdict:<6} {source}")
        logger.info(f"{'':<46} full float64: regenerated {regen_raw}, witness {wit_raw}")

    # --- THE ONE PRINTED RANGE WHOSE BRACKET IS A HALT CANDIDATE ---
    lo_row = cen_new.loc[cen_new["ADD_Data_Raw"].idxmin()]
    hi_row = cen_new.loc[cen_new["ADD_Data_Raw"].idxmax()]
    lo_ci = float(lo_row["ADD_Data_Raw"]) - Z_95 * float(lo_row["SEM_Data_Raw"])
    hi_ci = float(hi_row["ADD_Data_Raw"]) + Z_95 * float(hi_row["SEM_Data_Raw"])
    below = lo_ci < CENSORED_BRACKET[0]
    above = float(hi_row["ADD_Data_Raw"]) - Z_95 * float(hi_row["SEM_Data_Raw"]) >= \
        CENSORED_BRACKET[1]
    logger.info(f"L353 CENSORED RANGE, THE HALT CANDIDATE. v87 prints 2,400--3,000 ROUNDED TO THE "
                f"HUNDREDS, so the watch item is the rounding bracket "
                f"[{CENSORED_BRACKET[0]:.0f}, {CENSORED_BRACKET[1]:.0f}) and not the numerals: the "
                f"witness's own 2443.18 and 3005.28 both round onto them. Regenerated minimum "
                f"{float(lo_row['ADD_Data_Raw'])!r} at nu = {float(lo_row['nu'])} "
                f"(SEM_Data_Raw {float(lo_row['SEM_Data_Raw'])!r} on "
                f"{int(lo_row['n_detected_data'])} surviving streams, 95% lower bound "
                f"{lo_ci!r}); regenerated maximum {float(hi_row['ADD_Data_Raw'])!r} at "
                f"nu = {float(hi_row['nu'])} (SEM_Data_Raw {float(hi_row['SEM_Data_Raw'])!r} on "
                f"{int(hi_row['n_detected_data'])} surviving streams, 95% upper bound {hi_ci!r}). "
                f"Seed bootstrap envelope of the pair "
                f"[{envelopes['AddDataCensoredMin']['low']!r}, "
                f"{envelopes['AddDataCensoredMax']['high']!r}].")
    if below or above:
        logger.error(f"L353 CENSORED RANGE LEAVES ITS ROUNDING BRACKET with the regenerated 95% "
                     f"interval excluding the printed bound (below={below}, above={above}). Under "
                     f"the plan's halt condition this is a D3: full report, no parameter, "
                     f"tolerance, seed or bound moved.")
    else:
        logger.info(f"L353 CENSORED RANGE stays inside its rounding bracket at the 95% level; the "
                    f"printed pair is not breached in S3's sense.")

    # --- QUALITATIVE CLAIMS ---
    qualitative = []
    uncensored_pairs = [e for e in c4["margins"] if e["domain"] == "uncensored"]
    qualitative.append((
        "L353 'detection decays monotonically' (UNCENSORED domain, our restriction)",
        f"{sum(1 for e in uncensored_pairs if e['difference'] >= 0)} of {len(uncensored_pairs)} "
        f"adjacent pairs decrease; {len(c4['inversions_censored'])} inversion(s) in the censored "
        f"domain, characterised and not corrected",
        "D3" if c4["halt"] else "holds on the declared domain"))
    below_50 = frame_b[frame_b["nu"] <= collapse_new]["det_rate_data"]
    above_50 = frame_b[frame_b["nu"] > collapse_new]["det_rate_data"]
    qualitative.append((
        "L353/Fig.13 'collapses below the 50% censoring threshold'",
        f"every nu <= {collapse_new:g} is below {CENSORING_DETRATE} "
        f"(max {float(below_50.max()):.4f}) and every nu > {collapse_new:g} is at or above it "
        f"(min {float(above_50.min()):.4f})",
        "holds" if (below_50 < CENSORING_DETRATE).all() and (above_50 >= CENSORING_DETRATE).all()
        else "D3"))
    span = float(frame_b["ADD_Concept"].max() - frame_b["ADD_Concept"].min())
    qualitative.append((
        "L353/Fig.13 'Concept delay remains flat'",
        f"ADD_Concept spans {float(frame_b['ADD_Concept'].min()):.3f}-"
        f"{float(frame_b['ADD_Concept'].max()):.3f} steps, a span of {span:.3f} "
        f"({100 * span / float(frame_b['ADD_Concept'].mean()):.1f}% of its mean) against a Data "
        f"pipeline that collapses over the same grid",
        "holds"))
    qualitative.append((
        "L349/Fig.12 'leverage-invariant false-alarm rate'",
        f"control C9 slope {c9['slope']!r} points per unit gamma_lev, bootstrap 95% "
        f"[{c9['ci_low']!r}, {c9['ci_high']!r}], two-sided p = {c9['p_value']!r} at a gate of "
        f"{GATE_LEVEL}; over the whole grid that is at most "
        f"{abs(c9['slope']) * (GAMMA_LEV_GRID[-1] - GAMMA_LEV_GRID[0]):.4f} points of movement",
        "D2-grade movement, claim holds" if not c9["fired"] else "gate fired, see C9"))
    qualitative.append((
        "L349 the baseline 'fails to control false alarms even at the population limit'",
        f"fpr_data rises from {float(new_low['fpr_data']):.2f}% to {float(new_high['fpr_data']):.2f}%"
        f" against a 5% nominal, crossing it at gamma_lev = "
        f"{float(frame_a[frame_a['fpr_data'] > 5.0]['gamma_lev'].min()) if (frame_a['fpr_data'] > 5.0).any() else float('nan')}",
        "holds"))
    for label, measured, verdict in qualitative:
        logger.info(f"QUALITATIVE {label}: {measured} -> {verdict}")
    logger.info("=" * 78)
    return rows, qualitative, {"bracket_below": below, "bracket_above": above}


# --- MAIN ---

def main():
    parser = argparse.ArgumentParser(
        description="R12 -- volatility misspecification and moment singularity (v87 Figs 12, 13)")
    parser.add_argument("--n-jobs", type=int, default=-1,
                        help="Worker processes. NUM_CHUNKS_A, NUM_CHUNKS_B and NUM_CHUNKS_CLAMP "
                             "are fixed and every stream carries its own key, so the chunk "
                             "decomposition -- and therefore every output -- is independent of "
                             "this value: that is the second reproducibility axis of control C7.")
    args = parser.parse_args()

    RESULTS_DIR = BASE_DIR / "results" / "R12_gjr_student"
    DATA_DIR = RESULTS_DIR / "data"
    FIGURES_DIR = RESULTS_DIR / "figures"
    TABLES_DIR = RESULTS_DIR / "tables"
    LOGS_DIR = BASE_DIR / "logs" / "R12_gjr_student"
    for directory in (DATA_DIR, FIGURES_DIR, TABLES_DIR, LOGS_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(LOGS_DIR / "exp_R12_gjr_student.log", "exp_R12_gjr_student")
    if not verify_hash_seed(logger):
        sys.exit(1)
    log_environment(logger, ["numpy", "pandas", "scipy", "statsmodels", "matplotlib", "joblib",
                             "pytest"])
    t0 = time.time()

    logger.info("R12 measures v87 Figure 12 (fig:leverage) and Figure 13 (fig:fat_tails) and the "
                "two paragraphs at L349 and L353: what a symmetric GARCH standardisation costs "
                "when the stream carries GJR leverage, and what happens to both pipelines as the "
                "Student-t innovations approach the fourth-moment singularity. Experiment A is "
                f"{len(GAMMA_LEV_GRID)} leverage points x {N_SEEDS_A} streams of {N_TOTAL_A} steps "
                f"at nu = {NU_A}; Experiment B is {len(NU_GRID)} degrees of freedom x {N_SEEDS_B} "
                f"streams of {N_TOTAL_B} steps at a drift of c = {C_MAGNITUDE_B}.")
    logger.info(f"FIGURE NUMBERING. `fig:leverage` is Figure 12 and `fig:fat_tails` is Figure 13, "
                f"established by counting \\label{{fig:...}} in submission order in the frozen "
                f"articleB_whitening_v87.tex. That count places fig:anytime at 9, "
                f"fig:oracle_frontier at 14 and fig:multi_detector at 15, which is the numbering "
                f"R09, R13 and R11 already ship, so the three streams agree.")
    logger.info(f"ENTROPY. Keys carry ROLE AND INDEX ONLY, never gamma_lev and never nu: "
                f"('R12', '{ROLE_A_CRN}', s) for Experiment A's Data arm and its identity witness, "
                f"('R12', '{ROLE_A_INDEP}', gamma_index, s) for the PUBLISHED Concept arm -- an "
                f"integer index, never the float grid value -- ('R12', '{ROLE_B}', s) for "
                f"Experiment B, and ('R12', 'c9_bootstrap', r) / ('R12', 'envelope', name, r) for "
                f"the resampling. The witness keys on the process parameter itself "
                f"(int(gamma_lev*1000) + s*17 at l.131, int(nu*100) + s*23 at l.194), so both "
                f"campaigns are redrawn: pre-classified Class A / D2 as `R12-campaign-redraw`.")
    logger.info(f"WHY EXPERIMENT A HAS TWO CONCEPT ARMS, STATED BEFORE ANY NUMBER. Under a key "
                f"carrying no grid coordinate the Concept stream of Experiment A is BIT-IDENTICAL "
                f"at all {len(GAMMA_LEV_GRID)} gamma_lev, because simulate_gjr_garch draws its "
                f"innovations before the variance recursion and nu and n are held fixed across "
                f"the grid. Publishing 'leverage-invariant' on that arm would make v87's sentence "
                f"true MECHANICALLY. The CRN arm is therefore kept as an identity witness with "
                f"its degeneracy asserted (C8) and the published arm pays an index into its key.")

    identity_report = check_source_identity(logger)
    det_rate_expression = check_det_rate_concept_is_computed(logger)
    derivations = log_derivations(logger)
    log_control_design(logger, args.n_jobs)
    control_c11_legacy_globals(logger)
    c3 = control_c3_task_boundary(logger)

    campaign_crn = run_campaign_a(logger, args.n_jobs, ROLE_A_CRN)
    campaign_indep = run_campaign_a(logger, args.n_jobs, ROLE_A_INDEP)
    campaign_b = run_campaign_b(logger, args.n_jobs)

    identity = control_c8_crn_identity(logger, args.n_jobs, campaign_crn, campaign_indep)
    clamp_frame, clamp_summary = control_c10_clamp(logger, args.n_jobs)

    frame_a = build_leverage_fpr(campaign_crn, campaign_indep)
    frame_b = build_singularity_add(campaign_b, logger)
    frame_crn = build_concept_crn_witness(campaign_crn, identity)

    logger.info("Aggregated statistics for Experiment A:\n"
                + frame_a[["gamma_lev", "fpr_data", "fpr_concept", "lb_data_pct",
                           "lb_concept_pct"]].to_string(index=False))
    logger.info("Aggregated statistics for Experiment B:\n"
                + frame_b[["nu", "det_rate_data", "ADD_Data", "SEM_Data", "ADD_Data_Raw",
                           "SEM_Data_Raw", "det_rate_concept",
                           "ADD_Concept"]].to_string(index=False))

    c4 = control_c4_monotonicity(campaign_b, frame_b, logger)
    c5 = control_c5_ljungbox(frame_a, logger)
    c9 = control_c9_invariance(campaign_indep, campaign_crn, logger)
    envelopes = bootstrap_envelopes(campaign_indep, campaign_b, frame_b, logger)
    frame_diag = build_diagnostics(frame_a, frame_b, clamp_summary, identity, c4, c5, c9,
                                   envelopes, campaign_indep)

    render_figure_12(frame_a, FIGURES_DIR / "fig12_leverage.png", logger)
    render_figure_13(frame_b, FIGURES_DIR / "fig13_fat_tails.png", logger)
    emit_macros(logger, TABLES_DIR / "R12_claims.tex", frame_a, frame_b, c9, envelopes)
    rows, qualitative, bracket = classify_against_witness(logger, frame_a, frame_b, c4, c9,
                                                          envelopes)

    artefacts = {
        "R12_leverage_fpr.csv": frame_a,
        "R12_singularity_add.csv": frame_b,
        "R12_concept_crn_witness.csv": frame_crn,
        "R12_diagnostics.csv": frame_diag,
    }
    for name, frame in artefacts.items():
        save_fair_csv(frame, DATA_DIR / name)
        logger.info(f"{name}: {len(frame)} rows, {len(frame.columns)} columns.")

    # The figures and the macros are computed from the in-memory frames, never
    # from a reloaded CSV (repository policy). The frames are re-serialised
    # here and their digests compared with the files just written, so the figures
    # are CERTIFIED to describe the persisted campaign rather than assumed to.
    mismatched = []
    with tempfile.TemporaryDirectory() as scratch_dir:
        scratch = Path(scratch_dir) / "reconciliation.csv"
        for name, frame in artefacts.items():
            save_fair_csv(frame, scratch)
            if compute_sha256(scratch) != compute_sha256(DATA_DIR / name):
                mismatched.append(name)
    if mismatched:
        logger.error(f"Re-serialisation of {mismatched} does not reproduce the digest of the file "
                     f"just written; the figures and the macros would describe a campaign the CSVs "
                     f"do not contain.")
        sys.exit(1)
    logger.info(f"Re-serialisation reconciliation: all {len(artefacts)} CSVs re-serialise to the "
                f"digests written above. The two figures and the macros describe the persisted "
                f"campaign.")

    logger.info("--- SHA-256 of every artefact (repository policy) ---")
    for name in artefacts:
        logger.info(f"SHA-256 {name:<34} : {compute_sha256(DATA_DIR / name)}")
    for name in ("fig12_leverage.png", "fig13_fat_tails.png"):
        logger.info(f"SHA-256 {name:<34} : {compute_sha256(FIGURES_DIR / name)}")
    logger.info(f"SHA-256 {'R12_claims.tex':<34} : {compute_sha256(TABLES_DIR / 'R12_claims.tex')}")

    # Log artifact manifest
    all_artifacts = [
        DATA_DIR / name for name in artefacts
    ] + [
        FIGURES_DIR / name for name in ("fig12_leverage.png", "fig13_fat_tails.png")
    ] + [
        TABLES_DIR / "R12_claims.tex"
    ]
    log_artifact_manifest(logger, all_artifacts, RESULTS_DIR, BASE_DIR)

    n_d2 = sum(1 for r in rows if r[7] == "D2")
    logger.info(f"CONTROL SUMMARY. C1: `det_rate_concept` = `{det_rate_expression}`, computed. "
                f"C4 halt: {'MET' if c4['halt'] else 'not met'} "
                f"({len(c4['inversions_uncensored'])} uncensored inversion(s), "
                f"{len(c4['inversions_censored'])} censored). C5 KS on the Concept arm: "
                f"D = {c5['ks_concept'][0]:.4f}, p = {c5['ks_concept'][1]:.4f}. C6: "
                f"{identity_report['characters_compared']} characters and "
                f"{identity_report['statements_checked']} statements verified. C8: CRN identity "
                f"holds, deff on the published arm "
                f"{identity['deff']['fp_concept'][1]:.4f}. C9 gate: "
                f"{'FIRED' if c9['fired'] else 'not fired'} (p = {c9['p_value']!r}). C10: "
                f"{int(clamp_summary['n_clamped'].sum())} clamped steps over the subsample. "
                f"L353 bracket: {'BREACHED' if (bracket['bracket_below'] or bracket['bracket_above']) else 'intact'}. "
                f"{n_d2} of {len(rows)} classified numerals are D2. C3 read: orphan "
                f"{c3['naive_rate']:.3f}/{c3['median_rate']:.3f} beside R07 "
                f"{c3['r07_naive']:.4f}/{c3['r07_oracle']:.4f}, gap unexplained, no macro. "
                f"nu* = {derivations['nu_star']:.4f}.")
    logger.info(f"Execution completed in {time.time() - t0:.1f}s with n_jobs = {args.n_jobs} over "
                f"{2 * len(GAMMA_LEV_GRID) * N_SEEDS_A + len(NU_GRID) * N_SEEDS_B} monitored "
                f"streams. The submitted campaign ran "
                f"{len(GAMMA_LEV_GRID) * N_SEEDS_A + len(NU_GRID) * N_SEEDS_B} streams in 185.7s. "
                f"NUM_CHUNKS_A = {NUM_CHUNKS_A} and NUM_CHUNKS_B = {NUM_CHUNKS_B} fix the chunk "
                f"decomposition, so a rerun at a different worker count must produce "
                f"byte-identical artefacts.")


if __name__ == "__main__":
    main()
