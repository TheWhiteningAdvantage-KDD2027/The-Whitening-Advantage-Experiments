#!/usr/bin/env python3
"""
==========================================================================
R08 (a) -- THE ADVERSE DIRECTION AND THE DISCRETE NULL LAW (v87 Figure 8,
L241, L311)
==========================================================================
v87 claims the `Concept` threshold is EXACT: its null law is known without a
nuisance parameter. R08 establishes the two qualifications of that claim.

  L311  an injected centring bias moves the false-alarm rate IN BOTH
        DIRECTIONS ACCORDING TO ITS SIGN, at identical whiteness loss
                                        ->  R08_adverse_bias.csv (module A)
  L241  "exact" does not mean "every nominal level is attainable": under a
        dead band delta the statistic lives on a 2delta lattice and the
        attainable levels are discrete
                                        ->  R08_null_law_lattice.csv (module B)
  Fig. 8 caption (A) (B)                ->  module A, 10,000 trajectories per b
  Fig. 8 caption (C)                    ->  module B, 2x10^5 fair-coin streams

WHAT THIS STAGE PRODUCES. Five CSVs. Two of them carry v87 numerals
(`R08_adverse_bias.csv`, `R08_null_law_lattice.csv`); the other three certify
no published value and exist so that the controls can be recomputed by a third
party (`R08_operator_levels.csv`, `R08_lattice_exact_law.csv`,
`R08_pairing_diagnostic.csv`). The figure and the LaTeX macros are the remit of
`exp_R08_adverse_lattice_b.py`, which re-runs this campaign in memory.

SIX STRUCTURAL CHANGES AGAINST THE DELIVERED CHAIN
(`Priorite_21b_adverse_bias_and_null_law.py` ->
 `Priorite_21c_plot_adverse_lattice.py`), EACH FORCED BY THE PREAMBLE.

1. ENTROPY. The delivered `np.random.SeedSequence(424242).spawn(7 * 10000)`
   keyed a trajectory on its position in a spawn list, and the calibration ran
   on the bare integer seed `np.random.default_rng(100)` (witness l.228).
   Preamble S6 requires a 128-bit key on the ROLE AND INDEX ALONE, calibration
   included. Every Monte-Carlo value moves; that is pre-classified Class A / D2
   by the `R07/R09/R10/R13-campaign-redraw` precedents.
   THE TRAJECTORY KEY IS R07's, DELIBERATELY. Module A keys its trajectories on
   `seed_sequence_for("trajectory", i)`, which is the key
   `exp_R07_estimated_mean.py` uses. That is not an entropy collision: it is
   what makes control C6 an EXACT cross-stream identity rather than a
   fluctuation comparison, because `generate_dgp` draws `z`, `h` and `eps`
   without ever referencing `phi`. Module B keys on
   `("lattice_stream", index)`, which is R08's own namespace and is disjoint
   from R07's.
2. lambda* BY THE RULE L241 STATES, NOT BY A SAMPLE QUANTILE. The delivered
   `float(np.quantile(Ms_cal, 0.95))` on 20,000 fair-coin streams sits astride
   a lattice boundary. L241 states its own rule -- "we take the nearest
   attainable level at or below nominal" -- and `lambda_star_from_rule`
   implements it on the EXACT law. `docs/DEVIATIONS.md`
   `R07-lambda-star-estimator` already registers the estimator; R08 cites it
   and opens no duplicate entry.
3. ONE COMPARISON OPERATOR, ASSERTED BY `ast` (control C1). Every exceedance
   test routes through `exceeds`, `exceeds_units_strict` or
   `exceeds_units_weak`, and C1 parses BOTH modules of this stream to require
   that no other comparison orders a threshold name against anything.
4. NO SILENT DEGRADED PATH (S4.3). `--fast` is retained and STAMPED: it writes
   `R08_*_fast.csv` / `.png` / `.tex`, on the `*_legacy_seeds` precedent of
   R14. The delivered script reduced `N_SEEDS` from 10,000 to 200 under the
   same file names.
5. NO DISK ROUND TRIP AS A MEMORY BRIDGE (S7). `Priorite_21c` re-read its two
   CSVs with `pd.read_csv` and no `float_precision='round_trip'`, then plotted
   from disk. `_b` imports this module and re-runs `run_campaign`; every CSV
   read that survives for a structural reason is in `round_trip`.
6. THE DELIVERED CERTIFICATION BLOCK IS REPLACED. The witness `main` gates on
   four literals it produced itself (`0.0086`, `0.2076`, `0.05027`, `0.04287`)
   at `tol = 1e-9`, which preamble S7 forbids outright and which the mandated
   re-keying makes fail by construction. The C-series replaces it.

WHAT THIS STREAM DOES NOT OWN.
  - `eta_rmse_over_sigma`, the ratio "seven times the largest we measure" and
    the constant `2.5` of L311 are R07's: R07 holds the denominator of the
    ratio and registers the bound as `R07-bias-bound-not-a-bound`. R08 emits NO
    macro for any of the three and cites R07.
  - `20.8%` and the `1.1`-point penalty are cells of
    `results/R07_estimated_mean/data/R07_estmean_lb_fpr.csv`, and their
    movement is already registered as `R07-campaign-redraw`. R08 macro-ises
    them because the SITES -- L311 and the Figure 8 caption -- are R08's, and
    opens no new register entry on their movement.

NOTATION (prompt section 7)
  b                   injected over-centering bias, mu_hat_t = (phi_hat_t + b) r_{t-1}
  phi                 AR(1) momentum of the conditional mean; the naive
                      reference arm runs at phi = b
  n_ols               rolling-OLS window length, fixed at 250
  H                   monitoring horizon, 5,000 steps
  delta               CUSUM dead band; the two-sided increments live on a
                      lattice of step 2delta
  M_H                 maximum of the two-sided CUSUM statistic over the horizon
  lambda_star         the nearest attainable level at or below nominal
  is_lattice_point    lambda is an integer multiple of 2delta, decided in exact
                      rational arithmetic on the printed decimal
  bracket_role        which side of the nominal level a lattice point carries

References:
- Ljung, G. M. & Box, G. E. P. (1978). On a measure of lack of fit in time
  series models. Biometrika, 65(2), 297-303.
- Wilson, E. B. (1927). Probable inference, the law of succession, and
  statistical inference. JASA, 22(158), 209-212.
- Page, E. S. (1954). Continuous inspection schemes. Biometrika, 41, 100-115.
- McNemar, Q. (1947). Note on the sampling error of the difference between
  correlated proportions or percentages. Psychometrika, 12(2), 153-157.
- Kish, L. (1965). Survey Sampling. Wiley. (design effect)
- Kolmogorov, A. N. (1933); Smirnov, N. V. (1948). (calibration test)
==========================================================================
"""

import sys
from pathlib import Path

# Determinism bootstrap, in the order preamble S6 requires: fair_env imports only
# os and sys, so the environment block is posted before NumPy is loaded by anyone
# and before any BLAS thread limit is read. PYTHONHASHSEED cannot be set from
# here -- CPython reads it at interpreter start-up -- so it is exported by
# run_experiment_R08.sh and verified twice below.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from experiments.common.fair_env import enforce_strict_determinism, verify_hash_seed, log_environment

enforce_strict_determinism()

import os

if os.environ.get("PYTHONHASHSEED") != "42":
    sys.exit("FATAL: PYTHONHASHSEED is not 42. Execute via run_experiment_R08.sh")

import numpy as np
import pandas as pd
from experiments.common.fair_harness import (setup_logging, disable_pandas_multithreading,
                                             compute_sha256, save_fair_csv)

disable_pandas_multithreading()

import ast
import re
import time
import hashlib
import argparse
import itertools
import traceback
import concurrent.futures
from fractions import Fraction
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox

# --- PROTOCOL SPECIFICATION, IMPERATIVE, FROM v87 AND THE DELIVERED SCRIPT ---
# v87 section 1 of the R08 prompt fixes every grid below, and the delivered
# `main` (witness l.211-215) is the traceability line for each of them:
#   N_SEEDS = 200 if args.fast else 10000        -> l.211
#   N_LATTICE = 5000 if args.fast else 200000    -> l.212
#   H = 5000                                     -> l.213
#   B_GRID = [0.00, 0.02, 0.05, 0.075, 0.10, 0.15]      -> l.214
#   LAMBDA_GRID = [11.0, 11.2, 11.4, 11.6, 11.8, 12.0]  -> l.215
# and `worker_mod_A` (witness l.172-195) fixes phi = 0, n_ols = 250, the 6001
# path length and the [1000:6000] / [1001:6001] evaluation slices.
N_SEEDS = 10000
N_LATTICE = 200000
FAST_N_SEEDS = 200
FAST_N_LATTICE = 5000
B_GRID = (0.00, 0.02, 0.05, 0.075, 0.10, 0.15)
PHI_INJECTED = 0.00
N_OLS = 250
T_PATH = 6001
EVAL_START = 1001
EVAL_END = 6001
H = 5000
DELTA = 0.1
LB_LAG = 20
LB_LEVEL = 0.05

# The threshold grid of Figure 8 panel C, carried as the DECIMALS v87 prints.
# `11.2 / 0.2` is 55.99999999999999 in float64 and `56 * 0.2` is
# 11.200000000000001, so neither float route decides whether a grid point is a
# lattice point. The decision is taken in exact rational arithmetic on the
# printed decimal, which is what `lattice_units_of` does.
LAMBDA_GRID_DECIMAL = ('11.0', '11.2', '11.4', '11.6', '11.8', '12.0')
# A probe that is NOT a multiple of 2delta, used once to exhibit that
# `is_lattice_point` is a computation with two possible answers and not the
# literal `is_lattice = True` the witness writes at its line 373.
NON_LATTICE_PROBE_DECIMAL = '11.3'

# The 2delta lattice. The two CUSUM branches move by +0.4 and -0.6, i.e. by +2
# and -3 in units of 2delta = 0.2, so M_H is an integer multiple of 0.2 and the
# attainable levels are discrete. This is what L241 states.
LATTICE_UNIT = 2.0 * DELTA
LATTICE_UP = 2
LATTICE_DOWN = 3
LATTICE_STEPS_PER_UNIT = Fraction(1, 5)
NOMINAL_LEVEL = 0.05
# The bracketing region the exact survival function is tabulated over, in
# lattice units: 10.0 to 13.0 in steps of 2delta. Identical to the region
# exp_R07_estimated_mean.py scans, which is what makes control C2a a
# cell-by-cell comparison rather than an interpolation.
LATTICE_SCAN_UNITS = tuple(range(50, 66))
# Exhaustive enumeration of all 2^H paths validates the dynamic program. The
# horizons below are the UNION of what R07 (8, 10, 12) and R10 (10, 12, 14)
# validate on; control C2b asserts on the intersection and reports the union.
ENUMERATION_HORIZONS = (8, 10, 12, 14)
ENUMERATION_LAMBDA_UNITS = (4, 5, 6, 7)
ENUMERATION_Q = 0.5

# What v87 PRINTS, taken from the manuscript and never from an output of this
# repository. These are anchors of the D-classification, not targets.
V87_LAMBDA_STAR = 11.4
V87_LEVEL_ABOVE = 0.0503
V87_LEVEL_BELOW = 0.0429
V87_FPR_COLLAPSE = 0.0086
V87_FPR_INFLATE = 0.208
V87_WHITENESS_BOUND_POINTS = 3.0
V87_PENALTY_POINTS = 1.1
V87_RESIDUAL_MOMENTUM = 0.02
V87_N_TRAJECTORIES = 10000
V87_N_STREAMS = 200000

# Chunking. Fixed constants, deliberately NOT derived from the worker count: a
# chunk boundary that moved with `--n-jobs` would make the reassembly order a
# function of the machine. Every task is keyed on its role and index alone, so
# `--n-jobs 1` must give byte-identical artefacts (control C8).
CHUNK_SIZE = 50
LATTICE_CHUNK_SIZE = 2000

# --- STATISTICAL CONTROL DESIGN, FIXED BEFORE THE FIRST RUN (S4bis) ---
# C4 reads a MAXIMUM over the six b of a paired difference. A maximum has no
# binomial null (S4bis, 4th corollary), so it is read against a resampling null
# built on the only i.i.d. unit of this design -- the trajectory -- whose
# trigger probability under H0 is the level itself by construction of the null.
C4_NULL_LEVEL = 0.001
N_RESAMPLE_NULL = 10000
# The KS null of the six proportion p-values needs only a tail resolution of a
# few 1e-4 because it is REPORTED and gates nothing; 2,000 replicates place its
# 97.5% quantile on the 50th order statistic from the top.
N_RESAMPLE_KS = 2000
# The sampling envelope of the maximum whiteness gap, used for the D-class of
# v87's three-point bound under preamble S3's own rule: a printed bound is
# crossed at D3 only if the 95% interval of the regenerated value EXCLUDES it.
N_RESAMPLE_BOOT = 2000
BOOT_ALPHA = 0.05
# The ULP budget of the boundary counter, taken from the footnote of L241 --
# "floating-point accumulation leaves M_H a few ulps above its exact lattice
# value" -- and from the R08 prompt's section 2.1, which fixes the count at
# "moins de 4 ulp". It is a REPORTING budget: nothing exits on it.
ULP_BUDGET = 4
# The z beyond which a self-invalidating comparison stops being a fluctuation
# and becomes a finding to report. Fixed at 3 from the 0.27% two-sided normal
# tail and from nothing observed.
FINDING_Z = 3.0

# --- SOURCE-SEGMENT IDENTITY (control C7) ---
# Preamble S4.2 forbids hoisting a scientific primitive into
# experiments/common/, so every routine below is duplicated from the file that
# owns it and asserted byte-identical to that file at run time.
WITNESS_SOURCE = (BASE_DIR / "data" / "reference" / "R08"
                  / "Priorite_21b_adverse_bias_and_null_law.py")
WITNESS_PLOT_SOURCE = (BASE_DIR / "data" / "reference" / "R08"
                       / "Priorite_21c_plot_adverse_lattice.py")
R07_SOURCE = BASE_DIR / "experiments" / "R07_estimated_mean" / "exp_R07_estimated_mean.py"
WITNESS_CARRIED = ('wilson_ci', 'prop_test', 'lb_pvalue', 'compute_phi_hat_vectorized',
                   'cusum_concept_fast', 'generate_dgp')
R07_CARRIED = ('exceeds', 'exceeds_units_strict', 'exceeds_units_weak',
               'cusum_concept_lattice_units', 'lattice_exceedance_exact',
               'lattice_exceedance_enumerated', 'lattice_survival', 'lambda_star_from_rule',
               'get_deterministic_seed', 'seed_sequence_for', 'rng_for', 'sign_flip_null_max')
