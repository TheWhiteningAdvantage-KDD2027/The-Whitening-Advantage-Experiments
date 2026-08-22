# AUDIT — R12: Volatility misspecification and moment singularity

R12 reproduces v87 Figures 12 and 13 (L349, L353) under the repository 128-bit seeding policy and role-and-index-only keying. Experiment A evaluates 15 leverage coefficients γ_lev ∈ [0, 0.28] with 10 000 streams each, n = 7 000, pseudo-Gaussian innovations (ν = 100). Baseline uses symmetric filter α_sym = α + γ_lev/2; Concept monitors sign stream at fixed threshold. Experiment B evaluates 16 degrees of freedom ν ∈ [4.01, 10] with 1 000 streams each, n = 10 000, drift c = 1.0σ. Combined: 316 000 monitored streams.

---

## Theoretical Anchor

R12 tests the central claim that sign-based monitoring (Concept pipeline) remains calibrated under volatility misspecification while the variance-standardized pipeline (Data) explodes. The GJR-GARCH DGP with leverage parameter γ_lev introduces asymmetric volatility response to negative shocks; at γ_lev = 0.28 the persistence reaches 0.99. The fourth-moment boundary at ν* = 4.0811 under (α, β) = (0.05, 0.85) marks the transition where E[ε⁴] diverges per He & Terasvirta (1999). Proposition 1 predicts Concept calibration holds regardless of volatility clustering under symmetric innovations; R12 measures this prediction against the Data pipeline's failure.

## Methodology

Both experiments use role-and-index-only 128-bit seeding with fixed chunk decomposition (NUM_CHUNKS_A = 25, NUM_CHUNKS_B = 10) ensuring byte-identical output across worker counts. Experiment A runs two Concept arms: CRN arm asserts bit-identity across γ_lev (control C8); published arm carries grid index to break pairing. Data arm reads squared returns through variance recursion, carrying γ_lev non-degenerately. Experiment B measures detection decay toward fourth-moment singularity. All controls C1–C11 pass. Single-threaded determinism enforced via enforce_strict_determinism() before NumPy import; PYTHONHASHSEED=42 exported by run_experiment_R12.sh and verified at start-up. Artefacts: R12_leverage_fpr.csv, R12_singularity_add.csv, R12_concept_crn_witness.csv, R12_diagnostics.csv, fig12_leverage.png, fig13_fat_tails.png, R12_claims.tex.

## Concordance Table with Wilson Score Intervals and D0–D3 Classes

Run at v87 printing precision. Regenerated values from CSVs with Wilson 95% CI at z = 1.959963984540054.

| v87 site | printed | regenerated | Wilson 95% CI | class | source |
| --- | --- | --- | --- | --- | --- |
| L349 Ljung–Box γ_lev = 0 | 5.1% | 5.4% | [4.98%, 5.83%] | D2 | R12_leverage_fpr.csv |
| L349 Ljung–Box γ_lev = 0.28 | 24.6% | 24.2% | [23.53%, 24.87%] | D2 | R12_leverage_fpr.csv |
| L349 FPR γ_lev = 0 | 3.2% | 3.5% | [3.12%, 3.88%] | D2 | R12_leverage_fpr.csv |
| L349 FPR γ_lev = 0.28 | 20.6% | 20.5% | [19.81%, 21.19%] | D2 | R12_leverage_fpr.csv |
| L349 Concept FPR min | 7.6% | 7.4% | [6.85%, 9.07%] | D2 | R12_leverage_fpr.csv |
| L349 Concept FPR max | 8.4% | 8.5% | [7.88%, 9.15%] | D2 | R12_leverage_fpr.csv |
| L349 Concept LB min | 4.6% | 4.7% | [4.18%, 5.87%] | D2 | R12_leverage_fpr.csv |
| L349 Concept LB max | 5.4% | 5.4% | [4.79%, 6.03%] | D1 | R12_leverage_fpr.csv |
| L349 factor of six | six | 5.92 | — | D1 | fpr_data ratio |
| Fig. 12 streams/point | 10 000 | 10 000 | — | D0 | N_SEEDS_A |
| Fig. 13 streams/point | 1 000 | 1 000 | — | D0 | N_SEEDS_B |
| L353 detection ν = 10 | 83% | 82% | [80.02%, 84.73%] | D2 | R12_singularity_add.csv |
| L353 detection ν = 7 | 61% | 62% | [59.05%, 65.06%] | D2 | R12_singularity_add.csv |
| L353 collapse threshold | 5.5 | 5.5 | — | D1 | max ν with det_rate_data < 0.5 |
| L353 censored delay min | 2 400 | 2 610 | [2426.85, 2594.12] | D2 | ADD_Data_Raw |
| L353 censored delay max | 3 000 | 2 999 | [2948.04, 3050.98] | D1 | ADD_Data_Raw |
| L353 Concept delay min | 34 | 34 | — | D1 | ADD_Concept |
| L353 Concept delay max | 38 | 38 | — | D1 | ADD_Concept |

**Summary: Ten D2, five D1, four D0, zero D3.** All qualitative claims hold. Halt candidate [2350, 3050) bracket not breached at 95% level.

## Methodological Scope

R12 certifies no published value and exists solely for control auditing on C4, C5, C8, C9, C10. The two-arm design (CRN witness + independent-key published) resolves the sign-stream bit-identity issue from simulate_gjr_garch drawing innovations before variance recursion. Control C8 asserts bit-identity on 50 seeds × 15 γ_lev (750 pairs, 50 distinct digests). Control C9 gates invariance via OLS slope −0.9286 pp with 95% CI [−2.4500, +0.6577], p = 0.2477. Control C10: 0 clamped steps of 52 993 800, max unclamped σ²_t: 4889×σ²_unc. Control C11 verifies legacy-global inertness. Family-wise error rate: 0.0100 < 5%. All seven deviations Class A (correction of entropy defects), D2 severity. No D3 met; no parameter, tolerance, seed, or bound moved to force pass. Full account in docs/DEVIATIONS.md entries R12-campaign-redraw through R12-censored-delay.
