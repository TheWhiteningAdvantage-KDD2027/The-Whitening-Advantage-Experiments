# Camera-Ready Candidate: R04b_v87_efficiency_crossing

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** `R04b-efficiency-crossing`

**Target file: `articleB_whitening_v87.tex`**

`nu* ~ 4.9` is printed at **four** sites, not three: L57 (abstract), L253 (body), L372 (conclusion) and L519 (the caption of Figure 4). A candidate that patches three of them leaves the fourth wrong in the accepted version, so one block is filed per site. Each search string was verified against the frozen manuscript with `grep -Fc`, which returns exactly `1` for all four.

| # | site | `grep -Fc` |
| - | ---- | ---------- |
| 1 | L57, abstract | 1 |
| 2 | L253, body | 1 |
| 3 | L372, conclusion | 1 |
| 4 | L519, Figure 4 caption | 1 |

The regenerated bracket is `[7.0, 9.0]`, the shape fit `8.10 [7.78, 8.37]` and the grid bracket `[7.0, 8.0]` (`R04b_ratio_vs_nu.csv` :: `ratio`). The analytic crossing `4.7` reproduces at D0 and is not touched; only the *measured* crossing moves.

## Edit 1 — L57, the abstract

<<< SEARCH
~~~~~~~~~latex
overtakes it below a measured $\nu^{\star} \approx 4.9$ degrees of freedom, precisely where parametric estimation is most fragile
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
overtakes it below a measured $\nu^{\star}$ bracketed in $[7, 9]$ degrees of freedom, precisely where parametric estimation is most fragile
~~~~~~~~~
>>> END OF BLOCK

## Edit 2 — L253, the body

<<< SEARCH
~~~~~~~~~latex
crosses unity at a measured $\nu^{\star} \approx 4.9$, above the analytic $4.7$
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
crosses unity at a measured $\nu^{\star}$ in $[7, 9]$ (shape fit $8.10$, $95\%$ interval $[7.78, 8.37]$), above the analytic $4.7$
~~~~~~~~~
>>> END OF BLOCK

## Edit 3 — L372, the conclusion

<<< SEARCH
~~~~~~~~~latex
inverting below a measured $\nu^{\star} \approx 4.9$ (analytic $4.7$ for the exactly standardized ideal)
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
inverting below a measured $\nu^{\star}$ in $[7, 9]$ (analytic $4.7$ for the exactly standardized ideal)
~~~~~~~~~
>>> END OF BLOCK

## Edit 4 — L519, the caption of Figure 4

<<< SEARCH
~~~~~~~~~latex
crossing unity at a measured $\nu^{\star} \approx 4.9$ (analytic $4.7$ for the exactly standardized ideal), below which the sign filter overtakes parametric standardization
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
crossing unity at a measured $\nu^{\star}$ in $[7, 9]$ (analytic $4.7$ for the exactly standardized ideal), below which the sign filter overtakes parametric standardization
~~~~~~~~~
>>> END OF BLOCK

## Scope

The four edits are disjoint and commute. What is contradicted is the location of the measured crossing. Not contradicted: the whitening property, the exactness of the Concept threshold, the analytic crossing at `4.6788`, the absence of a second crossing above `nu = 7`, and no proposition of v87. `R04b_v87_oracle_tracks_analytic.md` holds the oracle clause of L253 and consumes a disjoint string; `R04b_v87_estimation_cost.md` holds the `0.3` of L253 and likewise.
