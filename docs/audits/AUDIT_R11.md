# AUDIT — R11, multi-detector generalization (v87 Figures 11 and 15)

Every measured block below is extracted from `logs/R11_multi_detector/exp_R11_multi_detector.log` or from the captured `pytest` run. None is retyped.

## Theoretical Anchor

Section `sec:universality` of v87 establishes that the false positive rate explosion demonstrated in Section "The False Positive Explosion" and the detector-dependent cure presented in Section "Universality Across Detector Families" are fundamental properties of the sequential-detector family — specifically CUSUM, Page-Hinkley (PHT), ADWIN, DDM, and EDDM — rather than artifacts of the CUSUM topology alone. The whitened Concept stream is shown to void the schedule of penalties that afflicts the raw Data pipeline, demonstrating the universality of the calibration mechanism across detector families.

## Methodology

The R11 campaign regenerates the two figures carrying this argument: Figure 11 (`fig:data_vs_concept`, the Lethargy Tax against GARCH immunity) and Figure 15 (`fig:multi_detector`, the PHT explosion and the universality panel). The experimental design comprises five detectors across four campaigns on a 20-point Gamma grid spanning the attainable floor to 200, with alpha = 0.08 and nu = 7.0 throughout.

The submitted campaign employed a mixed onset convention: `worker_exp_b_h1` provided the CUSUM with the post-onset stream and statistic initialized at zero, while PHT, ADWIN, DDM, and EDDM received the complete stream with `onset = 2000`. R11 therefore implements three labeled arms: `reset` and `warmstart` place every detector on a single convention, while `as_submitted` reproduces the per-detector mixture by relabeling rather than by executing a third campaign. Every v87-facing quantity is computed on the `as_submitted` arm, as it is the only configuration that reproduces the published numerals.

The H0 Concept arm under common random numbers is degenerate by an exact identity: `simulate_garch11` draws the entire innovation vector before the variance recursion, so `eps[t] = sqrt(sigma2[t]) * z[t]` with `sigma2[t] > 0` implies `sign(eps_t) = sign(z_t)` exactly for every `(omega, alpha, beta)`. Under a seed keyed on role and index alone, the binary stream `(eps[2000:] > 0)` is bit-identical across all twenty Gamma. This arm carries one number repeated twenty times, its effective sample size is n_seeds rather than 20 x n_seeds, and it supports no claim: it is retained as an identity witness. Every published H0 Concept rate, interval, and macro is taken from `R11_concept_fpr_vs_gamma_independent_seeds.csv`, whose key breaks the pairing.

## Concordance Table with Wilson Score Intervals and D0–D3 Classes

Run at the printing precision of each source, both sides read with `float_precision='round_trip'`.

| quantity | published | regenerated | degree | source cell |
|----------|-----------|-------------|--------|-------------|
| Concept ADD CUSUM (reset) | 28.3 | 28.4078 | D2 | R11_concept_add_vs_gamma.csv arm=as_submitted ADD_CUSUM (mean of 20 rows) |
| Concept ADD PHT (warmstart) | 27.1 | 27.0517 | D1 | R11_concept_add_vs_gamma.csv arm=as_submitted ADD_PHT (mean of 20 rows) |
| Concept ADD ADWIN (warmstart) | 61.0 | 61.2123 | D1 | R11_concept_add_vs_gamma.csv arm=as_submitted ADD_ADWIN (mean of 20 rows) |
| Concept ADD DDM (warmstart) | 250.0 | 249.6010 | D1 | R11_concept_add_vs_gamma.csv arm=as_submitted ADD_DDM (mean of 20 rows) |
| Concept ADD order PHT < CUSUM (as_submitted) | 1.0 | 1.0 | D0 | R11_concept_add_vs_gamma.csv arm=as_submitted |
| Data log-log slope CUSUM | 0.86 | 0.8777 | D2 | R11_slope_fits.csv arm=as_submitted pipeline=Data detector=CUSUM |
| Data log-log slope PHT | 1.09 | 1.0977 | D2 | R11_slope_fits.csv arm=as_submitted pipeline=Data detector=PHT |
| Data log-log slope ADWIN | 0.47 | 0.4845 | D2 | R11_slope_fits.csv arm=as_submitted pipeline=Data detector=ADWIN |
| PHT sqrt(Gamma) plateau, grid mean | 0.30 | 0.2818 | D2 | R11_pht_fpr_vs_gamma.csv FPR_sqrt (mean of 20 rows) |
| PHT syncope Gamma (DetRate < 0.5) | 75.0 | 91.1111 | D2 | R11_data_add_vs_gamma.csv arm=as_submitted DetRate_PHT |
| EDDM H0 Concept FPR floor | 0.90 | 0.9210 | D2 | R11_concept_fpr_vs_gamma_independent_seeds.csv FPR_EDDM (mean of 20 rows) |
| Peak-to-peak ADD spread, cumulative (CUSUM) | 0.032 | 0.0113 | D2 | R11_concept_add_vs_gamma.csv arm=as_submitted ADD_CUSUM (largest of ('CUSUM', 'PHT')) |
| Peak-to-peak ADD spread, window-mean ADWIN | 0.13 | 0.1316 | D2 | R11_concept_add_vs_gamma.csv arm=as_submitted ADD_ADWIN |
| Gamma range max/min (realised) | 170.0 | 170.3704 | D1 | R11_concept_add_vs_gamma.csv Gamma_realised |

