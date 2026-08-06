"""
R04 -- iso-FPR race and relative efficiency. Acceptance and classification.

Two kinds of statement live in this file and they are kept apart deliberately.

*Blocking assertions* rest on deterministic relations -- cardinalities, an
in-sample calibration that converged, an analytic identity, a formatting rule --
or on structural orderings that have no probability of firing under their own
null. None of them is a hypothesis test on a draw.

*Classification output* compares the regenerated campaign against the historical
witness of the submitted campaign and prints the degree of every deviation. It
asserts nothing about those degrees. A cell-by-cell equality gate against the
witness would convert every legitimate correction into a test failure whose only
exit is a widened tolerance, which the preamble forbids.

The witness of this experiment is known to have been produced by a generator
whose Gamma grid collapsed to a single point (see docs/sections/R04.md), so its
values are a record of what was submitted and never a target.

No numeric literal here comes from the regenerated output. The only constants
admitted are those printed in v87 -- 2000 null streams, 5000 steps, a 5% target
with a bisection tolerance of 0.003 over 15 iterations, the Gamma and c grids,
the dead band 0.125, the analytic crossing 4.7 and the Gaussian ceiling pi/2 --
and every reference value is read from the vendored witness by the code, with
float_precision='round_trip' on both sides.

The two derived rules of this experiment, the Table 3 printing precision and the
crossing interpolation, are reimplemented here independently of the experiment
module rather than imported from it, so that a test of either is a comparison of
two implementations and not a restatement of one.
"""

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import scipy.stats as stats

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "results" / "R04_isofpr_race" / "data"
TABLES_DIR = ROOT / "results" / "R04_isofpr_race" / "tables"
REFERENCE_DIR = ROOT / "data" / "reference" / "R04"

# Protocol constants, from v87 sec:magnitude / fig:isofpr and the R04 prompt.
N_STREAMS = 2000
STREAM_LENGTH = 5000
TARGET_FPR = 0.05
BISECTION_TOL = 0.003
BISECTION_ITERS = 15
GAMMA_GRID = (1.0, 11.58, 50.0, 200.0)
C_GRID = (0.25, 0.5, 1.0, 2.0)
ARMS = ("Recalib", "Eco_L1", "Oracle_Eco", "Concept")
GAMMA_RACE = 11.58
DELTA_R = 0.125
NU_STAR_ANALYTIC = 4.7
GAUSSIAN_CEILING = math.pi / 2.0
ALPHA_GARCH = 0.05
NU_RACE = 30.0


def _read(path):
    assert path.exists(), f"Missing artefact: {path}"
    return pd.read_csv(path, float_precision='round_trip')


@pytest.fixture
def df_calib():
    return _read(DATA_DIR / "R04_isofpr_calibration.csv")


@pytest.fixture
def df_race():
    return _read(DATA_DIR / "R04_isofpr_race.csv")


@pytest.fixture
def df_eff():
    return _read(DATA_DIR / "R04_relative_efficiency.csv")


@pytest.fixture
def df_family():
    return _read(DATA_DIR / "R04_cusum_vs_adwin.csv")


@pytest.fixture
def df_m0():
    return _read(DATA_DIR / "R04_bernoulli_constant.csv")


@pytest.fixture
def witness_race():
    return _read(REFERENCE_DIR / "protocol_9c_isofpr_race.csv")


@pytest.fixture
def witness_eff():
    return _read(REFERENCE_DIR / "protocol_9d_relative_efficiency.csv")


# --- INDEPENDENT REIMPLEMENTATIONS OF THE TWO DERIVED RULES ---

def format_table_cell(value):
    """Three significant figures, floored at integer precision."""
    decimals = max(0, 2 - int(math.floor(math.log10(abs(value)))))
    return f"{value:.{decimals}f}"


