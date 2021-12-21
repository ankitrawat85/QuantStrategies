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
from candle_rankings import candle_rankings
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


df  = yf.download(tickers='INFY.NS', period='1mo', interval='2m')
df  = df [["Open", "High", "Low", "Close", "Adj Close", "Volume"]]
df  = df .reset_index()
df  = df .rename(columns={"Datetime": "Date"})
df= df[df["Volume"] !=0]
## TA

bb_indicator = BollingerBands(df["Adj Close"])
df["upperBand"] = bb_indicator.bollinger_hband_indicator()
df["lowerBand"] = bb_indicator.bollinger_lband_indicator()
df["moving_average"] = bb_indicator.bollinger_mavg()


## TALIB

# candle stick
def recognize_candlestick(df):
    """
    Recognizes candlestick patterns and appends 2 additional columns to df;
    1st - Best Performance candlestick pattern matched by www.thepatternsite.com
    2nd - # of matched patterns
    """

    op = df['Open'].astype(float)
    hi = df['High'].astype(float)
    lo = df['Low'].astype(float)
    cl = df['Adj Close'].astype(float)

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
output_ = recognize_candlestick(df)
print(output_[["Open","High","Low","Close","Adj Close","Volume","candlestick_pattern","candlestick_match_count"]].tail(5))
output_.to_csv("technicalIndicators.csv")

temp_output = output_[["Open","High","Low","Close","Adj Close","Volume","candlestick_pattern","candlestick_match_count"]]

from plotly.offline import plot
import plotly.graph_objs as go
import pandas as pd

df = pd.read_csv('technicalIndicators.csv')
df_ = df.copy(deep=True)
df_.set_index("Date", inplace = True)
o = df_['Open'].astype(float)
h = df_['High'].astype(float)
l = df_['Low'].astype(float)
c = df_['Adj Close'].astype(float)

trace = go.Candlestick(
            open=o,
            high=h,
            low=l,
            close=c)
data = [trace]

#plot(data, filename='go_candle1.html')

layout = {
    'title': 'Stock- Candlestick Chart',
    'yaxis': {'title': 'Price'},
    'xaxis': {'title': 'Index Number'},

}
fig = dict(data=data, layout=layout)
#plot(fig, filename='Stock_candles')


df["Adj Close"].plot(title="Stock Adj Close");
plt.plot(df["Adj Close"],'--',label="Close Price")
upper, middle, lower = talib.BBANDS(df["Adj Close"], timeperiod=20)
plt.plot(upper,label='Upper')
plt.plot(middle,label='Middle')
plt.plot(lower,label='Lower')
plt.legend(loc ="best")
plt.title("Bolinger Bands (TA-lib)")
plt.show()

df = df.set_index("Date")
## Visualizing how price oscillated around the average
plt.plot(df["Adj Close"].values - middle)
plt.grid
plt.show()

## 220 Days Moving Average
sma30 = talib.SMA(df["Adj Close"].values,30)
plt.plot(sma30,label='SMA200')
plt.plot(df["Adj Close"].values,label='Price')
plt.legend(loc='best')
plt.show()


## Combining multiple indicators
sma25 = talib.SMA(df["Adj Close"].values,25)
sma50 = talib.SMA(df["Adj Close"].values,50)
EMA25 = talib.EMA(df["Adj Close"].values,50)
EMA50 = talib.EMA(df["Adj Close"].values,50)

## Normalization
sma_diff = (sma30 - sma50)/sma25
tem_sma_diff = pd.DataFrame()
tem_sma_diff["sma_diff"] = sma_diff
tem_sma_diff["BUY_SELL"] = np.NAN
tem_sma_diff["BUY_SELL"] = tem_sma_diff["sma_diff"].apply(lambda x : "Buy" if x > 0.03 else ( "Sell" if x < -0.03 else "neutral"))
print("SMA difference trading signal")
print(tem_sma_diff)
#plt.plot(sma50,label = 'sma50')
plt.plot(sma25,label = 'sma25')
plt.plot(EMA25,label = 'EMA25')
plt.plot(EMA50,label = 'EMA50')
plt.plot(sma50,label = 'EMA50')
plt.plot(df["Adj Close"].values,'--',label='Price')
plt.legend(loc='best')
plt.title("Different Moving Average")
plt.show()

# Moving average indicator perform
for i in range(len(df)):
    ## Buy
    if sma_diff[i] > 0.03:
        plt.plot(i,df["Adj Close"].values[i],'g.')
    elif sma_diff[i] < -0.03:
        plt.plot(i, df["Adj Close"].values[i], 'r.')
    else:
        plt.plot(i, df["Adj Close"].values[i], 'b.')

plt.title("Moving Average indicator signal")
plt.show()

def get_fwd_rest(ret_wdw):
    fwd_rets = (df["Adj Close"].iloc[ret_wdw:].values - df["Adj Close"].iloc[:-ret_wdw].values)/\
               (df["Adj Close"].iloc[:-ret_wdw].values)
    return fwd_rets

ret_wdw = 30
fwd_rets = get_fwd_rest(ret_wdw)
pnls = np.sign(sma_diff[101:-ret_wdw] * fwd_rets[101:])
print('Final PnL: %.2f' % (np.sum(pnls)/ret_wdw))
plt.hist(pnls,40)
plt.xlabel('PnLs')
plt.show()
len(pnls[pnls>0])


# add all available TA indicators
ta_all_indicators_df = ta.add_all_ta_features(df, open="Open", high="High",
                                              low="Low", close="Close",
                                              volume="Volume")


## MACD









