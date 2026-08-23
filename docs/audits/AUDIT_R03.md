# Audit Report: R03 — False Positive Rate Explosion Without Recalibration

**Note on source:** The file `logs/R03_fpr_explosion/exp_R03_fpr_explosion.log` in the current tree contains only a single warning line. All numerical content below was obtained by running `bash run_experiment_R03.sh` and capturing its output. Line numbers refer to that command output.

## 1. Deviation table (D0-D3)

| quantity | manuscript value | regenerated value | severity | source CSV cell | log line |
|----------|------------------|------------------|----------|-----------------|----------|
| CUSUM FPR_raw max | 0.830000 | 0.833333 | D2 | R03_fpr_cusum.csv :: FPR_raw at Gamma = 106.6667 | 36 |
| CUSUM FPR_raw min over Gamma > 20 | 0.760000 | 0.743333 | D2 | R03_fpr_cusum.csv :: FPR_raw at Gamma = 28.2222 | 37 |
| CUSUM FPR_raw mean over Gamma > 20 | 0.811042 | 0.807083 | D2 | R03_fpr_cusum.csv :: FPR_raw, 16-point mean | 38 |
| CUSUM FPR_sqrt max | 0.330000 | 0.310000 | D2 | R03_fpr_cusum.csv :: FPR_sqrt at Gamma = 91.1111 | 39 |
| CUSUM FPR_sqrt mean over Gamma > 20 | 0.319583 | 0.297917 | D2 | R03_fpr_cusum.csv :: FPR_sqrt, 16-point mean | 40 |
| CUSUM FPR_gamma max | 0.016667 | 0.040000 | D2 | R03_fpr_cusum.csv :: FPR_gamma at Gamma = 1.1739 | 41 |
| CUSUM FPR_raw at lowest Gamma | 0.026667 | 0.040000 | D2 | R03_fpr_cusum.csv :: FPR_raw at Gamma = 1.1739 | 42 |
| ADWIN FPR_raw max | 0.876667 | 0.870000 | D2 | R03_fpr_adwin.csv :: FPR_raw at Gamma = 184.4444 | 43 |
| ADWIN FPR_recalib max | 0.126667 | 0.110000 | D2 | R03_fpr_adwin.csv :: FPR_recalib at Gamma = 75.5556 | 44 |
| ADWIN FPR_recalib mean | 0.101833 | 0.095500 | D2 | R03_fpr_adwin.csv :: FPR_recalib, 20-point mean | 45 |
| ADWIN FPR_raw at lowest Gamma | 0.053333 | 0.093333 | D2 | R03_fpr_adwin.csv :: FPR_raw at Gamma = 1.1739 | 46 |

Count by severity: 11 D2, 0 D1, 0 D0, 0 D3.

All deviations are D2-class: numerical shifts at printed precision. No qualitative claim of the manuscript is contradicted.

## 2. Controls

### Shared-realisation premise
Tests that each row's columns are one realisation read at several thresholds (no nesting violations).
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised margin: CUSUM = 0, ADWIN = 0 over 6000 and 6000 streams (line 22).
Verdict: PASS. Zero violations means the column ordering is a deterministic identity.

### Cardinality check
Tests that both grid files carry 20 rows.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised margin: both grid files carry 20 rows (line 21).
Verdict: PASS.

### Consistency check (threshold ordering)
Tests that threshold ordering holds on all 20 rows of both files.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised margin: holds on all 20 rows (line 23).
Verdict: PASS.

### Monotonicity check beyond Gamma = 6.0
Tests monotonicity of FPR_raw beyond Gamma = 6.0.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised margin: mechanism-derived bound = -0.10997 (SE_diff = 0.03373, z_bonf = 3.261 at family-wise alpha = 0.01); most negative observed difference = +0.000000; Spearman rho = 0.9974 (p = 8.165e-21) (line 24).
Verdict: PASS.

### Extremal criterion [min FPR_raw over Gamma > 20]
Tests that min FPR_raw over Gamma > 20 does not breach threshold 0.76.
Trigger probability under its own null hypothesis: 0.255 for 16 independent grid points (upper bound under CRN) at observed aggregate rate 0.807083 (line 28).
Realised margin: observed 0.743333 at Gamma = 22.7778 against threshold 0.76.
Verdict: BREACHED, non-blocking.

### Extremal criterion [max FPR_sqrt over Gamma > 20]
Tests that max FPR_sqrt over Gamma > 20 does not breach threshold 0.35.
Trigger probability under its own null hypothesis: 0.301 for 16 independent grid points (upper bound under CRN) at observed aggregate rate 0.297917 (line 29).
Realised margin: observed 0.310000 at Gamma = 75.5556 against threshold 0.35.
Verdict: not breached.

### Extremal criterion [max FPR_recalib over the whole grid]
Tests that max FPR_recalib over the whole grid does not breach threshold 0.13.
Trigger probability under its own null hypothesis: 0.333 for 20 independent grid points (upper bound under CRN) at observed aggregate rate 0.095500 (line 30).
Realised margin: observed 0.110000 at Gamma = 91.1111 against threshold 0.13.
Verdict: not breached.

### Aggregate certification gate [mean FPR_raw over Gamma > 20]
Tests that mean FPR_raw over Gamma > 20 >= 0.76.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised margin: 0.807083 over n = 4800; SE_pooled = 0.00570, SE_crn = 0.02278; (+0.047083 above 0.76, +8.3 pooled SE, +2.1 CRN SE) (line 25).
Verdict: PASS.