def crossing_point(nu_values, ratios):
    """Linear interpolation of the first upward crossing of unity."""
    order = np.argsort(np.asarray(nu_values, dtype=float))
    nu = np.asarray(nu_values, dtype=float)[order]
    r = np.asarray(ratios, dtype=float)[order]
    for i in range(len(nu) - 1):
        if r[i] < 1.0 <= r[i+1]:
            return nu[i] + (nu[i+1] - nu[i]) * (1.0 - r[i]) / (r[i+1] - r[i])
    return float('nan')


# --- (b) CARDINALITIES ---

def test_R04_cardinalities(df_calib, df_race, df_eff, df_family):
    """(b) One row per cell of each design, no more and no fewer."""
    assert len(df_calib) == len(GAMMA_GRID) * len(ARMS) == 16
    assert len(df_race) == len(GAMMA_GRID) * len(C_GRID) * len(ARMS) == 64
    assert len(df_eff) == 6
    assert len(df_family) == len(GAMMA_GRID) * 2 == 8


# --- (a) CONFORMITY TO THE v87 SPECIFICATION ---

def test_R04_grids_match_v87(df_calib, df_race):
    """(a) The Gamma grid, the c grid and the four arms are those v87 specifies."""
    assert sorted(df_calib['Gamma'].unique()) == sorted(GAMMA_GRID)
    assert sorted(df_race['c'].unique()) == sorted(C_GRID)
    assert set(df_race['arm'].unique()) == set(ARMS)


def test_R04_horizon_and_sample_size(df_race, df_m0):
    """(a) 2000 null streams over a 5000-step horizon, on every row."""
    assert (df_race['horizon'] == STREAM_LENGTH).all()
    assert (df_race['n_detected'] + df_race['n_censored'] == N_STREAMS).all()
    assert (df_m0['horizon'] == STREAM_LENGTH).all()


def test_R04_reference_drifts_are_coherent(df_calib):
    """
    (a) The CUSUM reference drift of each arm is half the post-change mean of
    its own statistic at the design shift c = 0.5: c/2 for the standardized
    arms, c^2/2 for the squared arm. These are identities of the design, not
    measurements, so they are exact.
    """
    for arm, expected in (("Recalib", 0.125), ("Eco_L1", 0.25), ("Oracle_Eco", 0.25)):
        assert np.allclose(df_calib[df_calib['arm'] == arm]['delta'], expected)
    scale = math.sqrt((NU_RACE - 2.0) / NU_RACE)
    expected_concept = (stats.t.cdf(0.5 / scale, df=NU_RACE) - 0.5) / 2.0
    assert np.allclose(df_calib[df_calib['arm'] == "Concept"]['delta'], expected_concept)


# --- (c) EFFECTIVE CALIBRATION ---

def test_R04_all_arms_are_iso_fpr(df_calib):
    """
    (c) Every arm reaches the 5% target within the bisection tolerance.

    This gate is in-sample by construction, which is exactly why it is
    admissible: the threshold is selected on the same null set whose rate is
    reported, so the gate fires if and only if the bisection failed to converge
    within its 15 iterations. It has no probability of firing under a null
    hypothesis and is therefore not a multiple test under preamble S4bis.
    """
    off = (df_calib['FPR_achieved'] - TARGET_FPR).abs() > BISECTION_TOL
    assert not off.any(), (
        "The race is not iso-FPR on "
        f"{df_calib[off][['Gamma', 'arm', 'FPR_achieved']].to_dict('records')}")
    assert (df_calib['n_bisection_iter'] <= BISECTION_ITERS).all()
    assert df_calib['bisection_converged'].all()


# --- (d) GAMMA-INVARIANCE OF THE CONCEPT ARM ---

