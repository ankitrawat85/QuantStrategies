
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
trendline_stream_tlc_like_hough_cfg.py

TLC-like trendline streamer with OLS/Huber/Hough seeding **and** JSON config support.
Now includes optional plotting with grouped legends and confidence annotations.

Config precedence (highest → lowest):
1) Command-line flags
2) JSON config file (via --config path)
3) Built-in defaults

You can also dump the *effective* config after parsing with --dump-effective-config FILE.json
"""
import argparse, json, os, sys, math
import numpy as np
import pandas as pd
from dataclasses import dataclass
import matplotlib.dates as mdates
import numpy as np
from matplotlib.patches import Rectangle as _Rect

# === Envelope / Pivot-Channel utilities ===

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
trendline_suite.py

All-in-one toolkit for TLC-like trendlines with four methods:
- OLS
- Huber (robust OLS)
- Hough (pivot voting)
- OLS Envelope (OLS shifted to hug highs/lows): method name = "ols_env"

Features
- Streaming detection with creation / break / expire events
- Confidence-scored breaks (penetration, persistence, retest)
- Reseed modes: single-side or both
- Expiry: hard max length or ATR-based decay
- Snapshot "as of date": active lines + latest signal + channel
- Plotting (preview)
- Run-all helper: execute multiple methods and build a comparison plot
- JSON config with method-specific overrides, plus CLI overrides

Usage samples (see bottom for more):
  python trendline_suite.py stream --config tlc_config_suite.json --csv data_SBIN.csv --method ols_env --plot SBIN_env.png
  python trendline_suite.py run-all --config tlc_config_suite.json --csv data_SBIN.csv --methods ols,huber,hough,ols_env --o
"""
from typing import Optional
import matplotlib.pyplot as plt
#from matplotlib.lines import Line2D
from pathlib import Path as _Path
import os as _os
import numpy as np


# --- Angle veto globals (ADD) ---
ANGLE_BETWEEN_MIN_DEG = 20.0
PARALLEL_GAP_MAX_ATR = 0.5
PARALLEL_GAP_MAX_PCT = None
_ACTIVE_R = None
_ACTIVE_S = None
# --- end angle veto globals ---

def _angle_between_deg(m1: float, m2: float) -> float:
    """Angle between two slopes in degrees."""
    denom = 1.0 + (m1 * m2)
    if abs(denom) < 1e-12:
        return 90.0
    import numpy as _np
    return float(abs(_np.degrees(_np.arctan((m2 - m1) / denom))))

def _line_y(m: float, b: float, x: float) -> float:
    return float(m * x + b)


def atr_wilder(high, low, close, length=14):
    """Compute Wilder's ATR."""
    h, l, c = map(np.asarray, (high, low, close))
    prev_c = np.roll(c, 1)
    tr = np.maximum(h - l, np.maximum(np.abs(h - prev_c), np.abs(l - prev_c)))
    tr[0] = h[0] - l[0]  # initialize first bar
    atr = np.zeros_like(tr, dtype=float)
    atr[:length] = tr[:length].mean()
    alpha = 1.0 / length
    for i in range(length, len(tr)):
        atr[i] = atr[i-1] + alpha * (tr[i] - atr[i-1])
    return atr

def _draw_candles(ax, df_seg, width_frac=0.6):
    """
    Draw OHLC candlesticks on the given axes for the provided DataFrame segment.
    df_seg must have columns: date, open, high, low, close (date as datetime64).
    """
    import numpy as _np

    dates = mdates.date2num(pd.to_datetime(df_seg["date"]))
    if len(dates) > 1:
        dx = _np.median(_np.diff(dates))
    else:
        dx = 1.0
    w = float(dx) * float(width_frac)

    for x, (_, row) in zip(dates, df_seg.iterrows()):
        o = float(row["open"]); h = float(row["high"]); l = float(row["low"]); c = float(row["close"])
        # wick
        ax.vlines(x, l, h, linewidth=1.0)
        # body
        y = min(o, c); height = max(0.5, abs(c - o))
        rect = _Rect((x - w/2.0, y), w, height, fill=True, alpha=0.6, edgecolor="black",
                     facecolor=("tab:green" if c >= o else "tab:red"))
        ax.add_patch(rect)

    ax.xaxis_date()
    ax.grid(True, linestyle="--", alpha=0.25)




def fit_constrained_ols(x, y_fit_ref, c_bound, side, eps=1e-9):
    """
    Solve  min_{m,b} sum_i (y_fit_ref[i] - (m*x[i] + b))^2
    s.t.   resistance (side=='R'):  m*x[i] + b >= c_bound[i]   (typically highs + tol_abs)
           support   (else)       :  m*x[i] + b <= c_bound[i]   (typically lows  - tol_abs)

    Strategy:
      (A) Try unconstrained OLS → if feasible, return it.
      (B) Minimal intercept shift holding OLS slope → feasible.
      (C) All pairwise active-constraint candidates (two points on the bound) → keep feasible ones.
      Pick the feasible candidate with minimum SSE vs y_fit_ref.
    """
    x = np.asarray(x, float)
    y = np.asarray(y_fit_ref, float)
    c = np.asarray(c_bound, float)
    n = len(x)
    assert x.shape == y.shape == c.shape and n >= 2

    # (A) Unconstrained OLS
    X = np.vstack([x, np.ones_like(x)]).T
    m0, b0 = np.linalg.lstsq(X, y, rcond=None)[0]
    line0 = m0 * x + b0
    feas0 = np.all(line0 >= c - eps) if side == "R" else np.all(line0 <= c + eps)
    if feas0:
        return float(m0), float(b0)

    # candidate list
    candidates = []

    # (B) Minimal intercept shift with OLS slope
    if side == "R":
        b_shift = np.max(c - m0 * x)
    else:
        b_shift = np.min(c - m0 * x)
    candidates.append((float(m0), float(b_shift)))

    # (C) Pairwise active constraints
    for i in range(n - 1):
        xi, ci = x[i], c[i]
        for j in range(i + 1, n):
            xj, cj = x[j], c[j]
            if xi == xj:
                continue
            m = (ci - cj) / (xi - xj)
            b = ci - m * xi
            y_line = m * x + b
            feasible = np.all(y_line >= c - eps) if side == "R" else np.all(y_line <= c + eps)
            if feasible:
                candidates.append((float(m), float(b)))

    # fallback (shouldn't happen): use minimal shift
    if not candidates:
        return (float(m0), float(b_shift))

    # choose min-SSE candidate
    best, best_sse = None, np.inf
    for (m, b) in candidates:
        sse = np.sum((y - (m * x + b))**2)
        if sse < best_sse:
            best_sse = sse
            best = (m, b)
    return best

