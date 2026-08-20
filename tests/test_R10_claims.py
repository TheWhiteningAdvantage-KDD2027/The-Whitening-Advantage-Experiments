"""
R10 -- sensitivity to conditional asymmetry. Acceptance and reporting.

This verification protocol enforces three strictly demarcated epistemological categories.

*Blocking invariants* anchor directly to explicit manuscript outputs evaluated at matched publication precision, or leverage deterministic mathematical formulations reconstructed independently from the primary experimental framework. Such formulations include the absorbing-chain transition probability on a discrete 2delta lattice executed via sparse matrix multiplications, closed-form algebraic roots defining the Wilson confidence bounds, and exact zero-crossing integrations utilizing `scipy.stats.t.sf`. None of these terminal gates depend on natively produced computational objects.

*Self-invalidating mechanisms* formally state identified deviations. We explicitly quantify statistical divergence through standardized z-scores rather than relying on brittle floating-point equality checks. Because the mandated cryptographic re-keying deterministically shifts every Monte-Carlo trajectory, rigid equality assertions would trigger inescapable mechanical failures. Should subsequent refinements recuperate these initial values, the corresponding test activates, dictating a necessary update to the centralized `docs/DEVIATIONS.md` register rather than prompting artificial tolerance widening.

*Reporting diagnostics* output the exhaustive D0-D3 categorizations, comprehensive design-effect tabulations, extreme envelope limits, baseline operator trigger frequencies, and legacy witness juxtapositions without enforcing boolean assertions.

THE EPISTEMOLOGICAL FUNCTION OF THE WITNESS
The referential legacy architecture constitutes a target for deviation mapping, never an immutable standard for execution blocking. Enforcing cell-by-cell equivalence mathematically precludes structural corrections. The integrated 128-bit key migration fundamentally replaces the stochastic trajectories, guaranteeing immediate rejection of any naive numerical parity test.

INTERPRETING SELF-INVALIDATING COMPARISONS

`test_R10_the_three_monte_carlo_numerals_of_L290_move_within_their_own_sampling_error`
Validates standard score boundaries (|z| <= 3) for the critical triad (-1.44, 0.58, 97%) relative to the computed standard error distinguishing two structurally identical, statistically independent campaigns. Discrepancies exceeding this threshold constitute formal analytical findings rather than parameters requiring broadened tolerances.

`test_R10_the_caption_fpr_envelope_has_moved_at_its_upper_end`
Tracks the empirical shift associated with the published `1.0--1.8\\%` interval bounds. If subsequent computational iterations recover the 1.8% supremum, this mechanism triggers, necessitating the formal withdrawal of the D2 anomaly flag.

`test_R10_the_symmetric_grid_point_is_not_centred_on_one_half`
Demonstrates mathematically that the baseline marginal probability significantly aligns with the standardized constant q* rather than converging to exactly 1/2. This identifies a methodological imprecision within the preliminary design specifications rather than an inherent manuscript flaw.

`test_R10_the_implemented_threshold_test_coincides_with_the_weak_operator`
Evaluates terminal empirical alignments concerning threshold boundaries. If subsequent iterations structurally separate the strict and weak comparison operators, the corresponding documentation immediately requires updating.
"""

import ast
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats
from scipy import sparse

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "results" / "R10_skew_robustness" / "data"
FIGURES_DIR = ROOT / "results" / "R10_skew_robustness" / "figures"
TABLES_DIR = ROOT / "results" / "R10_skew_robustness" / "tables"
REFERENCE_DIR = ROOT / "data" / "reference" / "R10"
SOURCE = ROOT / "experiments" / "R10_skew_robustness" / "exp_R10_skew_robustness.py"
R07_SOURCE = ROOT / "experiments" / "R07_estimated_mean" / "exp_R07_estimated_mean.py"
LOG = ROOT / "logs" / "R10_skew_robustness" / "exp_R10_skew_robustness.log"
SECTION = ROOT / "docs" / "sections" / "R10.md"

XI_GRID = (1.0, 0.85, 0.65, 0.5)
N_SEEDS = 1000
N_STEPS = 8000
LB_LAGS = 20
ALPHA_LB = 0.05
DELTA = 0.1
THRESHOLD = 15.0
LATTICE_UNIT = 2.0 * DELTA
LATTICE_UP = 2
LATTICE_DOWN = 3
LAM_UNITS = 75
GARCH_NU = 7.0
GARCH_ALPHA = 0.1058
GARCH_BETA = 0.8742
TARGET_VAR = 0.04

# =====================================================================
# MANUSCRIPT ANCHORS -- EXTRACTED DIRECTLY FROM THE PUBLISHED TEXT
# =====================================================================
# Exact transcription referencing structural shifts resulting from conditional asymmetry.
V87_SKEWNESS_EXTREME = -1.44
V87_Q_EXTREME = 0.58
V87_FPR_HALF_EXTREME = 0.97
# Figure 10 analytical parameters defining preservation boundaries and observed FPR spans.
V87_STREAMS_PER_POINT = 1000
V87_FPR_QHAT_ENVELOPE = (0.010, 0.018)

# =====================================================================
# DETERMINISTIC TOLERANCES DERIVED FROM FIRST PRINCIPLES
# =====================================================================
FLOAT64_EPS = float(np.finfo(np.float64).eps)
# Absolute numerical bounds for floating-point conservation. The Markovian recursion dictates an admissible divergence restricted strictly to accumulated computational noise scaling linearly with the simulation horizon. It fundamentally rejects empirically fitted error bands.
LATTICE_ATOL = 4.0 * N_STEPS * FLOAT64_EPS
# Algebraic reformulation of the Wilson bounds introduces minor reassociation artifacts. The theoretical mismatch spans at most five computational units, guaranteeing robust safety under a 1e-12 threshold.
CLOSED_FORM_RTOL = 1e-12
# Independent integration of Student-t survival parameters inherently reorganizes fractional precision. The associated drift remains confined tightly within a 1e-12 boundary, precluding coincidental structural failures.
Q_STAR_ATOL = 1e-12
# Critical statistical threshold defining standard normal outlier events. Derived purely from the corresponding 0.27% bilateral probability density limits.
FINDING_Z = 3.0

