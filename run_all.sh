#!/usr/bin/env bash
# Master orchestrator. Experiments are discovered by sorted enumeration so that
# no per-experiment instance ever needs to edit this shared file.
set -euo pipefail

echo "Starting complete pipeline in strict topological order..."

# The execution order resolves the data dependency DAG between streams,
# rather than alphabetical sorting. For example, R08 requires files from R10,
# and R13 requires files from R16.
ORDERED_STREAMS=(
  "R01"
  "R02"
  "R02b"
  "R02c"
  "R03"
  "R04"
  "R04b"
  "R05"
  "R06"
  "R07"
  "R09"
  "R11"
  "R12"
  "R14"
  "R15"
  "R16"
  "R13"
  "R17"
  "R18"
  "R10"
  "R08"
)

for stream_id in "${ORDERED_STREAMS[@]}"; do
    script="./run_experiment_${stream_id}.sh"
    if [[ ! -f "${script}" ]]; then
        echo "[!] ERROR: Required orchestrator ${script} not found." >&2
        exit 1
    fi
    echo "--- ${script} ---"
    chmod +x "${script}"
    "${script}"
done

./run_tests.sh
echo "All executions completed."