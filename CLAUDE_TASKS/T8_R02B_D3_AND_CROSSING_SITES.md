# T8 — ESTABLISH THE R02b CONTRADICTION, AND COMPLETE THE CROSSING SITES

Repository root: `/home/m53/The-Whitening-Advantage-Experiments`. Write to
`docs/audits/AUDIT_R02b.md`, `docs/DEVIATIONS.md`, `docs/camera_ready_candidates/`,
`gate_docs.sh` and `refactor_all_streams.sh`. Never write to any `.tex` or `.bib`.

## PART A — the R02b contradiction is asserted in the README and established nowhere

`README.md` section 6.1 now carries a row `R02b-iid-arm-rejection`. That identifier occurs **zero**
times in `docs/DEVIATIONS.md`, and `docs/audits/AUDIT_R02b.md` carries **zero** D3 rows. The
repository asserts a formal contradiction it does not document.

The finding is real and must be established from the evidence, in this order.

**Step 1 — read what the manuscript prints.** Line 278 of `articleB_whitening_v87.tex` states that
the squared inputs "already over-reject on the i.i.d. arm ($9.2\%$), where $t_7$ innovations deprive
$\varepsilon^2$ of a fourth moment and the $\chi^2$ approximation fails". Quote it verbatim in the
audit. Two distinct assertions are printed there: a **rate** and a **mechanism**.

**Step 2 — settle the mechanism analytically, and derive it in the audit rather than asserting it.**
The Ljung--Box limiting distribution for an i.i.d. series requires a finite variance of the *tested*
series. The tested series here is `eps^2`, so the requirement is `E[eps^4] < infinity`, i.e.
`nu > 4`, which `t_7` satisfies. The moment that fails at `nu <= 8` is `E[eps^8]`, which governs the
tail quantile of the sample autocorrelations rather than the validity of the limit. Write that
derivation in one short paragraph, with the condition it rests on named.

**Step 3 — settle it empirically from R02b's and R02c's own artefacts**, read with
`float_precision='round_trip'`. R02b swept `nu` and R02c swept the horizon precisely to discriminate
mechanisms. Two facts the campaign established and which you must re-verify rather than copy:
at `nu = 7` the rejection rate's Wilson interval contains the nominal level, while at `nu = 6` and
`nu = 5` it excludes it; and the eighth-moment account is refuted by its own control, since
`E[eps^8]` is infinite for every `nu <= 8` including `nu = 7`. If the artefacts say otherwise,
report that and stop.

**Step 4 — classify.** The *rate* is a numeral and moves under redraw: that is the existing
`R02b-nu-grid-redraw` entry and it is not what this task adds. The *mechanism* is a printed
mathematical justification that the analysis shows to be incorrect. Under the D0-D3 scale a
falsified qualitative claim is **D3**, and a false statement of the condition under which an
asymptotic approximation holds is a qualitative claim, not a numeral. Add one row to
`AUDIT_R02b.md`'s table whose `regenerated value` column names the correct condition rather than a
number, followed by the falsified-claim paragraph and a mandatory **`**Scope:**`** clause.

**The scope clause is what keeps this honest and it must be precise.** What is contradicted is the
stated *reason* the chi-square approximation fails on the i.i.d. arm. What is **not** contradicted:
that the squared inputs do over-reject there — they do, and the reproduction confirms it; the
whitening property; the exactness of the Concept threshold; and any proposition of v87. Also state
that the true mechanism is **not identified** — the campaign located the effect near the loss of the
sixth moment without establishing why, and the audit must say so rather than supply a story.

**Step 5 — the register and the candidate.** Create `R02b-iid-arm-rejection` in
`docs/DEVIATIONS.md`, class A, severity D3, with its source cells. Then reconcile it with the
camera-ready corpus: a candidate on this subject existed historically under the name
`R02b_R02c_v87_ljungbox_clause.md`. Check `docs/camera_ready_candidates/RECONCILIATION.md` and the
git history for it. If it survives under another name, attach the register identifier to it and set
its family marker to the register family — it is no longer a clarification. If it was lost, restore
it from git and verify its anchor with `grep -Fc` against the frozen manuscript.

## PART B — the crossing numeral has four manuscript sites, not three

```bash
grep -n 'nu\^{\\star}\|\\nu^{\\star}' articleB_whitening_v87.tex
```

`nu* ~ 4.9` is printed at **L57** (abstract), **L253** (body), **L372** (conclusion) and **L519**
(the caption of Figure 4). `README.md` section 6.1 lists the site of `R04b-efficiency-crossing` as
"abstract, L57, L253, conclusion": `abstract` and `L57` are the same line, and **L519 is missing**.

Correct the site list in the heredoc of `build_readme.sh` — never in `README.md`, which is
generated — to `L57 (abstract), L253, L372 (conclusion), L519 (Figure 4 caption)`. Then check that
the camera-ready candidate for this correction carries an anchor for **each** of the four sites: a
candidate that patches three of them leaves the fourth wrong in the accepted version. Verify each
anchor with `grep -Fc`, which must return exactly 1. Apply the same check to
`R04b-estimation-cost`, whose `0.3` is printed at L253 — confirm whether it appears anywhere else.

## PART C — three defects in `refactor_all_streams.sh`

The script was corrected to add Gate 4 and to index `docs/camera_ready_candidates` in
`checkpoint_vcs`. Both changes are right. Three defects remain.

1. `experiments/common/verify_camera_ready.py` is now provided. Confirm it runs clean:
   `python experiments/common/verify_camera_ready.py`. Every finding it reports is a real defect in
   a candidate file, not in the validator -- fix the candidate, and report what you fixed.
2. Gate 4 sits inside the per-stream loop but validates the whole directory, so it runs 21 times on
   the same corpus and attributes any failure to whichever stream happened to be running. Pass the
   stream id: `python experiments/common/verify_camera_ready.py "${STREAM_ID}"`. The validator
   accepts stream ids as positional arguments and filters on them.
3. The script still exports `PYTHONHASHSEED=0`. The preamble mandates `42` and every experiment
   script **verifies it** and calls `sys.exit(1)` otherwise, so the direct `python "${py_script}"`
   branch would abort. Change it to `42`.

## PART D — three false positives in `gate_docs.sh`

`logs/gate_docs_final.log` reports three findings across 21 streams. All three are defects in the
gate, not in the documentation. Verify each claim below before repairing, then repair only the
greps.

1. **R06, G8.** Line 33 of `docs/audits/AUDIT_R06.md` discusses a Wilson interval on a *rejection
   rate* -- a proportion -- to show that the naive version understates by `sqrt(design effect)`.
   Line 50 reports a Wilson interval on a rate. Both legitimate. G8's exclusion list misses lines
   that name the statistic in words other than `rate` or `fpr`.
2. **R13, G5.** Line 171 writes `Kish design effect 1 + (m - 1) * rho_bar = 7.7275`. The grep
   matched the **formula**. R13 measures its design effect at 7.73 and reports `n_eff = 11.39`,
   which is the opposite of the defect G5 exists to catch. Exclude a `1` that is followed by an
   arithmetic operator.
3. **R16, G7b.** The audit writes "The D3 row falsifies the qualitative claim in v87 L329 that..."
   and carries `**Scope:**` at line 37. G7b greps for the fixed phrase `falsified qualitative
   claim`. Broaden it to a stem match on `falsif` within the deviation-table section.

After repair, `bash gate_docs.sh` must return zero findings across all 21 streams. If a repair
makes a gate unable to fire on the defect it was written for, the repair is wrong: construct a
one-line negative probe for each of the three and show it still fires.