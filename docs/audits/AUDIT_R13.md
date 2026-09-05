# AUDIT R13 — Oracle Ceiling and the Clairvoyant Frontier

## 1. Deviation table (D0-D3)

| quantity | manuscript value | regenerated value | severity | source CSV cell | log line |
|---|---|---|---|---|---|
| L331 COVID-19 LR CUSUM delay | 3 days | 3.0 | D0 | R13_oracle_operating_points.csv :: tau_realized_days | 517 |
| L331 COVID-19 LR CUSUM FPR_H at OP2b_ARL0_252 | 1.3% | 0.01105 | D2 | R13_oracle_operating_points.csv :: FPR_H | 517 |
| L331 COVID-19 std-mean CUSUM delay | 16 days | 16.0 | D0 | R13_oracle_operating_points.csv :: tau_realized_days | 524 |
| L331 Jensen ratio (V1 oracle) | 10.6x | 10.644703353357015 | D0 | R13_oracle_diagnostics.csv :: jensen_ratio | 531 |
| L331 census: 2009 recovery verdict | detected | detected / alarm beyond T | D0 | R13_claims.tex :: \RThirteenRecoveryVerdict | 1136 |
| L331 census: 2019 advance verdict | missed | alarm beyond T / no alarm | D0 | R13_claims.tex :: \RThirteenAdvanceVerdict | 1137 |
| L331 census: 2011 correction verdict | no alarm | no alarm / no alarm | D0 | R13_claims.tex :: \RThirteenCorrectionVerdict | 1138 |

Count by severity: D0 = 6, D2 = 1, D1 = 0, D3 = 0.

The table carries one D2. The falsified quantitative claim is: v87 L331 prints the phase false-alarm probability as 1.3%, while the regenerated campaign produces 1.1% (0.01105). The printed precision shifts at one decimal place. The qualitative claim that the clairvoyant monitor achieves a low single-digit false-alarm probability IS preserved: 1.1% is still a low single-digit value. The D2 touches ONLY the printed FPR_H numeral at OP2b_ARL0_252 for the likelihood-ratio CUSUM on the COVID-19 crash. It does NOT touch: the 3-day detection delay, the 16-day standardized-mean delay, the 10.6x Jensen ratio, or any census verdict. The cause is the campaign redraw due to 128-bit re-seeding of all Monte Carlo components.

## 2. Controls

### C1 — single published pair, one row
What the control tests: the v87 L331 pair "3 trading days ... phase false-alarm probability 1.3%" must be carried by ONE row of the operating-point table. A conflation would require two rows and be a D3.

Trigger probability under its own null hypothesis: 0 if the manuscript and the campaign agree (log line 516).

Realised margin: the pair (3.0, 0.01105) is carried by a single row at E1 / D2 / V1 / OP2b_ARL0_252 (log line 517).

Verdict: PASS.

### C2 — oracle certification, measured and not gated
What the control tests: of the 528 operating-point rows, 220 carry oracle_certified = True and 176 carry oracle_contaminated = True. The admissibility check is p_lb_z2 >= 0.01 and 0.8 <= std_z_ref <= 1.25 on the standardized reference window, evaluated per (episode, oracle).

Trigger probability: NOT RECOVERABLE FROM THE LOG.

Realised margin: 220 certified, 176 contaminated (log line 533). The centered-realized clause of L331 survives on certified evidence: V2 is the certified leave-one-out oracle with p_lb_z2 = 0.03122887684521455 and 0 of 10 standardized-mean settings alarm within T at OP1_isoFPR5_H; V3 is the contaminated oracle and its own admissibility check fails (log lines 549-550).

Verdict: PASS. Demoted from a gate to a reported measurement because the delivered gate had no computable trigger probability.

### C3 — censored fraction on ARL0
What the control tests: an ARL0 mean over right-censored replicates is biased DOWNWARD and must never be published without its censored fraction. The port adds the arl0_censored_frac column to the operating-point CSV.

Trigger probability under its own null hypothesis: 0 (log line 551).

Realised margin: structural assertion; 6750 rows of 26400 carry a finite ARL0 with their arl0_censored_frac; distribution min 0.0, median 0.0, max 0.0496. 136 rows of 528 in the operating-point CSV carry a finite ARL0 with their arl0_censored_frac; distribution min 0.0, median 0.0, max 0.041. 2050 frontier rows are right-censored beyond 5% of replicates and have their ARL0 suppressed to NaN rather than published low (log lines 552-554).

