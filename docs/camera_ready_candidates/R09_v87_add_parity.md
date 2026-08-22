STATUS: PARKED — DO NOT APPLY

# R09 Camera-Ready Candidate: ADD Parity at eta = 0.10

The manuscript at L243 states that at matched false-alarm rate and moderate drift, the mixture detects at least as fast as the fixed-horizon CUSUM ($409$ vs. $539$ steps at $\eta = 0.10$).

The reproduced measurements from `R09_eprocess_race.csv` at alpha = 0.05, eta = 0.10 are:
- MIX ADD: 410.40 with SEM 3.66
- CUSUM ADD: 532.85 with SEM 9.55

The discrepancy is classified as D1: float shifts but rounded value at printed precision is invariant for MIX (410 vs 409), and D1-D2 for CUSUM (533 vs 539). The qualitative claim that MIX is faster than CUSUM remains valid.

~~~~~~~~~~~latex
% Line 243: update ADD values to match reproduced measurements
-\text{MIX ADD at parity: } 409 \text{ vs. CUSUM: } 539
+\text{MIX ADD at parity: } 410 \text{ vs. CUSUM: } 533
~~~~~~~~~~~

Cross-reference: docs/DEVIATIONS.md entries R09-mix-add-parity-d1 and R09-cusum-add-parity-d2.

