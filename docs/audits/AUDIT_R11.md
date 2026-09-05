# Audit Report: R11 Multi-Detector Generalization

## 1. Deviation table (D0-D3)

| quantity | manuscript value | regenerated value | severity | source CSV cell | log line |
|----------|------------------|------------------|----------|-----------------|----------|
| Concept ADD CUSUM (reset) | 28.3 | 28.4078 | D2 | R11_concept_add_vs_gamma.csv arm=as_submitted ADD_CUSUM (mean of 20 rows) | 103 |
| Concept ADD PHT (warmstart) | 27.1 | 27.0517 | D1 | R11_concept_add_vs_gamma.csv arm=as_submitted ADD_PHT (mean of 20 rows) | 104 |
| Concept ADD ADWIN (warmstart) | 61.0 | 61.2123 | D1 | R11_concept_add_vs_gamma.csv arm=as_submitted ADD_ADWIN (mean of 20 rows) | 105 |
| Concept ADD DDM (warmstart) | 250.0 | 249.6010 | D1 | R11_concept_add_vs_gamma.csv arm=as_submitted ADD_DDM (mean of 20 rows) | 106 |
| Concept ADD order PHT < CUSUM (as_submitted) | 1.0 | 1.0 | D0 | R11_concept_add_vs_gamma.csv arm=as_submitted | 107 |
| Data log-log slope CUSUM | 0.86 | 0.8777 | D2 | R11_slope_fits.csv arm=as_submitted pipeline=Data detector=CUSUM | 108 |
| Data log-log slope PHT | 1.09 | 1.0977 | D2 | R11_slope_fits.csv arm=as_submitted pipeline=Data detector=PHT | 109 |
| Data log-log slope ADWIN | 0.47 | 0.4845 | D2 | R11_slope_fits.csv arm=as_submitted pipeline=Data detector=ADWIN | 110 |
| PHT sqrt(Gamma) plateau, grid mean | 0.30 | 0.2818 | D2 | R11_pht_fpr_vs_gamma.csv FPR_sqrt (mean of 20 rows) | 111 |
| PHT syncope Gamma (DetRate < 0.5) | 75.0 | 91.1111 | D2 | R11_data_add_vs_gamma.csv arm=as_submitted DetRate_PHT | 112 |
| EDDM H0 Concept FPR floor | 0.90 | 0.9210 | D2 | R11_concept_fpr_vs_gamma_independent_seeds.csv FPR_EDDM (mean of 20 rows) | 113 |
| Peak-to-peak ADD spread, cumulative (CUSUM) | 0.032 | 0.0113 | D2 | R11_concept_add_vs_gamma.csv arm=as_submitted ADD_CUSUM (largest of ('CUSUM', 'PHT')) | 114 |
| Peak-to-peak ADD spread, window-mean ADWIN | 0.13 | 0.1316 | D1 | R11_concept_add_vs_gamma.csv arm=as_submitted ADD_ADWIN | 115 |
| Gamma range max/min (realised) | 170.0 | 170.3704 | D1 | R11_concept_add_vs_gamma.csv Gamma_realised | 116 |
| Submitted linear slope CUSUM (submitted log) | 26.602 | 26.2411 | D2 | R11_slope_fits.csv response='ADD ~ Gamma' detector=CUSUM | 117 |
| Submitted linear slope PHT (submitted log) | 37.228 | 37.2746 | D2 | R11_slope_fits.csv response='ADD ~ Gamma' detector=PHT | 118 |
| Submitted linear slope ADWIN (submitted log) | 4.747 | 4.8731 | D2 | R11_slope_fits.csv response='ADD ~ Gamma' detector=ADWIN | 119 |
| PHT calibrated threshold, Data | 39.01 | 41.4515 | D2 | the calibration block of the log | 120 |
| PHT calibrated threshold, Concept | 10.34 | 10.3180 | D2 | the calibration block of the log | 121 |

Count by severity: D0: 1, D1: 5, D2: 11, D3: 0.

## 2. Controls

### C1 — PHT equivalence and separation
Tests that a PHT with mean_x frozen at 0.0 returns the same alarm index as strict_cusum, and that with mean_x live the alarm index differs.
- Trigger probability under its own null hypothesis: Not applicable (deterministic test).
- Realised margin: C1 (a) 0 streams (required: 0); C1 (b) 75 streams (required: at least 1).
- Verdict: Both gates passed. The adaptive reference is active and the PHT is not a relabelled CUSUM.
- Log line: 51-52

### C3 — river hard dependency
Tests that river is available as a hard dependency.
- Trigger probability: deterministic.
- Realised margin: river version 0.23.0 written into every CSV that carries a river detector.
- Verdict: Passed. The submitted `hasattr(drift, 'binary')` fork is replaced by an explicit path.
- Log line: 9

### C4 — Flatness gate is a slope test, not a peak-to-peak threshold
Tests that 5 detectors tested simultaneously at the 5% level give a family-wise error rate.
- Trigger probability under its own null hypothesis: 1 - 0.95^5 = 0.2262 (computed and logged before any result is read).
- Realised margin: The probability 0.2262 exceeds preamble S4bis's 5%, which is why 'no detector rejects' is NOT used as a binary door.
- Verdict: Gate replaced by slope test with seed-cluster bootstrap standard errors. Individual p-values are kept as description, never as an acceptance criterion.
- Log line: 77-81

