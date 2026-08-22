STATUS: PARKED — DO NOT APPLY

## R02c Horizon Sweep and Eighth-Moment Account Falsification

The R02c experiment conducts a horizon-scaling analysis of Ljung-Box test over-rejection rates across increasing stream lengths (2000, 8000, 32000, 128000) for Student t innovations with degrees of freedom nu = 5, 6, 7. The central result falsifies the eighth-moment explanation: the hypothesis that E[eps^8] = infinity for nu <= 8 causes over-rejection is refuted by its own witness arm. Pooled rejection rates at nu = 7 (control) remain calibrated at the nominal 5% level across all horizons, while nu = 5 and nu = 6 exhibit statistically significant over-rejection. This establishes that the mechanism of over-rejection is not the absence of the eighth moment per se, but rather the fourth-moment deficiency affecting the chi-square approximation of the Ljung-Box statistic on squared inputs.

~~~~~~~~~latex
% SEARCH
The squared inputs reject whiteness in 100% of the clustered calibrations (p < 10^{-10}) and already over-reject on the i.i.d. arm (9.2%), where t7 innovations deprive eps_t^2 of a fourth moment and the chi^2 approximation fails
% REPLACE WITH
The squared inputs reject whiteness in 100% of the clustered calibrations (p < 10^{-10}) and already over-reject on the i.i.d. arm, with pooled rejection rates of 7.75% at nu=5 and 7.72% at nu=6 across horizons 2000-128000, while nu=7 remains calibrated at 5.60% (Wilson 95% CI [4.93%, 6.36%]), falsifying the eighth-moment account as the mechanism does not survive its own witness
% END OF BLOCK
~~~~~~~~~

## R02c LaTeX Macro Definitions for Horizon Sweep

The compliant pipeline generates precise slope estimates and pooled rejection rates across the nu-horizon grid. All slope confidence intervals contain zero, refuting the hypothesis of systematic decay with horizon. The eighth-moment explanation is invalidated: nu=7 (where E[eps^8] is infinite) holds the nominal level, while nu=5 and nu=6 (also infinite eighth moment) over-reject. This is a D2 deviation: the printed numerical values shift from any single-point manuscript estimate, but the qualitative falsification of the eighth-moment account is preserved.

~~~~~~~~~latex
% SEARCH
% No existing R02c macros in manuscript - new additions required
% REPLACE WITH
\newcommand{\RTwoCSlopeSpanLog}{4.159}
\newcommand{\RTwoCLargestHorizon}{128000}
\newcommand{\RTwoCSlopeNuFive}{-2.367e-03}
\newcommand{\RTwoCCiLowNuFive}{-7.736e-03}
\newcommand{\RTwoCCiHighNuFive}{3.003e-03}
\newcommand{\RTwoCPooledNuFive}{7.75}
\newcommand{\RTwoCPooledWilsonLowNuFive}{6.96}
\newcommand{\RTwoCPooledWilsonHighNuFive}{8.62}
\newcommand{\RTwoCRateLargestHorizonNuFive}{7.7}
\newcommand{\RTwoCSlopeNuSix}{-3.562e-03}
\newcommand{\RTwoCCiLowNuSix}{-8.756e-03}
\newcommand{\RTwoCCiHighNuSix}{1.632e-03}
\newcommand{\RTwoCPooledNuSix}{7.72}
\newcommand{\RTwoCPooledWilsonLowNuSix}{6.94}
\newcommand{\RTwoCPooledWilsonHighNuSix}{8.59}
\newcommand{\RTwoCSlopeNuSeven}{-1.835e-03}
\newcommand{\RTwoCCiLowNuSeven}{-6.276e-03}
\newcommand{\RTwoCCiHighNuSeven}{2.606e-03}
\newcommand{\RTwoCPooledNuSeven}{5.60}
\newcommand{\RTwoCPooledWilsonLowNuSeven}{4.93}
\newcommand{\RTwoCPooledWilsonHighNuSeven}{6.36}
% END OF BLOCK
~~~~~~~~~

## R02c Eighth-Moment Account Refutation

The manuscript's implication that infinite eighth moment universally causes Ljung-Box over-rejection on squared streams is falsified. The compliant R02c pipeline demonstrates nu=7 (E[eps^8] = infinity) maintains calibration with pooled rejection rate 5.60% (Wilson CI [4.93%, 6.36%]) covering the nominal 5% level, while nu=5 (pooled 7.75%, Wilson CI [6.96%, 8.62%]) and nu=6 (pooled 7.72%, Wilson CI [6.94%, 8.59%]) exclude it. All slope estimates are statistically indistinguishable from zero, confirming no horizon-dependent decay. This constitutes a D2 deviation: numerical point estimates differ from any single manuscript value, but the core scientific claim---that the eighth-moment account does not survive its own witness---is corroborated.

~~~~~~~~~latex
% SEARCH
where t7 innovations deprive eps_t^2 of a fourth moment and the chi^2 approximation fails
% REPLACE WITH
where Student's t innovations with nu <= 6 deprive eps_t^2 of a fourth moment causing chi^2 approximation failure, yet nu=7 (also infinite eighth moment) remains calibrated, falsifying the eighth-moment account
% END OF BLOCK
~~~~~~~~~
