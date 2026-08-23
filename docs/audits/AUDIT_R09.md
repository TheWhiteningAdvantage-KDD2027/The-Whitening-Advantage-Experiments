# Audit Report: R09 Anytime-Valid Detection on the Fair-Coin Stream

## 1. Deviation table (D0-D3)

| quantity | manuscript value | regenerated value | severity | source CSV cell | log line |
|---|---|---|---|---|---|
| L243 / Fig. 9(A) CUSUM peeking FPR | 18% | 20% | D2 | R09_validity_stopping.csv :: CUSUM / 0.05 / peeking / FPR | 429 |
| L243 CUSUM calibrated to 5% at H | 5% | 5% | D1 | R09_level_granularity.csv :: CUSUM / 0.05 / achieved_level | 431 |
| L243 MIX ADD at eta = 0.10 | 409 | 410 | D2 | R09_eprocess_race.csv :: MIX / 0.05 / 0.10 / ADD | 433 |
| L243 CUSUM ADD at eta = 0.10 | 539 | 533 | D2 | R09_eprocess_race.csv :: CUSUM / 0.05 / 0.10 / ADD | 435 |
| L243/L559 fair-coin streams per level | 2\*10^4 | 20000 | D0 | N_NULL, the H0 arm of panels A and C | 437 |

Count by severity: D0: 1, D1: 1, D2: 3.

The table contains no D3 row.

Qualitative checks against v87, at printed precision:
- QUALITATIVE L243/L559 MIX 'remains bounded by alpha' under peeking: 7 of 7 levels at or below alpha; ratios 0.948, 0.966, 0.982, 0.970, 0.962, 1.000, 0.945 -> holds (log line 439)
- QUALITATIVE L559 'e-CUSUM satisfies ARL0 >= 1/alpha': 7 of 7 rows; minimum ratio 20.54 at alpha = 0.1 -> holds (log line 440)
- QUALITATIVE L559 'Only MIX controls the time-uniform false-alarm probability': CUSUM peeking exceeds MIX peeking at 7 of 7 levels; e-CUSUM peeking at alpha = 0.05 is 1.0000 -> holds (log line 441)
- QUALITATIVE L559 'MIX matches CUSUM speed for moderate drifts (eta <= 0.10)': MIX at or below CUSUM at eta [0.06, 0.08, 0.1] of the five grid points at or below 0.10; the marginal ADD is conditional on detection and the matched-rate reading is control C4's -> see C4 (log line 442)

## 2. Controls

### C1 -- CENSORING IS INSEPARABLE FROM EVERY ARL0
What the control tests: No ARL0_mean is written to any frame, plotted, or passed to the macro emitter without censored_frac on the same row.

Asserted on the frame schema and on the emitter's input. Deterministic; trigger probability 0.

Verdict: All 21 rows of the ARL0 frame carry a finite ARL0_mean with its censored_frac on the same row. Censoring by arm: CUSUM 0.6510-0.9554; MIX 0.9052-0.9906; eCUSUM 0.0000-0.0006. Passed (log line 328).

### C2 -- arl0_bound_respected IS COMPUTED, NOT A LITERAL
What the control tests: The flag is a computed comparison arl0 >= 1.0 / a, located in this file's own AST: a single >= whose right-hand side is 1.0 / a. It is NEITHER a definitional tautology NOR a literal -- it is a computed comparison that is ARITHMETICALLY NECESSARY for the censored arms.

Asserted on this file's own AST and, independently, in tests/test_R09_claims.py. Deterministic; trigger probability 0.

Verdict: THE FLAG CARRIES INFORMATION ON 7 OF 21 ROWS, and they are all on the ['eCUSUM'] arm(s). On every other row censored_frac * T_EXT already exceeds 1/alpha, so arl0_bound_respected could not have been False whatever the campaign measured (log line 329).

Per-row detail logged at lines 330-350.