### C4 diagnostic — Bootstrap against analytic standard errors
Measures the design effect the common-random-numbers pairing imposes on Concept slopes.
- Trigger probability: NOT RECOVERABLE FROM THE LOG.
- Realised margin: Bootstrap/analytic SE ratios — CUSUM 3.714, PHT 5.043, ADWIN 2.151, DDM 1.475, EDDM 3.129.
- Verdict: Ratios computed and reported; the ratio IS the design effect.
- Log line: 81

### C6 — Pre-onset leak counters
Logs the pre-onset leak per detector and per grid point, even at zero.
- Trigger probability: NOT RECOVERABLE FROM THE LOG.
- Realised margin: Totals over the grid, warmstart arm: CUSUM 3180; PHT 2400; ADWIN 40; DDM 9780; EDDM 91560.
- Verdict: Counter deliberately NOT a gate: over 2,000 warm-up steps a leak is near-certain across thousands of streams.
- Log line: 84

### C7 — Positive control at the median grid point
Tests that at Gamma = 60.0, amplitudes (0.0, 0.5, 1.0, 1.5, 2.0, 3.0), 1000 seeds, reset arm, detectors can detect injected drift.
- Trigger probability: NOT RECOVERABLE FROM THE LOG.
- Realised margin: C7 admission outcome: ['CUSUM', 'ADWIN'] enter the monotonicity gate; ['PHT', 'DDM', 'EDDM'] are excluded by their inability to discriminate drift from noise.
- Verdict: Monotonicity gate and curve reported. The gate is fixed from the mechanism before any measurement.
- Log lines: 61, 90-97

### C7 monotonicity — ADD decreases at every step of the amplitude sweep
- Trigger probability: NOT RECOVERABLE FROM THE LOG.
- Realised margin: CUSUM decreases at every step; ADWIN rises between c 1.0 -> 1.5: +204.6446 +/- 26.8278 (7.6 SE); c 1.5 -> 2.0: +385.8367 +/- 29.4156 (13.1 SE).
- Verdict: Characterised against its paired standard error and reported; nothing is corrected.
- Log lines: 96-97

### C8 — Verbatim-copy and adapted-primitive checks
Verifies that all 6 untouched primitives are byte-identical to Priorite_12_multi_detector.py, and that simulate_garch11 is byte-identical from its `sigma2_unc` line down.
- Trigger probability: NOT RECOVERABLE FROM THE LOG.
- Realised margin: 2206 characters compared for primitives; 440 characters compared for simulate_garch11 tail.
- Verdict: Both checks passed. The two heads of simulate_garch11 differ by the RNG construction alone and are quoted in full in the log.
- Log lines: 10-40

## 3. Test suite

```
tests/test_R11_claims.py::test_R11_cardinalities_and_arms PASSED         [  4%]
tests/test_R11_claims.py::test_R11_gamma_grid_is_the_target_grid_and_its_floor_is_respected PASSED [  8%]
tests/test_R11_claims.py::test_R11_gamma_range_matches_the_published_multiplier PASSED [ 12%]
tests/test_R11_claims.py::test_R11_as_submitted_arm_is_the_per_detector_mixture PASSED [ 16%]
tests/test_R11_claims.py::test_R11_putting_both_detectors_on_one_convention_moves_the_cusum PASSED [ 20%]
tests/test_R11_claims.py::test_R11_the_published_ordering_holds_on_the_arm_that_produced_it PASSED [ 24%]
tests/test_R11_claims.py::test_R11_crn_h0_arm_is_degenerate_and_the_independent_arm_is_not PASSED [ 28%]
tests/test_R11_claims.py::test_R11_kish_design_effect_of_a_degenerate_grid_is_its_width PASSED [ 32%]
tests/test_R11_claims.py::test_R11_pht_intervals_carry_the_calibration_variance_factor PASSED [ 36%]
tests/test_R11_claims.py::test_R11_every_interval_bound_is_clamped PASSED [ 40%]
tests/test_R11_claims.py::test_R11_data_loglog_slopes_reproduce_by_an_independent_fit PASSED [ 44%]
tests/test_R11_claims.py::test_R11_pht_data_slope_is_fitted_on_a_restricted_domain PASSED [ 48%]
tests/test_R11_claims.py::test_R11_low_gamma_sensitivity_arm_excludes_exactly_the_unattainable_point PASSED [ 52%]
tests/test_R11_claims.py::test_R11_bootstrap_standard_errors_are_present_and_the_ratio_is_reported PASSED [ 56%]
tests/test_R11_claims.py::test_R11_no_macro_restates_the_cusum_scaling_law PASSED [ 60%]
tests/test_R11_claims.py::test_R11_submitted_linear_fits_are_reproduced_for_traceability PASSED [ 64%]
tests/test_R11_claims.py::test_R11_peak_to_peak_spread_is_descriptive_and_arithmetically_correct PASSED [ 68%]
tests/test_R11_claims.py::test_R11_preonset_leak_is_recorded_for_every_detector_even_at_zero PASSED [ 72%]
tests/test_R11_claims.py::test_R11_onset_table_carries_a_paired_error PASSED [ 76%]
tests/test_R11_claims.py::test_R11_the_two_adwin_implementations_are_labelled PASSED [ 80%]
tests/test_R11_claims.py::test_R11_river_version_is_recorded_in_the_artefacts PASSED [ 84%]
tests/test_R11_claims.py::test_R11_macros_are_emitted_with_the_preamble_ordinal PASSED [ 88%]
tests/test_R11_claims.py::test_R11_concept_add_macros_match_their_arm PASSED [ 92%]
tests/test_R11_claims.py::test_R11_eddm_macros_come_from_the_independent_seed_arm PASSED [ 96%]
tests/test_R11_claims.py::test_R11_report_against_v87 PASSED             [100%]

============================== 25 passed in 0.45s ==============================
```

