# AUDIT — R14, efficiency reversal on real Bitcoin

This is the only document transmitted to the orchestrator. It contains: what R14 establishes and what it does not; the ten controls with their margins and their trigger probability under their own null, including the one that fired; the complete D0–D3 classification with the source CSV cell for every value, including one D2; the reproducibility evidence; the design decisions taken outside the plan; the findings that revise the plan's own premises; and the open questions, left open.

R14 measures v87 Figure 16 (`fig:crypto_race`, caption L635) and every numeral of L345, the paragraph that carries the efficiency reversal from the synthetic Student-`t` sweep of Figure `fig:isofpr`B onto a real heavy-tailed stream.

---

## 1. What R14 establishes, in one paragraph

Running the delivered iso-FPR race on the two vendored daily crypto series — 106 monthly onsets on Bitcoin, 72 on Ethereum, `H_ref = H_det = 500` trading days, eleven drift magnitudes, both arms bisected to a common realized false-alarm rate on real placebo windows — every quantity v87 publishes about Bitcoin reproduces bit for bit: the iso-FPR `4.7%` (`5/106`), the `106` onsets, `ν̂ = 2.78`, the delay ratio `0.74` at `c = 0.35`, parity `1.01` at `c = 1.5` and the mean `0.87`. The whole `Real_BTC` block of the race table matches the submitted campaign on all 13 shared columns with a worst difference of exactly `0`. The quasi-Gaussian control does not: the 128-bit re-keying redraws the `t₃₀` series outright and its three numerals move from `0.98`–`1.14`, mean `1.06` to `0.95`–`1.24`, mean `1.04` — a Class A, D2 registered as `R14-campaign-redraw`. The qualitative claim that the control inverts the ordering holds, and the paired bootstrap interval of the regenerated mean, `[0.9793, 1.0688]`, still covers the published `1.06`. However, this interval contains `1` (parity): the claim of inversion rests on a point estimate whose 95% confidence interval enjambs parity. The statement is true of the point estimate but its evidential weight is weaker than formulated. On Ethereum, both self-critical statements of L345 reproduce: the recentred sign stream fails whiteness at `p = 0.0188` and the synthetic control does not recover the light-tailed ordering (mean ratio `0.9189`, 95% `[0.7877, 0.9616]`, entirely below parity).

One control fired. C2 — the two arms of a source must realize the same false-alarm rate — holds on the three sources whose speed comparison v87 publishes and fails on `Real_ETH`, where the re-keyed dither moves the `Concept` calibration to `4/72` while `Eco` stays at `3/72`. The handling was fixed before the run: v87 makes no delay and no ordering claim about real Ethereum, so the source is stamped `iso_fpr_matched = False`, read by no macro, and reported. Nothing was reseeded, retuned or re-toleranced.

---

## 2. Five things the reader must not take from this stream

The `_legacy_seeds` artefacts certify no v87 value. They exist to separate the re-keying moved panel B from the transcription broke panel B. They restore the delivered `RandomState(100 / 200 / 201 / 300)` draws and nothing else, they ship under stamped names, and their macro file says so in its own header. Nothing in the manuscript may be checked against them.

`ADD` is conditional on detection at every cell, including the reliable ones. `DetRate >= 0.9` is not `1`. A delay average at a reliable magnitude still averages over between 90% and 100% of onsets, and the direction of that selection is not signed. This is the same conditioning `R09-add-conditioning` registers for Figure 9B. The per-cell `DetRate`, `n_detected` and the full 7832-row per-onset table ship so that a reader can price it rather than take it on trust.

The real Ethereum ratios are not a speed comparison. Under the migrated draw the two arms run at different realized false-alarm rates, so the ratio compares two detectors at two operating points. It is persisted and printed as description only, and no macro reads it.

The synthetic controls are a control, not a second dataset. They are `t₃₀` GARCH(1,1) paths matched on one moment of their real counterpart and read at the same onsets. They establish what the same machinery does under light tails and nothing whatever about crypto markets.

`28` of `88` unreliable cells is not a v87 numeral. v87 prints the rule — hollow markers, `DetRate < 0.9` — and no count. The count is a property of the redrawn synthetic controls; the legacy arm returns the submitted `25`. The macro `\RFourteenUnreliableCells` exists because the R14 prompt section 2.1 asks for it, not because the manuscript prints it.

---

