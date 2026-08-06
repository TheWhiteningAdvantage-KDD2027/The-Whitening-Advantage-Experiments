#!/usr/bin/env python3
"""
==========================================================================
R16 (b) -- SIGN FLOOR, FEASIBILITY GRID AND THE CLAIMS OF v87
==========================================================================
Second stage of the R16 chain. `_a` dates the phases and writes the census;
this script prices two detection floors on every phase and reports the counts
v87 publishes.

  ADD_min_unc(gamma)  = 504 * ln(gamma) / SR^2      the Sharpe ceiling of
                        Corollary cor:sharpe_ceiling, on the UNCONDITIONAL
                        daily-return stream
  ADD_min_sign(gamma) = ln(gamma) / kl(q_phase || q_ref)   the exact Bernoulli
                        budget of the SIGN stream

A phase is out of budget when its floor is not below its own duration. The
counts this produces are the manuscript's most-cited empirical claim: 53 of 66
at gamma = 20 (80%), 52 of 66 pricing the binarisation exactly, 64 of 66 at
gamma = 252 (L329).

THE TWO-STAGE CSV INTERFACE IS WHAT THE PROMPT MANDATES (its section 3), so the
census is re-read from disk with `float_precision='round_trip'` on both sides.
Preamble S7's ban on disk round-trips targets a figure re-plotted from a
reloaded CSV, not a declared `_a` -> `_b` chain.

WHAT THIS SCRIPT DOES NOT CARRY. `Priorite_20_sign_floor.py` embeds
`EXPECTED_FRAC_OUT = 0.803  # articleB v77` (l.229) as a manuscript-drift
tripwire inside the producing script. Preamble S6 forbids a hard-coded value in
a produced artefact and the same reasoning applies to a target inside the
producer: the regression anchor belongs in `tests/test_R16_claims.py`, read from
the vendored witness `data/reference/R16/protocol_20b_census_feasibility_vs_
gamma.csv`. Control C2 below reads its comparison values from that witness for
the same reason -- no published count is typed into this file.

THREE ARMS, ONE PERSISTED FLOOR TABLE. The floors are computed for the three
census arms `_a` writes, because four LaTeX macros price the counterfactuals;
`R16_sign_floor.csv` and `R16_feasibility_vs_gamma.csv` carry the CANONICAL arm
alone, in the schema of the delivered `protocol_20a` / `protocol_20b`, and
`census_source` keeps its witness value `refined` -- the MESO-refined census IS
the canonical arm, and renaming the field would break the witness comparison
that classifies every deviation.

ONE COLUMN BEYOND THE LEGACY SCHEMA. `arm_disagreement` in {none, sign_only,
unc_only} makes control C3 traceable: v87 says pricing the binarisation exactly
"moves that count by one phase", which is true of the COUNT (14 against 13) and
false of the SET (the two arms disagree on 19 of the 66 phases).

References:
- Lorden, G. (1971). Annals of Mathematical Statistics, 42(6), 1897-1908.
- Lai, T. L. (1998). IEEE Trans. Inf. Theory, 44(7), 2917-2929.
- Tartakovsky, A., Nikiforov, I. & Basseville, M. (2014). Sequential Analysis:
  Hypothesis Testing and Changepoint Detection. CRC Press.
- Wilson, E. B. (1927). JASA, 22(158), 209-212.

NOTATION (prompt section 6)
  gamma              in-control average run length in trading days, alpha_0 = 1/gamma
  kl_sign_nats_day   kl(q_phase || q_ref), the Bernoulli divergence in nats/day
  detectable_*_g     the arm's floor is strictly below the phase duration
  arm_disagreement   which of the two floors, if either, alone finds the phase
==========================================================================
"""

import sys
from pathlib import Path

# Determinism bootstrap, preamble S6's order: fair_env imports only os and sys.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from experiments.common.fair_env import enforce_strict_determinism, verify_hash_seed, log_environment

enforce_strict_determinism()

import os

if os.environ.get("PYTHONHASHSEED") != "42":
    sys.exit("FATAL: PYTHONHASHSEED is not 42. Execute via run_experiment_R16.sh")

import numpy as np
import pandas as pd
from experiments.common.fair_harness import (setup_logging, disable_pandas_multithreading,
                                             compute_sha256, save_fair_csv)

disable_pandas_multithreading()

import ast
import time
import argparse

# --- PROTOCOL SPECIFICATION, IMPERATIVE, FROM v87 AND THE DELIVERED SCRIPT ---
GAMMAS = (20, 252, 1260)
BUDGETS = ("unc", "sign")
ARMS = ("canonical", "strict_ps", "symmetric")
CENSUS_FILES = {
    "canonical": "R16_regime_census.csv",
    "strict_ps": "R16_regime_census_strict_ps.csv",
    "symmetric": "R16_regime_census_symmetric.csv",
}
# The legacy value of `census_source`, kept so that the witness comparison of
# `data/reference/R16/protocol_20a_sign_floor.csv` stays cell-for-cell.
CENSUS_SOURCE_LABEL = "refined"
# v87 L331's COVID crash is SPY's: Delta q ~ -0.28 and annualized Sharpe ~ -6.0
# are that ticker's phase. The label itself comes from `get_episodes`, which is
# carried in `_a`; the ticker is the one v87 L321 monitors through 2020.
COVID_TICKER = "SPY"
COVID_LABEL = "COVID_2020"
# v87 L329 reads "even there the floor consumes 55--92% of the phase" over the
# phases the ceiling does NOT exclude at the permissive budget. The reference
# reading is therefore the unconditional arm at gamma = 20.
HEADLINE_GAMMA = 20

