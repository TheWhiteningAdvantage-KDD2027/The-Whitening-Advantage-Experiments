"""
R17 -- estimation cost of the parametric route. Acceptance and reporting.

Two kinds of statement live in this file and they are kept apart deliberately.

*Blocking assertions* rest either on a value v87 PRINTS, compared at v87's own
printing precision, which is what preamble S3 fixes as the classification rule,
or on a deterministic relation reimplemented here independently of the
experiment -- the GARCH penalty recomputed from the autocorrelation series of
`eps^2` rather than from the closed form the experiment carries, the Wilson
interval written from a second algebraic form, the source identity of the
carried primitives extracted by a second `ast` pass, the differential identity
of the three adapted routines re-derived by a second redaction -- or on a
DISCRETE quantity: a count, a flag, a grid coordinate. NONE rests on a
continuous value R17 produced.

WHY THE WITNESS IS NOT A BLOCKING ANCHOR ON EITHER ARM. `data/reference/
README.md` states it outright: a witness value is the "published value" column
of a D0-D3 comparison, never the anchor of a blocking assertion. R17's position
is stronger than R14's on this point, because the entropy migration redraws BOTH
arms here: `--qmle-options legacy` restores the delivered optimiser call and
nothing else, so it shares no seed with the submitted campaign and reproduces no
Monte-Carlo cell of it. What the legacy arm anchors is therefore the DETERMINISTIC
witness content -- the `Gamma` grid the bisection produces -- and the
attribution: whatever separates the two arms is SPECS 1.10 and nothing else,
because they run on a common draw.

THE SELF-INVALIDATING ASSERTIONS, one per registered deviation.

`test_R17_the_four_numerals_of_L341_do_not_reproduce_at_their_printed_precision`
asserts the deviation `R17-campaign-redraw` itself. If a later campaign brings
any of the four back to its printed value, it fires, and what must then change is
`docs/DEVIATIONS.md` -- the entry is withdrawn -- never this assertion.

`test_R17_the_sign_stream_is_bit_identical_across_the_leverage_axis` asserts the
deviation `R17-sign-arm-crn-degeneracy`. If a later change to `simulate_gjr11`
or to the entropy key breaks the identity, it fires.

`test_R17_the_published_cell_carries_corner_solutions_the_convergence_flag_does_
not_see` asserts the defect the audit records: at the cell L341 publishes, the
delivered flag reports zero non-convergence while a fifth of the fits sit on the
optimiser's lower bound.
"""

import ast
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results" / "R17_econometric_baseline"
DATA_DIR = RESULTS_DIR / "data"
TABLES_DIR = RESULTS_DIR / "tables"
REFERENCE_DIR = ROOT / "data" / "reference" / "R17"
EXPERIMENT = ROOT / "experiments" / "R17_econometric_baseline" / "exp_R17_econometric_baseline.py"
WITNESS_SCRIPT = REFERENCE_DIR / "Priorite_6_econometric_baseline.py"
R13_SCRIPT = ROOT / "experiments" / "R13_oracle_ceiling" / "exp_R13_oracle_ceiling_a.py"

# The imperative grids, traced to the delivered script and cross-checked against
# the witness CSVs. `protocol_3c` forces `n_streams = 1000` at its line 331 and
# `__main__` passes `n_str = 200` to `protocol_3d_warmup_sensitivity` at its line
# 515; the R17 prompt section 1 has those two counts the other way round, and the
# arithmetic of the witness settles it (3c's `LB_Reject_Eco = 0.068` is not a
# multiple of 1/200, and 3d's `share_nonconverged = 0.005` is one fit in 200).
GAMMA_TARGETS = (1.0, 5.0, 11.58, 30.0, 50.0, 90.0, 140.0, 200.0)
ALPHA_3A = 0.08
C_GRID_3B = (0.5, 1.0, 2.0, 5.0, 10.0)
GAMMA_LEV_3C = (0.0, 0.10, 0.20, 0.28)
GAMMA_LEV_3D = (0.0, 0.28)
N_WARMUP_3D = (250, 500, 1000, 2000)
N_STREAMS_3D = 200
N_SEEDS_3B = 100
N_STREAMS_3C = 1000
ALPHA_DGP = 0.05
BETA_DGP = 0.80
QMLE_BOUND_LOW = 1e-6
BOUND_REL_TOL = 1e-6

# =====================================================================
# ANCHORS -- EVERY ONE OF THEM PRINTED IN articleB_whitening_v87.tex L341
# =====================================================================
# "\emph{Estimation cost.} \textsc{Eco-L1} must fit a persistent GARCH
# ($\alpha+\beta = 0.85$) on a finite warm-up: on a $250$-step window the
# estimated persistence collapses to a median $\hat\alpha+\hat\beta = 0.62$ and
# the FPR nearly doubles to $9.5\%$; the level is restored from $n = 500$
# onward. ... The sign pipeline is warm-up-independent in practice (measured FPR
# $3$--$8\%$ across all warm-up lengths)."
V87_TRUE_PERSISTENCE = 0.85
V87_MEDIAN_PERSISTENCE_AT_250 = 0.62      # NOT reproduced -- see the D2 test below
V87_FPR_ECO_AT_250_PERCENT = 9.5          # NOT reproduced -- see the D2 test below
V87_FPR_ECO_AT_500_PERCENT = 3.0          # NOT reproduced -- see the D2 test below
V87_SIGN_FPR_MIN_PERCENT = 3.0            # NOT reproduced -- see the D2 test below
V87_SIGN_FPR_MAX_PERCENT = 8.0            # NOT reproduced -- see the D2 test below
NOMINAL_LEVEL = 0.05

# =====================================================================
# TOLERANCES, EACH DERIVED FROM A MECHANISM
# =====================================================================
# The Wilson interval is a closed form in float64 evaluated two ways. The two
# expressions differ by the reassociation of a product of at most five terms,
# bounded by 5 * eps = 1.1e-15 in relative terms; 1e-12 carries three orders of
# margin and is derived from no observed deviation.
CLOSED_FORM_RTOL = 1e-12
# The penalty recomputed by summing the autocorrelation series of `eps^2` to
# ACF_TERMS lags instead of by its closed form. The truncation remainder is
# 2 * rho_1 * phi^K / (1 - phi); at the largest persistence of the grid,
# phi = alpha + beta < 0.92, so phi^4000 < 1e-140 and the remainder is far below
# float64 resolution. 1e-9 is three orders above the accumulated rounding of the
# 4000 additions and is derived from no observed gap.
ACF_TERMS = 4000
ACF_RTOL = 1e-9
# The bisection `solve_beta_for_gamma` runs is 100 halvings of [0, 1 - alpha -
# 1e-6], so its resolution is 2^-100 of an interval below 1. An independently
# written bisection over the same interval with the same iteration count lands on
# the same float; 1e-12 is the margin, and it is the bisection's own resolution
# and not an observed gap.
BISECTION_RTOL = 1e-12

MACRO_PREFIX = "RSeventeen"
MACRO_HEADER = "% Auto-generated by exp_R17_econometric_baseline.py -- do not edit."
LEGACY_SUFFIX = "_legacy_qmle"


def _read(path):
    assert path.exists(), f"Missing artefact: {path}"
    return pd.read_csv(path, float_precision='round_trip')


@pytest.fixture
def warmup():
    return _read(DATA_DIR / "R17_warmup_sensitivity.csv")


@pytest.fixture
def fits():
    return _read(DATA_DIR / "R17_warmup_fits.csv")


@pytest.fixture
def fpr_baseline():
    return _read(DATA_DIR / "R17_fpr_baseline.csv")


