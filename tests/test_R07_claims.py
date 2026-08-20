"""
R07 -- Evaluates foundational concept drift vulnerabilities encompassing estimated conditional mean architectures. Comprehensive validation protocols.

This module orchestrates three distinct methodological verification tiers, rigidly segregated to preserve inferential integrity.

1. Mandatory Blocking Assertions: These strict computational gates anchor onto explicitly printed literals from the manuscript (evaluated exactly at the stated typographical precision) or mandate conformity with mathematically deterministic identities reconstructed independently of the primary execution pipeline. For instance, we compute the discrete absorbing-chain probabilities utilizing explicit sparse transition matrices instead of reproducing the experiment's specific array slicing logic. None of these primary assertions depend functionally upon the operational outputs generated during runtime.

2. Contingent Falsification Checks: These dynamic assertions encode recognized methodological deviations. We evaluate these boundaries computing explicit z-scores against intrinsic standard errors rather than demanding arbitrary typographical equality. Because our mandated cryptographic re-keying fundamentally shifts every stochastic realization natively, defining an absolute numerical gate here guarantees an unresolvable failure cascade requiring unauthorized tolerance widening. Should subsequent protocol adjustments restore these parameters within expected analytical bounds, these specific tests trigger autonomously, prompting formal withdrawal of the deviation record.

3. Diagnostic Reporting Output: These functions persist observational mappings—including witness comparison matrices, Kish design-effect calculations, counterfactual mechanism ladders, and alternative interpretations of the L308 dispersion cost numeral—without triggering conditional logic barriers. The reference witness frameworks exclusively populate the published baseline columns utilized within D0-D3 magnitude classifications. Elevating these historical artefacts to the status of blocking invariants would erroneously reclassify every legitimate methodological correction as a systemic failure.
"""

import ast
import math
import re
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "results" / "R07_estimated_mean" / "data"
FIGURES_DIR = ROOT / "results" / "R07_estimated_mean" / "figures"
TABLES_DIR = ROOT / "results" / "R07_estimated_mean" / "tables"
REFERENCE_DIR = ROOT / "data" / "reference" / "R07"
SOURCE = ROOT / "experiments" / "R07_estimated_mean" / "exp_R07_estimated_mean.py"
LOG = ROOT / "logs" / "R07_estimated_mean" / "exp_R07_estimated_mean.log"
SECTION = ROOT / "docs" / "sections" / "R07.md"

PHI_GRID = (0.00, 0.02, 0.05, 0.075, 0.10, 0.125, 0.15)
N_OLS_GRID = (125, 250, 500, 1000)
ARM_ORDER = ('NAIVE', 'ORACLE', 'OLS-125', 'OLS-250', 'OLS-500', 'OLS-1000')
OLS_ARMS = tuple(arm for arm in ARM_ORDER if arm.startswith('OLS-'))
N_SEEDS = 10000
H = 5000
DELTA = 0.1
LATTICE_UNIT = 2.0 * DELTA
NOMINAL_LEVEL = 0.05
GARCH_ALPHA = 0.1058
GARCH_BETA = 0.8742
GARCH_NU = 7.0

# =====================================================================
# MANUSCRIPT ANCHORS -- LITERALLY TRANSCRIBED FROM articleB_whitening_v87.tex
# =====================================================================
# L308 theoretical bound delineations: "Ljung--Box rejection climbs from $5.1\%$ at $\phi = 0$ to $99.8\%$ at
# $\phi = 0.15$, dragging the \textsc{Concept} FPR to $20.8\%$. ... across the
# full $7 \times 4$ grid ... Ljung--Box rejection stays within $4.6$--$5.6\%$
# and FPR within $4.3$--$5.9\%$, matching the oracle bands on the same paths.
# ... the classical small-sample AR bias $\mathbb{E}[\hat{\phi}] - \phi \approx
# -2.5\,\phi/n$, stays under $2.9 \times 10^{-3}$, while the dispersion channel,
# whose RMSE reaches $11.4\%$ of $\sigma_{\mathrm{unc}}$ at $n = 125$, costs at
# most $0.4$ points of rejection. ... this holds on a DGP past the fourth-moment
# boundary ($\mathbb{E}[(\alpha z_t^2 + \beta)^2] = 1.005 > 1$)"
V87_NAIVE_LB_AT_PHI_ZERO = 0.051
V87_NAIVE_LB_AT_PHI_MAX = 0.998
V87_NAIVE_FPR_AT_PHI_MAX = 0.208
V87_OLS_LB_ENVELOPE = (0.046, 0.056)
V87_OLS_FPR_ENVELOPE = (0.043, 0.059)
V87_BIAS_BOUND = 2.9e-3
V87_ETA_AT_N125 = 0.114
V87_DISPERSION_COST_POINTS = 0.4
V87_MOMENT_PRODUCT = 1.005

# L241 manuscript operating levels: "the levels bracketing $5\%$ are $5.03\%$ at
# $\lambda = 11.2$ and $4.29\%$ at $\lambda = 11.4$ ($2 \times 10^5$ fair-coin
# streams); we take the nearest attainable level at or below nominal,
# $\lambda^{\star} = 11.4$."
V87_LAMBDA_STAR = 11.4
V87_LATTICE_LOW = 0.0429
V87_LATTICE_HIGH = 0.0503

# =====================================================================
# METHODOLOGICAL TOLERANCES DEFINING EXACT COMPUTATIONAL BOUNDARIES
# =====================================================================
FLOAT64_EPS = float(np.finfo(np.float64).eps)

# The analytical lattice law represents a mass-preserving forward structural recursion spanning exactly H = 5000 operational steps. 
# While the operational experiment executes continuous array slicing, our verification framework deploys an explicit sparse transition matrix. 
# Both approaches fundamentally differ exclusively regarding summation associativity resolving convex mathematical combinations. 
# Consequently, cumulative precision displacement cannot exceed 4 * H * eps natively.
LATTICE_ATOL = 4.0 * H * FLOAT64_EPS

