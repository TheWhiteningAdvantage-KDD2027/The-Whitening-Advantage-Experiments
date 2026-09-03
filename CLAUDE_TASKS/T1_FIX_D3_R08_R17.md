# T1 — CORRECT THE TWO D3 ROWS IN R08 AND R17

Repository root: `/home/m53/The-Whitening-Advantage-Experiments`. Read-only outside the two files
named below. Never write to any `.tex` or `.bib`.

Two audits carry a D3 finding that a documentation rewrite removed. A manual repair was then
attempted and placed the severity on the wrong rows. You correct both, from the evidence, and you
verify one claim about the logs before doing anything else.

## STEP 0 — VERIFY THE LOG-CORRUPTION HYPOTHESIS FIRST (blocking)

A claim is in circulation that a previous agent downgraded D3 severities *inside the Python test
suite that emits the execution log*, so that the logs themselves now carry `D2` where the campaign
established `D3`. If true, the logs are no longer a source of truth and this whole restoration is
compromised. If false, the audits simply lost the row.

Test it, do not assume it:

```bash
git log --oneline -- tests/test_R08_claims.py tests/test_R17_claims.py | head -20
git log -p --all -S 'D3' -- tests/test_R08_claims.py | head -80
grep -n 'D3\|D2\|severity\|classify' tests/test_R08_claims.py tests/test_R17_claims.py
grep -n 'D3\|D2' logs/R08_adverse_lattice/*.log | head -30
grep -n 'D3\|D2' logs/R17_econometric_baseline/*.log | head -30
```

Write your verdict in one paragraph at the top of your final report, with the commands and the
lines that establish it. A simpler and sufficient explanation exists — the automated gate counted
the literal string `D3`, which occurs in the mandatory section title `## 1. Deviation table
(D0-D3)`, so a file with zero D3 rows passed. **Do not adopt the graver hypothesis unless your own
commands establish it.** If the logs *are* corrupted, stop and report; do not repair the audits
from a corrupted source.

## STEP 1 — `docs/audits/AUDIT_R08.md`

The current table marks `D3` on the row `L241 level above nominal (lambda=11.2)`. That row measures
a Monte-Carlo redraw at `lambda = 11.2` and is a **D2**. Restore it to D2.

The D3 concerns a different quantity and needs **its own row**: the level delivered at the
*selected* threshold `lambda* = 11.4` under the operator the code actually implements.

The underlying arithmetic, which you must verify against
`results/R08_adverse_lattice/data/R08_lattice_exact_law.csv` and `R08_operator_levels.csv` read
with `float_precision='round_trip'`, is that on a lattice of step `2*delta = 0.2` the events
`{M >= 11.4}` and `{M > 11.2}` coincide, so the weak level at `lambda* = 11.4` equals the strict
level at `lambda = 11.2`. Confirm this in the data before writing it; if the CSVs say otherwise,
report that instead and change nothing.

Add one row of the form:

`| L241 level delivered at lambda* = 11.4 under the implemented (weak) operator | <= 0.05 by the stated rule | <regenerated value> | D3 | <csv :: column, lambda=11.4, weak operator> | <log line> |`

Then update the severity count, and keep exactly two paragraphs below it — the falsified claim, and
the scope clause. The scope clause is mandatory and non-negotiable in its substance: the null law
itself remains exact and free of nuisance parameters; what is contradicted is the selection rule
and the level reported, not the exactness result. Without it a reader takes the D3 as refuting the
paper's central contribution, which it does not.

## STEP 2 — `docs/audits/AUDIT_R17.md`

The current table marks `D3` on two rows, `FPR_Eco at n_warmup = 250` (9.5 -> 10.5) and
`= 500` (3.0 -> 7.0). Both are Monte-Carlo redraws under the mandated 128-bit re-keying. **Restore
both to D2.**

R17's D3 is not a numeral that moved. It is a contradiction of method attribution, and it has no
regenerated numerical value. Add one row whose `regenerated value` column names the producing arm
rather than a number:

`| L341 arm identity for the 9.5% false-alarm figure | Eco-L1 (level residual, Table 1 L117) | Eco_L2 (squared standardized residual, the arm the source script names) | D3 | R17_warmup_sensitivity.csv :: FPR_Eco, protocol 3d | <log line> |`

Then the falsified-claim paragraph, carrying the three-step evidence **exactly as established and
not otherwise**:

1. Table 1 at tex line 117 defines `Eco-L1` as the level residual `eps_t / sigma_hat_t`.
2. The cell L341 quotes its figure from is `protocol_3d`, which monitors `(z_hat^2 - mu)/sigma` —
   the arm the delivered script itself names `Eco_L2`, beside a separately thresholded L1 arm.
3. `protocol_3b`'s L1 arm runs 100 seeds, so `9.5%` is unattainable there; `9.5% = 19/200` is
   exactly `protocol_3d`'s resolution.

Then the scope clause: the false-alarm numerals only; the persistence median is arm-agnostic
because the fit is shared.

**A rejected draft is in circulation and you must not reproduce it.** It describes a false-alarm
explosion from `3.2%` to `20.6%` under pseudo-Gaussian innovations at 10,000 streams per point,
with Ljung-Box rejection rising `5.1% -> 24.6%`, citing `Fig15_Robustness_Leverage.png`. **Those
are R12's numbers, from manuscript line L349 and Figure 12.** R17 never measured them: its grid is
`n_warmup in {250, 500, 1000, 2000}` at 200 streams, and L341 mentions neither leverage nor an FPR
explosion. If any of those figures appears in your output, the output is wrong.

## STEP 3 — VERIFY

```bash
bash gate_docs.sh R08 R17
```

Both must return `[OK]`. Report the two corrected tables, your Step 0 verdict, and nothing else.