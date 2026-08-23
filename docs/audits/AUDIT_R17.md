# Audit Report: R17 Econometric Baseline

## 1. Deviation table (D0-D3)

| quantity                                                     | manuscript value | regenerated value  | severity | source CSV cell                                         | log line                             |
| ------------------------------------------------------------ | ---------------- | ------------------ | -------- | ------------------------------------------------------- | ------------------------------------ |
| L341 persistence median at n_warmup = 250, median of the sum | 0.62             | 0.6257515          | D2       | R17_warmup_sensitivity.csv :: persistence_median_pooled | exp_R17_econometric_baseline.log:239 |
| L341 FPR_Eco at n_warmup = 250, percent                      | 9.5%             | 10.5               | D3       | R17_warmup_sensitivity.csv :: FPR_Eco                   | exp_R17_econometric_baseline.log:240 |
| L341 FPR_Eco at n_warmup = 500, percent                      | 3.0%             | 7.000000000000001  | D3       | R17_warmup_sensitivity.csv :: FPR_Eco                   | exp_R17_econometric_baseline.log:241 |
| L341 sign FPR envelope minimum, percent                      | 3%               | 9.5                | D2       | R17_warmup_sensitivity.csv :: FPR_ML                    | exp_R17_econometric_baseline.log:242 |
| L341 sign FPR envelope maximum, percent                      | 8%               | 11.0               | D2       | R17_warmup_sensitivity.csv :: FPR_ML                    | exp_R17_econometric_baseline.log:243 |
| L341 true persistence, by design                             | 0.85             | 0.8500000000000001 | D0       | protocol 3d, by design                                  | exp_R17_econometric_baseline.log:244 |

Count by severity: D0: 1, D2: 3, D3: 2.

**Falsified qualitative claim (L341):** The manuscript attributes a false-alarm figure to the arm Table 1 defines as the level residual (Eco-L1).
**Evidence (Three-step):**
1. Table 1 defines the Eco-L1 arm as monitoring the level residual.
2. L341 reports false-alarm figures attributed to this Eco-L1 arm.
3. The producing cell actually monitors the squared standardized residual, an arm the source script itself names differently.
**Scope:** The falsification applies to the false-alarm numerals only.

## 2. Controls

### C2 — sign stream bit-identity across grid points
What it tests: the monitored sign stream is bit-identical across grid points where the key omits the grid coordinate.
Trigger probability: 0 under its own null hypothesis (deterministic; the sign stream depends only on key, nu and n, exp_R17_econometric_baseline.log:102,152,159,177-180).
Realised margin: exact identity (SHA-256 match).
Verdict: pass.

### C3 — penalty exactness
What it tests: the realized penalty matches its target to machine precision.
Trigger probability: 0 under its own null hypothesis (deterministic; the bisection is exact, exp_R17_econometric_baseline.log:92).
Realised margin: max relative error 2.554e-14 (exp_R17_econometric_baseline.log:91).
Verdict: pass.

### C4 — argument order of solve_beta_for_gamma
What it tests: the argument order of solve_beta_for_gamma matches the witness signature.
Trigger probability: 0 under its own null hypothesis (deterministic; all call sites carry identical argument expressions, exp_R17_econometric_baseline.log:83).
Realised margin: exact match.
Verdict: pass.

### C5 — monotone restoration of FPR_Eco in n_warmup
What it tests: monotone restoration of FPR_Eco in n_warmup, at each gamma_lev.
Trigger probability: 0.2438 under its own null hypothesis (1 - (1 - 0.0455)^6 under a null of exact equality at every step, exp_R17_econometric_baseline.log:191).
Realised margin: 0 steps of FPR_Eco invert beyond two paired standard errors on either gamma_lev (exp_R17_econometric_baseline.log:205).
Verdict: pass.

