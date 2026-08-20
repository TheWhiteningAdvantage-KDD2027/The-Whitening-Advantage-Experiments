"""
R08 -- the adverse direction and the discrete null law. Acceptance and reporting.

Three kinds of statement live in this file and they are kept apart deliberately.

*Blocking assertions* rest either on a value v87 PRINTS, compared at v87's own
printing precision, or on a deterministic relation reimplemented here
INDEPENDENTLY of the experiment -- the fair-coin absorbing-chain law of the
2delta lattice written as an explicit enumerated sparse transition matrix rather
than as the experiment's column algebra, the path enumeration rebuilt from an
integer bit mask, the Wilson interval written as the two roots of the score
equation rather than as a centre and a margin, the lattice coordinate of each
threshold recomputed in exact rational arithmetic, and the comparison operator
re-parsed from the two module sources. NONE rests on a value R08 produced.

*Self-invalidating assertions* state a deviation. Each is written with an
explicit z against its own standard error, never as an equality at printed
precision, because preamble S2 pre-classifies every Monte-Carlo value of this
stream as moving under the mandated re-keying: a blocking equality on such a
value would be a gate that fails by construction, whose only exit is a widened
tolerance, which preamble S7 bans. If a later campaign brings one of these
values back, the test fires and what changes is `docs/DEVIATIONS.md`, not the
tolerance.

*Reporting output* prints the D0-D3 classification, the operator levels and the
boundary counter, the pairing diagnostic and the control nulls, and asserts
nothing.

WHY THE WITNESS IS NOT A BLOCKING ANCHOR. `data/reference/README.md` states it
outright: a witness value is the "published value" column of a D0-D3
comparison, never the anchor of a blocking assertion, because a cell-by-cell
equality gate converts every legitimate correction into a test failure. R08's
128-bit re-keying redraws every Monte-Carlo value of the campaign by
construction, so a witness gate here would fail on the first run.

THE FOUR SELF-INVALIDATING ASSERTIONS, AND WHAT EACH WOULD MEAN IF IT FIRED.

`test_R08_the_monte_carlo_numerals_of_L241_and_L311_move_within_their_own_sampling_error`
asserts |z| <= 3 on each printed numeral that has moved at v87's own printing
precision, against the standard error of the difference between two independent
campaigns of the same design. A z beyond 3 is a finding to characterise in
AUDIT_R08.md, never a tolerance to widen.

`test_R08_the_level_the_implemented_operator_delivers_at_lambda_star_is_above_nominal`
asserts the D3 the register carries as `R08-delivered-level-above-nominal`. If a
later campaign or a changed operator brings the delivered level to or below
nominal, the test fires and the register entry is what is withdrawn.

`test_R08_the_implemented_float_test_coincides_with_the_weak_operator` asserts
control C1's empirical finding. It is stated for this threshold, this horizon and
this accumulation order only, and if a later campaign separates the two operators
the test fires and the section is what changes.

`test_R08_the_whiteness_gap_maximum_has_moved_from_the_witness_campaign` asserts
the D2 `R08-campaign-redraw` carries on the maximum whiteness gap. If a later
campaign brings it back to the witness value, the test fires and the numeral
leaves the register entry.
"""

import ast
import math
import re
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import sparse
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "results" / "R08_adverse_lattice" / "data"
FIGURES_DIR = ROOT / "results" / "R08_adverse_lattice" / "figures"
TABLES_DIR = ROOT / "results" / "R08_adverse_lattice" / "tables"
REFERENCE_DIR = ROOT / "data" / "reference" / "R08"
SOURCE_A = ROOT / "experiments" / "R08_adverse_lattice" / "exp_R08_adverse_lattice_a.py"
SOURCE_B = ROOT / "experiments" / "R08_adverse_lattice" / "exp_R08_adverse_lattice_b.py"
R07_SOURCE = ROOT / "experiments" / "R07_estimated_mean" / "exp_R07_estimated_mean.py"
R07_DATA = ROOT / "results" / "R07_estimated_mean" / "data"
R10_DATA = ROOT / "results" / "R10_skew_robustness" / "data"
LOG_A = ROOT / "logs" / "R08_adverse_lattice" / "exp_R08_adverse_lattice_a.log"
LOG_B = ROOT / "logs" / "R08_adverse_lattice" / "exp_R08_adverse_lattice_b.log"
SECTION = ROOT / "docs" / "sections" / "R08.md"
AUDIT = ROOT / "docs" / "audits" / "AUDIT_R08.md"

# =====================================================================
# THE PROTOCOL, AS v87 SECTION 1 AND THE DELIVERED SCRIPT FIX IT
# =====================================================================
B_GRID = (0.00, 0.02, 0.05, 0.075, 0.10, 0.15)
LAMBDA_GRID_DECIMAL = ('11.0', '11.2', '11.4', '11.6', '11.8', '12.0')
N_SEEDS = 10000
N_STREAMS = 200000
H = 5000
DELTA = 0.1
LB_LEVEL = 0.05
LATTICE_UNIT = 2.0 * DELTA
LATTICE_UP = 2
LATTICE_DOWN = 3
NOMINAL_LEVEL = 0.05
STAR_UNITS = 57
ABOVE_UNITS = 56

# =====================================================================
# ANCHORS -- EVERY ONE OF THEM PRINTED IN articleB_whitening_v87.tex
# =====================================================================
# L241: "At $\delta = 0.1$, $H = 5{,}000$, the levels bracketing $5\%$ are
# $5.03\%$ at $\lambda = 11.2$ and $4.29\%$ at $\lambda = 11.4$
# ($2 \times 10^5$ fair-coin streams); we take the nearest attainable level at
# or below nominal, $\lambda^{\star} = 11.4$."
V87_LEVEL_ABOVE = 0.0503
V87_LEVEL_BELOW = 0.0429
V87_LAMBDA_STAR = 11.4
# L311 and the Figure 8 caption: "the false-alarm rate collapses to $0.86\%$ at
# $b = 0.15$, while naive under-centering inflates it to $20.8\%$"; "the
# injected-bias arm and the naive arm at $\phi = b$ reject within three points of
# each other across a range spanning $5$ to $100\%$"; "the under-centering
# penalty is still only $1.1$ points of false-alarm rate".
V87_FPR_COLLAPSE = 0.0086
V87_FPR_INFLATE = 0.208
V87_WHITENESS_BOUND_POINTS = 3.0
V87_PENALTY_POINTS = 1.1
V87_RANGE_LOW = 0.05
V87_RANGE_HIGH = 1.00
# Figure 8 caption: "$10{,}000$ trajectories/point for A--B; $2 \times 10^5$
# fair-coin streams for C".
V87_TRAJECTORIES_PER_POINT = 10000
V87_STREAMS_PANEL_C = 200000

# =====================================================================
# TOLERANCES, EACH DERIVED FROM A MECHANISM
# =====================================================================
FLOAT64_EPS = float(np.finfo(np.float64).eps)
# The lattice law is a mass-preserving forward recursion of H = 5,000 steps. The
# experiment applies it by array slicing, this file by an explicit enumerated
# sparse transition matrix; the two differ only in the order in which the same
# convex combinations are summed. Each step can displace an accumulated cell by
# a few ulps of a quantity bounded by 1, so the admissible absolute gap is
# 4 * H * eps and nothing else. It is not derived from any observed deviation.
LATTICE_ATOL = 4.0 * H * FLOAT64_EPS
# The Wilson interval is a closed form in float64 evaluated two ways. The two
# expressions differ by the reassociation of a product of at most five terms,
# bounded by 5 * eps = 1.1e-15 in relative terms; 1e-12 carries three orders of
# margin.
CLOSED_FORM_RTOL = 1e-12
# The z beyond which a self-invalidating comparison stops being a fluctuation
# and becomes a finding to report. Fixed at 3 before any measurement, from the
# 0.27% two-sided normal tail and from nothing else.
FINDING_Z = 3.0

MACRO_PREFIX = "REight"
MACRO_HEADER = "% Auto-generated by exp_R08_adverse_lattice_b.py -- do not edit."

BANNED_CONFIRMATORY = (r'proves|proven|perfectly valid|validates the (theorem|thesis|claim)'
                       r'|confirms the|as expected|triumph|victory|irrefutable|brilliant')

WITNESS_CARRIED = ('wilson_ci', 'prop_test', 'lb_pvalue', 'compute_phi_hat_vectorized',
                   'cusum_concept_fast', 'generate_dgp')
