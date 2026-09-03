#!/usr/bin/env python3
"""Generate the v87 <-> repository mapping table promised at manuscript line 389.

Everything except the manuscript anchors is derived from the repository tree.
Anchors are declared below; the script exits non-zero if a declared stream has
no script, no claims file, or if a stream on disk is undeclared.

Artefacts are split into two families. A control artefact certifies no published
value: it is produced by a degraded or diagnostic arm, selected by an explicit
argument and stamped in its filename. Presenting it in the same column as a
manuscript-facing artefact would overstate what backs the paper.

Usage:  python3 build_mapping.py > docs/MAPPING.md
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Manuscript anchors: not derivable from the tree, declared once, verified below.
ANCHORS = {
    "R01": ("Figure 2", "Table 2 caption"),
    "R02": ("Figure 1", "L290"),
    "R02b": ("Appendix figure", "L290 (i.i.d. arm)"),
    "R02c": ("Appendix figure", "L290 (horizon sweep)"),
    "R03": ("Figure 3", "L171"),
    "R04": ("Figure 4", "Table 3, L274"),
    "R04b": ("Appendix figure", "L274 (nu* refinement)"),
    "R05": ("Figure 5", "L270, Appendix B"),
    "R06": ("Figure 6", "L284, L290"),
    "R07": ("Figure 7", "L302, L308"),
    "R08": ("Figure 8", "L241, L311"),
    "R09": ("Figure 9", "L243"),
    "R10": ("Figure 10", "L290"),
    "R11": ("Figures 11 and 15", "L171, L294, L296, L298"),
    "R12": ("Figures 12 and 13", "L349, L353"),
    "R13": ("Figure 14", "L331"),
    "R14": ("Figure 16", "L345"),
    "R15": ("Figure 17", "L376, L389"),
    "R16": ("no figure", "L329, L331, L260, L392"),
    "R17": ("no figure", "L341"),
    "R18": ("Appendix figure", "no v87 value certified"),
}

# Filename stems ending in one of these mark an artefact that certifies no
# published value: degraded modes, diagnostic arms, counterfactual arms.
CONTROL_SUFFIXES = (
    "_fast",
    "_legacy_seeds",
    "_legacy_qmle",
    "_legacy_blas",
    "_witness_blas",
    "_independent_seeds",
    "_crn_witness",
    "_control_ecusum",
    "_strict_ps",
    "_symmetric",
    "_pairing_diagnostic",
)


def is_control(path):
    return Path(path).stem.endswith(CONTROL_SUFFIXES)


def rel(p):
    return p.relative_to(ROOT).as_posix()


def split_family(paths):
    published, control = [], []
    for p in paths:
        (control if is_control(p) else published).append(rel(p))
    return published, control


def cell(items):
    return "<br>".join(f"`{s}`" for s in items) if items else "—"


def main():
    results = ROOT / "results"
    if not results.is_dir():
        sys.exit("results/ not found -- run from the repository root")

    on_disk = {}
    for d in sorted(results.iterdir()):
        if d.is_dir() and "_" in d.name:
            on_disk[d.name.split("_", 1)[0]] = d

    undeclared = sorted(set(on_disk) - set(ANCHORS))
    missing = sorted(set(ANCHORS) - set(on_disk))
    if undeclared or missing:
        sys.exit(f"anchor/tree mismatch -- undeclared: {undeclared}, missing: {missing}")

    rows, problems = [], []
    for stream in sorted(ANCHORS, key=lambda s: (int(s[1:3]), s[3:])):
        d = on_disk[stream]
        scripts = sorted((ROOT / "experiments" / d.name).glob("exp_*.py"))
        figures = sorted((d / "figures").glob("*.png")) if (d / "figures").is_dir() else []
        data = sorted((d / "data").glob("*.csv")) if (d / "data").is_dir() else []
        claims = sorted((d / "tables").glob("*_claims.tex")) if (d / "tables").is_dir() else []
        section = ROOT / "docs" / "sections" / f"{stream}.md"
        audit = ROOT / "docs" / "audits" / f"AUDIT_{stream}.md"

        if not scripts:
            problems.append(f"{stream}: no exp_*.py")
        if not claims:
            problems.append(f"{stream}: no *_claims.tex")
        if not data:
            problems.append(f"{stream}: no CSV")
        if not section.is_file():
            problems.append(f"{stream}: no docs/sections/{stream}.md")
        if not audit.is_file():
            problems.append(f"{stream}: no docs/audits/AUDIT_{stream}.md")

        fig_pub, fig_ctl = split_family(figures)
        dat_pub, dat_ctl = split_family(data)
        rendered, anchor = ANCHORS[stream]

        rows.append({
            "stream": stream,
            "rendered": rendered,
            "anchor": anchor,
            "scripts": [rel(p) for p in scripts],
            "fig_pub": fig_pub, "fig_ctl": fig_ctl,
            "dat_pub": dat_pub, "dat_ctl": dat_ctl,
            "claims": [rel(p) for p in claims],
            "section": rel(section) if section.is_file() else "",
            "audit": rel(audit) if audit.is_file() else "",
            "runner": f"run_experiment_{stream}.sh"
                      if (ROOT / f"run_experiment_{stream}.sh").is_file() else "",
        })

    if problems:
        sys.exit("incomplete tree:\n  " + "\n  ".join(problems))

    out = []
    out.append("## Mapping table (manuscript line 389)\n")
    out.append(
        "Every figure and every number of the submitted manuscript, linked to the script that "
        "generates it, the CSV that carries it, and the LaTeX macro file that certifies it. "
        "Generated by `build_mapping.py` from the repository tree; manuscript anchors are declared "
        "in that script and validated against it.\n")
    out.append(
        "**Two families of artefact.** The columns *Figures* and *Data* list artefacts that carry a "
        "value printed in the manuscript. The column *Control artefacts* lists artefacts produced by "
        "degraded or diagnostic arms -- explicitly selected by argument and stamped in their "
        "filename -- which certify no published value and exist to make a control auditable. "
        "The totals below count the first family only.\n")
    out.append("| v87 artefact | Manuscript anchor | Stream | Generating script | Runner | "
               "Figures | Data | Control artefacts | Macros | Report | Audit |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        out.append("| {} | {} | {} | {} | `{}` | {} | {} | {} | {} | `{}` | `{}` |".format(
            r["rendered"], r["anchor"], r["stream"],
            cell(r["scripts"]), r["runner"],
            cell(r["fig_pub"]), cell(r["dat_pub"]),
            cell(r["fig_ctl"] + r["dat_ctl"]),
            cell(r["claims"]), r["section"], r["audit"]))
    out.append("")

    n_fig = sum(len(r["fig_pub"]) for r in rows)
    n_csv = sum(len(r["dat_pub"]) for r in rows)
    n_ctl = sum(len(r["fig_ctl"]) + len(r["dat_ctl"]) for r in rows)
    out.append(f"{len(rows)} streams, {n_fig} manuscript-facing figures, "
               f"{n_csv} manuscript-facing CSV files, "
               f"{sum(len(r['claims']) for r in rows)} macro files, "
               f"{n_ctl} control artefacts certifying no published value.\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()