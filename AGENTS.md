# NORMATIVE REPOSITORY SPECIFICATION & ARCHITECTURE RULES
# PROJECT: The Whitening Advantage (KDD 2027 Research Track)

## 1. ABSOLUTE INVARIANTS & SYSTEM CONSTRAINTS

1. **Frozen Manuscript (SSOT):** `articleB_whitening_v87.tex` is the Single Source of Truth. It is STRICTLY READ-ONLY. Zero modifications permitted to any `.tex` or `.bib` files of the paper.
2. **Camera-Ready Staging:** Any identified manuscript discrepancy must be staged under `docs/camera_ready_candidates/R[XX]_v87_<topic>.md` with header `STATUS: PARKED — DO NOT APPLY`.
3. **Protected Core Orchestration:** `run_all.sh` and `run_tests.sh` are SHARED orchestration files. Individual stream refactorings must NEVER modify them.
4. **No Shared Scientific Primitives:** `experiments/common/` contains EXCLUSIVELY the determinism and FAIR logging harness (`fair_env.py`, `fair_harness.py`). Statistical, GARCH, QMLE, and CUSUM routines MUST remain duplicated verbatim in each `experiments/R[XX]_*/` folder to prevent cross-stream numerical drift.
5. **Strict Determinism Order (S7):** Every Python script must execute the bootstrap sequence in this exact order:
   - Import `sys`, `pathlib.Path`, inject root into `sys.path`.
   - `from experiments.common.fair_env import enforce_strict_determinism` (stdlib only).
   - `enforce_strict_determinism()` (clamps BLAS/OMP/MKL threads before NumPy initializes).
   - Import `numpy`, `pandas`, then disable pandas multithreading.
   - Assert `os.environ.get("PYTHONHASHSEED") == "42"`.
6. **No Silent Fallbacks:** Any failed condition must raise an explicit exception or terminate via `sys.exit(1)`.

---

## 2. CANONICAL DIRECTORY TOPOLOGY

```text
/home/m53/The-Whitening-Advantage-Experiments/
├── data/
│   ├── derived_crypto/           # Versioned derived daily crypto series (BTC, ETH)
│   ├── derived_equities/         # Versioned panel log-returns (R15)
│   ├── derived_firstrate/        # Versioned daily ETF series from proprietary raw data (R01)
│   ├── firstrate_etf/            # Proprietary raw 1-min data (NON-redistributable)
│   └── reference/                # Read-only historical baselines from submitted campaign
│       └── R[XX]/                # Historical outputs stored under legacy names (protocol_*)
│           └── superseded/       # Abandoned prototype artifacts with documentation
├── docs/
│   ├── audits/                   # Individual audit reports (AUDIT_R[XX].md)
│   ├── camera_ready_candidates/  # Staged LaTeX diff patches (NEVER applied to v87)
│   ├── sections/                 # Modular README fragments (R[XX].md)
│   ├── DEVIATIONS.md             # Consolidated discrepancy registry
│   └── MAPPING.md                # Paper-to-code traceability index
├── experiments/
│   ├── common/                   # Determinism bootstrap & FAIR harness ONLY
│   └── R[XX]_<slug>/             # Isolated stream pipelines (exp_R[XX]_<slug>[_a|_b|_c].py)
├── logs/
│   └── R[XX]_<slug>/             # Dual stdout/file logs (exp_R[XX]_<slug>[_<variant>].log)
├── requirements/
│   └── R[XX].txt                 # Per-stream dynamic requirements fragments
├── results/
│   └── R[XX]_<slug>/
│       ├── data/                 # Clean CSV exports (R[XX]_<logical_name>[_<variant>].csv)
│       ├── figures/              # Publication figures (figNN_<name>.png, figANN_<name>.png)
│       └── tables/               # Dynamic LaTeX macro files (R[XX]_claims.tex)
├── tests/
│   └── test_R[XX]_claims.py      # Non-regression pytest suites asserting published claims
├── build_mapping.py              # Generates docs/MAPPING.md
├── build_readme.sh               # Dynamically concatenates docs/sections/*.md into README.md
├── requirements.txt              # Global requirements compiled from requirements/*.txt
├── run_all.sh                    # Global sequential execution of all streams
├── run_tests.sh                  # Global pytest execution
└── run_experiment_R[XX].sh       # Standalone executable launcher per stream (exports PYTHONHASHSEED=42)
```

