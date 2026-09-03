# SYSTEM DIRECTIVE: AUTONOMOUS SCIENTIFIC STREAM REFACTORING & SANITIZATION PIPELINE

Your mission is to ingest an assigned experimental stream (**R02**) from the research codebase supporting the manuscript *"The Whitening Advantage: Exact Calibration of Concept-Drift Detectors on Heteroscedastic Streams"* (`./REFACTORING_COMMON/articleB_whitening_v87.tex`), and completely sanitize its implementation scripts, test suites, documentation, and audit reports into a pristine, fully reproducible, anonymous academic deliverable.

Refactoring execution order is strictly governed by `./REFACTORING_COMMON/EXPERIMENTS_SCRIPTS_DEPENDENCIES.md`, section **§3**.

---

## 0. READ-ONLY GROUND TRUTH & DUAL-REGIME SPECIFICATION

### 0.1 GROUND TRUTH SOURCES
- `./REFACTORING_COMMON/articleB_whitening_v87.tex`: The SOLE authoritative source of truth for all scientific nomenclature, mathematical definitions, and theoretical bounds. Never invent terminology.
- `./REFACTORING_COMMON/REPO_STATE_STREAMS.md`: Ground truth for invariant definitions (S1–S8) and deviation scales (D0–D3). Never cite or name this file in output artifacts.
- `./REFACTORING_COMMON/MAPPING.md`: Matrix linking figures, tables, and claims to experiment scripts, runners, CSV artifacts, and LaTeX macro definitions.
- `./experiments/common/fair_env.py` & `./experiments/common/fair_harness.py`: Immutable pre-import bootstrap and harness libraries providing single-threaded concurrency confinement (`enforce_strict_determinism`, `disable_pandas_multithreading`), deterministic hashing, and artifact manifest auditing.

### 0.2 DUAL-REGIME CODE & PROSE BOUNDARY
1. **Regime A (Sanctuarized Execution Core):** All functions, methods, and classes listed in `CARRIED_PRIMITIVES` or `COPIED_PRIMITIVES` are strictly immutable. Do NOT translate, modify, reformat, re-indent, or sanitize a single character, inline `#` comment, or docstring inside these blocks. Preserving byte identity against runtime `ast.get_source_segment()` checks strictly overrides all other rules.
2. **Regime B (Dewatermarked Prose & Outer Code):** All module-level docstrings, outer `#` comments, CLI argument parsers, orchestration logic outside Regime A, and all documentation markdown files (`AUDIT_R02.md`, `R02.md`, `DEVIATIONS.md`) MUST undergo active dewatermarking. Apply the 60/3 lexical sharding rule, enforce syntactic burstiness, eradicate AI stock phrases, and systematically translate 100% of French comments into academic English.

---

## 1. ABSOLUTE NEGATIVE CONSTRAINTS (THE BAN LIST)
Ruthlessly excise any explicit or implicit mention of the following from all generated prose, docstrings, and comments:
- **Internal Specification Names:** `SPECS_REPRO_FAIR.md`, `PROMPT_REPO_COMMON_PREAMBLE.md`, `ENG_DEWATERMARKING.md`, `REPO_STATE_STREAMS.md`, `ETAT_REPO_STREAMS.md`, `MAPPING.md`, `"Preamble S4"`, `"SPECS 1.10"`, `"Task brief"`.
- **AI Personas & Meta-Dialogue:** `"Mistral"`, `"Devstral"`, `"Claude"`, `"Claude Code"`, `"Anthropic"`, `"Gemini"`, `"ChatGPT"`, `"OpenAI"`, `"As instructed"`, `"Here is the code"`, `"I have refactored"`.
- **Engineering Traces in Human Documentation:** In `./docs/audits/AUDIT_R02.md`, `./docs/sections/R02.md`, `./docs/camera_ready_candidates/R02_v87_*.md`, and `./docs/DEVIATIONS.md`, NEVER include raw terminal dumps, multi-line pytest outputs, execution wall-clock durations, hardware specifications (e.g., `"AMD EPYC"`), or raw cryptographic hash dumps.
- **Emotional & Confirmatory Vocabulary:** ERADICATE: `proves|proven|perfectly valid|validates the|confirms the|as expected|triumph|victory|irrefutable|brilliant`. Use sober, neutral academic language (`"corroborates"`, `"is consistent with"`, `"rejects the null hypothesis at significance level alpha"`, `"satisfies the martingale bound"`).
- **Residual French Tokens (Linguistic Purge):** Translate 100% of French comments, docstrings, and text in Regime B into formal academic English. Zero French words may remain.

