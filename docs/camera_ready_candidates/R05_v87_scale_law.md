# Camera-Ready Candidate: R05_v87_scale_law.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** `R05-campaign-redraw`

**Target file:** `articleB_whitening_v87.tex`


STATUS: PARKED — DO NOT APPLY

# R05 Scale Law Camera-Ready Candidates

This document contains LaTeX macro diff blocks for the R05 scale law stream, comparing published v87 values against the regenerated deterministic compliant pipeline.

## Abrupt Campaign: ADD vs Gamma Linear Fit

The abrupt shift campaign measures detection delay inflation as a function of the GARCH penalty Gamma. Proposition prop:add_garch states ADD ~ 23.7 Gamma + 38.

<<< SEARCH
~~~~~~~~~latex
% Abrupt slope (Proposition prop:add_garch)
\newcommand{\RFiveAbruptSlope}{23.7}

% Abrupt intercept (Proposition prop:add_garch)
\newcommand{\RFiveAbruptIntercept}{38}

% Abrupt R-squared
\newcommand{\RFiveAbruptRSquared}{0.9887}

% Maximum relative residual
\newcommand{\RFiveAbruptMaxRelResidual}{52%}

% Slope excluding Gamma = 1
\newcommand{\RFiveAbruptSlopeExGammaOne}{24.8}

% Intercept excluding Gamma = 1
\newcommand{\RFiveAbruptInterceptExGammaOne}{42}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
% Abrupt slope (Proposition prop:add_garch)
\newcommand{\RFiveAbruptSlope}{26.0}

% Abrupt intercept (Proposition prop:add_garch)
\newcommand{\RFiveAbruptIntercept}{32}

% Abrupt R-squared
\newcommand{\RFiveAbruptRSquared}{0.9913}

% Maximum relative residual
\newcommand{\RFiveAbruptMaxRelResidual}{55%}

% Slope excluding Gamma = 1
\newcommand{\RFiveAbruptSlopeExGammaOne}{25.7}

% Intercept excluding Gamma = 1
\newcommand{\RFiveAbruptInterceptExGammaOne}{38}
~~~~~~~~~
>>> END OF BLOCK

## Sqrt Rule False Positive Rate

The sqrt rule FPR percentage (maximum across Gamma grid).

<<< SEARCH
~~~~~~~~~latex
% Sqrt rule FPR percentage
\newcommand{\RFiveSqrtRuleFpr}{31%}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
% Sqrt rule FPR percentage
\newcommand{\RFiveSqrtRuleFpr}{24%}
~~~~~~~~~
>>> END OF BLOCK

## Ramp Campaign 2e5: Scaling Law Fit

The ramp campaign at H = 200,000 measures the scaling law of Eq. (5).

<<< SEARCH
~~~~~~~~~latex
% Scaling median error percentage
\newcommand{\RFiveScalingMedianError}{5.4%}

% Recalibration margin min at 2e5
\newcommand{\RFiveRecalibMarginMinTwoEFive}{7%}

% Recalibration margin max at 2e5
\newcommand{\RFiveRecalibMarginMaxTwoEFive}{29%}

% lambda_iid at 2e5
\newcommand{\RFiveLambdaIidTwoEFive}{129.5}

% Grid reach at 2e5
\newcommand{\RFiveGridReachTwoEFive}{22.5}

% Censoring max at 2e5
\newcommand{\RFiveCensoringMaxTwoEFive}{1.3%}

% Detection min at 2e5
\newcommand{\RFiveDetectionMinTwoEFive}{98.7%}

% Lambda over Gamma min at 2e5
\newcommand{\RFiveLambdaOverGammaMinTwoEFive}{138}

% Lambda over Gamma max at 2e5
\newcommand{\RFiveLambdaOverGammaMaxTwoEFive}{167}

% SD over ADD max at 2e5
\newcommand{\RFiveSdOverAddMaxTwoEFive}{3.2}

% Median over ADD min at 2e5
\newcommand{\RFiveMedOverAddMinTwoEFive}{0.68}

% Rho w share at 2e5
\newcommand{\RFiveRhoWShareTwoEFive}{58%}

% Exponent min at 2e5
\newcommand{\RFiveExponentMinTwoEFive}{0.65}

% Exponent max at 2e5
\newcommand{\RFiveExponentMaxTwoEFive}{0.71}

% Model exponent min at 2e5
\newcommand{\RFiveModelExponentMinTwoEFive}{0.71}

% Model exponent max at 2e5
\newcommand{\RFiveModelExponentMaxTwoEFive}{0.73}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
% Scaling median error percentage
\newcommand{\RFiveScalingMedianError}{5.3%}

% Recalibration margin min at 2e5
\newcommand{\RFiveRecalibMarginMinTwoEFive}{-1%}

% Recalibration margin max at 2e5
\newcommand{\RFiveRecalibMarginMaxTwoEFive}{39%}

% lambda_iid at 2e5
\newcommand{\RFiveLambdaIidTwoEFive}{128.6}

% Grid reach at 2e5
\newcommand{\RFiveGridReachTwoEFive}{22.5}

% Censoring max at 2e5
\newcommand{\RFiveCensoringMaxPctTwoEFive}{0.25%}

% Detection min at 2e5
\newcommand{\RFiveDetectionMinPctTwoEFive}{99.75%}

% Lambda over Gamma min at 2e5
\newcommand{\RFiveLambdaOverGammaMinTwoEFive}{126.8}

% Lambda over Gamma max at 2e5
\newcommand{\RFiveLambdaOverGammaMaxTwoEFive}{179.2}

% SD over ADD max at 2e5
\newcommand{\RFiveSdOverAddMaxTwoEFive}{0.94}

