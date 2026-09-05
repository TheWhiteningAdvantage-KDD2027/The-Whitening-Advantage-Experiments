"""
R15 -- cross-sectional escape on a real equity panel. Acceptance and reporting.

Two kinds of statement live in this file and they are kept apart deliberately.

*Blocking assertions* rest either on a value v87 PRINTS, compared at v87's own
printing precision, which is what preamble S3 fixes as the classification rule,
or on a deterministic relation reimplemented HERE, independently of the
experiment -- the K = 1 median degeneracy re-derived from the panel CSV, the
Wilson interval written from a second algebraic form, the frozen composition
re-extracted from the witness by a SECOND `ast` pass and re-executed, the
survival chain recounted line by line from the submitted fetch log, and the
arithmetic of the `-1` sentinel. NONE rests on a continuous value R15 produced.

*Reporting output* prints the campaign against its witness, the design effects
and the two arms against each other, and asserts nothing.

WHY THE WITNESS IS NOT A BLOCKING ANCHOR. `data/reference/README.md` states it
outright: a witness value is the "published value" column of a D0-D3 comparison,
never the anchor of a blocking assertion, because a cell-by-cell equality gate
converts every legitimate correction into a test failure whose only exit is a
widened tolerance. R15's 128-bit re-keying redraws every threshold and every
delay by construction.

THE ONE PLACE A WITNESS VALUE DOES BLOCK, AND WHY IT IS SOUND. The frozen panel
composition is an INTEGER array and it is not a Monte-Carlo replicate: it selects
which real series enter the experiment, and if it moved, nothing in this stream
would be comparable to v87 at all. It is therefore asserted bit-identical --
re-derived here from the witness source rather than read from any value R15
wrote.

THE SELF-INVALIDATING ASSERTIONS, one per registered deviation.

`test_R15_the_scatter_correlation_of_the_figure_caption_is_negative` asserts
`R15-scatter-sign`. If a later campaign brings the coefficient above `+0.99`,
it fires, and what must then change is `docs/DEVIATIONS.md` -- the entry is
withdrawn -- never this assertion.

`test_R15_the_bootstrap_fpr_envelope_of_the_caption_does_not_reproduce` asserts
`R15-campaign-redraw`. If a later campaign restores `4.8`-`6.4%` at one
decimal, it fires.

`test_R15_the_sign_correlation_drifts_under_MKL_CBWR_and_not_otherwise` asserts
`R15-mkl-cbwr-rho`. If the default arm ever becomes bit-identical to the witness
on `rho_sign_meas`, or the attribution arm stops being so, it fires.

`test_R15_the_published_grid_is_declared_by_the_updated_witness_alone` asserts
`R15-grid-provenance`. If the vendored pair of scripts stops separating the ten-
and four-point grids, it fires.
"""

import ast
import hashlib
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "results" / "R15_cross_sectional" / "data"
FIGURES_DIR = ROOT / "results" / "R15_cross_sectional" / "figures"
TABLES_DIR = ROOT / "results" / "R15_cross_sectional" / "tables"
REFERENCE_DIR = ROOT / "data" / "reference" / "R15"
LOGS_DIR = ROOT / "logs" / "R15_cross_sectional"
PANEL_PATH = ROOT / "data" / "derived_equities" / "R15_panel_logreturns.csv"
EXPERIMENT_A = ROOT / "experiments" / "R15_cross_sectional" / "exp_R15_cross_sectional_a.py"
EXPERIMENT_B = ROOT / "experiments" / "R15_cross_sectional" / "exp_R15_cross_sectional_b.py"
WITNESS_SCRIPT = REFERENCE_DIR / "Priorite_25c_real_cross_sectional_escape_UPDATED.py"
SUPERSEDED_SCRIPT = REFERENCE_DIR / "Priorite_25c_real_cross_sectional_escape.py"
FETCH_LOG = REFERENCE_DIR / "Priorite_25b_fetch_yf_panel.log"
R13_SCRIPT = ROOT / "experiments" / "R13_oracle_ceiling" / "exp_R13_oracle_ceiling_a.py"

MACRO_PREFIX = "RFifteen"
WITNESS_SUFFIX = "_witness_blas"

# --- WHAT v87 PRINTS, AT THE PRECISION IT PRINTS IT ---
V87_PANEL_SIZE = 97
V87_PANEL_DAYS = 5154
V87_FIRST_DATE = "2005-01-04"
V87_LAST_DATE = "2025-06-30"
V87_RHO_SIGN = 0.26
V87_WHITENESS_FAILS_BEYOND_K = 10
V87_BUDGET_PLATEAU = 2.0
V87_SCATTER_R = 0.99
V87_COVID_DETECTIONS = 0
V87_FPR_BOOT_ENVELOPE_PCT = (4.8, 6.4)

# --- THE PROTOCOL, RE-DECLARED HERE SO THE TEST DOES NOT IMPORT THE SCRIPT ---
H_REF, H_DET = 500, 750
N_RACE = 2000
MASTER_SEED = 42
K_GRID = (1, 5, 10, 20, 30, 40, 50, 60, 75, 97)
C_GRID = (0.10, 0.25, 0.50, 0.75, 1.0)
C_TARGET = 0.25
PLATEAU_K_MIN = 20
RHO_POOL_K_MIN = 5
DET_RATE_FLOOR = 0.90
MIN_COVERAGE = 0.98
MAX_RETRY = 3