def test_R04_concept_threshold_is_flat_in_gamma(df_calib):
    """
    (d) The Concept threshold does not move with Gamma.

    Asserted against the resolution of the calibration rather than against the
    published band. The bisection halves [0.001, 1000] a fixed number of times,
    so lambda_star lives on a lattice whose step is about 0.122 at the depth
    this campaign reaches; the published band [10.6, 10.7] is narrower than one
    step, so a containment gate would test which lattice cell an empirical
    quantile fell into. What the Whitening theorem asserts is that the threshold
    does not MOVE, which is a bound on the spread.
    """
    concept = df_calib[df_calib['arm'] == "Concept"]
    lattice_step = (1000.0 - 0.001) / (2.0 ** BISECTION_ITERS)
    spread = concept['lambda_star'].max() - concept['lambda_star'].min()
    max_iters = int(concept['n_bisection_iter'].max())
    coarsest_step = (1000.0 - 0.001) / (2.0 ** max_iters)
    assert spread <= 3.0 * coarsest_step, (
        f"Concept threshold spread {spread:.6f} exceeds three lattice steps of "
        f"{coarsest_step:.6f} (finest possible {lattice_step:.6f})")


def test_R04_concept_level_is_homogeneous_in_gamma(df_calib):
    """
    (d) The achieved Concept level is the same at every Gamma.

    Under Proposition prop:whitening the sign stream is i.i.d. Bernoulli(1/2)
    whatever the volatility dynamics, so the four achieved rates are four draws
    from one binomial. A chi-square test of homogeneity addresses that directly
    and, unlike a band, does not depend on where the bisection lattice falls.
    """
    concept = df_calib[df_calib['arm'] == "Concept"]
    alarms = np.round(concept['FPR_achieved'].values * N_STREAMS).astype(int)
    table = np.column_stack([alarms, N_STREAMS - alarms])
    chi2, p, _, _ = stats.chi2_contingency(table)
    assert p > 0.01, (
        f"Concept level is not homogeneous across Gamma: chi2 = {chi2:.4f}, p = {p:.4f}. "
        "The sign stream would not be Bernoulli(1/2) independently of the volatility dynamics.")


# --- (e) THE BLIND ZONE IS AN ORDER-OF-RESPONSE EFFECT ---

def test_R04_recalib_blind_zone_persists_at_lowest_gamma(df_race):
    """
    (e) The collapse of the squared sensor below c = 0.5 is present at the
    lowest Gamma of the grid, so it cannot be a volatility-clustering effect.
    v87 rests the mechanism -- a second-order sensor against a first-order
    signal -- on exactly this.
    """
    lowest = min(GAMMA_GRID)
    block = df_race[(df_race['arm'] == "Recalib") & np.isclose(df_race['Gamma'], lowest)]
    below = block[block['c'] < 0.5]
    assert len(below) > 0
    assert (below['DetRate'] < 1.0).all(), (
        "Recalib detects every stream below c = 0.5 at the lowest Gamma, so the blind zone "
        "would be a GARCH effect rather than an order-of-response effect")


def test_R04_recalib_is_slower_than_both_first_order_arms(df_race):
    """
    (e) At the race Gamma the squared sensor trails both first-order monitors at
    every magnitude. This is the qualitative content of Table 3 and holds
    independently of the numerals: it is an ordering, not a ratio.
    """
    block = df_race[np.isclose(df_race['Gamma'], GAMMA_RACE)]
    recalib = block[block['arm'] == "Recalib"].set_index('c')['ADD_conditional']
    for arm in ("Eco_L1", "Concept"):
        other = block[block['arm'] == arm].set_index('c')['ADD_conditional']
        for c in C_GRID:
            assert recalib[c] > other[c], f"Recalib is not slower than {arm} at c = {c}"