### C3 -- THE MARTINGALE BOUND, AS ONE STATISTIC WITH AN EXACT NULL
What the control tests: Seven binary gates at 5% would ring on a compliant campaign with probability 1 - 0.95^7 = 0.3017; worse, the submitted MIX peeking rate sits at 0.94-0.99 of alpha, so at alpha = 0.05 the margin to the bound is 0.00055 against a binomial SE of 0.00154 -- 0.36 sigma, a ~36% chance of a spurious exceedance at that level alone. A KS test of seven p-values against Uniform(0,1) is the wrong instrument too: under Ville the p-values are STOCHASTICALLY LARGE by construction, so a two-sided uniformity test would reject precisely because the bound is conservative.

Derivation, one line as S4.6 requires: each mixture component is a non-negative martingale with E_0 = 1 (a component not yet started holds value 1), a convex combination of martingales is a martingale, and Ville's inequality on a non-negative martingale gives P(sup_t E_t >= c) <= E_0 / c = 1/c.

Design: let Z = sup_(1<=t<=T_EXT) E_t per H0 stream and U = min(1, 1/Z). Ville gives P(Z >= 1/alpha) <= alpha for EVERY alpha, i.e. F_U(alpha) <= alpha over the whole range. Tested with the ONE-SIDED Kolmogorov statistic D+ = sup_alpha (F_n(alpha) - alpha) on n = 20000, exact null scipy.stats.ksone.sf(D+, n) at the least-favourable boundary F_U = Id.

Gate at 0.01; trigger probability under its own null is EXACTLY 0.01, and strictly below it because the true F_U is bounded away from the identity and U has atoms.

C3 [MIX, H0 campaign] D+ = 0.00024248795043670026 on n = 20000, exact one-sided p = 0.9974895113826439 against the least-favourable boundary F_U = Id. Gate at 0.01; verdict = no rejection. U = min(1, 1/sup_t E_t) has an atom at 1 of mass 0.0046 -- streams whose mixture never exceeds 1 -- which sits above every alpha and cannot inflate D+ (log line 352).

C3 [MIX, M1(ii) independent replicate on a disjoint key] D+ = 0.0007543091674924681, exact one-sided p = 0.9770065602005356. Both replicates are reported; neither is averaged into the other (log line 353).

Trigger probability: EXACTLY 0.01.

C3 DESCRIPTIVE [MIX peeking alpha=0.1] FPR = 0.0948, FPR/alpha = 0.9480, exact one-sided binomial p = 0.9934201987948659. Persisted in R09_validity_stopping.csv; NOT an acceptance criterion (S4bis point 3) (log line 354).

Similar descriptive entries for alpha=0.07, 0.05, 0.035, 0.025, 0.015, 0.01 at lines 355-360.

C3 NEGATIVE CONTROL [CUSUM] D+ = 0.4775 on n = 20000, nominal exact one-sided p = 0.0. The statistic must reject decisively, and it is what establishes the instrument has power against the alternative it is used on. Two caveats travel with it and neither is repaired: U_cusum is read off an ESTIMATED survival function on N_CAL = 50000 draws, which carries the double variance of S4bis's second corollary, and the CUSUM statistic lives on a lattice so U_cusum has heavy ties, under which the ksone tail is not exact. The effect size dwarfs both; this direction is a control on power, not an acceptance gate (log line 368).

### C3 CALIBRATION COHERENCE (replacing delivered controls b and e)
The delivered gates 0.046 <= FPR <= 0.055 and |FPR_M2 - calib| <= 3 sqrt(alpha(1-alpha)/N_NULL) both ignore that lambda_star is ITSELF ESTIMATED on N_CAL = 50000 streams (S4bis, second corollary). The correct variance of the difference is alpha(1-alpha)(1/N_NULL + 1/N_CAL) = 3.325e-06 at alpha = 0.05, i.e. an SE of 0.001823 against the delivered 0.001541. The tolerance is z(1 - 0.001/2) times that SE and is derived from the mechanism, never from an observed gap; its trigger probability under its own null is 0.001.