# =====================================================================
# FIXTURES
# =====================================================================

def _read(name):
    path = DATA_DIR / name
    if not path.exists():
        pytest.skip(f"{path} is missing; run ./run_experiment_R15.sh first")
    return pd.read_csv(path, float_precision='round_trip')


@pytest.fixture(scope="module")
def diagnostics():
    return _read("R15_panel_diagnostics.csv")


@pytest.fixture(scope="module")
def diagnostics_witness_blas():
    return _read(f"R15_panel_diagnostics{WITNESS_SUFFIX}.csv")


@pytest.fixture(scope="module")
def race():
    return _read("R15_cross_sectional_race.csv")


@pytest.fixture(scope="module")
def covid():
    return _read("R15_covid_natural.csv")


@pytest.fixture(scope="module")
def composition():
    return _read("R15_panel_composition.csv")


@pytest.fixture(scope="module")
def race_windows():
    return _read("R15_race_windows.csv")


@pytest.fixture(scope="module")
def scatter():
    return _read("R15_scatter_correlation.csv")


@pytest.fixture(scope="module")
def witness_diagnostics():
    return pd.read_csv(REFERENCE_DIR / "protocol_25c_real_panel_diagnostics_UPDATED.csv",
                       float_precision='round_trip')


@pytest.fixture(scope="module")
def witness_race():
    return pd.read_csv(REFERENCE_DIR / "protocol_25d_real_cross_sectional_race_UPDATED.csv",
                       float_precision='round_trip')


@pytest.fixture(scope="module")
def panel():
    if not PANEL_PATH.exists():
        pytest.skip(f"{PANEL_PATH} is missing")
    return pd.read_csv(PANEL_PATH, index_col="Date", parse_dates=True,
                       float_precision='round_trip')


@pytest.fixture(scope="module")
def macros():
    path = TABLES_DIR / "R15_claims.tex"
    if not path.exists():
        pytest.skip(f"{path} is missing")
    return dict(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}\{(.*)\}", path.read_text()))


# =====================================================================
# BLOCKING -- RELATIONS REIMPLEMENTED INDEPENDENTLY OF THE EXPERIMENT
# =====================================================================

def test_R15_the_panel_is_the_one_v87_describes(panel):
    """v87 L376: '97 surviving US equities, 2005--2025'."""
    assert panel.shape == (V87_PANEL_DAYS, V87_PANEL_SIZE), (
        f"the panel is {panel.shape}, against the {V87_PANEL_DAYS} x {V87_PANEL_SIZE} v87 "
        f"describes")
    assert panel.index.min().date().isoformat() == V87_FIRST_DATE
    assert panel.index.max().date().isoformat() == V87_LAST_DATE
    assert panel.index.is_monotonic_increasing and not panel.index.has_duplicates
    assert not bool(panel.isna().any().any())


def test_R15_the_survival_chain_is_recounted_from_the_submitted_fetch_log():
    """
    The chain `103 -> 102 -> 100 -> 97` is a claim of docs/sections/R15.md, and
    it is recounted HERE from the log rather than read from any statement the
    experiment makes. The parse stops at the summary line: the vendored log
    holds three appended runs and only the first completed.
    """
    lines = FETCH_LOG.read_text().splitlines()
    end = next(i for i, line in enumerate(lines) if "panel_logreturns.csv:" in line)
    fetched, abandoned = {}, []
    for line in lines[:end]:
        rows = re.search(r"INFO: ([A-Z]+): (\d+) rows", line)
        if rows:
            fetched[rows.group(1)] = int(rows.group(2))
        gave_up = re.search(r"ERROR: ([A-Z]+): giving up", line)
        if gave_up:
            abandoned.append(gave_up.group(1))
    announced = re.search(r"Fetching (\d+) tickers", lines[0])
    assert announced and int(announced.group(1)) == 102, (
        "the submitted fetch announces 102 unique tickers")
    assert len(fetched) == 100, f"the log records {len(fetched)} fetched tickers, not 100"
    assert sorted(abandoned) == ["K", "MMC"], (
        f"the log abandons {sorted(abandoned)}; the section names MMC and K")
    days = max(fetched.values())
    assert days == V87_PANEL_DAYS
    low = {t: n for t, n in fetched.items() if n / days < MIN_COVERAGE}
    assert sorted(low) == ["GM", "MA", "V"], (
        f"the {MIN_COVERAGE:.0%} coverage floor drops {sorted(low)}; the section names V, MA, GM")
    assert len(fetched) - len(low) == V87_PANEL_SIZE
    # THE SURVIVAL RULE IS THE COVERAGE FILTER, NOT `dropna(how='any')`: every
    # retained ticker already carries the full index, so the row-wise dropna that
    # follows it removes no date at all.
    assert all(n == days for t, n in fetched.items() if t not in low)


