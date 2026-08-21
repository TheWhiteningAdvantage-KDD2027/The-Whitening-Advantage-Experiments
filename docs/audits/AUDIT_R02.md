# Audit Report: R02 Whitening Ljung-Box

## Theoretical Anchor

R02 implements the empirical verification of the Sign-Task Whitening Property (Proposition 1) via Ljung-Box Q-tests on 360 independent stationary GARCH(1,1) streams. The theoretical foundation rests on the proof that under conditionally symmetric innovations, the binary error stream of any non-anticipative classifier is i.i.d. Bernoulli(1/2), structurally insensitive to the GARCH penalty factor Γ. The experiment validates this property by demonstrating that while squared returns εₜ² feeding the Data pipeline exhibit overwhelming autocorrelation (100% rejection in clustered calibrations), the binary classification errors eₜᵇⁱⁿ remain white, maintaining the nominal type-I level across all regimes.

## Empirical Methodology

The pipeline generates 360 independent streams across three regimes (IID, Cal. A with Γ ∈ [4, 8], Cal. B with Γ ∈ [32, 110]), four ETF calibrations (SPY, PFF, VNQ, BWX), and 30 seeds, with horizon n = 8000 and lag-20 Ljung-Box tests. Each stream employs an online Hoeffding Tree classifier on a sign-prediction task with 128-bit deterministic seeding via monolithic MD5 hash injection. The implementation enforces strict single-threaded execution through `enforce_strict_determinism()`, `disable_pandas_multithreading()`, and shell-level environment pinning (PYTHONHASHSEED=42, OMP_NUM_THREADS=1, MKL_NUM_THREADS=1, OPENBLAS_NUM_THREADS=1, MKL_CBWR=COMPATIBLE). Artifacts are serialized using `save_fair_csv()` with float_format='%.17g' to ensure bit-for-bit reproducibility. Cross-stream independence is verified via 18 Bonferroni-corrected Pearson tests, all passing at α = 0.05/6.

## Concordance Table with Wilson 95% Confidence Intervals

| Metric | Manuscript Value | Regenerated Value | Deviation Class | Wilson 95% CI | Status |
| --- | --- | --- | --- | --- | --- |
| Pooled concept rejection rate | 4.4% | 4.17% | D2 | [2.54%, 6.76%] | Nominal covered |
| Wilson lower bound | 2.8% | 2.54% | D2 | — | — |
| Wilson upper bound | 7.1% | 6.76% | D2 | — | — |
| IID arm data rejection | 9.2% | 5.83% | D3 | — | Not over-rejecting |
| Cal. A data rejection | 100% | 100% | D0 | — | Match |
| Cal. B data rejection | 100% | 100% | D0 | — | Match |
| Concept rejection (IID) | 5.0% | 5.00% | D0 | — | Match |
| Concept rejection (Cal. A) | 3.3% | 3.33% | D0 | — | Match |
| Concept rejection (Cal. B) | 5.0% | 4.17% | D1 | — | Rounded match |

The D2 deviation in pooled binary-error rejection (4.4% → 4.17%) is attributed to 128-bit seeding and corrected river dependency. The nominal 5% level remains covered by the Wilson interval [2.54%, 6.76%]. The D3 deviation for the IID arm (9.2% → 5.83%) indicates the original over-rejection claim is not reproduced with the corrected campaign; the rate is consistent with nominal and does not support the mechanism attributed to t₇ innovations.

## Methodological Scope and Limitations

R02 demonstrates the whitening property for sign-prediction tasks with Hoeffding Tree classifiers under GARCH(1,1) dynamics. The scope covers Γ ∈ [1, 110] across four ETF calibrations, demonstrating that binary error streams remain white even when squared returns exhibit strong autocorrelation. Limitations: the experiment does not test continuous losses or non-median thresholds, which are known to break the whitening property; the IID arm rejection rate of 5.83% cannot separate from nominal at n = 120, requiring larger sample sizes or dedicated sweeps (see R02b) to resolve the mechanism behind the original 9.2% claim. All artifacts are generated deterministically and independently, with cross-stream independence verified via Bonferroni-corrected Pearson tests (all 18 pairwise comparisons pass at α = 0.05/6).