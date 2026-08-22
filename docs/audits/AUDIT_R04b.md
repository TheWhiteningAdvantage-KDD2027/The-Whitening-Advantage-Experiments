# Audit Report: R04b Nu Grid Refinement and Crossing Point Resolution

## Theoretical Anchor

R04b instantiates the nu grid refinement within the iso-FPR race framework under a location drift model with GARCH(1,1) conditional heteroscedasticity. Three monitoring pipelines are calibrated by bisection to the same 5% false-alarm rate: Eco-L1 (GARCH-fitted parametric location monitor), Oracle-Eco (ideal bound isolating estimation cost by using true GARCH parameters), and Concept (binary sign-error stream estimating no variance). The theoretical target is Appendix Figure A3, which resolves the efficiency crossing point that R04 bracketed but could not pinpoint. The delay ratio ADD_Concept / ADD_Eco-L1 is governed by 1/(4 f_z(0)^2) for Student-t innovations, and its analytic root at nu = 4.6788 provides a property of the innovation law alone. The Gamma penalty factor is fixed at 11.58, the drift magnitude at c = 0.5, the target FPR at 0.05 with bisection tolerance 0.003 over 15 iterations. The nu grid is refined to twelve points {4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 15.0, 20.0, 30.0}, spanning the (7, 30) void where the ratio crosses unity in R04's six-point grid {3, 4, 4.5, 5, 7, 30}.

## Empirical Methodology

The pipeline executes under strict S7 determinism with single-threaded BLAS, MKL_CBWR=COMPATIBLE, and PYTHONHASHSEED=42. The experiment generates 2000 null streams of length 5000 with 500-step warm-up, fitting GARCH(1,1) by QMLE on the warm-up segment. Each stream is monitored by all three arms with CUSUM detectors using bisection-calibrated thresholds. The drift onset occurs at the warm-up boundary, and detection delays are measured as average detection delay (ADD) in steps. The efficiency ratio between Concept and each arm is computed across the nu grid. Four crossing estimators are emitted for each arm: grid bracket (model-free, resolution-limited), inferential bracket (model-free with 95% confidence), shape fit with stream-level bootstrap (2000 replicates, 250 per chunk), and analytic root. Wilson 95% confidence intervals are computed for all false-alarm rates and detection metrics using z = 1.95996 with design effect sqrt(2) = 1.413 to account for the calibration sample error. The bootstrap resamples both calibration and drifted streams by recording first passage at a ladder of 7 thresholds around the calibrated lambda*, pricing the full variance of threshold estimation.

## Metric Concordance Table with Wilson 95% CIs

| Metric | Manuscript Value | Compliant Pipeline | Deviation Class | Wilson 95% CI (Compliant) | Notes |
|--------|-----------------|-------------------|----------------|----------------------------|-------|
| Eco-L1 nu* crossing | 4.9 | fit 8.10 [7.78, 8.37], bracket [7.0, 9.0] | D3 | N/A | Published value outside entire measured interval |
| Eco-L1 nu* grid interpolation | N/A | 7.75 [7.03, 8.32] | N/A | [7.0276, 8.3249] | Two-point rule across refined grid |
| Oracle nu* crossing | 4.6 | fit 4.47 [4.31, 4.57], bracket [4.0, 5.0] | Held | N/A | Published value within bracket |
| Oracle nu* grid interpolation | N/A | 4.53 [4.35, 4.70] | N/A | [4.3480, 4.7038] | Two-point rule across refined grid |
| Estimation cost (dof, shape fit) | 0.3 | 3.62 [3.31, 3.92] | D3 | [3.3085, 3.9222] | Difference of two shape fits |
| Estimation cost (model-free bracket) | 0.3 | [2.0, 5.0] | D3 | N/A | Outer bound treating crossings as independent |
| Estimation cost (model-free interp) | 0.3 | 3.22 [2.52, 3.82] | D3 | [2.5228, 3.8245] | Difference of two interpolations |
| Analytic crossing | 4.7 | 4.6788 | Held | N/A | Rounds to 4.7 at published precision |
| AUDIT_R04 interpolation | 8.52 | 7.75 | D3 | N/A | Across unsampled (7, 30) interval on non-linear curve |
| Gaussian ceiling pi/2 | 1.5708 | 1.5708 | CONFIRMED | N/A | Max Concept/Eco-L1 ratio 1.255 well below ceiling |
| Oracle ratio at nu >= 7 | > 1.0 | > 1.0 | CONFIRMED | N/A | No second crossing exists on extended grid |
| Variance factor sqrt(2) | sqrt(2) | 1.413 | CONFIRMED | N/A | Design effect validated by probe (p < 1e-10) |
| Held-out level | 5% | 5.07% | CONFIRMED | [4.84%, 5.29%] | Pooled over 36 arms, 2000 streams each |
| Conditional calibration KS p | > 0.01 | 0.641 | CONFIRMED | N/A | Over 36 arms, 2000 replicates |
| Bootstrap replicates | N/A | 2000 | N/A | N/A | All replicates invert to finite crossing |

All Wilson 95% confidence intervals computed using z = 1.959963984540054 with design effect sqrt(2). The R04b campaign resolves the crossing point by adding six nu values inside and below the (7, 30) void, revealing that the published Eco-L1 crossing at 4.9 is a D3 falsification (the true bracket is [7.0, 9.0]), while the Oracle crossing at 4.6 is held within its bracket [4.0, 5.0]. The estimation cost claim of 0.3 dof is also a D3 falsification, with the corrected value 3.62 reflecting the estimation error under the genuine Gamma span. The analytic crossing and Gaussian ceiling claims are corroborated at published precision.

## Methodological Scope & Limitations

The audit confirms R04b achieves full computational reproducibility under S7 determinism with zero tolerance widening and no parameter tuning. The nu grid refinement is the primary mechanism: adding points at 6.0, 8.0, 9.0, 10.0, 12.0, 15.0, and 20.0 inside and around the (7, 30) void resolves the crossing location. All 21 test suites pass, confirming cardinalities, bisection convergence, calibration to 5% FPR, continuity with R04 at common points, and crossing estimator consistency. Continuity omnibus chi-square tests yield p = 0.4498 (Eco-L1) and p = 0.5736 (Oracle_Eco). Shape fit goodness tests pass (Eco-L1: p = 0.5929, Oracle: p = 0.2960). The pipeline generates 2 CSV files, 1 PNG figure, and 55 LaTeX macros, all SHA-256 verified. Limitations: The D3 falsifications indicate that two qualitative claims in v87 (Eco-L1 crossing at 4.9, estimation cost 0.3 dof) do not survive the refined grid. Four claims are corroborated (Oracle crossing at 4.6, analytic crossing at 4.7, Gaussian ceiling, no second crossing). No parameter tuning, seed manipulation, or bound adjustment was performed to reconcile deviations.
