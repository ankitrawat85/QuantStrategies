# simple_volume_breaks.py
from typing import Optional
import numpy as np
import pandas as pd

def simple_volume_breaks(
    df: pd.DataFrame,
    vol_col: str = "volume",
    date_col: Optional[str] = "date",
    n: float = 2.0,          # trigger if today's vol ≥ n × rolling baseline
    lookback: int = 20,      # baseline window (uses prior bars via shift)
    last_n_days: int = 2,    # only return triggers from the last N days/rows
    use_median: bool = True, # also compare vs rolling median
    z_thresh: Optional[float] = None,  # also flag if z-score ≥ z_thresh (e.g., 2.0)
) -> pd.DataFrame:
    """
    Flags 'unexpected' volume in the last N days. A row triggers if ANY of:
      - Volume ≥ n × rolling mean (over lookback, excluding current bar)
      - (optional) Volume ≥ n × rolling median
      - New rolling MAX (over lookback, excluding current bar)
      - (optional) z-score ≥ z_thresh

    Returns a slim DataFrame with only triggered rows from the last N days.
    Works whether you have a separate date column, a DatetimeIndex, or a plain index.
    """
    if vol_col not in df.columns:
        raise ValueError(f"Column '{vol_col}' not found")

    out = df.copy()

    # Normalize date column if present
    if date_col and date_col in out.columns:
        out[date_col] = pd.to_datetime(out[date_col], errors="coerce")

    v = out[vol_col].astype(float)
    minp = max(5, int(lookback) // 2)

    # Rolling baselines (exclude current bar via shift(1))
    roll_mean   = v.rolling(lookback, min_periods=minp).mean().shift(1)
    roll_median = v.rolling(lookback, min_periods=minp).median().shift(1)
    roll_std    = v.rolling(lookback, min_periods=minp).std(ddof=0).shift(1)
    roll_max    = v.rolling(lookback, min_periods=minp).max().shift(1)

    # Features
    rvol_mean   = v / roll_mean
    rvol_median = v / roll_median
    z           = (v - roll_mean) / roll_std

    # Trigger conditions
    conds = {
        "rvol_mean": (rvol_mean >= float(n)),
        "new_high":  (v >= roll_max),
    }
    if use_median:
        conds["rvol_median"] = (rvol_median >= float(n))
    if z_thresh is not None:
        conds["zscore"] = (z >= float(z_thresh))

    # Combine to a single boolean Series
    any_trigger = pd.Series(False, index=out.index)
    for cond in conds.values():
        any_trigger = any_trigger | cond.fillna(False)

    # Build a simple reason string
    reasons = []
    for i in range(len(out)):
        hits = [name for name, cond in conds.items()
                if pd.notna(cond.iloc[i]) and bool(cond.iloc[i])]
        reasons.append(",".join(hits))

    # Attach columns
    out["rvol_mean"]   = rvol_mean
    out["rvol_median"] = rvol_median
    out["z"]           = z
    out["unexpected"]  = any_trigger
    out["reason"]      = reasons

    # --- Robust "last N days" mask ---
    N = max(1, int(last_n_days))
    if date_col and date_col in out.columns and pd.api.types.is_datetime64_any_dtype(out[date_col]):
        cutoff = out[date_col].max() - pd.Timedelta(days=N - 1)
        mask_last = out[date_col] >= cutoff
    elif isinstance(out.index, pd.DatetimeIndex):
        cutoff = out.index.max() - pd.Timedelta(days=N - 1)
        mask_last = out.index >= cutoff
    else:
        # position-based fallback (works for any index type)
        pos = np.arange(len(out))
        mask_last = pos >= (len(out) - N)

    # Final columns
    cols = ([date_col] if (date_col and date_col in out.columns) else []) + \
           [vol_col, "rvol_mean", "rvol_median", "z", "unexpected", "reason"]
    _output = out.loc[mask_last & out["unexpected"], cols].reset_index(drop=True)

    if len(_output[_output['unexpected']== True]):
        return set(_output[_output['unexpected']== True].iloc[-1].values)
    return False