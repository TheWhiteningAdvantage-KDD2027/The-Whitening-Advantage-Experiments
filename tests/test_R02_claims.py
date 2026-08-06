import numpy as np
import pandas as pd
import pytest
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "results" / "R02_whitening_ljungbox" / "data"

@pytest.fixture
def streams_df():
    csv_path = DATA_DIR / "R02_ljungbox_360streams.csv"
    assert csv_path.exists(), f"Missing file {csv_path}"
    return pd.read_csv(csv_path, float_precision='round_trip')

@pytest.fixture
def diag_df():
    csv_path = DATA_DIR / "R02_independence_diagnostics.csv"
    assert csv_path.exists(), f"Missing file {csv_path}"
    return pd.read_csv(csv_path, float_precision='round_trip')

def test_stream_counts(streams_df):
    assert len(streams_df) == 360
    assert len(streams_df['regime'].unique()) == 3
    assert len(streams_df['etf'].unique()) == 4
    assert len(streams_df['seed'].unique()) == 30

def test_classifier_integrity(streams_df):
    versions = streams_df['classifier_version'].unique()
    assert len(versions) == 1
    assert "N/A" not in str(versions[0]), "Classifier silently fell back to native implementation!"

def test_data_rejection_rates(streams_df):
    for regime in ['Cal. A', 'Cal. B']:
        sub = streams_df[streams_df['regime'] == regime]
        assert (sub['p_data'] < 0.05).mean() == 1.0

def test_distinct_p_concept(streams_df):
    for regime in ['IID', 'Cal. A', 'Cal. B']:
        sub = streams_df[streams_df['regime'] == regime]
        assert sub['p_concept'].nunique() == 120, f"Seed overlap detected in {regime}"

def test_independence_diagnostics(diag_df):
    """
    Checks cross-stream independence through the calibration of the eighteen
    Pearson p-values, not through a per-test threshold.

    A pass/fail gate requiring all eighteen tests to clear a 0.05/6 Bonferroni
    threshold fires with probability 1 - (1 - 0.00833)^18 ~ 14% under true
    independence. Such a gate invites reseeding until it clears, which would
    condition the random draw on the outcome of the very control meant to
    validate it. The distribution of the p-values is the quantity that carries
    the information: under independence it is Uniform(0, 1).
    """
    from scipy import stats

    assert len(diag_df) == 18
    pvalues = diag_df['pearson_pvalue'].to_numpy()
    assert np.all((pvalues >= 0.0) & (pvalues <= 1.0))

    result = stats.kstest(pvalues, 'uniform')
    assert result.pvalue > 0.01, (
        f"Cross-stream p-values depart from Uniform(0,1): D={result.statistic:.4f}, "
        f"p={result.pvalue:.4f}. Investigate the seed derivation; do not reseed.")


def test_iid_arm_rejection_is_reported_not_asserted(streams_df):
    """
    Records the i.i.d.-arm rejection rate of the squared stream without gating on
    the 9.2% figure printed in v87.

    At n = 120 the Wilson interval around the regenerated rate contains the
    nominal 5% level, so the manuscript claim of over-rejection is not resolvable
    at this sample size. The test asserts only that the rate stays in a range
    compatible with either reading, and surfaces the value for documentation.
    """
    sub = streams_df[streams_df['regime'] == 'IID']
    rate = (sub['p_data'] < 0.05).mean()
    print(f"[R02] i.i.d.-arm p_data rejection rate: {rate:.4%} (n={len(sub)})")
    assert 0.0 <= rate <= 0.25


def test_concept_level_covered_by_wilson(streams_df):
    """Checks that the pooled binary-error rejection rate covers the nominal level."""
    k = int((streams_df['p_concept'] < 0.05).sum())
    n = len(streams_df)
    z = 1.959963984540054
    p_hat = k / n
    den = 1.0 + z * z / n
    centre = (p_hat + z * z / (2 * n)) / den
    half = z * np.sqrt(p_hat * (1 - p_hat) / n + z * z / (4 * n * n)) / den
    low, high = max(0.0, centre - half), min(1.0, centre + half)
    print(f"[R02] pooled concept rejection {p_hat:.4%}, Wilson 95% [{low:.4%}, {high:.4%}]")
    assert low <= 0.05 <= high


def test_max_clustered_pvalue_below_manuscript_bound(streams_df):
    """Checks the p < 1e-10 bound stated in v87 for the clustered calibrations."""
    clustered = streams_df[streams_df['regime'].isin(['Cal. A', 'Cal. B'])]
    assert clustered['p_data'].max() < 1e-10