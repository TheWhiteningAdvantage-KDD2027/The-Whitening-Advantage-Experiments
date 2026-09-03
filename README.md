# The Whitening Advantage: Exact Calibration of Concept-Drift Detectors on Heteroscedastic Streams

This repository contains the official, strictly reproducible experimental pipeline for the KDD 2027 Research Track submission *The Whitening Advantage*.

**CRITICAL NOTICE:** Please read [`docs/DEVIATIONS.md`](docs/DEVIATIONS.md) first. It contains the consolidated register of every divergence between the submitted manuscript and this reproducible repository, classified at the manuscript's own printing precision.

## 1. Overview
This repository provides the code to independently reproduce the 21 experiment streams (R01-R18, including the variants R02b, R02c and R04b) supporting the paper's claims. The central thesis is that on a sign-prediction task, the binary error stream of a non-anticipative classifier is exactly i.i.d. Bernoulli(1/2) regardless of underlying GARCH volatility dynamics (Proposition 3.1, *Sign-Task Whitening Property*), enabling exact concept-drift detector calibration without variance estimation.

A complete mapping table linking every figure and every number of the manuscript to its generating script, its CSV and its LaTeX macro file is in [`docs/MAPPING.md`](docs/MAPPING.md), generated from the repository tree by `build_mapping.py`.

## 2. Repository Structure
* `data/`: Derived daily series (`derived_firstrate/`, `derived_crypto/`, `derived_equities/`) and read-only historical campaign witnesses (`reference/`). Raw proprietary intraday ETF data is omitted.
* `docs/`: The deviation register (`DEVIATIONS.md`), the mapping table (`MAPPING.md`), the forensic audit reports (`audits/`), the per-experiment reports (`sections/`), and the LaTeX corrections parked for the final version (`camera_ready_candidates/`).
* `experiments/`: The FAIR execution harness (`common/`) and the standalone execution scripts per stream (`R[XX]_<slug>/`).
* `logs/`: Execution logs. These carry the SHA-256 digests, the control margins and the package versions on which every reproducibility claim in this repository rests.
* `results/`: All generated artefacts (CSV data, figures, LaTeX macros).
* `tests/`: Pytest regression suites certifying the numerical integrity of each stream.

## 3. Certified Environment
The campaign is locked to the following environment to guarantee IEEE 754 float determinism.
* **Python:** 3.12.9
* **Determinism:** MKL and OpenBLAS are strictly pinned to single-threading (`OMP_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`) before NumPy imports. `PYTHONHASHSEED` is exported as `42` by each runner and verified by each script.

## 4. Reproduction Commands
```bash
# Execute the entire pipeline and the test suite
bash run_all.sh
```

To run a specific stream individually:
```bash
bash run_experiment_R01.sh
```

To execute only the test suite:
```bash
bash run_tests.sh
```

## 5. Data Availability
Experiments relying on real-world ETF data (R01, R16) consume pre-aggregated daily derived series in `data/derived_firstrate/`, giving full reproducibility without the proprietary 1-minute FirstRate data, which is not redistributable.

Every non-redistributable input has a public fetcher and a versioned derived series, so the nominal reviewer path never touches the network: R14 fetches daily Bitcoin and Ethereum into `data/derived_crypto/`, R15 fetches the 97-equity panel into `data/derived_equities/`, and R01 offers an open-source path via `--data-source yfinance`. Each of those streams separates `--stage ingest` from `--stage analyse`; `--stage analyse` is the nominal path and the one certified bit-identical across runs. No stream falls back silently to an alternative source: the source is selected by an explicit argument and stamped in the output filenames.

## 6. What This Repository Found Against Its Own Manuscript

The campaign regenerated all 21 streams under a stricter reproducibility standard than the submitted campaign used. What it found falls into three groups, and the proportions matter more than any single entry: about twenty defects in the experimental apparatus, eight formal contradictions of the manuscript, and no falsified proposition. Every one was found by the authors, and every one is documented here.

### 6.1 Formal contradictions of the submitted manuscript

Claims the regenerated pipeline does not produce. Full detail, with the source CSV cell for every value, is in [`docs/DEVIATIONS.md`](docs/DEVIATIONS.md) and in the corresponding audit under `docs/audits/`.

| Register entry | Manuscript site | What does not hold |
|---|---|---|
| `R02b-iid-arm-rejection` | L278 | The manuscript attributes the i.i.d. arm Ljung-Box over-rejection at $t_7$ to the loss of the fourth moment of $\varepsilon_t^2$. For an i.i.d. tested series the limit requires only that the tested series have a finite variance, i.e. $\mathbb{E}[\varepsilon_t^4] < \infty$, i.e. $\nu > 4$, which $t_7$ satisfies (`R02b_rejection_vs_nu.csv` :: `contains_nominal_squared`, row nu=7 = True). The moment absent at $\nu \le 8$ is $\mathbb{E}[\varepsilon_t^8]$, and that account is refuted by its own control: it is absent at $\nu=7$ too, where the rate is calibrated at every horizon to $n = 1.28\times10^5$. What is contradicted is the stated reason the $\chi^2$ approximation fails, and not the whitening property, not the exactness of the Concept threshold, and no proposition of v87. Two things are reported here rather than resolved. At the manuscript's own $t_7$ the regenerated rate is 5.8% with Wilson $[4.51, 7.43]\%$, which contains the nominal level, so the over-rejection is not corroborated at that arm; it is corroborated at $\nu=5$ (8.8%) and $\nu=6$ (7.9%), neither of which v87 runs. And the true mechanism is not identified: the boundary is located between $\nu=6$ and $\nu=7$, and locating it is not establishing it. |
| `R04-gamma-grid-defect` | Section 4 (Table 3 and family control) | The submitted campaign's Gamma grid had collapsed to a single point through a parameter-order defect. Consequently, the Recalib arm is published as running 2 to 19x behind the first-order arms (it runs 7 to 81x behind across the genuinely spanned grid), and the family-control false-alarm levels are published as flat across Gamma (they spread over 49 points for CUSUM and 24 points for ADWIN). The contradiction touches the magnitude of the Recalib penalty and the flatness of the family controls; it does not touch the Recalib blind zone, the Gaussian ceiling pi/2, the location of the efficiency crossing or the cost of the parametric route, which R04b owns, or any proposition of v87. |
| `R04b-efficiency-crossing` | L57 (abstract), L253, L372 (conclusion), L519 (Figure 4 caption) | The Eco-L1 efficiency crossing is published at one location, nu* ~ 4.9. Every regenerated estimator on the refined twelve-point grid places it higher and the inferential bracket excludes it entirely: bracket [7.0, 9.0], shape fit 8.10 [7.78, 8.37], grid bracket [7.0, 8.0] (`R04b_ratio_vs_nu.csv` :: `ratio`). The `8.52` this repository's own earlier R04 audit reported is not a competing measurement and is not counted here: it was a two-point interpolation across an unsampled interval, is carried at D2, and contradicts no printed numeral. What is contradicted is the location of the crossing, and not the whitening property, not the exactness of the Concept threshold, not the analytic crossing at 4.6788, not the absence of a second crossing above nu = 7, and no proposition of v87, whose asymptotic statement rests on the analytic root reproduced here at D0. |
| `R04b-estimation-cost` | L253 | The finite warm-up is published as costing 0.3 degrees of freedom. Three independent routes over the refined grid put it an order of magnitude higher and no interval among them reaches 0.3: 3.62 [3.31, 3.92] by the shape fit, 3.22 [2.52, 3.82] model-free, and the outer bound [2.0, 5.0]. They are three D3 rows of one audit and one contradiction, not three. What is contradicted is the cost of the parametric route, and not the whitening property, not the exactness of the Concept threshold, and no proposition. |
| `R07-bias-bound-not-a-bound` | L308 | L308 states that the classical small-sample AR bias `E[phi_hat] - phi approx -2.5 phi/n` stays under 2.9 x 10^-3 across the full 7 x 4 grid. It does not: the largest absolute bias over the 28 diagnostic cells is 3.1268677 x 10^-3 at phi = 0.15 and n_ols = 125, 1.44 standard errors past the printed bound and at the corner the printed formula itself designates (`R07_estmean_diagnostics.csv` :: `bias_phi_hat`). The falsification is confined to the numeral and to the words "stays under": it does not touch the ordering of the channels, Figure 7 panel A or panel B, neither of which plots the bias, the OLS-versus-ORACLE false-alarm comparison, or the lattice law. |
| `R08-delivered-level-above-nominal` | L241 and its footnote | The text selects "the nearest attainable level at or below nominal" and its own footnote makes the implemented test the weak comparison operator, whose level at the selected threshold is above nominal, while the level reported is the strict one. The null law itself remains exact and free of nuisance parameters; what is contradicted is the selection rule and the level reported, not the exactness result. |
| `R16-dating-misdescription` | L329 | The census is described as a multi-scale Pagan-Sossounov bull/bear dating of the four streams. Strict Pagan-Sossounov yields 48 phases, not 66: the canonical census reaches 66 by substituting Lunde-Timmermann for SPY alone when `check_sanity` fails. The falsification touches the dating description only; it does not affect the 80% headline, which is computed from the canonical census that does reach 66 phases and 53 out of budget at gamma=20. |
| `R17-eco-l1-arm-identity` | L341 and Table 1 at tex line 117 | A false-alarm figure is attributed to the arm Table 1 defines as the level residual, while the cell that produced it monitors the squared standardized residual, the arm the source script itself names differently. The false-alarm numerals only; the persistence median is arm-agnostic because the fit is shared. |

### 6.2 Printed numerals that move

Every stream was redrawn under 128-bit entropy keys, so Monte-Carlo values move. Each is classified D0 to D3 at the manuscript's own printing precision, with its source CSV cell, in [`docs/DEVIATIONS.md`](docs/DEVIATIONS.md). No qualitative claim of the paper is falsified by any of them.

### 6.3 A limitation we report against ourselves, contradicting nothing

**R18 — Power of the Ljung-Box test.** The Ljung-Box non-rejections reported in the manuscript are exact and the reported rates are correct. What R18 establishes is the strength of the evidence they carry: at the operating point behind those tests, the largest autocorrelation measured on the streams themselves is a small fraction of the amplitude the test detects with 80% power, where the instrument's power equals its own size. The non-rejections therefore exclude autocorrelation above that amplitude and exclude nothing below it. The theoretical result remains the guarantee of the whitening property. We report this because a reader is entitled to know what a non-rejection is worth, not because anything printed is wrong.

