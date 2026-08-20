# AUDIT — R12: Volatility misspecification and moment singularity

R12 reproduces v87 Figures 12 and 13 (L349, L353) under the repository 128-bit seeding policy. Experiment A: 15 leverage points `γ_lev ∈ {0.00, 0.02, ..., 0.28}`, 10 000 streams each, `n = 7 000`, pseudo-Gaussian innovations (`ν = 100`). Baseline uses symmetric filter `α_sym = α + γ_lev/2`; Concept monitors sign stream at fixed threshold. Experiment B: 16 degrees of freedom `ν ∈ {10, ..., 4.01}`, 1 000 streams each, `n = 10 000`, drift `c = 1.0 σ`.

**Result: Both paragraphs reproduce qualitatively. No D3.** Ten of twenty printed numerals shift at v87 precision under mandated re-keying (**D2**, `R12-campaign-redraw`); six are D1, four are structural D0. The halt candidate — L353's `2 400`–`3 000` bracket — stays within `[2350, 3050)` at 95 % level, D2 only at lower end.

**Certification partition.** `R12_leverage_fpr.csv` and `R12_singularity_add.csv` carry all manuscript values. `R12_concept_crn_witness.csv` and `R12_diagnostics.csv` certify no published value and exist solely for control auditing (C4, C5, C8, C9, C10).

---

## What must not be inferred

- The Concept arm's published flatness is **not** measured on the naive CRN arm. Under role-and-index-only keys, Experiment A's sign stream is bit-identical across all fifteen `γ_lev` because `simulate_gjr_garch` draws innovations before variance recursion, making `sign(ε_t) = sign(z_t)` exactly. Published Concept values come from a second arm whose key carries the grid index (§4.1).

- Printed ranges (`7.6`–`8.4 %`, `4.6`–`5.4 %`, `34`–`38`, `2 400`–`3 000`) are **not** tested as bounds. Each is a grid extremum with no stable sampling distribution. They ship with descriptive seed-bootstrap envelopes that gate nothing. The invariance gate is C9's slope, which has a proper null.

- The Data arm's Ljung–Box KS rejection (`24.19 %`) is **not** a calibration failure. It matches v87's printed claim, so uniformity rejects precisely because the manuscript is correct. It is a positive control on power; Concept arm calibration is the actual question.

- R12 does **not** measure the task boundary. Control C3 **reads** the orphan witness beside R07's certified `φ = 0.15` cell and leaves the gap unexplained. R12's negative witnesses are the cells it runs: `γ_lev = 0` and `ν = 10`.

- The collapse is **not** a clamp artefact. Control C10: 0 clamped steps of 52 993 800.

- `α_sym` is **not** established as the QMLE population limit (§5).

---

## Controls

