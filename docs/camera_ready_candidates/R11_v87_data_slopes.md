# Camera-Ready Candidate: R11_v87_data_slopes.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** `R11-regenerated`

STATUS: PARKED — DO NOT APPLY

## R11 Data Log-Log Slope Macro Updates

Data pipeline log-log regression slopes on ADD vs Gamma differ from manuscript values due to entropy re-keying. All slopes are classified as D2 deviations: the printed values shift at two decimal places, but the qualitative claim of near-linear scaling is preserved.

<<< SEARCH
~~~~~~~~~latex
\newcommand{\RElevenDataSlopeCusum}{0.86}
\newcommand{\RElevenDataSlopePht}{1.09}
\newcommand{\RElevenDataSlopeAdwin}{0.47}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\RElevenDataSlopeCusum}{0.88}
\newcommand{\RElevenDataSlopePht}{1.10}
\newcommand{\RElevenDataSlopeAdwin}{0.48}
~~~~~~~~~
>>> END OF BLOCK

## R11 Data Slope Extended Domain Macro Updates

Extended domain slopes (excluding low Gamma point) also differ and are classified as D2.

<<< SEARCH
~~~~~~~~~latex
\newcommand{\RElevenDataSlopeCusumExLowGamma}{0.74}
\newcommand{\RElevenDataSlopePhtExLowGamma}{1.01}
\newcommand{\RElevenDataSlopeAdwinExLowGamma}{0.42}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\RElevenDataSlopeCusumExLowGamma}{0.74}
\newcommand{\RElevenDataSlopePhtExLowGamma}{1.01}
\newcommand{\RElevenDataSlopeAdwinExLowGamma}{0.42}
~~~~~~~~~
>>> END OF BLOCK
