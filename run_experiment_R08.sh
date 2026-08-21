#!/usr/bin/env bash
# Orchestrator - R08 The adverse direction and the discrete null law (v87 Figure 8, L241, L311).
# Two-stage chain: _a runs the two modules -- 10,000 trajectories of the injected-bias
# campaign and 2x10^5 fair-coin streams of the lattice null law -- and writes the
# five CSVs; _b renders fig:adverse and emits the LaTeX macros. _b re-runs the
# campaign in memory rather than reloading a CSV, because preamble S7 forbids a
# disk round trip as a memory bridge and the delivered Priorite_21c did exactly
# that, so the two stages together cost twice one campaign.
# This script never calls pytest; the test suite is the exclusive remit of
# run_tests.sh.
set -e

# 1. STRICT DETERMINISM: Force single-threaded linear algebra BEFORE python starts
export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export OPENBLAS_NUM_THREADS="1"
export NUMEXPR_NUM_THREADS="1"
export VECLIB_MAXIMUM_THREADS="1"

# 2. SEED INJECTION: read by the interpreter at start-up, inert if set later.
#    Both R08 scripts stop if the shell has not exported it.
export PYTHONHASHSEED="42"

# 3. MKL COMPATIBILITY: Neutralize instruction set divergence
export MKL_CBWR="COMPATIBLE"

# Every argument is forwarded to both stages. The two options either accepts are
# --n-jobs and --fast. Every task is keyed on its role and index alone and the
# chunk boundaries are fixed constants, so the output does not depend on the
# worker count: `./run_experiment_R08.sh --n-jobs 1` is the second
# reproducibility axis of control C8 and must produce byte-identical artefacts.
# `--fast` is a degraded path and stamps every artefact it writes with `_fast`.
echo "[R08] Adverse direction and discrete null law: injected-bias campaign and lattice null law..."
python3 experiments/R08_adverse_lattice/exp_R08_adverse_lattice_a.py "$@"
python3 experiments/R08_adverse_lattice/exp_R08_adverse_lattice_b.py "$@"
echo "[R08] Execution completed."
