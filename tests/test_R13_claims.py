"""
R13 -- oracle ceiling and the clairvoyant frontier. Acceptance and reporting.

Two kinds of statement live in this file and they are kept apart deliberately.

*Blocking assertions* rest either on a value v87 PRINTS, compared at v87's own
printing precision, which is what preamble S3 fixes as the classification rule,
or on a deterministic relation reimplemented here independently of the
experiment -- the Gaussian log-likelihood-ratio increment written from
`norm.logpdf` rather than from its closed form, the frozen volatility path
rebuilt from the persisted GARCH parameters and re-digested, the four operating
points re-selected from the frontier grid, and the Wilson interval written from
a second algebraic form. NONE rests on a value R13 produced.

*Reporting output* prints the witness comparison, the threshold neighbourhood
of the published operating point and the certification status of the twelve
oracle fits, and asserts nothing.

WHY THE WITNESS IS NOT A BLOCKING ANCHOR. `data/reference/README.md` states it
outright: a witness value is the "published value" column of a D0-D3
comparison, never the anchor of a blocking assertion, because a cell-by-cell
equality gate converts every legitimate correction into a test failure whose
only exit is a widened tolerance. R13's 128-bit re-keying redraws every
Monte-Carlo value of the campaign by construction, so a witness gate here would
fail on the first run.

THE TWO SELF-INVALIDATING ASSERTIONS.

`test_R13_the_published_delay_and_false_alarm_probability_come_from_one_row`
requires that the pair v87 L331 prints -- "3 trading days ... phase false-alarm
probability 1.3%" -- be carried by a SINGLE row of the operating-point table. If
a future change ever splits it across two operating points, this test fires and
the PROSE is what must be revised: a published pair assembled from two rows is a
conflation, not a tolerance to widen.

`test_R13_the_phase_false_alarm_probability_of_L331_does_not_reproduce_at_its_
printed_precision` asserts the DEVIATION `R13-campaign-redraw` itself. If a
later campaign ever brings the regenerated probability back to `1.3%`, it fires,
and what must then change is `docs/DEVIATIONS.md` -- the entry is withdrawn --
not this assertion.
"""

import hashlib
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "results" / "R13_oracle_ceiling" / "data"
FIGURES_DIR = ROOT / "results" / "R13_oracle_ceiling" / "figures"
TABLES_DIR = ROOT / "results" / "R13_oracle_ceiling" / "tables"
REFERENCE_DIR = ROOT / "data" / "reference" / "R13"
CENSUS_DIR = ROOT / "results" / "R16_regime_census" / "data"
SERIES_DIR = ROOT / "data" / "derived_firstrate"

EPISODES = ("E1", "E2", "E3", "E4")
ORACLES = ("V1", "V2", "V3")
DETECTORS = ("D1", "D2")
# The four episodes, anchored on the invariant calendar boundaries R16 dated,
# never on a phase identifier.
EPISODE_DATES = {
    "E1": ("SPY", "2020-02-19", "2020-03-23"),
    "E2": ("SPY", "2009-03-09", "2010-04-23"),
    "E3": ("SPY", "2018-12-24", "2020-02-19"),
    "E4": ("SPY", "2011-04-29", "2011-10-03"),
}
PUBLISHED_OP = "OP2b_ARL0_252"
MATCHED_OP = "OP1_isoFPR5_H"
DELTA_STATIC_GRID = (0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50)
LAMBDA_GRID_POINTS = 200
N_BOOT_FPR = 20000
ISO_FPR_TARGET = 0.05
ARL0_TARGET_OP2 = 20
ARL0_TARGET_OP2B = 252

# =====================================================================
# ANCHORS -- EVERY ONE OF THEM PRINTED IN articleB_whitening_v87.tex
# =====================================================================
# L331: "in a look-ahead oracle backtest ... a CUSUM on returns standardized by
# the conditional volatility of a GARCH(1,1) fitted on a window including the
# crash---parameter oracle, causal filtration---detects it in $3$ trading days
# (likelihood-ratio increments, phase false-alarm probability $1.3\%$) to $16$
# days (standardized-mean CUSUM), against a bootstrap null freezing the same
# volatility path. The mechanism is Jensen's inequality: the path divergence
# ... is $10.6\times$ the unconditional budget ... The same protocol
# discriminates the census flags (2009 recovery detected, 2019 advance missed,
# no alarm on the 2011 correction at the matched operating point) ..."
V87_COVID_DELAY_LR = 3
V87_COVID_FPR_LR_PERCENT = 1.3          # NOT reproduced -- see the D2 test below
V87_COVID_DELAY_STD_MEAN = 16
V87_JENSEN_RATIO = 10.6
V87_COVID_T_DAYS = 23
# Figure 14 caption: "realized delay tau vs. bootstrap FPR_H under a
# frozen-volatility null, for the likelihood-ratio CUSUM and the
# standardized-mean CUSUM ($\delta = 0$ and $\delta_{\mathrm{opt}}$). Dotted
# line: phase end ($T$). The 2020 crash is detected well before $T$ at
# sub-percent false alarms; the 2011 correction is not detected at either
# setting."
V87_VERDICTS = {
    "E1": "detected within the phase at both settings the caption names",
    "E2": "detected",
    "E3": "missed",
    "E4": "no alarm at either setting",
}

# =====================================================================
# TOLERANCES, EACH DERIVED FROM A MECHANISM
# =====================================================================
# The Wilson interval is a closed form in float64 evaluated two ways. The two
# expressions differ by the reassociation of a product of at most five terms,
# bounded by 5 * eps = 1.1e-15 in relative terms; 1e-12 carries three orders of
# margin and is not derived from any observed deviation.
CLOSED_FORM_RTOL = 1e-12
# The likelihood-ratio increment is written here as a DIFFERENCE OF TWO LOG
# DENSITIES, each of magnitude L, where the experiment writes the algebraic
# cancellation of that difference. Subtracting two float64 numbers of magnitude
# L leaves an absolute error of order eps * L, so the admissible gap is
# LLR_CANCELLATION_ULPS * eps * max|logpdf| and nothing else. The constant is
# the number of elementary operations in the two routes, not a fitted margin.
LLR_CANCELLATION_ULPS = 8.0
FLOAT64_EPS = float(np.finfo(np.float64).eps)

MACRO_PREFIX = "RThirteen"
MACRO_HEADER = "% Auto-generated by exp_R13_oracle_ceiling_b.py -- do not edit."


def _read(path):
    assert path.exists(), f"Missing artefact: {path}"
    return pd.read_csv(path, float_precision='round_trip')


@pytest.fixture
def frontier():
    return _read(DATA_DIR / "R13_oracle_frontier.csv")


