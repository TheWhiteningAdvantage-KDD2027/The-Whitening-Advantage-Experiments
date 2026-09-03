#!/usr/bin/env bash
# ==============================================================================
# DOCUMENTATION RESTORATION HARNESS
# Sequentially spawns the doc_restorer agent per stream, then gates the output.
#
# This harness deliberately does NOT reuse refactor_all_streams.sh: that script's
# spawn prompt imposes a 200-350 word limit on sections and a 4-section audit
# template with blanket Wilson intervals, which is what removed the evidentiary
# content in the first place. Do not run refactor_all_streams.sh --spawn-vibe
# against this repository again until that prompt is corrected.
# ==============================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${REPO_ROOT}"

ORDERED_STREAMS=(
  "R08" "R17" "R16" "R04" "R04b"
  "R01" "R02" "R02b" "R02c" "R03"
  "R05" "R06" "R07" "R09" "R10"
  "R11" "R12" "R13" "R14" "R15" "R18"
)

export PYTHONHASHSEED=42
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export PYTHONUNBUFFERED=1

TARGET_STREAM=""
RESUME_FROM=""
DRY_RUN=false
SKIP_GIT=false
GATE_ONLY=false

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  -s, --stream <ID>       Restore one stream only
  -r, --resume-from <ID>  Resume the sequence from this stream
      --gate-only         Run the acceptance gates without spawning any agent
      --skip-git          Disable per-stream Git checkpoints
      --dry-run           Print the resolved sequence and exit
  -h, --help              Show this message
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -s|--stream)      TARGET_STREAM="$2"; shift 2 ;;
    -r|--resume-from) RESUME_FROM="$2";   shift 2 ;;
    --gate-only)      GATE_ONLY=true;     shift   ;;
    --skip-git)       SKIP_GIT=true;      shift   ;;
    --dry-run)        DRY_RUN=true;       shift   ;;
    -h|--help)        usage ;;
    *) echo "[!] Unknown option: $1" >&2; usage ;;
  esac
done

resolve_slug() {
  local id="$1" d
  d=$(find "${REPO_ROOT}/experiments" -mindepth 1 -maxdepth 1 -type d \
        \( -name "${id}_*" -o -name "${id}" \) 2>/dev/null | head -n 1)
  [[ -n "${d}" ]] && basename "${d}" || echo "${id}"
}

spawn_agent() {
  local id="$1" slug="$2"
  local prompt_file="DOC_RESTORE_PROMPTS/PROMPT_DOC_RESTORE_${id}.md"
  local log_dir="logs/doc_restore_sessions"
  local log_file="${log_dir}/restore_${id}.log"

  command -v vibe >/dev/null 2>&1 || { echo "[!] 'vibe' not in PATH." >&2; return 1; }
  [[ -f "${prompt_file}" ]] || { echo "[!] Missing ${prompt_file}. Run generate_doc_prompts.sh." >&2; return 1; }

  mkdir -p "${log_dir}"
  echo "[*] [Agent] Restoring documentation for ${id} (${slug})..."
  vibe --agent doc_restorer --auto-approve \
       -p "Execute the restoration contract in ${prompt_file}, in full, without omission. Read logs/${slug}/ before writing anything. If a required item is not in the log, write the NOT RECOVERABLE marker rather than a value." \
       < /dev/null 2>&1 | tee "${log_file}"
}

