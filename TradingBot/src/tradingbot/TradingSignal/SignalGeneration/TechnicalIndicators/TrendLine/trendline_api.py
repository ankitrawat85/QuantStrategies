"""
trendline_api.py — in-memory runner for trendline methods
---------------------------------------------------------
This module lets you execute your trendline pipeline entirely **in memory**,
with an optional switch to write CSVs. It loads your existing
`main_trendline_stream.py` and calls its `stream()` directly, passing a
DataFrame instead of forcing CSV I/O.

Public API
----------
- run_methods(df, config, methods, main_stream_path, ..., write_csv=False)
- run_single_method(...)

Return shape
------------
{
  "<method>": {
      "events":  pd.DataFrame,
      "points":  pd.DataFrame,
      "snapshot": pd.DataFrame (if provided by main)
  },
  ...
}

Assumptions
-----------
Your `main_trendline_stream.py` was patched as recommended:
- build_parser(defaults=None) -> argparse.ArgumentParser
- stream(args, df_in=None) -> returns {"events":..., "points":..., "snapshot":...} if args.return_results
- (optional) merge_config_with_method(cfg, argv_like) -> dict defaults

If some helper is missing, this module falls back gracefully with reasonable defaults.
"""

from __future__ import annotations

import argparse
import json
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

import importlib.util
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from time import perf_counter


__all__ = ["run_methods", "run_single_method"]


# -------------------------
# Utilities
# -------------------------

