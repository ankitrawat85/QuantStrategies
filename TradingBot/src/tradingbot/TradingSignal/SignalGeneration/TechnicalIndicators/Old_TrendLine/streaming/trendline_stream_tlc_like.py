
import os, json, csv, argparse
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Tuple, Any
import numpy as np
import pandas as pd
from tradingbot.TradingSignal.Tradingsignals.TechnicalIndicators.TrendLine.streaming.trendline_plot_minimal import plot_history_clean_latest,plot_history_active_break_by_kind

# ============================
# Utilities
# ============================

def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["High"].to_numpy(float), df["Low"].to_numpy(float), df["Close"].to_numpy(float)
    prev_c = np.concatenate([[c[0]], c[:-1]])
    tr = np.maximum.reduce([h - l, np.abs(h - prev_c), np.abs(l - prev_c)])
    atr = pd.Series(tr).rolling(n, min_periods=1).mean()
    return atr

def _wls(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> Tuple[float,float]:
    X = np.vstack([x, np.ones_like(x)]).T
    XtWX = (X.T * w) @ X
    XtWy = (X.T * w) @ y
    a, b = np.linalg.lstsq(XtWX, XtWy, rcond=None)[0]
    return float(a), float(b)

def _ols(x: np.ndarray, y: np.ndarray) -> Tuple[float,float]:
    X = np.vstack([x, np.ones_like(x)]).T
    a, b = np.linalg.lstsq(X, y, rcond=None)[0]
    return float(a), float(b)

def _huber_fit(x: np.ndarray, y: np.ndarray, c: float = 1.345, iters: int = 20) -> Tuple[float,float]:
    a, b = _ols(x, y)
    for _ in range(iters):
        r = y - (a*x + b)
        mad = np.median(np.abs(r - np.median(r))) or 1.0
        s = 1.4826 * mad or 1.0
        abs_r = np.abs(r) / (s + 1e-12)
        w = np.where(abs_r <= c, 1.0, (c / (abs_r + 1e-12)))
        a_new, b_new = _wls(x, y, w)
        if np.isclose(a, a_new) and np.isclose(b, b_new):
            break
        a, b = a_new, b_new
    return float(a), float(b)

def _fit_line(x: np.ndarray, y: np.ndarray, method: str = "huber") -> Tuple[float,float]:
    return _huber_fit(x, y) if method == "huber" else _ols(x, y)

def _tol_vector(close: np.ndarray, atr_vec: np.ndarray, tol_pct: float, atr_mult: float) -> np.ndarray:
    return np.maximum(close * tol_pct, atr_mult * atr_vec)

# ============================
# Config & Line types
# ============================

@dataclass
class Cfg:
    base_window: int = 40
    max_window: int = 120
    step_window: int = 5
    method: str = "huber"          # "huber" or "ols"
    min_touches: int = 3
    touch_spacing: int = 3         # min bars between counted touches
    tol_pct: float = 0.015
    atr_len: int = 14
    atr_mult: float = 1.0
    max_violations: int = 8        # bars allowed to pierce beyond tol while seeding
    max_active_len: int = 140      # expiry
    reseed_immediate: bool = True  # seed again on the same bar
    reseed_mode: str = "pair"      # "pair" (default) or "single"

@dataclass
class Line:
    line_id: int
    kind: str              # "support" or "resistance"
    start_idx: int
    end_idx: int
    slope: float
    intercept: float
    touch_indices: List[int]
    created_time: str
    last_update_time: str
    is_active: bool = True
    def value_at(self, idx: int) -> float:
        return self.slope * idx + self.intercept

# ============================
# Events logging
# ============================

EVENT_HEADERS = [
    "event", "line_id", "kind",
    "start_idx", "end_idx", "slope", "intercept",
    "touch_indices", "touch_prices", "touch_times",
    "break_idx", "break_time", "break_price",
]
POINTS_HEADERS = ["line_id", "kind", "touch_idx", "touch_time", "touch_price"]

def _append_csv(path: str, header: List[str], rows: List[Dict[str, Any]]):
    exists = os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        if not exists: w.writeheader()
        for r in rows: w.writerow({k: r.get(k, "") for k in header})

def _log_creation(events_path: str, points_path: str, df: pd.DataFrame, line: Line):
    times = df.iloc[line.touch_indices]["date"].dt.strftime("%Y-%m-%d").tolist()
    prices = (df.iloc[line.touch_indices]["Low"] if line.kind=="support" else df.iloc[line.touch_indices]["High"]).tolist()
    row = {
        "event": f"create_{line.kind}",
        "line_id": line.line_id, "kind": line.kind,
        "start_idx": line.start_idx, "end_idx": line.end_idx,
        "slope": line.slope, "intercept": line.intercept,
        "touch_indices": "|".join(map(str, line.touch_indices)),
        "touch_prices": "|".join(map(lambda x: f"{x:.6f}", prices)),
        "touch_times": "|".join(times),
        "break_idx": "", "break_time": "", "break_price": "",
    }
    _append_csv(events_path, EVENT_HEADERS, [row])
    rows = [{"line_id": line.line_id, "kind": line.kind, "touch_idx": ti, "touch_time": tm, "touch_price": px}
            for ti, tm, px in zip(line.touch_indices, times, prices)]
    _append_csv(points_path, POINTS_HEADERS, rows)

def _log_break(events_path: str, line: Line, break_idx: int, break_time: str, break_price: float):
    row = {
        "event": f"{line.kind}_break",
        "line_id": line.line_id, "kind": line.kind,
        "start_idx": line.start_idx, "end_idx": line.end_idx,
        "slope": line.slope, "intercept": line.intercept,
        "touch_indices": "|".join(map(str, line.touch_indices)),
        "touch_prices": "", "touch_times": "",
        "break_idx": break_idx, "break_time": break_time, "break_price": break_price
    }
    _append_csv(events_path, EVENT_HEADERS, [row])

def _log_expire(events_path: str, line: Line, expire_idx: int, expire_time: str):
    row = {
        "event": f"{line.kind}_expire",
        "line_id": line.line_id, "kind": line.kind,
        "start_idx": line.start_idx, "end_idx": line.end_idx,
        "slope": line.slope, "intercept": line.intercept,
        "touch_indices": "|".join(map(str, line.touch_indices)),
        "touch_prices": "", "touch_times": "",
        "break_idx": expire_idx, "break_time": expire_time, "break_price": ""
    }
    _append_csv(events_path, EVENT_HEADERS, [row])

# ============================
# Scan helpers
# ============================

def _count_touches(indices: np.ndarray, y: np.ndarray, yline: np.ndarray, tol: np.ndarray, spacing: int) -> List[int]:
    close_hits = np.where(np.abs(y - yline) <= tol)[0]
    if close_hits.size == 0: return []
    touches = []
    last = -10**9
    for i in close_hits:
        if i - last >= spacing:
            touches.append(int(indices[i]))
            last = i
    return touches

def _valid_support(lows: np.ndarray, yline: np.ndarray, tol: np.ndarray, max_violations: int) -> Tuple[bool, np.ndarray]:
    viol = (lows < (yline - tol))
    return (viol.sum() <= max_violations), viol

def _valid_resistance(highs: np.ndarray, yline: np.ndarray, tol: np.ndarray, max_violations: int) -> Tuple[bool, np.ndarray]:
    viol = (highs > (yline + tol))
    return (viol.sum() <= max_violations), viol

def _scan_best_pair(df: pd.DataFrame, atr_s: pd.Series, end_idx: int, cfg: Cfg) -> Optional[Tuple[Line, Line]]:
    best = None
    closes = df["Close"].to_numpy(float)
    lows   = df["Low"].to_numpy(float)
    highs  = df["High"].to_numpy(float)
    for W in range(cfg.base_window, cfg.max_window+1, cfg.step_window):
        start_idx = max(0, end_idx - W + 1)
        if end_idx - start_idx + 1 < max(10, cfg.min_touches): 
            continue
        idxs = np.arange(start_idx, end_idx+1)
        x = idxs.astype(float)
        atr_vec = atr_s.iloc[start_idx:end_idx+1].to_numpy(float)
        tol_vec = _tol_vector(closes[start_idx:end_idx+1], atr_vec, cfg.tol_pct, cfg.atr_mult)

        a_s, b_s = _fit_line(x, lows[start_idx:end_idx+1], cfg.method)
        yline_s = a_s * x + b_s
        ok_s, _ = _valid_support(lows[start_idx:end_idx+1], yline_s, tol_vec, cfg.max_violations)
        if not ok_s: continue
        touches_s = _count_touches(idxs, lows[start_idx:end_idx+1], yline_s, tol_vec, cfg.touch_spacing)
        if len(touches_s) < cfg.min_touches: continue

        a_r, b_r = _fit_line(x, highs[start_idx:end_idx+1], cfg.method)
        yline_r = a_r * x + b_r
        ok_r, _ = _valid_resistance(highs[start_idx:end_idx+1], yline_r, tol_vec, cfg.max_violations)
        if not ok_r: continue
        touches_r = _count_touches(idxs, highs[start_idx:end_idx+1], yline_r, tol_vec, cfg.touch_spacing)
        if len(touches_r) < cfg.min_touches: continue

        score = len(touches_s) + len(touches_r)
        key = (score, end_idx - start_idx + 1)
        if (best is None) or (key > best[0]):
            best = (key, start_idx, end_idx, (a_s, b_s, touches_s), (a_r, b_r, touches_r))

    if best is None: return None
    _, start_idx, end_idx, sup, res = best
    a_s, b_s, touches_s = sup
    a_r, b_r, touches_r = res
    created_time = f"{df.iloc[start_idx]['date'].date()}->{df.iloc[end_idx]['date'].date()}"
    tstr = str(df.iloc[end_idx]['date'].date())
    sup_line = Line(-1, "support", start_idx, end_idx, float(a_s), float(b_s), touches_s, created_time, tstr, True)
    res_line = Line(-1, "resistance", start_idx, end_idx, float(a_r), float(b_r), touches_r, created_time, tstr, True)
    return sup_line, res_line

def _scan_best_single(df: pd.DataFrame, atr_s: pd.Series, end_idx: int, cfg: Cfg, kind: str) -> Optional[Line]:
    best = None
    closes = df["Close"].to_numpy(float)
    lows   = df["Low"].to_numpy(float)
    highs  = df["High"].to_numpy(float)
    for W in range(cfg.base_window, cfg.max_window+1, cfg.step_window):
        start_idx = max(0, end_idx - W + 1)
        if end_idx - start_idx + 1 < max(10, cfg.min_touches):
            continue
        idxs = np.arange(start_idx, end_idx+1)
        x = idxs.astype(float)
        atr_vec = atr_s.iloc[start_idx:end_idx+1].to_numpy(float)
        tol_vec = _tol_vector(closes[start_idx:end_idx+1], atr_vec, cfg.tol_pct, cfg.atr_mult)
        if kind == "support":
            a, b = _fit_line(x, lows[start_idx:end_idx+1], cfg.method)
            yline = a*x + b
            ok, _ = _valid_support(lows[start_idx:end_idx+1], yline, tol_vec, cfg.max_violations)
            if not ok: continue
            touches = _count_touches(idxs, lows[start_idx:end_idx+1], yline, tol_vec, cfg.touch_spacing)
            if len(touches) < cfg.min_touches: continue
        else:
            a, b = _fit_line(x, highs[start_idx:end_idx+1], cfg.method)
            yline = a*x + b
            ok, _ = _valid_resistance(highs[start_idx:end_idx+1], yline, tol_vec, cfg.max_violations)
            if not ok: continue
            touches = _count_touches(idxs, highs[start_idx:end_idx+1], yline, tol_vec, cfg.touch_spacing)
            if len(touches) < cfg.min_touches: continue

        score = len(touches)
        key = (score, end_idx - start_idx + 1)
        if (best is None) or (key > best[0]):
            best = (key, start_idx, end_idx, a, b, touches)

    if best is None: return None
    _, start_idx, end_idx, a, b, touches = best
    created_time = f"{df.iloc[start_idx]['date'].date()}->{df.iloc[end_idx]['date'].date()}"
    tstr = str(df.iloc[end_idx]['date'].date())
    return Line(-1, kind, start_idx, end_idx, float(a), float(b), touches, created_time, tstr, True)

# ============================
# Streaming
# ============================

def simulate_over_csv(csv_path: str, cfg: Cfg, state_path: str, events_path: str, points_path: str):
    df = pd.read_csv(csv_path)
    lc = {c.lower(): c for c in df.columns}
    def pick(*alts):
        for a in alts:
            if a in lc: return lc[a]
        return None
    date_col = pick("date","datetime","timestamp","time")
    ocol = pick("open","o"); hcol = pick("high","h"); lcol = pick("low","l"); ccol = pick("close","adj close","c")
    df = df.rename(columns={date_col:"date", ocol:"Open", hcol:"High", lcol:"Low", ccol:"Close"})[["date","Open","High","Low","Close"]]
    df["date"] = pd.to_datetime(df["date"]); df = df.sort_values("date").reset_index(drop=True)

    for p in [events_path, points_path]:
        if os.path.exists(p): os.remove(p)

    atr_s = atr(df, cfg.atr_len)

    sup = None; res = None; line_seq = 0

    for idx in range(len(df)):
        bar = df.iloc[idx]; tstr = bar["date"].strftime("%Y-%m-%d")

        # Initial seeding
        if sup is None and res is None:
            pair = _scan_best_pair(df, atr_s, idx, cfg)
            if pair is not None:
                sup, res = pair
                line_seq += 1; sup.line_id = line_seq
                line_seq += 1; res.line_id = line_seq
                _log_creation(events_path, points_path, df, sup)
                _log_creation(events_path, points_path, df, res)
            elif cfg.reseed_mode == "single":
                # try single sides
                s = _scan_best_single(df, atr_s, idx, cfg, "support")
                if s is not None:
                    line_seq += 1; s.line_id = line_seq; _log_creation(events_path, points_path, df, s); sup = s
                r = _scan_best_single(df, atr_s, idx, cfg, "resistance")
                if r is not None:
                    line_seq += 1; r.line_id = line_seq; _log_creation(events_path, points_path, df, r); res = r

        # Extend lines
        if sup is not None and sup.is_active: sup.end_idx = idx; sup.last_update_time = tstr
        if res is not None and res.is_active: res.end_idx = idx; res.last_update_time = tstr

        tol = max(bar["Close"] * cfg.tol_pct, atr_s.iloc[idx] * cfg.atr_mult)

        ended_sup = False; ended_res = False

        if sup is not None and sup.is_active:
            y = sup.value_at(idx)
            if bar["Close"] < (y - tol):
                _log_break(events_path, sup, idx, tstr, float(bar["Close"]))
                sup.is_active = False; ended_sup = True
        if res is not None and res.is_active:
            y = res.value_at(idx)
            if bar["Close"] > (y + tol):
                _log_break(events_path, res, idx, tstr, float(bar["Close"]))
                res.is_active = False; ended_res = True

        # expiry checks
        if sup is not None and sup.is_active and (idx - sup.start_idx + 1) >= cfg.max_active_len:
            _log_expire(events_path, sup, idx, tstr); sup.is_active = False; ended_sup = True
        if res is not None and res.is_active and (idx - res.start_idx + 1) >= cfg.max_active_len:
            _log_expire(events_path, res, idx, tstr); res.is_active = False; ended_res = True

        # Reseed logic
        if cfg.reseed_mode == "pair":
            if ended_sup or ended_res:
                sup = None; res = None
                if cfg.reseed_immediate:
                    pair = _scan_best_pair(df, atr_s, idx, cfg)
                    if pair is not None:
                        sup, res = pair
                        line_seq += 1; sup.line_id = line_seq
                        line_seq += 1; res.line_id = line_seq
                        _log_creation(events_path, points_path, df, sup)
                        _log_creation(events_path, points_path, df, res)
        else:  # single-side reseed
            if ended_sup and not ended_res:
                sup = None
                if cfg.reseed_immediate:
                    s = _scan_best_single(df, atr_s, idx, cfg, "support")
                    if s is not None:
                        line_seq += 1; s.line_id = line_seq; _log_creation(events_path, points_path, df, s); sup = s
            if ended_res and not ended_sup:
                res = None
                if cfg.reseed_immediate:
                    r = _scan_best_single(df, atr_s, idx, cfg, "resistance")
                    if r is not None:
                        line_seq += 1; r.line_id = line_seq; _log_creation(events_path, points_path, df, r); res = r
            if ended_sup and ended_res:
                sup = None; res = None
                if cfg.reseed_immediate:
                    pair = _scan_best_pair(df, atr_s, idx, cfg)
                    if pair is not None:
                        sup, res = pair
                        line_seq += 1; sup.line_id = line_seq
                        line_seq += 1; res.line_id = line_seq
                        _log_creation(events_path, points_path, df, sup)
                        _log_creation(events_path, points_path, df, res)
                    else:
                        # fall back to singles
                        s = _scan_best_single(df, atr_s, idx, cfg, "support")
                        if s is not None:
                            line_seq += 1; s.line_id = line_seq; _log_creation(events_path, points_path, df, s); sup = s
                        r = _scan_best_single(df, atr_s, idx, cfg, "resistance")
                        if r is not None:
                            line_seq += 1; r.line_id = line_seq; _log_creation(events_path, points_path, df, r); res = r

    state = {"support": asdict(sup) if sup is not None else None,
             "resistance": asdict(res) if res is not None else None,
             "line_seq": line_seq, "last_idx": len(df)-1}
    with open(state_path, "w") as f: json.dump(state, f, indent=2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--state", default="tlc_state.json")
    ap.add_argument("--events", default="tlc_events.csv")
    ap.add_argument("--points", default="tlc_points.csv")
    ap.add_argument("--base-window", type=int, default=40)
    ap.add_argument("--max-window", type=int, default=120)
    ap.add_argument("--step-window", type=int, default=5)
    ap.add_argument("--method", choices=["ols","huber"], default="huber")
    ap.add_argument("--min-touches", type=int, default=3)
    ap.add_argument("--touch-spacing", type=int, default=3)
    ap.add_argument("--tol-pct", type=float, default=0.015)
    ap.add_argument("--atr-len", type=int, default=14)
    ap.add_argument("--atr-mult", type=float, default=1.0)
    ap.add_argument("--max-violations", type=int, default=8)
    ap.add_argument("--max-active-len", type=int, default=140)
    ap.add_argument("--reseed-immediate", action="store_true")
    ap.add_argument("--reseed-mode", choices=["pair","single"], default="pair")
    ap.add_argument("--simulate", action="store_true")
    args = ap.parse_args()

    cfg = Cfg(base_window=args.base_window, max_window=args.max_window, step_window=args.step_window,
              method=args.method, min_touches=args.min_touches, touch_spacing=args.touch_spacing,
              tol_pct=args.tol_pct, atr_len=args.atr_len, atr_mult=args.atr_mult,
              max_violations=args.max_violations, max_active_len=args.max_active_len,
              reseed_immediate=args.reseed_immediate, reseed_mode=args.reseed_mode)

    if args.simulate:
        simulate_over_csv(args.csv, cfg, args.state, args.events, args.points)
        print(f"Simulation done. State -> {args.state}; Events -> {args.events}; Points -> {args.points}")
        plot_history_active_break_by_kind(
        "data_SBIN.csv", "tlc_events.csv",
        save_path="SBIN_single_reseed.png",
        use_candles=True
        )
        return
    ap.error("Use --simulate for this minimal CLI")

if __name__ == "__main__":
    main()
