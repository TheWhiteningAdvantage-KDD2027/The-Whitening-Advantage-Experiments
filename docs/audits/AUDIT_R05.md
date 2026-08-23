# Audit Report: R05 — Scale Law and Location/Scale Orthogonality

## 1. Deviation table (D0-D3)

| quantity | manuscript value | regenerated value | severity | source CSV cell | log line |
|---|---|---|---|---|---|
| abrupt_slope | 23.70 | 26.0016 | D2 | R05_abrupt_add_vs_gamma.csv :: ADD_Data | exp_R05_scale_law_c.log:56 |
| abrupt_intercept | 38.00 | 32.1980 | D2 | R05_abrupt_add_vs_gamma.csv :: ADD_Data | exp_R05_scale_law_c.log:57 |
| sqrt_rule_fpr_pct | 31.00 | 24.5000 | D2 | R05_abrupt_add_vs_gamma.csv :: FPR_rule_xSqrtGamma | exp_R05_scale_law_c.log:58 |
| scaling_median_error_pct | 5.40 | 5.3465 | D2 | R05_ramp_multigamma_2e5.csv :: ADD_Data | exp_R05_scale_law_c.log:59 |
| recalib_margin_min_pct_2e5 | 7.00 | -1.4207 | D2 | R05_ramp_multigamma_2e5.csv :: lambda_star_Data/Gamma | exp_R05_scale_law_c.log:60 |
| recalib_margin_max_pct_2e5 | 29.00 | 39.2886 | D2 | R05_ramp_multigamma_2e5.csv :: lambda_star_Data/Gamma | exp_R05_scale_law_c.log:61 |
| lambda_iid_2e5 | 129.50 | 128.6319 | D2 | R05_ramp_multigamma_2e5.csv :: lambda_iid_H | exp_R05_scale_law_c.log:62 |
| grid_reach_wstar_2e5 | 22.50 | 22.5010 | D1 | R05_ramp_multigamma_2e5.csv :: w_over_wstar_predicted | exp_R05_scale_law_c.log:63 |
| censoring_max_pct_2e5 | 1.30 | 0.2500 | D2 | R05_ramp_multigamma_2e5.csv :: censored_Data | exp_R05_scale_law_c.log:64 |
| detection_min_pct_2e5 | 98.70 | 99.7500 | D2 | R05_ramp_multigamma_2e5.csv :: DetRate_Data | exp_R05_scale_law_c.log:65 |
| lambda_over_gamma_min_2e5 | 138.00 | 126.8044 | D2 | R05_ramp_multigamma_2e5.csv :: lambda_star_Data/Gamma | exp_R05_scale_law_c.log:66 |
| lambda_over_gamma_max_2e5 | 167.00 | 179.1696 | D2 | R05_ramp_multigamma_2e5.csv :: lambda_star_Data/Gamma | exp_R05_scale_law_c.log:67 |
| sd_over_add_max_2e5 | 3.20 | 0.9409 | D2 | R05_ramp_multigamma_2e5.csv :: SEM_Data | exp_R05_scale_law_c.log:68 |
| med_over_add_min_2e5 | 0.68 | 0.7586 | D2 | R05_ramp_multigamma_2e5.csv :: MED_Data/ADD_Data | exp_R05_scale_law_c.log:69 |
| rho_w_share_pct_2e5 | 58.00 | 57.2597 | D2 | R05_ramp_multigamma_2e5.csv :: widest w | exp_R05_scale_law_c.log:70 |
| exponent_min_2e5 | 0.65 | 0.6799 | D2 | R05_ramp_multigamma_2e5.csv :: ramp fit on w_delta_applied | exp_R05_scale_law_c.log:71 |
| exponent_max_2e5 | 0.71 | 0.6978 | D2 | R05_ramp_multigamma_2e5.csv :: ramp fit on w_delta_applied | exp_R05_scale_law_c.log:72 |
| model_exponent_min_2e5 | 0.71 | 0.7087 | D1 | R05_ramp_multigamma_2e5.csv :: Eq. (5) fit on w_delta_applied | exp_R05_scale_law_c.log:73 |
| model_exponent_max_2e5 | 0.73 | 0.7190 | D2 | R05_ramp_multigamma_2e5.csv :: Eq. (5) fit on w_delta_applied | exp_R05_scale_law_c.log:74 |
| lambda_iid_3e6 | 303.00 | 282.5363 | D2 | R05_ramp_multigamma_3e6.csv :: lambda_iid_H | exp_R05_scale_law_c.log:75 |
| grid_reach_wstar_3e6 | 225.00 | 224.99997 | D1 | R05_ramp_multigamma_3e6.csv :: w_over_wstar_predicted | exp_R05_scale_law_c.log:76 |
| low_gamma_max_error_pct_3e6 | 5.70 | 5.7976 | D2 | R05_ramp_multigamma_3e6.csv :: Gamma <= 4 vs Eq. (5) | exp_R05_scale_law_c.log:77 |
| rho_w_share_pct_3e6 | 78.00 | 78.1060 | D1 | R05_ramp_multigamma_3e6.csv :: widest w | exp_R05_scale_law_c.log:78 |
| recalib_margin_max_pct_3e6 | 96.00 | 96.4359 | D1 | R05_ramp_multigamma_3e6.csv :: lambda_star_Data/Gamma | exp_R05_scale_law_c.log:79 |
| sixth_moment_gamma | 7.10 | 7.0793 | D1 | closed form, no Monte Carlo | exp_R05_scale_law_c.log:80 |
| moment_margin_at_gamma_max | 0.80 | 0.7931 | D1 | closed form, no Monte Carlo | exp_R05_scale_law_c.log:81 |
| lambda_iid_ladder_77k | 102.80 | 111.0251 | D2 | R05_lambda_iid_horizon.csv :: H = 77000 | exp_R05_scale_law_c.log:82 |

