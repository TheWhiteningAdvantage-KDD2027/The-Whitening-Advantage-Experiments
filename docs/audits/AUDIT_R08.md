# R08 — Audit Report: The Adverse Direction and the Discrete Null Law

This audit report documents the reproducibility verification of stream R08 (slug `R08_adverse_lattice`).

---

## 1. Deviation table (D0-D3)

| quantity                                                                     | manuscript value           | regenerated value                             | severity | source CSV cell                                                                                            | log line |
| ---------------------------------------------------------------------------- | -------------------------- | --------------------------------------------- | -------- | ---------------------------------------------------------------------------------------------------------- | -------- |
| Fig. 8 (B) FPR collapses to                                                  | 0.0086                     | 0.0095                                        | D2       | R08_adverse_bias.csv :: fpr_biased, b=0.15                                                                 | L171     |
| Fig. 8 (B) / L311 FPR inflates to                                            | 0.208                      | 0.21                                          | D2       | R07_estmean_lb_fpr.csv :: fpr_concept, NAIVE, phi=0.15                                                     | L172     |
| L241 level above nominal (lambda=11.2)                                       | 0.0503                     | 0.050815                                      | D2       | R08_null_law_lattice.csv :: P_exceed_strict, lambda=11.2                                                   | L173     |
| L241 level below nominal (lambda=11.4)                                       | 0.0429                     | 0.04323                                       | D2       | R08_null_law_lattice.csv :: P_exceed_strict, lambda=11.4                                                   | L174     |
| L241 lambda*                                                                 | 11.4                       | 11.4                                          | D0       | R08_null_law_lattice.csv :: bracket_role=below_nominal                                                     | L175     |
| L241 level delivered at lambda* = 11.4 under the implemented (weak) operator | <= 0.05 by the stated rule | 0.050815 measured, 0.051020717214682557 exact | D3       | R08_operator_levels.csv :: realised_level and exact_level, lambda=11.4, operator `exact M_units >= lambda` | L147-149 |
| L311 whiteness gap bound (points)                                            | 3.0                        | 2.21                                          | D2       | R08_pairing_diagnostic.csv :: whiteness_bound                                                              | L176     |
| L311 penalty at residual momentum 0.02 (points)                              | 1.1                        | 1.2799999999999998                            | D2       | R07_estmean_lb_fpr.csv :: fpr_concept, NAIVE, phi in (0, 0.02)                                             | L177     |
| L311 whiteness range, low end                                                | 0.05                       | 0.0478                                        | D1       | R08_adverse_bias.csv :: min over both arms of the rejection rate                                           | L178     |
| L311 whiteness range, high end                                               | 1.0                        | 0.9984                                        | D1       | R08_adverse_bias.csv :: max over both arms of the rejection rate                                           | L179     |

Count by severity: D0: 1, D1: 2, D2: 6, D3: 1.

**Falsified qualitative claim (L241):** The manuscript states it selects "the nearest attainable level at or below nominal", and its own footnote makes the implemented test the weak comparison operator. The weak level at the selected threshold (11.4) is above the nominal level (0.050815 > 0.05). On the lattice of step 2delta = 0.2 the threshold 11.4 is 57 units and 11.2 is 56, so {M >= 11.4} and {M > 11.2} are the same event and the weak level at lambda* is the strict level at 11.2 bit for bit -- 0.051020717214682557 on the exact law, 0.050815 measured on 200000 streams. The row at lambda = 11.2 is the Monte-Carlo redraw of that strict level and carries D2; the D3 is the level the selection rule delivers at lambda*, which the exact law fixes with no sampling error.

**Scope:** The null law itself remains exact and free of nuisance parameters; what is contradicted is the selection rule and the level reported, not the exactness result.

---

## 2. Controls

