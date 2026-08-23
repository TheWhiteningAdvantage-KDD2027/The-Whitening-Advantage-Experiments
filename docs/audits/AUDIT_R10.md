# Audit Report — R10 Skew Robustness

## 1. Deviation table (D0-D3)

| quantity | manuscript value | regenerated value | severity | source CSV cell | log line |
|---|---|---|---|---|---|
| L290 realized skewness | -1.44 | -1.4279594830035083 | D2 | R10_skew_diagnostics.csv :: skewness | NOT RECOVERABLE FROM THE LOG |
| L290 marginal rate q | 0.58 | 0.58219112499999992 | D1 | R10_skew_diagnostics.csv :: q | NOT RECOVERABLE FROM THE LOG |
| L290 fixed-1/2 CUSUM fires at | 0.97 | 0.96599999999999997 | D1 | R10_skew_fpr.csv :: fpr_half_rate | NOT RECOVERABLE FROM THE LOG |
| Fig. 10 caption FPR lower end | 0.010 | 0.01 | D0 | R10_skew_fpr.csv :: fpr_qhat_rate (min) | NOT RECOVERABLE FROM THE LOG |
| Fig. 10 caption FPR upper end | 0.018 | 0.014999999999999999 | D2 | R10_skew_fpr.csv :: fpr_qhat_rate (max) | NOT RECOVERABLE FROM THE LOG |

Count by severity: D0: 1, D1: 2, D2: 2.

The table contains no D3 row.

## 2. Controls

### C1 — Symmetric witness at xi = 1
What the control tests: two two-sided tests at 4 standard errors of the across-stream mean, on the symmetric grid point xi = 1.

Trigger probability under its own null hypothesis: 6.3342e-05 per test under a normal null, 1.2668e-04 for the pair (line 37).

Realised margin: realized skewness -0.0002295139273865433 +/- 0.002857009597695856 over 1000 streams, which is -0.080 standard errors from 0; marginal rate q = 0.499485125 +/- 0.00017681318109910636, which is -1.066 standard errors from q* = 0.4996735799825578 and -2.912 standard errors from 1/2 (line 38).

Verdict: Criterion met: True (line 38).

### C2a — Ljung-Box calibration per cell
What the control tests: the Ljung-Box statistic on a binary stream is discrete, so its p-values carry atoms and a Kolmogorov-Smirnov test against a continuous uniform is conservative. Citation from R18: at n_steps = 8000, lags = 20, R18 measured ks_statistic = 0.03325305136405571 on 1000 null streams, with a bootstrap p-value of the maximum KS statistic of 0.5665 (line 40).

Trigger probability under its own null hypothesis: at most 1% per arm, and STRICTLY BELOW it (line 39).

Realised margin: within-cell KS statistics and p-values reported for all 8 cells (lb_sign and lb_ebin at xi = 1, 0.85, 0.65, 0.5) at lines 41-42 for xi=1, lines 44-49 for xi = 0.85, 0.65, 0.5. The pooled test KS of the 8 per-cell binomial p-values against Uniform(0,1) gives D = 0.3617023786656224, p = 0.19161868004262983 (line 43). The eight cells are computed on the SAME 1000 streams under the mandated common-random-numbers plan, and the sign arm is i.i.d. Bernoulli(q) at every xi by control C4, so the eight p-values are neither independent of one another nor eight independent readings of the proposition. A KS test assumes independent draws under its null and has neither property here. It is persisted descriptively per S4bis.3 and gates nothing (line 43).

Verdict: Criterion met: True for all cells (lines 41-42, 44-49). Pooled test is REPORTED, NOT GATED (line 43).

### C2b — Invariance across asymmetry grid
What the control tests: 3 displaced grid points x 2 arms = 6 paired differences against the xi = 1 cell on the same 1000 streams; the statistic is their maximum in absolute value, read against a Rademacher sign-flip null of the maximum on 10000 replicates (line 50).

