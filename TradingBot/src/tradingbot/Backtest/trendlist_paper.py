import os
import sys
from typing import List, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from skimage.transform import hough_line, hough_line_peaks

# -----------------------------------------------------------------------------
# 1) Data Fetch & Prep
# -----------------------------------------------------------------------------
def fetch_and_prepare_zerodha(root_dir: str, from_date: str, to_date: str,
                              instrument_token: str) -> pd.DataFrame:
    from tradingbot.trading_api.brokers.zerodha import ZerodhaAPI
    zerodha = ZerodhaAPI(os.path.join(root_dir, "config", "Broker", "zerodha.cfg"))
    raw = zerodha.get_historical_data(
        instrument_token=instrument_token,
        interval='day',
        from_date=from_date,
        to_date=to_date,
        output_format='dataframe'
    ).reset_index(drop=True)

    ts_col = 'timestamp' if 'timestamp' in raw.columns else 'date'
    raw[ts_col] = pd.to_datetime(raw[ts_col], errors='coerce').dt.tz_localize(None)
    df = raw.dropna(subset=[ts_col]).set_index(ts_col).sort_index()
    df.columns = [c.capitalize() for c in df.columns]
    for col in ['Open','High','Low','Close']:
        if col not in df:
            raise ValueError(f"Missing required column {col}")
    return df

