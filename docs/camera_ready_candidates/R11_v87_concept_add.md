# Camera-Ready Candidate: R11_v87_concept_add.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** `R11-regenerated`

STATUS: PARKED — DO NOT APPLY

## R11 Concept ADD Macro Updates

The compliant deterministic pipeline produces Concept ADD values that differ from manuscript values due to the re-keyed entropy (prompt S2.1). All Concept ADD values are classified as D1 or D2 deviations: the printed numerical values shift at published precision, but qualitative ordering (PHT < CUSUM < ADWIN < DDM) is preserved. No qualitative claims are falsified.

<<< SEARCH
~~~~~~~~~latex
\newcommand{\RElevenConceptAddCusum}{28.3}
\newcommand{\RElevenConceptAddPht}{27.1}
\newcommand{\RElevenConceptAddAdwin}{61.0}
\newcommand{\RElevenConceptAddDdm}{250.0}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\RElevenConceptAddCusum}{28.4}
\newcommand{\RElevenConceptAddPht}{27.1}
\newcommand{\RElevenConceptAddAdwin}{61.2}
\newcommand{\RElevenConceptAddDdm}{250.0}
~~~~~~~~~
>>> END OF BLOCK

## R11 Concept ADD Spread Macro Updates

Peak-to-peak ADD spread values differ due to the same entropy re-keying. Cumulative detectors (CUSUM, PHT) show D2 deviations, while window-mean ADWIN shows D1.

<<< SEARCH
~~~~~~~~~latex
\newcommand{\RElevenConceptSpreadCusum}{0.032}
\newcommand{\RElevenConceptSpreadPht}{0.0082}
\newcommand{\RElevenConceptSpreadAdwin}{0.13}
\newcommand{\RElevenConceptSpreadDdm}{0.0422}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\RElevenConceptSpreadCusum}{1.13\%}
\newcommand{\RElevenConceptSpreadPht}{0.82\%}
\newcommand{\RElevenConceptSpreadAdwin}{13.16\%}
\newcommand{\RElevenConceptSpreadDdm}{4.22\%}
~~~~~~~~~
>>> END OF BLOCK