At alpha = 0.05: lambda_star = 11.200000000000031, calibration level on N_CAL = 0.05034, H0 level over [1, H] on N_NULL = 0.05345, gap = 0.003110 against a tolerance of 0.006000 = 3.2905 x 0.001823. The SE carries the variance of the estimated threshold; the delivered (e) used 0.001541 and understated it by a factor 1.1832. Gap in SE units: 1.706 (log line 351).

Trigger probability under its own null: 0.001.

### C4 -- THE POSITIVE CONTROL, PER ARM, WITH AN AGGREGATE RATHER THAN NINE GATES
What the control tests: Nine adjacent-pair comparisons per arm would ring with probability 1 - (1 - p)^9 = 0.0865 at p = 0.01, and strict adjacent monotonicity is unusable anyway: in the submitted campaign the CUSUM pair eta = 0.02 -> 0.04 moves 1244.36 -> 1234.90, a difference of -9.5 against a difference SE of order 77, which inverts roughly half the time. INSTEAD, per arm: a Spearman rank correlation of ADD against eta over the 10 grid points, ONE-SIDED, with its EXACT permutation null (3628800 permutations, enumerated in full).

Gate at 0.01 on each of the arms; rho, the exact p-value, the nine pairwise z-margins and a weighted least-squares slope are reported descriptively. The same test runs on detection rate against eta, one-sided increasing, and is reported without gating.

The confounder is named, not buried: ADD is conditional on (fa > TAU) & (fa <= H), and detection rates run from about 0.057 to 0.98 across the grid, so at small eta a slower arm that detects MORE streams necessarily averages over slower ones. THE PRIMARY INSTRUMENT IS A MATCHED-DETECTION-RATE QUANTILE, not the common-detection subset: the intersection of two detection events whose rates differ by a factor of 2.8 is dominated by the streams both arms find easy, its composition depends on both detectors, and it is therefore itself a selected sample that cannot carry a D3 (log line 281). At each eta, q = min(p_CUSUM, p_MIX) and the q-quantile of each arm's alarm-time distribution is compared with non-detections placed at +inf. This asks 'to reach the same detection rate, which arm needs fewer steps', is well defined for every q <= min(p), conditions on nothing, and is the same iso-rate comparison the paper's own iso-FPR race uses. Reported with a paired bootstrap interval over the 2000 trajectory indices, 2000 replicates at the 5% level. The common-detection paired difference is computed and reported BESIDE it as a second reading and gates nothing.

DECISION RULE, FIXED BEFORE THE FIRST NUMBER: (1) If MIX's matched-rate quantile is at or below CUSUM's at eta in (0.02, 0.04), the marginal ADD reversal is an artefact of conditioning on detection; L243's 'ceding ground only for abrupt shifts' and the caption's 'matches ... for eta <= 0.10' stand, and the caveat is a Class A entry with no severity. (2) If MIX's matched-rate quantile is strictly above CUSUM's with the paired bootstrap interval excluding zero, a printed qualitative claim is contradicted: D3, full stop, full report, no parameter moved (log line 282).

Exact permutation null materialised: 3628800 permutations of 10 grid points (log line 369).

C4 [CUSUM, alpha=0.05] ADD vs eta: Spearman rho = -0.9999999999999999, exact one-sided p (decreasing) = 2.755731922398589e-07 over 3628800 permutations, 0 tied ADD values. Gate at 0.01: monotone decrease (log line 370).

C4 [MIX, alpha=0.05] ADD vs eta: Spearman rho = -0.9999999999999999, exact one-sided p (decreasing) = 2.755731922398589e-07 over 3628800 permutations, 0 tied ADD values. Gate at 0.01: monotone decrease (log line 373).

C4 [eCUSUM, alpha=0.05] ADD vs eta: Spearman rho = -0.9999999999999999, exact one-sided p (decreasing) = 2.755731922398589e-07 over 3628800 permutations, 0 tied ADD values. Gate at 0.01: monotone decrease (log line 376).

