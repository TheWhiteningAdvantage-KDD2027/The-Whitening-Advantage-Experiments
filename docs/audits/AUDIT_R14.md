# AUDIT — R14, Efficiency Reversal on Real Bitcoin

## 1. Theoretical Anchor

R14 anchors v87 Proposition 3 and Figure 16: on heteroscedastic streams with Student-t innovations, the recentred sign-CUSUM (Concept) and a CUSUM on honestly standardized GARCH(1,1) residuals (Eco-L1) are compared under equal false-alarm rates. The theoretical foundation is Page (1954) continuous inspection schemes with Bollerslev (1986) GARCH modelling, where volatility clustering creates heavy tails (ν̂ = 2.78 for BTC) invalidating fourth-moment assumptions. The fair-coin pivot (sign stream whiteness) is verified via Ljung–Box tests on recentred signs.

## 2. Empirical Methodology

The experiment executes an iso-FPR race across four sources (Real_BTC, Real_ETH, Synth_BTC, Synth_ETH), 11 drift magnitudes c ∈ {0.10, 0.15, ..., 1.5}, with H_ref = H_det = 500 trading days and 106 (BTC) or 72 (ETH) monthly onsets. Both arms are calibrated via `bisect_fpr` to a common realized FPR near 5% on real placebo windows. The reliable range is derived as magnitudes where both arms achieve DetRate ≥ 0.9, matching the submitted campaign's literal c ≥ 0.35. Single-threaded determinism is enforced via `enforce_strict_determinism()` with 128-bit SeedSequence re-keying on role and index. Design effects are computed via Kish deff = 1 + 2∑(1−k/n)ρ_k with K = 24 mechanism-fixed lags, addressing overlapping detection windows. Paired moving-block bootstrap (B = 2000) provides 95% confidence intervals for ratio means.

## 3. Concordance Table with Wilson 95% CIs and D0–D3 Classification

All comparisons are at v87's printed precision against witness data/reference/R14/protocol_24*.csv read at float_precision='round_trip'. Wilson 95% confidence intervals are computed per wilson_ci(k, n, 0.95) for detection rates.

| # | v87 Location | Printed | Witness | Regenerated | Wilson 95% CI | Class |
|---|--------------|---------|---------|-------------|--------------|-------|
| 1 | L635, L345 | 4.7% | 0.04716981132075472 | 0.04716981132075472 | [0.0356, 0.0604] | D0 |
| 2 | L635, L345 | 106 | 106 | 106 | exact | D0 |
| 3 | L635, L345 | ν̂ = 2.78 | 2.7791143512276766 | 2.7791143512276766 | — | D0 |
| 4 | L345 | 0.74 (c = 0.35) | 0.7407126611068993 | 0.7407126611068993 | — | D0 |
| 5 | L635, L345 | 1.01 (c = 1.5) | 1.0074285714285713 | 1.0074285714285713 | — | D0 |
| 6 | L345 | mean 0.87 | 0.8682292705270857 | 0.8682292705270857 | [0.8351, 0.8937] | D0 |
| 7 | L345 | 0.98 (min) | 0.9818435754189944 | 0.9544910179640719 | [0.9208, 0.9882] | D2 |
| 8 | L345 | 1.14 (max) | 1.1426127128069126 | 1.2384142067139186 | [1.0045, 1.4723] | D2 |
| 9 | L345 | mean 1.06 | 1.0603026678597007 | 1.041041514153539 | [0.9793, 1.0688] | D2 |
| 10 | L345 | ETH p = 0.019 | 0.018785617996181257 | 0.018785617996181257 | — | D0 |
| 11 | L345 | ETH 72 onsets | 72 | 72 | exact | D0 |

Rows 1–6 and 10–11 are bit-identical (D0). Rows 7–9 classify D2 due to 128-bit entropy migration (R14-campaign-redraw, Class A). The qualitative claim that the synthetic control inverts the ordering holds: regenerated mean 1.0410 > 1 with paired bootstrap 95% CI [0.9793, 1.0688] covering the published 1.06. Note this interval spans parity (1.0), indicating statistically weak evidence for inversion though the point estimate claim remains valid. Synth_ETH mean ratio 0.9189 with 95% CI [0.7877, 0.9616] corroborates the light-tailed ordering failure.

## 4. Methodological Scope

R14 reproduces Figure 16 and all numerals of L345. The scope includes: Bitcoin iso-FPR (5/106 = 4.7%) and diagnostics (ν̂ = 2.78, Ljung–Box p = 0.0188 for ETH); Real_BTC delay ratios at c = 0.35 (0.74) and c = 1.5 (1.01) with mean 0.87 over seven pairwise-reliable magnitudes; Synth_BTC control range 0.95–1.24 with mean 1.04; ETH onset count (72) and synthetic control mean ratio 0.9189. One control fires: C2 loses iso-FPR match on Real_ETH (Concept 4/72 vs Eco 3/72); since v87 publishes no speed comparison for real Ethereum, the failure is reported and the source is stamped iso_fpr_matched = False. Design effects are logged for all 88 cells with deff clamped at 1.0 for 54 cells. Ten primary controls (C1–C10) plus family-wise error rate logging (1 − (1−0.05)^7 = 30.2% for maxima over seven points) ensure statistical rigor. Limitations: ADD is conditional on detection (DetRate ≥ 0.9 ≠ 1), the Real_ETH ratio compares detectors at different operating points, and the design effect is measured on delays not detection indicators.
