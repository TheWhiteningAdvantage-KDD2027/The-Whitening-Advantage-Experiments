#!/usr/bin/env python3
"""
==========================================================================
R18 -- POWER OF THE LJUNG-BOX TEST ON A BINARY STREAM
==========================================================================
R18 reproduces no figure, table or number of articleB_whitening_v87.tex. It is
the global positive control of the repository: the manuscript establishes its
central whitening property by accumulating Ljung--Box NON-REJECTIONS on binary
streams, and a non-rejection bounds nothing unless the instrument can reject.

Four sites of v87 carry that weight:

  L278 (sec:validity_map)  "the binary errors hold the nominal level in every
                            regime (3.3--5.0%; 4.4% pooled)"   360 streams, n = 8000, lag 20
  L290                     "the binary error stream stays strictly white up to
                            Gamma = 200"
  L286 (Fig. 6 caption)    "show no detectable autocorrelation in any GARCH regime"
  L318 (sec:real_world)    "a lag-20 Ljung--Box test finds no serial correlation
                            on any asset ..., licensing the filter"

An exhaustive grep of v87 for `power`, `Type II`, `sensitivit*`, `false
negative`, `fail to reject` returns no Ljung--Box power analysis, and v87 has no
Limitations paragraph. The defect is flagged independently in AUDIT_R06.md
section 8 item 3 ("A rate at nominal is consistent with a test that has no power
at all. Nothing in this repository measures that.") and in WRAPUP_Stream_B1.md
section 6 item 3, whose recommendation was not carried into v87.

WHAT THIS SCRIPT PRODUCES IS A BOUND, NEVER A CONFIRMATION. It converts "we did
not reject" into "we would have rejected an autocorrelation above rho_80 with
probability 0.8". If rho_80 is large, the instrument is blunt, and that is the
result.

THE ALTERNATIVE. Symmetric two-state Markov chain on {0, 1} with stay
probability p_stay = 0.5 + theta. The transition matrix
[[0.5+t, 0.5-t], [0.5-t, 0.5+t]] has eigenvalues 1 and 2*theta and uniform
stationary law, so rho(k) = (2*theta)^k EXACTLY and the marginal stays EXACTLY
Bernoulli(1/2) for every theta: the dependence is isolated from the marginal
calibration, and an alternative that also moved the marginal rate would confound
two mechanisms. Implemented as a parity walk, which is O(n) vectorised and is
the natural carrier of control C4 -- the same uniform vector generates the chain
at every theta by re-thresholding, and its first n entries generate every
horizon.

THE INSTRUMENT. `lb_pvalue` is carried character for character from
experiments/R02_whitening_ljungbox/exp_R02_whitening_ljungbox.py, the
implementation behind the 360-stream claim of L278 and of the Figure 6 caption,
and the identity is asserted at start-up against that file. It is cross-checked
against statsmodels.stats.diagnostic.acorr_ljungbox on a sample of streams, so
that a test of a derived rule compares two implementations rather than restating
one. Its `denom == 0.0 -> (1.0, True)` branch is a degenerate-stream fallback
that AUDIT_R06.md section 2.3 names as biased towards "white": the flag is
counted and logged even at zero, and a non-zero count stops the run.

THE ANALYTIC PREDICTION IS COMPUTED IN-SCRIPT AND DIFFERENCED AGAINST THE
EMPIRICAL CURVE, which makes it a test rather than a description. Under the
local alternative Q -> chi2_nc(m, ncp) with
ncp = n * sum_{k=1..m} rho(k)^2 = n * sum_{k=1..m} (4*theta^2)^k, a geometric sum
of ratio 4*theta^2, and power = P(chi2_nc(m, ncp) > q) with q the 0.95 quantile
of the central chi-square on m degrees of freedom.

References:
- Ljung, G. M. & Box, G. E. P. (1978). On a measure of lack of fit in time
  series models. Biometrika, 65(2), 297-303.
- Box, G. E. P. & Pierce, D. A. (1970). Distribution of residual
  autocorrelations in autoregressive-integrated moving average time series
  models. JASA, 65(332), 1509-1526.
- Wilson, E. B. (1927). Probable inference, the law of succession, and
  statistical inference. JASA, 22(158), 209-212.
- Kish, L. (1965). Survey Sampling. Wiley. (design effect, effective sample size)
- Kolmogorov, A. N. (1933); Smirnov, N. V. (1948). (calibration of p-values)

NOTATION (prompt section 6)
  theta      half-excess of the chain's stay probability, p_stay = 0.5 + theta
  rho(k)     autocorrelation of the binary stream at lag k, equal to (2*theta)^k
  ncp        non-centrality parameter of the limiting chi-square
  theta_80   smallest amplitude at which the test attains 0.80 power
  rho_80     2 * theta_80, the interpretable lag-1 autocorrelation
  m          number of Ljung--Box lags, fixed at 20
  n          stream length in steps
==========================================================================
"""

import sys
from pathlib import Path

# Determinism bootstrap, in the order preamble S7 requires: fair_env imports only
# os and sys, so the environment block is posted before numpy is loaded by anyone
# and before any BLAS thread limit is read. PYTHONHASHSEED cannot be set from
# here -- CPython reads it at interpreter start-up -- so it is exported by
# run_experiment_R18.sh and verified twice below.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from experiments.common.fair_env import enforce_strict_determinism, verify_hash_seed, log_environment

enforce_strict_determinism()

import os

if os.environ.get("PYTHONHASHSEED") != "42":
    sys.exit("FATAL: PYTHONHASHSEED is not 42. Execute via run_experiment_R18.sh")

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
import importlib.metadata
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker
import scipy.stats as stats
from scipy.optimize import brentq, root_scalar
from statsmodels.stats.diagnostic import acorr_ljungbox
from joblib import Parallel, delayed

# river is a HARD dependency: the classifier arm is the one that carries the
# Figure 6 configuration, and an absent river would silently reduce R18 to the
# synthetic arms while still emitting an application CSV. Preamble S4.3 forbids
# that path; the identical defect is recorded on R02 at docs/DEVIATIONS.md
# entry 2.
try:
    import river
    from river import tree as river_tree
except ImportError as exc:  # noqa: F841 -- re-raised as a fatal exit, never swallowed
    sys.exit(f"FATAL: river is missing. R18's classifier arm reproduces the Figure 6 pipeline "
             f"and cannot run without it. Required: river==0.23.0. Details: {exc}")


# --- PROTOCOL SPECIFICATION ---
# There is no v87 specification for R18: the experiment does not appear in the
# manuscript. The test configuration is instead IMPOSED by the streams whose
# non-rejections R18 bounds, read from R02b_rejection_vs_nu.csv and
# R02c_rejection_vs_horizon.csv: n_steps = 8000, lags = 20, n_streams = 1000,
# nominal level 0.05, and the four horizons of the R02c sweep.
N_STEPS = 8000
LB_LAGS = 20
N_STREAMS = 1000
NOMINAL_LEVEL = 0.05
HORIZONS = (2000, 8000, 32000, 128000)
HORIZON_HEADLINE = 8000
# A4 of the plan: the largest horizon runs 36 thresholdings over 1000 streams of
# 128k points, so roughly 4.6e9 values enter autocorrelation estimation for that
# slice alone. It is measured and reported on its own before the rest of the grid
# is launched, and the design is not trimmed if it dominates.
HORIZONS_FIRST_PASS = (128000,)
HORIZONS_SECOND_PASS = (2000, 8000, 32000)

# The theta grid is a design decision: the prompt gives only the domain [0, 0.25].
# The whole transition lives in theta in [0.006, 0.06] -- theta_80 runs from
# 0.0509 at n = 2000 down to 0.0064 at n = 128000 -- so a uniform grid on
# [0, 0.25] would put theta_80 inside the first cell at the large horizons and
# saturate everywhere else. C2 requires monotonicity in n AT FIXED theta, so the
# grid must be common to all four horizons. 16 points per decade over two
# decades, plus the null point and the two anchors.
THETA_GRID_MIN = 0.0025
THETA_POINTS_PER_DECADE = 16
THETA_GRID_DECADES = 2
# theta = 0.05 is on the grid so that the power at rho = 0.10 is MEASURED rather
# than interpolated; theta = 0.10 is the amplitude control C5 verifies.
THETA_ANCHORS = (0.05, 0.10)
N_THETA_EXPECTED = 36

# Application arms. Arm (a) is the HoeffdingTree binary ERROR stream, which is
# what the Fig. 6 and L278 non-rejections were actually computed on; arm (b) is
# the raw sign stream (eps > 0), which is R11's Concept pipeline.
ALPHA_FIXED = 0.08
NU = 7.0
TARGET_VAR = 0.04
# R06's grid, the 13 penalties of the validity map, for the classifier arm.
GAMMA_GRID_CLASSIFIER = (1, 2, 5, 8.16, 11.58, 20, 30.85, 41, 60, 90, 120, 160, 200)
# R11's 20-point target grid, for the sign arm. Its first target lies below the
# attainable floor at alpha = 0.08; see A3 and docs/DEVIATIONS.md
# `R11-gamma-grid-floor`.
GAMMA_GRID_SIGN = tuple(np.concatenate([np.linspace(1.0, 50.0, 10),
                                        np.linspace(60.0, 200.0, 10)]))
N_STREAMS_APPLIED = 1000

# --- CONTROL CONSTANTS, EACH DERIVED FROM A MECHANISM ---
Z_95 = 1.959963984540054
# C3. At 1000 streams the standard error of a proportion is at most
# 0.5/sqrt(1000) = 0.0158114; three of them is 0.0474342. The non-central
# chi-square limit is moreover a LOCAL approximation whose validity degrades as
# ncp grows, so the tolerance is applied only where power_analytic < 0.95 and NO
# tolerance is applied above it. Neither number comes from an observed deviation.
C3_POWER_DOMAIN = 0.95
C3_TOLERANCE = 3.0 * 0.5 / math.sqrt(N_STREAMS)
# C5. The standard error of a sample autocorrelation on n observations is
# 1/sqrt(n); pooled over 10000 streams of 8000 steps the pooled estimator carries
# N = 8e7 pairs, so 4/sqrt(N) is a four-standard-error band. Measured over 8
# independent replicates during planning the deviation had mean -1.7e-5 and
# sd 6.5e-5, which puts the tolerance at 6.8 sd: the control does not fire on
# sampling noise.
C5_STREAMS = 10000
C5_THETA = 0.10
C5_TOLERANCE = 4.0 / math.sqrt(10000.0 * 8000.0)
# C2. An inversion is characterised against the standard error of the PAIRED
# difference -- the grid and the horizons share their streams -- and two standard
# errors is the ordinary two-sided 95% separation of a paired mean. Nothing is
# corrected when it fires.
C2_INVERSION_SE = 2.0
# The cross-check of `lb_pvalue` against statsmodels. Both evaluate the same
# closed form in float64; the only admissible difference is the reassociation of
# a sum over at most n = 128000 terms, whose relative error is bounded by
# n * eps = 1.28e5 * 2.22e-16 = 2.8e-11. The budget is 1e-9 on the Q statistic,
# a factor 35 above that bound, and it is propagated to the p-value through the
# chi-square density rather than compared to it directly, since p spans 300
# orders of magnitude over the grid.
CROSSCHECK_QSTAT_RTOL = 1.0e-9
CROSSCHECK_STREAMS = 25
CROSSCHECK_THETAS = (0.0, 0.01, 0.03)
CROSSCHECK_HORIZONS = (2000, 8000)
BOOTSTRAP_REPLICATES = 2000
POWER_TARGET = 0.80

