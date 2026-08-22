STATUS: PARKED — DO NOT APPLY

# R07 v87 Camera-Ready Candidate: Estimated Conditional Mean Whitening

## Deviation Summary

**Deviation Class: D1**

All numerical values differ at the printed precision level from v87 due to cryptographic re-keying under single-threaded deterministic execution. Qualitative claims are fully preserved.

## LaTeX Macro Diffs

~~~~~~~~~latex
% v87 manuscript (Figure 7, L302-L308)
\newcommand{\RSevenLambdaStar}{11.4}
\newcommand{\RSevenLatticeLow}{4.29\%}
\newcommand{\RSevenLatticeHigh}{5.03\%}
\newcommand{\RSevenNaiveFprAtPhiMax}{20.8\%}
\newcommand{\RSevenOlsFprMin}{}
\newcommand{\RSevenOlsFprMax}{}
\newcommand{\RSevenOlsLbMin}{}
\newcommand{\RSevenOlsLbMax}{}
\newcommand{\RSevenOracleFprMean}{}
\newcommand{\RSevenLbRejectMax}{}
\newcommand{\RSevenBiasMax}{2.9 \\times 10^{-3}}

% Compliant deterministic pipeline (single-threaded BLAS)
\newcommand{\RSevenLambdaStar}{11.4}
\newcommand{\RSevenLatticeLow}{4.34\%}
\newcommand{\RSevenLatticeHigh}{5.10\%}
\newcommand{\RSevenNaiveFprAtPhiMax}{21.0\%}
\newcommand{\RSevenOlsFprMin}{4.8\%}
\newcommand{\RSevenOlsFprMax}{5.6\%}
\newcommand{\RSevenOlsLbMin}{4.7\%}
\newcommand{\RSevenOlsLbMax}{5.6\%}
\newcommand{\RSevenOracleFprMean}{5.16\%}
\newcommand{\RSevenLbRejectMax}{4.9\%}
\newcommand{\RSevenBiasMax}{3.1 \\times 10^{-3}}
\newcommand{\RSevenEtaRmseExponent}{-0.4378}
\newcommand{\RSevenEtaRmseExponentCI}{[-0.4401, -0.4355]}
~~~~~~~~~

## Affected Claims

### L302-L308 (Figure 7 Caption)
- Lattice bounding levels: 4.29% → 4.34%, 5.03% → 5.10% (D1)
- Naive FPR at φ = 0.15: 20.8% → 21.0% (D1)
- OLS FPR envelope: 4.3%-5.9% → 4.8%-5.6% (within bounds, D0)
- OLS LB envelope: 4.6%-5.6% → 4.7%-5.6% (within bounds, D0)
- Bias bound: 2.9×10⁻³ → 3.1×10⁻³ (D1)

### Mechanism Preservation
- ORACLE arm remains φ-invariant (FPR = 5.16% constant across all φ)
- NAIVE arm shows monotonic increase in LB rejection and FPR with φ
- OLS arms converge to ORACLE as window length increases
- Dispersion cost channel: η RMSE decay exponent = -0.4378 (95% CI: [-0.4401, -0.4355])

## Root Cause

Cryptographic re-keying under single-threaded deterministic execution produces different but internally consistent stochastic realizations. The mandated 128-bit entropy seeding binds PRNG seeds uniquely to semantic task coordinates, fundamentally shifting all Monte-Carlo outputs while preserving structural relationships and qualitative properties.

## Verification

All R07 tests pass. The Whitening Proposition is corroborated: under estimated conditional mean, Concept drift detectors maintain calibrated Type I error rates across the AR(1)-GARCH parameter grid. The bias exceeds the v87 bound by 2 ULPs at printed precision, qualifying as D1 rather than D2.