def compute_atr(high, low, close, length=14):
    h,l,c = map(np.asarray, (high, low, close))
    prev_c = np.roll(c, 1)
    tr = np.maximum(h - l, np.maximum(np.abs(h - prev_c), np.abs(l - prev_c)))
    tr[0] = h[0] - l[0]
    atr = np.zeros_like(tr, dtype=float)
    atr[:length] = tr[:length].mean()
    alpha = 1.0 / length
    for i in range(length, len(tr)):
        atr[i] = atr[i-1] + alpha * (tr[i] - atr[i-1])
    return atr

def pivot_points(series, span=10, kind="max"):
    y = np.asarray(series, float); n = len(y); out = []
    for i in range(span, n-span):
        w = y[i-span:i+span+1]
        if (kind=="max" and y[i]==w.max()) or (kind=="min" and y[i]==w.min()):
            out.append(i)
    return np.asarray(out, int)

def fit_ols_line(x, y):
    X = np.vstack([x, np.ones_like(x)]).T
    m, b = np.linalg.lstsq(X, y, rcond=None)[0]
    return float(m), float(b)

def fit_huber_line(x, y, delta=1.0, iters=30, eps=1e-8):
    m, b = fit_ols_line(x, y)
    X = np.vstack([x, np.ones_like(x)]).T
    for _ in range(iters):
        r = y - (m*x + b)
        w = np.where(np.abs(r) <= delta, 1.0, delta / (np.abs(r) + eps))
        WX = X * w[:,None]; Wy = y * w
        m_new, b_new = np.linalg.lstsq(WX, Wy, rcond=None)[0]
        if abs(m_new-m) < 1e-9 and abs(b_new-b) < 1e-6:
            m, b = float(m_new), float(b_new); break
        m, b = float(m_new), float(b_new)
    return m, b

def hough_lines(x, y, piv_idxs, slope_bins=101, intercept_bins=201, top_k=1,
                tol_abs=1.0, min_touches=3):
    if len(piv_idxs) < min_touches: 
        return []
    xs = x[piv_idxs].astype(float); ys = y[piv_idxs].astype(float)
    xr = float(x[-1]-x[0]) if len(x)>1 else 1.0
    yr = float(np.nanmax(y) - np.nanmin(y))
    max_slope = 2.0 * (yr / max(1.0, xr))
    m_grid = np.linspace(-max_slope, max_slope, slope_bins)
    b_min = float(np.nanmin(y) - max_slope * x[-1])
    b_max = float(np.nanmax(y) - (-max_slope) * x[-1])
    b_grid = np.linspace(b_min, b_max, intercept_bins)
    acc = np.zeros((slope_bins, intercept_bins), dtype=np.int32)
    b_vals = ys[:,None] - m_grid[None,:] * xs[:,None]
    bj = np.floor((b_vals - b_min) / (b_max - b_min) * (intercept_bins-1)).astype(int)
    bj = np.clip(bj, 0, intercept_bins-1)
    for i in range(len(xs)):
        acc[np.arange(slope_bins), bj[i]] += 1
    peaks=[]; A=acc.copy()
    for _ in range(top_k*6):
        si, jj = np.unravel_index(np.argmax(A), A.shape)
        votes = int(A[si, jj])
        if votes <= 1: break
        peaks.append((si, jj, votes))
        A[max(0,si-3):min(A.shape[0],si+4), max(0,jj-6):min(A.shape[1],jj+7)] = 0
    lines = []
    for (si, jj, votes) in peaks:
        m = float(m_grid[si]); b = float(b_grid[jj])
        touches = int(np.sum(np.abs(ys - (m*xs + b)) <= tol_abs))
        if touches >= min_touches:
            lines.append(dict(m=m, b=b, touches=touches, votes=votes))
    return sorted(lines, key=lambda d:(-d["votes"], -d["touches"]))[:top_k]

def count_touches(x_idx, price, m, b, tol_abs, spacing=1):
    diffs = np.abs(price - (m*x_idx + b))
    cand = np.where(diffs <= tol_abs)[0]
    touches = []
    last_i = -10**9
    for i in cand:
        if i - last_i >= spacing:
            touches.append(i); last_i = i
    return len(touches), touches

def count_violations(x_idx, price, m, b, tol_abs, side):
    y = m*x_idx + b
    if side == "R":
        return int(np.sum(price > y + tol_abs))
    else:
        return int(np.sum(price < y - tol_abs))

def _sigmoid(x): return 1.0 / (1.0 + np.exp(-x))

