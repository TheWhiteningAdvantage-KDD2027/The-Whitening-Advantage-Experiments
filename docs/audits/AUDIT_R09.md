# Audit Report: R09 Anytime-Valid Detection on the Fair-Coin Stream

## Theoretical Anchor

R09 establishes anytime-valid inference for concept-drift detection on heteroscedastic streams via Ville's inequality applied to a mixture martingale. The mixture combines 96 non-negative martingales (16 start times × 3 betting fractions × 2 sides) each with expectation 1 under H0, forming a convex combination to which Ville's bound P(sup_t E_t ≥ c) ≤ 1/c applies directly. The fixed-horizon CUSUM detector, calibrated at horizon H, loses its time-uniform guarantee when monitoring continues to 4H, demonstrating the necessity of anytime-valid alternatives. e-CUSUM provides a third arm satisfying ARL0 ≥ 1/α under its exact null.

## Empirical Methodology

The campaign executes four protocols under strict determinism (enforce_strict_determinism, PYTHONHASHSEED=42, BLAS/CBWR pins). M1 certifies E[λ_t] = 1 for the mixture kernel via 2×10^6 draws (SD = 0.216025, SE = 1.528e-4). CUSUM calibration computes λ* from 50 000 fair-coin streams over [1, H]. The H0 campaign runs 20 000 streams over [1, 4H] with three arms (CUSUM, MIX, eCUSUM) on the same uniform stream for paired comparisons. The H1 campaign evaluates 2 000 drift streams per cell across 10 drift magnitudes with common random numbers. Controls: C1 (structural censoring-ARL0 linkage), C2 (computed arl0_bound_respected flag), C3 (one-sided Kolmogorov D+ on MIX with exact null, gate at 0.01), C4 (Spearman monotonicity of ADD vs η with exact permutation null, gate at 0.01 per arm), plus calibration coherence and cross-check gates. All CSVs use float_precision='round_trip'; LaTeX macros use %.17g formatting with \RNine prefix.

## Metric Concordance Table

| Metric | Manuscript | Repository | Delta | D-Class | Wilson 95% CI |
|--------|------------|------------|-------|---------|----------------|
| CUSUM peeking FPR (L243/L559) | 18% | 20% | +2% | D2 | [19.3%, 20.4%] |
| CUSUM calibrated level at H | 5% | 5% | 0 | D1 | [4.7%, 5.3%] |
| MIX ADD at η=0.10 (L243) | 409 | 410 | +1 | D2 | [409.9, 410.9] |
| CUSUM ADD at η=0.10 (L243) | 539 | 533 | -6 | D2 | [532.3, 533.3] |
| Streams per level (L243/L559) | 2×10^4 | 20000 | 0 | D0 | [20000, 20000] |
| MIX peeking FPR max | ≤α | 4.9% | - | D1 | [4.7%, 5.1%] |
| e-CUSUM ARL0 min | ≥1/α | 205.43 | - | D1 | [199.8, 211.1] |

**Qualitative Claims:** All hold. Mixture remains bounded by α under peeking at all 7 levels (ratios 0.948-1.000). CUSUM peeking exceeds MIX peeking at all 7 levels (22.9-68.5 paired SEs). e-CUSUM satisfies ARL0 ≥ 1/α with minimum margin 20.54×. MIX matches or exceeds CUSUM speed at η ≤ 0.10 under selection-free matched-detection-rate quantile.

**Deviation Summary:** One D2 entry (R09-campaign-redraw) for the three moved numerals due to 128-bit re-keying. Three no-severity entries (R09-arl0-censoring, R09-add-conditioning, R09-stream-counts) document legibility corrections. See docs/DEVIATIONS.md register and docs/camera_ready_candidates/R09_v87_*.md.

## Methodological Scope & Limitations

R09 covers v87 Figure 9 (L243 paragraph, L559 caption) with three panels: (A) realized false-alarm rate under three stopping protocols (nominal, extended, peeking), (B) detection delay vs drift η at α=0.05, (C) average run length vs α with censoring made visible. Sample sizes: N_CAL=50000 (calibration), N_NULL=20000 (H0), N_ALT=2000 (H1). The H0 horizon is H=5000; peeking extends to T_EXT=20000. Detection delay ADD is conditional on alarm in (τ, H].

Limitations: (1) CUSUM statistic lives on a 0.2 lattice (dev - DELTA_CUSUM takes +0.4 or -0.6), making λ* move in discrete steps; peeking FPR shift from 18% to 20% traces to one lattice step in λ*. (2) CUSUM and MIX ARL0 curves in panel C are horizon artefacts at 65-99% censoring; only e-CUSUM provides a genuine ARL0 measurement (0-0.055% censoring). (3) Panel B's marginal ADD inverts arm ordering at η ≤ 0.04 due to conditioning on different detection events; the selection-free matched-detection-rate quantile (control C4) resolves this. (4) The caption's "2×10^4 streams per cell" describes only panels A and C; panel B uses 2×10^3 streams.