# -----------------------------------------------------------------------------
# 2) Pivot Detection
# -----------------------------------------------------------------------------
def detect_pivots(df: pd.DataFrame, order: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    highs, lows = df['High'].values, df['Low'].values
    idx_h, _ = find_peaks(highs, distance=order)
    idx_l, _ = find_peaks(-lows, distance=order)
    xs = np.concatenate([idx_h, idx_l])
    ys = np.concatenate([highs[idx_h], lows[idx_l]])
    return xs, ys

# -----------------------------------------------------------------------------
# 3) Build Binary Image & Hough Transform
# -----------------------------------------------------------------------------
def build_binary_image(xs: np.ndarray, ys: np.ndarray,
                       w: int = 500, h: int = 500):
    x_n = (xs - xs.min())/(xs.max()-xs.min())
    y_n = (ys - ys.min())/(ys.max()-ys.min())
    px = (x_n * (w-1)).astype(int)
    py = ((1-y_n) * (h-1)).astype(int)
    img = np.zeros((h, w), bool)
    img[py, px] = True
    return img, (xs.min(), xs.max()), (ys.min(), ys.max())

def detect_hough(img: np.ndarray, num_peaks: int = 10):
    hspace, angles, dists = hough_line(img)
    _, thetas, rhos = hough_line_peaks(hspace, angles, dists, num_peaks=num_peaks)
    return list(zip(thetas, rhos))

# -----------------------------------------------------------------------------
# 4) Group Similar Lines
# -----------------------------------------------------------------------------
def group_lines(lines: List[Tuple[float,float]],
                tol_theta: float=0.02, tol_rho: float=20) -> List[Tuple[float,float]]:
    grouped: List[Tuple[float,float,int]] = []
    for θ,ρ in lines:
        for i,(gθ,gρ,count) in enumerate(grouped):
            if abs(θ-gθ)<tol_theta and abs(ρ-gρ)<tol_rho:
                new_count = count+1
                grouped[i] = ((gθ*count+θ)/new_count,
                              (gρ*count+ρ)/new_count,
                              new_count)
                break
        else:
            grouped.append((θ,ρ,1))
    return [(gθ,gρ) for gθ,gρ,_ in grouped]

# -----------------------------------------------------------------------------
# 5) Pixel↔Data Mapping (corrected)
# -----------------------------------------------------------------------------
def map_line_to_price(theta, rho, x_rng, y_rng, x_vals, img_shape):
    H, W = img_shape
    x0, x1 = x_rng
    y0, y1 = y_rng

    # 1) bar‐index → pixel‐x
    x_norm = (x_vals - x0) / (x1 - x0)
    x_pix  = x_norm * (W - 1)

    # 2) solve line in pixel‐space
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    y_pix = (rho - x_pix * cos_t) / sin_t

    # 3) pixel‐y → normalized price → actual price
    y_norm  = 1 - (y_pix / (H - 1))
    return y_norm * (y1 - y0) + y0

# -----------------------------------------------------------------------------
# 6) Break Detection
# -----------------------------------------------------------------------------
def detect_breaks(df: pd.DataFrame,
                  y_line: np.ndarray,
                  kind: str = 'support',
                  tol_pct: float = 0.005,
                  min_touch: int = 3) -> List[int]:
    """
    Returns list of bar‐indices where the line was first broken,
    after at least `min_touch` prior bars that did not break.
    """
    tol = tol_pct * df['Close']
    field = 'Low' if kind=='support' else 'High'
    crossed = (df[field] < (y_line - tol)) if kind=='support' else (df[field] > (y_line + tol))

    broken = []
    for i in range(min_touch, len(df)):
        prev_prices = df[field].iloc[i-min_touch:i].values
        prev_line   = y_line[i-min_touch:i]
        ok = (prev_prices >= prev_line - tol.iloc[i-min_touch:i]).all() if kind=='support' \
             else (prev_prices <= prev_line + tol.iloc[i-min_touch:i]).all()
        if ok and crossed.iloc[i]:
            broken.append(i)
    return broken

# -----------------------------------------------------------------------------
# 7) Plotting with Break Markers
# -----------------------------------------------------------------------------
def plot_trendlines_with_breaks(df: pd.DataFrame,
                                lines: List[Tuple[float,float]],
                                x_rng, y_rng,
                                img_shape,
                                top_n: int = 5):
    # score & pick top_n
    scored = []
    xs = np.arange(len(df))
    for θ,ρ in lines:
        ys = map_line_to_price(θ, ρ, x_rng, y_rng, xs, img_shape)
        # slope sign → support/resistance
        kind = 'support' if (ys[-1] - ys[0]) > 0 else 'resistance'
        states = detect_breaks(df, ys, kind=kind, tol_pct=0.005, min_touch=3)
        # score = #touches (we’ll use len(states) as a proxy; you can refine)
        scored.append((len(states), θ, ρ, kind, ys, states))
    scored.sort(reverse=True, key=lambda x: x[0])
    best = scored[:top_n]

    plt.figure(figsize=(14,6))
    plt.plot(df['Close'], color='k', label='Close Price')
    for count, θ, ρ, kind, ys, breaks in best:
        label = f"{kind[:3]} θ={θ:.2f},ρ={ρ:.0f},breaks={len(breaks)}"
        plt.plot(df.index, ys, '--', alpha=0.8, label=label)
        # mark break points
        bx = df.index[breaks]
        by = [ys[i] for i in breaks]
        plt.scatter(bx, by, marker='X', s=100,
                    label=f"{kind[:3]} break", zorder=5)
    plt.legend(loc='upper left')
    plt.title("Top Trend‐Lines with Breaks Marked")
    plt.show()

import numpy as np
import pandas as pd

def generate_break_signals(df: pd.DataFrame,
                           lines: List[Tuple[float,float]],
                           x_rng, y_rng, img_shape,
                           tol_pct: float = 0.005,
                           min_touch: int = 3) -> pd.Series:
    """
    For each bar in df, returns +1 if any resistance line breaks here,
    -1 if any support line breaks, or 0 otherwise.
    """
    n = len(df)
    sig = np.zeros(n, dtype=int)
    xs = np.arange(n)

    for θ,ρ in lines:
        # reconstruct the price‐space line
        y_line = map_line_to_price(θ, ρ, x_rng, y_rng, xs, img_shape)
        # classify slope
        kind = 'support' if (y_line[-1] - y_line[0]) > 0 else 'resistance'
        broken = detect_breaks(df, y_line, kind=kind,
                               tol_pct=tol_pct, min_touch=min_touch)
        for i in broken:
            sig[i] = -1 if kind=='support' else +1

    # avoid overlapping signals: pick only the strongest (e.g. first) per bar
    return pd.Series(sig, index=df.index)

def backtest_signals(df: pd.DataFrame,
                     signals: pd.Series,
                     max_holding: int = 10) -> pd.DataFrame:
    """
    Backtest a simple strategy:
      - Enter at next bar open
      - Exit when opposite signal fires or after `max_holding` bars
    Returns a DataFrame of trades and PnL.
    """
    trades = []
    position = 0
    entry_price = None
    entry_idx = None

    for i in range(len(df)-1):
        date = df.index[i]
        sig = signals.iloc[i]
        # entry
        if position == 0 and sig != 0:
            position = sig
            entry_price = df['Open'].iloc[i+1]
            entry_idx = i+1
        # exit: opposite signal
        elif position != 0 and sig == -position:
            exit_price = df['Open'].iloc[i+1]
            trades.append({
                'EntryDate': df.index[entry_idx],
                'ExitDate': df.index[i+1],
                'Position': position,
                'EntryPrice': entry_price,
                'ExitPrice': exit_price,
                'Pnl': position*(exit_price - entry_price)
            })
            position = 0
            entry_price = None
            entry_idx = None
        # exit: max holding
        elif position != 0 and (i+1 - entry_idx) >= max_holding:
            exit_price = df['Open'].iloc[i+1]
            trades.append({
                'EntryDate': df.index[entry_idx],
                'ExitDate': df.index[i+1],
                'Position': position,
                'EntryPrice': entry_price,
                'ExitPrice': exit_price,
                'Pnl': position*(exit_price - entry_price)
            })
            position = 0
            entry_price = None
            entry_idx = None

    return pd.DataFrame(trades)

# -----------------------------------------------------------------------------
# 8) Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    ROOT = os.path.abspath("/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot")
    sys.path.insert(0, ROOT)
    os.chdir(ROOT)

    df = fetch_and_prepare_zerodha(
        root_dir=ROOT,
        from_date='2024-05-01',
        to_date='2025-07-25',
        instrument_token='779521'
    )

    # detect pivots → build Hough image
    px, py            = detect_pivots(df, order=14)
    img, x_rng, y_rng = build_binary_image(px, py, w=500, h=500)

    # raw lines → group near‐dupes
    raw   = detect_hough(img, num_peaks=15)
    lines = group_lines(raw, tol_theta=0.015, tol_rho=25)

    # plot with breaks
    plot_trendlines_with_breaks(df, lines, x_rng, y_rng, img_shape=img.shape, top_n=5)
    signals = generate_break_signals(df, lines, x_rng, y_rng, img.shape)
    trades  = backtest_signals(df, signals, max_holding=5)

    # Results
    print("Total Trades:", len(trades))
    print("Win Rate:  ", (trades['Pnl']>0).mean())
    print("Avg PnL:   ", trades['Pnl'].mean())
    print(trades)
