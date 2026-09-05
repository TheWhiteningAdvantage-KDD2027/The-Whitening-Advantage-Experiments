# Superseded artefacts — a census replaced before submission

This directory holds an output of an R16 design that was **replaced before the manuscript was
submitted on 2026-07-27**. That is a different status from the files one level up in
`data/reference/R16/`, which are outputs of the submitted campaign and which support published
claims. Nothing here supports a claim of `articleB_whitening_v87.tex`.

## `protocol_10a_regime_census.csv`

**Produced by** an earlier revision of `Priorite_16_regime_census.py`, the delivered version of
which is vendored one level up. The exact revision is not in the attachment bundle and is not
guessed here. Fifty-two rows, eighteen columns.

**It is not the published census.** `protocol_10b_regime_census_refined.csv` carries **66** rows,
and **every downstream file of the submitted campaign carries 66**: `protocol_10d_boundary_
convention_delta.csv` (66), `protocol_20a_sign_floor.csv` (66) and `protocol_20b_census_
feasibility_vs_gamma.csv` (`n_phases = 66` on all six rows). v87 L329 prints `$66$ phases` and
`$53$ of $66$`. The refined census is therefore the source of the published numbers, and this
file is its predecessor.

**What the 14 extra rows are.** Read with `float_precision='round_trip'`, per ticker:

| ticker | `protocol_10a` | `protocol_10b` | of which `source_scale == MESO_SPLIT` in `10b` |
| ------ | -------------- | -------------- | ---------------------------------------------- |
| SPY    | 30             | 30             | 0                                              |
| PFF    | 5              | 7              | 3                                              |
| VNQ    | 6              | 18             | 11                                             |
| BWX    | 11             | 11             | 0                                              |
| total  | **52**         | **66**         | **14**                                         |

The row difference, 14, is exactly the number of `MESO_SPLIT` rows in `10b` — the phases the
hierarchical MACRO/MESO merge introduces by offering a MACRO phase longer than 400 trading days
to the 63-day filter. `protocol_10a` **has no `source_scale` column at all**, which is the
schema-level trace of the same thing: it predates the multi-scale refinement.

**The relation is not a strict refinement, and this is stated rather than implied.** The
per-ticker totals above line up, but the MACRO boundaries themselves also moved: nine phase
intervals present in `10a` appear nowhere in `10b` — three on PFF, four on VNQ and two on BWX —
so `10a` is not a sub-partition of `10b` obtained by removing the MESO splits. Both the dating
and the refinement differ. What can be said from the artefacts alone is that `10a` is an earlier
census with fewer phases and no scale column; what produced each boundary difference is not
established here.

**No script in this repository regenerates it.** `exp_R16_regime_census_a.py` implements the
delivered design only, in three explicitly named dating arms, and emits no counterpart to this
file.

**Why it is kept.** As a trace of the census the study ran before the multi-scale refinement, and
on that basis only. It is not a witness for classification, not an anchor for any test, and not a
target for any regenerated artefact. It is read once, by `exp_R16_regime_census_b.py`, as one of
the four definitional variants tested against v87 L329's `55--92\%` floor-fraction envelope —
it yields `[45.7%, 95.9%]`, which is not that envelope either, and the variant is logged as
excluded rather than as an explanation.

## Reading

As for every file under `data/reference/`, read with `float_precision='round_trip'` on both
sides of any comparison. See `data/reference/README.md`.
