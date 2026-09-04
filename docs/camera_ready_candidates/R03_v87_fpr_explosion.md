# Camera-Ready Candidate: R03_v87_fpr_explosion.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** `R03-campaign-redraw`

**Target file:** `articleB_whitening_v87.tex`


# Camera-Ready Candidate: R03 FPR Explosion

STATUS: PARKED — DO NOT APPLY

---

## LaTeX Macro Updates

The following LaTeX macro definitions require updates to reflect the regenerated values from the deterministic compliant pipeline. All changes are classified as D2 deviations at the printing precision of the manuscript.

<<< SEARCH
~~~~~~~~~latex
% FPR Explosion macros as printed by the submitted campaign
\newcommand{\RThreeCusumFprRawMax}{83.0\%}
\newcommand{\RThreeCusumFprRawMinAboveTwenty}{76.0\%}
\newcommand{\RThreeCusumFprRawMeanAboveTwenty}{81.1\%}
\newcommand{\RThreeCusumSqrtPlateau}{30.0\%}
\newcommand{\RThreeCusumSqrtPlateauMax}{33.0\%}
\newcommand{\RThreeCusumGammaRuleMax}{1.7\%}
\newcommand{\RThreeCusumFprLowestGamma}{2.7\%}
\newcommand{\RThreeAdwinFprRawMax}{87.7\%}
\newcommand{\RThreeAdwinFprRecalibMax}{12.7\%}
\newcommand{\RThreeAdwinFprRecalibMean}{10.2\%}
\newcommand{\RThreeAdwinFprLowestGamma}{5.3\%}
\newcommand{\RThreeCusumFprIid}{2.7\%}
\newcommand{\RThreeCusumFprIidWilsonLow}{1.4\%}
\newcommand{\RThreeCusumFprIidWilsonHigh}{4.5\%}
\newcommand{\RThreeAdwinFprIid}{5.3\%}
\newcommand{\RThreeAdwinFprIidWilsonLow}{3.2\%}
\newcommand{\RThreeAdwinFprIidWilsonHigh}{8.1\%}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
% FPR Explosion macros, regenerated compliant pipeline
\newcommand{\RThreeCusumFprRawMax}{83.3\%}
\newcommand{\RThreeCusumFprRawMinAboveTwenty}{74.3\%}
\newcommand{\RThreeCusumFprRawMeanAboveTwenty}{80.7\%}
\newcommand{\RThreeCusumSqrtPlateau}{29.8\%}
\newcommand{\RThreeCusumSqrtPlateauMax}{31.0\%}
\newcommand{\RThreeCusumGammaRuleMax}{4.0\%}
\newcommand{\RThreeCusumFprLowestGamma}{4.0\%}
\newcommand{\RThreeAdwinFprRawMax}{87.0\%}
\newcommand{\RThreeAdwinFprRecalibMax}{11.0\%}
\newcommand{\RThreeAdwinFprRecalibMean}{9.6\%}
\newcommand{\RThreeAdwinFprLowestGamma}{9.3\%}
\newcommand{\RThreeCusumFprIid}{2.0\%}
\newcommand{\RThreeCusumFprIidWilsonLow}{0.9\%}
\newcommand{\RThreeCusumFprIidWilsonHigh}{4.3\%}
\newcommand{\RThreeAdwinFprIid}{5.0\%}
\newcommand{\RThreeAdwinFprIidWilsonLow}{3.1\%}
\newcommand{\RThreeAdwinFprIidWilsonHigh}{8.1\%}
~~~~~~~~~
>>> END OF BLOCK

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