Count: 20 D2, 7 D1, 0 D3, 0 D0.

## 2. Controls

### control a — abrupt shift protocol constants
Tests the configuration of the abrupt shift campaign: protocol constants alpha, nu, Delta_mu_max, delta_C, target FPR, seeds per config, Gamma grid.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised: alpha=0.08 nu=7.0 Delta_mu_max=2.0 delta_C=0.1 target FPR=0.05 seeds/config=400 Gamma grid n=13 in [1.00, 30.00].
Verdict: pass, constants match v87.
Source: exp_R05_scale_law_a.log:20

### control a — Concept threshold constancy
Tests that lambda_star_Concept is constant across Gamma under the sign-stream identity.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised: lambda_star_Concept constant across Gamma at 11.4000 while lambda_star_Data runs 52.3860 to 943.3187 (ratio 18.0x).
Verdict: pass, constancy is an identity of the design.
Source: exp_R05_scale_law_a.log:21

### control c — Concept orthogonality (abrupt)
Tests that Concept detection under scale pathology equals its own false-alarm rate (orthogonality).
Trigger probability under null: Fisher exact test, two-sided. With 22/400 alarms under both H_0 and pathology, the exact p-value is 1.0000.
Realised margin: +0 streams difference.
Verdict: pass. The sign stream is a function of z alone, independent of beta and the scale factor, so constancy across Gamma is an identity of the design. The comparison uses disjoint seed blocks and carries information.
Source: exp_R05_scale_law_a.log:22-23

### control c — Concept orthogonality (ramp 2e5)
Tests that Concept hold-out FPR equals detection under the ramp across all 60 cells.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised: Concept hold-out FPR 0.0425, detection under the ramp in [0.0350, 0.0350] across all 60 cells.
Verdict: pass. The sign stream does not see the pathology, so this equality is an identity of the design; the positive control of step a shows the instrument responsive.
Source: exp_R05_scale_law_b_2e5.log:26

### control c — Concept orthogonality (ramp 3e6)
Tests that Concept hold-out FPR equals detection under the ramp across all 85 cells.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised: Concept hold-out FPR 0.0850, detection under the ramp in [0.0525, 0.0525] across all 85 cells.
Verdict: pass. The sign stream does not see the pathology, so this equality is an identity of the design; the positive control of step a shows the instrument responsive.
Source: exp_R05_scale_law_b_3e6.log:31

