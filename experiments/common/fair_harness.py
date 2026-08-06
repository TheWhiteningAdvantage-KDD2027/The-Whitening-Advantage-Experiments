"""
==========================================================================
FAIR HARNESS — COMMON UTILITIES
Strict Determinism, I/O Security, and Traceability
==========================================================================
"""

import os
import hashlib
import logging
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# NOTE: this module imports pandas and numpy at top level and therefore CANNOT
# host the environment bootstrap. Loading it already loads NumPy, at which point
# BLAS thread limits are fixed and any later assignment is inert. The bootstrap
# lives in experiments/common/fair_env.py, which imports only the standard
# library. See SPECS_REPRO_FAIR.md section 1.1.

def disable_pandas_multithreading():
    """
    Must be called IMMEDIATELY AFTER importing pandas.
    """
    pd.options.compute.use_bottleneck = False
    pd.options.compute.use_numexpr = False

def setup_logging(log_path: Path, script_name: str) -> logging.Logger:
    """
    Configures a dual-output logger (Console + File) compliant with FAIR standards.
    """
    log_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(script_name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        file_handler = logging.FileHandler(log_path, mode='w')
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)
        
    return logger

def compute_sha256(filepath: Path) -> str:
    """Computes the SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def save_fair_csv(df: pd.DataFrame, path: Path):
    """
    Saves a DataFrame to CSV ensuring bit-for-bit reproducible floating point strings.
    """
    df.to_csv(path, float_format='%.17g', na_rep='NaN', lineterminator='\n', index=False)