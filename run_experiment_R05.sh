#!/usr/bin/env bash
# Orchestrator - R05 Scale law and location/scale orthogonality (Figure 5, Appendix B)
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

# The three steps run inside ONE interpreter, driven by step c. Steps a and b
# are libraries as well as entry points: step c calls them, receives their
# frames in memory, and builds the figure and the macros from those objects.
# Launching them as three separate processes would force step c to reload the
# CSVs the earlier steps had just written, which SPECS 1.6 forbids -- a CSV is
# a final medium of diffusion, never a bridge between two stages of one
# computation. Each step still writes its own CSV deliverable and its own log
# under logs/R05_scale_law/; nothing reads them back.
#
# Chain, in order: step a (abrupt shift + Concept positive control), step b at
# budget 2e5, step b at budget 3e6 with the lambda_iid horizon ladder, step c
# (Figure 5, Appendix B numbers, LaTeX macros, deviation classification).
echo "[R05] Running the scale-law chain: abrupt shift, ramps at H=2e5 and H=3e6, figure and macros..."
echo "[R05] The 3e6 budget dominates the cost; expect roughly one hour in total."
python3 experiments/R05_scale_law/exp_R05_scale_law_c.py "$@"
echo "[R05] Execution completed successfully."