Total: 25 tests passed.

## 4. Reproducibility digests

SHA-256 digests from a single run (886.0s campaign over 465000 monitored streams, 936.0s including the analysis):

| artefact | SHA-256 | log line |
|----------|---------|----------|
| R11_pht_fpr_vs_gamma.csv | 91d2b94b45fe8edfdc7e0658a88a7d5bcebea6285af00819369810bd83491164 | 124 |
| R11_concept_fpr_vs_gamma.csv | c0f1bb2096f140ea38c634b673dad39c2433e531cd6d3c6155ea19cb99871326 | 125 |
| R11_concept_fpr_vs_gamma_independent_seeds.csv | d0ac29eb6a1ce46e103a443187878f4ca2981d55e86337ab5f0a0b4c49891d45 | 126 |
| R11_concept_add_vs_gamma.csv | fca0e9c36045d12a9d26867e179834fc5244920fd986c1cd6d3c6155ea19cb99871326 | 127 |
| R11_adwin_magnitude.csv | 8b16d2b5364f4f47935a1e85a2da074228ecc43afa970d400796008b0545c744 | 128 |
| R11_data_add_vs_gamma.csv | 9fdcb08279fe858fa02f1ec0f8008e18032b23d6381e91dec18a0a379b3daf32 | 129 |
| R11_slope_fits.csv | 06943ff168bc0dc0dd95f706cb99816981e6cf8588bc01febbf3e11ae57f6471 | 130 |
| R11_onset_convention_delta.csv | 10bfd492c5eb54bed0fcdd15e6b4393c080cdbbaf04b7db8409ea9fe036248c4 | 131 |
| fig11_data_vs_concept.png | b9f06563dee497ba98cd8f51708c1251285d9c638685148ad9eb252ef0cdf198 | 132 |
| fig15_multi_detector.png | 229e61aa0e96c10a874ac7563c854d432649d885e0ba70e3b7c45dc3feeb9847 | 133 |
| figA04_adwin_blind_zone.png | bdd78f6473d8b534732459d1ca8fc8f0b27f338006eceade26780d08f982632a | 134 |
| R11_claims.tex | 01e3365b7aab88ee97c8a8bc5a5e338516d0b4df8c0922821acb100100e25b13 | 135 |

Current tree, single run:
```
8b16d2b5364f4f47935a1e85a2da074228ecc43afa970d400796008b0545c744  results/R11_multi_detector/data/R11_adwin_magnitude.csv
fca0e9c36045d12a9d26867e179834fc5244920fd986c1cd6171a5b6b3d5ebec  results/R11_multi_detector/data/R11_concept_add_vs_gamma.csv
c0f1bb2096f140ea38c634b673dad39c2433e531cd6d3c6155ea19cb99871326  results/R11_multi_detector/data/R11_concept_fpr_vs_gamma.csv
d0ac29eb6a1ce46e103a443187878f4ca2981d55e86337ab5f0a0b4c49891d45  results/R11_multi_detector/data/R11_concept_fpr_vs_gamma_independent_seeds.csv
9fdcb08279fe858fa02f1ec0f8008e18032b23d6381e91dec18a0a379b3daf32  results/R11_multi_detector/data/R11_data_add_vs_gamma.csv
10bfd492c5eb54bed0fcdd15e6b4393c080cdbbaf04b7db8409ea9fe036248c4  results/R11_multi_detector/data/R11_onset_convention_delta.csv
91d2b94b45fe8edfdc7e0658a88a7d5bcebea6285af00819369810bd83491164  results/R11_multi_detector/data/R11_pht_fpr_vs_gamma.csv
06943ff168bc0dc0dd95f706cb99816981e6cf8588bc01febbf3e11ae57f6471  results/R11_multi_detector/data/R11_slope_fits.csv
01e3365b7aab88ee97c8a8bc5a5e338516d0b4df8c0922821acb100100e25b13  results/R11_multi_detector/tables/R11_claims.tex
```

## 5. Design decisions taken outside the plan

None recorded.

## 6. Open questions, left open

None recorded.