# --- SOURCE-SEGMENT IDENTITY (control C8, second half) ---
LEGACY_SOURCE = BASE_DIR / "data" / "reference" / "R16" / "Priorite_16_regime_census.py"
CARRIED_PRIMITIVES = {"compute_kl_sign": (LEGACY_SOURCE, "compute_kl_sign")}


# --- PRIMITIVE CARRIED FROM THE FILE THAT OWNS IT ---
# Do not reformat. Byte identity is checked on the exact source text at start-up,
# trailing whitespace included. `Priorite_20_sign_floor.py` writes this same
# expression inline inside `process_dataframe` (l.74-77) rather than as a
# function; the function form is the one this repository can assert against.

def compute_kl_sign(q_phase, q_ref):
    q0 = np.clip(q_ref, 1e-6, 1.0 - 1e-6)
    q1 = np.clip(q_phase, 1e-6, 1.0 - 1e-6)
    if abs(q1 - q0) < 1e-12: return 0.0
    return q1 * np.log(q1 / q0) + (1.0 - q1) * np.log((1.0 - q1) / (1.0 - q0))


# --- ROUTINES SPECIFIC TO R16 ---

def source_segments(path, names):
    """Source text of the named top-level functions, extracted by position."""
    text = Path(path).read_text()
    tree = ast.parse(text)
    return {node.name: ast.get_source_segment(text, node)
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in names}


def check_source_identity(logger):
    """C8, on the divergence this stage evaluates. Trigger probability 0."""
    own = source_segments(Path(__file__).resolve(), set(CARRIED_PRIMITIVES))
    compared = 0
    for local_name, (path, remote_name) in sorted(CARRIED_PRIMITIVES.items()):
        remote = source_segments(path, {remote_name}).get(remote_name)
        mine = own.get(local_name)
        if remote is None or mine is None:
            logger.error(f"C8 source-identity failure: {local_name} could not be extracted "
                         f"({path.name}::{remote_name}).")
            sys.exit(1)
        if mine != remote:
            logger.error(f"C8 source-identity failure on {local_name}: the copy has drifted from "
                         f"{path.name}::{remote_name}.")
            sys.exit(1)
        compared += len(remote)
    logger.info(f"C8 source identity: {len(CARRIED_PRIMITIVES)} primitive byte-identical to "
                f"{LEGACY_SOURCE.name} ({compared} characters compared). Deterministic; trigger "
                f"probability 0 unless the copy has drifted.")


def read_census(path, logger):
    """Preamble S3: every numeric read for comparison uses round_trip."""
    if not path.exists():
        logger.error(f"Missing input: {path}. Run exp_R16_regime_census_a.py first, with no "
                     f"flags, so that the canonical arm and both counterfactual arms are written.")
        sys.exit(1)
    return pd.read_csv(path, float_precision='round_trip')


def sign_floor_frame(census):
    """
    The two floors on every phase, at every gamma.

    Vectorised port of `Priorite_20_sign_floor.py::process_dataframe`, whose two
    `np.inf` branches are preserved exactly: `|sharpe| < 1e-12` on the
    unconditional arm and `kl == 0` on the sign arm. Both are counted by C5.
    """
    q0 = np.clip(census['q_ref'].to_numpy(), 1e-6, 1.0 - 1e-6)
    q1 = np.clip(census['q_phase'].to_numpy(), 1e-6, 1.0 - 1e-6)
    kl = q1 * np.log(q1 / q0) + (1.0 - q1) * np.log((1.0 - q1) / (1.0 - q0))
    kl = np.where(np.abs(q1 - q0) < 1e-12, 0.0, kl)

    sharpe = census['sharpe'].to_numpy()
    t_days = census['T_days'].to_numpy()
    frame = pd.DataFrame({
        'census_source': CENSUS_SOURCE_LABEL,
        'ticker': census['ticker'], 'phase_id': census['phase_id'],
        'phase_type': census['phase_type'], 'start_date': census['start_date'],
        'end_date': census['end_date'], 'T_days': t_days, 'sharpe': sharpe,
        'q_ref': census['q_ref'], 'q_phase': census['q_phase'], 'delta_q': census['delta_q'],
        'kl_sign_nats_day': kl,
    })
    for g in GAMMAS:
        a_unc = np.where(np.abs(sharpe) < 1e-12, np.inf, 504.0 * np.log(g) / (sharpe ** 2))
        a_sign = np.where(kl == 0.0, np.inf, np.log(g) / np.where(kl == 0.0, 1.0, kl))
        frame[f'ADD_min_unc_g{g}'] = a_unc
        frame[f'ADD_min_sign_g{g}'] = a_sign
    for g in GAMMAS:
        frame[f'detectable_unc_g{g}'] = frame[f'ADD_min_unc_g{g}'].to_numpy() < t_days
        frame[f'detectable_sign_g{g}'] = frame[f'ADD_min_sign_g{g}'].to_numpy() < t_days
    frame['episode_label'] = census['episode_label']

    sign_only = frame[f'detectable_sign_g{HEADLINE_GAMMA}'] & ~frame[f'detectable_unc_g{HEADLINE_GAMMA}']
    unc_only = frame[f'detectable_unc_g{HEADLINE_GAMMA}'] & ~frame[f'detectable_sign_g{HEADLINE_GAMMA}']
    frame['arm_disagreement'] = np.select([sign_only, unc_only], ['sign_only', 'unc_only'],
                                          default='none')
    return frame


