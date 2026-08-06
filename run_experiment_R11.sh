#!/usr/bin/env bash
# Orchestrator - R11 Multi-detector generalization (v87 Figures 11 and 15)
set -e

# 1. STRICT DETERMINISM: Force single-threaded linear algebra BEFORE python starts
export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export OPENBLAS_NUM_THREADS="1"
export NUMEXPR_NUM_THREADS="1"
export VECLIB_MAXIMUM_THREADS="1"

# 2. SEED INJECTION: read by the interpreter at start-up, inert if set later.
#    The submitted script never pinned it at all; exp_R11_multi_detector.py
#    verifies it here and stops if the shell has not exported it.
export PYTHONHASHSEED="42"

# 3. MKL COMPATIBILITY: Neutralize instruction set divergence
export MKL_CBWR="COMPATIBLE"

echo "[R11] Multi-detector generalization: 20 Gamma x 5 detectors x 2 onset conventions..."
python3 experiments/R11_multi_detector/exp_R11_multi_detector.py "$@"
echo "[R11] Execution completed successfully."
