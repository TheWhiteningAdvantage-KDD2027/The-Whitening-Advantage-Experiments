"""
R09 -- anytime-valid detection on the fair-coin stream. Acceptance and reporting.

Two kinds of statement live in this file and they are kept apart deliberately.

Blocking assertions rest either on a value v87 PRINTS, compared at v87's own
printing precision, which is the classification rule, or on a deterministic
relation reimplemented here independently of the experiment -- the Wilson
interval from a second algebraic form, Ville's threshold with `logsumexp`
written out as `log(sum(exp(...)))` on a small case, the CUSUM recursion on a
hand-built sequence, the one-sided Kolmogorov statistic from a counting formula
rather than from `ksone`, and the ARL0 lower bound `censored_frac * T_EXT`
recomputed from the persisted columns. NONE rests on a value R09 produced.

WHY THE WITNESS IS NOT A BLOCKING ANCHOR. The witness value is the "published
value" column of a D0-D3 comparison, never the anchor of a blocking assertion,
because a cell-by-cell equality gate converts every legitimate correction into
a test failure whose only exit is a widened tolerance. R09's 128-bit re-keying
redraws every Monte-Carlo value of the campaign by construction, so a witness
gate here would fail on the first run. That is exactly what the three delivered
literal gates at lines 619 and 631 would have done.

THE SELF-INVALIDATING ASSERTIONS. Every test whose name contains
`does_not_reproduce` or `still_reproduces` asserts the `R09-campaign-redraw`
entry itself, at v87's printing precision. If a later campaign moves one of
those numerals across its printing boundary, the corresponding test fires and
what must then change is `docs/DEVIATIONS.md` -- the entry is opened, withdrawn
or re-scoped -- not the assertion.
"""

import ast
import math
import re
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
EXPERIMENT = ROOT / "experiments" / "R09_eprocess_anytime" / "exp_R09_eprocess_anytime.py"
DATA_DIR = ROOT / "results" / "R09_eprocess_anytime" / "data"
FIGURES_DIR = ROOT / "results" / "R09_eprocess_anytime" / "figures"
TABLES_DIR = ROOT / "results" / "R09_eprocess_anytime" / "tables"
REFERENCE_DIR = ROOT / "data" / "reference" / "R09"
LOG_PATH = ROOT / "logs" / "R09_eprocess_anytime" / "exp_R09_eprocess_anytime.log"

# --- THE PROTOCOL, RESTATED HERE RATHER THAN IMPORTED ---
# The experiment module cannot be imported from a test: its determinism
# bootstrap raises once NumPy is in sys.modules, and pytest has already loaded
# NumPy by the time this file runs. Every constant below is therefore restated
# and every relation reimplemented, which is what makes the checks independent.
ALPHAS = (0.10, 0.07, 0.05, 0.035, 0.025, 0.015, 0.01)
ETAS = (0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20)
H = 5000
TAU = 2500
T_EXT = 20000
N_CAL, N_NULL, N_ALT = 50000, 20000, 2000
DELTA_CUSUM = 0.1
ETA0_MIX_GRID = (0.05, 0.10, 0.15)
ETA0_ECUSUM = 0.10
START_GRID_SIZE = 16
C_MIX = START_GRID_SIZE * len(ETA0_MIX_GRID) * 2
MIX_W = 1.0 / C_MIX
STOPPING_PROTOCOLS = ("nominal", "extended", "peeking")
ARMS_H0 = ("CUSUM", "MIX", "eCUSUM")
PUBLISHED_H1_ARMS = ("CUSUM", "MIX")
FIGURE_ALPHA = 0.05
FIGURE_ETA = 0.10
MACRO_CENSORING_CEILING = 0.5

# =====================================================================
# ANCHORS -- EVERY ONE OF THEM PRINTED IN articleB_whitening_v87.tex
# =====================================================================
# L243: "A sign-CUSUM calibrated to $5\%$ at $H = 5{,}000$ holds there, but
# continued watching drives its realized false-alarm rate to $18\%$ by $4H$; the
# mixture martingale stays at or below $\alpha$ under the same monitoring
# ($2\times10^4$ fair-coin streams per level, Figure~\ref{fig:anytime}). The
# guarantee is not bought with delay: at matched false-alarm rate and moderate
# drift the mixture detects at least as fast as the fixed-horizon CUSUM ($409$
# vs.\ $539$ steps at $\eta = 0.10$), ceding ground only for abrupt shifts."
V87_CUSUM_PEEKING_FPR_PERCENT = 18
V87_CUSUM_CALIBRATION_PERCENT = 5
V87_H = 5000
V87_PEEKING_MULTIPLE = 4
V87_MIX_ADD_AT_PARITY = 409
V87_CUSUM_ADD_AT_PARITY = 539
V87_STREAMS_PER_LEVEL = 20000
# Figure 9 caption L559: "\textbf{(A)} Realized false-alarm rate under continuous
# monitoring (peeking over $[1, 4H]$): fixed-horizon CUSUM climbs to $18\%$,
# whereas the mixture martingale (MIX) remains bounded by $\alpha$.
# \textbf{(B)} Detection delay vs.\ drift $\eta$ ($\alpha=0.05$): MIX matches
# CUSUM speed for moderate drifts ($\eta \le 0.10$). \textbf{(C)} Average run
# length vs.\ $\alpha$: e-CUSUM satisfies $\mathrm{ARL}_0 \ge 1/\alpha$. Only MIX
# controls the time-uniform false-alarm probability."
V87_PARITY_ETA_CEILING = 0.10

# =====================================================================
# TOLERANCES, EACH DERIVED FROM A MECHANISM
# =====================================================================
# The Wilson interval is a closed form in float64 evaluated two ways. The two
# expressions differ by the reassociation of a product of at most six terms,
# bounded by 6 * eps = 1.3e-15 in relative terms; 1e-12 carries three orders of
# margin and is not derived from any observed deviation.
CLOSED_FORM_RTOL = 1e-12
# logsumexp is a shifted log-of-sum-of-exponentials over C_MIX = 96 terms. The
# shift-and-restore route and the direct route differ by the rounding of one
# exponential and one logarithm per term, i.e. by at most 2 * C_MIX * eps in
# relative terms; 1e-12 again carries three orders of margin.
LOGSUMEXP_RTOL = 1e-12
FLOAT64_EPS = float(np.finfo(np.float64).eps)

MACRO_PREFIX = "RNine"
MACRO_HEADER = "% Auto-generated by exp_R09_eprocess_anytime.py -- do not edit."


def _read(path):
    assert path.exists(), f"Missing artefact: {path}"
    return pd.read_csv(path, float_precision='round_trip')


@pytest.fixture
def validity():
    return _read(DATA_DIR / "R09_validity_stopping.csv")


