"""
R14 -- efficiency reversal on real Bitcoin. Acceptance and reporting.

Two kinds of statement live in this file and they are kept apart deliberately.

*Blocking assertions* rest either on a value v87 PRINTS, compared at v87's own
printing precision, which is what preamble S3 fixes as the classification rule,
or on a deterministic relation reimplemented here independently of the
experiment -- the attainable lattice of the bisection tolerance computed from
arithmetic, the pairwise-reliable grid re-derived from the persisted CSV, the
Wilson interval written from a second algebraic form, the source identity of the
carried primitives extracted by a second `ast` pass -- or, on the
`_legacy_seeds` arm alone, on a DISCRETE quantity of the witness. NONE rests on
a continuous value R14 produced.

*Reporting output* prints the campaign against its witness, the design-effect
distribution and the bootstrap envelopes, and asserts nothing.

WHY THE WITNESS IS NOT A BLOCKING ANCHOR ON THE DEFAULT ARM.
`data/reference/README.md` states it outright: a witness value is the "published
value" column of a D0-D3 comparison, never the anchor of a blocking assertion,
because a cell-by-cell equality gate converts every legitimate correction into a
test failure whose only exit is a widened tolerance. R14's 128-bit re-keying
redraws both synthetic controls by construction.

WHY THE `_legacy_seeds` ARM IS DIFFERENT, AND WHERE ITS TOLERANCE STOPS. That
arm shares the witness's seeds, so the only admissible drift is the
`float_precision='round_trip'` parser change and the BLAS pinning. Its DISCRETE
quantities -- `n_onsets`, the realized false-alarm counts, the `add_reliable`
flags, `DetRate` -- are therefore asserted EXACTLY equal to the witness. `ADD` is
NOT given a tolerance: a CUSUM crossing is a discontinuous function of its
stream, so a 1-ULP input change legitimately moves a delay by a whole trading
day. The test reports how many cells moved and asserts nothing on that count.
Widening a tolerance until it passes is the manoeuvre preamble S4 rule 8 bans.

THE SELF-INVALIDATING ASSERTIONS, one per registered deviation.

`test_R14_the_synthetic_control_numerals_of_L345_do_not_reproduce_at_their_
printed_precision` asserts the deviation `R14-campaign-redraw` itself. If a
later campaign ever brings the t_30 mean ratio back to `1.06`, it fires, and
what must then change is `docs/DEVIATIONS.md` -- the entry is withdrawn -- never
this assertion.

`test_R14_the_iso_fpr_match_on_real_ethereum_is_lost_under_the_re_keying`
asserts that control C2 fires on `Real_ETH` and on nothing else. If a later
campaign restores the match, it fires, and the section and the audit are what
must change.
"""

import ast
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "results" / "R14_crypto_isofpr" / "data"
FIGURES_DIR = ROOT / "results" / "R14_crypto_isofpr" / "figures"
TABLES_DIR = ROOT / "results" / "R14_crypto_isofpr" / "tables"
REFERENCE_DIR = ROOT / "data" / "reference" / "R14"
SERIES_DIR = ROOT / "data" / "derived_crypto"
EXPERIMENT = ROOT / "experiments" / "R14_crypto_isofpr" / "exp_R14_crypto_isofpr.py"
WITNESS_SCRIPT = REFERENCE_DIR / "Priorite_24d_crypto_isofpr_race.py"
R13_SCRIPT = ROOT / "experiments" / "R13_oracle_ceiling" / "exp_R13_oracle_ceiling_a.py"

SOURCES = ("Real_BTC", "Real_ETH", "Synth_BTC", "Synth_ETH")
ARMS = ("Concept", "Eco")
# The imperative grid of R14 prompt section 1, cross-checked against protocol_24b.
C_GRID = (0.10, 0.15, 0.20, 0.25, 0.35, 0.5, 0.60, 0.75, 1.0, 1.25, 1.5)
DET_RATE_FLOOR = 0.90
TARGET_FPR = 0.05
BISECT_TOL = 0.005
H_DET = 500
TRADING_DAYS_PER_MONTH = 21
K_LAGS = 24
# v87 makes no delay and no ordering claim about REAL Ethereum; the three
# sources below are the ones L345 and the L635 caption compare on speed.
PUBLISHED_SPEED_SOURCES = ("Real_BTC", "Synth_BTC", "Synth_ETH")

# =====================================================================
# ANCHORS -- EVERY ONE OF THEM PRINTED IN articleB_whitening_v87.tex
# =====================================================================
# L635 caption: "Efficiency reversal on real Bitcoin (iso-FPR $4.7\%$ on real
# placebo windows, $106$ monthly onsets; hollow markers are unreliable points,
# $\mathrm{DetRate} < 0.9$). (A) Daily BTC ($\hat{\nu} = 2.78$): the sign filter
# (Concept) leads the honestly standardized residual (Eco-L1) across the
# reliable range, converging to parity at $c = 1.5$. (B) A quasi-Gaussian
# $t_{30}$ control on the same onsets inverts the ordering ..."
# L345: "... $106$ monthly onsets ... both arms at an identical $4.7\%$
# false-alarm rate on real placebo windows. On BTC, whose standardized
# innovations carry $\hat{\nu} = 2.78$ ... the delay ratio runs from $0.74$ at
# $c = 0.35$ to parity ($1.01$) at $c = 1.5$, mean $0.87$. A quasi-Gaussian
# synthetic control ($t_{30}$ ...) inverts the ordering to Eco-L1-faster
# ($0.98$--$1.14$, mean $1.06$) ... Ethereum marks the practical boundary: its
# recentred sign stream fails whiteness (Ljung--Box $p = 0.019$), the fair-coin
# pivot does not hold exactly, and the synthetic control does not recover the
# light-tailed ordering at its $72$ onsets ..."
V87_ISO_FPR_PERCENT = 4.7
V87_ONSETS_BTC = 106
V87_ONSETS_ETH = 72
V87_NU_HAT_BTC = 2.78
V87_NAMED_C_LOW = 0.35
V87_NAMED_C_PARITY = 1.5
V87_RATIO_REAL_AT_C_LOW = 0.74
V87_RATIO_REAL_AT_PARITY = 1.01
V87_RATIO_REAL_MEAN = 0.87
V87_RATIO_SYNTH_MIN = 0.98            # NOT reproduced -- see the D2 test below
V87_RATIO_SYNTH_MAX = 1.14            # NOT reproduced -- see the D2 test below
V87_RATIO_SYNTH_MEAN = 1.06           # NOT reproduced -- see the D2 test below
V87_LJUNG_BOX_ETH = 0.019
V87_LJUNG_BOX_LEVEL = 0.05