def _load_module_from_path(py_path: Union[str, Path]):
    """Dynamically import a Python module from a file path."""
    py_path = str(py_path)
    spec = importlib.util.spec_from_file_location("tlc_main", py_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {py_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    return module


def _coerce_config(config: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
    """Accept dict or JSON filepath and return a dict."""
    if isinstance(config, (str, Path)):
        with open(config, "r") as f:
            return json.load(f)
    elif isinstance(config, dict):
        return config
    else:
        raise TypeError("config must be a dict or path to a JSON file")


def _merge_top_and_method_cfg(cfg: Dict[str, Any], method: str) -> Dict[str, Any]:
    """
    Merge top-level config with per-method overrides if present.
    Expected shapes supported:
      - {"methods": {"ols": {...}, "huber": {...}}, <top-level keys...>}
      - {"method_overrides": {...}}
      - or flat dicts with no per-method blocks.
    Per-method keys win.
    """
    out = dict(cfg)
    for block_key in ("methods", "method_overrides"):
        if isinstance(cfg.get(block_key), dict) and isinstance(cfg[block_key].get(method), dict):
            out.update(cfg[block_key][method])
    return out


def _ensure_df(df: pd.DataFrame) -> pd.DataFrame:
    """Make a shallow copy and ensure DateTime ordering if 'date' present."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    out = df.copy()
    # common column casing tolerance
    for c in list(out.columns):
        if c.strip().lower() == "date" and not pd.api.types.is_datetime64_any_dtype(out[c]):
            # try auto-parse
            try:
                out[c] = pd.to_datetime(out[c])
            except Exception:
                pass
    # sort if date exists
    date_cols = [c for c in out.columns if c.strip().lower() == "date"]
    if date_cols:
        out = out.sort_values(by=date_cols[0])
    return out


@dataclass
class RunOptions:
    main_stream_path: Union[str, Path]
    config: Union[str, Path, Dict[str, Any]]
    write_csv: bool = False
    write_plots: bool = False
    outdir: Optional[Union[str, Path]] = None
    min_confidence: Optional[float] = None
    max_angle_deg: Optional[float] = None
    parallel: bool = True
    max_workers: Optional[int] = None
    extra_overrides: Dict[str, Any] = field(default_factory=dict)


def _prepare_args_for_method(
    tlc_main,
    cfg: Dict[str, Any],
    method: str,
    run_opts: RunOptions,
) -> argparse.Namespace:
    """
    Build an argparse.Namespace compatible with tlc_main.stream().
    We try in this order:
      1) Use tlc_main.merge_config_with_method(cfg, ["--method", method]) if available
      2) Fall back to merging top-level + per-method config, then use tlc_main.build_parser(defaults)
      3) As a last resort, create a minimal Namespace with expected attributes
    """
    defaults = None
    merged_cfg = _merge_top_and_method_cfg(cfg, method)

    # try #1: module-provided merger for defaults
    if hasattr(tlc_main, "merge_config_with_method"):
        try:
            defaults = tlc_main.merge_config_with_method(cfg, ["--method", method])  # type: ignore
        except Exception:
            defaults = None

    # try #2: build parser with defaults
    if hasattr(tlc_main, "build_parser"):
        try:
            parser = tlc_main.build_parser(defaults or merged_cfg)  # type: ignore
            # Parse empty argv to take defaults; then apply overrides we care about here
            args = parser.parse_args([])

            # Enforce method & critical behavior overrides
            # Input: in-memory, so clear CSV path
            setattr(args, "method", method)
            setattr(args, "csv", "")
            setattr(args, "events", "")
            setattr(args, "points", "")
            setattr(args, "snapshot_out", "")
            setattr(args, "write_csv", bool(run_opts.write_csv))
            setattr(args, "return_results", True)

            # Optional: plotting
            if run_opts.write_plots and run_opts.outdir:
                Path(run_opts.outdir).mkdir(parents=True, exist_ok=True)
                setattr(args, "plot", str(Path(run_opts.outdir) / f"{method}.png"))
            else:
                # Keep whatever default parser had; if none, ensure empty string
                if not getattr(args, "plot", ""):
                    setattr(args, "plot", "")

            # Optional specific overrides if provided
            if run_opts.min_confidence is not None:
                setattr(args, "min_confidence", run_opts.min_confidence)
            if run_opts.max_angle_deg is not None:
                setattr(args, "max_angle_deg", run_opts.max_angle_deg)

            # Any extra key->value overrides the caller wants to force
            for k, v in (run_opts.extra_overrides or {}).items():
                setattr(args, k, v)

            return args
        except Exception:
            pass

    # try #3: minimal namespace with commonly used fields
    ns = argparse.Namespace()
    # Required/important knobs
    setattr(ns, "method", method)
    setattr(ns, "csv", "")
    setattr(ns, "events", "")
    setattr(ns, "points", "")
    setattr(ns, "snapshot_out", "")
    setattr(ns, "write_csv", bool(run_opts.write_csv))
    setattr(ns, "return_results", True)
    # Optional
    setattr(ns, "plot", str(Path(run_opts.outdir) / f"{method}.png") if (run_opts.write_plots and run_opts.outdir) else "")
    if run_opts.min_confidence is not None:
        setattr(ns, "min_confidence", run_opts.min_confidence)
    if run_opts.max_angle_deg is not None:
        setattr(ns, "max_angle_deg", run_opts.max_angle_deg)
    for k, v in (run_opts.extra_overrides or {}).items():
        setattr(ns, k, v)

    return ns


def run_single_method(
    df: pd.DataFrame,
    config: Union[str, Path, Dict[str, Any]],
    method: str,
    main_stream_path: Union[str, Path],
    *,
    write_csv: bool = False,
    write_plots: bool = False,
    outdir: Optional[Union[str, Path]] = None,
    min_confidence: Optional[float] = None,
    max_angle_deg: Optional[float] = None,
    extra_overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, pd.DataFrame]:
    """
    Run a single method in-memory and return its dataframes.
    """
    tlc_main = _load_module_from_path(main_stream_path)
    cfg = _coerce_config(config)
    df_use = _ensure_df(df)

    run_opts = RunOptions(
        main_stream_path=main_stream_path,
        config=cfg,
        write_csv=write_csv,
        write_plots=write_plots,
        outdir=outdir,
        min_confidence=min_confidence,
        max_angle_deg=max_angle_deg,
        extra_overrides=extra_overrides or {},
    )

    args = _prepare_args_for_method(tlc_main, cfg, method, run_opts)

    # stream(...) MUST support df_in per the recommended patch
    res = tlc_main.stream(args, df_in=df_use)  # type: ignore

    # Normalize shape of return
    out = {
        "events": res.get("events", pd.DataFrame()),
        "points": res.get("points", pd.DataFrame()),
    }
    if isinstance(res, dict) and "snapshot" in res:
        out["snapshot"] = res.get("snapshot", pd.DataFrame())
    return out


def run_methods(
    df: pd.DataFrame,
    config: Union[str, Path, Dict[str, Any]],
    methods: List[str],
    main_stream_path: Union[str, Path],
    *,
    write_csv: bool = False,
    write_plots: bool = False,
    outdir: Optional[Union[str, Path]] = None,
    min_confidence: Optional[float] = None,
    max_angle_deg: Optional[float] = None,
    parallel: bool = True,
    max_workers: Optional[int] = None,
    extra_overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    Execute multiple methods (OLS, Huber, Hough, etc.) entirely in memory.

    Parameters
    ----------
    df : DataFrame
        OHLC(V) data. Column names are not enforced but should match your main script's expectations.
    config : dict or path
        JSON-like config (either dict or path to .json).
    methods : list[str]
        E.g. ["ols", "ols_shift_min", "ols_envelop", "huber", "hough"]
    main_stream_path : str or Path
        Filesystem path to your patched `main_trendline_stream.py`.

    Optional kwargs
    ---------------
    write_csv : bool
        If True, will write CSVs (events/points/snapshot) IF your main stream script supports it and paths are set.
        Default False.
    write_plots : bool
        If True and outdir provided, each method can write a plot image.
    outdir : str|Path|None
        Where to save plots; created if missing.
    min_confidence, max_angle_deg : Optional[float]
        Passed through to your main stream if available.
    parallel : bool
        Run methods concurrently. Default True.
    max_workers : Optional[int]
        Thread pool workers; defaults to len(methods) if None.
    extra_overrides : Dict[str, Any] | None
        Additional attributes forced onto the argparse Namespace for your main stream.

    Returns
    -------
    dict[method] -> {"events": DataFrame, "points": DataFrame, "snapshot": DataFrame (optional)}
    """
    tlc_main = _load_module_from_path(main_stream_path)
    cfg = _coerce_config(config)
    df_use = _ensure_df(df)

    results: Dict[str, Dict[str, pd.DataFrame]] = {}

    def _do(method: str) -> Tuple[str, Dict[str, pd.DataFrame]]:
        try:
            res = run_single_method(
                df=df_use,
                config=cfg,
                method=method,
                main_stream_path=main_stream_path,
                write_csv=write_csv,
                write_plots=write_plots,
                outdir=outdir,
                min_confidence=min_confidence,
                max_angle_deg=max_angle_deg,
                extra_overrides=extra_overrides,
            )
            return method, res
        except Exception as e:
            traceback.print_exc()
            return method, {"events": pd.DataFrame(), "points": pd.DataFrame()}

    if parallel and len(methods) > 1:
        workers = max_workers or max(1, len(methods))
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(_do, m): m for m in methods}
            for fut in as_completed(futs):
                m = futs[fut]
                _, res = fut.result()
                results[m] = res
    else:
        for m in methods:
            _, res = _do(m)
            results[m] = res

    return results