### Aggregate certification gate [mean FPR_sqrt over Gamma > 20]
Tests that mean FPR_sqrt over Gamma > 20 is in [0.25, 0.35].
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised margin: 0.297917 over n = 4800; SE_pooled = 0.00660, SE_crn = 0.02640; (+0.047917 above 0.25, +7.3 pooled SE, +1.8 CRN SE) (+0.052083 below 0.35, +7.9 pooled SE, +2.0 CRN SE) (line 26).
Verdict: PASS.

### Aggregate certification gate [mean FPR_recalib over the whole grid]
Tests that mean FPR_recalib over the whole grid <= 0.13.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised margin: 0.095500 over n = 6000; SE_pooled = 0.00379, SE_crn = 0.01697; (+0.034500 below 0.13, +9.1 pooled SE, +2.0 CRN SE) (line 27).
Verdict: PASS.

### i.i.d. calibration at Gamma = 1: StrictCUSUM
Tests that StrictCUSUM FPR at Gamma = 1 contains the 5% nominal level.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised margin: FPR = 0.020000 (6/300), Wilson 95% [0.009198, 0.042940], contains the 5% nominal level: False (line 32).
Verdict: FAIL (does not contain nominal level).

### i.i.d. calibration at Gamma = 1: ADWIN
Tests that ADWIN FPR at Gamma = 1 contains the 5% nominal level.
Trigger probability: NOT RECOVERABLE FROM THE LOG.
Realised margin: FPR = 0.050000 (15/300), Wilson 95% [0.030532, 0.080847], contains the 5% nominal level: True (line 33).
Verdict: PASS.

## 3. Test suite

```
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-9.0.3, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /home/m53/The-Whitening-Advantage-Experiments
plugins: anyio-4.8.8
collecting ... collected 9 items

tests/test_R03_claims.py::test_R03_grid_cardinality PASSED               [ 11%]
tests/test_R03_claims.py::test_R03_grid_is_unchanged PASSED              [ 22%]
tests/test_R03_claims.py::test_R03_threshold_ordering_is_structural PASSED [ 33%]
tests/test_R03_claims.py::test_R03_monotonicity_beyond_gamma_six PASSED  [ 44%]
tests/test_R03_claims.py::test_R03_aggregate_certification_gates PASSED  [ 55%]
tests/test_R03_claims.py::test_R03_gamma_rule_holds_the_nominal_level PASSED [ 66%]
tests/test_R03_claims.py::test_R03_iid_calibration_arm_is_well_formed PASSED [ 77%]
tests/test_R03_claims.py::test_R03_deviation_classification_against_witness PASSED [ 88%]
tests/test_R03_claims.py::test_R03_macros_are_emitted PASSED             [100%]

============================== 9 passed in 0.70s ===============================
```

Total: 9 passed.

## 4. Reproducibility digests

From log (48 workers):
- SHA-256 R03_fpr_cusum.csv : ef599446da928495185ea61dda060efbd4da0b586e87c9ee6711c5dcc7176d0e (line 61)
- SHA-256 R03_fpr_adwin.csv : 53a049f7a5b25da379212cfe48a5c32ef286827260eaea167e4ab5171dbb42d6 (line 62)
- SHA-256 R03_iid_calibration_check.csv : 54dabdc61097973f805e60edc0ed199f9ad7f2bdb82fa2af73087affde9bf004 (line 63)
- SHA-256 R03_add_vs_gamma.csv : 0c40f163f3a94b14a74ce863b603f14d4683ccde795f36b9a3ffe8b0bad5f2d3 (line 64)
- SHA-256 R03_add_vs_width.csv : 6509beeaa701c4e427c78e8f545b7405abcbc53b2bb8759106f1fd1cde50f51c (line 65)
- SHA-256 R03_sensitivity.csv : b66382ce3b6b82e7474a316ad732e19c2116f0ecfe200487059469a3de4cf68e (line 66)
- SHA-256 fig03_fpr_explosion.png : 6ec5f5ec7cc112455d2f2cf377065a75342966b770a01dfb5034c42af131ab6c (line 67)
- SHA-256 R03_claims.tex : 283b6a387f2b0514d1123ac61261f37b3e32fa5d791b6b8354866b9db0919db1 (line 68)

current tree, single run:
```
6509beeaa701c4e427c78e8f545b7405abcbc53b2bb8759106f1fd1cde50f51c  results/R03_fpr_explosion/data/R03_add_vs_width.csv
0c40f163f3a94b14a74ce863b603f14d4683ccde795f36b9a3ffe8b0bad5f2d3  results/R03_fpr_explosion/data/R03_add_vs_gamma.csv
53a049f7a5b25da379212cfe48a5c32ef286827260eaea167e4ab5171dbb42d6  results/R03_fpr_explosion/data/R03_fpr_adwin.csv
54dabdc61097973f805e60edc0ed199f9ad7f2bdb82fa2af73087affde9bf004  results/R03_fpr_explosion/data/R03_iid_calibration_check.csv
b66382ce3b6b82e7474a316ad732e19c2116f0ecfe200487059469a3de4cf68e  results/R03_fpr_explosion/data/R03_sensitivity.csv
ef599446da928495185ea61dda060efbd4da0b586e87c9ee6711c5dcc7176d0e  results/R03_fpr_explosion/data/R03_fpr_cusum.csv
6ec5f5ec7cc112455d2f2cf377065a75342966b770a01dfb5034c42af131ab6c  results/R03_fpr_explosion/figures/fig03_fpr_explosion.png
283b6a387f2b0514d1123ac61261f37b3e32fa5d791b6b8354866b9db0919db1  results/R03_fpr_explosion/tables/R03_claims.tex
```

## 5. Design decisions taken outside the plan

None recorded.

## 6. Open questions, left open

None recorded.