C4 HALT CONDITION NOT MET. At eta in (0.02, 0.04) the matched-rate quantile does not place MIX strictly above CUSUM with an interval excluding zero, so a marginal ADD reversal at those points is an artefact of conditioning on detection and is recorded under R09-add-conditioning with no severity (log line 399).

Matched-rate quantile results logged at lines 379-398.

Trigger probability: EXACTLY 0.01.

### C4 DELIVERED CONTROL (d) [reported, not gated]
CUSUM peeking FPR 0.34905 vs MIX 0.0948; PAIRED difference 0.25425 on the same 20000 streams, paired SE 0.0037121889600342274, z = 68.49. v87's panel A prints 'Only MIX controls the time-uniform false-alarm probability'; an inversion here would falsify it and would be a D3 (log line 401).

CUSUM peeking FPR 0.2585 vs MIX 0.06765; PAIRED difference 0.19085 on the same 20000 streams, paired SE 0.0033513152455416665, z = 56.95. v87's panel A prints 'Only MIX controls the time-uniform false-alarm probability'; an inversion here would falsify it and would be a D3 (log line 402).

CUSUM peeking FPR 0.1988 vs MIX 0.0491; PAIRED difference 0.1497 on the same 20000 streams, paired SE 0.0030181940792467278, z = 49.60. v87's panel A prints 'Only MIX controls the time-uniform false-alarm probability'; an inversion here would falsify it and would be a D3 (log line 403).

CUSUM peeking FPR 0.1482 vs MIX 0.03395; PAIRED difference 0.11425 on the same 20000 streams, paired SE 0.002672049190228354, z = 42.76. v87's panel A prints 'Only MIX controls the time-uniform false-alarm probability'; an inversion here would falsify it and would be a D3 (log line 404).

CUSUM peeking FPR 0.1051 vs MIX 0.02405; PAIRED difference 0.08105 on the same 20000 streams, paired SE 0.0023019654374034377, z = 35.21. v87's panel A prints 'Only MIX controls the time-uniform false-alarm probability'; an inversion here would falsify it and would be a D3 (log line 405).

CUSUM peeking FPR 0.06455 vs MIX 0.015; PAIRED difference 0.04955 on the same 20000 streams, paired SE 0.0018465480971260944, z = 26.83. v87's panel A prints 'Only MIX controls the time-uniform false-alarm probability'; an inversion here would falsify it and would be a D3 (log line 406).

CUSUM peeking FPR 0.04465 vs MIX 0.00945; PAIRED difference 0.0352 on the same 20000 streams, paired SE 0.0015388463211120202, z = 22.87. v87's panel A prints 'Only MIX controls the time-uniform false-alarm probability'; an inversion here would falsify it and would be a D3 (log line 407).

DELIVERED CONTROL (d): the CUSUM peeking rate exceeds the MIX one at all 7 levels; the direction v87's panel A states holds (log line 408).

### C5 -- ast SOURCE IDENTITY
What the control tests: 27 recursion statements extracted from the witness AST and found verbatim in exp_R09_eprocess_anytime.py -- the three CUSUM lines, the four MIX lines, the five e-CUSUM lines, the two mixture log-increments, the four e-CUSUM increment definitions and the calibration quantile.

Deterministic; trigger probability 0 unless a copy has drifted.

C5 (i) CARRIED PRIMITIVES: 1 byte-identical to Priorite_22_eprocess_anytime.py (442 characters compared) -- wilson_ci. Preamble S4.2 forbids hoisting any of them into experiments/common/, so the duplication is deliberate. Deterministic; trigger probability 0 (log line 14).

C5 (ii) ADAPTED ROUTINES: ['_process_m1_chunk', '_process_h0_chunk', 'calibrate_cusum', 'simulate_h1', 'run_m1_certificate'] each take an injected generator keyed on role and index where Priorite_22_eprocess_anytime.py spawns one from a master SeedSequence, and each replaces rng.binomial(1, p, size) by a threshold on a shared uniform, so byte identity is not assertable on them and the witness source of each is quoted in full. This is the treatment exp_R13_oracle_ceiling_a.py gives process_episode. The witness segments total 10047 characters (log line 15).