# =====================================================================
# TOLERANCES, EACH DERIVED FROM A MECHANISM
# =====================================================================
# The Wilson interval is a closed form in float64 evaluated two ways. The two
# expressions differ by the reassociation of a product of at most five terms,
# bounded by 5 * eps = 1.1e-15 in relative terms; 1e-12 carries three orders of
# margin and is derived from no observed deviation.
CLOSED_FORM_RTOL = 1e-12

MACRO_PREFIX = "RFourteen"
MACRO_HEADER = "% Auto-generated by exp_R14_crypto_isofpr.py -- do not edit."


def _read(path):
    assert path.exists(), f"Missing artefact: {path}"
    return pd.read_csv(path, float_precision='round_trip')


@pytest.fixture
def race():
    return _read(DATA_DIR / "R14_crypto_isofpr_race.csv")


@pytest.fixture
def diagnostics():
    return _read(DATA_DIR / "R14_crypto_diagnostics.csv")


@pytest.fixture
def qmle():
    return _read(DATA_DIR / "R14_qmle_recovery.csv")


@pytest.fixture
def onset_delays():
    return _read(DATA_DIR / "R14_onset_delays.csv")


@pytest.fixture
def legacy_race():
    return _read(DATA_DIR / "R14_crypto_isofpr_race_legacy_seeds.csv")


@pytest.fixture
def legacy_diagnostics():
    return _read(DATA_DIR / "R14_crypto_diagnostics_legacy_seeds.csv")


@pytest.fixture
def witness_race():
    return _read(REFERENCE_DIR / "protocol_24b_crypto_isofpr_race.csv")


@pytest.fixture
def witness_diagnostics():
    return _read(REFERENCE_DIR / "protocol_24a_crypto_diagnostics.csv")


@pytest.fixture
def witness_qmle():
    return _read(REFERENCE_DIR / "protocol_24c_qmle_recovery_crypto.csv")


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
    return _macros("R14_claims.tex")


@pytest.fixture
def legacy_macros():
    return _macros("R14_claims_legacy_seeds.tex")


# =====================================================================
# INDEPENDENT REIMPLEMENTATIONS OF THE DERIVED RULES
# =====================================================================

def wilson_score_interval(k, n, z=1.959963984540054):
    """
    The Wilson score interval written from the form R02 owns -- margin
    `z * sqrt((p(1-p) + z^2/(4n)) / n) / denom` -- rather than from the form the
    experiment carries, `z * sqrt(p(1-p)/n + z^2/(4n^2)) / denom`. The two are
    the same interval reassociated, which is the point: two routes, one number.
    """
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def pairwise_reliable(frame, source):
    """
    C1 re-derived from the persisted CSV alone: a magnitude qualifies when BOTH
    arms of the source reach the caption's `DetRate >= 0.9`. The delivered
    `verify_invariants` hard-codes `c >= 0.35` instead.
    """
    sub = frame[frame['source'] == source]
    grid = []
    for c in C_GRID:
        cell = sub[sub['c'] == c]
        if len(cell) == 2 and bool((cell['DetRate'] >= DET_RATE_FLOOR).all()):
            grid.append(c)
    return grid


def ratios_over(frame, source, grid):
    sub = frame[frame['source'] == source]
    return np.array([float(sub[(sub['c'] == c) & (sub['arm'] == 'Concept')]['ADD'].iloc[0])
                     / float(sub[(sub['c'] == c) & (sub['arm'] == 'Eco')]['ADD'].iloc[0])
                     for c in grid], dtype=float)


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


# =====================================================================
# BLOCKING ASSERTIONS -- STRUCTURE AND SCHEMA
# =====================================================================

def test_R14_every_artefact_the_prompt_lists_exists_with_its_prescribed_schema(
        race, diagnostics, qmle, onset_delays):
    """
    The cardinalities are the EXPERIMENTAL DESIGN v87 and the R14 prompt fix --
    four sources, eleven drift magnitudes, two arms -- and not measurements.
    """
    assert len(race) == len(SOURCES) * len(C_GRID) * len(ARMS) == 88
    assert len(diagnostics) == 2
    assert sorted(race['source'].unique()) == sorted(SOURCES)
    assert sorted(race['arm'].unique()) == sorted(ARMS)
    for c in C_GRID:
        assert len(race[race['c'] == c]) == len(SOURCES) * len(ARMS)
    onsets = {row['source']: int(row['n_onsets']) for _, row in race.iterrows()} if False else \
        {s: int(race[race['source'] == s]['n_onsets'].iloc[0]) for s in SOURCES}
    assert onsets == {'Real_BTC': V87_ONSETS_BTC, 'Synth_BTC': V87_ONSETS_BTC,
                      'Real_ETH': V87_ONSETS_ETH, 'Synth_ETH': V87_ONSETS_ETH}
    assert len(onset_delays) == len(C_GRID) * len(ARMS) * sum(onsets.values()) == 7832
    for column in ('deff', 'deff_clamped', 'deff_lags', 'n_eff', 'SEM_design', 'CI_low_design',
                   'CI_high_design', 'n_detected', 'FPR_count', 'iso_fpr_matched'):
        assert column in race.columns, f"the race CSV carries no `{column}`"
    for column in ('SEM', 'CI_low', 'CI_high'):
        assert column in race.columns, (
            f"the delivered `{column}` is kept unchanged beside the design-corrected column for "
            f"witness comparability")
    assert set(qmle['Metric']) >= {'Median_Bias', 'Fallback_Frac', 'Frozen_Frac'}
    assert (FIGURES_DIR / "fig16_crypto_race.png").exists(), (
        "v87 renders fig:crypto_race as Fig28_Crypto_HeavyTail_Race.png; the repository names it "
        "after the figure number the manuscript prints, which is 16.")
    assert (FIGURES_DIR / "fig16_crypto_race_legacy_seeds.png").exists()
    for ticker, sha in (('btc', 'a9c84c890cac7284f6330e3ab4d4aed70a9a5e01ec04a8fc0c9ba8999e79c3f4'),
                        ('eth', 'f44703a75e4510e906ab1cda6e0a50d96e232bc80aba4ef5105ce6ae94c049f1')):
        assert (SERIES_DIR / f"{ticker}_usd_daily.csv").exists(), (
            "the R14 prompt section 3 versions the two daily series under data/derived_crypto/ "
            "and forbids any download path")


