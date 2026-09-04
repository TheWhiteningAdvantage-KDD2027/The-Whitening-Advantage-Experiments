# R07 — Audit Report: Whitening Under an Estimated Conditional Mean

This audit report documents the reproducibility verification of stream R07 (slug `R07_estimated_mean`).

Environment recorded by the run: Python 3.12.9, numpy 1.26.4, pandas 2.3.2, scipy 1.16.2, statsmodels 0.14.5, matplotlib 3.10.6 (log L2-L7). `PYTHONHASHSEED` pinned to 42 before interpreter start (log L1).

---

## 1. Deviation table (D0-D3)

| quantity | manuscript value | regenerated value | severity | source CSV cell | log line |
| --- | --- | --- | --- | --- | --- |
| L308 Ljung-Box rejection at phi = 0, NAIVE | 0.051 | 0.0492 | D2 | R07_estmean_lb_fpr.csv :: lb_reject_rate, NAIVE, phi=0 (CSV line 2) | not in the log |
| L308 Ljung-Box rejection at phi = 0.15, NAIVE | 0.998 | 0.9979 | D1 | R07_estmean_lb_fpr.csv :: lb_reject_rate, NAIVE, phi=0.15 (CSV line 38) | not in the log |
| L308 / Fig. 7 (B) Concept FPR at phi = 0.15, NAIVE | 0.208 | 0.21 | D2 | R07_estmean_lb_fpr.csv :: fpr_concept, NAIVE, phi=0.15 (CSV line 38) | not in the log |
| L308 OLS Ljung-Box envelope, low end | 0.046 | 0.047 | D2 | R07_estmean_lb_fpr.csv :: lb_reject_rate, min over the 28 OLS cells, phi=0.075, OLS-250 (CSV line 23) | not in the log |
| L308 OLS Ljung-Box envelope, high end | 0.056 | 0.0563 | D1 | R07_estmean_lb_fpr.csv :: lb_reject_rate, max over the 28 OLS cells, phi=0.02, OLS-1000 (CSV line 13) | not in the log |
| L308 OLS Concept FPR envelope, low end | 0.043 | 0.0484 | D2 | R07_estmean_lb_fpr.csv :: fpr_concept, min over the 28 OLS cells, phi=0, OLS-125 (CSV line 4) | not in the log |
| L308 OLS Concept FPR envelope, high end | 0.059 | 0.0561 | D2 | R07_estmean_lb_fpr.csv :: fpr_concept, max over the 28 OLS cells, phi=0.15, OLS-500 (CSV line 42) | not in the log |
| L308 eta RMSE over sigma_unc at n = 125 | 0.114 | 0.11482335030427646 | D2 | R07_estmean_diagnostics.csv :: eta_rmse_over_sigma, phi=0.15, n_ols=125 (CSV line 26) | not in the log |
| L308 bias bound, max abs(E[phi_hat] - phi) over the 28 diagnostic cells | < 0.0029 | 0.0031268677484383445 | D3 | R07_estmean_diagnostics.csv :: bias_phi_hat, phi=0.15, n_ols=125 (CSV line 26) | L350, L351 |
| L308 dispersion cost, points of rejection | 0.4 | no reading returns 0.4; the six enumerated readings span 0.63 to 0.93 points | D2 | R07_estmean_lb_fpr.csv :: lb_reject_rate over the 28 OLS and 7 ORACLE cells | not in the log |
| L308 fourth-moment product E[(alpha z^2 + beta)^2] | 1.005 | 1.00517456 | D0 | R07_eta_scaling_counterfactual.csv :: moment_product, dgp_arm=t7_garch (CSV line 2) | L348 |
| L241 lambda* under L241's own selection rule | 11.4 | 11.4 | D0 | R07_lattice_exact_law.csv :: lambda_value, record_type=exact_survival, lambda_units=57 (CSV line 9) | not in the log |
| L241 level bracketing 5% at lambda = 11.4 | 0.0429 (2x10^5 fair-coin streams) | 0.043428228893176074 (exact law) | D2 | R07_lattice_exact_law.csv :: exact_level, lambda_units=57 (CSV line 9) | not in the log |
| L241 level bracketing 5% at lambda = 11.2 | 0.0503 (2x10^5 fair-coin streams) | 0.051020717214682557 (exact law) | D2 | R07_lattice_exact_law.csv :: exact_level, lambda_units=56 (CSV line 8) | not in the log |

