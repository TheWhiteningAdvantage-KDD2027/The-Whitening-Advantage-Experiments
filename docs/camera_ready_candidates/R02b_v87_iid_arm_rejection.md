STATUS: PARKED — DO NOT APPLY

## R02b: I.I.D. ARM Rejection Rate Correction (D3 Deviation)

The manuscript claims that Ljung--Box applied to squared innovations over-rejects on the i.i.d. arm at 9.2% with $t_7$ innovations. A dedicated sweep (R02b, 1000 streams per point, $n = 8000$, lag 20) measures the rejection rate on squared inputs across six degrees-of-freedom values. At $\nu = 5$, the rate is 8.8% with 95% Wilson [7.2, 10.7]%, and at $\nu = 6$, it is 7.9% [6.4, 9.7]%, both excluding the nominal 5% level. However, at $\nu = 7$, the rate is 5.8% [4.5, 7.4]%, which **includes** the nominal level.

The mechanism as stated is also incorrect: for an i.i.d. series, Ljung--Box asymptotics require a finite variance of the tested series; with $Y = \varepsilon_t^2$ that is $E[\varepsilon^4] < \infty$, hence $\nu > 4$, which holds at $t_7$. The moment that is missing below $\nu = 8$ is $E[\varepsilon^8]$, the fourth moment of $\varepsilon^2$, which governs the tail quantile rather than the validity of the limit.

~~~~~~~~~latex
SEARCH
already over-reject on the i.i.d.\ arm (9.2\%), where $t_7$ innovations deprive $\varepsilon_t^2$ of a fourth moment and the $\chi^2$ approximation fails
REPLACE WITH
measure 8.8\% at $\nu = 5$ (95\% Wilson [7.2, 10.7]\%) and 7.9\% at $\nu = 6$ ([6.4, 9.7]\%), both excluding the nominal level, while at $\nu = 7$ the rate is 5.8\% [4.5, 7.4]\% and the mechanism as stated is incorrect: Ljung--Box asymptotics on $Y = \varepsilon_t^2$ require $E[\varepsilon^4] < \infty$ (hence $\nu > 4$), not $E[\varepsilon^8] < \infty$; the phenomenon is real but occurs at heavier tails than stated
END OF BLOCK
~~~~~~~~~

Rationale: The original claim conflates two issues. First, the measured rate at the stated operating point ($t_7$) does not exclude the nominal level. Second, the theoretical justification misidentifies the moment condition. The corrected text preserves the qualitative finding (over-rejection at sufficiently heavy tails) while aligning with the measured data and the correct asymptotic theory.