---

## 3. STRICT NAMING CONVENTIONS & ARTIFACT SYNTAX

### 3.1 Stream Identifiers (`R[XX]`)
* Main streams: `R01`, `R02`, `R03`, ..., `R18` (two-digit format).
* Sub-streams / sweeps: `R02b`, `R02c`, `R04b`.

### 3.2 Script Architecture
* Single-file pipelines: `experiments/R[XX]_<slug>/exp_R[XX]_<slug>.py`
* Multi-stage pipelines: `experiments/R[XX]_<slug>/exp_R[XX]_<slug>_a.py`, `_b.py`, `_c.py`
* Standalone Launchers: `run_experiment_R[XX].sh` (must `export PYTHONHASHSEED=42`, must NEVER invoke pytest).

### 3.3 Generated Data Files (`results/R[XX]_<slug>/data/`)
* Standard naming: `R[XX]_<logical_name>.csv` (lowercase snake_case, strictly in English).
* Prohibited tokens: Do NOT use legacy prefixes like `protocol_` or tags like `_UPDATED`.
* Methodological variants: Suffixed explicitly (e.g., `_legacy_blas`, `_yfinance`, `_witness_blas`, `_legacy_seeds`, `_independent_seeds`).
* Serialization standard: `float_format='%.17g'`, `na_rep='NaN'`, `lineterminator='\n'`.

### 3.4 Figures (`results/R[XX]_<slug>/figures/`)
* Main paper figures: `figNN_<name>[_<variant>].png` where `NN` is the EXACT two-digit figure number in v87 (e.g., `fig01_ljungbox_whiteness.png`, `fig17_cross_section.png`).
* Appendix figures: `figANN_<name>.png` (e.g., `figA01_iid_overrejection_vs_nu.png`, `figA05_ljungbox_power.png`).
* Panel typography: Panel titles MUST be uppercase, bold, and left-aligned:
  `ax.set_title("(A) ...", fontweight="bold", loc="left")`

### 3.5 LaTeX Macro Tables (`results/R[XX]_<slug>/tables/`)
* File name: `R[XX]_claims[_<variant>].tex`
* Format: Exclusively `\newcommand{\R<Ordinal><ClaimCamelCase>}{<value>}` with zero hardcoded literals.
* Mandatory header: `% Auto-generated by exp_R[XX]_<slug>.py -- do not edit.`
* No raw NaN: If a metric evaluates to NaN, it must be intercepted or formatted to prevent rendering literal "nan" in LaTeX.

### 3.6 Audits, Sections & Requirements Fragments
* Per-stream README section: `docs/sections/R[XX].md`
* Per-stream requirements: `requirements/R[XX].txt` (versions resolved at runtime via `importlib.metadata.version()`).
* Audit report: `docs/audits/AUDIT_R[XX].md` (contains D0-D3 classification, SE bounds, verbatim pytest output, and SHA-256 dual-run verification).

---

## 4. SCIENTIFIC & STATISTICAL REPRODUCIBILITY PROTOCOL

### 4.1 Deviation Scale (D0–D3)
All numerical comparisons against published values in `articleB_whitening_v87.tex` are evaluated at the printed precision of the manuscript:
* **D0:** Identical float64, differing string representation.
* **D1:** Float shifts, but rounded value at printed precision is invariant.
* **D2:** Printed numerical value shifts, but the underlying qualitative claim holds. (Document in `docs/sections/R[XX].md` and `docs/DEVIATIONS.md`).
* **D3:** A qualitative claim is formally falsified or contradictory. (Immediate halt; full diagnostic; zero parameter tuning or post-hoc tolerance widening permitted).

### 4.2 Epistemic Asymmetry & Statistical Controls
* **Positive Controls:** When a detector evaluates invariance or non-rejection, an explicit positive control (injected drift/breakdown) is mandatory to rule out inert detectors.
* **Family-Wise Error Rate:** For $m$ simultaneous tests, log $1 - (1 - \alpha)^m$. If $> 5\%$, do not use zero rejections as a binary gate; use an omnibus or calibration test (e.g., KS test against Uniform(0,1)).
* **Paired Designs & CRN:** Enumerate inter-unit correlations. Account for design effects ($D_{\text{eff}}$) and threshold sampling variances (variance expansion factor $\approx \sqrt{2}$ on out-of-sample evaluations).