#!/usr/bin/env python3
"""Remove hard line-wrapping from Markdown prose, with a semantic guard.

Joins consecutive prose lines inside a paragraph so that paragraphs occupy the
full available width. Structure is preserved verbatim: fenced code blocks,
tables, lists, headings, blockquotes, horizontal rules, front matter, and the
DIFF command tags used by the camera-ready candidates.

The guard is the point of this script. After rewriting, the whitespace-normalised
token stream of the file must be identical to the original's. If a single token
differs, nothing is written and the file is reported. A wrapping change cannot
alter a word, a number or a symbol, so any difference is a defect.

Usage:
    python3 unwrap_docs.py --check   docs/                 # report only
    python3 unwrap_docs.py --write   docs/ README.md       # rewrite in place
"""
import argparse
import re
import sys
from pathlib import Path

FENCE = re.compile(r"^\s*(```+|~~~+)")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
HRULE = re.compile(r"^\s{0,3}([-*_])(\s*\1){2,}\s*$")
LIST = re.compile(r"^\s*([-*+]\s|\d+[.)]\s)")
QUOTE = re.compile(r"^\s*>")
TABLE = re.compile(r"^\s*\|")
INDENTED = re.compile(r"^(\t| {4,})\S")
# DIFF command tags and header keys must stay on their own line.
TAG = re.compile(r"^\s*(<{3}\s*(SEARCH|RECHERCHER)|={3}\s*(REPLACE WITH|REMPLACER PAR)"
                 r"|>{3}\s*(END OF BLOCK|FIN DU BLOC)|\*\*Target file|\*\*Fichier cible"
                 r"|Line[- ][Tt]erminator|Classe de terminateur)")
FRONTMATTER = re.compile(r"^---\s*$")


def is_structural(line):
    return bool(
        not line.strip()
        or FENCE.match(line)
        or HEADING.match(line)
        or HRULE.match(line)
        or LIST.match(line)
        or QUOTE.match(line)
        or TABLE.match(line)
        or INDENTED.match(line)
        or TAG.match(line)
    )


def unwrap(text):
    lines = text.split("\n")
    out, i, in_fence, fence_tok = [], 0, False, ""

    # Preserve YAML front matter verbatim.
    if lines and FRONTMATTER.match(lines[0]):
        out.append(lines[0])
        i = 1
        while i < len(lines) and not FRONTMATTER.match(lines[i]):
            out.append(lines[i])
            i += 1
        if i < len(lines):
            out.append(lines[i])
            i += 1

    while i < len(lines):
        line = lines[i]
        m = FENCE.match(line)
        if m:
            tok = m.group(1)
            if not in_fence:
                in_fence, fence_tok = True, tok[0] * 3
            elif tok.startswith(fence_tok):
                in_fence = False
            out.append(line)
            i += 1
            continue
        if in_fence or is_structural(line):
            out.append(line)
            i += 1
            continue

        # A prose paragraph: absorb following prose lines into one.
        buf = [line.rstrip()]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            if FENCE.match(nxt) or is_structural(nxt):
                break
            # A line ending in two spaces is an explicit Markdown line break.
            if buf[-1].endswith("  "):
                break
            buf.append(nxt.strip())
            i += 1
        out.append(" ".join(p for p in buf if p != ""))

    return "\n".join(out)


def tokens(text):
    """Whitespace-normalised token stream. Wrapping changes must not alter it."""
    return text.split()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--write", action="store_true")
    args = ap.parse_args()

    targets = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            targets.extend(sorted(path.rglob("*.md")))
        elif path.suffix == ".md":
            targets.append(path)
    targets = [t for t in targets if t.is_file()]

    changed, refused, clean = [], [], 0
    for f in targets:
        original = f.read_text(encoding="utf-8")
        new = unwrap(original)
        if not new.endswith("\n"):
            new += "\n"

        if tokens(original) != tokens(new):
            a, b = tokens(original), tokens(new)
            first = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
            refused.append(
                f"{f}: token stream changed at position {first} "
                f"({a[first:first+3]!r} -> {b[first:first+3]!r})")
            continue

        if new == original:
            clean += 1
            continue
        changed.append(f)
        if args.write:
            f.write_text(new, encoding="utf-8")

    print(f"{len(targets)} file(s) scanned, {clean} already unwrapped, "
          f"{len(changed)} {'rewritten' if args.write else 'would change'}, "
          f"{len(refused)} refused.")
    for f in changed:
        print(f"  ~ {f}")
    if refused:
        print("REFUSED -- semantic guard tripped, nothing written for these:", file=sys.stderr)
        for r in refused:
            print(f"  ! {r}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())