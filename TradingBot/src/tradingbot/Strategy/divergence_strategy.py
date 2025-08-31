import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.stats import linregress
from scipy.signal import argrelextrema


def debug_swing_points(series_high, series_low, window=20):
    order = max(1, window // 2)
    print(f"Window={window}, Order={order}, Length={len(series_high)}")
    # check for NaNs and dtype
    print("High dtype / nulls:", series_high.dtypes, series_high.isna().sum())
    print("Low dtype / nulls:", series_low.dtypes, series_low.isna().sum())

    high_vals = series_high.values.astype(float)
    low_vals = series_low.values.astype(float)

    swing_high_idx = argrelextrema(high_vals, np.greater_equal, order=order)[0]
    swing_low_idx = argrelextrema(low_vals, np.less_equal, order=order)[0]

    print("Detected swing high indices:", swing_high_idx)
    print("Detected swing low indices:", swing_low_idx)
    if len(swing_high_idx) == 0:
        print("No swing highs found. Consider reducing window or inspecting the local shape.")
    if len(swing_low_idx) == 0:
        print("No swing lows found.")
    return swing_high_idx, swing_low_idx


from scipy.signal import argrelextrema
import numpy as np

def detect_swing_points(data, window=20, strict=False):
    """
    Returns copy of data with 'Swing_High' and 'Swing_Low' columns.
    If strict=True uses np.greater / np.less instead of >= / <= to avoid flat ties.
    """
    df = data.copy()
    order = max(1, window // 2)
    high = pd.to_numeric(df['High'], errors='coerce')
    low = pd.to_numeric(df['Low'], errors='coerce')

    comparator_high = np.greater if strict else np.greater_equal
    comparator_low = np.less if strict else np.less_equal

    swing_high_idx = argrelextrema(high.values, comparator_high, order=order)[0]
    swing_low_idx = argrelextrema(low.values, comparator_low, order=order)[0]

    df['Swing_High'] = np.nan
    df.loc[df.index[swing_high_idx], 'Swing_High'] = df.loc[df.index[swing_high_idx], 'High']
    df['Swing_Low'] = np.nan
    df.loc[df.index[swing_low_idx], 'Swing_Low'] = df.loc[df.index[swing_low_idx], 'Low']
    return df


def fit_trend_line(points_series, min_points=3):
    """Fit a linear trend line to provided swing points (datetime index)"""
    valid = points_series.dropna()
    if len(valid) < min_points:
        return None, None, None  # insufficient data

    # Convert datetime index to ordinal (float) for regression to reflect actual time spacing
    x = np.array([dt.timestamp() for dt in valid.index])  # seconds since epoch
    y = valid.values.astype(float)

    # Normalize x for numerical stability
    x_mean = x.mean()
    x_norm = x - x_mean

    slope, intercept, r_value, p_value, std_err = linregress(x_norm, y)
    # Reconstruct full trend line over the original points_series index
    full_x = np.array([dt.timestamp() for dt in points_series.index])
    full_x_norm = full_x - x_mean
    trend_line = slope * full_x_norm + intercept

    return slope, intercept, trend_line

def detect_trend_break(data, trend_type, slope, intercept, break_pct=0.005,
                       vol_multiplier=1.2, confirmation_bars=2, vol_window=20):
    """Detect confirmed trend breaks with volume filter"""
    if slope is None:
        return pd.Series(False, index=data.index)

    df = data.copy()
    # Build trend line over the index
    timestamps = np.array([ts.timestamp() for ts in df.index])
    x_mean = timestamps.mean()
    x_norm = timestamps - x_mean
    trend_line = slope * x_norm + intercept
    df['Trend_Line'] = trend_line

    close = df['Close']

    if trend_type == 'support':
        raw_break = close < trend_line * (1 - break_pct)
    else:  # resistance
        raw_break = close > trend_line * (1 + break_pct)

    # Volume condition: require enough history to compute rolling mean
    rolling_vol_mean = df['Volume'].rolling(vol_window, min_periods=1).mean()
    vol_cond = df['Volume'] > rolling_vol_mean * vol_multiplier

    # Confirmation: after a raw_break, require that the next (confirmation_bars - 1) bars also satisfy the raw break
    # We define confirmed_break as: raw_break at t AND for next confirmation_bars-1 bars raw_break still True
    confirmed = pd.Series(False, index=df.index)
    for i in range(len(df) - confirmation_bars + 1):
        window_breaks = raw_break.iloc[i:i + confirmation_bars].all()
        if window_breaks:
            confirmed.iloc[i + confirmation_bars - 1] = True  # mark at the last bar of confirmation

    final_signal = raw_break & vol_cond & confirmed
    return final_signal

def plot_signals(data, trend_type, trend_line_label):
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Close Price', alpha=0.6)
    if 'Trend_Line' in data:
        plt.plot(data['Trend_Line'], '--', label=trend_line_label)
    plt.scatter(data.index, data['Swing_High'], marker='^', s=80,
                label='Swing Highs', edgecolor='green', facecolors='none', linewidths=1.5)
    plt.scatter(data.index, data['Swing_Low'], marker='v', s=80,
                label='Swing Lows', edgecolor='red', facecolors='none', linewidths=1.5)
    if 'Break_Signal' in data:
        sigs = data[data['Break_Signal']]
        plt.scatter(sigs.index, sigs['Close'], c='black', marker='X', s=150, label='Break Signal')
    plt.title(f'Trend Line Break - {trend_type.capitalize()}') 
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def trend_line_break_strategy(ticker='AAPL', period='6mo',
                              min_points=3, break_pct=0.005,
                              vol_multiplier=1.2, confirmation_bars=2,
                              swing_window=20):
    # Fetch data
    data = yf.download(ticker, period=period)
    data.to_csv("MFST.csv")
    if data.empty:
        print("No data fetched for", ticker)
        return None

    # Detect swing points
    data = detect_swing_points(data, window=swing_window)
    data['Break_Signal'] = False
    data['Signal_Type'] = None

    # Support (using swing lows)
    slope, intercept, trend_line = fit_trend_line(data['Swing_Low'], min_points=min_points)
    if slope is not None:
        support_breaks = detect_trend_break(data, 'support', slope, intercept,
                                            break_pct=break_pct,
                                            vol_multiplier=vol_multiplier,
                                            confirmation_bars=confirmation_bars)
        if support_breaks.any():
            data.loc[support_breaks, 'Break_Signal'] = True
            data.loc[support_breaks, 'Signal_Type'] = 'Support Break'
        # Attach trend line for plotting
        # Recompute trend line for the full index similarly to fit_trend_line output
        timestamps = np.array([ts.timestamp() for ts in data.index])
        x_mean = timestamps.mean()
        trend_line_full = slope * (timestamps - x_mean) + intercept
        data['Trend_Line'] = trend_line_full
        plot_signals(data, 'support', 'Support Trend')

    # Resistance (using swing highs)
    slope_r, intercept_r, trend_line_r = fit_trend_line(data['Swing_High'], min_points=min_points)
    if slope_r is not None:
        resistance_breaks = detect_trend_break(data, 'resistance', slope_r, intercept_r,
                                               break_pct=break_pct,
                                               vol_multiplier=vol_multiplier,
                                               confirmation_bars=confirmation_bars)
        if resistance_breaks.any():
            # If there's overlap, prefer labeling both indicators (could be refined)
            data.loc[resistance_breaks, 'Break_Signal'] = True
            data.loc[resistance_breaks, 'Signal_Type'] = 'Resistance Break'
        # Attach resistance trend line separately for plotting (don't overwrite previous if present)
        timestamps = np.array([ts.timestamp() for ts in data.index])
        x_mean_r = timestamps.mean()
        trend_line_full_r = slope_r * (timestamps - x_mean_r) + intercept_r
        data['Trend_Line'] = trend_line_full_r
        plot_signals(data, 'resistance', 'Resistance Trend')

    # Final detected signals
    signals = data[data['Break_Signal']][['Close', 'Signal_Type']]
    if not signals.empty:
        print(f"Detected signals (min_points={min_points}):\n{signals}")
    else:
        print(f"No confirmed breaks detected for {ticker} with current parameters.")
    return data

# Example usage
if __name__ == "__main__":
    df = trend_line_break_strategy(ticker='MSFT', period='1y',
                                   min_points=4,
                                   break_pct=0.005,
                                   vol_multiplier=1.2,
                                   confirmation_bars=2,
                                   swing_window=20)
    