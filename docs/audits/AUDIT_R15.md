# Audit Report: R15 — Cross-Sectional Escape on Real Equity Panel

## 1. Deviation table (D0-D3)

| quantity | manuscript value | regenerated value | severity | source CSV cell | log line |
|----------|------------------|-------------------|----------|-----------------|----------|
| S3 [rho_sign, mean over K >= 5] | 0.26 at 2 decimals | 0.2610027270444267 | D1 | R15_panel_diagnostics.csv :: rho_sign_meas | exp_R15_cross_sectional_b.log:205 |
| S3 [K_eff_meas at K = 97] | 3.8 at 1 decimals | 3.7370099487341837 | D0 | R15_panel_diagnostics.csv :: K_eff_meas | exp_R15_cross_sectional_b.log:206 |
| S3 [FPR_boot minimum, percent] | 4.8 at 1 decimals | 3.95 | D2 | R15_panel_diagnostics.csv :: FPR_boot | exp_R15_cross_sectional_b.log:207 |
| S3 [FPR_boot maximum, percent] | 6.4 at 1 decimals | 5.8500000000000005 | D2 | R15_panel_diagnostics.csv :: FPR_boot | exp_R15_cross_sectional_b.log:208 |
| S3 [whiteness switch point] | 10 at 0 decimals | 10.0 | D0 | R15_panel_diagnostics.csv :: ljungbox_p_Pt | exp_R15_cross_sectional_b.log:209 |
| S3 [budget reduction plateau, c = 0.25, K >= 20] | 2.0 at 0 decimals | 2.0299065255254365 | D1 | R15_cross_sectional_race.csv :: budget_reduction | exp_R15_cross_sectional_b.log:210 |
| S3 [scatter correlation |r| at c = 0.25] | 0.99 at 2 decimals | 0.9962104605839599 | D2 | R15_scatter_correlation.csv :: r_budget_vs_lambda_boot | exp_R15_cross_sectional_b.log:211 |
| S3 [COVID detections under the bootstrap threshold] | 0 at 0 decimals | 0.0 | D0 | R15_covid_natural.csv :: delay_boot | exp_R15_cross_sectional_b.log:212 |
| S3 [scatter correlation, SIGNED] | relation r >= 0.99 | -0.9962104605839599 | D2 | R15_scatter_correlation.csv :: r_budget_vs_lambda_boot | exp_R15_cross_sectional_b.log:214 |

Count by severity: D0=4, D1=3, D2=4, D3=0.

The D2 `R15-scatter-sign` falsifies the qualitative claim that the caption's relation `r >= 0.99` holds. The printed relation `r >= 0.99` is false at both signs on both the submitted campaign (witness -0.9893771840917368) and the regenerated campaign (regenerated -0.9962104605839599); the mirrored relation `r <= -0.99` is true. On absolute value, `|r| >= 0.99` holds for the regenerated campaign (0.9962) but fails for the submitted campaign (0.9894). The qualitative claim that the point-to-point scatter of panel B is almost entirely explained by variation in the bootstrap threshold holds on both campaigns; the falsification is of the printed relation only. Scope: v87 Figure 17 caption, line describing `r >= 0.99 with bootstrap threshold`. It does NOT touch the plateau magnitude, the effective panel size, or the whiteness switch point.

The D2 `S3 [FPR_boot minimum, percent]` and `S3 [FPR_boot maximum, percent]` shift the caption's envelope from 4.8-6.4% to 4.0-5.9%. The qualitative claim that the bootstrap calibration holds the level (all FPR_boot values lie inside the control (c) band (0.03, 0.07)) is preserved. Scope: v87 Figure 17 caption only.

## 2. Controls

### C1 — frozen composition fidelity
Fidelity of the frozen composition `assets_idx` against the witness Priorite_25c_real_cross_sectional_escape_UPDATED.py. The three statements that define the frozen composition are byte-identical to the witness at all 10 values of K, replayed by executing the witness's own statements. Trigger probability under its own null hypothesis: 0 (deterministic). Realised margin: bit-identical integer arrays at all K. Verdict: pass.

C1 leg 2: the 3 statements that define the frozen composition are byte-identical to Priorite_25c_real_cross_sectional_escape_UPDATED.py::run_real_experiment. Deterministic; trigger probability 0.

