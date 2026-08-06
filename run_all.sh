#!/usr/bin/env bash
# Master orchestrator. Experiments are discovered by sorted enumeration so that
# no per-experiment instance ever needs to edit this shared file.
set -euo pipefail

echo "Starting complete pipeline..."
shopt -s nullglob
# Only canonical orchestrators are eligible: run_experiment_R<NN>.sh, nothing else.
# A stale variant left in the working tree would otherwise be executed as if it
# were an experiment, and would abort the whole chain under `set -e`.
scripts=()
for candidate in ./run_experiment_R*.sh; do
    # Canonical form is run_experiment_R<NN>.sh, optionally followed by a single
    # lowercase letter for a supplementary experiment attached to that stream
    # (R02b, R02c, R04b). The earlier pattern omitted the suffix and silently
    # excluded every supplementary experiment from the full pipeline.
    if [[ "$(basename "${candidate}")" =~ ^run_experiment_R[0-9]{2}[a-z]?\.sh$ ]]; then
        scripts+=("${candidate}")
    else
        echo "Skipping non-canonical orchestrator: ${candidate}" >&2
    fi
done
if [ ${#scripts[@]} -eq 0 ]; then
    echo "No canonical run_experiment_R<NN>.sh found." >&2
    exit 1
fi
for script in $(printf '%s\n' "${scripts[@]}" | sort -V); do
    echo "--- ${script} ---"
    chmod +x "${script}"
    "${script}"
done
./run_tests.sh
echo "All executions completed."