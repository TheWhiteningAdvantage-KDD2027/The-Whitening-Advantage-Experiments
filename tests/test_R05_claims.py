"""
R05 -- scale law and location/scale orthogonality. Acceptance and classification.

Two kinds of statement live in this file and they are kept apart deliberately.

*Blocking assertions* rest on deterministic relations -- cardinalities, a
constancy the design imposes, an analytic identity, a formatting rule -- or on
structural orderings that have no probability of firing under their own null.
None of them is a hypothesis test on a draw. The one exception is the positive
control, which is a hypothesis test, and which is blocking because a
non-responsive Concept monitor makes every blindness statement of this
experiment uninterpretable rather than merely weaker.

*Classification output* compares the regenerated campaign against the historical
witness of the submitted campaign and prints the degree of every deviation. It
asserts nothing about those degrees. A cell-by-cell equality gate against the
witness would convert every legitimate correction into a test failure whose only
exit is a widened tolerance, which the preamble forbids. The witnesses here were
drawn under 32-bit-truncated integer seed offsets; R05 redraws them under
128-bit entropy, so every Monte-Carlo value is expected to move.

No numeric literal here comes from the regenerated output. The only constants
admitted are those printed in v87 -- 400 seeds per configuration, alpha = 0.08,
standardized t_7, Delta_mu_max = 2, delta_P = 0.5, delta_C = 0.1, a 5% target,
the penalty grids, the two horizons, and the published values of Appendix B --
and every reference value is read from the vendored witness by the code, with
float_precision='round_trip' on both sides.

The two derived rules of this experiment, the crossover width and the
sixth-moment boundary, are reimplemented here independently of the experiment
modules rather than imported from them, so that a test of either is a comparison
of two implementations and not a restatement of one.
"""

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import scipy.stats as stats

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "results" / "R05_scale_law" / "data"
FIGURES_DIR = ROOT / "results" / "R05_scale_law" / "figures"
TABLES_DIR = ROOT / "results" / "R05_scale_law" / "tables"
REFERENCE_DIR = ROOT / "data" / "reference" / "R05"

# Protocol constants, from v87 sec:scaling_validation and app:scaling.
SEEDS_PER_CONFIG = 400
ALPHA_GARCH = 0.08
NU = 7.0
DMU_TARGET = 2.0
DELTA_P = 0.5
DELTA_C = 0.1
TARGET_FPR = 0.05
RHO = DELTA_P / DMU_TARGET
ABRUPT_GAMMA_POINTS = 13
RAMP_GAMMA_GRID = (2.0, 4.0, 8.0, 11.58, 20.0)
HORIZON_2E5 = 200_000
HORIZON_3E6 = 3_000_000
LADDER_HORIZONS = (77_000, HORIZON_2E5, HORIZON_3E6)

# Published values of v87 used as classification witnesses, never as gates.
PUBLISHED_SIXTH_MOMENT_GAMMA = 7.1
PUBLISHED_MOMENT_MARGIN_AT_TWENTY = 0.8


def _read(path):
    assert path.exists(), f"Missing artefact: {path}"
    return pd.read_csv(path, float_precision='round_trip')


@pytest.fixture(scope="module")
def abrupt():
    return _read(DATA_DIR / "R05_abrupt_add_vs_gamma.csv")


@pytest.fixture(scope="module")
def positive():
    return _read(DATA_DIR / "R05_concept_positive_control.csv")


@pytest.fixture(scope="module")
def ramp_2e5():
    return _read(DATA_DIR / "R05_ramp_multigamma_2e5.csv")


@pytest.fixture(scope="module")
def ramp_3e6():
    return _read(DATA_DIR / "R05_ramp_multigamma_3e6.csv")


@pytest.fixture(scope="module")
def ladder():
    return _read(DATA_DIR / "R05_lambda_iid_horizon.csv")


@pytest.fixture(scope="module")
def macros():
    path = TABLES_DIR / "R05_claims.tex"
    assert path.exists(), f"Missing artefact: {path}"
    return path.read_text(encoding="utf-8")


# ----------------------------------------------------------------------------
# Blocking: cardinalities and protocol conformance (control a)
# ----------------------------------------------------------------------------

def test_abrupt_cardinality(abrupt):
    assert len(abrupt) == ABRUPT_GAMMA_POINTS
    assert abrupt.Gamma.is_monotonic_increasing


