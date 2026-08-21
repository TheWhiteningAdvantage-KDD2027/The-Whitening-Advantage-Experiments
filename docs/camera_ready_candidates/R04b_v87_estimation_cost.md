# Camera-ready candidate — Estimation cost correction, Section "Discussion", Abstract, and "Contributions"

| Field               | Value                                                       |
| ------------------- | ----------------------------------------------------------- |
| **Status**          | **PARKED — do not apply**                                   |
| Target file         | `articleB_whitening_v87.tex` (submitted 2026-07-27, frozen) |
| Trigger             | Acceptance notification only                                |
| Evidence            | R04b (12-point nu grid, full refinement)                   |
| Register entry      | `docs/DEVIATIONS.md`, entry `R04b-efficiency-crossing`     |
| Blocking dependency | none                                                        |

**Why this is not applied now.** The manuscript is under review and cannot be edited. The KDD 2027 Research Track allocates one additional content page to accepted papers for exactly this kind of revision, so budget is not the constraint; timing is.

**What is being corrected.** The manuscript states that the finite warm-up costs 0.3 degrees of freedom. R04b measures this cost as `3.62 [3.31, 3.92]` by the shape-fit route and `3.22 [2.52, 3.82]` by the model-free route. All three intervals exclude `0.3` by a wide margin, demonstrating that the mechanism v87 gives is correct in direction but wrong in magnitude by an order of magnitude. The cost arises because Eco-L1 must identify a persistent GARCH from 500 observations at Gamma = 11.58, where the submitted campaign ran at Gamma = 1.105 with almost no persistence to estimate.

<<< SEARCH
~~~~~~~~~latex
finite warm-up costs 0.3 degrees of freedom
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
finite warm-up costs 3.62 [3.31, 3.92] degrees of freedom
~~~~~~~~~
>>> END BLOCK

---

<<< SEARCH
~~~~~~~~~latex
0.3 degrees of freedom
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
3.62 [3.31, 3.92] degrees of freedom
~~~~~~~~~
>>> END BLOCK
