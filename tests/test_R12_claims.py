"""
R12 -- volatility misspecification and moment singularity. Acceptance and
reporting.

Three kinds of statement live in this file and they are kept apart deliberately.

*Blocking assertions* rest either on a value v87 PRINTS, compared at v87's own
printing precision, or on a deterministic relation reimplemented here
INDEPENDENTLY of the experiment -- the Wilson interval written as the two roots
of the score equation rather than as a centre and a margin, the GARCH
fourth-moment boundary written from He & Terasvirta's condition rather than
from the experiment's inversion, the exact penalty `Gamma` written from its own
closed form, and control C1 re-derived from the experiment's AST rather than
read from its log. NONE rests on a value R12 produced.

*Self-invalidating assertions* state a deviation. Each is written with an
explicit z against its own standard error, never as an equality at printed
precision, because preamble S2 pre-classifies every Monte-Carlo value of this
stream as moving under the mandated re-keying: a blocking equality on such a
value would be a gate that fails by construction, whose only exit is a widened
tolerance, which preamble S4.8 bans. If a later campaign brings one of these
values back, the test fires and what changes is `docs/DEVIATIONS.md`, not the
tolerance.

*Reporting output* prints the D0-D3 classification, the design-effect table and
the witness comparison, and asserts nothing.

WHY THE WITNESS IS NOT A BLOCKING ANCHOR. `data/reference/README.md` states it
outright: a witness value is the "published value" column of a D0-D3
comparison, never the anchor of a blocking assertion, because a cell-by-cell
equality gate converts every legitimate correction into a test failure. R12's
128-bit re-keying redraws every Monte-Carlo value of both campaigns by
construction, so a witness gate here would fail on the first run. The witness IS
a blocking anchor for one thing only, and it is not a measurement: the byte
identity of the three carried primitives.

THE FOUR SELF-INVALIDATING ASSERTIONS, AND WHAT EACH WOULD MEAN IF IT FIRED.

`test_R12_the_concept_false_alarm_envelope_has_moved_at_both_ends` asserts the
D2 `R12-campaign-redraw` carries on L349's `7.6`--`8.4\\%`. If a later campaign
brings both ends back, the test fires and the D2 is withdrawn from that pair.

`test_R12_the_censored_delay_minimum_has_moved_but_stays_in_its_rounding_bracket`
asserts both halves of the L353 finding: the printed `2,400` no longer
reproduces at the hundreds, AND the regenerated range stays inside
`[2350, 3050)`, which is what keeps it a D2 rather than the D3 the plan's halt
condition watches for.

`test_R12_the_detection_rate_at_nu_ten_is_a_count_whose_printed_rounding_moved`
asserts that the nu = 10 detection rate is an exact count out of 1,000 and that
its rounding to whole percent is no longer v87's `83\\%`.

`test_R12_the_crn_concept_arm_is_one_number_repeated_fifteen_times` asserts the
degeneracy that forced the two-arm design. If it ever fails, either
`simulate_gjr_garch` no longer draws its innovations before the variance
recursion or a key has acquired a grid coordinate, and the published arm's
justification has to be rewritten.
"""

import ast
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "results" / "R12_gjr_student" / "data"
FIGURES_DIR = ROOT / "results" / "R12_gjr_student" / "figures"
TABLES_DIR = ROOT / "results" / "R12_gjr_student" / "tables"
REFERENCE_DIR = ROOT / "data" / "reference" / "R12"
SOURCE = ROOT / "experiments" / "R12_gjr_student" / "exp_R12_gjr_student.py"
WITNESS = REFERENCE_DIR / "Priorite_10_robustness_gjr_student.py"
LOG = ROOT / "logs" / "R12_gjr_student" / "exp_R12_gjr_student.log"
SECTION = ROOT / "docs" / "sections" / "R12.md"
REQUIREMENTS = ROOT / "requirements" / "R12.txt"

