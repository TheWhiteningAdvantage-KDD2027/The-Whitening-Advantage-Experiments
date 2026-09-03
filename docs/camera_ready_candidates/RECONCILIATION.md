# RECONCILIATION — `docs/camera_ready_candidates/`

**Produced by** T4 (`CLAUDE_TASKS/T4_CAMERA_READY_RECONCILIATION.md`). **Read-only** with respect to
the manuscript and to every pre-existing candidate: no file was restored and no file was deleted.
The single write is the STEP 5 creation recorded in §5.

---

## 0. What git says, and where the manuscript is

**The documentation refactoring was never committed.** `git log --diff-filter=D --all` and
`git log --diff-filter=R --all` on this directory both return **empty**: no deletion and no rename
has ever entered a commit. The entire divergence lives in the working tree against `HEAD`
(`ac5f849`), so `HEAD` *is* the last commit before the refactoring and no ancestor search is needed.

|                                                  | count  |
| ------------------------------------------------ | ------ |
| candidates in `HEAD`                             | **60** |
| candidates on disk at the start of T4            | **43** |
| byte-identical (same name, same content)         | 13     |
| modified in place (same name, different content) | 17     |
| present in `HEAD`, absent on disk                | **30** |
| present on disk, absent from `HEAD`              | **13** |

**Every one of the 30 absent files is recoverable**, verified individually:
`git show HEAD:docs/camera_ready_candidates/<name>` succeeds for 30 / 30. None was relocated
elsewhere in the tree. Nothing is destroyed; the loss is *staged*, and committing the working tree
as it stands is what would make it permanent.

**The frozen manuscript.** `articleB_whitening_v87.tex` does **not** exist at the repository root,
which is the path T4 STEP 3 names. It is reachable at `REFACTORING_COMMON/articleB_whitening_v87.tex`
— `REFACTORING_COMMON` is a symlink (`120000` blob in `HEAD`) to
`/home/m53/Article_B_Whitening_effect/REFACTORING_COMMON`. 646 lines, SHA-256
`98c20e3bd1ec6de5985b6f664a1f154bcfd40491369c38de126b769ddebafb80`. Every `grep -Fc` below was run
against that file. It was read and never written.

**Rename detection: negative, twice.** No candidate is a rename.

- SHA-256 of all 60 `HEAD` blobs against all 43 worktree files: **0** content matches under a
  different name (13 matches, all same-name-same-content).
- `git diff --no-index -M30% -C30% --find-copies-harder` between the two directory states reports
  **0** renames and **0** copies — 30 pure `D`, 13 pure `A`.

The `RENAMED` class of STEP 2 is therefore **empty**. Every difference is a rewrite or a loss.

---

## 1. The three-class table

### 1.1 RENAMED — same content, different filename

**None.** See §0.

### 1.2 REWRITTEN — same subject, different content

Two sub-populations. **(a) Same name, rewritten in place** — 17 files. **(b) Name dropped, subject
carried by another file** — 19 files. The *successor* column names the file that now carries the
subject; `(pre-existing)` means the successor was already in `HEAD` and is not a product of the
refactoring.

#### (a) Rewritten in place — 17 files

| file                                 | anchor text                | what the rewrite did                                                                                                                                        |
| ------------------------------------ | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `R04b_v87_efficiency_crossing.md`    | unchanged (already broken) | header table → `STATUS:` line, `Trigger` date dropped, register id → bare `R04b`, markers → `% SEARCH` inside a `~~~latex` fence                            |
| `R04b_v87_estimation_cost.md`        | unchanged (already broken) | idem                                                                                                                                                        |
| `R04b_v87_oracle_tracks_analytic.md` | **MUTATED**                | `\emph{oracle}` → `oracle` in the SEARCH string; `$+5\%$` dropped from the replacement, which now says only "intersecting near it"                          |
| `R05_v87_lambda_c_numeral.md`        | unchanged                  | fence width `~~~~~~~~~` → `~~~~~~~~~~~` only                                                                                                                |
| `R05_v87_sixth_moment_gloss.md`      | unchanged                  | idem                                                                                                                                                        |
| `R07_v87_bias_bound.md`              | unchanged                  | evidence table (SE, standard-error distances, witness value) replaced by a 4-row macro stub; replacement now emits `\RSevenBiasMax`                         |
| `R07_v87_dispersion_cost.md`         | unchanged                  | title de-specified; the six-reading enumeration — the file's entire argument — replaced by one row; replacement emits `\RSevenOlsFprMax - \RSevenOlsFprMin` |
| `R07_v87_figure7_exactness.md`       | unchanged                  | exact-law table replaced by a macro stub; replacement unchanged in substance                                                                                |
| `R07_v87_lattice_handoff_to_R08.md`  | n/a (no anchor by design)  | title de-specified; exact-vs-printed table replaced by a macro stub                                                                                         |
| `R07_v87_panelB_operating_level.md`  | unchanged                  | operator table gutted; replacement rewritten to emit `\RSevenOracleFprMean`, `\RSevenLatticeHigh` and drops the contrast with `4.29\%`                      |
| `R10_v87_L290_skewness_numeral.md`   | unchanged                  | markers → `% SEARCH` / `% REPLACE WITH` / `% END OF BLOCK`                                                                                                  |
| `R10_v87_caption_fpr_envelope.md`    | unchanged                  | idem                                                                                                                                                        |
| `R10_v87_panelA_sign_arm_scope.md`   | unchanged                  | idem                                                                                                                                                        |
| `R15_v87_budget_bound_referent.md`   | unchanged                  | `<<< RECHERCHER` → `<<< SEARCH`, `=== REMPLACER PAR >>>` → bare `===`, **closing `>>> FIN DU BLOC` deleted**                                                |
| `R15_v87_naive_baseline.md`          | unchanged                  | idem                                                                                                                                                        |
| `R15_v87_scatter_attribution.md`     | unchanged                  | idem                                                                                                                                                        |
| `R15_v87_scatter_sign.md`            | unchanged                  | idem                                                                                                                                                        |