Trigger probability under its own null hypothesis: exactly 0.01, by construction of the null (line 50).

Realised margin: the widest paired difference is lb_sign @ xi=0.85 at +0.013000 on 93 discordant streams; the maximum over all 6 comparisons is 0.013000. The 99.0% quantile of the null maximum is 0.030000 and the observed maximum sits at a null exceedance probability of 0.6594 (line 51). Full vector of paired differences: {'lb_sign @ xi=0.85': 0.013, 'lb_sign @ xi=0.65': -0.004, 'lb_sign @ xi=0.5': 0.0, 'lb_ebin @ xi=0.85': 0.001, 'lb_ebin @ xi=0.65': 0.001, 'lb_ebin @ xi=0.5': 0.01}.

Verdict: Criterion met: True (line 51).

### C4 — Sign stream identity
What the control tests: eps_t = sqrt(h_t) z_t with h_t > 0, so `1{eps_t > 0} == 1{z_t > 0}` exactly. The consequence is that panel A's raw-sign arm measures the Ljung-Box test's calibration and not a property of the data-generating process.

Trigger probability: NOT RECOVERABLE FROM THE LOG.

Verdict: Control stated in tests/test_R10_claims.py line 472-481; passed.

### C6 — Standardisation constants are one deterministic input
What the control tests: the (m, s, q_oracle) triple every stream used is a single constant per grid point, bit-identical to the one the main process recomputed and persisted.

Trigger probability: NOT RECOVERABLE FROM THE LOG.

Verdict: Control stated in tests/test_R10_claims.py line 503-515; passed.

### C7 — Implemented threshold test coincides with the weak operator
What the control tests: Control C7c measures what `M > 15.0` implements on the lattice boundary. On this campaign it coincides with the mathematical `M >= 15.0` on every stream.

Trigger probability: NOT RECOVERABLE FROM THE LOG.

Verdict: Control stated in tests/test_R10_claims.py line 741-758; passed.

### C7b — Bernoulli twin reduces to the fair coin at one half
What the control tests: at q = 1/2 the Bernoulli twin must return the value of the fair-coin routine R07 owns, BIT FOR BIT, because `1.0 - 0.5` is exact in binary floating point.

Trigger probability: NOT RECOVERABLE FROM THE LOG.

Verdict: Control stated in tests/test_R10_claims.py line 372-387; passed.

### C7b — Transcription
What the control tests: the exact Bernoulli(q) predictions the experiment persists for the `half` arm are recomputed by an explicit enumerated sparse transition matrix, at the full campaign horizon.

Trigger probability: NOT RECOVERABLE FROM THE LOG.

Verdict: Control stated in tests/test_R10_claims.py line 351-369; passed.

### C8 — Operator null level
What the control tests: the level this CUSUM delivers under PERFECT centring, averaged over the 4 grid points, on 80000 keyed Bernoulli(q) streams. It is NOT the nominal level, which this detector does not attain at delta = 0.1 and lambda = 15.0.

Trigger probability: NOT RECOVERABLE FROM THE LOG.

Verdict: Control stated in tests/test_R10_claims.py line 616-620; passed.

### C9 — Design effect measurement
What the control tests: measurement of design effects for lb_sign, lb_ebin, fpr_half, fpr_oracle, fpr_qhat statistics pooled across the xi grid.

Trigger probability: NOT RECOVERABLE FROM THE LOG.

Verdict: Control stated in tests/test_R10_claims.py; passed. Results in R10_design_effect.csv.

### C10 — No degraded path is taken
What the control tests: neither branch of the carried `lb_pvalue` fired, on either binary stream. A constant 0/1 stream would have returned the non-rejection 1.0 and a swallowed exception would have returned NaN.

Trigger probability: NOT RECOVERABLE FROM THE LOG.

Verdict: Control stated in tests/test_R10_claims.py line 489-500; passed.

