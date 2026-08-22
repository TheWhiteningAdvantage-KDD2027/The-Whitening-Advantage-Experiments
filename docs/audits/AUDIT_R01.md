# Audit Report: R01 Real World Backtest

## Theoretical Anchor

R01 corroborates the GARCH penalty factor $\Gamma = 1 + 2\sum_{k\geq 1}\rho_e(k)$ and the Sign-Task Whitening Property (Proposition 1) on four ETF daily series (SPY, PFF, VNQ, BWX, 2000-2025). Under GARCH(1,1) dynamics, uncalibrated CUSUM false-positive rates approach 80% for $\Gamma \gtrsim 20$; recalibration multiplies thresholds by $\lambda \times \Gamma$. The whitening property establishes that on sign-prediction with conditionally symmetric innovations, the binary error stream of any non-anticipative classifier is i.i.d. Bernoulli(1/2), structurally insensitive to $\Gamma$ [Campbell and Dufour, 1995; Christoffersen and Diebold, 2006].

## Empirical Methodology

The pipeline executes three stages under strict single-threaded determinism (`enforce_strict_determinism()`, `PYTHONHASHSEED=42`, BLAS pins). Warm-up (2018-2019) fits GARCH(1,1) via QMLE to compute $\Gamma$ and validate concept drift absence via Ljung–Box on sign streams. COVID-19 phase (2020) monitors SPY variance shocks using recalibrated CUSUM on both data and concept pipelines. Injection study (2021-2023) tests detection across four delta factors (0.0, 0.5, 1.0, 1.5\sigma_{unc}) with 36 monthly onsets per ETF, measuring detection rates and average detection delay (ADD).

Placebo controls verify false alarm rates under null conditions; symmetry tests confirm sign-stream i.i.d. properties in 2020. All CSVs use `float_precision='round_trip'`; LaTeX macros employ `%.17g` formatting.

## Metric Concordance Table

| Metric | Manuscript | Repository | Delta | D-Class | Wilson 95% CI |
|--------|------------|------------|-------|---------|----------------|
| SPY $\Gamma$ | 15.0 | 15.0 | 0 | D0 | [15.0, 15.0] |
| PFF $\Gamma$ | 2.6 | 2.6 | 0 | D0 | [2.6, 2.6] |
| VNQ $\Gamma$ | 4.2 | 4.2 | 0 | D0 | [4.2, 4.2] |
| BWX $\Gamma$ | 5.8 | 5.8 | 0 | D0 | [5.8, 5.8] |
| COVID-19 Data Peak | 0.37 | 0.37 | 0 | D0 | [0.37, 0.37] |
| COVID-19 Concept Peak | 0.45 | 0.45 | 0 | D0 | [0.45, 0.45] |
| Placebo Data PFF Rate | 22.2% | 22.2% | 0 | D0 | [9.6%, 40.4%] |
| Placebo Concept SPY Rate | 2.8% | 2.8% | 0 | D0 | [0.5%, 14.2%] |
| Injection Data PFF Rate (\Delta=1.5) | 30.6% | 30.6% | 0 | D0 | [15.8%, 50.3%] |
| Injection Concept BWX ADD | 46.2 | 46.2 | 0 | D0 | [46.2, 46.2] |

**Deviation Summary:** D0 class only. `omega` and `sigma_unc` exhibit ≤ 2.7e-14 relative drift against the submitted campaign, but all published macros and rounded values are invariant. See `docs/DEVIATIONS.md` §1 and `docs/camera_ready_candidates/R01_v87_variance_target.md`.

## Methodological Scope & Limitations

R01 covers 25 years of daily ETF data, 253 trading days in 2020, and 36 onsets per ETF in 2021-2023. The data pipeline monitors raw returns; the concept pipeline monitors whitened sign streams. Detection uses strict CUSUM with thresholds calibrated by $\Gamma$. Limitations: (1) FirstRate intraday data is non-redistributable; yfinance provides a public fallback. (2) The D0 variance-target drift remains unclassified (A?); cause unidentified but bounded. (3) ADD statistics are conditional on detection; NaN entries indicate no alarm.
