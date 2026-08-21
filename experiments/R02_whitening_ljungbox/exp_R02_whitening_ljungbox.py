import sys
import logging
import random
import hashlib
import itertools
import argparse
from pathlib import Path

try:
    BASE_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = BASE_DIR.parent.parent
    sys.path.insert(0, str(PROJECT_ROOT))
except NameError:
    BASE_DIR = Path.cwd()
    PROJECT_ROOT = BASE_DIR
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.common.fair_env import enforce_strict_determinism, verify_hash_seed, log_environment

enforce_strict_determinism()

import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from joblib import Parallel, delayed

import river
from river import tree as river_tree

from experiments.common.fair_harness import disable_pandas_multithreading, log_artifact_manifest, save_fair_csv, setup_logging

disable_pandas_multithreading()

verify_hash_seed()

# ─── FAIR PATH RESOLUTION ──────────────────────────────────────────────
RESULTS_DIR = PROJECT_ROOT / "results" / "R02_whitening_ljungbox"
DATA_DIR = RESULTS_DIR / "data"
FIGS_DIR = RESULTS_DIR / "figures"
TABS_DIR = RESULTS_DIR / "tables"
LOGS_DIR = PROJECT_ROOT / "logs" / "R02_whitening_ljungbox"

for d in [DATA_DIR, FIGS_DIR, TABS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── LOGGING CONFIGURATION ─────────────────────────────────────────────
logger = setup_logging(LOGS_DIR / "exp_R02_whitening_ljungbox.log", "exp_R02_whitening_ljungbox")

# Log environment
log_environment(logger, ["numpy", "pandas", "scipy", "river", "matplotlib", "joblib"])

# ─── NOTATIONS AND GLOBAL PARAMETERS ───────────────────────────────────
"""
ε_t           : Standardized GARCH(1,1) innovation (Student-t7).
Γ             : GARCH penalty factor, long-run variance inflation.
e_t^bin       : Binary error indicator of the online classifier.
p_data        : Ljung-Box p-value on (ε_t)^2.
p_concept     : Ljung-Box p-value on e_t^bin.
error_rate    : Empirical mean of e_t^bin.
pearson_r     : Cross-correlation of p_concept between ETFs.
"""

SEEDS      = list(range(1, 31))
N_STEPS    = 8000
LB_LAGS    = 20
ALPHA_LB   = 0.05
TARGET_VAR = 0.04
NU         = 7.0

ETF_PARAMS_A = {
    'SPY': {'alpha': 0.08,  'beta': 0.88},
    'PFF': {'alpha': 0.05,  'beta': 0.90},
    'VNQ': {'alpha': 0.12,  'beta': 0.82},
    'BWX': {'alpha': 0.04,  'beta': 0.92},
}

ETF_PARAMS_B = {
    'SPY': {'alpha': 0.09,  'beta': 0.893},
    'PFF': {'alpha': 0.062, 'beta': 0.928},
    'VNQ': {'alpha': 0.115, 'beta': 0.875},
    'BWX': {'alpha': 0.055, 'beta': 0.940},
}
ETFS = ['SPY', 'PFF', 'VNQ', 'BWX']

# ─── SCIENTIFIC PRIMITIVES ─────────────────────────────────────────────
def get_deterministic_seed(*args) -> tuple:
    def format_arg(arg):
        if isinstance(arg, (float, np.floating)):
            return float(arg).hex()
        return str(arg)
    s = "_".join(map(format_arg, args))
    h = hashlib.md5(s.encode('utf-8')).hexdigest()
    # Returns (full_128_bit_entropy, legacy_32_bit_seed)
    return int(h, 16), int(h[:8], 16)

def gamma_exact(alpha: float, beta: float) -> float:
    if alpha == 0.0 and beta == 0.0:
        return 1.0
    phi = alpha + beta
    denom = 1.0 - 2.0 * alpha * beta - beta ** 2
    if denom <= 0.0 or phi >= 1.0:
        return float('inf')
    rho1 = alpha * (1.0 - beta * phi) / denom
    return 1.0 + 2.0 * rho1 / (1.0 - phi)

def wilson_score_interval(k: int, n: int, confidence: float = 0.95) -> tuple:
    if n == 0: return 0.0, 0.0
    p_hat = k / n
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n)) / denom
    return max(0.0, float(center - margin)), min(1.0, float(center + margin))

