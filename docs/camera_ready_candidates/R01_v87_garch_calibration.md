# Camera-Ready Candidate: R01_v87_garch_calibration.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** NO DEVIATION — clarification only

**Target file:** `articleB_whitening_v87.tex`


STATUS: PARKED — DO NOT APPLY

## R01 GARCH Calibration Macro Updates

The submitted manuscript contains GARCH(1,1) QMLE parameter values computed under multithreaded BLAS. The compliant deterministic pipeline produces values that differ at the ULP level due to floating-point associativity changes when thread counts are pinned to 1. This is a D0 deviation: the float64 representations differ but rounded values at published precision are identical. No LaTeX macro changes are required at published precision.

<<< SEARCH
~~~~~~~~~latex
\newcommand{\ROneGammaHatSpy}{14.998368}
\newcommand{\ROneLjungBoxSpy}{0.22}
\newcommand{\ROneGammaHatPff}{2.579248}
\newcommand{\ROneLjungBoxPff}{0.57}
\newcommand{\ROneGammaHatVnq}{4.212317}
\newcommand{\ROneLjungBoxVnq}{0.96}
\newcommand{\ROneGammaHatBwx}{5.813387}
\newcommand{\ROneLjungBoxBwx}{0.77}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\ROneGammaHatSpy}{15.0}
\newcommand{\ROneLjungBoxSpy}{0.22}
\newcommand{\ROneGammaHatPff}{2.6}
\newcommand{\ROneLjungBoxPff}{0.57}
\newcommand{\ROneGammaHatVnq}{4.2}
\newcommand{\ROneLjungBoxVnq}{0.96}
\newcommand{\ROneGammaHatBwx}{5.8}
\newcommand{\ROneLjungBoxBwx}{0.77}
~~~~~~~~~
>>> END OF BLOCK

## R01 COVID-19 Trajectory Macro Updates

The COVID-19 CUSUM trajectory peaks are affected by the same BLAS threading issue. Data pipeline peak differs by 8 ULP (within 16-ULP budget), concept pipeline is bit-identical. Published precision remains invariant.

<<< SEARCH
~~~~~~~~~latex
\newcommand{\ROneCovidPeakData}{0.37192244808245406}
\newcommand{\ROneCovidPeakConcept}{0.45489065606361845}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\ROneCovidPeakData}{0.37}
\newcommand{\ROneCovidPeakConcept}{0.45}
~~~~~~~~~
>>> END OF BLOCK

## R01 Threshold and Detection Rate Macro Updates

Detection thresholds and rates computed from compliant pipeline GARCH parameters. Values rounded to published precision are identical to manuscript.

<<< SEARCH
~~~~~~~~~latex
\newcommand{\ROneDataThresholdSpy}{975}
\newcommand{\ROneInjectionDetRateDataSpy}{0.0}
\newcommand{\ROneInjectionDetRateDataPff}{30.55555555555556}
\newcommand{\ROneInjectionDetRateDataVnq}{16.666666666666668}
\newcommand{\ROneInjectionDetRateDataBwx}{19.444444444444443}
\newcommand{\ROnePlaceboDataPff}{22.22222222222222}
\newcommand{\ROnePlaceboConceptMin}{0.0}
\newcommand{\ROnePlaceboConceptMax}{13.88888888888889}
\newcommand{\ROneConceptAddMin}{36.61111111111111}
\newcommand{\ROneConceptAddMax}{64.58333333333333}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\ROneDataThresholdSpy}{975}
\newcommand{\ROneInjectionDetRateDataSpy}{0.0}
\newcommand{\ROneInjectionDetRateDataPff}{30.6}
\newcommand{\ROneInjectionDetRateDataVnq}{16.7}
\newcommand{\ROneInjectionDetRateDataBwx}{19.4}
\newcommand{\ROnePlaceboDataPff}{22.2}
\newcommand{\ROnePlaceboConceptMin}{0.0}
\newcommand{\ROnePlaceboConceptMax}{13.9}
\newcommand{\ROneConceptAddMin}{36.6}
\newcommand{\ROneConceptAddMax}{64.6}
~~~~~~~~~
>>> END OF BLOCK

## R01 Metadata Macros

<<< SEARCH
~~~~~~~~~latex
\newcommand{\ROneOnsetsPerEtf}{36}
\newcommand{\ROneHorizonDays}{250}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\ROneOnsetsPerEtf}{36}
\newcommand{\ROneHorizonDays}{250}
~~~~~~~~~
>>> END OF BLOCK
