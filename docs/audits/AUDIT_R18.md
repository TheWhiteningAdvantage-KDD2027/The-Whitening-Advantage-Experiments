# Audit Report: R18 — Ljung-Box Power on Binary Streams

## 1. Deviation table (D0-D3)

R18 reproduces no figure, table or number of v87 (logs/R18_ljungbox_power/exp_R18_ljungbox_power.log line 11). Therefore no manuscript values are available for comparison, and no D0-D3 classification exists.

Count by severity: D0 = 0, D1 = 0, D2 = 0, D3 = 0.

## 2. Controls

### C1 — multiplicity across the four horizons
Tests that the four simultaneous 95% rejection-rate statements do not jointly violate the 5% family-wise error threshold. Trigger probability under its own null hypothesis: 1 - 0.95^4 = 0.1855 (logs/R18_ljungbox_power/exp_R18_ljungbox_power.log line 24). This control was demoted from a binary gate to a reported measurement because its trigger probability 0.1855 exceeds the 5% threshold proscribed by preamble S4bis. Replaced by: a Kolmogorov-Smirnov calibration test of the 1000 p-values against Uniform(0,1) at each horizon, with the four rates and their Wilson intervals reported as description. Verdict: all four KS p-values exceed 0.05 (0.6919 at n = 2000, 0.2140 at n = 8000, 0.3790 at n = 32000, 0.7745 at n = 128000 — logs/R18_ljungbox_power/exp_R18_ljungbox_power.log lines 25-28), and the pooled KS over stream indices yields bootstrap p = 0.5665 (line 29).

### C2 — monotonicity of the empirical power curve in theta at fixed n and in n at fixed theta
Tests that the rejection rate is non-decreasing in both the amplitude theta and the horizon n. Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: largest inversion in theta measured in paired standard errors is 1.50 against a margin of 2.0; largest inversion in n is 0.63 against 2.0 (logs/R18_ljungbox_power/exp_R18_ljungbox_power.log lines 30-33). Number of local inversions: 3 in theta, 2 in n, of which 0 exceed 2.0 paired standard errors. Verdict: all inversions are below the 2.0 paired-SE margin and are attributed to sampling noise; the curve is treated as monotone (line 31 and 33).

### C3 — sign pattern of empirical minus analytic power on the local domain
Tests the direction and magnitude of the departure between the empirical rejection rate and the analytic power prediction where the local chi-square limit is justified (power_analytic < 0.95). Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: maximum |empirical - analytic| is 0.0421 on the domain against a tolerance of 0.0474 = 3 * 0.5/sqrt(1000), i.e. three standard errors of a proportion at its worst variance (logs/R18_ljungbox_power/exp_R18_ljungbox_power.log lines 34-35). The empirical rate exceeds the analytic prediction at 48 of 67 amplitudes inside the domain; sign-test p = 5.216e-04 under independence, which the C4 pairing violates so the p-value understates. Verdict: the maximum deviation 0.0421 is within the tolerance 0.0474; the direction is reported and no term is added to the prediction.

### C4 — design effect of the paired Monte-Carlo draws
Tests the intra-cluster correlation induced by the C4 pairing (one uniform vector shared across all amplitudes at each stream index). Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: Kish design effect 1.962 measured at n = 8000 on 36000 readings, effective sample size 18351, cluster standard error 0.00362 against 0.00258 for a simple random sample, ratio 1.401; mean correlation of the rejection indicator between two of the 21 amplitudes whose indicator varies is 0.350, max 0.868 (logs/R18_ljungbox_power/exp_R18_ljungbox_power.log line 36). Verdict: NO INTERVAL POOLED OVER THE GRID IS PUBLISHED; the per-point Wilson intervals remain valid, each resting on 1000 independent streams.

