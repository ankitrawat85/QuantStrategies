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
from ta.momentum import StochasticOscillator
from ta.volume import VolumePriceTrendIndicator
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
"""
TICKER = "INFY.NS"
df  = yf.download(tickers='INFY.NS', period='1mo', interval='5m')
df  = df [["Open", "High", "Low", "Close", "Adj Close", "Volume"]]
df  = df .reset_index()
df  = df .rename(columns={"Datetime": "Date"})
df = df[df["Volume"] != 0]
"""
class technicalIndicators:
    def indicators(self,df,longer_period,shorter_period,signalperiod):
    ## Technical Indicator - Bolinger Band
        df["mv20"] = df['Close'].rolling(window=shorter_period).mean()
        indicator_bb = BollingerBands(close=df["Close"], window=shorter_period, window_dev=2)
        df['bb_bbm'] = df['Close'].rolling(shorter_period).mean()
        df['bb_bbh'] = indicator_bb.bollinger_hband()
        df['bb_bbl'] = indicator_bb.bollinger_lband()
        df['bbp'] = (df['Close'] - df['bb_bbl']) / (df['bb_bbh'] - df['bb_bbl'])
        '''
        plt.plot(df['bb_bbh'],label='Upper')
        plt.plot(df['bb_bbm'],label='Middle')
        plt.plot(df['bb_bbl'],label='Lower')
        plt.plot(df['Adj Close'],label='Adj Close')
        plt.fill_between(df.index, df['bb_bbh'], df['bb_bbl'], color='yellow',alpha=0.5)
        plt.title("Bolinger Bands")
        plt.legend()
        plt.show()
        '''
        ## Technical Indicator - RSI Indicator Price  -ome of the popular leading indicators are RSI and stochastic oscillators.
        df.ta.rsi(close='Close', length=shorter_period, append=True, signal_indicators=True, xa=60, xb=40)
        df = df.rename(columns = { "RSI_"+str(shorter_period): "RSI_"+str(shorter_period)+"_price", "RSI_"+str(shorter_period)+"_A_60":"RSI_"+str(shorter_period)+"_A_60_price","RSI_"+str(shorter_period)+"_B_40":"RSI_"+str(shorter_period)+"_B_40_price"})
        '''
        plt.plot(df['RSI_14_A_60_price'],label='RSI_14_A_60_price')
        plt.plot(df['RSI_14_B_40_price'],label='RSI_14_A_40_price')
        plt.title(" RSI Indicator Price")
        plt.legend()
        plt.show()
        '''
        ## RSI Indicator Volume
        df.ta.rsi(close='Volume', length=shorter_period, append=True, signal_indicators=True, xa=60, xb=40)

        df = df.rename(columns={"RSI_"+str(shorter_period): "RSI_" + str(shorter_period) + "_Volume",
                            "RSI_" + str(shorter_period) + "_A_60": "RSI_" + str(shorter_period) + "_A_60_Volume",
                            "RSI_" + str(shorter_period) + "_B_40": "RSI_" + str(shorter_period) + "_B_40_Volume"})

        #df = df.rename(columns = { "RSI_14": "RSI_14_Volume", "RSI_14_A_60":"RSI_14_A_60_Volume","RSI_14_B_40":"RSI_14_B_40_Volume"})

        ## ## Technical Indicator - MACD
        df["ewm12"] = df["Close"].ewm(span=shorter_period, adjust=False).mean()
        df["ewm26"] = df["Close"].ewm(span=longer_period, adjust=False).mean()
        df["macd"] = df["ewm12"]-df["ewm26"]
        '''Signal Line '''
        df["macd9"] = df["macd"].ewm(span=signalperiod, adjust=False).mean()
        '''
        plt.plot(df['ewm12'],label='ewm12')
        plt.plot(df['ewm26'],label='ewm26')
        plt.plot(df['macd9'],label='macd9')
        plt.title(" MACD")
        plt.legend()
        plt.show()
        '''

        ## VPT - Volume price trend  mainly for long term - 25-30 days

        df["VPT"] = VolumePriceTrendIndicator(close=df.Close,volume=df.Volume).volume_price_trend().pct_change(shorter_period)

        ## Stochastic Osicallator  - ome of the popular leading indicators are RSI and stochastic oscillators.
        '''
        Traditional settings use 80 as the overbought threshold and 20 as the oversold threshold
        '''
        df["StochasticOscillator"] = StochasticOscillator(high = df.High,close =df.Close,low=df.Low,window=14,smooth_window=3).stoch()
        df["StochasticOscillator_signal"] = df["StochasticOscillator"].apply(lambda x: "Overbought" if (x > 80) else ("OverSold" if x< 20 else ( "Bearish_divergence" if x < 50 else "Bullish Divergence") ))

        ## MACD Signal and BB bands  : Buy 1 and sell -1
        '''
        The first type of Signal Line Crossover to examine is the Bullish Signal Line Crossover.
         Bullish Signal Line Crossovers occur when the MACD Line crosses above the Signal Line.
        The second type of Signal Line Crossover to examine is the Bearish Signal Line Crossover. 
        Bearish Signal Line Crossovers occur when the MACD Line crosses below the Signal Line.
        '''
        df["macdsignal"] =  df.apply(lambda x: "Bullish" if x["macd"] > x["macd9"] else "Bearish",axis=1)
        df["BBMsignal"] = df.apply(lambda x : "Sell" if x["Close"] > x["bb_bbh"] else ( "Buy" if x["Close"] < x["bb_bbl"] else "Neutral") ,axis =1)
        df["BBP_Signal_price"] = df.apply(lambda x :"Sell" if (x["bbp"] > 1 and (x["RSI_"+str(shorter_period)+"_A_60_price"] > 0) ) else ( "Buy" if x["bbp"] < 0 and (x["RSI_"+str(shorter_period)+"_B_40_price"] > 0) else "No Signal") ,axis =1)

        '''
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
        '''
        #testing = df[["Close","Close","bb_bbh","bb_bbl","BBMsignal","macdsignal","BBP_Signal" ,"RSI_14_A_60_price","RSI_14_A_60_Volume", "RSI_14_B_40_price", "RSI_14_B_40_Volume"]]
        #print(testing[testing["BBMsignal"] != "Neutral"])
        return df.set_index('Datetime')