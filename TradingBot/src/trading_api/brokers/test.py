
import sys
from pathlib import Path
import os
from pathlib import Path

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


from brokers.zerodha import ZerodhaAPI
# Intialize with config
zerodha1 = ZerodhaAPI("config/zerodha.cfg")
print("hello")
# Fetch market data
infy_quote = zerodha1.get_quote("NSE", "INFY")
print(infy_quote["last_price"])

infy_quote = zerodha1.get_ohlc("NSE", "INFY")
print(infy_quote)


holding = zerodha1.get_holdings()
print(holding)

filePath = str(cwd) +"/../data/masters/" 

filters = {
    'segment': 'NSE',  # Only NSE instruments
    'instrument_type': 'EQ',
    'exchange'  : 'NSE'
    #'last_price': {'>': 10},  # Price between ₹100-500
}
columns = [
    'tradingsymbol',
    'name',
    'last_price', 
    'instrument_type',
    'segment',
    'exchange'
]

# Execute the download with filters
#download_result = zerodha1.download_masters(
#    path=filePath,
#    filters=filters,
#    columns=columns
#)

get_quote_list = zerodha1.get_quote_list([
    {'exchange': 'NSE', 'tradingsymbol': 'INFY'},
    {'exchange': 'NSE', 'tradingsymbol': 'ADANIENT'},
])
print("get_quote_list-->>>>")
print(get_quote_list)

ltp_data = zerodha1.get_ltp([
    {'exchange': 'NSE', 'tradingsymbol': 'INFY'},
    {'exchange': 'NSE', 'tradingsymbol': 'RELIANCE'},
    {'exchange': 'NSE', 'tradingsymbol': 'NIFTY 50'}
])
print("hello-->")
print(ltp_data)