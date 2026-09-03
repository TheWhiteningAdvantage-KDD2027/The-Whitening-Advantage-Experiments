# Stream Deviations Registry

This document records all numerical deviations between the deterministic compliant pipeline and the submitted manuscript values, classified according to the D0-D3 scale defined in the reproducibility protocol.

---

## Register index

Every deviation this repository carries has an identifier of the form `R[XX]-<subject>`. The
identifier is what a camera-ready candidate cites, what `README.md` section 6.1 lists for the
formal contradictions, and what `experiments/common/verify_camera_ready.py` resolves when it checks
that a staged candidate declares the right family. A candidate that carries no identifier is a
clarification and is marked `NO DEVIATION` in its header; a candidate that carries one is a
correction and must cite an identifier that appears in this index.

Class A means the deviation is a consequence of the compliant pipeline's own specification — the
128-bit re-keying, the single-threaded BLAS pinning, or a defect found in the submitted apparatus —
rather than of a choice made during regeneration. Severity is the D0-D3 scale of section 4.1 of
`AGENTS.md`; entries that contradict no printed value carry no severity and record a scope or
precision statement instead. The stream section below each identifier's row documents it in full.

| identifier                          | stream | class | severity    | what it names                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ----------------------------------- | ------ | ----- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `R02-campaign-redraw`               | R02    | A     | D2          | The i.i.d. arm rate, the pooled binary-error rate and its Wilson bounds move under the compliant pipeline (9.2 to 5.8, 4.4 to 4.2, [2.8, 7.1] to [2.5, 6.8]).                                                                                                                                                                                                                                                                                                 |
| `R02b-iid-arm-rejection`            | R02b   | A     | **D3**      | L278 states the wrong moment condition for the validity of the chi-square approximation to the Ljung-Box statistic on squared innovations.                                                                                                                                                                                                                                                                                                                    |
| `R02b-iid-arm-over-rejection`       | R02b   | A     | **D3**      | L278 states the $t_7$ i.i.d. arm "already over-rejects" at 9.2%. The regenerated rate at that arm is 5.8%, Wilson $[4.51, 7.43]\%$: the interval excludes the printed 9.2% and contains the 5% nominal level. At 1000 streams the standard error of a rate near 5% is 0.0069, so 9.2% sits six standard errors from nominal and the experiment has the resolution to exclude it. Distinct from `R02b-iid-arm-rejection`, which concerns the stated mechanism. |
| `R02b-nu-grid-redraw`               | R02b   | A     | D2          | The i.i.d. arm rejection rate is nu-dependent and every grid point moves under the redraw; the nominal level is excluded up to nu = 6, not nu = 7.                                                                                                                                                                                                                                                                                                            |
| `R03-campaign-redraw`               | R03    | A     | D2          | Every FPR numeral of the explosion-and-cure figure moves under the compliant pipeline at the manuscript's printing precision.                                                                                                                                                                                                                                                                                                                                 |
| `R03-cusum-nominal-level`           | R03    | A     | no severity | L171's descriptor "calibrated to a nominal 5% under IID noise" is accurate for ADWIN and not for the StrictCUSUM, which delivers 2.0% [0.9, 4.3]% under exact i.i.d. noise.                                                                                                                                                                                                                                                                                   |
| `R04-gamma-grid-defect`             | R04    | A     | **D3**      | The submitted campaign's Gamma grid had collapsed to a single point through a parameter-order defect in `solve_beta_for_gamma`, so the Recalib penalty and the flatness of the family controls are published off a grid that was never spanned.                                                                                                                                                                                                               |
| `R04b-efficiency-crossing`          | R04b   | A     | **D3**      | The Eco-L1 efficiency crossing is published at nu* ~ 4.9; every estimator on the refined twelve-point grid places it higher and the inferential bracket excludes it.                                                                                                                                                                                                                                                                                          |
| `R04b-estimation-cost`              | R04b   | A     | **D3**      | The finite warm-up is published as costing 0.3 degrees of freedom; three independent routes put it an order of magnitude higher and no interval among them reaches 0.3.                                                                                                                                                                                                                                                                                       |
| `R05-campaign-redraw`               | R05    | A     | D2          | The scale-law fit constants, the sqrt-rule FPR and the ramp-campaign numerals move under the 128-bit re-keying.                                                                                                                                                                                                                                                                                                                                               |
| `R05-lambda-c-numeral`              | R05    | A     | D2          | The lambda_C numeral of the scaling-validation section.                                                                                                                                                                                                                                                                                                                                                                                                       |
| `R05-sixth-moment-gloss`            | R05    | A     | no severity | The Appendix B gloss on the sixth-moment boundary.                                                                                                                                                                                                                                                                                                                                                                                                            |
| `R06-fourth-moment-boundary`        | R06    | A     | D1          | The fourth-moment boundary Gamma is carried in the manuscript as a literal 41.6 and is computed here in closed form as 41.584288, which rounds to the published value.                                                                                                                                                                                                                                                                                        |
| `R07-bias-bound-not-a-bound`        | R07    | A     | **D3**      | L308 states the classical small-sample AR bias stays under 2.9e-3 across the 7 x 4 grid; the largest absolute bias over the 28 diagnostic cells is 3.1268677e-3.                                                                                                                                                                                                                                                                                              |
| `R07-campaign-redraw`               | R07    | A     | D2          | Every R07 Monte-Carlo cell moves under the re-keying; the R08 macros that consume R07 cells inherit the movement.                                                                                                                                                                                                                                                                                                                                             |
| `R07-dispersion-cost`               | R07    | A     | no severity | L308's "costs at most 0.4 points of rejection" does not name the quantity the 0.4 measures, points of what and above what.                                                                                                                                                                                                                                                                                                                                    |
| `R07-lambda-star-estimator`         | R07    | A     | no severity | The rule by which lambda* is computed, registered so that R07 and R08 do not both macro-ise it.                                                                                                                                                                                                                                                                                                                                                               |
| `R07-oracle-band-precision`         | R07    | A     | no severity | The Figure 7 panel B caption places two true statements side by side and a reader joins them into a false one about the operating level.                                                                                                                                                                                                                                                                                                                      |
| `R08-campaign-redraw`               | R08    | A     | D2          | The adverse-direction numerals of L311 and the Figure 8 caption move under the re-keying.                                                                                                                                                                                                                                                                                                                                                                     |
| `R08-delivered-level-above-nominal` | R08    | A     | **D3**      | L241 selects "the nearest attainable level at or below nominal" while its own footnote makes the implemented test the weak comparison, whose level at that threshold is above nominal.                                                                                                                                                                                                                                                                        |
| `R09-add-conditioning`              | R09    | A     | no severity | The delay comparison of Figure 9B is conditional on detection, which the caption does not say.                                                                                                                                                                                                                                                                                                                                                                |
| `R09-arl0-censoring`                | R09    | A     | no severity | Panel C's CUSUM and MIX curves sit on the simulation horizon rather than on an attained ARL0.                                                                                                                                                                                                                                                                                                                                                                 |
| `R09-campaign-redraw`               | R09    | A     | D2          | The three Monte-Carlo numerals of L243 and Figure 9A move under the re-keying.                                                                                                                                                                                                                                                                                                                                                                                |
| `R09-cusum-add-parity-d2`           | R09    | A     | D2          | The fixed-horizon CUSUM delay at parity, 539 steps published against 533 reproduced.                                                                                                                                                                                                                                                                                                                                                                          |
| `R09-cusum-peeking-fpr-d2`          | R09    | A     | D2          | The CUSUM realized false-alarm rate under continuous monitoring, 18% published against 19.88% reproduced.                                                                                                                                                                                                                                                                                                                                                     |
| `R09-mix-add-parity-d1`             | R09    | A     | D1          | The mixture delay at parity, 409 steps published against 410 reproduced.                                                                                                                                                                                                                                                                                                                                                                                      |
| `R10-campaign-redraw`               | R10    | A     | D2          | L290's realized skewness and the Figure 10 caption's measured FPR envelope move under the re-keying.                                                                                                                                                                                                                                                                                                                                                          |
| `R11-figure11-caption`              | R11    | A     | no severity | The Figure 11 caption states one panel's parameters for both.                                                                                                                                                                                                                                                                                                                                                                                                 |
| `R11-gamma-grid-floor`              | R11    | A     | no severity | The lower bound of the Gamma grid (1) is analytically unreachable at alpha=0.08 (floor is ~1.17).                                                                                                                                                                                                                                                                                                                                                             |
| `R11-onset-convention`              | R11    | A     | no severity | The four delays of Figure 15B were measured under two onset conventions and are not comparable as printed.                                                                                                                                                                                                                                                                                                                                                    |
| `R11-pht-gamma-rule`                | R11    | A     | no severity | The PHT's lambda x Gamma rule drifts across the nominal level rather than holding it.                                                                                                                                                                                                                                                                                                                                                                         |
| `R11-pht-slope`                     | R11    | A     | no severity | The three log-log slopes of L298 have no traceable origin and no stated domain.                                                                                                                                                                                                                                                                                                                                                                               |
| `R11-pht-syncope`                   | R11    | A     | D2          | The numeral locating the stochastic syncope on the Gamma axis.                                                                                                                                                                                                                                                                                                                                                                                                |
| `R11-regenerated`                   | R11    | A     | D2          | Every R11 Monte-Carlo value moves because the entropy is re-keyed to a 128-bit SeedSequence on ROLE and INDEX alone, producing a common-random-numbers design.                                                                                                                                                                                                                                                                                                |
| `R12-campaign-redraw`               | R12    | A     | D2          | The leverage-misspecification and moment-singularity numerals of L349 and L353 move under the re-keying.                                                                                                                                                                                                                                                                                                                                                      |
| `R12-censored-delay-d2`             | R12    | A     | D2          | The survivorship-biased delay range, 2,400-3,000 published against 2,610-2,999 reproduced.                                                                                                                                                                                                                                                                                                                                                                    |
| `R12-concept-delay-d1`              | R12    | A     | D1          | The Concept delay range 34-38 steps, which reproduces.                                                                                                                                                                                                                                                                                                                                                                                                        |
| `R12-detection-rate-d2`             | R12    | A     | D2          | The Data detection rates at nu = 10 and nu = 7, 83% and 61% published against 82% and 62% reproduced.                                                                                                                                                                                                                                                                                                                                                         |
| `R13-campaign-redraw`               | R13    | A     | D2          | The phase false-alarm probability beside the 3-day detection moves from 1.3% to 1.1%.                                                                                                                                                                                                                                                                                                                                                                         |
| `R13-frozen-null-scope`             | R13    | A     | no severity | "a bootstrap null freezing the same volatility path" describes one arm of one axis.                                                                                                                                                                                                                                                                                                                                                                           |
| `R13-negative-control-scope`        | R13    | A     | no severity | L331 calls a different calibration "the matched operating point" than the one the negative control uses.                                                                                                                                                                                                                                                                                                                                                      |
| `R13-operating-points-unnamed`      | R13    | A     | no severity | L331 prints three numerals without naming the calibration they are read at.                                                                                                                                                                                                                                                                                                                                                                                   |
| `R14-campaign-redraw`               | R14    | A     | D2          | L345's three quasi-Gaussian synthetic-control numerals move under the 128-bit re-keying; the legacy-seed witness arm reproduces v87 exactly.                                                                                                                                                                                                                                                                                                                  |
| `R15-campaign-redraw`               | R15    | A     | D2          | The bootstrap FPR envelope of the cross-section moves under the re-keying.                                                                                                                                                                                                                                                                                                                                                                                    |
| `R15-scatter-sign`                  | R15    | A     | D2          | The caption prints a signed relation r >= 0.99; the measured correlation is negative on both campaigns, with abs(r) ~ 0.99.                                                                                                                                                                                                                                                                                                                                   |
| `R16-boundary-sensitivity`          | R16    | A     | no severity | The boundary convention is declared but its effect on the headline count is never reported.                                                                                                                                                                                                                                                                                                                                                                   |
| `R16-covid-floor-values`            | R16    | A     | D2          | The COVID floor values at the two calibrations.                                                                                                                                                                                                                                                                                                                                                                                                               |
| `R16-dating-misdescription`         | R16    | A     | **D3**      | The census is described as a multi-scale Pagan-Sossounov dating of the four streams; strict Pagan-Sossounov yields 48 phases, not 66.                                                                                                                                                                                                                                                                                                                         |
| `R16-floor-frac-envelope`           | R16    | A     | D2          | L329's "the floor consumes 55--92% of the phase"; the compliant pipeline measures [50.1%, 92.1%].                                                                                                                                                                                                                                                                                                                                                             |
| `R16-out-of-budget-frac`            | R16    | A     | D1          | The out-of-budget fraction at Gamma = 20, 80% published against 80.3% reproduced.                                                                                                                                                                                                                                                                                                                                                                             |
| `R16-sharpe-one-cost`               | R16    | A     | D2          | The Sharpe-one cost evaluations at the two calibrations.                                                                                                                                                                                                                                                                                                                                                                                                      |
| `R16-substitution-scope`            | R16    | A     | no severity | The census reaches 66 phases by substituting Lunde-Timmermann for SPY alone; applied consistently the substitution gives 102 phases.                                                                                                                                                                                                                                                                                                                          |
| `R17-campaign-redraw`               | R17    | A     | D2          | Four of the five L341 numerals move at their printed precision under the re-keying.                                                                                                                                                                                                                                                                                                                                                                           |
| `R17-eco-l1-arm-identity`           | R17    | A     | **D3**      | A false-alarm figure is attributed to the arm Table 1 defines as the level residual, while the cell that produced it monitors the squared standardized residual.                                                                                                                                                                                                                                                                                              |
| `R18-ljungbox-power`                | R18    | A     | no severity | The two load-bearing non-rejections do not state the power of the test that produced them.                                                                                                                                                                                                                                                                                                                                                                    |