### control d — OLS fit robustness (abrupt)
Tests the robustness of the ADD vs Gamma linear fit by comparing all-points fit to the fit excluding Gamma=1.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised margin: slope moves 1.1% and intercept 19.0% between the two fits. All points: ADD = 26.0016 Gamma + 32.1980, R^2 = 0.991299, max relative residual 54.5% at Gamma = 1.00. Excluding Gamma = 1: ADD = 25.7038 Gamma + 38.3027, R^2 = 0.990324, max relative residual 48.9%.
Verdict: pass. v87 prints the all-points fit; the alternative is reported, not adopted.
Source: exp_R05_scale_law_a.log:24-26

### positive control — location shift detection
Tests that the Concept monitor is responsive to a pure location shift.
Trigger probability under null: Fisher exact test, two-sided. With 400/400 detections vs 22/400 under H_0, the exact p-value is 3.1e-203.
Realised margin: +378 streams, conditional delay 42.9 steps.
Verdict: pass. Concept detects 400/400 (1.0000, Wilson [0.9905, 1.0000]) against 22/400 under H_0.
Source: exp_R05_scale_law_a.log:27

### control b — common horizon homogeneity (ramp 2e5)
Tests that the common monitoring horizon H = 200000 produces homogeneous null crossing probabilities across the 5 penalties.
Trigger probability under null: chi-square test on 4 dof. The probability of at least one rejection under the null of correct calibration is 1 - (1 - 0.05)^5 = 0.226.
Realised margin: chi-square = 1.11, p = 0.893.
Verdict: pass. Realised null levels [0.045, 0.055, 0.0575, 0.0575, 0.0475] ([18, 22, 23, 23, 19] alarms of 400); pooled realised level 0.0525, Wilson [0.0436, 0.0632], against the 0.05 v87 states for every Data arm. Target inside the interval.
Source: exp_R05_scale_law_b_2e5.log:20-23

### control h — family-wise error rate guard (ramp 2e5)
Tests that the 5 simultaneous cells at a 0.05 level do not use a per-cell binary gate.
Trigger probability under null: 1 - (1 - 0.05)^5 = 0.226. Above 5%, so no per-cell binary gate is used; the levels are tested as a distribution instead.
Realised margin: per-cell two-sided binomial p-values [0.7312, 0.6452, 0.4898, 0.4898, 0.9089]; Kolmogorov-Smirnov against Uniform(0,1): D = 0.4898, p = 0.1261.
Verdict: pass. Descriptive, retained in the CSV, and not an acceptance criterion.
Source: exp_R05_scale_law_b_2e5.log:23-24

### control b — common horizon homogeneity (ramp 3e6)
Tests that the common monitoring horizon H = 3000000 produces homogeneous null crossing probabilities across the 5 penalties.
Trigger probability under null: chi-square test on 4 dof. The probability of at least one rejection under the null of correct calibration is 1 - (1 - 0.05)^5 = 0.226.
Realised margin: chi-square = 3.07, p = 0.546.
Verdict: pass. Realised null levels [0.025, 0.035, 0.035, 0.04, 0.0475] ([10, 14, 14, 16, 19] alarms of 400); pooled realised level 0.0365, Wilson [0.0291, 0.0456], against the 0.05 v87 states for every Data arm. Target OUTSIDE the interval.
Source: exp_R05_scale_law_b_3e6.log:25-27

### control h — family-wise error rate guard (ramp 3e6)
Tests that the 5 simultaneous cells at a 0.05 level do not use a per-cell binary gate.
Trigger probability under null: 1 - (1 - 0.05)^5 = 0.226. Above 5%, so no per-cell binary gate is used; the levels are tested as a distribution instead.
Realised margin: per-cell two-sided binomial p-values [0.0208, 0.2054, 0.2054, 0.4218, 0.9089]; Kolmogorov-Smirnov against Uniform(0,1): D = 0.3946, p = 0.3235.
Verdict: pass. Descriptive, retained in the CSV, and not an acceptance criterion.
Source: exp_R05_scale_law_b_3e6.log:28-29