# =====================================================================
# ANCHORS -- EVERY ONE OF THEM PRINTED IN articleB_whitening_v87.tex
# =====================================================================
# L349 and the Figure 12 caption (tex L585): "residual Ljung--Box rejection on
# the standardized squared residual rises from $5.1\%$ to $24.6\%$ at
# $\gamma_{\mathrm{lev}} = 0.28$ ..., driving its false-alarm rate from $3.2\%$
# to $20.6\%$ ...: across the whole leverage grid its Ljung--Box rejection stays
# within $4.6$--$5.4\%$ and its false-alarm rate within $7.6$--$8.4\%$ at its
# fixed threshold---above nominal, but flat where the baseline's climbs by a
# factor of six."
V87_LB_DATA = (5.1, 24.6)
V87_FPR_DATA = (3.2, 20.6)
V87_FPR_CONCEPT = (7.6, 8.4)
V87_LB_CONCEPT = (4.6, 5.4)
V87_FPR_FACTOR = 6
V87_STREAMS_A = 10000
# L353 and the Figure 13 caption (tex L592): "detection decays monotonically
# ($83\%$ at $\nu = 10$, $61\%$ at $\nu = 7$), collapses below the $50\%$
# censoring threshold for $\nu \le 5.5$, and the surviving minority carries
# survivorship-biased delays of $2{,}400$--$3{,}000$ steps ... The \textsc{Concept}
# pipeline ... stays flat at $34$--$38$ steps right up to the singularity."
V87_DET_NU_TEN = 0.83
V87_DET_NU_SEVEN = 0.61
V87_COLLAPSE_NU = 5.5
V87_CENSORING_THRESHOLD = 0.5
V87_ADD_CENSORED = (2400, 3000)
V87_ADD_CONCEPT = (34, 38)
V87_STREAMS_B = 1000
# The grids v87 fixes and the R12 prompt restates as imperative.
V87_GAMMA_GRID = tuple(np.round(np.linspace(0.0, 0.28, 15), 3).tolist())
V87_NU_GRID = (10.0, 9.0, 8.0, 7.5, 7.0, 6.5, 6.0, 5.5,
               5.0, 4.75, 4.5, 4.25, 4.2, 4.1, 4.05, 4.01)

# =====================================================================
# TOLERANCES, EACH DERIVED FROM A MECHANISM
# =====================================================================
# The Wilson bounds are reimplemented here as the two roots of the score
# equation and in the experiment as a centre plus a margin. The two forms are
# algebraically identical and differ only in the order of a handful of float64
# operations, so the budget is a few ULP of a quantity of order 1.
WILSON_ULP_BUDGET = 32 * float(np.finfo(np.float64).eps)
# The moment boundary is a closed-form inversion on both sides; the only
# difference is the order of two divisions.
MOMENT_BOUNDARY_TOLERANCE = 1e-12
# A redraw is pre-classified D2, so every self-invalidating assertion is stated
# at three standard errors of the DIFFERENCE between two campaigns of the same
# design, never as an equality.
Z_REDRAW = 3.0
Z_95 = 1.959963984540054


@pytest.fixture(scope="module")
def leverage():
    return pd.read_csv(DATA_DIR / "R12_leverage_fpr.csv", float_precision='round_trip')


@pytest.fixture(scope="module")
def singularity():
    return pd.read_csv(DATA_DIR / "R12_singularity_add.csv", float_precision='round_trip')


@pytest.fixture(scope="module")
def crn_witness():
    return pd.read_csv(DATA_DIR / "R12_concept_crn_witness.csv", float_precision='round_trip')


@pytest.fixture(scope="module")
def diagnostics():
    return pd.read_csv(DATA_DIR / "R12_diagnostics.csv", float_precision='round_trip')


@pytest.fixture(scope="module")
def witness_a():
    return pd.read_csv(REFERENCE_DIR / "protocol_expA_leverage_fpr.csv",
                       float_precision='round_trip')


@pytest.fixture(scope="module")
def witness_b():
    return pd.read_csv(REFERENCE_DIR / "protocol_expB_singularity_add.csv",
                       float_precision='round_trip')


@pytest.fixture(scope="module")
def macros():
    text = (TABLES_DIR / "R12_claims.tex").read_text()
    return dict(re.findall(r"\\newcommand\{\\(\w+)\}\{(.*)\}", text))


def wilson_roots(k, n, z=Z_95):
    """
    The Wilson score interval as the two ROOTS of the score equation
    (p_hat - p)^2 = z^2 p (1 - p) / n, i.e. of
    (1 + z^2/n) p^2 - (2 p_hat + z^2/n) p + p_hat^2 = 0.

    Written this way on purpose: the experiment computes a centre and a margin,
    and an independent reimplementation of the same interval in a different
    algebraic form is what makes the comparison a check rather than a copy.
    """
    p = k / n
    a = 1.0 + z * z / n
    b = -(2.0 * p + z * z / n)
    c = p * p
    disc = math.sqrt(b * b - 4.0 * a * c)
    return max(0.0, (-b - disc) / (2.0 * a)), min(1.0, (-b + disc) / (2.0 * a))