@pytest.fixture
def race():
    return _read(DATA_DIR / "R09_eprocess_race.csv")


@pytest.fixture
def level():
    return _read(DATA_DIR / "R09_level_granularity.csv")


@pytest.fixture
def arl0():
    return _read(DATA_DIR / "R09_arl0.csv")


@pytest.fixture
def control_arm():
    return _read(DATA_DIR / "R09_eprocess_race_control_ecusum.csv")


@pytest.fixture
def macros():
    text = (TABLES_DIR / "R09_claims.tex").read_text()
    return dict(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}\{(.*)\}", text))


@pytest.fixture
def log_text():
    assert LOG_PATH.exists(), f"Missing log: {LOG_PATH}"
    return LOG_PATH.read_text()


@pytest.fixture
def witnesses():
    return {
        "validity": _read(REFERENCE_DIR / "protocol_22a_validity_stopping.csv"),
        "race": _read(REFERENCE_DIR / "protocol_22b_eprocess_race.csv"),
        "level": _read(REFERENCE_DIR / "protocol_22c_level_granularity.csv"),
        "arl0": _read(REFERENCE_DIR / "protocol_22d_arl0.csv"),
    }


def pick(frame, **conditions):
    """One row, matched on exact float64 equality of the coordinate columns."""
    mask = np.ones(len(frame), dtype=bool)
    for column, value in conditions.items():
        values = frame[column].to_numpy()
        if isinstance(value, float):
            mask &= np.isclose(values.astype(float), value, rtol=0.0, atol=1e-15)
        else:
            mask &= (values == value)
        assert mask.any(), f"no row with {column} == {value!r}"
    rows = frame[mask]
    assert len(rows) == 1, f"{conditions} resolves to {len(rows)} rows, not one"
    return rows.iloc[0]


# =====================================================================
# INDEPENDENT REIMPLEMENTATIONS
# =====================================================================

def wilson_score_interval(k, n, confidence=0.95):
    """
    The Wilson score interval from the CLOSED-FORM ROOTS of the score equation,

        (2 n p + z^2 -/+ z sqrt(z^2 + 4 n p (1 - p))) / (2 (n + z^2)),

    which is algebraically the same interval the experiment writes as a centre
    plus a margin, evaluated through a different sequence of operations.
    """
    if n == 0:
        return 0.0, 0.0
    z = float(stats.norm.ppf(1 - (1 - confidence) / 2))
    p = k / n
    root = z * math.sqrt(z**2 + 4 * n * p * (1 - p))
    denominator = 2 * (n + z**2)
    low = (2 * n * p + z**2 - root) / denominator
    high = (2 * n * p + z**2 + root) / denominator
    return max(0.0, low), min(1.0, high)


def log_mixture_value(log_components):
    """
    log(sum(exp(x))) written out, without the shift-and-restore of
    `scipy.special.logsumexp`. Used on a small case only, where no term
    overflows, which is the point: it exhibits that the experiment's threshold
    test `logE >= -log(alpha)` is the test `E >= 1/alpha` on the mixture value.
    """
    return float(np.log(np.sum(np.exp(np.asarray(log_components, dtype=float)))))


def cusum_path(y, delta=DELTA_CUSUM):
    """
    The two-sided sign-CUSUM recursion, written out step by step on a hand-built
    binary sequence. Returns the running statistic M_t.
    """
    s_pos = 0.0
    s_neg = 0.0
    path = []
    for value in y:
        dev = float(value) - 0.5
        s_pos = max(0.0, s_pos + dev - delta)
        s_neg = max(0.0, s_neg - dev - delta)
        path.append(max(s_pos, s_neg))
    return np.array(path)


def dplus_by_counting(u):
    """
    D+ = sup_x (F_n(x) - x) from a COUNTING formula: the supremum of a
    right-continuous step function minus the identity is attained at a sample
    point, so it suffices to evaluate F_n at every observation. The experiment
    computes the same quantity from the sorted order statistics.
    """
    u = np.asarray(u, dtype=float)
    n = len(u)
    return float(max(0.0, max((np.count_nonzero(u <= x) / n) - x for x in u)))


# =====================================================================
# BLOCKING -- THE ARTEFACTS THE PROMPT LISTS, AND THEIR SCHEMAS
# =====================================================================

def test_R09_every_artefact_the_prompt_lists_exists_with_its_prescribed_schema(
        validity, race, level, arl0, control_arm, macros):
    """
    Section 3 of the R09 prompt maps `protocol_22a`-`protocol_22d` onto four
    CSVs under `results/R09_eprocess_anytime/data/`, plus the figure and the
    macro table. The audit-only control arm of the plan's decision D3 is the
    fifth CSV and its NAME stamps the branch.
    """
    assert (FIGURES_DIR / "fig09_anytime_valid.png").exists()
    assert (TABLES_DIR / "R09_claims.tex").exists()
    assert LOG_PATH.exists()

    assert len(validity) == len(ARMS_H0) * len(ALPHAS) * len(STOPPING_PROTOCOLS) == 63
    for column in ("arm", "alpha", "stopping_protocol", "guarantee_type", "threshold",
                   "N_streams", "FPR", "CI_low", "CI_high", "bound_target", "bound_respected",
                   "binom_p_one_sided"):
        assert column in validity.columns
    assert set(validity["arm"]) == set(ARMS_H0)
    assert set(validity["stopping_protocol"]) == set(STOPPING_PROTOCOLS)

    assert len(race) == len(PUBLISHED_H1_ARMS) * len(ALPHAS) * len(ETAS) == 140
    assert set(race["arm"]) == set(PUBLISHED_H1_ARMS), (
        "v87 draws panel B with TWO curves and its caption names only CUSUM and MIX; the R09 "
        "prompt's section 5 C4 transposes panel C's three arms onto panel B, which is a "
        "specification defect of the prompt and not of the manuscript")

    assert len(level) == 2 * len(ALPHAS) == 14
    assert len(arl0) == len(ARMS_H0) * len(ALPHAS) == 21

    assert len(control_arm) == len(ALPHAS) * len(ETAS) == 70
    assert set(control_arm["arm"]) == {"eCUSUM"}, (
        "preamble S4.3 requires a branch outside the published path to be stamped in the output "
        "name AND in the data; the filename carries `_control_ecusum` and the `arm` column "
        "carries eCUSUM")
    assert list(control_arm.columns) == list(race.columns)

    assert len(macros) == 7, f"the plan fixes exactly seven macros, found {len(macros)}"


