# AUDIT — R03, false positive rate explosion (Figure 3)

Every measured block below is extracted from `logs/R03_fpr_explosion/exp_R03_fpr_explosion.log`
or from the captured `pytest` run. None is retyped.

**Starting state.** `experiments/R03_fpr_explosion/exp_R03_fpr_explosion.py`,
`run_experiment_R03.sh`, `tests/test_R03_claims.py`, `docs/sections/R03.md` and
`requirements/R03.txt` were already present in the repository, and none had ever produced a
result: `results/R03_fpr_explosion/` and `logs/R03_fpr_explosion/` did not exist. The script
terminated at its import line with `ModuleNotFoundError: No module named 'experiments'`,
because it referenced `experiments.common.fair_env` without placing the repository root on
`sys.path`, unlike R01, R02, R02b and R02c which all do. That is fixed; the campaign runs.

---

## 1. Deviation classification against the submitted campaign

Read from the vendored witness with `float_precision='round_trip'` on both sides, classified at
the printing precision of v87, which prints these quantities as percentages with one decimal.

```
quantity                               |  published | regenerated | degree | source cell
CUSUM FPR_raw max                      |   0.830000 |    0.833333 |     D2 | protocol_1a[FPR_raw] at Gamma = 106.6667
CUSUM FPR_raw min over Gamma > 20      |   0.760000 |    0.743333 |     D2 | protocol_1a[FPR_raw] at Gamma = 28.2222
CUSUM FPR_raw mean over Gamma > 20     |   0.811042 |    0.807083 |     D2 | protocol_1a[FPR_raw], 16-point mean
CUSUM FPR_sqrt max                     |   0.330000 |    0.310000 |     D2 | protocol_1a[FPR_sqrt] at Gamma = 91.1111
CUSUM FPR_sqrt mean over Gamma > 20    |   0.319583 |    0.297917 |     D2 | protocol_1a[FPR_sqrt], 16-point mean
CUSUM FPR_gamma max                    |   0.016667 |    0.040000 |     D2 | protocol_1a[FPR_gamma] at Gamma = 1.1739
CUSUM FPR_raw at lowest Gamma          |   0.026667 |    0.040000 |     D2 | protocol_1a[FPR_raw] at Gamma = 1.1739
ADWIN FPR_raw max                      |   0.876667 |    0.870000 |     D2 | protocol_1b[FPR_raw] at Gamma = 184.4444
ADWIN FPR_recalib max                  |   0.126667 |    0.110000 |     D2 | protocol_1b[FPR_recalib] at Gamma = 75.5556
ADWIN FPR_recalib mean                 |   0.101833 |    0.095500 |     D2 | protocol_1b[FPR_recalib], 20-point mean
ADWIN FPR_raw at lowest Gamma          |   0.053333 |    0.093333 |     D2 | protocol_1b[FPR_raw] at Gamma = 1.1739
```

All eleven quantities are **D2**: the printed value moves, the qualitative claim it supports
holds. No D3. The `Gamma` grid is bit-identical to the witness, which the test suite asserts,
so no difference is attributable to a moved grid point.

The cause is a change of draw forced by the specifications, plus one genuine defect of the
submitted seeding:

1. `make_seed` truncated its 256-bit digest to the leading 32 bits. The 300 stream seeds of
   protocols 1A and 1B are collision-free at that width — checked, zero collisions — so the
   correction is required by the 128-bit entropy rule, not by an observed failure.
2. Protocol 2C keyed its `H_0` seed stream on `int(lambda_c * 1000 + delta_c * 100000)`, which
   maps the 15 grid cells onto **12 distinct keys**. `(5.0, 0.02)` collides with `(2.0, 0.05)`,
   `(10.0, 0.02)` with `(2.0, 0.1)`, and `(10.0, 0.05)` with `(5.0, 0.1)`: three pairs of cells
   shared a realisation where the code intended independent entropy. This affects
   `R03_sensitivity.csv`, which no version of v87 cites.

---

## 2. Certification gates

The rules were fixed and logged before any regenerated value was read:

```
Certification rule fixed before measurement: v87 "close to 80% or above once Gamma > 20" -> mean FPR_raw over Gamma > 20 >= 0.76 (0.80 less 5% in relative terms)
Certification rule fixed before measurement: v87 "residual plateau near 30%" -> mean FPR_sqrt over Gamma > 20 in [0.25, 0.35] (0.30 plus or minus 5 percentage points)
Certification rule fixed before measurement: v87 "containing the FPR below 13%" -> mean FPR_recalib over the whole grid <= 0.13 (literal numeral, no operationalisation)
```