@pytest.fixture
def operating_points():
    return _read(DATA_DIR / "R13_oracle_operating_points.csv")


@pytest.fixture
def diagnostics():
    return _read(DATA_DIR / "R13_oracle_diagnostics.csv")


@pytest.fixture
def clairvoyant():
    return _read(DATA_DIR / "R13_clairvoyant_floor.csv")


@pytest.fixture
def detector_recovery():
    return _read(DATA_DIR / "R13_detector_recovery.csv")


@pytest.fixture
def qmle_recovery():
    return _read(DATA_DIR / "R13_qmle_recovery.csv")


@pytest.fixture
def census():
    return _read(CENSUS_DIR / "R16_regime_census.csv")


@pytest.fixture
def spy():
    frame = pd.read_csv(SERIES_DIR / "R01_daily_SPY.csv", float_precision='round_trip',
                        index_col='Date', parse_dates=True)
    frame = frame[~frame.index.duplicated(keep='first')].sort_index()
    return frame.dropna(subset=['log_ret'])


@pytest.fixture
def macros():
    path = TABLES_DIR / "R13_claims.tex"
    assert path.exists(), f"Missing artefact: {path}"
    text = path.read_text()
    assert text.endswith("\n"), ("preamble S6 requires every produced text file to end with a "
                                 "newline: docs/sections/*.md and requirements/*.txt are assembled "
                                 "by concatenation, and a missing newline corrupts the result.")
    lines = text.rstrip("\n").split("\n")
    assert lines[0] == MACRO_HEADER, f"Macro header is {lines[0]!r}, expected {MACRO_HEADER!r}"
    out = {}
    for line in lines[1:]:
        if line.startswith("%"):
            continue
        match = re.fullmatch(r"\\newcommand\{\\([A-Za-z]+)\}\{(.*)\}", line)
        assert match is not None, f"Not a bare \\newcommand: {line!r}"
        out[match.group(1)] = match.group(2)
    return out


@pytest.fixture
def witnesses():
    return {name: _read(REFERENCE_DIR / f"protocol_19{key}.csv") for name, key in (
        ("frontier", "a_oracle_frontier"),
        ("operating_points", "b_oracle_operating_points"),
        ("diagnostics", "c_oracle_diagnostics"),
        ("clairvoyant", "d_clairvoyant_floor"),
        ("detector_recovery", "e_detector_recovery"))}


# =====================================================================
# INDEPENDENT REIMPLEMENTATIONS OF THE DERIVED RULES
# =====================================================================

def wilson_score_interval(p, n, z=1.96):
    """
    The Wilson score interval written from the form R02 owns -- margin
    `z * sqrt((p(1-p) + z^2/(4n)) / n) / denom` -- rather than from the form the
    experiment carries, `z * sqrt(p(1-p)/n + z^2/(4n^2)) / denom`. The two are
    the same interval reassociated, which is the point: two routes, one number.
    """
    if n == 0:
        return 0.0, 0.0
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def gaussian_llr_increment(r, mu_0, mu_1, sigma):
    """
    The Gaussian log-likelihood ratio for a mean shift at known variance,
    written as a DIFFERENCE OF TWO LOG DENSITIES.

    The experiment writes its algebraic cancellation,
    `(mu_1 - mu_0) * (r - (mu_0 + mu_1)/2) / sigma^2`, which is what makes `D2`
    the likelihood-ratio CUSUM and `D1` the standardized-mean one. This route
    never performs that cancellation by hand.
    """
    return (stats.norm.logpdf(r, loc=mu_1, scale=sigma)
            - stats.norm.logpdf(r, loc=mu_0, scale=sigma))


def garch_sigma_path(returns, onset_index, end_index, t_days, omega, alpha, beta):
    """
    The V1 oracle volatility path, rebuilt from the persisted GARCH parameters
    and the raw return series: the same 1000-day reference span, the same
    survival cap, the same centring and the same causal recursion the campaign
    specifies, written here from the manuscript's description of the oracle
    rather than by calling the experiment.

    Returns the path over the phase horizon `[onset + 1, onset + 1 + t_days)`,
    which is the vector control C4 digests.
    """
    ref_start = max(0, onset_index - 1000)
    surv_end = min(onset_index + 3 * t_days, onset_index + 750, len(returns) - 1)
    window = returns.iloc[ref_start: surv_end + 1].to_numpy()
    eps = window - np.mean(window)
    sigma2 = np.zeros(len(eps))
    sigma2[0] = np.var(eps)
    for t in range(1, len(eps)):
        sigma2[t] = omega + alpha * eps[t - 1]**2 + beta * sigma2[t - 1]
    sigma = np.sqrt(sigma2)
    relative_onset = onset_index - ref_start
    return sigma[relative_onset + 1: relative_onset + 1 + t_days]


def sha256_of_array(array):
    return hashlib.sha256(np.ascontiguousarray(array, dtype=np.float64).tobytes()).hexdigest()


def rounds_to(value, printed, decimals):
    """v87's printing precision is the classification rule of preamble S3."""
    return round(float(value), decimals) == round(float(printed), decimals)


def cell_key(frame):
    """The grouping that isolates one threshold sweep: episode, oracle, detector, delta."""
    return frame.groupby(['episode_id', 'sigma_oracle', 'detector', 'delta'], dropna=False)


# =====================================================================
# BLOCKING ASSERTIONS -- STRUCTURE AND SCHEMA
# =====================================================================

def test_R13_every_artefact_the_prompt_lists_exists_with_its_prescribed_schema(
        frontier, operating_points, diagnostics, clairvoyant, detector_recovery, qmle_recovery):
    """
    The cardinalities are the EXPERIMENTAL DESIGN v87 section 1 fixes -- four
    episodes, three oracles, two detectors with a ten-point dead-band grid on
    one of them, 200 thresholds, four operating points -- and not measurements.
    """
    n_cells = len(EPISODES) * len(ORACLES) * (len(DELTA_STATIC_GRID) + 1 + 1)
    assert len(frontier) == n_cells * LAMBDA_GRID_POINTS == 26400
    assert len(operating_points) == n_cells * 4 == 528
    assert len(diagnostics) == len(EPISODES) * len(ORACLES) == 12
    assert len(clairvoyant) == len(EPISODES) * len(ORACLES) == 12
    assert len(detector_recovery) == 16
    assert len(qmle_recovery) == 88
    assert (FIGURES_DIR / "fig14_oracle_frontier.png").exists(), (
        "v87 renders fig:oracle_frontier as Fig24_Oracle_Frontier.png; the repository names it "
        "after the figure number the manuscript prints, which is 14.")
    for column in ('detector_family', 'arl0_censored_frac', 'lambda_grid_rescaled'):
        assert column in frontier.columns
    for column in ('detector_family', 'arl0_censored_frac', 'oracle_verdict', 'ADD_min_census',
                   'detectable_flag_census'):
        assert column in operating_points.columns
    assert 'sigma_path_sha256' in diagnostics.columns
    assert 'n_star_realized_below_analytic' in clairvoyant.columns
    assert 'anticonservative' not in clairvoyant.columns, (
        "the delivered script writes the literal `'anticonservative': True` into every row and "
        "never computes it; the port replaces it with the comparison it names")
    assert sorted(operating_points['operating_point'].unique()) == sorted(
        [MATCHED_OP, 'OP2_ARL0_20', PUBLISHED_OP, 'OP3_breakeven'])
    assert sorted(frontier['episode_id'].unique()) == sorted(EPISODES)
    assert sorted(frontier['sigma_oracle'].unique()) == sorted(ORACLES)


