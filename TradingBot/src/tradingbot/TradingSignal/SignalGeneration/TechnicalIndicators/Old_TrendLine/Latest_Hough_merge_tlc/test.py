from tradingbot.TradingSignal.SignalGeneration.TechnicalIndicators.Old_TrendLine.Latest_Hough_merge_tlc.trendline_api import  run_methods,consolidate_buy_sell,snapshot_at


from tradingbot.TradingSignal.SignalGeneration.TechnicalIndicators.Old_TrendLine.Latest_Hough_merge_tlc.combined_strength_api import get_combined_strength,compute_snapshot_strength,plot_strength_timeseries,compute_strength_timeseries,StrengthParams

from tradingbot.trading_api.brokers.zerodha import ZerodhaAPI
import os
import pandas as pd
import pandas as pd

pd.set_option("display.max_columns", None)   # show all columns
pd.set_option("display.max_rows", None)      # (optional) show all rows
pd.set_option("display.max_colwidth", None)  # don’t truncate column contents
pd.set_option("display.width", 0)            # auto-detect terminal width
pd.set_option("display.expand_frame_repr", False)  # keep one row per line

ROOT = os.environ.get("ZERODHA_ROOT", "/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot")
TOKEN = os.environ.get("ZERODHA_TOKEN", "6401")
CSV_PATH = os.environ.get("DATA_PATH", "/mnt/data/data_SBIN.csv")
zerodhacfg = os.path.join(ROOT, "config", "Broker", "zerodha.cfg")
zerodha = ZerodhaAPI(zerodhacfg)

def signal_generation(date,token,tradingsymbol,snapshot = False):
  fetch_last_n = zerodha.make_fetcher_zerodha_last_n(root_dir=ROOT,instrument_token=token,          # your token
          default_interval='day',
          end_dt = date ,
          n_bars = 300
        )

  fetch_last_n = fetch_last_n.rename(columns = {"timestamp":"date"})

  # download data
  fetch_last_n.to_csv('data_INFY.csv')
  import json

  path = '/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot/src/tradingbot/TradingSignal/SignalGeneration/TechnicalIndicators/Old_TrendLine/Latest_Hough_merge_tlc/tlc_config_methods.json'
  cfg = json.load(open(path))
  

  #cfg = json.load(open(ROOT +"/QuantStrategies/TradingBot/src/tradingbot/TradingSignal/SignalGeneration/TechnicalIndicators/Old_TrendLine/Latest_Hough_merge_tlc/tlc_config_methods.json"))
  # 3) Run any methods you want (e.g., OLS only)
  results = run_methods(
      df=fetch_last_n,
      config=cfg,
      methods=["ols_shift_min"],
      #methods=["ols","ols_shift_min","ols_envelop","huber","hough"],
      main_stream_path="/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot/src/tradingbot/TradingSignal/SignalGeneration/TechnicalIndicators/Old_TrendLine/Latest_Hough_merge_tlc/main_trendline_stream.py",
      min_confidence=0.0,
      outdir="./out_old/" + tradingsymbol   
  )
  return results
if __name__ == "__main__":
  #Read from CSV and conver to dicts
  output = pd.DataFrame()
  csv_path = '/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot/data/masters/'
  get_quote_list_data_= zerodha.read_csv_to_dicts(csv_path+"large_cap_stocks.csv")
  tickers = [
    "SBIN", ""
    """
    "BAJFINANCE",
    "BHARTIARTL", "CIPLA", "COALINDIA",
    
    "DRREDDY", "EICHERMOT", "GRASIM", "HCLTECH", "HDFCBANK",
    
    "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK",
    "INDUSINDBK", "INFY", "ITC", "JSWSTEEL", "KOTAKBANK",
    "LT", "M&M", "MARUTI", "NESTLEIND", "NTPC",
    "ONGC", "POWERGRID", "RELIANCE", "SBILIFE", "SBIN",
    "SHRIRAMFIN", "SUNPHARMA", "TATACONSUM", "TATAMOTORS", "TATASTEEL",
    "TCS", "TECHM", "TITAN", "ULTRACEMCO", "WIPRO",
    "BEL", "TRENT", "JIOFIN", "ZOMATO"
    """
]

params=StrengthParams(
        decay_lambda=0.12,
        decay_hold=0,
        decay_threshold=0.25,
        method_weights={"ols": 0.20, "ols_shift_min":0.20,"ols_envelop":0.20,"huber":0.20,"hough": 0.20},
        add_percentage_cols=True,        # optional percent view (buy/sell/net *_pct)
        include_indicator_columns=True,  # << turn on the new indicator columns
        indicator_column_prefix="ind_",  # per-method columns: ind_ols, ind_hough, ...
        indicator_list_delim=","         # lists joiner for buy_indicators/sell_indicators
    )

for row in get_quote_list_data_:
    try:
      if  row['tradingsymbol'] in tickers:
        print(row['instrument_token'],row['tradingsymbol'])
        data = signal_generation("2025-08-26",row['instrument_token'],row['tradingsymbol'])

        out = compute_strength_timeseries(data, params)

        # Same-day-only snapshot (ignores prior carryover)
        # Snapshot as-of vs same-day-only:
        #out = compute_snapshot_strength(data, "2025-08-07", ignore_prior=True)
        #strength_df = out["strength_df"]
        if out.get('strength_df',None):
          strength_df = out["strength_df"]
        else:
          strength_df = out
        
        strength_df['Symbol'] = row['tradingsymbol']

        #fig, ax = plot_strength_timeseries(strength_df,title=f"{row['tradingsymbol']} — Strength Time Series",out_path=f"{row['tradingsymbol']}_strength.png",)
        if output.empty:
          output = strength_df
        else:
          output= pd.concat([strength_df, output], ignore_index=True)
    except Exception as e:
      print(f" Failed to pricess { row['tradingsymbol'] }, Error : {e}")
    
output.to_csv(ROOT+"/Final_signals_test_later.csv")