R07_CARRIED = ('exceeds', 'exceeds_units_strict', 'exceeds_units_weak',
               'cusum_concept_lattice_units', 'lattice_exceedance_exact',
               'lattice_exceedance_enumerated', 'lattice_survival', 'lambda_star_from_rule',
               'get_deterministic_seed', 'seed_sequence_for', 'rng_for', 'sign_flip_null_max')
COMPARISON_HELPERS = ('exceeds', 'exceeds_units_strict', 'exceeds_units_weak')
THRESHOLD_NAMES = frozenset({'lambda_star', 'lam', 'lam_units', 'lambda_units',
                             'threshold', 'threshold_units'})


def _read(path):
    assert path.exists(), f"Missing artefact: {path}"
    return pd.read_csv(path, float_precision='round_trip')


@pytest.fixture(scope="module")
def adverse():
    return _read(DATA_DIR / "R08_adverse_bias.csv")


@pytest.fixture(scope="module")
def null_law():
    return _read(DATA_DIR / "R08_null_law_lattice.csv")


@pytest.fixture(scope="module")
def operator_levels():
    return _read(DATA_DIR / "R08_operator_levels.csv")


@pytest.fixture(scope="module")
def lattice():
    return _read(DATA_DIR / "R08_lattice_exact_law.csv")


@pytest.fixture(scope="module")
def pairing():
    return _read(DATA_DIR / "R08_pairing_diagnostic.csv")


@pytest.fixture(scope="module")
def witness_bias():
    return _read(REFERENCE_DIR / "protocol_21c_adverse_bias.csv")


@pytest.fixture(scope="module")
def witness_lattice():
    return _read(REFERENCE_DIR / "protocol_21d_null_law_lattice.csv")


@pytest.fixture(scope="module")
def r07_lb_fpr():
    return _read(R07_DATA / "R07_estmean_lb_fpr.csv")


@pytest.fixture(scope="module")
def r07_lattice():
    return _read(R07_DATA / "R07_lattice_exact_law.csv")


@pytest.fixture(scope="module")
def r10_lattice():
    return _read(R10_DATA / "R10_lattice_exact_law.csv")


@pytest.fixture(scope="module")
def macros():
    path = TABLES_DIR / "R08_claims.tex"
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


# =====================================================================
# INDEPENDENT REIMPLEMENTATIONS
# =====================================================================

def independent_fair_coin_lattice_exceedance(horizon, lam_units):
    """
    P(M_H > lam_units) on the 2delta lattice under a fair-coin sign stream,
    written as an EXPLICIT enumerated sparse transition over the joint state
    space rather than as the experiment's array slicing.

    The state is (S_pos, S_neg) in units of 2delta, both clamped at 0 and
    absorbed above `lam_units`; the up branch moves S_pos by +2 with probability
    1/2 while S_neg shrinks by 3 with a floor at 0, and the down branch is the
    mirror image. Every transition is listed by hand here and applied as a single
    sparse matrix-vector product per step, so agreement with the experiment is a
    statement about the transcription and not about the model.
    """
    side = lam_units + 1
    size = side * side
    absorbing = size
    rows, cols, vals = [], [], []
    for a in range(side):
        for b in range(side):
            source = a * side + b
            for probability, (a_next, b_next) in (
                    (0.5, (a + LATTICE_UP, max(0, b - LATTICE_DOWN))),
                    (0.5, (max(0, a - LATTICE_DOWN), b + LATTICE_UP))):
                target = absorbing if (a_next > lam_units or b_next > lam_units) \
                    else a_next * side + b_next
                rows.append(target)
                cols.append(source)
                vals.append(probability)
    rows.append(absorbing)
    cols.append(absorbing)
    vals.append(1.0)
    transition = sparse.csr_matrix((np.asarray(vals, dtype=np.float64),
                                    (np.asarray(rows), np.asarray(cols))),
                                   shape=(size + 1, size + 1))
    state = np.zeros(size + 1, dtype=np.float64)
    state[0] = 1.0
    for _ in range(horizon):
        state = transition.dot(state)
    return float(state[absorbing])


def independent_enumerated_exceedance(horizon, lam_units):
    """
    P(M_H > lam_units) by exhaustive enumeration of all 2^H sign paths, with the
    running maximum tracked in exact integer arithmetic written inline here.
    Feasible only at the small horizons the experiment validates on.
    """
    exceeding = 0
    for mask in range(2 ** horizon):
        s_pos = s_neg = maximum = 0
        for step in range(horizon):
            bit = (mask >> step) & 1
            s_pos = max(0, s_pos + (LATTICE_UP if bit else -LATTICE_DOWN))
            s_neg = max(0, s_neg + (-LATTICE_DOWN if bit else LATTICE_UP))
            maximum = max(maximum, s_pos, s_neg)
        if maximum > lam_units:
            exceeding += 1
    return exceeding / float(2 ** horizon)


def wilson_second_form(k, n, z=1.959963984540054):
    """
    The Wilson score interval written as the two roots of the score equation,
    which is a different algebraic route from the centre-and-margin form the
    experiment carries.
    """
    p = k / n
    a = 1.0 + z * z / n
    b = -(2.0 * p + z * z / n)
    c = p * p
    disc = b * b - 4.0 * a * c
    root = math.sqrt(max(0.0, disc))
    return (-b - root) / (2.0 * a), (-b + root) / (2.0 * a)


def exact_lattice_units(decimal_text):
    """
    The lattice coordinate of a threshold in exact rational arithmetic on the
    decimal v87 prints, written here independently of the experiment's helper.
    5 * lambda must be an integer for lambda to be attainable.
    """
    ratio = Fraction(decimal_text) * 5
    return (int(ratio) if ratio.denominator == 1 else None), ratio.denominator == 1


def source_segments(path, names):
    text = Path(path).read_text()
    tree = ast.parse(text)
    return {node.name: ast.get_source_segment(text, node)
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in names}


def paired_difference_se(rate_a, rate_b, n):
    """
    The standard error of the DIFFERENCE between two campaigns of the same
    design, which is sqrt(2) times the standard error of one, because the
    printed value is itself one Monte-Carlo realisation of that design.

    S4bis's 6th corollary: the design effect is stated before the standard
    error. Each campaign's cell is a proportion over units keyed on their index
    alone, so within a cell the observations are i.i.d. and deff = 1.0.
    """
    deff = 1.0
    return math.sqrt(deff * (rate_a * (1.0 - rate_a) + rate_b * (1.0 - rate_b)) / n)


# =====================================================================
# BLOCKING -- DETERMINISTIC RELATIONS AND PRINTED VALUES
# =====================================================================

def test_R08_every_artefact_the_plan_lists_exists_with_its_prescribed_schema(
        adverse, null_law, operator_levels, lattice, pairing):
    """Schema, cardinality, row order, clamping and the absence of NaN."""
    assert list(adverse.columns) == [
        'b', 'N_seeds', 'lb_reject_biased', 'lb_ci_low', 'lb_ci_high',
        'fpr_biased', 'fpr_ci_low', 'fpr_ci_high', 'lb_reject_naive_ref', 'fpr_naive_ref',
        'delta_lb_pp', 'delta_fpr_pp', 'z_lb', 'pval_lb', 'z_fpr', 'pval_fpr',
        'z_lb_paired', 'pval_lb_paired', 'z_fpr_paired', 'pval_fpr_paired',
        'deff_lb', 'deff_fpr']
    assert list(null_law.columns) == [
        'lambda', 'lambda_units', 'N_streams', 'P_exceed_strict', 'CI_low_strict',
        'CI_high_strict', 'P_exceed_weak', 'CI_low_weak', 'CI_high_weak',
        'exact_level_strict', 'exact_level_weak', 'is_lattice_point', 'bracket_role']
    assert len(adverse) == len(null_law) == len(B_GRID) == 6
    assert not adverse.isna().any().any()
    assert not null_law.isna().any().any()

    # Row order is the explicit grid, never a sort of a float column.
    assert list(adverse['b']) == list(B_GRID)
    assert list(null_law['lambda']) == [float(text) for text in LAMBDA_GRID_DECIMAL]
    assert (adverse['N_seeds'] == V87_TRAJECTORIES_PER_POINT).all()
    assert (null_law['N_streams'] == V87_STREAMS_PANEL_C).all()

    assert set(operator_levels['record_type']) == {'exact_level', 'realised_level',
                                                   'ulp_boundary', 'operator_delta'}
    assert set(lattice['record_type']) == {'exact_survival', 'enumeration_validation'}
    assert set(pairing['record_type']) == {'per_b', 'ks_calibration', 'sign_flip_null_max',
                                           'whiteness_bound'}
    assert len(pairing[pairing['record_type'] == 'per_b']) == len(B_GRID)
    assert (FIGURES_DIR / "fig08_adverse_lattice.png").exists()

    # Every interval bound of the stream is clipped into [0, 1] before
    # persistence, which is what preamble S7 requires.
    for low, rate, high in (('lb_ci_low', 'lb_reject_biased', 'lb_ci_high'),
                            ('fpr_ci_low', 'fpr_biased', 'fpr_ci_high')):
        assert adverse[low].between(0.0, 1.0).all()
        assert adverse[high].between(0.0, 1.0).all()
        assert (adverse[low] <= adverse[rate]).all()
        assert (adverse[rate] <= adverse[high]).all()
    for low, rate, high in (('CI_low_strict', 'P_exceed_strict', 'CI_high_strict'),
                            ('CI_low_weak', 'P_exceed_weak', 'CI_high_weak')):
        assert null_law[low].between(0.0, 1.0).all()
        assert null_law[high].between(0.0, 1.0).all()
        assert (null_law[low] <= null_law[rate]).all()
        assert (null_law[rate] <= null_law[high]).all()