def test_R13_the_detector_labels_carry_the_families_the_manuscript_fixes(
        frontier, operating_points, detector_recovery):
    """
    The R13 prompt's notation section glosses `D1 / D2` as "likelihood-ratio and
    standardized-mean". v87's Figure 14 caption attaches `delta = 0` and
    `delta_opt` to the STANDARDIZED-MEAN CUSUM, and only `D1` carries a
    dead-band grid -- which is the structural evidence for the opposite
    assignment. Preamble S1 makes the manuscript the specification.
    """
    for frame in (frontier, operating_points, detector_recovery):
        mapping = frame.groupby('detector')['detector_family'].unique()
        assert list(mapping.loc['D1']) == ['standardized_mean']
        assert list(mapping.loc['D2']) == ['likelihood_ratio']
    d1 = frontier[frontier['detector'] == 'D1']
    d2 = frontier[frontier['detector'] == 'D2']
    assert d2['delta'].isna().all(), (
        "the likelihood-ratio increment carries no dead band: the reflection is at zero and "
        "delta is undefined, which is why the witness writes NaN")
    for episode in EPISODES:
        for oracle in ORACLES:
            deltas = d1[(d1['episode_id'] == episode)
                        & (d1['sigma_oracle'] == oracle)]['delta'].unique()
            assert len(deltas) == len(DELTA_STATIC_GRID) + 1, (
                "the standardized-mean CUSUM carries the nine static dead bands plus delta_opt, "
                "which is the grid v87's caption names two points of")
            for value in DELTA_STATIC_GRID:
                assert np.isclose(deltas, value, rtol=0.0, atol=0.0).any()


# =====================================================================
# BLOCKING ASSERTIONS -- C1, THE PAIR AND ITS SINGLE ROW
# =====================================================================

def test_R13_the_published_delay_and_false_alarm_probability_come_from_one_row(operating_points):
    """
    THE FIRST SELF-INVALIDATING ASSERTION. v87 L331 prints "$3$ trading days
    (likelihood-ratio increments, phase false-alarm probability $1.3\\%$)" as two
    quantities of ONE operating point. A pair assembled from two operating
    points would be a conflation and a D3, and the prose -- not this test --
    would be what has to change.
    """
    rows = operating_points[(operating_points['episode_id'] == "E1")
                            & (operating_points['detector'] == "D2")
                            & (operating_points['sigma_oracle'] == "V1")
                            & (operating_points['operating_point'] == PUBLISHED_OP)]
    assert len(rows) == 1, (
        f"the pair v87 L331 prints is carried by {len(rows)} rows, not one; a published quantity "
        f"assembled from two operating points is a conflation")
    row = rows.iloc[0]
    assert bool(row['op_attainable'])
    assert int(row['tau_realized_days']) == V87_COVID_DELAY_LR
    assert np.isfinite(row['FPR_H'])
    assert bool(row['oracle_certified']) and not bool(row['oracle_contaminated'])
    assert int(row['T_days_phase']) == V87_COVID_T_DAYS
    assert row['oracle_verdict'] == 'detected_within_T'


# =====================================================================
# BLOCKING ASSERTIONS -- THE NUMERALS v87 PRINTS
# =====================================================================

def test_R13_the_two_covid_detection_delays_v87_prints_reproduce(operating_points):
    """
    L331: "detects it in $3$ trading days (likelihood-ratio increments ...) to
    $16$ days (standardized-mean CUSUM)". Both are integers in trading days and
    both are read at the same operating point, `OP2b_ARL0_252` -- one false
    alarm per trading year, which is the calibration the surrounding sentence
    uses for the sign floor.
    """
    e1 = operating_points[(operating_points['episode_id'] == "E1")
                          & (operating_points['sigma_oracle'] == "V1")
                          & (operating_points['operating_point'] == PUBLISHED_OP)]
    lr = e1[e1['detector'] == "D2"].iloc[0]
    assert int(lr['tau_realized_days']) == V87_COVID_DELAY_LR
    std_mean = e1[(e1['detector'] == "D1")
                  & np.isclose(e1['delta'].to_numpy(dtype=float), 0.0, rtol=0.0, atol=0.0)].iloc[0]
    assert int(std_mean['tau_realized_days']) == V87_COVID_DELAY_STD_MEAN
    assert lr['tau_realized_days'] < std_mean['tau_realized_days'], (
        "L331 reads '3 trading days ... to 16 days' as a range whose fast end is the "
        "likelihood-ratio arm; the order of the two arms is what the sentence asserts")
    assert std_mean['tau_realized_days'] < V87_COVID_T_DAYS, (
        "the Figure 14 caption says the 2020 crash is detected well before T on both arms")


def test_R13_the_jensen_ratio_v87_prints_reproduces_and_is_specific_to_one_oracle(diagnostics):
    """
    L331: "the path divergence $\\sum_t \\Delta^2/(2\\sigma_t^2)$ is
    $10.6\\times$ the unconditional budget". The ratio has no Monte Carlo in it:
    it is a deterministic function of the return series and the oracle fit.
    """
    e1 = diagnostics[diagnostics['episode_id'] == "E1"]
    best = e1.loc[e1['jensen_ratio'].idxmax()]
    assert best['sigma_oracle'] == "V1"
    assert rounds_to(best['jensen_ratio'], V87_JENSEN_RATIO, 1)
    assert bool(best['oracle_certified'])
    others = e1[e1['sigma_oracle'] != "V1"]['jensen_ratio']
    assert (others < 2.0).all(), (
        "the published 10.6x is SPECIFIC to the parametric oracle: the two realized-volatility "
        "oracles of the same episode price the same phase near 1.6x, and a reader who takes the "
        "ratio as a property of the episode has misread it")
    # The ratio is KL_path over KL_corollary and nothing else.
    assert np.allclose(diagnostics['jensen_ratio'],
                       diagnostics['KL_path'] / diagnostics['KL_corollary'],
                       rtol=CLOSED_FORM_RTOL, atol=0.0)