def test_R15_the_k_one_degeneracy_is_an_identity_of_the_median_split(panel, diagnostics,
                                                                    composition):
    """
    C1, re-derived from the panel CSV and the persisted composition, touching no
    value the experiment computed. The median of an even number of observations
    is the mean of the two central order statistics, so subtracting it leaves
    exactly half the sample strictly positive PROVIDED no observation ties it.
    `fraction_stream` at K = 1 is then +-0.5, mean 0, variance 1/4, and
    K_eff = 1/(4 * 1/4) = 1 exactly.
    """
    ticker = composition[composition['K'] == 1]['ticker'].iloc[0]
    series = panel[ticker].to_numpy(dtype=float)
    centred = series - np.median(series)
    assert len(series) % 2 == 0, "the exact split needs an even sample"
    assert int(np.sum(centred == 0.0)) == 0, "an exact tie with the median breaks the split"
    assert int(np.sum(centred > 0.0)) == len(series) // 2
    x = (centred > 0.0).astype(float) - 0.5
    assert float(np.mean(x)) == 0.0
    assert float(np.var(x)) == 0.25
    assert 1.0 / (4.0 * float(np.var(x))) == 1.0
    row = diagnostics[diagnostics['K'] == 1].iloc[0]
    assert float(row['rho_sign_meas']) == 0.0
    assert float(row['K_eff_meas']) == 1.0


def test_R15_every_persisted_interval_is_a_wilson_interval_inside_the_unit_square(race):
    """
    `wilson_ci` rewritten from a SECOND algebraic form -- the roots of
    (p_hat - p)^2 = z^2 p(1-p)/n solved directly -- so the check does not
    reproduce the carried implementation's own arithmetic.
    """
    z = 1.959963984540054  # Phi^{-1}(0.975)
    for row in race.itertuples():
        n, k = N_RACE, int(row.n_detected)
        p = k / n
        denom = 1.0 + z * z / n
        centre = (p + z * z / (2.0 * n)) / denom
        half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
        assert float(row.CI_low) == pytest.approx(max(0.0, centre - half), abs=1e-12)
        assert float(row.CI_high) == pytest.approx(min(1.0, centre + half), abs=1e-12)
        assert 0.0 <= float(row.CI_low) <= float(row.CI_high) <= 1.0
        # In exact arithmetic the Wilson interval contains p_hat. At p_hat = 1 the
        # carried implementation returns `min(1.0, c + m)` with `c + m` one ULP
        # short of 1, so containment is asserted to 1e-12 and not exactly. A
        # tolerance introduced for a named floating-point reason is not a widened
        # gate: it is the size of the effect it accommodates.
        assert float(row.CI_low) - 1e-12 <= float(row.DetRate) <= float(row.CI_high) + 1e-12


def test_R15_the_frozen_composition_is_the_delivered_one(composition):
    """
    C1 leg 1, re-derived by a SECOND `ast` pass over the witness. The three
    statements are extracted here, compiled, and executed in a namespace holding
    nothing but `hashlib`, `np`, `K`, `K_max` and `MASTER_SEED`; the integer
    arrays are then compared to the persisted composition. If this and the
    experiment's own check disagreed, one of them would be reading a different
    file.
    """
    text = WITNESS_SCRIPT.read_text()
    tree = ast.parse(text)
    wanted = ("cell_seed_base", "rng_diag", "assets_idx")
    found = {}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef) and node.name == "run_real_experiment"):
            continue
        for stmt in ast.walk(node):
            if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Name)
                    and stmt.targets[0].id in wanted and stmt.targets[0].id not in found):
                found[stmt.targets[0].id] = ast.get_source_segment(text, stmt)
    assert set(found) == set(wanted), f"the witness statements could not be extracted: {found}"
    program = compile("\n".join(found[name] for name in wanted), "<witness>", "exec")
    for K in K_GRID:
        namespace = {"hashlib": hashlib, "np": np, "K": K, "K_max": V87_PANEL_SIZE,
                     "MASTER_SEED": MASTER_SEED}
        exec(program, namespace)
        persisted = (composition[composition['K'] == K].sort_values('position')['asset_index']
                     .to_numpy())
        assert np.array_equal(persisted, namespace["assets_idx"]), (
            f"the persisted composition at K = {K} is not the one the delivered script draws")
    assert len(composition) == sum(K_GRID)


def test_R15_the_sentinel_never_enters_a_mean(race, race_windows, covid):
    """
    `bilateral_delay` returns `-1` iff neither one-sided CUSUM crosses, so `-1`
    is a NON-DETECTION and never a delay of minus one day. The arithmetic is
    recomputed here from the per-replicate windows.
    """
    assert set(race_windows['arm']) == {"panel", "reference"}
    panel_arm = race_windows[race_windows['arm'] == 'panel']
    for row in race.itertuples():
        cell = panel_arm[(panel_arm['K'] == row.K) & (panel_arm['c'] == row.c)]
        assert len(cell) == N_RACE
        detected = cell[cell['delay'] != -1]['delay'].to_numpy(dtype=float)
        assert len(detected) == int(row.n_detected)
        assert float(row.DetRate) == len(detected) / N_RACE
        assert (detected >= 0).all(), "a negative delay other than the sentinel was averaged"
        if len(detected):
            assert float(row.ADD) == pytest.approx(float(detected.mean()), rel=1e-12)
        assert (cell['delay'] >= -1).all()
    assert set(covid['delay_boot'].unique()) <= {-1} | set(range(0, H_DET + 1))


