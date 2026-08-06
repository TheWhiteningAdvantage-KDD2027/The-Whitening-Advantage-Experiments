import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["PYTHONHASHSEED"] = "42"
os.environ["MKL_CBWR"] = "COMPATIBLE"

"""
Priorite_7_whitening_boundary.py
=================================
Empirical validation of the Concept Drift Whitening boundaries.

Theoretical Notations:
- Gamma (Γ): GARCH penalty factor, normalized spectral density at zero frequency of the monitored statistic. Values: 1.00 to 200.00.
- p_data: Ljung-Box p-value on squared innovations stream.
- p_concept: Ljung-Box p-value on binary sign error stream, evaluated on identical trajectories as p_data. Ref: Ljung, G. M. & Box, G. E. P. (1978), Biometrika 65(2).
- task_type: Test variant in Part B. 'binary' evaluates non-median binarization threshold; 'continuous' evaluates MSE continuous loss.
- c: Drift magnitude injected, expressed in conditional standard deviation units.

This script produces a two-panel mapping (Figure 11):
    - Part A (Gamma boundary): Evaluates the insensitivity of the binary error
      stream (Concept Drift) to extreme GARCH variance inflation, bridging the
      gap up to Gamma=200, and plotting the 4th moment existence boundary.
    - Part B (Task boundary): Demonstrates that the whitening effect structurally
      fails when predicting non-median thresholds (c != 0) or outputting 
      continuous losses.

It complies with MLOps best practices: deterministic seeds, typed interfaces,
multiprocessing, and rigorous asymptotic confidence intervals (Wilson).
"""

import argparse
import importlib.metadata
import logging
import sys
import time
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
pd.set_option("compute.use_bottleneck", False)
pd.set_option("compute.use_numexpr", False)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from joblib import Parallel, delayed
from tqdm import tqdm
from statsmodels.stats.diagnostic import acorr_ljungbox
import scipy.stats as stats
from scipy.optimize import root_scalar

from river import tree as river_tree

def setup_logging(base_dir: Path, script_name: str) -> logging.Logger:
    """
    Configures a dual-output logger (Console + File) compliant with FAIR standards.
    - Console: Real-time monitoring via stdout (forces sys.stdout over stderr for standard traces).
    - File: Persistent, reproducible traceability via FileHandler.
    """
    log_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(script_name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        log_path = base_dir / f"{script_name}.log"
        file_handler = logging.FileHandler(log_path, mode='w')
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)
        
    return logger

# ─── MLOPS / PATHS CONSTANTS ───────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent if '__file__' in locals() else Path.cwd()
RESULTS_DIR = BASE_DIR / "figures"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ─── EXPERIMENTAL CONSTANTS ────────────────────────────────────────────────
N_STEPS = 8_000
LB_LAGS = 20
ALPHA_LB = 0.05
TARGET_VAR = 0.04
CONFIDENCE_LEVEL = 0.95

# Visual metadata matching the paper's style
BLUE   = '#04617b'
ORANGE = '#E8A000'
RED    = '#C62828'
GRAY   = '#546E7A'

plt.rcParams.update({
    'figure.dpi'        : 300,
    'font.family'       : 'sans-serif',
    'font.size'         : 11,
    'axes.spines.top'   : False,
    'axes.spines.right' : False,
    'axes.facecolor'    : 'white',
    'figure.facecolor'  : 'white',
    'mathtext.fontset'  : 'stix',
})


# ═══════════════════════════════════════════════════════════════════════════
# STATISTICAL PROCEDURES & WILSON INTERVALS
# ═══════════════════════════════════════════════════════════════════════════
def wilson_ci(k: int, n: int, confidence: float = 0.95) -> tuple:
    """
    Computes the asymmetric Wilson score interval for a binomial proportion.
    Returns absolute lower and upper bounds.
    """
    if n == 0:
        return 0.0, 0.0
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt((p * (1 - p)) / n + z**2 / (4 * n**2))) / denom
    return max(0.0, center - margin), min(1.0, center + margin)

def lb_pvalue(series: np.ndarray, lag: int = LB_LAGS) -> float:
    """Computes the Ljung-Box p-value for a given lag."""
    try:
        # Avoid potential singular matrix issues on perfectly constant streams
        if np.std(series) < 1e-12:
            return 1.0
        res = acorr_ljungbox(series, lags=[lag], return_df=True)
        return float(res['lb_pvalue'].iloc[0])
    except Exception:
        return np.nan