def break_confidence(idx, side, m, b, tol_abs, close, atr,
                     persist_n=3, retest_window=6,
                     w_pen=0.5, w_pers=0.3, w_retest=0.2):
    i = int(idx)
    line_i = m*i + b
    pen = (close[i] - line_i) if side=="R" else (line_i - close[i])
    pen_norm = pen / max(1e-8, atr[i])
    pen_score = _sigmoid(pen_norm)
    if pen <= tol_abs: pen_score *= 0.2
    j = min(len(close)-1, i + persist_n)
    idxs = np.arange(i+1, j+1)
    if len(idxs)==0: 
        pers_score = 0.0
    else:
        line_seg = m*idxs + b
        if side=="R":
            pers_hits = np.sum(close[idxs] > line_seg + tol_abs)
        else:
            pers_hits = np.sum(close[idxs] < line_seg - tol_abs)
        pers_score = pers_hits / max(1, len(idxs))
    k = min(len(close)-1, i + retest_window)
    idxs2 = np.arange(i+1, k+1)
    if len(idxs2)==0:
        retest_score = 0.0
    else:
        line_seg2 = m*idxs2 + b
        if side=="R":
            crossed_back = np.any(close[idxs2] < line_seg2 - tol_abs)
        else:
            crossed_back = np.any(close[idxs2] > line_seg2 + tol_abs)
        near = np.any(np.abs(close[idxs2] - line_seg2) <= tol_abs)
        retest_score = 0.0 if crossed_back else (1.0 if near else 0.5)
    conf = float(w_pen*pen_score + w_pers*pers_score + w_retest*retest_score)
    return float(pen_score), float(pers_score), float(retest_score), conf

from dataclasses import dataclass
@dataclass
class LineState:
    side: str
    m: float
    b: float
    start_idx: int
    created_at: int
    age: int = 0
    touches: int = 0
    window_len: int = 0
    lookback_used: int = 0
    pivot_span: Optional[int] = None

import numpy as np  # ensure this is at the top of your module

def seed_line(method, side, x_idx, highs, lows, close, tol_abs, min_touches, touch_spacing,
              max_violations, pivot_span, huber_delta, hough_slope_bins, hough_intercept_bins, topk_per_side,
              env_basis, env_mode, env_k, ATR,max_angle_deg=None):
    """
    Return (m, b, touch_n, touch_ix_local) or None if seed rejected.

    Args:
      method: "ols" | "huber" | "hough" | "ols_env"
      side  : "R" (resistance/highs) or anything else for support/lows
      x_idx : 1-D integer index array for the candidate window
      highs/lows/close: same-length arrays aligned to x_idx’s domain
      tol_abs, min_touches, touch_spacing, max_violations: touch/violation params
      pivot_span, huber_delta, hough_*: method-specific params
      env_basis: "hl2" or "close"  (only used when method == "ols_env")
      env_mode : "shift_min" | "atr" | "pct"
      env_k    : multiplier (for atr/pct modes)
      ATR      : precomputed ATR array aligned to price arrays (may be None unless env_mode == "atr")
    """
    # choose base reference for OLS/Huber
    y_ref_default = highs if side == "R" else lows

    # safety: ensure numpy arrays
    x_idx = np.asarray(x_idx)
    highs = np.asarray(highs)
    lows  = np.asarray(lows)
    close = np.asarray(close)
    if x_idx.size == 0:
        return None

    x = x_idx.astype(float)

    if method == "ols":
        y_use = y_ref_default
        m, b = fit_ols_line(x, y_use)
    
    elif method == "ols_shift_min":
        # Constrained least-squares that hugs candles with tolerance
        y_use = highs if side == "R" else lows
        c_bound = (highs + tol_abs) if side == "R" else (lows - tol_abs)
        m, b = fit_constrained_ols(x, y_use, c_bound, side)

    elif method == "ols_envelop":
        # Envelope variant (ATR / % shift) – this is your current ols_env without shift_min
        # 1) choose fitting basis
        if env_basis == "hl2":
            base_y = (highs + lows) * 0.5
        else:  # "close"
            base_y = close[x_idx.astype(int)]
        if base_y.size == 0:
            return None

        # 2) compute delta by env_mode (ATR or PCT)
        idx0, idx1 = int(x_idx[0]), int(x_idx[-1])
        if env_mode == "atr":
            if ATR is None or ATR.size == 0:
                return None
            seg = ATR[idx0:idx1+1]
            if seg.size == 0 or np.all(np.isnan(seg)):
                return None
            base_shift = float(np.nanmean(seg))
        else:  # "pct"
            seg = close[idx0:idx1+1]
            if seg.size == 0 or np.all(np.isnan(seg)):
                return None
            base_shift = float(np.nanmean(seg)) * 0.01

        delta = env_k * base_shift

        # 3) base OLS on basis, then shift by +/- delta
        m0, b0 = fit_ols_line(x, base_y)
        if side == "R":
            m, b = m0, b0 + delta
            y_use = highs
        else:
            m, b = m0, b0 - delta
            y_use = lows

    elif method == "huber":
        y_use = y_ref_default
        m, b = fit_huber_line(x, y_use, delta=huber_delta)

    elif method == "hough":
        piv = pivot_points(y_ref_default, span=pivot_span, kind=("max" if side == "R" else "min"))
        lines = hough_lines(
            x, y_ref_default, piv,
            slope_bins=hough_slope_bins, intercept_bins=hough_intercept_bins,
            top_k=topk_per_side, tol_abs=tol_abs, min_touches=min_touches
        )
        if not lines:
            return None
        m, b = lines[0]["m"], lines[0]["b"]
        y_use = y_ref_default

    else:
        raise ValueError(f"Unknown method: {method}")

    # --- Absolute steepness guard (new) ---
    if max_angle_deg is not None:
        _ang_abs = float(np.degrees(np.arctan(m)))
        if abs(_ang_abs) > float(max_angle_deg):
            return None
        
    # --- end absolute steepness guard ---

    # ===== Angle-between active line and candidate (parallel-veto) (ADD) =====
    # Active lines are exposed via globals set in stream()/try_seed
    try:
        active = _ACTIVE_R if side == "R" else _ACTIVE_S
    except NameError:
        active = None
    if active is not None:
        m_old = float(getattr(active, "m", getattr(active, "slope", getattr(active, "m", np.nan))))
        b_old = float(getattr(active, "b", getattr(active, "intercept", getattr(active, "b", np.nan))))
        ang_between = _angle_between_deg(m_old, m)

        x_last = float(x_idx[-1])
        gap_end = abs(_line_y(m_old, b_old, x_last) - _line_y(m, b, x_last))

        angle_thresh = ANGLE_BETWEEN_MIN_DEG
        atr_guard = PARALLEL_GAP_MAX_ATR
        pct_guard = PARALLEL_GAP_MAX_PCT

        veto = ang_between < angle_thresh

        if veto and atr_guard is not None and ATR is not None:
            i_last = int(x_last)
            if 0 <= i_last < len(ATR) and np.isfinite(ATR[i_last]):
                veto = gap_end <= atr_guard * abs(float(ATR[i_last]))

        if veto and pct_guard is not None:
            i_last = int(x_last)
            if 0 <= i_last < len(close) and np.isfinite(close[i_last]):
                veto = gap_end <= pct_guard * abs(float(close[i_last]))

        if veto:
            # Keep the current active line; skip this candidate
            return None
    # ===== end parallel-veto =====