# The rigorous Wilson score interval materializes utilizing two distinct algebraic formulations structurally. 
# Comparing explicit fractional representations against our quadratic root solutions yields trivial mantissa reassociation variances bounded natively by 5 * eps. 
# Allocating a conservative 1e-12 threshold ensures absolute tolerance robustness capturing three orders of precision margin effortlessly.
CLOSED_FORM_RTOL = 1e-12

# Delineates rigorous spatial constraints defining acceptable OLS performance variations against perfectly measured ORACLE benchmarks. 
# Enforcing four standard errors characterizing the strictly paired difference mathematically yields an asymptotic family-wise trigger probability peaking at 1 - (1 - 6.334e-5)^28 = 0.177%. 
# Because identical initialization keys induce profound positive covariance structures dynamically, this probability constitutes a definitive theoretical upper bound.
BAND_Z = 4.0

# Mathematical z-score boundary classifying ordinary statistical fluctuations distinctly apart from fundamental architectural deviations. 
# Derived strictly observing the 0.27% two-sided normal distribution tails intrinsically.
FINDING_Z = 3.0

MACRO_PREFIX = "RSeven"
MACRO_HEADER = "% Auto-generated by exp_R07_estimated_mean.py -- do not edit."

BANNED_CONFIRMATORY = (r'proves|proven|perfectly valid|validates the (theorem|thesis|claim)'
                       r'|confirms the|as expected|triumph|victory|irrefutable|brilliant')


def _read(path):
    assert path.exists(), f"Critical artefact missing: {path}"
    return pd.read_csv(path, float_precision='round_trip')


@pytest.fixture
def lb_fpr():
    return _read(DATA_DIR / "R07_estmean_lb_fpr.csv")


@pytest.fixture
def diagnostics():
    return _read(DATA_DIR / "R07_estmean_diagnostics.csv")


@pytest.fixture
def lattice():
    return _read(DATA_DIR / "R07_lattice_exact_law.csv")


@pytest.fixture
def design_effect():
    return _read(DATA_DIR / "R07_design_effect.csv")


@pytest.fixture
def eta_scaling():
    return _read(DATA_DIR / "R07_eta_scaling.csv")


@pytest.fixture
def counterfactual():
    return _read(DATA_DIR / "R07_eta_scaling_counterfactual.csv")


@pytest.fixture
def witness_lb_fpr():
    return _read(REFERENCE_DIR / "protocol_21a_estmean_lb_fpr.csv")


@pytest.fixture
def witness_diagnostics():
    return _read(REFERENCE_DIR / "protocol_21b_estmean_diagnostics.csv")


@pytest.fixture
def macros():
    path = TABLES_DIR / "R07_claims.tex"
    assert path.exists(), f"Critical artefact missing: {path}"
    text = path.read_text()
    assert text.endswith("\n"), ("Methodological invariant preamble S6 mandates absolute terminal newlines ensuring reliable concatenation protocols assembling final distribution packages.")
    lines = text.rstrip("\n").split("\n")
    assert lines[0] == MACRO_HEADER, f"Structural macro header divergence: detected {lines[0]!r}, strictly expected {MACRO_HEADER!r}"
    out = {}
    for line in lines[1:]:
        if line.startswith("%"):
            continue
        match = re.fullmatch(r"\\newcommand\{\\([A-Za-z]+)\}\{(.*)\}", line)
        assert match is not None, f"Encountered invalid non-compliant macro declaration: {line!r}"
        out[match.group(1)] = match.group(2)
    return out


# =====================================================================
# ORTHOGONAL RECONSTRUCTION EXAMINING FUNDAMENTAL LATTICE DYNAMICS
# =====================================================================

def independent_lattice_exceedance(horizon, lam_units):
    """
    Computes precise probabilistic survivorship P(M_H > lam_units) operating strictly within the discrete 2delta arithmetic lattice. 
    We articulate this mechanism constructing explicit sparse transition matrices characterizing enumerated joint parameter spaces, 
    intentionally bypassing the primary operational array slicing logic. This orthogonal mathematical formulation guarantees independent architectural verification.
    """
    size = (lam_units + 1) ** 2
    rows, cols, vals = [], [], []
    absorbing = size
    for a in range(lam_units + 1):
        for b in range(lam_units + 1):
            source = a * (lam_units + 1) + b
            for up_is_pos in (True, False):
                if up_is_pos:
                    a_next, b_next = a + 2, max(0, b - 3)
                else:
                    a_next, b_next = max(0, a - 3), b + 2
                if a_next > lam_units or b_next > lam_units:
                    target = absorbing
                else:
                    target = a_next * (lam_units + 1) + b_next
                rows.append(source)
                cols.append(target)
                vals.append(0.5)
    rows.append(absorbing)
    cols.append(absorbing)
    vals.append(1.0)
    transition = np.zeros((size + 1, size + 1), dtype=np.float64)
    np.add.at(transition, (np.asarray(rows), np.asarray(cols)), np.asarray(vals))
    state = np.zeros(size + 1, dtype=np.float64)
    state[0] = 1.0
    for _ in range(horizon):
        state = state @ transition
    return float(state[absorbing])


def wilson_second_form(k, n, z=1.959963984540054):
    """
    Analytically derives rigorous Wilson score boundaries extracting quadratic roots directly from fundamental asymptotic score equations. 
    Implementing this orthogonal algebraic pathway isolates mathematical verification protocols completely from the experiment's native center-and-margin computations.
    """
    p = k / n
    a = 1.0 + z * z / n
    b = -(2.0 * p + z * z / n)
    c = p * p
    disc = b * b - 4.0 * a * c
    root = math.sqrt(max(0.0, disc))
    return (-b - root) / (2.0 * a), (-b + root) / (2.0 * a)


# =====================================================================
# METHODOLOGICAL BLOCKING ASSERTIONS SECURING MANUSCRIPT PROJECTIONS
# =====================================================================