def test_R14_the_onset_delays_reproduce_every_aggregate_of_the_race(race, onset_delays):
    """
    `R14_onset_delays.csv` is added so that the paired bootstrap and the design
    effect are checkable without rerunning the campaign. It is only worth
    shipping if the aggregates are recoverable from it, so they are recomputed
    here cell by cell.
    """
    for key, cell in onset_delays.groupby(['source', 'c', 'arm']):
        source, c, arm = key
        row = race[(race['source'] == source) & (race['c'] == c)
                   & (race['arm'] == arm)].iloc[0]
        detected = cell[cell['delay'] != -1]
        assert len(cell) == int(row['n_onsets'])
        assert bool((cell['detected'] == (cell['delay'] != -1)).all())
        assert len(detected) == int(row['n_detected'])
        assert float(len(detected)) / len(cell) == float(row['DetRate'])
        if len(detected) == 0:
            assert pd.isna(row['ADD'])
            continue
        assert float(detected['delay'].mean()) == pytest.approx(float(row['ADD']), rel=1e-12)


# =====================================================================
# BLOCKING ASSERTIONS -- C2, THE REALIZED ISO-FPR
# =====================================================================

def test_R14_the_bisection_tolerance_admits_one_count_at_106_onsets_and_none_at_72():
    """
    C2's fragility, established by ARITHMETIC and not by the run. `bisect_fpr`
    breaks when `|k/N - 0.05| <= 0.005`, and `k/N` is the only value a realized
    false-alarm rate can take. At `N = 106` exactly one integer `k` satisfies
    that, so the two arms of a BTC source are FORCED onto the same rate; at
    `N = 72` no integer does, so the bisection exhausts its forty iterations and
    any agreement there is an outcome of its dynamics rather than a constraint.

    The two agreements are not the same kind of fact, which is why the test
    below treats them differently.
    """
    admissible = {n: [k for k in range(n + 1) if abs(k / n - TARGET_FPR) <= BISECT_TOL]
                  for n in (V87_ONSETS_BTC, V87_ONSETS_ETH)}
    assert admissible[V87_ONSETS_BTC] == [5], (
        "v87's iso-FPR 4.7% is 5/106, and it is the only count the delivered tolerance admits")
    assert rounds_to(100.0 * 5 / V87_ONSETS_BTC, V87_ISO_FPR_PERCENT, 1)
    assert admissible[V87_ONSETS_ETH] == [], (
        "3/72 = 4.17% and 4/72 = 5.56% straddle the band, so no count satisfies the tolerance")


def test_R14_the_two_arms_realize_one_false_alarm_rate_on_every_published_source(race):
    """
    C2. Without a common realized false-alarm rate the race is not iso-FPR and
    no speed comparison is interpretable. Blocking on the three sources whose
    speed comparison v87 publishes; the scope is read clause by clause off L345
    and fixed before the run, not after seeing which source failed.
    """
    for source in PUBLISHED_SPEED_SOURCES:
        sub = race[race['source'] == source]
        assert sub['FPR_achieved'].nunique() == 1, (
            f"{source} carries {sub['FPR_achieved'].nunique()} distinct realized rates; v87 "
            f"compares the two arms on speed at this source and the comparison needs one rate")
        assert bool(sub['iso_fpr_matched'].all())
        n = int(sub['n_onsets'].iloc[0])
        for arm in ARMS:
            row = sub[sub['arm'] == arm].iloc[0]
            assert int(row['FPR_count']) / n == float(row['FPR_achieved'])
    btc = race[race['source'] == 'Real_BTC'].iloc[0]
    assert int(btc['FPR_count']) == 5 and int(btc['n_onsets']) == V87_ONSETS_BTC
    assert rounds_to(100.0 * float(btc['FPR_achieved']), V87_ISO_FPR_PERCENT, 1), (
        "L345 and the L635 caption both print an identical 4.7% false-alarm rate on real "
        "placebo windows")


def test_R14_the_iso_fpr_match_on_real_ethereum_is_lost_under_the_re_keying(race, legacy_race):
    """
    A SELF-INVALIDATING ASSERTION. The re-keyed placebo dither moves the
    `Real_ETH` Concept calibration from 3/72 to 4/72 while the Eco arm stays at
    3/72, so that source is no longer iso-FPR and no speed comparison on it is
    interpretable. v87 publishes no delay and no ordering claim about real
    Ethereum, so nothing printed is contradicted -- and L345's own "the
    fair-coin pivot does not hold exactly" is the clause this corroborates.

    The `_legacy_seeds` arm, which shares the witness's dither, DOES match at
    3/72, which is what attributes the loss to the entropy migration rather than
    to the port.

    If a later campaign restores the match, this test fires and what must change
    is `docs/sections/R14.md` and `AUDIT_R14.md`, never this assertion.
    """
    unmatched = sorted(s for s in SOURCES
                       if not bool(race[race['source'] == s]['iso_fpr_matched'].all()))
    assert unmatched == ['Real_ETH'], (
        f"control C2 fires on {unmatched}; the section and the audit describe it firing on "
        f"Real_ETH alone")
    sub = race[race['source'] == 'Real_ETH']
    counts = {arm: int(sub[sub['arm'] == arm]['FPR_count'].iloc[0]) for arm in ARMS}
    assert counts['Concept'] != counts['Eco']
    legacy = legacy_race[legacy_race['source'] == 'Real_ETH']
    assert legacy['FPR_achieved'].nunique() == 1, (
        "the legacy-seed arm shares the witness's dither and must reproduce its 3/72 match; if it "
        "does not, the loss is a port error and not the entropy migration")
    assert int(legacy[legacy['arm'] == 'Concept']['FPR_count'].iloc[0]) == 3