## 3. Controls, with their margins and their trigger probabilities

Which rows each control reads. C1, C2 and C5 read all four sources and gate on the three whose speed comparison v87 publishes. C3, C8 and C9 are per-source or per-cell and read everything. C4 reads the two diagnostic rows. C6, C7 and C10 read no data at all: they are static or reproducibility controls.

### C1 — no aggregate reads a cell the caption draws hollow

Structural; trigger probability 0. The pairwise-reliable grid is computed once, every published aggregate is taken over it, and the grid is then re-derived from the persisted CSV and compared with the in-memory one. `28` of `88` cells carry `add_reliable == False` and none enters an aggregate.

The rule is `both arms at DetRate >= 0.9` and not the delivered literal `c >= 0.35`. That the two coincide is a statement about the submitted campaign and is asserted against the witness by the test suite: on `protocol_24b_crypto_isofpr_race.csv` the derived rule selects exactly `{0.35, 0.5, 0.6, 0.75, 1.0, 1.25, 1.5}` for `Real_BTC` and for `Synth_BTC`, seven magnitudes, which is the length of the seven-element reference vectors the delivered `verify_invariants` carries. That agreement is what licenses replacing the literal.

### C2 — one realized false-alarm rate per source — FIRED on `Real_ETH`

Deterministic given the data; trigger probability 0 once the draw is fixed. The scope was fixed before the run, read clause by clause off v87: `Real_BTC`, `Synth_BTC` and `Synth_ETH` carry a published speed comparison and stop the run if their match fails; real Ethereum carries none.

The fragility was logged before the outcome was read, and it is arithmetic, not a draw. `bisect_fpr` breaks when `|k/N - 0.05| <= 0.005`, and a realized rate can only take the values `k/N`. At `N = 106` exactly one integer qualifies, `k = 5` — which is v87's `4.7%` — so the BTC agreement is forced by the tolerance. At `N = 72` no integer qualifies: `3/72 = 4.17%` and `4/72 = 5.56%` straddle the band, the bisection exhausts all forty iterations, and any ETH agreement is an outcome of its dynamics rather than a constraint the calibration enforces.

What was done about it: nothing to the draw. The `Real_ETH` rows carry `iso_fpr_matched = False`, no macro reads a speed comparison from that source, its ratio series is logged with the caveat attached, and the audit reports it.

### C3 — the QMLE fallback counters, reported even at zero

Reporting obligation, no gate on the counters themselves.

The G2 band is a band on the instrument and its limit is stated. The delivered gate is `median bias < 0.05` and `fallback fraction < 0.10`. The null distribution of a median over twenty simulations has no closed form, so no trigger probability is quoted for it; the gate is kept because it guards the measuring instrument and not a published claim, and the log states before reading it that a firing would be characterised and reported, never reconciled by reseeding.

### C4 — the moment condition, derived at run time from the fitted nu_hat

Derivation, not a gate. For a Student-t standardized to unit variance, `E|z|^p < infinity iff p < nu`; hence the variance exists iff `nu > 2` and the fourth moment iff `nu > 4`. The script evaluates that one line at the value just measured rather than reciting a conclusion.

Consequence, logged: with `E[z^4]` infinite, the GARCH penalty Gamma — a functional of the autocorrelation of eps^2, which needs a finite fourth moment of z — and the chi-square limit of a Ljung-Box on squared residuals are both unjustified on the Data pipeline v87 contrasts against. Stated precisely, because the imprecise version would be wrong: the Ljung-Box actually computed in this stream is on the sign stream, which is bounded, so its own chi-square approximation is untouched by this. The caveat is about the Data pipeline, and the regime it describes is what Figure 16 illustrates rather than a defect of the protocol.

### C5 — direction, measured and not gated

The delivered Control (d) reads the synthetic ratio at `min(reliable c)` and calls `sys.exit(1)` when it is at or below `1.05`. A minimum over a grid is an extremum statistic with no sampling distribution, which the fourth corollary of the specifications bans outright, and the R14 prompt's own C5 says characterise, do not correct. It is replaced by a measurement.

Family-wise arithmetic, logged before the result was read. Over the seven paired magnitudes of `Real_BTC` a sign test has trigger probability `2 * 0.5^7 = 1.5625%` under exchangeability of the two arms. Reading a 95% band as a maximum over seven points would trigger with probability `1 - 0.95^7 = 30.2%` under its own null, which is why the extrema below are descriptive and gate nothing.

