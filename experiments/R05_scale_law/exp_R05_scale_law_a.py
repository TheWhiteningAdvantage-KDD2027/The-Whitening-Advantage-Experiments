#!/usr/bin/env python3
"""
==========================================================================
R05a -- ABRUPT SCALE SHIFT: DELAY VERSUS THE GARCH PENALTY (FIGURE 5A)
==========================================================================
Measures the detection delay of the Data pipeline under an abrupt scale
pathology, across thirteen values of the GARCH penalty Gamma, every arm
calibrated to its own 5% null quantile so that a comparison of delays is licit.

Two statements are under test.

1. Delay inflation (Proposition prop:add_garch of v87). At fixed standardized
   shift the Data delay grows linearly in Gamma. v87 sec:scaling_validation
   prints ADD ~ 23.7 Gamma + 38.

2. Location/scale orthogonality (Proposition prop:orthogonality). The injected
   pathology multiplies the innovation variance by s^2 and leaves the
   conditional sign law untouched, so the Concept monitor reading only the sign
   stream must return its own false-alarm rate and nothing more.

The second statement carries a subtlety this script makes explicit rather than
hides. Because sign(eps_t) = sign(z_t) and the pathology scales by s > 0, the
sign stream is invariant under the drift BY CONSTRUCTION: the blindness of the
Concept arm is an algebraic identity of the design, not an empirical finding,
and it would be reproduced by a monitor that had stopped working altogether.
Two devices separate those cases:

  - a blocking invariance assertion inside the drift worker, which checks that
    the sign stream really is untouched by the injected pathology (it would fire
    if the drift leaked into the Concept branch);
  - a POSITIVE CONTROL arm carrying a pure location shift on a disjoint seed
    block, whose Concept detection rate must exceed its own false-alarm rate by
    a margin a proportion test resolves. Without it, "blind" and "broken" are
    the same measurement.

Notations (v87 sec:scaling_validation, app:scaling):
- Gamma        : GARCH penalty factor, the inflation of the variance of the
                 partial sums of the monitored statistic; closed form in
                 (alpha, beta).
- e_t          : the monitored Data statistic, (eps_t^2 - mu_hat)/sig_hat, with
                 mu_hat and sig_hat estimated on the warm-up of each stream.
- s            : multiplicative standard-deviation factor of the injected scale
                 pathology; the variance is multiplied by s^2 and the
                 conditional sign law is unchanged.
- Delta_mu_max : standardized post-onset shift of the monitored statistic, held
                 at 2 for every Gamma so the arms are commensurable.
- delta_P      : CUSUM reference drift (dead band) of the Data arm.
- delta_C      : CUSUM reference drift of the Concept arm.
- lambda_star  : empirical null quantile of the running CUSUM maximum, the
                 threshold delivering the target false-alarm rate.
- lambda_iid   : lambda_star measured at Gamma = 1, the recalibration reference.
- ADD          : average detection delay in steps after onset, conditional on
                 detection. DetRate : fraction of streams that alarmed.

References:
- Bollerslev, T. (1986). Generalized autoregressive conditional
  heteroskedasticity. Journal of Econometrics, 31(3), 307-327.
- Francq, C. & Zakoian, J.-M. (2010). GARCH Models. Wiley.
- Page, E. S. (1954). Continuous inspection schemes. Biometrika, 41(1/2), 100-115.
- Siegmund, D. (1985). Sequential Analysis. Springer.
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

import os

from experiments.common.fair_env import (
    _THREAD_VARIABLES, enforce_strict_determinism, verify_hash_seed, log_environment,
)

# This module is both an entry point and a library: steps b and c import its
# constants, primitives and seed derivation so the chain runs in one process and
# no CSV ever serves as a bridge between stages (SPECS 1.6).
#
# Only the entry point may post the environment block. Once NumPy is loaded the
# BLAS thread limits have already been read and a second assignment is inert, so
# re-posting it would be a silent no-op dressed as a safeguard. When imported,
# this module therefore VERIFIES that the importing entry point posted the block,
# and refuses to load if it did not -- a degraded path that produced numbers
# would be worse than a crash (preamble S4.3).
if "numpy" in sys.modules:
    _unpinned = [name for name in _THREAD_VARIABLES if os.environ.get(name) != "1"]
    if os.environ.get("MKL_CBWR") != "COMPATIBLE":
        _unpinned.append("MKL_CBWR")
    if _unpinned:
        raise RuntimeError(
            f"exp_R05_scale_law_a was imported after NumPy was loaded, but the determinism "
            f"block is not in place: {_unpinned}. The importing module must call "
            f"enforce_strict_determinism() before importing numpy, pandas or scipy."
        )
else:
    enforce_strict_determinism()

import numpy as np
import pandas as pd
from experiments.common.fair_harness import setup_logging, disable_pandas_multithreading, save_fair_csv

disable_pandas_multithreading()

import math
import time
import random
import hashlib
import argparse
from concurrent.futures import ProcessPoolExecutor

import scipy.stats as stats
from scipy.optimize import brentq

# --- PROTOCOL SPECIFICATION (v87, sec:scaling_validation, fig:scale_law) ---
# Binding specification. If this script diverges from these values, the script
# is wrong and must be corrected, not the manuscript.
#   "400 seeds per configuration"                      -> N_DRIFT, N_CALIB, N_VAL
#   "Student-t_7, alpha = 0.08, beta solved per Gamma" -> NU, ALPHA_GARCH
#   "the injected drift multiplies the innovation variance by s^2"
#   "s set per Gamma so the standardized shift equals Delta_mu_max = 2"
#   "each Data arm calibrated to 5% false alarms by its own null quantile"
#   "the Concept CUSUM fixed once and for all, lambda_C = 10, delta_C = 0.1"
NU = 7.0
ALPHA_GARCH = 0.08
DMU_TARGET = 2.0
DELTA_P = 0.5
DELTA_C = 0.1
TARGET_FPR = 0.05

# Gamma grid bounded near 30: beyond it the fourth moment of eps diverges for
# t_7 (5 alpha^2 + 2 alpha beta + beta^2 >= 1), the standard deviation of eps^2
# explodes and the standardized statistic ceases to be defined. That regime is
# the "stochastic syncope" of v87 sec:singularity and is not this experiment's
# subject.
GAMMA_TARGETS = (1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 18.0, 21.0, 24.0, 27.0, 30.0)

WARMUP = 3000
MONITOR_H = 5000
N_STEPS = WARMUP + MONITOR_H

N_CALIB = 400
N_VAL = 400
N_DRIFT = 400

# --- THE lambda_C NUMERAL OF v87, AND WHY IT IS A DIAGNOSTIC AND NOT THE ARM ---
# v87 sec:scaling_validation states the Concept CUSUM is "fixed once and for
# all, lambda_C = 10, delta_C = 0.1". Read in float_precision='round_trip', the
# numeral 10 matches no campaign of the submitted study: the abrupt campaign
# calibrated 10.8, the ramp campaigns 15.81 at H = 2e5 and 19.02 at H = 3e6.
# What IS exact in that sentence, and what carries the orthogonality thesis, is
# that the Concept threshold is fixed with respect to Gamma: lambda_star_Concept
# is rigorously constant across the grid while lambda_star_Data runs from 43.9
# to 847.7 on the same rows.
#
# The reference arm is therefore the horizon-calibrated one, which produced
# every published number and carries the certification. The literal lambda_C =
# 10 is emitted alongside it as a DIAGNOSTIC whose function is to price the
# manuscript's numeral, not to offer a competing result. It costs no compute:
# the same running maxima are compared against a second threshold.
LAMBDA_C_LITERAL = 10.0

# --- POSITIVE CONTROL: MAGNITUDE, AND WHERE IT COMES FROM ---
# The Concept arm must be shown responsive before its blindness to scale means
# anything. The magnitude is not tuned here: it is read off R04, which measures
# the same sign-CUSUM family over the same 5000-step horizon at Gamma = 11.58
# and reports DetRate = 1.0 with a conditional delay of 42.6 steps at c = 1.0
# (results/R04_isofpr_race/data/R04_isofpr_race.csv, arm Concept). A delay two
# orders of magnitude inside the horizon is not a marginal detection, so a
# failure here is an instrument failure and not a power failure.
POSITIVE_CONTROL_GAMMA = 11.58
POSITIVE_CONTROL_C = 1.0

# Vacuity guard of the orthogonality control. An equality DetRate == FPR is
# trivially true when both are 0 or both are 1, so the equality is only
# informative while the monitor is operating away from its saturation points.
# The band is set from the attainable-level structure of the Concept CUSUM
# rather than from any observed value: under a dead band delta_C the two-sided
# increments live on a lattice of step 2 delta_C, so realised levels are
# discrete, and the submitted campaigns land between 3% and 10%. A band of
# [0.01, 0.20] admits that whole range with an order of magnitude of slack on
# each side while still excluding the degenerate ends.
CONCEPT_VACUITY_BAND = (0.01, 0.20)


def get_deterministic_seed(*args) -> int:
    """
    Derives a 128-bit collision-free seed from the semantic coordinates of a
    task, returned as a scalar integer so no entropy is discarded.

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