Count by severity: D0: 2, D1: 2, D2: 9, D3: 1.

**Falsified qualitative claim (L308).** The manuscript states that the systematic channel — "the classical small-sample AR bias E[phi_hat] - phi approx -2.5 phi/n" — **stays under 2.9 x 10^-3** across the full 7 x 4 grid. It does not. The largest absolute bias over the 28 diagnostic cells is 0.0031268677484383445, with a standard error of 0.00015754882900151143, at phi = 0.15 and n_ols = 125: **+1.44 standard errors past the printed bound**, and +0.81 standard errors past the 0.003 that the manuscript's own -2.5 phi/n approximation predicts at that same corner (log L350; `pytest -q -s`, `test_R07_the_bias_bound_of_L308_is_exceeded_by_the_regenerated_campaign`). The maximising cell is the corner the printed formula itself designates — largest phi, shortest window — so the extremum is structurally located and not a stochastic excursion (log L350). The log classifies the violation at L351 (`ERROR | D3 CANDIDATE. Bound violation authenticated.`). The printed formula already exceeds the printed bound on its own terms: -2.5 x 0.15 / 125 = -3.0 x 10^-3 is larger in magnitude than the 2.9 x 10^-3 written eleven words later.

**Scope:** the falsification is confined to the numeral `2.9 x 10^-3` and to the word "stays under" in L308. It does **not** touch: the ordering of the channels (systematic bias remains three orders of magnitude below the momentum coefficients it estimates); Figure 7 panel A or panel B, neither of which plots the bias; the OLS-versus-ORACLE false-alarm comparison, where the widest gap over the 28 cells is 1.41 paired standard errors against a 4.0 band (`pytest -q -s`, `test_R07_every_ols_cell_matches_the_oracle_band_of_the_figure7_caption`); the lattice law; or the `-2.5 phi/n` approximation itself, which R07 measures against but does not test. The camera-ready correction is staged, unapplied, in `docs/camera_ready_candidates/R07_v87_bias_bound.md` (`R07-bias-bound-not-a-bound`), which also owns the `2.5` constant of L308 that R08 cites without emitting a macro of its own.

**Where the severities come from.** The log classifies exactly one quantity, the bias bound (L350, L351). Every other severity in the table above is assigned here, from the CSV cell named in its own row against the manuscript value transcribed literally from `articleB_whitening_v87.tex` in `tests/test_R07_claims.py` L48-L73. The manuscript is frozen and is not present in this repository; that transcription and the parked camera-ready candidates are the citable record of what it prints.

**Cross-stream note on L241.** The two L241 rows above record R07's **exact** absorbing-chain law against the Monte-Carlo numerals L241 prints; they are not a redraw of L241's campaign, which R07 does not re-run. `docs/audits/AUDIT_R08.md` carries a D3 of its own at L241 — the level the selection rule delivers at lambda* under the implemented weak operator, 0.051020717214682557 exact — and R07's control C1 (iv) is the measurement that identifies that operator. R07 opens no row and no register entry on L241 by declared ownership (`docs/camera_ready_candidates/R07_v87_lattice_handoff_to_R08.md`), so the single falsification is counted once, in R08. The two streams agree numerically: see control C1 (i)-(ii) below.

---

## 2. Controls

### C5 Source identity of the carried primitives
What it tests: the 7 primitives R07 carries from the submitted script align byte-for-byte with the witness. They are `wilson_ci` (the score interval of a rejection rate), `lb_pvalue`, `compute_phi_hat_naive`, `compute_phi_hat_vectorized`, `cusum_concept_fast`, `check_anti_look_ahead` and `generate_dgp`, compared against `Priority_21_estimated_mean_robustness.py`, 4119 internal characters mapped (log L8). Three routines are declared ADAPTED (`calibrate_and_validate`, `worker`, `plot_results`) and two SUPERSEDED (`verify_checks`, `main`); byte parity is not assertable on those five, so each witness transcript is reproduced in full in the log with its own SHA-256 (log L9-L10; hashes at L11, L33, L79, L159, L203; transcripts at L12-L32, L34-L78, L80-L158, L160-L202, L204-L333). Trigger probability: 0 (log L8, verbatim). Realised margin: byte comparison, no sampling distribution. Verdict: PASSED.

