#!/usr/bin/env bash
# Orchestrator - R18 Power of the Ljung-Box test on a binary stream.
# R18 reproduces no v87 figure, table or number: it bounds what the manuscript's
# Ljung-Box non-rejections exclude. This script never calls pytest; the test
# suite is the exclusive remit of run_tests.sh.
set -e

# 1. STRICT DETERMINISM: Force single-threaded linear algebra BEFORE python starts
export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export OPENBLAS_NUM_THREADS="1"
export NUMEXPR_NUM_THREADS="1"
export VECLIB_MAXIMUM_THREADS="1"

# 2. SEED INJECTION: read by the interpreter at start-up, inert if set later.
#    exp_R18_ljungbox_power.py stops if the shell has not exported it.
export PYTHONHASHSEED="42"

# 3. MKL COMPATIBILITY: Neutralize instruction set divergence
export MKL_CBWR="COMPATIBLE"

echo "[R18] Ljung-Box power: 36 amplitudes x 4 horizons x 1000 streams, plus both application arms..."
python3 experiments/R18_ljungbox_power/exp_R18_ljungbox_power.py "$@"
echo "[R18] Execution completed."