C5 witness SHA-256 of _process_m1_chunk: 3b238fd994fcdb5182fe5871c8e7991770bfb0338fc5792ce2dd90dd79371636 (log line 16)

C5 witness SHA-256 of _process_h0_chunk: 5f5fdea9f45c86faaaf8a186e5d21de96cd94d73e473e48ef0d6866e8976ecc4 (log line 40)

C5 witness SHA-256 of calibrate_cusum: 742644fd9cc19fae405daffae3b1fcba69c03278ad6f5a264f6dba080b476290 (log line 95)

C5 witness SHA-256 of simulate_h1: ed7917df28fc2c1dbb2b30bba6a97c169b529e0e68d19989e7fb609f15ee0601 (log line 128)

C5 witness SHA-256 of run_m1_certificate: eba0ed5d53aa855cd2a85050dd4ad9c62fd988a4d290b3ee94fe45282358ef9b (log line 206)

C5 (iii) STATEMENT IDENTITY: 27 recursion statements extracted from the witness AST and found verbatim in exp_R09_eprocess_anytime.py (log line 270).

Trigger probability: 0.

### C6 -- REPRODUCIBILITY, THREE AXES
What the control tests: (1) two successive runs, SHA-256 identical on every artefact; (2) --n-jobs 1 against the default, byte-identical, since NUM_CHUNKS = 10 fixes the decomposition; (3) the run WITHOUT --control-arms reproduces the four published CSVs byte for byte, proving the control arm leaks no state into the published path.

Verified outside the process, from the digests this log records (log line 284).

Trigger probability: 0.

### DELIVERED CONTROL (c) [reported, not gated]
e-CUSUM peeking FPR over [1, T_EXT] at alpha = 0.05 is 1.0 (Wilson [0.9998079639438954, 0.9999999999999999]). The delivered floor of 0.80 is derived from nothing and is not carried as a gate; the quantity is what v87's panel A shows for the e-CUSUM bar and it is reported with its interval (log line 400).

Trigger probability: NOT RECOVERABLE FROM THE LOG.

### M1(i) GATE
Gate: |E[lambda_t] - 1| > 0.003 halts the run. Var(lambda_t) = 4 E[eta0^2] = 0.046667 exactly, so the SE over 2e+06 draws is 1.528e-04 and the delivered tolerance is 19.6 standard errors; two-sided trigger probability 7.094e-86. The tolerance is derived, so it is kept; the delivered M1(ii) gate if fpr > a + 0.005 is NOT, and it is removed as a gate and replaced by C3 (log line 286).

M1(i) mean of lambda_t over 2e+06 steps: 0.9997734, displaced from 1 by 1.483 standard errors (analytic SD 0.216025, SE 1.528e-04) (log line 292).

Trigger probability: 7.094e-86.

### STREAM-LEVEL FAMILY-WISE TRIGGER PROBABILITY
Logged once before any result is read: C3 gates at 0.01 on one arm; C4 gates on a one-sided Spearman at 0.01 on each of 3 arms. 4 gates whose nulls are, by construction, exact or conservative, so the probability that at least one fires on a compliant campaign is bounded by 1 - (1 - 0.01)^4 = 3.940399%, below the 5% ceiling S4bis fixes. Including the calibration coherence gate at 0.001 and the M1(i) gate the full stream-level figure is 4.036459%, still below the ceiling. No level is chosen after a result is seen (log line 287-288).

## 3. Test suite

