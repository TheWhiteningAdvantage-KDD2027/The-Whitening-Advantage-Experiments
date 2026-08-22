# Stream Deviations Registry

This document records all numerical deviations between the deterministic compliant pipeline and the submitted manuscript values, classified according to the D0-D3 scale defined in the reproducibility protocol.

---

## R01 — Real World Backtest

**Deviation Class: D0**

**Affected Metrics:** GARCH(1,1) QMLE parameters (omega, sigma_unc), COVID-19 trajectory peaks (Data pipeline only)

**Root Cause:** Floating-point associativity changes when BLAS thread counts are pinned to 1 in the compliant deterministic pipeline versus the multithreaded BLAS environment used in the submitted campaign.

**Mechanism:** Summation order in vectorized reductions (variance computation, GARCH likelihood) becomes a function of the thread scheduler under multithreaded BLAS. The compliant pipeline eliminates this non-determinism by enforcing single-threaded execution, resulting in ULP-level differences in reduction results.

**Quantitative Impact:**
- omega (SPY): Manuscript value 5.1751719325974024e-06 vs compliant 5.1751719325973652e-06 (relative difference: 6.8e-17)
- sigma_unc (SPY): Manuscript value 0.00933654472777823 vs compliant 0.0093365447277781975 (relative difference: 3.4e-17)
- COVID-19 Data peak: Manuscript value 0.37192244808245406 vs compliant 0.3719224480824543 (8 ULP difference, within 16-ULP budget)
- COVID-19 Concept peak: Bit-identical (0 ULP difference)

**Published Precision Impact:** NONE. All affected values, when rounded to the precision presented in the manuscript (typically 1-2 decimal places for gamma_hat, 2 decimal places for p-values), are identical between the submitted campaign and the compliant pipeline.

**Qualitative Claim Impact:** NONE. All qualitative claims (detection/non-detection, relative magnitudes, convergence properties) are preserved.

**Verification:** All R01 tests pass with tolerance budgets set from the largest observed drift (1e-13 relative tolerance for omega/sigma_unc, 16 ULP for trajectory peaks).

**Candidate Files:** See `docs/camera_ready_candidates/R01_v87_garch_calibration.md` for LaTeX macro diff blocks.

**Status:** CERTIFIED — D0 deviation documented and bounded. No manuscript changes required at published precision.
