# Audit Report: R02c Horizon Sweep Experiment

This report documents the reproducibility audit and scientific validation of experiment stream R02c, which investigates the persistence of Ljung-Box test over-rejection across increasing sample horizons for Student t innovations with varying degrees of freedom.

---

## 1. Theoretical Anchor

The experiment is anchored in the theoretical framework of martingale difference sequences and the Ljung-Box portmanteau test for serial correlation.

For Student t innovations with nu degrees of freedom, the innovation process epsilon_t exhibits heavy tails with E[epsilon^(2k)] infinite for 2k >= nu. The squared series epsilon_t^2 loses its fourth moment when nu <= 8, which breaks the chi^2 approximation underlying the Ljung-Box test when applied to the squared innovations.

Two competing mechanistic hypotheses are evaluated.

**H1 (Convergence Rate):** Over-rejection is a finite-sample artifact that vanishes as n approaches infinity, driven by the third absolute moment of the autocovariance summand.

**H2 (Asymptotic Quantile Breakdown):** Over-rejection persists asymptotically due to the absence of E[epsilon^8], which invalidates the quantile convergence of the Ljung-Box statistic.

The Berry-Esseen bound for the Ljung-Box statistic requires E|epsilon|^6 < infinity for the test to achieve its nominal level at finite samples. This moment exists only for nu > 6, providing a natural threshold for the transition between calibrated and over-rejecting behavior.

## 2. Empirical Methodology

The experimental design employs a 3 x 4 factorial grid with nu in {5, 6, 7} degrees of freedom and n_steps in {2000, 8000, 32000, 128000} horizon lengths. Each cell contains 1000 independent Monte Carlo streams, yielding 12,000 total simulations.

The Ljung-Box test is applied at lag 20 to both raw and squared innovation series.

Deterministic reproducibility is enforced via single-threaded BLAS/MKL/OMP configuration with OMP_NUM_THREADS=1, MKL_NUM_THREADS=1, OPENBLAS_NUM_THREADS=1, and MKL_CBWR=COMPATIBLE. PYTHONHASHSEED=42 is pinned before interpreter startup. 128-bit hash seeding via SeedSequence is used for each stream coordinate. Pandas multithreading is disabled at import time. Analytic weighted least squares slope estimation avoids FPU non-determinism.

Statistical controls include negative control checking that raw innovation series at nu=7 maintain nominal 5% rejection rate, witness arm verification that nu=7 squared series do not exhibit over-rejection, family-wise error rate control via Kolmogorov-Smirnov test on pooled p-values, and Wilson score 95% confidence intervals for all rejection rate estimates.

A continuity check ensures the nu=5, n=8000 cell reproduces the R02b results (k_sq=88, k_raw=57) to guarantee cross-stream determinism.

## 3. Concordance Table with Wilson Score Intervals and Deviation Classes

The following table presents the primary quantitative findings with their Wilson score 95% confidence intervals and deviation classification against the manuscript frozen v87 text. All values are derived from the generated artifacts in results/R02c_horizon_sweep/data/ and tables/R02c_claims.tex.

| Metric | Value | Wilson 95% CI | Manuscript Reference | Deviation Class | Severity |
| ------ | ----- | -------------- | ------------------- | --------------- | -------- |
| Slope span (log scale) | 4.159 | — | — | — | — |
| Largest horizon | 128000 | — | — | — | — |
| nu=5 slope | -2.367e-03 | [-7.736e-03, 3.003e-03] | Section 4.3 | D0 | — |
| nu=6 slope | -3.562e-03 | [-8.756e-03, 1.632e-03] | Section 4.3 | D0 | — |
| nu=7 slope | -1.835e-03 | [-6.276e-03, 2.606e-03] | Section 4.3 | D0 | — |
| nu=5 pooled rejection (squared) | 7.75% | [6.96%, 8.62%] | Section 4.3 | D0 | — |
| nu=6 pooled rejection (squared) | 7.72% | [6.94%, 8.59%] | Section 4.3 | D0 | — |
| nu=7 pooled rejection (squared) | 5.60% | [4.93%, 6.36%] | Section 4.3 | D0 | — |
| nu=5 largest horizon rejection | 7.7% | [6.2%, 9.5%] | Section 4.3 | D0 | — |

**Classification Summary:** All numerical values match the manuscript at the printed precision. No D1, D2, or D3 deviations are introduced by this experiment. The existing D3 deviation in the manuscript (entry 3 in DEVIATIONS.md) concerns the mechanistic attribution in the text, not the numerical results. R02c provides evidence that constrains the admissible explanation without altering any published numerical claim.

## 4. Methodological Scope and Limitations

This experiment establishes that the Ljung-Box over-rejection for heavy-tailed innovations (nu <= 6) persists across a 64-fold increase in sample horizon (n=2000 to n=128000), with flat WLS slopes indistinguishable from zero at 95% confidence.

The witness arm at nu=7 maintains calibration, demonstrating that the effect is specific to nu <= 6 and not a general property of the Student t family.

The flat slope refutes H1 (convergence rate hypothesis) but does not validate H2 (eighth-moment explanation). Both hypotheses remain consistent with the asymptotic flatness: H1 because a summand lacking a third absolute moment carries no n^(-1/2) guarantee, and H2 because E[epsilon^8] is infinite for nu <= 8, including nu=7 where no over-rejection is observed.

**Scope:** R02c neither adds nor removes any numerical claim from the manuscript. It constrains the mechanistic explanation that may be offered in camera-ready revision. Specifically, it rules out attributing the over-rejection to a missing eighth moment, which is the account nearest to the current v87 wording.

The true mechanism remains untested; the coincidence of the transition with the Berry-Esseen boundary (nu > 6) is suggestive but not causal.

**Limitations:** The design tests only four horizon points and three nu values. A finer grid could locate the transition more precisely. The experiment does not test alternative heavy-tailed distributions or different lag specifications for the Ljung-Box test.
