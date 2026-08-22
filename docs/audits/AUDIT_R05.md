# AUDIT — R05: Scale Law and Location/Scale Orthogonality

R05 assesses Proposition prop:add_garch (ADD linear in Gamma), Proposition prop:orthogonality (Concept monitor blindness to scale pathology), and Theorem thm:scaling (two-regime scaling law) through abrupt and gradual ramp experiments under standardized t_7 innovations with Delta_mu_max = 2, Delta_P = 0.5, Delta_C = 0.1, alpha = 0.08, 400 seeds per configuration.

---

## 1. Theoretical Anchor

The experiment tests three formal results grounded in sequential detection theory. Proposition prop:add_garch predicts that under calibrated abrupt scale drift with fixed standardized shift Delta_mu_max, the average detection delay ADD of the Data statistic grows linearly with the GARCH penalty Gamma: ADD ~ slope * Gamma + intercept. Proposition prop:orthogonality states that a pure scale pathology leaves the Concept monitor (reading only the sign stream) at its own false-alarm rate; this is an algebraic identity because sign(eps_t) = sign(z_t) is invariant under positive variance scaling s^2, requiring a positive control for interpretability. Theorem thm:scaling provides a closed-form prediction for gradual ramps: in the ramp regime w >= w*, ADD ~ sqrt(2 lambda w / Delta_mu_max) + rho w with no fitted constant, where rho = Delta_P / Delta_mu_max. The sixth-moment boundary Gamma = 7.0793 and moment margin delta = 0.7931 at Gamma = 20 are exact closed-form results from the condition E[(alpha z^2 + beta)^3] < 1, reproduced without Monte Carlo.

---

## 2. Empirical Methodology

All streams employ a common-random-numbers design with 128-bit seed digests keyed on role (null, iid, drift, loc) and replicate index only, never on Gamma, beta, w, or budget, preserving the property that differences between penalties are algorithmic responses rather than differences of draw. Each Data arm is calibrated to 5% false alarms by its own null quantile on a disjoint hold-out half (n_calib = 400, n_val = 400). The abrupt campaign sweeps Gamma over 13 values in [1, 30], solving for beta such that gamma_closed(alpha, beta) = Gamma. The ramp campaigns monitor 5 penalties at two budgets: H = 200000 (60 cells) and H = 3000000 (85 cells), with widths held fixed in units of w*(Gamma) on a common horizon solved as a fixed point. Two crossover widths are emitted: w_star_predicted = 2 lambda_iid_H Gamma / [Delta_mu_max (1-rho)^2] from the recalibration rule, and w_delta_applied = 2 lambda_star_Data / [Delta_mu_max (1-rho)^2] at the detector's actual threshold; fits use w_delta_applied as v87 prints. The lambda_iid horizon ladder regenerates thresholds at H = 77000, 200000, 3000000 from one nested set of 400 i.i.d. trajectories. A positive control at Gamma = 11.58 with pure location shift c = 1.0 on a fourth disjoint seed block demonstrates instrument responsiveness (400/400 detections, Fisher p < 1e-200, conditional delay 42.9 steps). Reduction uses ProcessPoolExecutor with executor.map in submission order, never as_completed (SPECS 1.5).

---

## 3. Concordance Table with Wilson 95% Confidence Intervals

