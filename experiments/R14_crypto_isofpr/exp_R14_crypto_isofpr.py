#!/usr/bin/env python3
"""
==========================================================================
R14 -- EFFICIENCY REVERSAL ON REAL BITCOIN (v87 Figure 16, L345)
==========================================================================
v87 races the recentred sign-CUSUM (`Concept`) against a CUSUM on the honestly
standardized residual eps_t / sigma_hat_t (`Eco-L1`, GARCH(1,1) refitted on each
pre-onset window and filtered forward through the OBSERVED stream) on daily
Bitcoin returns, both arms at one realized false-alarm rate measured on real
placebo windows. This single-stage script regenerates Figure 16
(`fig:crypto_race`) and every numeral of L345.

WHAT v87 PUBLISHES FROM THIS STREAM, AND WHERE EACH NUMBER LIVES.

  L635 caption + L345, iso-FPR `4.7%`   -> R14_crypto_diagnostics, BTC,
                                           FPR_C_real = FPR_E_real = 5/106
  L635 + L345, `106` monthly onsets     -> R14_crypto_isofpr_race, Real_BTC
  L635 + L345, `\\hat\\nu = 2.78`         -> R14_crypto_diagnostics, BTC, nu_hat
  L635, parity at `c = 1.5`             -> race, Real_BTC, c = 1.5, ADD ratio
  L345, ratio `0.74` at `c = 0.35`      -> race, Real_BTC, c = 0.35, ADD ratio
  L345, real mean `0.87`                -> mean ratio over the pairwise-reliable c
  L345, synth `0.98`-`1.14`, mean `1.06`-> Synth_BTC, same pairwise-reliable c
  L345, ETH Ljung-Box `p = 0.019`       -> R14_crypto_diagnostics, ETH, lb_pvalue
  L345, ETH `72` onsets                 -> race, Real_ETH
  L345, ETH synthetic control does not
        recover the light-tailed order  -> Synth_ETH mean ratio
  L635, hollow markers, `DetRate < 0.9` -> race, add_reliable

ETH IS A PUBLISHED CLAIM OF THIS STREAM. The Figure 16 caption says nothing
about Ethereum, but L345 does: it publishes ETH's Ljung-Box p-value, its 72
onsets, that the recentred sign stream fails whiteness, that the fair-coin pivot
does not hold exactly there, and that the synthetic control does not recover the
light-tailed ordering. Those are reproduced and classified here, not treated as
incidental. Preamble S3's asymmetry rule cuts the other way on them: v87 states
its own limitation, so reproducing the failure confirms a self-critical claim.

SIX STRUCTURAL CHANGES AGAINST THE DELIVERED SCRIPT, EACH FORCED BY THE
PREAMBLE.

1. NO SILENT FALLBACK AT THE QMLE (S4.3). `fit_garch_qmle` is carried
   byte-identically, including the `except Exception` branch that returns the
   (0.05, 0.90) initialiser with `converged = False`. It cannot be edited
   without breaking control C6, so EVERY call site asserts `conv is True` and
   `(alpha, beta) != (0.05, 0.90)` and stops otherwise.
2. EXPLICIT DATA SOURCE. The delivered `get_data_path` searches cwd, then the
   script directory, then `Data/yf`. It is replaced by a direct read of
   `data/derived_crypto/{btc,eth}_usd_daily.csv` with `sys.exit(1)` if absent,
   and the SHA-256 of both inputs is asserted against the digests the submitted
   run recorded.
3. THE AGGREGATION RULE IS DERIVED, NOT HARD-CODED. `verify_invariants` selects
   `c >= 0.35` by literal. The rule that reproduces v87's "reliable range" is
   `both arms carry DetRate >= 0.9`, recomputed per source. Control C1.
4. THE DIRECTION GATE STOPS HALTING. `Control (d)` reads the synthetic ratio at
   `min(reliable c)` and exits when it is at or below 1.05. A minimum over a
   grid has no sampling distribution, which S4bis's fourth corollary bans
   outright, and the R14 prompt's C5 says characterise, do not correct. It
   becomes a measurement: the ratio at every pairwise-reliable c, its mean, and
   a paired moving-block bootstrap envelope. Nothing halts on it.
5. NO BARE `np.sqrt(n)` (S4bis, sixth corollary). Monthly onsets with
   `H_DET = 500` trading days give windows that overlap for
   `ceil(500 / 21) = 24` monthly steps, so the independence the delivered
   `np.std(det) / np.sqrt(len(det))` assumes is false by construction. The
   delivered `SEM`, `CI_low` and `CI_high` are kept unchanged for witness
   comparability and the design-effect columns are added beside them.
6. THE `'__none__'` PLOTTING SENTINEL IS REMOVED. `plot_results` passes a
   source name that does not exist in order to obtain an empty frame. The
   panels are built from an explicit two-entry specification.

ENTROPY MIGRATION (preamble S6). The delivered script draws from exactly three
`RandomState` instances and never consumes its module-level `np.random.seed(42)`
/ `random.seed(42)`; control C10 re-establishes that by an `ast` walk rather
than by grep, and the two global seeds are then dropped. The placebo dither, the
synthetic generator and the QMLE recovery streams are re-keyed on a 128-bit
`SeedSequence` whose key carries the role and the index alone. `--legacy-seeds`
restores the delivered `RandomState(100 / 200 / 201 / 300)` draws and nothing
else, stamps every output with `_legacy_seeds`, and certifies no v87 value.

References:
- Page, E. S. (1954). Continuous inspection schemes. Biometrika, 41, 100-115.
- Bollerslev, T. (1986). Generalized autoregressive conditional
  heteroskedasticity. Journal of Econometrics, 31(3), 307-327.
- Bollerslev, T. & Wooldridge, J. M. (1992). Quasi-maximum likelihood estimation
  and inference in dynamic models with time-varying covariances. Econometric
  Reviews, 11(2), 143-172.
- Wilson, E. B. (1927). Probable inference, the law of succession, and
  statistical inference. JASA, 22(158), 209-212.
- Ljung, G. M. & Box, G. E. P. (1978). On a measure of lack of fit in time
  series models. Biometrika, 65(2), 297-303.
- Kish, L. (1965). Survey Sampling. Wiley. (design effect)
- Kunsch, H. R. (1989). The jackknife and the bootstrap for general stationary
  observations. Annals of Statistics, 17(3), 1217-1241. (moving-block bootstrap)

NOTATION (R14 prompt section 6)
  nu_hat        estimated degrees of freedom of the standardized innovations
  c             drift magnitude in units of the unconditional standard deviation
  n_onsets      number of monthly onset windows
  add_reliable  per-cell flag, DetRate >= 0.9
  Eco-L1        honestly standardized parametric residual arm (`Eco` in the CSV)
  FPR_achieved  realized false-alarm rate on real placebo windows
  ADD           average detection delay, CONDITIONAL ON DETECTION
  deff          Kish design effect of a mean over overlapping onset windows
  n_eff         n_detected / deff, the independent readings a cell contains
==========================================================================
"""

import sys
from pathlib import Path

# Determinism bootstrap, in the order preamble S6 requires: fair_env imports only
# os and sys, so the environment block is posted before NumPy is loaded by anyone
# and before any BLAS thread limit is read. PYTHONHASHSEED cannot be set from
# here -- CPython reads it at interpreter start-up -- so it is exported by
# run_experiment_R14.sh and verified twice below.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from experiments.common.fair_env import enforce_strict_determinism, verify_hash_seed, log_environment

enforce_strict_determinism()

import os

if os.environ.get("PYTHONHASHSEED") != "42":
    sys.exit("FATAL: PYTHONHASHSEED is not 42. Execute via run_experiment_R14.sh")

import numpy as np
import pandas as pd
from experiments.common.fair_harness import (setup_logging, disable_pandas_multithreading,
                                             compute_sha256, save_fair_csv, log_artifact_manifest)

disable_pandas_multithreading()

import ast
import time
import hashlib
import argparse
import warnings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.optimize import minimize
import statsmodels.api as sm

# The delivered script silences the optimiser's RuntimeWarnings. It is kept, and
# it is declared: it hides no branch of this script, because every fallback path
# of `fit_garch_qmle` is asserted against at its call sites rather than warned
# about.
warnings.filterwarnings('ignore', category=RuntimeWarning)

# The carried `fit_garch_qmle` logs its own exception branch through a
# module-level `logger`, which main() binds. The name is resolved at call time,
# so the byte-identical copy needs nothing else.
logger = None

# --- PROTOCOL SPECIFICATION, IMPERATIVE, FROM v87 AND THE DELIVERED SCRIPT ---
# R14 prompt section 1, cross-checked against `protocol_24b`: eleven drift
# magnitudes, four sources, two arms.
C_GRID = (0.10, 0.15, 0.20, 0.25, 0.35, 0.5, 0.60, 0.75, 1.0, 1.25, 1.5)
H_REF = 500
H_DET = 500
TARGET_FPR = 0.05
# The CUSUM dead band and the bisection tolerance of the delivered calibration.
DELTA_P = 0.1
BISECT_TOL = 0.005
# The two grid points v87 L345 NAMES. They are read by value, never by index: if
# a redraw moved the minimum of the ratio off `c = 0.35`, the macro must still
# report the point the sentence names, and the displacement is a finding.
NAMED_C_LOW = 0.35
NAMED_C_PARITY = 1.5
# A cell is reliable when its detection rate reaches this floor; v87's Figure 16
# caption renders the others as hollow markers.
DET_RATE_FLOOR = 0.90
# The delivered synthetic control: a quasi-Gaussian Student-t(30) GARCH(1,1)
# matched on the empirical variance of its real counterpart.
SYNTH_NU = 30
# QMLE recovery test (protocol 24c).
QMLE_N_SIMS = 20
QMLE_LENGTH = 2000
QMLE_VAR_EMP = 1e-4
QMLE_ALPHA_TRUE = 0.05
QMLE_BETA_TRUE = 0.90
QMLE_MAX_MEDIAN_BIAS = 0.05
QMLE_MAX_FALLBACK_FRAC = 0.10
# The initialiser `fit_garch_qmle` returns on a failed or degenerate fit. Every
# call site checks against it: preamble S4.3 forbids shipping it as a fit.
QMLE_INITIALISER = (0.05, 0.90)
# The delivered diagnostic gates (`Priorite_24d...py` l.267, l.271), unchanged.
G1_NU_CEILING = 4.7
G1_VAR_Z_LOW = 0.7
G1_VAR_Z_HIGH = 1.4
# The delivered iso-FPR admissibility band (l.433), unchanged.
ISO_FPR_MAX_DIFF = 0.015
ISO_FPR_BAND = (0.03, 0.07)
# The delivered Concept-deviation ceiling (l.416), unchanged.
MAX_DEV_CEILING = 1.0

# --- DEPENDENCE, FIXED BY THE MECHANISM AND NOT BY THE DATA (S4bis) ---
# Two onsets are the first trading days of two months, so consecutive onsets sit
# about 21 trading days apart. A detection window is H_DET = 500 trading days,
# so two onsets share observations for ceil(500 / 21) = 24 monthly steps and are
# disjoint beyond that. K is that number, taken from the mechanism; S4 rule 8
# forbids reading it off the observed autocorrelation.
TRADING_DAYS_PER_MONTH = 21
K_LAGS = int(np.ceil(H_DET / TRADING_DAYS_PER_MONTH))
# The paired moving-block bootstrap of the ratio aggregates. The block is the
# same 24 onsets, for the same reason.
BOOTSTRAP_BLOCK = K_LAGS
BOOTSTRAP_REPLICATES = 2000
BOOTSTRAP_ALPHA = 0.05

# --- WHAT v87 PRINTS, AT THE PRECISION IT PRINTS IT (preamble S3) ---
V87_ISO_FPR_PERCENT = 4.7
V87_ONSETS_BTC = 106
V87_ONSETS_ETH = 72
V87_NU_HAT_BTC = 2.78
V87_RATIO_REAL_AT_C_LOW = 0.74
V87_RATIO_REAL_AT_PARITY = 1.01
V87_RATIO_REAL_MEAN = 0.87
V87_RATIO_SYNTH_MIN = 0.98
V87_RATIO_SYNTH_MAX = 1.14
V87_RATIO_SYNTH_MEAN = 1.06
V87_LJUNG_BOX_ETH = 0.019
# The sources whose SPEED comparison v87 publishes, read clause by clause off
# L345 and the L635 caption and fixed before the first run:
#   Real_BTC   "the sign filter leads across the reliable range ... mean 0.87"
#   Synth_BTC  "a quasi-Gaussian synthetic control ... inverts the ordering"
#   Synth_ETH  "the synthetic control does not recover the light-tailed ordering
#               at its 72 onsets"
# v87 makes NO delay and no ordering claim about REAL Ethereum. What it
# publishes there is the Ljung-Box p, the onset count, the failure of the
# recentred sign stream to pass whiteness, and the statement that "the fair-coin
# pivot does not hold exactly" -- none of which is a speed comparison. Control
# C2 therefore stops the run when the iso-FPR match fails on one of these three
# and records the failure on any other, which is the handling the plan of this
# stream fixed in advance and not a rule chosen after seeing an outcome.
PUBLISHED_SPEED_SOURCES = ("Real_BTC", "Synth_BTC", "Synth_ETH")

