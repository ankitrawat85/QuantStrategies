#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
trendline_stream_run_all.py (patched)
- Runs main_trendline_stream.py for one or more methods
- Forwards angle veto knobs: --angle-between-min-deg, --parallel-gap-max-atr, --parallel-gap-max-pct
- Accepts extra args and passes them through
- Writes per-method events/points/plot under --outdir
- Optionally builds a consolidated signals summary CSV/JSON
"""
import argparse, os, sys, subprocess, json
from pathlib import Path
import pandas as pd

def parse_args():
    p = argparse.ArgumentParser(description="Run multiple methods & build consolidated summary")
    p.add_argument("--script", required=True, help="Path to main_trendline_stream.py")
    p.add_argument("--csv", required=True, help="Prices CSV")
    p.add_argument("--config", required=False, default="", help="Config JSON")
    p.add_argument("--methods", required=True, help="Comma-separated list, e.g. ols,huber,hough")
    p.add_argument("--outdir", required=True, help="Output directory")
    p.add_argument("--signals-summary-out", default="", help="Prefix path for consolidated summary (no extension)")
    p.add_argument("--min-confidence", type=float, default=0.0)

    # Angle veto knobs (optional)
    p.add_argument("--angle-between-min-deg", type=float, default=None)
    p.add_argument("--parallel-gap-max-atr", type=float, default=None)
    p.add_argument("--parallel-gap-max-pct", type=float, default=None)
    p.add_argument("--max-angle-deg", type=float, default=None)


    # Accept anything extra and pass through to the child script
    args, extras = p.parse_known_args()
    return args, extras

def run_method(script, csv, config, method, outdir, min_confidence, angle_deg, gap_atr, gap_pct, extras):
    Path(outdir).mkdir(parents=True, exist_ok=True)
    stem = Path(csv).stem  # e.g., data_SBIN -> data_SBIN
    # Try a nicer symbol if present in CSV name like SBIN.csv
    sym_guess = stem.split("_")[-1]
    ev_path = str(Path(outdir) / f"{sym_guess}_{method}_events.csv")
    pt_path = str(Path(outdir) / f"{sym_guess}_{method}_points.csv")
    plot_path = str(Path(outdir) / f"{sym_guess}_{method}.png")

    cmd = [sys.executable, script,
           "--csv", csv,
           "--method", method,
           "--events", ev_path,
           "--points", pt_path,
           "--plot", plot_path,
           "--min-confidence", str(min_confidence)]
    if config:
        cmd += ["--config", config]

    # Angle veto knobs if provided
    if angle_deg is not None:
        cmd += ["--angle-between-min-deg", str(angle_deg)]
    if gap_atr is not None:
        cmd += ["--parallel-gap-max-atr", str(gap_atr)]
    if gap_pct is not None:
        cmd += ["--parallel-gap-max-pct", str(gap_pct)]

    # Passthrough extras to allow things like --base-window, --step-window, etc.
    cmd += extras

    print(">> Running:", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr, file=sys.stderr)
        raise SystemExit(f"[{method}] run failed with code {res.returncode}")
    else:
        # echo a short tail of stdout for logs
        print(res.stdout.splitlines()[-10:])
    return ev_path, pt_path, plot_path

def load_events_safe(path):
    try:
        df = pd.read_csv(path)
        # Normalize typical columns if present
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        if "event" in df.columns:
            df["event"] = df["event"].astype(str)
        return df
    except Exception as e:
        print(f"Warning: could not read events {path}: {e}")
        return pd.DataFrame()


def build_summary(ev_files, summary_prefix):
    """
    Consolidate full-run BUY/SELL per date (across all methods).
    BUY  := resistance break  (side == 'R')
    SELL := support break     (side == 'S')
    Writes two files:
      <prefix>.csv   -> date, BUY, SELL, TOTAL
      <prefix>_by_method.csv -> date, method, BUY, SELL, TOTAL
    """
    if not summary_prefix:
        return ""

    def load_events_safe(path, method):
        try:
            df = pd.read_csv(path)
            df["method"] = method
            # Normalize date
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
            else:
                df["date"] = pd.NaT
            # Normalize side
            side_col = None
            for c in df.columns:
                if c.lower() == "side":
                    side_col = c; break
            if side_col is None:
                # try to infer from other columns if present
                # fall back to empty
                df["side"] = None
                side_col = "side"
            # Keep only break events if such a column exists
            if "event" in df.columns:
                # typical value is "break" for break events
                df = df[df["event"].astype(str).str.lower().eq("break")]
            # Map to BUY/SELL
            def to_signal(v):
                v = (str(v).strip().upper() if v is not None else "")
                if v == "R":
                    return "BUY"
                elif v == "S":
                    return "SELL"
                else:
                    return None
            df["signal"] = df[side_col].map(to_signal)
            # Keep only rows where we could map
            df = df[df["signal"].notna()]
            return df[["date", "signal", "method"]].dropna()
        except Exception as e:
            print(f"Warning: could not read events {path}: {e}")
            return pd.DataFrame(columns=["date","signal","method"])

    frames = []
    for method, f in ev_files.items():
        frames.append(load_events_safe(f, method))

    if not frames:
        print("No event files to summarize.")
        return ""

    all_ev = pd.concat(frames, ignore_index=True)
    # By-date consolidated
    by_date = (all_ev
               .groupby(["date", "signal"], dropna=False)
               .size()
               .unstack(fill_value=0)
               .reset_index()
               .rename_axis(None, axis=1))
    for col in ("BUY","SELL"):
        if col not in by_date.columns:
            by_date[col] = 0
    by_date["TOTAL"] = by_date["BUY"] + by_date["SELL"]

    # By date, by method (extra breakdown)
    by_m = (all_ev
            .groupby(["date", "method", "signal"], dropna=False)
            .size()
            .unstack(fill_value=0)
            .reset_index()
            .rename_axis(None, axis=1))
    for col in ("BUY","SELL"):
        if col not in by_m.columns:
            by_m[col] = 0
    by_m["TOTAL"] = by_m["BUY"] + by_m["SELL"]

    csv_path = f"{summary_prefix}.csv"
    csv_by_m = f"{summary_prefix}_by_method.csv"
    by_date.to_csv(csv_path, index=False)
    by_m.to_csv(csv_by_m, index=False)

    # Also dump a compact JSON for quick checks
    json_path = f"{summary_prefix}.json"
    try:
        with open(json_path, "w") as f:
            json.dump(by_date.to_dict(orient="records"), f, indent=2, default=str)
    except Exception as e:
        print("JSON export failed:", e)

    print(f"Wrote summary: {csv_path}")
    print(f"Wrote summary by method: {csv_by_m}")
    return csv_path
def main():
    args, extras = parse_args()
    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    ev_files = {}
    for m in methods:
        ev, pt, plot = run_method(args.script, args.csv, args.config, m, args.outdir,
                                  args.min_confidence, args.angle_between_min_deg,
                                  args.parallel_gap_max_atr, args.parallel_gap_max_pct, extras)
        ev_files[m] = ev
    if args.signals_summary_out:
        build_summary(ev_files, args.signals_summary_out)

if __name__ == "__main__":
    main()
