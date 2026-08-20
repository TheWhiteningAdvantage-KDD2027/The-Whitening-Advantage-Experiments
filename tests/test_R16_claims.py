"""
R16 -- regime census and sign floor. Acceptance and reporting.

Two kinds of statement live in this file and they are kept apart deliberately.

*Blocking assertions* rest either on a deterministic relation reimplemented here
independently of the experiment -- the Sharpe ceiling, the Bernoulli divergence,
the post-onset partition recomputed from the raw return series -- or on a value
v87 PRINTS, compared at v87's own printing precision, which is what protocol specification §3
fixes as the classification rule. NONE rests on a value R16 produced.

*Reporting output* prints the witness comparison, the three dating arms and the
set behind C3's step of one, and asserts nothing.

WHY THE WITNESS IS NOT A BLOCKING ANCHOR. `data/reference/README.md` states it
outright: a witness value is the "published value" column of a D0-D3
comparison, never the anchor of a blocking assertion, because a cell-by-cell
equality gate converts every legitimate correction into a test failure whose
only exit is a widened tolerance. The census happens to reproduce the witness
bit for bit on every shared column, and that fact is REPORTED below rather than
gated.

THE SELF-INVALIDATING ASSERTION.
`test_R16_the_published_dating_description_is_unreachable_by_strict_pagan_
sossounov` requires that a Pagan--Sossounov dating of all four streams NOT
produce the 66 phases v87 L329 attributes to it, and that the canonical census
carry at least one ticker dated by Lunde--Timmermann. That is the sentence
`docs/DEVIATIONS.md` entry `R16-dating-misdescription` is written around. If a
later revision of the dating code ever makes strict Pagan--Sossounov reach 66,
this test fires and the PROSE must be revised -- the D3 would then have
dissolved, and the register entry would have to be withdrawn rather than the
test relaxed.
"""

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "results" / "R16_regime_census" / "data"
TABLES_DIR = ROOT / "results" / "R16_regime_census" / "tables"
REFERENCE_DIR = ROOT / "data" / "reference" / "R16"
SERIES_DIR = ROOT / "data" / "derived_firstrate"

TICKERS = ("SPY", "PFF", "VNQ", "BWX")
GAMMAS = (20, 252, 1260)
ALPHA = 0.05
HEADLINE_GAMMA = 20

# =====================================================================
# ANCHORS -- EVERY ONE OF THEM PRINTED IN articleB_whitening_v87.tex
# =====================================================================
# L329: "(2000--2025; $66$ phases after duration censoring ...) ... for $53$ of
# $66$ phases ($80\%$), the floor ADD_min at the most permissive operating point
# exceeds the phase's own duration. Pricing the binarization exactly through
# kl(q_phase || q_ref) moves that count by one phase ($52$ of $66$); tightening
# to one false alarm per year leaves $64$ of $66$ ($97\%$) out of budget. ...
# (SPY 2011--2018: $0.541 \to 0.554$ over $1{,}753$ days) ... even there the
# floor consumes $55$--$92\%$ of the phase."
V87_PHASE_COUNT = 66
V87_OUT_OF_BUDGET_UNC_G20 = 53
V87_OUT_OF_BUDGET_FRAC_G20 = 80        # per cent, printed as an integer
V87_OUT_OF_BUDGET_SIGN_G20 = 52
V87_OUT_OF_BUDGET_UNC_G252 = 64
V87_OUT_OF_BUDGET_FRAC_G252 = 97       # per cent, printed as an integer
V87_SPY_LONG_Q_REF = 0.541
V87_SPY_LONG_Q_PHASE = 0.554
V87_SPY_LONG_T_DAYS = 1753
V87_FLOOR_FRAC_MAX = 92                # per cent; the lower end, 55, is NOT
                                       # reproduced -- see the D2 test below
# L260: "at the permissive $\gamma = 20$ used in our census, a drift of SR = 1
# costs at least ${\approx}1{,}510$ trading days; at the operational
# $\gamma = 252$ ..., ${\approx}2{,}790$."
V87_SHARPE_ONE_COST_G20 = 1510
V87_SHARPE_ONE_COST_G252 = 2790
# L331: "The COVID-19 crash ($\Delta q \approx -0.28$, annualized Sharpe
# ${\approx}{-6.0}$ over $23$ trading days) ... kl(q_phase || q_ref) = 0.162
# nats/day: a floor of ${\approx}34$ trading days at one false alarm per year,
# and $18.5$ days at the loosest calibration---four fifths of the phase."
V87_COVID_DELTA_Q = -0.28
V87_COVID_SHARPE = -6.0
V87_COVID_T_DAYS = 23
V87_COVID_KL = 0.162
V87_COVID_FLOOR_G252 = 34
V87_COVID_FLOOR_G20 = 18.5
V87_COVID_FLOOR_FRACTION = 0.8         # "four fifths of the phase"
# L392: "at troughs following a crash the turning-point return is an outlier
# (e.g. $-18.6\%$ on PFF, 2020-03-18)".
V87_PFF_BOUNDARY_RETURN_PRINTED = "-18.6%"
V87_PFF_BOUNDARY_DATE = "2020-03-18"