# =====================================================================
# BLOCKING ASSERTIONS -- C1, THE PAIRWISE-RELIABLE GRID
# =====================================================================

def test_R14_no_aggregate_reads_a_cell_the_caption_draws_hollow(race, macros):
    """
    C1. v87's L635 caption renders `DetRate < 0.9` cells as hollow markers
    precisely because their ADD is conditional on too few detections. Every
    published aggregate is re-derived here over the grid recomputed from the
    persisted CSV, and every macro is re-derived over that grid.
    """
    for source in SOURCES:
        grid = pairwise_reliable(race, source)
        sub = race[race['source'] == source]
        for c in grid:
            assert bool(sub[sub['c'] == c]['add_reliable'].all())
        assert bool((sub[sub['c'].isin(grid)]['DetRate'] >= DET_RATE_FLOOR).all())
        assert bool((sub['add_reliable'] == (sub['DetRate'] >= DET_RATE_FLOOR)).all()), (
            "`add_reliable` must be the caption's rule and nothing else")
    real_grid = pairwise_reliable(race, 'Real_BTC')
    synth_grid = pairwise_reliable(race, 'Synth_BTC')
    assert V87_NAMED_C_LOW in real_grid and V87_NAMED_C_PARITY in real_grid, (
        "L345 names c = 0.35 and c = 1.5; both must be inside the reliable range the sentence "
        "reads them over")
    real = ratios_over(race, 'Real_BTC', real_grid)
    synth = ratios_over(race, 'Synth_BTC', synth_grid)
    assert macros['RFourteenRatioRealMean'] == f"{float(np.mean(real)):.2f}"
    assert macros['RFourteenRatioSynthMean'] == f"{float(np.mean(synth)):.2f}"
    assert macros['RFourteenRatioSynthMin'] == f"{float(np.min(synth)):.2f}"
    assert macros['RFourteenRatioSynthMax'] == f"{float(np.max(synth)):.2f}"
    assert macros['RFourteenRatioRealAtCPointThreeFive'] == \
        f"{float(real[real_grid.index(V87_NAMED_C_LOW)]):.2f}"
    assert macros['RFourteenRatioRealAtParity'] == \
        f"{float(real[real_grid.index(V87_NAMED_C_PARITY)]):.2f}"
    assert int(macros['RFourteenUnreliableCells']) == int((~race['add_reliable']).sum())
    assert int(macros['RFourteenTotalCells']) == len(race) == 88


def test_R14_the_derived_reliability_rule_reproduces_the_delivered_literal(witness_race):
    """
    The delivered `verify_invariants` selects `c >= 0.35` by literal. The rule
    the port uses instead -- BOTH arms at `DetRate >= 0.9` -- is checked against
    the WITNESS, where the two must agree: that agreement is what licenses
    replacing the literal, and it is a statement about the submitted campaign,
    not about this one.
    """
    for source in ('Real_BTC', 'Synth_BTC'):
        derived = pairwise_reliable(witness_race, source)
        literal = [c for c in C_GRID if c >= V87_NAMED_C_LOW]
        assert derived == literal, (
            f"on the submitted campaign the derived rule selects {derived} for {source} while the "
            f"delivered literal selects {literal}; the port may not replace one by the other")
        assert len(derived) == 7, (
            "seven magnitudes, which is the length of the reference vectors the delivered "
            "verify_invariants carries")


# =====================================================================
# BLOCKING ASSERTIONS -- THE NUMERALS v87 PRINTS
# =====================================================================

def test_R14_the_bitcoin_numerals_of_L345_and_the_caption_reproduce(race, diagnostics, macros):
    """
    Every quantity v87 prints about Bitcoin, at v87's own printing precision.
    """
    btc = diagnostics[diagnostics['source'] == 'BTC'].iloc[0]
    assert rounds_to(btc['nu_hat'], V87_NU_HAT_BTC, 2)
    assert 2.0 < float(btc['nu_hat']) < 4.0, (
        "L345 places BTC 'well inside the heavy-tailed regime': the variance of a standardized "
        "Student-t exists iff nu > 2 and its fourth moment iff nu > 4, so 2 < nu_hat < 4 is the "
        "regime the sentence names")
    assert float(btc['FPR_C_real']) == float(btc['FPR_E_real'])
    assert rounds_to(100.0 * float(btc['FPR_C_real']), V87_ISO_FPR_PERCENT, 1)
    grid = pairwise_reliable(race, 'Real_BTC')
    values = ratios_over(race, 'Real_BTC', grid)
    assert rounds_to(values[grid.index(V87_NAMED_C_LOW)], V87_RATIO_REAL_AT_C_LOW, 2)
    assert rounds_to(values[grid.index(V87_NAMED_C_PARITY)], V87_RATIO_REAL_AT_PARITY, 2)
    assert rounds_to(np.mean(values), V87_RATIO_REAL_MEAN, 2)
    assert float(np.mean(values)) < 1.0, (
        "L345: 'the sign filter leads across the reliable range'")
    assert values[grid.index(V87_NAMED_C_PARITY)] > values[grid.index(V87_NAMED_C_LOW)], (
        "L345 reads the ratio as 'running from 0.74 at c = 0.35 to parity at c = 1.5'; the "
        "direction of that run is what the sentence asserts")
    assert macros['RFourteenNuHatBtc'] == f"{float(btc['nu_hat']):.2f}"
    assert macros['RFourteenIsoFprBtc'] == f"{100.0 * float(btc['FPR_C_real']):.1f}\\%"
    assert int(macros['RFourteenOnsetsBtc']) == V87_ONSETS_BTC
    assert macros['RFourteenParityMagnitude'] == f"{V87_NAMED_C_PARITY:g}"


