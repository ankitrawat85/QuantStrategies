import sys
import os
from pathlib import Path
from typing import List

# Set project root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)
print("ROOT_DIR:", ROOT_DIR)

# Imports
from tradingbot.Strategy.Technical_Analysis import CandlePatternRecognizer, TrendAnalyzer
from tradingbot.trading_api.brokers.zerodha import ZerodhaAPI
from tradingbot.Strategy.momentum import calculate_momentum
from tradingbot.API.nseSymbolCategory import read_symbol
from tradingbot.Strategy.consolidate_all_strategy import *


# Main screening logic
def screen_stocks(filters: List[StockFilter]):
    stocks = {}
    print("Started Screening ......!!")

    file_path = os.path.join(ROOT_DIR, "data", "masters", "large_cap_stocks.csv")
    zerodha = ZerodhaAPI(os.path.join(ROOT_DIR, "config", "Broker", "zerodha.cfg"))
    tickers = zerodha.read_csv_to_dataframe(file_path)

    for _, ticker in tickers[['instrument_token', 'tradingsymbol']].iterrows():
        try:
            day_df = zerodha.get_historical_data(
                instrument_token=ticker['instrument_token'],
                interval='day',
                from_date="2023-12-01",
                to_date="2025-02-18",
                output_format='dataframe'
            )
            min_df = zerodha.get_historical_data(
                instrument_token=ticker['instrument_token'],
                interval='5minute',
                from_date="2025-01-18",
                to_date="2025-02-18",
                output_format='dataframe'
            )

            if all(f.run(ticker['tradingsymbol'], day_df, min_df) for f in filters):
                
                stocks[ ticker['instrument_token'] ] =  ticker['tradingsymbol']

                print(f"PASS: {ticker['tradingsymbol'],ticker['instrument_token']}")

        except Exception as e:
            print(f"Skipping {ticker['tradingsymbol']} due to error: {e}")
        
    print("Completed Screening ......!!")
    return stocks

# Use your filters here
if __name__ == "__main__":

    # Read Symbol and Category
    symbol_category = read_symbol()[['Symbol','Industry']].set_index('Symbol')

    selected_filters = [
        MomentumFilter(threshold=0.8, comparison=">"),
        SlopeFilter(periods=10),
        #CandlePatternFilter()
    ]
    #x = screen_stocks(selected_filters)
    #print(x)  # prints the list of stocks that passed the filters

    #x = {524545: 'CHENNPETRO', 800513: 'BARBEQUE', 912129: 'ADANIGREEN', 945665: 'VINDHYATEL', 1095425: 'DENORA', 1034241: 'EIMCOELECO', 2722305: 'ASAL', 2649601: 'CSLFINANCE', 2927361: 'SPANDANA', 3197185: 'SWSOLAR', 3577857: 'TANLA', 3588865: 'VEEDOL', 4107521: 'PRINCEPIPE', 4643585: 'DOLPHIN', 4610817: 'WHIRLPOOL', 4935425: 'THEJO', 6201857: 'STANLEY'}
    x = {1038081: 'PANACEABIO', 3038209: '63MOONS', 3064577: 'GOLDIAM', 3738113: 'WEBELSOLAR', 4547585: 'REFEX', 5013761: 'BSE', 5088257: 'LGHL', 6392065: 'WINDMACHIN'}

    stock_category_Mapping = {}
    for key,value in x.items():
        try:
            stock_category_Mapping[value] = symbol_category.loc[value][0]
        except:
            print(f"Missing Category for Trading symbol {value}")
    
    print(f"stock_category_Mapping : {stock_category_Mapping}")  # prints the mapping of stocks to their categories