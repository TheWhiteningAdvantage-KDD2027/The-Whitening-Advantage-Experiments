# Camera-Ready Candidate: R04_v87_table3_data.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** `R04-gamma-grid-defect`

**Target file: `articleB_whitening_v87.tex`**

# R04 — Iso-FPR Race Table 3 Data Cells

STATUS: PARKED — DO NOT APPLY

This file contains the LaTeX table cell diff blocks for Table 3 between the regenerated compliant pipeline and the manuscript values from v87. The compliant pipeline uses a genuinely spanned Gamma grid (1.1053, 11.58, 50.0, 200.0) while the submitted campaign collapsed to Gamma = 1.0 for all labels.

## Root Cause

The parameter ordering bug in `solve_beta_for_gamma(gamma, alpha)` caused all Gamma targets to resolve to beta = 0, collapsing the grid. The compliant pipeline corrects this to `solve_beta_for_gamma(alpha, gamma)`, producing the intended grid span.

## Table 3 Cell Diff Blocks

All ADD values are rounded to 3 significant figures as per the Table 3 printing rule. DetRate values shown in parentheses when below 1.

### Gamma = 1.1053 (labelled 1.0 in v87)

<<< SEARCH
~~~~~~~~~latex
        $0.25$ & $2293$ \; $(0.19)$                              & $389$                                      & $460$                   \\
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
        $0.25$ & $2533$ \; $(0.179)$                              & $369$                                      & $439$                   \\
~~~~~~~~~
>>> END OF BLOCK

<<< SEARCH
~~~~~~~~~latex
        $0.50$ & $1337$ \; $(0.89)$                              & $72.0$                                     & $101$                   \\
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
        $0.50$ & $1483$ \; $(0.874)$                              & $70.3$                                     & $99.2$                   \\
~~~~~~~~~
>>> END OF BLOCK

<<< SEARCH
~~~~~~~~~latex
        $1.00$ & $203$                                           & $26.4$                                     & $43.8$                  \\
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
        $1.00$ & $236$                                           & $25.6$                                     & $42.1$                  \\
~~~~~~~~~
>>> END OF BLOCK

<<< SEARCH
~~~~~~~~~latex
        $2.00$ & $55.9$                                          & $12.6$                                     & $28.9$                  \\
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
        $2.00$ & $64.6$                                          & $12.2$                                     & $28.4$                  \\
~~~~~~~~~
>>> END OF BLOCK

### Gamma = 11.58

<<< SEARCH
~~~~~~~~~latex
% (Not present in manuscript - Gamma grid collapsed)
\newcommand{\placeholder}{}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
        $0.25$ & $2746$ \; $(0.097)$                              & $409$                                      & $382$                   \\
        $0.50$ & $2622$ \; $(0.239)$                              & $77.1$                                     & $96.9$                  \\
        $1.00$ & $1987$                                           & $30.9$                                     & $42.6$                  \\
        $2.00$ & $1311$                                          & $16.1$                                     & $28.6$                  \\
~~~~~~~~~
>>> END OF BLOCK

### Gamma = 50.0

<<< SEARCH
~~~~~~~~~latex
% (Not present in manuscript - Gamma grid collapsed)
\newcommand{\placeholder}{}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
        $0.25$ & $2980$ \; $(0.061)$                              & $404$                                      & $345$                   \\
        $0.50$ & $2964$ \; $(0.116)$                              & $84.3$                                     & $99.3$                  \\
        $1.00$ & $2626$                                           & $33.7$                                     & $43.8$                  \\
        $2.00$ & $2157$ \; $(0.536)$                              & $17.6$                                     & $29.2$                  \\
~~~~~~~~~
>>> END OF BLOCK

### Gamma = 200.0

<<< SEARCH
~~~~~~~~~latex
% (Not present in manuscript - Gamma grid collapsed)
\newcommand{\placeholder}{}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
        $0.25$ & $2805$ \; $(0.073)$                              & $345$                                      & $294$                   \\
        $0.50$ & $2843$ \; $(0.106)$                              & $84.0$                                     & $94.9$                  \\
        $1.00$ & $2647$ \; $(0.253)$                              & $33.5$                                     & $43.2$                  \\
        $2.00$ & $2277$ \; $(0.416)$                              & $17.2$                                     & $29.1$                  \\
~~~~~~~~~
>>> END OF BLOCK