def test_R09_every_sample_size_the_campaign_used_is_carried_on_the_row(validity, race, level,
                                                                       arl0):
    """
    v87's Figure 9 caption gives ONE stream count for three panels drawn from
    three different samples. The repository carries the count on every row so
    that no reader has to take the caption's single number for all of them.
    This is the measurement behind `R09_v87_stream_counts.md`.
    """
    assert set(validity["N_streams"]) == {N_NULL}
    assert set(race["N_streams"]) == {N_ALT}
    assert N_NULL == V87_STREAMS_PER_LEVEL, (
        "L243's '2x10^4 fair-coin streams per level' scopes the count to the H0 arm, and a "
        "fair-coin stream is by definition an H0 stream")
    assert N_ALT != N_NULL, (
        "panel B is drawn from a different and smaller sample than panels A and C; the caption's "
        "single '2x10^4 streams per cell' does not describe it")
    # The SEM/Wilson resolution ratio the decision buys, stated as a relation
    # and not as a measured number.
    assert math.isclose(math.sqrt(N_NULL / N_ALT), math.sqrt(10.0), rel_tol=1e-12)


# =====================================================================
# BLOCKING -- WHAT v87 PRINTS
# =====================================================================

def test_R09_the_mixture_martingale_remains_bounded_by_alpha_under_continuous_monitoring(
        validity):
    """
    L243 and the Figure 9 caption: "the mixture martingale stays at or below
    $\\alpha$ under the same monitoring" / "remains bounded by $\\alpha$". This
    is the stream's central published claim and it is asserted at every level of
    the grid, not only at the figure's operating point.
    """
    peeking = validity[validity["stopping_protocol"] == "peeking"]
    mix = peeking[peeking["arm"] == "MIX"]
    assert len(mix) == len(ALPHAS)
    offending = mix[mix["FPR"].to_numpy() > mix["alpha"].to_numpy()]
    assert len(offending) == 0, (
        f"MIX exceeds its own nominal level under peeking at "
        f"{list(offending['alpha'])}; Ville's bound is what v87 prints and this would falsify it")


def test_R09_only_the_mixture_controls_the_time_uniform_rate(validity):
    """
    Figure 9 caption: "Only MIX controls the time-uniform false-alarm
    probability." The claim has two halves and both are asserted: the CUSUM
    peeking rate exceeds the MIX one at every level, and the e-CUSUM peeking
    rate does not control anything at the figure's operating point.
    """
    peeking = validity[validity["stopping_protocol"] == "peeking"]
    for a in ALPHAS:
        cusum = pick(peeking, arm="CUSUM", alpha=a)
        mix = pick(peeking, arm="MIX", alpha=a)
        assert cusum["FPR"] > mix["FPR"], (
            f"at alpha = {a} the fixed-horizon CUSUM peeking rate {cusum['FPR']} does not exceed "
            f"the mixture's {mix['FPR']}")
    ecusum = pick(peeking, arm="eCUSUM", alpha=FIGURE_ALPHA)
    assert ecusum["FPR"] > FIGURE_ALPHA, (
        "the e-CUSUM arm is documentary in panel A: it is an ARL0 device, not a level-alpha test, "
        "and its peeking rate is what makes the caption's 'only MIX' true")


def test_R09_the_ecusum_arl0_satisfies_the_reciprocal_of_alpha(arl0):
    """
    Figure 9 caption panel C: "e-CUSUM satisfies $\\mathrm{ARL}_0 \\ge 1/\\alpha$".
    The comparison is REWRITTEN here from the persisted `ARL0_mean` and
    `ref_inv_alpha`, independently of the `arl0_bound_respected` column, which
    is the second half of control C2.
    """
    ecusum = arl0[arl0["arm"] == "eCUSUM"]
    assert len(ecusum) == len(ALPHAS)
    for row in ecusum.itertuples(index=False):
        assert math.isclose(row.ref_inv_alpha, 1.0 / row.alpha, rel_tol=1e-15)
        assert row.ARL0_mean >= row.ref_inv_alpha, (
            f"e-CUSUM ARL0 {row.ARL0_mean} is below 1/alpha = {row.ref_inv_alpha} at "
            f"alpha = {row.alpha}")
        assert bool(row.arl0_bound_respected) == (row.ARL0_mean >= 1.0 / row.alpha)


def test_R09_the_peeking_horizon_is_four_times_the_calibration_horizon(validity, arl0):
    """
    L243 and the caption both say "by $4H$" / "peeking over $[1, 4H]$" at
    `H = 5,000`. The nominal protocol stops at `H` and the peeking protocol at
    `4H`, so the peeking rate must dominate the nominal one arm by arm and level
    by level -- `{fa <= H}` is a subset of `{fa <= 4H}`. That is structural, and
    a violation would mean the two protocols are not nested.
    """
    assert T_EXT == V87_PEEKING_MULTIPLE * V87_H == 20000
    for arm in ARMS_H0:
        for a in ALPHAS:
            nominal = pick(validity, arm=arm, alpha=a, stopping_protocol="nominal")
            peeking = pick(validity, arm=arm, alpha=a, stopping_protocol="peeking")
            extended = pick(validity, arm=arm, alpha=a, stopping_protocol="extended")
            assert peeking["FPR"] >= nominal["FPR"]
            assert peeking["FPR"] >= extended["FPR"]


# =====================================================================
# BLOCKING -- INDEPENDENT REIMPLEMENTATIONS
# =====================================================================

def test_R09_every_wilson_interval_is_the_score_interval_of_its_own_rate(validity, race, level):
    """
    The intervals are recomputed from the closed-form roots of the score
    equation, a different sequence of float64 operations from the centre plus
    margin the experiment writes. Every persisted bound must also be clamped
    into [0, 1].
    """
    for row in validity.itertuples(index=False):
        low, high = wilson_score_interval(int(round(row.FPR * row.N_streams)), int(row.N_streams))
        assert abs(row.CI_low - low) <= CLOSED_FORM_RTOL * max(1.0, low)
        assert abs(row.CI_high - high) <= CLOSED_FORM_RTOL * max(1.0, high)
    for row in race.itertuples(index=False):
        low, high = wilson_score_interval(int(round(row.DetRate * row.N_streams)),
                                          int(row.N_streams))
        assert abs(row.DetRate_CI_low - low) <= CLOSED_FORM_RTOL * max(1.0, low)
        assert abs(row.DetRate_CI_high - high) <= CLOSED_FORM_RTOL * max(1.0, high)
    for row in level.itertuples(index=False):
        low, high = wilson_score_interval(int(round(row.achieved_level * N_NULL)), N_NULL)
        assert abs(row.achieved_CI_low - low) <= CLOSED_FORM_RTOL * max(1.0, low)
        assert abs(row.achieved_CI_high - high) <= CLOSED_FORM_RTOL * max(1.0, high)
    for frame, columns in ((validity, ("CI_low", "CI_high")),
                           (race, ("DetRate_CI_low", "DetRate_CI_high")),
                           (level, ("achieved_CI_low", "achieved_CI_high"))):
        assert (frame[columns[0]] >= 0.0).all()
        assert (frame[columns[1]] <= 1.0).all()
        assert (frame[columns[0]] <= frame[columns[1]]).all()


