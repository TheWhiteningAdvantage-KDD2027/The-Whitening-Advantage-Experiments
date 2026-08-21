import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["PYTHONHASHSEED"] = "42"
os.environ["MKL_CBWR"] = "COMPATIBLE"

import pandas as pd
import numpy as np
pd.options.compute.use_bottleneck = False
pd.options.compute.use_numexpr = False

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import hashlib
import logging
import sys

BASE_DIR = Path(__file__).resolve().parent if '__file__' in locals() else Path.cwd()
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def setup_logging(base_dir: Path, script_name: str):
    log_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    log_path = base_dir / f"{script_name}.log"
    file_handler = logging.FileHandler(log_path, mode='w')
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

def get_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def plot_adverse_and_lattice():
    import matplotlib.ticker as ticker
    
    csv_21c = FIGURES_DIR / 'protocol_21c_adverse_bias.csv'
    csv_21d = FIGURES_DIR / 'protocol_21d_null_law_lattice.csv'
    
    logging.info(f"MD5 protocol_21c_adverse_bias.csv: {get_md5(csv_21c)}")
    logging.info(f"MD5 protocol_21d_null_law_lattice.csv: {get_md5(csv_21d)}")

    df_21c = pd.read_csv(csv_21c)
    df_21d = pd.read_csv(csv_21d)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5), dpi=300)

    # Panel A: Ljung-Box Rejection
    ax = axes[0]
    ax.grid(True, which='both', alpha=0.3)
    ax.axhline(0.05, color='gray', linestyle=':', label='Target 0.05')

    err_low_lb = np.maximum(0, df_21c['lb_reject_biased'] - df_21c['lb_ci_low'])
    err_high_lb = np.maximum(0, df_21c['lb_ci_high'] - df_21c['lb_reject_biased'])

    label_ols = r"Rolling OLS +" + "\n" + r"injected bias" + "\n" + r"(over-centering, $\phi=0$)"
    label_naive = r"Naive sign" + "\n" + r"(under-centering," + "\n" + r"$\hat\mu_t=0$ at $\phi=b$)"

    ax.errorbar(df_21c['b'], df_21c['lb_reject_biased'], yerr=[err_low_lb, err_high_lb],
                fmt='-o', color='blue', capsize=4, label=label_ols)
    ax.plot(df_21c['b'], df_21c['lb_reject_naive_ref'], '--s', color='red', alpha=0.7, label=label_naive)

    ax.set_xlabel(r'Systematic mis-centering magnitude $b$')
    ax.set_ylabel('Ljung-Box Rejection Rate')
    ax.set_yscale('log')
    ax.set_ylim(0.04, 1.2)
    ax.set_xticks(df_21c['b'])
    ax.set_yticks([0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0])
    ax.get_yaxis().set_major_formatter(ticker.ScalarFormatter())
    ax.get_yaxis().set_minor_formatter(ticker.NullFormatter())
    ax.legend(loc='upper left', frameon=False)

    # Panel B: FPR
    ax = axes[1]
    ax.grid(True, alpha=0.3)
    ax.axhline(0.05, color='gray', linestyle=':', label='Target 0.05')
    ax.axhspan(0.0429, 0.0503, color='gray', alpha=0.2)

    err_low_fpr = np.maximum(0, df_21c['fpr_biased'] - df_21c['fpr_ci_low'])
    err_high_fpr = np.maximum(0, df_21c['fpr_ci_high'] - df_21c['fpr_biased'])

    ax.errorbar(df_21c['b'], df_21c['fpr_biased'], yerr=[err_low_fpr, err_high_fpr],
                fmt='-o', color='blue', capsize=4, label=label_ols)
    ax.plot(df_21c['b'], df_21c['fpr_naive_ref'], '--s', color='red', alpha=0.7, label=label_naive)

    ax.set_xlabel(r'Systematic mis-centering magnitude $b$')
    ax.set_ylabel('False Positive Rate (FPR)')
    ax.set_ylim(0, 0.22)
    ax.set_xticks(df_21c['b'])
    ax.legend(loc='upper left', frameon=False)

    # Panel C: Lattice
    ax = axes[2]
    ax.grid(True, alpha=0.3)
    ax.axhline(0.05, color='gray', linestyle=':', label='Target 0.05')

    ax.plot(df_21d['lambda'], df_21d['P_exceed'], drawstyle='steps-post', color='black', linewidth=1.5)
    ax.plot(df_21d['lambda'], df_21d['P_exceed'], 'ko')

    df_highlight = df_21d[df_21d['lambda'].isin([11.2, 11.4])]
    ax.plot(df_highlight['lambda'], df_highlight['P_exceed'], 'ro', markersize=8, label='Quantile Brackets')

    ax.set_xlabel(r'Critical Value ($\lambda$)')
    ax.set_ylabel(r'Empirical Survival Probability $P(M > \lambda)$')
    ax.set_xticks(df_21d['lambda'])
    ax.legend(loc='upper right', frameon=False)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'Fig26_Adverse_Bias_and_Lattice.png')
    plt.close()

if __name__ == "__main__":
    setup_logging(BASE_DIR, "Priorite_21c_plot_adverse_lattice")
    logging.info("NOTE: Execution order -> Priorite_21c_plot_adverse_lattice (21c) MUST be run LAST.")
    plot_adverse_and_lattice()
    logging.info("Fig26_Adverse_Bias_and_Lattice.png generated successfully.")