### C1 (i)-(iii) Operator Identity, by AST
What it tests: Every exceedance test routes through one of three helpers (`exceeds`, `exceeds_units_strict`, `exceeds_units_weak`). Of the 138 comparisons in exp_R08_adverse_lattice_a.py and exp_R08_adverse_lattice_b.py, the 3 inside the helper set are the only ones that may order a threshold name against anything, and none of the others does. `worker_mod_A` calls `exceeds`; `operator_levels_at` calls all three helpers; `lattice_exceedance_enumerated` calls `exceeds_units_strict`. lambda* itself comes from `lambda_star_from_rule` on the EXACT law, so the selection path and the evaluation path test the same operator by construction. Trigger probability: 0 (deterministic). Realised margin: N/A (deterministic). Verdict: PASSED.

### C1 / C2 The Exact Lattice Law
What it tests: With delta = 0.1 the two CUSUM branches move by +0.4 and -0.6, i.e. by +2 and -3 in units of 2delta = 0.2, so (S_pos, S_neg) is a Markov chain on the non-negative integer quadrant and M_H is an integer multiple of 0.2. An absorbing-chain dynamic program over that state space at H = 5000 gives P(M_H > lambda) exactly. No Monte-Carlo is involved and no entropy is consumed. Trigger probability: 0 (deterministic). Realised margin: N/A (deterministic). Verdict: PASSED.

### C1 lambda* by L241's own rule
What it tests: Evaluated on the exact law in 2.3s: 'we take the nearest attainable level at or below nominal' selects the SMALLEST lattice threshold whose exact level is at or below 0.05, which is 57 lattice units = 11.4. v87 prints lambda* = 11.4, and 57 * 0.2 == 11.4 is True bit-for-bit in float64. Trigger probability: 0 (deterministic). Realised margin: N/A (deterministic). Verdict: PASSED.

### C2a Exact Survival Against R07
What it tests: At H = 5000. 16 of the 16 scanned lattice points carry an R07 cell; 16 agree BIT FOR BIT and 0 do not. Largest absolute difference 0.0. Two independently written absorbing-chain programs at the same H over the same state space; agreement is a statement about the transcription, not about the model. Trigger probability: 0 (deterministic). Realised margin: N/A (deterministic). Verdict: PASSED.

### C2b Enumeration Concordance
What it tests: R08 enumerates all 2^H sign paths at H in (8, 10, 12, 14) and lambda in (4, 5, 6, 7) lattice units at q = 0.5, and agrees with its own dynamic program to the last bit on all 16 cells. Against the other two streams: 8 cells are shared by all THREE (H in (10, 12)) and are the assertion; 4 more are shared with R07 alone (H = 8) and 4 with R10 alone (H = 14), reported beside them. Trigger probability: 0 (deterministic). Realised margin: N/A (deterministic). Verdict: PASSED. Result: bit-for-bit agreement on every cell any other stream carries -- 8 three-way, 4 with R07 only, 4 with R10 only.

### C3 Bracketing on the Exact Law
What it tests: The bracketing roles are computed from the exact survival function. Trigger probability: 0 (deterministic). Realised margin: N/A (deterministic). Verdict: PASSED. Roles: [('11.0', 'none'), ('11.2', 'above_nominal'), ('11.4', 'below_nominal'), ('11.6', 'none'), ('11.8', 'none'), ('12.0', 'none')]. The pair that straddles 0.05 is lambda = 11.200000000000001 at 5.1021% and lambda = 11.4 at 4.3428%, and no other adjacent pair of the grid does.

### C3 Bracketing on the Measured Strict Levels
What it tests: The same roles as the exact law. Trigger probability: 1.9017% (computed before the streams were drawn: the exact level at lambda = 11.2 is 5.1021%, which is only 2.07 binomial standard errors above the 0.05 nominal at 200000 streams, so a Monte-Carlo realisation on the wrong side of nominal is an ordinary event. Summed over the 6 grid points the probability that at least one lands on the wrong side of nominal is 1.9017%). Realised margin: N/A (reported control, not a gate). Verdict: PASSED. The measured leg is a REPORTED control, it logs an error and the run continues, and only the exact leg exits. Roles: [('11.0', 'none'), ('11.2', 'above_nominal'), ('11.4', 'below_nominal'), ('11.6', 'none'), ('11.8', 'none'), ('12.0', 'none')].