# 3) Touches / violations checks
    touch_n, touch_ix_local = count_touches(x, y_use, m, b, tol_abs, spacing=touch_spacing)
    if touch_n < min_touches:
        return None

    viols = count_violations(x, y_use, m, b, tol_abs, side)
    if viols > max_violations:
        return None

    return (m, b, touch_n, touch_ix_local)

def stream(args):
    df = pd.read_csv(args.csv)

    # Ensure datetime index and robust snapshot resolution
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    if getattr(args, 'snapshot_date', None):
        snap_dt = pd.to_datetime(args.snapshot_date, errors='coerce')
        if pd.isna(snap_dt):
            raise ValueError(f"Invalid --snapshot-date: {args.snapshot_date}")
        snap_idx = int(np.searchsorted(df['date'].values, np.datetime64(snap_dt), side='right') - 1)
        snap_idx = max(0, min(snap_idx, len(df)-1))
    else:
        snap_idx = len(df) - 1
    # Resolve snapshot index
    if args.snapshot_date:
        try:
            snap_dt = pd.to_datetime(args.snapshot_date)
            snap_idx = int(np.where(df["date"] <= snap_dt)[0][-1])
        except Exception:
            snap_idx = len(df)-1
    else:
        snap_idx = len(df)-1

    latest_break = None  # store the last accepted break (<= snapshot)
    snapshot_rows = []   # rows to dump if requested

    df.columns = [c.lower() for c in df.columns]
    if "date" in df.columns: df["date"] = pd.to_datetime(df["date"])
    else: df["date"] = pd.RangeIndex(start=0, stop=len(df), step=1)
    openp = df["open"].to_numpy()
    high  = df["high"].to_numpy()
    low   = df["low"].to_numpy()
    close = df["close"].to_numpy()
    dates = df["date"].to_numpy()

    ATR = compute_atr(high, low, close, length=args.atr_len)

    # Sync angle-veto thresholds from CLI into globals (ADD)
    global ANGLE_BETWEEN_MIN_DEG, PARALLEL_GAP_MAX_ATR, PARALLEL_GAP_MAX_PCT

    ANGLE_BETWEEN_MIN_DEG = getattr(args, "angle_between_min_deg", ANGLE_BETWEEN_MIN_DEG)
    PARALLEL_GAP_MAX_ATR  = getattr(args, "parallel_gap_max_atr", PARALLEL_GAP_MAX_ATR)
    PARALLEL_GAP_MAX_PCT  = getattr(args, "parallel_gap_max_pct", PARALLEL_GAP_MAX_PCT)
    # --- end sync ---

    ev_rows, pt_rows = [], []
    active_R = None; active_S = None
    cooldown_R = cooldown_S = 0

    base_W = args.base_window; max_W = args.max_window; step_W = args.step_window

    for t in range(base_W-1, len(df)):
        if active_R: active_R.age += 1
        if active_S: active_S.age += 1
        cooldown_R = max(0, cooldown_R-1); cooldown_S = max(0, cooldown_S-1)

        # Breaks
        for side, st in (("R",active_R), ("S",active_S)):
            if st is None: continue
            y_t = st.m*t + st.b
            tol_abs = args.tol_pct * close[t]
            if side=="R":
                broke = (close[t-1] <= (st.m*(t-1)+st.b) + tol_abs) and (close[t] > y_t + tol_abs)
            else:
                broke = (close[t-1] >= (st.m*(t-1)+st.b) - tol_abs) and (close[t] < y_t - tol_abs)
            if broke:
                pen_s, pers_s, ret_s, conf = break_confidence(
                    t, side, st.m, st.b, tol_abs, close, ATR,
                    persist_n=args.persist_n, retest_window=args.retest_window,
                    w_pen=args.w_pen, w_pers=args.w_pers, w_retest=args.w_retest
                )
                if conf >= args.min_confidence:
                    ev_rows.append(dict(event="break", side=side, idx=t, date=pd.to_datetime(dates[t]),
                                        price=float(y_t), m=st.m, b=st.b, start_idx=st.start_idx,
                                        created_at=st.created_at, touches=st.touches, window_len=st.window_len,
                                        lookback_used=st.lookback_used, confidence=conf,method=args.method,
                                        penetration_score=pen_s, persistence_score=pers_s, retest_score=ret_s))
                if side=="R": active_R=None; cooldown_R=args.cooldown
                else: active_S=None; cooldown_S=args.cooldown
                if args.reseed_mode=="both":
                    if side=="R" and active_S is not None: active_S=None; cooldown_S=args.cooldown
                    if side=="S" and active_R is not None: active_R=None; cooldown_R=args.cooldown

        # Expiry
        for side, st in (("R",active_R), ("S",active_S)):
            if st is None: continue
            expired=False; reason=""
            if args.expiry_mode=="hard":
                if st.age >= args.max_active_len: expired=True; reason="max_active_len"
            else:
                dist = abs(close[t] - (st.m*t + st.b))
                if dist > args.decay_k_atr * ATR[t] and st.age >= args.decay_hold:
                    expired=True; reason=f"decay_{args.decay_k_atr}xATR_for_{args.decay_hold}"
            if expired:
                ev_rows.append(dict(event="expire", side=side, idx=t, date=pd.to_datetime(dates[t]),
                                    price=float(st.m*t + st.b), m=st.m, b=st.b, start_idx=st.start_idx,
                                    created_at=st.created_at, touches=st.touches, window_len=st.window_len,method=args.method,
                                    lookback_used=st.lookback_used, reason=reason))
                if side=="R": active_R=None; cooldown_R=args.cooldown
                else: active_S=None; cooldown_S=args.cooldown

        # Reseed
        def try_seed(side, prev_lookback=None):
            import numpy as np
            nonlocal active_R, active_S, pt_rows
            if side=="R":
                if active_R is not None or cooldown_R>0: return
            else:
                if active_S is not None or cooldown_S>0: return
            tried = []; 
            if prev_lookback is not None: tried.append(prev_lookback)
            W_list = tried + [W for W in range(base_W, max_W+1, step_W) if W not in tried]
            for W in W_list:
                s = t - W + 1
                if s < 0: continue
                x_idx = np.arange(s, t+1)
                highs = high[s:t+1]; lows = low[s:t+1]
                tol_abs = args.tol_pct * float(np.nanmean(close[s:t+1]))
                
                # Expose current actives to seed_line via globals (ADD)
                global _ACTIVE_R, _ACTIVE_S
                _ACTIVE_R, _ACTIVE_S = active_R, active_S
                # --- end expose ---
                fit = seed_line(args.method, side, x_idx, highs, lows, close, tol_abs,
                                args.min_touches, args.touch_spacing, args.max_violations,
                                args.pivot_span, args.huber_delta, args.hough_slope_bins, args.hough_intercept_bins, args.topk_per_side,
                                args.env_basis, args.env_mode, args.env_k, ATR,max_angle_deg=getattr(args, "max_angle_deg", None) )
                if fit is None: continue
                m,b,touch_n,touch_ix_local = fit
                st = LineState(side=side, m=m, b=b, start_idx=int(s), created_at=int(t),
                               age=0, touches=touch_n, window_len=W, lookback_used=W,
                               pivot_span=(args.pivot_span if args.method=="hough" else None))
                if side=="R": active_R=st
                else: active_S=st
                ev_rows.append(dict(event="create", side=side, idx=t, date=pd.to_datetime(dates[t]),
                                    price=float(m*t + b), m=m, b=b, start_idx=int(s), created_at=int(t),
                                    touches=touch_n, window_len=W, lookback_used=W, method=args.method,
                                    pivot_span=(args.pivot_span if args.method=="hough" else "")))
                abs_touch_ix = (s + np.asarray(touch_ix_local, int)).tolist()
                abs_touch_dates = [pd.to_datetime(dates[i]) for i in abs_touch_ix]
                pt_rows.append(dict(side=side, created_at=int(t), start_idx=int(s),
                                    touch_idx=";".join(map(str, abs_touch_ix)),
                                    touch_date=";".join(pd.to_datetime(abs_touch_dates).strftime("%Y-%m-%d"))))
                break

        prev_lb_R = active_R.lookback_used if active_R else None
        prev_lb_S = active_S.lookback_used if active_S else None
        try_seed("R", prev_lb_R)
        try_seed("S", prev_lb_S)

        # If we've reached the snapshot index, capture snapshot state
        if t == snap_idx:
            def line_row(st, side):
                if st is None:
                    return dict(side=side, status="inactive")
                price_at = float(st.m*t + st.b)
                age = int(t - st.created_at)
                return dict(
                    side=side, status="active",
                    m=st.m, b=st.b, start_idx=st.start_idx, created_at=st.created_at,
                    created_date=pd.to_datetime(dates[st.created_at]),
                    touches=st.touches, window_len=st.window_len, lookback_used=st.lookback_used,
                    pivot_span=(st.pivot_span if st.pivot_span is not None else ""),
                    price_at_snapshot=price_at, age_bars=age
                )
            row_R = line_row(active_R, "R")
            row_S = line_row(active_S, "S")
            # Channel (if both active)
            if row_R.get("status")=="active" and row_S.get("status")=="active":
                ch_w = row_R["price_at_snapshot"] - row_S["price_at_snapshot"]
                close_idx = max(0, min(len(close)-1, snap_idx))
                ch_pct = ch_w / max(1e-9, close[close_idx])
            else:
                ch_w = np.nan; ch_pct = np.nan
            snapshot_rows = [
                dict(kind="line", **row_R),
                dict(kind="line", **row_S),
                dict(kind="channel", side="BOTH", status=("active" if np.isfinite(ch_w) else "n/a"),
                     width=ch_w, width_pct=ch_pct)
            ]


    
    # Write normal outputs
    ev_df = pd.DataFrame(ev_rows); pt_df = pd.DataFrame(pt_rows)
    if args.events: ev_df.to_csv(args.events, index=False)
    if args.points: pt_df.to_csv(args.points, index=False)

    # Build snapshot DataFrame
    if snapshot_rows:
        snap_df = pd.DataFrame(snapshot_rows)
        # Attach latest signal (one row) if exists
        sig_df = pd.DataFrame()
        if latest_break is not None:
            sig_df = pd.DataFrame([{
                "kind":"signal", "side": latest_break["side"], "signal": "breakout" if latest_break["side"]=="R" else "breakdown",
                "signal_idx": latest_break["idx"], "signal_date": latest_break["date"],
                "signal_price": latest_break["price"], "confidence": latest_break.get("confidence", np.nan)
            }])
        snapshot_out_df = pd.concat([snap_df, sig_df], ignore_index=True)
        if args.snapshot_out:
            snapshot_out_df.to_csv(args.snapshot_out, index=False)
    else:
        snapshot_out_df = pd.DataFrame()

    # Plot if requested and not snapshot-only
    if args.plot and not args.snapshot_only:
        import matplotlib.pyplot as plt
        # Load events/points either from in-memory DFs or from files
        _ev_df = locals().get('ev_df', None)
        _pt_df = locals().get('pt_df', None)
        if (_ev_df is None or not isinstance(_ev_df, pd.DataFrame)) and getattr(args, 'events', None):
            try:
                _ev_df = pd.read_csv(args.events)
            except Exception:
                _ev_df = None
        if (_pt_df is None or not isinstance(_pt_df, pd.DataFrame)) and getattr(args, 'points', None):
            try:
                _pt_df = pd.read_csv(args.points)
            except Exception:
                _pt_df = None

        # Prep date filtering
        dt = pd.to_datetime(df['date'])
        x0 = pd.to_datetime(args.x_start) if args.x_start else dt.min()
        x1 = pd.to_datetime(args.x_end)   if args.x_end   else dt.max()
        mask = (dt >= x0) & (dt <= x1)
        dfp = df.loc[mask].copy()
        dtp = pd.to_datetime(dfp['date'])

        # Base figure
        fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
        _draw_candles(ax, dfp, width_frac=getattr(args, 'candle_width_frac', 0.6))


        # Helper: index → datetime
        def _i2d(ix:int):
            ix = max(0, min(int(ix), len(dt)-1))
            return dt.iloc[ix]

        # Confidence floor (use CLI if provided, but never below 0.70)
        min_conf_floor = 0.70
        min_conf = max(float(getattr(args, 'min_confidence', min_conf_floor)), min_conf_floor)

        # Draw broken lines (from events df)
        if isinstance(_ev_df, pd.DataFrame) and not _ev_df.empty:
            def _evt_time_ok(row):
                d = _i2d(row.get('idx', 0))
                return (d >= x0) and (d <= x1)

            ev_plot = _ev_df.copy()
            if 'confidence' in ev_plot.columns:
                ev_plot = ev_plot[pd.to_numeric(ev_plot['confidence'], errors='coerce') >= min_conf]
            else:
                ev_plot = ev_plot.iloc[0:0]
            ev_plot = ev_plot[ev_plot.apply(_evt_time_ok, axis=1)]

            for _, row in ev_plot.iterrows():
                m  = float(row.get('m', float('nan')))
                b  = float(row.get('b', float('nan')))
                si = int(row.get('start_idx', row.get('created_at', 0)))
                ei = int(row.get('idx', si))

                d0 = _i2d(si); d1 = _i2d(ei)
                y0 = m*si + b; y1 = m*ei + b

                is_res = str(row.get('side','')).upper().startswith('R')
                color  = 'tab:red' if is_res else 'tab:green'
                line_label  = 'Resistance line' if is_res else 'Support line'
                break_label = 'Resistance break' if is_res else 'Support break'
                break_marker = '^' if is_res else 'v'

                ax.plot([d0, d1], [y0, y1], linewidth=2.0, alpha=0.9, color=color, label=line_label)
                ax.scatter([d1], [y1], s=40, marker=break_marker, zorder=6,
                           edgecolors='black', facecolors=color, label=break_label)

                if getattr(args, 'annotate_conf', False) and ('confidence' in row) and pd.notna(row['confidence']):
                    ax.annotate(f"conf={float(row['confidence']):.2f}",
                                xy=(d1, y1), xytext=(6, 8), textcoords='offset points', fontsize=8)

            # Touch points only for kept events
            if isinstance(_pt_df, pd.DataFrame) and not _pt_df.empty and not ev_plot.empty:
                keep = {(str(r['side']).upper(), int(r['start_idx'])) for _, r in ev_plot.iterrows()
                        if 'side' in r and 'start_idx' in r}
                for _, prow in _pt_df.iterrows():
                    key = (str(prow.get('side','')).upper(), int(prow.get('start_idx',-1)))
                    if key not in keep:
                        continue
                    sidx = str(prow.get('touch_idx','')).strip()
                    if not sidx:
                        continue
                    idxs = []
                    for tok in sidx.split(';'):
                        tok = tok.strip()
                        if tok.isdigit():
                            ii = int(tok)
                            d  = _i2d(ii)
                            if x0 <= d <= x1:
                                idxs.append(ii)
                    if not idxs:
                        continue
                    is_res = key[0].startswith('R')
                    xs = [_i2d(ii) for ii in idxs]
                    ys = [df.loc[ii, 'high'] if is_res else df.loc[ii, 'low'] for ii in idxs]
                    ax.scatter(xs, ys, marker='^' if is_res else 'v',
                               label='Touch (res)' if is_res else 'Touch (sup)')

        # Style & legend
        ax.set_xlim([x0, x1])
        ax.set_title('Trendlines & Breaks'); ax.set_xlabel('Date'); ax.set_ylabel('Price')
        ax.grid(True, alpha=0.25)
        handles, labels = ax.get_legend_handles_labels()
        uniq = {}
        for h, l in zip(handles, labels):
            if l not in uniq:
                uniq[l] = h
        if uniq:
            ax.legend(list(uniq.values()), list(uniq.keys()), loc='best', fontsize=9)

        # Save robustly (expand ~/$VARS; keep real extension last)
        out_path = _Path(_os.path.expanduser(_os.path.expandvars(str(args.plot))))
        if not out_path.suffix:
            out_path = out_path.with_suffix('.png')
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = out_path.with_name(out_path.stem + '.__tmp__' + out_path.suffix)
        ext = out_path.suffix.lstrip('.').lower()
        fig.savefig(str(tmp_path), bbox_inches='tight', dpi=180, format=ext)
        plt.close(fig)
        tmp_path.replace(out_path)
        print(f'Wrote plot: {out_path.resolve()}')
        if args.plot and not args.snapshot_only: print(f"Wrote plot: {args.plot}")
    return 0