def test_R15_the_carried_primitives_are_byte_identical_to_the_files_that_own_them():
    """C9, re-extracted here rather than trusted from the experiment's own log."""
    owners = {
        "strict_cusum": WITNESS_SCRIPT, "bilateral_delay": WITNESS_SCRIPT,
        "cusum_max_bilateral": WITNESS_SCRIPT, "wilson_ci": WITNESS_SCRIPT,
        "fraction_stream": WITNESS_SCRIPT, "get_deterministic_seed": R13_SCRIPT,
        "seed_sequence_for": R13_SCRIPT, "rng_for": R13_SCRIPT,
    }

    def segments(path, names):
        text = Path(path).read_text()
        tree = ast.parse(text)
        return {n.name: ast.get_source_segment(text, n) for n in tree.body
                if isinstance(n, ast.FunctionDef) and n.name in names}

    mine = segments(EXPERIMENT_B, set(owners))
    for name, owner in sorted(owners.items()):
        theirs = segments(owner, {name}).get(name)
        assert theirs is not None, f"{owner.name} carries no {name}"
        assert mine.get(name) == theirs, (
            f"{name} has drifted from {owner.name}; preamble S4.2 requires byte identity")


def test_R15_no_draw_reaches_the_global_numpy_stream():
    """
    The entropy migration made mechanical. `np.random.<name>` is admissible only
    when it constructs a generator; anything else draws from the implicitly
    seeded global stream. `default_rng` on a bare integer is admissible in
    exactly one place -- the frozen composition, which is carried verbatim.
    """
    non_drawing = {"SeedSequence", "default_rng"}
    for path in (EXPERIMENT_A, EXPERIMENT_B):
        tree = ast.parse(Path(path).read_text())
        for node in tree.body:
            scope = node.name if isinstance(node, (ast.FunctionDef, ast.ClassDef)) else "<module>"
            for child in ast.walk(node):
                if not isinstance(child, ast.Attribute):
                    continue
                base = child.value
                if not (isinstance(base, ast.Attribute) and base.attr == "random"
                        and isinstance(base.value, ast.Name) and base.value.id == "np"):
                    continue
                assert child.attr in non_drawing, (
                    f"{path.name}::{scope} draws np.random.{child.attr} from the implicitly "
                    f"seeded global stream")
        assert "np.random.seed" not in Path(path).read_text()
        assert "RandomState" not in Path(path).read_text()


def test_R15_every_square_root_of_a_sample_size_follows_a_design_effect():
    """
    S4bis's sixth corollary made mechanical: a bare `np.sqrt(len(...))` is a
    form defect proscribed exactly as a bare `except:` is, and the rule is that
    the design effect is computed in the same logical block just above it.
    """
    text = EXPERIMENT_B.read_text()
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
        window = "\n".join(lines[max(0, i - 14):i])
        if "design_effect(" not in window and "deff" not in window:
            offenders.append((i + 1, line.strip()))
    assert not offenders, (
        f"a square root of a sample size is taken without a design effect in the same block "
        f"above it: {offenders}")


def test_R15_the_design_effect_is_computed_from_the_mechanism_and_never_below_one(race,
                                                                                 diagnostics):
    """
    A design effect below 1 would advertise more independent readings than the
    sample holds. The lag count comes from the overlap radius and the finite
    window population, never from an observed autocorrelation.
    """
    n_distinct = V87_PANEL_DAYS - (H_REF + H_DET) + 1
    radius = 2 * (H_REF + H_DET) - 1
    for row in race.itertuples():
        assert float(row.deff) >= 1.0
        assert float(row.n_eff) <= int(row.n_detected) + 1e-9
        if int(row.n_detected) > 1:
            expected = int(min(int(row.n_detected) - 1,
                               max(1, math.ceil(int(row.n_detected) * radius / n_distinct))))
            assert int(row.deff_lags) == expected
    for row in diagnostics.itertuples():
        assert float(row.deff_eval) >= 1.0 and float(row.deff_calib) >= 1.0
        assert float(row.SE_FPR_boot_design) > float(row.SE_FPR_boot_binomial), (
            "the finite window population can only widen the interval, never narrow it")
        assert int(row.distinct_windows_available) == n_distinct


# =====================================================================
# BLOCKING -- WHAT v87 PRINTS, AT v87's PRINTING PRECISION
# =====================================================================

def test_R15_the_numerals_of_L376_that_reproduce_do_reproduce(diagnostics, race, covid, macros):
    """
    The four published quantities that survive the re-keying at v87's own
    precision: the sign correlation, the whiteness switch point, the plateau and
    the COVID non-detection.
    """
    rho = float(diagnostics[diagnostics['K'] >= RHO_POOL_K_MIN]['rho_sign_meas'].mean())
    assert round(rho, 2) == V87_RHO_SIGN, (
        f"L376 prints a sign correlation of {V87_RHO_SIGN}; the campaign gives {rho!r}")
    assert macros[f"{MACRO_PREFIX}RhoSign"] == f"{V87_RHO_SIGN:.2f}"

    passing = diagnostics[diagnostics['ljungbox_p_Pt'] >= 0.05]['K']
    assert int(passing.max()) == V87_WHITENESS_FAILS_BEYOND_K, (
        f"L376 states temporal whiteness fails beyond K = {V87_WHITENESS_FAILS_BEYOND_K}")
    assert int(diagnostics[diagnostics['ljungbox_p_Pt'] < 0.05]['K'].min()) > \
        V87_WHITENESS_FAILS_BEYOND_K

    plotted = race[race['c'] == C_TARGET]
    plateau = float(plotted[plotted['K'] >= PLATEAU_K_MIN]['budget_reduction'].mean())
    assert round(plateau, 0) == V87_BUDGET_PLATEAU, (
        f"the caption says the budget reduction plateaus near {V87_BUDGET_PLATEAU:g}x for "
        f"K >= {PLATEAU_K_MIN}; the campaign gives {plateau!r}")

    assert int((covid['delay_boot'] != -1).sum()) == V87_COVID_DETECTIONS, (
        "L376 states the pooled monitor still never flags the 2020 crash")
    assert macros[f"{MACRO_PREFIX}CovidDetections"] == str(V87_COVID_DETECTIONS)
    assert macros[f"{MACRO_PREFIX}PanelSize"] == str(V87_PANEL_SIZE)
    assert macros[f"{MACRO_PREFIX}PanelDays"] == str(V87_PANEL_DAYS)