COLORS = {"empirical": "#04617b", "analytic": "#C62828", "band": "#04617b",
          "classifier": "#E8A000", "sign": "#2ca02c", "reference": "#546E7A"}
HORIZON_COLORS = {2000: "#9467bd", 8000: "#04617b", 32000: "#2ca02c", 128000: "#E8A000"}

# --- SOURCE-SEGMENT IDENTITY ---
# Preamble S4.2 forbids hoisting a scientific primitive into
# experiments/common/, so every routine below is duplicated from the experiment
# that owns it and asserted byte-identical to that file at start-up: the
# duplication is deliberate and it cannot drift. Two solvers collide in name --
# R06 solves by brentq and R11 by bisection, and the two return different betas
# for the same target -- so each is carried under a suffixed name and the
# identity check normalises exactly that one token on the `def` line.
R02_SOURCE = BASE_DIR / "experiments" / "R02_whitening_ljungbox" / "exp_R02_whitening_ljungbox.py"
R06_SOURCE = BASE_DIR / "experiments" / "R06_validity_map" / "exp_R06_validity_map.py"
R11_SOURCE = BASE_DIR / "experiments" / "R11_multi_detector" / "exp_R11_multi_detector.py"
CARRIED_PRIMITIVES = {
    "lb_pvalue": (R02_SOURCE, "lb_pvalue"),
    "gamma_exact": (R02_SOURCE, "gamma_exact"),
    "get_deterministic_seed": (R02_SOURCE, "get_deterministic_seed"),
    "wilson_score_interval": (R02_SOURCE, "wilson_score_interval"),
    "solve_beta_for_gamma_r06": (R06_SOURCE, "solve_beta_for_gamma"),
    "compute_gamma_exact": (R11_SOURCE, "compute_gamma_exact"),
    "solve_beta_for_gamma_r11": (R11_SOURCE, "solve_beta_for_gamma"),
    "simulate_garch11": (R11_SOURCE, "simulate_garch11"),
}
# The GARCH recursion and the HoeffdingTree loop of arm (a) live INSIDE R02's
# `simulate_task` and cannot be extracted as a function. Each carried line is
# checked for presence in that function's source text instead, stripped of
# indentation, which is the strongest identity available on an inlined body.
CARRIED_LINES_R02 = (
    "omega = TARGET_VAR * (1.0 - alpha - beta)",
    "eps = np.zeros(N_STEPS)",
    "h = np.zeros(N_STEPS)",
    "h[0] = omega / (1.0 - alpha - beta) if (alpha + beta) < 1.0 else TARGET_VAR",
    "z = rng.standard_t(NU, size=N_STEPS) * np.sqrt((NU - 2.0) / NU)",
    "eps[0] = np.sqrt(h[0]) * z[0]",
    "for t in range(1, N_STEPS):",
    "h[t] = max(omega + alpha * (eps[t - 1] ** 2) + beta * h[t - 1], 1e-12)",
    "eps[t] = np.sqrt(h[t]) * z[t]",
    "rv = pd.Series(eps).rolling(20, min_periods=1).std(ddof=1).fillna(0.0).values",
    "ht = river_tree.HoeffdingTreeClassifier()",
    "errs = np.zeros(N_STEPS, dtype=float)",
    "for t in range(N_STEPS):",
    "lag1 = eps[t - 1] if t >= 1 else 0.0",
    "lag2 = eps[t - 2] if t >= 2 else 0.0",
    "x_dict = {0: lag1, 1: lag2, 2: abs(lag1), 3: rv[t]}",
    "yt = int(eps[t] > 0)",
    "yp_raw = ht.predict_one(x_dict)",
    "yp = max(yp_raw, key=yp_raw.get) if isinstance(yp_raw, dict) and yp_raw else int(yp_raw or 0)",
    "errs[t] = float(yp != yt)",
    "ht.learn_one(x_dict, yt)",
)


# --- PRIMITIVES CARRIED FROM THE EXPERIMENTS THAT OWN THEM ---
# Do not reformat. Byte identity is checked on the exact source text at start-up,
# trailing whitespace included.


# The instrument itself, behind the 360-stream non-rejections of v87 L278 and of the
# Figure 6 caption. Its `denom == 0.0 -> (1.0, True)` branch is the degenerate-stream
# fallback AUDIT_R06.md section 2.3 names as biased towards "white"; the flag is
# returned, counted and logged even at zero, and a non-zero count stops the run.
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


# The per-point interval. Each grid point rests on 1000 independent streams, so it is
# valid under the paired design; nothing pooled over the grid uses it.
def wilson_score_interval(k: int, n: int, confidence: float = 0.95) -> tuple:
    if n == 0: return 0.0, 0.0
    p_hat = k / n
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n)) / denom
    return max(0.0, float(center - margin)), min(1.0, float(center + margin))


# The repository's canonical seed derivation, in the two-value form: md5 of the
# hex-formatted key, the full 128 bits for SeedSequence and the leading 32 for the
# legacy global states that river and scipy consume (SPECS 1.2 and 1.3).
def get_deterministic_seed(*args) -> tuple:
    def format_arg(arg):
        if isinstance(arg, (float, np.floating)):
            return float(arg).hex()
        return str(arg)
    s = "_".join(map(format_arg, args))
    h = hashlib.md5(s.encode('utf-8')).hexdigest()
    # Returns (full_128_bit_entropy, legacy_32_bit_seed)
    return int(h, 16), int(h[:8], 16)


# Closed-form penalty, used by arm (a) on R06's grid.
def gamma_exact(alpha: float, beta: float) -> float:
    if alpha == 0.0 and beta == 0.0:
        return 1.0
    phi = alpha + beta
    denom = 1.0 - 2.0 * alpha * beta - beta ** 2
    if denom <= 0.0 or phi >= 1.0:
        return float('inf')
    rho1 = alpha * (1.0 - beta * phi) / denom
    return 1.0 + 2.0 * rho1 / (1.0 - phi)


# R06's solver, by brentq, for arm (a). Renamed on its `def` line ONLY, because R11's
# solver carries the same name and returns a different beta for the same target; the
# identity check normalises exactly that token.
def solve_beta_for_gamma_r06(alpha: float, target_gamma: float) -> float:
    """Solves for beta to attain a target Gamma given alpha."""
    if target_gamma == 1.0:
        return 0.0
    # Find the pole where the denominator (1 - 2*alpha*beta - beta^2) hits 0.
    beta_pole = np.sqrt(alpha**2 + 1.0) - alpha
    
    def f(beta):
        return gamma_exact(alpha, beta) - target_gamma
    
    res = root_scalar(f, bracket=[0.0, beta_pole - 1e-6], method='brentq')
    return res.root


# R11's closed form, whose value at beta = 0 is the attainable penalty floor arm (b)
# needs in order to declare its first grid point unattainable (A3).
def compute_gamma_exact(alpha, beta):
    phi = alpha + beta
    if phi >= 1.0: return np.inf
    denom = 1 - 2 * alpha * beta - beta**2
    if denom <= 0: return (1 + phi) / (1 - phi)
    rho1 = alpha * (1 - beta * phi) / denom
    return max(1.0, 1 + 2 * rho1 / (1 - phi))


# R11's solver, by bisection, for arm (b). Renamed on its `def` line only.
def solve_beta_for_gamma_r11(alpha, target_gamma):
    if target_gamma <= 1.0: return 0.0
    lo, hi = 0.0, 1.0 - alpha - 1e-6
    for _ in range(100):
        mid = (lo + hi) / 2
        if compute_gamma_exact(alpha, mid) < target_gamma: lo = mid
        else: hi = mid
    return mid


# R11's generator for arm (b). Its docstring is carried with it: byte identity is
# asserted on the whole segment, and the assertion it records -- the innovation vector
# drawn before the variance recursion -- is exactly what forces `gamma` into the seed
# key of that arm.
def simulate_garch11(n, omega, alpha, beta, nu=7.0, rng=None):
    """
    ADAPTED. The submitted signature is `(n, omega, alpha, beta, nu=7.0,
    seed=42)` and builds `np.random.RandomState(seed)` on its first statement.
    Prompt S2.1 requires the migration to a 128-bit SeedSequence keyed on role
    and index, so the generator is constructed by the caller and passed in.

    Every line from `sigma2_unc` to `return eps` is asserted byte-identical to
    the witness at start-up (control C8), and both source segments are quoted in
    the log.
    """
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


# --- ROUTINES SPECIFIC TO R18 ---

def source_segments(path, names):
    """
    Source text of the named top-level functions, extracted by position rather
    than by import: importing another experiment would execute its environment
    block, its logger and its output directory creation.
    """
    text = Path(path).read_text()
    tree = ast.parse(text)
    return {node.name: ast.get_source_segment(text, node)
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in names}


def check_source_identity(logger):
    """
    Byte identity of every carried primitive against the experiment that owns it,
    and presence of every carried inline statement in R02's `simulate_task`.

    Deterministic, trigger probability zero unless a copy has drifted.
    """
    own = source_segments(Path(__file__).resolve(), set(CARRIED_PRIMITIVES))
    compared = 0
    for local_name, (path, remote_name) in sorted(CARRIED_PRIMITIVES.items()):
        remote = source_segments(path, {remote_name}).get(remote_name)
        mine = own.get(local_name)
        if remote is None or mine is None:
            logger.error(f"Source-identity failure: {local_name} could not be extracted "
                         f"({path.name}::{remote_name}).")
            sys.exit(1)
        normalised = mine.replace(f"def {local_name}(", f"def {remote_name}(", 1)
        if normalised != remote:
            logger.error(f"Source-identity failure on {local_name}: the copy has drifted from "
                         f"{path.name}::{remote_name}.")
            sys.exit(1)
        compared += len(remote)
    task = source_segments(R02_SOURCE, {"simulate_task"}).get("simulate_task")
    if task is None:
        logger.error("Source-identity failure: exp_R02_whitening_ljungbox.py::simulate_task "
                     "could not be extracted.")
        sys.exit(1)
    task_lines = {line.strip() for line in task.splitlines()}
    missing = [line for line in CARRIED_LINES_R02 if line not in task_lines]
    if missing:
        logger.error(f"Source-identity failure: {len(missing)} carried statements are absent from "
                     f"R02's simulate_task: {missing}")
        sys.exit(1)
    logger.info(f"Source-identity check: {len(CARRIED_PRIMITIVES)} primitives byte-identical to "
                f"their owning experiment ({compared} characters compared), and the "
                f"{len(CARRIED_LINES_R02)} carried statements of arm (a) all present in "
                f"exp_R02_whitening_ljungbox.py::simulate_task. Preamble S4.2 forbids hoisting any "
                f"of them into experiments/common/, so the duplication is deliberate; the two "
                f"`solve_beta_for_gamma` copies are compared with their `def` line renamed, which is "
                f"the only token that differs.")


def rng_for(*key):
    """Generator seeded by the full 128-bit condensate of a task's key."""
    seed_128, _legacy = get_deterministic_seed(*key)
    return np.random.default_rng(np.random.SeedSequence(seed_128))


