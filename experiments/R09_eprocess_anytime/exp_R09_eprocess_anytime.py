#!/usr/bin/env python3
"""
==========================================================================
R09 -- ANYTIME-VALID DETECTION ON THE FAIR-COIN STREAM (v87 Figure 9, L243)
==========================================================================
v87 L243 and Figure 9 (`fig:anytime`, L559) claim that a sign-CUSUM calibrated
to 5% at H = 5,000 sees its realized false-alarm rate climb to 18% when the
monitoring continues to 4H, while a mixture martingale (MIX) stays at or below
alpha under the same monitoring, and that e-CUSUM satisfies ARL0 >= 1/alpha.
This script ports the submitted campaign -- `Priorite_22_eprocess_anytime.py`,
which writes `protocol_22a`-`protocol_22d` -- into the repository's FAIR harness
and classifies every published numeral D0-D3.

WHAT v87 PRINTS, AND WHERE EACH NUMBER LIVES.

  L243, L559  CUSUM peeking FPR `18\\%`
                             -> R09_validity_stopping, CUSUM / 0.05 / peeking / FPR
  L243, L559  MIX "remains bounded by alpha"
                             -> R09_validity_stopping, MIX / peeking, 7 rows
  L243        CUSUM "calibrated to 5\\% at H = 5,000"
                             -> R09_level_granularity, CUSUM / 0.05 / achieved_level
  L243        `409` vs `539` steps at eta = 0.10
                             -> R09_eprocess_race, MIX/CUSUM, alpha = 0.05, eta = 0.10, ADD
  L559        "MIX matches CUSUM speed for moderate drifts (eta <= 0.10)"
                             -> R09_eprocess_race, alpha = 0.05
  L559        "e-CUSUM satisfies ARL0 >= 1/alpha"
                             -> R09_arl0, eCUSUM, 7 rows
  L559        "Only MIX controls the time-uniform false-alarm probability"
                             -> R09_validity_stopping, peeking, 3 arms
  L243, L559  `2x10^4` streams   -> N_NULL

THE ONE SUBSTANTIVE READABILITY PROBLEM OF THE STREAM. `protocol_22d`'s
`ARL0_mean` for CUSUM and MIX is a HORIZON ARTEFACT, not a measurement.
Right-censoring runs at 65.4%-95.8% (CUSUM) and 90.5%-99.1% (MIX) in the
submitted campaign, so both means converge mechanically on the simulation
horizon T_EXT = 20,000. The published caption names ONLY e-CUSUM in panel C,
whose censoring is 0 at six of seven levels, so no printed claim is falsified.
The task is to make the censoring legible in the artefacts, not to correct a
claim: no ARL0 is persisted, plotted or macro-emitted without `censored_frac` on
the same row (C1), panel C marks the censored arms hollow, and the macro emitter
refuses any ARL0-derived macro above 50% censoring.

SEVEN STRUCTURAL CHANGES AGAINST THE DELIVERED SCRIPT, EACH FORCED BY THE
PREAMBLE.

1. IMPORT SAFETY. `Priorite_22` calls `setup_logging(...)` and
   `log_requirements()` at MODULE level with `mode='w'`. Every side effect moves
   inside `main()` under `if __name__ == "__main__"`; the chunk workers stay pure
   module-level functions with no logging.
2. ENTROPY. `master_seed = 42027` plus a `SeedSequence.spawn` tree is replaced by
   the repository's canonical `get_deterministic_seed` / `seed_sequence_for` /
   `rng_for`, keyed on ROLE AND INDEX ONLY -- never on alpha or eta. This redraws
   the campaign and is pre-classified Class A / D2 by the `R05-campaign-redraw`,
   `R11-regenerated`, `R13-campaign-redraw` and `R07-campaign-redraw`
   precedents.
3. COMMON RANDOM NUMBERS, MADE STRUCTURAL. Every Bernoulli draw becomes
   `y_t = (rng.random(size) < p)` instead of `rng.binomial(1, p, size)`: with a
   threshold on a shared uniform, two eta values consume the IDENTICAL uniform
   stream and differ only where the threshold moves. `Generator.binomial`'s
   consumption pattern for n = 1 is an implementation detail that must not be
   relied upon. Exact Bernoulli either way; a deliberate change of draw
   mechanism, logged as such.
4. `--fast` IS DROPPED. It is a second, unstamped parameter set reachable by a
   flag, and the repository certifies one configuration. `--n-jobs` and
   `--control-arms` are the only arguments, and NUM_CHUNKS stays fixed at 10 so
   the chunk decomposition -- and therefore every output -- is independent of
   `n_jobs`.
5. THE e-CUSUM H1 ARM IS COMPUTED AND PERSISTED OUTSIDE THE PUBLISHED PATH.
   v87 draws panel B with two curves and its caption names only CUSUM and MIX.
   A monotone delay response to eta is nevertheless the positive control that
   separates a slow detector from a blind one, so the arm runs under an explicit
   `--control-arms ecusum` and lands in
   `R09_eprocess_race_control_ecusum.csv`, whose filename AND `arm` column stamp
   the branch (S4.3). It consumes no additional randomness, so a run WITHOUT the
   flag produces byte-identical published CSVs.
6. THREE HARD-CODED LITERAL GATES ARE REMOVED AS GATES. `Priorite_22:619`
   (`|FPR - 0.1801| > 1e-9`), `:631` (`|ADD - 409.1131405377981| > 1e-9` and
   `|ADD - 538.8051546391753| > 1e-9`) are self-anchored equality tests at
   machine precision on Monte-Carlo values, which S7 forbids; the delivered
   `if fpr > a + 0.005` in M1(ii) has a tolerance derived from nothing. All three
   become DEVIATION CLASSIFICATION against the witness CSVs, read with
   `float_precision='round_trip'`.
7. THE CONTROLS ARE REDESIGNED PER S4bis, NOT WEAKENED. The martingale bound is
   one one-sided Kolmogorov statistic with an exact null instead of seven binary
   gates whose family-wise trigger probability is 30.2%; the positive control is
   a one-sided Spearman with its exact permutation null instead of nine adjacent
   comparisons; the calibration coherence gate carries the variance of the
   ESTIMATED threshold, `alpha(1-alpha)(1/N_NULL + 1/N_CAL)`, which the delivered
   `(b)` and `(e)` both ignore.

References:
- Ville, J. (1939). Etude critique de la notion de collectif. Gauthier-Villars.
- Ramdas, A., Grunwald, P., Vovk, V. & Shafer, G. (2023). Game-theoretic
  statistics and safe anytime-valid inference. Statistical Science, 38(4).
- Page, E. S. (1954). Continuous inspection schemes. Biometrika, 41, 100-115.
- Wilson, E. B. (1927). Probable inference, the law of succession, and
  statistical inference. JASA, 22(158), 209-212.
- Kish, L. (1965). Survey Sampling. Wiley. (design effect)
- Birnbaum, Z. W. & Tingey, F. H. (1951). One-sided confidence contours for
  probability distribution functions. Annals of Mathematical Statistics, 22(4).

NOTATION (prompt section 6)
  alpha            nominal false-alarm level
  eta              drift in the Bernoulli rate under H1
  H                nominal calibration horizon; peeking is over [1, 4H]
  TAU              change point of the H1 stream
  T_EXT            simulation horizon, 4H
  ARL0             average run length under H0
  censored_frac    fraction of runs right-censored at the simulation horizon
  MIX              mixture martingale; eCUSUM -- e-process CUSUM
  ADD              average detection delay, CONDITIONAL on an alarm in (TAU, H]
  D+               one-sided Kolmogorov statistic sup_x (F_n(x) - x)
==========================================================================
"""

import sys
from pathlib import Path

# Determinism bootstrap, in the order preamble S6/S7 requires: fair_env imports
# only os and sys, so the environment block is posted before NumPy is loaded by
# anyone and before any BLAS thread limit is read. PYTHONHASHSEED cannot be set
# from here -- CPython reads it at interpreter start-up -- so it is exported by
# run_experiment_R09.sh and verified twice below.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from experiments.common.fair_env import enforce_strict_determinism, verify_hash_seed, log_environment

enforce_strict_determinism()

import os

if os.environ.get("PYTHONHASHSEED") != "42":
    sys.exit("FATAL: PYTHONHASHSEED is not 42. Execute via run_experiment_R09.sh")

import numpy as np
import pandas as pd
from experiments.common.fair_harness import (setup_logging, disable_pandas_multithreading,
                                             compute_sha256, save_fair_csv, log_artifact_manifest)

disable_pandas_multithreading()

import ast
import math
import time
import hashlib
import argparse
import tempfile
import itertools
from scipy import stats
from scipy.special import logsumexp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

# --- PROTOCOL SPECIFICATION, IMPERATIVE, CARRIED VERBATIM FROM THE WITNESS ---
# Every constant below is traced to its defining line in
# data/reference/R09/Priorite_22_eprocess_anytime.py and is unchanged in value.
H = 5000                                                            # witness l.138
TAU = 2500                                                          # witness l.139
ALPHAS = [0.10, 0.07, 0.05, 0.035, 0.025, 0.015, 0.01]              # witness l.140
ETAS = [0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20]  # witness l.141
DELTA_CUSUM = 0.1                                                   # witness l.142
ETA0_MIX_GRID = [0.05, 0.10, 0.15]                                  # witness l.143
ETA0_ECUSUM = 0.10                                                  # witness l.144
SIDES = [1, -1]                                                     # witness l.145
N_CAL, N_NULL, N_ALT = 50000, 20000, 2000                           # witness l.152
START_GRID_SIZE = 16                                                # witness l.153
T_EXT_MULT = 4                                                      # witness l.154
NUM_CHUNKS = 10                                                     # witness l.162

T_EXT = T_EXT_MULT * H
START_GRID = np.linspace(0, H - 1, START_GRID_SIZE, dtype=int)
C_MIX = len(START_GRID) * len(ETA0_MIX_GRID) * len(SIDES)
MIX_W = 1.0 / C_MIX
# M1(i) draws this many increments of the mixture kernel (witness l.203).
M1_EXPECTATION_STEPS = 2000000

# The published arms of panel B. v87's Figure 9 caption names CUSUM and MIX and
# nothing else there; `simulate_h1` returns keys for those two alone. e-CUSUM
# appears in panel C's caption only. The R09 prompt's section 5 C4 transposes
# panel C's three arms onto panel B; that is a specification defect of the
# prompt and is recorded in AUDIT_R09.md rather than silently repaired.
PUBLISHED_H1_ARMS = ("CUSUM", "MIX")
CONTROL_H1_ARM = "eCUSUM"
ARMS_H0 = ("CUSUM", "MIX", "eCUSUM")
# The three stopping protocols of panel A (witness l.537). `extended` is the
# CROSSING STATE at exactly t = T_EXT, not a cumulative probability.
STOPPING_PROTOCOLS = (("nominal", H, False), ("extended", T_EXT, True), ("peeking", T_EXT, False))
# The figure's operating point, which is the alpha v87's panel A and panel B use.
FIGURE_ALPHA = 0.05
FIGURE_ETA = 0.10

MACRO_HEADER = "% Auto-generated by exp_R09_eprocess_anytime.py -- do not edit."
# Section 2.3 of the R09 prompt, enforced in code rather than by convention.
MACRO_CENSORING_CEILING = 0.5

# --- STATISTICAL CONTROL DESIGN, FIXED BEFORE THE FIRST RUN (S4bis, S4.10) ---
# C3 gates on one one-sided Kolmogorov statistic at this level; C4 gates on one
# one-sided Spearman per arm at the same level. Both nulls are exact.
GATE_LEVEL = 0.01
# The calibration-coherence gate that replaces the delivered controls (b) and
# (e). Its two-sided level is fixed here and its tolerance is DERIVED from
# alpha(1-alpha)(1/N_NULL + 1/N_CAL) at run time -- never from an observed gap.
COHERENCE_LEVEL = 0.001
# M1(i) certifies E[lambda_t] = 1. lambda_t = 1 +/- 2*side*eta0 with side
# symmetric, so Var(lambda_t) = 4*E[eta0^2] = 4*(0.05^2+0.10^2+0.15^2)/3 and the
# standard error over 2e6 draws is 1.53e-4. The delivered tolerance 3e-3 is
# therefore 19.6 standard errors; it is kept because it is derived, and its
# exact trigger probability is logged below.
M1_EXPECTATION_TOL = 3e-3
# C4's paired bootstrap over the N_ALT trajectory indices.
C4_BOOTSTRAP_REPLICATES = 2000
C4_BOOTSTRAP_LEVEL = 0.05
# The etas at which the halt condition of the plan's section 10 is evaluated.
C4_HALT_ETAS = (0.02, 0.04)

# --- SOURCE-SEGMENT IDENTITY (control C5) ---
# Preamble S4.2 forbids hoisting a scientific primitive into
# experiments/common/, so the routines below are duplicated from the file that
# owns them and checked against that file at RUN TIME: the duplication is
# deliberate and it cannot drift.
WITNESS_SOURCE = BASE_DIR / "data" / "reference" / "R09" / "Priorite_22_eprocess_anytime.py"
WITNESS_CSV = {
    "validity_stopping": "protocol_22a_validity_stopping.csv",
    "eprocess_race": "protocol_22b_eprocess_race.csv",
    "level_granularity": "protocol_22c_level_granularity.csv",
    "arl0": "protocol_22d_arl0.csv",
}
# Byte-identical carry, asserted.
CARRIED_PRIMITIVES = ("wilson_ci",)
# Adapted routines: each takes an injected generator, drops the module globals
# the witness reads, or replaces `rng.binomial` by a thresholded uniform, so byte
# identity is not assertable on them. R13's treatment applies -- the witness
# source of each is quoted in full in the log with its SHA-256.
ADAPTED_ROUTINES = ("_process_m1_chunk", "_process_h0_chunk", "calibrate_cusum",
                    "simulate_h1", "run_m1_certificate")
# STATEMENT-LEVEL IDENTITY, which is what actually catches a transcription
# error. Each entry is (witness function, assignment target); the exact source
# text of every assignment to that target inside that function must appear
# VERBATIM in this file's own source.
CARRIED_STATEMENTS = (
    ("_process_h0_chunk", "dev"),
    ("_process_h0_chunk", "S_pos"),
    ("_process_h0_chunk", "S_neg"),
    ("_process_h0_chunk", "M_cusum"),
    ("_process_h0_chunk", "active_idx"),
    ("_process_h0_chunk", "inc_mix"),
    ("_process_h0_chunk", "logM_mix"),
    ("_process_h0_chunk", "logE_mix"),
    ("_process_h0_chunk", "ip"),
    ("_process_h0_chunk", "im"),
    ("_process_h0_chunk", "logMp"),
    ("_process_h0_chunk", "logMm"),
    ("_process_h0_chunk", "M_ecusum"),
    ("simulate_h0", "log_inc_1"),
    ("simulate_h0", "log_inc_0"),
    ("simulate_h0", "inc_p_1"),
    ("simulate_h0", "inc_p_0"),
    ("simulate_h0", "inc_m_1"),
    ("simulate_h0", "inc_m_0"),
    ("calibrate_cusum", "l_star"),
)