### C1 (iii) Operator identity, by AST
What it tests: every exceedance test routes through the single helper `exceeds`. Of the 101 relational operations in `exp_R07_estimated_mean.py`, only the 3 whitelisted endpoints may order a threshold against anything (log L334). Trigger probability: 0 (log L334, verbatim). Realised margin: deterministic AST walk, no sampling distribution. Verdict: PASSED.

### C1 (i)-(ii) The exact lattice law and the derivation of lambda*
What it tests: an absorbing-chain forward recursion over the 2delta = 0.2 lattice at H = 5000 returns P(M_H > lambda) with no entropy consumed, and lambda* is then fixed by L241's own stated rule — the nearest attainable level at or below nominal — applied to that law rather than to a sample quantile (log L335-L337; `results/R07_estimated_mean/tables/R07_claims.tex` L4-L10). Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: against exhaustive enumeration of all 2^H sign paths at H in (8, 10, 12) and lambda in (4, 5, 6, 7) lattice units, largest absolute difference 0.0 on 12 of 12 cells (`R07_lattice_exact_law.csv :: abs_difference`, record_type=enumeration_validation, CSV lines 18-29). An independently written explicit transition matrix re-derives the same law inside a 4 H eps = 4.44e-12 tolerance; that tolerance is the stated bound on the one convex combination whose associativity differs between the two programs (`tests/test_R07_claims.py` L80-L86 and `test_R07_the_lattice_law_reproduces_under_an_independent_dynamic_program`). Verdict: PASSED. Cross-stream concordance: `docs/audits/AUDIT_R08.md` control C2a scans 16 lattice points at H = 5000 against R07's cells and reports 16 of 16 in bit-for-bit agreement, largest absolute difference 0.0. The four exact levels R08 quotes at L234 of its audit — strict(11.2) = 5.1021%, weak(11.2) = 5.9900%, strict(11.4) = 4.3428%, weak(11.4) = 5.1021% — are the values carried by `R07_lattice_exact_law.csv` at lambda_units 56, 55 and 57 (CSV lines 8, 7, 9). No divergence.

### C1 (iv) Boundary artefact: which comparison the implementation performs
What it tests: whether the implemented float test M > lambda* is the strict or the weak lattice comparison, measured on three fair-coin stream sets rather than assumed from L241's footnote (log L341-L343). Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: on the 10000 oracle_phi0 streams, the 20000 calibration streams and the 5000 validation streams, the implemented test coincides with the weak operator M >= lambda* on **every** stream — 0 disagreements — and differs from the strict operator M > lambda* on 88, 137 and 42 streams respectively (log L341-L343; `R07_lattice_exact_law.csv :: operator, realised_level, disagreements`, record_type=float_drift, CSV lines 30-38). The delivered levels are 0.0516, 0.0509 and 0.0496 under the implemented test against 0.0428, 0.04405 and 0.0412 under the strict one. Verdict: PASSED, and reported rather than gated: the finding is a property of this threshold, this horizon and this accumulation order, not a theorem, so no pass/fail boundary is attached to it.

### C2 Bit-identity of the NAIVE and ORACLE arms at phi = 0
What it tests: at phi = 0 the DGP's oracle correction mu = phi r_prev is identically zero, so the NAIVE and ORACLE arms must agree bit-for-bit on every trajectory (log L344). Trigger probability: 0 (log L344, verbatim). Realised margin: exact identity; the two cells carry lb_reject_rate 0.0492 and fpr_concept 0.0516 with identical Wilson score intervals on those two rejection rates (`R07_estmean_lb_fpr.csv`, CSV lines 2 and 3). Verdict: PASSED.

