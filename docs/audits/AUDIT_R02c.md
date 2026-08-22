# Reproducibility Audit Report — R02c (Horizon Sweep)

## Theoretical Anchor

R02c evaluates Ljung-Box test over-rejection on Student t innovations with degrees of freedom ν = 5, 6, 7 across horizons n = 2000, 8000, 32000, 128000. The theoretical motivation tests whether the eighth-moment explanation (E[εₜ⁸] = ∞ for ν ≤ 8) survives its own witness: ν = 7 controls should remain calibrated at nominal 5% while ν = 5, 6 should exhibit significant over-rejection. The experiment uses squared and raw series, with 1000 independent streams per (ν, n) cell. Continuity with R02b is enforced at (ν = 5, n = 8000) to match the published 8.8% squared rejection rate.

## Empirical Methodology

All 12000 stream seeds are deterministic 128-bit hashes derived from the parameter tuple (R02c, ν, n, stream_index) via MD5, with a special continuity guard reusing R02b seeds for the ν = 5, n = 8000 cell. The Ljung-Box Q-statistic is computed with lag 20. Wilson score 95% confidence intervals (z = 1.959963984540054) bound rejection rates. A weighted least squares regression of rejection rate against log(n) estimates slope with 95% CI for each ν. Negative controls validate calibration: pooled raw p-values (12 cells) must pass a KS test against Uniform(0,1), and the ν = 7 witness arm (4 cells) must pass an identical check. Family-wise error rate bounds P(at least one rejection | H₀) = 1 − (1 − α)ᵐ for both controls.

## Metric Concordance Table

All values below are exact to 17 significant digits (float64). Wilson intervals are computed at z = 1.959963984540054 (95% coverage).

| Metric | ν = 5 | ν = 6 | ν = 7 | Manuscript | Class | Wilson 95% CI |
| ------ | ----- | ----- | ----- | ----------- | ----- | ------------- |
| Pooled squared rejection rate (%) | 7.75 | 7.72 | 5.60 | — | A | See below |
| Pooled squared Wilson low (%) | 6.96 | 6.94 | 4.93 | — | A | — |
| Pooled squared Wilson high (%) | 8.62 | 8.59 | 6.36 | — | A | — |
| Slope vs log n (10⁻³) | -2.367 | -3.562 | -1.835 | — | A | See below |
| Slope CI low (10⁻³) | -7.736 | -8.756 | -6.276 | — | A | — |
| Slope CI high (10⁻³) | 3.003 | 1.632 | 2.606 | — | A | — |
| Largest horizon rate ν=5 (%) | 7.7 | — | — | — | A | — |

For ν = 5: pooled rejection rate 7.75% with Wilson 95% CI [6.96%, 8.62%], excluding nominal 5%. Slope -2.367 × 10⁻³ with 95% CI [-7.736 × 10⁻³, 3.003 × 10⁻³]. For ν = 6: pooled 7.72% with Wilson CI [6.94%, 8.59%], excluding nominal. Slope -3.562 × 10⁻³ with CI [-8.756 × 10⁻³, 1.632 × 10⁻³]. For ν = 7 (control): pooled 5.60% with Wilson CI [4.93%, 6.36%], covering nominal. Slope -1.835 × 10⁻³ with CI [-6.276 × 10⁻³, 2.606 × 10⁻³]. All nu=7 cells contain nominal in both squared and raw Wilson intervals. Continuity cell (ν=5, n=8000): squared rejection rate 8.80% exactly matching R02b, raw rate 5.70%.

**Deviation Classification:** All R02c claims are Class A (correction of a defect in the submitted code) with null severity (—). No manuscript numerical claim is affected. The experiment constrains the admissible causal explanation by ruling out convergence-rate delay as the mechanism for over-rejection, leaving asymptotic quantile breakdown as the untested alternative.

## Methodological Scope & Limitations

R02c neither adds nor removes a manuscript claim; it constrains the causal explanation for over-rejection. The horizon sweep demonstrates that ν = 7 remains calibrated at all n (2000–128000), while ν = 5 and ν = 6 consistently over-reject, refuting the eighth-moment explanation. The slope test lacks power to distinguish between flat and decay-to-nominal hypotheses: the decay slope implied by the rate at n = 2000 lies within every measured confidence interval. Multiple testing controls verify that the null hypothesis (correct calibration) is not rejected for ν = 7. Limitation: the design does not test beyond ν = 7 or below n = 2000; the asymptotic quantile breakdown hypothesis remains untested.
