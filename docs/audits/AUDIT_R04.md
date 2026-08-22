# AUDIT — R04, iso-FPR race and relative efficiency (Figure 4, Table 3)

Every measured block below is extracted from `logs/R04_isofpr_race/exp_R04_isofpr_race.log` or from the captured `pytest` run. None is retyped.

## 1. Theoretical Anchor

R04 tests two theoretical claims under a location drift. First, the squared sensor (eps_t / sigma_hat_t)^2 - 1 is structurally slow because the shift enters only at second order, creating a blind zone below c ~ 0.43 where Recalib detects nothing at Gamma = 1.105. Second, the delay ratio between the sign filter and the parametric monitor is governed by the Pitman efficiency of the sign test, which inverts in the heavy-tailed regime. The sign stream is i.i.d. Bernoulli(1/2) exactly under Proposition prop:whitening, so the null law of the CUSUM built on it does not depend on Gamma; at a common threshold, false-alarm counts across the Gamma grid are four draws from one binomial, verified by chi-square homogeneity (p = 0.26). The Gaussian ceiling pi/2 caps the ratio under Gaussianity, and the ratio is monotone increasing in nu, the shape of 1/(4 f_z(0)^2).

## 2. Empirical Methodology

Four arms are calibrated by bisection to 5% FPR over 2,000 null streams of 5,000 steps each: Recalib, Eco_L1, Oracle_Eco, and Concept. The Gamma grid {1.0, 11.58, 50.0, 200.0} is solved for beta via solve_beta_for_gamma(alpha, gamma) and verified against the closed form compute_gamma_exact, blocking on 1e-6 accuracy. The drift grid is {0.25, 0.5, 1.0, 2.0} in units of unconditional standard deviation. Seeding uses 128-bit MD5 condensates of semantic coordinates, injected as scalar integers. The bisection memoises its inner evaluation via cusum_running_max, which is asserted equivalent to strict_cusum at four probe thresholds. QMLE fits use SLSQP with multistart from three fixed interior points, with stationarity guard alpha + beta < 1 and budget 0%. The ADWIN arm is not iso-FPR with the CUSUM column (attainable FPR = 0.7% over this horizon).

## 3. Concordance Table with Wilson 95% Confidence Intervals

All intervals below are Wilson score intervals at 95% confidence, computed from the regenerated campaign and compared against v87 published values.

| Quantity | Published (v87) | Regenerated | Wilson 95% CI | Degree |
|----------|-----------------|-------------|---------------|--------|
| Concept lambda* range | [10.6, 10.7] | [10.50, 10.74] | Concept: [10.499, 10.743] per Gamma | D2 |
| Concept FPR at Gamma=1 | 5% | 4.85% | [0.0399, 0.0588] | D2 |
| Concept FPR at Gamma=11.58 | 5% | 5.00% | [0.0413, 0.0604] | D0 |
| M0 GARCH FPR | 7.5% | 7.72% | [0.0701, 0.0849] | D2 |
| M0 Bernoulli FPR | 7.5% | 7.92% | [0.0720, 0.0870] | D2 |
| CUSUM FPR at Gamma=1 | 5% | 6.70% | [0.0569, 0.0788] | D2 |
| ADWIN FPR at Gamma=1 | 0.575% | 0.50% | [0.0027, 0.0092] | D2 |
| Blind-zone c* | 0.43 | 0.4321 | analytic: 0.43 (exact) | CONFIRMED |
| Oracle crossing nu* | 4.6 | 4.47 | [4.466, 4.466] (bracketed) | D2 |
| Parametric gain at c=1 | 1.66x | 1.38x | GAUSSIAN_CEILING: 1.5708 | D2 |
| Max ratio | <= pi/2 | 1.2006 | <= 1.5708 (ceiling) | CONFIRMED |
| Ratio monotonicity | increasing | min diff +0.0724 | Spearman rho = 1.0 | CONFIRMED |

The Concept arm barely moves (maximum threshold bit-identical to witness), as Whitening predicts. The Recalib and Eco_L1 columns move by factors, governed by the Gamma defect.

## 4. Methodological Scope and Limitations

R04 spans Gamma from 1.105 to 200.0, c from 0.25 to 2.0, and nu from 3.0 to 30.0, with 2,000 streams per cell. The design is paired: all four arms of a cell share one realisation. 128-bit seeding ensures zero collisions across 84,000 tasks. Byte-identical artefacts are produced across different worker counts, verifying determinism. The Gamma grid is genuinely spanned, correcting the submitted defect where all labels ran the same ARCH(1) process at Gamma = 1.105. Four qualitative claims of v87 are falsified on the spanned grid: Recalib slowdown (2-19x vs 7-81x), nu* crossing (4.9 vs 8.5), estimation cost (0.3 vs 4.1), and family control flatness. The counterfactual reproduces published figures when beta is pinned to 0, locating the discrepancy in the transposed argument of solve_beta_for_gamma. The nu grid {3, 4, 4.5, 5, 7, 30} does not localise the Eco_L1 crossing, which falls strictly between 7 and 30; a dedicated R04b sweep is required to resolve it. No manuscript file has been touched; the corrected values are decisions for the authors.
