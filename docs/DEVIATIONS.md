# Deviations between this repository and the submitted manuscript

The manuscript was submitted on 2026-07-27 and is frozen. This repository was built
afterwards and, in the course of hardening the experimental code, corrected defects that
were present in the code used to produce the submitted results. Where a correction changed
a published quantity, the change is recorded here. **This file is the index; each entry
links to the experiment section that documents it in full.**

Nothing in this repository is adjusted to match the manuscript. Where the two disagree, both
values are printed and the reason is stated.

## Classification

- **Class A — correction of a defect in the submitted code.** The submitted code did
  something other than what the manuscript describes. The repository cannot ship the defect,
  so the deviation is unavoidable.
- **Class B — environment hardening.** The submitted code was correct; the environment was
  not reproducible. The submitted values remain exactly recoverable, and the command that
  recovers them is given.
- **Class C — presentation.** Figure formatting only; no numerical content changes.

## Severity

- **D0** — same conclusion, same printed value; only sub-display-precision digits move.
- **D1** — value moves below the manuscript's printing precision.
- **D2** — a printed value changes; the qualitative claim it supports still holds.
- **D3** — a qualitative claim of the manuscript is not reproduced.

## Register

| id                                | Experiment | Manuscript location                        | Class | Severity | One-line summary                                                                                              |
| --------------------------------- | ---------- | ------------------------------------------ | ----- | -------- | ------------------------------------------------------------------------------------------------------------- |
| `R01-variance-target`             | R01        | Table 2 caption, Figure 2                  | A?    | D0       | `omega`, `sigma_unc` move by at most 2.7e-14 relative; no published number changes; **cause unidentified**    |
| `R02-binary-error-rate`           | R02        | Section "Empirical Boundaries"             | A     | D2       | pooled binary-error rejection 4.4% → 4.2%; Wilson [2.8, 7.1]% → [2.5, 6.8]%                                   |
| `R02b-iid-arm-rejection`          | R02 / R02b | Section "Empirical Boundaries"             | A     | **D3**   | the i.i.d.-arm over-rejection claim is not reproduced at `t_7`                                                |
| `R02-figure-1-redraw`             | R02        | Figure 1                                   | A     | D2       | the figure is regenerated from the corrected campaign, so its underlying data differ                          |
| `ALL-figure-presentation`         | all        | all figures                                | C     | —        | bold panel titles, uppercase `(A)`/`(B)` labels, some panels merged into single images                        |
| `R02c-mechanism-constraints`      | R02c       | Section "Empirical Boundaries"             | A     | —        | no manuscript claim affected; constrains the admissible explanation in camera-ready                           |
| `R03-cusum-nominal-level`         | R03        | Section "FPR explosion"                    | A     | D2       | the StrictCUSUM i.i.d. level is 2.0%, not the 5% the text ascribes to it                                      |
| `R03-campaign-redraw`             | R03        | Section "FPR explosion", Fig. 3            | A     | D2       | 128-bit seeding redraws the campaign; every printed rate moves, no claim moves                                |
| `R05-concept-threshold-numeral`   | R05        | Section "Scaling Validation"               | A     | D2       | the Concept threshold numeral `lambda_C = 10` matches no campaign of the study                                |
| `R05-campaign-redraw`             | R05        | Section "Scaling Validation", Appendix B   | A     | D2       | 128-bit seeding redraws both scaling campaigns; every Monte-Carlo value moves                                 |
| `R05-recalibration-residual`      | R05        | Appendix B                                 | A     | D2       | "residual on the conservative side" is `-1.4%` at one of five penalties                                       |
| `R05-sixth-moment-attribution`    | R05        | Appendix B                                 | A     | —        | the sixth-moment attribution is unsupported by R05; its two numerals are exact                                |
| `R04-gamma-grid-defect`           | R04        | Section "Sensor Mismatch"                  | A     | **D3**   | the submitted `Gamma` grid never varied due to a transposed parameter argument                                |
| `R04b-efficiency-crossing`        | R04 / R04b | Section "Discussion", abstract             | A     | **D3**   | the efficiency crossing `nu* ~ 4.9` is falsified; R04b encloses it in `[7, 9]` and prices the cost at `3.6`   |
| `R05-regime-column-contradiction` | R05        | Appendix B                                 | A     | —        | `regime` column contradicts the appendix; sixth-moment gloss is wrong (`E[eps^6]` is 3rd moment of `eps^2`)   |
| `R04b-calibration-variance`       | R04b       | —                                          | —     | —        | methodological: a threshold calibrated on a finite sample gives held-out counts twice the binomial variance   |
| `R06-fourth-moment-boundary`      | R06        | Figure 6 and its caption                   | A / C | D1       | the fourth-moment boundary is now computed (`41.58`, printed `41.6`); the figure conflated it with `Γ = 41`   |
| `R04b-oracle-ratio-offset`        | R04b       | Section "Discussion"                       | A     | D3       | the oracle curve exceeds its analytic prediction everywhere (+5%); the crossing does not track the prediction |
| `R11-onset-convention`            | R11        | Figure 15B caption, `sec:universality`     | A     | —        | the four caption delays were measured under two different onset conventions and are not comparable            |
| `R11-cusum-add`                   | R11        | Figure 15B caption                         | A     | D2       | `Concept` CUSUM delay `28.3` → **`28.4078`**                                                                  |
| `R11-pht-slope`                   | R11        | `sec:universality`, L298                   | A     | D2       | log-log PHT slope `1.09` → **`1.0977`** on 12 of 20 points, delays conditional on detection                   |
| `R11-pht-syncope`                 | R11        | `sec:universality`, L298                   | A     | D2       | "beyond `Γ ≈ 75`" → first point below 50% detection at **`Γ = 91.11`**                                        |
| `R11-pht-gamma-rule`              | R11        | `sec:fpr_explosion`, L171; Fig. 15 caption | A     | D2       | the PHT's `λ × Γ` rule holds no level: **14.46%** at the floor, **1.62%** at `Γ = 200`                        |
| `R11-figure11-caption`            | R11        | Figure 11 caption                          | A     | D2       | the caption applies panel A's `c=2 / n=1000` to a figure whose panel B is `c=1.5 / n=5000`                    |
| `R11-gamma-grid-floor`            | R11        | `sec:universality`, L296                   | A     | —        | the lower endpoint of "`Γ ∈ [1, 200]`" is not attainable at `alpha = 0.08`; the grid starts at `1.1739`       |
| `R11-regenerated`                 | R11        | Figures 11 and 15                          | A     | D2       | 128-bit re-keying redraws the whole campaign; every Monte-Carlo value moves, no claim moves                   |
| `R18-ljungbox-power`              | R18        | L278, L290, Fig. 6 caption L286, L318      | A     | —        | four Ljung--Box non-rejections are stated unqualified; the test resolves `rho_1 = 0.051` at `n = 8000`        |
| `R16-dating-misdescription`       | R16        | `sec:real_world`, L329                     | A     | **D3**   | a Pagan--Sossounov dating of the four streams yields **48** phases, not the `66` L329 attributes to it        |
| `R16-covid-phase-conditional`     | R16        | `sec:real_world`, L331                     | A     | —        | L331's four numerals reproduce exactly; the phase exists only under the SPY substitution                      |
| `R16-floor-frac-envelope`         | R16        | `sec:real_world`, L329                     | A     | D2       | `55--92\%` → **`50--92\%`**; cause **not identified**                                                         |
| `R16-boundary-sensitivity`        | R16        | `app:repro`, L392                          | A     | —        | 3 of 66 phases flip with the convention, all one way; the count is `[53, 56]`, never reported                 |
| `R16-sign-arm-disagreement`       | R16        | `sec:real_world`, L329                     | A     | —        | "moves that count by one phase" is a net of 10 and 9; the arms disagree on 19 of 66                           |
| `R16-substitution-scope`          | R16        | `sec:real_world`, L329                     | A     | —        | the published fraction is conditional on the substitution reaching one ticker of four: 80.3% → 73.5%          |

