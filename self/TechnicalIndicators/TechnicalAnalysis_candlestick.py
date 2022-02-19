# Data manipulation
import numpy as np
import pandas as pd
import datetime
# To calculate Greeks
import mibian
import scipy

# For Plotting
import matplotlib.pyplot as plt

import pandas as pd
import yfinance as yf
import talib

import numpy as np
from self.TechnicalIndicators.candle_rankings import candle_rankings
from itertools import compress



import pandas_ta as pta
from finta import TA

## another library for technical analysis
import ta
from ta.volatility import BollingerBands,AverageTrueRange
plt.style.use("seaborn")
plt.rcParams["figure.figsize"] = [14, 8]

desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',30)

#df  = yf.download(tickers='INFY.NS', period='3mo', interval='1d')
df  = yf.download(tickers='INFY.NS', period='1mo', interval='2m')
df  = df [["Open", "High", "Low", "Close", "Adj Close", "Volume"]]
df  = df .reset_index()
df  = df .rename(columns={"Datetime": "Date"})
df= df[df["Volume"] !=0]

def recognize_candlestick(df):
    """
    Recognizes candlestick patterns and appends 2 additional columns to df;
    1st - Best Performance candlestick pattern matched by www.thepatternsite.com
    2nd - # of matched patterns
    """

    op = df['Open'].astype(float)
    hi = df['High'].astype(float)
    lo = df['Low'].astype(float)
    cl = df['Close'].astype(float)

    candle_names = talib.get_function_groups()['Pattern Recognition']

    # patterns not found in the patternsite.com

    exclude_items = ('CDLCOUNTERATTACK',
                     'CDLLONGLINE',
                     'CDLSHORTLINE',
                     'CDLSTALLEDPATTERN',
                     'CDLKICKINGBYLENGTH')


    candle_names = [candle for candle in candle_names if candle not in exclude_items]


    # create columns for each candle
    for candle in candle_names:
        # below is same as;
        # df["CDL3LINESTRIKE"] = talib.CDL3LINESTRIKE(op, hi, lo, cl)
        df[candle] = getattr(talib, candle)(op, hi, lo, cl)


    df['candlestick_pattern'] = np.nan
    df['candlestick_match_count'] = np.nan
    for index, row in df.iterrows():
        # no pattern found
        if len(row[candle_names]) - sum(row[candle_names] == 0) == 0:
            df.loc[index,'candlestick_pattern'] = "NO_PATTERN"
            df.loc[index, 'candlestick_match_count'] = 0
        # single pattern found
        elif len(row[candle_names]) - sum(row[candle_names] == 0) == 1:
            # bull pattern 100 or 200
            if any(row[candle_names].values > 0):
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bull'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
            # bear pattern -100 or -200
            else:
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bear'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
        # multiple patterns matched -- select best performance
        else:
            # filter out pattern names from bool list of values
            patterns = list(compress(row[candle_names].keys(), row[candle_names].values != 0))
            container = []
            for pattern in patterns:
                if row[pattern] > 0:
                    container.append(pattern + '_Bull')
                else:
                    container.append(pattern + '_Bear')
            rank_list = [candle_rankings[p] for p in container]
            if len(rank_list) == len(container):
                rank_index_best = rank_list.index(min(rank_list))
                df.loc[index, 'candlestick_pattern'] = container[rank_index_best]
                df.loc[index, 'candlestick_match_count'] = len(container)
    # clean up candle columns
    cols_to_drop = candle_names + list(exclude_items)
    try:
        df.drop(cols_to_drop, axis = 1, inplace = True)
    except:
        pass

    return df
#output_ = recognize_candlestick(df.iloc[:20,:])
#print(output_[["Open","High","Low","Close","Volume","candlestick_pattern","candlestick_match_count"]].tail(5))
#output_.to_csv("technicalIndicators.csv")