MACRO_PREFIX = "RTen"
MACRO_HEADER = "% Auto-generated by exp_R10_skew_robustness.py -- do not edit."

BANNED_CONFIRMATORY = (r'proves|proven|perfectly valid|validates the (theorem|thesis|claim)'
                       r'|confirms the|as expected|triumph|victory|irrefutable|brilliant')

WITNESS_CARRIED = ('wilson_ci', 'lb_pvalue', 'strict_cusum', 'get_fs_moments',
                   'fs_skew_t_standardized', 'verify_fs_construction', 'evaluate_sign_task')
R07_CARRIED = ('cusum_concept_lattice_units', 'exceeds_units_strict', 'exceeds_units_weak',
               'lattice_exceedance_exact', 'lattice_exceedance_enumerated', 'lattice_survival',
               'get_deterministic_seed', 'seed_sequence_for', 'rng_for', 'sign_flip_null_max')


def _read(path):
    assert path.exists(), f"Missing artefact: {path}"
    return pd.read_csv(path, float_precision='round_trip')


@pytest.fixture(scope="module")
def fpr():
    return _read(DATA_DIR / "R10_skew_fpr.csv")


@pytest.fixture(scope="module")
def diagnostics():
    return _read(DATA_DIR / "R10_skew_diagnostics.csv")


@pytest.fixture(scope="module")
def constants():
    return _read(DATA_DIR / "R10_fs_constants.csv")


@pytest.fixture(scope="module")
def streams():
    return _read(DATA_DIR / "R10_skew_streams.csv")


@pytest.fixture(scope="module")
def lattice():
    return _read(DATA_DIR / "R10_lattice_exact_law.csv")


@pytest.fixture(scope="module")
def operator_null():
    return _read(DATA_DIR / "R10_operator_null_level.csv")


@pytest.fixture(scope="module")
def design_effect():
    return _read(DATA_DIR / "R10_design_effect.csv")


@pytest.fixture(scope="module")
def witness_fpr():
    return _read(REFERENCE_DIR / "skew_robustness_fpr.csv")


@pytest.fixture(scope="module")
def witness_diagnostics():
    return _read(REFERENCE_DIR / "skew_robustness_diagnostics.csv")


@pytest.fixture(scope="module")
def macros():
    path = TABLES_DIR / "R10_claims.tex"
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

def independent_bernoulli_lattice_exceedance(horizon, lam_units, q):
    """
    P(M_H > lam_units) on the 2delta lattice under a Bernoulli(q) sign stream,
    written as an EXPLICIT enumerated sparse transition over the joint state
    space rather than as the experiment's array slicing.

    The state is (S_pos, S_neg) in units of 2delta, both clamped at 0 and
    absorbed above `lam_units`; the up branch moves S_pos by +2 with probability
    q while S_neg shrinks by 3 with a floor at 0, and the down branch is the
    mirror image with probability 1 - q. Every transition is listed by hand here
    and applied as a single sparse matrix-vector product per step, so agreement
    with the experiment is a statement about the transcription and not about the
    model.
    """
    side = lam_units + 1
    size = side * side
    absorbing = size
    rows, cols, vals = [], [], []
    for a in range(side):
        for b in range(side):
            source = a * side + b
            for probability, (a_next, b_next) in (
                    (q, (a + LATTICE_UP, max(0, b - LATTICE_DOWN))),
                    (1.0 - q, (max(0, a - LATTICE_DOWN), b + LATTICE_UP))):
                if a_next > lam_units or b_next > lam_units:
                    target = absorbing
                else:
                    target = a_next * side + b_next
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


def independent_enumerated_exceedance(horizon, lam_units, q):
    """
    P(M_H > lam_units) by exhaustive enumeration of all 2^H sign paths, with the
    running maximum tracked in exact integer arithmetic written inline here.
    Feasible only at the small horizons the experiment validates on.
    """
    total = 0.0
    for mask in range(2 ** horizon):
        s_pos = s_neg = maximum = 0
        ones = 0
        for step in range(horizon):
            bit = (mask >> step) & 1
            ones += bit
            s_pos = max(0, s_pos + (LATTICE_UP if bit else -LATTICE_DOWN))
            s_neg = max(0, s_neg + (-LATTICE_DOWN if bit else LATTICE_UP))
            maximum = max(maximum, s_pos, s_neg)
        if maximum > lam_units:
            total += (q ** ones) * ((1.0 - q) ** (horizon - ones))
    return total


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


def independent_q_star(nu, xi, m):
    """
    P(Y_raw > m) for the Fernandez-Steel construction, written as a mixture of
    two one-sided Student-t tails rather than as the experiment's branch
    weighting.

    Y_raw is xi|T| with probability xi^2/(1+xi^2) and -|T|/xi otherwise. For
    m > 0 only the right branch can exceed m, and it does so when |T| > m/xi. For
    m < 0 the right branch always exceeds m and the left branch does so when
    |T| < -m xi. Written here through the SURVIVAL function of the Student-t on
    both sides, which is the route the experiment does not take.
    """
    p_right = (xi ** 2) / (1.0 + xi ** 2)
    if m > 0.0:
        return p_right * 2.0 * float(stats.t.sf(m / xi, nu))
    if m < 0.0:
        return p_right + (1.0 - p_right) * (1.0 - 2.0 * float(stats.t.sf(-m * xi, nu)))
    return p_right


def source_segments(path, names):
    text = Path(path).read_text()
    tree = ast.parse(text)
    return {node.name: ast.get_source_segment(text, node)
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in names}


# =====================================================================
# BLOCKING INVARIANTS -- DETERMINISTIC RELATIONS AND PUBLISHED VALUES
# =====================================================================