def source_segment(path, name):
    text = Path(path).read_text()
    for node in ast.parse(text).body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(text, node)
    return None


# =====================================================================
# BLOCKING -- SPECIFICATION
# =====================================================================

def test_R12_every_artefact_the_plan_lists_exists(leverage, singularity, crn_witness,
                                                  diagnostics):
    for path in (DATA_DIR / "R12_leverage_fpr.csv", DATA_DIR / "R12_singularity_add.csv",
                 DATA_DIR / "R12_concept_crn_witness.csv", DATA_DIR / "R12_diagnostics.csv",
                 FIGURES_DIR / "fig12_leverage.png", FIGURES_DIR / "fig13_fat_tails.png",
                 TABLES_DIR / "R12_claims.tex", LOG, SECTION, REQUIREMENTS,
                 WITNESS, REFERENCE_DIR / "Priorite_10_robustness_gjr_student.log",
                 REFERENCE_DIR / "protocol_expA_leverage_fpr.csv",
                 REFERENCE_DIR / "protocol_expB_singularity_add.csv",
                 REFERENCE_DIR / "orphans" / "expA_argarch_boundary.csv",
                 REFERENCE_DIR / "orphans" / "expB_race_condition.csv",
                 REFERENCE_DIR / "orphans" / "README.md"):
        assert path.exists(), f"{path} is missing"
    assert len(leverage) == 15 and len(singularity) == 16
    assert len(crn_witness) == 15 and len(diagnostics) > 0


def test_R12_the_grids_and_stream_counts_are_the_ones_v87_specifies(leverage, singularity):
    assert tuple(leverage["gamma_lev"]) == V87_GAMMA_GRID
    assert tuple(singularity["nu"]) == V87_NU_GRID
    assert set(leverage["n_seeds"]) == {V87_STREAMS_A}
    assert set(singularity["n_seeds"]) == {V87_STREAMS_B}


def test_R12_the_published_concept_arm_is_the_independent_key_on_every_row(leverage):
    """
    The one column that makes the two-arm design auditable from the CSV alone.
    Every published Concept value must be stamped with the arm that produced it,
    and that arm must be the one whose key carries the grid index.
    """
    assert set(leverage["concept_arm"]) == {"expA_concept_indep"}
    assert set(leverage["data_arm"]) == {"expA"}


def test_R12_the_three_carried_primitives_are_byte_identical_to_the_witness():
    """
    The only blocking use of the witness in this file, and it is not a
    measurement: preamble S4.2 forbids hoisting a scientific primitive into
    experiments/common/, so the duplication is deliberate and must not drift.
    """
    for name in ("simulate_gjr_garch", "compute_gamma_exact", "strict_cusum"):
        mine, theirs = source_segment(SOURCE, name), source_segment(WITNESS, name)
        assert mine is not None and theirs is not None, name
        assert mine == theirs, f"{name} has drifted from {WITNESS.name}"


def test_R12_det_rate_concept_is_computed_and_not_a_literal():
    """
    Control C1, re-derived here from the experiment's AST rather than read from
    its log. v87's Figure 13 caption rests on the Concept arm detecting on every
    stream at every nu, and the witness CSV carries the integer 1 at all sixteen
    grid points; a literal would make that claim unmeasured, which is a D3.
    """
    sites = [node.value for node in ast.walk(ast.parse(SOURCE.read_text()))
             if isinstance(node, ast.Assign)
             for target in node.targets
             if isinstance(target, ast.Name) and target.id == "det_rate_concept"]
    assert len(sites) == 1, f"{len(sites)} producing sites, not one"
    expression = sites[0]
    assert isinstance(expression, ast.BinOp) and isinstance(expression.op, ast.Div)
    assert isinstance(expression.left, ast.Call)
    assert isinstance(expression.left.func, ast.Name) and expression.left.func.id == "len"


def test_R12_the_concept_detection_rate_is_a_full_count_and_not_a_rounded_one(singularity):
    """
    The corroboration C1 cannot supply on its own: the rate is 1.0 at all
    sixteen nu BECAUSE the detected count equals the stream count, row by row.
    """
    assert (singularity["n_detected_concept"] == singularity["n_seeds"]).all()
    assert (singularity["det_rate_concept"] == 1.0).all()