### C4 Design effect of every pooled quantity
What it tests: under the mandated re-keying all 42 cells evaluate the same 10000 innovation streams, so pooled intervals cannot be taken at face value; the Kish design effect is measured before any pooled interval is computed (log L345). Two blocking assertions accompany the measurement: the ORACLE block must be bit-identical across phi with rho_bar exactly 1.0, and its effective sample size must round to 10000.

| statistic | block | cells | rho_bar | design effect | n_eff | SE inflation |
| --- | --- | --- | --- | --- | --- | --- |
| lb_reject | ORACLE | 7 | 1.000000 | 7.0000 | 10000.00 | x2.6458 |
| lb_reject | NAIVE | 7 | 0.212703 | 2.2762 | 30752.77 | x1.5087 |
| lb_reject | OLS | 28 | 0.646430 | 18.4536 | 15173.18 | x4.2958 |
| lb_reject | ALL | 42 | 0.508607 | 21.8529 | 19219.43 | x4.6747 |
| fpr_concept | ORACLE | 7 | 1.000000 | 7.0000 | 10000.00 | x2.6458 |
| fpr_concept | NAIVE | 7 | 0.601519 | 4.6091 | 15187.30 | x2.1469 |
| fpr_concept | OLS | 28 | 0.657864 | 18.7623 | 14923.52 | x4.3316 |
| fpr_concept | ALL | 42 | 0.608450 | 25.9465 | 16187.18 | x5.0938 |

Source: `R07_design_effect.csv`, CSV lines 2-9. Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: the ORACLE block is bit-identical on both statistics (`columns_bit_identical=True`, CSV lines 2 and 6) and n_eff is 10000 exactly, against the 70000 observations a naive pooling would claim. Verdict: PASSED.

### C7 Degenerate-path guards
What it tests: three preconditions of the asymptotic arguments, on all 420000 evaluated streams.
- Guard 1: no constant boolean sequence, which would falsify the asymptotic distribution assumption
  of the Ljung-Box statistic (log L338). Trigger probability: the log states it "corresponds effectively to absolute zero" and gives no numeral; NOT RECOVERABLE FROM THE LOG as a value. Realised margin: 0 degenerate streams out of 420000.
- Guard 2: the rolling-OLS denominator does not collapse. Trigger probability: NOT RECOVERABLE FROM
  THE LOG. Realised margin: lowest observed value 0.5230538332313017, clearing the 1e-12 precision mask by a factor of 5.231e+11 (log L339).
- Guard 3: the GARCH recursion respects h[t] >= omega = 0.0008000000000000007. Trigger probability:
  0 (log L340, verbatim). Realised margin: empirical minimum 0.00781096854974395, i.e. 9.76 times omega. Verdict: PASSED on all three guards.

### C8 Candidate mechanism, and the counterfactual ladder
What it tests: whether the eta RMSE decay exponent departs from -0.5 because the squared GARCH innovation lacks finite variance. The closed-form leg gives E[z^4] = 3(nu - 2)/(nu - 4) = 5.0 and E[(alpha z^2 + beta)^2] = 1.00517456 > 1 (log L348). The empirical leg runs three counterfactual DGP arms — t7_garch, gauss_garch (fourth moment alone), gauss_iid (volatility clustering alone) — at 2000 trajectories each (`R07_eta_scaling_counterfactual.csv`, CSV lines 2-7). Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: the exponents are -0.4413 +/- 0.0027 (t7_garch), -0.4594 +/- 0.0025 (gauss_garch) and -0.5193 +/- 0.0024 (gauss_iid); no arm's interval contains -0.5. The campaign's own pooled exponent is -0.4377698923005062 with 95% interval [-0.4400612105098945, -0.43547857409111795], +53.2 standard errors from -0.5 (`R07_eta_scaling.csv :: scope=pooled`, CSV line 9). Verdict: **the cause is NOT IDENTIFIED** (log L349, verbatim). This control is a reported measurement and not a gate, and it was written that way: the pre-registered criteria admit "not identified" as an outcome, and the log states that the confounding persistence factor alpha + beta = 0.98 might erode the effective sample capacity symmetrically, so attribution to the fourth moment is a hypothesis the ladder does not settle (log L348-L349). What the ladder does fix is negative and sufficient for the figure: the decay is not 1/sqrt(n), so panel B cannot be read as a window-size effect (log L349).

