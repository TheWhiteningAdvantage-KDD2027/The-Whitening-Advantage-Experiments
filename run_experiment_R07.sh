#!/usr/bin/env bash
set -euo pipefail

# 1. STRICT DETERMINISM: Force single-threaded linear algebra BEFORE python starts
export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export OPENBLAS_NUM_THREADS="1"
export NUMEXPR_NUM_THREADS="1"
export VECLIB_MAXIMUM_THREADS="1"

# 2. SEED INJECTION: read by the interpreter at start-up, inert if set later.
#    The R07 script stops if the shell has not exported it.
export PYTHONHASHSEED="42"

# 3. MKL COMPATIBILITY: Neutralize instruction set divergence
export MKL_CBWR="COMPATIBLE"

# Every argument is forwarded. The only option the script accepts is --n-jobs,
echo "[R07] Orchestrating estimated conditional mean pipeline: AR(1)-GARCH parameter grid evaluation..."
python3 experiments/R07_estimated_mean/exp_R07_estimated_mean.py "$@"
echo "[R07] Execution completed."
