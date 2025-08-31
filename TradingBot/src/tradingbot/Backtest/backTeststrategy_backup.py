import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tradingbot.Strategy.consolidate_all_strategy import *
import inspect

# ---- PROJECT SETUP ----
ROOT_DIR = os.path.abspath('/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot')
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from tradingbot.trading_api.brokers.zerodha import ZerodhaAPI

# ---- INITIALIZE ----
zerodha = ZerodhaAPI(os.path.join(ROOT_DIR, "config", "Broker", "zerodha.cfg"))

# ---------- HELPERS ----------

class Position:
    def __init__(self, side: str, entry_price: float, entry_date: pd.Timestamp):
        self.side = side
        self.entry_price = entry_price
        self.entry_date = entry_date

def batch_n_day_from_end(
    df: pd.DataFrame,
    batch_size: int,
    timestamp_col: str = "timestamp",
    drop_partial: bool = False
) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    df = df.copy()
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    df = df.sort_values(timestamp_col).reset_index(drop=True)
    rev = df.iloc[::-1].reset_index(drop=True)
    groups = (np.arange(len(rev)) // batch_size)
    aggregated = []
    for group_id in np.unique(groups):
        group_df = rev[groups == group_id]
        if drop_partial and len(group_df) < batch_size:
            continue
        close_row = group_df.iloc[0]
        open_row = group_df.iloc[-1]
        aggregated.append({
            "timestamp": close_row[timestamp_col],
            "open": open_row["open"],
            "high": group_df["high"].max(),
            "low": group_df["low"].min(),
            "close": close_row["close"],
            "volume": group_df["volume"].sum(),
            "days_aggregated": len(group_df)
        })
    if not aggregated:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume", "days_aggregated"])
    result = pd.DataFrame(aggregated)
    result = result.sort_values("timestamp").reset_index(drop=True)
    return result

def batch_n_day_weekly_from_end(df: pd.DataFrame, batch_size: int = 5, **kwargs) -> pd.DataFrame:
    return batch_n_day_from_end(df, batch_size=batch_size, **kwargs)

def batch_n_day_monthly_from_end(df: pd.DataFrame, batch_size: int = 22, **kwargs) -> pd.DataFrame:
    return batch_n_day_from_end(df, batch_size=batch_size, **kwargs)

def load_minute_data(zerodha_api, token, start_date, end_date, minute=5):
    df = zerodha_api.get_historical_data(
        instrument_token=token,
        interval=f"{minute}minute",
        from_date=start_date,
        to_date=end_date,
        output_format='dataframe'
    ).reset_index(drop=True)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
    return df

def load_daily_data(zerodha_api, token, start_date, end_date):
    df = zerodha_api.get_historical_data(
        instrument_token=token,
        interval='day',
        from_date=start_date,
        to_date=end_date,
        output_format='dataframe'
    ).reset_index(drop=True)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
    return df

def print_strategy_performance(df: pd.DataFrame):
    if df.empty:
        print("No trades found.")
        return
    print("\n---- Per Stock Compounded Return ----")
    for symbol in df["Symbol"].unique():
        trades = df[df["Symbol"] == symbol].sort_values("BuyDate")
        cumulative = 1.0
        for r in trades["Return"]:
            cumulative *= (1 + r)
        stock_return = cumulative - 1
        print(f"{symbol}: {stock_return:.2%} ({len(trades)} trades)")
    print("\n---- Total Pipeline Return ----")
    df_sorted = df.sort_values("BuyDate")
    cumulative = 1.0
    for r in df_sorted["Return"]:
        cumulative *= (1 + r)
    total_return = cumulative - 1
    print(f"Total compounded return: {total_return:.2%}")

def summarize_returns(df: pd.DataFrame):
    if df.empty:
        print("No trade data.")
        return
    print("\n=== Return Summary per Chain ===")
    for chain in df["Chain"].dropna().unique():
        chain_df = df[df["Chain"] == chain]
        cumulative = 1.0
        for r in chain_df.sort_values("BuyDate")["Return"]:
            cumulative *= (1 + r)
        total_return = cumulative - 1
        print(f"Chain '{chain}': Compounded return: {total_return:.2%} over {len(chain_df)} trades")
        print(f"  -- Per symbol:")
        for symbol in chain_df["Symbol"].unique():
            trades = chain_df[chain_df["Symbol"] == symbol].sort_values("BuyDate")
            cum = 1.0
            for r in trades["Return"]:
                cum *= (1 + r)
            sym_return = cum - 1
            print(f"     {symbol}: {sym_return:.2%} ({len(trades)} trades)")

# ---------- STRATEGY STAGE ABSTRACTION ----------

@dataclass
class StrategyStage:
    name: str
    strategy_fn: Callable[..., Tuple[int, Any, float, bool]]  # signal, pattern, significance, pass_symbol
    precondition_fn: Optional[Callable[..., bool]] = None
    execute_trades: bool = True
    momentum_threshold: float = 0.04
    lookback_months: int = 3
    weekly_batch_size: int = 5
    monthly_batch_size: int = 22
    allow_multiple_positions_per_symbol: bool = True
    max_open_positions: int = 4
    include_today: bool = False
    extra_kwargs: Dict[str, Any] = field(default_factory=dict)

# ---------- STRATEGY IMPLEMENTATIONS ----------

def daily_momentum_filter(symbol, short_win, long_win, monthly_win, momentum_threshold, lookback_months, **kwargs):
    signal = 0; pattern = None; significance = 0.0; pass_symbol = False
    if len(short_win) >= 2:
        latest = short_win.iloc[-1]["close"]
        prev = short_win.iloc[-2]["close"]
        change = (latest - prev) / prev if prev != 0 else 0
        if change > momentum_threshold:
            signal = 1; significance = change; pass_symbol = True
    return signal, pattern, significance, pass_symbol

def confirmation_with_minute(symbol, short_win, long_win, monthly_win, minute_window=None, momentum_threshold=0.02, lookback_months=1, **kwargs):
    signal = 0; pattern = None; significance = 0.0; pass_symbol = False
    # daily/weekly trend confirmation
    if len(long_win) >= 2 and len(short_win) >= 1:
        weekly_latest = long_win.iloc[-1]["close"]
        weekly_prev = long_win.iloc[-2]["close"]
        if weekly_latest > weekly_prev:
            signal = 1
            significance = (weekly_latest - weekly_prev) / weekly_prev
            pass_symbol = True
    # require minute-level confirmation if minute_window provided
    if signal != 0 and minute_window is not None and len(minute_window) >= 15:
        minute_signal, _, minute_sig = generate_minute_trade_signal(symbol, minute_window, short_win)
        if minute_signal != signal:
            signal = 0
            pass_symbol = False
    return signal, pattern, significance, pass_symbol

def volatility_filter(symbol, short_win, long_win, monthly_win, momentum_threshold, lookback_months, **kwargs):
    signal = 0; pattern = None; significance = 0.0; pass_symbol = False
    if len(short_win) >= 5:
        vol = short_win["close"].pct_change().dropna().rolling(5).std().iloc[-1]
        if vol is not None and vol < 0.01:
            signal = 1; significance = float(vol); pass_symbol = True
    return signal, pattern, significance, pass_symbol

def mean_reversion_entry(symbol, short_win, long_win, monthly_win, momentum_threshold, lookback_months, **kwargs):
    signal = 0; pattern = None; significance = 0.0; pass_symbol = True
    if len(short_win) >= 10:
        close_series = short_win["close"]
        rolling_mean = close_series.rolling(10).mean().iloc[-1]
        latest = close_series.iloc[-1]
        if rolling_mean is not None and latest > rolling_mean * 1.005:
            signal = -1
            significance = (latest - rolling_mean) / rolling_mean
    return signal, pattern, significance, pass_symbol

def volume_precondition(symbol, short_win, long_win, monthly_win, **kwargs):
    if len(short_win) == 0:
        return False
    latest_vol = short_win.iloc[-1]["volume"]
    return latest_vol > 100_000

# ---------- MINUTE SIGNAL GENERATOR ----------

def generate_minute_trade_signal(symbol, minute_window: pd.DataFrame, short_window: pd.DataFrame):
    signal = 0; pattern = None; significance = 0.0
    if len(minute_window) < 15:
        return signal, pattern, significance
    close_series = minute_window["close"]
    rolling_mean = close_series.rolling(10).mean().iloc[-1]
    latest = close_series.iloc[-1]
    if rolling_mean is not None:
        if latest > rolling_mean * 1.002:
            signal = 1
            significance = (latest - rolling_mean) / rolling_mean
            pattern = "breakout"
        elif latest < rolling_mean * 0.998:
            signal = -1
            significance = (rolling_mean - latest) / rolling_mean
            pattern = "dip"
    return signal, pattern, significance

# ---------- BACKTEST ENGINE ----------

def run_multi_tf_backtest(
    tickers: dict,
    strategy,
    zerodha_api,
    start_date: str,
    end_date: str,
    minute_interval: int = 5,
    max_open_positions: int = 4,
    includeTodaysdate: bool = False,
    allow_multiple_positions_per_symbol: bool = True
):
    results = []
    signals_log = []
    open_positions: Dict[str, List[Position]] = {}

    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

    for token, symbol in tickers.items():
        try:
            minute_df = load_minute_data(zerodha_api, token, start_date, end_date, minute=minute_interval)
            master_daily_data = load_daily_data(
                zerodha_api,
                token,
                (start_dt - timedelta(days=300)).strftime("%Y-%m-%d"),
                end_date
            )

            daily_data = master_daily_data.loc[
                (master_daily_data["timestamp"] >= pd.to_datetime(start_date)) &
                (master_daily_data["timestamp"] <= pd.to_datetime(end_date))
            ].reset_index(drop=True)
            if daily_data.empty or minute_df.empty:
                continue

            weekly_df = batch_n_day_weekly_from_end(master_daily_data, batch_size=5)
            monthly_df = batch_n_day_monthly_from_end(master_daily_data, batch_size=22)
            if weekly_df.empty or monthly_df.empty:
                continue

            open_positions.setdefault(symbol, [])

            for i in range(len(daily_data)):
                curr_bar = daily_data.iloc[i]
                curr_time = curr_bar["timestamp"]

                def sliced(df_hist):
                    if includeTodaysdate:
                        return df_hist[df_hist["timestamp"] <= curr_time]
                    else:
                        return df_hist[df_hist["timestamp"] < curr_time]

                long_window = sliced(weekly_df)
                short_window = sliced(master_daily_data)
                monthly_window = sliced(monthly_df)
                day_minutes = minute_df[minute_df["timestamp"].dt.date == curr_time.date()]

                signal, pattern, significance, pass_symbol = strategy(
                    symbol,
                    short_window,
                    long_window,
                    monthly_window,
                    minute_window=day_minutes  # passed if supported
                )

                stage_obj = getattr(strategy, "__wrapped_stage__", None)
                precond_ok = True
                if stage_obj and stage_obj.precondition_fn:
                    precond_ok = stage_obj.precondition_fn(
                        symbol,
                        short_window,
                        long_window,
                        monthly_window,
                        momentum_threshold=stage_obj.momentum_threshold,
                        lookback_months=stage_obj.lookback_months,
                        **stage_obj.extra_kwargs
                    )

                signals_log.append({
                    "Type": "Daily",
                    "Date": curr_time,
                    "Symbol": symbol,
                    "Signal": signal,
                    "Pattern": pattern,
                    "Significance": significance,
                    "PassSymbol": pass_symbol,
                    "PreconditionOK": precond_ok,
                    "Stage": stage_obj.name if stage_obj else strategy.__name__
                })

                total_open = sum(len(v) for v in open_positions.values())
                can_take_new = total_open < max_open_positions
                if not allow_multiple_positions_per_symbol and open_positions[symbol]:
                    can_take_new = False

                # ENTRY logic: only if stage wants trades and signal + precondition + capacity
                if stage_obj and not stage_obj.execute_trades:
                    continue

                if can_take_new and signal in [1, -1] and precond_ok:
                    trade_taken = False
                    for idx, bar in day_minutes.iterrows():
                        minute_window = day_minutes.loc[:idx]
                        if len(minute_window) < 10:
                            continue

                        minute_signal, minute_pattern, minute_significance = generate_minute_trade_signal(
                            symbol, minute_window, short_window
                        )

                        signals_log.append({
                            "Type": "Minute",
                            "Date": curr_time,
                            "Symbol": symbol,
                            "Signal": minute_signal,
                            "Pattern": minute_pattern,
                            "Significance": minute_significance,
                            "PassSymbol": pass_symbol,
                            "PreconditionOK": precond_ok,
                            "Stage": stage_obj.name if stage_obj else strategy.__name__
                        })

                        if minute_signal == signal and not trade_taken:
                            side = "long" if signal == 1 else "short"
                            entry_price = bar["open"]
                            entry_date = bar["timestamp"]
                            open_positions[symbol].append(Position(side, entry_price, entry_date))
                            trade_taken = True
                            print(f"[{stage_obj.name if stage_obj else strategy.__name__}] {symbol} ENTRY {side.upper()} at {entry_price} on {entry_date}")
                            if not allow_multiple_positions_per_symbol:
                                break

                # EXIT logic
                to_close = []
                for pos in open_positions[symbol]:
                    close_position = False
                    if curr_time.date() == end_dt:
                        close_position = True
                    if (pos.side == "long" and signal == -1) or (pos.side == "short" and signal == 1):
                        close_position = True

                    if close_position:
                        last_day_minutes = minute_df[minute_df["timestamp"].dt.date == curr_time.date()]
                        if not last_day_minutes.empty:
                            exit_row = last_day_minutes.iloc[-1]
                            exit_price = exit_row["close"]
                            exit_date = exit_row["timestamp"]
                        else:
                            exit_price = curr_bar["close"]
                            exit_date = curr_bar["timestamp"]

                        if pos.side == "long":
                            ret = (exit_price - pos.entry_price) / pos.entry_price
                            side_str = "BUY"
                        else:
                            ret = (pos.entry_price - exit_price) / pos.entry_price
                            side_str = "SELL"

                        results.append({
                            "Strategy": stage_obj.name if stage_obj else strategy.__name__,
                            "Symbol": symbol,
                            "Side": side_str,
                            "BuyDate": pos.entry_date,
                            "BuyPrice": pos.entry_price,
                            "SellDate": exit_date,
                            "SellPrice": exit_price,
                            "Return": ret,
                            "Stage": stage_obj.name if stage_obj else strategy.__name__
                        })
                        to_close.append(pos)
                for closed in to_close:
                    open_positions[symbol].remove(closed)

        except Exception as e:
            print(f"Error for {symbol} in {strategy.__name__}: {e}")

    return pd.DataFrame(results), pd.DataFrame(signals_log)

# ---------- PIPELINE ORCHESTRATOR ----------

def make_wrapped(stage: StrategyStage):
    sig_params = inspect.signature(stage.strategy_fn).parameters
    def wrapped(symbol, short_window, long_window, monthly_window, **unused):
        kwargs = {
            "momentum_threshold": stage.momentum_threshold,
            "lookback_months": stage.lookback_months,
            **stage.extra_kwargs
        }
        # pass minute_window if expected
        if "minute_window" in sig_params:
            # pull from unused if provided (the caller passes it)
            if "minute_window" in unused:
                kwargs["minute_window"] = unused["minute_window"]
        sig, pattern, significance, pass_symbol = stage.strategy_fn(
            symbol, short_window, long_window, monthly_window, **kwargs
        )
        return sig, pattern, significance, pass_symbol
    wrapped.__wrapped_stage__ = stage
    return wrapped

def execute_chain(chain: List[StrategyStage], tickers: dict, zerodha_api, start_date: str, end_date: str, minute_interval: int):
    current_tickers = tickers.copy()
    chain_results = []
    chain_signals = []
    for stage in chain:
        print(f"\n--- Running stage {stage.name} ---")
        wrapped = make_wrapped(stage)
        result_df, signal_df = run_multi_tf_backtest(
            tickers=current_tickers,
            strategy=wrapped,
            zerodha_api=zerodha_api,
            start_date=start_date,
            end_date=end_date,
            minute_interval=minute_interval,
            max_open_positions=stage.max_open_positions,
            includeTodaysdate=stage.include_today,
            allow_multiple_positions_per_symbol=stage.allow_multiple_positions_per_symbol
        )
        if not result_df.empty:
            result_df["Stage"] = stage.name
        if not signal_df.empty:
            signal_df["Stage"] = stage.name

        chain_results.append(result_df)
        chain_signals.append(signal_df)

        if "PassSymbol" in signal_df.columns:
            survivors = set(signal_df[signal_df["PassSymbol"] == True]["Symbol"].unique())
        else:
            survivors = set(signal_df[signal_df["Signal"].abs() > 0]["Symbol"].unique())
        current_tickers = {tok: sym for tok, sym in current_tickers.items() if sym in survivors}
        if not current_tickers:
            print(f"No survivors after stage '{stage.name}'")
            break

    return pd.concat(chain_results, ignore_index=True) if chain_results else pd.DataFrame(), pd.concat(chain_signals, ignore_index=True) if chain_signals else pd.DataFrame()

def run_strategy_pipeline(
    tickers: dict,
    zerodha_api,
    start_date: str,
    end_date: str,
    chains: List[Tuple[str, List[StrategyStage]]],
    minute_interval: int = 5,
    run_mode: str = "sequential"  # "parallel" or "sequential"
):
    all_results = []
    all_signals = []

    if run_mode == "parallel":
        with ThreadPoolExecutor(max_workers=len(chains)) as executor:
            future_to_chain_name = {
                executor.submit(execute_chain, chain, tickers, zerodha_api, start_date, end_date, minute_interval): chain_name
                for chain_name, chain in chains
            }
            for future in as_completed(future_to_chain_name):
                chain_name = future_to_chain_name[future]
                res_df, sig_df = future.result()
                if not res_df.empty:
                    res_df["Chain"] = chain_name
                    all_results.append(res_df)
                if not sig_df.empty:
                    sig_df["Chain"] = chain_name
                    all_signals.append(sig_df)
    else:  # sequential
        for chain_name, chain in chains:
            res_df, sig_df = execute_chain(chain, tickers, zerodha_api, start_date, end_date, minute_interval)
            if not res_df.empty:
                res_df["Chain"] = chain_name
                all_results.append(res_df)
            if not sig_df.empty:
                sig_df["Chain"] = chain_name
                all_signals.append(sig_df)

    combined_results = pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()
    combined_signals = pd.concat(all_signals, ignore_index=True) if all_signals else pd.DataFrame()
    return combined_results, combined_signals

# ---------- MAIN ----------

if __name__ == "__main__":
    file_path = os.path.join(ROOT_DIR, "data", "masters", "large_cap_stocks.csv")
    tickers_df = zerodha.read_csv_to_dataframe(file_path)
    tickers = dict(zip(tickers_df['instrument_token'], tickers_df['tradingsymbol']))

    start_date = '2025-06-01'
    end_date = '2025-06-30'

    # Chain A: momentum filter (filter-only) -> confirmation with minute verification (trade)
    chain_a = [
        StrategyStage(
            name="WeeklyPatternFilter",
            strategy_fn=generate_trade_signal_stage,
            precondition_fn=None,
            execute_trades=False,
            momentum_threshold=0.03,
            lookback_months=2,
            max_open_positions=10,
            allow_multiple_positions_per_symbol=False,
            include_today=False
        ),
        StrategyStage(
            name="ConfirmWithMinute",
            strategy_fn=confirmation_with_minute,
            precondition_fn=volume_precondition,
            execute_trades=True,
            momentum_threshold=0.02,
            lookback_months=1,
            max_open_positions=4,
            allow_multiple_positions_per_symbol=True,
            include_today=True
        )
    ]

    # Chain B: volatility filter (filter-only) -> mean reversion entry (trade)
    chain_b = [
        StrategyStage(
            name="VolatilityFilter",
            strategy_fn=volatility_filter,
            precondition_fn=None,
            execute_trades=False,
            momentum_threshold=0.0,
            lookback_months=2,
            max_open_positions=10,
            allow_multiple_positions_per_symbol=False,
            include_today=False
        ),
        StrategyStage(
            name="MeanReversionEntry",
            strategy_fn=mean_reversion_entry,
            precondition_fn=None,
            execute_trades=True,
            momentum_threshold=0.0,
            lookback_months=1,
            max_open_positions=3,
            allow_multiple_positions_per_symbol=True,
            include_today=True
        )
    ]

    chains = [
        ("WeeklyPatternFilter→MinuteConfirm", chain_a),
        ("Volatility→MeanReversion", chain_b)
    ]

    combined_results, combined_signals = run_strategy_pipeline(
        tickers=tickers,
        zerodha_api=zerodha,
        start_date=start_date,
        end_date=end_date,
        chains=chains,
        minute_interval=5,
        run_mode="parallel"  # or "sequential"
    )

    os.makedirs(os.path.join(ROOT_DIR, "data", "output"), exist_ok=True)
    combined_signals.to_csv(os.path.join(ROOT_DIR, "data", "output", "pipeline_signals.csv"), index=False)
    combined_results.to_csv(os.path.join(ROOT_DIR, "data", "output", "pipeline_results.csv"), index=False)

    print_strategy_performance(combined_results)
    summarize_returns(combined_results)