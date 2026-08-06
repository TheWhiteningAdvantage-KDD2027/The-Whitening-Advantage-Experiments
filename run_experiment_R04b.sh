#!/usr/bin/env bash
# Orchestrator - R04b Resolution of the efficiency crossing point (Appendix Figure A3)
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

echo "[R04b] Refining the nu grid (12 points, 3 arms, N=2000 streams per pass)..."
python3 experiments/R04b_nu_refinement/exp_R04b_nu_refinement.py "$@"
echo "[R04b] Execution completed successfully."