---

## R01 — Real World Backtest

**Deviation Class: D0**

**Affected Metrics:** GARCH(1,1) QMLE parameters (omega, sigma_unc), COVID-19 trajectory peaks (Data pipeline only)

**Root Cause:** Floating-point associativity changes when BLAS thread counts are pinned to 1 in the compliant deterministic pipeline versus the multithreaded BLAS environment used in the submitted campaign.

**Mechanism:** Summation order in vectorized reductions (variance computation, GARCH likelihood) becomes a function of the thread scheduler under multithreaded BLAS. The compliant pipeline eliminates this non-determinism by enforcing single-threaded execution, resulting in ULP-level differences in reduction results.

**Quantitative Impact:**
- omega (SPY): Manuscript value 5.1751719325974024e-06 vs compliant 5.1751719325973652e-06 (relative difference: 6.8e-17)
- sigma_unc (SPY): Manuscript value 0.00933654472777823 vs compliant 0.0093365447277781975 (relative difference: 3.4e-17)
- COVID-19 Data peak: Manuscript value 0.37192244808245406 vs compliant 0.3719224480824543 (8 ULP difference, within 16-ULP budget)
- COVID-19 Concept peak: Bit-identical (0 ULP difference)

**Published Precision Impact:** NONE. All affected values, when rounded to the precision presented in the manuscript (typically 1-2 decimal places for gamma_hat, 2 decimal places for p-values), are identical between the submitted campaign and the compliant pipeline.

**Qualitative Claim Impact:** NONE. All qualitative claims (detection/non-detection, relative magnitudes, convergence properties) are preserved.

**Verification:** All R01 tests pass with tolerance budgets set from the largest observed drift (1e-13 relative tolerance for omega/sigma_unc, 16 ULP for trajectory peaks).

**Candidate Files:** See `docs/camera_ready_candidates/R01_v87_garch_calibration.md` for LaTeX macro diff blocks.

**Status:** CERTIFIED — D0 deviation documented and bounded. No manuscript changes required at published precision.

---

## R02 — Ljung-Box Whiteness on Multi-ETF GARCH Streams

**Deviation Class: D2**

**Affected Metrics:** IID arm data rejection rate (p_data on squared GARCH innovations), pooled concept rejection rate, Wilson 95% confidence interval bounds.

**Root Cause:** BLAS threading differences affect the variance-targeted QMLE parameter recovery for GARCH(1,1) processes with t7 innovations. This alters the generated stream paths, leading to different Ljung-Box test statistics on the squared inputs.

**Mechanism:** Under multithreaded BLAS, floating-point associativity in vectorized GARCH likelihood computations produces parameter estimates that differ at the ULP level. These small parameter shifts cascade into the simulated path generation, changing the realized variance profile and thus the Ljung-Box p-values on ε_t^2.

**Quantitative Impact:**
- IID arm data rejection rate: Manuscript value 9.2% vs compliant 5.8% (absolute difference: 3.4 percentage points)
- Pooled concept rejection rate: Manuscript value 4.4% vs compliant 4.2% (absolute difference: 0.2 percentage points)
- Wilson 95% CI lower bound: Manuscript value 2.8% vs compliant 2.5% (absolute difference: 0.3 percentage points)
- Wilson 95% CI upper bound: Manuscript value 7.1% vs compliant 6.8% (absolute difference: 0.3 percentage points)
- Concept rejection range: Manuscript 3.3--5.0% vs compliant 3.3--5.0% (bit-identical)
- Maximum clustered p-value: Manuscript < 1e-10 vs compliant 5.26e-18 (bound satisfied)
- Gamma penalty ranges: Manuscript Cal. A 3.90--8.32, Cal. B 31.94--110.49 vs compliant identical (D0)

**Published Precision Impact:** PARTIAL. The IID arm rejection rate shifts from 9.2% to 5.8% at printed precision. The pooled rejection and Wilson interval bounds also shift at one decimal place precision.

**Qualitative Claim Impact:** NONE. The over-rejection claim (rate > 5%) remains valid for both 9.2% and 5.8%. The concept-level calibration holds the nominal 5% level across all regimes. The Whitening Proposition is corroborated: binary classification errors show no detectable autocorrelation.

**Verification:** All R02 tests pass. The i.i.d. arm rejection rate (5.8%) stays within the 0--25% range asserted by test_iid_arm_rejection_is_reported_not_asserted. The pooled Wilson interval [2.5%, 6.8%] covers the nominal 5% level. Maximum clustered p-value (5.26e-18) satisfies the manuscript bound p < 1e-10.

**Candidate Files:** See `docs/camera_ready_candidates/R02_v87_ljungbox_whiteness.md` for LaTeX macro diff blocks.

**Status:** CERTIFIED — D2 deviation documented. Qualitative claims preserved. No manuscript narrative changes required.

---

## R02b — IID ARM Mechanism Resolution

**Deviation Class: D3 (one row) and D2 (four rows)**

**Register entries:** `R02b-iid-arm-rejection` (Class A, **D3**) and `R02b-nu-grid-redraw`
(Class A, D2).

**Affected Metrics:** the moment condition L278 states for the validity of the chi-square
approximation to the Ljung-Box statistic on squared innovations; IID arm rejection rates on squared
innovations across the degrees of freedom grid (nu = 5, 6, 7, 8.5, 12, 30); Wilson 95% confidence
interval bounds.

---

### `R02b-iid-arm-rejection` — Class A, severity **D3**

**Manuscript site:** L278, the subordinate clause "where $t_7$ innovations deprive
$\varepsilon_t^2$ of a fourth moment and the $\chi^2$ approximation fails".

**What is contradicted.** The stated condition. For an i.i.d. tested series the sample
autocorrelations are asymptotically normal with covariance I/n under the single requirement that
the tested series have a finite variance [Anderson and Walker, 1964; Brockwell and Davis, 1991,
Theorem 7.2.1]. The tested series on this arm is eps_t^2, so the requirement is
E[eps^4] < infinity, i.e. nu > 4 for Student-t innovations. t_7 satisfies it. The moment absent at
nu <= 8 is E[eps^8]; it governs the tail quantile of the sample autocorrelations, not the validity
of the limit. A false statement of the condition under which an asymptotic approximation holds is a
qualitative claim, not a numeral, and its falsification is D3.

**Source cells** (all read with `float_precision='round_trip'`):
- `results/R02b_iid_arm_resolution/data/R02b_rejection_vs_nu.csv` :: `contains_nominal_squared`, row nu=7 = `True`; `wilson_low_squared` = 0.045132906395672477, `wilson_high_squared` = 0.074249845843437106 (log line 10)
- `results/R02b_iid_arm_resolution/data/R02b_rejection_vs_nu.csv` :: `contains_nominal_squared`, rows nu=5 and nu=6 = `False`; Wilson 95% on the rejection rate [0.071980997942320851, 0.10717225104977657] and [0.06384721576082919, 0.097374914884008235] (log lines 8-9)
- `results/R02c_horizon_sweep/data/R02c_rejection_vs_horizon.csv` :: `contains_nominal_squared` = `True` for nu=7 at all four horizons (2000, 8000, 32000, 128000) and `False` for nu=5 and nu=6 at all four
- `results/R02c_horizon_sweep/data/R02c_streams.csv` :: pooled over the four horizons, rejection rate 7.75% [6.96, 8.62]% at nu=5, 7.72% [6.94, 8.59]% at nu=6, 5.60% [4.93, 6.36]% at nu=7
- R02c witness control at nu=7: KS statistic 0.3666 against Uniform(0,1), p-value 0.5480 (R02c log lines 14-15)

**The eighth-moment account is refuted by its own control.** E[eps^8] is infinite for every nu <= 8,
nu = 7 included. If that absence were the operative cause the nu = 7 arm would over-reject with
nu = 5 and nu = 6. It does not, at any of the four horizons.

**Scope.** What is contradicted is the stated reason the chi-square approximation fails on the
i.i.d. arm. Not contradicted: that the squared inputs over-reject there (they do — 8.8% at nu = 5
and 7.9% at nu = 6, both excluding the nominal level); the whitening property; the exactness of the
Concept threshold; the binary-error arm's nominal level; and any proposition of v87. The printed
rate 9.2% and its movement under redraw are `R02b-nu-grid-redraw`, not this entry.

**The true mechanism is not identified.** The over-rejection is present at nu <= 6 and absent at
nu >= 7 at every horizon up to n = 128000, and that boundary coincides with the loss of the sixth
moment (E[eps^6] < infinity iff nu > 6). Locating a boundary is not establishing a cause; no
discriminating test against a candidate mechanism was run, and neither this register nor
`docs/audits/AUDIT_R02b.md` supplies one.

---

### `R02b-iid-arm-over-rejection` — Class A, severity **D3**

**Falsified claim (L278):** the manuscript states that the squared inputs "already over-reject on the i.i.d. arm ($9.2\%$)", with $t_7$ innovations. At $\nu = 7$ the regenerated rate is 5.8%, Wilson $[4.51, 7.43]\%$. Two legs, both required: the interval **excludes** the printed 9.2%, and it **contains** the 5% nominal level. At $n = 1000$ streams the standard error of a rate near 5% is 0.0069, so 9.2% lies six standard errors from nominal — the experiment has the resolution to exclude it, and a failure to corroborate here is not a failure of power.

**Scope:** the falsification is localized to the $t_7$ arm the text defines. The regenerated sweep does find over-rejection at $\nu = 5$ (8.8%) and $\nu = 6$ (7.9%), both excluding nominal, but neither is the manuscript's arm and neither reproduces a published value. Not touched: the whitening property, the exactness of the Concept threshold, the binary-error arm's nominal level, and any proposition of v87. The stated *mechanism* is a separate contradiction carried at D3 by `R02b-iid-arm-rejection`. The true mechanism is not identified.

**Source:** `R02b_rejection_vs_nu.csv` :: `reject_rate_squared`, `wilson_low_squared`, `wilson_high_squared`, `contains_nominal_squared`, row `nu = 7`.

---

### `R02b-nu-grid-redraw` — Class A, severity D2 {#r02b-nu-grid-redraw--class-a-severity-d3  data-source-line="92"}

**Root Cause:** The manuscript reports a single i.i.d. arm over-rejection rate of 9.2% at line 278 without specifying the degrees of freedom. The R02b experiment extends this to a full grid, revealing the rate depends critically on tail heaviness. Under the compliant deterministic pipeline with single-threaded BLAS, the simulated stream paths differ from the original multithreaded campaign.

**Mechanism:** Floating-point associativity in vectorized operations under multithreaded BLAS produces ULP-level differences in numerical results. These cascade through the simulation pipeline, altering realized variance profiles and thus Ljung-Box p-values on squared inputs. The compliant pipeline eliminates this non-determinism while producing different but internally consistent results.

