import pytest
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "results" / "R02b_iid_arm_resolution" / "data"

@pytest.fixture
def stats_df():
    csv_path = DATA_DIR / "R02b_rejection_vs_nu.csv"
    assert csv_path.exists(), f"Missing output artifact: {csv_path}"
    return pd.read_csv(csv_path, float_precision='round_trip')

def test_negative_control_integrity(stats_df):
    """
    Validates that the negative control (Ljung-Box applied to the raw innovations) 
    holds the nominal 5% level across the entire nu grid.
    """
    failures = stats_df[stats_df["contains_nominal_raw"] == False]
    assert len(failures) == 0, f"Negative control failed at nu={failures['nu'].tolist()}"

def test_nu_seven_is_indistinguishable_from_nominal(stats_df):
    """
    Records the measured outcome at nu = 7: the Wilson interval CONTAINS the
    nominal level, so the 9.2% over-rejection printed in v87 is not reproduced.

    This test asserts the measurement, not a hoped-for verdict. An earlier
    revision asserted the opposite and was never executed against the data it
    was meant to check.
    """
    row = stats_df[stats_df["nu"] == 7.0].iloc[0]
    assert bool(row["contains_nominal_squared"]) is True
    assert row["wilson_low_squared"] <= 0.05 <= row["wilson_high_squared"]


def test_heavy_tail_arms_exclude_nominal(stats_df):
    """
    Records that the effect the manuscript describes IS present, at heavier tails
    than the manuscript states: at nu = 5 and nu = 6 the Wilson interval on the
    squared stream excludes the nominal level.
    """
    for nu in (5.0, 6.0):
        row = stats_df[stats_df["nu"] == nu].iloc[0]
        assert bool(row["contains_nominal_squared"]) is False, (
            f"nu={nu}: expected exclusion of the nominal level, got "
            f"[{row['wilson_low_squared']:.4f}, {row['wilson_high_squared']:.4f}]")
        assert row["wilson_low_squared"] > 0.05


def test_rate_ordering_heavy_versus_light(stats_df):
    """
    Checks the qualitative shape without imposing pointwise monotonicity.

    A pointwise `rates[i] >= rates[i+1]` gate fails under ordinary sampling noise
    even when the underlying trend is monotone, and invites re-drawing until it
    clears. The informative comparison is between the aggregate of the two
    heavy-tailed points and the aggregate of the light-tailed ones.
    """
    heavy = stats_df[stats_df["nu"] <= 6.0]["reject_rate_squared"].mean()
    light = stats_df[stats_df["nu"] >= 8.5]["reject_rate_squared"].mean()
    assert heavy > light, f"heavy-tail mean {heavy:.4f} not above light-tail mean {light:.4f}"


def test_negative_control_matches_squared_at_light_tails(stats_df):
    """
    Checks that squared and raw streams agree once the tails are light: any
    residual gap at nu >= 12 would indicate a defect in the squaring path rather
    than a tail effect.
    """
    light = stats_df[stats_df["nu"] >= 12.0]
    gap = (light["reject_rate_squared"] - light["reject_rate_raw"]).abs().max()
    assert gap < 0.03, f"unexplained gap of {gap:.4f} at light tails"