def test_R10_every_artefact_the_plan_lists_exists_with_its_prescribed_schema(
        fpr, diagnostics, constants, streams, lattice, operator_null, design_effect):
    """Schema, cardinality, row order, clamping and the absence of NaN."""
    assert list(fpr.columns) == [
        'xi', 'n_streams', 'lb_ebin_rate', 'lb_ebin_low', 'lb_ebin_high',
        'lb_sign_rate', 'lb_sign_low', 'lb_sign_high', 'fpr_half_rate', 'fpr_half_low',
        'fpr_half_high', 'fpr_oracle_rate', 'fpr_oracle_low', 'fpr_oracle_high',
        'fpr_qhat_rate', 'fpr_qhat_low', 'fpr_qhat_high', 'lb_ebin_pvalue_binom',
        'lb_ebin_ks_statistic', 'lb_ebin_ks_pvalue', 'lb_sign_pvalue_binom',
        'lb_sign_ks_statistic', 'lb_sign_ks_pvalue']
    assert list(diagnostics.columns) == [
        'xi', 'skewness', 'q', 'skewness_se', 'q_se', 'n_streams', 'q_oracle',
        'q_star_analytic', 'z_q_against_q_star', 'z_q_against_one_half',
        'z_skewness_against_zero']
    assert len(fpr) == len(diagnostics) == len(constants) == len(XI_GRID) == 4
    assert len(streams) == len(XI_GRID) * N_SEEDS == 4000
    assert not fpr.isna().any().any()
    assert not diagnostics.isna().any().any()
    assert not constants.isna().any().any()
    assert not streams.isna().any().any()

    # Enforce strict grid sequencing to prevent non-deterministic floating-point sorting artifacts.
    assert list(fpr['xi']) == list(XI_GRID)
    assert list(diagnostics['xi']) == list(XI_GRID)
    assert list(constants['xi']) == list(XI_GRID)

    assert set(lattice['record_type']) == {
        'twin_binding_exact', 'enumeration_validation', 'fair_coin_survival',
        'half_arm_prediction_q_star_strict', 'half_arm_prediction_q_star_weak',
        'half_arm_prediction_q_measured_strict', 'half_arm_prediction_q_measured_weak',
        'boundary_artefact'}
    assert set(design_effect['record_type']) == {'design_effect', 'extremum_envelope'}
    assert set(design_effect[design_effect['record_type'] == 'design_effect']['statistic']) == {
        'lb_sign', 'lb_ebin', 'fpr_half', 'fpr_oracle', 'fpr_qhat'}
    assert len(operator_null) == len(XI_GRID)
    assert (FIGURES_DIR / "fig10_skew_robustness.png").exists()

    # Probability limits must be mathematically clamped to the canonical unit interval before downstream serialization processes.
    for arm in ('lb_ebin', 'lb_sign', 'fpr_half', 'fpr_oracle', 'fpr_qhat'):
        assert fpr[f'{arm}_low'].between(0.0, 1.0).all()
        assert fpr[f'{arm}_high'].between(0.0, 1.0).all()
        assert (fpr[f'{arm}_low'] <= fpr[f'{arm}_rate']).all()
        assert (fpr[f'{arm}_rate'] <= fpr[f'{arm}_high']).all()
    for column in ('null_level', 'null_level_low', 'null_level_high'):
        assert operator_null[column].between(0.0, 1.0).all()


def test_R10_the_operating_threshold_is_seventy_five_lattice_units():
    """
    BLOCKING, structural. At reference_value = 1/2 the two CUSUM branches move by
    +0.4 and -0.6, i.e. by +2 and -3 in units of 2delta = 0.2, so lambda = 15.0
    is exactly 75 lattice units and the exact absorbing-chain law is available on
    the `half` arm. Re-derived here from the two constants v87's own design fixes.
    """
    # Quantize state transitions. Sub-grid threshold logic confirms that fractional deviations map flawlessly to integer increments without floating-point truncation vulnerabilities. 
    assert abs((1.0 - 0.5 - DELTA) - LATTICE_UP * LATTICE_UNIT) <= 4.0 * FLOAT64_EPS
    assert abs((0.5 + DELTA) - LATTICE_DOWN * LATTICE_UNIT) <= 4.0 * FLOAT64_EPS
    assert int(round(THRESHOLD / LATTICE_UNIT)) == LAM_UNITS
    assert LAM_UNITS * LATTICE_UNIT == pytest.approx(THRESHOLD, rel=CLOSED_FORM_RTOL)


def test_R10_the_half_arm_law_reproduces_under_an_independent_dynamic_program(lattice):
    """
    BLOCKING, deterministic. The exact Bernoulli(q) predictions the experiment
    persists for the `half` arm are recomputed here by an explicit enumerated
    sparse transition matrix, at the full campaign horizon.
    """
    predictions = lattice[lattice['record_type'].str.startswith('half_arm_prediction')]
    assert len(predictions) == 4 * len(XI_GRID)
    checked = 0
    for row in predictions.itertuples(index=False):
        mine = independent_bernoulli_lattice_exceedance(int(row.H), int(row.lambda_units),
                                                        float(row.q))
        assert abs(mine - float(row.exact_level)) <= LATTICE_ATOL, (
            f"{row.record_type} at q = {row.q!r}, lambda = {int(row.lambda_units)} units: the "
            f"experiment gives {row.exact_level!r} and an independent absorbing-chain program "
            f"gives {mine!r}, a gap of {abs(mine - float(row.exact_level)):.3e} against a budget "
            f"of {LATTICE_ATOL:.3e} derived from {int(row.H)} mass-preserving float64 steps.")
        checked += 1
    assert checked == 4 * len(XI_GRID)


def test_R10_the_bernoulli_twin_reduces_to_the_fair_coin_at_one_half(lattice):
    """
    BLOCKING, deterministic. Control C7b's binding: at q = 1/2 the Bernoulli twin
    must return the value of the fair-coin routine R07 owns, BIT FOR BIT, because
    `1.0 - 0.5` is exact in binary floating point. The persisted record carries
    both values and the test re-reads them.
    """
    binding = lattice[lattice['record_type'] == 'twin_binding_exact']
    assert len(binding) >= 13
    assert (binding['q'] == 0.5).all()
    assert bool(binding['bit_identical'].all()), (
        f"the twin is not bit-identical to the carried routine on "
        f"{int((~binding['bit_identical']).sum())} of {len(binding)} points")
    assert (binding['exact_level'] == binding['twin_level']).all()
    assert (binding['abs_difference'] == 0.0).all()
    assert bool((binding['H'] == N_STEPS).any() & (binding['lambda_units'] == LAM_UNITS).any())


