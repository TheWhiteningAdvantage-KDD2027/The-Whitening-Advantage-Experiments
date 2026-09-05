# Audit Report: R04 — Iso-FPR Race and Relative Efficiency

## 1. Deviation table (D0-D3)

| quantity | manuscript value | regenerated value | severity | source CSV cell | log line |
|----------|-----------------|------------------|----------|-----------------|----------|
| Recalib runs 2 to 19x behind the first-order arms | 2 to 19x | 7 to 81x | D3 | R04_isofpr_race.csv :: ADD_conditional (min/max ratio across all Gamma, c, arms) | 132 |
| Recalib blind zone persists even at the lowest Gamma | collapse present | DetRate 0.1790 at Gamma = 1.1053 | D0 | R04_isofpr_race.csv :: DetRate at Gamma=1.0, arm=Recalib, c=0.25 | 133 |
| efficiency ratio crosses unity at nu* ~ 4.9 | 4.9 | 8.52, superseded by R04b, see AUDIT_R04b.md | D2 | R04_relative_efficiency.csv :: ratio (interpolated from nu=7.0 and nu=30.0) | 134 |
| oracle arm crosses unity at 4.6 | 4.6 | 4.47 | D2 | R04_relative_efficiency.csv :: ratio_oracle (interpolated from nu=4.0 and nu=4.5) | 135 |
| finite warm-up costs 0.3 degrees of freedom | 0.3 | 4.05, superseded by R04b, see AUDIT_R04b.md | D2 | R04_relative_efficiency.csv :: ratio,ratio_oracle (8.5180 - 4.4659) | 136 |
| parametric route is 1.66x faster at c = 1 | 1.66x | 1.38x | D2 | R04_isofpr_race.csv :: ADD_conditional at Gamma=11.58, c=1.0, arm=Eco_L1 and Oracle_Eco | 137 |
| ratio never exceeds the Gaussian ceiling pi/2 | <= 1.5708 | max 1.2006 | D0 | R04_relative_efficiency.csv :: ratio max value 1.200608 | 138 |
| ratio is monotone increasing in nu | monotone | min diff +0.0724 | D0 | R04_relative_efficiency.csv :: ratio; Spearman rho = 1.0000 | 139 |
| Concept threshold is flat in Gamma | [10.6, 10.7] | [10.50, 10.74], homogeneity p = 0.260 | D2 | R04_isofpr_calibration.csv :: lambda_star range [10.499036, 10.743177] | 140 |
| blind-zone onset c* ~ 0.43 | 0.43 | 0.4321 | D0 | analytic from R04_isofpr_race.py constants delta_R=0.125, kappa_z=3.230769 | 141 |
| family control: both levels flat in Gamma | CUSUM ~0.05, ADWIN ~0.006 flat | CUSUM 0.3609 spread 0.4905, ADWIN 0.1072 | D3 | R04_cusum_vs_adwin.csv :: FPR mean across Gamma grid | 142 |

Count by severity: D0: 4, D1: 0, D2: 5, D3: 2.

R04b owns both of those numerals. R04's nu grid {3, 4, 4.5, 5, 7, 30} samples no point inside (7, 30), and the Eco-L1 efficiency ratio crosses unity inside that 23-unit interval: R04_relative_efficiency.csv :: ratio reads 0.985825 at nu = 7.0 and 1.200608 at nu = 30.0. The 8.52 above is the two-point linear interpolation across that empty interval, and the 4.05 dof is a difference of two such interpolations. A value produced by interpolation across an unsampled interval is not a measurement of the quantity it names, so it cannot falsify a printed claim; that is why both rows are carried at D2 and not D3. R04b was created to extend the grid to the twelve points {4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 15.0, 20.0, 30.0} and resolve them, and its regenerated values -- inferential bracket [7.0, 9.0] with shape fit 8.10 [7.78, 8.37] for nu*, and 3.62 [3.31, 3.92] by the shape-fit route with 3.22 [2.52, 3.82] model-free for the estimation cost -- are the ones that carry the D3. See AUDIT_R04b.md.

Two falsified qualitative claims remain at D3 in v87 Section 4: (1) the Recalib slowdown is 7 to 81x rather than the printed 2 to 19x; (2) the family control levels are not flat across Gamma. The nu* crossing and the estimation cost were carried at D3 in the earlier revision of this table and are now D2, superseded by R04b for the reason given above. The root cause is the Gamma grid collapse in the submitted campaign (all labels resolved to Gamma = 1.1053) due to a parameter ordering bug in solve_beta_for_gamma(gamma, alpha). The compliant pipeline reproduces the submitted results in counterfactual mode (beta pinned to 0), confirming the discrepancy mechanism. The falsifications do NOT affect: the blind-zone mechanism (second-order sensor property), the Gaussian ceiling bound, the monotonicity of the efficiency ratio in nu, or the analytic crossing of f_z(0) = 1/2.