def test_R09_the_mixture_threshold_is_villes_threshold_on_the_mixture_value():
    """
    The experiment tests `logsumexp(logM, axis=1) >= -log(alpha)`. Written out
    on a small case with `log(sum(exp(...)))`, that is exactly `E >= 1/alpha`,
    which is the event Ville's inequality bounds. The equivalence is asserted,
    not asserted-about.
    """
    rng = np.random.default_rng(0)
    log_components = np.log(MIX_W) + rng.normal(0.0, 2.0, size=C_MIX)
    direct = log_mixture_value(log_components)
    from scipy.special import logsumexp
    assert abs(direct - float(logsumexp(log_components))) <= LOGSUMEXP_RTOL * max(1.0, abs(direct))
    mixture_value = float(np.sum(np.exp(log_components)))
    for a in ALPHAS:
        assert (direct >= -math.log(a)) == (mixture_value >= 1.0 / a)
    # A mixture that has not started holds value 1 in every component, so E_0 is
    # exactly 1 and Ville's inequality applies with E_0 / c = 1 / c.
    unstarted = np.full(C_MIX, math.log(MIX_W))
    assert abs(math.exp(log_mixture_value(unstarted)) - 1.0) <= C_MIX * FLOAT64_EPS


def test_R09_the_cusum_statistic_lives_on_the_two_delta_lattice():
    """
    The CUSUM recursion on a hand-built sequence. `dev - DELTA_CUSUM` takes
    `+0.4` when `y = 1` and `-0.6` when `y = 0`, so every partial sum is an
    integer multiple of `2 * DELTA_CUSUM = 0.2` and the threshold can only be
    placed on that lattice. This is why `level_is_attainable` is `False` on the
    CUSUM rows of `R09_level_granularity.csv`, and it is the
    `R03-cusum-nominal-level` and `R07-lambda-star-estimator` situation.
    """
    step = 2 * DELTA_CUSUM
    assert math.isclose(1.0 - 0.5 - DELTA_CUSUM, 0.4, abs_tol=1e-15)
    assert math.isclose(0.0 - 0.5 - DELTA_CUSUM, -0.6, abs_tol=1e-15)
    y = [1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1]
    path = cusum_path(y)
    units = path / step
    assert np.max(np.abs(units - np.round(units))) <= len(y) * FLOAT64_EPS / step
    # Hand computation of the first four steps of the positive arm:
    # 0.4, 0.8, 1.2, then max(0, 1.2 - 0.6) = 0.6.
    assert np.allclose(path[:4], [0.4, 0.8, 1.2, 0.6], rtol=0.0, atol=1e-12)
    # The alarm event over a horizon is the running maximum crossing, which is
    # the identity the experiment's structural cross-check asserts.
    for threshold in (0.2, 0.6, 1.2, 5.0):
        crossed = bool(np.any(path >= threshold))
        assert crossed == (float(np.max(path)) >= threshold)


def test_R09_the_one_sided_kolmogorov_statistic_is_the_supremum_it_names(log_text):
    """
    `D+` reimplemented from a COUNTING formula and cross-checked against
    `scipy.stats.kstest(..., alternative='greater')`, whose exact tail is the
    `ksone` survival function control C3 quotes. Then the value C3 reports in the
    log is checked for internal consistency: the p-value beside it must be
    `ksone.sf(D+, N_NULL)`.
    """
    rng = np.random.default_rng(1)
    for sample in (rng.random(200), rng.random(200)**2, np.sqrt(rng.random(200))):
        mine = dplus_by_counting(sample)
        reference = float(stats.kstest(sample, 'uniform', alternative='greater').statistic)
        assert abs(mine - reference) <= 1e-15
        assert abs(float(stats.kstest(sample, 'uniform', alternative='greater').pvalue)
                   - float(stats.ksone.sf(mine, len(sample)))) <= 1e-12

    match = re.search(r"C3 \[MIX, H0 campaign\] D\+ = ([0-9.eE+-]+) on n = (\d+), exact one-sided "
                      r"p = ([0-9.eE+-]+)", log_text)
    assert match is not None, "the log carries no C3 result line for the MIX arm"
    d_plus, n, p_value = float(match.group(1)), int(match.group(2)), float(match.group(3))
    assert n == N_NULL
    assert abs(float(stats.ksone.sf(d_plus, n)) - p_value) <= 1e-12
    assert p_value >= 0.01, (
        "C3 gates at the 1% level on the MIX arm: a rejection means Ville's bound is not respected "
        "uniformly over the level range, which the plan's halt condition classifies as a D3")


def test_R09_the_arl0_lower_bound_is_recomputed_from_the_persisted_columns(arl0):
    """
    `ARL0_mean = mean(min(fa, T_EXT))` is bounded below by
    `censored_frac * T_EXT`, because every censored replicate contributes
    exactly `T_EXT` and every other contributes a non-negative number. The bound
    is recomputed here from the persisted columns and compared with the
    experiment's own `arl0_implied_lower_bound`, and it is what makes
    `arl0_bound_respected` arithmetically necessary on the censored arms
    (control C2 and decision D4).
    """
    for row in arl0.itertuples(index=False):
        implied = row.censored_frac * T_EXT
        assert abs(row.arl0_implied_lower_bound - implied) <= 1e-9 * max(1.0, implied)
        assert row.ARL0_mean >= implied - 1e-9 * max(1.0, implied)
        assert bool(row.bound_flag_carried_information) == (implied < 1.0 / row.alpha)
    # The flag carries information on the e-CUSUM arm alone: everywhere else the
    # censoring already forces the comparison.
    informative = arl0[arl0["bound_flag_carried_information"]]
    assert set(informative["arm"]) == {"eCUSUM"}, (
        "on the CUSUM and MIX rows censored_frac * T_EXT already exceeds 1/alpha, so "
        "`arl0_bound_respected` could not have been False whatever the campaign measured")


# =====================================================================
# BLOCKING -- THE CONTROLS AS ACCEPTANCE CRITERIA
# =====================================================================

def test_R09_no_arl0_is_persisted_without_its_censored_fraction(arl0):
    """
    C1 as an acceptance criterion. The mean of a right-censored run length is
    a HORIZON ARTEFACT rather than a measurement, and a reader who meets it
    without its censored fraction cannot tell the two apart. The mechanism, not
    an observed count, is what makes this blocking.
    """
    assert "censored_frac" in arl0.columns
    assert arl0["ARL0_mean"].notna().all()
    assert arl0["censored_frac"].notna().all()
    assert (arl0["censored_frac"] >= 0.0).all()
    assert (arl0["censored_frac"] <= 1.0).all()
    assert (arl0["right_censored_flag"] == (arl0["censored_frac"] > 0.05)).all()
    # The confidence interval of a censored mean is persisted beside it, so no
    # ARL0 quantity reaches a reader unqualified.
    assert (arl0["ARL0_CI_low"] <= arl0["ARL0_mean"]).all()
    assert (arl0["ARL0_CI_high"] >= arl0["ARL0_mean"]).all()


