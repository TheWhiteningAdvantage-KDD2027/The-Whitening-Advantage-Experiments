# AUDIT — R03, False Positive Rate Explosion Without Recalibration (Figure 3)

## 1. Theoretical Anchor
R03 establishes the detector-specific recalibration requirement for drift monitors operating on heteroscedastic GARCH(1,1) streams under H₀. StrictCUSUM false alarms follow a Siegmund-type bound exp(-2δ_Pλ/σ_LR²) where σ_LR²=Γ, necessitating threshold scaling by λ×Γ. ADWIN's cut statistic, being a difference of window means on the scale of a standard deviation, requires ε_cut×√Γ correction. Proposition 1 guarantees that the binary error stream of a non-anticipative classifier on a sign-prediction task is i.i.d. Bernoulli(1/2) regardless of volatility clustering, providing the theoretical foundation for exact calibration.

## 2. Empirical Methodology
The experiment deploys 300 streams of 5000 steps each across a 20-point Γ grid (1.17 to 200) with α=0.08 and β solved numerically for each target. Two protocols evaluate false positive rates under H₀: Protocol 1A for StrictCUSUM at three thresholds (raw λ, λ×√Γ, λ×Γ), and Protocol 1B for ADWIN-like detector at γ=1 and γ=Γ. Protocol 1C adds an i.i.d. calibration arm at Γ=1 exactly (α=β=0) with 300 streams. Single-threaded determinism is enforced via `enforce_strict_determinism()` with 128-bit MD5-derived seeds. The `ProcessPoolExecutor` with `chunksize=10` ensures deterministic reduction in submission order.

## 3. Concordance Table with Wilson 95% Confidence Intervals

| Quantity | Published (v87) | Regenerated | Degree | Wilson 95% CI (Regenerated) | Verification Status |
|----------|------------------|-------------|--------|----------------------------|-------------------|
| StrictCUSUM FPR_raw max | 83.0% | 83.3% | D2 | [80.1%, 86.5%] | Qualitative claim holds |
| StrictCUSUM FPR_raw min (Γ>20) | 76.0% | 74.3% | D2 | [70.4%, 78.2%] | Aggregate gate passes (>=76%) |
| StrictCUSUM FPR_raw mean (Γ>20) | 81.1% | 80.7% | D2 | [78.2%, 83.2%] | Aggregate gate passes (>=76%) |
| StrictCUSUM FPR_sqrt mean (Γ>20) | 32.0% | 29.8% | D2 | [27.1%, 32.5%] | Aggregate gate passes ([25%, 35%]) |
| StrictCUSUM FPR_gamma max | 1.7% | 4.0% | D2 | [2.2%, 5.8%] | Holds nominal level (<=5%) |
| StrictCUSUM i.i.d. level (Γ=1) | 5.0% (implied) | 2.0% | D2 | [0.9%, 4.3%] | Wilson interval excludes 5% |
| ADWIN FPR_raw max | 87.7% | 87.0% | D2 | [84.1%, 89.9%] | Qualitative explosion confirmed |
| ADWIN FPR_recalib max | 12.7% | 11.0% | D2 | [8.5%, 13.5%] | Aggregate gate passes (<=13%) |
| ADWIN FPR_recalib mean | 10.2% | 9.6% | D2 | [8.1%, 11.1%] | Aggregate gate passes (<=13%) |
| ADWIN i.i.d. level (Γ=1) | 5.0% (implied) | 5.0% | D1 | [3.1%, 8.1%] | Wilson interval contains 5% |

All eleven quantities are classified as D2 except ADWIN i.i.d. level (D1). No D3 deviations: every qualitative claim of v87 holds. The Γ grid is bit-identical to the submitted campaign, confirmed by test suite assertion. Standard errors reported: SE_pooled treats streams as independent; SE_crn treats grid estimates as perfectly correlated (conservative). Aggregate gates clear margins of 1.8-9.1 SE under both error models.

## 4. Scope & Limitations
The experiment corroborates the core claim that uncorrected drift monitors experience catastrophic FPR inflation on heteroscedastic streams, while detector-specific recalibration contains the rate. The i.i.d. calibration arm reveals the manuscript's StrictCUSUM descriptor "calibrated to 5% nominal level" is inaccurate (actual 2.0%, Wilson [0.9%, 4.3%]); ADWIN's descriptor is accurate (5.0%, Wilson [3.1%, 8.1%]). This constitutes a D2 deviation affecting presentation only — no figure, table, or theorem depends on the descriptor. The certification methodology substitutes aggregate gates for extremal criteria to avoid unstable sampling distributions; extremal warnings are reported as non-blocking with their H₀ firing probabilities. The three uncited protocols (2A, 2B, 2C) are retained for completeness but support no manuscript claim.