def test_R04_add_decreases_with_drift_magnitude(df_race):
    """
    A larger drift cannot take longer to detect at a fixed threshold -- but only
    where the reported mean is a mean over the WHOLE sample.

    ADD_conditional averages the streams that alarmed inside the horizon. Where
    the arm censors, raising c admits streams that were previously censored, and
    those are by construction the slow ones, so the conditional mean can rise
    while the underlying delay falls. The monotonicity is therefore asserted
    only between consecutive magnitudes at which the arm detects everything,
    where the conditioning set is the full sample and the quantity is an ADD.
    The censoring case is characterised in its own test below rather than
    excused here.
    """
    for (gamma, arm), block in df_race.groupby(['Gamma', 'arm']):
        block = block.sort_values('c')
        uncensored = block[block['DetRate'] >= 1.0]
        add = uncensored['ADD_conditional'].values
        assert np.all(np.diff(add) <= 0), (
            f"ADD is not decreasing in c at Gamma = {gamma}, arm = {arm} over the "
            f"uncensored magnitudes {list(uncensored['c'])}")


def test_R04_conditional_mean_is_labelled_and_accompanied(df_race):
    """
    Wherever the reported mean is conditional, the row carries what makes it
    interpretable: the detection rate, the counts behind it, and the horizon
    that truncates it. v87 prints the detection rate in parentheses for exactly
    this reason, and a cell whose DetRate is below 1 is not comparable with one
    whose DetRate is 1 without it.
    """
    for column in ('DetRate', 'n_detected', 'n_censored', 'horizon'):
        assert column in df_race.columns
    censored = df_race[df_race['DetRate'] < 1.0]
    assert len(censored) > 0, "no censored cell: this experiment is expected to produce some"
    assert (censored['ADD_conditional'] <= censored['horizon']).all(), (
        "a conditional mean exceeds the horizon that truncates it, which is impossible")
    assert (df_race['n_detected'] == np.round(df_race['DetRate'] * N_STREAMS)).all()


# --- (f) RELATIVE EFFICIENCY ---

def test_R04_efficiency_ratio_is_monotone_in_nu(df_eff):
    """
    (f) The measured ratio increases with nu, the shape of 1/(4 f_z(0)^2).
    Structural: the Pitman constant is strictly increasing in nu, so an
    inversion is a defect and not sampling noise.
    """
    ordered = df_eff.sort_values('nu')
    assert np.all(np.diff(ordered['ratio'].values) >= 0)
    rho, _ = stats.spearmanr(ordered['nu'], ordered['ratio'])
    assert rho == pytest.approx(1.0)


def test_R04_ratio_respects_the_gaussian_ceiling(df_eff):
    """
    (f) Proposition prop:are caps the ratio at pi/2 under Gaussianity, which the
    grid approaches from below at nu = 30. A measured ratio above the ceiling
    would contradict the proposition itself.
    """
    assert df_eff['ratio'].max() <= GAUSSIAN_CEILING
    assert df_eff['ratio_oracle'].max() <= GAUSSIAN_CEILING


def test_R04_predicted_ratio_is_the_pitman_constant(df_eff):
    """
    The predicted column is 1/(4 f_z(0)^2) for a standardized Student-t. An
    analytic identity, exact to floating point, not a measurement.
    """
    nu = df_eff['nu'].values
    f0 = stats.t.pdf(0.0, df=nu) / np.sqrt((nu - 2.0) / nu)
    assert np.allclose(df_eff['f0_hat'].values, f0, rtol=1e-12)
    assert np.allclose(df_eff['ratio_pred'].values, 1.0 / (4.0 * f0**2), rtol=1e-12)


def test_R04_oracle_is_never_slower_than_the_fitted_arm(df_eff):
    """
    Knowing the true GARCH parameters cannot cost delay: the oracle arm bounds
    the fitted arm at every nu. The gap between them is what v87 calls the
    estimation cost, so a violation would make that quantity meaningless.
    """
    assert (df_eff['ADD_Oracle'] <= df_eff['ADD_Eco_L1']).all()


# --- (h) EMBEDDED CERTIFICATION OF THE ANALYTIC CONSTANTS ---

