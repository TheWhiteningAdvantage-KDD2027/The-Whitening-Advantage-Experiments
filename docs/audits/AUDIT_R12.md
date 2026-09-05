# R12: GJR Leverage Misspecification and Moment Singularity

## 1. Deviation table (D0-D3)

| quantity | manuscript value | regenerated value | severity | source CSV cell | log line |
|---|---|---|---|---|---|
| L349/Fig.12 Ljung-Box at gamma_lev = 0.0 | 5.1% | 5.4% | D2 | R12_leverage_fpr.csv, gamma_lev=0.0/lb_data_pct | l.294 |
| L349/Fig.12 Ljung-Box at gamma_lev = 0.28 | 24.6% | 24.2% | D2 | R12_leverage_fpr.csv, gamma_lev=0.28/lb_data_pct | l.296 |
| L349/Fig.12 FPR at gamma_lev = 0.0 | 3.2% | 3.5% | D2 | R12_leverage_fpr.csv, gamma_lev=0.0/fpr_data | l.298 |
| L349/Fig.12 FPR at gamma_lev = 0.28 | 20.6% | 20.5% | D2 | R12_leverage_fpr.csv, gamma_lev=0.28/fpr_data | l.300 |
| L349/Fig.12 Concept FPR minimum | 7.6% | 7.4% | D2 | R12_leverage_fpr.csv, min/max fpr_concept, arm expA_concept_indep | l.302 |
| L349/Fig.12 Concept FPR maximum | 8.4% | 8.5% | D2 | R12_leverage_fpr.csv, min/max fpr_concept, arm expA_concept_indep | l.304 |
| L349 Concept Ljung-Box minimum | 4.6% | 4.7% | D2 | R12_leverage_fpr.csv, min/max lb_concept_pct, arm expA_concept_indep | l.306 |
| L349 Concept Ljung-Box maximum | 5.4% | 5.4% | D1 | R12_leverage_fpr.csv, min/max lb_concept_pct, arm expA_concept_indep | l.308 |
| L349 'climbs by a factor of six' | 6 | 6 | D1 | R12_leverage_fpr.csv, fpr_data ratio | l.310 |
| Fig.12 caption streams per point | 10,000 | 10,000 | D0 | N_SEEDS_A | l.312 |
| Fig.13 caption streams per point | 1,000 | 1,000 | D0 | N_SEEDS_B | l.314 |
| Fig.12 leverage grid size | 15 | 15 | D0 | GAMMA_LEV_GRID, witness l.233 | l.316 |
| Fig.13 nu grid size | 16 | 16 | D0 | NU_GRID, witness l.332 | l.318 |
| L353 detection at nu = 10 | 83% | 82% | D2 | R12_singularity_add.csv, nu=10/det_rate_data | l.320 |
| L353 detection at nu = 7 | 61% | 62% | D2 | R12_singularity_add.csv, nu=7/det_rate_data | l.322 |
| L353 collapse threshold, largest nu below 50% | 5.5 | 5.5 | D1 | R12_singularity_add.csv, max nu with det_rate_data < 0.5 | l.324 |
| L353 censored delay minimum | 2,400 | 2,600 | D2 | R12_singularity_add.csv, min ADD_Data_Raw on the censored domain | l.326 |
| L353 censored delay maximum | 3,000 | 3,000 | D1 | R12_singularity_add.csv, max ADD_Data_Raw on the censored domain | l.328 |
| L353 Concept delay minimum | 34 | 34 | D1 | R12_singularity_add.csv, min ADD_Concept | l.330 |
| L353 Concept delay maximum | 38 | 38 | D1 | R12_singularity_add.csv, max ADD_Concept | l.332 |

Count by severity: D0: 4, D1: 6, D2: 10, D3: 0.

## 2. Controls

### C1 -- `det_rate_concept` IS COMPUTED, NOT A LITERAL
Asserted on this file's own AST and, independently, in tests/test_R12_claims.py. Deterministic; trigger probability 0; failure is a D3 because the flatness of the Concept arm would then be unmeasured. Corroboration after the campaign: det_rate_concept is 1.0000-1.0000 over the sixteen nu, and ADD_Concept varies over 33.638-37.900 steps, a span of 4.262 (log l.132, l.115, l.197).

