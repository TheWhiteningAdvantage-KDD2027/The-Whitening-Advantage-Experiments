# REGISTER RESTORATION — `docs/DEVIATIONS.md`

Repository root: `/home/m53/The-Whitening-Advantage-Experiments`. Run this **after** all 21 streams
have been restored by `restore_all_docs.sh`, because it reads the restored audits.

`docs/DEVIATIONS.md` is the single document an artefact evaluation committee will read first. Its
current state has four defects. Repair exactly these four and change nothing else about the file's
substance.

## DEFECT 1 — Two D3 findings are missing (blocking)

The register currently classes stream R08 and stream R17 as `D2`. Both carry a `D3` that the
rewrite removed. Read `docs/audits/AUDIT_R08.md` and `docs/audits/AUDIT_R17.md`, restored, and copy
the D3 rows from them into the register.

- **R08** — the manuscript at L241 states it selects "the nearest attainable level at or below
  nominal", and its own footnote makes the implemented test the weak comparison operator. The weak
  level at the selected threshold is above the nominal level. Reproduce the exact figures from the
  restored audit. **Scope clause, mandatory and immediately after the entry**: the null law itself
  remains exact and free of nuisance parameters; what is contradicted is the selection rule and the
  level reported, not the exactness result. Without that clause the entry will be read as refuting
  the paper's contribution, which it does not.
- **R17** — the manuscript at L341 attributes a false-alarm figure to the arm Table 1 defines as
  the level residual, while the producing cell monitors the squared standardized residual, the arm
  the source script itself names differently. Reproduce the exact figures and the three-step
  evidence from the restored audit. Scope: the false-alarm numerals only.

Both take the same severity as the existing `R16` dating entry, which is the governing precedent.

## DEFECT 2 — Stable identifiers were lost

Every entry must carry a stable identifier of the form `R<NN>-<short-slug>`, e.g.
`R16-dating-misdescription`, `R08-delivered-level-above-nominal`, `R17-eco-l1-arm-identity`,
`R04b-nu-star`, `R15-scatter-sign`, `R11-onset-convention`. Sequential numbering and
per-stream-only sectioning are what this replaces. Reconstruct the identifiers from the restored
audits, which carry them. Add an index at the top of the file: identifier, class, severity, one
line, in stream order.

Cross-references in `docs/audits/` and `docs/camera_ready_candidates/` point at these identifiers.
After you rewrite the register, run:

```bash
grep -rhoE 'R[0-9]{2}[a-z]?-[a-z0-9-]+' docs/audits/ docs/camera_ready_candidates/ | sort -u \
  | while read -r id; do grep -q "$id" docs/DEVIATIONS.md || echo "DANGLING: $id"; done
```

Every `DANGLING` line is a broken cross-reference you must resolve.

## DEFECT 3 — Refuted causal attributions

Three entries attribute Monte-Carlo displacement to BLAS threading, floating-point associativity
or summation order:

```bash
grep -n 'BLAS\|associativity\|summation order' docs/DEVIATIONS.md
```

**That hypothesis was tested and refuted inside this repository.** Stream R01 added a
`--legacy-blas` arm precisely to test it; the arm reproduces the compliant mode bit for bit and
does not recover the published values. The established cause of displacement across the campaign is
the 128-bit entropy re-keying, which replaced seed derivations that discarded most of their entropy.

For each hit: replace the attribution with the mechanism the restored audit for that stream
establishes, citing the audit. Where the audit establishes none, write `cause not identified`.
Do not soften it to "likely" or "consistent with". A displacement of several percentage points in a
rejection rate is not caused by unit-in-last-place differences, and writing that it is invites a
reviewer to check.

## DEFECT 4 — A superseded value and a stale header

- Section R04 still carries a crossing value that the R04b section, twenty lines below, declares
  superseded as an interpolation across an unsampled grid interval. Remove the superseded value
  from R04 and leave a one-line pointer to the R04b entry. The register must not contradict itself
  on the most exposed number of the campaign.
- The file opens with "This document records all **numerical** deviations". It also records
  contradictions of method descriptions, which are not numerical. Rewrite the opening paragraph to
  say that it records every divergence between the repository and the submitted manuscript,
  classified D0 to D3 at the manuscript's own printing precision, and that entries which contradict
  no printed claim carry the class and no severity.

## WHAT YOU MUST NOT DO

Do not delete an entry. Do not lower a severity. Do not add an entry that contradicts no printed
claim of the manuscript — imprecise, incomplete or unqualified formulations that are not false stay
out of this register and belong in `docs/camera_ready_candidates/` under a
`NO DEVIATION — clarification only` header. Do not touch any `.tex` or `.bib`. Do not touch
`README.md`; it is generated.