def test_ramp_cardinalities(ramp_2e5, ramp_3e6):
    # Five penalties on a grid of twelve and seventeen ratio points. The grid is
    # deduplicated after rounding to integer widths, so the count is an upper
    # bound that the published campaigns attain.
    assert set(np.round(ramp_2e5.Gamma.unique(), 2)) == set(RAMP_GAMMA_GRID)
    assert set(np.round(ramp_3e6.Gamma.unique(), 2)) == set(RAMP_GAMMA_GRID)
    assert len(ramp_2e5) == 60
    assert len(ramp_3e6) == 85


def test_protocol_constants(abrupt, ramp_2e5, ramp_3e6):
    for frame in (abrupt, ramp_2e5, ramp_3e6):
        assert int(frame.n_drift.iloc[0]) == SEEDS_PER_CONFIG
        assert float(frame.dmu_std_target.iloc[0]) == DMU_TARGET
        assert float(frame.delta_P.iloc[0]) == DELTA_P
        assert float(frame.delta_C.iloc[0]) == DELTA_C
    for frame in (ramp_2e5, ramp_3e6):
        assert float(frame.alpha.iloc[0]) == ALPHA_GARCH


def test_horizons_are_the_two_published_budgets(ramp_2e5, ramp_3e6):
    assert int(ramp_2e5.mon_len.iloc[0]) == HORIZON_2E5
    assert int(ramp_3e6.mon_len.iloc[0]) == HORIZON_3E6


# ----------------------------------------------------------------------------
# Blocking: the common horizon (control b, design half)
# ----------------------------------------------------------------------------

def test_common_horizon_is_constant_across_gamma(ramp_2e5, ramp_3e6):
    """
    v87 requires all penalties monitored over one common horizon, so that the
    null crossing probability is identical across Gamma and the thresholds are
    comparable in level. Without it no comparison across Gamma is interpretable.
    """
    for frame in (ramp_2e5, ramp_3e6):
        assert frame.mon_len.nunique() == 1


def test_null_levels_are_homogeneous_across_gamma(ramp_2e5, ramp_3e6):
    """
    The consequence half of control (b): what the common horizon buys is a
    common null crossing probability. Tested as one aggregate homogeneity test
    on the five realised levels rather than as five per-cell gates, which at a
    5% level would fire with probability 22.6% under correct calibration.

    The threshold is 0.001, three orders of magnitude below the nominal 5%: this
    is a structural test of whether the five arms share a level, not a test of
    whether that level is 5%, and at p < 0.001 the shared-level premise of the
    design has failed rather than merely fluctuated.
    """
    for frame in (ramp_2e5, ramp_3e6):
        n_val = int(frame.n_val.iloc[0])
        counts = frame.groupby("Gamma").n_alarm_Data_null.first().to_numpy(dtype=int)
        table = np.array([counts, np.full(len(counts), n_val) - counts])
        _, p_value, _, _ = stats.chi2_contingency(table, correction=False)
        assert p_value > 0.001, (
            f"The five null levels {counts}/{n_val} are not homogeneous (p = {p_value:.4g}). "
            f"The common horizon is supposed to make them so.")


# ----------------------------------------------------------------------------
# Blocking: orthogonality as an identity, and the positive control (control c)
# ----------------------------------------------------------------------------

def test_concept_branch_is_gamma_invariant_by_construction(abrupt, ramp_2e5, ramp_3e6):
    """
    The sign stream is 1{eps_t > 0} = 1{z_t > 0}, a function of the innovation
    alone: it does not see beta, and a positive scale factor cannot change it.
    Under the common-random-numbers design every penalty therefore replays ONE
    Concept measurement. Constancy across Gamma is an identity of the design and
    is asserted as such -- it is not evidence of anything, and this test exists
    to keep that visible rather than to celebrate it.
    """
    for frame in (abrupt, ramp_2e5, ramp_3e6):
        assert frame.lambda_star_Concept.nunique() == 1
        assert frame.FPR_Concept_val.nunique() == 1


