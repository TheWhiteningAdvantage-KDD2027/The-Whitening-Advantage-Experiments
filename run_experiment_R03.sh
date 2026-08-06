#!/usr/bin/env bash
# Auto-generated Orchestrator - R03 FPR Explosion
set -e

# 1. STRICT DETERMINISM: Force single-threaded linear algebra BEFORE python starts
export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export OPENBLAS_NUM_THREADS="1"
export NUMEXPR_NUM_THREADS="1"
export VECLIB_MAXIMUM_THREADS="1"

# 2. SEED INJECTION: Essential for hash stringification stability
export PYTHONHASHSEED="42"

# 3. MKL COMPATIBILITY: Neutralize instruction set divergence
export MKL_CBWR="COMPATIBLE"

echo "[R03] Running FPR Explosion experiments (N=300)..."
python3 experiments/R03_fpr_explosion/exp_R03_fpr_explosion.py "$@"
echo "[R03] Execution completed successfully."