### C4 Family-Wise Arithmetic
What it tests: Control C4 compares the two arms at 6 values of b. Gating on 'no test rejects' at the 0.05 level would trigger with probability 1 - (1 - 0.05)^6 = 26.4908% under the hypothesis of equality itself -- far above the 5% ceiling S4bis fixes. 'No test rejects' is therefore NOT used as a gate, and neither is 'two tests reject' used as a refutation. The substitute is a KS calibration of the six p-values against Uniform(0,1), read against a null built by sign-flip resampling on the trajectory index, because the six p-values are dependent twice over and the tabulated Kolmogorov distribution assumes neither dependence. Trigger probability: 26.4908% under the hypothesis of equality. Realised margin: 6 of 6 p-values, 3 of 6 reject at 0.05. Verdict: PASSED. The substitute KS calibration is used instead of gating.

### C4 KS Calibration
What it tests: KS calibration of the six p-values against Uniform(0,1). Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: D = 0.5583837080994306, tabulated p = 0.027417888290213646. THE TABULATED p DOES NOT APPLY: the six p-values are dependent twice over -- the six b share the same 10000 trajectories, and at each b the two arms share the same innovation stream -- and the Kolmogorov distribution assumes neither. The null of D is therefore built by sign-flip resampling on the trajectory index, one Rademacher sign per trajectory shared across the six columns, 2000 replicates: its 95% quantile is 0.5359638576177561 and the observed D sits at a null exceedance probability of 0.038. Verdict: PASSED. MEASUREMENT, NOT A GATE (S4bis.8): nothing exits on this number.

### C4 Sign-Flip Null of the Maximum [max |delta_lb_pp| over the b grid]
What it tests: The maximum over the b grid of the absolute paired difference in Ljung-Box rejection rates. Trigger probability: 0.001 (null built by sign-flip resampling on the trajectory index, 10000 replicates, read at level 0.001). Realised margin: observed 0.0221, 99.900% quantile of the null maximum 0.0223 on 10000 replicates, null exceedance probability 0.0011. Verdict: PASSED.

### C4 Sign-Flip Null of the Maximum [max |delta_fpr_pp| over the b grid]
What it tests: The maximum over the b grid of the absolute paired difference in false positive rates. Trigger probability: 0.001 (null built by sign-flip resampling on the trajectory index, 10000 replicates, read at level 0.001). Realised margin: observed 0.2005, 99.900% quantile of the null maximum 0.0151 on 10000 replicates, null exceedance probability 0.0. Verdict: PASSED.

### C4 The Three-Point Bound of L311
What it tests: Asserted separately and against the extremum's own law (S4bis.4). 'The injected-bias arm and the naive arm at phi = b reject within three points of each other': the largest |delta_lb_pp| over the 6 values of b is 2.2100 points, attained at b = 0.075, against the 3 the sentence states. The bound is RESPECTED. The 95% bootstrap envelope of that MAXIMUM, over 2000 resamplings of the trajectory index, is [1.5600, 3.6100] points. Trigger probability: 0.001 (null law built separately by sign-flip resampling, 10000 replicates, read at level 0.001). Realised margin: 2.2100 points (observed), bootstrap envelope [1.5600, 3.6100] points. Verdict: PASSED.

### C4 The Six Proportion p-Values
What it tests: The six proportion p-values on the Ljung-Box arm, reported and not gated. Trigger probability: 26.4908% (1 - (1 - 0.05)^6 under equality). Realised margin: [(0.0, 0.6449228388435186), (0.02, 0.10828295856723602), (0.05, 0.00026716158404238577), (0.075, 0.0017734684466137463), (0.1, 0.0003323256056320112), (0.15, 0.41064657021032636)]. 3 of 6 reject at 0.05: [(0.05, 0.00026716158404238577), (0.075, 0.0017734684466137463), (0.1, 0.0003323256056320112)]. Verdict: PASSED. A difference in REJECTION COUNT between the two campaigns is not a finding on its own -- the family-wise arithmetic logged above gives 26.4908% for at least one rejection under equality itself -- and the Figure 8 caption's parenthetical, a |Cov(y_t, y_(t+k))| response, is a statement of MECHANISM which is symmetric by construction and is not contradicted by a difference in measured rate.