def test_concept_is_blind_to_the_scale_pathology(abrupt):
    """
    Orthogonality on the reference arm: detection under the pathology must be
    indistinguishable from the arm's own false-alarm rate. The vacuity guard
    comes first -- at a saturated level the equality is true of any monitor,
    including a broken one -- and the comparison is unpaired because the two
    rates are measured on disjoint seed blocks.
    """
    fpr = float(abrupt.FPR_Concept_val.iloc[0])
    assert 0.01 <= fpr <= 0.20, (
        f"Concept hold-out FPR {fpr:.4f} is saturated; the equality below would measure nothing.")
    n_drift = int(abrupt.n_drift.iloc[0])
    n_val = int(abrupt.n_val.iloc[0])
    detected = int(abrupt.n_detected_Concept.iloc[0])
    alarms = int(abrupt.n_alarm_Concept_null.iloc[0])
    _, p_value = stats.fisher_exact([[detected, n_drift - detected],
                                     [alarms, n_val - alarms]], alternative='two-sided')
    assert p_value > 0.001, (
        f"Concept detection {detected}/{n_drift} under a pure scale pathology differs from its "
        f"own null level {alarms}/{n_val} (p = {p_value:.4g}), which contradicts "
        f"Proposition prop:orthogonality.")


def test_positive_control_shows_the_monitor_responsive(positive):
    """
    Blocking. Without this arm, "blind to scale" and "not working" are the same
    measurement: a monitor that never alarms returns its false-alarm rate under
    any pathology whatsoever. A pure location shift of one unconditional
    standard deviation must be detected.
    """
    row = positive.iloc[0]
    assert row.pathology == "location"
    assert row.DetRate_Concept > row.FPR_Concept_val, (
        f"Concept detection under a location shift ({row.DetRate_Concept:.4f}) does not exceed "
        f"its own false-alarm rate ({row.FPR_Concept_val:.4f}): the instrument is not responsive.")
    assert row.fisher_p_value < 0.05, (
        f"Concept detection under a location shift is not resolved from its null level "
        f"(p = {row.fisher_p_value:.4g}).")


# ----------------------------------------------------------------------------
# Blocking: the crossover rule, reimplemented independently (finding 3.3)
# ----------------------------------------------------------------------------

def _crossover_applied(lambda_star, dmu, rho):
    """Independent reimplementation of w_delta: the crossover at the applied threshold."""
    return (2.0 * lambda_star / dmu) / (1.0 - rho) ** 2


def _crossover_predicted(lambda_iid, gamma, dmu, rho):
    """Independent reimplementation of w*: the crossover the recalibration rule predicts."""
    return (2.0 * lambda_iid * gamma / dmu) / (1.0 - rho) ** 2


def test_both_crossovers_are_emitted_and_are_distinct(ramp_2e5, ramp_3e6):
    """
    The submitted pipeline labelled its regime column with one crossover and
    fitted its published exponents on the other. R05 emits both under names that
    cannot be confused; this test recomputes each from first principles and
    checks that the frame agrees, and that the two are genuinely different
    quantities rather than aliases.
    """
    for frame in (ramp_2e5, ramp_3e6):
        dmu = float(frame.dmu_std_target.iloc[0])
        rho = float(frame.delta_P.iloc[0]) / dmu
        lam_iid = float(frame.lambda_iid_H.iloc[0])
        for _, row in frame.groupby("Gamma").first().reset_index().iterrows():
            expected_applied = _crossover_applied(row.lambda_star_Data, dmu, rho)
            expected_predicted = _crossover_predicted(lam_iid, row.Gamma, dmu, rho)
            assert math.isclose(row.w_delta_applied, expected_applied, rel_tol=1e-12)
            assert math.isclose(row.w_star_predicted, expected_predicted, rel_tol=1e-12)
        assert not np.allclose(frame.w_delta_applied, frame.w_star_predicted), (
            "The two crossovers coincide, which would mean the recalibration rule holds "
            "exactly; Appendix B reports it holding only to within 7-29%.")


def test_scaling_law_branches_meet_at_the_crossover(ramp_2e5):
    """
    Analytic identity of Theorem thm:scaling: the saturated and ramp branches of
    Eq. (5) take the same value at w = w*. Reimplemented here from the printed
    formula, with no reference to the experiment module.
    """
    dmu = float(ramp_2e5.dmu_std_target.iloc[0])
    delta_p = float(ramp_2e5.delta_P.iloc[0])
    rho = delta_p / dmu
    for lam in ramp_2e5.groupby("Gamma").lambda_star_Data.first():
        w_star = (2.0 * lam / dmu) / (1.0 - rho) ** 2
        ramp_branch = math.sqrt(2.0 * lam * w_star / dmu) + rho * w_star
        saturated_branch = lam / (dmu - delta_p) + (1.0 + rho) * w_star / 2.0
        assert math.isclose(ramp_branch, saturated_branch, rel_tol=1e-12)


