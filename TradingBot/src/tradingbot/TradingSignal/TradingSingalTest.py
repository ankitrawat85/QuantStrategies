from __future__ import annotations

# Core / stdlib
import os
import sys

import json
from time import perf_counter
from concurrent.futures import ProcessPoolExecutor, as_completed

# Third-party
import pandas as pd
# Project imports
from tradingbot.TradingSignal.SignalGeneration.TechnicalIndicators.TrendLine.trendline_api import run_methods
from tradingbot.TradingSignal.PostSingalGeneration.CombinedSingals.combined_strength_api import (
    plot_candles_with_signals,
    summarize_breaks_min,
    get_combined_strength,
    get_combined_strength_from_snapshot,
    compute_snapshot_strength,
    plot_strength_timeseries,
    compute_strength_timeseries,
    StrengthParams,
    consolidate_buy_sell,
)
from tradingbot.Strategy.volume_confirmation import simple_volume_breaks
from tradingbot.Strategy.Technical_Analysis import CandlePatternRecognizer, TrendAnalyzer  # noqa: F401 (TrendAnalyzer kept for future use)
from tradingbot.trading_api.brokers.zerodha import ZerodhaAPI
from tradingbot.Strategy.momentum import calculate_momentum

# Pandas display (optional)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", 0)
pd.set_option("display.expand_frame_repr", False)

# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------
ROOT = os.environ.get("ZERODHA_ROOT", "/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot")
zerodhacfg = os.path.join(ROOT, "config", "Broker", "zerodha.cfg")
zerodha = ZerodhaAPI(zerodhacfg)

TLC_CONFIG_PATH = os.path.join(
    ROOT,
    "src",
    "tradingbot",
    "TradingSignal",
    "config",
    "tlc_config_methods.json",
)

MAIN_STREAM_PATH = os.path.join(
    ROOT,
    "src",
    "tradingbot",
    "TradingSignal",
    "SignalGeneration",
    "TechnicalIndicators",
    "TrendLine",
    "main_trendline_stream.py",
)

OUT_ROOT = "./out_sbin"

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def signal_generation(as_of_date: str, instrument_token: str | int, tradingsymbol: str, snapshot: bool = False):
    """
    Fetch recent OHLC and run trendline methods in-memory.
    Returns (results_dict, ohlc_df).
    """
    fetch_last_n = zerodha.make_fetcher_zerodha_last_n(
        root_dir=ROOT,
        instrument_token=instrument_token,
        default_interval="day",
        end_dt=as_of_date,
        n_bars=300,
    )

    # Normalize columns
    if "timestamp" in fetch_last_n.columns:
        fetch_last_n = fetch_last_n.rename(columns={"timestamp": "date"})
    if not pd.api.types.is_datetime64_any_dtype(fetch_last_n.get("date")):
        try:
            fetch_last_n["date"] = pd.to_datetime(fetch_last_n["date"])
        except Exception:
            pass

    # Load config
    cfg = json.load(open(TLC_CONFIG_PATH, "r"))
    fetch_last_n.to_csv('HAVELLS.csv')
    # Run methods fully in-memory
    results = run_methods(
        df=fetch_last_n,
        config=cfg,
        #methods=["huber"],
        methods=["ols", "ols_shift_min", "huber", "hough", "ols_envelop"],
        main_stream_path=MAIN_STREAM_PATH,
        min_confidence=0.40,
        parallel=True,           # across methods (internal)
        max_workers=None,        # defaults to len(methods)
        write_plots=False,       # keep off during batch
        outdir=os.path.join(OUT_ROOT, tradingsymbol),
    )
    return results, fetch_last_n


