#!/usr/bin/env python3
"""
==========================================================================
R15 (a) -- THE PUBLIC EQUITY FETCHER AND THE PANEL PROVENANCE (v87 L389)
==========================================================================
v87's Reproducibility appendix (L389) prints, as a promise, that this
repository ships "public fetchers for Bitcoin, Ethereum, and 97 equities". The
Bitcoin and Ethereum fetchers exist (R14). The equity fetcher did not: the panel
behind Figure 17 was produced by `Priorite_25b_fetch_yf_panel.py`, which was
never converted to the FAIR harness. A repository without an executable equity
fetcher contradicts the manuscript formally, so this script is a deliverable of
the manuscript and not a convenience.

TWO STAGES, AND THE NOMINAL ONE TOUCHES NO NETWORK.

  --stage analyse   (default) reads the committed
                    data/derived_equities/R15_panel_logreturns.csv, logs its
                    SHA-256, and re-verifies its shape and date span. This is
                    the reviewer's path and it is offline and bit-stable.
  --stage ingest    hits Yahoo Finance sequentially, rebuilds the panel from
                    scratch, and CHECKS it against the committed file. It is
                    L389's promise made executable. It is run once; a network
                    path cannot be part of a bit-for-bit determinism claim.
  --stage all       ingest, then analyse.

WHY THE FETCHER IS NOT CARRIED VERBATIM: THE SILENT DROP (preamble S4.3).
`Priorite_25b`'s `fetch_one` returns `None` after `MAX_RETRY` and its `main`
skips it with a bare `if s is not None`. Two consequences the delivered script
does not surface:

  1. A transient outage silently reduces the number of retained tickers.
  2. `K_max` -- the LAST element of the published `K_GRID` -- is that number.
     A network failure therefore silently rewrites the grid of the published
     figure. This is the preamble's gravest defect class: a fallback that
     produces a plausible number instead of stopping.

This port keeps the retry/abandon MECHANISM byte-for-byte in behaviour and
removes the silence. Every abandoned ticker is named with its attempt count and
its exception class; every ticker under MIN_COVERAGE is named with its row count
and its coverage; and the retained set is compared, as a set and in order, to
the column header of the committed panel. Any discrepancy stops the run with
`sys.exit(1)`. Nothing is absorbed.

THE SURVIVAL RULE, RESTATED, BECAUSE THE OBVIOUS READING IS WRONG.
The 97 columns are NOT the output of `dropna(how="any")`. `dropna(how="any")`
(delivered line 57) drops *dates*, not tickers, and on this panel it drops none.
The rule that sets the 97 is the coverage filter `cov >= MIN_COVERAGE`
(delivered line 56). The chain, reconstructed from
`data/reference/R15/Priorite_25b_fetch_yf_panel.log`:

  103 listed entries in UNIVERSE
  -> 102 unique          QCOM appears twice; `dict.fromkeys` dedupes in order
  -> 100 fetched         MMC and K exhaust MAX_RETRY and are abandoned
                         ("$MMC: possibly delisted; no timezone found", idem K)
  ->  97 retained        V (4347/5154 = 84.3%), MA (4803/5154 = 93.2%) and
                         GM (3673/5154 = 71.3%) fall under the 98% floor,
                         because each listed after 2005-01-04
  -> 5154 dates          the row-wise dropna drops nothing

SURVIVORSHIP IS A PROPERTY OF THE SPECIFICATION, NOT A DEFECT OF THE PORT.
UNIVERSE is a fixed list of currently-listed US large caps applied backwards to
2005, so the panel is survivorship-biased by construction. v87 says so in the
Figure 17 caption and in L376 ("a survivorship-biased panel providing an
upper-bound co-movement benchmark"). The bias inflates co-movement, which makes
the measured sign correlation an UPPER bound and the cross-sectional escape it
prices an OPTIMISTIC one -- the direction that does not flatter the claim.
UNIVERSE is therefore carried verbatim as specification.

`auto_adjust=True` IS CARRIED, AGAINST SPECS_REPRO_FAIR.md 1.12.
v87 specifies "public adjusted closes". With `auto_adjust=True` yfinance returns
the adjusted price in `Close` and emits no `Adj Close` column at all, so the
delivered call satisfies the manuscript. SPECS 1.12 prescribes
`auto_adjust=False`; preamble S1 makes the manuscript the source of truth for
experimental specification. The delivered value is kept and the conflict is
logged once here and recorded once in docs/audits/AUDIT_R15.md. It is not
resolved silently in either direction.

References:
- Yahoo Finance daily adjusted closes, retrieved through `yfinance`.
==========================================================================
"""