def test_R13_the_phase_false_alarm_probability_of_L331_does_not_reproduce_at_its_printed_precision(
        operating_points, macros):
    """
    THE SECOND SELF-INVALIDATING ASSERTION, and the deviation
    `R13-campaign-redraw` is written around it.

    v87 L331 prints the phase false-alarm probability of the 3-day detection as
    $1.3\\%$. The 128-bit re-keying redraws the 20,000-replicate bootstrap and
    the 5,000-replicate ARL0 null that selects the threshold, and the
    regenerated probability does NOT round to 1.3% at v87's printed precision.

    If a later campaign ever brings it back to 1.3%, this test fires, and what
    must then change is docs/DEVIATIONS.md -- the entry is withdrawn -- never
    this assertion. The qualitative claim the numeral supports is asserted
    alongside it and DOES hold.
    """
    row = operating_points[(operating_points['episode_id'] == "E1")
                           & (operating_points['detector'] == "D2")
                           & (operating_points['sigma_oracle'] == "V1")
                           & (operating_points['operating_point'] == PUBLISHED_OP)].iloc[0]
    observed = 100.0 * float(row['FPR_H'])
    assert not rounds_to(observed, V87_COVID_FPR_LR_PERCENT, 1), (
        f"the regenerated phase false-alarm probability is {observed:.4f}%, which now rounds to "
        f"v87's printed 1.3%. The deviation `R13-campaign-redraw` is registered on the fact that "
        f"it does NOT; if it now does, the register entry is what must be withdrawn.")
    assert macros['RThirteenCovidFprLR'] == f"{observed:.1f}\\%"
    # The qualitative claim survives: a few-day detection at a low single-digit
    # false-alarm probability, well inside the sentence's own range.
    assert 0.0 < observed < 2.0
    assert int(row['tau_realized_days']) == V87_COVID_DELAY_LR, (
        "the delay the sentence prints is unmoved; only the probability beside it is")


def test_R13_the_census_verdicts_of_L331_reproduce_at_the_matched_operating_point(
        operating_points, diagnostics):
    """
    L331: "The same protocol discriminates the census flags (2009 recovery
    detected, 2019 advance missed, no alarm on the 2011 correction at the
    matched operating point)".

    "The matched operating point" is the iso-FPR 5% point, which is NOT the
    calibration behind the three numerals earlier in the same sentence. The
    verdicts are read on the standardized-mean CUSUM at the two settings v87's
    Figure 14 caption names, `delta = 0` and `delta_opt`.
    """
    def verdicts(episode):
        sub = operating_points[(operating_points['episode_id'] == episode)
                               & (operating_points['sigma_oracle'] == "V1")
                               & (operating_points['detector'] == "D1")
                               & (operating_points['operating_point'] == MATCHED_OP)]
        d_opt = float(diagnostics[(diagnostics['episode_id'] == episode)
                                  & (diagnostics['sigma_oracle'] == "V1")].iloc[0]['delta_opt'])
        zero = sub[np.isclose(sub['delta'].to_numpy(dtype=float), 0.0,
                              rtol=0.0, atol=0.0)].iloc[0]
        opt = sub[np.isclose(sub['delta'].to_numpy(dtype=float), d_opt,
                             rtol=0.0, atol=0.0)].iloc[0]
        return zero, opt

    # Every iso-FPR row is at or below the 5% the operating point names.
    iso = operating_points[(operating_points['operating_point'] == MATCHED_OP)
                           & operating_points['op_attainable']]
    assert (iso['FPR_H'] <= ISO_FPR_TARGET).all()

    zero, opt = verdicts("E2")
    assert zero['oracle_verdict'] == 'detected_within_T', (
        "L331: '2009 recovery detected'. It is detected at delta = 0 and the verdict is "
        "setting-dependent, which the macro body carries in full")
    assert int(zero['tau_realized_days']) < int(zero['T_days_phase'])

    zero, opt = verdicts("E3")
    assert zero['oracle_verdict'] != 'detected_within_T'
    assert opt['oracle_verdict'] != 'detected_within_T', (
        "L331: '2019 advance missed'. Neither named setting alarms inside the phase")

    zero, opt = verdicts("E4")
    assert zero['oracle_verdict'] == 'no_alarm'
    assert opt['oracle_verdict'] == 'no_alarm', (
        "L331: 'no alarm on the 2011 correction at the matched operating point', and the "
        "Figure 14 caption: 'the 2011 correction is not detected at either setting'")

    zero, opt = verdicts("E1")
    assert zero['oracle_verdict'] == 'detected_within_T'
    assert opt['oracle_verdict'] == 'detected_within_T', (
        "the Figure 14 caption: 'The 2020 crash is detected well before T'")


def test_R13_the_2011_correction_alarms_at_dead_bands_the_caption_does_not_name(
        operating_points, diagnostics):
    """
    The caption is exact BECAUSE it names its two settings. Inside the same
    iso-FPR operating point, larger dead bands DO alarm on the 2011 correction,
    and the sentence at L331 -- which does not name the settings -- is true only
    of the two the caption specifies. That asymmetry is what the deviation
    `R13-negative-control-scope` records, and this test asserts it rather than
    leaving it to prose.
    """
    d_opt = float(diagnostics[(diagnostics['episode_id'] == "E4")
                              & (diagnostics['sigma_oracle'] == "V1")].iloc[0]['delta_opt'])
    sub = operating_points[(operating_points['episode_id'] == "E4")
                           & (operating_points['sigma_oracle'] == "V1")
                           & (operating_points['detector'] == "D1")
                           & (operating_points['operating_point'] == MATCHED_OP)]
    named = np.isclose(sub['delta'].to_numpy(dtype=float), 0.0, rtol=0.0, atol=0.0) | np.isclose(
        sub['delta'].to_numpy(dtype=float), d_opt, rtol=0.0, atol=0.0)
    assert int(named.sum()) == 2
    assert not sub[named]['alarm_within_T'].any()
    alarming = sub[~named & sub['alarm_within_T']]
    assert len(alarming) > 0, (
        "no dead band of the matched operating point alarms on the 2011 correction any more, so "
        "the L331 sentence is now true of the whole grid and `R13-negative-control-scope` has "
        "dissolved; the register entry is what must be withdrawn, not this assertion")
    assert (alarming['FPR_H'] <= ISO_FPR_TARGET).all(), (
        "the alarming settings are INSIDE the iso-FPR band, which is what makes the distinction "
        "one of dead band rather than one of calibration")