### C3 Ljung-Box calibration across the family
What it tests: the 42 binomial p-values of `lb_pvalue_binom` against Uniform(0,1) by KS, and the widest paired OLS-minus-ORACLE Ljung-Box rejection-rate gap against a sign-flip null over the 28 cells (`exp_R07_estimated_mean.py`, `control_c3_ljungbox_calibration`). Log record: **none.** The control emits no INFO line; it logs only on failure, and it did not fail. Trigger probability: NOT RECOVERABLE FROM THE LOG. The code computes the family-wise figure as 1 - (1 - 0.05)^42 for the 42 marginal tests but does not write it to the log. Realised margin: the widest OLS-versus-ORACLE gap over the 28 cells is 1.41 paired standard errors against a band of 4.0, and NAIVE at phi = 0.15 sits at 34.2 standard errors on the same scale (`pytest -q -s`, `test_R07_every_ols_cell_matches_the_oracle_band_of_the_figure7_caption`). The 4-sigma band carries an asymptotic family-wise trigger probability of 1 - (1 - 6.334e-5)^28 = 0.177%, derived and stated at `tests/test_R07_claims.py` L91-L94. Verdict: PASSED, on the evidence of the test suite; the run log carries no line for it.

### C9 Bootstrap envelope of the OLS extrema
What it tests: an extremum over 28 correlated cells has no per-cell binomial null, so the minimum and the maximum of the OLS grid are given a trajectory-resampling envelope instead of an interval (`exp_R07_estimated_mean.py`, `control_c9_envelope_null_law`; `R07_claims.tex` L13-L14, L23-L24). Log record: **none.** The control emits no INFO line; its output reaches the LaTeX header only. Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin, copied from `results/R07_estimated_mean/tables/R07_claims.tex` L23-L24: Ljung-Box rejection-rate minimum 95% [4.260%, 5.020%], maximum 95% [5.260%, 6.150%]; Concept FPR minimum 95% [4.390%, 5.220%], maximum 95% [5.260%, 6.130%]. These are bootstrap envelopes of an extremum, not Wilson intervals of a per-cell rejection rate. Verdict: PASSED — the control asserts that the bootstrap point estimates reproduce the frame's own extrema before the envelope is quoted, and did not fire.

### Gates demoted to reported measurements
1. **The bias bound.** The submitted script gated on `max_bias < 2.9e-3` (witness transcript of
   `main`, log L325) — a literal read off the output that same run had just produced. R07 replaces the gate with `classify_bias_bound`, which measures the extremum, its standard error and its distance from both the printed bound and the printed approximation, and classifies the result (log L350-L351). Reason, as the log states it: the archaic certification blocks relied on non-robust hardcoded bounds (log L10). Had the gate been kept, this run would have aborted at `sys.exit(1)` and the D3 would have been invisible.
2. **The submitted Controls (b) and (c).** The same witness `main` gated on four campaign literals
   — 0.0509, 0.4984, 0.9979, 0.2076 — and on OLS bounds 0.0461/0.0557 and 0.0428/0.0586 (log L311-L322). Those are cells of the submitted campaign, not manuscript claims; under any re-keying they cannot hold, and they are superseded by the C-series controls above (log L10).
3. **The calibration check (d).** The witness accepted a validation FPR in [0.043, 0.057] against a
   nominal 0.05 (log L30). R07 instead evaluates the binomial p-value of every cell against the empirically delivered CUSUM level of 0.05064, measured on 25000 independent calibration and validation streams, because the nominal 0.05 is not attainable on this lattice (log L346).

---

## 3. Test suite

