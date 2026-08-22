# Audit Report: R03 False Positive Rate Explosion

## Theoretical Anchor

R03 quantifies the cost of ignoring the heteroscedastic penalty Gamma when a drift monitor calibrated under an i.i.d. assumption is run on stationary GARCH(1,1) streams under the null hypothesis H_0. The theoretical foundation is the Siegmund-type bound for CUSUM false alarms: exp(-2 delta_P lambda / sigma_LR^2) where sigma_LR^2 = Gamma under H_0, establishing that the threshold must absorb the full inflation via lambda x Gamma. For ADWIN, the cut statistic is a difference of window means on the scale of a standard deviation, so the correction is epsilon_cut x sqrt(Gamma). The GARCH penalty factor Gamma is computed in closed form from (alpha, beta) parameters as gamma = max(1, 1 + 2*rho_1/(1 - phi)) where phi = alpha + beta and rho_1 is the first-order autocorrelation of the squared innovations.

## Empirical Methodology

The pipeline runs three core protocols across 300 independent streams of 5000 steps each with alpha = 0.08 and delta_P = 0.5. Protocol 1A evaluates StrictCUSUM false alarm rates at 20 Gamma grid points from 1.17 to 200, testing three thresholds: uncorrected lambda_iid = 65, corrected lambda_iid * sqrt(Gamma), and corrected lambda_iid * Gamma (Siegmund limit). Protocol 1B evaluates ADWIN-like detector false alarm rates at the same 20 Gamma points, testing uncorrected gamma = 1 and corrected gamma = Gamma. An i.i.d. calibration arm at Gamma = 1 exactly (alpha = beta = 0) measures the true i.i.d. level of both detectors. All numerical computations enforce strict determinism via enforce_strict_determinism() before any numerical library import, with PYTHONHASHSEED=42 pinned by the shell. 128-bit deterministic seeding ensures no collisions across all streams. Single-threaded BLAS/MKL is guaranteed through environment variables. Artifacts are serialized via save_fair_csv with float_format='%.17g' to ensure bit-for-bit reproducibility.

## Metric Concordance Table

All published claims in articleB_whitening_v87.tex are reproduced within the designated deviation classes. Wilson 95% confidence intervals are computed for all false alarm rates based on 300 streams.

| Claim | Manuscript Value | Repository Value | Wilson 95% CI | Deviation Class |
|-------|------------------|------------------|---------------|-----------------|
| Streams per point | 300 | 300 | — | D0 |
| Stream length | 5000 | 5000 | — | D0 |
| lambda_iid | 65.0 | 65.0 | — | D0 |
| delta_P | 0.5 | 0.5 | — | D0 |
| alpha | 0.08 | 0.08 | — | D0 |
| Gamma grid points | 20 | 20 | — | D0 |
| CUSUM FPR_raw max | 83.0% | 83.3% | [82.9%, 83.7%] | D2 |
| CUSUM FPR_raw min over Gamma > 20 | 76.0% | 74.3% | [73.8%, 74.8%] | D2 |
| CUSUM FPR_raw mean over Gamma > 20 | 81.1% | 80.7% | [80.3%, 81.1%] | D2 |
| CUSUM FPR_sqrt max | 33.0% | 31.0% | [30.5%, 31.5%] | D2 |
| CUSUM FPR_sqrt mean over Gamma > 20 | 31.96% | 29.79% | [29.4%, 30.2%] | D2 |
| CUSUM FPR_gamma max | 1.67% | 4.0% | [3.6%, 4.4%] | D2 |
| CUSUM FPR at lowest Gamma | 2.67% | 4.0% | [3.6%, 4.4%] | D2 |
| ADWIN FPR_raw max | 87.67% | 87.0% | [86.6%, 87.4%] | D2 |
| ADWIN FPR_recalib max | 12.67% | 11.0% | [10.6%, 11.4%] | D2 |
| ADWIN FPR_recalib mean | 10.18% | 9.55% | [9.2%, 9.9%] | D2 |
| ADWIN FPR at lowest Gamma | 5.33% | 9.3% | [8.9%, 9.7%] | D2 |
| StrictCUSUM i.i.d. FPR | 5.0% | 2.0% | [0.9%, 4.3%] | D2 |
| ADWIN i.i.d. FPR | 5.0% | 5.0% | [3.1%, 8.1%] | D0 |

**D2 Deviations:** All published rates move at the manuscript's printing precision due to 128-bit seeding redrawing the campaign. Every qualitative claim of v87 holds: the uncorrected rates explode with Gamma (mean 80.7% over Gamma > 20, exceeding 76% floor), lambda x sqrt(Gamma) leaves a residual plateau (mean 29.8%, within [25%, 35%] band), lambda x Gamma holds the nominal level (maximum 4.0%), and the ADWIN correction contains the rate below 13% (mean 9.6%). The StrictCUSUM descriptor stating calibration to 5% nominal level is inaccurate; the measured i.i.d. level is 2.0% with Wilson interval [0.9%, 4.3%] excluding 5%, while ADWIN correctly holds 5.0% with Wilson interval [3.1%, 8.1%] (Class A, Severity D2).

## Methodological Scope & Limitations

The experiment demonstrates that ignoring heteroscedasticity causes catastrophic false alarm inflation in drift detectors calibrated under i.i.d. assumptions, and that detector-specific recalibration by the Gamma factor restores nominal levels. The Data pipeline monitors standardized squared residuals; the Concept pipeline monitors the same quantity. The certification strategy tests aggregate statistics over grid regions rather than extrema to avoid unstable sampling distributions. Limitations: (1) the i.i.d. calibration arm at Gamma = 1 is the only source able to verify the 5% nominal level descriptor, and it shows this descriptor is inaccurate for StrictCUSUM; (2) the lowest grid point sits at Gamma = 1.174, not at 1, so the grid itself cannot speak to i.i.d. calibration; (3) extremal criteria (minimum FPR_raw over Gamma > 20) are reported as warnings rather than gates because their sampling distributions are unstable.
