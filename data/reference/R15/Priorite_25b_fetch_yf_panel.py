# Priorite_25b_fetch_yf_panel.py — quota-friendly daily equity panel for E4.
import os, time, logging
from pathlib import Path
import numpy as np, pandas as pd, yfinance as yf

BASE_DIR = Path("/home/m53/08_articleB/")
YF_DATA_DIR = BASE_DIR / "Data" / "yf"
YF_DATA_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=str(BASE_DIR / "Priorite_25b_fetch_yf_panel.log"),
                    level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger()

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

def fetch_one(t):
    for a in range(1, MAX_RETRY + 1):
        try:
            df = yf.Ticker(t).history(start=START, end=END, interval=INTERVAL, auto_adjust=True)
            if df is None or df.empty or "Close" not in df:
                raise ValueError("empty frame")
            df = df[["Close"]].copy()
            df.index = pd.DatetimeIndex(df.index).tz_localize(None).normalize()
            df["Log_Return"] = np.log(df["Close"] / df["Close"].shift(1))
            out = df[["Close", "Log_Return"]].dropna()
            out.to_csv(YF_DATA_DIR / f"{t}.csv", index_label="Date")
            logger.info(f"{t}: {len(out)} rows [{out.index.min().date()}..{out.index.max().date()}]")
            return out["Log_Return"].rename(t)
        except Exception as e:
            logger.warning(f"{t} attempt {a}/{MAX_RETRY}: {e}"); time.sleep(SLEEP_S * a)
    logger.error(f"{t}: giving up"); return None

def main():
    logger.info(f"Fetching {len(set(UNIVERSE))} tickers {START}..{END} ({INTERVAL}).")
    series = []
    for t in dict.fromkeys(UNIVERSE):          # dedupe, keep order
        s = fetch_one(t)
        if s is not None: series.append(s)
        time.sleep(SLEEP_S)
    if not series:
        logger.error("No tickers fetched; aborting."); return
    panel = pd.concat(series, axis=1).sort_index()
    cov = panel.notna().mean()
    keep = cov[cov >= MIN_COVERAGE].index
    panel = panel[keep].dropna(how="any")
    panel.to_csv(YF_DATA_DIR / "panel_logreturns.csv", index_label="Date")
    logger.info(f"panel_logreturns.csv: {panel.shape[1]} tickers x {panel.shape[0]} days "
                f"[{panel.index.min().date()}..{panel.index.max().date()}] "
                f"(dropped {len(series)-panel.shape[1]} low-coverage). SURVIVORSHIP: fixed current universe.")
    print(f"panel: {panel.shape[1]} tickers x {panel.shape[0]} days")

if __name__ == "__main__":
    main()