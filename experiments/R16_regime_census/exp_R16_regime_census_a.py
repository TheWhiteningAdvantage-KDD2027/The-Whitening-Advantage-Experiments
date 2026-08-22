#!/usr/bin/env python3
"""
==========================================================================
R16 (a) -- RETROSPECTIVE REGIME DATING AND CENSUS OF FOUR ETF STREAMS
==========================================================================
R16 carries the most-cited empirical claim of articleB_whitening_v87.tex --
"80% of dated directional episodes fall out of budget" -- which appears at L57
(abstract), L87 (contributions), L329 (body) and L374 (conclusion). This script
is the first of the two-stage chain: it dates the bull/bear phases of SPY, PFF,
VNQ and BWX over 2000--2025 and writes the census; `_b` prices the sign floor,
the feasibility grid and the LaTeX macros.

THREE DATING ARMS, ALL PERSISTED, ONE CANONICAL.

  canonical   Pagan--Sossounov on the four streams, with Lunde--Timmermann
              substituted on SPY when `check_sanity` fails on the PS MACRO
              dating.  66 phases (SPY 30, PFF 7, VNQ 18, BWX 11).  THIS IS THE
              PUBLISHED CONFIGURATION and the default output,
              `R16_regime_census.csv`.
  strict_ps   Pagan--Sossounov on all four, no substitution.  48 phases.
              `R16_regime_census_strict_ps.csv`.
  symmetric   Lunde--Timmermann substituted on EVERY ticker whose
              `check_sanity` fails -- the rule the delivered script writes for
              SPY, applied consistently.  102 phases.
              `R16_regime_census_symmetric.csv`.

WHAT THE SUBSTITUTION IS, AND WHAT IS AND IS NOT SILENT ABOUT IT.  The
delivered legacy script guards the substitution with
`if ticker == 'SPY'` (l.233) and logs it: line 3 of the vendored
`data/reference/R16/Priorite_16_regime_census.log` reads
`WARNING | [SPY] Sanity check P-S failed. Fallback to Lunde-Timmermann for
MACRO.`  The script is therefore NOT silent.  What the reproducibility specification requires of a
fallback that is kept rather than removed is more than a warning: it must be
selected by an explicit argument and stamped in the output filename.  That is
what the three arms above restructure, and the substitution is additionally
carried into a `dating_algorithm` column on every census row.

`sanity_ok` is initialised to `True` in the delivered script and reassigned only
inside the SPY branch, so PFF, VNQ and BWX are never tested by it.  This script
evaluates `check_sanity` on all four tickers on every run and logs the four
verdicts.  All four fail.

WHAT IS SILENT IS THE MANUSCRIPT.  v87 L329 describes "a retrospective
multi-scale Pagan--Sossounov bull/bear dating ... of the four streams
(2000--2025; $66$ phases after duration censoring)".  Lunde--Timmermann applies
no duration censoring, and strict Pagan--Sossounov on all four streams yields
48 phases, not 66.  L329's account of the method is unreachable as written.
The 66 values themselves reproduce exactly; what fails is the description of how
they were obtained.  Registered as Class A / D3 `R16-dating-misdescription` in
docs/DEVIATIONS.md, with `R16_regime_census_strict_ps.csv` as the proof
artefact.  Preamble S4.5 forbids attributing a cause or an intent that the
measurement does not establish, and none is attributed here.

THE POST-ONSET BOUNDARY CONVENTION (v87 L392) is imperative and is what the
delivered script's own header records as its correction: the return dated at a
turning point closes the regime it ends, so consecutive phases partition the
return series and no pre-change observation enters a phase's Sharpe.  Both
conventions are computed for every phase and their difference is persisted to
`R16_boundary_convention_delta.csv`, which is what makes control C4 readable.

NO STOCHASTIC SURFACE.  The delivered scripts call `set_seed(42)` and neither
draws a random number: the dating filters, the Sharpe ratios, the Bernoulli
divergences and the detectability flags are deterministic functions of the four
price series.  There is therefore no seed-derivation surface to migrate to a
128-bit `SeedSequence`, and no unused helper is added to suggest otherwise.
This is the honest outcome of the prompt's section 2.4 and is itself reportable.

NO FIGURE.  v87's census paragraphs L329 and L331 reference only
`fig:oracle_frontier`, which belongs to R01, and carry no `\\includegraphics`.
R16 renders no figure; the verdict is logged at start-up.

References:
- Pagan, A. R. & Sossounov, K. A. (2003). A simple framework for analysing bull
  and bear markets. Journal of Applied Econometrics, 18(1), 23-46.
- Lunde, A. & Timmermann, A. (2004). Duration dependence in stock prices: an
  analysis of bull and bear markets. Journal of Business & Economic Statistics,
  22(3), 253-273.
- Bry, G. & Boschan, C. (1971). Cyclical Analysis of Time Series: Selected
  Procedures and Computer Programs. NBER.
- Lorden, G. (1971). Procedures for reacting to a change in distribution.
  Annals of Mathematical Statistics, 42(6), 1897-1908.
- Lai, T. L. (1998). Information bounds and quick detection of parameter changes
  in stochastic systems. IEEE Trans. Inf. Theory, 44(7), 2917-2929.
- Wilson, E. B. (1927). Probable inference, the law of succession, and
  statistical inference. JASA, 22(158), 209-212.

NOTATION (prompt section 6)
  q_ref        unconditional probability of an up day over the whole history
  q_phase      probability of an up day inside the phase
  delta_q      q_phase - q_ref
  SR           annualized Sharpe of the phase, mean/std * sqrt(252), sign kept
  T_days       phase duration in trading days, post-onset: idx(en) - idx(st)
  ADD_min_days 504*ln(1/alpha)/SR^2 at alpha = 0.05, the Sharpe-ceiling floor
  source_scale MACRO or MESO_SPLIT, the dating scale that produced the phase
  dating_algorithm  pagan_sossounov or lunde_timmermann, per ticker per arm
==========================================================================
"""

import sys
from pathlib import Path

# Determinism bootstrap: fair_env imports only os and sys, so the environment
# block is posted before numpy is loaded and before any BLAS thread limit is read. PYTHONHASHSEED cannot be set from
# here -- CPython reads it at interpreter start-up -- so it is exported by
# run_experiment_R16.sh and verified twice below.
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
                                             compute_sha256, save_fair_csv, log_artifact_manifest)

disable_pandas_multithreading()

import ast
import time
import argparse
import scipy.stats as stats