# ═══════════════════════════════════════════════════════════════════════════
# GARCH THEORETICAL BOUNDARIES
# ═══════════════════════════════════════════════════════════════════════════
def gamma_exact(alpha: float, beta: float) -> float:
    """
    Computes the exact GARCH penalty factor Gamma under Gaussian / nominal
    ARMA(1,1) closed-form approximations.
    """
    if alpha == 0.0 and beta == 0.0:
        return 1.0
    phi = alpha + beta
    denom = 1.0 - 2.0 * alpha * beta - beta ** 2
    if denom <= 0.0 or phi >= 1.0:
        return float('inf')
    rho1 = alpha * (1.0 - beta * phi) / denom
    return 1.0 + 2.0 * rho1 / (1.0 - phi)

def boundary_4th_moment_beta(alpha: float, kurtosis: float = 5.0) -> float:
    """
    Computes the beta threshold where the 4th moment diverges for a given alpha.
    Kurtosis = 5.0 for a standardized Student-t with 7 degrees of freedom.
    Solves: kurtosis * alpha^2 + 2 * alpha * beta + beta^2 = 1.
    """
    def f(beta):
        return kurtosis * (alpha**2) + 2 * alpha * beta + beta**2 - 1.0
    res = root_scalar(f, bracket=[0.0, 1.0 - alpha])
    return res.root

def solve_beta_for_gamma(alpha: float, target_gamma: float) -> float:
    """Solves for beta to attain a target Gamma given alpha."""
    if target_gamma == 1.0:
        return 0.0
    # Find the pole where the denominator (1 - 2*alpha*beta - beta^2) hits 0.
    beta_pole = np.sqrt(alpha**2 + 1.0) - alpha
    
    def f(beta):
        return gamma_exact(alpha, beta) - target_gamma
    
    res = root_scalar(f, bracket=[0.0, beta_pole - 1e-6], method='brentq')
    return res.root


# ═══════════════════════════════════════════════════════════════════════════
# GARCH SIMULATOR & TASKS
# ═══════════════════════════════════════════════════════════════════════════
def generate_garch(alpha: float, beta: float, seed: int, n_steps: int, target_var: float) -> np.ndarray:
    """Generates a stationary GARCH(1,1) time series with Student-t7 innovations."""
    np.random.seed(seed)
    omega = target_var * (1.0 - alpha - beta) if (alpha + beta) < 1.0 else 0.0
    eps = np.zeros(n_steps)
    h = np.zeros(n_steps)
    h[0] = target_var
    
    nu = 7.0
    # Standardized student-t distribution (mean 0, variance 1)
    z = np.random.standard_t(nu, size=n_steps) * np.sqrt((nu - 2.0) / nu)
    eps[0] = np.sqrt(h[0]) * z[0]

    for t in range(1, n_steps):
        h[t] = max(omega + alpha * eps[t - 1] ** 2 + beta * h[t - 1], 1e-12)
        eps[t] = np.sqrt(h[t]) * z[t]

    return eps

def evaluate_sign_task(eps: np.ndarray, c: float, sigma_unc: float) -> np.ndarray:
    """
    Runs an online HoeffdingTreeClassifier sequentially and computes binary errors.
    The threshold evaluates non-median binarization if c != 0.0.
    """
    n_steps = len(eps)
    rv = pd.Series(eps).rolling(20, min_periods=1).std(ddof=1).fillna(0.0).values
    ht = river_tree.HoeffdingTreeClassifier()
    errs = np.zeros(n_steps, dtype=float)
    
    threshold = c * sigma_unc

    for t in range(n_steps):
        lag1 = eps[t - 1] if t >= 1 else 0.0
        lag2 = eps[t - 2] if t >= 2 else 0.0
        x_dict = {0: lag1, 1: lag2, 2: abs(lag1), 3: rv[t]}
        
        yt = int(eps[t] > threshold)
        yp = ht.predict_one(x_dict) or 0
        errs[t] = float(yp != yt)
        ht.learn_one(x_dict, yt)

    return errs

def evaluate_continuous_loss(eps: np.ndarray) -> np.ndarray:
    """
    Evaluates a trivial continuous forecaster (non-anticipative moving average).
    Returns the squared continuous loss.
    """
    df = pd.Series(eps)
    r_hat = df.shift(1).rolling(20, min_periods=1).mean().fillna(0.0).values
    loss = (eps - r_hat) ** 2
    return loss