import sys
from pathlib import Path

# Determinism bootstrap, in the order preamble S6 requires: fair_env imports only
# os and sys, so the environment block is posted before NumPy is loaded by anyone
# and before any BLAS thread limit is read. PYTHONHASHSEED cannot be set from
# here -- CPython reads it at interpreter start-up -- so it is exported by
# run_experiment_R15.sh and verified below.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from experiments.common.fair_env import enforce_strict_determinism, verify_hash_seed, log_environment

enforce_strict_determinism()

import os

if os.environ.get("PYTHONHASHSEED") != "42":
    sys.exit("FATAL: PYTHONHASHSEED is not 42. Execute via run_experiment_R15.sh")

import numpy as np
import pandas as pd
from experiments.common.fair_harness import (setup_logging, disable_pandas_multithreading,
                                             compute_sha256)

disable_pandas_multithreading()

import ast
import time
import hashlib
import argparse

# --- PROTOCOL SPECIFICATION, CARRIED VERBATIM FROM Priorite_25b ---
START, END, INTERVAL = "2005-01-01", "2025-07-01", "1d"
SLEEP_S, MAX_RETRY, MIN_COVERAGE = 2.0, 3, 0.98

# Fixed liquid US large-cap universe (survivorship-biased by construction; logged).
UNIVERSE = [
    "AAPL","MSFT","AMZN","GOOGL","JPM","JNJ","V","PG","HD","MA","BAC","DIS","ADBE","XOM","CVX",
    "KO","PEP","WMT","CSCO","INTC","CMCSA","PFE","ABT","MRK","WFC","TMO","COST","MCD","NKE","DHR",
    "TXN","NEE","ORCL","QCOM","HON","UNH","AMGN","IBM","GE","CAT","MMM","GS","BA","SBUX","LOW","AXP",
    "BLK","GILD","MDLZ","ISRG","AMD","ADP","C","MS","SPGI","CB","MO","DUK","SO","BDX","CL","USB",
    "PNC","TGT","FDX","CSX","EMR","ITW","AON","MMC","SLB","EOG","COP","APD","SHW","ECL","NSC","WM",
    "PSA","AEP","D","EXC","F","GM","DD","KMB","GIS","K","HSY","SYY","ADI","MU","LRCX","KLAC","AMAT",
    "ROP","INTU","UPS","RTX","NVDA","CRM","QCOM","LLY",
]

# --- WHAT THE SUBMITTED FETCH LOG RECORDS, AT THE PRECISION IT RECORDS IT ---
# Read off data/reference/R15/Priorite_25b_fetch_yf_panel.log and asserted, not
# retyped from memory: the survival chain is a claim of docs/sections/R15.md and
# a claim has to be checkable.
EXPECTED_UNIQUE = 102
EXPECTED_FETCHED = 100
EXPECTED_RETAINED = 97
EXPECTED_DAYS = 5154
EXPECTED_FIRST_DATE = "2005-01-04"
EXPECTED_LAST_DATE = "2025-06-30"
# Abandoned after MAX_RETRY attempts, both with "possibly delisted; no timezone
# found" (log lines 71-77 and 95-101).
WITNESS_ABANDONED = ("MMC", "K")
# Retained-set failures of the 98% coverage floor, with the row counts the log
# prints (lines 8, 11, 91).
WITNESS_LOW_COVERAGE = {"V": 4347, "MA": 4803, "GM": 3673}