### C6 — ast source identity

Static; trigger probability 0 unless a copy has drifted. Ten segments, 3675 characters compared, 0 differences: `_garch_nll`, `fit_garch_qmle`, `strict_cusum`, `bilateral_delay`, `bisect_fpr`, `wilson_ci` and `compute_onsets` against `data/reference/R14/Priorite_24d_crypto_isofpr_race.py`, and `get_deterministic_seed`, `seed_sequence_for` and `rng_for` against `experiments/R13_oracle_ceiling/exp_R13_oracle_ceiling_a.py`.

The duplication is deliberate and the evidence is machine-checked. A diff against this repository's other copies shows `_garch_nll`, `fit_garch_qmle`, `strict_cusum` and `wilson_ci` all differ between R14's witness and the R01/R03/R04/R04b/R11/R13 copies — R04's `fit_garch_qmle` carries a multistart ladder and a persistence projection R14's does not, and R01's carries `tol=1e-8`, `maxiter=1000` and a `round(., 6)` R14's does not. Hoisting or borrowing any of them would move published values, which is what the specifications forbid.

### C7 — two consecutive runs, identical SHA-256

Deterministic; trigger probability 0. Twelve artefacts, both sets identical.

### C8 — non-anticipativity, on the full pre-onset parameter vector

Structural and tautological by slicing; trigger probability 0. The delivered check compares `mu_hat` before and after `r[onset:] += 100`. It is extended to the eight quantities the detector actually consumes — `mu_hat`, `med_hat`, `q_hat_ref`, `omega`, `alpha`, `beta`, `eps_last`, `s2_last` — because a leak through any one of them would be invisible to a comparison on the mean alone. All eight are bit-identical on all four sources. The identity holds because `r[onset - 500 : onset]` cannot reach past `onset`; it is recorded as a structural assertion that a future reordering of the slicing cannot pass silently, and not as evidence of anything.

### C9 — the design effect, computed and logged before every `sqrt(n)`

Reporting obligation, mechanically enforced. `K = ceil(H_det / 21) = 24` comes from the mechanism: consecutive onsets are about 21 trading days apart, and a detection window is 500 trading days, so two onsets more than 24 monthly steps apart share no observation. The specifications forbid reading `K` off the observed autocorrelation, and it is not.

The delivered `SEM`, `CI_low` and `CI_high` are kept unchanged for witness comparability and `deff`, `n_eff`, `SEM_design`, `CI_low_design` and `CI_high_design` are added beside them. No printed v87 numeral depends on either. The figure's band is `SEM_design`. On the `Real_BTC` reliable grid the dependence sits almost entirely on the `Eco-L1` arm. 54 of the 88 cells return a Kish sum below 1, which would claim more independent readings than the cell contains; each is clamped to 1.0 with its own log line.

### C10 — the dropped global seeds are provably unconsumed

Static; trigger probability 0. The delivered script sets `np.random.seed(42)` and `random.seed(42)` at module level and this port drops both, which is admissible only if no draw consumed them. An ast walk over the witness establishes that no `np.random.<distribution>` call exists anywhere in it — the only `np.random` members it touches are `RandomState` and `seed` — and that it constructs exactly three `RandomState` instances. The same walk over this script requires that no draw reach the global stream and that `np.random.RandomState` appear only inside the three legacy-seed brokers.

### Every multi-test control logs `1 - (1 - p)^m` before its result is read

The two families of this stream are C5's sign test over `m = 7` paired magnitudes (`2 * 0.5^7 = 1.5625%`) and the per-magnitude envelope read as a maximum over the same seven (`1 - 0.95^7 = 30.2%`). Both are logged before the ratios are read, and the second is the reason `\RFourteenRatioSynthMin` and `\RFourteenRatioSynthMax` gate nothing. C1, C6, C7, C8 and C10 are structural or static and carry no null to arithmetise; C2 is deterministic once the draw is fixed; C3, C4 and C9 are reporting obligations.

---

## 4. Deviation classification against v87

### The complete D0–D3 table, with the source cell of every value

Classification is at v87's own printing precision. Witness is `data/reference/R14/protocol_24*.csv` read at `float_precision='round_trip'` by the script itself; no reference literal is transcribed by hand.