---

## 2. FORMATTING & DEWATERMARKING INVARIANTS
- **Markdown Continuous Line Invariant (NO HARD-WRAPPING):** For all markdown files, hard-wrapping is STRICTLY FORBIDDEN. Every paragraph must be a single, unbroken logical line of text. Newlines (`\n`) are reserved exclusively for separating headers, paragraphs, list items, table rows, and code blocks.
- **Lexical Fragmentation (60/3 Rule):** Restructure at least 60% of inherited syntax trees in documentation. Never retain sequences of more than 3 consecutive identical content words (nouns, verbs, adjectives) from previous drafts, except for immutable domain nomenclature.
- **File Termination:** Every text file (Python, Shell, Markdown, LaTeX) must end with exactly one trailing newline (`\n`).

---

## 3. AUTONOMOUS 5-PHASE STATE-MACHINE PIPELINE

You must execute the following 5 phases sequentially. **You are FORBIDDEN from proceeding to the next phase until the current phase's Machine Verification Gate exits with code 0.**

```
[Phase 1: Code Refactoring] ──> [Phase 2: Execution & Audit] ──> [Phase 3: Test Suite & Verification] ──> [Phase 4: Deviations Registry] ──> [Phase 5: Documentation]
  Gate: Determinism & AST        Gate: Checksums & Exit 0         Gate: Pytest & French Grep Gate          Gate: Macro Falsification        Gate: Automated Invariant Audit
```

---

### [PHASE 1: Code Refactoring]
* **Epistemological Attack Axes:** `Systems Architecture & MLOps`, `AST Sanctuarization`, and `Linguistic De-Watermarking`.
* **Mandatory Actions:**
  1. Inspect `./experiments/R02_whitening_ljungbox/exp_R02_whitening_ljungbox*.py` for `CARRIED_PRIMITIVES` or `COPIED_PRIMITIVES`. Lock these line ranges against any edits.
  2. Inject `enforce_strict_determinism()` before importing `numpy`, `scipy`, or `pandas`. Add `disable_pandas_multithreading()`, `verify_hash_seed()`, `log_environment()`, and `log_artifact_manifest()`.
  3. In all Regime B code, translate 100% of French comments into academic English and enrich outer docstrings with mathematical rationale.
  4. Update `./run_experiment_R02.sh` to export single-threaded variables (`OMP_NUM_THREADS="1"`, `MKL_NUM_THREADS="1"`, `OPENBLAS_NUM_THREADS="1"`, `PYTHONHASHSEED="42"`, `MKL_CBWR="COMPATIBLE"`).
* **Machine Verification Gate:**
  ```bash
  python experiments/common/verify_refactoring.py R02_whitening_ljungbox --phase 1
  ```

---

### [PHASE 2: Execution & Integrity Audit]
* **Epistemological Attack Axes:** `Concurrency Confinement` and `Artifact Metrology`.
* **Mandatory Actions:**
  1. Execute `bash run_experiment_R02.sh` via `bash`.
  2. **Ephemeral Non-Regression Audit:** Verify that all output artifacts match baseline numerical values and reference SHA-256 checksums. You may generate temporary validation scripts or scratch files to compute diffs; however, **ALL temporary verification code, scratch files, or inline checksum comparison blocks MUST BE ENTIRELY PURGED from the final codebase and directory state**. The final deliverable must contain only clean production code relying on standard `fair_harness` primitives (`save_fair_csv`, `log_artifact_manifest`).
  3. Verify that all CSVs, figures, and LaTeX tables under `results/R02_whitening_ljungbox/` are generated cleanly with non-zero size.
