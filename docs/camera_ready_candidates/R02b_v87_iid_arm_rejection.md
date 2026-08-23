# Camera-Ready Candidate: R02b_v87_iid_arm_rejection

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry: `none`

**Target file: `articleB_whitening_v87.tex`**

<<< SEARCH
~~~~~~~~~latex
already over-reject on the i.i.d.\ arm ($9.2\%$), where $t_7$ innovations deprive $\varepsilon_t^2$ of a fourth moment and the $\chi^2$ approximation fails
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
measure 8.8\% at $\nu = 5$ (95\% Wilson [7.2, 10.7]\%) and 7.9\% at $\nu = 6$ ([6.4, 9.7]\%), both excluding the nominal level, while at $\nu = 7$ the rate is 5.8\% [4.5, 7.4]\% and the mechanism as stated is incorrect: Ljung--Box asymptotics on $Y = \varepsilon_t^2$ require $E[\varepsilon^4] < \infty$ (hence $\nu > 4$), the moment that governs the tail quantile is $E[\varepsilon^8]$ which fails below $\nu \le 8$; the phenomenon is real but occurs at heavier tails than stated
~~~~~~~~~
>>> END OF BLOCK