def _worker_symbol_block(payload: dict) -> dict:
    """
    Process a single symbol in its own process.
    Returns a dict with rows (for moreIndicators_df), png path (optional), and timing.
    """
    try:
        symbol = payload["symbol"]
        token = payload["instrument_token"]
        as_of_date = payload["as_of_date"]
        params: StrengthParams = payload["params"]
        plot_Graph = payload.get("plot_Graph", False)

        t0 = perf_counter()

        # 1) Generate raw signals + OHLC
        data, ohlc = signal_generation(as_of_date, token, symbol)

        # 2) Consolidate snapshot into strength_df
        out = consolidate_buy_sell(data, params)
        try:
            strength_df = out["strength_df"] if out.get("strength_df", None) is not None else out
        except Exception:
            strength_df = out
        strength_df["Symbol"] = symbol

        # 3) Summarize & persist per symbol
        out_dir = os.path.join(OUT_ROOT, symbol, "consolidated")
        summary = summarize_breaks_min(
            strength_df,
            method_weights={"ols": 1, "ols_shift_min": 1, "ols_envelop": 1, "huber": 1, "hough": 1},
            side_weights={"BUY": 1.0, "SELL": 1.0},
            save=True,
            out_dir=out_dir,
            basename="breaks",
        )

        # 4) Optional plot
        png_path = None
        if plot_Graph:
            _, _, png_path = plot_candles_with_signals(
                ohlc,
                summary,
                save=True,
                out_dir=out_dir,
                basename="breaks",
            )

        # 5) Event-level extras
        summary = summary.copy()
        summary["tradingsymbol"] = symbol

        rows = []
        for _, evrow in summary.iterrows():
            # short period (<= event date), long 7D aggregations
            _short = ohlc[ohlc["date"] <= evrow["date"]].copy()
            _short = _short.set_index("date")
            _short = _short.rename(
                columns={
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                }
            )
            long_idx = _short.index
            _long = pd.DataFrame(index=long_idx)
            _long["open"] = _short["open"].rolling("7D").apply(lambda x: x.iloc[0], raw=False)
            _long["high"] = _short["high"].rolling("7D").max()
            _long["low"] = _short["low"].rolling("7D").min()
            _long["close"] = _short["close"].rolling("7D").apply(lambda x: x.iloc[-1], raw=False)
            _long["volume"] = _short["volume"].rolling("7D").sum()

            pattern_info = CandlePatternRecognizer.identify_pattern(_short, _long)
            try:
                mom_series = calculate_momentum(_long["close"], lookback_months=7)
                momentum_val = float(mom_series.iloc[-1]) if len(mom_series) else None
            except Exception:
                momentum_val = None

            try:
                vol_breaks = simple_volume_breaks(_long[["volume"]])
                if hasattr(vol_breaks, "iloc"):
                    vol_val = vol_breaks.iloc[-1]
                    if hasattr(vol_val, "item"):
                        vol_val = vol_val.item()
                else:
                    vol_val = vol_breaks
            except Exception:
                vol_val = None

            row_out = evrow.to_dict()
            row_out["momentum"] = momentum_val
            row_out["significance"] = pattern_info.get("significance") if isinstance(pattern_info, dict) else None
            row_out["pattern"] = pattern_info.get("pattern") if isinstance(pattern_info, dict) else None
            row_out["simple_volume_breaks"] = vol_val
            rows.append(row_out)

        elapsed = perf_counter() - t0
        return {"symbol": symbol, "rows": rows, "summary_rows": len(rows), "png_path": png_path, "sec": elapsed}

    except Exception as e:
        return {
            "symbol": payload.get("symbol", "?"),
            "rows": [],
            "summary_rows": 0,
            "png_path": None,
            "sec": 0.0,
            "error": str(e),
        }


def run_user_block_parallel(get_quote_list_data_: list[dict], tickers: list[str], params: StrengthParams,
                            *, as_of_date: str = "2025-09-03", plot_Graph: bool = False, workers: int | None = None) -> pd.DataFrame:
    """
    Parallel wrapper: filters by tickers, processes symbols with ProcessPool, aggregates results.
    Returns the aggregated moreIndicators_df and writes ./out_sbin/Final_signals_test_later1.csv
    """
    # Build jobs
    jobs = []
    for row in get_quote_list_data_:
        try:
            if row["tradingsymbol"] in tickers:
                jobs.append(
                    {
                        "symbol": row["tradingsymbol"],
                        "instrument_token": row["instrument_token"],
                        "as_of_date": as_of_date,
                        "params": params,
                        "plot_Graph": plot_Graph,
                    }
                )
        except Exception:
            continue

    if not jobs:
        print("No matching symbols to process.")
        return pd.DataFrame()

    workers = workers or max(1, (os.cpu_count() or 1))
    print(f"Launching {len(jobs)} symbols across {workers} workers...")

    t_all = perf_counter()
    results = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_worker_symbol_block, payload=j) for j in jobs]
        for fut in as_completed(futs):
            results.append(fut.result())
    total_sec = perf_counter() - t_all
    print(f"Total parallel time: {total_sec:.3f}s")

    # Aggregate
    rows_all = []
    for r in results:
        if r.get("error"):
            print(f"[WARN] {r['symbol']}: {r['error']}")
        rows_all.extend(r.get("rows", []))

    moreIndicators_df = pd.DataFrame(rows_all)
    out_csv = os.path.join(OUT_ROOT, "Final_signals_test_later1.csv")
    if not moreIndicators_df.empty:
        os.makedirs(OUT_ROOT, exist_ok=True)
        moreIndicators_df.to_csv(out_csv, index=False)
        print(f"Saved moreIndicators_df: {out_csv} (rows: {len(moreIndicators_df)})")
    else:
        print("No rows produced (moreIndicators_df is empty).")
    return moreIndicators_df