# =====================================================================
# BLOCKING -- DETERMINISTIC RELATIONS, REIMPLEMENTED INDEPENDENTLY
# =====================================================================

def test_R12_every_wilson_interval_is_the_score_interval_of_its_own_rate(leverage, singularity):
    checked = 0
    for row in leverage.itertuples(index=False):
        for rate, low, high in (
                (row.fp_data, row.fp_data_ci_low, row.fp_data_ci_high),
                (row.fp_concept, row.fp_concept_ci_low, row.fp_concept_ci_high),
                (row.lb_reject_data, row.lb_reject_data_ci_low, row.lb_reject_data_ci_high),
                (row.lb_reject_concept, row.lb_reject_concept_ci_low,
                 row.lb_reject_concept_ci_high)):
            expected = wilson_roots(int(round(rate * row.n_seeds)), row.n_seeds)
            assert abs(low - expected[0]) <= WILSON_ULP_BUDGET
            assert abs(high - expected[1]) <= WILSON_ULP_BUDGET
            checked += 1
    for row in singularity.itertuples(index=False):
        expected = wilson_roots(int(row.n_detected_data), row.n_seeds)
        assert abs(row.det_rate_data_ci_low - expected[0]) <= WILSON_ULP_BUDGET
        assert abs(row.det_rate_data_ci_high - expected[1]) <= WILSON_ULP_BUDGET
        checked += 1
    assert checked == 4 * 15 + 16


def test_R12_the_fourth_moment_boundary_and_the_exact_penalty_are_their_own_closed_forms():
    """
    Both derivations of the run log, recomputed from their own statements.

    E[eps^4] < inf iff alpha^2 k(nu) + 2 alpha beta + beta^2 < 1 with
    k(nu) = 3(nu-2)/(nu-4) (He & Terasvirta 1999), so nu* solves
    k(nu*) = (1 - 2 alpha beta - beta^2) / alpha^2. Checked by substitution
    rather than by re-inverting the same formula.
    """
    alpha, beta = 0.05, 0.85
    k_star = (1.0 - 2.0 * alpha * beta - beta**2) / alpha**2
    nu_star = (4.0 * k_star - 6.0) / (k_star - 3.0)
    assert abs(3.0 * (nu_star - 2.0) / (nu_star - 4.0) - k_star) <= MOMENT_BOUNDARY_TOLERANCE
    assert abs(nu_star - 4.081081081081081) <= MOMENT_BOUNDARY_TOLERANCE
    # Only the last two grid points sit beyond it, while the collapse starts
    # near nu = 5.5-6: the log reports that distance and attributes no mechanism.
    assert [nu for nu in V87_NU_GRID if nu < nu_star] == [4.05, 4.01]

    phi = alpha + beta
    rho1 = alpha * (1 - beta * phi) / (1 - 2 * alpha * beta - beta**2)
    gamma_exact = max(1.0, 1 + 2 * rho1 / (1 - phi))
    assert abs(gamma_exact - 2.2207792207792205) <= MOMENT_BOUNDARY_TOLERANCE
    assert abs(65.0 * gamma_exact - 144.35064935064935) <= 1e-10


def test_R12_the_leverage_grid_runs_to_the_edge_of_the_stationary_region(leverage):
    """
    Under innovations symmetric about zero, E[1{eps < 0}] = 1/2, so the GJR
    second-moment condition is alpha + gamma_lev/2 + beta < 1. Recomputed here
    from the persisted alpha_sym rather than read from the log.
    """
    assert np.allclose(leverage["alpha_sym"], 0.05 + leverage["gamma_lev"] / 2.0)
    assert np.allclose(leverage["persistence"], leverage["alpha_sym"] + 0.80)
    assert (leverage["persistence"] < 1.0).all()
    assert abs(float(leverage["persistence"].iloc[-1]) - 0.99) < 1e-12
    # Variance targeting: omega = 0.04 (1 - alpha_sym - beta) makes sigma2_unc
    # exactly 0.04 at every grid point, which is what isolates the misspecified
    # DYNAMICS from a level error.
    assert np.allclose(leverage["omega"] / (1.0 - leverage["persistence"]), 0.04)