@pytest.fixture
def add_baseline():
    return _read(DATA_DIR / "R17_add_baseline.csv")


@pytest.fixture
def fpr_arms():
    return _read(DATA_DIR / "R17_fpr_arms.csv")


@pytest.fixture
def misspecification():
    return _read(DATA_DIR / "R17_misspecification.csv")


@pytest.fixture
def legacy_warmup():
    return _read(DATA_DIR / f"R17_warmup_sensitivity{LEGACY_SUFFIX}.csv")


@pytest.fixture
def legacy_fpr_baseline():
    return _read(DATA_DIR / f"R17_fpr_baseline{LEGACY_SUFFIX}.csv")


@pytest.fixture
def legacy_fits():
    return _read(DATA_DIR / f"R17_warmup_fits{LEGACY_SUFFIX}.csv")


@pytest.fixture
def witness_warmup():
    return _read(REFERENCE_DIR / "protocol_3d_warmup_sensitivity.csv")


@pytest.fixture
def witness_fpr_baseline():
    return _read(REFERENCE_DIR / "protocol_3a_fpr_baseline_v2.csv")


@pytest.fixture
def witness_fpr_arms():
    return _read(REFERENCE_DIR / "protocol_3b_fpr_arms.csv")


@pytest.fixture
def witness_misspecification():
    return _read(REFERENCE_DIR / "protocol_3c_misspec_v2.csv")


def _macros(name):
    path = TABLES_DIR / name
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
def macros():
    return _macros("R17_claims.tex")


@pytest.fixture
def legacy_macros():
    return _macros(f"R17_claims{LEGACY_SUFFIX}.tex")


# =====================================================================
# INDEPENDENT REIMPLEMENTATIONS OF THE DETERMINISTIC RELATIONS
# =====================================================================

def wilson_score_interval(p_hat, n, z=1.96):
    """
    The Wilson score interval written from the form R02 owns -- margin
    `z * sqrt((p(1-p) + z^2/(4n)) / n) / denom` -- rather than from the form the
    experiment carries, `z * sqrt(p(1-p)/n + z^2/(4n^2)) / denom`. The two are
    the same interval reassociated, which is the point: two routes, one number.
    `z = 1.96` is the delivered constant and not the exact normal quantile.
    """
    if n == 0:
        return 0.0, 0.0
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    margin = (z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n)) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def gamma_from_acf_series(alpha, beta, terms=ACF_TERMS):
    """
    The GARCH penalty recomputed from the DEFINITION instead of from the closed
    form the experiment carries.

    Derivation, in one line each. For a GARCH(1,1) with `phi = alpha + beta < 1`
    and a finite fourth moment of the innovations, the autocorrelation of
    `eps^2` is `rho_k = rho_1 * phi^(k-1)` with
    `rho_1 = alpha (1 - alpha beta - beta^2) / (1 - 2 alpha beta - beta^2)`; the
    variance-inflation factor of a mean of `eps^2` over a long window is
    `Gamma = 1 + 2 * sum_{k>=1} rho_k`. Summing the series term by term is a
    different arithmetic route from `1 + 2 rho_1 / (1 - phi)`, which is what the
    experiment evaluates.
    """
    phi = alpha + beta
    if phi >= 1.0:
        return float('inf')
    denom = 1 - 2 * alpha * beta - beta**2
    if denom <= 0:
        return (1 + phi) / (1 - phi)
    rho_1 = alpha * (1 - alpha * beta - beta**2) / denom
    total = 0.0
    term = rho_1
    for _ in range(terms):
        total += term
        term *= phi
    return max(1.0, 1.0 + 2.0 * total)


def beta_for_gamma(alpha, target, iterations=100):
    """
    An independently written bisection for the coefficient that realises the
    target penalty, over the same interval and with the same iteration count as
    `solve_beta_for_gamma`, but driven by `gamma_from_acf_series` rather than by
    the closed form.
    """
    if target <= 1.0:
        return 0.0
    lo, hi = 0.0, 1.0 - alpha - 1e-6
    mid = hi
    for _ in range(iterations):
        mid = (lo + hi) / 2
        if gamma_from_acf_series(alpha, mid) < target:
            lo = mid
        else:
            hi = mid
    return mid


def rounds_to(value, printed, decimals):
    """v87's printing precision is the classification rule of preamble S3."""
    return round(float(value), decimals) == round(float(printed), decimals)


def top_level_segments(path, names):
    """
    A second, independent extraction of the named top-level functions, written
    here rather than imported: importing the experiment would run its
    determinism bootstrap, which raises once NumPy is loaded.
    """
    text = Path(path).read_text()
    tree = ast.parse(text)
    return {node.name: ast.get_source_segment(text, node)
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in names}


def top_level_nodes(path, names):
    tree = ast.parse(Path(path).read_text())
    return {node.name: node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in names}


class _Redact(ast.NodeTransformer):
    """A second, independent redactor for the differential identity of C8."""

    def __init__(self, targets):
        self.targets = set(map(id, targets))
        self.redacted = 0

    def visit(self, node):
        if id(node) in self.targets:
            self.redacted += 1
            return ast.copy_location(ast.Name(id="__ADAPTED__", ctx=ast.Load()), node)
        return super().visit(node)


def cell(frame, gamma_lev, n_warmup):
    sub = frame[(frame['gamma_lev'] == gamma_lev) & (frame['n_warmup'] == n_warmup)]
    assert len(sub) == 1, f"expected one cell at ({gamma_lev}, {n_warmup}), found {len(sub)}"
    return sub.iloc[0]


# =====================================================================
# BLOCKING ASSERTIONS -- STRUCTURE AND SCHEMA
# =====================================================================

def test_R17_every_artefact_the_prompt_lists_exists_with_its_prescribed_schema(
        warmup, fits, fpr_baseline, add_baseline, fpr_arms, misspecification):
    """
    The cardinalities are the EXPERIMENTAL DESIGN the delivered script fixes --
    eight penalties, five shift magnitudes, four leverage points, four warm-ups
    times two leverage levels -- and not measurements.
    """
    assert len(fpr_baseline) == len(GAMMA_TARGETS) == 8
    assert len(add_baseline) == len(GAMMA_TARGETS) * len(C_GRID_3B) == 40
    assert len(fpr_arms) == len(GAMMA_TARGETS) == 8
    assert len(misspecification) == len(GAMMA_LEV_3C) == 4
    assert len(warmup) == len(GAMMA_LEV_3D) * len(N_WARMUP_3D) == 8
    assert len(fits) == len(GAMMA_LEV_3D) * len(N_WARMUP_3D) * N_STREAMS_3D == 1600
    assert sorted(warmup['n_warmup'].unique()) == list(N_WARMUP_3D)
    assert sorted(warmup['gamma_lev'].unique()) == list(GAMMA_LEV_3D)
    assert bool((warmup['n_streams'] == N_STREAMS_3D).all())
    for column in ('share_equals_initialiser', 'share_at_lower_bound', 'share_at_upper_bound',
                   'n_converged', 'persistence_median_pooled', 'persistence_median_converged',
                   'persistence_sum_of_medians_pooled', 'persistence_sum_of_medians_converged',
                   'alpha_hat_50_converged', 'beta_hat_50_converged',
                   'FPR_Eco_CI_low', 'FPR_Eco_CI_high', 'FPR_ML_CI_low', 'FPR_ML_CI_high'):
        assert column in warmup.columns, f"the warm-up table carries no `{column}`"
    for column in ('share_nonconverged', 'alpha_hat_10', 'alpha_hat_50', 'alpha_hat_90',
                   'beta_hat_10', 'beta_hat_50', 'beta_hat_90'):
        assert column in warmup.columns, (
            f"the delivered `{column}` is kept unchanged beside the added columns for witness "
            f"comparability")
    for column in ('gamma_lev', 'n_warmup', 'stream', 'omega_hat', 'alpha_hat', 'beta_hat',
                   'persistence_hat', 'converged', 'equals_initialiser', 'at_lower_bound',
                   'at_upper_bound', 'alarm_eco', 'alarm_ml'):
        assert column in fits.columns, f"the per-fit table carries no `{column}`"
    assert not (RESULTS_DIR / "figures").exists(), (
        "R17 renders no figure of v87: `grep -c Fig10_Econometric_Baseline` on the frozen "
        "manuscript returns 0, and the witness PNG is vendored under data/reference/R17/ as "
        "produced and not cited")
    assert (REFERENCE_DIR / "Fig10_Econometric_Baseline.png").exists()


