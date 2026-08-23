# Audit Report: R14 — Crypto iso-FPR Efficiency Reversal

## 1. Deviation table (D0-D3)

| quantity | manuscript value | regenerated value | severity | source CSV cell | log line |
|----------|-----------------|-------------------|----------|-----------------|----------|
| BTC nu_hat | 2.78 | 2.7791143512276766 | D0 | R14_crypto_diagnostics.csv :: nu_hat_BTC | 293 |
| iso-FPR BTC, percent | 4.7 | 4.716981132075472 | D0 | R14_crypto_isofpr_race.csv :: iso_fpr_matched (Real_BTC) | 294 |
| ETH Ljung-Box p-value | 0.019 | 0.018785617996181257 | D0 | R14_crypto_diagnostics.csv :: ljung_box_p_ETH | 295 |
| BTC onsets | 106 | 106.0 | D0 | R14_crypto_isofpr_race.csv :: n_onsets (Real_BTC) | 296 |
| ETH onsets | 72 | 72.0 | D0 | R14_crypto_isofpr_race.csv :: n_onsets (Real_ETH) | 297 |
| Real_BTC ratio at c = 0.35 | 0.74 | 0.7407126611068993 | D0 | R14_crypto_isofpr_race.csv :: ADD ratio (Concept/Eco) | 298 |
| Real_BTC ratio at c = 1.5 | 1.01 | 1.0074285714285713 | D0 | R14_crypto_isofpr_race.csv :: ADD ratio (Concept/Eco) | 299 |
| Real_BTC mean ratio | 0.87 | 0.8682292705270857 | D0 | R14_crypto_isofpr_race.csv :: ADD ratio mean (Real_BTC) | 300 |
| Synth_BTC mean ratio | 1.06 | 1.041041514153539 | D2 | R14_crypto_isofpr_race.csv :: ADD ratio mean (Synth_BTC) | 301 |
| Synth_BTC ratio minimum | 0.98 | 0.9544910179640719 | D2 | R14_crypto_isofpr_race.csv :: ADD ratio min (Synth_BTC) | 302 |
| Synth_BTC ratio maximum | 1.14 | 1.2384142067139186 | D2 | R14_crypto_isofpr_race.csv :: ADD ratio max (Synth_BTC) | 303 |

Count by severity: D0: 8, D2: 3, D3: 0.

## 2. Controls

### C1 — Pairwise-reliable grids re-derivation
Tests that the pairwise-reliable grids re-derive identically from R14_crypto_isofpr_race.csv, and every aggregate above was taken over them.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Verdict: Passed (log line 288).

### C2 — iso-FPR
Tests that both arms realize one false-alarm rate on every published source. The realized FPR on Real_BTC is 5/106 = 0.04716981132075472; on Real_ETH, Concept lambda* = 7.799994544332583 realizes 4/72 = 0.05555555555555555, Eco lambda* = 39.81696944588852 realizes 3/72 = 0.041666666666666664. 
Trigger probability: For BTC, the bisection tolerance admits exactly one count (5) at 106 onsets, so the two arms are forced onto the same rate (0). For ETH, no integer count satisfies the tolerance, so agreement is an outcome of dynamics (NOT RECOVERABLE FROM THE LOG).
Verdict: Passed for Real_BTC and Synth_BTC (exact match); Real_ETH arms differ by 0.0138889 (log lines 28, 146, 169).

### C3 — QMLE recovery
20 GARCH(1,1) streams of 2000 steps at (alpha, beta) = (0.05, 0.9), unconditional variance 0.0001, standard-normal innovations. Median bias = 0.0228, fallback fraction = 0.0000, frozen fraction = 0.0000, 20/20 converged.
Trigger probability: NOT RECOVERABLE FROM THE LOG (the null distribution of a median over 20 simulations has no closed form).
Verdict: Passed (log line 24). The delivered admissibility band is median bias < 0.05 and fallback fraction < 0.1.

### C4 — Moment condition
Derived at run time: for a standardized Student-t, E|z|^p < inf iff p < nu, so the variance exists iff nu > 2 and the fourth moment iff nu > 4. At nu_hat = 2.779114 for BTC and 3.249791 for ETH, the variance exists and the fourth moment DOES NOT exist.
Trigger probability: 0 (static derivation).
Verdict: Recorded (log lines 26-27, 29-30).

### C6 — Source identity
10 primitives byte-identical to the files that own them (3670 characters compared) — _garch_nll, fit_garch_qmle, strict_cusum, bilateral_delay, bisect_fpr, wilson_ci and compute_onsets against Priorite_24d_crypto_isofpr_race.py, and get_deterministic_seed, seed_sequence_for and rng_for against exp_R13_oracle_ceiling_a.py.
Trigger probability: 0 unless a copy has drifted.
Verdict: Deterministic (log line 15).