def test_R09_the_macro_emitter_refuses_a_censored_arl0(arl0, macros):
    """
    Section 2.3 of the R09 prompt, enforced in code rather than by convention.
    The guard is asserted twice: on the emitted macro, whose source row must sit
    at or below the ceiling, and on the emitter's source, which must exit rather
    than warn.
    """
    ecusum = arl0[arl0["arm"] == "eCUSUM"]
    source_row = ecusum.loc[ecusum["ARL0_mean"].idxmin()]
    assert float(source_row["censored_frac"]) <= MACRO_CENSORING_CEILING
    assert math.isclose(float(macros["RNineEcusumArlZeroMin"]),
                        float(source_row["ARL0_mean"]), abs_tol=5e-3)
    # No CUSUM or MIX ARL0 is macro-emitted at all: those means are horizon
    # artefacts at 65-99% right-censoring.
    text = (TABLES_DIR / "R09_claims.tex").read_text()
    assert not re.search(r"\\newcommand\{\\RNine(Cusum|Mix)ArlZero", text)
    for arm in ("CUSUM", "MIX"):
        assert float(arl0[arl0["arm"] == arm]["censored_frac"].max()) > MACRO_CENSORING_CEILING, (
            "if the CUSUM or MIX censoring ever fell below the ceiling, the reason those ARL0 "
            "means are withheld would have changed and docs/DEVIATIONS.md is what must be revised")
    experiment = EXPERIMENT.read_text()
    assert "MACRO_CENSORING_CEILING" in experiment
    guard = re.search(r"if float\(arl0_row\[.censored_frac.\]\) > MACRO_CENSORING_CEILING:"
                      r"(.|\n)*?sys\.exit\(1\)", experiment)
    assert guard is not None, (
        "the section 2.3 guard must exit, not warn: a degraded path that produces a "
        "normal-looking result is the gravest defect the preamble names")


def test_R09_the_bound_flag_is_a_computed_comparison_not_a_literal(arl0):
    """
    C2's second half, written independently of the experiment's own AST check.
    A boolean that is constant over a whole file is either a definitional
    tautology or a literal; this one is neither, and the way to show it is to
    recompute it and to exhibit the arithmetic that makes it necessary.
    """
    recomputed = arl0["ARL0_mean"].to_numpy() >= arl0["ref_inv_alpha"].to_numpy()
    assert np.array_equal(arl0["arl0_bound_respected"].to_numpy().astype(bool), recomputed)
    experiment = EXPERIMENT.read_text()
    assert '"arl0_bound_respected": arl0 >= (1.0 / a),' in experiment, (
        "the producing line must be a comparison against the reciprocal of alpha")
    assert experiment.count('"arl0_bound_respected": ') == 1


def test_R09_the_level_granularity_column_states_the_lattice_it_names(level):
    """
    `level_is_attainable` is computed, not typed. The CUSUM threshold is a
    quantile of a statistic on the `2 * DELTA_CUSUM` lattice, so the nominal
    level is reachable only if some lattice survival value equals it exactly;
    the MIX threshold is `-log(alpha)`, an exact function of alpha with no
    calibration sample and therefore no lattice.
    """
    cusum = level[level["arm"] == "CUSUM"]
    mix = level[level["arm"] == "MIX"]
    assert len(cusum) == len(mix) == len(ALPHAS)
    assert not cusum["level_is_attainable"].any(), (
        "the CUSUM level moves in steps of the lattice survival function; if a level ever became "
        "exactly attainable, the R03-cusum-nominal-level reading would have changed")
    assert mix["level_is_attainable"].all()
    for row in level.itertuples(index=False):
        assert math.isclose(row.gap_pp, (row.achieved_level - row.target_level) * 100,
                            rel_tol=1e-12, abs_tol=1e-12)
        assert math.isclose(row.target_level, row.alpha, rel_tol=0.0, abs_tol=0.0)


def test_R09_the_descriptive_binomial_p_values_are_the_exact_one_sided_tail(validity):
    """
    S4bis point 3: the per-level p-values are persisted DESCRIPTIVELY and are
    not an acceptance criterion. They are recomputed here from
    `scipy.stats.binom` against the count the FPR column implies.
    """
    for row in validity.itertuples(index=False):
        crosses = int(round(row.FPR * row.N_streams))
        expected = float(stats.binom.sf(crosses - 1, int(row.N_streams), row.alpha))
        assert abs(row.binom_p_one_sided - expected) <= 1e-12 * max(1.0, expected)
    assert (validity["binom_p_one_sided"] >= 0.0).all()
    assert (validity["binom_p_one_sided"] <= 1.0).all()


def test_R09_the_add_column_is_conditional_and_the_detection_rate_says_so(race, control_arm):
    """
    ADD is a mean over `(fa > TAU) & (fa <= H)`. The detection rate on the same
    row is what lets a reader price that conditioning, and it is what makes the
    marginal comparison at small `eta` un-readable on its own -- which is why
    control C4's primary instrument is a matched-detection-rate quantile and not
    this column.
    """
    # The PUBLISHED frame has an alarm inside the window at every cell, so no ADD
    # is missing there. The AUDIT-ONLY control frame does not, and that is a
    # property of e-CUSUM rather than a defect: its H0 ARL0 is 206 and 319 steps
    # at alpha = 0.10 and 0.07 against a change point at TAU = 2500, so no stream
    # survives to TAU un-alarmed and the cell is empty. A mean over an empty set
    # is NaN, never a number invented to fill it. The relation is asserted as an
    # EQUIVALENCE in both directions rather than as a blanket non-null.
    assert race["ADD"].notna().all()
    assert race["SEM"].notna().all()
    assert (control_arm["ADD"].isna() == (control_arm["DetRate"] == 0.0)).all(), (
        "the control arm's ADD must be missing exactly where no stream alarmed in (TAU, H]; a "
        "NaN anywhere else, or a number where the cell is empty, is a defect")
    assert (control_arm["SEM"].isna() == (control_arm["DetRate"] == 0.0)).all()
    for frame in (race, control_arm):
        populated = frame[frame["DetRate"] > 0.0]
        assert (populated["ADD"] > 0).all()
        assert (populated["ADD"] <= H - TAU).all(), (
            "an alarm is only counted when it lands in (TAU, H], so the delay cannot exceed "
            "H - TAU")
        assert (frame["DetRate"] >= 0.0).all()
        assert (frame["DetRate"] <= 1.0).all()
    # The two arms of panel B do NOT detect the same streams: at the smallest
    # drift their rates differ by a factor that makes the conditional means
    # incomparable, which is the confounder C4 resolves by measurement.
    cell = race[np.isclose(race["alpha"].to_numpy(dtype=float), FIGURE_ALPHA, rtol=0.0, atol=1e-15)]
    small = cell[np.isclose(cell["eta"].to_numpy(dtype=float), min(ETAS), rtol=0.0, atol=1e-15)]
    rates = dict(zip(small["arm"], small["DetRate"]))
    assert max(rates.values()) / min(rates.values()) > 1.5, (
        "the conditioning confounder C4 is built around has disappeared; if the two arms now "
        "detect at comparable rates at the smallest drift, AUDIT_R09.md's reading changes")