*Entries are added as each experiment is certified. Streams R06 onwards are not yet complete;
this register is not final.*

---

### 1 — R01, variance target (class undetermined, D0)

`omega` and `sigma_unc` move by at most 2.7e-14 in relative terms against the submitted
campaign. `alpha`, `beta`, `gamma_hat`, `q_hat`, `n_days` and every Ljung-Box p-value are
bit-identical, and **every macro in `R01_claims.tex` is unchanged**: no published number moves.

**The cause is not identified, and one candidate has been tested and rejected.** A
`--legacy-blas` mode was added to test whether the drift came from BLAS thread pinning. It
lifts the pins and `MKL_CBWR`, and it reproduces the compliant output bit for bit without
recovering the submitted values. The hypothesis is refuted. It was weak on inspection as well:
the variance target is a one-dimensional NumPy reduction, which does not dispatch to BLAS.

Until the cause is established, this entry is not classified: it may be an environment
difference (class B, in which case the submitted values remain recoverable by some command we
have not found) or a code difference introduced during hardening (class A, in which case they
are not). The drift is bounded and affects no published quantity either way.

### 2 and 3 — R02 and R02b, whitening verification (Class A)

Two defects in the submitted code:

1. The script fell back to a majority-class stub whenever `river` was absent, and `river` was
   absent from the pinned requirements. The manuscript specifies an online Hoeffding Tree.
   Both learners produce an error rate near 0.5 on a sign stream, so no output revealed which
   one had run.
2. The 128-bit seed digest was truncated to its leading 32 bits.

Correcting both draws a different, equally valid set of 360 trajectories. Consequences:

**Pooled binary-error rate (D2).** 4.4% → 4.2%, Wilson [2.8, 7.1]% → [2.5, 6.8]%. The nominal
5% level remains inside the interval, so the claim that the binary error stream holds its
nominal level is unaffected. The per-regime range printed in the manuscript, 3.3-5.0%, is
reproduced exactly.

**i.i.d.-arm over-rejection (D3).** The manuscript reports that the squared inputs "already
over-reject on the i.i.d. arm (9.2%), where `t_7` innovations deprive `eps^2` of a fourth
moment and the chi-square approximation fails". Three findings, of decreasing importance:

- **The mechanism as stated is incorrect, independently of any sample.** For an i.i.d. series
  the Ljung-Box asymptotics require a finite variance of the tested series; with `Y = eps^2`
  that is `E[eps^4] < inf`, hence `nu > 4`, which holds at `t_7`. The moment that is missing
  below `nu = 8` is `E[eps^8]`, the fourth moment of `eps^2`, which governs the tail quantile
  rather than the validity of the limit.
- **The phenomenon is real, at heavier tails than stated.** A dedicated sweep (R02b, 1000
  streams per point) measures 8.8% at `nu = 5` (Wilson [7.2, 10.7]%) and 7.9% at `nu = 6`
  ([6.4, 9.7]%), both excluding the nominal level, against 5.8% at `nu = 7` ([4.5, 7.4]%). A
  negative control applying the same test to `eps_t` itself holds the nominal level at all six
  grid points, so the distortion is specific to the squaring step.
- **The published number is not itself an error.** Under a true rate of 5.8%, observing 11 or
  more rejections out of 120 has probability 8.9%. The submitted campaign reported an ordinary
  draw; what does not follow from 11/120 is the inference of a systematic effect.

The mechanism behind the measured transition is not identified. A convergence-rate explanation
predicts the transition point but fails its own counterfactual: the rejection rate at `nu = 5`
is flat across horizons from 2,000 to 128,000 steps. This repository asserts no mechanism.

See `docs/sections/R02.md` and `docs/sections/R02b.md`.

### 4 — R02, Figure 1 (Class A, D2)

Figure 1 in this repository is generated by the corrected script and therefore rests on the
corrected campaign. Re-plotting the submitted CSV files instead would produce a figure that
the shipped code does not generate, which is a worse failure of correspondence than a
documented difference. The visual conclusion — squared inputs rejecting throughout the
clustered regimes, binary errors at nominal — is unchanged.

### 5 — All experiments, figure presentation (Class C)

Every figure carries bold, left-aligned panel titles prefixed `(A)`, `(B)`, `(C)`, matching
the panel letters already used in the manuscript captions. Figures rendered in the manuscript
as multiple LaTeX subfigures are emitted here as single multi-panel images. No numerical
content is affected. Two manuscript captions ("Left:"/"Right:") do not carry panel letters and
are therefore desynchronised from the repository figures; this is noted in the relevant
experiment sections.

### 6 — R02c, mechanism explanation constraints (Class A, —)

R02c neither adds nor removes a manuscript claim: it constrains the causal explanation that a
camera-ready revision may offer for the over-rejection. Specifically, it rules out attributing
the effect to a convergence-rate delay, leaving the alternative hypothesis (asymptotic quantile
breakdown) untested. As this establishes an interpretative boundary without altering a numerical
finding of the paper, the severity is null. See `docs/sections/R02c.md`.

### 7 — R03, StrictCUSUM nominal level (Class A, D2)

The manuscript describes the StrictCUSUM as "calibrated to a 5% nominal level under i.i.d.
noise". The submitted campaign contains nothing that could support or refute this: its lowest
grid point sits at `Gamma = 1.174` with `alpha = 0.08` and `beta = 0`, which is an ARCH(1)
stream, not an i.i.d. one.

