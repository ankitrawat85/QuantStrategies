
import os, json, csv, argparse
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Tuple, Any
import numpy as np
import pandas as pd

# ----------------------------
# Config
# ----------------------------

@dataclass
class StreamCfg:
    lookback: int = 80            # bars to look back when (re)seeding a line
    min_touches: int = 3          # require at least this many "touch" bars
    tol_pct: float = 0.002        # tolerance as a fraction of price (e.g., 0.2%)
    confirm_wait: int = 0         # 0 = flag break on same bar (kept minimal)

# ----------------------------
# Line model
# ----------------------------

@dataclass
class Line:
    line_id: int
    kind: str                     # 'support' or 'resistance'
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

# ----------------------------
# State
# ----------------------------

def empty_state() -> Dict[str, Any]:
    return {
        "line_seq": 0,
        "support": None,          # serialized Line or None
        "resistance": None,       # serialized Line or None
        "last_idx": -1
    }

def serialize_line(line: Optional[Line]) -> Optional[Dict[str, Any]]:
    return asdict(line) if line is not None else None

def deserialize_line(obj: Optional[Dict[str, Any]]) -> Optional[Line]:
    if obj is None: return None
    return Line(**obj)

# ----------------------------
# Utility
# ----------------------------

def _ensure_datetime(df: pd.DataFrame) -> pd.DataFrame:
    if "date" not in df.columns:
        raise ValueError("CSV must have a 'date' column")
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"])
    return out

def _calc_tol(price: float, tol_pct: float) -> float:
    return abs(price) * tol_pct