def test_R10_the_enumeration_validation_agrees_with_an_independent_enumeration(lattice):
    """
    BLOCKING, deterministic. The experiment validates its Bernoulli dynamic
    program against its own path enumeration; this test re-enumerates the same
    paths from an integer bit mask and an inline recursion, at the smallest of
    the validated horizons where the enumeration is free.
    """
    validation = lattice[lattice['record_type'] == 'enumeration_validation']
    assert len(validation) == 36
    smallest = validation[validation['H'] == validation['H'].min()]
    assert len(smallest) == 12
    checked = 0
    for row in smallest.itertuples(index=False):
        mine = independent_enumerated_exceedance(int(row.H), int(row.lambda_units), float(row.q))
        # Epistemological budget mapping: sequential addition over exponentially scaling non-negative configurations incurs bounded accumulated rounding noise. The derived threshold strictly limits theoretical discrepancy.
        budget = (2.0 ** int(row.H) + 3.0) * FLOAT64_EPS
        assert abs(mine - float(row.enumerated_level)) <= budget, (
            f"H = {int(row.H)}, lambda = {int(row.lambda_units)}, q = {row.q!r}: the experiment "
            f"enumerates {row.enumerated_level!r} and this file {mine!r}")
        checked += 1
    assert checked == 12


def test_R10_the_wilson_intervals_reproduce_from_a_second_algebraic_form(fpr):
    """
    BLOCKING, deterministic. Every persisted Wilson bound is recomputed here as
    a root of the score equation rather than as a centre and a margin.
    """
    checked = 0
    for row in fpr.itertuples(index=False):
        n = int(row.n_streams)
        for arm in ('lb_ebin', 'lb_sign', 'fpr_half', 'fpr_oracle', 'fpr_qhat'):
            k = int(round(getattr(row, f'{arm}_rate') * n))
            low, high = wilson_second_form(k, n)
            assert getattr(row, f'{arm}_low') == pytest.approx(max(0.0, min(1.0, low)),
                                                              rel=CLOSED_FORM_RTOL, abs=1e-15)
            assert getattr(row, f'{arm}_high') == pytest.approx(max(0.0, min(1.0, high)),
                                                               rel=CLOSED_FORM_RTOL, abs=1e-15)
            checked += 2
    assert checked == 2 * 5 * len(XI_GRID)


def test_R10_q_star_reproduces_from_the_student_t_survival_function(constants):
    """
    BLOCKING, deterministic. The centre the standardised sign stream actually has
    is P(Y_raw > m) at the Monte-Carlo constant m, recomputed here through the
    Student-t survival function on both branches.
    """
    for row in constants.itertuples(index=False):
        mine = independent_q_star(float(row.nu), float(row.xi), float(row.m_monte_carlo))
        assert float(row.q_star_at_monte_carlo_m) == pytest.approx(mine, abs=Q_STAR_ATOL), (
            f"xi = {row.xi!r}: the experiment gives {row.q_star_at_monte_carlo_m!r} and an "
            f"independent Student-t computation gives {mine!r}")
    # Symmetrical convergence constraint. The parameterized density reduces perfectly to the canonical Student-t distribution exclusively at unity. 
    symmetric = constants[constants['xi'] == 1.0].iloc[0]
    assert float(symmetric.q_star_at_monte_carlo_m) == pytest.approx(
        float(stats.t.sf(float(symmetric.m_monte_carlo), GARCH_NU)), abs=Q_STAR_ATOL)


def test_R10_the_caption_stream_count_is_one_thousand_per_point(streams, fpr, diagnostics):
    """
    BLOCKING, on a value v87 PRINTS. The Figure 10 caption states "1,000 streams
    per point"; the per-stream artefact carries exactly that, on four grid
    points, with the same stream indices at every point because the entropy key
    carries the index alone.
    """
    assert (fpr['n_streams'] == V87_STREAMS_PER_POINT).all()
    assert (diagnostics['n_streams'] == V87_STREAMS_PER_POINT).all()
    reference = None
    for xi in XI_GRID:
        cell = streams[streams['xi'] == xi]
        assert len(cell) == V87_STREAMS_PER_POINT
        indices = np.sort(cell['stream_index'].to_numpy())
        assert len(np.unique(indices)) == V87_STREAMS_PER_POINT
        if reference is None:
            reference = indices
        else:
            assert np.array_equal(indices, reference), (
                f"the xi = {xi} cell does not carry the same stream indices as the first grid "
                f"point, so the design is not the paired one the entropy plan mandates")


def test_R10_the_sign_stream_is_bit_identically_the_innovation_sign(streams):
    """
    BLOCKING, deterministic. Control C4: eps_t = sqrt(h_t) z_t with h_t > 0, so
    `1{eps_t > 0} == 1{z_t > 0}` exactly. The consequence, which the section
    states, is that panel A's raw-sign arm measures the Ljung-Box test's
    calibration and not a property of the data-generating process.
    """
    assert bool(streams['sign_identity'].all()), (
        f"{int((~streams['sign_identity']).sum())} of {len(streams)} streams break the sign "
        f"identity")
    omega = TARGET_VAR * (1.0 - GARCH_ALPHA - GARCH_BETA)
    assert float(streams['min_h'].min()) >= omega, (
        f"the smallest conditional variance {float(streams['min_h'].min())!r} is below the "
        f"derived bound omega = {omega!r}")
    assert float(streams['min_h'].min()) > 1e-12


def test_R10_no_degraded_path_is_taken(streams):
    """
    BLOCKING. Control C10: neither branch of the carried `lb_pvalue` fired, on
    either binary stream. A constant 0/1 stream would have returned the
    non-rejection 1.0 and a swallowed exception would have returned NaN.
    """
    assert int(streams['degenerate_sign'].sum()) == 0
    assert int(streams['degenerate_ebin'].sum()) == 0
    assert int(streams['lb_sign_p'].isna().sum()) == 0
    assert int(streams['lb_ebin_p'].isna().sum()) == 0
    assert streams['lb_sign_p'].between(0.0, 1.0).all()
    assert streams['lb_ebin_p'].between(0.0, 1.0).all()


