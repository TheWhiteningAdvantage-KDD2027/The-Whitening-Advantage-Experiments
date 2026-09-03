# T5 — RECONCILE R04 WITH R04b, AND CLOSE THE SCOPE CLAUSES

Repository root: `/home/m53/The-Whitening-Advantage-Experiments`. Write only to
`docs/audits/AUDIT_R04.md`, `docs/audits/AUDIT_R04b.md`, `docs/audits/AUDIT_R16.md` and
`gate_docs.sh`. Never write to any `.tex` or `.bib`.

## PART A — the two audits contradict each other (blocking)

`AUDIT_R04.md` and `AUDIT_R04b.md` publish different regenerated values for the same two printed
numerals, and `AUDIT_R04b.md` explicitly declares one of `AUDIT_R04.md`'s values falsified:

| printed numeral       | AUDIT_R04  | AUDIT_R04b                                                                                               |
| --------------------- | ---------- | -------------------------------------------------------------------------------------------------------- |
| `nu* ~ 4.9`           | `8.52`, D3 | bracket `[7.0, 9.0]`, fit `8.10 [7.78, 8.37]`, D3 — plus a dedicated row classifying `8.52` itself as D3 |
| estimation cost `0.3` | `4.05`, D3 | `3.62 [3.31, 3.92]` and `3.22 [2.52, 3.82]`, D3                                                          |

The campaign record is unambiguous: R04's grid `{3, 4, 4.5, 5, 7, 30}` left the crossing in a
23-unit interval with no sampled point, `8.52` is a two-point interpolation across that empty
interval, and R04b was created to extend the grid and supersede it. **R04b is the owner.**

Establish this from the artefacts before writing — read `results/R04_isofpr_race/data/` and
`results/R04b_nu_refinement/data/` with `float_precision='round_trip'` and confirm the grid gap.
If the artefacts say otherwise, stop and report.

Then, in `AUDIT_R04.md` only:

- Keep the two rows. They record what R04's own design measured, and deleting them would hide the
  history. **Change their severity from D3 to D2** and add to each row's `regenerated value` cell
  the phrase `superseded by R04b, see AUDIT_R04b.md`. The rationale, which you state in the audit:
  a value produced by interpolation across an unsampled interval is not a measurement of the
  quantity, so it cannot falsify a printed claim; R04b's refined grid is what does.
- Update the severity count.
- Add, immediately after the table, a short paragraph naming R04b as the owner of both numerals and
  stating that R04's grid could not resolve them.

Do not touch `AUDIT_R04b.md`'s values. Its bracket and its fits stand.

## PART B — `AUDIT_R04b.md` declares six D3 and carries five

```bash
sed -n '/^## 1\. Deviation table/,/^## 2\./p' docs/audits/AUDIT_R04b.md | grep -c '| *D3 *|'
grep -oiE 'Count by severity[^.]*' docs/audits/AUDIT_R04b.md
```

The body has five rows, the count declares six. One of the two is wrong. Read the log
`logs/R04b_nu_refinement/*.log` and determine which: a sixth D3 the table lost, or a miscount.
Repair the one the log establishes, and say in the audit which it was.

## PART C — scope clauses on every D3

A D3 without a scope clause is read as refuting more than it refutes. Three audits need one.

- `AUDIT_R04.md` (after Part A it may carry no D3 left; if it does, it needs the clause) and
  `AUDIT_R04b.md`: a scope clause bounding what the `nu*` and estimation-cost findings touch. Both
  concern the **location of an efficiency crossing and the cost of the parametric route**, not the
  whitening property, not the exactness of the Concept threshold, and not any proposition. State
  precisely what each does and does not touch, from the audit's own evidence.
- `AUDIT_R16.md` carries the substance already, in prose: "The falsification touches the dating
  description only; it does NOT affect the 80% headline, which is computed from the canonical
  census that does reach 66 phases and 53 out of budget at gamma=20." **Do not rewrite it** — give
  it the marker `**Scope:**` at the head of that sentence so an extraction can find it.

Format, in every case, immediately after the falsified-claim paragraph:

```
**Scope:** <what is contradicted>, and not <what is not>.
```

## PART D — two false positives in `gate_docs.sh`

The gate reports findings that are not defects. Repair its two greps, and only those.

- **G8** fires on prose mentions of the word "Wilson" and on the primitive name `wilson_ci`. Its
  purpose is to catch a Wilson interval applied to a statistic that is not a binomial proportion.
  Narrow it to lines that both mention Wilson **and** carry an interval, and exclude lines that
  mention it in prose, in a test name, in a primitive name, or in a table header describing the
  column rather than applying it. Verify against `AUDIT_R09.md` line 229, `AUDIT_R14.md` line 128,
  `AUDIT_R16.md` lines 82 and 96 and `AUDIT_R18.md` lines 37, 41, 43 — all seven are legitimate and
  must stop firing — and confirm it would still fire on a Wilson interval attached to a delay, a
  ratio or a degrees-of-freedom estimate.
- **G7c** requires a scope clause matching `^\*\*Scope|^Scope:`. After Part C every D3 audit has
  one, so this should pass; verify it does rather than relaxing the pattern.

## VERIFY

```bash
bash gate_docs.sh 2>&1 | tee logs/gate_docs_T5.log
```

Report the reconciled R04 table, the Part B verdict, and the gate output. Nothing else.