import os
import pandas as pd
from typing import List, Dict
from datetime import datetime
import sys
import os
from pathlib import Path
from typing import List


# Set project root
ROOT_DIR = os.path.abspath('/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot')
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)
print("ROOT_DIR:", ROOT_DIR)

# Imports
#from tradingbot.Strategy.Technical_Analysis import CandlePatternRecognizer, TrendAnalyzer
from tradingbot.trading_api.brokers.zerodha import ZerodhaAPI
#from tradingbot.Strategy.momentum import calculate_momentum
#from tradingbot.API.nseSymbolCategory import read_symbol
from tradingbot.Strategy.consolidate_all_strategy import *


zerodha = ZerodhaAPI(os.path.join(ROOT_DIR, "config", "Broker", "zerodha.cfg"))
from datetime import timedelta
import pandas as pd

def load_daily_data(zerodha_api, token, start_date, end_date):
    df = zerodha_api.get_historical_data(
        instrument_token=token,
        interval='5minute',
        from_date=start_date,
        to_date=end_date,
        output_format='dataframe'
    ).reset_index(drop=True)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
    return df

def load_weekly_data(zerodha_api, token, start_date, end_date):
    df = zerodha_api.get_historical_data(
        instrument_token=token,
        interval='day',
        from_date=start_date,
        to_date=end_date,
        output_format='dataframe'
    ).reset_index(drop=True)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
    return df

def get_last_long_tf_bar(ts, longer_df):
    """Return the most recent bar in longer_df whose timestamp is <= ts."""
    idx = longer_df[longer_df['timestamp'] <= ts].index
    if len(idx) == 0:
        return None
    return longer_df.loc[idx[-1]]

def run_multi_tf_backtest(
    tickers: dict,
    strategy,
    zerodha_api,
    start_date: str,
    end_date: str,
    min_lookback_days: int = 250,
    long_window: int = 10,   # e.g., how many weekly bars to pass for context
    short_window: int = 30   # e.g., how many daily bars to pass for context
):
    results = []
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)

    for token, symbol in tickers.items():
        try:
            # Load data
            short_df = load_daily_data(zerodha_api, token, start_date, end_date)
            long_df = load_weekly_data(zerodha_api, token, start_date, end_date)

            short_df_history = load_daily_data(zerodha_api,token,(short_df['timestamp'].iloc[:1] - timedelta(days=min_lookback_days))[0].strftime("%Y-%m-%d"), end_date)

            long_df_history = load_weekly_data(zerodha_api,token,(long_df['timestamp'].iloc[:1] - timedelta(days=min_lookback_days))[0].strftime("%Y-%m-%d"), end_date)

            if short_df.empty or long_df.empty or short_df_history.empty or long_df_history.empty:
                continue

            position = None
            entry_price = entry_date = entry_index = None

            # Loop over every daily bar (shorter timeframe)
            for i in range(0, len(short_df)):
                curr_bar = short_df.iloc[i]
                curr_time = curr_bar['timestamp']

                # Find latest completed weekly bar for this daily bar
                last_long_idx = long_df[long_df['timestamp'] <= curr_time].index
                if len(last_long_idx) == 0:
                    continue
                last_week_bar = long_df.loc[last_long_idx[-1]]

                # Get lookback windows (can adjust window size as needed)

                short_window =  short_df_history[short_df_history['timestamp'] <= curr_time]
                long_window  = long_df_history[long_df_history['timestamp'] <= curr_time]

                # Generate signal: pass symbol, daily window, weekly window, last completed weekly bar
                signal = strategy(symbol, short_window, long_window)

                # ---- Position Management Logic ----
                if signal == 1:
                    if position == 'short':
                        # Close short, open long
                        exit_price = curr_bar['open']
                        exit_date = curr_bar['timestamp']
                        returns = (entry_price - exit_price) / entry_price
                        results.append({
                            "Strategy": strategy,
                            "Symbol": symbol,
                            "Side": "SELL",
                            "BuyDate": entry_date,
                            "BuyPrice": entry_price,
                            "SellDate": exit_date,
                            "SellPrice": exit_price,
                            "Return": returns
                        })
                        position = 'long'
                        entry_price = exit_price
                        entry_date = exit_date
                        entry_index = i
                    elif position is None:
                        position = 'long'
                        entry_price = curr_bar['open']
                        entry_date = curr_bar['timestamp']
                        entry_index = i

                elif signal == -1:
                    if position == 'long':
                        # Close long, open short
                        exit_price = curr_bar['open']
                        exit_date = curr_bar['timestamp']
                        returns = (exit_price - entry_price) / entry_price
                        results.append({
                            "Strategy": strategy,
                            "Symbol": symbol,
                            "Side": "BUY",
                            "BuyDate": entry_date,
                            "BuyPrice": entry_price,
                            "SellDate": exit_date,
                            "SellPrice": exit_price,
                            "Return": returns
                        })
                        position = 'short'
                        entry_price = exit_price
                        entry_date = exit_date
                        entry_index = i
                    elif position is None:
                        position = 'short'
                        entry_price = curr_bar['open']
                        entry_date = curr_bar['timestamp']
                        entry_index = i

                # else: hold

            # Square off any open position at last bar
            if position is not None and entry_index is not None:
                exit_row = short_df.iloc[-1]
                exit_price = exit_row['close']
                exit_date = exit_row['timestamp']
                if position == 'long':
                    returns = (exit_price - entry_price) / entry_price
                    side = "BUY"
                else:
                    returns = (entry_price - exit_price) / entry_price
                    side = "SELL"
                results.append({
                    "Strategy": strategy,
                    "Symbol": symbol,
                    "Side": side,
                    "BuyDate": entry_date,
                    "BuyPrice": entry_price,
                    "SellDate": exit_date,
                    "SellPrice": exit_price,
                    "Return": returns
                })
        except Exception as e:
            print(f"Error for {symbol}: {e}")
    return pd.DataFrame(results)