def lb_pvalue(series: np.ndarray, lags: int = 20) -> tuple:
    n = len(series)
    mean = np.mean(series)
    denom = np.sum((series - mean) ** 2)
    if denom == 0.0:
        return 1.0, True
    r = np.zeros(lags)
    for k in range(1, lags + 1):
        num = np.sum((series[k:] - mean) * (series[:-k] - mean))
        r[k-1] = num / denom
    k_arr = np.arange(1, lags + 1)
    q_stat = n * (n + 2) * np.sum((r ** 2) / (n - k_arr))
    return float(stats.chi2.sf(q_stat, df=lags)), False

# ─── DISTRIBUTED WORKER ────────────────────────────────────────────────
def simulate_task(task_id: int, regime: str, etf: str, seed: int, alpha: float, beta: float) -> tuple:
    logs = []
    try:
        seed_128, legacy_seed = get_deterministic_seed(regime, etf, seed)
        
        np.random.seed(legacy_seed)
        random.seed(legacy_seed)
        
        # Absolute 128-bit int injection (bypassing Numpy sequence hashing)
        ss = np.random.SeedSequence(seed_128)
        rng = np.random.default_rng(ss)
        
        omega = TARGET_VAR * (1.0 - alpha - beta)
        eps = np.zeros(N_STEPS)
        h = np.zeros(N_STEPS)
        h[0] = omega / (1.0 - alpha - beta) if (alpha + beta) < 1.0 else TARGET_VAR
        
        z = rng.standard_t(NU, size=N_STEPS) * np.sqrt((NU - 2.0) / NU)
        eps[0] = np.sqrt(h[0]) * z[0]
        
        for t in range(1, N_STEPS):
            h[t] = max(omega + alpha * (eps[t - 1] ** 2) + beta * h[t - 1], 1e-12)
            eps[t] = np.sqrt(h[t]) * z[t]
            
        rv = pd.Series(eps).rolling(20, min_periods=1).std(ddof=1).fillna(0.0).values
        
        ht = river_tree.HoeffdingTreeClassifier()
        errs = np.zeros(N_STEPS, dtype=float)
        
        for t in range(N_STEPS):
            lag1 = eps[t - 1] if t >= 1 else 0.0
            lag2 = eps[t - 2] if t >= 2 else 0.0
            x_dict = {0: lag1, 1: lag2, 2: abs(lag1), 3: rv[t]}
            yt = int(eps[t] > 0)
            yp_raw = ht.predict_one(x_dict)
            yp = max(yp_raw, key=yp_raw.get) if isinstance(yp_raw, dict) and yp_raw else int(yp_raw or 0)
            errs[t] = float(yp != yt)
            ht.learn_one(x_dict, yt)
            
        p_data, p_data_deg = lb_pvalue(eps ** 2, LB_LAGS)
        p_concept, p_concept_deg = lb_pvalue(errs, LB_LAGS)
        
        if p_data_deg or p_concept_deg:
            logs.append(('WARNING', f"Degenerate Ljung-Box (denom=0) for {regime}-{etf}-{seed}"))
            
        res = {
            'regime': regime,
            'etf': etf,
            'seed': seed,
            'alpha': alpha,
            'beta': beta,
            'gamma_penalty': gamma_exact(alpha, beta),
            'p_data': p_data,
            'p_concept': p_concept,
            'error_rate': float(np.mean(errs)),
            'classifier_version': river.__version__,
            'degenerate': int(p_data_deg or p_concept_deg)
        }
        return task_id, res, logs
    except Exception as e:
        logs.append(('ERROR', f"Exception in cell {regime}-{etf}-{seed}: {str(e)}"))
        return task_id, {'error': True}, logs

