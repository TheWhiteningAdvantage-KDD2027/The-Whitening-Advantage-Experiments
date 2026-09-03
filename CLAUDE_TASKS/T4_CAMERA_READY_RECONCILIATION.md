# T4 — RECONCILE `docs/camera_ready_candidates/`

Repository root: `/home/m53/The-Whitening-Advantage-Experiments`.

43 candidate files are present. A documentation refactoring renamed and possibly rewrote them, and
several candidates parked during the campaign are absent under their recorded names. In the current
tree a rename and a deletion are indistinguishable. **Git is the only authority.** Produce a
reconciliation report; do not create or delete a file until the report is reviewed.

## STEP 1 — recover the history

```bash
git log --oneline --all -- docs/camera_ready_candidates/ | head -40
git log --diff-filter=D --name-only --all -- docs/camera_ready_candidates/ | sort -u
git log --diff-filter=R --name-status --all -- docs/camera_ready_candidates/
git log --all --format='%H %ad %s' --date=short -- docs/camera_ready_candidates/ | tail -5
```

Identify the last commit before the documentation refactoring and diff its candidate directory
against `HEAD`:

```bash
git diff --stat <that_commit> HEAD -- docs/camera_ready_candidates/
```

## STEP 2 — classify every difference

Three classes, and the distinction is the whole point of the task:

- **RENAMED** — same content, different filename. Record old and new name. No loss.
- **REWRITTEN** — same subject, different content. **These are the dangerous ones.** For each,
  diff the two versions and report what changed in the `RECHERCHER` block and in the proposed
  replacement. A candidate whose search anchor was rewritten without access to the frozen `.tex` is
  unusable at camera-ready time.
- **LOST** — no successor. Record the subject from the deleted file.

Candidates the campaign records as parked, whose current names do not obviously correspond, and
which must each be resolved to one of the three classes: the Ljung-Box i.i.d.-arm clause of
R02b/R02c; the StrictCUSUM nominal-level descriptor of R03; the Figure 6 caption of R06; R11's
figure-11 caption, log-log slopes, PHT gamma rule, PHT syncope threshold and detector
comparability; R13's operating points; R16's boundary sensitivity; R08's operator and delivered
level; R17's warm-up restoration scope and persistence-collapse mechanism.

## STEP 3 — verify every surviving anchor against the frozen manuscript

For every candidate present in `HEAD`, extract its `RECHERCHER` / SEARCH block and check it occurs
exactly once in the frozen manuscript:

```bash
grep -Fc "<search string>" articleB_whitening_v87.tex     # must be exactly 1
```

Report every candidate whose count is 0 (the anchor does not exist — the block was reconstructed
from memory) or greater than 1 (the anchor is not unique — the patch would apply in the wrong
place). The manuscript is READ-ONLY: you read it, you never write to it.

## STEP 4 — the two-family header

Every candidate must carry, in its header, `PARKED — do not apply`, the trigger (acceptance
notification, 14 November 2026), and one of two family markers:

- nothing extra, if the candidate corrects a formal contradiction carried by `docs/DEVIATIONS.md`;
- `NO DEVIATION — clarification only`, if it clarifies a formulation that is true but incomplete
  and which therefore carries **no** register entry.

Report which candidates lack a family marker, and which carry `NO DEVIATION` while also having a
register entry, or the reverse. Both are inconsistencies.

## STEP 5 — one missing candidate to create

`R14_v87_synthetic_control_strength.md` was decided and never written. Create it, family
`NO DEVIATION — clarification only`, no register entry. Subject: manuscript line L345 states that
the `t30` synthetic control inverts the efficiency ordering. The point estimate verifies it, so
nothing printed is false; the paired bootstrap interval of the regenerated mean spans parity, so
the inversion carries less evidential weight than the sentence suggests. Take the exact figures
from `docs/audits/AUDIT_R14.md`, verify the `RECHERCHER` anchor with `grep -Fc` against the frozen
`.tex`, and propose a clause in the manuscript's own register noting that the interval spans parity.

## DELIVERABLE

A single report, `docs/camera_ready_candidates/RECONCILIATION.md`: the three-class table, the anchor
verification results, the family-marker inconsistencies, and a recommendation per LOST or REWRITTEN
candidate. **Restore no file and delete no file in this task.** The one exception is Step 5.