**Scope:** the two D3 rows contradict the printed magnitude of the Recalib slowdown (7 to 81x against the printed 2 to 19x, R04_isofpr_race.csv :: ADD_conditional) and the printed flatness of the family control levels across Gamma (CUSUM spread 0.490500, ADWIN spread 0.239000, R04_cusum_vs_adwin.csv :: FPR), and not the Recalib blind zone (DetRate 0.1790 at the lowest Gamma, D0), not the Gaussian ceiling pi/2 (max ratio 1.200608, D0), not the monotonicity of the efficiency ratio in nu (Spearman rho = 1.0000, D0), not the flatness of the Concept threshold in Gamma (lambda_C* in [10.499036, 10.743177], homogeneity p = 0.2601, D2), not the location of the efficiency crossing or the cost of the parametric route, which R04b owns, and not any proposition of v87.

## 2. Controls

### Seed uniqueness (A2)
Tests that every task derives a unique 128-bit seed. Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: 84000 distinct seeds over 84000 tasks, zero collisions (log line 80). Verdict: passed.

### QMLE non-convergence
Tests the rate of QMLE fits that fail on all 3 starts of the multistart ladder. Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: 0 of 64000 (0.0000%), budget 0.5% (log line 81). Verdict: passed.

### QMLE stationarity guard
Tests the rate of fits hitting the alpha + beta >= 0.999 boundary. Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: 0 of 64000 (0.0000%), budget 0% (log line 82). Verdict: passed. The guard is unreachable once an infeasible pair is projected back onto alpha + beta = 0.999, so any firing is structural.

### QMLE constraint boundary
Tests the rate of fits at the feasibility boundary. Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: 699 of 64000 (1.0922%) returned alpha + beta >= 0.999 (log line 83). Verdict: reported, not gated. Those fits are stationary and are KEPT. The submitted script guarded on that same predicate and reverted every one of them to (0.05, 0.9) without counting them.

### Cardinality (b)
Tests that row counts match the design. Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: R04_isofpr_calibration = 16, R04_isofpr_race = 64, R04_relative_efficiency = 6, R04_cusum_vs_adwin = 8, all exact (log line 84). Verdict: passed.

### Calibration (c)
Tests that all 16 arms achieve FPR within 0.003 of 0.05. Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: all 16 arms within 0.003 of 0.05; achieved rates span [0.0480, 0.0530] (log line 85). Verdict: passed.

### Concept threshold invariance (d)
Tests that Concept lambda_star is flat across Gamma and that false-alarm counts are homogeneous. Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: lambda_C* in [10.499036, 10.743177] over Gamma, spanning 2.0 bisection lattice steps; chi-square homogeneity = 4.0125, p = 0.2601 (log lines 86-88). Verdict: reported, not gated. The span leaves the admissible band (10.5, 10.8) by 0.000964, less than one lattice step.

### Blind-zone persistence (e)
Tests that Recalib detection rate is below 1 at c < 0.5 for the lowest Gamma. Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: DetRate below c = 0.5 at Gamma=1.0: 0.1790 (log lines 89-90). Verdict: passed. The collapse is present at Gamma = 1, so it is not a GARCH effect.

### Monotonicity (f)
Tests that the efficiency ratio is monotone increasing in nu. Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: 5 consecutive differences of the ratio in nu, most negative = +0.072364, Spearman rho = 1.0000 (p = 0.000e+00) (log line 91). Verdict: passed.

### Family control (g)
Tests that CUSUM and ADWIN FPR are flat across Gamma. Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: CUSUM FPR over Gamma grid = [0.067, 0.3305, 0.4885, 0.5575], spread = 0.490500; ADWIN FPR = [0.005, 0.044, 0.136, 0.244], spread = 0.239000 (log lines 92-93). Verdict: reported, not gated. On a Gamma grid that is genuinely spanned, the level of a CUSUM monitoring the RAW return stream is not flat. This is a deviation, not reconciled.

### ADWIN ceiling
Tests the maximum attainable FPR for ADWIN. Trigger probability under null: NOT RECOVERABLE FROM THE LOG. Realised margin: the loosest admissible delta 0.794328 attains only 0.007000 on i.i.d. Gaussian streams; no delta in (0, 1) brings ADWIN to nominal level (log lines 62-74). Verdict: reported, not gated. The ADWIN column is NOT iso-FPR with the CUSUM column.

## 3. Test suite

Command run: `cd /home/m53/The-Whitening-Advantage-Experiments && /home/m53/miniforge3/envs/Trading/bin/python -m pytest tests/test_R04_claims.py -v`