def test_R17_the_per_fit_table_reproduces_every_aggregate_of_the_warmup_table(warmup, fits):
    """
    `R17_warmup_fits.csv` is added so that the convergence diagnostics and the
    published median are checkable without rerunning the campaign. It is only
    worth shipping if the aggregates are recoverable from it, so all of them are
    recomputed here cell by cell.
    """
    for row in warmup.to_dict('records'):
        sub = fits[(fits['gamma_lev'] == row['gamma_lev'])
                   & (fits['n_warmup'] == row['n_warmup'])]
        assert len(sub) == N_STREAMS_3D
        assert sorted(sub['stream']) == list(range(N_STREAMS_3D))
        persistence = sub['persistence_hat'].to_numpy(dtype=float)
        alpha = sub['alpha_hat'].to_numpy(dtype=float)
        beta = sub['beta_hat'].to_numpy(dtype=float)
        converged = sub['converged'].to_numpy(dtype=bool)
        assert bool(np.allclose(persistence, alpha + beta, rtol=CLOSED_FORM_RTOL, atol=0.0))
        assert float((~converged).mean()) == float(row['share_nonconverged'])
        assert int(converged.sum()) == int(row['n_converged'])
        assert float(np.percentile(persistence, 50)) == float(row['persistence_median_pooled'])
        assert float(np.percentile(alpha, 50)) == float(row['alpha_hat_50'])
        assert float(np.percentile(beta, 50)) == float(row['beta_hat_50'])
        assert float(np.percentile(alpha, 50) + np.percentile(beta, 50)) == \
            float(row['persistence_sum_of_medians_pooled'])
        assert float(sub['alarm_eco'].mean()) == float(row['FPR_Eco'])
        assert float(sub['alarm_ml'].mean()) == float(row['FPR_ML'])
        assert float(sub['at_lower_bound'].mean()) == float(row['share_at_lower_bound'])
        assert float(sub['equals_initialiser'].mean()) == float(row['share_equals_initialiser'])


def test_R17_the_lower_bound_flag_is_the_box_constraint_and_not_a_threshold(fits):
    """
    `at_lower_bound` must be the optimiser's own box constraint read back, not a
    tolerance chosen to make a share come out. The rule is recomputed here from
    the bound and the SPECS 1.10 truncation resolution alone.
    """
    alpha = fits['alpha_hat'].to_numpy(dtype=float)
    beta = fits['beta_hat'].to_numpy(dtype=float)
    expected = np.minimum(alpha, beta) <= QMLE_BOUND_LOW * (1.0 + BOUND_REL_TOL)
    assert bool((fits['at_lower_bound'].to_numpy(dtype=bool) == expected).all())
    assert bool((alpha >= QMLE_BOUND_LOW).all()) and bool((beta >= QMLE_BOUND_LOW).all()), (
        "no fit may sit below the box the delivered `bounds` declares")
    assert bool((alpha + beta < 0.999).all()), (
        "the delivered routine returns the initialiser whenever the stationarity constraint is "
        "reached, so no persisted fit may violate it")


# =====================================================================
# BLOCKING ASSERTIONS -- THE DETERMINISTIC RELATIONS, REIMPLEMENTED
# =====================================================================

def test_R17_the_realized_penalty_matches_its_target_at_the_eight_grid_points(fpr_baseline):
    """
    C3, re-derived by a second arithmetic route. The `Gamma` column is
    recomputed by SUMMING the autocorrelation series of `eps^2` over 4000 lags,
    where the experiment evaluates the closed form of the same series.
    """
    persisted = sorted(float(v) for v in fpr_baseline['Gamma'])
    for target, realized in zip(GAMMA_TARGETS, persisted):
        if target == 1.0:
            assert realized == 1.0, (
                "at alpha = 0.08 the value Gamma = 1 is unattainable inside the GARCH family; "
                "the delivered script reaches it by simulating (0, 0), which leaves the family. "
                "This is the structure `R11-gamma-grid-floor` registers.")
            assert gamma_from_acf_series(0.0, 0.0) == 1.0
            continue
        beta = beta_for_gamma(ALPHA_3A, target)
        assert beta < 1.0 - ALPHA_3A - 1e-6, "the bisection may not saturate its ceiling"
        independent = gamma_from_acf_series(ALPHA_3A, beta)
        assert abs(independent / target - 1.0) < 1e-6
        assert abs(realized - independent) <= ACF_RTOL * independent, (
            f"the persisted penalty {realized!r} at target {target} does not match the "
            f"{independent!r} the autocorrelation series gives at the beta an independent "
            f"bisection finds")


def test_R17_every_persisted_interval_is_a_wilson_interval_inside_the_unit_square(
        warmup, fpr_arms):
    """
    Every interval is recomputed from a second algebraic form of the same closed
    form, and preamble S7 requires every persisted bound to be clamped into
    [0, 1] before it reaches disk.
    """
    for column in ('FPR_Eco', 'FPR_ML', 'FPR_Eco_CI_low', 'FPR_Eco_CI_high',
                   'FPR_ML_CI_low', 'FPR_ML_CI_high', 'share_nonconverged',
                   'share_at_lower_bound', 'share_equals_initialiser', 'share_at_upper_bound'):
        assert bool((warmup[column] >= 0.0).all()) and bool((warmup[column] <= 1.0).all())
    for row in warmup.itertuples(index=False):
        for rate, low, high in ((row.FPR_Eco, row.FPR_Eco_CI_low, row.FPR_Eco_CI_high),
                                (row.FPR_ML, row.FPR_ML_CI_low, row.FPR_ML_CI_high)):
            expected_low, expected_high = wilson_score_interval(rate, N_STREAMS_3D)
            assert abs(low - expected_low) <= CLOSED_FORM_RTOL * max(1.0, expected_low)
            assert abs(high - expected_high) <= CLOSED_FORM_RTOL * max(1.0, expected_high)
            assert low <= rate <= high
    for row in fpr_arms.itertuples(index=False):
        for rate, low, high in ((row.FPR_Recalib, row.CI_low_Recalib, row.CI_high_Recalib),
                                (row.FPR_Eco_L2, row.CI_low_Eco_L2, row.CI_high_Eco_L2),
                                (row.FPR_Eco_L1, row.CI_low_Eco_L1, row.CI_high_Eco_L1),
                                (row.FPR_ML, row.CI_low_ML, row.CI_high_ML)):
            expected_low, expected_high = wilson_score_interval(rate, N_SEEDS_3B)
            assert abs(low - expected_low) <= CLOSED_FORM_RTOL * max(1.0, expected_low)
            assert abs(high - expected_high) <= CLOSED_FORM_RTOL * max(1.0, expected_high)
            assert 0.0 <= low <= high <= 1.0


