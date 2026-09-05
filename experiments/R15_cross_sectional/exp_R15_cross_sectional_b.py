#!/usr/bin/env python3
"""
==========================================================================
R15 (b) -- CROSS-SECTIONAL ESCAPE ON A REAL EQUITY PANEL
           (v87 Figure 17 `fig:cross_section`, L376)
==========================================================================
v87 closes its Discussion with the only structural escape left to the univariate
Sharpe ceiling: pooling K correlated streams. L376 and the Figure 17 caption
publish what that pooling buys on 97 surviving US equities, 2005--2025. This
stage regenerates the figure and every numeral of L376 from the panel
exp_R15_cross_sectional_a.py certifies.

WHAT v87 PUBLISHES FROM THIS STREAM, AND WHERE EACH NUMBER LIVES.

  L376 + caption, `97` equities, 2005--2025 -> R15_panel_diagnostics, K = 97
  L376 + caption, `rho ~ 0.26`              -> same file, rho_sign_meas, K >= 5
  L376 + caption, `K_eff ~ 1/rho ~ 3.8`     -> same file, K_eff_meas at K = 97
  L376, "budget contracts by a measured 2x" -> race, budget_reduction, c = 0.25
  caption (B), "plateaus near 2x (K >= 20)" -> same, mean over K >= 20
  L376, "whiteness fails beyond K = 10"      -> diagnostics, ljungbox_p_Pt
  L376, "~100% false alarms by K = 40"       -> diagnostics, FPR_naive
  caption (A), bootstrap holds `4.8`-`6.4%` -> diagnostics, FPR_boot min/max
  caption (B), `r >= 0.99` with the
        bootstrap threshold                  -> R15_scatter_correlation, c = 0.25
  L376, "still never flags the 2020 crash"   -> R15_covid_natural, delay_boot

THE FROZEN COMPOSITION, AND WHY IT IS CARRIED RATHER THAN RE-KEYED.
`assets_idx` selects WHICH REAL SERIES ENTER THE EXPERIMENT. It is the same
category of object as R01's four ETFs, R16's four streams and R14's 106 monthly
onsets, none of which is redrawn: a frozen nuisance draw over the data, not a
Monte-Carlo replicate of the apparatus. It is carried verbatim, digest and all.

It is NOT exempted by the preamble's S6 "regle de partage". That clause covers
analytic constants of the apparatus; `assets_idx` is a uniform draw over subsets
of size K, and invoking the clause here would licence freezing any inconvenient
draw later. The ground is the category of the draw and nothing else.

Every Monte-Carlo draw around it MIGRATES to a 128-bit SeedSequence keyed on
role and INTEGER GRID INDEX -- never on the float c, never on the value of K,
never on MASTER_SEED:

  lambda_naive calibration        ("naive_calib", k_index)
  bootstrap calibration windows   ("boot_calib",  k_index, i)
  held-out FPR windows            ("fpr_window",  k_index, i)
  H1 race windows                 ("race_h1",     k_index, c_index, i)
  H1 single-stream reference      ("race_h1_ref", c_index, i)

CONSEQUENCE, STATED BEFORE ANY RESULT IS READ. `rho_sign_meas`, `K_eff_meas`,
`K_eff_ana` and `ljungbox_p_Pt` carry NO RNG once the composition is fixed: they
are deterministic functions of the panel and they are GUARANTEED to reproduce.
A guaranteed agreement is evidence of port fidelity and of nothing else. It says
nothing about the sampling behaviour of rho or of K_eff, and the
epistemic-asymmetry rule applies to it at full force, which is why control C1
below is an ASSERTION on the integer composition and not an observation on a
float.

`lambda_naive`, `lambda_boot`, `FPR_naive`, `FPR_boot`, `ADD`, `SEM`, `DetRate`
and `budget_reduction` are redrawn by the migration and may move.

ONE PAIRING THE MIGRATION DELIBERATELY BREAKS. In the delivered script the
reference arm's seed string is `real_race1_1_{c}_{MASTER_SEED}_{i}` and the
panel arm's at K = 1 is `real_race1_{K}_{c}_{MASTER_SEED}_{i}`. At K = 1 those
are the SAME STRING on the SAME sub-panel, so the delivered
`budget_reduction(K = 1)` is exactly 1.0 by construction rather than by
measurement -- the submitted CSV shows 1.0 to every digit at c = 0.25, 0.50,
0.75 and 1.0. The migrated keys separate the two roles, so the regenerated
K = 1 cell is an honest estimate of 1 with sampling error instead of an
identity. The plateau statistic reads K >= 20 and is untouched; the change is
reported, not repaired.

FIVE STRUCTURAL CHANGES AGAINST THE DELIVERED SCRIPT, EACH FORCED BY THE
PREAMBLE.

1. NO HALTING GATE ON A CONTINUOUS MONTE-CARLO VALUE. The delivered Control (c)
   exits when `FPR_boot` leaves [0.03, 0.07]. S4bis forbids gating a campaign on
   a continuous redrawn quantity: the band becomes an instrument of selection
   over seeds. The band is measured, logged and reported at every K, and it
   halts nothing.
2. NO BARE sqrt(n) (S4bis, sixth corollary). `H_ref + H_det = 1250` on
   `T = 5154` days admits only 3905 distinct windows, so 20 000 calibration
   draws enumerate the window population about five times over and two windows
   can share up to 1249 of their 1250 days. The delivered `stats.sem` is kept
   unchanged for witness comparability and every design-effect column is added
   beside it.
3. THE --fast BRANCH IS REMOVED. A second grid is a second campaign and v87
   publishes one.
4. `tqdm`, the absolute `BASE_DIR`, `PYTHONHASHSEED = "0"` and the
   `logging.info = logger.info` monkey-patch are removed (R06/R12 precedent).
5. `joblib.Parallel` becomes `concurrent.futures.ProcessPoolExecutor` with
   `executor.map` in SUBMISSION ORDER, never `as_completed` (SPECS 1.5). The
   K x 5154 sub-panel is passed once through a pool initialiser and never per
   task: 300 000 tasks each re-pickling a 4 MB array is the difference between
   minutes and hours.

THE TWO ARMS OF THIS SCRIPT.
  default          `enforce_strict_determinism()`, the repository's canonical
                   bootstrap, MKL_CBWR = COMPATIBLE included.
  --witness-blas   the same four thread pins with MKL_CBWR REMOVED, which is the
                   environment the submitted campaign ran under. Outputs are
                   stamped `_witness_blas` and CERTIFY NO v87 VALUE. The arm
                   exists for ATTRIBUTION, not for passing: it answers whether a
                   residual comes from the BLAS summation order or from this
                   port. R01's `--legacy-blas` refuted its hypothesis and R14's
                   `--legacy-seeds` confirmed its own; either outcome is
                   information. It runs unconditionally, after the default arm,
                   because a diagnostic executed only when a result looks wrong
                   is an instrument of selection.

References:
- Page, E. S. (1954). Continuous inspection schemes. Biometrika, 41, 100-115.
- Wilson, E. B. (1927). Probable inference, the law of succession, and
  statistical inference. JASA, 22(158), 209-212.
- Ljung, G. M. & Box, G. E. P. (1978). On a measure of lack of fit in time
  series models. Biometrika, 65(2), 297-303.
- Kish, L. (1965). Survey Sampling. Wiley. (design effect)
- Kunsch, H. R. (1989). The jackknife and the bootstrap for general stationary
  observations. Annals of Statistics, 17(3), 1217-1241. (moving-block bootstrap)
- Higham, N. J. (2002). Accuracy and Stability of Numerical Algorithms, 2nd ed.
  SIAM, chapter 4. (the N*eps bound on a reordered floating-point summation)

NOTATION
  K                number of pooled equity streams
  K_max            surviving panel width, 97, and the last element of K_GRID
  P_t              cross-sectional fraction of positive recentred signs, minus
                   1/2; `fraction_stream` in the code
  rho_sign_meas    mean pairwise correlation of the sign matrix, upper triangle
  K_eff_meas       1 / (4 * Var(P_t)), the effective panel size read off P_t
  K_eff_ana        K / (1 + (K-1) * rho_sign_meas), its analytic counterpart
  lambda_naive     CUSUM threshold calibrated on Binomial(K, 1/2), i.e. under an
                   independence assumption the panel violates
  lambda_boot      CUSUM threshold calibrated on real null windows of the panel
  c                injected drift, in units of the per-stream H_ref sigma
  ADD              average detection delay, CONDITIONAL ON DETECTION
  add_reliable     per-cell flag, DetRate >= 0.90
  budget_reduction ADD_single / ADD, the realized cross-sectional speed-up
  q_hat            P(z > 0) on the H_det half against the H_ref median
  deff             Kish design effect of a mean over overlapping windows
  n_eff            n / deff, the independent readings a sample contains
==========================================================================
"""

import sys
from pathlib import Path

# Determinism bootstrap, in the order preamble S6 requires: fair_env imports only
# os and sys, so the environment block is posted before NumPy is loaded by anyone
# and before any BLAS thread limit is read. PYTHONHASHSEED cannot be set from
# here -- CPython reads it at interpreter start-up -- so it is exported by
# run_experiment_R15.sh and verified below.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from experiments.common.fair_env import enforce_strict_determinism, verify_hash_seed, log_environment

enforce_strict_determinism()

import os

if os.environ.get("PYTHONHASHSEED") != "42":
    sys.exit("FATAL: PYTHONHASHSEED is not 42. Execute via run_experiment_R15.sh")

# The attribution arm, read off sys.argv BEFORE NumPy exists. `MKL_CBWR` is read
# once, when the BLAS is loaded, so an assignment after `import numpy` is inert
# and argparse -- which runs inside main() -- is far too late. This is local to
# R15: `experiments/common/fair_env.py` is shared by every stream and is not
# touched. `legacy_blas=True` is NOT the same thing and does not serve here: it
# lifts the four thread pins as well, and the submitted campaign ran WITH them.
WITNESS_BLAS = "--witness-blas" in sys.argv
if WITNESS_BLAS:
    os.environ.pop("MKL_CBWR", None)

import numpy as np
import pandas as pd
from experiments.common.fair_harness import (setup_logging, disable_pandas_multithreading,
                                             compute_sha256, save_fair_csv, log_artifact_manifest)

disable_pandas_multithreading()

import ast
import time
import hashlib
import argparse
import concurrent.futures
from itertools import repeat
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy.stats as stats
import statsmodels.api as sm

# --- PROTOCOL SPECIFICATION, IMPERATIVE, FROM v87 AND THE DELIVERED SCRIPT ---
# `Priorite_25c_real_cross_sectional_escape_UPDATED.py` lines 167-175, the FULL
# real branch. Every one of these is LOGGED and not merely coded (S2.7).
H_REF = 500
# The delivered comment on this line is part of the specification: "finite real
# panel: shorter horizon => more distinct, less-overlapping windows".
H_DET = 750
TARGET_FPR = 0.05
N_CAL = 20000
N_RACE = 2000
MASTER_SEED = 42
# K_max is appended at run time from the panel width; it is NOT typed here,
# because a hard-coded 97 would survive a panel that no longer has 97 columns.
K_GRID_PREFIX = (1, 5, 10, 20, 30, 40, 50, 60, 75)
C_GRID = (0.10, 0.25, 0.50, 0.75, 1.0)
# The delivered plotting line 378, `c_target = C_GRID[1]`, fixes WHICH drift
# magnitude Figure 17 panel B draws. It is read by INDEX, from the plotting code,
# and never chosen: the published "plateaus near 2x" is a statement about the
# curve the figure shows.
C_TARGET_INDEX = 1
# The delivered reliability floor (line 310).
DET_RATE_FLOOR = 0.90
# The plateau is read over this range because the caption names it: "plateaus
# near 2x (K >= 20)".
PLATEAU_K_MIN = 20
# The pooled sign correlation of L376 excludes K = 1, where rho is 0 by
# construction and not by measurement (control C1).
RHO_POOL_K_MIN = 5
# The synthetic branch of the delivered script is NOT RUN: it produces Figure 29,
# which is not in v87, and the scope filter is strictly v87's content. Its
# constants are recorded as the specification of a branch this port does not
# execute, so that the omission is legible rather than silent.
SYNTHETIC_BRANCH_SPEC = {"alpha": 0.08, "beta": 0.90, "nu": 7.0, "H_det": 2000,
                         "K_GRID": (1, 50, 100, 200, 500),
                         "RHO_GRID": (0.0, 0.05, 0.10, 0.20, 0.30, 0.50)}
# The delivered Control (c) band. Kept as a REPORTED interval; it halts nothing.
DELIVERED_FPR_BAND = (0.03, 0.07)
# COVID natural experiment, delivered line 328.
COVID_ONSET = "2020-02-20"

# --- WHAT v87 PRINTS, AT THE PRECISION IT PRINTS IT (preamble S3) ---
V87_PANEL_SIZE = 97
V87_RHO_SIGN = 0.26
V87_KEFF = 3.8
V87_FPR_BOOT_MIN_PCT = 4.8
V87_FPR_BOOT_MAX_PCT = 6.4
V87_WHITENESS_FAILS_BEYOND_K = 10
V87_BUDGET_PLATEAU = 2.0
V87_SCATTER_R = 0.99
V87_COVID_DETECTIONS = 0

# --- BOOTSTRAP ENVELOPES (descriptive; they gate nothing) ---
BOOTSTRAP_REPLICATES = 2000
BOOTSTRAP_CONF = 95.0

# --- THE FLOATING-POINT REORDERING BOUND (control C1, leg 2) ---
# DERIVED FROM THE MECHANISM, NOT FROM AN OBSERVATION. `rho_sign_meas` is the
# mean of the upper triangle of `np.corrcoef(signs)`, whose every entry is a
# BLAS inner product over the T = 5154 days, and the statistic aggregates
# K(K-1)/2 of them; the number of floating-point additions whose ORDER the BLAS
# may permute therefore scales as T * K. A double-precision summation of N terms
# evaluated in two different orders differs by at most about N * eps in relative
# terms, with eps = 2^-52 (Higham 2002, ch. 4; the classical (N-1)*u*
# sum|x_i|/|sum x_i| bound, at the unit amplification factor a sign matrix
# gives). At K = 97 this is 5154 * 97 * 2.2e-16 = 1.1e-10. The bound is stated
# here BEFORE the run and is exceeded by nothing in this file; a bound read off
# the measured residual would assert nothing at all.
FP_EPS = float(np.finfo(np.float64).eps)