# =====================================================================
# TOLERANCES, EACH DERIVED FROM A MECHANISM
# =====================================================================
# The Sharpe ceiling and the Bernoulli divergence are closed forms in float64.
# Reassociating a product of at most four terms is bounded by 4 * eps =
# 8.9e-16 in relative terms; 1e-12 carries three orders of magnitude of margin
# and is not derived from any observed deviation.
CLOSED_FORM_RTOL = 1e-12
# The per-phase statistics are recomputed here from the raw derived series with
# the same float64 reductions pandas performs, so the admissible difference is
# the reassociation of a sum over at most 2141 terms: 2141 * eps = 4.8e-13.
# 1e-9 is that bound with three orders of margin.
RECOMPUTED_STAT_RTOL = 1e-9

MACRO_PREFIX = "RSixteen"
MACRO_HEADER = "% Auto-generated by exp_R16_regime_census_b.py -- do not edit."


def _read(path):
    assert path.exists(), f"Missing artefact: {path}"
    return pd.read_csv(path, float_precision='round_trip')


@pytest.fixture
def census():
    return _read(DATA_DIR / "R16_regime_census.csv")


@pytest.fixture
def census_strict_ps():
    return _read(DATA_DIR / "R16_regime_census_strict_ps.csv")


@pytest.fixture
def census_symmetric():
    return _read(DATA_DIR / "R16_regime_census_symmetric.csv")


@pytest.fixture
def sign_floor():
    return _read(DATA_DIR / "R16_sign_floor.csv")


@pytest.fixture
def feasibility():
    return _read(DATA_DIR / "R16_feasibility_vs_gamma.csv")


@pytest.fixture
def boundary_delta():
    return _read(DATA_DIR / "R16_boundary_convention_delta.csv")


@pytest.fixture
def meso_split():
    return _read(DATA_DIR / "R16_meso_split_report.csv")


@pytest.fixture
def witness_census():
    return _read(REFERENCE_DIR / "protocol_10b_regime_census_refined.csv")


@pytest.fixture
def witness_sign_floor():
    return _read(REFERENCE_DIR / "protocol_20a_sign_floor.csv")


@pytest.fixture
def returns():
    out = {}
    for ticker in TICKERS:
        frame = pd.read_csv(SERIES_DIR / f"R01_daily_{ticker}.csv", float_precision='round_trip',
                            index_col='Date', parse_dates=True)
        series = frame['log_ret']
        out[ticker] = series[~series.index.duplicated(keep='first')].sort_index().dropna()
    return out


