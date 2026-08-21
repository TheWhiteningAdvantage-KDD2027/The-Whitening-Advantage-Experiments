#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path("/home/m53/08_articleB/")
FIGURES_DIR = BASE_DIR / "figures"

def generate_fig24():
    file_path = FIGURES_DIR / "protocol_19a_oracle_frontier.csv"
    if not file_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {file_path}")
        
    df = pd.read_csv(file_path)
    
    # Filtre sur l'Oracle Paramétrique (V1) non contaminé
    df_v1 = df[(df['sigma_oracle'] == 'V1') & (~df['oracle_contaminated'])]
    
    episodes = ['E1', 'E2', 'E3', 'E4']
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for i, ep in enumerate(episodes):
        ax = axes[i]
        df_ep = df_v1[df_v1['episode_id'] == ep]
        if df_ep.empty:
            ax.set_title(f"Episode {ep} - Data missing")
            continue
            
        t_days = df_ep['T_days_phase'].iloc[0]
        ticker = df_ep['ticker'].iloc[0]
        phase = df_ep['phase_id'].iloc[0]
        
        # Identification dynamique de delta_opt (delta hors grille statique)
        deltas = df_ep[df_ep['detector'] == 'D1']['delta'].dropna().unique()
        static_grid = np.array([0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5])
        d_opt = None
        for d in deltas:
            if not np.any(np.isclose(d, static_grid)):
                d_opt = d
                break
        
        # Fonction de tracé avec tri strict sur lambda pour éviter le zigzag
        def plot_curve(sub_df, label, color, style):
            sub_df = sub_df.sort_values('lambda').dropna(subset=['tau_realized_days'])
            if not sub_df.empty:
                ax.plot(sub_df['FPR_H'], sub_df['tau_realized_days'], label=label, color=color, linestyle=style, linewidth=2)
                
        # D2 (Likelihood Ratio Fisher)
        plot_curve(df_ep[df_ep['detector'] == 'D2'], 'D2 (Fisher LR)', 'black', '-')
        
        # D1 (CUSUM classique delta=0)
        plot_curve(df_ep[(df_ep['detector'] == 'D1') & (df_ep['delta'] == 0.0)], 'D1 (delta = 0.0)', 'blue', '--')
        
        # D1 (CUSUM delta_opt)
        if d_opt is not None:
            plot_curve(df_ep[(df_ep['detector'] == 'D1') & np.isclose(df_ep['delta'], d_opt)], r'D1 ($\delta = \delta_{opt}$)', 'orange', '-.')
            
        # Borne d'horizon (fin de phase)
        ax.axhline(t_days, color='red', linestyle=':', label=r'Phase End ($T$)')
        
        # Inversion de l'axe X (échelle Log) pour lire de gauche à droite (FPR 1.0 -> 0.001)
        ax.set_xscale('log')
        ax.set_xlim(1e-3, 1.0)
        ax.invert_xaxis()
        
        ax.set_title(f"Episode {ep} ({ticker} Phase {phase})")
        ax.set_xlabel(r"False Positive Rate ($FPR_H$) [Reverse Log Scale]")
        ax.set_ylabel(r"Realized Detection Delay ($\tau$)")
        ax.legend(loc="upper left" if i<2 else "lower right")
        ax.grid(True, which="both", ls="-", alpha=0.2)
        
    plt.suptitle("Empirical Oracle Detectability Frontier", weight='bold', fontsize=14)
    plt.tight_layout()
    out_file = FIGURES_DIR / "Fig24_Oracle_Frontier.png"
    plt.savefig(out_file, dpi=300)
    print(f"[SUCCESS] Figure generated successfully: {out_file}")

if __name__ == "__main__":
    generate_fig24()