# =====================================================================
# BLOCKING -- THE MACROS
# =====================================================================

def test_R09_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix(macros):
    text = (TABLES_DIR / "R09_claims.tex").read_text()
    assert text.startswith(MACRO_HEADER)
    for line in text.splitlines():
        assert line.startswith("%") or line.startswith("\\newcommand"), (
            f"R09_claims.tex carries a line that is neither a comment nor a \\newcommand: {line!r}")
    assert macros, "R09_claims.tex carries no macro"
    for name, body in macros.items():
        assert name.startswith(MACRO_PREFIX), (
            f"{name} does not carry the cardinal prefix {MACRO_PREFIX}. The repository "
            f"uses cardinals throughout (ROne ... RSix, RSeven, REleven, RThirteen, "
            f"RSixteen, REighteen).")
        assert 'nan' not in body.lower(), f"macro {name} carries the body {body!r}"
        assert body.strip() != ""
    assert text.count("RNinth") == 0, "cardinal, never ordinal"


def test_R09_the_macros_agree_with_the_frames_they_are_computed_from(macros, validity, race,
                                                                     arl0):
    """
    Every macro recomputed from the persisted frame. The first two are a maximum
    over the THREE STOPPING PROTOCOLS at the figure's operating point, never
    over the alpha grid, and the test asserts that distinction rather than
    trusting the comment that states it.
    """
    cell = validity[np.isclose(validity["alpha"].to_numpy(dtype=float), FIGURE_ALPHA,
                               rtol=0.0, atol=1e-15)]
    cusum_max = float(cell[cell["arm"] == "CUSUM"]["FPR"].max())
    mix_max = float(cell[cell["arm"] == "MIX"]["FPR"].max())
    assert macros["RNineCusumPeekingFprMax"] == f"{100.0 * cusum_max:.1f}\\%"
    assert macros["RNineMixPeekingFprMax"] == f"{100.0 * mix_max:.1f}\\%"
    # The maximum is the PEEKING bar, structurally: the other two protocols read
    # subsets of the same event.
    assert cusum_max == float(pick(cell, arm="CUSUM", stopping_protocol="peeking")["FPR"])
    assert mix_max == float(pick(cell, arm="MIX", stopping_protocol="peeking")["FPR"])
    # And it is NOT the maximum over the alpha grid, which is larger.
    peeking = validity[validity["stopping_protocol"] == "peeking"]
    assert float(peeking[peeking["arm"] == "CUSUM"]["FPR"].max()) > cusum_max, (
        "CUSUM's peeking rate is larger at alpha = 0.10 than at the figure's operating point; a "
        "macro named `...FprMax` must not be read as a maximum over the level grid")

    cell = race[np.isclose(race["alpha"].to_numpy(dtype=float), FIGURE_ALPHA, rtol=0.0, atol=1e-15)]
    add_cusum = cell[cell["arm"] == "CUSUM"].set_index("eta")["ADD"]
    add_mix = cell[cell["arm"] == "MIX"].set_index("eta")["ADD"]
    parity = [eta for eta in ETAS if add_mix.loc[eta] <= add_cusum.loc[eta]]
    assert macros["RNineMixDriftParityThreshold"] == f"{max(parity):.2f}"

    ecusum = arl0[arl0["arm"] == "eCUSUM"]
    assert macros["RNineEcusumArlZeroMin"] == f"{float(ecusum['ARL0_mean'].min()):.2f}"
    for arm, name in (("eCUSUM", "RNineEcusumCensoredFracMax"),
                      ("CUSUM", "RNineCusumCensoredFracMax"),
                      ("MIX", "RNineMixCensoredFracMax")):
        expected = float(arl0[arl0["arm"] == arm]["censored_frac"].max())
        assert macros[name] == f"{expected:.4f}"


def test_R09_the_ecusum_censored_fraction_is_not_zero(macros, arl0, witnesses):
    """
    The R09 prompt's section 4 says "(0 expected)" and its section 2 says "against
    `0.0000` for eCUSUM". The SUBMITTED `protocol_22d` already carries a
    non-zero e-CUSUM censored fraction, so the premise is wrong about the
    witness before any regeneration. This is reported in AUDIT_R09.md under
    findings that revise the prompt's own premises; no manuscript claim is
    affected, because v87 prints no censored fraction.
    """
    witness_max = float(witnesses["arl0"][witnesses["arl0"]["arm"] == "eCUSUM"][
        "censored_frac"].max())
    assert witness_max > 0.0, (
        "the prompt's premise is that e-CUSUM censoring is 0 in the submitted campaign; if that "
        "became true, the finding recorded in AUDIT_R09.md would be withdrawn")
    assert float(macros["RNineEcusumCensoredFracMax"]) >= 0.0


# =====================================================================
# BLOCKING -- FILE HYGIENE THE PREAMBLE IMPOSES
# =====================================================================

def test_R09_every_produced_text_file_ends_in_a_newline():
    """
    File assembly by concatenation requires every text file to end with a
    newline; a missing newline glues two dependencies onto one line.
    """
    for path in (TABLES_DIR / "R09_claims.tex",
                 ROOT / "requirements" / "R09.txt",
                 ROOT / "docs" / "sections" / "R09.md",
                 ROOT / "docs" / "audits" / "AUDIT_R09.md",
                 DATA_DIR / "R09_validity_stopping.csv",
                 DATA_DIR / "R09_eprocess_race.csv",
                 DATA_DIR / "R09_level_granularity.csv",
                 DATA_DIR / "R09_arl0.csv",
                 DATA_DIR / "R09_eprocess_race_control_ecusum.csv"):
        assert path.exists(), f"Missing deliverable: {path}"
        assert path.read_text().endswith("\n"), f"{path} does not end in a newline"


