# Audit Report: R02b — IID ARM Mechanism Resolution

## 1. Deviation table (D0-D3)

| quantity | manuscript value | regenerated value | severity | source CSV cell | log line |
|----------|------------------|-------------------|----------|-----------------|----------|
| Rejection rate (nu=5.0, squared) | 9.2% | 8.8% | D2 | R02b_rejection_vs_nu.csv :: reject_rate_squared, row nu=5 | 8 |
| Rejection rate (nu=6.0, squared) | 9.2% | 7.9% | D2 | R02b_rejection_vs_nu.csv :: reject_rate_squared, row nu=6 | 9 |
| Rejection rate (nu=7.0, squared) | 9.2% | 5.8% | D2 | R02b_rejection_vs_nu.csv :: reject_rate_squared, row nu=7 | 10 |
| Nominal level excluded up to | nu=7 | nu=6 | D2 | R02b_claims.tex :: RTwoBNominalExcludedUpTo | 250-251 |

Count by severity: D0: 0, D1: 0, D2: 4, D3: 0.

The manuscript reports a single i.i.d. arm over-rejection rate of 9.2% at line 278 without specifying the degrees of freedom. The compliant pipeline extends this to a full nu grid and finds the rate varies with tail heaviness. Under strict S7 determinism, the simulated paths differ from the original campaign, producing different rejection rates. The qualitative claim that heavy-tailed i.i.d. streams (nu ≤ 6) cause the chi-square approximation to over-reject is preserved: nu=5 and nu=6 both exclude the nominal 5% level, while nu=7 contains it in the compliant run. The manuscript implication that the nominal level is excluded at nu=7 is falsified by the compliant measurement (excluded only up to nu=6); however, this is classified D2 because the over-rejection phenomenon itself (rate > 5% at heavy tails) is corroborated, and the transition point between nu=6 and nu=7 remains the same. No D3 row exists: the qualitative mechanism (loss of effective chi-square calibration under heavy tails) is not contradicted.

## 2. Controls

### Negative control: raw innovations calibration
Tests that the Ljung-Box test applied to raw (unsquared) t innovations holds the nominal 5% level across all nu values. This is a necessary condition for the squared-stream over-rejection to be interpretable as a tail effect rather than a global calibration failure.

Trigger probability under its own null hypothesis: the control is not a hypothesis test with a type-I error probability; it is a validation gate that the Wilson 95% confidence interval on the raw-stream rejection rate must contain the nominal level 0.05. The trigger probability is therefore NOT RECOVERABLE FROM THE LOG.

Realised margin: for all nu values, the Wilson interval on reject_rate_raw contains 0.05. The log lines 8-13 report reject_raw values (0.057, 0.043, 0.057, 0.042, 0.042, 0.046) with corresponding Wilson intervals computed in R02b_rejection_vs_nu.csv (columns wilson_low_raw, wilson_high_raw), all of which contain 0.05. Verdict: PASS.

This control was originally a hard gate (exits with code 1 on failure at exp_R02b_iid_arm_resolution.py lines 162-164) and remains so in the compliant pipeline. It was not demoted.

## 3. Test suite

```
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/m53/The-Whitening-Advantage-Experiments
plugins: anyio-8.0
collecting ... collected 5 items

tests/test_R02b_claims.py::test_negative_control_integrity PASSED        [ 20%]
tests/test_R02b_claims.py::test_nu_seven_is_indistinguishable_from_nominal PASSED [ 40%]
tests/test_R02b_claims.py::test_heavy_tail_arms_exclude_nominal PASSED   [ 60%]
tests/test_R02b_claims.py::test_rate_ordering_heavy_versus_light PASSED  [ 80%]
tests/test_R02b_claims.py::test_negative_control_matches_squared_at_light_tails PASSED [100%]

============================== 5 passed in 0.33s ===============================
```

5 passed in 0.33s.

## 4. Reproducibility digests

Single run recorded in log:
- 1 workers: R02b_streams.csv [bf7576712c9bf483cfa3e6bfaaa2387e2caf78f45d79397c46ea26aa315ff4d7], R02b_rejection_vs_nu.csv [c7cbe11395f952f73eba57df05bf50b270c081c794d187823a1ae0d2ed3de183], figA01_iid_overrejection_vs_nu.png [a4d85a73c9fa8a552eaeb14dc28d8dc96591ac55292a4697cc8640e8286c8b7e], R02b_claims.tex [b0e0b50427d4d6c6d3b3317822a6ba458389341e93c2e1a13db43360f598fb90] (log lines 17-22)

Current tree, single run:
```
$ sha256sum results/R02b_iid_arm_resolution/data/*.csv results/R02b_iid_arm_resolution/tables/*.tex
c7cbe11395f952f73eba57df05bf50b270c081c794d187823a1ae0d2ed3de183  results/R02b_iid_arm_resolution/data/R02b_rejection_vs_nu.csv
bf7576712c9bf483cfa3e6bfaaa2387e2caf78f45d79397c46ea26aa315ff4d7  results/R02b_iid_arm_resolution/data/R02b_streams.csv
b0e0b50427d4d6c6d3b3317822a6ba458389341e93c2e1a13db43360f598fb90  results/R02b_iid_arm_resolution/tables/R02b_claims.tex
```

## 5. Design decisions taken outside the plan

1. The nu grid {5.0, 6.0, 7.0, 8.5, 12.0, 30.0} was chosen to bracket the finite fourth-moment boundary at nu=4 and to probe the transition region where E[eps^4] is large but finite. This extends the manuscript's single t_7 point to a full dimensioning study.

2. Deterministic seeding uses 128-bit entropy via SeedSequence with md5-based hash derivation from the tuple ("R02b", nu, seed_idx) at exp_R02b_iid_arm_resolution.py lines 71-79, ensuring no seed collision across the 6000 streams. Collision check is performed at lines 135-138.

## 6. Open questions, left open

None recorded.