def test_R07_every_artefact_the_plan_lists_exists_with_its_prescribed_schema(
        lb_fpr, diagnostics, lattice, design_effect, eta_scaling, counterfactual):
    """Rigorous schema enforcement tracking precise parameter dimensionalities confirming absolute absence encompassing missing NaN values."""
    assert list(lb_fpr.columns) == ['phi', 'arm', 'n_ols', 'N_seeds', 'lb_reject_rate',
                                    'lb_ci_low', 'lb_ci_high', 'fpr_concept', 'fpr_ci_low',
                                    'fpr_ci_high', 'lb_pvalue_binom', 'fpr_pvalue_binom']
    assert len(lb_fpr) == len(PHI_GRID) * len(ARM_ORDER) == 42
    assert list(diagnostics.columns) == ['phi', 'n_ols', 'eta_rmse_over_sigma', 'eta_se',
                                         'eta_ci_low', 'eta_ci_high', 'mean_phi_hat',
                                         'sd_phi_hat', 'bias_phi_hat', 'bias_phi_hat_se']
    assert len(diagnostics) == len(PHI_GRID) * len(N_OLS_GRID) == 28
    assert not diagnostics.isna().any().any()
    assert not lb_fpr.drop(columns=['n_ols']).isna().any().any()

    for i, phi in enumerate(PHI_GRID):
        block = lb_fpr.iloc[i * len(ARM_ORDER):(i + 1) * len(ARM_ORDER)]
        assert list(block['arm']) == list(ARM_ORDER)
        assert np.allclose(block['phi'].to_numpy(), phi, rtol=0, atol=0)

    assert set(lattice['record_type']) == {'exact_survival', 'enumeration_validation',
                                           'float_drift'}
    assert set(design_effect['block']) == {'ORACLE', 'NAIVE', 'OLS', 'ALL'}
    assert set(eta_scaling['scope']) == {'per_phi', 'pooled'}
    assert set(counterfactual['dgp_arm']) == {'t7_garch', 'gauss_garch', 'gauss_iid'}
    assert len(counterfactual) == 6
    assert (FIGURES_DIR / "fig07_estimated_mean.png").exists()
    
    for column in ('lb_ci_low', 'lb_ci_high', 'fpr_ci_low', 'fpr_ci_high'):
        assert lb_fpr[column].between(0.0, 1.0).all()
    for column in ('eta_ci_low', 'eta_ci_high'):
        assert diagnostics[column].between(0.0, 1.0).all()


def test_R07_the_lattice_law_reproduces_under_an_independent_dynamic_program(lattice):
    """
    Mandatory blocking verification confirming topological invariances defining continuous mass transport logic intrinsically.
    """
    survival = lattice[lattice['record_type'] == 'exact_survival']
    assert len(survival) > 0
    checked = 0
    for row in survival.itertuples(index=False):
        units = int(row.lambda_units)
        if units < 50 or units > 58:
            continue
        mine = independent_lattice_exceedance(H, units)
        assert abs(mine - row.exact_level) <= LATTICE_ATOL, (
            f"lambda = {units} lattice units: primary empirical extraction recorded {row.exact_level!r} whereas independent "
            f"Markov absorbing-chain projections returned {mine!r}. Measured deviation {abs(mine - row.exact_level):.3e} structurally "
            f"violates stringent accumulation bounds constrained mathematically under {LATTICE_ATOL:.3e}.")
        checked += 1
    assert checked >= 5


def test_R07_the_two_attainable_levels_bracket_five_percent_and_fix_lambda_star(lattice, macros):
    """
    Mandatory blocking validation re-deriving strict discrete decision algorithms anchoring precisely upon nominal significance parameters.
    """
    survival = lattice[lattice['record_type'] == 'exact_survival'].sort_values('lambda_units')
    levels = {int(row.lambda_units): float(row.exact_level)
              for row in survival.itertuples(index=False)}
    eligible = [u for u in sorted(levels) if levels[u] <= NOMINAL_LEVEL]
    assert eligible, "Algorithm isolated strictly zero spatial constraints bounding desired structural properties reliably."
    star = eligible[0]
    assert levels[star] <= NOMINAL_LEVEL <= levels[star - 1], (
        f"Critical theoretical failure identifying required discrete thresholds successfully enveloping {NOMINAL_LEVEL}: "
        f"measured boundary distributions indicate {levels[star]!r} against operational coordinate {levels[star - 1]!r}")
    assert star * LATTICE_UNIT == V87_LAMBDA_STAR
    assert macros['RSevenLambdaStar'] == f"{V87_LAMBDA_STAR:.1f}"
    
    assert independent_lattice_exceedance(H, star) <= NOMINAL_LEVEL
    assert independent_lattice_exceedance(H, star - 1) >= NOMINAL_LEVEL


def test_R07_the_dynamic_program_agrees_with_exhaustive_enumeration(lattice):
    """
    Mandatory blocking parity verification corroborating analytical absorbing-chain recursive mathematics directly against discrete binary permutations structurally.
    """
    checks = lattice[lattice['record_type'] == 'enumeration_validation']
    assert len(checks) >= 6
    assert (checks['abs_difference'] == 0.0).all(), (
        "Detected mathematical deviations mapping continuous transition models onto discrete binary permutations. "
        "Consequently, recursive algorithmic logic incorrectly approximates theoretically proven spatial realities.")
    for row in checks.itertuples(index=False):
        assert row.n_streams == 2 ** int(row.H)


def test_R07_the_fourth_moment_product_of_L308_reproduces_in_closed_form(counterfactual):
    """
    Mandatory blocking verification calculating fundamental asymptotic kurtosis constraints strictly validating continuous stability mathematically.
    """
    e_z4 = 3.0 * (GARCH_NU - 2.0) / (GARCH_NU - 4.0)
    assert e_z4 == 5.0
    product = GARCH_ALPHA ** 2 * e_z4 + 2.0 * GARCH_ALPHA * GARCH_BETA + GARCH_BETA ** 2
    assert product > 1.0
    assert round(product, 3) == V87_MOMENT_PRODUCT
    arm = counterfactual[counterfactual['dgp_arm'] == 't7_garch'].iloc[0]
    assert arm['e_z4'] == e_z4
    assert abs(arm['moment_product'] - product) <= CLOSED_FORM_RTOL * product
    
    gauss = counterfactual[counterfactual['dgp_arm'] == 'gauss_garch'].iloc[0]
    assert gauss['e_z4'] == 3.0
    assert gauss['alpha'] == arm['alpha'] and gauss['beta'] == arm['beta']
    assert gauss['persistence'] == arm['persistence']
    assert gauss['moment_product'] < 1.0


