#!/usr/bin/env bash
# ==============================================================================
# Orchestration Pipeline — Autonomous Sequential Stream Refactoring & CI Harness
# The Whitening Advantage Experiments (KDD 2027 Submission Codebase)
# ==============================================================================

set -euo pipefail

# Resolve repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ ! -d "${REPO_ROOT}/experiments" ]]; then
  REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fi
cd "${REPO_ROOT}"

# ------------------------------------------------------------------------------
# 1. Strict Execution Order Definition (Single Source of Truth - SSOT)
# ------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------
# 2. Strict Deterministic Environment Configuration
# ------------------------------------------------------------------------------
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0
export CUBLAS_WORKSPACE_CONFIG=:4096:8
export PYTHONUNBUFFERED=1

# ------------------------------------------------------------------------------
# 3. Command-Line Interface (CLI) Options and Parsing
# ------------------------------------------------------------------------------
TARGET_STREAM=""
RESUME_FROM=""
FIX_FLAG="--fix"
SPAWN_VIBE=false
GENERATE_TASKS=false
DRY_RUN=false
SKIP_EXPERIMENT=false
SKIP_TESTS=false
SKIP_GIT=false

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  -s, --stream <ID>          Execute exclusively the specified research stream (e.g., R13, R02b)
  -r, --resume-from <ID>     Resume ordered sequence starting from specified stream (e.g., R09)
      --spawn-vibe           Launch Mistral Vibe agent in batch mode ('vibe -p') per stream before CI gates
      --generate-tasks       Generate isolated stream task payloads in REFACTORING_PROMPTS/tasks/
      --no-fix               Disable automated self-healing/patching in verify_refactoring.py
      --skip-experiment      Bypass experimental execution stage; run verification audits and test suites only
      --skip-tests           Bypass pytest validation test suite
      --skip-git             Disable intermediate Version Control System (Git) checkpoints
      --dry-run              Display resolved stream pipeline sequence and paths without executing
  -h, --help                 Display this help message and exit
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -s|--stream)
      TARGET_STREAM="$2"
      shift 2
      ;;
    -r|--resume-from)
      RESUME_FROM="$2"
      shift 2
      ;;
    --spawn-vibe)
      SPAWN_VIBE=true
      shift
      ;;
    --generate-tasks)
      GENERATE_TASKS=true
      shift
      ;;
    --no-fix)
      FIX_FLAG=""
      shift
      ;;
    --skip-experiment)
      SKIP_EXPERIMENT=true
      shift
      ;;
    --skip-tests)
      SKIP_TESTS=true
      shift
      ;;
    --skip-git)
      SKIP_GIT=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "[!] Unknown option: $1" >&2
      usage
      ;;
  esac
done

# ------------------------------------------------------------------------------
# 4. Dynamic Resolution & Engine Functions
# ------------------------------------------------------------------------------

# Dynamically resolve stream directory slug on filesystem without heuristics
resolve_stream_slug() {
  local stream_id="$1"
  local matched_dir

  matched_dir=$(find "${REPO_ROOT}/experiments" -mindepth 1 -maxdepth 1 -type d \( -name "${stream_id}_*" -o -name "${stream_id}" \) 2>/dev/null | head -n 1)

  if [[ -n "${matched_dir}" ]]; then
    basename "${matched_dir}"
  else
    echo "${stream_id}"
  fi
}

# Generate lightweight, isolated runtime task payload for Agent execution
generate_stream_task_payload() {
  local stream_id="$1"
  local stream_slug="$2"
  local task_dir="${REPO_ROOT}/REFACTORING_PROMPTS/tasks"
  local task_file="${task_dir}/TASK_${stream_id}.md"

  mkdir -p "${task_dir}"
  cat <<EOF > "${task_file}"
# REFACTORING TASK INVOCATION: STREAM ${stream_id}

- Target Stream ID   : ${stream_id}
- Target Stream Slug : ${stream_slug}
- Target Directory   : experiments/${stream_slug}
- Master Contract    : REFACTORING_PROMPTS/PROMPT_REFACTORING_MISTRAL.md

Execute the 5-phase refactoring lifecycle for ${stream_slug} following .vibe/prompts/ENG_VIBE_REFACTOR_STREAM.md.
EOF
  echo "[+] [Task Generator] Emitted task payload: ${task_file}"
}

