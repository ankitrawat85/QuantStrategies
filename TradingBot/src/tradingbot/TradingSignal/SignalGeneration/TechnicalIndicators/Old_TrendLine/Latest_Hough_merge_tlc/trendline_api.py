#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
trendline_api.py
A clean API to run the trendline streamer on in-memory OHLCV data (e.g., from Zerodha).

Key entrypoints:
- run_methods(df, config, methods, **kwargs) -> dict per method with events/points DataFrames
- consolidate_buy_sell(results) -> DataFrame [date, BUY, SELL, TOTAL]
- snapshot_at(results, snapshot_date) -> one-row summary at a given date (latest if None)

Notes:
- We call the existing main_trendline_stream.stream(args) to avoid duplicating core logic.
- We write the input df to a temp CSV (expected by stream) and read back events/points.
- "BUY" is mapped from resistance breaks (side == "R"); "SELL" from support breaks (side == "S").
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
import argparse
import json
import tempfile
import os
from pathlib import Path
import importlib.util

# --------- Utilities ---------
def _import_main_stream(path: str):
    spec = importlib.util.spec_from_file_location("main_trendline_stream", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def _to_temp_csv(df: pd.DataFrame, suffix: str = "prices") -> str:
    fd, p = tempfile.mkstemp(prefix=f"tlc_{suffix}_", suffix=".csv")
    os.close(fd)
    df.to_csv(p, index=False)
    return p

def _ensure_cols(df: pd.DataFrame) -> pd.DataFrame:
    need = ["date","open","high","low","close"]
    # try to coerce/rename common casing
    rename = {c: c.lower() for c in df.columns}
    df2 = df.rename(columns=rename)
    for c in need:
        if c not in df2.columns:
            raise ValueError(f"Input DataFrame must contain columns: {need}; missing '{c}'")
    # Ensure datetime
    df2["date"] = pd.to_datetime(df2["date"], errors="coerce")
    return df2[["date","open","high","low","close"]].copy()

def _build_args_from_config(config: dict, overrides: dict) -> argparse.Namespace:
    # Flatten config (top-level + method block assumed already merged by caller if needed)
    print("testiig",config,overrides)
    cfg = dict(config)
    cfg.update(overrides or {})
    return argparse.Namespace(**cfg)

def _default_overrides(method: str,
                       events_path: str,
                       points_path: str,
                       plot_path: str,
                       min_confidence: float) -> dict:
    d = {
        "csv": None,              # will be set per-run
        "events": events_path,
        "points": points_path,
        "plot": plot_path,
        "method": method,
        "min_confidence": min_confidence,
        "snapshot_date": "",
        "snapshot_out": "",
        "snapshot_only": False,
    }
    return d

# --------- Public API ---------
def run_methods(
    df: pd.DataFrame,
    config: dict,
    methods: List[str],
    main_stream_path: str,
    min_confidence: float = 0.0,
    outdir: Optional[str] = None,
    max_angle_deg: Optional[float] = None,
) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    Run one or more methods on the given OHLCV DataFrame.
    Returns: dict like {method: {"events": DataFrame, "points": DataFrame}}
    """
    df_use = _ensure_cols(df)
    outroot = Path(outdir) if outdir else Path(tempfile.mkdtemp(prefix="tlc_out_"))
    outroot.mkdir(parents=True, exist_ok=True)

    ms = _import_main_stream(main_stream_path)

    results: Dict[str, Dict[str, pd.DataFrame]] = {}
    for method in methods:
        prices_csv = _to_temp_csv(df_use, suffix=f"{method}")
        ev_path = str(outroot / f"events_{method}.csv")
        pt_path = str(outroot / f"points_{method}.csv")
        plot_path = str(outroot / f"plot_{method}.png")

        overrides = _default_overrides(method, ev_path, pt_path, plot_path,
                                       min_confidence)
        overrides["csv"] = prices_csv
        if max_angle_deg is not None:
            overrides["max_angle_deg"] = max_angle_deg

        # Build args: let main_trendline_stream handle defaults for windows/etc.
        args = _build_args_from_config(config or {}, overrides)

        # Execute
        ms.stream(args)

        # Read outputs
        try:
            ev = pd.read_csv(ev_path)
        except Exception:
            ev = pd.DataFrame()
        try:
            pt = pd.read_csv(pt_path)
        except Exception:
            pt = pd.DataFrame()

        results[method] = {"events": ev, "points": pt}

    return results

def consolidate_buy_sell(results: Dict[str, Dict[str, pd.DataFrame]]) -> pd.DataFrame:
    """
    Map events to BUY/SELL per date across methods.
    BUY  := side == 'R' (resistance break)
    SELL := side == 'S' (support break)
    Returns DataFrame [date, BUY, SELL, TOTAL]
    """
    frames = []
    for method, dct in results.items():
        ev = dct.get("events", pd.DataFrame())
        if ev is None or ev.empty: 
            continue
        df = ev.copy()
        if "event" in df.columns:
            df = df[df["event"].astype(str).str.lower().eq("break")]
        # Normalise date and side
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        else:
            continue
        side_col = None
        for c in df.columns:
            if c.lower() == "side":
                side_col = c; break
        if side_col is None:
            continue
        # Map to signal
        df["signal"] = df[side_col].map(lambda s: "BUY" if str(s).upper()=="R" else ("SELL" if str(s).upper()=="S" else None))
        df = df[df["signal"].notna()]
        frames.append(df[["date","signal"]])

    if not frames:
        return pd.DataFrame(columns=["date","BUY","SELL","TOTAL"])

    all_ev = pd.concat(frames, ignore_index=True)
    by_date = (all_ev.groupby(["date","signal"]).size().unstack(fill_value=0).reset_index())
    for col in ("BUY","SELL"):
        if col not in by_date.columns:
            by_date[col] = 0
    by_date["TOTAL"] = by_date["BUY"] + by_date["SELL"]
    return by_date.sort_values("date").reset_index(drop=True)

def snapshot_at(results: Dict[str, Dict[str, pd.DataFrame]], snapshot_date: Optional[str]=None) -> pd.DataFrame:
    """
    Very light helper: get latest signal on or before snapshot_date (or last available)
    per method by scanning events dataframes. Returns rows with columns [date, method, side, price, confidence].
    """
    rows = []
    snap = pd.to_datetime(snapshot_date).date() if snapshot_date else None
    for method, dct in results.items():
        ev = dct.get("events", pd.DataFrame())
        if ev is None or ev.empty: 
            continue
        df = ev.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        df = df.sort_values("date")
        if snap:
            df = df[df["date"] <= snap]
        if df.empty: 
            continue
        last = df.iloc[-1]
        rows.append({
            "method": method,
            "date": last["date"],
            "side": last.get("side", None),
            "price": float(last.get("price", float("nan"))),
            "confidence": float(last.get("confidence", float("nan"))),
        })
    return pd.DataFrame(rows)
