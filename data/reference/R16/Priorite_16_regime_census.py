"""
STREAM R0 — OFFLINE FEASIBILITY SIEVE / REGIME CENSUS
CORRECTED VERSION: STRICT POST-ONSET BOUNDARY CONVENTION

SOURCES:
- Pagan, A. R. & Sossounov, K. A. (2003). "A simple framework for analysing bull and bear markets", Journal of Applied Econometrics 18(1), 23-46.
- Lunde, A. & Timmermann, A. (2004). "Duration dependence in stock prices...", Journal of Business & Economic Statistics 22(3), 253-273.
- Lorden, G. (1971), Annals of Math. Stat. 42(6) ; Lai, T. L. (1998), IEEE Trans. Inf. Theory 44(7).

NOTATION DEFINITIONS (CRITICAL):
- st, en   : Dates de pic ou de creux délimitant une phase (datation Pagan-Sossounov).
- r_t      : Log-rendement quotidien daté du jour t.
- T_days   : Convention post-onset stricte. La phase [st, en] porte les rendements r_t pour t ∈ ]st, en]. T_days = idx(en) - idx(st).
- SR       : Sharpe annualisé post-onset, mean(r_phase)/std(r_phase, ddof=1) * sqrt(252).
- q_ref    : Taux de jours de hausse sur la phase / sur tout l'historique global.
- ADD_min_days : 504*ln(1/alpha)/SR^2 avec alpha = 0.05 (gamma = 20).
- kl_sign  : Divergence de Bernoulli, q1*ln(q1/q0) + (1-q1)*ln((1-q1)/(1-q0)).
"""

import os

# R0. STRICT DETERMINISM
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["PYTHONHASHSEED"] = "42"

import sys
import numpy as np
import pandas as pd
import logging
import random
from pathlib import Path

# EXPLICIT FAIR FIX
pd.options.compute.use_bottleneck = False
pd.options.compute.use_numexpr = False

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)

set_seed(42)

BASE_DIR = Path(__file__).resolve().parent if '__file__' in locals() else Path.cwd()
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

try:
    from Priorite_14_real_world_backtest import get_daily_data, load_data_fallback
except ImportError:
    logging.warning("Import of Priorite_14_real_world_backtest not found. Execution compromised without data access.")
    def get_daily_data(ticker):
        raise NotImplementedError(f"Please inject the get_daily_data code to load {ticker}.")