# ═══════════════════════════════════════════════════════════════════════════
# PARALLEL WORKERS
# ═══════════════════════════════════════════════════════════════════════════
def worker_partA(gamma: float, alpha: float, beta: float, seed: int) -> dict:
    eps = generate_garch(alpha, beta, seed, N_STEPS, TARGET_VAR)
    # Ljung-Box on Data Drift (epsilon^2)
    p_data = lb_pvalue(eps ** 2)
    # Ljung-Box on Concept Drift (c=0)
    sigma_unc = np.sqrt(TARGET_VAR)
    e_bin = evaluate_sign_task(eps, c=0.0, sigma_unc=sigma_unc)
    p_concept = lb_pvalue(e_bin)
    
    return {'gamma': gamma, 'seed': seed, 'p_data': p_data, 'p_concept': p_concept}

def worker_partB(task_type: str, c: float, seed: int, alpha: float, beta: float) -> dict:
    eps = generate_garch(alpha, beta, seed, N_STEPS, TARGET_VAR)
    sigma_unc = np.sqrt(TARGET_VAR)
    
    if task_type == 'binary':
        errs = evaluate_sign_task(eps, c=c, sigma_unc=sigma_unc)
    else:
        errs = evaluate_continuous_loss(eps)
        
    p_val = lb_pvalue(errs)
    return {'task_type': task_type, 'c': c, 'seed': seed, 'p_val': p_val}