def test_R14_the_ethereum_boundary_of_L345_reproduces(race, diagnostics, macros):
    """
    L345 states its own limitation on Ethereum: the recentred sign stream fails
    whiteness at `p = 0.019`, and the synthetic control does not recover the
    light-tailed ordering at its 72 onsets. Reproducing a self-critical claim
    takes ordinary scrutiny under preamble S3's asymmetry rule; it is asserted
    here because it is published, not because it is favourable.
    """
    eth = diagnostics[diagnostics['source'] == 'ETH'].iloc[0]
    btc = diagnostics[diagnostics['source'] == 'BTC'].iloc[0]
    assert rounds_to(eth['lb_pvalue'], V87_LJUNG_BOX_ETH, 3)
    assert float(eth['lb_pvalue']) < V87_LJUNG_BOX_LEVEL, (
        "L345: ETH's 'recentred sign stream fails whiteness'")
    assert float(btc['lb_pvalue']) >= V87_LJUNG_BOX_LEVEL, (
        "the contrast the sentence draws needs BTC's sign stream to pass the same test")
    assert int(race[race['source'] == 'Real_ETH']['n_onsets'].iloc[0]) == V87_ONSETS_ETH
    grid = pairwise_reliable(race, 'Synth_ETH')
    assert len(grid) > 0
    mean_ratio = float(np.mean(ratios_over(race, 'Synth_ETH', grid)))
    assert mean_ratio < 1.0, (
        "L345: 'the synthetic control does not recover the light-tailed ordering at its 72 "
        "onsets'. The light-tailed ordering is Eco-L1-faster, i.e. a ratio above 1; a mean below "
        "1 is the failure the sentence reports.")
    assert int(macros['RFourteenOnsetsEth']) == V87_ONSETS_ETH
    assert macros['RFourteenLjungBoxEth'] == f"{float(eth['lb_pvalue']):.3f}"
    assert macros['RFourteenNuHatEth'] == f"{float(eth['nu_hat']):.2f}"


def test_R14_the_synthetic_control_numerals_of_L345_do_not_reproduce_at_their_printed_precision(
        race, macros):
    """
    THE SELF-INVALIDATING ASSERTION the deviation `R14-campaign-redraw` is
    written around.

    v87 L345 prints the quasi-Gaussian control as `0.98`--`1.14`, mean `1.06`.
    The 128-bit re-keying redraws the `t_30` series outright, and none of the
    three rounds to its printed value any more.

    The QUALITATIVE claim is a different question and is asserted alongside:
    L345 says the control INVERTS the ordering to Eco-L1-faster, which is a mean
    ratio above 1, and it still is. A single magnitude below parity falsifies
    nothing -- v87 itself prints a range whose lower end, 0.98, is already on
    the other side of parity.

    If a later campaign brings any of the three back, this test fires, and what
    must then change is `docs/DEVIATIONS.md` -- the entry is withdrawn -- never
    this assertion.
    """
    grid = pairwise_reliable(race, 'Synth_BTC')
    values = ratios_over(race, 'Synth_BTC', grid)
    mean_ratio = float(np.mean(values))
    assert not rounds_to(mean_ratio, V87_RATIO_SYNTH_MEAN, 2), (
        f"the regenerated t_30 mean ratio is {mean_ratio!r}, which now rounds to v87's printed "
        f"1.06. The deviation `R14-campaign-redraw` is registered on the fact that it does NOT; "
        f"if it now does, the register entry is what must be withdrawn.")
    assert not rounds_to(np.min(values), V87_RATIO_SYNTH_MIN, 2)
    assert not rounds_to(np.max(values), V87_RATIO_SYNTH_MAX, 2)
    # The qualitative claim survives, and it is the only thing that gates.
    assert mean_ratio > 1.0, (
        "L345: the quasi-Gaussian control 'inverts the ordering to Eco-L1-faster'. A mean ratio "
        "at or below 1 falsifies that, which is a D3 and stops the campaign; it does not.")
    assert macros['RFourteenRatioSynthMean'] == f"{mean_ratio:.2f}"


def test_R14_the_real_bitcoin_race_is_untouched_by_the_re_keying(race, witness_race):
    """
    The other half of the same deviation, and the reason its scope is the
    synthetic controls alone. `FPR_achieved` on real BTC is the discrete count
    5/106 and the +/-1e-6 dither only breaks CUSUM ties, so the real arm is
    insensitive to the migration. Asserted against the WITNESS because these are
    the quantities the deviation claims did NOT move; if they had, the register
    entry would be wrong in the other direction.
    """
    new = race[race['source'] == 'Real_BTC'].sort_values(['c', 'arm']).reset_index(drop=True)
    old = witness_race[witness_race['source'] == 'Real_BTC'].sort_values(
        ['c', 'arm']).reset_index(drop=True)
    assert len(new) == len(old) == len(C_GRID) * len(ARMS)
    for column in ('n_onsets', 'FPR_achieved', 'DetRate', 'ADD', 'add_reliable'):
        assert bool((new[column] == old[column]).all()), (
            f"`{column}` moves on Real_BTC between the submitted campaign and this one; the "
            f"deviation `R14-campaign-redraw` states that the real arm does not move, and that "
            f"statement is what must be revised")


# =====================================================================
# BLOCKING ASSERTIONS -- THE DESIGN EFFECT AND THE INTERVALS
# =====================================================================