R03 adds an arm at `Gamma = 1` exactly (`alpha = beta = 0`), 300 streams of 5000 steps, with
the same innovations, the same standardisation chain, the same detectors and the same
thresholds as the grid. The script asserts `compute_gamma_exact(0, 0) == 1.0` before running
it.

| Detector    | FPR at `Gamma = 1` | Wilson 95%  | contains 5% |
| ----------- | ------------------ | ----------- | ----------- |
| StrictCUSUM | 2.0% (6/300)       | [0.9, 4.3]% | **no**      |
| ADWIN       | 5.0% (15/300)      | [3.1, 8.1]% | yes         |

The descriptor is accurate for the window-mean detector and inaccurate for the CUSUM. This is
not a defect of the detector: `lambda_iid = 65` is a conservative threshold, a legitimate
design choice, and a conservative i.i.d. level makes the explosion the section documents start
from a lower base. What is inexact is calling that threshold calibrated to 5%. **No figure,
table or theorem depends on the descriptor.** See `docs/sections/R03.md` and the parked
candidate `docs/camera_ready_candidates/v87_cusum_nominal_level.md`.

### 8 — R03, regenerated campaign (Class A, D2)

Two defects in the submitted seeding, both required to be corrected by the specifications:

1. The 256-bit digest of `make_seed` was truncated to its leading 32 bits, the same truncation
   already recorded for R02 at entry 3. The 300 stream seeds of protocols 1A and 1B are in fact
   collision-free at that width, so no collision occurred; the correction is required by the
   128-bit entropy rule, not by an observed failure.
2. Protocol 2C keyed its `H_0` seed stream on `int(lambda_c * 1000 + delta_c * 100000)`, which
   maps the 15 grid cells onto **12 distinct keys**: `(5.0, 0.02)` collides with `(2.0, 0.05)`,
   `(10.0, 0.02)` with `(2.0, 0.1)`, and `(10.0, 0.05)` with `(5.0, 0.1)`. Three pairs of cells
   therefore shared a realisation where the code intended independent entropy. This affects
   `R03_sensitivity.csv` only, which no version of v87 cites.

Correcting both draws a different, equally valid campaign, so every rate printed in
`sec:fpr_explosion` moves at the manuscript's printing precision. The classification of all
eleven published quantities is in `docs/sections/R03.md`; every one is D2 and every qualitative
claim of the section holds: the uncorrected rates explode with `Gamma`, `lambda x Gamma` holds
the nominal level (4.0% maximum), `lambda x sqrt(Gamma)` leaves a residual plateau (29.8%
mean), and the ADWIN correction contains the rate below 13% (9.6% mean).

One consequence deserves separate mention because it bears on how the section is certified.
The regenerated minimum of `FPR_raw` over `Gamma > 20` is 74.3%, below the 76.0% of the
submitted campaign. A certification gate placed on that minimum would abort the run while no
claim of the manuscript is contradicted. R03 therefore certifies on aggregates over the grid
region rather than on extrema; the reasoning is in the "Control design" section of
`docs/sections/R03.md`.

### 9 — R05, the `lambda_C` numeral (Class A, D2)

`sec:scaling_validation` states the Concept CUSUM was "fixed once and for all, `lambda_C = 10`,
`delta_C = 0.1`". Read in `float_precision='round_trip'`, the numeral matches no campaign of
the submitted study: the threshold was calibrated per horizon, at **10.8** for the abrupt
campaign (`H = 5,000`), **15.81** at `H = 2x10^5` and **19.02** at `H = 3x10^6`. R05
regenerates 11.40, 16.00 and 18.80.

What the sentence gets right, and what carries Proposition `prop:orthogonality`, is that the
threshold is fixed **with respect to `Gamma`**: constant within each campaign while the Data
threshold runs from 52.4 to 943.3 on the same rows. Only the numeral is wrong, and the
correction moves it onto a value the manuscript derives elsewhere — `lambda_star = 11.4`, from
the attainable-level analysis in "What ``exact'' means here". The submitted 10.8 realised a
9.5% level against a 5% target; the corrected campaign realises 5.5%.

`delta_C = 0.1` is correct and untouched. No figure, table or theorem depends on the numeral.
See `docs/sections/R05.md` and the parked candidate
`docs/camera_ready_candidates/v87_lambda_c_numeral.md`.

### 10 — R05, regenerated scaling campaigns (Class A, D2)

The submitted scripts derived seeds by integer offset, which the specifications require to be
replaced by a 128-bit digest. R05 keys the digest on the role and replicate index only — never
on `Gamma`, `beta`, `w` or the budget — repairing the entropy defect while preserving the
common-random-numbers design that makes a difference between two penalties an algorithmic
response rather than a difference of draw.

Both campaigns are therefore redrawn and every Monte-Carlo value moves. The movement is
mechanical: `lambda_star_Data`, a 95th percentile of 400 heavy-tailed CUSUM maxima, moves
`-7.9%` to `+19.4%` per cell, and `ADD_Data` moves `-12.2%` to `+14.4%` in lockstep, as
`ADD ~ lambda*/d + kappa` requires at fixed drift. The abrupt slope rises from 23.7 to 26.00
for that reason and no other; `R^2` is 0.9913, so the linearity it describes is unaffected.

Twenty-seven published quantities are classified in `docs/sections/R05.md`: seven D1 and
twenty D2. Every qualitative claim of the section holds — the delay is linear in the penalty,
Eq. (5) predicts the ramp delays with no fitted constant, the recalibration margin grows with
the penalty and with the horizon, and the Concept monitor is blind to the scale pathology.

### 11 — R05, the sign of the recalibration residual (Class A, D2)

`app:scaling` reports the `lambda_iid x Gamma` rule "holding to within 7-29% over a tenfold
range of `Gamma`, with the residual on the conservative side". In the regenerated 2e5 campaign
the margins are `+2.7%`, `-1.4%`, `+5.0%`, `+17.2%`, `+39.3%`. Four of the five keep the sign
the manuscript asserts; at `Gamma = 4` the residual is **`-1.4%`**, the opposite sign, which on
a strict reading of a one-sided statement is a D3.

It is recorded as D2, with the reasoning stated rather than buried: **this is an explicit boundary arbitration**. The estimator's own redraw
noise is an order of magnitude larger than the violation — the same quantity moved `-7.9%` to
`+19.4%` per cell under nothing but reseeding — so a residual of `-1.4%` is not distinguishable
from zero at `N = 400`, and the sign at `Gamma = 4` is undetermined rather than shown negative.
No parameter, tolerance, seed or bound was altered to reach this reading; the 400-seed design
is the manuscript's own. Resolving the sign needs a larger `N`, not a rewording, which is why
no camera-ready candidate is parked. See `docs/sections/R05.md`.

### 12 — R05, the sixth-moment attribution (Class A, —)