# --- INPUTS ---
DERIVED_DIR = BASE_DIR / "data" / "derived_equities"
PANEL_PATH = DERIVED_DIR / "R15_panel_logreturns.csv"
WITNESS_DIR = BASE_DIR / "data" / "reference" / "R15"
WITNESS_SOURCE = WITNESS_DIR / "Priorite_25c_real_cross_sectional_escape_UPDATED.py"
# The SUPERSEDED four-point re-run of the same code. It is vendored, and it is
# read here, because the provenance of the published K grid is a claim of
# `docs/DEVIATIONS.md` (`R15-grid-provenance`) and a claim has to be checkable
# by a reader holding this repository and nothing else.
SUPERSEDED_SOURCE = WITNESS_DIR / "Priorite_25c_real_cross_sectional_escape.py"
SUPERSEDED_LOG = WITNESS_DIR / "Priorite_25c_real_cross_sectional_escape.log"
WITNESS_LOG = WITNESS_DIR / "Priorite_25c_real_cross_sectional_escape_UPDATED.log"
R13_SOURCE = BASE_DIR / "experiments" / "R13_oracle_ceiling" / "exp_R13_oracle_ceiling_a.py"
WITNESS_CSVS = {
    'diagnostics': "protocol_25c_real_panel_diagnostics_UPDATED.csv",
    'race': "protocol_25d_real_cross_sectional_race_UPDATED.csv",
    'covid': "protocol_25e_covid_natural.csv",
}
PANEL_SHA256 = "fb426ab0e7e112de61f112952737fd38ea103bd90e1989defa6d33dc086bcf8f"
# The line of each vendored script that declares the FULL real-branch K grid, and
# the line of each log that records which grid actually ran. Both are asserted
# below, so `R15-grid-provenance` rests on a check and not on a sentence.
GRID_EVIDENCE = {
    WITNESS_SOURCE: (167, "K_GRID = [1, 5, 10, 20, 30, 40, 50, 60, 75, K_max]"),
    SUPERSEDED_SOURCE: (167, "K_GRID = [1, 20, 50, K_max]"),
}

# --- SOURCE-SEGMENT IDENTITY (control C9) ---
# Preamble S4.2 forbids hoisting a scientific primitive into experiments/common/.
# The ban is not pedantry here: `strict_cusum`, `bilateral_delay` and `wilson_ci`
# all differ between this witness and the R01/R03/R04/R11/R13/R14 copies, and
# borrowing any of them would move a published value.
CARRIED_PRIMITIVES = {
    "strict_cusum": (WITNESS_SOURCE, "strict_cusum"),
    "bilateral_delay": (WITNESS_SOURCE, "bilateral_delay"),
    "cusum_max_bilateral": (WITNESS_SOURCE, "cusum_max_bilateral"),
    "wilson_ci": (WITNESS_SOURCE, "wilson_ci"),
    "fraction_stream": (WITNESS_SOURCE, "fraction_stream"),
    "get_deterministic_seed": (R13_SOURCE, "get_deterministic_seed"),
    "seed_sequence_for": (R13_SOURCE, "seed_sequence_for"),
    "rng_for": (R13_SOURCE, "rng_for"),
}
# The two workers this port ADAPTS. The adaptation is exactly one line each --
# the internal `rng = np.random.default_rng(seed)` becomes an injected generator
# -- so byte identity is not assertable and the witness source of each is quoted
# in full in the log instead.
ADAPTED_ROUTINES = ("worker_null_window_real", "worker_race_h1_real")
# The three statements of the delivered `run_real_experiment` that this port
# carries VERBATIM, as text, because they define the frozen composition. Control
# C1 leg 1 additionally EXECUTES the witness's own extracted statements and
# compares the resulting integer arrays, so leg 1 cannot pass on a coincidence
# of a rewritten derivation.
CARRIED_STATEMENTS = ("cell_seed_base", "rng_diag", "assets_idx")
# Superseded outright, pinned by the SHA-256 of the witness segment and NOT
# quoted, which is preamble S4.2's treatment for a routine this port replaces.
# `simulate_panel` and `standardized_t` are named by the R15 prompt's C9 but have
# NO CALL SITE IN SCOPE: they serve the `--source synthetic` branch alone, which
# produces Figure 29 and is not in v87. The over-specification is reported in
# docs/audits/AUDIT_R15.md as an open question rather than settled here.
SUPERSEDED_ROUTINES = {
    "simulate_panel": "synthetic branch only (Figure 29, not in v87); no call site in scope",
    "standardized_t": "synthetic branch only (Figure 29, not in v87); no call site in scope",
    "load_real_panel": "replaced by an explicit read of data/derived_equities/ with round-trip "
                       "parsing and a digest",
    "setup_logger": "replaced by experiments/common/fair_harness.setup_logging",
    "run_experiment": "the --fast branch and the --source synthetic branch are both out of scope",
    "worker_boot_calib": "synthetic branch only; no call site in scope",
    "worker_race_h0": "synthetic branch only; no call site in scope",
    "worker_race_h1": "synthetic branch only; no call site in scope",
    "run_real_experiment": "restructured: injected generators, pool initialiser, design effects, "
                           "and no halting gate on a continuous Monte-Carlo value",
}

MACRO_HEADER = "% Auto-generated by exp_R15_cross_sectional_b.py -- do not edit."
WITNESS_BLAS_SUFFIX = "_witness_blas"
REQUIREMENT_PACKAGES = ("numpy", "pandas", "scipy", "statsmodels", "matplotlib", "yfinance",
                        "pytest")


# --- PRIMITIVES CARRIED FROM THE FILES THAT OWN THEM ---
# Do not reformat. Byte identity is checked on the exact source text at start-up,
# trailing whitespace included.

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

def fraction_stream(eps):
    """Cross-sectional fraction of positive recentered signs (median=0 by symmetry)."""
    return (eps>0.0).mean(axis=0) - 0.5                   # centered: E[.]=0 under H0


# --- SEED DERIVATION (preamble S6, SPECS 1.2) ---
# Carried byte-identically from exp_R13_oracle_ceiling_a.py, which is this
# repository's canonical form.