def seed_for(role: str, index: int) -> int:
    """
    Seed key for one replicate of one role.

    The key deliberately carries the ROLE and the REPLICATE INDEX only, and
    never Gamma, beta, w or the budget. That is not an oversight: it is the
    common-random-numbers design of SPECS 1.4. Every penalty sees the same
    innovation sequence, so a difference between two values of Gamma is a
    response of the algorithm and not a difference of draw. Keying on Gamma
    would raise the entropy of the key and destroy the comparison the
    experiment exists to make.

    The four roles occupy disjoint key spaces by construction, since the role
    string enters the digest:
      null  -- streams under H_0, split into a calibration half and a hold-out half
      iid   -- streams at Gamma = 1 for the recalibration reference
      drift -- streams carrying the scale pathology
      loc   -- streams carrying the location shift of the positive control
    """
    return get_deterministic_seed("R05", role, index)


def make_rng(seed_int: int) -> np.random.Generator:
    """
    Builds the worker generator and pins the legacy global states.

    SciPy and any third-party routine that samples without being handed a
    generator consumes the global NumPy and random states, which a worker
    process inherits in whatever condition the parent left them. Both are
    therefore pinned from a spawned child of the same seed sequence, disjoint
    from the child that drives the returned generator (SPECS 1.3).
    """
    ss = np.random.SeedSequence(entropy=seed_int)
    child_rng, child_legacy = ss.spawn(2)
    legacy = int(child_legacy.generate_state(1)[0]) & 0xFFFFFFFF
    np.random.seed(legacy)
    random.seed(legacy)
    return np.random.default_rng(child_rng)


