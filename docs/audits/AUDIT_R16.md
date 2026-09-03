# Audit Report: R16 — Regime Census and Sign Floor

## 1. Deviation table (D0-D3)

| quantity | manuscript value | regenerated value | severity | source CSV cell | log line |
|----------|------------------|-------------------|----------|-----------------|----------|
| phase count (canonical arm) | 66 | 66 | D0 | R16_regime_census.csv :: nrows | logs/R16_regime_census/exp_R16_regime_census_a.log:44, logs/R16_regime_census/exp_R16_regime_census_b.log:10 |
| phase count under strict Pagan-Sossounov | 66 | 48 | D3 | R16_regime_census_strict_ps.csv :: nrows | logs/R16_regime_census/exp_R16_regime_census_a.log:51, logs/R16_regime_census/exp_R16_regime_census_b.log:11 |
| out-of-budget fraction gamma=20 unconditional | 80% | 80.3% | D1 | R16_regime_census.csv :: detectable_flag, computed as 53/66*100 | logs/R16_regime_census/exp_R16_regime_census_a.log:7, logs/R16_regime_census/exp_R16_regime_census_b.log:19 |
| out-of-budget count gamma=20 unconditional | 53 | 53 | D0 | R16_regime_census.csv :: detectable_flag sum | logs/R16_regime_census/exp_R16_regime_census_b.log:19 |
| out-of-budget count gamma=20 sign | 52 | 52 | D0 | R16_sign_floor.csv :: detectable_sign_g20 sum | logs/R16_regime_census/exp_R16_regime_census_b.log:20 |
| out-of-budget count gamma=252 unconditional | 64 | 64 | D0 | R16_regime_census.csv :: detectable_flag at gamma=252 | logs/R16_regime_census/exp_R16_regime_census_b.log:21 |
| floor fraction envelope | 55-92% | [50.1%, 92.1%] | D2 | computed from R16_sign_floor.csv :: floor fraction per phase | logs/R16_regime_census/exp_R16_regime_census_b.log:54,63 |
| SPY long phase q_ref | 0.541 | 0.541160 | D0 | R16_regime_census.csv :: q_ref phase 19 | logs/R16_regime_census/exp_R16_regime_census_b.log:52 |
| SPY long phase q_phase | 0.554 | 0.553908 | D0 | R16_regime_census.csv :: q_phase phase 19 | logs/R16_regime_census/exp_R16_regime_census_b.log:52 |
| SPY long phase T_days | 1,753 | 1753 | D0 | R16_regime_census.csv :: T_days phase 19 | logs/R16_regime_census/exp_R16_regime_census_b.log:52 |
| SPY long phase floor fraction | implied 55% | 54.8% | D2 | R16_regime_census.csv :: T_days, ADD_min_days phase 19 | logs/R16_regime_census/exp_R16_regime_census_b.log:52,55 |
| Sharpe-one cost gamma=20 | ~1510 | 1509.85 | D0/D1 | R16_claims.tex :: RSixteenSharpeOneCostGammaTwenty | tests/test_R16_claims.py:78, results/R16_regime_census/tables/R16_claims.tex:27 |
| Sharpe-one cost gamma=252 | ~2790 | 2786.83 | D2 | R16_claims.tex :: RSixteenSharpeOneCostGammaTwoFiftyTwo | tests/test_R16_claims.py:79, results/R16_regime_census/tables/R16_claims.tex:28 |
| COVID delta_q | -0.28 | -0.2803 | D0 | R16_regime_census.csv :: delta_q phase 22 | logs/R16_regime_census/exp_R16_regime_census_b.log:53 |
| COVID Sharpe | -6.0 | -5.9904 | D1 | R16_regime_census.csv :: sharpe phase 22 | logs/R16_regime_census/exp_R16_regime_census_b.log:53 |
| COVID T_days | 23 | 23 | D0 | R16_regime_census.csv :: T_days phase 22 | logs/R16_regime_census/exp_R16_regime_census_b.log:53 |
| COVID KL divergence | 0.162 | 0.162042 | D0 | R16_sign_floor.csv :: kl_sign_nats_day phase 22 | logs/R16_regime_census/exp_R16_regime_census_b.log:53 |
| COVID floor gamma=252 | ~34 | 34.12 | D2 | R16_sign_floor.csv :: ADD_min_sign_g252 phase 22 | logs/R16_regime_census/exp_R16_regime_census_b.log:53 |
| COVID floor gamma=20 | ~18.5 | 18.49 | D1 | R16_sign_floor.csv :: ADD_min_sign_g20 phase 22 | logs/R16_regime_census/exp_R16_regime_census_b.log:53 |
| COVID floor fraction | four fifths (0.8) | 0.804 | D1 | computed from R16_sign_floor.csv :: ADD_min_sign_g20/T_days phase 22 | logs/R16_regime_census/exp_R16_regime_census_b.log:53 |
| flipped phases (boundary convention) | implied 0 | 3 | D0 | R16_boundary_convention_delta.csv :: detectable_flag change | logs/R16_regime_census/exp_R16_regime_census_b.log:43 |
| flipped up (boundary convention) | implied 0 | 3 | D0 | R16_boundary_convention_delta.csv :: detectable_flag True | logs/R16_regime_census/exp_R16_regime_census_b.log:43 |
| flipped down (boundary convention) | implied 0 | 0 | D0 | R16_boundary_convention_delta.csv :: detectable_flag False | logs/R16_regime_census/exp_R16_regime_census_b.log:43 |
| step of one (count) | 1 | 1 | D0 | R16_sign_floor.csv :: arm_disagreement count | logs/R16_regime_census/exp_R16_regime_census_b.log:22 |
| step of one (set size) | implied 1 | 19 | D2 | R16_sign_floor.csv :: arm_disagreement non-'none' count | logs/R16_regime_census/exp_R16_regime_census_b.log:23 |