def test_R08_the_operating_threshold_is_fifty_seven_lattice_units(null_law):
    """
    BLOCKING, structural. Under a dead band delta = 0.1 the two CUSUM branches
    move by (1 - 1/2) - delta = +0.4 and -((0 - 1/2) - delta) = -0.6, i.e. by +2
    and -3 in units of 2delta = 0.2, so M_H is an integer multiple of 0.2 and
    lambda* = 11.4 is exactly 57 lattice units. Re-derived here from the two
    constants v87's own design fixes, and the lattice-point verdict of every grid
    threshold is recomputed in exact rational arithmetic on the printed decimal.
    """
    assert abs((1.0 - 0.5 - DELTA) - LATTICE_UP * LATTICE_UNIT) <= 4.0 * FLOAT64_EPS
    assert abs((0.5 + DELTA) - LATTICE_DOWN * LATTICE_UNIT) <= 4.0 * FLOAT64_EPS
    assert STAR_UNITS * LATTICE_UNIT == V87_LAMBDA_STAR, (
        "57 * 0.2 must be the float64 of the 11.4 v87 prints, bit for bit")
    for position, text in enumerate(LAMBDA_GRID_DECIMAL):
        units, is_lattice = exact_lattice_units(text)
        assert int(null_law['lambda_units'].iloc[position]) == units
        assert bool(null_law['is_lattice_point'].iloc[position]) is is_lattice is True
        assert float(null_law['lambda'].iloc[position]) == float(text)
    # The column is a computation with two possible answers, not the literal
    # `is_lattice = True` the delivered script writes at its line 373: a
    # threshold that is not a multiple of 2delta returns False here.
    assert exact_lattice_units('11.3') == (None, False)
    assert exact_lattice_units('11.1') == (None, False)
    # Neither float route decides the question, which is why the column is
    # computed on the printed decimal and not on its binary neighbour.
    assert 11.2 / LATTICE_UNIT != 56.0
    assert 56 * LATTICE_UNIT != 11.2


def test_R08_the_exact_lattice_law_reproduces_under_an_independent_dynamic_program(lattice):
    """
    BLOCKING, deterministic. The exact survival values the experiment persists at
    H = 5,000 are recomputed here by an explicit enumerated sparse transition
    matrix over the joint (S_pos, S_neg) state space, on the three lattice points
    that carry L241's bracketing statement and lambda* itself.
    """
    survival = lattice[lattice['record_type'] == 'exact_survival']
    checked = 0
    for units in (55, ABOVE_UNITS, STAR_UNITS):
        row = survival[survival['lambda_units'] == units].iloc[0]
        mine = independent_fair_coin_lattice_exceedance(H, units)
        assert abs(mine - float(row.exact_level)) <= LATTICE_ATOL, (
            f"lambda = {units} lattice units: the experiment gives {row.exact_level!r} and an "
            f"independent absorbing-chain program gives {mine!r}, a gap of "
            f"{abs(mine - float(row.exact_level)):.3e} against a budget of {LATTICE_ATOL:.3e} "
            f"derived from {H} mass-preserving float64 steps.")
        checked += 1
    assert checked == 3


def test_R08_the_enumeration_validation_agrees_with_an_independent_enumeration(lattice):
    """
    BLOCKING, deterministic. The experiment validates its dynamic program against
    its own path enumeration; this test re-enumerates the same paths from an
    integer bit mask and an inline recursion, at the smallest of the validated
    horizons where the enumeration is free.
    """
    validation = lattice[lattice['record_type'] == 'enumeration_validation']
    assert len(validation) == 16
    smallest = validation[validation['H'] == validation['H'].min()]
    assert len(smallest) == 4
    for row in smallest.itertuples(index=False):
        mine = independent_enumerated_exceedance(int(row.H), int(row.lambda_units))
        # BUDGET FROM THE MECHANISM: both routes count the same integer number of
        # exceeding paths and divide by the same power of two, so the two values
        # are equal in exact arithmetic and the division is a single correctly
        # rounded operation on both sides. The admissible gap is zero.
        assert mine == float(row.enumerated_level), (
            f"H = {int(row.H)}, lambda = {int(row.lambda_units)}: the experiment enumerates "
            f"{row.enumerated_level!r} and this file {mine!r}")
        assert float(row.abs_difference) == 0.0


def test_R08_the_three_streams_agree_on_the_cells_they_share(lattice, r07_lattice, r10_lattice):
    """
    BLOCKING, deterministic. Control C2, re-run outside the experiment. R07 owns
    an H = 5,000 exact survival table and R08's must equal it cell by cell; R07
    and R10 each own a small-H path enumeration and R08's must equal both on the
    cells they share. R10 carries NO H = 5,000 cell -- its campaign runs at
    H = 8,000 -- which is why the prompt's single three-way comparison is split.
    """
    r10_here = r10_lattice[r10_lattice['H'] == H]
    assert len(r10_here) == 0, (
        "R10 now carries an H = 5,000 cell; the C2 re-derivation recorded in AUDIT_R08.md "
        "section 6 no longer applies and the control can be stated as the prompt wrote it.")

    mine = lattice[lattice['record_type'] == 'exact_survival']
    theirs = r07_lattice[(r07_lattice['record_type'] == 'exact_survival')
                         & (r07_lattice['H'] == H)]
    joined = mine.merge(theirs[['lambda_units', 'exact_level']], on='lambda_units',
                        suffixes=('_r08', '_r07'))
    assert len(joined) == 16
    assert (joined['exact_level_r08'] == joined['exact_level_r07']).all(), (
        "two exact enumerations of one law returned different numbers; that is a porting "
        "defect in one of the two streams and not a tolerance question")

    enumerated = lattice[lattice['record_type'] == 'enumeration_validation']
    r07_cells = {(int(row.H), int(row.lambda_units)): float(row.enumerated_level)
                 for row in r07_lattice[r07_lattice['record_type'] == 'enumeration_validation']
                 .itertuples(index=False)}
    r10_pool = r10_lattice[(r10_lattice['record_type'] == 'enumeration_validation')
                           & (r10_lattice['q'] == 0.5)]
    r10_cells = {(int(row.H), int(row.lambda_units)): float(row.enumerated_level)
                 for row in r10_pool.itertuples(index=False)}
    three_way = 0
    for row in enumerated.itertuples(index=False):
        key = (int(row.H), int(row.lambda_units))
        if key in r07_cells:
            assert float(row.enumerated_level) == r07_cells[key], f"R07 disagrees at {key}"
        if key in r10_cells:
            assert float(row.enumerated_level) == r10_cells[key], f"R10 disagrees at {key}"
        if key in r07_cells and key in r10_cells:
            three_way += 1
    assert three_way == 8, (
        f"the three streams share {three_way} enumeration cells, not the 8 the C2b split "
        f"records (H in (10, 12) x lambda_units in (4, 5, 6, 7))")


