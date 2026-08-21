#!/usr/bin/env bash
set -euo pipefail

# 1. STRICT DETERMINISM: Force single-threaded linear algebra BEFORE python starts
export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export OPENBLAS_NUM_THREADS="1"
export NUMEXPR_NUM_THREADS="1"
export VECLIB_MAXIMUM_THREADS="1"

# 2. SEED INJECTION: read by the interpreter at start-up, inert if set later.
#    The script stops if the shell has not exported it.
export PYTHONHASHSEED="42"

# 3. MKL COMPATIBILITY: Neutralize instruction set divergence
export MKL_CBWR="COMPATIBLE"

echo "[R17] Econometric baseline: SPECS 1.10 arm (tol, ftol, eps, truncation)..."
python3 experiments/R17_econometric_baseline/exp_R17_econometric_baseline.py "$@"

echo "[R17] Econometric baseline: legacy-QMLE attribution arm (certifies no v87 value)..."
python3 experiments/R17_econometric_baseline/exp_R17_econometric_baseline.py --qmle-options legacy "$@"

echo "[R17] Execution completed."