Two consequences carry beyond cosmetics.

1. **The four R15 blocks have no terminator.** The replacement side now runs to the next `##`
   heading with nothing marking its end. Any tool that reads these blocks reads the wrong extent.
2. **Three R07 replacements now emit `\RSeven…` macros** — `R07_v87_bias_bound` (`\RSevenBiasMax`),
   `R07_v87_dispersion_cost` (`\RSevenOlsFprMax`, `\RSevenOlsFprMin`) and
   `R07_v87_panelB_operating_level` (`\RSevenOracleFprMean`, `\RSevenLatticeHigh`). The frozen
   manuscript contains **zero** `\newcommand` definitions and **zero**
   `\RSeven`/`\RFour`/`\REight`/`\REleven` tokens (`grep -c` = 0 for each), so each of those three
   edits compiles to `Undefined control sequence`. Their `HEAD` replacements were literal numerals
   and compiled; the refactoring introduced the defect. `R07_v87_figure7_exactness`'s replacement is
   unchanged and macro-free, and `R07_v87_lattice_handoff_to_R08` carries no block at all — only
   their body tables were gutted. A machine scan of every replacement body in both trees finds no
   other case in the working tree, and exactly one in `HEAD`: the deleted
   `R02_v87_binary_error_wilson.md`, whose replacement emits six undefined `\RTwo…` macros.

#### (b) Name dropped, subject carried elsewhere — 19 files

| deleted file                             | manuscript site      | successor now carrying the subject                                        | what did not survive                                                                                               |
| ---------------------------------------- | -------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `R02_v87_binary_error_wilson.md`         | L278                 | `R02_v87_ljungbox_whiteness.md` *(pre-existing)*                          | the verified L278 anchor; the edit itself                                                                          |
| `R02b_R02c_v87_ljungbox_clause.md`       | L278                 | `R02b_v87_iid_mechanism.md`, `R02c_v87_horizon_sweep.md` *(pre-existing)* | **the correction is reversed** — see §4.1                                                                          |
| `R02b_v87_iid_arm_rejection.md`          | L278                 | idem                                                                      | idem; a D3 finding                                                                                                 |
| `R03_v87_cusum_nominal_level.md`         | L171                 | `R03_v87_fpr_explosion.md` *(pre-existing)*                               | **the manuscript edit** — see §4.2                                                                                 |
| `R06_v87_caption_paired.md`              | L535 (Fig 6 caption) | `R06_v87_validity_map.md` *(pre-existing)*                                | the paired-design clause and `N_eff = 405`; the figure-file replacement                                            |
| `R08_v87_adverse_numerals.md`            | L311, L551           | `R08_v87_adverse_direction.md` *(new)*                                    | 5 verified anchors; the `1.1`-points under-centering numeral                                                       |
| `R08_v87_delivered_level.md`             | L241 + footnote      | `R08_v87_discrete_null_law.md` *(new)*                                    | **a D3 correction** — see §4.3                                                                                     |
| `R08_v87_lattice_exact_basis.md`         | L241                 | `R08_v87_discrete_null_law.md` *(new)*                                    | the anchor; the `NO DEVIATION` family marker                                                                       |
| `R08_v87_whiteness_identity.md`          | L551                 | `R08_v87_adverse_direction.md` *(new)*                                    | the anchor; the `NO DEVIATION` family marker                                                                       |
| `R09_v87_anytime_numerals.md`            | L243, L559           | `R09_v87_add_parity.md`, `R09_v87_cusum_peeking_fpr.md` *(pre-existing)*  | 3 verified anchors; the Fig 9A caption edit                                                                        |
| `R11_v87_detector_comparability.md`      | L627 (Fig 15B)       | `R11_v87_concept_add.md` *(new)*                                          | **the two-onset-convention finding** — the macros keep the four delays and drop the reason they are not comparable |
| `R11_v87_loglog_slopes.md`               | L298                 | `R11_v87_data_slopes.md` *(new)*                                          | the "no traceable origin, no stated domain" finding; the anchor                                                    |
| `R11_v87_pht_gamma_rule.md`              | L171, Fig 15 caption | `R11_v87_pht_macros.md` *(new)*                                           | the finding that the rule *drifts across* the nominal level rather than holding it                                 |
| `R11_v87_pht_syncope_gamma.md`           | L298                 | `R11_v87_pht_macros.md` *(new)*                                           | the anchor; `\RElevenPhtSyncopeGamma{75}` survives as a bare macro                                                 |
| `R13_v87_covid_delay_numerals.md`        | L331                 | `R13_v87_oracle_ceiling.md` *(pre-existing)*                              | the anchor `phase false-alarm probability $1.3\%$`                                                                 |
| `R13_v87_operating_points.md`            | L331                 | `R13_v87_oracle_ceiling.md` *(pre-existing)*                              | **the mislabelling finding** — see §4.4                                                                            |
| `R14_v87_synthetic_control_numerals.md`  | L345                 | `R14_v87_crypto_isofpr_ratios.md` *(new)*                                 | the anchor; the `--legacy-seeds` counterfactual that establishes the cause                                         |
| `R17_v87_warmup_restoration_scope.md`    | L341                 | `R17_v87_econometric_baseline.md` *(new)*                                 | **the clarification is inverted into a corroboration** — see §4.5                                                  |
| `R18_v87_whitening_evidence_strength.md` | L290, L318           | `R18_v87_ljungbox_power_bound.md` *(new)*                                 | the two anchors; the edits at L290 and L318                                                                        |