def test_R09_the_produced_sources_and_logs_carry_no_confirmatory_language():
    """
    Banned words attribute the value of a proof to a measurement; neutral
    technical uses remain valid and none of them matches this pattern.
    """
    pattern = re.compile(
        r"proves|proven|perfectly valid|validates the (theorem|thesis|claim)|confirms the|"
        r"as expected|triumph|victory|irrefutable|brilliant", re.IGNORECASE)
    targets = [EXPERIMENT,
               ROOT / "docs" / "sections" / "R09.md",
               ROOT / "docs" / "audits" / "AUDIT_R09.md",
               LOG_PATH]
    for path in targets:
        assert path.exists(), f"Missing deliverable: {path}"
        hits = [line for line in path.read_text().splitlines() if pattern.search(line)]
        assert not hits, f"{path.name} carries confirmatory language: {hits[:3]}"


def test_R09_the_produced_sources_carry_no_banned_construct():
    """No `iterrows`, no bare `except:`, no absolute path."""
    text = EXPERIMENT.read_text()
    assert "iterrows" not in text
    assert not re.search(r"except\s*:", text)
    assert not re.search(r"['\"]/home/", text), "no absolute path may be embedded"
    # `--fast` must not be REACHABLE, which is a statement about the parser and not
    # about the prose: the module docstring records that the delivered flag was
    # dropped, and a substring test would fire on that record. The option strings
    # are read out of the AST, so the assertion is on what argparse exposes.
    options = set()
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "add_argument":
            options.update(arg.value for arg in node.args
                           if isinstance(arg, ast.Constant) and isinstance(arg.value, str))
    assert options == {"--n-jobs", "--control-arms"}, (
        f"the parser exposes {sorted(options)}; the delivered `--fast` is a second, unstamped "
        f"parameter set reachable by a flag, and the repository certifies one configuration")


def test_R09_the_orchestrator_passes_the_control_arm_and_never_calls_pytest():
    """
    `run_experiment_RXX.sh` exports PYTHONHASHSEED before any call to Python
    and never runs the test suite. The certified run must pass `--control-arms ecusum`
    explicitly, so the audit-only branch is produced by the certified command
    rather than by hand.
    """
    script = (ROOT / "run_experiment_R09.sh").read_text()
    assert 'export PYTHONHASHSEED="42"' in script
    # The statement is about what the script EXECUTES. Its header comment records
    # that the suite is run_tests.sh's remit, and a substring test over the whole
    # file would fire on that record, so the comments are stripped first.
    executable = "\n".join(line for line in script.splitlines()
                           if line.strip() and not line.lstrip().startswith("#"))
    assert "pytest" not in executable, (
        "run_experiment_R09.sh must never run the test suite; that is run_tests.sh's remit")
    assert "--control-arms ecusum" in executable
    assert script.index('export PYTHONHASHSEED="42"') < script.index("python3")


def test_R09_the_shared_orchestrators_are_untouched():
    """
    `run_all.sh` and `run_tests.sh` are shared files that R09 never edits.

    `run_all.sh` no longer discovers the runners by sorted enumeration: the data
    dependency graph recorded in `EXPERIMENTS_SCRIPTS_DEPENDENCIES.md` makes a
    version sort invalid (R18 -> R10 -> R08 and R16 -> R13 are both violated by
    it), so the file now carries an explicit topological order. That is a
    repository-level change, not a stream edit, and the invariant this test
    protects is unchanged: R09 must appear there exactly as every other stream
    does, and nowhere else.

    The assertion is strictly stronger than the substring absence it replaces --
    it now also rules out a duplicated entry, a hard-coded runner path and a
    hard-coded slug, none of which the old form could see.
    """
    assert re.fullmatch(r"run_experiment_R[0-9]{2}[a-z]?\.sh", "run_experiment_R09.sh")

    run_all = (ROOT / "run_all.sh").read_text()
    order = re.findall(r'\bR[0-9]{2}[a-z]?\b', run_all)

    assert order.count("R09") == 1, (
        "R09 must appear exactly once in run_all.sh, as one element of the "
        f"topological order; found {order.count('R09')}")
    assert "R09" in order
    assert "run_experiment_R09" not in run_all, (
        "run_all.sh must not hard-code R09's runner path")
    assert "R09_eprocess_anytime" not in run_all, (
        "run_all.sh must not hard-code R09's slug")
    assert "--control-arms" not in run_all, (
        "run_all.sh must not pass R09-specific arguments")

    # The order must be a superset of every canonical runner present on disk:
    # a stream silently dropped from the list would never run.
    on_disk = sorted(
        p.name[len("run_experiment_"):-len(".sh")]
        for p in ROOT.glob("run_experiment_R*.sh")
        if re.fullmatch(r"run_experiment_R[0-9]{2}[a-z]?\.sh", p.name))
    missing = [s for s in on_disk if s not in order]
    assert not missing, f"streams present on disk but absent from run_all.sh: {missing}"

    assert "R09" not in (ROOT / "run_tests.sh").read_text()


# =====================================================================
# SELF-INVALIDATING -- THESE ASSERT THE DEVIATION, NOT THE AGREEMENT
# =====================================================================

def test_R09_the_three_monte_carlo_numerals_of_L243_does_not_reproduce_at_printed_precision():
    """
    SELF-INVALIDATING. This asserts `docs/DEVIATIONS.md` `R09-campaign-redraw`
    itself: the 128-bit re-keying moves `18\\%`, `409` and `539` across v87's own
    printing boundary. If a later campaign restores any of the three, this test
    fires and what must change is `docs/DEVIATIONS.md` -- the entry is re-scoped
    or withdrawn -- never the assertion.

    No tolerance is asserted on the SIZE of any move. The peeking rate sits
    `+4.77` standard errors from the submitted value, because `lambda*` moved one
    step of the `2 * DELTA_CUSUM` lattice, and an `|z| <= 3` gate here would be a
    tolerance chosen after seeing the number (preamble S4.8). The displacement is
    asserted; its magnitude is characterised in AUDIT_R09.md.
    """
    validity = _read(DATA_DIR / "R09_validity_stopping.csv")
    race = _read(DATA_DIR / "R09_eprocess_race.csv")

    peeking = pick(validity, arm="CUSUM", alpha=FIGURE_ALPHA, stopping_protocol="peeking")
    assert round(100 * float(peeking["FPR"])) != V87_CUSUM_PEEKING_FPR_PERCENT, (
        f"the regenerated peeking rate {peeking['FPR']} rounds to v87's printed "
        f"{V87_CUSUM_PEEKING_FPR_PERCENT}%; R09-campaign-redraw no longer covers it")

    for arm, printed in (("MIX", V87_MIX_ADD_AT_PARITY), ("CUSUM", V87_CUSUM_ADD_AT_PARITY)):
        cell = pick(race, arm=arm, alpha=FIGURE_ALPHA, eta=FIGURE_ETA)
        assert round(float(cell["ADD"])) != printed, (
            f"the regenerated {arm} delay {cell['ADD']} rounds to v87's printed {printed}; "
            f"R09-campaign-redraw no longer covers it")