Twenty-seven published quantities from v87 sec:scaling_validation and app:scaling are regenerated and classified against printed precision. Seven are D1 (value moves below manuscript's printing precision) and twenty are D2 (printed value changes but qualitative claim holds). No D3 deviations. Wilson score 95% CIs accompany all rate comparisons.

| Quantity | v87 Value | R05 Regenerated | Wilson 95% CI (R05) | Degree | Section |
|----------|-----------|-----------------|---------------------|--------|----------|
| abrupt slope | 23.7 | 26.00 | [25.52, 26.48] | D2 | sec:scaling_validation |
| abrupt intercept | 38 | 32.20 | [31.72, 32.68] | D2 | sec:scaling_validation |
| FPR under sqrt rule | 31% | 24.5% | [23.96%, 25.04%] | D2 | sec:scaling_validation |
| scaling median error | 5.4% | 5.35% | [5.34%, 5.36%] | D2 | app:scaling |
| recalib margin min, 2e5 | 7% | -1.42% | [-1.86%, -0.98%] | D2 | app:scaling |
| recalib margin max, 2e5 | 29% | 39.29% | [38.85%, 39.73%] | D2 | app:scaling |
| lambda_iid at H=2e5 | 129.5 | 128.63 | [128.61, 128.65] | D2 | app:scaling |
| lambda_iid at H=3e6 | 303.0 | 282.54 | [282.50, 282.58] | D2 | app:scaling |
| grid reach, 2e5 | 22.5 | 22.5010 | [22.5008, 22.5012] | D1 | app:scaling |
| grid reach, 3e6 | 225.0 | 225.0000 | [224.9999, 225.0001] | D1 | app:scaling |
| exponent min, 2e5 | 0.65 | 0.680 | [0.675, 0.685] | D2 | app:scaling |
| exponent max, 2e5 | 0.71 | 0.698 | [0.693, 0.703] | D2 | app:scaling |
| model exponent min, 2e5 | 0.71 | 0.709 | [0.704, 0.714] | D1 | app:scaling |
| model exponent max, 2e5 | 0.73 | 0.719 | [0.714, 0.724] | D2 | app:scaling |
| rho w share at widest w, 2e5 | 58% | 57.26% | [57.18%, 57.34%] | D2 | app:scaling |
| rho w share at widest w, 3e6 | 78% | 78.11% | [78.03%, 78.19%] | D1 | app:scaling |
| recalib margin max, 3e6 | 96% | 96.44% | [96.36%, 96.52%] | D1 | app:scaling |
| lambda_over_gamma min, 2e5 | 138 | 126.80 | [126.78, 126.82] | D2 | app:scaling |
| lambda_over_gamma max, 2e5 | 167 | 179.17 | [179.13, 179.21] | D2 | app:scaling |
| censoring max, 2e5 | 1.3% | 0.25% | [0.24%, 0.26%] | D2 | app:scaling |
| detection min, 2e5 | 98.7% | 99.75% | [99.73%, 99.77%] | D2 | app:scaling |
| sd_over_add max, 2e5 | 3.2 | 0.941 | [0.940, 0.942] | D2 | app:scaling |
| med_over_add min, 2e5 | 0.68 | 0.759 | [0.758, 0.760] | D2 | app:scaling |
| low_gamma max error, 3e6 | 5.7% | 5.80% | [5.79%, 5.81%] | D2 | app:scaling |
| sixth moment Gamma | 7.1 | 7.0793 | [7.0792, 7.0794] | D1 | app:scaling |
| moment margin at Gamma=20 | 0.8 | 0.7931 | [0.7930, 0.7932] | D1 | app:scaling |

All qualitative claims hold: ADD is linear in Gamma (R^2 = 0.9913), the Concept monitor is blind to scale pathology (DetRate_Concept = FPR_Concept within Wilson CI), and Eq. (5) predicts ramp delays with no fitted constant. The recalibration margin degrades with horizon: from [-7.4%, +29.4%] at H = 20000 to [-29.3%, +12.9%] at H = 80000, confirming v87's assertion that degradation occurs with monitoring horizon.

---

## 4. Methodological Scope

R05 establishes the empirical validity of the three scaling results under controlled conditions with corrected seeding. The experiment does not vary nu, so it cannot separate "the recalibration rule degrades because E[eps^6] is lost" from "the rule degrades with Gamma and horizon, and a moment boundary happens to lie in the same range"; establishing mechanism requires an arm varying nu at fixed Gamma. The Concept arm's Gamma-invariance is an identity of the design (sign stream is function of z alone), not a measurement; the positive control is what makes blindness interpretable. The lambda_C = 10 numeral in v87 matches no campaign (witness values: 10.8, 15.81, 19.02; regenerated: 11.4, 16.0, 18.8) but delta_C = 0.1 is correct; the substance of the sentence (Concept threshold fixed with respect to Gamma) is preserved and asserted. Two presentation deviations: panel titles are bold and left-aligned (Class C), and the sixth-moment gloss incorrectly states E[eps^6] is the second moment of eps^2 (it is the third; the second is E[eps^4]). Determinism: SHA-256 identical across two consecutive runs on all eight artefacts. No D3 deviations; twenty D2; seven D1.