### control f — recalibration rule margins (ramp 2e5)
Tests the departure from the lambda_iid x Gamma rule at H = 200000.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised margin: lambda*(Gamma)/Gamma = [132.1, 126.8, 135.0, 150.7, 179.2] against lambda_iid_H = 128.63; departure from the rule -1.4% to +39.3%.
Verdict: pass. Margins by Gamma: [2.7, -1.4, 4.9, 17.2, 39.3].
Source: exp_R05_scale_law_b_2e5.log:25

### control f — recalibration rule margins (ramp 3e6)
Tests the departure from the lambda_iid x Gamma rule at H = 3000000.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised margin: lambda*(Gamma)/Gamma = [326.5, 327.6, 379.0, 436.5, 555.0] against lambda_iid_H = 282.54; departure from the rule +15.6% to +96.4%.
Verdict: pass. Margins by Gamma: [15.6, 15.9, 34.2, 54.5, 96.4]. The span widens from [-1.4, +39.3]% at H = 200000 to [+15.6, +96.4]% at H = 3000000. The degradation with the horizon that v87 asserts is visible in these two budgets.
Source: exp_R05_scale_law_b_3e6.log:30, exp_R05_scale_law_c.log:38-40

### control e — moment boundary
Tests the closed-form sixth-moment boundary for standardized t_7.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised: E[eps^6] is finite up to beta = 0.874405, i.e. Gamma = 7.0793. E[eps^4] survives much further, to beta = 0.907117, Gamma = 41.5843. Largest finite moment order at Gamma = 20 is 4 + 0.7931.
Verdict: pass. THIS EXPERIMENT SWEEPS NO nu. Every campaign runs standardized t_7, so no output of R05 can attribute the degradation of the recalibration rule to the loss of a moment: what R05 measures is that the departure from lambda_iid x Gamma grows with Gamma and with the horizon, and what the closed form above supplies is a boundary that happens to fall inside the same range of Gamma. The coincidence is an association. Establishing the mechanism would need an arm varying nu at fixed Gamma, and this experiment has none. v87 app:scaling glosses E[eps^6] as 'the second moment of the monitored statistic eps^2'. E[eps^6] is the THIRD moment of eps^2; the second is E[eps^4], whose boundary sits at Gamma = 41.6, far outside the grid. The numeral 7.1 is reproduced; the description attached to it is not.
Source: exp_R05_scale_law_c.log:33-36

## 3. Test suite