C1 leg 3: at all 10 values of K, the four RNG-free columns (rho_sign_meas, K_eff_meas, K_eff_ana, ljungbox_p_Pt) sit inside the mechanism-derived reordering bound T*K*eps. Worst realised relative difference per column: rho_sign_meas 3.214e-15 at K = 10, K_eff_meas 0.000e+00 (bit-identical at every K), K_eff_ana 2.367e-15 at K = 10, ljungbox_p_Pt 0.000e+00 (bit-identical at every K). The agreement is guaranteed by the frozen composition and is evidence of port fidelity alone. Trigger probability under its own null hypothesis: 0 (deterministic, mechanism-derived bound). Realised margin: all relative differences at or below the bound. Verdict: pass.

### C2 — consistency of the two K_eff estimators
Max relative gap |K_eff_meas - K_eff_ana| / K_eff_ana = 1.520598e-03 at K = 10. It is an extremum over a grid and therefore gates nothing (S4bis, fourth corollary). Its envelope is derived from SE(rho) ~ 1/sqrt(T) = 1.392925e-02, never from the observed gap: a one-SE move of rho displaces K_eff_ana by 5.194e-02 in relative terms at its widest (K = 75), so the measured gap sits at 0.0293 of one sampling standard error of the input it is a function of. Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: 1.520598e-03 relative. Verdict: reported, not gated.

### C3 — the uncertainty of FPR_boot
THE R15 PROMPT'S sqrt(2) RULE IS NOT IMPORTED. R04b established a variance doubling for n_cal = n_eval; here N_CAL = 20000 and N_RACE = 2000, so the first-order delta-method variance is p(1-p)/n_r + alpha(1-alpha)/n_c and the multiplier would be sqrt(1 + n_r/n_c) = 1.0488, not 1.4142. Preamble S4bis's fifth corollary forbids importing R04b's rule un-re-derived. NEITHER MULTIPLIER IS CORRECT ANYWAY: with only 3905 distinct windows the two sets are drawn from the SAME population and overlap in DATA by up to 1249 of 1250 days, so the uncertainty is not Monte-Carlo and no fixed multiplier produces it. What is published instead is SE = sqrt(deff_r * p(1-p)/n_r + deff_c * alpha(1-alpha)/n_c) with BOTH design effects measured on the t_start-ordered exceedance indicators. IT GATES NOTHING. Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: design-corrected SEs measured at each K. Verdict: reported, not gated.

### C4 — temporal whiteness of P_t
Ten Ljung-Box tests at lag 20. THE FAMILY-WISE ARITHMETIC, LOGGED BEFORE ANY INTERPRETATION: reading 10 independent tests at the 5% level as one verdict triggers with probability 1 - 0.95^10 = 0.401 = 40.1% under a true null of whiteness at every K. The publishable statistic is therefore the SWITCH POINT max{K : p >= 0.05}, which is RNG-free and reads one boundary rather than ten tests. Trigger probability under its own null hypothesis: 0.401. Realised margin: whiteness holds up to K = 10 and fails from K = 20 onward; p-values in K order: K=1: 9.8412e-01, K=5: 1.9465e-01, K=10: 1.4686e-01, K=20: 4.2705e-03, K=30: 2.6398e-04, K=40: 1.0865e-04, K=50: 3.7368e-04, K=60: 2.6181e-04, K=75: 1.9857e-04, K=97: 1.9778e-04. Verdict: descriptive only; switch point at K = 10.

C4 KS STATISTIC, DESCRIPTIVE AND NON-NULL-BEARING: D = 0.7053483714150465, p = 1.589494109493783e-05 against Uniform(0,1). IT IS NOT A TEST HERE AND GATES NOTHING. The ten p-values come from nested-in-distribution asset subsets of ONE panel over ONE common 5154-day index -- K = 5 is a subset of the same 97 series as K = 97 -- so they are strongly dependent and the Uniform(0,1) null does not hold even under perfect whiteness. Trigger probability: NOT RECOVERABLE FROM THE LOG.