def test_R08_the_bracketing_of_the_nominal_level_is_the_one_L241_states(null_law, lattice):
    """
    BLOCKING, on the qualitative content of L241 and deterministic. "The levels
    bracketing 5% are ... at lambda = 11.2 and ... at lambda = 11.4; we take the
    nearest attainable level at or below nominal, lambda* = 11.4." Read on the
    EXACT law, where the statement has trigger probability 0: the exact strict
    level is non-increasing in lambda, exactly one adjacent pair of the grid
    straddles 5%, and it is the pair L241 names.
    """
    strict = null_law['exact_level_strict'].to_numpy(dtype=float)
    assert np.all(np.diff(strict) < 0.0), "the exact survival function must be strictly decreasing"
    straddle = [index for index in range(len(strict) - 1)
                if strict[index] > NOMINAL_LEVEL >= strict[index + 1]]
    assert straddle == [1], (
        f"the grid pairs that straddle {NOMINAL_LEVEL} are {straddle}; L241 names exactly one, "
        f"(11.2, 11.4)")
    assert list(null_law['bracket_role']) == ['none', 'above_nominal', 'below_nominal',
                                              'none', 'none', 'none']
    assert int(null_law['lambda_units'].iloc[straddle[0] + 1]) == STAR_UNITS
    assert float(null_law['lambda'].iloc[straddle[0] + 1]) == V87_LAMBDA_STAR
    # lambda* by L241's own rule, re-derived on the full scanned region and not
    # on the six-point grid: the SMALLEST lattice threshold whose exact level is
    # at or below nominal.
    survival = lattice[lattice['record_type'] == 'exact_survival'].sort_values('lambda_units')
    eligible = survival[survival['exact_level'] <= NOMINAL_LEVEL]
    assert int(eligible['lambda_units'].iloc[0]) == STAR_UNITS
    # And the weak level is the survival function one lattice point lower, which
    # is the identity P(M >= u) = P(M > u - 1) on the integer lattice.
    for index in range(1, len(null_law)):
        assert (float(null_law['exact_level_weak'].iloc[index])
                == float(null_law['exact_level_strict'].iloc[index - 1]))


def test_R08_the_wilson_intervals_reproduce_from_a_second_algebraic_form(adverse, null_law):
    """
    BLOCKING, deterministic. Every persisted Wilson bound is recomputed here as
    a root of the score equation rather than as a centre and a margin.
    """
    checked = 0
    for row in adverse.itertuples(index=False):
        n = int(row.N_seeds)
        for rate, low, high in ((row.lb_reject_biased, row.lb_ci_low, row.lb_ci_high),
                                (row.fpr_biased, row.fpr_ci_low, row.fpr_ci_high)):
            mine_low, mine_high = wilson_second_form(int(round(rate * n)), n)
            assert low == pytest.approx(max(0.0, min(1.0, mine_low)), rel=CLOSED_FORM_RTOL,
                                        abs=1e-15)
            assert high == pytest.approx(max(0.0, min(1.0, mine_high)), rel=CLOSED_FORM_RTOL,
                                         abs=1e-15)
            checked += 2
    for row in null_law.itertuples(index=False):
        n = int(row.N_streams)
        for rate, low, high in ((row.P_exceed_strict, row.CI_low_strict, row.CI_high_strict),
                                (row.P_exceed_weak, row.CI_low_weak, row.CI_high_weak)):
            mine_low, mine_high = wilson_second_form(int(round(rate * n)), n)
            assert low == pytest.approx(max(0.0, min(1.0, mine_low)), rel=CLOSED_FORM_RTOL,
                                        abs=1e-15)
            assert high == pytest.approx(max(0.0, min(1.0, mine_high)), rel=CLOSED_FORM_RTOL,
                                         abs=1e-15)
            checked += 2
    assert checked == 2 * 2 * len(B_GRID) + 2 * 2 * len(LAMBDA_GRID_DECIMAL)


def test_R08_one_comparison_operator_is_shared_by_both_modules():
    """
    BLOCKING, structural. Control C1's AST legs, re-run outside the experiment:
    `exceeds` must be a single `Compare` carrying `ast.Gt`, and no ordering
    comparison outside the three declared helpers, in EITHER module of this
    stream, may mention a threshold name. A campaign that calibrates with `>` and
    evaluates with `>=` reports a level that does not exist.
    """
    trees = {path.name: ast.parse(path.read_text()) for path in (SOURCE_A, SOURCE_B)}
    functions = {node.name: node for node in ast.walk(trees[SOURCE_A.name])
                 if isinstance(node, ast.FunctionDef)}
    for helper in COMPARISON_HELPERS:
        assert helper in functions, f"{helper} is missing from {SOURCE_A.name}"
    body = [node for node in functions['exceeds'].body
            if not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant))]
    assert len(body) == 1 and isinstance(body[0], ast.Return)
    compare = body[0].value
    assert isinstance(compare, ast.Compare)
    assert len(compare.ops) == 1 and isinstance(compare.ops[0], ast.Gt)
    assert isinstance(functions['exceeds_units_strict'].body[-1].value.ops[0], ast.Gt)
    assert isinstance(functions['exceeds_units_weak'].body[-1].value.ops[0], ast.GtE)

    whitelisted = {id(node) for helper in COMPARISON_HELPERS
                   for node in ast.walk(functions[helper]) if isinstance(node, ast.Compare)}
    ordering = (ast.Gt, ast.GtE, ast.Lt, ast.LtE)
    offending = []
    for name, tree in trees.items():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare) or id(node) in whitelisted:
                continue
            names = {sub.id for sub in ast.walk(node) if isinstance(sub, ast.Name)}
            if (names & THRESHOLD_NAMES) and any(isinstance(op, ordering) for op in node.ops):
                offending.append((name, getattr(node, 'lineno', -1)))
    assert not offending, (
        f"{len(offending)} ordering comparison(s) outside {COMPARISON_HELPERS} mention a "
        f"threshold name: {offending}")
    for routine, required in (('worker_mod_A', {'exceeds'}),
                              ('operator_levels_at', set(COMPARISON_HELPERS))):
        called = {sub.func.id for sub in ast.walk(functions[routine])
                  if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)}
        assert required <= called, f"{routine} does not call {sorted(required - called)}"


def test_R08_the_carried_primitives_are_byte_identical_to_both_owning_files():
    """
    BLOCKING, deterministic. Control C7, re-run outside the experiment: the
    eighteen carried primitives must be byte-identical to the two files that own
    them. Preamble S4.2 forbids hoisting any of them into experiments/common/, so
    the duplication is deliberate and this is what stops it drifting.
    """
    mine = source_segments(SOURCE_A, set(WITNESS_CARRIED) | set(R07_CARRIED))
    witness = source_segments(REFERENCE_DIR / "Priorite_21b_adverse_bias_and_null_law.py",
                              set(WITNESS_CARRIED))
    r07 = source_segments(R07_SOURCE, set(R07_CARRIED))
    for name in WITNESS_CARRIED:
        assert mine.get(name) == witness.get(name), f"{name} has drifted from the R08 witness"
    for name in R07_CARRIED:
        assert mine.get(name) == r07.get(name), f"{name} has drifted from exp_R07_estimated_mean.py"


def test_R08_the_two_dgp_primitives_are_ast_identical_across_their_two_owners():
    """
    BLOCKING, deterministic. What underwrites the cross-stream identity of
    control C6: R07's copy of `generate_dgp` and `compute_phi_hat_vectorized`
    carries blank lines the R08 witness does not, so BYTE identity across the two
    owners is false and is not asserted; the normalized ASTs must be equal, which
    is the statement that the two files compile the same instructions.
    """
    witness = source_segments(REFERENCE_DIR / "Priorite_21b_adverse_bias_and_null_law.py",
                              {'generate_dgp', 'compute_phi_hat_vectorized'})
    r07 = source_segments(R07_SOURCE, {'generate_dgp', 'compute_phi_hat_vectorized'})
    for name in ('generate_dgp', 'compute_phi_hat_vectorized'):
        assert witness[name] != r07[name], (
            f"{name} is now byte-identical across the two owners; AUDIT_R08.md records the "
            f"whitespace-only difference and the section is what changes")
        assert ast.dump(ast.parse(witness[name])) == ast.dump(ast.parse(r07[name]))
        assert ([line for line in witness[name].splitlines() if line.strip()]
                == [line for line in r07[name].splitlines() if line.strip()])