```
tests/test_R09_claims.py::test_R09_every_artefact_the_prompt_lists_exists_with_its_prescribed_schema PASSED [  3%]
tests/test_R09_claims.py::test_R09_every_sample_size_the_campaign_used_is_carried_on_the_row PASSED [  6%]
tests/test_R09_claims.py::test_R09_the_mixture_martingale_remains_bounded_by_alpha_under_continuous_monitoring PASSED [  9%]
tests/test_R09_claims.py::test_R09_only_the_mixture_controls_the_time_uniform_rate PASSED [ 12%]
tests/test_R09_claims.py::test_R09_the_ecusum_arl0_satisfies_the_reciprocal_of_alpha PASSED [ 16%]
tests/test_R09_claims.py::test_R09_the_peeking_horizon_is_four_times_the_calibration_horizon PASSED [ 19%]
tests/test_R09_claims.py::test_R09_every_wilson_interval_is_the_score_interval_of_its_own_rate PASSED [ 22%]
tests/test_R09_claims.py::test_R09_the_mixture_threshold_is_villes_threshold_on_the_mixture_value PASSED [ 25%]
tests/test_R09_claims.py::test_R09_the_cusum_statistic_lives_on_the_two_delta_lattice PASSED [ 29%]
tests/test_R09_claims.py::test_R09_the_one_sided_kolmogorov_statistic_is_the_supremum_it_names PASSED [ 32%]
tests/test_R09_claims.py::test_R09_the_arl0_lower_bound_is_recomputed_from_the_persisted_columns PASSED [ 35%]
tests/test_R09_claims.py::test_R09_no_arl0_is_persisted_without_its_censored_fraction PASSED [ 38%]
tests/test_R09_claims.py::test_R09_the_macro_emitter_refuses_a_censored_arl0 PASSED [ 41%]
tests/test_R09_claims.py::test_R09_the_bound_flag_is_a_computed_comparison_not_a_literal PASSED [ 45%]
tests/test_R09_claims.py::test_R09_the_level_granularity_column_states_the_lattice_it_names PASSED [ 48%]
tests/test_R09_claims.py::test_R09_the_descriptive_binomial_p_values_are_the_exact_one_sided_tail PASSED [ 51%]
tests/test_R09_claims.py::test_R09_the_add_column_is_conditional_and_the_detection_rate_says_so PASSED [ 54%]
tests/test_R09_claims.py::test_R09_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix PASSED [ 58%]
tests/test_R09_claims.py::test_R09_the_macros_agree_with_the_frames_they_are_computed_from PASSED [ 61%]
tests/test_R09_claims.py::test_R09_the_ecusum_censored_fraction_is_not_zero PASSED [ 64%]
tests/test_R09_claims.py::test_R09_every_produced_text_file_ends_in_a_newline PASSED [ 67%]
tests/test_R09_claims.py::test_R09_the_produced_sources_and_logs_carry_no_confirmatory_language PASSED [ 70%]
tests/test_R09_claims.py::test_R09_the_produced_sources_carry_no_banned_construct PASSED [ 74%]
tests/test_R09_claims.py::test_R09_the_orchestrator_passes_the_control_arm_and_never_calls_pytest PASSED [ 77%]
tests/test_R09_claims.py::test_R09_the_shared_orchestrators_are_untouched PASSED [ 80%]
tests/test_R09_claims.py::test_R09_the_three_monte_carlo_numerals_of_L243_does_not_reproduce_at_printed_precision PASSED [ 83%]
tests/test_R09_claims.py::test_R09_the_calibrated_level_and_the_stream_count_still_reproduces_v87s_numerals PASSED [ 87%]
tests/test_R09_claims.py::test_R09_report_the_campaign_against_its_witness PASSED [ 90%]
tests/test_R09_claims.py::test_R09_report_the_published_numerals_at_their_printed_precision PASSED [ 93%]
tests/test_R09_claims.py::test_R09_report_the_censoring_that_makes_panel_c_a_horizon_artefact PASSED [ 96%]
tests/test_R09_claims.py::test_R09_report_the_control_outcomes_the_log_records PASSED [100%]

============================== 31 passed in 0.86s ==============================
```

Total for the whole suite: 31 passed in 0.86s.

## 4. Reproducibility digests

The log carries only one set of SHA-256 digests, pasted below, then run sha256sum produces the current listing beside it, labelled current tree, single run.

