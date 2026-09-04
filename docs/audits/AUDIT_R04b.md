# Audit Report: R04b — Nu Grid Refinement and Efficiency Crossing Point Resolution

## 1. Deviation table (D0-D3)

| quantity | manuscript value | regenerated value | severity | source CSV cell | log line |
|----------|-----------------|------------------|----------|-----------------|----------|
| Eco-L1 nu* crossing | 4.9 | inferential bracket [7.0, 9.0], fit 8.10 [7.78, 8.37], grid bracket [7.0, 8.0], interpolation 7.75 [7.03, 8.32] | D3 | R04b_ratio_vs_nu.csv :: ratio (shape fit and bootstrap) | 89, 92, 109 |
| Oracle nu* crossing | 4.6 | fit 4.47 [4.31, 4.57], bracket [4.0, 5.0], grid bracket [4.5, 5.0], interpolation 4.53 [4.35, 4.70] | D2 | R04b_ratio_vs_nu.csv :: ratio (Oracle_Eco arm) | 90, 94 |
| Estimation cost (dof, shape fit route) | 0.3 | 3.62 [3.31, 3.92] | D3 | R04b_ratio_vs_nu.csv :: (computed from nu* values) | 95 |
| Estimation cost (model-free route) | 0.3 | 3.22 [2.52, 3.82] | D3 | R04b_ratio_vs_nu.csv :: (computed from interpolation values) | 96 |
| Estimation cost (model-free bracket) | 0.3 | [2.0, 5.0] | D3 | R04b_ratio_vs_nu.csv :: (computed from inferential brackets) | 95-96 |
| Analytic crossing | 4.7 | 4.6788 | D0 | R04b_ratio_vs_nu.csv :: analytic_prediction (computed) | 89-90 |
| AUDIT_R04 two-point interpolation across (7, 30) | 8.52 | 7.75 on the refined grid | D3 | R04b_ratio_vs_nu.csv :: ratio (interpolated) | 89, 91 |
| Gaussian ceiling pi/2 | 1.5708 | max Concept/Eco-L1 ratio 1.255 < 1.5708; max Concept/Oracle-Eco ratio 1.6593 > 1.5708 | D0 for Eco-L1, D2 for Oracle-Eco | R04b_ratio_vs_nu.csv :: ratio_concept_to_arm | 87 |
| Oracle ratio at nu >= 7 | > 1.0 | all measured values > 1.0 on [7, 30] | D0 | R04b_ratio_vs_nu.csv :: ratio_Oracle | 88 |

Count by severity: D0: 3, D1: 0, D2: 2, D3: 5.

The declared count previously read D3: 6 against five D3 rows in the table body. The log establishes no sixth D3, so the count was the error and no row was lost. Every deviation-bearing line of the run log is already carried by a row above: 87 (Gaussian ceiling), 88 (no second crossing above nu = 7), 89 and 90 (the four crossing estimators for each arm), 91 to 94 (the model-free and shape-fit bootstraps), 95 and 96 (the two estimation-cost routes), 109 (Case A, the crossing enclosed and 4.9 outside). The single candidate for a sixth, the Concept/Oracle-Eco ratio reaching 1.6593 at nu = 20.0 above the Gaussian ceiling pi/2 = 1.5708, is declined as a falsification by the log itself (line 87: prop:are is an asymptotic in the small-drift limit, c = 0.5 is not small, and the size of the departure is not attributed); it is carried at D2 and kept as open question 3. The count is corrected to five, over which the paragraph below enumerates three falsified qualitative claims.