# ═══════════════════════════════════════════════════════════════════════════
# PLOTTING ROUTINE
# ═══════════════════════════════════════════════════════════════════════════
def plot_figure(df_A: pd.DataFrame, df_B: pd.DataFrame, n_seeds: int, 
                gamma_star: float, alpha_fixed: float, out_path: Path):
    
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.0))
    
    # ─── PANEL A: Gamma Boundary ──────────────────────────────────────────
    ax_A = axes[0]
    gammas = sorted(df_A['gamma'].unique())
    
    x_g, y_data, y_concept = [], [], []
    ci_concept_low, ci_concept_high = [], []
    
    for g in gammas:
        sub = df_A[df_A['gamma'] == g]
        # Data drift
        k_data = (sub['p_data'] < ALPHA_LB).sum()
        y_data.append((k_data / n_seeds) * 100.0)
        # Concept drift
        k_concept = (sub['p_concept'] < ALPHA_LB).sum()
        p_c = k_concept / n_seeds
        low, high = wilson_ci(k_concept, n_seeds, CONFIDENCE_LEVEL)
        
        x_g.append(g)
        y_concept.append(p_c * 100.0)
        ci_concept_low.append(low * 100.0)
        ci_concept_high.append(high * 100.0)
        
    ax_A.plot(x_g, y_data, marker='o', color=RED, lw=2, label=r'Data Drift ($\varepsilon_t^2$)')
    ax_A.plot(x_g, y_concept, marker='s', color=BLUE, lw=2, label=r'Concept Drift ($e_t^{\rm bin}$)')
    ax_A.fill_between(x_g, ci_concept_low, ci_concept_high, color=BLUE, alpha=0.15,
                      label='95% Wilson CI')
    
    # Signif threshold
    ax_A.axhline(ALPHA_LB * 100, color=GRAY, linestyle='--', lw=1.5, alpha=0.8,
                 label=rf'Nominal rate ($\alpha={ALPHA_LB}$)')
                 
    # 4th moment boundary
    ax_A.axvline(gamma_star, color='black', linestyle=':', lw=1.8, alpha=0.75,
                 label=r'Finite $\mathbb{E}[\varepsilon^4]$ limit')
    
    # Annotations for canonical regimes (Moved above Wilson CI)
    ax_A.annotate('Cal. A\n(ProteuS)', xy=(8.16, 15), xytext=(8.16, 35),
                  arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.2),
                  ha='center', va='bottom', fontsize=9, color=GRAY, fontweight='bold')
    ax_A.annotate('Cal. B\n(ProteuS)', xy=(30.85, 15), xytext=(30.85, 35),
                  arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.2),
                  ha='center', va='bottom', fontsize=9, color=GRAY, fontweight='bold')

    ax_A.set_xscale('log')
    ax_A.set_xticks([1, 5, 20, gamma_star, 100, 200])
    ax_A.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    
    ax_A.set_ylim(-5, 105)
    ax_A.set_xlabel(r'GARCH Penalty Factor ($\Gamma$)', fontsize=11)
    ax_A.set_ylabel('% Rejecting Null (Ljung-Box lag=20)', fontsize=11)
    ax_A.set_title(r'A. $\Gamma$-Insensitivity & Moment Boundary', fontsize=12, fontweight='bold')
    ax_A.legend(loc='center right', bbox_to_anchor=(0.98, 0.75), fontsize=9, framealpha=0.9)


    # ─── PANEL B: Task Boundary ───────────────────────────────────────────
    ax_B = axes[1]
    
    labels, y_b, err_low, err_high, colors = [], [], [], [], []
    
    # Process Binary tasks
    for c in [0.0, 0.25, 0.5, 1.0]:
        sub = df_B[(df_B['task_type'] == 'binary') & (df_B['c'] == c)]
        k = (sub['p_val'] < ALPHA_LB).sum()
        p = k / n_seeds
        low, high = wilson_ci(k, n_seeds, CONFIDENCE_LEVEL)
        
        lbl = 'Median\n($c=0$)' if c == 0.0 else f'$c={c}$'
        labels.append(lbl)
        y_b.append(p * 100)
        err_low.append(max(0.0, p - low) * 100)
        err_high.append(max(0.0, high - p) * 100)
        colors.append(BLUE if c == 0.0 else ORANGE)
        
    # Process Continuous loss task
    sub_c = df_B[df_B['task_type'] == 'continuous']
    k_c = (sub_c['p_val'] < ALPHA_LB).sum()
    p_c = k_c / n_seeds
    low_c, high_c = wilson_ci(k_c, n_seeds, CONFIDENCE_LEVEL)
    
    labels.append('Cont. Loss\n(MSE)')
    y_b.append(p_c * 100)
    err_low.append(max(0.0, p_c - low_c) * 100)
    err_high.append(max(0.0, high_c - p_c) * 100)
    colors.append(RED)

    # Plot Bars
    x_pos = np.arange(len(labels))
    ax_B.bar(x_pos, y_b, yerr=[err_low, err_high], color=colors, alpha=0.85, 
             capsize=5, edgecolor='black', lw=0.8)
             
    # Signif threshold
    ax_B.axhline(ALPHA_LB * 100, color=GRAY, linestyle='--', lw=1.5, alpha=0.8)
    
    # Formatting
    ax_B.set_xticks(x_pos)
    ax_B.set_xticklabels(labels, fontsize=10)
    ax_B.set_ylim(-5, 105)
    ax_B.set_ylabel('% Rejecting Null (Ljung-Box lag=20)', fontsize=11)
    ax_B.set_title(r'B. Scope Limits: Thresholds & Continuous Loss (Cal. B: $\Gamma\approx 30.8$)', fontsize=12, fontweight='bold')
    
    # Legend for error bars
    ax_B.plot([], [], color='black', lw=1.5, marker='|', markersize=8, 
              label='95% Wilson\nConfidence Interval')
    ax_B.legend(loc='upper left', fontsize=9, framealpha=0.9)

    # Global Title & Footer
    fig.suptitle('Empirical Validity Map of the Concept-Drift Whitening Theorem', 
                 fontsize=14, fontweight='bold', y=1.03)
    
    footer_text = (f'{n_seeds} independent streams per point | n={N_STEPS} | '
                   f'Student-t7 innovations | Non-adaptive Hoeffding Tree online')
    fig.text(0.5, -0.05, footer_text, ha='center', fontsize=10, color=GRAY)

    plt.tight_layout()
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    
    logger = logging.getLogger("Priorite_7_whitening_boundary")
    logger.info(f"Figure saved: {out_path}")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════