def base_parser_for_config():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--config", help="Path to JSON config file")
    p.add_argument("--dump-effective-config", default="", help="Write effective config to JSON then run")
    return p


def merge_config_with_method(cfg: dict, cli_remaining: list):
    """
        Return a dict of defaults = cfg + cfg['methods'][method] if present.
        CLI may specify --method; if not, fall back to cfg['method'] or 'huber'.
    """
    # quick parse to detect CLI method if passed
    import argparse as _argparse
    pre = _argparse.ArgumentParser(add_help=False)
    pre.add_argument("--method", choices=["ols","huber","hough","ols_shift_min","ols_envelop"], default=None)
    pre_args, _ = pre.parse_known_args(cli_remaining)
    method = pre_args.method or cfg.get("method") or "huber"
    defaults = dict(cfg)  # shallow copy
    methods_block = cfg.get("methods", {})
    if isinstance(methods_block, dict) and method in methods_block and isinstance(methods_block[method], dict):
        # overlay method-specific
        for k,v in methods_block[method].items():
            defaults[k] = v
    return defaults

def build_parser(defaults=None):
    p = argparse.ArgumentParser(description="TLC-like trendline streamer (OLS/Huber/Hough) with config support")
    # IO
    p.add_argument("--csv", required=True, help="Prices CSV (date, open, high, low, close)")
    p.add_argument("--events", default="tlc_events.csv", help="Output events CSV")
    p.add_argument("--points", default="tlc_points.csv", help="Output points CSV")
    # Windows
    p.add_argument("--base-window", type=int, default=80)
    p.add_argument("--max-window", type=int, default=160)
    p.add_argument("--step-window", type=int, default=10)
    # Methods
    p.add_argument("--method", choices=["ols","huber","hough","ols_shift_min","ols_envelop"], default="huber")
    p.add_argument("--huber-delta", type=float, default=1.0)
    p.add_argument("--pivot-span", type=int, default=10)
    p.add_argument("--topk-per-side", type=int, default=1)
    p.add_argument("--hough-slope-bins", type=int, default=101)
    p.add_argument("--hough-intercept-bins", type=int, default=201)
    # Acceptance
    p.add_argument("--min-touches", type=int, default=3)
    p.add_argument("--touch-spacing", type=int, default=3)
    p.add_argument("--max-violations", type=int, default=8)
    p.add_argument("--tol-pct", type=float, default=0.01)
    # Reseed/expiry
    p.add_argument("--reseed-immediate", action="store_true")
    p.add_argument("--reseed-mode", choices=["single","both"], default="single")
    p.add_argument("--cooldown", type=int, default=0)
    p.add_argument("--max-active-len", type=int, default=180)
    p.add_argument("--expiry-mode", choices=["hard","decay","soft_hold"], default="hard")

    p.add_argument("--stale-alpha", type=float, default=0.35,
                   help="Plot alpha for stale lines in soft_hold mode")
    p.add_argument("--stale-replace-min-touches", type=int, default=2,
                   help="Min touches a candidate needs to replace a stale line")
    p.add_argument("--relevance-decay", action="store_true",
                   help="Enable relevance score decay when beyond k*ATR")
    p.add_argument("--decay-lambda", type=float, default=0.12,
                   help="Exponential decay rate when beyond k*ATR")
    p.add_argument("--decay-threshold", type=float, default=0.25,
                   help="Expire when relevance drops below this")
    p.add_argument("--decay-max-overdist", type=int, default=5,
                   help="Max consecutive bars beyond k*ATR before expiry")
    p.add_argument("--decay-k-atr", type=float, default=2.5)
    p.add_argument("--decay-hold", type=int, default=10)
    # Confidence
    p.add_argument("--atr-len", type=int, default=14)
    p.add_argument("--persist-n", type=int, default=3)
    p.add_argument("--retest-window", type=int, default=6)
    p.add_argument("--w-pen", type=float, default=0.5)
    p.add_argument("--w-pers", type=float, default=0.3)
    p.add_argument("--w-retest", type=float, default=0.2)
    p.add_argument("--min-confidence", type=float, default=0.0)
    # Plot
    p.add_argument("--plot", default="")
    p.add_argument("--x-start", default="")
    p.add_argument("--x-end", default="")
    p.add_argument("--annotate-conf", action="store_true")
    # Snapshot controls
    p.add_argument("--snapshot-date", default="", help="YYYY-MM-DD; if empty uses last bar")
    p.add_argument("--snapshot-out", default="", help="Write a CSV summary of active lines & latest signal at snapshot date")
    p.add_argument("--snapshot-only", action="store_true", help="Run streaming and emit snapshot (and CSVs) without plotting")

    # Angle-between veto (ADD)
    p.add_argument("--angle-between-min-deg", type=float, default=4.0,
                   help="Skip creating a new line if angle to active line is below this")
    p.add_argument("--parallel-gap-max-atr", type=float, default=0.5,
                   help="Additionally require end-point vertical gap <= this * ATR to veto (None to ignore)")
    p.add_argument("--parallel-gap-max-pct", type=float, default=None,
                   help="Alternatively/also require gap <= this * close price to veto (None to ignore)")
    # --- end angle-between veto flags ---

    p.add_argument("--env-base", type=int, default=14,
                    help="Envelope base length (ATR/pct window)")
    p.add_argument("--env-k", type=float, default=2.0,
                    help="Envelope width multiplier")
    p.add_argument("--env-mode", choices=["atr","pct","abs",'shift_min'], default="atr",
                    help="Envelope mode")
    p.add_argument("--out-prefix", default="out_", help="Prefix for output artifacts")
    p.add_argument("--env_basis", default= "close"),
    p.add_argument("--env_mode", default="shift_min"),
    p.add_argument("--env_k", default= 1.0)
    p.add_argument("--max-angle-deg", type=float, default=None,help="Reject any candidate trendline steeper than this absolute angle (deg) vs horizontal")



    if defaults:
        dests = {a.dest for a in p._actions}
        p.set_defaults(**{k:v for k,v in defaults.items() if k in dests})
    return p