def test_R12_the_censoring_rule_is_the_one_stated_before_the_frame_was_read(singularity):
    """
    Control C2. `ADD_Data` exists exactly where det_rate_data >= 0.5;
    `ADD_Data_Raw` and `SEM_Data_Raw` exist everywhere, because v87 L353
    publishes a delay range ON the censored domain and the submitted artefact
    carries no dispersion there.
    """
    censored = singularity["det_rate_data"] < V87_CENSORING_THRESHOLD
    assert (singularity["censored"] == censored).all()
    assert singularity.loc[censored, "ADD_Data"].isna().all()
    assert singularity.loc[censored, "SEM_Data"].isna().all()
    assert singularity.loc[~censored, "ADD_Data"].notna().all()
    assert singularity["ADD_Data_Raw"].notna().all()
    assert singularity["SEM_Data_Raw"].notna().all()
    assert (singularity["SEM_Data_Raw"] > 0).all()


# =====================================================================
# BLOCKING -- THE QUALITATIVE CLAIMS OF v87 THAT REPRODUCE
# =====================================================================

def test_R12_the_baseline_false_alarm_rate_explodes_with_leverage(leverage):
    """L349: the parametric route fails to control false alarms once misspecified."""
    assert float(leverage["fpr_data"].iloc[0]) < 5.0
    assert float(leverage["fpr_data"].iloc[-1]) > 4 * float(leverage["fpr_data"].iloc[0])
    assert float(leverage["lb_data_pct"].iloc[-1]) > 4 * float(leverage["lb_data_pct"].iloc[0])


def test_R12_the_sign_pipeline_holds_a_leverage_invariant_rate(leverage, diagnostics):
    """
    L349's "leverage-invariant", tested as control C9 tests it -- by a SLOPE with
    a null, never by the range, which is an extremum over a grid and has no
    sampling distribution (S4bis, fourth corollary).
    """
    slope = diagnostics[diagnostics["quantity"] == "invariance_slope"]["value"].iloc[0]
    p_value = diagnostics[diagnostics["quantity"] == "invariance_slope_pvalue"]["value"].iloc[0]
    assert p_value > 0.01, f"the zero-slope null is rejected at the gate: slope {slope}"
    span = float(leverage["gamma_lev"].iloc[-1] - leverage["gamma_lev"].iloc[0])
    assert abs(slope) * span < 1.0, "the fitted drift exceeds one percentage point over the grid"


def test_R12_detection_decays_monotonically_on_the_uncensored_domain(singularity):
    """
    L353's "detection decays monotonically", on the domain control C4 declares
    BEFORE the frame is read. The restriction is this repository's choice and not
    v87's formulation; the submitted witness is itself non-monotone at two
    censored grid points.
    """
    reliable = singularity[~singularity["censored"]]["det_rate_data"].to_numpy()
    assert (np.diff(reliable) <= 0).all(), "an inversion in the reliable region is a D3"


def test_R12_the_collapse_threshold_is_the_one_L353_prints(singularity):
    below = singularity[singularity["nu"] <= V87_COLLAPSE_NU]["det_rate_data"]
    above = singularity[singularity["nu"] > V87_COLLAPSE_NU]["det_rate_data"]
    assert (below < V87_CENSORING_THRESHOLD).all()
    assert (above >= V87_CENSORING_THRESHOLD).all()


def test_R12_the_concept_delay_stays_flat_at_the_printed_range(singularity):
    """L353: "stays flat at $34$--$38$ steps right up to the singularity"."""
    add = singularity["ADD_Concept"]
    assert round(float(add.min())) == V87_ADD_CONCEPT[0]
    assert round(float(add.max())) == V87_ADD_CONCEPT[1]
    # And it is flat only relative to a Data pipeline that moves by two orders of
    # magnitude over the same grid.
    assert float(add.max() - add.min()) < 0.05 * float(singularity["ADD_Data_Raw"].min())


# =====================================================================
# SELF-INVALIDATING -- EACH STATES A DEVIATION
# =====================================================================

