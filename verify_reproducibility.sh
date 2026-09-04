#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# DETERMINISTIC ENVIRONMENT CONFIGURATION & RUNTIME SPECIFICATION (PER README §3)
# ==============================================================================
export PYTHONHASHSEED=42
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export MKL_CBWR=COMPATIBLE
export SOURCE_DATE_EPOCH=1700000000
export LC_ALL=C

REPO_DIR="/home/m53/The-Whitening-Advantage-Experiments"
cd "$REPO_DIR"

echo "=== [ STAGE 1/5 ] Verifying repository integrity and execution environment ==="
if [ ! -f "run_all.sh" ]; then
    echo "ERROR: run_all.sh could not be located in $REPO_DIR" >&2
    exit 1
fi
chmod +x run_all.sh

# Purge transient artifacts from preceding experimental evaluations
rm -rf results_run1 results_run2 manifest_run1.sha256 manifest_run2.sha256 results_diff.patch

# ==============================================================================
# RUN #1: PIPELINE EXECUTION AND BASELINE CRYPTOGRAPHIC MANIFEST GENERATION
# ==============================================================================
echo "=== [ STAGE 2/5 ] Initiating RUN #1 (Artifact purge + pipeline execution) ==="
find results/ -mindepth 1 -delete

./run_all.sh 2>&1 | tee logs/double_run_1.log

if [ ! -d "results" ] || [ -z "$(ls -A results)" ]; then
    echo "ERROR: Directory results/ is unpopulated following RUN #1." >&2
    exit 1
fi

echo "Archiving baseline output hierarchy: results/ -> results_run1/..."
cp -a results results_run1

echo "Generating cryptographic manifest via SHA-256 (Run #1)..."
(cd results_run1 && find . -type f -exec sha256sum {} + | LC_ALL=C sort -k2) > manifest_run1.sha256
echo "Run #1 complete: $(wc -l < manifest_run1.sha256) files indexed."

# ==============================================================================
# RUN #2: ARTIFACT PURGE AND INDEPENDENT RE-EXECUTION
# ==============================================================================
echo "=== [ STAGE 3/5 ] Initiating RUN #2 (Artifact purge + pipeline execution) ==="
find results/ -mindepth 1 -delete

./run_all.sh 2>&1 | tee logs/double_run_2.log

if [ ! -d "results" ] || [ -z "$(ls -A results)" ]; then
    echo "ERROR: Directory results/ is unpopulated following RUN #2." >&2
    exit 1
fi

echo "Archiving replicated output hierarchy: results/ -> results_run2/..."
cp -a results results_run2

echo "Generating cryptographic manifest via SHA-256 (Run #2)..."
(cd results_run2 && find . -type f -exec sha256sum {} + | LC_ALL=C sort -k2) > manifest_run2.sha256
echo "Run #2 complete: $(wc -l < manifest_run2.sha256) files indexed."

# ==============================================================================
# RIGOROUS DIFFERENTIAL VERIFICATION AND DETERMINISM EVALUATION
# ==============================================================================
echo "=== [ STAGE 4/5 ] Differential comparison of cryptographic manifests ==="
if diff -u manifest_run1.sha256 manifest_run2.sha256 > results_diff.patch; then
    echo "======================================================================"
    echo "VERIFICATION SUCCESS: End-to-end bitwise reproducibility confirmed."
    echo "The results/ hierarchy generates 100% identical SHA-256 digests."
    echo "======================================================================"
    rm -rf results_run1 results_run2 manifest_run1.sha256 manifest_run2.sha256 results_diff.patch
    exit 0
else
    echo "======================================================================" >&2
    echo "VERIFICATION FAILURE: Cryptographic divergence detected between runs!" >&2
    echo "Inspect differential patch artifact: $REPO_DIR/results_diff.patch" >&2
    echo "======================================================================" >&2
    exit 1
fi