def test_R15_the_independence_calibration_loses_its_level_and_the_bootstrap_holds_one(diagnostics):
    """
    The qualitative claim of Figure 17 panel A: the naive calibration climbs
    toward 100% while the real-window bootstrap stays at the nominal level. Read
    as the relations v87 states, not as the numerals it prints.
    """
    naive = diagnostics.set_index('K')['FPR_naive']
    boot = diagnostics.set_index('K')['FPR_boot']
    assert float(naive.loc[40]) > 0.95, (
        f"L376 states an independence null reaches ~100% false alarms by K = 40; it reaches "
        f"{float(naive.loc[40])!r}")
    assert float(naive.loc[97]) >= float(naive.loc[40])
    assert float(naive.loc[1]) > 2.0 * 0.05, (
        "the K = 1 counterfactual: the naive threshold already over-fires with no cross-sectional "
        "correlation present at all")
    assert (boot < 0.10).all() and (boot > 0.02).all(), (
        f"the real-window bootstrap does not hold a nominal-scale level: {boot.to_dict()}")


def test_R15_no_aggregate_reads_a_cell_below_the_reliability_floor(race, macros):
    """C6. The delivered floor is DetRate >= 0.90 and it is what gates ADD."""
    unreliable = race[race['add_reliable'] == 0]
    assert bool(unreliable['budget_reduction'].isna().all()), (
        "an unreliable cell carries a budget_reduction")
    assert (race[race['add_reliable'] == 1]['DetRate'] >= DET_RATE_FLOOR).all()
    plotted = race[(race['c'] == C_TARGET) & (race['K'] >= PLATEAU_K_MIN)]
    assert (plotted['add_reliable'] == 1).all(), (
        "the plateau macro pools a cell the caption draws hollow")
    assert (plotted['ADD_single_reliable'] == 1).all(), (
        "the plateau macro divides by a censored reference arm")


def test_R15_the_effective_panel_saturates_and_the_two_estimators_agree(diagnostics):
    """
    L376: the effective panel saturates. `K_eff_meas` is asserted to stop
    growing while `K` grows twentyfold, and the two estimators are asserted to
    agree far inside one sampling standard error of `rho`.
    """
    keff = diagnostics.set_index('K')['K_eff_meas']
    assert float(keff.loc[97]) < 5.0, (
        f"L376 says the effective panel saturates near 1/rho ~ 3.8; it reaches {keff.loc[97]!r}")
    assert float(keff.loc[97]) / float(keff.loc[20]) < 1.5, (
        "K_eff must saturate: from K = 20 to K = 97 it may not grow like K")
    gap = (diagnostics['K_eff_relative_gap'] / diagnostics['K_eff_gap_envelope']).max()
    assert float(gap) < 1.0, (
        f"the two K_eff estimators differ by {gap:.3f} of one sampling standard error of rho; "
        f"beyond one they are not the same quantity")


# =====================================================================
# BLOCKING -- ONE SELF-INVALIDATING ASSERTION PER REGISTER ENTRY
# =====================================================================

def test_R15_the_scatter_correlation_of_the_figure_caption_is_negative(scatter, macros):
    """
    SELF-INVALIDATING, `R15-scatter-sign`. v87's Figure 17 caption prints the
    RELATION `r >= 0.99`. The measured coefficient is negative and it is
    negative for a mechanical reason: `budget_reduction` is ADD_single / ADD_K,
    so a higher bootstrap threshold lengthens ADD_K and shrinks the ratio. If a
    later campaign brings the coefficient above `+0.99`, this fires, and what
    changes then is `docs/DEVIATIONS.md`, never this assertion.
    """
    row = scatter[scatter['is_plotted_c'] == 1].iloc[0]
    r = float(row['r_budget_vs_lambda_boot'])
    assert r < 0.0, f"the coefficient is {r!r}; the registered deviation asserts a negative sign"
    assert not (r >= V87_SCATTER_R), "the caption's printed relation would now hold"
    assert abs(r) > 0.9, (
        f"the qualitative claim the caption carries -- the scatter is almost entirely explained "
        f"by threshold variation -- rests on a large |r|; it is {abs(r)!r}")
    assert float(macros[f"{MACRO_PREFIX}ScatterCorrelation"]) == pytest.approx(r, abs=5e-5)
    assert float(macros[f"{MACRO_PREFIX}ScatterCorrelationAbs"]) == pytest.approx(abs(r), abs=5e-5)
    # Every c on the grid gives the same sign: the finding is a property of the
    # mechanism and not of the magnitude the plotting code happens to draw.
    assert (scatter['r_budget_vs_lambda_boot'] < 0).all()