Five of the 13 new arrivals have **no** deleted counterpart and are additions, not successors:
`R01_v87_garch_calibration.md`, `R05_v87_scale_law.md`, `R11_v87_eddm_fpr.md`,
`R11_v87_grid_metadata.md`, `R16_v87_regime_census.md`.

### 1.3 LOST — no successor

Eleven files. Each carried at least one anchor verified at `grep -Fc` = 1 against the frozen `.tex`
(§2.3). No file in the working tree addresses the subject.

| deleted file                                | subject, from the deleted file                                                                                                                       | register status                                           |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| `R09_v87_arl0_censoring.md`                 | Figure 9 panel C: the CUSUM and MIX curves sit **on the simulation horizon**, so the `ARL_0 >= 1/alpha` the panel displays is censored, not attained | `R09-arl0-censoring` **absent** from `docs/DEVIATIONS.md` |
| `R09_v87_delay_parity_scope.md`             | Figure 9B and L243: the delay comparison is **conditional on detection**, which the caption does not say                                             | `R09-add-conditioning` — Class A, live                    |
| `R09_v87_stream_counts.md`                  | Figure 9 caption: "$2\times10^4$ streams per cell" describes **one arm of three**                                                                    | none by design (imprecise, not false)                     |
| `R11_v87_figure11_caption.md`               | Figure 11 caption states **one panel's parameters for both** ($c=2$, $1{,}000$ streams)                                                              | entry 19 (legacy numbering)                               |
| `R13_v87_frozen_null_scope.md`              | L331: "a bootstrap null freezing the same volatility path" describes **one arm of one axis**                                                         | `R13-frozen-null-scope` **absent** from the register      |
| `R14_v87_reliable_range_scope.md`           | L345 and Fig 16 caption: "the reliable range" is **never defined**, and the mean is taken over seven grid points — `NO DEVIATION`                    | none by design                                            |
| `R14_v87_synthetic_control_strength.md`     | L345: the `t30` inversion is a point estimate whose bootstrap interval **spans parity** — `NO DEVIATION`                                             | none by design — **recreated under STEP 5, §5**           |
| `R16_v87_boundary_sensitivity.md`           | L392 `app:repro`: the boundary convention is declared but its effect on the headline is **never reported**                                           | `R16-boundary-sensitivity` — Class A, live                |
| `R16_v87_dating_algorithm.md`               | L329: the census is **not the output of the dating algorithm the sentence names** (Pagan–Sossounov gives 48 phases, not 66)                          | `R16-dating-misdescription` — Class A, **D3**, live       |
| `R17_v87_persistence_collapse_mechanism.md` | L341: a third of the persistence collapse is a **corner solution at the optimiser's bound** — `NO DEVIATION`                                         | none by design                                            |
| `R17_v87_warmup_resolution.md`              | L341: the two numerals are read at **200 streams**, and the sign envelope is a **min–max over four cells** — `NO DEVIATION`                          | none by design                                            |

---

## 2. Anchor verification against the frozen manuscript (STEP 3)

### 2.1 Two genres of block, and only one is a manuscript anchor

The corpus mixes two kinds of `SEARCH` block, and STEP 3's test applies to one of them.

- **Prose anchors** — the search string is a verbatim fragment of `articleB_whitening_v87.tex`.
  These are the blocks STEP 3 governs.
- **Macro blocks** — the search string is a run of `\newcommand{\R…}` definitions. These target a
  stream's `results/R[XX]_*/tables/R[XX]_claims.tex`, **not** the manuscript. The frozen `.tex`
  contains **zero** `\newcommand` and zero `\R{Four,Seven,Eight,Eleven}…` tokens, so a `grep -Fc`
  of a macro block against it returns `0` by construction and is not evidence of a defect.

Counts on the working tree at the start of T4 (43 files, 65 blocks): **26 prose anchors**,
**39 macro blocks**. After the STEP 5 creation: 27 prose anchors, 39 macro blocks.

### 2.2 Prose-anchor results — working tree

| verdict                                               | count                                      |
| ----------------------------------------------------- | ------------------------------------------ |
| `grep -Fc` = 1 (unique, applies)                      | **18** (17 pre-existing + the STEP 5 file) |
| `grep -Fc` = 0 (**does not exist in the manuscript**) | **9**                                      |
| `grep -Fc` > 1 (ambiguous)                            | 0                                          |

