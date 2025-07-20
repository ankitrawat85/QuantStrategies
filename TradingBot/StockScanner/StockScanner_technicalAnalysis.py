import sys
from pathlib import Path
import os
from pathlib import Path


# Set Path
# Set the root of your package
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)
print("ROOT_DIR:", ROOT_DIR)


# import lib
from tradingbot.Strategy.Technical_Analysis import CandlePatternRecognizer,TrendAnalyzer
from tradingbot.trading_api.brokers.zerodha import ZerodhaAPI
from tradingbot.Strategy.momentum import calculate_momentum

# Check if the package exists at the expected path
#package_path = Path("__init__.py")
#print("Package exists:", package_path.is_file())
cwd = os.getcwd()
#print("Current working directory:", cwd)

## set file path

filePath = str(cwd) +"/./data/masters/" 


# Intialize with config
zerodha1 = ZerodhaAPI((ROOT_DIR +"/config/Broker/zerodha.cfg"))

tickers = zerodha1.read_csv_to_dataframe(filePath+"large_cap_stocks.csv")


#for ticker in list(tickers['tradingsymbol']):
"""
print("Started  Screening ......!!")
for index,ticker in tickers[['instrument_token',"tradingsymbol"]].iterrows():
    try:
        data_day        =  zerodha1.get_historical_data(   instrument_token=ticker['instrument_token'],
                                                        interval='day',
                                                        from_date="2023-12-01",
                                                        to_date="2025-02-18",
                                                        output_format = 'dataframe'
                                                    )
        
        data_60_minute  =   zerodha1.get_historical_data(   instrument_token=ticker['instrument_token'],
                                                    interval='5minute',
                                                    from_date="2025-01-18",
                                                    to_date="2025-02-18",
                                                    output_format = 'dataframe'
                                            )
        
        momentum =  calculate_momentum(data_day[['close','timestamp']].set_index(['timestamp']),lookback_months=6).iloc[-1].close
       

        #print("Started Screening ..")
        if momentum > 0.8 :
            slope_with_trend = TrendAnalyzer.slope_with_trend(data_day,10,price_type="typical")
            cp = CandlePatternRecognizer.identify_pattern(data_60_minute, data_day.iloc[:-1,:])
            #if slope_with_trend[1] == 'Uptrend' and 'None' not in cp:
            print(f" Ticker : {ticker['tradingsymbol']} |||  Momentum : {momentum} ||| Slope : {slope_with_trend} ||| Candle Pattern : {cp} ")
        

    except Exception as e:
        pass
        #print(f"Skipping {ticker['tradingsymbol']} due to error: {str(e)}")
print("Completed Screening ......!!")



"""
import pandas as pd
from datetime import datetime, timedelta

# Configuration
tickers_list = ['REFEX']
#tickers_list = ['PANACEABIO','63MOONS','GOLDIAM','REFEX','LGHL','WINDMACHIN']
start_date = "2025-02-18"
end_date = "2025-06-20"
evaluation_frequency = '1D'  # Could be '1D' for daily or '1W' for weekly
momentum_lookback = 6  # months
trend_window = 10  # days
momentum_threshold = 0.8

# Convert to datetime objects
current_date = datetime.strptime(start_date, "%Y-%m-%d")
end_date = datetime.strptime(end_date, "%Y-%m-%d")

# Prepare results storage
results = []

while current_date <= end_date:
    evaluation_date = current_date.strftime("%Y-%m-%d")
    print(f"\nEvaluating date: {evaluation_date}")
    
    for ticker_name in tickers_list:
        try:
            # Find the instrument token for this ticker
            ticker_info = tickers[tickers['tradingsymbol'] == ticker_name].iloc[0]
            
            # Get historical data up to evaluation date
            start_date_calc = (current_date - timedelta(days=trend_window+ 10)).strftime("%Y-%m-%d")
            data_day = zerodha1.get_historical_data(
                instrument_token=ticker_info['instrument_token'],
                interval='day',
                from_date=start_date_calc,
                to_date=evaluation_date,
                output_format='dataframe'
            )
            
            # Get intraday data for the last month (for candle patterns)
            from_date_intraday = (current_date - timedelta(days=30)).strftime("%Y-%m-%d")
            data_60_minute = zerodha1.get_historical_data(
                instrument_token=ticker_info['instrument_token'],
                interval='5minute',
                from_date=from_date_intraday,
                to_date=evaluation_date,
                output_format='dataframe'
            )
            

            slope_with_trend = TrendAnalyzer.slope_with_trend(
                data_day, trend_window, price_type="typical"
            )
            cp = CandlePatternRecognizer.identify_pattern(
                data_60_minute, data_day.iloc[:-1,:]
            )
            if 'bullish' in cp or 'bearish' in  cp:
                print(f"Signal on {evaluation_date} for {ticker_name}: "
                        f"Trend={slope_with_trend[1]}, "
                        f"Pattern={cp}")
        
        except Exception as e:
            print(f"Skipping {ticker_name} on {evaluation_date} due to error: {str(e)}")
    
    # Move to next evaluation date
    if evaluation_frequency == '1D':
        current_date += timedelta(days=1)
    elif evaluation_frequency == '1W':
        current_date += timedelta(weeks=1)