def test_R07_every_wilson_interval_is_the_score_interval_of_its_own_rate(lb_fpr):
    """Mandatory blocking metric validating structural symmetry connecting observed proportions flawlessly toward asymmetric interval projections."""
    for row in lb_fpr.itertuples(index=False):
        for rate, low, high in ((row.lb_reject_rate, row.lb_ci_low, row.lb_ci_high),
                                (row.fpr_concept, row.fpr_ci_low, row.fpr_ci_high)):
            k = int(round(rate * N_SEEDS))
            assert abs(k / N_SEEDS - rate) < 1e-12
            expected_low, expected_high = wilson_second_form(k, N_SEEDS)
            assert abs(low - expected_low) <= CLOSED_FORM_RTOL * max(1e-6, expected_low)
            assert abs(high - expected_high) <= CLOSED_FORM_RTOL * max(1e-6, expected_high)
            assert 0.0 <= low <= rate <= high <= 1.0


def test_R07_the_naive_arm_and_the_oracle_arm_coincide_at_phi_zero(lb_fpr, design_effect):
    """
    Mandatory blocking verification confirming theoretical identity boundaries characterizing operational convergence dynamically. 
    Eliminating conditional dependencies systematically enforces perfectly equivalent statistical extractions sequentially.
    """
    at_zero = lb_fpr[lb_fpr['phi'] == 0.0]
    naive = at_zero[at_zero['arm'] == 'NAIVE'].iloc[0]
    oracle = at_zero[at_zero['arm'] == 'ORACLE'].iloc[0]
    for column in ('lb_reject_rate', 'lb_ci_low', 'lb_ci_high',
                   'fpr_concept', 'fpr_ci_low', 'fpr_ci_high'):
        assert naive[column] == oracle[column], (
            f"Detected arithmetic discrepancy breaking necessary logical parity characterizing NAIVE and ORACLE architectures inherently: "
            f"measured NAIVE boundary {naive[column]!r} structurally diverges from explicit ORACLE resolution {oracle[column]!r}")


def test_R07_the_oracle_arm_is_exactly_phi_invariant(lb_fpr, design_effect):
    """
    Mandatory blocking verification corroborating absolute momentum parameter detachment ensuring continuous mathematical stationarity unconditionally. 
    Strict cryptographic seeding perfectly insulates stochastic environments maintaining precise statistical immutability natively.
    """
    oracle = lb_fpr[lb_fpr['arm'] == 'ORACLE']
    assert len(oracle) == len(PHI_GRID)
    for column in ('lb_reject_rate', 'fpr_concept', 'lb_ci_low', 'lb_ci_high',
                   'fpr_ci_low', 'fpr_ci_high', 'lb_pvalue_binom', 'fpr_pvalue_binom'):
        assert oracle[column].nunique() == 1, (
            f"Calculated statistical matrix {column} uncovers unresolvable phi-variance structurally negating ORACLE invariances definitively: "
            f"{oracle[column].to_list()}")
    for statistic in ('lb_reject', 'fpr_concept'):
        row = design_effect[(design_effect['block'] == 'ORACLE')
                            & (design_effect['statistic'] == statistic)].iloc[0]
        assert bool(row['columns_bit_identical'])
        assert row['rho_bar'] == 1.0
        assert row['design_effect'] == float(len(PHI_GRID))
        assert row['n_eff'] == float(N_SEEDS)


def test_R07_the_design_effect_is_measured_on_every_pooled_quantity(design_effect):
    """
    Mandatory blocking structural assurance implementing requisite covariance diagnostics quantifying intra-unit dependencies accurately.
    """
    assert len(design_effect) == 8
    for row in design_effect.itertuples(index=False):
        assert np.isfinite(row.design_effect) and row.design_effect >= 1.0
        assert row.n_observations == row.n_cells * row.n_trajectories
        assert 0.0 < row.n_eff <= row.n_observations
        assert row.se_inflation >= 1.0
        assert abs(row.se_inflation - math.sqrt(row.design_effect)) < 1e-9


def test_R07_the_ljungbox_rejection_of_L308_climbs_monotonically_in_phi(lb_fpr):
    """
    Mandatory blocking verification tracking precise continuous monotonic expansions dominating analytical progression architectures uniformly.
    """
    naive = lb_fpr[lb_fpr['arm'] == 'NAIVE'].sort_values('phi')
    rates = naive['lb_reject_rate'].to_numpy()
    assert np.all(np.diff(rates) > 0), f"Continuous trajectory assessments failed verifying strictly positive monotonic expansions characterizing operational rates: {rates}"
    fprs = naive['fpr_concept'].to_numpy()
    assert np.all(np.diff(fprs) > 0), f"Calculated Concept structural variances inherently violated expected contiguous parameter growths continuously: {fprs}"
    assert round(100.0 * rates[-1], 1) == round(100.0 * V87_NAIVE_LB_AT_PHI_MAX, 1), (
        f"Empirical execution resolved final boundary distributions measuring {100.0 * rates[-1]:.2f}%, critically conflicting alongside theoretically printed "
        f"L308 manuscript limits establishing {100.0 * V87_NAIVE_LB_AT_PHI_MAX:.1f}%.")


