
import yfinance as yf

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

tickers = zerodha1.read_csv_to_dataframe(filePath+"large_cap_stocks.csv")


def get_valuation_ratios(ticker):
    """
    Fetches P/E, P/B, and P/CF ratios for a given stock ticker from Yahoo Finance.

    Parameters:
        ticker (str): Stock symbol (e.g., 'AAPL')

    Returns:
        dict: {'pe_ratio': float, 'pb_ratio': float, 'pcf_ratio': float or None}
    """
    stock = yf.Ticker(ticker)
    info = stock.info

    pe_ratio = info.get("trailingPE")
    pb_ratio = info.get("priceToBook")

    try:
        price = info.get("currentPrice")
        ocf = info.get("operatingCashflow")
        shares = info.get("sharesOutstanding")
        pcf_ratio = price / (ocf / shares) if price and ocf and shares else None
    except:
        pcf_ratio = None

    return {ticker :  {
                    "pe_ratio": pe_ratio,
                    "pb_ratio": pb_ratio,
                    "pcf_ratio": pcf_ratio
                    }}

for ticker in list(tickers["tradingsymbol"]):
    try:
        output = get_valuation_ratios(str(ticker)+".NS")
        #print(f" Ticker : {ticker} and ratios : {output}")
    except:
        print(f" failed - Ticker : {ticker}")