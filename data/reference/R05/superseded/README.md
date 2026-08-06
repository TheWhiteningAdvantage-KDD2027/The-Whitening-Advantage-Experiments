# Superseded artefacts — retired before submission

This directory holds outputs of an R05 design that was **abandoned before the manuscript was
submitted on 2026-07-27**. That is a different status from the files one level up in
`data/reference/R05/`, which are outputs of the submitted campaign and which support published
claims. Nothing here supports a claim of `articleB_whitening_v87.tex`.

## `protocol_18a_scale_add_vs_width.csv`

**Produced by** the script the R05 bundle refers to only as `Priorite_18`, the single-penalty
precursor of `Priorite_18b_scale_add_vs_width_multigamma.py`, whose docstring records that it
reuses `Priorite_18`'s primitives verbatim. The file itself is not in the bundle, so its exact
name is not known here and is not guessed. Ten rows, eighteen columns.

**Its design was formally retired** by the figure generator that succeeded it. The comment at
line 60 of `Priorite_18c_generate_fig_scale_orthogonality.py` reads, verbatim:

> `# Abandon formel de l'ancien CSV protocol_18a (censure par horizon statique et grille absolue).`

— that is, the static monitoring horizon censored the widest ramps, and the absolute `w` grid
was not comparable across penalties. `Priorite_18b` replaced both: a horizon solved as a fixed
point and shared by every penalty, and a `w` grid held fixed in units of `w*(Gamma)`.

**No script in this repository regenerates it.** Its generator, `Priorite_18.py`, is not part
of the R05 attachment bundle and is not vendored here. `exp_R05_scale_law_b.py` implements the
`Priorite_18b` design only, and emits no counterpart to this file.

**It cannot support the five-penalty claim of v87.** `sec:scaling_validation` describes the
ramp campaign as "five penalties spanning `Gamma in [2, 20]`, all monitored over one common
horizon". This file carries a **single** penalty, `Gamma = 11.58`, on all ten of its rows.
Read in `float_precision='round_trip'`, its columns `lambda_star_Data`,
`lambda_star_Concept`, `lambda_iid_H`, `FPR_Data_val`, `FPR_Concept_val`, `DetRate_Concept`
and `ADD_Concept` are constant row to row; only `w`, `regime`, `ADD_Data`, `SEM_Data` and
`DetRate_Data` vary. It is a one-penalty width sweep, not a penalty comparison.

**Why it is kept.** As a trace of the extent of the campaigns run during the study, and on
that basis only. It is not a witness for classification, not an anchor for any test, and not a
target for any regenerated artefact.

## Reading

As for every file under `data/reference/`, read with `float_precision='round_trip'` on both
sides of any comparison. See `data/reference/README.md`.