def test_R08_the_cross_stream_identity_with_R07_is_exact(adverse, pairing, r07_lb_fpr):
    """
    BLOCKING, deterministic, trigger probability 0. Control C6. `generate_dgp`
    draws z, h and eps without ever referencing phi and R08 keys its trajectories
    on R07's own ("trajectory", i), so R08's b = 0 arm IS R07's OLS-250 arm at
    phi = 0 and R08's pairing diagnostic at phi = b IS R07's NAIVE arm at
    phi = b. Both sides are read at round_trip and the equality is bit-for-bit.
    """
    reference = r07_lb_fpr[(r07_lb_fpr['arm'] == 'OLS-250')
                           & (r07_lb_fpr['phi'] == 0.0)].iloc[0]
    zero = adverse[adverse['b'] == 0.0].iloc[0]
    assert float(zero['lb_reject_biased']) == float(reference['lb_reject_rate'])
    assert float(zero['fpr_biased']) == float(reference['fpr_concept'])
    per_b = pairing[pairing['record_type'] == 'per_b']
    assert len(per_b) == len(B_GRID)
    for row in per_b.itertuples(index=False):
        naive = r07_lb_fpr[(r07_lb_fpr['arm'] == 'NAIVE')
                           & (r07_lb_fpr['phi'] == float(row.b))]
        assert len(naive) == 1
        assert float(row.lb_reject_naive) == float(naive['lb_reject_rate'].iloc[0])
        assert float(row.fpr_naive) == float(naive['fpr_concept'].iloc[0])
        assert bool(row.bit_identical_lb) and bool(row.bit_identical_fpr)
    # And the published reference columns of the v87 frame are those same cells.
    for row in adverse.itertuples(index=False):
        naive = r07_lb_fpr[(r07_lb_fpr['arm'] == 'NAIVE')
                           & (r07_lb_fpr['phi'] == float(row.b))].iloc[0]
        assert float(row.lb_reject_naive_ref) == float(naive['lb_reject_rate'])
        assert float(row.fpr_naive_ref) == float(naive['fpr_concept'])


def test_R08_the_sign_asymmetry_of_L311_holds_in_both_directions(adverse):
    """
    BLOCKING, on the qualitative content of L311 and of the Figure 8 panel B
    caption. "Injected over-centering makes the sign stream negatively
    autocorrelated and the false-alarm rate collapses ... while naive
    under-centering inflates it": the biased arm's rate must be non-increasing in
    b and the naive arm's non-decreasing, on the whole grid. This is the claim
    that carries the panel; the NUMERALS are classified separately.
    """
    biased = adverse['fpr_biased'].to_numpy(dtype=float)
    naive = adverse['fpr_naive_ref'].to_numpy(dtype=float)
    assert np.all(np.diff(biased) <= 0.0), (
        f"the over-centred arm's false-alarm rate is not non-increasing in b: {biased}")
    assert np.all(np.diff(naive) >= 0.0), (
        f"the under-centred arm's false-alarm rate is not non-decreasing in b: {naive}")
    assert biased[-1] < biased[0] < naive[-1]
    # The two arms start together at b = 0, where there is no mis-centering to
    # give a direction, and separate by an order of magnitude at the far end.
    assert naive[-1] / biased[-1] > 10.0


def test_R08_the_three_point_bound_of_L311_holds_with_its_extremum_envelope(adverse, pairing):
    """
    BLOCKING, on a value v87 PRINTS. "The injected-bias arm and the naive arm at
    phi = b reject within three points of each other across a range spanning 5 to
    100%." The maximum is over six correlated cells, so it is reported with its
    own bootstrap envelope (S4bis.4) and preamble S3 fixes the D3 criterion: a
    printed bound is crossed only when the 95% interval EXCLUDES it.
    """
    observed = 100.0 * float(adverse['delta_lb_pp'].abs().max())
    bound = pairing[pairing['record_type'] == 'whiteness_bound'].iloc[0]
    assert float(bound.observed) == pytest.approx(observed, rel=CLOSED_FORM_RTOL)
    assert float(bound.null_quantile) == V87_WHITENESS_BOUND_POINTS
    assert observed <= V87_WHITENESS_BOUND_POINTS, (
        f"the largest whiteness gap is {observed:.4f} points against the "
        f"{V87_WHITENESS_BOUND_POINTS:g} L311 states, with a 95% envelope of the maximum of "
        f"[{float(bound.ci_low):.4f}, {float(bound.ci_high):.4f}]. Preamble S3 makes this a D3 "
        f"only if that interval excludes the bound; either way no parameter, tolerance, seed or "
        f"bound is moved and docs/DEVIATIONS.md is what changes.")
    assert float(bound.ci_low) <= V87_WHITENESS_BOUND_POINTS <= float(bound.ci_high) \
        or float(bound.ci_high) < V87_WHITENESS_BOUND_POINTS
    # The range the same sentence states, at its own printing precision.
    rates = np.concatenate([adverse['lb_reject_biased'].to_numpy(dtype=float),
                            adverse['lb_reject_naive_ref'].to_numpy(dtype=float)])
    assert round(float(rates.min()), 2) == round(V87_RANGE_LOW, 2)
    assert round(float(rates.max()), 2) == round(V87_RANGE_HIGH, 2)


def test_R08_the_family_wise_arithmetic_is_logged_before_any_gate_is_read():
    """
    BLOCKING, structural. S4bis requires the trigger probability of a family of
    tests to be computed and journalled BEFORE its result is interpreted. The log
    is read here and the order of the records is asserted.
    """
    text = LOG_A.read_text()
    family = text.find("FAMILY-WISE ARITHMETIC, LOGGED BEFORE ANY RESULT IS INTERPRETED")
    c3_declaration = text.find("C3, BEFORE ANY RESULT IS READ")
    c4_declaration = text.find("C4, BEFORE ANY RESULT IS READ")
    c3_result = text.find("C3 BRACKETING ON THE MEASURED STRICT LEVELS")
    c4_pvalues = text.find("C4 THE SIX PROPORTION p-VALUES")
    c4_ks = text.find("C4 KS CALIBRATION")
    for marker in (family, c3_declaration, c4_declaration, c3_result, c4_pvalues, c4_ks):
        assert marker >= 0
    assert family < c3_declaration < c3_result
    assert family < c4_declaration < c4_pvalues < c4_ks
    assert "1 - (1 - 0.05)^6 = 26.4908%" in text
    # The ULP boundary counter is logged even at zero (prompt section 2.1).
    assert "C1 (a) THE ULP BOUNDARY COUNTER, logged even at zero" in text