### C5 [fpr_biased] over the b grid
What it tests: Required non-increasing in b. Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: [0.052, 0.0429, 0.0309, 0.0238, 0.0175, 0.0095]. Verdict: PASSED. No local inversion on either arm, over the 10 consecutive steps of the grid. This is the qualitative content of L311 and of the Figure 8 panel B caption; both directions are read on the whole grid.

### C5 [fpr_naive_ref] over the b grid
What it tests: Required non-decreasing in b. Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: [0.0516, 0.0644, 0.0854, 0.1094, 0.1377, 0.21]. Verdict: PASSED. No local inversion on either arm, over the 10 consecutive steps of the grid. This is the qualitative content of L311 and of the Figure 8 panel B caption; both directions are read on the whole grid.

### C6 Cross-Stream Identity
What it tests: Module A's pairing diagnostic keys on R07's namespace -- seed_sequence_for('trajectory', i) -- deliberately; every other draw in R08 keys on R08's own ('lattice_stream', index). An unexplained reuse would read as an entropy collision, so it is declared here. The identity is EXACT and its trigger probability is 0: `generate_dgp` draws z, h and eps without reference to phi, only r[t] = phi r[t-1] + eps[t] uses it, and control C7's normalized-AST leg establishes that R07's copy of `generate_dgp` and `compute_phi_hat_vectorized` compile the same instructions as the R08 witness's. Trigger probability: 0 (deterministic). Realised margin: N/A (deterministic). Verdict: PASSED. Result: R08's b = 0 arm against R07's OLS-250 at phi = 0 -- Ljung-Box 0.0478 vs 0.0478 (bit-identical True), FPR 0.052 vs 0.052 (bit-identical True). The pairing diagnostic against R07's NAIVE arm: 6/6 bit-identical on Ljung-Box and 6/6 on FPR.

### C6 The Level the b = 0 Cell Lands On
What it tests: Its false-alarm rate is 0.052 on 10000 trajectories. Against the two exact levels at lambda* = 11.4: strict M > lambda* = 4.3428% -> z = +4.21 (SE 0.002038); weak M >= lambda* = 5.1021% -> z = +0.45 (SE 0.002200). Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: z-scores +4.21 and +0.45 standard errors respectively. Verdict: PASSED. It lands on the weak M >= lambda* level.

### C7 Source Identity
What it tests: 6 primitives byte-identical to Priorite_21b_adverse_bias_and_null_law.py (wilson_ci, prop_test, lb_pvalue, compute_phi_hat_vectorized, cusum_concept_fast, generate_dgp) and 12 byte-identical to exp_R07_estimated_mean.py (exceeds, exceeds_units_strict, exceeds_units_weak, cusum_concept_lattice_units, lattice_exceedance_exact, lattice_exceedance_enumerated, lattice_survival, lambda_star_from_rule, get_deterministic_seed, seed_sequence_for, rng_for, sign_flip_null_max); 9086 characters compared, 0 differences. The protocol forbids hoisting any of them into experiments/common/, so the duplication is deliberate and it cannot drift. Trigger probability: 0 unless a copy has drifted. Realised margin: N/A (deterministic). Verdict: PASSED.

### C7 Cross-Owner AST Identity on generate_dgp
What it tests: Byte identity against exp_R07_estimated_mean.py is FALSE and is not asserted -- R07's copy carries 5 blank line(s) at positions [5, 10, 14, 18, 23] that the R08 witness does not, and every non-blank line is identical (True). `ast.dump(ast.parse(...))` of the two segments is EQUAL, so the two files compile the same instructions. Trigger probability: 0 (deterministic). Realised margin: N/A (deterministic). Verdict: PASSED. SHA-256 witness: 9772f0bc99705b56037dcdd863d1aa1d5c440f7420f7389e4d06fcc205ef7464 SHA-256 R07: 8dda36b3707f8d9a152ec48e8c583b58eaaedb45b627ccca90d3d0c1412f6aec

