#!/usr/bin/env bash
set -euo pipefail

# 1. STRICT DETERMINISM: Force single-threaded linear algebra BEFORE python starts
export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export OPENBLAS_NUM_THREADS="1"
export NUMEXPR_NUM_THREADS="1"
export VECLIB_MAXIMUM_THREADS="1"

# 2. SEED INJECTION: read by the interpreter at start-up, inert if set later.
#    Both R15 scripts stop if the shell has not exported it.
export PYTHONHASHSEED="42"

# 3. MKL COMPATIBILITY: Neutralize instruction set divergence
export MKL_CBWR="COMPATIBLE"

# Every argument is forwarded to both stages. The only options either accepts are
# --n-jobs, --data-source and --stage, and the campaign is keyed per task with
# `executor.map` in submission order, so no output depends on --n-jobs:
# `./run_experiment_R15.sh --n-jobs 1` is the second reproducibility axis of
# control C10 and must produce byte-identical artefacts.
echo "[R15] Panel provenance and the public equity fetcher (offline stage)..."
python3 experiments/R15_cross_sectional/exp_R15_cross_sectional_a.py "$@"

echo "[R15] Cross-sectional escape: calibration, H1 race, COVID control, figure, macros..."
python3 experiments/R15_cross_sectional/exp_R15_cross_sectional_b.py "$@"

echo "[R15] Cross-sectional escape: witness-BLAS attribution arm (certifies no v87 value)..."
python3 experiments/R15_cross_sectional/exp_R15_cross_sectional_b.py --witness-blas "$@"

echo "[R15] Execution completed."