# --- PROTOCOL SPECIFICATION, IMPERATIVE, FROM v87 AND THE DELIVERED SCRIPT ---
# Prompt section 1: the four ETFs, the two dating scales with their exact
# parameters, the Lunde--Timmermann cross-check, and alpha = 0.05 (gamma = 20).
TICKERS = ("SPY", "PFF", "VNQ", "BWX")
ALPHA = 0.05
MACRO_PARAMS = dict(window=168, min_phase=84, min_cycle=336, min_edge=126, jump_thresh=0.182321)
MESO_PARAMS = dict(window=63, min_phase=42, min_cycle=126, min_edge=126, jump_thresh=0.182321)
LT_PARAMS = dict(lambda_1=0.15, lambda_2=0.15)
# The hierarchical merge: a MACRO phase longer than 400 trading days is offered
# to the MESO scale, and a candidate sub-phase shorter than 42 days or of
# amplitude below 0.15 in cumulated log price is pruned. Both literals are the
# delivered script's (l.248, l.266).
MERGE_MACRO_DURATION = 400
SUBSPLIT_MIN_DURATION = 42
SUBSPLIT_MIN_AMPLITUDE = 0.15
ARMS = ("canonical", "strict_ps", "symmetric")
# C6's tolerance ladder is the filters' own resolution and nothing else: the
# MACRO minimum phase (84 trading days) and the MESO minimum phase (42). Exact
# agreement is the first rung. No rung is derived from an observed agreement.
CONCORDANCE_TOLERANCES = (0, MESO_PARAMS["min_phase"], MACRO_PARAMS["min_phase"])

# --- SOURCE-SEGMENT IDENTITY (control C8) ---
# Preamble S4.2 forbids hoisting a scientific primitive into
# experiments/common/, so every routine below is duplicated from the file that
# owns it and asserted byte-identical to that file at start-up: the duplication
# is deliberate and it cannot drift. The dating primitives are owned by the
# vendored legacy script; the Wilson interval is owned by R02, which is where
# this repository's copy of it lives.
LEGACY_SOURCE = BASE_DIR / "data" / "reference" / "R16" / "Priorite_16_regime_census.py"
R02_SOURCE = BASE_DIR / "experiments" / "R02_whitening_ljungbox" / "exp_R02_whitening_ljungbox.py"
CARRIED_PRIMITIVES = {
    "enforce_alternance": (LEGACY_SOURCE, "enforce_alternance"),
    "pagan_sossounov": (LEGACY_SOURCE, "pagan_sossounov"),
    "lunde_timmermann": (LEGACY_SOURCE, "lunde_timmermann"),
    "get_episodes": (LEGACY_SOURCE, "get_episodes"),
    "check_sanity": (LEGACY_SOURCE, "check_sanity"),
    "compute_kl_sign": (LEGACY_SOURCE, "compute_kl_sign"),
    "wilson_score_interval": (R02_SOURCE, "wilson_score_interval"),
}


# --- PRIMITIVES CARRIED FROM THE FILES THAT OWN THEM ---
# Do not reformat. Byte identity is checked on the exact source text at start-up,
# trailing whitespace included.

def enforce_alternance(pts):
    if not pts: return []
    res = []
    current_type = pts[0][1]
    current_extreme = pts[0]
    for pt in pts[1:]:
        if pt[1] == current_type:
            if current_type == 'peak' and pt[2] > current_extreme[2]:
                current_extreme = pt
            elif current_type == 'trough' and pt[2] < current_extreme[2]:
                current_extreme = pt
        else:
            res.append(current_extreme)
            current_type = pt[1]
            current_extreme = pt
    res.append(current_extreme)
    return res


def pagan_sossounov(prices, window=168, min_phase=84, min_cycle=336, min_edge=126, jump_thresh=0.182321):
    n = len(prices)
    if n < min_cycle: return []
    
    roll_max = prices.rolling(window=2*window+1, center=True, min_periods=1).max()
    roll_min = prices.rolling(window=2*window+1, center=True, min_periods=1).min()
    
    is_peak = (prices == roll_max)
    is_trough = (prices == roll_min)
    
    is_peak.iloc[:min_edge] = False
    is_peak.iloc[-min_edge:] = False
    is_trough.iloc[:min_edge] = False
    is_trough.iloc[-min_edge:] = False
    
    pts = []
    for d, _ in is_peak[is_peak].items(): pts.append((d, 'peak', prices.loc[d]))
    for d, _ in is_trough[is_trough].items(): pts.append((d, 'trough', prices.loc[d]))
    pts.sort(key=lambda x: x[0])
    
    pts = enforce_alternance(pts)
    
    while True:
        pts = enforce_alternance(pts)
        if len(pts) < 2: break
        bad_idx = -1
        min_dur = float('inf')
        for i in range(len(pts)-1):
            dur = prices.index.get_loc(pts[i+1][0]) - prices.index.get_loc(pts[i][0])
            jump = abs(pts[i+1][2] - pts[i][2])
            if dur < min_phase and jump <= jump_thresh:
                if dur < min_dur:
                    min_dur = dur
                    bad_idx = i
        if bad_idx == -1: break
        pts.pop(bad_idx+1)
        pts.pop(bad_idx)
        
    while True:
        pts = enforce_alternance(pts)
        if len(pts) < 3: break
        bad_idx = -1
        min_cyc = float('inf')
        for i in range(len(pts)-2):
            dur = prices.index.get_loc(pts[i+2][0]) - prices.index.get_loc(pts[i][0])
            jump1 = abs(pts[i+1][2] - pts[i][2])
            jump2 = abs(pts[i+2][2] - pts[i+1][2])
            if dur < min_cycle and jump1 <= jump_thresh and jump2 <= jump_thresh:
                if dur < min_cyc:
                    min_cyc = dur
                    bad_idx = i
        if bad_idx == -1: break
        pt1 = pts[bad_idx]
        pt3 = pts[bad_idx+2]
        if pt1[1] == 'peak':
            if pt1[2] < pt3[2]:
                pts.pop(bad_idx+1); pts.pop(bad_idx)
            else:
                pts.pop(bad_idx+2); pts.pop(bad_idx+1)
        else:
            if pt1[2] > pt3[2]:
                pts.pop(bad_idx+1); pts.pop(bad_idx)
            else:
                pts.pop(bad_idx+2); pts.pop(bad_idx+1)
                
    return enforce_alternance(pts)


