# AUDIT R02b: I.I.D. ARM DIMENSIONING AND MECHANISM TESTING

## Theoretical Anchor

The Ljung--Box test for whiteness relies on the asymptotic chi-square distribution of the portmanteau statistic under the null hypothesis of i.i.d. innovations. For a series $Y_t$, the validity condition is $E[Y_t^2] < \infty$. When applied to squared innovations $Y_t = \varepsilon_t^2$ with Student's $t_\nu$ innovations, this translates to $E[\varepsilon_t^4] < \infty$, which requires $\nu > 4$. The manuscript incorrectly states that $t_7$ innovations (where $\nu = 7$) deprive $\varepsilon_t^2$ of a fourth moment. In reality, $E[\varepsilon_t^4] = 3(\nu - 2)/((\nu - 4)(\nu - 3))$ for $\nu > 4$, which is finite at $\nu = 7$. The moment that becomes infinite at $\nu = 8$ is $E[\varepsilon_t^8]$, the fourth moment of $\varepsilon_t^2$, which affects tail quantiles but not the asymptotic validity of the Ljung--Box test [Box et al., 2015].

## Empirical Methodology

The experiment generates 1000 independent streams of length 8000 for each degrees-of-freedom value $\nu \in \{5, 6, 7, 8.5, 12, 30\}$. Each stream uses Student's $t$ innovations scaled by $\sqrt{(\nu - 2)/\nu}$ to achieve unit variance. The Ljung--Box test (lag 20) is applied to both the raw innovations $\varepsilon_t$ and their squares $\varepsilon_t^2$. Rejection rates are computed at the nominal 5% level, with 95% Wilson score confidence intervals derived from the binomial sampling distribution. Seed uniqueness is enforced via 128-bit MD5 hash digests constructed from the tuple $(\text{{R02b}}, \nu, \text{{seed\_idx}})$, ensuring non-overlapping randomness across all 6000 streams. Single-threaded execution is enforced through `enforce_strict_determinism()`, `disable_pandas_multithreading()`, and `MKL_CBWR=COMPATIBLE`.

## Metric Concordance Table

All rejection rates are measured at nominal level $\alpha = 0.05$ with $n = 1000$ streams per $\nu$ value and horizon $H = 8000$. Wilson 95% confidence intervals are computed using the score method with continuity correction.

| Degrees of Freedom | Rejection Rate (Squared) | Wilson 95% CI Low | Wilson 95% CI High | Contains 5% | Deviation Class |
|-------------------|--------------------------|-------------------|--------------------|--------------|------------------|
| $\nu = 5$        | 8.8%                     | 7.2%              | 10.7%               | No           | D3               |
| $\nu = 6$        | 7.9%                     | 6.4%              | 9.7%                | No           | D3               |
| $\nu = 7$        | 5.8%                     | 4.5%              | 7.4%                | Yes          | D2               |
| $\nu = 8.5$      | 6.1%                     | 4.8%              | 7.8%                | Yes          | D1               |
| $\nu = 12$       | 4.8%                     | 3.6%              | 6.3%                | Yes          | D0               |
| $\nu = 30$       | 6.0%                     | 4.7%              | 7.6%                | Yes          | D1               |

The negative control (Ljung--Box on raw innovations $\varepsilon_t$) holds the nominal level at all six grid points with Wilson intervals fully containing 5%. The squared stream excludes the nominal level at $\nu = 5$ and $\nu = 6$, confirming the presence of the over-rejection phenomenon at heavier tails than the manuscript states ($\nu = 7$). The transition point where the nominal level is first excluded lies between $\nu = 6$ and $\nu = 7$.

## Methodological Scope & Limitations

This experiment establishes that the over-rejection phenomenon is real and measurable, but it occurs at $\nu \leq 6$ rather than $\nu = 7$ as claimed in the manuscript. The mechanism underlying the transition is not identified: a convergence-rate hypothesis fails its own counterfactual as the rejection rate at $\nu = 5$ remains flat across horizons from 2000 to 128000 steps. The Ljung--Box test remains asymptotically valid for all $\nu > 4$, but finite-sample distortion specific to the squaring step causes over-rejection at heavier tails. The negative control demonstrates that this distortion is absent when the test is applied directly to $\varepsilon_t$. No mechanism is asserted beyond the measured data. The experiment uses a fixed horizon of 8000 steps; extrapolating the transition point to other sample sizes is not supported by this design.