def test_R15_the_bootstrap_fpr_envelope_of_the_caption_does_not_reproduce(diagnostics):
    """
    SELF-INVALIDATING, `R15-campaign-redraw`. The Figure 17 caption prints
    `4.8`-`6.4%`. The entropy migration redraws both calibration sets, so the
    envelope moves. If a later campaign restores the printed pair at one
    decimal, this fires.
    """
    lo = round(100.0 * float(diagnostics['FPR_boot'].min()), 1)
    hi = round(100.0 * float(diagnostics['FPR_boot'].max()), 1)
    assert (lo, hi) != V87_FPR_BOOT_ENVELOPE_PCT, (
        f"the regenerated envelope is {(lo, hi)}, which is the printed one; the registered "
        f"deviation is withdrawn")
    assert 3.0 <= lo <= hi <= 8.0, (
        f"the envelope {(lo, hi)} leaves any nominal-scale reading; the qualitative claim that "
        f"the bootstrap HOLDS the 5% level would not survive that")


def test_R15_the_sign_correlation_drifts_under_MKL_CBWR_and_not_otherwise(
        diagnostics, diagnostics_witness_blas, witness_diagnostics):
    """
    SELF-INVALIDATING, `R15-mkl-cbwr-rho`. The attribution: `rho_sign_meas`
    differs from the witness on the default arm and is bit-identical on the arm
    that removes `MKL_CBWR`. Both halves are asserted, because the entry claims
    both. If either changes, the entry must be rewritten.
    """
    w = witness_diagnostics.set_index('K')['rho_sign_meas']
    default = diagnostics.set_index('K')['rho_sign_meas']
    attributed = diagnostics_witness_blas.set_index('K')['rho_sign_meas']
    drifted = [K for K in K_GRID if float(default.loc[K]) != float(w.loc[K])]
    assert drifted, (
        "the default arm is now bit-identical to the witness on rho_sign_meas; the registered "
        "deviation is withdrawn")
    for K in K_GRID:
        assert float(attributed.loc[K]) == float(w.loc[K]), (
            f"the attribution arm no longer recovers the witness at K = {K}, so the residual is "
            f"NOT the BLAS summation order and the entry's cause is wrong")
    # The drift is bounded by the mechanism, not by the observation: a reordered
    # double-precision sum of N terms moves by at most about N*eps, and the
    # statistic reduces over T*K terms.
    eps = float(np.finfo(np.float64).eps)
    for K in drifted:
        rel = abs(float(default.loc[K]) - float(w.loc[K])) / abs(float(w.loc[K]))
        assert rel <= V87_PANEL_DAYS * K * eps, (
            f"the drift at K = {K} is {rel:.3e}, beyond the reordering bound "
            f"{V87_PANEL_DAYS * K * eps:.3e}; it is not a summation-order artefact")
    # D0 by the repository's own definition: no printed digit moves.
    assert round(float(diagnostics[diagnostics['K'] >= RHO_POOL_K_MIN]['rho_sign_meas'].mean()),
                 2) == round(float(witness_diagnostics[witness_diagnostics['K']
                                                       >= RHO_POOL_K_MIN]['rho_sign_meas'].mean()),
                             2)


def test_R15_the_published_grid_is_declared_by_the_updated_witness_alone():
    """
    SELF-INVALIDATING, `R15-grid-provenance`. The ten-point grid of Figure 17 is
    RECOVERED FROM A SOURCE LINE and is not read off the published artefact. Both
    vendored scripts are checked, because the entry's claim is about the pair.
    """
    updated = WITNESS_SCRIPT.read_text().splitlines()
    superseded = SUPERSEDED_SCRIPT.read_text().splitlines()
    assert updated[166].strip() == "K_GRID = [1, 5, 10, 20, 30, 40, 50, 60, 75, K_max]"
    assert updated[167].strip() == "C_GRID = [0.10, 0.25, 0.50, 0.75, 1.0]"
    assert superseded[166].strip() == "K_GRID = [1, 20, 50, K_max]"
    assert superseded[167].strip() == "C_GRID = [0.10, 0.25, 0.50, 1.0]"
    # The logs settle which grid actually ran under each declaration.
    updated_log = (REFERENCE_DIR / "Priorite_25c_real_cross_sectional_escape_UPDATED.log").read_text()
    superseded_log = (REFERENCE_DIR / "Priorite_25c_real_cross_sectional_escape.log").read_text()
    for probe in ("Whiteness K=5:", "Whiteness K=10:", "Whiteness K=30:"):
        assert probe in updated_log and probe not in superseded_log
    # Same code path on two grids: the values agree exactly at every shared K.
    for probe in ("FPR_naive=0.1115, FPR_boot=0.0490", "FPR_naive=0.9060, FPR_boot=0.0615",
                  "FPR_naive=0.9865, FPR_boot=0.0525", "FPR_naive=1.0000, FPR_boot=0.0495"):
        assert probe in updated_log and probe in superseded_log


# =====================================================================
# BLOCKING -- FILE HYGIENE THE PREAMBLE IMPOSES
# =====================================================================

