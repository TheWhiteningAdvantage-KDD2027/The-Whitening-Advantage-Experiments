# Audit Report: R02b — IID ARM Mechanism Resolution

## 1. Deviation table (D0-D3)

| quantity                                                                                        | manuscript value                                                 | regenerated value                                                                                                                   | severity | source CSV cell                                                                        | log line |
| ----------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------- | -------- |
| Rejection rate on the i.i.d. arm at the manuscript's own `t_7` (L278)                           | 9.2% (over-rejects)                                              | 5.8%, Wilson [4.51, 7.43]%, which contains the 5% nominal level                                                                     | D3       | R02b_rejection_vs_nu.csv :: reject_rate_squared and contains_nominal_squared, row nu=7 | 10       |
| Rejection rate at nu=5.0, squared (R02b sweep, no published counterpart)                        | not printed in v87                                               | 8.8%, Wilson [7.20, 10.72]%, excludes nominal                                                                                       | n/a      | R02b_rejection_vs_nu.csv :: reject_rate_squared, row nu=5                              | 8        |
| Rejection rate at nu=6.0, squared (R02b sweep, no published counterpart)                        | not printed in v87                                               | 7.9%, Wilson [6.38, 9.74]%, excludes nominal                                                                                        | n/a      | R02b_rejection_vs_nu.csv :: reject_rate_squared, row nu=6                              | 9        |
| Nominal level excluded up to                                                                    | nu=7                                                             | nu=6                                                                                                                                | D2       | R02b_claims.tex :: RTwoBNominalExcludedUpTo                                            | 250-251  |
| Moment condition under which the chi-square approximation for Ljung-Box on `eps^2` holds (L278) | "$t_7$ innovations deprive $\varepsilon_t^2$ of a fourth moment" | the condition is `E[eps^4] < infinity`, i.e. `nu > 4`; `t_7` satisfies it, so no moment required by the limit is absent at `nu = 7` | D3       | R02b_rejection_vs_nu.csv :: contains_nominal_squared, row nu=7 = True                  | 10       |

Count by severity: D0: 0, D1: 0, D2: 1, D3: 2, plus 2 rows carrying no severity.

*Note: v87 prints one rate for one arm, at `t_7`; the `nu = 5` and `nu = 6` cells belong to R02b's own sweep, reproduce no published value, and carry no severity.*

**What L278 prints.** The clause audited here is quoted verbatim from line 278 of
`articleB_whitening_v87.tex`:

> The squared inputs reject whiteness in $100\%$ of the clustered calibrations ($p < 10^{-10}$) and
> already over-reject on the i.i.d.\ arm ($9.2\%$), where $t_7$ innovations deprive
> $\varepsilon_t^2$ of a fourth moment and the $\chi^2$ approximation fails

It carries two distinct assertions. The first is a **rate**, $9.2\%$. The second is a **mechanism**:
that at $\nu = 7$ the squared innovation stream has no fourth moment, and that this absence is what
makes the $\chi^2$ approximation fail. The four D2 rows above concern the rate. The D3 row concerns
the mechanism.

**The condition the limit actually requires, derived.** The Ljung-Box statistic is computed on a
*tested* series; on the i.i.d. arm the tested series is `Y_t = eps_t^2`. For an i.i.d. tested series
the sample autocorrelations at fixed lags are jointly asymptotically normal with covariance `I/n`
under the single requirement that the tested series have a finite variance
[Anderson and Walker, 1964, Ann. Math. Statist. 35(3), 1296-1303; Brockwell and Davis, 1991,
*Time Series: Theory and Methods*, Theorem 7.2.1]. The numerator of the lag-`k` sample
autocovariance is a sum of the i.i.d. summands `(Y_t - mu)(Y_{t+k} - mu)`, whose variance is
`Var(Y)^2` under independence, and the denominator is `sum (Y_t - mu)^2`, whose law of large numbers
needs `E[Y^2]`. Both requirements reduce to the same one: `Var(Y) < infinity`, i.e.
`E[eps^4] < infinity`. For Student-$t_\nu$ innovations `E[|eps|^p] < infinity` if and only if
`p < nu`, so the requirement is `nu > 4`. `t_7` satisfies it. The condition on which the derivation
rests is that the tested series be i.i.d.; on this arm it is, by construction of the arm.

