# T2 — RESTORE R07, AND SETTLE THE WILSON INTERVALS IN R14

Repository root: `/home/m53/The-Whitening-Advantage-Experiments`.

## PART A — `docs/audits/AUDIT_R07.md` was never restored

It still carries the superseded four-section template: `## Theoretical Anchor`,
`## Empirical Methodology`, `## Metric Concordance Table with Wilson 95% CIs`,
`## Methodological Scope & Limitations`.

Execute `DOC_RESTORE_PROMPTS/PROMPT_DOC_RESTORE_R07.md` in full. Its contract governs; read it
before writing. The single rule that overrides everything in it: **every number you write comes
either from a file you cite by path and line, or from a command you show. Where neither exists,
write `NOT RECOVERABLE FROM THE LOG.` A fabricated pytest block or an invented digest in an
artefact repository is misconduct, not a shortcut.**

Two R07-specific points the generic template does not carry:

- R07 owns the lattice exact law at `H = 5000` (`R07_lattice_exact_law.csv`) and stream R08 cites it
  in its own control C2a. Whatever you write about the lattice must remain consistent with
  `docs/audits/AUDIT_R08.md`; if it is not, report the divergence rather than aligning either side.
- R07 also owns `R07-bias-bound-not-a-bound` and the `2.5` constant of manuscript line L308, which
  R08 cites without emitting a macro. Do not delete that entry.

## PART B — the three Wilson mentions in `docs/audits/AUDIT_R14.md`

`AUDIT_R14.md` is restored and structurally correct: it carries the six mandatory sections. But it
contains three occurrences of `wilson`, and an objection has been raised that at least one applies
to a statistic that is not a binomial proportion.

```bash
grep -in 'wilson' docs/audits/AUDIT_R14.md
```

For each hit, determine the statistic it qualifies. Proportions in this stream are detection rates,
false-alarm rates, `add_reliable` fractions. **Not proportions**: `nu_hat` (an estimated degrees of
freedom, 2.78), `ADD` (a delay in steps), and above all the **ADD ratio** between arms, which is a
ratio of two conditional means and for which `[1.041, 1.041]` is not an interval of anything.

Where the interval is misapplied: replace it with the dispersion the log actually carries for that
quantity, named for what it is — `SEM`, `design-corrected SE`, `paired moving-block bootstrap
interval`. R14's ratio intervals come from a paired moving-block bootstrap over onsets, block
length 24, `B = 2000`; the log records them. If the log records no dispersion for a value, write the
value alone rather than manufacturing one.

Do not otherwise rewrite `AUDIT_R14.md`. It passed its gate.

## VERIFY

```bash
bash gate_docs.sh R07 R14
```