# =====================================================================
# BLOCKING ASSERTIONS -- THE DERIVED RULES, AGAINST A SECOND IMPLEMENTATION
# =====================================================================

def test_R13_the_D2_increment_is_the_gaussian_log_likelihood_ratio(diagnostics):
    """
    `D2` is the likelihood-ratio CUSUM and `D1` is the standardized-mean one.
    The claim is checked here on the identity itself: the increment the campaign
    applies to `D2` equals the difference of two Gaussian log densities, written
    without performing the cancellation by hand.
    """
    for row in diagnostics.itertuples(index=False):
        mu_0, mu_1 = float(row.mu_0), float(row.mu_1)
        sigma_grid = np.array([0.25, 0.5, 1.0, 2.0, 4.0]) * float(row.sigma_bar_phase)
        r_grid = mu_0 + np.array([-4.0, -1.0, 0.0, 1.0, 4.0]) * float(row.sigma_bar_phase)
        for sigma in sigma_grid:
            closed_form = (mu_1 - mu_0) * (r_grid - (mu_0 + mu_1) / 2) / sigma**2
            by_densities = gaussian_llr_increment(r_grid, mu_0, mu_1, sigma)
            magnitude = float(np.max(np.abs(stats.norm.logpdf(r_grid, loc=mu_0, scale=sigma))))
            budget = LLR_CANCELLATION_ULPS * FLOAT64_EPS * max(1.0, magnitude)
            assert np.max(np.abs(closed_form - by_densities)) <= budget, (
                f"{row.episode_id}/{row.sigma_oracle} at sigma = {sigma}: the D2 increment is not "
                f"the Gaussian log-likelihood ratio for a mean shift at known variance")
    # And the standardized-mean increment is NOT that ratio, which is the whole
    # content of the label assignment.
    row = diagnostics.iloc[0]
    mu_0, mu_1, sigma = float(row.mu_0), float(row.mu_1), float(row.sigma_bar_phase)
    r_grid = mu_0 + np.array([-2.0, 2.0]) * sigma
    standardized_mean = np.sign(mu_1 - mu_0) * (r_grid - mu_0) / sigma
    assert not np.allclose(standardized_mean,
                           gaussian_llr_increment(r_grid, mu_0, mu_1, sigma), rtol=1e-6)


def test_R13_the_frozen_volatility_path_recomputes_from_the_persisted_parameters(
        diagnostics, census, spy):
    """
    C4 as an acceptance criterion. The Figure 14 caption says the null freezes
    "the same volatility path"; the experiment digests that path and asserts the
    H0 and H1 vectors identical. The digest is meaningless unless the path is
    the one the manuscript describes, so it is rebuilt here from the persisted
    GARCH parameters and the raw return series and re-digested.
    """
    for episode, (ticker, start, end) in EPISODE_DATES.items():
        row = diagnostics[(diagnostics['episode_id'] == episode)
                          & (diagnostics['sigma_oracle'] == "V1")].iloc[0]
        phase = census[(census['ticker'] == ticker) & (census['start_date'] == start)
                       & (census['end_date'] == end)].iloc[0]
        t_days = int(phase['T_days'])
        onset = spy.index.get_loc(pd.Timestamp(start))
        end_index = spy.index.get_loc(pd.Timestamp(end))
        assert end_index - onset == t_days, (
            "the post-onset convention of v87 L392: T_days is idx(end) - idx(start)")
        path = garch_sigma_path(spy['log_ret'], onset, end_index, t_days,
                                float(row['omega']), float(row['alpha']), float(row['beta']))
        assert len(path) == int(row['sigma_path_len']) == t_days
        assert (path > 0).all()
        assert sha256_of_array(path) == row['sigma_path_sha256'], (
            f"{episode}: the volatility path the campaign froze is not the causal GARCH recursion "
            f"the manuscript describes, rebuilt from the parameters the campaign persisted")


def test_R13_the_four_operating_points_are_the_rules_they_name(frontier, operating_points):
    """
    Every operating point re-selected from the frontier grid, by the rule its
    own name states, independently of the selection the campaign performed.

      OP1_isoFPR5_H   first threshold whose bootstrap FPR_H is at or below 5%
      OP2_ARL0_20     first threshold whose ARL0 reaches 20
      OP2b_ARL0_252   first threshold whose ARL0 reaches 252
      OP3_breakeven   LAST threshold whose realized delay is still within T
    """
    checked = 0
    for key, cell in cell_key(frontier):
        episode, oracle, detector, delta = key
        cell = cell.reset_index(drop=True)
        assert len(cell) == LAMBDA_GRID_POINTS
        assert cell['lambda'].is_monotonic_increasing
        fpr = cell['FPR_H'].to_numpy()
        arl = cell['ARL0'].to_numpy()
        tau = cell['tau_realized_days'].to_numpy()
        t_days = int(cell['T_days_phase'].iloc[0])
        expected = {
            MATCHED_OP: np.where(fpr <= ISO_FPR_TARGET)[0],
            'OP2_ARL0_20': np.where(arl >= ARL0_TARGET_OP2)[0],
            PUBLISHED_OP: np.where(arl >= ARL0_TARGET_OP2B)[0],
            'OP3_breakeven': np.where(tau <= t_days)[0],
        }
        rows = operating_points[(operating_points['episode_id'] == episode)
                                & (operating_points['sigma_oracle'] == oracle)
                                & (operating_points['detector'] == detector)]
        rows = rows[rows['delta'].isna()] if pd.isna(delta) else rows[
            np.isclose(rows['delta'].to_numpy(dtype=float), delta, rtol=0.0, atol=0.0)]
        assert len(rows) == 4
        for op_name, indices in expected.items():
            row = rows[rows['operating_point'] == op_name].iloc[0]
            if len(indices) == 0:
                assert not bool(row['op_attainable'])
                assert pd.isna(row['lambda_star'])
                continue
            index = int(indices[-1] if op_name == 'OP3_breakeven' else indices[0])
            assert bool(row['op_attainable'])
            assert row['lambda_star'] == cell['lambda'].iloc[index]
            assert row['FPR_H'] == fpr[index]
            assert (pd.isna(row['ARL0']) and pd.isna(arl[index])) or row['ARL0'] == arl[index]
            assert (pd.isna(row['tau_realized_days']) and np.isnan(tau[index])) or (
                row['tau_realized_days'] == tau[index])
            checked += 1
    assert checked > 0


