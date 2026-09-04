# AUDIT R06 — Empirical Validity Map

## 1. Deviation table (D0-D3)

| quantity | manuscript value | regenerated value | severity | source CSV cell | log line |
|----------|------------------|-------------------|----------|-----------------|----------|
| Pooled binary rejection over the Gamma grid | 0.0477 | 0.0477 | D0 | R06_gamma_grid.csv :: p_concept | 34 |
| Pooled squared-stream rejection over the grid | 0.9277 | 0.9277 | D0 | R06_gamma_grid.csv :: p_data | 35 |
| Task boundary binary c = 0.0 | 0.0700 | 0.0700 | D0 | R06_task_boundary.csv :: p_val | 36 |
| Task boundary binary c = 0.25 | 0.4400 | 0.4400 | D0 | R06_task_boundary.csv :: p_val | 37 |
| Task boundary binary c = 0.5 | 1.0000 | 1.0000 | D0 | R06_task_boundary.csv :: p_val | 38 |
| Task boundary binary c = 1.0 | 1.0000 | 1.0000 | D0 | R06_task_boundary.csv :: p_val | 39 |
| Task boundary continuous MSE | 1.0000 | 1.0000 | D0 | R06_task_boundary.csv :: p_val | 40 |
| Fourth-moment boundary Gamma | 41.6000 | 41.5843 | D1 | N/A (analytic) | 41 |

Count by severity: 7 D0, 1 D1, 0 D2, 0 D3.

The single D1 deviation is the fourth-moment boundary Gamma: manuscript value 41.6 vs regenerated value 41.584288. At the one-decimal-place precision used in the manuscript, round(41.584288, 1) = 41.6, matching exactly. The boundary is an analytic computation from (alpha, nu) using closed-form expressions: kurtosis = 3*(nu-2)/(nu-4) = 5.0 for nu = 7, solving kurtosis * alpha^2 + 2 * alpha * beta + beta^2 = 1 yields beta = 0.907117, mapping to Gamma = 41.584288. The value is NOT a measured grid point; the nearest measured Gamma is 41, which is 0.584288 below the analytic boundary.

## 2. Controls

### Control (a): Specification check
Tests that the Gamma grid, number of streams, nu parameter, c grid, task types, n steps, Ljung-Box lag, and nominal level match the specification in v87. Trigger probability: NOT RECOVERABLE FROM THE LOG. Verdict: Passed (line 11).

### Control (b): Calibration of the pooled binary rejection with cluster-robust interval
Tests that the pooled binary rejection rate covers the nominal level when the design variance (pairing) is accounted for. The cluster bootstrap interval resamples SEEDS, not streams. Trigger probability: 0.05 (nominal level). Realised margin: 0.020000 standard errors (half-width of cluster bootstrap interval [0.029231, 0.069231]). Verdict: Contains 0.05: True (GATING) — line 23.

Note: The Wilson interval that assumes 1300 independent streams would read [0.037381, 0.060669], half-width 0.011644, understating by sqrt(design effect) = 1.7913. The per-Gamma family of 13 simultaneous 95% intervals fires at least once with probability 1 - 0.95^13 = 0.4867 under its own null, which preamble S4bis forbids. The 13 per-Gamma gates of the submitted script were therefore demoted from a gate to a reported measurement.

### Control (c): Squared-stream check
Tests that the squared stream (p_data) rejects massively across the grid. Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: Pooled rejection 0.927692 (1206/1300), with all Gamma >= 2.0 at 100% rejection. Verdict: Reported, with no assertion on any extremum (line 25).

### Control (d): Task-boundary check
Tests that saturated cells reach 100% rejection and the intermediate threshold is reported. Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: binary c=0.0: 0.07, binary c=0.25: 0.44, binary c=0.5: 1.00, binary c=1.0: 1.00, continuous c=0.0: 1.00. Verdict: The three saturated cells [('binary', 0.5), ('binary', 1.0), ('continuous', 0.0)] all reach 1.0 (lines 27-28). The intermediate cell binary c = 0.25 at 0.44 is NOT CITED IN v87 and is kept as the only measurement of the transition.

### Control (e): Median-task control
Tests that the median task (binary c = 0) control covers the nominal level and documents its resolution limitation. Trigger probability: 0.05 (nominal level). Realised margin: Wilson 95% [0.034319, 0.137495], half-width 5.2 percentage points = 1.0 times the nominal level. Verdict: Contains 0.05: True. At N = 100 the half-width is 5.2 percentage points, so the control is consistent with whiteness rather than confirmatory. Every true rate from 3.4% to 13.7% is compatible with what was observed (lines 29-30).

### Control (a): Cardinality check
Tests that the cardinalities of the generated dataframes match the specification. Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: R06_gamma_grid = 1300, R06_task_boundary = 500, R06_gamma_grid_independent_seeds = 1300. Verdict: Passed (line 31).

## 3. Test suite