### C2 -- THE CENSORING RULE, STATED BEFORE THE REGENERATED FRAME IS READ
`ADD_Data` and `SEM_Data` are written only where det_rate_data >= 0.5, which is the witness's own rule and the rule the published figure censors on. `ADD_Data_Raw` carries the conditional delay at EVERY nu, because v87 L353 explicitly publishes the censored domain. The witness leaves the DISPERSION of exactly those published values missing, so `SEM_Data_Raw` is added on the surviving streams of every cell. Without it S3's rule cannot be evaluated on the one range v87 prints for the censored domain. Deterministic; trigger probability 0 (log l.133).

### C3 -- TASK BOUNDARY, AS A READ AND NOT AS A MEASUREMENT
The claim behind `expA_argarch_boundary.csv` -- that the property holds at the MEDIAN threshold and not at the ZERO threshold -- is v87 L302, which is R07's mission statement, and R07 has already delivered it on a certified campaign. C3 therefore READS R07's phi = 0.15 cell at float_precision='round_trip' and prints it beside the orphan witness, states the gap, and leaves it unexplained. NO MACRO, NO REGISTER ENTRY. Deterministic. R12's own negative witnesses are the cells it actually runs: gamma_lev = 0.0 and nu = 10.0. Trigger probability: NOT RECOVERABLE FROM THE LOG. (log l.134-154).

C3b `expB_race_condition.csv` IS PRODUCED AND NOT CITED. 1000 rows, seed 0-999 with 1000 distinct values. `delay_frozen` is populated on all 1000 rows; `delay_arf` is EMPTY on 999 of 1000 rows. Reported as measured; THE MECHANISM IS NOT ATTRIBUTED. v87 cites no frozen-versus-ARF race, so there is no reconstruction, no camera-ready candidate and no register entry (log l.155).

### C4 -- MONOTONICITY, WITH ITS DOMAIN DECLARED BEFORE THE DATA IS READ
v87 L353 states 'detection decays monotonically' with NO domain restriction, and the submitted witness is ALREADY non-monotone at nu = 4.75 and nu = 4.05, both inside the censored domain. The gate is therefore declared on det_rate_data over the UNCENSORED domain (det_rate_data >= 0.5) and nowhere else. RESTRICTING THE DOMAIN IS THIS REPOSITORY'S CHOICE, NOT v87'S FORMULATION: it salvages the region where the quantity is a reliable mean rather than a survivorship-biased one. Censored inversions are characterised with their PAIRED standard errors and never corrected. An inversion in the uncensored region is a D3. Trigger probability under its own null: 0 (deterministic domain restriction). The gate is met: det_rate_data decreases at every adjacent pair of the uncensored domain (6 pairs) (log l.135, l.248-250).

### C5 -- LJUNG-BOX CALIBRATION, NOT A BINARY GATE
1 - 0.95^30 = 0.7854 is computed and logged before interpretation. The reading is a two-sided Kolmogorov-Smirnov test of the 30 exact binomial p-values against Uniform(0,1), reported for the whole family (D = 0.4533132209266487, p = 3.767279117365883e-06) and separately per arm: Data arm (D = 0.9369321658226811, p = 1.9867752983182183e-18), Concept arm (D = 0.1701196640935867, p = 0.7171151534601743). NOTHING IS GATED ON IT, and the reason is stated in the same breath: the Data arm's rejection rate climbing to 24.6% IS v87's own printed claim, so a uniformity test on that arm rejects precisely because the manuscript is right. The 30 individual p-values are persisted in R12_leverage_fpr.csv as DESCRIPTIVE columns. Trigger probability under its own null: NOT RECOVERABLE FROM THE LOG. (log l.126-127, l.136, l.251-252).

### C6 -- `ast` SOURCE IDENTITY, three layers
Run before any campaign so a transcription error costs no compute. Deterministic; trigger probability 0 unless a copy has drifted. 3 byte-identical primitives to Priorite_10_robustness_gjr_student.py (simulate_gjr_garch, compute_gamma_exact, strict_cusum). 29 statements extracted from the witness AST and found verbatim in exp_R12_gjr_student.py. (log l.14, l.114, l.137).

