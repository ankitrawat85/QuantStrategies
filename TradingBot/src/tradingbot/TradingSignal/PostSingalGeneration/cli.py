
#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pandas as pd
from .CombinedSingals.core import apply_confidence, confidence_methods
from .SignalDecay.core import apply_decay_snapshot, expand_decay_timeseries, decay_methods

def parse_args():
    ap = argparse.ArgumentParser(description="Confidence & Decay pluggable runner")
    ap.add_argument("--events-csv", required=True, help="CSV with columns at least: date, side, price; optionally ref_px, atr, r2, distance, etc.")
    ap.add_argument("--confidence", default="identity", help=f"One of: {confidence_methods()}")
    ap.add_argument("--confidence-params", default="{}", help="JSON dict of params for confidence method")
    ap.add_argument("--decay", default="exp", help=f"One of: {decay_methods()}")
    ap.add_argument("--decay-params", default="{}", help="JSON dict of params for decay method")
    ap.add_argument("--calendar-csv", help="Optional CSV with a 'date' column to define trading calendar (or derive from events index)")
    ap.add_argument("--snapshot-date", help="If provided, compute decayed snapshot at this date (YYYY-MM-DD). Otherwise emit timeseries.")
    ap.add_argument("--out-prefix", default="./out/confdecay")
    return ap.parse_args()

def main():
    args = parse_args()
    ev = pd.read_csv(args.events_csv)
    if "date" in ev.columns:
        ev["date"] = pd.to_datetime(ev["date"])

    if args.calendar_csv:
        cal = pd.read_csv(args.calendar_csv)
        cal = pd.to_datetime(cal['date'])
    else:
        cal = pd.DatetimeIndex(sorted(ev['date'].unique()))

    conf_params = json.loads(args.confidence_params or "{}")
    dec_params = json.loads(args.decay_params or "{}")

    ev_conf = apply_confidence(ev, method=args.confidence, params=conf_params)

    if args.snapshot_date:
        out = apply_decay_snapshot(ev_conf, target_date=args.snapshot_date, method=args.decay, params=dec_params, calendar_index=cal)
        out.to_csv(f"{args.out_prefix}_snapshot.csv", index=False)
        print(f"Wrote snapshot: {args.out_prefix}_snapshot.csv")
    else:
        out = expand_decay_timeseries(ev_conf, calendar_index=cal, method=args.decay, params=dec_params)
        out.to_csv(f"{args.out_prefix}_timeseries.csv", index=False)
        print(f"Wrote timeseries: {args.out_prefix}_timeseries.csv")

if __name__ == "__main__":
    main()