### C7 Cross-Owner AST Identity on compute_phi_hat_vectorized
What it tests: Byte identity against exp_R07_estimated_mean.py is FALSE and is not asserted -- R07's copy carries 4 blank line(s) at positions [5, 10, 13, 16] that the R08 witness does not, and every non-blank line is identical (True). `ast.dump(ast.parse(...))` of the two segments is EQUAL, so the two files compile the same instructions. Trigger probability: 0 (deterministic). Realised margin: N/A (deterministic). Verdict: PASSED. SHA-256 witness: ae5cf1ceefdfa7d0845dc1f9262dd380536cac8a60ea296639f41fa03321d1b8 SHA-256 R07: d960886a69b4f09b21619f4bedc4381b2e822f8a18a09997d8f844c85f94a629

### C7 Adapted Routines
What it tests: ['worker_mod_A', 'worker_mod_B', 'plot_adverse_and_lattice', 'main'] are restructured for the reasons stated in the module docstring -- keyed entropy, per-trajectory return values, the removal of the disk round trip, and the replacement of a certification block that gates on four literals the script itself produced -- so byte identity is not assertable on them. Each segment is passed through the S4.4 grep FIRST and quoted in full only if the grep is empty. Trigger probability: NOT RECOVERABLE FROM THE LOG. Realised margin: S4.4 grep returns empty for all adapted routines. Verdict: PASSED.

---

## 3. Test suite

============================= test session starts ============================== platform linux -- Python 3.12.9, pytest-9.0.3, pluggy-1.6.0 -- /home/m53/miniforge3/envs/Trading/bin/python cachedir: .pytest_cache rootdir: /home/m53/The-Whitening-Advantage-Experiments plugins: anyio-4.8.0 collecting ... collected 26 items

