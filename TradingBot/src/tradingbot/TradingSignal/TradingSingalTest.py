from tradingbot.TradingSignal.SignalGeneration.TechnicalIndicators.TrendLine.trendline_api import  run_methods
from tradingbot.TradingSignal.PostSingalGeneration.CombinedSingals.combined_strength_api import plot_candles_with_signals,summarize_breaks_min,get_combined_strength,get_combined_strength_from_snapshot,compute_snapshot_strength,plot_strength_timeseries,compute_strength_timeseries,StrengthParams,consolidate_buy_sell
from tradingbot.Strategy.volume_confirmation import simple_volume_breaks
from tradingbot.Strategy.Technical_Analysis import CandlePatternRecognizer, TrendAnalyzer
from tradingbot.trading_api.brokers.zerodha import ZerodhaAPI
from tradingbot.Strategy.momentum import calculate_momentum
import os
import pandas as pd
import pandas as pd
import json
from time import perf_counter


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
  path = '/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot/src/tradingbot/TradingSignal/config/tlc_config_methods.json'
  cfg = json.load(open(path))
  

  results = run_methods(
    df=fetch_last_n,
    config=cfg,
    methods=["ols","ols_shift_min","huber","hough","ols_envelop"],
    #methods=["ols","ols_shift_min","huber","hough","ols_envelop"],
    main_stream_path="/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot/src/tradingbot/TradingSignal/SignalGeneration/TechnicalIndicators/TrendLine/main_trendline_stream.py",
    min_confidence=0.70,
    parallel=True,              # default
    max_workers=None,           # defaults to len(methods)
    write_plots=False,           # default (no plots generated)
    outdir="./out_sbin/" + tradingsymbol,
    write_csv=False,                             # switch OFF/on disk writes
   )
  
  return results,fetch_last_n

if __name__ == "__main__":
  #Read from CSV and conver to dicts
  output = pd.DataFrame()
  csv_path = '/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot/data/masters/'
  get_quote_list_data_= zerodha.read_csv_to_dicts(csv_path+"large_cap_stocks.csv")
  tickers = [
    "INFY",
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
plot_Graph = False
params=StrengthParams(
        decay_lambda=0.12,
        decay_hold=0,
        decay_threshold=0.25,
        method_weights={"ols": 0.20, "ols_shift_min":0.20,"ols_envelop":0.20,"huber":0.20,"hough": 0.20},
        add_percentage_cols=True,        # optional percent view (buy/sell/net *_pct)
        include_indicator_columns=True,  # << turn on the new indicator columns
        indicator_column_prefix="ind_",  # per-method columns: ind_ols, ind_hough, ...
        indicator_list_delim="," ,      # lists joiner for buy_indicators/sell_indicators
        calendar_index  = None,
        apply_decay = False,
        write_plots=False,  
                  # default (no plots generated)
    
    )
moreIndicators_df = pd.DataFrame()
for row in get_quote_list_data_:
    try:
      if  row['tradingsymbol'] in tickers:
        t0 = perf_counter()
        print(row['instrument_token'],row['tradingsymbol'])
        data,ohlc = signal_generation("2025-08-30",row['instrument_token'],row['tradingsymbol'])
        print(f"Total Signal generation time : {perf_counter() - t0:.3f}s")
        # Snapshot as-of vs same-day-only:
        #out = compute_snapshot_strength(data, "2025-08-07", ignore_prior=True)
        out = consolidate_buy_sell(data,params)

        try:  
          if out.get('strength_df',None):
            strength_df = out["strength_df"]
          else:
            strength_df = out
        except:
          strength_df = out
        
        strength_df['Symbol'] = row['tradingsymbol']


        # 1) build daily summary and save CSV
        summary = summarize_breaks_min(strength_df,
            method_weights={"ols": 1, "ols_shift_min":1,"ols_envelop":1,"huber":1,"hough": 1},
            side_weights={"BUY":1.0,"SELL":1.0},
            save=True,
            out_dir="./out_sbin/" + row['tradingsymbol'] +"/consolidated",
            basename="breaks"
        )
        print("CSV:", summary.attrs.get("saved_csv_path"))

        # 2) plot and save PNG
        if plot_Graph:
          _, _, png_path = plot_candles_with_signals(ohlc,summary,
              save=True,
              out_dir="./out_sbin/" + row['tradingsymbol'] +"/consolidated",
              basename="breaks"
          )
          print("PNG:", png_path)

        # Adding more analysis
        summary['tradingsymbol'] = row['tradingsymbol']
        
        for count,row in summary.iterrows():
          _longPeriod = pd.DataFrame()
          _shortPeriod = ohlc[ohlc['date'] <=row['date']]
          _shortPeriod = _shortPeriod.set_index('date')
          _shortPeriod = _shortPeriod.rename(columns = {"Open":"open","High":"high","Low":"low", "Close":"close","Volume":"volume"})
          
          _longPeriod['open']   = _shortPeriod['open'].rolling('7D').apply(lambda x: x.iloc[0], raw=False)
          _longPeriod['high']   = _shortPeriod['high'].rolling('7D').max()
          _longPeriod['low']    = _shortPeriod['low'].rolling('7D').min()
          _longPeriod['close']  = _shortPeriod['close'].rolling('7D').apply(lambda x: x.iloc[-1], raw=False)
          _longPeriod['volume'] = _shortPeriod['volume'].rolling('7D').sum()
          pattern_info = CandlePatternRecognizer.identify_pattern(_shortPeriod,_longPeriod)
          row['momentum'] = calculate_momentum(_longPeriod['close'] ,lookback_months=7)[-1]
          row['significance'] = pattern_info['significance']
          row['pattern'] = pattern_info['pattern']
          row['simple_volume_breaks'] = simple_volume_breaks( _longPeriod[['volume']])
          moreIndicators_df = pd.concat([moreIndicators_df, pd.DataFrame([row])], ignore_index=True)
        print(f"Total time taken to add additonal signals : {perf_counter() - t0:.3f}s")
    except Exception as e:
      print(f" Failed to pricess { row['tradingsymbol'] } and exception : {e}")

  
moreIndicators_df.to_csv("./out_sbin/Final_signals_test_later1.csv")

# Filter on date 
dates = pd.to_datetime(['2025-08-23','2025-08-24','2025-08-25','2025-08-26','2025-08-27','2025-08-28','2025-08-29'])
if output.empty:
  print("No data available ")
else:
  out = output[output['date'].dt.floor('D').isin(dates)]
  out.to_csv("./out_sbin/Final_signals_SNAPDATE.csv")
  # Filter on date