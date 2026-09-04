#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

trap 'rm -f README_preamble.md' EXIT

# 1. Preamble generation (anonymised)
cat << 'EOF' > README_preamble.md
# The Whitening Advantage: Exact Calibration of Concept-Drift Detectors on Heteroscedastic Streams

This repository contains the official, strictly reproducible experimental pipeline for the KDD 2027 Research Track submission *The Whitening Advantage*.

**CRITICAL NOTICE:** Please read [`docs/DEVIATIONS.md`](docs/DEVIATIONS.md) first. It contains the consolidated register of every divergence between the submitted manuscript and this reproducible repository, classified at the manuscript's own printing precision.

## 1. Overview
This repository provides the code to independently reproduce the 21 experiment streams (R01-R18, including the variants R02b, R02c and R04b) supporting the paper's claims. The central thesis is that on a sign-prediction task, the binary error stream of a non-anticipative classifier is exactly i.i.d. Bernoulli(1/2) regardless of underlying GARCH volatility dynamics (Proposition 3.1, *Sign-Task Whitening Property*), enabling exact concept-drift detector calibration without variance estimation.

A complete mapping table linking every figure and every number of the manuscript to its generating script, its CSV and its LaTeX macro file is in [`docs/MAPPING.md`](docs/MAPPING.md), generated from the repository tree by `build_mapping.py`.

## 2. Repository Structure
* `data/`: Derived daily series (`derived_firstrate/`, `derived_crypto/`, `derived_equities/`) and read-only historical campaign witnesses (`reference/`). Raw proprietary intraday ETF data is omitted.
* `docs/`: The deviation register (`DEVIATIONS.md`), the mapping table (`MAPPING.md`), the forensic audit reports (`audits/`), the per-experiment reports (`sections/`), and the LaTeX corrections parked for the final version (`camera_ready_candidates/`).
* `experiments/`: The FAIR execution harness (`common/`) and the standalone execution scripts per stream (`R[XX]_<slug>/`).
* `logs/`: Execution logs. These carry the SHA-256 digests, the control margins and the package versions on which every reproducibility claim in this repository rests.
* `results/`: All generated artefacts (CSV data, figures, LaTeX macros).
* `tests/`: Pytest regression suites certifying the numerical integrity of each stream.

## 3. Certified Environment
The campaign is locked to the following environment to guarantee IEEE 754 float determinism.
* **Python:** 3.12.9
* **Determinism:** MKL and OpenBLAS are strictly pinned to single-threading (`OMP_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`) before NumPy imports. `PYTHONHASHSEED` is exported as `42` by each runner and verified by each script.