| # | v87 location | printed | source cell | witness | regenerated | class |
|---|--------------|---------|-------------|---------|-------------|-------|
| 1 | L635, L345 | `4.7%` | `R14_crypto_diagnostics.csv`, `BTC`, `FPR_C_real` = `FPR_E_real` | `0.04716981132075472` | `0.04716981132075472` | D0 |
| 2 | L635, L345 | `106` | `R14_crypto_isofpr_race.csv`, `Real_BTC`, `n_onsets` | `106` | `106` | D0 |
| 3 | L635, L345 | `2.78` | `R14_crypto_diagnostics.csv`, `BTC`, `nu_hat` | `2.7791143512276766` | `2.7791143512276766` | D0 |
| 4 | L345 | `0.74` | race, `Real_BTC`, `c = 0.35`, `ADD` ratio | `0.7407126611068993` | `0.7407126611068993` | D0 |
| 5 | L635, L345 | `1.01` | race, `Real_BTC`, `c = 1.5`, `ADD` ratio | `1.0074285714285713` | `1.0074285714285713` | D0 |
| 6 | L345 | `0.87` | race, `Real_BTC`, mean over 7 pairwise-reliable `c` | `0.8682292705270857` | `0.8682292705270857` | D0 |
| 7 | L345 | `0.98` | race, `Synth_BTC`, minimum over the same 7 | `0.9818435754189944` | `0.9544910179640719` | D2 |
| 8 | L345 | `1.14` | race, `Synth_BTC`, maximum over the same 7 | `1.1426127128069126` | `1.2384142067139186` | D2 |
| 9 | L345 | `1.06` | race, `Synth_BTC`, mean over the same 7 | `1.0603026678597007` | `1.041041514153539` | D2 |
| 10 | L345 | `0.019` | `R14_crypto_diagnostics.csv`, `ETH`, `lb_pvalue` | `0.018785617996181257` | `0.018785617996181257` | D0 |
| 11 | L345 | `72` | race, `Real_ETH`, `n_onsets` | `72` | `72` | D0 |

Rows 1–6, 10 and 11 are bit-identical, not merely equal at printing precision. Rows 7–9 are D2. The qualitative claims all hold: the control still inverts the ordering (mean > 1), and the paired bootstrap interval `[0.9793, 1.0688]` still covers the published `1.06`.

### `R14-campaign-redraw` — Class A, D2

The single register entry. The specifications require migrating the delivered `RandomState(100 / 200 / 201 / 300)` draws onto a 128-bit `SeedSequence` keyed on role and index alone. Three numerals of the quasi-Gaussian control move at v87's printing precision.

