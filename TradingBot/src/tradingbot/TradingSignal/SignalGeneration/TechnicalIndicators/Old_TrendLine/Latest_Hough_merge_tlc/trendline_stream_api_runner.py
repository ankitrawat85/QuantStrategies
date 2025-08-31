#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
trendline_stream_api_runner.py
- Minimal CLI thin wrapper around trendline_api.run_methods
- Designed to be imported from your Zerodha data pipeline (e.g., TrendLineWrapper)
"""
import argparse, json, pandas as pd
from pathlib import Path
from trendline_api import run_methods, consolidate_buy_sell

def parse_args():
    p = argparse.ArgumentParser(description="Trendline API runner (slim)")
    p.add_argument("--main-stream", required=True, help="Path to main_trendline_stream.py")
    p.add_argument("--csv", required=True, help="Input prices CSV (date,open,high,low,close)")
    p.add_argument("--config", default="", help="Config JSON (merged defaults)")
    p.add_argument("--methods", default="ols", help="Comma-separated methods")
    p.add_argument("--min-confidence", type=float, default=0.0)
    p.add_argument("--angle-between-min-deg", type=float, default=None)
    p.add_argument("--parallel-gap-max-atr", type=float, default=None)
    p.add_argument("--parallel-gap-max-pct", type=float, default=None)
    p.add_argument("--outdir", default="", help="Optional output directory for artifacts")
    p.add_argument("--summary-out", default="", help="If set, write consolidated BUY/SELL CSV here")
    p.add_argument("--max-angle-deg", type=float, default=None)

    return p.parse_args()

def main():
    args = parse_args()
    df = pd.read_csv(args.csv)
    cfg = {}
    if args.config and Path(args.config).exists():
        with open(args.config, "r") as f:
            cfg = json.load(f)

    results = run_methods(
        df=df,
        config=cfg,
        methods=[m.strip() for m in args.methods.split(",") if m.strip()],
        main_stream_path=args.main_stream,
        min_confidence=args.min_confidence,
        angle_between_min_deg=args.angle_between_min_deg,
        parallel_gap_max_atr=args.parallel_gap_max_atr,
        parallel_gap_max_pct=args.parallel_gap_max_pct,
        max_angle_deg=args.max_angle_deg,outdir=args.outdir or None,
    )

    if args.summary_out:
        summary = consolidate_buy_sell(results)
        summary.to_csv(args.summary_out, index=False)
        print(f"Wrote consolidated BUY/SELL: {args.summary_out}")

if __name__ == "__main__":
    main()