### C5 — the plateau statistic
v87's Figure 17 caption says the realized budget reduction 'plateaus near 2x (K >= 20)'. The delivered script computes budget_reduction per (K, c) cell at line 311 AND AGGREGATES NOWHERE; the only selection of a magnitude in the whole file is the plotting line 378, `c_target = C_GRID[1]`, and lines 379-380 draw exactly one budget_reduction curve, at that c. With C_GRID = [0.1, 0.25, 0.5, 0.75, 1.0] that c is 0.25. THE PUBLISHED PLATEAU IS THEREFORE THE MEAN OF THE PLOTTED c = 0.25 SERIES OVER K >= 20. It is established by reading the plotting code, not selected among candidates. On the submitted campaign that mean is 2.0086. Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: regenerated plateau is 2.0299065255254365 over the 7 cells [20, 30, 40, 50, 60, 75, 97] at c = 0.25, with a delta-method standard error of 0.049935. Per-cell values: K=20: 2.0581, K=30: 1.9072, K=40: 1.7650, K=50: 2.2026, K=60: 2.0766, K=75: 2.1070, K=97: 2.0927. Verdict: the caption's literal reading -- 'bounded by the effective panel size K_eff' -- holds.

### C6 — no macro and no published aggregate reads a row with add_reliable == 0
2 of 50 cells are unreliable: [(1, 0.1, 0.6405), (5, 0.1, 0.738)]. Structural; trigger probability 0. Verdict: pass.

C6 EXTENDED, AND THE FLAG DOES NOT PROPAGATE. `add_reliable` describes the PANEL arm of a cell and says nothing about the REFERENCE arm its budget_reduction divides by. At c = [0.1] the reference arm itself detects at [0.6115], below the 0.9 floor, so ADD_single is CENSORED -- a mean over the detected subset of a cell that mostly does not detect -- and every one of the 8 cells inheriting it is nonetheless flagged reliable. This is REPORTED, not repaired: it does not touch the published c = 0.25 macro, whose reference arm detects at 0.9995. Trigger probability: NOT RECOVERABLE FROM THE LOG. Verdict: reported, not gated.

### C7 — the sentinel -1 is returned by `bilateral_delay` iff neither one-sided CUSUM crosses
C7: the sentinel -1 is returned by `bilateral_delay` iff neither one-sided CUSUM crosses, so it is a NON-DETECTION and never a delay of -1 day. It enters no mean anywhere in this file. lambda_boot is redrawn by the entropy migration, so this gate is live. Deterministic given the regenerated thresholds. Trigger probability under its own null hypothesis: 0. Realised margin: delay_boot == -1 at all 10 values of K, so the claim holds. Verdict: pass. The NAIVE threshold, by contrast, fires at 8 of 10 values of K ([5, 20, 30, 40, 50, 60, 75, 97]) -- those are FALSE ALARMS of a threshold that already runs at up to 100% false-alarm rate under the null, not detections, and no macro reads delay_naive.

### C8 — the design effect is a PREREQUISITE of every pooled reading
\RFifteenRhoSign pools 9 cells and the plateau pools 7. The mechanism makes EVERY PAIR of those cells dependent: all 10 compositions are subsets of ONE 97-asset panel over ONE common index, with a mean pairwise Jaccard overlap of 0.2235 (range [0.0000, 0.7732]) among the pooled cells, so the lag count is the full 8 and not a mechanism-derived subset. Kish deff over the K-ordered rho series: 1.000000 (clamped: True), i.e. 9.00 independent readings in 9 cells. CONSEQUENCE, APPLIED: \RFifteenRhoSign IS PUBLISHED AS A POINT STATISTIC WITH ITS DISPERSION AND NO INTERVAL -- min 0.253588, max 0.288102, sd 0.010425 -- because an interval over cells this dependent would advertise precision the design does not hold. Trigger probability: NOT RECOVERABLE FROM THE LOG. Verdict: reported, not gated.

### C9 — source identity
8 primitives byte-identical to the files that own them (2050 characters compared) -- strict_cusum, bilateral_delay, cusum_max_bilateral, wilson_ci (Wilson score interval for binomial proportions) and fraction_stream against Priorite_25c_real_cross_sectional_escape_UPDATED.py, and get_deterministic_seed, seed_sequence_for and rng_for against exp_R13_oracle_ceiling_a.py. Preamble S4.2 forbids hoisting any of them into experiments/common/: strict_cusum, bilateral_delay and wilson_ci all differ between this witness and the R01/R03/R04/R11/R13/R14 copies, so the duplication is deliberate. Deterministic; trigger probability 0 unless a copy has drifted.

