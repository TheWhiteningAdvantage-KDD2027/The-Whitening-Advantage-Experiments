# Camera-Ready Candidate: R09_v87_cusum_peeking_fpr.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** `R09-cusum-peeking-fpr-d2`

**Target file:** `articleB_whitening_v87.tex`


STATUS: PARKED — DO NOT APPLY

# R09 Camera-Ready Candidate: CUSUM Peeking FPR

The manuscript at L243 states that CUSUM's realized false-alarm rate climbs to $18\%$ under continuous monitoring (peeking over $[1, 4H]$). 

The reproduced measurement from `R09_validity_stopping.csv` at alpha = 0.05, stopping_protocol = peeking is $19.88\%$ with Wilson 95% CI $[0.1933, 0.2044]$.

The discrepancy is classified as D2: the printed numerical value shifts from 18% to 19.88% at the manuscript's own precision. The qualitative claim that CUSUM's rate climbs under peeking remains valid.

<<< SEARCH
~~~~~~~~~latex
% Line 243: replace 18\% with 19.88\%
\newcommand{\RNineCusumPeekingFprMax}{19.88\%}
~~~~~~~~~
=== REPLACE WITH >>>
~~~~~~~~~latex
% Line 243: replace 18\% with 19.88\%
\newcommand{\RNineCusumPeekingFprMax}{19.9\%}
~~~~~~~~~
>>> END OF BLOCK

Cross-reference: docs/DEVIATIONS.md entry R09-cusum-peeking-fpr-d2.

