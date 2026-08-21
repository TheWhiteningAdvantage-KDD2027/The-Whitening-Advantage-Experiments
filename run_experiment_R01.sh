#!/usr/bin/env bash
# Default path replays the published analysis from the versioned derived series,
# which requires no proprietary raw data. Pass --stage all to re-ingest the raw
# FirstRate tapes when they are available locally.
set -euo pipefail
export PYTHONHASHSEED=42
export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export OPENBLAS_NUM_THREADS="1"
export MKL_CBWR="COMPATIBLE"

DATA_SOURCE="firstrate"
STAGE="analyse"
LEGACY_BLAS=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --data-source)
      if [[ $# -lt 2 ]]; then echo "Error: --data-source requires an argument." >&2; exit 1; fi
      DATA_SOURCE="$2"
      shift 2
      ;;
    --stage)
      if [[ $# -lt 2 ]]; then echo "Error: --stage requires an argument." >&2; exit 1; fi
      STAGE="$2"
      shift 2
      ;;
    --legacy-blas)
      LEGACY_BLAS=true
      shift 1
      ;;
    ingest|analyse|all)
      STAGE="$1"
      shift 1
      ;;
    firstrate|yfinance)
      DATA_SOURCE="$1"
      shift 1
      ;;
    *)
      echo "Error: Unknown argument '$1'" >&2
      exit 1
      ;;
  esac
done

# Dynamic construction of Python arguments
PYTHON_ARGS=(
  --data-source "${DATA_SOURCE}"
  --stage "${STAGE}"
)

if [[ "${LEGACY_BLAS}" == "true" ]]; then
  PYTHON_ARGS+=(--legacy-blas)
fi

echo "Executing R01: Real World Backtest (data-source=${DATA_SOURCE}, stage=${STAGE}, legacy-blas=${LEGACY_BLAS})"
python experiments/R01_real_world_backtest/exp_R01_real_world_backtest.py "${PYTHON_ARGS[@]}"
echo "R01 Execution Completed."