def _worker_run_symbol(payload):
    """
    Top-level (pickleable) worker for ProcessPool.
    payload = {
        'symbol': str,
        'df_json': str (DataFrame.to_json orient='records'),
        'config': dict|path,
        'methods': list[str],
        'main_stream_path': str|Path,
        'write_csv': bool,
        'write_plots': bool,
        'outdir': str|Path|None,
        'min_confidence': float|None,
        'max_angle_deg': float|None,
        'per_symbol_method_parallel': bool,
        'max_workers_methods': int|None,
        'extra_overrides': dict|None,
    }
    """
    import pandas as pd
    from pathlib import Path
    symbol = payload["symbol"]
    df = pd.read_json(payload["df_json"], orient="records")
    t0 = perf_counter()
    res = run_methods(  # uses the in-memory runner you already have
        df=df,
        config=payload["config"],
        methods=payload["methods"],
        main_stream_path=payload["main_stream_path"],
        write_csv=payload["write_csv"],
        write_plots=payload["write_plots"],
        outdir=Path(payload["outdir"]) if payload["outdir"] else None,
        min_confidence=payload["min_confidence"],
        max_angle_deg=payload["max_angle_deg"],
        parallel=bool(payload["per_symbol_method_parallel"]),
        max_workers=payload["max_workers_methods"],
        extra_overrides=payload.get("extra_overrides"),
    )
    elapsed = perf_counter() - t0
    return symbol, res, elapsed