C9 ADAPTED ROUTINES. ['worker_null_window_real', 'worker_race_h1_real'] cannot be byte-compared: each takes an injected generator where Priorite_25c_real_cross_sectional_escape_UPDATED.py builds one from an integer seed inside the function body. That is the ONLY line that differs in either. Trigger probability: NOT RECOVERABLE FROM THE LOG.

C9 SUPERSEDED routines: load_real_panel, run_experiment, run_real_experiment, setup_logger, simulate_panel, standardized_t, worker_boot_calib, worker_race_h0, worker_race_h1. All are superseded and pinned by digest. Trigger probability: NOT RECOVERABLE FROM THE LOG.

C9 REPORTED, NOT SETTLED: the R15 prompt's C9 names `simulate_panel` and `standardized_t` among the primitives to carry. Neither has a call site in scope. Both serve the `--source synthetic` branch alone, which produces Figure 29, and Figure 29 is not in v87. They are pinned by digest above and not quoted, which is preamble S4.2's treatment for a superseded routine; the over-specification is carried to docs/audits/AUDIT_R15.md as an open question.

### C10 — worker processes
Worker processes requested: 48. `executor.map` preserves submission order and every task is keyed, so no artefact depends on this number. Trigger probability under its own null hypothesis: NOT RECOVERABLE FROM THE LOG. Verdict: no dependency.

## 3. Test suite

```
============================= test session starts ==============================
platform linux -- Python 12.9, pytest-9.0.3, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /home/m53/The-Whitening-Advantage-Experiments
generated by /home/m53/miniforge3/envs/Trading/bin/python
collected 28 items

tests/test_R15_claims.py::test_R15_the_panel_is_the_one_v87_describes PASSED [  3%]
tests/test_R15_claims.py::test_R15_the_survival_chain_is_recounted_from_the_submitted_fetch_log PASSED [  7%]
tests/test_R15_claims.py::test_R15_the_k_one_degeneracy_is_an_identity_of_the_median_split PASSED [ 10%]
tests/test_R15_claims.py::test_R15_every_persisted_interval_is_a_wilson_interval_inside_the_unit_square PASSED [ 14%]
tests/test_R15_claims.py::test_R15_the_frozen_composition_is_the_delivered_one PASSED [ 17%]
tests/test_R15_claims.py::test_R15_the_sentinel_never_enters_a_mean PASSED [ 21%]
tests/test_R15_claims.py::test_R15_the_carried_primitives_are_byte_identical_to_the_files_that_own_them PASSED [ 25%]
tests/test_R15_claims.py::test_R15_no_draw_reaches_the_global_numpy_stream PASSED [ 28%]
tests/test_R15_claims.py::test_R15_every_square_root_of_a_sample_size_follows_a_design_effect PASSED [ 32%]
tests/test_R15_claims.py::test_R15_the_design_effect_is_computed_from_the_mechanism_and_never_below_one PASSED [ 35%]
tests/test_R15_claims.py::test_R15_the_numerals_of_L376_that_reproduce_do_reproduce PASSED [ 39%]
tests/test_R15_claims.py::test_R15_the_independence_calibration_loses_its_level_and_the_bootstrap_holds_one PASSED [ 42%]
tests/test_R15_claims.py::test_R15_no_aggregate_reads_a_cell_below_the_reliability_floor PASSED [ 46%]
tests/test_R15_claims.py::test_R15_the_effective_panel_saturates_and_the_two_estimators_agree PASSED [ 50%]
tests/test_R15_claims.py::test_R15_the_scatter_correlation_of_the_figure_caption_is_negative PASSED [ 53%]
tests/test_R15_claims.py::test_R15_the_bootstrap_fpr_envelope_of_the_caption_does_not_reproduce PASSED [ 57%]
tests/test_R15_claims.py::test_R15_the_sign_correlation_drifts_under_MKL_CBWR_and_not_otherwise PASSED [ 60%]
tests/test_R15_claims.py::test_R15_the_published_grid_is_declared_by_the_updated_witness_alone PASSED [ 64%]
tests/test_R15_claims.py::test_R15_every_artefact_the_plan_lists_exists_with_its_prescribed_schema PASSED [ 67%]
tests/test_R15_claims.py::test_R15_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix PASSED [ 71%]
tests/test_R15_claims.py::test_R15_the_witness_blas_artefacts_declare_that_they_certify_no_published_value PASSED [ 75%]
tests/test_R15_claims.py::test_R15_every_produced_text_file_ends_in_a_newline PASSED [ 78%]
tests/test_R15_claims.py::test_R15_the_produced_sources_and_logs_carry_no_confirmatory_language PASSED [ 82%]
tests/test_R15_claims.py::test_R15_the_produced_sources_carry_no_banned_construct PASSED [ 85%]
tests/test_R15_claims.py::test_R15_report_the_campaign_against_its_witness PASSED [ 89%]
tests/test_R15_claims.py::test_R15_report_the_design_effects_and_what_they_cost PASSED [ 92%]
tests/test_R15_claims.py::test_R15_report_the_two_readings_of_the_caption_correlation PASSED [ 96%]
tests/test_R15_claims.py::test_R15_report_the_marginal_channel_the_caption_does_not_name PASSED [100%]

============================== 28 passed in 0.85s ==============================
```