def lunde_timmermann(prices, lambda_1=0.15, lambda_2=0.15):
    if len(prices) == 0: return []
    state = None
    run_max, run_max_date = prices.iloc[0], prices.index[0]
    run_min, run_min_date = prices.iloc[0], prices.index[0]
    pts = []
    
    for d, p in prices.items():
        if state is None:
            if run_max - p > lambda_1:
                state = -1; pts.append((run_max_date, 'peak', run_max)); run_min, run_min_date = p, d
            elif p - run_min > lambda_2:
                state = 1; pts.append((run_min_date, 'trough', run_min)); run_max, run_max_date = p, d
            else:
                if p > run_max: run_max, run_max_date = p, d
                if p < run_min: run_min, run_min_date = p, d
        elif state == 1:
            if p > run_max: run_max, run_max_date = p, d
            elif run_max - p > lambda_1:
                state = -1; pts.append((run_max_date, 'peak', run_max)); run_min, run_min_date = p, d
        elif state == -1:
            if p < run_min: run_min, run_min_date = p, d
            elif p - run_min > lambda_2:
                state = 1; pts.append((run_min_date, 'trough', run_min)); run_max, run_max_date = p, d
                
    if state == 1: pts.append((run_max_date, 'peak', run_max))
    elif state == -1: pts.append((run_min_date, 'trough', run_min))
    return enforce_alternance(pts)


def get_episodes(start, end, ptype):
    sy, ey = start.year, end.year
    st_str, en_str = start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
    if ptype == 'bear' and st_str <= '2020-03-31' and en_str >= '2020-03-01': return "COVID_2020"
    if ptype == 'bear' and sy <= 2008 and ey >= 2008: return "GFC_2008"
    if ptype == 'bull' and sy <= 2017 and ey >= 2017: return "MeltUp_2017"
    if ptype == 'bull' and (sy <= 2015 <= ey or sy <= 2019 <= ey): return "Calm_2015_or_2019"
    return ""


def check_sanity(phases):
    eps = [get_episodes(p[0], p[1], p[2]) for p in phases]
    return ('COVID_2020' in eps) and ('GFC_2008' in eps) and ('MeltUp_2017' in eps) and any('Calm' in e for e in eps)


def compute_kl_sign(q_phase, q_ref):
    q0 = np.clip(q_ref, 1e-6, 1.0 - 1e-6)
    q1 = np.clip(q_phase, 1e-6, 1.0 - 1e-6)
    if abs(q1 - q0) < 1e-12: return 0.0
    return q1 * np.log(q1 / q0) + (1.0 - q1) * np.log((1.0 - q1) / (1.0 - q0))


# The per-point interval used by C6. Carried from R02, which owns this
# repository's copy, and asserted byte-identical to it alongside the dating
# primitives.
def wilson_score_interval(k: int, n: int, confidence: float = 0.95) -> tuple:
    if n == 0: return 0.0, 0.0
    p_hat = k / n
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n)) / denom
    return max(0.0, float(center - margin)), min(1.0, float(center + margin))


# --- ROUTINES SPECIFIC TO R16 ---

def source_segments(path, names):
    """
    Source text of the named top-level functions, extracted by position rather
    than by import: importing the legacy script would execute its environment
    block, its logger, its output directory creation and its `try/except
    ImportError` data-loading fallback.
    """
    text = Path(path).read_text()
    tree = ast.parse(text)
    return {node.name: ast.get_source_segment(text, node)
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in names}


def check_source_identity(logger):
    """
    C8. Byte identity of every carried primitive against the file that owns it.

    Deterministic, trigger probability zero unless a copy has drifted. The same
    control intercepted three transcription errors on R06 before any execution.
    """
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
    logger.info(f"C8 source identity: {len(CARRIED_PRIMITIVES)} primitives byte-identical to the "
                f"files that own them ({compared} characters compared) -- the six dating and "
                f"divergence routines against {LEGACY_SOURCE.name}, and the Wilson interval "
                f"against {R02_SOURCE.name}. Preamble S4.2 forbids hoisting any of them into "
                f"experiments/common/, so the duplication is deliberate. Deterministic; trigger "
                f"probability 0 unless a copy has drifted.")


def load_returns(ticker):
    """
    The daily log-return series, read directly from the derived FirstRate CSV.

    This replaces the delivered script's `try: from
    Priorite_14_real_world_backtest import get_daily_data / except ImportError:
    ... NotImplementedError` block, which is a fallback of exactly the kind
    the specification bans: an absent module left the script running with a stub.
    `float_precision='round_trip'` is required on every numeric read of this
    repository: the fast float parser is not correctly rounded.
    """
    path = BASE_DIR / "data" / "derived_firstrate" / f"R01_daily_{ticker}.csv"
    if not path.exists():
        sys.exit(f"FATAL: {path} is missing. R16 dates the derived FirstRate series and has no "
                 f"other source for them.")
    frame = pd.read_csv(path, float_precision='round_trip', index_col='Date', parse_dates=True)
    if 'log_ret' not in frame.columns:
        sys.exit(f"FATAL: {path.name} carries no `log_ret` column.")
    series = frame['log_ret']
    series = series[~series.index.duplicated(keep='first')].sort_index()
    return series.dropna()


def merge_meso(prices, pts_macro, pts_meso):
    """
    The hierarchical MACRO/MESO merge, carried from the delivered script's main
    block (l.240-276), where it is inlined and cannot be extracted as a function.

    A MACRO phase of more than `MERGE_MACRO_DURATION` trading days is offered the
    MESO turning points strictly inside it; the resulting sequence is pruned of
    every sub-phase shorter than `SUBSPLIT_MIN_DURATION` or of amplitude below
    `SUBSPLIT_MIN_AMPLITUDE`, smallest amplitude first, with the two MACRO
    endpoints protected.
    """
    final_pts = []
    if len(pts_macro) > 0:
        final_pts.append(pts_macro[0])
    for i in range(len(pts_macro) - 1):
        A = pts_macro[i]
        B = pts_macro[i + 1]
        dur_macro = prices.index.get_loc(B[0]) - prices.index.get_loc(A[0])
        if dur_macro <= MERGE_MACRO_DURATION:
            final_pts.append(B)
            continue
        candidates = [m for m in pts_meso if A[0] < m[0] < B[0]]
        if not candidates:
            final_pts.append(B)
            continue
        seq = [A] + candidates + [B]
        while True:
            seq = enforce_alternance(seq)
            if len(seq) <= 2:
                break
            bad_idx = -1
            min_amp = float('inf')
            for j in range(len(seq) - 1):
                dur = prices.index.get_loc(seq[j + 1][0]) - prices.index.get_loc(seq[j][0])
                amp = abs(seq[j + 1][2] - seq[j][2])
                if dur < SUBSPLIT_MIN_DURATION or amp < SUBSPLIT_MIN_AMPLITUDE:
                    if amp < min_amp:
                        min_amp = amp
                        bad_idx = j
            if bad_idx == -1:
                break
            if bad_idx == 0:
                seq.pop(1)
            elif bad_idx == len(seq) - 2:
                seq.pop(len(seq) - 2)
            else:
                seq.pop(bad_idx + 1)
        for pt in seq[1:]:
            final_pts.append(pt)
    return final_pts


