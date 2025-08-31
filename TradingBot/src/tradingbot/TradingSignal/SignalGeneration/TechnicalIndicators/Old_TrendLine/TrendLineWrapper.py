# ===========================================================
# Trendlines — Batch, Streaming, Hybrid (with Zerodha reseed)
# ===========================================================
from dataclasses import dataclass, field
import os
import datetime as dt
from typing import Optional, Dict, Any, Tuple, List, Callable
import numpy as np
import pandas as pd
import math
from collections import deque
from tradingbot.trading_api.brokers.zerodha import ZerodhaAPI

from tradingbot.TradingSignal.Tradingsignals.TechnicalIndicators.TrendLine.TrendLineCreation import (
                            build_stateful_segments_confirming,   # your batch engine
                            scan_candidates_regression,           # your candidate scanner
                            add_segment_angles,                   # optional, for pattern/angles
                            classify_pattern_for_segment,         # optional, for pattern meta
                            compute_signal_strength,              # returns score/label/confidence/...
                            tol_at,                               # if you need %/abs tolerance
                            Signal,                               # your dataclass
                            MIN_VISIBLE_BARS, REQUIRE_POST_CREATION_TOUCH, TOL_PCT_FOR_INTERACTION,
                            
                        )
# Constants
ROOT = os.environ.get("ZERODHA_ROOT", "/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot")

def fetch_and_prepare_zerodha(root_dir: str, from_date: str, to_date: str, instrument_token: str) -> pd.DataFrame:
    
    cfg = os.path.join(root_dir, "config", "Broker", "zerodha.cfg")
    zerodha = ZerodhaAPI(cfg)
    raw = zerodha.get_historical_data(instrument_token=instrument_token, interval='day',
                                      from_date=from_date, to_date=to_date, output_format='dataframe').reset_index(drop=True)
    ts = 'timestamp' if 'timestamp' in raw.columns else 'date'
    raw[ts] = pd.to_datetime(raw[ts]).dt.tz_localize(None)
    df = raw.set_index(ts).sort_index()
    df = df.rename(columns={c: c.capitalize() for c in df.columns})
    need = ['Open','High','Low','Close']
    if not set(need).issubset(df.columns):
        raise ValueError("Missing OHLC columns after fetch.")
    return df[need]

# If you need ATR tolerance in streaming strength/conf:
def atr_wilder(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["High"], df["Low"], df["Close"]
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0/n, adjust=False, min_periods=n).mean()

# -----------------------------------------------------------
# CONFIG + STATE (Streaming)
# -----------------------------------------------------------
@dataclass
class StreamCfg:
    symbol: str
    interval: str = "15minute"
    base_window: int = 30
    max_window: int = 50
    step_window: int = 10
    # trendline fit / scan controls (mirror your batch)
    method: str = "huber"
    track_support: bool = True
    track_resistance: bool = True
    tol_abs: Optional[float] = None
    tol_pct: Optional[float] = None
    min_touches_support: int = 3
    min_touches_resistance: int = 3
    create_on: str = "both"
    start_new_at_next_bar: bool = False
    prefer_candidate: str = "strongest"
    min_slope_abs: float = 0.0
    force_when_missing: bool = False
    min_r2: float = 0.70
    alpha_p: float = 0.05
    use_atr_tol: bool = True
    touch_spacing: int = 3
    atr_len: int = 14
    max_active_len: int = 150
    recreate_mode: str = "both"  # "both" | "same-side"
    # break/confirm
    confirm_wait: int = 1
    # ATR tolerance multiplier (only used in streaming confirm/strength helpers)
    atr_k: float = 0.5
    # decay
    enable_decay: bool = True
    decay_threshold: float = 0.20
    half_life_bars: int = 80
    touch_half_life: int = 20
    dist_free_atr: float = 0.5
    dist_penalty_k: float = 1.0
    # lookback queue / reseed fetch size
    reseed_pad_bars: int = 10  # fetch a bit more than max_window when reseeding