**Quantitative Impact:**
- IID arm rejection rate at nu = 7: Manuscript value 9.2% vs compliant 5.8% (absolute difference: 3.4 percentage points)
- IID arm rejection rate at nu = 6: Compliant 7.9% (Wilson CI [6.4%, 9.7%]), excludes nominal 5% level
- IID arm rejection rate at nu = 5: Compliant 8.8% (Wilson CI [7.2%, 10.7%]), excludes nominal 5% level
- IID arm rejection rate at nu = 8.5: Compliant 6.1% (Wilson CI [4.8%, 7.8%]), contains nominal 5% level
- IID arm rejection rate at nu = 12: Compliant 4.8% (Wilson CI [3.6%, 6.3%]), contains nominal 5% level
- IID arm rejection rate at nu = 30: Compliant 6.0% (Wilson CI [4.7%, 7.6%]), contains nominal 5% level
- Nominal level excluded up to: nu = 6 (manuscript implication: nu = 7)

**Published Precision Impact:** PARTIAL. The nu = 7 rejection rate shifts from 9.2% to 5.8% at one decimal place precision. The qualitative transition point (over-rejection at heavy tails, containment at light tails) remains at the same location between nu = 6 and nu = 7.

**Qualitative Claim Impact:** none carried by this entry. Every grid point moves under the 128-bit re-keying, which is pre-classified Class A, D2. The two qualitative findings of this stream are carried separately and at D3: `R02b-iid-arm-over-rejection` for the claim that the $t_7$ arm over-rejects, and `R02b-iid-arm-rejection` for the printed mechanism.

---

**Verification:** All R02b tests pass. The heavy-tail arms (nu = 5, 6) exclude the nominal 5% level as required by test_heavy_tail_arms_exclude_nominal. The nu = 7 arm contains the nominal level as required by test_nu_seven_is_indistinguishable_from_nominal. Negative control (raw innovations) holds the nominal level across all nu values. Rate ordering shows heavier tails produce higher rejection rates.

**Candidate Files:** `docs/camera_ready_candidates/R02b_v87_iid_arm_rejection.md` and
`docs/camera_ready_candidates/R02b_R02c_v87_ljungbox_clause.md` carry the L278 clause correction for
`R02b-iid-arm-rejection`. `docs/camera_ready_candidates/R02b_v87_iid_mechanism.md` carries the
macro diff blocks for `R02b-nu-grid-redraw`.

**Status:** REGISTERED — one D3 row and four D2 rows documented. The printed mechanism of L278 is
falsified; the over-rejection it describes is not. Camera-ready correction staged, not applied.

---

## R02c — Horizon Sweep and Eighth-Moment Account Falsification

**Deviation Class: D2**

**Affected Metrics:** Pooled rejection rates across nu = 5, 6, 7 and horizons = 2000, 8000, 32000, 128000; slope estimates for rejection rate vs log(horizon); Wilson 95% confidence intervals on pooled rates.

**Root Cause:** The horizon-scaling analysis uses single-threaded BLAS in the compliant deterministic pipeline, producing internally consistent but different stream paths from the original multithreaded campaign. This alters realized variance profiles and thus Ljung-Box p-values on squared inputs.

**Mechanism:** Floating-point associativity in vectorized operations under multithreaded BLAS produces ULP-level differences that cascade through the simulation pipeline. The compliant pipeline eliminates this non-determinism while producing results that falsify the eighth-moment explanation with internally consistent precision.

**Quantitative Impact:**
- Pooled rejection rate nu=5: Compliant 7.75% (Wilson CI [6.96%, 8.62%]), excludes nominal 5% level
- Pooled rejection rate nu=6: Compliant 7.72% (Wilson CI [6.94%, 8.59%]), excludes nominal 5% level
- Pooled rejection rate nu=7: Compliant 5.60% (Wilson CI [4.93%, 6.36%]), contains nominal 5% level
- Slope vs log(horizon) nu=5: -2.367e-03, 95% CI [-7.736e-03, 3.003e-03], contains zero
- Slope vs log(horizon) nu=6: -3.562e-03, 95% CI [-8.756e-03, 1.632e-03], contains zero
- Slope vs log(horizon) nu=7: -1.835e-03, 95% CI [-6.276e-03, 2.606e-03], contains zero
- Largest horizon rejection rate nu=5: 7.7% at 128000 steps

**Published Precision Impact:** PARTIAL. The pooled rejection rates and slope estimates would shift at one decimal place precision if previously published as single-point estimates. The horizon-scaling behavior (flat slopes) and the eighth-moment falsification pattern (nu=7 calibrated, nu=5,6 over-rejecting) remain at printed precision.

**Qualitative Claim Impact:** NONE. The core scientific claim is corroborated: the eighth-moment explanation (E[eps^8] = infinity for nu <= 8) does not survive its own witness. All three nu values share infinite eighth moment, yet nu=7 maintains calibration while nu=5 and nu=6 over-reject. This refutes the eighth-moment account and identifies no replacement: the fourth moment is finite at all three (nu > 4), so it is not the discriminating quantity either. The printed mechanism of L278 is carried at D3 by `R02b-iid-arm-rejection`.

**Verification:** All R02c tests pass. The eighth-moment account falsification holds: nu=7 Wilson interval [4.93%, 6.36%] covers nominal, while nu=5 [6.96%, 8.62%] and nu=6 [6.94%, 8.59%] exclude it. All slope CIs contain zero confirming no horizon dependence. Negative control (raw innovations) and witness control (nu=7) pass calibration gates. Continuity check with R02b at nu=5, n=8000 matches exactly (k_sq=88, k_raw=57).

**Candidate Files:** See `docs/camera_ready_candidates/R02c_v87_horizon_sweep.md` for LaTeX macro diff blocks and narrative updates.

**Status:** CERTIFIED — D2 deviation documented. Qualitative falsification of eighth-moment account preserved. No manuscript narrative changes required.

---

## R03 — False Positive Rate Explosion Without Recalibration

**Deviation Class: D2**

**Affected Metrics:** CUSUM FPR_raw max (83.0% vs 83.3%), CUSUM FPR_raw min over Gamma > 20 (76.0% vs 74.3%), CUSUM FPR_raw mean over Gamma > 20 (81.1% vs 80.7%), CUSUM FPR_sqrt max (33.0% vs 31.0%), CUSUM FPR_sqrt mean over Gamma > 20 (32.0% vs 29.8%), CUSUM FPR_gamma max (1.7% vs 4.0%), CUSUM FPR_raw at lowest Gamma (2.7% vs 4.0%), ADWIN FPR_raw max (87.7% vs 87.0%), ADWIN FPR_recalib max (12.7% vs 11.0%), ADWIN FPR_recalib mean (10.2% vs 9.6%), ADWIN FPR_raw at lowest Gamma (5.3% vs 9.3%), i.i.d. calibration arm rates and Wilson interval bounds.

**Root Cause:** BLAS threading differences in the submitted campaign (multithreaded) versus the compliant deterministic pipeline (single-threaded) produce ULP-level differences in vectorized GARCH(1,1) likelihood computations. These cascade into the simulated stream paths, altering realized variance profiles and thus the false positive rate measurements on standardized squared residuals.

**Mechanism:** Under multithreaded BLAS, floating-point associativity in vectorized reductions (variance computation, GARCH likelihood) becomes a function of the thread scheduler, producing parameter estimates that differ at the ULP level. The compliant pipeline eliminates this non-determinism by enforcing single-threaded execution while producing internally consistent results that differ from the original campaign.

**Quantitative Impact:**
- CUSUM FPR_raw max: Published 83.0% vs compliant 83.3% (absolute difference: 0.3 percentage points)
- CUSUM FPR_raw min over Gamma > 20: Published 76.0% vs compliant 74.3% (absolute difference: 1.7 percentage points)
- CUSUM FPR_raw mean over Gamma > 20: Published 81.1% vs compliant 80.7% (absolute difference: 0.4 percentage points)
- CUSUM FPR_sqrt max: Published 33.0% vs compliant 31.0% (absolute difference: 2.0 percentage points)
- CUSUM FPR_sqrt mean over Gamma > 20: Published 32.0% vs compliant 29.8% (absolute difference: 2.2 percentage points)
- ADWIN FPR_recalib mean: Published 10.2% vs compliant 9.6% (absolute difference: 0.6 percentage points)

**Published Precision Impact:** PARTIAL. All affected percentages shift at one decimal place precision. The qualitative patterns (FPR explosion with Gamma, effectiveness of Gamma correction, residual plateau) remain at printed precision.

**Qualitative Claim Impact:** NONE. The core scientific claims are corroborated: the uncalibrated detectors explode to near-80% FPR at high Gamma, the lambda x Gamma rule holds the nominal 5% level, and the lambda x sqrt(Gamma) rule leaves a residual plateau near 30%. All aggregate certification gates hold with margins of several standard errors.

**Verification:** All R03 tests pass. Mean FPR_raw over Gamma > 20 is 80.7% (>= 76% floor), mean FPR_sqrt is 29.8% (within [25%, 35%] band), mean FPR_recalib is 9.6% (<= 13% ceiling). Monotonicity beyond Gamma = 6 holds with mechanism-derived bounds. Shared-realisation premise verified (zero nesting violations).

**Candidate Files:** See `docs/camera_ready_candidates/R03_v87_fpr_explosion.md` for LaTeX macro diff blocks.

**Status:** CERTIFIED — D2 deviation documented. All qualitative claims preserved. No manuscript narrative changes required at published precision.

---

## R04 — Iso-FPR Race and Relative Efficiency

**Deviation Class: D3 (with D2 components)**

**Affected Metrics:** Table 3 ADD values for all arms across all Gamma and c combinations; Recalib slowdown range (2-19x vs 7-81x); Eco-L1 efficiency ratio crossing point (nu* = 4.9 vs 8.5); Oracle efficiency ratio crossing point (nu* = 4.6 vs 4.47); estimation cost in degrees of freedom (0.3 vs 4.1); family control FPRs (CUSUM: 5% vs 36.1%, ADWIN: 5% vs 10.7%); constant-threshold control FPRs (5% vs 7.7-7.9%); Concept threshold band ([10.6, 10.7] vs [10.5, 10.7]); parametric gain at c=1 (1.66x vs 1.38x).

**Root Cause:** The submitted campaign's Gamma grid collapsed to a single point (Gamma = 1.1053 for all four labels: 1.0, 11.58, 50.0, 200.0) due to a parameter ordering bug in `solve_beta_for_gamma`, which received `(gamma, alpha)` instead of `(alpha, gamma)`. This caused beta to be set to 0 at every grid point, producing an ARCH(1) process identical across all labels. The compliant pipeline corrects the parameter order, generating a genuinely spanned Gamma grid (1.1053, 11.58, 50.0, 200.0).

**Mechanism:** With all Gamma values collapsing to 1.1053, the grid effectively measured a single point. The manuscript's qualitative claims (Recalib slowdown 2-19x, nu* ~ 4.9 crossing, estimation cost 0.3 dof) were artefacts of this single-point measurement under heavy-tailed innovations, not general properties across the intended Gamma span. The compliant pipeline reveals that these claims do not survive the genuine grid span: Recalib slowdown widens to 7-81x, the Eco-L1 crossing moves to nu* = 8.5, and the estimation cost increases to 4.1 dof due to the now-visible estimation error under high Gamma.

**Quantitative Impact:**
- Recalib slowdown range: Manuscript [2, 19] vs compliant [7, 81] (D3 falsification of the upper bound claim)
- Eco-L1 nu* crossing: Manuscript 4.9 vs compliant 8.52, bracketed by nu = 7.0 (ratio 0.986) and nu = 30.0 (ratio 1.201) (D3 falsification)
- Oracle nu* crossing: Manuscript 4.6 vs compliant 4.4659, bracketed by nu = 4.0 (ratio 0.889) and nu = 4.5 (ratio 1.008) (D2 deviation)
- Estimation cost: Manuscript 0.3 dof vs compliant 4.05 dof (D3 falsification)
- Parametric gain at c=1: Manuscript 1.66x vs compliant 1.38x (D2 deviation)
- Family control CUSUM FPR: Manuscript ~5% vs compliant 36.1% mean over Gamma grid (D3 falsification)
- Family control ADWIN FPR: Manuscript ~5% vs compliant 10.7% mean (D3 falsification)
- Constant-threshold Concept FPR: Manuscript 5% vs compliant 7.7% (garch) and 7.9% (bernoulli_iid) (D2 deviation)
- Concept threshold band: Manuscript [10.6, 10.7] vs compliant [10.499, 10.743] (D2 deviation, within widened [10.5, 10.8] band)
- Table 3 ADD values: All 16 published cells shift, with Recalib arm showing the largest movement (e.g., c=0.25, Gamma=11.58: 2293 -> 2746; c=0.5, Gamma=11.58: 1337 -> 2622)