def load_config(path):
    if not path: return {}
    with open(path, "r") as f:
        return json.load(f)

def main():
    pre = base_parser_for_config()
    pre_args, remaining = pre.parse_known_args()
    cfg = load_config(pre_args.config)
    eff_defaults = merge_config_with_method(cfg, remaining)
    parser = build_parser(eff_defaults)
    args = parser.parse_args(remaining)
    if pre_args.dump_effective_config:
        eff = vars(args).copy()
        with open(pre_args.dump_effective_config, "w") as f:
            json.dump(eff, f, indent=2, default=str)
        print(f"Effective config written to: {pre_args.dump_effective_config}")
    return stream(args)

if __name__ == "__main__":
    raise SystemExit(main())


if __name__ == "__main__":
    import argparse, json
    parser = argparse.ArgumentParser(description="Soft-decay trendline runner (enhanced)")
    parser.add_argument("--config", required=False, default="tlc_config_methods_softdecay.json")
    parser.add_argument("--csv", required=False, help="Input CSV for prices")
    parser.add_argument("--plot", required=False, help="Output plot file")
    parser.add_argument("--method", required=False, help="Comma-separated methods (e.g., ols,huber,hough) to run")
    parser.add_argument("--env-base", type=int, default=14, help="Envelope base length (ATR or lookback)")
    parser.add_argument("--env-k", type=float, default=2.0, help="Envelope width multiplier (ATR k or percent)")
    parser.add_argument("--env-mode", choices=["atr","pct","abs"], default="atr", help="Envelope mode: atr|pct|abs")
    parser.add_argument("--out-prefix", default="out_", help="Prefix for output artifacts")
    parser.add_argument("--env-base", type=int, default=14,help="Envelope base length (ATR/pct window)")
    parser.add_argument("--env-k", type=float, default=2.0,help="Envelope width multiplier")
    parser.add_argument("--env-mode", choices=["atr","pct","abs"], default="atr",help="Envelope mode")
    parser.add_argument("--out-prefix", default="out_", help="Prefix for output artifacts")
    # near the other argparse adds
    parser.add_argument("--max-angle-deg", type=float, default=None,help="Reject any candidate trendline steeper than this absolute angle (deg) vs horizontal")

    args = parser.parse_args()

    # Load config and override with CLI when given
    cfg = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, "r") as f:
            cfg = json.load(f)

    cfg.setdefault("env_base", args.env_base)
    cfg.setdefault("env_k", args.env_k)
    cfg.setdefault("env_mode", args.env_mode)
    if args.methods:
        cfg["methods_to_run"] = [m.strip() for m in args.methods.split(",") if m.strip()]
    if args.out_prefix:
        cfg["out_prefix"] = args.out_prefix

    # (Placeholder) call main runner if present
    try:
        main(cfg, args)  # if the module already defines main(cfg,args)
    except NameError:
        pass