def _ols_fit(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    # y ~ a*x + b ; return (a, b)
    if len(x) == 0:
        raise ValueError("Empty data for OLS fit")
    A = np.vstack([x, np.ones_like(x)]).T
    a, b = np.linalg.lstsq(A, y, rcond=None)[0]
    return float(a), float(b)

def _touch_indices_support(y: np.ndarray, y_line: np.ndarray, tol: float) -> np.ndarray:
    ok = (y >= y_line - tol)
    if not ok.all():
        return np.array([], dtype=int)
    touch = np.where((y - y_line) <= tol)[0]
    return touch

def _touch_indices_resistance(y: np.ndarray, y_line: np.ndarray, tol: float) -> np.ndarray:
    ok = (y <= y_line + tol)
    if not ok.all():
        return np.array([], dtype=int)
    touch = np.where((y_line - y) <= tol)[0]
    return touch

def _maybe_seed_support(df: pd.DataFrame, cfg: StreamCfg, end_idx: int):
    start_idx = max(0, end_idx - cfg.lookback + 1)
    win = df.iloc[start_idx:end_idx+1]
    idxs = np.arange(start_idx, end_idx+1)
    y = win["low"].to_numpy(dtype=float)
    x = idxs.astype(float)
    a, b = _ols_fit(x, y)
    y_line = a * x + b
    tol = _calc_tol(win["close"].iloc[-1], cfg.tol_pct)
    touches = _touch_indices_support(y, y_line, tol)
    if len(touches) >= cfg.min_touches:
        abs_touches = (start_idx + touches).tolist()
        created_time = str(win["date"].iloc[0].date()) + "->" + str(win["date"].iloc[-1].date())
        line = Line(
            line_id=-1,
            kind="support",
            start_idx=int(start_idx),
            end_idx=int(end_idx),
            slope=float(a),
            intercept=float(b),
            touch_indices=abs_touches,
            created_time=created_time,
            last_update_time=str(win['date'].iloc[-1].date()),
            is_active=True
        )
        return line, abs_touches
    return None

def _maybe_seed_resistance(df: pd.DataFrame, cfg: StreamCfg, end_idx: int):
    start_idx = max(0, end_idx - cfg.lookback + 1)
    win = df.iloc[start_idx:end_idx+1]
    idxs = np.arange(start_idx, end_idx+1)
    y = win["high"].to_numpy(dtype=float)
    x = idxs.astype(float)
    a, b = _ols_fit(x, y)
    y_line = a * x + b
    tol = _calc_tol(win["close"].iloc[-1], cfg.tol_pct)
    touches = _touch_indices_resistance(y, y_line, tol)
    if len(touches) >= cfg.min_touches:
        abs_touches = (start_idx + touches).tolist()
        created_time = str(win["date"].iloc[0].date()) + "->" + str(win["date"].iloc[-1].date())
        line = Line(
            line_id=-1,
            kind="resistance",
            start_idx=int(start_idx),
            end_idx=int(end_idx),
            slope=float(a),
            intercept=float(b),
            touch_indices=abs_touches,
            created_time=created_time,
            last_update_time=str(win['date'].iloc[-1].date()),
            is_active=True
        )
        return line, abs_touches
    return None

def _append_csv(path: str, header: list, rows: list):
    import csv, os
    exists = os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        if not exists:
            w.writeheader()
        for r in rows:
            r2 = {k: r.get(k, "") for k in header}
            w.writerow(r2)

EVENT_HEADERS = [
    "event", "line_id", "kind",
    "start_idx", "end_idx", "slope", "intercept",
    "touch_indices", "touch_prices", "touch_times",
    "break_idx", "break_time", "break_price",
]

POINTS_HEADERS = [
    "line_id", "kind", "touch_idx", "touch_time", "touch_price"
]

def _log_creation(events_path: str, points_path: str, df: pd.DataFrame, line: Line):
    times = df.iloc[line.touch_indices]["date"].dt.strftime("%Y-%m-%d").tolist()
    prices = (df.iloc[line.touch_indices]["low"] if line.kind=="support" else df.iloc[line.touch_indices]["high"]).tolist()
    row = {
        "event": f"create_{line.kind}",
        "line_id": line.line_id,
        "kind": line.kind,
        "start_idx": line.start_idx,
        "end_idx": line.end_idx,
        "slope": line.slope,
        "intercept": line.intercept,
        "touch_indices": "|".join(map(str, line.touch_indices)),
        "touch_prices": "|".join(map(lambda x: f"{x:.6f}", prices)),
        "touch_times": "|".join(times),
        "break_idx": "",
        "break_time": "",
        "break_price": "",
    }
    _append_csv(events_path, EVENT_HEADERS, [row])

    rows = []
    for ti, tm, px in zip(line.touch_indices, times, prices):
        rows.append({
            "line_id": line.line_id,
            "kind": line.kind,
            "touch_idx": ti,
            "touch_time": tm,
            "touch_price": px
        })
    _append_csv(points_path, POINTS_HEADERS, rows)

def _log_break(events_path: str, line: Line, break_idx: int, break_time: str, break_price: float):
    row = {
        "event": f"{line.kind}_break",
        "line_id": line.line_id,
        "kind": line.kind,
        "start_idx": line.start_idx,
        "end_idx": line.end_idx,
        "slope": line.slope,
        "intercept": line.intercept,
        "touch_indices": "|".join(map(str, line.touch_indices)),
        "touch_prices": "",
        "touch_times": "",
        "break_idx": break_idx,
        "break_time": break_time,
        "break_price": break_price
    }
    _append_csv(events_path, EVENT_HEADERS, [row])

def update_streaming(state: Dict[str, Any], df: pd.DataFrame, i: int, cfg: StreamCfg,
                     events_path: str, points_path: str) -> Dict[str, Any]:
    state = dict(state) if state is not None else empty_state()
    sup = deserialize_line(state.get("support"))
    res = deserialize_line(state.get("resistance"))
    line_seq = int(state.get("line_seq", 0))

    bar = df.iloc[i]
    idx = i
    tstr = bar["date"].strftime("%Y-%m-%d")
    price = float(bar["close"])
    tol = _calc_tol(price, cfg.tol_pct)

    if sup is None:
        seeded = _maybe_seed_support(df, cfg, idx)
        if seeded is not None:
            line, _ = seeded
            line_seq += 1
            line.line_id = line_seq
            _log_creation(events_path, points_path, df, line)
            sup = line
    if res is None:
        seeded = _maybe_seed_resistance(df, cfg, idx)
        if seeded is not None:
            line, _ = seeded
            line_seq += 1
            line.line_id = line_seq
            _log_creation(events_path, points_path, df, line)
            res = line

    if sup is not None and sup.is_active:
        sup.end_idx = idx
        sup.last_update_time = tstr
        yline = sup.value_at(idx)
        if price < (yline - tol):
            _log_break(events_path, sup, idx, tstr, price)
            sup.is_active = False

    if res is not None and res.is_active:
        res.end_idx = idx
        res.last_update_time = tstr
        yline = res.value_at(idx)
        if price > (yline + tol):
            _log_break(events_path, res, idx, tstr, price)
            res.is_active = False

    out = {
        "line_seq": line_seq,
        "support": serialize_line(sup),
        "resistance": serialize_line(res),
        "last_idx": idx
    }
    return out

def load_state(path: str) -> Dict[str, Any]:
    import os, json
    if not os.path.exists(path):
        return empty_state()
    with open(path, "r") as f:
        return json.load(f)

def save_state(path: str, state: Dict[str, Any]):
    import json
    with open(path, "w") as f:
        json.dump(state, f, indent=2)

def simulate_over_csv(csv_path: str, cfg: StreamCfg,
                      state_path: str, events_path: str, points_path: str,
                      start: str=None, end: str=None):
    df = pd.read_csv(csv_path)
    df = _ensure_datetime(df)
    if start is not None:
        df = df[df["date"] >= pd.to_datetime(start)]
    if end is not None:
        df = df[df["date"] <= pd.to_datetime(end)]
    df = df.reset_index(drop=True)

    state = empty_state()
    for p in [events_path, points_path]:
        import os
        if os.path.exists(p):
            os.remove(p)

    for i in range(len(df)):
        state = update_streaming(state, df, i, cfg, events_path, points_path)
    save_state(state_path, state)

def init_state_upto(csv_path: str, cfg: StreamCfg,
                    state_path: str, events_path: str, points_path: str,
                    upto_date: str):
    df = pd.read_csv(csv_path)
    df = _ensure_datetime(df)
    df = df[df["date"] <= pd.to_datetime(upto_date)].reset_index(drop=True)

    state = empty_state()
    for i in range(len(df)):
        state = update_streaming(state, df, i, cfg, events_path, points_path)
    save_state(state_path, state)

def step_one_date(csv_path: str, cfg: StreamCfg,
                  state_path: str, events_path: str, points_path: str,
                  date_str: str):
    df = pd.read_csv(csv_path)
    df = _ensure_datetime(df)
    row = df[df["date"] == pd.to_datetime(date_str)]
    if len(row) != 1:
        raise ValueError(f"Could not find exactly one row for date={date_str}. Found {len(row)}.")
    df = df.sort_values("date").reset_index(drop=True)
    idx = df.index[df["date"] == pd.to_datetime(date_str)][0]

    state = load_state(state_path)
    state = update_streaming(state, df, idx, cfg, events_path, points_path)
    save_state(state_path, state)

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Minimal streaming trendline creation + break detection with state + CSV logs")
    ap.add_argument("--csv", required=True, help="Input CSV with columns: date, open, high, low, close")
    ap.add_argument("--state", default="trend_state.json", help="Path to JSON file to persist streaming state")
    ap.add_argument("--events", default="trend_events.csv", help="Path to event CSV log")
    ap.add_argument("--points", default="line_points.csv", help="Path to per-touch points CSV log")
    ap.add_argument("--lookback", type=int, default=80)
    ap.add_argument("--min-touches", type=int, default=3)
    ap.add_argument("--tol-pct", type=float, default=0.002)
    ap.add_argument("--confirm-wait", type=int, default=0)

    ap.add_argument("--simulate", action="store_true", help="Run full simulation over CSV (clears logs)")
    ap.add_argument("--start", type=str, default=None, help="Start date for simulation (YYYY-MM-DD)")
    ap.add_argument("--end", type=str, default=None, help="End date for simulation (YYYY-MM-DD)")

    ap.add_argument("--init-upto", type=str, default=None, help="Initialize state up to this date (inclusive)")
    ap.add_argument("--step-date", type=str, default=None, help="Process exactly one new bar for this date")

    args = ap.parse_args()
    cfg = StreamCfg(
        lookback=args.lookback,
        min_touches=args.min_touches,
        tol_pct=args.tol_pct,
        confirm_wait=args.confirm_wait
    )

    if args.simulate:
        simulate_over_csv(args.csv, cfg, args.state, args.events, args.points, args.start, args.end)
        print(f"Simulation done. State -> {args.state}; Events -> {args.events}; Points -> {args.points}")
        return

    if args.init_upto is not None:
        init_state_upto(args.csv, cfg, args.state, args.events, args.points, args.init_upto)
        print(f"Initialized state up to {args.init_upto}. State -> {args.state}")
        return

    if args.step_date is not None:
        step_one_date(args.csv, cfg, args.state, args.events, args.points, args.step_date)
        print(f"Processed bar for {args.step_date}. State -> {args.state}; Events -> {args.events}")
        return

    ap.error("Please specify one mode: --simulate OR --init-upto DATE OR --step-date DATE")

if __name__ == "__main__":
    main()