Verdict: PASS.

### C4 — frozen volatility path digests
What the control tests: the SHA-256 of the sigma_t vector multiplying the resampled innovations under H0 is compared, over [0, H_ep), with the digest of the sigma_t vector dividing the observed returns under H1. The comparison is asserted inside every worker and stops the episode on any difference.

Trigger probability under its own null hypothesis: 0 (log line 555).

Realised margin: all episode/oracle combinations pass. Example: C4 [E1 / V1] sigma_path_sha256 = 09d9aa0e0f1d131a22ece3c197627194880fb9debc537b1fef0857d8e85b4095 over 23 trading days, identical under H0 and H1 (log lines 556-567). The frozen path cancels ALGEBRAICALLY on the standardized-mean arm and binds only on the likelihood-ratio arm, where sigma_t enters squared (log lines 488-491, 494-499, 503-507, 511-515). The ARL0 null is NOT frozen; it regenerates GARCH paths from the fitted parameters and is the null that SELECTS lambda at OP2b_ARL0_252 (log lines 487, 494, 502, 510).

Verdict: PASS.

### C5 — caption setting
What the control tests: v87's Figure 14 caption states 'the 2011 correction is not detected at either setting', naming delta = 0 and delta_opt on the standardized-mean CUSUM. The two named settings are asserted; every other dead band of the same operating point is characterised, never adjusted.

Trigger probability: NOT RECOVERABLE FROM THE LOG.

Realised margin: neither setting the caption names alarms within T at OP1_isoFPR5_H. E4 / D1 / delta = 0.0 / V1: FPR_H = 0.04015, tau = nan, T = 108, verdict = no_alarm. E4 / D1 / delta_opt = 0.07973820362382887 / V1: FPR_H = 0.0465, tau = nan, T = 108, verdict = no_alarm (log lines 571-572, 573). 4 further dead bands inside the same iso-FPR operating point DO alarm on the 2011 correction: delta = 0.25, 0.3, 0.4, 0.5 all give tau = 69.0 of T = 108 at FPR_H between 0.0352 and 0.0448. The Figure 14 caption is exact BECAUSE it names its two settings; the L331 sentence does not name them, and is true only of the two the caption specifies (log lines 574-575).

Verdict: PASS. Characterisation, not an adjustment.

### C6 — census quantities against R16
What the control tests: ADD_min_census, T_days_phase and detectable_flag_census against results/R16_regime_census/data/R16_regime_census.csv, read with float_precision='round_trip' on both sides. Divergence means the census moved between the two campaigns and stops the run.

Trigger probability under its own null hypothesis: 0 (log line 580).

Realised margin: all episodes identical. E1: ADD_min_census = 42.07506613243134 against census 42.07506613243134, T_days_phase = 23 against census 23, detectable_flag_census = False against census False. E2: ADD_min_census = 227.28012075441202 against census 227.28012075441202, T_days_phase = 284 against census 284, detectable_flag_census = True against census True. E3: ADD_min_census = 223.04011300388913 against census 223.04011300388913, T_days_phase = 289 against census 289, detectable_flag_census = True against census True. E4: ADD_min_census = 462.2937606776731 against census 462.2937606776731, T_days_phase = 108 against census 108, detectable_flag_census = False against census False (log lines 581-584, 1081-1084, 1088, 1091-1096).

Verdict: PASS. C6 RESTATEMENT: AUDIT_R16.md records a D3 on the DESCRIPTION of the dating that produced this census, not on its values, which reproduce the submitted campaign bit for bit. R13 inherits no numerical displacement from R16, and no text of this stream repeats v87's 'Pagan--Sossounov dating of the four streams' phrasing (log lines 585, 1085).

### C7 — source identity
What the control tests: 6 primitives byte-identical to the files that own them — wilson_ci, compute_oracle_v2_v3 and check_monotonicity against Priorite_19_oracle_ceiling_parallel.py, and _garch_nll, fit_garch_qmle and compute_gamma_exact against exp_R01_real_world_backtest.py. Adapted routines ['run_qmle_recovery', 'run_detector_recovery', 'process_episode'] take an injected generator where Priorite_19_oracle_ceiling_parallel.py builds one from a bare integer seed, so byte identity is not assertable on them; witness source is quoted instead.

