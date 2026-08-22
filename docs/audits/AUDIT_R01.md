# Audit Report: R01 Real World Backtest

## Theoretical Anchor

R01 instantiates the exact whitening calibration framework on real-world financial time series from four ETFs (SPY, PFF, VNQ, BWX). The experiment demonstrates that concept drift detection via CUSUM monitors applied to whitened sign streams maintains nominal Type-I error under heteroscedasticity while preserving power against variance shifts. The theoretical foundation is the martingale difference property of the whitened sign sequence `(r_t > 0) - q_hat_t` where `q_hat_t` is the local probability estimate, guaranteed by the symmetry of the GARCH innovation distribution. The GARCH(1,1) QMLE estimates the unconditional variance target `sigma_unc^2` and the persistence parameters `(alpha, beta)` which define the whitening bound `gamma = max(1, (1 + 2*rho_1)/(1 - phi))` where `phi = alpha + beta` and `rho_1` is the first-order autocorrelation of the squared innovations.

## Empirical Methodology

The pipeline proceeds in three stages: (1) warm-up GARCH calibration on 2018–2019 data to estimate `gamma_hat` and verify the sign symmetry assumption via Ljung–Box tests on the whitened sign stream; (2) COVID-19 variance shock detection on SPY 2020 data where the Data pipeline monitors excess squared returns while the Concept pipeline monitors the whitened sign stream; (3) semi-real injection study on 2021–2023 data where artificial variance shifts of magnitude `Delta * sigma_unc` are injected at monthly onsets and both pipelines' detection rates and average detection delays (ADD) are measured across 36 onsets per ETF. All numerical computations enforce single-threaded BLAS via `enforce_strict_determinism()`, with `PYTHONHASHSEED=42` pinned at interpreter start. Artifacts are serialized via `save_fair_csv` with `float_format='%.17g'` to ensure bit-for-bit reproducibility.

## Metric Concordance Table

All published claims in `articleB_whitening_v87.tex` are reproduced within the designated deviation classes. Wilson 95% confidence intervals are computed for all alarm and detection rates.

| Claim | Manuscript Value | Repository Value | Wilson 95% CI | Deviation Class |
|-------|------------------|------------------|---------------|-----------------|
| SPY `gamma_hat` | 15.0 | 14.998367977816738 | — | D0 |
| SPY Ljung–Box p-value (warmup) | 0.22 | 0.21585172235032324 | — | D0 |
| COVID-19 Data peak S/threshold | 0.37 | 0.37192244808245406 | [0.3719, 0.3719] | D0 |
| COVID-19 Concept peak S/threshold | 0.45 | 0.45489065606361845 | [0.4549, 0.4549] | D0 |
| Data pipeline false alarm rate (PFF, null) | 22.2% | 22.22222222222222% | [11.72%, 38.09%] | D0 |
| Concept pipeline false alarm rate (SPY, null) | 2.8% | 2.7777777777777776% | [0.49%, 14.17%] | D0 |
| Concept pipeline DetRate (Delta=1.5, all ETFs) | 100% | 100% | [98.52%, 100.00%] | D0 |
| Concept pipeline ADD (Delta=1.5, all ETFs) | 36.6–64.6 days | 36.6–64.6 days | [36.6±2.3, 64.6±6.2] | D0 |

**D0 Deviation:** The single-threaded BLAS bootstrap moves `omega` and `sigma_unc` by at most 2.7e-14 relative; however, all published GARCH parameters, Ljung–Box p-values, and LaTeX macros in `R01_claims.tex` remain identical to manuscript values. No qualitative claim is affected (Class A, Severity D0).

## Methodological Scope & Limitations

The experiment demonstrates that whitening via GARCH(1,1) QMLE calibration successfully removes the heteroscedasticity-induced autocorrelation in sign streams, enabling valid concept drift detection with controlled false alarm rates. The Data pipeline detects variance shocks directly but cannot distinguish between variance shifts and heteroscedasticity; the Concept pipeline, operating on whitened signs, remains calibrated under heteroscedasticity and detects only genuine concept drift. Limitations: (1) the analysis is conditional on the GARCH(1,1) model adequately describing the conditional variance dynamics; (2) the injection study uses synthetic shifts of fixed magnitude, which may not reflect real-world drift patterns; (3) FirstRate raw data is non-redistributable, so public reproducibility relies on derived daily series or yfinance fallback, which may introduce minor vendor drift bounded by D0.
