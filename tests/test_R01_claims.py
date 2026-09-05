"""
Test suite for R01 Real World Backtest.

Validates mathematical invariance and non-regression against baseline claims
for GARCH calibrations, CUSUM trajectories, injection detection, placebo
controls, and symmetry properties.
"""

import math

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
R01_DATA_DIR = BASE_DIR / "results" / "R01_real_world_backtest" / "data"

def test_r01_models():
    """Validates GARCH(1,1) QMLE parameter calibrations and whitening bounds."""
    df = pd.read_csv(R01_DATA_DIR / "R01_garch_models.csv", float_precision='round_trip').set_index('Ticker')
    
    assert df.loc['SPY', 'gamma_hat'] == 14.998367977816738
    assert df.loc['SPY', 'lb_pvalue_warmup'] == 0.21585172235032324
    assert df.loc['SPY', 'n_days'] == 6414
    assert df.loc['SPY', 'data_start'] == "2000-01-04"
    assert df.loc['SPY', 'data_end'] == "2025-07-07"
    assert df.loc['SPY', 'alpha'] == 0.211551
    assert df.loc['SPY', 'beta'] == 0.729081
    assert df.loc['SPY', 'q_hat'] == 0.558648111332008
    # omega and sigma_unc are the only quantities the single-threaded BLAS
    # bootstrap moves. The submitted campaign ran under multithreaded BLAS, so
    # exact agreement is unattainable once the determinism protocol is enforced: this is
    # a deviation of the manuscript from the compliant pipeline, not a defect.
    # The budget below is set from the largest relative drift measured across the
    # four tickers (2.7e-14 on PFF omega), rounded up one decade to 1e-13. It is
    # NOT set from the observed SPY value, and it must not be widened to make a
    # future run pass: a drift beyond this budget indicates a mechanism change,
    # not floating-point noise, and must be investigated.
    assert math.isclose(df.loc['SPY', 'omega'], 5.1751719325974024e-06, rel_tol=1e-13)
    assert math.isclose(df.loc['SPY', 'sigma_unc'], 0.00933654472777823, rel_tol=1e-13)
    
    assert df.loc['PFF', 'gamma_hat'] == 2.579247897388547
    assert df.loc['VNQ', 'gamma_hat'] == 4.212317152289107
    assert df.loc['BWX', 'gamma_hat'] == 5.813386828034849
    
    assert (df['qmle_converged'] == True).all()
    assert (df['n_truncated_windows'] == 0).all()

# Reference values from the submitted campaign
# (R01_covid_trajectories.csv), read back with float_precision='round_trip'.
# Transcribing them from a default pandas read is unsafe: the fast float parser is
# not correctly rounded and returns a value one unit in the last place away, which
# manufactures a drift that does not exist.
#
# Concept: bit-identical to the submitted campaign under both the multithreaded and
#   the single-threaded bootstrap, because the sign stream consumes neither the GARCH
#   variance target nor the conditional volatility. Budget kept at zero.
# Data: eight ULP away once the determinism protocol is enforced, propagated from the
#   variance-target drift on omega. Budget set to 16 ULP, one binary decade above the
#   measured value, and not to be widened further.
REF_COVID_PEAK_DATA = 0.37192244808245406
REF_COVID_PEAK_CONCEPT = 0.45489065606361845
MAX_ULP_DRIFT_DATA = 16
MAX_ULP_DRIFT_CONCEPT = 0


def _within_ulp(observed: float, reference: float, budget: int) -> bool:
    """True when observed is at most `budget` representable doubles from reference."""
    return abs(observed - reference) <= budget * math.ulp(reference)


def test_r01_trajectories():
    """Checks COVID-19 CUSUM trajectories against the submitted campaign baseline."""
    df = pd.read_csv(R01_DATA_DIR / "R01_covid_trajectories.csv", float_precision='round_trip')
    assert len(df) == 253
    assert df['Date'].iloc[0] == "2020-01-02"
    assert df['Date'].iloc[-1] == "2020-12-31"

    peak_data = df['S_over_thr_Data'].max()
    peak_concept = df['S_over_thr_Concept'].max()
    assert _within_ulp(peak_data, REF_COVID_PEAK_DATA, MAX_ULP_DRIFT_DATA), (
        f"Data peak {peak_data!r} exceeds the {MAX_ULP_DRIFT_DATA}-ULP budget around "
        f"{REF_COVID_PEAK_DATA!r}")
    assert peak_concept == REF_COVID_PEAK_CONCEPT, (
        f"Concept peak {peak_concept!r} is not bit-identical to the submitted "
        f"{REF_COVID_PEAK_CONCEPT!r}. The sign stream does not consume the volatility "
        f"estimate, so any drift here indicates a change in the classifier input, "
        f"not floating-point noise.")

    # Neither monitor reaches its threshold: the published claim is silence.
    assert peak_data < 1.0 and peak_concept < 1.0
    assert round(peak_data, 2) == 0.37 and round(peak_concept, 2) == 0.45

def test_r01_injection_summary():
    """Validates directional injection detection rates and delays."""
    df = pd.read_csv(R01_DATA_DIR / "R01_injection_summary.csv", float_precision='round_trip')
    
    spy_data = df[(df['ETF'] == 'SPY') & (df['Pipeline'] == 'Data')].iloc[0]
    assert spy_data['DetRate'] == 0.0
    assert np.isnan(spy_data['ADD'])
    
    pff_data = df[(df['ETF'] == 'PFF') & (df['Pipeline'] == 'Data')].iloc[0]
    assert pff_data['DetRate'] == 0.3055555555555556
    assert pff_data['ADD'] == 147.8181818181818
    
    bwx_concept = df[(df['ETF'] == 'BWX') & (df['Pipeline'] == 'Concept')].iloc[0]
    assert bwx_concept['DetRate'] == 1.0
    assert bwx_concept['ADD'] == 46.22222222222222

def test_r01_placebo():
    """Validates placebo control false alarm rates under null conditions."""
    df = pd.read_csv(R01_DATA_DIR / "R01_placebo_control.csv", float_precision='round_trip')
    
    spy_concept = df[(df['ETF'] == 'SPY') & (df['Pipeline'] == 'Concept')].iloc[0]
    assert spy_concept['AlarmRate'] == 0.027777777777777776
    
    pff_data = df[(df['ETF'] == 'PFF') & (df['Pipeline'] == 'Data')].iloc[0]
    assert pff_data['AlarmRate'] == 0.2222222222222222

def test_r01_magnitude_and_symmetry():
    """Validates magnitude sweep detection rates and 2020 sign symmetry."""
    df_mag = pd.read_csv(R01_DATA_DIR / "R01_magnitude_sweep.csv")
    assert len(df_mag) == 24
    
    df_sym = pd.read_csv(R01_DATA_DIR / "R01_symmetry_2020.csv", float_precision='round_trip').set_index('Ticker')
    assert df_sym.loc['SPY', 'q_hat_2020'] == 0.5770750988142292
    assert df_sym.loc['SPY', 'lb_pvalue_2020'] == 0.5531305507685548
    assert df_sym.loc['SPY', 'n_days_2020'] == 253