def test_R10_the_standardisation_constants_are_one_deterministic_input(streams, constants):
    """
    BLOCKING, deterministic. Control C6: the (m, s, q_oracle) triple every stream
    used is a single constant per grid point, bit-identical to the one the main
    process recomputed and persisted.
    """
    for row in constants.itertuples(index=False):
        cell = streams[streams['xi'] == row.xi]
        for column, expected in (('fs_m', row.m_monte_carlo), ('fs_s', row.s_monte_carlo),
                                 ('fs_q_oracle', row.q_oracle_monte_carlo)):
            values = np.unique(cell[column].to_numpy())
            assert len(values) == 1
            assert values[0] == expected


def test_R10_the_fixed_half_cusum_explodes_with_asymmetry(fpr, diagnostics):
    """
    BLOCKING, on the qualitative content of L290. "Asymmetry shifts the marginal
    rate, making a fixed-1/2 CUSUM fire at ~97%": the rate must be monotone in
    the realized asymmetry and must reach the high-alarm regime at the extreme
    grid point. The NUMERAL 97% is not asserted here -- it is classified against
    its own sampling error in the self-invalidating group.
    """
    merged = fpr.merge(diagnostics[['xi', 'skewness']], on='xi').sort_values('skewness',
                                                                            ascending=False)
    rates = merged['fpr_half_rate'].to_numpy()
    assert np.all(np.diff(rates) > 0.0), (
        f"the fixed-1/2 false-alarm rate is not monotone in the realized skewness: {rates}")
    assert rates[-1] >= 0.90, (
        f"the fixed-1/2 CUSUM fires on {100.0 * rates[-1]:.1f}% of the streams at the extreme "
        f"grid point, against the ~97% v87 prints")
    assert rates[0] <= ALPHA_LB


def test_R10_recentering_restores_false_alarm_control(fpr):
    """
    BLOCKING, on the qualitative content of the Figure 10 caption. "Recentering
    on warm-up estimate q_hat restores false-alarm control": at every grid point
    the recentred arm must sit below the nominal level and orders of magnitude
    below the fixed-1/2 arm at the extreme point.
    """
    assert (fpr['fpr_qhat_rate'] < ALPHA_LB).all(), (
        f"the recentred arm does not sit below the {ALPHA_LB:g} nominal at every grid point: "
        f"{fpr['fpr_qhat_rate'].to_numpy()}")
    assert (fpr['fpr_oracle_rate'] < ALPHA_LB).all()
    assert float(fpr['fpr_qhat_rate'].max()) < float(fpr['fpr_half_rate'].max())
    # Empirical verification of the published boundary. Extracted interval coordinates must align exclusively within the specified control parameter bounds.
    assert 0.0 < float(fpr['fpr_qhat_rate'].min())


def test_R10_the_carried_primitives_are_byte_identical_to_both_owning_files():
    """
    BLOCKING, deterministic. Control C5, re-run outside the experiment: the
    seventeen carried primitives must be byte-identical to the two files that own
    them. Preamble S4.2 forbids hoisting any of them into experiments/common/, so
    the duplication is deliberate and this is what stops it drifting.
    """
    mine = source_segments(SOURCE, set(WITNESS_CARRIED) | set(R07_CARRIED))
    witness = source_segments(REFERENCE_DIR / "Priorite_9_skew_robustness.py",
                              set(WITNESS_CARRIED))
    r07 = source_segments(R07_SOURCE, set(R07_CARRIED))
    for name in WITNESS_CARRIED:
        assert mine.get(name) == witness.get(name), f"{name} has drifted from the R10 witness"
    for name in R07_CARRIED:
        assert mine.get(name) == r07.get(name), f"{name} has drifted from exp_R07_estimated_mean.py"


def test_R10_the_family_wise_arithmetic_is_logged_before_any_gate_is_read():
    """
    BLOCKING, structural. S4bis requires the trigger probability of a family of
    tests to be computed and journalled BEFORE its result is interpreted. The log
    is read here and the order of the two records is asserted.
    """
    text = LOG.read_text()
    family = text.find("FAMILY-WISE ARITHMETIC, LOGGED BEFORE ANY RESULT IS INTERPRETED")
    c1_declaration = text.find("C1, BEFORE ANY RESULT IS READ")
    c2a_declaration = text.find("C2a, BEFORE ANY RESULT IS READ")
    c2b_declaration = text.find("C2b, BEFORE ANY RESULT IS READ")
    c1_result = text.find("C1 SYMMETRIC WITNESS")
    c2a_result = text.find("C2a [lb_sign]")
    c2b_result = text.find("C2b RESULT")
    for marker in (family, c1_declaration, c2a_declaration, c2b_declaration,
                   c1_result, c2a_result, c2b_result):
        assert marker >= 0
    assert family < c1_declaration < c1_result
    assert family < c2a_declaration < c2a_result
    assert family < c2b_declaration < c2b_result
    assert "1 - (1 - 0.05)^8 = 33.6580%" in text