def test_R08_macros_are_emitted_and_agree_with_the_frames(macros, adverse, null_law,
                                                          operator_levels, r07_lb_fpr):
    """
    BLOCKING, internal consistency. Every macro body must be the corresponding
    cell of a persisted frame at the precision it prints. This asserts that no
    literal was typed into R08_claims.tex, not that any value is right.
    """
    expected = {'REightFprCollapse', 'REightFprInflate', 'REightWhitenessGapMax',
                'REightWhitenessGapMaxAtB', 'REightWhitenessRangeLow', 'REightWhitenessRangeHigh',
                'REightLevelAbove', 'REightLevelBelow', 'REightLambdaStar', 'REightLatticeStep',
                'REightOperatorDelta', 'REightBoundaryCases',
                'REightPenaltyAtResidualMomentum'}
    assert set(macros) == expected
    assert all(name.startswith(MACRO_PREFIX) for name in macros)
    assert not any(name.startswith("REighth") for name in macros)
    assert all(body.strip() and 'nan' not in body.lower() for body in macros.values())
    text = (TABLES_DIR / "R08_claims.tex").read_text()
    for banned in ("EtaRmse", "SevenTimes", "BiasCoefficient", "ResidualMomentumCoefficient"):
        assert not re.search(r"\\newcommand\{\\REight[A-Za-z]*" + banned, text), (
            "R07 owns eta_rmse_over_sigma, the 'seven times' ratio and the constant 2.5")

    extreme = adverse[adverse['b'] == max(B_GRID)].iloc[0]
    assert macros['REightFprCollapse'] == f"{100.0 * float(extreme['fpr_biased']):.2f}\\%"
    assert macros['REightFprInflate'] == f"{100.0 * float(extreme['fpr_naive_ref']):.1f}\\%"
    gaps = 100.0 * adverse['delta_lb_pp'].abs().to_numpy(dtype=float)
    assert macros['REightWhitenessGapMax'] == f"{float(gaps.max()):.2f}"
    assert float(macros['REightWhitenessGapMaxAtB']) == float(
        adverse['b'].iloc[int(np.argmax(gaps))])
    rates = np.concatenate([adverse['lb_reject_biased'].to_numpy(dtype=float),
                            adverse['lb_reject_naive_ref'].to_numpy(dtype=float)])
    assert macros['REightWhitenessRangeLow'] == f"{100.0 * float(rates.min()):.1f}\\%"
    assert macros['REightWhitenessRangeHigh'] == f"{100.0 * float(rates.max()):.1f}\\%"
    above = null_law[null_law['lambda_units'] == ABOVE_UNITS].iloc[0]
    below = null_law[null_law['lambda_units'] == STAR_UNITS].iloc[0]
    assert macros['REightLevelAbove'] == f"{100.0 * float(above['P_exceed_strict']):.2f}\\%"
    assert macros['REightLevelBelow'] == f"{100.0 * float(below['P_exceed_strict']):.2f}\\%"
    assert macros['REightLambdaStar'] == f"{V87_LAMBDA_STAR:.1f}"
    assert macros['REightLatticeStep'] == f"{LATTICE_UNIT:.1f}"
    delta_row = operator_levels[operator_levels['record_type'] == 'operator_delta'].iloc[0]
    assert macros['REightOperatorDelta'] == f"{100.0 * float(delta_row['exact_level']):.2f}"
    ulp_row = operator_levels[operator_levels['record_type'] == 'ulp_boundary'].iloc[0]
    assert int(macros['REightBoundaryCases']) == int(ulp_row['count_within_ulp_budget'])
    naive_zero = r07_lb_fpr[(r07_lb_fpr['arm'] == 'NAIVE') & (r07_lb_fpr['phi'] == 0.0)].iloc[0]
    naive_two = r07_lb_fpr[(r07_lb_fpr['arm'] == 'NAIVE') & (r07_lb_fpr['phi'] == 0.02)].iloc[0]
    penalty = 100.0 * (float(naive_two['fpr_concept']) - float(naive_zero['fpr_concept']))
    assert macros['REightPenaltyAtResidualMomentum'] == f"{penalty:.1f}"


def test_R08_text_artefacts_end_with_a_newline():
    """BLOCKING. Preamble S6: the section and the requirements file are assembled
    by concatenation, so a missing final newline corrupts the result."""
    for path in (SECTION, AUDIT, ROOT / "requirements" / "R08.txt",
                 TABLES_DIR / "R08_claims.tex"):
        assert path.exists(), f"Missing deliverable: {path}"
        assert path.read_text().endswith("\n"), f"{path.name} does not end with a newline"


def test_R08_no_confirmatory_language_in_the_scripts_the_logs_or_the_section():
    """BLOCKING. Preamble S4.4: the grep must return empty on every produced file."""
    pattern = re.compile(BANNED_CONFIRMATORY, re.IGNORECASE)
    for path in (SOURCE_A, SOURCE_B, LOG_A, LOG_B, SECTION):
        assert path.exists(), f"Missing artefact: {path}"
        hits = [line for line in path.read_text().splitlines() if pattern.search(line)]
        assert not hits, f"{path.name} carries confirmatory language: {hits[:3]}"


def test_R08_the_scripts_own_S4_4_pattern_accepts_the_preambles_language():
    """
    BLOCKING, deterministic. `exp_R08_adverse_lattice_a.py` needs the S4.4 pattern
    at run time, because control C7 quotes an adapted routine only after the grep
    clears its segment. Writing the preamble's wording verbatim there would make
    the file fail the very grep it implements, so every alternative carries one of
    its own characters inside a single-character class. That device must not
    change the language the expression accepts, and this is what checks it: the
    script's compiled pattern is imported from the source and agreed with the
    preamble's own wording on every banned string and on the neutral technical
    uses §S4.4 explicitly leaves licit.
    """
    tree = ast.parse(SOURCE_A.read_text())
    assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == 'BANNED_CONFIRMATORY'
                           for target in node.targets)]
    assert len(assignments) == 1
    pattern_text = "".join(
        node.value for node in ast.walk(assignments[0].value)
        if isinstance(node, ast.Constant) and isinstance(node.value, str))
    theirs = re.compile(BANNED_CONFIRMATORY, re.IGNORECASE)
    mine = re.compile(pattern_text, re.IGNORECASE)
    probes = ("proves", "PROVEN", "perfectly valid", "validates the theorem",
              "validates the thesis", "validates the claim", "confirms the", "as expected",
              "triumph", "Victory", "irrefutable", "brilliant",
              "Control (a) Passed: Strict uniqueness across Mod A and Mod B seeds proven.",
              # Neutral technical uses S4.4 leaves licit, and near misses.
              "assertion passed", "validates the invariance of X", "approves the",
              "improvement", "the level is proved by nothing", "confirms that")
    for probe in probes:
        assert bool(mine.search(probe)) == bool(theirs.search(probe)), (
            f"the script's S4.4 pattern and the preamble's wording disagree on {probe!r}")
    # And the literal wording must not appear in the file the pattern lives in.
    assert not theirs.search(SOURCE_A.read_text())


def test_R08_the_produced_sources_carry_no_banned_construct():
    """
    BLOCKING. Preamble S7: no `iterrows`, no bare `except:`, no absolute path,
    no `np.random.seed`. S4bis's 6th corollary: no bare `np.sqrt` of a sample
    size, which is the form that silently assumes independence.
    """
    for path in (SOURCE_A, SOURCE_B):
        text = path.read_text()
        assert "iterrows" not in text
        assert not re.search(r"except\s*:", text)
        assert not re.search(r"['\"]/home/", text), "no absolute path may be embedded"
        assert "np.random.seed" not in text
        assert not re.search(r"np\.sqrt\(\s*(len\(|n_seeds|n_lattice|N_SEEDS|N_LATTICE)", text), (
            "a bare np.sqrt of a sample size assumes independence; S4bis's 6th corollary "
            "requires the design effect to be computed and logged in the same block")


# =====================================================================
# SELF-INVALIDATING -- EACH STATES A DEVIATION WITH ITS OWN z
# =====================================================================

def test_R08_the_monte_carlo_numerals_of_L241_and_L311_move_within_their_own_sampling_error(
        adverse, null_law):
    """
    SELF-INVALIDATING. v87 prints 5.03%, 4.29%, 0.86% and 20.8%, each to a stated
    number of decimals. Preamble S3 fixes the comparison: a printed numeral is
    read AT ITS PRINTING PRECISION, so a regenerated value that rounds to it has
    not moved at all (D0/D1) and there is nothing to compare against a standard
    error. Only a value whose rounding DIFFERS from the printed one has moved,
    and that gap is read against the standard error of the DIFFERENCE between two
    campaigns -- because the printed value is itself one Monte-Carlo realisation
    of the same design. A |z| beyond 3 on a numeral that HAS moved is a finding to
    characterise in AUDIT_R08.md, never a tolerance to widen (preamble S4.8).
    """
    above = null_law[null_law['lambda_units'] == ABOVE_UNITS].iloc[0]
    below = null_law[null_law['lambda_units'] == STAR_UNITS].iloc[0]
    extreme = adverse[adverse['b'] == max(B_GRID)].iloc[0]
    comparisons = (
        ('L241 level at lambda = 11.2', V87_LEVEL_ABOVE, float(above['P_exceed_strict']), 4,
         N_STREAMS),
        ('L241 level at lambda = 11.4', V87_LEVEL_BELOW, float(below['P_exceed_strict']), 4,
         N_STREAMS),
        ('Fig. 8 (B) FPR collapse at b = 0.15', V87_FPR_COLLAPSE, float(extreme['fpr_biased']), 4,
         N_SEEDS),
        ('Fig. 8 (B) FPR inflation at b = 0.15', V87_FPR_INFLATE, float(extreme['fpr_naive_ref']),
         3, N_SEEDS),
    )
    failures = []
    moved = []
    for label, printed, regenerated, decimals, n in comparisons:
        if round(regenerated, decimals) == round(printed, decimals):
            continue                      # D0 or D1: the printed value has not moved
        moved.append(label)
        se = paired_difference_se(printed, regenerated, n)
        z = (regenerated - printed) / se
        if abs(z) > FINDING_Z:
            failures.append(f"{label}: printed {printed!r}, regenerated {regenerated!r}, "
                            f"z = {z:+.2f} against a paired standard error of {se!r}")
    assert not failures, ("a printed numeral of L241 or L311 has moved beyond three standard "
                          "errors of the difference between two campaigns: " + "; ".join(failures))
    assert len(moved) == 4, (
        f"the set of printed numerals that move at v87's printing precision is {moved}; "
        f"docs/DEVIATIONS.md `R08-campaign-redraw` and `R07-campaign-redraw` record four")


