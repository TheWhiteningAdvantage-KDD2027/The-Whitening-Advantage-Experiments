#!/usr/bin/env python3
"""
==========================================================================
R05b -- GRADUAL SCALE RAMPS: THE TWO-REGIME SCALING LAW (FIGURE 5B, APPENDIX B)
==========================================================================
Sweeps the width w of a gradual scale ramp across five GARCH penalties, every
arm calibrated to its own 5% null quantile and ALL penalties monitored over one
common horizon, and tests Eq. (5) of v87 (Theorem thm:scaling) with no fitted
constant.

Two budgets are run and both are kept. v87 sec:scaling_validation states that
the recalibration margin "degrades with the monitoring horizon", and that
statement rests precisely on the comparison of the two:
  --budget 2e5  the main campaign, H = 200,000, the source of Figure 5B
  --budget 3e6  the boundary campaign, H = 3,000,000, Appendix B's
                "where the recalibration rule stops holding"

Why one common horizon. lambda_star is a quantile of the running maximum of a
CUSUM over H steps, so it grows with H. Monitoring different penalties over
different horizons would make their thresholds incomparable in level, and the
rule lambda_iid x Gamma -- which is a statement about levels -- would not be
measurable at all. The horizon is therefore solved once, as a fixed point, and
shared.

Two crossover widths coexist in this design and they are NOT the same quantity.
The submitted pipeline used one of them to label the regime column of its CSV
and the other to fit the published exponents, and the two disagree by the
recalibration margin:

  w_star_predicted = 2 lambda_iid_H Gamma / [Delta_mu_max (1-rho)^2]
      the crossover Theorem thm:scaling predicts, from the recalibration rule.
  w_delta_applied  = 2 lambda_star_Data / [Delta_mu_max (1-rho)^2]
      the crossover at the threshold the detector actually ran with.

Appendix B's measured exponents (0.65-0.71) and Figure 5B's model curves are
both computed on w_delta_applied. This script emits both columns under names
that cannot be confused, and fits the ramp branch on w_delta_applied, which is
what the manuscript prints.

Notations: as in exp_R05_scale_law_a.py, plus
- w            : width of the gradual ramp, in steps.
- v_max        : terminal variance multiplier of the ramp, solved per Gamma so
                 the standardized shift reaches Delta_mu_max.
- rho          : dead-band fraction delta_P / Delta_mu_max.
- mon_len      : common monitoring horizon, identical across Gamma at a budget.
- lambda_iid_H : the i.i.d. threshold at the common horizon, Gamma = 1.

References:
- Page, E. S. (1954). Continuous inspection schemes. Biometrika, 41(1/2), 100-115.
- Siegmund, D. (1985). Sequential Analysis. Springer.
- Francq, C. & Zakoian, J.-M. (2010). GARCH Models. Wiley.
==========================================================================
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

import os

from experiments.common.fair_env import (
    _THREAD_VARIABLES, enforce_strict_determinism, verify_hash_seed, log_environment,
)

# Entry point when run alone, library when step c drives the chain. As in step
# a, only the entry point may post the environment block: once NumPy is loaded
# the BLAS thread limits have been read and a second assignment is inert, so an
# imported module verifies instead of re-posting, and refuses to load if the
# block is absent rather than running degraded (preamble S4.3).
if "numpy" in sys.modules:
    _unpinned = [name for name in _THREAD_VARIABLES if os.environ.get(name) != "1"]
    if os.environ.get("MKL_CBWR") != "COMPATIBLE":
        _unpinned.append("MKL_CBWR")
    if _unpinned:
        raise RuntimeError(
            f"exp_R05_scale_law_b was imported after NumPy was loaded, but the determinism "
            f"block is not in place: {_unpinned}. The importing module must call "
            f"enforce_strict_determinism() before importing numpy, pandas or scipy."
        )
else:
    enforce_strict_determinism()

import numpy as np
import pandas as pd
from experiments.common.fair_harness import setup_logging, disable_pandas_multithreading, save_fair_csv, log_artifact_manifest

disable_pandas_multithreading()

import math
import time
import argparse
from concurrent.futures import ProcessPoolExecutor

import scipy.stats as stats

from experiments.R05_scale_law.exp_R05_scale_law_a import (
    NU, ALPHA_GARCH, DMU_TARGET, DELTA_P, DELTA_C, TARGET_FPR, WARMUP,
    N_CALIB, N_VAL, N_DRIFT, LAMBDA_C_LITERAL, CONCEPT_VACUITY_BAND,
    seed_for, make_rng, gamma_closed, solve_beta, gen_eps,
    cusum1_firstpass, cusum2_maxexc, cusum2_firstpass, wilson_interval,
)

# Dead-band fraction of Theorem thm:scaling. rho = delta_P / Delta_mu_max.
RHO = DELTA_P / DMU_TARGET

GAMMA_LIST = (2.0, 4.0, 8.0, 11.58, 20.0)

# Budget definitions. R_MAX and N_R are the reach and resolution of the grid in
# units of W0 = 2 lambda_iid_H Gamma / Delta_mu_max, the crossover WITHOUT the
# dead-band factor. The published crossover is w* = W0/(1-rho)^2, so a reach of
# 40 W0 is 22.5 w* and 400 W0 is 225 w* -- the two figures Appendix B prints.
BUDGETS = {
    "2e5": dict(mon_len_min=20000, mon_len_cap=200000, r_max=40.0, n_r=12),
    "3e6": dict(mon_len_min=20000, mon_len_cap=3000000, r_max=400.0, n_r=17),
}
SAFETY = 8.0

# Horizons of the lambda_iid ladder. v87 app:scaling states the i.i.d. threshold
# grows 102.8 -> 129.5 -> 303.0 over these three, i.e. as H^0.24-H^0.31 rather
# than the log H of Siegmund's ARL_0 formula. Only the last two are produced by
# the campaigns; the first is not produced by any script of the submitted study
# and survives only as a comment in Priorite_18b. The ladder regenerates all
# three from one nested set of trajectories.
LADDER_HORIZONS = (77000, 200000, 3000000)


def cusum1_max_at_checkpoints(x, delta, checkpoints):
    """
    Running maximum of the one-sided CUSUM, sampled at a sorted list of prefix
    lengths, in a single pass.

    Sampling one trajectory at several prefixes rather than drawing one
    trajectory per horizon is what makes the horizons NESTED by construction:
    the value at the shorter horizon is the running maximum over a prefix of the
    very path that produces the longer one. Monotonicity in H is then an
    identity of the recursion rather than a property to hope for, and the
    comparison across horizons carries no draw noise at all.
    """
    S = 0.0
    mx = 0.0
    out = []
    ci = 0
    n_check = len(checkpoints)
    for i, v in enumerate(x):
        S += v - delta
        if S < 0.0:
            S = 0.0
        elif S > mx:
            mx = S
        while ci < n_check and (i + 1) == checkpoints[ci]:
            out.append(mx)
            ci += 1
    while ci < n_check:
        out.append(mx)
        ci += 1
    return out


def _worker_null_ramp(args):
    """One stream under H_0 at the common horizon."""
    index, alpha, beta, mon_len = args
    rng = make_rng(seed_for("null", index))
    eps = gen_eps(WARMUP + mon_len, alpha, beta, NU, rng)
    eps2 = eps * eps
    mu = float(eps2[:WARMUP].mean())
    sig = float(eps2[:WARMUP].std(ddof=1))
    e_data = ((eps2[WARMUP:] - mu) / sig).tolist()
    m_sign = ((eps[WARMUP:] > 0.0).astype(float) - 0.5).tolist()
    max_data = cusum1_max_at_checkpoints(e_data, DELTA_P, (mon_len,))[0]
    return mu, sig, max_data, cusum2_maxexc(m_sign, DELTA_C)


def _worker_iid_ladder(args):
    """
    One i.i.d. stream (Gamma = 1, alpha = beta = 0) carried to the longest
    horizon, with the Data running maximum read off at every checkpoint.
    """
    index, checkpoints = args
    rng = make_rng(seed_for("iid", index))
    eps = gen_eps(WARMUP + max(checkpoints), 0.0, 0.0, NU, rng)
    eps2 = eps * eps
    mu = float(eps2[:WARMUP].mean())
    sig = float(eps2[:WARMUP].std(ddof=1))
    e_data = ((eps2[WARMUP:] - mu) / sig).tolist()
    return cusum1_max_at_checkpoints(e_data, DELTA_P, checkpoints)


def _worker_ramp_drift(args):
    """
    One stream carrying the gradual scale ramp. The variance multiplier climbs
    linearly from 1 to v_max over w steps and then holds.

    As in the abrupt case, the sign stream is untouched by a positive variance
    multiplier, and the assertion states it rather than assuming it.
    """
    index, alpha, beta, v_max, w, mon_len, thr_data, thr_concept = args
    rng = make_rng(seed_for("drift", index))
    eps = gen_eps(WARMUP + mon_len, alpha, beta, NU, rng)
    eps2 = eps * eps
    mu = float(eps2[:WARMUP].mean())
    sig = float(eps2[:WARMUP].std(ddof=1))

    monitored = eps[WARMUP:]
    tau = np.arange(mon_len, dtype=float)
    v = 1.0 + (v_max - 1.0) * np.minimum(tau / w, 1.0)

    sign_undrifted = (monitored > 0.0).astype(float) - 0.5
    if not np.array_equal(sign_undrifted, ((monitored * np.sqrt(v)) > 0.0).astype(float) - 0.5):
        raise AssertionError(
            f"Ramp pathology altered the sign stream at replicate {index}: a positive variance "
            f"multiplier cannot change a sign, so the Concept branch has been fed the drifted "
            f"series.")

    mon2 = eps2[WARMUP:] * v
    e_data = ((mon2 - mu) / sig).tolist()
    m_sign = sign_undrifted.tolist()
    del eps, eps2, tau, v, mon2, monitored, sign_undrifted
    return (cusum1_firstpass(e_data, DELTA_P, thr_data),
            cusum2_firstpass(m_sign, DELTA_C, thr_concept),
            cusum2_firstpass(m_sign, DELTA_C, LAMBDA_C_LITERAL))


def solve_common_horizon(executor, logger, budget, n_calib):
    """
    Solves the common monitoring horizon as a fixed point, and reports the
    margin it actually achieves.

    lambda_iid depends on the horizon, and the horizon required to keep the
    widest ramps uncensored depends on lambda_iid through the w grid. Solving
    in one pass would size the horizon on a lambda_iid measured at the seed
    horizon while building the grid on a lambda_iid measured at the final one.

    The submitted script printed SAFETY as if it had been achieved, using a
    prediction computed before the last threshold update, and did not say when
    the cap had bound. Both are corrected here: the realised margin is
    recomputed at the final threshold, and clamping is reported.
    """
    spec = BUDGETS[budget]
    r_grid = np.logspace(np.log10(0.15), np.log10(spec["r_max"]), spec["n_r"])
    max_gamma = max(GAMMA_LIST)

    def lambda_iid_at(horizon):
        results = list(executor.map(_worker_iid_ladder,
                                    [(i, (horizon,)) for i in range(n_calib)],
                                    chunksize=4))
        return float(np.quantile(np.array([r[0] for r in results]), 1.0 - TARGET_FPR))

    horizon = spec["mon_len_min"]
    lam_iid = lambda_iid_at(horizon)
    clamped = False
    for _ in range(3):
        w_max = float(max(r_grid)) * 2.0 * lam_iid * max_gamma / DMU_TARGET
        predicted = math.sqrt(2.0 * lam_iid * max_gamma * w_max / DMU_TARGET) + RHO * w_max
        wanted = SAFETY * predicted
        proposed = int(min(spec["mon_len_cap"], max(spec["mon_len_min"], wanted)))
        clamped = wanted > spec["mon_len_cap"]
        if proposed <= horizon:
            break
        horizon = proposed
        lam_iid = lambda_iid_at(horizon)

    # Realised margin, recomputed at the threshold the campaign will actually
    # use rather than at the one the last iteration started from.
    w_max_final = float(max(r_grid)) * 2.0 * lam_iid * max_gamma / DMU_TARGET
    predicted_final = math.sqrt(2.0 * lam_iid * max_gamma * w_max_final / DMU_TARGET) + RHO * w_max_final
    realised_margin = horizon / predicted_final

    logger.info(
        f"[horizon] common monitoring horizon H = {horizon} (fixed point), "
        f"lambda_iid_H = {lam_iid:.4f}")
    if clamped:
        logger.info(
            f"[horizon] the cap of {spec['mon_len_cap']} bound: the fixed point wanted "
            f"{int(wanted)} steps to reach the SAFETY target of {SAFETY:.0f}x the deterministic "
            f"prediction at the widest ramp. SAFETY is a design target this budget does NOT "
            f"reach; the realised margin is {realised_margin:.2f}x. Censoring is measured "
            f"directly per cell and is the quantity that decides admissibility.")
    else:
        logger.info(f"[horizon] realised margin {realised_margin:.2f}x the deterministic "
                    f"prediction at the widest ramp (SAFETY target {SAFETY:.0f}x, not clamped).")
    return horizon, lam_iid, r_grid, realised_margin, clamped


def run_ladder(executor, logger, n_calib):
    """
    Regenerates lambda_iid at the three horizons of v87 app:scaling from ONE
    nested set of i.i.d. trajectories.
    """
    checkpoints = tuple(sorted(LADDER_HORIZONS))
    results = list(executor.map(_worker_iid_ladder,
                                [(i, checkpoints) for i in range(n_calib)],
                                chunksize=4))
    matrix = np.array(results, dtype=float)

    # Nesting is an identity of the single-pass recursion, not a hypothesis.
    # Asserted because an indexing error in the checkpoint sampler would break
    # it silently, and because the whole ladder rests on it.
    if not np.all(np.diff(matrix, axis=1) >= 0.0):
        raise AssertionError(
            "The running CUSUM maximum decreased with the horizon on at least one stream. "
            "The three horizons are prefixes of one trajectory, so this is impossible unless "
            "the checkpoint sampler is mis-indexed.")

    rows = []
    for column, horizon in enumerate(checkpoints):
        lam = float(np.quantile(matrix[:, column], 1.0 - TARGET_FPR))
        rows.append(dict(H=horizon, Gamma=1.0, alpha=0.0, beta=0.0, n_streams=n_calib,
                         delta_P=DELTA_P, target_fpr=TARGET_FPR, lambda_iid_H=lam))
    frame = pd.DataFrame(rows)

    exponent = float(np.polyfit(np.log(frame.H), np.log(frame.lambda_iid_H), 1)[0])
    frame["loglog_exponent_over_ladder"] = exponent

    logger.info("[ladder] lambda_iid by horizon, from one nested set of trajectories:")
    for _, row in frame.iterrows():
        logger.info(f"[ladder]   H = {int(row.H):>9d}  lambda_iid = {row.lambda_iid_H:.4f}")
    logger.info(
        f"[ladder] log-log slope over the three horizons: {exponent:.4f}. This is a descriptive "
        f"slope through three perfectly dependent measurements -- the same 400 trajectories read "
        f"at three prefixes -- so it carries no standard error and none is emitted. Siegmund's "
        f"ARL_0 formula would give a growth in log H, whose Cramer condition squared innovations "
        f"do not satisfy.")
    return frame


def run_campaign(executor, logger, budget, n_calib, n_val, n_drift):
    """Runs one ramp campaign at one budget and returns the frame in memory."""
    horizon, lam_iid, r_grid, realised_margin, clamped = solve_common_horizon(
        executor, logger, budget, n_calib)

    rows = []
    for gamma_target in GAMMA_LIST:
        beta = solve_beta(gamma_target, ALPHA_GARCH)
        gamma = gamma_closed(ALPHA_GARCH, beta)

        # The absolute grid is anchored on W0, the crossover without the dead
        # band, preserving continuity with the submitted campaigns. The regime
        # labels and the ramp fit use w* and w_delta, which include it.
        w0 = 2.0 * lam_iid * gamma / DMU_TARGET
        w_grid = sorted(set(int(round(r * w0)) for r in r_grid if r * w0 >= 10))

        null = list(executor.map(_worker_null_ramp,
                                 [(i, ALPHA_GARCH, beta, horizon) for i in range(n_calib + n_val)],
                                 chunksize=4))
        mus = np.array([r[0] for r in null])
        sigs = np.array([r[1] for r in null])
        max_data = np.array([r[2] for r in null])
        max_concept = np.array([r[3] for r in null])

        pop_mu, pop_sig = mus.mean(), sigs.mean()
        v_max = 1.0 + DMU_TARGET * pop_sig / pop_mu
        s_max = math.sqrt(v_max)

        lam_data = float(np.quantile(max_data[:n_calib], 1.0 - TARGET_FPR))
        lam_concept = float(np.quantile(max_concept[:n_calib], 1.0 - TARGET_FPR))
        hold_data = max_data[n_calib:]
        hold_concept = max_concept[n_calib:]
        fpr_data = float((hold_data > lam_data).mean())
        fpr_concept = float((hold_concept > lam_concept).mean())
        fpr_concept_literal = float((hold_concept > LAMBDA_C_LITERAL).mean())
        n_alarm_data_null = int((hold_data > lam_data).sum())
        n_alarm_concept_null = int((hold_concept > lam_concept).sum())

        w_star_predicted = w0 / (1.0 - RHO) ** 2
        w_delta_applied = (2.0 * lam_data / DMU_TARGET) / (1.0 - RHO) ** 2

        logger.info(
            f"[Gamma={gamma:6.3f}] beta={beta:.6f} v_max={v_max:.4f} "
            f"lambda*_Data={lam_data:10.3f} (lambda*/Gamma={lam_data/gamma:8.3f}, "
            f"{100*(lam_data/gamma/lam_iid - 1):+6.2f}% on the x Gamma rule) "
            f"w*_predicted={w_star_predicted:9.1f} w_delta_applied={w_delta_applied:9.1f} "
            f"w in [{min(w_grid)}, {max(w_grid)}] n_w={len(w_grid)}")

        for w in w_grid:
            drift = list(executor.map(
                _worker_ramp_drift,
                [(i, ALPHA_GARCH, beta, v_max, w, horizon, lam_data, lam_concept)
                 for i in range(n_drift)],
                chunksize=4))
            add_data = np.array([r[0] for r in drift], dtype=float)
            add_concept = np.array([r[1] for r in drift], dtype=float)
            add_concept_literal = np.array([r[2] for r in drift], dtype=float)
            det_data = add_data >= 0
            det_concept = add_concept >= 0

            if det_data.any():
                sel = add_data[det_data]
                add_d = float(sel.mean())
                med_d = float(np.median(sel))
                sem_d = float(sel.std(ddof=1) / math.sqrt(det_data.sum())) if det_data.sum() > 1 else float('nan')
            else:
                add_d = med_d = sem_d = float('nan')
            if det_concept.any():
                sel_c = add_concept[det_concept]
                add_c = float(sel_c.mean())
                med_c = float(np.median(sel_c))
                sem_c = float(sel_c.std(ddof=1) / math.sqrt(det_concept.sum())) if det_concept.sum() > 1 else float('nan')
            else:
                add_c = med_c = sem_c = float('nan')

            rows.append(dict(
                w=w, Gamma=gamma, alpha=ALPHA_GARCH, beta=beta, s_max=s_max, v_max=v_max,
                dmu_std_target=DMU_TARGET, delta_P=DELTA_P, delta_C=DELTA_C, rho=RHO,
                budget=budget, mon_len=horizon, warmup=WARMUP,
                n_calib=n_calib, n_val=n_val, n_drift=n_drift,
                lambda_star_Data=lam_data, lambda_star_Concept=lam_concept,
                lambda_C_literal=LAMBDA_C_LITERAL, lambda_iid_H=lam_iid,
                w_star_predicted=w_star_predicted, w_over_wstar_predicted=w / w_star_predicted,
                regime_predicted=("ramp" if w >= w_star_predicted else "saturated"),
                w_delta_applied=w_delta_applied, w_over_wdelta_applied=w / w_delta_applied,
                regime_applied=("ramp" if w >= w_delta_applied else "saturated"),
                FPR_Data_val=fpr_data, FPR_Concept_val=fpr_concept,
                FPR_Concept_literal=fpr_concept_literal,
                n_alarm_Data_null=n_alarm_data_null, n_alarm_Concept_null=n_alarm_concept_null,
                censored_Data=float((~det_data).mean()),
                DetRate_Data=float(det_data.mean()),
                ADD_Data=add_d, MED_Data=med_d, SEM_Data=sem_d,
                DetRate_Concept=float(det_concept.mean()),
                ADD_Concept=add_c, MED_Concept=med_c, SEM_Concept=sem_c,
                DetRate_Concept_literal=float((add_concept_literal >= 0).mean()),
                n_detected_Concept=int(det_concept.sum()),
            ))

        subset = pd.DataFrame([r for r in rows if r["Gamma"] == gamma])
        ramp_applied = subset[(subset.regime_applied == "ramp") & subset.ADD_Data.notna()]
        ramp_predicted = subset[(subset.regime_predicted == "ramp") & subset.ADD_Data.notna()]
        slope_applied = (float(np.polyfit(np.log(ramp_applied.w), np.log(ramp_applied.ADD_Data), 1)[0])
                         if len(ramp_applied) >= 2 else float('nan'))
        slope_predicted = (float(np.polyfit(np.log(ramp_predicted.w), np.log(ramp_predicted.ADD_Data), 1)[0])
                           if len(ramp_predicted) >= 2 else float('nan'))
        logger.info(
            f"[Gamma={gamma:6.3f}] ramp exponent {slope_applied:.3f} on w >= w_delta_applied "
            f"(n={len(ramp_applied)}) against {slope_predicted:.3f} on w >= w*_predicted "
            f"(n={len(ramp_predicted)}); v87 app:scaling prints the former. "
            f"DetRate_Data in [{subset.DetRate_Data.min():.4f}, {subset.DetRate_Data.max():.4f}], "
            f"censoring max {subset.censored_Data.max():.4f}, "
            f"Concept hold-out FPR {fpr_concept:.4f} vs detection "
            f"[{subset.DetRate_Concept.min():.4f}, {subset.DetRate_Concept.max():.4f}]")

    frame = pd.DataFrame(rows)
    frame["realised_horizon_margin"] = realised_margin
    frame["horizon_cap_bound"] = clamped
    return frame


def certify(frame, logger, budget):
    """Blocking controls (b), (f) and (h) of the R05 prompt for one budget."""
    failures = []
    n_val = int(frame.n_val.iloc[0])

    # (b) Common horizon, in two parts. The design half is an assertion on
    # mon_len; the consequence half tests what v87 actually claims the common
    # horizon buys -- that the null crossing probability is identical across
    # Gamma -- on the realised levels.
    horizons = frame.mon_len.nunique()
    if horizons != 1:
        failures.append(
            f"mon_len takes {horizons} distinct values at budget {budget}. v87 requires all "
            f"penalties monitored over one common horizon; without it the thresholds are not "
            f"comparable in level and no comparison across Gamma is interpretable.")

    per_gamma = frame.groupby("Gamma").agg(
        alarms=("n_alarm_Data_null", "first"), fpr=("FPR_Data_val", "first")).reset_index()
    counts = per_gamma.alarms.to_numpy(dtype=int)
    table = np.array([counts, np.full(len(counts), n_val) - counts])
    chi2, p_homog, dof, _ = stats.chi2_contingency(table, correction=False)
    pooled = float(counts.sum()) / float(len(counts) * n_val)
    pooled_low, pooled_high = wilson_interval(int(counts.sum()), len(counts) * n_val)
    logger.info(
        f"[control b] mon_len constant at {int(frame.mon_len.iloc[0])} across the "
        f"{len(per_gamma)} penalties.")
    logger.info(
        f"[control b] realised null levels {list(np.round(per_gamma.fpr.to_numpy(), 4))} "
        f"({list(counts)} alarms of {n_val}); chi-square homogeneity {chi2:.2f} on {dof} dof, "
        f"p = {p_homog:.3f}.")
    logger.info(
        f"[control b] pooled realised level {pooled:.4f}, Wilson [{pooled_low:.4f}, "
        f"{pooled_high:.4f}], against the {TARGET_FPR:.2f} v87 states for every Data arm. "
        f"Target {'inside' if pooled_low <= TARGET_FPR <= pooled_high else 'OUTSIDE'} the interval.")

    # (h) Multiple testing. The family-wise probability is computed and logged
    # BEFORE the result is read, per preamble S4bis, and no per-cell gate is
    # used. The calibration of the per-cell levels is tested as a distribution.
    m = len(per_gamma)
    family_wise = 1.0 - (1.0 - TARGET_FPR) ** m
    logger.info(
        f"[control h] {m} simultaneous cells at a {TARGET_FPR:.2f} level: the probability of at "
        f"least one rejection under the null of correct calibration is "
        f"1 - (1 - {TARGET_FPR})^{m} = {family_wise:.3f}. Above 5%, so no per-cell binary gate "
        f"is used; the levels are tested as a distribution instead.")
    p_values = np.array([
        float(stats.binomtest(int(k), n_val, TARGET_FPR, alternative='two-sided').pvalue)
        for k in counts])
    ks_stat, ks_p = stats.kstest(p_values, 'uniform')
    logger.info(
        f"[control h] per-cell two-sided binomial p-values {list(np.round(p_values, 4))}; "
        f"Kolmogorov-Smirnov against Uniform(0,1): D = {ks_stat:.4f}, p = {ks_p:.4f}. "
        f"Descriptive, retained in the CSV, and not an acceptance criterion.")

    # (f) The recalibration margin, the quantity Appendix B prices.
    margins = 100.0 * (per_gamma.Gamma.map(
        lambda g: float(frame[frame.Gamma == g].lambda_star_Data.iloc[0]) / g
    ) / float(frame.lambda_iid_H.iloc[0]) - 1.0)
    logger.info(
        f"[control f] budget {budget}: lambda*(Gamma)/Gamma = "
        f"{[round(float(frame[frame.Gamma == g].lambda_star_Data.iloc[0]) / g, 1) for g in per_gamma.Gamma]} "
        f"against lambda_iid_H = {frame.lambda_iid_H.iloc[0]:.2f}; departure from the "
        f"lambda_iid x Gamma rule {margins.min():+.1f}% to {margins.max():+.1f}%.")

    # Orthogonality vacuity guard on the reference arm.
    fpr_concept = float(frame.FPR_Concept_val.iloc[0])
    lo, hi = CONCEPT_VACUITY_BAND
    if not (lo <= fpr_concept <= hi):
        failures.append(
            f"[vacuity] Concept hold-out FPR is {fpr_concept:.4f} at budget {budget}, outside "
            f"{CONCEPT_VACUITY_BAND}. The equality DetRate == FPR is uninformative there.")
    else:
        logger.info(
            f"[control c] Concept hold-out FPR {fpr_concept:.4f}, detection under the ramp in "
            f"[{frame.DetRate_Concept.min():.4f}, {frame.DetRate_Concept.max():.4f}] across all "
            f"{len(frame)} cells. The sign stream does not see the pathology, so this equality "
            f"is an identity of the design; the positive control of step a is what shows the "
            f"instrument responsive.")

    logger.info(
        f"[diagnostic] literal lambda_C = {LAMBDA_C_LITERAL} at H = {int(frame.mon_len.iloc[0])}: "
        f"hold-out FPR {frame.FPR_Concept_literal.iloc[0]:.4f}, detection under the ramp in "
        f"[{frame.DetRate_Concept_literal.min():.4f}, {frame.DetRate_Concept_literal.max():.4f}]. "
        f"A threshold fixed at 10 is far below the running maximum of a CUSUM over this horizon, "
        f"so the arm saturates; that is the price of the v87 numeral at this budget.")

    return failures


def apply_fast_profile():
    """
    Shrinks both budgets and the ladder to a smoke-test scale.

    Kept in one place and applied by whichever entry point is running, so the
    degraded path can never be half-applied. It is stamped into every output
    file name, per preamble S4.3: a degraded run must be identifiable from its
    artefacts alone.
    """
    global LADDER_HORIZONS
    # The reach in units of W0 is kept at the published 40 and 400 so the smoke
    # path still exercises both the saturated and the ramp branch, and so the
    # ramp fits are populated rather than NaN. Only the stream count and the
    # horizon cap are cut, which is what makes it fast.
    BUDGETS["2e5"] = dict(mon_len_min=5000, mon_len_cap=20000, r_max=40.0, n_r=12)
    BUDGETS["3e6"] = dict(mon_len_min=5000, mon_len_cap=80000, r_max=400.0, n_r=17)
    LADDER_HORIZONS = (5000, 20000, 80000)


def make_logger(budget, fast, n_jobs):
    """Builds this stage's logger. Step c calls it so each budget keeps its own log file."""
    suffix = "_fast" if fast else ""
    logs_dir = BASE_DIR / "logs" / "R05_scale_law"
    logs_dir.mkdir(parents=True, exist_ok=True)
    name = f"exp_R05_scale_law_b_{budget}{suffix}"
    logger = setup_logging(logs_dir / f"{name}.log", name)
    if not verify_hash_seed(logger):
        sys.exit(1)
    log_environment(logger, ["numpy", "pandas", "scipy"])
    logger.info(f"Budget {budget}: cap {BUDGETS[budget]['mon_len_cap']} steps, grid reach "
                f"{BUDGETS[budget]['r_max']:.0f} W0 on {BUDGETS[budget]['n_r']} points, "
                f"penalties {list(GAMMA_LIST)}.")
    logger.info(f"Deterministic reduction: ProcessPoolExecutor with max_workers = {n_jobs}, "
                f"executor.map in submission order; as_completed is not used (SPECS 1.5).")
    if fast:
        logger.warning("--fast: degraded smoke path. Not a certifiable run.")
    return logger


