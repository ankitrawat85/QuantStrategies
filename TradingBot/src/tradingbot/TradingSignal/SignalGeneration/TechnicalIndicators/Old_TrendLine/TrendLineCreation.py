
import os
import sys
import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from sklearn.linear_model import LinearRegression, HuberRegressor, RANSACRegressor

# Dash 3.x
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Callable, Tuple, Union
from math import erf

# ===========================
# Defaults
# ===========================
MIN_R2_DEFAULT: float = 0.70
ALPHA_P_DEFAULT: float = 0.05
TOUCH_SPACING_DEFAULT: int = 3
USE_ATR_TOL_DEFAULT: bool = True
ATR_LEN_DEFAULT: int = 14

MIN_VISIBLE_BARS = 3
REQUIRE_POST_CREATION_TOUCH = False
TOL_PCT_FOR_INTERACTION = 0.001

# ===========================
# SIGNALS
# ===========================

@dataclass
class Signal:
    side: str               # "BUY" or "SELL"
    reason: str             # e.g., "support_break_confirmed"
    bar_index: int          # confirmation bar (t+1)
    price: float            # execution/reference price (here: close[t+1])
    meta: Dict[str, Any]

def _normal_cdf(x: float) -> float:
    return 0.5*(1.0 + erf(x/np.sqrt(2.0)))

def _rolling_true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df['Close'].shift(1)
    tr1 = (df['High'] - df['Low']).abs()
    tr2 = (df['High'] - prev_close).abs()
    tr3 = (df['Low']  - prev_close).abs()
    return pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

def atr(df: pd.DataFrame, n: int) -> pd.Series:
    return _rolling_true_range(df).rolling(n, min_periods=1).mean()

def fit_trendline(seg: pd.DataFrame, method: str = 'huber') -> tuple[float, float]:
    idx = np.arange(len(seg)).reshape(-1, 1)
    mids = ((seg['Open'] + seg['Close']) / 2.0).values
    if method == 'ols':
        model = LinearRegression().fit(idx, mids)
    elif method == 'huber':
        model = HuberRegressor().fit(idx, mids)
    elif method == 'ransac':
        try:
            model = RANSACRegressor(estimator=LinearRegression(), random_state=0).fit(idx, mids)
        except TypeError:
            model = RANSACRegressor(base_estimator=LinearRegression(), random_state=0).fit(idx, mids)
    else:
        raise ValueError(f"Unknown method: {method}")
    return float(model.coef_[0]), float(model.intercept_)

def slope_stats(seg: pd.DataFrame) -> Dict[str, float]:
    x = np.arange(len(seg)).astype(float)
    y = ((seg['Open'] + seg['Close'])/2.0).astype(float).values
    n = x.size
    if n < 3: return dict(r2=np.nan, p=np.nan, slope=np.nan, intercept=np.nan)
    xm, ym = x.mean(), y.mean()
    Sxx = ((x - xm)**2).sum()
    Sxy = ((x - xm)*(y - ym)).sum()
    if Sxx <= 0: return dict(r2=np.nan, p=np.nan, slope=np.nan, intercept=np.nan)
    slope = Sxy / Sxx
    intercept = ym - slope*xm
    yhat = intercept + slope * x
    ss_res = ((y - yhat)**2).sum()
    ss_tot = ((y - ym)**2).sum()
    r2 = 1.0 - (ss_res/ss_tot) if ss_tot>0 else 0.0
    se2 = (ss_res / (n - 2)) / Sxx if n > 2 else np.inf
    se = np.sqrt(se2) if se2>0 else np.inf
    t = slope / se if se>0 else np.inf
    p = 2.0 * (1.0 - _normal_cdf(abs(t)))
    return dict(r2=float(r2), p=float(p), slope=float(slope), intercept=float(intercept))

def compute_support_intercept(seg: pd.DataFrame, slope: float, intercept: float) -> float:
    i = np.arange(len(seg))
    baseline = slope * i + intercept
    shift_down = (seg['Low'].values - baseline).min()
    return intercept + float(shift_down)

def compute_resistance_intercept(seg: pd.DataFrame, slope: float, intercept: float) -> float:
    i = np.arange(len(seg))
    baseline = slope * i + intercept
    shift_up = (baseline - seg['High'].values).min()
    return intercept - float(shift_up)

def tol_at(line_price: float, tol_abs: Optional[float], tol_pct: Optional[float]) -> float:
    t = 0.0
    if tol_abs is not None: t = max(t, float(tol_abs))
    if tol_pct is not None: t = max(t, float(tol_pct) * abs(float(line_price)))
    return t

def _segment_has_interaction(df: pd.DataFrame, r: pd.Series, tol_pct: float = TOL_PCT_FOR_INTERACTION) -> bool:
    s, e = int(r["start"]), int(r["end"])
    if e < s: return False
    idx_rel = np.arange(e - s + 1)
    seg = df.iloc[s:e+1]
    tol = tol_at(float(seg["Close"].median()), None, tol_pct)
    y_sup = r["sup_int"] + r["slope_sup"] * idx_rel
    y_res = r["res_int"] + r["slope_res"] * idx_rel
    sup_hits = int((np.abs(seg["Low"].values  - y_sup) <= tol).sum())
    res_hits = int((np.abs(seg["High"].values - y_res) <= tol).sum())
    return (sup_hits + res_hits) > 0

def _is_visible_active_segment(df: pd.DataFrame, seg_dict: Dict[str, Any]) -> bool:
    s, e = int(seg_dict["start"]), int(seg_dict["end"])
    seg_len = e - s + 1
    long_enough = seg_len >= MIN_VISIBLE_BARS
    interacted = (not REQUIRE_POST_CREATION_TOUCH) or _segment_has_interaction(
        df, pd.Series(seg_dict), TOL_PCT_FOR_INTERACTION
    )
    result = bool(long_enough and interacted)

    # Debug print
    print(
        f"[VISIBLE_CHECK] start={s} end={e} len={seg_len} "
        f"sup_touches={seg_dict.get('sup_touches')} res_touches={seg_dict.get('res_touches')} "
        f"long_enough={long_enough} interacted={interacted} -> visible={result}"
    )

    return result


# ===========================
# Candidate scanner
# ===========================
def _validity_flags(track_support, track_resistance, sup_t, res_t, min_touches_support, min_touches_resistance, create_on: str) -> bool:
    a = True if not track_support    else (sup_t >= min_touches_support)
    b = True if not track_resistance else (res_t >= min_touches_resistance)
    if create_on == 'both': return a and b
    if create_on == 'support': return a
    if create_on == 'resistance': return b
    return a or b

def scan_candidates_regression(df: pd.DataFrame, end_idx: int,
                               base_window: int, max_window: int, step: int,
                               method: str, tol: float,
                               track_support: bool, track_resistance: bool,
                               min_touches_support: int, min_touches_resistance: int,
                               create_on: str, prefer: str = 'max',
                               min_slope_abs: float = 0.0, force_when_missing: bool = True,
                               min_r2: float = MIN_R2_DEFAULT, alpha_p: float = ALPHA_P_DEFAULT,
                               use_atr_tol: bool = USE_ATR_TOL_DEFAULT, touch_spacing: int = TOUCH_SPACING_DEFAULT,
                               atr_len: int = ATR_LEN_DEFAULT, atr_series: Optional[pd.Series] = None):
    best = None; best_score = -1
    max_W = min(max_window, end_idx + 1)
    for W in range(base_window, max_W + 1, step):
        s = end_idx - W + 1
        if s < 0: break
        seg = df.iloc[s:end_idx+1]
        slope, intercept = fit_trendline(seg, method)
        stats = slope_stats(seg)
        if abs(slope) < min_slope_abs: continue
        if not np.isfinite(stats["r2"]) or stats["r2"] < min_r2: continue
        if not np.isfinite(stats["p"]) or stats["p"] >= alpha_p: continue
        if use_atr_tol:
            tol_local = float(atr_series.iloc[s:end_idx+1].mean()) if atr_series is not None else float(atr(seg, atr_len).mean())
        else:
            tol_local = tol
        sup_int = compute_support_intercept(seg, slope, intercept) if track_support else np.nan
        res_int = compute_resistance_intercept(seg, slope, intercept) if track_resistance else np.nan
        # touch counts (spaced)
        i = np.arange(len(seg))
        sup_t = 0; res_t = 0
        if track_support and np.isfinite(sup_int):
            y = sup_int + slope * i
            hits = np.where(np.abs(seg['Low'].values - y) <= tol_local)[0]
            if hits.size:
                kept = [int(hits[0])]
                for j in hits[1:]:
                    if (j - kept[-1]) >= touch_spacing: kept.append(int(j))
                sup_t = len(kept)
        if track_resistance and np.isfinite(res_int):
            y = res_int + slope * i
            hits = np.where(np.abs(seg['High'].values - y) <= tol_local)[0]
            if hits.size:
                kept = [int(hits[0])]
                for j in hits[1:]:
                    if (j - kept[-1]) >= touch_spacing: kept.append(int(j))
                res_t = len(kept)
        valid = _validity_flags(track_support, track_resistance, sup_t, res_t,
                                min_touches_support, min_touches_resistance, create_on)
        cand = {'start': s, 'end': end_idx, 'window': W,
                'slope_sup': slope, 'slope_res': slope,
                'sup_int': sup_int, 'res_int': res_int,
                'sup_touches': sup_t, 'res_touches': res_t,
                'r2': float(stats["r2"]), 'p': float(stats["p"])}
        
        # --- attach pre-break line quality (no price info needed)
        try:
            q = compute_line_quality(cand, side_hint=None, req_touches=min_touches_support)
            cand["quality_score"] = q["quality_score"]
            cand["quality_label"] = q["quality_label"]
            cand["quality_components"] = q["quality_components"]
        except Exception:
            cand["quality_score"] = np.nan
            cand["quality_label"] = ""
            cand["quality_components"] = None

        score = sup_t + res_t
        if valid:
            if prefer == 'first': return cand
            if score > best_score: best, best_score = cand, score
        else:
            if force_when_missing and score > best_score: best, best_score = cand, score
    return best

