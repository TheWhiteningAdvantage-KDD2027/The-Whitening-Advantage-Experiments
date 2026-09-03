# Camera-Ready Candidate: R14_v87_crypto_isofpr_ratios.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** `R14-campaign-redraw`

**Target file:** `articleB_whitening_v87.tex`


STATUS: PARKED — DO NOT APPLY

## R14 Synth_BTC ADD Ratio Macro Updates

The compliant deterministic pipeline with 128-bit re-keying produces Synth_BTC ADD ratio values that differ from the submitted manuscript at printed precision. The witness arm (legacy seeds) reproduces v87 values exactly (D0), but the migrated arm produces new values due to entropy migration. This is a D2 deviation: the printed numerical values shift but qualitative claims (inversion of light-tailed ordering) are preserved.

<<< SEARCH
~~~~~~~~~latex
\newcommand{\RFourteenRatioSynthMin}{0.98}
\newcommand{\RFourteenRatioSynthMax}{1.14}
\newcommand{\RFourteenRatioSynthMean}{1.06}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\RFourteenRatioSynthMin}{0.95}
\newcommand{\RFourteenRatioSynthMax}{1.24}
\newcommand{\RFourteenRatioSynthMean}{1.04}
~~~~~~~~~
>>> END OF BLOCK