def run_stage(executor, logger, budget, ladder=False, fast=False):
    """
    Runs one budget of step b on a caller-supplied executor and returns
    (campaign frame, ladder frame or None) in memory.
    """
    suffix = "_fast" if fast else ""
    n_calib = 40 if fast else N_CALIB
    n_val = 40 if fast else N_VAL
    n_drift = 40 if fast else N_DRIFT

    data_dir = BASE_DIR / "results" / "R05_scale_law" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    frame = run_campaign(executor, logger, budget, n_calib, n_val, n_drift)
    ladder_frame = run_ladder(executor, logger, n_calib) if ladder else None
    failures = certify(frame, logger, budget)

    path = data_dir / f"R05_ramp_multigamma_{budget}{suffix}.csv"
    save_fair_csv(frame, path)
    logger.info(f"Wrote {path.relative_to(BASE_DIR)} ({len(frame)} rows)")
    artifacts = [path]

    if ladder_frame is not None:
        ladder_path = data_dir / f"R05_lambda_iid_horizon{suffix}.csv"
        save_fair_csv(ladder_frame, ladder_path)
        logger.info(f"Wrote {ladder_path.relative_to(BASE_DIR)} ({len(ladder_frame)} rows)")
        artifacts.append(ladder_path)
        campaign_lam = float(frame.lambda_iid_H.iloc[0])
        matching = ladder_frame[ladder_frame.H == int(frame.mon_len.iloc[0])]
        if len(matching) == 1:
            gap = abs(float(matching.lambda_iid_H.iloc[0]) - campaign_lam)
            logger.info(
                f"[ladder] cross-check at H = {int(frame.mon_len.iloc[0])}: ladder "
                f"{float(matching.lambda_iid_H.iloc[0]):.6f} against campaign {campaign_lam:.6f}, "
                f"absolute gap {gap:.3g}. Both read the same 'iid' seed block over the same "
                f"prefix, so the gap must be zero.")
            if gap != 0.0:
                failures.append(
                    f"Ladder and campaign disagree on lambda_iid at H = "
                    f"{int(frame.mon_len.iloc[0])}: {gap:.6g}. They share a seed block and a "
                    f"prefix, so any difference is a defect in one of the two paths.")
    
    log_artifact_manifest(logger, artifacts, data_dir, BASE_DIR)

    logger.info(f"Step b ({budget}) elapsed: {time.time() - started:.1f} s")

    if failures and not fast:
        for message in failures:
            logger.error(message)
        sys.exit(1)
    if failures:
        for message in failures:
            logger.warning("--fast, control not binding: %s", message)
    return frame, ladder_frame


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", choices=sorted(BUDGETS), default="2e5",
                        help="Monitoring-horizon budget. Both are published and both are kept.")
    parser.add_argument("--ladder", action="store_true",
                        help="Additionally regenerate the lambda_iid horizon ladder of app:scaling.")
    parser.add_argument("--fast", action="store_true",
                        help="Degraded smoke path: fewer streams and a shorter cap, outputs stamped '_fast'")
    parser.add_argument("--n-jobs", type=int, default=os.cpu_count())
    args = parser.parse_args()

    if args.fast:
        apply_fast_profile()
    logger = make_logger(args.budget, args.fast, args.n_jobs)
    with ProcessPoolExecutor(max_workers=args.n_jobs) as executor:
        return run_stage(executor, logger, args.budget, ladder=args.ladder, fast=args.fast)


if __name__ == "__main__":
    main()
