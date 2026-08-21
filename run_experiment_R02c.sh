#!/bin/bash
# FAIR HARNESS - Strict single-threaded initialisation
export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export OPENBLAS_NUM_THREADS="1"
export PYTHONHASHSEED="42"
export MKL_CBWR="COMPATIBLE"

mkdir -p logs/R02c_horizon_sweep
python experiments/R02c_horizon_sweep/exp_R02c_horizon_sweep.py --n-jobs 1