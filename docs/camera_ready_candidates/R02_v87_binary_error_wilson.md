# Camera-ready candidate — Binary error rate and Wilson interval, Section "Empirical Boundaries"

| Field               | Value                                                         |
| ------------------- | ------------------------------------------------------------- |
| **Status**          | **PARKED — do not apply**                                     |
| Target file         | `articleB_whitening_v87.tex` (submitted 2026-07-27, frozen)   |
| Trigger             | Acceptance notification only                                  |
| Evidence            | R02 (360 independent streams, 128-bit seeding)                |
| Register entry      | `docs/DEVIATIONS.md`, entry `R02-binary-error-rate`           |
| Cost                | Numerical update only, no textual change                      |
| Blocking dependency | none                                                         |

**Why this is not applied now.** The manuscript is under review and cannot be edited. The numerical values in the LaTeX macros will be updated in camera-ready based on the corrected campaign.

**What is being corrected.** The pooled binary-error rejection rate and Wilson confidence interval shift due to 128-bit seeding and corrected river dependency. The qualitative claim (nominal level covered) remains valid.

<<< SEARCH
~~~~~~~~~latex
and already over-reject on the i.i.d.\ arm ($9.2\%$), where $t_7$ innovations deprive $\varepsilon_t^2$ of a fourth moment and the $\chi^2$ approximation fails; the binary errors hold the nominal level in every regime ($3.3$--$5.0\%$; $4.4\%$ pooled, $95\%$ Wilson $[2.8, 7.1]\%$), even through the finite-sample transient of online learning (Figure~\ref{fig:ljungbox}).
~~~~~~~~~

=== REPLACE WITH >>>
~~~~~~~~~latex
and reject at $\RTwoDataRejectIid\%$ on the i.i.d.\ arm; the binary errors hold the nominal level in every regime ($\RTwoConceptRejectMin\%$--$\RTwoConceptRejectMax\%$; $\RTwoConceptRejectPooled\%$ pooled, $95\%$ Wilson [$\RTwoConceptWilsonLow\%$, $\RTwoConceptWilsonHigh\%$]\%), even through the finite-sample transient of online learning (Figure~\ref{fig:ljungbox}).
~~~~~~~~~
>>> END BLOCK
