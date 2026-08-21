#!/usr/bin/env bash
set -euo pipefail

# 1. STRICT DETERMINISM: Force single-threaded linear algebra BEFORE python starts
export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export OPENBLAS_NUM_THREADS="1"
export NUMEXPR_NUM_THREADS="1"
export VECLIB_MAXIMUM_THREADS="1"

# 2. SEED INJECTION: read by the interpreter at start-up, inert if set later.
#    The R09 script stops if the shell has not exported it.
export PYTHONHASHSEED="42"

# 3. MKL COMPATIBILITY: Neutralize instruction set divergence
export MKL_CBWR="COMPATIBLE"

# `--control-arms ecusum` is passed EXPLICITLY, so the certified run produces
# results/R09_eprocess_anytime/data/R09_eprocess_race_control_ecusum.csv. The
# flag governs what is COMPUTED, not merely what is persisted, and the branch is
# stamped in the filename and in the `arm` column (preamble S4.3). The control
# arm recurses on the same per-chunk y_t and consumes no additional randomness,
# so a run WITHOUT the flag must produce byte-identical published CSVs: that is
# the third reproducibility axis of control C6.
#
# Every further argument is forwarded. The only other option the script accepts
# is --n-jobs, and NUM_CHUNKS is fixed at 10, so the chunk decomposition -- and
# therefore every output -- is independent of it: `./run_experiment_R09.sh
# --n-jobs 1` is the second reproducibility axis of control C6 and must produce
# byte-identical artefacts.
echo "[R09] Anytime-valid detection: mixture martingale against fixed-horizon CUSUM on the fair-coin stream..."
python3 experiments/R09_eprocess_anytime/exp_R09_eprocess_anytime.py --control-arms ecusum "$@"
echo "[R09] Execution completed."