| control | statement | margin | trigger probability under H₀ |
| --- | --- | --- | --- |
| **C1** | `det_rate_concept` is computed `len(d_concept) / n_seeds` (script AST l.381), not a literal | structural | **0**; failure = D3 |
| **C1** corroboration | `det_rate_concept = 1.0000` at all 16 `ν` because `n_detected_concept == n_seeds`; `ADD_Concept` spans `33.638`–`37.900` | real 1 000/1 000 | — |
| **C2** | censoring logged **before** frame read; `ADD_Data`/`SEM_Data` only where `det_rate_data ≥ 0.5`; `ADD_Data_Raw` and `SEM_Data_Raw` on every cell | 9 cells gain SE | **0** — deterministic |
| **C3** | task boundary as read: R07 `φ = 0.15` NAIVE `0.9979` `[0.99679, 0.99863]`, ORACLE `0.0492` `[0.04513, 0.05361]`, `N = 10 000`; orphan `1.000` `[0.99617, 1.0]` / `0.045` `[0.03380, 0.05968]`, `N = 1 000` | gap stated, unexplained | deterministic; no macro |
| **C3** | orphan intervals reproduced bit-identically from counts `1000/1000` and `45/1000` at `z = Φ⁻¹(0.975) = 1.959963984540054`; at `z = 1.96` miss by `1.4×10⁻⁷` and `1.8×10⁻⁷` | 17 digits | **0** — deterministic |
| **C4** | 6/6 uncensored adjacent pairs decrease, `+0.044` to `+0.062`, paired SE `0.0085`–`0.0104`, `z` `+4.23` to `+6.39` | domain pre-declared | qualitative D3 criterion |
| **C4** | one censored inversion: `ν 4.2 → 4.1` at `−0.0060`, SE `0.0081`, `z = −0.74`, 95 % `[−0.0219, +0.0099]` — characterised, never corrected | covers zero | reported |
| **C5** | Ljung–Box calibration: Concept `D = 0.1701`, `p = 0.7172`; Data `D = 0.9369`, `p = 1.99×10⁻¹⁸`; family `D = 0.4533`, `p = 3.77×10⁻⁶` | `1 − 0.95³⁰ = 78.54 %` logged first | gates nothing |
| **C6** | source identity: 3 primitives byte-identical (1 160 chars); 6 routines by SHA-256; 29 statements verbatim | byte equality | **0** unless copy drifted |
| **C7** | two consecutive runs + one different `--n-jobs` run, byte-identical on all seven artefacts | exact | **0** — deterministic |
| **C8** | CRN identity: 50 seeds × 15 `γ_lev`, SHA-256 of `(ε[2000:7000] > 0)` identical per seed — 750 pairs, 50 distinct digests, `sys.exit(1)` otherwise | bit equality | **0** — structural |
| **C8** | design effect: `deff(fp_concept) = 15.0015` (CRN) vs `1.0004` (published); Data arm `9.1059` vs `0.9528` | signature of 15-point grid | measured, gates nothing |
| **C9** | invariance slope: OLS of Concept FPR on `γ_lev` slope **`−0.9286`** pp, analytic SE `0.8797`, bootstrap SE `0.8034` (2 000 replicates), 95 % `[−2.4500, +0.6577]`, `p = 0.2477` | gate `0.01`, not fired; `1.16 σ` from zero | exactly `0.01`, two-sided |
| **C9** | degenerate CRN arm: slope **`0.0`**, analytic SE `5.70×10⁻¹⁵` | exactly zero | — |
| **C10** | clamp binding: **0 clamped steps of 52 993 800** (6 200 streams, 200 per grid point, both experiments); max unclamped `σ²_t`: `4 889 × σ²_unc` (A), `262 ×` (B) vs `10 000 ×` ceiling | 2× headroom at worst | reported, gates nothing |
| **C10** | instrumented equivalence: copy returns bit-identical `ε` on all 6 200 streams, 0 disagreements | bit equality | **0** |
| **C11** | legacy-global inertness: each worker bit-identical under two different `np.random` / `random` states | exact | **0** — deterministic |

**Family-wise arithmetic.** Exactly one gate consumes entropy — C9 at `0.01` — so probability a gate fires on a compliant campaign is `0.0100`, below 5 % ceiling. C4 is qualitative; C1, C2, C3, C6, C7, C8, C10, C11 are deterministic. **No level chosen after seeing results.**

**Derivations (repository policy).** (1) Symmetric innovations: `E[1{ε<0}] = 1/2`, so GJR second-moment condition `α + γ_lev/2 + β < 1`; grid runs `0.85 → 0.99` (edge of stationary region). (2) `E[ε²·1{ε<0}] = E[ε²]/2`, so `E[h_t]` matches `E[σ²_t]` exactly; `ω = 0.04(1 − α_sym − β)` gives `σ²_unc = 0.04` everywhere — misspecification is in dynamics, not level. (3) `E[ε⁴] < ∞` iff `α²·3(ν−2)/(ν−4) + 2αβ + β² < 1`, giving `ν* = 4.0811` at `(0.05, 0.85)`. (4) `compute_gamma_exact(0.05, 0.85) = 2.2208`, so Data threshold `65 × 2.2208 = 144.35`; Concept threshold `10` (no multiplier). (5) `deff` assigned explicitly: within-cell streams independent (`deff = 1.0`); across grid CRN makes readings paired (C4, C8, C9 measure it).

---

## Decisions outside the plan

### 4.1 Two Concept arms
Plan anticipated this (finding F3, decision 4). Under `("R12", "expA", s)` the Experiment A sign stream is bit-identical at all fifteen `γ_lev`; C8 digests it on 50 seeds, exits `1` unless all fifteen agree. Consequence: `deff(fp_concept) = 15.0015` (CRN) vs `1.0004` (published arm keyed `("R12", "expA_concept_indep", γ_index, s)`). Key carries grid **index** (integer), never float value, so no platform formatting dependency.

