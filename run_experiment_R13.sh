#!/usr/bin/env bash
set -euo pipefail

# 1. STRICT DETERMINISM: Force single-threaded linear algebra BEFORE python starts
export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export OPENBLAS_NUM_THREADS="1"
export NUMEXPR_NUM_THREADS="1"
export VECLIB_MAXIMUM_THREADS="1"

# 2. SEED INJECTION: read by the interpreter at start-up, inert if set later.
#    Both R13 scripts stop if the shell has not exported it.
export PYTHONHASHSEED="42"

# 3. MKL COMPATIBILITY: Neutralize instruction set divergence
export MKL_CBWR="COMPATIBLE"

# Every argument is forwarded to both stages. The only option either accepts is
# --n-jobs, and the campaign is keyed per episode so its output does not depend
# on it: `./run_experiment_R13.sh --n-jobs 1` is the second reproducibility axis
# of control C8 and must produce byte-identical artefacts.
echo "[R13] Oracle ceiling: look-ahead GARCH oracle campaign on four SPY episodes..."
python3 experiments/R13_oracle_ceiling/exp_R13_oracle_ceiling_a.py "$@"
python3 experiments/R13_oracle_ceiling/exp_R13_oracle_ceiling_b.py "$@"
# Combine the two stage logs into a single file for compatibility with the verification gate
cat logs/R13_oracle_ceiling/exp_R13_oracle_ceiling_a.log logs/R13_oracle_ceiling/exp_R13_oracle_ceiling_b.log > logs/R13_oracle_ceiling/exp_R13_oracle_ceiling.log
echo "[R13] Execution completed."
