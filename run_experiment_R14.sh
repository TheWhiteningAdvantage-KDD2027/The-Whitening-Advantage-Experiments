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

echo "[R14] Crypto iso-FPR race: migrated arm (128-bit re-keying)..."
python3 experiments/R14_crypto_isofpr/exp_R14_crypto_isofpr.py "$@"

echo "[R14] Crypto iso-FPR race: legacy-seed port-fidelity diagnostic (certifies no v87 value)..."
python3 experiments/R14_crypto_isofpr/exp_R14_crypto_isofpr.py --legacy-seeds "$@"

echo "[R14] Execution completed."