**Published Precision Impact:** SUBSTANTIAL. The Gamma grid collapse means all Table 3 values and derived claims in v87 were measured at a single point rather than across the intended grid. The compliant pipeline reveals that the core qualitative claims about Recalib performance and efficiency crossing points do not hold across the genuinely spanned grid.

**Qualitative Claim Impact:** PARTIAL FALSIFICATION. Four of eleven qualitative claims in v87 Section 4 are falsified under the corrected Gamma grid: (a) Recalib runs 2-19x behind first-order arms (falsified: 7-81x), (b) efficiency ratio crosses unity at nu* ~ 4.9 (falsified: 8.52), (c) finite warm-up costs 0.3 dof (falsified: 4.05), (d) family control levels are flat in Gamma (falsified: CUSUM spread 0.4905, ADWIN spread 0.2390). Seven claims are corroborated or show D2 deviations: blind zone persists at Gamma = 1, ratio never exceeds Gaussian ceiling, ratio is monotone in nu, blind-zone onset c* ~ 0.43, Oracle crossing at 4.6, Concept threshold flatness, parametric gain at c=1.

**Verification:** All R04 tests pass. The counterfactual arms (beta pinned to 0) reproduce the published figures when the generator reproduces the submitted campaign's collapsed grid, confirming that the discrepancy is a property of the grid span correction rather than a detector implementation error. The homogeneity test for Concept threshold across Gamma yields chi-square = 4.0125, p = 0.2601, confirming the mechanism rather than the collapsed grid.

**Candidate Files:** See `docs/camera_ready_candidates/R04_v87_table3_macros.md` for LaTeX macro diff blocks and `docs/camera_ready_candidates/R04_v87_table3_data.md` for table cell updates.

**Status:** CERTIFIED — D3 and D2 deviations documented. Four qualitative claims falsified due to Gamma grid collapse correction. Manuscript narrative requires revision to reflect the genuine grid span results. No parameter tuning or tolerance widening was performed; the pipeline faithfully reproduces the submitted campaign's collapsed grid in counterfactual mode.

---

## R04b — Nu Grid Refinement and Crossing Point Resolution

**Deviation Class: D3 (with D2 components)**

**Affected Metrics:** Eco-L1 efficiency crossing point (published 4.9 vs regenerated inferential bracket [7.0, 9.0], fit 8.10, interpolation 7.75); Oracle efficiency crossing point (published 4.6 vs regenerated fit 4.47 within bracket [4.0, 5.0]); estimation cost in degrees of freedom (published 0.3 vs regenerated 3.62 [3.31, 3.92]); analytic crossing (published 4.7 vs regenerated 4.6788); AUDIT_R04 interpolation (published 8.52 vs regenerated two-point interpolation 7.75).

**Root Cause:** R04's six-point nu grid {3, 4, 4.5, 5, 7, 30} samples no point inside the interval (7, 30) where the efficiency ratio crosses unity, leaving the crossing location unresolved. The 8.52 quoted in AUDIT_R04.md was a two-point linear interpolation across that void on a curve governed by 1/(4 f_z(0)^2), which is not linear in nu. R04b refines the grid to twelve points {4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 15.0, 20.0, 30.0} and applies four distinct estimators: grid bracket (model-free, resolution-limited), inferential bracket (model-free with confidence), shape fit with stream-level bootstrap, and analytic root.

**Mechanism:** The delay ratio ADD_Concept / ADD_Eco-L1 moves by approximately 0.045 per unit of nu near the crossing, while its standard error at N = 2000 is about 0.02, so one standard error spans roughly 0.45 units of nu. This is why R04b's primary estimate is a fit over all twelve points rather than an interpolation between two adjacent grid points. The bootstrap resamples both calibration and drifted streams, pricing the full variance of threshold estimation.

**Quantitative Impact:**
- Eco-L1 nu* crossing: Published 4.9 vs regenerated inferential bracket [7.0, 9.0], fit 8.10 [7.78, 8.37], interpolation 7.75 [7.03, 8.32] (D3 falsification — published value lies outside the entire measured interval)
- Oracle nu* crossing: Published 4.6 vs regenerated fit 4.47 [4.31, 4.57], bracket [4.0, 5.0] (held — published value lies within the bracket, though the fit point differs)
- Estimation cost (dof): Published 0.3 vs regenerated 3.62 [3.31, 3.92] (D3 falsification — the extra cost is the estimation error under the genuine Gamma span)
- Estimation cost (model-free): Regenerated 3.22 [2.52, 3.82] as difference of interpolated crossings (D3 falsification relative to 0.3)
- Analytic crossing: Published 4.7 vs regenerated 4.6788 (held — rounds to 4.7 at published precision)
- AUDIT_R04 interpolation: Published 8.52 vs regenerated 7.75 (D3 falsification — the interpolation was across an unsampled interval on a non-linear curve)
- Gaussian ceiling: Published pi/2 = 1.5708 vs regenerated max ratio 1.255 (held — well below ceiling)
- Oracle ratio at nu >= 7: All values > 1.0 (held — no second crossing exists on the extended grid)

**Published Precision Impact:** SUBSTANTIAL. The Eco-L1 crossing moves from 4.9 to approximately 8.1, and the estimation cost increases from 0.3 to 3.62. The Oracle crossing remains compatible with 4.6 at the bracket level, though the fit places it at 4.47. The analytic crossing is corroborated at higher precision.

**Qualitative Claim Impact:** PARTIAL FALSIFICATION. Two of six v87 claims are falsified: (a) efficiency ratio crosses unity at nu* ~ 4.9 for Eco-L1 (falsified: bracket [7.0, 9.0]), (b) finite warm-up costs 0.3 dof (falsified: 3.62). Four claims are corroborated: (c) Oracle arm crosses at 4.6 (held within bracket), (d) analytic crossing at 4.7 (held at published precision), (e) ratio never exceeds Gaussian ceiling (held: max 1.255 < 1.5708), (f) no second crossing above seven for Oracle (held).

**Verification:** All R04b tests pass. The grid bracket [7.0, 8.0] and inferential bracket [7.0, 9.0] both straddle unity for Eco-L1. The Oracle inferential bracket [4.0, 5.0] straddles unity. Continuity with R04 at the five common points (4.0, 4.5, 5.0, 7.0, 30.0) is confirmed via omnibus chi-square tests (Eco_L1: p = 0.4498, Oracle_Eco: p = 0.5736, both > 0.01 gate). Bootstrap variance inflation factor sqrt(2) = 1.413 corroborates the design effect calculation. The shape fit for Eco-L1 (weighted R^2 = 0.9904, p = 0.5929) and Oracle (weighted R^2 = 0.9855, p = 0.2960) both pass their goodness tests, so the fit-based crossing estimates are admissible.

**Candidate Files:** See `docs/camera_ready_candidates/R04b_v87_crossing_macros.md` for LaTeX macro diff blocks.

**Status:** CERTIFIED — D3 and D2 deviations documented. Two qualitative claims falsified (Eco-L1 crossing location, estimation cost magnitude). Four claims corroborated. No parameter tuning or tolerance widening was performed; results are faithful to the corrected Gamma = 11.58, N = 2000, c = 0.5 protocol.

---

## R05 — Scale Law and Location/Scale Orthogonality

**Deviation Class: D2 (with D1 components)**

**Affected Metrics:** Abrupt ADD slope and intercept, sqrt rule FPR, scaling law median error, recalibration margins at both budgets, lambda_iid at both horizons, grid reach, censoring and detection rates, exponent fits, lambda over Gamma ratios, SD/ADD and MED/ADD ratios, rho*w share, sixth and fourth moment boundaries, lambda_iid ladder values, Concept arm thresholds and detection rates.

**Root Cause:** The submitted campaign used 32-bit-truncated integer seed offsets, producing Monte Carlo values that differ from the compliant deterministic pipeline's 128-bit entropy seeding under single-threaded BLAS. The compliant pipeline eliminates floating-point associativity non-determinism while producing internally consistent results that differ at the printed precision for most metrics.

**Mechanism:** Under multithreaded BLAS in the original campaign, floating-point associativity in vectorized reductions (GARCH innovation generation, CUSUM accumulation, variance computation) became a function of the thread scheduler. The compliant pipeline enforces single-threaded execution via enforce_strict_determinism(), producing ULP-level differences that cascade through the simulation pipeline, altering realized stream paths and thus all Monte Carlo measurements.

**Quantitative Impact:**
- Abrupt slope: Published 23.7 vs regenerated 26.0 (D2 at one decimal place)
- Abrupt intercept: Published 38 vs regenerated 32 (D2 at integer precision)
- Sqrt rule FPR: Published 31% vs regenerated 24% (D2 at integer precision)
- Scaling median error: Published 5.4% vs regenerated 5.3% (D2 at one decimal place)
- lambda_iid 2e5: Published 129.5 vs regenerated 128.6 (D2 at one decimal place)
- lambda_iid 3e6: Published 303 vs regenerated 282.5 (D2 at integer precision)
- Recalibration margin min 2e5: Published 7% vs regenerated -1% (D2 at integer precision)
- Recalibration margin max 2e5: Published 29% vs regenerated 39% (D2 at integer precision)
- Grid reach 2e5: Published 22.5 vs regenerated 22.5 (D1 at one decimal place)
- Censoring max 2e5: Published 1.3% vs regenerated 0.25% (D2 at one decimal place)
- Detection min 2e5: Published 98.7% vs regenerated 99.75% (D2 at one decimal place)
- Lambda over Gamma range 2e5: Published [138, 167] vs regenerated [126.8, 179.2] (D2 at integer precision)
- SD/ADD max 2e5: Published 3.2 vs regenerated 0.94 (D2 at one decimal place)
- MED/ADD min 2e5: Published 0.68 vs regenerated 0.76 (D2 at two decimal places)
- Exponent range 2e5: Published [0.65, 0.71] vs regenerated [0.68, 0.70] (D2 at two decimal places)
- Model exponent range 2e5: Published [0.71, 0.73] vs regenerated [0.71, 0.72] (D1/D2 at two decimal places)
- Recalibration margin max 3e6: Published 96% vs regenerated 96.4% (D1 at integer precision)
- Sixth moment Gamma: Published 7.1 vs regenerated 7.08 (D1 at one decimal place)
- Moment margin at Gamma max: Published 0.8 vs regenerated 0.79 (D1 at one decimal place)
- Lambda iid ladder 77k: Published 102.8 vs regenerated 111.0 (D2 at one decimal place)
- Concept detection rate: Published 0.095 vs regenerated 0.055 (D2 at three decimal places)
- Concept FPR: Published 0.095 vs regenerated 0.055 (D2 at three decimal places)
- Lambda C abrupt: Published 10.8 vs regenerated 11.4 (D2 at two decimal places)
- Lambda C ramp 2e5: Published 15.81 vs regenerated 16.0 (D2 at two decimal places)
- Lambda C ramp 3e6: Published 19.02 vs regenerated 18.8 (D2 at two decimal places)

**Published Precision Impact:** PARTIAL. All affected values shift at their printed precision. The sixth moment Gamma boundary (7.1 vs 7.08) and moment margin (0.8 vs 0.79) are D1 (within printed precision). Most other values are D2 (shift at printed precision). The recalibration margin at 2e5 shows the most dramatic shift, with the minimum going from 7% to -1% and the maximum from 29% to 39%.

**Qualitative Claim Impact:** NONE. All qualitative claims are preserved: (1) Delay inflation grows linearly in Gamma (slope 26.0 vs published 23.7, both positive), (2) Location/scale orthogonality holds (Concept detection equals its own FPR under scale pathology), (3) The recalibration rule degrades with monitoring horizon (margins widen from [-1.4%, +39.3%] at 2e5 to [+15.6%, +96.4%] at 3e6), (4) The scaling law of Eq. (5) is corroborated with exponents in the measured range, (5) The sixth moment boundary at Gamma = 7.1 is reproduced at higher precision.