def test_R12_the_concept_false_alarm_envelope_has_moved_at_both_ends(leverage):
    """
    `R12-campaign-redraw`, D2 on L349's `7.6`--`8.4\\%`. Both ends move at v87's
    printing precision. Stated with the standard error of the DIFFERENCE between
    two campaigns of the same design, because the printed value is itself one
    realisation of that design.
    """
    low = float(leverage["fpr_concept"].min())
    high = float(leverage["fpr_concept"].max())
    assert round(low, 1) != V87_FPR_CONCEPT[0], "the lower end has returned; withdraw the D2"
    assert round(high, 1) != V87_FPR_CONCEPT[1], "the upper end has returned; withdraw the D2"
    # Two independent campaigns of n = 10,000 at p ~ 0.08: SE of the difference.
    se = 100.0 * math.sqrt(2.0 * 0.08 * 0.92 / V87_STREAMS_A)
    assert abs(low - V87_FPR_CONCEPT[0]) / se < Z_REDRAW
    assert abs(high - V87_FPR_CONCEPT[1]) / se < Z_REDRAW


def test_R12_the_censored_delay_minimum_has_moved_but_stays_in_its_rounding_bracket(
        singularity, diagnostics):
    """
    `R12-campaign-redraw`, D2 on L353's `2,400`--`3,000`, and the halt condition
    that did NOT fire. v87 prints the pair rounded to the hundreds, so the
    contradiction watch item is the bracket [2350, 3050) and not the numerals --
    the witness's own 2443.18 and 3005.28 both round onto them.
    """
    censored = singularity[singularity["censored"]]
    low = float(censored["ADD_Data_Raw"].min())
    high = float(censored["ADD_Data_Raw"].max())
    assert round(low, -2) != V87_ADD_CENSORED[0], "the lower end has returned; withdraw the D2"
    assert round(high, -2) == V87_ADD_CENSORED[1], "the upper end has moved; reclassify it"
    # S3: a printed bound is breached at D3 only if the regenerated 95% interval
    # excludes it. Both ends stay inside the bracket at that level.
    sem_low = float(censored.loc[censored["ADD_Data_Raw"].idxmin(), "SEM_Data_Raw"])
    sem_high = float(censored.loc[censored["ADD_Data_Raw"].idxmax(), "SEM_Data_Raw"])
    assert low - Z_95 * sem_low >= 2350.0, "the range has left its rounding bracket: D3"
    assert high - Z_95 * sem_high < 3050.0, "the range has left its rounding bracket: D3"


def test_R12_the_detection_rate_at_nu_ten_is_a_count_whose_printed_rounding_moved(singularity):
    """
    `R12-campaign-redraw`, D2 on L353's `83\\%`. The regenerated rate is an exact
    count out of 1,000 whose rounding to whole percent is no longer 83.
    """
    row = singularity[np.isclose(singularity["nu"], 10.0)].iloc[0]
    assert int(row["n_detected_data"]) == round(float(row["det_rate_data"]) * V87_STREAMS_B)
    assert f"{100 * float(row['det_rate_data']):.0f}" != f"{100 * V87_DET_NU_TEN:.0f}"
    se = math.sqrt(2.0 * V87_DET_NU_TEN * (1 - V87_DET_NU_TEN) / V87_STREAMS_B)
    assert abs(float(row["det_rate_data"]) - V87_DET_NU_TEN) / se < Z_REDRAW


def test_R12_the_crn_concept_arm_is_one_number_repeated_fifteen_times(crn_witness, diagnostics):
    """
    `R12-concept-crn-degeneracy`. The finding that forced the two-arm design:
    under a key carrying no grid coordinate the Experiment A sign stream is
    bit-identical at all fifteen gamma_lev, so that arm's range is zero by
    construction and supports no claim.
    """
    assert crn_witness["fp_concept"].nunique() == 1
    assert crn_witness["lb_reject_concept"].nunique() == 1
    # `n_distinct_e_bin_digests` counts distinct digests WITHIN a grid point over
    # the C8 subsample, so one per seed is the identity's own signature: 50
    # streams, 50 digests, and the SAME 50 at every gamma_lev -- the cross-grid
    # half is what control C8 asserts with sys.exit(1), since a CSV column cannot
    # carry it.
    assert (crn_witness["n_distinct_e_bin_digests"]
            == crn_witness["n_identity_seeds"]).all()
    assert not crn_witness["supports_published_claim"].any()
    assert (crn_witness["n_eff"] == V87_STREAMS_A).all()
    deff = diagnostics[(diagnostics["quantity"] == "kish_design_effect")
                       & (diagnostics["arm"] == "expA:fp_concept")]["value"].iloc[0]
    indep = diagnostics[(diagnostics["quantity"] == "kish_design_effect")
                        & (diagnostics["arm"] == "expA_concept_indep:fp_concept")]["value"].iloc[0]
    assert deff > 14.0, "the CRN arm no longer carries a design effect of 15"
    assert 0.8 < indep < 1.25, "the independent key has not broken the pairing"