def get_deterministic_seed(*args) -> int:
    """
    Derives a 128-bit collision-free seed from the semantic coordinates of a
    task, returned as a scalar integer so no entropy is discarded. This is the
    repository's canonical form, carried from exp_R11_multi_detector.py.

    Floats are formatted through .hex() rather than str(): the decimal repr of a
    float is platform-dependent at the last digit on some C libraries, which
    would silently re-key a cell across machines. The native hash() is randomly
    salted and is forbidden outright (§1.2).
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


# --- THE FROZEN COMPOSITION, CARRIED VERBATIM (control C1) ---

def composition_for(K, K_max):
    """
    The three statements below are the delivered script's own, lines 186, 187
    and 190 of `run_real_experiment`, character for character. They are asserted
    against the witness source by `ast` at start-up AND re-executed from the
    witness text, so that this function cannot pass by resembling the witness.

    `% (2**32)` truncates a 128-bit digest to 32 bits and `default_rng` then
    expands it again. That is exactly the truncation the entropy migration
    exists to remove -- and it is kept here anyway, because what this draw
    selects is WHICH REAL SERIES ENTER THE PANEL, not a Monte-Carlo replicate.
    Re-keying it would draw a different set of equities and answer a different
    question from v87's.
    """
    cell_seed_base = int(hashlib.md5(f"real_{K}_{MASTER_SEED}".encode()).hexdigest(), 16) % (2**32)
    rng_diag = np.random.default_rng(cell_seed_base)
    assets_idx = rng_diag.choice(K_max, size=K, replace=False)
    return assets_idx


# --- WORKERS ADAPTED FROM THE DELIVERED SCRIPT (injected RNG only) ---

def worker_null_window_real(rng, eps_K_full, H_ref, H_det):
    """
    ADAPTED. The delivered form reads
    `def worker_null_window_real(seed, eps_K_full, H_ref, H_det)` with
    `rng = np.random.default_rng(seed)` as its first statement. Preamble S6
    requires the migration to a 128-bit SeedSequence keyed on role and index, so
    the generator is constructed by the caller and passed in. EVERY OTHER LINE
    IS THE WITNESS'S, and the witness segment is quoted in full in the log by
    control C9.

    Windowed REAL null (c=0), byte-for-byte commensurable with
    worker_race_h1_real: a random window, per-window median/std recentring on
    the H_ref past (non-anticipative), no injection. `cusum_max > lambda` is
    equivalent to `bilateral_delay` firing, so this null is the exact
    false-alarm construction of the H1 race pipeline at c = 0.
    """
    K, T_full = eps_K_full.shape
    t_start = rng.integers(0, T_full - (H_ref + H_det) + 1)
    w = eps_K_full[:, t_start:t_start + H_ref + H_det]
    med = np.median(w[:, :H_ref], axis=1, keepdims=True)
    std = np.std(w[:, :H_ref], axis=1, keepdims=True); std[std == 0] = 1.0
    z = (w - med) / std
    x = fraction_stream(z)[H_ref:]
    return cusum_max_bilateral(x, 0.0)


def worker_race_h1_real(rng, eps_K_full, H_ref, H_det, c, lam_boot):
    """
    ADAPTED, on the same single line and for the same reason. Every other line
    is the witness's, comments included, and the witness segment is quoted in
    full in the log by control C9.
    """
    K, T_full = eps_K_full.shape
    max_start = T_full - (H_ref + H_det)
    t_start = rng.integers(0, max_start + 1)
    eps_window = eps_K_full[:, t_start : t_start + H_ref + H_det]

    # Standardization over H_ref for c*sigma injection
    med = np.median(eps_window[:, :H_ref], axis=1, keepdims=True)
    std = np.std(eps_window[:, :H_ref], axis=1, keepdims=True)
    std[std == 0] = 1.0
    eps_std = (eps_window - med) / std

    # Semi-real H1 injection
    eps_std[:, H_ref:] += c

    x = fraction_stream(eps_std)[H_ref:]
    return bilateral_delay(x, 0.0, lam_boot)


def window_start(seed, T_full):
    """
    The window index a task draws, recovered WITHOUT touching the adapted
    worker. `rng.integers` is the first and only draw either worker takes from
    its generator, so a second generator built from the same 128-bit seed
    returns the same `t_start` by construction. This is what lets the design
    effect of control C8 be computed on the ACTUAL windows a cell used, instead
    of on an assumption about them, while both workers keep the witness's body.
    """
    return int(np.random.default_rng(np.random.SeedSequence(seed))
               .integers(0, T_full - (H_REF + H_DET) + 1))


def window_q_hat(eps_K_full, t_start):
    """
    NOT IN THE WITNESS. `q_hat` = P(z > 0) measured on the H_det half against
    the H_ref median, the MARGINAL channel of the false-alarm inflation.

    Why it is needed. At K = 1 the naive threshold is calibrated on
    Binomial(1, 1/2) -- a fair coin -- while the real recentred sign stream
    carries P(z > 0) = q. Control C1 establishes `rho_sign_meas = 0` and
    `K_eff_meas = 1` EXACTLY at K = 1, so there is NO cross-sectional
    correlation there to be ignored, and the delivered `FPR_naive = 0.1115` at
    K = 1 -- 2.2x its nominal level -- cannot be attributed to the mechanism the
    Figure 17 caption names.
    """
    w = eps_K_full[:, t_start:t_start + H_REF + H_DET]
    med = np.median(w[:, :H_REF], axis=1, keepdims=True)
    return float((w[:, H_REF:] > med).mean())


# --- PARALLEL PLUMBING: THE SUB-PANEL TRAVELS ONCE, NEVER PER TASK ---

_PANEL = None


def _init_worker(panel):
    global _PANEL
    _PANEL = panel


def _null_task(seed):
    """One real null window: its CUSUM maximum, its start index and its q_hat."""
    m = worker_null_window_real(np.random.default_rng(np.random.SeedSequence(seed)),
                                _PANEL, H_REF, H_DET)
    t_start = window_start(seed, _PANEL.shape[1])
    return float(m), t_start, window_q_hat(_PANEL, t_start)


def _race_task(seed, c, lam_boot):
    """One H1 race replicate: its delay and its start index."""
    d = worker_race_h1_real(np.random.default_rng(np.random.SeedSequence(seed)),
                            _PANEL, H_REF, H_DET, c, lam_boot)
    return int(d), window_start(seed, _PANEL.shape[1])


class _Pool:
    """
    A process pool whose initialiser carries the sub-panel, or a transparent
    in-process fallback at `--n-jobs 1`. `executor.map` preserves SUBMISSION
    ORDER (SPECS 1.5), so the result sequence -- and every quantile, mean and
    digest taken from it -- does not depend on `--n-jobs`. That invariance is
    control C10 and it is what `run_experiment_R15.sh --n-jobs 1` verifies.
    Workers return values only and never write to the log.
    """

    def __init__(self, panel, n_jobs):
        self.n_jobs = n_jobs
        self.panel = panel
        self.executor = None

    def __enter__(self):
        if self.n_jobs > 1:
            self.executor = concurrent.futures.ProcessPoolExecutor(
                max_workers=self.n_jobs, initializer=_init_worker, initargs=(self.panel,))
        else:
            _init_worker(self.panel)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.executor is not None:
            self.executor.shutdown()
        return False

    def map(self, fn, *iterables, total):
        if self.executor is None:
            return list(map(fn, *iterables))
        chunksize = max(1, total // (self.n_jobs * 8))
        return list(self.executor.map(fn, *iterables, chunksize=chunksize))


# --- SOURCE IDENTITY AND PROVENANCE (control C9) ---

def source_segments(path, names):
    """
    Source text of the named top-level functions, extracted by position rather
    than by import: importing the delivered script would execute its environment
    block, create an absolute output directory outside this repository, and
    build a logger writing outside it.
    """
    text = Path(path).read_text()
    tree = ast.parse(text)
    return {node.name: ast.get_source_segment(text, node)
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in names}


def statement_segments(path, func_name, targets):
    """
    Source text of the FIRST assignment to each named target inside a function,
    extracted by `ast`. `run_real_experiment` assigns `cell_seed_base` and
    `assets_idx` in three places under three different names
    (`..._1`, `..._K`); only the exact identifiers are matched, and only their
    first occurrence is taken.
    """
    text = Path(path).read_text()
    tree = ast.parse(text)
    found = {}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef) and node.name == func_name):
            continue
        for stmt in ast.walk(node):
            if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
                continue
            target = stmt.targets[0]
            if isinstance(target, ast.Name) and target.id in targets and target.id not in found:
                found[target.id] = ast.get_source_segment(text, stmt)
    return found


def check_source_identity(log):
    """
    C9. Byte identity of every carried primitive against the file that owns it,
    at run time, plus the witness source of the two adapted workers quoted in
    full and the SHA-256 of every superseded routine. Deterministic; trigger
    probability 0 unless a copy has drifted.
    """
    own = source_segments(Path(__file__).resolve(), set(CARRIED_PRIMITIVES))
    compared = 0
    for local_name, (path, remote_name) in sorted(CARRIED_PRIMITIVES.items()):
        if not path.exists():
            log.error(f"C9 source-identity failure: {path} is missing, so the copy of "
                      f"{local_name} cannot be verified.")
            sys.exit(1)
        remote = source_segments(path, {remote_name}).get(remote_name)
        mine = own.get(local_name)
        if remote is None or mine is None:
            log.error(f"C9 source-identity failure: {local_name} could not be extracted "
                      f"({path.name}::{remote_name}).")
            sys.exit(1)
        if mine != remote:
            log.error(f"C9 source-identity failure on {local_name}: the copy has drifted from "
                      f"{path.name}::{remote_name}.")
            sys.exit(1)
        compared += len(remote)
    log.info(f"C9 source identity: {len(CARRIED_PRIMITIVES)} primitives byte-identical to the "
             f"files that own them ({compared} characters compared) -- strict_cusum, "
             f"bilateral_delay, cusum_max_bilateral, wilson_ci and fraction_stream against "
             f"{WITNESS_SOURCE.name}, and get_deterministic_seed, seed_sequence_for and rng_for "
             f"against {R13_SOURCE.name}. Preamble S4.2 forbids hoisting any of them into "
             f"experiments/common/: strict_cusum, bilateral_delay and wilson_ci all differ "
             f"between this witness and the R01/R03/R04/R11/R13/R14 copies, so the duplication "
             f"is deliberate. Deterministic; trigger probability 0 unless a copy has drifted.")

    witness = source_segments(WITNESS_SOURCE, set(ADAPTED_ROUTINES))
    missing = [name for name in ADAPTED_ROUTINES if name not in witness]
    if missing:
        log.error(f"C9: the witness carries no {missing}; the adaptation cannot be exhibited.")
        sys.exit(1)
    log.info(f"C9 ADAPTED ROUTINES. {list(ADAPTED_ROUTINES)} cannot be byte-compared: each takes "
             f"an injected generator where {WITNESS_SOURCE.name} builds one from an integer seed "
             f"inside the function body. That is the ONLY line that differs in either. The "
             f"witness source of each is quoted in full below; the two segments total "
             f"{sum(len(witness[n]) for n in ADAPTED_ROUTINES)} characters.")
    for name in ADAPTED_ROUTINES:
        log.info(f"C9 witness SHA-256 of {name}: "
                 f"{hashlib.sha256(witness[name].encode('utf-8')).hexdigest()}")
        log.info(f"C9 witness source of {name}:\n{witness[name].rstrip()}")
    superseded = source_segments(WITNESS_SOURCE, set(SUPERSEDED_ROUTINES))
    for name, reason in sorted(SUPERSEDED_ROUTINES.items()):
        segment = superseded.get(name)
        if segment is None:
            log.error(f"C9: {WITNESS_SOURCE.name} carries no {name}; the supersession cannot be "
                      f"pinned.")
            sys.exit(1)
        log.info(f"C9 SUPERSEDED {name}: witness segment SHA-256 "
                 f"{hashlib.sha256(segment.encode('utf-8')).hexdigest()} "
                 f"({len(segment)} characters) -- {reason}.")
    log.info("C9 REPORTED, NOT SETTLED: the R15 prompt's C9 names `simulate_panel` and "
             "`standardized_t` among the primitives to carry. Neither has a call site in scope. "
             "Both serve the `--source synthetic` branch alone, which produces Figure 29, and "
             "Figure 29 is not in v87. They are pinned by digest above and not quoted, which is "
             "preamble S4.2's treatment for a superseded routine; the over-specification is "
             "carried to docs/audits/AUDIT_R15.md as an open question.")


def check_carried_statements(log):
    """
    C1, LEG 2 (source identity of the frozen draw). The three statements that
    define the composition are compared as TEXT to the witness, so that leg 1
    below cannot pass on a coincidence of a rewritten derivation that happens to
    agree numerically.
    """
    witness = statement_segments(WITNESS_SOURCE, "run_real_experiment", set(CARRIED_STATEMENTS))
    mine = statement_segments(Path(__file__).resolve(), "composition_for",
                              set(CARRIED_STATEMENTS))
    for name in CARRIED_STATEMENTS:
        if name not in witness or name not in mine:
            log.error(f"C1 leg 2: the statement assigning `{name}` could not be extracted from "
                      f"{'the witness' if name not in witness else 'this file'}.")
            sys.exit(1)
        if witness[name] != mine[name]:
            log.error(f"C1 leg 2 FAILED on `{name}`. Witness: {witness[name]!r}. This port: "
                      f"{mine[name]!r}. The frozen composition is not the delivered one.")
            sys.exit(1)
    log.info(f"C1 leg 2: the {len(CARRIED_STATEMENTS)} statements that define the frozen "
             f"composition are byte-identical to {WITNESS_SOURCE.name}::run_real_experiment -- "
             + " | ".join(f"`{witness[n]}`" for n in CARRIED_STATEMENTS)
             + ". Deterministic; trigger probability 0.")
    return witness


def check_composition(log, witness_statements, K_grid, K_max):
    """
    C1, LEG 1 (the gate). The witness's OWN extracted statements are executed in
    a namespace holding nothing but `hashlib`, `np`, `K`, `K_max` and
    `MASTER_SEED`, and the integer array they produce is compared to this port's
    with `np.array_equal`. THE FROZEN OBJECT IS AN INTEGER ARRAY: the comparison
    is exact in any BLAS regime, and it is the only thing that has to be frozen,
    because everything downstream is a deterministic function of it given a
    fixed summation order. `sys.exit(1)` on any difference.
    """
    program = "\n".join(witness_statements[name] for name in CARRIED_STATEMENTS)
    compositions = {}
    for K in K_grid:
        namespace = {"hashlib": hashlib, "np": np, "K": K, "K_max": K_max,
                     "MASTER_SEED": MASTER_SEED}
        exec(compile(program, "<witness:run_real_experiment>", "exec"), namespace)
        replayed = namespace["assets_idx"]
        mine = composition_for(K, K_max)
        if mine.dtype != replayed.dtype or not np.array_equal(mine, replayed):
            log.error(f"C1 leg 1 FAILED at K = {K}: the port draws {mine.tolist()} "
                      f"(dtype {mine.dtype}) and the witness statements draw "
                      f"{replayed.tolist()} (dtype {replayed.dtype}). The panel composition is "
                      f"not the published one and NOTHING downstream is comparable to v87.")
            sys.exit(1)
        compositions[K] = mine
    log.info(f"C1 leg 1: the frozen composition is bit-identical to the witness at all "
             f"{len(K_grid)} values of K, integer array against integer array, replayed by "
             f"EXECUTING {WITNESS_SOURCE.name}'s own statements rather than by resembling them. "
             f"Deterministic; trigger probability 0.")
    return compositions


def check_grid_provenance(log):
    """
    The published K grid is recovered from a SOURCE LINE, not read off the
    published figure. Both candidate scripts are vendored and both are checked
    here, because `docs/DEVIATIONS.md :: R15-grid-provenance` states which one
    produced Figure 17 and a reader must be able to verify that with the
    repository alone.
    """
    for path, (lineno, expected) in GRID_EVIDENCE.items():
        if not path.exists():
            log.error(f"Missing {path}; the provenance of the published K grid cannot be checked.")
            sys.exit(1)
        line = path.read_text().splitlines()[lineno - 1].strip()
        if line != expected:
            log.error(f"{path.name} line {lineno} reads {line!r}, expected {expected!r}. The "
                      f"grid provenance recorded in docs/DEVIATIONS.md no longer holds.")
            sys.exit(1)
        log.info(f"GRID PROVENANCE {path.name} (SHA-256 {compute_sha256(path)}) line {lineno}: "
                 f"{line}")
    updated_log = WITNESS_LOG.read_text()
    superseded_log = SUPERSEDED_LOG.read_text()
    for probe in ("Whiteness K=5:", "Whiteness K=10:"):
        if probe not in updated_log:
            log.error(f"{WITNESS_LOG.name} does not run {probe!r}; the ten-point grid is not "
                      f"evidenced by the log of the script that declares it.")
            sys.exit(1)
        if probe in superseded_log:
            log.error(f"{SUPERSEDED_LOG.name} runs {probe!r}, which the four-point grid it "
                      f"declares cannot produce.")
            sys.exit(1)
    log.info(f"GRID PROVENANCE, resolved against both vendored artefacts. "
             f"{WITNESS_SOURCE.name} declares the TEN-point grid at line 167 and "
             f"{WITNESS_LOG.name} runs K = 5 and K = 10, which no four-point grid can produce; "
             f"{SUPERSEDED_SOURCE.name} declares the FOUR-point grid at the same line number and "
             f"{SUPERSEDED_LOG.name} runs K = 1, 20, 50, 97 only. The two runs AGREE EXACTLY at "
             f"every shared K -- FPR_naive = 0.1115 / FPR_boot = 0.0490 at K = 1 in both -- so "
             f"they are the same code path on two grids, and the superseded log is timestamped "
             f"19:25 against the ten-point 14:16 of the SAME DAY: the four-point run is a later, "
             f"COARSER re-run, not a predecessor. v87 embeds "
             f"Fig30_RealCrossSectional_Escape_UPDATED.png, the ten-point figure. The published "
             f"grid is therefore RECOVERED FROM A SOURCE LINE and is not read off the artefact. "
             f"docs/DEVIATIONS.md :: R15-grid-provenance records the pair, Class A, no severity.")


def read_witness_csvs(log):
    """
    The three submitted CSVs, read with `float_precision='round_trip'` because
    preamble S3 forbids transcribing a reference literal by hand and the fast
    float parser of pandas is not correctly rounded.
    """
    frames = {}
    for key, name in WITNESS_CSVS.items():
        path = WITNESS_DIR / name
        if not path.exists():
            log.error(f"Missing witness: {path}. The D0-D3 classification of preamble S3 cannot "
                      f"be computed by code, and transcribing its literals by hand is forbidden.")
            sys.exit(1)
        frames[key] = pd.read_csv(path, float_precision='round_trip')
        log.info(f"Witness {name}: {len(frames[key])} rows, SHA-256 {compute_sha256(path)}.")
    return frames


# --- THE DESIGN EFFECT (control C8, S4bis sixth corollary) ---

def overlap_lags(n, n_distinct):
    """
    The number of neighbouring replicates, IN t_start ORDER, that can share data
    with a given one. Fixed by the MECHANISM and never by an observed
    autocorrelation (preamble S4, rule 8): two windows overlap iff their starts
    differ by less than H_ref + H_det = 1250, `n` starts are drawn uniformly
    over `n_distinct` admissible positions, so a window's overlap neighbourhood
    holds about n * (2*1250 - 1) / n_distinct of them, half on each side.
    """
    radius = 2 * (H_REF + H_DET) - 1
    return int(min(n - 1, max(1, np.ceil(n * radius / n_distinct))))


def design_effect(values, k_used, label, log):
    """
    Kish design effect of a mean over overlapping windows,
    `deff = 1 + 2 * sum_{k=1..K} (1 - k/n) * rho_k`, with `rho_k` the lag-k
    autocorrelation of the t_start-ORDERED sequence and `K` supplied by the
    mechanism.

    Returns `(deff, clamped, k_used)`. A negative-autocorrelation estimate can
    push the sum below 1, where it would ADVERTISE more information than the
    sample holds; it is clamped at 1 and the clamp is logged.
    """
    n = len(values)
    if n < 2:
        return 1.0, False, 0
    k_used = int(min(k_used, n - 1))
    x = np.asarray(values, dtype=float)
    centred = x - x.mean()
    denom = float(np.dot(centred, centred))
    if denom <= 0.0:
        log.info(f"deff [{label}]: the {n} values are identical, so no autocorrelation is "
                 f"defined and deff is 1.0 by construction.")
        return 1.0, False, k_used
    raw = 1.0
    for k in range(1, k_used + 1):
        raw += 2.0 * (1.0 - k / n) * float(np.dot(centred[:-k], centred[k:]) / denom)
    if raw < 1.0:
        log.info(f"deff [{label}]: the estimate is {raw:.6f} < 1, which would claim more "
                 f"independent readings than the {n} observations contain; clamped to 1.0.")
        return 1.0, True, k_used
    return raw, False, k_used


def ordered_by_start(values, starts):
    """The values of a cell, sorted by window start; ties broken by draw index."""
    order = np.argsort(np.asarray(starts, dtype=np.int64), kind='stable')
    return np.asarray(values, dtype=float)[order]


def moving_block_bootstrap_mean(values, starts, n_distinct, key, log, label):
    """
    A percentile envelope for the mean of a cell, resampled in MOVING BLOCKS of
    the t_start-ordered sequence (Kunsch 1989) so that the overlap structure the
    design effect measures survives the resampling. Block length is the
    mechanism-fixed overlap neighbourhood, not a tuned constant.

    DESCRIPTIVE. No gate in this file reads it.
    """
    x = ordered_by_start(values, starts)
    n = len(x)
    if n < 2:
        return float('nan'), float('nan')
    block = int(min(n, max(1, overlap_lags(n, n_distinct))))
    n_blocks = int(np.ceil(n / block))
    rng = rng_for(*key)
    starts_idx = rng.integers(0, n - block + 1, size=(BOOTSTRAP_REPLICATES, n_blocks))
    offsets = np.arange(block)
    index = (starts_idx[:, :, None] + offsets[None, None, :]).reshape(BOOTSTRAP_REPLICATES, -1)
    means = x[index[:, :n]].mean(axis=1)
    lo = float(np.percentile(means, (100.0 - BOOTSTRAP_CONF) / 2.0))
    hi = float(np.percentile(means, 100.0 - (100.0 - BOOTSTRAP_CONF) / 2.0))
    log.info(f"Bootstrap [{label}]: B = {BOOTSTRAP_REPLICATES}, moving blocks of {block} "
             f"t_start-ordered replicates over n = {n}, {BOOTSTRAP_CONF:g}% percentile interval "
             f"[{lo!r}, {hi!r}] around a mean of {float(x.mean())!r}.")
    return lo, hi


# --- PHASE 1: DIAGNOSTICS AND CALIBRATION ---

def run_diagnostics(eps_real_full, compositions, K_grid, log):
    """
    The four columns that carry NO RNG once the composition is frozen. Every
    line of arithmetic here is the delivered script's.
    """
    rows = []
    for k_index, K in enumerate(K_grid):
        eps_K_full = eps_real_full[compositions[K], :]

        # Re-centering on the global temporal median for directional symmetry
        med_full = np.median(eps_K_full, axis=1, keepdims=True)
        eps_K_centered = eps_K_full - med_full
        x_diag = fraction_stream(eps_K_centered)

        rho_sign_meas = 0.0
        if K > 1:
            signs = np.sign(eps_K_centered)
            cm = np.corrcoef(signs)
            rho_sign_meas = cm[np.triu_indices(K, k=1)].mean()

        var_x = np.var(x_diag)
        K_eff_meas = 1.0 / (4.0 * var_x) if var_x > 0 else float('nan')
        K_eff_ana = K / (1.0 + (K - 1) * rho_sign_meas)

        lb_res = sm.stats.acorr_ljungbox(x_diag, lags=[20], return_df=True)
        p_val_lb = lb_res['lb_pvalue'].iloc[0]

        # Delivered Control (a): a post-onset perturbation leaves the H_ref
        # recentring unchanged. Carried; it is a structural identity and holds
        # at 0.0 by construction.
        w_chk = eps_K_full[:, :H_REF + H_DET].copy()
        med0 = np.median(w_chk[:, :H_REF], axis=1); std0 = np.std(w_chk[:, :H_REF], axis=1)
        w_chk[:, H_REF:] += 1e3
        a_diff = float(np.max(np.abs(np.median(w_chk[:, :H_REF], axis=1) - med0))
                       + np.max(np.abs(np.std(w_chk[:, :H_REF], axis=1) - std0)))
        max_abs = float(np.max(np.abs(x_diag)))
        has_nan = bool(np.isnan(x_diag).any())
        log.info(f"Diagnostics K={K}: rho_sign_meas={rho_sign_meas!r}, K_eff_meas={K_eff_meas!r}, "
                 f"K_eff_ana={K_eff_ana!r}, ljungbox_p_Pt={float(p_val_lb):.4e}, "
                 f"K_eff_meas/K_eff_ana={K_eff_meas / K_eff_ana:.6f}. Delivered controls (a) "
                 f"non-anticipativity max recentring diff = {a_diff:.2e}, (g) bounds "
                 f"max|P_t|={max_abs:.4f}, NaNs={has_nan}.")
        if a_diff != 0.0 or has_nan or max_abs > 0.5:
            log.error(f"FAIL at K={K}: the delivered structural controls (a)/(g) are identities "
                      f"of the recentring and the bounded fraction, and one of them does not "
                      f"hold: a_diff={a_diff!r}, NaNs={has_nan}, max|P_t|={max_abs!r}.")
            sys.exit(1)
        rows.append({'K': K, 'k_index': k_index, 'rho_sign_meas': rho_sign_meas,
                     'K_eff_meas': K_eff_meas, 'K_eff_ana': K_eff_ana,
                     'ljungbox_p_Pt': float(p_val_lb), 'nonanticipativity_diff': a_diff,
                     'max_abs_Pt': max_abs})
    return pd.DataFrame(rows)


def check_degeneracy_at_k_one(eps_real_full, compositions, diagnostics, log):
    """
    C1 (the derivation). At K = 1, `rho_sign_meas == 0.0` and
    `K_eff_meas == 1.0` EXACTLY, and both are identities rather than
    measurements.

    ONE LINE OF DERIVATION. The median of 5154 (even) values is the mean of the
    two central order statistics, so subtracting it leaves exactly 2577 strictly
    positive and 2577 strictly negative entries PROVIDED no return equals the
    median. At K = 1, `fraction_stream` is `(eps > 0) - 1/2`, i.e. +-0.5 with
    mean 0, so Var(P_t) = 0.25 and K_eff = 1 / (4 * 0.25) = 1 exactly. The only
    way the split breaks is an exact tie with the median, which is asserted
    against. Deterministic; P(fire | H0) = 0.
    """
    stream = eps_real_full[compositions[1], :]
    centred = stream - np.median(stream, axis=1, keepdims=True)
    T = centred.shape[1]
    n_pos = int(np.sum(centred > 0.0))
    n_zero = int(np.sum(centred == 0.0))
    row = diagnostics[diagnostics['K'] == 1].iloc[0]
    failures = []
    if T % 2 != 0:
        failures.append(f"the panel carries {T} days, which is odd, so the median is an order "
                        f"statistic of the sample and the exact split does not follow")
    if n_zero != 0:
        failures.append(f"{n_zero} returns equal the median exactly, which is the only way the "
                        f"median split breaks")
    if n_pos != T // 2:
        failures.append(f"{n_pos} of {T} recentred returns are strictly positive, against the "
                        f"{T // 2} the median split requires")
    if float(row['rho_sign_meas']) != 0.0:
        failures.append(f"rho_sign_meas is {float(row['rho_sign_meas'])!r}, not 0.0")
    if float(row['K_eff_meas']) != 1.0:
        failures.append(f"K_eff_meas is {float(row['K_eff_meas'])!r}, not 1.0")
    if failures:
        log.error("C1 FAILED at K = 1: " + "; ".join(failures) + ". The K = 1 counterfactual of "
                  "the FPR decomposition rests on this degeneracy, so the run stops.")
        sys.exit(1)
    log.info(f"C1: at K = 1 the median split of {T} (even) values gives exactly {n_pos} strictly "
             f"positive returns and {n_zero} ties, so P_t = +-0.5 with zero mean, "
             f"Var(P_t) = 0.25 and K_eff_meas = 1/(4*0.25) = 1.0 EXACTLY; rho_sign_meas = 0.0 is "
             f"an identity of a one-stream panel and not a measurement. Deterministic; "
             f"P(fire | H0) = 0.")


def classify_diagnostics_against_witness(diagnostics, witness, K_grid, T, log):
    """
    C1, LEG 3. The four RNG-free columns against the submitted CSV, at a bound
    DERIVED FROM THE MECHANISM. Bit identity is NOT the criterion: each entry of
    `np.corrcoef` is a BLAS inner product over T days and the statistic averages
    K(K-1)/2 of them, so the count of additions whose order the BLAS may permute
    scales as T*K, and a reordered double-precision sum of N terms moves by at
    most about N*eps in relative terms (Higham 2002, ch. 4). The bound is
    `T * K * eps`; it is stated in the source above the run and is not read off
    any residual. Exceeding it is a real finding and stops the run.
    """
    witness_indexed = witness.set_index('K')
    columns = ('rho_sign_meas', 'K_eff_meas', 'K_eff_ana', 'ljungbox_p_Pt')
    worst = {c: (0.0, None) for c in columns}
    exceeded = []
    for K in K_grid:
        bound = T * K * FP_EPS
        row = diagnostics[diagnostics['K'] == K].iloc[0]
        ref = witness_indexed.loc[K]
        parts = []
        for column in columns:
            mine, theirs = float(row[column]), float(ref[column])
            rel = 0.0 if mine == theirs else abs(mine - theirs) / abs(theirs)
            parts.append(f"{column} {rel:.3e} ({rel / bound:.2e} of bound)")
            if rel > worst[column][0]:
                worst[column] = (rel, K)
            if rel > bound:
                exceeded.append((K, column, mine, theirs, rel, bound))
        log.info(f"C1 leg 3 K={K}: reordering bound T*K*eps = {bound:.3e}; realised relative "
                 f"differences against the witness -- " + ", ".join(parts) + ".")
    if exceeded:
        for K, column, mine, theirs, rel, bound in exceeded:
            log.error(f"C1 leg 3 FAILED at K={K} on {column}: witness {theirs!r}, regenerated "
                      f"{mine!r}, relative difference {rel:.6e} against a mechanism-derived "
                      f"bound of {bound:.6e}. A residual beyond the reordering bound is NOT a "
                      f"summation-order artefact. `ljungbox_p_Pt` additionally depends on the "
                      f"statsmodels build, so a failure on that column alone is a build "
                      f"difference and is reported as one.")
        log.error("C1 leg 3: nothing is absorbed, no tolerance is widened and no seed is moved. "
                  "Run with --witness-blas to attribute the residual.")
        sys.exit(1)
    log.info(f"C1 leg 3: the four RNG-free columns sit inside the mechanism-derived reordering "
             f"bound at all {len(K_grid)} values of K. Worst realised relative difference per "
             f"column -- "
             + ", ".join(f"{c} {worst[c][0]:.3e}"
                         + (f" at K = {worst[c][1]}" if worst[c][1] is not None
                            else " (bit-identical at every K)")
                         for c in columns)
             + f". THE AGREEMENT IS GUARANTEED BY THE FROZEN COMPOSITION and is evidence of port "
               f"fidelity ALONE: it says nothing whatever about the sampling behaviour of rho or "
               f"of K_eff, whose only draw was frozen before the campaign began.")
    return {c: worst[c] for c in columns}


def calibrate(eps_real_full, compositions, K_grid, n_jobs, log):
    """
    Phase 1's Monte-Carlo half: the naive threshold, the real-window bootstrap
    threshold, and the held-out false-alarm rates. Every draw here is MIGRATED.
    """
    T_full = eps_real_full.shape[1]
    n_distinct = T_full - (H_REF + H_DET) + 1
    rows, lambdas, window_records = [], {}, []
    for k_index, K in enumerate(K_grid):
        eps_K_full = eps_real_full[compositions[K], :]

        # Calibration Naive (independence assumption: Binomial(K, 1/2)). One
        # sequential generator per cell, exactly as delivered; the migration
        # replaces `default_rng(cell_seed_base + 1)` by a 128-bit key carrying
        # the ROLE and the INTEGER GRID INDEX, never the value of K.
        naive_maxes = []
        rng_naive = rng_for("naive_calib", k_index)
        for _ in range(N_CAL):
            p_indep = rng_naive.binomial(K, 0.5, size=H_DET) / K - 0.5
            naive_maxes.append(cusum_max_bilateral(p_indep, 0.0))
        lam_naive = np.quantile(naive_maxes, 1.0 - TARGET_FPR)

        with _Pool(eps_K_full, n_jobs) as pool:
            cal_seeds = [get_deterministic_seed("boot_calib", k_index, i) for i in range(N_CAL)]
            cal = pool.map(_null_task, cal_seeds, total=N_CAL)
            fpr_seeds = [get_deterministic_seed("fpr_window", k_index, i) for i in range(N_RACE)]
            held = pool.map(_null_task, fpr_seeds, total=N_RACE)

        cal_maxes = [m for m, _, _ in cal]
        lam_boot = np.quantile(cal_maxes, 1.0 - TARGET_FPR)
        lambdas[K] = lam_boot

        fpr_maxes = [m for m, _, _ in held]
        fpr_starts = [t for _, t, _ in held]
        fpr_q = np.array([q for _, _, q in held], dtype=float)
        fpr_n = sum(1 for m in fpr_maxes if m > lam_naive) / N_RACE
        fpr_b = sum(1 for m in fpr_maxes if m > lam_boot) / N_RACE

        # C3. The design effects of BOTH sets, and the standard error they give.
        eval_ind = np.array([1.0 if m > lam_boot else 0.0 for m in fpr_maxes])
        cal_ind = np.array([1.0 if m > lam_boot else 0.0 for m, _, _ in cal])
        cal_starts = [t for _, t, _ in cal]
        deff_r, clamp_r, lags_r = design_effect(ordered_by_start(eval_ind, fpr_starts),
                                                overlap_lags(N_RACE, n_distinct),
                                                f"FPR eval K={K}", log)
        deff_c, clamp_c, lags_c = design_effect(ordered_by_start(cal_ind, cal_starts),
                                                overlap_lags(N_CAL, n_distinct),
                                                f"calibration K={K}", log)
        se_design = float(np.sqrt(deff_r * fpr_b * (1.0 - fpr_b) / N_RACE
                                  + deff_c * TARGET_FPR * (1.0 - TARGET_FPR) / N_CAL))
        se_sqrt2 = float(np.sqrt(2.0) * np.sqrt(fpr_b * (1.0 - fpr_b) / N_RACE))
        se_naive_binomial = float(np.sqrt(fpr_b * (1.0 - fpr_b) / N_RACE))
        distinct_used = len(set(fpr_starts))

        ci_low, ci_high = wilson_ci(int(round(fpr_b * N_RACE)), N_RACE)
        # A resampling envelope for FPR_boot, in MOVING BLOCKS of the
        # t_start-ordered exceedance indicator so the overlap structure the
        # design effect measures survives the resampling. It exists because
        # \RFifteenFprBootMin and \RFifteenFprBootMax are extrema over a grid and
        # must ship with an envelope; it gates nothing.
        boot_low, boot_high = moving_block_bootstrap_mean(
            eval_ind, fpr_starts, n_distinct, ("bootstrap_fpr", k_index), log,
            f"FPR_boot K={K}")
        log.info(f"Calibration K={K}: lambda_naive={lam_naive!r}, lambda_boot={lam_boot!r}, "
                 f"FPR_naive={fpr_n:.4f}, FPR_boot={fpr_b:.4f} (delivered Control (c) band "
                 f"{DELIVERED_FPR_BAND}: "
                 f"{'inside' if DELIVERED_FPR_BAND[0] <= fpr_b <= DELIVERED_FPR_BAND[1] else 'OUTSIDE'}"
                 f"). q_hat over the {N_RACE} held-out windows: mean {float(fpr_q.mean())!r}, "
                 f"sd {float(fpr_q.std(ddof=1))!r}, range "
                 f"[{float(fpr_q.min())!r}, {float(fpr_q.max())!r}].")
        rows.append({
            'K': K, 'k_index': k_index, 'lambda_naive': lam_naive, 'lambda_boot': lam_boot,
            'FPR_naive': fpr_n, 'FPR_boot': fpr_b,
            'FPR_boot_CI_low': ci_low, 'FPR_boot_CI_high': ci_high,
            'FPR_boot_boot_low': boot_low, 'FPR_boot_boot_high': boot_high,
            'q_hat_mean': float(fpr_q.mean()), 'q_hat_sd': float(fpr_q.std(ddof=1)),
            'q_hat_min': float(fpr_q.min()), 'q_hat_max': float(fpr_q.max()),
            'deff_eval': deff_r, 'deff_eval_clamped': clamp_r, 'deff_eval_lags': lags_r,
            'deff_calib': deff_c, 'deff_calib_clamped': clamp_c, 'deff_calib_lags': lags_c,
            'n_eff_eval': N_RACE / deff_r, 'n_eff_calib': N_CAL / deff_c,
            'SE_FPR_boot_design': se_design, 'SE_FPR_boot_sqrt2_rule': se_sqrt2,
            'SE_FPR_boot_binomial': se_naive_binomial,
            'distinct_windows_used': distinct_used, 'distinct_windows_available': n_distinct,
        })
        window_records.append((K, fpr_starts))
    return pd.DataFrame(rows), lambdas, window_records, n_distinct


# --- PHASE 2: THE H1 SEMI-REAL RACE ---

def aggregate_cell(delays, starts, n_distinct, label, log):
    """
    One (K, c) cell. The delivered `DetRate`, `CI_low`, `CI_high`, `ADD` and
    `SEM` are computed exactly as delivered, and the design-effect columns are
    added beside them (R14 precedent).
    """
    valid = [d for d in delays if d != -1]
    valid_starts = [t for d, t in zip(delays, starts) if d != -1]
    det_rate = len(valid) / len(delays)
    ci_low, ci_high = wilson_ci(len(valid), len(delays))
    add_val = np.mean(valid) if valid else float('nan')
    sem_val = stats.sem(valid) if len(valid) > 1 else float('nan')

    # S4bis, SIXTH COROLLARY. The design effect is computed HERE, in the same
    # block and before the delivered `stats.sem` -- which divides by the square
    # root of a sample size whose independence is false by construction.
    deff, clamped, lags = design_effect(ordered_by_start(valid, valid_starts),
                                        overlap_lags(max(len(valid), 2), n_distinct),
                                        label, log)
    n_eff = len(valid) / deff if valid else 0.0
    sem_design = float(sem_val) * float(np.sqrt(deff)) if len(valid) > 1 else float('nan')
    return {
        'DetRate': det_rate, 'CI_low': ci_low, 'CI_high': ci_high, 'ADD': add_val,
        'SEM': sem_val, 'n_detected': len(valid), 'deff': deff, 'deff_clamped': clamped,
        'deff_lags': lags, 'n_eff': n_eff, 'SEM_design': sem_design,
        'distinct_starts': len(set(valid_starts)),
    }, valid, valid_starts


def run_race(eps_real_full, compositions, K_grid, lambdas, n_jobs, n_distinct, log):
    """
    The delivered two-phase race, with the reference arm computed once per c on
    the K = 1 sub-panel and the panel arm once per (K, c).
    """
    T_full = eps_real_full.shape[1]
    eps_1_full = eps_real_full[compositions[1], :]
    lam_b_1 = lambdas[1]

    reference = {}
    window_rows = []
    with _Pool(eps_1_full, n_jobs) as pool:
        for c_index, c in enumerate(C_GRID):
            seeds = [get_deterministic_seed("race_h1_ref", c_index, i) for i in range(N_RACE)]
            out = pool.map(_race_task, seeds, repeat(c), repeat(lam_b_1), total=N_RACE)
            delays = [d for d, _ in out]
            starts = [t for _, t in out]
            stats_ref, valid, valid_starts = aggregate_cell(
                delays, starts, n_distinct, f"reference c={c}", log)
            reference[c_index] = stats_ref
            window_rows.extend({'arm': 'reference', 'K': 1, 'c': c, 'replicate': i,
                                't_start': t, 'delay': d}
                               for i, (d, t) in enumerate(zip(delays, starts)))
            log.info(f"Reference arm c={c}: ADD_single={stats_ref['ADD']!r}, "
                     f"DetRate={stats_ref['DetRate']!r}, n_detected={stats_ref['n_detected']}, "
                     f"deff={stats_ref['deff']:.6f}.")

    cells = {}
    for k_index, K in enumerate(K_grid):
        eps_K_full = eps_real_full[compositions[K], :]
        lam_b = lambdas[K]
        with _Pool(eps_K_full, n_jobs) as pool:
            for c_index, c in enumerate(C_GRID):
                seeds = [get_deterministic_seed("race_h1", k_index, c_index, i)
                         for i in range(N_RACE)]
                out = pool.map(_race_task, seeds, repeat(c), repeat(lam_b), total=N_RACE)
                delays = [d for d, _ in out]
                starts = [t for _, t in out]
                cell, valid, valid_starts = aggregate_cell(
                    delays, starts, n_distinct, f"K={K} c={c}", log)
                cell['valid'] = valid
                cell['valid_starts'] = valid_starts
                cells[(c_index, k_index)] = cell
                window_rows.extend({'arm': 'panel', 'K': K, 'c': c, 'replicate': i,
                                    't_start': t, 'delay': d}
                                   for i, (d, t) in enumerate(zip(delays, starts)))

    rows = []
    for c_index, c in enumerate(C_GRID):
        ref = reference[c_index]
        add_single = ref['ADD']
        for k_index, K in enumerate(K_grid):
            cell = cells[(c_index, k_index)]
            add_reliable = int(cell['DetRate'] >= DET_RATE_FLOOR)
            budget_reduction = (add_single / cell['ADD']
                                if (add_reliable and not np.isnan(add_single))
                                else float('nan'))
            rows.append({
                'K': K, 'c': c, 'k_index': k_index, 'c_index': c_index,
                'DetRate': cell['DetRate'], 'CI_low': cell['CI_low'],
                'CI_high': cell['CI_high'], 'ADD': cell['ADD'], 'SEM': cell['SEM'],
                'ADD_single': add_single, 'budget_reduction': budget_reduction,
                'add_reliable': add_reliable,
                'n_detected': cell['n_detected'], 'deff': cell['deff'],
                'deff_clamped': cell['deff_clamped'], 'deff_lags': cell['deff_lags'],
                'n_eff': cell['n_eff'], 'SEM_design': cell['SEM_design'],
                'distinct_starts': cell['distinct_starts'],
                'ADD_single_DetRate': ref['DetRate'],
                'ADD_single_reliable': int(ref['DetRate'] >= DET_RATE_FLOOR),
                'ADD_single_SEM': ref['SEM'], 'ADD_single_SEM_design': ref['SEM_design'],
                'ADD_single_n_detected': ref['n_detected'],
            })
    return pd.DataFrame(rows), pd.DataFrame(window_rows), cells, reference


# --- PHASE 3: THE COVID NATURAL EXPERIMENT ---

def run_covid(eps_real_full, dates, compositions, K_grid, calibration, lambdas, log):
    """
    The delivered natural experiment, carried whole. It carries NO RNG: the
    window is the calendar, so only the two thresholds are redrawn.
    """
    idx_onset = int(np.argmin(np.abs(dates - pd.to_datetime(COVID_ONSET))))
    end_idx = min(idx_onset + H_DET, len(dates))
    if idx_onset - H_REF < 0:
        log.error(f"The COVID onset sits at index {idx_onset}, less than H_ref = {H_REF} days "
                  f"into the panel, so the delivered recentring window does not exist.")
        sys.exit(1)
    log.info(f"COVID natural experiment: onset {COVID_ONSET} maps to index {idx_onset} "
             f"({dates[idx_onset].date()}), reference window "
             f"[{dates[idx_onset - H_REF].date()}..{dates[idx_onset - 1].date()}], detection "
             f"window [{dates[idx_onset].date()}..{dates[end_idx - 1].date()}] "
             f"({end_idx - idx_onset} of the {H_DET} days H_det asks for -- the panel ends "
             f"{dates[-1].date()}).")
    rows = []
    calib = calibration.set_index('K')
    for K in K_grid:
        eps_covid = eps_real_full[compositions[K], idx_onset - H_REF: end_idx]
        med = np.median(eps_covid[:, :H_REF], axis=1, keepdims=True)
        std = np.std(eps_covid[:, :H_REF], axis=1, keepdims=True)
        std[std == 0] = 1.0
        eps_centered = (eps_covid - med) / std
        x_covid = fraction_stream(eps_centered)[H_REF:]
        delay_naive = bilateral_delay(x_covid, 0.0, float(calib.loc[K, 'lambda_naive']))
        delay_boot = bilateral_delay(x_covid, 0.0, lambdas[K])
        det_date = dates[idx_onset + delay_boot].date() if delay_boot != -1 else None
        log.info(f"COVID K={K}: Delay Naive = {delay_naive}, Delay Boot = {delay_boot}"
                 + (f", detection date {det_date}" if det_date is not None else ""))
        rows.append({'K': K, 'delay_boot': delay_boot, 'delay_naive': delay_naive,
                     'detection_date': det_date})
    return pd.DataFrame(rows), idx_onset, end_idx


def check_covid_sentinel(covid, log):
    """
    C7, a D3 GATE. v87 L376 states that the pooled monitor "still never flags the
    2020 crash". `-1` is a sentinel by CONSTRUCTION -- `bilateral_delay` returns
    it iff neither one-sided CUSUM crosses -- so the claim is the assertion
    `delay_boot == -1` at every K, and the sentinel must never enter a mean.

    `lambda_boot` IS REDRAWN BY THE MIGRATION, so this is a live risk and not a
    formality: a lower regenerated threshold detects. If one K detects, the run
    halts, reports in full, and reconciles nothing.
    """
    detected = covid[covid['delay_boot'] != -1]
    log.info(f"C7: the sentinel -1 is returned by `bilateral_delay` iff neither one-sided CUSUM "
             f"crosses, so it is a NON-DETECTION and never a delay of -1 day. It enters no mean "
             f"anywhere in this file. lambda_boot is redrawn by the entropy migration, so this "
             f"gate is live. Deterministic given the regenerated thresholds.")
    if len(detected):
        log.error(f"C7 FIRED. v87 L376 states the pooled monitor 'still never flags the 2020 "
                  f"crash'. The regenerated campaign DETECTS at "
                  f"{detected[['K', 'delay_boot', 'detection_date']].to_dict('records')}. This "
                  f"is a falsified qualitative claim of the manuscript (preamble S3, D3). The "
                  f"run stops here: no threshold, seed, dead band or window is moved to "
                  f"reconcile it, and the --witness-blas arm is what attributes the difference.")
        sys.exit(1)
    naive_detections = covid[covid['delay_naive'] != -1]
    log.info(f"C7: delay_boot == -1 at all {len(covid)} values of K, so the claim holds. The "
             f"NAIVE threshold, by contrast, fires at {len(naive_detections)} of {len(covid)} "
             f"values of K ({sorted(naive_detections['K'].tolist())}) -- those are FALSE ALARMS "
             f"of a threshold that already runs at up to 100% false-alarm rate under the null, "
             f"not detections, and no macro reads delay_naive.")


# --- THE SCATTER CORRELATION OF THE FIGURE 17 CAPTION ---

def scatter_correlations(race, calibration, K_grid, log):
    """
    `\\RFifteenScatterCorrelation`. NO LINE OF EITHER WITNESS SCRIPT COMPUTES A
    CORRELATION, so R15 must define one, and the referent is fixed ON THE TEXT.

    The caption reads: "Point-to-point scatter reflects threshold variations
    across panel compositions (r >= 0.99 with bootstrap threshold)". The
    referent of "with bootstrap threshold" is `lambda_boot`; the referent of
    "scatter" is panel B's ORDINATE, which the delivered plotting code (line
    378-380) fixes as `budget_reduction` at `c = C_GRID[1] = 0.25`, one curve
    and no other.

    Reading 1, PUBLISHED: Pearson r between `budget_reduction` and
    `lambda_boot` over the ten K, computed at EVERY c and all five persisted;
    the macro is emitted for the c the plotting code draws.
    Reading 2, PERSISTED, no macro and no register entry: Pearson r between
    `ADD` and `lambda_boot`, same c. It documents that the sentence admits a
    second reading and that the first was chosen on the text.

    ORDER OF OPERATIONS, RECORDED AS SEQUENCE AND NOT AS DEFENCE. Both readings
    were computed during planning, on the WITNESS campaign, BEFORE the referent
    was fixed: reading 1 gives -0.9894 and reading 2 gives +0.9947 there. The
    selection was made on the textual referent -- panel B's ordinate against
    lambda_boot -- and on nothing else. Choosing after seeing which sign matched
    the caption would be selection on the outcome, which preamble S4 bans.
    """
    lam = calibration.set_index('K')['lambda_boot']
    rows = []
    for c_index, c in enumerate(C_GRID):
        sub = race[race['c'] == c].set_index('K').reindex(K_grid)
        usable = sub['budget_reduction'].notna().to_numpy()
        n = int(usable.sum())
        thresholds = lam.reindex(sub.index[usable]).to_numpy(dtype=float)
        r_budget = (float(np.corrcoef(sub['budget_reduction'].to_numpy(dtype=float)[usable],
                                      thresholds)[0, 1]) if n > 2 else float('nan'))
        add_usable = sub['ADD'].notna().to_numpy()
        n_add = int(add_usable.sum())
        r_add = (float(np.corrcoef(sub['ADD'].to_numpy(dtype=float)[add_usable],
                                   lam.reindex(sub.index[add_usable]).to_numpy(dtype=float))[0, 1])
                 if n_add > 2 else float('nan'))
        rows.append({'c': c, 'c_index': c_index, 'is_plotted_c': int(c_index == C_TARGET_INDEX),
                     'n_points_budget': n, 'r_budget_vs_lambda_boot': r_budget,
                     'n_points_add': n_add, 'r_add_vs_lambda_boot': r_add})
        log.info(f"Scatter correlation c={c}"
                 f"{' (THE PLOTTED c, C_GRID[1])' if c_index == C_TARGET_INDEX else ''}: "
                 f"reading 1, r(budget_reduction, lambda_boot) = {r_budget!r} over {n} K; "
                 f"reading 2, r(ADD, lambda_boot) = {r_add!r} over {n_add} K.")
    return pd.DataFrame(rows)


# --- THE FIGURE ---

def render_figure(diag, race, path, log):
    c_target = C_GRID[C_TARGET_INDEX]
    sub = race[race['c'] == c_target].sort_values('K')
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

    ax = axes[0]
    ax.plot(diag['K'], diag['FPR_naive'], marker='o', linestyle='-', color='red',
            label='FPR naive (independence calibration)')
    ax.plot(diag['K'], diag['FPR_boot'], marker='x', linestyle='--', color='blue',
            label='FPR bootstrap (real-window calibration)')
    # The Wilson interval of each bootstrap point, widened by the F3 factor:
    # the calibration and evaluation windows are drawn from the same finite
    # population of window starts, so the binomial interval understates.
    scale = (diag['SE_FPR_boot_design'] / diag['SE_FPR_boot_binomial']).to_numpy(dtype=float)
    centre = diag['FPR_boot'].to_numpy(dtype=float)
    lo = centre - scale * (centre - diag['FPR_boot_CI_low'].to_numpy(dtype=float))
    hi = centre + scale * (diag['FPR_boot_CI_high'].to_numpy(dtype=float) - centre)
    ax.fill_between(diag['K'], np.clip(lo, 0.0, 1.0), np.clip(hi, 0.0, 1.0),
                    color='blue', alpha=0.15,
                    label='Wilson interval x design-effect factor')
    ax.axhline(0.05, color='black', linestyle=':', label='Target 5%')
    first = diag.iloc[0]
    ax.plot([first['K']], [first['FPR_naive']], marker='s', markersize=11,
            markerfacecolor='none', markeredgecolor='darkred', linestyle='none',
            label=r'$K=1$: $\rho_{\mathrm{sign}}=0$, $K_{\mathrm{eff}}=1$ exactly')
    ax.set_xscale('log')
    ax.set_xlabel('Panel size $K$ (real data)')
    ax.set_ylabel('False positive rate')
    ax.set_title("(A) Independence calibration loses its level; the real-window bootstrap holds it",
                 fontweight="bold", loc="center", fontsize=9.5)
    ax.legend(fontsize=7.5, loc='center right')

    ax = axes[1]
    ax.plot(sub['K'], sub['budget_reduction'], marker='s', linestyle='-', color='purple',
            label=rf'Realized $\mathrm{{ADD}}_{{K=1}}/\mathrm{{ADD}}_K$ ($c={c_target}$)')
    ax.plot(diag['K'], np.sqrt(diag['K_eff_meas']), marker='x', linestyle=':', color='black',
            linewidth=2, label=r'$\sqrt{K_{\mathrm{eff}}}$ (delay-ratio scale)')
    ax.plot(diag['K'], diag['K_eff_meas'], linestyle='-.', color='gray', linewidth=1.5,
            label=r"$K_{\mathrm{eff}}$ (the caption's bound)")
    ax2 = ax.twinx()
    ax2.plot(diag['K'], diag['lambda_boot'], marker='.', linestyle='--', color='darkorange',
             linewidth=1.2, alpha=0.8, label=r'Bootstrap threshold $\lambda_{\mathrm{boot}}$')
    ax2.set_ylabel(r'$\lambda_{\mathrm{boot}}$', color='darkorange')
    ax2.tick_params(axis='y', labelcolor='darkorange')
    ax.set_xscale('log')
    ax.set_xlabel('Panel size $K$ (real data)')
    ax.set_ylabel(rf'Budget reduction $\mathrm{{ADD}}_{{K=1}}/\mathrm{{ADD}}_K$ ($c={c_target}$)')
    ax.set_title("(B) Realized budget reduction against both candidate ceilings",
                 fontweight="bold", loc="center", fontsize=9.5)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc='upper left', fontsize=8.0, framealpha=0.95,
              facecolor='white')

    plt.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    log.info(f"Figure written to {path.name}. Panel B draws BOTH candidate ceilings: "
             f"sqrt(K_eff), which is the delivered script's own reference line and the one "
             f"commensurable with a ratio of delays, and K_eff, which is what the caption's "
             f"'bounded by the effective panel size K_eff ~ 3.8' names. Which of the two the "
             f"realized curve respects is a finding of this stream, not a choice of this plot.")


# --- CLASSIFICATION AGAINST v87 (preamble S3) ---

def witness_scatter_r(witnesses, c_target):
    """
    Reading 1 recomputed on the SUBMITTED campaign by the identical rule, so
    that the classification of `R15-scatter-sign` compares two measurements and
    never a measurement against a transcribed literal.
    """
    w_race, w_diag = witnesses['race'], witnesses['diagnostics']
    plotted = w_race[w_race['c'] == c_target].sort_values('K')
    lam = w_diag.set_index('K')['lambda_boot']
    usable = plotted['budget_reduction'].notna().to_numpy()
    return float(np.corrcoef(plotted['budget_reduction'].to_numpy(dtype=float)[usable],
                             lam.reindex(plotted['K'].to_numpy()[usable]).to_numpy(dtype=float))
                 [0, 1])


def classify(label, regenerated, witness, printed, decimals, log):
    """
    Preamble S3, computed rather than asserted. D0 is bit identity with the
    witness; D1 is a move that leaves v87's printed rounding unchanged; anything
    else is at least D2, and whether it is a D3 is a question about a
    qualitative claim, decided separately and never by this function.
    """
    if witness is not None and float(regenerated) == float(witness):
        verdict = "D0"
    elif round(float(regenerated), decimals) == round(float(printed), decimals):
        verdict = "D1"
    else:
        verdict = "D2 or worse -- the qualitative claim is examined separately"
    log.info(f"S3 [{label}]: v87 prints {printed!r} at {decimals} decimals; witness "
             f"{witness!r}; regenerated {float(regenerated)!r} -> rounds to "
             f"{round(float(regenerated), decimals)!r}. Class {verdict}.")
    return verdict


def main():
    parser = argparse.ArgumentParser(
        description="R15 (b) -- cross-sectional escape on a real equity panel "
                    "(v87 Figure 17, L376)")
    parser.add_argument("--n-jobs", type=int, default=-1,
                        help="Worker processes. The campaign is keyed per task and "
                             "`executor.map` preserves submission order, so every artefact is "
                             "invariant to this value; `--n-jobs 1` is control C10's second axis.")
    parser.add_argument("--witness-blas", action="store_true",
                        help="Attribution arm. Removes MKL_CBWR before NumPy loads, which is the "
                             "environment the submitted campaign ran under, and stamps every "
                             "output '_witness_blas'. It CERTIFIES NO v87 VALUE: it separates "
                             "'the BLAS summation order moved this' from 'the port moved this'.")
    parser.add_argument("--data-source", choices=["yfinance"], default="yfinance",
                        help="Accepted and forwarded from the orchestrator; the panel is read "
                             "from data/derived_equities/ in every case.")
    parser.add_argument("--stage", choices=["ingest", "analyse", "all"], default="analyse",
                        help="Accepted and forwarded from the orchestrator; this stage has one "
                             "path and it is offline.")
    args = parser.parse_args()
    sfx = WITNESS_BLAS_SUFFIX if args.witness_blas else ""
    n_jobs = args.n_jobs if args.n_jobs > 0 else (os.cpu_count() or 1)

    RESULTS_DIR = BASE_DIR / "results" / "R15_cross_sectional"
    DATA_DIR = RESULTS_DIR / "data"
    FIGURES_DIR = RESULTS_DIR / "figures"
    TABLES_DIR = RESULTS_DIR / "tables"
    LOGS_DIR = BASE_DIR / "logs" / "R15_cross_sectional"
    REQUIREMENTS_DIR = BASE_DIR / "requirements"
    for d in (DATA_DIR, FIGURES_DIR, TABLES_DIR, LOGS_DIR, REQUIREMENTS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    log = setup_logging(LOGS_DIR / f"exp_R15_cross_sectional_b{sfx}.log", f"exp_R15_b{sfx}")
    if not verify_hash_seed(log):
        sys.exit(1)
    versions = log_environment(log, list(REQUIREMENT_PACKAGES))
    (REQUIREMENTS_DIR / "R15.txt").write_text(
        "".join(f"{name}=={versions[name]}\n" for name in REQUIREMENT_PACKAGES))
    t0 = time.time()

    log.info("R15 (b) regenerates v87 Figure 17 (fig:cross_section) and every numeral of L376: "
             "the cross-sectional sign monitor on 97 surviving US equities, 2005-2025, under an "
             "independence calibration and under a real-window bootstrap.")
    log.info(f"Worker processes requested: {n_jobs}. `executor.map` preserves submission order "
             f"and every task is keyed, so no artefact depends on this number (control C10).")
    if args.witness_blas:
        log.warning("WITNESS-BLAS ATTRIBUTION ARM. MKL_CBWR was removed before NumPy loaded, "
                    "which restores the summation order of the submitted campaign; the four "
                    "thread pins are unchanged. Every output is stamped "
                    f"'{WITNESS_BLAS_SUFFIX}' and CERTIFIES NO v87 VALUE. This arm exists to "
                    "attribute a residual, not to pass a check: it separates the BLAS "
                    "instruction-set constraint from a transcription error in this port. It runs "
                    "unconditionally and after the default arm, because a diagnostic executed "
                    "only when a result looks wrong is an instrument of selection.")
    else:
        log.info(f"MKL_CBWR = {os.environ.get('MKL_CBWR')!r}: the repository's canonical "
                 f"determinism bootstrap. It constrains the BLAS to one instruction-set "
                 f"behaviour, which is NOT the one the submitted campaign ran under. The "
                 f"consequence is measured by control C1 leg 3 below and registered as "
                 f"`R15-mkl-cbwr-rho`.")

    # --- SPECIFICATION, LOGGED AND NOT MERELY CODED (S2.7) ---
    if not PANEL_PATH.exists():
        log.error(f"[FATAL] {PANEL_PATH} is missing. Run exp_R15_cross_sectional_a.py first.")
        sys.exit(1)
    digest = compute_sha256(PANEL_PATH)
    panel_frame = pd.read_csv(PANEL_PATH, index_col="Date", parse_dates=True,
                              float_precision='round_trip')
    eps_real_full = panel_frame.values.T
    tickers = panel_frame.columns.tolist()
    dates = panel_frame.index
    K_max, T_full = eps_real_full.shape
    K_GRID = list(K_GRID_PREFIX) + [K_max]
    n_distinct = T_full - (H_REF + H_DET) + 1
    log.info(f"Panel {PANEL_PATH.name}: {K_max} tickers x {T_full} days "
             f"[{dates.min().date()}..{dates.max().date()}], SHA-256 {digest} "
             f"(submitted campaign: {PANEL_SHA256}; match: {digest == PANEL_SHA256}).")
    log.info(f"SPECIFICATION: H_ref={H_REF}, H_det={H_DET} ('finite real panel: shorter horizon "
             f"=> more distinct, less-overlapping windows', delivered line 173), "
             f"TARGET_FPR={TARGET_FPR}, N_CAL={N_CAL}, N_RACE={N_RACE}, "
             f"MASTER_SEED={MASTER_SEED}, DET_RATE_FLOOR={DET_RATE_FLOOR}, "
             f"K_GRID={K_GRID} (K_max read from the panel, never typed), C_GRID={list(C_GRID)}, "
             f"plotted c = C_GRID[{C_TARGET_INDEX}] = {C_GRID[C_TARGET_INDEX]}.")
    log.info(f"SPECIFICATION OF A BRANCH THIS PORT DOES NOT RUN, recorded so the omission is "
             f"legible: the delivered `--source synthetic` branch carries "
             f"{SYNTHETIC_BRANCH_SPEC}. It produces Figure 29, which is NOT in v87, and the "
             f"scope filter of this stream is strictly v87's content. The `--fast` branch is "
             f"removed outright: a second grid is a second campaign and v87 publishes one.")
    log.info(f"THE WINDOW POPULATION IS FINITE AND SMALL, and every design effect below follows "
             f"from it: H_ref + H_det = {H_REF + H_DET} on T = {T_full} days admits exactly "
             f"{n_distinct} distinct window starts. N_CAL = {N_CAL} draws therefore enumerate "
             f"that population about {N_CAL / n_distinct:.1f} times over, and two windows can "
             f"share up to {H_REF + H_DET - 1} of their {H_REF + H_DET} days. The calibration "
             f"and evaluation sets are DISJOINT IN SEED and drawn from the SAME "
             f"{n_distinct} windows.")

    check_source_identity(log)
    check_grid_provenance(log)
    witness_statements = check_carried_statements(log)
    compositions = check_composition(log, witness_statements, K_GRID, K_max)

    composition_frame = pd.DataFrame(
        [{'K': K, 'k_index': k_index, 'position': j, 'asset_index': int(idx),
          'ticker': tickers[int(idx)]}
         for k_index, K in enumerate(K_GRID)
         for j, idx in enumerate(compositions[K])])
    log.info(f"Frozen compositions, made inspectable rather than implicit: "
             + "; ".join(f"K={K} -> {[tickers[int(i)] for i in compositions[K]][:5]}"
                         + ("..." if K > 5 else "") for K in K_GRID))

    witnesses = read_witness_csvs(log)
    diagnostics = run_diagnostics(eps_real_full, compositions, K_GRID, log)
    check_degeneracy_at_k_one(eps_real_full, compositions, diagnostics, log)
    classify_diagnostics_against_witness(
        diagnostics, witnesses['diagnostics'], K_GRID, T_full, log)
    keff_at_max = float(diagnostics[diagnostics['K'] == K_max]['K_eff_meas'].iloc[0])

    # =====================================================================
    # CONTROL C2 -- K_eff CONSISTENCY, MEASURED AND NOT GATED
    # =====================================================================
    gap = ((diagnostics['K_eff_meas'] - diagnostics['K_eff_ana']).abs()
           / diagnostics['K_eff_ana'])
    gap_max = float(gap.max())
    gap_at = int(diagnostics['K'].iloc[int(gap.to_numpy().argmax())])
    # The envelope is derived from the SAMPLING ERROR of rho and never from the
    # observed gap: SE(rho) ~ 1/sqrt(T) for a correlation near 0, and
    # K_eff_ana = K/(1+(K-1)rho) has d log K_eff_ana / d rho = -(K-1)/(1+(K-1)rho),
    # so a one-SE move of rho displaces K_eff_ana by (K-1)/((1+(K-1)rho)*sqrt(T))
    # in relative terms.
    se_rho = 1.0 / np.sqrt(T_full)
    envelope = ((diagnostics['K'] - 1)
                / (1.0 + (diagnostics['K'] - 1) * diagnostics['rho_sign_meas']) * se_rho)
    log.info(f"C2 -- consistency of the two K_eff estimators. Max relative gap "
             f"|K_eff_meas - K_eff_ana| / K_eff_ana = {gap_max:.6e} at K = {gap_at}. It is an "
             f"EXTREMUM OVER A GRID and therefore gates nothing (S4bis, fourth corollary). Its "
             f"envelope is derived from SE(rho) ~ 1/sqrt(T) = {se_rho:.6e}, NEVER from the "
             f"observed gap: a one-SE move of rho displaces K_eff_ana by "
             f"{float(envelope.max()):.3e} in relative terms at its widest (K = "
             f"{int(diagnostics['K'].iloc[int(envelope.to_numpy().argmax())])}), so the measured "
             f"gap sits at {gap_max / float(envelope.max()):.4f} of one sampling standard error "
             f"of the input it is a function of.")
    diagnostics['K_eff_relative_gap'] = gap
    diagnostics['K_eff_gap_envelope'] = envelope

    # =====================================================================
    # CONTROL C4 -- WHITENESS, AND THE ARITHMETIC BEFORE THE INTERPRETATION
    # =====================================================================
    n_lb = len(diagnostics)
    log.info(f"C4 -- temporal whiteness of P_t, ten Ljung-Box tests at lag 20. THE FAMILY-WISE "
             f"ARITHMETIC, LOGGED BEFORE ANY INTERPRETATION: reading {n_lb} independent tests at "
             f"the 5% level as one verdict triggers with probability "
             f"1 - 0.95^{n_lb} = {1 - 0.95 ** n_lb:.3f} = {1 - 0.95 ** n_lb:.1%} under a true "
             f"null of whiteness at every K. The publishable statistic is therefore the SWITCH "
             f"POINT max{{K : p >= 0.05}}, which is RNG-free and reads one boundary rather than "
             f"ten tests.")
    passing = diagnostics[diagnostics['ljungbox_p_Pt'] >= 0.05]['K']
    switch_k = int(passing.max()) if len(passing) else 0
    ks = stats.kstest(diagnostics['ljungbox_p_Pt'].to_numpy(dtype=float), 'uniform')
    log.info(f"C4: whiteness holds up to K = {switch_k} and fails from K = "
             f"{int(diagnostics[diagnostics['ljungbox_p_Pt'] < 0.05]['K'].min())} onward. The "
             f"p-values in K order: "
             + ", ".join(f"K={int(r.K)}: {r.ljungbox_p_Pt:.4e}"
                         for r in diagnostics.itertuples()) + ".")
    log.info(f"C4 KS STATISTIC, DESCRIPTIVE AND NON-NULL-BEARING: D = {ks.statistic!r}, "
             f"p = {ks.pvalue!r} against Uniform(0,1). IT IS NOT A TEST HERE AND GATES NOTHING. "
             f"The ten p-values come from nested-in-distribution asset subsets of ONE panel over "
             f"ONE common {T_full}-day index -- K = 5 is a subset of the same 97 series as "
             f"K = 97 -- so they are strongly dependent and the Uniform(0,1) null does not hold "
             f"even under perfect whiteness. It is persisted because a statistic computed and "
             f"withheld is worse than one computed and qualified.")

    calibration, lambdas, _, n_distinct = calibrate(
        eps_real_full, compositions, K_GRID, n_jobs, log)

    # =====================================================================
    # CONTROL C3 -- THE STANDARD ERROR OF FPR_boot, RE-DERIVED
    # =====================================================================
    log.info(f"C3 -- the uncertainty of FPR_boot. THE R15 PROMPT'S sqrt(2) RULE IS NOT IMPORTED. "
             f"R04b established a variance doubling for n_cal = n_eval; here N_CAL = {N_CAL} and "
             f"N_RACE = {N_RACE}, so the first-order delta-method variance is "
             f"p(1-p)/n_r + alpha(1-alpha)/n_c and the multiplier would be "
             f"sqrt(1 + n_r/n_c) = {np.sqrt(1 + N_RACE / N_CAL):.4f}, not "
             f"{np.sqrt(2.0):.4f}. Preamble S4bis's fifth corollary forbids importing R04b's rule "
             f"un-re-derived. NEITHER MULTIPLIER IS CORRECT ANYWAY: with only {n_distinct} "
             f"distinct windows the two sets are drawn from the SAME population and overlap in "
             f"DATA by up to {H_REF + H_DET - 1} of {H_REF + H_DET} days, so the uncertainty is "
             f"not Monte-Carlo and no fixed multiplier produces it. What is published instead is "
             f"SE = sqrt(deff_r * p(1-p)/n_r + deff_c * alpha(1-alpha)/n_c) with BOTH design "
             f"effects measured on the t_start-ordered exceedance indicators. IT GATES NOTHING.")
    for row in calibration.itertuples():
        log.info(f"C3 K={row.K}: deff_eval = {row.deff_eval:.6f} over {row.deff_eval_lags} "
                 f"mechanism-fixed lags (n_eff = {row.n_eff_eval:.1f} of {N_RACE}), "
                 f"deff_calib = {row.deff_calib:.6f} over {row.deff_calib_lags} lags "
                 f"(n_eff = {row.n_eff_calib:.1f} of {N_CAL}); SE_design = "
                 f"{row.SE_FPR_boot_design:.6f}, against {row.SE_FPR_boot_sqrt2_rule:.6f} from "
                 f"the literal sqrt(2) rule and {row.SE_FPR_boot_binomial:.6f} from the bare "
                 f"binomial; {row.distinct_windows_used} distinct starts used of "
                 f"{row.distinct_windows_available} available.")

    # =====================================================================
    # THE MARGINAL CHANNEL AT K = 1 (measurement, not gate)
    # =====================================================================
    first = calibration.iloc[0]
    log.info(f"THE FPR_naive DECOMPOSITION, AND WHERE IT STOPS BEING IDENTIFIABLE. At K = 1, "
             f"control C1 establishes rho_sign_meas = 0 and K_eff_meas = 1 EXACTLY, so NO "
             f"cross-sectional correlation exists there to be ignored -- and yet FPR_naive = "
             f"{float(first['FPR_naive']):.4f}, {float(first['FPR_naive']) / TARGET_FPR:.1f}x its "
             f"nominal level. That excess is NOT attributable to the mechanism the Figure 17 "
             f"caption names. The measurable marginal channel is q_hat = P(z > 0) on the H_det "
             f"half against the H_ref median, which the naive calibration fixes at 0.5 by "
             f"assumption: measured mean {float(first['q_hat_mean']):.6f} "
             f"(sd {float(first['q_hat_sd']):.6f}, range [{float(first['q_hat_min']):.4f}, "
             f"{float(first['q_hat_max']):.4f}]) at K = 1.")
    log.info(f"THE CROSS-SECTIONAL CHANNEL is reported as the INCREMENT FPR_naive(K) - "
             f"FPR_naive(1): "
             + ", ".join(f"K={int(r.K)}: {float(r.FPR_naive) - float(first['FPR_naive']):+.4f}"
                         for r in calibration.itertuples()) + ". THE DECOMPOSITION IS NOT "
             f"IDENTIFIABLE UNDER v87's DESIGN and this section says so rather than asserting a "
             f"mechanism: q_hat and rho_sign both move with K along a single arm, there is no "
             f"arm holding one fixed while the other varies, and the marginal and "
             f"cross-sectional contributions to FPR_naive cannot be separated from these ten "
             f"cells. What IS established is the boundary case: at K = 1 the correlation channel "
             f"is exactly empty and the excess is entirely marginal.")

    race, race_windows, cells, reference = run_race(
        eps_real_full, compositions, K_GRID, lambdas, n_jobs, n_distinct, log)
    log.info(f"THE K = 1 PAIRING THE MIGRATION BREAKS, reported before its consequence is read. "
             f"The delivered reference seed string `real_race1_1_{{c}}_{{MASTER_SEED}}_{{i}}` and "
             f"the delivered panel seed string at K = 1 are the SAME STRING on the SAME "
             f"sub-panel, so the submitted budget_reduction(K = 1) is exactly 1.0 BY "
             f"CONSTRUCTION. The migrated keys ('race_h1', k_index, c_index, i) and "
             f"('race_h1_ref', c_index, i) separate the two roles, so the regenerated K = 1 cell "
             f"is an honest estimate of 1 with sampling error: "
             + ", ".join(f"c={r.c}: {r.budget_reduction!r}"
                         for r in race[race['K'] == 1].itertuples()) + ".")

    covid, idx_onset, end_idx = run_covid(
        eps_real_full, dates, compositions, K_GRID, calibration, lambdas, log)
    check_covid_sentinel(covid, log)

    # =====================================================================
    # CONTROL C6 -- WHAT MAY BE READ, AND WHAT THE FLAG DOES NOT COVER
    # =====================================================================
    unreliable = race[race['add_reliable'] == 0]
    log.info(f"C6 -- no macro and no published aggregate reads a row with add_reliable == 0. "
             f"{len(unreliable)} of {len(race)} cells are unreliable: "
             f"{[(int(r.K), float(r.c), round(float(r.DetRate), 4)) for r in unreliable.itertuples()]}. "
             f"Structural; trigger probability 0.")
    if bool(race[race['add_reliable'] == 0]['budget_reduction'].notna().any()):
        log.error("C6 FAILED: an unreliable cell carries a budget_reduction.")
        sys.exit(1)
    censored_ref = race[(race['ADD_single_reliable'] == 0) & (race['add_reliable'] == 1)]
    log.info(f"C6 EXTENDED, AND THE FLAG DOES NOT PROPAGATE. `add_reliable` describes the PANEL "
             f"arm of a cell and says nothing about the REFERENCE arm its budget_reduction "
             f"divides by. At c = "
             f"{sorted(set(float(c) for c in censored_ref['c']))} the reference arm itself "
             f"detects at "
             f"{sorted(set(round(float(d), 4) for d in censored_ref['ADD_single_DetRate']))}, "
             f"below the {DET_RATE_FLOOR} floor, so ADD_single is CENSORED -- a mean over the "
             f"detected subset of a cell that mostly does not detect -- and every one of the "
             f"{len(censored_ref)} cells inheriting it is nonetheless flagged reliable. This is "
             f"REPORTED, not repaired: it does not touch the published c = "
             f"{C_GRID[C_TARGET_INDEX]} macro, whose reference arm detects at "
             f"{float(race[race['c'] == C_GRID[C_TARGET_INDEX]]['ADD_single_DetRate'].iloc[0]):.4f}.")

    # =====================================================================
    # CONTROL C5 -- THE PLATEAU, ANNOUNCED BEFORE IT IS READ
    # =====================================================================
    c_target = C_GRID[C_TARGET_INDEX]
    log.info(f"C5 -- the plateau statistic, ANNOUNCED BEFORE THE REGENERATED VALUE IS READ. v87's "
             f"Figure 17 caption says the realized budget reduction 'plateaus near 2x "
             f"(K >= {PLATEAU_K_MIN})'. The delivered script computes budget_reduction per "
             f"(K, c) cell at line 311 AND AGGREGATES NOWHERE; the only selection of a magnitude "
             f"in the whole file is the plotting line 378, `c_target = C_GRID[1]`, and lines "
             f"379-380 draw exactly one budget_reduction curve, at that c. With C_GRID = "
             f"{list(C_GRID)} that c is {c_target}. THE PUBLISHED PLATEAU IS THEREFORE THE MEAN "
             f"OF THE PLOTTED c = {c_target} SERIES OVER K >= {PLATEAU_K_MIN}. It is established "
             f"by reading the plotting code, not selected among candidates. On the submitted "
             f"campaign that mean is 2.0086. It is neither the maximum nor the minimum over c, "
             f"and no macro reads either.")
    plotted = race[race['c'] == c_target].sort_values('K')
    plateau_rows = plotted[plotted['K'] >= PLATEAU_K_MIN]
    plateau = float(plateau_rows['budget_reduction'].mean())
    # A delta-method envelope built from the DESIGN-CORRECTED standard errors of
    # the cells the mean pools, not from a resample of the seven grid points: the
    # K grid is a design, not a sample, and resampling it would answer a question
    # nobody asked. plateau = add_single * mean_K(1/ADD_K), so
    # d/d add_single = plateau/add_single and d/d ADD_K = -add_single/(m*ADD_K^2).
    add_single = float(plateau_rows['ADD_single'].iloc[0])
    se_single = float(plateau_rows['ADD_single_SEM_design'].iloc[0])
    m = len(plateau_rows)
    var = (plateau / add_single) ** 2 * se_single ** 2
    for r in plateau_rows.itertuples():
        var += (add_single / (m * float(r.ADD) ** 2)) ** 2 * float(r.SEM_design) ** 2
    se_plateau = float(np.sqrt(var))
    log.info(f"C5: the regenerated plateau is {plateau!r} over the {m} cells "
             f"{sorted(int(k) for k in plateau_rows['K'])} at c = {c_target}, with a "
             f"delta-method standard error of {se_plateau:.6f} propagated from the "
             f"DESIGN-CORRECTED SEMs of the {m} panel cells and of the shared reference arm "
             f"(the cells share ADD_single, so they are not independent and a naive sum of "
             f"variances would understate). Per-cell values: "
             + ", ".join(f"K={int(r.K)}: {float(r.budget_reduction):.4f}"
                         for r in plateau_rows.itertuples()) + ".")
    # WHICH CEILING THE REALIZED CURVE RESPECTS. Panel B of the delivered figure
    # draws sqrt(K_eff) (line 381); the caption names K_eff. They are different
    # claims and only one of them can be the bound the curve obeys.
    merged = plotted.merge(diagnostics[['K', 'K_eff_meas']], on='K')
    over_sqrt = merged[merged['budget_reduction'] > np.sqrt(merged['K_eff_meas'])]
    over_keff = merged[merged['budget_reduction'] > merged['K_eff_meas']]
    log.info(f"THE TWO CANDIDATE CEILINGS OF PANEL B, MEASURED. sqrt(K_eff) at K = {K_max} is "
             f"{np.sqrt(keff_at_max):.4f} and K_eff is {keff_at_max:.4f}. Over the "
             f"{len(merged)} plotted cells at c = {c_target}, the realized budget reduction "
             f"EXCEEDS sqrt(K_eff) at {len(over_sqrt)} of them "
             f"({sorted(int(k) for k in over_sqrt['K'])}) and exceeds K_eff at "
             f"{len(over_keff)}. The caption's literal reading -- 'bounded by the effective "
             f"panel size K_eff' -- therefore HOLDS, while the reference line the delivered "
             f"figure actually draws does NOT bound the curve. That is a clarification of which "
             f"quantity the sentence names, not a contradiction of it: "
             f"docs/camera_ready_candidates/R15_v87_budget_bound_referent.md, no register entry.")
    for r in plateau_rows.itertuples():
        moving_block_bootstrap_mean(
            cells[(C_TARGET_INDEX, int(r.k_index))]['valid'],
            cells[(C_TARGET_INDEX, int(r.k_index))]['valid_starts'],
            n_distinct, ("bootstrap_add", int(r.k_index), C_TARGET_INDEX), log,
            f"ADD K={int(r.K)} c={c_target}")

    # =====================================================================
    # CONTROL C8 -- THE DESIGN EFFECT BEFORE ANY POOLED INTERVAL
    # =====================================================================
    rho_pool = diagnostics[diagnostics['K'] >= RHO_POOL_K_MIN]
    overlaps = []
    pooled_K = list(rho_pool['K'])
    for i, Ki in enumerate(pooled_K):
        for Kj in pooled_K[i + 1:]:
            a, b = set(compositions[Ki].tolist()), set(compositions[Kj].tolist())
            overlaps.append(len(a & b) / len(a | b))
    deff_rho, clamp_rho, lags_rho = design_effect(
        rho_pool['rho_sign_meas'].to_numpy(dtype=float), len(rho_pool) - 1,
        f"rho over K >= {RHO_POOL_K_MIN}", log)
    log.info(f"C8 -- the design effect is a PREREQUISITE of every pooled reading here, and it is "
             f"computed before one is taken. \\RFifteenRhoSign pools {len(rho_pool)} cells and "
             f"the plateau pools {m}. The mechanism makes EVERY PAIR of those cells dependent: "
             f"all {len(K_GRID)} compositions are subsets of ONE {K_max}-asset panel over ONE "
             f"common index, with a mean pairwise Jaccard overlap of "
             f"{float(np.mean(overlaps)):.4f} (range [{float(np.min(overlaps)):.4f}, "
             f"{float(np.max(overlaps)):.4f}]) among the pooled cells, so the lag count is the "
             f"full {len(rho_pool) - 1} and not a mechanism-derived subset. Kish deff over the "
             f"K-ordered rho series: {deff_rho:.6f} (clamped: {clamp_rho}), i.e. "
             f"{len(rho_pool) / deff_rho:.2f} independent readings in {len(rho_pool)} cells. "
             f"CONSEQUENCE, APPLIED: \\RFifteenRhoSign IS PUBLISHED AS A POINT STATISTIC WITH "
             f"ITS DISPERSION AND NO INTERVAL -- min {float(rho_pool['rho_sign_meas'].min()):.6f}, "
             f"max {float(rho_pool['rho_sign_meas'].max()):.6f}, sd "
             f"{float(rho_pool['rho_sign_meas'].std(ddof=1)):.6f} -- because an interval over "
             f"cells this dependent would advertise precision the design does not hold.")
    rho_sign = float(rho_pool['rho_sign_meas'].mean())

    # =====================================================================
    # FPR EXTREMA, WITH THE ENVELOPES THEY DO NOT GATE ON
    # =====================================================================
    fpr_min_row = calibration.loc[calibration['FPR_boot'].idxmin()]
    fpr_max_row = calibration.loc[calibration['FPR_boot'].idxmax()]
    log.info(f"FPR_boot extrema are EXTREMA OVER A GRID (S4bis, fourth corollary): they are "
             f"descriptive, they ship with an envelope, and they support no gate. Minimum "
             f"{float(fpr_min_row['FPR_boot']):.4f} at K = {int(fpr_min_row['K'])} "
             f"(SE_design {float(fpr_min_row['SE_FPR_boot_design']):.6f}), maximum "
             f"{float(fpr_max_row['FPR_boot']):.4f} at K = {int(fpr_max_row['K'])} "
             f"(SE_design {float(fpr_max_row['SE_FPR_boot_design']):.6f}). Reading the wider of "
             f"the two as a 95% statement over {len(calibration)} cells would trigger with "
             f"probability 1 - 0.95^{len(calibration)} = "
             f"{1 - 0.95 ** len(calibration):.1%} under its own null.")

    log.info(f"THE CAPTION'S `K_eff ~ 3.8` IS 1/rho_hat AND NOT K_eff. L376 reads 'sign "
             f"correlation rho_hat ~ 0.26 saturates the effective panel near 1/rho_hat ~ 3.8'. "
             f"1/rho_hat on this campaign is {1.0 / rho_sign:.4f}, which rounds to "
             f"{1.0 / rho_sign:.1f}; the MEASURED effective panel size at K = {K_max} is "
             f"K_eff_meas = {keff_at_max:.4f}, which rounds to "
             f"{keff_at_max:.1f}. The two are different quantities -- 1/rho is the "
             f"K -> infinity limit of K/(1+(K-1)rho) and K_eff is its value at a finite K -- and "
             f"the gap is the finite-panel term, not a discrepancy. It is recorded in "
             f"docs/camera_ready_candidates/R15_v87_budget_bound_referent.md, which already owns "
             f"the question of which ceiling the caption names; no register entry, because "
             f"nothing printed is contradicted.")
    scatter = scatter_correlations(race, calibration, K_GRID, log)
    plotted_scatter = scatter[scatter['is_plotted_c'] == 1].iloc[0]
    r_signed = float(plotted_scatter['r_budget_vs_lambda_boot'])
    w_r_planning = witness_scatter_r(witnesses, c_target)
    log.info(f"THE CAPTION'S INEQUALITY, EVALUATED AS PRINTED. v87 writes 'r >= "
             f"{V87_SCATTER_R} with bootstrap threshold' -- a RELATION, not a value. At the "
             f"plotted c = {c_target} the measured coefficient is {r_signed!r}. The printed "
             f"relation r >= {V87_SCATTER_R} is FALSE ({r_signed:.4f} >= {V87_SCATTER_R} is "
             f"{r_signed >= V87_SCATTER_R}), and the mirrored relation r <= -{V87_SCATTER_R} is "
             f"{r_signed <= -V87_SCATTER_R}: THE SIGN IS NEGATIVE, and it is negative for a "
             f"reason -- budget_reduction is ADD_single / ADD_K, so a HIGHER bootstrap threshold "
             f"lengthens ADD_K and SHRINKS the ratio. On the ABSOLUTE value the relation "
             f"|r| >= {V87_SCATTER_R} holds here ({abs(r_signed):.4f}) and FAILS on the "
             f"submitted campaign ({abs(w_r_planning):.4f}), so `|r| >= {V87_SCATTER_R}` is NOT "
             f"a form both campaigns support and `|r| ~ {V87_SCATTER_R}` is. D2: the printed "
             f"relation is falsified under both sign conventions on the submitted campaign and "
             f"under the printed one here, while the qualitative claim it carries -- the "
             f"point-to-point scatter of panel B is almost entirely explained by variation in "
             f"the bootstrap threshold -- holds on both. Registered `R15-scatter-sign`, with a "
             f"camera-ready candidate proposing |r| ~ {V87_SCATTER_R}.")
    log.info(f"THE CAPTION'S ATTRIBUTION IS NOT TESTABLE BY THIS DESIGN. 'Point-to-point scatter "
             f"reflects threshold variations across panel compositions' names COMPOSITIONS as "
             f"the source. This design draws EXACTLY ONE composition per K, so moving along the "
             f"abscissa changes K and the composition together and the two are confounded. No "
             f"composition-resampling arm is added: v87 describes none and the scope filter "
             f"excludes it. The caption is not false -- compositions do vary -- so no register "
             f"entry is opened; it earns "
             f"docs/camera_ready_candidates/R15_v87_scatter_attribution.md, headed NO DEVIATION.")

    # =====================================================================
    # PERSISTENCE
    # =====================================================================
    diagnostics_out = diagnostics.merge(calibration, on=('K', 'k_index'))
    artefacts = {
        f"R15_panel_diagnostics{sfx}.csv": diagnostics_out,
        f"R15_cross_sectional_race{sfx}.csv": race,
        f"R15_covid_natural{sfx}.csv": covid,
        f"R15_panel_composition{sfx}.csv": composition_frame,
        f"R15_race_windows{sfx}.csv": race_windows,
        f"R15_scatter_correlation{sfx}.csv": scatter,
    }
    for name, frame in artefacts.items():
        save_fair_csv(frame, DATA_DIR / name)
        log.info(f"{name}: {len(frame)} rows, {len(frame.columns)} columns.")

    render_figure(diagnostics_out, race, FIGURES_DIR / f"fig17_cross_section{sfx}.png", log)

    # =====================================================================
    # LATEX MACROS
    # =====================================================================
    keff_row = diagnostics_out[diagnostics_out['K'] == K_max].iloc[0]
    fpr_at_40 = float(calibration[calibration['K'] == 40]['FPR_naive'].iloc[0])
    fpr_at_1 = float(calibration[calibration['K'] == 1]['FPR_naive'].iloc[0])
    covid_detections = int((covid['delay_boot'] != -1).sum())
    macros = [
        MACRO_HEADER,
        "% THE CSV CELL BEHIND EACH MACRO.",
        f"%   \\RFifteenPanelSize, \\RFifteenPanelDays        data/derived_equities/"
        f"R15_panel_logreturns.csv shape",
        f"%   \\RFifteenRhoSign, \\RFifteenKeff*              R15_panel_diagnostics{sfx}.csv",
        f"%   \\RFifteenFpr*                                 same file, FPR_boot / FPR_naive",
        f"%   \\RFifteenWhitenessFailsBeyondK                same file, ljungbox_p_Pt",
        f"%   \\RFifteenBudgetReductionPlateau               R15_cross_sectional_race{sfx}.csv,"
        f" c = {c_target}, K >= {PLATEAU_K_MIN}",
        f"%   \\RFifteenScatterCorrelation*                  R15_scatter_correlation{sfx}.csv,"
        f" c = {c_target}",
        f"%   \\RFifteenCovidDetections                      R15_covid_natural{sfx}.csv,"
        f" delay_boot != -1",
        "% \\RFifteenRhoSign is a MEAN OVER THE K >= 5 CELLS and carries NO interval: control C8",
        f"%   measures a Kish deff of {deff_rho:.4f} over cells whose mean pairwise asset overlap",
        f"%   is {float(np.mean(overlaps)):.4f}, so a pooled interval would advertise precision",
        "%   the design does not hold. Its dispersion is in the log and in the section.",
        "% \\RFifteenFprBootMin and \\RFifteenFprBootMax are EXTREMA OVER A GRID (S4bis, fourth",
        f"%   corollary): descriptive, they gate nothing. Moving-block bootstrap envelopes, in",
        f"%   percent: minimum [{100.0 * float(fpr_min_row['FPR_boot_boot_low']):.2f}, "
        f"{100.0 * float(fpr_min_row['FPR_boot_boot_high']):.2f}], maximum "
        f"[{100.0 * float(fpr_max_row['FPR_boot_boot_low']):.2f}, "
        f"{100.0 * float(fpr_max_row['FPR_boot_boot_high']):.2f}]; design-corrected SE "
        f"{float(fpr_min_row['SE_FPR_boot_design']):.5f} and "
        f"{float(fpr_max_row['SE_FPR_boot_design']):.5f}.",
        f"% \\RFifteenBudgetReductionPlateau carries a delta-method standard error of "
        f"{se_plateau:.4f}",
        f"%   propagated from the design-corrected SEMs of its {m} cells and their shared",
        "%   reference arm; it is the mean of the c = "
        f"{c_target} series the delivered plotting code draws.",
        "% \\RFifteenScatterCorrelation is SIGNED and \\RFifteenScatterCorrelationAbs is not.",
        f"%   v87's caption prints the RELATION `r >= {V87_SCATTER_R}`, which the measured sign",
        "%   falsifies; see docs/DEVIATIONS.md :: R15-scatter-sign. Both are printed at FOUR",
        f"%   decimals on purpose: |r| = {abs(r_signed):.4f} rounds to {abs(r_signed):.2f} at two,",
        f"%   which would hide that it sits just above the caption's {V87_SCATTER_R} bound while",
        f"%   the submitted campaign's {abs(w_r_planning):.4f} sits just below it.",
        "% NO MACRO IS EMITTED for the Sharpe ceiling or ADD_min (R16 owns them), and none for",
        "%   delay_naive: the naive threshold's COVID firings are false alarms of a threshold",
        "%   running at up to 100% false-alarm rate under the null, not detections.",
        f"\\newcommand{{\\RFifteenPanelSize}}{{{K_max}}}",
        f"\\newcommand{{\\RFifteenPanelDays}}{{{T_full}}}",
        f"\\newcommand{{\\RFifteenRhoSign}}{{{rho_sign:.2f}}}",
        f"\\newcommand{{\\RFifteenKeffMeasured}}{{{float(keff_row['K_eff_meas']):.1f}}}",
        f"\\newcommand{{\\RFifteenKeffAnalytic}}{{{float(keff_row['K_eff_ana']):.1f}}}",
        f"\\newcommand{{\\RFifteenKeffAgreementMax}}{{{gap_max:.1e}}}",
        f"\\newcommand{{\\RFifteenFprBootMin}}{{{100.0 * float(fpr_min_row['FPR_boot']):.1f}\\%}}",
        f"\\newcommand{{\\RFifteenFprBootMax}}{{{100.0 * float(fpr_max_row['FPR_boot']):.1f}\\%}}",
        f"\\newcommand{{\\RFifteenFprNaiveAtKOne}}{{{100.0 * fpr_at_1:.1f}\\%}}",
        f"\\newcommand{{\\RFifteenFprNaiveAtKForty}}{{{100.0 * fpr_at_40:.1f}\\%}}",
        f"\\newcommand{{\\RFifteenWhitenessFailsBeyondK}}{{{switch_k}}}",
        f"\\newcommand{{\\RFifteenBudgetReductionPlateau}}{{{plateau:.2f}}}",
        f"\\newcommand{{\\RFifteenScatterCorrelation}}{{{r_signed:.4f}}}",
        f"\\newcommand{{\\RFifteenScatterCorrelationAbs}}{{{abs(r_signed):.4f}}}",
        f"\\newcommand{{\\RFifteenCovidDetections}}{{{covid_detections}}}",
    ]
    if args.witness_blas:
        macros.insert(1, "% WITNESS-BLAS ATTRIBUTION ARM. These macros CERTIFY NO v87 VALUE. "
                         "They are produced with")
        macros.insert(2, "%   MKL_CBWR removed, which restores the submitted campaign's BLAS "
                         "summation order, and")
        macros.insert(3, "%   exist only to attribute a residual. Never \\input this file.")
    tex_path = TABLES_DIR / f"R15_claims{sfx}.tex"
    tex_path.write_text("\n".join(macros) + "\n")
    emitted = [line for line in macros if line.startswith("\\newcommand")]
    bad = [line for line in emitted if 'nan' in line.lower()]
    if bad:
        log.error(f"{len(bad)} macros carry the body `nan`: {bad}")
        sys.exit(1)
    log.info(f"Emitted {len(emitted)} macros to {tex_path.name}, cardinal prefix \\RFifteen per "
             f"preamble S6. Every value is computed from an object in memory.")

    # =====================================================================
    # ARTIFACT MANIFEST
    # =====================================================================
    artefact_paths = [DATA_DIR / name for name in artefacts]
    artefact_paths.append(FIGURES_DIR / f"fig17_cross_section{sfx}.png")
    artefact_paths.append(tex_path)
    log_artifact_manifest(log, artefact_paths, RESULTS_DIR, BASE_DIR)

    # =====================================================================
    # PREAMBLE S3 -- THE CLASSIFICATION, COMPUTED
    # =====================================================================
    w_diag = witnesses['diagnostics']
    w_race = witnesses['race']
    w_covid = witnesses['covid']
    w_rho = float(w_diag[w_diag['K'] >= RHO_POOL_K_MIN]['rho_sign_meas'].mean())
    w_keff = float(w_diag[w_diag['K'] == K_max]['K_eff_meas'].iloc[0])
    w_plotted = w_race[w_race['c'] == c_target].sort_values('K')
    w_plateau = float(w_plotted[w_plotted['K'] >= PLATEAU_K_MIN]['budget_reduction'].mean())
    w_r = w_r_planning
    classify("rho_sign, mean over K >= 5", rho_sign, w_rho, V87_RHO_SIGN, 2, log)
    classify(f"K_eff_meas at K = {K_max}", float(keff_row['K_eff_meas']), w_keff, V87_KEFF, 1, log)
    classify("FPR_boot minimum, percent", 100.0 * float(fpr_min_row['FPR_boot']),
             100.0 * float(w_diag['FPR_boot'].min()), V87_FPR_BOOT_MIN_PCT, 1, log)
    classify("FPR_boot maximum, percent", 100.0 * float(fpr_max_row['FPR_boot']),
             100.0 * float(w_diag['FPR_boot'].max()), V87_FPR_BOOT_MAX_PCT, 1, log)
    classify("whiteness switch point", switch_k,
             int(w_diag[w_diag['ljungbox_p_Pt'] >= 0.05]['K'].max()),
             V87_WHITENESS_FAILS_BEYOND_K, 0, log)
    classify(f"budget reduction plateau, c = {c_target}, K >= {PLATEAU_K_MIN}",
             plateau, w_plateau, V87_BUDGET_PLATEAU, 0, log)
    classify(f"scatter correlation |r| at c = {c_target}", abs(r_signed), abs(w_r),
             V87_SCATTER_R, 2, log)
    classify("COVID detections under the bootstrap threshold", covid_detections,
             int((w_covid['delay_boot'] != -1).sum()), V87_COVID_DETECTIONS, 0, log)
    log.info(f"S3 [FPR_naive at K = 40]: v87 states an independence null 'reaches ~100% false "
             f"alarms by K = 40'. Witness "
             f"{float(w_diag[w_diag['K'] == 40]['FPR_naive'].iloc[0]):.4f}, regenerated "
             f"{fpr_at_40:.4f}. The claim is qualitative and it is read as such.")
    log.info(f"S3 [scatter correlation, SIGNED]: witness {w_r!r}, regenerated {r_signed!r}. v87 "
             f"prints the RELATION `r >= {V87_SCATTER_R}`, not a value, and the relation is "
             f"false at both signs on both campaigns. D2, `R15-scatter-sign`.")

    # =====================================================================
    # DIGESTS
    # =====================================================================
    for name in list(artefacts) + [f"fig17_cross_section{sfx}.png", f"R15_claims{sfx}.tex"]:
        directory = (DATA_DIR if name.endswith(".csv")
                     else FIGURES_DIR if name.endswith(".png") else TABLES_DIR)
        log.info(f"SHA-256 {name:<44} : {compute_sha256(directory / name)}")
    log.info(f"Execution completed in {time.time() - t0:.1f}s with {n_jobs} workers "
             f"({'witness-BLAS attribution arm' if args.witness_blas else 'default arm'}).")


if __name__ == "__main__":
    main()