```
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-9.1.3, pluggy-1.6.0 -- /home/m53/miniforge3/envs/Trading/bin/python3.12
cachedir: .pytest_cache
rootdir: /home/m53/The-Whitening-Advantage-Experiments
plugins: anyio-8.4.2
collecting ... collected 16 items

tests/test_R06_claims.py::test_R06_cardinalities_and_grid PASSED         [  6%]
tests/test_R06_claims.py::test_R06_gamma_grid_is_realised_in_closed_form PASSED [ 12%]
tests/test_R06_claims.py::test_R06_fourth_moment_boundary_is_computed_not_hard_coded PASSED [ 18%]
tests/test_R06_claims.py::test_R06_boundary_is_not_confused_with_the_nearest_grid_point PASSED [ 25%]
tests/test_R06_claims.py::test_R06_panel_A_design_is_paired_and_declared PASSED [ 31%]
tests/test_R06_claims.py::test_R06_pooled_binary_level_covers_nominal_at_cluster_precision PASSED [ 37%]
tests/test_R06_claims.py::test_R06_counterfactual_arm_removes_the_pairing PASSED [ 43%]
tests/test_R06_claims.py::test_R06_no_per_gamma_gate_is_possible PASSED [ 50%]
tests/test_R06_claims.py::test_R06_squared_stream_rejects_massively PASSED [ 56%]
tests/test_R06_claims.py::test_R06_task_boundaries_saturate PASSED       [62%]
tests/test_R06_claims.py::test_R06_intermediate_threshold_is_reported_and_labelled PASSED [ 68%]
tests/test_R06_claims.py::test_R06_median_task_control_covers_nominal_and_is_weakly_resolved PASSED [ 75%]
tests/test_R06_claims.py::test_R06_no_silent_fallback_survived_into_the_artefacts PASSED [ 81%]
tests/test_R06_claims.py::test_R06_reproduces_the_witness_byte_for_byte PASSED [ 87%]
tests/test_R06_claims.py::test_R06_macros_are_emitted_and_computed PASSED [ 93%]
tests/test_R06_claims.py::test_R06_report_against_the_witness PASSED     [100%]

============================== 16 passed in 0.72s ==============================
```

Total: 16 passed in 0.72s.

## 4. Reproducibility digests

From log (lines 44-48):
- SHA-256 R06_gamma_grid.csv : b1b94011b8b94dd8fdfdbd60731da054e25ea774f6c2887e037714f709bbc744
- SHA-256 R06_task_boundary.csv : 9a95701f7131e8a686a30d9293b2d439dd1bf3367ecdc536dacd20a078c1f93e
- SHA-256 R06_gamma_grid_independent_seeds.csv : c4fdeebc1ffebb01e54ee9717bf31ad1f0c362a890b0548826d7329e7e12a863
- SHA-256 fig06_validity_map.png : 8909ad650d4969c0a47c2aebdcaa0abe3936b8d4988ae422798c6e82fa77d8fb
- SHA-256 R06_claims.tex : 7572a736f24d9f27e7dcb9bedb043dd046adbf3ffccbe8c744f63615d31d7d7e

Current tree, single run:
```
b1b94011b8b94dd8fdfdbd60731da054e25ea774f6c2887e037714f709bbc744  results/R06_validity_map/data/R06_gamma_grid.csv
c4fdeebc1ffebb01e54ee9717bf31ad1f0c362a890b0548826d7329e7e12a863  results/R06_validity_map/data/R06_gamma_grid_independent_seeds.csv
9a95701f7131e8a686a30d9293b2d439dd1bf3367ecdc536dacd20a078c1f93e  results/R06_validity_map/data/R06_task_boundary.csv
7572a736f24d9f27e7dcb9bedb043dd046adbf3ffccbe8c744f63615d31d7d7e  results/R06_validity_map/tables/R06_claims.tex
```

## 5. Design decisions taken outside the plan

1. The submitted script hard-coded its own observed rejection rates for all 13 Gamma and all 5 task cells and exited on any deviation at 1e-9. This is a self-certification that can only reproduce, not measure. Preamble S1.2 forbids a published value as a target. Decision: removed the hard-coded gates, replaced with measured rates and proper statistical controls.

2. The submitted script gated the Wilson interval at each of the 13 Gamma separately. Under its own null that family fires with probability 1 - 0.95^13 = 48.67% under its own null, which preamble S4bis forbids. Decision: the level is judged pooled instead of per-cell.

3. Three fallbacks returned silently in the submitted script, all three biased towards "white": an unnamed exception mapped to NaN (counts as non-rejection), a degenerate stream mapped to p = 1.0 (counts as non-rejection), and a null prediction mapped to class 0 (structural, 1 per stream at t = 0, 3000 total in this campaign). Decision: named, counted and logged: 0 degenerate streams, 0 estimator failures, 3000 null predictions (line 21).

4. The design of panel A is paired: the submitted campaign draws the innovations before the variance recursion, so sign(sigma_t z_t) = sign(z_t) and one seed carries the same LABEL stream to every Gamma. The ERROR stream is not shared (the classifier reads amplitudes). Decision: declared the paired design, measured its design effect (3.2088), and computed the pooled interval by resampling SEEDS rather than streams.

5. The fourth-moment boundary is computed from (alpha, nu) using closed-form expressions rather than being hard-coded as 41.6. Decision: analytic computation yielding Gamma = 41.584288, which rounds to 41.6 at manuscript precision (D1). The nearest measured Gamma is 41, which is 0.584288 below the analytic boundary, and the two must not be conflated.

## 6. Open questions, left open

1. The median-task control (binary c = 0) has a Wilson interval [0.034319, 0.137495] with half-width 5.2 percentage points, which is 1.0 times the nominal level. This control excludes very little and is consistent with whiteness rather than confirmatory. Is this resolution limitation acceptable for the purposes of the manuscript, or should the design be strengthened?

2. The squared-stream rejection is 0.927692 (1206/1300) with all Gamma >= 2.0 at 100% rejection. The per-Gamma descriptive rates are emitted but not gated. Should any threshold be set for individual Gamma points, and if so, at what level?

3. The intermediate threshold binary c = 0.25 at 0.44 rejection is NOT CITED IN v87. It is the only measurement of the transition between the white regime and the saturated one in this repository. Should this value be added to the manuscript, or is its absence intentional?

4. The design effect is measured at 3.2088 for the paired campaign. The counterfactual arm with independent per-cell seeds yields a design effect of 1.0133. The paired design sharpens comparisons across Gamma, but could the pairing mask effects that vary within a seed across Gamma?