# --- PRIMITIVES, DUPLICATED VERBATIM PER PREAMBLE S4.2 ---
# These routines are deliberately NOT hoisted into experiments/common/. The
# copies carried by the other experiments of this repository differ numerically
# from one another, and mutualising them would silently move published values.

def gamma_closed(alpha, beta):
    """
    Closed-form GARCH penalty: the normalised spectral density at frequency zero
    of the squared-innovation process (Bollerslev 1986; Francq & Zakoian 2010).
    """
    denom = 1.0 - 2.0 * alpha * beta - beta ** 2
    rho1 = alpha * (1.0 - beta * (alpha + beta)) / denom
    return 1.0 + 2.0 * rho1 / (1.0 - alpha - beta)


def solve_beta(gamma_target, alpha):
    """Solves gamma_closed(alpha, beta) = gamma_target for beta on (0, 1-alpha)."""
    f = lambda b: gamma_closed(alpha, b) - gamma_target
    return brentq(f, 1e-6, 1.0 - alpha - 1e-6, xtol=1e-10, rtol=1e-12)


def regime_for_gamma(g, alpha):
    """Returns (alpha_eff, beta). Gamma = 1 is the i.i.d. point, alpha = beta = 0."""
    if g <= 1.0 + 1e-9:
        return 0.0, 0.0
    return alpha, solve_beta(g, alpha)


def gen_eps(n, alpha, beta, nu, rng):
    """
    GARCH(1,1) innovations with unconditional variance 1 and standardized
    Student-t shocks. omega = 1 - alpha - beta fixes the variance target.
    """
    z = rng.standard_t(nu, size=n) * math.sqrt((nu - 2.0) / nu)
    if alpha == 0.0 and beta == 0.0:
        return z
    omega = 1.0 - alpha - beta
    eps = np.empty(n)
    s2 = 1.0
    e2 = 1.0
    for t in range(n):
        s2 = omega + alpha * e2 + beta * s2
        e = math.sqrt(s2) * z[t]
        eps[t] = e
        e2 = e * e
    return eps


def cusum1_maxS(x, delta):
    """Running maximum of the one-sided CUSUM recursion (Data arm)."""
    S = 0.0
    mx = 0.0
    for v in x:
        S += v - delta
        if S < 0.0:
            S = 0.0
        elif S > mx:
            mx = S
    return mx


def cusum1_firstpass(x, delta, thr):
    """First index at which the one-sided CUSUM exceeds thr, or -1 if never."""
    S = 0.0
    for i in range(len(x)):
        S += x[i] - delta
        if S < 0.0:
            S = 0.0
        elif S > thr:
            return i
    return -1


def cusum2_maxexc(m, delta):
    """Running maximum of the two-sided CUSUM recursion (Concept arm)."""
    Sp = 0.0
    Sn = 0.0
    mx = 0.0
    for v in m:
        Sp += v - delta
        if Sp < 0.0:
            Sp = 0.0
        Sn += -v - delta
        if Sn < 0.0:
            Sn = 0.0
        e = Sp if Sp > Sn else Sn
        if e > mx:
            mx = e
    return mx


def cusum2_firstpass(m, delta, thr):
    """First index at which the two-sided CUSUM exceeds thr, or -1 if never."""
    Sp = 0.0
    Sn = 0.0
    for i in range(len(m)):
        v = m[i]
        Sp += v - delta
        if Sp < 0.0:
            Sp = 0.0
        Sn += -v - delta
        if Sn < 0.0:
            Sn = 0.0
        if Sp > thr or Sn > thr:
            return i
    return -1