def test_R14_the_design_effect_is_computed_from_the_mechanism_and_never_below_one(race):
    """
    S4bis, sixth corollary. Consecutive onsets are the first trading days of
    consecutive months, about 21 trading days apart, and a detection window is
    500 trading days, so two onsets share observations for `ceil(500/21) = 24`
    monthly steps. `K` is that number and comes from the mechanism, never from
    the observed autocorrelation.
    """
    assert K_LAGS == math.ceil(H_DET / TRADING_DAYS_PER_MONTH) == 24
    assert bool((race['deff'] >= 1.0).all()), (
        "a design effect below 1 would advertise more independent readings than the sample holds")
    assert bool((race['n_eff'] <= race['n_detected'] + 1e-12).all())
    assert bool((race['SEM_design'] >= race['SEM'] - 1e-12).all()), (
        "the delivered SEM assumes independent onsets, so the design-corrected one can only be "
        "wider")
    detected = race[race['n_detected'] > 1]
    assert bool(np.allclose(detected['n_eff'], detected['n_detected'] / detected['deff'],
                            rtol=CLOSED_FORM_RTOL, atol=0.0))
    assert bool(np.allclose(detected['SEM_design'], detected['SEM'] * np.sqrt(detected['deff']),
                            rtol=CLOSED_FORM_RTOL, atol=0.0))
    for row in race.itertuples(index=False):
        assert row.deff_lags == min(K_LAGS, max(row.n_detected - 1, 0)), (
            "the lag count is the mechanism's 24, truncated only when the detected subset is "
            "shorter than that")
    assert bool(race['deff_clamped'].any()), (
        "no cell is clamped, so the clamp is dead code; if the campaign no longer produces a "
        "negative-autocorrelation estimate, AUDIT_R14.md's account of it must change")


def test_R14_every_persisted_interval_is_a_wilson_interval_inside_the_unit_square(race):
    """
    The delivered intervals are recomputed from a second algebraic form of the
    same closed form, and preamble S7 requires every persisted bound to be
    clamped into [0, 1] before it reaches disk.
    """
    for column in ('CI_low', 'CI_high', 'CI_low_design', 'CI_high_design', 'DetRate'):
        assert bool((race[column] >= 0.0).all()) and bool((race[column] <= 1.0).all())
    assert bool((race['CI_low'] <= race['DetRate'] + 1e-12).all())
    assert bool((race['DetRate'] <= race['CI_high'] + 1e-12).all())
    assert bool((race['CI_low_design'] <= race['CI_high_design']).all())
    for row in race.itertuples(index=False):
        low, high = wilson_score_interval(int(row.n_detected), int(row.n_onsets))
        assert abs(row.CI_low - low) <= CLOSED_FORM_RTOL * max(1.0, low)
        assert abs(row.CI_high - high) <= CLOSED_FORM_RTOL * max(1.0, high)
        if row.n_eff > 0.0:
            dl, dh = wilson_score_interval(row.DetRate * row.n_eff, row.n_eff)
            assert abs(row.CI_low_design - max(0.0, min(1.0, dl))) <= 1e-12
            assert abs(row.CI_high_design - max(0.0, min(1.0, dh))) <= 1e-12
        assert row.CI_high_design >= row.CI_high - 1e-12 or row.CI_high >= 1.0 - 1e-12
        assert row.CI_low_design <= row.CI_low + 1e-12 or row.CI_low <= 1e-12


def test_R14_the_qmle_fallback_counters_are_reported_even_at_zero(race, qmle):
    """
    C3. A fallback counter reported only when it is non-zero establishes nothing
    about the runs where it is not, which is why `protocol_24c` carries
    `Fallback_Frac = 0` and why the port persists it per source as well.
    """
    values = dict(zip(qmle['Metric'], qmle['Value']))
    assert float(values['Fallback_Frac']) == 0.0
    assert float(values['Frozen_Frac']) == 0.0
    assert float(values['N_Converged']) == float(values['N_Sims'])
    assert 0.0 < float(values['Median_Bias']) < 0.05, (
        "the delivered G2 admissibility band on the recovery instrument")
    for column in ('qmle_n_non_converged', 'qmle_n_frozen', 'qmle_fallback_frac'):
        assert column in race.columns
        assert bool((race[column] == 0).all()), (
            "a single frozen or non-converged pre-onset fit would mean an ADD read off a fit no "
            "optimiser produced; preamble S4.3 makes that fatal, so a shipped CSV cannot carry one")


# =====================================================================
# BLOCKING ASSERTIONS -- THE LEGACY-SEED PORT-FIDELITY ARM
# =====================================================================

def test_R14_the_legacy_seed_arm_reproduces_every_discrete_quantity_of_the_witness(
        legacy_race, legacy_diagnostics, witness_race, witness_diagnostics):
    """
    The `_legacy_seeds` arm shares the witness's seeds, so the only admissible
    drift is the `float_precision='round_trip'` parser change and the BLAS
    pinning -- both of which perturb a float by about one ULP and neither of
    which can change a COUNT. Every discrete quantity is therefore asserted
    exactly equal.

    `ADD` gets no tolerance here. A CUSUM crossing is a discontinuous function
    of its stream, so a 1-ULP input change legitimately moves a delay by a whole
    trading day; the reporting test below prints how many cells moved and
    asserts nothing on it.
    """
    new = legacy_race.sort_values(['source', 'c', 'arm']).reset_index(drop=True)
    old = witness_race.sort_values(['source', 'c', 'arm']).reset_index(drop=True)
    assert len(new) == len(old) == 88
    for column in ('source', 'ticker', 'arm', 'c', 'n_onsets', 'FPR_achieved', 'DetRate',
                   'add_reliable'):
        assert bool((new[column] == old[column]).all()), (
            f"`{column}` is discrete or exactly determined and differs between the legacy-seed "
            f"arm and the witness; that is a transcription defect in the port, not a redraw")
    assert int((~new['add_reliable']).sum()) == int((~old['add_reliable']).sum()) == 25, (
        "the R14 prompt section 2.1 states 25 unreliable cells of 88, and the legacy arm must "
        "reproduce the count exactly")
    for source in SOURCES:
        assert pairwise_reliable(new, source) == pairwise_reliable(old, source)
    for column in ('nu_hat', 'lb_pvalue', 'FPR_C_real', 'FPR_E_real'):
        assert bool((legacy_diagnostics[column] == witness_diagnostics[column]).all()), (
            f"`{column}` moves on the legacy-seed arm; only the round_trip parser separates it "
            f"from the submitted campaign")