The moment that is absent at `nu <= 8` is `E[eps^8] = E[Y^4]`, the fourth moment of the *tested*
series. It does not enter the requirement above. It governs the tail quantile of the sample
autocorrelations — the rate at which the finite-sample distribution approaches its limit — rather
than the existence or the identity of that limit.

**Empirical settlement from R02b's and R02c's own artefacts.** Both files are read with
`float_precision='round_trip'`. In `R02b_rejection_vs_nu.csv` at `n = 8000`, 1000 streams per point,
the Wilson 95% interval on the squared-stream rejection rate is `[4.51, 7.43]%` at `nu = 7` and
contains the nominal 5% level (`contains_nominal_squared = True`, log line 10), while it is
`[7.20, 10.72]%` at `nu = 5` and `[6.38, 9.74]%` at `nu = 6` and excludes the nominal level in both
(log lines 8-9). `R02c_rejection_vs_horizon.csv` repeats the three points at horizons
`n = 2000, 8000, 32000, 128000`: the `nu = 7` interval contains the nominal rejection level at all
four horizons and the `nu = 5` and `nu = 6` intervals exclude it at all four, with every slope of
the rate against `log n` indistinguishable from zero (log lines 9-11). Pooled over the four
horizons, the rejection rate is 7.75% `[6.96, 8.62]%` at `nu = 5`, 7.72% `[6.94, 8.59]%` at
`nu = 6`, and 5.60% `[4.93, 6.36]%` at `nu = 7`.

The eighth-moment account is refuted by its own control. `E[eps^8]` is infinite for every
`nu <= 8`, `nu = 7` included; if the absence of that moment were the operative cause, the `nu = 7`
arm would over-reject with the other two. It does not, at any of the four horizons, and R02c's
witness control at `nu = 7` returns a KS statistic of 0.3666 against Uniform(0,1) with p-value
0.5480 (log lines 14-15).

**Falsified qualitative claim.** The printed clause states the condition under which the $\chi^2$
approximation for the Ljung-Box statistic on $\varepsilon_t^2$ holds, and states it incorrectly. The
requirement is `E[eps^4] < infinity`, i.e. `nu > 4`, which `t_7` meets; `t_7` does not deprive
$\varepsilon_t^2$ of a fourth moment, and the failure asserted at $\nu = 7$ is not reproduced there.
A false statement of the condition under which an asymptotic approximation holds is a qualitative
claim, not a numeral, and its falsification is D3 under the D0-D3 scale. The alternative account —
that the absent moment is `E[eps^8]` — is refuted by the same artefacts, since that moment is absent
at `nu = 7` as well.

**Scope:** what is contradicted is twofold: first, the stated *reason* the $\chi^2$ approximation fails on the i.i.d. arm; second, the qualitative claim that the manuscript's own $t_7$ arm "already over-rejects". At $\nu = 7$ the regenerated rate is 5.8% and its Wilson interval $[4.51, 7.43]\%$ contains nominal. At $n = 1000$ streams, the standard error of a rate near 5% is 0.0069. The printed 9.2% lies six standard errors from nominal, so the experiment has the resolution to distinguish it. Because the interval explicitly excludes the printed 9.2% and contains 5%, the published value is rejected and the over-rejection claim is formally falsified. What it does **not** touch: the whitening property; the exactness of the Concept threshold; the binary-error arm's nominal level; and any proposition of v87.

The regenerated sweep does find over-rejection at `nu = 5` (8.8%) and `nu = 6` (7.9%), both excluding nominal, but neither is the manuscript's arm and neither reproduces a published value. The falsification of the over-rejection claim is strict and localized to the $t_7$ arm defined by the text.

**The true mechanism is not identified.** R02b and R02c locate the effect: the over-rejection is
present at `nu <= 6` and absent at `nu >= 7`, at every horizon tested up to `n = 128000`, and that
boundary coincides with the loss of the sixth moment (`E[eps^6] < infinity` if and only if
`nu > 6`). Locating a boundary is not establishing a cause. Neither stream tested a candidate
mechanism against an alternative that would discriminate it, and this audit supplies none. What the
campaign has is a refutation of two accounts — the printed fourth-moment one and the eighth-moment
one — and a coincidence of the empirical boundary with a third moment condition, which is not
evidence that the third condition is the cause.