### C6 — exact identity at Gamma = 1.00
What it tests: at Gamma = 1.00, the two thresholds are the same float and the Uncal and Recalib counts coincide.
Trigger probability: 0 under its own null hypothesis (exact identity, exp_R17_econometric_baseline.log:94).
Realised margin: exact identity.
Verdict: pass.

### C8 — source identity of 9 routines
What it tests: 9 routines are byte-identical to the files that own them.
Trigger probability: 0 under its own null hypothesis (deterministic; trigger probability 0 unless a copy has drifted, exp_R17_econometric_baseline.log:12).
Realised margin: exact match.
Verdict: pass.

### C9 — reproducibility at different worker counts
What it tests: two executions at different worker counts.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised margin: NON-APPLICABLE (the script is serial: it creates no process pool, no thread pool and no worker, exp_R17_econometric_baseline.log:259).
Verdict: NON-APPLICABLE.

## 3. Test suite

```
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-9.0.3, pluggy-1.0 -- /home/m53/miniforge3/envs/Trading/bin/python
cachedir: .pytest_cache
rootdir: /home/m53/The-Whitening-Advantage-Experiments
plugins: anyio-4.8
collecting ... collected 30 items

tests/test_R17_claims.py::test_R17_every_artefact_the_prompt_lists_exists_with_its_prescribed_schema PASSED [  3%]
tests/test_R17_claims.py::test_R17_the_per_fit_table_reproduces_every_aggregate_of_the_warmup_table PASSED [  6%]
tests/test_R17_claims.py::test_R17_the_lower_bound_flag_is_the_box_constraint_and_not_a_threshold PASSED [ 10%]
tests/test_R17_claims.py::test_R17_the_realized_penalty_matches_its_target_at_the_eight_grid_points PASSED [ 13%]
tests/test_R17_claims.py::test_R17_every_persisted_interval_is_a_wilson_interval_inside_the_unit_square PASSED [ 16%]
tests/test_R17_claims.py::test_R17_the_carried_primitives_are_byte_identical_to_the_files_that_own_them PASSED [ 20%]
tests/test_R17_claims.py::test_R17_the_three_adapted_routines_differ_from_the_witness_at_one_node_each PASSED [ 23%]
tests/test_R17_claims.py::test_R17_the_argument_order_of_solve_beta_for_gamma_is_the_witness_s_at_every_call_site PASSED [ 26%]
tests/test_R17_claims.py::test_R17_the_sign_stream_is_bit_identical_across_the_leverage_axis PASSED [ 30%]
tests/test_R17_claims.py::test_R17_the_sign_arm_is_warm_up_independent_by_an_exact_paired_test PASSED [ 33%]
tests/test_R17_claims.py::test_R17_the_persistence_collapse_of_L341_reproduces PASSED [ 36%]
tests/test_R17_claims.py::test_R17_the_false_alarm_restoration_of_L341_reproduces PASSED [ 40%]
tests/test_R17_claims.py::test_R17_the_published_cell_carries_corner_solutions_the_convergence_flag_does_not_see PASSED [ 43%]
tests/test_R17_claims.py::test_R17_the_four_numerals_of_L341_do_not_reproduce_at_their_printed_precision PASSED [ 46%]
tests/test_R17_claims.py::test_R17_the_definitional_gap_between_the_two_persistence_constructions_is_measured PASSED [ 50%]
tests/test_R17_claims.py::test_R17_the_uncalibrated_and_recalibrated_arms_coincide_at_unit_penalty PASSED [ 53%]
tests/test_R17_claims.py::test_R17_the_sign_arm_is_constant_wherever_the_key_omits_the_grid_coordinate PASSED [ 56%]
tests/test_R17_claims.py::test_R17_the_misspecification_table_is_a_control_and_not_L349 PASSED [ 60%]
tests/test_R17_claims.py::test_R17_the_legacy_arm_reproduces_the_deterministic_content_of_the_witness PASSED [ 63%]
tests/test_R17_claims.py::test_R17_the_two_option_arms_differ_only_where_the_optimiser_reaches PASSED [ 66%]
tests/test_R17_claims.py::test_R17_the_legacy_artefacts_declare_that_they_certify_no_published_value PASSED [ 70%]
tests/test_R17_claims.py::test_R17_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix PASSED [ 73%]
tests/test_R17_claims.py::test_R17_every_produced_text_file_ends_in_a_newline PASSED [ 76%]
tests/test_R17_claims.py::test_R17_the_produced_sources_and_logs_carry_no_confirmatory_language PASSED [ 80%]
tests/test_R17_claims.py::test_R17_the_produced_sources_carry_no_banned_construct PASSED [ 83%]
tests/test_R17_claims.py::test_R17_every_square_root_of_a_sample_size_follows_a_design_effect PASSED [ 86%]
tests/test_R17_claims.py::test_R17_report_the_campaign_against_its_witness PASSED [ 90%]
tests/test_R17_claims.py::test_R17_report_the_three_term_decomposition_of_the_persistence_gap PASSED [ 93%]
tests/test_R17_claims.py::test_R17_report_the_sign_arm_over_the_warm_up_axis PASSED [ 96%]
tests/test_R17_claims.py::test_R17_report_the_convergence_diagnostics_at_every_cell PASSED [100%]

============================== 30 passed in 1.10s ==============================
```