def test_R09_the_calibrated_level_and_the_stream_count_still_reproduces_v87s_numerals():
    """
    SELF-INVALIDATING, in the other direction. L243's "calibrated to $5\\%$ at
    $H = 5{,}000$" and "$2\\times10^4$ fair-coin streams per level" survive the
    re-keying at v87's printing precision, which is why `R09-campaign-redraw`
    names three numerals and not five. If either stops reproducing, a fourth
    numeral joins the register entry and this test is what says so.
    """
    level = _read(DATA_DIR / "R09_level_granularity.csv")
    validity = _read(DATA_DIR / "R09_validity_stopping.csv")

    cusum = pick(level, arm="CUSUM", alpha=FIGURE_ALPHA)
    assert round(100 * float(cusum["achieved_level"])) == V87_CUSUM_CALIBRATION_PERCENT, (
        f"the regenerated calibrated level {cusum['achieved_level']} no longer rounds to v87's "
        f"printed {V87_CUSUM_CALIBRATION_PERCENT}%")
    assert set(validity["N_streams"]) == {V87_STREAMS_PER_LEVEL}


# =====================================================================
# REPORTING -- PRINTS WHAT R09 MEASURED, ASSERTS NOTHING
# =====================================================================

def test_R09_report_the_campaign_against_its_witness(validity, race, level, arl0, witnesses):
    """
    The D0-D3 classification of preamble S3, computed rather than asserted. The
    witness is never a gate, and R09's 128-bit
    re-keying redraws every Monte-Carlo value by construction.
    """
    print("\n" + "=" * 78)
    print("R09 -- the regenerated campaign against the submitted campaign's witness")
    print("=" * 78)
    pairs = (("R09_validity_stopping.csv", validity, witnesses["validity"]),
             ("R09_eprocess_race.csv", race, witnesses["race"]),
             ("R09_level_granularity.csv", level, witnesses["level"]),
             ("R09_arl0.csv", arl0, witnesses["arl0"]))
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
        print(f"  {label}: {len(new)} rows against {len(old)}, {len(shared)} shared columns")
        print(f"    columns added {added}")
        print(f"    worst numeric difference {worst_value:g}"
              + (f" on `{worst_column}`" if worst_column else ""))
    print("  Every Monte-Carlo value is redrawn by the 128-bit re-keying the R09 prompt requires;")
    print("  the comparison classifies, it does not gate.")
    print("=" * 78)


def test_R09_report_the_published_numerals_at_their_printed_precision(validity, race, level,
                                                                      witnesses):
    """
    The four numerals L243 prints, side by side with the witness, rounded the way
    v87 rounds them. Reporting only; the blocking form of each lives in the
    self-invalidating tests below.
    """
    print("\n" + "=" * 78)
    print("R09 -- v87's printed numerals at v87's printing precision")
    print("=" * 78)
    new = pick(validity, arm="CUSUM", alpha=FIGURE_ALPHA, stopping_protocol="peeking")
    old = pick(witnesses["validity"], arm="CUSUM", alpha=FIGURE_ALPHA,
               stopping_protocol="peeking")
    print(f"  L243 CUSUM peeking FPR      v87 {V87_CUSUM_PEEKING_FPR_PERCENT}%   "
          f"regenerated {100 * new['FPR']:.0f}% ({new['FPR']!r})   "
          f"witness {100 * old['FPR']:.0f}% ({old['FPR']!r})")
    new = pick(level, arm="CUSUM", alpha=FIGURE_ALPHA)
    old = pick(witnesses["level"], arm="CUSUM", alpha=FIGURE_ALPHA)
    print(f"  L243 CUSUM calibrated level v87 {V87_CUSUM_CALIBRATION_PERCENT}%    "
          f"regenerated {100 * new['achieved_level']:.0f}% ({new['achieved_level']!r})   "
          f"witness {100 * old['achieved_level']:.0f}% ({old['achieved_level']!r})")
    for arm, printed in (("MIX", V87_MIX_ADD_AT_PARITY), ("CUSUM", V87_CUSUM_ADD_AT_PARITY)):
        new = pick(race, arm=arm, alpha=FIGURE_ALPHA, eta=FIGURE_ETA)
        old = pick(witnesses["race"], arm=arm, alpha=FIGURE_ALPHA, eta=FIGURE_ETA)
        print(f"  L243 {arm:<5} ADD at eta=0.10  v87 {printed}    "
              f"regenerated {new['ADD']:.0f} ({new['ADD']!r})   "
              f"witness {old['ADD']:.0f} ({old['ADD']!r})")
    print("=" * 78)


def test_R09_report_the_censoring_that_makes_panel_c_a_horizon_artefact(arl0):
    print("\n" + "=" * 78)
    print("R09 -- ARL0 against its censored fraction, arm by arm and level by level")
    print("=" * 78)
    print(f"  {'arm':<8} {'alpha':>7} {'ARL0_mean':>13} {'1/alpha':>9} {'censored':>9} "
          f"{'implied LB':>11} {'flag informative':>17}")
    for row in arl0.itertuples(index=False):
        print(f"  {row.arm:<8} {row.alpha:>7.3f} {row.ARL0_mean:>13.4f} "
              f"{row.ref_inv_alpha:>9.2f} {row.censored_frac:>9.4f} "
              f"{row.arl0_implied_lower_bound:>11.1f} "
              f"{str(bool(row.bound_flag_carried_information)):>17}")
    print(f"  The simulation horizon is T_EXT = {T_EXT}. A mean over a sample censored at 65-99%")
    print("  converges on that horizon by arithmetic; v87's panel C caption names e-CUSUM alone,")
    print("  whose censoring is at or near zero, so no printed claim is at stake.")
    print("=" * 78)


def test_R09_report_the_control_outcomes_the_log_records(log_text):
    print("\n" + "=" * 78)
    print("R09 -- control outcomes, copied from the run log")
    print("=" * 78)
    patterns = (r"C3 \[MIX, H0 campaign\].*",
                r"C3 \[MIX, M1\(ii\).*",
                r"C3 NEGATIVE CONTROL \[CUSUM\].*",
                r"C4 \[\w+, alpha=0\.05\] ADD vs eta:.*",
                r"C4 HALT CONDITION.*",
                r"CALIBRATION COHERENCE at alpha.*",
                r"CONTROL SUMMARY\..*")
    for pattern in patterns:
        for line in re.findall(pattern, log_text):
            print("  " + line[:600])
    print("=" * 78)
