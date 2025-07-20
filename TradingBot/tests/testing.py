from tradingbot.Strategy import Technical_Analysis
from tradingbot.trading_api.brokers.zerodha import ZerodhaAPI

import sys
from pathlib import Path
import os
from pathlib import Path


# Set the root of your package
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)
print("ROOT_DIR:", ROOT_DIR)

connection = ZerodhaAPI(ROOT_DIR +"/config/Broker/zerodha.cfg")

# Fetch market data
infy_quote = connection.get_quote("NSE", "INFY")
infy_ohlc = connection.get_ohlc("NSE", "INFY")
print(infy_quote)