The mechanism is established by a counterfactual that was run. The `--legacy-seeds` arm restores the delivered integer seeds and keeps every other change of this port — the `round_trip` parser, the BLAS pinning, the assertion at every QMLE call site, the derived reliability rule, the extended non-anticipativity check. It reproduces the witness on all 88 cells of `ADD`, `DetRate`, `SEM`, `FPR_achieved`, `n_onsets` and `add_reliable`, and on both diagnostic rows of `nu_hat`, `lb_pvalue`, `FPR_C_real` and `FPR_E_real`. Exactly two quantities drift in it, and both have a mechanism: `lambda_star` for `Real_ETH` and `Synth_ETH` (the only two bisections that never break early) and `Var_z_hat` (both assets, moved by one ULP from the parser change amplified by SLSQP's tolerance). Neither perturbation changes a single delay: `ADD` moves on `0` of `88` cells in that arm. A transcription error is therefore excluded, and the whole movement of the default arm is the re-keying.

Why the severity is D2 and not more. L345's qualitative claim about panel B is that the t_30 control inverts the ordering to Eco-L1-faster. Its falsification condition, fixed before the run, is that the 95% interval of the regenerated mean lie entirely below 1. It is `[0.9793, 1.0688]`, so the claim stands, and the interval additionally covers the published `1.06`: the move is not distinguishable from the redraw's own noise. Note that this interval contains 1 (parity), which means the evidence for the inversion is statistically weak, though the point estimate claim remains true.

---

## 5. Reproducibility and the whole suite

Execution is performed via `run_experiment_R14.sh`, which runs both the migrated arm and the `--legacy-seeds` port-fidelity diagnostic unconditionally. `run_all.sh` discovers `run_experiment_R14.sh` by sorted enumeration. `run_all.sh`, `run_tests.sh`, `logs/all_tests.log`, `README.md` and every `.tex`/`.bib` of the manuscript are untouched.

### C7 — Deterministic reproduction

Two consecutive runs produce byte-identical artefacts on all twelve outputs. The two vendored input series are digest-asserted at start-up against the values the submitted campaign recorded.

### The test suite

All 358 tests pass, of which 26 are R14's. No blocking assertion rests on a continuous value R14 produced; each rests on one of four things: a value v87 prints compared at v87's printing precision; an arithmetic fact independent of any run; a relation reimplemented in the test file independently of the experiment; or, on the `_legacy_seeds` arm alone, a discrete quantity of the witness. The witness is deliberately not a gate on the default arm; on the `_legacy_seeds` arm it is a gate on discrete quantities only. `ADD` is given no tolerance on either arm.

---

## 6. Design decisions taken outside the plan

1. C2's blocking scope. The plan states C2 as an exact equality assertion, per source and, separately, that if the two ETH arms land on different counts the ETH race is not iso-FPR and no ETH speed comparison is interpretable; that is reported, not repaired. Those two are only jointly satisfiable if the assertion halts on the sources whose speed comparison v87 publishes and records the failure elsewhere. The set `{Real_BTC, Synth_BTC, Synth_ETH}` was read clause by clause off L345 and is written into the source with that derivation beside it. It is a scope fixed by what the manuscript says, not by which source turned out to fail, and the run would have stopped had the mismatch landed on any of the three.

2. A mirror D3 test on `Real_BTC`. The plan fixes the D3 falsification condition for panel B only. The specifications require halting on any falsified qualitative claim, and L345 makes one about Bitcoin too, so the symmetric test — the interval lying entirely above 1 — is implemented and evaluated. It does not fire.

3. The onset bootstrap carries no legacy keying. The plan's entropy table marks it new, and `--legacy-seeds` restores the delivered `RandomState(100/200/201/300)` draws and nothing else. A draw with no delivered counterpart therefore has no legacy form, and the bootstrap uses `rng_for` in both arms.

4. Four delivered gates are kept as they stand. The plan lists six non-negotiable corrections and none of them touches the iso-FPR band `[0.03, 0.07]`, `|diff| <= 0.015`, the deviation ceiling `max |dev| <= 1.0`, G1 (`nu_hat < 4.7` on at least one asset) or G2 (the QMLE recovery band). All four are kept, all four pass, and G2's missing trigger probability is declared rather than papered over.

5. `requirements/R14.txt` carries `pytest`. The script does not import it; `tests/test_R14_claims.py` does, and it is a deliverable of the same stream. `requirements/R13.txt` sets the precedent. All six versions are read by `importlib.metadata.version()` at run time and written by the script.

6. Columns beyond the plan's list. `FPR_count`, `iso_fpr_matched`, `n_detected`, `deff_clamped`, `deff_lags`, `qmle_n_non_converged`, `qmle_n_frozen` and `qmle_fallback_frac` were added to the race CSV so that C2's integer counts, C1's flag, C3's obligation and C9's clamp are each checkable from the file alone rather than from the log.

7. The figure's band is `SEM_design`, and the delivered `SEM` still ships. The plan requires both; this records that the visible band is the honest one and the witness-comparable column is the persisted one, so a reader comparing the PNG with `protocol_24b` is comparing different quantities by design.

---

## 7. Findings that revise the plan's own premises

1. The R14 prompt's section 2.3 is wrong, and the direction of the error matters. The caption indeed says nothing about Ethereum. L345 does. It publishes five ETH statements: the Ljung-Box `p = 0.019`, the `72` onsets, that the recentred sign stream fails whiteness, that the fair-coin pivot does not hold exactly, and that the synthetic control does not recover the light-tailed ordering. ETH is therefore a published claim to be reproduced and classified, and rows 10, 11 of section 4 do that. The direction matters for the specifications' asymmetry rule: v87 states its own limitation here, so reproducing the failure reproduces a self-critical claim and takes ordinary scrutiny rather than the heavier examination reserved for results that favour the manuscript.

2. C2's trigger probability was quoted as 0 given the data, and the control fired. The plan's own C2 row logged the fragility that caused it — the tolerance admits one count at `N = 106` and none at `N = 72` — and its Known risks section pre-declared the handling. The measured event is the anticipated branch, not a surprise; what the plan did not anticipate is that 0 given the data was conditional on a draw the plan itself required to be replaced. A trigger probability conditional on the draw being kept is not a trigger probability for a stream whose specification redraws.

3. The plan's row-count estimate for the added artefact is wrong. It states ~9.3k rows for `R14_onset_delays.csv`. The design gives `11 magnitudes * 2 arms * (106 + 72 + 106 + 72) onsets = 7832` rows, and that is what ships. The test suite asserts the arithmetic rather than the estimate.

4. `Synth_ETH` carries seven pairwise-reliable magnitudes, not eight. The plan's witness table records Synth_ETH mean ratio `0.5418` (< 1), 8 pairwise-reliable c. That is the witness figure and the legacy arm reproduces it exactly. Under the migrated draw `c = 0.25` loses reliability and the grid is seven long, which is why the regenerated mean is `0.9189` rather than `0.5418`. The claim it supports — that the control does not recover the light-tailed ordering — holds on both grids, and the interval `[0.7877, 0.9616]` lies entirely below parity.

5. The plan's D2 criterion is stricter than the specifications', and the specifications prevail. The plan writes: A printed numeral moving is D2: the condition is that the 95% interval of the regenerated mean excludes the printed `1.06`. The interval does not exclude `1.06`, while the printed rounding does change (`1.06 -> 1.04`). The specifications define D2 as the rounding at the manuscript's printing precision differing while the qualitative claim holds, and the preamble prevails over the plan without exception. The entry is therefore registered as D2, and the fact that the interval covers the published value is reported as the reason the severity is not more.

6. The real arm moved even less than the plan predicted. The plan states that the real BTC/ETH results depend on the migration only through the +/-1e-6 dither. On BTC the dependence is not merely small: not one of the 22 `Real_BTC` cells moves in any of the thirteen shared columns. On ETH the same dither does move a calibration, which is finding 2 above; the two outcomes differ because the tolerance forces the BTC count and leaves the ETH one free.

---

## 8. Open questions, left open

1. Why does `round_trip` parsing move `Var_z_hat` by `4.7e-09` while `nu_hat` and `lb_pvalue` are bit-identical? The traced route is that a one-ULP change in the parsed returns propagates through a 2800-step variance recursion into SLSQP, whose finite convergence tolerance returns a parameter vector differing at the ninth digit; `np.var(z_hat)` is a direct sum and shows it, while `stats.t.fit` and the Ljung-Box are optimiser and rank statistics that absorb it. The route is plausible and not measured, so the specifications forbid asserting it. What is measured is that no delay moves.

2. Is the loss of the `Real_ETH` iso-FPR match a property of this particular key, or of most keys? Answering it means running many re-keyings and reading a control's outcome across them, which is precisely the selection surface the specifications close. The question is posed and not settled; what can be said without opening that surface is the arithmetic, which shows the match was never enforced at `N = 72`.

3. The design effect is measured on the delay series and applied to the detection-rate interval. `CI_low_design` and `CI_high_design` evaluate the carried Wilson interval at `n_eff = n_det/deff`, where `deff` is the Kish factor of the delay mean. Whether the detection indicator carries the same dependence is not measured. No published numeral depends on it, and the plan prescribes this construction, but the two are different statistics and the substitution is an assumption.

4. 54 of 88 cells return a Kish sum below 1. Whether that is finite-sample noise in the 24 autocorrelation estimates or a genuine negative dependence between overlapping detection windows is not settled here. The clamp is conservative in the direction that matters — it never narrows an interval below the independent one — but a negative dependence, if real, would mean the independent interval is itself too wide on those cells.

5. Should `\RFourteenUnreliableCells` be published at all? v87 prints the rule and not the count, and the count is a property of the redrawn synthetic controls: it is `28` here and `25` in the submitted campaign. The macro exists because the R14 prompt section 4 lists it. Whether a camera-ready revision should quote a count that moves with the draw is a question for the orchestrator, not for this stream.

6. Is `Real_ETH`'s lost iso-FPR match the same phenomenon L345 calls the fair-coin pivot does not hold exactly? The two are consistent — a non-white recentred sign stream is exactly what makes the `Concept` arm's placebo crossing count refuse to sit where the calibration wants — but this stream measures no link between the Ljung-Box rejection and the bisection outcome. The association is recorded and no mechanism is attributed.