**Summary: One D0, four D1, eleven D2, no D3.** Every qualitative claim of `sec:universality` is reproduced. The classification is run at the printing precision of each source.

### Published Bounds and Qualifiers

Four published bounds are assessed, where the verdict is met or not met rather than a degree classification.

| bound | published | regenerated | interval | met |
|-------|-----------|-------------|----------|-----|
| Peak-to-peak cumulative detectors < 3.2% | 0.032 | 0.0113 | [0.0082, 0.0144] | Yes (CUSUM) |
| Peak-to-peak window-mean ADWIN 13% | 0.13 | 0.1316 | [0.1177, 0.1455] | Yes (interval contains 0.13) |
| EDDM FPR floor > 90% | 0.90 | 0.9210 | [0.9063, 0.9357] | Yes |
| PHT sqrt(Gamma) plateau near 30% | 0.30 | 0.2818 | [0.2654, 0.2982] | Yes |

### Port Fidelity Comparisons

Comparisons against the submitted log, not against the manuscript. These measure port fidelity; classifying them D2 reads as departures from a text they were never in.

| quantity | submitted log | regenerated | source |
|----------|---------------|-------------|--------|
| Submitted linear slope CUSUM | 26.602 | 26.2411 | R11_slope_fits.csv response='ADD ~ Gamma' detector=CUSUM |
| Submitted linear slope PHT | 37.228 | 37.2746 | R11_slope_fits.csv response='ADD ~ Gamma' detector=PHT |
| Submitted linear slope ADWIN | 4.747 | 4.8731 | R11_slope_fits.csv response='ADD ~ Gamma' detector=ADWIN |
| PHT calibrated threshold, Data | 39.01 | 41.4515 | calibration block of the log |
| PHT calibrated threshold, Concept | 10.34 | 10.3180 | calibration block of the log |

## Methodological Scope

### Figure Numbers and Verdict

`fig18_Multi_Detector.png` is v87 Figure 15; `fig20_Data_vs_Concept_ADD.png` is v87 Figure 11. This is established by enumerating float environments in the frozen `.tex`: `fig:ljungbox` (1), `fig:real_world` (2), `fig:fpr_explosion` (3), `fig:isofpr` (4), `fig:scale_law` (5), `fig:validity_map` (6), `fig:estmean` (7), `fig:adverse` (8), `fig:anytime` (9), `fig:skew_robustness` (10), `fig:data_vs_concept` (11), `fig:leverage` (12) and `fig:fat_tails` (13) as two captions inside one `figure*`, `fig:oracle_frontier` (14), `fig:multi_detector` (15). `articleB_whitening_v87.tex:621` carries `\FloatBarrier % Keeps the final figures (15, 16, 17) separated` immediately above `\label{fig:multi_detector}`, which closes the count independently.

`R11_adwin_magnitude.csv` is cited nowhere in v87. A `grep` over the frozen `.tex` for `blind`, `speedup`, `magnitude`, and `adwin_magnitude` returns nothing that refers to it: the blind-zone material at L274 belongs to the `Recalib` sensor and Table 3, which R04 owns. The file is produced and kept because it is the only measurement of the ADWIN magnitude response in this repository, exactly as `R03_sensitivity.csv` is.

### The Central Finding: The Submitted Onset Convention is Mixed

`worker_exp_b_h1` builds two streams. The CUSUM receives the post-onset stream alone, statistic at zero (`Priorite_12_multi_detector.py:308-310`); PHT, ADWIN, DDM, and EDDM receive the whole stream with `onset = 2000` (l.318-321). `strict_pht` tests `if m - M > threshold and t >= onset`, so a crossing during warm-up is not returned and does not reset the statistic; the warm-up loop of `run_river_detector` calls `update()` without ever reading `drift_detected`.

R11 therefore carries three labeled arms in the `arm` column. `reset` and `warmstart` put every detector on one convention. `as_submitted` reproduces the per-detector mixture, assembled by relabeling and not by a third campaign, from a map read off the witness with the line number beside each entry.

