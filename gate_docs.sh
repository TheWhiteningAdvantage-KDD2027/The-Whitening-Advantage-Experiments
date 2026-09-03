#!/usr/bin/env bash
# ==============================================================================
# DOCUMENTATION ACCEPTANCE GATES — standalone, no agent spawning.
# Supersedes gate_stream() in restore_all_docs.sh, whose G6 fires on legitimate
# '_witness_blas' artefact names and whose G7 is blind because the string 'D3'
# occurs in the mandatory section title '## 1. Deviation table (D0-D3)'.
# ==============================================================================

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${REPO_ROOT}"

STREAMS=(R01 R02 R02b R02c R03 R04 R04b R05 R06 R07 R08 R09 R10 R11 R12 R13 R14 R15 R16 R17 R18)
[[ $# -gt 0 ]] && STREAMS=("$@")

CONF_RE='proves|proven|perfectly valid|validates the (theorem|thesis|claim)|confirms the|as expected|triumph|victory|irrefutable|brilliant'
SECTIONS=("1. Deviation table" "2. Controls" "3. Test suite" \
          "4. Reproducibility digests" "5. Design decisions" "6. Open questions")

resolve_slug() {
  local d
  d=$(find experiments -mindepth 1 -maxdepth 1 -type d \( -name "$1_*" -o -name "$1" \) | head -n 1)
  [[ -n "${d}" ]] && basename "${d}" || echo "$1"
}

TOTAL_FAIL=0
for id in "${STREAMS[@]}"; do
  slug="$(resolve_slug "${id}")"
  audit="docs/audits/AUDIT_${id}.md"
  section="docs/sections/${id}.md"
  e=0
  echo "── ${id} (${slug})"

  for f in "${audit}" "${section}"; do
    [[ -f "${f}" ]] || { echo "   [MISS] ${f}"; e=$((e+1)); }
  done
  if [[ ${e} -gt 0 ]]; then TOTAL_FAIL=$((TOTAL_FAIL+1)); continue; fi

  # G1 confirmatory language
  grep -Ein "${CONF_RE}" "${audit}" "${section}" >/dev/null 2>&1 && {
    echo "   [G1] confirmatory language"; grep -Ein "${CONF_RE}" "${audit}" "${section}"; e=$((e+1)); }

  # G2 six mandatory sections
  for h in "${SECTIONS[@]}"; do
    grep -qF "${h}" "${audit}" || { echo "   [G2] missing section: ${h}"; e=$((e+1)); }
  done

  # G3 pytest outcome present
  grep -qE '[0-9]+ (passed|failed)' "${audit}" || { echo "   [G3] no pytest outcome"; e=$((e+1)); }

  # G4 digests present or explicitly unrecoverable
  grep -qiE '[0-9a-f]{64}|NOT RECOVERABLE FROM THE LOG' "${audit}" || {
    echo "   [G4] no digest and no unrecoverable marker"; e=$((e+1)); }

  # G5 assumed design effect -- a '1' followed by an arithmetic operator opens the
  # Kish formula 1 + (m - 1) * rho_bar and is a measurement, not an assumption of 1.
  g5=$(grep -Ein 'deff *= *1[^0-9.]|design effect (of )?1[^0-9.]|simple random sampling' "${audit}" \
       | grep -vE '(deff *= *|design effect (of )?)1 *[-+*/]')
  if [[ -n "${g5}" ]]; then
    echo "   [G5] assumed design effect"; echo "${g5}"; e=$((e+1))
  fi

  # G6 uncited causal attribution -- exclude artefact/file/test names carrying '_blas'
  grep -Ein 'BLAS|associativity|summation order' "${audit}" "${section}" \
    | grep -viE '_blas|witness-blas|legacy-blas|\.csv|\.png|\.log|::|test_' >/dev/null 2>&1 && {
      echo "   [G6] causal attribution -- each hit must cite the log line that established it"
      grep -Ein 'BLAS|associativity|summation order' "${audit}" "${section}" \
        | grep -viE '_blas|witness-blas|legacy-blas|\.csv|\.png|\.log|::|test_'
      e=$((e+1)); }

  # G7 severity counted from the table body only, never from the section title
  body_d3=$(sed -n '/^## 1\. Deviation table/,/^## 2\./p' "${audit}" | grep -c '| *D3 *|')
  decl_d3=$(grep -oiE 'D3 *: *[0-9]+' "${audit}" | head -1 | grep -oE '[0-9]+$')
  decl_d3=${decl_d3:-0}
  if [[ "${body_d3}" -ne "${decl_d3}" ]]; then
    echo "   [G7] declared D3 count (${decl_d3}) does not match table rows (${body_d3})"; e=$((e+1))
  fi
  if [[ "${body_d3}" -gt 0 ]]; then
    sed -n '/^## 1\. Deviation table/,/^## 2\./p' "${audit}" | grep -qiE 'falsif' || {
      echo "   [G7b] D3 row present but no falsified-claim statement in the deviation table"; e=$((e+1)); }
    grep -qiE '^\*\*Scope|^Scope:' "${audit}" || {
      echo "   [G7c] D3 row present but no scope clause"; e=$((e+1)); }
    grep -qiE 'all qualitative claims are preserved' "${audit}" "${section}" && {
      echo "   [G7d] D3 present and 'all qualitative claims are preserved' asserted"; e=$((e+1)); }
  fi

  # G8 Wilson intervals only on proportions. A hit must name Wilson AND carry a
  # numeric interval on the same line: prose, a test name, the primitive
  # wilson_ci and a column header describe the interval, they do not apply it.
  # A proportion is not always called a 'rate': 'level', 'probability' and
  # 'percentage points' name one too, and those lines are not findings.
  w8=$(grep -in 'wilson' "${audit}" \
       | grep -E '\[ *[0-9][0-9.eE+-]* *, *[0-9][0-9.eE+-]* *\]' \
       | grep -viE 'rate|fpr|detrate|proportion|reject|alarm|frac|detect|level|probability|percentage point|::|test_|wilson_ci|\| *wilson[^|[]*\|')
  if [[ -n "${w8}" ]]; then
    echo "   [G8] Wilson interval on what may not be a proportion -- inspect:"
    echo "${w8}"
    e=$((e+1))
  fi

  # G9 trailing newline
  for f in "${audit}" "${section}"; do
    [[ -n "$(tail -c 1 "${f}")" ]] && { echo "   [G9] ${f}: no trailing newline"; e=$((e+1)); }
  done

  if [[ ${e} -eq 0 ]]; then echo "   [OK]"; else TOTAL_FAIL=$((TOTAL_FAIL+1)); fi
done

echo ""
echo "════════════════════════════════════════════"
echo "Streams with findings: ${TOTAL_FAIL}/${#STREAMS[@]}"
[[ ${TOTAL_FAIL} -gt 0 ]] && exit 1
exit 0