# ===========================
# Stateful segments with recreate_mode + visible-only trading
# ===========================
def add_segment_angles(df: pd.DataFrame, segs: pd.DataFrame, atr_len: int = ATR_LEN_DEFAULT, atr_series: Optional[pd.Series]=None) -> pd.DataFrame:
    if segs is None or segs.empty:
        return segs
    segs = segs.copy()
    if atr_series is None:
        atr_series = atr(df, atr_len)
    cols = ["angle_sup_deg_raw","angle_res_deg_raw","angle_sup_deg_pct","angle_res_deg_pct",
            "angle_sup_deg_atr","angle_res_deg_atr","seg_median_px","seg_mean_atr","seg_atr_pct"]
    for c in cols:
        if c not in segs.columns:
            segs[c] = np.nan
    for i, r in segs.iterrows():
        s, e = int(r["start"]), int(r["end"])
        if e < s: continue
        px_med = float(df["Close"].iloc[s:e+1].median())
        atr_mean = float(atr_series.iloc[s:e+1].mean())
        sl_sup = float(r["slope_sup"]); sl_res = float(r["slope_res"])
        ang_sup_raw = np.degrees(np.arctan(sl_sup))
        ang_res_raw = np.degrees(np.arctan(sl_res))
        sl_sup_pct = sl_sup / max(px_med, 1e-12)
        sl_res_pct = sl_res / max(px_med, 1e-12)
        ang_sup_pct = np.degrees(np.arctan(sl_sup_pct))
        ang_res_pct = np.degrees(np.arctan(sl_res_pct))
        if atr_mean > 0:
            ang_sup_atr = np.degrees(np.arctan(sl_sup / atr_mean))
            ang_res_atr = np.degrees(np.arctan(sl_res / atr_mean))
        else:
            ang_sup_atr = ang_res_atr = np.nan
        segs.at[i, "angle_sup_deg_raw"] = ang_sup_raw
        segs.at[i, "angle_res_deg_raw"] = ang_res_raw
        segs.at[i, "angle_sup_deg_pct"] = ang_sup_pct
        segs.at[i, "angle_res_deg_pct"] = ang_res_pct
        segs.at[i, "angle_sup_deg_atr"] = ang_sup_atr
        segs.at[i, "angle_res_deg_atr"] = ang_res_atr
        segs.at[i, "seg_median_px"]     = px_med
        segs.at[i, "seg_mean_atr"]      = atr_mean
        segs.at[i, "seg_atr_pct"]       = (atr_mean / max(px_med, 1e-12)) if px_med > 0 else np.nan
    return segs

def classify_pattern_for_segment(seg_row: pd.Series) -> dict:
    sls = float(seg_row["slope_sup"]); slr = float(seg_row["slope_res"])
    s, e = int(seg_row["start"]), int(seg_row["end"]); L = max(1, e - s + 1)
    eps_flat, eps_parallel, min_slope = 0.02, 0.03, 0.05
    shrink_strong, short_len = 0.25, 20
    def gap_at(rel):
        return (seg_row["res_int"] + slr*rel) - (seg_row["sup_int"] + sls*rel)
    g0 = gap_at(0); g1 = gap_at(L-1)
    gap_shrink = (g0 - g1) / max(g0, 1e-9) if g0 > 0 else 0.0
    if abs(sls - slr) < 1e-12: t_apex = np.inf
    else: t_apex = (seg_row["res_int"] - seg_row["sup_int"]) / (sls - slr)
    flat_sup, flat_res = abs(sls) <= eps_flat, abs(slr) <= eps_flat
    up_sup, dn_sup = sls >=  min_slope, sls <= -min_slope
    up_res, dn_res = slr >=  min_slope, slr <= -min_slope
    parallel = abs(sls - slr) <= eps_parallel
    converging = (gap_shrink >= shrink_strong) and (t_apex > 0) and (t_apex < 3*L)
    if flat_sup and flat_res: kind = "Rectangle"
    elif up_sup and flat_res: kind = "Ascending Triangle"
    elif dn_sup and flat_res: kind = "Descending Triangle"
    elif (up_sup and dn_res and converging): kind = "Symmetrical Triangle"
    elif parallel and up_sup and up_res: kind = "Rising Wedge" if converging else "Rising Channel"
    elif parallel and dn_sup and dn_res: kind = "Falling Wedge" if converging else "Falling Channel"
    else:
        if L <= short_len and converging: kind = "Pennant"
        elif L <= short_len and parallel: kind = "Flag"
        else: kind = "Unclassified"
    touches = float(seg_row.get("sup_touches",0)) + float(seg_row.get("res_touches",0))
    slope_strength = max(abs(sls), abs(slr))
    conf = 0.4*(min(1.0, touches/4.0)) + 0.4*(min(1.0, max(0.0, gap_shrink))) + 0.2*(min(1.0, slope_strength/0.5))
    return {"pattern": kind, "confidence": round(float(conf), 2), "gap_shrink": round(float(gap_shrink), 3),
            "apex_bars_from_start": None if np.isinf(t_apex) else float(t_apex)}


# ========= strength & quality helpers =========

