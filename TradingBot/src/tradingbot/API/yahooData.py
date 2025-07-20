import sys
import os

# Add `src` to sys.path
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(SRC_PATH)
print(SRC_PATH)
from lib.imports import yf 


import yfinance as yhaoo
import pandas as pd

def get_financial_data(ticker):
    """Fetch financial statements from Yahoo Finance."""
    stock = yhaoo.Ticker(ticker)
    
    # Get financial statements (annual)
    income = stock.financials.T
    balance = stock.balance_sheet.T
    cashflow = stock.cashflow.T
    
    # Combine into a single DataFrame
    financials = pd.concat([income, balance, cashflow], axis=1)
    financials = financials.sort_index()  # Sort by year
    
    return financials

def calculate_piotroski_f_score(ticker):
    """Calculate Piotroski F-Score for a given stock."""
    df = get_financial_data(ticker)
    
    # Ensure we have at least 2 years of data
    if len(df) < 2:
        raise ValueError("Insufficient data (need at least 2 years)")
    
    # Get the two most recent years
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    
    # Calculate Total Assets (Avg if needed)
    total_assets = latest['Total Assets']
    prev_total_assets = previous['Total Assets']
    
    # 1. Profitability Measures
    roa = latest['Net Income'] / total_assets
    cfo = latest['Operating Cash Flow'] / total_assets
    delta_roa = roa - (previous['Net Income'] / prev_total_assets)
    accrual = (latest['Net Income'] - latest['Operating Cash Flow']) / total_assets
    
    # 2. Leverage & Liquidity
    leverage = latest['Long Term Debt'] / total_assets
    prev_leverage = previous['Long Term Debt'] / prev_total_assets
    delta_leverage = leverage - prev_leverage
    
    current_ratio = latest['Current Assets'] / latest['Current Liabilities']
    prev_current_ratio = previous['Current Assets'] / previous['Current Liabilities']
    delta_liquid = current_ratio - prev_current_ratio
    
    # 3. Operating Efficiency
    gross_margin = latest['Gross Profit'] / latest['Total Revenue']
    prev_gross_margin = previous['Gross Profit'] / previous['Total Revenue']
    delta_margin = gross_margin - prev_gross_margin
    
    asset_turnover = latest['Total Revenue'] / total_assets
    prev_asset_turnover = previous['Total Revenue'] / prev_total_assets
    delta_turn = asset_turnover - prev_asset_turnover
    
    # 4. Equity Issuance (Check if shares increased)
    shares_latest = latest['Common Stock'] if 'Common Stock' in latest else latest['Ordinary Shares Number']
    shares_previous = previous['Common Stock'] if 'Common Stock' in previous else previous['Ordinary Shares Number']
    eq_offer = 1 if shares_latest <= shares_previous else 0
    
    # Calculate F-Score (0-9)
    f_score = 0
    
    # Profitability (4 points)
    f_score += 1 if roa > 0 else 0
    f_score += 1 if cfo > 0 else 0
    f_score += 1 if delta_roa > 0 else 0
    f_score += 1 if cfo > roa else 0  # F_ACCRUAL
    
    # Leverage & Liquidity (3 points)
    f_score += 1 if delta_leverage < 0 else 0
    f_score += 1 if delta_liquid > 0 else 0
    f_score += eq_offer
    
    # Operating Efficiency (2 points)
    f_score += 1 if delta_margin > 0 else 0
    f_score += 1 if delta_turn > 0 else 0
    
    return f_score



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
    # Example Usage
    ticker = "AAPL"  # Apple stock
    f_score = calculate_piotroski_f_score(ticker)
    print(f"Piotroski F-Score for {ticker}: {f_score}/9")


