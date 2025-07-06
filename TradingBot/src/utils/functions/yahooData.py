import sys
import os

# Add `src` to sys.path
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(SRC_PATH)
print(SRC_PATH)
from lib.imports import yf 

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

if __name__ == "__main__":
    print(get_valuation_ratios('AAPL')) 