def build_phases(final_pts, pts_macro):
    """(start, end, type, source_scale) for every consecutive pair of points."""
    phases = []
    for i in range(len(final_pts) - 1):
        st = final_pts[i][0]
        en = final_pts[i + 1][0]
        ptype = 'bear' if final_pts[i][1] == 'peak' else 'bull'
        is_macro = any(pts_macro[j][0] == st and pts_macro[j + 1][0] == en
                       for j in range(len(pts_macro) - 1))
        phases.append((st, en, ptype, 'MACRO' if is_macro else 'MESO_SPLIT'))
    return phases


def classify_pathology(vol_pct, sharpe):
    """
    Vectorised form of the delivered script's `df_t.apply(classify_pathology,
    axis=1)` (l.359-368), which the specification bans in its row-wise form. The
    branch order of the original if-chain is preserved exactly by `np.select`,
    which returns the first condition that holds.
    """
    h_vol = vol_pct >= 0.75
    abs_sr = sharpe.abs()
    h_sr = abs_sr >= 2.0
    l_sr = abs_sr < 1.0
    return np.select([h_vol & l_sr, (~h_vol) & h_sr, h_vol & h_sr],
                     ['scale', 'location', 'both'], default='neither')


def refined_episode_label(frame):
    """
    Vectorised form of the delivered script's `df_t.apply(refined_episode_label,
    axis=1)` (l.370-381). A bull phase covering 2017 keeps the MeltUp label only
    if it is a low-volatility, 150-400 day, |SR| in [2, 4] advance; otherwise the
    label is stripped, exactly as the original's `else` branch does, and only
    when the token is present.
    """
    base = frame['base_episode_label']
    start_year = pd.to_datetime(frame['start_date']).dt.year
    end_year = pd.to_datetime(frame['end_date']).dt.year
    covers = (start_year <= 2017) & (end_year >= 2017) & (frame['phase_type'] == 'bull')
    abs_sr = frame['sharpe'].abs()
    keeps = (covers & (frame['vol_pct'] < 0.25)
             & (frame['T_days'] >= 150) & (frame['T_days'] <= 400)
             & (abs_sr >= 2) & (abs_sr <= 4))
    stripped = base.str.replace("MeltUp_2017", "", regex=False).str.strip()
    has_token = base.str.contains("MeltUp_2017", regex=False)
    otherwise = base.where(~has_token, stripped)
    return pd.Series(np.where(keeps, "MeltUp_2017", np.where(covers, otherwise, base)),
                     index=frame.index)


def dating_for_arm(arm, ticker, sanity_ok, pts_macro_ps, pts_macro_lt):
    """
    The turning points the arm feeds to the census, and the name of the
    algorithm that produced them.

    canonical  substitutes Lunde--Timmermann on SPY alone when `check_sanity`
               fails, which is the delivered script's `if ticker == 'SPY'` guard
               (l.233) reproduced exactly.
    strict_ps  never substitutes.
    symmetric  substitutes on every ticker whose `check_sanity` fails.
    """
    if arm == "canonical":
        substitute = (ticker == "SPY") and not sanity_ok
    elif arm == "strict_ps":
        substitute = False
    elif arm == "symmetric":
        substitute = not sanity_ok
    else:
        sys.exit(f"FATAL: unknown dating arm {arm!r}.")
    if substitute:
        return pts_macro_lt, "lunde_timmermann"
    return pts_macro_ps, "pagan_sossounov"


