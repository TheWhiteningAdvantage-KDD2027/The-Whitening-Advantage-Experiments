# T3 — RESTORE `docs/DEVIATIONS.md`

Repository root: `/home/m53/The-Whitening-Advantage-Experiments`. Run **after** T1 and T2, because
this task reads the corrected audits. Write to `docs/DEVIATIONS.md` only.

`docs/DEVIATIONS.md` is the document an artefact evaluation committee reads first. Four defects.

## DEFECT 1 — the two D3 findings are missing (blocking)

The register classes R08 and R17 as `D2`. Both carry a `D3`. **Copy them from
`docs/audits/AUDIT_R08.md` and `docs/audits/AUDIT_R17.md` as corrected by task T1** — do not
reconstruct them from any other source, and do not paraphrase their numbers.

- `R08-delivered-level-above-nominal`, class D3. Manuscript line L241 and its footnote. The text
  selects "the nearest attainable level at or below nominal" while its own footnote makes the
  implemented test the weak comparison operator, whose level at the selected threshold is above
  nominal; the level reported is the strict one. **Mandatory scope clause, immediately after the
  entry, in substance and not necessarily in these words:** the null law itself remains exact and
  free of nuisance parameters; what is contradicted is the selection rule and the level reported,
  not the exactness result.
- `R17-eco-l1-arm-identity`, class D3. Manuscript line L341 and Table 1 at tex line 117. A
  false-alarm figure is attributed to the arm Table 1 defines as the level residual, while the
  producing cell monitors the squared standardized residual — the arm the source script itself
  names differently. Carry the three-step evidence from the audit. **Scope: the false-alarm
  numerals only.**

Both take the severity of `R16-dating-misdescription`, which is the governing precedent for a
method description the pipeline does not produce.

**Two rejected drafts you must not reproduce.** First: R17's finding does **not** concern a
false-alarm explosion from `3.2%` to `20.6%` under leverage, nor a Ljung-Box rise from `5.1%` to
`24.6%`, nor `Fig15_Robustness_Leverage.png` — those belong to R12 and to manuscript line L349.
Second: R17's D3 is **not** the movement of `9.5% -> 10.5%` or `3.0% -> 7.0%`; those are
campaign-redraw D2 rows.

## DEFECT 2 — stable identifiers were lost

Every entry carries an identifier `R<NN>-<short-slug>`. Reconstruct them from the audits and the
camera-ready candidates, which cite them. Add an index at the top: identifier, class, severity,
one line, in stream order.

Twenty-one identifiers are currently cited somewhere and absent from the register:

```
R05-campaign-redraw  R07-dispersion-cost-numeral  R07-oracle-band-precision  R07-panel
R09-add-conditioning  R09-cusum-add-parity-d2  R09-cusum-peeking-fpr-d2  R09-mix-add-parity-d1
R10-campaign-redraw  R11-gamma-grid-floor  R11-regenerated  R12-campaign-redraw
R12-censored-delay-d2  R12-concept-delay-d1  R12-detection-rate-d2  R16-covid-floor-values
R16-floor-frac-envelope  R16-out-of-budget-frac  R16-sharpe-one-cost  R17-campaign-redraw
R18-ljungbox-power
```

For each: locate the audit that defines it, and either create the register entry from that audit,
or — if the finding contradicts no printed claim of the manuscript — record it with its class and
**no severity**, which is a legitimate register state. `R07-panel` looks like a truncated
identifier; resolve it against the R07 audit rather than inventing an entry. Re-run afterwards:

```bash
grep -rhoE 'R[0-9]{2}[a-z]?-[a-z0-9-]+' docs/audits/ docs/camera_ready_candidates/ | sort -u \
  | while read -r id; do grep -q "$id" docs/DEVIATIONS.md || echo "DANGLING: $id"; done
```

The output must be empty.

## DEFECT 3 — refuted causal attributions

```bash
grep -n 'BLAS\|associativity\|summation order' docs/DEVIATIONS.md
```

Attributing Monte-Carlo displacement to BLAS threading was **tested and refuted inside this
repository**: stream R01 added a `--legacy-blas` arm for exactly that purpose; it reproduces the
compliant mode bit for bit and does not recover the published values. The established cause across
the campaign is the 128-bit entropy re-keying, which replaced seed derivations discarding most of
their entropy. Replace each attribution with the mechanism the corresponding audit establishes,
citing it; where none is established, write `cause not identified`. Do not soften to "likely" or
"consistent with": a displacement of several percentage points in a rejection rate is not caused by
unit-in-last-place differences, and asserting it invites a reviewer to check.

Exception: `R15-mkl-cbwr-rho` **is** an established BLAS-reordering finding, with a `--witness-blas`
arm that confirmed it. Leave it, and make sure it cites its arm.

## DEFECT 4 — a superseded value and a stale header

- Section R04 carries a crossing value that section R04b declares superseded twenty lines below, as
  an interpolation across an unsampled grid interval. Remove it from R04, leave a one-line pointer
  to the R04b entry. The register must not contradict itself on the most exposed number of the
  campaign.
- The opening says the file records "all **numerical** deviations". It also records contradictions
  of method descriptions, which are not numerical. Rewrite it: the file records every divergence
  between the repository and the submitted manuscript, classified D0 to D3 at the manuscript's own
  printing precision; entries that contradict no printed claim carry a class and no severity.

## WHAT YOU MUST NOT DO

Do not delete an entry. Do not lower a severity. Do not add an entry for a formulation that is
imprecise, incomplete or unqualified but **not false** — those belong in
`docs/camera_ready_candidates/` under a `NO DEVIATION — clarification only` header, never here.
Do not touch any `.tex`, any `.bib`, `README.md`, or `docs/audits/`.