# --- PRIMITIVE CARRIED FROM THE FILE THAT OWNS IT ---
# Do not reformat. Byte identity is checked on the exact source text at
# start-up, trailing whitespace included.

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


# --- SEED DERIVATION (SPECS 1.2), CARRIED FROM exp_R13_oracle_ceiling_a.py ---

def get_deterministic_seed(*args) -> int:
    """
    Derives a 128-bit collision-free seed from the semantic coordinates of a
    task, returned as a scalar integer so no entropy is discarded. This is the
    repository's canonical form, carried from exp_R11_multi_detector.py.

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


# --- MIXTURE KERNEL, SHARED BY EVERY CAMPAIGN ---

def build_mixture_kernel():
    """
    The 16 x 3 x 2 = 96 betting martingales of the mixture, in the witness's own
    construction order (l.356-366): a start time from the horizon grid, a
    betting fraction from ETA0_MIX_GRID, a side from SIDES. A component that has
    not started holds value 1, so the convex combination is a non-negative
    martingale with E_0 = 1 and Ville's inequality applies to it.
    """
    log_inc_1 = np.zeros(C_MIX)
    log_inc_0 = np.zeros(C_MIX)
    idx = 0
    start_times = np.zeros(C_MIX, dtype=int)
    for st in START_GRID:
        for e0 in ETA0_MIX_GRID:
            for sd in SIDES:
                start_times[idx] = st
                log_inc_1[idx] = np.log(2 * (0.5 + sd * e0))
                log_inc_0[idx] = np.log(2 * (0.5 - sd * e0))
                idx += 1
    return start_times, log_inc_1, log_inc_0


def build_ecusum_increments():
    """The four e-CUSUM log-increments (witness l.368-371)."""
    inc_p_1 = np.log(2 * (0.5 + ETA0_ECUSUM))
    inc_p_0 = np.log(2 * (0.5 - ETA0_ECUSUM))
    inc_m_1 = np.log(2 * (0.5 - ETA0_ECUSUM))
    inc_m_0 = np.log(2 * (0.5 + ETA0_ECUSUM))
    return inc_p_1, inc_p_0, inc_m_1, inc_m_0


def chunk_sizes_for(n_total):
    """The witness's chunk decomposition (l.374-376), invariant in `n_jobs`."""
    base_chunk = n_total // NUM_CHUNKS
    rem = n_total % NUM_CHUNKS
    return [base_chunk + 1 if i < rem else base_chunk for i in range(NUM_CHUNKS)]


# --- CHUNK WORKERS: PURE MODULE-LEVEL FUNCTIONS, NO LOGGING, NO SIDE EFFECT ---
# The delivered script configures its logger at module level with mode='w'.
# Under a process pool every worker that re-imports the module would truncate
# the log, so every side effect of this file lives inside main().

def process_m1_chunk(chunk_index, chunk_size, start_times, log_inc_1, log_inc_0):
    """
    M1(ii). The mixture martingale alone, on `chunk_size` fair-coin streams over
    [1, T_EXT]. Returns the first alarm per alpha AND the running maximum of
    logE, which is the statistic control C3 needs.
    """
    rng = rng_for("R09", "m1_ville", chunk_index)
    log_w = np.log(MIX_W)
    logM_mix = np.full((chunk_size, C_MIX), log_w)
    first_alarm_mix = {a: np.full(chunk_size, np.inf) for a in ALPHAS}
    max_logE = np.full(chunk_size, -np.inf)

    for t in range(T_EXT):
        y_t = (rng.random(size=chunk_size) < 0.5)
        active_idx = np.where(t >= start_times)[0]
        if len(active_idx) > 0:
            inc_mix = np.where(y_t[:, None] == 1, log_inc_1[active_idx], log_inc_0[active_idx])
            logM_mix[:, active_idx] += inc_mix
        logE_mix = logsumexp(logM_mix, axis=1)
        if np.any(np.isnan(logE_mix)) or np.any(np.isinf(logE_mix)):
            raise ValueError("NaN/Inf encountered in MIX logE_t.")
        max_logE = np.maximum(max_logE, logE_mix)
        for a in ALPHAS:
            cross = (logE_mix >= -np.log(a))
            mask = cross & (first_alarm_mix[a] == np.inf)
            first_alarm_mix[a][mask] = t + 1
    return first_alarm_mix, max_logE


def process_calibration_chunk(chunk_index, chunk_size):
    """
    The CUSUM calibration statistic: the maximum of M_t over the NOMINAL horizon
    [1, H] on `chunk_size` fair-coin streams. The delivered `calibrate_cusum`
    runs this serially over N_CAL; chunking it leaves the decomposition fixed at
    NUM_CHUNKS so the output cannot depend on `n_jobs`.
    """
    rng = rng_for("R09", "cusum_calibration", chunk_index)
    max_M = np.zeros(chunk_size)
    S_pos = np.zeros(chunk_size)
    S_neg = np.zeros(chunk_size)
    for t in range(H):
        y_t = (rng.random(size=chunk_size) < 0.5)
        dev = y_t - 0.5
        S_pos = np.maximum(0, S_pos + dev - DELTA_CUSUM)
        S_neg = np.maximum(0, S_neg - dev - DELTA_CUSUM)
        M_t = np.maximum(S_pos, S_neg)
        max_M = np.maximum(max_M, M_t)
    return max_M


def process_h0_chunk(chunk_index, chunk_size, lambda_star, start_times, log_inc_1, log_inc_0,
                     inc_p_1, inc_p_0, inc_m_1, inc_m_0):
    """
    The H0 campaign of panels A and C: three arms on the SAME fair-coin stream,
    so every between-arm comparison at fixed alpha is paired by construction.

    Returns, per arm: the first alarm per alpha, the crossing state at exactly
    t = T_EXT per alpha, and the running maximum of the arm's statistic over
    [1, T_EXT]. The running maxima are the addition against the delivered
    worker; they cost one np.maximum per step and they give control C3 its
    aggregate statistic and a structural cross-check with trigger probability
    zero (mean(first_alarm <= T_EXT) must equal mean(running_max >= threshold)
    exactly, for every arm and every alpha).
    """
    rng = rng_for("R09", "h0", chunk_index)
    S_pos = np.zeros(chunk_size)
    S_neg = np.zeros(chunk_size)
    logM_mix = np.full((chunk_size, C_MIX), np.log(MIX_W))
    logMp = np.zeros(chunk_size)
    logMm = np.zeros(chunk_size)

    fa_cusum = {a: np.full(chunk_size, np.inf) for a in ALPHAS}
    fa_mix = {a: np.full(chunk_size, np.inf) for a in ALPHAS}
    fa_ecusum = {a: np.full(chunk_size, np.inf) for a in ALPHAS}
    xt_cusum = {a: np.zeros(chunk_size, dtype=bool) for a in ALPHAS}
    xt_mix = {a: np.zeros(chunk_size, dtype=bool) for a in ALPHAS}
    xt_ecusum = {a: np.zeros(chunk_size, dtype=bool) for a in ALPHAS}
    max_cusum = np.full(chunk_size, -np.inf)
    max_mix = np.full(chunk_size, -np.inf)
    max_ecusum = np.full(chunk_size, -np.inf)

    for t in range(T_EXT):
        y_t = (rng.random(size=chunk_size) < 0.5)

        # CUSUM
        dev = y_t - 0.5
        S_pos = np.maximum(0, S_pos + dev - DELTA_CUSUM)
        S_neg = np.maximum(0, S_neg - dev - DELTA_CUSUM)
        M_cusum = np.maximum(S_pos, S_neg)

        # MIX
        active_idx = np.where(t >= start_times)[0]
        if len(active_idx) > 0:
            inc_mix = np.where(y_t[:, None] == 1, log_inc_1[active_idx], log_inc_0[active_idx])
            logM_mix[:, active_idx] += inc_mix
        logE_mix = logsumexp(logM_mix, axis=1)

        # eCUSUM
        ip = np.where(y_t == 1, inc_p_1, inc_p_0)
        im = np.where(y_t == 1, inc_m_1, inc_m_0)
        logMp = np.maximum(0, logMp + ip)
        logMm = np.maximum(0, logMm + im)
        M_ecusum = np.maximum(logMp, logMm)

        max_cusum = np.maximum(max_cusum, M_cusum)
        max_mix = np.maximum(max_mix, logE_mix)
        max_ecusum = np.maximum(max_ecusum, M_ecusum)

        for a in ALPHAS:
            c_cross = (M_cusum >= lambda_star[a])
            m_cross = (logE_mix >= -np.log(a))
            e_cross = (M_ecusum >= -np.log(a))

            fa_cusum[a][c_cross & (fa_cusum[a] == np.inf)] = t + 1
            fa_mix[a][m_cross & (fa_mix[a] == np.inf)] = t + 1
            fa_ecusum[a][e_cross & (fa_ecusum[a] == np.inf)] = t + 1

            if t == T_EXT - 1:
                xt_cusum[a] = c_cross
                xt_mix[a] = m_cross
                xt_ecusum[a] = e_cross

    return (fa_cusum, fa_mix, fa_ecusum, xt_cusum, xt_mix, xt_ecusum,
            max_cusum, max_mix, max_ecusum)


def process_h1_chunk(chunk_index, chunk_size, stream_sides, lambda_star, start_times,
                     log_inc_1, log_inc_0, inc_p_1, inc_p_0, inc_m_1, inc_m_0,
                     with_control_arm):
    """
    The H1 campaign of panel B. One uniform block is drawn per chunk BEFORE the
    eta loop, so every eta reads the same u[t] and differs only in the threshold
    applied to it: the common-random-numbers plan is structural here, not
    incidental, and comparisons across eta are paired.

    The e-CUSUM arm recurses on the same y_t and consumes no additional
    randomness, so a run without `--control-arms ecusum` produces byte-identical
    CUSUM and MIX alarms.
    """
    rng = rng_for("R09", "h1", chunk_index)
    u = rng.random(size=(H, chunk_size))
    arms = list(PUBLISHED_H1_ARMS) + ([CONTROL_H1_ARM] if with_control_arm else [])
    alarms = {}

    for eta in ETAS:
        p_alt = 0.5 + stream_sides * eta
        S_pos = np.zeros(chunk_size)
        S_neg = np.zeros(chunk_size)
        logM_mix = np.full((chunk_size, C_MIX), np.log(MIX_W))
        logMp = np.zeros(chunk_size)
        logMm = np.zeros(chunk_size)
        first = {arm: {a: np.full(chunk_size, np.inf) for a in ALPHAS} for arm in arms}

        for t in range(H):
            y_t = (u[t] < (0.5 if t < TAU else p_alt))

            dev = y_t - 0.5
            S_pos = np.maximum(0, S_pos + dev - DELTA_CUSUM)
            S_neg = np.maximum(0, S_neg - dev - DELTA_CUSUM)
            M_cusum = np.maximum(S_pos, S_neg)

            active_idx = np.where(t >= start_times)[0]
            if len(active_idx) > 0:
                inc_mix = np.where(y_t[:, None] == 1, log_inc_1[active_idx], log_inc_0[active_idx])
                logM_mix[:, active_idx] += inc_mix
            logE_mix = logsumexp(logM_mix, axis=1)

            if with_control_arm:
                ip = np.where(y_t == 1, inc_p_1, inc_p_0)
                im = np.where(y_t == 1, inc_m_1, inc_m_0)
                logMp = np.maximum(0, logMp + ip)
                logMm = np.maximum(0, logMm + im)
                M_ecusum = np.maximum(logMp, logMm)

            for a in ALPHAS:
                c_cross = (M_cusum >= lambda_star[a])
                m_cross = (logE_mix >= -np.log(a))
                first["CUSUM"][a][c_cross & (first["CUSUM"][a] == np.inf)] = t + 1
                first["MIX"][a][m_cross & (first["MIX"][a] == np.inf)] = t + 1
                if with_control_arm:
                    e_cross = (M_ecusum >= -np.log(a))
                    first[CONTROL_H1_ARM][a][
                        e_cross & (first[CONTROL_H1_ARM][a] == np.inf)] = t + 1

        for arm in arms:
            for a in ALPHAS:
                alarms[(arm, a, eta)] = first[arm][a]
    return alarms


# --- SOURCE IDENTITY (control C5), RUN BEFORE ANY CAMPAIGN ---

def source_segments(path, names):
    """
    Source text of the named top-level functions, extracted BY POSITION rather
    than by import: importing the witness would execute its environment block,
    its `mode='w'` logger, its `log_requirements()` call and its directory
    creation.
    """
    text = Path(path).read_text()
    tree = ast.parse(text)
    return {node.name: ast.get_source_segment(text, node)
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in names}


