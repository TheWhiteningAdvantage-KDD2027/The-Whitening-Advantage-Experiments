# Camera-ready candidate — compute and implementation figures

- **Status:** PARKED — do not apply
- **Trigger:** acceptance notification, 14 November 2026
- **Register entry:** carried as D2 in `docs/DEVIATIONS.md` under `R00-repo-compute-timings` (three moving numerals: overall figure, iso-FPR race, and scaling campaign timing; plus reconciliation of the $H = 3\times10^6$ scope)
- **Manuscript site:** Appendix `\section{Reproducibility}\label{app:repro}`, paragraph `\paragraph{Compute and implementation.}`

## What was measured

The repository was executed end to end twice consecutively from a clean `results/` tree on the hardware specified in the manuscript: an AMD EPYC 8224P (24 cores, 48 threads, 192 GB RAM, no GPU). All 169 generated artefacts are byte-identical across runs. Each run required **128 minutes** of wall-clock time for the complete pipeline, which includes diagnostic arms and supplementary streams not reported in the paper.

Per-campaign wall-clock durations are derived from the ISO 8601 timestamps recorded on each line of the execution logs.

**Summing individual log durations overstates wall-clock time due to hierarchical logging structures.** Adding first-to-last timestamps across all 36 log files yields 190.4 min versus the measured 128.0 min wall-clock time. Three factors account for this difference:
1. *Uninvoked logs (1.0 min):* Three historical logs remain on disk from auxiliary test runs not called by `run_all.sh` (`R01_..._legacy_blas.log`, `R03_..._fast.log`, and `R04b_..._fast.log`).
2. *Composite orchestrators (5.0 min):* Master runners in R08 (2.6 min) and R13 (2.4 min) write enclosing session logs alongside their constituent sub-stage logs, double-counting both stages.
3. *Sequential driver encapsulation in R05 (58.5 min):* `run_experiment_R05.sh` executes a single Python driver (`exp_R05_scale_law_c.py`) that chains step a (3.9 s), step b at 2e5 (173.3 s), step b at 3e6 (3331.3 s), and step c (0.8 s) sequentially within one process. The driver log (`exp_R05_scale_law_c.log`, 58.5 min) encompasses all sub-stages; summing it alongside the stage logs counts R05's runtime twice.

The remaining 2.1 min reflects test suite execution (`run_tests.sh`, 1.9 min / 113 s) and shell orchestration overhead (0.2 min). All reported benchmarks represent true elapsed wall-clock intervals.

| Benchmark figure                       | Site                          | Measured      | Basis                                                                            |
| -------------------------------------- | ----------------------------- | ------------- | -------------------------------------------------------------------------------- |
| overall paper regeneration, `≈1 h`     | `Compute and implementation.` | **113.7 min** | `run2.log` (128.0 min minus 14.3 min of non-published diagnostic arms and tests) |
| Section 4 iso-FPR race, `≈25 min`      | same                          | **3.8 min**   | `logs/R04_isofpr_race/exp_R04_isofpr_race.log`, first-to-last timestamp          |
| Appendix B scaling campaign, `≈45 min` | same                          | **55.5 min**  | `logs/R05_scale_law/exp_R05_scale_law_b_3e6.log`, first-to-last timestamp        |

All comparisons evaluate identical hardware; all three published figures move.

## Scope reconciliation and publication subtotal

The manuscript's overall estimate of ${\approx}1$\,h reflects an internal scope inconsistency: it characterizes the $H = 3\times10^6$ scaling campaign as unused, while simultaneously citing five numerical results from it in Appendix~\ref{app:scaling} (`AUDIT_R05.md` lines 26--30). Because these values form part of the published evidence, this campaign (55.5 min) cannot be excluded from the reproduction budget.

Deducting only the 14.3 min spent on diagnostic arms that certify no published results (R14, R15, R17 controls, stream R18, and `run_tests.sh`) from the measured 128.0 min yields a published subtotal of 113.7 min (${\approx}2$\,h). The overall figure therefore moves from ${\approx}1$\,h to ${\approx}2$\,h (D2).

## Proposed edit

The opening sentence is patched as an atomic unit, and the scaling sentence is revised to clarify its role in Appendix B:

<<< SEARCH
~~~~~~~~~latex
takes ${\approx}1$\,h of wall-clock time, of which ${\approx}25$\,min is the iso-FPR race of Section~\ref{sec:magnitude}
~~~~~~~~~

=== REPLACE WITH >>>
~~~~~~~~~latex
takes ${\approx}2$\,h of wall-clock time, of which ${\approx}4$\,min is the iso-FPR race of Section~\ref{sec:magnitude}
~~~~~~~~~
>>> END OF BLOCK

<<< SEARCH
~~~~~~~~~latex
The repository also ships a higher-resolution scaling campaign (${\approx}45$\,min) that the paper does not use.
~~~~~~~~~

=== REPLACE WITH >>>
~~~~~~~~~latex
The repository also ships a higher-resolution scaling campaign (${\approx}55$\,min) supporting Appendix~\ref{app:scaling}.
~~~~~~~~~
>>> END OF BLOCK

## Verified

The hardware description, the native QMLE and Fernández–Steel implementations, the post-onset truncation convention (exemplified by PFF 2020-03-18), the two scaling horizons, and the parallelisation schemes via `joblib` and `concurrent.futures` all reproduce reliably and require no modification. `joblib.Parallel` is imported across eight streams, and `concurrent.futures` is instantiated at 29 sites.