### Blocking gates, on aggregates

```
Aggregate gate [mean FPR_raw over Gamma > 20]: 0.807083 over n = 4800 (16 grid points x 300 streams); SE_pooled = 0.00570, SE_crn = 0.02278; (+0.047083 above 0.76, +8.3 pooled SE, +2.1 CRN SE); verdict = PASS
Aggregate gate [mean FPR_sqrt over Gamma > 20]: 0.297917 over n = 4800 (16 grid points x 300 streams); SE_pooled = 0.00660, SE_crn = 0.02640; (+0.047917 above 0.25, +7.3 pooled SE, +1.8 CRN SE) (+0.052083 below 0.35, +7.9 pooled SE, +2.0 CRN SE); verdict = PASS
Aggregate gate [mean FPR_recalib over the whole grid]: 0.095500 over n = 6000 (20 grid points x 300 streams); SE_pooled = 0.00379, SE_crn = 0.01697; (+0.034500 below 0.13, +9.1 pooled SE, +2.0 CRN SE); verdict = PASS
```

Two standard errors are reported per gate. `SE_pooled` treats the streams as independent;
`SE_crn` treats the grid estimates as perfectly correlated, which they nearly are, since the
seed of protocol 1A does not depend on `Gamma` and the base innovations are shared across grid
points. The truth lies between the two; the conservative figure is `SE_crn`, and every gate
clears it by at least 1.8 standard errors.

### Non-blocking extremal criteria, with their firing probability under `H_0`

```
Extremal criterion [min FPR_raw over Gamma > 20]: observed 0.743333 at Gamma = 22.7778 against threshold 0.76; probability of firing under H_0 at the observed aggregate rate 0.807083 is 0.255 for 16 independent grid points (upper bound under CRN) -- BREACHED, non-blocking
Extremal criterion [max FPR_sqrt over Gamma > 20]: observed 0.310000 at Gamma = 75.5556 against threshold 0.35; probability of firing under H_0 at the observed aggregate rate 0.297917 is 0.301 for 16 independent grid points (upper bound under CRN) -- not breached
Extremal criterion [max FPR_recalib over the whole grid]: observed 0.110000 at Gamma = 91.1111 against threshold 0.13; probability of firing under H_0 at the observed aggregate rate 0.095500 is 0.333 for 20 independent grid points (upper bound under CRN) -- not breached
```

**The literal criterion of the original specification fires.** The minimum `FPR_raw` over
`Gamma > 20` is 0.743333 at `Gamma = 22.7778`, below the 0.76 floor, with a firing probability
of 0.255 at the observed aggregate rate. Had the certification been placed on that minimum, as
originally specified, this run would have aborted with `sys.exit(1)` while no claim of v87 was
contradicted — and the only permitted response would have been to report, never to touch the
draw. The substitution of aggregates for extrema was therefore not precautionary.

---

## 3. The i.i.d. calibration arm

```
i.i.d. calibration arm: compute_gamma_exact(0, 0) = 1.0
i.i.d. calibration at Gamma = 1: StrictCUSUM FPR = 0.020000 (6/300), Wilson 95% [0.009198, 0.042940], contains the 5% nominal level: False
i.i.d. calibration at Gamma = 1: ADWIN FPR = 0.050000 (15/300), Wilson 95% [0.030532, 0.080847], contains the 5% nominal level: True
```

**Classification: D2, not D1.** The Wilson interval of the StrictCUSUM excludes 5%, so the
descriptor "calibrated to a 5% nominal level" that v87 attaches to it is not reproduced. Had
the interval contained 5%, the deviation would have dropped to D1 as agreed; it does not.

ADWIN holds its nominal level exactly (5.0%, Wilson [3.1%, 8.1%]), so the descriptor is
accurate for the window-mean detector and inaccurate only for the CUSUM.

This is not a defect of the detector: `lambda_iid = 65` is a conservative threshold, a
legitimate design choice, and a conservative i.i.d. level makes the explosion start from a
lower base. What is inexact is calling that threshold calibrated to 5%. Registered as entry 7
of `docs/DEVIATIONS.md`; a parked candidate sits in
`docs/camera_ready_candidates/v87_cusum_nominal_level.md`.

---

## 4. Shared-realisation verdict