# ----------------------------------------------------------------------------
# Blocking: the lambda_iid ladder (finding 3.5)
# ----------------------------------------------------------------------------

def test_ladder_visits_the_three_published_horizons(ladder):
    assert tuple(sorted(int(h) for h in ladder.H)) == tuple(sorted(LADDER_HORIZONS))


def test_ladder_is_monotone_in_the_horizon(ladder):
    """
    lambda_iid is a quantile of a running maximum over [0, H], and the three
    horizons are prefixes of ONE set of trajectories, so the threshold cannot
    decrease with H. A violation would mean the checkpoint sampler is
    mis-indexed, not that the measurement is surprising.
    """
    ordered = ladder.sort_values("H")
    assert ordered.lambda_iid_H.is_monotonic_increasing


def test_ladder_agrees_with_the_campaigns_it_overlaps(ladder, ramp_2e5, ramp_3e6):
    """
    The ladder and the campaigns read the same 'iid' seed block over the same
    prefix, so their thresholds must be identical bit for bit -- not close.
    """
    for frame in (ramp_2e5, ramp_3e6):
        horizon = int(frame.mon_len.iloc[0])
        row = ladder[ladder.H == horizon]
        if len(row) == 1:
            assert float(row.lambda_iid_H.iloc[0]) == float(frame.lambda_iid_H.iloc[0])


# ----------------------------------------------------------------------------
# Blocking: the analytic moment boundary, reimplemented independently (control e)
# ----------------------------------------------------------------------------

def _standardised_t_even_moment(order, nu):
    """E[z^order] for a unit-variance Student-t, computed from the Beta function."""
    if order >= nu:
        return float('inf')
    scale = ((nu - 2.0) / nu) ** (order / 2.0)
    return scale * (nu ** (order / 2.0)) * math.gamma((order + 1) / 2.0) \
        * math.gamma((nu - order) / 2.0) / (math.sqrt(math.pi) * math.gamma(nu / 2.0))


def _gamma_closed(alpha, beta):
    denominator = 1.0 - 2.0 * alpha * beta - beta ** 2
    rho1 = alpha * (1.0 - beta * (alpha + beta)) / denominator
    return 1.0 + 2.0 * rho1 / (1.0 - alpha - beta)


def test_sixth_moment_boundary_matches_the_published_gamma(macros):
    """
    E[eps^6] < infinity for a GARCH(1,1) iff E[(alpha z^2 + beta)^3] < 1. The
    cubic is expanded here directly and solved by bisection, independently of
    the experiment module, and compared against v87's printed 7.1.

    This is the one published number of R05 that no draw can move: it is a
    closed-form condition on (alpha, beta, nu). It is therefore asserted rather
    than classified.
    """
    z2, z4, z6 = 1.0, _standardised_t_even_moment(4, NU), _standardised_t_even_moment(6, NU)

    def functional(beta):
        return (ALPHA_GARCH ** 3 * z6 + 3 * ALPHA_GARCH ** 2 * beta * z4
                + 3 * ALPHA_GARCH * beta ** 2 * z2 + beta ** 3)

    low, high = 1e-9, 1.0 - ALPHA_GARCH - 1e-9
    for _ in range(200):
        middle = 0.5 * (low + high)
        if functional(middle) < 1.0:
            low = middle
        else:
            high = middle
    gamma_boundary = _gamma_closed(ALPHA_GARCH, 0.5 * (low + high))
    assert round(gamma_boundary, 1) == PUBLISHED_SIXTH_MOMENT_GAMMA

    emitted = float(re.search(r"\\RFiveSixthMomentGamma\}\{([-\d.]+)\}", macros).group(1))
    assert round(emitted, 1) == round(gamma_boundary, 1)


def test_moment_margin_macro_matches_the_published_bound(macros):
    emitted = float(re.search(r"\\RFiveMomentMarginAtGammaMax\}\{([-\d.]+)\}", macros).group(1))
    assert round(emitted, 1) == PUBLISHED_MOMENT_MARGIN_AT_TWENTY


# ----------------------------------------------------------------------------
# Blocking: artefact form
# ----------------------------------------------------------------------------

