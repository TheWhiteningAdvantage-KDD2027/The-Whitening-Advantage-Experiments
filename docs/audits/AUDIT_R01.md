# Audit Report: R01 Real World Backtest

## Theoretical Anchor

R01 instantiates the whitening proposition over four heteroscedastic ETF streams (SPY, PFF, VNQ, BWX) spanning 2000–2025. The theoretical construct establishes that for a martingale difference sequence, the sign stream is whitened by construction, while variance-normalized magnitudes retain temporal dependence. This yields two monitoring regimes: a variance-based detector prone to structural latency under heteroscedasticity, and a sign-based concept-drift monitor calibrated to the nominal level. The GARCH(1,1) QMLE fit provides the whitening penalty gamma, which scales the CUSUM threshold for the variance arm. The expected qualitative separation is a silent variance detector versus a concept monitor firing at every injected onset.

## Empirical Methodology

The pipeline executes in three phases. Phase 1 (2018–2019 warm-up) estimates GARCH parameters and the Ljung-Box p-value for sign autocorrelation, validating the whitening assumption. Phase 2 (2020) runs both detectors over the COVID-19 variance shock on SPY, confirming no alarm is raised. Phase 2.5 verifies sign symmetry in 2020 across all tickers. Phase 3 (2021–2023) injects directional shifts of magnitude Delta in {0.0, 0.5, 1.0, 1.5} times sigma_unc at 36 monthly onsets per ETF and records detection rates, average detection delays, and standard errors. The pipeline supports three execution modes: derived FirstRate data (default), raw FirstRate ingestion (--stage all), and public yfinance replication (--data-source yfinance).

## Concordance Table

| Claim | Published Value | Reproduced Value | Deviation Class | Wilson 95% CI | Status |
|-------|-----------------|------------------|-----------------|---------------|--------|
| gamma-hat_SPY | 15.0 | 15.0 | — | — | Exact |
| gamma-hat_PFF | 2.6 | 2.6 | — | — | Exact |
| gamma-hat_VNQ | 4.2 | 4.2 | — | — | Exact |
| gamma-hat_BWX | 5.8 | 5.8 | — | — | Exact |
| COVID-19 Data peak | 0.37 | 0.37 | D0 | — | Rounded match |
| COVID-19 Concept peak | 0.45 | 0.45 | — | — | Bit-identical |
| Data injection rate (PFF, Delta=1.5 sigma) | 30.6% | 30.6% | — | [19.6%, 43.5%] | Exact |
| Concept injection rate (BWX, Delta=1.5 sigma) | 100% | 100% | — | [90.1%, 100%] | Exact |
| Placebo Data rate (PFF) | 22.2% | 22.2% | — | [12.2%, 35.0%] | Exact |
| Placebo Concept rate range | [0%, 13.9%] | [0%, 13.9%] | — | — | Exact |

**D0 Deviation:** omega and sigma_unc drift by at most 2.7e-14 in relative terms across tickers. The cause remains unidentified. The drift is bounded, affects no published quantity, and every macro in R01_claims.tex is unchanged. The Concept arm trajectory is bit-identical; the Data arm peak rounds to the same published value. No D1-D3 deviations are present.

## Methodological Scope

The experiment validates the structural latency claim under real-world heteroscedasticity. Positive controls confirm that injected drift is reliably detected by the concept monitor. The placebo study establishes the false alarm rate under the null. Limitations: the variance-target drift source is unidentified; yfinance data spans different date ranges for PFF, VNQ, and BWX, confounding source and window effects; the pipeline depends on proprietary FirstRate data for the baseline results, though public replication is provided. The certified environment is CPython 3.12.9 with numpy 1.26.4, pandas 2.3.2, scipy 1.16.2, statsmodels 0.14.5, matplotlib 3.10.6, yfinance 1.2.0, under PYTHONHASHSEED=42 and single-threaded BLAS.