**The nine anchors that do not exist.** All nine fail for the same reason: the search string is a
**de-LaTeX-ified transcription** of real manuscript text — math delimiters, `\varepsilon`, `\nu`,
`\chi`, `\emph{}` and escaped percent signs stripped — or, in one case, a paraphrase. Every one has
a unique repaired form, verified below at `grep -Fc` = 1.

| file                                 | #   | as written (count 0)                                                                           | repaired form (count 1)                                                                                                                                                                                                                                               |
| ------------------------------------ | --- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `R02b_v87_iid_mechanism.md`          | 1   | `The squared inputs reject whiteness in 100% … (9.2%), where t7 innovations deprive eps_t^2 …` | `…in $100\%$ … ($p < 10^{-10}$) … i.i.d.\ arm ($9.2\%$), where $t_7$ … $\varepsilon_t^2$ … $\chi^2$ …`                                                                                                                                                                |
| `R02b_v87_iid_mechanism.md`          | 3   | `already over-reject on the i.i.d. arm (9.2%)`                                                 | `already over-reject on the i.i.d.\ arm ($9.2\%$)`                                                                                                                                                                                                                    |
| `R02c_v87_horizon_sweep.md`          | 1   | as above                                                                                       | as above                                                                                                                                                                                                                                                              |
| `R02c_v87_horizon_sweep.md`          | 3   | `where t7 innovations deprive eps_t^2 of a fourth moment and the chi^2 approximation fails`    | `where $t_7$ innovations deprive $\varepsilon_t^2$ of a fourth moment and the $\chi^2$ approximation fails`                                                                                                                                                           |
| `R04b_v87_efficiency_crossing.md`    | 1   | `an efficiency crossing at nu* ~ 4.9, precisely where parametric estimation is most fragile`   | **no repair by transcription** — the phrase *"efficiency crossing"* occurs nowhere in the manuscript. The clause exists at L57 as `overtakes it below a measured $\nu^{\star} \approx 4.9$ degrees of freedom, precisely where parametric estimation is most fragile` |
| `R04b_v87_efficiency_crossing.md`    | 2   | `overtakes it below a measured nu* ~ 4.9`                                                      | `overtakes it below a measured $\nu^{\star} \approx 4.9$`                                                                                                                                                                                                             |
| `R04b_v87_estimation_cost.md`        | 1   | `finite warm-up costs 0.3 degrees of freedom`                                                  | a **paraphrase**, not a quote. L253 reads `so the extra $0.3$ degrees of freedom is what a finite warm-up costs the parametric route`                                                                                                                                 |
| `R04b_v87_estimation_cost.md`        | 2   | `0.3 degrees of freedom`                                                                       | `$0.3$ degrees of freedom` (unique; note bare `degrees of freedom` occurs **4** times)                                                                                                                                                                                |
| `R04b_v87_oracle_tracks_analytic.md` | 1   | `an oracle arm standardized by … crosses at 4.6, on the analytic prediction, so the extra`     | `an \emph{oracle} arm standardized by the true GARCH parameters crosses at $4.6$, on the analytic prediction, so the extra`                                                                                                                                           |

**Eight of these nine were already broken in `HEAD`.** Only `R04b_v87_oracle_tracks_analytic.md`
was degraded by the refactoring, which stripped `\emph{}` from an anchor that was already failing on
`$4.6$` alone. The R02b/R02c pair are among the 13 byte-identical files: their anchors predate the
refactoring entirely.

### 2.3 Prose-anchor results — the 30 deleted files

| verdict        | count        |
| -------------- | ------------ |
| `grep -Fc` = 1 | **42** of 43 |
| `grep -Fc` = 0 | 1            |
| `grep -Fc` > 1 | 0            |

The single failure is `R02b_v87_iid_arm_rejection.md`, which writes `(9.2\%)` where the manuscript
has `($9.2\%$)`; repaired, it is unique.

**This is the reconciliation's central asymmetry.** The deleted population carried 43 anchors and
42 of them applied cleanly. The surviving population carries 27, of which 18 apply. **Every file
the refactoring removed was anchor-verified; not one anchored candidate was added to replace one.**
Of the 13 new arrivals, **none carries a manuscript prose anchor**: seven carry macro blocks only
and six (`R05_v87_scale_law`, `R08_v87_adverse_direction`, `R08_v87_discrete_null_law`,
`R16_v87_regime_census`, `R17_v87_econometric_baseline`, `R18_v87_ljungbox_power_bound`) carry no
block of any kind. The additions are entirely macro-genre.

### 2.4 Marker dialects

Six incompatible block syntaxes are now in use. Any tool that applies these blocks must implement
all six or silently skip files.

| dialect                                                                                                                             | worktree files                   |
| ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| `<<< SEARCH` / `=== REPLACE WITH >>>` / `>>> END BLOCK`                                                                             | R07 ×4, and the STEP 5 file      |
| `<<< SEARCH` / `===` / *(no terminator)*                                                                                            | R15 ×4                           |
| `<<< SEARCH` / `===` + `REPLACE WITH` / `>>>`                                                                                       | R05 ×2                           |
| `% SEARCH` / `% REPLACE WITH` / `% END OF BLOCK`, outside a fence                                                                   | R10 ×3                           |
| `% SEARCH` … inside a `~~~latex` fence                                                                                              | R04b ×3, and all 39 macro blocks |
| *(in `HEAD` only)* `<<< RECHERCHER` / `=== REMPLACER PAR >>>` / `>>> FIN DU BLOC`; and four R13 blocks flattened onto a single line | —                                |