### C8 — Non-anticipativity
First onset verification: the full pre-onset vector ['alpha', 'beta', 'eps_last', 'med_hat', 'mu_hat', 'omega', 'q_hat_ref', 's2_last'] is bit-identical after r[onset:] += 100. The identity is tautological by slicing.
Trigger probability: 0 (structural assertion, not evidence).
Verdict: Recorded for Real_BTC (onset 516, log line 37), Real_ETH (onset 507, log line 143), Synth_BTC (onset 516, log line 212).

### C9 — Design effect
Design effect computed from the mechanism over 24 mechanism-fixed lags. Multiple clamped and unclamped values reported throughout the race. Clamped when the estimate would claim more independent readings than the observations contain.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Verdict: Recorded for all sources and magnitudes (log lines 41-46, 53-57, 64-68, 72-76, 80-84, 88-92, 96-100, 104-108, 112-116, 120-124, 128-132, 136-140, 151-155, 161-165, 174-178, 184-188, 198-202, 206-210).

### C10 — Entropy migration
On Priorite_24d_crypto_isofpr_race.py: no np.random.<distribution> call exists anywhere in the witness — the only np.random members it touches are ['RandomState', 'seed'] — and it constructs 3 RandomState instances. On this script: no draw touches the global NumPy stream, and np.random.RandomState appears only inside ['dither_vector', 'synth_generator', 'qmle_innovation_streams'].
Trigger probability: 0 (static).
Verdict: Recorded (log lines 16-17).

## 3. Test suite

```
tests/test_R14_claims.py::test_R14_every_artefact_the_prompt_lists_exists_with_its_prescribed_schema PASSED
tests/test_R14_claims.py::test_R14_the_onset_delays_reproduce_every_aggregate_of_the_race PASSED
tests/test_R14_claims.py::test_R14_the_bisection_tolerance_admits_one_count_at_106_onsets_and_none_at_72 PASSED
tests/test_R14_claims.py::test_R14_the_two_arms_realize_one_false_alarm_rate_on_every_published_source PASSED
tests/test_R14_claims.py::test_R14_the_iso_fpr_match_on_real_ethereum_is_lost_under_the_re_keying PASSED
tests/test_R14_claims.py::test_R14_no_aggregate_reads_a_cell_the_caption_draws_hollow PASSED
tests/test_R14_claims.py::test_R14_the_derived_reliability_rule_reproduces_the_delivered_literal PASSED
tests/test_R14_claims.py::test_R14_the_bitcoin_numerals_of_L345_and_the_caption_reproduce PASSED
tests/test_R14_claims.py::test_R14_the_ethereum_boundary_of_L345_reproduces PASSED
tests/test_R14_claims.py::test_R14_the_synthetic_control_numerals_of_L345_do_not_reproduce_at_their_printed_precision PASSED
tests/test_R14_claims.py::test_R14_the_real_bitcoin_race_is_untouched_by_the_re_keying PASSED
tests/test_R14_claims.py::test_R14_the_design_effect_is_computed_from_the_mechanism_and_never_below_one PASSED
tests/test_R14_claims.py::test_R14_every_persisted_interval_is_a_wilson_interval_inside_the_unit_square PASSED
tests/test_R14_claims.py::test_R14_the_qmle_fallback_counters_are_reported_even_at_zero PASSED
tests/test_R14_claims.py::test_R14_the_legacy_seed_arm_reproduces_every_discrete_quantity_of_the_witness PASSED
tests/test_R14_claims.py::test_R14_the_legacy_seed_artefacts_declare_that_they_certify_no_published_value PASSED
tests/test_R14_claims.py::test_R14_the_carried_primitives_are_byte_identical_to_the_files_that_own_them PASSED
tests/test_R14_claims.py::test_R14_no_draw_reaches_the_global_numpy_stream PASSED
tests/test_R14_claims.py::test_R14_every_square_root_of_a_sample_size_follows_a_design_effect PASSED
tests/test_R14_claims.py::test_R14_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix PASSED
tests/test_R14_claims.py::test_R14_every_produced_text_file_ends_in_a_newline PASSED
tests/test_R14_claims.py::test_R14_the_produced_sources_and_logs_carry_no_confirmatory_language PASSED
tests/test_R14_claims.py::test_R14_the_produced_sources_carry_no_banned_construct PASSED
tests/test_R14_claims.py::test_R14_report_the_campaign_against_its_witness PASSED
tests/test_R14_claims.py::test_R14_report_the_design_effect_and_the_reliable_grids PASSED
tests/test_R14_claims.py::test_R14_report_the_ratio_series_of_every_source PASSED
```

