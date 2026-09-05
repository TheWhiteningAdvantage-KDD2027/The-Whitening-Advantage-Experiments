# Audit Report: R02c — Horizon Sweep and Eighth-Moment Account Falsification

## 1. Deviation table (D0-D3)

NOT RECOVERABLE FROM THE LOG.

## 2. Controls

### Negative control: raw innovations calibration
Tests that the Ljung-Box test applied to raw (unsquared) Student t innovations holds the nominal 5% level across all 12 cells (3 nu x 4 horizons). This is a necessary condition for the squared-stream over-rejection to be interpretable as a tail effect rather than a global calibration failure.

Trigger probability under its own null hypothesis: 1 - (1 - 0.05)^12 = 0.460 (log line 12).

Realised margin: S4bis Substituted KS test on the 12 raw-stream p-values yields KS_stat=0.2380, p-value=0.4374 (log lines 12-13). p-value > 0.05, therefore the raw arm is calibrated. Verdict: PASS.

This control is a hard gate in exp_R02c_horizon_sweep.py lines 268-282; it was not demoted.

### Witness control: nu=7 squared innovations calibration
Tests that the Ljung-Box test applied to squared Student t innovations with nu=7 holds the nominal 5% level across all 4 horizons. This is the witness arm that falsifies the eighth-moment explanation: if nu=7 (where E[eps^8] = infinity) were over-rejecting, the eighth-moment account would be corroborated.

Trigger probability under its own null hypothesis: 1 - (1 - 0.05)^4 = 0.185 (log line 14).

Realised margin: S4bis Substituted KS test on the 4 squared-stream p-values for nu=7 yields KS_stat=0.3666, p-value=0.5480 (log lines 14-15). p-value > 0.05, therefore the nu=7 arm is calibrated. Verdict: PASS.

This control is a hard gate in exp_R02c_horizon_sweep.py lines 284-297; it was not demoted.

## 3. Test suite

```
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-9.3.3, pluggy-1.6.0 -- /home/m53/miniforge3/envs/Trading/bin/python
cachedir: .pytest_cache
rootdir: /home/m53/The-Whitening-Advantage-Experiments
plugins: anyio-4.8.0
collecting ... collected 7 items

tests/test_R02c_claims.py::test_R02c_seed_uniqueness PASSED              [ 14%]
tests/test_R02c_claims.py::test_R02c_negative_control_calibration PASSED [ 28%]
tests/test_R02c_claims.py::test_R02c_eighth_moment_account_is_refuted PASSED [ 42%]
tests/test_R02c_claims.py::test_R02c_slope_test_power_is_declared PASSED [ 57%]
tests/test_R02c_claims.py::test_R02c_control_arm_integrity PASSED        [ 71%]
tests/test_R02c_claims.py::test_R02c_continuity PASSED                   [ 85%]
tests/test_R02c_claims.py::test_R02c_mechanism_slope_logic PASSED        [100%]

============================== 7 passed in 0.34s ===============================
```

7 passed in 0.34s.

Command: `pytest tests/test_R02c_claims.py -v`

## 4. Reproducibility digests

SHA-256 digests from log lines 20-22, 24-25 (single run, 1 worker):

```
9c8e24a6c0434e08d579cf1859abd0fdfa25ed923c243ea0eabeb5f4570c212c  results/R02c_horizon_sweep/data/R02c_streams.csv
4d47c65ef4decf65474103842add8c5ebb8b081c143eaa876945a60dbfb55f21  results/R02c_horizon_sweep/data/R02c_rejection_vs_horizon.csv
b90f95a77d3dd6ce0860b76d99b3134f2c40a6b204472f76d7a6cafbc9205a09  results/R02c_horizon_sweep/figures/figA02_overrejection_vs_horizon.png
f708ff62ee90c41f7c18b1e7ccaff3f563af9ec0575794a293318e295e6a1498  results/R02c_horizon_sweep/tables/R02c_claims.tex
```

current tree, single run:

```
$ sha256sum results/R02c_horizon_sweep/data/*.csv results/R02c_horizon_sweep/tables/*.tex
4d47c65ef4decf65474103842add8c5ebb8b081c143eaa876945a60dbfb55f21  results/R02c_horizon_sweep/data/R02c_rejection_vs_horizon.csv
9c8e24a6c0434e08d579cf1859abd0fdfa25ed923c243ea0eabeb5f4570c212c  results/R02c_horizon_sweep/data/R02c_streams.csv
f708ff62ee90c41f7c18b1e7ccaff3f563af9ec0575794a293318e295e6a1498  results/R02c_horizon_sweep/tables/R02c_claims.tex
```

## 5. Design decisions taken outside the plan

1. Continuity guard at exp_R02c_horizon_sweep.py lines 114-117: for n_steps=8000, the seeding is forced to reuse the exact state from R02b via get_deterministic_seed("R02b", nu, seed_idx) to guarantee exact matching of the printed 8.8% claim for nu=5. This ensures continuity with the R02b stream.

2. Seed derivation uses 128-bit SeedSequence entropy with md5-based hash derivation from the tuple ("R02c", nu, n_steps, seed_idx) for non-8000 horizons at exp_R02c_horizon_sweep.py line 118, ensuring 12000 unique seeds across 3 nu x 4 horizons x 1000 streams.

3. The slope test is explicitly bounded to prevent misinterpretation: exp_R02c_horizon_sweep.py lines 254-260 log whether the slope CI is significantly negative, positive, or indistinguishable from zero, with the conclusion "H1 refuted, H2 not refuted" when the CI contains zero (log lines 9-11).

## 6. Open questions, left open

None recorded.