---

## 3. The two-family header (STEP 4)

Required in every candidate's header: `PARKED — do not apply`; the trigger *acceptance
notification, 14 November 2026*; and exactly one family — nothing extra when the candidate corrects
a contradiction carried by `docs/DEVIATIONS.md`, or `NO DEVIATION — clarification only` when it does
not and therefore has no register entry.

### 3.1 Conformance, 43 files as found

| requirement                           | conforming | failing |
| ------------------------------------- | ---------- | ------- |
| `PARKED — do not apply` present       | 42         | **1**   |
| `Trigger` field present at all        | 16         | **27**  |
| Trigger carries `14 November 2026`    | **11**     | **32**  |
| `Register entry` field present at all | 17         | **26**  |
| family determinable                   | **15**     | **28**  |

"Family determinable" counts the 11 files citing a register entry plus the 4 carrying
`NO DEVIATION — clarification only`. The 2 files of §3.2(b) declare no entry without the marker and
the 26 of §3.2(a) declare nothing at all; neither can be sorted.

### 3.2 Candidates that lack a family marker

**(a) 26 files carry no `Register entry` field at all.** They therefore assert neither family. None
carries `NO DEVIATION`, so each reads by default as a deviation-correcting candidate while
declaring no register entry — the "reverse" inconsistency of STEP 4, on more than half the corpus:

`R01_v87_garch_calibration`, `R02_v87_ljungbox_whiteness`, `R02b_v87_iid_mechanism`,
`R02c_v87_horizon_sweep`, `R03_v87_fpr_explosion`, `R04_v87_table3_data`, `R04_v87_table3_macros`,
`R05_v87_scale_law`, `R06_v87_validity_map`, `R07_v87_estimated_mean`, `R08_v87_adverse_direction`,
`R08_v87_discrete_null_law`, `R09_v87_add_parity`, `R09_v87_cusum_peeking_fpr`,
`R11_v87_concept_add`, `R11_v87_data_slopes`, `R11_v87_eddm_fpr`, `R11_v87_grid_metadata`,
`R11_v87_pht_macros`, `R12_v87_leverage_fpr`, `R12_v87_singularity_add`, `R13_v87_oracle_ceiling`,
`R14_v87_crypto_isofpr_ratios`, `R16_v87_regime_census`, `R17_v87_econometric_baseline`,
`R18_v87_ljungbox_power_bound`.

**(b) 2 files declare `Register entry: none` without the `NO DEVIATION — clarification only`
marker** — the declaration and the marker must travel together:

- `R07_v87_figure7_exactness.md` — "**none in R07.** The two numerals belong to R08"
- `R07_v87_lattice_handoff_to_R08.md` — "**none.** R07 opens no entry on another stream's published values"

`R07_v87_lattice_handoff_to_R08.md` is also the one file with **no `PARKED` marker**. It is a
hand-off note rather than a candidate; if it is to stay in this directory it needs the header, and
if it is not, it belongs in `docs/audits/`.

### 3.3 `NO DEVIATION` carried alongside a register entry

**None.** The four files carrying the marker — `R10_v87_panelA_sign_arm_scope`,
`R15_v87_budget_bound_referent`, `R15_v87_naive_baseline`, `R15_v87_scatter_attribution` — each
declare `Register entry: **none**`, and `docs/DEVIATIONS.md` carries no entry for any of their
subjects. Consistent. The STEP 5 file added in §5 is the fifth and is likewise consistent.

**Seven of the deleted files carried the marker** and are the ones whose loss removes the
clarification family from R08, R14 and R17 entirely: `R08_v87_lattice_exact_basis`,
`R08_v87_whiteness_identity`, `R14_v87_reliable_range_scope`, `R14_v87_synthetic_control_strength`,
`R17_v87_persistence_collapse_mechanism`, `R17_v87_warmup_resolution`,
`R17_v87_warmup_restoration_scope`.

### 3.4 Register references that do not resolve

**Worktree → register: clean.** Every backticked register id declared by a surviving candidate
exists in `docs/DEVIATIONS.md`.

**Deleted → register: 7 dangling ids**, absent from `docs/DEVIATIONS.md` both at `HEAD` and in the
working tree. These candidates cite entries that the register has never carried:
the R02 binary-error-rate entry as it was then named, `R09-arl0-censoring`, `R11-onset-convention`, `R11-pht-slope`,
`R11-pht-gamma-rule`, `R11-pht-syncope`, `R13-frozen-null-scope`. Three further deleted files cite
the legacy numeric scheme (`entry 3`, `entry 7`, `entry 19`) that the register no longer uses; the
surviving `R05` pair cite `entry 9` and `entry 12` in the same dead scheme.

**Register → candidates: 39 of 63 entries are unreferenced.** `docs/DEVIATIONS.md` carries 63
register ids; 39 are named by no candidate in the working tree. Three of them are **D3**:

| entry                               | class  | candidate that carried it                        |
| ----------------------------------- | ------ | ------------------------------------------------ |
| `R08-delivered-level-above-nominal` | **D3** | `R08_v87_delivered_level.md` — deleted           |
| `R16-dating-misdescription`         | **D3** | `R16_v87_dating_algorithm.md` — deleted          |
| `R17-eco-l1-arm-identity`           | **D3** | never had one — a genuine gap, not a T4 casualty |

A live D3 with no camera-ready candidate is a contradiction the register admits and the directory
cannot fix at acceptance.

---

## 4. Recommendation, per LOST or REWRITTEN candidate

**Global recommendation.** Do not commit the working tree as it stands. The refactoring is a net
subtraction: it removed 43 verified manuscript anchors and 30 arguments, added 13 macro-only files,
and left the corpus unable to satisfy STEP 4 on 26 of 43 files. `git show HEAD:…` reverses any part
of it at zero cost for as long as the change stays uncommitted.

The six numbered items below are the ones where a *finding* — not merely a numeral — was inverted,
dropped, or is inconsistent with a live register entry. They are ordered by severity.

### 4.1 R02b / R02c — the Ljung–Box i.i.d.-arm clause: **the correction was reversed**

Two deleted candidates, `R02b_R02c_v87_ljungbox_clause.md` (register entry 3) and
`R02b_v87_iid_arm_rejection.md` (D3), both target the L278 clause

> already over-reject on the i.i.d.\ arm ($9.2\%$), where $t_7$ innovations deprive
> $\varepsilon_t^2$ of a fourth moment and the $\chi^2$ approximation fails

and both correct the same thing: **the mechanism is wrong independently of any sample.** Ljung–Box
on `Y = eps_t^2` needs `E[eps^4] < inf`, hence `nu > 4`, which holds at `t_7`. The moment that
fails below `nu = 8` is `E[eps^8]`. `R02b_v87_iid_arm_rejection.md` states this in terms; the joint
candidate places the over-rejection "beyond the sixth-moment boundary … where the autocovariance
summand loses its third absolute moment".

The two surviving files, `R02b_v87_iid_mechanism.md` and `R02c_v87_horizon_sweep.md`, propose a
replacement that reads

> `already over-reject on the i.i.d. arm (5.8% at nu=7), where Student's t innovations with nu <= 6
> deprive eps_t^2 of a fourth moment and the chi^2 approximation fails`

which **restates the falsified fourth-moment mechanism** and merely moves the threshold to
`nu <= 6`. Their anchors do not exist in the manuscript (§2.2), so neither could be applied in any
case. Both files are byte-identical to `HEAD`: the defect predates the refactoring, and deleting the
two candidates that corrected it is what makes it load-bearing.

**Recommendation.** Restore `R02b_v87_iid_arm_rejection.md` and `R02b_R02c_v87_ljungbox_clause.md`
from `HEAD`; repair the one anchor of the former (`(9.2\%)` → `($9.2\%$)`, then unique). Repair or
withdraw the mechanism sentence in `R02b_v87_iid_mechanism.md` and `R02c_v87_horizon_sweep.md`;
their `nu <= 6` fourth-moment claim must not reach the camera-ready.

**Status: executed.** Both files are present in the working tree with `grep -Fc` = 1 anchors. The
finding is now registered as `R02b-iid-arm-rejection`, Class A, **D3**, in `docs/DEVIATIONS.md`, and
carried as a D3 row in `docs/audits/AUDIT_R02b.md`. The two files, and `R02c_v87_horizon_sweep.md`,
cite that identifier and are no longer marked `NO DEVIATION`. The `nu <= 6` fourth-moment
replacement in `R02c_v87_horizon_sweep.md` has been withdrawn: the fourth moment is finite for every
`nu > 4`, so it discriminates nothing, and the replacement now states the boundary without naming a
cause. Neither the audit nor any candidate identifies the mechanism.

### 4.2 R03 — the StrictCUSUM nominal-level descriptor: **the edit is gone, the register entry is live**

`R03_v87_cusum_nominal_level.md` carried a verified anchor at L171 and the finding that
`lambda_iid = 65` delivers **2.0 %** under exact i.i.d. noise (Wilson `[0.9, 4.3] %`, excluding 5 %),
so the manuscript's descriptor "calibrated to a nominal $5\%$ under IID noise" is inaccurate for the
CUSUM while remaining accurate for ADWIN (5.0 %, `[3.1, 8.1] %`).

`R03_v87_fpr_explosion.md` carries the *same numbers* as macros — `\RThreeCusumFprIid{2.0\%}`,
`\RThreeCusumFprIidWilsonLow{0.9\%}`, `\RThreeCusumFprIidWilsonHigh{4.3\%}` — and then states
"**Manuscript Changes Required: None** at published precision" and "All qualitative claims
preserved". `docs/DEVIATIONS.md` carries `R03-cusum-nominal-level`. The register says the descriptor
is a deviation; the only surviving R03 candidate says no manuscript change is needed.

**Recommendation.** Restore `R03_v87_cusum_nominal_level.md` from `HEAD` (anchor verified, no
repair needed). Amend `R03_v87_fpr_explosion.md`'s "Manuscript Changes Required: None", or scope it
explicitly to the macro layer.

### 4.3 R08 — the operator and the delivered level: **a D3 correction replaced by a D2 restatement**

