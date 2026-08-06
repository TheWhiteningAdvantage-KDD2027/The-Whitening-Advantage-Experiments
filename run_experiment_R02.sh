#!/usr/bin/env bash
set -e

export PYTHONHASHSEED=42

echo "=== Launching Experiment R02: Whitening Ljung-Box ==="
python experiments/R02_whitening_ljungbox/exp_R02_whitening_ljungbox.py --n-jobs 4

# The test suite is invoked exclusively by run_tests.sh, never from an
# individual experiment orchestrator.
echo "=== R02 Execution Completed ==="