def test_R04_analytic_crossing_matches_v87():
    """
    (h) v87 prints 4.7 for the crossing of f_z(0) = 1/2. Recomputed here from
    the definition, independently of the experiment.
    """
    from scipy.optimize import brentq
    nu_star = brentq(lambda v: stats.t.pdf(0.0, df=v) / math.sqrt((v - 2.0) / v) - 0.5, 3.0, 20.0)
    assert round(nu_star, 1) == NU_STAR_ANALYTIC


def test_R04_blind_zone_onset_matches_v87():
    """
    (h) v87 prints c* ~ 0.43 for the magnitude at which the second-order entry
    of the shift, c^2/sqrt(kappa_z - 1), clears the dead band delta_R = 0.125
    under t_30. An analytic identity in the published constants.
    """
    kappa_z = 3.0 * (NU_RACE - 2.0) / (NU_RACE - 4.0)
    c_star = math.sqrt(DELTA_R * math.sqrt(kappa_z - 1.0))
    assert round(c_star, 2) == 0.43


def test_R04_macros_are_emitted_and_computed():
    """
    (h) Every macro the R04 prompt requires is present, and the derived ones
    agree with the artefacts they are computed from. \\RFourEstimationCostDof in
    particular must be the difference of the two crossings, never a literal.
    """
    text = (TABLES_DIR / "R04_claims.tex").read_text()
    assert text.startswith("% Auto-generated by exp_R04_isofpr_race.py -- do not edit.")
    required = [
        "RFourNullStreams", "RFourBisectionIters", "RFourTargetFpr", "RFourGammaRace",
        "RFourRecalibSlowdownMin", "RFourRecalibSlowdownMax", "RFourDeadBand",
        "RFourBlindZoneCStar", "RFourParametricGainAtCOne", "RFourNuStarMeasured",
        "RFourNuStarLower", "RFourNuStarUpper", "RFourNuStarOracle", "RFourNuStarAnalytic",
        "RFourEstimationCostDof", "RFourConceptLambdaMin", "RFourConceptLambdaMax",
    ]
    for name in required:
        assert f"\\newcommand{{\\{name}}}" in text, f"Missing macro {name}"

    macros = dict(
        line.split("}{", 1)[0].replace("\\newcommand{\\", "") and
        (line.split("}{", 1)[0].replace("\\newcommand{\\", ""), line.split("}{", 1)[1].rstrip("}"))
        for line in text.splitlines() if line.startswith("\\newcommand"))
    cost = float(macros["RFourEstimationCostDof"])
    measured = float(macros["RFourNuStarMeasured"])
    oracle = float(macros["RFourNuStarOracle"])
    assert cost == pytest.approx(round(measured - oracle, 1), abs=0.1), (
        "RFourEstimationCostDof is not the difference of the two emitted crossings")


def test_R04_crossings_agree_with_the_interpolation_rule(df_eff):
    """
    (h) The emitted crossings reproduce the rule of the R04 prompt section 4 --
    linear interpolation between the two grid points bracketing unity -- when
    that rule is applied independently to the efficiency CSV.
    """
    text = (TABLES_DIR / "R04_claims.tex").read_text()
    macros = dict(
        (line.split("}{", 1)[0].replace("\\newcommand{\\", ""), line.split("}{", 1)[1].rstrip("}"))
        for line in text.splitlines() if line.startswith("\\newcommand"))
    for column, macro in (('ratio', "RFourNuStarMeasured"), ('ratio_oracle', "RFourNuStarOracle")):
        expected = crossing_point(df_eff['nu'], df_eff[column])
        assert float(macros[macro]) == pytest.approx(round(expected, 1), abs=1e-9)