```
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-0.70.0, pluggy-1.6.0 -- /home/m53/miniforge3/envs/Trading/bin/python
cachedir: .pytest_cache
rootdir: /home/m53/The-Whitening-Advantage-Experiments
plugins: anyio-10.4.0
collecting ... collected 22 items

tests/test_R05_claims.py::test_abrupt_cardinality PASSED                 [  4%]
tests/test_R05_claims.py::test_ramp_cardinalities PASSED                 [  9%]
tests/test_R05_claims.py::test_protocol_constants PASSED                 [ 13%]
tests/test_R05_claims.py::test_horizons_are_the_two_published_budgets PASSED [ 18%]
tests/test_R05_claims.py::test_common_horizon_is_constant_across_gamma PASSED [ 22%]
tests/test_R05_claims.py::test_null_levels_are_homogeneous_across_gamma PASSED [ 27%]
tests/test_R05_claims.py::test_concept_branch_is_gamma_invariant_by_construction PASSED [ 31%]
tests/test_R05_claims.py::test_concept_is_blind_to_the_scale_pathology PASSED [ 36%]
tests/test_R05_claims.py::test_positive_control_shows_the_monitor_responsive PASSED [ 40%]
tests/test_R05_claims.py::test_both_crossovers_are_emitted_and_are_distinct PASSED [ 45%]
tests/test_R05_claims.py::test_scaling_law_branches_meet_at_the_crossover PASSED [ 50%]
tests/test_R05_claims.py::test_ladder_visits_the_three_published_horizons PASSED [ 54%]
tests/test_R05_claims.py::test_ladder_is_monotone_in_the_horizon PASSED [ 59%]
tests/test_R05_claims.py::test_ladder_agrees_with_the_campaigns_it_overlaps PASSED [ 63%]
tests/test_R05_claims.py::test_sixth_moment_boundary_matches_the_published_gamma PASSED [ 68%]
tests/test_R05_claims.py::test_moment_margin_macro_matches_the_published_bound PASSED [ 72%]
tests/test_R05_claims.py::test_macro_file_is_well_formed PASSED          [ 77%]
tests/test_R05_claims.py::test_required_macros_are_present PASSED        [ 81%]
tests/test_R05_claims.py::test_figure_exists PASSED                      [ 86%]
tests/test_R05_claims.py::test_text_artefacts_end_with_a_newline PASSED  [ 90%]
tests/test_R05_claims.py::test_superseded_witness_is_documented_not_regenerated PASSED [ 95%]
tests/test_R05_claims.py::test_report_deviation_classification 
--- R05 deviation classification against v87 ---
                   quantity  published  regenerated  printed_decimals degree                                                 source_cell
               abrupt_slope      23.70    26.001631                 1     D2       R05_abrupt_add_vs_gamma.csv, OLS of ADD_Data on Gamma
           abrupt_intercept      38.00    32.198021                 0     D2       R05_abrupt_add_vs_gamma.csv, OLS of ADD_Data on Gamma
          sqrt_rule_fpr_pct      31.00    24.500000                 0     D2        R05_abrupt_add_vs_gamma.csv, FPR_rule_xSqrtGamma max
   scaling_median_error_pct       5.40     5.346536                 1     D2            R05_ramp_multigamma_2e5.csv, ADD_Data vs Eq. (5)
 recalib_margin_min_pct_2e5       7.00    -1.420701                 0     D2         R05_ramp_multigamma_2e5.csv, lambda_star_Data/Gamma
 recalib_margin_max_pct_2e5      29.00    39.288641                 0     D2         R05_ramp_multigamma_2e5.csv, lambda_star_Data/Gamma
             lambda_iid_2e5     129.50   128.631853                 1     D2                   R05_ramp_multigamma_2e5.csv, lambda_iid_H
       grid_reach_wstar_2e5      22.50    22.500988                 1     D1     R05_ramp_multigamma_2e5.csv, w_over_wstar_predicted max
      censoring_max_pct_2e5       1.30     0.250000                 1     D2              R05_ramp_multigamma_2e5.csv, censored_Data max
      detection_min_pct_2e5      98.70    99.750000                 1     D2               R05_ramp_multigamma_2e5.csv, DetRate_Data min
  lambda_over_gamma_min_2e5     138.00   126.804379                 0     D2         R05_ramp_multigamma_2e5.csv, lambda_star_Data/Gamma
  lambda_over_gamma_max_2e5     167.00   179.169559                 0     D2         R05_ramp_multigamma_2e5.csv, lambda_star_Data/Gamma
        sd_over_add_max_2e5       3.20     0.940909                 1     D2      R05_ramp_multigamma_2e5.csv, SEM_Data and DetRate_Data
       med_over_add_min_2e5       0.68     0.758602                 2     D2              R05_ramp_multigamma_2e5.csv, MED_Data/ADD_Data
        rho_w_share_pct_2e5      58.00    57.259679                 0     D2                       R05_ramp_multigamma_2e5.csv, widest w
           exponent_min_2e5       0.65     0.679887                 2     D2    R05_ramp_multigamma_2e5.csv, ramp fit on w_delta_applied
           exponent_max_2e5       0.71     0.697822                 2     D2    R05_ramp_multigamma_2e5.csv, ramp fit on w_delta_applied
     model_exponent_min_2e5       0.71     0.708701                 2     D1 R05_ramp_multigamma_2e5.csv, Eq. (5) fit on w_delta_applied
     model_exponent_max_2e5       0.73     0.719008                 2     D2 R05_ramp_multigamma_2e5.csv, Eq. (5) fit on w_delta_applied
             lambda_iid_3e6     303.00   282.536302                 1     D2                   R05_ramp_multigamma_3e6.csv, lambda_iid_H
       grid_reach_wstar_3e6     225.00   224.999974                 1     D1     R05_ramp_multigamma_3e6.csv, w_over_wstar_predicted max
low_gamma_max_error_pct_3e6       5.70     5.797607                 1     D2          R05_ramp_multigamma_3e6.csv, Gamma <= 4 vs Eq. (5)
        rho_w_share_pct_3e6      78.00    78.106010                 0     D1                       R05_ramp_multigamma_3e6.csv, widest w
 recalib_margin_max_pct_3e6      96.00    96.435906                 0     D1         R05_ramp_multigamma_3e6.csv, lambda_star_Data/Gamma
         sixth_moment_gamma       7.10     7.079317                 1     D1                                 closed form, no Monte Carlo
 moment_margin_at_gamma_max       0.80     0.793127                 1     D1                                 closed form, no Monte Carlo
      lambda_iid_ladder_77k     102.80   111.025130                 1     D2                       R05_lambda_iid_horizon.csv, H = 77000

--- Concept threshold, witness against regenerated ---
 abrupt: witness lambda_star_Concept = 10.8000, FPR = 0.0950
    2e5: witness lambda_star_Concept = 15.8100, FPR = 0.0525
    3e6: witness lambda_star_Concept = 19.0200, FPR = 0.0550

The v87 numeral lambda_C = 10 matches none of the three. See docs/sections/R05.md.
PASSED    [100%]

============================== 22 passed in 0.71s ==============================
```