# The two primitives that are byte-identical to the R08 witness and only
# AST-identical to R07's copy of the same routine: R07's copy carries five blank
# lines the witness does not. C7 asserts normalized-AST equality across the two
# owners and logs the whitespace-only diff; byte identity would fail here and is
# not asserted.
CROSS_OWNER_AST_IDENTICAL = ('generate_dgp', 'compute_phi_hat_vectorized')
# The routines this port ADAPTS: restructured for a stated reason, so byte
# identity is not assertable and the witness source of each is quoted in full in
# the log instead -- but only after the S4.4 grep clears the segment.
ADAPTED_ROUTINES = ('worker_mod_A', 'worker_mod_B', 'plot_adverse_and_lattice', 'main')
# The routines the port does NOT carry at all. Preamble S4.2 pins a superseded
# routine by its SHA-256 and does NOT quote it, so that proscribed language
# cannot be imported into the log by way of a citation.
SUPERSEDED_ROUTINES = ('setup_logging', 'get_sha256', 'dump_requirements', 'get_md5')
# The S4.4 pattern, written so that NONE of the proscribed strings appears
# literally in this file. Every alternative carries one of its own characters
# inside a single-character class, which leaves the language the regular
# expression accepts unchanged while removing the literal from the source.
# Without that device the pattern would make this file fail the very grep it
# implements, and exempting the file that carries the pattern would be the wrong
# repair: the exemption, and not the pattern, is what would then have to be
# trusted. The equivalence is asserted against the preamble's own wording in
# tests/test_R08_claims.py.
BANNED_CONFIRMATORY = re.compile(
    r"prove[sn]|perfectl[y] valid|validate[s] the (theorem|thesi[s]|claim)|confirm[s] the|"
    r"as expecte[d]|triump[h]|victor[y]|irrefutabl[e]|brillian[t]", re.IGNORECASE)

# --- THE COMPARISON OPERATOR, AND THE NAMES CONTROL C1 POLICES ---
# Every exceedance test of a CUSUM statistic against a threshold goes through
# one of the three helpers below. C1 walks the AST of BOTH modules of this
# stream and requires that no other comparison mentions any of these names, so
# "module A and module B use the same operator" is verified rather than asserted
# from a comment. The design is R07's, carried unchanged.
COMPARISON_HELPERS = ('exceeds', 'exceeds_units_strict', 'exceeds_units_weak')
THRESHOLD_NAMES = frozenset({'lambda_star', 'lam', 'lam_units', 'lambda_units',
                             'threshold', 'threshold_units'})

# --- CROSS-STREAM INPUTS, READ round_trip ---
R07_LB_FPR = BASE_DIR / "results" / "R07_estimated_mean" / "data" / "R07_estmean_lb_fpr.csv"
R07_DIAGNOSTICS = (BASE_DIR / "results" / "R07_estimated_mean" / "data"
                   / "R07_estmean_diagnostics.csv")
R07_LATTICE = (BASE_DIR / "results" / "R07_estimated_mean" / "data"
               / "R07_lattice_exact_law.csv")
R10_LATTICE = (BASE_DIR / "results" / "R10_skew_robustness" / "data"
               / "R10_lattice_exact_law.csv")

ADVERSE_BIAS_COLUMNS = [
    'b', 'N_seeds', 'lb_reject_biased', 'lb_ci_low', 'lb_ci_high',
    'fpr_biased', 'fpr_ci_low', 'fpr_ci_high', 'lb_reject_naive_ref', 'fpr_naive_ref',
    'delta_lb_pp', 'delta_fpr_pp', 'z_lb', 'pval_lb', 'z_fpr', 'pval_fpr',
    'z_lb_paired', 'pval_lb_paired', 'z_fpr_paired', 'pval_fpr_paired',
    'deff_lb', 'deff_fpr']
NULL_LAW_COLUMNS = [
    'lambda', 'lambda_units', 'N_streams', 'P_exceed_strict', 'CI_low_strict', 'CI_high_strict',
    'P_exceed_weak', 'CI_low_weak', 'CI_high_weak', 'exact_level_strict', 'exact_level_weak',
    'is_lattice_point', 'bracket_role']
OPERATOR_LEVEL_COLUMNS = [
    'record_type', 'lambda_value', 'lambda_units', 'operator', 'n_streams',
    'exact_level', 'realised_level', 'disagreements_vs_strict', 'disagreements_vs_weak',
    'count_on_boundary', 'count_within_ulp_budget', 'count_float_above', 'count_float_below',
    'count_float_equal']
LATTICE_EXACT_COLUMNS = [
    'record_type', 'H', 'lambda_units', 'lambda_value', 'q', 'exact_level', 'enumerated_level',
    'abs_difference', 'r07_level', 'abs_difference_r07', 'bit_identical_r07',
    'r10_level', 'abs_difference_r10', 'bit_identical_r10', 'n_paths']
PAIRING_COLUMNS = [
    'record_type', 'b', 'n_trajectories', 'lb_reject_naive', 'fpr_naive',
    'r07_lb_reject_rate', 'r07_fpr_concept', 'bit_identical_lb', 'bit_identical_fpr',
    'lb_reject_biased', 'fpr_biased', 'delta_lb_pp', 'delta_fpr_pp',
    'n_discordant_lb', 'n_discordant_fpr', 'rho_lb', 'deff_lb', 'rho_fpr', 'deff_fpr',
    'statistic', 'observed', 'tabulated_pvalue', 'null_quantile', 'null_p', 'ci_low',
    'ci_high', 'n_resample']


# --- PRIMITIVES CARRIED FROM THE FILE THAT OWNS THEM ---
# Do not reformat. Byte identity is checked on the exact source text at start-up,
# trailing whitespace included (control C7).

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


def prop_test(p1: float, n1: int, p2: float, n2: int) -> tuple:
    """Two-sample test of proportions returning Z-score and bilateral p-value."""
    k1 = round(p1 * n1)
    k2 = round(p2 * n2)
    if n1 == 0 or n2 == 0:
        return 0.0, 1.0
    p = (k1 + k2) / (n1 + n2)
    if p == 0 or p == 1:
        return 0.0, 1.0
    se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se < 1e-12:
        return 0.0, 1.0
    z = (p1 - p2) / se
    pval = 2 * (1 - stats.norm.cdf(abs(z)))
    return float(z), float(pval)


def lb_pvalue(series: np.ndarray, lag: int = 20) -> float:
    """Computes the Ljung-Box p-value for a given lag."""
    if np.std(series) < 1e-12:
        return 1.0
    res = acorr_ljungbox(series, lags=[lag], return_df=True)
    return float(res['lb_pvalue'].iloc[0])


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

# --- CARRIED FROM exp_R07_estimated_mean.py, WHICH OWNS THEM ---
# The seed derivation, the three comparison helpers, the two lattice control
# instruments, the exact law and the sign-flip null. Byte-identical to R07 at
# run time (control C7); preamble S4.2 forbids hoisting any of them.

