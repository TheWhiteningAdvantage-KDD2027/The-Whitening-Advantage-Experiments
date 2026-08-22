STATUS: PARKED — DO NOT APPLY

# R12 Camera-Ready Candidate: Moment Singularity (Figure 13)

The manuscript at L353 states that under Student-t innovations approaching the kurtosis singularity (nu -> 4), the Data pipeline detection decays monotonically (83% at nu = 10, 61% at nu = 7), collapses below the 50% censoring threshold for nu <= 5.5, with survivorship-biased delays of 2,400--3,000 steps. The Concept pipeline stays flat at 34--38 steps.

The reproduced measurements from `R12_singularity_add.csv` are:
- Detection at nu = 10: 82% (v87: 83%, D2)
- Detection at nu = 7: 62% (v87: 61%, D2)
- Collapse threshold nu: 5.5 (v87: 5.5, D1)
- Censored delay minimum: 2,610 (v87: 2,400 rounded to hundreds, D2)
- Censored delay maximum: 2,999 (v87: 3,000 rounded to hundreds, D1)
- Concept delay range: 34--38 (v87: 34--38, D1)

The censored delay range [2,610, 2,999] stays within the rounding bracket [2350, 3050) at the 95% level with bootstrap envelope [2432.3277, 3249.7077], satisfying S3's non-falsification criterion.

~~~~~~~~~~~latex
% Line 353: update detection rates
-\text{detection decays monotonically ($83\%$ at $\nu = 10$, $61\%$ at $\nu = 7$)}
+\text{detection decays monotonically ($82\%$ at $\nu = 10$, $62\%$ at $\nu = 7$)}

-\text{collapses below the $50\%$ censoring threshold for $\nu \le 5.5$}
+\text{collapses below the $50\%$ censoring threshold for $\nu \le 5.5$}
~~~~~~~~~~~

~~~~~~~~~~~latex
% Line 353: update survivorship-biased delays
-\text{survivorship-biased delays of $2\,{}400$--$3\,{}000$ steps}
+\text{survivorship-biased delays of $2\,{}610$--$2\,{}999$ steps}
~~~~~~~~~~~

~~~~~~~~~~~latex
% Line 353: update Concept pipeline delays
-\text{stays flat at $34$--$38$ steps}
+\text{stays flat at $34$--$38$ steps}
~~~~~~~~~~~

Cross-reference: docs/DEVIATIONS.md entries R12-campaign-redraw, R12-detection-rate-d2, R12-censored-delay-d2, R12-concept-delay-d1.