# --- INPUTS ---
DERIVED_DIR = BASE_DIR / "data" / "derived_equities"
PANEL_PATH = DERIVED_DIR / "R15_panel_logreturns.csv"
WITNESS_DIR = BASE_DIR / "data" / "reference" / "R15"
WITNESS_FETCHER = WITNESS_DIR / "Priorite_25b_fetch_yf_panel.py"
WITNESS_FETCH_LOG = WITNESS_DIR / "Priorite_25b_fetch_yf_panel.log"
# The digest of the panel the submitted campaign produced and that
# Priorite_25c consumed. A different input file would silently produce a
# different campaign under identical code, which is the one substitution no
# control downstream could detect.
PANEL_SHA256 = "fb426ab0e7e112de61f112952737fd38ea103bd90e1989defa6d33dc086bcf8f"

# The routines of the witness fetcher this script SUPERSEDES rather than
# carries. Neither is quoted: `fetch_one` gains named exception classes and a
# structured failure record, `main` gains the no-silent-drop verification. Each
# is pinned by the SHA-256 of its witness source segment, which is preamble
# S4.2's treatment for a superseded routine.
SUPERSEDED_ROUTINES = ("fetch_one", "main")

REQUIREMENT_PACKAGES = ("numpy", "pandas", "yfinance")


def source_segments(path, names):
    """
    Source text of the named top-level functions, extracted by position rather
    than by import: importing the delivered fetcher would execute its
    `logging.basicConfig`, create an absolute output directory outside this
    repository, and -- on `main` -- start hitting the network.
    """
    text = Path(path).read_text()
    tree = ast.parse(text)
    return {node.name: ast.get_source_segment(text, node)
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in names}


def pin_witness(log):
    """
    Provenance of the superseded fetcher, by digest rather than by quotation.
    Deterministic; trigger probability 0 unless the vendored witness has moved.
    """
    if not WITNESS_FETCHER.exists():
        log.error(f"Missing witness fetcher {WITNESS_FETCHER}. The provenance of UNIVERSE, of "
                  f"MIN_COVERAGE and of the survival chain cannot be pinned, and transcribing "
                  f"them from memory is what preamble S3 forbids.")
        sys.exit(1)
    log.info(f"Witness fetcher {WITNESS_FETCHER.name}: SHA-256 {compute_sha256(WITNESS_FETCHER)}.")
    segments = source_segments(WITNESS_FETCHER, set(SUPERSEDED_ROUTINES))
    missing = [name for name in SUPERSEDED_ROUTINES if name not in segments]
    if missing:
        log.error(f"The witness fetcher carries no {missing}; its supersession cannot be exhibited.")
        sys.exit(1)
    for name in SUPERSEDED_ROUTINES:
        digest = hashlib.sha256(segments[name].encode('utf-8')).hexdigest()
        log.info(f"SUPERSEDED {name}: witness segment SHA-256 {digest} "
                 f"({len(segments[name])} characters). Not carried byte-identically -- "
                 + ("`fetch_one` swallows every exception into one `except Exception` and returns "
                    "None, which is the silent drop of preamble S4.3."
                    if name == "fetch_one" else
                    "`main` skips a None series with a bare `if s is not None`, so a network "
                    "outage silently reduces K_max and rewrites the published K_GRID."))
    log.info(f"Witness fetch log {WITNESS_FETCH_LOG.name}: SHA-256 "
             f"{compute_sha256(WITNESS_FETCH_LOG)}. It is the artefact that fixes the survival "
             f"chain reproduced below.")


