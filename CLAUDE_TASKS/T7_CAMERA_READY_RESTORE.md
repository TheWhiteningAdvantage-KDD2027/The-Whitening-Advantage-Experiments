# T7 — RESTORE THE CAMERA-READY CANDIDATES FROM GIT

Repository root: `/home/m53/The-Whitening-Advantage-Experiments`. Write only under
`docs/camera_ready_candidates/`. Never write to any `.tex` or `.bib`.

`docs/camera_ready_candidates/RECONCILIATION.md`, produced by task T4, establishes that the
`RENAMED` class is empty: every difference between the pre-refactoring corpus and `HEAD` is a
rewrite or a loss. Seventeen files were rewritten in place with their anchors altered; eleven were
lost, each having carried at least one anchor verified at `grep -Fc = 1` against the frozen
manuscript.

A candidate whose `RECHERCHER` block no longer occurs in `articleB_whitening_v87.tex` is
**unapplicable**, and the failure surfaces only on the day the correction is applied. That is the
defect this task removes.

## PART A — restore the eleven lost files

`RECONCILIATION.md` section 1.3 lists them with the commit that held them. For each:

```bash
git show <commit>:docs/camera_ready_candidates/<file> > docs/camera_ready_candidates/<file>
```

Then, for every restored file, verify each of its anchors:

```bash
grep -Fc "<exact search string>" articleB_whitening_v87.tex     # must be exactly 1
```

An anchor returning 0 means the block was never valid or the manuscript moved; an anchor returning
more than 1 means the patch would apply in the wrong place. Report both classes and repair neither
by guessing: quote the surrounding manuscript text and state what a valid anchor would be.

## PART B — reconcile the seventeen rewritten files against their originals

For each, diff the pre-refactoring version against `HEAD`:

```bash
git diff <commit> HEAD -- docs/camera_ready_candidates/<file>
```

`RECONCILIATION.md` records what each rewrite removed. Restore the removed substance where the
original carried a verified anchor or a finding the current version dropped, and keep whatever the
rewrite genuinely improved. Two examples the reconciliation names explicitly:
`R07_v87_panelB_operating_level.md` had its operator table gutted and lost the contrast with the
`4.29%` level; `R07_v87_lattice_handoff_to_R08.md` had its exact-versus-printed table replaced by a
macro stub. Both losses are substantive.

Where the original and the rewrite disagree on a number, the audit for that stream arbitrates. If
the audit is silent, keep both and flag the divergence in the file.

## PART C — merge duplicates and set the family marker

Several lost files map onto a single surviving successor (`R08_v87_adverse_numerals.md` and
`R08_v87_whiteness_identity.md` both onto `R08_v87_adverse_direction.md`). Do not create two files
that patch the same manuscript line: merge, and state the merge in the file's header.

Every candidate ends with a header carrying, in this order: `PARKED — do not apply`; the trigger,
acceptance notification of 14 November 2026; and exactly one family marker — nothing extra when the
candidate corrects a formal contradiction carried by `docs/DEVIATIONS.md`, or
`NO DEVIATION — clarification only` when it clarifies a formulation that is true but incomplete and
therefore carries no register entry. A candidate carrying `NO DEVIATION` while a register entry
exists for it, or the reverse, is an inconsistency to report.

## PART D — the final anchor sweep

```bash
for f in docs/camera_ready_candidates/*_v87_*.md; do
  echo "== $f"
done
```

For every file, extract every search block and run `grep -Fc` against the frozen manuscript.
Produce `docs/camera_ready_candidates/ANCHOR_VERIFICATION.md`: one row per anchor, with the file,
the first sixty characters of the string, the count, and a verdict. **Every anchor must be exactly
1.** Any other value is a blocking item listed at the top of that file.

Report the count of restored files, the count of merged files, and the anchor table's failures.