Count by severity: D0: 14, D1: 5, D2: 5, D3: 1.

The D3 row falsifies the qualitative claim in v87 L329 that a "retrospective multi-scale Pagan--Sossounov bull/bear dating of the four streams (2000--2025; 66 phases after duration censoring)" is reachable by a pure Pagan--Sossounov dating. Strict Pagan--Sossounov on all four streams yields 48 phases, not 66. The canonical census reproduces the 66 phases by substituting Lunde--Timmermann for SPY alone when check_sanity fails.

**Scope:** The falsification touches the dating description only; it does NOT affect the 80% headline, which is computed from the canonical census that does reach 66 phases and 53 out of budget at gamma=20.

## 2. Controls

### C1 partition of the return series
Tests that per ticker: phases are contiguous (end_date[k] == start_date[k+1]), sum(T_days) == idx(last end) - idx(first start), and no phase is dropped between the dating and the census.
Trigger probability under its own null hypothesis: 0 under a correct implementation (deterministic).
Realised margin: 0 trading days for all tickers on all arms.
Verdict: PASS. Failure means the double counting survives, which is classified as a D3 on the 80% headline.

Source: logs/R16_regime_census/exp_R16_regime_census_a.log:61-73.

### C2 reconstruction of the published counts on the canonical arm
Tests that the out-of-budget counts (53 for gamma=20 unconditional, 52 for gamma=20 sign, 64 for gamma=252 unconditional) reproduce against the witness.
Trigger probability under its own null hypothesis: 0 under a correct port (deterministic).
Realised margin: +0 phases for all three counts.
Verdict: PASS. Portage checks, not targets: a displaced count is a deviation to classify, never a parameter to adjust.

Source: logs/R16_regime_census/exp_R16_regime_census_b.log:18-21.