def test_R08_the_level_the_implemented_operator_delivers_at_lambda_star_is_above_nominal(
        null_law, operator_levels):
    """
    SELF-INVALIDATING, and it is the D3 the register carries as
    `R08-delivered-level-above-nominal`. L241 states a selection rule -- "we take
    the nearest attainable level at or below nominal" -- and its own footnote
    states that the implemented test `M_H > lambda*` IS the mathematical
    `M_H >= lambda*`. Control C1 measures the second statement to hold on every
    one of the 2x10^5 streams, and the level the WEAK operator delivers at
    lambda* = 11.4 is above nominal: 5.1021% exactly, 5.08% measured. The two
    statements cannot both hold with the delivered level at or below nominal.

    The EXACT leg is deterministic and carries no interval. The Monte-Carlo leg
    is reported beside it and its Wilson interval does NOT exclude 5%, which is
    why the audit states the classification rests on the exact leg. If a later
    campaign or a changed operator brings the delivered level to or below
    nominal, this test fires and the register entry is what is withdrawn.
    """
    star = null_law[null_law['lambda_units'] == STAR_UNITS].iloc[0]
    exact_weak = float(star['exact_level_weak'])
    measured_weak = float(star['P_exceed_weak'])
    assert exact_weak > NOMINAL_LEVEL, (
        f"the exact weak level at lambda* is {exact_weak!r}, at or below the {NOMINAL_LEVEL} "
        f"nominal; the D3 `R08-delivered-level-above-nominal` must be withdrawn from "
        f"docs/DEVIATIONS.md")
    assert measured_weak > NOMINAL_LEVEL
    # The strict level is the one L241 prints and it does satisfy the rule; the
    # contradiction is between the rule and the operator, not inside either.
    assert float(star['exact_level_strict']) <= NOMINAL_LEVEL
    # And the gap between the two operators is the size the audit reports.
    delta_row = operator_levels[operator_levels['record_type'] == 'operator_delta'].iloc[0]
    assert float(delta_row['exact_level']) == pytest.approx(
        exact_weak - float(star['exact_level_strict']), rel=CLOSED_FORM_RTOL)
    assert float(delta_row['exact_level']) > 0.0
    # The Monte-Carlo leg alone does not exclude nominal, which the audit states.
    assert float(star['CI_low_weak']) < NOMINAL_LEVEL < float(star['CI_high_weak'])


def test_R08_the_implemented_float_test_coincides_with_the_weak_operator(operator_levels):
    """
    SELF-INVALIDATING. Control C1 measures what `M > lambda` implements on the
    lattice boundary. On this campaign it coincides with the mathematical
    `M >= lambda` on every one of the 2x10^5 streams, at every grid threshold.
    The statement is EMPIRICAL and holds for this horizon and this accumulation
    order only; if a later campaign separates the two operators the test fires
    and docs/sections/R08.md is what changes.
    """
    realised = operator_levels[operator_levels['record_type'] == 'realised_level']
    assert len(realised) == 3 * len(LAMBDA_GRID_DECIMAL)
    for units in sorted(set(realised['lambda_units'].astype(int))):
        cell = realised[realised['lambda_units'] == units]
        levels = {row.operator: (float(row.realised_level), float(row.disagreements_vs_strict),
                                 float(row.disagreements_vs_weak))
                  for row in cell.itertuples(index=False)}
        assert set(levels) == {'float M > lambda', 'exact M_units > lambda',
                               'exact M_units >= lambda'}
        assert levels['float M > lambda'][2] == 0.0, (
            f"at {units} lattice units the implemented float test no longer coincides with the "
            f"weak operator; docs/sections/R08.md and the C1 statement of record are what change")
        assert levels['float M > lambda'][1] > 0.0, (
            f"at {units} lattice units no stream reached the boundary, so this campaign separates "
            f"neither operator from the other and the C1 statement has no content on it")
        assert levels['float M > lambda'][0] == levels['exact M_units >= lambda'][0]
        assert levels['float M > lambda'][0] > levels['exact M_units > lambda'][0]
    ulp = operator_levels[operator_levels['record_type'] == 'ulp_boundary'].iloc[0]
    assert int(ulp['count_float_above']) > int(ulp['count_float_below']), (
        "the L241 footnote describes accumulation leaving M_H a few ulps ABOVE its exact lattice "
        "value; if the balance reverses, the empirical coincidence with the weak operator loses "
        "its mechanism and the section is what changes")


def test_R08_the_whiteness_gap_maximum_has_moved_from_the_witness_campaign(adverse, witness_bias):
    """
    SELF-INVALIDATING. The witness campaign's largest |delta_lb_pp| is 2.84
    points at b = 0.075; the re-keyed campaign's is smaller. That movement is the
    D2 the register carries as `R08-campaign-redraw`. If a later campaign brings
    it back to the witness value at v87's own two-decimal precision, this test
    fires and the numeral leaves the register entry.
    """
    witness_gaps = 100.0 * witness_bias['delta_lb_pp'].abs().to_numpy(dtype=float)
    mine_gaps = 100.0 * adverse['delta_lb_pp'].abs().to_numpy(dtype=float)
    assert round(float(mine_gaps.max()), 2) != round(float(witness_gaps.max()), 2), (
        f"the maximum whiteness gap has returned to the witness value "
        f"{float(witness_gaps.max()):.2f} points; the D2 on that numeral must be withdrawn from "
        f"docs/DEVIATIONS.md `R08-campaign-redraw`.")
    # The mechanism the section states: the two campaigns place the maximum at
    # the same b, so the movement is a redraw of one cell and not a relocation
    # of the extremum.
    assert float(adverse['b'].iloc[int(np.argmax(mine_gaps))]) == float(
        witness_bias['b'].iloc[int(np.argmax(witness_gaps))])
    # Both remain inside the bound the body states, which is the qualitative
    # claim; only the numeral moves.
    assert float(mine_gaps.max()) <= V87_WHITENESS_BOUND_POINTS
    assert float(witness_gaps.max()) <= V87_WHITENESS_BOUND_POINTS


# =====================================================================
# REPORTING -- ASSERTS NOTHING
# =====================================================================

