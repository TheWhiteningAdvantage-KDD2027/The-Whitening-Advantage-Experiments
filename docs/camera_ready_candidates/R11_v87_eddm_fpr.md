# Camera-Ready Candidate: R11_v87_eddm_fpr.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** `R11-regenerated`

STATUS: PARKED — DO NOT APPLY

## R11 EDDM FPR Floor Macro Updates

The EDDM false positive rate floor under H0 Concept differs from the manuscript value and is classified as D2. The compliant pipeline produces 92.10% vs manuscript 90%. The qualitative claim that EDDM is permanently triggered (>90% FPR) remains valid.

<<< SEARCH
~~~~~~~~~latex
\newcommand{\RElevenEddmFprMean}{90\%}
\newcommand{\RElevenEddmFprWilsonLow}{88.5\%}
\newcommand{\RElevenEddmFprWilsonHigh}{91.5\%}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\RElevenEddmFprMean}{92.10\%}
\newcommand{\RElevenEddmFprWilsonLow}{90.99\%}
\newcommand{\RElevenEddmFprWilsonHigh}{93.21\%}
~~~~~~~~~
>>> END OF BLOCK