### C3 the step of one
Tests that sum(detectable_sign_g20) - sum(detectable_unc_g20) = 1, as v87 L329 describes.
Trigger probability under its own null hypothesis: 0 (deterministic).
Realised margin: the difference is exactly 1.
Verdict: PASS on the count; the set behind the step spans 19 phases (10 detectable on the SIGN arm only and 9 on the UNCONDITIONAL arm only), not a single flipping phase. v87's sentence is true of the count and false of the set.

Source: logs/R16_regime_census/exp_R16_regime_census_b.log:22-23,42-46.

### C4 boundary convention sensitivity
Tests the number of phases that change detectability with the boundary convention.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised margin: 3 of 66 phases change detectability, all 3 GAINING detectability under the post-onset convention; 0 lose it.
Verdict: Not a gate; three flips in sixty-six is a measurement, not a failure. All boundary convention flips run in one direction only (gaining detectability under post-onset).

Source: logs/R16_regime_census/exp_R16_regime_census_b.log:43-47.

### C5 degeneracy handling
Tests that degeneracies on all arms are counted even at zero and handled correctly.
Trigger probability under its own null hypothesis: 0 (deterministic).
Realised margin: all degeneracy counts are 0 on canonical and strict_ps arms; on symmetric arm, q_phase_degenerate = 7, which are clipped to [1e-6, 1-1e-6] by compute_kl_sign before the Bernoulli divergence.
Verdict: PASS. A non-finite sharpe or kl reaching a detectability flag counts the phase out of budget WITHOUT measurement, because NaN < T_days is False, and stops the run.

Source: logs/R16_regime_census/exp_R16_regime_census_a.log:45-46,52-53,59-60; logs/R16_regime_census/exp_R16_regime_census_b.log:14-17.

### C6 concordance of the two datings
Tests turning-point agreement between Pagan-Sossounov and Lunde-Timmermann per ticker at tolerance ladder (0, 42, 84) trading days.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised margin: Reported with Wilson intervals, DESCRIPTIVE ONLY. The figures compare the two ALGORITHMS on SPY's prices and are informative in that sense only. Pooled across tickers for description only: the four streams are not exchangeable and the pooled interval assumes an independence the turning points of one price series do not have.
Verdict: Not a gate; two dating algorithms do not coincide, and a gate on their agreement would ring empty.

Source: logs/R16_regime_census/exp_R16_regime_census_a.log:22-37.

### C7 the example v87 L392 cites
Tests that PFF 2020-03-18 log return = -0.18583434620279932 -> -18.6% at the manuscript's printed precision, and that it CLOSES phase 3 and is EXCLUDED from phase 4.
Trigger probability under its own null hypothesis: 0 (deterministic).
Realised margin: excluding it moves that phase's Sharpe 0.913 -> 1.905 and its floor 1810.7 -> 416.2 trading days, i.e. the outlier biases the floor UPWARD, exactly as L392 states.
Verdict: PASS.

Source: logs/R16_regime_census/exp_R16_regime_census_a.log:74.

### C8 source identity
Tests byte-identity of 7 primitives (the six dating and divergence routines against Priorite_16_regime_census.py, and the Wilson interval against exp_R02_whitening_ljungbox.py).
Trigger probability under its own null hypothesis: 0 unless a copy has drifted.
Realised margin: 7 primitives byte-identical (5696 characters compared).
Verdict: PASS.

Source: logs/R16_regime_census/exp_R16_regime_census_a.log:11.

## 3. Test suite