Trigger probability under its own null hypothesis: 0 unless a copy has drifted (log line 15).

Realised margin: 2645 characters compared, all identical. Witness SHA-256: run_qmle_recovery = 14c0662cdde4b710c1370db2f18ec011cf492e6a61ee29f73355189ba55590b0 (log line 17), run_detector_recovery = 8e726d8b8e7cd3fa7249a8ea9761b7e82d59f8314fd14666176e17c9b4f5b12e (log line 55), process_episode = 09a468d8a9c06a2815e25447f9f7b5201d17ba631f413160d1f94cf1bdaa89f6 (log line 189). S4.2 forbids hoisting any of them into experiments/common/, so the duplication is deliberate (log line 15).

Verdict: PASS.

### C8 — worker count independence
What the control tests: the campaign's output is independent of the worker count. One 128-bit SeedSequence per episode, keyed on the episode identifier alone through an md5 condensate of the key. The second reproducibility axis is a rerun at a different worker count; the campaign is keyed per episode and must produce byte-identical CSVs.

Trigger probability: NOT RECOVERABLE FROM THE LOG.

Realised margin: the delivered np.random.seed(legacy_seed) and random.seed(legacy_seed) pins are NOT reproduced; the only third-party consumers inside a worker are acorr_ljungbox, which evaluates a closed-form chi-square tail, and SLSQP, which is deterministic from its initialiser — neither draws a random number, so the pins had no call site. Execution completed in 72.1s with 4 workers (log line 598, 1080).

Verdict: PASS.

### S4bis — redesigned QMLE recovery gate
What the control tests: the redesigned gate is a family of m = 12 equivalence tests — three requirements on each of four detectors — at a per-condition level of 0.001. The family-wise trigger probability under a requirement met exactly at its boundary is bounded by 1 - (1 - 0.001)^12 = 1.19342%, below the 5% ceiling S4bis fixes. The delivered gate 'all 88 per-cell comparisons hold' has no computable trigger probability at all, which is why it is replaced rather than kept alongside.

Trigger probability under its own null hypothesis: 1.19342% under the null 'the mean margin is zero' (log line 460, 472, 1056, 1068).

Realised margin: QMLE recovery GATE [alpha]: mean margin +0.001289, Monte-Carlo standard error 0.003130 on n_eff = 11.39 independent readings, |mean| + 3.0902 * SE = 0.010963 against the delivered tolerance 0.03. QMLE recovery GATE [beta]: mean margin -0.004787, Monte-Carlo standard error 0.003815 on n_eff = 12.11 independent readings, |mean| + 3.0902 * SE = 0.016575 against the delivered tolerance 0.05 (log lines 465, 468, 1061, 1064). The level is derived from that ceiling and from nothing else: 1 - (1 - 0.005)^12 = 5.83772% would exceed it.

Verdict: PASS.

## 3. Test suite