The exemption of the ordering checks from the multiple-testing rule rests on the three CUSUM
columns being one realisation read at three thresholds. That premise is verified at run time,
not assumed: each worker reports whether its own indicators nest.

```
Shared-realisation verdict: per-stream nesting violations, CUSUM = 0, ADWIN = 0 over 6000 and 6000 streams. Zero violations means each row's columns are one realisation read at several thresholds, so the column ordering below is a deterministic identity and not a hypothesis test.
```

Zero violations over 6000 CUSUM streams and 6000 ADWIN streams. The ordering checks are
therefore deterministic identities and remain hard gates. The monotonicity check is a genuine
hypothesis test and its bound is derived from the sampling mechanism:

```
Monotonicity check (e): 18 consecutive differences beyond Gamma = 6.0; mechanism-derived bound = -0.10997 (SE_diff = 0.03373, z_bonf = 3.261 at family-wise alpha = 0.01); most negative observed difference = +0.000000; Spearman rho = 0.9974 (p = 8.165e-21).
```

Other blocking checks:

```
Specification: n_streams = 300, stream_length = 5000, lambda_iid = 65.0, delta_P = 0.5, alpha = 0.08
Specification check (a): all five protocol constants match v87.
Deterministic reduction: ProcessPoolExecutor with max_workers = 48, executor.map in submission order, chunksize = 10. No completion-order reduction, no worker-side logging. Outputs are invariant to the worker count because every task derives its own 128-bit seed.
Cardinality check (b): both grid files carry 20 rows.
Consistency check (e): threshold ordering holds on all 20 rows of both files.
Certification check (f): the three aggregate gates hold.
```

---

## 5. Plot-removal neutrality (control g)

An instrumented copy of the delivered script, built in the scratchpad with the three uncited
plotting routines `Fig8`, `Fig9` and `Fig12` re-injected from
`Priorite_2_protocol_mission2.py`, was run against a separate output root. The repository was
not modified.

| Artefact                        | Delivered (no plot code)                                           | Instrumented (plot code re-injected)                               | Verdict   |
| ------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------ | --------- |
| `R03_fpr_cusum.csv`             | `ef599446da928495185ea61dda060efbd4da0b586e87c9ee6711c5dcc7176d0e` | `ef599446da928495185ea61dda060efbd4da0b586e87c9ee6711c5dcc7176d0e` | identical |
| `R03_fpr_adwin.csv`             | `53a049f7a5b25da379212cfe48a5c32ef286827260eaea167e4ab5171dbb42d6` | `53a049f7a5b25da379212cfe48a5c32ef286827260eaea167e4ab5171dbb42d6` | identical |
| `R03_add_vs_gamma.csv`          | `0c40f163f3a94b14a74ce863b603f14d4683ccde795f36b9a3ffe8b0bad5f2d3` | `0c40f163f3a94b14a74ce863b603f14d4683ccde795f36b9a3ffe8b0bad5f2d3` | identical |
| `R03_add_vs_width.csv`          | `6509beeaa701c4e427c78e8f545b7405abcbc53b2bb8759106f1fd1cde50f51c` | `6509beeaa701c4e427c78e8f545b7405abcbc53b2bb8759106f1fd1cde50f51c` | identical |
| `R03_sensitivity.csv`           | `b66382ce3b6b82e7474a316ad732e19c2116f0ecfe200487059469a3de4cf68e` | `b66382ce3b6b82e7474a316ad732e19c2116f0ecfe200487059469a3de4cf68e` | identical |
| `R03_iid_calibration_check.csv` | `54dabdc61097973f805e60edc0ed199f9ad7f2bdb82fa2af73087affde9bf004` | `54dabdc61097973f805e60edc0ed199f9ad7f2bdb82fa2af73087affde9bf004` | identical |

**The hidden coupling the brief anticipated exists, and it is confined to the plots.** The
`Fig9` routine of the submitted script re-read `protocol_2a_add_vs_gamma.csv` from disk to
recover its overshoot intercept `kappa` — a CSV round-trip used as a memory bridge, which the
specifications forbid. The coupling runs from one plot to another and touches no data path,
which is why the six CSV files are unaffected. Removing the plot code removes the only
consumer of that round-trip.

### Reproducibility (control h)

Four consecutive runs of `run_experiment_R03.sh` were compared. Runs 1 and 2 certify the
script as first delivered; runs 3 and 4 certify it after two comment-only edits made to clear
the narrative-language grep, and match runs 1 and 2 digest for digest, which establishes that
those edits moved no value.

