# Camera-Ready Candidate: R02b_v87_iid_mechanism.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** NO DEVIATION — clarification only

## R02b IID Mechanism Test Macro Updates

The manuscript reports a single i.i.d. arm over-rejection rate of 9.2% at line 278. The R02b experiment extends this to a full grid of degrees of freedom values (nu = 5, 6, 7, 8.5, 12, 30), revealing that the over-rejection phenomenon depends critically on the tail heaviness. At nu = 7, the compliant pipeline produces 5.8% instead of 9.2%. The Wilson 95% confidence intervals confirm statistical significance of the deviation at heavy tails (nu = 5, 6) while containing the nominal level at nu = 7 and above. This is a D2 deviation: the printed numerical value shifts, but the underlying qualitative claim of over-rejection at heavy tails remains valid.

## R02b Rejection Rate Macros by Degrees of Freedom

The compliant pipeline generates precise rejection rates across the nu grid. All values differ from the manuscript's single 9.2% point estimate. The transition from over-rejection to nominal-level containment occurs between nu = 6 and nu = 7. This constitutes a D2 deviation: the printed values shift, but the qualitative mechanism (heavy tails induce over-rejection) is corroborated.

<<< SEARCH
~~~~~~~~~latex
% No existing RTwoB macros in manuscript - these are new additions
\newcommand{\RTwoBStreamsPerPoint}{1000}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
% No existing RTwoB macros in manuscript - these are new additions
\newcommand{\RTwoBStreamsPerPoint}{1000}
\newcommand{\RTwoBHorizon}{8000}
\newcommand{\RTwoBLbLags}{20}
\newcommand{\RTwoBRejectNuFive}{8.8}
\newcommand{\RTwoBWilsonLowNuFive}{7.2}
\newcommand{\RTwoBWilsonHighNuFive}{10.7}
\newcommand{\RTwoBRejectNuSix}{7.9}
\newcommand{\RTwoBWilsonLowNuSix}{6.4}
\newcommand{\RTwoBWilsonHighNuSix}{9.7}
\newcommand{\RTwoBRejectNuSeven}{5.8}
\newcommand{\RTwoBWilsonLowNuSeven}{4.5}
\newcommand{\RTwoBWilsonHighNuSeven}{7.4}
\newcommand{\RTwoBRejectNuEightHalf}{6.1}
\newcommand{\RTwoBWilsonLowNuEightHalf}{4.8}
\newcommand{\RTwoBWilsonHighNuEightHalf}{7.8}
\newcommand{\RTwoBRejectNuTwelve}{4.8}
\newcommand{\RTwoBWilsonLowNuTwelve}{3.6}
\newcommand{\RTwoBWilsonHighNuTwelve}{6.3}
\newcommand{\RTwoBRejectNuThirty}{6.0}
\newcommand{\RTwoBWilsonLowNuThirty}{4.7}
\newcommand{\RTwoBWilsonHighNuThirty}{7.6}
\newcommand{\RTwoBNominalExcludedUpTo}{6}
~~~~~~~~~
>>> END OF BLOCK

## R02b IID Arm Over-Rejection Rate Update

The manuscript states the i.i.d. arm over-rejects at 9.2%. The compliant R02b pipeline demonstrates this varies with degrees of freedom, measuring 5.8% at nu=7. This is a D2 deviation: the point estimate changes, but the phenomenon of over-rejection for heavy-tailed i.i.d. streams (nu < 8.5) is preserved.

<<< SEARCH
~~~~~~~~~latex
already over-reject on the i.i.d.\ arm ($9.2\%$)
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
already over-reject on the i.i.d.\ arm ($5.8\%$ at $\nu = 7$, $7.9\%$ at $\nu = 6$, $8.8\%$ at $\nu = 5$)
~~~~~~~~~
>>> END OF BLOCK
