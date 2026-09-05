# `data/reference/R12/orphans/` — two CSVs with no producing script

These two files were delivered with the R12 attachment set. **No script in the delivered tree
writes either of them, and their provenance is unknown.**

## The fact, and the command that establishes it

`Priorite_10_robustness_gjr_student.py` writes exactly two CSVs — `protocol_expA_leverage_fpr.csv`
(l.274) and `protocol_expB_singularity_add.csv` (l.404) — and nothing else. Run over the whole of
the delivery directory, on 2026-08-09:

```
$ cd /home/m53/Article_B_Whitening_effect && grep -rIlEn 'argarch_boundary|race_condition' .
R12_gjr_student/PROMPT_REPO_R12_gjr_student.md
```

The only file in the tree that names either CSV is the prompt that attaches them. There is no
producing script, no log line that announces a write, and no parameterisation to recover.

## Why they are vendored rather than rebuilt

Rebuilding a file from two output numbers means inferring a design from the numbers it then
reproduces, which is not a measurement. Both files are therefore kept **verbatim, under their
original names**, as historical witnesses of the submitted delivery — the same status
`data/reference/README.md` gives every other file under `data/reference/`.

## `expA_argarch_boundary.csv` — the task-boundary witness

Two rows, `target / rejection_rate / ci_low / ci_high`:

| `target`                   | `rejection_rate` | `ci_low`             | `ci_high`             |
| -------------------------- | ---------------- | -------------------- | --------------------- |
| `Naive Sign (0 threshold)` | `1.000`          | `0.996173241514445`  | `1.0`                 |
| `Centered Sign (Median)`   | `0.045`          | `0.03379951228563171`| `0.059682837936223455`|

**What is recovered, exactly.** Both intervals are Wilson score intervals at `n = 1000` and
`z = Φ⁻¹(0.975) = 1.959963984540054`, reproduced to all 17 significant digits by
`exp_R12_gjr_student.py`'s control C3 from the counts `1000/1000` and `45/1000` alone. (The
rounder `z = 1.96` does **not** reproduce them: it misses by `1.4 × 10⁻⁷` and `1.8 × 10⁻⁷`.)

**What is not recovered.** Recovering the interval construction recovers the *arithmetic*, not the
*data-generating process*. Nothing here fixes the stream length, the innovation law, the AR
coefficient, the conditional-mean estimator or the number of lags behind the two rates. The claim
these rows would support — that the whitening property holds at the **median** threshold and not at
the **zero** threshold — belongs to `sec:ar_garch` (v87 L302), which is R07's mission statement, and
R07 has already delivered it on a certified campaign of its own. R12 therefore **reads** this file
in control C3 and prints it beside R07's `phi = 0.15` cell; it rebuilds nothing, emits no macro from
it, and opens no register entry on it.

## `expB_race_condition.csv` — produced and not cited

1 000 rows, `seed / delay_frozen / delay_arf`, `seed` running `0 … 999` with no repeats.

- `delay_frozen` is populated on **all 1 000 rows**: minimum `35`, maximum `356`, mean `76.149`,
  no `-1` sentinel anywhere.
- `delay_arf` is **empty on 999 of the 1 000 rows**. The single populated row is `seed = 492`,
  which carries `delay_frozen = 78` and `delay_arf = 216.0`.

That is reported as measured. **The mechanism behind the 999 empty cells is not attributed**
(preamble §S4.5): the file's producing code does not exist in the delivered tree, so a missing
value here cannot be distinguished from a censored run, an unwritten column or an aborted arm.

`articleB_whitening_v87.tex` cites **no** frozen-versus-ARF race — neither in the two paragraphs
this stream serves (L349, L353) nor in either figure caption (`fig:leverage`, `fig:fat_tails`). The
file is therefore declared **produced and not cited**, exactly as the R12 prompt's §2.4 directs
when no citation is found. No reconstruction, no camera-ready candidate, no register entry: a
camera-ready candidate must attach to a manuscript sentence, and there is none.