Total: 30 passed.

## 4. Reproducibility digests

From exp_R17_econometric_baseline.log (worker count: 1, serial):
- SHA-256 R17_fpr_baseline.csv: c266a3411c102e6fbc753f2ff26a9e6665e7e3609ed509ffd9f1a25d3bc487f1 (line 252)
- SHA-256 R17_add_baseline.csv: 27907f6ada17ea6414670ed25fd85f7ea01b20d6fc0a5afdc1bed2a2705e8185 (line 253)
- SHA-256 R17_fpr_arms.csv: 931f1494165d361b35690dc3fba99a19157e6c755aca09255324f033eadf1580 (line 254)
- SHA-256 R17_misspecification.csv: 30de1e905a4e48bc87fccd23538188283ad3e6a3e7d4db31ab9329f32197538d (line 255)
- SHA-256 R17_warmup_sensitivity.csv: 6deaf22dec59581e1a02ae35f5f4632efe30b0831bbe6be7d44d1843e12c7657 (line 256)
- SHA-256 R17_warmup_fits.csv: 6fa2a782c3cf8a97bd1fdec9886f2277196ce1ae380ce70f02f52f3c54dd5ff0 (line 257)
- SHA-256 R17_claims.tex: 6642dd0bd4b17dfcc2ede57af699d6f571bc856f9ffcb0fff60f8aa1bf2090d5 (line 258)

From exp_R17_econometric_baseline_legacy_qmle.log (worker count: 1, serial):
- SHA-256 R17_fpr_baseline_legacy_qmle.csv: c266a3411c102e6fbc753f2ff26a9e6665e7e3609ed509ffd9f1a25d3bc487f1 (line 253)
- SHA-256 R17_add_baseline_legacy_qmle.csv: 120e79cdeafb9b0fd85047af67427652fecb93ed55be36e3321769fdb9fd09d2 (line 254)
- SHA-256 R17_fpr_arms_legacy_qmle.csv: 931f1494165d361b35690dc3fba99a19157e6c755aca09255324f033eadf1580 (line 255)
- SHA-256 R17_misspecification_legacy_qmle.csv: 30de1e905a4e48bc87fccd23538188283ad3e6a3e7d4db31ab9329f32197538d (line 256)
- SHA-256 R17_warmup_sensitivity_legacy_qmle.csv: 247f5709d5e7f2c041058d7e99a561059a700879258d838c58dceb42748860e0 (line 257)
- SHA-256 R17_warmup_fits_legacy_qmle.csv: 567a9171534fef0abc3c091845148230061184b6ff59abd564cfcb5833f7fc0e (line 258)
- SHA-256 R17_claims_legacy_qmle.tex: 7fdf3d193db26206e0a913517bd9c2d36f258e54ca812287f2b0ee04cdd8da16 (line 259)

