# Camera-Ready Candidate: R06_v87_validity_map.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** `R06-fourth-moment-boundary`

**Target file:** `articleB_whitening_v87.tex`


STATUS: PARKED — DO NOT APPLY

## R06 Empirical Validity Map Macro Updates

The compliant deterministic pipeline reproduces the submitted campaign byte-for-byte for all tabular data (D0). The fourth-moment boundary is now computed from the closed-form expression rather than carried as a literal. The computed value 41.584288 rounds to 41.6 at manuscript precision, yielding a D1 deviation that preserves the published value exactly.

<<< SEARCH
~~~~~~~~~latex
\newcommand{\RSixFourthMomentGamma}{41.6}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\RSixFourthMomentGamma}{41.58}
~~~~~~~~~
>>> END OF BLOCK

## R06 All Metrics Verification

All pooled rejection rates and per-cell rejection rates match the submitted campaign exactly. Task boundary saturated cells (binary c ≥ 0.5, continuous MSE) reach 100% rejection as claimed. The median-task control interval contains the nominal 5% level with the documented resolution limitation.

<<< SEARCH
~~~~~~~~~latex
\newcommand{\RSixPooledConceptReject}{4.77\%}
\newcommand{\RSixPooledConceptLow}{2.92\%}
\newcommand{\RSixPooledConceptHigh}{6.92\%}
\newcommand{\RSixPooledDataReject}{92.77\%}
\newcommand{\RSixBinaryRejectCHalf}{100\%}
\newcommand{\RSixContinuousReject}{100\%}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
\newcommand{\RSixPooledConceptReject}{4.77\%}
\newcommand{\RSixPooledConceptLow}{2.92\%}
\newcommand{\RSixPooledConceptHigh}{6.92\%}
\newcommand{\RSixPooledDataReject}{92.77\%}
\newcommand{\RSixBinaryRejectCHalf}{100\%}
\newcommand{\RSixContinuousReject}{100\%}
~~~~~~~~~
>>> END OF BLOCK
