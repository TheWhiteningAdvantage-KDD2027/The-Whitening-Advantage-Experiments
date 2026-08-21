#!/usr/bin/env bash
# ==============================================================================
# STANDALONE GENERATOR: BATCH PROMPT MATERIALIZATION PIPELINE
# Compiles concrete stream prompts from the master template into ./REFACTORING_PROMPTS/
# ==============================================================================

set -euo pipefail

# Portable repository root resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-${SCRIPT_DIR}}"
cd "${REPO_ROOT}"

# Default paths
GENERIC_PROMPT_TEMPLATE="${REPO_ROOT}/REFACTORING_PROMPTS/PROMPT_REFACTORING_MISTRAL.md"
OUTPUT_DIR="${REPO_ROOT}/REFACTORING_PROMPTS"

# Full 21-stream SSOT dependency sequence (§3 of EXPERIMENTS_SCRIPTS_DEPENDENCIES.md)
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

# CLI Options
TARGET_STREAM=""
RESUME_FROM=""
DRY_RUN=false

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  -s, --stream <ID>          Generate prompt exclusively for the specified stream (e.g., R02b, R13)
  -r, --resume-from <ID>     Generate prompts starting from specified stream to the end
  -t, --template <PATH>      Override path to generic prompt template (default: REFACTORING_PROMPTS/PROMPT_REFACTORING_MISTRAL.md)
  -o, --output-dir <DIR>     Override output directory (default: REFACTORING_PROMPTS/)
      --dry-run              Display streams and target paths without writing files
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
    -t|--template)
      GENERIC_PROMPT_TEMPLATE="$2"
      shift 2
      ;;
    -o|--output-dir)
      OUTPUT_DIR="$2"
      shift 2
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

if [[ ! -f "${GENERIC_PROMPT_TEMPLATE}" ]]; then
  echo "[!] ERROR: Generic prompt template '${GENERIC_PROMPT_TEMPLATE}' not found." >&2
  exit 1
fi

mkdir -p "${OUTPUT_DIR}"

# ------------------------------------------------------------------------------
# Stream Sequence Filtering
# ------------------------------------------------------------------------------
STREAMS_TO_GENERATE=()
RESUME_ACTIVE=true
[[ -n "${RESUME_FROM}" ]] && RESUME_ACTIVE=false

for STREAM_ID in "${ORDERED_STREAMS[@]}"; do
  if [[ -n "${TARGET_STREAM}" ]]; then
    if [[ "${TARGET_STREAM}" == "${STREAM_ID}" ]]; then
      STREAMS_TO_GENERATE+=("${STREAM_ID}")
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
    STREAMS_TO_GENERATE+=("${STREAM_ID}")
  fi
done

if [[ ${#STREAMS_TO_GENERATE[@]} -eq 0 ]]; then
  echo "[!] ERROR: No research stream matches criteria (Target: '${TARGET_STREAM}', Resume: '${RESUME_FROM}')." >&2
  exit 1
fi

# ------------------------------------------------------------------------------
# Materialization Engine
# ------------------------------------------------------------------------------
echo "======================================================================"
echo "[*] BATCH PROMPT MATERIALIZATION PIPELINE"
echo "[*] Total Streams      : ${#STREAMS_TO_GENERATE[@]}"
echo "[*] Template Source    : ${GENERIC_PROMPT_TEMPLATE}"
echo "[*] Output Directory   : ${OUTPUT_DIR}"
echo "======================================================================"

GENERATED_COUNT=0

for STREAM_ID in "${STREAMS_TO_GENERATE[@]}"; do
  # Robust discovery matching both experiments/RXX_* and experiments/RXX
  shopt -s nullglob
  MATCHING_DIRS=(experiments/${STREAM_ID}_* experiments/${STREAM_ID})
  shopt -u nullglob

  if [[ ${#MATCHING_DIRS[@]} -gt 0 ]]; then
    STREAM_SLUG=$(basename "${MATCHING_DIRS[0]}")
  else
    STREAM_SLUG="${STREAM_ID}"
  fi

  if [[ "${STREAM_SLUG}" == "${STREAM_ID}" ]]; then
    SLUG_SUFFIX=""
  else
    SLUG_SUFFIX="${STREAM_SLUG#${STREAM_ID}_}"
  fi

  TARGET_PROMPT="${OUTPUT_DIR}/PROMPT_REFACTORING_MISTRAL_${STREAM_ID}.md"

  if [[ "${DRY_RUN}" == true ]]; then
    printf "  [DRY-RUN] Stream %-6s -> Slug: %-25s -> Target: %s\n" "${STREAM_ID}" "${STREAM_SLUG}" "$(basename "${TARGET_PROMPT}")"
    continue
  fi

  # Comprehensive substitution matrix supporting legacy and modernized parameter tags
  sed \
    -e "s|R\[XX\]_<slug>|${STREAM_SLUG}|g" \
    -e "s|<stream_slug>|${STREAM_SLUG}|g" \
    -e "s|R\[XX\]|${STREAM_ID}|g" \
    -e "s|<stream_id>|${STREAM_ID}|g" \
    -e "s|<slug>|${SLUG_SUFFIX}|g" \
    "${GENERIC_PROMPT_TEMPLATE}" > "${TARGET_PROMPT}"

  if [[ -s "${TARGET_PROMPT}" ]]; then
    echo "[+] [${STREAM_ID}] -> ${TARGET_PROMPT} (Slug: ${STREAM_SLUG})"
    ((GENERATED_COUNT += 1))
  else
    echo "[!] ERROR: Generated prompt ${TARGET_PROMPT} is empty." >&2
    exit 1
  fi
done

if [[ "${DRY_RUN}" == false ]]; then
  echo "======================================================================"
  echo "[+] SUCCESS: ${GENERATED_COUNT}/${#STREAMS_TO_GENERATE[@]} prompts compiled in ${OUTPUT_DIR}/"
  echo "======================================================================"
fi