Total: 26 passed in 0.66s.

## 4. Reproducibility digests

Default arm (migrated entropy):
- SHA-256 R14_crypto_diagnostics.csv               : e598dd2d4b0d58f09d704dc65d960db9cb169d9e27bdbfc39a36815c8f629bf7 (log line 309)
- SHA-256 R14_crypto_isofpr_race.csv               : f6d037d6e0316d3ff494459fd92debc878ec518f831bab8c20bd1f99302e681e (log line 310)
- SHA-256 R14_qmle_recovery.csv                    : 671bc7377c69ed8aacf9ceb336255d15df1ef0e92d38e39fd39b804afbf574db (log line 311)
- SHA-256 R14_onset_delays.csv                     : 8c763481cf351213824b7ae844fdc3cff763e7d501164c054533cd85d9214d31 (log line 312)
- SHA-256 fig16_crypto_race.png                    : 96d3c9f381c4f91aafb52456df207f08769f4b3a914a2e3b8f8830cfc8f7187d (log line 313)
- SHA-256 R14_claims.tex                           : 2fe6fd0a43004c72e46b2f8f6397bfa39cc220cd98c102a2f4b2d3679a257544 (log line 314)

Legacy seeds arm:
- SHA-256 R14_crypto_diagnostics_legacy_seeds.csv : NOT RECOVERABLE FROM THE LOG
- SHA-256 R14_crypto_isofpr_race_legacy_seeds.csv : NOT RECOVERABLE FROM THE LOG
- SHA-256 R14_onset_delays_legacy_seeds.csv        : NOT RECOVERABLE FROM THE LOG
- SHA-256 R14_qmle_recovery_legacy_seeds.csv       : NOT RECOVERABLE FROM THE LOG
- SHA-256 fig16_crypto_race_legacy_seeds.png       : NOT RECOVERABLE FROM THE LOG
- SHA-256 R14_claims_legacy_seeds.tex              : NOT RECOVERABLE FROM THE LOG

Witness (Priorite_24d):
- SHA-256 protocol_24a_crypto_diagnostics.csv: 9940385c6180aad8db1eea795433aa6b5a42957250fec82f6efd073e1e01bf20 (log line 286)
- SHA-256 protocol_24b_crypto_isofpr_race.csv: 1d589cd3d3a0fdc8b3bd2c599f540f884f4151fa5161ea89777327f365d94d06 (log line 287)
- SHA-256 protocol_24c_qmle_recovery_crypto.csv: c5bf3ca2b92a8799b143c8b29ec47ad7756daee26741a440214f8fb634221c23 (log line 288)

Data inputs:
- SHA-256 btc_usd_daily.csv: a9c84c890cac7284f6330e3ab4d4aed70a9a5e01ec04a8fc0c9ba8999e79c3f4 (log line 58)
- SHA-256 eth_usd_daily.csv: f44703a75e4510e906ab1cda6e0a50d96e232bc80aba4ef5105ce6ae94c049f1 (log line 60)

## 5. Design decisions taken outside the plan

1. The entropy migration replaces hardcoded seeds (100, 200, 201, 300) with role-and-index keys: ('R14', 'dither'), ('R14', 'synth', 'BTC'), ('R14', 'synth', 'ETH'), ('R14', 'qmle'). Every migrated draw is keyed by rng_for on its role and index alone, never on a process parameter, instituting common random numbers (log line 17).
2. The `_legacy_seeds` arm is executed unconditionally by run_experiment_R14.sh after the default arm, to separate the effect of the entropy migration from a transcription error in this port (log line 1 in legacy_seeds log).
3. The QMLE audit over pre-onset fits reports non-converged, frozen, and fallback counters even at zero (log lines 38, 147, 215).
4. Control S4.2 forbids hoisting any primitives into experiments/common/: a machine diff shows _garch_nll, fit_garch_qmle, strict_cusum and wilson_ci all differ between this witness and the R01/R03/R04/R04b/R11/R13 copies (log line 15).

## 6. Open questions, left open

1. The R14 prompt states 25 of 88 unreliable cells; witness 25 of 88, regenerated 28 of 88 (log line 306).
2. Witness Synth_ETH: mean ratio 0.5418423397760349 over 8 pairwise-reliable magnitudes; regenerated 0.9189199350683375 over 7 magnitudes, 95% interval [0.7876523389282832, 0.9615749561648425] (log line 307).
3. The ETH synthetic control does not recover the light-tailed ordering at ETH's onsets, as stated in L345 (log line 307).