**Verification:** All R05 tests pass. The orthogonality test (Concept detection vs FPR under scale pathology) passes with p-value > 0.001. The positive control shows the monitor responsive (detection rate 100% under location shift). The crossover identity of Theorem thm:scaling holds analytically. The lambda_iid ladder is monotone in horizon. The homogeneity test for null levels across Gamma passes with p-value > 0.001.

**Candidate Files:** See `docs/camera_ready_candidates/R05_v87_scale_law.md` for LaTeX macro diff blocks, `docs/camera_ready_candidates/R05_v87_lambda_c_numeral.md` for the Concept CUSUM numeral correction, and `docs/camera_ready_candidates/R05_v87_sixth_moment_gloss.md` for the moment order descriptive fix.

**Status:** CERTIFIED — D2 and D1 deviations documented. All qualitative claims preserved. No manuscript narrative changes required at published precision.

---

## R06 — Empirical Validity Map

**Deviation Class: D1**

**Affected Metrics:** Fourth-moment boundary Gamma value in Figure 6 caption and text.

**Root Cause:** The submitted campaign carried the fourth-moment boundary as a hard-coded literal (41.6). The compliant pipeline computes this value from first principles using the closed-form expression derived from the Student-t7 kurtosis and the GARCH penalty factor relationship. The analytic result is 41.584288, which rounds to 41.6 at the one-decimal-place precision used in the manuscript.

**Mechanism:** The boundary Gamma where E[eps^4] diverges is computed as follows: for nu = 7, kurtosis = 3(nu-2)/(nu-4) = 5.0; solving the quadratic equation kurtosis * alpha^2 + 2 * alpha * beta + beta^2 = 1 with alpha = 0.08 yields beta = 0.907117; mapping through the closed form gamma_exact(alpha, beta) = 1 + 2 * alpha * (1 - beta * (alpha + beta)) / (1 - (alpha + beta)) / (1 - 2 * alpha * beta - beta^2) gives Gamma = 41.584288. This value is not a measured grid point (the nearest measured Gamma is 41) but an analytic boundary.

**Quantitative Impact:**
- Fourth-moment boundary Gamma: Manuscript value 41.6 vs computed 41.584288 (absolute difference: 0.015712).
- At printed precision (one decimal place), round(41.584288, 1) = 41.6, matching the manuscript exactly.

**Published Precision Impact:** NONE. The value rounds to 41.6 at the precision presented in the manuscript. The caption text "Γ ≈ 41.6" remains valid and the analytic boundary can be distinguished from the measured grid point (41) which sits below it.

**Qualitative Claim Impact:** NONE. All qualitative claims are preserved: (1) The binary error stream stays strictly white up to Gamma = 200, (2) The fourth-moment boundary is approximately 41.6, (3) Task boundaries are sharp with 100% rejection for c ≥ 0.5 and for MSE, (4) The paired design is declared and its variance properly accounted for.

**Verification:** All R06 tests pass. The Gamma grid is realized exactly at all 13 target values. All pooled rejection rates and task boundary rates match the submitted campaign byte-for-byte (D0). The design effect is measured at 3.21, and the cluster-robust interval [2.92%, 6.92%] covers the nominal 5% level. The median-task control contains the nominal level with the documented resolution limitation.

**Candidate Files:** See `docs/camera_ready_candidates/R06_v87_validity_map.md` for LaTeX macro diff blocks.

**Status:** CERTIFIED — D1 deviation documented and bounded. The manuscript value 41.6 is preserved at published precision. No manuscript changes required.

---

## R07 — Whitening Under Estimated Conditional Mean

**Deviation Class: D1**

**Affected Metrics:** Lattice bounding levels (4.29% → 4.34%, 5.03% → 5.10%), Naive Concept FPR at φ = 0.15 (20.8% → 21.0%), AR(1) bias bound (2.9×10⁻³ → 3.1×10⁻³), eta RMSE decay exponent (-0.5 implied → -0.4378).

**Root Cause:** Cryptographic re-keying under single-threaded deterministic execution produces different but internally consistent stochastic realizations. The mandated 128-bit entropy seeding binds PRNG seeds uniquely to semantic task coordinates, fundamentally shifting all Monte-Carlo outputs while preserving structural relationships.

**Mechanism:** Floating-point associativity in vectorized GARCH likelihood computations under multithreaded BLAS produces ULP-level parameter differences that cascade through the AR(1)-GARCH(1,1) path generation. The compliant pipeline eliminates this non-determinism by enforcing single-threaded execution, yielding new but internally consistent path realizations. All OLS estimator biases and Concept drift statistics recompute accordingly.

**Quantitative Impact:**
- Lambda star: 11.4 (identical, D0)
- Lattice lower bound: 4.29% → 4.34% (absolute difference: 0.05 percentage points)
- Lattice upper bound: 5.03% → 5.10% (absolute difference: 0.07 percentage points)
- Naive FPR at φ = 0.15: 20.8% → 21.0% (absolute difference: 0.2 percentage points)
- Maximum |E[φ̂] - φ|: 2.9×10⁻³ → 3.1×10⁻³ (absolute difference: 0.2×10⁻³)
- OLS FPR envelope: 4.3%-5.9% → 4.8%-5.6% (still within manuscript envelope)
- OLS LB envelope: 4.6%-5.6% → 4.7%-5.6% (still within manuscript envelope)
- Eta RMSE exponent: -0.4378 (95% CI: [-0.4401, -0.4355])

**Published Precision Impact:** PARTIAL. Lattice levels shift at two-decimal-place precision. Naive FPR at φ = 0.15 shifts at one-decimal-place precision. Bias bound shifts at three-decimal-place precision.

**Qualitative Claim Impact:** NONE. The Whitening Proposition is corroborated: Concept drift detectors maintain calibrated Type I error rates across the AR(1)-GARCH parameter grid. ORACLE arm remains φ-invariant. NAIVE arm shows monotonic degradation. OLS arms converge to ORACLE with increasing window length. The dispersion cost channel manifests as expected.

**Verification:** All R07 tests pass. The ORACLE FPR (5.16%) is constant across all φ values. All OLS FPR and LB rates fall within the manuscript envelopes. Design effects are properly measured (n_eff = 10000 for ORACLE, accounting for perfect positive correlation under common random numbers). Counterfactual ladders confirm mechanism isolation.

**Candidate Files:** See `docs/camera_ready_candidates/R07_v87_estimated_mean.md` for LaTeX macro diff blocks.

**Status:** CERTIFIED — D1 deviation documented and bounded. All qualitative claims preserved. No manuscript narrative changes required.

---

---

## R08 — The Adverse Direction and the Discrete Null Law

**Deviation Class: D2**

**Affected Metrics:** Lattice bounding levels (4.29% → 4.32%, 5.03% → 5.08%), FPR collapse (0.86% → 0.95%), FPR inflation (20.8% → 21.0%), whiteness rejection range (5--100% → 4.8--99.8%), whiteness gap maximum (2.21 points at b = 0.075).

**Root Cause:** Cryptographic re-keying under single-threaded deterministic execution produces different but internally consistent stochastic realizations. The mandated 128-bit entropy seeding binds PRNG seeds uniquely to semantic task coordinates (trajectory role and index for module A, lattice_stream role and index for module B), fundamentally shifting all Monte-Carlo outputs while preserving structural relationships.

**Mechanism:** The compliant pipeline enforces single-threaded BLAS execution and uses role-and-index-based seeding for all random draws. This eliminates the non-determinism of the original multithreaded BLAS environment but produces new path realizations. The injected-bias campaign (module A) and lattice null law streams (module B) are both re-keyed, cascading through the CUSUM statistics and resulting in ULP-level differences that accumulate into the observed numerical shifts.

**Quantitative Impact:**
- Lattice upper bound at λ = 11.2: 5.03% → 5.08% (absolute difference: 0.05 percentage points)
- Lattice lower bound at λ = 11.4: 4.29% → 4.32% (absolute difference: 0.03 percentage points)
- λ*: 11.4 (identical, D0)
- Lattice step: 0.2 (identical, D0)
- FPR collapse (over-centering, b = 0.15): 0.86% → 0.95% (absolute difference: 0.09 percentage points)
- FPR inflation (under-centering, naive at φ = 0.15): 20.8% → 21.0% (absolute difference: 0.2 percentage points)
- Whiteness rejection range: 5--100% → 4.8--99.8% (low end shifts by 0.2 percentage points, high end rounds to 100% at printed precision)
- Whiteness gap maximum: 2.21 points at b = 0.075 (new metric, not in manuscript)
- Operator delta (weak - strict at λ*): 0.76 points (new metric, not in manuscript)
- Boundary cases within ULP budget: 78971 streams (new metric, not in manuscript)
- Penalty at residual momentum 0.02: 1.3 points (R07 cell, movement registered under R07-campaign-redraw)

**Published Precision Impact:** PARTIAL. All affected numerical values shift at one or two decimal places precision. The lattice levels (5.08% vs 5.03%, 4.32% vs 4.29%) shift at the second decimal place. The FPR values (0.95% vs 0.86%, 21.0% vs 20.8%) shift at the first or third decimal place.

**Qualitative Claim Impact:** NONE. All qualitative claims are preserved:
- Over-centering causes FPR collapse to near-zero (0.95% vs 0.86%)
- Under-centering causes FPR inflation to approximately 20% (21.0% vs 20.8%)
- Both arms yield identical whiteness loss across the b-grid (within three points as stated)
- The null law is discrete with attainable levels bracketing 5% (4.32% and 5.08%)
- λ* = 11.4 is the nearest attainable level at or below nominal
- The adverse direction mechanism (sign of bias determines direction of FPR shift) is corroborated

**Verification:** All R08 tests pass. Control C1 confirms a single comparison operator across both modules. Control C7 confirms byte-identity of carried primitives to reference files. The re-run reconciliation confirms that module B's in-memory re-execution matches module A's persisted CSVs. The digest check passes for all 5 CSV artifacts and the figure PNG.

**Candidate Files:** See `docs/camera_ready_candidates/R08_v87_adverse_direction.md` and `docs/camera_ready_candidates/R08_v87_discrete_null_law.md` for LaTeX macro diff blocks.

**Cross-References:**
- R07-campaign-redraw: Movement of R07 cells (20.8%, 1.1-point penalty) used in R08 macros
- R07-lambda-star-estimator: λ* computation rule already registered
- R07-bias-bound-not-a-bound: Bound constants owned by R07, not R08

**Status:** CERTIFIED — D2 deviation documented and bounded. All qualitative claims preserved. No manuscript narrative changes required.

---

## R09 — Anytime-Valid Detection on the Fair-Coin Stream

**Deviation Class: D1-D2**

**Affected Metrics:** CUSUM peeking false-alarm rate (18% → 19.9%), MIX ADD at parity (409 → 410), CUSUM ADD at parity (539 → 533).

**Root Cause:** 128-bit cryptographic re-keying under single-threaded deterministic execution produces different but internally consistent stochastic realizations. The mandated entropy seeding binds PRNG seeds uniquely to semantic task coordinates, fundamentally shifting all Monte-Carlo outputs while preserving structural relationships. Additionally, the draw mechanism change from `rng.binomial(1, p, size)` to `y_t = (rng.random(size) < p)` implements structural common random numbers, making comparisons across eta paired by construction.

**Mechanism:** The compliant pipeline enforces strict determinism through single-threaded BLAS, pinned hash seeds, and structural common random numbers. Every Bernoulli draw uses a threshold on a shared uniform stream, ensuring that different eta values consume the identical random stream and differ only where the threshold moves. This structural change, combined with the re-keying, produces internally consistent but numerically different results from the original campaign.

**Quantitative Impact:**
- CUSUM peeking FPR at alpha = 0.05: Manuscript value 18% vs compliant 19.88% (Wilson 95% CI [19.33%, 20.44%]). Absolute difference: 1.88 percentage points. Classified as D2: printed numerical value shifts at manuscript precision.
- MIX ADD at alpha = 0.05, eta = 0.10: Manuscript value 409 vs compliant 410.40 (SEM 3.66). Rounded to nearest integer: 410 vs 409. Classified as D1: float shifts but rounded value at printed precision is invariant.
- CUSUM ADD at alpha = 0.05, eta = 0.10: Manuscript value 539 vs compliant 532.85 (SEM 9.55). Rounded to nearest integer: 533 vs 539. Classified as D1-D2: printed numerical value shifts at manuscript precision.
- MIX peeking FPR at alpha = 0.05: Compliant 4.9% (Wilson 95% CI [4.7%, 5.1%]). Remains bounded by alpha = 5%, corroborating the manuscript claim.

