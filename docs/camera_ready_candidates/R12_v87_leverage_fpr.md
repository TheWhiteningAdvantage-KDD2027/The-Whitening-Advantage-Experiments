STATUS: PARKED — DO NOT APPLY

# R12 Camera-Ready Candidate: Leverage Misspecification (Figure 12)

The manuscript at L349 states that under asymmetric volatility clustering (GJR-GARCH with leverage gamma_lev > 0), residual Ljung-Box rejection rises from 5.1% to 24.6% at gamma_lev = 0.28, driving false-alarm rate from 3.2% to 20.6%. The sign pipeline remains immune to leverage with Ljung-Box rejection within 4.6--5.4% and false-alarm rate within 7.6--8.4% at its fixed threshold, climbing by a factor of six.

The reproduced measurements from `R12_leverage_fpr.csv` are:
- Data Ljung-Box at gamma_lev = 0.0: 5.4% (v87: 5.1%, D2)
- Data Ljung-Box at gamma_lev = 0.28: 24.2% (v87: 24.6%, D2)
- Data FPR at gamma_lev = 0.0: 3.5% (v87: 3.2%, D2)
- Data FPR at gamma_lev = 0.28: 20.5% (v87: 20.6%, D2)
- Concept FPR range: 7.4--8.5% (v87: 7.6--8.4%, D2)
- Concept Ljung-Box range: 4.7--5.4% (v87: 4.6--5.4%, D1-D2)
- Factor of six: 5.92 (v87: 6, D1)

All range claims are D2 due to campaign redraw. The leverage-invariant claim is tested by control C9 slope test (p = 0.2477) and holds qualitatively.

~~~~~~~~~~~latex
% Line 349: update leverage misspecification values
-\text{Ljung--Box rejection rises from $5.1\%$ to $24.6\%$ at $\gamma_{\mathrm{lev}} = 0.28$}
+\text{Ljung--Box rejection rises from $5.4\%$ to $24.2\%$ at $\gamma_{\mathrm{lev}} = 0.28$}

-\text{driving its false-alarm rate from $3.2\%$ to $20.6\%$}
+\text{driving its false-alarm rate from $3.5\%$ to $20.5\%$}

-\text{climbs by a factor of six}
+\text{climbs by a factor of 5.92}
~~~~~~~~~~~

~~~~~~~~~~~latex
% Line 349: update sign pipeline values
-\text{Ljung--Box rejection stays within $4.6$--$5.4\%$}
+\text{Ljung--Box rejection stays within $4.7$--$5.4\%$}

-\text{false-alarm rate within $7.6$--$8.4\%$}
+\text{false-alarm rate within $7.4$--$8.5\%$}
~~~~~~~~~~~

Cross-reference: docs/DEVIATIONS.md entry R12-campaign-redraw.