# === Envelope / Pivot-Channel utilities ===
def compute_envelope_for_line(line, df, mode="atr", env_base=14, env_k=2.0):
    """
    Compute upper/lower channel for a given trendline.
    Expects: line.slope, line.intercept, line.start_idx, line.end_idx
    Returns dict with 'upper','lower','mid' as lists of (i, y).
    """
    import numpy as np
    n = len(df)
    start = int(getattr(line, "start_idx", 0))
    end   = int(getattr(line, "end_idx", n - 1))
    if end < start:
        start, end = end, start
    xs = np.arange(start, min(end, n - 1) + 1, dtype=int)
    mids = line.slope * xs + line.intercept

    if mode == "atr" and "atr" in df.columns:
        atr_roll = df["atr"].rolling(int(max(1, env_base)), min_periods=1).mean()
        half = env_k * atr_roll.iloc[xs].to_numpy()
    elif mode == "pct":
        half = (float(env_k) * 0.01) * mids
    else:  # "abs" or fallback
        half = float(env_k)
        half = np.full_like(mids, half, dtype=float)

    upper = mids + half
    lower = mids - half
    return {
        "mid":   list(zip(xs.tolist(), mids.tolist())),
        "upper": list(zip(xs.tolist(), upper.tolist())),
        "lower": list(zip(xs.tolist(), lower.tolist())),
    }