# Spawn Mistral Vibe agent in non-interactive batch mode with dual logging
spawn_vibe_agent() {
  local stream_id="$1"
  local stream_slug="$2"
  local log_dir="${REPO_ROOT}/logs/${stream_slug}"
  local log_file="${log_dir}/vibe_refactor.log"

  if ! command -v vibe >/dev/null 2>&1; then
    echo "[!] [Agent Error] 'vibe' CLI executable not found in PATH." >&2
    return 1
  fi

  mkdir -p "${log_dir}"

  local prompt_msg="Execute the complete 5-phase refactoring lifecycle for target stream ${stream_id} (slug: ${stream_slug}). Master domain standard: REFACTORING_PROMPTS/PROMPT_REFACTORING_MISTRAL.md."

  echo "[*] [Vibe Agent] Spawning autonomous batch refactoring agent for stream ${stream_id}..."
  echo "[*] [Vibe Agent] Streaming live execution (Log: logs/${stream_slug}/vibe_refactor.log)..."
  vibe --agent refactor --auto-approve -p "${prompt_msg}" < /dev/null 2>&1 | tee "${log_file}"
}

# Gate 0: Non-English / French comment invariant verification
check_french_invariants() {
  local stream_slug="$1"
  local stream_id="$2"
  local exp_dir="experiments/${stream_slug}"
  local test_file="tests/test_${stream_id}_claims.py"
  local errors=0

  local pattern='(#|//|/\*).*[éèêëàâäôöûüçÉÈÊËÀÂÄÔÖÛÜÇ]'

  if [[ -d "${exp_dir}" ]]; then
    while IFS= read -r f; do
      if grep -En "${pattern}" "${f}" >/dev/null 2>&1; then
        echo "[!] [French Gate] Non-English (French) comment detected in: ${f}" >&2
        grep -En "${pattern}" "${f}" >&2 || true
        errors=$((errors + 1))
      fi
    done < <(find "${exp_dir}" -type f \( -name "*.py" -o -name "*.sh" \))
  fi

  if [[ -f "${test_file}" ]]; then
    if grep -En "${pattern}" "${test_file}" >/dev/null 2>&1; then
      echo "[!] [French Gate] Non-English (French) comment detected in: ${test_file}" >&2
      grep -En "${pattern}" "${test_file}" >&2 || true
      errors=$((errors + 1))
    fi
  fi

  return "${errors}"
}