def wilson_interval(k, n, confidence=0.95):
    """Wilson score interval, clamped to the unit interval before persistence."""
    if n == 0:
        return 0.0, 0.0
    z = stats.norm.ppf(0.5 + confidence / 2.0)
    p_hat = k / n
    den = 1.0 + z * z / n
    centre = (p_hat + z * z / (2.0 * n)) / den
    half = z * math.sqrt(p_hat * (1.0 - p_hat) / n + z * z / (4.0 * n * n)) / den
    low = max(0.0, min(1.0, centre - half))
    high = max(0.0, min(1.0, centre + half))
    return min(low, p_hat), max(high, p_hat)


def two_proportion_test(k1, n1, k2, n2):
    """
    Two-sided Fisher exact test on two independent binomial counts, returning
    (difference in streams, p-value).

    UNPAIRED, deliberately. The two rates being compared -- the detection rate
    of the drift block and the false-alarm rate of the null hold-out block --
    are measured on DISJOINT seed blocks, so no pairing exists to exploit and a
    McNemar test has no discordant pairs to count.

    Pairing them would require running both on one seed block, and under a pure
    scale pathology that comparison is degenerate rather than powerful: the sign
    stream is invariant under the drift, so every pair is concordant by
    construction and the paired statistic is identically zero whatever the
    monitor does. That identity is worth asserting -- and it IS asserted, inside
    the drift worker -- but it is an invariance check, not a test of equality of
    two rates. Fisher's exact test is used rather than a normal approximation
    because the counts are small (of order 40 out of 400).
    """
    table = [[k1, n1 - k1], [k2, n2 - k2]]
    _, p_value = stats.fisher_exact(table, alternative='two-sided')
    return k1 - k2, float(p_value)


# --- WORKERS ---
# Each worker receives its own seed and returns a plain tuple. Reduction is by
# executor.map in submission order, never as_completed (SPECS 1.5), and no
# worker writes to the log: messages are accumulated by the parent.

def _worker_null(args):
    """One stream under H_0. Returns the warm-up moments and both running maxima."""
    index, alpha, beta = args
    rng = make_rng(seed_for("null", index))
    eps = gen_eps(N_STEPS, alpha, beta, NU, rng)
    eps2 = eps * eps
    mu = float(eps2[:WARMUP].mean())
    sig = float(eps2[:WARMUP].std(ddof=1))
    e_data = ((eps2[WARMUP:] - mu) / sig).tolist()
    m_sign = ((eps[WARMUP:] > 0.0).astype(float) - 0.5).tolist()
    return mu, sig, cusum1_maxS(e_data, DELTA_P), cusum2_maxexc(m_sign, DELTA_C)


def _worker_scale_drift(args):
    """
    One stream carrying the abrupt scale pathology.

    The variance of the monitored window is multiplied by s^2. The sign stream
    is built from eps itself and is therefore untouched, which the assertion
    below states rather than assumes: it is the invariance that makes the
    Concept blindness an identity, and it is exactly what would break if the
    pathology ever leaked into the Concept branch.
    """
    index, alpha, beta, s, thr_data, thr_concept = args
    rng = make_rng(seed_for("drift", index))
    eps = gen_eps(N_STEPS, alpha, beta, NU, rng)
    eps2 = eps * eps
    mu = float(eps2[:WARMUP].mean())
    sig = float(eps2[:WARMUP].std(ddof=1))

    monitored = eps[WARMUP:]
    sign_undrifted = (monitored > 0.0).astype(float) - 0.5
    sign_drifted = ((monitored * s) > 0.0).astype(float) - 0.5
    if not np.array_equal(sign_undrifted, sign_drifted):
        raise AssertionError(
            f"Scale pathology altered the sign stream at replicate {index}: a positive "
            f"scale factor cannot change a sign, so the Concept branch has been fed the "
            f"drifted series. Every blindness statement of this experiment depends on "
            f"this invariance."
        )

    mon2 = eps2[WARMUP:] * (s * s)
    e_data = ((mon2 - mu) / sig).tolist()
    m_sign = sign_undrifted.tolist()
    return (cusum1_firstpass(e_data, DELTA_P, thr_data),
            cusum2_firstpass(m_sign, DELTA_C, thr_concept),
            cusum2_firstpass(m_sign, DELTA_C, LAMBDA_C_LITERAL))


def _worker_location(args):
    """
    One stream of the positive control: a pure location shift of c * sigma_unc,
    the unconditional standard deviation being 1 by the variance target of
    gen_eps. Only the Concept arm is read; the point is instrument
    responsiveness, not a delay measurement.
    """
    index, alpha, beta, shift, thr_concept = args
    rng = make_rng(seed_for("loc", index))
    eps = gen_eps(N_STEPS, alpha, beta, NU, rng)
    monitored = eps[WARMUP:] + shift
    m_sign = ((monitored > 0.0).astype(float) - 0.5).tolist()
    return (cusum2_firstpass(m_sign, DELTA_C, thr_concept),
            cusum2_firstpass(m_sign, DELTA_C, LAMBDA_C_LITERAL))