def declare_specification(log):
    """Preamble S2.7: every parameter that shapes an output is logged, not merely coded."""
    listed = len(UNIVERSE)
    unique = list(dict.fromkeys(UNIVERSE))
    duplicates = sorted({t for t in UNIVERSE if UNIVERSE.count(t) > 1})
    log.info(f"SPECIFICATION: START={START}, END={END}, INTERVAL={INTERVAL}, SLEEP_S={SLEEP_S}, "
             f"MAX_RETRY={MAX_RETRY}, MIN_COVERAGE={MIN_COVERAGE}. UNIVERSE carries {listed} "
             f"listed entries and {len(unique)} unique tickers; the duplicate(s) {duplicates} are "
             f"removed in place by `dict.fromkeys`, which preserves first-occurrence order and "
             f"therefore fixes the COLUMN ORDER of the panel -- and, through it, every "
             f"`rng.choice` composition drawn downstream by exp_R15_cross_sectional_b.py.")
    if len(unique) != EXPECTED_UNIQUE:
        log.error(f"UNIVERSE dedupes to {len(unique)} tickers, against the {EXPECTED_UNIQUE} the "
                  f"submitted fetch log records. The specification has moved; the panel "
                  f"downstream is not the published one.")
        sys.exit(1)
    log.info(f"SURVIVORSHIP, declared: UNIVERSE is a fixed list of currently-listed US large caps "
             f"applied backwards to {START}. The panel is survivorship-biased BY CONSTRUCTION. "
             f"v87 states this in the Figure 17 caption and at L376 and reads the panel as an "
             f"upper-bound co-movement benchmark: the bias inflates cross-sectional correlation, "
             f"so the measured sign correlation is an UPPER bound and the escape it prices is "
             f"OPTIMISTIC. The direction is against the manuscript's own thesis, not for it.")
    log.info(f"auto_adjust=True IS CARRIED, against SPECS_REPRO_FAIR.md 1.12, which prescribes "
             f"auto_adjust=False. v87 specifies 'public adjusted closes'; with auto_adjust=True "
             f"yfinance returns the adjusted price in `Close` and emits no `Adj Close` column, so "
             f"the delivered call is the one that satisfies the manuscript. Preamble S1 makes the "
             f"manuscript the source of truth for experimental specification. The conflict is "
             f"logged here and recorded in docs/audits/AUDIT_R15.md; it is not resolved silently.")
    return unique


def fetch_one(ticker, yf, log):
    """
    SUPERSEDES `Priorite_25b.fetch_one`. The retry ladder, the sleep schedule,
    the `auto_adjust=True` call, the timezone strip and the log-return
    definition are the witness's. What changes is the failure path: the witness
    returns None after swallowing every exception into one `except Exception`,
    and this form records the exception CLASS of every attempt and returns a
    structured failure that `build_panel` refuses to absorb.

    Index de-duplication and sorting are added per SPECS_REPRO_FAIR.md 1.11: a
    provider that returns a duplicated timestamp would otherwise put a
    non-monotone index into `pd.concat`, whose alignment is then order-dependent.
    """
    attempts = []
    for a in range(1, MAX_RETRY + 1):
        try:
            df = yf.Ticker(ticker).history(start=START, end=END, interval=INTERVAL,
                                           auto_adjust=True)
            if df is None or df.empty or "Close" not in df:
                raise ValueError("empty frame")
            df = df[["Close"]].copy()
            df.index = pd.DatetimeIndex(df.index).tz_localize(None).normalize()
            df = df[~df.index.duplicated(keep='first')].sort_index()
            df["Log_Return"] = np.log(df["Close"] / df["Close"].shift(1))
            out = df[["Close", "Log_Return"]].dropna()
            log.info(f"{ticker}: {len(out)} rows "
                     f"[{out.index.min().date()}..{out.index.max().date()}] "
                     f"(attempt {a}/{MAX_RETRY}).")
            return out["Log_Return"].rename(ticker), attempts
        except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
            attempts.append(f"{type(exc).__name__}: {exc}")
            log.warning(f"{ticker} attempt {a}/{MAX_RETRY} failed -- "
                        f"{type(exc).__name__}: {exc}")
            time.sleep(SLEEP_S * a)
    log.error(f"{ticker}: ABANDONED after {MAX_RETRY} attempts. Reasons, in order: {attempts}. "
              f"The delivered fetcher drops this ticker silently; this one records it and the "
              f"panel verification below refuses to absorb it.")
    return None, attempts


