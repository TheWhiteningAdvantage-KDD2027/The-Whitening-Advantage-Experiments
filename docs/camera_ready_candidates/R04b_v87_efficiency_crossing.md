# Camera-ready candidate — Efficiency crossing point correction, Section "Discussion", Abstract, and "Contributions"

| Field               | Value                                                       |
| ------------------- | ----------------------------------------------------------- |
| **Status**          | **PARKED — do not apply**                                   |
| Target file         | `articleB_whitening_v87.tex` (submitted 2026-07-27, frozen) |
| Trigger             | Acceptance notification only                                |
| Evidence            | R04b (12-point nu grid, full refinement)                   |
| Register entry      | `docs/DEVIATIONS.md`, entry `R04b-efficiency-crossing`     |
| Blocking dependency | none                                                        |

**Why this is not applied now.** The manuscript is under review and cannot be edited. The KDD 2027 Research Track allocates one additional content page to accepted papers for exactly this kind of revision, so budget is not the constraint; timing is.

**What is being corrected.** The manuscript states that the efficiency crossing occurs at `nu* ~ 4.9`, precisely where parametric estimation is most fragile. R04b demonstrates that this value is falsified: the crossing is enclosed by `[7, 9]` with 95% confidence and estimated at `8.10 [7.78, 8.37]` by the primary shape-fit estimator. The value `8.1` lies outside the moment singularity `nu < 8` that the original gloss appeals to, and the oracle crossing at `4.47 [4.31, 4.57]` is the only claim of this family that survives.

<<< SEARCH
~~~~~~~~~latex
an efficiency crossing at nu* ~ 4.9, precisely where parametric estimation is most fragile
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
an efficiency crossing enclosed by [7, 9] with 95% confidence, estimated at 8.10 [7.78, 8.37]
~~~~~~~~~
>>> END BLOCK

---

<<< SEARCH
~~~~~~~~~latex
overtakes it below a measured nu* ~ 4.9
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
overtakes it in the interval [7, 9]
~~~~~~~~~
>>> END BLOCK
