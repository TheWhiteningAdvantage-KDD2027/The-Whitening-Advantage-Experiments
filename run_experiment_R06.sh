#!/usr/bin/env bash
# Orchestrator - R06 Empirical validity map of the whitening property (Figure 6)
set -e

# 1. STRICT DETERMINISM: Force single-threaded linear algebra BEFORE python starts
export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export OPENBLAS_NUM_THREADS="1"
export NUMEXPR_NUM_THREADS="1"
export VECLIB_MAXIMUM_THREADS="1"

# 2. SEED INJECTION: read by the interpreter at start-up, inert if set later.
#    The submitted script assigned this from inside the interpreter, where it has
#    no effect at all; only the shell can pin it.
export PYTHONHASHSEED="42"

# 3. MKL COMPATIBILITY: Neutralize instruction set divergence
export MKL_CBWR="COMPATIBLE"

echo "[R06] Mapping the whitening validity boundaries (13 Gamma + 5 task cells + counterfactual arm)..."
python3 experiments/R06_validity_map/exp_R06_validity_map.py "$@"
echo "[R06] Execution completed successfully."