### C5 — generator fidelity
Tests that the symmetric two-state Markov chain generator produces the exact autocorrelation rho(k) = (2*theta)^k and the exact marginal Bernoulli(0.5) law. Trigger probability under a correct generator: the autocorrelation arm is a four-sigma band, so 6.3e-5 two-sided; the marginal arm is a 95% Wilson interval, so 5% (logs/R18_ljungbox_power/exp_R18_ljungbox_power.log line 18). Realised margin: pooled lag-1 autocorrelation 0.19996860625004817 against the exact 0.2, deviation -3.139e-05 for a tolerance of 4.472e-04 = 4/sqrt(10000*8000), i.e. 0.070 of the budget; marginal rate 0.49992356, Wilson [0.49981400, 0.50003313] on 80000000 observations, and [0.49978937, 0.50005775] after the sqrt((1+rho)/(1-rho)) = 1.2247 inflation (lines 17-18). Verdict: both arms pass; the autocorrelation deviation is 0.070 of its budget, and both Wilson intervals cover their targets.

## 3. Test suite

```
============================= test session starts ==============================
platform linux -- Python 12.9, pytest-9.0.3, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /home/m53/The-Whitening-Advantage-Experiments
plugins: anyio-4.8
collecting ... collected 24 items

tests/test_R18_claims.py::test_R18_every_artefact_the_prompt_lists_exists_with_its_prescribed_schema PASSED [  4%]
tests/test_R18_claims.py::test_R18_the_grids_have_the_cardinality_their_specification_fixes PASSED [  8%]
tests/test_R18_claims.py::test_R18_the_amplitude_grid_is_the_one_the_design_specifies PASSED [ 12%]
tests/test_R18_claims.py::test_R18_the_lag_one_autocorrelation_column_is_twice_the_amplitude PASSED [ 16%]
tests/test_R18_claims.py::test_R18_the_non_centrality_column_closes_its_own_geometric_sum PASSED [ 20%]
tests/test_R18_claims.py::test_R18_the_analytic_power_column_is_the_non_central_chi_square_tail PASSED [ 25%]
tests/test_R18_claims.py::test_R18_the_analytic_power_is_monotone_in_both_of_its_arguments PASSED [ 29%]
tests/test_R18_claims.py::test_R18_the_deviation_column_is_the_difference_it_names PASSED [ 33%]
tests/test_R18_claims.py::test_R18_the_wilson_intervals_agree_with_the_roots_of_the_score_equation PASSED [ 37%]
tests/test_R18_claims.py::test_R18_the_size_of_the_test_covers_the_nominal_level_at_every_horizon PASSED [ 41%]
tests/test_R18_claims.py::test_R18_the_null_p_values_are_calibrated_against_the_kolmogorov_limit PASSED [ 45%]
tests/test_R18_claims.py::test_R18_the_empirical_curve_matches_the_analytic_one_inside_the_local_domain PASSED [ 50%]
tests/test_R18_claims.py::test_R18_the_detectable_amplitude_solves_its_own_analytic_equation PASSED [ 54%]
tests/test_R18_claims.py::test_R18_the_detectable_amplitude_halves_when_the_horizon_quadruples PASSED [ 58%]
tests/test_R18_claims.py::test_R18_the_non_centrality_at_eighty_percent_power_is_a_constant_of_the_test PASSED [ 62%]
tests/test_R18_claims.py::test_R18_the_application_arms_carry_the_two_grids_they_borrow PASSED [ 66%]
tests/test_R18_claims.py::test_R18_the_realised_penalty_matches_its_target_where_the_target_is_attainable PASSED [ 70%]
tests/test_R18_claims.py::test_R18_the_measured_sign_streams_sit_below_the_detectable_amplitude PASSED [ 75%]
tests/test_R18_claims.py::test_R18_the_power_at_the_measured_autocorrelation_is_the_analytic_one PASSED [ 79%]
tests/test_R18_claims.py::test_R18_the_ljung_box_rejection_of_both_arms_covers_the_nominal_level PASSED [ 83%]
tests/test_R18_claims.py::test_R18_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix PASSED [ 87%]
tests/test_R18_claims.py::test_R18_the_headline_macros_agree_with_the_frames_they_are_computed_from PASSED [ 91%]
tests/test_R18_claims.py::test_R18_the_reported_detectable_amplitude_is_the_one_the_analytic_law_gives PASSED [ 95%]
tests/test_R18_claims.py::test_R18_report_the_bound_the_repository_can_state PASSED [100%]

============================== 24 passed in 0.77s ==============================
```

Total for the whole suite: 24 (logs/R18_ljungbox_power/exp_R18_ljungbox_power.log does not record a total; the pytest output above shows 24 passed).