SHA-256 digests from log (1 workers, control arm = ecusum):

```
SHA-256 R09_validity_stopping.csv                    : 27e296087afa6369ce93b3f9aaf402eec3c6b78c8c734202e910742d02f7c6df
SHA-256 R09_eprocess_race.csv                        : dad44f3d05e14863c8fbbd9e91ba38a5298457255f02980891b56ad0ed544264
SHA-256 R09_level_granularity.csv                    : af880acfcbe2136b4ccd10a17ff6f8058b72fe669a44e9acc6e2d3f7729c5c70
SHA-256 R09_arl0.csv                                 : b0b486eca9404c8bc7c96799d20af9cf783ad4ec299ff7a2d7eedec623dbbcaa
SHA-256 R09_eprocess_race_control_ecusum.csv         : 90f7dd73e8d8f811113ddc629d88894d295cff05c9e481b9c7dbe629ada718f6
SHA-256 fig09_anytime_valid.png                      : 95dadf2706062b7b7ab406da6f97f13d5057849869e0dac4db7cae64836927ee
SHA-256 R09_claims.tex                               : 34b92176ccefee604f8034a97463efe72a760b7f5326a6fb655b511d20e80cfe
```

current tree, single run:

```
b0b486eca9404c8bc7c96799d20af9cf783ad4ec299ff7a2d7eedec623dbbcaa  results/R09_eprocess_anytime/data/R09_arl0.csv
dad44f3d05e14863c8fbbd9e91ba38a5298457255f02980891b56ad0ed544264  results/R09_eprocess_anytime/data/R09_eprocess_race.csv
90f7dd73e8d8f811113ddc629d88894d295cff05c9e481b9c7dbe629ada718f6  results/R09_eprocess_anytime/data/R09_eprocess_race_control_ecusum.csv
af880acfcbe2136b4ccd10a17ff6f8058b72fe669a44e9acc6e2d3f7729c5c70  results/R09_eprocess_anytime/data/R09_level_granularity.csv
27e296087afa6369ce93b3f9aaf402eec3c6b78c8c734202e910742d02f7c6df  results/R09_eprocess_anytime/data/R09_validity_stopping.csv
34b92176ccefee604f8034a97463efe72a760b7f5326a6fb655b511d20e80cfe  results/R09_eprocess_anytime/tables/R09_claims.tex
```

Note: C6 states that two successive runs produce SHA-256 identical artefacts and that --n-jobs 1 against the default produces byte-identical output since NUM_CHUNKS = 10 fixes the decomposition. The run WITHOUT --control-arms reproduces the four published CSVs byte for byte, proving the control arm leaks no state into the published path. Verified outside the process from the digests this log records (log line 284).

## 5. Design decisions taken outside the plan

1. DRAW MECHANISM, A DELIBERATE CHANGE FROM THE WITNESS: Every Bernoulli draw is y_t = (rng.random(size) < p) rather than rng.binomial(1, p, size). Exact Bernoulli either way, but with a threshold on a shared uniform two eta values consume the IDENTICAL uniform stream and differ only where the threshold moves, which makes the common-random-numbers plan structural rather than incidental. Generator.binomial's consumption pattern for n = 1 is an implementation detail that must not be relied upon (log line 12).

2. ENTROPY: Keys carry ROLE AND INDEX ONLY, never alpha and never eta: ('R09','m1_expectation'), ('R09','m1_ville',i), ('R09','cusum_calibration',i), ('R09','h0',i), ('R09','h1_sides'), ('R09','h1',i), ('R09','c4_matched_rate_bootstrap'). Because no key carries a process parameter, the same key serves every grid point: every comparison between arms at fixed (alpha, eta), and every comparison across eta and across alpha, is PAIRED. No pooled interval is published; the design effect of the one paired comparison control C4 reads is measured and logged beside it (log line 13).

