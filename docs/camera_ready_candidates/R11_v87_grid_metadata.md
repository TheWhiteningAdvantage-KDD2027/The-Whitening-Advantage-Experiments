# Camera-Ready Candidate: R11_v87_grid_metadata.md

- **Status:** PARKED — do not apply
- **Trigger:** Acceptance notification of 14 November 2026
- **Register entry:** NO DEVIATION — clarification only

STATUS: PARKED — DO NOT APPLY

## R11 Grid Metadata Macro Updates

Grid metadata values including realized Gamma range differ slightly from manuscript values due to the entropy re-keying and solver precision. These are classified as D1 deviations.

~~~~~~~~~latex
% SEARCH
\newcommand{\RElevenGridPoints}{20}
\newcommand{\RElevenStreamsPerPoint}{5000}
\newcommand{\RElevenGammaRange}{170}
% REPLACE WITH
\newcommand{\RElevenGridPoints}{20}
\newcommand{\RElevenStreamsPerPoint}{5000}
\newcommand{\RElevenGammaRange}{170.4}
% END OF BLOCK
~~~~~~~~~