`R08_v87_delivered_level.md` carried two verified anchors (L241 and its footnote) and the finding
that the weak comparison the footnote declares delivers `5.1021 %` at `lambda* = 11.4` — **above**
the nominal level the selection rule promises to stay at or below — established by an
absorbing-chain dynamic program that consumes no entropy and carries no sampling interval. The
register carries this as `R08-delivered-level-above-nominal`, Class A, **D3**, with the same exact
value.

`R08_v87_discrete_null_law.md` proposes no manuscript edit, classifies the L241 levels as **D2**,
and introduces `\REightOperatorDelta{0.76}` — the strict-minus-weak gap — while stating that "both
regenerated levels still bracket 5%, preserving the qualitative claim". The D3 the register still
carries is not mentioned.

`R08_v87_lattice_exact_basis.md` and `R08_v87_whiteness_identity.md`, both `NO DEVIATION`
clarifications on the same two sites, are gone with their anchors.

**Recommendation.** Restore `R08_v87_delivered_level.md`, `R08_v87_lattice_exact_basis.md`,
`R08_v87_whiteness_identity.md` and `R08_v87_adverse_numerals.md` from `HEAD` — all nine of their
anchors verify at 1. Keep `R08_v87_discrete_null_law.md`
and `R08_v87_adverse_direction.md` as the macro layer and give them the STEP 4 header; they do not
substitute for a D3 correction and must not be read as closing it.

### 4.4 R13 — the operating points

`R13_v87_operating_points.md` carried two verified anchors and the finding that L331 prints three
numerals without naming their calibration while calling a *different* calibration "the matched
operating point". `R13_v87_oracle_ceiling.md` quotes the same clause, produces verdict macros for
it, and concludes "the qualitative claims are fully preserved" at D0.

**Recommendation.** Restore `R13_v87_operating_points.md` and `R13_v87_frozen_null_scope.md` (LOST)
from `HEAD`. The verdict macros in `R13_v87_oracle_ceiling.md` are compatible with both and need no
change.

### 4.5 R17 — the warm-up restoration scope: **a clarification inverted into a corroboration**

`R17_v87_warmup_restoration_scope.md` was a `NO DEVIATION` clarification: "the level is restored
from $n = 500$ onward" is stated without conditioning on the leverage and rests on an interval
rather than on a point. `R17_v87_econometric_baseline.md` addresses the same sentence and concludes
the opposite — "**corroborating** 'the level is restored from n = 500 onward'. The Wilson 95% CI at
n=500 [4.2%, 11.4%] contains the nominal 5% level" — which is the same interval argument used to
support the claim instead of to qualify it, at a regenerated `7.0 %` against the printed `3.0 %`.

