#!/usr/bin/env python3
"""Gate 4 -- camera-ready candidate integrity.

Verifies, for every file in docs/camera_ready_candidates/:
  1. the PARKED header, the trigger, and exactly one family marker;
  2. that every prose search anchor occurs EXACTLY ONCE in the frozen manuscript;
  3. that the family marker agrees with docs/DEVIATIONS.md -- a candidate marked
     NO DEVIATION must have no register entry, and one that is not must have one.

Read-only on the manuscript. Never writes anything. Exit 0 clean, 1 on any finding.

Usage:
    python experiments/common/verify_camera_ready.py [STREAM_ID ...]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CAND_DIR = ROOT / "docs" / "camera_ready_candidates"
REGISTER = ROOT / "docs" / "DEVIATIONS.md"
MANUSCRIPT = ROOT / "articleB_whitening_v87.tex"

TRIGGER = "14 November 2026"
PARKED = "PARKED"
NO_DEV = "NO DEVIATION"

# A search block opens with nine tildes, optionally typed, and closes the same way.
FENCE = re.compile(r"^~{9}[A-Za-z]*\s*$")
SEARCH_TAG = re.compile(r"^<{3}\s*(SEARCH|RECHERCHER)\s*$")
REPLACE_TAG = re.compile(r"^={3}\s*(REPLACE WITH|REMPLACER PAR)\s*>{3}\s*$")
ID_RE = re.compile(r"R[0-9]{2}[a-z]?-[a-z0-9-]{3,}")

# A block whose payload is a macro definition is not a manuscript anchor and is
# not looked up in the .tex; it is verified only for structural well-formedness.
MACRO_ONLY = re.compile(r"\\newcommand|\\renewcommand")


def extract_search_blocks(text):
    """Return the payload of every SEARCH block, in order."""
    lines = text.splitlines()
    blocks, i = [], 0
    while i < len(lines):
        if SEARCH_TAG.match(lines[i].strip()):
            j = i + 1
            while j < len(lines) and not FENCE.match(lines[j]):
                j += 1
            if j >= len(lines):
                break
            k, payload = j + 1, []
            while k < len(lines) and not FENCE.match(lines[k]):
                payload.append(lines[k])
                k += 1
            if payload:
                blocks.append("\n".join(payload))
            i = k
        elif REPLACE_TAG.match(lines[i].strip()):
            i += 1
        else:
            i += 1
    return blocks


def main():
    wanted = set(sys.argv[1:])
    findings = []

    for path in (CAND_DIR, REGISTER, MANUSCRIPT):
        if not path.exists():
            print(f"[Gate 4] MISSING: {path}", file=sys.stderr)
            return 1

    tex = MANUSCRIPT.read_text(encoding="utf-8", errors="replace")
    register = REGISTER.read_text(encoding="utf-8", errors="replace")
    register_ids = set(ID_RE.findall(register))

    files = sorted(CAND_DIR.glob("*_v87_*.md"))
    if not files:
        print("[Gate 4] no candidate files found", file=sys.stderr)
        return 1

    checked = 0
    for f in files:
        stream_tokens = f.name.split("_v87_")[0].split("_")
        if wanted and not any(token in wanted for token in stream_tokens):
            continue
        checked += 1
        rel = f.relative_to(ROOT).as_posix()
        text = f.read_text(encoding="utf-8", errors="replace")
        head = "\n".join(text.splitlines()[:15])

        if PARKED not in head:
            findings.append(f"{rel}: no PARKED header in the first 15 lines")
        if TRIGGER not in head:
            findings.append(f"{rel}: no trigger '{TRIGGER}' in the first 15 lines")

        no_dev = NO_DEV in head
        cited = set(ID_RE.findall(text))
        in_register = {i for i in cited if i in register_ids}

        if no_dev and in_register:
            findings.append(
                f"{rel}: marked NO DEVIATION but cites register entries "
                f"{sorted(in_register)} -- a clarification carries no register entry")
        if not no_dev and not in_register:
            findings.append(
                f"{rel}: not marked NO DEVIATION and cites no register entry present in "
                f"docs/DEVIATIONS.md -- add the family marker or the register entry")
        for i in sorted(cited - register_ids):
            findings.append(f"{rel}: dangling register identifier '{i}'")

        blocks = extract_search_blocks(text)
        if not blocks:
            findings.append(f"{rel}: no SEARCH block found")
        for n, payload in enumerate(blocks, 1):
            if MACRO_ONLY.search(payload):
                continue
            probe = payload.strip()
            if not probe:
                findings.append(f"{rel}: SEARCH block {n} is empty")
                continue
            count = tex.count(probe)
            if count != 1:
                first = probe.splitlines()[0][:70]
                findings.append(
                    f"{rel}: SEARCH block {n} occurs {count} times in the frozen manuscript "
                    f"(must be exactly 1) -- starts: {first!r}")

    print(f"[Gate 4] {checked} candidate file(s) checked.")
    if findings:
        print(f"[Gate 4] {len(findings)} finding(s):", file=sys.stderr)
        for x in findings:
            print(f"  - {x}", file=sys.stderr)
        return 1
    print("[Gate 4] clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())