def test_R17_the_carried_primitives_are_byte_identical_to_the_files_that_own_them():
    """
    C8, re-run by a second extraction rather than trusted from the log. Preamble
    S4.2 forbids hoisting a scientific primitive into `experiments/common/`, and
    the reason is measurable: the same routine names exist elsewhere in this
    repository with different bodies, so borrowing one would move a published
    value.
    """
    from_witness = ("compute_gamma_exact", "solve_beta_for_gamma", "strict_cusum",
                    "_garch_nll", "filter_sigma2", "wilson_ci")
    from_r13 = ("get_deterministic_seed", "seed_sequence_for", "rng_for")
    mine = top_level_segments(EXPERIMENT, set(from_witness) | set(from_r13))
    witness = top_level_segments(WITNESS_SCRIPT, set(from_witness))
    r13 = top_level_segments(R13_SCRIPT, set(from_r13))
    for name in from_witness:
        assert mine[name] == witness[name], f"{name} has drifted from {WITNESS_SCRIPT.name}"
    for name in from_r13:
        assert mine[name] == r13[name], f"{name} has drifted from {R13_SCRIPT.name}"
    # The duplication is deliberate, and this is the evidence for it: R17's
    # quasi-likelihood is NOT R14's, which is the copy R14 carries from its own
    # witness.
    r14 = top_level_segments(
        ROOT / "experiments" / "R14_crypto_isofpr" / "exp_R14_crypto_isofpr.py",
        {"_garch_nll", "strict_cusum", "wilson_ci"})
    for name in ("_garch_nll", "strict_cusum", "wilson_ci"):
        assert mine[name] != r14[name], (
            f"{name} is now identical to R14's copy; if the two have genuinely converged, the "
            f"justification recorded in AUDIT_R17.md for duplicating it must be revised")


def test_R17_the_three_adapted_routines_differ_from_the_witness_at_one_node_each():
    """
    C8's differential clause, re-derived by a second redaction. The named node is
    replaced by a sentinel in BOTH trees and full `ast.dump` equality is then
    required: that admits exactly one difference and proscribes every other, at
    any depth, which a visual diff does not.
    """
    names = ("simulate_garch11", "simulate_gjr11", "fit_garch_qmle")
    mine = top_level_nodes(EXPERIMENT, set(names))
    witness = top_level_nodes(WITNESS_SCRIPT, set(names))
    for name in names:
        if name == "fit_garch_qmle":
            def targets(node):
                calls = [child for child in ast.walk(node)
                         if isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
                         and child.func.id in ("minimize", "qmle_minimize")]
                assert len(calls) == 1, f"{name} must contain exactly one optimiser call"
                return calls
        else:
            def targets(node):
                return [node.args.args[-1], node.args.defaults[-1], node.body[1]]
        mine_targets, witness_targets = targets(mine[name]), targets(witness[name])
        mine_redactor, witness_redactor = _Redact(mine_targets), _Redact(witness_targets)
        mine_dump = ast.dump(mine_redactor.visit(mine[name]))
        witness_dump = ast.dump(witness_redactor.visit(witness[name]))
        assert mine_redactor.redacted == len(mine_targets)
        assert witness_redactor.redacted == len(witness_targets)
        assert mine_dump == witness_dump, (
            f"{name} differs from {WITNESS_SCRIPT.name} somewhere other than its one permitted "
            f"node")
    # The permitted difference is what it is declared to be, and not something else.
    assert "np.random.default_rng(seed)" in top_level_segments(
        WITNESS_SCRIPT, {"simulate_garch11"})["simulate_garch11"]
    assert "rng = loc_rng" in top_level_segments(
        EXPERIMENT, {"simulate_garch11"})["simulate_garch11"]
    own = top_level_segments(EXPERIMENT, {"fit_garch_qmle", "qmle_minimize"})
    assert "qmle_minimize(" in own["fit_garch_qmle"]
    for required in ("tol=QMLE_SPECS_TOL", "'ftol': QMLE_SPECS_FTOL", "'eps': QMLE_SPECS_EPS",
                     "round(float(res.x[0]), QMLE_SPECS_DECIMALS)"):
        assert required in own["qmle_minimize"], (
            f"SPECS 1.10 requires {required} on the `specs` arm")


def test_R17_the_argument_order_of_solve_beta_for_gamma_is_the_witness_s_at_every_call_site():
    """
    C4, re-derived. Transposing these two arguments destroyed a whole stream of
    this campaign (`R04-gamma-grid-defect`, registered D3), so the assertion is
    that every call site of the port carries the same argument EXPRESSIONS as
    the witness's, not merely the same arity.
    """
    def signatures(path):
        tree = ast.parse(Path(path).read_text())
        return {tuple(ast.dump(arg) for arg in node.args)
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "solve_beta_for_gamma"}

    definition = top_level_nodes(WITNESS_SCRIPT, {"solve_beta_for_gamma"})["solve_beta_for_gamma"]
    assert [a.arg for a in definition.args.args] == ["alpha", "target_gamma"]
    mine, witness = signatures(EXPERIMENT), signatures(WITNESS_SCRIPT)
    assert len(mine) == 1 and mine == witness, (
        f"this port calls solve_beta_for_gamma with {sorted(mine)} while the witness calls it "
        f"with {sorted(witness)}")


# =====================================================================
# BLOCKING ASSERTIONS -- THE SIGN ARM AND ITS DEGENERACY
# =====================================================================

def test_R17_the_sign_stream_is_bit_identical_across_the_leverage_axis(warmup, fits):
    """
    A SELF-INVALIDATING ASSERTION, and the one the deviation
    `R17-sign-arm-crn-degeneracy` is written around.

    `simulate_gjr11` draws the whole innovation vector BEFORE the variance
    recursion and every `sigma2[t]` is strictly positive, so
    `sign(eps_t) = sign(z_t)` exactly and the monitored binary stream depends on
    the key, on `nu` and on `n` alone. Under a key carrying role and index only,
    the two `gamma_lev` of a warm-up length therefore read the SAME stream, and
    the eight cells of the table hold four readings and not eight.

    If a later change to the simulator or to the key breaks the identity, this
    fires, and `docs/DEVIATIONS.md` and `AUDIT_R17.md` are what must change.
    """
    for nw in N_WARMUP_3D:
        rates = {g: float(cell(warmup, g, nw)['FPR_ML']) for g in GAMMA_LEV_3D}
        assert len(set(rates.values())) == 1, (
            f"at n_warmup = {nw} the sign arm reads {rates}; the two leverage levels share one "
            f"innovation vector, so the two rates are the same number by construction")
        per_stream = {g: fits[(fits['gamma_lev'] == g) & (fits['n_warmup'] == nw)]
                      .sort_values('stream')['alarm_ml'].to_numpy(dtype=bool)
                      for g in GAMMA_LEV_3D}
        assert bool((per_stream[GAMMA_LEV_3D[0]] == per_stream[GAMMA_LEV_3D[1]]).all()), (
            f"at n_warmup = {nw} the per-stream sign alarms differ between the two leverage "
            f"levels, which is impossible if the monitored streams are identical")
    assert len(set(warmup['FPR_ML'])) <= len(N_WARMUP_3D), (
        "eight cells cannot carry more than four distinct sign rates")