tests/test_R08_claims.py::test_R08_every_artefact_the_plan_lists_exists_with_its_prescribed_schema PASSED [  3%] tests/test_R08_claims.py::test_R08_the_operating_threshold_is_fifty_seven_lattice_units PASSED [  7%] tests/test_R08_claims.py::test_R08_the_exact_lattice_law_reproduces_under_an_independent_dynamic_program PASSED [ 11%] tests/test_R08_claims.py::test_R08_the_enumeration_validation_agrees_with_an_independent_enumeration PASSED [ 15%] tests/test_R08_claims.py::test_R08_the_three_streams_agree_on_the_cells_they_share PASSED [ 19%] tests/test_R08_claims.py::test_R08_the_bracketing_of_the_nominal_level_is_the_one_L241_states PASSED [ 23%] tests/test_R08_claims.py::test_R08_the_wilson_intervals_reproduce_from_a_second_algebraic_form PASSED [ 26%] tests/test_R08_claims.py::test_R08_one_comparison_operator_is_shared_by_both_modules PASSED [ 30%] tests/test_R08_claims.py::test_R08_the_carried_primitives_are_byte_identical_to_both_owning_files PASSED [ 34%] tests/test_R08_claims.py::test_R08_the_two_dgp_primitives_are_ast_identical_across_their_two_owners PASSED [ 38%] tests/test_R08_claims.py::test_R08_the_cross_stream_identity_with_R07_is_exact PASSED [ 42%] tests/test_R08_claims.py::test_R08_the_sign_asymmetry_of_L311_holds_in_both_directions PASSED [ 46%] tests/test_R08_claims.py::test_R08_the_three_point_bound_of_L311_holds_with_its_extremum_envelope PASSED [ 50%] tests/test_R08_claims.py::test_R08_the_family_wise_arithmetic_is_logged_before_any_gate_is_read PASSED [ 53%] tests/test_R08_claims.py::test_R08_macros_are_emitted_and_agree_with_the_frames PASSED [ 57%] tests/test_R08_claims.py::test_R08_text_artefacts_end_with_a_newline PASSED [ 61%] tests/test_R08_claims.py::test_R08_no_confirmatory_language_in_the_scripts_the_logs_or_the_section PASSED [ 65%] tests/test_R08_claims.py::test_R08_the_scripts_own_S4_4_pattern_accepts_the_preambles_language PASSED [ 69%] tests/test_R08_claims.py::test_R08_the_produced_sources_carry_no_banned_construct PASSED [ 73%] tests/test_R08_claims.py::test_R08_the_monte_carlo_numerals_of_L241_and_L311_move_within_their_own_sampling_error PASSED [ 76%] tests/test_R08_claims.py::test_R08_the_level_the_implemented_operator_delivers_at_lambda_star_is_above_nominal PASSED [ 80%] tests/test_R08_claims.py::test_R08_the_implemented_float_test_coincides_with_the_weak_operator PASSED [ 84%] tests/test_R08_claims.py::test_R08_the_whiteness_gap_maximum_has_moved_from_the_witness_campaign PASSED [ 88%] tests/test_R08_claims.py::test_R08_report_deviation_classification R08 deviation classification against v87, at the manuscript's printing precision site                                       printed   regenerated  degree  source cell L241 level at lambda = 11.2                 0.0503      0.050815  D2      R08_null_law_lattice.csv, lambda=11.2, P_exceed_strict L241 level at lambda = 11.4                 0.0429       0.04323  D2      R08_null_law_lattice.csv, lambda=11.4, P_exceed_strict L241 lambda*                                  11.4          11.4  D0      R08_null_law_lattice.csv, bracket_role=below_nominal Fig. 8 (B) FPR collapses to                 0.0086        0.0095  D2      R08_adverse_bias.csv, b=0.15, fpr_biased Fig. 8 (B) FPR inflates to                   0.208          0.21  D2      R07_estmean_lb_fpr.csv, NAIVE, phi=0.15, fpr_concept L311 whiteness gap bound (points)                3          2.21  D2      R08_pairing_diagnostic.csv, whiteness_bound L311 penalty at momentum 0.02 (points)         1.1          1.28  D2      R07_estmean_lb_fpr.csv, NAIVE, phi in (0, 0.02) L311 whiteness range, low end                 0.05        0.0478  D1      R08_adverse_bias.csv, min over both arms L311 whiteness range, high end                   1        0.9984  D1      R08_adverse_bias.csv, max over both arms The witness is a record of the submitted campaign, not a target; see data/reference/README.md. witness [21c] b = 0.0   : lb 0.0485 -> 0.0478, fpr 0.0546 -> 0.0520, naive lb 0.0509 -> 0.0492, naive fpr 0.0535 -> 0.0516 witness [21c] b = 0.02  : lb 0.0642 -> 0.0647, fpr 0.0441 -> 0.0429, naive lb 0.0685 -> 0.0704, naive fpr 0.0640 -> 0.0644 witness [21c] b = 0.05  : lb 0.1918 -> 0.1943, fpr 0.0307 -> 0.0309, naive lb 0.2045 -> 0.2151, naive fpr 0.0836 -> 0.0854 witness [21c] b = 0.075 : lb 0.4700 -> 0.4815, fpr 0.0235 -> 0.0238, naive lb 0.4984 -> 0.5036, naive fpr 0.1134 -> 0.1094 witness [21c] b = 0.1   : lb 0.8031 -> 0.8003, fpr 0.0168 -> 0.0175, naive lb 0.8076 -> 0.8202, naive fpr 0.1369 -> 0.1377 witness [21c] b = 0.15  : lb 0.9984 -> 0.9984, fpr 0.0086 -> 0.0095, naive lb 0.9979 -> 0.9979, naive fpr 0.2076 -> 0.2100 witness [21d] lambda = 11     (55 units): P_exceed 0.059150 -> strict 0.060200, weak 0.070360, exact strict 0.059900 witness [21d] lambda = 11.2   (56 units): P_exceed 0.050270 -> strict 0.050815, weak 0.060200, exact strict 0.051021 witness [21d] lambda = 11.4   (57 units): P_exceed 0.042870 -> strict 0.043230, weak 0.050815, exact strict 0.043428 witness [21d] lambda = 11.6   (58 units): P_exceed 0.036470 -> strict 0.036705, weak 0.043230, exact strict 0.036945 witness [21d] lambda = 11.8   (59 units): P_exceed 0.031075 -> strict 0.031170, weak 0.036705, exact strict 0.031414 witness [21d] lambda = 12     (60 units): P_exceed 0.026540 -> strict 0.026320, weak 0.031170, exact strict 0.026700 PASSED [ 92%] tests/test_R08_claims.py::test_R08_report_the_operator_levels_and_the_boundary_counter R08 the level each comparison operator delivers (control C1)
    lambda  units  float M > l   units > l  units >= l  d(strict)  d(weak)  boundary
        11     55     0.070360    0.060200    0.070360       2032        0      2032
      11.2     56     0.060200    0.050815    0.060200       1877        0      1877
      11.4     57     0.050815    0.043230    0.050815       1517        0      1517
      11.6     58     0.043230    0.036705    0.043230       1305        0      1305
      11.8     59     0.036705    0.031170    0.036705       1107        0      1107
        12     60     0.031170    0.026320    0.031170        970        0       970
  Float position against the exact lattice point over 200000 streams: above 192842, below 2776, exactly on 4382; within 4 ulp 78971. The four exact levels L241's two thresholds carry: strict(11.2) = 5.1021%, weak(11.2) = 5.9900%, strict(11.4) = 4.3428%, weak(11.4) = 5.1021%. The rule L241 states promises 'at or below nominal' and the operator the code implements delivers the last of the four. PASSED [ 96%] tests/test_R08_claims.py::test_R08_report_the_pairing_diagnostic_and_the_control_nulls R08 the paired design behind panels A and B (controls C4, C5, C6)
        b  lb biased  lb naive   gap pt  discord   rho_lb  deff_lb  fpr biased  fpr naive  rho_fpr
    0.000     0.0478    0.0492    -0.14      454   0.5082   1.5082      0.0520     0.0516   0.5684
    0.020     0.0647    0.0704    -0.57      739   0.4139   1.4139      0.0429     0.0644   0.5396
    0.050     0.1943    0.2151    -2.08     2630   0.1932   1.1932      0.0309     0.0854   0.4706
    0.075     0.4815    0.5036    -2.21     4889   0.0225   1.0225      0.0238     0.1094   0.3425
    0.100     0.8003    0.8202    -1.99     3211  -0.0437   0.9563      0.0175     0.1377   0.2565
    0.150     0.9984    0.9979     0.05       37  -0.0018   0.9982      0.0095     0.2100   0.1393
  Family-wise arithmetic: gating on all 6 proportion tests at 0.05 would trigger with probability 26.4908% under equality itself, which is why it is not a gate. 3 of 6 proportion tests reject: [(0.05, 0.00026716158404238577), (0.075, 0.0017734684466137463), (0.1, 0.0003323256056320112)]. The Figure 8 caption's parenthetical is a statement of mechanism, symmetric by construction; it is not contradicted by a difference in measured rate. [ks_calibration] KS of the six pval_lb against Uniform(0,1): observed 0.558384, tabulated p 0.027418, null quantile 0.535964, null p 0.038000, 2000 replicates [sign_flip_null_max] max |delta_lb_pp| over the b grid: observed 0.022100, null quantile 0.022300, null p 0.001100, 10000 replicates [sign_flip_null_max] max |delta_fpr_pp| over the b grid: observed 0.200500, null quantile 0.015100, null p 0.000000, 10000 replicates [whiteness_bound] max |delta_lb_pp| in points, against L311s three-point bound: observed 2.210000, null quantile 3.000000, 95% envelope [1.5600, 3.6100], 2000 replicates PASSED [100%]