Data arm is not degenerate on either key. The second pass provides a counterfactual: unpublished independent-key Data FPR `3.32 % → 20.95 %`, Ljung–Box `4.93 % → 24.30 %` vs published CRN-key `3.46 % → 20.48 %`, `5.41 % → 24.19 %`. Data response is not a pairing artefact. Both unpublished readings in `R12_diagnostics.csv` (`fpr_data_independent_key`, `lb_data_pct_independent_key`) are not macro-emitted.

### 4.2 C3 quantile correction
Plan stated orphan intervals as "Wilson at `z = 1.96`, `n = 1000` — recovered to all 17 digits". **Not recovered at `z = 1.96`**: misses lower bounds by `1.401×10⁻⁷` and `1.774×10⁻⁷`. At `z = Φ⁻¹(0.975) = 1.959963984540054` both reproduce bit-identically from counts. Substantive point unchanged: recovering interval construction recovers arithmetic and sample size, not DGP.

### 4.3 Figure comparison against code
Plan verification step 6 prescribed comparing against `Fig15_Robustness_Leverage.png` and `Fig16_Robustness_FatTails.png`. PNGs not transmitted; comparison made against witness plotting code (`Priorite_10` l.276–298, l.406–451): same curves, censoring, blind-zone span, singularity rule, axis limits, log scale. Cosmetic divergences in §8.

### 4.4 Parallel verification
Plan step 2 prescribed `--n-jobs 1`. Not run (≈48× serialisation). `--n-jobs 6` run instead: **substitution, not reduction**. Tests uneven partitioning and accumulation order effects. Passes.

