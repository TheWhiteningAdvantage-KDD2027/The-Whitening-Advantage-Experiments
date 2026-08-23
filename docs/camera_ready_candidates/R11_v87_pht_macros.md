# Camera-Ready Candidate: R11_v87_pht_macros.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** NO DEVIATION — clarification only

STATUS: PARKED — DO NOT APPLY

## R11 PHT Calibration and Plateau Macro Updates

PHT detector calibration thresholds and plateau values differ due to entropy re-keying. All are classified as D2 deviations except the ADWIN peak-to-peak spread which is D1.

~~~~~~~~~latex
% SEARCH
\newcommand{\RElevenPhtLambdaData}{39.01}
\newcommand{\RElevenPhtLambdaConcept}{10.34}
% REPLACE WITH
\newcommand{\RElevenPhtLambdaData}{41.45}
\newcommand{\RElevenPhtLambdaConcept}{10.32}
% END OF BLOCK
~~~~~~~~~

## R11 PHT Plateau and Syncope Macro Updates

The PHT sqrt(Gamma) scaling plateau and syncope Gamma (where detection rate drops below 50%) both shift and are classified as D2.

~~~~~~~~~latex
% SEARCH
\newcommand{\RElevenPhtPlateauSqrt}{30\%}
\newcommand{\RElevenPhtSyncopeGamma}{75}
% REPLACE WITH
\newcommand{\RElevenPhtPlateauSqrt}{28.2\%}
\newcommand{\RElevenPhtSyncopeGamma}{91}
% END OF BLOCK
~~~~~~~~~

## R11 PHT Raw and Gamma-Rule Macro Updates

PHT false positive rates under raw and Gamma-rule scaling differ and are classified as D2.

~~~~~~~~~latex
% SEARCH
\newcommand{\RElevenPhtRawMean}{85\%}
\newcommand{\RElevenPhtGammaRuleLow}{15\%}
\newcommand{\RElevenPhtGammaRuleHigh}{2\%}
% REPLACE WITH
\newcommand{\RElevenPhtRawMean}{84.1\%}
\newcommand{\RElevenPhtGammaRuleLow}{14.46\%}
\newcommand{\RElevenPhtGammaRuleHigh}{2.10\%}
% END OF BLOCK
~~~~~~~~~