def _check_collision_and_assert(seeds_list: list, group_names: dict, logger: logging.Logger):
    """
    Ensures seed uniqueness constraint across streams.
    Intra-group collisions are fatal (statistical duplication).
    Inter-group collisions (CRN) are logged but structurally acceptable.
    """
    total_seeds = len(seeds_list)
    unique_seeds = len(set(seeds_list))
    
    logger.info(f"Seed evaluation: {total_seeds} tasks requested.")
    
    for name, group_seeds in group_names.items():
        if len(group_seeds) != len(set(group_seeds)):
            logger.error(f"Critical intra-group seed collision detected in {name}.")
            sys.exit(1)
            
    if unique_seeds != total_seeds:
        logger.info(f"Inter-group seed collision (Common Random Numbers) detected. Unique seeds: {unique_seeds}/{total_seeds}.")
    else:
        logger.info("All seeds across all grids and variants are strictly unique.")


def evaluate_empirical_certifications(df_A: pd.DataFrame, df_B: pd.DataFrame, logger: logging.Logger, n_seeds: int):
    """
    Evaluates invariants specified in empirical certifications.
    Terminates execution if constraints deviate.
    """
    TOL = 1e-9
    
    rej_data_1 = (df_A[df_A['gamma'] == 1.0]['p_data'] < 0.05).sum() / n_seeds
    if abs(rej_data_1 - 0.06) > TOL:
        logger.error(f"Data stream invariant broken at Gamma=1.00: expected 0.06, got {rej_data_1}")
        sys.exit(1)
        
    for g in df_A['gamma'].unique():
        if g >= 2.0:
            rej_g = (df_A[df_A['gamma'] == g]['p_data'] < 0.05).sum() / n_seeds
            if abs(rej_g - 1.00) > TOL:
                logger.error(f"Data stream invariant broken at Gamma={g}: expected 1.00, got {rej_g}")
                sys.exit(1)
                
    expected_concept = {
        1.0: 0.03, 2.0: 0.07, 5.0: 0.02, 8.16: 0.06, 11.58: 0.05,
        20.0: 0.02, 30.85: 0.05, 41.0: 0.05, 60.0: 0.03, 90.0: 0.06,
        120.0: 0.03, 160.0: 0.07, 200.0: 0.08
    }
    
    logger.info("Grid A 95% Wilson CIs for nominal rates:")
    for g, exp_rate in expected_concept.items():
        sub = df_A[df_A['gamma'] == g]
        k_rej = (sub['p_concept'] < 0.05).sum()
        rej_g = k_rej / n_seeds
        if abs(rej_g - exp_rate) > TOL:
            logger.error(f"Concept stream invariant broken at Gamma={g}: expected {exp_rate}, got {rej_g}")
            sys.exit(1)
        low, high = wilson_ci(k_rej, n_seeds, 0.95)
        logger.info(f"  Gamma={g:>6}: rate={rej_g:.2f}, CI=[{low:.4f}, {high:.4f}] (Contains 0.05: {low <= 0.05 <= high})")
        if not (low <= 0.05 <= high):
            logger.error(f"Wilson interval for Gamma={g} does not contain 0.05.")
            sys.exit(1)
            
    expected_partB = {
        ('binary', 0.0): 0.07,
        ('binary', 0.25): 0.44,
        ('binary', 0.5): 1.00,
        ('binary', 1.0): 1.00,
        ('continuous', 0.0): 1.00
    }
    
    for (t_type, c_val), exp_rate in expected_partB.items():
        sub = df_B[(df_B['task_type'] == t_type) & (df_B['c'] == c_val)]
        rej_b = (sub['p_val'] < 0.05).sum() / n_seeds
        if abs(rej_b - exp_rate) > TOL:
            logger.error(f"Task invariant broken for {t_type} c={c_val}: expected {exp_rate}, got {rej_b}")
            sys.exit(1)
            
    logger.info("All programmatic statistical certifications passed successfully.")


def export_reproducible_csv(df: pd.DataFrame, out_path: Path):
    """
    Exports DataFrame to CSV with strictly deterministic I/O representation.
    """
    df.to_csv(out_path, index=False, float_format='%.17g', na_rep='NaN')