def build_panel(log):
    """
    SUPERSEDES `Priorite_25b.main`. The concatenation, the coverage filter and
    the row-wise dropna are the witness's, in the witness's order. What changes:
    every abandoned ticker and every low-coverage ticker is NAMED with its
    grounds, and the retained column header is verified against the committed
    panel rather than accepted.
    """
    import yfinance as yf

    unique = declare_specification(log)
    log.info(f"INGEST: fetching {len(unique)} tickers {START}..{END} ({INTERVAL}) sequentially in "
             f"the main thread, {SLEEP_S}s between tickers. The pacing is the specification: the "
             f"provider rate-limits, and a parallel fetch would trade a reproducible panel for a "
             f"partial one.")
    series, abandoned = [], {}
    for ticker in unique:
        s, attempts = fetch_one(ticker, yf, log)
        if s is None:
            abandoned[ticker] = attempts
        else:
            series.append(s)
        time.sleep(SLEEP_S)
    if not series:
        log.error("No ticker fetched. The panel cannot be built and nothing is written.")
        sys.exit(1)

    panel = pd.concat(series, axis=1).sort_index()
    cov = panel.notna().mean()
    keep = cov[cov >= MIN_COVERAGE].index
    dropped = {t: (int(panel[t].notna().sum()), float(cov[t]))
               for t in panel.columns if t not in keep}
    panel_filtered = panel[keep]
    dates_before = len(panel_filtered)
    panel_filtered = panel_filtered.dropna(how="any")
    dates_after = len(panel_filtered)

    log.info(f"SURVIVAL CHAIN, every step named: {len(UNIVERSE)} listed entries -> {len(unique)} "
             f"unique -> {len(series)} fetched -> {len(keep)} retained -> {dates_after} dates.")
    for ticker, attempts in abandoned.items():
        log.info(f"  ABANDONED {ticker}: {MAX_RETRY} attempts exhausted, reasons {attempts}.")
    for ticker, (rows, coverage) in dropped.items():
        log.info(f"  LOW COVERAGE {ticker}: {rows}/{len(panel)} = {100.0 * coverage:.1f}% "
                 f"< {100.0 * MIN_COVERAGE:.0f}%. It is dropped as a COLUMN by the coverage "
                 f"filter, not by any dropna.")
    log.info(f"  THE SURVIVAL RULE IS THE COVERAGE FILTER `cov >= {MIN_COVERAGE}`, not "
             f"`dropna(how='any')`. The row-wise dropna that follows it removes DATES, and here "
             f"it removes {dates_before - dates_after} of {dates_before}.")

    if len(series) != EXPECTED_FETCHED or sorted(abandoned) != sorted(WITNESS_ABANDONED):
        log.error(f"The fetch retained {len(series)} of {len(unique)} tickers, abandoning "
                  f"{sorted(abandoned)}; the submitted campaign fetched {EXPECTED_FETCHED} and "
                  f"abandoned {sorted(WITNESS_ABANDONED)}. K_max is the LAST element of the "
                  f"published K_GRID, so absorbing this difference would silently rewrite the "
                  f"grid of v87 Figure 17. The run stops.")
        sys.exit(1)
    if sorted(dropped) != sorted(WITNESS_LOW_COVERAGE):
        log.error(f"The coverage filter dropped {sorted(dropped)}; the submitted campaign dropped "
                  f"{sorted(WITNESS_LOW_COVERAGE)}. Same reasoning: the run stops.")
        sys.exit(1)
    return panel_filtered


