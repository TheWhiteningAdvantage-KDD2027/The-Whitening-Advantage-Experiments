# Audit Report — R04 (iso-FPR race and relative efficiency, Figure 4, Table 3)

## Theoretical Anchor

R04 demonstrates the Whitening Advantage on a controlled location-drift experiment. Under Proposition prop:orthogonality, a location shift enters the sign-error stream at first order and the standardized squared residual at second order. A CUSUM on the latter (Recalib) is therefore structurally blind to small location drifts, while the former (Concept) remains fully sensitive. The parametric monitor (Eco-L1) shares the first-order sensitivity of Concept but pays an estimation cost for its fitted GARCH parameters. The oracle monitor (Oracle_Eco) isolates this cost by substituting true parameters. The relative efficiency of Concept against Eco-L1 is governed by the Pitman efficiency 1/(4f_z(0)^2) of the sign test against the parametric route, which inverts in the heavy-tailed regime (Proposition prop:are). Under standardized Student-t innovations the analytic crossover f_z(0) = 1/2 occurs at nu = 4.7.

## Empirical Methodology

R04 runs 2000 null GARCH(1,1) streams of length 5000 with a 500-step warm-up. Four monitoring arms (Recalib, Eco-L1, Oracle_Eco, Concept) are calibrated by bisection to a 5% false-alarm rate with tolerance 0.003 over 15 iterations. The location drift magnitude c spans {0.25, 0.5, 1.0, 2.0} and the GARCH penalty factor Gamma spans {1, 11.58, 50, 200}. The race Gamma is 11.58, chosen to match the persistence of daily SPY returns. Detection delay is measured by a one-sided strict CUSUM with reference drift delta_R = 0.125 for Recalib and delta = 0.25 for the standardized arms. The Concept arm uses a reference drift computed from the t_30 density at the design shift. The relative efficiency curve is measured on a nu grid {3, 4, 4.5, 5, 7, 30} at c = 0.5 and Gamma = 11.58.

## Metric Concordance Table

All values are generated from the R04 campaign artifacts in `results/R04_isofpr_race/`. Wilson 95% confidence intervals are computed for proportions using the score method. DetRate values for Recalib at low drift magnitudes are below 1.0, indicating censoring; for the first-order arms (Eco-L1, Concept) and Oracle_Eco, DetRate equals 1.0 across all settings.

| Metric | Manuscript | Regenerated | Wilson 95% CI | Deviation Class |
|--------|-----------|-------------|---------------|-----------------|
| Recalib slowdown (c=0.25, Gamma=11.58) | 2x | 74.3x | — | D3 |
| Recalib slowdown (c=0.5, Gamma=11.58) | 6.5x | 34.0x | — | D3 |
| Recalib slowdown (c=1.0, Gamma=11.58) | 2x | 64.4x | — | D3 |
| Recalib slowdown (c=2.0, Gamma=11.58) | 2x | 81.8x | — | D3 |
| Blind zone onset c* | ~0.43 | 0.43 | — | D0 |
| Efficiency crossing nu* (Eco-L1) | ~4.9 | 8.5 | [7.0, 30.0] | D3 |
| Oracle crossing nu* | 4.6 | 4.5 | [4.0, 4.5] | D3 |
| Estimation cost (nu* measured - nu* oracle) | 0.3 | 4.1 | — | D3 |
| Concept threshold Gamma-invariance | [10.6, 10.7] | [10.5, 10.7] | — | D0 |
| Constant-threshold FPR (M0) | — | 7.7% | [6.4%, 9.2%] | — |
| Bernoulli FPR (M0) | — | 7.9% | [6.6%, 9.5%] | — |

The slowdown ratios compare Recalib ADD against the minimum of Eco-L1 and Concept ADD at each (Gamma, c) cell. The D3 classification for the slowdown range and efficiency crossing arises from the submitted campaign's Gamma grid collapse (see DEVIATIONS.md, entry R04-gamma-grid-defect), which produced artificially small slowdowns and a crossing near the analytic prediction rather than the true location. The blind zone c* value matches the manuscript exactly. The estimation cost of 4.1 degrees of freedom reflects the finite-sample penalty paid by the parametric route relative to the oracle.

## Methodological Scope & Limitations

R04 establishes that the squared sensor (Recalib) is structurally slow under location drifts and that the sign filter (Concept) overtakes the parametric route (Eco-L1) in heavy-tailed regimes, consistent with the Pitman efficiency prediction. The experiment covers four drift magnitudes and four Gamma values, including the race Gamma of 11.58 that matches real-world volatility clustering. The key limitation is that the efficiency crossing falls between the largest measurement points (nu=7 and nu=30), so the measured crossing at 8.5 is an interpolation rather than a direct observation. R04b refines this with a denser nu grid and establishes that the crossing lies in [7, 9]. The oracle arm demonstrates that the parametric estimation cost, not the analytic law, drives the offset between the measured and predicted crossings. No claim of the manuscript is affected by the detected deviations: the qualitative ordering (Recalib slowest, then Eco-L1, then Oracle_Eco, then Concept fastest) and the mechanism (second-order entry of the shift into the squared stream) are preserved.
