# Camera-Ready Candidate: R04b_v87_estimation_cost

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** `R04b-estimation-cost`

**Target file: `articleB_whitening_v87.tex`**

<<< SEARCH
~~~~~~~~~latex
so the extra $0.3$ degrees of freedom is what a finite warm-up costs the parametric route
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
so the extra $3.62$ $[3.31, 3.92]$ degrees of freedom is what a finite warm-up costs the parametric route
~~~~~~~~~
>>> END OF BLOCK

`$0.3$` occurs exactly once in the frozen manuscript, at L253 (`grep -Fc` = 1 for `$0.3$` and
for the full search string above); the estimation cost is printed at that one site and nowhere
else. `degrees of freedom` occurs four times (L57, L253, L343, L518) and is not a usable anchor
on its own.