% Median over ADD min at 2e5
\newcommand{\RFiveMedOverAddMinTwoEFive}{0.76}

% Rho w share at 2e5
\newcommand{\RFiveRhoWSharePctTwoEFive}{57.3%}

% Exponent min at 2e5
\newcommand{\RFiveExponentMinTwoEFive}{0.68}

% Exponent max at 2e5
\newcommand{\RFiveExponentMaxTwoEFive}{0.70}

% Model exponent min at 2e5
\newcommand{\RFiveModelExponentMinTwoEFive}{0.71}

% Model exponent max at 2e5
\newcommand{\RFiveModelExponentMaxTwoEFive}{0.72}
~~~~~~~~~
>>> END OF BLOCK

## Ramp Campaign 3e6: Degradation with Horizon

The ramp campaign at H = 3,000,000 demonstrates degradation of the recalibration rule with monitoring horizon.

<<< SEARCH
~~~~~~~~~latex
% lambda_iid at 3e6
\newcommand{\RFiveLambdaIidThreeESix}{303}

% Grid reach at 3e6
\newcommand{\RFiveGridReachThreeESix}{225}

% Low Gamma max error at 3e6
\newcommand{\RFiveLowGammaMaxErrorThreeESix}{5.7%}

% Rho w share at 3e6
\newcommand{\RFiveRhoWShareThreeESix}{78%}

% Recalibration margin max at 3e6
\newcommand{\RFiveRecalibMarginMaxThreeESix}{96%}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
% lambda_iid at 3e6
\newcommand{\RFiveLambdaIidThreeESix}{282.5}

% Grid reach at 3e6
\newcommand{\RFiveGridReachThreeESix}{225.0}

% Low Gamma max error at 3e6
\newcommand{\RFiveLowGammaMaxErrorPctThreeESix}{5.8%}

% Rho w share at 3e6
\newcommand{\RFiveRhoWSharePctThreeESix}{78.1%}

% Recalibration margin max at 3e6
\newcommand{\RFiveRecalibMarginMaxThreeESix}{96.4%}
~~~~~~~~~
>>> END OF BLOCK

## Moment Boundaries

Closed-form moment boundaries independent of Monte Carlo sampling.

<<< SEARCH
~~~~~~~~~latex
% Sixth moment Gamma boundary
\newcommand{\RFiveSixthMomentGamma}{7.1}

% Fourth moment Gamma boundary
\newcommand{\RFiveFourthMomentGamma}{41.6}

% Moment margin at Gamma max
\newcommand{\RFiveMomentMarginAtGammaMax}{0.8}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
% Sixth moment Gamma boundary
\newcommand{\RFiveSixthMomentGamma}{7.1}

% Fourth moment Gamma boundary
\newcommand{\RFiveFourthMomentGamma}{41.6}

% Moment margin at Gamma max
\newcommand{\RFiveMomentMarginAtGammaMax}{0.8}
~~~~~~~~~
>>> END OF BLOCK

## Lambda iid Ladder

The lambda_iid horizon ladder for the crossover analysis.

<<< SEARCH
~~~~~~~~~latex
% Lambda iid ladder exponent
\newcommand{\RFiveLambdaIidLadderExponent}{0.25}

% Lambda iid at H = 77000
\newcommand{\RFiveLambdaIidAtH77000}{102.8}

% Lambda iid at H = 200000
\newcommand{\RFiveLambdaIidAtH200000}{128.6}

% Lambda iid at H = 3000000
\newcommand{\RFiveLambdaIidAtH3000000}{282.5}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
% Lambda iid ladder exponent
\newcommand{\RFiveLambdaIidLadderExponent}{0.26}

% Lambda iid at H = 77000
\newcommand{\RFiveLambdaIidAtH77000}{111.0}

% Lambda iid at H = 200000
\newcommand{\RFiveLambdaIidAtH200000}{128.6}

% Lambda iid at H = 3000000
\newcommand{\RFiveLambdaIidAtH3000000}{282.5}
~~~~~~~~~
>>> END OF BLOCK

## Concept Arm Metrics

Concept arm threshold and detection rates across campaigns.

<<< SEARCH
~~~~~~~~~latex
% Concept detection rate (abrupt)
\newcommand{\RFiveConceptDetRate}{0.095}

% Concept FPR (abrupt)
\newcommand{\RFiveConceptFpr}{0.095}

% Concept positive detection rate
\newcommand{\RFiveConceptPositiveDetRate}{0.97}

% Concept positive shift
\newcommand{\RFiveConceptPositiveShift}{0.8}

% Lambda C abrupt
\newcommand{\RFiveLambdaCAbrupt}{10.8}

% Lambda C ramp 2e5
\newcommand{\RFiveLambdaCRampTwoEFive}{15.81}

% Lambda C ramp 3e6
\newcommand{\RFiveLambdaCRampThreeESix}{19.02}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
% Concept detection rate (abrupt)
\newcommand{\RFiveConceptDetRate}{0.0550}

% Concept FPR (abrupt)
\newcommand{\RFiveConceptFpr}{0.0550}

% Concept positive detection rate
\newcommand{\RFiveConceptPositiveDetRate}{1.0000}

% Concept positive shift
\newcommand{\RFiveConceptPositiveShift}{1.00}

% Lambda C abrupt
\newcommand{\RFiveLambdaCAbrupt}{11.40}

% Lambda C ramp 2e5
\newcommand{\RFiveLambdaCRampTwoEFive}{16.00}

% Lambda C ramp 3e6
\newcommand{\RFiveLambdaCRampThreeESix}{18.80}
~~~~~~~~~
>>> END OF BLOCK