`app:scaling` attributes the degradation of the recalibration rule to "the loss of
`E[eps^6]`", placing the boundary at `Gamma ~ 7.1` with a moment margin `delta <= 0.8` at
`Gamma = 20`. **Both numerals are exact**: R05 recomputes them in closed form —
`E[eps^6] < infinity` iff `E[(alpha z^2 + beta)^3] < 1` — obtaining 7.0793 and 0.7931, with no
Monte Carlo involved.

The **attribution** is a different matter. Every R05 campaign runs `t_7`; there is no `nu`
sweep, so no output of this experiment separates "the rule degrades because a moment is lost"
from "the rule degrades with `Gamma` and with the horizon, and a moment boundary happens to lie
in the same range". The two budgets also place the measured transition differently, while the
analytic boundary does not move. This repository reports the association and asserts no
mechanism; establishing one needs an arm varying `nu` at fixed `Gamma`.

Separately, the parenthetical describing `E[eps^6]` as "the second moment of the monitored
statistic `eps^2`" is wrong independently of any measurement: `E[eps^6]` is the third moment of
`eps^2`, and the second is `E[eps^4]`, whose boundary the same closed form puts at
`Gamma = 41.6`. No numerical finding is affected. As this constrains an interpretation without
altering a value, the severity is null. A camera-ready candidate is parked in `docs/camera_ready_candidates/v87_sixth_moment_gloss.md`.

### 13 — R04, the transposed `Gamma` generator defect (Class A, D3)

In the submitted campaign, the `Gamma` grid never actually varied. `Priorite_15_isofpr_dichotomy.py` called `solve_beta_for_gamma(gamma, alpha)` against a definition of `(alpha, target_gamma)`, triggering an early return of `beta = 0` at every grid point. The four labels `{1, 11.58, 50, 200}` all silently ran the identical ARCH(1) process at `Gamma = 1.1053`.
Four qualitative claims of the manuscript (Recalib delay ratio, the efficiency crossing `nu*`, the oracle crossing, and the flat family control) are falsified when the grid genuinely spans. The discrepancy originates entirely from this defect. 

**Scope closure:** The project contains two homonymous functions with transposed argument orders. An exhaustive grep of all 23 call sites across the project confirms this collision is exclusively isolated to the R04 script. No other stream is affected.

### 14 — R04, the `nu*` efficiency crossing value (Class A, D3)

The manuscript states the efficiency ratio `ADD_Concept / ADD_Eco-L1` crosses unity at a measured `nu* ~ 4.9`, that an oracle arm crosses at `4.6`, and that the difference of `0.3` degrees of freedom is what a finite warm-up costs the parametric route. On a grid that genuinely spans `Gamma`, the crossing moves up. R04's grid `{3, 4, 4.5, 5, 7, 30}` could not say by how much: the crossing fell strictly inside `(7, 30)`, an interval with no measurement points in it.

R04b resolved it on twelve degrees of freedom, `{4, 4.5, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30}`, at the same `Gamma = 11.58`, `c = 0.5` and 2,000 streams, with continuity against R04 verified at the five common points.

- **`nu*(Eco-L1)` is enclosed by `[7, 9]`** — the last `nu` whose 95% ratio interval lies entirely below unity and the first whose interval lies entirely above it — and estimated at `8.10`, interval `[7.78, 8.37]`. The published `4.9` is far outside. **D3 stands**, now with a location.
- **`nu*(Oracle)` is enclosed by `[4, 5]`**, estimated at `4.47`, interval `[4.31, 4.57]`. The published `4.6` lies inside the bracket, and the arm sits on the analytic `4.7` (`4.678793`). **This claim is not falsified.**
- **The estimation cost is `3.62`, interval `[3.31, 3.92]`**, or `3.22 [2.52, 3.82]` by a route assuming no functional form, against the published `0.3`. Every interval excludes it. **D3.**

The bracket, not the point estimate, is the formulation to use in any revision: near the crossing one standard error spans 0.46 units of `nu`, so no point value is meaningful without its interval.

**The figure `8.52` that an earlier revision of `AUDIT_R04.md` obtained must not be quoted.** It was a two-point interpolation across the empty `(7, 30)` interval on a curve that is not linear in `nu`. The same rule on the refined grid gives `7.75`.

Full account, including the two controls that were re-specified before the result was read: `docs/sections/R04b.md` and `AUDIT_R04b.md`.

### 15 — R05, `regime` column contradiction (Class A, —)

The submitted script `Priorite_18b` wrote a `regime` column based on the recalibration rule's predicted crossover `w_star`, but the manuscript's appendix reported exponents fitted on `w_delta`, the crossover at the threshold the detector *actually* ran with. The CSV contradicted the paper it supported. R05 now emits both crossovers explicitly. No numerical claim of the manuscript is altered.

### 16 — R04b, the variance of a level read at a calibrated threshold (methodological, no manuscript claim affected)

Recorded here because it applies to every experiment of this repository that calibrates a threshold on one sample and measures at it on another, not because any published value moves.

A threshold selected on a finite calibration sample carries that sample's error into whatever is later read at it. The held-out false-alarm count of such a threshold therefore has the binomial variance **twice over**: once from the held-out draw, once from the calibration draw that placed the threshold. R04b verifies the factor distribution-free — calibrate on the empirical 95th percentile of 2,000 draws, read on 2,000 fresh ones, 20,000 replicates — and measures `1.4133` against the `sqrt(2) = 1.4142` a doubled variance predicts.

Two consequences were found by controls firing, and both were corrected in the specification of the control rather than in any draw:

1. A control that tests each arm's held-out level against *exactly* the nominal level omits half the variance of its own statistic and rejects by construction as the sample grows. R04b replaces it with a conditional two-sample test per arm, which removes the unknown true level from the analysis, plus a pooled control that carries the factor 2 in its interval and the bisection tolerance in its band. The two halves see different failures: the conditional test is blind to a bias common to every arm, which is why the pooled one is retained.
2. A bootstrap that resamples only the measurement sample holds the threshold fixed and understates the standard error of anything read at it — by a factor of 2.1 to 2.6 for the delay ratios of R04b. An understated error narrows every interval and can also make a correct model fail its own goodness-of-fit test, which is what happened before the correction.

**Recommended for `PROMPT_REPO_COMMON_PREAMBLE.md`, not applied**, since editing the shared preamble is outside the remit of one experiment: *the out-of-sample level of a threshold calibrated on a finite sample has twice the binomial variance, and any interval on that level must carry the factor, including after aggregation; more generally, any interval on a quantity read at a calibrated threshold must price the calibration error, and a bootstrap that resamples only the measurement sample does not.*

Whether any interval published by R04 or by another stream is affected is a question for an audit of those streams. It is posed here and not settled: R04's calibration control is in-sample by construction, which is a different situation, but the interaction has not been analysed.