```
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-9.0.3, pluggy-1.6.0 -- /home/m53/miniforge3/envs/Trading/bin/python
cachedir: .pytest_cache
rootdir: /home/m53/The-Whitening-Advantage-Experiments
plugins: anyio-4.8.0
collecting ... collected 28 items

tests/test_R07_claims.py::test_R07_every_artefact_the_plan_lists_exists_with_its_prescribed_schema PASSED [  3%]
tests/test_R07_claims.py::test_R07_the_lattice_law_reproduces_under_an_independent_dynamic_program PASSED [  7%]
tests/test_R07_claims.py::test_R07_the_two_attainable_levels_bracket_five_percent_and_fix_lambda_star PASSED [ 10%]
tests/test_R07_claims.py::test_R07_the_dynamic_program_agrees_with_exhaustive_enumeration PASSED [ 14%]
tests/test_R07_claims.py::test_R07_the_fourth_moment_product_of_L308_reproduces_in_closed_form PASSED [ 17%]
tests/test_R07_claims.py::test_R07_every_wilson_interval_is_the_score_interval_of_its_own_rate PASSED [ 21%]
tests/test_R07_claims.py::test_R07_the_naive_arm_and_the_oracle_arm_coincide_at_phi_zero PASSED [ 25%]
tests/test_R07_claims.py::test_R07_the_oracle_arm_is_exactly_phi_invariant PASSED [ 28%]
tests/test_R07_claims.py::test_R07_the_design_effect_is_measured_on_every_pooled_quantity PASSED [ 32%]
tests/test_R07_claims.py::test_R07_the_ljungbox_rejection_of_L308_climbs_monotonically_in_phi PASSED [ 35%]
tests/test_R07_claims.py::test_R07_every_ols_cell_matches_the_oracle_band_of_the_figure7_caption PASSED [ 39%]
tests/test_R07_claims.py::test_R07_the_ols_envelopes_stay_inside_the_two_bands_L308_prints PASSED [ 42%]
tests/test_R07_claims.py::test_R07_the_macro_file_is_a_bare_newcommand_list_under_the_cardinal_prefix PASSED [ 46%]
tests/test_R07_claims.py::test_R07_the_macros_agree_with_the_frames_they_are_computed_from PASSED [ 50%]
tests/test_R07_claims.py::test_R07_every_produced_text_file_ends_in_a_newline PASSED [ 53%]
tests/test_R07_claims.py::test_R07_the_produced_sources_and_logs_carry_no_confirmatory_language PASSED [ 57%]
tests/test_R07_claims.py::test_R07_the_produced_sources_carry_no_banned_construct PASSED [ 60%]
tests/test_R07_claims.py::test_R07_the_comparison_operator_is_the_same_on_both_paths PASSED [ 64%]
tests/test_R07_claims.py::test_R07_the_seven_carried_primitives_are_byte_identical_to_the_witness PASSED [ 67%]
tests/test_R07_claims.py::test_R07_the_three_monte_carlo_numerals_of_L308_move_within_their_own_sampling_error PASSED [ 71%]
tests/test_R07_claims.py::test_R07_the_bias_bound_of_L308_is_exceeded_by_the_regenerated_campaign PASSED [ 75%]
tests/test_R07_claims.py::test_R07_the_exact_lattice_levels_differ_from_the_two_numerals_v87_prints PASSED [ 78%]
tests/test_R07_claims.py::test_R07_the_eta_decay_is_not_one_over_root_n PASSED [ 82%]
tests/test_R07_claims.py::test_R07_report_the_campaign_against_its_witness PASSED [ 85%]
tests/test_R07_claims.py::test_R07_report_the_design_effect_of_every_pooled_quantity PASSED [ 89%]
tests/test_R07_claims.py::test_R07_report_the_counterfactual_ladder PASSED [ 92%]
tests/test_R07_claims.py::test_R07_report_the_candidate_readings_of_the_dispersion_cost_numeral PASSED [ 96%]
tests/test_R07_claims.py::test_R07_report_the_float_drift_on_the_lattice_boundary PASSED [100%]

======================== 28 passed in 107.91s (0:01:47) ========================
```

Total for the whole suite: NOT RECOVERABLE FROM THE LOG. `logs/R07_estimated_mean/exp_R07_estimated_mean.log` records no pytest invocation, and `logs/all_tests.log` predates this stream's test file — its `120 passed in 1.08s` (L188) collects no `tests/test_R07_claims.py` item.

---

## 4. Reproducibility digests