def run_abrupt(executor, logger, n_calib, n_val, n_drift):
    """
    Runs the abrupt campaign and returns (grid frame, positive-control frame).

    Both frames are returned in memory. Step c consumes them directly; the CSV
    written by main() is a deliverable, never a bridge between stages
    (SPECS 1.6).
    """
    rows = []
    max_by_gamma = {}

    for gamma_target in GAMMA_TARGETS:
        alpha, beta = regime_for_gamma(gamma_target, ALPHA_GARCH)
        gamma = gamma_closed(alpha, beta)

        null = list(executor.map(_worker_null,
                                 [(i, alpha, beta) for i in range(n_calib + n_val)],
                                 chunksize=8))
        mus = np.array([r[0] for r in null])
        sigs = np.array([r[1] for r in null])
        max_data = np.array([r[2] for r in null])
        max_concept = np.array([r[3] for r in null])
        max_by_gamma[gamma] = max_data[n_calib:]

        # Commensurability: s is solved so the standardized post-onset shift of
        # the monitored statistic equals Delta_mu_max at every Gamma. Without
        # it the delay comparison across Gamma would confound the penalty with
        # the amplitude of the pathology.
        pop_mu, pop_sig = mus.mean(), sigs.mean()
        s_scale = math.sqrt(1.0 + DMU_TARGET * pop_sig / pop_mu)

        lam_data = float(np.quantile(max_data[:n_calib], 1.0 - TARGET_FPR))
        lam_concept = float(np.quantile(max_concept[:n_calib], 1.0 - TARGET_FPR))

        hold_data = max_data[n_calib:]
        hold_concept = max_concept[n_calib:]
        fpr_data = float((hold_data > lam_data).mean())
        fpr_concept = float((hold_concept > lam_concept).mean())
        fpr_concept_literal = float((hold_concept > LAMBDA_C_LITERAL).mean())

        drift = list(executor.map(_worker_scale_drift,
                                  [(i, alpha, beta, s_scale, lam_data, lam_concept)
                                   for i in range(n_drift)],
                                  chunksize=8))
        add_data = np.array([r[0] for r in drift], dtype=float)
        add_concept = np.array([r[1] for r in drift], dtype=float)
        add_concept_literal = np.array([r[2] for r in drift], dtype=float)
        det_data = add_data >= 0
        det_concept = add_concept >= 0
        det_concept_literal = add_concept_literal >= 0

        def _conditional(values, mask):
            if not mask.any():
                return float('nan'), float('nan')
            sel = values[mask]
            mean = float(sel.mean())
            sem = float(sel.std(ddof=1) / math.sqrt(mask.sum())) if mask.sum() > 1 else float('nan')
            return mean, sem

        add_d, sem_d = _conditional(add_data, det_data)
        add_c, sem_c = _conditional(add_concept, det_concept)

        det_c_low, det_c_high = wilson_interval(int(det_concept.sum()), n_drift)
        fpr_c_low, fpr_c_high = wilson_interval(int((hold_concept > lam_concept).sum()), n_val)

        rows.append(dict(
            Gamma=gamma, alpha=alpha, beta=beta, s_scale=s_scale,
            dmu_std_target=DMU_TARGET, delta_P=DELTA_P, delta_C=DELTA_C,
            mon_len=MONITOR_H, warmup=WARMUP, n_calib=n_calib, n_val=n_val, n_drift=n_drift,
            lambda_star_Data=lam_data, lambda_star_Concept=lam_concept,
            lambda_C_literal=LAMBDA_C_LITERAL,
            FPR_Data_val=fpr_data, FPR_Concept_val=fpr_concept,
            FPR_Concept_literal=fpr_concept_literal,
            FPR_Concept_val_CI_low=fpr_c_low, FPR_Concept_val_CI_high=fpr_c_high,
            DetRate_Data=float(det_data.mean()),
            ADD_Data=add_d, SEM_Data=sem_d,
            censored_Data=float((~det_data).mean()),
            DetRate_Concept=float(det_concept.mean()),
            DetRate_Concept_CI_low=det_c_low, DetRate_Concept_CI_high=det_c_high,
            ADD_Concept=add_c, SEM_Concept=sem_c,
            DetRate_Concept_literal=float(det_concept_literal.mean()),
            n_detected_Concept=int(det_concept.sum()),
            n_alarm_Concept_null=int((hold_concept > lam_concept).sum()),
        ))
        logger.info(
            f"[Gamma={gamma:6.2f}] beta={beta:.6f} s={s_scale:5.3f} "
            f"lambda*_Data={lam_data:9.3f} lambda*_Concept={lam_concept:6.2f} "
            f"FPR_Data={fpr_data:.4f} ADD_Data={add_d:9.3f} DetRate_Data={det_data.mean():.4f} "
            f"DetRate_Concept={det_concept.mean():.4f}"
        )

    frame = pd.DataFrame(rows)

    # Recalibration rule of Proposition prop:add_garch, priced on the hold-out
    # half so the comparison is out of sample.
    lam_iid = float(frame.loc[frame.Gamma.idxmin(), "lambda_star_Data"])
    frame["ratio_lam_star"] = frame.lambda_star_Data / lam_iid
    frame["FPR_rule_xGamma"] = [
        float((max_by_gamma[g] > lam_iid * g).mean()) for g in frame.Gamma
    ]
    frame["FPR_rule_xSqrtGamma"] = [
        float((max_by_gamma[g] > lam_iid * math.sqrt(g)).mean()) for g in frame.Gamma
    ]

    # --- POSITIVE CONTROL ---
    # The Concept threshold and its null level are read from row 0 rather than
    # from a row matched to POSITIVE_CONTROL_GAMMA, because the entire Concept
    # branch is Gamma-invariant: the sign stream is a function of z alone and
    # does not see beta. That invariance is asserted here rather than assumed,
    # since it is the premise that makes any row an admissible source.
    concept_invariant = ("lambda_star_Concept", "FPR_Concept_val", "n_alarm_Concept_null")
    varying = [c for c in concept_invariant if frame[c].nunique() != 1]
    if varying:
        raise AssertionError(
            f"Concept columns {varying} vary across Gamma. The sign stream is a function of z "
            f"alone under common random numbers, so this cannot happen unless the Concept "
            f"branch has been keyed on a GARCH parameter.")

    alpha_pc, beta_pc = regime_for_gamma(POSITIVE_CONTROL_GAMMA, ALPHA_GARCH)
    gamma_pc = gamma_closed(alpha_pc, beta_pc)
    lam_concept_pc = float(frame.lambda_star_Concept.iloc[0])
    fpr_concept_pc = float(frame.FPR_Concept_val.iloc[0])
    n_alarm_null_pc = int(frame.n_alarm_Concept_null.iloc[0])

    located = list(executor.map(_worker_location,
                                [(i, alpha_pc, beta_pc, POSITIVE_CONTROL_C, lam_concept_pc)
                                 for i in range(n_drift)],
                                chunksize=8))
    add_loc = np.array([r[0] for r in located], dtype=float)
    det_loc = add_loc >= 0
    add_loc_mean = float(add_loc[det_loc].mean()) if det_loc.any() else float('nan')
    det_low, det_high = wilson_interval(int(det_loc.sum()), n_drift)
    diff_streams, p_value = two_proportion_test(
        int(det_loc.sum()), n_drift, n_alarm_null_pc, n_val)

    positive = pd.DataFrame([dict(
        Gamma=gamma_pc, c=POSITIVE_CONTROL_C, Delta_std=POSITIVE_CONTROL_C,
        pathology="location", mon_len=MONITOR_H, n_streams=n_drift,
        lambda_star_Concept=lam_concept_pc, delta_C=DELTA_C,
        FPR_Concept_val=fpr_concept_pc, n_alarm_Concept_null=n_alarm_null_pc,
        DetRate_Concept=float(det_loc.mean()),
        DetRate_Concept_CI_low=det_low, DetRate_Concept_CI_high=det_high,
        n_detected=int(det_loc.sum()), ADD_Concept=add_loc_mean,
        excess_streams=int(diff_streams), fisher_p_value=p_value,
    )])

    return frame, positive