def apply_envelope_if_ols_env(method, line, df, args, fig=None, name_prefix="env"):
    """
    Call this right after you create the Line.
    If method == "ols_env", compute envelope & optionally add to `fig` (Plotly or Matplotlib).
    Returns the envelope dict (or None).
    """
    if method != "ols_env" or line is None:
        return None

    # Ensure ATR exists if using ATR mode
    try:
        if getattr(args, "env_mode", "atr") == "atr" and "atr" not in df.columns:
            try:
                atr_len = getattr(args, "atr_len", 14) if hasattr(args, "atr_len") else 14
                if "atr_wilder" in globals():
                    df["atr"] = atr_wilder(df, atr_len)
            except Exception:
                pass
    except Exception:
        pass

    try:
        env = compute_envelope_for_line(
            line, df,
            mode=getattr(args, "env_mode", "atr"),
            env_base=getattr(args, "env_base", 14),
            env_k=getattr(args, "env_k", 2.0)
        )
    except Exception as e:
        print("Envelope computation failed:", e)
        return None

    # Build x-axis
    try:
        xs = [df.index[i] for (i, _) in env["upper"]]
    except Exception:
        xs = [i for (i, _) in env["upper"]]

    # Plotly overlay
    try:
        import plotly.graph_objects as go
        if fig is not None and hasattr(fig, "add_trace"):
            fig.add_trace(go.Scatter(x=xs, y=[y for (_, y) in env["upper"]],
                                     mode="lines", name=f"{name_prefix}↑", opacity=0.5))
            fig.add_trace(go.Scatter(x=xs, y=[y for (_, y) in env["lower"]],
                                     mode="lines", name=f"{name_prefix}↓", opacity=0.5))
    except Exception:
        # Matplotlib fallback
        try:
            import matplotlib.pyplot as plt
            if fig is None:
                plt.plot(xs, [y for (_, y) in env["upper"]], label=f"{name_prefix}↑")
                plt.plot(xs, [y for (_, y) in env["lower"]], label=f"{name_prefix}↓")
        except Exception:
            pass

    return env
