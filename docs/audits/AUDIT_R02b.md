# Audit Report: R02b I.I.D. Arm Resolution

## 1. Theoretical Anchor

The Ljung-Box portmanteau test for white noise requires finite variance of the tested series to guarantee asymptotic chi-square validity. For Student's t innovations with nu degrees of freedom, the squared series epsilon_t^2 has variance Var(eps^2) = 2 * nu^2 / (nu - 4) for nu > 4, satisfying the Ljung-Box condition throughout the grid. The fourth moment E[eps^8] exists only for nu > 8 and governs tail quantile convergence, not the validity of the limiting distribution. This experiment isolates the squaring operation as the sole distortion source by testing both raw and squared innovations on identical realizations.

## 2. Empirical Methodology

Design: 1000 independent i.i.d. streams per grid point, nu in {5.0, 6.0, 7.0, 8.5, 12.0, 30.0}, horizon n = 8000, Ljung-Box lag = 20. Each stream is seeded via 128-bit deterministic hash (MD5 of stream identifier + nu + index). Negative control applies the same test to raw innovations eps_t, which have finite variance for all nu and must therefore hold the nominal 5% level if the implementation is correct.

Execution: Single-threaded BLAS/MKL environment under PYTHONHASHSEED=42, MKL_CBWR=COMPATIBLE. Parallelization via joblib with n_jobs=4 for stream-level embarrassment. Seed collision detection enforced at runtime.

## 3. Concordance Table with Wilson 95% Confidence Intervals

| nu  | Reject Rate (squared) | Wilson Low | Wilson High | Contains 5% | Classification |
|-----|------------------------|------------|--------------|--------------|----------------|
| 5.0 | 8.8% | 7.2% | 10.7% | NO | D3 |
| 6.0 | 7.9% | 6.4% | 9.7% | NO | D3 |
| 7.0 | 5.8% | 4.5% | 7.4% | YES | D2 |
| 8.5 | 6.1% | 4.8% | 7.8% | YES | D1 |
| 12.0 | 4.8% | 3.6% | 6.3% | YES | D0 |
| 30.0 | 6.0% | 4.7% | 7.6% | YES | D0 |

Negative control (raw innovations): All six Wilson intervals contain the nominal 5% level, confirming implementation correctness.

Deviation Classes: D3 at nu=5,6 (qualitative claim falsified at printed precision), D2 at nu=7 (printed value shifts but qualitative claim holds), D1 at nu=8.5 (rounded value invariant), D0 at nu=12,30 (float64 identical within representation).

## 4. Methodological Scope and Limitations

Scope: This experiment certifies the i.i.d. arm rejection phenomenon and constrains its location to the region nu < 7. It does not identify the mechanism, which would require theoretical analysis beyond the empirical sweep performed here. The manuscript's stated mechanism (t_7 lacking a fourth moment) is demonstrated to be incorrect; the transition sits between nu=6 and nu=7, not at nu=8.

Limitations: The 8000-step horizon may be insufficient to distinguish convergence-rate effects from genuine asymptotic failure. A dedicated horizon sweep (R02c) addresses this. The negative control validates the implementation but cannot rule out shared defects in the underlying random number generation.