def test_R15_every_artefact_the_plan_lists_exists_with_its_prescribed_schema(
        diagnostics, race, covid, composition, race_windows, scatter):
    assert len(diagnostics) == len(K_GRID)
    assert list(diagnostics['K']) == list(K_GRID)
    assert len(race) == len(K_GRID) * len(C_GRID)
    assert len(covid) == len(K_GRID)
    assert len(scatter) == len(C_GRID)
    assert int(scatter['is_plotted_c'].sum()) == 1
    assert float(scatter[scatter['is_plotted_c'] == 1]['c'].iloc[0]) == C_TARGET
    assert len(race_windows) == N_RACE * (len(K_GRID) + 1) * len(C_GRID)
    for column in ('q_hat_mean', 'q_hat_sd', 'deff_eval', 'deff_calib', 'SE_FPR_boot_design',
                   'SE_FPR_boot_sqrt2_rule', 'K_eff_relative_gap'):
        assert column in diagnostics.columns
    for column in ('deff', 'n_eff', 'SEM_design', 'ADD_single_DetRate', 'ADD_single_reliable'):
        assert column in race.columns
    assert (FIGURES_DIR / "fig17_cross_section.png").exists()
    assert (TABLES_DIR / "R15_claims.tex").exists()


def test_R15_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix(macros):
    assert macros, "R15_claims.tex carries no macro"
    for name, body in macros.items():
        assert name.startswith(MACRO_PREFIX), (
            f"{name} does not carry the cardinal prefix {MACRO_PREFIX}")
        assert not name.startswith("RFifteenth"), "cardinal, never ordinal"
        assert 'nan' not in body.lower(), f"macro {name} carries the body {body!r}"
        assert body.strip() != ""
    assert len(macros) == 15
    body = (TABLES_DIR / "R15_claims.tex").read_text()
    assert body.startswith("% Auto-generated by exp_R15_cross_sectional_b.py -- do not edit.")
    for line in body.splitlines():
        assert line.startswith("%") or line.startswith("\\newcommand") or not line.strip()
    # R16 owns the Sharpe ceiling and ADD_min; the naive COVID firings are false
    # alarms of an uncalibrated threshold and no macro may publish them.
    assert not any("Sharpe" in n or "AddMin" in n or "DelayNaive" in n for n in macros)


def test_R15_the_witness_blas_artefacts_declare_that_they_certify_no_published_value():
    path = TABLES_DIR / f"R15_claims{WITNESS_SUFFIX}.tex"
    if not path.exists():
        pytest.skip("the attribution arm has not been run")
    header = path.read_text()
    assert "CERTIFY NO v87 VALUE" in header
    assert "Never \\input this file" in header


def test_R15_every_produced_text_file_ends_in_a_newline():
    for path in (TABLES_DIR / "R15_claims.tex",
                 TABLES_DIR / f"R15_claims{WITNESS_SUFFIX}.tex",
                 ROOT / "requirements" / "R15.txt",
                 ROOT / "docs" / "sections" / "R15.md",
                 ROOT / "docs" / "audits" / "AUDIT_R15.md"):
        assert path.exists(), f"Missing deliverable: {path}"
        assert path.read_text().endswith("\n"), f"{path} does not end in a newline"


def test_R15_the_produced_sources_and_logs_carry_no_confirmatory_language():
    """
    Preamble S4.4. The banned words attribute the value of a proof to a
    measurement; neutral technical uses stay licit.

    `proves` and `proven` carry WORD BOUNDARIES here, and the repository's
    canonical `grep -Ein` does not. Without them the pattern matches
    "**proven**ance", which is the ordinary word for where an artefact came from
    and is used throughout this stream, `data/reference/README.md` and the v87
    appendix itself. Adding `\\b` narrows the pattern to what the rule means; it
    does not exempt any use of the banned words.
    """
    pattern = re.compile(
        r"\bproves\b|\bproven\b|perfectly valid|validates the (theorem|thesis|claim)|"
        r"confirms the|as expected|triumph|victory|irrefutable|brilliant", re.IGNORECASE)
    targets = [EXPERIMENT_A, EXPERIMENT_B,
               ROOT / "docs" / "sections" / "R15.md",
               ROOT / "docs" / "audits" / "AUDIT_R15.md",
               LOGS_DIR / "exp_R15_cross_sectional_a.log",
               LOGS_DIR / "exp_R15_cross_sectional_b.log",
               LOGS_DIR / f"exp_R15_cross_sectional_b{WITNESS_SUFFIX}.log"]
    for path in targets:
        if not path.exists():
            continue
        hits = [line for line in path.read_text().splitlines() if pattern.search(line)]
        assert not hits, f"{path.name} carries confirmatory language: {hits[:3]}"


def test_R15_the_produced_sources_carry_no_banned_construct():
    """
    Preamble S7: no `iterrows`, no bare `except:`, no absolute path, no `tqdm`,
    no `logging.basicConfig`. The scan is on EXECUTABLE code: both scripts name
    `tqdm` and `logging.basicConfig` in prose, to record what the delivered
    script did and this port does not, and a docstring that says "the monkey-patch
    is removed" must not be read as the monkey-patch.
    """
    for path in (EXPERIMENT_A, EXPERIMENT_B):
        text = path.read_text()
        code = "\n".join(line for line in text.splitlines()
                         if not line.lstrip().startswith("#"))
        tree = ast.parse(text)
        first = tree.body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
            code = "\n".join(code.splitlines()[first.end_lineno:])
        assert "iterrows" not in code
        assert not re.search(r"except\s*:", code)
        assert not re.search(r"['\"]/home/", text), "no absolute path may be embedded"
        assert not re.search(r"(^|\W)(import|from)\s+tqdm", code)
        assert "tqdm(" not in code
        assert not re.search(r"logging\.basicConfig\s*\(", code)
        assert "run_all.sh" not in code
        # `run_tests.sh` is named once, in the sentence that says the test suite
        # is its exclusive remit. It is never invoked.
        assert not re.search(r"(bash|sh|subprocess|os\.system).*run_tests\.sh", code)
    orchestrator = (ROOT / "run_experiment_R15.sh").read_text()
    executable = [line for line in orchestrator.splitlines()
                  if line.strip() and not line.lstrip().startswith("#")]
    assert not any("pytest" in line for line in executable), (
        "preamble S6: the test suite is the exclusive remit of run_tests.sh")
    assert any("--witness-blas" in line for line in executable), (
        "the attribution arm runs unconditionally; running it only when a result looks wrong "
        "turns it into an instrument of selection")
    assert not any("--stage ingest" in line for line in executable), (
        "the network path is never inside a determinism claim")