def test_R08_report_deviation_classification(adverse, null_law, witness_bias, witness_lattice,
                                             r07_lb_fpr, pairing, capsys):
    """Reporting only. The D0-D3 table, with the source cell of every value."""
    with capsys.disabled():
        above = null_law[null_law['lambda_units'] == ABOVE_UNITS].iloc[0]
        below = null_law[null_law['lambda_units'] == STAR_UNITS].iloc[0]
        extreme = adverse[adverse['b'] == max(B_GRID)].iloc[0]
        naive_zero = r07_lb_fpr[(r07_lb_fpr['arm'] == 'NAIVE')
                                & (r07_lb_fpr['phi'] == 0.0)].iloc[0]
        naive_two = r07_lb_fpr[(r07_lb_fpr['arm'] == 'NAIVE')
                               & (r07_lb_fpr['phi'] == 0.02)].iloc[0]
        bound = pairing[pairing['record_type'] == 'whiteness_bound'].iloc[0]
        rates = np.concatenate([adverse['lb_reject_biased'].to_numpy(dtype=float),
                                adverse['lb_reject_naive_ref'].to_numpy(dtype=float)])
        rows = [
            ('L241 level at lambda = 11.2', V87_LEVEL_ABOVE, float(above['P_exceed_strict']), 4,
             'R08_null_law_lattice.csv, lambda=11.2, P_exceed_strict'),
            ('L241 level at lambda = 11.4', V87_LEVEL_BELOW, float(below['P_exceed_strict']), 4,
             'R08_null_law_lattice.csv, lambda=11.4, P_exceed_strict'),
            ('L241 lambda*', V87_LAMBDA_STAR, float(below['lambda']), 1,
             'R08_null_law_lattice.csv, bracket_role=below_nominal'),
            ('Fig. 8 (B) FPR collapses to', V87_FPR_COLLAPSE, float(extreme['fpr_biased']), 4,
             'R08_adverse_bias.csv, b=0.15, fpr_biased'),
            ('Fig. 8 (B) FPR inflates to', V87_FPR_INFLATE, float(extreme['fpr_naive_ref']), 3,
             'R07_estmean_lb_fpr.csv, NAIVE, phi=0.15, fpr_concept'),
            ('L311 whiteness gap bound (points)', V87_WHITENESS_BOUND_POINTS,
             float(bound.observed), 1, 'R08_pairing_diagnostic.csv, whiteness_bound'),
            ('L311 penalty at momentum 0.02 (points)', V87_PENALTY_POINTS,
             100.0 * (float(naive_two['fpr_concept']) - float(naive_zero['fpr_concept'])), 1,
             'R07_estmean_lb_fpr.csv, NAIVE, phi in (0, 0.02)'),
            ('L311 whiteness range, low end', V87_RANGE_LOW, float(rates.min()), 2,
             'R08_adverse_bias.csv, min over both arms'),
            ('L311 whiteness range, high end', V87_RANGE_HIGH, float(rates.max()), 2,
             'R08_adverse_bias.csv, max over both arms'),
        ]
        print("\n  R08 deviation classification against v87, at the manuscript's printing "
              "precision")
        print(f"  {'site':<40}{'printed':>10}{'regenerated':>14}  degree  source cell")
        for site, printed, regenerated, decimals, cell in rows:
            if regenerated == printed:
                degree = 'D0'
            elif round(regenerated, decimals) == round(printed, decimals):
                degree = 'D1'
            else:
                degree = 'D2'
            print(f"  {site:<40}{printed:>10.4g}{regenerated:>14.6g}  {degree:<7} {cell}")
        print("  The witness is a record of the submitted campaign, not a target; see "
              "data/reference/README.md.")
        merged = adverse.merge(witness_bias, on='b', suffixes=('_new', '_witness'))
        for row in merged.itertuples(index=False):
            print(f"  witness [21c] b = {row.b:<6}: "
                  f"lb {row.lb_reject_biased_witness:.4f} -> {row.lb_reject_biased_new:.4f}, "
                  f"fpr {row.fpr_biased_witness:.4f} -> {row.fpr_biased_new:.4f}, "
                  f"naive lb {row.lb_reject_naive_ref_witness:.4f} -> "
                  f"{row.lb_reject_naive_ref_new:.4f}, naive fpr "
                  f"{row.fpr_naive_ref_witness:.4f} -> {row.fpr_naive_ref_new:.4f}")
        for position in range(len(witness_lattice)):
            row = witness_lattice.iloc[position]
            units = int(round(float(row['lambda']) / LATTICE_UNIT))
            mine = null_law[null_law['lambda_units'] == units].iloc[0]
            print(f"  witness [21d] lambda = {float(row['lambda']):<6.4g} ({units} units): "
                  f"P_exceed {float(row['P_exceed']):.6f} -> strict "
                  f"{float(mine['P_exceed_strict']):.6f}, weak "
                  f"{float(mine['P_exceed_weak']):.6f}, exact strict "
                  f"{float(mine['exact_level_strict']):.6f}")


def test_R08_report_the_operator_levels_and_the_boundary_counter(operator_levels, null_law,
                                                                 capsys):
    """Reporting only. Control C1: what each operator delivers, and where the
    float statistic sits relative to its exact lattice point."""
    with capsys.disabled():
        print("\n  R08 the level each comparison operator delivers (control C1)")
        print(f"  {'lambda':>8}{'units':>7}{'float M > l':>13}{'units > l':>12}{'units >= l':>12}"
              f"{'d(strict)':>11}{'d(weak)':>9}{'boundary':>10}")
        realised = operator_levels[operator_levels['record_type'] == 'realised_level']
        for units in sorted(set(realised['lambda_units'].astype(int))):
            cell = realised[realised['lambda_units'] == units]
            values = {row.operator: row for row in cell.itertuples(index=False)}
            float_row = values['float M > lambda']
            print(f"  {float(float_row.lambda_value):>8.4g}{units:>7}"
                  f"{float(float_row.realised_level):>13.6f}"
                  f"{float(values['exact M_units > lambda'].realised_level):>12.6f}"
                  f"{float(values['exact M_units >= lambda'].realised_level):>12.6f}"
                  f"{int(float_row.disagreements_vs_strict):>11}"
                  f"{int(float_row.disagreements_vs_weak):>9}"
                  f"{int(float_row.count_on_boundary):>10}")
        ulp = operator_levels[operator_levels['record_type'] == 'ulp_boundary'].iloc[0]
        print(f"  Float position against the exact lattice point over "
              f"{int(ulp['n_streams'])} streams: above {int(ulp['count_float_above'])}, "
              f"below {int(ulp['count_float_below'])}, exactly on "
              f"{int(ulp['count_float_equal'])}; within 4 ulp "
              f"{int(ulp['count_within_ulp_budget'])}.")
        star = null_law[null_law['lambda_units'] == STAR_UNITS].iloc[0]
        print(f"  The four exact levels L241's two thresholds carry: strict(11.2) = "
              f"{100.0 * float(null_law[null_law['lambda_units'] == ABOVE_UNITS]['exact_level_strict'].iloc[0]):.4f}%, "
              f"weak(11.2) = "
              f"{100.0 * float(null_law[null_law['lambda_units'] == ABOVE_UNITS]['exact_level_weak'].iloc[0]):.4f}%, "
              f"strict(11.4) = {100.0 * float(star['exact_level_strict']):.4f}%, weak(11.4) = "
              f"{100.0 * float(star['exact_level_weak']):.4f}%. The rule L241 states promises "
              f"'at or below nominal' and the operator the code implements delivers the last of "
              f"the four.")


def test_R08_report_the_pairing_diagnostic_and_the_control_nulls(pairing, adverse, capsys):
    """Reporting only. Controls C4, C5 and C6: the paired design, its design
    effects, and the null laws every extremum is read against."""
    with capsys.disabled():
        per_b = pairing[pairing['record_type'] == 'per_b']
        print("\n  R08 the paired design behind panels A and B (controls C4, C5, C6)")
        print(f"  {'b':>7}{'lb biased':>11}{'lb naive':>10}{'gap pt':>9}{'discord':>9}"
              f"{'rho_lb':>9}{'deff_lb':>9}{'fpr biased':>12}{'fpr naive':>11}{'rho_fpr':>9}")
        for row in per_b.itertuples(index=False):
            print(f"  {float(row.b):>7.3f}{float(row.lb_reject_biased):>11.4f}"
                  f"{float(row.lb_reject_naive):>10.4f}"
                  f"{100.0 * float(row.delta_lb_pp):>9.2f}{int(row.n_discordant_lb):>9}"
                  f"{float(row.rho_lb):>9.4f}{float(row.deff_lb):>9.4f}"
                  f"{float(row.fpr_biased):>12.4f}{float(row.fpr_naive):>11.4f}"
                  f"{float(row.rho_fpr):>9.4f}")
        print(f"  Family-wise arithmetic: gating on all {len(B_GRID)} proportion tests at "
              f"{LB_LEVEL:g} would trigger with probability "
              f"{1 - (1 - LB_LEVEL) ** len(B_GRID):.4%} under equality itself, which is why it "
              f"is not a gate.")
        rejecting = adverse[adverse['pval_lb'] < LB_LEVEL]
        print(f"  {len(rejecting)} of {len(adverse)} proportion tests reject: "
              f"{[(float(r.b), float(r.pval_lb)) for r in rejecting.itertuples(index=False)]}. "
              f"The Figure 8 caption's parenthetical is a statement of mechanism, symmetric by "
              f"construction; it is not contradicted by a difference in measured rate.")
        for row in pairing[pairing['record_type'] != 'per_b'].itertuples(index=False):
            print(f"  [{row.record_type}] {row.statistic}: observed {float(row.observed):.6f}"
                  + (f", tabulated p {float(row.tabulated_pvalue):.6f}"
                     if row.tabulated_pvalue == row.tabulated_pvalue else "")
                  + (f", null quantile {float(row.null_quantile):.6f}"
                     if row.null_quantile == row.null_quantile else "")
                  + (f", null p {float(row.null_p):.6f}"
                     if row.null_p == row.null_p else "")
                  + (f", 95% envelope [{float(row.ci_low):.4f}, {float(row.ci_high):.4f}]"
                     if row.ci_low == row.ci_low else "")
                  + f", {int(row.n_resample)} replicates")