### C7 -- REPRODUCIBILITY, TWO AXES
(1) two successive runs, SHA-256 identical on every CSV, PNG and .tex; (2) a run at a different `--n-jobs` against the default, byte-identical, since NUM_CHUNKS_A = 25 and NUM_CHUNKS_B = 10 fix the decomposition and every stream carries its own key. Verified outside the process, from the digests this log records. Trigger probability: NOT RECOVERABLE FROM THE LOG. (log l.138).

### C8 -- THE CRN CONCEPT ARM IS DEGENERATE, AND IT IS ASSERTED RATHER THAN OBSERVED
On 50 subsampled seeds the SHA-256 of (eps[2000:7000] > 0) must be IDENTICAL at all 15 gamma_lev under the key ('R12', 'expA', s), with sys.exit(1) otherwise. The Kish design effect is measured on BOTH Concept arms: 15 by construction on the CRN arm, near 1 on the independent one. On all 50 subsampled seeds the SHA-256 of (eps[2000:7000] > 0) is IDENTICAL at all 15 gamma_lev: eps[t] = sqrt(sigma2[t]) * z[t] with sigma2[t] > 0, so sign(eps_t) = sign(z_t) exactly and the leverage leaves no trace on the sign. R12_concept_crn_witness.csv therefore carries one number repeated 15 times, its effective sample size is 10000 and not 150000, and IT SUPPORTS NO CLAIM. Every published Concept rate, interval, macro and figure point is taken from the arm keyed ('R12', 'expA_concept_indep', gamma_index, s), whose key breaks the pairing. Deterministic; trigger probability 0 unless the generator or the key has changed (log l.139, l.159-163).

Design effects measured: deff(fp_concept) = 15.0015 (CRN) vs 1.0004 (independent); deff(lb_concept) = 15.0015 vs 0.9843; deff(fp_data) = 9.1059 (CRN) vs 0.9528; deff(lb_data) = 9.0668 (CRN) vs 0.9675 (log l.160-162).

### C9 -- LEVERAGE INVARIANCE AS A SLOPE, BECAUSE A RANGE HAS NO NULL
v87's 'leverage-invariant' is tested by an OLS slope of the INDEPENDENT-arm Concept FPR on gamma_lev against a null of zero slope, with a seed-cluster bootstrap standard error over 2000 replicates. GATE AT 0.01, two-sided; trigger probability under its own null is exactly 0.01. OLS of the Concept false-alarm rate (percentage points) on gamma_lev over the 15 grid points: slope = -0.9285714285714289 points per unit gamma_lev, intercept 8.088, R^2 = 0.0789. Analytic OLS standard error 0.8797; seed-cluster bootstrap standard error 0.8034 over 2000 resamples, percentile 95% interval [-2.4500, 0.6577]. Two-sided p against a null of zero slope: 0.2477349743281695. GATE AT 0.01: not fired (log l.140, l.253-255).

### C10 -- THE DGP VARIANCE CLAMP, MEASURED RATHER THAN ASSUMED
`simulate_gjr_garch` l.106 caps sigma2[t] <= 1e4 * sigma2_unc. At gamma_lev = 0.28 the persistence is 0.99 and near nu = 4 the innovations are extreme, so the clamp is a silent execution path that could mechanically produce the published collapse. The primitive is carried VERBATIM; the binding rate is measured by a separate instrumented copy on 200 streams per grid point, each asserted to return a bit-identical eps, and lands in R12_diagnostics.csv and the audit ONLY. Reported, not gated. Total over the whole subsample: 0 clamped steps of 52993800 (log l.141, l.164-196).

### C11 -- LEGACY-GLOBAL INERTNESS, ASSERTED RATHER THAN ASSUMED
The witness locks np.random and random and nothing downstream reads either. Each worker is evaluated TWICE under deliberately different global states and must return bit-identical output; that is what justifies dropping the two calls rather than carrying them. Deterministic; trigger probability 0. _worker_expA at gamma_lev = 0.28 and _worker_expB at nu = 4.01 each return bit-identical output under two deliberately different np.random / random global states. Note what this does NOT establish: it is a statement about these two workers and the statsmodels version logged above, not about acorr_ljungbox in general (log l.142, l.147).