Total: 28 passed.

## 4. Reproducibility digests

Default arm (48 workers):
- SHA-256 R15_panel_diagnostics.csv                    : af306e051875a06af5f7c52c1e1f53411d8133916e30a8eaa4766f197ab7b639 (exp_R15_cross_sectional_b.log:215)
- SHA-256 R15_cross_sectional_race.csv                 : 7c0483a05b471f563b71ae4376b04103212fe2d405245c928b31a08e458b85ca (exp_R15_cross_sectional_b.log:216)
- SHA-256 R15_covid_natural.csv                        : 087636db3d8fc018895fd13702de408eb75a486fc7c31015319cb61eb79a7e7a (exp_R15_cross_sectional_b.log:217)
- SHA-256 R15_panel_composition.csv                    : 828d646f7204358480d90208f120214df7600294192f35d7314b18923a0e9503 (exp_R15_cross_sectional_b.log:218)
- SHA-256 R15_race_windows.csv                         : 610deddba45517e0c08dd8f9560103135c8b431a980a50e7db3090840ca0057d (exp_R15_cross_sectional_b.log:219)
- SHA-256 R15_scatter_correlation.csv                  : 13b16bdf8cd504f79b69c437ca111823c2f6179c25f04bd8d084f70012ed9e71 (exp_R15_cross_sectional_b.log:220)
- SHA-256 fig17_cross_section.png                      : 60837f64636bc71c8e1e032ca178152eefbb96a5a6585bd957844cddd43693be (exp_R15_cross_sectional_b.log:221)
- SHA-256 R15_claims.tex                               : 043d7e80ebfcfb0964ec21a0a4202d7b28cdecfa2c4c9d972d2618fdc2933993 (exp_R15_cross_sectional_b.log:222)

Witness-BLAS attribution arm (48 workers) (logs/R15_cross_sectional/exp_R15_cross_sectional_b_witness_blas.log:12):
- SHA-256 R15_panel_diagnostics_witness_blas.csv       : fdb311ff941eccc175cd21d803596c1193ac43d378d66d0b65357b06a6bce32a (exp_R15_cross_sectional_b_witness_blas.log:215)
- SHA-256 R15_cross_sectional_race_witness_blas.csv    : e12c876b5148526ee30e7606b171aa5f16f18081dd242bd7889a783070c10c44 (exp_R15_cross_sectional_b_witness_blas.log:216)
- SHA-256 R15_covid_natural_witness_blas.csv           : 087636db3d8fc018895fd13702de408eb75a486fc7c31015319cb61eb79a7e7a (exp_R15_cross_sectional_b_witness_blas.log:217)
- SHA-256 R15_panel_composition_witness_blas.csv       : 828d646f7204358480d90208f120214df7600294192f35d7314b18923a0e9503 (exp_R15_cross_sectional_b_witness_blas.log:218)
- SHA-256 R15_race_windows_witness_blas.csv            : 610deddba45517e0c08dd8f9560103135c8b431a980a50e7db3090840ca0057d (exp_R15_cross_sectional_b_witness_blas.log:219)
- SHA-256 R15_scatter_correlation_witness_blas.csv     : 1fb69fea76d2f66cfcc84adcc6d7af76345f63dd063969cd9ae18b63c462aa8c (exp_R15_cross_sectional_b_witness_blas.log:220)
- SHA-256 fig17_cross_section_witness_blas.png         : 60837f64636bc71c8e1e032ca178152eefbb96a5a6585bd957844cddd43693be (exp_R15_cross_sectional_b_witness_blas.log:221)
- SHA-256 R15_claims_witness_blas.tex                  : 8b60606a8cd5294b3bb5134ef27c2f8cdc2294905a1d521fa787579ca06fe0ac (exp_R15_cross_sectional_b_witness_blas.log:222)

