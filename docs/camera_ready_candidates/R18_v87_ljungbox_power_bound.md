# Camera-Ready Candidate: R18_v87_ljungbox_power_bound.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** NO DEVIATION — clarification only

**Target file:** `articleB_whitening_v87.tex`


STATUS: PARKED — DO NOT APPLY

## R18 Ljung-Box Power Bound on Binary Streams

R18 reproduces no figure, table or number of articleB_whitening_v87.tex. It establishes a bound on what the manuscript's Ljung-Box non-rejections exclude at four sites: L278, L290, the Figure 6 caption at L286, and L318.

The experiment converts non-rejection statements into probability bounds: the instrument attains 80% power against a lag-1 autocorrelation of \REighteenRhoEightyAnalytic at n = 8000, lag 20, level 0.05. A non-rejection therefore excludes an autocorrelation above that amplitude with probability 0.8.

<<< SEARCH
~~~~~~~~~latex
% v87 defines no \REighteen macro: R18 reproduces no figure, table or number of the
% manuscript, so this block is an addition and replaces nothing.
\newcommand{\REighteenLags}{20}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
% R18 power of the Ljung-Box test on a binary stream (bound, not a v87 reproduction)
\newcommand{\REighteenThetaEighty}{0.0253}
\newcommand{\REighteenRhoEighty}{0.0506}
\newcommand{\REighteenThetaEightyAnalytic}{0.0256}
\newcommand{\REighteenRhoEightyAnalytic}{0.0511}
\newcommand{\REighteenRhoEightyCiLow}{0.0494}
\newcommand{\REighteenRhoEightyCiHigh}{0.0518}
\newcommand{\REighteenPowerAtRhoOneTenth}{1.000}
\newcommand{\REighteenPowerAtRhoOneTenthShortHorizon}{0.782}
\newcommand{\REighteenSizeAtNull}{4.5\%}
\newcommand{\REighteenSizeAtNullKsPvalue}{0.214}
\newcommand{\REighteenMaxDeviationAnalytic}{0.0421}
\newcommand{\REighteenPowerAtMeasuredRho}{0.050}
\newcommand{\REighteenMeasuredRhoClassifier}{0.0008}
\newcommand{\REighteenMeasuredRhoSign}{0.0007}
\newcommand{\REighteenPowerAtMeasuredRhoSign}{0.050}
\newcommand{\REighteenStreamsPerPoint}{1000}
\newcommand{\REighteenAmplitudeGridPoints}{36}
\newcommand{\REighteenLags}{20}
\newcommand{\REighteenDesignEffect}{1.96}
\newcommand{\REighteenRhoEightyTwoThousand}{0.1023}
\newcommand{\REighteenRhoEightyEightThousand}{0.0506}
\newcommand{\REighteenRhoEightyThirtyTwoThousand}{0.0265}
\newcommand{\REighteenRhoEightyOneTwentyEightThousand}{0.0127}
~~~~~~~~~
>>> END OF BLOCK

Measured lag-1 autocorrelations on the streams the manuscript's non-rejections were taken from:
- Binary classifier error (Figure 6, L278): max |ρ₁| = \REighteenMeasuredRhoClassifier, instrument power at that autocorrelation: \REighteenPowerAtMeasuredRho
- Raw sign stream (R11 Concept pipeline): max |ρ₁| = \REighteenMeasuredRhoSign, instrument power at that autocorrelation: \REighteenPowerAtMeasuredRhoSign

The non-centrality parameter at 80% power is constant across horizons: 20.96. The detectable amplitude follows an n⁻¹ᐟ² law with ratios of consecutive analytic θ₈₀ against 0.5: 0.5020, 0.5005, 0.5001.

At n = 32000, the cluster-bootstrap 95% interval on θ₈₀ [0.012956, 0.013490] does not cover the analytic root 0.012793. This is flagged as a finding but does not affect the bound: four intervals at 95% miss at least once with probability 0.1855 under their own null.
