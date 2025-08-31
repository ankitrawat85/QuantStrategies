
import sys
from pathlib import Path
import os
from pathlib import Path

from tradingbot.Strategy import Technical_Analysis
from tradingbot.trading_api.brokers.zerodha import ZerodhaAPI


# Set the root of your package
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)
print("ROOT_DIR:", ROOT_DIR)

# Check if the package exists at the expected path
package_path = Path("__init__.py")
print("Package exists:", package_path.is_file())
cwd = os.getcwd()
print("Current working directory:", cwd)

## set file path

filePath = str(cwd) +"/./data/masters/" 


# Intialize with config
zerodha1 = ZerodhaAPI((ROOT_DIR +"/config/Broker/zerodha.cfg"))


# Fetch market data
infy_quote = zerodha1.get_quote("NSE", "INFY")
infy_ohlc = zerodha1.get_ohlc("NSE", "INFY")


filters = {
    'segment': 'NSE',  # Only NSE instruments
    'instrument_type': 'EQ',
    'exchange'  : 'NSE',
    'lot_size': 1,  # Price between ₹100-500,
    
}
columns = [
    'instrument_token',
    'exchange',
    'tradingsymbol',
    #'name',
    #'last_price', 
    #'instrument_type',
    #'segment',
]


# Execute the download with filters
download_result = zerodha1.download_masters(
   path=filePath,
   filters=filters,
   columns=columns,
   ignore_tradingsymbols = ['-','-BZ', '-BE','-GB']
)


# Read from CSV and conver to dicts
get_quote_list_data_1 = zerodha1.read_csv_to_dicts(filePath+"zerodha_master_processed.csv")

get_quote_list_data = zerodha1.get_quote_list(get_quote_list_data_1)
#print("get_quote_list-->>>>")
#print(get_quote_list_data)


# Save data to CSV
zerodha1.save_quotes_to_csv(
    get_quote_list_data,
    filters={"close": (300, 3000)},
    filename=filePath+"large_cap_stocks.csv"
)

"""
ltp_data = zerodha1.get_ltp([
    {'exchange': 'NSE', 'tradingsymbol': 'INFY'},
    {'exchange': 'NSE', 'tradingsymbol': 'RELIANCE'},
    {'exchange': 'NSE', 'tradingsymbol': 'NIFTY 50'}
])
print("hello-->")
print(ltp_data)


zerodha1.create_database("zerodha.db")
zerodha1.create_historical_data_table('timeseries')


success = zerodha1.get_batch_historical_data(
    csv_path= filePath+"/zerodha_master_processed.csv",
    save_to = "db",  # "csv" or "db"
    output_path = "timeseries",
    interval="day",
    from_date="2024-01-01",
    to_date="2025-07-08",
    db_conn =zerodha1.db
    )


nifty_data = zerodha1.fetch_data(
    "timeseries"
)

"""