Current tree, single run (includes witness-BLAS attribution arm files; see logs/R15_cross_sectional/exp_R15_cross_sectional_b_witness_blas.log:12):
```
087636db3d8fc018895fd13702de408eb75a486fc7c31015319cb61eb79a7e7a  data/R15_covid_natural.csv
e12c876b5148526ee30e7606b171aa5f16f18081dd242bd7889a783070c10c44  data/R15_cross_sectional_race_witness_blas.csv
828d646f7204358480d90208f120214df7600294192f35d7314b18923a0e9503  data/R15_panel_composition.csv
828d646f7204358480d90208f120214df7600294192f35d7314b18923a0e9503  data/R15_panel_composition_witness_blas.csv
fdb311ff941eccc175cd21d803596c1193ac43d378d66d0b65357b06a6bce32a  data/R15_panel_diagnostics_witness_blas.csv
af306e051875a06af5f7c52c1e1f53411d8133916e30a8eaa4766f197ab7b639  data/R15_panel_diagnostics.csv
610deddba45517e0c08dd8f9560103135c8b431a980a50e7db3090840ca0057d  data/R15_race_windows.csv
610deddba45517e0c08dd8f9560103135c8b431a980a50e7db3090840ca0057d  data/R15_race_windows_witness_blas.csv
13b16bdf8cd504f79b69c437ca111823c2f6179c25f04bd8d084f70012ed9e71  data/R15_scatter_correlation.csv
1fb69fea76d2f66cfcc84adcc6d7af76345f63dd063969cd9ae18b63c462aa8c  data/R15_scatter_correlation_witness_blas.csv
043d7e80ebfcfb0964ec21a0a4202d7b28cdecfa2c4c9d972d2618fdc2933993  tables/R15_claims.tex
8b60606a8cd5294b3bb5134ef27c2f8cdc2294905a1d521fa787579ca06fe0ac  tables/R15_claims_witness_blas.tex
```

## 5. Design decisions taken outside the plan

1. The K = 1 pairing the migration breaks: the delivered reference seed string `real_race1_1_{c}_{MASTER_SEED}_{i}` and the delivered panel seed string at K = 1 are the SAME STRING on the SAME sub-panel, so the submitted budget_reduction(K = 1) is exactly 1.0 BY CONSTRUCTION. The migrated keys ('race_h1', k_index, c_index, i) and ('race_h1_ref', c_index, i) separate the two roles, so the regenerated K = 1 cell is an honest estimate of 1 with sampling error: c=0.1: nan, c=0.25: 0.9901523419752389, c=0.5: 0.9986380991755636, c=0.75: 0.9785149389759195, c=1.0: 0.9964983545404819 (exp_R15_cross_sectional_b.log:146).

2. THE TWO CANDIDATE CEILINGS OF PANEL B, MEASURED: sqrt(K_eff) at K = 97 is 1.9331 and K_eff is 3.7370. Over the 10 plotted cells at c = 0.25, the realized budget reduction EXCEEDS sqrt(K_eff) at 6 of them ([20, 30, 50, 60, 75, 97]) and exceeds K_eff at 0. The caption's literal reading -- 'bounded by the effective panel size K_eff' -- therefore HOLDS, while the reference line the delivered figure actually draws does NOT bound the curve (exp_R15_cross_sectional_b.log:164).

3. THE CAPTION'S `K_eff ~ 3.8` IS 1/rho_hat AND NOT K_eff. L376 reads 'sign correlation rho_hat ~ 0.26 saturates the effective panel near 1/rho_hat ~ 3.8'. 1/rho_hat on this campaign is 3.8314, which rounds to 3.8; the MEASURED effective panel size at K = 97 is K_eff_meas = 3.7370, which rounds to 3.7. The two are different quantities -- 1/rho is the K -> infinity limit of K/(1+(K-1)rho) and K_eff is its value at a finite K -- and the gap is the finite-panel term, not a discrepancy (exp_R15_cross_sectional_b.log:175).