def _safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def compute_line_quality(
    seg_like: dict | pd.Series,
    side_hint: Optional[str] = None,  # "support" or "resistance"
    min_r2_for_full: float = 0.85,
    req_touches: int = 3,
    angle_cap_deg: float = 60.0,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Pre-break 'line quality' in [0..100] with label, using only R², p-value, touches, angle.
    """
    if weights is None:
        weights = {"r2": 0.40, "pval": 0.25, "touches": 0.20, "angle": 0.15}

    r2 = _safe_float(seg_like.get("r2", 0.0))
    p  = _safe_float(seg_like.get("p", 1.0))

    comp_r2 = min(1.0, max(0.0, r2 / max(1e-8, min_r2_for_full)))

    def p_to_score(pv):
        if pv <= 0.01: return 1.0
        if pv >= 0.20: return 0.0
        return max(0.0, (0.20 - pv) / (0.20 - 0.01))
    comp_p = p_to_score(p)

    touches = max(int(seg_like.get("sup_touches", 0) or 0),
                  int(seg_like.get("res_touches", 0) or 0))
    comp_touches = min(1.0, touches / max(1, req_touches))

    ang_sup = _safe_float(seg_like.get("angle_sup_deg_atr", seg_like.get("angle_sup_deg", float("nan"))), float("nan"))
    ang_res = _safe_float(seg_like.get("angle_res_deg_atr", seg_like.get("angle_res_deg", float("nan"))), float("nan"))
    if side_hint == "support":
        angle_use = ang_sup
    elif side_hint == "resistance":
        angle_use = ang_res
    else:
        cands = [x for x in [ang_sup, ang_res] if not np.isnan(x)]
        angle_use = max(cands, key=lambda v: abs(v)) if cands else float("nan")
    comp_angle = 0.0 if np.isnan(angle_use) else min(1.0, abs(angle_use) / angle_cap_deg)

    comps = {"r2": comp_r2, "pval": comp_p, "touches": comp_touches, "angle": comp_angle}
    total_w = sum(weights.values())
    score01 = sum((weights[k]/total_w)*v for k, v in comps.items())
    score = round(100.0 * score01, 1)
    label = "WEAK" if score < 40 else ("MEDIUM" if score < 70 else "STRONG")

    return {"quality_score": score, "quality_label": label, "quality_components": comps}

def compute_signal_strength(
    df: pd.DataFrame,
    seg_row: pd.Series,
    e: int,                       # confirm bar index
    side: str,                    # "BUY" or "SELL"
    tol_abs: Optional[float],
    tol_pct: Optional[float],
    atr_series: Optional[pd.Series] = None,
    min_r2_for_full: float = 0.85,
    req_touches: int = 3,
    angle_cap_deg: float = 60.0,
    weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Post-confirm signal strength in [0..100] + label.
    Combines breach/confirm margins (ATR-normalized) with quality factors.
    """
    if weights is None:
        weights = {"breach_depth": 0.25, "confirm_margin": 0.25, "r2": 0.15, "pval": 0.10, "touches": 0.10, "angle": 0.10, "volume": 0.05}

    start = int(seg_row["start"])
    t = e - 1
    if t < 0:
        return {"score_0_100": 0.0, "label": "WEAK", "components": {}, "explain": ["No prior bar for confirmation."]}

    sup_int = seg_row.get("sup_int", float("nan"))
    res_int = seg_row.get("res_int", float("nan"))
    slope_sup = seg_row.get("slope_sup", float("nan"))
    slope_res = seg_row.get("slope_res", float("nan"))

    def _atr_at(i: int) -> float:
        if atr_series is not None and i < len(atr_series) and pd.notna(atr_series.iloc[i]):
            return float(atr_series.iloc[i])
        return max(1e-8, float(df["High"].iloc[i]) - float(df["Low"].iloc[i]))

    def _tol_at(px: float) -> float:
        base = 0.0
        if tol_abs is not None: base = tol_abs
        if tol_pct: base = max(base, tol_pct * abs(px))
        return base

    def proj_support(i: int) -> float:
        if pd.isna(sup_int) or pd.isna(slope_sup): return float("nan")
        return float(sup_int + slope_sup * (i - start))

    def proj_resist(i: int) -> float:
        if pd.isna(res_int) or pd.isna(slope_res): return float("nan")
        return float(res_int + slope_res * (i - start))

    breach_depth = 0.0; confirm_margin = 0.0
    if side == "SELL":
        line_t, line_e1 = proj_support(t), proj_support(e)
        if not np.isnan(line_t) and not np.isnan(line_e1):
            atr_t, atr_e = _atr_at(t), _atr_at(e)
            tol_t, tol_e = _tol_at(line_t), _tol_at(line_e1)
            breach_raw  = (line_t - float(df["Close"].iloc[t]) - tol_t)
            confirm_raw = (line_e1 - float(df["High"].iloc[e]) - tol_e)
            breach_depth  = max(0.0, breach_raw  / max(1e-8, atr_t))
            confirm_margin = max(0.0, confirm_raw / max(1e-8, atr_e))
    else:  # BUY
        line_t, line_e1 = proj_resist(t), proj_resist(e)
        if not np.isnan(line_t) and not np.isnan(line_e1):
            atr_t, atr_e = _atr_at(t), _atr_at(e)
            tol_t, tol_e = _tol_at(line_t), _tol_at(line_e1)
            breach_raw  = (float(df["Close"].iloc[t]) - line_t - tol_t)
            confirm_raw = (float(df["Low"].iloc[e])  - line_e1 - tol_e)
            breach_depth  = max(0.0, breach_raw  / max(1e-8, atr_t))
            confirm_margin = max(0.0, confirm_raw / max(1e-8, atr_e))

    def squash(x, cap=3.0):  # cap 3 ATRs → 1.0
        return min(1.0, x / cap)

    comp_breach  = squash(breach_depth)
    comp_confirm = squash(confirm_margin)

    qual = compute_line_quality(seg_row)
    comp_r2      = qual["quality_components"]["r2"]
    comp_pval    = qual["quality_components"]["pval"]
    comp_touches = qual["quality_components"]["touches"]
    comp_angle   = qual["quality_components"]["angle"]

    comp_vol = 0.0
    if "Volume" in df.columns:
        w = 50
        start_i = max(0, e - w)
        ref = float(np.median(df["Volume"].iloc[start_i:e])) if e > start_i else float(df["Volume"].iloc[e])
        v_e = float(df["Volume"].iloc[e])
        comp_vol = min(1.0, (v_e / max(1e-8, ref)) - 0.5)

    comps = {"breach_depth": comp_breach, "confirm_margin": comp_confirm, "r2": comp_r2, "pval": comp_pval, "touches": comp_touches, "angle": comp_angle, "volume": comp_vol}
    total_w = sum(weights.values())
    score01 = sum((weights.get(k,0.0)/total_w)*v for k, v in comps.items() if k in weights)
    score = round(100.0 * score01, 1)
    label = "WEAK" if score < 40 else ("MEDIUM" if score < 70 else "STRONG")

    # put this helper near your other helpers
    def strength_to_confidence(score_0_100: float) -> float:
        s = max(0.0, min(100.0, float(score_0_100)))
        return round(s / 100.0, 3)
    confidence = strength_to_confidence(score)
    explain = [f"breach={comp_breach:.2f}", f"confirm={comp_confirm:.2f}", f"r2→{comp_r2:.2f}", f"p→{comp_pval:.2f}", f"touches→{comp_touches:.2f}", f"angle→{comp_angle:.2f}"]
    if "Volume" in df.columns: explain.append(f"volume→{comp_vol:.2f}")

    return {"score_0_100": score, "label": label,"confidence": confidence, "components": comps, "explain": explain}


# ========= MAIN: build_stateful_segments_confirming (complete, strength-integrated) =========
def build_stateful_segments_confirming(
    df: pd.DataFrame,
    base_window: int, max_window: int, step_window: int,
    method: str, track_support: bool, track_resistance: bool,
    tol_abs: Optional[float], tol_pct: Optional[float],
    min_touches_support: int, min_touches_resistance: int,
    create_on: str, start_new_at_next_bar: bool, prefer_candidate: str, min_slope_abs: float, force_when_missing: bool,
    min_r2: float, alpha_p: float, use_atr_tol: bool, touch_spacing: int, atr_len: int,
    max_active_len: Optional[int] = 140,
    recreate_mode: str = "both",
    atr_series: Optional[pd.Series] = None,
    # ---- NEW (optional) decay controls ----
    enable_decay: bool = False,
    decay_threshold: float = 0.20,
    half_life_bars: int = 80,
    touch_half_life: int = 20,
    dist_free_atr: float = 0.5,
    dist_penalty_k: float = 1.0,
) -> Tuple[pd.DataFrame, List[Signal]]:
    """
    Stateful trendline segmentation with 2-bar break confirmation.
    Now includes:
      - per-signal strength (score + label + confidence) stored on segment & Signal.meta
      - optional decay of active lines; reseed only after break/expiry/decay
      - segment fields: decay_score_support/decay_score_resist, quality carry-through
    """

    # --- small local helpers (self-contained) ---
    import math

    def _touched_line_bar(i: int, line_px: float, tol_px: float) -> bool:
        """True if bar i overlaps [line_px - tol_px, line_px + tol_px]."""
        if np.isnan(line_px) or np.isnan(tol_px): return False
        hi = float(df["High"].iloc[i]); lo = float(df["Low"].iloc[i])
        return (lo <= line_px + tol_px) and (hi >= line_px - tol_px)

    def _dist_atr(i: int, line_px: float) -> float:
        """Distance from price to line in ATRs (if atr_series is available), else 0."""
        if np.isnan(line_px): return 0.0
        if atr_series is not None and i < len(atr_series) and pd.notna(atr_series.iloc[i]):
            A = float(atr_series.iloc[i])
            if A <= 1e-8: return 0.0
            return abs(float(df["Close"].iloc[i]) - line_px) / A
        return 0.0

    def _compute_decay_score(
        age_bars: int, bars_since_touch: int, dist_atr_val: float,
        quality_floor: float = 0.7,
        half_life_bars_: int = 80, touch_half_life_: int = 20,
        dist_free_atr_: float = 0.5, dist_penalty_k_: float = 1.0
    ) -> float:
        """Combine time decay, freshness (touch), and distance penalty into [0..1]."""
        lam_age   = math.log(2)/max(1, half_life_bars_)
        lam_touch = math.log(2)/max(1, touch_half_life_)
        time_decay  = math.exp(-lam_age   * max(0, age_bars))
        touch_decay = math.exp(-lam_touch * max(0, bars_since_touch))
        excess = max(0.0, dist_atr_val - dist_free_atr_)
        dist_decay = 1.0/(1.0 + dist_penalty_k_ * excess)
        q = max(0.0, min(1.0, float(quality_floor)))
        return max(0.0, min(1.0, q * time_decay * touch_decay * dist_decay))

    # --- main body ---
    N = len(df)
    if N < base_window:
        return pd.DataFrame(), []

    HAS_SIGNAL_FLAG = "_has_signal"
    coarse_tol = 0.0 if tol_abs is None and not tol_pct else tol_at(float(df["Close"].median()), tol_abs, tol_pct)

    segments: List[Dict[str, Any]] = []
    active: Optional[Dict[str, Any]] = None
    pending: Optional[Dict[str, Any]] = None
    signals: List[Signal] = []

    # dynamic tracking flags (may be narrowed after break based on recreate_mode)
    track_sup_cur = bool(track_support)
    track_res_cur = bool(track_resistance)

    def reseed(e_idx: int):
        nonlocal active
        cand = scan_candidates_regression(
            df, e_idx, base_window, max_window, step_window, method, coarse_tol,
            track_sup_cur, track_res_cur,
            min_touches_support, min_touches_resistance,
            create_on, prefer_candidate, min_slope_abs, force_when_missing,
            min_r2, alpha_p, use_atr_tol, touch_spacing, atr_len, atr_series=atr_series
        )
        if cand:
            new_start = e_idx + 1 if start_new_at_next_bar else e_idx
            delta = new_start - cand["start"]

            sup_i_new = cand["sup_int"] + cand["slope_sup"] * delta if track_sup_cur else np.nan
            res_i_new = cand["res_int"] + cand["slope_res"] * delta if track_res_cur else np.nan

            row = {
                "start": new_start, "end": e_idx,
                "slope_sup": cand["slope_sup"], "slope_res": cand["slope_res"],
                "sup_int": sup_i_new, "res_int": res_i_new,
                "break_at": np.nan, "break_kind": "",
                "sup_touches": cand["sup_touches"], "res_touches": cand["res_touches"],
                "window_used": cand["window"], "r2": cand["r2"], "p": cand["p"],
                HAS_SIGNAL_FLAG: False,
                # strength (post-break) defaults
                "signal_strength": np.nan, "signal_strength_label": "", "signal_confidence": np.nan,
                "signal_strength_components": None,
                # decay visibility
                "decay_score_support": np.nan, "decay_score_resist": np.nan,
                # carry candidate quality (pre-break, if scan attached it)
                "quality_score": cand.get("quality_score", np.nan),
                "quality_label": cand.get("quality_label", ""),
                "quality_components": cand.get("quality_components", None),
            }
            segments.append(row)
            active = {
                "start": new_start,
                "slope_sup": cand["slope_sup"], "sup_int": sup_i_new,
                "slope_res": cand["slope_res"], "res_int": res_i_new,
                # decay state
                "last_touch_sup": new_start,
                "last_touch_res": new_start,
            }
        else:
            active = None

    for e in range(base_window - 1, N):
        if active is None:
            reseed(e)
            continue

        # extend current segment to e
        segments[-1]["end"] = e

        # hard expiry by length
        if max_active_len is not None:
            cur_len = e - int(active["start"]) + 1
            if cur_len >= max_active_len:
                segments[-1]["break_at"] = np.nan
                segments[-1]["break_kind"] = "expired"
                # reset which sides we track, then reseed
                track_sup_cur = bool(track_support); track_res_cur = bool(track_resistance)
                pending = None; reseed(e); continue

        # projections at e
        proj_sup_e = (active["sup_int"] + active["slope_sup"] * (e - active["start"])
                      if not np.isnan(active["sup_int"]) else np.nan)
        proj_res_e = (active["res_int"] + active["slope_res"] * (e - active["start"])
                      if not np.isnan(active["res_int"]) else np.nan)

        # --- optional decay logic (no instant reseed; reseed only after we retire by decay) ---
        if enable_decay:
            tol_sup_e = tol_at(proj_sup_e, tol_abs, tol_pct) if not np.isnan(proj_sup_e) else np.nan
            tol_res_e = tol_at(proj_res_e, tol_abs, tol_pct) if not np.isnan(proj_res_e) else np.nan

            if track_sup_cur and not np.isnan(proj_sup_e) and _touched_line_bar(e, proj_sup_e, tol_sup_e):
                active["last_touch_sup"] = e
            if track_res_cur and not np.isnan(proj_res_e) and _touched_line_bar(e, proj_res_e, tol_res_e):
                active["last_touch_res"] = e

            age = e - int(active["start"]) + 1
            q_floor = float(np.clip(segments[-1].get("r2", 0.7), 0.0, 1.0))

            d_sup = (_compute_decay_score(
                age_bars=age,
                bars_since_touch=e - int(active.get("last_touch_sup", segments[-1]["start"])),
                dist_atr_val=_dist_atr(e, proj_sup_e),
                quality_floor=q_floor,
                half_life_bars_=half_life_bars, touch_half_life_=touch_half_life,
                dist_free_atr_=dist_free_atr, dist_penalty_k_=dist_penalty_k
            ) if not np.isnan(proj_sup_e) and track_sup_cur else np.nan)

            d_res = (_compute_decay_score(
                age_bars=age,
                bars_since_touch=e - int(active.get("last_touch_res", segments[-1]["start"])),
                dist_atr_val=_dist_atr(e, proj_res_e),
                quality_floor=q_floor,
                half_life_bars_=half_life_bars, touch_half_life_=touch_half_life,
                dist_free_atr_=dist_free_atr, dist_penalty_k_=dist_penalty_k
            ) if not np.isnan(proj_res_e) and track_res_cur else np.nan)

            segments[-1]["decay_score_support"] = d_sup
            segments[-1]["decay_score_resist"]  = d_res

            # retirement by decay: if tracking both, require BOTH to be weak; if one side only, use that side's score
            cond_sup = track_sup_cur and not np.isnan(d_sup) and d_sup < decay_threshold
            cond_res = track_res_cur and not np.isnan(d_res) and d_res < decay_threshold
            expire_now = False
            if track_sup_cur and track_res_cur:
                expire_now = cond_sup and cond_res
            elif track_sup_cur:
                expire_now = cond_sup
            elif track_res_cur:
                expire_now = cond_res

            if expire_now:
                segments[-1]["break_at"] = np.nan
                segments[-1]["break_kind"] = "decayed"
                track_sup_cur = bool(track_support); track_res_cur = bool(track_resistance)
                pending = None; reseed(e); continue

        # --- first-touch (set pending) ---
        if pending is None:
            if track_sup_cur and not np.isnan(proj_sup_e):
                tol_e_sup = tol_at(proj_sup_e, tol_abs, tol_pct)
                if float(df["Close"].iloc[e]) < (proj_sup_e - tol_e_sup):
                    pending = {"type": "support", "t": e}
                    continue
            if track_res_cur and not np.isnan(proj_res_e):
                tol_e_res = tol_at(proj_res_e, tol_abs, tol_pct)
                if float(df["Close"].iloc[e]) > (proj_res_e + tol_e_res):
                    pending = {"type": "resistance", "t": e}
                    continue

        if pending is None:
            continue

        t = int(pending["t"])

        # --- support break confirm branch ---
        if (pending["type"] == "support"
            and track_sup_cur
            and not np.isnan(active["sup_int"])
            and not np.isnan(segments[-1].get("slope_sup", np.nan))):

            sup_t  = active["sup_int"] + active["slope_sup"] * (t   - active["start"])
            sup_t1 = active["sup_int"] + active["slope_sup"] * (t+1 - active["start"])
            tol_t  = tol_at(sup_t,  tol_abs, tol_pct)
            tol_t1 = tol_at(sup_t1, tol_abs, tol_pct)

            cond = (float(df["Close"].iloc[t]) < (sup_t - tol_t)) and (float(df["High"].iloc[e]) < (sup_t1 - tol_t1))
            if cond:
                segments[-1]["break_at"]   = e
                segments[-1]["break_kind"] = "support"
                segments[-1]["end"]        = e

                visible_ok = _is_visible_active_segment(df, segments[-1])
                if visible_ok:
                    tmp_df = pd.DataFrame([segments[-1]])
                    tmp_df = add_segment_angles(df, tmp_df, atr_len=atr_len, atr_series=atr_series)
                    pat = classify_pattern_for_segment(tmp_df.iloc[0])

                    strength = compute_signal_strength(
                        df=df, seg_row=tmp_df.iloc[0], e=e, side="SELL",
                        tol_abs=tol_abs, tol_pct=tol_pct, atr_series=atr_series,
                        req_touches=min(min_touches_support, min_touches_resistance)
                    )
                    segments[-1]["signal_strength"] = strength["score_0_100"]
                    segments[-1]["signal_strength_label"] = strength["label"]
                    segments[-1]["signal_confidence"] = strength.get("confidence", strength.get("score_0_100", 0.0)/100.0)
                    segments[-1]["signal_strength_components"] = strength["components"]

                    signals.append(Signal(
                        side="SELL", reason="support_break_confirmed", bar_index=e, price=float(df["Close"].iloc[e]),
                        meta={
                            "pattern": pat["pattern"], "pattern_conf": pat["confidence"], "gap_shrink": pat["gap_shrink"],
                            "apex_bars_from_start": pat["apex_bars_from_start"],
                            "angle_sup_deg_atr": float(tmp_df.iloc[0]["angle_sup_deg_atr"]),
                            "angle_res_deg_atr": float(tmp_df.iloc[0]["angle_res_deg_atr"]),
                            "sup_touches": int(segments[-1]["sup_touches"]), "res_touches": int(segments[-1]["res_touches"]),
                            "window_used": int(segments[-1]["window_used"]), "r2": float(segments[-1]["r2"]), "p": float(segments[-1]["p"]),
                            "strength_score": strength["score_0_100"], "strength_label": strength["label"],
                            "signal_confidence": strength.get("confidence", strength.get("score_0_100", 0.0)/100.0),
                            "strength_components": strength["components"], "strength_explain": strength["explain"],
                        }
                    ))
                    segments[-1][HAS_SIGNAL_FLAG] = True

                # recreate mode selection
                if recreate_mode == "same-side":
                    track_sup_cur, track_res_cur = True, False
                else:
                    track_sup_cur, track_res_cur = bool(track_support), bool(track_resistance)
                pending = None; reseed(e)
            else:
                pending = None

        # --- resistance break confirm branch ---
        elif (pending["type"] == "resistance"
              and track_res_cur
              and not np.isnan(active["res_int"])
              and not np.isnan(segments[-1].get("slope_res", np.nan))):

            res_t  = active["res_int"] + active["slope_res"] * (t   - active["start"])
            res_t1 = active["res_int"] + active["slope_res"] * (t+1 - active["start"])
            tol_t  = tol_at(res_t,  tol_abs, tol_pct)
            tol_t1 = tol_at(res_t1, tol_abs, tol_pct)

            cond = (float(df["Close"].iloc[t]) > (res_t + tol_t)) and (float(df["Low"].iloc[e]) > (res_t1 + tol_t1))
            if cond:
                segments[-1]["break_at"]   = e
                segments[-1]["break_kind"] = "resistance"
                segments[-1]["end"]        = e

                visible_ok = _is_visible_active_segment(df, segments[-1])
                if visible_ok:
                    tmp_df = pd.DataFrame([segments[-1]])
                    tmp_df = add_segment_angles(df, tmp_df, atr_len=atr_len, atr_series=atr_series)
                    pat = classify_pattern_for_segment(tmp_df.iloc[0])

                    strength = compute_signal_strength(
                        df=df, seg_row=tmp_df.iloc[0], e=e, side="BUY",
                        tol_abs=tol_abs, tol_pct=tol_pct, atr_series=atr_series,
                        req_touches=min(min_touches_support, min_touches_resistance)
                    )
                    segments[-1]["signal_strength"] = strength["score_0_100"]
                    segments[-1]["signal_strength_label"] = strength["label"]
                    segments[-1]["signal_confidence"] = strength["confidence"]
                    segments[-1]["signal_strength_components"] = strength["components"]

                    signals.append(Signal(
                        side="BUY", reason="resistance_break_confirmed", bar_index=e, price=float(df["Close"].iloc[e]),
                        meta={
                            "pattern": pat["pattern"], "pattern_conf": pat["confidence"], "gap_shrink": pat["gap_shrink"],
                            "apex_bars_from_start": pat["apex_bars_from_start"],
                            "angle_sup_deg_atr": float(tmp_df.iloc[0]["angle_sup_deg_atr"]),
                            "angle_res_deg_atr": float(tmp_df.iloc[0]["angle_res_deg_atr"]),
                            "sup_touches": int(segments[-1]["sup_touches"]), "res_touches": int(segments[-1]["res_touches"]),
                            "window_used": int(segments[-1]["window_used"]), "r2": float(segments[-1]["r2"]), "p": float(segments[-1]["p"]),
                            "strength_score": strength["score_0_100"], "strength_label": strength["label"],
                            "signal_confidence": strength["confidence"],
                            "strength_components": strength["components"], "strength_explain": strength["explain"],
                        }
                    ))
                    segments[-1][HAS_SIGNAL_FLAG] = True

                if recreate_mode == "same-side":
                    track_sup_cur, track_res_cur = False, True
                else:
                    track_sup_cur, track_res_cur = bool(track_support), bool(track_resistance)
                pending = None; reseed(e)
            else:
                pending = None

    # --- finalize & prune (always keep rows that produced a signal) ---
    segs = pd.DataFrame(segments)
    if not segs.empty:
        keep_mask = []
        for _, r in segs.iterrows():
            s_i, e_i = int(r["start"]), int(r["end"])
            long_enough = ((e_i - s_i + 1) >= MIN_VISIBLE_BARS)
            interacted = (not REQUIRE_POST_CREATION_TOUCH) or _segment_has_interaction(df, r, TOL_PCT_FOR_INTERACTION)
            keep = bool(r.get(HAS_SIGNAL_FLAG, False)) or (long_enough and interacted)
            keep_mask.append(keep)
        segs = segs.loc[keep_mask].reset_index(drop=True)

    segs = add_segment_angles(df, segs, atr_len=atr_len, atr_series=atr_series)
    return segs, signals


def with_timestamps(df: pd.DataFrame, segs: pd.DataFrame) -> pd.DataFrame:
    segs = segs.copy()
    if segs.empty: return segs
    segs["start_ts"] = df.index.take(segs["start"].astype(int))
    segs["end_ts"]   = df.index.take(segs["end"].astype(int))
    segs["break_ts"] = pd.NaT
    m_break = segs["break_at"].notna()
    segs.loc[m_break, "break_ts"] = df.index.take(segs.loc[m_break, "break_at"].astype(int))
    return segs

def process_signals_simple(df_slice: pd.DataFrame,
                           signals: list,
                           state: dict) -> dict:
    """
    Minimal trade sink:
      - If flat, open on first new signal.
      - If in a position, close on opposite-side signal.
      - Writes rows to state['trades'] for the Datatable.
    """
    # unpack state
    pos = int(state.get("position", 0))         # -1 short, 0 flat, +1 long
    entry = state.get("entry_price", None)
    realized = float(state.get("realized", 0.0))
    last_sig_idx = int(state.get("last_signal_idx", -1))
    trades = list(state.get("trades", []))

    # sort and filter new signals by bar_index > last_sig_idx
    new_sigs = [s for s in sorted(signals, key=lambda s: s.bar_index)
                if int(s.bar_index) > last_sig_idx]

    def add_row(i, action, price, pos_after, pnl_trade):
        ts = df_slice.index[i]
        trades.append({
            "time": str(ts),
            "action": action,
            "price": (None if price is None else float(price)),
            "pos_after": pos_after,
            "pnl_trade": (None if pnl_trade is None else float(pnl_trade)),
            "realized": float(realized)
        })

    for s in new_sigs:
        i = int(s.bar_index)
        px = float(s.price)
        side = 1 if s.side == "BUY" else -1

        # if flat -> open
        if pos == 0:
            pos = side
            entry = px
            pat = s.meta.get("pattern", "")
            add_row(i, f"{s.side} (open {'long' if side==1 else 'short'}) [{pat}]", px, pos, 0.0)
            last_sig_idx = i
            continue

        # if already in position -> close on opposite signal
        if pos != 0 and side == -pos:
            if pos == 1:
                # closing long
                pnl = px - float(entry)
                realized += pnl
                add_row(i, f"EXIT long (opp {s.side})", px, 0, pnl)
            else:
                # closing short
                pnl = float(entry) - px
                realized += pnl
                add_row(i, f"EXIT short (opp {s.side})", px, 0, pnl)
            pos = 0
            entry = None
            last_sig_idx = i
            # (optional) immediately open in new direction; comment out if you prefer not to flip the same bar
            pos = side
            entry = px
            pat = s.meta.get("pattern", "")
            add_row(i, f"{s.side} (open {'long' if side==1 else 'short'}) [{pat}]", px, pos, 0.0)
            last_sig_idx = i

    # write back
    state.update({
        "position": pos,
        "entry_price": entry,
        "realized": float(realized),
        "last_signal_idx": last_sig_idx,
        "trades": trades
    })
    return state

# ===========================
# Higher-frame (fixed window)
# ===========================
def build_higher_frame(df_: pd.DataFrame, higher_window: int, max_active_len_hi: int,
                       method: str, min_r2: float, alpha_p: float, touch_spacing: int,
                       use_atr_tol: bool, atr_len: int, atr_series: Optional[pd.Series]) -> pd.DataFrame:
    segs_hi, _ = build_stateful_segments_confirming(
        df_, higher_window, higher_window, 1, method, True, True,
        None, None, 2, 2, 'either', False, 'max', 0.0, True,
        min_r2, alpha_p, use_atr_tol, touch_spacing, atr_len, max_active_len_hi,
        recreate_mode="both", atr_series=atr_series
    )
    return segs_hi

# ===========================
# plotting
# ===========================
def plot_segments_plotly(df, segs, signals, mark_mode='candle', color_scheme='by_side',
                         support_color='green', resistance_color='red',
                         active_color='#00BCD4', broken_color='#FF9800', expired_color='#9E9E9E',
                         active_dash='solid', broken_dash='dash', expired_dash='dot',
                         active_width=2.2, other_width=1.6, show_rangeslider=True, title=None,
                         uirevision_key="keep"):
    if segs is None:
        segs = pd.DataFrame()
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='OHLC', increasing_line_color='#26a69a', decreasing_line_color='#ef5350', showlegend=False
    )])
    last_bar = len(df) - 1
    def state_for_row(r, is_last_row: bool) -> str:
        if r.get('break_kind', '') == 'expired': return 'expired'
        broke = not np.isnan(r.get('break_at', np.nan)) and (r.get('break_kind', '') in ('support','resistance'))
        if broke: return 'broken'
        if is_last_row and int(r['end']) == last_bar: return 'active'
        return 'broken'
    added_legends = set()
    if not segs.empty:
        for i, (_, r) in enumerate(segs.iterrows()):
            s, e = int(r['start']), int(r['end'])
            if e < s: continue
            W = e - s + 1
            x0, x1 = df.index[s], df.index[e]
            state = state_for_row(r, is_last_row=(i == len(segs)-1))
            dash = active_dash if state=='active' else (expired_dash if state=='expired' else broken_dash)
            width = active_width if state=='active' else other_width
            if color_scheme == 'by_state':
                c = {'active': active_color, 'broken': broken_color, 'expired': expired_color}[state]
                c_sup = c_res = c; sup_name = res_name = f"{state.capitalize()} line"
            else:
                c_sup, c_res = support_color, resistance_color
                sup_name, res_name = "Support", "Resistance"
            y0_sup = r['sup_int']; y1_sup = r['sup_int'] + r['slope_sup'] * (W - 1)
            y0_res = r['res_int']; y1_res = r['res_int'] + r['slope_res'] * (W - 1)
            fig.add_trace(go.Scatter(x=[x0, x1], y=[y0_sup, y1_sup], mode='lines',
                                     line=dict(color=c_sup, width=width, dash=dash),
                                     name=sup_name, showlegend=(sup_name not in added_legends)))
            added_legends.add(sup_name)
            fig.add_trace(go.Scatter(x=[x0, x1], y=[y0_res, y1_res], mode='lines',
                                     line=dict(color=c_res, width=width, dash=dash),
                                     name=res_name, showlegend=(res_name not in added_legends)))
            added_legends.add(res_name)
            if not pd.isna(r.get("break_at", np.nan)) and r.get("break_kind","") in ("support","resistance"):
                bi = int(r["break_at"]); rel = bi - s; ts = df.index[bi]
                if r["break_kind"]=="support":
                    line_y = r["sup_int"] + r["slope_sup"] * rel
                    fig.add_trace(go.Scatter(x=[ts], y=[line_y], mode="markers",
                                             marker=dict(symbol='triangle-down', size=12),
                                             name=f"Support break", showlegend=False))
                if r["break_kind"]=="resistance":
                    line_y = r["res_int"] + r["slope_res"] * rel
                    fig.add_trace(go.Scatter(x=[ts], y=[line_y], mode="markers",
                                             marker=dict(symbol='triangle-up', size=12),
                                             name=f"Resistance break", showlegend=False))
    for s in signals:
        ts = df.index[s.bar_index]
        label = 'Support break' if s.side == "SELL" else 'Resistance break'
        y = (df['Low'].iloc[s.bar_index] if s.side=="SELL" else df['High'].iloc[s.bar_index]) if mark_mode=='candle' else s.price
        fig.add_trace(go.Scatter(x=[ts], y=[y], mode='markers',
                                 marker=dict(symbol='triangle-down' if s.side=="SELL" else 'triangle-up', size=12, line=dict(width=0)),
                                 name=label, showlegend=False))
    fig.update_layout(title=title or "S/R Trendlines",
                      xaxis_title='Date', yaxis_title='Price',
                      xaxis=dict(rangeslider=dict(visible=show_rangeslider)),
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
                      template='plotly_white', hovermode='x unified',
                      uirevision=uirevision_key)
    return fig

