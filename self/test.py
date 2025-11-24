import yfinance as yf
import pandas as pd

def download_nse(ticker, start="2010-01-01", end="2025-01-01", save=True):
    """
    Downloads NSE stock data from Yahoo Finance. 
    Automatically adds '.NS' for NSE tickers.
    """
    yf_ticker = ticker.upper() + ".NS"
    print(f"Downloading {yf_ticker} ...")

    df = yf.download(yf_ticker, start=start, end=end)

    if df.empty:
        print("No data found. Check ticker:", yf_ticker)
        return None

    # Standardize column names
    df = df.reset_index()
    df = df.rename(columns={
        "Date": "Date",
        "Open": "Open",
        "High": "High",
        "Low": "Low",
        "Close": "Close",
        "Adj Close": "AdjClose",
        "Volume": "Volume"
    })

    if save:
        filename = f"{ticker}.csv"
        df.to_csv(filename, index=False)
        print(f"Saved: {filename}")

    return df


# Example
if __name__ == "__main__":
    download_nse("RELIANCE")
