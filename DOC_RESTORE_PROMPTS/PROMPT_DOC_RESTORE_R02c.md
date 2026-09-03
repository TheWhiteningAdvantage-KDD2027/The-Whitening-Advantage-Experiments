# DOCUMENTATION RESTORATION — STREAM R02c

Repository root: `/home/m53/The-Whitening-Advantage-Experiments`. All paths below are relative to it.

You restore two documents for stream **R02c** (slug `R02c_horizon_sweep`). The experimental artefacts,
the scripts and the tests are **correct and frozen**: you do not touch them. A previous rewrite
compressed the documentation under a template that removed its evidentiary content. You put that
content back, from the logs.

## §1. SOURCES, IN PRIORITY ORDER

1. `logs/R02c_horizon_sweep/*.log` — the execution log. **Source of truth for every number.** Read it
   in full before writing anything.
2. `results/R02c_horizon_sweep/data/*.csv` and `results/R02c_horizon_sweep/tables/R02c_claims.tex` — for
   locating the source cell of a value. Read CSVs with `float_precision='round_trip'` if you read
   them programmatically.
3. `docs/audits/AUDIT_R02c.md` and `docs/sections/R02c.md` — current drafts. Use them for
   structure and for prose you may keep. **Never use them as a source for a number**: they are
   what you are repairing.
4. `docs/DEVIATIONS.md`, section R02c — cross-check only.

The frozen manuscript `articleB_whitening_v87.tex` is READ-ONLY. You may quote it. You may not
write to it, ever, under any instruction.

## §2. DELIVERABLE 1 — `docs/audits/AUDIT_R02c.md`

Rewrite it with **exactly these six sections, in this order**. This structure supersedes any
4-section template you may find in the current file.

### `## 1. Deviation table (D0-D3)`
The full table, copied from the log, one row per classified quantity, with these columns:
`quantity | manuscript value | regenerated value | severity | source CSV cell | log line`.
The `source CSV cell` names a file and a column, e.g. `R02c_foo.csv :: bar_rate`. The `log line`
is the line number in the log the value is copied from.
Below the table, a one-line count by severity. **If the table contains a D3 row, write immediately
after the count: what the falsified qualitative claim is, where in v87 it is printed, and the exact
scope of the falsification** — what the finding does NOT touch matters as much as what it does.

### `## 2. Controls`
One subsection per control the log records. Each carries, in this order: what the control tests;
its **trigger probability under its own null hypothesis**, with the derivation in one line; the
realised margin, in standard errors where the log gives one; and the verdict. Where a control was
demoted from a gate to a reported measurement, say so and say why.
Where the log records a control without a trigger probability, write the control and then
`Trigger probability: NOT RECOVERABLE FROM THE LOG.`

### `## 3. Test suite`
Run `pytest tests/test_R02c_claims.py -v` and paste the output **verbatim** inside a fenced block.
Do not summarise it, do not truncate it, do not reformat it. Below it, one line giving the total
for the whole suite if the log records one.

### `## 4. Reproducibility digests`
The SHA-256 digests of the two (or more) successive runs, copied from the log, with the number of
workers of each. If the log carries only one set, paste it, then run
`sha256sum results/R02c_horizon_sweep/data/*.csv results/R02c_horizon_sweep/tables/*.tex` and paste the current
listing beside it, labelled `current tree, single run`. If the log carries none, write the section
title followed by `NOT RECOVERABLE FROM THE LOG.` and the current listing.

### `## 5. Design decisions taken outside the plan`
Numbered list, copied from the log or from the current draft where the draft describes a decision
rather than a measurement. Each entry states what was decided and why. If the current draft records
none and the log records none, write `None recorded.`

### `## 6. Open questions, left open`
Numbered list. **These are questions, not conclusions: you do not answer them, and you do not
delete one because it looks unresolved.** An unresolved question in an audit is the audit working.
If none is recorded anywhere, write `None recorded.`

## §3. DELIVERABLE 2 — `docs/sections/R02c.md`

A reader-facing report. Keep the current prose where it is accurate. Fix it where it is not.
Required content, in this order:

1. Title `# R02c — <short title>`.
2. What the experiment establishes, and which figures, tables and numbered claims of the manuscript
   it certifies. Name them (`Figure N`, `L<line>`).
3. The reproduction command: `bash run_experiment_R02c.sh`.
4. Expected artefacts with their paths, split into **two named groups**: those that certify a
   published value, and those that certify a control and certify no published value. This split is
   mandatory. The second group typically contains files whose names carry a suffix such as
   `_fast`, `_legacy_seeds`, `_legacy_qmle`, `_witness_blas`, `_independent_seeds`, `_crn_witness`,
   `_control_ecusum`, `_strict_ps`, `_symmetric`.
5. Measured execution cost, copied from the log.
6. `## Known deviations from the submitted manuscript` — **if and only if** the D0-D3 table of the
   audit carries a D2 or a D3. One short paragraph per deviation, each naming its register entry
   identifier. If the table carries only D0 and D1 rows, omit this section entirely.

**Blocking consistency check before you finish**: if the audit's D0-D3 table carries a D3, this
section must not state, in any form, that the corresponding manuscript claim holds, and must not
contain the sentence "all qualitative claims are preserved" or any variant.

## §4. SELF-VERIFICATION — run these and paste nothing, fix everything they find

```bash
grep -Ein 'proves|proven|perfectly valid|validates the (theorem|thesis|claim)|confirms the|as expected|triumph|victory|irrefutable|brilliant' \
  docs/audits/AUDIT_R02c.md docs/sections/R02c.md
grep -in 'wilson' docs/audits/AUDIT_R02c.md      # every hit must be on a proportion
grep -in 'deff *= *1\|simple random sampling'      docs/audits/AUDIT_R02c.md
grep -in 'BLAS\|associativity\|summation order'    docs/audits/AUDIT_R02c.md docs/sections/R02c.md
grep -c 'D3' docs/audits/AUDIT_R02c.md            # compare against the log
tail -c 1 docs/audits/AUDIT_R02c.md | od -c | head -1   # must end with \n
```

The first must return empty. The second must return only proportions. The third and fourth must
return empty unless a log line establishes the claim, in which case the citation is on the same
line. The fifth must not be lower than the log's own D3 count.

## §5. WHAT YOU DO NOT DO

You do not touch `experiments/`, `results/`, `tests/`, `logs/`, `run_all.sh`, `run_tests.sh`,
`logs/all_tests.log`, `docs/DEVIATIONS.md`, `README.md`, `build_readme.sh`, `build_mapping.py`,
or any `.tex` or `.bib`. Two files only: `docs/audits/AUDIT_R02c.md` and `docs/sections/R02c.md`.

You do not compress. You do not impose a word count. You do not remove a D3, an open question, or
a control. If you find yourself deleting evidence to meet a shape, the shape is wrong.