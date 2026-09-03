# Camera-Ready Candidate: R17_v87_econometric_baseline.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** `R17-campaign-redraw`

**Target file:** `articleB_whitening_v87.tex`


STATUS: PARKED — DO NOT APPLY

# R17 — Econometric Baseline: L341 Published Values vs Regenerated

The following LaTeX macro definitions from `results/R17_econometric_baseline/tables/R17_claims.tex` differ from the values printed in v87 L341 at their printed precision.

## Manuscript Values (v87 L341)

```latex
\newcommand{\RSeventeenTruePersistence}{0.85}
\newcommand{\RSeventeenMedianPersistenceAtWarmupTwoFifty}{0.62}
\newcommand{\RSeventeenFprEcoAtWarmupTwoFifty}{9.5\%}
\newcommand{\RSeventeenFprEcoAtWarmupFiveHundred}{3.0\%}
\newcommand{\RSeventeenSignFprMin}{3\%}
\newcommand{\RSeventeenSignFprMax}{8\%}
```

## Regenerated Values (Compliant Deterministic Pipeline)

```latex
\newcommand{\RSeventeenTruePersistence}{0.85}
\newcommand{\RSeventeenMedianPersistenceAtWarmupTwoFifty}{0.63}
\newcommand{\RSeventeenFprEcoAtWarmupTwoFifty}{10.5\%}
\newcommand{\RSeventeenFprEcoAtWarmupFiveHundred}{7.0\%}
\newcommand{\RSeventeenSignFprMin}{10\%}
\newcommand{\RSeventeenSignFprMax}{11\%}
```

## Diff Blocks for Camera-Ready

<<< SEARCH
~~~~~~~~~latex
% L341 persistence median
% \newcommand{\RSeventeenMedianPersistenceAtWarmupTwoFifty}{0.62}

% L341 FPR at n = 250
% \newcommand{\RSeventeenFprEcoAtWarmupTwoFifty}{9.5\%}

% L341 FPR at n = 500
% \newcommand{\RSeventeenFprEcoAtWarmupFiveHundred}{3.0\%}

% L341 sign FPR envelope
% \newcommand{\RSeventeenSignFprMin}{3\%}
% \newcommand{\RSeventeenSignFprMax}{8\%}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
% L341 persistence median
\newcommand{\RSeventeenMedianPersistenceAtWarmupTwoFifty}{0.63}

% L341 FPR at n = 250
\newcommand{\RSeventeenFprEcoAtWarmupTwoFifty}{10.5\%}

% L341 FPR at n = 500
\newcommand{\RSeventeenFprEcoAtWarmupFiveHundred}{7.0\%}

% L341 sign FPR envelope
\newcommand{\RSeventeenSignFprMin}{10\%}
\newcommand{\RSeventeenSignFprMax}{11\%}
~~~~~~~~~
>>> END OF BLOCK

## Deviation Classification

- **\RSeventeenTruePersistence**: D0 (identical float64 at printed precision)
- **\RSeventeenMedianPersistenceAtWarmupTwoFifty**: D2 (0.62 -> 0.63, printed value shifts)
- **\RSeventeenFprEcoAtWarmupTwoFifty**: D2 (9.5% -> 10.5%, printed value shifts)
- **\RSeventeenFprEcoAtWarmupFiveHundred**: D2 (3.0% -> 7.0%, printed value shifts)
- **\RSeventeenSignFprMin / \RSeventeenSignFprMax**: D2 (3-8% -> 10-11%, printed range shifts)

## Qualitative Claims Preservation

All three qualitative claims of L341 are CORROBORATED despite the D2 deviations:

1. **Persistence collapse**: The regenerated pooled median 0.63 is well below the true persistence 0.85, corroborating "the estimated persistence collapses to a median alpha_hat + beta_hat".

2. **FPR restoration**: FPR_Eco falls from 10.5% at n=250 to 7.0% at n=500, corroborating "the level is restored from n = 500 onward". The Wilson 95% CI at n=500 [4.2%, 11.4%] contains the nominal 5% level.

3. **Sign arm warm-up independence**: The WLS slope of sign FPR on log(n_warmup) is 0.0021 with 95% paired-bootstrap interval [-0.0153, 0.0195], which covers zero, corroborating "the sign pipeline is warm-up-independent in practice".

## Root Cause

The entropy migration (SPECS 1.2) redraws both the SPECS 1.10-compliant arm and the legacy-QMLE attribution arm from injected 128-bit SeedSequence keys, producing different Monte-Carlo realizations from the submitted campaign. This is a deliberate design choice: the legacy arm certifies NO v87 value and isolates the SPECS 1.10 displacement alone.

## Cross-References

- `docs/DEVIATIONS.md` section "## R17 — Econometric Baseline and L341" documents the formal D2 classification.
- `R17_sign-arm-crn-degeneracy`: The sign stream is bit-identical across the leverage axis at c=0, a consequence of the same entropy migration.
- `R17-campaign-redraw`: The four L341 numerals fail to reproduce at printed precision due to the campaign redraw.