def test_R07_every_ols_cell_matches_the_oracle_band_of_the_figure7_caption(lb_fpr, design_effect):
    """
    Mandatory blocking constraint enforcing absolute paired mathematical stability ensuring generalized estimators perform accurately within theoretically bounded standard error intervals natively.
    """
    oracle_mean = float(lb_fpr[lb_fpr['arm'] == 'ORACLE']['fpr_concept'].mean())
    oracle_row = design_effect[(design_effect['block'] == 'ORACLE')
                               & (design_effect['statistic'] == 'fpr_concept')].iloc[0]
    oracle_se = math.sqrt(oracle_mean * (1 - oracle_mean) / float(oracle_row['n_eff']))
    ols = lb_fpr[lb_fpr['arm'].isin(OLS_ARMS)]
    assert len(ols) == 28
    worst = 0.0
    for row in ols.itertuples(index=False):
        cell_se = math.sqrt(row.fpr_concept * (1 - row.fpr_concept) / N_SEEDS)
        margin = BAND_Z * math.sqrt(cell_se ** 2 + oracle_se ** 2)
        gap = abs(row.fpr_concept - oracle_mean)
        worst = max(worst, gap / math.sqrt(cell_se ** 2 + oracle_se ** 2))
        assert gap <= margin, (
            f"Identified anomalous OLS performance drift located analytically at phi={row.phi!r} encompassing structure {row.arm}. "
            f"Measured divergence indicates {gap:.6f} absolute magnitude fundamentally exceeding rigorous {BAND_Z}-sigma paired bounds defined rigorously at {margin:.6f}.")
    
    naive = lb_fpr[(lb_fpr['arm'] == 'NAIVE') & (lb_fpr['phi'] == max(PHI_GRID))].iloc[0]
    naive_se = math.sqrt(naive['fpr_concept'] * (1 - naive['fpr_concept']) / N_SEEDS)
    z_naive = ((naive['fpr_concept'] - oracle_mean)
               / math.sqrt(naive_se ** 2 + oracle_se ** 2))
    assert z_naive > 20.0, (
        f"Rigorous analytical boundary checks exposed insufficient spatial separation characterizing NAIVE execution structures. Calculated divergence merely {z_naive:.1f} standard errors.")
    print(f"\n[R07] widest OLS-vs-ORACLE gap over the 28 cells: {worst:.2f} paired standard "
          f"errors, against a band of {BAND_Z}. NAIVE at phi = {max(PHI_GRID)}: "
          f"{z_naive:.1f} standard errors.")


def test_R07_the_ols_envelopes_stay_inside_the_two_bands_L308_prints(lb_fpr):
    """
    Mandatory blocking measurement guaranteeing explicit containment assertions exactly match theoretically recorded boundary parameters sequentially.
    """
    ols = lb_fpr[lb_fpr['arm'].isin(OLS_ARMS)]
    for column, (low, high) in (('lb_reject_rate', V87_OLS_LB_ENVELOPE),
                                ('fpr_concept', V87_OLS_FPR_ENVELOPE)):
        observed = (float(ols[column].min()), float(ols[column].max()))
        assert round(100.0 * observed[0], 1) >= round(100.0 * low, 1), (
            f"Evaluated continuous lower containment structures tracking dimension {column} inherently fell precisely to {100.0 * observed[0]:.2f}%, structurally breaching printed L308 minimum definitions at {100.0 * low:.1f}%.")
        assert round(100.0 * observed[1], 1) <= round(100.0 * high, 1), (
            f"Measured continuous maximum operational envelopes determining scalar variance regarding {column} reached effectively {100.0 * observed[1]:.2f}%, directly violating explicit theoretically recognized boundaries terminating fundamentally at {100.0 * high:.1f}%.")


def test_R07_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix(macros):
    """Mandatory blocking structural assurance parsing LaTeX deliverables natively capturing syntactic parameter invariants correctly."""
    assert macros, "Critical LaTeX artifact compilation failure extracting viable syntactic macros securely."
    for name in macros:
        assert name.startswith(MACRO_PREFIX), f"Discovered architectural non-compliance evaluating namespace prefix definition regarding macro {name}"
        assert not name.startswith("RSeventh"), f"Erroneous ordinal syntax implementation recognized incorrectly inside analytical declaration space referencing {name}"
    for required in ('RSevenLambdaStar', 'RSevenLatticeLow', 'RSevenLatticeHigh',
                     'RSevenNaiveFprAtPhiMax', 'RSevenOlsFprMin', 'RSevenOlsFprMax',
                     'RSevenOracleFprMean', 'RSevenLbRejectMax', 'RSevenEtaRmseExponent',
                     'RSevenEtaRmseExponentCI', 'RSevenOlsLbMin', 'RSevenOlsLbMax',
                     'RSevenBiasMax'):
        assert required in macros, f"Discovered critical missing foundational declarative macro {required}"
    for name, body in macros.items():
        assert 'nan' not in body.lower(), f"Fatal arithmetic singularity generated undefined computational expressions natively inside variable {name}"


def test_R07_the_macros_agree_with_the_frames_they_are_computed_from(
        macros, lb_fpr, diagnostics, lattice, eta_scaling):
    """Mandatory blocking analytical redundancy measuring structural alignment connecting final formatting components accurately."""
    ols = lb_fpr[lb_fpr['arm'].isin(OLS_ARMS)]
    oracle = lb_fpr[lb_fpr['arm'] == 'ORACLE']
    naive_max = lb_fpr[(lb_fpr['arm'] == 'NAIVE') & (lb_fpr['phi'] == max(PHI_GRID))].iloc[0]
    survival = {int(r.lambda_units): float(r.exact_level)
                for r in lattice[lattice['record_type'] == 'exact_survival'].itertuples(index=False)}
    star = int(round(V87_LAMBDA_STAR / LATTICE_UNIT))
    pooled = eta_scaling[(eta_scaling['scope'] == 'pooled')
                         & (eta_scaling['statistic'] == 'eta_rmse_over_sigma')].iloc[0]
    expected = {
        'RSevenLatticeLow': f"{100.0 * survival[star]:.2f}\\%",
        'RSevenLatticeHigh': f"{100.0 * survival[star - 1]:.2f}\\%",
        'RSevenNaiveFprAtPhiMax': f"{100.0 * naive_max['fpr_concept']:.1f}\\%",
        'RSevenOlsFprMin': f"{100.0 * ols['fpr_concept'].min():.1f}\\%",
        'RSevenOlsFprMax': f"{100.0 * ols['fpr_concept'].max():.1f}\\%",
        'RSevenOlsLbMin': f"{100.0 * ols['lb_reject_rate'].min():.1f}\\%",
        'RSevenOlsLbMax': f"{100.0 * ols['lb_reject_rate'].max():.1f}\\%",
        'RSevenOracleFprMean': f"{100.0 * oracle['fpr_concept'].mean():.2f}\\%",
        'RSevenLbRejectMax': f"{100.0 * oracle['lb_reject_rate'].max():.1f}\\%",
        'RSevenBiasMax': f"{1000.0 * diagnostics['bias_phi_hat'].abs().max():.1f} \\times 10^{{-3}}",
        'RSevenEtaRmseExponent': f"{pooled['exponent']:.4f}",
        'RSevenEtaRmseExponentCI': f"[{pooled['exponent_ci_low']:.4f}, "
                                   f"{pooled['exponent_ci_high']:.4f}]",
    }
    for name, body in expected.items():
        assert macros[name] == body, f"Mathematical divergence tracking output formatting string parameters strictly isolating discrepancy {name} evaluating observed {macros[name]!r} against mathematically verified {body!r}"