### 17 — R06, the fourth-moment boundary and the pairing of Figure 6 (Class A and C, D1)

R06 is a port: its two tables are **byte-identical to the submitted campaign**, digests included, and every published quantity of Figure 6 is reproduced at D0. Three things nevertheless differ from what the manuscript shows or says.

**The fourth-moment boundary is computed rather than held as a literal (Class A, D1).** The submitted script carried the kurtosis of the standardized innovation as a default argument, `kurtosis=5.0`, with a comment naming `nu = 7`. The value is right — `3(nu-2)/(nu-4) = 5` — but a literal cannot follow `nu`. Computed from `(alpha, nu)`, the boundary is `beta = 0.9071`, `Gamma = 41.5843`. v87 prints `41.6`, so the value moves below the manuscript's printing precision and nothing published changes.

**The submitted figure conflates that boundary with the grid point beside it (Class C).** `Fig11_Whitening_Boundary.png` places an axis tick at the analytic boundary and plots the `Gamma = 41` measurement on top of it, so a reader takes a measurement to have been made *at* `41.6`. It was not: the grid contains `41`, which brackets the boundary from below by `0.58`, and nothing was run at the boundary. `fig06_validity_map.png` puts the grid on the ticks and the boundary on its own labelled rule. The claim is unaffected and supported — the binary stream is white at `41`, below the boundary, and at `60, 90, 120, 160, 200`, all above it.

**The caption's "100 independent streams per configuration" is true within a configuration and misleading across them (Class A, no published value affected).** The generator draws its innovations before the variance recursion, so `sign(eps_t) = sign(z_t)` and the submitted campaign, which keys streams on the seed alone, carries the same 100 label streams to all 13 `Gamma`. The error streams are not shared — the classifier reads amplitudes — so the readings are correlated rather than identical: measured design effect **3.21**, effective sample size **405** of 1,300. This is a legitimate paired design that sharpens comparisons across `Gamma`; what it requires is declaration and the variance treatment it imposes, and **an undeclared paired design is a defect of analysis rather than of experiment**. R06 declares it, gates the pooled level on a seed-cluster bootstrap rather than on an interval that assumes independence, and measures the same design effect a second way with a counterfactual arm keyed per (`Gamma`, stream): **1.01** against **3.21**. The conclusion of the panel survives either treatment.

A camera-ready revision should say "100 paired streams per configuration", or cite the effective sample size, or both. Full account: `docs/sections/R06.md` and `AUDIT_R06.md`.

### 18 — R04b, oracle ratio offset (Class A, D3)

The manuscript claims the oracle arm crosses unity at 4.6 "on the analytic prediction". R04b demonstrates the oracle ratio exceeds its analytic prediction at all twelve grid points by a mean of ~5% (sign test p ~ 5e-4). The curve does not track the prediction; it lies systematically above it, and the crossing near 4.6 is the result of compensation between this offset and the curve's slope. The point `nu = 20` exceeding `pi/2` is the largest realization of this systematic offset, not an isolated anomaly. The crossing value is reproduced, but the characterization of its mechanism is falsified. Full account: `docs/sections/R04b.md`.

### `R11-onset-convention` — R11, the four delays of Figure 15B are not mutually comparable (Class A, no published value affected)

The submitted campaign gave the CUSUM one onset convention and the other four detectors another.
`worker_exp_b_h1` builds the CUSUM's stream as `eps[2000:] + Delta` with the statistic at zero
(`Priorite_12_multi_detector.py:308-310`), while PHT, ADWIN, DDM and EDDM receive the whole stream
with `onset=2000` (l.318-321). `strict_pht` tests `if m - M > threshold and t >= onset`, so a
crossing during warm-up is not returned **and does not reset the statistic**, and the warm-up loop of
`run_river_detector` calls `update()` without ever reading `drift_detected`.

R11 runs three labelled arms. `reset` and `warmstart` put every detector on one convention;
`as_submitted` reproduces the per-detector mixture and is the only arm on which the caption's four
numerals reproduce.

| detector | `reset` | `warmstart` | `as_submitted` | v87  |
| -------- | ------- | ----------- | -------------- | ---- |
| CUSUM    | 28.4078 | 25.4347     | **28.4078**    | 28.3 |
| PHT      | —       | 27.0517     | **27.0517**    | 27.1 |
| ADWIN    | 2023.75 | 61.2123     | **61.2123**    | 61   |
| DDM      | 1873.61 | 249.6010    | **249.6010**   | 250  |

Placing the CUSUM and the PHT on one convention **reverses their published order**: the CUSUM falls
to 25.4347 while the PHT stays at 27.0517, a paired seed-clustered difference of `+1.6170 ± 0.0318`,
**50.9 standard errors**. This falsifies nothing v87 states — the caption asserts flat delays, and
the delays are flat; neither the caption nor the body asserts an ordering in words — so the severity
is null. What it establishes is that a reader comparing the four numerals compares across two
conventions, and the caption does not say so.

The pre-onset leak is counted per detector over 100,000 streams: EDDM 91,560, DDM 9,780, CUSUM 3,180,
PHT 2,400, ADWIN 40. It is logged even at zero and is deliberately not a gate.

Full account: `docs/sections/R11.md` and `AUDIT_R11.md`. Candidate:
`docs/camera_ready_candidates/R11_v87_detector_comparability.md`.

### `R11-cusum-add`, `R11-pht-slope`, `R11-pht-syncope` — R11, three moved numerals (Class A, D2)

All three follow from the 128-bit re-keying and are classified at v87's printing precision, each on
the arm that produced it.

- **`Concept` CUSUM delay**, `reset` arm: `28.3` → **`28.4078`**. The three other caption delays move
  below the printed precision and are D1: PHT `27.0517`, ADWIN `61.2123`, DDM `249.6010`.
- **PHT log-log slope**, `as_submitted`: `1.09` → **`1.0977 ± 0.0094`**, fitted on the **12 of 20**
  grid points where `DetRate ≥ 0.5`. Those delays are conditional on detection and biased downward by
  selection on survival; the CUSUM and ADWIN are censored nowhere. The manuscript states neither the
  domain nor the conditioning.
- **The stochastic syncope**: "beyond `Γ ≈ 75`" → the first grid point below 50% detection is
  **`Γ = 91.11`**. The collapse itself reproduces; the numeral moves. Both values are upper bounds on
  a crossing the grid does not resolve, since detection declines across several points.

### `R11-pht-gamma-rule` — R11, the `λ × Γ` rule holds no level for the PHT (Class A, D2)