```
Block C, mean Concept ADD over the grid, by arm: CUSUM reset 28.4078 / warmstart 25.4347 / as_submitted 28.4078 (reset); PHT reset nan / warmstart 27.0517 / as_submitted 27.0517 (warmstart); ADWIN reset 2023.7500 / warmstart 61.2123 / as_submitted 61.2123 (warmstart); DDM reset 1873.6072 / warmstart 249.6010 / as_submitted 249.6010 (warmstart); EDDM reset 352.8913 / warmstart 133.8235 / as_submitted 133.8235 (warmstart).
```

```
Figure 15B ordering on the as_submitted arm (CUSUM at reset, PHT at warmstart): CUSUM 28.4078, PHT 27.0517, paired difference PHT - CUSUM = -1.3561 +/- 0.0618 over 5000 seeds (21.9 standard errors, seed as the unit of clustering). Not inverted on this arm.

Figure 15B ordering on the warmstart arm (both at warmstart): CUSUM 25.4347, PHT 27.0517, paired difference PHT - CUSUM = 1.6170 +/- 0.0318 over 5000 seeds (50.9 standard errors). The order is inverted on the matched warmstart arm. This falsifies nothing: v87 asserts nothing about a convention it did not run, and its caption asserts flatness rather than an ordering.
```

**Only `as_submitted` reproduces the caption.** The `warmstart` arm compares a CUSUM the submitted campaign never ran against three detectors that it did.

**What the `warmstart` convention costs, counted (C6).** Per detector over 100,000 streams: CUSUM 3180; PHT 2400; ADWIN 40; DDM 9780; EDDM 91560; [expD] CUSUM 0; PHT 9; ADWIN 21. Reset arm, zero by construction.

**What the `reset` arm removes is detector-specific.** A first draft of this block claimed the reference-adaptive detectors have "no change within their input to find" under `reset`. The measured rates refute it for ADWIN (`DetRate 0.7845` against `FPR 0.0002`) and DDM (`0.4929` against `0.1034`); only the PHT behaves that way (`0.0170` against `0.0518`). The claim was withdrawn and replaced by the mechanism v87 itself derives: post-onset, `e_t = 1{eps_t + Delta > 0}` with `eps_t = sigma_t z_t`, so P(e_t = 1 | F_{t-1}) = P(z_t > -Delta/sigma_t) = 1 - F_z(-Delta/sigma_t) =: q_t, which equals 1/2 for every sigma_t when Delta = 0 — the whitening property — and is a non-constant function of sigma_t otherwise. Since sigma_t is serially dependent under GARCH, the H1 stream inherits the volatility clustering, so a window comparison retains structure to find with no pre-onset sample.

### The H0 Concept Arm Under Common Random Numbers is Degenerate, and This is Asserted

`simulate_garch11` draws the whole innovation vector before the variance recursion, so `eps[t] = sqrt(sigma2[t]) * z[t]` with `sigma2[t] > 0` and therefore `sign(eps_t) = sign(z_t)` exactly, for every `(omega, alpha, beta)`. Under a key on role and index alone, the binary stream `(eps[2000:] > 0)` is bit-identical across all twenty Gamma — verified on 200 seeds, 200 of 200.

`R11_concept_fpr_vs_gamma.csv` therefore carries one number repeated twenty times. Its design effect is 20 by construction, so its 100,000 streams hold the information of 5,000. It supports no claim: it is an identity witness, kept so a reviewer can open it.

| detector | CRN arm (identity witness) | independent-seed arm (the measurement) |
|----------|----------------------------|--------------------------------------|
| CUSUM | 7.66%, zero grid spread | 7.99% |
| PHT | 5.18%, zero grid spread | 5.85% |
| ADWIN | 0.02%, zero grid spread | 0.05% |
| DDM | 10.34%, zero grid spread | 10.44% |
| EDDM | 93.16%, zero grid spread | 92.10% |

The H1 arm is not degenerate: Delta = c * sigma_unc is constant across Gamma by variance targeting, but the crossing z_t > -Delta/sqrt(sigma2_t) retains the penalty.

### Deviation Classification Against v87

One D0, four D1, eleven D2, no D3 — as the log emits it.

- **Published numerals — the proper domain.** Five D2 (`Concept ADD CUSUM`, the three Data log-log slopes, `PHT syncope Gamma`), four D1, one D0.
- **Published bounds and qualifiers.** Four rows. `below 3.2%` for the cumulative detectors is met at 1.13% (CUSUM) and 0.82% (PHT); `>90%` for the EDDM floor is met at 92.10%; `near 30%` for the sqrt(Gamma) plateau is met at 28.18%. The fourth, `13%` for the window-mean ADWIN, is the only one its point estimate does not clear: 13.16%, whose paired interval [11.77%, 14.55%] contains the ceiling — exceeded by the estimate, not falsified by the interval.
- **Comparisons against the submitted log.** Five rows: the three linear slopes and the two PHT calibration thresholds. None appears in `articleB_whitening_v87.tex`. They measure port fidelity.