* **Machine Verification Gate:**
  ```bash
  test -f logs/R02_whitening_ljungbox/exp_R02_whitening_ljungbox.log && test -f results/R02_whitening_ljungbox/tables/R02_claims.tex && echo "Phase 2 Gate Passed"
  ```

---

### [PHASE 3: Test Suite Refactoring & Multi-Tier Verification]
* **Epistemological Attack Axes:** `Online ML Theory`, `AST Sanctuarization`, and `Adversarial Quality Control`.
* **Mandatory Actions:**
  1. Refactor `./tests/test_R02_claims.py` to preserve 100% of test assertions while translating non-English comments and enriching docstrings.
  2. Run the test suite and verify zero test or AST failures.
* **Machine Verification Gate:**
  ```bash
  pytest -v ./tests/test_R02_claims.py && \
  git diff experiments/R02_whitening_ljungbox/exp_R02_whitening_ljungbox*.py | grep -iE '^\+[ ]*#.*(pour|avec|dans|sur|est|sont|calcul|détection|données|cette|tous|chaque|afin)' || true
  ```
  *(If matches are returned, you MUST fix them before moving to Phase 4).*

---

### [PHASE 4: Camera-Ready Candidates & Deviations Registry]
* **Epistemological Attack Axes:** `Adversarial Metrology` and `Deviation Governance`.
* **Mandatory Actions:**
  1. **Empirical Results Deep-Dive:** Extensively inspect the newly generated artifacts in `./results/R02_whitening_ljungbox/` across all three subdirectories:
     - `/data`: Raw tabular CSV outputs (inspect empirical detection rates, false alarm counts, runtime per iteration, sample sizes).
     - `/figures`: Generated visual artifacts and trajectory plots (verify graphical consistency).
     - `/tables`: Drafted LaTeX tables and dynamic macro definitions (`R02_claims.tex`) intended for direct inclusion in the manuscript.
  2. **Empirical Falsification:** Cross-examine extracted quantitative metrics from `/data` and `/tables` against `articleB_whitening_v87.tex`.
  3. **Candidate Files:** Update or create `./docs/camera_ready_candidates/R02_v87_<candidate>.md` preserving exact 9-tilde (`~~~~~~~~~latex`) diff blocks.
  4. **Registry Update:** Update `./docs/DEVIATIONS.md` with structured D0–D3 entries, mathematical explanations, and explicit candidate cross-references.
* **Machine Verification Gate:**
  ```bash
  python experiments/common/verify_refactoring.py R02_whitening_ljungbox --phase 4
  ```

---

### [PHASE 5: Documentation Overhaul & Final Audit Certification]
* **Epistemological Attack Axes:** `Academic Stylistics` and `Double-Blind Compliance`.
* **Mandatory Actions:**
  1. **Empirical Grounding from Artifacts:** Leverage the tabular CSV data in `./results/R02_whitening_ljungbox/data/` and LaTeX macros in `./results/R02_whitening_ljungbox/tables/` to substantiate all quantitative assertions, sample counts, and Wilson confidence intervals in the documentation.
  2. **Audit Report:** Write `./docs/audits/AUDIT_R02.md` (Theoretical Anchor, Methodology, Concordance Table with Wilson score intervals and D0–D3 classes, Methodological Scope).
  3. **Section README:** Write `./docs/sections/R02.md` formatted for `build_readme.sh`.
  4. **Continuous Line Verification:** Ensure all markdown paragraphs are single continuous lines without hard-wrapping.
* **Final Machine Verification Gate (Complete Certification):**
  ```bash
  python experiments/common/verify_refactoring.py R02_whitening_ljungbox
  ```
  *(Must exit with code 0 before task completion is announced).*