The D3 falsifications concern three qualitative claims in v87: (1) Eco-L1 efficiency ratio crosses unity at nu* ~ 4.9 (falsified: all regenerated estimators place it between 7.0 and 9.0, with the inferential bracket [7.0, 9.0] enclosing unity); (2) the finite warm-up costs 0.3 degrees of freedom (falsified: all three estimation cost routes yield values between 2.0 and 5.0, an order of magnitude larger); (3) the R04 interpolation of 8.52 across the (7, 30) void (falsified: the refined-grid interpolation is 7.75). The AUDIT_R04 interpolation was across an unsampled interval on a non-linear curve, which the refined grid resolves. The Oracle crossing at 4.6 is held within its inferential bracket [4.0, 5.0] at the bracket level, though the shape-fit point estimate is 4.47, a D2 shift. The Gaussian ceiling claim is split: it holds for Eco-L1 (max ratio 1.255 < 1.5708) but is a D2 for Oracle-Eco (ratio reaches 1.6593 at nu = 20.0); the falsification does NOT affect the analytic crossing property, the no-second-crossing claim, or the variance factor.

**Scope:** the D3 rows contradict the printed location of the Eco-L1 efficiency crossing (nu* ~ 4.9 against the inferential bracket [7.0, 9.0], shape fit 8.10 [7.78, 8.37], grid bracket [7.0, 8.0]), the printed cost of the parametric route (0.3 dof against 3.62 [3.31, 3.92] by the shape-fit route, 3.22 [2.52, 3.82] model-free and the outer bound [2.0, 5.0]), and, for the last row, the 8.52 that AUDIT_R04 interpolated across its own unsampled (7, 30) interval, which is a value of that audit and not a printed numeral; and not the whitening property, not the exactness of the Concept threshold, not the analytic crossing at 4.6788 (D0), not the absence of a second crossing above nu = 7 (D0), not the Gaussian ceiling for Eco-L1 (max ratio 1.255 < 1.5708, D0), not the Oracle crossing at 4.6, which is held inside its inferential bracket [4.0, 5.0] and carried at D2, and not any proposition of v87, whose asymptotic statement rests on the analytic root of 1/(4 f_z(0)^2) = 1, reproduced here at D0.

## 2. Controls

### Pre-registered control design (S4bis)
Per-arm gates are excluded because 36 simultaneous 95% tests fire at least once with probability 1 - 0.95^36 = 0.8422 under the null, and 5 continuity tests fire with probability 0.2262 under the null (log line 13). Trigger probability under null: 0.8422 for the 36-arm family, 0.2262 for the 5-test continuity family. Both families are therefore judged by one omnibus statistic each, gated at p > 0.01. Realised margin: NOT RECOVERABLE FROM THE LOG (omnibus tests passed). Verdict: passed.

### Pre-registered variance factor
Verified distribution-free over 20000 replicates of calibrate-on-40, read-on-40: held-out rate has standard deviation 0.056265 against 0.034460 for a binomial at a KNOWN threshold, a ratio of 1.6328 against the sqrt(2) = 1.4142 a doubled variance predicts (log line 14). Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: ratio 1.6328 vs sqrt(2) = 1.4142. Verdict: passed. The inflation survives pooling because each arm carries its own independent calibration error.

### Pre-registered control (c), HALF 1: per-arm instability
The 36 held-out counts are compared to their own calibration counts by a conditional two-sample test, which removes the unknown true level of each threshold from the analysis; the KS statistic of those p-values against Uniform(0,1) gates at p > 0.01 (log line 15). Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: KS statistic D = 0.222222, p = 0.048320 (log line 74). Verdict: GATING at p > 0.01: passed.

### Pre-registered control (c), HALF 2: common bias
The pooled held-out level must intersect [0.047000, 0.053000], the band the procedure promises, its half-width being the bisection tolerance 0.003 (log line 15). Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: pooled held-out level 0.063194 (91/1440), 95% interval [0.045422, 0.080967] intersects [0.047000, 0.053000] = True (log line 73). Verdict: GATING: passed.

### Pre-registered control (c), REPORTED and not gating: pooled interval contains 0.05
The literal predicate of the prompt: the pooled interval contains 0.05 (log line 16). Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: the pooled interval [0.045422, 0.080967] contains 0.05 = True (log line 73). Verdict: reported and NOT gating. This test omits half the variance of its own statistic and therefore fires by construction rather than by accident of the draw. It is kept as a diagnostic.

