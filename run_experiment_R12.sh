#!/usr/bin/env bash
set -euo pipefail

# 1. STRICT DETERMINISM: Force single-threaded linear algebra BEFORE python starts
export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export OPENBLAS_NUM_THREADS="1"
export NUMEXPR_NUM_THREADS="1"
export VECLIB_MAXIMUM_THREADS="1"

# 2. SEED INJECTION: read by the interpreter at start-up, inert if set later.
#    The R12 script stops if the shell has not exported it.
export PYTHONHASHSEED="42"

# 3. MKL COMPATIBILITY: Neutralize instruction set divergence
export MKL_CBWR="COMPATIBLE"

# Every argument is forwarded. The only option the script accepts is --n-jobs,
# and every stream is keyed on its role and index alone with fixed chunk
# boundaries, so the output does not depend on it: `./run_experiment_R12.sh
# --n-jobs <k>` is the second reproducibility axis of control C7 and must produce
# byte-identical artefacts.
echo "[R12] GJR leverage misspecification and Student-t moment singularity..."
python3 experiments/R12_gjr_student/exp_R12_gjr_student.py "$@"
echo "[R12] Execution completed."