def get_deterministic_seed(*args) -> int:
    """
    Derives a 128-bit collision-free seed from the semantic coordinates of a
    task, returned as a scalar integer so no entropy is discarded. This is the
    repository's canonical form, carried from exp_R13_oracle_ceiling_a.py.

    Floats are formatted through .hex() rather than str(): the decimal repr of a
    float is platform-dependent at the last digit on some C libraries, which
    would silently re-key a cell across machines. The native hash() is randomly
    salted and is forbidden outright (SPECS 1.2).
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


def exceeds(M, lam):
    """
    The exceedance test of the campaign, used by BOTH the calibration path and
    the evaluation path. Control C1 parses this body and requires it to be a
    single `Compare` carrying `ast.Gt`, and requires that no other comparison in
    the module mentions a threshold name.
    """
    return M > lam


def exceeds_units_strict(m_units, lam_units):
    """Control instrument: the strict test on the exact integer lattice."""
    return m_units > lam_units


def exceeds_units_weak(m_units, lam_units):
    """Control instrument: the weak test on the exact integer lattice."""
    return m_units >= lam_units


def sign_flip_null_max(rng, differences, n_resample):
    """
    The null law of the MAXIMUM of `m` paired differences measured on shared
    trajectories (S4bis, 4th corollary).

    Under the null that the two arms of a discordant pair are exchangeable, the
    sign of every trajectory's paired difference is Rademacher. ONE sign per
    trajectory is drawn and applied to all `m` columns, so the dependence
    between columns induced by the common trajectories is carried into the null
    rather than assumed away. The trigger probability of a criterion read at
    level `a` against the (1 - a) quantile of this law is exactly `a`.

    A bootstrap of the observed differences is not usable here: it is centred on
    the observed value and is a sampling distribution, not a null.
    """
    n_units, _ = differences.shape
    maxima = np.zeros(n_resample, dtype=np.float64)
    for replicate in range(n_resample):
        signs = rng.integers(0, 2, size=n_units).astype(np.float64) * 2.0 - 1.0
        maxima[replicate] = np.abs(signs @ differences).max() / n_units
    return maxima


def cusum_concept_lattice_units(y_series) -> int:
    """
    The same recursion as `cusum_concept_fast`, in exact integer arithmetic on
    the 2delta lattice: the two branches move by +2 and -3 units of 2delta and
    are clamped at 0, so M is an integer and no rounding can occur.

    CONTROL INSTRUMENT ONLY. It never feeds a published value. It exists so that
    control C1 can MEASURE what the float comparison implements on the boundary
    instead of asserting it from the delivered script's comment.
    """
    s_pos = 0
    s_neg = 0
    m = 0
    for y in y_series.tolist():
        s_pos += LATTICE_UP if y else -LATTICE_DOWN
        if s_pos < 0:
            s_pos = 0
        elif s_pos > m:
            m = s_pos
        s_neg += -LATTICE_DOWN if y else LATTICE_UP
        if s_neg < 0:
            s_neg = 0
        elif s_neg > m:
            m = s_neg
    return m


def lattice_exceedance_exact(horizon: int, lam_units: int) -> float:
    """
    P(M_H > lam_units) under the fair-coin null, EXACTLY, by an absorbing-chain
    dynamic program over the joint state (S_pos, S_neg) of the two CUSUM
    branches in units of 2delta.

    The chain is finite: both branches are clamped at 0 below and absorbed above
    `lam_units`, so the state space is ({0..L} x {0..L}) plus one absorbing
    state, with L = lam_units. Each step splits the mass in half; the branch
    that grows moves by +2 and absorbs when it would exceed L, the branch that
    shrinks moves by -3 with a floor at 0. No entropy is consumed and the
    trigger probability of any assertion built on this value is exactly 0.
    """
    L = int(lam_units)
    if L < 4:
        sys.exit("FATAL: the lattice dynamic program is written for lam_units >= 4; the "
                 "column algebra below assumes at least one non-degenerate shrink block.")
    P = np.zeros((L + 1, L + 1), dtype=np.float64)
    P[0, 0] = 1.0
    absorbed = 0.0
    for _ in range(horizon):
        half = 0.5 * P
        # y = 1: S_pos -> S_pos + 2 (absorbed if it would exceed L),
        #        S_neg -> max(0, S_neg - 3).
        up_pos = np.zeros_like(P)
        up_pos[:, 0] = half[:, 0:LATTICE_DOWN + 1].sum(axis=1)
        up_pos[:, 1:L - LATTICE_DOWN + 1] = half[:, LATTICE_DOWN + 1:L + 1]
        # y = 0: the mirror image, by the exact symmetry of the two branches.
        up_neg = np.zeros_like(P)
        up_neg[0, :] = half[0:LATTICE_DOWN + 1, :].sum(axis=0)
        up_neg[1:L - LATTICE_DOWN + 1, :] = half[LATTICE_DOWN + 1:L + 1, :]
        Q = np.zeros_like(P)
        absorbed += up_pos[L - LATTICE_UP + 1:L + 1, :].sum()
        Q[LATTICE_UP:L + 1, :] += up_pos[0:L - LATTICE_UP + 1, :]
        absorbed += up_neg[:, L - LATTICE_UP + 1:L + 1].sum()
        Q[:, LATTICE_UP:L + 1] += up_neg[:, 0:L - LATTICE_UP + 1]
        P = Q
    return float(absorbed)


def lattice_exceedance_enumerated(horizon: int, lam_units: int) -> float:
    """
    P(M_H > lam_units) by exhaustive enumeration of all 2^H sign paths, through
    the integer recursion itself. Feasible only for the small horizons of
    `ENUMERATION_HORIZONS`; it is the independent check that the dynamic program
    is the law of the recursion and not of a transcription of it.
    """
    exceeding = 0
    for bits in itertools.product((0, 1), repeat=horizon):
        if exceeds_units_strict(cusum_concept_lattice_units(np.asarray(bits, dtype=np.int64)),
                                lam_units):
            exceeding += 1
    return exceeding / float(2 ** horizon)


def lattice_survival(horizon: int, scan_units) -> dict:
    """The exact survival function P(M_H > lambda) over the bracketing region."""
    return {u: lattice_exceedance_exact(horizon, u) for u in scan_units}


def lambda_star_from_rule(survival: dict) -> int:
    """
    v87 L241's own rule -- "we take the nearest attainable level at or below
    nominal" -- read on the exact law: the exceedance level is non-increasing in
    lambda, so the nearest attainable level at or below 5% is carried by the
    SMALLEST lattice threshold whose exact level is at or below nominal.
    """
    eligible = [u for u in sorted(survival) if survival[u] <= NOMINAL_LEVEL]
    if not eligible:
        sys.exit("FATAL: no lattice threshold of the scanned region attains a level at or below "
                 "nominal. The scan region is too narrow and preamble S4.7 forbids extrapolating "
                 "outside a grid: extend LATTICE_SCAN_UNITS in the source.")
    return eligible[0]


# --- LATTICE ARITHMETIC ON THE PRINTED DECIMALS ---

def lattice_units_of(decimal_text):
    """
    The lattice coordinate of a threshold, decided in EXACT rational arithmetic
    on the decimal v87 prints, and the verdict of `is_lattice_point`.

    DERIVATION, one line: with delta = 0.1 the two branches move by +0.4 and
    -0.6, both integer multiples of 2delta = 1/5, so M_H is supported on
    {u/5 : u in N} and a threshold is attainable exactly when 5*lambda is a
    non-negative integer.

    Neither float route decides this. `11.2 / 0.2` returns 55.99999999999999
    and `56 * 0.2` returns 11.200000000000001, so a float test would answer the
    question about the binary neighbour of the decimal rather than about the
    decimal. `Fraction(str)` is exact on the printed decimal and the
    `denominator == 1` test is the definition itself.
    """
    ratio = Fraction(decimal_text) / LATTICE_STEPS_PER_UNIT
    return (int(ratio) if ratio.denominator == 1 else None), ratio.denominator == 1


def clamp_unit_interval(value):
    """Preamble S7: every interval bound is clipped into [0, 1] before persistence."""
    return max(0.0, min(1.0, float(value)))


def binomial_se(rate, count):
    """
    The standard error of a proportion measured on `count` INDEPENDENT units.

    S4bis, 6th corollary: the design effect is stated before the standard error
    and never left implicit. The unit here is the trajectory (module A) or the
    fair-coin stream (module B); both are keyed on their index alone and share
    nothing, so the observations entering a SINGLE cell are i.i.d. and
    deff = 1.0 exactly. Pooling ACROSS cells is a different matter and is priced
    by the Kish factors this stream measures in `R08_pairing_diagnostic.csv`.
    deff = 1.0
    """
    return float(np.sqrt(rate * (1.0 - rate) / count))


def mcnemar_paired(indicator_a, indicator_b):
    """
    The paired comparison the design actually buys, and the reason the
    two-sample `prop_test` the witness carries is not it.

    The biased arm and the naive arm share the SAME trajectory at every b -- the
    entropy key carries the role and the index alone -- so the two rates are
    correlated and a two-sample test of proportions prices a variance the design
    does not have. McNemar's statistic conditions on the discordant pairs, which
    is the only randomness the null leaves.

    Returns (z, p, n_discordant, rho, deff). `rho` is the Pearson correlation of
    the two indicator columns over trajectories and `deff = 1 + (2 - 1) * rho`
    is the Kish factor of the two-cell block (S4bis, 3rd corollary). A constant
    column leaves the correlation undefined; that returns NaN and is logged by
    the caller rather than replaced by a fabricated 1.0.
    """
    a = np.asarray(indicator_a, dtype=np.int8)
    b = np.asarray(indicator_b, dtype=np.int8)
    n_10 = int(np.sum((a == 1) & (b == 0)))
    n_01 = int(np.sum((a == 0) & (b == 1)))
    discordant = n_10 + n_01
    if discordant == 0:
        z = 0.0
        pvalue = 1.0
    else:
        z = float((n_10 - n_01) / np.sqrt(discordant))
        pvalue = float(2.0 * (1.0 - stats.norm.cdf(abs(z))))
    if a.std() == 0.0 or b.std() == 0.0:
        rho = float('nan')
    else:
        rho = float(np.corrcoef(a.astype(np.float64), b.astype(np.float64))[0, 1])
    deff = float(1.0 + rho) if rho == rho else float('nan')
    return z, pvalue, discordant, rho, deff


def sign_flip_null_ks(rng, arm_a, arm_b, n_reference, n_resample):
    """
    The null law of the KS calibration statistic of the six proportion p-values,
    built by exchanging the two arms WITHIN a trajectory.

    The six p-values are dependent twice over: the six b share the same
    trajectories, and at each b the two arms share the same innovation stream.
    The tabulated Kolmogorov distribution assumes neither, so it is reported and
    not used. Under the null that the two arms of a trajectory are
    exchangeable, one Rademacher sign per trajectory -- SHARED across the six
    columns, so their dependence is carried into the null rather than assumed
    away -- swaps the pair, the six rates are recomputed, the six p-values are
    recomputed through the SAME carried `prop_test`, and the KS statistic of the
    replicate is stored.
    """
    n_units, n_columns = arm_a.shape
    statistics = np.zeros(n_resample, dtype=np.float64)
    for replicate in range(n_resample):
        take_a = rng.integers(0, 2, size=n_units).astype(bool)
        first = np.where(take_a[:, None], arm_a, arm_b)
        second = np.where(take_a[:, None], arm_b, arm_a)
        pvalues = np.zeros(n_columns, dtype=np.float64)
        for column in range(n_columns):
            _, pvalues[column] = prop_test(float(first[:, column].mean()), n_units,
                                           float(second[:, column].mean()), n_reference)
        statistics[replicate] = float(stats.kstest(pvalues, 'uniform').statistic)
    return statistics


def bootstrap_max_envelope(rng, differences, n_resample, alpha):
    """
    The sampling envelope of the MAXIMUM absolute paired difference over the six
    b, by resampling TRAJECTORIES with replacement.

    S4bis, 4th corollary: an extremum over six correlated cells has neither the
    distribution nor the interval of one cell. Preamble S3 fixes what this
    envelope is for -- a printed bound is crossed at D3 only when the 95%
    interval of the regenerated value EXCLUDES the bound -- so what is needed
    here is a sampling distribution and not a null, which is why this is a
    bootstrap and `sign_flip_null_max` is not.
    """
    n_units, _ = differences.shape
    maxima = np.zeros(n_resample, dtype=np.float64)
    for replicate in range(n_resample):
        draw = rng.integers(0, n_units, size=n_units)
        maxima[replicate] = float(np.abs(differences[draw, :].mean(axis=0)).max())
    return (float(np.quantile(maxima, alpha / 2.0)),
            float(np.quantile(maxima, 1.0 - alpha / 2.0)), maxima)


# --- SOURCE IDENTITY (control C7) ---

def source_segments(path, names):
    """
    Source text of the named top-level functions, extracted by position rather
    than by import: importing a delivered script would execute its environment
    block, its logger and its output-directory creation. Duplicated locally
    because preamble S4.2 forbids hoisting it into experiments/common/.
    """
    text = Path(path).read_text()
    tree = ast.parse(text)
    return {node.name: ast.get_source_segment(text, node)
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in names}


def control_c7_source_identity(logger):
    """
    C7. Byte identity of the eighteen carried primitives against the two files
    that own them, at run time; the normalized-AST control that underwrites
    control C6; and the disposal of the adapted and superseded routines.

    Deterministic, trigger probability 0 unless a copy has drifted.
    """
    for required in (WITNESS_SOURCE, WITNESS_PLOT_SOURCE, R07_SOURCE):
        if not required.exists():
            logger.error(f"C7 source-identity failure: {required} is missing, so no copy can be "
                         f"verified. The witnesses are vendored under data/reference/R08/ under "
                         f"their original names and are INPUTS of this experiment, not an archive.")
            sys.exit(1)
    witness = source_segments(WITNESS_SOURCE, set(WITNESS_CARRIED) | set(ADAPTED_ROUTINES)
                              | set(SUPERSEDED_ROUTINES))
    witness_plot = source_segments(WITNESS_PLOT_SOURCE,
                                   set(ADAPTED_ROUTINES) | set(SUPERSEDED_ROUTINES))
    r07 = source_segments(R07_SOURCE, set(R07_CARRIED) | set(CROSS_OWNER_AST_IDENTICAL))
    mine = source_segments(Path(__file__).resolve(), set(WITNESS_CARRIED) | set(R07_CARRIED))

    compared = 0
    for name, owner, table in ([(n, WITNESS_SOURCE.name, witness) for n in WITNESS_CARRIED]
                               + [(n, R07_SOURCE.name, r07) for n in R07_CARRIED]):
        remote = table.get(name)
        local = mine.get(name)
        if remote is None or local is None:
            logger.error(f"C7 source-identity failure: {name} could not be extracted from "
                         f"{owner} or from this module.")
            sys.exit(1)
        if local != remote:
            logger.error(f"C7 source-identity failure on {name}: the copy has drifted from "
                         f"{owner}.")
            sys.exit(1)
        compared += len(remote)
    logger.info(f"C7 SOURCE IDENTITY: {len(WITNESS_CARRIED)} primitives byte-identical to "
                f"{WITNESS_SOURCE.name} ({', '.join(WITNESS_CARRIED)}) and "
                f"{len(R07_CARRIED)} byte-identical to {R07_SOURCE.name} "
                f"({', '.join(R07_CARRIED)}); {compared} characters compared, 0 differences. "
                f"Preamble S4.2 forbids hoisting any of them into experiments/common/, so the "
                f"duplication is deliberate and it cannot drift. Deterministic; trigger "
                f"probability 0 unless a copy has drifted.")

    # The normalized-AST leg. This is what underwrites control C6: R08's b = 0
    # arm can only BE R07's OLS-250 arm at phi = 0 if the two files compute the
    # DGP and the rolling OLS with the same instructions.
    for name in CROSS_OWNER_AST_IDENTICAL:
        left = witness[name]
        right = r07[name]
        if ast.dump(ast.parse(left)) != ast.dump(ast.parse(right)):
            logger.error(f"C7 CROSS-OWNER failure on {name}: the R08 witness and "
                         f"{R07_SOURCE.name} do not parse to the same tree, so the cross-stream "
                         f"identity control C6 asserts has no basis.")
            sys.exit(1)
        left_lines = left.splitlines()
        right_lines = right.splitlines()
        extra_blank = [index + 1 for index, line in enumerate(right_lines)
                       if line.strip() == '']
        stripped_equal = ([line for line in left_lines if line.strip() != '']
                          == [line for line in right_lines if line.strip() != ''])
        logger.info(f"C7 CROSS-OWNER AST IDENTITY on {name}: byte identity against "
                    f"{R07_SOURCE.name} is FALSE and is not asserted -- R07's copy carries "
                    f"{len(extra_blank)} blank line(s) at positions {extra_blank} that the R08 "
                    f"witness does not, and every non-blank line is identical "
                    f"({stripped_equal}). `ast.dump(ast.parse(...))` of the two segments is "
                    f"EQUAL, so the two files compile the same instructions and control C6's "
                    f"cross-stream identity is a statement about entropy keys alone. "
                    f"SHA-256 witness {hashlib.sha256(left.encode('utf-8')).hexdigest()}, "
                    f"SHA-256 R07 {hashlib.sha256(right.encode('utf-8')).hexdigest()}.")

    # The adapted routines, quoted in full -- but only after the S4.4 grep
    # clears the segment. A segment that carries proscribed language is NOT
    # quoted: preamble S4.2 asks for the grep precisely so that a citation
    # cannot import banned wording into this log.
    logger.info(f"C7 ADAPTED ROUTINES. {list(ADAPTED_ROUTINES)} are restructured for the reasons "
                f"stated in the module docstring -- keyed entropy, per-trajectory return values, "
                f"the removal of the disk round trip, and the replacement of a certification "
                f"block that gates on four literals the script itself produced -- so byte "
                f"identity is not assertable on them. Each segment is passed through the S4.4 "
                f"grep FIRST and quoted in full only if the grep is empty.")
    for name in ADAPTED_ROUTINES:
        segment = witness.get(name) or witness_plot.get(name)
        origin = WITNESS_SOURCE.name if name in witness else WITNESS_PLOT_SOURCE.name
        if segment is None:
            logger.error(f"C7: neither witness carries {name}; the adaptation cannot be "
                         f"exhibited.")
            sys.exit(1)
        digest = hashlib.sha256(segment.encode('utf-8')).hexdigest()
        hits = [line.strip() for line in segment.splitlines() if BANNED_CONFIRMATORY.search(line)]
        logger.info(f"C7 witness SHA-256 of {name} [{origin}]: {digest}")
        if hits:
            logger.info(f"C7 {name} is NOT quoted: the S4.4 grep returns {len(hits)} line(s) "
                        f"carrying proscribed wording inside the segment, and preamble S4.2 makes "
                        f"the grep a precondition of the citation precisely so that a quotation "
                        f"cannot import that wording into this log. The routine is pinned by the "
                        f"SHA-256 above and its adaptation is described in the module docstring "
                        f"and in docs/audits/AUDIT_R08.md instead. Line numbers in {origin}: "
                        f"{[i + 1 for i, line in enumerate(segment.splitlines()) if BANNED_CONFIRMATORY.search(line)]}.")
        else:
            logger.info(f"C7 S4.4 grep on {name}: empty. Witness source of {name}:\n"
                        f"{segment.rstrip()}")
    logger.info(f"C7 SUPERSEDED ROUTINES. {list(SUPERSEDED_ROUTINES)} are NOT carried at all: the "
                f"FAIR harness supplies `setup_logging`, `compute_sha256` and `save_fair_csv`, "
                f"the version relevé goes through `importlib.metadata.version()` in "
                f"`log_environment`, and `get_md5` is superseded by SHA-256 outright. Preamble "
                f"S4.2 pins a superseded routine by its digest and does not quote it.")
    for name in SUPERSEDED_ROUTINES:
        segment = witness.get(name) or witness_plot.get(name)
        if segment is None:
            logger.error(f"C7: neither witness carries the superseded routine {name}.")
            sys.exit(1)
        origin = WITNESS_SOURCE.name if name in witness else WITNESS_PLOT_SOURCE.name
        logger.info(f"C7 superseded SHA-256 of {name} [{origin}]: "
                    f"{hashlib.sha256(segment.encode('utf-8')).hexdigest()}")


def control_c1_operator_identity(logger):
    """
    C1 (i)-(iii). The AST of BOTH modules of this stream is parsed and the
    exceedance operator is asserted rather than read: `exceeds` must be a single
    `Compare` carrying `ast.Gt`; no comparison OUTSIDE the three declared
    helpers may ORDER a threshold name against anything; and the module-A worker
    and the module-B level routine must call the declared helpers. Identity of
    the operator between the lambda* selection path and module A's evaluation
    path then holds by construction and is verified.

    Deterministic, trigger probability 0.
    """
    module_a = Path(__file__).resolve()
    module_b = module_a.parent / "exp_R08_adverse_lattice_b.py"
    if not module_b.exists():
        logger.error(f"C1 FAILED: {module_b.name} is missing, so the operator cannot be asserted "
                     f"identical across the two modules of this stream.")
        sys.exit(1)

    trees = {}
    for path in (module_a, module_b):
        trees[path.name] = ast.parse(path.read_text())
    functions = {node.name: node for node in ast.walk(trees[module_a.name])
                 if isinstance(node, ast.FunctionDef)}

    body = functions['exceeds'].body
    statements = [node for node in body if not (isinstance(node, ast.Expr)
                                                and isinstance(node.value, ast.Constant))]
    if len(statements) != 1 or not isinstance(statements[0], ast.Return):
        logger.error(f"C1 FAILED: `exceeds` has {len(statements)} statements after its docstring; "
                     f"exactly one `return` is required.")
        sys.exit(1)
    compare = statements[0].value
    if not isinstance(compare, ast.Compare) or len(compare.ops) != 1 \
            or not isinstance(compare.ops[0], ast.Gt):
        logger.error("C1 FAILED: the body of `exceeds` is not a single strict-greater comparison.")
        sys.exit(1)

    whitelisted = set()
    for helper in COMPARISON_HELPERS:
        for node in ast.walk(functions[helper]):
            if isinstance(node, ast.Compare):
                whitelisted.add(id(node))
    ordering_ops = (ast.Gt, ast.GtE, ast.Lt, ast.LtE)
    offending = []
    total_comparisons = 0
    for name, tree in trees.items():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare):
                continue
            total_comparisons += 1
            if id(node) in whitelisted:
                continue
            names = {sub.id for sub in ast.walk(node) if isinstance(sub, ast.Name)}
            if (names & THRESHOLD_NAMES) and any(isinstance(op, ordering_ops) for op in node.ops):
                offending.append((name, getattr(node, 'lineno', -1),
                                  sorted(names & THRESHOLD_NAMES)))
    if offending:
        logger.error(f"C1 FAILED: {len(offending)} ordering comparison(s) outside "
                     f"{COMPARISON_HELPERS} mention a threshold name: {offending}. Every "
                     f"exceedance test must route through the helpers so that the lambda* "
                     f"selection path and module A's evaluation path cannot diverge.")
        sys.exit(1)

    routed = {'worker_mod_A': {'exceeds'},
              'operator_levels_at': set(COMPARISON_HELPERS),
              'lattice_exceedance_enumerated': {'exceeds_units_strict'}}
    for routine, required in routed.items():
        called = {sub.func.id for sub in ast.walk(functions[routine])
                  if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)}
        missing = required - called
        if missing:
            logger.error(f"C1 FAILED: `{routine}` does not call {sorted(missing)}; the operator "
                         f"identity between module A and module B cannot be established.")
            sys.exit(1)
    logger.info(f"C1 (i)-(iii) OPERATOR IDENTITY, by AST, over BOTH modules of this stream. "
                f"`exceeds` is a single `Compare` carrying `ast.Gt`; of the {total_comparisons} "
                f"comparisons in exp_R08_adverse_lattice_a.py and exp_R08_adverse_lattice_b.py, "
                f"the {len(whitelisted)} inside {list(COMPARISON_HELPERS)} are the only ones that "
                f"may ORDER a threshold name against anything, and none of the others does. "
                f"`worker_mod_A` calls `exceeds`; `operator_levels_at` calls all three helpers; "
                f"`lattice_exceedance_enumerated` calls `exceeds_units_strict`. lambda* itself "
                f"comes from `lambda_star_from_rule` on the EXACT law, so the selection path and "
                f"the evaluation path test the same operator by construction. Deterministic; "
                f"trigger probability 0.")


# --- PARALLEL WORKERS, ADAPTED FROM THE DELIVERED SCRIPT ---

def worker_mod_A(trajectory_index, lambda_star):
    """
    ADAPTED from the delivered `worker_mod_A` (witness l.172-195). Three
    changes, each forced by the preamble.

    (i) ENTROPY. The delivered worker received the s-th element of a
        `spawn(7 * 10000)` list; the trajectory is now keyed on the 128-bit
        condensate of ("trajectory", index) alone. The key is R07's, and that
        is the point: control C6 then reads as an exact identity.
    (ii) PER-TRAJECTORY RETURN VALUES. Controls C4, C5 and C6 all need a unit
        of resampling and the trajectory is the only i.i.d. unit of this design,
        so the worker returns the raw indicators rather than a rate.
    (iii) THE PAIRING DIAGNOSTIC IS COMPUTED HERE. The delivered script read the
        naive reference arm from `protocol_21a`, a CSV of another campaign. This
        worker recomputes it -- `generate_dgp` at phi = b on the SAME key -- so
        that control C6 can assert the cross-stream identity rather than assume
        it. Seven `generate_dgp` calls per trajectory is the price of byte
        identity with the carried primitive and it is deliberately not
        vectorised into one `eps` draw.

    Every scientific line inside is the witness's: the same `generate_dgp`, the
    same [1000:6000] / [1001:6001] slicing, the same `compute_phi_hat_vectorized`
    at n = 250, the same `lb_pvalue` at lag 20, the same `cusum_concept_fast` at
    delta = 0.1.
    """
    seed_sq = seed_sequence_for("trajectory", trajectory_index)
    width = len(B_GRID)
    lb_biased = np.zeros(width, dtype=bool)
    fpr_biased = np.zeros(width, dtype=bool)
    m_float_biased = np.zeros(width, dtype=np.float64)
    m_units_biased = np.zeros(width, dtype=np.int64)
    lb_naive = np.zeros(width, dtype=bool)
    fpr_naive = np.zeros(width, dtype=bool)
    degenerate = np.zeros(2 * width, dtype=bool)

    r = generate_dgp(T_PATH, PHI_INJECTED, seed_sq)
    r_prev = r[EVAL_START - 1:EVAL_END - 1]
    r_curr = r[EVAL_START:EVAL_END]
    phi_hat = compute_phi_hat_vectorized(r, N_OLS, EVAL_START, EVAL_END)
    for index, bias in enumerate(B_GRID):
        mu_hat_biased = (phi_hat + bias) * r_prev
        y_biased = (r_curr - mu_hat_biased > 0).astype(int)
        degenerate[index] = bool(y_biased.min() == y_biased.max())
        lb_biased[index] = bool(lb_pvalue(y_biased, LB_LAG) < LB_LEVEL)
        statistic = cusum_concept_fast(y_biased, DELTA)
        m_float_biased[index] = statistic
        fpr_biased[index] = bool(exceeds(statistic, lambda_star))
        m_units_biased[index] = cusum_concept_lattice_units(y_biased)

    for index, bias in enumerate(B_GRID):
        r_naive = generate_dgp(T_PATH, bias, seed_sq)
        y_naive = (r_naive[EVAL_START:EVAL_END] > 0).astype(int)
        degenerate[width + index] = bool(y_naive.min() == y_naive.max())
        lb_naive[index] = bool(lb_pvalue(y_naive, LB_LAG) < LB_LEVEL)
        fpr_naive[index] = bool(exceeds(cusum_concept_fast(y_naive, DELTA), lambda_star))

    return {'lb_biased': lb_biased, 'fpr_biased': fpr_biased,
            'm_float_biased': m_float_biased, 'm_units_biased': m_units_biased,
            'lb_naive': lb_naive, 'fpr_naive': fpr_naive, 'degenerate': degenerate}


def trajectory_chunk(start, stop, lambda_star):
    """One chunk of trajectories, stacked. Chunk boundaries are fixed constants."""
    results = [worker_mod_A(index, lambda_star) for index in range(start, stop)]
    return {key: np.stack([item[key] for item in results]) for key in results[0]}


def worker_mod_B(stream_index):
    """
    ADAPTED from the delivered `worker_mod_B` (witness l.197-200). Two changes.

    (i) ENTROPY, as above: the stream is keyed on ("lattice_stream", index).
    (ii) BOTH FORMS OF THE STATISTIC ARE RETURNED. The delivered worker returns
        the float maximum only, and the delivered `main` then rounds it to six
        decimals before comparing (witness l.337, l.369), which silently turns
        the reported level into the STRICT lattice level. The integer recursion
        is computed here beside the float one, so control C1 can measure what
        each operator delivers instead of inferring it from a rounding.
    """
    rng = rng_for("lattice_stream", stream_index)
    y = rng.integers(0, 2, size=H)
    return cusum_concept_fast(y, DELTA), cusum_concept_lattice_units(y)


def lattice_chunk(start, stop):
    """One chunk of fair-coin streams. Chunk boundaries are fixed constants."""
    m_float = np.zeros(stop - start, dtype=np.float64)
    m_units = np.zeros(stop - start, dtype=np.int64)
    for index in range(start, stop):
        m_float[index - start], m_units[index - start] = worker_mod_B(index)
    return m_float, m_units


def operator_levels_at(m_float, m_units, units, threshold_value):
    """
    The three realised levels at one threshold, and the disagreement counts
    between them.

    This is the only place in either module where a measured statistic meets a
    threshold, and it routes through all three declared helpers so that control
    C1's AST assertion covers module B as well as module A.
    """
    float_flag = exceeds(m_float, threshold_value)
    strict_flag = exceeds_units_strict(m_units, units)
    weak_flag = exceeds_units_weak(m_units, units)
    return {'float': float_flag, 'strict': strict_flag, 'weak': weak_flag,
            'level_float': float(np.mean(float_flag)),
            'level_strict': float(np.mean(strict_flag)),
            'level_weak': float(np.mean(weak_flag)),
            'disagree_strict': int(np.sum(float_flag != strict_flag)),
            'disagree_weak': int(np.sum(float_flag != weak_flag)),
            'on_boundary': int(np.sum(m_units == units))}


# --- THE CAMPAIGN ---

def read_round_trip(path, logger):
    """Preamble S3: every CSV read destined for a comparison is `round_trip`."""
    if not path.exists():
        logger.error(f"Missing cross-stream input: {path}. R08 reads it as an INPUT and does not "
                     f"regenerate it; run the stream that owns it first.")
        sys.exit(1)
    return pd.read_csv(path, float_precision='round_trip')


def run_campaign(logger, n_jobs, fast):
    """
    The whole measurement, in memory: the exact law, module A, module B and the
    five frames. `exp_R08_adverse_lattice_b.py` calls this again rather than
    reloading a CSV, because preamble S7 forbids a disk round trip as a memory
    bridge.
    """
    n_seeds = FAST_N_SEEDS if fast else N_SEEDS
    n_lattice = FAST_N_LATTICE if fast else N_LATTICE
    stamp = "_fast" if fast else ""
    if fast:
        logger.info(f"DEGRADED PATH SELECTED EXPLICITLY (S4.3). `--fast` reduces N_SEEDS "
                    f"{N_SEEDS} -> {n_seeds} and N_LATTICE {N_LATTICE} -> {n_lattice}. Every "
                    f"artefact of this run is stamped `{stamp}` and certifies NO v87 value. The "
                    f"delivered script took the same reduction under the same file names.")

    # =================================================================
    # 0. THE ARITHMETIC OF EVERY MULTI-TEST CONTROL, BEFORE ANY RESULT
    # =================================================================
    family = 1.0 - (1.0 - LB_LEVEL) ** len(B_GRID)
    logger.info(f"FAMILY-WISE ARITHMETIC, LOGGED BEFORE ANY RESULT IS INTERPRETED (S4bis.1). "
                f"Control C4 compares the two arms at {len(B_GRID)} values of b. Gating on "
                f"'no test rejects' at the {LB_LEVEL:g} level would trigger with probability "
                f"1 - (1 - {LB_LEVEL:g})^{len(B_GRID)} = {family:.4%} under the hypothesis of "
                f"equality itself -- far above the 5% ceiling S4bis fixes. 'No test rejects' is "
                f"therefore NOT used as a gate, and neither is 'two tests reject' used as a "
                f"refutation. The substitute is a KS calibration of the six p-values against "
                f"Uniform(0,1), read against a null built by sign-flip resampling on the "
                f"trajectory index, because the six p-values are dependent twice over and the "
                f"tabulated Kolmogorov distribution assumes neither dependence.")

    # =================================================================
    # 1. THE EXACT LAW OF THE LATTICE, AND lambda* BY L241's OWN RULE
    # =================================================================
    logger.info(f"C1/C2 THE EXACT LATTICE LAW. With delta = {DELTA} the two CUSUM branches move "
                f"by +0.4 and -0.6, i.e. by +{LATTICE_UP} and -{LATTICE_DOWN} in units of "
                f"2delta = {LATTICE_UNIT}, so (S_pos, S_neg) is a Markov chain on the "
                f"non-negative integer quadrant and M_H is an integer multiple of "
                f"{LATTICE_UNIT}. An absorbing-chain dynamic program over that state space at "
                f"H = {H} gives P(M_H > lambda) exactly. No Monte-Carlo is involved and no "
                f"entropy is consumed; the trigger probability of every assertion resting on it "
                f"is 0.")
    t_exact = time.time()
    survival = lattice_survival(H, LATTICE_SCAN_UNITS)
    star_units = lambda_star_from_rule(survival)
    lambda_star = star_units * LATTICE_UNIT
    logger.info(f"C1 lambda* BY L241's OWN RULE, evaluated on the exact law in "
                f"{time.time() - t_exact:.1f}s: 'we take the nearest attainable level at or "
                f"below nominal' selects the SMALLEST lattice threshold whose exact level is at "
                f"or below {NOMINAL_LEVEL}, which is {star_units} lattice units = "
                f"{lambda_star!r}. v87 prints lambda* = {V87_LAMBDA_STAR}, and "
                f"{star_units} * {LATTICE_UNIT} == {V87_LAMBDA_STAR} is "
                f"{star_units * LATTICE_UNIT == V87_LAMBDA_STAR} bit-for-bit in float64. The "
                f"delivered `float(np.quantile(Ms_cal, 0.95))` on 20,000 fair-coin streams "
                f"(witness l.228-233) is a superseded estimator: it sits astride a lattice "
                f"boundary and docs/DEVIATIONS.md `R07-lambda-star-estimator` already registers "
                f"it with the exact probability that it returns 11.4. R08 cites that entry and "
                f"opens no duplicate.")
    if star_units * LATTICE_UNIT != V87_LAMBDA_STAR:
        logger.error(f"C1 FAILED: L241's own rule selects {star_units} lattice units, i.e. "
                     f"{star_units * LATTICE_UNIT!r}, which is not the {V87_LAMBDA_STAR} v87 "
                     f"prints. The threshold behind every number of this stream would not be the "
                     f"published one.")
        sys.exit(1)

    grid = []
    for decimal_text in LAMBDA_GRID_DECIMAL:
        units, is_lattice = lattice_units_of(decimal_text)
        if not is_lattice:
            logger.error(f"C3 FAILED: the grid point {decimal_text} is not an integer multiple "
                         f"of 2delta = 1/5, so P(M_H > lambda) at that threshold is not a level "
                         f"the statistic can attain and the panel-C step function has no step "
                         f"there.")
            sys.exit(1)
        grid.append({'decimal': decimal_text, 'value': float(decimal_text), 'units': units,
                     'is_lattice_point': is_lattice})
    probe_units, probe_is_lattice = lattice_units_of(NON_LATTICE_PROBE_DECIMAL)
    logger.info(f"IS_LATTICE_POINT IS COMPUTED, NOT WRITTEN (prompt section 2.6). The witness "
                f"line 373 is the bare assignment `is_lattice = True` -- an `ast.Constant`, not a "
                f"computation -- so the column carries no information in the delivered CSV. Here "
                f"the verdict is taken in exact rational arithmetic on the decimal v87 prints: "
                f"5*lambda must be an integer. On the six grid points the verdict is "
                f"{[(item['decimal'], item['units'], item['is_lattice_point']) for item in grid]}; "
                f"on the probe {NON_LATTICE_PROBE_DECIMAL}, which is not a multiple of 2delta, it "
                f"is {probe_is_lattice} with units {probe_units}. The probe is a negative control "
                f"of the column and enters no artefact. Neither float route decides this: "
                f"11.2 / 0.2 = {11.2 / LATTICE_UNIT!r} and 56 * 0.2 = {56 * LATTICE_UNIT!r}.")

    # C3's own arithmetic, before the measured levels exist.
    exact_strict = {item['units']: survival[item['units']] for item in grid}
    threshold_count = int(np.floor(NOMINAL_LEVEL * n_lattice))
    correct_side = 1.0
    for item in grid:
        level_value = exact_strict[item['units']]
        if level_value > NOMINAL_LEVEL:
            correct_side *= float(stats.binom.sf(threshold_count, n_lattice, level_value))
        else:
            correct_side *= float(stats.binom.cdf(threshold_count, n_lattice, level_value))
    c3_trigger = 1.0 - correct_side
    logger.info(f"C3, BEFORE ANY RESULT IS READ. The bracketing roles are computed on the EXACT "
                f"law, where the trigger probability is 0. The SAME roles are then required of "
                f"the MEASURED strict levels, and that leg has a computable trigger probability "
                f"under its own null: the exact level at lambda = 11.2 is "
                f"{100.0 * exact_strict[grid[1]['units']]:.4f}%, which is only "
                f"{(exact_strict[grid[1]['units']] - NOMINAL_LEVEL) / binomial_se(exact_strict[grid[1]['units']], n_lattice):.2f} "
                f"binomial standard errors above the {NOMINAL_LEVEL:g} nominal at "
                f"{n_lattice} streams, so a Monte-Carlo realisation on the wrong side of nominal "
                f"is an ordinary event. Summed over the {len(grid)} grid points the probability "
                f"that at least one lands on the wrong side of nominal is {c3_trigger:.4%}. "
                f"S4bis forbids reading a gate whose trigger probability under its own null is "
                f"of that size: the measured leg is a REPORTED control, it logs an error and the "
                f"run continues, and only the exact leg exits.")

    logger.info(f"C4, BEFORE ANY RESULT IS READ. The three-point bound of L311 is a MAXIMUM over "
                f"the {len(B_GRID)} values of b of a paired difference measured on shared "
                f"trajectories. S4bis's 4th corollary forbids reading it against the tolerance "
                f"of one point: the sampling envelope of the maximum is built by resampling "
                f"trajectories ({N_RESAMPLE_BOOT} replicates) and preamble S3 fixes what it is "
                f"for -- a printed bound is crossed at D3 only when the 95% interval of the "
                f"regenerated value EXCLUDES it. The null law of the same maximum under "
                f"exchangeability of the two arms is built separately by sign-flip resampling "
                f"({N_RESAMPLE_NULL} replicates), read at level {C4_NULL_LEVEL:g}, whose trigger "
                f"probability under that null is exactly {C4_NULL_LEVEL:g} by construction.")

    # =================================================================
    # 2. MODULE A -- THE ADVERSE DIRECTION
    # =================================================================
    logger.info(f"MODULE A: {n_seeds} trajectories, phi = {PHI_INJECTED}, n_ols = {N_OLS}, "
                f"T = {T_PATH}, evaluation on [{EVAL_START}:{EVAL_END}], b in {list(B_GRID)}. "
                f"Each trajectory carries BOTH arms: the injected-bias arm "
                f"mu_hat = (phi_hat + b) r_prev at phi = 0, and the naive pairing diagnostic "
                f"r_naive[t] > 0 at phi = b on the SAME key.")
    t_module_a = time.time()
    bounds_a = [(start, min(start + CHUNK_SIZE, n_seeds))
                for start in range(0, n_seeds, CHUNK_SIZE)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_jobs) as executor:
        futures_a = [executor.submit(trajectory_chunk, start, stop, lambda_star)
                     for start, stop in bounds_a]
        collected_a = []
        for (start, stop), future in zip(bounds_a, futures_a):
            try:
                collected_a.append(future.result())
            except Exception:
                logger.error(f"Module A worker for [{start}:{stop}] raised:\n"
                             f"{traceback.format_exc()}")
                raise
        module_a = {key: np.concatenate([chunk[key] for chunk in collected_a])
                    for key in collected_a[0]}
        cost_a = time.time() - t_module_a
        logger.info(f"Module A completed in {cost_a:.1f}s on {n_jobs} workers "
                    f"({len(bounds_a)} chunks of {CHUNK_SIZE}).")

        # =============================================================
        # 3. MODULE B -- THE NULL LAW OF THE LATTICE
        # =============================================================
        logger.info(f"MODULE B: {n_lattice} fair-coin streams at H = {H}, keyed "
                    f"('lattice_stream', index). Each stream yields BOTH the float statistic and "
                    f"the exact integer one. Both are required: the integer form gives the two "
                    f"exact-operator levels, the float form gives the level the implemented test "
                    f"delivers and the boundary count. The delivered module B computed the float "
                    f"form alone and rounded it to six decimals before comparing, which reports "
                    f"the strict lattice level without saying so.")
        t_module_b = time.time()
        bounds_b = [(start, min(start + LATTICE_CHUNK_SIZE, n_lattice))
                    for start in range(0, n_lattice, LATTICE_CHUNK_SIZE)]
        futures_b = [executor.submit(lattice_chunk, start, stop) for start, stop in bounds_b]
        floats, units_list = [], []
        for (start, stop), future in zip(bounds_b, futures_b):
            try:
                chunk_float, chunk_units = future.result()
            except Exception:
                logger.error(f"Module B worker for [{start}:{stop}] raised:\n"
                             f"{traceback.format_exc()}")
                raise
            floats.append(chunk_float)
            units_list.append(chunk_units)
        m_float = np.concatenate(floats)
        m_units = np.concatenate(units_list)
        cost_b = time.time() - t_module_b
        logger.info(f"Module B completed in {cost_b:.1f}s on {n_jobs} workers "
                    f"({len(bounds_b)} chunks of {LATTICE_CHUNK_SIZE}). The delivered module B "
                    f"computed the float statistic alone; computing both forms is the cost this "
                    f"stream pays to measure the operator instead of inferring it.")

    if module_a['lb_biased'].shape != (n_seeds, len(B_GRID)):
        logger.error(f"Module A shape is {module_a['lb_biased'].shape}, expected "
                     f"{(n_seeds, len(B_GRID))}.")
        sys.exit(1)
    if len(m_float) != n_lattice:
        logger.error(f"Module B returned {len(m_float)} streams, expected {n_lattice}.")
        sys.exit(1)

    degenerate_total = int(module_a['degenerate'].sum())
    logger.info(f"NO DEGRADED PATH ON THE CARRIED lb_pvalue (S4.3): a constant sign stream would "
                f"take its `np.std(series) < 1e-12` branch and return the non-rejection 1.0 "
                f"without any test being run. Over the {2 * len(B_GRID) * n_seeds} module-A "
                f"streams the branch was taken {degenerate_total} times. The other two fallbacks "
                f"of the carried primitives -- `compute_phi_hat_vectorized`'s "
                f"`sum_den >= 1e-12` mask and `generate_dgp`'s `h[t] = max(..., 1e-12)` floor -- "
                f"are established unreachable on this DGP and these keys by control C7 of "
                f"exp_R07_estimated_mean.py, which runs the same recursion on the same "
                f"trajectory keys; R08 cites that measurement and does not re-run it.")

    # =================================================================
    # 4. THE CROSS-STREAM REFERENCE, READ round_trip
    # =================================================================
    r07_frame = read_round_trip(R07_LB_FPR, logger)
    naive_reference = {}
    for bias in B_GRID:
        row = r07_frame[(r07_frame['arm'] == 'NAIVE')
                        & np.isclose(r07_frame['phi'].to_numpy(dtype=float), bias,
                                     rtol=0.0, atol=0.0)]
        if len(row) != 1:
            logger.error(f"R07_estmean_lb_fpr.csv carries {len(row)} NAIVE rows at phi = {bias!r}; "
                         f"exactly one is required.")
            sys.exit(1)
        naive_reference[bias] = row.iloc[0]
    ols_reference = r07_frame[(r07_frame['arm'] == 'OLS-250')
                              & np.isclose(r07_frame['phi'].to_numpy(dtype=float), PHI_INJECTED,
                                           rtol=0.0, atol=0.0)]
    if len(ols_reference) != 1:
        logger.error(f"R07_estmean_lb_fpr.csv carries {len(ols_reference)} OLS-250 rows at "
                     f"phi = {PHI_INJECTED!r}; exactly one is required.")
        sys.exit(1)
    ols_reference = ols_reference.iloc[0]

    # =================================================================
    # 5. FRAME 1 -- R08_adverse_bias.csv (v87 panels A and B)
    # =================================================================
    adverse_rows = []
    for index, bias in enumerate(B_GRID):
        biased_lb = module_a['lb_biased'][:, index]
        biased_fpr = module_a['fpr_biased'][:, index]
        naive_lb = module_a['lb_naive'][:, index]
        naive_fpr = module_a['fpr_naive'][:, index]
        k_lb = int(biased_lb.sum())
        k_fpr = int(biased_fpr.sum())
        lb_rate = k_lb / n_seeds
        fpr_rate = k_fpr / n_seeds
        lb_low, lb_high = wilson_ci(k_lb, n_seeds)
        fpr_low, fpr_high = wilson_ci(k_fpr, n_seeds)
        reference = naive_reference[bias]
        ref_lb_rate = float(reference['lb_reject_rate'])
        ref_fpr_rate = float(reference['fpr_concept'])
        n_reference = int(reference['N_seeds'])
        z_lb, pval_lb = prop_test(lb_rate, n_seeds, ref_lb_rate, n_reference)
        z_fpr, pval_fpr = prop_test(fpr_rate, n_seeds, ref_fpr_rate, n_reference)
        z_lb_paired, p_lb_paired, discordant_lb, rho_lb, deff_lb = mcnemar_paired(biased_lb,
                                                                                 naive_lb)
        z_fpr_paired, p_fpr_paired, discordant_fpr, rho_fpr, deff_fpr = mcnemar_paired(biased_fpr,
                                                                                       naive_fpr)
        if rho_lb != rho_lb or rho_fpr != rho_fpr:
            logger.info(f"DESIGN EFFECT UNDEFINED at b = {bias!r}: one of the two indicator "
                        f"columns is constant over the {n_seeds} trajectories, which leaves the "
                        f"Pearson correlation undefined (rho_lb = {rho_lb!r}, "
                        f"rho_fpr = {rho_fpr!r}). The cell carries NaN rather than a fabricated "
                        f"1.0; S4.3 forbids replacing an undefined quantity with a default.")
        adverse_rows.append({
            'b': bias, 'N_seeds': n_seeds,
            'lb_reject_biased': lb_rate, 'lb_ci_low': clamp_unit_interval(lb_low),
            'lb_ci_high': clamp_unit_interval(lb_high),
            'fpr_biased': fpr_rate, 'fpr_ci_low': clamp_unit_interval(fpr_low),
            'fpr_ci_high': clamp_unit_interval(fpr_high),
            'lb_reject_naive_ref': ref_lb_rate, 'fpr_naive_ref': ref_fpr_rate,
            'delta_lb_pp': lb_rate - ref_lb_rate, 'delta_fpr_pp': fpr_rate - ref_fpr_rate,
            'z_lb': z_lb, 'pval_lb': pval_lb, 'z_fpr': z_fpr, 'pval_fpr': pval_fpr,
            'z_lb_paired': z_lb_paired, 'pval_lb_paired': p_lb_paired,
            'z_fpr_paired': z_fpr_paired, 'pval_fpr_paired': p_fpr_paired,
            'deff_lb': deff_lb, 'deff_fpr': deff_fpr})
    adverse_bias = pd.DataFrame(adverse_rows, columns=ADVERSE_BIAS_COLUMNS)

    # =================================================================
    # 6. FRAME 2 -- R08_null_law_lattice.csv (v87 panel C, L241)
    # =================================================================
    measured = {}
    for item in grid:
        measured[item['units']] = operator_levels_at(m_float, m_units, item['units'],
                                                     item['value'])
    roles_exact = bracket_roles(grid, {item['units']: survival[item['units']] for item in grid})
    roles_measured = bracket_roles(grid, {item['units']: measured[item['units']]['level_strict']
                                          for item in grid})
    null_rows = []
    for item in grid:
        units = item['units']
        cell = measured[units]
        k_strict = int(round(cell['level_strict'] * n_lattice))
        k_weak = int(round(cell['level_weak'] * n_lattice))
        low_strict, high_strict = wilson_ci(k_strict, n_lattice)
        low_weak, high_weak = wilson_ci(k_weak, n_lattice)
        null_rows.append({
            'lambda': item['value'], 'lambda_units': units, 'N_streams': n_lattice,
            'P_exceed_strict': cell['level_strict'],
            'CI_low_strict': clamp_unit_interval(low_strict),
            'CI_high_strict': clamp_unit_interval(high_strict),
            'P_exceed_weak': cell['level_weak'],
            'CI_low_weak': clamp_unit_interval(low_weak),
            'CI_high_weak': clamp_unit_interval(high_weak),
            'exact_level_strict': survival[units], 'exact_level_weak': survival[units - 1],
            'is_lattice_point': item['is_lattice_point'], 'bracket_role': roles_exact[units]})
    null_law = pd.DataFrame(null_rows, columns=NULL_LAW_COLUMNS)

    # =================================================================
    # 7. FRAME 3 -- R08_operator_levels.csv (control C1, no v87 value)
    # =================================================================
    exact_value = m_units * LATTICE_UNIT
    float_above = int((m_float > exact_value).sum())
    float_below = int((m_float < exact_value).sum())
    float_equal = int((m_float == exact_value).sum())
    spacing = np.spacing(np.maximum(exact_value, LATTICE_UNIT))
    within_budget = int((np.abs(m_float - exact_value) <= ULP_BUDGET * spacing).sum())
    star_cell = measured[star_units]
    operator_rows = []
    for item in grid:
        units = item['units']
        for operator_name, index_used in (('exact M_units > lambda', units),
                                          ('exact M_units >= lambda', units - 1)):
            operator_rows.append({
                'record_type': 'exact_level', 'lambda_value': item['value'],
                'lambda_units': units, 'operator': operator_name, 'n_streams': np.nan,
                'exact_level': survival[index_used], 'realised_level': np.nan,
                'disagreements_vs_strict': np.nan, 'disagreements_vs_weak': np.nan,
                'count_on_boundary': np.nan, 'count_within_ulp_budget': np.nan,
                'count_float_above': np.nan, 'count_float_below': np.nan,
                'count_float_equal': np.nan})
    for item in grid:
        units = item['units']
        cell = measured[units]
        for operator_name, key in (('float M > lambda', 'level_float'),
                                   ('exact M_units > lambda', 'level_strict'),
                                   ('exact M_units >= lambda', 'level_weak')):
            flag = cell[{'level_float': 'float', 'level_strict': 'strict',
                         'level_weak': 'weak'}[key]]
            operator_rows.append({
                'record_type': 'realised_level', 'lambda_value': item['value'],
                'lambda_units': units, 'operator': operator_name, 'n_streams': float(n_lattice),
                'exact_level': np.nan, 'realised_level': cell[key],
                'disagreements_vs_strict': float(np.sum(flag != cell['strict'])),
                'disagreements_vs_weak': float(np.sum(flag != cell['weak'])),
                'count_on_boundary': float(cell['on_boundary']),
                'count_within_ulp_budget': np.nan, 'count_float_above': np.nan,
                'count_float_below': np.nan, 'count_float_equal': np.nan})
    operator_rows.append({
        'record_type': 'ulp_boundary', 'lambda_value': np.nan, 'lambda_units': np.nan,
        'operator': f'|M_float - M_units * 2delta| <= {ULP_BUDGET} ulp',
        'n_streams': float(n_lattice), 'exact_level': np.nan, 'realised_level': np.nan,
        'disagreements_vs_strict': np.nan, 'disagreements_vs_weak': np.nan,
        'count_on_boundary': float(star_cell['on_boundary']),
        'count_within_ulp_budget': float(within_budget), 'count_float_above': float(float_above),
        'count_float_below': float(float_below), 'count_float_equal': float(float_equal)})
    operator_rows.append({
        'record_type': 'operator_delta', 'lambda_value': lambda_star, 'lambda_units': star_units,
        'operator': 'exact weak minus exact strict at lambda*', 'n_streams': np.nan,
        'exact_level': survival[star_units - 1] - survival[star_units], 'realised_level':
            star_cell['level_weak'] - star_cell['level_strict'],
        'disagreements_vs_strict': np.nan, 'disagreements_vs_weak': np.nan,
        'count_on_boundary': np.nan, 'count_within_ulp_budget': np.nan,
        'count_float_above': np.nan, 'count_float_below': np.nan, 'count_float_equal': np.nan})
    operator_levels = pd.DataFrame(operator_rows, columns=OPERATOR_LEVEL_COLUMNS)

    # =================================================================
    # 8. FRAME 4 -- R08_lattice_exact_law.csv (control C2, no v87 value)
    # =================================================================
    r07_lattice = read_round_trip(R07_LATTICE, logger)
    r10_lattice = read_round_trip(R10_LATTICE, logger)
    r07_survival = {int(row.lambda_units): float(row.exact_level)
                    for row in r07_lattice[(r07_lattice['record_type'] == 'exact_survival')
                                           & (r07_lattice['H'] == H)].itertuples(index=False)}
    r07_enumeration = {(int(row.H), int(row.lambda_units)): float(row.enumerated_level)
                       for row in r07_lattice[
                           r07_lattice['record_type'] == 'enumeration_validation'
                       ].itertuples(index=False)}
    r10_pool = r10_lattice[(r10_lattice['record_type'].isin(('enumeration_validation',
                                                             'twin_binding_exact')))
                           & np.isclose(r10_lattice['q'].to_numpy(dtype=float), ENUMERATION_Q,
                                        rtol=0.0, atol=0.0)]
    r10_enumeration = {}
    for row in r10_pool.itertuples(index=False):
        value = row.enumerated_level if row.enumerated_level == row.enumerated_level \
            else row.exact_level
        r10_enumeration.setdefault((int(row.H), int(row.lambda_units)), float(value))
    r10_h5000 = r10_lattice[r10_lattice['H'] == H]

    lattice_rows = []
    for units in LATTICE_SCAN_UNITS:
        mine = survival[units]
        theirs = r07_survival.get(units, float('nan'))
        lattice_rows.append({
            'record_type': 'exact_survival', 'H': H, 'lambda_units': units,
            'lambda_value': units * LATTICE_UNIT, 'q': ENUMERATION_Q, 'exact_level': mine,
            'enumerated_level': np.nan, 'abs_difference': np.nan, 'r07_level': theirs,
            'abs_difference_r07': abs(mine - theirs) if theirs == theirs else np.nan,
            'bit_identical_r07': bool(mine == theirs) if theirs == theirs else np.nan,
            'r10_level': np.nan, 'abs_difference_r10': np.nan, 'bit_identical_r10': np.nan,
            'n_paths': np.nan})
    for horizon in ENUMERATION_HORIZONS:
        for units in ENUMERATION_LAMBDA_UNITS:
            dp_value = lattice_exceedance_exact(horizon, units)
            enumerated = lattice_exceedance_enumerated(horizon, units)
            theirs_07 = r07_enumeration.get((horizon, units), float('nan'))
            theirs_10 = r10_enumeration.get((horizon, units), float('nan'))
            lattice_rows.append({
                'record_type': 'enumeration_validation', 'H': horizon, 'lambda_units': units,
                'lambda_value': units * LATTICE_UNIT, 'q': ENUMERATION_Q,
                'exact_level': dp_value, 'enumerated_level': enumerated,
                'abs_difference': abs(dp_value - enumerated), 'r07_level': theirs_07,
                'abs_difference_r07': (abs(enumerated - theirs_07) if theirs_07 == theirs_07
                                       else np.nan),
                'bit_identical_r07': (bool(enumerated == theirs_07) if theirs_07 == theirs_07
                                      else np.nan),
                'r10_level': theirs_10,
                'abs_difference_r10': (abs(enumerated - theirs_10) if theirs_10 == theirs_10
                                       else np.nan),
                'bit_identical_r10': (bool(enumerated == theirs_10) if theirs_10 == theirs_10
                                      else np.nan),
                'n_paths': float(2 ** horizon)})
    lattice_exact = pd.DataFrame(lattice_rows, columns=LATTICE_EXACT_COLUMNS)

    # =================================================================
    # 9. FRAME 5 -- R08_pairing_diagnostic.csv (C4/C5/C6, no v87 value)
    # =================================================================
    lb_difference = (module_a['lb_biased'].astype(np.float64)
                     - module_a['lb_naive'].astype(np.float64))
    fpr_difference = (module_a['fpr_biased'].astype(np.float64)
                      - module_a['fpr_naive'].astype(np.float64))
    pairing_rows = []
    for index, bias in enumerate(B_GRID):
        reference = naive_reference[bias]
        own_lb = float(module_a['lb_naive'][:, index].mean())
        own_fpr = float(module_a['fpr_naive'][:, index].mean())
        ref_lb = float(reference['lb_reject_rate'])
        ref_fpr = float(reference['fpr_concept'])
        _, _, discordant_lb, rho_lb, deff_lb = mcnemar_paired(module_a['lb_biased'][:, index],
                                                              module_a['lb_naive'][:, index])
        _, _, discordant_fpr, rho_fpr, deff_fpr = mcnemar_paired(
            module_a['fpr_biased'][:, index], module_a['fpr_naive'][:, index])
        pairing_rows.append({
            'record_type': 'per_b', 'b': bias, 'n_trajectories': n_seeds,
            'lb_reject_naive': own_lb, 'fpr_naive': own_fpr,
            'r07_lb_reject_rate': ref_lb, 'r07_fpr_concept': ref_fpr,
            'bit_identical_lb': bool(own_lb == ref_lb), 'bit_identical_fpr':
                bool(own_fpr == ref_fpr),
            'lb_reject_biased': float(module_a['lb_biased'][:, index].mean()),
            'fpr_biased': float(module_a['fpr_biased'][:, index].mean()),
            'delta_lb_pp': float(lb_difference[:, index].mean()),
            'delta_fpr_pp': float(fpr_difference[:, index].mean()),
            'n_discordant_lb': float(discordant_lb), 'n_discordant_fpr': float(discordant_fpr),
            'rho_lb': rho_lb, 'deff_lb': deff_lb, 'rho_fpr': rho_fpr, 'deff_fpr': deff_fpr,
            'statistic': '', 'observed': np.nan, 'tabulated_pvalue': np.nan,
            'null_quantile': np.nan, 'null_p': np.nan, 'ci_low': np.nan, 'ci_high': np.nan,
            'n_resample': np.nan})

    observed_pvalues = adverse_bias['pval_lb'].to_numpy(dtype=float)
    ks_observed = stats.kstest(observed_pvalues, 'uniform')
    n_reference = int(naive_reference[B_GRID[0]]['N_seeds'])
    ks_null = sign_flip_null_ks(rng_for("resample", "c4_ks_null"),
                                module_a['lb_biased'].astype(np.float64),
                                module_a['lb_naive'].astype(np.float64),
                                n_reference, N_RESAMPLE_KS)
    pairing_rows.append(scalar_pairing_row(
        'ks_calibration', 'KS of the six pval_lb against Uniform(0,1)',
        float(ks_observed.statistic), float(ks_observed.pvalue),
        float(np.quantile(ks_null, 1.0 - LB_LEVEL)),
        float(np.mean(ks_null >= float(ks_observed.statistic))), np.nan, np.nan, N_RESAMPLE_KS,
        n_seeds))
    for label, differences in (('lb', lb_difference), ('fpr', fpr_difference)):
        observed_max = float(np.abs(differences.mean(axis=0)).max())
        null_max = sign_flip_null_max(rng_for("resample", f"c4_signflip_{label}"), differences,
                                      N_RESAMPLE_NULL)
        pairing_rows.append(scalar_pairing_row(
            'sign_flip_null_max', f'max |delta_{label}_pp| over the b grid', observed_max,
            np.nan, float(np.quantile(null_max, 1.0 - C4_NULL_LEVEL)),
            float(np.mean(null_max >= observed_max)), np.nan, np.nan, N_RESAMPLE_NULL, n_seeds))
    gap_low, gap_high, _ = bootstrap_max_envelope(rng_for("resample", "c4_bootstrap_gap"),
                                                  lb_difference, N_RESAMPLE_BOOT, BOOT_ALPHA)
    observed_gap = float(np.abs(lb_difference.mean(axis=0)).max())
    pairing_rows.append(scalar_pairing_row(
        'whiteness_bound', 'max |delta_lb_pp| in points, against L311s three-point bound',
        100.0 * observed_gap, np.nan, V87_WHITENESS_BOUND_POINTS, np.nan, 100.0 * gap_low,
        100.0 * gap_high, N_RESAMPLE_BOOT, n_seeds))
    pairing_diagnostic = pd.DataFrame(pairing_rows, columns=PAIRING_COLUMNS)

    return {'adverse_bias': adverse_bias, 'null_law': null_law,
            'operator_levels': operator_levels, 'lattice_exact': lattice_exact,
            'pairing_diagnostic': pairing_diagnostic,
            'module_a': module_a, 'm_float': m_float, 'm_units': m_units,
            'survival': survival, 'grid': grid, 'measured': measured,
            'star_units': star_units, 'lambda_star': lambda_star,
            'roles_exact': roles_exact, 'roles_measured': roles_measured,
            'naive_reference': naive_reference, 'ols_reference': ols_reference,
            'n_seeds': n_seeds, 'n_lattice': n_lattice, 'fast': fast, 'stamp': stamp,
            'family_trigger': family, 'c3_trigger': c3_trigger,
            'within_ulp_budget': within_budget, 'float_above': float_above,
            'float_below': float_below, 'float_equal': float_equal,
            'r10_h5000_rows': int(len(r10_h5000)), 'r07_enumeration': r07_enumeration,
            'r10_enumeration': r10_enumeration, 'degenerate_total': degenerate_total,
            'cost_module_a': cost_a, 'cost_module_b': cost_b}


def bracket_roles(grid, levels):
    """
    Which grid point carries the level immediately above the nominal one and
    which carries the level immediately below it, computed and never read.

    The exceedance level is non-increasing in lambda, so at most one ADJACENT
    pair of grid points straddles the nominal level. `above_nominal` is the
    upper member of that pair and `below_nominal` the lower one; every other
    point carries `none`.
    """
    ordered = sorted(grid, key=lambda item: item['units'])
    roles = {item['units']: 'none' for item in ordered}
    straddling = [index for index in range(len(ordered) - 1)
                  if levels[ordered[index]['units']] > NOMINAL_LEVEL
                  >= levels[ordered[index + 1]['units']]]
    for index in straddling:
        roles[ordered[index]['units']] = 'above_nominal'
        roles[ordered[index + 1]['units']] = 'below_nominal'
    return roles


def scalar_pairing_row(record_type, statistic, observed, tabulated, quantile, null_p, low, high,
                       n_resample, n_trajectories):
    """One grid-level row of the pairing diagnostic, with the per-b cells blank."""
    row = {name: np.nan for name in PAIRING_COLUMNS}
    row['record_type'] = record_type
    row['statistic'] = statistic
    row['n_trajectories'] = n_trajectories
    row['observed'] = observed
    row['tabulated_pvalue'] = tabulated
    row['null_quantile'] = quantile
    row['null_p'] = null_p
    row['ci_low'] = low
    row['ci_high'] = high
    row['n_resample'] = float(n_resample)
    return row


# --- CONTROLS THAT READ THE FINISHED CAMPAIGN ---

def deviation_degree(printed, regenerated, decimals):
    """
    Preamble S3's classification, at v87's OWN printing precision. D3 is never
    assigned here: a qualitative falsification is a judgement the controls make,
    not an arithmetic one.
    """
    if regenerated == printed:
        return 'D0'
    if round(regenerated, decimals) == round(printed, decimals):
        return 'D1'
    return 'D2'


def control_c1_operator_measurement(logger, campaign):
    """
    C1 (a)-(c). What the float comparison implements on the lattice boundary,
    measured on R08's own 2x10^5 fair-coin streams, and the two exact levels at
    lambda* with their difference.

    Deterministic given the streams. The three verdicts below are exhaustive and
    their wording is fixed here, before any of them is selected by the data.
    """
    star_units = campaign['star_units']
    lambda_star = campaign['lambda_star']
    survival = campaign['survival']
    cell = campaign['measured'][star_units]
    n_lattice = campaign['n_lattice']

    logger.info(f"C1 (a) THE ULP BOUNDARY COUNTER, logged even at zero. Over the {n_lattice} "
                f"module-B streams the accumulated float M sits ABOVE its exact lattice value on "
                f"{campaign['float_above']}, BELOW on {campaign['float_below']} and exactly ON "
                f"it on {campaign['float_equal']}. The number of streams whose float M lies "
                f"within {ULP_BUDGET} ulp of its exact lattice point is "
                f"{campaign['within_ulp_budget']}. {cell['on_boundary']} streams have their "
                f"EXACT maximum equal to lambda* = {lambda_star!r} itself, which is the "
                f"configuration the L241 footnote describes.")
    logger.info(f"C1 (b) OPERATOR DISAGREEMENT COUNTS at lambda* = {lambda_star!r} "
                f"({star_units} lattice units) over all {n_lattice} streams. Realised level of "
                f"`float M > lambda*` = {cell['level_float']!r}; of the exact "
                f"`M_units > lambda*` = {cell['level_strict']!r}; of the exact "
                f"`M_units >= lambda*` = {cell['level_weak']!r}. The float test disagrees with "
                f"the STRICT operator on {cell['disagree_strict']} streams and with the WEAK "
                f"operator on {cell['disagree_weak']}.")
    if cell['disagree_weak'] == 0 and cell['disagree_strict'] > 0:
        verdict = (f"the implemented test COINCIDES with the weak operator M >= lambda* on every "
                   f"one of the {n_lattice} streams and differs from the strict one on "
                   f"{cell['disagree_strict']}")
    elif cell['disagree_strict'] == 0 and cell['disagree_weak'] > 0:
        verdict = (f"the implemented test COINCIDES with the strict operator M > lambda* on "
                   f"every one of the {n_lattice} streams")
    elif cell['disagree_strict'] == 0 and cell['disagree_weak'] == 0:
        verdict = ("no stream reached the boundary, so this campaign separates neither operator "
                   "from the other and the statement has no content on it")
    else:
        verdict = (f"the implemented test is a MIXTURE: it differs from the strict operator on "
                   f"{cell['disagree_strict']} streams and from the weak one on "
                   f"{cell['disagree_weak']}")
    gap_exact = survival[star_units - 1] - survival[star_units]
    logger.info(f"C1 (c) THE TWO EXACT LEVELS AT lambda* AND THEIR DIFFERENCE. On the integer "
                f"lattice P(M >= u) = P(M > u - 1), so the weak level at lambda* is the survival "
                f"function one lattice point lower: strict "
                f"{100.0 * survival[star_units]:.4f}% at {star_units} units and weak "
                f"{100.0 * survival[star_units - 1]:.4f}% at {star_units - 1} units, a "
                f"difference of {100.0 * gap_exact:.4f} points -- {100.0 * gap_exact / NOMINAL_LEVEL:.1f}% "
                f"of the nominal level itself. On this evidence {verdict}. v87's L241 footnote "
                f"states that 'the implemented test M_H > lambda* IS the mathematical "
                f"M_H >= lambda*'; what this control measures is whether that holds on R08's own "
                f"apparatus, and the answer is read off the disagreement counts above rather "
                f"than assumed from R10's or R07's.")
    logger.info(f"C1 THE LEVEL DELIVERED. L241's selection rule promises 'the nearest attainable "
                f"level at or below nominal'. The level the implemented operator delivers at "
                f"lambda* is {100.0 * cell['level_float']:.4f}% measured and "
                f"{100.0 * survival[star_units - 1]:.4f}% exactly, against the "
                f"{100.0 * NOMINAL_LEVEL:.1f}% the rule promises to stay at or below.")
    return {'verdict': verdict, 'gap_exact': gap_exact, 'cell': cell}


def control_c2_lattice_concordance(logger, campaign):
    """
    C2. Three streams enumerate the same lattice law and must agree cell by cell.

    C2a -- R08's exact survival at H = 5,000 against R07's, on every unit of the
    scanned region.
    C2b -- R08's path enumeration against R07's and R10's on the cells the three
    streams share. THE PROMPT'S C2 AS WRITTEN IS NOT SATISFIABLE and the
    re-derivation is recorded here: `R10_lattice_exact_law.csv` carries H = 8,000
    and small-H enumerations at q = 1/2, and holds NO H = 5,000 cell, so no level
    at lambda in {11.2, 11.4} can be looked up in it.
    """
    lattice = campaign['lattice_exact']
    surv = lattice[lattice['record_type'] == 'exact_survival']
    compared = surv[surv['bit_identical_r07'].notna()]
    disagreeing = compared[~compared['bit_identical_r07'].astype(bool)]
    logger.info(f"C2a EXACT SURVIVAL AGAINST R07, at H = {H}. {len(compared)} of the "
                f"{len(surv)} scanned lattice points carry an R07 cell; "
                f"{len(compared) - len(disagreeing)} agree BIT FOR BIT and {len(disagreeing)} do "
                f"not. Largest absolute difference "
                f"{float(compared['abs_difference_r07'].max())!r}. Two independently written "
                f"absorbing-chain programs at the same H over the same state space; agreement is "
                f"a statement about the transcription, not about the model. Deterministic; "
                f"trigger probability 0.")
    if len(disagreeing) > 0:
        logger.error(f"C2a FAILED on {len(disagreeing)} lattice point(s): "
                     f"{disagreeing[['lambda_units', 'exact_level', 'r07_level']].to_dict('records')}. "
                     f"A divergence between two exact enumerations of one law is a porting defect "
                     f"in one of the two streams.")
        sys.exit(1)

    logger.info(f"C2 RE-DERIVATION, RECORDED. The prompt asks for the levels at "
                f"lambda in (11.2, 11.4), delta = 0.1, H = {H} to coincide with BOTH "
                f"R07_lattice_exact_law.csv and R10_lattice_exact_law.csv. R10's file carries "
                f"{campaign['r10_h5000_rows']} rows at H = {H}: its own campaign runs at "
                f"H = 8000 (lambda_units 74/75/76) and validates its dynamic program on small-H "
                f"enumerations, so it holds no cell at this horizon and no level at either "
                f"threshold can be looked up in it. The control is therefore split: C2a compares "
                f"the H = {H} law against R07, which has it; C2b compares the path enumeration "
                f"against both streams on the cells all three actually share.")

    enumerated = lattice[lattice['record_type'] == 'enumeration_validation']
    internal = enumerated[enumerated['abs_difference'] != 0.0]
    if len(internal) > 0:
        logger.error(f"C2b FAILED: R08's own dynamic program and its own path enumeration differ "
                     f"on {len(internal)} of {len(enumerated)} cells. The program is not the law "
                     f"of the recursion.")
        sys.exit(1)
    shared = enumerated[enumerated['bit_identical_r07'].notna()
                        & enumerated['bit_identical_r10'].notna()]
    only_r07 = enumerated[enumerated['bit_identical_r07'].notna()
                          & enumerated['bit_identical_r10'].isna()]
    only_r10 = enumerated[enumerated['bit_identical_r10'].notna()
                          & enumerated['bit_identical_r07'].isna()]
    failures = []
    for column, subset in (('bit_identical_r07',
                            enumerated[enumerated['bit_identical_r07'].notna()]),
                           ('bit_identical_r10',
                            enumerated[enumerated['bit_identical_r10'].notna()])):
        bad = subset[~subset[column].astype(bool)]
        if len(bad) > 0:
            failures.append((column, bad[['H', 'lambda_units', 'enumerated_level']]
                             .to_dict('records')))
    logger.info(f"C2b ENUMERATION CONCORDANCE. R08 enumerates all 2^H sign paths at "
                f"H in {ENUMERATION_HORIZONS} and lambda in {ENUMERATION_LAMBDA_UNITS} lattice "
                f"units at q = {ENUMERATION_Q}, and agrees with its own dynamic program to the "
                f"last bit on all {len(enumerated)} cells. Against the other two streams: "
                f"{len(shared)} cells are shared by all THREE (H in (10, 12)) and are the "
                f"assertion; {len(only_r07)} more are shared with R07 alone (H = 8) and "
                f"{len(only_r10)} with R10 alone (H = 14), reported beside them. Deterministic; "
                f"trigger probability 0.")
    if failures:
        logger.error(f"C2b FAILED: {failures}. Three streams enumerating one law must return one "
                     f"number; a divergence is a porting defect in one of the three.")
        sys.exit(1)
    logger.info(f"C2b RESULT: bit-for-bit agreement on every cell any other stream carries -- "
                f"{len(shared)} three-way, {len(only_r07)} with R07 only, {len(only_r10)} with "
                f"R10 only.")


def control_c3_bracketing(logger, campaign):
    """
    C3. The bracketing of the nominal level, computed and never read, on the
    exact law and then required of the measured strict levels.
    """
    roles_exact = campaign['roles_exact']
    roles_measured = campaign['roles_measured']
    grid = campaign['grid']
    survival = campaign['survival']
    expected = {}
    for item in grid:
        if item['units'] == campaign['star_units']:
            expected[item['units']] = 'below_nominal'
        elif item['units'] == campaign['star_units'] - 1:
            expected[item['units']] = 'above_nominal'
        else:
            expected[item['units']] = 'none'
    logger.info(f"C3 BRACKETING ON THE EXACT LAW. Roles computed from the exact survival "
                f"function: {[(item['decimal'], roles_exact[item['units']]) for item in grid]}. "
                f"The pair that straddles {NOMINAL_LEVEL:g} is "
                f"lambda = {(campaign['star_units'] - 1) * LATTICE_UNIT!r} at "
                f"{100.0 * survival[campaign['star_units'] - 1]:.4f}% and "
                f"lambda = {campaign['lambda_star']!r} at "
                f"{100.0 * survival[campaign['star_units']]:.4f}%, and no other adjacent pair of "
                f"the grid does. Deterministic; trigger probability 0.")
    if roles_exact != expected:
        logger.error(f"C3 FAILED on the exact law: roles are {roles_exact}, expected {expected}. "
                     f"L241's bracketing statement is contradicted by the exact law itself.")
        sys.exit(1)
    if roles_measured == roles_exact:
        logger.info(f"C3 BRACKETING ON THE MEASURED STRICT LEVELS: the same roles, "
                    f"{[(item['decimal'], roles_measured[item['units']]) for item in grid]}. The "
                    f"trigger probability of this leg under the exact law was computed before "
                    f"the streams were drawn and is {campaign['c3_trigger']:.4%}.")
    else:
        logger.error(f"C3 MEASURED LEG FIRED. The Monte-Carlo strict levels assign "
                     f"{roles_measured} where the exact law assigns {roles_exact}. Preamble "
                     f"S4.10: no seed, no tolerance and no parameter is touched. The trigger "
                     f"probability of this leg was computed BEFORE the streams were drawn and is "
                     f"{campaign['c3_trigger']:.4%}, which is why it is a reported control and "
                     f"not a gate; the run continues so that the artefacts needed to "
                     f"characterise it exist. The persisted `bracket_role` column carries the "
                     f"EXACT law's roles, which are deterministic.")


def control_c4_whiteness_symmetry(logger, campaign):
    """
    C4. The symmetry of the whiteness loss: L311's three-point bound, which is
    the body's claim and is measurable, and the Figure 8 caption's "identical
    whiteness loss", which is a statement of mechanism and is not.
    """
    pairing = campaign['pairing_diagnostic']
    adverse = campaign['adverse_bias']
    per_b = pairing[pairing['record_type'] == 'per_b']
    pvalues = adverse['pval_lb'].to_numpy(dtype=float)
    rejecting = [(float(adverse['b'].iloc[index]), float(pvalues[index]))
                 for index in range(len(pvalues)) if pvalues[index] < LB_LEVEL]
    logger.info(f"C4 THE SIX PROPORTION p-VALUES on the Ljung-Box arm, reported and not gated: "
                f"{[(float(row.b), float(row_p)) for row, row_p in zip(adverse.itertuples(index=False), pvalues)]}. "
                f"{len(rejecting)} of {len(pvalues)} reject at {LB_LEVEL:g}: {rejecting}. The "
                f"witness campaign had two rejections, 5.9e-05 at b = 0.075 and 0.0243 at "
                f"b = 0.05. A difference in REJECTION COUNT between the two campaigns is not a "
                f"finding on its own -- the family-wise arithmetic logged above gives "
                f"{campaign['family_trigger']:.4%} for at least one rejection under equality "
                f"itself -- and the Figure 8 caption's parenthetical, a |Cov(y_t, y_(t+k))| "
                f"response, is a statement of MECHANISM which is symmetric by construction and "
                f"is not contradicted by a difference in measured rate. Nothing here presents "
                f"'identical' as an established measurement.")
    ks_row = pairing[pairing['record_type'] == 'ks_calibration'].iloc[0]
    logger.info(f"C4 KS CALIBRATION of the six p-values against Uniform(0,1): D = "
                f"{float(ks_row.observed)!r}, tabulated p = {float(ks_row.tabulated_pvalue)!r}. "
                f"THE TABULATED p DOES NOT APPLY: the six p-values are dependent twice over -- "
                f"the six b share the same {campaign['n_seeds']} trajectories, and at each b the "
                f"two arms share the same innovation stream -- and the Kolmogorov distribution "
                f"assumes neither. The null of D is therefore built by sign-flip resampling on "
                f"the trajectory index, one Rademacher sign per trajectory shared across the six "
                f"columns, {int(ks_row.n_resample)} replicates: its "
                f"{1 - LB_LEVEL:.0%} quantile is {float(ks_row.null_quantile)!r} and the observed "
                f"D sits at a null exceedance probability of {float(ks_row.null_p)!r}. "
                f"MEASUREMENT, NOT A GATE (S4bis.8): nothing exits on this number.")
    for row in pairing[pairing['record_type'] == 'sign_flip_null_max'].itertuples(index=False):
        logger.info(f"C4 SIGN-FLIP NULL OF THE MAXIMUM [{row.statistic}]: observed "
                    f"{float(row.observed)!r}, {1 - C4_NULL_LEVEL:.3%} quantile of the null "
                    f"maximum {float(row.null_quantile)!r} on {int(row.n_resample)} replicates, "
                    f"null exceedance probability {float(row.null_p)!r}. The null carries the "
                    f"dependence between the six columns because one sign per trajectory is "
                    f"applied to all of them.")
    bound = pairing[pairing['record_type'] == 'whiteness_bound'].iloc[0]
    observed_points = float(bound.observed)
    worst_index = int(np.argmax(np.abs(per_b['delta_lb_pp'].to_numpy(dtype=float))))
    worst_b = float(per_b['b'].iloc[worst_index])
    respected = observed_points <= V87_WHITENESS_BOUND_POINTS
    excluded = float(bound.ci_low) > V87_WHITENESS_BOUND_POINTS
    logger.info(f"C4 THE THREE-POINT BOUND OF L311, asserted separately and against the "
                f"extremum's own law (S4bis.4). 'The injected-bias arm and the naive arm at "
                f"phi = b reject within three points of each other': the largest "
                f"|delta_lb_pp| over the {len(B_GRID)} values of b is "
                f"{observed_points:.4f} points, attained at b = {worst_b!r}, against the "
                f"{V87_WHITENESS_BOUND_POINTS:g} the sentence states. The bound is "
                f"{'RESPECTED' if respected else 'NOT RESPECTED'}. The 95% bootstrap envelope of "
                f"that MAXIMUM, over {int(bound.n_resample)} resamplings of the trajectory "
                f"index, is [{float(bound.ci_low):.4f}, {float(bound.ci_high):.4f}] points; "
                f"preamble S3 makes a printed bound crossed at D3 only when that interval "
                f"EXCLUDES the bound, and it {'DOES' if excluded else 'does not'}.")
    if not respected:
        logger.error(f"D3 CANDIDATE ON L311. The three-point bound the body states is exceeded "
                     f"by the regenerated campaign: {observed_points:.4f} points against "
                     f"{V87_WHITENESS_BOUND_POINTS:g}, with a 95% envelope of the maximum of "
                     f"[{float(bound.ci_low):.4f}, {float(bound.ci_high):.4f}]. Preamble S3 "
                     f"requires the run to stop reconciling: no parameter, tolerance, seed or "
                     f"bound is moved. The remaining artefacts are produced because the report "
                     f"needs them, and the classification is carried to docs/DEVIATIONS.md and "
                     f"docs/audits/AUDIT_R08.md.")
    return {'observed_points': observed_points, 'worst_b': worst_b, 'respected': respected,
            'ci_low': float(bound.ci_low), 'ci_high': float(bound.ci_high)}


def control_c5_sign_asymmetry(logger, campaign):
    """
    C5. The claim that carries Figure 8 panel B: over-centering makes the sign
    stream negatively autocorrelated and the false-alarm rate FALLS, while
    under-centering makes it positively autocorrelated and the rate RISES. Both
    monotonicities are read on the whole grid, and every local inversion is
    characterised against the paired standard error of the step it inverts.
    """
    module_a = campaign['module_a']
    n_seeds = campaign['n_seeds']
    inversions = []
    for label, tensor, direction in (('fpr_biased', module_a['fpr_biased'], 'non-increasing'),
                                     ('fpr_naive_ref', module_a['fpr_naive'], 'non-decreasing')):
        rates = tensor.astype(np.float64).mean(axis=0)
        for index in range(len(B_GRID) - 1):
            step = tensor[:, index + 1].astype(np.float64) - tensor[:, index].astype(np.float64)
            gap = float(step.mean())
            # The two cells share the same trajectory, so the standard error of
            # their difference is the standard error of the PAIRED difference and
            # never the sum of two independent binomial variances. The unit is
            # the trajectory and the trajectories are keyed on their index alone,
            # so within this statistic deff = 1.0.
            deff = 1.0
            se = float(np.sqrt(deff * np.var(step, ddof=1) / n_seeds))
            wrong_way = gap > 0.0 if direction == 'non-increasing' else gap < 0.0
            if wrong_way:
                inversions.append((label, float(B_GRID[index]), float(B_GRID[index + 1]), gap, se,
                                   gap / se if se > 0.0 else float('nan')))
        logger.info(f"C5 [{label}] over the b grid: {np.array2string(rates, precision=6)}, "
                    f"required {direction} in b. This is the qualitative content of L311 and of "
                    f"the Figure 8 panel B caption; both directions are read on the whole grid.")
    if not inversions:
        logger.info(f"C5 RESULT: no local inversion on either arm, over the "
                    f"{2 * (len(B_GRID) - 1)} consecutive steps of the grid.")
    else:
        material = [item for item in inversions if abs(item[5]) > 2.0]
        logger.info(f"C5 RESULT: {len(inversions)} local inversion(s), of which {len(material)} "
                    f"beyond two paired standard errors. Each is CHARACTERISED and none is "
                    f"corrected (S4.10).")
        for label, left, right, gap, se, z_value in inversions:
            logger.info(f"C5 inversion [{label}] between b = {left!r} and b = {right!r}: paired "
                        f"difference {gap:+.6f} with paired standard error {se:.6f} "
                        f"(z = {z_value:+.3f}) on {n_seeds} shared trajectories.")
    return inversions


def control_c6_cross_stream_identity(logger, campaign):
    """
    C6. The degenerate witness, upgraded to an EXACT cross-stream identity.

    `generate_dgp` draws z, h and eps without ever referencing phi, and R07 keys
    every trajectory on ("trajectory", i) as this module does. Therefore R08's
    b = 0 arm IS R07's OLS-250 arm at phi = 0, and R08's pairing diagnostic at
    phi = b IS R07's NAIVE arm at phi = b -- by construction, not by
    coincidence. Control C7's normalized-AST leg is what licenses the word
    "therefore". A failure here is a cross-stream PORT DEFECT to characterise
    and report, never something to reconcile by adjusting either side.
    """
    if campaign['fast']:
        logger.info(f"C6 NOT ASSERTED IN --fast MODE, and the reason is stated rather than "
                    f"silent: the identity is between RATES measured on {N_SEEDS} trajectories "
                    f"and this run measures {campaign['n_seeds']}. The artefacts of this run are "
                    f"stamped `{campaign['stamp']}` and certify no v87 value (S4.3).")
        return None
    pairing = campaign['pairing_diagnostic']
    per_b = pairing[pairing['record_type'] == 'per_b']
    failures = []
    for row in per_b.itertuples(index=False):
        if not bool(row.bit_identical_lb):
            failures.append(('lb', float(row.b), float(row.lb_reject_naive),
                             float(row.r07_lb_reject_rate)))
        if not bool(row.bit_identical_fpr):
            failures.append(('fpr', float(row.b), float(row.fpr_naive),
                             float(row.r07_fpr_concept)))
    adverse = campaign['adverse_bias']
    zero_row = adverse[np.isclose(adverse['b'].to_numpy(dtype=float), 0.0, rtol=0.0,
                                  atol=0.0)].iloc[0]
    reference = campaign['ols_reference']
    identical_lb = float(zero_row['lb_reject_biased']) == float(reference['lb_reject_rate'])
    identical_fpr = float(zero_row['fpr_biased']) == float(reference['fpr_concept'])
    if not identical_lb:
        failures.append(('b0_lb', 0.0, float(zero_row['lb_reject_biased']),
                         float(reference['lb_reject_rate'])))
    if not identical_fpr:
        failures.append(('b0_fpr', 0.0, float(zero_row['fpr_biased']),
                         float(reference['fpr_concept'])))
    logger.info(f"C6 CROSS-STREAM IDENTITY, DECLARED. Module A's pairing diagnostic keys on "
                f"R07's namespace -- seed_sequence_for('trajectory', i) -- deliberately; every "
                f"other draw in R08 keys on R08's own ('lattice_stream', index). An unexplained "
                f"reuse would read as an entropy collision, so it is declared here and in "
                f"docs/audits/AUDIT_R08.md. The identity is EXACT and its trigger probability is "
                f"0: `generate_dgp` draws z, h and eps without reference to phi, only "
                f"r[t] = phi r[t-1] + eps[t] uses it, and control C7's normalized-AST leg "
                f"establishes that R07's copy of `generate_dgp` and "
                f"`compute_phi_hat_vectorized` compile the same instructions as the R08 witness's.")
    logger.info(f"C6 RESULT: R08's b = 0 arm against R07's OLS-250 at phi = 0 -- Ljung-Box "
                f"{float(zero_row['lb_reject_biased'])!r} vs {float(reference['lb_reject_rate'])!r} "
                f"(bit-identical {identical_lb}), FPR {float(zero_row['fpr_biased'])!r} vs "
                f"{float(reference['fpr_concept'])!r} (bit-identical {identical_fpr}). The "
                f"pairing diagnostic against R07's NAIVE arm: "
                f"{int(per_b['bit_identical_lb'].astype(bool).sum())}/{len(per_b)} bit-identical "
                f"on Ljung-Box and "
                f"{int(per_b['bit_identical_fpr'].astype(bool).sum())}/{len(per_b)} on FPR.")
    if failures:
        logger.error(f"C6 FAILED on {len(failures)} cell(s): {failures}. This is a CROSS-STREAM "
                     f"PORT DEFECT -- two files that compile the same instructions on the same "
                     f"entropy key returned different numbers -- and preamble S4.10 forbids "
                     f"reconciling it by adjusting either side. It is characterised here and in "
                     f"docs/audits/AUDIT_R08.md.")
        sys.exit(1)

    # The level question the prompt poses, answered against BOTH operators.
    survival = campaign['survival']
    star_units = campaign['star_units']
    n_seeds = campaign['n_seeds']
    fpr_zero = float(zero_row['fpr_biased'])
    readings = []
    for name, level_value in (('strict M > lambda*', survival[star_units]),
                              ('weak M >= lambda*', survival[star_units - 1])):
        # deff = 1.0: the trajectories entering this single cell are keyed on
        # their index alone and share nothing, so the cell is i.i.d. binomial.
        deff = 1.0
        se = float(np.sqrt(deff * level_value * (1.0 - level_value) / n_seeds))
        readings.append((name, level_value, (fpr_zero - level_value) / se, se))
    lands_on = min(readings, key=lambda item: abs(item[2]))
    logger.info(f"C6 THE LEVEL THE b = 0 CELL LANDS ON. Its false-alarm rate is {fpr_zero!r} on "
                f"{n_seeds} trajectories. Against the two exact levels at "
                f"lambda* = {campaign['lambda_star']!r}: "
                + "; ".join(f"{name} = {100.0 * value:.4f}% -> z = {z_value:+.2f} "
                            f"(SE {se:.6f})" for name, value, z_value, se in readings)
                + f". It lands on the {lands_on[0]} level. The prompt's C6 expected both "
                f"witness values, 0.0546 and 0.0535, to cover the attainable "
                f"{100.0 * survival[star_units]:.2f}% and observed that they do not; the reason "
                f"is not a threshold error but an OPERATOR difference, and control C1 -- not "
                f"this assertion -- is what settles it: module A compares the raw accumulated "
                f"float against lambda* and therefore delivers the WEAK level, while the "
                f"delivered module B rounds to six decimals before comparing and therefore "
                f"reports the STRICT one. lambda* itself is {campaign['lambda_star']!r} on both "
                f"paths, and the witness log records lambda_star = 11.400000 for the delivered "
                f"campaign as well.")
    return {'fpr_zero': fpr_zero, 'readings': readings, 'lands_on': lands_on[0]}


def report_residual_momentum_trace(logger, campaign):
    """
    The trace of the two L311 quantities R08 does not own, reported and never
    macro-ised (prompt section 2.3 and section 4).
    """
    diagnostics = read_round_trip(R07_DIAGNOSTICS, logger)
    bias_column = diagnostics['bias_phi_hat'].abs()
    largest = float(bias_column.max())
    worst = diagnostics.iloc[int(bias_column.to_numpy().argmax())]
    eta_max = float(diagnostics['eta_rmse_over_sigma'].max())
    logger.info(f"THE CONSTANT 2.5 OF L311 HAS A SOURCE, AND IT IS v87's OWN. L311 writes 'its "
                f"bias leaves a residual momentum +2.5 phi/n > 0'; L308 of the same manuscript "
                f"prints 'the classical small-sample AR bias E[phi_hat] - phi ~ -2.5 phi / n, "
                f"stays under 2.9e-3'. The constant is therefore not orphaned: it is the "
                f"coefficient of the standard first-order bias expansion of the AR(1) "
                f"least-squares estimator, and the manuscript states it at L308. R07 owns that "
                f"sentence: it carries the constant as V87_BIAS_BOUND, classifies it in "
                f"`classify_bias_bound`, registers docs/DEVIATIONS.md "
                f"`R07-bias-bound-not-a-bound` and files "
                f"docs/camera_ready_candidates/R07_v87_bias_bound.md. R08 states the trace and "
                f"emits NO macro for 2.5.")
    logger.info(f"'SEVEN TIMES THE LARGEST WE MEASURE' HAS ITS DENOMINATOR IN R07, NOT HERE. The "
                f"ratio is {V87_RESIDUAL_MOMENTUM} over the largest residual momentum measured, "
                f"and R07_estmean_diagnostics.csv is where that maximum lives: the largest "
                f"|E[phi_hat] - phi| over R07's {len(diagnostics)} diagnostic cells is "
                f"{largest!r}, attained at phi = {float(worst['phi'])!r}, "
                f"n_ols = {int(worst['n_ols'])}, giving a ratio of "
                f"{V87_RESIDUAL_MOMENTUM / largest:.2f}. Against the 2.9e-3 v87 itself prints as "
                f"the bound, the ratio is {V87_RESIDUAL_MOMENTUM / 2.9e-3:.2f}. The largest "
                f"eta_rmse_over_sigma over the same file is {eta_max!r}. R08 emits NO macro for "
                f"any of these three quantities: R07 holds the denominator and preamble S4's "
                f"perimeter filter keeps one cell behind one published number.")
    logger.info(f"THE PENALTY AT A RESIDUAL MOMENTUM OF {V87_RESIDUAL_MOMENTUM} IS ALSO R07's "
                f"CELL. L311's 'the under-centering penalty is still only "
                f"{V87_PENALTY_POINTS} points of false-alarm rate' is the difference between the "
                f"naive arm at phi = 0.02 and at phi = 0 in "
                f"R07_estmean_lb_fpr.csv: "
                f"{float(campaign['naive_reference'][0.02]['fpr_concept'])!r} - "
                f"{float(campaign['naive_reference'][0.00]['fpr_concept'])!r} = "
                f"{100.0 * (float(campaign['naive_reference'][0.02]['fpr_concept']) - float(campaign['naive_reference'][0.00]['fpr_concept'])):.4f} "
                f"points. \\REightPenaltyAtResidualMomentum is emitted from those two cells and "
                f"says so in the .tex comment block; the movement of the cells themselves is "
                f"already registered as `R07-campaign-redraw` and R08 opens no duplicate entry.")


def report_deviation_table(logger, campaign, c4_result):
    """The D0-D3 table, with the source CSV cell of every value (preamble S3)."""
    adverse = campaign['adverse_bias']
    null_law = campaign['null_law']
    star_units = campaign['star_units']
    collapse = float(adverse['fpr_biased'].iloc[len(B_GRID) - 1])
    inflate = float(adverse['fpr_naive_ref'].iloc[len(B_GRID) - 1])
    above = float(null_law[null_law['lambda_units'] == star_units - 1]['P_exceed_strict'].iloc[0])
    below = float(null_law[null_law['lambda_units'] == star_units]['P_exceed_strict'].iloc[0])
    penalty = 100.0 * (float(campaign['naive_reference'][0.02]['fpr_concept'])
                       - float(campaign['naive_reference'][0.00]['fpr_concept']))
    rates = np.concatenate([adverse['lb_reject_biased'].to_numpy(dtype=float),
                            adverse['lb_reject_naive_ref'].to_numpy(dtype=float)])
    rows = [
        ('Fig. 8 (B) FPR collapses to', V87_FPR_COLLAPSE, collapse, 4,
         f'R08_adverse_bias{campaign["stamp"]}.csv, b=0.15, fpr_biased'),
        ('Fig. 8 (B) / L311 FPR inflates to', V87_FPR_INFLATE, inflate, 3,
         'R07_estmean_lb_fpr.csv, NAIVE, phi=0.15, fpr_concept'),
        ('L241 level above nominal (lambda=11.2)', V87_LEVEL_ABOVE, above, 4,
         f'R08_null_law_lattice{campaign["stamp"]}.csv, lambda=11.2, P_exceed_strict'),
        ('L241 level below nominal (lambda=11.4)', V87_LEVEL_BELOW, below, 4,
         f'R08_null_law_lattice{campaign["stamp"]}.csv, lambda=11.4, P_exceed_strict'),
        ('L241 lambda*', V87_LAMBDA_STAR, campaign['lambda_star'], 1,
         f'R08_null_law_lattice{campaign["stamp"]}.csv, bracket_role=below_nominal'),
        ('L311 whiteness gap bound (points)', V87_WHITENESS_BOUND_POINTS,
         c4_result['observed_points'], 1,
         f'R08_pairing_diagnostic{campaign["stamp"]}.csv, whiteness_bound'),
        ('L311 penalty at residual momentum 0.02 (points)', V87_PENALTY_POINTS, penalty, 1,
         'R07_estmean_lb_fpr.csv, NAIVE, phi in (0, 0.02), fpr_concept'),
        ('L311 whiteness range, low end', 0.05, float(rates.min()), 2,
         f'R08_adverse_bias{campaign["stamp"]}.csv, min over both arms of the rejection rate'),
        ('L311 whiteness range, high end', 1.00, float(rates.max()), 2,
         f'R08_adverse_bias{campaign["stamp"]}.csv, max over both arms of the rejection rate'),
    ]
    logger.info("D0-D3 CLASSIFICATION AGAINST v87, AT THE MANUSCRIPT'S OWN PRINTING PRECISION")
    for site, printed, regenerated, decimals, cell in rows:
        logger.info(f"  {deviation_degree(printed, regenerated, decimals)} | {site}: v87 prints "
                    f"{printed!r}, regenerated {regenerated!r} (rounds to "
                    f"{round(regenerated, decimals)!r}) | source cell: {cell}")


# --- MAIN ---

def main():
    parser = argparse.ArgumentParser(
        description="R08 (a) -- the adverse direction and the discrete null law (v87 Figure 8)")
    parser.add_argument("--n-jobs", type=int, default=os.cpu_count(),
                        help="Worker processes. Every task is keyed on its role and index alone "
                             "and the chunk boundaries are fixed constants, so the output is "
                             "independent of this value: that is the second reproducibility axis "
                             "of control C8.")
    parser.add_argument("--fast", action="store_true",
                        help="Degraded path, explicitly selected and STAMPED (S4.3): 200 "
                             "trajectories and 5,000 lattice streams, every artefact written "
                             "under a _fast name. It certifies no v87 value.")
    args = parser.parse_args()

    RESULTS_DIR = BASE_DIR / "results" / "R08_adverse_lattice"
    DATA_DIR = RESULTS_DIR / "data"
    FIGURES_DIR = RESULTS_DIR / "figures"
    TABLES_DIR = RESULTS_DIR / "tables"
    LOGS_DIR = BASE_DIR / "logs" / "R08_adverse_lattice"
    for directory in (DATA_DIR, FIGURES_DIR, TABLES_DIR, LOGS_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(LOGS_DIR / "exp_R08_adverse_lattice_a.log", "exp_R08_adverse_lattice_a")
    if not verify_hash_seed(logger):
        sys.exit(1)
    log_environment(logger, ["numpy", "pandas", "scipy", "statsmodels", "matplotlib", "pytest"])
    t0 = time.time()

    logger.info("R08 (a) measures the two qualifications of v87's exactness claim: L311 and "
                "Figure 8 panels A-B, where an injected centring bias moves the false-alarm rate "
                "in both directions according to its sign at identical whiteness loss; and L241 "
                "and Figure 8 panel C, where the statistic lives on a 2delta lattice and the "
                "attainable levels are discrete.")
    logger.info(f"Worker processes requested: {args.n_jobs}. Every task of this stream is keyed "
                f"on its role and index alone and the chunk boundaries are fixed constants, so "
                f"this value cannot move a number.")
    logger.info("THE STATUS OF THE SECOND DELIVERED LOG (prompt section 0bis). The R08 prompt "
                "reports Priorite_21c_plot_adverse_lattice.py as reputed never to have been "
                "executed in this project, and asks for a verdict rather than an assumption. The "
                "verdict is established by digest and by timestamp in docs/audits/AUDIT_R08.md "
                "section 2 and is reproduced here: the two MD5 digests the delivered log prints "
                "are the digests of the two delivered CSVs, the two SHA-256 digests "
                "Priorite_21b's own log prints are the digests of the same two files, and the "
                "timestamps are consistent (21b ends 07:23:57, 21c runs 07:25:37 on the same "
                "day). The log corresponds to the delivered script and to the delivered CSVs.")

    control_c7_source_identity(logger)
    control_c1_operator_identity(logger)

    campaign = run_campaign(logger, args.n_jobs, args.fast)

    control_c1_operator_measurement(logger, campaign)
    control_c2_lattice_concordance(logger, campaign)
    control_c3_bracketing(logger, campaign)
    c4_result = control_c4_whiteness_symmetry(logger, campaign)
    control_c5_sign_asymmetry(logger, campaign)
    control_c6_cross_stream_identity(logger, campaign)
    report_residual_momentum_trace(logger, campaign)
    report_deviation_table(logger, campaign, c4_result)

    stamp = campaign['stamp']
    artefacts = {
        f"R08_adverse_bias{stamp}.csv": campaign['adverse_bias'],
        f"R08_null_law_lattice{stamp}.csv": campaign['null_law'],
        f"R08_operator_levels{stamp}.csv": campaign['operator_levels'],
        f"R08_lattice_exact_law{stamp}.csv": campaign['lattice_exact'],
        f"R08_pairing_diagnostic{stamp}.csv": campaign['pairing_diagnostic'],
    }
    for name, frame in artefacts.items():
        save_fair_csv(frame, DATA_DIR / name)
        logger.info(f"{name}: {len(frame)} rows, {len(frame.columns)} columns.")
    for name in artefacts:
        logger.info(f"SHA-256 {name:<34} : {compute_sha256(DATA_DIR / name)}")

    logger.info(f"Execution completed in {time.time() - t0:.1f}s with {args.n_jobs} workers "
                f"(module A {campaign['cost_module_a']:.1f}s, module B "
                f"{campaign['cost_module_b']:.1f}s). Control C8's second axis is a rerun at a "
                f"different worker count: every task is keyed on its role and index alone and "
                f"the chunk boundaries are fixed constants, so the artefacts must be "
                f"byte-identical.")


if __name__ == "__main__":
    main()