# --- INPUTS AND THEIR DIGESTS ---
DERIVED_CRYPTO_DIR = BASE_DIR / "data" / "derived_crypto"
WITNESS_DIR = BASE_DIR / "data" / "reference" / "R14"
WITNESS_SOURCE = WITNESS_DIR / "Priorite_24d_crypto_isofpr_race.py"
R13_SOURCE = (BASE_DIR / "experiments" / "R13_oracle_ceiling"
              / "exp_R13_oracle_ceiling_a.py")
# The digests the submitted run recorded in `Priorite_24d_crypto_isofpr_race.log`
# lines 7 and 8. A different input series would silently produce a different
# campaign under the same code, which is the one substitution no control below
# could detect.
INPUT_SERIES = {
    'BTC': ("btc_usd_daily.csv",
            "a9c84c890cac7284f6330e3ab4d4aed70a9a5e01ec04a8fc0c9ba8999e79c3f4"),
    'ETH': ("eth_usd_daily.csv",
            "f44703a75e4510e906ab1cda6e0a50d96e232bc80aba4ef5105ce6ae94c049f1"),
}
WITNESS_CSVS = {
    'diagnostics': "protocol_24a_crypto_diagnostics.csv",
    'race': "protocol_24b_crypto_isofpr_race.csv",
    'qmle': "protocol_24c_qmle_recovery_crypto.csv",
}

# --- SOURCE-SEGMENT IDENTITY (control C6) ---
# Control S4.2 forbids hoisting a scientific primitive into
# experiments/common/, and a machine diff against this repository's other copies
# shows why the ban is not pedantry: `_garch_nll`, `fit_garch_qmle`,
# `strict_cusum` and `wilson_ci` ALL differ between R14's witness and
# R01/R03/R04/R04b/R11/R13 -- R04's `fit_garch_qmle` carries a multistart ladder
# and a persistence projection R14's does not. Borrowing any of them would move
# published values. Every routine below is therefore duplicated from the file
# that owns it and asserted byte-identical to that file at run time.
CARRIED_PRIMITIVES = {
    "_garch_nll": (WITNESS_SOURCE, "_garch_nll"),
    "fit_garch_qmle": (WITNESS_SOURCE, "fit_garch_qmle"),
    "strict_cusum": (WITNESS_SOURCE, "strict_cusum"),
    "bilateral_delay": (WITNESS_SOURCE, "bilateral_delay"),
    "bisect_fpr": (WITNESS_SOURCE, "bisect_fpr"),
    "wilson_ci": (WITNESS_SOURCE, "wilson_ci"),
    "compute_onsets": (WITNESS_SOURCE, "compute_onsets"),
    "get_deterministic_seed": (R13_SOURCE, "get_deterministic_seed"),
    "seed_sequence_for": (R13_SOURCE, "seed_sequence_for"),
    "rng_for": (R13_SOURCE, "rng_for"),
}
# The two routines the port ADAPTS rather than carries, so byte identity is not
# assertable on them and the witness source of each is quoted in full in the log
# instead. This is the treatment exp_R13_oracle_ceiling_a.py gives its three
# adapted routines and exp_R11_multi_detector.py gives `simulate_garch11`.
ADAPTED_ROUTINES = ("generate_synthetic_garch", "parse_crypto_csv")
# The routines the port SUPERSEDES outright, named so that the log records what
# was dropped and why. None is quoted: each is replaced by repository harness or
# by a control this file implements differently.
SUPERSEDED_ROUTINES = {
    "get_data_path": "three-way cwd / BASE_DIR / Data/yf search, replaced by an explicit source",
    "compute_sha256": "replaced by experiments/common/fair_harness.compute_sha256",
    "log_and_export_requirements": "replaced by fair_env.log_environment plus requirements/R14.txt",
    "setup_logging": "replaced by experiments/common/fair_harness.setup_logging",
    "run_diagnostics": "restructured: the QMLE assertion of S4.3 and the C4 moment derivation",
    "run_qmle_recovery_test": "restructured: injected generators and the C3 reporting obligation",
    "evaluate_arm": "restructured: injected dither, per-onset delays, design effect, C8",
    "plot_results": "the '__none__' sentinel source is removed; panels are an explicit spec",
    "verify_invariants": "gates on 12 literals the delivered run itself produced; see C1 and C5",
    "main": "the halting direction gate of Control (d) becomes a measurement",
}
# The only function of THIS file allowed to touch `np.random.RandomState`:
# the legacy-seed diagnostic arm. Control C10 asserts it.
LEGACY_BROKERS = ("dither_vector", "synth_generator", "qmle_innovation_streams")
# `np.random.<name>` uses that construct a generator or set a global state
# instead of drawing a variate. Anything else on `np.random` is a draw from the
# implicitly seeded global stream, which the entropy migration forbids.
NON_DRAWING_NUMPY_RANDOM = frozenset({"RandomState", "SeedSequence", "default_rng", "seed"})
# The delivered integer seeds, restored by --legacy-seeds and by nothing else.
LEGACY_SEED_DITHER = 100
LEGACY_SEED_SYNTH = {'BTC': 200, 'ETH': 201}
LEGACY_SEED_QMLE = 300

MACRO_HEADER = "% Auto-generated by exp_R14_crypto_isofpr.py -- do not edit."
LEGACY_SUFFIX = "_legacy_seeds"
# The five packages this script imports, plus pytest, which tests/test_R14_claims.py
# imports and which is a deliverable of the same stream. Preamble S5 requires the
# file to be transcribed from importlib.metadata at run time and never written
# from memory.
REQUIREMENT_PACKAGES = ("numpy", "pandas", "scipy", "statsmodels", "matplotlib", "pytest")


# --- PRIMITIVES CARRIED FROM THE FILES THAT OWN THEM ---
# Do not reformat. Byte identity is checked on the exact source text at start-up,
# trailing whitespace included.

def _garch_nll(params, eps, var_emp):
    alpha, beta = params; omega = var_emp*(1.0-alpha-beta)
    n=len(eps); s2=np.zeros(n); s2[0]=var_emp
    for t in range(1,n):
        s2[t]=omega+alpha*eps[t-1]**2+beta*s2[t-1]
        if s2[t]<1e-10: s2[t]=1e-10
    return 0.5*np.sum(np.log(s2)+(eps**2)/s2)


def fit_garch_qmle(eps_w):
    var_emp=np.var(eps_w); init=[0.05,0.90]
    bnds=[(1e-6,0.5),(1e-6,0.99)]; cons={'type':'ineq','fun':lambda x:0.999-(x[0]+x[1])}
    try:
        res=minimize(_garch_nll,init,args=(eps_w,var_emp),method='SLSQP',bounds=bnds,constraints=cons)
        a,b=res.x if res.success else init
        conv=res.success and max(abs(a-0.05),abs(b-0.90))>1e-6
        if not conv: a,b=init
        return (var_emp*(1.0-a-b),a,b),conv
    except Exception as e:
        logger.error(f"QMLE Fit Exception: {e}")
        return (var_emp*(1.0-0.95),0.05,0.90),False


def strict_cusum(stream, delta_P, threshold):
    S=0.0
    for t in range(len(stream)):
        S=max(0.0,S+stream[t]-delta_P)
        if S>threshold: return t
    return -1


def bilateral_delay(stream, delta, thr):
    i1=strict_cusum(stream,delta,thr); i2=strict_cusum(-stream,delta,thr)
    cs=[i for i in (i1,i2) if i!=-1]; return min(cs) if cs else -1


def bisect_fpr(placebo_streams, delta, target=0.05, tol=0.005, max_iter=40):
    """Calibrate threshold so FPR over the given placebo streams == target.
    Returns (lambda, achieved_fpr). Ties broken by a fixed micro-dither already
    baked into the streams by the caller (must be identical placebo/race)."""
    lo, hi, lam, N = 0.001, 2000.0, 5.0, len(placebo_streams)
    for _ in range(12):
        f = sum(1 for s in placebo_streams if strict_cusum(s,delta,hi)!=-1)/N
        if f <= target: break
        hi *= 2.0
    for _ in range(max_iter):
        lam=(lo+hi)/2.0
        f=sum(1 for s in placebo_streams if strict_cusum(s,delta,lam)!=-1)/N
        if abs(f-target)<=tol: break
        if f>target: lo=lam
        else: hi=lam
    f=sum(1 for s in placebo_streams if strict_cusum(s,delta,lam)!=-1)/N
    return lam, f


def wilson_ci(k,n,conf=0.95):
    if n==0: return 0.0,0.0
    z=stats.norm.ppf(1-(1-conf)/2); p=k/n; den=1+z**2/n
    c=(p+z**2/(2*n))/den; m=(z*np.sqrt((p*(1-p))/n+z**2/(4*n**2)))/den
    return max(0.0,c-m),min(1.0,c+m)


def compute_onsets(df, H_ref, H_det):
    df['YearMonth'] = df['Date'].dt.to_period('M')
    first_days = df.groupby('YearMonth').head(1).index.values
    onsets = [idx for idx in first_days if idx >= H_ref and idx <= len(df) - H_det]
    return onsets


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


# --- ROUTINES ADAPTED FROM THE DELIVERED SCRIPT, EACH FOR A STATED REASON ---

def generate_synthetic_garch(length, var_emp, nu=30, loc_rng=None):
    """
    ADAPTED. The delivered form reads
    `def generate_synthetic_garch(length, var_emp, nu=30, seed=42)` with
    `rng = np.random.RandomState(seed)` as its first statement. Preamble S6
    requires the migration to a 128-bit SeedSequence keyed on role and index, so
    the generator is constructed by the caller and passed in. Every line from
    `alpha, beta` to `return eps` is the witness's, and the witness segment is
    quoted in full in the log by control C6.
    """
    alpha, beta = 0.05, 0.90
    omega = var_emp * (1.0 - alpha - beta)

    # Standardized student-t to variance 1
    z = loc_rng.standard_t(df=nu, size=length) * np.sqrt((nu - 2.0) / nu)

    eps = np.zeros(length)
    s2 = np.zeros(length)
    s2[0] = var_emp
    eps[0] = np.sqrt(s2[0]) * z[0]

    for t in range(1, length):
        s2[t] = omega + alpha * eps[t-1]**2 + beta * s2[t-1]
        eps[t] = np.sqrt(s2[t]) * z[t]

    return eps