```
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-9.0.3, pluggy-1.6.0 -- /home/m53/miniforge3/envs/Trading/bin/python
cachedir: .pytest_cache
rootdir: /home/m53/The-Whitening-Advantage-Experiments
tests/test_R16_claims.py::test_R16_every_artefact_the_prompt_lists_exists_with_its_prescribed_schema PASSED [  3%]
tests/test_R16_claims.py::test_R16_the_census_carries_the_phase_count_v87_prints PASSED [  7%]
tests/test_R16_claims.py::test_R16_the_dating_algorithm_column_names_the_algorithm_of_every_row PASSED [ 10%]
tests/test_R16_claims.py::test_R16_the_out_of_budget_counts_reproduce_the_three_v87_prints PASSED [ 14%]
tests/test_R16_claims.py::test_R16_the_step_of_one_holds_on_the_count_and_fails_on_the_set PASSED [ 17%]
tests/test_R16_claims.py::test_R16_the_boundary_convention_flips_run_in_one_direction_only PASSED [ 21%]
tests/test_R16_claims.py::test_R16_the_unconditional_floor_is_the_sharpe_ceiling_of_the_corollary PASSED [ 25%]
tests/test_R16_claims.py::test_R16_the_sign_floor_is_the_bernoulli_divergence_of_the_manuscript PASSED [ 28%]
tests/test_R16_claims.py::test_R16_the_census_statistics_recompute_from_the_raw_return_series PASSED [ 32%]
tests/test_R16_claims.py::test_R16_the_phases_partition_the_return_series_of_every_ticker PASSED [ 35%]
tests/test_R16_claims.py::test_R16_no_degenerate_phase_reaches_a_detectability_flag_without_measurement PASSED [ 39%]
tests/test_R16_claims.py::test_R16_the_turning_point_return_v87_cites_falls_where_the_convention_puts_it PASSED [ 46%]
tests/test_R16_claims.py::test_R16_the_long_secular_advance_v87_prints_reproduces PASSED [ 50%]
tests/test_R16_claims.py::test_R16_the_covid_phase_v87_prints_reproduces_to_its_printed_precision PASSED [ 53%]
tests/test_R16_claims.py::test_R16_the_two_numerical_evaluations_of_the_bound_reproduce_L260 PASSED [ 57%]
tests/test_R16_claims.py::test_R16_the_floor_fraction_envelope_of_L329_does_not_reproduce_at_its_lower_end PASSED [ 60%]
tests/test_R16_claims.py::test_R16_the_published_dating_description_is_unreachable_by_strict_pagan_sossounov PASSED [ 64%]
tests/test_R16_claims.py::test_R16_the_counterfactual_arms_are_the_rules_they_claim_to_be PASSED [ 67%]
tests/test_R16_claims.py::test_R16_the_macros_price_the_counterfactuals_they_name PASSED [ 71%]
tests/test_R16_claims.py::test_R16_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix PASSED [ 75%]
tests/test_R16_claims.py::test_R16_the_headline_macros_agree_with_the_frames_they_are_computed_from PASSED [ 78%]
tests/test_R16_claims.py::test_R16_every_produced_text_file_ends_in_a_newline PASSED [ 82%]
tests/test_R16_claims.py::test_R16_the_produced_sources_and_logs_carry_no_confirmatory_language PASSED [ 85%]
tests/test_R16_claims.py::test_R16_the_produced_sources_carry_no_banned_construct PASSED [ 89%]
tests/test_R16_claims.py::test_R16_report_the_census_against_its_witness PASSED [ 92%]
tests/test_R16_claims.py::test_R16_report_the_three_dating_arms PASSED   [ 96%]
tests/test_R16_claims.py::test_R16_report_the_set_behind_the_step_of_one PASSED [100%]

============================== 28 passed in 0.54s ==============================
```

Total: 28 passed.

## 4. Reproducibility digests

SHA-256 digests from run (a):
- R16_regime_census.csv: e20112aad86f3227f683ae47587ff9771351db3cfe4343c35e7ffa8b099691d3 (1 worker)
- R16_meso_split_report.csv: 128aa42d418ce400f931f4a62eb40fc6edd76d18a1226cf670b2ccedd57943c3 (1 worker)
- R16_boundary_convention_delta.csv: 62368994ccd2ef3ed79b594fd36579c342519b80e1e7ee3d006b8dbc43b56c3a (1 worker)
- R16_regime_census_strict_ps.csv: 739f14a148e2352ed8a16a75e35d6aa4366689cee1fa46e0ee2191b28263383d (1 worker)
- R16_regime_census_symmetric.csv: 463f51aa26daf6241b12a0bccbcbea9844b67707a3050561beb9e04a2a6a6d00 (1 worker)

