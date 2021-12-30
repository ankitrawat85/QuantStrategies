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
pd.set_option('display.max_rows',2000)

## graph
from plotly.offline import plot
import plotly.graph_objs as go
import pandas_ta

cf.go_offline()

## Download Data
TICKER = "INFY.NS"
df  = yf.download(tickers='INFY.NS', period='3mo', interval='1d')
df  = df [["Open", "High", "Low", "Close", "Adj Close", "Volume"]]
df  = df .reset_index()
df  = df .rename(columns={"Datetime": "Date"})
df = df[df["Volume"] != 0]

## Technical Indicator - Bolinger Band
df["mv20"] = df['Adj Close'].rolling(window=20).mean()
indicator_bb = BollingerBands(close=df["Adj Close"], window=20, window_dev=2)
df['bb_bbm'] = df['Adj Close'].rolling(20).mean()
df['bb_bbh'] = indicator_bb.bollinger_hband()
df['bb_bbl'] = indicator_bb.bollinger_lband()
df['bbp'] = (df['Adj Close'] - df['bb_bbl']) / (df['bb_bbh'] - df['bb_bbl'])

plt.plot(df['bb_bbh'],label='Upper')
plt.plot(df['bb_bbm'],label='Middle')
plt.plot(df['bb_bbl'],label='Lower')
plt.plot(df['Adj Close'],label='Adj Close')
plt.fill_between(df.index, df['bb_bbh'], df['bb_bbl'], color='yellow',alpha=0.5)
plt.title("Bolinger Bands")
plt.legend()
plt.show()


## Technical Indicator - RSI Indicator Price
df.ta.rsi(close='Adj Close', length=14, append=True, signal_indicators=True, xa=60, xb=40)
df = df.rename(columns = { "RSI_14": "RSI_14_price", "RSI_14_A_60":"RSI_14_A_60_price","RSI_14_B_40":"RSI_14_B_40_price"})
plt.plot(df['RSI_14_A_60_price'],label='RSI_14_A_60_price')
plt.plot(df['RSI_14_B_40_price'],label='RSI_14_A_40_price')
plt.title(" RSI Indicator Price")
plt.legend()
plt.show()

## RSI Indicator Volume
df.ta.rsi(close='Volume', length=14, append=True, signal_indicators=True, xa=60, xb=40)
df = df.rename(columns = { "RSI_14": "RSI_14_Volume", "RSI_14_A_60":"RSI_14_A_60_Volume","RSI_14_B_40":"RSI_14_B_40_Volume"})


## ## Technical Indicator - MACD
df["ewm12"] = df["Adj Close"].ewm(span=12, adjust=False).mean()
df["ewm26"] = df["Adj Close"].ewm(span=26, adjust=False).mean()
df["macd"] = df["ewm12"]-df["ewm26"]
'''Signal Line '''
df["macd9"] = df["macd"].ewm(span=9, adjust=False).mean()
plt.plot(df['ewm12'],label='ewm12')
plt.plot(df['ewm26'],label='ewm26')
plt.plot(df['macd9'],label='macd9')
plt.title(" MACD")
plt.legend()
plt.show()

## MACD Signal and BB bands  : Buy 1 and sell -1
'''
The first type of Signal Line Crossover to examine is the Bullish Signal Line Crossover. Bullish Signal Line Crossovers occur when the MACD Line crosses above the Signal Line.
The second type of Signal Line Crossover to examine is the Bearish Signal Line Crossover. Bearish Signal Line Crossovers occur when the MACD Line crosses below the Signal Line.
'''
df["macdsignal"] = df.apply(lambda x: "Bullish" if x["macd"] > x["macd9"] else "Bearish",axis=1)
df["BBMsignal"] =  df.apply(lambda x : "Sell" if x["Adj Close"] > x["bb_bbh"] else ( "Buy" if x["Adj Close"] < x["bb_bbl"] else "Neutral") ,axis =1)
df["BBP_Signal"] = df.apply(lambda x :"Sell" if (x["bbp"] > 1 and (x["RSI_14_A_60_price"] > 0) ) else ( "Buy" if x["bbp"] < 0 and (x["RSI_14_B_40_price"] > 0) else "No Signal") ,axis =1)

df = df.dropna()
df = df.reset_index()
trace1 = go.Scatter(x=df["Date"],y=df["mv20"])
trace = go.Figure(go.Candlestick(x = df["Date"],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']))

trace.add_trace(go.Scatter(x=df["Date"],y=df["mv20"]))
trace.add_trace(go.Scatter(x=df["Date"],y=df["bb_bbh"]))
trace.add_trace(go.Scatter(x=df["Date"],y=df["bb_bbl"]))
layout = {
    'title': 'Stock Data ',
    'yaxis': {'title': 'Price'},
    'xaxis': {'title': 'Index Number'},}
#fig = dict(data=trace, layout=layout)
#plot(trace, filename='btc_candles')
testing = df[["Date","Adj Close","Close","bb_bbh","bb_bbl","BBMsignal","macdsignal","BBP_Signal" ,"RSI_14_A_60_price","RSI_14_A_60_Volume", "RSI_14_B_40_price", "RSI_14_B_40_Volume"]]
print(testing[testing["BBMsignal"] != "Neutral"])