### Family-wise arithmetic
What the control tests: The prompt's eight-cell reading -- 4 xi x 2 arms of Ljung-Box tests at the 0.05 level -- has a probability 1 - (1 - 0.05)^8 = 33.6580% of at least one rejection under a perfectly calibrated null, far above the 5% ceiling S4bis fixes: 'no test rejects' is NOT usable as a binary gate here and is not used as one. The two gates actually adopted, C2a and C2b, give 1 - (1 - 0.01)^2 = 1.9900% (2.9701% if C2a's two arms and C2b are counted separately). C1 adds two deterministic-band tests at 6.3342e-05 each (line 9).

Trigger probability under its own null hypothesis: 1.9900% for C2a and C2b combined, 2.9701% if C2a's two arms and C2b are counted separately, 1.2668e-04 for C1's pair of tests, 6.3342e-05 per test for C1 (line 9).

Realised margin: logged before any result is read (line 9).

Verdict: Statement logged at line 9; gates adopted are C2a and C2b, not the eight-cell gate.

## 3. Test suite

```
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-9.0.0, pluggy-1.6.0
rootdir: /home/m53/The-Whitening-Advantage-Experiments
plugins: anyio-1.6.0
collecting ... collected 26 items

tests/test_R10_claims.py::test_R10_every_artefact_the_plan_lists_exists_with_its_prescribed_schema PASSED [  3%]
tests/test_R10_claims.py::test_R10_the_operating_threshold_is_seventy_five_lattice_units PASSED [  7%]
tests/test_R10_claims.py::test_R10_the_half_arm_law_reproduces_under_an_independent_dynamic_program PASSED [ 11%]
tests/test_R10_claims.py::test_R10_the_bernoulli_twin_reduces_to_the_fair_coin_at_one_half PASSED [ 15%]
tests/test_R10_claims.py::test_R10_the_enumeration_validation_agrees_with_an_independent_enumeration PASSED [ 19%]
tests/test_R10_claims.py::test_R10_the_wilson_intervals_reproduce_from_a_second_algebraic_form PASSED [ 23%]
tests/test_R10_claims.py::test_R10_q_star_reproduces_from_the_student_t_survival_function PASSED [ 26%]
tests/test_R10_claims.py::test_R10_the_caption_stream_count_is_one_thousand_per_point PASSED [ 30%]
tests/test_R10_claims.py::test_R10_the_sign_stream_is_bit_identically_the_innovation_sign PASSED [ 34%]
tests/test_R10_claims.py::test_R10_no_degraded_path_is_taken PASSED      [ 38%]
tests/test_R10_claims.py::test_R10_the_standardisation_constants_are_one_deterministic_input PASSED [ 42%]
tests/test_R10_claims.py::test_R10_the_fixed_half_cusum_explodes_with_asymmetry PASSED [ 46%]
tests/test_R10_claims.py::test_R10_recentering_restores_false_alarm_control PASSED [ 50%]
tests/test_R10_claims.py::test_R10_the_carried_primitives_are_byte_identical_to_both_owning_files PASSED [ 53%]
tests/test_R10_claims.py::test_R10_the_family_wise_arithmetic_is_logged_before_any_gate_is_read PASSED [ 57%]
tests/test_R10_claims.py::test_R10_macros_are_emitted_and_agree_with_the_frames PASSED [ 61%]
tests/test_R10_claims.py::test_R10_text_artefacts_end_with_a_newline PASSED [ 65%]
tests/test_R10_claims.py::test_R10_no_confirmatory_language_in_the_script_the_log_or_the_section PASSED [ 69%]
tests/test_R10_claims.py::test_R10_the_three_monte_carlo_numerals_of_L290_move_within_their_own_sampling_error PASSED [ 73%]
tests/test_R10_claims.py::test_R10_the_caption_fpr_envelope_has_moved_at_its_upper_end PASSED [ 77%]
tests/test_R10_claims.py::test_R10_the_symmetric_grid_point_is_not_centred_on_one_half PASSED [ 80%]
tests/test_R10_claims.py::test_R10_the_implemented_threshold_test_coincides_with_the_weak_operator PASSED [ 84%]
tests/test_R10_claims.py::test_R10_report_deviation_classification PASSED [ 88%]
tests/test_R10_claims.py::test_R10_report_design_effect_and_extremum_envelopes PASSED [ 92%]
tests/test_R10_claims.py::test_R10_report_the_operator_null_level_and_the_exact_half_arm_law PASSED [ 96%]
tests/test_R10_claims.py::test_R10_report_the_ljungbox_calibration_and_its_power_bound PASSED [100%]

============================== 26 passed in 2.51s ==============================
```