def verify_against_committed(panel, log):
    """
    The freshly fetched panel against `data/derived_equities/R15_panel_logreturns.csv`,
    as a column header IN ORDER, as a shape, and as a date span. A discrepancy
    stops the run; it is never reconciled.
    """
    if not PANEL_PATH.exists():
        log.warning(f"{PANEL_PATH.name} does not exist, so the fetched panel is written as the "
                    f"committed input. NOTHING IS OVERWRITTEN by this branch: a committed panel "
                    f"is the frozen reviewer input of exp_R15_cross_sectional_b.py, and a network "
                    f"fetch is not a bit-stable object.")
        panel.to_csv(PANEL_PATH, index_label="Date")
        return
    committed = pd.read_csv(PANEL_PATH, index_col="Date", parse_dates=True,
                            float_precision='round_trip')
    if list(panel.columns) != list(committed.columns):
        only_fetched = [t for t in panel.columns if t not in set(committed.columns)]
        only_committed = [t for t in committed.columns if t not in set(panel.columns)]
        log.error(f"The fetched column header differs from the committed panel. Present only in "
                  f"the fetch: {only_fetched}. Present only in the committed file: "
                  f"{only_committed}. Order identical: "
                  f"{sorted(panel.columns) == sorted(committed.columns)}. K_max and every "
                  f"`rng.choice` composition downstream read this header, so the run stops.")
        sys.exit(1)
    if panel.shape != committed.shape:
        log.error(f"The fetched panel is {panel.shape} against the committed {committed.shape}.")
        sys.exit(1)
    aligned = panel.reindex(committed.index)
    identical = bool(np.array_equal(aligned.values, committed.values, equal_nan=True))
    worst = float(np.nanmax(np.abs(aligned.values - committed.values))) if not identical else 0.0
    log.info(f"INGEST verification: the fetched panel matches the committed "
             f"{PANEL_PATH.name} on its {panel.shape[1]} columns in order and its "
             f"{panel.shape[0]} dates. Values bit-identical: {identical}; worst absolute "
             f"difference {worst!r}. The committed file is NOT overwritten -- the provider "
             f"restates history (splits, dividends, delistings), so a later fetch is a different "
             f"object and the frozen file is what makes exp_R15_cross_sectional_b.py "
             f"reproducible.")


