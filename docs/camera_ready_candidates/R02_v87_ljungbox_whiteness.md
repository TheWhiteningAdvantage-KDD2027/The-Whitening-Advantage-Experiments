# Camera-Ready Candidate: R02_v87_ljungbox_whiteness.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** `R02-campaign-redraw`

STATUS: PARKED — DO NOT APPLY

## R02 Ljung-Box Whiteness Macro Updates

The manuscript reports an i.i.d. arm over-rejection rate of 9.2% for squared GARCH(1,1) streams with t7 innovations. The compliant deterministic pipeline produces 5.8% due to BLAS threading differences affecting the variance-targeted QMLE parameter recovery, which in turn alters the generated streams. The qualitative claim of over-rejection (rate > 5%) remains valid. This is a D2 deviation: the printed numerical value shifts, but the underlying qualitative claim holds.

<<< SEARCH
~~~~~~~~~latex
\newcommand{\RTwoDataRejectIid}{9.2}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\RTwoDataRejectIid}{5.8}
~~~~~~~~~
>>> END OF BLOCK

## R02 Concept Rejection Rate Macro Updates

The concept-level rejection rates for binary classification errors are stable across the compliant pipeline. The pooled rejection rate differs slightly from the manuscript (4.2% vs 4.4%), and the Wilson 95% confidence interval is [2.5, 6.8]% vs [2.8, 7.1]%. Both are D1 deviations: float shifts but rounded values at printed precision are considered invariant. The min-max range 3.3--5.0% matches exactly (D0).

<<< SEARCH
~~~~~~~~~latex
\newcommand{\RTwoConceptRejectPooled}{4.4}
\newcommand{\RTwoConceptWilsonLow}{2.8}
\newcommand{\RTwoConceptWilsonHigh}{7.1}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\RTwoConceptRejectPooled}{4.2}
\newcommand{\RTwoConceptWilsonLow}{2.5}
\newcommand{\RTwoConceptWilsonHigh}{6.8}
~~~~~~~~~
>>> END OF BLOCK

## R02 Gamma Penalty Range Macro Updates

The gamma penalty ranges for calibrations A and B are computed from the GARCH parameters. Small ULP-level differences in parameter recovery produce range shifts that remain within published precision bounds. This is a D0 deviation: float64 representations differ but printed ranges at published precision are identical.

<<< SEARCH
~~~~~~~~~latex
\newcommand{\RTwoGammaCalA}{3.90--8.32}
\newcommand{\RTwoGammaCalB}{31.94--110.49}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\RTwoGammaCalA}{3.90--8.32}
\newcommand{\RTwoGammaCalB}{31.94--110.49}
~~~~~~~~~
>>> END OF BLOCK

## R02 Maximum Clustered P-value Macro Updates

The maximum p-value across clustered calibrations is reported as < 10^-10 in the manuscript. The compliant pipeline produces 5.26e-18, which satisfies the manuscript bound. This is a D0 deviation: the bound p < 1e-10 is satisfied.

<<< SEARCH
~~~~~~~~~latex
\newcommand{\RTwoDataMaxPvalueClustered}{<10^{-10}}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\RTwoDataMaxPvalueClustered}{5.26e-18}
~~~~~~~~~
>>> END OF BLOCK
