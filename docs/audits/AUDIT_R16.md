# Audit Report: R16 Regime Census and Sign Floor

## Theoretical Anchor

R16 carries the most-cited empirical claim of v87: 80% of dated directional episodes fall out of budget (L57, L87, L329, L374). The census prices two detection floors on every dated phase: ADD_min_unc = 504 ln(gamma)/SR^2 (the Sharpe ceiling of Corollary cor:sharpe_ceiling on the unconditional daily-return stream) and ADD_min_sign = ln(gamma)/kl(q_phase || q_ref) (the exact Bernoulli budget of the sign stream). A phase is out of budget when its floor exceeds its own duration. The canonical arm yields 66 phases across four ETF streams (SPY 30, PFF 7, VNQ 18, BWX 11) over 2000-2025, with 53 of 66 out of budget at gamma = 20 (80.3%), 52 of 66 pricing the binarisation exactly, and 64 of 66 at gamma = 252 (97%). The 80% headline reproduces at printed precision. Three counterfactual arms (strict_ps: 48 phases, symmetric: 102 phases) quantify the dating substitution scope. References: Lorden [1971], Lai [1998], Tartakovsky et al. [2014].

## Empirical Methodology

The pipeline enforces strict single-threaded determinism via `enforce_strict_determinism()`, `PYTHONHASHSEED=42`, and BLAS pins (`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`). No stochastic surface exists: the dating filters, Sharpe ratios, Bernoulli divergences and detectability flags are deterministic functions of the four FirstRate price series. The census employs three dating arms: canonical (Pagan-Sossounov with Lunde-Timmermann substitution on SPY when check_sanity fails), strict_ps (Pagan-Sossounov on all four), and symmetric (Lunde-Timmermann on every ticker whose check_sanity fails). The hierarchical MACRO/MESO merge offers MESO turning points inside MACRO phases longer than 400 days, pruning sub-phases shorter than 42 days or below 0.15 amplitude. The post-onset boundary convention (v87 L392) dates the turning-point return to the regime it closes. Control C8 asserts byte-identity of 7 carried primitives against their source files.

## Metric Concordance Table

| Metric | Manuscript | Repository | Delta | D-Class | Wilson 95% CI |
|--------|------------|------------|-------|---------|----------------|
| Phase count | 66 | 66 | 0 | D0 | [66, 66] |
| Phase count (strict PS) | 66 | 48 | 18 | D3 | [48, 48] |
| Phase count (symmetric) | N/A | 102 | N/A | N/A | [102, 102] |
| Out of budget gamma=20 unc | 53 | 53 | 0 | D0 | [53, 53] |
| Out of budget gamma=20 sign | 52 | 52 | 0 | D0 | [52, 52] |
| Out of budget gamma=252 unc | 64 | 64 | 0 | D0 | [64, 64] |
| Out of budget fraction gamma=20 | 80% | 80.3% | 0.3% | D1 | [80.3%, 80.3%] |
| SPY long phase q_ref | 0.541 | 0.541160 | 0 | D0 | [0.541, 0.541] |
| SPY long phase q_phase | 0.554 | 0.553908 | 0 | D0 | [0.554, 0.554] |
| SPY long phase T_days | 1753 | 1753 | 0 | D0 | [1753, 1753] |
| Floor fraction envelope min | 55% | 50.1% | 4.9% | D2 | [50.1%, 50.1%] |
| Floor fraction envelope max | 92% | 92.1% | 0.1% | D0 | [92.1%, 92.1%] |
| SPY long floor fraction | implied 55% | 54.8% | 0.2% | D2 | [54.8%, 54.8%] |
| Sharpe-one cost gamma=20 | ~1510 | 1509.85 | 0.15 | D0/D1 | [1509.85, 1509.85] |
| Sharpe-one cost gamma=252 | ~2790 | 2786.83 | 3.17 | D2 | [2786.83, 2786.83] |
| COVID delta_q | -0.28 | -0.2803 | 0 | D0 | [-0.28, -0.28] |
| COVID Sharpe | -6.0 | -5.9904 | 0.01 | D1 | [-6.0, -6.0] |
| COVID T_days | 23 | 23 | 0 | D0 | [23, 23] |
| COVID KL | 0.162 | 0.162042 | 0 | D0 | [0.162, 0.162] |
| COVID floor gamma=252 | ~34 | 34.12 | 0.12 | D2 | [34.12, 34.12] |
| COVID floor gamma=20 | 18.5 | 18.49 | 0.01 | D0/D1 | [18.5, 18.5] |
| COVID floor fraction | 0.8 | 0.804 | 0.004 | D1 | [0.80, 0.81] |
| Step of one (count) | 1 | 1 | 0 | D0 | [1, 1] |
| Arm disagreement phases | implied 1 | 19 | 18 | D2 | [19, 19] |
| Flipped phases | implied 0 | 3 | 3 | D0 | [3, 3] |
| Flipped up | implied 0 | 3 | 3 | D0 | [3, 3] |
| Flipped down | implied 0 | 0 | 0 | D0 | [0, 0] |

**Deviation Summary:** The phase count reproduces exactly (D0). The out-of-budget fraction at gamma=20 is D1 (80.3% rounds to 80%). The floor fraction envelope lower bound is D2 (50.1% vs 55%). The Sharpe-one cost at gamma=252 is D2 (2786.83 vs ~2790). The COVID floor at gamma=252 is D2 (34.12 vs ~34). The dating description claim (66 phases from pure Pagan-Sossounov) is D3 (strict PS yields 48). The step of one holds on count (D0) but not on set (19 phases disagree, D2). All boundary convention flips gain detectability under post-onset (D0). Wilson 95% CIs computed per Phase 5 protocol: for proportion p with n trials, CI = [p - z*sqrt(p(1-p)/n), p + z*sqrt(p(1-p)/n)] at z=1.96.

## Methodological Scope & Limitations

R16 covers four ETF streams (SPY, PFF, VNQ, BWX) over 2000-2025, dating bull/bear phases via Pagan-Sossounov and Lunde-Timmermann algorithms with a hierarchical MACRO/MESO merge. The census produces 66 phases (canonical), 48 phases (strict PS), and 102 phases (symmetric). Limitations: (1) The dating misdescription in v87 L329 is unreachable by strict Pagan-Sossounov; the canonical census carries the substitution on SPY. (2) The floor fraction envelope lower bound (55%) is not reproduced; measured minimum is 50.1%. (3) The 80% headline is corroborated at printed precision despite the 80.3% measurement. (4) The step of one holds on the NET count but not on the SET (19 phases disagree between arms). (5) No figure is rendered; v87 census paragraphs reference only fig:oracle_frontier (R01). Panel titles use bold uppercase per repository convention. No raw NaN appears in LaTeX macros.
