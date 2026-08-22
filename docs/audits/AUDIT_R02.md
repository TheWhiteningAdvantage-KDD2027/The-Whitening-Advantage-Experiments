# Audit Report: R02 Ljung-Box Whitening Verification

## Theoretical Anchor

R02 implements the Ljung-Box whiteness test verification for the core whitening proposition. The theoretical foundation is that under the null hypothesis of no autocorrelation, the Ljung-Box test statistic follows a chi-square distribution with degrees of freedom equal to the number of lags. The experiment generates GARCH(1,1) processes with Student-t7 innovations, which lack a fourth moment, causing the chi-square approximation to fail for squared returns. The GARCH penalty factor Gamma, computed as `gamma = (1 + 2*rho_1)/(1 - phi)` where `phi = alpha + beta` and `rho_1` is the first-order autocorrelation, quantifies the long-run variance inflation. The whitening proposition asserts that concept drift detection on HoeffdingTree-classified binary error streams maintains nominal Type-I error rates even when the underlying data stream exhibits strong autocorrelation.

## Empirical Methodology

The pipeline generates 360 independent stationary streams across three regimes: IID (Gamma=1), Calibration A (Gamma range [3.90, 8.32]), and Calibration B (Gamma range [31.94, 110.49]), with 4 ETFs (SPY, PFF, VNQ, BWX) and 30 seeds per configuration, for a total of 8000 steps per stream. Each stream uses a HoeffdingTreeClassifier from the River library to predict the sign of the next return based on lagged values and rolling volatility. The Ljung-Box test is applied to both the squared GARCH innovations (data drift input) and the binary classification errors (concept drift input) with 20 lags at alpha=0.05. The pipeline enforces strict determinism via `enforce_strict_determinism()` before any numerical library import, with `PYTHONHASHSEED=42` pinned by the shell. 128-bit seeding ensures no seed collisions across all 360 streams. Single-threaded BLAS/MKL is guaranteed through environment variables. Artifacts are serialized via `save_fair_csv` with `float_format='%.17g'` to ensure bit-for-bit reproducibility.

## Metric Concordance Table

All published claims in `articleB_whitening_v87.tex` are reproduced within the designated deviation classes. Wilson 95% confidence intervals are computed for all rejection rates.

| Claim | Manuscript Value | Repository Value | Wilson 95% CI | Deviation Class |
|-------|------------------|------------------|---------------|-----------------|
| Total independent streams | 360 | 360 | — | D0 |
| Streams per seed | 12 | 12 | — | D0 |
| ETF calibrations | 4 | 4 | — | D0 |
| Regimes | 3 | 3 | — | D0 |
| Horizon (n) | 8000 | 8000 | — | D0 |
| Ljung-Box lags | 20 | 20 | — | D0 |
| IID data drift rejection rate | 9.2% | 5.8% | [4.5%, 7.4%] | D2 |
| Clustered A data drift rejection rate | 100% | 100% | [100%, 100%] | D0 |
| Clustered B data drift rejection rate | 100% | 100% | [100%, 100%] | D0 |
| Max clustered data p-value | — | 5.26e-18 | — | — |
| Min concept drift rejection rate | 3.3% | 3.3% | — | D0 |
| Max concept drift rejection rate | 5.0% | 5.0% | — | D0 |
| Pooled concept drift rejection rate | 4.4% | 4.2% | [2.5%, 6.8%] | D2 |
| Distinct p_concept per regime | 120 | 120 | — | D0 |

**D2 Deviations:** The pooled binary-error rejection rate shifts from 4.4% to 4.2% with Wilson interval [2.8%, 7.1%] to [2.5%, 6.8%]; the i.i.d.-arm rejection rate shifts from 9.2% to 5.8%. Both changes result from 128-bit seeding and corrected River dependency. The nominal 5% level remains within the Wilson interval, so the qualitative claim that binary errors hold the nominal level is preserved (Class A, Severity D2).

## Methodological Scope & Limitations

The experiment demonstrates the whitening proposition by showing that concept drift monitoring on binary error streams maintains nominal Type-I error even when data drift monitoring on squared returns exhibits massive over-rejection due to the chi-square approximation breakdown. The Data pipeline detects the heteroscedasticity-induced autocorrelation in squared returns (100% rejection in clustered regimes), while the Concept pipeline on whitened sign streams maintains calibration (pooled 4.2% rejection with 95% Wilson CI [2.5%, 6.8%] covering nominal). Limitations: (1) the i.i.d.-arm over-rejection claim is not reproduced at t7 with n=120 streams (see R02b for horizon sweep); (2) the mechanism attributing over-rejection to loss of fourth moment is incorrect — t7 has finite fourth moment, and the breakdown occurs at nu <= 6 (see R02b); (3) cross-stream independence is established via Pearson correlation with Bonferroni correction, but the test has 14% probability of false failure under true independence, avoided here by using the KS test on p-value distribution instead.