## 3. Test suite

```
============================= test session starts ==============================
platform linux -- Python 12.9, pytest-9.0.3, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /home/m53/The-Whitening-Advantage-Experiments
plugins: anyio-4.8
collected 26 items

tests/test_R12_claims.py::test_R12_every_artefact_the_plan_lists_exists PASSED [  3%]
tests/test_R12_claims.py::test_R12_the_grids_and_stream_counts_are_the_ones_v87_specifies PASSED [  7%]
tests/test_R12_claims.py::test_R12_the_published_concept_arm_is_the_independent_key_on_every_row PASSED [ 11%]
tests/test_R12_claims.py::test_R12_the_three_carried_primitives_are_byte_identical_to_the_witness PASSED [ 15%]
tests/test_R12_claims.py::test_R12_det_rate_concept_is_computed_and_not_a_literal PASSED [ 19%]
tests/test_R12_claims.py::test_R12_the_concept_detection_rate_is_a_full_count_and_not_a_rounded_one PASSED [ 23%]
tests/test_R12_claims.py::test_R12_every_wilson_interval_is_the_score_interval_of_its_own_rate PASSED [ 26%]
tests/test_R12_claims.py::test_R12_the_fourth_moment_boundary_and_the_exact_penalty_are_their_own_closed_forms PASSED [ 30%]
tests/test_R12_claims.py::test_R12_the_leverage_grid_runs_to_the_edge_of_the_stationary_region PASSED [ 34%]
tests/test_R12_claims.py::test_R12_the_censoring_rule_is_the_one_stated_before_the_frame_was_read PASSED [ 38%]
tests/test_R12_claims.py::test_R12_the_baseline_false_alarm_rate_explodes_with_leverage PASSED [ 42%]
tests/test_R12_claims.py::test_R12_the_sign_pipeline_holds_a_leverage_invariant_rate PASSED [ 46%]
tests/test_R12_claims.py::test_R12_detection_decays_monotonically_on_the_uncensored_domain PASSED [ 50%]
tests/test_R12_claims.py::test_R12_the_collapse_threshold_is_the_one_L353_prints PASSED [ 53%]
tests/test_R12_claims.py::test_R12_the_concept_delay_stays_flat_at_the_printed_range PASSED [ 57%]
tests/test_R12_claims.py::test_R12_the_concept_false_alarm_envelope_has_moved_at_both_ends PASSED [ 61%]
tests/test_R12_claims.py::test_R12_the_censored_delay_minimum_has_moved_but_stays_in_its_rounding_bracket PASSED [ 65%]
tests/test_R12_claims.py::test_R12_the_detection_rate_at_nu_ten_is_a_count_whose_printed_rounding_moved PASSED [ 69%]
tests/test_R12_claims.py::test_R12_the_crn_concept_arm_is_one_number_repeated_fifteen_times PASSED [ 73%]
tests/test_R12_claims.py::test_R12_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix PASSED [ 76%]
tests/test_R12_claims.py::test_R12_the_macros_agree_with_the_frames_they_are_computed_from PASSED [ 80%]
tests/test_R12_claims.py::test_R12_every_produced_text_file_ends_in_a_newline PASSED [ 84%]
tests/test_R12_claims.py::test_R12_the_produced_sources_and_logs_carry_no_confirmatory_language PASSED [ 88%]
tests/test_R12_claims.py::test_R12_the_produced_sources_carry_no_banned_construct PASSED [ 92%]
tests/test_R12_claims.py::test_R12_report_the_campaign_against_its_witness PASSED [ 96%]
tests/test_R12_claims.py::test_R12_report_the_control_layer PASSED       [100%]

============================== 26 passed in 0.48s ==============================
```

Total: 26 passed in 0.48s.

## 4. Reproducibility digests

log-captured run (n_jobs = -1, 316000 monitored streams):