def overlay_higher(fig, df, segs_hi, higher_window: int):
    added = set(t.name for t in fig.data)
    for _, r in (segs_hi if not segs_hi.empty else pd.DataFrame([])).iterrows():
        s, e = int(r["start"]), int(r["end"])
        idx = df.index[s:e+1]; rel = np.arange(e - s + 1)
        y_sup = r["sup_int"] + r["slope_sup"]*rel
        y_res = r["res_int"] + r["slope_res"]*rel
        sup_name = f"High({higher_window}) Support"
        res_name = f"High({higher_window}) Resistance"
        if sup_name not in added:
            fig.add_trace(go.Scatter(x=idx, y=y_sup, mode='lines', name=sup_name,
                                     line=dict(color='purple', width=2.4, dash='solid'))); added.add(sup_name)
        else:
            fig.add_trace(go.Scatter(x=idx, y=y_sup, mode='lines', name=sup_name,
                                     line=dict(color='purple', width=2.4, dash='solid'), showlegend=False))
        if res_name not in added:
            fig.add_trace(go.Scatter(x=idx, y=y_res, mode='lines', name=res_name,
                                     line=dict(color='orange', width=2.4, dash='solid'))); added.add(res_name)
        else:
            fig.add_trace(go.Scatter(x=idx, y=y_res, mode='lines', name=res_name,
                                     line=dict(color='orange', width=2.4, dash='solid'), showlegend=False))
    return fig

