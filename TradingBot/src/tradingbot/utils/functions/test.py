import yfinance as yf
import datetime

import yfinance as yf

def get_valuation_ratios(ticker):
    """
    Get P/E, P/B, and P/CF ratios for a given stock ticker from Yahoo Finance.

    Parameters:
        ticker (str): Stock symbol, e.g., 'AAPL'

    Returns:
        dict: {'pe_ratio': float, 'pb_ratio': float, 'pcf_ratio': float or None}
    """
    stock = yf.Ticker(ticker)
    info = stock.info

    pe_ratio = info.get("trailingPE")  # P/E
    pb_ratio = info.get("priceToBook")  # P/B

    # P/CF = current price / (operating cash flow per share)
    try:
        price = info.get("currentPrice")
        ocf = info.get("operatingCashflow")
        shares = info.get("sharesOutstanding")
        pcf_ratio = price / (ocf / shares) if price and ocf and shares else None
    except:
        pcf_ratio = None

    return {
        "pe_ratio": pe_ratio,
        "pb_ratio": pb_ratio,
        "pcf_ratio": pcf_ratio
    }

# 🔍 Example
ticker = "AAPL"
ratios = get_valuation_ratios(ticker)
print(f"{ticker} Valuation Ratios:")
print(f"P/E Ratio : {ratios['pe_ratio']}")
print(f"P/B Ratio : {ratios['pb_ratio']}")
print(f"P/CF Ratio: {ratios['pcf_ratio']}")