3. RESOLUTION THAT DECISION BUYS, PANEL BY PANEL: Panels A and C carry Wilson intervals at n = 20000; panel B carries SEMs at n = 2000, i.e. sqrt(20000/2000) = 3.16x wider for the same underlying dispersion. Panel B's axis is labelled with its own n so the figure is not read against the caption's single number (log line 11).

4. CALIBRATION COHERENCE, REPLACING THE DELIVERED CONTROLS (b) AND (e): The delivered gates 0.046 <= FPR <= 0.055 and |FPR_M2 - calib| <= 3 sqrt(alpha(1-alpha)/N_NULL) both ignore that lambda_star is ITSELF ESTIMATED on N_CAL = 50000 streams (S4bis, second corollary). Replaced by C3 with correct variance alpha(1-alpha)(1/N_NULL + 1/N_CAL) (log line 285).

5. M1(i) GATE: |E[lambda_t] - 1| > 0.003 halts the run. The tolerance is derived from the mechanism (19.6 SE), so it is kept; the delivered M1(ii) gate if fpr > a + 0.005 is NOT, and it is removed as a gate and replaced by C3 (log line 286).

6. HALT CONDITION: If C4's matched-detection-rate quantile shows MIX strictly slower than CUSUM at eta <= 0.04 with its paired bootstrap interval excluding zero, or if C3's D+ rejects on the MIX arm, that is a D3: stop, report in full, change no parameter, tolerance, seed or bound. A reversal visible only in the marginal conditional ADD, or only on the common-detection subset, is NOT a halt condition and is reported under R09-add-conditioning (log line 288).

C4 HALT CONDITION NOT MET. At eta in (0.02, 0.04) the matched-rate quantile does not place MIX strictly above CUSUM with an interval excluding zero, so a marginal ADD reversal at those points is an artefact of conditioning on detection and is recorded under R09-add-conditioning with no severity (log line 399).

7. PARITY THRESHOLD is a KNIFE-EDGE OVER A GRID: The first non-parity point is eta = 0.02 at ADD_MIX - ADD_CUSUM = 211.8808049535603, z = +2.89. A redraw can move the threshold by one grid step; moving it UP leaves the caption's eta <= 0.10 true (log line 419).

## 6. Open questions, left open

1. The caption's '(2x10^4 streams per cell)' is IMPRECISE, NOT FALSE -- it describes neither the calibration (N_CAL = 50000) nor panel B (N_ALT = 2000) -- so the R09 prompt's perimeter filter keeps it out of docs/DEVIATIONS.md and it is carried as a camera-ready candidate instead (log line 10).

2. R09_validity_stopping.csv: 63 rows, 12 columns; R09_eprocess_race.csv: 140 rows, 9 columns; R09_level_granularity.csv: 14 rows, 8 columns; R09_arl0.csv: 21 rows, 11 columns; R09_eprocess_race_control_ecusum.csv: 70 rows, 9 columns (log lines 444-448). Re-serialisation reconciliation: all 5 CSVs re-serialise to the digests written above (log line 449).

3. CUSUM LATTICE: The increment dev - DELTA_CUSUM takes +0.4 or -0.6, so max_M lives on a 0.2 lattice; measured over the 50000 calibration streams, the largest distance from a lattice point is 6.253e-13 in lattice units, i.e. floating-point accumulation and not a second support. 1628 distinct values are realised, giving 1628 attainable levels (log line 305).

4. CUSUM LATTICE nearest attainable levels for each alpha (log lines 306-312).

5. MACRO SCOPE [CUSUM] the maximum peeking FPR over the WHOLE alpha grid is 0.34905 at alpha = 0.1, against 0.1988 at the figure's operating point alpha = 0.05. The macro binds the latter; the former is logged so the macro cannot be misread (log line 420).

6. MACRO SCOPE [MIX] the maximum peeking FPR over the WHOLE alpha grid is 0.0948 at alpha = 0.1, against 0.0491 at the figure's operating point alpha = 0.05. The macro binds the latter; the former is logged so the macro cannot be misread (log line 421).