Total: 22 passed.

## 4. Reproducibility digests

NOT RECOVERABLE FROM THE LOG.

current tree, single run:
```
9e4a09c4a28b66478a965fbb6a026f50d1aceacc18a1b5cb77100cec124294fd  results/R05_scale_law/data/R05_abrupt_add_vs_gamma.csv
c29bdc53638287a38f34adf4431c433ae30f775e0644273a6c80ad94525c2808  results/R05_scale_law/data/R05_concept_positive_control.csv
f6d28d282c2290a9e7b948e1b186a7577ed5c434b226e5986044c9f711aea2df  results/R05_scale_law/data/R05_deviation_classification.csv
91812bd9de76bebf07fa8ce6779754087cb5db143873442cc945daa5a74f37e1  results/R05_scale_law/data/R05_lambda_iid_horizon.csv
02d13472afe6e724ec6a7222442a99e369584438cbcb34706f6e11b3ac0ba564  results/R05_scale_law/data/R05_ramp_multigamma_2e5.csv
15d770b8d43b5e33b18b50729c1aa28f993f1e2e2a8d598554fa777f16a2b72a  results/R05_scale_law/data/R05_ramp_multigamma_3e6.csv
7e0871097907d12dd9d4f89b982321747fe65170001dc3a561c4ea525fae357d  results/R05_scale_law/tables/R05_claims.tex
```

## 5. Design decisions taken outside the plan

1. Budget 2e5: the cap of 200000 bound. The fixed point wanted 335977 steps to reach the SAFETY target of 8x the deterministic prediction at the widest ramp. SAFETY is a design target this budget does NOT reach; the realised margin is 4.76x. Censoring is measured directly per cell and is the quantity that decides admissibility.
   Source: exp_R05_scale_law_b_2e5.log:9

2. Budget 3e6: the cap of 3000000 bound. The fixed point wanted 5424696 steps to reach the SAFETY target of 8x the deterministic prediction at the widest ramp. SAFETY is a design target this budget does NOT reach; the realised margin is 4.42x. Censoring is measured directly per cell and is the quantity that decides admissibility.
   Source: exp_R05_scale_law_b_3e6.log:9

3. Driving steps a and b in this process: their frames are received in memory and no CSV is read back (SPECS 1.6).
   Source: exp_R05_scale_law_c.log:7

4. v87 prints the all-points OLS fit for ADD vs Gamma; the alternative fit excluding Gamma = 1 is reported, not adopted.
   Source: exp_R05_scale_law_a.log:26

## 6. Open questions, left open

1. Can the degradation of the recalibration rule with Gamma and horizon be attributed to the loss of a moment mechanism? Establishing the mechanism would need an arm varying nu at fixed Gamma, and this experiment has none.
   Source: exp_R05_scale_law_c.log:35

2. Is the coincidence that the closed-form moment boundary falls inside the same range of Gamma as the measured degradation of the recalibration rule a causal relationship or merely an association?
   Source: exp_R05_scale_law_c.log:35
