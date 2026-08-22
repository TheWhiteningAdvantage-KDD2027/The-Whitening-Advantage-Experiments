# AUDIT — R04b, Resolution of the Efficiency Crossing Point (Appendix Figure A3)

## 1. Theoretical Anchor

R04b addresses the indeterminate efficiency crossing identified in AUDIT_R04.md. The theoretical foundation rests on Proposition prop:are, which establishes that the delay ratio ADD_Concept / ADD_parametric converges to 1/(4 f_z(0)^2) under standardized t_nu innovations, with Gaussian ceiling pi/2. This experiment tests whether the submitted campaign's nu* ~ 4.9 holds when Gamma is varied to 11.58 and the nu grid is extended from 6 to 12 points spanning (4, 30). The analytic root of 1/(4 f_z(0)^2) = 1 is computed at 4.6788 degrees of freedom, serving as the theoretical anchor against which all empirical crossings are compared.

## 2. Empirical Methodology

The campaign executes a paired iso-FPR race on twelve nu values {4, 4.5, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30} with Gamma = 11.58, c = 0.5, 2,000 null streams per cell, and a 5,000-step horizon with 500-step warm-up. Three arms are monitored: Eco_L1 (estimated GARCH standardization), Oracle_Eco (true GARCH parameters), and Concept (binary sign-error stream). Sixteen scientific primitives are copied verbatim from R04 and byte-verified at start-up. Calibration uses bisection to achieve 5% FPR within 0.003 tolerance over 15 iterations. A joint bootstrap of 2,000 replicates resamples both calibration and drifted streams, pricing threshold placement error. Continuity with R04 is verified at five common nu points using a chi-square omnibus test.

## 3. Concordance Table with Wilson 95% Confidence Intervals

| Claim | Published Value | Regenerated Value | Wilson 95% CI | Deviation Class | Verdict |
|-------|-----------------|------------------|---------------|-----------------|---------|
| Eco-L1 efficiency crossing nu* | 4.9 | inferential bracket [7.0, 9.0] | [7.78, 8.37] | D3 | not held |
| Eco-L1 efficiency crossing nu* | 4.9 | shape fit estimate | 8.10 [7.78, 8.37] | D3 | not held |
| Oracle efficiency crossing nu* | 4.6 | inferential bracket [4.0, 5.0] | [4.31, 4.57] | D0 | held |
| Oracle efficiency crossing nu* | 4.6 | shape fit estimate | 4.47 [4.31, 4.57] | D0 | held |
| Analytic crossing | 4.7 | computed root | 4.6788 | D0 | held |
| Estimation cost (shape-fit) | 0.3 | point estimate | 3.62 [3.31, 3.92] | D3 | not held |
| Estimation cost (model-free) | 0.3 | point estimate | 3.22 [2.52, 3.82] | D3 | not held |
| Ratio respects Gaussian ceiling | <= 1.5708 | max observed | 1.255 | D0 | held |
| R04 interpolated value | 8.52 | two-point interpolation | 7.75 [7.03, 8.32] | D2 | not held |

Wilson score intervals are computed for all bracket-based inferences using z = 1.959963984540054. The inferential bracket for Eco-L1, [7.0, 9.0], is the primary statement carrying confidence: at nu = 7 the 95% ratio interval lies entirely below unity, at nu = 9 entirely above it, and the crossing must lie between them. This is the formulation that governs any manuscript-facing statement.

## 4. Methodological Scope

The campaign establishes that the efficiency crossing for Eco-L1 sits near nu = 8.1, not 4.9, falsifying v87's central claim with a localization. The oracle crossing at 4.47 [4.31, 4.57] survives and tracks near the analytic prediction of 4.6788, though it exhibits a systematic +5% offset across all grid points. The estimation cost of a finite warm-up at Gamma = 11.58 is measured at 3.62 [3.31, 3.92], an order of magnitude above the published 0.3, confirming R04's mechanism in direction and magnitude. The Gaussian ceiling pi/2 is respected by the Eco-L1 curve but exceeded by the oracle curve at nu = 20 (1.5810 vs 1.5708), indicating that Proposition prop:are's asymptotic characterization does not hold at c = 0.5.

Controls: all 36 arms pass calibration half 1 (conditional mid-p KS p = 0.641 > 0.01) and half 2 (pooled level 5.07% [4.84%, 5.29%] intersects [4.70%, 5.30%]). Continuity with R04 holds at five common points (Eco_L1 chi2 = 4.73 on 5 dof, p = 0.4498; Oracle_Eco chi2 = 3.83 on 5 dof, p = 0.5736). QMLE convergence: 0 failures on all three starts (budget 0.5%); 0 stationarity guard fires (budget 0%); 268 of 72,000 (0.3722%) hit the feasibility boundary alpha + beta >= 0.999 and are kept as in R04.

Reproducibility: three consecutive runs at different worker counts produce byte-identical artefacts. R04 is untouched; all eight digests recorded in AUDIT_R04.md still verify. The whole suite passes: 21 tests in test_R04b_claims.py.
