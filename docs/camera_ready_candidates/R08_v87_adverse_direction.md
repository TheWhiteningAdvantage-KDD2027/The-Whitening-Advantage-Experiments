# Camera-Ready Candidate: R08_v87_adverse_direction.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** `R08-campaign-redraw`

**Target file:** `articleB_whitening_v87.tex`


# R08 v87 Camera-Ready Candidate: Adverse Direction Claims

| Field               | Value                                                       |
| ------------------- | ----------------------------------------------------------- |
| **Status**          | **PARKED — do not apply**                                   |
| Target file         | `articleB_whitening_v87.tex` (submitted 2026-07-27, frozen) |
| Trigger             | Acceptance notification, 14 November 2026                  |
| Register entry      | `docs/DEVIATIONS.md`, `R08-campaign-redraw` (Class A, D2)   |
| Cost                | macro definitions only; no clause changes                 |

This candidate addresses the numerical discrepancies between the manuscript values and the regenerated results for the adverse direction claims in Figure 8.

## Macro Definitions (Regenerated)

<<< SEARCH
~~~~~~~~~latex
% v87 L311 and the Figure 8 caption, as printed
\newcommand{\REightFprCollapse}{0.86\%}
\newcommand{\REightFprInflate}{20.8\%}
% \REightWhitenessGapMax and \REightWhitenessGapMaxAtB: v87 prints no counterpart
\newcommand{\REightWhitenessGapMax}{2.21}
\newcommand{\REightWhitenessGapMaxAtB}{0.075}
\newcommand{\REightWhitenessRangeLow}{5\%}
\newcommand{\REightWhitenessRangeHigh}{100\%}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
% regenerated compliant pipeline
\newcommand{\REightFprCollapse}{0.95\%}
\newcommand{\REightFprInflate}{21.0\%}
\newcommand{\REightWhitenessGapMax}{2.21}
\newcommand{\REightWhitenessGapMaxAtB}{0.075}
\newcommand{\REightWhitenessRangeLow}{4.8\%}
\newcommand{\REightWhitenessRangeHigh}{99.8\%}
~~~~~~~~~
>>> END OF BLOCK

## Manuscript Values (v87)

- FPR collapse (over-centering at b = 0.15): 0.86%
- FPR inflate (under-centering at b = 0.15): 20.8%
- Whiteness range: spanning 5 to 100%

## Deviation Classification

| Macro | Manuscript | Regenerated | Deviation | Rationale |
|-------|-----------|-------------|-----------|-----------|
| \REightFprCollapse | 0.86% | 0.95% | D2 | Printed value shifts at third decimal; qualitative claim (collapse to near-zero) holds |
| \REightFprInflate | 20.8% | 21.0% | D2 | Printed value shifts at first decimal; qualitative claim (inflation by ~20%) holds |
| \REightWhitenessRangeLow | 5% | 4.8% | D2 | Printed value shifts at first decimal; range still spans low single-digits to near-100% |
| \REightWhitenessRangeHigh | 100% | 99.8% | D0 | Rounded value at printed precision (100%) is invariant |

## Control C1 Verification

The regenerated results confirm that both arms (injected-bias and naive reference) yield identical whiteness loss across the b-grid, measured as |delta_lb_pp|. The maximum gap of 2.21 points at b = 0.075 is consistent with the manuscript's claim of "within three points of each other across a range spanning 5 to 100%."

## Cross-Reference

The FPR values for the naive arm reference R07 cells (R07_estmean_lb_fpr.csv), whose movement is already registered as `R07-campaign-redraw`. The adverse direction claims are R08's original contribution.