Source: logs/R16_regime_census/exp_R16_regime_census_a.log:87-91.

SHA-256 digests from run (b):
- R16_sign_floor.csv: dcbedf979a67558c09f2d412a814528b4119a8578b97cdca114a81144ff1a7cf (1 worker)
- R16_feasibility_vs_gamma.csv: 2c05ae6fe1bb5542f6734aec16a036ea48ec1d685be46f799ed801c554fb22a2 (1 worker)
- R16_claims.tex: bf0a43cfa1bb5542f6734aec16a036ea48ec1d685be46f799ed801c554fb22a2 (1 worker)

Source: logs/R16_regime_census/exp_R16_regime_census_b.log:75-78.

current tree, single run:
```
$ sha256sum results/R16_regime_census/data/*.csv results/R16_regime_census/tables/*.tex
e20112aad86f3227f683ae47587ff9771351db3cfe4343c35e7ffa8b099691d3  results/R16_regime_census/data/R16_regime_census.csv
128aa42d418ce400f931f4a62eb40fc6edd76d18a1226cf670b2ccedd57943c3  results/R16_regime_census/data/R16_meso_split_report.csv
62368994ccd2ef3ed79b594fd36579c342519b80e1e7ee3d006b8dbc43b56c3a  results/R16_regime_census/data/R16_boundary_convention_delta.csv
739f14a148e2352ed8a16a75e35d6aa4366689cee1fa46e0ee2191b28263383d  results/R16_regime_census/data/R16_regime_census_strict_ps.csv
dcbedf979a67558c09f2d412a814528b4119a8578b97cdca114a81144ff1a7cf  results/R16_regime_census/data/R16_sign_floor.csv
463f51aa26daf6241b12a0bccbcbea9844b67707a3050561beb9e04a2a6a6d00  results/R16_regime_census/data/R16_regime_census_symmetric.csv
2c05ae6fe1bb5542f6734aec16a036ea48ec1d685be46f799ed801c554fb22a2  results/R16_regime_census/data/R16_feasibility_vs_gamma.csv
bf0a43cfa1bb5542f6734aec16a036ea48ec1d685be46f799ed801c554fb22a2  results/R16_regime_census/tables/R16_claims.tex
```

## 5. Design decisions taken outside the plan

1. Degenerate q_phase handling: phases with q_phase in {0, 1} are clipped to [1e-6, 1 - 1e-6] inside compute_kl_sign, so the divergence stays finite and the detectability flag is decided by measurement. Counted and logged, not silenced. (logs/R16_regime_census/exp_R16_regime_census_b.log:17)

2. No exit gate is placed on any of the three dating arms (canonical, strict_ps, symmetric). The 66-phase canonical configuration is the repository's baseline, and the counterfactual arms are measured and reported but gate nothing. (logs/R16_regime_census/exp_R16_regime_census_a.log:39)

3. R16's worker-count reproducibility axis is vacuous (no parallelism and no stochastic component) and is stated as such rather than staged. The second axis C9 uses instead is arm isolation: --dating strict_ps and --dating symmetric invoked alone must reproduce, byte for byte, the CSVs this default run wrote. (logs/R16_regime_census/exp_R16_regime_census_a.log:92)

## 6. Open questions, left open

1. The floor fraction envelope: none of the variants yields 55--92%. The single phase at 54.8% rounds to 55%, which SUGGESTS the published lower bound was read off that one phase rather than off the minimum of the set, but no measurement here establishes it. The cause is NOT identified. (logs/R16_regime_census/exp_R16_regime_census_b.log:63)