```
tests/test_R04_claims.py::test_R04_cardinalities PASSED                  [  3%]
tests/test_R04_claims.py::test_R04_grids_match_v87 PASSED                [  7%]
tests/test_R04_claims.py::test_R04_horizon_and_sample_size PASSED        [ 11%]
tests/test_R04_claims.py::test_R04_reference_drifts_are_coherent PASSED  [ 14%]
tests/test_R04_claims.py::test_R04_all_arms_are_iso_fpr PASSED           [ 18%]
tests/test_R04_claims.py::test_R04_concept_threshold_is_flat_in_gamma PASSED [ 22%]
tests/test_R04_claims.py::test_R04_concept_level_is_homogeneous_in_gamma PASSED [ 25%]
tests/test_R04_claims.py::test_R04_recalib_blind_zone_persists_at_lowest_gamma PASSED [ 29%]
tests/test_R04_claims.py::test_R04_recalib_is_slower_than_both_first_order_arms PASSED [ 33%]
tests/test_R04_claims.py::test_R04_add_decreases_with_drift_magnitude PASSED [ 37%]
tests/test_R04_claims.py::test_R04_conditional_mean_is_labelled_and_accompanied PASSED [ 40%]
tests/test_R04_claims.py::test_R04_efficiency_ratio_is_monotone_in_nu PASSED [ 44%]
tests/test_R04_claims.py::test_R04_ratio_respects_the_gaussian_ceiling PASSED [ 48%]
tests/test_R04_claims.py::test_R04_predicted_ratio_is_the_pitman_constant PASSED [ 51%]
tests/test_R04_claims.py::test_R04_oracle_is_never_slower_than_the_fitted_arm PASSED [ 55%]
tests/test_R04_claims.py::test_R04_analytic_crossing_matches_v87 PASSED [ 59%]
tests/test_R04_claims.py::test_R04_blind_zone_onset_matches_v87 PASSED   [ 62%]
tests/test_R04_claims.py::test_R04_macros_are_emitted_and_computed PASSED [ 66%]
tests/test_R04_claims.py::test_R04_crossings_agree_with_the_interpolation_rule PASSED [ 70%]
tests/test_R04_claims.py::test_R04_emitted_crossing_brackets_contain_the_crossing PASSED [ 74%]
tests/test_R04_claims.py::test_R04_table3_printing_rule_reproduces_v87 PASSED [ 77%]
tests/test_R04_claims.py::test_R04_table3_is_generated_from_the_csv PASSED [ 81%]
tests/test_R04_claims.py::test_R04_table3_shows_detrate_exactly_when_below_one PASSED [ 85%]
tests/test_R04_claims.py::test_R04_intervals_are_clamped_and_ordered PASSED [ 88%]
tests/test_R04_claims.py::test_R04_no_nan_in_reported_delays PASSED      [ 92%]
tests/test_R04_claims.py::test_R04_m0_universality_arm_matches_the_garch_arm PASSED [ 96%]
tests/test_R04_claims.py::test_R04_report_deviation_degrees PASSED       [100%]

  R04 deviation classification against the submitted campaign
  quantity                     |    published |  regenerated | degree
  Table 3 Recalib     c=0.25  |  2293.457219 |  2746.329897 | D2
  Table 3 Recalib     c=0.5   |  1336.727426 |  2622.018789 | D2
  Table 3 Recalib     c=1.0   |   202.627814 |  1986.673764 | D2
  Table 3 Recalib     c=2.0   |    55.909000 |  1311.240964 | D2
  Table 3 Eco_L1      c=0.25  |   389.309500 |   409.219500 | D2
  Table 3 Eco_L1      c=0.5   |    72.002000 |    77.128500 | D2
  Table 3 Eco_L1      c=1.0   |    26.393500 |    30.886500 | D2
  Table 3 Eco_L1      c=2.0   |    12.579000 |    16.096000 | D2
  Table 3 Concept     c=0.25  |   460.290000 |   381.935500 | D2
  Table 3 Concept     c=0.5   |   100.639000 |    96.859500 | D2
  Table 3 Concept     c=1.0   |    43.831500 |    42.628500 | D2
  Table 3 Concept     c=2.0   |    28.881500 |    28.572000 | D2
  ratio at nu=3.0                  |     0.407263 |     0.331177 | D2
  ratio at nu=4.0                  |     0.778229 |     0.622199 | D2
  ratio at nu=4.5                  |     0.921953 |     0.694563 | D2
  ratio at nu=5.0                  |     1.022764 |     0.788887 | D2
  ratio at nu=7.0                  |     1.236853 |     0.985825 | D2
  ratio at nu=30.0                 |     1.489896 |     1.200608 | D2
  The witness is a record of the submitted campaign, not a target; see docs/sections/R04.md for why its Gamma grid does not span.
PASSED
```

