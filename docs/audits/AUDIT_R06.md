# R06 Audit Report: Empirical Validity Map of the Whitening Property

## 1. Theoretical Anchor

R06 maps the empirical boundaries of Proposition prop:whitening, which states that the binary error stream of a non-anticipative classifier predicting the sign of a return is exactly i.i.d. Bernoulli(1/2) regardless of GARCH dynamics. Panel (A) demonstrates moment-robust whitening: the t7 innovation grid violates E[eps_t^4] < ∞ beyond Gamma ≈ 41.6, yet the binary error stream remains strictly white up to Gamma = 200 with pooled rejection rate 4.77% covering the nominal 5% level at cluster-robust precision. Panel (B) charts sharp task boundaries: a non-median threshold (c > 0) or continuous MSE loss re-inherits autocorrelation, with 100% rejection for c ≥ 0.5 and for MSE, exactly as Remark rem:scope requires. The experiment implements a paired design where one seed carries the same label stream to every Gamma (innovations drawn before variance recursion), which sharpens cross-Gamma comparisons and is declared with its design effect (3.21) properly measured and accounted for.

## 2. Empirical Methodology

The experiment generates 100 streams per configuration across a 13-point Gamma grid (1, 2, 5, 8.16, 11.58, 20, 30.85, 41, 60, 90, 120, 160, 200) with nu = 7 Student-t innovations, N = 8000 steps, and Ljung-Box test at lag 20 with nominal level alpha = 0.05. Part A produces 1300 paired streams; Part B evaluates 4 thresholds (0, 0.25, 0.5, 1) for binary classification and continuous MSE, totaling 500 streams; a counterfactual arm with 1300 independent per-cell seeds removes pairing to verify design effects. The GARCH(1,1) generator and both task evaluators (evaluate_sign_task, evaluate_continuous_loss) are copied verbatim from the submitted script and asserted byte-identical at start-up. The fourth-moment boundary is computed from (alpha, nu) using closed-form expressions: kurtosis = 3(nu-2)/(nu-4) = 5.0 for nu = 7, solving kurtosis * alpha^2 + 2 * alpha * beta + beta^2 = 1 yields beta = 0.907117, mapping to Gamma = 41.584288. All float64 representations and p-value computations use IEEE-754 compliant arithmetic with single-threaded BLAS enforcement.

## 3. Concordance Table with Wilson 95% Confidence Intervals

| Metric | Manuscript Value | Regenerated Value | Deviation Class | Wilson 95% CI Lower | Wilson 95% CI Upper |
|--------|------------------|-------------------|-----------------|---------------------|---------------------|
| Fourth-moment boundary Gamma | 41.6 | 41.58 | D1 | N/A (analytic) | N/A (analytic) |
| Pooled binary rejection (1300 streams) | 0.0477 | 0.0477 | D0 | 0.0292 | 0.0692 |
| Pooled squared-stream rejection | 0.9277 | 0.9277 | D0 | N/A | N/A |
| Task boundary: binary c = 0.0 | 0.0700 | 0.0700 | D0 | 0.0343 | 0.1375 |
| Task boundary: binary c = 0.25 | 0.4400 | 0.4400 | D0 | N/A | N/A |
| Task boundary: binary c = 0.5 | 1.0000 | 1.0000 | D0 | N/A | N/A |
| Task boundary: binary c = 1.0 | 1.0000 | 1.0000 | D0 | N/A | N/A |
| Task boundary: continuous MSE | 1.0000 | 1.0000 | D0 | N/A | N/A |
| Design effect (paired campaign) | N/A | 3.21 | N/A | N/A | N/A |
| Effective sample size | N/A | 405 | N/A | N/A | N/A |

All tabular data (gamma_grid.csv, task_boundary.csv) reproduce the submitted campaign byte-for-byte. The fourth-moment boundary rounds to 41.6 at manuscript precision (D1). All other metrics are bit-identical (D0). Wilson intervals use the cluster-robust variance for pooled metrics and simple binomial variance for marginal cells.

## 4. Methodological Scope & Limitations

R06 establishes that the whitening property holds empirically across a wide Gamma range despite fourth-moment violations. The paired design declaration is critical: failure to account for it would understate variance by sqrt(3.21) = 1.79, potentially leading to false certifications. The median-task control (c = 0) has limited resolution at N = 100: Wilson interval [3.4%, 13.7%] has half-width 5.2 percentage points, which is 1.0 times the nominal level, so the control is consistent with whiteness rather than confirmatory. Three fallbacks from the submitted script are counted and logged: degenerate streams mapped to p = 1.0 (count: 0), estimator failures mapped to NaN (count: 0), and null predictions substituted by class 0 (structural: 1 per stream at t = 0, total 3000). The fourth-moment boundary is an analytic computation, not a measured grid point; the nearest measured Gamma is 41, which is 0.584288 below the boundary. The grid does not sample the boundary, and the figure draws it as a labelled vertical rule distinct from the axis ticks.
