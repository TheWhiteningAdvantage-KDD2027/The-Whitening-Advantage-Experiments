# Reference artefacts — historical witness of the submitted campaign

The files under `data/reference/RXX/` are **outputs of the campaign submitted on 2026-07-27**,
produced by the pipeline that predates the FAIR hardening of this repository. They are kept
here so that the deviation classification of `docs/DEVIATIONS.md` can be recomputed by code
rather than asserted from a printed table.

**They are not outputs of this repository.** No script in this repository writes to
`data/reference/`. They must never be regenerated, overwritten, or reconciled with a
regenerated result. The files are stored read-only for that reason.

**Their role is classification, never acceptance.** A witness value is the "published value"
column of a D0/D1/D2/D3 comparison. It is never the anchor of a blocking assertion: the
hardening of a defect in the submitted code is expected to move values, and a cell-by-cell
equality gate against the witness would convert every legitimate correction into a test
failure whose only exit is a widened tolerance.

**Read them with `float_precision='round_trip'`, on both sides of any comparison.** They were
written by `pandas.DataFrame.to_csv` under its default float formatting, without
`float_format='%.17g'`. The fast float parser of pandas is not correctly rounded and commonly
returns a value one ULP away from the true one, which manufactures a drift that does not exist
or masks one that does.

## Register

| Directory              | Files                                                    | Produced by                                                  |
| ---------------------- | -------------------------------------------------------- | ------------------------------------------------------------ |
| `data/reference/R03/`  | `protocol_1a_fpr_cusum.csv`, `protocol_1b_fpr_adwin.csv` | `Priorite_2_protocol_mission2.py`, protocols 1A and 1B        |
| `data/reference/R05/`  | `protocol_17a_scale_add_vs_gamma.csv`                    | `Priorite_17_rerun_scale_gamma.py`                            |
| `data/reference/R05/`  | `protocol_18b_..._2e5.csv`, `protocol_18b_..._3e6.csv`   | `Priorite_18b_scale_add_vs_width_multigamma.py`, two budgets  |
| `data/reference/R11/`  | `Priorite_12_multi_detector.py`, `Priorite_12_multi_detector.log` | the submitted multi-detector campaign (v87 Figures 11 and 15) |
| `data/reference/R16/`  | `Priorite_16_regime_census.py`, `Priorite_20_sign_floor.py` and both `.log` files | the submitted regime-census campaign (v87 L260, L329, L331) |
| `data/reference/R16/`  | `protocol_10b_regime_census_refined.csv`, `protocol_10c_split_report.csv`, `protocol_10d_boundary_convention_delta.csv` | `Priorite_16_regime_census.py` |
| `data/reference/R16/`  | `protocol_20a_sign_floor.csv`, `protocol_20b_census_feasibility_vs_gamma.csv` | `Priorite_20_sign_floor.py` |

`data/reference/R11/` holds no CSV. The submitted campaign wrote its tables beside its figures and
they were not preserved; what is vendored is the script itself and its console log. The script is
read at run time by control C8 of `exp_R11_multi_detector.py`, which asserts that six primitives are
byte-identical to it and that the seventh differs only above its RNG construction, so the file is an
input of the experiment and not merely an archive. The log supplies the submitted PHT thresholds,
the submitted linear slopes and the submitted execution cost, all of which the deviation table of
`AUDIT_R11.md` classifies against. Whether an executable belongs under `data/reference/` is the
question `AUDIT_R06.md` §8.4 already poses for `data/reference/R06/`; it is not settled here.

`data/reference/R16/` holds both the scripts and their CSVs. The scripts are read at run time by
control C8 of `exp_R16_regime_census_a.py` and `_b.py`, which assert that six dating and
divergence primitives are byte-identical to `Priorite_16_regime_census.py`, so those files are
inputs of the experiment and not merely an archive — the same situation as `data/reference/R11/`.
`Priorite_16_regime_census.log` carries the SPY dating substitution at its line 3 and is the
artefact that fixes what the delivered script did and did not announce; `docs/DEVIATIONS.md`
`R16-dating-misdescription` classifies against it.

Two subdirectories depart from the rule above and are signposted rather than listed here:
`data/reference/R05/superseded/` holds an artefact of a design **abandoned before submission**,
and `data/reference/R16/superseded/` a census **replaced before submission** by the multi-scale
refinement that produced the published one. Neither supports a published claim and neither is a
classification witness. Each has its own `README.md` stating the grounds.

The `protocol_*` naming of the submitted pipeline is preserved deliberately. The `RXX_*`
naming convention is reserved for artefacts produced by this repository, and conflating the
two would make the origin of a file depend on where it happens to sit.