def test_macro_file_is_well_formed(macros):
    lines = macros.splitlines()
    assert lines[0] == "% Auto-generated by exp_R05_scale_law_c.py -- do not edit."
    assert macros.endswith("\n")
    for line in lines[1:]:
        assert line.startswith("\\newcommand{\\RFive"), f"Unexpected macro line: {line!r}"


def test_required_macros_are_present(macros):
    required = (
        "RFiveSeedsPerConfig", "RFiveAlphaGarch", "RFiveDeltaMuMax", "RFiveDeltaC",
        "RFiveTargetFpr", "RFiveGammaRampMin", "RFiveGammaRampMax",
        "RFiveAbruptSlope", "RFiveAbruptIntercept", "RFiveAbruptRSquared",
        "RFiveAbruptSlopeExGammaOne", "RFiveAbruptInterceptExGammaOne",
        "RFiveSqrtRuleFpr", "RFiveScalingMedianError",
        "RFiveRecalibMarginMinTwoEFive", "RFiveRecalibMarginMaxTwoEFive",
        "RFiveRecalibMarginMinThreeESix", "RFiveRecalibMarginMaxThreeESix",
        "RFiveConceptDetRate", "RFiveConceptFpr",
        "RFiveConceptPositiveDetRate", "RFiveConceptPositiveShift",
        "RFiveLambdaCAbrupt", "RFiveLambdaCRampTwoEFive", "RFiveLambdaCRampThreeESix",
        "RFiveSixthMomentGamma", "RFiveMomentMarginAtGammaMax",
    )
    for name in required:
        assert f"\\newcommand{{\\{name}}}" in macros, f"Missing macro: {name}"


def test_figure_exists():
    assert (FIGURES_DIR / "fig05_scale_law_orthogonality.png").exists()


def test_text_artefacts_end_with_a_newline():
    """
    docs/sections/*.md and requirements/*.txt are assembled by concatenation. A
    file without a final newline glues two dependencies onto one line and
    silently corrupts the assembled requirements.
    """
    for path in (ROOT / "requirements" / "R05.txt",
                 ROOT / "docs" / "sections" / "R05.md",
                 TABLES_DIR / "R05_claims.tex"):
        assert path.exists(), f"Missing artefact: {path}"
        assert path.read_bytes().endswith(b"\n"), f"No trailing newline: {path}"


def test_superseded_witness_is_documented_not_regenerated():
    """
    protocol_18a is an output of a design retired before submission. It is kept
    as a trace, under a directory that says so, and no shipped script produces a
    counterpart. This test guards the second half of that statement.
    """
    superseded = REFERENCE_DIR / "superseded"
    assert (superseded / "protocol_18a_scale_add_vs_width.csv").exists()
    assert (superseded / "README.md").exists()
    assert not (DATA_DIR / "R05_ramp_add_vs_width.csv").exists(), (
        "A counterpart to the retired protocol_18a has appeared. No v87 claim rests on it and "
        "no script regenerates it; emitting one would give a new artefact an old file's name.")


# ----------------------------------------------------------------------------
# Classification output: asserts nothing
# ----------------------------------------------------------------------------

def test_report_deviation_classification(capsys):
    """
    Prints the D0/D1/D2 table produced by step c, plus the witness comparison
    for the quantities whose witness lives in a reference CSV rather than in the
    manuscript text. Run with -s to read it.
    """
    table = _read(DATA_DIR / "R05_deviation_classification.csv")
    with capsys.disabled():
        print("\n--- R05 deviation classification against v87 ---")
        print(table.to_string(index=False))
        print("\n--- Concept threshold, witness against regenerated ---")
        for name, witness_file in (("abrupt", "protocol_17a_scale_add_vs_gamma.csv"),
                                   ("2e5", "protocol_18b_scale_add_vs_width_multigamma_2e5.csv"),
                                   ("3e6", "protocol_18b_scale_add_vs_width_multigamma_3e6.csv")):
            witness = _read(REFERENCE_DIR / witness_file)
            print(f"{name:>7}: witness lambda_star_Concept = "
                  f"{float(witness.lambda_star_Concept.iloc[0]):.4f}, "
                  f"FPR = {float(witness.FPR_Concept_val.iloc[0]):.4f}")
        print("\nThe v87 numeral lambda_C = 10 matches none of the three. See docs/sections/R05.md.")
    assert len(table) > 0
