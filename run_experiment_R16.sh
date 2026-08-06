#!/usr/bin/env bash
# Orchestrator - R16 Regime census and sign floor.
# Two-stage chain: _a dates the phases of SPY, PFF, VNQ and BWX over 2000-2025
# and writes the census; _b prices the two detection floors, the feasibility
# grid and the LaTeX macros. Neither renders a figure: v87's census paragraphs
# L329 and L331 reference only fig:oracle_frontier, which belongs to R01.
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
#    Both R16 scripts stop if the shell has not exported it. R16 draws no random
#    number anywhere, so this pins string hashing and nothing else; the absence
#    of a stochastic surface is logged rather than papered over with an unused
#    seed helper.
export PYTHONHASHSEED="42"

# 3. MKL COMPATIBILITY: Neutralize instruction set divergence
export MKL_CBWR="COMPATIBLE"

# _a runs with NO FLAGS, which is the canonical 66-phase configuration, and in
# that mode it also writes the two stamped counterfactual censuses that price
# the dating deviation. Do not add --dating here: a single-arm invocation writes
# that arm only, and is the arm-isolation axis of control C9.
echo "[R16] Regime census: dating four ETF streams, three arms, then the sign floor..."
python3 experiments/R16_regime_census/exp_R16_regime_census_a.py
python3 experiments/R16_regime_census/exp_R16_regime_census_b.py
echo "[R16] Execution completed."
