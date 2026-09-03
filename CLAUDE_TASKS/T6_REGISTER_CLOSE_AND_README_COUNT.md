# T6 — CLOSE THE REGISTER AND RECOUNT THE README

Repository root: `/home/m53/The-Whitening-Advantage-Experiments`. Run **after** T5. Write only to
`docs/DEVIATIONS.md` and `build_readme.sh`. Never write to any `.tex` or `.bib`, and never edit
`README.md` directly — it is generated.

## PART A — seven dangling identifiers

```bash
grep -rhoE 'R[0-9]{2}[a-z]?-[a-z0-9-]+' docs/audits/ docs/camera_ready_candidates/ | sort -u \
  | while read -r id; do grep -q "$id" docs/DEVIATIONS.md || echo "DANGLING: $id"; done
```

Seven remain: `R02-binary-error-rate`, `R09-arl0-censoring`, `R11-onset-convention`,
`R11-pht-gamma-rule`, `R11-pht-slope`, `R11-pht-syncope`, `R13-frozen-null-scope`.

Four of them are register entries R11 wrote at its own closure and the register lost:

- `R11-pht-slope` — the published log-log slope for the PHT on the Data pipeline moves, and the fit
  domain is restricted to the points where detection exceeds one half, the delays there being
  conditional on detection.
- `R11-pht-syncope` — the manuscript's threshold for the PHT's detection collapse moves.
- `R11-pht-gamma-rule` — the manuscript states the PHT needs the same `lambda x Gamma` inflation as
  the CUSUM and that this holds the nominal level; measured over the grid the rate falls
  monotonically with non-overlapping extremes, so no level is held anywhere.
- `R11-onset-convention` — the four delay numerals of the Figure 15B caption were produced under
  two different onset conventions and are not mutually comparable. This one contradicts no printed
  claim: it carries a class and **no severity**.

For each of the seven: locate the audit that defines it, and create the entry **from that audit**,
with its class, its severity where one applies, its source CSV cell, and a one-line statement.
Where the audit shows the finding contradicts no printed claim, record it with no severity — that
is a legitimate register state and not a gap. If an audit does not define an identifier it cites,
say so rather than inventing an entry.

Re-run the DANGLING command afterwards. It must return empty.

## PART B — recount section 6 of the README preamble

The preamble is a heredoc inside `build_readme.sh`, lines 5 to 47 approximately. Its section 6.1
carries a table of five formal contradictions. That table was written before the audits were
restored and it is now wrong in two ways: it omits at least one D3, and it may double-count R04
against R04b.

Establish the true landscape first:

```bash
for f in docs/audits/AUDIT_R*.md; do
  n=$(sed -n '/^## 1\. Deviation table/,/^## 2\./p' "$f" | grep -c '| *D3 *|')
  [[ $n -gt 0 ]] && echo "$f : $n"
done
```

Then rebuild the 6.1 table from what that command returns, after T5 has reconciled R04 with R04b.
One row per **finding**, not per table row: several D3 rows of one audit may express one finding
(R04b's estimation-cost rows are three routes to one contradiction). Each row names its register
identifier, its manuscript site, and what does not hold — and where the audit carries a scope
clause, the row's last sentence carries its substance. `R07`'s bias-bound finding must appear; it
is currently absent from the table.

Do not inflate and do not deflate. A row that expresses no contradiction of a printed claim does
not belong in 6.1 — it belongs in the register with no severity and is not surfaced in the README.

Update the count sentence in the lead paragraph of section 6 to match.

## PART C — regenerate

```bash
sed -i 's/\r$//' docs/sections/R*.md
python3 build_mapping.py > docs/MAPPING.md
bash build_readme.sh
grep -c '^# R' README.md      # must be 21
```

Report the seven created entries, the D3 landscape command output, and the rebuilt 6.1 table.