## 4. Reproducibility digests

SHA-256 digests from the log (single run, n_jobs = -1):

```
SHA-256 R18_power_vs_theta.csv                   : a6396d87f0abbb5feb66f7d552a4ca4d6df710fa51ace334afe7baa9e40fc2b1 (line 97)
SHA-256 R18_power_vs_horizon.csv                 : d6f9b388a3c66fa639de8afc4657eb26de0827746692df2f3bd395071927a438 (line 98)
SHA-256 R18_detectable_amplitude.csv             : 765ba366e79afe696501668aa775a2bfc30fb4f9c69a3cf1d16946c9b347540a (line 99)
SHA-256 R18_applied_to_sign_streams.csv          : 4315c1467c1aec815b3064196fb23d616d0e8095f1962a467ec4312c2b54a552 (line 100)
SHA-256 R18_size_at_null.csv                     : 38f76e7a0b97f47879869bfeb6067701254a7fe418eaafd18347540a (line 101)
SHA-256 figA05_ljungbox_power.png                : 2651f59d05594cb0cd4607c9daba9fb8903c635d0fd8cb2e5d15bbfd4de8e366 (line 102)
SHA-256 R18_claims.tex                           : 671faf44c05edb1f55fc132e7b89c397d11bccc09437bcf0f5ac4aaea3e26307 (line 103)
```

current tree, single run:
```
4315c1467c1aec815b3064196fb23d616d0e8095f1962a467ec4312c2b54a552  results/R18_ljungbox_power/data/R18_applied_to_sign_streams.csv
765ba366e79afe696501668aa775a2bfc30fb4f9c69a3cf1d16946c9b347540a  results/R18_ljungbox_power/data/R18_detectable_amplitude.csv
d6f9b388a3c66fa639de8afc4657eb26de0827746692df2f3bd395071927a438  results/R18_ljungbox_power/data/R18_power_vs_horizon.csv
a6396d87f0abbb5feb66f7d552a4ca4d6df710fa51ace334afe7baa9e40fc2b1  results/R18_ljungbox_power/data/R18_power_vs_theta.csv
38f76e7a0b97f47879869bfeb6067701254a7fe418eaafd18347540a  results/R18_ljungbox_power/data/R18_size_at_null.csv
671faf44c05edb1f55fc132e7b89c397d11bccc09437bcf0f5ac4aaea3e26307  results/R18_ljungbox_power/tables/R18_claims.tex
```

## 5. Design decisions taken outside the plan

1. The seed key for C4 is ('R18', 'power', index) with NO theta and NO n_steps, so one uniform vector of length 128000 generates the chain at every amplitude by re-thresholding and its first n entries generate every horizon; the grid is paired by construction (logs/R18_ljungbox_power/exp_R18_ljungbox_power.log line 15).

2. Pass 1 of the grid measured horizon 128000 alone (36 amplitudes x 1000 streams) before the rest of the grid was launched, to report its cost rather than use it to trim the design; it elapsed 129.3s on n_jobs = -1 (line 20).

3. The binary gate on the four simultaneous 95% rejection-rate statements (C1) was replaced by a Kolmogorov-Smirnov calibration test of the 1000 p-values against Uniform(0,1) at each horizon, because 1 - 0.95^4 = 0.1855 exceeds the 5% threshold of preamble S4bis; the four rates and their Wilson intervals are reported as description instead (line 24).

4. The cluster-bootstrap 95% interval on theta_80 at n = 32000 [0.012956, 0.013490] does not cover the analytic root 0.012793; this finding is recorded but no draw, grid or tolerance is touched, per preamble S4.7, and the macro file carries the grid estimate, the analytic root and the bootstrap interval as three separate values (line 42).

5. The attainable penalty floor at alpha = 0.08 is 1 + 2*alpha/(1-alpha) = 1.1739130434782608; arm (b) inherits R11's 20-point target grid, whose first target 1.0 lies below it, and Gamma_target, Gamma_realised and attainable are carried as three distinct columns; the finding itself is cited from docs/DEVIATIONS.md `R11-gamma-grid-floor` rather than restated (line 44).

## 6. Open questions, left open

None recorded.
