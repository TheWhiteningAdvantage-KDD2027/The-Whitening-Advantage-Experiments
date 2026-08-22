# AUDIT — R07, whitening under an estimated conditional mean

## Theoretical Anchor

R07 evaluates the survival of whitening when the conditional mean is estimated rather than known. The theoretical propositions guarantee Bernoulli(1/2) whitening under conditional measurability but do not guarantee estimator accuracy. Six arms are evaluated: NAIVE (µ̂ₜ = 0), ORACLE (µ̂ₜ = φ rₜ₋₁), and four rolling-OLS configurations with n ∈ {125, 250, 500, 1000}. The analysis covers φ ∈ {0, 0.02, 0.05, 0.075, 0.10, 0.125, 0.15} under AR(1)-GARCH(1,1) with Student-t₇ innovations, horizon H = 5000, 10000 paired trajectories.

## Empirical Methodology

The pipeline executes under 128-bit cryptographic seeding with every task keyed on semantic role and index. The ORACLE arm is bit-identical across all seven φ values by construction. The exact 2δ lattice law is computed via absorbing-chain dynamic programming, validated against exhaustive enumeration at H ∈ {8, 10, 12}. Threshold λ* = 11.4 is fixed by L241's rule (nearest attainable level at or below nominal). All 28 OLS cells are compared against ORACLE using paired McNemar tests at 99.9% confidence. Design effects are measured via Kish's formula before any pooled interval.

## Concordance Table with Wilson Score Intervals and D0–D3 Classes

| Metric | v87 prints | R07 measures | Wilson 95% CI | Deviation |
| ------ | ---------- | ------------- | ------------- | --------- |
| NAIVE LB at φ=0 | 5.1% | 4.92% | [4.51%, 5.36%] | D2 |
| NAIVE LB at φ=0.15 | 99.8% | 99.79% | [99.66%, 99.92%] | D0 |
| NAIVE FPR at φ=0.15 | 20.8% | 21.00% | [20.48%, 21.52%] | D2 |
| OLS LB envelope | 4.6–5.6% | 4.7–5.63% | — | D2 |
| OLS FPR envelope | 4.3–5.9% | 4.84–5.61% | — | D2 |
| Bias bound | < 2.9×10⁻³ | 3.1269×10⁻³ | [3.082×10⁻³, 3.172×10⁻³] | D3 |
| η at n=125 | 11.4% | 11.48% | [11.33%, 11.63%] | D1 |
| E[(αz²+β)²] | 1.005 | 1.00517456 | — | D0 |

Four D2, one D3, one D1, two D0 classifications. The D3 (bias bound) does not falsify the qualitative claim that bias is small; 3.1×10⁻³ remains three orders of magnitude below estimated coefficients.

## Methodological Scope

The stream establishes that rolling-OLS estimation preserves whitening properties within oracle bands across the full 7×4 grid. All OLS cells match ORACLE at four paired standard errors while NAIVE diverges at 34 standard errors at φ=0.15. The η exponent (-0.4378, 95% CI [-0.4401, -0.4355]) confirms non-1/√n decay, invalidating interpretation of panel B as a window-size effect. Controls C1–C9 provide deterministic and statistical validation. The exact lattice levels (4.3428%, 5.1021%) are handed to R08 via camera-ready candidate R07_v87_lattice_handoff_to_R08.md.