def test_R17_the_sign_arm_is_warm_up_independent_by_an_exact_paired_test(fits):
    """
    L341's qualitative claim about the sign pipeline is that it is
    "warm-up-independent in practice". A min-max envelope is NOT a test of that
    claim -- an extremum over a grid has no stable sampling distribution
    (S4bis, fourth corollary) -- so the claim is tested here by the EXACT paired
    test the design admits: the four warm-up lengths are read on the same 200
    streams, so the extreme pair of cells forms a matched sample and McNemar's
    exact binomial on the discordant streams applies with no asymptotics and no
    bootstrap.
    """
    rates = {nw: float(fits[(fits['gamma_lev'] == GAMMA_LEV_3D[0])
                            & (fits['n_warmup'] == nw)]['alarm_ml'].mean())
             for nw in N_WARMUP_3D}
    low_nw = min(rates, key=rates.get)
    high_nw = max(rates, key=rates.get)
    low = fits[(fits['gamma_lev'] == GAMMA_LEV_3D[0]) & (fits['n_warmup'] == low_nw)] \
        .sort_values('stream')['alarm_ml'].to_numpy(dtype=bool)
    high = fits[(fits['gamma_lev'] == GAMMA_LEV_3D[0]) & (fits['n_warmup'] == high_nw)] \
        .sort_values('stream')['alarm_ml'].to_numpy(dtype=bool)
    b = int(np.sum(high & ~low))
    c = int(np.sum(low & ~high))
    assert b + c > 0, (
        "the two extreme cells agree stream by stream, so no paired test is defined; the four "
        "readings would then be one reading and AUDIT_R17.md's account of the warm-up axis as "
        "four genuine draws must be revised")
    result = stats.binomtest(b, b + c, 0.5)
    assert result.pvalue > NOMINAL_LEVEL, (
        f"the two extreme warm-up lengths of the sign arm, n = {low_nw} at {rates[low_nw]} and "
        f"n = {high_nw} at {rates[high_nw]}, are distinguishable on their {b + c} discordant "
        f"streams at p = {result.pvalue}. L341's 'warm-up-independent in practice' would then be "
        f"contradicted, which is a D3 and stops the campaign.")


# =====================================================================
# BLOCKING ASSERTIONS -- THE THREE QUALITATIVE CLAIMS OF L341
# =====================================================================

def test_R17_the_persistence_collapse_of_L341_reproduces(warmup, macros):
    """
    L341: "\\textsc{Eco-L1} must fit a persistent GARCH ($\\alpha+\\beta = 0.85$)
    on a finite warm-up: on a $250$-step window the estimated persistence
    collapses to a median $\\hat\\alpha+\\hat\\beta = 0.62$". The true value is a
    design constant and reproduces exactly; the collapse and its recovery with
    the warm-up are the qualitative content and both hold.
    """
    assert ALPHA_DGP + BETA_DGP == pytest.approx(V87_TRUE_PERSISTENCE, rel=CLOSED_FORM_RTOL)
    assert macros['RSeventeenTruePersistence'] == f"{ALPHA_DGP + BETA_DGP:.2f}"
    at_250 = float(cell(warmup, GAMMA_LEV_3D[0], 250)['persistence_median_pooled'])
    at_500 = float(cell(warmup, GAMMA_LEV_3D[0], 500)['persistence_median_pooled'])
    at_1000 = float(cell(warmup, GAMMA_LEV_3D[0], 1000)['persistence_median_pooled'])
    assert at_250 < V87_TRUE_PERSISTENCE, "L341: the persistence 'collapses' at n = 250"
    assert at_250 < at_500 < at_1000, (
        "the collapse is a finite-warm-up effect, so the median must climb back toward the truth "
        "as the window grows")
    assert macros['RSeventeenMedianPersistenceAtWarmupTwoFifty'] == f"{at_250:.2f}"


def test_R17_the_false_alarm_restoration_of_L341_reproduces(warmup, macros):
    """
    L341: "the FPR nearly doubles to $9.5\\%$; the level is restored from
    $n = 500$ onward." The qualitative content is a rate that falls with the
    warm-up and a level held from n = 500. Preamble S3 fixes the falsification
    rule for a printed bound: it is crossed only if the 95% interval of the
    regenerated value EXCLUDES it.
    """
    for gamma_lev in GAMMA_LEV_3D:
        rates = [float(cell(warmup, gamma_lev, nw)['FPR_Eco']) for nw in N_WARMUP_3D]
        assert rates == sorted(rates, reverse=True), (
            f"at gamma_lev = {gamma_lev} the parametric false-alarm rate {rates} does not fall "
            f"monotonically with the warm-up; L341's restoration claim rests on that direction")
        at_500 = cell(warmup, gamma_lev, 500)
        assert float(at_500['FPR_Eco_CI_low']) <= NOMINAL_LEVEL <= float(at_500['FPR_Eco_CI_high']), (
            f"at gamma_lev = {gamma_lev} the n = 500 Wilson interval "
            f"[{at_500['FPR_Eco_CI_low']}, {at_500['FPR_Eco_CI_high']}] excludes the nominal "
            f"{NOMINAL_LEVEL}, so 'the level is restored from n = 500 onward' is falsified there")
    at_250 = float(cell(warmup, GAMMA_LEV_3D[0], 250)['FPR_Eco'])
    at_500 = float(cell(warmup, GAMMA_LEV_3D[0], 500)['FPR_Eco'])
    assert at_250 > NOMINAL_LEVEL, "L341: the rate at n = 250 sits above the nominal level"
    assert macros['RSeventeenFprEcoAtWarmupTwoFifty'] == f"{100.0 * at_250:.1f}\\%"
    assert macros['RSeventeenFprEcoAtWarmupFiveHundred'] == f"{100.0 * at_500:.1f}\\%"


def test_R17_the_published_cell_carries_corner_solutions_the_convergence_flag_does_not_see(
        warmup, fits):
    """
    A SELF-INVALIDATING ASSERTION. The delivered convergence flag is
    `res.success and max(|a - 0.05|, |b - 0.90|) > 1e-6`: it detects an SLSQP
    failure or a return to the initialiser and nothing else, so a corner
    solution at the optimiser's lower bound -- persistence about zero, no GARCH
    at all -- is recorded as converged. At the cell L341 publishes, the flag
    reports no failure at all while a substantial share of the fits sit ON that
    bound.

    If a later campaign removes the corner solutions, this fires, and what must
    change is `AUDIT_R17.md`'s account of the flag, never this assertion.
    """
    published = cell(warmup, GAMMA_LEV_3D[0], 250)
    assert float(published['share_nonconverged']) == 0.0, (
        "the delivered flag reports no non-convergence at this cell, which is what makes the "
        "corner solutions invisible in the witness table")
    assert float(published['share_at_lower_bound']) > 0.0, (
        "the finding this stream records is that fits the flag calls converged sit on the "
        "optimiser's lower bound; if none does, the audit's account must be revised")
    sub = fits[(fits['gamma_lev'] == GAMMA_LEV_3D[0]) & (fits['n_warmup'] == 250)]
    corners = sub[sub['at_lower_bound']]
    assert bool(corners['converged'].all()), (
        "every corner solution at this cell is flagged converged: that is the defect, stated as "
        "an assertion so that it cannot quietly stop being true")
    assert len(corners) == int(round(float(published['share_at_lower_bound']) * N_STREAMS_3D))
    # The share falls as the window grows, which is what makes it a
    # finite-warm-up artefact rather than a coding defect.
    shares = [float(cell(warmup, GAMMA_LEV_3D[0], nw)['share_at_lower_bound'])
              for nw in N_WARMUP_3D]
    assert shares == sorted(shares, reverse=True)