@pytest.fixture
def macros():
    path = TABLES_DIR / "R16_claims.tex"
    assert path.exists(), f"Missing artefact: {path}"
    text = path.read_text()
    assert text.endswith("\n"), ("protocol specification §6 requires every produced text file to end with a "
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


# =====================================================================
# INDEPENDENT REIMPLEMENTATIONS OF THE DERIVED RULES
# =====================================================================

def sharpe_ceiling(gamma, sharpe):
    """
    Corollary cor:sharpe_ceiling, written from the manuscript's own statement
    ADD_min >= ln(gamma) / KL with KL = SR^2 / 504, rather than from the
    experiment's `504 * ln(gamma) / SR^2`. Two routes to one number.
    """
    kl_per_observation = (sharpe ** 2) / 504.0
    if kl_per_observation == 0.0:
        return math.inf
    return math.log(gamma) / kl_per_observation


def bernoulli_kl(q_phase, q_ref):
    """
    kl(Bernoulli(q1) || Bernoulli(q0)) accumulated as the expectation of the
    log-likelihood ratio under q1, term by term, which is the definition the
    experiment's closed form closes.
    """
    q0 = min(max(q_ref, 1e-6), 1.0 - 1e-6)
    q1 = min(max(q_phase, 1e-6), 1.0 - 1e-6)
    if abs(q1 - q0) < 1e-12:
        return 0.0
    return sum(p * math.log(p / r) for p, r in ((q1, q0), (1.0 - q1, 1.0 - q0)))


def post_onset_statistics(series, start, end):
    """
    T_days, annualized Sharpe and the up-day rate of a phase under the strict
    post-onset convention v87 L392 imposes, recomputed from the raw series.
    """
    i0 = series.index.get_loc(pd.Timestamp(start))
    i1 = series.index.get_loc(pd.Timestamp(end))
    window = series.iloc[i0 + 1: i1 + 1]
    t_days = i1 - i0
    volatility = window.std(ddof=1) * math.sqrt(252)
    sharpe = (window.mean() * 252) / volatility if volatility != 0 else 0.0
    return t_days, float(sharpe), float((window > 0).mean())


def rounds_to(value, printed, decimals):
    """v87's printing precision is the classification rule of protocol specification §3."""
    return round(float(value), decimals) == round(float(printed), decimals)


# =====================================================================
# BLOCKING ASSERTIONS -- STRUCTURE AND SCHEMA
# =====================================================================

def test_R16_every_artefact_the_prompt_lists_exists_with_its_prescribed_schema(
        census, sign_floor, feasibility, boundary_delta, meso_split,
        census_strict_ps, census_symmetric):
    assert list(census.columns) == [
        'ticker', 'phase_id', 'phase_type', 'start_date', 'end_date', 'T_days', 'ann_return',
        'ann_vol', 'vol_pct', 'sharpe', 'q_ref', 'q_phase', 'delta_q', 'alpha', 'ADD_min_days',
        'detectable_flag', 'pathology_class', 'episode_label', 'source_scale', 'dating_algorithm']
    assert list(census_strict_ps.columns) == list(census.columns)
    assert list(census_symmetric.columns) == list(census.columns)
    assert list(feasibility.columns) == ['census_source', 'gamma', 'budget', 'n_phases',
                                         'n_detectable', 'frac_detectable']
    assert list(meso_split.columns) == ['ticker', 'macro_phase_id', 'macro_T_days',
                                        'n_meso_splits_applied', 'resulting_subphase_ids']
    for column in ['ticker', 'phase_id', 'start_date', 'end_date', 'T_days_before',
                   'T_days_after', 'r_boundary', 'sharpe_before', 'sharpe_after',
                   'ADD_min_before', 'ADD_min_after', 'detectable_before', 'detectable_after',
                   'flipped']:
        assert column in boundary_delta.columns
    for gamma in GAMMAS:
        for budget in ('unc', 'sign'):
            assert f'ADD_min_{budget}_g{gamma}' in sign_floor.columns
            assert f'detectable_{budget}_g{gamma}' in sign_floor.columns
    assert 'arm_disagreement' in sign_floor.columns, (
        "the column that makes C3 traceable: v87's 'moves that count by one phase' is true of "
        "the count and false of the set")
    assert not (ROOT / "results" / "R16_regime_census" / "figures").exists() or not list(
        (ROOT / "results" / "R16_regime_census" / "figures").glob("*.png")), (
        "R16 renders no figure: v87's census paragraphs L329 and L331 carry no \\includegraphics "
        "and reference only \\ref{fig:oracle_frontier}, which belongs to R01.")


def test_R16_the_census_carries_the_phase_count_v87_prints(census, sign_floor, boundary_delta):
    """v87 L329 prints "$66$ phases after duration censoring"."""
    assert len(census) == V87_PHASE_COUNT
    assert len(sign_floor) == V87_PHASE_COUNT
    assert len(boundary_delta) == V87_PHASE_COUNT
    assert sorted(census['ticker'].unique()) == sorted(TICKERS)


def test_R16_the_dating_algorithm_column_names_the_algorithm_of_every_row(
        census, census_strict_ps, census_symmetric):
    """
    Preamble S4.3 requires a fallback that is kept to be selected by an explicit
    argument and stamped in the output; the column is the row-by-row half of
    that requirement, and its content is what the arms mean.
    """
    for frame in (census, census_strict_ps, census_symmetric):
        assert set(frame['dating_algorithm']) <= {'pagan_sossounov', 'lunde_timmermann'}
        # one algorithm per ticker: the substitution is a per-stream decision
        assert (frame.groupby('ticker')['dating_algorithm'].nunique() == 1).all()
    assert set(census_strict_ps['dating_algorithm']) == {'pagan_sossounov'}, (
        "the strict_ps arm is Pagan--Sossounov on all four streams by definition")
    assert set(census_symmetric['dating_algorithm']) == {'lunde_timmermann'}, (
        "every one of the four tickers fails check_sanity, so the symmetric arm substitutes on "
        "all four")


# =====================================================================
# BLOCKING ASSERTIONS -- THE COUNTS v87 PRINTS
# =====================================================================

def test_R16_the_out_of_budget_counts_reproduce_the_three_v87_prints(sign_floor, feasibility):
    """
    C2 as an acceptance criterion, at v87's printing precision. The three counts
    are the manuscript's most-cited empirical claim (L57, L87, L329, L374).
    """
    n = len(sign_floor)
    out_unc_20 = n - int(sign_floor['detectable_unc_g20'].sum())
    out_sign_20 = n - int(sign_floor['detectable_sign_g20'].sum())
    out_unc_252 = n - int(sign_floor['detectable_unc_g252'].sum())
    assert out_unc_20 == V87_OUT_OF_BUDGET_UNC_G20
    assert out_sign_20 == V87_OUT_OF_BUDGET_SIGN_G20
    assert out_unc_252 == V87_OUT_OF_BUDGET_UNC_G252
    assert round(100.0 * out_unc_20 / n) == V87_OUT_OF_BUDGET_FRAC_G20
    assert round(100.0 * out_unc_252 / n) == V87_OUT_OF_BUDGET_FRAC_G252
    # the same three counts read off the feasibility grid, which is a second
    # persisted route to them
    for gamma, budget, expected in ((20, 'unc', V87_OUT_OF_BUDGET_UNC_G20),
                                    (20, 'sign', V87_OUT_OF_BUDGET_SIGN_G20),
                                    (252, 'unc', V87_OUT_OF_BUDGET_UNC_G252)):
        row = feasibility[(feasibility['gamma'] == gamma)
                          & (feasibility['budget'] == budget)].iloc[0]
        assert int(row['n_phases']) - int(row['n_detectable']) == expected


def test_R16_the_step_of_one_holds_on_the_count_and_fails_on_the_set(sign_floor):
    """
    C3. v87 L329: pricing the binarisation exactly "moves that count by one
    phase". The step is asserted because v87 prints it; the SET is asserted to
    be larger than one, because that is what the `arm_disagreement` column
    exists to make checkable.
    """
    n_sign = int(sign_floor['detectable_sign_g20'].sum())
    n_unc = int(sign_floor['detectable_unc_g20'].sum())
    assert n_sign - n_unc == 1
    sign_only = sign_floor['detectable_sign_g20'] & ~sign_floor['detectable_unc_g20']
    unc_only = sign_floor['detectable_unc_g20'] & ~sign_floor['detectable_sign_g20']
    assert (sign_floor['arm_disagreement'] == 'sign_only').equals(sign_only.rename(
        'arm_disagreement'))
    assert (sign_floor['arm_disagreement'] == 'unc_only').equals(unc_only.rename(
        'arm_disagreement'))
    assert int(sign_only.sum()) - int(unc_only.sum()) == 1, (
        "the step of one is the NET of the two disagreement sets, by construction")
    assert int(sign_only.sum()) + int(unc_only.sum()) > 1, (
        "if the two arms ever disagreed on exactly one phase, v87's 'moves that count by one "
        "phase' would be true of the set as well, and docs/DEVIATIONS.md "
        "`R16-sign-arm-disagreement` would have to be withdrawn rather than this test relaxed")


def test_R16_the_boundary_convention_flips_run_in_one_direction_only(boundary_delta, macros):
    """
    C4. The prompt's section 2.2 asserts an envelope of [50, 56]; all the flips
    run one way, so the reachable envelope is [published, published + flips] and
    the published figure is its conservative end. Asserted structurally, not
    against a count R16 produced.
    """
    flipped = boundary_delta['flipped']
    gained = (~boundary_delta['detectable_before']) & boundary_delta['detectable_after']
    lost = boundary_delta['detectable_before'] & (~boundary_delta['detectable_after'])
    assert flipped.equals((gained | lost).rename('flipped'))
    assert int(lost.sum()) == 0, (
        "every flip gains detectability under the post-onset convention, so the published count "
        "is the LOW end of its own convention envelope; a flip in the other direction would put "
        "the published figure inside the interval and docs/DEVIATIONS.md "
        "`R16-boundary-sensitivity` would have to be rewritten")
    n = len(boundary_delta)
    out_post_onset = n - int(boundary_delta['detectable_after'].sum())
    out_inclusive = n - int(boundary_delta['detectable_before'].sum())
    assert out_post_onset == V87_OUT_OF_BUDGET_UNC_G20, (
        "the post-onset arm is the one v87 publishes")
    assert out_inclusive - out_post_onset == int(flipped.sum())
    assert int(macros['RSixteenFlippedUp']) == int(gained.sum())
    assert int(macros['RSixteenFlippedDown']) == int(lost.sum())
    assert int(macros['RSixteenOutOfBudgetLow']) == out_post_onset
    assert int(macros['RSixteenOutOfBudgetHigh']) == out_inclusive
    # T_days shortens by exactly one under the post-onset convention, which is
    # what "the return dated at a turning point closes the regime it ends" means.
    assert ((boundary_delta['T_days_before'] - boundary_delta['T_days_after']) == 1).all()


# =====================================================================
# BLOCKING ASSERTIONS -- THE DERIVED RULES, AGAINST A SECOND IMPLEMENTATION
# =====================================================================

def test_R16_the_unconditional_floor_is_the_sharpe_ceiling_of_the_corollary(sign_floor):
    for row in sign_floor.itertuples(index=False):
        for gamma in GAMMAS:
            expected = sharpe_ceiling(gamma, row.sharpe)
            observed = getattr(row, f'ADD_min_unc_g{gamma}')
            assert abs(observed / expected - 1.0) < CLOSED_FORM_RTOL, (
                f"{row.ticker} {row.start_date}: ADD_min_unc_g{gamma} = {observed} against "
                f"{expected} from ln(gamma)/KL with KL = SR^2/504")


def test_R16_the_sign_floor_is_the_bernoulli_divergence_of_the_manuscript(sign_floor):
    for row in sign_floor.itertuples(index=False):
        expected_kl = bernoulli_kl(row.q_phase, row.q_ref)
        assert abs(row.kl_sign_nats_day - expected_kl) < CLOSED_FORM_RTOL * max(1.0, expected_kl)
        for gamma in GAMMAS:
            observed = getattr(row, f'ADD_min_sign_g{gamma}')
            expected = math.inf if expected_kl == 0.0 else math.log(gamma) / expected_kl
            if math.isinf(expected):
                assert math.isinf(observed)
            else:
                assert abs(observed / expected - 1.0) < CLOSED_FORM_RTOL


def test_R16_every_detectability_flag_is_its_own_floor_against_its_own_duration(
        sign_floor, census):
    for gamma in GAMMAS:
        for budget in ('unc', 'sign'):
            expected = sign_floor[f'ADD_min_{budget}_g{gamma}'] < sign_floor['T_days']
            assert sign_floor[f'detectable_{budget}_g{gamma}'].equals(
                expected.rename(f'detectable_{budget}_g{gamma}'))
    assert census['detectable_flag'].equals(
        (census['ADD_min_days'] < census['T_days']).rename('detectable_flag'))
    # `alpha = 0.05` is `gamma = 20`, so the census flag and the g20
    # unconditional flag are the same statement made twice.
    assert (census['alpha'] == ALPHA).all()
    assert census['detectable_flag'].equals(
        sign_floor['detectable_unc_g20'].rename('detectable_flag'))


def test_R16_the_census_statistics_recompute_from_the_raw_return_series(census, returns):
    """
    The whole census, recomputed from `data/derived_firstrate/` under the
    post-onset convention. This is the only route by which a dating error could
    hide behind a self-consistent CSV.
    """
    for row in census.itertuples(index=False):
        t_days, sharpe, q_phase = post_onset_statistics(returns[row.ticker], row.start_date,
                                                        row.end_date)
        assert t_days == row.T_days
        assert abs(sharpe - row.sharpe) <= RECOMPUTED_STAT_RTOL * max(1.0, abs(sharpe))
        assert abs(q_phase - row.q_phase) <= RECOMPUTED_STAT_RTOL


def test_R16_the_phases_partition_the_return_series_of_every_ticker(census, returns):
    """
    C1 as an acceptance criterion, asserted and not observed. v87 L392: "the
    return dated at a turning point closes the regime it ends, so consecutive
    phases partition the return series and no pre-change observation enters a
    phase's Sharpe."
    """
    for ticker in TICKERS:
        sub = census[census['ticker'] == ticker].sort_values('phase_id')
        assert len(sub) > 0
        starts = list(sub['start_date'])
        ends = list(sub['end_date'])
        assert all(ends[k] == starts[k + 1] for k in range(len(sub) - 1)), (
            f"{ticker}: consecutive phases are not contiguous, so they do not partition")
        series = returns[ticker]
        span = (series.index.get_loc(pd.Timestamp(ends[-1]))
                - series.index.get_loc(pd.Timestamp(starts[0])))
        assert int(sub['T_days'].sum()) == span, (
            f"{ticker}: sum(T_days) = {int(sub['T_days'].sum())} against a covered span of "
            f"{span}; the partition has a hole or an overlap")
        assert (sub['phase_id'].values == np.arange(len(sub))).all(), (
            f"{ticker}: the phase ids are not consecutive from zero, so a phase was dropped "
            f"between the dating and the census")


def test_R16_no_degenerate_phase_reaches_a_detectability_flag_without_measurement(
        census, sign_floor):
    """
    C5. `NaN < T_days` is False, so a phase with a non-finite Sharpe or a
    non-finite divergence would be counted OUT OF BUDGET without ever being
    measured -- which inflates the very fraction the manuscript publishes. The
    mechanism, not an observed count, is what makes this blocking.
    """
    assert np.isfinite(census['sharpe']).all()
    assert np.isfinite(census['ann_vol']).all()
    assert np.isfinite(sign_floor['kl_sign_nats_day']).all()
    assert (census['T_days'] > 0).all()
    assert not census['q_phase'].isin([0.0, 1.0]).any()


# =====================================================================
# BLOCKING ASSERTIONS -- THE PHASES AND THE NUMERALS v87 NAMES
# =====================================================================

def test_R16_the_turning_point_return_v87_cites_falls_where_the_convention_puts_it(
        census, returns, boundary_delta):
    """
    C7. v87 L392 cites `-18.6%` on PFF, 2020-03-18 as the outlier the post-onset
    convention excludes. Deterministic; trigger probability 0.
    """
    boundary = returns["PFF"].loc[pd.Timestamp(V87_PFF_BOUNDARY_DATE)]
    assert f"{boundary * 100:.1f}%" == V87_PFF_BOUNDARY_RETURN_PRINTED
    pff = census[census['ticker'] == "PFF"]
    closing = pff[pff['end_date'] == V87_PFF_BOUNDARY_DATE]
    opening = pff[pff['start_date'] == V87_PFF_BOUNDARY_DATE]
    assert len(closing) == 1 and len(opening) == 1, (
        "the post-onset convention makes the turning-point return close exactly one phase and "
        "open exactly one")
    row = boundary_delta[(boundary_delta['ticker'] == "PFF")
                         & (boundary_delta['start_date'] == V87_PFF_BOUNDARY_DATE)].iloc[0]
    assert row['r_boundary'] == boundary
    assert abs(row['sharpe_after']) > abs(row['sharpe_before']), (
        "L392: the outlier depresses the mean and inflates the variance of the phase that "
        "follows, so excluding it RAISES that phase's Sharpe")
    assert row['ADD_min_after'] < row['ADD_min_before'], (
        "L392: the defect biases the phase's floor upward, so the correction lowers it")


def test_R16_the_long_secular_advance_v87_prints_reproduces(census, sign_floor):
    """
    L329: "Long secular advances move the up-day probability only marginally
    (SPY 2011--2018: $0.541 \\to 0.554$ over $1{,}753$ days); they nonetheless
    dominate the detectable set on duration alone".

    The phase is found as the longest of the detectable set -- which is the
    property the sentence asserts -- and never by a typed date.
    """
    detectable = sign_floor['detectable_unc_g20']
    longest = sign_floor[detectable].loc[sign_floor[detectable]['T_days'].idxmax()]
    assert longest['ticker'] == "SPY"
    assert int(longest['T_days']) == V87_SPY_LONG_T_DAYS
    assert rounds_to(longest['q_ref'], V87_SPY_LONG_Q_REF, 3)
    assert rounds_to(longest['q_phase'], V87_SPY_LONG_Q_PHASE, 3)
    assert pd.to_datetime(longest['start_date']).year == 2011
    assert pd.to_datetime(longest['end_date']).year == 2018


def test_R16_the_covid_phase_v87_prints_reproduces_to_its_printed_precision(sign_floor):
    """
    L331, every numeral. The phase is selected by the episode label the dating
    itself assigns, on the ticker v87 L321 monitors through 2020.
    """
    covid = sign_floor[(sign_floor['ticker'] == "SPY")
                       & (sign_floor['episode_label'] == "COVID_2020")]
    assert len(covid) == 1
    covid = covid.iloc[0]
    assert int(covid['T_days']) == V87_COVID_T_DAYS
    assert rounds_to(covid['delta_q'], V87_COVID_DELTA_Q, 2)
    assert rounds_to(covid['sharpe'], V87_COVID_SHARPE, 1)
    assert rounds_to(covid['kl_sign_nats_day'], V87_COVID_KL, 3)
    assert rounds_to(covid['ADD_min_sign_g252'], V87_COVID_FLOOR_G252, 0)
    assert rounds_to(covid['ADD_min_sign_g20'], V87_COVID_FLOOR_G20, 1)
    assert rounds_to(covid['ADD_min_sign_g20'] / covid['T_days'], V87_COVID_FLOOR_FRACTION, 1), (
        "L331 calls the gamma = 20 sign floor 'four fifths of the phase'")


def test_R16_the_two_numerical_evaluations_of_the_bound_reproduce_L260(macros):
    """
    L260: a drift of SR = 1 costs at least ~1,510 trading days at gamma = 20 and
    ~2,790 at gamma = 252. Both are closed forms with no Monte Carlo in them.
    """
    assert round(sharpe_ceiling(20, 1.0)) == V87_SHARPE_ONE_COST_G20
    assert round(sharpe_ceiling(252, 1.0), -1) == V87_SHARPE_ONE_COST_G252
    assert rounds_to(macros['RSixteenSharpeOneCostGammaTwenty'], sharpe_ceiling(20, 1.0), 2)
    assert rounds_to(macros['RSixteenSharpeOneCostGammaTwoFiftyTwo'], sharpe_ceiling(252, 1.0), 2)


def test_R16_the_floor_fraction_envelope_of_L329_does_not_reproduce_at_its_lower_end(sign_floor):
    """
    D2, `R16-floor-frac-envelope`. v87 L329 states "the floor consumes 55--92%
    of the phase" over the detectable set. The upper end reproduces; the lower
    end does not, and the deviation is REGISTERED rather than absorbed.

    This test asserts the deviation itself. If a later campaign ever brings the
    minimum back to 55%, it fires, and what must then change is
    docs/DEVIATIONS.md -- the entry is withdrawn -- not this assertion.
    """
    detectable = sign_floor['detectable_unc_g20']
    fractions = (sign_floor[detectable]['ADD_min_unc_g20']
                 / sign_floor[detectable]['T_days'])
    assert round(100.0 * fractions.max()) == V87_FLOOR_FRAC_MAX
    assert round(100.0 * fractions.min()) < 55, (
        f"the minimum floor fraction is {100.0 * fractions.min():.1f}%, which v87 L329 prints as "
        f"55%. The deviation `R16-floor-frac-envelope` is registered on the fact that it does "
        f"NOT reproduce; if it now does, the register entry is what must be withdrawn.")
    assert (fractions <= 1.0).all(), (
        "a detectable phase has a floor strictly below its own duration by definition")


# =====================================================================
# BLOCKING ASSERTIONS -- THE DEVIATION THE COUNTERFACTUAL ARMS PRICE
# =====================================================================

def test_R16_the_published_dating_description_is_unreachable_by_strict_pagan_sossounov(
        census, census_strict_ps):
    """
    THE SELF-INVALIDATING ASSERTION, and the sentence `R16-dating-misdescription`
    is written around.

    v87 L329 describes "a retrospective multi-scale Pagan--Sossounov bull/bear
    dating of the four streams (2000--2025; 66 phases after duration censoring)".
    A Pagan--Sossounov dating of all four streams does NOT produce 66 phases,
    and the census that does is not a pure Pagan--Sossounov dating. If a later
    revision of the dating code ever makes strict Pagan--Sossounov reach 66, this
    test fires and the register entry must be withdrawn rather than the test
    relaxed.
    """
    assert len(census) == V87_PHASE_COUNT
    assert len(census_strict_ps) != V87_PHASE_COUNT, (
        "strict Pagan--Sossounov now reaches the phase count v87 attributes to it; the D3 "
        "`R16-dating-misdescription` has dissolved and docs/DEVIATIONS.md must be revised")
    substituted = census[census['dating_algorithm'] == 'lunde_timmermann']['ticker'].unique()
    assert len(substituted) >= 1, (
        "the canonical census is a pure Pagan--Sossounov dating after all; the D3 has dissolved")
    assert set(substituted) == {"SPY"}, (
        "the delivered script guards the substitution with `if ticker == 'SPY'`; a different "
        "scope changes what `R16-substitution-scope` records")


def test_R16_the_counterfactual_arms_are_the_rules_they_claim_to_be(
        census, census_strict_ps, census_symmetric):
    """
    The arms are asserted on their RULE, never on the phase counts they produce,
    which are outputs of this experiment.
    """
    # The three arms agree exactly on the tickers where no substitution applies.
    for ticker in TICKERS:
        canonical_rows = census[census['ticker'] == ticker]
        strict_rows = census_strict_ps[census_strict_ps['ticker'] == ticker]
        if canonical_rows['dating_algorithm'].iloc[0] == 'pagan_sossounov':
            assert len(canonical_rows) == len(strict_rows)
            assert list(canonical_rows['start_date']) == list(strict_rows['start_date'])
            assert list(canonical_rows['end_date']) == list(strict_rows['end_date'])
        else:
            symmetric_rows = census_symmetric[census_symmetric['ticker'] == ticker]
            assert list(canonical_rows['start_date']) == list(symmetric_rows['start_date']), (
                "on a ticker the canonical arm substitutes, the symmetric arm applies the same "
                "substitution and must agree phase for phase")
    # Lunde--Timmermann applies no duration censoring, which is exactly what v87
    # L329's "after duration censoring" describes and what the substitution
    # removes on the stream it touches.
    assert census_symmetric['T_days'].min() < census_strict_ps['T_days'].min(), (
        "the substituted dating admits shorter phases than Pagan--Sossounov's min_phase rule "
        "permits, which is the sense in which it applies no duration censoring")


def test_R16_the_macros_price_the_counterfactuals_they_name(
        macros, census, census_strict_ps, census_symmetric):
    assert int(macros['RSixteenPhaseCount']) == len(census)
    assert int(macros['RSixteenStrictPsPhaseCount']) == len(census_strict_ps)
    assert int(macros['RSixteenSymmetricPhaseCount']) == len(census_symmetric)
    assert int(macros['RSixteenStrictPsSpyPhaseCount']) == int(
        (census_strict_ps['ticker'] == "SPY").sum())
    assert int(macros['RSixteenStrictPsPhaseCount']) != int(macros['RSixteenPhaseCount'])


# =====================================================================
# BLOCKING ASSERTIONS -- THE MACROS
# =====================================================================

def test_R16_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix(macros):
    assert macros, "R16_claims.tex carries no macro"
    for name, body in macros.items():
        assert name.startswith(MACRO_PREFIX), (
            f"{name} does not carry the cardinal prefix {MACRO_PREFIX}. Preamble S6 fixes "
            f"\\R<Ordinal><Claim> with the ordinal in English words, and the repository realises "
            f"cardinals throughout (ROne ... RSix, REleven, REighteen).")
        assert not name.startswith("RSixteenth"), "cardinal, never ordinal"
        assert 'nan' not in body.lower(), f"macro {name} carries the body {body!r}"
        assert body.strip() != ""
    text = (TABLES_DIR / "R16_claims.tex").read_text()
    assert "504" not in text.replace("504 ln(1/alpha_0)/SR^2", ""), (
        "no macro may name the analytic bound itself; only its two numerical evaluations, which "
        "is what v87 L260 prints")


def test_R16_the_headline_macros_agree_with_the_frames_they_are_computed_from(
        macros, census, sign_floor, boundary_delta):
    n = len(census)
    out_unc_20 = n - int(sign_floor['detectable_unc_g20'].sum())
    assert int(macros['RSixteenOutOfBudgetUncGammaTwenty']) == out_unc_20
    assert int(macros['RSixteenOutOfBudgetSignGammaTwenty']) == (
        n - int(sign_floor['detectable_sign_g20'].sum()))
    assert int(macros['RSixteenOutOfBudgetGammaTwoFiftyTwo']) == (
        n - int(sign_floor['detectable_unc_g252'].sum()))
    assert macros['RSixteenOutOfBudgetFracGammaTwenty'] == f"{100.0 * out_unc_20 / n:.1f}\\%"
    assert int(macros['RSixteenFlippedPhases']) == int(boundary_delta['flipped'].sum())
    covid = sign_floor[(sign_floor['ticker'] == "SPY")
                       & (sign_floor['episode_label'] == "COVID_2020")].iloc[0]
    assert int(macros['RSixteenCovidTDays']) == int(covid['T_days'])
    assert macros['RSixteenCovidKl'] == f"{covid['kl_sign_nats_day']:.4f}"
    assert macros['RSixteenCovidFloorGammaTwenty'] == f"{covid['ADD_min_sign_g20']:.2f}"
    assert macros['RSixteenCovidFloorGammaTwoFiftyTwo'] == f"{covid['ADD_min_sign_g252']:.2f}"
    detectable = sign_floor['detectable_unc_g20']
    longest = sign_floor[detectable].loc[sign_floor[detectable]['T_days'].idxmax()]
    assert int(macros['RSixteenSpyLongTDays']) == int(longest['T_days'])
    assert macros['RSixteenSpyLongQRef'] == f"{longest['q_ref']:.3f}"
    assert macros['RSixteenSpyLongQPhase'] == f"{longest['q_phase']:.3f}"


# =====================================================================
# BLOCKING ASSERTIONS -- FILE HYGIENE THE PREAMBLE IMPOSES
# =====================================================================

def test_R16_every_produced_text_file_ends_in_a_newline():
    """
    Preamble S6: docs/sections/*.md and requirements/*.txt are assembled by
    concatenation, and a missing newline glues two dependencies onto one line.
    """
    for path in (TABLES_DIR / "R16_claims.tex",
                 ROOT / "requirements" / "R16.txt",
                 ROOT / "docs" / "sections" / "R16.md",
                 ROOT / "docs" / "audits" / "AUDIT_R16.md",
                 ROOT / "data" / "reference" / "R16" / "superseded" / "README.md"):
        assert path.exists(), f"Missing deliverable: {path}"
        assert path.read_text().endswith("\n"), f"{path} does not end in a newline"


def test_R16_the_produced_sources_and_logs_carry_no_confirmatory_language():
    """
    Preamble S4.4. The banned words attribute the value of a proof to a
    measurement; neutral technical uses stay licit and none of them matches this
    pattern.
    """
    pattern = re.compile(
        r"proves|proven|perfectly valid|validates the (theorem|thesis|claim)|confirms the|"
        r"as expected|triumph|victory|irrefutable|brilliant", re.IGNORECASE)
    targets = [ROOT / "experiments" / "R16_regime_census" / "exp_R16_regime_census_a.py",
               ROOT / "experiments" / "R16_regime_census" / "exp_R16_regime_census_b.py",
               ROOT / "docs" / "sections" / "R16.md",
               ROOT / "logs" / "R16_regime_census" / "exp_R16_regime_census_a.log",
               ROOT / "logs" / "R16_regime_census" / "exp_R16_regime_census_b.log"]
    for path in targets:
        if not path.exists():
            continue
        hits = [line for line in path.read_text().splitlines() if pattern.search(line)]
        assert not hits, f"{path.name} carries confirmatory language: {hits[:3]}"


def test_R16_the_produced_sources_carry_no_banned_construct():
    """Preamble S7: no `iterrows`, no bare `except:`, no absolute path."""
    for name in ("exp_R16_regime_census_a.py", "exp_R16_regime_census_b.py"):
        text = (ROOT / "experiments" / "R16_regime_census" / name).read_text()
        assert "iterrows" not in text
        assert not re.search(r"except\s*:", text)
        assert not re.search(r"['\"]/home/", text), "no absolute path may be embedded"


# =====================================================================
# REPORTING -- PRINTS WHAT R16 MEASURED, ASSERTS NOTHING
# =====================================================================

def test_R16_report_the_census_against_its_witness(census, witness_census, sign_floor,
                                                   witness_sign_floor):
    """
    The D0-D3 classification of protocol specification §3, computed rather than asserted. The
    witness is never a gate (`data/reference/README.md`).
    """
    print("\n" + "=" * 78)
    print("R16 -- the regenerated census against the submitted campaign's witness")
    print("=" * 78)
    for label, new, old in (("R16_regime_census.csv", census, witness_census),
                            ("R16_sign_floor.csv", sign_floor, witness_sign_floor)):
        shared = [c for c in old.columns if c in new.columns]
        worst_column, worst_value = None, 0.0
        mismatched = []
        for column in shared:
            if old[column].dtype.kind in "fi":
                gap = float((new[column].astype(float) - old[column].astype(float)).abs().max())
                if gap > worst_value:
                    worst_column, worst_value = column, gap
            elif not (new[column].fillna("") == old[column].fillna("")).all():
                mismatched.append(column)
        added = [c for c in new.columns if c not in old.columns]
        print(f"  {label}: {len(new)} rows against {len(old)}, {len(shared)} shared columns, "
              f"columns added by this repository {added}")
        print(f"    worst numeric difference {worst_value:g}"
              + (f" on `{worst_column}`" if worst_column else "")
              + f"; non-numeric columns that differ: {mismatched or 'none'}")
    print("=" * 78)


def test_R16_report_the_three_dating_arms(census, census_strict_ps, census_symmetric,
                                          sign_floor):
    print("\n" + "=" * 78)
    print("R16 -- the three dating arms and the headline each of them produces")
    print("=" * 78)
    print(f"{'arm':<12}  {'phases':>7}  {'SPY':>5}  {'PFF':>5}  {'VNQ':>5}  {'BWX':>5}  "
          f"{'out of budget, gamma = 20 unc':>30}")
    for name, frame in (("canonical", census), ("strict_ps", census_strict_ps),
                        ("symmetric", census_symmetric)):
        floors = 504.0 * np.log(20) / (frame['sharpe'].to_numpy() ** 2)
        out = int((floors >= frame['T_days'].to_numpy()).sum())
        counts = frame['ticker'].value_counts()
        print(f"{name:<12}  {len(frame):>7}  " + "  ".join(
            f"{int(counts.get(t, 0)):>5}" for t in TICKERS)
            + f"  {out:>13} / {len(frame):<3} = {out / len(frame):>7.1%}")
    print("\nv87 L329 attributes the 66-phase census to a Pagan--Sossounov dating of the four "
          "streams after duration censoring.")
    print("Strict Pagan--Sossounov on the four streams does not reach that count. The 66 require "
          "substituting Lunde--Timmermann on SPY,")
    print("which applies no duration censoring. The 66 VALUES reproduce exactly; what does not "
          "reproduce is the account of how they were obtained.")
    print("Registered `R16-dating-misdescription`, Class A, D3; proof artefact "
          "R16_regime_census_strict_ps.csv.")
    print("=" * 78)


def test_R16_report_the_set_behind_the_step_of_one(sign_floor):
    print("\n" + "=" * 78)
    print("R16 -- C3: 'moves that count by one phase' is true of the count, false of the set")
    print("=" * 78)
    disagreeing = sign_floor[sign_floor['arm_disagreement'] != 'none']
    print(f"The two arms disagree on {len(disagreeing)} of {len(sign_floor)} phases; the step of "
          f"one is their NET.")
    print(f"{'arm':<10}  {'ticker':<7}  {'start':<11}  {'end':<11}  {'T':>5}  {'SR':>8}  "
          f"{'kl':>9}  {'floor unc':>10}  {'floor sign':>11}")
    for row in disagreeing.itertuples(index=False):
        print(f"{row.arm_disagreement:<10}  {row.ticker:<7}  {row.start_date:<11}  "
              f"{row.end_date:<11}  {int(row.T_days):>5}  {row.sharpe:>8.4f}  "
              f"{row.kl_sign_nats_day:>9.6f}  {row.ADD_min_unc_g20:>10.2f}  "
              f"{row.ADD_min_sign_g20:>11.2f}")
    print("=" * 78)