def theta_grid():
    """
    36 amplitudes: the null point, 16 per decade over [0.0025, 0.25], and the two
    anchors. Built once and asserted against its cardinality, so that a change of
    resolution cannot pass unnoticed.
    """
    n_geom = THETA_POINTS_PER_DECADE * THETA_GRID_DECADES + 1
    geometric = THETA_GRID_MIN * 10.0 ** (np.arange(n_geom) / THETA_POINTS_PER_DECADE)
    values = sorted(set([0.0]) | set(float(v) for v in geometric) | set(THETA_ANCHORS))
    return tuple(values)


def markov_binary_stream(u, theta):
    """
    Parity-walk realisation of the symmetric two-state chain with stay
    probability 0.5 + theta, driven by a uniform vector `u`.

    `flip_t = 1{u_t > 0.5 + theta}` has probability 0.5 - theta, and
    `x_t = x_{t-1} XOR flip_t`. The initial state takes `u[0]` at the fixed
    threshold 0.5, so x_0 is exactly Bernoulli(1/2) and the chain starts in its
    stationary law; every later entry of `u` is a transition.

    THIS IS WHAT MAKES C4 STRUCTURAL RATHER THAN DECLARED: the same `u`
    generates the chain at every theta by re-thresholding, and its first n
    entries generate every horizon, so no seed depends on theta or on n_steps.
    The coupling is monotone -- raising theta only removes flips -- so the
    resulting power curve is paired across the whole grid.
    """
    flip = u > (0.5 + theta)
    flip[0] = u[0] > 0.5
    return np.bitwise_xor.accumulate(flip)


def ncp_analytic(theta, n, lags=LB_LAGS):
    """
    ncp = n * sum_{k=1..m} rho(k)^2 with rho(k) = (2*theta)^k, hence a geometric
    sum of ratio r = 4*theta^2 and first term r.
    """
    r = 4.0 * float(theta) * float(theta)
    if r == 0.0:
        return 0.0
    if r == 1.0:
        return float(n) * lags
    return float(n) * r * (1.0 - r ** lags) / (1.0 - r)


def power_analytic(theta, n, quantile, lags=LB_LAGS):
    """P(chi2_nc(m, ncp) > q), the limiting power under the local alternative."""
    ncp = ncp_analytic(theta, n, lags)
    if ncp == 0.0:
        return float(stats.chi2.sf(quantile, df=lags))
    return float(stats.ncx2.sf(quantile, lags, ncp))


def theta_80_analytic(n, quantile, lags=LB_LAGS, target=POWER_TARGET):
    """
    Root of power_analytic(theta, n) = target, by brentq on the analytic
    expression. Bracketed by the null point, where the power is the level, and by
    the top of the domain the prompt fixes.
    """
    lo, hi = 1e-9, 0.25
    f_lo = power_analytic(lo, n, quantile, lags) - target
    f_hi = power_analytic(hi, n, quantile, lags) - target
    if f_lo * f_hi > 0.0:
        return float('nan')
    return float(brentq(lambda t: power_analytic(t, n, quantile, lags) - target,
                        lo, hi, xtol=1e-15, rtol=8.9e-16))


def interpolate_threshold(thetas, rates, target=POWER_TARGET):
    """
    Smallest amplitude at which the EMPIRICAL curve reaches `target`, by
    log-linear interpolation between the two grid points that bracket the
    crossing. The abscissa is interpolated in log-theta because the grid is
    geometric and because theta_80 obeys an n^{-1/2} law, which is linear in
    that coordinate.

    Returns nan when the curve does not reach the target anywhere on the grid,
    which is a reportable outcome and not an error.
    """
    thetas = np.asarray(thetas, dtype=float)
    rates = np.asarray(rates, dtype=float)
    for i in range(1, len(thetas)):
        if rates[i] >= target > rates[i - 1]:
            t_lo, t_hi = thetas[i - 1], thetas[i]
            p_lo, p_hi = rates[i - 1], rates[i]
            if p_hi == p_lo:
                return float(t_hi)
            if t_lo <= 0.0:
                return float(t_lo + (target - p_lo) * (t_hi - t_lo) / (p_hi - p_lo))
            frac = (target - p_lo) / (p_hi - p_lo)
            return float(math.exp(math.log(t_lo) + frac * (math.log(t_hi) - math.log(t_lo))))
    return float('nan')


def clamped(value):
    """Preamble S7: every interval bound is clipped to [0, 1] before persistence."""
    if not np.isfinite(value):
        return float('nan')
    return max(0.0, min(1.0, float(value)))


def wilson_bounds(k, n):
    """Wilson score interval, clipped, on the carried R02 implementation."""
    low, high = wilson_score_interval(int(k), int(n))
    return clamped(low), clamped(high)


def ks_uniform(pvalues):
    """
    Two-sided Kolmogorov--Smirnov distance between an empirical distribution and
    Uniform(0, 1), reimplemented rather than delegated so that the bootstrap
    below and the gate above share one definition.
    """
    p = np.sort(np.asarray(pvalues, dtype=float))
    n = p.size
    i = np.arange(1, n + 1)
    return float(max(np.max(i / n - p), np.max(p - (i - 1) / n)))


def bootstrap_max_ks(pvalue_matrix, replicates, rng):
    """
    Null distribution of `max` over horizons of the KS distance, obtained by
    resampling WHOLE STREAM INDICES.

    The four horizons are nested prefixes of the same 1000 streams, so their KS
    statistics are dependent and a pooled KS over 4000 p-values would be invalid.
    Resampling stream indices carries that dependence; each replicate is scored
    against the ORIGINAL empirical distribution of its own horizon, which is the
    ordinary bootstrap approximation to the sampling variation of an empirical
    distribution function around its population law. Under the null that law is
    Uniform(0, 1), which is what the observed statistic is scored against.

    `pvalue_matrix` is (n_streams, n_horizons).
    """
    n_streams, n_h = pvalue_matrix.shape
    ranks = np.empty((n_streams, n_h), dtype=np.int64)
    for h in range(n_h):
        order = np.argsort(pvalue_matrix[:, h], kind='stable')
        ranks[order, h] = np.arange(n_streams)
    steps = (np.arange(1, n_streams + 1)) / n_streams
    draws = np.empty(replicates, dtype=float)
    for b in range(replicates):
        idx = rng.integers(0, n_streams, size=n_streams)
        worst = 0.0
        for h in range(n_h):
            counts = np.bincount(ranks[idx, h], minlength=n_streams)
            cum = np.cumsum(counts) / n_streams
            worst = max(worst, float(np.max(np.abs(cum - steps))))
        draws[b] = worst
    return draws


def kish_design_effect(matrix):
    """
    Kish design effect of a proportion measured on a paired grid: the ratio of
    the cluster-robust variance of the pooled rate to the variance a simple
    random sample of the same size would have. `matrix` is streams x grid points.

    A value of 1 means the readings carry independent information; a value of d
    means the n readings carry the information of n/d independent ones. Carried
    from R11, where it measures the same object on the same kind of paired grid.
    """
    p = float(matrix.mean())
    if p <= 0.0 or p >= 1.0:
        return float('nan')
    se_cluster = float(np.std(matrix.mean(axis=1), ddof=1) / math.sqrt(matrix.shape[0]))
    se_srs = math.sqrt(p * (1.0 - p) / matrix.size)
    return (se_cluster / se_srs) ** 2


def pooled_lag1(sums, cross, first, last, n_steps):
    """
    Pooled lag-1 autocorrelation of binary streams, with a GLOBAL mean over all
    within-stream pairs.

    The estimator matches the N = n_streams * n_steps that the prescribed C5
    tolerance 4/sqrt(N) is written against, and it uses the same denominator
    convention as `lb_pvalue`'s r_1 -- sum of squared deviations over the whole
    stream, not over the n-1 pairs.

    Every argument is a per-stream aggregate: `sums` = sum_t x_t,
    `cross` = sum_t x_t x_{t+1}, `first` = x_0, `last` = x_{n-1}. Keeping the
    aggregates rather than the streams is what makes the cluster bootstrap below
    possible without holding 8e7 values in memory.
    """
    sums = np.asarray(sums, dtype=float)
    cross = np.asarray(cross, dtype=float)
    first = np.asarray(first, dtype=float)
    last = np.asarray(last, dtype=float)
    total = float(sums.size) * n_steps
    m = float(sums.sum()) / total
    num = float(np.sum(cross - m * (sums - last) - m * (sums - first) + (n_steps - 1) * m * m))
    den = float(np.sum(sums * (1.0 - 2.0 * m) + n_steps * m * m))
    if den == 0.0:
        return float('nan')
    return num / den


def bootstrap_pooled_lag1(sums, cross, first, last, n_steps, replicates, rng):
    """Cluster bootstrap of `pooled_lag1`, resampling whole stream indices."""
    n = len(sums)
    draws = np.empty(replicates, dtype=float)
    for b in range(replicates):
        idx = rng.integers(0, n, size=n)
        draws[b] = pooled_lag1(sums[idx], cross[idx], first[idx], last[idx], n_steps)
    return draws


def power_interval_from_rho(rho_low, rho_high, n, quantile):
    """
    Analytic power over an interval of lag-1 autocorrelation, mapped onto the
    Markov alternative that has that lag-1 autocorrelation (theta = rho / 2).

    The power is an EVEN function of rho with its minimum at rho = 0, so an
    interval that straddles zero has the level as its lower bound. Propagating
    the endpoints without that check would report the smaller of two positive
    amplitudes as a lower bound on the power, which it is not.
    """
    lo = power_analytic(abs(rho_low) / 2.0, n, quantile)
    hi = power_analytic(abs(rho_high) / 2.0, n, quantile)
    if rho_low <= 0.0 <= rho_high:
        return clamped(power_analytic(0.0, n, quantile)), clamped(max(lo, hi))
    return clamped(min(lo, hi)), clamped(max(lo, hi))


# --- WORKERS ---

def worker_power(index, thetas, horizons, n_max):
    """
    One stream of common random numbers, thresholded at every theta and read at
    every requested horizon. Returns the p-value matrix, the degenerate-branch
    count and its log lines; per SPECS 1.5 a worker never writes to the log.
    """
    logs = []
    rng = rng_for("R18", "power", index)
    u = rng.random(n_max)
    out = np.empty((len(thetas), len(horizons)), dtype=float)
    degenerate = 0
    for ti, theta in enumerate(thetas):
        x = markov_binary_stream(u, theta).astype(np.float64)
        for hi, n in enumerate(horizons):
            p, deg = lb_pvalue(x[:n], LB_LAGS)
            out[ti, hi] = p
            if deg:
                degenerate += 1
                logs.append(('WARNING', f"Degenerate Ljung-Box (denom = 0) at stream {index}, "
                                        f"theta = {theta!r}, n = {n}."))
    return index, out, degenerate, logs


def worker_generator_check(index, theta, n_steps):
    """C5: the per-stream aggregates of the pooled lag-1 estimator."""
    rng = rng_for("R18", "generator_check", index)
    u = rng.random(n_steps)
    x = markov_binary_stream(u, theta).astype(np.float64)
    return (float(x.sum()), float(np.dot(x[:-1], x[1:])), float(x[0]), float(x[-1]))