# ===========================
# App wiring
# ===========================

def fetch_and_prepare_zerodha(root_dir: str, from_date: str, to_date: str, instrument_token: str) -> pd.DataFrame:
    from tradingbot.trading_api.brokers.zerodha import ZerodhaAPI
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

def load_csv(path: str, ts_col: str = None) -> pd.DataFrame:
    df = pd.read_csv(path)
    if ts_col is None:
        for cand in ['timestamp','date','Datetime','datetime','Date']:
            if cand in df.columns:
                ts_col = cand; break
    if ts_col is None:
        raise ValueError("Please provide ts_col or include a timestamp/date column in CSV.")
    df[ts_col] = pd.to_datetime(df[ts_col])
    df = df.rename(columns={
        'open':'Open','high':'High','low':'Low','close':'Close',
        'OPEN':'Open','HIGH':'High','LOW':'Low','CLOSE':'Close'
    })
    need = ['Open','High','Low','Close']
    if not set(need).issubset(df.columns):
        raise ValueError("CSV missing Open/High/Low/Close columns.")
    df = df.set_index(ts_col).sort_index()
    return df[need]

def make_dummy_ohlc(n=400, start='2024-01-01', freq='B', seed=42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start=start, periods=n, freq=freq)
    steps = rng.normal(loc=0.0, scale=1.0, size=n).cumsum()
    close = 100 + steps
    open_ = np.empty(n)
    open_[0] = close[0] + rng.normal(0, 0.3)
    for i in range(1, n):
        open_[i] = close[i-1] + rng.normal(0, 0.3)
    spread_up = np.abs(rng.normal(0.6, 0.2, size=n))
    spread_dn = np.abs(rng.normal(0.6, 0.2, size=n))
    high = np.maximum(open_, close) + spread_up
    low  = np.minimum(open_, close) - spread_dn
    df = pd.DataFrame({'Open': open_, 'High': high, 'Low': low, 'Close': close}, index=idx)
    return df

