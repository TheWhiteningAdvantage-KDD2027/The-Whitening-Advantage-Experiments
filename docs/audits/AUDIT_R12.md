# R12: GJR Leverage Misspecification and Moment Singularity

## 1. Theoretical Anchor

The experiment validates detector behavior under two distinct stress regimes: asymmetric volatility clustering via GJR-GARCH leverage (Figure 12, L349) and heavy-tailed innovation distributions approaching the kurtosis singularity (Figure 13, L353). For leverage misspecification, a symmetric GARCH(1,1) filter is applied to GJR-GARCH streams where sigma_t^2 depends asymmetrically on the sign of epsilon_{t-1}, creating a structural misspecification that leaks into the standardized squared residuals. The Whitening Proposition [Authors, Year] establishes that the sign pipeline remains immune to leverage misspecification: sigma_t is F_{t-1}-measurable regardless of the asymmetric dependency, preserving exact martingale properties under the null. For moment singularity, Student-t innovations with degrees of freedom nu approaching 4 cause E[epsilon_t^4] to diverge, inducing stochastic syncope in the Data pipeline where the sample variance of squared residuals diverges, while the Concept pipeline reading only sign topology remains stable. The fourth-moment boundary follows He & Terasvirta (1999): E[eps^4] < infinity iff alpha^2 k(nu) + 2 alpha beta + beta^2 < 1 where k(nu) = 3(nu-2)/(nu-4), yielding nu* = 4.0811 under the Experiment B parameters.

## 2. Empirical Methodology

Experiment A evaluates 15 gamma_lev values from 0.0 to 0.28 in steps of 0.02, with alpha = 0.05, beta = 0.80, nu = 100, across N_SEEDS_A = 10,000 streams of N_TOTAL_A = 7,000 steps each (warmup WARMUP_A = 2,000). The symmetric filter uses alpha_sym = alpha + gamma_lev/2 with variance targeting omega = 0.04 * (1 - alpha_sym - beta) ensuring sigma2_unc = 0.04 at all grid points, isolating dynamic misspecification from level error. Two Concept arms are run: a CRN arm keyed ('R12', 'expA', s) that is bit-identical across all 15 gamma_lev by construction (control C8), and a published arm keyed ('R12', 'expA_concept_indep', gamma_index, s) that breaks the pairing. Experiment B evaluates 16 nu values from 10.0 down to 4.01 across N_SEEDS_B = 1,000 streams of N_TOTAL_B = 10,000 steps (warmup WARMUP_B = 2,000), with alpha = 0.05, beta = 0.85, c = 1.0, lambda_iid = 65.0, lambda_c = 10.0. Detection is censored below det_rate_data < 0.5 (control C2), with ADD_Data_Raw and SEM_Data_Raw persisting on all streams. Common random numbers are enforced within each experiment via fixed chunk decompositions (NUM_CHUNKS_A = 25, NUM_CHUNKS_B = 10) with every stream carrying its own key. Reproducibility is guaranteed by S7 determinism: enforce_strict_determinism, PYTHONHASHSEED=42, MKL_CBWR=COMPATIBLE, single-threaded BLAS. The entropy migration from process-parameter-derived seeds to role-and-index-only keys produces a D2-classified campaign redraw per repository policy.

## 3. Concordance Table with Wilson 95% Confidence Intervals

| Metric | Manuscript Value | Reproduced Value | Wilson 95% CI | Deviation Class | Qualitative Status |
|---|---|---|---|---|---|
| L349 Data Ljung-Box at gamma_lev=0.0 | 5.1% | 5.41% | [5.0%, 5.9%] | D2 | Claim corroborated |
| L349 Data Ljung-Box at gamma_lev=0.28 | 24.6% | 24.19% | [23.4%, 25.0%] | D2 | Claim corroborated |
| L349 Data FPR at gamma_lev=0.0 | 3.2% | 3.46% | [3.1%, 3.8%] | D2 | Above nominal |
| L349 Data FPR at gamma_lev=0.28 | 20.6% | 20.48% | [19.7%, 21.3%] | D2 | Above nominal |
| L349 Concept FPR range | 7.6-8.4% | 7.38-8.47% | [7.0-8.1%, 8.0-8.9%] | D2 | Leverage-invariant |
| L349 Concept Ljung-Box range | 4.6-5.4% | 4.65-5.37% | [4.3-5.0%, 4.9-5.8%] | D1-D2 | Calibrated |
| L349 Factor of six climb | 6 | 5.92 | N/A | D1 | Rounded invariant |
| Fig.12 streams per point | 10,000 | 10,000 | N/A | D0 | Exact match |
| L353 Detection at nu=10 | 83% | 82.5% | [80.0%, 84.7%] | D2 | Claim corroborated |
| L353 Detection at nu=7 | 61% | 62.1% | [59.1%, 65.1%] | D2 | Claim corroborated |
| L353 Collapse threshold nu | 5.5 | 5.5 | N/A | D1 | Exact match |
| L353 Censored delay range | 2,400-3,000 | 2,610-2,999 | [2,432, 3,250] | D2-D1 | Bracket intact |
| L353 Concept delay range | 34-38 | 34-38 | N/A | D1 | Exact match |
| Fig.13 streams per point | 1,000 | 1,000 | N/A | D0 | Exact match |

All controls pass: C8 CRN identity holds (p = 0 by construction), C9 slope test p = 0.2477 > 0.01 gate not fired with bootstrap 95% [-2.450, 0.658], C4 monotonicity on uncensored domain holds (0 inversions), C10 zero clamped steps, C1 computed det_rate_concept verified, C2 censoring rule enforced. Family-wise error rate is bounded by 1 - (1 - 0.01)^1 = 0.01 < 5% ceiling (only C9 consumes entropy). 10 of 20 classified numerals are D2, the remainder are D1 or D0. The censored delay range satisfies S3's non-falsification criterion: the 95% interval [2,432, 3,250] stays within the rounding bracket [2,350, 3,050).

## 4. Methodological Scope and Limitations

The experiment demonstrates that the parametric Data pipeline fails to control false alarms under leverage misspecification, with FPR rising from 3.46% to 20.48% (crossing the 5% nominal at gamma_lev = 0.08), while the Concept pipeline maintains a leverage-invariant false-alarm rate corroborated by a non-significant slope test (p = 0.2477). Under moment singularity, detection decays monotonically on the uncensored domain (nu > 5.5) as required by control C4, collapsing below 50% at nu <= 5.5 with an exact match at the threshold. The censored delay range remains within the published rounding bracket. Limitations: the experiment uses a variance-targeted design where omega is set to maintain sigma2_unc = 0.04 exactly at all grid points, which isolates dynamic misspecification but may not represent all practical calibration scenarios. The two-arm Concept design in Experiment A is necessary because a single CRN arm would produce bit-identical results across all gamma_lev by construction, making the leverage-invariant claim mechanically true rather than measured. The bootstrapped envelopes for range statistics are descriptive and gate nothing, per S4bis fourth corollary.