def test_R13_no_arl0_is_persisted_without_its_censored_fraction(frontier, operating_points):
    """
    C3 as an acceptance criterion. The mean of a right-censored run length is
    biased DOWNWARD, so an ARL0 without its censored fraction understates the
    time between false alarms by an amount the reader cannot bound. The
    mechanism, not an observed count, is what makes this blocking.
    """
    for frame in (frontier, operating_points):
        assert 'arl0_censored_frac' in frame.columns
        finite = frame[frame['ARL0'].notna()]
        assert len(finite) > 0
        assert finite['arl0_censored_frac'].notna().all()
        assert (finite['arl0_censored_frac'] >= 0.0).all()
        assert (finite['arl0_censored_frac'] <= 1.0).all()
    # A surviving mean is censored on at most the declared fraction of
    # replicates, and a suppressed one is NaN rather than published low.
    finite = frontier[frontier['ARL0'].notna()]
    assert (finite['arl0_censored_frac'] <= 0.05).all()
    assert not finite['arl0_right_censored'].any()
    suppressed = frontier[frontier['arl0_right_censored']]
    assert suppressed['ARL0'].isna().all()
    assert (suppressed['arl0_censored_frac'] > 0.05).all()
    # Where the ARL0 null was not run at all, nothing is claimed.
    absent = frontier[~frontier['arl0_available']]
    assert absent['ARL0'].isna().all()
    assert (absent['sigma_oracle'] != "V1").all(), (
        "the ARL0 null is generated from the fitted GARCH parameters and therefore exists on the "
        "parametric oracle alone")


def test_R13_every_wilson_interval_is_the_score_interval_of_its_own_rate(
        frontier, detector_recovery):
    """
    The intervals are recomputed from a second algebraic form of the same
    closed form. Preamble S7 also requires every persisted bound to be clamped
    into [0, 1] before it reaches disk.
    """
    sample = frontier.iloc[::173]
    for row in sample.itertuples(index=False):
        low, high = wilson_score_interval(float(row.FPR_H), N_BOOT_FPR)
        assert abs(row.FPR_H_ci_low - low) <= CLOSED_FORM_RTOL * max(1.0, low)
        assert abs(row.FPR_H_ci_high - high) <= CLOSED_FORM_RTOL * max(1.0, high)
    assert (frontier['FPR_H_ci_low'] >= 0.0).all()
    assert (frontier['FPR_H_ci_high'] <= 1.0).all()
    assert (frontier['FPR_H_ci_low'] <= frontier['FPR_H_ci_high']).all()
    for row in detector_recovery.itertuples(index=False):
        low, high = wilson_score_interval(float(row.detection_rate), int(row.n_replicates))
        assert abs(row.ci_low - low) <= CLOSED_FORM_RTOL * max(1.0, low)
        assert abs(row.ci_high - high) <= CLOSED_FORM_RTOL * max(1.0, high)
        gate_low, gate_high = wilson_score_interval(float(row.detection_rate),
                                                    int(row.n_replicates), float(row.gate_z))
        assert abs(row.gate_ci_low - gate_low) <= CLOSED_FORM_RTOL * max(1.0, gate_low)
        assert abs(row.gate_ci_high - gate_high) <= CLOSED_FORM_RTOL * max(1.0, gate_high)


def test_R13_the_certification_gates_are_equivalence_statements_with_a_null_law(
        qmle_recovery, detector_recovery):
    """
    Preamble S4bis, third corollary: a per-point tolerance read in `max` over
    `m` points is a statistic of an extremum and does not have the distribution
    of its point. The delivered gates were exactly that -- `passes == 88` and a
    conjunction over twelve conditions -- and the port replaces both by
    equivalence statements on statistics that carry a sampling margin.

    The per-cell margins survive in the CSV as description, which is the other
    half of the same rule, and the family-wise trigger probability is logged
    before any result is read.
    """
    assert len(qmle_recovery) == 88
    assert bool(qmle_recovery['converged'].all()), (
        "fit_garch_qmle returns the (0.05, 0.90) initialiser when SLSQP fails, so an unconverged "
        "cell would price the recovery statistic on a value no optimiser produced")
    for name in ('alpha', 'beta'):
        margins = qmle_recovery[f'{name}_margin'].to_numpy()
        assert np.isfinite(margins).all()
        assert np.allclose(margins,
                           qmle_recovery[f'{name}_hat'] - qmle_recovery[f'{name}_target'],
                           rtol=0.0, atol=0.0)
    # The 88 cells are 4 targets x 2 scales x 11 replicates, and the replicate
    # index alone keys the draw: common random numbers across the parameter
    # cells, which is the design SPECS 1.4 requires.
    assert sorted(qmle_recovery['replicate_index'].unique()) == list(range(11))
    assert len(qmle_recovery.groupby(['alpha_target', 'beta_target', 'sigma_target'])) == 8
    assert 'interval_resolves_failure' in detector_recovery.columns
    assert not detector_recovery['interval_resolves_failure'].any(), (
        "a resolved failure stops the run; a row carrying one in a shipped CSV means the gate did "
        "not")
    assert (detector_recovery['gate_level'] == 0.001).all()
    # The gate interval is strictly wider than the reported 95% one, so the gate
    # is more conservative than the description beside it and never the reverse.
    assert (detector_recovery['gate_ci_low'] <= detector_recovery['ci_low'] + 1e-15).all()
    assert (detector_recovery['gate_ci_high'] >= detector_recovery['ci_high'] - 1e-15).all()


def test_R13_the_census_quantities_are_r16s_canonical_arm(operating_points, clairvoyant, census):
    """
    C6 as an acceptance criterion. R13 consumes `ADD_min_days` and
    `detectable_flag` of the DEFAULT-RUN CANONICAL census, under the names
    `ADD_min_census` and `detectable_flag_census` that AUDIT_R16.md section 5
    fixes. Read at round_trip on both sides.
    """
    for episode, (ticker, start, end) in EPISODE_DATES.items():
        phase = census[(census['ticker'] == ticker) & (census['start_date'] == start)
                       & (census['end_date'] == end)]
        assert len(phase) == 1, f"{episode} does not resolve to one census phase"
        phase = phase.iloc[0]
        for frame in (operating_points, clairvoyant):
            sub = frame[frame['episode_id'] == episode]
            assert len(sub) > 0
            assert (sub['ADD_min_census'] == phase['ADD_min_days']).all()
            assert (sub['phase_id'] == phase['phase_id']).all()
            assert (sub['T_days_phase'] == phase['T_days']).all()
        sub = operating_points[operating_points['episode_id'] == episode]
        assert (sub['detectable_flag_census'] == bool(phase['detectable_flag'])).all()
    # The census flag is its own floor against its own duration, which is the
    # relation R16 owns and R13 must not restate differently.
    for episode, (ticker, start, end) in EPISODE_DATES.items():
        sub = operating_points[operating_points['episode_id'] == episode].iloc[0]
        assert bool(sub['detectable_flag_census']) == (
            float(sub['ADD_min_census']) < int(sub['T_days_phase']))