def certify(frame, positive, logger):
    """
    Blocking controls (a), (c) and (d) of the R05 prompt, evaluated on the
    regenerated campaign. Every threshold here is a literal of v87 or a
    structural relation; none is a published measurement used as a target.
    """
    failures = []

    # (a) v87 conformance, in the amended form: the numeral lambda_C = 10 is not
    # asserted, because it matches no campaign of the study. What IS asserted is
    # the property that numeral was meant to express -- that the Concept
    # threshold does not depend on Gamma -- together with delta_C, which the
    # witness does not contradict.
    if float(frame.delta_C.iloc[0]) != DELTA_C:
        failures.append(f"delta_C is {frame.delta_C.iloc[0]}, v87 specifies {DELTA_C}")
    n_concept_thresholds = frame.lambda_star_Concept.nunique()
    if n_concept_thresholds != 1:
        failures.append(
            f"lambda_star_Concept takes {n_concept_thresholds} distinct values across Gamma; "
            f"v87 sec:scaling_validation states the Concept CUSUM is fixed once and for all")
    logger.info(
        f"[control a] alpha={ALPHA_GARCH} nu={NU} Delta_mu_max={DMU_TARGET} delta_C={DELTA_C} "
        f"target FPR={TARGET_FPR} seeds/config={int(frame.n_drift.iloc[0])} "
        f"Gamma grid n={len(frame)} in [{frame.Gamma.min():.2f}, {frame.Gamma.max():.2f}]")
    logger.info(
        f"[control a] lambda_star_Concept constant across Gamma at "
        f"{frame.lambda_star_Concept.iloc[0]:.4f} while lambda_star_Data runs "
        f"{frame.lambda_star_Data.min():.4f} to {frame.lambda_star_Data.max():.4f} "
        f"(ratio {frame.lambda_star_Data.max()/frame.lambda_star_Data.min():.1f}x)")

    # (c) Orthogonality, on the reference arm only, with the vacuity guard first.
    fpr_concept = float(frame.FPR_Concept_val.iloc[0])
    lo, hi = CONCEPT_VACUITY_BAND
    if not (lo <= fpr_concept <= hi):
        failures.append(
            f"[vacuity] Concept hold-out FPR is {fpr_concept:.4f}, outside {CONCEPT_VACUITY_BAND}. "
            f"At a saturated level the equality DetRate == FPR is true of any monitor, "
            f"including one that has stopped working, so the orthogonality control measures "
            f"nothing and is not reported as passing.")
    else:
        det = int(frame.n_detected_Concept.iloc[0])
        alarms = int(frame.n_alarm_Concept_null.iloc[0])
        diff, p_value = two_proportion_test(det, int(frame.n_drift.iloc[0]),
                                            alarms, int(frame.n_val.iloc[0]))
        logger.info(
            f"[control c] Concept under scale drift {det}/{int(frame.n_drift.iloc[0])} streams "
            f"vs {alarms}/{int(frame.n_val.iloc[0])} under H_0: difference {diff:+d} streams, "
            f"Fisher exact p = {p_value:.4f}")
        logger.info(
            "[control c] the thirteen Gamma rows carry ONE measurement, not thirteen: the sign "
            "stream is a function of z alone, independent of beta and of the scale factor, so "
            "constancy across Gamma is an identity of the design and not an empirical finding. "
            "The comparison above is between disjoint seed blocks and does carry information.")

    # (d) Abrupt linearity. Slope, intercept, R^2 and the largest relative
    # residual are reported; 23.7 and 38 are estimates to classify, never
    # assertions.
    valid = frame.dropna(subset=["ADD_Data"])
    slope, intercept = np.polyfit(valid.Gamma, valid.ADD_Data, 1)
    fitted = slope * valid.Gamma + intercept
    ss_res = float(((valid.ADD_Data - fitted) ** 2).sum())
    ss_tot = float(((valid.ADD_Data - valid.ADD_Data.mean()) ** 2).sum())
    r_squared = 1.0 - ss_res / ss_tot
    max_rel = float((abs(valid.ADD_Data - fitted) / valid.ADD_Data).max())
    worst = valid.loc[(abs(valid.ADD_Data - fitted) / valid.ADD_Data).idxmax(), "Gamma"]

    # The same fit excluding the i.i.d. point. Gamma = 1 is the only row where
    # alpha = beta = 0, so it is the one row the GARCH delay-inflation argument
    # does not describe, and the intercept is anchored on it. Reported so a
    # reader can see which numeral rests on which sample; NOT substituted for
    # the all-points fit, which is what v87 prints.
    ex_iid = valid[valid.Gamma > 1.0 + 1e-9]
    slope_ex, intercept_ex = np.polyfit(ex_iid.Gamma, ex_iid.ADD_Data, 1)
    fitted_ex = slope_ex * ex_iid.Gamma + intercept_ex
    r_squared_ex = 1.0 - float(((ex_iid.ADD_Data - fitted_ex) ** 2).sum()) / float(
        ((ex_iid.ADD_Data - ex_iid.ADD_Data.mean()) ** 2).sum())
    max_rel_ex = float((abs(ex_iid.ADD_Data - fitted_ex) / ex_iid.ADD_Data).max())

    logger.info(
        f"[control d] all points: ADD = {slope:.4f} Gamma + {intercept:.4f}, "
        f"R^2 = {r_squared:.6f}, max relative residual {100*max_rel:.1f}% at Gamma = {worst:.2f}")
    logger.info(
        f"[control d] excluding Gamma = 1: ADD = {slope_ex:.4f} Gamma + {intercept_ex:.4f}, "
        f"R^2 = {r_squared_ex:.6f}, max relative residual {100*max_rel_ex:.1f}%")
    logger.info(
        f"[control d] the slope moves {100*abs(slope_ex/slope - 1):.1f}% and the intercept "
        f"{100*abs(intercept_ex/intercept - 1):.1f}% between the two fits. v87 prints the "
        f"all-points fit; the alternative is reported, not adopted.")

    # Positive control: the instrument must be shown responsive.
    row = positive.iloc[0]
    if row.DetRate_Concept <= row.FPR_Concept_val:
        failures.append(
            f"[positive control] Concept detection under a pure location shift is "
            f"{row.DetRate_Concept:.4f}, not above its own false-alarm rate "
            f"{row.FPR_Concept_val:.4f}. The monitor is not responsive, so its blindness to a "
            f"scale pathology is uninterpretable.")
    elif row.fisher_p_value >= 0.05:
        failures.append(
            f"[positive control] Concept detection {row.n_detected}/{int(row.n_streams)} under a "
            f"location shift is not resolved from {int(row.n_alarm_Concept_null)}/"
            f"{int(row.n_streams)} under H_0 (Fisher p = {row.fisher_p_value:.4f}).")
    logger.info(
        f"[positive control] location shift c = {row.c} at Gamma = {row.Gamma:.2f}: Concept "
        f"detects {row.n_detected}/{int(row.n_streams)} ({row.DetRate_Concept:.4f}, Wilson "
        f"[{row.DetRate_Concept_CI_low:.4f}, {row.DetRate_Concept_CI_high:.4f}]) against "
        f"{int(row.n_alarm_Concept_null)}/{int(row.n_streams)} under H_0, "
        f"{row.excess_streams:+d} streams, Fisher p = {row.fisher_p_value:.3g}, "
        f"conditional delay {row.ADD_Concept:.1f} steps")

    # Diagnostic arm: the price of the v87 numeral, reported and never gated.
    logger.info(
        f"[diagnostic] literal lambda_C = {LAMBDA_C_LITERAL}: hold-out FPR "
        f"{frame.FPR_Concept_literal.iloc[0]:.4f} and detection "
        f"{frame.DetRate_Concept_literal.iloc[0]:.4f} under the scale pathology, against "
        f"{frame.FPR_Concept_val.iloc[0]:.4f} / {frame.DetRate_Concept.iloc[0]:.4f} on the "
        f"calibrated reference arm. The numeral 10 of v87 sec:scaling_validation matches no "
        f"campaign of the study; this row prices the difference.")

    return failures, dict(slope=slope, intercept=intercept, r_squared=r_squared,
                          max_rel_residual=max_rel,
                          slope_ex_iid=slope_ex, intercept_ex_iid=intercept_ex,
                          r_squared_ex_iid=r_squared_ex, max_rel_residual_ex_iid=max_rel_ex)