def census_for_ticker(arm, ticker, returns, prices, pts_macro, algorithm, pts_meso, logger):
    """
    The phases of one ticker under one arm, with both boundary conventions
    measured on each.

    Returns (census_rows, split_rows, delta_rows, n_phases_built, degeneracies).
    """
    phases_macro = [(pts_macro[i][0], pts_macro[i + 1][0],
                     'bear' if pts_macro[i][1] == 'peak' else 'bull')
                    for i in range(len(pts_macro) - 1)]
    final_pts = merge_meso(prices, pts_macro, pts_meso)
    phases = build_phases(final_pts, pts_macro)
    logger.info(f"[{arm}][{ticker}] {algorithm}: {len(phases_macro)} MACRO phases -> "
                f"{len(phases)} phases after the MESO merge.")

    split_rows = []
    for i in range(len(pts_macro) - 1):
        A = pts_macro[i]
        B = pts_macro[i + 1]
        dur_macro = prices.index.get_loc(B[0]) - prices.index.get_loc(A[0])
        if dur_macro > MERGE_MACRO_DURATION:
            sub_ids = [final_id for final_id, p in enumerate(phases)
                       if p[0] >= A[0] and p[1] <= B[0]]
            split_rows.append({
                'ticker': ticker, 'macro_phase_id': i, 'macro_T_days': dur_macro,
                'n_meso_splits_applied': max(0, len(sub_ids) - 1),
                'resulting_subphase_ids': str(sub_ids),
            })

    q_ref_global = (returns > 0).mean()
    census_rows = []
    delta_rows = []
    degeneracies = {'sharpe_non_finite': 0, 'q_phase_degenerate': 0, 'T_days_zero': 0,
                    'sharpe_below_1e-12': 0, 'ann_vol_zero': 0}

    for pid, (st, en, ptype, source_scale) in enumerate(phases):
        idx_st = returns.index.get_loc(st)
        idx_en = returns.index.get_loc(en)

        # INCLUSIVE CONVENTION -- the boundary return counted in both adjacent
        # phases. This is the arm v87 L392 describes as the defect it corrected;
        # it is measured here so that C4 can price the correction, never used as
        # the census.
        r_b = returns.loc[st:en]
        T_b = len(r_b)
        ann_vol_b = r_b.std(ddof=1) * np.sqrt(252)
        sr_b = (r_b.mean() * 252) / ann_vol_b if ann_vol_b != 0 else 0
        q_b = (r_b > 0).mean()
        kl_b = compute_kl_sign(q_b, q_ref_global)
        add_b = (504 * np.log(1 / ALPHA)) / (sr_b ** 2) if sr_b != 0 else np.inf
        det_b = add_b < T_b

        # STRICT POST-ONSET CONVENTION (v87 L392, imperative): the return dated
        # at the turning point closes the phase it ends.
        r_a = returns.iloc[idx_st + 1: idx_en + 1]
        T_a = idx_en - idx_st

        # The delivered script reads `if T_a < 2: continue` here (l.321), which
        # would drop a phase silently and tear the partition C1 asserts. It never
        # fires on this data. A skipped phase is precisely what C1 exists to
        # catch, so the branch stops the run instead of hiding.
        if T_a < 2:
            logger.error(f"[{arm}][{ticker}] phase {pid} ({st.date()} -> {en.date()}) has "
                         f"T_days = {T_a} < 2 under the post-onset convention. The delivered "
                         f"script skipped such a phase and tore the partition; this run stops.")
            sys.exit(1)

        ann_ret_a = r_a.mean() * 252
        ann_vol_a = r_a.std(ddof=1) * np.sqrt(252)
        sr_a = ann_ret_a / ann_vol_a if ann_vol_a != 0 else 0
        q_a = (r_a > 0).mean()
        delta_q_a = q_a - q_ref_global
        kl_a = compute_kl_sign(q_a, q_ref_global)
        add_a = (504 * np.log(1 / ALPHA)) / (sr_a ** 2) if sr_a != 0 else np.inf
        det_a = add_a < T_a

        # C5, counted even at zero. A non-finite Sharpe or a degenerate sign rate
        # reaching a detectability flag would count the phase out of budget
        # WITHOUT measurement -- `NaN < T_days` is False -- which is the degraded
        # path the specification's asymmetry rule targets on a claim the defect would
        # inflate.
        if not np.isfinite(sr_a):
            degeneracies['sharpe_non_finite'] += 1
        if q_a in (0.0, 1.0):
            degeneracies['q_phase_degenerate'] += 1
        if T_a == 0:
            degeneracies['T_days_zero'] += 1
        if abs(sr_a) < 1e-12:
            degeneracies['sharpe_below_1e-12'] += 1
        if ann_vol_a == 0:
            degeneracies['ann_vol_zero'] += 1

        delta_rows.append({
            'ticker': ticker, 'phase_id': pid,
            'start_date': st.strftime('%Y-%m-%d'), 'end_date': en.strftime('%Y-%m-%d'),
            'T_days_before': T_b, 'T_days_after': T_a,
            'r_boundary': r_b.iloc[0],
            'sharpe_before': sr_b, 'sharpe_after': sr_a,
            'ADD_min_before': add_b, 'ADD_min_after': add_a,
            'q_phase_before': q_b, 'q_phase_after': q_a,
            'kl_sign_before': kl_b, 'kl_sign_after': kl_a,
            'detectable_before': det_b, 'detectable_after': det_a,
            'flipped': det_b != det_a,
        })

        census_rows.append({
            'ticker': ticker, 'phase_id': pid, 'phase_type': ptype,
            'start_date': st.strftime('%Y-%m-%d'), 'end_date': en.strftime('%Y-%m-%d'),
            'T_days': T_a, 'ann_return': ann_ret_a, 'ann_vol': ann_vol_a, 'sharpe': sr_a,
            'q_ref': q_ref_global, 'q_phase': q_a, 'delta_q': delta_q_a, 'alpha': ALPHA,
            'ADD_min_days': add_a, 'detectable_flag': det_a,
            'base_episode_label': get_episodes(st, en, ptype), 'source_scale': source_scale,
            'dating_algorithm': algorithm,
        })

    return census_rows, split_rows, delta_rows, len(phases), degeneracies


CENSUS_COLUMNS = ['ticker', 'phase_id', 'phase_type', 'start_date', 'end_date', 'T_days',
                  'ann_return', 'ann_vol', 'vol_pct', 'sharpe', 'q_ref', 'q_phase', 'delta_q',
                  'alpha', 'ADD_min_days', 'detectable_flag', 'pathology_class', 'episode_label',
                  'source_scale', 'dating_algorithm']

DELTA_COLUMNS = ['ticker', 'phase_id', 'start_date', 'end_date', 'T_days_before', 'T_days_after',
                 'r_boundary', 'sharpe_before', 'sharpe_after', 'ADD_min_before', 'ADD_min_after',
                 'q_phase_before', 'q_phase_after', 'kl_sign_before', 'kl_sign_after',
                 'detectable_before', 'detectable_after', 'flipped']

SPLIT_COLUMNS = ['ticker', 'macro_phase_id', 'macro_T_days', 'n_meso_splits_applied',
                 'resulting_subphase_ids']


def finalise_census(per_ticker_rows):
    """
    Per-ticker volatility percentile, pathology class and refined episode label,
    then the strict column order. The percentile is ranked WITHIN a ticker, as
    the delivered script does (l.357).
    """
    frames = []
    for rows in per_ticker_rows:
        frame = pd.DataFrame(rows)
        frame['vol_pct'] = frame['ann_vol'].rank(pct=True, method='first')
        frame['pathology_class'] = classify_pathology(frame['vol_pct'], frame['sharpe'])
        frame['episode_label'] = refined_episode_label(frame)
        frame = frame.drop(columns=['base_episode_label'])
        frames.append(frame)
    census = pd.concat(frames, ignore_index=True)
    return census[CENSUS_COLUMNS]


def turning_point_index(prices, points):
    """Positional index of each turning point, with its peak/trough type."""
    return [(prices.index.get_loc(p[0]), p[1]) for p in points]


def concordance(reference, other, tolerance):
    """
    Fraction of `reference` turning points that have a turning point of the SAME
    type in `other` within `tolerance` trading days. Returns (matched, total).
    """
    matched = 0
    for idx, kind in reference:
        if any(kind == other_kind and abs(idx - other_idx) <= tolerance
               for other_idx, other_kind in other):
            matched += 1
    return matched, len(reference)


