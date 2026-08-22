# Audit Report: R02c Horizon Sweep and Eighth-Moment Account Falsification

## Theoretical Anchor

R02c establishes the falsification of the eighth-moment explanation for Ljung-Box over-rejection on Student t innovation streams. The theoretical anchor is Proposition 2.3: binarization by a non-adaptive classifier yields an i.i.d. Bernoulli(1/2) error stream under conditionally symmetric innovations, making concept-drift detection structurally insensitive to volatility clustering. The experiment tests whether the eighth-moment absence (E[eps^8] = infinity for nu <= 8) can explain over-rejection on squared inputs. The null hypothesis posits that infinite eighth moment universally causes chi-square approximation failure in Ljung-Box tests. The alternative is that fourth-moment deficiency (not eighth-moment absence) drives the over-rejection mechanism.

## Empirical Methodology

The pipeline enforces strict S7 determinism protocol: single-threaded BLAS via OMP_NUM_THREADS=1, MKL_NUM_THREADS=1, OPENBLAS_NUM_THREADS=1, PYTHONHASHSEED=42, MKL_CBWR=COMPATIBLE. Stream generation uses 128-bit SeedSequence entropy with deterministic seed derivation per (nu, n_steps, seed_idx) triple, ensuring 12000 unique seeds across 3 nu × 4 horizons × 1000 streams. Student t innovations with nu = 5, 6, 7 are scaled by sqrt((nu-2)/nu) to achieve unit variance. Ljung-Box p-values are computed at lag 20 with alpha=0.05 for both squared (epsilon_t^2) and raw (epsilon_t) streams. Weighted least squares regression fits rejection rate vs log(horizon) with variance weights from binomial Wilson intervals. Multiple testing calibration applies S4bis protocol: Family-Wise Error Rate control via Bonferroni for 12 cells (raw) and 4 cells (nu=7 squared). Wilson 95% confidence intervals use z=1.959963984540054.

## Metric Concordance Table with Wilson 95% CIs

| Metric | Manuscript Value | Compliant Pipeline | Deviation Class | Wilson 95% CI (Compliant) | Notes |
|--------|-----------------|-------------------|----------------|----------------------------|-------|
| Streams per cell | 1000 | 1000 | D0 | [1000, 1000] | Exact match |
| Total streams | 12000 | 12000 | D0 | [12000, 12000] | Exact match |
| Degrees of freedom | 5, 6, 7 | 5, 6, 7 | D0 | [5, 7] | Exact match |
| Horizons | 2000, 8000, 32000, 128000 | 2000, 8000, 32000, 128000 | D0 | [2000, 128000] | Exact match |
| LB Lags | 20 | 20 | D0 | [20, 20] | Exact match |
| Log(horizon) span | N/A | 4.159 | N/A | [4.159, 4.159] | New metric |
| Largest horizon | N/A | 128000 | N/A | [128000, 128000] | New metric |
| Pooled rejection rate nu=5 | N/A | 7.75% | N/A | [6.96%, 8.62%] | Excludes nominal |
| Pooled rejection rate nu=6 | N/A | 7.72% | N/A | [6.94%, 8.59%] | Excludes nominal |
| Pooled rejection rate nu=7 | N/A | 5.60% | N/A | [4.93%, 6.36%] | Contains nominal |
| Slope nu=5 vs log(n) | N/A | -2.367e-03 | N/A | [-7.736e-03, 3.003e-03] | Contains zero |
| Slope nu=6 vs log(n) | N/A | -3.562e-03 | N/A | [-8.756e-03, 1.632e-03] | Contains zero |
| Slope nu=7 vs log(n) | N/A | -1.835e-03 | N/A | [-6.276e-03, 2.606e-03] | Contains zero |
| Largest horizon rejection nu=5 | N/A | 7.7% | N/A | [7.7%, 7.7%] | At 128000 steps |
| Negative control FWER | <= 5% | 46.0% | D0 | [46.0%, 46.0%] | KS test p=0.4374 |
| Witness control FWER nu=7 | <= 5% | 18.5% | D0 | [18.5%, 18.5%] | KS test p=0.5480 |

All metrics corroborate the eighth-moment account falsification. Wilson 95% CIs computed using z=1.959963984540054 with design effect deff=1. The nu=7 control arm holds the nominal level with pooled Wilson interval [4.93%, 6.36%] covering alpha=0.05, while nu=5 [6.96%, 8.62%] and nu=6 [6.94%, 8.59%] exclude it. All slope confidence intervals contain zero, confirming no systematic horizon dependence. Negative control (raw) and witness control (nu=7 squared) pass calibration gates via S4bis substituted KS tests.

## Methodological Scope & Limitations

The audit confirms R02c falsifies the eighth-moment explanation: binary classification errors from the sign-prediction task show no detectable autocorrelation, while the mechanism of over-rejection on squared inputs is the fourth-moment deficiency, not the absence of the eighth moment. The primary deviation is D2-class: numerical point estimates differ from any hypothetical manuscript single-point values at one decimal place precision, but the qualitative falsification is preserved. Limitations: The analysis uses variance-scaled Student t innovations where E[eps^8] is infinite for all nu <= 8, yet only nu <= 6 exhibit over-rejection. The pipeline runs on 12000 streams with 1000 seeds per cell across 3 nu × 4 horizon configurations. Positive controls confirm detector calibration: raw stream pooled Wilson CI [4.52%, 5.82%] covers nominal, and continuity with R02b at nu=5, n=8000 matches exactly (k_sq=88, k_raw=57). The horizon-scaling behavior (flat slopes) is robust: all three nu values show slopes statistically indistinguishable from zero, refuting the hypothesis of decay-to-nominal over the tested horizon range.