def test_R17_the_four_numerals_of_L341_do_not_reproduce_at_their_printed_precision(
        warmup, macros):
    """
    THE SELF-INVALIDATING ASSERTION the deviation `R17-campaign-redraw` is
    written around.

    v87 L341 prints a persistence median of `0.62`, a false-alarm rate of
    `9.5\\%` at `n = 250`, a restored level of `3.0\\%` at `n = 500`, and a sign
    envelope of `3`--`8\\%`. The 128-bit re-keying redraws every stream of the
    campaign and none of them rounds to its printed value any more. The
    QUALITATIVE claims are a different question and are asserted in the three
    tests above; all of them hold.

    If a later campaign brings any of these back, this test fires, and what must
    then change is `docs/DEVIATIONS.md` -- the entry is withdrawn -- never this
    assertion.
    """
    at_250 = cell(warmup, GAMMA_LEV_3D[0], 250)
    at_500 = cell(warmup, GAMMA_LEV_3D[0], 500)
    assert not rounds_to(at_250['persistence_median_pooled'],
                         V87_MEDIAN_PERSISTENCE_AT_250, 2)
    assert not rounds_to(100.0 * float(at_250['FPR_Eco']), V87_FPR_ECO_AT_250_PERCENT, 1)
    assert not rounds_to(100.0 * float(at_500['FPR_Eco']), V87_FPR_ECO_AT_500_PERCENT, 1)
    sign_rates = [float(cell(warmup, GAMMA_LEV_3D[0], nw)['FPR_ML']) for nw in N_WARMUP_3D]
    assert not rounds_to(100.0 * min(sign_rates), V87_SIGN_FPR_MIN_PERCENT, 0)
    assert not rounds_to(100.0 * max(sign_rates), V87_SIGN_FPR_MAX_PERCENT, 0)
    assert macros['RSeventeenSignFprMin'] == f"{100.0 * min(sign_rates):.0f}\\%"
    assert macros['RSeventeenSignFprMax'] == f"{100.0 * max(sign_rates):.0f}\\%"
    assert macros['RSeventeenNonConvergedMax'] == \
        f"{100.0 * float(warmup['share_nonconverged'].max()):.1f}\\%"


def test_R17_the_definitional_gap_between_the_two_persistence_constructions_is_measured(warmup):
    """
    The witness stores marginal medians and never the median of the sum: its
    `0.62` is `alpha_hat_50 + beta_hat_50`. L341 reads "a median
    $\\hat\\alpha+\\hat\\beta$", which is the median OF the sum. Both are computed
    on the same fits and persisted side by side, so the definitional term of the
    gap is a measured quantity here rather than an argument.
    """
    for row in warmup.to_dict('records'):
        assert not math.isnan(float(row['persistence_median_pooled']))
        assert not math.isnan(float(row['persistence_sum_of_medians_pooled']))
        if int(row['n_converged']) == N_STREAMS_3D:
            assert float(row['persistence_median_pooled']) == \
                float(row['persistence_median_converged']), (
                "with every fit converged the pooled and converged medians are the same object")
    published = cell(warmup, GAMMA_LEV_3D[0], 250)
    assert float(published['persistence_median_pooled']) != \
        float(published['persistence_sum_of_medians_pooled']), (
        "the two constructions coincide only by accident; if they now do at the published cell, "
        "the three-term decomposition in AUDIT_R17.md must be rewritten")


# =====================================================================
# BLOCKING ASSERTIONS -- THE CONTROL TABLES AND THE OTHER DEGENERACIES
# =====================================================================

def test_R17_the_uncalibrated_and_recalibrated_arms_coincide_at_unit_penalty(fpr_baseline):
    """
    C6. At `Gamma = 1.00` there is nothing to recalibrate: `65.0 * 1.0` and
    `65.0` are the same float, so the two arms read one threshold. It is this
    witness that makes the `Uncal` column interpretable at every other point.
    """
    at_one = fpr_baseline[fpr_baseline['Gamma'] == 1.0]
    assert len(at_one) == 1
    assert float(at_one['Uncal'].iloc[0]) == float(at_one['Recalib'].iloc[0])
    assert 65.0 * 1.0 == 65.0
    above = fpr_baseline[fpr_baseline['Gamma'] > 1.0]
    assert bool((above['Uncal'] > above['Recalib']).all()), (
        "away from the unit penalty the recalibrated threshold must alarm strictly less often, "
        "which is the whole content of the `Lethargy Tax`")


def test_R17_the_sign_arm_is_constant_wherever_the_key_omits_the_grid_coordinate(
        fpr_baseline, fpr_arms, misspecification):
    """
    The same identity as the warm-up table, read on the three control tables.
    `n = 7000` is fixed in 3a, 3b and 3c, so one draw serves the whole grid and
    the `ML` column is ONE measurement printed eight or four times. The witness
    prints exactly the same constancy under its own integer seeds, for the same
    reason.
    """
    assert len(set(fpr_baseline['ML'])) == 1, (
        "3a: the monitored sign stream is bit-identical at all eight penalties")
    assert len(set(fpr_arms['FPR_ML'])) == 1, (
        "3b at c = 0: the shift is zero, so the sign stream is the unshifted one and identical "
        "at all eight penalties")
    assert len(set(misspecification['FPR_ML'])) == 1, (
        "3c: the sign of eps does not depend on the leverage coefficient")
    assert len(set(misspecification['LB_Reject_ML'])) == 1, (
        "3c: the Ljung-Box on the sign stream reads the same stream at all four leverage points")
    assert len(set(misspecification['FPR_Eco'])) > 1, (
        "the parametric arm reads eps^2 through the variance recursion, which DOES carry the "
        "leverage coefficient; if it too were constant the standardization would not be reading "
        "the process")


def test_R17_the_misspecification_table_is_a_control_and_not_L349(misspecification):
    """
    Scope, asserted rather than stated. L349's numerals belong to
    `fig:leverage`, which R12 owns at 15 leverage points, 10 000 streams and a
    pseudo-Gaussian `nu = 100`. Protocol 3c runs four points, 1000 streams and
    Student-`t7`; the two designs are different measurements of the same
    phenomenon and no macro of R17 reads this table.
    """
    assert len(misspecification) == 4
    assert sorted(float(v) for v in misspecification['GammaLev']) == list(GAMMA_LEV_3C)
    for column in ('FPR_Eco', 'LB_Reject_Eco'):
        values = misspecification.sort_values('GammaLev')[column].to_numpy(dtype=float)
        assert float(values[-1]) > float(values[0]), (
            f"`{column}` must climb with the leverage the symmetric limit ignores; that direction "
            f"is the qualitative content L349 states, and it is R12 that publishes its numerals")
    macros = _macros("R17_claims.tex")
    assert not any('Uncal' in name or 'Misspec' in name or 'Leverage' in name for name in macros), (
        "no macro of R17 may encroach on R03's FPR explosion or on R12's leverage table")


# =====================================================================
# BLOCKING ASSERTIONS -- THE LEGACY-QMLE ATTRIBUTION ARM
# =====================================================================

def test_R17_the_legacy_arm_reproduces_the_deterministic_content_of_the_witness(
        legacy_fpr_baseline, witness_fpr_baseline):
    """
    The `Gamma` grid is the one part of the witness that is DETERMINISTIC: it
    comes from a 100-iteration bisection on a closed form and carries no draw.
    Both arms must reproduce it exactly. Every other witness cell is a
    Monte-Carlo value the 128-bit re-keying redraws on BOTH arms, which is why
    no other witness quantity anchors an assertion here.
    """
    mine = sorted(float(v) for v in legacy_fpr_baseline['Gamma'])
    witness = sorted(float(v) for v in witness_fpr_baseline['Gamma'])
    assert len(mine) == len(witness) == 8
    for a, b in zip(mine, witness):
        assert abs(a - b) <= BISECTION_RTOL * max(1.0, abs(b)), (
            f"the regenerated penalty {a!r} differs from the witness's {b!r} by more than the "
            f"bisection's own resolution; the grid is deterministic and must not move")


