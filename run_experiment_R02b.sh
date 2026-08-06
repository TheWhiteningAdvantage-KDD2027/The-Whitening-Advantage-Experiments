#!/bin/bash
# FAIR HARNESS - Strict initialisation
export PYTHONHASHSEED=42

# Ensure the log and output directories exist locally prior to parallel writes
mkdir -p logs/R02b_iid_arm_resolution

# Dispatching payload with 4 parallel cores
python experiments/R02b_iid_arm_resolution/exp_R02b_iid_arm_resolution.py --n-jobs 4