Total: 27 passed.

## 4. Reproducibility digests

From log (lines 144-151, 166):
- SHA-256 R04_bernoulli_constant.csv : 5735644c3f4d1819a6a0b98a0d1756409bf536a38178c9445c1c23ff28069ee8 (48 workers)
- SHA-256 R04_isofpr_calibration.csv : 3788c496e70dd2e092e35332d55113ac1fb3fc0559d7baa01aa409463dfaa3af (48 workers)
- SHA-256 R04_isofpr_race.csv : 7a038bd628c54d663bc87681732c656222cdf8a01e1a584aa2ca2b9832404a22 (48 workers)
- SHA-256 R04_relative_efficiency.csv : c024cf43d6b2abf1e1ea1385f88b159cd0e06467c46d1c0647365ab042ed2b6f (48 workers)
- SHA-256 R04_cusum_vs_adwin.csv : ea54dc9d62dc474d99e8cfd8f76f8b4fe9f2ea21959d4d75cff6834a93bc809b (48 workers)
- SHA-256 fig04_isofpr_race.png : 52b8fb9619dfba284dee0f61dd66f345d6bbe94ccbe7a0ab059f3614611b187a (48 workers)
- SHA-256 tab03_isofpr_race.tex : 9847c3fb98174ea78a1b5e449dbfe901215a685aa451039d55d3c502a0b32d7b (48 workers)
- SHA-256 R04_claims.tex : eac7da6efffbb002c97ac07ca367f30ffec5d47053c83d3a2672142efaf6466e (48 workers)

Command run: `sha256sum results/R04_isofpr_race/data/*.csv results/R04_isofpr_race/tables/*.tex`

Current tree, single run:
```
5735644c3f4d1819a6a0b98a0d1756409bf536a38178c9445c1c23ff28069ee8  results/R04_isofpr_race/data/R04_bernoulli_constant.csv
3788c496e70dd2e092e35332d55113ac1fb3fc0559d7baa01aa409463dfaa3af  results/R04_isofpr_race/data/R04_isofpr_calibration.csv
7a038bd628c54d663bc87681732c656222cdf8a01e1a584aa2ca2b9832404a22  results/R04_isofpr_race/data/R04_isofpr_race.csv
c024cf43d6b2abf1e1ea1385f88b159cd0e06467c46d1c0647365ab042ed2b6f  results/R04_isofpr_race/data/R04_relative_efficiency.csv
ea54dc9d62dc474d99e8cfd8f76f8b4fe9f2ea21959d4d75cff6834a93bc809b  results/R04_isofpr_race/data/R04_cusum_vs_adwin.csv
eac7da6efffbb002c97ac07ca367f30ffec5d47053c83d3a2672142efaf6466e  results/R04_isofpr_race/tables/R04_claims.tex
9847c3fb98174ea78a1b5e449dbfe901215a685aa451039d55d3c502a0b32d7b  results/R04_isofpr_race/tables/tab03_isofpr_race.tex
```

Note: fig04_isofpr_race.png is not included in the current tree sha256sum because it is a figure file, not CSV or TeX. The log line 149 gives its digest as 52b8fb9619dfba284dee0f61dd66f345d6bbe94ccbe7a0ab059f3614611b187a.

## 5. Design decisions taken outside the plan

1. Interpolation rule fixed before measurement: nu_star is linear interpolation of the delay ratio between the two grid points bracketing unity, on the nu grid as sampled (3.0, 4.0, 4.5, 5.0, 7.0, 30.0), reported with its bracket and rounded to one decimal for macro emission. (log line 10)
2. QMLE budgets fixed before measurement: stationarity 0% (the guard is unreachable once an infeasible pair is projected onto alpha + beta = 0.999), non-convergence 0.5% (derived from the sampling error of the means it protects, not from any observed rate). Multistart ladder: ((0.05, 0.9), (0.1, 0.85), (0.02, 0.95)). (log line 11)
3. Gamma grid corrected: at alpha = 0.05 the attainable floor is Gamma(alpha, beta=0) = 1.105263; the point labelled Gamma = 1 in v87 is in fact Gamma = 1.1053, an ARCH(1) stream. Every target above the floor is realised to within 1e-6, so the grid genuinely spans Gamma from 1.1053 to 200.0. (log lines 12-13)

## 6. Open questions, left open

1. Why does the family control CUSUM FPR vary so widely across Gamma (spread 0.490500)? The submitted campaign did not report this spread. (log lines 92-93)
2. Why does the ADWIN detector fail to reach the 5% target and terminate at the boundary of its search domain? (log line 62)
3. What is the correct interpretation of the estimation cost (4.05 dof vs 0.3 in v87) given that the Gamma grid in the submitted campaign collapsed? (log line 99)