```
SHA-256 R03_fpr_cusum.csv : ef599446da928495185ea61dda060efbd4da0b586e87c9ee6711c5dcc7176d0e
SHA-256 R03_fpr_adwin.csv : 53a049f7a5b25da379212cfe48a5c32ef286827260eaea167e4ab5171dbb42d6
SHA-256 R03_iid_calibration_check.csv : 54dabdc61097973f805e60edc0ed199f9ad7f2bdb82fa2af73087affde9bf004
SHA-256 R03_add_vs_gamma.csv : 0c40f163f3a94b14a74ce863b603f14d4683ccde795f36b9a3ffe8b0bad5f2d3
SHA-256 R03_add_vs_width.csv : 6509beeaa701c4e427c78e8f545b7405abcbc53b2bb8759106f1fd1cde50f51c
SHA-256 R03_sensitivity.csv : b66382ce3b6b82e7474a316ad732e19c2116f0ecfe200487059469a3de4cf68e
SHA-256 fig03_fpr_explosion.png : 6ec5f5ec7cc112455d2f2cf377065a75342966b770a01dfb5034c42af131ab6c
SHA-256 R03_claims.tex : 283b6a387f2b0514d1123ac61261f37b3e32fa5d791b6b8354866b9db0919db1
```

Environment and cost:

```
PYTHONHASHSEED correctly pinned to 42 before interpreter start.
Python: 3.12.9
  numpy: 1.26.4
  pandas: 2.3.2
  scipy: 1.16.2
  matplotlib: 3.10.6
Execution completed in 39.4s with 48 workers.
```

---

## 6. Test suite

Run after the measurements existed, never before. No assertion in `tests/test_R03_claims.py`
was written against an expected value.

```
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-9.0.3, pluggy-1.6.0 -- /home/m53/miniforge3/envs/Trading/bin/python3
cachedir: .pytest_cache
rootdir: /home/m53/The-Whitening-Advantage-Experiments
plugins: anyio-4.8.0
collecting ... collected 34 items

tests/test_R01_claims.py::test_r01_models PASSED                         [  2%]
tests/test_R01_claims.py::test_r01_trajectories PASSED                   [  5%]
tests/test_R01_claims.py::test_r01_injection_summary PASSED              [  8%]
tests/test_R01_claims.py::test_r01_placebo PASSED                        [ 11%]
tests/test_R01_claims.py::test_r01_magnitude_and_symmetry PASSED         [ 14%]
tests/test_R02_claims.py::test_stream_counts PASSED                      [ 17%]
tests/test_R02_claims.py::test_classifier_integrity PASSED               [ 20%]
tests/test_R02_claims.py::test_data_rejection_rates PASSED               [ 23%]
tests/test_R02_claims.py::test_distinct_p_concept PASSED                 [ 26%]
tests/test_R02_claims.py::test_independence_diagnostics PASSED           [ 29%]
tests/test_R02_claims.py::test_iid_arm_rejection_is_reported_not_asserted PASSED [ 32%]
tests/test_R02_claims.py::test_concept_level_covered_by_wilson PASSED    [ 35%]
tests/test_R02_claims.py::test_max_clustered_pvalue_below_manuscript_bound PASSED [ 38%]
tests/test_R02b_claims.py::test_negative_control_integrity PASSED        [ 41%]
tests/test_R02b_claims.py::test_nu_seven_is_indistinguishable_from_nominal PASSED [ 44%]
tests/test_R02b_claims.py::test_heavy_tail_arms_exclude_nominal PASSED   [ 47%]
tests/test_R02b_claims.py::test_rate_ordering_heavy_versus_light PASSED  [ 50%]
tests/test_R02b_claims.py::test_negative_control_matches_squared_at_light_tails PASSED [ 52%]
tests/test_R02c_claims.py::test_R02c_seed_uniqueness PASSED              [ 55%]
tests/test_R02c_claims.py::test_R02c_negative_control_calibration PASSED [ 58%]
tests/test_R02c_claims.py::test_R02c_eighth_moment_account_is_refuted PASSED [ 61%]
tests/test_R02c_claims.py::test_R02c_slope_test_power_is_declared PASSED [ 64%]
tests/test_R02c_claims.py::test_R02c_control_arm_integrity PASSED        [ 67%]
tests/test_R02c_claims.py::test_R02c_continuity PASSED                   [ 70%]
tests/test_R02c_claims.py::test_R02c_mechanism_slope_logic PASSED        [ 73%]
tests/test_R03_claims.py::test_R03_grid_cardinality PASSED               [ 76%]
tests/test_R03_claims.py::test_R03_grid_is_unchanged PASSED              [ 79%]
tests/test_R03_claims.py::test_R03_threshold_ordering_is_structural PASSED [ 82%]
tests/test_R03_claims.py::test_R03_monotonicity_beyond_gamma_six PASSED  [ 85%]
tests/test_R03_claims.py::test_R03_aggregate_certification_gates PASSED  [ 88%]
tests/test_R03_claims.py::test_R03_gamma_rule_holds_the_nominal_level PASSED [ 91%]
tests/test_R03_claims.py::test_R03_iid_calibration_arm_is_well_formed PASSED [ 94%]
tests/test_R03_claims.py::test_R03_deviation_classification_against_witness PASSED [ 97%]
tests/test_R03_claims.py::test_R03_macros_are_emitted PASSED             [100%]

============================== 34 passed in 0.76s ==============================
```