@dataclass
class Line:
    side: str                  # "support" | "resistance"
    start_idx: int
    slope: float
    intercept: float           # y = intercept + slope * (i - start_idx)
    r2: float
    touches: int = 0
    last_touch_idx: Optional[int] = None
    age_bars: int = 0
    pending_break_t: Optional[int] = None
    break_confirm_needed: bool = False
    max_active_len: int = 150
    quality_floor: float = 0.7
    decay_score: float = 1.0

    def proj(self, i: int) -> float:
        return self.intercept + self.slope * (i - self.start_idx)

@dataclass
class StreamState:
    i: int = -1
    support: Optional[Line] = None
    resistance: Optional[Line] = None
    last_buy: Optional[Dict[str, Any]] = None
    last_sell: Optional[Dict[str, Any]] = None
    # rolling window (for plots/ATR if you prefer local buffer). Optional.
    buffer: deque = field(default_factory=lambda: deque(maxlen=300))

# -----------------------------------------------------------
# STREAMING HELPERS
# -----------------------------------------------------------
def _linreg_y_on_x(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    X = np.c_[np.ones_like(x), x]
    b0, b1 = np.linalg.lstsq(X, y, rcond=None)[0]
    yhat = b0 + b1*x
    ss_tot = ((y - y.mean())**2).sum()
    ss_res = ((y - yhat)**2).sum()
    r2 = 1 - (ss_res/(ss_tot if ss_tot>0 else 1.0))
    return b1, b0, float(max(0.0, min(1.0, r2)))

def _seed_from_candidate(cand: Dict[str, Any], side: str, new_start_idx: int) -> Optional[Line]:
    if cand is None: return None
    slope = cand["slope_sup"] if side == "support" else cand["slope_res"]
    base_int = cand["sup_int"]  if side == "support" else cand["res_int"]
    # shift intercept if needed
    delta = new_start_idx - int(cand["start"])
    intercept = base_int + slope * delta
    touches = int(cand["sup_touches"] if side == "support" else cand["res_touches"])
    return Line(
        side=side,
        start_idx=new_start_idx,
        slope=float(slope),
        intercept=float(intercept),
        r2=float(cand["r2"]),
        touches=touches,
        last_touch_idx=new_start_idx,
        max_active_len=int(cand.get("max_active_len", 150)),
        quality_floor=float(np.clip(cand.get("r2", 0.7), 0.0, 1.0)),
    )

def _touched_bar(hi: float, lo: float, line_px: float, tol_px: float) -> bool:
    return (lo <= line_px + tol_px) and (hi >= line_px - tol_px)

def _decay_score(age_bars, bars_since_touch, dist_atr, q_floor,
                 half_life_bars, touch_half_life, dist_free_atr, dist_penalty_k) -> float:
    lam_age = math.log(2)/max(1, half_life_bars)
    lam_touch = math.log(2)/max(1, touch_half_life)
    time_decay = math.exp(-lam_age * max(0, age_bars))
    touch_decay = math.exp(-lam_touch * max(0, bars_since_touch))
    excess = max(0.0, dist_atr - dist_free_atr)
    dist_decay = 1.0/(1.0 + dist_penalty_k*excess)
    q = max(0.0, min(1.0, q_floor))
    return max(0.0, min(1.0, q * time_decay * touch_decay * dist_decay))

def _strength_conf(side, df, i_prev, i, line: Line, atr_prev, atr_now, atr_k) -> Tuple[float, float]:
    cap = 3.0
    if side == "SELL":  # support break
        lt = line.proj(i_prev); le = line.proj(i)
        breach  = max(0.0, (lt - df["Close"].iat[i_prev] - atr_k*atr_prev) / max(1e-8, atr_prev))
        confirm = max(0.0, (le - df["High"].iat[i]  - atr_k*atr_now) / max(1e-8, atr_now))
    else:               # BUY
        lt = line.proj(i_prev); le = line.proj(i)
        breach  = max(0.0, (df["Close"].iat[i_prev] - lt - atr_k*atr_prev) / max(1e-8, atr_prev))
        confirm = max(0.0, (df["Low"].iat[i]   - le - atr_k*atr_now) / max(1e-8, atr_now))
    b = min(1.0, breach/cap); c = min(1.0, confirm/cap); r = max(0.0, min(1.0, line.r2))
    score = max(0.0, min(100.0, 35*b + 35*c + 30*r))
    conf = round(score/100.0, 3)
    return score, conf


def init_stream_state(
    fetch_last_n: Callable[[str, pd.Timestamp, int, str], pd.DataFrame],
    cfg: StreamCfg,
    end_dt: Optional[pd.Timestamp] = None
) -> Tuple[StreamState, pd.DataFrame, pd.Series]:
    """
    Bootstrap from Zerodha (or your data source). Returns initial state, df_buf, atr_buf.
    """
    need = cfg.max_window + cfg.reseed_pad_bars
    if end_dt is None:
        end_dt = pd.Timestamp.utcnow()  # you can pass IST now if you prefer

    df_buf = fetch_last_n(cfg.symbol, end_dt, need, cfg.interval)
    if df_buf.empty:
        raise RuntimeError("No lookback data available from fetch_last_n().")

    df_buf["timestamp"] = pd.to_datetime(df_buf["timestamp"])
    df_buf.set_index("timestamp", inplace=True)
    atr_buf = atr_wilder(df_buf, cfg.atr_len) if cfg.use_atr_tol else pd.Series(index=df_buf.index, dtype=float)

    # Seed both sides using YOUR scanner so signals match batch
    e_local = len(df_buf) - 1
    coarse_tol = 0.0  # your scanner will handle tol/unit; or use tol_at if needed

    cand = scan_candidates_regression(
        df_buf, e_local, cfg.base_window, cfg.max_window, cfg.step_window, cfg.method, coarse_tol,
        cfg.track_support, cfg.track_resistance, cfg.min_touches_support, cfg.min_touches_resistance,
        cfg.create_on, cfg.prefer_candidate, cfg.min_slope_abs, cfg.force_when_missing,
        cfg.min_r2, cfg.alpha_p, cfg.use_atr_tol, cfg.touch_spacing, cfg.atr_len,
        atr_series=atr_buf if cfg.use_atr_tol else None
    )

    i = e_local
    sup = _seed_from_candidate(cand, "support", i) if cfg.track_support else None
    res = _seed_from_candidate(cand, "resistance", i) if cfg.track_resistance else None

    state = StreamState(i=i, support=sup, resistance=res)
    # preload rolling buffer (optional)
    for ts, r in df_buf.reset_index().iterrows():
        state.buffer.append(r.to_dict())
    return state, df_buf, atr_buf

def update_streaming(
    state: StreamState,
    df_buf: pd.DataFrame,        # growing DataFrame (append new bar before calling)
    atr_buf: pd.Series,          # ATR aligned to df_buf index (append new ATR)
    cfg: StreamCfg,
    fetch_last_n: Callable[[str, pd.Timestamp, int, str], pd.DataFrame],
) -> Tuple[StreamState, Optional[Dict[str, Any]]]:
    """
    Process the NEXT bar already appended to df_buf/atr_buf.
    Reseeds by calling your Zerodha fetcher when a side is missing.
    Returns (updated_state, signal_or_none).
    """
    i = state.i + 1
    if i >= len(df_buf):
        # nothing new
        return state, None

    close = float(df_buf["Close"].iloc[i])
    high  = float(df_buf["High"].iloc[i])
    low   = float(df_buf["Low"].iloc[i])
    atr_now = float(atr_buf.iloc[i]) if cfg.use_atr_tol else 0.0
    atr_prev = float(atr_buf.iloc[i-1]) if cfg.use_atr_tol and i-1 >= 0 else atr_now
    tol_now = cfg.atr_k * atr_now if cfg.use_atr_tol else (cfg.tol_abs or 0.0)

    # A) decay/age/expiry
    for side_name in ("support", "resistance"):
        L: Optional[Line] = getattr(state, side_name)
        if L is None: continue
        L.age_bars = i - L.start_idx + 1
        proj_i = L.proj(i)
        if cfg.use_atr_tol:
            if _touched_bar(high, low, proj_i, tol_now):
                L.last_touch_idx = i
            if cfg.enable_decay:
                dist_atr = abs(close - proj_i) / max(1e-8, atr_now if atr_now > 0 else 1.0)
                dtouch = i - (L.last_touch_idx if L.last_touch_idx is not None else L.start_idx)
                L.decay_score = _decay_score(
                    age_bars=L.age_bars, bars_since_touch=dtouch, dist_atr=dist_atr,
                    q_floor=L.quality_floor, half_life_bars=cfg.half_life_bars, touch_half_life=cfg.touch_half_life,
                    dist_free_atr=cfg.dist_free_atr, dist_penalty_k=cfg.dist_penalty_k
                )
        # expiry rules
        if L.age_bars >= L.max_active_len or (cfg.enable_decay and L.decay_score < cfg.decay_threshold):
            setattr(state, side_name, None)

    # B) only reseed missing sides (HIT ZERODHA HERE)
    for side in ("support", "resistance"):
        L = getattr(state, side)
        if L is None:
            # pull a fresh window from Zerodha, ending at current bar time
            end_dt = df_buf.index[i]
            need = cfg.max_window + cfg.reseed_pad_bars
            df_reseed = fetch_last_n(cfg.symbol, end_dt, need, cfg.interval)
            if df_reseed.empty or len(df_reseed) < cfg.base_window:
                continue  # can't seed now
            df_reseed["timestamp"] = pd.to_datetime(df_reseed["timestamp"])
            df_reseed.set_index("timestamp", inplace=True)
            atr_reseed = atr_wilder(df_reseed, cfg.atr_len) if cfg.use_atr_tol else None

            e_loc = len(df_reseed) - 1
            cand = scan_candidates_regression(
                df_reseed, e_loc, cfg.base_window, cfg.max_window, cfg.step_window, cfg.method, 0.0,
                side == "support", side == "resistance",
                cfg.min_touches_support, cfg.min_touches_resistance,
                cfg.create_on, cfg.prefer_candidate, cfg.min_slope_abs, cfg.force_when_missing,
                cfg.min_r2, cfg.alpha_p, cfg.use_atr_tol, cfg.touch_spacing, cfg.atr_len,
                atr_series=atr_reseed if cfg.use_atr_tol else None
            )
            if cand:
                new_start = i if cfg.start_new_at_next_bar else i  # you can use i+1 if you want
                seeded = _seed_from_candidate(cand, side, new_start)
                setattr(state, side, seeded)

    signal = None

    # C) first-breach + confirm
    for side_name in ("support", "resistance"):
        L: Optional[Line] = getattr(state, side_name)
        if L is None: continue
        proj_i = L.proj(i)

        if side_name == "support":
            # breach
            if not L.break_confirm_needed and close < (proj_i - tol_now):
                L.pending_break_t = i; L.break_confirm_needed = True; continue
            # confirm next bar only
            if L.break_confirm_needed and i == (L.pending_break_t or -1) + cfg.confirm_wait:
                proj_now = L.proj(i)
                if high < (proj_now - tol_now):
                    # SELL signal
                    score, conf = _strength_conf("SELL", df_buf, i-1, i, L, atr_prev, atr_now, cfg.atr_k) if cfg.use_atr_tol else (np.nan, np.nan)
                    signal = {
                        "time": df_buf.index[i], "bar_index": i, "side": "SELL",
                        "price": close, "strength_score": score, "signal_confidence": conf
                    }
                    state.last_sell = {"bar_index": i, "time": df_buf.index[i], "strength": score, "confidence": conf}
                    state.support = None
                    if cfg.recreate_mode == "same-side":
                        # keep the other side as-is
                        pass
                else:
                    L.break_confirm_needed = False; L.pending_break_t = None

        else:  # resistance
            if not L.break_confirm_needed and close > (proj_i + tol_now):
                L.pending_break_t = i; L.break_confirm_needed = True; continue
            if L.break_confirm_needed and i == (L.pending_break_t or -1) + cfg.confirm_wait:
                proj_now = L.proj(i)
                if low > (proj_now + tol_now):
                    # BUY signal
                    score, conf = _strength_conf("BUY", df_buf, i-1, i, L, atr_prev, atr_now, cfg.atr_k) if cfg.use_atr_tol else (np.nan, np.nan)
                    signal = {
                        "time": df_buf.index[i], "bar_index": i, "side": "BUY",
                        "price": close, "strength_score": score, "signal_confidence": conf
                    }
                    state.last_buy = {"bar_index": i, "time": df_buf.index[i], "strength": score, "confidence": conf}
                    state.resistance = None
                    if cfg.recreate_mode == "same-side":
                        pass
                else:
                    L.break_confirm_needed = False; L.pending_break_t = None

    state.i = i
    return state, signal

# -----------------------------------------------------------
# BATCH: thin wrapper (uses your existing function)
# -----------------------------------------------------------
def run_batch(df: pd.DataFrame, cfg: StreamCfg, atr_series: Optional[pd.Series] = None):
    """
    Returns (segments_df, signals_list) using your battle-tested batch implementation.
    """
    return build_stateful_segments_confirming(
        df,
        cfg.base_window, cfg.max_window, cfg.step_window,
        cfg.method, cfg.track_support, cfg.track_resistance,
        cfg.tol_abs, cfg.tol_pct,
        cfg.min_touches_support, cfg.min_touches_resistance,
        cfg.create_on, cfg.start_new_at_next_bar, cfg.prefer_candidate, cfg.min_slope_abs, cfg.force_when_missing,
        cfg.min_r2, cfg.alpha_p, cfg.use_atr_tol, cfg.touch_spacing, cfg.atr_len,
        max_active_len=cfg.max_active_len, recreate_mode=cfg.recreate_mode,
        atr_series=atr_series,
        # If you added decay flags to your batch function, set them here:
        # enable_decay=cfg.enable_decay, decay_threshold=cfg.decay_threshold,
        # half_life_bars=cfg.half_life_bars, touch_half_life=cfg.touch_half_life,
        # dist_free_atr=cfg.dist_free_atr, dist_penalty_k=cfg.dist_penalty_k,
    )

# -----------------------------------------------------------
# HYBRID: stream per bar + periodic batch reconciliation
# -----------------------------------------------------------
def process_stream_hybrid(
    fetch_last_n: Callable[[str, pd.Timestamp, int, str], pd.DataFrame],
    cfg: StreamCfg,
    bars: List[Dict[str, Any]],   # iterable of incoming bars (timestamp, OHLC, ...)
    reconcile_every: int = 50
) -> List[Dict[str, Any]]:
    """
    For each incoming bar:
      - append to df_buf/atr_buf
      - streaming update (+ Zerodha reseed when needed)
      - every `reconcile_every` bars, run batch on the recent window to align/validate
    Returns a list of per-bar outputs (signal or NEUTRAL meta).
    """
    # bootstrap
    state, df_buf, atr_buf = init_stream_state(fetch_last_n, cfg)
    outputs: List[Dict[str, Any]] = []

    for k, bar in enumerate(bars, 1):
        # append bar
        ts = pd.to_datetime(bar["timestamp"])
        df_buf.loc[ts, ["Open","High","Low","Close"]] = [bar["Open"], bar["High"], bar["Low"], bar["Close"]]
        # ATR grow
        if cfg.use_atr_tol:
            # recompute last ATR incrementally or just re-run end (simple way below)
            atr_buf = atr_wilder(df_buf, cfg.atr_len)

        # STREAMING step
        state, sig = update_streaming(state, df_buf, atr_buf, cfg, fetch_last_n)
        if sig is None:
            out = {"time": ts, "bar_index": state.i, "signal": "NEUTRAL", "price": float(df_buf["Close"].iloc[-1])}
        else:
            out = {"time": sig["time"], "bar_index": sig["bar_index"], "signal": sig["side"],
                   "price": sig["price"], "strength_score": sig.get("strength_score"),
                   "signal_confidence": sig.get("signal_confidence")}
        outputs.append(out)

        # HYBRID reconcile
        if reconcile_every and (k % reconcile_every == 0):
            # run batch on the last max_window+pad window (or full df_buf if you prefer)
            tail_n = cfg.max_window + cfg.reseed_pad_bars
            df_tail = df_buf.tail(tail_n).copy()
            atr_tail = atr_buf.tail(tail_n) if cfg.use_atr_tol else None
            segs, signals = run_batch(df_tail, cfg, atr_series=atr_tail)
            # Optionally compare the last streaming signal with batch for parity, or refresh state lines from segs
            # (left as a no-op here to keep this lightweight)

    return outputs



if __name__ == "__main__":

    TOKEN = os.environ.get("ZERODHA_TOKEN", "408065")
    CSV_PATH = os.environ.get("DATA_PATH", "/mnt/data/data_SBIN.csv")
    cfg = os.path.join(ROOT, "config", "Broker", "zerodha.cfg")
    zerodha = ZerodhaAPI(cfg)

    fetch_last_n = zerodha.make_fetcher_zerodha_last_n(
        root_dir=ROOT,
        instrument_token=TOKEN,          # your token
        default_interval='day'         # or "day"
        )
    # BATCH (unchanged)
    cfg = StreamCfg(symbol="SBIN", interval="day",
                    base_window=30, max_window=50, max_active_len=150,
                    use_atr_tol=True, atr_len=14, atr_k=0.5, enable_decay=True)

    # Suppose you already have a full df for backtest:
    # segments, signals = run_batch(df_full, cfg, atr_series=atr_wilder(df_full, 14))

    # STREAMING bootstrap (from Zerodha)
    state, df_buf, atr_buf = init_stream_state(fetch_last_n, cfg, end_dt= dt.date(2025,8,6))

    # In your live loop, after appending a new bar into df_buf:
    state, sig = update_streaming(state, df_buf, atr_buf, cfg, fetch_last_n)
    if sig:
        print("Signal:", sig["side"], sig["price"], sig["strength_score"], sig["signal_confidence"])

    # HYBRID (stream decisions + periodic batch reconciliation)
    outputs = process_stream_hybrid(fetch_last_n, cfg, bars=live_bars, reconcile_every=50)

    # Assume you have:
    # - df_ticks: your 10-row DataFrame with columns ["timestamp","Open","High","Low","Close"]
    # - cfg: your StreamCfg with parameters (base_window, max_window, etc.)
    # - update_streaming: the per-tick update function
    # - init_stream_state: initializes the state from history
    # - fetch_last_n: your Zerodha adapter

    # Bootstrap the streaming state with the first part of df

    #ROOT = os.environ.get("ZERODHA_ROOT", "/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot")
    from collections import deque

    FROM = os.environ.get("ZERODHA_FROM", "2021-11-01")
    TO   = os.environ.get("ZERODHA_TO",   "2024-01-10")

    # 1. Fetch data
    df_ticks = fetch_and_prepare_zerodha(ROOT, FROM, TO, TOKEN)
    df_ticks = df_ticks.reset_index().rename(columns={"index": "timestamp"})  # ensure timestamp column exists

    LOOKBACK_BARS = cfg.max_window + 10  # for safety

    # 2. Initial history chunk
    df_init = df_ticks.head(LOOKBACK_BARS).copy()
    df_init["timestamp"] = pd.to_datetime(df_init["timestamp"])
    df_init = df_init.set_index("timestamp")

    # 3. ATR buffer if needed
    atr_buf = atr_wilder(df_init, cfg.atr_len) if cfg.use_atr_tol else None

    # 4. Initial state as StreamState
    state = StreamState(
        i=len(df_init) - 1,
        support=None,
        resistance=None,
        last_buy=None,
        last_sell=None,
        buffer=deque(df_init.to_dict("records"), maxlen=LOOKBACK_BARS),
    )

    # 5. Simulate feeding ticks
    for i in range(LOOKBACK_BARS, len(df_ticks)):
        new_bar = df_ticks.iloc[i].copy()
        new_bar["timestamp"] = pd.to_datetime(new_bar["timestamp"])

        # Append to buffer
        state.buffer.append(new_bar.to_dict())

        # Prepare df_buf for update_streaming
        df_buf = pd.DataFrame(state.buffer)
        df_buf = df_buf.set_index("timestamp")

        # Recompute ATR on current buffer if needed
        atr_buf = atr_wilder(df_buf, cfg.atr_len) if cfg.use_atr_tol else None

        # Run streaming update
        state, signal = update_streaming(
            state,
            df_buf,
            atr_buf,
            cfg=cfg,
            fetch_last_n=fetch_last_n  # only called on reseed events
        )

        # Output
        ts = new_bar["timestamp"]
        if signal:
            print(f"{ts} → {signal['side']} @ {signal['price']}  "
                f"strength={signal.get('strength_score', float('nan')):.2f} "
                f"conf={signal.get('signal_confidence', float('nan')):.2f}")
        else:
            print(f"{ts} → Neutral")