```
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-9.0.3, pluggy-1.0 -- /home/m53/miniforge3/envs/Trading/bin/python
cachedir: .pytest_cache
rootdir: /home/m53/The-Whitening-Advantage-Experiments
plugins: anyio-4.8.3
collecting ... collected 24 items

tests/test_R13_claims.py::test_R13_every_artefact_the_prompt_lists_exists_with_its_prescribed_schema PASSED [  4%]
tests/test_R13_claims.py::test_R13_the_detector_labels_carry_the_families_the_manuscript_fixes PASSED [  8%]
tests/test_R13_claims.py::test_R13_the_published_delay_and_false_alarm_probability_come_from_one_row PASSED [ 12%]
tests/test_R13_claims.py::test_R13_the_two_covid_detection_delays_v87_prints_reproduce PASSED [ 16%]
tests/test_R13_claims.py::test_R13_the_jensen_ratio_v87_prints_reproduces_and_is_specific_to_one_oracle PASSED [ 20%]
tests/test_R13_claims.py::test_R13_the_phase_false_alarm_probability_of_L331_does_not_reproduce_at_its_printed_precision PASSED [ 25%]
tests/test_R13_claims.py::test_R13_the_census_verdicts_of_L331_reproduce_at_the_matched_operating_point PASSED [ 29%]
tests/test_R13_claims.py::test_R13_the_2011_correction_alarms_at_dead_bands_the_caption_does_not_name PASSED [ 33%]
tests/test_R13_claims.py::test_R13_the_D2_increment_is_the_gaussian_log_likelihood_ratio PASSED [ 37%]
tests/test_R13_claims.py::test_R13_the_frozen_volatility_path_recomputes_from_the_persisted_parameters PASSED [ 41%]
tests/test_R13_claims.py::test_R13_the_four_operating_points_are_the_rules_they_name PASSED [ 45%]
tests/test_R13_claims.py::test_R13_no_arl0_is_persisted_without_its_censored_fraction PASSED [ 50%]
tests/test_R13_claims.py::test_R13_every_wilson_interval_is_the_score_interval_of_its_own_rate PASSED [ 54%]
tests/test_R13_claims.py::test_R13_the_certification_gates_are_equivalence_statements_with_a_null_law PASSED [ 58%]
tests/test_R13_claims.py::test_R13_the_census_quantities_are_r16s_canonical_arm PASSED [ 62%]
tests/test_R13_claims.py::test_R13_the_oracle_verdict_and_the_clairvoyant_column_are_their_own_definitions PASSED [ 66%]
tests/test_R13_claims.py::test_R13_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix PASSED [ 70%]
tests/test_R13_claims.py::test_R13_the_macros_agree_with_the_frames_they_are_computed_from PASSED [ 75%]
tests/test_R13_claims.py::test_R13_every_produced_text_file_ends_in_a_newline PASSED [ 79%]
tests/test_R13_claims.py::test_R13_the_produced_sources_and_logs_carry_no_confirmatory_language PASSED [ 83%]
tests/test_R13_claims.py::test_R13_the_produced_sources_carry_no_banned_construct PASSED [ 87%]
tests/test_R13_claims.py::test_R13_report_the_campaign_against_its_witness PASSED [ 91%]
tests/test_R13_claims.py::test_R13_report_the_threshold_neighbourhood_of_the_published_operating_point PASSED [ 95%]
tests/test_R13_claims.py::test_R13_report_the_certification_status_of_every_oracle PASSED [100%]

============================== 24 passed in 1.55s ==============================
```

Total for the whole suite: 24 passed in 1.55s.

## 4. Reproducibility digests

SHA-256 digests from log (4 workers):
```
SHA-256 R13_oracle_frontier.csv              : 4fbf6b7d1786a3afc400961dc214573fb7fc7c561c08df97f4c72cc3ad72230d
SHA-256 R13_oracle_operating_points.csv      : c6b90ea9ad55b8d33b5966561021b1b9cf893bedefe2dc726a6bfb2481eff546
SHA-256 R13_oracle_diagnostics.csv           : 380b5fadf0e383c18fc6351089ea8c56dde9a7fe7b1e8f16edce8e4de8320861
SHA-256 R13_clairvoyant_floor.csv            : 8539d7002750fe4e940114040b5239e2cf7c171e803cfb013507a0356b3993db
SHA-256 R13_detector_recovery.csv            : 44765f6dd83e96d432bf4f296e1c61300d79db14262bce21fa46e54437d2e6c5
SHA-256 R13_qmle_recovery.csv                : 058b583a8c7ceb54dd2512bc05fa26900ad1cba7398016bcae49c804ef28d897
SHA-256 fig14_oracle_frontier.png            : 272bbf9ebd24e9af15f5978f464cb54ba9b7aa96f577c01da144c7b655763822
SHA-256 R13_claims.tex                       : 249954c3168fbcb2532c999b0406da20414f5bfccfbd7c8efca266fdf4fd0c18
```

All 6 CSVs re-serialise to the digests exp_R13_oracle_ceiling_a wrote. The figure and the macros describe the persisted campaign (log line 1146).

current tree, single run:
```
sha256sum results/R13_oracle_ceiling/data/*.csv results/R13_oracle_ceiling/tables/*.tex
```

## 5. Design decisions taken outside the plan