def test_R07_every_produced_text_file_ends_in_a_newline():
    """Mandatory blocking structural assurance guaranteeing POSIX compliant file termination uniformly."""
    for path in (SOURCE, TABLES_DIR / "R07_claims.tex", LOG, SECTION,
                 ROOT / "requirements" / "R07.txt", ROOT / "run_experiment_R07.sh",
                 *sorted(DATA_DIR.glob("*.csv"))):
        assert path.exists(), f"Critical artefact missing ensuring POSIX boundary verifications comprehensively: {path}"
        assert path.read_bytes().endswith(b"\n"), f"Detected malformed sequence missing necessary explicit terminating newline architectures fundamentally referencing {path}"


def test_R07_the_produced_sources_and_logs_carry_no_confirmatory_language():
    """Mandatory blocking protocol eradicating subjective emotional phrasing compromising strict neutral academic prose requirements inherently."""
    for path in (SOURCE, LOG, SECTION):
        assert path.exists(), f"Critical artefact missing isolating linguistic regulatory verifications accurately: {path}"
        result = subprocess.run(['grep', '-Ein', BANNED_CONFIRMATORY, str(path)],
                                capture_output=True, text=True)
        assert result.stdout == "", f"Systematically detected explicitly prohibited subjective linguistic formulations fundamentally contaminating structural outputs natively inside {path.name}:\n{result.stdout}"


def test_R07_the_produced_sources_carry_no_banned_construct():
    """
    Mandatory blocking analytical code inspection actively enforcing secure methodological conventions systematically natively rejecting anti-patterns dynamically.
    """
    text = SOURCE.read_text()
    assert 'iterrows()' not in text, "Methodological governance expressly forbids traversing structured DataFrames leveraging iterrows implicitly natively."
    assert '/home/' not in text, "Configuring operations involving explicitly hardcoded absolute directories compromises portability architectures."
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            assert node.type is not None, "Architectural standards universally reject unspecific broad exception handlers silently suppressing critical evaluations structurally."
            assert not all(isinstance(stmt, ast.Pass) for stmt in node.body), (
                "Implementation frameworks natively forbid establishing silent exception absorption pipelines effectively blinding operational monitoring.")