def make_logger(fast, n_jobs):
    """Builds this stage's logger. Step c calls it so each stage keeps its own log file."""
    suffix = "_fast" if fast else ""
    logs_dir = BASE_DIR / "logs" / "R05_scale_law"
    logs_dir.mkdir(parents=True, exist_ok=True)
    name = f"exp_R05_scale_law_a{suffix}"
    logger = setup_logging(logs_dir / f"{name}.log", name)
    if not verify_hash_seed(logger):
        sys.exit(1)
    log_environment(logger, ["numpy", "pandas", "scipy"])
    logger.info(f"Deterministic reduction: ProcessPoolExecutor with max_workers = {n_jobs}, "
                f"executor.map in submission order; as_completed is not used (SPECS 1.5).")
    if fast:
        logger.warning("--fast: degraded smoke path. Not a certifiable run.")
    return logger


def run_stage(executor, logger, fast=False):
    """
    Runs the whole of step a on a caller-supplied executor and returns its
    frames in memory, having written its own CSV deliverables.

    Step c calls this rather than re-reading the CSVs, so no disk artefact ever
    acts as a bridge between stages (SPECS 1.6).
    """
    suffix = "_fast" if fast else ""
    n_calib = 40 if fast else N_CALIB
    n_val = 40 if fast else N_VAL
    n_drift = 40 if fast else N_DRIFT

    data_dir = BASE_DIR / "results" / "R05_scale_law" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    frame, positive = run_abrupt(executor, logger, n_calib, n_val, n_drift)
    failures, fit = certify(frame, positive, logger)

    grid_path = data_dir / f"R05_abrupt_add_vs_gamma{suffix}.csv"
    control_path = data_dir / f"R05_concept_positive_control{suffix}.csv"
    save_fair_csv(frame, grid_path)
    save_fair_csv(positive, control_path)
    logger.info(f"Wrote {grid_path.relative_to(BASE_DIR)} ({len(frame)} rows)")
    logger.info(f"Wrote {control_path.relative_to(BASE_DIR)} ({len(positive)} rows)")
    logger.info(f"Step a elapsed: {time.time() - started:.1f} s")

    if failures and not fast:
        for message in failures:
            logger.error(message)
        sys.exit(1)
    if failures:
        for message in failures:
            logger.warning("--fast, control not binding: %s", message)
    return frame, positive, fit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true",
                        help="Degraded smoke path: fewer streams, certification relaxed, outputs stamped '_fast'")
    parser.add_argument("--n-jobs", type=int, default=os.cpu_count(),
                        help="Worker processes. Outputs do not depend on this value: every task carries its own seed.")
    args = parser.parse_args()

    logger = make_logger(args.fast, args.n_jobs)
    with ProcessPoolExecutor(max_workers=args.n_jobs) as executor:
        return run_stage(executor, logger, fast=args.fast)


if __name__ == "__main__":
    main()