SHA-256 R12_leverage_fpr.csv               : 8a0326eff4444d99b4769781ae2d22ae1091ed8a89479a895a58ee4c4bb49a4b (log l.348) SHA-256 R12_singularity_add.csv            : 2fc012cd0508cc71ae1ad7da64590478984b28a81ea6aad6af26225577aa005b (log l.349) SHA-256 R12_concept_crn_witness.csv        : 6630674065604db80a313114daf8b1f266c144fd7b5829c7ab35f9f6a6804a8f (log l.350) SHA-256 R12_diagnostics.csv                : f6f994a73e1a4421e66352bebad7ba07ce2b74d0dcdc3b2c23b4733839884b60 (log l.351) SHA-256 fig12_leverage.png                 : a5f4100ce0b7c413460925884f132cd1878f89540388ada522f36effdb7170bd (log l.352) SHA-256 fig13_fat_tails.png                : 5fa39b4ccac47bfb421840ae907153b5eba970565b897b8912d884f7062cff83 (log l.353) SHA-256 R12_claims.tex                     : 47df982b6543ff1a38298b5edb71a3562181259feef0a269f85db5ef2018f569 (log l.354)

current tree, single run: SHA-256 R12_concept_crn_witness.csv        : 6630674065604db80a313114daf8b1f266c144fd7b5829c7ab35f9f6a6804a8f SHA-256 R12_diagnostics.csv                : f6f994a73e1a4421e66352bebad7ba07ce2b74d0dcdc3b2c23b4733839884b60 SHA-256 R12_leverage_fpr.csv               : 8a0326eff4444d99b4769781ae2d22ae1091ed8a89479a895a58ee4c4bb49a4b SHA-256 R12_singularity_add.csv            : 2fc012cd0508cc71ae1ad7da64590478984b28a81ea6aad6af26225577aa005b SHA-256 R12_claims.tex                     : 47df982b6543ff1a38298b5edb71a3562181259feef0a269f85db5ef2018f569

## 5. Design decisions taken outside the plan

1. Experiment A carries TWO Concept arms instead of one: a CRN arm keyed ('R12', 'expA', s) that is bit-identical across all 15 gamma_lev by construction, and a published arm keyed ('R12', 'expA_concept_indep', gamma_index, s) that breaks the pairing. Publishing 'leverage-invariant' on the CRN arm would make v87's sentence true MECHANICALLY, so the CRN arm is kept as an identity witness with its degeneracy asserted (C8) and the published arm pays an index into its key (log l.13).

2. The variance-targeted design: omega = 0.04 * (1 - alpha_sym - beta) at every grid point, so sigma2_unc = 0.04 on all fifteen, isolating dynamic misspecification from level error (log l.120).

3. Experiment B Data threshold: compute_gamma_exact(0.05, 0.85) = 2.22077922077922, so the Data CUSUM runs at lambda_iid * Gamma = 65.0 * 2.2208 = 144.3506493506493. The Concept CUSUM runs at lambda_c = 10.0 with NO penalty multiplier, which is the asymmetry Figure 13 exists to show (log l.124).

4. Experiment B drift: sigma_unc = sqrt(omega / (1 - alpha - beta)) = 0.2 and Delta = c * sigma_unc = 0.2 at c = 1.0. The Data statistic monitors (eps + Delta)^2, whose mean shift is Delta^2 = 0.04000000000000001 against a warm-up standard deviation of the squared residual that DIVERGES as nu -> 4: that ratio is the whole content of the 'stochastic syncope' (log l.125).

5. C9 uses a SLOPE test instead of a RANGE test: v87 prints '7.6--8.4%' and calls the rate 'leverage-invariant'. A max minus a min over 15 noisy estimates is an extremum statistic with no stable sampling distribution; the slope has a null, and it is the only inferential gate of this stream (log l.255).

6. The submitted figure censors on det_rate_data >= 0.5, and the witness adds `ADD_Data_Raw` and `SEM_Data_Raw` on ALL streams because v87 L353 explicitly publishes the censored domain (log l.133).

## 6. Open questions, left open

1. v87 L349 calls alpha_sym the symmetric GARCH(1,1) 'population limit'. Mean-matching is what this stream derives; a 'population limit' in the QMLE sense is the Gaussian pseudo-true parameter of Bollerslev & Wooldridge (1992), the minimiser of the expected quasi-log-likelihood. The two need not coincide, and NO measurement in this stream decides which one alpha_sym is: the witness never fits anything, it substitutes alpha + gamma_lev/2 in closed form (log l.121).