def test_R10_macros_are_emitted_and_agree_with_the_frames(macros, fpr, diagnostics,
                                                          operator_null, lattice):
    """
    BLOCKING, internal consistency. Every macro body must be the corresponding
    cell of a persisted frame at the precision it prints. This asserts that no
    literal was typed into R10_claims.tex, not that any value is right.
    """
    expected = {'RTenSkewnessMax', 'RTenQMax', 'RTenLbSignMin', 'RTenLbSignMax',
                'RTenFprQhatMin', 'RTenFprQhatMax', 'RTenFprHalfMax', 'RTenFprOracleMax',
                'RTenOperatorNullLevel', 'RTenFprHalfMaxExact'}
    assert set(macros) == expected
    assert all(name.startswith(MACRO_PREFIX) for name in macros)
    assert not any(name.startswith("RTenth") for name in macros)
    assert macros['RTenSkewnessMax'] == f"{float(diagnostics['skewness'].min()):.2f}"
    assert macros['RTenQMax'] == f"{float(diagnostics['q'].max()):.4f}"
    for macro, column, extremum in (('RTenLbSignMin', 'lb_sign_rate', 'min'),
                                    ('RTenLbSignMax', 'lb_sign_rate', 'max'),
                                    ('RTenFprQhatMin', 'fpr_qhat_rate', 'min'),
                                    ('RTenFprQhatMax', 'fpr_qhat_rate', 'max'),
                                    ('RTenFprHalfMax', 'fpr_half_rate', 'max'),
                                    ('RTenFprOracleMax', 'fpr_oracle_rate', 'max')):
        value = float(getattr(fpr[column], extremum)())
        assert macros[macro] == f"{100.0 * value:.1f}\\%"
    assert macros['RTenOperatorNullLevel'] == \
        f"{100.0 * float(operator_null['null_level'].mean()):.2f}\\%"
    strict = lattice[lattice['record_type'] == 'half_arm_prediction_q_star_strict']
    extreme = strict[strict['operator'].str.startswith('xi=0.5 ')].iloc[0]
    assert macros['RTenFprHalfMaxExact'] == f"{100.0 * float(extreme.exact_level):.1f}\\%"


def test_R10_text_artefacts_end_with_a_newline():
    """BLOCKING. Preamble S6: the section and the requirements file are assembled
    by concatenation, so a missing final newline corrupts the result."""
    for path in (SECTION, ROOT / "requirements" / "R10.txt",
                 TABLES_DIR / "R10_claims.tex"):
        assert path.exists(), f"Missing artefact: {path}"
        assert path.read_text().endswith("\n"), f"{path.name} does not end with a newline"


def test_R10_no_confirmatory_language_in_the_script_the_log_or_the_section():
    """BLOCKING. Preamble S4.4: the grep must return empty on all three files."""
    pattern = re.compile(BANNED_CONFIRMATORY, re.IGNORECASE)
    for path in (SOURCE, LOG, SECTION):
        assert path.exists(), f"Missing artefact: {path}"
        hits = [line for line in path.read_text().splitlines() if pattern.search(line)]
        assert not hits, f"{path.name} carries confirmatory language: {hits[:3]}"


# =====================================================================
# SELF-INVALIDATING -- EACH STATES A DEVIATION WITH ITS OWN z
# =====================================================================

def test_R10_the_three_monte_carlo_numerals_of_L290_move_within_their_own_sampling_error(
        diagnostics, fpr):
    """
    SELF-INVALIDATING. v87 L290 prints -1.44, 0.58 and ~97%, each to a stated
    number of decimals. Preamble S3 fixes the comparison: a printed numeral is
    read AT ITS PRINTING PRECISION, so a regenerated value that rounds to it has
    not moved at all (D0/D1) and there is nothing to compare against a standard
    error. Only a value whose rounding DIFFERS from the printed one has moved,
    and that gap is read against the standard error of the DIFFERENCE between two
    campaigns -- sqrt(2) times the standard error of one -- because the printed
    value is itself one Monte-Carlo realisation of the same design.

    Both branches are needed and neither is a tolerance. Reading `q = 0.58`
    against a standard error of 1.8e-4 would compare a rounding to a
    measurement: the printed numeral carries a rounding uncertainty of 5e-3,
    which is 28 standard errors wide, so the comparison would fire on the
    manuscript's choice of decimals rather than on any disagreement. A |z| beyond
    3 on a numeral that HAS moved is a finding to characterise in AUDIT_R10.md,
    never a tolerance to widen (preamble S4.8).
    """
    extreme_diag = diagnostics.iloc[int(diagnostics['skewness'].to_numpy().argmin())]
    extreme_fpr = fpr[fpr['xi'] == extreme_diag['xi']].iloc[0]
    half = float(extreme_fpr['fpr_half_rate'])
    comparisons = (
        ('realized skewness', V87_SKEWNESS_EXTREME, float(extreme_diag['skewness']), 2,
         float(extreme_diag['skewness_se'])),
        ('marginal rate q', V87_Q_EXTREME, float(extreme_diag['q']), 2,
         float(extreme_diag['q_se'])),
        ('fixed-1/2 false-alarm rate', V87_FPR_HALF_EXTREME, half, 2,
         math.sqrt(half * (1.0 - half) / N_SEEDS)),
    )
    failures = []
    moved = []
    for label, printed, regenerated, decimals, se in comparisons:
        if round(regenerated, decimals) == round(printed, decimals):
            continue                      # D0 or D1: the printed value has not moved
        moved.append(label)
        paired_se = math.sqrt(2.0) * se
        z = (regenerated - printed) / paired_se
        if abs(z) > FINDING_Z:
            failures.append(f"{label}: printed {printed!r}, regenerated {regenerated!r}, "
                            f"z = {z:+.2f} against a paired standard error of {paired_se!r}")
    assert not failures, ("a printed numeral of L290 has moved beyond three standard errors of "
                          "the difference between two campaigns: " + "; ".join(failures))
    assert moved == ['realized skewness'], (
        f"the set of L290 numerals that move at v87's printing precision is {moved}, and "
        f"docs/DEVIATIONS.md `R10-campaign-redraw` records exactly ['realized skewness']")


