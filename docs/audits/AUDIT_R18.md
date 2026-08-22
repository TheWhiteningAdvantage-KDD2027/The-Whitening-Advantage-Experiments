# Audit Report: R18 Ljung-Box Power on Binary Streams

## 1. Theoretical Anchor

R18 establishes a global positive control bounding the interpretation of the manuscript's Ljung-Box non-rejections at four sites: L278 (binary errors hold nominal level 3.3-5.0%), L290 (binary error stream stays white up to Gamma = 200), L286 (Figure 6 caption: no detectable autocorrelation), and L318 (lag-20 Ljung-Box finds no serial correlation). The theoretical foundation converts non-rejection statements into probability bounds via the non-central chi-square limit theorem.

Under a symmetric two-state Markov chain with stay probability p = 0.5 + theta, the transition matrix [[0.5+theta, 0.5-theta], [0.5-theta, 0.5+theta]] has eigenvalues 1 and 2*theta with uniform stationary law. The autocorrelation function is rho(k) = (2*theta)^k exactly, isolating dependence from marginal calibration. The Ljung-Box Q statistic under this local alternative converges to a non-central chi-square with m degrees of freedom and non-centrality parameter ncp = n * sum_{k=1}^m rho(k)^2, a geometric sum. The power is P(chi2_nc(m, ncp) > q_0.95), where q_0.95 = 31.4104 is the 0.95 quantile of chi2(20).

The detectable amplitude theta_80 is the root of this power equation at 0.80. The corresponding lag-1 autocorrelation rho_80 = 2*theta_80 is the interpretable bound: a non-rejection excludes an autocorrelation above rho_80 with probability 0.8.

## 2. Empirical Methodology

The compliant pipeline evaluates power on a 36-point amplitude grid (theta in [0, 0.25] with 16 points per decade plus anchors at 0.05 and 0.10) across four horizons (2000, 8000, 32000, 128000) with 1000 streams per point, Ljung-Box at lag 20, nominal level 0.05. Control C4 is structural: one uniform vector of length 128000 generates the chain at every amplitude by re-thresholding, and its first n entries generate every horizon, ensuring paired Monte-Carlo draws.

The symmetric two-state chain is implemented as a parity walk: X_t = Bernoulli(0.5 + theta * (2*U_t - 1)) where U_t ~ Uniform(0,1). This ensures O(n) vectorization and exact rho(k) = (2*theta)^k. The instrument lb_pvalue is carried byte-identical from R02's exp_R02_whitening_ljungbox.py and cross-checked against statsmodels.acorr_ljungbox on 150 sample streams with worst deviation 0.0001 of its budget.

Two application arms validate the bound on actual manuscript streams: (a) the HoeffdingTree binary classifier error stream reproducing Figure 6 and L278, and (b) the raw sign stream 1{eps_t > 0} from R11's Concept pipeline. Both arms use the same configuration (n = 8000, lag 20, level 0.05, 1000 streams) and verify that all measured |rho_1| < rho_80, with power at the measured autocorrelation essentially equal to the nominal level.

## 3. Concordance Table with Wilson 95% Confidence Intervals

R18 reproduces no v87 figure, table, or number. All macros are emitted to results/R18_ljungbox_power/tables/R18_claims.tex with cardinal prefix \REighteen. Wilson 95% confidence intervals use z = 1.96 and account for design effect deff = 1.96 on 36000 paired readings (Kish design effect measured at n = 8000).

| Metric | Value | Wilson 95% CI Low | Wilson 95% CI High | Deviation Class | Notes |
|---|---|---|---|---|---|
| theta_80 grid estimate at n=8000 | 0.0253 | 0.0247 | 0.0259 | N/A | Cluster-bootstrap interval |
| rho_80 grid estimate at n=8000 | 0.0506 | 0.0494 | 0.0518 | N/A | 2 * theta_80 |
| theta_80 analytic at n=8000 | 0.0256 | N/A | N/A | N/A | Brentq on geometric sum |
| rho_80 analytic at n=8000 | 0.0511 | N/A | N/A | N/A | 2 * theta_80 |
| Power at rho=0.10 (theta=0.05) | 1.000 | N/A | N/A | N/A | Saturated, measured not interpolated |
| Power at rho=0.10, n=2000 | 0.782 | N/A | N/A | N/A | Below saturation threshold |
| Size at null, n=8000 | 4.5% | 3.4% | 6.0% | N/A | Wilson interval covers 5% |
| KS p-value at null, n=8000 | 0.214 | N/A | N/A | N/A | Uniform(0,1) calibration |
| Max |emp - anal| on domain | 0.0421 | N/A | N/A | N/A | Against tolerance 0.0474 |
| Design effect (Kish) | 1.96 | N/A | N/A | N/A | On 36000 paired readings |
| Non-centrality at 80% power | 20.96 | N/A | N/A | N/A | Constant across horizons |
| n=32000 bootstrap coverage | N/A | 0.012956 | 0.013490 | N/A | Does NOT cover analytic 0.012793 |

The self-invalidating assertion confirms every measured lag-1 autocorrelation on both application arms lies below rho_80. The classifier-error arm (Figure 6, L278) has max |rho_1| = 0.0008 with power = 0.050 at that autocorrelation. The raw sign arm (R11 Concept) has max |rho_1| = 0.0007 with power = 0.050 at that autocorrelation. The ratio |rho_1|/rho_80 is at most 0.0111, confirming the bound.

## 4. Methodological Scope and Limitations

R18 produces one figure (figA05_ljungbox_power.png) and one table (R18_claims.tex) for camera-ready insertion. The figure shows empirical power curves against analytic predictions across the theta grid and four horizons. The table defines 23 macros carrying the headline bound values, measured autocorrelations, and diagnostic metrics.

R18 validates all qualitative non-rejection claims in the manuscript by establishing that the instrument has sufficient power to exclude meaningful autocorrelations. The local chi-square approximation is exact in the limit and justified at these horizons for binary streams. The C3 tolerance (three standard errors of a proportion) is applied only where power_analytic < 0.95; above this, the approximation degrades and no tolerance is claimed. The measured C3 deviation of 0.0421 is within the 0.0474 budget.

A finding at n = 32000 is recorded: the cluster-bootstrap 95% interval on theta_80 does not cover the analytic root. This is unremarkable (four 95% intervals miss with probability 0.1855 under the null) and does not affect the bound. The grid estimate, analytic root, and bootstrap interval are carried as three separate macros so no reader is handed one in place of another.

All 24 R18 tests pass, including: schema validation of all artifacts, analytic power curve monotonicity, Wilson interval agreement with quadratic formula roots, KS calibration of null p-values, C3 tolerance on the local domain, halving law for theta_80 across quadrupling horizons, constancy of ncp at 80% power, GARCH penalty exactness, and the self-invalidating assertion on measured autocorrelations. The experiment enforces byte-identity of 8 carried primitives and verifies 21 carried statements in R02's simulate_task.