## 4. Reproduction Commands
The pipeline relies on specific package versions to guarantee numeric determinism. Create a virtual environment and install the root requirements before executing.

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Execute the entire pipeline and the test suite
bash run_all.sh
```

To run a specific stream individually:
```bash
bash run_experiment_R01.sh
```

To execute only the test suite:
```bash
bash run_tests.sh
```

## 5. Data Availability
Experiments relying on real-world ETF data (R01, R16) consume pre-aggregated daily derived series in `data/derived_firstrate/`, giving full reproducibility without the proprietary 1-minute FirstRate data, which is not redistributable.

Every non-redistributable input has a public fetcher and a versioned derived series, so the nominal reviewer path never touches the network: R14 fetches daily Bitcoin and Ethereum into `data/derived_crypto/`, R15 fetches the 97-equity panel into `data/derived_equities/`, and R01 offers an open-source path via `--data-source yfinance`. Each of those streams separates `--stage ingest` from `--stage analyse`; `--stage analyse` is the nominal path and the one certified bit-identical across runs. No stream falls back silently to an alternative source: the source is selected by an explicit argument and stamped in the output filenames.

## 6. What This Repository Found Against Its Own Manuscript

The campaign regenerated all 21 streams under a stricter reproducibility standard than the submitted campaign used. What it found falls into three groups, and the proportions matter more than any single entry: about twenty defects in the experimental apparatus, nine formal contradictions of the manuscript, and no falsified proposition. Every one was found by the authors, and every one is documented here.

### 6.1 Formal contradictions of the submitted manuscript

Claims the regenerated pipeline does not produce. Full detail, with the source CSV cell for every value, is in [`docs/DEVIATIONS.md`](docs/DEVIATIONS.md) and in the corresponding audit under `docs/audits/`.

| Register entry | Manuscript site | What does not hold |
|---|---|---|
| `R02b-iid-arm-over-rejection`       | L278                                                             | The manuscript states the squared inputs "already over-reject on the i.i.d. arm ($9.2\%$)" with $t_7$ innovations. At $\nu = 7$ the regenerated rate is 5.8%, Wilson $[4.51, 7.43]\%$: the interval excludes the printed 9.2% and contains the 5% nominal level. At 1000 streams the standard error of a rate near 5% is 0.0069, so 9.2% lies six standard errors from nominal and the experiment has the resolution to exclude it. Over-rejection is found at $\nu = 5$ (8.8%) and $\nu = 6$ (7.9%), neither of which v87 runs. What is contradicted is the over-rejection at the arm the text defines, and not the whitening property, not the exactness of the Concept threshold, and no proposition of v87. |
| `R02b-iid-arm-rejection`            | L278                                                             | The manuscript attributes the i.i.d. arm Ljung-Box over-rejection at $t_7$ to the loss of the fourth moment of $\varepsilon_t^2$. For an i.i.d. tested series the limit requires only that the tested series have a finite variance, i.e. $\mathbb{E}[\varepsilon_t^4] < \infty$, i.e. $\nu > 4$, which $t_7$ satisfies (`R02b_rejection_vs_nu.csv` :: `contains_nominal_squared`, row nu=7 = True). The moment absent at $\nu \le 8$ is $\mathbb{E}[\varepsilon_t^8]$, and that account is refuted by its own control: it is absent at $\nu=7$ too, where the rate is calibrated at every horizon to $n = 1.28\times10^5$. What is contradicted is the stated reason the $\chi^2$ approximation fails, and not the whitening property, not the exactness of the Concept threshold, and no proposition of v87. The true mechanism is not identified: the boundary is located between $\nu=6$ and $\nu=7$, and locating it is not establishing it. |
| `R04-gamma-grid-defect` | Section 4 (Table 3 and family control) | The submitted campaign's Gamma grid had collapsed to a single point through a parameter-order defect. Consequently, the Recalib arm is published as running 2 to 19x behind the first-order arms (it runs 7 to 81x behind across the genuinely spanned grid), and the family-control false-alarm levels are published as flat across Gamma (they spread over 49 points for CUSUM and 24 points for ADWIN). The contradiction touches the magnitude of the Recalib penalty and the flatness of the family controls; it does not touch the Recalib blind zone, the Gaussian ceiling pi/2, the location of the efficiency crossing or the cost of the parametric route, which R04b owns, or any proposition of v87. |
| `R04b-efficiency-crossing` | L57 (abstract), L253, L372 (conclusion), L519 (Figure 4 caption) | The Eco-L1 efficiency crossing is published at one location, nu* ~ 4.9. Every regenerated estimator on the refined twelve-point grid places it higher and the inferential bracket excludes it entirely: bracket [7.0, 9.0], shape fit 8.10 [7.78, 8.37], grid bracket [7.0, 8.0] (`R04b_ratio_vs_nu.csv` :: `ratio`). The `8.52` this repository's own earlier R04 audit reported is not a competing measurement and is not counted here: it was a two-point interpolation across an unsampled interval, is carried at D2, and contradicts no printed numeral. What is contradicted is the location of the crossing, and not the whitening property, not the exactness of the Concept threshold, not the analytic crossing at 4.6788, not the absence of a second crossing above nu = 7, and no proposition of v87, whose asymptotic statement rests on the analytic root reproduced here at D0. |
| `R04b-estimation-cost` | L253 | The finite warm-up is published as costing 0.3 degrees of freedom. Three independent routes over the refined grid put it an order of magnitude higher and no interval among them reaches 0.3: 3.62 [3.31, 3.92] by the shape fit, 3.22 [2.52, 3.82] model-free, and the outer bound [2.0, 5.0]. They are three D3 rows of one audit and one contradiction, not three. What is contradicted is the cost of the parametric route, and not the whitening property, not the exactness of the Concept threshold, and no proposition. |
| `R07-bias-bound-not-a-bound` | L308 | L308 states that the classical small-sample AR bias `E[phi_hat] - phi approx -2.5 phi/n` stays under 2.9 x 10^-3 across the full 7 x 4 grid. It does not: the largest absolute bias over the 28 diagnostic cells is 3.1268677 x 10^-3 at phi = 0.15 and n_ols = 125, 1.44 standard errors past the printed bound and at the corner the printed formula itself designates (`R07_estmean_diagnostics.csv` :: `bias_phi_hat`). The falsification is confined to the numeral and to the words "stays under": it does not touch the ordering of the channels, Figure 7 panel A or panel B, neither of which plots the bias, the OLS-versus-ORACLE false-alarm comparison, or the lattice law. |
| `R08-delivered-level-above-nominal` | L241 and its footnote | The text selects "the nearest attainable level at or below nominal" and its own footnote makes the implemented test the weak comparison operator, whose level at the selected threshold is above nominal, while the level reported is the strict one. The null law itself remains exact and free of nuisance parameters; what is contradicted is the selection rule and the level reported, not the exactness result. |
| `R16-dating-misdescription` | L329 | The census is described as a multi-scale Pagan-Sossounov bull/bear dating of the four streams. Strict Pagan-Sossounov yields 48 phases, not 66: the canonical census reaches 66 by substituting Lunde-Timmermann for SPY alone when `check_sanity` fails. The falsification touches the dating description only; it does not affect the 80% headline, which is computed from the canonical census that does reach 66 phases and 53 out of budget at gamma=20. |
| `R17-eco-l1-arm-identity` | L341 and Table 1 at tex line 117 | A false-alarm figure is attributed to the arm Table 1 defines as the level residual, while the cell that produced it monitors the squared standardized residual, the arm the source script itself names differently. The false-alarm numerals only; the persistence median is arm-agnostic because the fit is shared. |

### 6.2 Printed numerals that move

Every stream was redrawn under 128-bit entropy keys, so Monte-Carlo values move. Each is classified D0 to D3 at the manuscript's own printing precision, with its source CSV cell, in [`docs/DEVIATIONS.md`](docs/DEVIATIONS.md). No qualitative claim of the paper is falsified by any of them.

### 6.3 A limitation we report against ourselves, contradicting nothing

**R18 — Power of the Ljung-Box test.** The Ljung-Box non-rejections reported in the manuscript are exact and the reported rates are correct. What R18 establishes is the strength of the evidence they carry: at the operating point behind those tests, the largest autocorrelation measured on the streams themselves is a small fraction of the amplitude the test detects with 80% power, where the instrument's power equals its own size. The non-rejections therefore exclude autocorrelation above that amplitude and exclude nothing below it. The theoretical result remains the guarantee of the whitening property. We report this because a reader is entitled to know what a non-rejection is worth, not because anything printed is wrong.

---
## EXPERIMENT REPORTS

EOF

# 2. Sequential concatenation of the per-stream sections
cat README_preamble.md $(ls docs/sections/R*.md | sort -V) > README.md

echo "Root README.md generated: $(wc -l < README.md) lines, $(ls docs/sections/R*.md | wc -l) sections."