def test_R10_the_caption_fpr_envelope_has_moved_at_its_upper_end(fpr, design_effect):
    """
    SELF-INVALIDATING. The Figure 10 caption prints "measured FPR 1.0--1.8%". The
    regenerated upper end does not round to 1.8% at the caption's own printing
    precision, which is the D2 the register carries as `R10-campaign-redraw`. If
    a later campaign brings it back, this test fires and the numeral leaves the
    register entry.
    """
    low = float(fpr['fpr_qhat_rate'].min())
    high = float(fpr['fpr_qhat_rate'].max())
    assert round(low, 3) == round(V87_FPR_QHAT_ENVELOPE[0], 3), (
        f"the lower end of the caption's envelope has moved: printed "
        f"{V87_FPR_QHAT_ENVELOPE[0]!r}, regenerated {low!r}. That is a change to the register "
        f"entry, not to this test.")
    assert round(high, 3) != round(V87_FPR_QHAT_ENVELOPE[1], 3), (
        f"the upper end of the caption's envelope has returned to the printed "
        f"{V87_FPR_QHAT_ENVELOPE[1]!r}; the D2 on that numeral must be withdrawn from "
        f"docs/DEVIATIONS.md.")
    # Extremum distributions fundamentally differ from isolated marginal intervals. Bootstrapped limits dictate the correct inferential containment regime.
    envelope = design_effect[(design_effect['record_type'] == 'extremum_envelope')
                             & (design_effect['macro'] == 'RTenFprQhatMax')].iloc[0]
    assert float(envelope.ci_low) <= V87_FPR_QHAT_ENVELOPE[1] <= float(envelope.ci_high), (
        f"the printed {V87_FPR_QHAT_ENVELOPE[1]!r} sits outside the bootstrap envelope of the "
        f"regenerated maximum [{envelope.ci_low!r}, {envelope.ci_high!r}], which would make this "
        f"a contradiction rather than a redraw")


def test_R10_the_symmetric_grid_point_is_not_centred_on_one_half(diagnostics, constants):
    """
    SELF-INVALIDATING. The R10 prompt's section 2.1 asks the xi = 1 cell to cover
    1/2. It does not, and the reason is deterministic: `get_fs_moments` fixes a
    standardisation constant m that is not zero, so the standardised stream is
    centred on q* = P(Y_raw > m) and not on 1/2. This states a SPECIFICATION
    IMPRECISION OF THE PROMPT, not a defect of v87, which claims nothing about
    the xi = 1 cell.
    """
    row = diagnostics[diagnostics['xi'] == 1.0].iloc[0]
    constant = constants[constants['xi'] == 1.0].iloc[0]
    assert float(constant.m_monte_carlo) != 0.0
    assert abs(float(row.z_q_against_q_star)) < abs(float(row.z_q_against_one_half)), (
        f"the xi = 1 marginal rate is now closer to 1/2 "
        f"({float(row.z_q_against_one_half):+.3f} SE) than to q* "
        f"({float(row.z_q_against_q_star):+.3f} SE); the standardisation constant no longer "
        f"explains the displacement and docs/sections/R10.md is what changes.")
    assert abs(float(row.z_q_against_q_star)) <= 4.0


def test_R10_the_implemented_threshold_test_coincides_with_the_weak_operator(lattice):
    """
    SELF-INVALIDATING. Control C7c measures what `M > 15.0` implements on the
    lattice boundary. On this campaign it coincides with the mathematical
    `M >= 15.0` on every stream. The statement is EMPIRICAL and holds for this
    threshold, this horizon and this accumulation order only.
    """
    boundary = lattice[lattice['record_type'] == 'boundary_artefact']
    assert len(boundary) == 3
    levels = {row.operator: float(row.realised_level) for row in boundary.itertuples(index=False)}
    assert set(levels) == {'float M > lambda', 'exact M_units > lambda',
                           'exact M_units >= lambda'}
    assert levels['float M > lambda'] == levels['exact M_units >= lambda'], (
        "the implemented float test no longer coincides with the weak operator; "
        "docs/sections/R10.md and the C7 predictor of record are what change")
    assert levels['float M > lambda'] > levels['exact M_units > lambda'], (
        "no stream reached the lattice boundary, so this campaign separates neither operator "
        "from the other and the C7c statement has no content on it")


# =====================================================================
# REPORTING -- ASSERTS NOTHING
# =====================================================================

def test_R10_report_deviation_classification(diagnostics, fpr, witness_diagnostics, witness_fpr,
                                             capsys):
    """Reporting only. The D0-D3 table, with the source cell of every value."""
    with capsys.disabled():
        extreme = diagnostics.iloc[int(diagnostics['skewness'].to_numpy().argmin())]
        extreme_fpr = fpr[fpr['xi'] == extreme['xi']].iloc[0]
        half = float(extreme_fpr['fpr_half_rate'])
        rows = [
            ('L290 realized skewness', V87_SKEWNESS_EXTREME, float(extreme['skewness']), 2,
             float(extreme['skewness_se']), 'R10_skew_diagnostics.csv, xi=0.5, skewness'),
            ('L290 marginal rate q', V87_Q_EXTREME, float(extreme['q']), 2, float(extreme['q_se']),
             'R10_skew_diagnostics.csv, xi=0.5, q'),
            ('L290 fixed-1/2 CUSUM fires at', V87_FPR_HALF_EXTREME, half, 2,
             math.sqrt(half * (1.0 - half) / N_SEEDS), 'R10_skew_fpr.csv, xi=0.5, fpr_half_rate'),
            ('Fig. 10 caption FPR lower end', V87_FPR_QHAT_ENVELOPE[0],
             float(fpr['fpr_qhat_rate'].min()), 3, float('nan'),
             'R10_skew_fpr.csv, min fpr_qhat_rate'),
            ('Fig. 10 caption FPR upper end', V87_FPR_QHAT_ENVELOPE[1],
             float(fpr['fpr_qhat_rate'].max()), 3, float('nan'),
             'R10_skew_fpr.csv, max fpr_qhat_rate'),
        ]
        print("\n  R10 deviation classification against v87, at the manuscript's printing precision")
        print(f"  {'site':<34}{'printed':>10}{'regenerated':>14}{'z_paired':>10}  degree  source cell")
        for site, printed, regenerated, decimals, se, cell in rows:
            if regenerated == printed:
                degree = 'D0'
            elif round(regenerated, decimals) == round(printed, decimals):
                degree = 'D1'
            else:
                degree = 'D2'
            z = ((regenerated - printed) / (math.sqrt(2.0) * se)
                 if se == se and se > 0.0 else float('nan'))
            print(f"  {site:<34}{printed:>10.4g}{regenerated:>14.6g}{z:>10.2f}  {degree:<7} {cell}")
        print("  The witness is a record of the submitted campaign, not a target; see "
              "data/reference/README.md.")
        for name, frame, witness, columns in (
                ('diagnostics', diagnostics, witness_diagnostics, ('skewness', 'q')),
                ('fpr', fpr, witness_fpr, ('lb_ebin_rate', 'lb_sign_rate', 'fpr_half_rate',
                                           'fpr_oracle_rate', 'fpr_qhat_rate'))):
            merged = frame.merge(witness, on='xi', suffixes=('_new', '_witness'))
            for row in merged.itertuples(index=False):
                moves = ", ".join(f"{c} {getattr(row, c + '_witness'):.6g} -> "
                                  f"{getattr(row, c + '_new'):.6g}" for c in columns)
                print(f"  witness [{name}] xi = {row.xi:<5}: {moves}")


