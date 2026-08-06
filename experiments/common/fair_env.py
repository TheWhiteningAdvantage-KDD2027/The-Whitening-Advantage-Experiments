"""
==========================================================================
FAIR ENVIRONMENT — DETERMINISM BOOTSTRAP
==========================================================================
This module MUST be imported and invoked before any scientific library is
loaded, directly or transitively. It therefore imports nothing beyond the
standard library: importing `numpy` or `pandas` here would defeat its own
purpose, because BLAS thread limits are read at NumPy load time.

Reference: SPECS_REPRO_FAIR.md, section 1.1.
==========================================================================
"""

import os
import sys

_THREAD_VARIABLES = (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)


def enforce_strict_determinism(legacy_blas: bool = False) -> None:
    """
    Pins single-threaded linear algebra and conditional bitwise reproducibility.

    Multithreaded BLAS/MKL reductions destroy floating-point associativity, so
    the summation order — and hence the last bits of every reduction — becomes a
    function of the scheduler. MKL_CBWR neutralises divergence between vector
    instruction sets (FMA, AVX2, AVX-512).

    Raises RuntimeError if NumPy is already loaded, since the thread limits
    would then be silently ignored.
    """
    if "numpy" in sys.modules:
        raise RuntimeError(
            "NumPy is already imported: BLAS thread limits can no longer take "
            "effect. Call enforce_strict_determinism() before importing numpy, "
            "pandas, scipy, or any module that imports them."
        )
    if legacy_blas:
        # Reproduction mode for the submitted campaign, which predates this
        # repository and ran under multithreaded BLAS. Thread pins and CBWR are
        # deliberately NOT applied, so reductions accumulate in whatever order the
        # scheduler chooses. Output is machine-dependent by construction: two runs
        # on different hosts, or on the same host under different load, may differ
        # in the last bits. This mode exists to demonstrate that the gap between
        # this repository and the manuscript is one environment variable, and it
        # must never be used to certify a result.
        for name in _THREAD_VARIABLES:
            os.environ.pop(name, None)
        os.environ.pop("MKL_CBWR", None)
        return
    for name in _THREAD_VARIABLES:
        os.environ[name] = "1"
    os.environ["MKL_CBWR"] = "COMPATIBLE"


def verify_hash_seed(logger=None, expected: str = "42") -> bool:
    """
    Checks that PYTHONHASHSEED was pinned by the shell before interpreter start.

    Assigning os.environ["PYTHONHASHSEED"] from inside a running interpreter is
    inert: CPython reads the hash seed at start-up. The orchestrator shell script
    is the only place where this variable can be set effectively.
    """
    observed = os.environ.get("PYTHONHASHSEED")
    ok = observed == expected
    message = (
        f"PYTHONHASHSEED correctly pinned to {expected} before interpreter start."
        if ok
        else f"PYTHONHASHSEED is {observed!r}, expected {expected!r}. String hashing "
        f"is randomised: run this script through run_experiment_RXX.sh."
    )
    if logger is not None:
        (logger.info if ok else logger.warning)(message)
    else:
        print(message, file=sys.stdout)
    return ok


def log_environment(logger, packages) -> dict:
    """
    Records the interpreter version and every third-party package version, read
    from installed distribution metadata rather than from module attributes.
    """
    from importlib.metadata import version, PackageNotFoundError

    logger.info(f"Python: {sys.version.split()[0]}")
    resolved = {}
    for name in packages:
        try:
            resolved[name] = version(name)
        except PackageNotFoundError:
            resolved[name] = "NOT INSTALLED"
        logger.info(f"  {name}: {resolved[name]}")
    return resolved