4. The window population is finite and small: H_ref + H_det = 1250 on T = 5154 days admits exactly 3905 distinct window starts. N_CAL = 20000 draws therefore enumerate that population about 5.1 times over, and two windows can share up to 1249 of their 1250 days. The calibration and evaluation sets are DISJOINT IN SEED and drawn from the SAME 3905 windows (exp_R15_cross_sectional_b.log:16).

5. GRID SOURCE: Priorite_25c_real_cross_sectional_escape_UPDATED.py declares the TEN-point grid at line 167 and is the artefact that fixes the survival chain. The published grid is therefore RECOVERED FROM A SOURCE LINE and is not read off the artefact (exp_R15_cross_sectional_b.log:65-67).

6. SPECIFICATION: H_ref=500, H_det=750 ('finite real panel: shorter horizon => more distinct, less-overlapping windows', delivered line 173), TARGET_FPR=0.05, N_CAL=20000, N_RACE=2000, MASTER_SEED=42, DET_RATE_FLOOR=0.9, K_GRID=[1, 5, 10, 20, 30, 40, 50, 60, 75, 97] (K_max read from the panel, never typed), C_GRID=[0.1, 0.25, 0.5, 0.75, 1.0], plotted c = C_GRID[1] = 0.25 (exp_R15_cross_sectional_b.log:14).

7. SPECIFICATION OF A BRANCH THIS PORT DOES NOT RUN: the delivered `--source synthetic` branch carries {'alpha': 0.08, 'beta': 0.9, 'nu': 7.0, 'H_det': 2000, 'K_GRID': (1, 50, 100, 200, 500), 'RHO_GRID': (0.0, 0.05, 0.1, 0.2, 0.3, 0.5)}. It produces Figure 29, which is NOT in v87, and the scope filter of this stream is strictly v87's content. The `--fast` branch is removed outright: a second grid is a second campaign and v87 publishes one (exp_R15_cross_sectional_b.log:15).

## 6. Open questions, left open

1. C9 REPORTED, NOT SETTLED: the R15 prompt's C9 names `simulate_panel` and `standardized_t` among the primitives to carry. Neither has a call site in scope. Both serve the `--source synthetic` branch alone, which produces Figure 29, and Figure 29 is not in v87. They are pinned by digest above and not quoted, which is preamble S4.2's treatment for a superseded routine; the over-specification is carried to docs/audits/AUDIT_R15.md as an open question (exp_R15_cross_sectional_b.log:64).

2. THE CAPTION'S ATTRIBUTION IS NOT TESTABLE BY THIS DESIGN. 'Point-to-point scatter reflects threshold variations across panel compositions' names COMPOSITIONS as the source. This design draws EXACTLY ONE composition per K, so moving along the abscissa changes K and the composition together and the two are confounded. No composition-resampling arm is added: v87 describes none and the scope filter excludes it. The caption is not false -- compositions do vary -- so no register entry is opened; it earns docs/camera_ready_candidates/R15_v87_scatter_attribution.md, headed NO DEVIATION (exp_R15_cross_sectional_b.log:182).

3. The R15 prompt's sqrt(2) RULE IS NOT IMPORTED. R04b established a variance doubling for n_cal = n_eval; here N_CAL = 20000 and N_RACE = 2000, so neither the sqrt(2) rule nor the sqrt(1 + n_r/n_c) = 1.0488 multiplier is correct because the window population is finite and the two sets overlap in data. What is published instead is SE = sqrt(deff_r * p(1-p)/n_r + deff_c * alpha(1-alpha)/n_c) with BOTH design effects measured. Is there a closed-form variance for overlapping window samples that would replace the measured deff?

4. The deff estimate for rho_sign over K >= 5 is clamped to 1.0 (0.299654 < 1). With only 9 observations, can a design effect below 1 be interpreted, or does it signal that the estimator is not appropriate for this statistic?

5. Multiple deff estimates for individual (K, c) cells are clamped to 1.0 (e.g., reference c=0.25: -4.214726, c=0.5: -3.654826). What is the correct interpretation of negative deff estimates in this context?