def test_R14_the_legacy_seed_artefacts_declare_that_they_certify_no_published_value(legacy_macros):
    """
    Control S4.3 requires a deliberately selected alternative path to be
    stamped in the name of its output. The stamp is necessary and not
    sufficient: the macro file says in its own header what it is for, because a
    file called `R14_claims_legacy_seeds.tex` is one `\\input` away from being
    mistaken for the real one.
    """
    text = (TABLES_DIR / "R14_claims_legacy_seeds.tex").read_text()
    assert "CERTIFY NO v87 VALUE" in text
    assert set(legacy_macros) == set(_macros("R14_claims.tex")), (
        "the two arms must emit the same macro NAMES, or the diagnostic is not comparable with "
        "the arm it diagnoses")
    for name in ('R14_crypto_isofpr_race', 'R14_crypto_diagnostics', 'R14_qmle_recovery',
                 'R14_onset_delays'):
        assert (DATA_DIR / f"{name}_legacy_seeds.csv").exists(), (
            "every output of the diagnostic arm is stamped, not just the ones that differ")


# =====================================================================
# BLOCKING ASSERTIONS -- THE CONTROLS THAT ARE STATIC
# =====================================================================

def test_R14_the_carried_primitives_are_byte_identical_to_the_files_that_own_them():
    """
    C6, re-run by a second extraction rather than trusted from the log. Preamble
    S4.2 forbids hoisting a scientific primitive into `experiments/common/`, and
    the reason is measurable: the same four routine names exist elsewhere in
    this repository with different bodies, so borrowing one would move a
    published value.
    """
    from_witness = ("_garch_nll", "fit_garch_qmle", "strict_cusum", "bilateral_delay",
                    "bisect_fpr", "wilson_ci", "compute_onsets")
    from_r13 = ("get_deterministic_seed", "seed_sequence_for", "rng_for")
    mine = top_level_segments(EXPERIMENT, set(from_witness) | set(from_r13))
    witness = top_level_segments(WITNESS_SCRIPT, set(from_witness))
    r13 = top_level_segments(R13_SCRIPT, set(from_r13))
    for name in from_witness:
        assert mine[name] == witness[name], f"{name} has drifted from {WITNESS_SCRIPT.name}"
    for name in from_r13:
        assert mine[name] == r13[name], f"{name} has drifted from {R13_SCRIPT.name}"
    # The duplication is deliberate, and this is the evidence for it: R14's
    # GARCH quasi-likelihood is NOT R01's, which is the copy R13 carries.
    r01 = top_level_segments(
        ROOT / "experiments" / "R01_real_world_backtest" / "exp_R01_real_world_backtest.py",
        {"_garch_nll", "fit_garch_qmle", "strict_cusum", "wilson_ci"})
    for name in ("_garch_nll", "fit_garch_qmle", "strict_cusum", "wilson_ci"):
        assert mine[name] != r01[name], (
            f"{name} is now identical to R01's copy; if the two have genuinely converged, the "
            f"justification recorded in AUDIT_R14.md for duplicating it must be revised")


def test_R14_no_draw_reaches_the_global_numpy_stream():
    """
    C10. The delivered script sets `np.random.seed(42)` and `random.seed(42)` at
    module level and this port drops both, which is only admissible if no draw
    consumed them. The same walk requires `np.random.RandomState` to appear
    inside the three legacy-seed brokers and nowhere else.
    """
    non_drawing = {"RandomState", "SeedSequence", "default_rng", "seed"}
    brokers = {"dither_vector", "synth_generator", "qmle_innovation_streams"}
    for path, exempt in ((WITNESS_SCRIPT, None), (EXPERIMENT, brokers)):
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
                    f"{Path(path).name}::{scope} draws np.random.{child.attr} from the implicitly "
                    f"seeded global stream")
                if exempt is not None and child.attr == "RandomState":
                    assert scope in exempt, (
                        f"{Path(path).name}::{scope} constructs a RandomState outside the "
                        f"legacy-seed brokers {sorted(exempt)}")


def test_R14_every_square_root_of_a_sample_size_follows_a_design_effect():
    """
    S4bis's sixth corollary made mechanical. A bare `np.sqrt(len(...))` is a
    form defect proscribed exactly as a bare `except:` is, and the rule is that
    the design effect is computed and logged in the same logical block just
    above it.
    """
    text = EXPERIMENT.read_text()
    lines = text.splitlines()
    # The module docstring states the rule in prose and quotes the construct it
    # bans, so the scan starts after it; comment lines are skipped for the same
    # reason. What is checked is executable code.
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
        if "design_effect(" not in window:
            offenders.append((i + 1, line.strip()))
    assert not offenders, (
        f"a square root of a sample size is taken without the design effect computed in the same "
        f"block above it: {offenders}")


# =====================================================================
# BLOCKING ASSERTIONS -- FILE HYGIENE THE PREAMBLE IMPOSES
# =====================================================================

def test_R14_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix(macros):
    assert macros, "R14_claims.tex carries no macro"
    for name, body in macros.items():
        assert name.startswith(MACRO_PREFIX), (
            f"{name} does not carry the cardinal prefix {MACRO_PREFIX}. Preamble S6 fixes "
            f"\\R<Ordinal><Claim> with the ordinal in English words, and the repository realises "
            f"cardinals throughout (ROne ... RSix, REleven, RThirteen, RSixteen, REighteen).")
        assert not name.startswith("RFourteenth"), "cardinal, never ordinal"
        assert 'nan' not in body.lower(), f"macro {name} carries the body {body!r}"
        assert body.strip() != ""
    assert len(macros) == 17


def test_R14_every_produced_text_file_ends_in_a_newline():
    """
    Preamble S6: docs/sections/*.md and requirements/*.txt are assembled by
    concatenation, and a missing newline glues two dependencies onto one line.
    """
    for path in (TABLES_DIR / "R14_claims.tex",
                 TABLES_DIR / "R14_claims_legacy_seeds.tex",
                 ROOT / "requirements" / "R14.txt",
                 ROOT / "docs" / "sections" / "R14.md",
                 ROOT / "docs" / "audits" / "AUDIT_R14.md"):
        assert path.exists(), f"Missing deliverable: {path}"
        assert path.read_text().endswith("\n"), f"{path} does not end in a newline"