def test_R07_the_comparison_operator_is_the_same_on_both_paths():
    """
    Mandatory blocking deterministic evaluation inspecting module syntaxes actively ensuring identical relational translation sequences universally.
    """
    tree = ast.parse(SOURCE.read_text())
    functions = {node.name: node for node in ast.walk(tree)
                 if isinstance(node, ast.FunctionDef)}
    body = [node for node in functions['exceeds'].body
            if not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant))]
    assert len(body) == 1 and isinstance(body[0], ast.Return)
    compare = body[0].value
    assert isinstance(compare, ast.Compare) and len(compare.ops) == 1
    assert isinstance(compare.ops[0], ast.Gt), "Logical bounds must implement continuous rigid inequalities enforcing explicitly strict ast.Gt relational boundaries perfectly."
    for routine in ('calibrate_and_validate', 'worker'):
        calls = {node.func.id for node in ast.walk(functions[routine])
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        assert 'exceeds' in calls, f"Detected structural implementation failing necessary mandatory logic encapsulation constraints executing within procedural function {routine}"


def test_R07_the_seven_carried_primitives_are_byte_identical_to_the_witness():
    """
    Mandatory blocking deterministic constraint asserting flawless cryptographic preservation connecting specific designated baseline mechanisms absolutely flawlessly.
    """
    witness_path = REFERENCE_DIR / "Priorite_21_estimated_mean_robustness.py"
    assert witness_path.exists()

    def segments(path, names):
        text = Path(path).read_text()
        tree = ast.parse(text)
        return {node.name: ast.get_source_segment(text, node) for node in tree.body
                if isinstance(node, ast.FunctionDef) and node.name in names}

    names = {'wilson_ci', 'lb_pvalue', 'compute_phi_hat_naive', 'compute_phi_hat_vectorized',
             'cusum_concept_fast', 'check_anti_look_ahead', 'generate_dgp'}
    witness = segments(witness_path, names)
    mine = segments(SOURCE, names)
    assert set(witness) == names and set(mine) == names
    for name in sorted(names):
        assert mine[name] == witness[name], f"Detected fundamental cryptographic drift separating natively transcribed logic completely characterizing algorithm {name}"


# =====================================================================
# CONTINGENT FALSIFICATION CHECKS -- EVALUATING EXPLICIT NORMAL DEVIATIONS
# =====================================================================

def _binomial_z(observed, reference, n=N_SEEDS):
    return (observed - reference) / math.sqrt(reference * (1 - reference) / n)


def test_R07_the_three_monte_carlo_numerals_of_L308_move_within_their_own_sampling_error(
        lb_fpr, diagnostics):
    """
    Contingent falsification framework. Implementing explicit 128-bit seeding structurally shifts historical Monte-Carlo parameters deterministically. 
    Evaluating variations analyzing intrinsic standard error deviations establishes empirical continuity boundaries authentically preserving analytical integrity inherently.
    """
    naive = lb_fpr[lb_fpr['arm'] == 'NAIVE'].sort_values('phi')
    checks = [
        ("L308 Ljung-Box rejection at phi = 0", float(naive.iloc[0]['lb_reject_rate']),
         V87_NAIVE_LB_AT_PHI_ZERO, _binomial_z(float(naive.iloc[0]['lb_reject_rate']),
                                               V87_NAIVE_LB_AT_PHI_ZERO)),
        ("L308 Concept FPR at phi = 0.15", float(naive.iloc[-1]['fpr_concept']),
         V87_NAIVE_FPR_AT_PHI_MAX, _binomial_z(float(naive.iloc[-1]['fpr_concept']),
                                               V87_NAIVE_FPR_AT_PHI_MAX)),
    ]
    at_125 = diagnostics[diagnostics['n_ols'] == 125]
    peak = at_125.iloc[int(at_125['eta_rmse_over_sigma'].to_numpy().argmax())]
    checks.append(("L308 eta at n = 125", float(peak['eta_rmse_over_sigma']), V87_ETA_AT_N125,
                   (float(peak['eta_rmse_over_sigma']) - V87_ETA_AT_N125) / float(peak['eta_se'])))
    print("")
    for label, observed, printed, z in checks:
        print(f"[R07] {label}: v87 prints {printed!r}, regenerated {observed!r}, z = {z:+.2f}")
    for label, observed, printed, z in checks:
        assert abs(z) <= FINDING_Z, (
            f"Empirical divergence tracking parameter {label} identified explicit baseline deviations. Theoretical {printed!r} "
            f"juxtaposed mathematically representing regenerated {observed!r} establishes profound {z:+.2f} standard errors shift. "
            f"Exceeding rigorous {FINDING_Z} sigma boundaries officially dictates formal methodological reporting constraints comprehensively.")


def test_R07_the_bias_bound_of_L308_is_exceeded_by_the_regenerated_campaign(diagnostics):
    """
    Contingent falsification framework establishing strict D3 structural manifestations explicitly confirming specific bound deviations reliably.
    """
    worst_index = int(diagnostics['bias_phi_hat'].abs().to_numpy().argmax())
    worst = diagnostics.iloc[worst_index]
    observed = abs(float(worst['bias_phi_hat']))
    se = float(worst['bias_phi_hat_se'])
    predicted = 2.5 * float(worst['phi']) / float(worst['n_ols'])
    print(f"\n[R07] L308 bias bound: v87 states < {V87_BIAS_BOUND:g}; the largest "
          f"|E[phi_hat] - phi| is {observed!r} +/- {se!r} at phi = {worst['phi']!r}, "
          f"n_ols = {int(worst['n_ols'])}, i.e. {(observed - V87_BIAS_BOUND) / se:+.2f} standard "
          f"errors past the bound and {(observed - predicted) / se:+.2f} from the {predicted:g} "
          f"that v87's own -2.5 phi / n predicts there.")
    assert float(worst['phi']) == max(PHI_GRID) and int(worst['n_ols']) == min(N_OLS_GRID), (
        "Detected architectural spatial displacement confirming explicit analytical extrema deviations identifying divergent functional behaviors consistently.")
    assert observed > V87_BIAS_BOUND, (
        f"Structural parameter updates correctly re-established mathematical convergence stabilizing precisely below {V87_BIAS_BOUND:g} theoretically. "
        f"Consequently, prior formal deviation assertions completely invalidate dynamically eliminating necessary manual constraint modifications entirely.")


def test_R07_the_exact_lattice_levels_differ_from_the_two_numerals_v87_prints(lattice):
    """
    Contingent falsification framework authenticating precise empirical boundary disparities highlighting inherent continuous estimation offsets sequentially.
    """
    survival = {int(r.lambda_units): float(r.exact_level)
                for r in lattice[lattice['record_type'] == 'exact_survival'].itertuples(index=False)}
    star = int(round(V87_LAMBDA_STAR / LATTICE_UNIT))
    exact_low, exact_high = survival[star], survival[star - 1]
    se = math.sqrt(exact_low * (1 - exact_low) / 200000)
    print(f"\n[R07] exact lattice levels: {100.0 * exact_low:.4f}% at lambda = {V87_LAMBDA_STAR} "
          f"against the {100.0 * V87_LATTICE_LOW:.2f}% v87 prints "
          f"({(V87_LATTICE_LOW - exact_low) / se:+.2f} Monte-Carlo standard errors of a 2x10^5 "
          f"basis), and {100.0 * exact_high:.4f}% at lambda = {(star - 1) * LATTICE_UNIT:.1f} "
          f"against {100.0 * V87_LATTICE_HIGH:.2f}%.")
    assert round(100.0 * exact_low, 2) != round(100.0 * V87_LATTICE_LOW, 2)
    assert round(100.0 * exact_high, 2) != round(100.0 * V87_LATTICE_HIGH, 2)
    assert exact_low > V87_LATTICE_LOW and exact_high > V87_LATTICE_HIGH


def test_R07_the_eta_decay_is_not_one_over_root_n(eta_scaling):
    """
    Contingent falsification framework documenting anomalous algorithmic convergence structures actively tracking significant analytical boundary alterations sequentially natively.
    """
    pooled = eta_scaling[(eta_scaling['scope'] == 'pooled')
                         & (eta_scaling['statistic'] == 'eta_rmse_over_sigma')].iloc[0]
    print(f"\n[R07] eta exponent {pooled['exponent']!r} 95% "
          f"[{pooled['exponent_ci_low']!r}, {pooled['exponent_ci_high']!r}], "
          f"{pooled['z_against_minus_half']:+.1f} standard errors from -0.5.")
    assert pooled['exponent_ci_low'] > -0.5 or pooled['exponent_ci_high'] < -0.5, (
        "Empirical decay distributions successfully repositioned explicitly encompassing theoretically correct 1/sqrt(n) boundaries formally. "
        "Rigorous comprehensive reassessment investigating underlying phenomenological variables currently mandatory systematically determining accurate experimental consequences.")
    assert abs(pooled['z_against_minus_half']) > FINDING_Z
    per_phi = eta_scaling[(eta_scaling['scope'] == 'per_phi')
                          & (eta_scaling['statistic'] == 'eta_rmse_over_sigma')]
    assert len(per_phi) == len(PHI_GRID)
    assert (per_phi['exponent'] > -0.5).all(), (
        f"Detected explicit mathematical boundary violations demonstrating inconsistent localized scaling parameters structurally measuring exponents critically: {per_phi['exponent'].to_list()}")


# =====================================================================
# DIAGNOSTIC REPORTING OUTPUT -- AVOIDING IMPLICIT ARBITRARY ASSERTIONS
# =====================================================================

def test_R07_report_the_campaign_against_its_witness(lb_fpr, diagnostics, witness_lb_fpr,
                                                     witness_diagnostics):
    """
    Diagnostic reporting function compiling comprehensive comparative grids measuring detailed algorithmic transformations natively without instituting artificial error triggers formally.
    """
    merged = lb_fpr.merge(witness_lb_fpr, on=['phi', 'arm'], suffixes=('_new', '_witness'))
    assert len(merged) == len(lb_fpr)
    print("\n[R07] witness comparison, protocol_21a -> R07_estmean_lb_fpr:")
    for row in merged.itertuples(index=False):
        print(f"  phi = {row.phi:<6} {row.arm:<9} lb {row.lb_reject_rate_witness:.4f} -> "
              f"{row.lb_reject_rate_new:.4f}   fpr {row.fpr_concept_witness:.4f} -> "
              f"{row.fpr_concept_new:.4f}")
    merged_b = diagnostics.merge(witness_diagnostics, on=['phi', 'n_ols'],
                                 suffixes=('_new', '_witness'))
    assert len(merged_b) == len(diagnostics)
    print("[R07] witness comparison, protocol_21b -> R07_estmean_diagnostics:")
    for row in merged_b.itertuples(index=False):
        print(f"  phi = {row.phi:<6} n = {int(row.n_ols):<5} eta "
              f"{row.eta_rmse_over_sigma_witness:.6f} -> {row.eta_rmse_over_sigma_new:.6f}   "
              f"mean_phi_hat {row.mean_phi_hat_witness:+.6f} -> {row.mean_phi_hat_new:+.6f}")


def test_R07_report_the_design_effect_of_every_pooled_quantity(design_effect):
    """Diagnostic reporting function mapping detailed internal covariance calculations structurally determining valid effective sample sizes intrinsically."""
    print("\n[R07] design effect, measured before any pooled interval:")
    for row in design_effect.itertuples(index=False):
        print(f"  {row.block:<7} {row.statistic:<12} m = {row.n_cells:<3} rho_bar = "
              f"{row.rho_bar:+.6f}  deff = {row.design_effect:8.4f}  n_eff = {row.n_eff:10.2f}  "
              f"SE inflation x{row.se_inflation:.4f}")


def test_R07_report_the_counterfactual_ladder(counterfactual):
    """
    Diagnostic reporting function compiling analytical mechanism ladders separating orthogonal perturbation parameters meticulously ensuring distinct exploratory variable tracking.
    """
    print("\n[R07] C8 mechanism ladder (audit-only):")
    for row in counterfactual.itertuples(index=False):
        contains_half = (row.eta_exponent_ci_low <= -0.5 <= row.eta_exponent_ci_high)
        print(f"  {row.dgp_arm:<12} phi = {row.phi:<6} {row.innovation_law:<16} "
              f"persistence {row.persistence:.2f}  E[(az^2+b)^2] = {row.moment_product:.6f}  "
              f"eta exponent {row.eta_exponent:+.4f} +/- {row.eta_exponent_se:.4f}  "
              f"interval contains -0.5: {contains_half}")


def test_R07_report_the_candidate_readings_of_the_dispersion_cost_numeral(lb_fpr):
    """
    Diagnostic reporting function tracking ambiguous manuscript identifiers accurately exploring plausible mathematical translations completely preventing unwarranted analytical exclusions.
    """
    table = lb_fpr.pivot_table(index='phi', columns='arm', values='lb_reject_rate')
    ols = table[list(OLS_ARMS)]
    readings = {
        'max over phi of (max OLS - ORACLE) at the same phi':
            float((ols.max(axis=1) - table['ORACLE']).max()) * 100.0,
        'max OLS anywhere - max ORACLE anywhere':
            float(ols.to_numpy().max() - table['ORACLE'].max()) * 100.0,
        'max OLS anywhere - mean ORACLE over the grid':
            float(ols.to_numpy().max() - table['ORACLE'].mean()) * 100.0,
        'max over phi of the spread across the four windows':
            float((ols.max(axis=1) - ols.min(axis=1)).max()) * 100.0,
        'max OLS anywhere - the 5% nominal level':
            float(ols.to_numpy().max() - 0.05) * 100.0,
        'max OLS anywhere - min OLS anywhere':
            float(ols.to_numpy().max() - ols.to_numpy().min()) * 100.0,
    }
    print(f"\n[R07] candidate readings of L308's "
          f"{V87_DISPERSION_COST_POINTS} points of rejection:")
    for name, value in readings.items():
        print(f"  {value:6.4f} points (rounds to {value:.1f})  --  {name}")
    matched = [name for name, value in readings.items()
               if abs(round(value, 1) - V87_DISPERSION_COST_POINTS) < 1e-9]
    print(f"  readings that round to {V87_DISPERSION_COST_POINTS}: "
          f"{matched if matched else 'none'}")


def test_R07_report_the_float_drift_on_the_lattice_boundary(lattice):
    """
    Diagnostic reporting function compiling distinct boundary disparity metrics translating continuous arithmetic noise profiles reliably comparing analytical strict operators correctly.
    """
    drift = lattice[lattice['record_type'] == 'float_drift']
    print("\n[R07] realised level of each operator, per stream set:")
    for row in drift.itertuples(index=False):
        print(f"  {row.operator:<45} n = {int(row.n_streams):<6} level = {row.realised_level:.6f}"
              f"  disagreements with the strict operator: {int(row.disagreements)}")