The log carries **one** manifest, at L353-L366. Number of workers of that run: NOT RECOVERABLE FROM THE LOG — `exp_R07_estimated_mean.py` takes `--n-jobs` with `os.cpu_count()` as its default and writes neither the flag nor the resolved count to the log.

First run (workers not recorded, log L353-L366):
```
R07_estmean_lb_fpr.csv              [f8321f6421b069570935531ee05ba33eadd57bf0dcf76c662170c5f94c32c77f]
R07_estmean_diagnostics.csv         [a2e1bbefba9696d552cbaf75c624803e6708b0e9f58befd022d1861b6a5a39eb]
R07_lattice_exact_law.csv           [22b2da85c2f140b32dcab32f001418f6cf373654cb214e984cd2529d58218e06]
R07_design_effect.csv               [a693e3378a5143115d45de6cbb7582cc2bb52f526c27e2d41b04d1866109745c]
R07_eta_scaling.csv                 [a9d4672b5775aaa328e74233e354abbd889828f1d9fe53320a6c8e54a4024a07]
R07_eta_scaling_counterfactual.csv  [955dc0b78e2988915389e6f1525e24e464a24c5ce541798c5acbf26f651f777a]
fig07_estimated_mean.png            [28a43eb8f32487a45eff9dc8d33c8e49405cfbd7382fe49f1a7881bc21898c73]
R07_claims.tex                      [476c36463ef5803c72e20a996e7590a759375e9639f1254031e25045388c0828]
```

Second run: NOT RECOVERABLE FROM THE LOG. No second manifest is recorded.

current tree, single run — `sha256sum results/R07_estimated_mean/data/*.csv results/R07_estimated_mean/tables/*.tex results/R07_estimated_mean/figures/*.png`:
```
a693e3378a5143115d45de6cbb7582cc2bb52f526c27e2d41b04d1866109745c  results/R07_estimated_mean/data/R07_design_effect.csv
a2e1bbefba9696d552cbaf75c624803e6708b0e9f58befd022d1861b6a5a39eb  results/R07_estimated_mean/data/R07_estmean_diagnostics.csv
f8321f6421b069570935531ee05ba33eadd57bf0dcf76c662170c5f94c32c77f  results/R07_estimated_mean/data/R07_estmean_lb_fpr.csv
a9d4672b5775aaa328e74233e354abbd889828f1d9fe53320a6c8e54a4024a07  results/R07_estimated_mean/data/R07_eta_scaling.csv
955dc0b78e2988915389e6f1525e24e464a24c5ce541798c5acbf26f651f777a  results/R07_estimated_mean/data/R07_eta_scaling_counterfactual.csv
22b2da85c2f140b32dcab32f001418f6cf373654cb214e984cd2529d58218e06  results/R07_estimated_mean/data/R07_lattice_exact_law.csv
476c36463ef5803c72e20a996e7590a759375e9639f1254031e25045388c0828  results/R07_estimated_mean/tables/R07_claims.tex
28a43eb8f32487a45eff9dc8d33c8e49405cfbd7382fe49f1a7881bc21898c73  results/R07_estimated_mean/figures/fig07_estimated_mean.png
```

All eight digests of the current tree reproduce the manifest the log recorded, byte for byte.

---

## 5. Design decisions taken outside the plan

1. lambda* is fixed by L241's own stated rule applied to the **exact** lattice law, not by the
   delivered sample quantile, which sits astride the lattice boundary (`R07_claims.tex` L4-L10). The value is unchanged, 11.4; what changes is which object the rule is applied to.
2. R07 computes the exact law but does **not** re-run L241's 2 x 10^5-stream Monte-Carlo. That
   campaign belongs to R08, and re-running it would put two competing CSV sources behind one published numeral (`R07_claims.tex` L6-L8; `docs/camera_ready_candidates/R07_v87_lattice_handoff_to_R08.md`).
3. The binomial p-value of each false-positive rate is evaluated against the empirically delivered
   CUSUM level 0.05064, from 25000 independent calibration streams, rather than against the unattainable nominal 0.05 — evaluating against 5% would penalise the arms for lattice granularity (log L346).