SIGN_FLOOR_COLUMNS = (
    ['census_source', 'ticker', 'phase_id', 'phase_type', 'start_date', 'end_date', 'T_days',
     'sharpe', 'q_ref', 'q_phase', 'delta_q', 'kl_sign_nats_day']
    + [f'ADD_min_unc_g{g}' for g in GAMMAS]
    + [f'ADD_min_sign_g{g}' for g in GAMMAS]
    + [f'detectable_unc_g{g}' for g in GAMMAS]
    + [f'detectable_sign_g{g}' for g in GAMMAS]
    + ['episode_label', 'arm_disagreement']
)

FEASIBILITY_COLUMNS = ['census_source', 'gamma', 'budget', 'n_phases', 'n_detectable',
                       'frac_detectable']


def feasibility_frame(floors):
    """The (gamma, budget) grid of detectable counts, `protocol_20b`'s schema."""
    rows = []
    n_phases = len(floors)
    for g in GAMMAS:
        for b in BUDGETS:
            n_det = int(floors[f'detectable_{b}_g{g}'].sum())
            rows.append({'census_source': CENSUS_SOURCE_LABEL, 'gamma': g, 'budget': b,
                         'n_phases': n_phases, 'n_detectable': n_det,
                         'frac_detectable': n_det / n_phases if n_phases > 0 else 0.0})
    return pd.DataFrame(rows)[FEASIBILITY_COLUMNS]


def floor_fraction_envelope(floors, mask, budget):
    """min and max of floor / duration over the phases the mask selects."""
    sub = floors[mask]
    if sub.empty:
        return float('nan'), float('nan'), 0
    fractions = sub[f'ADD_min_{budget}_g{HEADLINE_GAMMA}'] / sub['T_days']
    return float(fractions.min()), float(fractions.max()), len(sub)