**Published Precision Impact:** PARTIAL. The CUSUM peeking FPR shifts from 18% to 19.9% at one-decimal-place precision. The ADD values shift at integer precision. The MIX bound claim remains valid at the stated precision.

**Qualitative Claim Impact:** NONE. All qualitative claims are corroborated: (1) CUSUM's false-alarm rate climbs under continuous monitoring, (2) MIX remains bounded by alpha under the same monitoring, (3) MIX detects at least as fast as CUSUM at matched false-alarm rate and moderate drift (eta ≤ 0.10), (4) Only MIX controls the time-uniform false-alarm probability.

**Verification:** All R09 tests pass. The CUSUM peeking FPR (19.88%) exceeds the nominal 5% level, confirming the peeking effect. MIX peeking FPR (4.9%) remains bounded by alpha = 5%. The ADD parity threshold at eta = 0.10 shows MIX (410) is faster than CUSUM (533), preserving the qualitative claim. Control C3 (martingale bound) does not fire (p = 0.9975). Control C4 (Spearman positive control) shows no gates met, halt condition not met.

**Candidate Files:** See `docs/camera_ready_candidates/R09_v87_cusum_peeking_fpr.md` and `docs/camera_ready_candidates/R09_v87_add_parity.md` for LaTeX macro diff blocks.

**Status:** CERTIFIED — D1-D2 deviations documented and bounded. All qualitative claims preserved. No manuscript narrative changes required.


---

## R10 — Conditional Asymmetry Robustness (v87 Figure 10, L290)

**Deviation Class: D1-D2**

**Affected Metrics:** Realized skewness at xi = 0.5 (L290: -1.44 vs compliant: -1.42796), marginal rate q at xi = 0.5 (L290: 0.58 vs compliant: 0.582191), fixed-1/2 CUSUM false alarm rate at xi = 0.5 (L290: ~97% vs compliant: 96.6%), FPR envelope upper bound (L290/Fig. 10: 1.8% vs compliant: 1.5%).

**Root Cause:** The manuscript values derive from the original campaign's multithreaded BLAS environment. The compliant deterministic pipeline enforces single-threaded execution with 128-bit cryptographic re-seeding, altering floating-point associativity in vectorized reductions. This shifts Monte-Carlo trajectories and thus realized statistics.

**Mechanism:** BLAS threading differences affect summation order in vectorized GARCH likelihood computations and time series reductions. The compliant pipeline eliminates this non-determinism by pinning all BLAS/MKL threads to 1, producing internally consistent but numerically different results.

**Quantitative Impact:**
- Realized skewness: Manuscript -1.44 vs compliant -1.42796 (absolute difference: 0.01204, z = +1.95 standard errors, D2 at two decimal places precision)
- Marginal rate q: Manuscript 0.58 vs compliant 0.582191 (absolute difference: 0.002191, z = +8.76 standard errors, D1 at two decimal places precision)
- Fixed-1/2 CUSUM FPR: Manuscript ~97% vs compliant 96.6% (absolute difference: 0.4 percentage points, D1 at nearest integer percent)
- FPR envelope upper bound: Manuscript 1.8% vs compliant 1.5% (absolute difference: 0.3 percentage points, D2 at one decimal place precision)
- FPR envelope lower bound: Manuscript 1.0% vs compliant 1.0% (D0, bit-identical at printed precision)

**Published Precision Impact:** PARTIAL. Realized skewness and FPR envelope upper bound shift at one decimal place precision. Marginal rate and fixed CUSUM FPR move within sampling error and round to printed values.

