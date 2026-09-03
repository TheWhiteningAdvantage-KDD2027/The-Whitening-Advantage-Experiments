#!/usr/bin/env bash
# ==============================================================================
# DOCUMENTATION RESTORATION — BATCH PROMPT MATERIALIZATION
# Compiles per-stream restoration prompts into ./DOC_RESTORE_PROMPTS/
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-${SCRIPT_DIR}}"
cd "${REPO_ROOT}"

TEMPLATE="${REPO_ROOT}/DOC_RESTORE_PROMPTS/PROMPT_DOC_RESTORE_MISTRAL.md"
OUTPUT_DIR="${REPO_ROOT}/DOC_RESTORE_PROMPTS"

# Restoration order: highest evidentiary damage first, so that a partial run
# repairs the most exposed streams. R08 and R17 lost a D3; R01, R02 and R08
# carry refuted causal attributions; the rest lost the six mandatory sections.
ORDERED_STREAMS=(
  "R08" "R17" "R16" "R04" "R04b"
  "R01" "R02" "R02b" "R02c" "R03"
  "R05" "R06" "R07" "R09" "R10"
  "R11" "R12" "R13" "R14" "R15" "R18"
)

TARGET_STREAM=""
DRY_RUN=false

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  -s, --stream <ID>      Generate the prompt for one stream only (e.g. R08)
  -t, --template <PATH>  Override the master template
  -o, --output-dir <DIR> Override the output directory
      --dry-run          List targets without writing
  -h, --help             Show this message
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -s|--stream)     TARGET_STREAM="$2"; shift 2 ;;
    -t|--template)   TEMPLATE="$2";      shift 2 ;;
    -o|--output-dir) OUTPUT_DIR="$2";    shift 2 ;;
    --dry-run)       DRY_RUN=true;       shift   ;;
    -h|--help)       usage ;;
    *) echo "[!] Unknown option: $1" >&2; usage ;;
  esac
done

[[ -f "${TEMPLATE}" ]] || { echo "[!] ERROR: template '${TEMPLATE}' not found." >&2; exit 1; }
mkdir -p "${OUTPUT_DIR}"

STREAMS=()
for S in "${ORDERED_STREAMS[@]}"; do
  if [[ -n "${TARGET_STREAM}" ]]; then
    [[ "${TARGET_STREAM}" == "${S}" ]] && { STREAMS+=("${S}"); break; }
    continue
  fi
  STREAMS+=("${S}")
done

[[ ${#STREAMS[@]} -gt 0 ]] || { echo "[!] ERROR: no stream matches '${TARGET_STREAM}'." >&2; exit 1; }

echo "======================================================================"
echo "[*] DOC RESTORATION PROMPT MATERIALIZATION"
echo "[*] Streams   : ${#STREAMS[@]}"
echo "[*] Template  : ${TEMPLATE}"
echo "[*] Output    : ${OUTPUT_DIR}"
echo "======================================================================"

COUNT=0
for STREAM_ID in "${STREAMS[@]}"; do
  shopt -s nullglob
  MATCHING=(experiments/${STREAM_ID}_* experiments/${STREAM_ID})
  shopt -u nullglob

  if [[ ${#MATCHING[@]} -eq 0 ]]; then
    echo "[!] ERROR: no experiments/ directory for ${STREAM_ID}." >&2
    exit 1
  fi
  STREAM_SLUG=$(basename "${MATCHING[0]}")
  SLUG_SUFFIX="${STREAM_SLUG#${STREAM_ID}_}"
  [[ "${STREAM_SLUG}" == "${STREAM_ID}" ]] && SLUG_SUFFIX=""

  if [[ ! -d "logs/${STREAM_SLUG}" ]]; then
    echo "[!] ERROR: logs/${STREAM_SLUG}/ is absent. The restoration has no source for ${STREAM_ID}." >&2
    echo "[!]        Restore the logs before generating this prompt." >&2
    exit 1
  fi

  TARGET="${OUTPUT_DIR}/PROMPT_DOC_RESTORE_${STREAM_ID}.md"

  if [[ "${DRY_RUN}" == true ]]; then
    printf "  [DRY-RUN] %-6s -> %-28s -> %s\n" "${STREAM_ID}" "${STREAM_SLUG}" "$(basename "${TARGET}")"
    continue
  fi

  sed \
    -e "s|R\[XX\]_<slug>|${STREAM_SLUG}|g" \
    -e "s|R\[XX\]|${STREAM_ID}|g" \
    -e "s|<slug>|${SLUG_SUFFIX}|g" \
    "${TEMPLATE}" > "${TARGET}"

  [[ -s "${TARGET}" ]] || { echo "[!] ERROR: ${TARGET} is empty." >&2; exit 1; }
  echo "[+] [${STREAM_ID}] -> ${TARGET} (slug: ${STREAM_SLUG})"
  COUNT=$((COUNT + 1))
done

if [[ "${DRY_RUN}" == false ]]; then
  echo "======================================================================"
  echo "[+] ${COUNT}/${#STREAMS[@]} restoration prompts compiled in ${OUTPUT_DIR}/"
  echo "======================================================================"
fi