def test_R17_the_two_option_arms_differ_only_where_the_optimiser_reaches(
        warmup, legacy_warmup, fpr_baseline, legacy_fpr_baseline, misspecification):
    """
    C7, the attribution. The two arms share every draw, so whatever separates
    them is SPECS 1.10 and nothing else. Protocol 3c fits nothing -- it
    standardizes with the symmetric population limit -- so its table must be
    bit-identical between the arms; the warm-up table, whose every cell is
    downstream of a fit, is where the displacement can appear.
    """
    legacy_misspecification = _read(DATA_DIR / f"R17_misspecification{LEGACY_SUFFIX}.csv")
    assert misspecification.equals(legacy_misspecification), (
        "protocol 3c performs no QMLE fit at all, so SPECS 1.10 cannot reach it; a difference "
        "here would mean the option flag leaks into a code path it does not name")
    for column in ('n_warmup', 'gamma_lev', 'n_streams'):
        assert bool((warmup[column] == legacy_warmup[column]).all())
    assert bool((fpr_baseline['ML'] == legacy_fpr_baseline['ML']).all()), (
        "the sign arm reads no fitted parameter, so no optimiser option can move it")
    assert bool((warmup['FPR_ML'] == legacy_warmup['FPR_ML']).all())


def test_R17_the_legacy_artefacts_declare_that_they_certify_no_published_value(legacy_macros):
    """
    Preamble S4.3 requires a deliberately selected alternative path to be
    stamped in the name of its output. The stamp is necessary and not
    sufficient: the macro file says in its own header what it is for, because a
    file called `R17_claims_legacy_qmle.tex` is one `\\input` away from being
    mistaken for the real one.
    """
    text = (TABLES_DIR / f"R17_claims{LEGACY_SUFFIX}.tex").read_text()
    assert "CERTIFY NO v87 VALUE" in text
    assert set(legacy_macros) == set(_macros("R17_claims.tex")), (
        "the two arms must emit the same macro NAMES, or the diagnostic is not comparable with "
        "the arm it diagnoses")
    for name in ('R17_fpr_baseline', 'R17_add_baseline', 'R17_fpr_arms', 'R17_misspecification',
                 'R17_warmup_sensitivity', 'R17_warmup_fits'):
        assert (DATA_DIR / f"{name}{LEGACY_SUFFIX}.csv").exists(), (
            "every output of the diagnostic arm is stamped, not just the ones that differ")


# =====================================================================
# BLOCKING ASSERTIONS -- FILE HYGIENE THE PREAMBLE IMPOSES
# =====================================================================

def test_R17_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix(macros):
    assert macros, "R17_claims.tex carries no macro"
    for name, body in macros.items():
        assert name.startswith(MACRO_PREFIX), (
            f"{name} does not carry the cardinal prefix {MACRO_PREFIX}. Preamble S6 fixes "
            f"\\R<Ordinal><Claim> with the ordinal in English words, and the repository realises "
            f"cardinals throughout (ROne ... RSix, REleven, RThirteen, RSixteen, REighteen).")
        assert not name.startswith("RSeventeenth"), "cardinal, never ordinal"
        assert 'nan' not in body.lower(), f"macro {name} carries the body {body!r}"
        assert body.strip() != ""
    assert 'RSeventeenUncalFprMax' not in macros, (
        "the R17 prompt section 4 mandates this macro for protocol 3a's FPR explosion; it is "
        "expressly dropped because that explosion belongs to R03 and the preamble forbids a "
        "macro that encroaches on another stream's results directory")
    assert not any('Median' in name and 'Asympt' in name for name in macros), (
        "no macro for 1/(4 n f_z(0)^2): it is an analytic result L341 cites to van der Vaart, "
        "not a measurement of this stream")
    assert len(macros) == 12


def test_R17_every_produced_text_file_ends_in_a_newline():
    """
    Preamble S6: docs/sections/*.md and requirements/*.txt are assembled by
    concatenation, and a missing newline glues two dependencies onto one line.
    """
    for path in (TABLES_DIR / "R17_claims.tex",
                 TABLES_DIR / f"R17_claims{LEGACY_SUFFIX}.tex",
                 ROOT / "requirements" / "R17.txt",
                 ROOT / "docs" / "sections" / "R17.md",
                 ROOT / "docs" / "audits" / "AUDIT_R17.md"):
        assert path.exists(), f"Missing deliverable: {path}"
        assert path.read_text().endswith("\n"), f"{path} does not end in a newline"


def test_R17_the_produced_sources_and_logs_carry_no_confirmatory_language():
    """
    Preamble S4.4. The banned words attribute the value of a proof to a
    measurement; neutral technical uses stay licit and none of them matches this
    pattern.
    """
    pattern = re.compile(
        r"proves|proven|perfectly valid|validates the (theorem|thesis|claim)|confirms the|"
        r"as expected|triumph|victory|irrefutable|brilliant", re.IGNORECASE)
    targets = [EXPERIMENT,
               ROOT / "docs" / "sections" / "R17.md",
               ROOT / "docs" / "audits" / "AUDIT_R17.md",
               ROOT / "logs" / "R17_econometric_baseline" / "exp_R17_econometric_baseline.log",
               ROOT / "logs" / "R17_econometric_baseline"
               / f"exp_R17_econometric_baseline{LEGACY_SUFFIX}.log"]
    for path in targets:
        assert path.exists(), f"Missing deliverable: {path}"
        hits = [line for line in path.read_text().splitlines() if pattern.search(line)]
        assert not hits, f"{path.name} carries confirmatory language: {hits[:3]}"


def test_R17_the_produced_sources_carry_no_banned_construct():
    """Preamble S7: no `iterrows`, no bare `except:`, no absolute path."""
    text = EXPERIMENT.read_text()
    assert "iterrows" not in text
    assert not re.search(r"except\s*:", text)
    assert not re.search(r"['\"]/home/", text), "no absolute path may be embedded"
    assert "run_all.sh" not in text and "run_tests.sh" not in text, (
        "the shared orchestrators are never touched by an experiment")
    # The one `except Exception` of the file is the witness's own fallback,
    # carried byte-identically under control C8. Preamble S7 forbids leaving it
    # UNLOGGED, and what discharges that is `qmle_minimize`: it logs the
    # optimiser exception and re-raises, so the carried handler runs exactly as
    # written and nothing is silent.
    handlers = [node for node in ast.walk(ast.parse(text)) if isinstance(node, ast.ExceptHandler)]
    assert len(handlers) == 2, (
        f"this file carries {len(handlers)} exception handlers; the two admitted are "
        f"qmle_minimize's, which logs and re-raises, and the witness's own fallback in "
        f"fit_garch_qmle, which is carried byte-identically under control C8")
    handler = top_level_segments(EXPERIMENT, {"qmle_minimize"})["qmle_minimize"]
    assert "logger.error" in handler and "raise" in handler
    orchestrator = (ROOT / "run_experiment_R17.sh").read_text()
    executable = [line for line in orchestrator.splitlines()
                  if line.strip() and not line.lstrip().startswith("#")]
    assert not any("pytest" in line for line in executable), (
        "preamble S6: the test suite is the exclusive remit of run_tests.sh")
    assert any("--qmle-options legacy" in line for line in executable), (
        "the attribution arm runs unconditionally; running it only when a result looks wrong "
        "turns it into an instrument of selection")
    assert 'PYTHONHASHSEED="42"' in orchestrator