# ---------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # Load universe
    csv_path = os.path.join(ROOT, "data", "masters", "zerodha_master_processed.csv")
    get_quote_list_data_ = zerodha.read_csv_to_dicts(csv_path)

    # Ticker filter (deduped)
    tickers = [
        "INFY", "BAJFINANCE","BHARTIARTL", "CIPLA", "WIPRO",
        "DRREDDY", "EICHERMOT", "GRASIM", "HCLTECH", "HDFCBANK",
        "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK",
        "INDUSINDBK", "ITC", "JSWSTEEL", "KOTAKBANK","COALINDIA",
        "LT", "M&M", "MARUTI", "NESTLEIND", "NTPC",
        "ONGC", "POWERGRID", "RELIANCE", "SBILIFE", "SBIN",
        "SHRIRAMFIN", "SUNPHARMA", "TATACONSUM", "TATAMOTORS", "TATASTEEL",
        "TCS", "TECHM", "TITAN", "ULTRACEMCO", "BEL",
         "TRENT", "JIOFIN", "ZOMATO",
    ]

    nifty_100 = [
        "HAVELLS",
        "CGPOWER",
        "UNITDSPR","ITC","BOSCHLTD","SHRIRAMFIN","BRITANNIA","BEL","DABUR","LT", 
        "ASIANPAINT","GAIL","DMART","TRENT","MOTHERSON","ULTRACEMCO","TATAPOWER","TVSMOTOR",
        "ADANIPOWER","KOTAKBANK","SUNPHARMA","HYUNDAI","SIEMENS","TATASTEEL","POWERGRID",
        "ZYDUSLIFE","CIPLA","HAVELLS","JIOFIN","BHARTIARTL","HINDALCO","HEROMOTOCO","HCLTECH",
        "MARUTI","BAJFINANCE","AMBUJACEM","HINDUNILVR","COALINDIA","SBIN","ETERNAL","ONGC","ABB",
        "LTIM","HAL","TATACONSUM","BAJAJFINSV","HDFCLIFE","ADANIPORTS","BANKBARODA","ICICIBANK",
        "GRASIM","GODREJCP","AXISBANK","TCS","DRREDDY","IRFC","TORNTPHARM","PNB","HDFCBANK",
        "BAJAJHFL","TITAN","EICHERMOT","PIDILITIND","PFC","WIPRO","SBILIFE","ADANIGREEN",
        "DIVISLAB","TECHM","BAJAJ-AUTO","BPCL","INDHOTEL","NESTLEIND","CANBK","INDUSINDBK",
        "LODHA","NTPC","VEDL","JSWSTEEL","TATAMOTORS","ADANIENSOL","ICICIGI","CHOLAFIN","IOC",
        "ADANIENT","SHREECEM","DLF","RECLTD","APOLLOHOSP","ICICIPRULI","JINDALSTEL","BAJAJHLDNG",
        "LICI","JSWENERGY","INDIGO","INFY","NAUKRI","RELIANCE","VBL","SWIGGY","M&M"
       ]

    # Strength params (tune as needed)
    params = StrengthParams(
        decay_lambda=0.12,
        decay_hold=0,
        decay_threshold=0.25,
        method_weights={"ols": 0.20, "ols_shift_min": 0.20, "ols_envelop": 0.20, "huber": 0.20, "hough": 0.20},
        add_percentage_cols=True,        # optional percent view (buy/sell/net *_pct)
        include_indicator_columns=True,  # per-method columns: ind_ols, ind_hough, ...
        indicator_column_prefix="ind_",  # prefix for indicator columns
        indicator_list_delim=",",        # delimiter for buy_indicators/sell_indicators
        calendar_index=None,
        apply_decay=False,
        write_plots=True,
    )

    # Run
    plot_Graph = True
    moreIndicators_df = run_user_block_parallel(
        get_quote_list_data_=get_quote_list_data_,
        tickers=nifty_100,
        params=params,
        as_of_date="2025-09-03",
        plot_Graph=False,
        workers= 20 #os.cpu_count(),   # set workers; adjust as needed
    )

    print("Aggregated rows:", len(moreIndicators_df))
