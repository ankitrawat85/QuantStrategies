
"""
combined_strength_api.py
------------------------
API to compute consolidated BUY/SELL strengths from per-method event tables that have
'event' and 'confidence' (and typically 'side' = 'S'/'R').

Public API (exported via __all__):
  - StrengthParams
  - consolidate_buy_sell
  - compute_strength_timeseries
  - compute_snapshot_strength
  - snapshot_at
  - get_combined_strength
  - plot_strength_timeseries
  - get_combined_strength_from_snapshot

Input (signals_like):
  * Either a pandas.DataFrame with columns:
        ['date', 'event', 'side', 'method', 'confidence', ...]
    - or any superset where at least event, side, date, method/confidence exist.
    - 'date' or 'created_at' will be used as the event timestamp (date preferred).
  * OR a dict[str -> {'events': DataFrame}], typically keyed by method name, where
    the inner DataFrame has the same columns.

Event -> Trade side mapping conventions:
  - If event.lower() == 'break' and side == 'R' (resistance)  => BUY contribution
  - If event.lower() == 'break' and side == 'S' (support)     => SELL contribution

Decay model (if enabled):
  Contribution of an event dated t0 to a later date t:
    if days_since <= hold_days: w(t) = 1
    else w(t) = exp(-lambda * (days_since - hold_days))
  Event is included only if (confidence * w(t)) >= decay_threshold.
  Final daily BUY/SELL strengths are sums across methods and events (with optional weights).

Percent view:
  You can request *_pct columns, which normalize BUY/SELL strength to percentages of total (absolute) strength.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from typing import Any, Dict, Mapping, Optional, Union, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

__all__ = [
    "StrengthParams",
    "consolidate_buy_sell",
    "compute_strength_timeseries",
    "compute_snapshot_strength",
    "snapshot_at",
    "get_combined_strength",
    "plot_strength_timeseries",
    "get_combined_strength_from_snapshot",
]

# -----------------------
# Parameter container
# -----------------------

@dataclass
class StrengthParams:
    # Minimum raw confidence to allow an event to participate at all
    min_confidence: float = 0.0

    # Exponential decay controls
    decay_lambda: float = 0.12     # per-day lambda (approx half-life ~ ln(2)/lambda)
    decay_hold: int = 0            # days of full weight before decay starts
    decay_threshold: float = 0.25  # discard if (confidence*decay) < threshold

    # Cap/Bound behavior for final daily strengths
    cap_confidence_at_1: bool = True   # clip per-event confidence to [0,1]
    bound_mode: Optional[str] = "clip" # one of {None, "clip"}
    bound_clip_value: float = 1.0      # used if bound_mode == "clip"

    # Optional weighting
    side_weights: Optional[Mapping[str, float]] = None   # {"BUY": 1.0, "SELL": 1.0}
    method_weights: Optional[Mapping[str, float]] = None # {"ols": 1.0, "huber": 0.7, ...}

    # Calendar to compute daily series on (if None, infer union of dates from events)
    calendar_index: Optional[pd.DatetimeIndex] = None

    # Output knobs
    include_pct_columns: bool = True       # master switch for percentage columns
    add_percentage_cols: Optional[bool] = None  # alias -> maps into include_pct_columns (if not None)
    include_indicator_columns: bool = True
    indicator_column_prefix: str = "ind_"
    indicator_list_delim: str = ","

    # Which events contribute strength
    events_as_signals: Optional[Mapping[str, Dict[str, str]]] = None
    # Default:
    #   {"break": {"R": "BUY", "S": "SELL"}}

    def __post_init__(self):
        # support alias 'add_percentage_cols'
        if self.add_percentage_cols is not None:
            self.include_pct_columns = bool(self.add_percentage_cols)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Convert any pd.Index to a serializable form (stringified) for meta
        if isinstance(d.get("calendar_index"), pd.DatetimeIndex):
            d["calendar_index"] = [str(x) for x in d["calendar_index"]]
        return d


def default_events_as_signals() -> Mapping[str, Dict[str, str]]:
    return {"break": {"R": "BUY", "S": "SELL"}}


# -----------------------
# Normalization helpers
# -----------------------

def _first_non_null(*vals):
    for v in vals:
        if v is not None:
            return v
    return None

def _coerce_datetime(s) -> pd.Series:
    try:
        out = pd.to_datetime(s)
    except Exception:
        out = pd.to_datetime(s, errors="coerce")
    return out

def _normalize_events_df(signals_like: Union[pd.DataFrame, Mapping[str, Any]]) -> pd.DataFrame:
    """Return a normalized events DF with columns:
       ['date', 'event', 'side', 'method', 'confidence']
       plus any other columns carried through.
    """
    if isinstance(signals_like, pd.DataFrame):
        df = signals_like.copy()
    elif isinstance(signals_like, Mapping):
        frames = []
        for method, payload in signals_like.items():
            if not isinstance(payload, Mapping) or 'events' not in payload:
                continue
            ev = payload['events'].copy()
            if 'method' not in ev.columns:
                ev['method'] = method
            frames.append(ev)
        if not frames:
            return pd.DataFrame(columns=['date','event','side','method','confidence'])
        df = pd.concat(frames, ignore_index=True, sort=False)
    else:
        raise TypeError("signals_like must be a DataFrame or a dict-of-methods {'m': {'events': df}}")

    # Ensure required columns exist, try to infer/massage
    if 'method' not in df.columns:
        df['method'] = 'unknown'
    # Choose event timestamp: prefer 'date', else 'created_at'
    if 'date' in df.columns:
        dt = _coerce_datetime(df['date'])
    elif 'created_at' in df.columns:
        dt = _coerce_datetime(df['created_at'])
    else:
        raise KeyError("events must have 'date' or 'created_at' column")
    df['date'] = dt
    # Uniform text normalization
    df['event'] = df.get('event', '').astype(str).str.lower()
    if 'side' in df.columns:
        df['side'] = df['side'].astype(str).str.upper().str[0]  # 'S' or 'R' (support/resistance)
    else:
        # If side missing, assume neutral (no signal contribution)
        df['side'] = None

    # Confidence
    if 'confidence' not in df.columns:
        df['confidence'] = 1.0
    df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce').fillna(0.0)

    # Drop rows with no timestamp
    df = df[~df['date'].isna()].copy()
    df.sort_values('date', inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


# -----------------------
# Core math
# -----------------------

def _decay_weight(days_since: int, params: StrengthParams) -> float:
    if days_since <= _safe_int(params.decay_hold):
        return 1.0
    x = max(0, days_since - _safe_int(params.decay_hold))
    lam = float(params.decay_lambda)
    return math.exp(-lam * x)

def _safe_int(x, default=0) -> int:
    try:
        return int(x)
    except Exception:
        return int(default)

def _bound_value(x: float, params: StrengthParams) -> float:
    if params.bound_mode == "clip":
        clipv = float(params.bound_clip_value)
        return max(-clipv, min(clipv, x))
    return x

def _apply_method_side_weights(v: float, method: str, trade_side: str, params: StrengthParams) -> float:
    if params.method_weights and method in params.method_weights:
        v *= float(params.method_weights[method])
    if params.side_weights and trade_side in params.side_weights:
        v *= float(params.side_weights[trade_side])
    return v

def _event_to_trade_side(evt: str, side: Optional[str], events_map: Mapping[str, Dict[str, str]]) -> Optional[str]:
    if side is None or not isinstance(side, str):
        return None
    try:
        mapping = events_map.get(evt, {})
        ts = mapping.get(side)
        return ts  # 'BUY' / 'SELL' / None
    except Exception:
        return None


# -----------------------
# Public functions
# -----------------------

def consolidate_buy_sell(signals_like: Union[pd.DataFrame, Mapping[str, Any]],
                         params: Optional[StrengthParams] = None) -> pd.DataFrame:
    """Return row-per-event DF with columns:
      ['date','method','event','side','confidence','trade_side','weight','buy','sell']
      where buy/sell are the *raw (possibly weighted/decayed)* per-event contributions.
    """
    params = params or StrengthParams()
    events_map = params.events_as_signals or default_events_as_signals()

    df = _normalize_events_df(signals_like)
    # Filter by min_confidence
    df = df[df['confidence'] >= float(params.min_confidence)].copy()

    # trade_side resolution
    df['trade_side'] = [
        _event_to_trade_side(evt, s, events_map) for evt, s in zip(df['event'], df['side'])
    ]

    # Consolidation weight at event-level (cap optional)
    c = df['confidence'].clip(0.0, 1.0) if params.cap_confidence_at_1 else df['confidence']
    df['weight'] = c

    # Apply per-method and per-trade-side weights
    if params.method_weights or params.side_weights:
        df['weight'] = [
            _apply_method_side_weights(v, m, ts if ts else "", params)
            for v, m, ts in zip(df['weight'], df['method'], df['trade_side'])
        ]

    # Split into buy/sell columns (no decay here; decay is applied in per-day aggregation)
    df['buy']  = np.where(df['trade_side'] == 'BUY',  df['weight'], 0.0)
    df['sell'] = np.where(df['trade_side'] == 'SELL', df['weight'], 0.0)
    return df


def _infer_calendar(df: pd.DataFrame, params: StrengthParams) -> pd.DatetimeIndex:
    if params.calendar_index is not None:
        return pd.DatetimeIndex(params.calendar_index)
    # trading days implied by event dates (unique, sorted, daily freq not enforced)
    return pd.DatetimeIndex(sorted(pd.unique(df['date'].dt.normalize())))

def _expand_to_calendar(rows: pd.DataFrame, calendar: pd.DatetimeIndex,
                        params: StrengthParams) -> pd.DataFrame:
    """Aggregate per-event contributions into daily BUY/SELL time series with decay."""
    
    # Prepare containers
    buy = np.zeros(len(calendar), dtype=float)
    sell = np.zeros(len(calendar), dtype=float)

    # Also track indicator presence per-method per day for counts/lists
    methods = sorted(pd.unique(rows['method']))
    ind_cols = [f"{params.indicator_column_prefix}{m}" for m in methods]
    ind_matrix_buy = np.zeros((len(calendar), len(methods)), dtype=int)
    ind_matrix_sell = np.zeros((len(calendar), len(methods)), dtype=int)

    # Pre-vectorize some arrays
    evt_dates = rows['date'].dt.normalize().to_numpy(dtype='datetime64[D]')
    evt_buy   = rows['buy'].to_numpy(float)
    evt_sell  = rows['sell'].to_numpy(float)
    evt_method_idx = rows['method'].map({m:i for i,m in enumerate(methods)}).to_numpy(int)
    evt_trade_side = rows['trade_side'].to_numpy(object)
    evt_conf = rows['confidence'].to_numpy(float)

    cal_np = calendar.values.astype('datetime64[D]')

    for di, day in enumerate(cal_np):
        # days_since per event
        ds = (cal_np[di] - evt_dates).astype('timedelta64[D]').astype(int)
        # Only include events on or before this day
        mask = ds >= 0
        if not mask.any():
            continue
        ds = ds[mask]
        w_buy  = evt_buy[mask].copy()
        w_sell = evt_sell[mask].copy()
        m_idx  = evt_method_idx[mask]
        tside  = evt_trade_side[mask]
        conf   = evt_conf[mask]

        # Decay
        dec = np.ones_like(ds, dtype=float)
        if params.decay_lambda is not None and float(params.decay_lambda) > 0:
            dec = np.where(ds <= int(params.decay_hold), 1.0,
                           np.exp(-float(params.decay_lambda) * (ds - int(params.decay_hold))))

        # Apply threshold (on confidence * decay)
        eff = conf * dec
        keep = eff >= float(params.decay_threshold)
        if keep.any():
            w_buy  = w_buy[keep] * dec[keep]
            w_sell = w_sell[keep] * dec[keep]
            m_idx  = m_idx[keep]
            tside  = tside[keep]

            buy[di]  += w_buy.sum()
            sell[di] += w_sell.sum()

            # Indicator matrices: mark presence (+1/-1) per method on this day
            contrib_sign = np.zeros(len(methods), dtype=int)
            for w, mi, ts in zip(np.r_[w_buy, w_sell], np.r_[m_idx, m_idx], np.r_[np.array(['BUY']*len(w_buy)), np.array(['SELL']*len(w_sell))]):
                if w > 0:
                    contrib_sign[mi] += (1 if ts == 'BUY' else -1)
            ind_matrix_buy[di, :]  = (contrib_sign > 0).astype(int)
            ind_matrix_sell[di, :] = (contrib_sign < 0).astype(int)

    out = pd.DataFrame({
        "date": pd.to_datetime(calendar),
        "buy_strength": buy,
        "sell_strength": sell,
    }).set_index("date", drop=True)

    # net and pct
    out["net_strength"] = out["buy_strength"] - out["sell_strength"]

    if params.include_pct_columns:
        total = (out["buy_strength"].abs() + out["sell_strength"].abs())
        out["buy_strength_pct"]  = np.where(total > 0, out["buy_strength"]  / total * 100.0, 0.0)
        out["sell_strength_pct"] = np.where(total > 0, out["sell_strength"] / total * 100.0, 0.0)
        out["net_strength_pct"]  = np.where(total > 0, out["net_strength"]  / total * 100.0, 0.0)

    if params.bound_mode == "clip":
        clipv = float(params.bound_clip_value)
        out["buy_strength"]  = out["buy_strength"].clip(-clipv, clipv)
        out["sell_strength"] = out["sell_strength"].clip(-clipv, clipv)
        out["net_strength"]  = out["net_strength"].clip(-clipv, clipv)

    if params.include_indicator_columns and len(ind_cols) > 0:
        ind_buy_df  = pd.DataFrame(ind_matrix_buy,  index=out.index, columns=ind_cols)
        ind_sell_df = pd.DataFrame(ind_matrix_sell, index=out.index, columns=ind_cols)
        out = pd.concat([out, ind_buy_df, ind_sell_df], axis=1)
        out["buy_indicator_count"]  = ind_buy_df.sum(axis=1).astype(int)
        out["sell_indicator_count"] = ind_sell_df.sum(axis=1).astype(int)
        # Lists of indicator names that contributed that day
        out["buy_indicators"]  = [params.indicator_list_delim.join([m for m, f in zip(methods, ind_matrix_buy[i]) if f == 1])
                                  for i in range(len(out))]
        out["sell_indicators"] = [params.indicator_list_delim.join([m for m, f in zip(methods, ind_matrix_sell[i]) if f == 1])
                                  for i in range(len(out))]

    return out


def compute_strength_timeseries(signals_like: Union[pd.DataFrame, Mapping[str, Any]],
                                params: Optional[StrengthParams] = None) -> pd.DataFrame:
    params = params or StrengthParams()
    rows = consolidate_buy_sell(signals_like, params=params)
    calendar = _infer_calendar(rows, params)
    return _expand_to_calendar(rows, calendar, params)


def compute_snapshot_strength(signals_like: Union[pd.DataFrame, Mapping[str, Any]],
                              snapshot_date: Union[str, pd.Timestamp],
                              params: Optional[StrengthParams] = None,
                              ignore_prior: bool = False) -> Dict[str, Any]:
    """Compute strength snapshot at a specified date.
    If ignore_prior=True, only events ON snapshot_date contribute; else events on/before decay into it.
    """
    params = params or StrengthParams()
    rows = consolidate_buy_sell(signals_like, params=params)
    day = pd.to_datetime(snapshot_date).normalize()
    if ignore_prior:
        cal = pd.DatetimeIndex([day])
        ts = _expand_to_calendar(rows[rows['date'].dt.normalize() == day], cal, params)
    else:
        # include all prior by using a calendar up to day
        cal = pd.DatetimeIndex(sorted(pd.unique(rows['date'].dt.normalize())))
        cal = cal[cal <= day]
        if len(cal) == 0:
            cal = pd.DatetimeIndex([day])
        ts = _expand_to_calendar(rows, cal, params)
    snap = ts.iloc[-1].to_dict() if len(ts) else {"buy_strength": 0.0, "sell_strength": 0.0, "net_strength": 0.0}
    return {"date": str(day.date()), "values": snap, "params": params.to_dict()}


def snapshot_at(strength_df: pd.DataFrame, date: Union[str, pd.Timestamp]) -> Dict[str, Any]:
    d = pd.to_datetime(date).normalize()
    s = strength_df[strength_df.index.normalize() <= d]
    if len(s) == 0:
        return {"date": str(d.date()), "values": {"buy_strength": 0.0, "sell_strength": 0.0, "net_strength": 0.0}}
    last = s.iloc[-1]
    return {"date": str(d.date()), "values": last.to_dict()}


def get_combined_strength(signals_like: Union[pd.DataFrame, Mapping[str, Any]],
                          **param_kwargs) -> Dict[str, Any]:
    params = StrengthParams(**param_kwargs)
    strength_df = compute_strength_timeseries(signals_like, params=params)
    latest = snapshot_at(strength_df, pd.Timestamp.max)
    return {
        "strength_df": strength_df,
        "snapshot": latest,
        "params": params.to_dict(),
        "meta": {
            "rows": len(strength_df),
            "start": str(strength_df.index.min()) if len(strength_df) else None,
            "end": str(strength_df.index.max()) if len(strength_df) else None,
        }
    }


def plot_strength_timeseries(strength_df: pd.DataFrame, title: Optional[str] = None):
    """Simple Matplotlib plot (single figure, no explicit colors)."""
    fig, ax = plt.subplots(figsize=(10, 4))
    # Plot buy, sell, net
    if "buy_strength" in strength_df.columns:
        ax.plot(strength_df.index, strength_df["buy_strength"], label="BUY strength")
    if "sell_strength" in strength_df.columns:
        ax.plot(strength_df.index, strength_df["sell_strength"], label="SELL strength")
    if "net_strength" in strength_df.columns:
        ax.plot(strength_df.index, strength_df["net_strength"], label="NET strength")

    ax.set_xlabel("Date")
    ax.set_ylabel("Strength")
    if title:
        ax.set_title(title)
    ax.legend(loc="best")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.5)
    fig.tight_layout()
    return fig


# -----------------------
# Snapshot adapters
# -----------------------

def _is_strength_df(df: pd.DataFrame) -> bool:
    cols = set(df.columns)
    return {"buy_strength", "sell_strength"}.issubset(cols)

def _prepare_events_from_snapshot(snapshot_df: pd.DataFrame,
                                  snapshot_date: Optional[str] = None,
                                  weight_column: Optional[str] = None) -> pd.DataFrame:
    """Coerce a flexible snapshot DF into normalized per-event rows."""
    df = snapshot_df.copy()

    # Date handling
    if "date" not in df.columns:
        if snapshot_date is None:
            raise KeyError("Snapshot adapter: need a 'date' column or pass snapshot_date=...")
        df["date"] = pd.to_datetime(snapshot_date)
    else:
        df["date"] = pd.to_datetime(df["date"])

    # Columns defaulting
    if "event" not in df.columns:
        df["event"] = "break"
    if "side" in df.columns:
        df["side"] = df["side"].astype(str).str.upper().str[0]
    else:
        df["side"] = None
    if "method" not in df.columns:
        df["method"] = "unknown"

    # Weight selection
    use_col = None
    for c in [weight_column, "decayed_weight", "weight", "w", "decayed", "confidence"]:
        if c and c in df.columns:
            use_col = c
            break
        if c in df.columns:
            use_col = c
            break
    if use_col is None:
        df["confidence"] = 1.0
    else:
        df["confidence"] = pd.to_numeric(df[use_col], errors="coerce").fillna(0.0)

    keep = [c for c in df.columns if c in {"date","event","side","method","confidence"}]
    df = df[keep].copy()
    return df

def get_combined_strength_from_snapshot(snapshot_df: pd.DataFrame,
                                        snapshot_date: Optional[str] = None,
                                        weight_column: Optional[str] = None,
                                        **param_kwargs) -> Dict[str, Any]:
    """
    High-level: take your test.py 'snapshot' output (either already per-day strength
    or a per-event snapshot), and return the standard get_combined_strength dict.
    - If snapshot_df already has buy_strength/sell_strength columns, it will be returned as-is.
    - Else we convert it to events and compute strengths (calendar = unique dates in snapshot).
    """
    params = StrengthParams(**param_kwargs)

    if _is_strength_df(snapshot_df):
        strength_df = snapshot_df.copy()
        if not isinstance(strength_df.index, pd.DatetimeIndex):
            if "date" in strength_df.columns:
                strength_df = strength_df.set_index(pd.to_datetime(strength_df["date"])).drop(columns=["date"], errors="ignore")
        latest = snapshot_at(strength_df, pd.Timestamp.max)
        return {
            "strength_df": strength_df,
            "snapshot": latest,
            "params": params.to_dict(),
            "meta": {"rows": len(strength_df),
                     "start": str(strength_df.index.min()) if len(strength_df) else None,
                     "end": str(strength_df.index.max()) if len(strength_df) else None}
        }

    # Otherwise, treat it as per-event snapshot
    ev = _prepare_events_from_snapshot(snapshot_df, snapshot_date=snapshot_date, weight_column=weight_column)
    # Use calendar from the snapshot dates only (no prior expansion)
    params.calendar_index = pd.DatetimeIndex(sorted(pd.unique(ev["date"].dt.normalize())))
    strength_df = compute_strength_timeseries(ev, params=params)
    latest = snapshot_at(strength_df, pd.Timestamp.max)
    return {
        "strength_df": strength_df,
        "snapshot": latest,
        "params": params.to_dict(),
        "meta": {"rows": len(strength_df),
                 "start": str(strength_df.index.min()) if len(strength_df) else None,
                 "end": str(strength_df.index.max()) if len(strength_df) else None}
    }