4. Row order in the emitted frames follows the declared architectural order
   ('NAIVE', 'ORACLE', 'OLS-125', 'OLS-250', 'OLS-500', 'OLS-1000') and the window grid (125, 250, 500, 1000), not lexicographic sort (log L347).
5. The certification blocks of the submitted script were dropped and replaced by the dynamically
   parameterised C-series controls, because the originals gated on hardcoded literals the same run had produced (log L10; see "Gates demoted to reported measurements" above).
6. The two OLS pairs published as macros are **extrema** over the 28-cell grid. An extremum has no
   per-cell interval, so they carry the control C9 bootstrap envelope in the LaTeX header rather than a per-cell interval (`R07_claims.tex` L11-L14, L23-L24).
7. The eta exponent interval is computed from 10000 per-trajectory log-log fits, pooled over phi
   within each trajectory first, and carries no design-effect correction: the trajectory is the only i.i.d. unit of the design (`R07_claims.tex` L19-L21).
8. C1 (iv) measures which comparison operator the float implementation performs instead of inheriting
   the assertion from L241's footnote (log L341-L343).

---

## 6. Open questions, left open

1. Why does the eta RMSE decay exponent sit at -0.4378 rather than -0.5? Control C8's pre-registered
   ladder returns NOT IDENTIFIED: the fourth-moment reading (E[(alpha z^2 + beta)^2] = 1.005 > 1) and the persistence reading (alpha + beta = 0.98) are not separated by the arms that were run, and the protocol forbids adding arms after seeing the interim outcome (log L348-L349).
2. What quantity does the `0.4 points of rejection` of L308 measure? Six readings were enumerated in
   advance and logged by the pipeline; they return 0.71, 0.71, 0.71, 0.89, 0.63 and 0.93 points, and none rounds to 0.4 (`pytest -q -s`, `test_R07_report_the_candidate_readings_of_the_dispersion_cost_numeral`). The numeral is unlocatable in the submitted campaign as well as in this one, so the question is open against the manuscript, not against the redraw (`docs/camera_ready_candidates/R07_v87_dispersion_cost.md`).
3. Does the Figure 7 caption's phrase "exact lattice level" belong to the numerals it qualifies?
   L241 sources the same two numerals to a Monte-Carlo. R07 owns the caption but not the numerals, and the two possible repairs — change the word, or change the numerals — sit in different streams (`docs/camera_ready_candidates/R07_v87_figure7_exactness.md`).
4. At which of the two attainable levels does Figure 7 panel B operate? C1 (iv) shows the
   implemented test is the weak comparison, whose exact level at lambda* equals the strict level at lambda = 11.2, i.e. above the 5% nominal that L241's selection rule promises; the caption names the level below it (`docs/camera_ready_candidates/R07_v87_panelB_operating_level.md`).
5. `docs/DEVIATIONS.md` section R07 classes this stream **D1** and states that all qualitative
   claims are preserved. The run log authenticates a bound violation and classes it D3 (log L350, L351), and `docs/camera_ready_candidates/R07_v87_dispersion_cost.md` refers to the neighbouring bias-bound candidate as "a D3" while that candidate's own header reads "Class A, D2" and its inner table reads D1. Which classification governs the register is unresolved, and this audit reports the divergence rather than reconciling it: the register and the candidate files are outside this document's perimeter.
6. Is R08's D3 at L241 and R07's C1 (iv) operator finding one falsification or two? R07 counts it
   once, in R08, on the ownership rule stated in the hand-off note. Nothing in either log settles whether a finding produced by one stream and published by another should be registered twice.

---

## Measured execution cost

Wall-clock span of the recorded run: 2026-08-22 04:40:08 to 2026-08-22 04:42:42, i.e. 154 seconds (log L1 and L367). Phase boundaries readable from the timestamps: source and operator controls plus the exact lattice law complete by 04:40:10 (log L337); the trajectory campaign and the C7 guards run to 04:42:31 (log L338); the remaining controls, the counterfactual ladder, the figure and the artefacts complete by 04:42:42 (log L352-L367). Number of workers: NOT RECOVERABLE FROM THE LOG.