The manuscript reports a single i.i.d. arm over-rejection rate of 9.2% at line 278 without
specifying the degrees of freedom. The compliant pipeline extends this to a full nu grid and finds
the rate varies with tail heaviness. Under strict S7 determinism, the simulated paths differ from
the original campaign, producing different rejection rates. The qualitative claim that heavy-tailed
i.i.d. streams (nu <= 6) over-reject is corroborated: nu=5 and nu=6 both exclude the nominal 5%
level, while nu=7 contains it in the compliant run. The manuscript implication that the nominal
level is excluded at nu=7 is not reproduced (excluded only up to nu=6); that row stays D2 because
the over-rejection phenomenon itself is corroborated and the transition sits between nu=6 and nu=7
in both readings.

## 2. Controls

### Negative control: raw innovations calibration
Tests that the Ljung-Box test applied to raw (unsquared) t innovations holds the nominal 5% level across all nu values. This is a necessary condition for the squared-stream over-rejection to be interpretable as a tail effect rather than a global calibration failure.

Trigger probability under its own null hypothesis: the control is not a hypothesis test with a type-I error probability; it is a validation gate that the Wilson 95% confidence interval on the raw-stream rejection rate must contain the nominal level 0.05. The trigger probability is therefore NOT RECOVERABLE FROM THE LOG.

Realised margin: for all nu values, the Wilson interval on reject_rate_raw contains 0.05. The log lines 8-13 report reject_raw values (0.057, 0.043, 0.057, 0.042, 0.042, 0.046) with corresponding Wilson intervals computed in R02b_rejection_vs_nu.csv (columns wilson_low_raw, wilson_high_raw), all of which contain 0.05. Verdict: PASS.

This control was originally a hard gate (exits with code 1 on failure at exp_R02b_iid_arm_resolution.py lines 162-164) and remains so in the compliant pipeline. It was not demoted.

## 3. Test suite

```
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/m53/The-Whitening-Advantage-Experiments
plugins: anyio-8.0
collecting ... collected 5 items

tests/test_R02b_claims.py::test_negative_control_integrity PASSED        [ 20%]
tests/test_R02b_claims.py::test_nu_seven_is_indistinguishable_from_nominal PASSED [ 40%]
tests/test_R02b_claims.py::test_heavy_tail_arms_exclude_nominal PASSED   [ 60%]
tests/test_R02b_claims.py::test_rate_ordering_heavy_versus_light PASSED  [ 80%]
tests/test_R02b_claims.py::test_negative_control_matches_squared_at_light_tails PASSED [100%]

============================== 5 passed in 0.33s ===============================
```

5 passed in 0.33s.

## 4. Reproducibility digests

Single run recorded in log:
- 1 workers: R02b_streams.csv [bf7576712c9bf483cfa3e6bfaaa2387e2caf78f45d79397c46ea26aa315ff4d7], R02b_rejection_vs_nu.csv [c7cbe11395f952f73eba57df05bf50b270c081c794d187823a1ae0d2ed3de183], figA01_iid_overrejection_vs_nu.png [a4d85a73c9fa8a552eaeb14dc28d8dc96591ac55292a4697cc8640e8286c8b7e], R02b_claims.tex [b0e0b50427d4d6c6d3b3317822a6ba458389341e93c2e1a13db43360f598fb90] (log lines 17-22)

Current tree, single run:
```
$ sha256sum results/R02b_iid_arm_resolution/data/*.csv results/R02b_iid_arm_resolution/tables/*.tex
c7cbe11395f952f73eba57df05bf50b270c081c794d187823a1ae0d2ed3de183  results/R02b_iid_arm_resolution/data/R02b_rejection_vs_nu.csv
bf7576712c9bf483cfa3e6bfaaa2387e2caf78f45d79397c46ea26aa315ff4d7  results/R02b_iid_arm_resolution/data/R02b_streams.csv
b0e0b50427d4d6c6d3b3317822a6ba458389341e93c2e1a13db43360f598fb90  results/R02b_iid_arm_resolution/tables/R02b_claims.tex
```

## 5. Design decisions taken outside the plan

1. The nu grid {5.0, 6.0, 7.0, 8.5, 12.0, 30.0} was chosen to bracket the finite fourth-moment boundary at nu=4 and to probe the transition region where E[eps^4] is large but finite. This extends the manuscript's single t_7 point to a full dimensioning study.

2. Deterministic seeding uses 128-bit entropy via SeedSequence with md5-based hash derivation from the tuple ("R02b", nu, seed_idx) at exp_R02b_iid_arm_resolution.py lines 71-79, ensuring no seed collision across the 6000 streams. Collision check is performed at lines 135-138.

## 6. Open questions, left open

None recorded.

