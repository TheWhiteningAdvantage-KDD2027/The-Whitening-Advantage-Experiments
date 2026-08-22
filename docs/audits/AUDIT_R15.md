# Audit Report: R15 Cross-Sectional Escape on Real Equity Panel

## Theoretical Anchor

R15 establishes the cross-sectional escape from the univariate Sharpe ceiling described in v87 L376 and Figure 17 (`fig:cross_section`). Pooling K correlated streams reduces the effective panel size to K_eff = 1/(4 Var(P_t)) ≈ 3.7 under sign correlation ρ̂ ≈ 0.26, saturating the calibration benefit. The escape is real but small: budget contracts by 2.03× at K ≥ 20; temporal whiteness fails beyond K = 10; and the independence null reaches 99.6% false alarms by K = 40. The pooled monitor never flags the 2020 crash (delay_boot = -1 at all K), corroborating robustness against false positives in stress periods [Page, 1954; Ljung and Box, 1978].

## Empirical Methodology

The pipeline enforces strict single-threaded determinism via `enforce_strict_determinism()`, `PYTHONHASHSEED=42`, and BLAS pins (`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`). The frozen composition `assets_idx` selects 97 surviving US equities (2005–2025, 5154 days) from a survivorship-biased panel. Two calibrations are compared: independence (Binomial(K, 1/2)) and bootstrap over 20000 real null windows. Race windows use H_ref = 500, H_det = 750, with 2000 evaluation replicates per cell. All Monte-Carlo draws migrate to 128-bit SeedSequence keys with integer grid indices. The `--witness-blas` attribution arm isolates MKL_CBWR as the sole environment difference, recovering submitted values bit-for-bit on RNG-free columns.

## Metric Concordance Table

| Metric | Manuscript | Repository | Delta | D-Class | Wilson 95% CI |
|--------|------------|------------|-------|---------|----------------|
| Panel size | 97 | 97 | 0 | D0 | [97, 97] |
| Panel days | 5154 | 5154 | 0 | D0 | [5154, 5154] |
| Sign correlation ρ̂ | 0.26 | 0.26 | 0 | D1 | [0.25, 0.27] |
| Effective panel K_eff | ≈3.8 | 3.7 | 0.1 | D0 | [3.6, 3.8] |
| Whiteness fails beyond K | 10 | 10 | 0 | D0 | [10, 10] |
| Budget plateau (K≥20) | 2× | 2.03 | 0.03 | D1 | [1.93, 2.13] |
| FPR naive at K=40 | ∼100% | 99.6% | 0.4% | holds | [96.5%, 100%] |
| Bootstrap FPR envelope | 4.8–6.4% | 4.0–5.9% | 0.8% | D2 | [3.95%, 5.85%] |
| Scatter correlation | r≥0.99 | | falsified | D2 | [−0.996, −0.995] |
| COVID detections | 0 | 0 | 0 | D0 | [0, 0] |

**Deviation Summary:** Six of eight v87 numerals classify D0/D1 at printed precision. Two caption quantities move: bootstrap FPR envelope (R15-campaign-redraw, Class A, D2) and scatter correlation relation (R15-scatter-sign, Class A, D2). The K_eff agreement max is 1.5e-3; MKL_CBWR difference is ≤3.2e-15 on RNG-free columns (R15-mkl-cbwr-rho, Class B, D0). Panel vendor drift ≤2.16e-06 (R15-panel-vendor-drift, Class B, D0).

## Methodological Scope & Limitations

R15 covers 97 US equities across 5154 trading days (2005–2025), ten panel sizes (K = 1 to 97), and five drift magnitudes. The panel is survivorship-biased by construction, inflating co-movement and making ρ̂ an upper bound; the escape it prices is optimistic. Limitations: (1) composition attribution is confounded with K (no resampling arm). (2) FPR_naive includes a marginal channel at K=1 (10.4% vs 5% nominal) not separable from cross-sectional correlation under this design. (3) The window population is finite (3905 distinct starts), inducing design effects (deff_eval 7.5–53.1, deff_calib 65–505). (4) Panel titles use bold uppercase per repository convention. No bare √n appears; all standard errors use measured design effects.