def run_symbols(
    symbol_dfs: dict,
    *,
    config,
    methods,
    main_stream_path,
    workers: int | None = None,
    use_processes: bool = True,
    per_symbol_method_parallel: bool = False,
    max_workers_methods: int | None = None,
    write_csv: bool = False,
    write_plots: bool = False,
    outdir: str | None = None,
    min_confidence: float | None = None,
    max_angle_deg: float | None = None,
    extra_overrides: dict | None = None,
):
    """
    Parallel orchestrator across symbols.

    Recommendations:
      - Set `use_processes=True` for CPU-bound work (NumPy releases GIL often, but this is safest).
      - Keep `per_symbol_method_parallel=False` to avoid N_symbols × N_methods thread explosion.
      - Keep `write_csv=False` to prevent file collisions; plots also off for big batches.
    """
    import pandas as pd
    from math import ceil
    workers = workers or max(1, os.cpu_count() or 1)
    Executor = ProcessPoolExecutor if use_processes else ThreadPoolExecutor

    # Serialize DataFrames so payload is pickle-safe & small(ish)
    jobs = []
    for sym, df in symbol_dfs.items():
        df_use = df.copy()
        if "Symbol" not in df_use.columns:
            df_use["Symbol"] = sym
        jobs.append({
            "symbol": sym,
            "df_json": df_use.to_json(orient="records"),
            "config": config,
            "methods": list(methods),
            "main_stream_path": str(main_stream_path),
            "write_csv": bool(write_csv),
            "write_plots": bool(write_plots),
            "outdir": outdir,
            "min_confidence": min_confidence,
            "max_angle_deg": max_angle_deg,
            "per_symbol_method_parallel": bool(per_symbol_method_parallel),
            "max_workers_methods": max_workers_methods,
            "extra_overrides": extra_overrides or {},
        })

    results_by_symbol = {}
    timings = {}
    t_all = perf_counter()

    with Executor(max_workers=workers) as ex:
        futs = [ex.submit(_worker_run_symbol, payload=j) for j in jobs]
        for fut in futs:
            sym, res, sec = fut.result()
            results_by_symbol[sym] = res
            timings[sym] = sec

    timings["__total__"] = perf_counter() - t_all
    return results_by_symbol, timings


def concat_symbol_results(results_by_symbol: dict, which: str = "events"):
    """
    Flatten {symbol -> {method -> {'events','points',...}}} into a single DataFrame.
    which: 'events' | 'points' | 'snapshot'
    """
    import pandas as pd
    frames = []
    for sym, by_method in results_by_symbol.items():
        for method, payload in by_method.items():
            df = payload.get(which)
            if df is None or df is ...:
                continue
            if not isinstance(df, pd.DataFrame) or df.empty:
                continue
            tmp = df.copy()
            if "Symbol" not in tmp.columns:
                tmp["Symbol"] = sym
            if "method" not in tmp.columns:
                tmp["method"] = method
            frames.append(tmp)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