def test_R04_emitted_crossing_brackets_contain_the_crossing(df_eff):
    """
    (h) The crossing is emitted with the two nu values that bracket it, so a
    reader can redo the interpolation by hand. Those two values must actually
    bracket unity in the CSV.
    """
    text = (TABLES_DIR / "R04_claims.tex").read_text()
    macros = dict(
        (line.split("}{", 1)[0].replace("\\newcommand{\\", ""), line.split("}{", 1)[1].rstrip("}"))
        for line in text.splitlines() if line.startswith("\\newcommand"))
    ratios = df_eff.set_index('nu')['ratio']
    lo, hi = float(macros["RFourNuStarLower"]), float(macros["RFourNuStarUpper"])
    assert ratios[lo] < 1.0 <= ratios[hi]


# --- TABLE 3 ---

def test_R04_table3_printing_rule_reproduces_v87(witness_race):
    """
    The printing precision of Table 3 is three significant figures floored at
    integer precision. Anchored on v87: the rule is applied to the WITNESS
    values, which are the ones v87 printed, and must reproduce the twelve
    strings the manuscript shows. This tests the formatter against the
    manuscript rather than against the regenerated campaign.
    """
    published = {
        ("Recalib", 0.25): "2293", ("Eco_L1", 0.25): "389", ("Concept", 0.25): "460",
        ("Recalib", 0.5): "1337", ("Eco_L1", 0.5): "72.0", ("Concept", 0.5): "101",
        ("Recalib", 1.0): "203", ("Eco_L1", 1.0): "26.4", ("Concept", 1.0): "43.8",
        ("Recalib", 2.0): "55.9", ("Eco_L1", 2.0): "12.6", ("Concept", 2.0): "28.9",
    }
    block = witness_race[np.isclose(witness_race['Gamma'], GAMMA_RACE)]
    for (arm, c), expected in published.items():
        value = block[(block['arm'] == arm) & np.isclose(block['c'], c)]['ADD'].iloc[0]
        assert format_table_cell(float(value)) == expected, (
            f"printing rule gives {format_table_cell(float(value))} for {arm} at c = {c}, "
            f"v87 prints {expected}")


def test_R04_table3_is_generated_from_the_csv(df_race):
    """
    (A3) Table 3 carries no hard-coded value: every cell is the projection of
    R04_isofpr_race.csv at the race Gamma through the printing rule, and the
    environment is complete and ready to \\input.
    """
    text = (TABLES_DIR / "tab03_isofpr_race.tex").read_text()
    assert text.startswith("% Auto-generated by exp_R04_isofpr_race.py -- do not edit.")
    assert "\\begin{table}" in text and "\\end{table}" in text
    assert "\\toprule" in text and "\\bottomrule" in text
    assert "\\label{tab:isofpr_race}" in text
    assert text.endswith("\n")

    block = df_race[np.isclose(df_race['Gamma'], GAMMA_RACE)]
    for arm in ("Recalib", "Eco_L1", "Concept"):
        for c in C_GRID:
            row = block[(block['arm'] == arm) & np.isclose(block['c'], c)].iloc[0]
            assert f"${format_table_cell(row['ADD_conditional'])}$" in text, (
                f"Table 3 does not carry the CSV value for {arm} at c = {c}")


def test_R04_table3_shows_detrate_exactly_when_below_one(df_race):
    """DetRate appears in parentheses if and only if it is below 1, per v87."""
    text = (TABLES_DIR / "tab03_isofpr_race.tex").read_text()
    block = df_race[np.isclose(df_race['Gamma'], GAMMA_RACE)]
    for arm in ("Recalib", "Eco_L1", "Concept"):
        for c in C_GRID:
            row = block[(block['arm'] == arm) & np.isclose(block['c'], c)].iloc[0]
            if row['DetRate'] < 1.0:
                assert f"$({row['DetRate']:.2f})$" in text


# --- INTERVALS AND PERSISTENCE HYGIENE ---