`grep -nE '0\.[0-9]{3,}' tests/test_R03_claims.py` returns nothing: no numeric literal in the
test file comes from a CSV. The only constants are those printed in v87. The narrative-language
grep of the preamble returns nothing on the script, the log, the test file and the Markdown
section.

---

## 7. Design decisions taken outside the plan, and open questions

### Decisions

1. **`standardised_squared_stream()` extracted inside the experiment file.** The comparability
   condition of the i.i.d. arm requires it to share the grid's construction of the monitored
   stream exactly. The helper stays inside `exp_R03_fpr_explosion.py`; no scientific primitive
   was moved into `experiments/common/`, which the preamble forbids.
2. **Per-stream nesting indicators returned by the workers.** Needed to verify rather than
   assume the shared-realisation premise, at negligible cost.
3. **Two standard errors reported per aggregate gate.** The pooled figure alone would claim
   margins of 8-9 SE; under common random numbers the honest figure is 1.8-2.1 SE. Reporting
   only the pooled one would overstate the strength of the certification.
4. **`--fast` outputs stamped `_fast`.** The flag previously overwrote the certified artefacts
   with 10-stream data under identical filenames. Certification and deviation classification
   are both withheld on that path and the withholding is logged.
5. **`--n-jobs` added**, defaulting to `os.cpu_count()`, and the worker count logged. Outputs
   do not depend on it: every task derives its own 128-bit seed and `executor.map` reduces in
   submission order.
6. **`\RThreeGammaMin` emitted with two decimals** rather than one, which rendered the grid's
   left endpoint 1.173913 as "1.2", a value the manuscript does not print.

### Open questions

1. **The camera-ready candidate's search block is reconstructed, not read.** The frozen
   `articleB_whitening_v87.tex` was not available to this run, so the LaTeX in
   `docs/camera_ready_candidates/v87_cusum_nominal_level.md` was rebuilt from the sentence as
   quoted in the R03 brief. It must be verified against the source before it is ever applied.
2. **Figure numbering not verified against the manuscript.** The output is named
   `fig03_fpr_explosion.png` on the brief's statement that this is Figure 3; the submitted
   pipeline named the two source images `Fig4` and `Fig5`. Confirm against v87.
3. **`\RThreeLowestGamma` is retained, `\RThreeGammaMin` is removed.** Two macros for the same value invite citing one for the other, and the second underpins no direct claim.
4. **A jump at the bottom of the ADWIN grid.** ADWIN measures 5.0% at `Gamma = 1` exactly and 9.3% at `Gamma = 1.174`, against 5.3% at that point in the submitted campaign. The lowest point carries `alpha = 0.08` with `beta = 0`, so it is an ARCH(1) stream and some increase is expected, but this represents a 2 SE increase, for which neither the mechanism nor the magnitude is established. This affects no certified quantity: the certification region is `Gamma > 20`.
5. **The three uncited CSV files are retained and unexamined.** `R03_add_vs_gamma.csv`,
   `R03_add_vs_width.csv` and `R03_sensitivity.csv` record the extent of the campaigns and
   support no claim. The 2C seed-key collision described in section 1 affects the last of them;
   its values are correct for the corrected seeding, but no result of the submitted campaign
   built on them has been re-verified, because none is cited.