def parse_crypto_csv(filepath):
    """
    ADAPTED on one argument. `float_precision='round_trip'` is added to the
    delivered `pd.read_csv(filepath, sep=',', quotechar='"')`: preamble S3 makes
    round-trip parsing the reading protocol of this repository, because the fast
    float parser of pandas is not correctly rounded and commonly returns a value
    one ULP from the true one. `load_returns` of exp_R13_oracle_ceiling_a.py
    sets the precedent. Every other line is the witness's, and the witness
    segment is quoted in full in the log by control C6.
    """
    df = pd.read_csv(filepath, sep=',', quotechar='"', float_precision='round_trip')
    if df['Log_Return'].dtype == object:
        df['Log_Return'] = df['Log_Return'].astype(str).str.replace('"', '').str.replace(',', '.')
    df['Log_Return'] = pd.to_numeric(df['Log_Return'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'])

    # 1.11: Topologic chaos purge via index (RangeIndex natively preserves exact numerical footprint)
    df = df[~df.index.duplicated(keep='first')].sort_index()

    # 1.12: API alignment on index
    if isinstance(df.index, pd.DatetimeIndex):
        df.index = df.index.tz_localize(None)
        df.index = pd.to_datetime(df.index.date)

    nans = df['Log_Return'].isna().sum()
    if nans > 0:
        logger.warning(f"Control (g) Notice: Dropped {nans} NaNs from {Path(filepath).name}")

    return df.dropna(subset=['Log_Return']).reset_index(drop=True)


# --- ENTROPY BROKERS: THE THREE DRAWS, MIGRATED AND LEGACY ---
# Each broker holds both keyings side by side so that the diagnostic arm is one
# branch and not a second pipeline. Control C10 asserts that
# `np.random.RandomState` appears nowhere else in this file.

def dither_vector(n_onsets, legacy):
    """
    The placebo micro-dither that breaks CUSUM ties on the binary Concept
    stream. The delivered form is one `RandomState(100).uniform(-1e-6, 1e-6, N)`
    per source; the migrated key carries the ONSET INDEX alone, so the dither is
    identical across the four sources and identical between calibration and
    race, which is the delivered script's own stated requirement, and it
    institutes common random numbers across sources.
    """
    if legacy:
        return np.random.RandomState(LEGACY_SEED_DITHER).uniform(-1e-6, 1e-6, size=n_onsets)
    return np.array([rng_for("R14", "placebo_dither", i).uniform(-1e-6, 1e-6)
                     for i in range(n_onsets)])


def synth_generator(ticker, legacy):
    """The generator of the quasi-Gaussian t_30 synthetic control of `ticker`."""
    if legacy:
        return np.random.RandomState(LEGACY_SEED_SYNTH[ticker])
    return rng_for("R14", "synth_garch", ticker)


def qmle_innovation_streams(n_sims, length, legacy):
    """
    The `n_sims` standard-normal innovation streams of the QMLE recovery test.
    The delivered form consumes ONE `RandomState(300)` sequentially across the
    simulations, so the legacy branch must build the whole set from one
    generator; the migrated branch keys each stream on its simulation index.
    """
    if legacy:
        rng = np.random.RandomState(LEGACY_SEED_QMLE)
        return [rng.standard_normal(length) for _ in range(n_sims)]
    return [rng_for("R14", "qmle_recovery", s).standard_normal(length) for s in range(n_sims)]


# --- STATIC CONTROLS: SOURCE IDENTITY (C6) AND ENTROPY MIGRATION (C10) ---

def source_segments(path, names):
    """
    Source text of the named top-level functions, extracted by position rather
    than by import: importing the delivered script would execute its environment
    block, its logger, its output directory creation and its cwd-dependent data
    search.
    """
    text = Path(path).read_text()
    tree = ast.parse(text)
    return {node.name: ast.get_source_segment(text, node)
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in names}


def check_source_identity(log):
    """
    C6. Byte identity of every carried primitive against the file that owns it,
    at run time, plus the witness source of the two adapted routines quoted in
    full. Deterministic; trigger probability 0 unless a copy has drifted.
    """
    own = source_segments(Path(__file__).resolve(), set(CARRIED_PRIMITIVES))
    compared = 0
    for local_name, (path, remote_name) in sorted(CARRIED_PRIMITIVES.items()):
        if not path.exists():
            log.error(f"C6 source-identity failure: {path} is missing, so the copy of "
                      f"{local_name} cannot be verified.")
            sys.exit(1)
        remote = source_segments(path, {remote_name}).get(remote_name)
        mine = own.get(local_name)
        if remote is None or mine is None:
            log.error(f"C6 source-identity failure: {local_name} could not be extracted "
                      f"({path.name}::{remote_name}).")
            sys.exit(1)
        if mine != remote:
            log.error(f"C6 source-identity failure on {local_name}: the copy has drifted from "
                      f"{path.name}::{remote_name}.")
            sys.exit(1)
        compared += len(remote)
    log.info(f"C6 source identity: {len(CARRIED_PRIMITIVES)} primitives byte-identical to the "
             f"files that own them ({compared} characters compared) -- _garch_nll, "
             f"fit_garch_qmle, strict_cusum, bilateral_delay, bisect_fpr, wilson_ci and "
             f"compute_onsets against {WITNESS_SOURCE.name}, and get_deterministic_seed, "
             f"seed_sequence_for and rng_for against {R13_SOURCE.name}. Control S4.2 forbids "
             f"hoisting any of them into experiments/common/: a machine diff shows _garch_nll, "
             f"fit_garch_qmle, strict_cusum and wilson_ci all differ between this witness and "
             f"the R01/R03/R04/R04b/R11/R13 copies, so the duplication is deliberate and "
             f"mutualising it would move published values. Deterministic; trigger probability 0 "
             f"unless a copy has drifted.")

    witness = source_segments(WITNESS_SOURCE, set(ADAPTED_ROUTINES))
    missing = [name for name in ADAPTED_ROUTINES if name not in witness]
    if missing:
        log.error(f"C6: the witness carries no {missing}; the adaptation cannot be exhibited.")
        sys.exit(1)
    log.info(f"C6 ADAPTED ROUTINES. {list(ADAPTED_ROUTINES)} cannot be byte-compared -- "
             f"generate_synthetic_garch takes an injected generator where {WITNESS_SOURCE.name} "
             f"builds a RandomState from a bare integer seed, and parse_crypto_csv gains "
             f"float_precision='round_trip', which preamble S3 makes the reading protocol of "
             f"every numeric CSV in this repository. The witness source of each is quoted in "
             f"full below instead; the two segments total "
             f"{sum(len(witness[n]) for n in ADAPTED_ROUTINES)} characters.")
    for name in ADAPTED_ROUTINES:
        log.info(f"C6 witness SHA-256 of {name}: "
                 f"{hashlib.sha256(witness[name].encode('utf-8')).hexdigest()}")
        log.info(f"C6 witness source of {name}:\n{witness[name].rstrip()}")
    log.info("C6 SUPERSEDED ROUTINES, named rather than quoted: "
             + "; ".join(f"{k} ({v})" for k, v in sorted(SUPERSEDED_ROUTINES.items())) + ".")


def bare_global_draws(tree, exempt):
    """
    Every `np.random.<name>` access whose `<name>` draws a variate, paired with
    the enclosing top-level function. A draw taken directly on `np.random` reads
    the implicitly seeded global stream, which the entropy migration forbids.
    """
    hits = []
    for node in tree.body:
        scope = node.name if isinstance(node, (ast.FunctionDef, ast.ClassDef)) else "<module>"
        for child in ast.walk(node):
            if not isinstance(child, ast.Attribute):
                continue
            base = child.value
            if not (isinstance(base, ast.Attribute) and base.attr == "random"
                    and isinstance(base.value, ast.Name) and base.value.id == "np"):
                continue
            if child.attr in NON_DRAWING_NUMPY_RANDOM:
                if child.attr == "RandomState" and scope not in exempt:
                    hits.append((scope, "np.random.RandomState"))
                continue
            hits.append((scope, f"np.random.{child.attr}"))
    return hits


def check_entropy_migration(log):
    """
    C10. The delivered script sets `np.random.seed(42)` and `random.seed(42)` at
    module level; this port drops both. Dropping them is only admissible if no
    draw consumed them, and that is re-established here by an `ast` walk rather
    than by a grep: no `np.random.<distribution>` call exists in the witness, so
    every variate it draws comes from one of its three explicit `RandomState`
    instances. The same walk over THIS file additionally requires that
    `np.random.RandomState` appear only inside the legacy-seed brokers.

    Static; trigger probability 0.
    """
    witness_tree = ast.parse(WITNESS_SOURCE.read_text())
    # The witness is allowed its three RandomState constructions -- they are the
    # draws this port re-keys -- so every scope of it is exempt from the
    # RandomState clause. What is asserted on it is the other clause: that no
    # DISTRIBUTION is drawn on `np.random` itself.
    witness_scopes = {node.name for node in witness_tree.body
                      if isinstance(node, (ast.FunctionDef, ast.ClassDef))} | {"<module>"}
    witness_hits = bare_global_draws(witness_tree, exempt=witness_scopes)
    if witness_hits:
        log.error(f"C10 failure: {WITNESS_SOURCE.name} draws from the implicitly seeded global "
                  f"NumPy stream at {witness_hits}, so its module-level np.random.seed(42) is "
                  f"consumed and cannot be dropped without changing a published value.")
        sys.exit(1)
    constructors = sorted({node.func.attr
                           for node in ast.walk(witness_tree)
                           if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                           and isinstance(node.func.value, ast.Attribute)
                           and node.func.value.attr == "random"
                           and isinstance(node.func.value.value, ast.Name)
                           and node.func.value.value.id == "np"})
    n_random_state = sum(1 for node in ast.walk(witness_tree)
                         if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                         and node.func.attr == "RandomState")
    log.info(f"C10 entropy migration, on {WITNESS_SOURCE.name}: no np.random.<distribution> call "
             f"exists anywhere in the witness -- the only np.random members it touches are "
             f"{constructors} -- and it constructs {n_random_state} RandomState instances. Its "
             f"module-level np.random.seed(42) and random.seed(42) are therefore set and never "
             f"consumed, which is what licenses dropping them here. Static; trigger probability 0.")

    own_tree = ast.parse(Path(__file__).resolve().read_text())
    own_hits = bare_global_draws(own_tree, exempt=set(LEGACY_BROKERS))
    if own_hits:
        log.error(f"C10 failure: this script reaches the global NumPy stream, or constructs a "
                  f"RandomState outside the legacy-seed brokers, at {own_hits}.")
        sys.exit(1)
    log.info(f"C10 entropy migration, on this script: no draw touches the global NumPy stream, "
             f"and np.random.RandomState appears only inside {list(LEGACY_BROKERS)}. Every "
             f"migrated draw is keyed by rng_for on its role and index alone -- never on a "
             f"process parameter -- which institutes common random numbers: every cross-source "
             f"and cross-magnitude comparison below is PAIRED, and every pooled interval "
             f"therefore carries its design effect (S4bis, third corollary).")


# --- INPUTS ---

def load_series(ticker, log):
    """
    The daily crypto series, read from `data/derived_crypto/` and from nowhere
    else. The delivered `get_data_path` searches the working directory, then the
    script directory, then `Data/yf`, so the campaign's own input depended on
    where it was launched from; preamble S4.3 bans a pipeline that chooses its
    own data source.
    """
    filename, expected = INPUT_SERIES[ticker]
    path = DERIVED_CRYPTO_DIR / filename
    if not path.exists():
        log.error(f"Missing input: {path}. R14 reads the versioned daily crypto series and has "
                  f"no download path.")
        sys.exit(1)
    digest = compute_sha256(path)
    log.info(f"SHA-256 {filename:<22} : {digest}")
    if digest != expected:
        log.error(f"Input digest mismatch on {filename}: {digest} against the {expected} the "
                  f"submitted run recorded. A different input series produces a different "
                  f"campaign under identical code.")
        sys.exit(1)
    frame = parse_crypto_csv(path)
    log.info(f"{ticker}: {len(frame)} daily returns, "
             f"{frame['Date'].iloc[0].date()} to {frame['Date'].iloc[-1].date()}.")
    return frame


def assert_qmle_usable(params, converged, where, log):
    """
    Control S4.3, applied at every call site because the primitive itself is
    carried byte-identically and cannot be edited. `fit_garch_qmle` returns the
    (0.05, 0.90) initialiser both when SLSQP raises and when the solution lands
    within 1e-6 of that initialiser, and it flags the second case through
    `converged` alone. Shipping the initialiser as a fit is the degraded path
    that produces a normal-looking result.
    """
    _, alpha, beta = params
    frozen = (alpha, beta) == QMLE_INITIALISER
    if converged and not frozen:
        return
    log.error(f"QMLE failure at {where}: converged = {converged}, (alpha, beta) = "
              f"({alpha!r}, {beta!r}) against the initialiser {QMLE_INITIALISER}. Control S4.3 "
              f"forbids continuing on a fit no optimiser produced.")
    sys.exit(1)


# --- 24c: QMLE RECOVERY (control C3) ---

def run_qmle_recovery(legacy, log):
    """
    The delivered G2 recovery test, with its innovation streams injected and its
    fallback counters reported even at zero.
    """
    omega_true = QMLE_VAR_EMP * (1.0 - QMLE_ALPHA_TRUE - QMLE_BETA_TRUE)
    log.info(f"C3 -- QMLE recovery: {QMLE_N_SIMS} GARCH(1,1) streams of {QMLE_LENGTH} steps at "
             f"(alpha, beta) = ({QMLE_ALPHA_TRUE}, {QMLE_BETA_TRUE}), unconditional variance "
             f"{QMLE_VAR_EMP:g}, standard-normal innovations. The fallback, frozen and "
             f"non-converged counters are logged and persisted EVEN AT ZERO: a counter reported "
             f"only when it is non-zero establishes nothing about the runs where it is not.")
    streams = qmle_innovation_streams(QMLE_N_SIMS, QMLE_LENGTH, legacy)
    biases, fallbacks, frozen = [], 0, 0
    for sim, z in enumerate(streams):
        eps = np.zeros(QMLE_LENGTH)
        s2 = np.zeros(QMLE_LENGTH)
        s2[0] = QMLE_VAR_EMP
        eps[0] = np.sqrt(s2[0]) * z[0]
        for t in range(1, QMLE_LENGTH):
            s2[t] = omega_true + QMLE_ALPHA_TRUE * eps[t-1]**2 + QMLE_BETA_TRUE * s2[t-1]
            eps[t] = np.sqrt(s2[t]) * z[t]
        params, conv = fit_garch_qmle(eps)
        if not conv:
            fallbacks += 1
        if (params[1], params[2]) == QMLE_INITIALISER:
            frozen += 1
        assert_qmle_usable(params, conv, f"QMLE recovery simulation {sim}", log)
        biases.append(abs(params[1] - QMLE_ALPHA_TRUE) + abs(params[2] - QMLE_BETA_TRUE))

    median_bias = float(np.median(biases))
    fallback_frac = fallbacks / QMLE_N_SIMS
    frozen_frac = frozen / QMLE_N_SIMS
    log.info(f"C3 QMLE recovery: median bias = {median_bias:.4f}, fallback fraction = "
             f"{fallback_frac:.4f}, frozen fraction = {frozen_frac:.4f}, "
             f"{QMLE_N_SIMS - fallbacks}/{QMLE_N_SIMS} converged. Worst bias "
             f"{max(biases):.4f}, best {min(biases):.4f}.")
    log.info(f"C3 GATE, stated before it is read: the delivered admissibility band is "
             f"median bias < {QMLE_MAX_MEDIAN_BIAS} and fallback fraction < "
             f"{QMLE_MAX_FALLBACK_FRAC}. It is a band on the INSTRUMENT, not on a published "
             f"claim, and the null distribution of a median over {QMLE_N_SIMS} simulations has "
             f"no closed form, so no trigger probability is quoted for it. If it fires, the "
             f"failure is characterised and reported; preamble S4.10 forbids reseeding until it "
             f"passes.")
    if median_bias >= QMLE_MAX_MEDIAN_BIAS or fallback_frac >= QMLE_MAX_FALLBACK_FRAC:
        log.error(f"C3 gate FIRED: median bias {median_bias:.6f} against "
                  f"{QMLE_MAX_MEDIAN_BIAS}, fallback fraction {fallback_frac:.6f} against "
                  f"{QMLE_MAX_FALLBACK_FRAC}. No seed, tolerance or parameter is touched.")
        sys.exit(1)
    frame = pd.DataFrame({
        'Metric': ['Median_Bias', 'Fallback_Frac', 'Frozen_Frac', 'N_Sims', 'N_Converged',
                   'Max_Bias', 'Min_Bias'],
        'Value': [median_bias, fallback_frac, frozen_frac, float(QMLE_N_SIMS),
                  float(QMLE_N_SIMS - fallbacks), float(max(biases)), float(min(biases))],
    })
    return frame, median_bias, fallback_frac


# --- 24a: DIAGNOSTICS (controls C3 and C4) ---

def run_diagnostics(series, log):
    """
    The delivered G1 and G3 diagnostics: the Student-t degrees of freedom of the
    standardized innovations, the variance of those innovations, and a lag-10
    Ljung-Box on the recentred SIGN stream.
    """
    records = []
    for name, frame in series.items():
        r = frame['Log_Return'].values
        eps = r - np.mean(r)
        var_emp = np.var(eps)
        params, conv = fit_garch_qmle(eps)
        assert_qmle_usable(params, conv, f"whole-sample diagnostic fit on {name}", log)
        omega, alpha, beta = params

        s2 = np.zeros(len(eps))
        s2[0] = var_emp
        for t in range(1, len(eps)):
            s2[t] = max(1e-10, omega + alpha * eps[t-1]**2 + beta * s2[t-1])
        z_hat = eps / np.sqrt(s2)

        df_nu, _, _ = stats.t.fit(z_hat)
        var_z = float(np.var(z_hat))

        signs = np.sign(r - np.median(r))
        lb_res = sm.stats.acorr_ljungbox(signs, lags=[10], return_df=True)
        p_val = float(lb_res['lb_pvalue'].iloc[0])

        records.append({'source': name, 'nu_hat': float(df_nu), 'Var_z_hat': var_z,
                        'lb_pvalue': p_val, 'omega': float(omega), 'alpha': float(alpha),
                        'beta': float(beta), 'n_days': int(len(r)),
                        'qmle_converged': bool(conv)})
        log.info(f"Diagnostic {name}: nu_hat = {df_nu!r}, Var(z_hat) = {var_z!r}, "
                 f"lag-10 Ljung-Box p = {p_val!r} on the recentred sign stream, "
                 f"(omega, alpha, beta) = ({omega!r}, {alpha!r}, {beta!r}).")

        # C4 -- THE MOMENT CONDITION, DERIVED AT RUN TIME FROM THE FITTED nu_hat
        # AND NOT RECITED. For a Student-t standardized to unit variance,
        # E|z|^p < infinity if and only if p < nu; hence the variance exists iff
        # nu > 2 and the fourth moment iff nu > 4. Everything below follows from
        # that one line evaluated at the value just measured.
        variance_exists = df_nu > 2.0
        fourth_moment_exists = df_nu > 4.0
        log.info(f"C4 [{name}] moment condition, derived at run time: for a standardized "
                 f"Student-t, E|z|^p < inf iff p < nu, so the variance exists iff nu > 2 and the "
                 f"fourth moment iff nu > 4. At nu_hat = {df_nu:.6f} the variance "
                 f"{'exists' if variance_exists else 'DOES NOT exist'} and the fourth moment "
                 f"{'exists' if fourth_moment_exists else 'DOES NOT exist'}.")
        if not fourth_moment_exists:
            log.info(f"C4 [{name}] consequence: with E[z^4] infinite, the GARCH penalty Gamma -- "
                     f"which is a functional of the autocorrelation of eps^2 and therefore needs "
                     f"a finite fourth moment of z -- and the chi-square limit of a Ljung-Box on "
                     f"SQUARED residuals are both unjustified on the `Data` pipeline v87 "
                     f"contrasts against. STATED PRECISELY: the Ljung-Box actually computed here "
                     f"is on the SIGN stream, which is bounded, so its own chi-square "
                     f"approximation is untouched by this. The caveat is about the Data pipeline, "
                     f"not about this diagnostic, and Figure 16 is what that regime illustrates.")

    frame = pd.DataFrame(records)
    nu_values = frame['nu_hat'].to_numpy()
    var_values = frame['Var_z_hat'].to_numpy()
    if (nu_values >= G1_NU_CEILING).all():
        log.error(f"G1 failure: heavy tails not present, nu_hat >= {G1_NU_CEILING} on every "
                  f"asset ({nu_values}). Figure 16's premise does not hold on this input.")
        sys.exit(1)
    outside = frame[(frame['Var_z_hat'] < G1_VAR_Z_LOW) | (frame['Var_z_hat'] > G1_VAR_Z_HIGH)]
    if len(outside) > 0:
        log.warning(f"G1 warning: standardized-residual variance outside "
                    f"[{G1_VAR_Z_LOW}, {G1_VAR_Z_HIGH}] on "
                    f"{list(outside['source'])} ({list(outside['Var_z_hat'])}).")
    log.info(f"G1: nu_hat = {list(nu_values)} against the {G1_NU_CEILING} ceiling, "
             f"Var(z_hat) = {list(var_values)} inside [{G1_VAR_Z_LOW}, {G1_VAR_Z_HIGH}].")
    return frame


# --- THE DESIGN EFFECT (control C9, S4bis sixth corollary) ---

def design_effect(values, label, log):
    """
    The Kish design effect of a mean over overlapping onset windows,
    `deff = 1 + 2 * sum_{k=1..K} (1 - k/n) * rho_k`.

    `K` comes from the MECHANISM and never from the observed autocorrelation
    (preamble S4, rule 8): consecutive onsets are the first trading days of
    consecutive months, about 21 trading days apart, and a detection window is
    H_DET = 500 trading days, so two onsets more than
    ceil(500 / 21) = 24 monthly steps apart share no observation at all.

    `rho_k` is the lag-k autocorrelation of the delays over the DETECTED subset
    taken in onset order. On a reliable cell that subset is almost the whole
    grid, so a lag of k positions is a lag of about k monthly steps; on an
    unreliable cell it is coarser, which is one more reason those cells enter no
    aggregate (control C1).

    Returns `(deff, clamped, k_used)`. A negative-autocorrelation estimate can
    push the sum below 1, where it would ADVERTISE more information than the
    sample holds; it is clamped at 1 and the clamp is logged.
    """
    n = len(values)
    if n < 2:
        return 1.0, False, 0
    k_used = min(K_LAGS, n - 1)
    x = np.asarray(values, dtype=float)
    centred = x - x.mean()
    denom = float(np.dot(centred, centred))
    if denom <= 0.0:
        log.info(f"deff [{label}]: the {n} detected delays are identical, so no autocorrelation "
                 f"is defined and deff is 1.0 by construction.")
        return 1.0, False, k_used
    raw = 1.0
    for k in range(1, k_used + 1):
        raw += 2.0 * (1.0 - k / n) * float(np.dot(centred[:-k], centred[k:]) / denom)
    if raw < 1.0:
        log.info(f"deff [{label}]: the estimate is {raw:.6f} < 1, which would claim more "
                 f"independent readings than the {n} observations contain; clamped to 1.0.")
        return 1.0, True, k_used
    return raw, False, k_used


def aggregate_cell(delays, n_onsets, label, log):
    """
    One (source, arm, c) cell. The delivered `DetRate`, `CI_low`, `CI_high`,
    `ADD` and `SEM` are computed exactly as `_aggregate` computes them, and the
    design-effect columns are added beside them.
    """
    det = [d for d in delays if d != -1]
    n_det = len(det)
    dr = n_det / n_onsets
    ci_l, ci_h = wilson_ci(n_det, n_onsets)
    add = float(np.mean(det)) if det else np.nan

    # S4bis, SIXTH COROLLARY. The design effect is computed and logged HERE, in
    # the same block and before the division by the square root of a sample size
    # on the next line. The delivered SEM assumes independent onsets; the
    # windows overlap for K_LAGS monthly steps by construction.
    deff, clamped, k_used = design_effect(det, label, log)
    sem = np.std(det) / np.sqrt(len(det)) if len(det) > 1 else 0.0
    n_eff = n_det / deff if n_det else 0.0
    sem_design = float(sem) * float(np.sqrt(deff))
    if n_eff > 0.0:
        cid_l, cid_h = wilson_ci(dr * n_eff, n_eff)
    else:
        cid_l, cid_h = 0.0, 0.0
    log.info(f"C9 [{label}]: n_detected = {n_det}/{n_onsets}, deff = {deff:.6f} over "
             f"{k_used} mechanism-fixed lags (clamped = {clamped}), n_eff = {n_eff:.4f}, "
             f"SEM = {float(sem):.6f} -> SEM_design = {sem_design:.6f}, "
             f"DetRate interval [{ci_l:.6f}, {ci_h:.6f}] -> design-corrected "
             f"[{cid_l:.6f}, {cid_h:.6f}].")
    clip = lambda v: max(0.0, min(1.0, float(v)))
    return {
        'DetRate': dr, 'CI_low': clip(ci_l), 'CI_high': clip(ci_h), 'ADD': add,
        'SEM': float(sem), 'add_reliable': bool(dr >= DET_RATE_FLOOR),
        'n_detected': n_det, 'deff': float(deff), 'deff_clamped': bool(clamped),
        'deff_lags': int(k_used), 'n_eff': float(n_eff), 'SEM_design': sem_design,
        'CI_low_design': clip(cid_l), 'CI_high_design': clip(cid_h),
    }


# --- 24b: THE ISO-FPR RACE ---

def check_non_anticipativity(r_series, onset, log, source_name):
    """
    C8, extended. The delivered check perturbs the post-onset segment by +100
    and compares `mu_hat` before and after. It is extended to the FULL pre-onset
    parameter vector -- the median, the reference sign frequency, the three
    GARCH parameters and the two filter seeds -- because a leak through any one
    of them would be invisible to a comparison on the mean alone.

    The identity is tautological by slicing: `r_series[onset - H_REF : onset]`
    cannot see `r_series[onset:]`. It is recorded as such rather than presented
    as evidence, and it is asserted so that a future edit that reorders the
    slicing cannot pass silently.
    """
    def pre_onset_vector(series):
        r_ref = series[onset-H_REF : onset]
        mu_hat = np.mean(r_ref)
        med_hat = np.median(r_ref)
        q_hat_ref = np.mean(r_ref > med_hat)
        eps_ref = r_ref - mu_hat
        var_emp = np.var(eps_ref)
        params, conv = fit_garch_qmle(eps_ref)
        assert_qmle_usable(params, conv, f"C8 non-anticipativity fit on {source_name}", log)
        omega, alpha, beta = params
        s2_ref = np.zeros(H_REF)
        s2_ref[0] = var_emp
        for t in range(1, H_REF):
            s2_ref[t] = max(1e-10, omega + alpha * eps_ref[t-1]**2 + beta * s2_ref[t-1])
        return {'mu_hat': mu_hat, 'med_hat': med_hat, 'q_hat_ref': q_hat_ref, 'omega': omega,
                'alpha': alpha, 'beta': beta, 'eps_last': eps_ref[-1], 's2_last': s2_ref[-1]}

    perturbed = r_series.copy()
    perturbed[onset:] += 100.0
    clean = pre_onset_vector(r_series)
    shifted = pre_onset_vector(perturbed)
    differing = {k: (clean[k], shifted[k]) for k in clean if clean[k] != shifted[k]}
    if differing:
        log.error(f"C8 failure on {source_name}: the pre-onset parameter vector moves when the "
                  f"post-onset segment is shifted by +100 -- {differing}. Information leaks from "
                  f"the future into the detector's calibration.")
        sys.exit(1)
    log.info(f"C8 non-anticipativity [{source_name}], first onset {int(onset)}: the full "
             f"pre-onset vector {sorted(clean)} is bit-identical after r[onset:] += 100. The "
             f"identity is TAUTOLOGICAL BY SLICING -- the reference window is "
             f"r[onset - {H_REF} : onset] and cannot reach past `onset` -- and is recorded as a "
             f"structural assertion, trigger probability 0, not as evidence of anything.")


def evaluate_source(source_name, ticker, r_series, onsets, dither, log):
    """
    One of the four sources: calibrate both arms to a common realized FPR on its
    own placebo windows, then race them over the drift grid.

    Restructured from the delivered `evaluate_arm`: the dither is injected, the
    per-onset delays are retained so that the bootstrap and the design effect
    are checkable without rerunning, the non-anticipativity check covers the
    whole pre-onset vector, and every QMLE fit is asserted usable.
    """
    n_onsets = len(onsets)
    log.info(f"--- {source_name}: {n_onsets} monthly onsets, H_ref = {H_REF}, H_det = {H_DET}, "
             f"one series shared by both arms ---")

    check_non_anticipativity(r_series, onsets[0], log, source_name)

    placebo_C, placebo_E, onset_data = [], [], []
    max_dev = 0.0
    n_frozen = n_non_conv = 0

    for i, onset in enumerate(onsets):
        r_ref = r_series[onset-H_REF : onset]
        r_fut = r_series[onset : onset+H_DET]

        mu_hat = np.mean(r_ref)
        med_hat = np.median(r_ref)
        q_hat_ref = np.mean(r_ref > med_hat)

        eps_ref = r_ref - mu_hat
        var_emp = np.var(eps_ref)
        params, conv = fit_garch_qmle(eps_ref)
        if not conv:
            n_non_conv += 1
        if (params[1], params[2]) == QMLE_INITIALISER:
            n_frozen += 1
        assert_qmle_usable(params, conv, f"{source_name} onset {int(onset)}", log)
        omega, alpha, beta = params

        s2_ref = np.zeros(H_REF)
        s2_ref[0] = var_emp
        for t in range(1, H_REF):
            s2_ref[t] = max(1e-10, omega + alpha * eps_ref[t-1]**2 + beta * s2_ref[t-1])
        eps_last = eps_ref[-1]
        s2_last = s2_ref[-1]

        dev = (r_fut > med_hat).astype(float) - q_hat_ref + dither[i]
        max_dev = max(max_dev, np.max(np.abs(dev - dither[i])))

        eps_fut = r_fut - mu_hat
        s2_fut = np.zeros(H_DET)
        s2_fut[0] = max(1e-10, omega + alpha * eps_last**2 + beta * s2_last)
        for t in range(1, H_DET):
            s2_fut[t] = max(1e-10, omega + alpha * eps_fut[t-1]**2 + beta * s2_fut[t-1])
        z_fut = eps_fut / np.sqrt(s2_fut)

        placebo_C.append(dev)
        placebo_E.append(z_fut)
        onset_data.append({'r_fut': r_fut, 'mu_hat': mu_hat, 'med_hat': med_hat,
                           'q_hat_ref': q_hat_ref, 'sigma_unc': np.sqrt(var_emp),
                           'eps_last': eps_last, 's2_last': s2_last, 'omega': omega,
                           'alpha': alpha, 'beta': beta, 'dither': dither[i]})

    log.info(f"C3 [{source_name}] QMLE audit over {n_onsets} pre-onset fits: non-converged = "
             f"{n_non_conv}/{n_onsets}, frozen to the (0.05, 0.90) initialiser = "
             f"{n_frozen}/{n_onsets}, fallback fraction = {n_non_conv / n_onsets:.4f}. Logged "
             f"even at zero.")
    log.info(f"Concept deviation ceiling [{source_name}]: max |dev| = {max_dev:.6f} against the "
             f"delivered {MAX_DEV_CEILING}.")
    if max_dev > MAX_DEV_CEILING:
        log.error(f"The Concept deviation exceeds {MAX_DEV_CEILING} on {source_name} "
                  f"({max_dev}); the binary stream is not a recentred indicator.")
        sys.exit(1)

    lambda_C, fpr_C = bisect_fpr(placebo_C, DELTA_P, TARGET_FPR, BISECT_TOL)
    lambda_E, fpr_E = bisect_fpr(placebo_E, DELTA_P, TARGET_FPR, BISECT_TOL)
    k_C = int(round(fpr_C * n_onsets))
    k_E = int(round(fpr_E * n_onsets))
    log.info(f"C2 [{source_name}] iso-FPR: Concept lambda* = {lambda_C!r} realizes "
             f"{k_C}/{n_onsets} = {fpr_C!r}; Eco lambda* = {lambda_E!r} realizes "
             f"{k_E}/{n_onsets} = {fpr_E!r}; |difference| = {abs(fpr_C - fpr_E):.6g}.")
    if abs(fpr_C - fpr_E) > ISO_FPR_MAX_DIFF or not all(
            ISO_FPR_BAND[0] <= f <= ISO_FPR_BAND[1] for f in (fpr_C, fpr_E)):
        log.error(f"The delivered iso-FPR admissibility band is violated on {source_name}: "
                  f"FPR_C = {fpr_C}, FPR_E = {fpr_E}, band {ISO_FPR_BAND}, maximum difference "
                  f"{ISO_FPR_MAX_DIFF}. The race is not iso-FPR and no speed comparison on this "
                  f"source is interpretable.")
        sys.exit(1)

    rows, delay_rows = [], []
    delays_by_arm = {'Concept': {}, 'Eco': {}}
    for c in C_GRID:
        race_C, race_E = [], []
        for i in range(n_onsets):
            dat = onset_data[i]
            r_fut_c = dat['r_fut'] + c * dat['sigma_unc']

            dev_c = (r_fut_c > dat['med_hat']).astype(float) - dat['q_hat_ref'] + dat['dither']
            race_C.append(dev_c)

            # Eco (honest, non-anticipative): the GARCH conditional variance is
            # filtered FORWARD from the INJECTED residuals, so the location
            # drift inflates the variance exactly as it does for a deployed
            # detector and volatility masking is NOT neutralized. The parameters
            # and the seeds (eps_last, s2_last) come only from the pre-onset
            # window.
            eps_fut_c = r_fut_c - dat['mu_hat']
            s2_fut_c = np.zeros(H_DET)
            s2_fut_c[0] = max(1e-10, dat['omega'] + dat['alpha'] * dat['eps_last']**2
                              + dat['beta'] * dat['s2_last'])
            for t_e in range(1, H_DET):
                s2_fut_c[t_e] = max(1e-10, dat['omega'] + dat['alpha'] * eps_fut_c[t_e-1]**2
                                    + dat['beta'] * s2_fut_c[t_e-1])
            race_E.append(eps_fut_c / np.sqrt(s2_fut_c))

        for arm, streams, lam, fpr in (('Concept', race_C, lambda_C, fpr_C),
                                       ('Eco', race_E, lambda_E, fpr_E)):
            delays = [bilateral_delay(s, DELTA_P, lam) for s in streams]
            delays_by_arm[arm][c] = np.array(delays, dtype=float)
            cell = aggregate_cell(delays, n_onsets, f"{source_name} / {arm} / c = {c}", log)
            rows.append({'source': source_name, 'ticker': ticker, 'c': c, 'arm': arm,
                         'n_onsets': n_onsets, 'lambda_star': lam, 'FPR_achieved': fpr,
                         'FPR_count': k_C if arm == 'Concept' else k_E,
                         'iso_fpr_matched': bool(fpr_C == fpr_E),
                         'qmle_n_non_converged': n_non_conv, 'qmle_n_frozen': n_frozen,
                         'qmle_fallback_frac': n_non_conv / n_onsets, **cell})
            for i, d in enumerate(delays):
                delay_rows.append({'source': source_name, 'ticker': ticker, 'c': c, 'arm': arm,
                                   'onset_position': i, 'onset_index': int(onsets[i]),
                                   'delay': int(d), 'detected': bool(d != -1)})

    return rows, delay_rows, delays_by_arm, (fpr_C, fpr_E)


# --- C1: THE PAIRWISE-RELIABLE GRID ---

def pairwise_reliable_grid(race, source, log=None):
    """
    C1. The grid points at which BOTH arms of a source carry
    `DetRate >= 0.9`. The delivered `verify_invariants` selects `c >= 0.35` by
    literal; this rule derives the same set from the data on BTC and is the only
    filter any published aggregate below passes through.
    """
    sub = race[race['source'] == source]
    grid = []
    for c in C_GRID:
        cell = sub[sub['c'] == c]
        if len(cell) == 2 and bool(cell['add_reliable'].all()):
            grid.append(c)
    if log is not None:
        log.info(f"C1 [{source}] pairwise-reliable grid: {grid} ({len(grid)} of {len(C_GRID)} "
                 f"magnitudes). A magnitude qualifies when BOTH arms reach "
                 f"DetRate >= {DET_RATE_FLOOR}; no literal `c >= {NAMED_C_LOW}` is typed.")
    return grid


def ratio_series(race, source, grid):
    """`ADD_Concept / ADD_Eco` at each magnitude of `grid`, in grid order."""
    sub = race[race['source'] == source]
    out = []
    for c in grid:
        add_c = float(sub[(sub['c'] == c) & (sub['arm'] == 'Concept')]['ADD'].iloc[0])
        add_e = float(sub[(sub['c'] == c) & (sub['arm'] == 'Eco')]['ADD'].iloc[0])
        out.append(add_c / add_e)
    return np.array(out, dtype=float)


# --- C5: THE PAIRED MOVING-BLOCK BOOTSTRAP ---

def block_bootstrap_ratios(delays_by_arm, grid, n_onsets, source, log):
    """
    A paired moving-block bootstrap of the ADD ratio over onsets.

    ONE resampled onset-index vector serves both arms and every magnitude of the
    grid, so the pairing the common-random-numbers design creates is preserved
    and the interval is an interval on the DIFFERENCE, not on two independent
    means. The block length is the same `K_LAGS` monthly steps the design effect
    uses, and for the same mechanical reason: two onsets further apart than that
    share no observation.

    This resampling has NO counterpart in the delivered script, so it carries no
    legacy keying in either arm: `--legacy-seeds` restores the three draws the
    submitted campaign made and nothing else.

    Returns `(mean_replicates, per_c_replicates)`, of shapes `(B,)` and
    `(B, len(grid))`. An all-undetected magnitude inside a replicate gives an
    empty slice whose mean is NaN by definition; those replicates are counted
    and excluded, never replaced.
    """
    if not grid:
        return np.empty(0), np.empty((0, 0))
    matrix = {arm: np.vstack([np.where(delays_by_arm[arm][c] == -1, np.nan,
                                       delays_by_arm[arm][c]) for c in grid])
              for arm in ('Concept', 'Eco')}
    n_blocks = int(np.ceil(n_onsets / BOOTSTRAP_BLOCK))
    starts_high = max(1, n_onsets - BOOTSTRAP_BLOCK + 1)
    offsets = np.arange(BOOTSTRAP_BLOCK)
    per_c = np.empty((BOOTSTRAP_REPLICATES, len(grid)), dtype=float)
    for b in range(BOOTSTRAP_REPLICATES):
        starts = rng_for("R14", "onset_bootstrap", source, b).integers(
            0, starts_high, size=n_blocks)
        idx = (starts[:, None] + offsets[None, :]).ravel()[:n_onsets] % n_onsets
        per_c[b] = (np.nanmean(matrix['Concept'][:, idx], axis=1)
                    / np.nanmean(matrix['Eco'][:, idx], axis=1))
    means = np.nanmean(per_c, axis=1)
    n_bad = int(np.sum(~np.isfinite(means)))
    if n_bad:
        log.warning(f"C5 [{source}] bootstrap: {n_bad} of {BOOTSTRAP_REPLICATES} replicates "
                    f"carry a non-finite mean ratio because a resampled grid point had no "
                    f"detection; they are reported and excluded from the quantiles rather than "
                    f"replaced.")
    return means[np.isfinite(means)], per_c


def bootstrap_interval(replicates):
    """The percentile interval of a bootstrap replicate vector."""
    if replicates.size == 0:
        return np.nan, np.nan
    return (float(np.percentile(replicates, 100.0 * BOOTSTRAP_ALPHA / 2.0)),
            float(np.percentile(replicates, 100.0 * (1.0 - BOOTSTRAP_ALPHA / 2.0))))


# --- THE FIGURE ---

def render_figure(race, diagnostics, path, log):
    """
    v87 Figure 16, two panels, drawn from the in-memory campaign.

    Hollow markers on a dashed connector are the unreliable cells, filled
    markers on a solid line the reliable ones, which is the convention the L635
    caption states. The shaded band is `SEM_design`, not the delivered `SEM`:
    the onset windows overlap and the delivered band understates the dispersion
    of the mean by the square root of the design effect.

    ETH is not plotted, matching v87's two-panel figure; its numbers ship in the
    CSVs and in two macros.
    """
    panels = (('A', 'Real_BTC'), ('B', 'Synth_BTC'))
    arm_style = {'Concept': ('mediumblue', 'o', 'Concept (recentred sign CUSUM)'),
                 'Eco': ('darkred', 's', 'Eco-L1 (standardized residual CUSUM)')}
    nu_btc = float(diagnostics[diagnostics['source'] == 'BTC'].iloc[0]['nu_hat'])
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, (letter, source) in zip(axes, panels):
        sub_source = race[race['source'] == source]
        if sub_source.empty:
            log.error(f"Figure 16: {source} carries no row.")
            sys.exit(1)
        n_onsets = int(sub_source['n_onsets'].iloc[0])
        fpr = float(sub_source['FPR_achieved'].iloc[0])
        for arm, (colour, marker, label) in arm_style.items():
            curve = sub_source[sub_source['arm'] == arm].sort_values('c')
            ax.plot(curve['c'], curve['ADD'], marker=marker, markerfacecolor='none',
                    linestyle='--', color=colour, alpha=0.5)
            reliable = curve[curve['add_reliable']]
            if reliable.empty:
                log.warning(f"Figure 16 panel ({letter}): {source} / {arm} has no reliable cell.")
                continue
            ax.plot(reliable['c'], reliable['ADD'], marker=marker, linestyle='-', linewidth=2,
                    color=colour, label=label)
            ax.fill_between(reliable['c'], reliable['ADD'] - reliable['SEM_design'],
                            reliable['ADD'] + reliable['SEM_design'], alpha=0.15, color=colour)
        if letter == 'A':
            title = (f"(A) Daily BTC ($\\hat{{\\nu}} = {nu_btc:.2f}$), "
                     f"{n_onsets} monthly onsets, iso-FPR {100.0 * fpr:.1f}%")
        else:
            title = (f"(B) Quasi-Gaussian $t_{{{SYNTH_NU}}}$ control, "
                     f"same {n_onsets} onsets, iso-FPR {100.0 * fpr:.1f}%")
        ax.set_title(title, fontweight="bold", loc="center")
        ax.set_xlabel("Signal magnitude $c$ (unconditional standard deviations)")
        ax.set_ylabel("Average detection delay (trading days)")
        ax.grid(True, linestyle=':', alpha=0.7)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(dict(zip(labels, handles)).values(), dict(zip(labels, handles)).keys())
        log.info(f"Figure 16 panel ({letter}) {source}: {n_onsets} onsets, realized FPR "
                 f"{fpr!r}, {int(sub_source['add_reliable'].sum())} of {len(sub_source)} cells "
                 f"reliable and drawn filled, the rest hollow on a dashed connector, band = "
                 f"SEM_design.")
    fig.suptitle("Iso-FPR detection-delay race on real Bitcoin and its quasi-Gaussian control",
                 fontweight='bold', fontsize=14, ha='center')
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)
    log.info(f"Figure 16 written to {path.name}. Cosmetic divergence from the submitted "
             f"Fig28_Crypto_HeavyTail_Race.png, per preamble S6: bold horizontally centred panel "
             f"titles prefixed (A) and (B), the panel subject named in the title, and the band "
             f"drawn at SEM_design rather than SEM. No numerical value moves on that account.")


# --- CLASSIFICATION AGAINST THE WITNESS AND AGAINST v87 ---

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


def witness_ratio_mean(witness_race, source, log):
    """
    The witness mean ADD ratio over ITS OWN pairwise-reliable grid, recomputed
    from the submitted CSV by the same derived rule. The delivered
    `verify_invariants` hard-codes `c >= 0.35`; recomputing shows the rule and
    the literal select the same seven magnitudes on BTC, which is what
    discharges control C1 against the witness as well as against this run.
    """
    sub = witness_race[witness_race['source'] == source]
    grid, ratios = [], []
    for c in sorted(sub['c'].unique()):
        cell = sub[sub['c'] == c]
        if len(cell) != 2 or not bool(cell['add_reliable'].all()):
            continue
        grid.append(float(c))
        add_c = float(cell[cell['arm'] == 'Concept']['ADD'].iloc[0])
        add_e = float(cell[cell['arm'] == 'Eco']['ADD'].iloc[0])
        ratios.append(add_c / add_e)
    ratios = np.array(ratios, dtype=float)
    log.info(f"Witness [{source}]: pairwise-reliable grid {grid} ({len(grid)} magnitudes), "
             f"ratios {list(ratios)}, mean {float(np.mean(ratios)) if ratios.size else np.nan!r}.")
    return grid, ratios


def main():
    global logger
    parser = argparse.ArgumentParser(
        description="R14 -- efficiency reversal on real Bitcoin (v87 Figure 16, L345)")
    parser.add_argument(
        "--legacy-seeds",
        action="store_true",
        help="Port-fidelity diagnostic. Restores the delivered RandomState(100 / 200 / 201 / 300) "
             "draws and nothing else, and stamps every output '_legacy_seeds'. It certifies no "
             "v87 value; it separates 'the re-keying moved panel B' from 'the transcription broke "
             "panel B'.")
    args = parser.parse_args()
    legacy = args.legacy_seeds
    sfx = LEGACY_SUFFIX if legacy else ""

    RESULTS_DIR = BASE_DIR / "results" / "R14_crypto_isofpr"
    DATA_DIR = RESULTS_DIR / "data"
    FIGURES_DIR = RESULTS_DIR / "figures"
    TABLES_DIR = RESULTS_DIR / "tables"
    LOGS_DIR = BASE_DIR / "logs" / "R14_crypto_isofpr"
    REQUIREMENTS_DIR = BASE_DIR / "requirements"
    for d in (DATA_DIR, FIGURES_DIR, TABLES_DIR, LOGS_DIR, REQUIREMENTS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(LOGS_DIR / f"exp_R14_crypto_isofpr{sfx}.log", f"exp_R14{sfx}")
    log = logger
    if not verify_hash_seed(log):
        sys.exit(1)
    versions = log_environment(log, list(REQUIREMENT_PACKAGES))
    (REQUIREMENTS_DIR / "R14.txt").write_text(
        "".join(f"{name}=={versions[name]}\n" for name in REQUIREMENT_PACKAGES))
    t0 = time.time()

    log.info("R14 measures v87 Figure 16 (fig:crypto_race) and the numerals of L345: an iso-FPR "
             "race between the recentred sign-CUSUM and a CUSUM on the honestly standardized "
             "GARCH residual, on daily Bitcoin and Ethereum returns and on their quasi-Gaussian "
             "t_30 synthetic controls.")
    if legacy:
        log.warning("LEGACY-SEEDS ARM. The delivered RandomState(100 / 200 / 201 / 300) draws are "
                    "restored and every output is stamped '_legacy_seeds'. This arm CERTIFIES NO "
                    "v87 VALUE. It exists to separate the effect of the entropy migration from a "
                    "transcription error in this port, which is a question about the port and "
                    "not an exploration of how far a published result holds. It is executed "
                    "unconditionally by run_experiment_R14.sh, after the default arm: running a "
                    "diagnostic only when a result looks wrong turns the diagnostic into an "
                    "instrument of selection.")
    log.info("ETH IS A PUBLISHED CLAIM HERE. The Figure 16 caption says nothing about Ethereum, "
             "but L345 publishes its Ljung-Box p, its 72 onsets, the failure of its recentred "
             "sign stream to pass whiteness, and the failure of its synthetic control to recover "
             "the light-tailed ordering. Preamble S3's asymmetry rule applies in the manuscript's "
             "disfavour there: v87 states its own limitation, so reproducing the failure "
             "reproduces a self-critical claim and takes ordinary scrutiny.")

    check_source_identity(log)
    check_entropy_migration(log)

    series = {ticker: load_series(ticker, log) for ticker in ('BTC', 'ETH')}
    qmle_frame, median_bias, fallback_frac = run_qmle_recovery(legacy, log)
    diagnostics = run_diagnostics(series, log)

    variances = {t: float(np.var(series[t]['Log_Return'].values
                                 - np.mean(series[t]['Log_Return'].values)))
                 for t in ('BTC', 'ETH')}
    synthetic = {t: generate_synthetic_garch(len(series[t]), variances[t], nu=SYNTH_NU,
                                             loc_rng=synth_generator(t, legacy))
                 for t in ('BTC', 'ETH')}
    onsets = {t: compute_onsets(series[t], H_REF, H_DET) for t in ('BTC', 'ETH')}
    log.info(f"Onsets: BTC {len(onsets['BTC'])}, ETH {len(onsets['ETH'])}. Synthetic controls: "
             f"t_{SYNTH_NU} GARCH(1,1) matched on the empirical variances "
             f"{variances}, evaluated at the SAME onsets as their real counterparts.")

    # The dither is keyed on the onset index alone, so one vector serves every
    # source: it is identical across the four sources and identical between
    # calibration and race, which is the delivered script's own requirement.
    max_onsets = max(len(onsets['BTC']), len(onsets['ETH']))
    dither = dither_vector(max_onsets, legacy)
    dither_origin = ("the delivered RandomState(100).uniform(-1e-6, 1e-6, N), whose first N "
                     "values are the same for every N" if legacy else
                     "keyed on the onset index alone, so it is bit-identical across the four "
                     "sources and between calibration and race")
    log.info(f"Placebo dither: {max_onsets} values in [-1e-6, 1e-6], "
             f"SHA-256 {hashlib.sha256(np.ascontiguousarray(dither).tobytes()).hexdigest()}, "
             f"{dither_origin}.")

    runs = (('Real_BTC', 'BTC', series['BTC']['Log_Return'].values, onsets['BTC']),
            ('Real_ETH', 'ETH', series['ETH']['Log_Return'].values, onsets['ETH']),
            ('Synth_BTC', 'BTC', synthetic['BTC'], onsets['BTC']),
            ('Synth_ETH', 'ETH', synthetic['ETH'], onsets['ETH']))

    rows, delay_rows, delays, fpr_records = [], [], {}, {}
    for source_name, ticker, r_series, source_onsets in runs:
        r, d, by_arm, fprs = evaluate_source(source_name, ticker, r_series, source_onsets,
                                             dither[:len(source_onsets)], log)
        rows.extend(r)
        delay_rows.extend(d)
        delays[source_name] = by_arm
        fpr_records[source_name] = fprs

    race = pd.DataFrame(rows)
    onset_delays = pd.DataFrame(delay_rows)
    diagnostics['FPR_C_real'] = diagnostics['source'].map(lambda s: fpr_records[f"Real_{s}"][0])
    diagnostics['FPR_E_real'] = diagnostics['source'].map(lambda s: fpr_records[f"Real_{s}"][1])
    diagnostics['n_onsets'] = diagnostics['source'].map(lambda s: len(onsets[s]))

    # =====================================================================
    # CONTROL C2 -- THE REALIZED ISO-FPR, AND ITS FRAGILITY
    # =====================================================================
    log.info("C2 -- the two arms of a source must realize the SAME false-alarm rate on the same "
             "placebo windows; without it the race is not iso-FPR and no speed comparison is "
             "interpretable. Exact equality, per source; deterministic, trigger probability 0 "
             "given the data.")
    log.info(f"C2 SCOPE, fixed before the run and read clause by clause off v87: the sources "
             f"whose SPEED comparison the manuscript publishes are {list(PUBLISHED_SPEED_SOURCES)} "
             f"-- L345's 'the sign filter leads across the reliable range' on Real_BTC, its "
             f"'inverts the ordering to Eco-L1-faster' on the t_30 control, and its 'the "
             f"synthetic control does not recover the light-tailed ordering at its 72 onsets' on "
             f"Synth_ETH. v87 makes no delay and no ordering claim about REAL Ethereum. A failed "
             f"match on one of the three stops the run; a failed match anywhere else makes that "
             f"source's speed comparison uninterpretable and is reported, not repaired.")
    iso_matched = {}
    for source in race['source'].unique():
        sub = race[race['source'] == source]
        values = sub['FPR_achieved'].unique()
        n = int(sub['n_onsets'].iloc[0])
        iso_matched[source] = len(values) == 1
        if iso_matched[source]:
            log.info(f"C2 [{source}]: both arms at {values[0]!r} = "
                     f"{int(round(values[0] * n))}/{n} over all {len(sub)} rows.")
            continue
        counts = {arm: int(sub[sub['arm'] == arm]['FPR_count'].iloc[0]) for arm in ('Concept',
                                                                                   'Eco')}
        message = (f"C2 FIRED on {source}: the two arms realize different placebo counts, "
                   f"Concept {counts['Concept']}/{n} = "
                   f"{counts['Concept'] / n!r} and Eco {counts['Eco']}/{n} = "
                   f"{counts['Eco'] / n!r}. The race on this source is NOT iso-FPR and no speed "
                   f"comparison on it is interpretable.")
        if source in PUBLISHED_SPEED_SOURCES:
            log.error(message + " v87 publishes a speed comparison on this source, so the run "
                                "stops here. No seed, tolerance or parameter is touched.")
            sys.exit(1)
        log.warning(message + " v87 publishes no delay and no ordering claim on this source, so "
                              "the failure is recorded rather than fatal: the source is stamped "
                              "iso_fpr_matched = False on every row of the race CSV, no macro "
                              "reads a speed comparison from it, and the audit reports it.")
    log.info(f"C2 FRAGILITY, logged whatever the outcome. `bisect_fpr` stops when "
             f"|f - {TARGET_FPR}| <= {BISECT_TOL}, and f can only take values k/N. At N = "
             f"{len(onsets['BTC'])} that admits exactly k = 5 "
             f"({5 / len(onsets['BTC']):.6f}), so the BTC agreement is FORCED by the tolerance. "
             f"At N = {len(onsets['ETH'])} it admits NO integer k -- "
             f"{3 / len(onsets['ETH']):.6f} and {4 / len(onsets['ETH']):.6f} straddle the band -- "
             f"so the bisection exhausts its 40 iterations and the ETH agreement is an OUTCOME OF "
             f"THE BISECTION DYNAMICS, not a constraint the calibration enforces. The two "
             f"agreements are not the same kind of fact and the audit reports them separately.")

    # =====================================================================
    # CONTROL C1 -- THE PAIRWISE-RELIABLE GRID, AND WHAT MAY READ IT
    # =====================================================================
    log.info(f"C1 -- no macro and no aggregate reads a cell with add_reliable == False. v87's "
             f"L635 caption renders those cells as hollow markers precisely because their ADD is "
             f"conditional on a detection rate below {DET_RATE_FLOOR}. Structural; trigger "
             f"probability 0.")
    grids = {source: pairwise_reliable_grid(race, source, log)
             for source in ('Real_BTC', 'Real_ETH', 'Synth_BTC', 'Synth_ETH')}
    unreliable = int((~race['add_reliable']).sum())
    log.info(f"C1: {unreliable} of {len(race)} cells are unreliable. The derived rule `both arms "
             f"reach DetRate >= {DET_RATE_FLOOR}` selects {grids['Real_BTC']} on Real_BTC and "
             f"{grids['Synth_BTC']} on Synth_BTC, which is the range the delivered "
             f"`c >= {NAMED_C_LOW}` literal hard-codes; the rule reproduces it without typing it.")

    ratios = {source: ratio_series(race, source, grids[source]) for source in grids}
    for source, values in ratios.items():
        log.info(f"C5 [{source}] ADD_Concept / ADD_Eco at each pairwise-reliable magnitude: "
                 + ", ".join(f"c = {c}: {v:.6f}" for c, v in zip(grids[source], values))
                 + f" | mean {float(np.mean(values)) if values.size else np.nan}"
                 + ("" if iso_matched[source] else
                    " | NOT ISO-FPR (control C2 fired on this source): the two arms ran at "
                    "different realized false-alarm rates, so this ratio series compares two "
                    "detectors at two operating points and is DESCRIPTIVE ONLY. No macro reads "
                    "it and no claim rests on it."))

    # =====================================================================
    # CONTROL C5 -- DIRECTION, MEASURED AND NOT GATED
    # =====================================================================
    n_paired = len(grids['Real_BTC'])
    log.info(f"C5 -- the direction of the ordering, CHARACTERISED AND NOT CORRECTED. The "
             f"delivered Control (d) reads the synthetic ratio at min(reliable c) and exits when "
             f"it is at or below 1.05; a minimum over a grid is an extremum statistic with no "
             f"sampling distribution, which S4bis's fourth corollary bans outright, and the R14 "
             f"prompt's own C5 says characterise, do not correct. What replaces it: the ratio at "
             f"every pairwise-reliable magnitude, its mean, and a paired moving-block bootstrap "
             f"envelope. NOTHING HALTS ON IT except a falsified qualitative claim of v87.")
    log.info(f"C5 FAMILY-WISE ARITHMETIC, logged BEFORE the result is read: over the "
             f"{n_paired} paired magnitudes of Real_BTC, a sign test has trigger probability "
             f"2 * 0.5^{n_paired} = {2 * 0.5 ** n_paired:.6f} under exchangeability of the two "
             f"arms, i.e. {2 * 0.5 ** n_paired:.2%}. The same arithmetic for the per-magnitude "
             f"envelope: reading a 95% band as a maximum over {n_paired} points would trigger "
             f"with probability 1 - 0.95^{n_paired} = {1 - 0.95 ** n_paired:.2%} under its own "
             f"null, which is why the extrema below are DESCRIPTIVE and gate nothing.")

    envelopes = {}
    for source, ticker, _, source_onsets in runs:
        means, per_c = block_bootstrap_ratios(delays[source], grids[source],
                                              len(source_onsets), source, log)
        lo, hi = bootstrap_interval(means)
        envelopes[source] = {'mean': float(np.mean(ratios[source])) if ratios[source].size else np.nan,
                             'ci_low': lo, 'ci_high': hi, 'replicates': means, 'per_c': per_c}
        log.info(f"C5 [{source}] paired moving-block bootstrap: B = {BOOTSTRAP_REPLICATES}, block "
                 f"= {BOOTSTRAP_BLOCK} onsets, one resampled index vector shared by both arms and "
                 f"all {len(grids[source])} magnitudes. Mean ratio "
                 f"{envelopes[source]['mean']!r}, 95% percentile interval [{lo!r}, {hi!r}], "
                 f"{int(np.sum(ratios[source] < 1.0))} of {len(grids[source])} magnitudes below "
                 f"parity.")

    # =====================================================================
    # THE TWO THRESHOLDS OF PREAMBLE S3, EVALUATED SEPARATELY
    # =====================================================================
    log.info("S3 -- a moved numeral and a falsified claim are different thresholds and are "
             "evaluated separately. On L345's synthetic control the QUALITATIVE claim is that the "
             "t_30 control INVERTS the ordering to Eco-L1-faster, so its falsification condition "
             "is that the 95% interval of the regenerated mean ratio lies ENTIRELY BELOW 1. The "
             "printed numeral 1.06 is a different question: it is D2 when the interval excludes "
             "1.06 while the claim still holds. An interval that excludes 1.06 and covers 1 is a "
             "D2 on the numeral and falsifies nothing. A single magnitude below 1 falsifies "
             "nothing at all: v87 itself prints the range 0.98-1.14, which already contains a "
             "point on the other side of parity.")
    stop = []
    for source, claim, direction in (('Real_BTC', "the sign filter leads across the reliable "
                                      "range (ratio below 1)", 'below'),
                                     ('Synth_BTC', "the quasi-Gaussian control inverts the "
                                      "ordering to Eco-L1-faster (ratio above 1)", 'above')):
        env = envelopes[source]
        lo, hi = env['ci_low'], env['ci_high']
        falsified = (hi < 1.0) if direction == 'above' else (lo > 1.0)
        log.info(f"S3 D3 TEST [{source}]: v87's qualitative claim is that {claim}. Regenerated "
                 f"mean ratio {env['mean']!r}, 95% interval [{lo!r}, {hi!r}]. The interval lies "
                 f"entirely on the wrong side of parity: {falsified}.")
        if falsified:
            stop.append(source)
    numeral_checks = (('Real_BTC', V87_RATIO_REAL_MEAN), ('Synth_BTC', V87_RATIO_SYNTH_MEAN))
    for source, printed in numeral_checks:
        env = envelopes[source]
        excludes = not (env['ci_low'] <= printed <= env['ci_high'])
        log.info(f"S3 D2 TEST [{source}]: v87 prints the mean ratio {printed}. The regenerated "
                 f"95% interval [{env['ci_low']!r}, {env['ci_high']!r}] excludes it: {excludes}.")
    if stop:
        log.error(f"S3 D3: a qualitative claim of v87 L345 is falsified on {stop}. Preamble S3 "
                  f"requires stopping here. No parameter, tolerance, seed or bound is moved to "
                  f"reconcile anything; the _legacy_seeds arm is what says whether the entropy "
                  f"migration or the port is responsible, and it runs unconditionally.")
        sys.exit(1)

    # =====================================================================
    # THE PUBLISHED READINGS
    # =====================================================================
    btc = diagnostics[diagnostics['source'] == 'BTC'].iloc[0]
    eth = diagnostics[diagnostics['source'] == 'ETH'].iloc[0]
    real_grid = grids['Real_BTC']
    synth_grid = grids['Synth_BTC']
    real_ratios = ratios['Real_BTC']
    synth_ratios = ratios['Synth_BTC']
    for named in (NAMED_C_LOW, NAMED_C_PARITY):
        if named not in real_grid:
            log.error(f"L345 names c = {named}, and it is not pairwise-reliable on Real_BTC "
                      f"({real_grid}). The sentence reads a magnitude the reliability rule "
                      f"excludes; that is a finding, not a reason to move the rule.")
            sys.exit(1)
    ratio_at_low = float(real_ratios[real_grid.index(NAMED_C_LOW)])
    ratio_at_parity = float(real_ratios[real_grid.index(NAMED_C_PARITY)])
    argmin_c = real_grid[int(np.argmin(real_ratios))]
    log.info(f"The two magnitudes L345 NAMES: ratio {ratio_at_low!r} at c = {NAMED_C_LOW} and "
             f"{ratio_at_parity!r} at c = {NAMED_C_PARITY}. They are read at the named grid "
             f"points and never at an argmin, so they carry a stable sampling distribution. The "
             f"minimum of the regenerated ratio over the reliable grid sits at c = {argmin_c}; "
             f"if that is not {NAMED_C_LOW} it is a finding to report, not a reason to rename a "
             f"macro.")

    # =====================================================================
    # PERSISTENCE
    # =====================================================================
    artefacts = {
        f"R14_crypto_diagnostics{sfx}.csv": diagnostics,
        f"R14_crypto_isofpr_race{sfx}.csv": race,
        f"R14_qmle_recovery{sfx}.csv": qmle_frame,
        f"R14_onset_delays{sfx}.csv": onset_delays,
    }
    for name, frame in artefacts.items():
        save_fair_csv(frame, DATA_DIR / name)
        log.info(f"{name}: {len(frame)} rows, {len(frame.columns)} columns.")

    # C1, re-derived from the PERSISTED file rather than from memory, so that a
    # third party holding only the CSV reaches the same reliable set.
    persisted = pd.read_csv(DATA_DIR / f"R14_crypto_isofpr_race{sfx}.csv",
                            float_precision='round_trip')
    for source, grid in grids.items():
        replayed = pairwise_reliable_grid(persisted, source)
        if replayed != grid:
            log.error(f"C1 FAILED on {source}: the reliable grid re-derived from the persisted "
                      f"CSV is {replayed}, against {grid} in memory.")
            sys.exit(1)
        for c in grid:
            cell = persisted[(persisted['source'] == source) & (persisted['c'] == c)]
            if not bool(cell['add_reliable'].all()):
                log.error(f"C1 FAILED: {source} at c = {c} enters an aggregate with "
                          f"add_reliable == False.")
                sys.exit(1)
    if int((~persisted['add_reliable']).sum()) != unreliable:
        log.error("C1 FAILED: the unreliable count of the persisted CSV differs from memory.")
        sys.exit(1)
    log.info(f"C1: the pairwise-reliable grids re-derive identically from "
             f"R14_crypto_isofpr_race{sfx}.csv, and every aggregate above was taken over them.")

    render_figure(race, diagnostics, FIGURES_DIR / f"fig16_crypto_race{sfx}.png", log)

    # =====================================================================
    # LATEX MACROS
    # =====================================================================
    macros = [
        MACRO_HEADER,
        "% THE CSV CELL BEHIND EACH MACRO.",
        f"%   \\RFourteenNuHatBtc, \\RFourteenNuHatEth, \\RFourteenLjungBoxEth"
        f"      R14_crypto_diagnostics{sfx}.csv, nu_hat / lb_pvalue",
        f"%   \\RFourteenIsoFprBtc                                    same file, FPR_C_real"
        f" (= FPR_E_real, control C2)",
        f"%   \\RFourteenOnsetsBtc, \\RFourteenOnsetsEth               R14_crypto_isofpr_race"
        f"{sfx}.csv, n_onsets",
        f"%   \\RFourteenUnreliableCells, \\RFourteenTotalCells        same file, add_reliable",
        f"%   \\RFourteenRatio...                                     same file, ADD, over the"
        f" pairwise-reliable grid",
        f"%   \\RFourteenQmleMedianBias, \\RFourteenQmleFallbackFrac   R14_qmle_recovery{sfx}.csv",
        "% \\RFourteenRatioRealAtCPointThreeFive and \\RFourteenRatioRealAtParity are read at the",
        "%   grid points L345 NAMES, c = 0.35 and c = 1.5, and never at an argmin: a named point",
        "%   has a stable sampling distribution and an extremum does not. If a redraw moves the",
        "%   minimum of the ratio off c = 0.35, that is a finding to report and not a reason to",
        "%   rename the macro.",
        "% \\RFourteenRatioSynthMin and \\RFourteenRatioSynthMax are EXTREMA over the grid",
        "%   (S4bis, fourth corollary). They are descriptive, they ship with the bootstrap",
        "%   envelope of the mean beside them in the log, and they gate nothing.",
        "% \\RFourteenQmleFallbackFrac is printed even at zero: a fallback counter reported only",
        "%   when it is non-zero establishes nothing about the runs where it is not (control C3).",
        f"\\newcommand{{\\RFourteenNuHatBtc}}{{{float(btc['nu_hat']):.2f}}}",
        f"\\newcommand{{\\RFourteenNuHatEth}}{{{float(eth['nu_hat']):.2f}}}",
        f"\\newcommand{{\\RFourteenIsoFprBtc}}{{{100.0 * float(btc['FPR_C_real']):.1f}\\%}}",
        f"\\newcommand{{\\RFourteenOnsetsBtc}}{{{len(onsets['BTC'])}}}",
        f"\\newcommand{{\\RFourteenOnsetsEth}}{{{len(onsets['ETH'])}}}",
        f"\\newcommand{{\\RFourteenParityMagnitude}}{{{NAMED_C_PARITY:g}}}",
        f"\\newcommand{{\\RFourteenUnreliableCells}}{{{unreliable}}}",
        f"\\newcommand{{\\RFourteenTotalCells}}{{{len(race)}}}",
        f"\\newcommand{{\\RFourteenQmleMedianBias}}{{{median_bias:.4f}}}",
        f"\\newcommand{{\\RFourteenQmleFallbackFrac}}{{{fallback_frac:.4f}}}",
        f"\\newcommand{{\\RFourteenRatioRealAtCPointThreeFive}}{{{ratio_at_low:.2f}}}",
        f"\\newcommand{{\\RFourteenRatioRealAtParity}}{{{ratio_at_parity:.2f}}}",
        f"\\newcommand{{\\RFourteenRatioRealMean}}{{{float(np.mean(real_ratios)):.2f}}}",
        f"\\newcommand{{\\RFourteenRatioSynthMin}}{{{float(np.min(synth_ratios)):.2f}}}",
        f"\\newcommand{{\\RFourteenRatioSynthMax}}{{{float(np.max(synth_ratios)):.2f}}}",
        f"\\newcommand{{\\RFourteenRatioSynthMean}}{{{float(np.mean(synth_ratios)):.2f}}}",
        f"\\newcommand{{\\RFourteenLjungBoxEth}}{{{float(eth['lb_pvalue']):.3f}}}",
    ]
    if legacy:
        macros.insert(1, "% LEGACY-SEEDS DIAGNOSTIC ARM. These macros CERTIFY NO v87 VALUE. They "
                         "are produced by the")
        macros.insert(2, "%   delivered RandomState(100 / 200 / 201 / 300) draws and exist only "
                         "to separate the effect")
        macros.insert(3, "%   of the entropy migration from a transcription error in this port. "
                         "Never \\input this file.")
    tex_path = TABLES_DIR / f"R14_claims{sfx}.tex"
    tex_path.write_text("\n".join(macros) + "\n")
    emitted = [m for m in macros if m.startswith("\\newcommand")]
    bad = [m for m in emitted if 'nan' in m.lower()]
    if bad:
        log.error(f"{len(bad)} macros carry the body `nan`: {bad}")
        sys.exit(1)
    log.info(f"Emitted {len(emitted)} macros to {tex_path.name}, cardinal prefix \\RFourteen per "
             f"preamble S6. Every value is computed from an object in memory.")

    # Log artifact manifest for FAIR traceability
    all_artifacts = [
        DATA_DIR / f"R14_crypto_diagnostics{sfx}.csv",
        DATA_DIR / f"R14_crypto_isofpr_race{sfx}.csv",
        DATA_DIR / f"R14_qmle_recovery{sfx}.csv",
        DATA_DIR / f"R14_onset_delays{sfx}.csv",
        FIGURES_DIR / f"fig16_crypto_race{sfx}.png",
        TABLES_DIR / f"R14_claims{sfx}.tex",
    ]
    log_artifact_manifest(log, all_artifacts, RESULTS_DIR, BASE_DIR)

    # =====================================================================
    # PREAMBLE S3 -- THE CLASSIFICATION, COMPUTED
    # ==========================================================================================================================================
    # PREAMBLE S3 -- THE CLASSIFICATION, COMPUTED
    # =====================================================================
    witnesses = read_witness_csvs(log)
    w_diag = witnesses['diagnostics']
    w_race = witnesses['race']
    w_qmle = witnesses['qmle']
    w_btc = w_diag[w_diag['source'] == 'BTC'].iloc[0]
    w_eth = w_diag[w_diag['source'] == 'ETH'].iloc[0]
    w_real_grid, w_real_ratios = witness_ratio_mean(w_race, 'Real_BTC', log)
    w_synth_grid, w_synth_ratios = witness_ratio_mean(w_race, 'Synth_BTC', log)
    w_eth_synth_grid, w_eth_synth_ratios = witness_ratio_mean(w_race, 'Synth_ETH', log)
    w_qmle_map = dict(zip(w_qmle['Metric'], w_qmle['Value']))
    log.info(f"Witness Synth_ETH: mean ratio "
             f"{float(np.mean(w_eth_synth_ratios)) if w_eth_synth_ratios.size else np.nan!r} over "
             f"{len(w_eth_synth_grid)} pairwise-reliable magnitudes -- the submitted campaign's "
             f"own evidence for L345's 'the synthetic control does not recover the light-tailed "
             f"ordering at its 72 onsets'.")

    def witness_ratio_at(grid, values, c):
        return float(values[grid.index(c)]) if c in grid else None

    classify("nu_hat BTC", btc['nu_hat'], w_btc['nu_hat'], V87_NU_HAT_BTC, 2, log)
    classify("iso-FPR BTC, percent", 100.0 * float(btc['FPR_C_real']),
             100.0 * float(w_btc['FPR_C_real']), V87_ISO_FPR_PERCENT, 1, log)
    classify("Ljung-Box p, ETH", eth['lb_pvalue'], w_eth['lb_pvalue'], V87_LJUNG_BOX_ETH, 3, log)
    classify("onsets BTC", len(onsets['BTC']), int(w_race[w_race['source'] == 'Real_BTC']
                                                   ['n_onsets'].iloc[0]), V87_ONSETS_BTC, 0, log)
    classify("onsets ETH", len(onsets['ETH']), int(w_race[w_race['source'] == 'Real_ETH']
                                                   ['n_onsets'].iloc[0]), V87_ONSETS_ETH, 0, log)
    classify(f"Real_BTC ratio at c = {NAMED_C_LOW}", ratio_at_low,
             witness_ratio_at(w_real_grid, w_real_ratios, NAMED_C_LOW),
             V87_RATIO_REAL_AT_C_LOW, 2, log)
    classify(f"Real_BTC ratio at c = {NAMED_C_PARITY}", ratio_at_parity,
             witness_ratio_at(w_real_grid, w_real_ratios, NAMED_C_PARITY),
             V87_RATIO_REAL_AT_PARITY, 2, log)
    classify("Real_BTC mean ratio", float(np.mean(real_ratios)),
             float(np.mean(w_real_ratios)), V87_RATIO_REAL_MEAN, 2, log)
    classify("Synth_BTC mean ratio", float(np.mean(synth_ratios)),
             float(np.mean(w_synth_ratios)), V87_RATIO_SYNTH_MEAN, 2, log)
    classify("Synth_BTC ratio minimum", float(np.min(synth_ratios)),
             float(np.min(w_synth_ratios)), V87_RATIO_SYNTH_MIN, 2, log)
    classify("Synth_BTC ratio maximum", float(np.max(synth_ratios)),
             float(np.max(w_synth_ratios)), V87_RATIO_SYNTH_MAX, 2, log)
    log.info(f"S3 [QMLE median bias]: no v87 numeral; witness "
             f"{float(w_qmle_map['Median_Bias'])!r}, regenerated {median_bias!r}. The entropy "
             f"migration redraws the twenty recovery streams, so this moves by construction and "
             f"is pre-classified Class A / D2 under `R14-campaign-redraw`.")
    log.info(f"S3 [QMLE fallback fraction]: witness {float(w_qmle_map['Fallback_Frac'])!r}, "
             f"regenerated {fallback_frac!r} (control C3, reported even at zero).")
    log.info(f"S3 [unreliable cells]: v87 prints no such count; the R14 prompt states 25 of 88. "
             f"Witness {int((~w_race['add_reliable']).sum())} of {len(w_race)}, regenerated "
             f"{unreliable} of {len(race)}.")
    eth_synth_grid = grids['Synth_ETH']
    eth_synth_mean = float(np.mean(ratios['Synth_ETH'])) if ratios['Synth_ETH'].size else np.nan
    log.info(f"S3 [ETH synthetic control]: L345 states that the synthetic control does not "
             f"recover the light-tailed ordering at ETH's onsets. Witness mean ratio "
             f"{float(np.mean(w_eth_synth_ratios)) if w_eth_synth_ratios.size else np.nan!r} over "
             f"{len(w_eth_synth_grid)} magnitudes; regenerated {eth_synth_mean!r} over "
             f"{len(eth_synth_grid)} magnitudes, 95% interval "
             f"[{envelopes['Synth_ETH']['ci_low']!r}, {envelopes['Synth_ETH']['ci_high']!r}]. The "
             f"claim is v87's own limitation, so reproducing it reproduces a self-critical "
             f"statement.")

    # =====================================================================
    # DIGESTS
    # =====================================================================
    for name in list(artefacts) + [f"fig16_crypto_race{sfx}.png", f"R14_claims{sfx}.tex"]:
        directory = (DATA_DIR if name.endswith(".csv")
                     else FIGURES_DIR if name.endswith(".png") else TABLES_DIR)
        log.info(f"SHA-256 {name:<40} : {compute_sha256(directory / name)}")
    log.info(f"Execution completed in {time.time() - t0:.1f}s "
             f"({'legacy-seeds diagnostic arm' if legacy else 'migrated default arm'}).")


if __name__ == "__main__":
    main()