v87 L171 says the PHT "needs the same `λ × Γ` inflation" as the CUSUM, whose cure is described as one
that "holds the nominal level", and the Figure 15 caption calls it the "same `λ × Γ` cure". Measured
over the 20-point grid at 5,000 streams per point, with the `sqrt(2)` inflation that a calibrated
threshold requires, the rate falls monotonically from **14.46%** `[13.14%, 15.89%]` at the attainable
floor to **1.62%** `[1.19%, 2.19%]` at `Γ = 200` (value cited here; the macro
`\RElevenPhtGammaRuleHigh` reports the mean over `Γ > 20` at 2.10%). The extreme intervals do not
overlap, so the drift is not sampling noise; there is no plateau at 5% anywhere.

**The cure works and only the word "same" fails.** False alarms are contained throughout — the raw
threshold runs above 80% on the same rows. This repository recorded the identical situation once
before: entry 7 found the StrictCUSUM's i.i.d. level to be 2.0% rather than the 5% ascribed to it and
classified it D2, on the grounds that a conservative threshold is a legitimate design choice and what
is inexact is calling it calibrated. The same reading and the same severity apply here. No figure,
table or theorem depends on the descriptor. Candidate:
`docs/camera_ready_candidates/R11_v87_pht_gamma_rule.md`.

### `R11-figure11-caption` — R11, the Figure 11 caption states one panel's parameters for both (Class A, D2)

The caption reads "abrupt drift `c=2`, `1,000` streams per point" for a figure whose panel A is
produced by `run_experiment_d(n_seeds=1000)` at `Delta = 2.0 σ` and whose panel B is produced by
`run_experiment_b(n_seeds=5000)` at `c = 1.5` (`Priorite_12_multi_detector.py:337, 592, 609, 613`).
v87 corroborates the correction twice in its own text: L296 and the Figure 15 caption both say
`c = 1.5` for the same `Concept` campaign. The claim the caption supports — "flat delays for all
detectors" — is a statement about panel B and is unaffected. Candidate:
`docs/camera_ready_candidates/R11_v87_figure11_caption.md`.

### `R11-gamma-grid-floor` — R11, the lower endpoint of the published `Γ` range is not attainable (Class A, no published value affected)

v87 L296 states the detectors hold a bounded FPR "across `Γ ∈ [1, 200]`". At `alpha = 0.08` the
penalty is minimised at `beta = 0`, where the closed form gives

    Gamma_floor(alpha) = 1 + 2*alpha/(1 - alpha) = 1.1739130435,

so no `beta ∈ [0, 1)` reaches `Γ = 1`. The submitted target grid
`concat(linspace(1, 50, 10), linspace(60, 200, 10))` therefore has an unattainable first point: the
bisection collapses to `beta = 0` and the process runs at the floor. The grid spans `1.1739` to
`200`, a ratio of **170.37**, which is what v87's own "`×170` range" describes — so the range
descriptor is right and the interval endpoint is not.

**This is the same finding entry 7 records for R03**, where the lowest grid point sat at
`Γ = 1.174` with `alpha = 0.08` and `beta = 0` and was an ARCH(1) stream rather than an i.i.d. one.
R11's macros carrying the sensitivity restriction are therefore named `…ExLowGamma` and not
`…ExIid`: excluding the point removes an ARCH(1) process at the attainable floor, not an i.i.d. one.

The control that found it was not adjusted. C2 carries two assertions decided by a closed form before
any solving — the realised penalty within `1e-6` of an attainable target, and `beta == 0.0` exactly
for an unattainable one — and `Gamma_target`, `Gamma_realised` and `attainable` are three distinct
persisted columns.

Separately: the R11 prompt lists the grid as the literals `1.17, 6.44, 11.89, …`. Those are the
submitted campaign's **realised** penalties rounded to two decimals, not its targets, and the script
verifies at run time that rounding each realised penalty reproduces the printed literal at all twenty
points. Solving for the targets instead of the literals moves `beta` at sixteen of the twenty points,
by at most `2.89e-5`.

### `R11-regenerated` — R11, the regenerated campaign (Class A, D2, pre-classified)

Prompt §2.1 requires migrating off `np.random.RandomState` keyed on the process parameter to a
128-bit `SeedSequence` keyed on role and index alone, which is the strategy R05 established. Every
Monte-Carlo value moves; this is acknowledged in advance and needs no per-value justification.

What it buys is a common-random-numbers design in which a difference between two `Γ` is an
algorithmic response rather than a difference of draw. What it costs is priced rather than ignored:
the seed-cluster bootstrap standard errors on the `Concept` slopes exceed their analytic OLS
counterparts by factors of **1.5 to 5.0**, and that ratio is the design effect. One consequence is
structural and is declared rather than corrected — under a key that carries no `gamma`, the `H0`
`Concept` arm is **bit-identical at all twenty penalties**, because `simulate_garch11` draws its
innovations before the variance recursion and `sign(eps_t) = sign(z_t)` exactly. That arm is kept as
an identity witness with a design effect of 20 by construction, it supports no claim, and every
published `H0` `Concept` rate is taken from a second arm whose key breaks the pairing.

Twelve published quantities are classified in `docs/sections/R11.md`: one D0, four D1, and the rest
D2. **No D3.** Every qualitative claim of `sec:universality` is reproduced.

### `R18-ljungbox-power` — R18, the Ljung–Box non-rejections are stated without their power (Class A, no published value affected)

Four sites of v87 carry the whitening property on an accumulation of Ljung–Box **non-rejections**:

| site                           | wording                                                                                        | design                          |
| ------------------------------ | ---------------------------------------------------------------------------------------------- | ------------------------------- |
| §4.4 L278 (`sec:validity_map`) | "the binary errors hold the nominal level in every regime (3.3–5.0%; 4.4% pooled)"             | 360 streams, `n = 8000`, lag 20 |
| §4.4 L290                      | "the binary error stream **stays strictly white** up to `Gamma = 200`"                         | Fig. 11A, 100 streams/config    |
| Fig. 6 caption L286            | "show **no detectable** autocorrelation in any GARCH regime"                                   | same 360 streams                |
| §4.8 L318 (`sec:real_world`)   | "a lag-20 Ljung–Box test finds no serial correlation on any asset …, **licensing** the filter" | 4 ETFs, 4 single tests          |

A non-rejection bounds nothing unless the instrument can reject, and an exhaustive grep of v87 for
`power`, `Type II`, `sensitivit*`, `false negative` and `fail to reject` returns no power analysis.
The gap was flagged independently by `AUDIT_R06.md` §8 item 3 and by `WRAPUP_Stream_B1.md` §6 item 3;
the second was written before submission and was not carried into v87.

**No published value changes and no D0–D3 severity applies**: R18 regenerates nothing. What is
registered is the other kind of divergence this file exists for — a claim whose evidential weight the
repository can bound while the manuscript states it unqualified. `R11-onset-convention` is the same
shape and carries the same null severity.

The bound, at the nominal 5% level and lag 20:

| `n`       | `rho_80`, the lag-1 autocorrelation the test detects with probability 0.8 |
| --------- | ------------------------------------------------------------------------- |
| `2,000`   | **0.1023** measured, `0.1018` analytic, 95% `[0.0992, 0.1050]`            |
| `8,000`   | **0.0506** measured, `0.0511` analytic, 95% `[0.0494, 0.0518]`            |
| `32,000`  | **0.0265** measured, `0.0256` analytic                                    |
| `128,000` | **0.0127** measured, `0.0128` analytic                                    |

`n = 8000` is the configuration behind L278 and the Figure 6 caption. L290's Figure 11A campaign runs
at the same horizon. L318's four ETF tests run on pre-2020 daily warm-up windows, bracketed by the two
shortest horizons above, so `rho_80` there lies between `0.051` and `0.102` — and each asset is read
once, not over 1,000 streams.

**What the non-rejections do and do not exclude.** Applied to the streams themselves — 13,000
HoeffdingTree error streams on R06's `Gamma` grid and 20,000 raw sign streams on R11's — the largest
pooled lag-1 autocorrelation measured anywhere is `0.000818`, which is `1.6%` of `rho_80`. At that
amplitude the instrument's power is **`0.050`, its own level**. The published non-rejections therefore
exclude a lag-1 autocorrelation above `0.051` at `n = 8000`, under a geometric-decay alternative, and
exclude nothing below it: the same non-rejection is returned whether the true autocorrelation is
`0.0008` or `0.04`.

This neither supports nor contradicts Proposition `prop:whitening`. It removes one reading — that the
non-rejections bound the autocorrelation by something smaller than `rho_80` — and it leaves the
proposition exactly where its own proof puts it.

Full account: `docs/sections/R18.md` and `AUDIT_R18.md`. Candidate:
`docs/camera_ready_candidates/R18_v87_whitening_evidence_strength.md`.

### `R16-dating-misdescription` — R16, the census is not the output of the dating L329 names (Class A, D3)

v87 L329 opens the census paragraph with "A retrospective multi-scale **Pagan--Sossounov**
bull/bear dating~\cite{pagan_sossounov_2003} **of the four streams** (2000--2025; $66$ phases
**after duration censoring**, the COVID-19 crash---too brief for the filter---dated at the *raw
scale*)". Measured on the same four derived FirstRate series, with the dating parameters the
delivered script fixes:

| dating run on the four streams                                 | phases | out of budget at `gamma = 20` | artefact                          |
| -------------------------------------------------------------- | ------ | ----------------------------- | --------------------------------- |
| Pagan--Sossounov on all four, no substitution                  | **48** | 38 (79.2%)                    | `R16_regime_census_strict_ps.csv` |
| Pagan--Sossounov on PFF, VNQ, BWX; Lunde--Timmermann on SPY    | **66** | **53 (80.3%)**                | `R16_regime_census.csv`           |
| Lunde--Timmermann wherever `check_sanity` fails, i.e. all four | 102    | 75 (73.5%)                    | `R16_regime_census_symmetric.csv` |

**The 66 are not reachable by the algorithm the sentence names.** `Priorite_16_regime_census.py`
evaluates `check_sanity` on SPY's Pagan--Sossounov MACRO dating (l.233), it fails, and the MACRO
turning points of that one stream are replaced by `lunde_timmermann(0.15, 0.15)` (l.237). SPY
contributes 30 of the 66 phases. Lunde--Timmermann applies **no duration censoring**: its
shortest SPY phase is 6 trading days, against 49 under strict Pagan--Sossounov on the same
stream. Both load-bearing clauses of the sentence — "of the four streams" and "after duration
censoring" — are therefore inexact.

**The values are not falsified.** `53`/`66` at the permissive budget, `52` on the sign arm, `64`
at one false alarm per year, `504\ln 20 = 1{,}510`, `504\ln 252 = 2{,}790`, the SPY 2011--2018
phase (`0.541 \to 0.554` over `1{,}753` days) and every numeral of L331 reproduce exactly, and
the regenerated census is **bit-identical** to the submitted `protocol_10b_regime_census_refined.csv`
on all 19 shared columns and all 66 rows. What is contradicted is the account of how the 66 were
obtained, which is why the severity falls on the method description and not on any number.

**The substitution is not silent in the delivered code.** Line 3 of the vendored
`data/reference/R16/Priorite_16_regime_census.log` reads `WARNING | [SPY] Sanity check P-S
failed. Fallback to Lunde-Timmermann for MACRO.` What preamble §S4.3 requires of a fallback that
is kept rather than removed is more than a warning — an explicit argument and a stamp in the
output filename — and that is what R16's three arms restructure. `sanity_ok` is moreover
initialised to `True` and reassigned only inside the `if ticker == 'SPY'` branch, so PFF, VNQ and
BWX are never tested by it; this repository evaluates the check on all four on every run, and
**all four fail it**.

**On §S3's halt obligation.** A D3 requires stopping, not reconciling. Here the halt lands on the
*manuscript*, which is frozen and cannot be edited, so the obligation is discharged by this
entry, by the camera-ready candidate, and by the persisted 48-phase counterfactual that makes the
claim checkable by a third party. No parameter, tolerance, seed or bound was moved to reconcile
anything, and the pipeline runs to completion because the regenerated *values* are not in
contradiction.

**No cause and no intent is attributed.** Preamble §S4.5 forbids it, and the evidence is equally
consistent with a description written from the design as intended rather than as executed.

Full account: `docs/sections/R16.md` and `AUDIT_R16.md`. Candidate:
`docs/camera_ready_candidates/R16_v87_dating_algorithm.md`.

### `R16-covid-phase-conditional` — R16, the COVID phase reproduces and is conditional on the substitution (Class A, no severity)

v87 L331's four numerals for the COVID crash reproduce **exactly**: `\Delta q = -0.2803`
(printed `\approx -0.28`), annualized Sharpe `-5.9904` (printed `\approx -6.0`), `23` trading
days, `\mathrm{kl} = 0.162042` nats/day (printed `0.162`), floors `34.12` at `\gamma = 252`
(printed `\approx 34`) and `18.49` at `\gamma = 20` (printed `18.5`), the latter being `80.4\%`
of the phase — v87's "four fifths". **Nothing in L331 is falsified.**

The phase nevertheless exists only under the SPY substitution: strict Pagan--Sossounov censors
the 23-day crash at its `min_phase = 84` rule, and the sentence and its four numerals disappear
with it. That is **the same measured fact** as `R16-dating-misdescription`, and one measured
fact produces one register entry: entering it twice at D3 would double the manuscript's apparent
exposure on a single finding, which is the over-declaration this campaign corrected on R11's
deviation table. This row therefore cross-references the D3 and registers no second severity.