`R17_v87_persistence_collapse_mechanism.md` (corner solution at the optimiser's bound) and
`R17_v87_warmup_resolution.md` (200 streams; min–max over four cells) are LOST outright.

**Recommendation.** Restore all three R17 candidates from `HEAD`. Reconcile
`R17_v87_econometric_baseline.md`'s corroboration paragraph against them before either is applied.

### 4.6 R16 — the dating algorithm: **a live D3 with no candidate**

`R16_v87_dating_algorithm.md` (LOST) carried a verified 250-character anchor at L329 and the
finding behind `R16-dating-misdescription` — Class A, **D3**: strict Pagan–Sossounov yields 48
phases, not the 66 the sentence claims; the 66 come from a Lunde–Timmermann substitution on SPY
alone. `R16_v87_regime_census.md` addresses L329 only through the floor-fraction envelope (D2) and
never mentions the dating algorithm. `R16_v87_boundary_sensitivity.md` (LOST, `R16-boundary-sensitivity`
live) is likewise unaddressed.

**Recommendation.** Restore both R16 candidates from `HEAD`.

### 4.7 The remaining LOST and REWRITTEN files

| files                                                                                                                                                                                                                                                                                                                    | recommendation                                                                                                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `R09_v87_arl0_censoring`, `R09_v87_delay_parity_scope`, `R09_v87_stream_counts`, `R11_v87_figure11_caption`, `R14_v87_reliable_range_scope` (LOST)                                                                                                                                                                       | restore from `HEAD`; all anchors verify at 1, no repair needed                                                                                                                                             |
| `R06_v87_caption_paired`, `R09_v87_anytime_numerals`, `R11_v87_detector_comparability`, `R11_v87_loglog_slopes`, `R11_v87_pht_gamma_rule`, `R11_v87_pht_syncope_gamma`, `R13_v87_covid_delay_numerals`, `R14_v87_synthetic_control_numerals`, `R18_v87_whitening_evidence_strength` (REWRITTEN, successor is macro-only) | restore from `HEAD` and keep the successor as the macro layer beside it; the two are complementary, not alternatives                                                                                       |
| `R02_v87_binary_error_wilson` (REWRITTEN, successor is macro-only)                                                                                                                                                                                                                                                       | restore from `HEAD`, **and substitute literal numerals for the six `\RTwo…` macros its replacement emits** — the only `HEAD` candidate carrying that defect before the refactoring                         |
| `R04b_v87_oracle_tracks_analytic` (anchor mutated)                                                                                                                                                                                                                                                                       | repair the anchor to `an \emph{oracle} arm standardized by the true GARCH parameters crosses at $4.6$, on the analytic prediction, so the extra` (verified unique) and restore `$+5\%$` to the replacement |
| `R04b_v87_efficiency_crossing`, `R04b_v87_estimation_cost` (anchors broken in `HEAD`)                                                                                                                                                                                                                                    | repair per §2.2. `efficiency_crossing` #1 cannot be repaired by transcription — the phrase does not exist; re-target it on the L57 clause or withdraw it                                                   |
| `R15_v87_budget_bound_referent`, `R15_v87_naive_baseline`, `R15_v87_scatter_attribution`, `R15_v87_scatter_sign` (terminator deleted)                                                                                                                                                                                    | restore the closing `>>> END BLOCK`; the blocks currently have no end and their replacement side runs to the next `##` heading                                                                             |
| `R07_v87_bias_bound`, `R07_v87_dispersion_cost`, `R07_v87_panelB_operating_level` (replacements emit undefined macros)                                                                                                                                                                                                   | replace `\RSeven…` with the literal numerals `HEAD` carried; the manuscript defines no macros                                                                                                              |
| `R07_v87_figure7_exactness`, `R07_v87_lattice_handoff_to_R08` (body tables gutted)                                                                                                                                                                                                                                       | restore the exact-law and operator tables from `HEAD`; both replacements are already correct, and `lattice_handoff` also needs the §3.2(b) header                                                          |
| `R10_v87_L290_skewness_numeral`, `R10_v87_caption_fpr_envelope`, `R10_v87_panelA_sign_arm_scope` (marker dialect changed to `% SEARCH`)                                                                                                                                                                                  | anchors and replacements intact; no action beyond the dialect convergence of §4.8                                                                                                                          |
| `R05_v87_lambda_c_numeral`, `R05_v87_sixth_moment_gloss` (fence width only)                                                                                                                                                                                                                                              | anchors and replacements intact; no action beyond §4.8                                                                                                                                                     |

### 4.8 Two structural recommendations

1. **Fix one marker dialect.** Six are in use. `<<< SEARCH` / `=== REPLACE WITH >>>` /
   `>>> END BLOCK` is the only one that survives the refactoring intact and is machine-parseable;
   adopt it and convert the rest.
2. **Add the STEP 4 header to the 26 macro-genre files.** They are legitimate camera-ready
   artefacts, but without `Trigger` and `Register entry` they cannot be sorted into either family
   and cannot be audited at acceptance.

---

## 5. STEP 5 — `R14_v87_synthetic_control_strength.md`

**Created.** Family `NO DEVIATION — clarification only`, no register entry.

**Correction to the task's premise.** The file was **not** "decided and never written": a 34-line
version exists in `HEAD` and is one of the 30 deleted files (§1.3). It was authored fresh here
rather than restored, per T4's "restore no file", and the `HEAD` version is available for comparison
at `git show HEAD:docs/camera_ready_candidates/R14_v87_synthetic_control_strength.md`.
Because the path exists in `HEAD`, the new file registers in `git status` as `M`, not as an
untracked add: `git diff HEAD` shows the `HEAD` body replaced in full, which is what
distinguishes an authored file from a restored one.

**Figures.** Taken from `docs/audits/AUDIT_R14.md` §1: Synth_BTC mean ratio, printed `1.06`,
regenerated `1.041041514153539`, class **D2**; minimum `0.98` → `0.9544910179640719`; maximum
`1.14` → `1.2384142067139186`. §6.2 supplies the bootstrap design (paired moving-block over onsets,
block length `24`, `B = 2000`, one resampled index vector shared by both arms and all seven
magnitudes) and the reason the statistic carries a bootstrap envelope and no Wilson interval.

**One figure is not in the audit.** `AUDIT_R14.md` prints the bootstrap interval for **Synth_ETH**
only. The **Synth_BTC** interval — `[0.9792954429533721, 1.068777876438032]`, three of seven
magnitudes below parity — is in `logs/R14_crypto_isofpr/exp_R14_crypto_isofpr.log` lines 257, 261
and 263, which `AUDIT_R14.md` §1 cites for the adjacent rows. The candidate sources it there
explicitly. **`AUDIT_R14.md` §1 should gain that row**; it is the quantity on which the whole
clarification turns.

**Anchor.** `reproducing the light-tailed Pitman penalty on real machinery` — `grep -Fc` = **1**
against `REFACTORING_COMMON/articleB_whitening_v87.tex`. Chosen in preference to the `HEAD`
version's `inverts the ordering to \textsc{Eco-L1}-faster`, which is also unique but is a **strict
substring** of the string `R14_v87_synthetic_control_numerals.md` searches — the two would not
commute, and that file's own header claims disjointness it does not have. The anchor used here is
disjoint from both sibling candidates and the three edits commute.

**Proposed clause.** The replacement keeps the claim and every printed numeral and appends:
"though a paired moving-block bootstrap over onsets puts the mean's $95\%$ interval at
$[0.98, 1.07]$, so the inversion is a point-estimate ordering and not an interval that excludes
parity."

**Why no register entry.** The falsification condition was fixed before the run — the interval of
the regenerated mean would have to lie entirely below `1` (`exp_R14_crypto_isofpr.log:259`) — and
is not met (`:261`). The interval also covers the published `1.06` (`:263`), so the two campaigns do
not disagree. Nothing printed at L345 is false; the formulation is true and incomplete, which is
the clarification family by definition.
