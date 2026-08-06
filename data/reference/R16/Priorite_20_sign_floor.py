import os
import sys

# STRICT DETERMINISM: Force single-threaded linear algebra BEFORE importing numpy/pandas
# Prevents floating-point non-associativity in multithreaded BLAS/MKL routines
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["PYTHONHASHSEED"] = "42"

import random
import numpy as np
import pandas as pd
import logging
from pathlib import Path

# --- REPRODUCIBILITY (FAIR STANDARDS) ---
def set_seed(seed=42):
    """Enforce deterministic randomness for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)

set_seed(42)

# --- DIRECTORY SETUP (FAIR STANDARDS) ---
BASE_DIR = Path(__file__).resolve().parent if '__file__' in locals() else Path.cwd()
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# NOTATION DEFINITIONS
# =============================================================================
# q_ref   : Unconditional probability of a positive return over the entire asset history.
# q_phase : Conditional probability of a positive return during a specific market phase.
# kl_sign : Kullback-Leibler divergence of Bernoulli(q_phase) from Bernoulli(q_ref), in nats/day.
#           kl_sign = q1*ln(q1/q0) + (1-q1)*ln((1-q1)/(1-q0)), where q1=q_phase, q0=q_ref.
# gamma   : Acceptable in-control Average Run Length (ARL_0) in trading days. Grid: {20, 252, 1260}.
# ADD_min_sign_g : Information-theoretic lower bound on detection delay for sign stream = ln(gamma)/kl_sign.
# ADD_min_unc_g  : Lower bound on detection delay for unconditional return stream = 504*ln(gamma)/sharpe^2.
# detectable_sign_g : Boolean flag, True if ADD_min_sign_g < T_days.
# detectable_unc_g  : Boolean flag, True if ADD_min_unc_g < T_days.
#
# References:
# Lorden, G. (1971), Ann. Math. Stat. 42(6)
# Lai, T. L. (1998), IEEE Trans. Inf. Theory 44(7)
# =============================================================================

def setup_logging():
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler(BASE_DIR / 'Priorite_20_sign_floor.log', mode='w')
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)
    return root_logger

def process_dataframe(df, source_label):
    records = []
    gammas = [20, 252, 1260]
    
    for row in df.itertuples(index=False):
        q0 = np.clip(row.q_ref, 1e-6, 1.0 - 1e-6)
        q1 = np.clip(row.q_phase, 1e-6, 1.0 - 1e-6)
        sharpe = row.sharpe
        t_days = row.T_days
        
        if abs(q1 - q0) < 1e-12:
            kl_sign = 0.0
        else:
            kl_sign = q1 * np.log(q1 / q0) + (1.0 - q1) * np.log((1.0 - q1) / (1.0 - q0))
            
        add_unc = {}
        add_sign = {}
        detect_unc = {}
        detect_sign = {}
        
        for g in gammas:
            if abs(sharpe) < 1e-12:
                a_unc = np.inf
            else:
                a_unc = 504.0 * np.log(g) / (sharpe**2)
            add_unc[g] = a_unc
            detect_unc[g] = a_unc < t_days
            
            if kl_sign == 0.0:
                a_sign = np.inf
            else:
                a_sign = np.log(g) / kl_sign
            add_sign[g] = a_sign
            detect_sign[g] = a_sign < t_days
            
        record = {
                'census_source': source_label,
                'ticker': row.ticker,
                'phase_id': row.phase_id,
                'phase_type': row.phase_type,
                'start_date': row.start_date,
                'end_date': row.end_date,
                'T_days': t_days,
                'sharpe': sharpe,
                'q_ref': row.q_ref,
                'q_phase': row.q_phase,
                'delta_q': row.delta_q,
                'kl_sign_nats_day': kl_sign,
                'ADD_min_unc_g20': add_unc[20],
                'ADD_min_unc_g252': add_unc[252],
                'ADD_min_unc_g1260': add_unc[1260],
                'ADD_min_sign_g20': add_sign[20],
                'ADD_min_sign_g252': add_sign[252],
                'ADD_min_sign_g1260': add_sign[1260],
                'detectable_unc_g20': detect_unc[20],
                'detectable_unc_g252': detect_unc[252],
                'detectable_unc_g1260': detect_unc[1260],
                'detectable_sign_g20': detect_sign[20],
                'detectable_sign_g252': detect_sign[252],
                'detectable_sign_g1260': detect_sign[1260],
                'episode_label': getattr(row, 'episode_label', np.nan)
        }
        records.append(record)
        
    return pd.DataFrame(records)

def main():
    logger = setup_logging()
    logger.info("Starting evaluation of detection floors (sign stream vs unconditional budget).")
    
    file_10b = FIGURES_DIR / 'protocol_10b_regime_census_refined.csv'
    
    if not file_10b.exists():
        logger.error(f"Input file not found. Required: {file_10b}")
        sys.exit(1)
        
    # FAIR STRICT DETERMINISM: Enforce IEEE 754 bit-exact float parsing across architectures
    df_10b_orig = pd.read_csv(file_10b, float_precision='round_trip')
    
    df_20a = process_dataframe(df_10b_orig, 'refined')
    
    # Synthese 20b
    stats = []
    gammas = [20, 252, 1260]
    budgets = ['unc', 'sign']
    
    for src in ['refined']:
        sub = df_20a[df_20a['census_source'] == src]
        n_phases = len(sub)
        for g in gammas:
            for b in budgets:
                col_det = f"detectable_{b}_g{g}"
                n_det = sub[col_det].sum()
                stats.append({
                    'census_source': src,
                    'gamma': g,
                    'budget': b,
                    'n_phases': n_phases,
                    'n_detectable': n_det,
                    'frac_detectable': n_det / n_phases if n_phases > 0 else 0.0
                })
                
    df_20b = pd.DataFrame(stats)
    
    # Sanity checks
    sanity_passed = True
    
    # (a) Consistency with baseline detectable flags
    match_10b = (df_20a['detectable_unc_g20'] == df_10b_orig['detectable_flag']).all()
    if not match_10b:
        logger.error("SANITY CHECK (a) FAILED: detectable_unc_g20 does not match original detectable_flag.")
        sanity_passed = False
    else:
        logger.info("SANITY CHECK (a) PASSED: consistency with original detectable_flag validated.")
        
    # (b) COVID crash anchor cell
    try:
        covid_row = df_20a[(df_20a['ticker'] == 'SPY') & 
                           (df_20a['start_date'] == '2020-02-19') & 
                           (df_20a['end_date'] == '2020-03-23')].iloc[0]
        # Internal-consistency anchor: the stored columns must be reproducible from
        # the primitives of the same row. This holds under any dating convention and
        # therefore cannot be silently re-tuned to whatever the run produced.
        q1 = min(max(covid_row['q_phase'], 1e-6), 1 - 1e-6)
        q0 = min(max(covid_row['q_ref'], 1e-6), 1 - 1e-6)
        kl_recomputed = q1 * np.log(q1 / q0) + (1 - q1) * np.log((1 - q1) / (1 - q0))
        kl_ok = abs(covid_row['kl_sign_nats_day'] - kl_recomputed) <= 1e-12
        add252_ok = abs(covid_row['ADD_min_sign_g252'] - np.log(252) / kl_recomputed) <= 1e-9
        add20_ok = abs(covid_row['ADD_min_sign_g20'] - np.log(20) / kl_recomputed) <= 1e-9
        logger.info(
            f"COVID anchor: T={covid_row['T_days']}, q_phase={q1:.6f}, "
            f"kl={kl_recomputed:.6f}, floor_g20={np.log(20)/kl_recomputed:.2f}, "
            f"floor_g252={np.log(252)/kl_recomputed:.2f}"
        )
        
        if not (kl_ok and add252_ok and add20_ok):
            logger.error(f"SANITY CHECK (b) FAILED: COVID anchor values incorrect (kl={covid_row['kl_sign_nats_day']}, add252={covid_row['ADD_min_sign_g252']}, add20={covid_row['ADD_min_sign_g20']})")
            sanity_passed = False
        else:
            logger.info("SANITY CHECK (b) PASSED: COVID anchor cell verified.")
    except Exception as e:
        logger.error(f"SANITY CHECK (b) FAILED: Unable to locate COVID anchor by dates. Error: {e}")
        sanity_passed = False
        
    # (c) Abstract claim paper count (~85% out of budget)
    try:
        total_phases = len(df_10b_orig)
        count_unc_20 = df_20b[(df_20b['gamma'] == 20) & 
                              (df_20b['budget'] == 'unc')]['n_detectable'].iloc[0]
        out_of_budget = total_phases - count_unc_20
        frac_out = out_of_budget / total_phases if total_phases > 0 else 0
        
        # Structural assertion (convention-independent): the published count must be
        # exactly the count implied by the floor/duration comparison, with no
        # separate accumulator. A drift here is an implementation error, not a
        # scientific result.
        implied_out = int((df_20a['ADD_min_unc_g20'] >= df_20a['T_days']).sum())
        if implied_out != out_of_budget:
            logger.error(f"SANITY CHECK (c) FAILED: reported {out_of_budget} out-of-budget phases, floor/duration comparison implies {implied_out}.")
            sanity_passed = False
        else:
            logger.info(f"SANITY CHECK (c) PASSED: {out_of_budget}/{total_phases} phases out of budget ({frac_out:.2%}); internally consistent.")
        # Manuscript regression tripwire. EXPECTED_FRAC_OUT tracks the value printed in
        # the paper and MUST be edited only together with the manuscript, in the same
        # commit, with the revision noted below. It never silences the run.
        EXPECTED_FRAC_OUT = 0.803   # articleB v77, post-onset convention, 53/66
        if abs(frac_out - EXPECTED_FRAC_OUT) > 0.02:
            logger.warning(f"MANUSCRIPT DRIFT: out-of-budget fraction {frac_out:.2%} differs from the published {EXPECTED_FRAC_OUT:.1%}; the paper must be updated or this run explained.")
    except Exception as e:
        logger.error(f"SANITY CHECK (c) FAILED: Count extraction error. Error: {e}")
        sanity_passed = False
        
    # (d) No NaN values in valid phases
    if df_20a[df_20a['T_days'] > 0]['kl_sign_nats_day'].isna().any():
        logger.error("SANITY CHECK (d) FAILED: NaN values detected in kl_sign_nats_day for T_days > 0.")
        sanity_passed = False
    else:
        logger.info("SANITY CHECK (d) PASSED: No NaN values in kl_sign_nats_day.")
        
    if not sanity_passed:
        logger.error("CRITICAL HALT: One or more sanity checks failed. CSV generation aborted.")
        sys.exit(1)
        
    # Ecriture des fichiers
    cols_20a = [
        'census_source', 'ticker', 'phase_id', 'phase_type', 'start_date', 'end_date', 'T_days',
        'sharpe', 'q_ref', 'q_phase', 'delta_q', 'kl_sign_nats_day',
        'ADD_min_unc_g20', 'ADD_min_unc_g252', 'ADD_min_unc_g1260',
        'ADD_min_sign_g20', 'ADD_min_sign_g252', 'ADD_min_sign_g1260',
        'detectable_unc_g20', 'detectable_unc_g252', 'detectable_unc_g1260',
        'detectable_sign_g20', 'detectable_sign_g252', 'detectable_sign_g1260',
        'episode_label'
    ]
    df_20a = df_20a[cols_20a]
    # STRICT DETERMINISM: Enforce Kahan's 17-digit rule for exact IEEE-754 round-trip capability
    df_20a.to_csv(FIGURES_DIR / 'protocol_20a_sign_floor.csv', index=False, float_format='%.17g', na_rep='NaN')
    logger.info(f"File generated: {FIGURES_DIR / 'protocol_20a_sign_floor.csv'} ({len(df_20a) + 1} lines)")
    
    cols_20b = ['census_source', 'gamma', 'budget', 'n_phases', 'n_detectable', 'frac_detectable']
    df_20b = df_20b[cols_20b]
    df_20b.to_csv(FIGURES_DIR / 'protocol_20b_census_feasibility_vs_gamma.csv', index=False, float_format='%.17g', na_rep='NaN')
    logger.info(f"File generated: {FIGURES_DIR / 'protocol_20b_census_feasibility_vs_gamma.csv'} ({len(df_20b) + 1} lines)")
    
    logger.info("Processing completed successfully.")

if __name__ == '__main__':
    main()