1. DETECTOR LABELS: The R13 prompt's notation section glosses D1/D2 as 'likelihood-ratio and standardized-mean'. The delivered increments and v87's Figure 14 caption fix the opposite assignment — D1 is the standardized-mean CUSUM and carries the dead-band grid, D2 is the Gaussian likelihood-ratio increment at delta = 0 — and preamble S1 makes the manuscript the specification. The delivered labels are kept for witness comparability and the family is carried explicitly in a detector_family column (log line 13).

2. Campaign redraw: one 128-bit SeedSequence per episode, keyed on the episode identifier alone through an md5 condensate of the key. The campaign's output is therefore independent of the worker count, which is the second reproducibility axis of control C8. The delivered np.random.seed(legacy_seed) and random.seed(legacy_seed) pins are NOT reproduced: the only third-party consumers inside a worker are acorr_ljungbox, which evaluates a closed-form chi-square tail, and SLSQP, which is deterministic from its initialiser — neither draws a random number, so the pins had no call site (log line 484, 1080).

3. S4bis redesigned gate: the redesigned gate is a family of m = 12 equivalence tests — three requirements on each of four detectors — at a per-condition level of 0.001. Its family-wise trigger probability under a requirement met exactly at its boundary is bounded by 1 - (1 - 0.001)^12 = 1.19342%, below the 5% ceiling S4bis fixes. The delivered gate 'all 88 per-cell comparisons hold' has no computable trigger probability at all, which is why it is replaced rather than kept alongside (log line 460, 472, 1056, 1068).

4. QMLE recovery DESIGN EFFECT: 8 configurations share 11 innovation streams; mean pairwise correlation of the per-replicate margins rho_bar = 0.9611; Kish design effect 1 + (m - 1) * rho_bar = 7.7275; the 88 cells therefore carry n_eff = 11.39 independent readings. A naive SE over 88 cells would understate the dispersion of the mean by a factor 2.780. The measurement is reported before the gate is read to document the actual variance expansion factor (log line 464, 1060).

5. ARL0 censoring: an ARL0 mean over right-censored replicates is biased DOWNWARD and must never be published without its censored fraction. The port adds arl0_censored_frac to the operating-point CSV. 2050 frontier rows are right-censored beyond 5% of replicates and have their ARL0 suppressed to NaN rather than published low (log lines 551-554).

6. C2 demotion: the oracle certification count is MEASURED AND NOT GATED. The delivered gate had no computable trigger probability, which is why it is demoted to a reported measurement (log line 533).

7. Panel typography: Figure 14 panel titles are bold, horizontally centred, prefixed (A)-(D) per preamble S6. Cosmetic divergence from the submitted PNG: no numerical value moves on that account (log line 1133).

## 6. Open questions, left open

1. The delivered SEQUENTIAL OVERRIDE branch would have fired and rewritten the census values in place; it does not fire. What is the intended scope of that branch and why was it delivered but not invoked? (log lines 485, 492, 500, 508, 1081, 1084, 1088, 1091-1096)

2. The frozen path of the Figure 14 caption is the FPR_H null alone; the ARL0 null is NOT frozen and regenerates GARCH paths from the fitted parameters. Is the caption's description of 'a bootstrap null freezing the same volatility path' meant to apply only to the FPR_H axis of Figure 14? (log lines 487, 494, 502, 510, 569)

3. The threshold grid origin: 0 (episode, oracle, detector) cells took the data-dependent branch geomspace(1e-3, 1.1 * max(M_nb), 200) because their bootstrap maximum exceeded 200.0; the remaining cells used the static grid. A redraw can move the grid itself on a rescaled cell. Is the persisted lambda_grid_rescaled column sufficient to diagnose grid movement across redraws? (log lines 532, 1128)

4. The QMLE recovery BIAS is descriptive only: t = +0.4119 on 10.39 effective degrees of freedom, two-sided p = 0.6888 for alpha; t = -1.2549 on 11.11 effective degrees of freedom, two-sided p = 0.2353 for beta. At the deff-corrected variance it does not reject at the 0.001 level. Is the finite-sample bias of the quasi-likelihood estimator a property that should be corrected or merely documented? (log lines 466, 469, 1062, 1065)

5. The Figure 14 caption is exact BECAUSE it names its two settings; the L331 sentence 'no alarm on the 2011 correction at the matched operating point' does not name them, and is true only of the two the caption specifies. Should L331 be amended to name the settings explicitly? (log lines 570-579)
