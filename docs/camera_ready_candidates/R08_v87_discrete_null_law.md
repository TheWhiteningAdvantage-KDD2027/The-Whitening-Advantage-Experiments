# Camera-Ready Candidate: R08_v87_discrete_null_law.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** `R08-delivered-level-above-nominal`

**Target file:** `articleB_whitening_v87.tex`


# R08 v87 Camera-Ready Candidate: Discrete Null Law Claims

| Field               | Value                                                       |
| ------------------- | ----------------------------------------------------------- |
| **Status**          | **PARKED — do not apply**                                   |
| Target file         | `articleB_whitening_v87.tex` (submitted 2026-07-27, frozen) |
| Trigger             | Acceptance notification, 14 November 2026                  |
| Register entry      | `docs/DEVIATIONS.md`, `R08-delivered-level-above-nominal` (Class A, D3) |
| Cost                | macro definitions only; no clause changes                 |

This candidate addresses the numerical discrepancies between the manuscript values and the regenerated results for the discrete null law claims in L241 and Figure 8 Panel C.

## Macro Definitions (Regenerated)

<<< SEARCH
~~~~~~~~~latex
% v87 L241 and the Figure 8 panel C caption, as printed
\newcommand{\REightLevelAbove}{5.03\%}
\newcommand{\REightLevelBelow}{4.29\%}
\newcommand{\REightLambdaStar}{11.4}
\newcommand{\REightLatticeStep}{0.2}
% \REightOperatorDelta and \REightBoundaryCases: v87 prints no counterpart
\newcommand{\REightOperatorDelta}{0.76}
\newcommand{\REightBoundaryCases}{78971}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
% regenerated compliant pipeline
\newcommand{\REightLevelAbove}{5.08\%}
\newcommand{\REightLevelBelow}{4.32\%}
\newcommand{\REightLambdaStar}{11.4}
\newcommand{\REightLatticeStep}{0.2}
\newcommand{\REightOperatorDelta}{0.76}
\newcommand{\REightBoundaryCases}{78971}
~~~~~~~~~
>>> END OF BLOCK

## Manuscript Values (v87 L241, Figure 8 Caption)

- Levels bracketing 5%: 5.03% at λ = 11.2, 4.29% at λ = 11.4
- λ* (nearest attainable level at or below nominal): 11.4
- Lattice step: 2δ = 0.2
- Operator delta: not explicitly stated in manuscript

## Deviation Classification

| Macro | Manuscript | Regenerated | Deviation | Rationale |
|-------|-----------|-------------|-----------|-----------|
| \REightLevelAbove | 5.03% | 5.08% | D2 | Printed value shifts at second decimal; qualitative claim (bracketing 5%) holds |
| \REightLevelBelow | 4.29% | 4.32% | D2 | Printed value shifts at second decimal; qualitative claim (bracketing 5%) holds |
| \REightLambdaStar | 11.4 | 11.4 | D0 | Identical float64 value |
| \REightLatticeStep | 0.2 | 0.2 | D0 | Identical float64 value |
| \REightOperatorDelta | N/A | 0.76 | N/A | New metric not in manuscript; documents the exact weak level minus exact strict level |
| \REightBoundaryCases | N/A | 78971 | N/A | New metric counting streams within ULP budget |

## Explanation of L241 Rule

The manuscript states: "we take the nearest attainable level at or below nominal." The null law lives on a 2δ lattice (δ = 0.1, so 2δ = 0.2). At λ = 11.4 (7 × 2δ units = 14 lattice steps), the exact survival function yields 4.29% in the manuscript vs 4.32% regenerated. At λ = 11.2 (56 lattice units), the level is 5.03% vs 5.08%. Both regenerated levels still bracket 5%, preserving the qualitative claim.

## Control C1 and Operator Identity

The regenerated results confirm that module A operates with the WEAK operator (M >= λ*), delivering 5.08% at λ = 11.2, while the lattice attains the STRICT operator (M > λ*), delivering 4.32% at λ = 11.4. The difference of 0.76 points is the operator delta, which is explicitly quantified in the regenerated results but was implicit in the manuscript.

## Cross-Reference

The λ* computation cites `R07-lambda-star-estimator` in docs/DEVIATIONS.md, which already registers the estimator replacement. The lattice step and δ = 0.1 are anchored in the manuscript's L241 and Figure 8 caption.