# =====================================================================
# BLOCKING -- ARTEFACT HYGIENE
# =====================================================================

def test_R12_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix(macros):
    lines = (TABLES_DIR / "R12_claims.tex").read_text().splitlines()
    assert lines[0] == "% Auto-generated by exp_R12_gjr_student.py -- do not edit."
    for line in lines[1:]:
        assert line.startswith("%") or line.startswith("\\newcommand"), line
    assert all(name.startswith("RTwelve") for name in macros)
    # The two macros the R12 prompt lists and this stream deliberately does not
    # emit: their claim is v87 L302, which R07 has already delivered.
    assert "RTwelveBoundaryNaiveRate" not in macros
    assert "RTwelveBoundaryMedianRate" not in macros
    assert len(macros) == 21


def test_R12_the_macros_agree_with_the_frames_they_are_computed_from(macros, leverage,
                                                                    singularity):
    assert macros["RTwelveLbDataLow"] == f"{float(leverage['lb_data_pct'].iloc[0]):.1f}\\%"
    assert macros["RTwelveLbDataHigh"] == f"{float(leverage['lb_data_pct'].iloc[-1]):.1f}\\%"
    assert macros["RTwelveFprDataLow"] == f"{float(leverage['fpr_data'].iloc[0]):.1f}\\%"
    assert macros["RTwelveFprDataHigh"] == f"{float(leverage['fpr_data'].iloc[-1]):.1f}\\%"
    assert macros["RTwelveFprConceptMin"] == f"{float(leverage['fpr_concept'].min()):.1f}\\%"
    assert macros["RTwelveFprConceptMax"] == f"{float(leverage['fpr_concept'].max()):.1f}\\%"
    assert macros["RTwelveLbConceptMin"] == f"{float(leverage['lb_concept_pct'].min()):.1f}\\%"
    assert macros["RTwelveLbConceptMax"] == f"{float(leverage['lb_concept_pct'].max()):.1f}\\%"
    factor = float(leverage["fpr_data"].iloc[-1]) / float(leverage["fpr_data"].iloc[0])
    assert macros["RTwelveFprDataFactor"] == f"{factor:.2f}"
    censored = singularity[singularity["censored"]]
    assert macros["RTwelveCollapseNu"] == f"{float(censored['nu'].max()):g}"
    assert macros["RTwelveAddConceptMin"] == f"{round(float(singularity['ADD_Concept'].min()))}"
    assert macros["RTwelveAddConceptMax"] == f"{round(float(singularity['ADD_Concept'].max()))}"
    for name, value in (("RTwelveAddDataCensoredMin", censored["ADD_Data_Raw"].min()),
                        ("RTwelveAddDataCensoredMax", censored["ADD_Data_Raw"].max())):
        rounded = int(round(float(value)))
        assert macros[name] == f"{rounded // 1000}{{,}}{rounded % 1000:03d}"
    assert "nan" not in " ".join(macros.values()).lower()


def test_R12_every_produced_text_file_ends_in_a_newline():
    for path in (SOURCE, SECTION, REQUIREMENTS, LOG, TABLES_DIR / "R12_claims.tex",
                 ROOT / "run_experiment_R12.sh", REFERENCE_DIR / "orphans" / "README.md",
                 *DATA_DIR.glob("*.csv")):
        assert path.read_text().endswith("\n"), path


def test_R12_the_produced_sources_and_logs_carry_no_confirmatory_language():
    banned = re.compile(r"proves|proven|perfectly valid|validates the (theorem|thesis|claim)"
                        r"|confirms the|as expected|triumph|victory|irrefutable|brilliant",
                        re.IGNORECASE)
    for path in (SOURCE, LOG, SECTION):
        offending = [line for line in path.read_text().splitlines() if banned.search(line)]
        assert not offending, f"{path.name}: {offending[:3]}"


def test_R12_the_produced_sources_carry_no_banned_construct():
    text = SOURCE.read_text()
    assert "iterrows" not in text
    assert not re.search(r"except\s*:", text)
    assert not re.search(r"['\"]/home/", text)
    # S4bis, sixth corollary: a bare sqrt of a sample size is a defect of form.
    for match in re.finditer(r"np\.sqrt\(len|np\.sqrt\(n[^a-z_]", text):
        block = text[max(0, match.start() - 900):match.start()]
        assert "deff" in block, f"a bare sqrt(n) at offset {match.start()}"


