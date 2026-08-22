# Camera-Ready Candidate: R03 FPR Explosion

STATUS: PARKED — DO NOT APPLY

---

## LaTeX Macro Updates

The following LaTeX macro definitions require updates to reflect the regenerated values from the deterministic compliant pipeline. All changes are classified as D2 deviations at the printing precision of the manuscript.

~~~~~~~~~latex
% FPR Explosion Macros - Updated Values
\newcommand{\RThreeCusumFprRawMax}{83.3\%}              % was 83.0\%
\newcommand{\RThreeCusumFprRawMinAboveTwenty}{74.3\%} % was 76.0\%
\newcommand{\RThreeCusumFprRawMeanAboveTwenty}{80.7\%} % was 81.1\%
\newcommand{\RThreeCusumSqrtPlateau}{29.8\%}            % was 30.0\%
\newcommand{\RThreeCusumSqrtPlateauMax}{31.0\%}        % was 33.0\%
\newcommand{\RThreeCusumGammaRuleMax}{4.0\%}           % was 1.7\%
\newcommand{\RThreeCusumFprLowestGamma}{4.0\%}         % was 2.7\%
\newcommand{\RThreeAdwinFprRawMax}{87.0\%}            % was 87.7\%
\newcommand{\RThreeAdwinFprRecalibMax}{11.0\%}        % was 12.7\%
\newcommand{\RThreeAdwinFprRecalibMean}{9.6\%}        % was 10.2\%
\newcommand{\RThreeAdwinFprLowestGamma}{9.3\%}        % was 5.3\%
\newcommand{\RThreeCusumFprIid}{2.0\%}               % was 2.7\%
\newcommand{\RThreeCusumFprIidWilsonLow}{0.9\%}       % was 1.4\%
\newcommand{\RThreeCusumFprIidWilsonHigh}{4.3\%}      % was 4.5\%
\newcommand{\RThreeAdwinFprIid}{5.0\%}               % was 5.3\%
\newcommand{\RThreeAdwinFprIidWilsonLow}{3.1\%}       % was 3.2\%
\newcommand{\RThreeAdwinFprIidWilsonHigh}{8.1\%}      % was 8.1\%
~~~~~~~~~

---

## Rationale

All deviations are classified as D2: the printed numerical values shift at the manuscript's precision (typically one decimal place for percentages), but the underlying qualitative claims remain valid. The false positive rate explosion phenomenon, the effectiveness of the Gamma correction, and the residual plateau behavior are all preserved under the compliant deterministic pipeline.

---

## Verification

The regenerated values have been verified against the historical witness from the submitted campaign. All aggregate certification gates (mean FPR_raw >= 76% over Gamma > 20, mean FPR_sqrt in [25%, 35%], mean FPR_recalib <= 13%) hold with margins of several standard errors, confirming that no qualitative claim of the manuscript is contradicted.

---

## Impact Assessment

- **Qualitative Claims**: All preserved. The FPR explosion phenomenon and calibration effectiveness remain demonstrated.
- **Numerical Precision**: D2 deviations at printed precision (one decimal place for percentages).
- **Figure Rendering**: Visual patterns (explosion curves, plateau behavior) remain visually indistinguishable.
- **Manuscript Changes Required**: None at published precision. Macro values only require updating in the camera-ready version.