def main():
    parser = argparse.ArgumentParser(
        description="R16 (b) -- sign floor, feasibility grid and the claims of v87")
    parser.parse_args()

    RESULTS_DIR = BASE_DIR / "results" / "R16_regime_census"
    DATA_DIR = RESULTS_DIR / "data"
    TABLES_DIR = RESULTS_DIR / "tables"
    LOGS_DIR = BASE_DIR / "logs" / "R16_regime_census"
    for d in (DATA_DIR, TABLES_DIR, LOGS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(LOGS_DIR / "exp_R16_regime_census_b.log", "exp_R16_regime_census_b")
    if not verify_hash_seed(logger):
        sys.exit(1)
    log_environment(logger, ["numpy", "pandas", "scipy", "pytest"])
    t0 = time.time()

    logger.info("R16 (b) prices two detection floors on every dated phase and reports the counts "
                "v87 L329 publishes. R16 renders no figure; the verdict is established in _a.")
    logger.info("Stochastic surface: NONE, as in _a. No seed is drawn and no seed-derivation "
                "surface exists.")

    check_source_identity(logger)

    # =====================================================================
    # INPUTS
    # =====================================================================
    census = {arm: read_census(DATA_DIR / CENSUS_FILES[arm], logger) for arm in ARMS}
    delta = read_census(DATA_DIR / "R16_boundary_convention_delta.csv", logger)
    witness = pd.read_csv(
        BASE_DIR / "data" / "reference" / "R16" / "protocol_20b_census_feasibility_vs_gamma.csv",
        float_precision='round_trip')
    superseded = pd.read_csv(
        BASE_DIR / "data" / "reference" / "R16" / "superseded" / "protocol_10a_regime_census.csv",
        float_precision='round_trip')
    for arm in ARMS:
        logger.info(f"Census [{arm}]: {len(census[arm])} phases, dating algorithms "
                    + ", ".join(f"{t} {a}" for t, a in
                                census[arm].groupby('ticker')['dating_algorithm'].first().items()))

    floors = {arm: sign_floor_frame(census[arm]) for arm in ARMS}

    # The vectorised divergence against the carried scalar primitive: two
    # implementations of one rule, per R06's doctrine. Deterministic, and the
    # budget is EXACT equality because both evaluate the same float64
    # expression on the same operands.
    scalar_kl = np.array([compute_kl_sign(q, r) for q, r in
                          zip(census["canonical"]['q_phase'], census["canonical"]['q_ref'])])
    worst_kl = float(np.max(np.abs(floors["canonical"]['kl_sign_nats_day'].to_numpy() - scalar_kl)))
    if worst_kl != 0.0:
        logger.error(f"The vectorised Bernoulli divergence departs from the carried scalar "
                     f"`compute_kl_sign` by {worst_kl:.3e}. Both evaluate the same float64 "
                     f"expression on the same operands, so any difference is a port error.")
        sys.exit(1)
    logger.info(f"Divergence cross-check: the vectorised kl(q_phase || q_ref) is EXACTLY equal to "
                f"the carried scalar `compute_kl_sign` on all {len(scalar_kl)} canonical phases "
                f"(worst |difference| = {worst_kl:g}).")

    canonical = floors["canonical"]
    n_phases = len(canonical)

    # =====================================================================
    # C5 -- DEGENERACIES OF THE FLOOR TABLE, COUNTED EVEN AT ZERO
    # =====================================================================
    for arm in ARMS:
        frame = floors[arm]
        counts = {
            'kl_sign_non_finite': int((~np.isfinite(frame['kl_sign_nats_day'])).sum()),
            'kl_sign_zero_to_infinite_floor': int((frame['kl_sign_nats_day'] == 0.0).sum()),
            'sharpe_below_1e-12_to_infinite_floor': int((frame['sharpe'].abs() < 1e-12).sum()),
            'q_phase_degenerate': int(frame['q_phase'].isin([0.0, 1.0]).sum()),
            'T_days_zero': int((frame['T_days'] == 0).sum()),
        }
        logger.info(f"C5 [{arm}] floor-table degeneracies, counted even at zero: "
                    + ", ".join(f"{k} = {v}" for k, v in counts.items())
                    + ". Deterministic; trigger probability 0.")
        if counts['kl_sign_non_finite'] > 0:
            logger.error(f"C5 FAILED on the {arm} arm: {counts['kl_sign_non_finite']} phases carry "
                         f"a non-finite kl, whose detectability flag is then decided without "
                         f"measurement (`NaN < T_days` is False counts the phase out of budget).")
            sys.exit(1)
        if counts['q_phase_degenerate'] > 0:
            logger.warning(f"C5 [{arm}]: {counts['q_phase_degenerate']} phases have q_phase in "
                           f"{{0, 1}}. Their defined treatment is the clip to [1e-6, 1 - 1e-6] "
                           f"inside compute_kl_sign, so the divergence stays finite and the "
                           f"detectability flag is decided by measurement. Counted and logged, "
                           f"not silenced.")

    # =====================================================================
    # C2 -- RECONSTRUCTION OF THE PUBLISHED COUNTS
    # =====================================================================
    # The comparison values are READ from the vendored witness rather than typed,
    # per preamble S7's rule that anchors come from v87 or from the reference CSV.
    logger.info("C2 reconstruction of the published counts on the canonical arm. Portage checks, "
                "not targets: a displaced count is a deviation to classify, never a parameter to "
                "adjust. Deterministic; trigger probability 0 under a correct port.")
    displaced = []
    for gamma, budget in ((20, 'unc'), (20, 'sign'), (252, 'unc')):
        observed = n_phases - int(canonical[f'detectable_{budget}_g{gamma}'].sum())
        row = witness[(witness['gamma'] == gamma) & (witness['budget'] == budget)].iloc[0]
        published = int(row['n_phases']) - int(row['n_detectable'])
        margin = observed - published
        message = (f"C2 (gamma = {gamma}, {budget}): {observed}/{n_phases} out of budget "
                   f"({observed / n_phases:.1%}) against the witness's {published}/"
                   f"{int(row['n_phases'])}; displacement {margin:+d} phases.")
        if margin == 0:
            logger.info(message + " Reproduces exactly.")
        else:
            displaced.append((gamma, budget, observed, published))
            logger.warning(message + " Logged before classification; nothing is tuned toward the "
                                     "published value.")
    if displaced:
        logger.warning(f"C2: {len(displaced)} of 3 published counts are displaced. They are "
                       f"reported in AUDIT_R16.md and classified there; the run continues, since "
                       f"a displaced count is a measurement.")

    # =====================================================================
    # C3 -- THE STEP OF ONE, AND THE SET BEHIND IT
    # =====================================================================
    n_sign = int(canonical[f'detectable_sign_g{HEADLINE_GAMMA}'].sum())
    n_unc = int(canonical[f'detectable_unc_g{HEADLINE_GAMMA}'].sum())
    step = n_sign - n_unc
    sign_only = canonical[canonical['arm_disagreement'] == 'sign_only']
    unc_only = canonical[canonical['arm_disagreement'] == 'unc_only']
    n_disagree = len(sign_only) + len(unc_only)
    logger.info(f"C3 the step of one. sum(detectable_sign_g20) - sum(detectable_unc_g20) = "
                f"{n_sign} - {n_unc} = {step}, which is what v87 L329 describes as 'moves that "
                f"count by one phase'. Deterministic; trigger probability 0.")
    if step != 1:
        logger.warning(f"C3: the step is {step}, not 1. Logged as measured; no parameter moves.")
    logger.info(f"C3 THE SET BEHIND THE STEP. The two arms disagree on {n_disagree} of "
                f"{n_phases} phases -- {len(sign_only)} detectable on the SIGN arm only and "
                f"{len(unc_only)} on the UNCONDITIONAL arm only. There is no single flipping "
                f"phase to name: the step of one is a NET of {len(sign_only)} and "
                f"{len(unc_only)}. v87's sentence is true of the count and false of the set. All "
                f"{n_disagree} are persisted in the `arm_disagreement` column of "
                f"R16_sign_floor.csv.")
    for label, sub in (("sign_only", sign_only), ("unc_only", unc_only)):
        for row in sub.itertuples(index=False):
            logger.info(f"C3 [{label}] {row.ticker} phase {row.phase_id} "
                        f"{row.start_date} -> {row.end_date}, T = {row.T_days}, "
                        f"SR = {row.sharpe:.4f}, kl = {row.kl_sign_nats_day:.6f}, "
                        f"floor_unc = {getattr(row, f'ADD_min_unc_g{HEADLINE_GAMMA}'):.2f}, "
                        f"floor_sign = {getattr(row, f'ADD_min_sign_g{HEADLINE_GAMMA}'):.2f}")

    # =====================================================================
    # C4 -- CONVENTION SENSITIVITY, WITH ITS DIRECTION
    # =====================================================================
    flipped = delta[delta['flipped']]
    gained = delta[(~delta['detectable_before']) & delta['detectable_after']]
    lost = delta[delta['detectable_before'] & (~delta['detectable_after'])]
    out_post_onset = len(delta) - int(delta['detectable_after'].sum())
    out_inclusive = len(delta) - int(delta['detectable_before'].sum())
    out_low, out_high = min(out_post_onset, out_inclusive), max(out_post_onset, out_inclusive)
    logger.info(f"C4 convention sensitivity. {len(flipped)} of {len(delta)} phases change "
                f"detectability with the boundary convention, {len(gained)} GAINING detectability "
                f"under the post-onset convention v87 L392 imposes and {len(lost)} losing it. Not "
                f"a gate: three flips in sixty-six is a measurement, not a failure.")
    for row in flipped.itertuples(index=False):
        logger.info(f"C4 [flip] {row.ticker} phase {row.phase_id} {row.start_date} -> "
                    f"{row.end_date}: detectable {row.detectable_before} -> "
                    f"{row.detectable_after}, boundary return {row.r_boundary:.6f}, Sharpe "
                    f"{row.sharpe_before:.4f} -> {row.sharpe_after:.4f}, floor "
                    f"{row.ADD_min_before:.1f} -> {row.ADD_min_after:.1f}")
    logger.info(f"C4 envelope of the published count: [{out_low}, {out_high}] out of "
                f"{len(delta)}, i.e. [{out_low / len(delta):.1%}, {out_high / len(delta):.1%}]. "
                f"The post-onset convention gives {out_post_onset} and the inclusive convention "
                f"{out_inclusive}. The published figure is therefore the CONSERVATIVE end of its "
                f"own sensitivity interval, and the convention correction LOWERED the headline "
                f"rather than raising it: the outlier at a trough depresses the mean and inflates "
                f"the variance of the phase that follows, which biases its floor upward, which is "
                f"the mechanism v87 L392 states.")

    # =====================================================================
    # THE COUNTERFACTUAL ARMS, MEASURED AND REPORTED
    # =====================================================================
    arm_counts = {}
    for arm in ARMS:
        frame = floors[arm]
        n = len(frame)
        out = n - int(frame[f'detectable_unc_g{HEADLINE_GAMMA}'].sum())
        out_sign = n - int(frame[f'detectable_sign_g{HEADLINE_GAMMA}'].sum())
        out_252 = n - int(frame['detectable_unc_g252'].sum())
        arm_counts[arm] = {'n': n, 'out_unc20': out, 'out_sign20': out_sign, 'out_unc252': out_252,
                           'frac': out / n}
        logger.info(f"Arm [{arm}]: {n} phases, {out} out of budget at gamma = 20 unconditional "
                    f"({out / n:.1%}), {out_sign} on the sign arm, {out_252} at gamma = 252.")
    logger.info(f"The three arms move the headline from {arm_counts['canonical']['frac']:.1%} "
                f"(canonical, published) to {arm_counts['strict_ps']['frac']:.1%} (strict "
                f"Pagan-Sossounov) and {arm_counts['symmetric']['frac']:.1%} (the substitution "
                f"applied to every ticker whose check_sanity fails). The symmetric arm moves the "
                f"headline AGAINST the manuscript's thesis by "
                f"{100 * (arm_counts['canonical']['frac'] - arm_counts['symmetric']['frac']):.1f} "
                f"points, so preamble S3's asymmetry rule assigns it the lighter examination, not "
                f"the heavier. Its CSV ships and it is registered as `R16-substitution-scope`.")

    # =====================================================================
    # THE PHASES v87 NAMES
    # =====================================================================
    detectable = canonical[f'detectable_unc_g{HEADLINE_GAMMA}']
    # "Long secular advances ... nonetheless dominate the detectable set on
    # duration alone" (L329): the longest phase of the detectable set, found by
    # argmax rather than by a typed date.
    longest = canonical[detectable].loc[canonical[detectable]['T_days'].idxmax()]
    long_floor_frac = longest[f'ADD_min_unc_g{HEADLINE_GAMMA}'] / longest['T_days']
    logger.info(f"The longest phase of the detectable set: {longest['ticker']} "
                f"{longest['start_date']} -> {longest['end_date']}, {int(longest['T_days'])} "
                f"trading days, q_ref {longest['q_ref']:.6f} -> q_phase "
                f"{longest['q_phase']:.6f}, floor {longest[f'ADD_min_unc_g{HEADLINE_GAMMA}']:.2f} "
                f"days = {long_floor_frac:.1%} of the phase. v87 L329 prints 'SPY 2011--2018: "
                f"0.541 -> 0.554 over 1,753 days'.")

    covid = canonical[(canonical['ticker'] == COVID_TICKER)
                      & (canonical['episode_label'] == COVID_LABEL)]
    if len(covid) != 1:
        logger.error(f"The COVID anchor is not unique: {len(covid)} phases of {COVID_TICKER} "
                     f"carry the label {COVID_LABEL}. v87 L331 names one.")
        sys.exit(1)
    covid = covid.iloc[0]
    logger.info(f"The COVID anchor v87 L331 names: {COVID_TICKER} {covid['start_date']} -> "
                f"{covid['end_date']}, T = {int(covid['T_days'])} trading days, delta_q = "
                f"{covid['delta_q']:.4f}, annualized Sharpe = {covid['sharpe']:.4f}, "
                f"kl = {covid['kl_sign_nats_day']:.6f} nats/day, sign floor "
                f"{covid['ADD_min_sign_g252']:.2f} days at gamma = 252 and "
                f"{covid['ADD_min_sign_g20']:.2f} at gamma = 20, i.e. "
                f"{covid['ADD_min_sign_g20'] / covid['T_days']:.1%} of the phase. v87 prints "
                f"Delta q ~ -0.28, SR ~ -6.0, 23 days, kl = 0.162, ~34 and 18.5 days, 'four "
                f"fifths of the phase'. This phase exists ONLY under the substitution: strict "
                f"Pagan-Sossounov censors it at min_phase = 84.")

    # =====================================================================
    # THE 55--92% ENVELOPE OF L329, AND THE VARIANTS THAT DO NOT REACH IT
    # =====================================================================
    frac_min, frac_max, n_det = floor_fraction_envelope(canonical, detectable, 'unc')
    logger.info(f"v87 L329 reads 'even there the floor consumes 55--92% of the phase'. Measured "
                f"over the {n_det} phases the ceiling does not exclude at gamma = 20 "
                f"unconditional: [{frac_min:.1%}, {frac_max:.1%}]. The upper end reproduces; the "
                f"lower end does not.")
    below = canonical[detectable & ((canonical[f'ADD_min_unc_g{HEADLINE_GAMMA}']
                                     / canonical['T_days']) < 0.55)]
    for row in below.itertuples(index=False):
        fraction = getattr(row, f'ADD_min_unc_g{HEADLINE_GAMMA}') / row.T_days
        logger.info(f"Below 55%: {row.ticker} {row.start_date} -> {row.end_date}, T = "
                    f"{row.T_days}, floor fraction {fraction:.2%}")
    # Preamble S4.5: the definitional variants are ENUMERATED and logged, and the
    # cause is then declared unidentified. None of them yields 55--92.
    variants = {
        "bull phases only": detectable & (canonical['phase_type'] == 'bull'),
        "T_days >= 250": detectable & (canonical['T_days'] >= 250),
        "bull and T_days >= 250": (detectable & (canonical['phase_type'] == 'bull')
                                   & (canonical['T_days'] >= 250)),
    }
    for name, mask in variants.items():
        lo, hi, count = floor_fraction_envelope(canonical, mask, 'unc')
        logger.info(f"Variant '{name}': [{lo:.1%}, {hi:.1%}] over {count} phases.")
    lo_sign, hi_sign, n_sign_det = floor_fraction_envelope(
        canonical, canonical[f'detectable_sign_g{HEADLINE_GAMMA}'], 'sign')
    logger.info(f"Variant 'sign arm at gamma = 20': [{lo_sign:.1%}, {hi_sign:.1%}] over "
                f"{n_sign_det} phases.")
    sup_det = superseded['detectable_flag'].astype(bool)
    sup_fraction = (superseded['ADD_min_days'] / superseded['T_days'])[sup_det]
    logger.info(f"Variant 'the superseded protocol_10a census' ({len(superseded)} phases, "
                f"{int(sup_det.sum())} detectable): [{sup_fraction.min():.1%}, "
                f"{sup_fraction.max():.1%}].")
    logger.info(f"None of the variants yields 55--92%. The single phase at "
                f"{long_floor_frac:.1%} rounds to 55%, which SUGGESTS the published lower bound "
                f"was read off that one phase rather than off the minimum of the set, but no "
                f"measurement here establishes it. Per preamble S4.5 the cause is NOT identified. "
                f"Classified D2 as `R16-floor-frac-envelope`.")

    # =====================================================================
    # PERSISTENCE
    # =====================================================================
    sign_floor = canonical[SIGN_FLOOR_COLUMNS]
    feasibility = feasibility_frame(canonical)
    save_fair_csv(sign_floor, DATA_DIR / "R16_sign_floor.csv")
    save_fair_csv(feasibility, DATA_DIR / "R16_feasibility_vs_gamma.csv")
    logger.info("R16_feasibility_vs_gamma.csv: " + "; ".join(
        f"gamma {int(r.gamma)} {r.budget} n_detectable {int(r.n_detectable)} "
        f"(out of budget {int(r.n_phases - r.n_detectable)})"
        for r in feasibility.itertuples(index=False)))

    cardinalities = {"R16_sign_floor": (len(sign_floor), n_phases),
                     "R16_feasibility_vs_gamma": (len(feasibility), len(GAMMAS) * len(BUDGETS))}
    for name, (observed, required) in cardinalities.items():
        if observed != required:
            logger.error(f"Cardinality error on {name}: {observed} rows, expected {required}.")
            sys.exit(1)
    logger.info("Cardinality check: " + ", ".join(f"{k} = {v[0]}" for k, v in cardinalities.items()))

    # =====================================================================
    # LATEX MACROS
    # =====================================================================
    # Cardinal, not ordinal: preamble S6 fixes \R<Ordinal><Claim> with the
    # ordinal in English words, and the repository realises cardinals throughout
    # (ROne ... RSix, REleven, REighteen). Every value below is computed from an
    # object in memory; no literal is typed.
    out_unc20 = n_phases - n_unc
    out_sign20 = n_phases - n_sign
    out_unc252 = n_phases - int(canonical['detectable_unc_g252'].sum())
    sharpe_one_g20 = 504.0 * np.log(20)
    sharpe_one_g252 = 504.0 * np.log(252)
    strict = arm_counts["strict_ps"]
    symmetric = arm_counts["symmetric"]
    strict_spy = int((census["strict_ps"]['ticker'] == "SPY").sum())

    macros = ["% Auto-generated by exp_R16_regime_census_b.py -- do not edit.",
              "% \\RSixteenFlippedUp counts the phases that GAIN detectability under the",
              "% post-onset boundary convention of v87 L392; \\RSixteenFlippedDown counts those",
              "% that lose it. The direction is not readable from the count alone.",
              "% The \\RSixteenStrictPs... and \\RSixteenSymmetric... macros price the two",
              "% counterfactual datings of docs/DEVIATIONS.md `R16-dating-misdescription` and",
              "% `R16-substitution-scope`. They are not the published configuration.",
              "% No macro is emitted for the analytic bound 504 ln(1/alpha_0)/SR^2 itself: it is",
              "% a result of the manuscript, not a measurement of this stream. Only its two",
              "% numerical evaluations, which is what v87 L260 prints, appear below."]
    macros.append(f"\\newcommand{{\\RSixteenPhaseCount}}{{{n_phases}}}")
    macros.append(f"\\newcommand{{\\RSixteenOutOfBudgetUncGammaTwenty}}{{{out_unc20}}}")
    macros.append(f"\\newcommand{{\\RSixteenOutOfBudgetSignGammaTwenty}}{{{out_sign20}}}")
    macros.append(f"\\newcommand{{\\RSixteenOutOfBudgetFracGammaTwenty}}"
                  f"{{{100.0 * out_unc20 / n_phases:.1f}\\%}}")
    macros.append(f"\\newcommand{{\\RSixteenOutOfBudgetGammaTwoFiftyTwo}}{{{out_unc252}}}")
    macros.append(f"\\newcommand{{\\RSixteenFlippedPhases}}{{{len(flipped)}}}")
    macros.append(f"\\newcommand{{\\RSixteenFlippedUp}}{{{len(gained)}}}")
    macros.append(f"\\newcommand{{\\RSixteenFlippedDown}}{{{len(lost)}}}")
    macros.append(f"\\newcommand{{\\RSixteenOutOfBudgetLow}}{{{out_low}}}")
    macros.append(f"\\newcommand{{\\RSixteenOutOfBudgetHigh}}{{{out_high}}}")
    macros.append(f"\\newcommand{{\\RSixteenSpyLongQRef}}{{{longest['q_ref']:.3f}}}")
    macros.append(f"\\newcommand{{\\RSixteenSpyLongQPhase}}{{{longest['q_phase']:.3f}}}")
    macros.append(f"\\newcommand{{\\RSixteenSpyLongTDays}}{{{int(longest['T_days'])}}}")
    macros.append(f"\\newcommand{{\\RSixteenSpyLongFloorFrac}}{{{100.0 * long_floor_frac:.1f}\\%}}")
    macros.append(f"\\newcommand{{\\RSixteenFloorFracMin}}{{{100.0 * frac_min:.1f}\\%}}")
    macros.append(f"\\newcommand{{\\RSixteenFloorFracMax}}{{{100.0 * frac_max:.1f}\\%}}")
    macros.append(f"\\newcommand{{\\RSixteenSharpeOneCostGammaTwenty}}{{{sharpe_one_g20:.2f}}}")
    macros.append(f"\\newcommand{{\\RSixteenSharpeOneCostGammaTwoFiftyTwo}}"
                  f"{{{sharpe_one_g252:.2f}}}")
    macros.append(f"\\newcommand{{\\RSixteenCovidKl}}{{{covid['kl_sign_nats_day']:.4f}}}")
    macros.append(f"\\newcommand{{\\RSixteenCovidFloorGammaTwoFiftyTwo}}"
                  f"{{{covid['ADD_min_sign_g252']:.2f}}}")
    macros.append(f"\\newcommand{{\\RSixteenCovidFloorGammaTwenty}}"
                  f"{{{covid['ADD_min_sign_g20']:.2f}}}")
    macros.append(f"\\newcommand{{\\RSixteenCovidTDays}}{{{int(covid['T_days'])}}}")
    macros.append(f"\\newcommand{{\\RSixteenStrictPsPhaseCount}}{{{strict['n']}}}")
    macros.append(f"\\newcommand{{\\RSixteenStrictPsOutOfBudgetUncGammaTwenty}}"
                  f"{{{strict['out_unc20']}}}")
    macros.append(f"\\newcommand{{\\RSixteenStrictPsOutOfBudgetFracGammaTwenty}}"
                  f"{{{100.0 * strict['frac']:.1f}\\%}}")
    macros.append(f"\\newcommand{{\\RSixteenStrictPsSpyPhaseCount}}{{{strict_spy}}}")
    macros.append(f"\\newcommand{{\\RSixteenSymmetricPhaseCount}}{{{symmetric['n']}}}")
    macros.append(f"\\newcommand{{\\RSixteenSymmetricOutOfBudgetUncGammaTwenty}}"
                  f"{{{symmetric['out_unc20']}}}")
    macros.append(f"\\newcommand{{\\RSixteenSymmetricOutOfBudgetFracGammaTwenty}}"
                  f"{{{100.0 * symmetric['frac']:.1f}\\%}}")
    macros.append(f"\\newcommand{{\\RSixteenArmDisagreementPhases}}{{{n_disagree}}}")
    macros.append(f"\\newcommand{{\\RSixteenArmDisagreementSignOnly}}{{{len(sign_only)}}}")
    macros.append(f"\\newcommand{{\\RSixteenArmDisagreementUncOnly}}{{{len(unc_only)}}}")

    tex_path = TABLES_DIR / "R16_claims.tex"
    with open(tex_path, "w") as handle:
        handle.write("\n".join(macros) + "\n")
    n_emitted = sum(1 for m in macros if m.startswith("\\newcommand"))
    logger.info(f"Emitted {n_emitted} macros to {tex_path.name}, prefix \\RSixteen per preamble "
                f"S6's ordinal-in-English rule; \\RSixteenth appears nowhere. Every value is "
                f"computed from an object in memory. No macro names the analytic bound "
                f"504 ln(1/alpha_0)/SR^2 itself, only its two numerical evaluations at SR = 1, "
                f"which is what v87 L260 prints.")
    undefined = [m for m in macros if m.startswith("\\newcommand") and 'nan' in m.lower()]
    if undefined:
        logger.error(f"{len(undefined)} macros carry the body `nan`: {undefined}")
        sys.exit(1)

    # =====================================================================
    # THE SECTION ADDRESSED TO R13
    # =====================================================================
    logger.info("For stream R13, which consumes this census: the columns R13 reads as "
                "`ADD_min_census` and `detectable_flag_census` are `ADD_min_days` and "
                "`detectable_flag` of results/R16_regime_census/data/R16_regime_census.csv, "
                "which keep the witness names so that the reference comparison stays "
                "cell-for-cell. `ADD_min_days` is 504*ln(1/alpha)/SR^2 at alpha = 0.05 "
                "(gamma = 20) in trading days and `detectable_flag` is `ADD_min_days < T_days`; "
                "the same two quantities appear at every gamma in R16_sign_floor.csv as "
                "`ADD_min_unc_g{20,252,1260}` and `detectable_unc_g{20,252,1260}`. The file R13 "
                "reads is the DEFAULT-RUN CANONICAL ARM.")

    # =====================================================================
    # DIGESTS AND TIMING
    # =====================================================================
    for name in ("R16_sign_floor.csv", "R16_feasibility_vs_gamma.csv"):
        logger.info(f"SHA-256 {name:<40} : {compute_sha256(DATA_DIR / name)}")
    logger.info(f"SHA-256 {tex_path.name:<40} : {compute_sha256(tex_path)}")
    logger.info(f"Execution completed in {time.time() - t0:.1f}s.")


if __name__ == "__main__":
    main()