def main():
    parser = argparse.ArgumentParser(
        description="R16 (a) -- retrospective regime dating and census of four ETF streams")
    parser.add_argument("--dating", choices=("all",) + ARMS, default="all",
                        help="Dating arm to compute and persist. `all` (the default) computes and "
                             "persists the three arms in one process; a single arm writes that "
                             "arm's CSV only, byte-identical to what `all` wrote. The canonical "
                             "arm is the published 66-phase configuration and is what the default "
                             "run writes to R16_regime_census.csv.")
    args = parser.parse_args()

    RESULTS_DIR = BASE_DIR / "results" / "R16_regime_census"
    DATA_DIR = RESULTS_DIR / "data"
    TABLES_DIR = RESULTS_DIR / "tables"
    LOGS_DIR = BASE_DIR / "logs" / "R16_regime_census"
    for d in (DATA_DIR, TABLES_DIR, LOGS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(LOGS_DIR / "exp_R16_regime_census_a.log", "exp_R16_regime_census_a")
    if not verify_hash_seed(logger):
        sys.exit(1)
    log_environment(logger, ["numpy", "pandas", "scipy", "pytest"])
    t0 = time.time()

    logger.info("R16 (a) dates the bull/bear phases of SPY, PFF, VNQ and BWX over 2000-2025 and "
                "writes the census that carries v87's most-cited empirical claim: 80% of dated "
                "directional episodes out of budget (L57, L87, L329, L374).")
    logger.info("Stochastic surface: NONE. The delivered scripts call set_seed(42) and neither "
                "draws a random number -- the dating filters, the Sharpe ratios, the Bernoulli "
                "divergences and the detectability flags are deterministic functions of the four "
                "price series. There is therefore no seed-derivation surface to migrate to a "
                "128-bit SeedSequence, and no unused helper is added to suggest otherwise.")
    logger.info("Figure verdict: R16 renders no figure. v87's census paragraphs L329 and L331 "
                "carry no \\includegraphics and reference only \\ref{fig:oracle_frontier}, which "
                "belongs to R01's look-ahead oracle backtest.")
    logger.info(f"Dating arm requested: --dating {args.dating}. Both datings are computed for "
                f"every ticker on every run by construction: check_sanity cannot be evaluated "
                f"without the Pagan-Sossounov points, and the canonical arm cannot be built "
                f"without the Lunde-Timmermann points.")

    check_source_identity(logger)

    # =====================================================================
    # DATING: BOTH ALGORITHMS, EVERY TICKER, EVERY RUN
    # =====================================================================
    series = {}
    prices = {}
    ps_macro = {}
    ps_meso = {}
    lt_macro = {}
    sanity = {}
    for ticker in TICKERS:
        r = load_returns(ticker)
        series[ticker] = r
        prices[ticker] = r.cumsum()
        logger.info(f"[{ticker}] Ingestion OK | {len(r)} trading days | "
                    f"{r.index[0].strftime('%Y-%m-%d')} to {r.index[-1].strftime('%Y-%m-%d')}")
        ps_macro[ticker] = pagan_sossounov(prices[ticker], **MACRO_PARAMS)
        ps_meso[ticker] = pagan_sossounov(prices[ticker], **MESO_PARAMS)
        lt_macro[ticker] = lunde_timmermann(prices[ticker], **LT_PARAMS)
        phases_ps = [(ps_macro[ticker][i][0], ps_macro[ticker][i + 1][0],
                      'bear' if ps_macro[ticker][i][1] == 'peak' else 'bull')
                     for i in range(len(ps_macro[ticker]) - 1)]
        sanity[ticker] = check_sanity(phases_ps)

    logger.info("check_sanity on the Pagan-Sossounov MACRO dating, evaluated on ALL FOUR tickers: "
                + ", ".join(f"{t} = {sanity[t]}" for t in TICKERS)
                + ". The delivered script initialises `sanity_ok = True` and reassigns it only "
                  "inside its `if ticker == 'SPY'` branch (l.233), so PFF, VNQ and BWX are never "
                  "tested by it. All four fail the same check.")
    for ticker in TICKERS:
        if not sanity[ticker]:
            logger.warning(f"[{ticker}] check_sanity fails on the Pagan-Sossounov MACRO dating: "
                           f"{len(ps_macro[ticker])} turning points, "
                           f"{len(ps_macro[ticker]) - 1} phases. Under --dating canonical the "
                           f"Lunde-Timmermann substitution applies to SPY only; under "
                           f"--dating symmetric it applies here too; under --dating strict_ps it "
                           f"never applies.")
    logger.info("SPY substitution, canonical arm: check_sanity fails on the Pagan-Sossounov MACRO "
                "dating (Pagan-Sossounov yields 8 phases and censors the COVID crash at "
                "min_phase = 84), so the canonical arm substitutes "
                "lunde_timmermann(lambda_1=0.15, lambda_2=0.15) for SPY's MACRO stream. This is "
                "the delivered script's line 237 and is named in line 3 of the vendored "
                "data/reference/R16/Priorite_16_regime_census.log. It is carried into the "
                "`dating_algorithm` column of every census row and stamped in the counterfactual "
                "filenames.")

    # =====================================================================
    # C6 -- CONCORDANCE OF THE TWO DATINGS, DESCRIPTIVE, NOT A GATE
    # =====================================================================
    logger.info("C6 concordance of the two datings. Turning-point agreement between "
                "Pagan-Sossounov and Lunde-Timmermann per ticker, at exact date and on a "
                f"tolerance ladder derived from the filters' own resolution "
                f"{CONCORDANCE_TOLERANCES} trading days (0 = exact, "
                f"{MESO_PARAMS['min_phase']} = MESO min_phase, {MACRO_PARAMS['min_phase']} = "
                f"MACRO min_phase). Never tuned. Reported with a Wilson interval, DESCRIPTIVE "
                "ONLY: two dating algorithms do not coincide, and a gate on "
                "their agreement would ring empty.")
    concordance_records = []
    for ticker in TICKERS:
        ps_pts = turning_point_index(prices[ticker], ps_macro[ticker])
        lt_pts = turning_point_index(prices[ticker], lt_macro[ticker])
        for tolerance in CONCORDANCE_TOLERANCES:
            m_ps, n_ps = concordance(ps_pts, lt_pts, tolerance)
            m_lt, n_lt = concordance(lt_pts, ps_pts, tolerance)
            lo_ps, hi_ps = wilson_score_interval(m_ps, n_ps)
            lo_lt, hi_lt = wilson_score_interval(m_lt, n_lt)
            concordance_records.append((ticker, tolerance, m_ps, n_ps, m_lt, n_lt))
            logger.info(f"C6 [{ticker}] tolerance {tolerance:>3d} d: PS->LT {m_ps}/{n_ps} = "
                        f"{(m_ps / n_ps if n_ps else float('nan')):.3f} Wilson "
                        f"[{lo_ps:.3f}, {hi_ps:.3f}] | LT->PS {m_lt}/{n_lt} = "
                        f"{(m_lt / n_lt if n_lt else float('nan')):.3f} Wilson "
                        f"[{lo_lt:.3f}, {hi_lt:.3f}]")
    for tolerance in CONCORDANCE_TOLERANCES:
        rung = [row for row in concordance_records if row[1] == tolerance]
        m_ps, n_ps = sum(r[2] for r in rung), sum(r[3] for r in rung)
        m_lt, n_lt = sum(r[4] for r in rung), sum(r[5] for r in rung)
        lo_ps, hi_ps = wilson_score_interval(m_ps, n_ps)
        lo_lt, hi_lt = wilson_score_interval(m_lt, n_lt)
        logger.info(f"C6 [all four] tolerance {tolerance:>3d} d: PS->LT {m_ps}/{n_ps} = "
                    f"{m_ps / n_ps:.3f} Wilson [{lo_ps:.3f}, {hi_ps:.3f}] | LT->PS {m_lt}/{n_lt} "
                    f"= {m_lt / n_lt:.3f} Wilson [{lo_lt:.3f}, {hi_lt:.3f}]. Pooled across "
                    f"tickers for description only: the four streams are not exchangeable and "
                    f"the pooled interval assumes an independence the turning points of one "
                    f"price series do not have.")
    logger.info("C6 RESTATEMENT, required: under the canonical arm SPY's census IS the "
                "Lunde-Timmermann dating, so SPY's concordance with the census is 100% BY "
                "CONSTRUCTION and is an identity, not corroboration. The figures above compare "
                "the two ALGORITHMS on SPY's prices and are informative in that sense only. "
                "PFF, VNQ and BWX are the three tickers where Pagan-Sossounov survives into the "
                "canonical census and where this control carries information about the dating "
                "that the census actually uses.")

    # =====================================================================
    # THE ARMS
    # =====================================================================
    arms_to_run = list(ARMS) if args.dating == "all" else [args.dating]
    logger.info(f"Arms computed and persisted on this invocation: {arms_to_run}. No exit gate is "
                "placed on any of these paths: the 66-phase canonical configuration is the "
                "repository's baseline, and the counterfactual arms are measured and reported "
                "but gate nothing.")

    census = {}
    splits = {}
    deltas = {}
    phases_built = {}
    for arm in arms_to_run:
        per_ticker = []
        split_rows = []
        delta_rows = []
        built = {}
        degeneracies = {}
        for ticker in TICKERS:
            pts_macro, algorithm = dating_for_arm(arm, ticker, sanity[ticker],
                                                  ps_macro[ticker], lt_macro[ticker])
            rows, splits_t, deltas_t, n_built, degen = census_for_ticker(
                arm, ticker, series[ticker], prices[ticker], pts_macro, algorithm,
                ps_meso[ticker], logger)
            if not rows:
                logger.error(f"[{arm}][{ticker}] produced no phase. A ticker absent from the "
                             f"census would silently change every denominator downstream.")
                sys.exit(1)
            per_ticker.append(rows)
            split_rows.extend(splits_t)
            delta_rows.extend(deltas_t)
            built[ticker] = n_built
            for key, value in degen.items():
                degeneracies[key] = degeneracies.get(key, 0) + value

        census[arm] = finalise_census(per_ticker)
        phases_built[arm] = built
        splits[arm] = pd.DataFrame(split_rows)[SPLIT_COLUMNS]
        deltas[arm] = pd.DataFrame(delta_rows)[DELTA_COLUMNS]
        counts = census[arm]['ticker'].value_counts().reindex(TICKERS).to_dict()
        algos = (census[arm].groupby('ticker')['dating_algorithm'].first()
                 .reindex(TICKERS).to_dict())
        logger.info(f"[{arm}] {len(census[arm])} phases: " + ", ".join(
            f"{t} {counts[t]} ({algos[t]})" for t in TICKERS))

        # C5 -- DEGENERACIES, COUNTED EVEN AT ZERO, ON EVERY ARM
        logger.info(f"C5 degeneracies on the {arm} arm, counted even at zero: " + ", ".join(
            f"{k} = {v}" for k, v in sorted(degeneracies.items()))
            + ". Deterministic; trigger probability 0. A non-finite `sharpe` or `kl` reaching a "
              "detectability flag counts the phase out of budget WITHOUT measurement, because "
              "`NaN < T_days` is False, and stops the run.")
        reached = census[arm][~np.isfinite(census[arm]['sharpe'])]
        if len(reached) > 0:
            logger.error(f"C5 FAILED on the {arm} arm: {len(reached)} phases carry a non-finite "
                         f"`sharpe` and their detectability flag is therefore decided without "
                         f"measurement.")
            sys.exit(1)
        n_inf_add = int((~np.isfinite(census[arm]['ADD_min_days'])).sum())
        n_degen_q = int(census[arm]['q_phase'].isin([0.0, 1.0]).sum())
        n_zero_T = int((census[arm]['T_days'] == 0).sum())
        logger.info(f"C5 [{arm}] persisted-column recount: ADD_min_days non-finite = {n_inf_add} "
                    f"(the `sharpe == 0 -> np.inf` branch), q_phase in {{0, 1}} = {n_degen_q}, "
                    f"T_days == 0 = {n_zero_T}. Their defined treatment: an infinite floor is "
                    f"never below T_days, so such a phase counts out of budget by measurement "
                    f"rather than by default; a degenerate q_phase is clipped to [1e-6, 1-1e-6] "
                    f"by compute_kl_sign before the Bernoulli divergence.")

    # =====================================================================
    # C1 -- PARTITION, ASSERTED AND NOT OBSERVED
    # =====================================================================
    logger.info("C1 partition of the return series. Per ticker: phases contiguous "
                "(end_date[k] == start_date[k+1]), sum(T_days) == idx(last end) - idx(first "
                "start), and no phase dropped between the dating and the census. The post-onset "
                "convention of v87 L392 imposes it by construction. Deterministic; trigger "
                "probability 0 under a correct implementation. Failure means the double counting "
                "survives, which is a D3 on the 80%.")
    for arm in arms_to_run:
        frame = census[arm]
        gate = (arm == "canonical")
        for ticker in TICKERS:
            sub = frame[frame['ticker'] == ticker].sort_values('phase_id')
            r = series[ticker]
            starts = list(sub['start_date'])
            ends = list(sub['end_date'])
            contiguous = all(ends[k] == starts[k + 1] for k in range(len(sub) - 1))
            idx_start = r.index.get_loc(pd.to_datetime(starts[0]))
            idx_end = r.index.get_loc(pd.to_datetime(ends[-1]))
            sum_t = int(sub['T_days'].sum())
            span = idx_end - idx_start
            head = idx_start
            tail = len(r) - 1 - idx_end
            # No phase dropped: the count the DATING produced against the count
            # that reached the census. The delivered script's `if T_a < 2:
            # continue` is exactly what would separate the two.
            kept = len(sub) == phases_built[arm][ticker]
            ok = contiguous and (sum_t == span) and kept
            message = (f"C1 [{arm}][{ticker}]: {len(sub)} phases of the "
                       f"{phases_built[arm][ticker]} the dating produced (none dropped = {kept}), "
                       f"contiguous = {contiguous}, "
                       f"sum(T_days) = {sum_t}, idx(last end) - idx(first start) = {span}, "
                       f"margin = {sum_t - span}. Head {head} and tail {tail} returns lie outside "
                       f"the covered span: that is the min_edge = {MACRO_PARAMS['min_edge']} "
                       f"censoring of the dating filter, not a hole in the partition.")
            if ok:
                logger.info(message)
            elif gate:
                logger.error(message + " PARTITION TORN.")
                sys.exit(1)
            else:
                logger.warning(message + " Partition torn on a counterfactual arm; reported, "
                                         "not a gate.")
        if gate:
            n_built_total = len(frame)
            if n_built_total != len(deltas[arm]):
                logger.error(f"C1 [{arm}]: {n_built_total} census rows against "
                             f"{len(deltas[arm])} boundary-convention rows. A phase was dropped "
                             f"between the two conventions.")
                sys.exit(1)

    # =====================================================================
    # C7 -- THE EXAMPLE v87 CITES
    # =====================================================================
    # v87 L392: "at troughs following a crash the turning-point return is an
    # outlier (e.g. -18.6% on PFF, 2020-03-18) that both depresses the mean and
    # inflates the variance of the phase that follows, biasing its floor upward."
    if "canonical" in arms_to_run:
        pff = series["PFF"]
        boundary_date = pd.Timestamp("2020-03-18")
        if boundary_date not in pff.index:
            logger.error("C7 FAILED: PFF has no return dated 2020-03-18.")
            sys.exit(1)
        boundary_return = float(pff.loc[boundary_date])
        printed = f"{boundary_return * 100:.1f}%"
        if printed != "-18.6%":
            logger.error(f"C7 FAILED: the PFF return of 2020-03-18 prints as {printed}, where "
                         f"v87 L392 prints -18.6%.")
            sys.exit(1)
        frame = census["canonical"]
        pff_rows = frame[frame['ticker'] == "PFF"].sort_values('phase_id')
        closes = pff_rows[pff_rows['end_date'] == "2020-03-18"]
        opens = pff_rows[pff_rows['start_date'] == "2020-03-18"]
        if len(closes) != 1 or len(opens) != 1:
            logger.error(f"C7 FAILED: 2020-03-18 closes {len(closes)} PFF phases and opens "
                         f"{len(opens)}; the post-onset convention requires exactly one of each.")
            sys.exit(1)
        closing = closes.iloc[0]
        opening = opens.iloc[0]
        delta = deltas["canonical"]
        opening_delta = delta[(delta['ticker'] == "PFF")
                              & (delta['start_date'] == "2020-03-18")].iloc[0]
        if not np.isclose(opening_delta['r_boundary'], boundary_return, rtol=0, atol=0):
            logger.error("C7 FAILED: the boundary return persisted for PFF 2020-03-18 is not the "
                         "series value.")
            sys.exit(1)
        logger.info(f"C7 the example v87 L392 cites. PFF 2020-03-18 log return = "
                    f"{boundary_return!r} -> {printed} at the manuscript's printed precision. It "
                    f"CLOSES phase {int(closing['phase_id'])} "
                    f"({closing['start_date']} -> {closing['end_date']}) and is EXCLUDED from "
                    f"phase {int(opening['phase_id'])} "
                    f"({opening['start_date']} -> {opening['end_date']}), which is what the "
                    f"post-onset convention describes. Excluding it moves that phase's Sharpe "
                    f"{opening_delta['sharpe_before']:.3f} -> {opening_delta['sharpe_after']:.3f} "
                    f"and its floor {opening_delta['ADD_min_before']:.1f} -> "
                    f"{opening_delta['ADD_min_after']:.1f} trading days, i.e. the outlier biases "
                    f"the floor UPWARD, exactly as L392 states. Deterministic; trigger "
                    f"probability 0.")
    else:
        logger.info(f"C7 not applicable under --dating {args.dating}: it reads the canonical arm, "
                    f"which this invocation does not build.")

    # =====================================================================
    # PERSISTENCE
    # =====================================================================
    written = []
    if "canonical" in arms_to_run:
        save_fair_csv(census["canonical"], DATA_DIR / "R16_regime_census.csv")
        save_fair_csv(splits["canonical"], DATA_DIR / "R16_meso_split_report.csv")
        save_fair_csv(deltas["canonical"], DATA_DIR / "R16_boundary_convention_delta.csv")
        written += ["R16_regime_census.csv", "R16_meso_split_report.csv",
                    "R16_boundary_convention_delta.csv"]
    if "strict_ps" in arms_to_run:
        save_fair_csv(census["strict_ps"], DATA_DIR / "R16_regime_census_strict_ps.csv")
        written += ["R16_regime_census_strict_ps.csv"]
    if "symmetric" in arms_to_run:
        save_fair_csv(census["symmetric"], DATA_DIR / "R16_regime_census_symmetric.csv")
        written += ["R16_regime_census_symmetric.csv"]

    # Build artifact paths for manifest
    artifact_paths = [DATA_DIR / name for name in written]
    log_artifact_manifest(logger, artifact_paths, RESULTS_DIR, BASE_DIR)

    expected_rows = {"canonical": 66, "strict_ps": 48, "symmetric": 102}
    for arm in arms_to_run:
        observed = len(census[arm])
        if observed != expected_rows[arm]:
            logger.warning(f"Cardinality displacement on the {arm} arm: {observed} phases against "
                           f"the {expected_rows[arm]} this configuration produced when the port "
                           f"was established. Logged before classification; no "
                           f"parameter is moved toward the expected value.")
        else:
            logger.info(f"Cardinality [{arm}]: {observed} phases, as measured when the port was "
                        f"established.")

    for name in written:
        logger.info(f"SHA-256 {name:<40} : {compute_sha256(DATA_DIR / name)}")

    logger.info(f"Execution completed in {time.time() - t0:.1f}s. No parallelism and no "
                f"stochastic component: R16's worker-count reproducibility axis is vacuous and is "
                f"stated as such rather than staged. The second axis C9 uses instead is arm "
                f"isolation -- `--dating strict_ps` and `--dating symmetric` invoked alone must "
                f"reproduce, byte for byte, the CSVs this default run wrote.")


if __name__ == "__main__":
    main()