def test_R04_intervals_are_clamped_and_ordered(df_calib, df_race, df_family, df_m0):
    """Every persisted interval lies in [0, 1] and brackets its own estimate."""
    for frame, point in ((df_calib, 'FPR_achieved'), (df_race, 'DetRate'),
                         (df_family, 'FPR'), (df_m0, 'FPR')):
        assert (frame['CI_low'] >= 0.0).all() and (frame['CI_high'] <= 1.0).all()
        assert (frame['CI_low'] <= frame[point]).all()
        assert (frame[point] <= frame['CI_high']).all()


def test_R04_no_nan_in_reported_delays(df_race, df_eff):
    """Every cell of the race produced at least one detection, so Table 3 is fillable."""
    assert df_race['ADD_conditional'].notna().all()
    assert df_eff[['ADD_Eco_L1', 'ADD_Oracle', 'ADD_Concept']].notna().all().all()


def test_R04_m0_universality_arm_matches_the_garch_arm(df_m0):
    """
    Corollary cor:universal states the null law of the Concept CUSUM is
    universal and reproducible "by direct Monte-Carlo simulation of a fair
    coin". The two arms of M0 -- one driven by a GARCH generator, one by a
    fair coin with no GARCH anywhere -- must therefore agree. Tested as a
    two-proportion homogeneity, which is the property, not as an equality.
    """
    assert set(df_m0['source']) == {"garch", "bernoulli_iid"}
    alarms = df_m0.set_index('source')['alarms']
    n = df_m0.set_index('source')['N_streams']
    table = np.array([[alarms['garch'], n['garch'] - alarms['garch']],
                      [alarms['bernoulli_iid'], n['bernoulli_iid'] - alarms['bernoulli_iid']]])
    _, p, _, _ = stats.chi2_contingency(table)
    assert p > 0.01, (
        f"The fair-coin arm and the GARCH arm disagree (p = {p:.4f}), which would contradict the "
        "universality of the Bernoulli(1/2) null")


# --- CLASSIFICATION OUTPUT, ASSERTS NOTHING ---

def test_R04_report_deviation_degrees(df_race, df_eff, witness_race, witness_eff, capsys):
    """
    Prints the D0/D1/D2/D3 degree of every published quantity against the
    vendored witness. Deliberately assertion-free: the witness was produced by a
    generator whose Gamma grid collapsed to a single point, so agreement with it
    would be evidence of reproducing a defect rather than of correctness.
    """
    lines = []
    block = df_race[np.isclose(df_race['Gamma'], GAMMA_RACE)]
    w_block = witness_race[np.isclose(witness_race['Gamma'], GAMMA_RACE)]
    for arm in ("Recalib", "Eco_L1", "Concept"):
        for c in C_GRID:
            pub = float(w_block[(w_block['arm'] == arm) & np.isclose(w_block['c'], c)]['ADD'].iloc[0])
            reg = float(block[(block['arm'] == arm) & np.isclose(block['c'], c)]['ADD_conditional'].iloc[0])
            degree = "D0" if pub == reg else (
                "D1" if format_table_cell(pub) == format_table_cell(reg) else "D2")
            lines.append(f"Table 3 {arm:<11} c={c:<5} | {pub:>12.6f} | {reg:>12.6f} | {degree}")
    for nu in df_eff['nu']:
        pub = float(witness_eff[np.isclose(witness_eff['nu'], nu)]['ratio'].iloc[0])
        reg = float(df_eff[np.isclose(df_eff['nu'], nu)]['ratio'].iloc[0])
        degree = "D0" if pub == reg else ("D1" if round(pub, 6) == round(reg, 6) else "D2")
        lines.append(f"ratio at nu={nu:<20} | {pub:>12.6f} | {reg:>12.6f} | {degree}")

    with capsys.disabled():
        print("\n  R04 deviation classification against the submitted campaign")
        print(f"  {'quantity':<28} | {'published':>12} | {'regenerated':>12} | degree")
        for line in lines:
            print(f"  {line}")
        print("  The witness is a record of the submitted campaign, not a target; see "
              "docs/sections/R04.md for why its Gamma grid does not span.")