============================== 26 passed in 1.02s ==============================

Total: 26 passed.

---

## 4. Reproducibility digests

First run (48 workers, log L185-189):
```
SHA-256 R08_adverse_bias.csv               : 167bc67f6913ebea6fe5023c62a9638259a1036028821d0fa051339ea772f675
SHA-256 R08_null_law_lattice.csv           : 01abacb1f055f2006d4cf32f3f630003813180f0bdb3da5bb3b839c76e7df611
SHA-256 R08_operator_levels.csv            : f80e06d2d24de02b0878a840e89acfd6aa622c633468a0032c0cce93141913d6
SHA-256 R08_lattice_exact_law.csv          : 7134ae5e2cc683f18fbbf7efb0c32dbebd68cabbf36e06fc5b880d1710e00893
SHA-256 R08_pairing_diagnostic.csv         : 0492b16f924e68779a22bfdb60820ef1c531483b09c211e425c06422f895b917
```
Number of workers: 48.

Second run (48 workers, log L345-349):
```
SHA-256 R08_adverse_bias.csv               : 167bc67f6913ebea6fe5023c62a9638259a1036028821d0fa051339ea772f675
SHA-256 R08_null_law_lattice.csv           : 01abacb1f055f2006d4cf32f3f630003813180f0bdb3da5bb3b839c76e7df611
SHA-256 R08_operator_levels.csv            : f80e06d2d24de02b0878a840e89acfd6aa622c633468a0032c0cce93141913d6
SHA-256 R08_lattice_exact_law.csv          : 7134ae5e2cc683f18fbbf7efb0c32dbebd68cabbf36e06fc5b880d1710e00893
SHA-256 R08_pairing_diagnostic.csv         : 0492b16f924e68779a22bfdb60820ef1c531483b09c211e425c06422f895b917
```
Number of workers: 48.