if __name__ == "__main__":
    ROOT = os.environ.get("ZERODHA_ROOT", "/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot")
    FROM = os.environ.get("ZERODHA_FROM", "2022-11-01")
    TO   = os.environ.get("ZERODHA_TO",   "2024-01-10")

    DF_FULL = fetch_and_prepare_zerodha(ROOT, FROM,TO, '408065')
    print(f"Dataframe length {len(DF_FULL)}")
    assert set(['Open','High','Low','Close']).issubset(DF_FULL.columns)

    app = Dash(__name__)

    app.layout = html.Div([
        html.H3("S/R Trendlines – v02.1 (v03 fixes folded into v02)"),
        html.Div([
            dcc.Checklist(id='live-mode', options=[{'label':' Live streaming','value':'on'}], value=[],
                        style={"display":"inline-block","marginRight":"16px"}),
            dcc.Checklist(id='loop', options=[{'label':' Loop playback','value':'on'}], value=[],
                        style={"display":"inline-block","marginRight":"16px"}),
            html.Label("Show last N bars:"),
            dcc.Input(id='last-n', type='number', value=1000, min=50, step=10, style={"width":"100px","marginRight":"16px"}),
            html.Label("Reveal step (bars):"),
            dcc.Input(id='step-bars', type='number', value=5, min=1, step=1, style={"width":"80px","marginRight":"16px"}),
            html.Label("Refresh (ms):"),
            dcc.Input(id='refresh-ms', type='number', value=1500, min=100, step=100, style={"width":"100px"}),
        ], style={"marginBottom":"8px"}),

        html.Div([
            html.Label("Method:"), dcc.Dropdown(id='method', value='huber', options=[
                {'label':'Huber','value':'huber'}, {'label':'OLS','value':'ols'}, {'label':'RANSAC','value':'ransac'}
            ], style={"width":"140px","marginRight":"12px","display":"inline-block"}),
            html.Div([html.Label("MIN R²:"), dcc.Slider(id='min-r2', min=0.0, max=0.99, step=0.01, value=MIN_R2_DEFAULT,
                                            tooltip={"placement":"bottom"})], style={"display":"inline-block","width":"260px","marginRight":"12px","verticalAlign":"top"}),
            html.Div([html.Label("α (p-value):"), dcc.Slider(id='alpha-p', min=0.0, max=0.2, step=0.005, value=ALPHA_P_DEFAULT,
                                                tooltip={"placement":"bottom"})], style={"display":"inline-block","width":"260px","marginRight":"12px","verticalAlign":"top"}),
            html.Div([html.Label("Touch spacing:"), dcc.Slider(id='touch-spacing', min=1, max=10, step=1, value=TOUCH_SPACING_DEFAULT,
                                                    tooltip={"placement":"bottom"})], style={"display":"inline-block","width":"240px","verticalAlign":"top"}),
        ], style={"marginBottom":"8px"}),

        html.Div([
            dcc.Checklist(id='use-atr-tol', options=[{'label':' ATR-based touch tolerance','value':'on'}],
                        value=['on'] if USE_ATR_TOL_DEFAULT else [], style={"display":"inline-block","marginRight":"16px"}),
            html.Label("ATR len:"), dcc.Input(id='atr-len', type='number', value=ATR_LEN_DEFAULT, min=5, step=1,
                                            style={"width":"80px","marginRight":"16px"}),
            html.Label("Min touches S/R:"),
            dcc.Input(id='min-touch-s', type='number', value=2, min=1, step=1, style={"width":"60px","marginRight":"8px"}),
            dcc.Input(id='min-touch-r', type='number', value=2, min=1, step=1, style={"width":"60px"}),
        ], style={"marginBottom":"8px"}),

        html.Div([
            html.Label("Create on:"), dcc.Dropdown(id='create-on', value='either', options=[
                {'label':'Either','value':'either'},{'label':'Both','value':'both'},
                {'label':'Support only','value':'support'},{'label':'Resistance only','value':'resistance'}
            ], style={"width":"160px","display":"inline-block","marginRight":"12px"}),
            html.Label("Prefer:"), dcc.Dropdown(id='prefer', value='max', options=[
                {'label':'Max touches','value':'max'},{'label':'First valid','value':'first'}
            ], style={"width":"160px","display":"inline-block","marginRight":"12px"}),
            html.Label("Min slope |Δ|:"),
            html.Div([dcc.Slider(id='min-slope', min=0.0, max=1.0, step=0.01, value=0.0, tooltip={"placement":"bottom"})], style={"display":"inline-block","width":"260px","marginRight":"12px"}),
            html.Label("Windows (base/max/step):"),
            dcc.Input(id='base-w', type='number', value=60, min=5, step=1, style={"width":"70px","marginRight":"6px"}),
            dcc.Input(id='max-w', type='number', value=80, min=10, step=1, style={"width":"70px","marginRight":"6px"}),
            dcc.Input(id='step-w', type='number', value=5, min=1, step=1, style={"width":"70px"}),
        ], style={"marginBottom":"8px"}),

        html.Div([
            html.Label("Max active length:"),
            dcc.Input(id='max-active-len', type='number', value=140, min=20, step=5, style={"width":"110px","marginRight":"16px"}),
            html.Label("Plot scheme:"),
            dcc.Dropdown(id='plot-scheme', value='by_side', options=[
                {'label':'By line type','value':'by_side'},{'label':'By state','value':'by_state'}
            ], style={"width":"160px","display":"inline-block","marginRight":"16px"}),
            dcc.Checklist(id='show-rangeslider', options=[{'label':' Show rangeslider','value':'on'}], value=['on'],
                        style={"display":"inline-block"}),
        ], style={"marginBottom":"8px"}),

        html.Div([
            html.Label("Recreate mode:"),
            dcc.Dropdown(id='recreate-mode', value='both', options=[
                {'label':'Both S & R','value':'both'},
                {'label':'Same-side only','value':'same-side'}
            ], style={"width":"200px","display":"inline-block","marginLeft":"12px"}),
            dcc.Checklist(id='show-higher', options=[{'label':' Show higher-frame','value':'on'}], value=['on'],
                        style={"display":"inline-block","marginLeft":"16px"}),
            html.Label("Higher window:"),
            dcc.Input(id='higher-window', type='number', value=180, min=60, step=10, style={"width":"100px","marginLeft":"8px","marginRight":"12px"}),
            html.Label("Higher max-active:"),
            dcc.Input(id='higher-max-active', type='number', value=250, min=60, step=10, style={"width":"110px"}),
            html.Label("Recent segs (live):"),
            dcc.Input(id='recent-segs', type='number', value=18, min=6, step=2, style={"width":"80px","marginLeft":"12px"}),
        ], style={"marginBottom":"8px"}),

        html.Div([
            html.Label("Trailing: target_mult"),
            dcc.Input(id='trg-mult', type='number', value=1.0, step=0.1, style={"width":"80px","marginRight":"12px"}),
            html.Label("tick_size"),
            dcc.Input(id='tick-size', type='number', value=0.5, step=0.05, style={"width":"80px","marginRight":"12px"}),
            html.Label("min_R_ticks"),
            dcc.Input(id='min-R-ticks', type='number', value=3, step=1, style={"width":"80px","marginRight":"12px"}),
            html.Label("min_stop_nudge_ticks"),
            dcc.Input(id='min-stop-nudge', type='number', value=1, step=1, style={"width":"120px","marginRight":"12px"}),
            dcc.Checklist(id='intrabar-stop', options=[{'label':' Intrabar stop','value':'on'}], value=['on'],
                        style={"display":"inline-block","marginRight":"12px"}),
            dcc.Checklist(id='close-target', options=[{'label':' Close-based target','value':'on'}], value=['on'],
                        style={"display":"inline-block"}),
        ], style={"marginBottom":"8px"}),

        html.Div(id='status', style={'margin':'6px 0'}),
        dcc.Graph(id='sr-chart', style={'height': '60vh'}),

        html.H4("Executed Trades"),
        dash_table.DataTable(
            id="trades-table",
            columns=[
                {"name": "Time", "id": "time"},
                {"name": "Action", "id": "action"},
                {"name": "Price", "id": "price", "type": "numeric", "format": {"specifier": ".2f"}},
                {"name": "Position After", "id": "pos_after"},
                {"name": "PnL (trade)", "id": "pnl_trade", "type": "numeric", "format": {"specifier": ".2f"}},
                {"name": "Realized PnL", "id": "realized", "type": "numeric", "format": {"specifier": ".2f"}},
            ],
            data=[],
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"fontFamily": "Courier New, monospace", "fontSize": "12px"},
        ),

        html.H4("Segments (angles, slopes, pattern, stats)"),
        dash_table.DataTable(
            id="segments-table",
            columns=[
                {"name":"Start", "id":"start_ts"},
                {"name":"End", "id":"end_ts"},
                {"name":"Break", "id":"break_ts"},
                {"name":"Break Kind", "id":"break_kind"},
                {"name":"Sup Angle (ATR°)", "id":"angle_sup_deg_atr", "type":"numeric", "format":{"specifier":".1f"}},
                {"name":"Res Angle (ATR°)", "id":"angle_res_deg_atr", "type":"numeric", "format":{"specifier":".1f"}},
                {"name":"Sup Slope", "id":"slope_sup", "type":"numeric", "format":{"specifier":".4f"}},
                {"name":"Res Slope", "id":"slope_res", "type":"numeric", "format":{"specifier":".4f"}},
                {"name":"Sup Touches", "id":"sup_touches"},
                {"name":"Res Touches", "id":"res_touches"},
                {"name":"Window", "id":"window_used"},
                {"name":"R²", "id":"r2", "type":"numeric", "format":{"specifier":".2f"}},
                {"name":"p-value", "id":"p", "type":"numeric", "format":{"specifier":".3f"}},
                {"name":"Pattern", "id":"pattern"},
                {"name":"Conf", "id":"pattern_conf", "type":"numeric", "format":{"specifier":".2f"}},
            ],
            data=[], page_size=8, style_table={"overflowX": "auto"},
            style_cell={"fontFamily": "Courier New, monospace", "fontSize": "12px"},
        ),

        dcc.Store(id="state", data={
            "position": 0, "entry_price": None, "realized": 0.0,
            "last_signal_idx": -1, "trades": [], "trailing": None, "last_processed_bar": -1
        }),
        dcc.Store(id="calc-cache", data={}),

        dcc.Interval(id='refresh', interval=1500, n_intervals=0),
    ])

    # Callback to dynamically adjust Interval interval
    @app.callback(Output('refresh', 'interval'),
                Input('refresh-ms', 'value'))
    def set_interval(ms):
        try:
            return int(ms)
        except Exception:
            return 1500

    @app.callback(
        [Output('sr-chart', 'figure'),
        Output('status', 'children'),
        Output('refresh', 'disabled'),
        Output('trades-table', 'data'),
        Output('segments-table', 'data'),
        Output('state', 'data'),
        Output('calc-cache', 'data')],
        [Input('refresh', 'n_intervals'),
        Input('live-mode','value'),
        Input('loop','value'),
        Input('last-n','value'),
        Input('step-bars','value'),
        Input('method','value'),
        Input('min-r2','value'),
        Input('alpha-p','value'),
        Input('touch-spacing','value'),
        Input('use-atr-tol','value'),
        Input('atr-len','value'),
        Input('min-touch-s','value'),
        Input('min-touch-r','value'),
        Input('create-on','value'),
        Input('prefer','value'),
        Input('min-slope','value'),
        Input('base-w','value'),
        Input('max-w','value'),
        Input('step-w','value'),
        Input('max-active-len','value'),
        Input('plot-scheme','value'),
        Input('show-rangeslider','value'),
        Input('trg-mult','value'),
        Input('tick-size','value'),
        Input('min-R-ticks','value'),
        Input('min-stop-nudge','value'),
        Input('intrabar-stop','value'),
        Input('close-target','value'),
        Input('recreate-mode','value'),
        Input('show-higher','value'),
        Input('higher-window','value'),
        Input('higher-max-active','value'),
        Input('recent-segs','value')],
        [State('state', 'data'),
        State('calc-cache','data')]
    )
    def refresh_chart(n, live_values, loop_values, last_n, step_bars,
                    method, min_r2, alpha_p, touch_spacing, use_atr_tol_values, atr_len,
                    min_touch_s, min_touch_r, create_on, prefer, min_slope, base_w, max_w, step_w,
                    max_active_len, plot_scheme, show_rangeslider_values,
                    trg_mult, tick_size, min_R_ticks, min_stop_nudge, intrabar_stop_values, close_target_values,
                    recreate_mode_value, show_higher_values, higher_window, higher_max_active, recent_segs,
                    state, cache):

        t0 = time.perf_counter()

        df = DF_FULL.iloc[-int(last_n):].copy() if isinstance(last_n, (int, float)) and last_n else DF_FULL.copy()
        total = len(df)

        live_on = (live_values is not None) and ('on' in live_values)
        loop_on = (loop_values is not None) and ('on' in loop_values)
        step_bars = int(step_bars) if step_bars else 5


        base_w = max(5, int(base_w or 20))
        max_w  = max(base_w, int(max_w or base_w))
        step_w = max(1, int(step_w or 5))

        # rows to reveal (no-freeze)
        if live_on:
            growable = max(0, total - base_w)
            if growable == 0:
                k = base_w
            else:
                steps_used = max(0, n) * max(1, int(step_bars))
                if loop_on:
                    offset = (steps_used % growable) + 1
                    k = base_w + offset
                else:
                    k = min(base_w + steps_used, total)
            k = max(base_w, min(k, total))
            df_slice = df.iloc[:max(1, k)]
        else:
            df_slice = df

        # Adjust ATR tolerance usage based on streaming mode
        use_atr_live = (
        (use_atr_tol_values is not None and 'on' in use_atr_tol_values)
        and (not live_on)  # disable ATR tolerance during live to speed up
        )

        method_eff = method
        if live_on and method in ('huber', 'ransac'):
            method_eff = 'ols'


        tol_pct = 0.001; tol_abs = None

        atr_len_eff = int(atr_len or ATR_LEN_DEFAULT)
        atr_series = atr(df_slice, atr_len_eff)  # precompute once

        # cache key
        cache = cache or {}
        last_ts = str(df_slice.index[-1])
        
        param_key = (method_eff, float(min_r2 or 0), float(alpha_p or 0), int(touch_spacing or 0),
                    bool(use_atr_tol_values and 'on' in use_atr_tol_values), atr_len_eff,
                    int(min_touch_s or 0), int(min_touch_r or 0),
                    create_on or 'either', prefer or 'max', float(min_slope or 0.0),
                    int(base_w or 0), int(max_w or 0), int(step_w or 0),
                    int(max_active_len or 0), str(recreate_mode_value or 'both'),
                    bool(show_higher_values and 'on' in show_higher_values),
                    int(higher_window or 0), int(higher_max_active or 0))
        cache_key = (last_ts, param_key)

        if cache.get("key") == cache_key:
            segs_ts = pd.DataFrame(cache.get("segs_ts", []))
            signals = [Signal(**s) for s in cache.get("signals", [])]
            segs_hi = pd.DataFrame(cache.get("segs_hi", []))
        else:
            segs, signals = build_stateful_segments_confirming(
                df_slice, base_w, max_w, step_w,
                method_eff, True, True,
                tol_abs, tol_pct,
                int(min_touch_s or 2), int(min_touch_r or 2),
                create_on or 'either', False, prefer or 'max',
                float(min_slope or 0.0), True,
                float(min_r2 or MIN_R2_DEFAULT), float(alpha_p or ALPHA_P_DEFAULT),
                int(touch_spacing or TOUCH_SPACING_DEFAULT),
                atr_len_eff,
                int(max_active_len or 140),
                recreate_mode=str(recreate_mode_value or "both"),
                atr_series=atr_series
            )

            # Consume signals into trades/state (simple open/close logic)
            state = state or {"position":0,"entry_price":None,"realized":0.0,"last_signal_idx":-1,"trades":[]}
            state = process_signals_simple(df_slice, signals, state)


            # --- Save outputs to CSV ---
            # Save signals
            if not live_on:
                if signals:
                    pd.DataFrame([s.__dict__ for s in signals]).to_csv("signals_output.csv", index=False)

                # Save executed trades
                trades_df = pd.DataFrame(state.get("trades", []))
                if not trades_df.empty:
                    trades_df.to_csv("executed_trades_output.csv", index=False)


            segs_ts = with_timestamps(df_slice, segs)
            segs_hi = pd.DataFrame()
            if show_higher_values is not None and 'on' in show_higher_values:
                segs_hi = build_higher_frame(df_slice, int(higher_window or 1000), int(higher_max_active or 340),
                                            method, float(min_r2 or MIN_R2_DEFAULT), float(alpha_p or ALPHA_P_DEFAULT),
                                            int(touch_spacing or TOUCH_SPACING_DEFAULT),
                                            (use_atr_tol_values is not None and 'on' in use_atr_tol_values),
                                            atr_len_eff, atr_series=atr_series)

            cache = {"key": cache_key,
                    "segs_ts": segs_ts.to_dict("records"),
                    "signals": [s.__dict__ for s in signals],
                    "segs_hi": segs_hi.to_dict("records")}

        # Pattern (last active)
        pattern_text = ""
        if not segs_ts.empty:
            pat_info = classify_pattern_for_segment(segs_ts.iloc[-1])
            pattern_text = f" | Pattern: {pat_info['pattern']} (conf {pat_info['confidence']:.2f})"

        # trailing — placeholder: keep your existing logic externally if needed
        state = state or {"position":0,"entry_price":None,"realized":0.0,"last_signal_idx":-1,"trades":[],"trailing":None,"last_processed_bar":-1}
        cur_px = float(df_slice['Close'].iloc[-1])
        pos = int(state.get("position",0)); entry = state.get("entry_price"); realized = float(state.get("realized",0.0))
        unreal = 0.0 if not pos or entry is None else (cur_px - entry) * pos
        total_pnl = realized + unreal

        # Plot
        t1 = time.perf_counter()
        segs_to_plot = segs_ts.tail(int(recent_segs or 18)) if live_on else segs_ts
        fig = plot_segments_plotly(
            df_slice, segs_to_plot, signals,
            mark_mode='candle', color_scheme=plot_scheme or 'by_side',
            show_rangeslider=(show_rangeslider_values is not None and 'on' in show_rangeslider_values),
            title=None, uirevision_key="keep"
        )
        if cache.get("segs_hi"):
            segs_hi_df = pd.DataFrame(cache["segs_hi"])
            fig = overlay_higher(fig, df_slice, segs_hi_df, int(higher_window or 180))

        last_dt = str(df.index[-1].date()) if hasattr(df.index[-1], 'date') else str(df.index[-1])
        t2 = time.perf_counter()

        pos_label = { -1: "SHORT", 0: "FLAT", 1: "LONG" }[pos]
        status = f"S/R Trendlines – {len(df_slice)}/{total} bars (data till {last_dt})"
        status += f" | Pos: {pos_label}"
        if entry is not None:
            status += f" | Entry: {entry:.2f}"
        status += f" | PnL: Realized {realized:.2f}, Unrealized {unreal:.2f}, Total {total_pnl:.2f}{pattern_text}"
        status += f" | timings: build={ (t1-t0)*1000:.0f}ms, plot={ (t2-t1)*1000:.0f}ms"

        done = (len(df_slice) >= total) and live_on and (not loop_on)
        #interval_disabled = False if loop_on else done is 
        interval_disabled = (not live_on) or (live_on and not loop_on and len(df_slice) >= total)

        # segments table
        seg_rows = segs_ts.to_dict("records")

        return fig, status, interval_disabled, state.get("trades", []), seg_rows, state, cache


    ## Testing 
    # ---------- 1) Run the scan and return signals ----------
    def run_signal_scan(
        df: pd.DataFrame,
        *,
        base_window: int = 30, max_window: int = 120, step_window: int = 10,
        method: str = "huber", track_support: bool = True, track_resistance: bool = True,
        tol_abs: Optional[float] = None, tol_pct: Optional[float] = 0.0025,
        min_touches_support: int = 3, min_touches_resistance: int = 3,
        create_on: str = "both", start_new_at_next_bar: bool = False,
        prefer_candidate: str = "strongest", min_slope_abs: float = 0.0, force_when_missing: bool = False,
        min_r2: float = 0.70, alpha_p: float = 0.05, use_atr_tol: bool = True,
        touch_spacing: int = 3, atr_len: int = 14,
        max_active_len: Optional[int] = 140, recreate_mode: str = "both",
        atr_series: Optional[pd.Series] = None,
    ) -> Tuple[pd.DataFrame, List[Signal]]:
        """
        Runs the full pipeline and returns (segments_df, signals_list).
        """
        segs, signals = build_stateful_segments_confirming(
            df,
            base_window, max_window, step_window,
            method, track_support, track_resistance,
            tol_abs, tol_pct,
            min_touches_support, min_touches_resistance,
            create_on, start_new_at_next_bar, prefer_candidate, min_slope_abs, force_when_missing,
            min_r2, alpha_p, use_atr_tol, touch_spacing, atr_len,
            max_active_len=max_active_len,
            recreate_mode=recreate_mode,
            atr_series=atr_series
        )
        return segs, signals


    # ---------- 2) Convert Signal objects to a tidy DataFrame ----------
    def signals_to_dataframe(signals: List[Signal], df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Flattens your Signal list (including meta like strength/pattern) into a DataFrame.
        If df is provided, adds a 'time' column from df.index[bar_index].
        """
        rows = []
        for s in signals:
            row = {
                "side": s.side,
                "reason": s.reason,
                "bar_index": int(s.bar_index),
                "price": float(s.price),
            }
            # Map to timestamp if df is given
            if df is not None and 0 <= s.bar_index < len(df):
                row["time"] = df.index[s.bar_index]

            meta = getattr(s, "meta", {}) or {}
            row.update({
                "pattern": meta.get("pattern"),
                "pattern_conf": meta.get("pattern_conf"),
                "angle_sup_deg_atr": meta.get("angle_sup_deg_atr"),
                "angle_res_deg_atr": meta.get("angle_res_deg_atr"),
                "sup_touches": meta.get("sup_touches"),
                "res_touches": meta.get("res_touches"),
                "window_used": meta.get("window_used"),
                "r2": meta.get("r2"),
                "p": meta.get("p"),
                "strength_score": meta.get("strength_score"),
                "strength_label": meta.get("strength_label"),
                "strength_components": meta.get("strength_components"),
                "strength_explain": meta.get("strength_explain"),
            })
            rows.append(row)

        df_out = pd.DataFrame(rows)
        return df_out.sort_values("bar_index").reset_index(drop=True)


    # ---------- 3) (Optional) Quick dummy data generator for smoke tests ----------
    def make_dummy_ohlc(n: int = 300, seed: int = 42) -> pd.DataFrame:
        """
        Creates a simple OHLC dataframe with a drift + noise regime and a couple of trend shifts.
        Useful just to see signals triggering end-to-end.
        """
        rng = np.random.default_rng(seed)
        # base walk
        drift = np.r_[np.full(n//3, 0.06), np.full(n//3, -0.04), np.full(n - 2*(n//3), 0.02)]
        ret = drift + rng.normal(0, 0.5, size=n)
        px = 100 + np.cumsum(ret).astype(float)

        # synth OHLC around close
        close = px
        high = close + rng.uniform(0.1, 0.8, size=n)
        low  = close - rng.uniform(0.1, 0.8, size=n)
        open_ = (high + low) / 2 + rng.normal(0, 0.05, size=n)
        vol = (rng.lognormal(mean=12.0, sigma=0.35, size=n)).astype(int)

        dt_index = pd.date_range("2023-01-01", periods=n, freq="D")
        return pd.DataFrame({
            "Open": open_, "High": high, "Low": low, "Close": close, "Volume": vol
        }, index=dt_index)

    def summarize_as_of_last_close(
        df: pd.DataFrame,
        # pass-through params for your builder with sensible defaults:
        base_window: int = 30, max_window: int = 120, step_window: int = 10,
        method: str = "huber", track_support: bool = True, track_resistance: bool = True,
        tol_abs: Optional[float] = None, tol_pct: Optional[float] = 0.0025,
        min_touches_support: int = 3, min_touches_resistance: int = 3,
        create_on: str = "both", start_new_at_next_bar: bool = False,
        prefer_candidate: str = "strongest", min_slope_abs: float = 0.0, force_when_missing: bool = False,
        min_r2: float = 0.70, alpha_p: float = 0.05, use_atr_tol: bool = True,
        touch_spacing: int = 3, atr_len: int = 14,
        max_active_len: Optional[int] = 140, recreate_mode: str = "both",
        atr_series: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """
        Returns a dict with:
        - signal: "BUY" | "SELL" | "NEUTRAL"
        - reason: string or None
        - bar_index: last bar index
        - time: last index (if datetime-like)
        - price: last Close
        - slope_sup, slope_res: floats (may be nan)
        - pattern, pattern_confidence: from classify_pattern_for_segment
        - segment_meta: the segment row (start,end,break_kind,...)
        """
        if df is None or len(df) == 0:
            return {"signal": "NEUTRAL", "reason": None, "bar_index": None, "time": None,
                    "price": None, "slope_sup": float("nan"), "slope_res": float("nan"),
                    "pattern": None, "pattern_confidence": None, "segment_meta": None}

        last_idx = len(df) - 1
        last_time = getattr(df.index, "tolist", lambda: [None])()[last_idx] if len(getattr(df, "index", [])) else None
        last_px = float(df["Close"].iloc[last_idx])

        # run your segment builder
        segs, signals = build_stateful_segments_confirming(
            df,
            base_window, max_window, step_window,
            method, track_support, track_resistance,
            tol_abs, tol_pct,
            min_touches_support, min_touches_resistance,
            create_on, start_new_at_next_bar, prefer_candidate, min_slope_abs, force_when_missing,
            min_r2, alpha_p, use_atr_tol, touch_spacing, atr_len,
            max_active_len=max_active_len,
            recreate_mode=recreate_mode,
            atr_series=atr_series
        )

        # default
        out_signal = "NEUTRAL"
        out_reason = None

        # treat it as a signal "as of last close" only if the confirm happened on the last bar
        if signals:
            last_sig = signals[-1]
            if int(last_sig.bar_index) == last_idx:
                out_signal = last_sig.side
                out_reason = last_sig.reason

        # find the segment that spans the last bar; else fall back to the most recent segment
        seg_row = None
        if isinstance(segs, pd.DataFrame) and not segs.empty:
            mask = (segs["start"].astype(int) <= last_idx) & (segs["end"].astype(int) >= last_idx)
            if mask.any():
                seg_row = segs.loc[mask].iloc[-1]
            else:
                seg_row = segs.iloc[-1]

        slope_sup = float(seg_row["slope_sup"]) if seg_row is not None and pd.notna(seg_row["slope_sup"]) else float("nan")
        slope_res = float(seg_row["slope_res"]) if seg_row is not None and pd.notna(seg_row["slope_res"]) else float("nan")

        # pattern on the active/last segment
        pattern = None
        pattern_conf = None
        if seg_row is not None:
            try:
                pat = classify_pattern_for_segment(seg_row)
                pattern = pat.get("pattern")
                pattern_conf = pat.get("confidence")
            except Exception:
                # if your classifier expects angles that aren't present, that's fine—we just skip
                pass

        # include some useful segment meta for debugging/UI
        segment_meta = None
        if seg_row is not None:
            wanted_cols = ["start", "end", "break_at", "break_kind", "sup_touches", "res_touches",
                        "window_used", "r2", "p", "slope_sup", "slope_res"]
            segment_meta = {c: (seg_row[c] if c in seg_row else None) for c in wanted_cols}

        return {
            "signal": out_signal,
            "reason": out_reason,
            "bar_index": int(last_idx),
            "time": last_time,
            "price": last_px,
            "slope_sup": slope_sup,
            "slope_res": slope_res,
            "pattern": pattern,
            "pattern_confidence": pattern_conf,
            "segment_meta": segment_meta,
        }
    app.run(debug=True, use_reloader=False)