gate_stream() {
  local id="$1" slug="$2"
  local audit="docs/audits/AUDIT_${id}.md"
  local section="docs/sections/${id}.md"
  local errors=0

  echo "[*] [Gate] ${id}"

  for f in "${audit}" "${section}"; do
    [[ -f "${f}" ]] || { echo "[!] missing ${f}" >&2; errors=$((errors+1)); }
  done
  [[ ${errors} -gt 0 ]] && return "${errors}"

  # G1 - confirmatory language
  if grep -Ein 'proves|proven|perfectly valid|validates the (theorem|thesis|claim)|confirms the|as expected|triumph|victory|irrefutable|brilliant' \
       "${audit}" "${section}" >/dev/null 2>&1; then
    echo "[!] [G1] confirmatory language in ${id}" >&2
    grep -Ein 'proves|proven|perfectly valid|validates the (theorem|thesis|claim)|confirms the|as expected|triumph|victory|irrefutable|brilliant' "${audit}" "${section}" >&2
    errors=$((errors+1))
  fi

  # G2 - the six mandatory audit sections
  for h in "1. Deviation table" "2. Controls" "3. Test suite" \
           "4. Reproducibility digests" "5. Design decisions" "6. Open questions"; do
    grep -qF "${h}" "${audit}" || { echo "[!] [G2] ${id}: missing audit section '${h}'" >&2; errors=$((errors+1)); }
  done

  # G3 - pytest output actually pasted
  grep -qE 'passed|failed|error' "${audit}" || { echo "[!] [G3] ${id}: no pytest outcome in the audit" >&2; errors=$((errors+1)); }

  # G4 - digests present or explicitly marked unrecoverable
  if ! grep -qiE 'sha256|sha-256|NOT RECOVERABLE FROM THE LOG' "${audit}"; then
    echo "[!] [G4] ${id}: no digest section and no unrecoverable marker" >&2
    errors=$((errors+1))
  fi

  # G5 - assumed design effect
  if grep -Ein 'deff *= *1[^0-9.]|simple random sampling' "${audit}" >/dev/null 2>&1; then
    echo "[!] [G5] ${id}: assumed design effect" >&2
    errors=$((errors+1))
  fi

  # G6 - uncited BLAS attribution
  if grep -Ein 'BLAS|associativity|summation order' "${audit}" "${section}" >/dev/null 2>&1; then
    echo "[!] [G6] ${id}: causal attribution to BLAS - each hit must cite the log line that established it" >&2
    grep -Ein 'BLAS|associativity|summation order' "${audit}" "${section}" >&2
    errors=$((errors+1))
  fi

  # G7 - D3 count must not be below the log's
  local log_d3 doc_d3
  log_d3=$(grep -ho 'D3' logs/"${slug}"/*.log 2>/dev/null | wc -l | tr -d ' ')
  doc_d3=$(grep -ho 'D3' "${audit}" 2>/dev/null | wc -l | tr -d ' ')
  if [[ "${log_d3}" -gt 0 && "${doc_d3}" -eq 0 ]]; then
    echo "[!] [G7] ${id}: the log records D3 and the audit records none" >&2
    errors=$((errors+1))
  fi

  # G8 - trailing newline
  for f in "${audit}" "${section}"; do
    [[ -n "$(tail -c 1 "${f}")" ]] && { echo "[!] [G8] ${f}: no trailing newline" >&2; errors=$((errors+1)); }
  done

  return "${errors}"
}

checkpoint() {
  local id="$1"
  [[ "${SKIP_GIT}" == true ]] && return 0
  git add "docs/audits/AUDIT_${id}.md" "docs/sections/${id}.md" 2>/dev/null || return 0
  git diff --cached --quiet || \
    git commit -m "docs(${id}): restore forensic audit content from execution logs" 2>/dev/null || true
  return 0
}

STREAMS=()
ACTIVE=true
[[ -n "${RESUME_FROM}" ]] && ACTIVE=false
for S in "${ORDERED_STREAMS[@]}"; do
  if [[ -n "${TARGET_STREAM}" ]]; then
    [[ "${TARGET_STREAM}" == "${S}" ]] && { STREAMS+=("${S}"); break; }
    continue
  fi
  [[ "${ACTIVE}" == false && "${S}" == "${RESUME_FROM}" ]] && ACTIVE=true
  [[ "${ACTIVE}" == true ]] && STREAMS+=("${S}")
done

[[ ${#STREAMS[@]} -gt 0 ]] || { echo "[!] ERROR: empty sequence." >&2; exit 1; }

if [[ "${DRY_RUN}" == true ]]; then
  echo "Sequence (${#STREAMS[@]}):"
  for i in "${!STREAMS[@]}"; do
    printf "  [%02d] %-6s -> %s\n" "$((i+1))" "${STREAMS[i]}" "$(resolve_slug "${STREAMS[i]}")"
  done
  exit 0
fi

PASSED=(); FAILED=()
for id in "${STREAMS[@]}"; do
  slug="$(resolve_slug "${id}")"
  echo ""
  echo "------------------------------------------------------------------------"
  echo "[>>>] ${id} (${slug})"
  echo "------------------------------------------------------------------------"

  if [[ "${GATE_ONLY}" == false ]]; then
    spawn_agent "${id}" "${slug}" || { FAILED+=("${id} (agent)"); continue; }
  fi

  if gate_stream "${id}" "${slug}"; then
    checkpoint "${id}"
    PASSED+=("${id}")
    echo "[+] [OK] ${id}"
  else
    FAILED+=("${id} (gate)")
    echo "[!] [FAIL] ${id} - documentation left in place for manual inspection" >&2
  fi
done

echo ""
echo "========================================================================"
echo "[*] Passed : ${#PASSED[@]}/${#STREAMS[@]}"
[[ ${#FAILED[@]} -gt 0 ]] && { echo "[!] Failed:"; for f in "${FAILED[@]}"; do echo "  - ${f}"; done; exit 1; }
echo "[+] ALL STREAMS RESTORED AND GATED."
exit 0