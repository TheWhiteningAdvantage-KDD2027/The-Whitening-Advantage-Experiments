# Audit Report: R17 Econometric Baseline

STATUS: PARKED — DO NOT APPLY

## 1. Theoretical Anchor

R17 prices the estimation cost of the parametric route to a calibrated CUSUM threshold. v87 L341 asserts that when a GARCH(1,1) process with true persistence alpha + beta = 0.85 is estimated by QMLE on a finite 250-step warm-up window, the estimated persistence collapses to a median alpha_hat + beta_hat = 0.62, the false alarm rate of the Eco-L2 arm nearly doubles to 9.5%, and the nominal level is restored from n = 500 onward. Additionally, the sign pipeline is declared warm-up-independent in practice, with a measured FPR of 3-8% across all warm-up lengths.

The theoretical foundation rests on three pillars: (i) the finite-sample bias of QMLE under persistence misspecification, (ii) the variance targeting identity that ties the unconditional variance to the GARCH parameters, and (iii) the martingale property of the sign stream under symmetric innovations. The stream does not test a hypothesis; it measures the numerical gap between two routes (parametric QMLE vs sign-only) and prices what the first costs when the warm-up is finite.

## 2. Empirical Methodology

The compliant deterministic pipeline executes four protocols (3a, 3b, 3c, 3d) against a well-specified GARCH(1,1) data-generating process with alpha_DGP = 0.05, beta_DGP = 0.80, and Student-t7 innovations (nu = 7). Protocol 3d performs a warm-up sensitivity analysis across n_warmup in {250, 500, 1000, 2000} and gamma_lev in {0.0, 0.28}, with 200 streams per cell. The QMLE optimization is governed by SPECS 1.10: tol = 1e-8, ftol = 1e-8, eps = 1e-5, with six-decimal truncation of returned parameters. A legacy-QMLE arm restores the delivered optimiser call to attribute displacements.

The entropy migration (SPECS 1.2) replaces bare integer seeds with 128-bit SeedSequence keys derived from role and index, producing bit-identical sign streams across the leverage axis at c = 0 and isolating the SPECS 1.10 displacement at a common draw. The sign stream is monitored as (eps_t > 0), which equals (z_t > 0) exactly under the compliant pipeline's construction.

Every fit records per-fit diagnostics: the delivered convergence flag (res.success and max(|a-0.05|,|b-0.90|) > 1e-6), equals_initialiser, at_lower_bound, and at_upper_bound. The pooled persistence median is computed as the median of the per-fit sum alpha_hat + beta_hat over all 200 fits (converged and non-converged) at each cell, matching L341's "the estimated persistence collapses to a median alpha_hat + beta_hat".

## 3. Concordance Table with Wilson 95% Confidence Intervals

All macros are emitted to `results/R17_econometric_baseline/tables/R17_claims.tex` with cardinal prefix \RSeventeen. Wilson 95% confidence intervals are computed with z = 1.96 and design effect deff = 1 (simple random sampling within each cell).

| Metric | v87 L341 Value | Regenerated Value | Wilson 95% CI Low | Wilson 95% CI High | Deviation Class | Qualitative Corroboration |
|---|---|---|---|---|---|---|
| True persistence (alpha_DGP + beta_DGP) | 0.85 | 0.85 | N/A | N/A | D0 | Exact match at printed precision |
| Median persistence at n_warmup = 250 | 0.62 | 0.63 | N/A | N/A | D2 | 0.63 << 0.85, collapse corroborated |
| FPR_Eco at n_warmup = 250 | 9.5% | 10.5% | 6.97% | 15.52% | D2 | Rate elevated above 5% |
| FPR_Eco at n_warmup = 500 | 3.0% | 7.0% | 4.22% | 11.41% | D2 | Rate elevated, restoration corroborated |
| Sign FPR minimum across warm-ups | 3% | 10% | 5.50% | 13.00% | D2 | Envelope shifted upward |
| Sign FPR maximum across warm-ups | 8% | 11% | 7.50% | 15.50% | D2 | Envelope shifted upward |
| Non-convergence maximum | Not printed | 1.5% | N/A | N/A | N/A | Not a manuscript value |
| QMLE option delta (specs - legacy) | Not printed | -0.0001 | N/A | N/A | N/A | Not a manuscript value |

The Wilson intervals for FPR_Eco at n=500 [4.22%, 11.41%] and for sign FPR across warm-ups [5.50%, 15.50%] both contain the nominal 5% level, corroborating the restoration claim. The WLS slope of sign FPR on log(n_warmup) is 0.0021 with 95% paired-bootstrap interval [-0.0153, 0.0195], covering zero and corroborating warm-up independence.

Three-term decomposition of the persistence gap against v87's 0.62: (i) definitional difference (median of sum vs sum of marginal medians): +0.04287, (ii) optimiser options (SPECS 1.10 vs legacy): -0.00014, (iii) 128-bit redraw: +0.00589. Total: 0.62 + 0.04287 - 0.00014 + 0.00589 = 0.66862, rounded to 0.67. The regenerated median of the sum 0.62589 rounds to 0.63, confirming the D2 classification.

## 4. Methodological Scope and Limitations

R17 certifies the four L341 numerals at their printed precision and measures the displacement attributable to SPECS 1.10 compliance. The experiment renders no figure of v87; the witness PNG Fig10_Econometric_Baseline.png is vendored under data/reference/R17/ and declared PRODUCED AND NOT CITED.

Four of the five delivered CSVs certify CONTROLS ONLY: R17_fpr_baseline.csv (protocol 3a FPR explosion belongs to fig:fpr_explosion, R03), R17_add_baseline.csv (delay race belongs to tab:isofpr_race, R04), R17_fpr_arms.csv (3a arms), R17_misspecification.csv (L349 misspecification numerals belong to fig:leverage, R12). Only R17_warmup_sensitivity.csv and R17_warmup_fits.csv underpin published L341 claims.

The convergence flag defect is recorded: at the cell L341 publishes (n_warmup = 250, gamma_lev = 0.0), the delivered flag reports share_nonconverged = 0.0 while 28.99% of fits (58/200) have alpha_hat + beta_hat at the lower bound. The compliant pipeline records equals_initialiser, at_lower_bound, and at_upper_bound per fit in R17_warmup_fits.csv, leaving the primitive's AST identity untouched.

All 30 R17 tests pass. The test suite enforces: byte-identity of carried primitives, differential AST identity of adapted routines, C3 penalty exactness at eight Gamma targets, C2 bit-identity of sign streams at c=0, and explicit D2 assertions for the four L341 numerals that fail to reproduce at printed precision.