def assignment_segments(path, function_name, target_name):
    """
    The exact source text of every assignment to `target_name` inside
    `function_name` of `path`, in source order and de-duplicated.
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
    C5. Three layers, run BEFORE any campaign so that a transcription error
    costs no compute.

    (i)   byte identity of every carried primitive against the file that owns it;
    (ii)  the witness source of every adapted routine, quoted in full with its
          SHA-256, because an injected generator makes byte identity
          unassertable on them;
    (iii) STATEMENT-LEVEL identity of the recursions, which is what actually
          catches a transcription error: the exact source text of each
          recursion statement is extracted from the witness AST and must appear
          verbatim in this file.

    Deterministic; trigger probability 0 unless a copy has drifted.
    """
    if not WITNESS_SOURCE.exists():
        logger.error(f"C5 source-identity failure: {WITNESS_SOURCE} is missing, so no copy can be "
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
            logger.error(f"C5 source-identity failure: {name} could not be extracted "
                         f"({WITNESS_SOURCE.name}).")
            sys.exit(1)
        if mine != remote:
            logger.error(f"C5 source-identity failure on {name}: the copy has drifted from "
                         f"{WITNESS_SOURCE.name}.")
            sys.exit(1)
        compared += len(remote)
    logger.info(f"C5 (i) CARRIED PRIMITIVES: {len(CARRIED_PRIMITIVES)} byte-identical to "
                f"{WITNESS_SOURCE.name} ({compared} characters compared) -- "
                f"{', '.join(CARRIED_PRIMITIVES)}. Preamble S4.2 forbids hoisting any of them "
                f"into experiments/common/, so the duplication is deliberate. Deterministic; "
                f"trigger probability 0 unless a copy has drifted.")

    witness_adapted = source_segments(WITNESS_SOURCE, set(ADAPTED_ROUTINES))
    missing = [name for name in ADAPTED_ROUTINES if name not in witness_adapted]
    if missing:
        logger.error(f"C5: the witness carries no {missing}; the adaptation cannot be exhibited.")
        sys.exit(1)
    logger.info(f"C5 (ii) ADAPTED ROUTINES. {list(ADAPTED_ROUTINES)} each take an injected "
                f"generator keyed on role and index where {WITNESS_SOURCE.name} spawns one from a "
                f"master SeedSequence, and each replaces `rng.binomial(1, p, size)` by a threshold "
                f"on a shared uniform, so byte identity is not assertable on them and the witness "
                f"source of each is quoted in full below instead. This is the treatment "
                f"exp_R13_oracle_ceiling_a.py gives process_episode. The witness segments total "
                f"{sum(len(witness_adapted[n]) for n in ADAPTED_ROUTINES)} characters.")
    for name in ADAPTED_ROUTINES:
        logger.info(f"C5 witness SHA-256 of {name}: "
                    f"{hashlib.sha256(witness_adapted[name].encode('utf-8')).hexdigest()}")
        logger.info(f"C5 witness source of {name}:\n{witness_adapted[name].rstrip()}")

    checked = 0
    for function_name, target_name in CARRIED_STATEMENTS:
        segments = assignment_segments(WITNESS_SOURCE, function_name, target_name)
        if not segments:
            logger.error(f"C5 statement identity: the witness carries no assignment to "
                         f"`{target_name}` inside `{function_name}`.")
            sys.exit(1)
        for segment in segments:
            if segment not in own_text:
                logger.error(f"C5 STATEMENT IDENTITY FAILURE. The witness statement "
                             f"`{segment}` ({WITNESS_SOURCE.name}::{function_name}) does not "
                             f"appear verbatim in {own_path.name}. A recursion has been "
                             f"transcribed differently.")
                sys.exit(1)
            checked += 1
    logger.info(f"C5 (iii) STATEMENT IDENTITY: {checked} recursion statements extracted from the "
                f"witness AST and found verbatim in {own_path.name} -- the three CUSUM lines, the "
                f"four MIX lines, the five e-CUSUM lines, the two mixture log-increments, the four "
                f"e-CUSUM increment definitions and the calibration quantile. Deterministic; "
                f"trigger probability 0 unless a copy has drifted.")


def check_bound_flag_is_computed(logger):
    """
    C2, first half. `arl0_bound_respected` must be a COMPUTED comparison against
    1.0/alpha and not a constant. The producing expression is located in this
    file's own AST and its shape asserted; the second half -- the flag evaluated
    against an independently written comparison -- lives in
    tests/test_R09_claims.py.

    Deterministic; trigger probability 0.
    """
    tree = ast.parse(Path(__file__).resolve().read_text())
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and key.value == "arl0_bound_respected":
                found.append(value)
    if len(found) != 1:
        logger.error(f"C2 FAILED: `arl0_bound_respected` is produced at {len(found)} sites, not "
                     f"one; the control cannot name the line it asserts.")
        sys.exit(1)
    expression = found[0]
    if not isinstance(expression, ast.Compare) or len(expression.ops) != 1 \
            or not isinstance(expression.ops[0], ast.GtE):
        logger.error("C2 FAILED: `arl0_bound_respected` is not a single `>=` comparison. A "
                     "constant boolean written into every row of a file is either a definitional "
                     "tautology or a literal, and neither is a measurement.")
        sys.exit(1)
    right = ast.unparse(expression.comparators[0])
    if "1.0" not in right:
        logger.error(f"C2 FAILED: `arl0_bound_respected` compares against `{right}`, which does "
                     f"not carry the reciprocal 1.0/alpha.")
        sys.exit(1)
    logger.info(f"C2 (i) `arl0_bound_respected` is the computed comparison "
                f"`{ast.unparse(expression)}`, located in this file's own AST: a single `>=` "
                f"whose right-hand side is `{right}`. It is NEITHER a definitional tautology NOR "
                f"a literal -- it is a computed comparison that is ARITHMETICALLY NECESSARY for "
                f"the censored arms, because arl0 = mean(min(fa, T_EXT)) is bounded below by "
                f"censored_frac * T_EXT, i.e. by at least "
                f"{0.65 * T_EXT:.0f} at a censored fraction of 0.65, against a 1/alpha of at most "
                f"{1.0 / min(ALPHAS):.0f}. The per-row implied lower bound and whether the flag "
                f"carried information are logged with the ARL0 table. Deterministic; trigger "
                f"probability 0. This answers R09 prompt section 2.1.")


# --- CONTROL STATISTICS: EACH WITH ITS NULL LAW ---

def one_sided_ks_dplus(u):
    """
    D+ = sup_x (F_n(x) - x), the one-sided Kolmogorov statistic against the
    Uniform(0,1) boundary, computed from the sorted sample rather than from a
    library routine so that the test file can reimplement it independently.
    """
    n = len(u)
    ordered = np.sort(np.asarray(u, dtype=float))
    return float(max(0.0, np.max(np.arange(1, n + 1) / n - ordered)))


def permutation_matrix(n):
    """
    All n! permutations of range(n) as an int8 matrix, materialised once and
    reused by every exact permutation test of control C4. Streamed through
    itertools in blocks so peak memory stays bounded.
    """
    count = math.factorial(n)
    out = np.empty((count, n), dtype=np.int8)
    stream = itertools.permutations(range(n))
    block = 262144
    filled = 0
    while filled < count:
        take = min(block, count - filled)
        flat = np.fromiter(itertools.chain.from_iterable(itertools.islice(stream, take)),
                           dtype=np.int8, count=n * take)
        out[filled:filled + take] = flat.reshape(take, n)
        filled += take
    return out


def exact_spearman(values, grid, perms):
    """
    Spearman's rho of `values` against `grid` with the EXACT conditional
    permutation null: the statistic T = sum_i rank(values)[p(i)] * rank(grid)[i]
    is evaluated over all n! permutations p. Exact in the presence of ties,
    which a closed-form sum-of-d-squared tail is not.

    Returns rho, the one-sided p-value for a DECREASING relation, the one-sided
    p-value for an INCREASING relation, and the tie count of `values`.
    """
    a = stats.rankdata(np.asarray(values, dtype=float))
    b = stats.rankdata(np.asarray(grid, dtype=float))
    n = len(a)
    rho = float(np.corrcoef(a, b)[0, 1])
    observed = float(np.dot(a, b))
    count = perms.shape[0]
    at_or_below = 0
    at_or_above = 0
    block = 500000
    for start in range(0, count, block):
        gathered = a[perms[start:start + block]]
        totals = gathered @ b
        at_or_below += int(np.count_nonzero(totals <= observed + 1e-9))
        at_or_above += int(np.count_nonzero(totals >= observed - 1e-9))
    ties = int(n - len(np.unique(np.asarray(values, dtype=float))))
    return rho, at_or_below / count, at_or_above / count, ties


def weighted_least_squares_slope(x, y, sem):
    """
    Slope of `y` on `x` weighted by 1/sem^2, with the standard error the weights
    imply. Returns (slope, se); NaN when a weight is not finite.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    sem = np.asarray(sem, dtype=float)
    if not (np.isfinite(y).all() and np.isfinite(sem).all() and (sem > 0).all()):
        return float('nan'), float('nan')
    w = 1.0 / sem**2
    xbar = float(np.sum(w * x) / np.sum(w))
    ybar = float(np.sum(w * y) / np.sum(w))
    sxx = float(np.sum(w * (x - xbar)**2))
    slope = float(np.sum(w * (x - xbar) * (y - ybar)) / sxx)
    return slope, float(np.sqrt(1.0 / sxx))


def empirical_quantile(values, q):
    """
    The smallest x with F_n(x) >= q, i.e. the inverted-CDF quantile, written out
    as an index into the sorted sample so that +inf entries never enter an
    arithmetic interpolation and so that the test file can reimplement it.
    """
    ordered = np.sort(np.asarray(values, dtype=float))
    n = len(ordered)
    index = int(math.ceil(q * n)) - 1
    return float(ordered[min(max(index, 0), n - 1)])


# --- CAMPAIGN ---

def run_campaign(logger, n_jobs, with_control_arm):
    """
    M1, the CUSUM calibration, the H0 campaign and the H1 campaign, in that
    order. Every task is keyed on its role and index alone; NUM_CHUNKS fixes the
    decomposition, so `n_jobs` cannot move a number.
    """
    start_times, log_inc_1, log_inc_0 = build_mixture_kernel()
    inc_p_1, inc_p_0, inc_m_1, inc_m_0 = build_ecusum_increments()
    logger.info(f"Mixture kernel: {C_MIX} = {len(START_GRID)} start times x "
                f"{len(ETA0_MIX_GRID)} betting fractions x {len(SIDES)} sides, uniform weight "
                f"{MIX_W!r}. e-CUSUM increments: log(2*(0.5+eta0)) = {inc_p_1!r}, "
                f"log(2*(0.5-eta0)) = {inc_p_0!r} at eta0 = {ETA0_ECUSUM}.")

    # --- M1(i): the mixture kernel has expectation one under H0 ---
    t_m1 = time.time()
    rng = rng_for("R09", "m1_expectation")
    y = (rng.random(size=M1_EXPECTATION_STEPS) < 0.5)
    eta0_draws = rng.choice(ETA0_MIX_GRID, size=M1_EXPECTATION_STEPS)
    side_draws = rng.choice(SIDES, size=M1_EXPECTATION_STEPS)
    lambda_t = np.where(y == 1, 2 * (0.5 + side_draws * eta0_draws),
                        2 * (0.5 - side_draws * eta0_draws))
    mean_lambda = float(np.mean(lambda_t))
    sd_lambda = math.sqrt(4.0 * sum(e**2 for e in ETA0_MIX_GRID) / len(ETA0_MIX_GRID))
    se_lambda = sd_lambda / math.sqrt(M1_EXPECTATION_STEPS)
    logger.info(f"M1(i) mean of lambda_t over {M1_EXPECTATION_STEPS:g} steps: {mean_lambda:.7f}, "
                f"displaced from 1 by {abs(mean_lambda - 1.0) / se_lambda:.3f} standard errors "
                f"(analytic SD {sd_lambda:.6f}, SE {se_lambda:.3e}).")
    if abs(mean_lambda - 1.0) > M1_EXPECTATION_TOL:
        logger.error(f"M1(i) FAILED: E[lambda_t] = {mean_lambda!r} is more than "
                     f"{M1_EXPECTATION_TOL} from 1. The mixture kernel is not a martingale "
                     f"increment and Ville's inequality does not apply to it.")
        sys.exit(1)

    # --- M1(ii): Ville's bound on an independent 20 000-stream replicate ---
    sizes = chunk_sizes_for(N_NULL)
    m1_chunks = Parallel(n_jobs=n_jobs)(
        delayed(process_m1_chunk)(i, sizes[i], start_times, log_inc_1, log_inc_0)
        for i in range(NUM_CHUNKS))
    m1_first_alarm = {a: np.concatenate([chunk[0][a] for chunk in m1_chunks]) for a in ALPHAS}
    m1_max_logE = np.concatenate([chunk[1] for chunk in m1_chunks])
    logger.info(f"M1 completed in {time.time() - t_m1:.1f}s over {NUM_CHUNKS} chunks of "
                f"{sizes[0]} streams.")

    # --- CUSUM calibration on N_CAL streams over the NOMINAL horizon ---
    t_cal = time.time()
    cal_sizes = chunk_sizes_for(N_CAL)
    max_M = np.concatenate(Parallel(n_jobs=n_jobs)(
        delayed(process_calibration_chunk)(i, cal_sizes[i]) for i in range(NUM_CHUNKS)))
    lambda_star = {}
    actual_level = {}
    for a in ALPHAS:
        l_star = np.quantile(max_M, 1 - a)
        lambda_star[a] = l_star
        achieved = np.mean(max_M >= l_star)
        actual_level[a] = float(achieved)
        logger.info(f"Calibration alpha={a}: lambda_star={l_star:.4f}, achieved={achieved:.4f} "
                    f"on N_CAL = {N_CAL} streams over [1, H].")
    logger.info(f"CUSUM comparison semantics, carried from the witness: raw float64 "
                f"max_M >= lambda_star. Calibration completed in {time.time() - t_cal:.1f}s.")

    # --- H0 campaign ---
    t_h0 = time.time()
    h0_chunks = Parallel(n_jobs=n_jobs)(
        delayed(process_h0_chunk)(i, sizes[i], lambda_star, start_times, log_inc_1, log_inc_0,
                                  inc_p_1, inc_p_0, inc_m_1, inc_m_0)
        for i in range(NUM_CHUNKS))
    first_alarm = {
        "CUSUM": {a: np.concatenate([c[0][a] for c in h0_chunks]) for a in ALPHAS},
        "MIX": {a: np.concatenate([c[1][a] for c in h0_chunks]) for a in ALPHAS},
        "eCUSUM": {a: np.concatenate([c[2][a] for c in h0_chunks]) for a in ALPHAS},
    }
    exact_cross = {
        "CUSUM": {a: np.concatenate([c[3][a] for c in h0_chunks]) for a in ALPHAS},
        "MIX": {a: np.concatenate([c[4][a] for c in h0_chunks]) for a in ALPHAS},
        "eCUSUM": {a: np.concatenate([c[5][a] for c in h0_chunks]) for a in ALPHAS},
    }
    running_max = {
        "CUSUM": np.concatenate([c[6] for c in h0_chunks]),
        "MIX": np.concatenate([c[7] for c in h0_chunks]),
        "eCUSUM": np.concatenate([c[8] for c in h0_chunks]),
    }
    logger.info(f"H0 campaign completed in {time.time() - t_h0:.1f}s: {N_NULL} fair-coin streams "
                f"over [1, {T_EXT}], three arms on the SAME stream, so every between-arm "
                f"comparison at fixed alpha is paired.")

    # --- H1 campaign ---
    t_h1 = time.time()
    stream_sides = rng_for("R09", "h1_sides").choice(SIDES, size=N_ALT)
    alt_sizes = chunk_sizes_for(N_ALT)
    offsets = np.concatenate([[0], np.cumsum(alt_sizes)])
    h1_chunks = Parallel(n_jobs=n_jobs)(
        delayed(process_h1_chunk)(i, alt_sizes[i],
                                  stream_sides[offsets[i]:offsets[i + 1]], lambda_star,
                                  start_times, log_inc_1, log_inc_0,
                                  inc_p_1, inc_p_0, inc_m_1, inc_m_0, with_control_arm)
        for i in range(NUM_CHUNKS))
    h1_arms = list(PUBLISHED_H1_ARMS) + ([CONTROL_H1_ARM] if with_control_arm else [])
    h1_alarm = {(arm, a, eta): np.concatenate([c[(arm, a, eta)] for c in h1_chunks])
                for arm in h1_arms for a in ALPHAS for eta in ETAS}
    logger.info(f"H1 campaign completed in {time.time() - t_h1:.1f}s: {N_ALT} drift streams per "
                f"cell, {len(ETAS)} drift magnitudes, arms {h1_arms}. The side of every stream is "
                f"drawn once from the key ('R09', 'h1_sides') and is SHARED across every eta, and "
                f"one uniform block per chunk is drawn before the eta loop, so the drift grid is "
                f"traversed under common random numbers.")

    return {
        "lambda_star": lambda_star,
        "actual_level": actual_level,
        "max_M_cal": max_M,
        "first_alarm": first_alarm,
        "exact_cross": exact_cross,
        "running_max": running_max,
        "m1_first_alarm": m1_first_alarm,
        "m1_max_logE": m1_max_logE,
        "h1_alarm": h1_alarm,
        "h1_arms": h1_arms,
        "stream_sides": stream_sides,
    }


# --- FRAME CONSTRUCTION ---

def build_validity_stopping(campaign):
    """
    `protocol_22a`. Three arms x seven levels x three stopping protocols, with
    the exact one-sided binomial p-value of the realized rate against its own
    nominal level added as a DESCRIPTIVE column (S4bis point 3).
    """
    guarantee = {"CUSUM": "fixed_horizon", "MIX": "ville_anytime", "eCUSUM": "arl0_only"}
    records = []
    for arm in ARMS_H0:
        for a in ALPHAS:
            for p_name, p_time, exact in STOPPING_PROTOCOLS:
                if exact:
                    crosses = int(np.sum(campaign["exact_cross"][arm][a]))
                else:
                    crosses = int(np.sum(campaign["first_alarm"][arm][a] <= p_time))
                fpr = crosses / N_NULL
                ci_low, ci_high = wilson_ci(crosses, N_NULL)
                if arm == "MIX":
                    b_resp = str(fpr <= a)
                elif arm == "CUSUM":
                    b_resp = ("FPR~alpha at calibration point" if p_name == "nominal"
                              else str(fpr <= a))
                else:
                    b_resp = "n/a (documentary)"
                records.append({
                    "arm": arm, "alpha": a, "stopping_protocol": p_name,
                    "guarantee_type": guarantee[arm], "threshold": a, "N_streams": N_NULL,
                    "FPR": fpr, "CI_low": max(0.0, min(1.0, ci_low)),
                    "CI_high": max(0.0, min(1.0, ci_high)),
                    "bound_target": a, "bound_respected": b_resp,
                    "binom_p_one_sided": float(stats.binom.sf(crosses - 1, N_NULL, a)),
                })
    return pd.DataFrame(records)


def build_eprocess_race(campaign, arms):
    """
    `protocol_22b`. ADD is CONDITIONAL on an alarm in (TAU, H]; the detection
    rate on the same row is what makes that conditioning readable.
    """
    records = []
    for arm in arms:
        for a in ALPHAS:
            for eta in ETAS:
                fa = campaign["h1_alarm"][(arm, a, eta)]
                valid = (fa > TAU) & (fa <= H)
                n_valid = int(np.sum(valid))
                delays = fa[valid] - TAU
                det = float(np.mean(valid))
                ci_low, ci_high = wilson_ci(n_valid, N_ALT)
                records.append({
                    "arm": arm, "alpha": a, "eta": eta, "N_streams": N_ALT,
                    "DetRate": det, "DetRate_CI_low": max(0.0, min(1.0, ci_low)),
                    "DetRate_CI_high": max(0.0, min(1.0, ci_high)),
                    "ADD": float(np.mean(delays)) if n_valid > 0 else float('nan'),
                    "SEM": (float(np.std(delays) / math.sqrt(n_valid)) if n_valid > 0
                            else float('nan')),
                })
    return pd.DataFrame(records)


def build_level_granularity(campaign, attainable_levels):
    """
    `protocol_22c`. `level_is_attainable` is COMPUTED, not typed: the CUSUM
    threshold is a quantile of a statistic living on the 2*DELTA_CUSUM lattice,
    so only that lattice's own survival values are reachable, whereas the MIX
    threshold is -log(alpha), an exact function of alpha with no calibration
    sample and therefore no lattice.
    """
    records = []
    for arm in ("CUSUM", "MIX"):
        for a in ALPHAS:
            fa = campaign["first_alarm"][arm][a]
            crosses = int(np.sum(fa <= H))
            fpr = crosses / N_NULL
            ci_low, ci_high = wilson_ci(crosses, N_NULL)
            if arm == "CUSUM":
                attainable = bool(np.any(attainable_levels == a))
            else:
                attainable = bool(np.isfinite(-np.log(a)))
            records.append({
                "arm": arm, "alpha": a, "target_level": a, "achieved_level": fpr,
                "achieved_CI_low": max(0.0, min(1.0, ci_low)),
                "achieved_CI_high": max(0.0, min(1.0, ci_high)),
                "gap_pp": (fpr - a) * 100, "level_is_attainable": attainable,
            })
    return pd.DataFrame(records)


def build_arl0(campaign, logger):
    """
    `protocol_22d`. C1 is structural here: `censored_frac` is written on the
    same row as every `ARL0_mean`, and two further columns make the censoring
    arithmetic legible -- the implied lower bound censored_frac * T_EXT, and
    whether `arl0_bound_respected` carried any information once that bound is
    known (D4).
    """
    records = []
    for arm in ARMS_H0:
        for a in ALPHAS:
            arr = campaign["first_alarm"][arm][a]
            arr_capped = np.minimum(arr, T_EXT)
            arl0 = float(np.mean(arr_capped))
            sem = float(np.std(arr_capped) / math.sqrt(N_NULL))
            c_frac = float(np.mean(arr == np.inf))
            implied = c_frac * T_EXT
            records.append({
                "arm": arm, "alpha": a, "ARL0_mean": arl0,
                "ARL0_CI_low": arl0 - 1.96 * sem, "ARL0_CI_high": arl0 + 1.96 * sem,
                "ref_inv_alpha": 1.0 / a, "censored_frac": c_frac,
                "right_censored_flag": c_frac > 0.05,
                "arl0_bound_respected": arl0 >= (1.0 / a),
                "arl0_implied_lower_bound": implied,
                "bound_flag_carried_information": implied < (1.0 / a),
            })
            if c_frac > 0:
                logger.info(f"Censorship registered: {arm} alpha={a} has right-censored fraction "
                            f"= {c_frac:.4f}. ARL0_mean behaves strictly as a lower bound, and the "
                            f"censoring alone forces ARL0_mean >= {implied:.1f} against a "
                            f"1/alpha of {1.0 / a:.1f}.")
    return pd.DataFrame(records)


# --- CONTROLS ---

def log_control_design(logger, n_jobs, with_control_arm):
    """
    Every numeric gate of this stream, with its null law and its trigger
    probability under that null, logged BEFORE any result is read (S4bis).
    """
    logger.info("=" * 78)
    logger.info("CONTROL DESIGN, FIXED BEFORE THE FIRST NUMBER IS READ (S4bis, S4.10)")
    logger.info("=" * 78)
    logger.info(f"C1 -- CENSORING IS INSEPARABLE FROM EVERY ARL0. No ARL0_mean is written to any "
                f"frame, plotted, or passed to the macro emitter without censored_frac on the same "
                f"row. Asserted on the frame schema and on the emitter's input. Deterministic; "
                f"trigger probability 0.")
    logger.info(f"C2 -- `arl0_bound_respected` IS COMPUTED, NOT A LITERAL. Asserted on this file's "
                f"own AST and, independently, in tests/test_R09_claims.py. Deterministic; trigger "
                f"probability 0.")
    logger.info(f"C3 -- THE MARTINGALE BOUND, AS ONE STATISTIC WITH AN EXACT NULL. Seven binary "
                f"gates at 5% would ring on a compliant campaign with probability "
                f"1 - 0.95^{len(ALPHAS)} = {1 - 0.95**len(ALPHAS):.4f}; worse, the submitted MIX "
                f"peeking rate sits at 0.94-0.99 of alpha, so at alpha = 0.05 the margin to the "
                f"bound is 0.00055 against a binomial SE of "
                f"{math.sqrt(0.05 * 0.95 / N_NULL):.5f} -- 0.36 sigma, a ~36% chance of a spurious "
                f"exceedance at that level alone. A KS test of seven p-values against Uniform(0,1) "
                f"is the wrong instrument too: under Ville the p-values are STOCHASTICALLY LARGE "
                f"by construction, so a two-sided uniformity test would reject precisely because "
                f"the bound is conservative. DESIGN: let Z = sup_(1<=t<=T_EXT) E_t per H0 stream "
                f"and U = min(1, 1/Z). Ville gives P(Z >= 1/alpha) <= alpha for EVERY alpha, i.e. "
                f"F_U(alpha) <= alpha over the whole range. Tested with the ONE-SIDED Kolmogorov "
                f"statistic D+ = sup_alpha (F_n(alpha) - alpha) on n = {N_NULL}, exact null "
                f"scipy.stats.ksone.sf(D+, n) at the least-favourable boundary F_U = Id. GATE AT "
                f"{GATE_LEVEL}; trigger probability under its own null is EXACTLY {GATE_LEVEL}, "
                f"and strictly below it because the true F_U is bounded away from the identity "
                f"and U has atoms.")
    logger.info(f"C3 DERIVATION, one line as S4.6 requires: each mixture component is a "
                f"non-negative martingale with E_0 = 1 (a component not yet started holds value "
                f"1), a convex combination of martingales is a martingale, and Ville's inequality "
                f"on a non-negative martingale gives P(sup_t E_t >= c) <= E_0 / c = 1/c.")
    logger.info(f"C3 NEGATIVE CONTROL, same statistic, on the CUSUM arm, with U_cusum the "
                f"calibration survival probability of the peeking maximum read off the "
                f"N_CAL = {N_CAL} sample. It must reject decisively -- that is v87's own claim "
                f"that fixed-horizon CUSUM does not control the time-uniform rate -- which is what "
                f"establishes the test has power against the alternative it is used on. U_cusum "
                f"uses an ESTIMATED CDF and therefore carries the double variance of S4bis's "
                f"second corollary; this direction is a control on power, not an acceptance gate.")
    logger.info(f"C4 -- THE POSITIVE CONTROL, PER ARM, WITH AN AGGREGATE RATHER THAN NINE GATES. "
                f"Nine adjacent-pair comparisons per arm would ring with probability "
                f"1 - (1 - p)^9 = {1 - 0.99**9:.4f} at p = 0.01, and strict adjacent monotonicity "
                f"is unusable anyway: in the submitted campaign the CUSUM pair eta = 0.02 -> 0.04 "
                f"moves 1244.36 -> 1234.90, a difference of -9.5 against a difference SE of order "
                f"77, which inverts roughly half the time. INSTEAD, per arm: a Spearman rank "
                f"correlation of ADD against eta over the {len(ETAS)} grid points, ONE-SIDED, with "
                f"its EXACT permutation null ({math.factorial(len(ETAS))} permutations, enumerated "
                f"in full). GATE AT {GATE_LEVEL} on each of the arms; rho, the exact p-value, the "
                f"nine pairwise z-margins and a weighted least-squares slope are reported "
                f"descriptively. The same test runs on detection rate against eta, one-sided "
                f"increasing, and is reported without gating.")
    logger.info(f"C4 THE CONFOUNDER IS NAMED, NOT BURIED. ADD is conditional on "
                f"(fa > TAU) & (fa <= H), and detection rates run from about 0.057 to 0.98 across "
                f"the grid, so at small eta a slower arm that detects MORE streams necessarily "
                f"averages over slower ones. THE PRIMARY INSTRUMENT IS A MATCHED-DETECTION-RATE "
                f"QUANTILE, not the common-detection subset: the intersection of two detection "
                f"events whose rates differ by a factor of 2.8 is dominated by the streams both "
                f"arms find easy, its composition depends on both detectors, and it is therefore "
                f"itself a selected sample that cannot carry a D3. At each eta, q = "
                f"min(p_CUSUM, p_MIX) and the q-quantile of each arm's alarm-time distribution is "
                f"compared with non-detections placed at +inf. This asks 'to reach the same "
                f"detection rate, which arm needs fewer steps', is well defined for every "
                f"q <= min(p), conditions on nothing, and is the same iso-rate comparison the "
                f"paper's own iso-FPR race uses. Reported with a paired bootstrap interval over "
                f"the {N_ALT} trajectory indices, {C4_BOOTSTRAP_REPLICATES} replicates at the "
                f"{C4_BOOTSTRAP_LEVEL:.0%} level. The common-detection paired difference is "
                f"computed and reported BESIDE it as a second reading and gates nothing.")
    logger.info(f"C4 DECISION RULE, FIXED BEFORE THE FIRST NUMBER. (1) If MIX's matched-rate "
                f"quantile is at or below CUSUM's at eta in {C4_HALT_ETAS}, the marginal ADD "
                f"reversal is an artefact of conditioning on detection; L243's 'ceding ground only "
                f"for abrupt shifts' and the caption's 'matches ... for eta <= 0.10' stand, and "
                f"the caveat is a Class A entry with no severity. (2) If MIX's matched-rate "
                f"quantile is strictly above CUSUM's with the paired bootstrap interval excluding "
                f"zero, a printed qualitative claim is contradicted: D3, full stop, full report, "
                f"no parameter moved.")
    logger.info(f"C5 -- `ast` SOURCE IDENTITY, run before any compute so a transcription error "
                f"costs no time. Deterministic; trigger probability 0 unless a copy has drifted.")
    logger.info(f"C6 -- REPRODUCIBILITY, THREE AXES. (1) two successive runs, SHA-256 identical on "
                f"every artefact; (2) --n-jobs 1 against the default, byte-identical, since "
                f"NUM_CHUNKS = {NUM_CHUNKS} fixes the decomposition; (3) the run WITHOUT "
                f"--control-arms reproduces the four published CSVs byte for byte, proving the "
                f"control arm leaks no state into the published path. Verified outside the "
                f"process, from the digests this log records.")
    logger.info(f"CALIBRATION COHERENCE, REPLACING THE DELIVERED CONTROLS (b) AND (e). The "
                f"delivered gates `0.046 <= FPR <= 0.055` and "
                f"`|FPR_M2 - calib| <= 3 sqrt(alpha(1-alpha)/N_NULL)` both ignore that "
                f"lambda_star is ITSELF ESTIMATED on N_CAL = {N_CAL} streams (S4bis, second "
                f"corollary). The correct variance of the difference is "
                f"alpha(1-alpha)(1/N_NULL + 1/N_CAL) = "
                f"{FIGURE_ALPHA * (1 - FIGURE_ALPHA) * (1 / N_NULL + 1 / N_CAL):.3e} at "
                f"alpha = {FIGURE_ALPHA}, i.e. an SE of "
                f"{math.sqrt(FIGURE_ALPHA * (1 - FIGURE_ALPHA) * (1 / N_NULL + 1 / N_CAL)):.6f} "
                f"against the delivered {math.sqrt(FIGURE_ALPHA * (1 - FIGURE_ALPHA) / N_NULL):.6f}"
                f". The tolerance is z(1 - {COHERENCE_LEVEL}/2) times that SE and is derived from "
                f"the mechanism, never from an observed gap; its trigger probability under its own "
                f"null is {COHERENCE_LEVEL}.")
    logger.info(f"M1(i) GATE. |E[lambda_t] - 1| > {M1_EXPECTATION_TOL} halts the run. "
                f"Var(lambda_t) = 4 E[eta0^2] = "
                f"{4.0 * sum(e**2 for e in ETA0_MIX_GRID) / len(ETA0_MIX_GRID):.6f} exactly, so "
                f"the SE over {M1_EXPECTATION_STEPS:g} draws is "
                f"{math.sqrt(4.0 * sum(e**2 for e in ETA0_MIX_GRID) / len(ETA0_MIX_GRID) / M1_EXPECTATION_STEPS):.3e}"
                f" and the delivered tolerance is "
                f"{M1_EXPECTATION_TOL / math.sqrt(4.0 * sum(e**2 for e in ETA0_MIX_GRID) / len(ETA0_MIX_GRID) / M1_EXPECTATION_STEPS):.1f}"
                f" standard errors; two-sided trigger probability "
                f"{2 * stats.norm.sf(M1_EXPECTATION_TOL / math.sqrt(4.0 * sum(e**2 for e in ETA0_MIX_GRID) / len(ETA0_MIX_GRID) / M1_EXPECTATION_STEPS)):.3e}"
                f". The tolerance is derived, so it is kept; the delivered M1(ii) gate "
                f"`if fpr > a + 0.005` is NOT, and it is removed as a gate and replaced by C3.")
    n_gates = 1 + len(ARMS_H0)
    family = 1 - (1 - GATE_LEVEL) ** n_gates
    logger.info(f"STREAM-LEVEL FAMILY-WISE TRIGGER PROBABILITY, LOGGED ONCE BEFORE ANY RESULT IS "
                f"READ. C3 gates at {GATE_LEVEL} on one arm; C4 gates on a one-sided Spearman at "
                f"{GATE_LEVEL} on each of {len(ARMS_H0)} arms. {n_gates} gates whose nulls are, by "
                f"construction, exact or conservative, so the probability that at least one fires "
                f"on a compliant campaign is bounded by 1 - (1 - {GATE_LEVEL})^{n_gates} = "
                f"{family:.6%}, below the 5% ceiling S4bis fixes. Including the calibration "
                f"coherence gate at {COHERENCE_LEVEL} and the M1(i) gate the full stream-level "
                f"figure is "
                f"{1 - (1 - GATE_LEVEL) ** n_gates * (1 - COHERENCE_LEVEL) * (1 - 2 * stats.norm.sf(M1_EXPECTATION_TOL / math.sqrt(4.0 * sum(e**2 for e in ETA0_MIX_GRID) / len(ETA0_MIX_GRID) / M1_EXPECTATION_STEPS))):.6%}"
                f", still below the ceiling. No level is chosen after a result is seen.")
    logger.info(f"HALT CONDITION. If C4's matched-detection-rate quantile shows MIX strictly "
                f"slower than CUSUM at eta <= {max(C4_HALT_ETAS)} with its paired bootstrap "
                f"interval excluding zero, or if C3's D+ rejects on the MIX arm, that is a D3: "
                f"stop, report in full, change no parameter, tolerance, seed or bound. A reversal "
                f"visible only in the marginal conditional ADD, or only on the common-detection "
                f"subset, is NOT a halt condition and is reported under `R09-add-conditioning`.")
    logger.info(f"Worker processes requested: {n_jobs}; control arm computed: {with_control_arm}. "
                f"NUM_CHUNKS = {NUM_CHUNKS} is fixed, so neither value can move a number.")
    logger.info("=" * 78)


def control_c1(frame_arl0, logger):
    """C1. Structural; deterministic; trigger probability 0."""
    if "censored_frac" not in frame_arl0.columns:
        logger.error("C1 FAILED: the ARL0 frame persists ARL0_mean with no censored_frac column.")
        sys.exit(1)
    offending = frame_arl0[frame_arl0["ARL0_mean"].notna() & frame_arl0["censored_frac"].isna()]
    if len(offending) > 0:
        logger.error(f"C1 FAILED: {len(offending)} rows carry a finite ARL0_mean with no censored "
                     f"fraction.")
        sys.exit(1)
    if not ((frame_arl0["censored_frac"] >= 0.0) & (frame_arl0["censored_frac"] <= 1.0)).all():
        logger.error("C1 FAILED: a censored fraction lies outside [0, 1].")
        sys.exit(1)
    logger.info(f"C1: all {len(frame_arl0)} rows of the ARL0 frame carry a finite ARL0_mean with "
                f"its censored_frac on the same row. Censoring by arm: "
                + "; ".join(
                    f"{arm} {frame_arl0[frame_arl0['arm'] == arm]['censored_frac'].min():.4f}"
                    f"-{frame_arl0[frame_arl0['arm'] == arm]['censored_frac'].max():.4f}"
                    for arm in ARMS_H0)
                + ". Deterministic; trigger probability 0.")


def control_c2_report(frame_arl0, logger):
    """
    C2, second half: whether the computed flag carried information, per row.
    D4 of the plan -- `arl0 = mean(min(fa, T_EXT))` is bounded below by
    `censored_frac * T_EXT`, so on a heavily censored arm the comparison against
    1/alpha is arithmetically necessary and the flag is uninformative.
    """
    informative = frame_arl0[frame_arl0["bound_flag_carried_information"]]
    logger.info(f"C2 (ii) THE FLAG CARRIES INFORMATION ON {len(informative)} OF "
                f"{len(frame_arl0)} ROWS, and they are all on the {sorted(set(informative['arm']))}"
                f" arm(s). On every other row censored_frac * T_EXT already exceeds 1/alpha, so "
                f"`arl0_bound_respected` could not have been False whatever the campaign measured.")
    for row in frame_arl0.itertuples(index=False):
        logger.info(f"C2 [{row.arm} alpha={row.alpha}] ARL0_mean = {row.ARL0_mean!r}, "
                    f"censored_frac = {row.censored_frac!r}, implied lower bound "
                    f"censored_frac*T_EXT = {row.arl0_implied_lower_bound!r}, 1/alpha = "
                    f"{row.ref_inv_alpha!r}, flag = {bool(row.arl0_bound_respected)}, flag carried "
                    f"information = {bool(row.bound_flag_carried_information)}.")


def control_c3(campaign, frame_validity, logger):
    """
    C3. One one-sided Kolmogorov statistic with an exact null on the MIX arm,
    an independent replicate from M1(ii), the seven descriptive binomial
    p-values, and the negative control on the CUSUM arm.

    Returns the assembled diagnostics and whether the gate fired.
    """
    u_mix = np.minimum(1.0, np.exp(-campaign["running_max"]["MIX"]))
    d_plus = one_sided_ks_dplus(u_mix)
    p_value = float(stats.ksone.sf(d_plus, N_NULL))
    logger.info(f"C3 [MIX, H0 campaign] D+ = {d_plus!r} on n = {N_NULL}, exact one-sided p = "
                f"{p_value!r} against the least-favourable boundary F_U = Id. Gate at "
                f"{GATE_LEVEL}; verdict = {'REJECT' if p_value < GATE_LEVEL else 'no rejection'}. "
                f"U = min(1, 1/sup_t E_t) has an atom at 1 of mass "
                f"{float(np.mean(u_mix >= 1.0)):.4f} -- streams whose mixture never exceeds 1 -- "
                f"which sits above every alpha and cannot inflate D+.")

    u_m1 = np.minimum(1.0, np.exp(-campaign["m1_max_logE"]))
    d_plus_m1 = one_sided_ks_dplus(u_m1)
    p_m1 = float(stats.ksone.sf(d_plus_m1, N_NULL))
    logger.info(f"C3 [MIX, M1(ii) independent replicate on a disjoint key] D+ = {d_plus_m1!r}, "
                f"exact one-sided p = {p_m1!r}. Both replicates are reported; neither is averaged "
                f"into the other.")

    mix_peeking = frame_validity[(frame_validity["arm"] == "MIX")
                                 & (frame_validity["stopping_protocol"] == "peeking")]
    for row in mix_peeking.itertuples(index=False):
        logger.info(f"C3 DESCRIPTIVE [MIX peeking alpha={row.alpha}] FPR = {row.FPR!r}, "
                    f"FPR/alpha = {row.FPR / row.alpha:.4f}, exact one-sided binomial p = "
                    f"{row.binom_p_one_sided!r}. Persisted in R09_validity_stopping.csv; NOT an "
                    f"acceptance criterion (S4bis point 3).")
    for a in ALPHAS:
        fpr_m1 = float(np.mean(campaign["m1_first_alarm"][a] <= T_EXT))
        low, high = wilson_ci(int(np.sum(campaign["m1_first_alarm"][a] <= T_EXT)), N_NULL)
        logger.info(f"M1(ii) alpha={a}: FPR anytime over T_EXT = {fpr_m1:.4f} (Wilson CI: "
                    f"[{low:.4f}, {high:.4f}]), ratio to alpha {fpr_m1 / a:.4f}. Reported; the "
                    f"delivered gate `if fpr > a + 0.005` is removed -- 0.005 is derived from "
                    f"nothing -- and C3 replaces it.")

    ordered_cal = np.sort(campaign["max_M_cal"])
    peek = campaign["running_max"]["CUSUM"]
    u_cusum = (N_CAL - np.searchsorted(ordered_cal, peek, side='left')) / N_CAL
    d_plus_cusum = one_sided_ks_dplus(u_cusum)
    p_cusum = float(stats.ksone.sf(d_plus_cusum, N_NULL))
    logger.info(f"C3 NEGATIVE CONTROL [CUSUM] D+ = {d_plus_cusum!r} on n = {N_NULL}, nominal "
                f"exact one-sided p = {p_cusum!r}. The statistic must reject decisively, and it "
                f"is what establishes the instrument has power against the alternative it is used "
                f"on. Two caveats travel with it and neither is repaired: U_cusum is read off an "
                f"ESTIMATED survival function on N_CAL = {N_CAL} draws, which carries the double "
                f"variance of S4bis's second corollary, and the CUSUM statistic lives on a lattice "
                f"so U_cusum has heavy ties, under which the ksone tail is not exact. The effect "
                f"size dwarfs both; this direction is a control on power, not an acceptance gate.")

    fired = p_value < GATE_LEVEL
    if fired:
        logger.error(f"C3 GATE FIRED on the MIX arm: D+ = {d_plus!r}, p = {p_value!r} < "
                     f"{GATE_LEVEL}. Ville's bound is not respected uniformly over the level "
                     f"range. Under the plan's halt condition this is a D3: no parameter, "
                     f"tolerance, seed or bound is moved.")
    return {"d_plus_mix": d_plus, "p_mix": p_value, "d_plus_m1": d_plus_m1, "p_m1": p_m1,
            "d_plus_cusum": d_plus_cusum, "p_cusum": p_cusum, "fired": fired}


def control_c4(campaign, frame_race, frame_control, logger):
    """
    C4. Per arm, a one-sided Spearman of ADD against eta with its exact
    permutation null; then the matched-detection-rate quantile that is the
    primary instrument for the conditioning confounder, with its paired
    bootstrap; then the common-detection paired difference as a second reading.
    """
    perms = permutation_matrix(len(ETAS))
    logger.info(f"C4 exact permutation null materialised: {perms.shape[0]} permutations of "
                f"{perms.shape[1]} grid points.")

    frames = {arm: frame_race[frame_race["arm"] == arm] for arm in PUBLISHED_H1_ARMS}
    if frame_control is not None:
        frames[CONTROL_H1_ARM] = frame_control
    spearman = {}
    for arm, frame in frames.items():
        cell = frame[np.isclose(frame["alpha"].to_numpy(dtype=float), FIGURE_ALPHA,
                                rtol=0.0, atol=0.0)].sort_values("eta")
        add = cell["ADD"].to_numpy(dtype=float)
        sem = cell["SEM"].to_numpy(dtype=float)
        det = cell["DetRate"].to_numpy(dtype=float)
        grid = cell["eta"].to_numpy(dtype=float)
        rho, p_less, p_greater, ties = exact_spearman(add, grid, perms)
        rho_d, pd_less, pd_greater, ties_d = exact_spearman(det, grid, perms)
        slope, slope_se = weighted_least_squares_slope(grid, add, sem)
        verdict = "monotone decrease" if p_less < GATE_LEVEL else "NOT RESOLVED at the gate level"
        logger.info(f"C4 [{arm}, alpha={FIGURE_ALPHA}] ADD vs eta: Spearman rho = {rho!r}, exact "
                    f"one-sided p (decreasing) = {p_less!r} over {perms.shape[0]} permutations, "
                    f"{ties} tied ADD values. Gate at {GATE_LEVEL}: {verdict}. Weighted "
                    f"least-squares slope = {slope!r} steps per unit eta, SE {slope_se!r}.")
        logger.info(f"C4 [{arm}, alpha={FIGURE_ALPHA}] DetRate vs eta: Spearman rho = {rho_d!r}, "
                    f"exact one-sided p (increasing) = {pd_greater!r}, {ties_d} tied rates. "
                    f"Reported, not gated.")
        margins = []
        for j in range(len(grid) - 1):
            diff = add[j] - add[j + 1]
            se = math.sqrt(sem[j]**2 + sem[j + 1]**2)
            margins.append(f"eta {grid[j]:.2f}->{grid[j + 1]:.2f}: dADD = {diff:+.2f}, "
                           f"SE {se:.2f}, z = {diff / se:+.2f}")
        logger.info(f"C4 [{arm}] nine adjacent z-margins, DESCRIPTIVE and gating nothing: "
                    + "; ".join(margins))
        spearman[arm] = {"rho": rho, "p_less": p_less, "ties": ties, "slope": slope,
                         "slope_se": slope_se, "rho_det": rho_d, "p_det_greater": pd_greater,
                         "fired": p_less >= GATE_LEVEL}
        if p_less >= GATE_LEVEL:
            logger.error(f"C4 GATE NOT MET on {arm}: the exact one-sided p for a decreasing ADD "
                         f"is {p_less!r} at the {GATE_LEVEL} level. An arm whose delay does not "
                         f"respond to the drift amplitude is not slow, it is blind. This is "
                         f"reported in full; no parameter, seed or threshold is moved to make it "
                         f"decrease.")

    boot_index = rng_for("R09", "c4_matched_rate_bootstrap").integers(
        0, N_ALT, size=(C4_BOOTSTRAP_REPLICATES, N_ALT))
    matched = []
    for eta in ETAS:
        delays = {}
        detected = {}
        for arm in PUBLISHED_H1_ARMS:
            fa = campaign["h1_alarm"][(arm, FIGURE_ALPHA, eta)]
            valid = (fa > TAU) & (fa <= H)
            d = np.where(valid, fa - TAU, np.inf)
            delays[arm] = d
            detected[arm] = valid
        rates = {arm: float(np.mean(detected[arm])) for arm in PUBLISHED_H1_ARMS}
        q = min(rates.values())
        quantiles = {arm: empirical_quantile(delays[arm], q) for arm in PUBLISHED_H1_ARMS}
        gap = quantiles["MIX"] - quantiles["CUSUM"]

        boot = np.empty(C4_BOOTSTRAP_REPLICATES)
        for b in range(C4_BOOTSTRAP_REPLICATES):
            idx = boot_index[b]
            rb = {arm: float(np.mean(detected[arm][idx])) for arm in PUBLISHED_H1_ARMS}
            qb = min(rb.values())
            boot[b] = (empirical_quantile(delays["MIX"][idx], qb)
                       - empirical_quantile(delays["CUSUM"][idx], qb))
        low = float(np.quantile(boot, C4_BOOTSTRAP_LEVEL / 2))
        high = float(np.quantile(boot, 1 - C4_BOOTSTRAP_LEVEL / 2))

        both = detected["CUSUM"] & detected["MIX"]
        n_both = int(np.sum(both))
        paired = delays["MIX"][both] - delays["CUSUM"][both]
        paired_mean = float(np.mean(paired)) if n_both > 0 else float('nan')
        paired_se = float(np.std(paired) / math.sqrt(n_both)) if n_both > 0 else float('nan')
        sem_c = (float(np.std(delays["CUSUM"][detected["CUSUM"]])
                       / math.sqrt(int(np.sum(detected["CUSUM"]))))
                 if np.any(detected["CUSUM"]) else float('nan'))
        sem_m = (float(np.std(delays["MIX"][detected["MIX"]])
                       / math.sqrt(int(np.sum(detected["MIX"]))))
                 if np.any(detected["MIX"]) else float('nan'))
        unpaired_se = math.sqrt(sem_c**2 + sem_m**2)
        deff = (paired_se / unpaired_se)**2 if unpaired_se > 0 else float('nan')
        corr = (float(np.corrcoef(delays["CUSUM"][both], delays["MIX"][both])[0, 1])
                if n_both > 1 else float('nan'))
        matched.append({
            "eta": eta, "rate_cusum": rates["CUSUM"], "rate_mix": rates["MIX"], "q": q,
            "quantile_cusum": quantiles["CUSUM"], "quantile_mix": quantiles["MIX"],
            "gap": gap, "boot_low": low, "boot_high": high,
            "n_common": n_both, "paired_mean": paired_mean, "paired_se": paired_se,
            "unpaired_se": unpaired_se, "design_effect": deff, "paired_corr": corr,
        })
        logger.info(f"C4 MATCHED-RATE QUANTILE [alpha={FIGURE_ALPHA}, eta={eta}] q = "
                    f"min({rates['CUSUM']:.4f}, {rates['MIX']:.4f}) = {q:.4f}; CUSUM q-quantile "
                    f"of the delay = {quantiles['CUSUM']!r}, MIX = {quantiles['MIX']!r}, "
                    f"MIX - CUSUM = {gap!r} with a paired bootstrap "
                    f"{1 - C4_BOOTSTRAP_LEVEL:.0%} interval [{low!r}, {high!r}] over "
                    f"{C4_BOOTSTRAP_REPLICATES} resamples of the {N_ALT} trajectory indices. "
                    f"Non-detections are placed at +inf and the comparison conditions on nothing.")
        logger.info(f"C4 SECOND READING [eta={eta}] common-detection subset: {n_both} of {N_ALT} "
                    f"streams detected by BOTH arms; paired mean ADD_MIX - ADD_CUSUM = "
                    f"{paired_mean!r}, paired SE {paired_se!r} against an unpaired SE of "
                    f"{unpaired_se!r}, Kish design effect (paired variance over unpaired variance) "
                    f"= {deff!r}, within-pair correlation {corr!r}. The subset is the intersection "
                    f"of two detection events whose rates differ, so it is itself a selected "
                    f"sample; it gates nothing.")

    halt = []
    for entry in matched:
        if entry["eta"] in C4_HALT_ETAS and entry["gap"] > 0 and entry["boot_low"] > 0:
            halt.append(entry)
    if halt:
        logger.error(f"C4 HALT CONDITION MET at eta {[e['eta'] for e in halt]}: MIX's "
                     f"matched-detection-rate quantile is STRICTLY ABOVE CUSUM's with its paired "
                     f"bootstrap interval excluding zero. A printed qualitative claim of v87 is "
                     f"contradicted. This is a D3: full report, no parameter, tolerance, seed or "
                     f"bound moved.")
    else:
        logger.info(f"C4 HALT CONDITION NOT MET. At eta in {C4_HALT_ETAS} the matched-rate "
                    f"quantile does not place MIX strictly above CUSUM with an interval excluding "
                    f"zero, so a marginal ADD reversal at those points is an artefact of "
                    f"conditioning on detection and is recorded under `R09-add-conditioning` with "
                    f"no severity.")
    return {"spearman": spearman, "matched": matched, "halt": halt}


def control_cross_check(campaign, logger):
    """
    The structural cross-check of the plan's section 4.2, whose trigger
    probability is zero: mean(first_alarm[a] <= T_EXT) must EQUAL
    mean(running_max >= threshold(a)) exactly, arm by arm and level by level,
    because the running maximum is taken over exactly the statistic the alarm
    rule reads.
    """
    checked = 0
    for arm in ARMS_H0:
        for a in ALPHAS:
            threshold = campaign["lambda_star"][a] if arm == "CUSUM" else -np.log(a)
            by_alarm = campaign["first_alarm"][arm][a] <= T_EXT
            by_max = campaign["running_max"][arm] >= threshold
            if not np.array_equal(by_alarm, by_max):
                logger.error(f"CROSS-CHECK FAILED [{arm} alpha={a}]: the alarm indicator and the "
                             f"running-maximum indicator disagree on "
                             f"{int(np.sum(by_alarm != by_max))} of {N_NULL} streams. The two are "
                             f"the same event by construction; a difference means the running "
                             f"maximum is not taken over the statistic the rule reads.")
                sys.exit(1)
            checked += 1
    logger.info(f"CROSS-CHECK: {checked} (arm, alpha) cells -- the first-alarm indicator over "
                f"[1, T_EXT] and the running-maximum indicator are IDENTICAL stream by stream on "
                f"all {N_NULL} streams. Deterministic; trigger probability 0.")


def control_calibration_coherence(campaign, frame_level, logger):
    """
    The gate that replaces the delivered controls (b) and (e), with the variance
    of the ESTIMATED threshold carried (S4bis, second corollary).
    """
    achieved_h0 = float(frame_level[(frame_level["arm"] == "CUSUM")
                                    & np.isclose(frame_level["alpha"].to_numpy(dtype=float),
                                                 FIGURE_ALPHA, rtol=0.0, atol=0.0)
                                    ].iloc[0]["achieved_level"])
    calib = campaign["actual_level"][FIGURE_ALPHA]
    se = math.sqrt(FIGURE_ALPHA * (1 - FIGURE_ALPHA) * (1 / N_NULL + 1 / N_CAL))
    z = float(stats.norm.ppf(1 - COHERENCE_LEVEL / 2))
    tolerance = z * se
    gap = abs(achieved_h0 - calib)
    logger.info(f"CALIBRATION COHERENCE at alpha = {FIGURE_ALPHA}: lambda_star = "
                f"{campaign['lambda_star'][FIGURE_ALPHA]!r}, calibration level on N_CAL = "
                f"{calib!r}, H0 level over [1, H] on N_NULL = {achieved_h0!r}, gap = {gap:.6f} "
                f"against a tolerance of {tolerance:.6f} = {z:.4f} x {se:.6f}. The SE carries the "
                f"variance of the estimated threshold; the delivered (e) used "
                f"{math.sqrt(FIGURE_ALPHA * (1 - FIGURE_ALPHA) / N_NULL):.6f} and understated it "
                f"by a factor {se / math.sqrt(FIGURE_ALPHA * (1 - FIGURE_ALPHA) / N_NULL):.4f}. "
                f"Gap in SE units: {gap / se:.3f}. Trigger probability under its own null: "
                f"{COHERENCE_LEVEL}.")
    if gap > tolerance:
        logger.error(f"CALIBRATION COHERENCE FAILED: the H0 level at the calibrated threshold is "
                     f"{gap / se:.3f} SE from the calibration level. The threshold and the "
                     f"campaign do not describe the same rule.")
        sys.exit(1)


def report_delivered_diagnostics(campaign, frame_validity, logger):
    """
    The delivered controls (c) and (d), computed and REPORTED rather than gated,
    and the direction of the race that v87's panel A states.

    (d) is v87's own printed claim -- "Only MIX controls the time-uniform
    false-alarm probability" -- so a sign inversion would be a D3 and is
    reported as one. (c)'s literal floor of 0.80 is derived from nothing and is
    not carried as a gate; the quantity it reads is logged with its interval.
    """
    peeking = frame_validity[frame_validity["stopping_protocol"] == "peeking"]
    ecusum = peeking[(peeking["arm"] == "eCUSUM")
                     & np.isclose(peeking["alpha"].to_numpy(dtype=float), FIGURE_ALPHA,
                                  rtol=0.0, atol=0.0)].iloc[0]
    logger.info(f"DELIVERED CONTROL (c), REPORTED NOT GATED: e-CUSUM peeking FPR over "
                f"[1, T_EXT] at alpha = {FIGURE_ALPHA} is {ecusum['FPR']!r} (Wilson "
                f"[{ecusum['CI_low']!r}, {ecusum['CI_high']!r}]). The delivered floor of 0.80 is "
                f"derived from nothing and is not carried as a gate; the quantity is what v87's "
                f"panel A shows for the e-CUSUM bar and it is reported with its interval.")
    inversions = []
    for a in ALPHAS:
        row_c = peeking[(peeking["arm"] == "CUSUM")
                        & np.isclose(peeking["alpha"].to_numpy(dtype=float), a,
                                     rtol=0.0, atol=0.0)].iloc[0]
        row_m = peeking[(peeking["arm"] == "MIX")
                        & np.isclose(peeking["alpha"].to_numpy(dtype=float), a,
                                     rtol=0.0, atol=0.0)].iloc[0]
        both = campaign["running_max"]
        ind_c = (both["CUSUM"] >= campaign["lambda_star"][a]).astype(float)
        ind_m = (both["MIX"] >= -np.log(a)).astype(float)
        diff = ind_c - ind_m
        se = float(np.std(diff) / math.sqrt(N_NULL))
        z = float(np.mean(diff) / se) if se > 0 else float('inf')
        logger.info(f"DELIVERED CONTROL (d) [alpha={a}] CUSUM peeking FPR {row_c['FPR']!r} vs MIX "
                    f"{row_m['FPR']!r}; PAIRED difference {float(np.mean(diff))!r} on the same "
                    f"{N_NULL} streams, paired SE {se!r}, z = {z:.2f}. v87's panel A prints 'Only "
                    f"MIX controls the time-uniform false-alarm probability'; an inversion here "
                    f"would falsify it and would be a D3.")
        if row_c["FPR"] <= row_m["FPR"]:
            inversions.append(a)
    if inversions:
        logger.error(f"DELIVERED CONTROL (d): the CUSUM peeking rate is at or below the MIX one at "
                     f"alpha {inversions}. v87's 'Only MIX controls the time-uniform false-alarm "
                     f"probability' is contradicted. D3; no parameter moved.")
    else:
        logger.info(f"DELIVERED CONTROL (d): the CUSUM peeking rate exceeds the MIX one at all "
                    f"{len(ALPHAS)} levels; the direction v87's panel A states holds.")


def report_cusum_lattice(campaign, logger):
    """
    The lattice on which the CUSUM statistic lives, measured rather than
    asserted. `dev - DELTA_CUSUM` takes +0.4 or -0.6, so max_M sits on a 0.2
    lattice up to floating-point accumulation, lambda_star moves in discrete
    steps, and the nominal level is not exactly attainable -- the
    `level_is_attainable = False` column and the `R03-cusum-nominal-level`
    precedent.

    Returns the vector of attainable levels of the calibration sample.
    """
    max_M = campaign["max_M_cal"]
    step = 2 * DELTA_CUSUM
    units = max_M / step
    drift = float(np.max(np.abs(units - np.round(units))))
    ordered = np.sort(max_M)
    support = np.unique(ordered)
    levels = (N_CAL - np.searchsorted(ordered, support, side='left')) / N_CAL
    logger.info(f"CUSUM LATTICE. The increment `dev - DELTA_CUSUM` takes +{0.5 - DELTA_CUSUM} or "
                f"-{0.5 + DELTA_CUSUM}, so max_M lives on a {step} lattice; measured over the "
                f"{N_CAL} calibration streams, the largest distance from a lattice point is "
                f"{drift:.3e} in lattice units, i.e. floating-point accumulation and not a second "
                f"support. {len(support)} distinct values are realised, giving {len(support)} "
                f"attainable levels.")
    for a in ALPHAS:
        at_or_below = levels[levels <= a]
        above = levels[levels > a]
        logger.info(f"CUSUM LATTICE [alpha={a}] nearest attainable levels: "
                    f"{float(at_or_below.max()) if len(at_or_below) else float('nan'):.6f} at or "
                    f"below, {float(above.min()) if len(above) else float('nan'):.6f} above; "
                    f"alpha itself attainable exactly: {bool(np.any(levels == a))}.")
    return levels


# --- FIGURE ---

def render_figure(frame_validity, frame_race, frame_arl0, path, logger):
    """
    v87 Figure 9, three panels, drawn from the in-memory frames.

    Cosmetic divergence from the submitted Fig27_Eprocess_AnytimeValid.png,
    declared per preamble S6 and covered by the `ALL-figure-presentation`
    register row: bold lettered panel titles, an explicit sample size on each
    panel's axis, and the censoring markers of panel C. No numerical value moves
    on that account.
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.4), dpi=300)
    colours = {"CUSUM": '#1f77b4', "MIX": '#ff7f0e', "eCUSUM": '#2ca02c'}

    # --- (A) realized false-alarm rate under three stopping protocols ---
    ax = axes[0]
    cell = frame_validity[np.isclose(frame_validity["alpha"].to_numpy(dtype=float), FIGURE_ALPHA,
                                     rtol=0.0, atol=0.0)]
    protocols = [name for name, _, _ in STOPPING_PROTOCOLS]
    x = np.arange(len(protocols))
    width = 0.25
    for arm, offset in zip(ARMS_H0, (-width, 0.0, width)):
        values, err_low, err_high = [], [], []
        for name in protocols:
            row = cell[(cell["arm"] == arm) & (cell["stopping_protocol"] == name)].iloc[0]
            values.append(row["FPR"])
            err_low.append(max(0.0, row["FPR"] - row["CI_low"]))
            err_high.append(max(0.0, row["CI_high"] - row["FPR"]))
        ax.bar(x + offset, values, width, label=arm, yerr=[err_low, err_high], capsize=4,
               color=colours[arm])
    ax.axhline(FIGURE_ALPHA, color='k', linestyle='--', linewidth=1.4,
               label=rf"nominal $\alpha = {FIGURE_ALPHA}$")
    ax.set_xticks(x)
    ax.set_xticklabels(protocols)
    ax.set_xlabel(f"stopping protocol  ($n = {N_NULL}$ fair-coin streams per bar,\n"
                  f"Wilson 95% intervals)")
    ax.set_ylabel(r"realized false-alarm rate")
    ax.set_title(rf"(A) Continuous monitoring over $[1, 4H]$ at $\alpha = {FIGURE_ALPHA}$",
                 fontweight="bold", loc="center")
    ax.legend(fontsize=9)
    ax.grid(True, axis='y', ls='-', alpha=0.2)

    # --- (B) detection delay against drift ---
    ax = axes[1]
    race = frame_race[np.isclose(frame_race["alpha"].to_numpy(dtype=float), FIGURE_ALPHA,
                                 rtol=0.0, atol=0.0)]
    for arm in PUBLISHED_H1_ARMS:
        sub = race[race["arm"] == arm].sort_values("eta")
        ax.errorbar(sub["eta"], sub["ADD"], yerr=sub["SEM"], fmt='-o', label=arm,
                    color=colours[arm], capsize=4, linewidth=2)
    ax.set_xlabel(rf"drift $\eta$  ($n = {N_ALT}$ drift streams per cell, error bars = SEM)")
    ax.set_ylabel(r"detection delay ADD (steps)")
    ax.set_title(rf"(B) Detection delay vs. drift at $\alpha = {FIGURE_ALPHA}$",
                 fontweight="bold", loc="center")
    ax.legend(fontsize=9)
    ax.grid(True, ls='-', alpha=0.2)
    ax.annotate(rf"ADD is conditional on an alarm in $({TAU}, {H}]$;"
                "\n"
                r"the detection rate on the same row is in the CSV.",
                xy=(0.98, 0.96), xycoords='axes fraction', ha='right', va='top', fontsize=8)

    # --- (C) average run length against level, with the censoring made visible ---
    ax = axes[2]
    for arm in ARMS_H0:
        sub = frame_arl0[frame_arl0["arm"] == arm].sort_values("alpha")
        censored = sub["censored_frac"].to_numpy(dtype=float) > MACRO_CENSORING_CEILING
        if censored.any():
            ax.plot(sub["alpha"], sub["ARL0_mean"], linestyle='--', linewidth=1.4, alpha=0.55,
                    color=colours[arm], marker='o', markerfacecolor='none', markersize=7,
                    label=f"{arm}  ({100 * sub['censored_frac'].min():.1f}"
                          f"-{100 * sub['censored_frac'].max():.1f}% right-censored)")
        else:
            ax.plot(sub["alpha"], sub["ARL0_mean"], linestyle='-', linewidth=2, color=colours[arm],
                    marker='o', markersize=6, label=arm)
    grid = np.array(sorted(ALPHAS))
    ax.plot(grid, 1.0 / grid, 'k--', linewidth=1.4, label=r"$1/\alpha$")
    ax.axhline(T_EXT, color='0.35', linestyle=':', linewidth=1.8,
               label=rf"simulation horizon $4H = {T_EXT}$ -- right-censoring ceiling")
    ax.plot([], [], color='0.35', marker='o', markerfacecolor='none', linestyle='--', alpha=0.55,
            label=f"hollow: >{MACRO_CENSORING_CEILING:.0%} right-censored (horizon artefact)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(grid)
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_xlabel(rf"nominal level $\alpha$  ($n = {N_NULL}$ fair-coin streams per point)")
    ax.set_ylabel(r"$\mathrm{ARL}_0$ (steps)")
    ax.set_title(r"(C) Average run length vs. level", fontweight="bold", loc="center")
    ax.legend(fontsize=7.5, loc="lower left")
    ax.grid(True, which="both", ls='-', alpha=0.2)

    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    logger.info(f"Figure 9 written to {path.name}: three panels drawn from the in-memory frames. "
                f"Panel C makes the censoring visible, which is R09 prompt section 2.2's actual "
                f"requirement -- a horizontal rule at the simulation horizon T_EXT = {T_EXT}, "
                f"hollow markers and a lighter dashed line for every arm above "
                f"{MACRO_CENSORING_CEILING:.0%} right-censoring, the per-arm censoring range in "
                f"the legend entry, and a legend line naming the convention. Cosmetic divergence "
                f"from the submitted Fig27_Eprocess_AnytimeValid.png, per preamble S6 and the "
                f"`ALL-figure-presentation` register row: bold lettered panel titles, per-panel "
                f"sample sizes on the axes, and the censoring markers. No numerical value moves on "
                f"that account.")


# --- MACROS ---

def emit_macros(logger, path, frame_validity, frame_race, frame_arl0, grid_max):
    """
    Exactly seven macros, each computed from an object in memory. Cardinal
    prefix \\RNine per preamble S6's ordinal-in-English rule.

    Section 2.3 of the R09 prompt is enforced HERE, in code: the emitter refuses
    to emit any ARL0-derived macro whose source row carries a censored fraction
    above 0.5, and exits 1. Under the published configuration it never fires --
    only e-CUSUM's ARL0 is emitted -- but the guard is the mechanism.
    """
    cell = frame_validity[np.isclose(frame_validity["alpha"].to_numpy(dtype=float), FIGURE_ALPHA,
                                     rtol=0.0, atol=0.0)]
    cusum_peeking_max = float(cell[cell["arm"] == "CUSUM"]["FPR"].max())
    mix_peeking_max = float(cell[cell["arm"] == "MIX"]["FPR"].max())

    race = frame_race[np.isclose(frame_race["alpha"].to_numpy(dtype=float), FIGURE_ALPHA,
                                 rtol=0.0, atol=0.0)]
    add_cusum = race[race["arm"] == "CUSUM"].set_index("eta")["ADD"]
    add_mix = race[race["arm"] == "MIX"].set_index("eta")["ADD"]
    parity = [eta for eta in ETAS if add_mix.loc[eta] <= add_cusum.loc[eta]]
    parity_threshold = max(parity) if parity else float('nan')

    ecusum = frame_arl0[frame_arl0["arm"] == "eCUSUM"]
    arl0_row = ecusum.loc[ecusum["ARL0_mean"].idxmin()]
    if float(arl0_row["censored_frac"]) > MACRO_CENSORING_CEILING:
        logger.error(f"MACRO EMITTER REFUSED: \\RNineEcusumArlZeroMin would be read from a row "
                     f"whose censored fraction is {arl0_row['censored_frac']!r}, above the "
                     f"{MACRO_CENSORING_CEILING} ceiling R09 prompt section 2.3 fixes. An ARL0 "
                     f"mean over a right-censored sample is a horizon artefact and must not reach "
                     f"the manuscript.")
        sys.exit(1)
    censored_max = {arm: float(frame_arl0[frame_arl0["arm"] == arm]["censored_frac"].max())
                    for arm in ARMS_H0}

    macros = [
        MACRO_HEADER,
        "% EVERY VALUE BELOW IS COMPUTED FROM AN OBJECT IN MEMORY. The source frame and the",
        "% operating point of each are named here because v87's Figure 9 caption names neither.",
        "% \\RNineCusumPeekingFprMax and \\RNineMixPeekingFprMax are the MAXIMUM OVER THE THREE",
        f"%   STOPPING PROTOCOLS at the figure's operating point alpha = {FIGURE_ALPHA}, which is",
        "%   the tallest bar of each arm in panel A and is exactly what 'climbs to 18%' names.",
        "%   They are NOT a maximum over the alpha grid: CUSUM's peeking rate reaches",
        f"%   {grid_max['CUSUM']:.5f} at alpha = {grid_max['CUSUM_alpha']} and MIX's",
        f"%   {grid_max['MIX']:.5f} at alpha = {grid_max['MIX_alpha']}. Peeking dominates nominal",
        "%   and extended BY CONSTRUCTION -- {fa <= H} and {cross at T_EXT} are both subsets of",
        "%   {fa <= T_EXT} -- so the maximum is always the peeking bar. Structural, not empirical.",
        "% \\RNineMixDriftParityThreshold is the largest eta on the grid with ADD_MIX <= ADD_CUSUM",
        f"%   at alpha = {FIGURE_ALPHA}. It is a KNIFE-EDGE OVER A GRID: the paired difference and",
        "%   paired SE at every eta, and the z of the first non-parity point, are in the log and",
        "%   in AUDIT_R09.md. S4bis's fourth corollary applies -- an extremum over a grid needs",
        "%   its own null, supplied here by a paired bootstrap over streams.",
        "% \\RNineEcusumArlZeroMin is the minimum over the seven alpha of e-CUSUM's ARL0_mean, at",
        f"%   alpha = {arl0_row['alpha']}, and it is emitted only because its source row carries a",
        f"%   censored fraction of {arl0_row['censored_frac']!r}, at or below the",
        f"%   {MACRO_CENSORING_CEILING} ceiling. No CUSUM or MIX ARL0 is macro-emitted: those",
        "%   means are horizon artefacts at 65-99% right-censoring.",
        "% The three censored-fraction macros exist so that a reader of the caption can price the",
        "%   ARL0 curves of panel C without opening the CSV.",
        f"\\newcommand{{\\RNineCusumPeekingFprMax}}{{{100.0 * cusum_peeking_max:.1f}\\%}}",
        f"\\newcommand{{\\RNineMixPeekingFprMax}}{{{100.0 * mix_peeking_max:.1f}\\%}}",
        f"\\newcommand{{\\RNineMixDriftParityThreshold}}{{{parity_threshold:.2f}}}",
        f"\\newcommand{{\\RNineEcusumArlZeroMin}}{{{float(arl0_row['ARL0_mean']):.2f}}}",
        f"\\newcommand{{\\RNineEcusumCensoredFracMax}}{{{censored_max['eCUSUM']:.4f}}}",
        f"\\newcommand{{\\RNineCusumCensoredFracMax}}{{{censored_max['CUSUM']:.4f}}}",
        f"\\newcommand{{\\RNineMixCensoredFracMax}}{{{censored_max['MIX']:.4f}}}",
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
    logger.info(f"Emitted {emitted} macros to {path.name}, prefix \\RNine per preamble S6's "
                f"ordinal-in-English rule; \\RNinth appears nowhere. The section 2.3 guard was "
                f"evaluated on the one ARL0-derived macro and its trigger probability under the "
                f"published configuration is 0: e-CUSUM's censored fraction never exceeds "
                f"{censored_max['eCUSUM']!r}.")
    logger.info(f"\\RNineEcusumCensoredFracMax = {censored_max['eCUSUM']!r} CONTRADICTS the R09 "
                f"prompt's parenthetical '(0 expected)' and its section 2 'against 0.0000 for "
                f"eCUSUM': the submitted `protocol_22d` itself carries 0.0006 at alpha = 0.01. "
                f"Reported in AUDIT_R09.md under findings that revise the prompt's premises. No "
                f"manuscript claim is affected -- v87 prints no censored fraction.")
    return macros


# --- DEVIATION CLASSIFICATION (S3) ---

def classify_against_witness(logger, frame_validity, frame_race, frame_level, frame_arl0):
    """
    The D0-D3 classification of preamble S3, computed rather than asserted, at
    v87's own printing precision. The witness CSVs are read with
    `float_precision='round_trip'` on both sides and no literal is transcribed
    by hand. This replaces the three delivered literal gates at `Priorite_22`
    l.619 and l.631, which are self-anchored equality tests at machine precision
    on Monte-Carlo values and which the 128-bit re-keying redraws by
    construction.
    """
    reference = BASE_DIR / "data" / "reference" / "R09"
    witness = {key: pd.read_csv(reference / name, float_precision='round_trip')
               for key, name in WITNESS_CSV.items()}

    def cell(frame, **conditions):
        mask = np.ones(len(frame), dtype=bool)
        for column, value in conditions.items():
            column_values = frame[column].to_numpy()
            if isinstance(value, float):
                mask &= np.isclose(column_values.astype(float), value, rtol=1e-12, atol=1e-15)
            else:
                mask &= (column_values == value)
        return frame[mask].iloc[0]

    logger.info("=" * 78)
    logger.info("DEVIATION CLASSIFICATION D0-D3 (preamble S3), AT v87'S PRINTING PRECISION")
    logger.info("=" * 78)
    rows = []

    new = cell(frame_validity, arm="CUSUM", alpha=FIGURE_ALPHA, stopping_protocol="peeking")
    old = cell(witness["validity_stopping"], arm="CUSUM", alpha=FIGURE_ALPHA,
               stopping_protocol="peeking")
    rows.append(("L243 / Fig. 9(A) CUSUM peeking FPR", r"18\%",
                 f"{100 * new['FPR']:.0f}%", f"{100 * old['FPR']:.0f}%",
                 f"{new['FPR']!r}", f"{old['FPR']!r}",
                 "R09_validity_stopping.csv, CUSUM / 0.05 / peeking / FPR",
                 "D1" if f"{100 * new['FPR']:.0f}" == "18" else "D2"))

    new = cell(frame_level, arm="CUSUM", alpha=FIGURE_ALPHA)
    old = cell(witness["level_granularity"], arm="CUSUM", alpha=FIGURE_ALPHA)
    rows.append(("L243 CUSUM calibrated to 5% at H", r"5\%",
                 f"{100 * new['achieved_level']:.0f}%", f"{100 * old['achieved_level']:.0f}%",
                 f"{new['achieved_level']!r}", f"{old['achieved_level']!r}",
                 "R09_level_granularity.csv, CUSUM / 0.05 / achieved_level",
                 "D1" if f"{100 * new['achieved_level']:.0f}" == "5" else "D2"))

    for arm, printed in (("MIX", "409"), ("CUSUM", "539")):
        new = cell(frame_race, arm=arm, alpha=FIGURE_ALPHA, eta=FIGURE_ETA)
        old = cell(witness["eprocess_race"], arm=arm, alpha=FIGURE_ALPHA, eta=FIGURE_ETA)
        rows.append((f"L243 {arm} ADD at eta = 0.10", printed,
                     f"{new['ADD']:.0f}", f"{old['ADD']:.0f}",
                     f"{new['ADD']!r}", f"{old['ADD']!r}",
                     f"R09_eprocess_race.csv, {arm} / 0.05 / 0.10 / ADD",
                     "D1" if f"{new['ADD']:.0f}" == printed else "D2"))

    witness_streams = int(witness["validity_stopping"]["N_streams"].iloc[0])
    rows.append(("L243/L559 fair-coin streams per level", r"$2\times10^4$",
                 f"{N_NULL}", f"{witness_streams}", f"{N_NULL}", f"{witness_streams}",
                 "N_NULL, the H0 arm of panels A and C",
                 "D0" if N_NULL == witness_streams == 20000 else "D2"))

    logger.info(f"{'v87 site':<40} {'printed':<16} {'regenerated':<12} {'witness':<12} "
                f"{'class':<6} source cell")
    for label, printed, regen, wit, regen_raw, wit_raw, source, verdict in rows:
        logger.info(f"{label:<40} {printed:<16} {regen:<12} {wit:<12} {verdict:<6} {source}")
        logger.info(f"{'':<40} full float64: regenerated {regen_raw}, witness {wit_raw}")

    qualitative = []
    peeking = frame_validity[frame_validity["stopping_protocol"] == "peeking"]
    mix_peeking = peeking[peeking["arm"] == "MIX"]
    bounded = int(np.sum(mix_peeking["FPR"].to_numpy() <= mix_peeking["alpha"].to_numpy()))
    qualitative.append((r"L243/L559 MIX 'remains bounded by $\alpha$' under peeking",
                        f"{bounded} of {len(mix_peeking)} levels at or below alpha; ratios "
                        + ", ".join(f"{r.FPR / r.alpha:.3f}" for r in mix_peeking.itertuples()),
                        "holds" if bounded == len(mix_peeking) else "D3"))
    ecusum_arl0 = frame_arl0[frame_arl0["arm"] == "eCUSUM"]
    respected = int(np.sum(ecusum_arl0["arl0_bound_respected"].to_numpy()))
    ratios = ecusum_arl0["ARL0_mean"].to_numpy() / ecusum_arl0["ref_inv_alpha"].to_numpy()
    qualitative.append((r"L559 'e-CUSUM satisfies $\mathrm{ARL}_0 \ge 1/\alpha$'",
                        f"{respected} of {len(ecusum_arl0)} rows; minimum ratio "
                        f"{float(ratios.min()):.2f} at alpha = "
                        f"{float(ecusum_arl0.iloc[int(ratios.argmin())]['alpha'])}",
                        "holds" if respected == len(ecusum_arl0) else "D3"))
    order = []
    for a in ALPHAS:
        row_c = cell(peeking, arm="CUSUM", alpha=a)
        row_m = cell(peeking, arm="MIX", alpha=a)
        order.append(row_c["FPR"] > row_m["FPR"])
    qualitative.append((r"L559 'Only MIX controls the time-uniform false-alarm probability'",
                        f"CUSUM peeking exceeds MIX peeking at {int(np.sum(order))} of "
                        f"{len(ALPHAS)} levels; e-CUSUM peeking at alpha = 0.05 is "
                        f"{float(cell(peeking, arm='eCUSUM', alpha=FIGURE_ALPHA)['FPR']):.4f}",
                        "holds" if all(order) else "D3"))
    race = frame_race[np.isclose(frame_race["alpha"].to_numpy(dtype=float), FIGURE_ALPHA,
                                 rtol=0.0, atol=0.0)]
    add_c = race[race["arm"] == "CUSUM"].set_index("eta")["ADD"]
    add_m = race[race["arm"] == "MIX"].set_index("eta")["ADD"]
    faster = [eta for eta in ETAS if eta <= 0.10 and add_m.loc[eta] <= add_c.loc[eta]]
    qualitative.append((r"L559 'MIX matches CUSUM speed for moderate drifts ($\eta \le 0.10$)'",
                        f"MIX at or below CUSUM at eta {faster} of the five grid points at or "
                        f"below 0.10; the marginal ADD is conditional on detection and the "
                        f"matched-rate reading is control C4's",
                        "see C4"))
    for label, measured, verdict in qualitative:
        logger.info(f"QUALITATIVE {label}: {measured} -> {verdict}")
    logger.info("=" * 78)
    return rows, qualitative


# --- MAIN ---

def main():
    parser = argparse.ArgumentParser(
        description="R09 -- anytime-valid detection on the fair-coin stream (v87 Figure 9)")
    parser.add_argument("--n-jobs", type=int, default=NUM_CHUNKS,
                        help="Worker processes. NUM_CHUNKS is fixed at 10, so the chunk "
                             "decomposition -- and therefore every output -- is independent of "
                             "this value: that is the second reproducibility axis of control C6.")
    parser.add_argument("--control-arms", choices=("none", "ecusum"), default="none",
                        help="`ecusum` computes and persists the e-CUSUM H1 delay curve, which "
                             "reproduces nothing v87 prints, to "
                             "R09_eprocess_race_control_ecusum.csv. The branch is stamped in the "
                             "filename AND in the `arm` column (preamble S4.3). It consumes no "
                             "additional randomness, so the four published CSVs are byte-identical "
                             "with and without it.")
    args = parser.parse_args()
    with_control_arm = (args.control_arms == "ecusum")

    RESULTS_DIR = BASE_DIR / "results" / "R09_eprocess_anytime"
    DATA_DIR = RESULTS_DIR / "data"
    FIGURES_DIR = RESULTS_DIR / "figures"
    TABLES_DIR = RESULTS_DIR / "tables"
    LOGS_DIR = BASE_DIR / "logs" / "R09_eprocess_anytime"
    for directory in (DATA_DIR, FIGURES_DIR, TABLES_DIR, LOGS_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(LOGS_DIR / "exp_R09_eprocess_anytime.log", "exp_R09_eprocess_anytime")
    if not verify_hash_seed(logger):
        sys.exit(1)
    log_environment(logger, ["numpy", "pandas", "scipy", "matplotlib", "joblib", "pytest"])
    t0 = time.time()

    logger.info("R09 measures v87 Figure 9 (fig:anytime) and the paragraph at L243: what happens "
                "to a fixed-horizon sign-CUSUM when the monitoring does not stop at the horizon it "
                "was calibrated for, and what a mixture martingale delivers instead. Three arms -- "
                "CUSUM, MIX, e-CUSUM -- on 20,000 fair-coin streams over [1, 4H], seven nominal "
                "levels, and a 10-point drift grid on 2,000 drift streams per cell.")
    logger.info(f"N_ALT STAYS AT {N_ALT}. L243's 409 and 539 are themselves {N_ALT}-stream "
                f"measurements: `simulate_h1` loops on N_ALT and the delivered log line "
                f"'Control (g): ... ADD=409.11' is that loop's output. Raising N_ALT to "
                f"{N_NULL} would displace two printed numerals that the witness configuration "
                f"reproduces exactly, which is a self-inflicted D2 against the non-regression role "
                f"preamble S1 gives v87's results. L243's '2x10^4 fair-coin streams per level' "
                f"scopes 2e4 to the H0 arm, and a fair-coin stream is by definition an H0 stream. "
                f"The Figure 9 caption's '(2x10^4 streams per cell)' is IMPRECISE, NOT FALSE -- it "
                f"describes neither the calibration (N_CAL = {N_CAL}) nor panel B "
                f"(N_ALT = {N_ALT}) -- so the R09 prompt's perimeter filter keeps it out of "
                f"docs/DEVIATIONS.md and it is carried as a camera-ready candidate instead.")
    logger.info(f"RESOLUTION THAT DECISION BUYS, PANEL BY PANEL. Panels A and C carry Wilson "
                f"intervals at n = {N_NULL}; panel B carries SEMs at n = {N_ALT}, i.e. "
                f"sqrt({N_NULL}/{N_ALT}) = {math.sqrt(N_NULL / N_ALT):.2f}x wider for the same "
                f"underlying dispersion. Panel B's axis is labelled with its own n so the figure "
                f"is not read against the caption's single number.")
    logger.info(f"DRAW MECHANISM, A DELIBERATE CHANGE FROM THE WITNESS. Every Bernoulli draw is "
                f"`y_t = (rng.random(size) < p)` rather than `rng.binomial(1, p, size)`. Exact "
                f"Bernoulli either way, but with a threshold on a shared uniform two eta values "
                f"consume the IDENTICAL uniform stream and differ only where the threshold moves, "
                f"which makes the common-random-numbers plan structural rather than incidental. "
                f"`Generator.binomial`'s consumption pattern for n = 1 is an implementation detail "
                f"that must not be relied upon.")
    logger.info("ENTROPY. Keys carry ROLE AND INDEX ONLY, never alpha and never eta: "
                "('R09','m1_expectation'), ('R09','m1_ville',i), ('R09','cusum_calibration',i), "
                "('R09','h0',i), ('R09','h1_sides'), ('R09','h1',i), "
                "('R09','c4_matched_rate_bootstrap'). Because no key carries a process parameter, "
                "the same key serves every grid point: every comparison between arms at fixed "
                "(alpha, eta), and every comparison across eta and across alpha, is PAIRED. No "
                "pooled interval is published; the design effect of the one paired comparison "
                "control C4 reads is measured and logged beside it.")

    check_source_identity(logger)
    check_bound_flag_is_computed(logger)
    log_control_design(logger, args.n_jobs, with_control_arm)

    campaign = run_campaign(logger, args.n_jobs, with_control_arm)
    control_cross_check(campaign, logger)
    attainable_levels = report_cusum_lattice(campaign, logger)

    frame_validity = build_validity_stopping(campaign)
    frame_race = build_eprocess_race(campaign, PUBLISHED_H1_ARMS)
    frame_level = build_level_granularity(campaign, attainable_levels)
    frame_arl0 = build_arl0(campaign, logger)
    frame_control = (build_eprocess_race(campaign, (CONTROL_H1_ARM,)) if with_control_arm else None)

    control_c1(frame_arl0, logger)
    control_c2_report(frame_arl0, logger)
    control_calibration_coherence(campaign, frame_level, logger)
    c3 = control_c3(campaign, frame_validity, logger)
    c4 = control_c4(campaign, frame_race, frame_control, logger)
    report_delivered_diagnostics(campaign, frame_validity, logger)

    # The parity threshold is an extremum over a grid, so its own null travels
    # with it (S4bis, fourth corollary).
    race = frame_race[np.isclose(frame_race["alpha"].to_numpy(dtype=float), FIGURE_ALPHA,
                                 rtol=0.0, atol=0.0)]
    add_c = race[race["arm"] == "CUSUM"].set_index("eta")
    add_m = race[race["arm"] == "MIX"].set_index("eta")
    first_break = None
    for eta in ETAS:
        gap = float(add_m.loc[eta, "ADD"] - add_c.loc[eta, "ADD"])
        se = math.sqrt(float(add_m.loc[eta, "SEM"])**2 + float(add_c.loc[eta, "SEM"])**2)
        entry = next(e for e in c4["matched"] if e["eta"] == eta)
        logger.info(f"PARITY THRESHOLD [eta={eta}] ADD_MIX - ADD_CUSUM = {gap!r}, unpaired SE "
                    f"{se!r}, z = {gap / se:+.2f}; on the common-detection subset the PAIRED mean "
                    f"difference is {entry['paired_mean']!r} with paired SE {entry['paired_se']!r}"
                    f", design effect {entry['design_effect']!r}.")
        if first_break is None and gap > 0:
            first_break = (eta, gap, se)
    if first_break is not None:
        logger.info(f"PARITY THRESHOLD is a KNIFE-EDGE OVER A GRID. The first non-parity point is "
                    f"eta = {first_break[0]} at ADD_MIX - ADD_CUSUM = {first_break[1]!r}, "
                    f"z = {first_break[1] / first_break[2]:+.2f}. A redraw can move the threshold "
                    f"by one grid step; moving it UP leaves the caption's eta <= 0.10 true.")

    grid_max = {}
    peeking = frame_validity[frame_validity["stopping_protocol"] == "peeking"]
    for arm in ("CUSUM", "MIX"):
        sub = peeking[peeking["arm"] == arm]
        row = sub.loc[sub["FPR"].idxmax()]
        grid_max[arm] = float(row["FPR"])
        grid_max[f"{arm}_alpha"] = float(row["alpha"])
        logger.info(f"MACRO SCOPE [{arm}] the maximum peeking FPR over the WHOLE alpha grid is "
                    f"{row['FPR']!r} at alpha = {row['alpha']!r}, against "
                    f"{float(peeking[(peeking['arm'] == arm) & np.isclose(peeking['alpha'].to_numpy(dtype=float), FIGURE_ALPHA, rtol=0.0, atol=0.0)].iloc[0]['FPR'])!r}"
                    f" at the figure's operating point alpha = {FIGURE_ALPHA}. The macro binds the "
                    f"latter; the former is logged so the macro cannot be misread.")

    render_figure(frame_validity, frame_race, frame_arl0,
                  FIGURES_DIR / "fig09_anytime_valid.png", logger)
    emit_macros(logger, TABLES_DIR / "R09_claims.tex", frame_validity, frame_race, frame_arl0,
                grid_max)
    classify_against_witness(logger, frame_validity, frame_race, frame_level, frame_arl0)

    artefacts = {
        "R09_validity_stopping.csv": frame_validity,
        "R09_eprocess_race.csv": frame_race,
        "R09_level_granularity.csv": frame_level,
        "R09_arl0.csv": frame_arl0,
    }
    if with_control_arm:
        artefacts["R09_eprocess_race_control_ecusum.csv"] = frame_control
    for name, frame in artefacts.items():
        save_fair_csv(frame, DATA_DIR / name)
        logger.info(f"{name}: {len(frame)} rows, {len(frame.columns)} columns.")

    # The figure and the macros are computed from the in-memory frames, never
    # from a reloaded CSV (preamble S7, SPECS 1.6). The frames are re-serialised
    # here and their digests compared with the files just written, so the figure
    # is CERTIFIED to describe the persisted campaign rather than assumed to.
    mismatched = []
    with tempfile.TemporaryDirectory() as scratch_dir:
        scratch = Path(scratch_dir) / "reconciliation.csv"
        for name, frame in artefacts.items():
            save_fair_csv(frame, scratch)
            if compute_sha256(scratch) != compute_sha256(DATA_DIR / name):
                mismatched.append(name)
    if mismatched:
        logger.error(f"Re-serialisation of {mismatched} does not reproduce the digest of the file "
                     f"just written; the figure and the macros would describe a campaign the CSVs "
                     f"do not contain.")
        sys.exit(1)
    logger.info(f"Re-serialisation reconciliation: all {len(artefacts)} CSVs re-serialise to the "
                f"digests written above. The figure and the seven macros describe the persisted "
                f"campaign.")

    # Log artifact manifest for traceability
    all_artifacts = [DATA_DIR / name for name in artefacts]
    all_artifacts.extend([FIGURES_DIR / "fig09_anytime_valid.png", TABLES_DIR / "R09_claims.tex"])
    log_artifact_manifest(logger, all_artifacts, RESULTS_DIR, BASE_DIR)

    logger.info("--- SHA-256 of every artefact (preamble S2) ---")
    for name in artefacts:
        logger.info(f"SHA-256 {name:<44} : {compute_sha256(DATA_DIR / name)}")
    logger.info(f"SHA-256 {'fig09_anytime_valid.png':<44} : "
                f"{compute_sha256(FIGURES_DIR / 'fig09_anytime_valid.png')}")
    logger.info(f"SHA-256 {'R09_claims.tex':<44} : "
                f"{compute_sha256(TABLES_DIR / 'R09_claims.tex')}")

    fired = [name for name, entry in c4["spearman"].items() if entry["fired"]]
    logger.info(f"CONTROL SUMMARY. C3 gate on MIX: "
                f"{'FIRED' if c3['fired'] else 'not fired'} (p = {c3['p_mix']!r}). C4 Spearman "
                f"gates not met on: {fired or 'none'}. C4 halt condition: "
                f"{'MET' if c4['halt'] else 'not met'}.")
    logger.info(f"Execution completed in {time.time() - t0:.1f}s with {args.n_jobs} workers and "
                f"control arm = {args.control_arms}. NUM_CHUNKS = {NUM_CHUNKS} fixes the chunk "
                f"decomposition, so a rerun at a different worker count must produce "
                f"byte-identical artefacts.")


if __name__ == "__main__":
    main()
