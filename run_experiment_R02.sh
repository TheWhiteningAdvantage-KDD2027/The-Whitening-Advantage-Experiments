#!/usr/bin/env bash
set -e

export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export OPENBLAS_NUM_THREADS="1"
export PYTHONHASHSEED="42"
export MKL_CBWR="COMPATIBLE"

echo "=== Launching Experiment R02: Whitening Ljung-Box ==="
python experiments/R02_whitening_ljungbox/exp_R02_whitening_ljungbox.py --n-jobs 1

# The test suite is invoked exclusively by run_tests.sh, never from an
# individual experiment orchestrator.
echo "=== R02 Execution Completed ==="