current tree, single run:
```
167bc67f6913ebea6fe5023c62a9638259a1036028821d0fa051339ea772f675  results/R08_adverse_lattice/data/R08_adverse_bias.csv
7134ae5e2cc683f18fbbf7efb0c32dbebd68cabbf36e06fc5b880d1710e00893  results/R08_adverse_lattice/data/R08_lattice_exact_law.csv
01abacb1f055f2006d4cf32f3f630003813180f0bdb3da5bb3b839c76e7df611  results/R08_adverse_lattice/data/R08_null_law_lattice.csv
f80e06d2d24de02b0878a840e89acfd6aa622c633468a0032c0cce93141913d6  results/R08_adverse_lattice/data/R08_operator_levels.csv
0492b16f924e68779a22bfdb60820ef1c531483b09c211e425c06422f895b917  results/R08_adverse_lattice/data/R08_pairing_diagnostic.csv
6a5f743e5920c8043358e20a3013026f994a94f5e019f186fca52e0a4c1dc9c6  results/R08_adverse_lattice/tables/R08_claims.tex
```

---

## 5. Design decisions taken outside the plan

1. R08's b = 0 arm reuses R07's namespace for module A — seed_sequence_for('trajectory', i) — deliberately, to establish cross-stream identity. This decision is declared in the log to prevent an unexplained reuse from reading as an entropy collision (log L130, L140, L164-165).
2. The delivered module B computed the float form alone and rounded it to six decimals before comparing, which reports the strict lattice level without saying so. R08 computes both forms to measure the operator instead of inferring it, and pays the computational cost of that measurement (log L143-144, L340-341).
3. Figure 8 panels (A) and (B) remove the 5% rule and draw the two operator levels (strict and weak) in its place. This is NOT cosmetic and is recorded in this audit (log L343).
4. Panel titles are bold, horizontally centred and prefixed (A)-(C) — a cosmetic divergence from the submitted Fig26_Adverse_Bias_and_Lattice.png, declared per the protocol (log L343).

---

## 6. Open questions, left open

None recorded.