# =====================================================================
# REPORTING -- PRINTS WHAT R15 MEASURED, ASSERTS NOTHING
# =====================================================================

def test_R15_report_the_campaign_against_its_witness(diagnostics, witness_diagnostics,
                                                     race, witness_race):
    w = witness_diagnostics.set_index('K')
    print("\nR15 -- the diagnostics against the submitted campaign, per K:")
    print(f"{'K':>4} {'rho (reg)':>13} {'rho (wit)':>13} {'FPR_b (reg)':>12} {'FPR_b (wit)':>12} "
          f"{'lam_b (reg)':>12} {'lam_b (wit)':>12}")
    for row in diagnostics.itertuples():
        ref = w.loc[int(row.K)]
        print(f"{int(row.K):>4} {row.rho_sign_meas:>13.10f} {ref['rho_sign_meas']:>13.10f} "
              f"{row.FPR_boot:>12.4f} {ref['FPR_boot']:>12.4f} "
              f"{row.lambda_boot:>12.4f} {ref['lambda_boot']:>12.4f}")
    wp = witness_race[witness_race['c'] == C_TARGET].set_index('K')
    print(f"\nR15 -- budget reduction at c = {C_TARGET}, regenerated against submitted:")
    for row in race[race['c'] == C_TARGET].sort_values('K').itertuples():
        ref = wp.loc[int(row.K)]
        print(f"  K = {int(row.K):>3}: {row.budget_reduction!r:>22} against "
              f"{ref['budget_reduction']!r:>22} (ADD {row.ADD:.2f} against {ref['ADD']:.2f})")


def test_R15_report_the_design_effects_and_what_they_cost(diagnostics, race):
    n_distinct = V87_PANEL_DAYS - (H_REF + H_DET) + 1
    print(f"\nR15 -- the window population is {n_distinct} distinct starts for "
          f"H_ref + H_det = {H_REF + H_DET} on {V87_PANEL_DAYS} days.")
    print(f"{'K':>4} {'deff_eval':>11} {'n_eff_eval':>11} {'deff_calib':>12} "
          f"{'SE_design':>11} {'SE_sqrt2':>11} {'SE_binom':>11}")
    for row in diagnostics.itertuples():
        print(f"{int(row.K):>4} {row.deff_eval:>11.3f} {row.n_eff_eval:>11.1f} "
              f"{row.deff_calib:>12.3f} {row.SE_FPR_boot_design:>11.6f} "
              f"{row.SE_FPR_boot_sqrt2_rule:>11.6f} {row.SE_FPR_boot_binomial:>11.6f}")
    print(f"\nR15 -- race cells at c = {C_TARGET}: deff, n_eff and the two standard errors.")
    for row in race[race['c'] == C_TARGET].sort_values('K').itertuples():
        print(f"  K = {int(row.K):>3}: n_det {int(row.n_detected):>5}, deff {row.deff:>8.3f}, "
              f"n_eff {row.n_eff:>8.1f}, SEM {row.SEM:>8.4f} -> SEM_design "
              f"{row.SEM_design:>8.4f}")


def test_R15_report_the_two_readings_of_the_caption_correlation(scatter):
    print("\nR15 -- the Figure 17 caption's `r >= 0.99`, both readings, at every c:")
    for row in scatter.itertuples():
        marker = "  <- the c the plotting code draws" if int(row.is_plotted_c) else ""
        print(f"  c = {row.c:<5}: r(budget_reduction, lambda_boot) = "
              f"{row.r_budget_vs_lambda_boot:>10.6f} over {int(row.n_points_budget)} K | "
              f"r(ADD, lambda_boot) = {row.r_add_vs_lambda_boot:>10.6f} over "
              f"{int(row.n_points_add)} K{marker}")


def test_R15_report_the_marginal_channel_the_caption_does_not_name(diagnostics):
    print("\nR15 -- FPR_naive, its K = 1 counterfactual, and the marginal channel q_hat:")
    base = float(diagnostics[diagnostics['K'] == 1]['FPR_naive'].iloc[0])
    for row in diagnostics.itertuples():
        print(f"  K = {int(row.K):>3}: FPR_naive {row.FPR_naive:.4f} "
              f"(increment over K = 1: {row.FPR_naive - base:+.4f}), rho_sign "
              f"{row.rho_sign_meas:.6f}, q_hat {row.q_hat_mean:.6f} +- {row.q_hat_sd:.6f}")
    print("  At K = 1 the cross-sectional channel is EXACTLY empty (rho = 0, K_eff = 1) and the "
          "excess over the nominal 5% is entirely marginal. Beyond K = 1 the two channels move "
          "together along a single arm and the decomposition is not identifiable.")
