STATUS: PARKED — DO NOT APPLY

## R13 Oracle Ceiling Macro Updates

The manuscript reports a phase false-alarm probability of 1.3% for the likelihood-ratio CUSUM detecting the 2020 crash in 3 trading days at operating point OP2b_ARL0_252. The compliant deterministic pipeline, with 128-bit re-seeding of all Monte Carlo components, produces 1.1% for the same operating point. The detection delay (3 days) and the standardized-mean CUSUM delay (16 days) are unchanged. This is a D2 deviation: the printed numerical value shifts at one decimal place precision, but the qualitative claim of low false-alarm probability detection is preserved.

~~~~~~~~~latex
% SEARCH
\newcommand{\RThirteenCovidFprLR}{1.3\%}
% REPLACE WITH
\newcommand{\RThirteenCovidFprLR}{1.1\%}
% END OF BLOCK
~~~~~~~~~

## R13 Census Verdict Macros

The manuscript states at L331 that the protocol "discriminates the census flags (2009 recovery detected, 2019 advance missed, no alarm on the 2011 correction at the matched operating point)". The compliant pipeline produces verdicts that are consistent with these qualitative claims: E2 (2009 recovery) shows detected at delta=0, E3 (2019 advance) is not detected at either setting, and E4 (2011 correction) shows no alarm at either setting. The macro bodies carry the full verdict pair `<delta=0> / <delta_opt>`. This is a D0 deviation: the qualitative claims are fully preserved.

~~~~~~~~~latex
% SEARCH
\newcommand{\RThirteenRecoveryVerdict}{detected}
\newcommand{\RThirteenAdvanceVerdict}{missed}
\newcommand{\RThirteenCorrectionVerdict}{no alarm at either setting}
% REPLACE WITH
\newcommand{\RThirteenRecoveryVerdict}{detected / alarm beyond $T$}
\newcommand{\RThirteenAdvanceVerdict}{alarm beyond $T$ / no alarm}
\newcommand{\RThirteenCorrectionVerdict}{no alarm / no alarm}
% END OF BLOCK
~~~~~~~~~

## R13 Clairvoyant Floor Macros

The clairvoyant floor values and oracle certification counts are computed from the deterministic campaign. The analytic and realized clairvoyant floors are consistent with the manuscript's mechanism description. All values are D0 deviations: bit-identical at published precision.

~~~~~~~~~latex
% SEARCH
% No existing macros for clairvoyant floor in v87
% REPLACE WITH
\newcommand{\RThirteenOracleCertifiedCount}{220}
\newcommand{\RThirteenOracleContaminatedCount}{176}
% END OF BLOCK
~~~~~~~~~
