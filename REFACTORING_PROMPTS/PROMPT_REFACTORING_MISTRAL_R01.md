# DOMAIN SPECIFICATION: SCIENTIFIC STREAM REFACTORING & SANITIZATION STANDARD

This document is the authoritative domain specification for refactoring, sanitizing, and validating experimental stream codebases (**R01**) supporting the manuscript *"The Whitening Advantage: Exact Calibration of Concept-Drift Detectors on Heteroscedastic Streams"* (`./REFACTORING_COMMON/articleB_whitening_v87.tex`).

Refactoring execution priority is governed by `./REFACTORING_COMMON/EXPERIMENTS_SCRIPTS_DEPENDENCIES.md`, section **§3**.

---

## 1. GROUND TRUTH SOURCES & REGIME BOUNDARIES

### 1.1 Ground Truth Sources
- `./REFACTORING_COMMON/articleB_whitening_v87.tex`: The sole authoritative source of truth for scientific nomenclature, mathematical definitions, and theoretical bounds.
- `./REFACTORING_COMMON/REPO_STATE_STREAMS.md`: Authoritative source for stream invariants (S1–S8) and deviation classifications (D0–D3). (Do not cite or mention this file in output artifacts).
- `./REFACTORING_COMMON/MAPPING.md`: Concordance matrix linking figures, tables, and claims to experiment scripts, runners, CSV artifacts, and LaTeX macros.
- `./experiments/common/fair_env.py` & `./experiments/common/fair_harness.py`: Pre-import determinism harness (`enforce_strict_determinism`, `disable_pandas_multithreading`, `save_fair_csv`, `log_artifact_manifest`).

### 1.2 Dual-Regime Code & Prose Boundaries
1. **Regime A (Sanctuarized Execution Core):** All functions, methods, and classes listed in `CARRIED_PRIMITIVES` or `COPIED_PRIMITIVES` are strictly immutable. Byte-level identity must be preserved against runtime `ast.get_source_segment()` audits. Zero alterations to characters, docstrings, inline comments, or indentation are permitted.
2. **Regime B (Dewatermarked Prose & Outer Code):** All module-level docstrings, outer comments, CLI parsers, orchestration code outside Regime A, and documentation files (`AUDIT_R01.md`, `R01.md`, `DEVIATIONS.md`, `R01_v87_*.md`) must undergo active dewatermarking and French-to-English translation.

---

## 2. NEGATIVE CONSTRAINTS (THE MASTER BAN LIST)
The following elements are strictly forbidden in all generated code, docstrings, and documentation:
- **Internal Specification Names:** `SPECS_REPRO_FAIR.md`, `PROMPT_REPO_COMMON_PREAMBLE.md`, `ENG_DEWATERMARKING.md`, `REPO_STATE_STREAMS.md`, `ETAT_REPO_STREAMS.md`, `MAPPING.md`, `"Preamble S4"`, `"SPECS 1.10"`, `"Task brief"`.
- **AI Persona Markers & Meta-Dialogue:** `"Mistral"`, `"Devstral"`, `"Claude"`, `"Claude Code"`, `"Anthropic"`, `"Gemini"`, `"ChatGPT"`, `"OpenAI"`, `"As instructed"`, `"Here is the code"`, `"I have refactored"`.
- **Engineering Traces in Human Documentation:** Raw terminal dumps, multi-line pytest execution traces, wall-clock durations, hardware identifiers (`"AMD EPYC"`), and raw cryptographic hashes.
- **Emotional & Confirmatory Vocabulary:** `proves|proven|perfectly valid|validates the|confirms the|as expected|triumph|victory|irrefutable|brilliant`. Use neutral academic terminology (`"corroborates"`, `"is consistent with"`, `"rejects the null hypothesis"`, `"satisfies the martingale bound"`).
- **Residual French Tokens:** 100% of French comments and text outside Regime A must be translated into formal academic English.

---

## 3. FORMATTING & DELIVERABLE SCHEMAS

### 3.1 Markdown Continuous Line Invariant
Hard-wrapping is strictly prohibited across all Markdown documents. Every paragraph must be a single continuous logical line of text. Newlines are reserved exclusively for structural elements (headers, list items, table rows, code blocks).

### 3.2 Candidate Diff Encapsulation
All LaTeX diffs in `docs/camera_ready_candidates/R01_v87_*.md` must be encapsulated strictly using 9-tilde fences (`~~~~~~~~~latex`) to prevent Markdown code block collisions.

### 3.3 Audit Report Structure (`docs/audits/AUDIT_R01.md`)
Every audit report must contain:
1. **Section 1: Theoretical Anchor:** Mapping claims to theorems, Ville martingale inequalities, and whitening bounds.
2. **Section 2: Empirical Methodology:** Data generating processes, sample horizons $T$, Monte Carlo iterations $B$, and seed schedules.
3. **Section 3: Metric Concordance Table:** Markdown table (`| Metric / Claim | Manuscript Claim | Empirical Witness (Log/CSV) | Wilson 95% CI | Deviation Class |`) with exact Wilson score intervals $[p_L, p_U]$ computed from data counts:
   $$\tilde{p} \pm \frac{z}{1 + z^2/n} \sqrt{\frac{\hat{p}(1 - \hat{p})}{n} + \frac{z^2}{4n^2}}, \quad z = 1.96$$
4. **Section 4: Methodological Scope & Limitations:** Boundary conditions and asymptotic validity domain.

### 3.4 Section README Structure (`docs/sections/R01.md`)
A concise summary (maximum 350 words) structured for automated concatenation:
- `### Stream Overview & Mathematical Target`: Compact single paragraph.
- `### Execution & Verification`: Script name, runner command, and test suite.
- `### Output Artifacts`: Mapping of CSVs, figures, and LaTeX tables.

### 3.5 Deviations Registry (`docs/DEVIATIONS.md`)
Entries categorized strictly under the standardized taxonomy:
- **D0:** Numerical identity within tolerance.
- **D1:** Minor sample-size or boundary variation with statistical justification.
- **D2:** Methodological shift or hyperparameter correction with theoretical rationale.
- **D3:** Structural divergence or broken claim with falsification bound.