log_path = BASE_DIR / 'Priorite_16_regime_census.log'
logging.basicConfig(
    filename=str(log_path),
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.info("--- START STREAM R0: REGIME CENSUS (POST-ONSET STRICT) ---")

# --- ALGORITHMES DE DATATION (INCHANGÉS) ---
def enforce_alternance(pts):
    if not pts: return []
    res = []
    current_type = pts[0][1]
    current_extreme = pts[0]
    for pt in pts[1:]:
        if pt[1] == current_type:
            if current_type == 'peak' and pt[2] > current_extreme[2]:
                current_extreme = pt
            elif current_type == 'trough' and pt[2] < current_extreme[2]:
                current_extreme = pt
        else:
            res.append(current_extreme)
            current_type = pt[1]
            current_extreme = pt
    res.append(current_extreme)
    return res

def pagan_sossounov(prices, window=168, min_phase=84, min_cycle=336, min_edge=126, jump_thresh=0.182321):
    n = len(prices)
    if n < min_cycle: return []
    
    roll_max = prices.rolling(window=2*window+1, center=True, min_periods=1).max()
    roll_min = prices.rolling(window=2*window+1, center=True, min_periods=1).min()
    
    is_peak = (prices == roll_max)
    is_trough = (prices == roll_min)
    
    is_peak.iloc[:min_edge] = False
    is_peak.iloc[-min_edge:] = False
    is_trough.iloc[:min_edge] = False
    is_trough.iloc[-min_edge:] = False
    
    pts = []
    for d, _ in is_peak[is_peak].items(): pts.append((d, 'peak', prices.loc[d]))
    for d, _ in is_trough[is_trough].items(): pts.append((d, 'trough', prices.loc[d]))
    pts.sort(key=lambda x: x[0])
    
    pts = enforce_alternance(pts)
    
    while True:
        pts = enforce_alternance(pts)
        if len(pts) < 2: break
        bad_idx = -1
        min_dur = float('inf')
        for i in range(len(pts)-1):
            dur = prices.index.get_loc(pts[i+1][0]) - prices.index.get_loc(pts[i][0])
            jump = abs(pts[i+1][2] - pts[i][2])
            if dur < min_phase and jump <= jump_thresh:
                if dur < min_dur:
                    min_dur = dur
                    bad_idx = i
        if bad_idx == -1: break
        pts.pop(bad_idx+1)
        pts.pop(bad_idx)
        
    while True:
        pts = enforce_alternance(pts)
        if len(pts) < 3: break
        bad_idx = -1
        min_cyc = float('inf')
        for i in range(len(pts)-2):
            dur = prices.index.get_loc(pts[i+2][0]) - prices.index.get_loc(pts[i][0])
            jump1 = abs(pts[i+1][2] - pts[i][2])
            jump2 = abs(pts[i+2][2] - pts[i+1][2])
            if dur < min_cycle and jump1 <= jump_thresh and jump2 <= jump_thresh:
                if dur < min_cyc:
                    min_cyc = dur
                    bad_idx = i
        if bad_idx == -1: break
        pt1 = pts[bad_idx]
        pt3 = pts[bad_idx+2]
        if pt1[1] == 'peak':
            if pt1[2] < pt3[2]:
                pts.pop(bad_idx+1); pts.pop(bad_idx)
            else:
                pts.pop(bad_idx+2); pts.pop(bad_idx+1)
        else:
            if pt1[2] > pt3[2]:
                pts.pop(bad_idx+1); pts.pop(bad_idx)
            else:
                pts.pop(bad_idx+2); pts.pop(bad_idx+1)
                
    return enforce_alternance(pts)

def lunde_timmermann(prices, lambda_1=0.15, lambda_2=0.15):
    if len(prices) == 0: return []
    state = None
    run_max, run_max_date = prices.iloc[0], prices.index[0]
    run_min, run_min_date = prices.iloc[0], prices.index[0]
    pts = []
    
    for d, p in prices.items():
        if state is None:
            if run_max - p > lambda_1:
                state = -1; pts.append((run_max_date, 'peak', run_max)); run_min, run_min_date = p, d
            elif p - run_min > lambda_2:
                state = 1; pts.append((run_min_date, 'trough', run_min)); run_max, run_max_date = p, d
            else:
                if p > run_max: run_max, run_max_date = p, d
                if p < run_min: run_min, run_min_date = p, d
        elif state == 1:
            if p > run_max: run_max, run_max_date = p, d
            elif run_max - p > lambda_1:
                state = -1; pts.append((run_max_date, 'peak', run_max)); run_min, run_min_date = p, d
        elif state == -1:
            if p < run_min: run_min, run_min_date = p, d
            elif p - run_min > lambda_2:
                state = 1; pts.append((run_min_date, 'trough', run_min)); run_max, run_max_date = p, d
                
    if state == 1: pts.append((run_max_date, 'peak', run_max))
    elif state == -1: pts.append((run_min_date, 'trough', run_min))
    return enforce_alternance(pts)

def get_episodes(start, end, ptype):
    sy, ey = start.year, end.year
    st_str, en_str = start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
    if ptype == 'bear' and st_str <= '2020-03-31' and en_str >= '2020-03-01': return "COVID_2020"
    if ptype == 'bear' and sy <= 2008 and ey >= 2008: return "GFC_2008"
    if ptype == 'bull' and sy <= 2017 and ey >= 2017: return "MeltUp_2017"
    if ptype == 'bull' and (sy <= 2015 <= ey or sy <= 2019 <= ey): return "Calm_2015_or_2019"
    return ""

def check_sanity(phases):
    eps = [get_episodes(p[0], p[1], p[2]) for p in phases]
    return ('COVID_2020' in eps) and ('GFC_2008' in eps) and ('MeltUp_2017' in eps) and any('Calm' in e for e in eps)

def compute_kl_sign(q_phase, q_ref):
    q0 = np.clip(q_ref, 1e-6, 1.0 - 1e-6)
    q1 = np.clip(q_phase, 1e-6, 1.0 - 1e-6)
    if abs(q1 - q0) < 1e-12: return 0.0
    return q1 * np.log(q1 / q0) + (1.0 - q1) * np.log((1.0 - q1) / (1.0 - q0))

# --- EXECUTION PRINCIPALE ---
if __name__ == "__main__":
    tickers = ['SPY', 'PFF', 'VNQ', 'BWX']
    alpha = 0.05
    all_phases_data = []
    split_report_data = []
    delta_report_data = []
    
    for ticker in tickers:
        try:
            data = get_daily_data(ticker)
            if isinstance(data, pd.DataFrame):
                r = data['log_ret'] if 'log_ret' in data.columns else data.iloc[:, 0]
            else:
                r = data
                
            r = r[~r.index.duplicated(keep='first')].sort_index()
            r = r.dropna()
            
            n_days = len(r)
            if n_days == 0: continue
            
            d_start, d_end = r.index[0].strftime('%Y-%m-%d'), r.index[-1].strftime('%Y-%m-%d')
            logging.info(f"[{ticker}] Ingestion OK | {n_days} jours | {d_start} à {d_end}")
            
            prices = r.cumsum()
            pts_macro = pagan_sossounov(prices, window=168, min_phase=84, min_cycle=336, min_edge=126, jump_thresh=0.182321)
            pts_meso = pagan_sossounov(prices, window=63, min_phase=42, min_cycle=126, min_edge=126, jump_thresh=0.182321)
            
            phases_macro = [(pts_macro[i][0], pts_macro[i+1][0], 'bear' if pts_macro[i][1] == 'peak' else 'bull') for i in range(len(pts_macro)-1)]
            
            sanity_ok = True
            if ticker == 'SPY':
                sanity_ok = check_sanity(phases_macro)
                if not sanity_ok:
                    logging.warning("[SPY] Sanity check P-S failed. Fallback to Lunde-Timmermann for MACRO.")
                    pts_macro = lunde_timmermann(prices, lambda_1=0.15, lambda_2=0.15)
                    phases_macro = [(pts_macro[i][0], pts_macro[i+1][0], 'bear' if pts_macro[i][1] == 'peak' else 'bull') for i in range(len(pts_macro)-1)]
            
            final_pts = []
            if len(pts_macro) > 0: final_pts.append(pts_macro[0])
                
            for i in range(len(pts_macro)-1):
                A = pts_macro[i]
                B = pts_macro[i+1]
                dur_macro = prices.index.get_loc(B[0]) - prices.index.get_loc(A[0])
                
                if dur_macro <= 400:
                    final_pts.append(B)
                else:
                    candidates = [m for m in pts_meso if A[0] < m[0] < B[0]]
                    if not candidates:
                        final_pts.append(B)
                        continue
                    seq = [A] + candidates + [B]
                    
                    while True:
                        seq = enforce_alternance(seq)
                        if len(seq) <= 2: break
                        bad_idx = -1
                        min_amp = float('inf')
                        
                        for j in range(len(seq)-1):
                            dur = prices.index.get_loc(seq[j+1][0]) - prices.index.get_loc(seq[j][0])
                            amp = abs(seq[j+1][2] - seq[j][2])
                            if dur < 42 or amp < 0.15:
                                if amp < min_amp:
                                    min_amp = amp; bad_idx = j
                                    
                        if bad_idx != -1:
                            if bad_idx == 0: seq.pop(1) 
                            elif bad_idx == len(seq) - 2: seq.pop(len(seq) - 2) 
                            else: seq.pop(bad_idx + 1)
                        else: break
                            
                    for pt in seq[1:]: final_pts.append(pt)
            
            phases = []
            for i in range(len(final_pts)-1):
                st = final_pts[i][0]; en = final_pts[i+1][0]
                ptype = 'bear' if final_pts[i][1] == 'peak' else 'bull'
                is_macro = any(pts_macro[j][0] == st and pts_macro[j+1][0] == en for j in range(len(pts_macro)-1))
                source_scale = 'MACRO' if is_macro else 'MESO_SPLIT'
                phases.append((st, en, ptype, source_scale))
            
            logging.info(f"[{ticker}] Raffinement : {len(phases_macro)} phases MACRO -> {len(phases)} phases après fusion MESO.")
                
            for i in range(len(pts_macro)-1):
                A = pts_macro[i]; B = pts_macro[i+1]
                dur_macro = prices.index.get_loc(B[0]) - prices.index.get_loc(A[0])
                if dur_macro > 400:
                    sub_ids = [final_id for final_id, p in enumerate(phases) if p[0] >= A[0] and p[1] <= B[0]]
                    split_report_data.append({
                        'ticker': ticker, 'macro_phase_id': i, 'macro_T_days': dur_macro,
                        'n_meso_splits_applied': max(0, len(sub_ids) - 1),
                        'resulting_subphase_ids': str(sub_ids)
                    })
            
            # --- EVALUATION STRICTE AVANT/APRES ---
            q_ref_global = (r > 0).mean()
            ticker_phases = []
            
            for pid, (st, en, ptype, source_scale) in enumerate(phases):
                idx_st = r.index.get_loc(st)
                idx_en = r.index.get_loc(en)
                
                # METRIQUES INCLUSIVES (ERREUR D'ORIGINE - M4 BIAIS)
                r_b = r.loc[st:en]
                T_b = len(r_b)
                ann_vol_b = r_b.std(ddof=1) * np.sqrt(252)
                sr_b = (r_b.mean() * 252) / ann_vol_b if ann_vol_b != 0 else 0
                q_b = (r_b > 0).mean()
                kl_b = compute_kl_sign(q_b, q_ref_global)
                add_b = (504 * np.log(1/alpha)) / (sr_b**2) if sr_b != 0 else np.inf
                det_b = add_b < T_b
                
                # METRIQUES STRICTEMENT POST-ONSET (VERITE TERRAIN ORACLE)
                r_a = r.iloc[idx_st+1 : idx_en+1]
                T_a = idx_en - idx_st 
                
                if T_a < 2: continue
                
                ann_ret_a = r_a.mean() * 252
                ann_vol_a = r_a.std(ddof=1) * np.sqrt(252)
                sr_a = ann_ret_a / ann_vol_a if ann_vol_a != 0 else 0
                q_a = (r_a > 0).mean()
                delta_q_a = q_a - q_ref_global
                kl_a = compute_kl_sign(q_a, q_ref_global)
                add_a = (504 * np.log(1/alpha)) / (sr_a**2) if sr_a != 0 else np.inf
                det_a = add_a < T_a
                
                delta_report_data.append({
                    'ticker': ticker, 'phase_id': pid, 'start_date': st.strftime('%Y-%m-%d'), 'end_date': en.strftime('%Y-%m-%d'),
                    'T_days_before': T_b, 'T_days_after': T_a,
                    'r_boundary': r_b.iloc[0],
                    'sharpe_before': sr_b, 'sharpe_after': sr_a,
                    'ADD_min_before': add_b, 'ADD_min_after': add_a,
                    'q_phase_before': q_b, 'q_phase_after': q_a,
                    'kl_sign_before': kl_b, 'kl_sign_after': kl_a,
                    'detectable_before': det_b, 'detectable_after': det_a,
                    'flipped': det_b != det_a
                })
                
                ticker_phases.append({
                    'ticker': ticker, 'phase_id': pid, 'phase_type': ptype,
                    'start_date': st.strftime('%Y-%m-%d'), 'end_date': en.strftime('%Y-%m-%d'),
                    'T_days': T_a, 'ann_return': ann_ret_a, 'ann_vol': ann_vol_a, 'sharpe': sr_a,
                    'q_ref': q_ref_global, 'q_phase': q_a, 'delta_q': delta_q_a, 'alpha': alpha,
                    'ADD_min_days': add_a, 'detectable_flag': det_a,
                    'base_episode_label': get_episodes(st, en, ptype), 'source_scale': source_scale
                })
                
            logging.info(f"[TOPOLOGY CHECK] N_phases {ticker} initial: {len(phases)}. N_phases post-onset (T>=2): {len(ticker_phases)}. Topologie conservée.")
            
            if ticker_phases:
                df_t = pd.DataFrame(ticker_phases)
                df_t['vol_pct'] = df_t['ann_vol'].rank(pct=True, method='first')
                
                def classify_pathology(row):
                    h_vol = row['vol_pct'] >= 0.75
                    h_sr = abs(row['sharpe']) >= 2.0
                    l_sr = abs(row['sharpe']) < 1.0
                    if h_vol and l_sr: return 'scale'
                    if not h_vol and h_sr: return 'location'
                    if h_vol and h_sr: return 'both'
                    return 'neither'
                    
                df_t['pathology_class'] = df_t.apply(classify_pathology, axis=1)
                
                def refined_episode_label(row):
                    lab = row['base_episode_label']
                    sy = pd.to_datetime(row['start_date']).year
                    ey = pd.to_datetime(row['end_date']).year
                    if (sy <= 2017 and ey >= 2017) and row['phase_type'] == 'bull':
                        if row['vol_pct'] < 0.25 and 150 <= row['T_days'] <= 400 and 2 <= abs(row['sharpe']) <= 4:
                            return "MeltUp_2017"
                        else:
                            return lab.replace("MeltUp_2017", "").strip() if "MeltUp_2017" in lab else lab
                    return lab
                
                df_t['episode_label'] = df_t.apply(refined_episode_label, axis=1)
                df_t = df_t.drop(columns=['base_episode_label'])
                all_phases_data.append(df_t)
                
        except Exception as e:
            logging.error(f"Erreur d'exécution globale pour {ticker}: {e}")
            sys.exit(1)
            
    # --- SYNTHESE, RAPPORTS ET CONTROLES (a-f) ---
    if split_report_data:
        pd.DataFrame(split_report_data).to_csv(FIGURES_DIR / 'protocol_10c_split_report.csv', index=False)
        
    if all_phases_data:
        df_final = pd.concat(all_phases_data, ignore_index=True)
        cols = ['ticker', 'phase_id', 'phase_type', 'start_date', 'end_date', 'T_days', 
                'ann_return', 'ann_vol', 'vol_pct', 'sharpe', 'q_ref', 'q_phase', 'delta_q', 
                'alpha', 'ADD_min_days', 'detectable_flag', 'pathology_class', 'episode_label', 'source_scale']
        df_final = df_final[cols]
        df_final.to_csv(FIGURES_DIR / 'protocol_10b_regime_census_refined.csv', index=False, float_format='%.17g', na_rep='NaN')
        
        df_delta = pd.DataFrame(delta_report_data)
        df_delta.to_csv(FIGURES_DIR / 'protocol_10d_boundary_convention_delta.csv', index=False, float_format='%.17g', na_rep='NaN')
        
        # CONTROLE (a) & (b) - Partition Stricte et Topologie Delta
        for tk in tickers:
            df_tk = df_final[df_final['ticker'] == tk]
            if df_tk.empty: continue
            
            data_tk = get_daily_data(tk)
            r_tk = data_tk['log_ret'] if 'log_ret' in data_tk.columns else data_tk.iloc[:, 0]
            r_tk = r_tk[~r_tk.index.duplicated(keep='first')].sort_index().dropna()
            
            idx_start = r_tk.index.get_loc(pd.to_datetime(df_tk['start_date'].iloc[0]))
            idx_end = r_tk.index.get_loc(pd.to_datetime(df_tk['end_date'].iloc[-1]))
            sum_t = df_tk['T_days'].sum()
            
            if sum_t != (idx_end - idx_start):
                logging.error(f"[SANITY (a) FAILED] {tk}: sum_T={sum_t}, diff={idx_end - idx_start}")
                sys.exit(1)
            else:
                logging.info(f"[SANITY (a) PASSED] {tk}: Partition stricte vérifiée (Sum T_days = {sum_t} = Exact index diff).")
                
        if (df_delta['T_days_before'] - df_delta['T_days_after'] != 1).any():
            logging.error("[SANITY (b) FAILED] Le décalage de T_days diffère de 1.")
            sys.exit(1)
        else:
            logging.info("[SANITY (b) PASSED] Raccourcissement strictement égal à 1 sur toutes les phases (66/66).")
            
        # CONTROLE (e) - Ancrage COVID
        covid_row = df_delta[(df_delta['ticker'] == 'SPY') & (df_delta['start_date'] == '2020-02-19') & (df_delta['end_date'] == '2020-03-23')]
        if not covid_row.empty:
            c = covid_row.iloc[0]
            msg_e = f"""
            --- CONTRÔLE (e) : ANCRAGE COVID-19 ---
            AVANT CORRECTION:
            T_days = {c['T_days_before']}
            sharpe = {c['sharpe_before']:.4f}
            q_phase = {int(round(c['T_days_before'] * c['q_phase_before']))}/{c['T_days_before']} ({c['q_phase_before']:.4f})
            kl_sign = {c['kl_sign_before']:.4f}
            ADD_min_sign_g20 = {np.log(20)/c['kl_sign_before'] if c['kl_sign_before'] != 0 else np.inf:.2f}
            ADD_min_sign_g252 = {np.log(252)/c['kl_sign_before'] if c['kl_sign_before'] != 0 else np.inf:.2f}
            detectable_sign_g20 = {(np.log(20)/c['kl_sign_before']) < c['T_days_before']}
            
            APRÈS CORRECTION (Post-Onset Stricte):
            T_days = {c['T_days_after']}
            sharpe = {c['sharpe_after']:.4f}
            q_phase = {int(round(c['T_days_after'] * c['q_phase_after']))}/{c['T_days_after']} ({c['q_phase_after']:.4f})
            kl_sign = {c['kl_sign_after']:.4f}
            ADD_min_sign_g20 = {np.log(20)/c['kl_sign_after'] if c['kl_sign_after'] != 0 else np.inf:.2f}
            ADD_min_sign_g252 = {np.log(252)/c['kl_sign_after'] if c['kl_sign_after'] != 0 else np.inf:.2f}
            detectable_sign_g20 = {(np.log(20)/c['kl_sign_after']) < c['T_days_after']}
            ---------------------------------------
            """
            logging.info(msg_e)
            print(msg_e)
            
        # CONTROLE (f) - Décomptes HORS BUDGET
        df_delta['add_unc_g20_b'] = (504 * np.log(20)) / df_delta['sharpe_before']**2
        df_delta['add_unc_g20_a'] = (504 * np.log(20)) / df_delta['sharpe_after']**2
        df_delta['add_unc_g252_b'] = (504 * np.log(252)) / df_delta['sharpe_before']**2
        df_delta['add_unc_g252_a'] = (504 * np.log(252)) / df_delta['sharpe_after']**2
        df_delta['add_sign_g20_b'] = np.log(20) / df_delta['kl_sign_before'].replace(0, np.inf)
        df_delta['add_sign_g20_a'] = np.log(20) / df_delta['kl_sign_after'].replace(0, np.inf)
        
        n = len(df_delta)
        c_unc_20_b = (df_delta['add_unc_g20_b'] >= df_delta['T_days_before']).sum()
        c_unc_20_a = (df_delta['add_unc_g20_a'] >= df_delta['T_days_after']).sum()
        c_sign_20_b = (df_delta['add_sign_g20_b'] >= df_delta['T_days_before']).sum()
        c_sign_20_a = (df_delta['add_sign_g20_a'] >= df_delta['T_days_after']).sum()
        c_unc_252_b = (df_delta['add_unc_g252_b'] >= df_delta['T_days_before']).sum()
        c_unc_252_a = (df_delta['add_unc_g252_a'] >= df_delta['T_days_after']).sum()
        
        msg_f = f"""
        --- CONTRÔLE (f) : DÉCOMPTES PUBLIÉS HORS BUDGET (n_phases - n_detectable) ---
        (γ=20, unc)  : AVANT = {c_unc_20_b}/{n} ({c_unc_20_b/n:.1%}) | APRÈS = {c_unc_20_a}/{n} ({c_unc_20_a/n:.1%})
        (γ=20, sign) : AVANT = {c_sign_20_b}/{n} ({c_sign_20_b/n:.1%}) | APRÈS = {c_sign_20_a}/{n} ({c_sign_20_a/n:.1%})
        (γ=252, unc) : AVANT = {c_unc_252_b}/{n} ({c_unc_252_b/n:.1%}) | APRÈS = {c_unc_252_a}/{n} ({c_unc_252_a/n:.1%})
        ------------------------------------------------------------------------------
        """
        logging.info(msg_f)
        print(msg_f)
        
        flipped_phases = df_delta[df_delta['flipped']]
        if not flipped_phases.empty:
            msg_flip = "--- PHASES AYANT BASCULÉ (Flipped Detectability) ---\n"
            for _, row in flipped_phases.iterrows():
                msg_flip += f"[{row['ticker']} Phase {row['phase_id']}] {row['start_date']} to {row['end_date']} (Detect: {row['detectable_before']} -> {row['detectable_after']})\n"
        else:
            msg_flip = "--- PHASES AYANT BASCULÉ (Flipped Detectability) ---\nAucune phase n'a basculé."
        print(msg_flip)
        logging.info(msg_flip)