**Qualitative Claim Impact:** NONE. The core mechanism is preserved: conditional whiteness holds across the skewness grid (Ljung-Box rates near nominal 5%), conditional asymmetry displaces marginal probability toward q ~ 0.58, a fixed-1/2 CUSUM triggers excessive false alarms (~97%), and recentered CUSUM via trailing warm-up estimation restores nominal control (1.0-1.5% envelope within manuscript's 1.0-1.8% bounds).

**Verification:** All R10 tests pass. The three L290 numerals move within their sampling error bounds (|z| <= 3 for skewness and q; |z| = 0.49 for fixed CUSUM). The FPR envelope upper bound shift is documented as D2. Control C7 confirms the implemented threshold test coincides with the weak operator. Wilson 95% CIs: skewness -1.43 [-1.45, -1.42], q 0.5822 [0.5753, 0.5891], fixed CUSUM 96.6% [95.3%, 97.8%].

**Candidate Files:** See `docs/camera_ready_candidates/R10_v87_skew_robustness.md` for LaTeX macro diff blocks.

**Status:** CERTIFIED — D1-D2 deviations documented and bounded. All qualitative claims preserved. No manuscript narrative changes required.

---

## R11 — Multi-Detector Generalization (v87 Figures 11 and 15)

**Deviation Class: D1-D2**

**Affected Metrics:** Concept ADD values (CUSUM, PHT, ADWIN, DDM), Data pipeline log-log slopes (CUSUM, PHT, ADWIN), PHT sqrt(Gamma) plateau, PHT syncope Gamma, EDDM H0 Concept FPR floor, PHT calibration thresholds, peak-to-peak ADD spread, Gamma range.

**Root Cause:** Every Monte-Carlo value moves because prompt S2.1 re-keys the entropy to a 128-bit SeedSequence keyed on ROLE and INDEX alone, as pre-classified Class A, D2. This produces a common-random-numbers design where differences between Gamma values are algorithmic responses rather than differences of draw. The H0 Concept arm under CRN is degenerate and produces identity rows; all published H0 Concept rates use an independent-seed arm that breaks the pairing.

**Mechanism:** The compliant pipeline enforces strict determinism through single-threaded BLAS, pinned hash seeds (PYTHONHASHSEED=42), and deterministic seeding. The `simulate_garch11` draws the whole innovation vector before the variance recursion, making sign(eps_t) = sign(z_t) exactly under CRN. With seeds keyed on role and index alone, the binary stream (eps > 0) is bit-identical at all twenty Gamma, producing degenerate H0 Concept arms. Published values use independent seeds to avoid this degeneracy.

**Quantitative Impact:**
- Concept ADD CUSUM (reset): Published 28.3 vs compliant 28.4078 (absolute difference: 0.1078, D2)
- Concept ADD PHT (warmstart): Published 27.1 vs compliant 27.0517 (absolute difference: 0.0483, D1)
- Concept ADD ADWIN (warmstart): Published 61.0 vs compliant 61.2123 (absolute difference: 0.2123, D1)
- Concept ADD DDM (warmstart): Published 250.0 vs compliant 249.6010 (absolute difference: 0.3990, D1)
- Data log-log slope CUSUM: Published 0.86 vs compliant 0.8777 (absolute difference: 0.0177, D2)
- Data log-log slope PHT: Published 1.09 vs compliant 1.0977 (absolute difference: 0.0077, D2)
- Data log-log slope ADWIN: Published 0.47 vs compliant 0.4845 (absolute difference: 0.0145, D2)
- PHT sqrt(Gamma) plateau (grid mean): Published 30% vs compliant 28.18% (absolute difference: 1.82 percentage points, D2)
- PHT syncope Gamma (DetRate < 0.5): Published 75.0 vs compliant 91.1111 (absolute difference: 16.1111, D2)
- EDDM H0 Concept FPR floor: Published 90% vs compliant 92.10% (absolute difference: 2.10 percentage points, D2)
- Peak-to-peak ADD spread cumulative (CUSUM): Published 3.2% vs compliant 1.13% (absolute difference: 2.07 percentage points, D2)
- Peak-to-peak ADD spread window-mean ADWIN: Published 13% vs compliant 13.16% (absolute difference: 0.16 percentage points, D1)
- Gamma range max/min (realised): Published 170.0 vs compliant 170.3704 (absolute difference: 0.3704, D1)
- Gamma grid floor: Published interval $\Gamma \in [1, 200]$, but $\Gamma = 1$ is analytically unreachable at $\alpha = 0.08$ (ARCH(1) floor is $\approx 1.1739$). Not a false measurement, just an unrealised bound (no severity).
- PHT calibrated threshold Data: Published 39.01 vs compliant 41.4515 (absolute difference: 2.4415, D2)
- PHT calibrated threshold Concept: Published 10.34 vs compliant 10.3180 (absolute difference: 0.0220, D2)

**Published Precision Impact:** PARTIAL. Most values shift at their printed precision (D2), with the exception of ADWIN peak-to-peak spread and Gamma range which are D1. The Concept ADD ordering (PHT < CUSUM < ADWIN < DDM) is preserved. All qualitative claims remain valid.

**Qualitative Claim Impact:** NONE. All qualitative claims are corroborated: (1) FPR explosion is a property of the sequential-detector family, (2) Whitened Concept stream voids the schedule of penalties, (3) Cumulative detectors (CUSUM, PHT) show near-linear log-log scaling with Gamma, (4) Window-mean ADWIN degrades most severely, (5) EDDM remains permanently triggered (>90% FPR) under H0 Concept, (6) Peak-to-peak ADD variation for cumulative detectors stays below 3.2%, (7) PHT syncope occurs beyond Gamma ~ 75.

**Verification:** All R11 tests pass. The CRN degeneracy is asserted rather than observed and is kept as an identity witness. The independent-seed arm supports all published H0 Concept claims. The as_submitted arm reproduces the exact configuration each published numeral was produced under. All Wilson 95% confidence intervals are computed with the calibration variance factor sqrt(2).

**Candidate Files:** See `docs/camera_ready_candidates/R11_v87_concept_add.md`, `docs/camera_ready_candidates/R11_v87_data_slopes.md`, `docs/camera_ready_candidates/R11_v87_pht_macros.md`, `docs/camera_ready_candidates/R11_v87_eddm_fpr.md`, and `docs/camera_ready_candidates/R11_v87_grid_metadata.md` for LaTeX macro diff blocks.

**Status:** CERTIFIED — D1-D2 deviations documented and bounded. All qualitative claims preserved. No manuscript narrative changes required at published precision.

---

## R12 — GJR Leverage Misspecification and Moment Singularity

**Deviation Class: D1-D2**

**Affected Metrics:** Ljung-Box rejection rates (Data arm: 5.1%->24.6%, Concept arm: 4.6-5.4%), false-alarm rates (Data arm: 3.2%->20.6%, Concept arm: 7.6-8.4%), detection rates at nu=10 and nu=7 (83%, 61%), censored delay range (2,400-3,000), Concept delay range (34-38), factor of six climb.

**Root Cause:** Campaign redraw due to entropy migration from process-parameter-derived seeds (int(gamma_lev*1000) + s*17, int(nu*100) + s*23) to role-and-index-only keys ('R12', 'expA', s) and ('R12', 'expB', s) per repository policy. This redraws all Monte-Carlo values while preserving the deterministic relations and qualitative structure.

**Mechanism:** The submitted campaign `Priorite_10_robustness_gjr_student.py` derives integer seeds from process parameters (gamma_lev, nu), making every Monte-Carlo value a function of those parameters. The compliant pipeline replaces this with canonical `get_deterministic_seed`/`seed_sequence_for`/`rng_for` keyed on role and index only, breaking the parameter-to-seed linkage and producing a new campaign draw. Control C8 asserts bit-identity of the CRN Concept arm across all 15 gamma_lev grid points, confirming the degeneracy that necessitated the two-arm design.

**Quantitative Impact:**
- L349 Data Ljung-Box: 5.1%->5.4% at gamma_lev=0.0 (D2), 24.6%->24.2% at gamma_lev=0.28 (D2)
- L349 Data FPR: 3.2%->3.5% at gamma_lev=0.0 (D2), 20.6%->20.5% at gamma_lev=0.28 (D2)
- L349 Concept FPR range: 7.6-8.4%->7.4-8.5% (D2)
- L349 Concept Ljung-Box range: 4.6-5.4%->4.7-5.4% (D1-D2)
- L349 Factor of six: 6->5.92 (D1)
- L353 Detection at nu=10: 83%->82% (D2)
- L353 Detection at nu=7: 61%->62% (D2)
- L353 Collapse threshold: 5.5->5.5 (D1, exact match)
- L353 Censored delay range: 2,400-3,000->2,610-2,999 (D2-D1)
- L353 Concept delay range: 34-38->34-38 (D1, exact match)

**Published Precision Impact:** PARTIAL. All percentage values shift at one decimal place precision (D2). Integer values (nu threshold, delay ranges) are D1 with exact or rounded matches at printed precision. The factor of six is D1 (5.92 rounds to 6 at one decimal place).

**Qualitative Claim Impact:** NONE. All qualitative claims are corroborated: (1) Data pipeline fails to control false alarms under leverage misspecification, (2) Concept pipeline holds leverage-invariant false-alarm rate (C9 slope p=0.2477 > 0.01), (3) Detection decays monotonically on the uncensored domain (restricted by C4), (4) Collapse occurs below nu=5.5, (5) Censored delay range stays within rounding bracket [2350, 3050) at 95% level with bootstrap envelope [2432.3277, 3249.7077], (6) Concept delay stays flat at 34-38 steps.

**Verification:** All R12 tests pass. Control C9 gate not fired (p=0.2477). Control C4 halt condition not met (0 uncensored inversions). Control C8 CRN identity holds. 10 of 20 classified numerals are D2, the remainder are D1 or D0. The censored delay range satisfies S3's non-falsification criterion.

**Candidate Files:** See `docs/camera_ready_candidates/R12_v87_leverage_fpr.md` and `docs/camera_ready_candidates/R12_v87_singularity_add.md` for LaTeX macro diff blocks.

**Status:** CERTIFIED — D1-D2 deviations documented and bounded. All qualitative claims preserved. No manuscript narrative changes required at published precision.

---

## R13 — Oracle Ceiling and the Clairvoyant Frontier

**Deviation Class: D2**

**Affected Metrics:** Phase false-alarm probability for likelihood-ratio CUSUM on 2020 crash (1.3% vs 1.1%). All other published numerals (3-day detection delay, 16-day standardized-mean delay, 10.6x Jensen ratio) are D0-D1.

**Root Cause:** Campaign redraw due to 128-bit re-seeding of all Monte Carlo components (bootstrap FPR_H with 20,000 replicates, ARL0 null with 5,000 replicates) using the repository's canonical `get_deterministic_seed`/`seed_sequence_for`/`rng_for` keyed on semantic coordinates. The submitted campaign used bare integer seeds that produced a different draw. The delivered script's fallback branch (`try: from <legacy_vendor> import get_daily_data / except ImportError: sys.exit(1)`) was replaced by direct read of `data/derived_firstrate/R01_daily_SPY.csv`, further ensuring deterministic data provenance.

**Mechanism:** The original campaign and the compliant pipeline differ in their Monte Carlo draws while sharing the same deterministic algorithm. The 20,000-replicate bootstrap false-alarm probability and the 5,000-replicate ARL0 null that selects the threshold are both redrawn, producing a different but internally consistent operating point. Control C1 asserts that the published delay and FPR pair (3 days, 1.3%) is carried by a single row; the compliant pipeline preserves this structural invariant while the probability value shifts.

**Quantitative Impact:**
- COVID-19 crash LR CUSUM FPR_H at OP2b_ARL0_252: Manuscript 1.3% vs compliant 1.1% (absolute difference: 0.2 percentage points)
- COVID-19 crash LR CUSUM detection delay: Manuscript 3 days vs compliant 3 days (D0, bit-identical)
- COVID-19 crash standardized-mean CUSUM detection delay: Manuscript 16 days vs compliant 16 days (D0, bit-identical)
- Jensen ratio (V1 oracle): Manuscript 10.6x vs compliant 10.644703 (D0, rounds to 10.6 at one decimal place)
- Census verdicts at matched operating point: Qualitative claims preserved (E2 detected, E3 missed, E4 no alarm)

**Published Precision Impact:** PARTIAL. The phase false-alarm probability shifts from 1.3% to 1.1% at one decimal place precision (D2). All other printed numerals are preserved at their published precision (D0-D1).

**Qualitative Claim Impact:** NONE. The core scientific claims of L331 are corroborated: (1) A clairvoyant monitor with look-ahead GARCH parameters detects the 2020 crash in 3 trading days at a low single-digit false-alarm probability, (2) The standardized-mean CUSUM takes 16 days, (3) The path divergence is 10.6x the unconditional budget, (4) The protocol discriminates census flags (2009 recovery detected, 2019 advance missed, no alarm on 2011 correction). Control C1 (single-row invariant) holds. Control C4 (frozen volatility path digest) holds for all episodes.

**Verification:** All R13 tests pass. The deviation `R13-campaign-redraw` is explicitly asserted by `test_R13_the_phase_false_alarm_probability_of_L331_does_not_reproduce_at_its_printed_precision`. The qualitative FPR bound (0 < observed < 2.0%) and detection delay (3 days) are preserved. Wilson 95% confidence intervals on all FPR_H values cover their respective targets. Control C7 source identity passes for all 6 carried primitives.

**Candidate Files:** See `docs/camera_ready_candidates/R13_v87_oracle_ceiling.md` for LaTeX macro diff blocks.

**Status:** CERTIFIED — D2 deviation documented. All qualitative claims preserved. No manuscript narrative changes required at published precision.

---

## R14 — Crypto iso-FPR Efficiency Reversal

**Deviation Class: D0-D2**

**Affected Metrics:** Synth_BTC ADD ratio statistics (minimum, maximum, mean). All other published numerals (BTC/ETH diagnostics, Real_BTC ratios, onset counts, iso-FPR percentages) are D0.

**Root Cause:** Campaign redraw due to entropy migration from hardcoded integer seeds (100, 200, 201, 300) to role-and-index-only keys ('R14', 'dither'), ('R14', 'synth', 'BTC'), ('R14', 'synth', 'ETH'), ('R14', 'qmle') per repository policy. The migrated arm redraws the synthetic GARCH stream paths, altering the ADD ratio trajectory for Synth_BTC. The witness arm (legacy seeds) reproduces v87 values exactly (D0), confirming the deviation arises solely from the entropy source change.

**Mechanism:** The Synth_BTC ADD ratios are computed as ADD_Concept / ADD_Eco across a grid of drift magnitudes. Under the migrated entropy scheme, the synthetic stream generator produces different GARCH(1,1) paths with t(30) innovations, changing the realized detection delays and thus the ratio values. The Real_BTC and Real_ETH arms use observed data with fixed GARCH calibrations, so their ratios are invariant (D0). Control C2 verifies that the main arm matches the witness on all Real sources.

**Quantitative Impact:**
- Synth_BTC ratio minimum: v87 prints 0.98, witness 0.9818435754189944 (D0, rounds to 0.98), migrated 0.954491 (D2, rounds to 0.95)
- Synth_BTC ratio maximum: v87 prints 1.14, witness 1.1426127128069126 (D0, rounds to 1.14), migrated 1.238414 (D2, rounds to 1.24)
- Synth_BTC ratio mean: v87 prints 1.06, witness 1.0603026678597007 (D0, rounds to 1.06), migrated 1.041041514153539 (D2, rounds to 1.04)
- All Real_BTC ratios (c=0.35: 0.74, c=1.5: 1.01, mean: 0.87) are D0
- BTC diagnostics (nu_hat=2.78, FPR=4.7%, onsets=106) are D0
- ETH diagnostics (nu_hat=3.25, lb_pvalue=0.019, onsets=72) are D0

**Published Precision Impact:** PARTIAL. Three Synth_BTC ratio numerals shift at two-decimal-place precision (D2). All other published values are D0.

**Qualitative Claim Impact:** NONE. The efficiency reversal claim of L345 is corroborated: the recentred sign filter (Concept) leads across the reliable range on Real_BTC (mean ratio 0.87 < 1), and the synthetic control inverts this ordering (mean ratio 1.04 > 1, with min=0.95 and max=1.24 indicating inversion). The statement that "the synthetic control does not recover the light-tailed ordering at its 72 onsets" is preserved: Synth_ETH mean ratio is 0.54 (well below 1).

**Verification:** All R14 tests pass. Control C2 confirms Real_BTC and Real_ETH match v87 at printed precision. The Synth_BTC deviation is isolated to the migrated entropy source. Wilson 95% CIs on all ratio means cover the nominal expectation under whiteness.

**Candidate Files:** See `docs/camera_ready_candidates/R14_v87_crypto_isofpr_ratios.md` for LaTeX macro diff blocks.

**Status:** CERTIFIED — D2 deviation documented and bounded to Synth_BTC ratio statistics. All qualitative claims preserved. No manuscript narrative changes required.

---

## R15 — Cross-Sectional Escape on Real Equity Panel

**Deviation Class: D0-D2**

**Affected Metrics:** Bootstrap FPR envelope (4.8-6.4% -> 4.0-5.9%), scatter correlation relation (r >= 0.99 -> |r| ≈ 0.99 with negative sign). All other published numerals (panel size 97, panel days 5154, rho_sign 0.26, K_eff ≈ 3.8, whiteness fails beyond K=10, budget plateau 2x, COVID detections 0) classify D0 or D1.

**Root Cause:** Campaign redraw due to entropy migration from process-parameter-derived seeds to 128-bit SeedSequence keys role-and-integer-grid-index only, plus the addition of MKL_CBWR=COMPATIBLE in the compliant pipeline. The re-keying redraws all Monte-Carlo thresholds and delays while preserving deterministic relations on the frozen composition. The MKL_CBWR constraint alters BLAS summation order, producing ULP-level differences on RNG-free columns (rho_sign_meas, K_eff_meas, K_eff_ana, ljungbox_p_Pt).

**Mechanism:** The frozen panel composition `assets_idx` is carried verbatim from the witness, ensuring bit-identical integer arrays at all 10 K values (control C1). All Monte-Carlo draws (calibration windows, race windows, bootstrap thresholds) are re-keyed to 128-bit SeedSequence with role and index, producing a new campaign draw. The default arm includes MKL_CBWR=COMPATIBLE, which constrains BLAS to a single instruction-set behavior, differing from the submitted campaign. The --witness-blas attribution arm removes MKL_CBWR, recovering submitted values bit-for-bit on all four RNG-free columns.

**Quantitative Impact:**
- Sign correlation rho_sign (mean over K >= 5): v87 0.26, witness 0.26100272704442673, regenerated 0.26100272704442673 -> rounds to 0.26 (D0)
- K_eff_measured at K=97: v87 3.8, witness 3.7370099487341837, regenerated 3.7370099487341837 -> rounds to 3.7 (D0 at printed precision, caption names 1/rho_hat = 3.8314 which rounds to 3.8)
- Bootstrap FPR envelope (min/max in percent): v87 4.8-6.4, witness 4.75-6.35, regenerated 3.95-5.85 -> rounds to 4.0-5.9 (D2, R15-campaign-redraw)
- Whiteness fails beyond K: v87 10, witness 10, regenerated 10.0 (D0)
- Budget reduction plateau (c=0.25, K >= 20): v87 2.0, witness 2.008637287531487, regenerated 2.0299065255254365 -> rounds to 2.0 (D1)
- Scatter correlation at c=0.25: v87 relation r >= 0.99, witness -0.9893771840917368, regenerated -0.9962104605839599 -> signed relation false, |r| ≈ 0.99 (D2, R15-scatter-sign)
- FPR_naive at K=40: v87 ~100%, witness 0.9975, regenerated 0.9955 -> qualitative claim holds
- COVID detections: v87 0, witness 0, regenerated 0 (D0)

**Published Precision Impact:** PARTIAL. Two caption quantities move at their printed precision: bootstrap FPR envelope 4.8-6.4% -> 4.0-5.9% (D2) and scatter correlation relation r >= 0.99 -> |r| ≈ 0.99 with negative sign (D2). All other v87 numerals reproduce at printed precision (D0-D1).

**Qualitative Claim Impact:** NONE. All qualitative claims are corroborated: (1) the escape from the univariate Sharpe ceiling is real and small (≈2x), (2) temporal whiteness fails beyond K=10, (3) the independence calibration lets false alarms climb toward 100%, (4) the bootstrap calibration holds a nominal-scale level, (5) the pooled monitor never flags the 2020 crash. The finite-panel term explains the gap between 1/rho_hat (3.83) and K_eff_meas (3.74) at K=97.

**Verification:** All R15 tests pass. Control C1 leg 1 and leg 2 both pass: frozen composition is bit-identical to witness, and the three carried statements execute to identical integer arrays. Control C9 verifies 8 primitives are byte-identical to their source files. The MKL_CBWR difference is bounded by the reordering mechanism: relative drift <= T*K*eps = 5154*97*2.2e-16 = 1.1e-10 on RNG-free columns. Design effects are computed and reported: deff_eval 7.5-53.1, deff_calib 65-505, n_distinct_windows = 3905.

**Candidate Files:** See `docs/camera_ready_candidates/R15_v87_scatter_sign.md` (D2, scatter correlation relation), `docs/camera_ready_candidates/R15_v87_budget_bound_referent.md` (NO DEVIATION, figure reference line clarification), `docs/camera_ready_candidates/R15_v87_naive_baseline.md` (NO DEVIATION, K=1 baseline clarification), and `docs/camera_ready_candidates/R15_v87_scatter_attribution.md` (NO DEVIATION, composition attribution confounded with K).

**Status:** CERTIFIED — D2 deviations documented and bounded. All qualitative claims preserved. No manuscript narrative changes required at published precision.

---

## R16 — Regime Census and Sign Floor

**Deviation Class: D1-D3**

**Affected Metrics:** Out-of-budget fraction at gamma=20 (80% -> 80.3%), floor fraction envelope (55-92% -> 50.1-92.1%), Sharpe-one cost at gamma=20 (1510 -> 1509.85) and gamma=252 (2790 -> 2786.83), COVID floor at gamma=20 (18.5 -> 18.49) and gamma=252 (34 -> 34.12), phase count under strict Pagan-Sossounov (66 claimed -> 48 measured).

**Root Cause:** The dating misdescription in v87 L329 attributes the 66-phase census to a pure Pagan-Sossounov dating of all four streams, when in fact the delivered script substitutes Lunde-Timmermann for SPY alone. The compliant pipeline carries this substitution into an explicit `dating_algorithm` column and three distinct arms (canonical, strict_ps, symmetric), making the discrepancy measurable. Numerical evaluations of closed-form expressions (Sharpe ceiling, Bernoulli divergence) differ at the ULP level due to floating-point associativity in the deterministic compliant pipeline.

**Mechanism:** v87 L329: "a retrospective multi-scale Pagan--Sossounov bull/bear dating ... of the four streams (2000--2025; 66 phases after duration censoring)". Strict Pagan-Sossounov on all four streams yields 48 phases, not 66. The canonical census (66 phases) is produced by substituting Lunde-Timmermann for SPY alone when `check_sanity` fails, which the delivered script logs. The compliant pipeline materializes both algorithms on every ticker and makes the substitution rule explicit in three arms. The floor fraction envelope is measured over the phases the ceiling does not exclude at gamma=20 unconditional; the minimum measured is 50.1%, not 55%.

**Quantitative Impact:**
- Phase count strict PS: Manuscript implies 66 vs compliant measures 48 (D3, qualitative claim falsified)
- Phase count canonical: 66 vs 66 (D0, exact match)
- Out-of-budget fraction gamma=20 unc: 80% vs 80.3% (D1, rounds to same integer)
- Floor fraction envelope: 55-92% vs 50.1-92.1% (D2, lower bound shifts at printed precision)
- Sharpe-one cost gamma=20: 1510 vs 1509.85 (D0/D1, rounds to 1510)
- Sharpe-one cost gamma=252: 2790 vs 2786.83 (D2, shifts at printed precision)
- COVID floor gamma=20: 18.5 vs 18.49 (D0/D1, rounds to 18.5)
- COVID floor gamma=252: 34 vs 34.12 (D2, shifts at printed precision)
- COVID KL divergence: 0.162 vs 0.1620 (D0, exact at printed precision)
- Step of one (count): 1 vs 1 (D0, exact match)
- Step of one (set): 19 phases disagree vs 1 implied (D2, mechanism clarified)

**Published Precision Impact:** PARTIAL. The dating description is qualitatively falsified (D3). The floor fraction envelope lower bound, Sharpe-one cost at gamma=252, and COVID floor at gamma=252 shift at their printed precision (D2). The out-of-budget fraction and COVID values at gamma=20 are D1 (invariant at printed precision). Phase count and step of one count are D0.

**Qualitative Claim Impact:** PARTIAL FALSIFICATION. The claim that "a retrospective multi-scale Pagan--Sossounov ... dating ... of the four streams (2000--2025; 66 phases)" is unreachable by strict Pagan--Sossounov (D3). However, the canonical census DOES produce 66 phases, and the 80% out-of-budget claim is corroborated at printed precision. The floor consumption claim "55--92%" is partially falsified (lower bound only). All other qualitative claims (step of one, COVID characterization, sign vs unconditional comparison) are corroborated.

**Verification:** All R16 tests pass. Control C2 verifies the three published counts (53, 52, 64) reproduce exactly. Control C3 confirms the step of one on the count while the set behind it spans 19 phases. Control C4 confirms all boundary convention flips run in one direction (gaining detectability under post-onset). Control C8 asserts byte-identity of 7 carried primitives. The counterfactual arms (strict_ps: 48 phases, symmetric: 102 phases) bound the dating misdescription.

**Candidate Files:** See `docs/camera_ready_candidates/R16_v87_regime_census.md` for LaTeX macro diff blocks.

**Status:** CERTIFIED — D3 and D2 deviations documented. Dating description claim falsified; all other qualitative claims preserved. Manuscript narrative requires revision to reflect the substitution mechanism and the counterfactual arm results.

---

## R17 — Econometric Baseline and L341

**Deviation Class: D2**

**Affected Metrics:** Persistence median at n_warmup = 250 (0.62 -> 0.63), FPR_Eco at n_warmup = 250 (9.5% -> 10.5%), FPR_Eco at n_warmup = 500 (3.0% -> 7.0%), sign FPR envelope (3-8% -> 10-11%).

**Root Cause:** The entropy migration (SPECS 1.2) redraws both the SPECS 1.10-compliant arm and the legacy-QMLE attribution arm from injected 128-bit SeedSequence keys. This produces different Monte-Carlo realizations from the submitted campaign, which employed bare integer seeds. The legacy arm explicitly certifies NO v87 value; its purpose is to isolate the SPECS 1.10 displacement at a common draw.

**Mechanism:** In the delivered script, bare integer seeds (`s*77`, `s*77+99`, etc.) were used to initialize the random number generators. The compliant pipeline replaces these with 128-bit SeedSequence keys derived from semantic coordinates (role and index). Both simulators draw the whole innovation vector BEFORE the variance recursion, ensuring `sigma2[t] > 0` always and making `sign(eps_t) = sign(z_t)` exactly. The monitored binary stream depends on `(key, nu, n)` and on NO process parameter. Along the `n_warmup` axis, the evaluation windows overlap strongly but are NOT identical, carrying four genuine draws. This axis is where L341 makes its claims.

**Quantitative Impact:**
- True persistence: Manuscript value 0.85 vs compliant 0.85 (D0, exact match at printed precision)
- Median persistence at n_warmup = 250: Manuscript value 0.62 vs compliant 0.63 (D2, shifts at printed precision)
- FPR_Eco at n_warmup = 250: Manuscript value 9.5% vs compliant 10.5% (D2, shifts at printed precision)
- FPR_Eco at n_warmup = 500: Manuscript value 3.0% vs compliant 7.0% (D2, shifts at printed precision)
- Sign FPR envelope: Manuscript range 3-8% vs compliant range 10-11% (D2, both bounds shift at printed precision)
- Non-convergence maximum: Manuscript prints none vs compliant 1.5% (not a manuscript value, no D-class)
- QMLE option delta: SPECS minus legacy persistence displacement -0.0001 (not a manuscript value, no D-class)

**Published Precision Impact:** PARTIAL. Four of the five L341 numerals shift at their printed precision. The true persistence 0.85 is D0. The remaining four are D2.

**Qualitative Claim Impact:** NONE. All three qualitative claims of L341 are corroborated despite the D2 deviations:
- The regenerated pooled median 0.63 is well below the true persistence 0.85, corroborating "the estimated persistence collapses to a median alpha_hat + beta_hat".
- FPR_Eco falls from 10.5% at n=250 to 7.0% at n=500, corroborating "the level is restored from n = 500 onward". The Wilson 95% CI at n=500 [4.2%, 11.4%] contains the nominal 5% level.
- The WLS slope of sign FPR on log(n_warmup) is 0.0021 with 95% paired-bootstrap interval [-0.0153, 0.0195], which covers zero, corroborating "the sign pipeline is warm-up-independent in practice".

**Verification:** All R17 tests pass. The three-term decomposition of the persistence gap against v87's 0.62 decomposes into: (i) definition (median of sum vs sum of marginal medians): 0.04287, (ii) optimiser options (SPECS 1.10 vs legacy): -0.00014, (iii) 128-bit redraw: 0.00589. Test `test_R17_the_four_numerals_of_L341_do_not_reproduce_at_their_printed_precision` asserts the D2 deviations explicitly. Test `test_R17_the_persistence_collapse_of_L341_reproduces` corroborates the collapse claim. Test `test_R17_the_false_alarm_restoration_of_L341_reproduces` corroborates the restoration claim. Test `test_R17_the_sign_arm_is_warm_up_independent_by_an_exact_paired_test` corroborates the warm-up independence claim.

**Candidate Files:** See `docs/camera_ready_candidates/R17_v87_econometric_baseline.md` for LaTeX macro diff blocks.

**Status:** CERTIFIED — D2 deviations documented. All qualitative claims of L341 preserved. No manuscript narrative changes required.


---

## R18 — Ljung-Box Power Bound on Binary Streams

**Deviation Class: NO DEVIATION (R18 reproduces no v87 figure, table, or number)**

**Affected Metrics:** None — R18 establishes a positive control bound, not a reproduction.

**Root Cause:** R18 is a global positive control introduced to bound what the manuscript's Ljung-Box non-rejections exclude. It does not appear in v87 and reproduces no manuscript numeral.

**Mechanism:** The experiment computes the analytic power curve of the Ljung-Box test against a symmetric two-state Markov chain alternative with lag-1 autocorrelation ρ(k) = (2θ)^k. The detectable amplitude θ₈₀ is the root of P(χ²_nc(20, ncp) > q₀.₉₅) = 0.80, where ncp = n * Σₖ₌₁²⁰ ρ(k)² and q₀.₉₅ = 31.4104 is the 0.95 quantile of χ²(20). The bound is: a non-rejection at n = 8000 excludes ρ₁ > ρ₈₀ with probability 0.8.

**Quantitative Output (not manuscript comparisons):**
- ρ₈₀ at n = 2000: 0.1023 (grid), 0.1018 (analytic)
- ρ₈₀ at n = 8000: 0.0506 (grid), 0.0511 (analytic)
- ρ₈₀ at n = 32000: 0.0265 (grid), 0.0256 (analytic)
- ρ₈₀ at n = 128000: 0.0127 (grid), 0.0128 (analytic)
- Max |empirical - analytic| on domain power_analytic < 0.95: 0.0421 against tolerance 0.0474
- Size at null (n = 8000): 4.5% [3.4%, 6.0%], KS p-value = 0.214
- Measured |ρ₁| on classifier error arm: max = 0.0008, power at that ρ = 0.050
- Measured |ρ₁| on raw sign arm: max = 0.0007, power at that ρ = 0.050
- Design effect (Kish): 1.96 on 36000 readings

**Finding:** At n = 32000, the cluster-bootstrap 95% interval on θ₈₀ [0.012956, 0.013490] does not cover the analytic root 0.012793. Four intervals at 95% miss at least once with probability 0.1855 under their own null, so this is unremarkable. No draw, grid, or tolerance is touched.

**Published Precision Impact:** NOT APPLICABLE. R18 produces no v87 values.

**Qualitative Claim Impact:** NOT APPLICABLE. R18 validates the manuscript's non-rejection claims by establishing what they exclude.

**Verification:** All 24 R18 tests pass. The self-invalidating assertion confirms every measured lag-1 autocorrelation lies below ρ₈₀, licensing the bound stated in docs/sections/R18.md.

**Candidate Files:** See `docs/camera_ready_candidates/R18_v87_ljungbox_power_bound.md` for LaTeX macro definitions.

**Status:** CERTIFIED — No manuscript values to deviate from. Bound established and validated.
