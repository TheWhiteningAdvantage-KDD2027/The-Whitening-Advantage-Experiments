#!/bin/bash
# FAIR HARNESS - Strict initialisation
export PYTHONHASHSEED=42

mkdir -p logs/R02c_horizon_sweep
python experiments/R02c_horizon_sweep/exp_R02c_horizon_sweep.py --n-jobs 4