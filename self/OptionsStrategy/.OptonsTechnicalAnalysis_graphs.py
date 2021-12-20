import numpy as np
import pandas as pd
import ta.momentum
import yfinance as yf
import warnings

import cufflinks as cf
import plotly.graph_objects as go
from plotly.offline import iplot, init_notebook_mode, plot
import matplotlib.pyplot as plt
import plotly.offline as py
# For Plotting
import matplotlib.pyplot as plt

import pandas as pd
import yfinance as yf
from ta.volatility import BollingerBands,AverageTrueRange
plt.style.use("seaborn")
plt.rcParams["figure.figsize"] = [14, 8]

desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',30)

## graph
from plotly.offline import plot
import plotly.graph_objs as go


cf.go_offline()

TICKER = "INFY.NS"

df = yf.download(TICKER,
                 start="2021-10-01",
                 end="2021-12-20")

##
df["mv20"] = df['Adj Close'].rolling(window=20).mean()
indicator_bb = BollingerBands(close=df["Adj Close"], window=20, window_dev=2)
df['bb_bbm'] = df['Adj Close'].rolling(20).mean()
df['bb_bbh'] = indicator_bb.bollinger_hband()
df['bb_bbl'] = indicator_bb.bollinger_lband()
df["RSI14"] = ta.momentum.RSIIndicator(df["Adj Close"],window=14).rsi()
## MACD

df["ewm12"] = df["Adj Close"].ewm(span=12, adjust=False).mean()
df["ewm26"] = df["Adj Close"].ewm(span=26, adjust=False).mean()
df["macd"] = df["ewm12"]-df["ewm26"]
df["macd9"] = df["macd"].ewm(span=9, adjust=False).mean()
df["macdsignal"] =  df.apply(lambda x: 1 if x["macd"] > x["macd9"] else -1,axis=1)
df = df.dropna()
df = df.reset_index()
print(df)
trace1 = go.Scatter(x=df["Date"],y=df["mv20"])
trace = go.Figure(go.Candlestick(x = df["Date"],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']))

trace.add_trace(go.Scatter(x=df["Date"],y=df["mv20"]))
trace.add_trace(go.Scatter(x=df["Date"],y=df["bb_bbh"]))
trace.add_trace(go.Scatter(x=df["Date"],y=df["bb_bbl"]))
trace.add_trace(go.Scatter(x=df["Date"],y=df["RSI14"]))
trace.add_trace(go.Scatter(x=df["Date"],y=df["macd9"]))
trace.add_trace(go.Scatter(x=df["Date"],y=df["macdsignal"]))
#data = [trace,trace1]



layout = {
    'title': '2019 Feb - 2020 Feb Bitcoin Candlestick Chart',
    'yaxis': {'title': 'Price'},
    'xaxis': {'title': 'Index Number'},

}
#fig = dict(data=trace, layout=layout)
plot(trace, filename='btc_candles')
print(df)