# Gate 1: Experimental execution stage
run_experiment_stage() {
  local stream_slug="$1"
  local stream_id="$2"
  local exp_dir="experiments/${stream_slug}"
  local runner_sh="${exp_dir}/run_experiment_${stream_id}.sh"
  local generic_sh="${exp_dir}/run_experiment.sh"

  if [[ "${SKIP_EXPERIMENT}" == true ]]; then
    echo "[*] [Phase 2] Experimental execution bypassed (--skip-experiment)."
    return 0
  fi

  if [[ -f "${runner_sh}" ]]; then
    echo "[*] [Phase 2] Launching experiment runner: ${runner_sh}..."
    (cd "${exp_dir}" && bash "./$(basename "${runner_sh}")")
  elif [[ -f "${generic_sh}" ]]; then
    echo "[*] [Phase 2] Launching generic experiment runner: ${generic_sh}..."
    (cd "${exp_dir}" && bash "./$(basename "${generic_sh}")")
  else
    local py_scripts=($(find "${exp_dir}" -maxdepth 1 -name "exp_*.py" 2>/dev/null | sort))
    if [[ ${#py_scripts[@]} -gt 0 ]]; then
      for py_script in "${py_scripts[@]}"; do
        echo "[*] [Phase 2] Executing standalone experiment script: python ${py_script}..."
        python "${py_script}"
      done
    else
      echo "[*] [Phase 2] No executable experiment script located in ${exp_dir} (bypassing)."
    fi
  fi
  return 0
}

# Gate 2: Python and Markdown invariant audit & automated self-healing remediation
run_python_invariants_gate() {
  local stream_slug="$1"
  echo "[*] [Gate Invariants] Auditing invariants via verify_refactoring.py: ${stream_slug}..."

  if [[ -n "${FIX_FLAG}" ]]; then
    python experiments/common/verify_refactoring.py "${stream_slug}" --fix >/dev/null 2>&1 || true
  fi

  python experiments/common/verify_refactoring.py "${stream_slug}"
}

# Gate 3: Pytest claim and contract validation
run_pytest_gate() {
  local stream_id="$1"
  local stream_slug="$2"
  local test_file="tests/test_${stream_id}_claims.py"
  local alt_test="tests/test_${stream_slug}.py"

  if [[ "${SKIP_TESTS}" == true ]]; then
    echo "[*] [Phase 3] Test suite bypassed (--skip-tests)."
    return 0
  fi

  if [[ -f "${test_file}" ]]; then
    echo "[*] [Phase 3] Executing pytest verification: ${test_file}..."
    pytest "${test_file}" -q --tb=short
  elif [[ -f "${alt_test}" ]]; then
    echo "[*] [Phase 3] Executing pytest verification: ${alt_test}..."
    pytest "${alt_test}" -q --tb=short
  else
    echo "[*] [Phase 3] No dedicated test suite discovered for stream ${stream_id} (bypassing)."
  fi
  return 0
}

# Non-blocking Version Control (VCS) Checkpoint (Soft Gate)
checkpoint_vcs() {
  local stream_id="$1"
  local stream_slug="$2"

  if [[ "${SKIP_GIT}" == true ]]; then
    return 0
  fi

  echo "[*] [VCS] Recording Git checkpoint for ${stream_id}..."

  local files_to_add=()
  [[ -d "experiments/${stream_slug}" ]] && files_to_add+=("experiments/${stream_slug}")
  [[ -f "docs/audits/AUDIT_${stream_id}.md" ]] && files_to_add+=("docs/audits/AUDIT_${stream_id}.md")
  [[ -f "docs/sections/${stream_id}.md" ]] && files_to_add+=("docs/sections/${stream_id}.md")
  [[ -f "docs/DEVIATIONS.md" ]] && files_to_add+=("docs/DEVIATIONS.md")
  [[ -d "tests" ]] && files_to_add+=("tests")
  [[ -d "results/${stream_slug}" ]] && files_to_add+=("results/${stream_slug}")

  if [[ ${#files_to_add[@]} -gt 0 ]]; then
    git add "${files_to_add[@]}" 2>/dev/null || {
      echo "[!] [VCS WARNING] Non-blocking failure during 'git add' for stream ${stream_id}." >&2
      return 0
    }
  fi

  if ! git diff --cached --quiet; then
    if git commit -m "refactor(${stream_id}): verified invariants, claims tests, and documentation" 2>/dev/null; then
      echo "[+] [VCS] Git checkpoint successfully committed for ${stream_id}."
    else
      echo "[!] [VCS WARNING] Non-blocking failure during 'git commit' for stream ${stream_id}." >&2
    fi
  else
    echo "[*] [VCS] No staged changes detected for stream ${stream_id}."
  fi

  return 0
}

# ------------------------------------------------------------------------------
# 5. Stream Sequence Filtering Preserving ORDERED_STREAMS Topology
# ------------------------------------------------------------------------------
STREAMS_TO_RUN=()
RESUME_ACTIVE=true
[[ -n "${RESUME_FROM}" ]] && RESUME_ACTIVE=false

for STREAM_ID in "${ORDERED_STREAMS[@]}"; do
  if [[ -n "${TARGET_STREAM}" ]]; then
    if [[ "${TARGET_STREAM}" == "${STREAM_ID}" ]]; then
      STREAMS_TO_RUN+=("${STREAM_ID}")
      break
    fi
    continue
  fi

  if [[ "${RESUME_ACTIVE}" == false ]]; then
    if [[ "${STREAM_ID}" == "${RESUME_FROM}" ]]; then
      RESUME_ACTIVE=true
    fi
  fi

  if [[ "${RESUME_ACTIVE}" == true ]]; then
    STREAMS_TO_RUN+=("${STREAM_ID}")
  fi
done

if [[ ${#STREAMS_TO_RUN[@]} -eq 0 ]]; then
  echo "[!] ERROR: No research stream matches specified execution criteria (Target: '${TARGET_STREAM}', Resume: '${RESUME_FROM}')." >&2
  exit 1
fi

# ------------------------------------------------------------------------------
# 6. Dry-Run Inspection Dispatch
# ------------------------------------------------------------------------------
if [[ "${DRY_RUN}" == true ]]; then
  echo "========================================================================"
  echo "[*] DRY-RUN PIPELINE TOPOLOGY & RESOLUTION"
  echo "========================================================================"
  echo "Execution Sequence (${#STREAMS_TO_RUN[@]} Streams):"
  for idx in "${!STREAMS_TO_RUN[@]}"; do
    s_id="${STREAMS_TO_RUN[idx]}"
    s_slug="$(resolve_stream_slug "${s_id}")"
    printf "  [%02d/21] Stream ID: %-6s -> Directory: experiments/%s\n" "$((idx + 1))" "${s_id}" "${s_slug}"
  done
  exit 0
fi

# ------------------------------------------------------------------------------
# 7. Main Orchestration Execution Loop
# ------------------------------------------------------------------------------
START_TOTAL_TIME=${SECONDS}
SUCCESS_COUNT=0
FAILED_STREAMS=()
SUMMARY_LOG=()

echo "========================================================================"
echo "[*] REFACTORING HARNESS — STRICT SEQUENTIAL PIPELINE"
echo "[*] Total Streams      : ${#STREAMS_TO_RUN[@]}"
echo "[*] Sequence           : ${STREAMS_TO_RUN[*]}"
echo "[*] Agent Spawning     : $([[ "${SPAWN_VIBE}" == true ]] && echo "Enabled (vibe -p batch mode)" || echo "Disabled")"
echo "[*] Task Generation    : $([[ "${GENERATE_TASKS}" == true ]] && echo "Enabled (REFACTORING_PROMPTS/tasks/)" || echo "Disabled")"
echo "[*] Automated Repair   : ${FIX_FLAG:-Disabled}"
echo "[*] Experiments Stage  : $([[ "${SKIP_EXPERIMENT}" == true ]] && echo "Bypassed" || echo "Enabled")"
echo "========================================================================"

for STREAM_ID in "${STREAMS_TO_RUN[@]}"; do
  STREAM_START_TIME=${SECONDS}
  STREAM_SLUG="$(resolve_stream_slug "${STREAM_ID}")"

  echo ""
  echo "------------------------------------------------------------------------"
  echo "[>>>] PROCESSING STREAM: ${STREAM_ID} (Directory: experiments/${STREAM_SLUG})"
  echo "------------------------------------------------------------------------"

  # Optional: Emit lightweight task payload file
  if [[ "${GENERATE_TASKS}" == true ]]; then
    generate_stream_task_payload "${STREAM_ID}" "${STREAM_SLUG}"
  fi

  # Optional: Spawn autonomous Vibe agent refactoring session
  if [[ "${SPAWN_VIBE}" == true ]]; then
    if ! spawn_vibe_agent "${STREAM_ID}" "${STREAM_SLUG}"; then
      echo "[!] [FATAL] Vibe agent execution failed for stream ${STREAM_ID}." >&2
      FAILED_STREAMS+=("${STREAM_ID} (Vibe Agent)")
      exit 1
    fi
  fi

  # Gate 0: Linguistic validation
  echo "[*] [Gate 0] Verifying comment language invariants..."
  if ! check_french_invariants "${STREAM_SLUG}" "${STREAM_ID}"; then
    echo "[!] [FATAL] Non-English comments detected in stream ${STREAM_ID}." >&2
    FAILED_STREAMS+=("${STREAM_ID} (French Gate)")
    exit 1
  fi

  # Gate 1: Experiment execution
  if ! run_experiment_stage "${STREAM_SLUG}" "${STREAM_ID}"; then
    echo "[!] [FATAL] Experimental execution failed for stream ${STREAM_ID}." >&2
    FAILED_STREAMS+=("${STREAM_ID} (Experiment Run)")
    exit 1
  fi

  # Gate 2: Python & Markdown invariant audit (with auto-repair)
  if ! run_python_invariants_gate "${STREAM_SLUG}"; then
    echo "[!] [FATAL] Invariant contract failed for stream ${STREAM_ID}." >&2
    FAILED_STREAMS+=("${STREAM_ID} (Invariants Audit)")
    exit 1
  fi

  # Gate 3: Pytest claim verification
  if ! run_pytest_gate "${STREAM_ID}" "${STREAM_SLUG}"; then
    echo "[!] [FATAL] Pytest claim verification failed for stream ${STREAM_ID}." >&2
    FAILED_STREAMS+=("${STREAM_ID} (Pytest Claims)")
    exit 1
  fi

  # VCS Checkpoint (Non-blocking)
  checkpoint_vcs "${STREAM_ID}" "${STREAM_SLUG}"

  STREAM_DURATION=$((SECONDS - STREAM_START_TIME))
  SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
  SUMMARY_LOG+=("[PASS] ${STREAM_ID} (${STREAM_SLUG}) - ${STREAM_DURATION}s")
  echo "[+] [OK] Stream ${STREAM_ID} successfully validated in ${STREAM_DURATION}s."
done

# ------------------------------------------------------------------------------
# 8. Execution Summary and Diagnostics Report
# ------------------------------------------------------------------------------
TOTAL_DURATION=$((SECONDS - START_TOTAL_TIME))

echo ""
echo "========================================================================"
echo "[+] PIPELINE EXECUTION SUMMARY"
echo "========================================================================"
echo "[*] Total Duration : ${TOTAL_DURATION}s"
echo "[*] Success Rate   : ${SUCCESS_COUNT}/${#STREAMS_TO_RUN[@]}"
echo ""
echo "Validation Breakdown:"
for log_entry in "${SUMMARY_LOG[@]}"; do
  echo "  ${log_entry}"
done

if [[ ${#FAILED_STREAMS[@]} -gt 0 ]]; then
  echo ""
  echo "[!] DETECTED FAILURES:"
  for failed_entry in "${FAILED_STREAMS[@]}"; do
    echo "  - ${failed_entry}"
  done
  exit 1
fi

echo ""
echo "[+] ALL RESEARCH STREAMS SUCCESSFULLY VALIDATED IN PRESCRIBED SEQUENCE."
exit 0