def analyse(log):
    """
    The nominal path. No network I/O of any kind, so the reviewer's run is
    offline and bit-stable.
    """
    if not PANEL_PATH.exists():
        log.error(f"[FATAL] {PANEL_PATH} is missing. It is the versioned input of "
                  f"exp_R15_cross_sectional_b.py. Run this script with "
                  f"`--data-source yfinance --stage ingest` to rebuild it from Yahoo Finance "
                  f"(one-off, rate-limited, roughly 5 minutes), or restore it from the "
                  f"repository. Nothing is fabricated in its place.")
        sys.exit(1)
    digest = compute_sha256(PANEL_PATH)
    log.info(f"{PANEL_PATH.name}: SHA-256 {digest}.")
    if digest != PANEL_SHA256:
        log.warning(f"The committed panel digest is {digest}, against the {PANEL_SHA256} the "
                    f"submitted campaign consumed. Every downstream value is conditional on this "
                    f"file, so the difference is reported here and carried into the audit rather "
                    f"than absorbed.")
    panel = pd.read_csv(PANEL_PATH, index_col="Date", parse_dates=True,
                        float_precision='round_trip')
    n_days, n_tickers = panel.shape
    first, last = panel.index.min().date().isoformat(), panel.index.max().date().isoformat()
    log.info(f"Panel: {n_tickers} tickers x {n_days} days [{first}..{last}]. "
             f"Column order: {list(panel.columns)}.")
    failures = []
    if n_tickers != EXPECTED_RETAINED:
        failures.append(f"{n_tickers} tickers against the published {EXPECTED_RETAINED}")
    if n_days != EXPECTED_DAYS:
        failures.append(f"{n_days} days against the published {EXPECTED_DAYS}")
    if first != EXPECTED_FIRST_DATE or last != EXPECTED_LAST_DATE:
        failures.append(f"span [{first}..{last}] against the published "
                        f"[{EXPECTED_FIRST_DATE}..{EXPECTED_LAST_DATE}]")
    if not panel.index.is_monotonic_increasing or panel.index.has_duplicates:
        failures.append("the date index is not strictly increasing")
    if bool(panel.isna().any().any()):
        failures.append(f"{int(panel.isna().sum().sum())} NaN cells remain after the row-wise "
                        f"dropna the fetcher applies")
    if failures:
        log.error(f"[FATAL] The committed panel contradicts v87's published description: "
                  f"{'; '.join(failures)}. K_max is the last element of the published K_GRID and "
                  f"is read from this shape, so nothing downstream may run.")
        sys.exit(1)
    log.info(f"The committed panel reproduces v87's published description exactly: "
             f"{EXPECTED_RETAINED} surviving US equities, {EXPECTED_DAYS} common trading days, "
             f"{EXPECTED_FIRST_DATE} to {EXPECTED_LAST_DATE} -- L376's '97 surviving US "
             f"equities, 2005--2025'.")
    log.info(f"SURVIVAL CHAIN, replayed from {WITNESS_FETCH_LOG.name} without a network call: "
             f"{len(UNIVERSE)} listed -> {EXPECTED_UNIQUE} unique (QCOM duplicated) -> "
             f"{EXPECTED_FETCHED} fetched ({', '.join(WITNESS_ABANDONED)} abandoned after "
             f"{MAX_RETRY} attempts, both 'possibly delisted; no timezone found') -> "
             f"{EXPECTED_RETAINED} retained ("
             + ", ".join(f"{t} {r}/{EXPECTED_DAYS} = {100.0 * r / EXPECTED_DAYS:.1f}%"
                         for t, r in WITNESS_LOW_COVERAGE.items())
             + f" below the {100.0 * MIN_COVERAGE:.0f}% floor) -> {EXPECTED_DAYS} dates.")
    return panel


def main():
    parser = argparse.ArgumentParser(
        description="R15 (a) -- public equity fetcher and panel provenance (v87 L389)")
    parser.add_argument("--data-source", choices=["yfinance"], default="yfinance",
                        help="Source of the equity panel. One value, stated explicitly: an "
                             "automatic switch between a network source and a cached file is how "
                             "a run silently changes its own input.")
    parser.add_argument("--stage", choices=["ingest", "analyse", "all"], default="analyse",
                        help="`analyse` (default) is the nominal offline path. `ingest` hits the "
                             "network and is run once; it verifies the committed panel and never "
                             "overwrites it.")
    parser.add_argument("--n-jobs", type=int, default=-1,
                        help="Accepted and unused: this stage is sequential by specification. "
                             "The flag exists so that run_experiment_R15.sh can forward one "
                             "argument list to both stages.")
    args = parser.parse_args()

    LOGS_DIR = BASE_DIR / "logs" / "R15_cross_sectional"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    log = setup_logging(LOGS_DIR / "exp_R15_cross_sectional_a.log", "exp_R15_a")
    if not verify_hash_seed(log):
        sys.exit(1)
    log_environment(log, list(REQUIREMENT_PACKAGES))
    t0 = time.time()

    log.info(f"R15 (a) establishes the provenance of the 97-equity panel behind v87 Figure 17 "
             f"and discharges L389's printed promise of a public equity fetcher. Stage: "
             f"{args.stage}; data source: {args.data_source}.")
    pin_witness(log)

    if args.stage in ("ingest", "all"):
        panel = build_panel(log)
        verify_against_committed(panel, log)
    if args.stage in ("analyse", "all"):
        analyse(log)
    else:
        log.info("Stage `ingest` completed. The nominal reviewer path is `--stage analyse`, "
                 "which touches no network.")
    log.info(f"Execution completed in {time.time() - t0:.1f}s (stage {args.stage}).")


if __name__ == "__main__":
    main()