def test_R14_the_produced_sources_and_logs_carry_no_confirmatory_language():
    """
    Control S4.4. The banned words attribute the value of a proof to a
    measurement; neutral technical uses stay licit and none of them matches this
    pattern.
    """
    pattern = re.compile(
        r"proves|proven|perfectly valid|validates the (theorem|thesis|claim)|confirms the|"
        r"as expected|triumph|victory|irrefutable|brilliant", re.IGNORECASE)
    targets = [EXPERIMENT,
               ROOT / "docs" / "sections" / "R14.md",
               ROOT / "docs" / "audits" / "AUDIT_R14.md",
               ROOT / "logs" / "R14_crypto_isofpr" / "exp_R14_crypto_isofpr.log",
               ROOT / "logs" / "R14_crypto_isofpr" / "exp_R14_crypto_isofpr_legacy_seeds.log"]
    for path in targets:
        if not path.exists():
            continue
        hits = [line for line in path.read_text().splitlines() if pattern.search(line)]
        assert not hits, f"{path.name} carries confirmatory language: {hits[:3]}"


def test_R14_the_produced_sources_carry_no_banned_construct():
    """Preamble S7: no `iterrows`, no bare `except:`, no absolute path."""
    text = EXPERIMENT.read_text()
    assert "iterrows" not in text
    assert not re.search(r"except\s*:", text)
    assert not re.search(r"['\"]/home/", text), "no absolute path may be embedded"
    assert "run_all.sh" not in text and "run_tests.sh" not in text, (
        "the shared orchestrators are never touched by an experiment")
    orchestrator = (ROOT / "run_experiment_R14.sh").read_text()
    executable = [line for line in orchestrator.splitlines()
                  if line.strip() and not line.lstrip().startswith("#")]
    assert not any("pytest" in line for line in executable), (
        "preamble S6: the test suite is the exclusive remit of run_tests.sh")
    assert "--legacy-seeds" in orchestrator, (
        "the diagnostic arm runs unconditionally; running it only when a result looks wrong turns "
        "it into an instrument of selection")


# =====================================================================
# REPORTING -- PRINTS WHAT R14 MEASURED, ASSERTS NOTHING
# =====================================================================

def test_R14_report_the_campaign_against_its_witness(race, legacy_race, witness_race):
    """
    The D0-D3 classification of preamble S3, computed rather than asserted, and
    the port-fidelity separation the legacy arm exists to provide.
    """
    print("\n" + "=" * 78)
    print("R14 -- the regenerated campaign against the submitted campaign's witness")
    print("=" * 78)
    old = witness_race.sort_values(['source', 'c', 'arm']).reset_index(drop=True)
    for label, frame in (("migrated (default)", race), ("legacy-seeds (diagnostic)", legacy_race)):
        new = frame.sort_values(['source', 'c', 'arm']).reset_index(drop=True)
        print(f"  {label}:")
        for source in SOURCES:
            a = new[new['source'] == source].reset_index(drop=True)
            b = old[old['source'] == source].reset_index(drop=True)
            moved = int((a['ADD'].astype(float) != b['ADD'].astype(float)).sum())
            worst = float((a['ADD'].astype(float) - b['ADD'].astype(float)).abs().max())
            flips = int((a['add_reliable'] != b['add_reliable']).sum())
            lam = float((a['lambda_star'].astype(float)
                         - b['lambda_star'].astype(float)).abs().max())
            print(f"    {source:<10} ADD cells moved {moved:>2}/{len(a)}, worst |dADD| "
                  f"{worst:>10.4f}, add_reliable flips {flips}, worst |dlambda*| {lam:.3g}")
    print("  The legacy arm shares the witness's seeds, so what it does NOT reproduce is the")
    print("  port's own error budget; the migrated arm's remaining movement is the re-keying.")
    print("=" * 78)


def test_R14_report_the_design_effect_and_the_reliable_grids(race):
    print("\n" + "=" * 78)
    print("R14 -- design effect over the pairwise-reliable grid (K = 24 monthly steps)")
    print("=" * 78)
    for source in SOURCES:
        grid = pairwise_reliable(race, source)
        sub = race[(race['source'] == source) & (race['c'].isin(grid))]
        print(f"  {source:<10} reliable grid {grid}")
        print(f"    {'c':>6} {'arm':<8} {'n_det':>6} {'deff':>9} {'n_eff':>9} {'SEM':>9} "
              f"{'SEM_design':>11} {'clamped':>8}")
        for row in sub.sort_values(['c', 'arm']).itertuples(index=False):
            print(f"    {row.c:>6} {row.arm:<8} {row.n_detected:>6} {row.deff:>9.4f} "
                  f"{row.n_eff:>9.4f} {row.SEM:>9.4f} {row.SEM_design:>11.4f} "
                  f"{str(row.deff_clamped):>8}")
    clamped = int(race['deff_clamped'].sum())
    print(f"  {clamped} of {len(race)} cells have a negative-autocorrelation estimate clamped to")
    print("  deff = 1: the Kish sum can fall below 1 on a finite sample, where it would claim")
    print("  more independent readings than the cell contains.")
    print("=" * 78)


def test_R14_report_the_ratio_series_of_every_source(race):
    print("\n" + "=" * 78)
    print("R14 -- ADD_Concept / ADD_Eco over each pairwise-reliable grid")
    print("=" * 78)
    for source in SOURCES:
        grid = pairwise_reliable(race, source)
        values = ratios_over(race, source, grid)
        matched = bool(race[race['source'] == source]['iso_fpr_matched'].all())
        print(f"  {source:<10} n = {len(grid)}, mean {np.mean(values):.6f}, "
              f"min {np.min(values):.6f}, max {np.max(values):.6f}, "
              f"{int((values < 1.0).sum())} of {len(values)} below parity"
              + ("" if matched else "   [NOT ISO-FPR -- descriptive only, control C2 fired]"))
        print("    " + ", ".join(f"c={c}: {v:.4f}" for c, v in zip(grid, values)))
    print("=" * 78)