### 4.5 Macros deliberately not emitted
`\RTwelveBoundaryNaiveRate` and `\RTwelveBoundaryMedianRate` would read from `expA_argarch_boundary.csv`. Dropped per plan decision 2: claim is v87 L302 (R07's mission), already delivered by R07. Six macros omitted from prompt list **are** emitted because v87 prints them: Concept Ljung–Box range (L349), Concept delay range and censored delay range (L353), "factor of six" (L349), C9 slope with interval. Twenty-one macros total.

### 4.6 No camera-ready candidate
Plan deliverable table lists none. §S8 third channel requires candidate attached to a true-but-incomplete manuscript sentence. Three potential findings held in §5–6 instead, unsettled. Scope decision.

### 4.7 C6: superseded routines pinned by digest
Plan requires witness source of two adapted workers quoted with SHA-256 (done). Initial implementation quoted four superseded routines; withdrawn because `run_experiment_B` l.463 carries a banned phrase, verbatim quotation imported it into run log (grep returned one match). Superseded routines now pinned by SHA-256 with replacements named in same line. Same bytes fixed, none reproduced, grep returns zero.

---

## Open questions

1. **"Population limit" at L349.** v87 calls `α_sym = α + γ_lev/2` the symmetric GARCH(1,1) "population limit". Design delivers **mean-matching**: under symmetric innovations, `E[h_t]` matches `E[σ²_t]` exactly. QMLE population limit is Gaussian pseudo-true parameter [Bollerslev & Wooldridge, 1992]. **Two need not coincide; no R12 measurement decides which `α_sym` is** — witness substitutes `α + γ_lev/2` in closed form. Requires QMLE arm, outside v87 scope.

2. **Moment boundary vs collapse distance.** `ν* = 4.0811`; only `ν = 4.05, 4.01` beyond fourth-moment boundary, but detection collapse begins near `ν = 5.5–6`. Reported as derived; **no mechanism attributed**. `R02c-mechanism-constraints` records identical shape on i.i.d. arm (infinite eighth moment up to `ν ≤ 8`, effect gone at `ν = 7`) under same ruling. R12 cross-references, invents nothing.

3. **Orphan boundary CSV.** Arithmetic fully recovered; DGP not recovered; no producing script. §6.

---

## Orphan CSVs

`expA_argarch_boundary.csv` and `expB_race_condition.csv` delivered with attachment. Grep of delivery for `argarch_boundary|race_condition` returns only the prompt. `Priorite_10` writes exactly two CSVs (l.274, l.404), neither is these. **Vendored verbatim** under `data/reference/R12/orphans/` with README; not rebuilt (reconstructing from outputs means inferring design from reproduced numbers).

- **`expA_argarch_boundary.csv`** — C3 reads it. Two Wilson intervals recovered exactly (§3, §4.2). Orphan: `1.000 / 0.045` on `N = 1 000`; R07 certified: `0.9979 / 0.0492` on `N = 10 000` at `φ = 0.15`. **Gap stated, unexplained**: design unknown (stream length, innovation law, AR coefficient, estimator, lag count); §S4.5 forbids mechanism attribution. No macro, no entry.

- **`expB_race_condition.csv`** — **produced and not cited**. 1 000 rows; `delay_frozen` populated all (min `35`, max `356`, mean `76.149`, no `-1`); `delay_arf` empty on 999/1 000, single populated row `seed = 492` at `216.0`. **Mechanism not attributed** — no code means missing value indistinguishable from censored run, unwritten column, aborted arm. v87 cites no frozen-vs-ARF race at L349, L353, or captions; no reconstruction, no candidate, no entry.

---

## D0–D3 table

| v87 site | printed | regenerated | witness | source | class |
| --- | --- | --- | --- | --- | --- |
| L349 Ljung–Box `γ_lev = 0` | `5.1 %` | **`5.4 %`** | `5.1 %` | `R12_leverage_fpr.csv`, `gamma_lev=0.0` / `lb_data_pct` | **D2** |
| L349 Ljung–Box `γ_lev = 0.28` | `24.6 %` | **`24.2 %`** | `24.6 %` | `R12_leverage_fpr.csv`, `gamma_lev=0.28` / `lb_data_pct` | **D2** |
| L349 FPR `γ_lev = 0` | `3.2 %` | **`3.5 %`** | `3.2 %` | `R12_leverage_fpr.csv`, `gamma_lev=0.0` / `fpr_data` | **D2** |
| L349 FPR `γ_lev = 0.28` | `20.6 %` | **`20.5 %`** | `20.6 %` | `R12_leverage_fpr.csv`, `gamma_lev=0.28` / `fpr_data` | **D2** |
| L349 Concept FPR min | `7.6 %` | **`7.4 %`** | `7.6 %` | `R12_leverage_fpr.csv`, min `fpr_concept` | **D2** |
| L349 Concept FPR max | `8.4 %` | **`8.5 %`** | `8.4 %` | `R12_leverage_fpr.csv`, max `fpr_concept` | **D2** |
| L349 Concept Ljung–Box min | `4.6 %` | **`4.7 %`** | `4.6 %` | `R12_leverage_fpr.csv`, min `lb_concept_pct` | **D2** |
| L349 Concept Ljung–Box max | `5.4 %` | `5.4 %` | `5.4 %` | `R12_leverage_fpr.csv`, max `lb_concept_pct` | D1 |
| L349 "factor of six" | `six` | `6` | `6` | `R12_leverage_fpr.csv`, `fpr_data` ratio | D1 |
| Fig.12 streams/point | `10 000` | `10 000` | `10 000` | `N_SEEDS_A` | **D0** |
| Fig.13 streams/point | `1 000` | `1 000` | `1 000` | `N_SEEDS_B` | **D0** |
| Fig.12 grid size | `15` | `15` | `15` | `GAMMA_LEV_GRID` | **D0** |
| Fig.13 `ν` grid size | `16` | `16` | `16` | `NU_GRID` | **D0** |
| L353 detection `ν = 10` | `83 %` | **`82 %`** | `83 %` | `R12_singularity_add.csv`, `nu=10` / `det_rate_data` | **D2** |
| L353 detection `ν = 7` | `61 %` | **`62 %`** | `61 %` | `R12_singularity_add.csv`, `nu=7` / `det_rate_data` | **D2** |
| L353 collapse threshold | `5.5` | `5.5` | `5.5` | `R12_singularity_add.csv`, max `ν` with `det_rate_data < 0.5` | D1 |
| L353 censored delay min | `2 400` | **`2 600`** | `2 400` | `R12_singularity_add.csv`, min `ADD_Data_Raw` | **D2** |
| L353 censored delay max | `3 000` | `3 000` | `3 000` | `R12_singularity_add.csv`, max `ADD_Data_Raw` | D1 |
| L353 Concept delay min | `34` | `34` | `34` | `R12_singularity_add.csv`, min `ADD_Concept` | D1 |
| L353 Concept delay max | `38` | `38` | `38` | `R12_singularity_add.csv`, max `ADD_Concept` | D1 |

**Full float64.** Regenerated: `5.41 / 24.19 / 3.46 / 20.48 / 7.38 / 8.47 / 4.65 / 5.37 / 5.919 / 0.825 / 0.621 / 5.5 / 2610.23 / 2998.77 / 33.638 / 37.9`. Witness: `5.13 / 24.6 / 3.24 / 20.64 / 7.63 / 8.37 / 4.63 / 5.44 / 6.37 / 0.83 / 0.607 / 5.5 / 2443.18 / 3005.28 / 33.96 / 38.28`.

**`83 % → 82 %` knife edge.** Regenerated rate exactly `825/1000 = 82.5 %`. Not representable in binary64; nearest double `0.82499999999999995559…` → `82` under all conventions. Displacement `−0.005` vs two-campaign SE `0.0168` (`0.30 σ`). Ordinary draw.

**Halt candidate did not fire.** v87 prints `2 400`–`3 000` rounded to hundreds → brackets `[2350, 2450)` and `[2950, 3050)`. Regenerated: min `2610.23` at `ν = 5.5` (SE `93.57`, 471 survivors, 95 % LB `2426.85`); max `2998.77` at `ν = 4.25` (SE `112.64`, 341 survivors). Max inside bracket (D1); min outside but LB covers `2400` → D2 at lower end only, not D3.

**Qualitative claims: all hold.**

| claim | measured | verdict |
| --- | --- | --- |
| L353 detection decays monotonically (uncensored) | 6/6 adjacent pairs decrease; 1 censored inversion, `z = −0.74`, interval covers zero | holds on declared domain |
| L353/Fig.13 collapses below 50 % threshold | every `ν ≤ 5.5` below `0.5` (max `0.4710`); every `ν > 5.5` ≥ `0.5` (min `0.5180`) | holds |
| L353/Fig.13 Concept delay flat | `ADD_Concept` spans `33.638`–`37.900` (12 % of mean) vs collapsing Data | holds |
| L349/Fig.12 leverage-invariant FAR | C9 slope `−0.9286`, 95 % `[−2.45, +0.66]`, `p = 0.248`; total drift `0.26` pp | holds |
| L349 baseline fails to control FAR | `3.46 % → 20.48 %`, crosses 5 % at `γ_lev = 0.08` | holds |

---

## Cosmetic divergence

Repository policy class; `ALL-figure-presentation` covers it. Single-panel figures: titles bold and centred, no letter prefix. Figure 12: asymmetric Wilson bands vs submitted symmetric normal half-widths (witness `ci_data`/`ci_concept` at `1.96` carried in CSV for comparability); Concept legend names the arm. Figure 13 censored branch: `SEM_Data_Raw` band (submitted artefact has no SE there). Both axes carry sample size. **No numerical value moves.**

Submitted PNGs `Fig15_Robustness_Leverage.png` and `Fig16_Robustness_FatTails.png` not present; comparison made against `Priorite_10` plotting code (l.276–298, l.406–451).

---

## Reproducibility

All runs produce same seven digests (SHA-256 verified). **C7 axis 1**: two consecutive executions byte-identical on all artefacts (repository acceptance criterion). **C7 axis 2**: different `--n-jobs` run byte-identical (fixed `NUM_CHUNKS_A = 25`, `NUM_CHUNKS_B = 10`, `NUM_CHUNKS_CLAMP = 4`). Run log, script, and `docs/sections/R12.md` pass repository grep with **zero** matches. Script re-serialises every frame to temp file, compares digest with written file → figures and macros **certified** to describe persisted campaign.

---

## Halt condition

**Not met.** Live candidates: C1 failing, `[2350, 3050)` bracket excluded by regenerated interval. C1 passed (producing site `len(d_concept) / n_seeds`, one site). Bracket intact at 95 % level. **No parameter, tolerance, seed, or bound moved.** No statistical control made to pass by modifying a draw.

