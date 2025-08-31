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
import argparse
import importlib.util
from .....TradingSignal.config.config_utils import method_params
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import subprocess
import  sys


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



def _build_args_from_config(config: dict,
                            overrides: dict | None,
                            method: str) -> argparse.Namespace:
    """
    Build final args with this precedence:
        overrides  >  config['methods'][method]  >  top-level config

    - Treat "" in the method block as "missing" so it doesn't clobber parent values.
    - Keeps it minimal; add casting elsewhere if you need strict types.
    """
    cfg = dict(config or {})

    # 1) top-level (exclude control keys)
    top = {k: v for k, v in cfg.items() if k not in ("methods", "methods_to_run")}

    # 2) method-level (wins over top-level)
    meth = (cfg.get("methods") or {}).get(method, {}) or {}
    meth = {k: v for k, v in meth.items() if not (isinstance(v, str) and v == "")}

    # 3) explicit overrides (highest)
    ov = {k: v for k, v in (overrides or {}).items() if v is not None and v != ""}

    merged = {}
    merged.update(top)
    merged.update(meth)
    merged.update(ov)

    return argparse.Namespace(**merged)


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
    parallel: bool = True,
    max_workers: Optional[int] = None,
    write_plots: bool = False,
    in_memory: bool = True,          # NEW: default to in-memory
    write_csv: bool = False          # NEW: keep disk off by default
) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    Run one or more methods on the given OHLCV DataFrame.
    Returns: dict like {method: {"events": DataFrame, "points": DataFrame}}
    """
    df_use = _ensure_cols(df)
    outroot = Path(outdir) if outdir else Path(tempfile.mkdtemp(prefix="tlc_out_"))
    outroot.mkdir(parents=True, exist_ok=True)

    # Write a temp CSV for the stream to read
    tmp_csv = outroot / "_input.csv"
    df_use.to_csv(tmp_csv, index=False)
    
    cfg_path = None
    if isinstance(config, dict):
        cfg_path = outroot / "_config.json"
        with open(cfg_path, "w") as f:
            json.dump(config, f)

    python_exec = sys.executable
    stream_script = str(main_stream_path)

    ms = _import_main_stream(main_stream_path)

    def _out_paths(method: str):
        ev_path = outroot / f"{method}_events.csv"
        pt_path = outroot / f"{method}_points.csv"
        plot_path = outroot / f"{method}.png"
        return ev_path, pt_path, plot_path

    def _build_cmd(method: str, ev_path: Path, pt_path: Path, plot_path: Path):
        cmd = [
            python_exec, stream_script,
            "--csv", str(tmp_csv),
            "--method", method,
            "--events", str(ev_path),
            "--points", str(pt_path),
            "--min-confidence", str(min_confidence),
        ]
        if cfg_path:
            cmd += ["--config", str(cfg_path)]
        if max_angle_deg is not None:
            cmd += ["--max-angle-deg", str(max_angle_deg)]
        if write_plots:
            cmd += ["--plot", str(plot_path)]
        return cmd

    # Avoid oversubscription when children use BLAS/OMP
    env = os.environ.copy()
    env.setdefault("OMP_NUM_THREADS", "1")
    env.setdefault("MKL_NUM_THREADS", "1")

    results: Dict[str, Dict[str, pd.DataFrame]] = {}


    def worker(method: str):
        ev_path, pt_path, plot_path = _out_paths(method)
        cmd = _build_cmd(method, ev_path, pt_path, plot_path)
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        if proc.returncode != 0:
            sys.stderr.write(f"[run_methods] {method} failed:\n{proc.stderr}\n")
        try:
            ev = pd.read_csv(ev_path)
        except Exception:
            ev = pd.DataFrame()
        try:
            pt = pd.read_csv(pt_path)
        except Exception:
            pt = pd.DataFrame()
        return method, ev, pt
    
    if parallel and len(methods) > 1:
        workers = max_workers or len(methods)
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(worker, m): m for m in methods}
            for fut in as_completed(futs):
                m = futs[fut]
                try:
                    meth, ev, pt = fut.result()
                except Exception as e:
                    sys.stderr.write(f"[run_methods] {m} raised: {e}\n")
                    ev, pt = pd.DataFrame(), pd.DataFrame()
                    meth = m
                results[meth] = {"events": ev, "points": pt}
    else:
        for m in methods:
            meth, ev, pt = worker(m)
            results[meth] = {"events": ev, "points": pt}

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
        return pd.DataFrame(columns=["date","BUY","SELL","TOTAL","CONFIDENCE"])

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