def worker_sign_garch(gamma, index, alpha, beta, omega, n_steps):
    """
    Arm (b): the raw sign stream of an R11 Concept pipeline.

    `gamma` IS in the seed key, and this departure from C4 is declared rather
    than hidden. R11's own docstring asserts that `simulate_garch11` draws the
    whole innovation vector before the variance recursion, so
    sign(eps_t) = sign(z_t) exactly and the sign stream would be BIT-IDENTICAL
    at all twenty penalties under a Gamma-free key: the arm would measure one
    number repeated twenty times. R11 keeps such an arm as an identity witness;
    R18 needs twenty independent readings instead, so the key carries Gamma.
    """
    logs = []
    rng = rng_for("R18", "sign_garch", gamma, index)
    eps = simulate_garch11(n_steps, omega, alpha, beta, NU, rng)
    x = (eps > 0).astype(np.float64)
    p, deg = lb_pvalue(x, LB_LAGS)
    if deg:
        logs.append(('WARNING', f"Degenerate Ljung-Box (denom = 0) on the sign arm at "
                                f"Gamma = {gamma}, stream {index}."))
    return (float(p), int(deg), float(x.mean()),
            float(x.sum()), float(np.dot(x[:-1], x[1:])), float(x[0]), float(x[-1]), logs)


def worker_sign_classifier(gamma, index, alpha, beta, n_steps):
    """
    Arm (a): the HoeffdingTree binary ERROR stream, which is the stream the
    Figure 6 and L278 non-rejections were computed on.

    The GARCH recursion, the realised-volatility feature and the classifier loop
    are carried statement by statement from
    exp_R02_whitening_ljungbox.py::simulate_task; every carried line is checked
    for presence in that function at start-up. Per SPECS 1.3 the worker pins the
    two legacy global states before touching river or scipy, since both consume
    inherited global entropy.
    """
    logs = []
    seed_128, legacy_seed = get_deterministic_seed("R18", "sign_classifier", gamma, index)
    np.random.seed(legacy_seed)
    random.seed(legacy_seed)
    rng = np.random.default_rng(np.random.SeedSequence(seed_128))

    omega = TARGET_VAR * (1.0 - alpha - beta)
    eps = np.zeros(n_steps)
    h = np.zeros(n_steps)
    h[0] = omega / (1.0 - alpha - beta) if (alpha + beta) < 1.0 else TARGET_VAR

    z = rng.standard_t(NU, size=n_steps) * np.sqrt((NU - 2.0) / NU)
    eps[0] = np.sqrt(h[0]) * z[0]

    for t in range(1, n_steps):
        h[t] = max(omega + alpha * (eps[t - 1] ** 2) + beta * h[t - 1], 1e-12)
        eps[t] = np.sqrt(h[t]) * z[t]

    rv = pd.Series(eps).rolling(20, min_periods=1).std(ddof=1).fillna(0.0).values

    ht = river_tree.HoeffdingTreeClassifier()
    errs = np.zeros(n_steps, dtype=float)

    for t in range(n_steps):
        lag1 = eps[t - 1] if t >= 1 else 0.0
        lag2 = eps[t - 2] if t >= 2 else 0.0
        x_dict = {0: lag1, 1: lag2, 2: abs(lag1), 3: rv[t]}
        yt = int(eps[t] > 0)
        yp_raw = ht.predict_one(x_dict)
        yp = max(yp_raw, key=yp_raw.get) if isinstance(yp_raw, dict) and yp_raw else int(yp_raw or 0)
        errs[t] = float(yp != yt)
        ht.learn_one(x_dict, yt)

    p, deg = lb_pvalue(errs, LB_LAGS)
    if deg:
        logs.append(('WARNING', f"Degenerate Ljung-Box (denom = 0) on the classifier arm at "
                                f"Gamma = {gamma}, stream {index}."))
    return (float(p), int(deg), float(errs.mean()),
            float(errs.sum()), float(np.dot(errs[:-1], errs[1:])), float(errs[0]),
            float(errs[-1]), logs)