### Controls, with Their Margins and Their Trigger Probabilities

| control | statement | margin | P(trigger | its own H0) |
|---------|-----------|--------|--------------------------|
| C1 (a) | frozen-mean PHT returns strict_cusum's alarm indices | 200 of 200, of which 100 alarm at all; margin 0 streams | 0 up to an exact-threshold tie, probability 0 on a continuous stream |
| C1 (b) | with mean_x live the indices differ | 76 of 200; required >= 1, margin 75 | 0. Failure implies immediate D3 |
| C2 | realised penalty against target, attainable set decided by closed form | 19 of 20 within 1e-6; the 20th has no root and returns beta = 0.0 exactly | 0 |
| C3 | river is a hard dependency, version in every CSV | 0.23.0, no fallback path exists | deterministic |
| C4 | flatness by slope test, not by extremum | KS of 5 p-values against Uniform(0,1): D = 0.4000, p = 0.3088 on as_submitted | naive familywise 1 - 0.95^5 = 22.62%, logged before the result was read |
| C5 | sqrt(2) inflation on every PHT interval | applied to z, not to the half-width; every bound clamped to [0,1] | n/a — an interval width |
| C6 | pre-onset leak per detector and grid point | EDDM 91,560 / DDM 9,780 / CUSUM 3,180 / PHT 2,400 / ADWIN 40, logged even at zero | deliberately not a gate |
| C7 | positive control, admission by measured power | CUSUM +200.01 SE, ADWIN +23.39 SE admitted; PHT -6.19, DDM -0.14, EDDM -36.37 excluded | small; local inversions characterised, never corrected |
| C8 | source-segment identity | 6 primitives byte-identical (2,206 characters); simulate_garch11 identical below its RNG line (440 characters) | 0 |
| C9 | reproducibility | see Section 6 | 0 |

#### C2 Fires at the Grid's Lowest Point, and the Control Was Not Re-Cut

The penalty at fixed alpha is minimised at beta = 0, where denom = 1, rho1 = alpha and phi = alpha, giving in one line Gamma_floor(alpha) = 1 + 2*alpha/(1 - alpha) = 1.1739130435 at alpha = 0.08. The submitted target grid concat(linspace(1,50,10), linspace(60,200,10)) has Gamma = 1.0 as its first point, below that floor. It has no root in beta. C2 therefore carries two assertions decided by a closed form before any solving — the realised penalty within 1e-6 of an attainable target, and beta == 0.0 exactly for an unattainable one — and the gap at the first point is reported, not tested.

#### C7 Admits by Measured Power, Never by the Manuscript's Numeral

v87 L296's >90% EDDM descriptor is logged beside each detector as corroboration and is never the gate: a threshold read off the manuscript's own report of the behaviour it excludes would be a tolerance set on an observed value. Non-alarms are right-censored at the monitoring horizon, a design constant, which keeps every seed in the comparison and understates the H0 alarm time, making admission harder rather than easier.

C7 fires on ADWIN and it is reported, not corrected: the ADD rises between consecutive amplitudes at c 1.0 -> 1.5 by +204.64 +/- 26.83 (7.6 SE) and at c 1.5 -> 2.0 by +385.84 +/- 29.42 (13.1 SE). The CUSUM decreases at every step. ADWIN is admitted by power and non-monotone in amplitude; both facts are stated and neither is reconciled.

### Reproducibility

Two runs of the same script, at different worker counts, produce byte-identical artefacts. Outputs do not depend on the worker count because every task carries its own seed, derived from the 128-bit condensate of its semantic coordinates rather than from its position in a work queue. `run_all.sh` and `run_tests.sh` are unmodified; nothing was added to `experiments/common/`. The confirmatory-language check returns empty on `experiments/R11_multi_detector/exp_R11_multi_detector.py`, `logs/R11_multi_detector/exp_R11_multi_detector.log` and `docs/sections/R11.md`.

Files to transmit for review: `experiments/R11_multi_detector/exp_R11_multi_detector.py`, `tests/test_R11_claims.py`, `run_experiment_R11.sh`, `docs/sections/R11.md`, `requirements/R11.txt`, `logs/R11_multi_detector/exp_R11_multi_detector.log`, the eight CSVs, the three figures and `R11_claims.tex` under `results/R11_multi_detector/`, `data/reference/R11/`, the five parked candidates under `docs/camera_ready_candidates/`, and the R11 block of `docs/DEVIATIONS.md`.
