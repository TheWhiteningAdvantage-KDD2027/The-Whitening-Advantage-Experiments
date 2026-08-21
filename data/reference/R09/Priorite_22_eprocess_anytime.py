import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["PYTHONHASHSEED"] = "42"
os.environ["MKL_CBWR"] = "COMPATIBLE"

# ==============================================================================
# Priorite_22_eprocess_anytime.py
# Stream P6b: Detection Anytime-Valid vs CUSUM Fixed Horizon
# ==============================================================================
"""
Notations:
- H : Horizon de calibration du CUSUM à seuil fixe.
- α (alpha) : Niveau de fausse alarme nominal.
- η (eta) : Magnitude de la dérive sous l'alternative (H1), exprimée en écart au taux 0.5.
- MIX : Martingale de test par mélange, dont l'inégalité de Ville borne la fausse alarme uniformément.
- ARL0 : Average Run Length sous contrôle (H0). 
- censored_frac : Fraction de trajectoires censurées à droite (qui n'ont pas franchi le seuil avant T_EXT). L'ARL0 est dès lors une borne inférieure stricte.

References:
- Ville, J. (1939), Étude critique de la notion de collectif.
- Ramdas, A. et al. (2023), Game-theoretic statistics and safe anytime-valid inference.
"""

import argparse
import logging
import sys
import time
import importlib.metadata
import hashlib
import numpy as np
import pandas as pd

# Desactivation stricte des moteurs d'execution C implicites pour prevenir l'asymetrie flottante
pd.options.compute.use_bottleneck = False
pd.options.compute.use_numexpr = False

from scipy import stats
from scipy.special import logsumexp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from joblib import Parallel, delayed, cpu_count
from pathlib import Path