Total for the whole suite: 26 passed.

## 4. Reproducibility digests

From the log (lines 57-68):

```
results/R10_skew_robustness/
├── data/
│   ├── R10_skew_fpr.csv                    [d2bda65da5accec537d66ff8c4fee516d89cb524ed429cc0927af8297c131d5f]
│   ├── R10_skew_diagnostics.csv            [cc72f77fa539d29c614a222f5477e27708ae8e0519a6efa36e65b00f3bc52718]
│   ├── R10_fs_constants.csv                [14520038fd72bc5dca1ac5f12496ed777f541036d2701205046a9ad37ea968b7]
│   ├── R10_skew_streams.csv                [cb1543dcd4b8cd5aa761dbf96b9312b4b325321377dfcf77a697a1c126696f73]
│   ├── R10_lattice_exact_law.csv           [8cf75d61533283c0a9f036b6586d7afb96a6aaca928923216522c3c8cb4f0ec8]
│   ├── R10_operator_null_level.csv         [226fbfc23aa11be36fb016792797a43f6c70417786fcd4483bffa652a2383962]
│   └── R10_design_effect.csv               [a63a7cbae9f0f40aa01b6a33b859c897ebef8e227090b50faaf91e638ab07a50]
├── figures/
│   └── fig10_skew_robustness.png           [7abce27915f8fe47e6a2f2d170000909dff5bc8cbc28c016db19ed2243c3da70]
└── tables/
    └── R10_claims.tex                      [bcd03ff5abe7d121bc0acca0eb4fedf07940c47455652325ba3bfe48824ba07a]
```

current tree, single run:
```
a63a7cbae9f0f40aa01b6a33b859c897ebef8e227090b50faaf91e638ab07a50  results/R10_skew_robustness/data/R10_design_effect.csv
14520038fd72bc5dca1ac5f12496ed777f541036d2701205046a9ad37ea968b7  results/R10_skew_robustness/data/R10_fs_constants.csv
8cf75d61533283c0a9f036b6586d7afb96a6aaca928923216522c3c8cb4f0ec8  results/R10_skew_robustness/data/R10_lattice_exact_law.csv
226fbfc23aa11be36fb016792797a43f6c70417786fcd4483bffa652a2383962  results/R10_skew_robustness/data/R10_operator_null_level.csv
cc72f77fa539d29c614a222f5477e27708ae8e0519a6efa36e65b00f3bc52718  results/R10_skew_robustness/data/R10_skew_diagnostics.csv
d2bda65da5accec537d66ff8c4fee516d89cb524ed429cc0927af8297c131d5f  results/R10_skew_robustness/data/R10_skew_fpr.csv
cb1543dcd4b8cd5aa761dbf96b9312b4b325321377dfcf77a697a1c126696f73  results/R10_skew_robustness/data/R10_skew_streams.csv
bcd03ff5abe7d121bc0acca0eb4fedf07940c47455652325ba3bfe48824ba07a  results/R10_skew_robustness/tables/R10_claims.tex
```

Worker count: single run with ProcessPoolExecutor max_workers as passed to exp_R10_skew_robustness.py (default from run_experiment_R10.sh). The log does not record the number of workers for this single run.

## 5. Design decisions taken outside the plan

None recorded.

## 6. Open questions, left open

None recorded.