def test_R13_the_oracle_verdict_and_the_clairvoyant_column_are_their_own_definitions(
        operating_points, clairvoyant):
    """
    Two additive columns, each asserted against the rule it names rather than
    against a value. `n_star_realized_below_analytic` replaces the delivered
    `anticonservative`, which is the literal `True` written into every row of
    `protocol_19d` and computed nowhere.
    """
    for row in operating_points.itertuples(index=False):
        if not row.op_attainable:
            expected = 'not_attainable'
        elif pd.isna(row.tau_realized_days):
            expected = 'no_alarm'
        elif row.tau_realized_days <= row.T_days_phase:
            expected = 'detected_within_T'
        else:
            expected = 'alarm_beyond_T'
        assert row.oracle_verdict == expected
        assert bool(row.alarm_within_T) == (expected == 'detected_within_T')
    for row in clairvoyant.itertuples(index=False):
        if pd.isna(row.n_star_realized) or pd.isna(row.n_star_analytic):
            assert pd.isna(row.n_star_realized_below_analytic), (
                "a floor that was never crossed is not a floor that was crossed early; the "
                "delivered constant `True` asserted the second of the first")
        else:
            assert bool(row.n_star_realized_below_analytic) == (
                row.n_star_realized < row.n_star_analytic)
    assert clairvoyant['n_star_realized_below_analytic'].nunique(dropna=True) > 1, (
        "the column the port replaced was constant over all twelve rows of protocol_19d while "
        "n_star_realized sits above n_star_analytic on some rows and below on others; if the "
        "computed column is now constant too, the finding recorded in AUDIT_R13.md changes")


# =====================================================================
# BLOCKING ASSERTIONS -- THE MACROS
# =====================================================================

def test_R13_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix(macros):
    assert macros, "R13_claims.tex carries no macro"
    for name, body in macros.items():
        assert name.startswith(MACRO_PREFIX), (
            f"{name} does not carry the cardinal prefix {MACRO_PREFIX}. Preamble S6 fixes "
            f"\\R<Ordinal><Claim> with the ordinal in English words, and the repository realises "
            f"cardinals throughout (ROne ... RSix, REleven, RSixteen, REighteen).")
        assert not name.startswith("RThirteenth"), "cardinal, never ordinal"
        assert 'nan' not in body.lower(), f"macro {name} carries the body {body!r}"
        assert body.strip() != ""
    text = (TABLES_DIR / "R13_claims.tex").read_text()
    for banned in ("ADDmin", "ADD_min", "SharpeCeiling"):
        assert not re.search(r"\\newcommand\{\\RThirteen[A-Za-z]*" + banned, text), (
            "R16 owns ADD_min and the Sharpe ceiling; R13 consumes them and cites \\RSixteen...")


def test_R13_the_macros_agree_with_the_frames_they_are_computed_from(
        macros, operating_points, diagnostics):
    published = operating_points[(operating_points['episode_id'] == "E1")
                                 & (operating_points['detector'] == "D2")
                                 & (operating_points['sigma_oracle'] == "V1")
                                 & (operating_points['operating_point'] == PUBLISHED_OP)].iloc[0]
    std_mean = operating_points[(operating_points['episode_id'] == "E1")
                                & (operating_points['detector'] == "D1")
                                & (operating_points['sigma_oracle'] == "V1")
                                & (operating_points['operating_point'] == PUBLISHED_OP)]
    std_mean = std_mean[np.isclose(std_mean['delta'].to_numpy(dtype=float), 0.0,
                                   rtol=0.0, atol=0.0)].iloc[0]
    assert int(macros['RThirteenCovidDelayLR']) == int(published['tau_realized_days'])
    assert macros['RThirteenCovidFprLR'] == f"{100.0 * published['FPR_H']:.1f}\\%"
    assert int(macros['RThirteenCovidDelayStdMean']) == int(std_mean['tau_realized_days'])
    assert macros['RThirteenArlZeroCensoredFrac'] == f"{published['arl0_censored_frac']:.4f}"
    e1 = diagnostics[diagnostics['episode_id'] == "E1"]
    best = e1.loc[e1['jensen_ratio'].idxmax()]
    assert macros['RThirteenJensenRatio'] == f"{best['jensen_ratio']:.1f}"
    assert macros['RThirteenJensenOracle'] == best['sigma_oracle']
    assert int(macros['RThirteenOracleCertifiedCount']) == int(
        operating_points['oracle_certified'].sum())
    assert int(macros['RThirteenOracleContaminatedCount']) == int(
        operating_points['oracle_contaminated'].sum())
    # The four verdict macros carry BOTH settings the Figure 14 caption names.
    for name in ('RThirteenCovidVerdict', 'RThirteenRecoveryVerdict', 'RThirteenAdvanceVerdict',
                 'RThirteenCorrectionVerdict'):
        assert " / " in macros[name], (
            "the verdict at delta = 0 and the verdict at delta_opt do not always agree, and a "
            "single word would hide which one the reader is given")
    assert macros['RThirteenCorrectionVerdict'] == "no alarm / no alarm", (
        "the Figure 14 caption: 'the 2011 correction is not detected at either setting'")


# =====================================================================
# BLOCKING ASSERTIONS -- FILE HYGIENE THE PREAMBLE IMPOSES
# =====================================================================

def test_R13_every_produced_text_file_ends_in_a_newline():
    """
    Preamble S6: docs/sections/*.md and requirements/*.txt are assembled by
    concatenation, and a missing newline glues two dependencies onto one line.
    """
    for path in (TABLES_DIR / "R13_claims.tex",
                 ROOT / "requirements" / "R13.txt",
                 ROOT / "docs" / "sections" / "R13.md",
                 ROOT / "docs" / "audits" / "AUDIT_R13.md"):
        assert path.exists(), f"Missing deliverable: {path}"
        assert path.read_text().endswith("\n"), f"{path} does not end in a newline"