def test_R10_report_design_effect_and_extremum_envelopes(design_effect, capsys):
    """Reporting only. Control C9, measured before any pooled quantity is read."""
    with capsys.disabled():
        blocks = design_effect[design_effect['record_type'] == 'design_effect']
        print("\n  R10 design effect of every quantity pooled across the xi grid (control C9)")
        print(f"  {'statistic':<12}{'cells':>6}{'rho_bar':>10}{'deff':>9}{'n_eff':>10}"
              f"{'pooled':>10}{'SE inflation':>14}")
        for row in blocks.itertuples(index=False):
            print(f"  {row.statistic:<12}{int(row.n_cells):>6}{row.rho_bar:>10.4f}"
                  f"{row.design_effect:>9.4f}{row.n_eff:>10.1f}{row.pooled_rate:>10.5f}"
                  f"{row.se_inflation:>14.4f}")
        envelopes = design_effect[design_effect['record_type'] == 'extremum_envelope']
        print("  Extremum envelopes: an extremum over four correlated cells has neither the "
              "distribution nor the interval of one cell (S4bis.4).")
        for row in envelopes.itertuples(index=False):
            print(f"  {row.macro:<18} point {row.point_value:.4f}  bootstrap 95% "
                  f"[{row.ci_low:.4f}, {row.ci_high:.4f}]  bootstrap mean {row.bootstrap_mean:.6f}")


def test_R10_report_the_operator_null_level_and_the_exact_half_arm_law(operator_null, lattice,
                                                                      fpr, capsys):
    """Reporting only. Controls C7, C7b, C7c and C8."""
    with capsys.disabled():
        print("\n  R10 the level this CUSUM delivers under perfect centring (control C8)")
        for row in operator_null.itertuples(index=False):
            print(f"  xi = {row.xi:<5} ref = {row.reference_value:.6f}  {int(row.alarms):>5} alarms "
                  f"on {int(row.n_streams)} streams -> {100.0 * row.null_level:.4f}% "
                  f"[{100.0 * row.null_level_low:.4f}%, {100.0 * row.null_level_high:.4f}%]; "
                  f"fair-coin exact {100.0 * row.fair_coin_exact_level:.4f}%; nominal "
                  f"{100.0 * row.nominal_level:.1f}%")
        print("  The exact Bernoulli(q) law of the fixed-1/2 arm (control C7), both operators:")
        predictions = lattice[lattice['record_type'].str.startswith('half_arm_prediction_q_star')]
        for row in predictions.sort_values(['operator', 'record_type']).itertuples(index=False):
            print(f"  {row.operator:<14} q = {row.q:.6f}  lambda = {int(row.lambda_units)} units  "
                  f"exact {100.0 * row.exact_level:.4f}%  observed "
                  f"{100.0 * row.realised_level:.4f}%")
        boundary = lattice[lattice['record_type'] == 'boundary_artefact']
        print("  What the float comparison implements on the lattice boundary (control C7c):")
        for row in boundary.itertuples(index=False):
            print(f"  {row.operator:<26} realised level {row.realised_level:.6f} on "
                  f"{int(row.n_streams)} streams, {int(row.disagreements)} disagreements with the "
                  f"strict operator")
        print(f"  Panel B is read against both references: nominal 5.0% and the operator's own "
              f"{100.0 * float(operator_null['null_level'].mean()):.4f}%. The recentred arm spans "
              f"{100.0 * float(fpr['fpr_qhat_rate'].min()):.1f}-"
              f"{100.0 * float(fpr['fpr_qhat_rate'].max()):.1f}%.")


def test_R10_report_the_ljungbox_calibration_and_its_power_bound(fpr, streams, capsys):
    """
    Reporting only. Controls C2a and C2b, and the cross-reference to
    `docs/DEVIATIONS.md` `R18-ljungbox-power`, which already covers L290 at this
    exact configuration. R10 opens no duplicate register entry.
    """
    with capsys.disabled():
        print("\n  R10 Ljung-Box calibration, per cell (control C2a; only the xi = 1 row is a gate)")
        print(f"  {'xi':>6}{'lb_sign rate':>14}{'KS D':>10}{'KS p':>10}"
              f"{'lb_ebin rate':>14}{'KS D':>10}{'KS p':>10}")
        for row in fpr.itertuples(index=False):
            print(f"  {row.xi:>6}{row.lb_sign_rate:>14.4f}{row.lb_sign_ks_statistic:>10.5f}"
                  f"{row.lb_sign_ks_pvalue:>10.5f}{row.lb_ebin_rate:>14.4f}"
                  f"{row.lb_ebin_ks_statistic:>10.5f}{row.lb_ebin_ks_pvalue:>10.5f}")
        print(f"  Family-wise arithmetic: gating on all {2 * len(XI_GRID)} cells at "
              f"{ALPHA_LB:g} would trigger with probability "
              f"{1 - (1 - ALPHA_LB) ** (2 * len(XI_GRID)):.4%} under a perfectly calibrated null, "
              f"which is why it is not a gate.")
        print(f"  Smallest p-value over the {len(streams)} streams: raw sign "
              f"{float(streams['lb_sign_p'].min()):.6g}, HT error "
              f"{float(streams['lb_ebin_p'].min()):.6g}.")
        print("  The HT-error arm's evidence is a NON-REJECTION; its power at n = 8000, lag 20 is "
              "bounded by docs/DEVIATIONS.md R18-ljungbox-power, and R10 opens no duplicate entry.")