def test_R17_every_square_root_of_a_sample_size_follows_a_design_effect():
    """
    S4bis's sixth corollary made mechanical. A bare `np.sqrt(len(...))` is a
    form defect proscribed exactly as a bare `except:` is, and the rule is that
    the design effect is computed and logged in the same logical block just
    above it.
    """
    text = EXPERIMENT.read_text()
    lines = text.splitlines()
    tree = ast.parse(text)
    first = tree.body[0]
    start = (first.end_lineno if isinstance(first, ast.Expr)
             and isinstance(first.value, ast.Constant) else 0)
    offenders = []
    for i, line in enumerate(lines):
        if i < start or line.lstrip().startswith("#"):
            continue
        if not re.search(r"np\.sqrt\(\s*(len\(|n[_a-z]*\s*\))", line):
            continue
        window = "\n".join(lines[max(0, i - 12):i])
        if "deff" not in window:
            offenders.append((i + 1, line.strip()))
    assert not offenders, (
        f"a square root of a sample size is taken without the design effect computed in the same "
        f"block above it: {offenders}")


# =====================================================================
# REPORTING -- PRINTS WHAT R17 MEASURED, ASSERTS NOTHING
# =====================================================================

def test_R17_report_the_campaign_against_its_witness(warmup, legacy_warmup, witness_warmup):
    """
    The D0-D3 classification of preamble S3, computed rather than asserted, and
    the attribution the legacy arm exists to provide.
    """
    print("\n" + "=" * 78)
    print("R17 -- the warm-up table against the submitted campaign's witness")
    print("=" * 78)
    print(f"  {'g_lev':>6} {'nw':>5} | {'FPR_Eco':>26} | {'FPR_ML':>26} | {'nonconv':>20}")
    print(f"  {'':>6} {'':>5} | {'witness':>8}{'specs':>9}{'legacy':>9} | "
          f"{'witness':>8}{'specs':>9}{'legacy':>9} | {'witness':>6}{'specs':>7}{'legacy':>7}")
    for g in GAMMA_LEV_3D:
        for nw in N_WARMUP_3D:
            w, s, l = (cell(witness_warmup, g, nw), cell(warmup, g, nw),
                       cell(legacy_warmup, g, nw))
            print(f"  {g:>6.2f} {nw:>5} | {w['FPR_Eco']:>8.3f}{s['FPR_Eco']:>9.3f}"
                  f"{l['FPR_Eco']:>9.3f} | {w['FPR_ML']:>8.3f}{s['FPR_ML']:>9.3f}"
                  f"{l['FPR_ML']:>9.3f} | {w['share_nonconverged']:>6.3f}"
                  f"{s['share_nonconverged']:>7.3f}{l['share_nonconverged']:>7.3f}")
    print("  The two arms share every draw, so what separates them is SPECS 1.10 alone; what")
    print("  separates both from the witness is the 128-bit re-keying.")
    print("=" * 78)


def test_R17_report_the_three_term_decomposition_of_the_persistence_gap(warmup, legacy_warmup):
    print("\n" + "=" * 78)
    print("R17 -- the persistence median, and the three terms of its gap against v87's 0.62")
    print("=" * 78)
    print(f"  {'g_lev':>6} {'nw':>5} {'median of sum':>15} {'sum of medians':>16} "
          f"{'definitional':>14} {'converged only':>16}")
    for g in GAMMA_LEV_3D:
        for nw in N_WARMUP_3D:
            row = cell(warmup, g, nw)
            print(f"  {g:>6.2f} {nw:>5} {row['persistence_median_pooled']:>15.6f} "
                  f"{row['persistence_sum_of_medians_pooled']:>16.6f} "
                  f"{row['persistence_median_pooled'] - row['persistence_sum_of_medians_pooled']:>14.6f} "
                  f"{row['persistence_median_converged']:>16.6f}")
    published = cell(warmup, GAMMA_LEV_3D[0], 250)
    legacy_published = cell(legacy_warmup, GAMMA_LEV_3D[0], 250)
    definitional = float(published['persistence_median_pooled']) \
        - float(published['persistence_sum_of_medians_pooled'])
    options = float(published['persistence_median_pooled']) \
        - float(legacy_published['persistence_median_pooled'])
    total = float(published['persistence_median_pooled']) - V87_MEDIAN_PERSISTENCE_AT_250
    print(f"  At the published cell (250, 0.00): total gap against 0.62 = {total:+.6f}")
    print(f"    definitional term  (median of the sum vs sum of medians) = {definitional:+.6f}")
    print(f"    optimiser options  (specs arm vs legacy arm, common draw) = {options:+.6f}")
    print(f"    128-bit redraw     (residual)                            = "
          f"{total - definitional - options:+.6f}")
    print("=" * 78)


def test_R17_report_the_sign_arm_over_the_warm_up_axis(warmup, fits):
    print("\n" + "=" * 78)
    print("R17 -- the sign arm: four readings in eight cells, and their paired comparison")
    print("=" * 78)
    for nw in N_WARMUP_3D:
        row = cell(warmup, GAMMA_LEV_3D[0], nw)
        other = cell(warmup, GAMMA_LEV_3D[1], nw)
        print(f"  n_warmup {nw:>5}: FPR_ML {row['FPR_ML']:.3f} "
              f"[{row['FPR_ML_CI_low']:.3f}, {row['FPR_ML_CI_high']:.3f}] at gamma_lev 0.00, "
              f"{other['FPR_ML']:.3f} at gamma_lev 0.28 -- identical by construction")
    rates = {nw: float(fits[(fits['gamma_lev'] == GAMMA_LEV_3D[0])
                            & (fits['n_warmup'] == nw)]['alarm_ml'].mean())
             for nw in N_WARMUP_3D}
    print(f"  envelope {100 * min(rates.values()):.1f}% -- {100 * max(rates.values()):.1f}%, "
          f"against v87's printed 3--8%")
    for i, a in enumerate(N_WARMUP_3D):
        for b in N_WARMUP_3D[i + 1:]:
            first = fits[(fits['gamma_lev'] == GAMMA_LEV_3D[0]) & (fits['n_warmup'] == a)] \
                .sort_values('stream')['alarm_ml'].to_numpy(dtype=bool)
            second = fits[(fits['gamma_lev'] == GAMMA_LEV_3D[0]) & (fits['n_warmup'] == b)] \
                .sort_values('stream')['alarm_ml'].to_numpy(dtype=bool)
            discordant_b = int(np.sum(second & ~first))
            discordant_c = int(np.sum(first & ~second))
            p = stats.binomtest(discordant_b, discordant_b + discordant_c, 0.5).pvalue \
                if discordant_b + discordant_c else float('nan')
            print(f"    {a:>5} vs {b:>5}: discordant {discordant_c} / {discordant_b}, "
                  f"exact paired p = {p:.4f}")
    print("=" * 78)


def test_R17_report_the_convergence_diagnostics_at_every_cell(warmup):
    print("\n" + "=" * 78)
    print("R17 -- what the delivered convergence flag does and does not see (control C1)")
    print("=" * 78)
    print(f"  {'g_lev':>6} {'nw':>5} {'nonconv':>9} {'=init':>8} {'at low':>9} {'at high':>9} "
          f"{'median a+b':>12}")
    for row in warmup.to_dict('records'):
        print(f"  {row['gamma_lev']:>6.2f} {row['n_warmup']:>5} "
              f"{row['share_nonconverged']:>9.4f} {row['share_equals_initialiser']:>8.4f} "
              f"{row['share_at_lower_bound']:>9.4f} {row['share_at_upper_bound']:>9.4f} "
              f"{row['persistence_median_pooled']:>12.6f}")
    print("  Every share is printed at every cell, zeros included: a counter reported only when")
    print("  it is non-zero establishes nothing about the cells where it is not.")
    print("=" * 78)