# =====================================================================
# REPORTING -- ASSERTS NOTHING
# =====================================================================

def test_R12_report_the_campaign_against_its_witness(leverage, singularity, witness_a, witness_b):
    print("\n--- R12 against the submitted witness, at v87's printing precision ---")
    print(f"{'quantity':<34} {'v87':>10} {'regen':>10} {'witness':>10}")
    rows = [
        ("L349 Ljung-Box at gamma_lev = 0", f"{V87_LB_DATA[0]}%",
         f"{float(leverage['lb_data_pct'].iloc[0]):.1f}%",
         f"{float(witness_a['lb_data_pct'].iloc[0]):.1f}%"),
        ("L349 Ljung-Box at gamma_lev = 0.28", f"{V87_LB_DATA[1]}%",
         f"{float(leverage['lb_data_pct'].iloc[-1]):.1f}%",
         f"{float(witness_a['lb_data_pct'].iloc[-1]):.1f}%"),
        ("L349 FPR at gamma_lev = 0", f"{V87_FPR_DATA[0]}%",
         f"{float(leverage['fpr_data'].iloc[0]):.1f}%",
         f"{float(witness_a['fpr_data'].iloc[0]):.1f}%"),
        ("L349 FPR at gamma_lev = 0.28", f"{V87_FPR_DATA[1]}%",
         f"{float(leverage['fpr_data'].iloc[-1]):.1f}%",
         f"{float(witness_a['fpr_data'].iloc[-1]):.1f}%"),
        ("L349 Concept FPR min", f"{V87_FPR_CONCEPT[0]}%",
         f"{float(leverage['fpr_concept'].min()):.1f}%",
         f"{float(witness_a['fpr_concept'].min()):.1f}%"),
        ("L349 Concept FPR max", f"{V87_FPR_CONCEPT[1]}%",
         f"{float(leverage['fpr_concept'].max()):.1f}%",
         f"{float(witness_a['fpr_concept'].max()):.1f}%"),
        ("L349 Concept Ljung-Box min", f"{V87_LB_CONCEPT[0]}%",
         f"{float(leverage['lb_concept_pct'].min()):.1f}%",
         f"{float(witness_a['lb_concept_pct'].min()):.1f}%"),
        ("L349 Concept Ljung-Box max", f"{V87_LB_CONCEPT[1]}%",
         f"{float(leverage['lb_concept_pct'].max()):.1f}%",
         f"{float(witness_a['lb_concept_pct'].max()):.1f}%"),
        ("L353 detection at nu = 10", f"{100 * V87_DET_NU_TEN:.0f}%",
         f"{100 * float(singularity['det_rate_data'].iloc[0]):.0f}%",
         f"{100 * float(witness_b['det_rate_data'].iloc[0]):.0f}%"),
        ("L353 detection at nu = 7", f"{100 * V87_DET_NU_SEVEN:.0f}%",
         f"{100 * float(singularity[np.isclose(singularity['nu'], 7.0)]['det_rate_data'].iloc[0]):.0f}%",
         f"{100 * float(witness_b[np.isclose(witness_b['nu'], 7.0)]['det_rate_data'].iloc[0]):.0f}%"),
    ]
    for label, printed, regen, wit in rows:
        print(f"{label:<34} {printed:>10} {regen:>10} {wit:>10}")


def test_R12_report_the_control_layer(diagnostics):
    print("\n--- R12 control layer ---")
    for quantity in ("invariance_slope", "invariance_slope_se_ols",
                     "invariance_slope_se_bootstrap", "invariance_slope_pvalue",
                     "invariance_slope_crn", "ks_statistic_all", "ks_pvalue_all"):
        sub = diagnostics[diagnostics["quantity"] == quantity]
        if len(sub):
            print(f"{quantity:<32} {float(sub['value'].iloc[0])!r}")
    clamp = diagnostics[diagnostics["quantity"] == "clamp_rate_per_step"]
    print(f"{'clamp binding rate, max over grid':<32} {float(clamp['value'].max())!r} "
          f"over {len(clamp)} grid points")
    deff = diagnostics[diagnostics["quantity"] == "kish_design_effect"]
    for row in deff.itertuples(index=False):
        print(f"{'deff ' + str(row.arm):<32} {float(row.value)!r}")