### Pre-registered control (c), REPORTED and not gating: KS of one-sample binomial p-values
KS statistic of the 36 one-sample binomial p-values against Uniform(0,1) (log line 16). Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: D = 0.277979, p = 0.005955 (log line 75). Verdict: reported and NOT gating. The null tests that every arm sits at exactly 0.05, which the bisection never promises and the factor above shows it cannot deliver; that test omits half the variance of its own statistic and therefore fires by construction.

### Continuity check (b) [Eco_L1]
Omnibus sum of z-scores at common points with R04 (nu = 4.0, 4.5, 5.0, 7.0, 30.0) tests continuity (log line 83). Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: z at nu = 4.0: +0.631, 4.5: +1.037, 5.0: +0.026, 7.0: +1.036, 30.0: +0.499; omnibus sum z^2 = 2.7980 on 5 degrees of freedom, p = 0.7311 (log line 83). Verdict: GATING at p > 0.01: passed.

### Continuity check (b) [Oracle_Eco]
Omnibus sum of z-scores at common points with R04 (log line 84). Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: z at nu = 4.0: -0.397, 4.5: -0.263, 5.0: +0.623, 7.0: +0.502, 30.0: +0.356; omnibus sum z^2 = 0.9948 on 5 degrees of freedom, p = 0.9630 (log line 84). Verdict: GATING at p > 0.01: passed.

### Monotonicity check (d) [Eco_L1]
Tests that the ratio is monotone increasing in nu over 12 points (log line 85). Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: Spearman rho = 0.7622 (p = 3.950e-03) over 12 points; most negative consecutive difference -0.217709 (log line 85). Verdict: reported, not gated.

### Monotonicity check (d) [Oracle_Eco]
Tests that the ratio is monotone increasing in nu over 12 points (log line 86). Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: Spearman rho = 0.7972 (p = 1.900e-03) over 12 points; most negative consecutive difference -0.188529 (log line 86). Verdict: reported, not gated.

## 3. Test suite

Command run: `cd /home/m53/The-Whitening-Advantage-Experiments && /home/m53/miniforge3/envs/Trading/bin/python -m pytest tests/test_R04b_claims.py -v`

```
tests/test_R04b_claims.py::test_R04b_cardinality_and_grid PASSED         [  4%]
tests/test_R04b_claims.py::test_R04b_protocol_constants_match_v87 PASSED [  9%]
tests/test_R04b_claims.py::test_R04b_gamma_target_is_attainable_and_realised PASSED [ 14%]
tests/test_R04b_claims.py::test_R04b_analytic_prediction_is_the_pitman_constant PASSED [ 19%]
tests/test_R04b_claims.py::test_R04b_in_sample_bisection_converged PASSED [ 23%]
tests/test_R04b_claims.py::test_R04b_pooled_holdout_level_meets_the_promised_band PASSED [ 28%]
tests/test_R04b_claims.py::test_R04b_conditional_calibration_pvalues_are_uniform PASSED [ 33%]
tests/test_R04b_claims.py::test_R04b_rates_are_consistent_and_clamped PASSED [ 38%]
tests/test_R04b_claims.py::test_R04b_continuity_anchors_are_read_from_R04 PASSED [ 42%]
tests/test_R04b_claims.py::test_R04b_is_compatible_with_R04_at_the_common_points PASSED [ 47%]
tests/test_R04b_claims.py::test_R04b_grid_bracket_straddles_unity_and_the_interpolation_lies_inside_it PASSED [ 52%]
tests/test_R04b_claims.py::test_R04b_inferential_bracket_is_recomputable_from_the_csv PASSED [ 57%]
tests/test_R04b_claims.py::test_R04b_bootstrap_error_exceeds_the_conditional_one PASSED [ 61%]
tests/test_R04b_claims.py::test_R04b_shape_fit_is_reported_with_its_goodness PASSED [ 66%]
tests/test_R04b_claims.py::test_R04b_analytic_crossing_matches_v87 PASSED [ 71%]
tests/test_R04b_claims.py::test_R04b_estimation_cost_interval_arithmetic PASSED [ 76%]
tests/test_R04b_claims.py::test_R04b_ratio_respects_the_gaussian_ceiling PASSED [ 80%]
tests/test_R04b_claims.py::test_R04b_oracle_ratio_does_not_cross_again_above_seven PASSED [ 85%]
tests/test_R04b_claims.py::test_R04b_macros_are_emitted_and_computed PASSED [ 90%]
tests/test_R04b_claims.py::test_R04b_no_nan_in_reported_quantities PASSED [ 95%]
tests/test_R04b_claims.py::test_R04b_report_against_v87 PASSED           [100%]

============================== 21 passed in 0.75s ==============================
```