def test_R13_the_produced_sources_and_logs_carry_no_confirmatory_language():
    """
    Preamble S4.4. The banned words attribute the value of a proof to a
    measurement; neutral technical uses stay licit and none of them matches this
    pattern.
    """
    pattern = re.compile(
        r"proves|proven|perfectly valid|validates the (theorem|thesis|claim)|confirms the|"
        r"as expected|triumph|victory|irrefutable|brilliant", re.IGNORECASE)
    targets = [ROOT / "experiments" / "R13_oracle_ceiling" / "exp_R13_oracle_ceiling_a.py",
               ROOT / "experiments" / "R13_oracle_ceiling" / "exp_R13_oracle_ceiling_b.py",
               ROOT / "docs" / "sections" / "R13.md",
               ROOT / "AUDIT_R13.md",
               ROOT / "logs" / "R13_oracle_ceiling" / "exp_R13_oracle_ceiling_a.log",
               ROOT / "logs" / "R13_oracle_ceiling" / "exp_R13_oracle_ceiling_b.log"]
    for path in targets:
        if not path.exists():
            continue
        hits = [line for line in path.read_text().splitlines() if pattern.search(line)]
        assert not hits, f"{path.name} carries confirmatory language: {hits[:3]}"


def test_R13_the_produced_sources_carry_no_banned_construct():
    """Preamble S7: no `iterrows`, no bare `except:`, no absolute path."""
    for name in ("exp_R13_oracle_ceiling_a.py", "exp_R13_oracle_ceiling_b.py"):
        text = (ROOT / "experiments" / "R13_oracle_ceiling" / name).read_text()
        assert "iterrows" not in text
        assert not re.search(r"except\s*:", text)
        assert not re.search(r"['\"]/home/", text), "no absolute path may be embedded"


# =====================================================================
# REPORTING -- PRINTS WHAT R13 MEASURED, ASSERTS NOTHING
# =====================================================================

def test_R13_report_the_campaign_against_its_witness(frontier, operating_points, diagnostics,
                                                     clairvoyant, detector_recovery, witnesses):
    """
    The D0-D3 classification of preamble S3, computed rather than asserted. The
    witness is never a gate (`data/reference/README.md`), and R13's 128-bit
    re-keying redraws every Monte-Carlo value by construction.
    """
    print("\n" + "=" * 78)
    print("R13 -- the regenerated campaign against the submitted campaign's witness")
    print("=" * 78)
    pairs = (("R13_oracle_frontier.csv", frontier, witnesses['frontier']),
             ("R13_oracle_operating_points.csv", operating_points, witnesses['operating_points']),
             ("R13_oracle_diagnostics.csv", diagnostics, witnesses['diagnostics']),
             ("R13_clairvoyant_floor.csv", clairvoyant, witnesses['clairvoyant']),
             ("R13_detector_recovery.csv", detector_recovery, witnesses['detector_recovery']))
    for label, new, old in pairs:
        shared = [c for c in old.columns if c in new.columns]
        worst_column, worst_value = None, 0.0
        for column in shared:
            if old[column].dtype.kind in "fi" and new[column].dtype.kind in "fi" \
                    and len(new) == len(old):
                gap = float((new[column].astype(float)
                             - old[column].astype(float)).abs().max(skipna=True))
                if np.isfinite(gap) and gap > worst_value:
                    worst_column, worst_value = column, gap
        added = [c for c in new.columns if c not in old.columns]
        dropped = [c for c in old.columns if c not in new.columns]
        print(f"  {label}: {len(new)} rows against {len(old)}, {len(shared)} shared columns")
        print(f"    columns added {added}")
        print(f"    columns dropped {dropped or 'none'}")
        print(f"    worst numeric difference {worst_value:g}"
              + (f" on `{worst_column}`" if worst_column else ""))
    print("  Every Monte-Carlo value is redrawn by the 128-bit re-keying prompt section 2.6")
    print("  requires; the comparison classifies, it does not gate.")
    print("=" * 78)


def test_R13_report_the_threshold_neighbourhood_of_the_published_operating_point(frontier):
    """
    `OP2b_ARL0_252` selects the first threshold whose ARL0 -- a mean over 5,000
    regenerated GARCH paths -- reaches 252. A one-index shift moves both FPR_H
    and tau, so the neighbours are printed and the sensitivity is visible rather
    than inferred.
    """
    print("\n" + "=" * 78)
    print("R13 -- the threshold neighbourhood of the published operating point (E1 / V1)")
    print("=" * 78)
    for detector, delta in (("D2", None), ("D1", 0.0)):
        cell = frontier[(frontier['episode_id'] == "E1") & (frontier['sigma_oracle'] == "V1")
                        & (frontier['detector'] == detector)]
        cell = (cell[cell['delta'].isna()] if delta is None
                else cell[np.isclose(cell['delta'].to_numpy(dtype=float), delta,
                                     rtol=0.0, atol=0.0)]).reset_index(drop=True)
        selected = int(np.where(cell['ARL0'].to_numpy() >= ARL0_TARGET_OP2B)[0][0])
        print(f"  {detector} (delta = {delta}), selected grid index {selected} of "
              f"{len(cell)}:")
        print(f"    {'idx':>4}  {'lambda':>14}  {'FPR_H':>9}  {'ARL0':>10}  {'tau':>5}")
        for j in range(max(0, selected - 2), min(len(cell), selected + 3)):
            row = cell.iloc[j]
            marker = "  <== selected" if j == selected else ""
            print(f"    {j:>4}  {row['lambda']:>14.6f}  {row['FPR_H']:>9.5f}  "
                  f"{row['ARL0']:>10.4f}  {row['tau_realized_days']:>5.0f}{marker}")
    print("=" * 78)


def test_R13_report_the_certification_status_of_every_oracle(diagnostics):
    print("\n" + "=" * 78)
    print("R13 -- oracle admissibility: p_lb_z2 >= 0.01 and std_z_ref in [0.8, 1.25]")
    print("=" * 78)
    print(f"  {'ep':<4} {'oracle':<7} {'p_lb_z2':>12} {'std_z_ref':>11} {'kurt_z_ref':>11} "
          f"{'certified':>10} {'contaminated':>13} {'jensen':>9}")
    for row in diagnostics.itertuples(index=False):
        print(f"  {row.episode_id:<4} {row.sigma_oracle:<7} {row.p_lb_z2:>12.6g} "
              f"{row.std_z_ref:>11.6f} {row.kurt_z_ref:>11.6f} {str(row.oracle_certified):>10} "
              f"{str(row.oracle_contaminated):>13} {row.jensen_ratio:>9.4f}")
    print("  V3 is contaminated by construction: its 21-day realized window includes the current")
    print("  return, which prices the crash into sigma_t contemporaneously. That is the oracle")
    print("  L331's 'centered realized volatility' clause describes, and its own admissibility")
    print("  check fails; the certified leave-one-out oracle V2 returns the same verdict.")
    print("=" * 78)
