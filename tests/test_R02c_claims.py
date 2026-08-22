import pytest
import pandas as pd
from pathlib import Path
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "results" / "R02c_horizon_sweep" / "data"

@pytest.fixture
def stats_df():
    csv_path = DATA_DIR / "R02c_rejection_vs_horizon.csv"
    assert csv_path.exists(), f"Missing output artifact: {csv_path}"
    return pd.read_csv(csv_path, float_precision='round_trip')

@pytest.fixture
def streams_df():
    csv_path = DATA_DIR / "R02c_streams.csv"
    assert csv_path.exists(), f"Missing output artifact: {csv_path}"
    return pd.read_csv(csv_path, float_precision='round_trip')

def test_R02c_seed_uniqueness(streams_df):
    """
    Validates that 12 000 distinct stream coordinates were recorded.
    The actual 128-bit hash uniqueness is enforced at runtime by the script.
    The 'seed' column records the cell-local index [0, 999], so uniqueness
    must be asserted on the composite parameter key.
    """
    assert len(streams_df) == 12000
    assert len(streams_df[["nu", "n_steps", "seed"]].drop_duplicates()) == 12000

def test_R02c_negative_control_calibration(stats_df):
    """
    Checks the negative control through the calibration of the twelve cells, not
    through a per-cell gate.

    Requiring all twelve Wilson intervals to cover the nominal level fires with
    probability 1 - 0.95^12 = 46% under true coverage, so the gate is a coin flip
    that invites reseeding. The pooled rate across cells is the quantity that
    carries the information. One cell (nu=6, n=32000) sits below nominal in the
    current campaign; that is an expected downward excursion, not a defect.
    """
    n_total = int(stats_df["n_streams"].sum())
    k_total = int(round((stats_df["reject_rate_raw"] * stats_df["n_streams"]).sum()))
    z = 1.959963984540054
    p_hat = k_total / n_total
    den = 1.0 + z * z / n_total
    centre = (p_hat + z * z / (2 * n_total)) / den
    half = z * np.sqrt(p_hat * (1 - p_hat) / n_total + z * z / (4 * n_total * n_total)) / den
    low, high = centre - half, centre + half
    print(f"[R02c] pooled raw-stream rejection {p_hat:.4%}, Wilson 95% [{low:.4%}, {high:.4%}]")
    assert low <= 0.05 <= high, (
        f"Pooled negative control {p_hat:.4%} excludes the nominal level: the "
        f"distortion is not specific to the squaring step.")
    # No more than two of twelve cells may miss, which is the 99th percentile of
    # Binomial(12, 0.05) and therefore does not fire on ordinary sampling noise.
    assert int((~stats_df["contains_nominal_raw"]).sum()) <= 2


def test_R02c_eighth_moment_account_is_refuted(stats_df):
    """
    Records that the witness arm falsifies the eighth-moment explanation.

    E[eps^8] is infinite for every nu <= 8, hence at nu = 5, 6 AND 7. An account
    resting on that missing moment predicts over-rejection in all three arms.
    Pooled over the four horizons, nu = 5 and nu = 6 exclude the nominal level and
    nu = 7 does not. The account does not survive its own witness.
    """
    z = 1.959963984540054

    def pooled(nu):
        sub = stats_df[stats_df["nu"] == nu]
        n = int(sub["n_streams"].sum())
        k = int(round((sub["reject_rate_squared"] * sub["n_streams"]).sum()))
        p = k / n
        den = 1.0 + z * z / n
        c = (p + z * z / (2 * n)) / den
        h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
        return p, c - h, c + h

    for nu in (5.0, 6.0):
        p, lo, hi = pooled(nu)
        assert lo > 0.05, f"nu={nu}: pooled {p:.4%} does not exclude nominal"
    p7, lo7, hi7 = pooled(7.0)
    assert lo7 <= 0.05 <= hi7, (
        f"nu=7 pooled {p7:.4%} excludes nominal: the witness arm no longer "
        f"separates the two accounts and the analysis must be revisited.")


def test_R02c_slope_test_power_is_declared(stats_df):
    """
    Guards against reading the flat slope as a refutation of the rate hypothesis.

    The slope a decay-to-nominal would produce over this horizon range lies inside
    the measured confidence interval at every nu, so the test cannot reject that
    hypothesis. This test asserts that state of affairs explicitly, so that a later
    revision cannot quietly reinterpret the interval as evidence of absence.
    """
    span = np.log(128000 / 2000)
    for nu in (5.0, 6.0, 7.0):
        sub = stats_df[stats_df["nu"] == nu]
        rate_at_min = sub[sub["n_steps"] == 2000]["reject_rate_squared"].iloc[0]
        required = (0.05 - rate_at_min) / span
        lo = sub["slope_ci_low"].iloc[0]
        hi = sub["slope_ci_high"].iloc[0]
        assert lo <= required <= hi, (
            f"nu={nu}: the decay slope {required:.5f} now falls outside "
            f"[{lo:.5f}, {hi:.5f}]. The slope test has gained power and the "
            f"conclusion in docs/sections/R02c.md must be revisited.")

def test_R02c_control_arm_integrity(stats_df):
    """
    Validates that the nu=7 arm (baseline) holds the nominal level on squared series.
    """
    control_arm = stats_df[stats_df["nu"] == 7.0]
    failures = control_arm[~control_arm["contains_nominal_squared"]]
    assert len(failures) == 0, f"nu=7 arm drifted at horizons: {failures['n_steps'].tolist()}"

def test_R02c_continuity(stats_df):
    """
    Validates identical rejection rates at nu=5, n=8000 compared to R02b.
    """
    row = stats_df[(stats_df["nu"] == 5.0) & (stats_df["n_steps"] == 8000)].iloc[0]
    assert abs(row["reject_rate_squared"] - 0.088) < 1e-9
    assert abs(row["reject_rate_raw"] - 0.057) < 1e-9

def test_R02c_mechanism_slope_logic(stats_df):
    """
    Validates that slope tests are logically bounded without yet asserting the final verdict.
    """
    sub = stats_df[stats_df["nu"] == 5.0].iloc[0]
    assert sub["slope_ci_low"] < sub["slope_ci_high"], "Invalid Confidence Interval."