def hash_file(filepath: Path) -> str:
    """Computes SHA-256 hash of a file for CI deterministic verification."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def main(fast: bool = False):
    start_time = time.time()
    logger = setup_logging(BASE_DIR, "Priorite_7_whitening_boundary")
    
    logger.info("=" * 70)
    logger.info("  Priorité 7 : Cartographie de la frontière du théorème de Whitening")
    logger.info("=" * 70)

    with open(BASE_DIR / "requirements.txt", "w") as f:
        packages = ["numpy", "pandas", "scipy", "statsmodels", "matplotlib", "tqdm", "joblib", "river"]
        for pkg in packages:
            try:
                version = importlib.metadata.version(pkg)
                f.write(f"{pkg}=={version}\n")
                logger.info(f"Dependency locked: {pkg}=={version}")
            except importlib.metadata.PackageNotFoundError:
                logger.warning(f"Dependency {pkg} not found in current environment.")

    if fast:
        logger.info("[!] Mode --fast activé (grille légère, 5 seeds)")
        grid_gamma = [1, 8.16, 41, 120]
        n_seeds = 5
    else:
        grid_gamma = [1, 2, 5, 8.16, 11.58, 20, 30.85, 41, 60, 90, 120, 160, 200]
        n_seeds = 100

    alpha_fixed = 0.08
    
    beta_star = boundary_4th_moment_beta(alpha_fixed, kurtosis=5.0)
    gamma_star = gamma_exact(alpha_fixed, beta_star)
    logger.info(f"Boundaries: alpha={alpha_fixed} | 4th Moment diverges at beta={beta_star:.4f}")
    logger.info(f"Boundaries: Equivalent nominal Gamma: {gamma_star:.2f}")

    tasks_A = []
    all_seeds = []
    group_seeds = {}
    
    for gamma in grid_gamma:
        beta = 0.0 if gamma == 1.0 else solve_beta_for_gamma(alpha_fixed, gamma)
        alpha = 0.0 if gamma == 1.0 else alpha_fixed
        g_seeds = []
        for seed in range(1, n_seeds + 1):
            tasks_A.append((gamma, alpha, beta, seed))
            all_seeds.append(seed)
            g_seeds.append(seed)
        group_seeds[f"Gamma_{gamma}"] = g_seeds

    logger.info(f"Running Gamma Grid ({len(tasks_A)} streams)...")
    results_A = Parallel(n_jobs=-1)(
        delayed(worker_partA)(g, a, b, s) for g, a, b, s in tqdm(tasks_A)
    )
    df_A = pd.DataFrame(results_A)
    csv_path_A = RESULTS_DIR / "whitening_boundary_gridA.csv"
    export_reproducible_csv(df_A, csv_path_A)

    alpha_B, beta_B = 0.1058, 0.8742
    tasks_B = []
    for c in [0.0, 0.25, 0.5, 1.0]:
        g_seeds = []
        for seed in range(1, n_seeds + 1):
            tasks_B.append(('binary', c, seed, alpha_B, beta_B))
            all_seeds.append(seed)
            g_seeds.append(seed)
        group_seeds[f"binary_c_{c}"] = g_seeds

    g_seeds = []
    for seed in range(1, n_seeds + 1):
        tasks_B.append(('continuous', 0.0, seed, alpha_B, beta_B))
        all_seeds.append(seed)
        g_seeds.append(seed)
    group_seeds["continuous_c_0.0"] = g_seeds
        
    logger.info(f"Running Task Configurations ({len(tasks_B)} streams)...")
    results_B = Parallel(n_jobs=-1)(
        delayed(worker_partB)(t, c, s, a, b) for t, c, s, a, b in tqdm(tasks_B)
    )
    df_B = pd.DataFrame(results_B)
    csv_path_B = RESULTS_DIR / "whitening_boundary_partB.csv"
    export_reproducible_csv(df_B, csv_path_B)

    if not fast:
        if len(df_A) != 1300 or len(df_B) != 500:
            logger.error("Data cardinality mismatch: expected 1300 (A) and 500 (B).")
            sys.exit(1)
        
        _check_collision_and_assert(all_seeds, group_seeds, logger)
        evaluate_empirical_certifications(df_A, df_B, logger, n_seeds)

    out_fig = RESULTS_DIR / "Fig11_Whitening_Boundary.png"
    plot_figure(df_A, df_B, n_seeds, gamma_star, alpha_fixed, out_fig)
    
    logger.info(f"SHA-256 Grid A (CSV): {hash_file(csv_path_A)}")
    logger.info(f"SHA-256 Part B (CSV): {hash_file(csv_path_B)}")
    
    elapsed = time.time() - start_time
    logger.info(f"Execution Complete. Total elapsed time: {elapsed:.2f} seconds.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Whitening Boundary Validator")
    parser.add_argument('--fast', action='store_true', help="Fast mode for rapid prototyping.")
    args = parser.parse_args()
    main(fast=args.fast)