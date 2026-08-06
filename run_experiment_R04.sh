#!/usr/bin/env bash
# Orchestrator - R04 Iso-FPR race and relative efficiency (Figure 4, Table 3)
set -e

# 1. STRICT DETERMINISM: Force single-threaded linear algebra BEFORE python starts
export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export OPENBLAS_NUM_THREADS="1"
export NUMEXPR_NUM_THREADS="1"
export VECLIB_MAXIMUM_THREADS="1"

# 2. SEED INJECTION: read by the interpreter at start-up, inert if set later
export PYTHONHASHSEED="42"

# 3. MKL COMPATIBILITY: Neutralize instruction set divergence
export MKL_CBWR="COMPATIBLE"

echo "[R04] Running iso-FPR race (N=2000 null streams, 4 arms)..."
python3 experiments/R04_isofpr_race/exp_R04_isofpr_race.py "$@"
echo "[R04] Execution completed successfully."