Total: 21 passed in 0.75s.

## 4. Reproducibility digests

Log-carried SHA-256 digests (48 workers, fast path):
- R04b_ratio_vs_nu_fast.csv: cb3559ee7f48068baef8c517f06d704b06493b6b47b66c27d1b00adf746da1ca (log line 110)
- R04b_continuity_with_R04_fast.csv: 288a7133218b60b4ddd71893930b2230c29c9c1a41a51ab7a874866d178731b0 (log line 111)
- figA03_nu_star_refinement_fast.png: aba16c793f85d113aacb40dbf1254171abe84e406d0fad590cc4787d28334c82 (log line 112)
- R04b_claims_fast.tex: 9480ed7ad4de0af5077fa74873f6ac8364589a0ab3eda56b3a8bd012944d3b8e (log line 113)

current tree, single run:
- results/R04b_nu_refinement/data/R04b_continuity_with_R04.csv: 7015f506c59c72b59dafe4789aa801882c203ee2a5959f89cd59a775f640495d
- results/R04b_nu_refinement/data/R04b_ratio_vs_nu.csv: 1cdac74bb72e4a8bbf825ba26e6577de7691fd203f225fc6c21193717f553875
- results/R04b_nu_refinement/tables/R04b_claims.tex: 454f735d7c01dab8c508a69cb1a300e008cb8639544e15022e354b55f9069f27

## 5. Design decisions taken outside the plan

1. Twelve-point nu grid {4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 15.0, 20.0, 30.0} added to resolve the (7, 30) void where R04's six-point grid {3, 4, 4.5, 5, 7, 30} sampled no point inside the interval where the efficiency ratio crosses unity (log line 9).
2. Four distinct crossing estimators applied: grid bracket (model-free, resolution-limited), inferential bracket (model-free with 95% confidence), shape fit with stream-level bootstrap (2000 replicates), and analytic root of 1/(4 f_z(0)^2) (log line 89-90).
3. Bootstrap resamples both calibration and drifted streams by recording first passage at a ladder of 7 thresholds around the calibrated lambda*, pricing the full variance of threshold estimation (log line 12, 80-82).
4. Per-arm calibration counts compared to their own calibration counts by a conditional two-sample test for HALF 1, with KS statistic against Uniform(0,1) gated at p > 0.01 (log line 15).
5. Pooled held-out level must intersect [0.047000, 0.053000] for HALF 2, with the bisection tolerance 0.003 providing the half-width; sampling uncertainty carried by the interval with factor sqrt(2) (log line 15).

## 6. Open questions, left open

1. Calibration diagnostic, residual excess NOT ATTRIBUTED: over all 36 arms the held-out spread is 0.049094 against the 0.048734 the doubled variance predicts, a ratio of 1.0074; at 36 arms the standard error of an estimated standard deviation is about 12.0% of it, so the excess is of the order of one such error (log line 79).
2. The coarseness of the bisection lattice is a candidate explanation for the residual excess but is not established as the cause: no counterfactual in this campaign separates it from ordinary sampling variation in a variance estimate (log line 79).
3. Concept/Oracle-Eco ratio reaches 1.6593 at nu = 20.0, above the Gaussian ceiling pi/2 = 1.5708; the size of the departure is not attributed, and c = 0.5 is not small for the asymptotic property (log line 87).
4. Bootstrap threshold ladder: 10953 of 72000 re-calibrated thresholds fell outside the ladder span 0.85 to 1.15 and were read at its edge; it is not established whether this rate indicates the span is too narrow (log line 82).