# --------------------------------
# Example usage (setup as before)
# --------------------------------
tickers = {
    1038081: 'PANACEABIO',
    3038209: '63MOONS',
    3064577: 'GOLDIAM',
    3738113: 'WEBELSOLAR'
}

def print_strategy_performance(df):
    if df.empty:
        print("No trades found.")
        return
    # Per-symbol performance
    print("\n---- Per Stock Compounded Return ----")
    for symbol in df['Symbol'].unique():
        trades = df[df['Symbol'] == symbol].sort_values('BuyDate')
        cumulative = 1.0
        for r in trades['Return']:
            cumulative *= (1 + r)
        stock_return = cumulative - 1
        print(f"{symbol}: {stock_return:.2%} ({len(trades)} trades)")
    # Total strategy compounded return
    print("\n---- Total Strategy Compounded Return ----")
    df = df.sort_values('BuyDate')
    cumulative = 1.0
    for r in df['Return']:
        cumulative *= (1 + r)
    total_return = cumulative - 1
    print(f"Total compounded return for strategy: {total_return:.2%}")


if __name__ == "__main__":
    file_path = os.path.join(ROOT_DIR, "data", "masters", "large_cap_stocks.csv")
    tickers = zerodha.read_csv_to_dataframe(file_path)
    tickers = dict(zip(tickers['instrument_token'], tickers['tradingsymbol']))
    # Example tickers dictionary (token: symbol)
    """
    tickers = {
        1038081: 'PANACEABIO',
        3038209: '63MOONS',
        3064577: 'GOLDIAM',
        3738113: 'WEBELSOLAR'
    }
    """
    # Example strategy instance (using a slope/trend strategy as an example)
    strategy = generate_trade_signal

    # Example date range and parameters
    start_date = '2025-02-18'
    end_date = '2025-02-25'
    min_lookback_days = 20
    trade_on_next_day_open = True
    max_deals = 5
    hold_period = 5

    # Call the backtest function
    result_df = run_multi_tf_backtest(
        tickers=tickers,
        strategy=strategy,
        zerodha_api=zerodha,
        start_date=start_date,
        end_date=end_date,
        min_lookback_days=min_lookback_days
    )

    # Print results
    print(result_df)

    # Example usage:
    print_strategy_performance(result_df)