# R04 — Iso-FPR Race Table 3 Macro Definitions

STATUS: PARKED — DO NOT APPLY

This file contains the LaTeX macro diff blocks for Table 3 (Iso-FPR Race) between the regenerated compliant pipeline and the manuscript values from v87.

## Root Cause

The submitted campaign's Gamma grid collapsed to a single point (Gamma = 1.1053 for all four labels) due to a parameter ordering bug in `solve_beta_for_gamma`. The compliant pipeline corrects this bug, producing a genuinely spanned Gamma grid (1.1053, 11.58, 50.0, 200.0). This structural correction reveals that several qualitative claims in v87 were artefacts of the collapsed grid rather than general properties.

## LaTeX Macro Diff Blocks

### Core Protocol Parameters

~~~~~~~~~~~latex
% SEARCH
\newcommand{\RFourNullStreams}{2000}
\newcommand{\RFourBisectionIters}{15}
\newcommand{\RFourBisectionTol}{0.003}
\newcommand{\RFourTargetFpr}{5\%}
\newcommand{\RFourGammaRace}{11.58}
\newcommand{\RFourStreamLength}{5000}
\newcommand{\RFourWarmup}{500}
% REPLACE WITH
\newcommand{\RFourNullStreams}{2000}
\newcommand{\RFourBisectionIters}{15}
\newcommand{\RFourBisectionTol}{0.003}
\newcommand{\RFourTargetFpr}{5\%}
\newcommand{\RFourGammaRace}{11.58}
\newcommand{\RFourStreamLength}{5000}
\newcommand{\RFourWarmup}{500}
% END OF BLOCK
~~~~~~~~~~~

### Slowdown Range (D3 Falsification)

~~~~~~~~~~~latex
% SEARCH
\newcommand{\RFourRecalibSlowdownMin}{2}
\newcommand{\RFourRecalibSlowdownMax}{19}
% REPLACE WITH
\newcommand{\RFourRecalibSlowdownMin}{7}
\newcommand{\RFourRecalibSlowdownMax}{81}
% END OF BLOCK
~~~~~~~~~~~

### Blind Zone Parameters (Confirmed)

~~~~~~~~~~~latex
% SEARCH
\newcommand{\RFourDeadBand}{0.125}
\newcommand{\RFourKappaZ}{3.231}
\newcommand{\RFourBlindZoneCStar}{0.43}
% REPLACE WITH
\newcommand{\RFourDeadBand}{0.125}
\newcommand{\RFourKappaZ}{3.231}
\newcommand{\RFourBlindZoneCStar}{0.43}
% END OF BLOCK
~~~~~~~~~~~

### Parametric Gain (D2 Deviation)

~~~~~~~~~~~latex
% SEARCH
\newcommand{\RFourParametricGainAtCOne}{1.66$\times$}
% REPLACE WITH
\newcommand{\RFourParametricGainAtCOne}{1.38$\times$}
% END OF BLOCK
~~~~~~~~~~~

### Crossing Points

~~~~~~~~~~~latex
% SEARCH
\newcommand{\RFourNuStarMeasured}{4.9}
\newcommand{\RFourNuStarLower}{4.0}
\newcommand{\RFourNuStarUpper}{5.0}
\newcommand{\RFourNuStarOracle}{4.6}
\newcommand{\RFourNuStarOracleLower}{4.0}
\newcommand{\RFourNuStarOracleUpper}{5.0}
\newcommand{\RFourNuStarAnalytic}{4.7}
% REPLACE WITH
\newcommand{\RFourNuStarMeasured}{8.5}
\newcommand{\RFourNuStarLower}{7.0}
\newcommand{\RFourNuStarUpper}{30.0}
\newcommand{\RFourNuStarOracle}{4.5}
\newcommand{\RFourNuStarOracleLower}{4.0}
\newcommand{\RFourNuStarOracleUpper}{4.5}
\newcommand{\RFourNuStarAnalytic}{4.7}
% END OF BLOCK
~~~~~~~~~~~

### Estimation Cost (D3 Falsification)

~~~~~~~~~~~latex
% SEARCH
\newcommand{\RFourEstimationCostDof}{0.3}
% REPLACE WITH
\newcommand{\RFourEstimationCostDof}{4.1}
% END OF BLOCK
~~~~~~~~~~~

### Concept Threshold Band (D2 Deviation)

~~~~~~~~~~~latex
% SEARCH
\newcommand{\RFourConceptLambdaMin}{10.6}
\newcommand{\RFourConceptLambdaMax}{10.7}
% REPLACE WITH
\newcommand{\RFourConceptLambdaMin}{10.5}
\newcommand{\RFourConceptLambdaMax}{10.7}
% END OF BLOCK
~~~~~~~~~~~

### Ceiling and Max Ratio (Confirmed)

~~~~~~~~~~~latex
% SEARCH
\newcommand{\RFourGaussianCeiling}{1.57}
\newcommand{\RFourRatioMax}{1.20}
% REPLACE WITH
\newcommand{\RFourGaussianCeiling}{1.57}
\newcommand{\RFourRatioMax}{1.20}
% END OF BLOCK
~~~~~~~~~~~

### Family Control FPRs (D3 Falsification)

~~~~~~~~~~~latex
% SEARCH
\newcommand{\RFourFamilyCusumFpr}{5\%}
\newcommand{\RFourFamilyAdwinFpr}{5\%}
% REPLACE WITH
\newcommand{\RFourFamilyCusumFpr}{36.1\%}
\newcommand{\RFourFamilyAdwinFpr}{10.7\%}
% END OF BLOCK
~~~~~~~~~~~

### Constant Threshold Control (D2 Deviation)

~~~~~~~~~~~latex
% SEARCH
\newcommand{\RFourConstantThresholdFpr}{5\%}
\newcommand{\RFourBernoulliFpr}{5\%}
% REPLACE WITH
\newcommand{\RFourConstantThresholdFpr}{7.7\%}
\newcommand{\RFourBernoulliFpr}{7.9\%}
% END OF BLOCK
~~~~~~~~~~~

### ADWIN Attainable FPR

~~~~~~~~~~~latex
% SEARCH
% (Not present in manuscript)
% REPLACE WITH
\newcommand{\RFourAdwinAttainableFpr}{0.7\%}
% END OF BLOCK
~~~~~~~~~~~