---
## EXPERIMENT REPORTS

# R01 — Real World Backtest

R01 instantiates the whitening advantage framework on FirstRate intraday ETF data (SPY, PFF, VNQ, BWX) spanning 2000-01-04 to 2025-07-07. It establishes three results: (1) GARCH(1,1) QMLE calibration of conditional heteroscedasticity bounds under the exact gamma formula of [Berkowitz and O'Brien, 2002]; (2) CUSUM detection of variance regime shifts during COVID-19 (2020) via strict monitors; and (3) semi-real injection experiments with Δ ∈ {0.0, 0.5, 1.0, 1.5}σ_unc across 36 monthly onsets per ETF in 2021-2023. It certifies Figure 2, and the numbered claims carried in `results/R01_real_world_backtest/tables/R01_claims.tex`. The Data pipeline monitors raw squared returns normalized by empirical moments; the Concept pipeline whitens the sign stream via probability normalization.

Reproduction: `bash run_experiment_R01.sh`

## Expected artefacts

### Artefacts that certify a published value
- `results/R01_real_world_backtest/data/R01_garch_models.csv`
- `results/R01_real_world_backtest/data/R01_covid_trajectories.csv`
- `results/R01_real_world_backtest/data/R01_covid_alarms.csv`
- `results/R01_real_world_backtest/data/R01_symmetry_2020.csv`
- `results/R01_real_world_backtest/data/R01_injection_summary.csv`
- `results/R01_real_world_backtest/data/R01_magnitude_sweep.csv`
- `results/R01_real_world_backtest/figures/fig02_spy_in_the_wild.png`
- `results/R01_real_world_backtest/tables/R01_claims.tex`

### Artefacts that certify a control and certify no published value
- `results/R01_real_world_backtest/data/R01_placebo_control.csv`

## Measured execution cost

NOT RECOVERABLE FROM THE LOG.
# R02 — Ljung-Box Whiteness on Multi-ETF GARCH Streams

R02 establishes the whitening advantage by verifying that binary classification errors from a sign-prediction task on GARCH(1,1) streams form a serially uncorrelated sequence under H0, while squared innovations exhibit detectable autocorrelation due to volatility clustering. The experiment certifies Figure 1 (R02 : Fig1 - Ljung-Box Multi-ETF, log line 9) and the associated claims in the manuscript through empirical Ljung-Box Q-tests.

Reproduction command: `bash run_experiment_R02.sh`

## Expected artefacts

### Artefacts that certify a published value
- `results/R02_whitening_ljungbox/data/R02_ljungbox_360streams.csv` — 360 stream results (log line 12) with p_data and p_concept values
- `results/R02_whitening_ljungbox/data/R02_independence_diagnostics.csv` — cross-stream independence tests
- `results/R02_whitening_ljungbox/figures/fig01_ljungbox_whiteness.png` — Figure 1 from the manuscript
- `results/R02_whitening_ljungbox/tables/R02_claims.tex` — LaTeX macros for published metrics

### Artefacts that certify a control and certify no published value
None recorded.

## Measured execution cost

NOT RECOVERABLE FROM THE LOG.
# R02b — IID ARM Mechanism Resolution

R02b performs a dedicated i.i.d. mechanism test for the Ljung-Box whiteness validation, extending the manuscript's single t_7 point to a full degrees-of-freedom grid. It varies Student's t degrees of freedom nu across {5, 6, 7, 8.5, 12, 30} to locate the transition where the chi-square approximation on squared innovations fails or holds. For Student's t innovations, the theoretical finite fourth-moment boundary is nu > 4; the experiment empirically identifies where the nominal 5% level is excluded. It certifies Figure A01 (i.i.d. over-rejection vs nu) and the i.i.d. arm mechanism discussion at line 278 of the manuscript.

Reproduction command: `bash run_experiment_R02b.sh`

### Expected artefacts

**Artifacts that certify published values:**
- `results/R02b_iid_arm_resolution/data/R02b_rejection_vs_nu.csv` — rejection rates and Wilson 95% CIs per nu (certifies Figure A01 and the transition point)
- `results/R02b_iid_arm_resolution/tables/R02b_claims.tex` — LaTeX macros for all published quantities
- `results/R02b_iid_arm_resolution/figures/figA01_iid_overrejection_vs_nu.png` — the figure itself

**Artifacts that certify controls and certify no published value:**
- `results/R02b_iid_arm_resolution/data/R02b_streams.csv` — per-stream p-values for both raw and squared innovations (6000 rows), used for negative control validation

Measured execution cost: NOT RECOVERABLE FROM THE LOG.

## Known deviations from the submitted manuscript

D2-1: The manuscript reports a single i.i.d. arm over-rejection rate of 9.2% at line 278 without specifying nu. The compliant pipeline extends this to a grid and finds nu-dependent rates: 8.8% at nu=5, 7.9% at nu=6, 5.8% at nu=7. The qualitative over-rejection mechanism for heavy tails (nu ≤ 6) is preserved.

D2-2: The manuscript implication that the nominal 5% level is excluded at nu=7 is not reproduced; the compliant pipeline excludes the nominal only up to nu=6, with nu=7 containing the level. The transition point between nu=6 and nu=7 is however corroborated.
# R02c — Horizon Sweep and Eighth-Moment Account Falsification

R02c conducts a horizon-scaling analysis of Ljung-Box test over-rejection rates across stream lengths 2000, 8000, 32000, and 128000 for Student t innovations with nu = 5, 6, 7. The experiment establishes that the eighth-moment explanation (E[eps^8] = infinity for nu <= 8) does not survive its own witness: nu=7 (where E[eps^8] is also infinite) remains calibrated at the nominal 5% level, while nu=5 and nu=6 exhibit significant over-rejection. This falsifies the hypothesis that infinite eighth moment universally causes chi-square approximation failure in Ljung-Box tests on squared inputs. It certifies Figure A02 (figA02_overrejection_vs_horizon.png) and the LaTeX macros in R02c_claims.tex.

Reproduction command: `bash run_experiment_R02c.sh`

### Expected artefacts

Artefacts that certify a published value:
- results/R02c_horizon_sweep/figures/figA02_overrejection_vs_horizon.png
- results/R02c_horizon_sweep/tables/R02c_claims.tex

Artefacts that certify a control and certify no published value:
- results/R02c_horizon_sweep/data/R02c_streams.csv
- results/R02c_horizon_sweep/data/R02c_rejection_vs_horizon.csv

Measured execution cost: Completed execution in 3.0 minutes (log line 16).
# R03 — False Positive Rate Explosion Without Recalibration

Quantifies the cost of ignoring the heteroscedastic penalty Γ inflicted on drift detectors calibrated under i.i.d. assumptions when deployed on stationary GARCH(1,1) streams under H₀. The experiment corroborates the detector-specific remedies: for StrictCUSUM the threshold must be multiplied by Γ (Siegmund limit), and for ADWIN by √Γ. It demonstrates FPR explosion without recalibration, validates the Γ-corrected thresholds, and shows the residual plateau behaviour.

Certifies Figure 3 and the claims published as LaTeX macros in R03_claims.tex: FPR_raw, FPR_sqrt, FPR_gamma, FPR_recalib rates across the Γ grid, and i.i.d. calibration arm rates with Wilson intervals.

## Execution

```bash
bash run_experiment_R03.sh
```

## Expected artefacts

### Artefacts that certify published values
- `results/R03_fpr_explosion/data/R03_fpr_cusum.csv` — StrictCUSUM false alarm rates (FPR_raw, FPR_sqrt, FPR_gamma) at 20 Γ grid points
- `results/R03_fpr_explosion/data/R03_fpr_adwin.csv` — ADWIN false alarm rates (FPR_raw, FPR_recalib) at 20 Γ grid points
- `results/R03_fpr_explosion/data/R03_iid_calibration_check.csv` — i.i.d. calibration arm (Gamma = 1) rates with Wilson intervals for StrictCUSUM and ADWIN
- `results/R03_fpr_explosion/data/R03_add_vs_gamma.csv` — detection delay against Γ (Protocol 2A)
- `results/R03_fpr_explosion/data/R03_add_vs_width.csv` — detection delay against drift width (Protocol 2B)
- `results/R03_fpr_explosion/data/R03_sensitivity.csv` — speedup sensitivity (Protocol 2C)
- `results/R03_fpr_explosion/figures/fig03_fpr_explosion.png` — Figure 3
- `results/R03_fpr_explosion/tables/R03_claims.tex` — 26 LaTeX macros defining stream parameters, FPR metrics, and Wilson intervals

### Artefacts that certify controls and certify no published value
- `results/R03_fpr_explosion/data/R03_fpr_cusum_fast.csv` — degraded path (10 streams, certification gates disabled)
- `results/R03_fpr_explosion/data/R03_fpr_adwin_fast.csv` — degraded path (10 streams, certification gates disabled)
- `results/R03_fpr_explosion/data/R03_iid_calibration_check_fast.csv` — degraded path (10 streams, certification gates disabled)
- `results/R03_fpr_explosion/data/R03_add_vs_gamma_fast.csv` — degraded path (10 streams, certification gates disabled)
- `results/R03_fpr_explosion/data/R03_add_vs_width_fast.csv` — degraded path (10 streams, certification gates disabled)
- `results/R03_fpr_explosion/data/R03_sensitivity_fast.csv` — degraded path (10 streams, certification gates disabled)
- `results/R03_fpr_explosion/figures/fig03_fpr_explosion_fast.png` — degraded path (10 streams, certification gates disabled)
- `results/R03_fpr_explosion/tables/R03_claims_fast.tex` — degraded path (10 streams, certification gates disabled)

## Measured execution cost

Execution completed in 38.6s with 48 workers (output of: bash run_experiment_R03.sh, line 69).

## Known deviations from the submitted manuscript

All 11 deviations are classified as D2 (numerical shifts at printed precision). The manuscript values and regenerated values differ numerically; the cause is not identified in the log. No qualitative claim is falsified: the core scientific findings — FPR explosion to near-80% at high Γ, the effectiveness of the Γ correction in holding the nominal 5% level, and the √Γ residual plateau near 30% — all hold in the compliant pipeline.
# R04 — Iso-FPR Race and Relative Efficiency

R04 races four monitoring pipelines (Recalib, Eco-L1, Oracle-Eco, Concept) against one another under a location drift model with GARCH(1,1) conditional heteroscedasticity. All arms are calibrated by bisection to the same 5% false-alarm rate. The experiment establishes Figure 4 and Table 3, validating that Recalib (a second-order sensor) is structurally slow against location drift while first-order monitors detect efficiently. The Pitman efficiency of the sign test governs the delay ratio between Concept and Eco-L1.

Reproduction command: `bash run_experiment_R04.sh`

## Expected artefacts

### Artefacts that certify a published value
- `results/R04_isofpr_race/data/R04_isofpr_race.csv` — Table 3 ADD values
- `results/R04_isofpr_race/data/R04_relative_efficiency.csv` — efficiency ratios and nu* crossing points
- `results/R04_isofpr_race/data/R04_isofpr_calibration.csv` — lambda_star thresholds
- `results/R04_isofpr_race/figures/fig04_isofpr_race.png` — Figure 4
- `results/R04_isofpr_race/tables/tab03_isofpr_race.tex` — Table 3 LaTeX
- `results/R04_isofpr_race/tables/R04_claims.tex` — LaTeX macros for published values

### Artefacts that certify a control and certify no published value
- `results/R04_isofpr_race/data/R04_cusum_vs_adwin.csv` — family control FPR comparison
- `results/R04_isofpr_race/data/R04_bernoulli_constant.csv` — M0 universality control

## Measured execution cost

Execution completed in 227.0s with 48 workers (log line 166). v87 reports about 25 min for this race on 24 cores; the ratio is 6.6x.

## Known deviations from the submitted manuscript

**RFourRecalibSlowdownRange (D3):** Recalib slowdown range is 7-81x instead of 2-19x. The Gamma grid collapse correction reveals that the squared sensor is materially slower across the genuinely spanned grid than was measured at the single collapsed point.

**RFourNuStarMeasured (D3):** Eco-L1 efficiency ratio crosses unity at nu* = 8.52 instead of 4.9. The crossing moves outside the published value due to the genuinely spanned Gamma grid.

**RFourEstimationCostDof (D3):** The estimation cost is 4.05 dof instead of 0.3. The difference between Eco-L1 nu* (8.52) and Oracle nu* (4.47) reveals the true estimation error under the corrected grid.

**RFourFamilyCusumFpr, RFourFamilyAdwinFpr (D3):** Family control levels are not flat across Gamma. CUSUM FPR mean = 36.1% (spread 0.4905) and ADWIN FPR mean = 10.7% (spread 0.2390) over the Gamma grid, rather than approximately 5% and flat.

**RFourNuStarOracle (D2):** Oracle arm crosses unity at nu* = 4.47 instead of 4.6. The regenerated value is bracketed by [4.0, 4.5] and remains compatible at the bracket level.

**RFourParametricGainAtCOne (D2):** Parametric gain at c=1 is 1.38x instead of 1.66x. The ratio of Eco-L1 ADD to Oracle-Eco ADD at Gamma=11.58, c=1.0 shifts while the qualitative ordering (Eco-L1 slower than Oracle) is preserved.

**RFourConceptLambdaMin, RFourConceptLambdaMax (D2):** Concept threshold band is [10.5, 10.7] instead of [10.6, 10.7]. The measured range [10.499, 10.743] spans 2.0 bisection lattice steps; homogeneity chi-square p = 0.2601 supports the proposition.

**RFourConstantThresholdFpr, RFourBernoulliFpr (D2):** Constant-threshold Concept FPR is 7.7% (garch) and 7.9% (bernoulli_iid) instead of 5%. Wilson 95% CIs: [0.0701, 0.0849] and [0.0720, 0.0870] respectively.
# R04b — Nu Grid Refinement and Efficiency Crossing Point Resolution

R04b resolves the efficiency crossing point that R04 bracketed but could not pinpoint. It re-measures three arms (Eco-L1, Oracle-Eco, Concept) at Gamma = 11.58, c = 0.5, with 2000 null streams of length 5000 and 500-step warm-up, on a refined twelve-point nu grid {4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 15.0, 20.0, 30.0} spanning the (7, 30) void where the delay ratio ADD_Concept / ADD_Eco-L1 crosses unity. The stream certifies Appendix Figure A3 (figA03_nu_star_refinement.png) and the crossing estimators: grid bracket (model-free, resolution-limited), inferential bracket (model-free with 95% confidence), shape fit with stream-level bootstrap (2000 replicates), and analytic root of 1/(4 f_z(0)^2).

Reproduction command: `bash run_experiment_R04b.sh`

### Expected artefacts

**Artefacts that certify published values:**
- `results/R04b_nu_refinement/data/R04b_ratio_vs_nu.csv` — delay ratios and crossing estimator inputs
- `results/R04b_nu_refinement/tables/R04b_claims.tex` — 55 LaTeX macros for Figure A3 and all crossing claims
- `results/R04b_nu_refinement/figures/figA03_nu_star_refinement.png` — Appendix Figure A3

**Artefacts that certify controls and certify no published value:**
- `results/R04b_nu_refinement/data/R04b_continuity_with_R04.csv` — continuity check with R04 at common points (4.0, 4.5, 5.0, 7.0, 30.0)

Measured execution cost: 29.4s with 48 workers (1440 monitored streams over three passes), plus 2000 bootstrap replicates (log line 114).

### Known deviations from the submitted manuscript

**R04b_D3_EcoL1_crossing:** The manuscript states the Eco-L1 efficiency ratio crosses unity at nu* ~ 4.9. R04b demonstrates this value is falsified: the inferential bracket is [7.0, 9.0], the shape fit is 8.10 [7.78, 8.37], and the grid bracket is [7.0, 8.0]. The published value lies outside the entire measured interval. The root cause is that R04's six-point grid sampled no point inside (7, 30), leaving the crossing location unresolved.

**R04b_D3_estimation_cost:** The manuscript states the finite warm-up costs 0.3 degrees of freedom. R04b measures this cost as 3.62 [3.31, 3.92] by the shape-fit route, 3.22 [2.52, 3.82] by the model-free interpolation route, and [2.0, 5.0] by the model-free bracket. All intervals exclude 0.3 by a wide margin, an order of magnitude larger.

**R04b_D3_R04_interpolation:** The manuscript cites AUDIT_R04's two-point interpolation of 8.52 across the unsampled (7, 30) interval. R04b's refined-grid interpolation is 7.75 [7.03, 8.32], demonstrating the interpolation was across an unsampled interval on a non-linear curve.

**R04b_D2_Oracle_crossing:** The manuscript states the Oracle arm crosses at 4.6. R04b's shape fit places it at 4.47 [4.31, 4.57], a D2 shift, but the published value is held within the inferential bracket [4.0, 5.0].

**R04b_D2_Gaussian_ceiling_Oracle:** The manuscript states the ratio never exceeds the Gaussian ceiling pi/2 = 1.5708. R04b confirms this for Eco-L1 (max ratio 1.255 < 1.5708) but the Concept/Oracle-Eco ratio reaches 1.6593 at nu = 20.0, exceeding the ceiling.
# R05 — Scale Law and Location/Scale Orthogonality

R05 validates the GARCH penalty scaling law (Proposition prop:add_garch) and location/scale orthogonality (Proposition prop:orthogonality) across three campaigns. The abrupt shift campaign (Figure 5A) sweeps 13 Gamma values from 1 to 30 on a 5000-step horizon with 400 seeds per configuration. The ramp campaigns at H = 200000 and H = 3000000 (Figure 5B) verify Theorem thm:scaling with gradual scale pathologies. The ladder campaign (Appendix B) computes lambda_iid at three horizons for cross-validation.

Reproduction command: `bash run_experiment_R05.sh`.

## Expected artefacts

**Artefacts that certify published values:**
- `results/R05_scale_law/data/R05_abrupt_add_vs_gamma.csv` — ADD slope 26.0016, intercept 32.1980, R^2 = 0.991299 (Figure 5A)
- `results/R05_scale_law/data/R05_ramp_multigamma_2e5.csv` — scaling law verification at H = 200000, lambda_iid_H = 128.6319 (Figure 5B, left)
- `results/R05_scale_law/data/R05_ramp_multigamma_3e6.csv` — scaling law verification at H = 3000000, lambda_iid_H = 282.5363 (Figure 5B, right)
- `results/R05_scale_law/data/R05_lambda_iid_horizon.csv` — lambda_iid at H = 77000, 200000, 3000000 (Appendix B, Table)
- `results/R05_scale_law/tables/R05_claims.tex` — LaTeX macros for all R05 claims
- `results/R05_scale_law/figures/fig05_scale_law_orthogonality.png` — Figure 5 (panels A and B)

**Artefacts that certify controls and no published value:**
- `results/R05_scale_law/data/R05_concept_positive_control.csv` — positive control showing Concept monitor responsiveness to location shift
- `results/R05_scale_law/data/R05_deviation_classification.csv` — D0-D3 classification table

## Measured execution cost

Total wall-clock time: 7054.7 s (3.9 s for step a, 173.0 s for step b 2e5, 3350.0 s for step b 3e6, 3527.8 s for step c).
Worker configuration: ProcessPoolExecutor with max_workers = 48, executor.map in submission order.

## Known deviations from the submitted manuscript

All numerical values shift at printed precision due to 128-bit entropy seeding replacing 32-bit truncation in the submitted campaign. No qualitative claims are falsified. 20 D2 deviations and 7 D1 deviations are recorded in the audit.

The abrupt ADD slope shifts from 23.70 to 26.0016 (D2), and the intercept from 38.00 to 32.1980 (D2). The delay still grows linearly in Gamma, preserving the qualitative claim of Proposition prop:add_garch.

The recalibration margin widens from [-1.42%, +39.29%] at H = 200000 to [+15.56%, +96.44%] at H = 3000000, corroborating the manuscript assertion that the recalibration rule degrades with monitoring horizon.

The sixth-moment boundary is reproduced at 7.0793 (D1 against manuscript 7.1). The fourth-moment boundary is 41.5843, far outside the Gamma grid, so the v87 description of E[eps^6] as "the second moment of eps^2" is corrected: E[eps^6] is the third moment of eps^2.

The v87 numeral lambda_C = 10 matches none of the three calibrated Concept thresholds (11.40 for abrupt, 16.00 for ramp 2e5, 18.80 for ramp 3e6).

# R06 — Empirical Validity Map of the Whitening Property

R06 maps the empirical boundaries of Proposition prop:whitening: the binary error stream of a non-anticipative classifier predicting the SIGN of a return is exactly i.i.d. Bernoulli(1/2) whatever the GARCH dynamics. It certifies Figure 6 and its caption, and the statements in Remark rem:scope on sharp task boundaries. The experiment establishes that the binary error stream remains white across a 13-point Gamma grid from 1 to 200 despite the t7 innovation grid violating E[eps_t^4] < ∞ beyond Gamma ≈ 41.6. Panel (B) demonstrates that non-median thresholds or continuous MSE loss re-inherit autocorrelation, with 100% rejection for c ≥ 0.5 and for MSE.

Reproduction command: `bash run_experiment_R06.sh`.

## Expected artefacts

### Artefacts that certify a published value
- `results/R06_validity_map/figures/fig06_validity_map.png` — Figure 6
- `results/R06_validity_map/tables/R06_claims.tex` — LaTeX macros for the manuscript
- `results/R06_validity_map/data/R06_gamma_grid.csv` — Gamma grid results certifying pooled binary rejection rate and squared-stream rejection
- `results/R06_validity_map/data/R06_task_boundary.csv` — Task boundary results certifying rejection rates for binary and continuous tasks

### Artefacts that certify a control and certify no published value
- `results/R06_validity_map/data/R06_gamma_grid_independent_seeds.csv` — Counterfactual arm with independent per-cell seeds to verify design effects

Measured execution cost: Execution completed in 33.5s over 3100 monitored streams, of which 1300 are the counterfactual arm (log line 60).
# R07 — Whitening Under an Estimated Conditional Mean

R07 asks what survives of the whitening property when the conditional mean is estimated instead of
known. On an AR(1)-GARCH(1,1) DGP with standardized Student-t7 innovations it runs six arms over a
7 x 4 grid — NAIVE (no centring), ORACLE (the true conditional mean) and rolling OLS at window
lengths n in {125, 250, 500, 1000}, at phi in {0, 0.02, 0.05, 0.075, 0.1, 0.125, 0.15} — with 10000
trajectories per cell. It certifies Figure 7 (`fig:estmean`, both panels, caption at L543), the
numerals of **L308** — Ljung-Box rejection at phi = 0 and phi = 0.15, the Concept FPR at phi = 0.15,
the two OLS envelopes, the eta RMSE at n = 125, the fourth-moment product, the bias bound and the
dispersion cost — and, for **L241**, only lambda* = 11.4: the two bracketing levels L241 prints come
from a 2 x 10^5-stream campaign that belongs to R08, which R07 does not re-run.

Two results are R07's own rather than v87's. The exact absorbing-chain law of the 2delta = 0.2
lattice at H = 5000 replaces a Monte-Carlo estimate of the same quantity and fixes lambda* by L241's
own stated rule; it is handed to R08 in
`docs/camera_ready_candidates/R07_v87_lattice_handoff_to_R08.md`, and `docs/audits/AUDIT_R08.md`
control C2a reproduces all 16 of its scanned lattice points bit for bit. And the largest estimator
bias over the 28 diagnostic cells exceeds the bound L308 prints — see the deviations below.

Reproduction command: `bash run_experiment_R07.sh`

## Expected artefacts

### Artefacts that certify a published value
- `results/R07_estimated_mean/data/R07_estmean_lb_fpr.csv` — Ljung-Box rejection rate and Concept
  false-positive rate with their Wilson score intervals and binomial p-values, 42 cells, certifying
  Figure 7 panels A and B and the L308 rate numerals
- `results/R07_estimated_mean/data/R07_estmean_diagnostics.csv` — eta = RMSE(mu_hat - mu_oracle) over
  sigma_unc, mean and dispersion of phi_hat and its bias with standard error, 28 cells, certifying
  the dispersion and bias clauses of L308
- `results/R07_estimated_mean/data/R07_lattice_exact_law.csv` — the exact survival law of the lattice
  at H = 5000 and its validation against exhaustive enumeration, certifying lambda* = 11.4 at L241
  and the threshold named in the Figure 7 caption
- `results/R07_estimated_mean/figures/fig07_estimated_mean.png` — rendered Figure 7, both panels
- `results/R07_estimated_mean/tables/R07_claims.tex` — 13 LaTeX macros (prefix `\RSeven`)

### Artefacts that certify a control and certify no published value
- `results/R07_estimated_mean/data/R07_design_effect.csv` — Kish design effect, effective sample size
  and standard-error inflation for the four pooled blocks of both statistics (control C4)
- `results/R07_estimated_mean/data/R07_eta_scaling.csv` — per-phi and pooled log-log decay exponents
  of eta and of the phi_hat dispersion, with their intervals (control C8); v87 prints no exponent
- `results/R07_estimated_mean/data/R07_eta_scaling_counterfactual.csv` — the three counterfactual DGP
  arms (t7_garch, gauss_garch, gauss_iid) that attempt to isolate the mechanism behind that exponent
  (control C8 ladder)
- the `float_drift` records inside `R07_lattice_exact_law.csv` — the realised level of each
  comparison operator on the oracle, calibration and validation stream sets (control C1 (iv))

## Measured execution cost

154 seconds wall-clock, from 2026-08-22 04:40:08 to 04:42:42
(`logs/R07_estimated_mean/exp_R07_estimated_mean.log` L1 and L367). The source and operator controls
and the exact lattice law complete in the first 2 seconds; the 420000-stream trajectory campaign and
the C7 guards take the next 141; the design effect, the counterfactual ladder, the figure and the
artefacts take the remaining 11. The number of workers is not recorded in the log: the script takes
`--n-jobs` and defaults it to `os.cpu_count()` without writing the resolved value.

## Known deviations from the submitted manuscript

- **R07-bias-bound-not-a-bound** (D3). L308 states that the systematic AR bias "stays under
  2.9 x 10^-3" across the full 7 x 4 grid. The largest absolute bias over the 28 diagnostic cells is
  3.1268677 x 10^-3 with a standard error of 0.15754883 x 10^-3, at phi = 0.15 and n_ols = 125:
  1.44 standard errors past the printed bound, and 0.81 past the 3.0 x 10^-3 that L308's own
  -2.5 phi/n approximation predicts at that same corner. The maximising cell is the grid corner the
  printed formula designates, so the extremum is structurally located rather than drawn. The bound
  as printed does not hold. What the finding does not touch is set out under **Scope** in
  `docs/audits/AUDIT_R07.md`; the parked correction is
  `docs/camera_ready_candidates/R07_v87_bias_bound.md`.
- **R07-campaign-redraw** (D2). The re-keyed campaign moves the L308 rate numerals at printed
  precision: Ljung-Box rejection at phi = 0 from 5.1% to 4.92%, the Concept FPR at phi = 0.15 from
  20.8% to 21.0%, the OLS Ljung-Box envelope from 4.6%-5.6% to 4.70%-5.63%, the OLS Concept FPR
  envelope from 4.3%-5.9% to 4.84%-5.61%, and the eta RMSE at n = 125 from 11.4% to 11.48%. Each
  moves within its own sampling error — the three numerals the test suite scores sit at -0.82, +0.49
  and +2.24 standard errors — and both OLS envelopes remain inside the bands L308 prints. Ljung-Box
  rejection at phi = 0.15 rounds to the printed 99.8% (D1).
- **R07-dispersion-cost-numeral** (D2). L308 says the dispersion channel "costs at most 0.4 points
  of rejection" without naming the quantity measured. Six readings were enumerated before the run
  and each is reported: 0.71, 0.71, 0.71, 0.89, 0.63 and 0.93 points. None rounds to 0.4, in this
  campaign or in the submitted witness, so the register entry is opened against the manuscript
  rather than against the redraw. Parked correction:
  `docs/camera_ready_candidates/R07_v87_dispersion_cost.md`.
- **R07-lambda-star-estimator** (D0 on the value). lambda* is selected by applying L241's own rule —
  the nearest attainable level at or below nominal — to the exact lattice law rather than to a
  delivered sample quantile, which sits astride the lattice boundary. The threshold does not move:
  11.4, bit-identical in float64 to the literal v87 prints.
- **R07-panelB-operating-level** (no severity; no numeral is wrong). Control C1 (iv) measures, on
  35000 fair-coin streams, that the implemented float test `M > lambda*` coincides with the
  mathematical `M >= lambda*` on every one of them and differs from `M > lambda*` on 267. The level
  the panel therefore operates at is the upper attainable one, 5.10% exact, not the 4.29% the
  caption names beside lambda*. The delivered level on the 25000 independent calibration and
  validation streams is 5.064%, and the ORACLE arm sits at 5.16%. `docs/audits/AUDIT_R08.md` carries
  the falsification this implies for L241's selection rule, which is R08's to register. Parked
  correction: `docs/camera_ready_candidates/R07_v87_panelB_operating_level.md`.
- **R07-oracle-band-precision** (no severity). Under the mandated common-random-number plan the
  seven ORACLE cells are bit-identical — the DGP never references phi when it draws the innovations
  — so the reference band against which the rolling-OLS arms are compared is carried by 10000
  effective trajectories, not 70000. The design effect is 7.0000 exactly on both statistics
  (`R07_design_effect.csv`). The comparison itself is unaffected: the widest OLS-versus-ORACLE gap
  over the 28 cells is 1.41 paired standard errors against a band of 4.0.
- **Lattice levels at L241, no register entry in R07.** The exact law returns 4.3428% at
  lambda = 11.4 and 5.1021% at lambda = 11.2, against the 4.29% and 5.03% L241 prints from a
  2 x 10^5-stream Monte-Carlo — 1.16 and 1.46 Monte-Carlo standard errors of that stated basis. R07
  opens no register entry on those two numerals and consumes no search string at L241, because the
  campaign behind them belongs to R08. The word "exact" in the Figure 7 caption, which R07 does own,
  is the separate parked candidate `docs/camera_ready_candidates/R07_v87_figure7_exactness.md`.
# R08 — The Adverse Direction and the Discrete Null Law

R08 establishes the two qualifications of the manuscript's claim that the Concept threshold is exact. First, injected centring bias moves the false-alarm rate in both directions according to its sign at identical whiteness loss (L311, Figure 8 Panels A–B). Second, the attainable levels under the CUSUM dead band are discrete: with delta = 0.1, the two-sided increments move by +2delta and -3delta, placing M_H on a 2delta = 0.2 lattice (L241, Figure 8 Panel C). The experiment certifies Figure 8 (all three panels), L241 (lambda* = 11.4, bracketing levels at lambda = 11.2 and 11.4), and L311 (whiteness gap bound of 3 points, penalty at residual momentum 0.02).

Reproduction command: `bash run_experiment_R08.sh`

## Expected artefacts

### Artefacts that certify a published value
- `results/R08_adverse_lattice/data/R08_adverse_bias.csv` — Ljung-Box rejection and false positive rates for both arms across the bias grid, certifying Figure 8 panels A–B and L311
- `results/R08_adverse_lattice/data/R08_null_law_lattice.csv` — survival probabilities over 16 lattice points, certifying Figure 8 panel C and L241
- `results/R08_adverse_lattice/figures/fig08_adverse_lattice.png` — rendered Figure 8 with all three panels
- `results/R08_adverse_lattice/tables/R08_claims.tex` — 13 LaTeX macros (prefix \REight) for L241 and L311 claims

### Artefacts that certify a control and certify no published value
- `results/R08_adverse_lattice/data/R08_pairing_diagnostic.csv` — pairing diagnostic for controls C4, C5, C6 (whiteness bound, sign asymmetry, cross-stream identity)
- `results/R08_adverse_lattice/data/R08_operator_levels.csv` — comparison operator levels for control C1 (operator identity)
- `results/R08_adverse_lattice/data/R08_lattice_exact_law.csv` — exact lattice survival for control C2 (lattice enumeration concordance)

## Measured execution cost

77.3s with 48 workers (module A 61.3s, module B 8.9s) on first run; 78.4s on second run. Worker count is fixed by keyed entropy on role and index alone, so this value cannot move a number.

## Known deviations from the submitted manuscript

The D0-D3 table carries D2 deviations only. No D3 rows exist, so no qualitative claim is falsified.

- **R08-lattice-levels**: L241 level above nominal (lambda=11.2): v87 prints 0.0503, regenerated 0.050815 (rounds to 0.0508). L241 level below nominal (lambda=11.4): v87 prints 0.0429, regenerated 0.04323 (rounds to 0.0432). Both retain the bracketing of 0.05.
- **R08-fpr-collapse**: Fig. 8 (B) FPR collapses to: v87 prints 0.0086, regenerated 0.0095 (rounds to 0.0095). The qualitative claim of collapse to near-zero is preserved.
- **R08-fpr-inflation**: Fig. 8 (B) / L311 FPR inflates to: v87 prints 0.208, regenerated 0.21 (rounds to 0.21). The qualitative claim of inflation is preserved.
- **R08-whiteness-gap-bound**: L311 whiteness gap bound (points): v87 prints 3.0, regenerated 2.21 (rounds to 2.2). The bound is still within the manuscript's "three points" bound, and the 95% bootstrap envelope [1.5600, 3.6100] points does not exclude 3.
- **R08-whiteness-range**: L311 whiteness range, low end: v87 prints 0.05, regenerated 0.0478 (rounds to 0.05, D1). High end: v87 prints 1.0, regenerated 0.9984 (rounds to 1.0, D1). Both ends round to the printed values.
- **R08-penalty-at-momentum**: L311 penalty at residual momentum 0.02 (points): v87 prints 1.1, regenerated 1.2799999999999998 (rounds to 1.3, D2). Value sourced from R07_estmean_lb_fpr.csv; movement registered under R07-campaign-redraw.
# R09 — Anytime-Valid Detection on the Fair-Coin Stream

R09 reproduces v87 Figure 9 (fig:anytime) and the paragraph at L243: what happens to a fixed-horizon sign-CUSUM when the monitoring does not stop at the horizon it was calibrated for, and what a mixture martingale delivers instead. Three arms -- CUSUM, MIX, e-CUSUM -- on 20,000 fair-coin streams over [1, 4H], seven nominal levels, and a 10-point drift grid on 2,000 drift streams per cell (log line 9).

It certifies:
- Figure 9 (L243 paragraph, L559 caption)
- L243 narrative: fixed-horizon CUSUM loses time-uniform control under continuous monitoring to 4H; MIX maintains Ville's bound; e-CUSUM satisfies ARL0 >= 1/alpha
- L559 qualitative claims: MIX remains bounded by alpha under peeking at all 7 levels; CUSUM peeking exceeds MIX peeking at all 7 levels; Only MIX controls the time-uniform false-alarm probability; MIX matches CUSUM speed for moderate drifts (eta <= 0.10)
- The seven LaTeX macros in R09_claims.tex

Reproduction command: `bash run_experiment_R09.sh`

## Expected artefacts

### Artefacts that certify a published value

- `results/R09_eprocess_anytime/data/R09_validity_stopping.csv` — certifies L243 / Fig. 9(A) CUSUM peeking FPR, MIX peeking FPR, and the descriptive control (d) comparisons
- `results/R09_eprocess_anytime/data/R09_eprocess_race.csv` — certifies L243 CUSUM ADD at eta = 0.10, MIX ADD at eta = 0.10, and the ADD vs eta monotonicity controls
- `results/R09_eprocess_anytime/data/R09_level_granularity.csv` — certifies L243 CUSUM calibrated to 5% at H
- `results/R09_eprocess_anytime/figures/fig09_anytime_valid.png` — certifies Figure 9
- `results/R09_eprocess_anytime/tables/R09_claims.tex` — certifies the seven LaTeX macros

### Artefacts that certify a control and certify no published value

- `results/R09_eprocess_anytime/data/R09_arl0.csv` — certifies control C1 (censoring-ARL0 linkage) and C2 (arl0_bound_respected computation); carries 21 rows with censored_frac on every row
- `results/R09_eprocess_anytime/data/R09_eprocess_race_control_ecusum.csv` — certifies control C6 (reproducibility) and delivered control (c); carries 70 rows, 9 columns for the e-CUSUM control arm

## Measured execution cost

Execution completed in 1190.2s with 1 workers and control arm = ecusum. NUM_CHUNKS = 10 fixes the chunk decomposition, so a rerun at a different worker count must produce byte-identical artefacts (log line 472).

Breakdown: M1 completed in 492.2s over 10 chunks of 2000 streams; Calibration completed in 2.4s; H0 campaign completed in 510.0s: 20000 fair-coin streams over [1, 20000]; H1 campaign completed in 180.5s: 2000 drift streams per cell, 10 drift magnitudes, arms ['CUSUM', 'MIX', 'eCUSUM'] (log lines 293, 301, 302, 303).

## Known deviations from the submitted manuscript

**R09_v87_cusum_peeking_fpr (D2):** CUSUM peeking FPR at alpha = 0.05: manuscript value 18% vs compliant 19.88% (Wilson 95% CI [19.33%, 20.44%]). Absolute difference: 1.88 percentage points. Full float64: regenerated 0.1988, witness 0.1801 (log lines 429-430).

**R09_v87_add_parity (D2/D1):** MIX ADD at alpha = 0.05, eta = 0.10: manuscript value 409 vs compliant 410.40 (SEM 3.66). Rounded to nearest integer: 410 vs 409. CUSUM ADD at alpha = 0.05, eta = 0.10: manuscript value 539 vs compliant 532.85 (SEM 9.55). Rounded to nearest integer: 533 vs 539. Full float64: regenerated MIX 410.40266393442624, witness 409.1131405377981; regenerated CUSUM 532.851184346035, witness 538.8051546391753 (log lines 433-436).

**R09_v87_anytime_numerals (D1):** CUSUM calibrated to 5% at H: manuscript value 5% vs compliant 5%. Full float64: regenerated 0.05345, witness 0.0493 (log lines 431-432).

**R09_v87_stream_counts (D0):** L243/L559 fair-coin streams per level: manuscript 2\*10^4 vs compliant 20000. Full float64: regenerated 20000, witness 20000 (log lines 437-438).

All qualitative claims are preserved: MIX remains bounded by alpha under peeking at all 7 levels; CUSUM peeking exceeds MIX peeking at all 7 levels; Only MIX controls the time-uniform false-alarm probability; MIX matches CUSUM speed for moderate drifts (eta <= 0.10) under the selection-free matched-detection-rate quantile (log lines 439-442).
# R10 — Sensitivity to Conditional Asymmetry

R10 validates v87 Figure 10 (fig:skew_robustness, tex L565-L568) and L290, demonstrating that Fernandez-Steel skew-t(7) innovations preserve conditional independence while displacing the marginal probability P(epsilon_t > 0) away from 1/2. A fixed-reference CUSUM anchored at 1/2 triggers false alarms at 96.6%, but recentered monitoring using a trailing warm-up estimate q-hat restores nominal control with empirical FPR 1.0-1.5%. The stream generates 1000 GARCH(1,1) paths of 8000 steps each across four asymmetry parameters xi in {1.0, 0.85, 0.65, 0.5}, with alpha = 0.1058, beta = 0.8742, target variance 0.04.

Reproduction command: `bash run_experiment_R10.sh`.

## Expected artefacts

### Artefacts that certify published values
- `results/R10_skew_robustness/data/R10_skew_diagnostics.csv` — realized skewness and marginal rate q per xi (L290)
- `results/R10_skew_robustness/data/R10_skew_fpr.csv` — FPR rates for all CUSUM variants (Figure 10, L290)
- `results/R10_skew_robustness/tables/R10_claims.tex` — 10 LaTeX macros: RTenSkewnessMax, RTenQMax, RTenLbSignMin, RTenLbSignMax, RTenFprQhatMin, RTenFprQhatMax, RTenFprHalfMax, RTenFprOracleMax, RTenOperatorNullLevel, RTenFprHalfMaxExact
- `results/R10_skew_robustness/figures/fig10_skew_robustness.png` — Figure 10

### Artefacts that certify controls and no published value
- `results/R10_skew_robustness/data/R10_fs_constants.csv` — Fernandez-Steel standardization constants (control C6)
- `results/R10_skew_robustness/data/R10_skew_streams.csv` — raw stream data with sign identity check (control C4)
- `results/R10_skew_robustness/data/R10_lattice_exact_law.csv` — lattice exceedance validation against independent dynamic programs (control C7)
- `results/R10_skew_robustness/data/R10_operator_null_level.csv` — CUSUM level under perfect centring (control C8)
- `results/R10_skew_robustness/data/R10_design_effect.csv` — design effect measurements for pooled statistics (control C9)

## Measured execution cost

NOT RECOVERABLE FROM THE LOG.

## Known deviations from the submitted manuscript

**R10-skew_robustness-redraw (D1):** L290 marginal rate q shifts from 0.58 to 0.5822, within sampling error (z = +8.76 SE at the difference scale). The printed value 0.58 rounds to the regenerated 0.5822 at the manuscript's two-decimal precision.

**R10-fixed-cusum-redraw (D1):** L290 fixed-1/2 CUSUM false-alarm rate shifts from ~97% to 96.6% (z = -0.49 SE at the difference scale). The qualitative claim that asymmetry causes a fixed-1/2 CUSUM to "explode" holds: the rate remains above 90%.

**R10-skewness-redraw (D2):** L290 realized skewness shifts from -1.44 to -1.43 at two-decimal precision (z = +1.95 SE at the difference scale). The third decimal moves but the mechanism — conditional asymmetry displaces marginal probability — is preserved.

**R10-envelope-upper-redraw (D2):** Figure 10 caption FPR envelope upper bound shifts from 1.8% to 1.5% at one-decimal precision. The lower bound (1.0%) is unchanged (D0). The recentered CUSUM claim — FPR envelope 1.0-1.5% — remains within the manuscript's stated 1.0-1.8% range.
# R11 — Multi-Detector Generalization

R11 establishes that the false positive rate explosion of Section "The False Positive Explosion" and the detector-dependent cure of Section "Universality Across Detector Families" are properties of the sequential-detector family (CUSUM, Page-Hinkley, ADWIN, DDM, EDDM) and not of the CUSUM topology alone. The whitened Concept stream voids the schedule of penalties under heteroscedastic GARCH(1,1) streams with standardized t7 innovations, alpha = 0.08, and beta solved per target penalty Gamma across a 20-point grid from 1 to 200. Four campaigns validate the Whitening Proposition across detector families: (A) Data pipeline PHT under H0 across three threshold scalings, (B) Concept pipeline with five detectors under H0 and location shift c = 1.5 (Figures 15 and 11), (C) ADWIN magnitude grid at Gamma = 11.58 comparing local vs river implementations, (D) Data pipeline tax with three detectors under location shift c = 2.0 over 14,000-step streams (Figure 11). This stream certifies Figures 11 and 15.

Reproduction command: `bash run_experiment_R11.sh`

### Expected artefacts

**Artefacts that certify published values:**
- `results/R11_multi_detector/data/R11_pht_fpr_vs_gamma.csv`
- `results/R11_multi_detector/data/R11_concept_fpr_vs_gamma_independent_seeds.csv`
- `results/R11_multi_detector/data/R11_concept_add_vs_gamma.csv`
- `results/R11_multi_detector/data/R11_data_add_vs_gamma.csv`
- `results/R11_multi_detector/data/R11_slope_fits.csv`
- `results/R11_multi_detector/figures/fig11_data_vs_concept.png` (Figure 11)
- `results/R11_multi_detector/figures/fig15_multi_detector.png` (Figure 15)
- `results/R11_multi_detector/tables/R11_claims.tex`

**Artefacts that certify controls and certify no published value:**
- `results/R11_multi_detector/data/R11_concept_fpr_vs_gamma.csv` (CRN degeneracy identity witness)
- `results/R11_multi_detector/data/R11_adwin_magnitude.csv` (Block E: local vs river ADWIN comparison)
- `results/R11_multi_detector/data/R11_onset_convention_delta.csv` (onset convention comparison)
- `results/R11_multi_detector/figures/figA04_adwin_blind_zone.png` (Block E visualization)

Measured execution cost: 886.0s of campaign over 465000 monitored streams, 936.0s including the analysis.

### Known deviations from the submitted manuscript

D1-D2 deviations are documented. All deviations are at manuscript precision: printed numerical values shift but all qualitative claims are preserved. The Concept ADD ordering (PHT < CUSUM < ADWIN < DDM) holds across all arms. Cumulative detectors show near-linear log-log scaling with Gamma. Window-mean ADWIN degrades most severely under the whitened stream. EDDM remains permanently triggered (>90% FPR) under H0 Concept. Peak-to-peak ADD variation for cumulative detectors stays below 3.2%. PHT syncope occurs beyond Gamma ~ 75. Full deviation table in `docs/audits/AUDIT_R11.md` section 1.
# R12 — GJR Leverage Misspecification and Moment Singularity

R12 reproduces v87 Figures 12-13 and paragraphs L349-L353. Experiment A stresses a symmetric GARCH(1,1) filter with asymmetric GJR-GARCH innovations across 15 gamma_lev values (0.0 to 0.28), demonstrating how leverage misspecification inflates Data pipeline Ljung-Box rejection from 5.1% to 24.6% and false-alarm rate from 3.2% to 20.6% while the Concept pipeline maintains a flat 4.6-5.4% Ljung-Box and 7.6-8.4% false-alarm rate. Experiment B demonstrates detection decay under Student-t innovations as nu approaches the fourth-moment singularity at nu* = 4.0811, collapsing below 50% at nu <= 5.5 with survivorship-biased delays of 2,400-3,000 steps, while the Concept pipeline remains flat at 34-38 steps.

**Reproduction command**: `bash run_experiment_R12.sh`

**Expected artefacts**:

Artefacts that certify a published value:
- `results/R12_gjr_student/data/R12_leverage_fpr.csv` — 15 x 10000 streams, the source of Figure 12 and its caption statistics (L349, Fig.12)
- `results/R12_gjr_student/data/R12_singularity_add.csv` — 16 x 1000 streams, the source of Figure 13 and its caption statistics (L353, Fig.13)
- `results/R12_gjr_student/figures/fig12_leverage.png` — Figure 12
- `results/R12_gjr_student/figures/fig13_fat_tails.png` — Figure 13
- `results/R12_gjr_student/tables/R12_claims.tex` — 21 LaTeX macros with prefix \RTwelve

Artefacts that certify a control and certify no published value:
- `results/R12_gjr_student/data/R12_concept_crn_witness.csv` — 15 rows, CRN Concept arm degeneracy witness (C8), one number repeated 15 times
- `results/R12_gjr_student/data/R12_diagnostics.csv` — 245 rows, clamp binding rate measurements (C10)
- `data/reference/R12/orphans/expA_argarch_boundary.csv` — orphan witness for C3 task boundary, gap unexplained beside R07's certified measurement
- `data/reference/R12/orphans/expB_race_condition.csv` — 1000 rows, uncited, mechanism not attributed (C3b)

**Measured execution cost**: 373.2s with n_jobs = -1 over 316000 monitored streams (Experiment A: 173.7s for expA + 172.3s for expA_concept_indep = 150000 streams of 7000 steps; Experiment B: 13.1s for 16000 streams of 10000 steps) (log l.156-158, l.369). The submitted campaign ran 166000 streams in 185.7s.

## Known deviations from the submitted manuscript

R12-D2-L349-LB-0: Ljung-Box at gamma_lev = 0.0 shifted from 5.1% to 5.4% (log l.294).

R12-D2-L349-LB-1: Ljung-Box at gamma_lev = 0.28 shifted from 24.6% to 24.2% (log l.296).

R12-D2-L349-FPR-0: Data FPR at gamma_lev = 0.0 shifted from 3.2% to 3.5% (log l.298).

R12-D2-L349-FPR-1: Data FPR at gamma_lev = 0.28 shifted from 20.6% to 20.5% (log l.300).

R12-D2-L349-CONCEPT-FPR-MIN: Concept FPR minimum shifted from 7.6% to 7.4% (log l.302).

R12-D2-L349-CONCEPT-FPR-MAX: Concept FPR maximum shifted from 8.4% to 8.5% (log l.304).

R12-D2-L349-CONCEPT-LB-MIN: Concept Ljung-Box minimum shifted from 4.6% to 4.7% (log l.306).

R12-D1-L349-CONCEPT-LB-MAX: Concept Ljung-Box maximum unchanged at 5.4% at printed precision (log l.308).

R12-D1-L349-FACTOR: 'climbs by a factor of six' unchanged at printed precision (regenerated 5.92, witness 6.37) (log l.310).

R12-D2-L353-DET-10: detection at nu = 10 shifted from 83% to 82% (log l.320).

R12-D2-L353-DET-7: detection at nu = 7 shifted from 61% to 62% (log l.322).

R12-D1-L353-THRESHOLD: collapse threshold unchanged at 5.5 (log l.324).

R12-D2-L353-CENS-MIN: censored delay minimum shifted from 2,400 to 2,600 (log l.326).

R12-D1-L353-CENS-MAX: censored delay maximum unchanged at 3,000 at printed precision (log l.328).

R12-D1-L353-CONCEPT-MIN: Concept delay minimum unchanged at 34 (log l.330).

R12-D1-L353-CONCEPT-MAX: Concept delay maximum unchanged at 38 (log l.332).
# R13 — Oracle Ceiling and the Clairvoyant Frontier

R13 reproduces v87 Figure 14 and L331, establishing the clairvoyant frontier for concept-drift detection under a parameter oracle: a CUSUM on returns standardized by the conditional volatility of a GARCH(1,1) fitted on a window including the change point, with causal filtration, read against a bootstrap null that freezes the same volatility path [Lorden, 1971; Page, 1954; Moustakides, 1986]. The Whitening Proposition guarantees that under the null, sign(epsilon_t) forms an exact martingale regardless of conditional heteroskedasticity, so the sign pipeline requires no volatility model. Under the alternative with known change magnitude, the clairvoyant detector achieves the minimum possible detection delay, bounded by Jensen's inequality: the path divergence sum_t Delta^2/(2 sigma_t^2) exceeds the unconditional budget by a factor that quantifies the information gain from look-ahead parameter estimation.

The experiment establishes:
- v87 Figure 14: the oracle detectability frontier across four SPY episodes
- v87 L331: 3-day detection of the 2020 COVID-19 crash at a low single-digit phase false-alarm probability under likelihood-ratio increments, 16 days under the standardized-mean CUSUM, path divergence 10.6x the unconditional budget via Jensen's inequality
- Census verdicts at the matched operating point: 2009 recovery detected, 2019 advance missed, 2011 correction no alarm

The campaign evaluates two detectors (D1: standardized-mean CUSUM with dead band delta; D2: Gaussian likelihood-ratio increment) across four operating points (OP1_isoFPR5_H, OP2_ARL0_20, OP2b_ARL0_252, OP3_breakeven) on a 200-point lambda grid, using 20,000 bootstrap replicates for FPR_H and 5,000 for ARL0. Three volatility oracles are evaluated: V1 (look-ahead GARCH), V2 (leave-one-out realized volatility), V3 (contaminated realized volatility).

## Execution

```bash
bash run_experiment_R13.sh
```

## Expected artefacts

### Artefacts that certify a published value

| artefact | path | certifies |
|---|---|---|
| CSV | results/R13_oracle_ceiling/data/R13_oracle_frontier.csv | v87 Figure 14 oracle frontier |
| CSV | results/R13_oracle_ceiling/data/R13_oracle_operating_points.csv | v87 L331: 3-day LR CUSUM delay at E1/D2/V1/OP2b_ARL0_252; 16-day standardized-mean CUSUM delay at E1/D1/V1/OP2b_ARL0_252 |
| CSV | results/R13_oracle_ceiling/data/R13_oracle_diagnostics.csv | v87 L331: Jensen ratio 10.6x for V1 oracle; oracle certification and contamination counts |
| CSV | results/R13_oracle_ceiling/data/R13_clairvoyant_floor.csv | clairvoyant floor computation |
| Figure | results/R13_oracle_ceiling/figures/fig14_oracle_frontier.png | v87 Figure 14 |
| LaTeX macros | results/R13_oracle_ceiling/tables/R13_claims.tex | v87 L331: \RThirteenCovidDelayLR, \RThirteenCovidFprLR, \RThirteenCovidDelayStdMean, \RThirteenJensenRatio, \RThirteenJensenOracle, \RThirteenOracleCertifiedCount, \RThirteenOracleContaminatedCount, \RThirteenArlZeroCensoredFrac, \RThirteenCovidVerdict, \RThirteenRecoveryVerdict, \RThirteenAdvanceVerdict, \RThirteenCorrectionVerdict |

### Artefacts that certify a control and certify no published value

| artefact | path | certifies |
|---|---|---|
| CSV | results/R13_oracle_ceiling/data/R13_detector_recovery.csv | Control: detector recovery (D1, D2, D3) with power, symmetry, degenerate requirements |
| CSV | results/R13_oracle_ceiling/data/R13_qmle_recovery.csv | Control: QMLE recovery with equivalence gates on alpha, beta |

## Measured execution cost

Execution completed in 72.5s with 4 workers (log line 1149).

## Known deviations from the submitted manuscript

**Register entry: R13-campaign-redraw (D2)**

The campaign redraw due to 128-bit re-seeding of all Monte Carlo components (bootstrap FPR_H with 20,000 replicates, ARL0 null with 5,000 replicates) produces a different but internally consistent Monte Carlo draw. The COVID-19 LR CUSUM phase false-alarm probability shifts from 1.3% (manuscript) to 1.1% (regenerated) at OP2b_ARL0_252. The printed precision shifts at one decimal place (D2). The qualitative claim that the clairvoyant monitor achieves a low single-digit false-alarm probability is preserved. All other numerals of L331 are invariant at published precision: 3-day delay (D0), 16-day delay (D0), 10.6x Jensen ratio (D0, rounds to 10.6 at one decimal place), and all census verdicts (D0). Cause: 128-bit re-keying. No parameter tuning or tolerance widening was applied.
# R14 — Crypto iso-FPR Efficiency Reversal

R14 instantiates the efficiency reversal hypothesis of L345 on daily cryptocurrency returns (BTC and ETH). It measures v87 Figure 16 (`fig:crypto_race`) and every numeral of L345 via an iso-FPR race between the recentred sign-CUSUM detector (Concept) and a CUSUM on the honestly standardized GARCH(1,1) residual (Eco-L1). Both arms use bilateral CUSUM with dead band DELTA_P = 0.1 and thresholds calibrated via `bisect_fpr` to achieve exactly FPR = 5% on real placebo windows. The Concept pipeline whitens the sign stream via recentring, while Eco-L1 uses parametric GARCH standardization. The experiment spans 4215 daily BTC returns (2015-01-02 to 2026-07-17) and 3172 daily ETH returns (2017-11-10 to 2026-07-17), with quasi-Gaussian t_30 synthetic controls matched on empirical variances.

Reproduction: `bash run_experiment_R14.sh`

## Expected artefacts

### Artefacts that certify a published value

- `results/R14_crypto_isofpr/data/R14_crypto_diagnostics.csv`
- `results/R14_crypto_isofpr/data/R14_crypto_isofpr_race.csv`
- `results/R14_crypto_isofpr/data/R14_onset_delays.csv`
- `results/R14_crypto_isofpr/data/R14_qmle_recovery.csv`
- `results/R14_crypto_isofpr/figures/fig16_crypto_race.png`
- `results/R14_crypto_isofpr/tables/R14_claims.tex`

### Artefacts that certify a control and certify no published value

- `results/R14_crypto_isofpr/data/R14_crypto_diagnostics_legacy_seeds.csv`
- `results/R14_crypto_isofpr/data/R14_crypto_isofpr_race_legacy_seeds.csv`
- `results/R14_crypto_isofpr/data/R14_onset_delays_legacy_seeds.csv`
- `results/R14_crypto_isofpr/data/R14_qmle_recovery_legacy_seeds.csv`
- `results/R14_crypto_isofpr/figures/fig16_crypto_race_legacy_seeds.png`
- `results/R14_crypto_isofpr/tables/R14_claims_legacy_seeds.tex`

Measured execution cost: 11.6s (migrated default arm, log line 314).

## Known deviations from the submitted manuscript

R14-campaign-redraw: The entropy migration from hardcoded integer seeds (100, 200, 201, 300) to role-and-index keys redraws the synthetic GARCH stream paths, altering the ADD ratio trajectory for Synth_BTC. Synth_BTC ratio statistics (mean 1.04 vs manuscript 1.06, minimum 0.95 vs 0.98, maximum 1.24 vs 1.14) are classified D2. The witness arm with legacy seeds reproduces v87 values exactly (D0), confirming the deviation mechanism is the 128-bit re-keying and not a transcription error. All Real_BTC and diagnostic metrics remain D0; qualitative claims for Real_BTC hold as printed.
# R15 — Cross-Sectional Sign Monitor on 97 US Equities

R15 regenerates v87 Figure 17 (`fig:cross_section`) and every numeral of L376 by running the cross-sectional sign-CUSUM monitor on 97 surviving US equities, 2005–2025 (5154 trading days). It also discharges L389's printed promise of a public equity fetcher. The experiment pools K correlated streams under two calibrations—an independence assumption and a bootstrap over real null windows—and races the pooled monitor against single streams under injected drift, establishing the panel's origin and history.

**Reproduction command:** `bash run_experiment_R15.sh`

**Expected artefacts, split by purpose:**

Artefacts that certify a published value:
- `results/R15_cross_sectional/data/R15_panel_diagnostics.csv` — certifies rho_sign, K_eff, FPR_boot, whiteness switch point
- `results/R15_cross_sectional/data/R15_cross_sectional_race.csv` — certifies budget reduction plateau
- `results/R15_cross_sectional/data/R15_scatter_correlation.csv` — certifies scatter correlation
- `results/R15_cross_sectional/data/R15_covid_natural.csv` — certifies COVID detections under bootstrap threshold
- `results/R15_cross_sectional/figures/fig17_cross_section.png` — certifies Figure 17
- `results/R15_cross_sectional/tables/R15_claims.tex` — 15 macros under cardinal prefix \RFifteen

Artefacts that certify a control and certify no published value:
- `results/R15_cross_sectional/data/R15_panel_composition.csv` — frozen composition fidelity (control C1)
- `results/R15_cross_sectional/data/R15_race_windows.csv` — window population tracking
- `results/R15_cross_sectional/figures/fig17_cross_section_witness_blas.png` — witness-BLAS attribution arm
- `results/R15_cross_sectional/data/R15_panel_diagnostics_witness_blas.csv` — witness-BLAS attribution arm
- `results/R15_cross_sectional/data/R15_cross_sectional_race_witness_blas.csv` — witness-BLAS attribution arm
- `results/R15_cross_sectional/data/R15_covid_natural_witness_blas.csv` — witness-BLAS attribution arm
- `results/R15_cross_sectional/data/R15_panel_composition_witness_blas.csv` — witness-BLAS attribution arm
- `results/R15_cross_sectional/data/R15_race_windows_witness_blas.csv` — witness-BLAS attribution arm
- `results/R15_cross_sectional/data/R15_scatter_correlation_witness_blas.csv` — witness-BLAS attribution arm
- `results/R15_cross_sectional/tables/R15_claims_witness_blas.tex` — witness-BLAS attribution arm

**Measured execution cost:** 111.2s with 48 workers (default arm); 110.4s with 48 workers (witness-BLAS attribution arm) (logs/R15_cross_sectional/exp_R15_cross_sectional_b.log:223, logs/R15_cross_sectional/exp_R15_cross_sectional_b_witness_blas.log:223).

## Known deviations from the submitted manuscript

Two caption quantities carry a D2 classification and are reported in the D0-D3 table of docs/audits/AUDIT_R15.md:

`R15-scatter-sign` (register entry): v87's Figure 17 caption prints the relation `r >= 0.99` for the scatter correlation between budget reduction and bootstrap threshold at the plotted c = 0.25. The regenerated value is -0.9962104605839599 (signed) with |r| = 0.9962104605839599. The printed relation `r >= 0.99` is false; the mirrored relation `r <= -0.99` is true. The qualitative claim that the point-to-point scatter of panel B is almost entirely explained by variation in the bootstrap threshold holds on both campaigns; the falsification is of the printed relation only.

`R15-campaign-redraw` (register entry): v87's Figure 17 caption prints the bootstrap FPR envelope as 4.8–6.4%. The regenerated envelope is 4.0–5.9%. The qualitative claim that the bootstrap calibration holds the nominal level (all FPR_boot values lie inside the control band (0.03, 0.07)) is preserved; the shift is at the printed precision only.
# R16 — Regime Census and Sign Floor

R16 dates the bull/bear phases of SPY, PFF, VNQ and BWX over 2000-2025 and certifies v87's most-cited empirical claim across L57, L87, L329, and L374: that 80% of dated directional episodes fall out of budget. It prices two detection floors on every dated phase: ADD_min_unc = 504 ln(gamma)/SR^2 (the Sharpe ceiling) and ADD_min_sign = ln(gamma)/kl(q_phase || q_ref) (the Bernoulli budget). The experiment renders no figure; v87's census paragraphs L329 and L331 carry no \includegraphics and reference only \ref{fig:oracle_frontier}, which belongs to R01.

Reproduction command: `bash run_experiment_R16.sh`

## Expected artefacts

### Artefacts that certify published values
- `results/R16_regime_census/data/R16_regime_census.csv` — 66 phases (canonical arm: SPY 30 lunde_timmermann, PFF 7 pagan_sossounov, VNQ 18 pagan_sossounov, BWX 11 pagan_sossounov), certifies the 53/66, 52/66, 64/66 out-of-budget counts and the 80% headline.
- `results/R16_regime_census/data/R16_sign_floor.csv` — 66 rows, certifies the two floors per phase (unconditional and sign) that define detectability.
- `results/R16_regime_census/tables/R16_claims.tex` — 42 LaTeX macros under the RSixteen prefix that price the census and the counterfactual arms.

### Artefacts that certify controls and certify no published value
- `results/R16_regime_census/data/R16_regime_census_strict_ps.csv` — 48 phases (pure Pagan-Sossounov on all four tickers), counterfactual arm demonstrating the dating misdescription (D3).
- `results/R16_regime_census/data/R16_regime_census_symmetric.csv` — 102 phases (Lunde-Timmermann on every ticker whose check_sanity fails), counterfactual arm quantifying the substitution scope.
- `results/R16_regime_census/data/R16_boundary_convention_delta.csv` — 66 rows, boundary convention sensitivity (C4).
- `results/R16_regime_census/data/R16_meso_split_report.csv` — MESO merge report.
- `results/R16_regime_census/data/R16_feasibility_vs_gamma.csv` — feasibility counts across gamma values.

Measured execution cost: 0.2s for run (a), 0.0s for run (b). No parallelism and no stochastic component: R16's worker-count reproducibility axis is vacuous. (logs/R16_regime_census/exp_R16_regime_census_a.log:92, logs/R16_regime_census/exp_R16_regime_census_b.log:79)

## Known deviations from the submitted manuscript

**R16-dating-misdescription (D3):** The claim in v87 L329 that "a retrospective multi-scale Pagan--Sossounov bull/bear dating of the four streams (2000--2025; 66 phases after duration censoring)" is reachable by pure Pagan--Sossounov is falsified. Strict Pagan--Sossounov on all four streams yields 48 phases, not 66. The canonical census reproduces the 66 phases by substituting Lunde--Timmermann for SPY alone when check_sanity fails. The falsification touches the dating description only; it does NOT affect the 80% headline, which is computed from the canonical census. (logs/R16_regime_census/exp_R16_regime_census_a.log:44,51, logs/R16_regime_census/exp_R16_regime_census_b.log:10-11)

**R16-floor-frac-envelope (D2):** v87 L329 states "the floor consumes 55--92% of the phase". Measured over the 13 phases the ceiling does not exclude at gamma=20 unconditional: [50.1%, 92.1%]. The upper end reproduces; the lower end does not. None of the variants yields 55--92%. The single phase at 54.8% rounds to 55%, which SUGGESTS the published lower bound was read off that one phase rather than off the minimum of the set, but no measurement here establishes it. The cause is NOT identified. (logs/R16_regime_census/exp_R16_regime_census_b.log:54-57,63)
# R17 — Econometric Baseline and the Estimation Cost of the Parametric Route

R17 prices what the parametric route costs when the warm-up is finite: the QMLE persistence at a 250-step window, the false-alarm rate it delivers, the warm-up length at which the level returns, and the sign pipeline's rate over the same axis. It feeds v87 L341 and renders no figure of the manuscript.

## Published Claims and Regenerated Values

The compliant deterministic pipeline certifies the true persistence at 0.85 (D0), but regenerated values differ at printed precision: median persistence at n_warmup = 250 is 0.63 (D2), FPR_Eco at n_warmup = 250 is 10.5% (D2), FPR_Eco at n_warmup = 500 is 7.0% (D2), and the sign FPR envelope is 10-11% (D2). Despite these D2 deviations, all three qualitative claims of L341 are corroborated.

## Reproduction Command

```bash
bash run_experiment_R17.sh
```

## Expected Artefacts

### Artefacts that certify published values
- `results/R17_econometric_baseline/tables/R17_claims.tex` — LaTeX macros for L341 claims
- `results/R17_econometric_baseline/data/R17_warmup_sensitivity.csv` — warm-up sensitivity table (certifies L341's persistence median, FPR_Eco rates, and sign FPR envelope)

### Artefacts that certify controls and certify no published value
- `results/R17_econometric_baseline/data/R17_fpr_baseline.csv` — protocol 3a FPR baseline (FPR explosion belongs to fig:fpr_explosion, R03)
- `results/R17_econometric_baseline/data/R17_add_baseline.csv` — protocol 3b ADD baseline (delay race belongs to tab:isofpr_race, R04)
- `results/R17_econometric_baseline/data/R17_fpr_arms.csv` — protocol 3a arms
- `results/R17_econometric_baseline/data/R17_misspecification.csv` — protocol 3c misspecification (L349's numerals belong to fig:leverage, R12)
- `results/R17_econometric_baseline/data/R17_warmup_fits.csv` — per-fit diagnostics for protocol 3d
- `results/R17_econometric_baseline/data/R17_fpr_baseline_legacy_qmle.csv` — legacy-QMLE diagnostic arm
- `results/R17_econometric_baseline/data/R17_add_baseline_legacy_qmle.csv` — legacy-QMLE diagnostic arm
- `results/R17_econometric_baseline/data/R17_fpr_arms_legacy_qmle.csv` — legacy-QMLE diagnostic arm
- `results/R17_econometric_baseline/data/R17_misspecification_legacy_qmle.csv` — legacy-QMLE diagnostic arm
- `results/R17_econometric_baseline/data/R17_warmup_sensitivity_legacy_qmle.csv` — legacy-QMLE diagnostic arm
- `results/R17_econometric_baseline/data/R17_warmup_fits_legacy_qmle.csv` — legacy-QMLE diagnostic arm
- `results/R17_econometric_baseline/tables/R17_claims_legacy_qmle.tex` — legacy-QMLE diagnostic arm macros

## Measured Execution Cost

363.7s (SPECS 1.10 default arm, exp_R17_econometric_baseline.log:260).

## Known deviations from the submitted manuscript

**R17-001**: Persistence median at n_warmup = 250 shifts from 0.62 to 0.63. The qualitative claim that "the estimated persistence collapses to a median alpha_hat + beta_hat" (L341) is corroborated: 0.63 is well below the true persistence 0.85.

**R17-002**: FPR_Eco at n_warmup = 250 shifts from 9.5% to 10.5%, and at n_warmup = 500 from 3.0% to 7.0%. The qualitative claim that "the false-alarm rate at that window is materially above the level it holds from n = 500 onward, and the level IS restored from n = 500" (L341) is corroborated: the rate falls from 10.5% to 7.0%, and the Wilson 95% CI at n=500 [0.04215178292291873, 0.11405578216683726] (exp_R17_econometric_baseline.log:248) contains the nominal 0.05.

**R17-003**: Sign FPR envelope shifts from 3-8% to 10-11%. The qualitative claim that "the sign pipeline is warm-up-independent in practice" (L341) is corroborated: the WLS slope of the rate on log(n_warmup) is 0.0021037529986339164 with 95% paired-bootstrap interval [-0.01529432408925942, 0.01945446250398922] (exp_R17_econometric_baseline.log:188), which covers zero.
# R18 — Ljung-Box Power on Binary Streams

R18 establishes a global positive control bounding what the manuscript's Ljung-Box non-rejections exclude at four sites: Line 278 (binary errors hold nominal level 3.3-5.0%), Line 290 (binary error stream stays white up to Gamma = 200), the Figure 6 caption at Line 286 (no detectable autocorrelation), and Line 318 (lag-20 Ljung-Box finds no serial correlation). It certifies no figure, table, or number of the submitted manuscript; it produces Appendix Figure A05 (figA05_ljungbox_power.png) and the LaTeX macro file R18_claims.tex.

Reproduction command: `bash run_experiment_R18.sh`.

## Expected artefacts

### Artefacts that certify a published value
None. R18 reproduces no figure, table, or number from v87 (logs/R18_ljungbox_power/exp_R18_ljungbox_power.log line 11).

### Artefacts that certify a control and certify no published value
- `results/R18_ljungbox_power/data/R18_power_vs_theta.csv` — rejection rates on the 36-point amplitude grid at n = 8000
- `results/R18_ljungbox_power/data/R18_power_vs_horizon.csv` — rejection rates on the 36 x 4 grid (36 amplitudes x 4 horizons)
- `results/R18_ljungbox_power/data/R18_detectable_amplitude.csv` — theta_80 and rho_80 grid and analytic estimates with cluster-bootstrap intervals at all four horizons
- `results/R18_ljungbox_power/data/R18_applied_to_sign_streams.csv` — application arms: classifier_error (13 penalties) and raw_sign (20 penalties) at n = 8000
- `results/R18_ljungbox_power/data/R18_size_at_null.csv` — size and KS calibration at theta = 0 for all four horizons
- `results/R18_ljungbox_power/figures/figA05_ljungbox_power.png` — empirical power curves against analytic predictions
- `results/R18_ljungbox_power/tables/R18_claims.tex` — 23 macros with prefix \REighteen carrying bound values and diagnostics

## Measured execution cost
Execution completed in 291.3s over 45000 generated streams: 1000 common-random-number streams read at 36 amplitudes x 4 horizons in two passes (129.3s for n = 128000 alone, 2.9s for the other three), 10000 for C5, 13000 classifier streams (131.4s) and 20000 sign streams (22.3s) (logs/R18_ljungbox_power/exp_R18_ljungbox_power.log line 104).