def main():
    parser = argparse.ArgumentParser(
        description="R18 -- power of the Ljung-Box test on a binary stream")
    parser.add_argument("--n-jobs", type=int, default=-1,
                        help="Worker processes. Outputs do not depend on this value: every task "
                             "carries its own seed.")
    args = parser.parse_args()

    # No --fast flag. There is one code path only, so no degraded path exists to
    # stamp, and preamble S4.3 asks that a degraded path be either impossible or
    # named in the artefact.
    RESULTS_DIR = BASE_DIR / "results" / "R18_ljungbox_power"
    DATA_DIR = RESULTS_DIR / "data"
    FIGURES_DIR = RESULTS_DIR / "figures"
    TABLES_DIR = RESULTS_DIR / "tables"
    LOGS_DIR = BASE_DIR / "logs" / "R18_ljungbox_power"
    for d in (DATA_DIR, FIGURES_DIR, TABLES_DIR, LOGS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(LOGS_DIR / "exp_R18_ljungbox_power.log", "exp_R18_ljungbox_power")
    if not verify_hash_seed(logger):
        sys.exit(1)
    log_environment(logger, ["numpy", "pandas", "scipy", "statsmodels", "matplotlib", "joblib",
                             "river", "pytest"])
    logger.info("R18 reproduces no figure, table or number of v87. It bounds what the manuscript's "
                "Ljung-Box NON-REJECTIONS exclude, at the four sites that carry them: L278, L290, "
                "the Figure 6 caption at L286, and L318. Its output is a bound.")
    t0 = time.time()

    check_source_identity(logger)

    # --- SPECIFICATION, FIXED BEFORE ANY MEASUREMENT ---
    thetas = theta_grid()
    quantile = float(stats.chi2.ppf(1.0 - NOMINAL_LEVEL, LB_LAGS))
    spec = {
        "n_theta": (len(thetas), N_THETA_EXPECTED),
        "theta_min_positive": (min(t for t in thetas if t > 0), THETA_GRID_MIN),
        "theta_max": (max(thetas), 0.25),
        "n_horizons": (len(HORIZONS), 4),
        "n_steps_headline": (HORIZON_HEADLINE, 8000),
        "lags": (LB_LAGS, 20),
        "n_streams": (N_STREAMS, 1000),
        "nominal_level": (NOMINAL_LEVEL, 0.05),
        "c5_streams": (C5_STREAMS, 10000),
        "c5_theta": (C5_THETA, 0.10),
        "alpha_fixed": (ALPHA_FIXED, 0.08),
        "nu": (NU, 7.0),
        "n_gamma_classifier": (len(GAMMA_GRID_CLASSIFIER), 13),
        "n_gamma_sign": (len(GAMMA_GRID_SIGN), 20),
    }
    for name, (observed, required) in spec.items():
        if observed != required:
            logger.error(f"Specification mismatch on {name}: {observed} != {required}. The test "
                         "configuration is imposed by the streams whose non-rejections R18 bounds, "
                         "and the script is what must yield.")
            sys.exit(1)
    logger.info(f"Specification: {len(thetas)} amplitudes from {min(thetas)} to {max(thetas)} "
                f"({THETA_POINTS_PER_DECADE} per decade on [{THETA_GRID_MIN}, 0.25] plus the null "
                f"point and the anchors {THETA_ANCHORS}), horizons {HORIZONS}, {N_STREAMS} streams "
                f"per point, Ljung-Box at lag {LB_LAGS}, nominal level {NOMINAL_LEVEL}, "
                f"chi2 quantile q = {quantile!r}.")
    logger.info("Theta grid: " + ", ".join(f"{t:.6f}" for t in thetas))
    logger.info(f"C4 is structural: the seed key is ('R18', 'power', index) with NO theta and NO "
                f"n_steps, so one uniform vector of length {max(HORIZONS)} generates the chain at "
                f"every amplitude by re-thresholding and its first n entries generate every "
                f"horizon. The grid is paired by construction.")

    # --- THE INSTRUMENT, CROSS-CHECKED AGAINST A SECOND IMPLEMENTATION ---
    # R06's doctrine: a test of a derived rule must compare two implementations,
    # not restate one. The budget is derived above from the reassociation of a
    # float64 sum over at most n terms and is propagated to the p-value scale
    # through the chi-square density, since p spans 300 orders of magnitude.
    worst_ratio, worst_detail, n_compared = 0.0, "", 0
    for index in range(CROSSCHECK_STREAMS):
        u = rng_for("R18", "power", index).random(max(CROSSCHECK_HORIZONS))
        for theta in CROSSCHECK_THETAS:
            x = markov_binary_stream(u, theta).astype(np.float64)
            for n in CROSSCHECK_HORIZONS:
                mine, _deg = lb_pvalue(x[:n], LB_LAGS)
                table = acorr_ljungbox(x[:n], lags=[LB_LAGS], return_df=True)
                q_sm = float(table['lb_stat'].iloc[0])
                p_sm = float(table['lb_pvalue'].iloc[0])
                budget = float(stats.chi2.pdf(q_sm, LB_LAGS)) * q_sm * CROSSCHECK_QSTAT_RTOL + 1e-15
                ratio = abs(mine - p_sm) / budget
                n_compared += 1
                if ratio > worst_ratio:
                    worst_ratio = ratio
                    worst_detail = (f"stream {index}, theta = {theta}, n = {n}: "
                                    f"{mine!r} against {p_sm!r}, budget {budget:.3e}")
    logger.info(f"Instrument cross-check: {n_compared} Ljung-Box p-values from the carried R02 "
                f"`lb_pvalue` against statsmodels.acorr_ljungbox. Worst deviation is "
                f"{worst_ratio:.4f} of its own budget ({worst_detail}). The budget is "
                f"chi2.pdf(q) * q * {CROSSCHECK_QSTAT_RTOL:g}, the float64 reassociation error of a "
                f"sum over n <= {max(CROSSCHECK_HORIZONS)} terms propagated to the p-value scale.")
    if worst_ratio > 1.0:
        logger.error("Instrument cross-check failure: the two implementations differ by more than "
                     "the float64 reassociation budget. One of them does not compute the Ljung-Box "
                     "statistic, and nothing downstream is interpretable.")
        sys.exit(1)

    # =====================================================================
    # C5 -- GENERATOR VERIFICATION, BEFORE ANY POWER IS READ
    # =====================================================================
    t_c5 = time.time()
    c5 = Parallel(n_jobs=args.n_jobs)(
        delayed(worker_generator_check)(i, C5_THETA, N_STEPS) for i in range(C5_STREAMS))
    c5_sums = np.array([row[0] for row in c5])
    c5_cross = np.array([row[1] for row in c5])
    c5_first = np.array([row[2] for row in c5])
    c5_last = np.array([row[3] for row in c5])
    rho_c5 = pooled_lag1(c5_sums, c5_cross, c5_first, c5_last, N_STEPS)
    rho_target = 2.0 * C5_THETA
    c5_deviation = rho_c5 - rho_target
    c5_n_obs = C5_STREAMS * N_STEPS
    c5_ones = int(round(float(c5_sums.sum())))
    c5_rate = c5_ones / c5_n_obs
    c5_low, c5_high = wilson_bounds(c5_ones, c5_n_obs)
    # The Wilson interval assumes independent draws. On a chain with rho = 0.2
    # the variance of the mean is inflated by (1+rho)/(1-rho) = 1.5, so the
    # honest interval is sqrt(1.5) wider; both are reported and the prescribed
    # one is the criterion, exactly as written.
    inflation = math.sqrt((1.0 + rho_target) / (1.0 - rho_target))
    c5_low_dep = clamped(c5_rate - inflation * (c5_rate - c5_low))
    c5_high_dep = clamped(c5_rate + inflation * (c5_high - c5_rate))
    logger.info(f"C5 generator check, {C5_STREAMS} streams of {N_STEPS} steps at theta = {C5_THETA}: "
                f"pooled lag-1 autocorrelation {rho_c5!r} against the exact {rho_target}, deviation "
                f"{c5_deviation:+.3e} for a tolerance of {C5_TOLERANCE:.3e} = 4/sqrt("
                f"{C5_STREAMS}*{N_STEPS}), i.e. {abs(c5_deviation) / C5_TOLERANCE:.3f} of the "
                f"budget. Marginal rate {c5_rate:.8f}, Wilson [{c5_low:.8f}, {c5_high:.8f}] on "
                f"{c5_n_obs} observations, and [{c5_low_dep:.8f}, {c5_high_dep:.8f}] after the "
                f"sqrt((1+rho)/(1-rho)) = {inflation:.4f} inflation the chain's own dependence "
                f"imposes. The tolerance is four standard errors of a sample autocorrelation on "
                f"N observations, 1/sqrt(N); it comes from the estimator, not from this draw.")
    if abs(c5_deviation) > C5_TOLERANCE:
        logger.error("C5 failure on the autocorrelation: the generator does not implement the "
                     "announced alternative and nothing else is interpretable.")
        sys.exit(1)
    if not (c5_low <= 0.5 <= c5_high):
        logger.error(f"C5 failure on the marginal: the Wilson interval [{c5_low}, {c5_high}] does "
                     f"not cover 0.5, so the chain's stationary law is not the uniform one and the "
                     f"dependence is not isolated from the marginal calibration.")
        sys.exit(1)
    logger.info(f"C5 elapsed {time.time() - t_c5:.1f}s. Trigger probability under a correct "
                f"generator: the autocorrelation arm is a four-sigma band, so 6.3e-5 two-sided; the "
                f"marginal arm is a 95% Wilson interval, so 5%. Both are single tests, below the "
                f"5% threshold of preamble S4bis for the first and at it for the second.")

    # =====================================================================
    # THE POWER GRID. A4: THE LARGEST HORIZON IS MEASURED AND REPORTED ALONE
    # =====================================================================
    n_theta = len(thetas)
    pvalues = {n: np.empty((N_STREAMS, n_theta), dtype=float) for n in HORIZONS}
    degenerate_total = 0

    t_pass1 = time.time()
    logger.info(f"Pass 1 of the grid: horizon {HORIZONS_FIRST_PASS[0]} alone, {n_theta} amplitudes "
                f"x {N_STREAMS} streams. Roughly "
                f"{n_theta * N_STREAMS * HORIZONS_FIRST_PASS[0] / 1e9:.1f}e9 values enter "
                f"autocorrelation estimation for this slice; A4 of the plan requires it measured "
                f"and reported before the rest of the grid is launched.")
    results = Parallel(n_jobs=args.n_jobs)(
        delayed(worker_power)(i, thetas, HORIZONS_FIRST_PASS, max(HORIZONS))
        for i in range(N_STREAMS))
    for index, out, degenerate, logs in results:
        degenerate_total += degenerate
        for level, message in logs:
            getattr(logger, level.lower())(message)
        for hi, n in enumerate(HORIZONS_FIRST_PASS):
            pvalues[n][index, :] = out[:, hi]
    elapsed_pass1 = time.time() - t_pass1
    logger.info(f"Pass 1 elapsed {elapsed_pass1:.1f}s on n_jobs = {args.n_jobs}. The measured cost "
                f"of the largest horizon is reported rather than used to trim the design.")

    t_pass2 = time.time()
    logger.info(f"Pass 2 of the grid: horizons {HORIZONS_SECOND_PASS}, same {N_STREAMS} stream "
                f"indices and therefore the same uniform vectors.")
    results = Parallel(n_jobs=args.n_jobs)(
        delayed(worker_power)(i, thetas, HORIZONS_SECOND_PASS, max(HORIZONS))
        for i in range(N_STREAMS))
    for index, out, degenerate, logs in results:
        degenerate_total += degenerate
        for level, message in logs:
            getattr(logger, level.lower())(message)
        for hi, n in enumerate(HORIZONS_SECOND_PASS):
            pvalues[n][index, :] = out[:, hi]
    elapsed_pass2 = time.time() - t_pass2
    logger.info(f"Pass 2 elapsed {elapsed_pass2:.1f}s. Grid total "
                f"{elapsed_pass1 + elapsed_pass2:.1f}s over "
                f"{N_STREAMS * n_theta * len(HORIZONS)} Ljung-Box readings.")

    # The degenerate branch of `lb_pvalue` returns p = 1.0, which AUDIT_R06.md
    # section 2.3 names as biased towards "white". It is counted and logged at
    # zero as well as above it, because an absent counter and a zero counter do
    # not look different in a log.
    logger.info(f"Degenerate-stream branch of `lb_pvalue` (denom == 0 -> p = 1.0, biased towards "
                f"white per AUDIT_R06.md section 2.3): {degenerate_total} occurrences over "
                f"{N_STREAMS * n_theta * len(HORIZONS)} readings.")
    if degenerate_total:
        logger.error("A degenerate stream entered the power grid. The fallback counts as a "
                     "non-rejection and would understate the power; the run stops.")
        sys.exit(1)

    rejections = {n: (pvalues[n] < NOMINAL_LEVEL).astype(np.int64) for n in HORIZONS}
    rates = {n: rejections[n].mean(axis=0) for n in HORIZONS}

    # =====================================================================
    # C1 -- SIZE AT theta = 0, FOUR HORIZONS
    # =====================================================================
    null_index = thetas.index(0.0)
    m_tests = len(HORIZONS)
    family_probability = 1.0 - (1.0 - NOMINAL_LEVEL) ** m_tests
    logger.info(f"C1 multiplicity, computed and logged BEFORE any interpretation per preamble "
                f"S4bis: {m_tests} simultaneous 95% statements reject at least once with "
                f"probability 1 - {1 - NOMINAL_LEVEL}^{m_tests} = {family_probability:.4f}, above "
                f"the 5% threshold. The binary gate is therefore replaced by a Kolmogorov-Smirnov "
                f"calibration test of the {N_STREAMS} p-values against Uniform(0,1) at each "
                f"horizon, and the four rates are reported with their Wilson intervals as "
                f"description.")
    c1_rows = []
    null_pvalues = np.column_stack([pvalues[n][:, null_index] for n in HORIZONS])
    for hi, n in enumerate(HORIZONS):
        k = int(rejections[n][:, null_index].sum())
        rate = k / N_STREAMS
        low, high = wilson_bounds(k, N_STREAMS)
        ks_stat = ks_uniform(null_pvalues[:, hi])
        ks_p = float(stats.kstest(null_pvalues[:, hi], 'uniform').pvalue)
        c1_rows.append((n, k, rate, low, high, ks_stat, ks_p, low <= NOMINAL_LEVEL <= high))
        logger.info(f"C1 at n = {n}: rejection rate {rate:.4f} ({k}/{N_STREAMS}), Wilson "
                    f"[{low:.4f}, {high:.4f}], covers {NOMINAL_LEVEL}: "
                    f"{low <= NOMINAL_LEVEL <= high}. KS distance to Uniform(0,1) {ks_stat:.4f}, "
                    f"p = {ks_p:.4f}.")
    max_ks = max(row[5] for row in c1_rows)
    ks_draws = bootstrap_max_ks(null_pvalues, BOOTSTRAP_REPLICATES,
                                rng_for("R18", "bootstrap", "c1_max_ks"))
    max_ks_p = float((ks_draws >= max_ks).mean())
    logger.info(f"C1 across horizons: max KS distance {max_ks:.4f}, bootstrap p = {max_ks_p:.4f} "
                f"over {BOOTSTRAP_REPLICATES} resamples of WHOLE STREAM INDICES. The four horizons "
                f"are nested prefixes of the same {N_STREAMS} streams, so their KS statistics are "
                f"dependent and a pooled KS over {N_STREAMS * m_tests} p-values would be invalid; "
                f"resampling stream indices carries the dependence. A1 of the plan is answered: "
                f"four rates and four KS p-values, one per horizon, none dropped.")
    if max_ks_p < NOMINAL_LEVEL:
        logger.warning(f"C1 FINDING: the max-KS calibration statistic sits at p = {max_ks_p:.4f} "
                       f"under its own bootstrap null. Characterised and reported; no draw is "
                       f"touched (preamble S4.7). The four per-horizon KS p-values and the four "
                       f"rates above locate it.")

    # =====================================================================
    # C2 -- MONOTONICITY, IN theta AT FIXED n AND IN n AT FIXED theta
    # =====================================================================
    inversions_theta = []
    for n in HORIZONS:
        for j in range(1, n_theta):
            if rates[n][j] < rates[n][j - 1]:
                d = rejections[n][:, j] - rejections[n][:, j - 1]
                mean_d = float(d.mean())
                se_d = float(d.std(ddof=1) / math.sqrt(N_STREAMS))
                z = abs(mean_d / se_d) if se_d > 0 else float('inf')
                inversions_theta.append((n, thetas[j - 1], thetas[j], mean_d, se_d, z))
    inversions_horizon = []
    for j in range(n_theta):
        for hi in range(1, len(HORIZONS)):
            n_lo, n_hi = HORIZONS[hi - 1], HORIZONS[hi]
            if rates[n_hi][j] < rates[n_lo][j]:
                d = rejections[n_hi][:, j] - rejections[n_lo][:, j]
                mean_d = float(d.mean())
                se_d = float(d.std(ddof=1) / math.sqrt(N_STREAMS))
                z = abs(mean_d / se_d) if se_d > 0 else float('inf')
                inversions_horizon.append((thetas[j], n_lo, n_hi, mean_d, se_d, z))
    for label, found, fmt in (("in theta at fixed n", inversions_theta,
                               lambda r: f"n = {r[0]}, theta {r[1]:.6f} -> {r[2]:.6f}: "
                                         f"{r[3]:+.4f} +/- {r[4]:.4f} ({r[5]:.1f} SE)"),
                              ("in n at fixed theta", inversions_horizon,
                               lambda r: f"theta = {r[0]:.6f}, n {r[1]} -> {r[2]}: "
                                         f"{r[3]:+.4f} +/- {r[4]:.4f} ({r[5]:.1f} SE)")):
        above = [r for r in found if r[5] > C2_INVERSION_SE]
        worst = max((r[5] for r in found), default=0.0)
        logger.info(f"C2, largest inversion {label} measured in paired standard errors: "
                    f"{worst:.2f}, against the margin of {C2_INVERSION_SE}. Reported whether or "
                    f"not it reaches the margin, so that an absent inversion and a small one stay "
                    f"distinguishable in the log.")
        if above:
            logger.warning(f"C2 FINDING, monotonicity {label}: {len(above)} inversions exceed "
                           f"{C2_INVERSION_SE} standard errors of their PAIRED difference: "
                           + "; ".join(fmt(r) for r in above)
                           + ". Characterised against its own paired standard error and reported; "
                             "no draw, seed or parameter is touched (preamble S4.7).")
        logger.info(f"C2, monotonicity {label}: {len(found)} local inversions on "
                    f"{n_theta * len(HORIZONS)} readings, of which {len(above)} exceed "
                    f"{C2_INVERSION_SE} paired standard errors. Inversions below that margin are "
                    f"the sampling noise of a paired proportion and are listed in the CSV rather "
                    f"than in a gate.")

    # =====================================================================
    # C3 -- EMPIRICAL AGAINST ANALYTIC
    # =====================================================================
    analytic = {n: np.array([power_analytic(t, n, quantile) for t in thetas]) for n in HORIZONS}
    ncps = {n: np.array([ncp_analytic(t, n) for t in thetas]) for n in HORIZONS}
    deviations = {n: rates[n] - analytic[n] for n in HORIZONS}
    domain = {n: analytic[n] < C3_POWER_DOMAIN for n in HORIZONS}
    max_dev, max_dev_where = 0.0, ""
    for n in HORIZONS:
        if not domain[n].any():
            continue
        idx = int(np.argmax(np.abs(deviations[n][domain[n]])))
        sub_thetas = np.array(thetas)[domain[n]]
        value = float(np.abs(deviations[n][domain[n]])[idx])
        if value > max_dev:
            max_dev, max_dev_where = value, f"n = {n}, theta = {sub_thetas[idx]:.6f}"
    max_dev_all = max(float(np.max(np.abs(deviations[n]))) for n in HORIZONS)
    # The sign pattern of the deviation is characterised as well as its size. A
    # curve that sits on one side of its prediction over most of the domain is a
    # different statement from one that scatters around it, and preamble S3's
    # asymmetry rule asks agreement to be examined more severely than
    # disagreement. Descriptive: the sign test is reported, never gated, since the
    # deviations are paired across amplitudes by the C4 design and the test's
    # independence assumption does not hold.
    signs_positive = sum(int(d > 0) for n in HORIZONS for d in deviations[n][domain[n]])
    signs_total = sum(int(domain[n].sum()) for n in HORIZONS)
    sign_p = float(stats.binomtest(signs_positive, signs_total, 0.5).pvalue)
    logger.info(f"C3 sign pattern, descriptive and NOT a gate: the empirical rate exceeds the "
                f"analytic prediction at {signs_positive} of {signs_total} amplitudes inside the "
                f"domain, sign-test p = {sign_p:.3e} under independence, which the C4 pairing "
                f"violates so the p-value understates. The local chi-square limit is an "
                f"approximation from below at these horizons on a binary stream; the direction is "
                f"reported and no term is added to the prediction to absorb it.")
    logger.info(f"C3: maximum |empirical - analytic| is {max_dev:.4f} on the domain "
                f"power_analytic < {C3_POWER_DOMAIN} ({max_dev_where}), against a tolerance of "
                f"{C3_TOLERANCE:.4f} = 3 * 0.5/sqrt({N_STREAMS}), i.e. three standard errors of a "
                f"proportion at its worst variance. Over the WHOLE grid, including the saturated "
                f"region where the local chi-square limit is not justified and no tolerance is "
                f"applied, the maximum is {max_dev_all:.4f}.")
    if max_dev > C3_TOLERANCE:
        logger.error("C3 failure: the empirical power departs from the non-central chi-square "
                     "prediction by more than three standard errors of a proportion, inside the "
                     "domain where the local limit is justified. Either the generator or the test "
                     "implementation is defective; the run stops rather than interpret a curve "
                     "whose two derivations disagree.")
        sys.exit(1)

    # =====================================================================
    # C4 -- COMMON RANDOM NUMBERS, PRICED BEFORE ANY POOLED INTERVAL
    # =====================================================================
    deff = kish_design_effect(rejections[HORIZON_HEADLINE])
    pooled_rate = float(rejections[HORIZON_HEADLINE].mean())
    n_readings = rejections[HORIZON_HEADLINE].size
    se_srs = math.sqrt(pooled_rate * (1.0 - pooled_rate) / n_readings)
    se_cluster = float(np.std(rejections[HORIZON_HEADLINE].mean(axis=1), ddof=1)
                       / math.sqrt(N_STREAMS))
    # An amplitude at which every stream rejects has a degenerate indicator and no
    # correlation with anything; those columns are excluded by their variance
    # rather than divided by zero and filtered afterwards.
    varying = rejections[HORIZON_HEADLINE][:, rejections[HORIZON_HEADLINE].std(axis=0) > 0.0]
    corr = np.corrcoef(varying, rowvar=False)
    off = corr[~np.eye(varying.shape[1], dtype=bool)]
    logger.info(f"C4 design effect at n = {HORIZON_HEADLINE}, measured BEFORE any interval pooled "
                f"over the grid: Kish {deff:.3f} on {n_readings} readings, so an effective sample "
                f"size of {n_readings / deff:.0f}. Cluster standard error {se_cluster:.5f} against "
                f"{se_srs:.5f} for a simple random sample, ratio {se_cluster / se_srs:.3f}. Mean "
                f"correlation of the rejection indicator between two of the {varying.shape[1]} "
                f"amplitudes whose indicator varies {float(off.mean()):.3f}, max "
                f"{float(off.max()):.3f}. NO INTERVAL POOLED OVER THE GRID IS PUBLISHED; the "
                f"per-point Wilson intervals remain valid, each resting on {N_STREAMS} independent "
                f"streams.")

    # =====================================================================
    # THE DELIVERABLE: theta_80 AND rho_80, BY GRID AND BY ANALYTIC ROOT
    # =====================================================================
    amplitude_rows = []
    theta80 = {}
    for n in HORIZONS:
        t_grid = interpolate_threshold(thetas, rates[n])
        t_ana = theta_80_analytic(n, quantile)
        # The interpolator applied to the ANALYTIC curve on the same grid. This
        # separates the two error sources of `theta_80_grid`: the bias of a
        # log-linear interpolation on a 16-per-decade grid, which this isolates
        # exactly and which carries no Monte-Carlo term, and the sampling error
        # of the empirical curve, which the cluster bootstrap prices. The grid
        # resolution was chosen on the premise that the first is an order of
        # magnitude below the second; the premise is verified here rather than
        # assumed.
        t_interp_bias = interpolate_threshold(thetas, analytic[n])
        draws = np.empty(BOOTSTRAP_REPLICATES, dtype=float)
        rng_boot = rng_for("R18", "bootstrap", "theta80", n)
        matrix = rejections[n]
        for b in range(BOOTSTRAP_REPLICATES):
            idx = rng_boot.integers(0, N_STREAMS, size=N_STREAMS)
            draws[b] = interpolate_threshold(thetas, matrix[idx].mean(axis=0))
        finite = draws[np.isfinite(draws)]
        ci_low = float(np.percentile(finite, 2.5)) if finite.size else float('nan')
        ci_high = float(np.percentile(finite, 97.5)) if finite.size else float('nan')
        theta80[n] = (t_grid, t_ana, ci_low, ci_high)
        amplitude_rows.append({
            'n_steps': n, 'n_streams': N_STREAMS, 'lags': LB_LAGS,
            'theta_80_grid': t_grid, 'theta_80_analytic': t_ana,
            'rho_80_grid': 2.0 * t_grid, 'rho_80_analytic': 2.0 * t_ana,
            'ci_low': ci_low, 'ci_high': ci_high,
            'rho_ci_low': 2.0 * ci_low, 'rho_ci_high': 2.0 * ci_high,
            'ncp_at_theta_80_analytic': ncp_analytic(t_ana, n),
            'theta_80_grid_on_analytic': t_interp_bias,
            'interpolation_bias': t_interp_bias / t_ana - 1.0,
            'ci_covers_analytic': bool(ci_low <= t_ana <= ci_high),
            'bootstrap_replicates': BOOTSTRAP_REPLICATES,
            'bootstrap_non_finite': int(BOOTSTRAP_REPLICATES - finite.size),
        })
        logger.info(f"Detectable amplitude at n = {n}: theta_80 = {t_grid:.6f} by grid "
                    f"interpolation and {t_ana:.6f} by brentq on the analytic expression, a "
                    f"relative gap of {t_grid / t_ana - 1:+.4%}; rho_80 = 2*theta_80 = "
                    f"{2 * t_grid:.6f} (analytic {2 * t_ana:.6f}). Cluster-bootstrap 95% interval "
                    f"on theta_80 [{ci_low:.6f}, {ci_high:.6f}], resampling whole stream indices so "
                    f"that the C4 pairing across the grid is preserved; it covers the analytic "
                    f"root: {ci_low <= t_ana <= ci_high}. Of that gap, "
                    f"{t_interp_bias / t_ana - 1:+.4%} is the bias of the interpolator itself, "
                    f"measured by running it on the analytic curve over the same grid, and the "
                    f"remainder is Monte-Carlo error.")
    worst_bias = max(abs(row['interpolation_bias']) for row in amplitude_rows)
    not_covering = [row['n_steps'] for row in amplitude_rows if not row['ci_covers_analytic']]
    logger.info(f"Interpolation bias of the amplitude grid, isolated from any Monte-Carlo term by "
                f"running the interpolator on the analytic curve: at most {worst_bias:.4%} over the "
                f"four horizons, against a bootstrap half-width on theta_80 of "
                f"{max((row['ci_high'] - row['ci_low']) / 2 / row['theta_80_analytic'] for row in amplitude_rows):.4%} "
                f"in relative terms. The grid resolution rests on that ordering and it holds.")
    if not_covering:
        logger.warning(
            f"FINDING: the cluster-bootstrap interval on theta_80 does not cover the analytic root "
            f"at n = {not_covering}. Four intervals at 95% miss at least once with probability "
            f"{1 - 0.95 ** len(HORIZONS):.4f} under their own null, so the event is unremarkable in "
            f"itself; it is recorded because the point estimate and the analytic root are then two "
            f"different statements about the same quantity, and docs/sections/R18.md reports both. "
            f"No draw, grid or tolerance is touched (preamble S4.7). The macro file carries the "
            f"grid estimate, the analytic root and the bootstrap interval as three separate "
            f"values, so that a reader is never handed one in place of another.")
    ncp_at_80 = [row['ncp_at_theta_80_analytic'] for row in amplitude_rows]
    logger.info(f"The non-centrality at 80% power is a constant of the test and not of the horizon: "
                f"{['%.4f' % v for v in ncp_at_80]}, which is why theta_80 follows an n^{{-1/2}} "
                f"law. Ratios of consecutive analytic theta_80 against the predicted 0.5: "
                + ", ".join(f"{theta80[HORIZONS[i]][1] / theta80[HORIZONS[i - 1]][1]:.4f}"
                            for i in range(1, len(HORIZONS))) + ".")

    # =====================================================================
    # APPLICATION ARMS -- WHAT THE PUBLISHED NON-REJECTIONS EXCLUDE
    # =====================================================================
    floor_r11 = compute_gamma_exact(ALPHA_FIXED, 0.0)
    logger.info(f"Attainable penalty floor at alpha = {ALPHA_FIXED}: "
                f"1 + 2*alpha/(1-alpha) = {floor_r11!r}. Arm (b) inherits R11's 20-point target "
                f"grid, whose first target 1.0 lies below it; Gamma_target, Gamma_realised and "
                f"attainable are carried as three distinct columns and the finding itself is "
                f"docs/DEVIATIONS.md `R11-gamma-grid-floor`, cited rather than restated.")

    applied_rows = []
    arm_cache = {}
    for arm, grid in (("classifier_error", GAMMA_GRID_CLASSIFIER), ("raw_sign", GAMMA_GRID_SIGN)):
        t_arm = time.time()
        for gamma in grid:
            if arm == "classifier_error":
                # R06's convention on its own grid: the Gamma = 1 point is
                # alpha = beta = 0, a genuinely i.i.d. stream rather than an
                # ARCH(1) process at the attainable floor. It is R06's grid, so
                # it is R06's convention, and the difference with arm (b) is
                # what A3 asks to be visible in the columns.
                beta = 0.0 if gamma == 1.0 else solve_beta_for_gamma_r06(ALPHA_FIXED, gamma)
                alpha = 0.0 if gamma == 1.0 else ALPHA_FIXED
                realised = gamma_exact(alpha, beta)
                attainable = True
                out = Parallel(n_jobs=args.n_jobs)(
                    delayed(worker_sign_classifier)(gamma, i, alpha, beta, N_STEPS)
                    for i in range(N_STREAMS_APPLIED))
            else:
                alpha = ALPHA_FIXED
                beta = solve_beta_for_gamma_r11(ALPHA_FIXED, gamma)
                omega = TARGET_VAR * (1.0 - alpha - beta)
                realised = compute_gamma_exact(alpha, beta)
                attainable = bool(gamma >= floor_r11)
                out = Parallel(n_jobs=args.n_jobs)(
                    delayed(worker_sign_garch)(gamma, i, alpha, beta, omega, N_STEPS)
                    for i in range(N_STREAMS_APPLIED))
            p_arr = np.array([row[0] for row in out])
            deg = int(sum(row[1] for row in out))
            mean_rate = float(np.mean([row[2] for row in out]))
            sums = np.array([row[3] for row in out])
            cross = np.array([row[4] for row in out])
            first = np.array([row[5] for row in out])
            last = np.array([row[6] for row in out])
            for row in out:
                for level, message in row[7]:
                    getattr(logger, level.lower())(message)
            if deg:
                logger.error(f"Degenerate Ljung-Box branch fired {deg} times on arm {arm} at "
                             f"Gamma = {gamma}. The fallback counts as a non-rejection; the run "
                             f"stops rather than report a rate it biased.")
                sys.exit(1)
            rho = pooled_lag1(sums, cross, first, last, N_STEPS)
            draws = bootstrap_pooled_lag1(sums, cross, first, last, N_STEPS,
                                          BOOTSTRAP_REPLICATES,
                                          rng_for("R18", "bootstrap", arm, gamma))
            rho_low = float(np.percentile(draws, 2.5))
            rho_high = float(np.percentile(draws, 97.5))
            k_reject = int((p_arr < NOMINAL_LEVEL).sum())
            lb_low, lb_high = wilson_bounds(k_reject, N_STREAMS_APPLIED)
            power_low, power_high = power_interval_from_rho(rho_low, rho_high, N_STEPS, quantile)
            rho80_here = 2.0 * theta80[N_STEPS][1]
            applied_rows.append({
                'arm': arm,
                'stream': ('binary classifier error e_t^bin (HoeffdingTree)'
                           if arm == "classifier_error" else 'raw sign 1{eps_t > 0}'),
                'source_grid': 'R06' if arm == "classifier_error" else 'R11',
                'gamma_target': float(gamma),
                'gamma_realised': float(realised),
                'attainable': bool(attainable),
                'alpha': float(alpha), 'beta': float(beta),
                'n_steps': N_STEPS, 'n_streams': N_STREAMS_APPLIED, 'lags': LB_LAGS,
                'rho_lag1': rho, 'rho_ci_low': rho_low, 'rho_ci_high': rho_high,
                'abs_rho_lag1': abs(rho),
                'rho_80_analytic': rho80_here,
                'ratio_rho_to_rho_80': abs(rho) / rho80_here,
                'lb_reject_rate': k_reject / N_STREAMS_APPLIED,
                'lb_wilson_low': lb_low, 'lb_wilson_high': lb_high,
                'lb_pvalue_median': float(np.median(p_arr)),
                'power_at_measured_rho': power_analytic(abs(rho) / 2.0, N_STEPS, quantile),
                'power_at_rho_ci_low': power_low,
                'power_at_rho_ci_high': power_high,
                'mean_rate': mean_rate,
                'degenerate': deg,
                'classifier_version': (river.__version__ if arm == "classifier_error"
                                       else 'not-used'),
            })
            logger.info(f"Arm {arm}, Gamma target {gamma} (realised {realised:.6f}, attainable "
                        f"{attainable}): pooled lag-1 autocorrelation {rho:+.6f} "
                        f"[{rho_low:+.6f}, {rho_high:+.6f}], |rho|/rho_80 = "
                        f"{abs(rho) / rho80_here:.4f}, Ljung-Box rejection "
                        f"{k_reject}/{N_STREAMS_APPLIED} = {k_reject / N_STREAMS_APPLIED:.3f} "
                        f"[{lb_low:.3f}, {lb_high:.3f}], analytic power of the instrument at that "
                        f"autocorrelation {power_analytic(abs(rho) / 2.0, N_STEPS, quantile):.4f} "
                        f"[{power_low:.4f}, {power_high:.4f}].")
        arm_cache[arm] = time.time() - t_arm
        logger.info(f"Arm {arm} elapsed {arm_cache[arm]:.1f}s over "
                    f"{len(grid) * N_STREAMS_APPLIED} streams of {N_STEPS} steps.")

    df_applied = pd.DataFrame(applied_rows)
    classifier_view = df_applied[df_applied['arm'] == "classifier_error"]
    sign_view = df_applied[df_applied['arm'] == "raw_sign"]
    # The MAXIMUM over each arm's penalties, not a pooling of them: the sentence
    # A2 asks the section to be able to state is a bound, so it must be read at
    # the largest autocorrelation the arm exhibits and not at an average that
    # would sit below it. Every per-penalty value is in the CSV.
    rho_classifier_max = float(classifier_view['abs_rho_lag1'].max())
    power_classifier_max = float(classifier_view['power_at_measured_rho'].max())
    rho_sign_max = float(sign_view['abs_rho_lag1'].max())
    power_sign_max = float(sign_view['power_at_measured_rho'].max())
    logger.info(f"Application summary at n = {N_STEPS}: the largest |lag-1 autocorrelation| over "
                f"the 13 classifier-arm penalties is {rho_classifier_max:.6f}, which is "
                f"{rho_classifier_max / (2 * theta80[N_STEPS][1]):.4f} of rho_80 = "
                f"{2 * theta80[N_STEPS][1]:.6f} and at which the instrument has analytic power "
                f"{power_classifier_max:.4f}. Over the 20 sign-arm penalties the largest is "
                f"{rho_sign_max:.6f}, power {power_sign_max:.4f}. A non-rejection at those sites "
                f"therefore excludes an autocorrelation above rho_80 with probability "
                f"{POWER_TARGET}, and excludes nothing at the amplitudes measured here.")

    # =====================================================================
    # PERSISTENCE
    # =====================================================================
    def power_frame(horizons):
        rows = []
        for n in horizons:
            for j, t in enumerate(thetas):
                k = int(rejections[n][:, j].sum())
                low, high = wilson_bounds(k, N_STREAMS)
                rows.append({
                    'theta': t, 'rho_lag1': 2.0 * t, 'n_steps': n, 'n_streams': N_STREAMS,
                    'lags': LB_LAGS, 'reject_rate': rates[n][j],
                    'wilson_low': low, 'wilson_high': high,
                    'ncp_analytic': ncps[n][j], 'power_analytic': analytic[n][j],
                    'deviation_emp_minus_analytic': deviations[n][j],
                })
        return pd.DataFrame(rows)

    df_theta = power_frame([HORIZON_HEADLINE])
    df_horizon = power_frame(HORIZONS)
    df_amplitude = pd.DataFrame(amplitude_rows)
    df_c1 = pd.DataFrame([{'n_steps': n, 'n_streams': N_STREAMS, 'lags': LB_LAGS,
                           'rejections': k, 'reject_rate': rate, 'wilson_low': low,
                           'wilson_high': high, 'ks_statistic': ks_stat, 'ks_pvalue': ks_p,
                           'covers_nominal': covers, 'max_ks_statistic': max_ks,
                           'max_ks_bootstrap_pvalue': max_ks_p}
                          for n, k, rate, low, high, ks_stat, ks_p, covers in c1_rows])

    outputs = {
        "R18_power_vs_theta.csv": df_theta,
        "R18_power_vs_horizon.csv": df_horizon,
        "R18_detectable_amplitude.csv": df_amplitude,
        "R18_applied_to_sign_streams.csv": df_applied,
        "R18_size_at_null.csv": df_c1,
    }
    for name, frame in outputs.items():
        save_fair_csv(frame, DATA_DIR / name)
    cardinalities = {
        "R18_power_vs_theta": (len(df_theta), n_theta),
        "R18_power_vs_horizon": (len(df_horizon), n_theta * len(HORIZONS)),
        "R18_detectable_amplitude": (len(df_amplitude), len(HORIZONS)),
        "R18_applied_to_sign_streams": (len(df_applied),
                                        len(GAMMA_GRID_CLASSIFIER) + len(GAMMA_GRID_SIGN)),
        "R18_size_at_null": (len(df_c1), len(HORIZONS)),
    }
    for name, (observed, required) in cardinalities.items():
        if observed != required:
            logger.error(f"Cardinality error on {name}: {observed} rows, expected {required}")
            sys.exit(1)
    logger.info("Cardinality check: " + ", ".join(f"{k} = {v[0]}" for k, v in cardinalities.items()))

    # =====================================================================
    # FIGURE figA05 -- PLOTTED FROM RAM, NEVER FROM A RELOADED CSV
    # =====================================================================
    # figA04 is already taken: R11 emits figA04_adwin_blind_zone.png. The R18
    # prompt's justification for figA04 enumerates R02b, R02c and R04b and misses
    # R11, which has no docs/sections/R11.md-adjacent audit under that name; the
    # stale premise is recorded in AUDIT_R18.md section 7.
    plt.rcParams.update({
        'figure.dpi': 300, 'font.family': 'sans-serif', 'font.size': 10,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.facecolor': 'white', 'figure.facecolor': 'white', 'mathtext.fontset': 'stix',
    })
    fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.6))
    positive = [t for t in thetas if t > 0]
    pos_mask = np.array([t > 0 for t in thetas])
    fine = np.exp(np.linspace(math.log(min(positive)), math.log(max(positive)), 400))

    ax = axes[0]
    n = HORIZON_HEADLINE
    ax.plot(positive, rates[n][pos_mask], 'o-', color=COLORS['empirical'], ms=3.5, lw=1.4,
            label=f'Empirical, {N_STREAMS} streams')
    ax.fill_between(positive,
                    [wilson_bounds(int(rejections[n][:, j].sum()), N_STREAMS)[0]
                     for j in range(n_theta) if thetas[j] > 0],
                    [wilson_bounds(int(rejections[n][:, j].sum()), N_STREAMS)[1]
                     for j in range(n_theta) if thetas[j] > 0],
                    color=COLORS['band'], alpha=0.18, lw=0, label='95% Wilson')
    ax.plot(fine, [power_analytic(t, n, quantile) for t in fine], '--', color=COLORS['analytic'],
            lw=1.6, label=r'Analytic $\chi^2_{\mathrm{nc}}(20,\ \mathrm{ncp})$')
    ax.axhline(POWER_TARGET, color=COLORS['reference'], lw=1.0, ls=':')
    ax.axhline(NOMINAL_LEVEL, color=COLORS['reference'], lw=1.0, ls='-.')
    ax.axvline(theta80[n][0], color=COLORS['empirical'], lw=1.2, ls='-')
    ax.annotate(rf'$\theta_{{80}} = {theta80[n][0]:.4f}$' '\n' rf'$\rho_{{80}} = {2 * theta80[n][0]:.4f}$',
                xy=(theta80[n][0], POWER_TARGET), xytext=(0.055, 0.45),
                textcoords='axes fraction', fontsize=9, color=COLORS['empirical'])
    ax.set_xscale('log')
    ax.set_xlabel(r'$\theta$  (lag-1 autocorrelation $\rho = 2\theta$)')
    ax.set_ylabel('Rejection rate of the lag-20 Ljung--Box test')
    ax.set_title(f'(A) Power at n = {n}, the Figure 6 horizon', fontweight='bold', loc='left')
    ax.set_ylim(-0.03, 1.03)
    ax.legend(fontsize=8, loc='center right', framealpha=0.9)

    ax = axes[1]
    for n in HORIZONS:
        ax.plot(positive, rates[n][pos_mask], 'o-', ms=3.0, lw=1.3, color=HORIZON_COLORS[n],
                label=f'n = {n:,}')
        ax.plot(fine, [power_analytic(t, n, quantile) for t in fine], '--', lw=1.0,
                color=HORIZON_COLORS[n], alpha=0.65)
    ax.axhline(POWER_TARGET, color=COLORS['reference'], lw=1.0, ls=':')
    ax.set_xscale('log')
    ax.set_xlabel(r'$\theta$')
    ax.set_ylabel('Rejection rate')
    ax.set_title('(B) The four horizons of the R02c sweep', fontweight='bold', loc='left')
    ax.set_ylim(-0.03, 1.03)
    ax.legend(fontsize=8, loc='center right', framealpha=0.9, title='solid: empirical\ndashed: analytic',
              title_fontsize=8)

    ax = axes[2]
    ns = np.array(HORIZONS, dtype=float)
    rho80_grid = np.array([2.0 * theta80[n][0] for n in HORIZONS])
    rho80_ana = np.array([2.0 * theta80[n][1] for n in HORIZONS])
    rho80_lo = np.array([2.0 * theta80[n][2] for n in HORIZONS])
    rho80_hi = np.array([2.0 * theta80[n][3] for n in HORIZONS])
    ax.plot(ns, rho80_ana, '--', color=COLORS['analytic'], lw=1.6,
            label=r'Analytic $\rho_{80}$ ($n^{-1/2}$)')
    ax.errorbar(ns, rho80_grid, yerr=[rho80_grid - rho80_lo, rho80_hi - rho80_grid], fmt='o',
                color=COLORS['empirical'], ms=5, capsize=3, lw=1.2,
                label=r'Measured $\rho_{80}$, cluster bootstrap')
    ax.scatter(np.full(len(classifier_view), N_STEPS) * 0.86, classifier_view['abs_rho_lag1'],
               marker='s', s=22, color=COLORS['classifier'], zorder=5,
               label=r'$|\rho_1|$, classifier error stream (13 $\Gamma$)')
    ax.scatter(np.full(len(sign_view), N_STEPS) * 1.16, sign_view['abs_rho_lag1'],
               marker='^', s=22, color=COLORS['sign'], zorder=5,
               label=r'$|\rho_1|$, raw sign stream (20 $\Gamma$)')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Stream length n')
    ax.set_ylabel(r'lag-1 autocorrelation ($|\rho_1|$ for the two arms)')
    ax.set_title('(C) Detectable amplitude against the measured streams', fontweight='bold',
                 loc='left')
    # Both arms are measured at n = 8000 -- the horizon prompt section 1 imposes
    # -- and their markers are displaced horizontally so that 33 points at one
    # abscissa stay legible. The displacement is cosmetic and is stated on the
    # panel, since a log abscissa would otherwise read as two different horizons.
    ax.text(0.98, 0.97, 'both arms measured at n = 8,000\nmarkers offset for legibility',
            transform=ax.transAxes, fontsize=7, color=COLORS['reference'],
            ha='right', va='top')
    ax.legend(fontsize=7.5, loc='lower left', framealpha=0.9)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _p: f'{int(v):,}'))

    plt.tight_layout()
    fig_path = FIGURES_DIR / "figA05_ljungbox_power.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()

    # =====================================================================
    # LATEX MACROS
    # =====================================================================
    # Cardinal, not the prompt's ordinal. Preamble S6 fixes the naming as
    # \R<Ordinal><ClaimInCamelCase> with "l'ordinal en toutes lettres anglaises
    # (One, Two, ..., Seventeen)", and the preamble prevails over the prompt by
    # its own precedence clause. The repository realises cardinals throughout --
    # ROne ... RSix, RTwoC, and REleven, which R11 emitted after correcting the
    # identical defect in its own prompt (AUDIT_R11.md section 7). Emitting
    # REighteenth would leave one stream out of eighteen with a different
    # namespace in a file destined for \input.
    headline = HORIZON_HEADLINE
    rho_one_tenth_index = thetas.index(0.05)
    macros = ["% Auto-generated by exp_R18_ljungbox_power.py -- do not edit."]
    macros.append(f"\\newcommand{{\\REighteenThetaEighty}}{{{theta80[headline][0]:.4f}}}")
    macros.append(f"\\newcommand{{\\REighteenRhoEighty}}{{{2 * theta80[headline][0]:.4f}}}")
    macros.append(f"\\newcommand{{\\REighteenThetaEightyAnalytic}}"
                  f"{{{theta80[headline][1]:.4f}}}")
    macros.append(f"\\newcommand{{\\REighteenRhoEightyAnalytic}}"
                  f"{{{2 * theta80[headline][1]:.4f}}}")
    macros.append(f"\\newcommand{{\\REighteenRhoEightyCiLow}}{{{2 * theta80[headline][2]:.4f}}}")
    macros.append(f"\\newcommand{{\\REighteenRhoEightyCiHigh}}{{{2 * theta80[headline][3]:.4f}}}")
    macros.append(f"\\newcommand{{\\REighteenPowerAtRhoOneTenth}}"
                  f"{{{rates[headline][rho_one_tenth_index]:.3f}}}")
    macros.append(f"\\newcommand{{\\REighteenPowerAtRhoOneTenthShortHorizon}}"
                  f"{{{rates[2000][rho_one_tenth_index]:.3f}}}")
    size_index = null_index
    macros.append(f"\\newcommand{{\\REighteenSizeAtNull}}"
                  f"{{{rates[headline][size_index] * 100:.1f}\\%}}")
    macros.append(f"\\newcommand{{\\REighteenSizeAtNullKsPvalue}}"
                  f"{{{[row[6] for row in c1_rows][HORIZONS.index(headline)]:.3f}}}")
    macros.append(f"\\newcommand{{\\REighteenMaxDeviationAnalytic}}{{{max_dev:.4f}}}")
    macros.append(f"\\newcommand{{\\REighteenPowerAtMeasuredRho}}{{{power_classifier_max:.3f}}}")
    macros.append(f"\\newcommand{{\\REighteenMeasuredRhoClassifier}}{{{rho_classifier_max:.4f}}}")
    macros.append(f"\\newcommand{{\\REighteenMeasuredRhoSign}}{{{rho_sign_max:.4f}}}")
    macros.append(f"\\newcommand{{\\REighteenPowerAtMeasuredRhoSign}}{{{power_sign_max:.3f}}}")
    macros.append(f"\\newcommand{{\\REighteenStreamsPerPoint}}{{{N_STREAMS}}}")
    macros.append(f"\\newcommand{{\\REighteenAmplitudeGridPoints}}{{{n_theta}}}")
    macros.append(f"\\newcommand{{\\REighteenLags}}{{{LB_LAGS}}}")
    macros.append(f"\\newcommand{{\\REighteenDesignEffect}}{{{deff:.2f}}}")
    for n in HORIZONS:
        word = {2000: "TwoThousand", 8000: "EightThousand",
                32000: "ThirtyTwoThousand", 128000: "OneTwentyEightThousand"}[n]
        macros.append(f"\\newcommand{{\\REighteenRhoEighty{word}}}{{{2 * theta80[n][0]:.4f}}}")
    tex_path = TABLES_DIR / "R18_claims.tex"
    with open(tex_path, "w") as f:
        f.write("\n".join(macros) + "\n")
    logger.info(f"Emitted {len(macros) - 1} macros to {tex_path.name}, prefix \\REighteen per "
                f"preamble S6's ordinal-in-English rule. The R18 prompt prints \\REighteenth, which "
                f"does not follow it and which no other stream of this repository uses; the defect "
                f"is recorded in AUDIT_R18.md section 7. Every value is computed from objects in "
                f"memory; no literal is hard-coded.")
    undefined = [m for m in macros[1:] if '{nan' in m]
    if undefined:
        logger.warning(f"{len(undefined)} macros carry the body `nan` because the quantity they "
                       f"name is not defined on this grid: {undefined}. Emitted as measured rather "
                       f"than suppressed.")

    # =====================================================================
    # CAMERA-READY TRIGGER, DECIDED AT RUN TIME
    # =====================================================================
    rho80_headline = 2.0 * theta80[headline][1]
    trigger = rho80_headline > rho_classifier_max and rho80_headline > rho_sign_max
    logger.info(f"Camera-ready trigger condition of prompt section 8, evaluated on the measured "
                f"arms rather than assumed: rho_80 = {rho80_headline:.6f} against the largest "
                f"measured |rho_1| of {max(rho_classifier_max, rho_sign_max):.6f}. Condition holds: "
                f"{trigger}. A candidate is parked under docs/camera_ready_candidates/ when it "
                f"holds, with the header PARKED -- do not apply.")

    # =====================================================================
    # DIGESTS AND TIMING
    # =====================================================================
    artefacts = [(name, DATA_DIR / name) for name in outputs]
    artefacts += [(fig_path.name, fig_path), (tex_path.name, tex_path)]
    
    # Log artifact manifest with hierarchical tree structure
    artifact_paths = [path for _, path in artefacts]
    log_artifact_manifest(logger, artifact_paths, DATA_DIR.parent, BASE_DIR)
    
    for label, path in artefacts:
        logger.info(f"SHA-256 {label:<40} : {compute_sha256(path)}")

    elapsed = time.time() - t0
    total_streams = (2 * N_STREAMS + C5_STREAMS
                     + (len(GAMMA_GRID_CLASSIFIER) + len(GAMMA_GRID_SIGN)) * N_STREAMS_APPLIED)
    logger.info(f"Execution completed in {elapsed:.1f}s over {total_streams} generated streams: "
                f"{N_STREAMS} common-random-number streams read at {n_theta} amplitudes x "
                f"{len(HORIZONS)} horizons in two passes ({elapsed_pass1:.1f}s for n = "
                f"{HORIZONS_FIRST_PASS[0]} alone, {elapsed_pass2:.1f}s for the other three), "
                f"{C5_STREAMS} for C5, {len(GAMMA_GRID_CLASSIFIER) * N_STREAMS_APPLIED} classifier "
                f"streams ({arm_cache['classifier_error']:.1f}s) and "
                f"{len(GAMMA_GRID_SIGN) * N_STREAMS_APPLIED} sign streams "
                f"({arm_cache['raw_sign']:.1f}s).")


if __name__ == "__main__":
    main()
