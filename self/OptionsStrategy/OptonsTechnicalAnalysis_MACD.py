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
from ta import add_all_ta_features
from ta.utils import dropna

desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',30)
from plotly.offline import plot
import plotly.graph_objs as go
import pandas as pd

## graph
from plotly.offline import plot
import plotly.graph_objs as go

df = yf.download("INFY.NS",
                 start="2020-01-01",
                 end="2020-12-31")
##
df["RSI14"] = talib.RSI(df["Adj Close"],timeperiod = 14)
df["ATR"] = talib.ATR(df["High"],df["Low"],df["Adj Close"],timeperiod = 14)


## All TA Features
df = add_all_ta_features(
    df, open="Open", high="High", low="Low", close="Adj Close", volume="Volume", fillna=True)

## BollingerBands
indicator_bb = BollingerBands(close=df["Adj Close"], window=20, window_dev=2)
df['bb_bbm'] = df['Close'].rolling(20).mean()
df['bb_bbh'] = indicator_bb.bollinger_hband()
df['bb_bbl'] = indicator_bb.bollinger_lband()

# Add Bollinger Band high indicator
df['bb_bbhi'] = indicator_bb.bollinger_hband_indicator()
# Add Bollinger Band low indicator
df['bb_bbli'] = indicator_bb.bollinger_lband_indicator()
df[['Adj Close','bb_bbm']].plot()
plt.fill_between(df.index,df["bb_bbh"],df["bb_bbl"],color ='orange')
plt.show()
print(df.dropna())

o = df['Open'].astype(float)
h = df['High'].astype(float)
l = df['Low'].astype(float)
c = df['Close'].astype(float)

trace = go.Candlestick(
            open=o,
            high=h,
            low=l,
            close=c)

print(trace)
data = [trace]
layout = {
    'title': '2019 Feb - 2020 Feb Bitcoin Candlestick Chart',
    'yaxis': {'title': 'Price'},
    'xaxis': {'title': 'Index Number'},

}
fig = dict(data=data, layout=layout)
plot(fig, filename='btc_candles')