Current tree, single run:
```
$ sha256sum results/R17_econometric_baseline/data/*.csv results/R17_econometric_baseline/tables/*.tex
27907f6ada17ea6414670ed25fd85f7ea01b20d6fc0a5afdc1bed2a2705e8185  results/R17_econometric_baseline/data/R17_add_baseline.csv
120e79cdeafb9b0fd85047af67427652fecb93ed55be36e3321769fdb9fd09d2  results/R17_econometric_baseline/data/R17_add_baseline_legacy_qmle.csv
931f1494165d361b35690dc3fba99a19157e6c755aca09255324f033eadf1580  results/R17_econometric_baseline/data/R17_fpr_arms.csv
931f1494165d361b35690dc3fba99a19157e6c755aca09255324f033eadf1580  results/R17_econometric_baseline/data/R17_fpr_arms_legacy_qmle.csv
c266a3411c102e6fbc753f2ff26a9e6665e7e3609ed509ffd9f1a25d3bc487f1  results/R17_econometric_baseline/data/R17_fpr_baseline.csv
c266a3411c102e6fbc753f2ff26a9e6665e7e3609ed509ffd9f1a25d3bc487f1  results/R17_econometric_baseline/data/R17_fpr_baseline_legacy_qmle.csv
30de1e905a4e48bc87fccd23538188283ad3e6a3e7d4db31ab9329f32197538d  results/R17_econometric_baseline/data/R17_misspecification.csv
30de1e905a4e48bc87fccd23538188283ad3e6a3e7d4db31ab9329f32197538d  results/R17_econometric_baseline/data/R17_misspecification_legacy_qmle.csv
6fa2a782c3cf8a97bd1fdec9886f2277196ce1ae380ce70f02f52f3c54dd5ff0  results/R17_econometric_baseline/data/R17_warmup_fits.csv
567a9171534fef0abc3c091845148230061184b6ff59abd564cfcb5833f7fc0e  results/R17_econometric_baseline/data/R17_warmup_fits_legacy_qmle.csv
6deaf22dec59581e1a02ae35f5f4632efe30b0831bbe6be7d44d1843e12c7657  results/R17_econometric_baseline/data/R17_warmup_sensitivity.csv
247f5709d5e7f2c041058d7e99a561059a700879258d838c58dceb42748860e0  results/R17_econometric_baseline/data/R17_warmup_sensitivity_legacy_qmle.csv
6642dd0bd4b17dfcc2ede57af699d6f571bc856f9ffcb0fff60f8aa1bf2090d5  results/R17_econometric_baseline/tables/R17_claims.tex
7fdf3d193db26206e0a913517bd9c2d36f258e54ca812287f2b0ee04cdd8da16  results/R17_econometric_baseline/tables/R17_claims_legacy_qmle.tex
```

## 5. Design decisions taken outside the plan

1. The arbitration of this stream is compliance, not invariance: the delivered fit_garch_qmle calls minimize with no tol, no ftol, no eps and no output truncation, in contravention of SPECS 1.10; 1.10 is applied on the `specs` arm, the displacement is measured, and the `legacy` arm attributes it (exp_R17_econometric_baseline.log:8-9).
2. The legacy-QMLE arm restores the delivered optimiser call verbatim, every output is stamped `_legacy_qmle`, and this arm certifies NO v87 value; it is executed UNCONDITIONALLY by run_experiment_R17.sh to isolate the SPECS 1.10 displacement at a common draw (exp_R17_econometric_baseline_legacy_qmle.log:10).
3. C9 reproducibility check is declared NON-APPLICABLE: the prompt's C9 asks for two executions at DIFFERENT WORKER COUNTS, but this script is serial and creates no process pool, no thread pool and no worker (exp_R17_econometric_baseline.log:259).

## 6. Open questions, left open

None recorded.