**L329 already flags the exception.** The dating clause ends "the COVID-19 crash---too brief for
the filter---dated at the *raw scale*". The raw scale **is** the uncensored Lunde--Timmermann
dating, so the manuscript names the exception without naming the algorithm. Whether that
phrasing was meant to carry the substitution is not established by any measurement, and §S4.5
forbids deciding it. The D3 at `R16-dating-misdescription` stands unchanged and is unaffected by
this clause: "a Pagan--Sossounov dating of the four streams" still does not describe a
Lunde--Timmermann dating of one of them.

### `R16-floor-frac-envelope` — R16, the floor-fraction envelope of L329 (Class A, D2)

v87 L329 states that the phases the ceiling does not exclude are dominated on duration alone,
"and even there the floor consumes $55$--$92\%$ of the phase". Measured over the 13 phases
detectable at `\gamma = 20` on the unconditional arm: **`[50.1\%, 92.1\%]`**. The upper end
reproduces at the printed precision; the lower end does not. Two phases lie below 55%:

| phase                       | `T_days` | floor / duration |
| --------------------------- | -------- | ---------------- |
| PFF 2009-03-06 → 2011-05-19 | 556      | **50.11%**       |
| BWX 2021-01-05 → 2022-10-20 | 452      | **50.47%**       |
| SPY 2011-10-03 → 2018-09-20 | 1753     | 54.79%           |

**The cause is not identified.** SPY 2011--2018 is at `54.79\%`, which rounds to 55, and it is
the phase L329 names two clauses earlier — which *suggests* the published lower bound was read
off that single phase rather than off the minimum of the set. No measurement here establishes
it, so preamble §S4.5 applies and the association is recorded without a mechanism. Four
definitional variants were enumerated and logged by `exp_R16_regime_census_b.py`, and **none
yields 55--92**: bull phases only `[50.1\%, 92.1\%]`, `T_days >= 250` `[50.1\%, 92.1\%]`, both
together `[50.1\%, 92.1\%]`, the sign arm at `\gamma = 20` `[41.0\%, 97.5\%]`, and the
superseded `protocol_10a` census `[45.7\%, 95.9\%]`.

The qualitative claim the sentence supports — that the floor consumes most of even the phases it
does not exclude — holds at the corrected envelope, which is why the severity is D2 and not D3.

### `R16-boundary-sensitivity` — R16, the convention is declared and its effect is never reported (Class A, no severity)

v87 L392 declares the post-onset cut, states its mechanism correctly, and cites the right
example (`-18.6\%` on PFF, 2020-03-18, which this repository reproduces as
`-0.18583434620279932`). It never reports how much the convention moves the headline.

Three of the 66 phases change detectability with the convention, and **all three change in the
same direction** — they gain detectability under the post-onset cut:

| ticker | phase                   | Sharpe, inclusive → post-onset | floor, inclusive → post-onset |
| ------ | ----------------------- | ------------------------------ | ----------------------------- |
| PFF    | 2011-08-08 → 2013-05-08 | `1.0254 → 1.9800`              | `1435.8 → 385.1`              |
| PFF    | 2020-03-18 → 2021-12-31 | `0.9132 → 1.9046`              | `1810.7 → 416.2`              |
| BWX    | 2020-03-18 → 2021-01-05 | `1.8179 → 3.1323`              | `456.9 → 153.9`               |

The published count is therefore the **conservative end** of the interval `[53, 56]` =
`[80.3\%, 84.8\%]` that the two conventions bracket, and the sensitivity can only strengthen the
claim. Two of the three flips are the 2020-03-18 turning point L392 already cites.

**The direction runs against the manuscript's own headline, and the manuscript has the mechanism
right.** The double-counted trough return is a large negative outlier that depresses the mean
and inflates the variance of the phase that follows, biasing its floor upward — so the defect
*inflated* the published fraction (84.8%) and the correction *lowered* it (80.3%). Candidate:
`docs/camera_ready_candidates/R16_v87_boundary_sensitivity.md`.

### `R16-sign-arm-disagreement` — R16, "moves that count by one phase" is true of the count and false of the set (Class A, no severity)

v87 L329: "Pricing the binarization exactly through `kl(q_phase || q_ref)` moves that count by
one phase ($52$ of $66$)". The step of one holds — 14 phases detectable on the sign arm against
13 on the unconditional arm at `\gamma = 20`. **The two arms nevertheless disagree on 19 of the
66 phases**: 10 are detectable on the sign arm only and 9 on the unconditional arm only. The
step is a net, and there is no single flipping phase to name.

The two sets separate cleanly by phase type and by duration, which is a measured description and
not a mechanism: **all 10** sign-only phases are bear phases, of median duration 170 trading days
(SPY's 23-day COVID crash at `kl = 0.162`, its 40-day 2022 decline, VNQ's 2013 taper decline),
while **8 of the 9** unc-only phases are bull phases, of median duration 450 days (SPY 2003--2007
and 2011--2018 at `kl \approx 0.0003`, where the Bernoulli floor runs to nine thousand days
against an unconditional floor near nine hundred). All 19 are persisted in the
`arm_disagreement` column of `results/R16_regime_census/data/R16_sign_floor.csv`. No published
value moves; what is registered is that the sentence describes the count and not the set.

### `R16-substitution-scope` — R16, the published fraction is conditional on the substitution reaching one ticker of four (Class A, no severity)

The delivered script guards its dating substitution with `if ticker == 'SPY'`, and
`check_sanity` fails on all four tickers. Applying the same rule consistently — Lunde--Timmermann
wherever the check fails — gives **102** phases and **75** out of budget, i.e. **73.5%** against
the published 80.3%. That is 6.8 points: four times the displacement strict Pagan--Sossounov
produces (79.2%) and more than twice the boundary-convention envelope (80.3--84.8%).

The arm ships as `results/R16_regime_census/data/R16_regime_census_symmetric.csv` and is priced
by three macros. It is registered rather than left in the artefacts because an evaluator who
reads `if ticker == 'SPY'` will ask exactly this question, and finding the answer computed but
unremarked is worse than finding it stated.

**Direction, and the scrutiny it earns.** This arm moves the headline *against* the manuscript's
thesis, so preamble §S3's asymmetry rule assigns it the lighter examination, not the heavier. It
is also not a correction: Lunde--Timmermann at `\lambda = 0.15` on all four streams produces
102 phases of which seven are 2-to-6-day episodes of the 2008 crisis with a degenerate up-day
rate (`q_phase` exactly 0 or 1, clipped to `[10^{-6}, 1-10^{-6}]` before the divergence), which
is a different census rather than a better one. What it establishes is the conditionality, and
that is all it is recorded as establishing.

Full account: `docs/sections/R16.md` and `AUDIT_R16.md`.