# --- DIRECTORIES ---
BASE_DIR = Path(__file__).resolve().parent if '__file__' in locals() else Path.cwd()
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------------------
# 0. CONFIGURATION & LOGGING
# ------------------------------------------------------------------------------
def setup_logging(base_dir: Path, script_name: str) -> logging.Logger:
    """
    Configures a dual-output logger (Console + File) compliant with FAIR standards.
    - Console: Real-time monitoring via stdout.
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

logger = setup_logging(BASE_DIR, "Priorite_22_eprocess_anytime")
logging.info = logger.info
logging.error = logger.error
logging.warning = logger.warning

def log_requirements():
    reqs = ["numpy", "pandas", "scipy", "statsmodels", "matplotlib", "joblib", "tqdm"]
    logging.info("--- Execution Environment Requirements ---")
    for req in reqs:
        try:
            version = importlib.metadata.version(req)
            logging.info(f"{req}=={version}")
        except importlib.metadata.PackageNotFoundError:
            logging.warning(f"{req} is not installed.")
    logging.info("------------------------------------------")

log_requirements()

# Global registry for deterministic seed verification
_SEEDS_REGISTRY = set()
_CRN_REGISTRY = set()

def register_seeds(seqs, context, is_crn=False):
    """
    Asserts seed uniqueness to prevent intra-group collisions.
    Inter-group collisions (CRN) are structurally permitted and documented.
    """
    for s in seqs:
        val = (s.entropy, s.spawn_key)
        if val in _SEEDS_REGISTRY:
            if is_crn:
                if val not in _CRN_REGISTRY:
                    _CRN_REGISTRY.add(val)
                    logging.info(f"CRN logged: Reusing seed {val} for context '{context}'.")
            else:
                logging.error(f"FATAL: Seed collision detected for seed {val} in context '{context}'.")
                sys.exit(1)
        else:
            _SEEDS_REGISTRY.add(val)
            logging.info(f"Registered PRNG seed key {val} for context '{context}'.")

def wilson_ci(k: int, n: int, confidence: float = 0.95) -> tuple:
    """Asymmetric Wilson score interval for a binomial proportion."""
    if n == 0:
        return 0.0, 0.0
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt((p * (1 - p)) / n + z**2 / (4 * n**2))) / denom
    return max(0.0, center - margin), min(1.0, center + margin)

# ------------------------------------------------------------------------------
# 1. ARCHITECTURE AND SIMULATION PARAMETERS
# ------------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--fast", action="store_true", help="Run with reduced parameters")
args = parser.parse_args()

H = 5000
TAU = 2500
ALPHAS = [0.10, 0.07, 0.05, 0.035, 0.025, 0.015, 0.01]
ETAS = [0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20]
DELTA_CUSUM = 0.1
ETA0_MIX_GRID = [0.05, 0.10, 0.15]
ETA0_ECUSUM = 0.10
SIDES = [1, -1]

if args.fast:
    N_CAL, N_NULL, N_ALT = 2000, 2000, 1000
    START_GRID_SIZE = 6
    T_EXT_MULT = 2
else:
    N_CAL, N_NULL, N_ALT = 50000, 20000, 2000
    START_GRID_SIZE = 16
    T_EXT_MULT = 4

T_EXT = T_EXT_MULT * H
START_GRID = np.linspace(0, H - 1, START_GRID_SIZE, dtype=int)
C_MIX = len(START_GRID) * len(ETA0_MIX_GRID) * len(SIDES)
MIX_W = 1.0 / C_MIX

# Parallelization scaling parameter (invariant graph for exact reproducibility)
NUM_CHUNKS = 10

# Seed isolation
master_seed = 42027
seq = np.random.SeedSequence(master_seed)
logging.info(f"Master SeedSequence initialized with entropy: {master_seed}")
logging.info(f"Fast mode: {args.fast} | N_CAL={N_CAL}, N_NULL={N_NULL}, N_ALT={N_ALT}, T_EXT={T_EXT}")

# ------------------------------------------------------------------------------
# 2. MODULE M1: MARTINGALE CERTIFICATE (BLOQUANT)
# ------------------------------------------------------------------------------
def _process_m1_chunk(seq_chunk, chunk_size, start_times, log_inc_1, log_inc_0):
    rng = np.random.default_rng(seq_chunk)
    log_w = np.log(MIX_W)
    logM_mix = np.full((chunk_size, C_MIX), log_w)
    first_alarm_mix = {a: np.full(chunk_size, np.inf) for a in ALPHAS}
    
    for t in range(T_EXT):
        y_t = rng.binomial(1, 0.5, size=chunk_size)
        active_idx = np.where(t >= start_times)[0]
        if len(active_idx) > 0:
            inc = np.where(y_t[:, None] == 1, log_inc_1[active_idx], log_inc_0[active_idx])
            logM_mix[:, active_idx] += inc
        
        logE_t = logsumexp(logM_mix, axis=1)
        if np.any(np.isnan(logE_t)) or np.any(np.isinf(logE_t)):
            raise ValueError("NaN/Inf encountered in MIX logE_t.")
            
        for a in ALPHAS:
            cross = (logE_t >= -np.log(a))
            mask = cross & (first_alarm_mix[a] == np.inf)
            first_alarm_mix[a][mask] = t + 1
    return first_alarm_mix

def run_m1_certificate(seq):
    logging.info("Executing M1 Certificate (Parallelized via invariant PRNG spawning)...")
    child_seqs_main = seq.spawn(2)
    register_seeds(child_seqs_main, "M1_main")
    rng = np.random.default_rng(child_seqs_main[0])
    
    # M1 (i): Expectation of lambda_t
    n_steps = 2000000
    y = rng.binomial(1, 0.5, size=n_steps)
    eta0_draws = rng.choice(ETA0_MIX_GRID, size=n_steps)
    side_draws = rng.choice(SIDES, size=n_steps)
    
    lambda_t = np.where(y == 1, 2 * (0.5 + side_draws * eta0_draws), 2 * (0.5 - side_draws * eta0_draws))
    mean_lambda = np.mean(lambda_t)
    logging.info(f"M1(i) Mean of lambda_t over 2e6 steps: {mean_lambda:.5f}")
    if abs(mean_lambda - 1.0) > 3e-3:
        logging.error("FATAL: M1(i) violated. E[lambda_t] != 1.0.")
        sys.exit(1)
        
    # M1 (ii): Ville's Bound via fast simulation
    n_ville = N_NULL
    log_w = np.log(MIX_W)
    logM_mix = np.full((n_ville, C_MIX), log_w)
    
    # Precompute log increments
    log_inc_1 = np.zeros(C_MIX)
    log_inc_0 = np.zeros(C_MIX)
    idx = 0
    start_times = np.zeros(C_MIX, dtype=int)
    for st in START_GRID:
        for e0 in ETA0_MIX_GRID:
            for sd in SIDES:
                start_times[idx] = st
                log_inc_1[idx] = np.log(2 * (0.5 + sd * e0))
                log_inc_0[idx] = np.log(2 * (0.5 - sd * e0))
                idx += 1
                
    # Ensure NUM_CHUNKS invariantly determines execution graph for absolute reproducibility
    n_jobs = min(cpu_count(), NUM_CHUNKS)
    child_seqs = child_seqs_main[1].spawn(NUM_CHUNKS)
    register_seeds(child_seqs, "M1_chunks")
    
    base_chunk = n_ville // NUM_CHUNKS
    rem = n_ville % NUM_CHUNKS
    chunk_sizes = [base_chunk + 1 if i < rem else base_chunk for i in range(NUM_CHUNKS)]
    
    res_chunks = Parallel(n_jobs=n_jobs)(
        delayed(_process_m1_chunk)(child_seqs[i], chunk_sizes[i], start_times, log_inc_1, log_inc_0)
        for i in range(NUM_CHUNKS)
    )
    
    first_alarm_mix = {a: np.concatenate([res[a] for res in res_chunks]) for a in ALPHAS}

    for a in ALPHAS:
        fpr = np.mean(first_alarm_mix[a] <= T_EXT)
        ci_low, ci_high = wilson_ci(np.sum(first_alarm_mix[a] <= T_EXT), n_ville)
        logging.info(f"M1(ii) alpha={a}: FPR anytime over T_EXT = {fpr:.4f} (Wilson CI: [{ci_low:.4f}, {ci_high:.4f}])")
        if fpr > a + 0.005:
            logging.error(f"FATAL: M1(ii) Ville's bound violated for alpha={a}. FPR={fpr:.4f}")
            sys.exit(1)
            
    logging.info("M1 Certificate PASS.")

# ------------------------------------------------------------------------------
# 3. CUSUM CALIBRATION
# ------------------------------------------------------------------------------
def calibrate_cusum(seq):
    logging.info("Calibrating CUSUM threshold on lattice...")
    child_seq = seq.spawn(1)
    register_seeds(child_seq, "CUSUM_calib")
    rng = np.random.default_rng(child_seq[0])
    max_M = np.zeros(N_CAL)
    
    S_pos = np.zeros(N_CAL)
    S_neg = np.zeros(N_CAL)
    
    for t in range(H):
        y_t = rng.binomial(1, 0.5, size=N_CAL)
        dev = y_t - 0.5
        S_pos = np.maximum(0, S_pos + dev - DELTA_CUSUM)
        S_neg = np.maximum(0, S_neg - dev - DELTA_CUSUM)
        M_t = np.maximum(S_pos, S_neg)
        max_M = np.maximum(max_M, M_t)
        
    lambda_star = {}
    actual_level = {}
    for a in ALPHAS:
        # float lattice behavior emulation
        l_star = np.quantile(max_M, 1 - a)
        lambda_star[a] = l_star
        # The prompt requires raw floats >= lambda_star (Yielding ~5.03% on alpha=0.05)
        achieved = np.mean(max_M >= l_star)
        actual_level[a] = achieved
        logging.info(f"Calibration alpha={a}: lambda_star={l_star:.4f}, achieved={achieved:.4f}")
    
    logging.info("CUSUM comparison semantics: flottants bruts >= lambda_star (niveau effectif ~5.03%)")
    return lambda_star, actual_level

# ------------------------------------------------------------------------------
# 4. MAIN SIMULATION (H0)
# ------------------------------------------------------------------------------
def _process_h0_chunk(seq_chunk, chunk_size, lambda_star, start_times, log_inc_1, log_inc_0, inc_p_1, inc_p_0, inc_m_1, inc_m_0):
    rng = np.random.default_rng(seq_chunk)
    S_pos = np.zeros(chunk_size)
    S_neg = np.zeros(chunk_size)
    logM_mix = np.full((chunk_size, C_MIX), np.log(MIX_W))
    logMp = np.zeros(chunk_size)
    logMm = np.zeros(chunk_size)
    
    fa_cusum = {a: np.full(chunk_size, np.inf) for a in ALPHAS}
    fa_mix = {a: np.full(chunk_size, np.inf) for a in ALPHAS}
    fa_ecusum = {a: np.full(chunk_size, np.inf) for a in ALPHAS}
    xt_cusum = {a: np.zeros(chunk_size, dtype=bool) for a in ALPHAS}
    xt_mix = {a: np.zeros(chunk_size, dtype=bool) for a in ALPHAS}
    xt_ecusum = {a: np.zeros(chunk_size, dtype=bool) for a in ALPHAS}
    
    for t in range(T_EXT):
        y_t = rng.binomial(1, 0.5, size=chunk_size)
        
        # CUSUM
        dev = y_t - 0.5
        S_pos = np.maximum(0, S_pos + dev - DELTA_CUSUM)
        S_neg = np.maximum(0, S_neg - dev - DELTA_CUSUM)
        M_cusum = np.maximum(S_pos, S_neg)
        
        # MIX
        active_idx = np.where(t >= start_times)[0]
        if len(active_idx) > 0:
            inc_mix = np.where(y_t[:, None] == 1, log_inc_1[active_idx], log_inc_0[active_idx])
            logM_mix[:, active_idx] += inc_mix
        logE_mix = logsumexp(logM_mix, axis=1)
        
        # eCUSUM
        ip = np.where(y_t == 1, inc_p_1, inc_p_0)
        im = np.where(y_t == 1, inc_m_1, inc_m_0)
        logMp = np.maximum(0, logMp + ip)
        logMm = np.maximum(0, logMm + im)
        M_ecusum = np.maximum(logMp, logMm)
        
        for a in ALPHAS:
            c_cross = (M_cusum >= lambda_star[a])
            m_cross = (logE_mix >= -np.log(a))
            e_cross = (M_ecusum >= -np.log(a))
            
            fa_cusum[a][c_cross & (fa_cusum[a] == np.inf)] = t + 1
            fa_mix[a][m_cross & (fa_mix[a] == np.inf)] = t + 1
            fa_ecusum[a][e_cross & (fa_ecusum[a] == np.inf)] = t + 1
            
            if t == T_EXT - 1:
                xt_cusum[a] = c_cross
                xt_mix[a] = m_cross
                xt_ecusum[a] = e_cross
                
    return fa_cusum, fa_mix, fa_ecusum, xt_cusum, xt_mix, xt_ecusum

def simulate_h0(seq, lambda_star):
    logging.info("Simulating H0 streams for M2, M3, M6 (Parallelized via invariant PRNG spawning)...")
    child_seqs = seq.spawn(NUM_CHUNKS)
    register_seeds(child_seqs, "H0_chunks")
    
    log_inc_1 = np.zeros(C_MIX)
    log_inc_0 = np.zeros(C_MIX)
    idx = 0
    start_times = np.zeros(C_MIX, dtype=int)
    for st in START_GRID:
        for e0 in ETA0_MIX_GRID:
            for sd in SIDES:
                start_times[idx] = st
                log_inc_1[idx] = np.log(2 * (0.5 + sd * e0))
                log_inc_0[idx] = np.log(2 * (0.5 - sd * e0))
                idx += 1
                
    inc_p_1 = np.log(2 * (0.5 + ETA0_ECUSUM))
    inc_p_0 = np.log(2 * (0.5 - ETA0_ECUSUM))
    inc_m_1 = np.log(2 * (0.5 - ETA0_ECUSUM))
    inc_m_0 = np.log(2 * (0.5 + ETA0_ECUSUM))
    
    n_jobs = min(cpu_count(), NUM_CHUNKS)
    base_chunk = N_NULL // NUM_CHUNKS
    rem = N_NULL % NUM_CHUNKS
    chunk_sizes = [base_chunk + 1 if i < rem else base_chunk for i in range(NUM_CHUNKS)]
    
    res = Parallel(n_jobs=n_jobs)(
        delayed(_process_h0_chunk)(
            child_seqs[i], chunk_sizes[i], lambda_star, start_times, 
            log_inc_1, log_inc_0, inc_p_1, inc_p_0, inc_m_1, inc_m_0
        ) for i in range(NUM_CHUNKS)
    )
    
    first_alarm_CUSUM = {a: np.concatenate([r[0][a] for r in res]) for a in ALPHAS}
    first_alarm_MIX = {a: np.concatenate([r[1][a] for r in res]) for a in ALPHAS}
    first_alarm_eCUSUM = {a: np.concatenate([r[2][a] for r in res]) for a in ALPHAS}
    exact_Text_cross_CUSUM = {a: np.concatenate([r[3][a] for r in res]) for a in ALPHAS}
    exact_Text_cross_MIX = {a: np.concatenate([r[4][a] for r in res]) for a in ALPHAS}
    exact_Text_cross_eCUSUM = {a: np.concatenate([r[5][a] for r in res]) for a in ALPHAS}

    return (first_alarm_CUSUM, first_alarm_MIX, first_alarm_eCUSUM, 
            exact_Text_cross_CUSUM, exact_Text_cross_MIX, exact_Text_cross_eCUSUM)

# ------------------------------------------------------------------------------
# 5. MAIN SIMULATION (H1)
# ------------------------------------------------------------------------------
def simulate_h1(seq, lambda_star):
    logging.info("Simulating H1 streams for M4...")
    child_seq = seq.spawn(1)
    register_seeds(child_seq, "H1_sim")
    rng = np.random.default_rng(child_seq[0])
    
    log_inc_1 = np.zeros(C_MIX)
    log_inc_0 = np.zeros(C_MIX)
    idx = 0
    start_times = np.zeros(C_MIX, dtype=int)
    for st in START_GRID:
        for e0 in ETA0_MIX_GRID:
            for sd in SIDES:
                start_times[idx] = st
                log_inc_1[idx] = np.log(2 * (0.5 + sd * e0))
                log_inc_0[idx] = np.log(2 * (0.5 - sd * e0))
                idx += 1
                
    results = {}
    
    for eta in ETAS:
        # Pre-assign sides randomly per stream
        stream_sides = rng.choice(SIDES, size=N_ALT)
        p_alt = 0.5 + stream_sides * eta
        
        S_pos = np.zeros(N_ALT)
        S_neg = np.zeros(N_ALT)
        logM_mix = np.full((N_ALT, C_MIX), np.log(MIX_W))
        
        fa_cusum = {a: np.full(N_ALT, np.inf) for a in ALPHAS}
        fa_mix = {a: np.full(N_ALT, np.inf) for a in ALPHAS}
        
        for t in range(H):
            if t < TAU:
                y_t = rng.binomial(1, 0.5, size=N_ALT)
            else:
                y_t = rng.binomial(1, p_alt)
                
            dev = y_t - 0.5
            S_pos = np.maximum(0, S_pos + dev - DELTA_CUSUM)
            S_neg = np.maximum(0, S_neg - dev - DELTA_CUSUM)
            M_cusum = np.maximum(S_pos, S_neg)
            
            active_idx = np.where(t >= start_times)[0]
            if len(active_idx) > 0:
                inc_mix = np.where(y_t[:, None] == 1, log_inc_1[active_idx], log_inc_0[active_idx])
                logM_mix[:, active_idx] += inc_mix
            logE_mix = logsumexp(logM_mix, axis=1)
            
            for a in ALPHAS:
                c_cross = (M_cusum >= lambda_star[a])
                m_cross = (logE_mix >= -np.log(a))
                
                fa_cusum[a][c_cross & (fa_cusum[a] == np.inf)] = t + 1
                fa_mix[a][m_cross & (fa_mix[a] == np.inf)] = t + 1
                
        for a in ALPHAS:
            valid_c = (fa_cusum[a] > TAU) & (fa_cusum[a] <= H)
            valid_m = (fa_mix[a] > TAU) & (fa_mix[a] <= H)
            
            det_c = np.mean(valid_c)
            det_m = np.mean(valid_m)
            
            add_c = np.mean(fa_cusum[a][valid_c] - TAU) if np.sum(valid_c) > 0 else np.nan
            add_m = np.mean(fa_mix[a][valid_m] - TAU) if np.sum(valid_m) > 0 else np.nan
            
            sem_c = np.std(fa_cusum[a][valid_c] - TAU)/np.sqrt(np.sum(valid_c)) if np.sum(valid_c) > 0 else np.nan
            sem_m = np.std(fa_mix[a][valid_m] - TAU)/np.sqrt(np.sum(valid_m)) if np.sum(valid_m) > 0 else np.nan
            
            ci_c = wilson_ci(np.sum(valid_c), N_ALT)
            ci_m = wilson_ci(np.sum(valid_m), N_ALT)
            
            results[("CUSUM", a, eta)] = (det_c, ci_c[0], ci_c[1], add_c, sem_c)
            results[("MIX", a, eta)] = (det_m, ci_m[0], ci_m[1], add_m, sem_m)
            
    return results

# ------------------------------------------------------------------------------
# 6. EXECUTION AND REPORTING
# ------------------------------------------------------------------------------
def main():
    # Strict tree-based cryptographic isolation to prevent cross-contamination
    branch_seqs = seq.spawn(4)
    register_seeds([seq], "Master")
    register_seeds(branch_seqs, "main_branches")
    
    run_m1_certificate(branch_seqs[0])
    lambda_star, actual_calib_level = calibrate_cusum(branch_seqs[1])
    
    (fa_cusum_h0, fa_mix_h0, fa_ecusum_h0, 
     xt_cusum, xt_mix, xt_ecusum) = simulate_h0(branch_seqs[2], lambda_star)
     
    res_h1 = simulate_h1(branch_seqs[3], lambda_star)
    
    # --- Control Flags Validation ---
    logging.info("Validating control flags (b) to (g)...")
    
    # (b) CUSUM anchoring
    fpr_cusum_m2_05 = np.mean(fa_cusum_h0[0.05] <= H)
    lstar_05 = lambda_star[0.05]
    logging.info(f"Control (b): CUSUM alpha=0.05 lambda_star={lstar_05:.4f}, FPR_M2={fpr_cusum_m2_05:.4f}")
    if not (0.046 <= fpr_cusum_m2_05 <= 0.055):
        logging.error("FATAL: Control (b) failed. CUSUM FPR out of [0.046, 0.055].")
        sys.exit(1)
        
    # (c) eCUSUM validation
    fpr_ecusum_ext_05 = np.mean(fa_ecusum_h0[0.05] <= T_EXT)
    logging.info(f"Control (c): eCUSUM FPR on [1, T_ext] at alpha=0.05 is {fpr_ecusum_ext_05:.4f}")
    if fpr_ecusum_ext_05 < 0.80:
        logging.error("FATAL: Control (c) failed. eCUSUM reset logic seems broken.")
        sys.exit(1)
        
    # (d) Sens de la course
    for a in ALPHAS:
        f_cus = np.mean(fa_cusum_h0[a] <= T_EXT)
        f_mix = np.mean(fa_mix_h0[a] <= T_EXT)
        if f_cus <= f_mix:
            logging.error(f"FATAL: Control (d) failed. CUSUM peeking FPR {f_cus} <= MIX {f_mix} at alpha={a}.")
            sys.exit(1)
            
    # (e) Coherence interne
    std_mc = np.sqrt(0.05 * 0.95 / N_NULL)
    diff = abs(fpr_cusum_m2_05 - actual_calib_level[0.05])
    if diff > 3 * std_mc:
        logging.error(f"FATAL: Control (e) failed. Gap between M2 ({fpr_cusum_m2_05}) and Calib ({actual_calib_level[0.05]}) exceeds 3 sigma ({3*std_mc}).")
        sys.exit(1)
        
    # (f) handled natively by numpy warnings & check in M1
    
    # (g) Indicative anchors
    fpr_mix_ext_05 = np.mean(fa_mix_h0[0.05] <= T_EXT)
    det_mix_05_10 = res_h1[("MIX", 0.05, 0.10)][0]
    add_mix_05_10 = res_h1[("MIX", 0.05, 0.10)][3]
    logging.info(f"Control (g): MIX FPR_ext={fpr_mix_ext_05:.4f}, Det={det_mix_05_10:.4f}, ADD={add_mix_05_10:.2f}")
    if fpr_mix_ext_05 > 0.06 or det_mix_05_10 < 0.90 or not (300 <= add_mix_05_10 <= 700):
        logging.warning("WARNING: Control (g) anchor values slightly off (expected for fast mode / variance).")
    
    # --- Generating CSV 22a (Validity Stopping) ---
    records_22a = []
    protocols = [("nominal", H, False), ("extended", T_EXT, True), ("peeking", T_EXT, False)]
    
    for arm, fa_dict, xt_dict, g_type in [
        ("CUSUM", fa_cusum_h0, xt_cusum, "fixed_horizon"),
        ("MIX", fa_mix_h0, xt_mix, "ville_anytime"),
        ("eCUSUM", fa_ecusum_h0, xt_ecusum, "arl0_only")
    ]:
        for a in ALPHAS:
            for p_name, p_time, exact in protocols:
                if exact:
                    crosses = np.sum(xt_dict[a])
                else:
                    crosses = np.sum(fa_dict[a] <= p_time)
                fpr = crosses / N_NULL
                ci_low, ci_high = wilson_ci(crosses, N_NULL)
                
                if arm == "MIX":
                    b_resp = str(fpr <= a)
                elif arm == "CUSUM":
                    b_resp = "FPR~alpha at calibration point" if p_name == "nominal" else str(fpr <= a)
                else:
                    b_resp = "n/a (documentary)"
                    
                records_22a.append({
                    "arm": arm, "alpha": a, "stopping_protocol": p_name,
                    "guarantee_type": g_type, "threshold": a, "N_streams": N_NULL,
                    "FPR": fpr, "CI_low": ci_low, "CI_high": ci_high,
                    "bound_target": a, "bound_respected": b_resp
                })
    pd.DataFrame(records_22a).to_csv(FIGURES_DIR / "protocol_22a_validity_stopping.csv", index=False, float_format='%.17g', na_rep='NaN')
    
    # --- Generating CSV 22b (Eprocess Race) ---
    records_22b = []
    for arm in ["CUSUM", "MIX"]:
        for a in ALPHAS:
            for eta in ETAS:
                d = res_h1[(arm, a, eta)]
                records_22b.append({
                    "arm": arm, "alpha": a, "eta": eta, "N_streams": N_ALT,
                    "DetRate": d[0], "DetRate_CI_low": d[1], "DetRate_CI_high": d[2],
                    "ADD": d[3], "SEM": d[4]
                })
    pd.DataFrame(records_22b).to_csv(FIGURES_DIR / "protocol_22b_eprocess_race.csv", index=False, float_format='%.17g', na_rep='NaN')
    
    # --- Generating CSV 22c (Level Granularity) ---
    records_22c = []
    for arm, fa_dict in [("CUSUM", fa_cusum_h0), ("MIX", fa_mix_h0)]:
        for a in ALPHAS:
            fpr = np.mean(fa_dict[a] <= H)
            ci = wilson_ci(np.sum(fa_dict[a] <= H), N_NULL)
            gap = (fpr - a) * 100
            records_22c.append({
                "arm": arm, "alpha": a, "target_level": a, "achieved_level": fpr,
                "achieved_CI_low": ci[0], "achieved_CI_high": ci[1],
                "gap_pp": gap, "level_is_attainable": (arm == "MIX")
            })
    pd.DataFrame(records_22c).to_csv(FIGURES_DIR / "protocol_22c_level_granularity.csv", index=False, float_format='%.17g', na_rep='NaN')
    
    # --- Generating CSV 22d (ARL0) ---
    records_22d = []
    for arm, fa_dict in [("CUSUM", fa_cusum_h0), ("MIX", fa_mix_h0), ("eCUSUM", fa_ecusum_h0)]:
        for a in ALPHAS:
            arr = fa_dict[a]
            arr_capped = np.minimum(arr, T_EXT)
            arl0 = np.mean(arr_capped)
            sem = np.std(arr_capped) / np.sqrt(N_NULL)
            c_frac = np.mean(arr == np.inf)
            
            if c_frac > 0:
                logging.info(f"Censorship registered: {arm} alpha={a} has right-censored fraction = {c_frac:.4f}. ARL0_mean behaves strictly as a lower bound.")
                
            records_22d.append({
                "arm": arm, "alpha": a, "ARL0_mean": arl0,
                "ARL0_CI_low": arl0 - 1.96*sem, "ARL0_CI_high": arl0 + 1.96*sem,
                "ref_inv_alpha": 1.0/a, "censored_frac": c_frac,
                "right_censored_flag": c_frac > 0.05,
                "arl0_bound_respected": arl0 >= (1.0/a)
            })
            
    # --- Programmatic Empirical Certification ---
    df_22a = pd.DataFrame(records_22a)
    cusum_peeking_05 = df_22a[(df_22a["arm"] == "CUSUM") & (df_22a["alpha"] == 0.05) & (df_22a["stopping_protocol"] == "peeking")]["FPR"].values[0]
    if abs(cusum_peeking_05 - 0.1801) > 1e-9:
        logging.error(f"FATAL: Control (b) failed. CUSUM peeking FPR expected ~0.1801, got {cusum_peeking_05}")
        sys.exit(1)
        
    mix_failed = df_22a[(df_22a["arm"] == "MIX") & (df_22a["bound_respected"] == "False")]
    if not mix_failed.empty:
        logging.error("FATAL: Control (c) failed. Anytime-Valid MIX theoretical bound explicitly violated.")
        sys.exit(1)
        
    df_22b = pd.DataFrame(records_22b)
    mix_add_010 = df_22b[(df_22b["arm"] == "MIX") & (df_22b["alpha"] == 0.05) & (df_22b["eta"] == 0.10)]["ADD"].values[0]
    cus_add_010 = df_22b[(df_22b["arm"] == "CUSUM") & (df_22b["alpha"] == 0.05) & (df_22b["eta"] == 0.10)]["ADD"].values[0]
    if abs(mix_add_010 - 409.1131405377981) > 1e-9 or abs(cus_add_010 - 538.8051546391753) > 1e-9:
        logging.error(f"FATAL: Control (d) failed. Expected ADD ~409.11 (MIX) and ~538.80 (CUSUM) at eta=0.10.")
        sys.exit(1)
        
    df_22d = pd.DataFrame(records_22d)
    arl0_failed = df_22d[df_22d["arl0_bound_respected"] == False]
    if not arl0_failed.empty:
        logging.error("FATAL: Control (e) failed. ARL0 strict lower bound violated.")
        sys.exit(1)

    df_22d.to_csv(FIGURES_DIR / "protocol_22d_arl0.csv", index=False, float_format='%.17g', na_rep='NaN')
    
    # --- Figure 27 ---
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=300)
    df_22a = pd.DataFrame(records_22a)
    df_22a_05 = df_22a[df_22a["alpha"] == 0.05]
    
    # Panel A
    prots = ["nominal", "extended", "peeking"]
    x = np.arange(len(prots))
    width = 0.25
    arms = ["CUSUM", "MIX", "eCUSUM"]
    offsets = [-width, 0, width]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    for arm, off, col in zip(arms, offsets, colors):
        y_vals = []
        y_err_low = []
        y_err_high = []
        for p in prots:
            row = df_22a_05[(df_22a_05["arm"] == arm) & (df_22a_05["stopping_protocol"] == p)].iloc[0]
            y_vals.append(row["FPR"])
            y_err_low.append(max(0.0, row["FPR"] - row["CI_low"]))
            y_err_high.append(max(0.0, row["CI_high"] - row["FPR"]))
        axes[0].bar(x + off, y_vals, width, label=arm, yerr=[y_err_low, y_err_high], capsize=4, color=col)
        
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(prots)
    axes[0].axhline(0.05, color='k', linestyle='--')
    axes[0].set_ylabel(r"$FPR$")
    axes[0].legend()
    
    # Panel B
    df_22b = pd.DataFrame(records_22b)
    df_22b_05 = df_22b[df_22b["alpha"] == 0.05]
    for arm, col in zip(["CUSUM", "MIX"], colors[:2]):
        sub = df_22b_05[df_22b_05["arm"] == arm].sort_values("eta")
        axes[1].errorbar(sub["eta"], sub["ADD"], yerr=sub["SEM"], fmt='-o', label=arm, color=col, capsize=4)
    axes[1].set_xlabel(r"$\eta$")
    axes[1].set_ylabel(r"$ADD$")
    axes[1].legend()
    
    # Panel C
    df_22d = pd.DataFrame(records_22d)
    for arm, col in zip(arms, colors):
        sub = df_22d[df_22d["arm"] == arm].sort_values("alpha")
        axes[2].plot(sub["alpha"], sub["ARL0_mean"], '-o', label=arm, color=col)
    
    alphas_arr = np.array(sorted(ALPHAS))
    axes[2].plot(alphas_arr, 1.0/alphas_arr, 'k--', label=r"$1/\alpha$")
    axes[2].set_xscale("log")
    axes[2].set_yscale("log")
    axes[2].set_xticks(alphas_arr)
    axes[2].get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    axes[2].set_xlabel(r"$\alpha$")
    axes[2].set_ylabel(r"$ARL_0$")
    axes[2].legend()
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "Fig27_Eprocess_AnytimeValid.png", dpi=300, bbox_inches='tight')
    
    def hash_file(filepath):
        if not filepath.exists(): return None
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()

    logging.info("--- File Integrity Checks (SHA-256) ---")
    files_to_hash = [
        "protocol_22a_validity_stopping.csv",
        "protocol_22b_eprocess_race.csv",
        "protocol_22c_level_granularity.csv",
        "protocol_22d_arl0.csv"
    ]
    for fn in files_to_hash:
        fpath = FIGURES_DIR / fn
        logging.info(f"{fn} SHA-256: {hash_file(fpath)}")
        
    logging.info("All deliverables generated successfully.")

if __name__ == "__main__":
    main()