# ─── CORE PIPELINE ─────────────────────────────────────────────────────
def plot_figure(df: pd.DataFrame, out_path: Path) -> None:
    cals_ordered = ['IID', 'Cal. A', 'Cal. B']
    rng_jitter = np.random.default_rng(42)

    BLUE, ORANGE, RED, GRAY = '#04617b', '#E8A000', '#C62828', '#546E7A'
    REGIMES_META = {
        'IID':    {'label': r'IID ($\Gamma=1$)', 'color': GRAY},
        'Cal. A': {'label': r'Cal. A ($\Gamma\in[4,8]$)', 'color': ORANGE},
        'Cal. B': {'label': r'Cal. B ($\Gamma\in[32,110]$)', 'color': BLUE},
    }

    plt.rcParams.update({
        'figure.dpi': 300, 'font.family': 'sans-serif', 'font.size': 11,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.facecolor': 'white', 'figure.facecolor': 'white', 'mathtext.fontset': 'stix',
    })

    fig, axes = plt.subplots(1, 2, figsize=(10, 5.0), sharey=True)

    panels = [
        (axes[0], 'p_data', r'(A) Ljung-Box p-values: $\varepsilon_t^2$ (Data Drift input)', RED, "GARCH detected:\np << 0.05 for Cal. A and Cal. B"),
        (axes[1], 'p_concept', r'(B) Ljung-Box p-values: $e_t^{\mathrm{bin}}$ (HT Concept Drift input)', BLUE, None),
    ]

    for ax, col, title, annot_color, annot_txt in panels:
        box_data = []
        for i, rname in enumerate(cals_ordered):
            sub = df[df['regime'] == rname][col].dropna().values
            color = REGIMES_META[rname]['color']
            box_data.append(sub)
            jitter = rng_jitter.uniform(-0.18, 0.18, size=len(sub))
            ax.scatter(i + jitter, sub, color=color, alpha=0.25, s=8, zorder=2)
            pct_reject = (sub < ALPHA_LB).mean() * 100
            ax.text(i, -0.11, f'{pct_reject:.0f}%', ha='center', va='top', fontsize=9, fontweight='bold', color=color, transform=ax.get_xaxis_transform())

        bp = ax.boxplot(box_data, positions=range(len(cals_ordered)), widths=0.32, patch_artist=True, manage_ticks=False, zorder=3,
                        medianprops=dict(color='black', lw=2.0), whiskerprops=dict(color=GRAY, lw=1.2), capprops=dict(color=GRAY, lw=1.2), flierprops=dict(marker='', alpha=0))
        for patch, rname in zip(bp['boxes'], cals_ordered):
            patch.set_facecolor(REGIMES_META[rname]['color'])
            patch.set_alpha(0.35)

        ax.axhline(ALPHA_LB, color=RED, linestyle='--', lw=1.8, alpha=0.85, zorder=4, label=(r'Significance threshold $\alpha=0.05$' if ax == axes[0] else None))
        if ax == axes[0]:
            ax.legend(fontsize=9, loc='upper right', framealpha=0.9)
            ax.set_ylabel('Ljung-Box p-value (lag=20)', fontsize=11)

        if annot_txt:
            ax.text(0.97, 0.50, annot_txt, transform=ax.transAxes, ha='right', va='center', fontsize=9, color=annot_color,
                    bbox=dict(facecolor='white', edgecolor=annot_color, alpha=0.90, boxstyle='round,pad=0.35', linewidth=0.8))

        ax.set_xticks(range(len(cals_ordered)))
        ax.set_xticklabels([REGIMES_META[r]['label'] for r in cals_ordered], fontsize=9.5)
        ax.set_xlim(-0.5, len(cals_ordered) - 0.5)
        ax.set_ylim(-0.04, 1.08)
        ax.set_title(title, fontsize=11.5, fontweight='bold', loc='left')

    fig.suptitle('Empirical Evaluation of the Whitening Proposition (Sign-Task ML Filter)', fontsize=13, fontweight='bold', y=1.02)
    fig.text(0.5, -0.05, '360 independent stationary streams (120/regime) | HoeffdingTree online | sign-prediction task | n=8000', ha='center', fontsize=9, color=GRAY)
    
    handles = [mpatches.Patch(color=REGIMES_META[r]['color'], alpha=0.65, label=REGIMES_META[r]['label']) for r in cals_ordered]
    fig.legend(handles=handles, loc='lower center', ncol=3, fontsize=9.5, framealpha=0.9, bbox_to_anchor=(0.5, -0.14))
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--n-jobs', type=int, default=1, help='Number of parallel jobs')
    args = parser.parse_args()

    assert len(SEEDS) == 30 and len(ETFS) == 4 and N_STEPS == 8000 and LB_LAGS == 20 and NU == 7.0, "Specification breach."

    logger.info("=================================================================")
    logger.info("  R02 : Fig1 - Ljung-Box Multi-ETF")
    logger.info(f"  River version: {river.__version__}")
    logger.info("=================================================================")

    grid, seed_tuples, base_idx = [], set(), 0
    for seed in SEEDS:
        for etf in ETFS:
            for rname, a, b in [('IID', 0.0, 0.0), ('Cal. A', ETF_PARAMS_A[etf]['alpha'], ETF_PARAMS_A[etf]['beta']), ('Cal. B', ETF_PARAMS_B[etf]['alpha'], ETF_PARAMS_B[etf]['beta'])]:
                grid.append((base_idx, rname, etf, seed, a, b))
                seed_128, _ = get_deterministic_seed(rname, etf, seed)
                seed_tuples.add(seed_128)
                base_idx += 1

    if len(seed_tuples) != 360:
        logger.error(f"FATAL: Seed collision detected! Unique seeds: {len(seed_tuples)}/360")
        sys.exit(1)

    logger.info(f"Executing {len(grid)} independent stream simulations on {args.n_jobs} cores...")
    results_raw = Parallel(n_jobs=args.n_jobs)(delayed(simulate_task)(*g) for g in grid)

    results, degenerate_count = [], 0
    for expected_idx, (idx, res, logs) in enumerate(results_raw):
        assert idx == expected_idx, "FATAL: Joblib out-of-order execution detected."
        for lvl, msg in logs:
            if lvl == 'WARNING': logger.warning(msg)
            elif lvl == 'ERROR': logger.error(msg)
        
        if 'error' in res:
            logger.error("FATAL: Worker encountered an exception. Aborting pipeline.")
            sys.exit(1)
            
        degenerate_count += res.pop('degenerate', 0)
        results.append(res)

    logger.info(f"Total degenerate Ljung-Box calculations: {degenerate_count}")

    df = pd.DataFrame(results).sort_values(by=['regime', 'etf', 'seed']).reset_index(drop=True)
    csv_out = DATA_DIR / "R02_ljungbox_360streams.csv"
    save_fair_csv(df, csv_out)
    
    diag_rows, bonferroni_thresh = [], ALPHA_LB / 6.0
    for rname in ['IID', 'Cal. A', 'Cal. B']:
        sub = df[df['regime'] == rname]
        n_distinct = int(sub['p_concept'].nunique())
        if n_distinct != 120:
            logger.error(f"FATAL: Independence failure in {rname} (distinct p_concept: {n_distinct} != 120)")
            sys.exit(1)
            
        piv = sub.pivot(index='seed', columns='etf', values='p_concept')
        for etf1, etf2 in itertools.combinations(ETFS, 2):
            r_val, p_val = stats.pearsonr(piv[etf1], piv[etf2])
            diag_rows.append({
                'regime': rname, 'n_distinct_p_concept': n_distinct, 'etf_pair': f"{etf1}-{etf2}",
                'pearson_r': float(r_val), 'pearson_pvalue': float(p_val),
                'bonferroni_threshold': float(bonferroni_thresh), 'independence_pass': bool(p_val >= bonferroni_thresh)
            })

    df_diag = pd.DataFrame(diag_rows)
    diag_csv_out = DATA_DIR / "R02_independence_diagnostics.csv"
    save_fair_csv(df_diag, diag_csv_out)

    tex_out = TABS_DIR / "R02_claims.tex"
    with open(tex_out, "w") as f:
        f.write("% Auto-generated by exp_R02_whitening_ljungbox.py -- do not edit.\n")
        f.write(f"\\newcommand{{\\RTwoStreams}}{{{len(df)}}}\n")
        f.write(f"\\newcommand{{\\RTwoSeeds}}{{{len(SEEDS)}}}\n")
        f.write(f"\\newcommand{{\\RTwoCalibrations}}{{{len(ETFS)}}}\n")
        f.write(f"\\newcommand{{\\RTwoRegimes}}{{3}}\n")
        f.write(f"\\newcommand{{\\RTwoHorizon}}{{{N_STEPS}}}\n")
        f.write(f"\\newcommand{{\\RTwoLbLags}}{{{LB_LAGS}}}\n")
        
        reject_iid = (df[df['regime'] == 'IID']['p_data'] < ALPHA_LB).mean() * 100
        reject_a = (df[df['regime'] == 'Cal. A']['p_data'] < ALPHA_LB).mean() * 100
        reject_b = (df[df['regime'] == 'Cal. B']['p_data'] < ALPHA_LB).mean() * 100
        f.write(f"\\newcommand{{\\RTwoDataRejectIid}}{{{reject_iid:.1f}}}\n")
        f.write(f"\\newcommand{{\\RTwoDataRejectClusteredA}}{{{reject_a:.1f}}}\n")
        f.write(f"\\newcommand{{\\RTwoDataRejectClusteredB}}{{{reject_b:.1f}}}\n")
        
        max_p_clustered = df[df['regime'].isin(['Cal. A', 'Cal. B'])]['p_data'].max()
        f.write(f"\\newcommand{{\\RTwoDataMaxPvalueClustered}}{{{max_p_clustered:.2e}}}\n")
        
        concept_rejects = df.groupby('regime')['p_concept'].apply(lambda x: (x < ALPHA_LB).mean() * 100)
        f.write(f"\\newcommand{{\\RTwoConceptRejectMin}}{{{concept_rejects.min():.1f}}}\n")
        f.write(f"\\newcommand{{\\RTwoConceptRejectMax}}{{{concept_rejects.max():.1f}}}\n")
        
        pooled_k, pooled_n = (df['p_concept'] < ALPHA_LB).sum(), len(df)
        w_low, w_high = wilson_score_interval(pooled_k, pooled_n)
        f.write(f"\\newcommand{{\\RTwoConceptRejectPooled}}{{{(pooled_k / pooled_n) * 100:.1f}}}\n")
        f.write(f"\\newcommand{{\\RTwoConceptWilsonLow}}{{{w_low * 100:.1f}}}\n")
        f.write(f"\\newcommand{{\\RTwoConceptWilsonHigh}}{{{w_high * 100:.1f}}}\n")
        
        gamma_A, gamma_B = df[df['regime'] == 'Cal. A']['gamma_penalty'], df[df['regime'] == 'Cal. B']['gamma_penalty']
        f.write(f"\\newcommand{{\\RTwoGammaCalA}}{{{gamma_A.min():.2f}--{gamma_A.max():.2f}}}\n")
        f.write(f"\\newcommand{{\\RTwoGammaCalB}}{{{gamma_B.min():.2f}--{gamma_B.max():.2f}}}\n")
        f.write(f"\\newcommand{{\\RTwoDistinctPConcept}}{{120}}\n")

    plot_figure(df, FIGS_DIR / "fig01_ljungbox_whiteness.png")

    logger.info("Running empirical certification...")
    if reject_a < 100.0 or reject_b < 100.0:
        logger.error(f"Certification failed: Data rejection not 100% (A: {reject_a}%, B: {reject_b}%)")
        sys.exit(1)
    if not (w_low <= ALPHA_LB <= w_high):
        logger.error(f"Certification failed: Nominal 0.05 out of bounds [{w_low*100:.2f}%, {w_high*100:.2f}%]")
        sys.exit(1)
    if not df_diag['independence_pass'].all():
        logger.error("Certification failed: Cross-correlation bonferroni test rejected independence.")
        sys.exit(1)
    logger.info("Empirical certification passed successfully.")
    
    # Log artifact manifest
    artifacts = [
        csv_out,
        diag_csv_out,
        tex_out,
        FIGS_DIR / "fig01_ljungbox_whiteness.png"
    ]
    log_artifact_manifest(logger, artifacts, RESULTS_DIR, PROJECT_ROOT)

if __name__ == '__main__':
    main()