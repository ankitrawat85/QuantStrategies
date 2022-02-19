import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import ta.momentum
import ta.trend
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',20)
pd.set_option('display.max_rows',6000)

df_ = yf.download('INFY.NS',
                      start='2020-10-01',
                      end='2022-01-08',
                      progress=False,
)
df_ = df_.dropna()
df_ = yf.download(tickers='INFY.NS', period='1mo', interval='5m', progress=False)
print(df_)
df_ = df_.reset_index()
df_.rename(columns = {"Datetime" : "Date"}, inplace = True)
df_.set_index("Date")
print(df_.head(5))
'''df_["Price_Min"] =df_["Low"].rolling(7).min()
df_["Price_Max"] = df_["High"].rolling(7).max()
df_["fibonnachi_diff"] = df_["Price_Max"]-df_["Price_Min"]
df_["level1"] = df_["Price_Max"] - 0.236 * df_["fibonnachi_diff"]
df_["level2"] = df_["Price_Max"] - 0.382 * df_["fibonnachi_diff"]
df_["level3"] = df_["Price_Max"] - 0.618 * df_["fibonnachi_diff"]

df_["Down_level1"] = df_["Price_Min"] + 0.236 * df_["fibonnachi_diff"]
df_["Down_level2"] = df_["Price_Min"] + 0.382 * df_["fibonnachi_diff"]
df_["Down_level3"] = df_["Price_Min"] + 0.618 * df_["fibonnachi_diff"]
print(df_[["Close","High","Low","Price_Min","Price_Max","fibonnachi_diff","level1","level2","level3","Down_level1","Down_level2","Down_level3"]])




df_["Pct_change"] = df_["Adj Close"].pct_change(periods=1)
df_["moving_Avg"] = df_["Pct_change"].rolling(10).mean()
df_["weekday"] =  df_.index.weekday
df_.reset_index(inplace = True )
import numpy as np
appl_ = df_[df_["weekday"] == 3].groupby([df_.Date.dt.year, df_.Date.dt.month]).last()

pct_change =  0.018

print("greater than 0.0377 ")
appl_  = appl_[["Date","Pct_change"]]
plt.plot(appl_[appl_["Pct_change"] >= pct_change]["Date"],appl_[appl_["Pct_change"] >= pct_change]["Pct_change"])
plt.show()
print(appl_[appl_["Pct_change"] >=pct_change])
print ("total count : {}".format(len(appl_[appl_["Pct_change"] >=pct_change])))
## MACD
df_["ewm12"] = df_["Close"].ewm(span=12, adjust=False).mean()
df_["ewm26"] = df_["Close"].ewm(span=26, adjust=False).mean()
df_["macd"] = df_["ewm12"] - df_["ewm26"]
##
df_["macd9"] = df_["macd"].ewm(span=9, adjust=False).mean()
df_["macdsignal"] = df_.apply(lambda x: "Bullish" if x["macd"] > x["macd9"] else "Bearish", axis=1)
df_["MACD_ta"] =  ta.trend.MACD(df_["Close"],window_slow=12,window_fast=26,window_sign=9).macd_signal()
df_["MACD_ta_diff"] =  ta.trend.MACD(df_["Close"],window_slow=12,window_fast=26,window_sign=9).macd_diff()
## RSI

#df_.ta.rsi(close='Volume', length=30, append=True, signal_indicators=True, xa=60, xb=40)
print('RSI')
df_["RSI_30Days"] = ta.momentum.rsi(df_["Close"],window=30)
df_["RSI_7Days"] = ta.momentum.rsi(df_["Close"],window=7)
df_["RSI_1Days"] = ta.momentum.rsi(df_["Close"],window=1)
'''
## RSI Divergence

class rsiDivergence:
    def myRSI(self,price, n=10):
        print("inside RSI")
        print(price)
        delta = price['Close'].diff()
        dUp, dDown = delta.copy(), delta.copy()
        dUp[dUp < 0] = 0
        dDown[dDown > 0] = 0

        RolUp = dUp.rolling(window=n).mean()
        RolDown = dDown.rolling(window=n).mean().abs()

        RS = RolUp / RolDown
        rsi = 100.0 - (100.0 / (1.0 + RS))
        print(rsi)
        return rsi

    def pivotid(self,df1, l, n1, n2):  # n1 n2 before and after candle l
        if l - n1 < 0 or l + n2 >= len(df1):
            return 0

        pividlow = 1
        pividhigh = 1
        for i in range(l - n1, l + n2 + 1):
            print(i,df1.Low[l], df1.Low[i])
            if (df1.Low[l] > df1.Low[i]):
                pividlow = 0
            if (df1.High[l] < df1.High[i]):
                pividhigh = 0
        print(i, pividlow, pividhigh)
        if pividlow and pividhigh:
            return 3
        elif pividlow:
            return 1
        elif pividhigh:
            return 2
        else:
            return 0

    def RSIpivotid(self,df1, l, n1, n2):  # n1 n2 before and after candle l
        if l - n1 < 0 or l + n2 >= len(df1):
            return 0

        pividlow = 1
        pividhigh = 1
        for i in range(l - n1, l + n2 + 1):
            print(df1.RSI[l],df1.RSI[i])
            if (df1.RSI[l] > df1.RSI[i]):
                pividlow = 0
            if (df1.RSI[l] < df1.RSI[i]):
                pividhigh = 0
        if pividlow and pividhigh:
            return 3
        elif pividlow:
            return 1
        elif pividhigh:
            return 2
        else:
            return 0

    def graph(self):
        self.df["RSI"] = self.myRSI(self.df)
        print(self.df["RSI"])
        dfpl = self.df
        from datetime import datetime

        fig = make_subplots(rows=2, cols=1)
        fig.append_trace(go.Candlestick(x=dfpl.index,
                                        open=dfpl['Open'],
                                        high=dfpl['High'],
                                        low=dfpl['Low'],
                                        close=dfpl['Close']), row=1, col=1)
        fig.append_trace(go.Scatter(
            x=dfpl.index,
            y=dfpl['RSI'],
        ), row=2, col=1)

        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.show()

    def pointpos(self,data):  ## this function for visualization and not mandatory for calcualtion
        if data['pivot'] == 1:
            return data['Low'] - 1e-3
        elif data['pivot'] == 2:
            return data['High'] + 1e-3
        else:
            return np.nan

    def RSIpointpos(self,data):  ## this function for visualization and not mandatory for calcualtion
        if data['RSIpivot'] == 1:
            return data['RSI'] - 1
        elif data['RSIpivot'] == 2:
            return data['RSI'] + 1
        else:
            return np.nan

    def divsignal(self,data,row, nbackcandles):
        backcandles = nbackcandles
        candleid = int(row.name)

        maxim = np.array([])
        minim = np.array([])
        xxmin = np.array([])
        xxmax = np.array([])

        maximRSI = np.array([])
        minimRSI = np.array([])
        xxminRSI = np.array([])
        xxmaxRSI = np.array([])

        for i in range(candleid - backcandles, candleid + 1):
            if data.iloc[i].pivot == 1:
                minim = np.append(minim, data.iloc[i].Low)
                xxmin = np.append(xxmin, i)  # could be i instead df.iloc[i].name
            if data.iloc[i].pivot == 2:
                maxim = np.append(maxim, data.iloc[i].High)
                xxmax = np.append(xxmax, i)  # df.iloc[i].name
            if data.iloc[i].RSIpivot == 1:
                minimRSI = np.append(minimRSI, data.iloc[i].RSI)
                xxminRSI = np.append(xxminRSI, data.iloc[i].name)
            if data.iloc[i].RSIpivot == 2:
                maximRSI = np.append(maximRSI, data.iloc[i].RSI)
                xxmaxRSI = np.append(xxmaxRSI, data.iloc[i].name)
        print("minimax")
        print(maxim, minim, xxmin, xxmax)
        print("RSIminmax")
        print(minim, xxmin, maxim, xxmax, maximRSI, minimRSI, xxminRSI, xxmaxRSI)
        if maxim.size < 2 or minim.size < 2 or maximRSI.size < 2 or minimRSI.size < 2:
            return 0

        slmin, intercmin = np.polyfit(xxmin, minim, 1)
        slmax, intercmax = np.polyfit(xxmax, maxim, 1)
        slminRSI, intercminRSI = np.polyfit(xxminRSI, minimRSI, 1)
        slmaxRSI, intercmaxRSI = np.polyfit(xxmaxRSI, maximRSI, 1)
        ## slmin > 0 and slmax > 0  ->  price uptream but slmaxRSI - Downtrend
        if slmin > 1e-4 and slmax > 1e-4 and slmaxRSI < -0.1:
            return "Bull Divergence - Price expected to fall"  ## Divergence expected here . Uptrend going to fall
        elif slmin < -1e-4 and slmax < -1e-4 and slminRSI > 0.1:
            return "Bear Divergence - Price expected to Rise"   ## Divergence expected here . Uptrend going to fall
        else:
            return "No divergence noticed"  # no divergance noticed

    def divsignal2(self,data,row, nbackcandles):
        backcandles = nbackcandles
        candleid = int(row.name)

        closp = np.array([])  ## Closing price value
        xxclos = np.array([]) ## index of the closing price value

        maxim = np.array([])
        minim = np.array([])
        xxmin = np.array([])
        xxmax = np.array([])

        maximRSI = np.array([])
        minimRSI = np.array([])
        xxminRSI = np.array([])
        xxmaxRSI = np.array([])

        for i in range(candleid - backcandles, candleid + 1):
            closp = np.append(closp, data.iloc[i].Close)
            xxclos = np.append(xxclos, i)
            if data.iloc[i].pivot == 1:
                minim = np.append(minim, data.iloc[i].Low)
                xxmin = np.append(xxmin, i)  # could be i instead df.iloc[i].name
            if data.iloc[i].pivot == 2:
                maxim = np.append(maxim, data.iloc[i].High)
                xxmax = np.append(xxmax, i)  # df.iloc[i].name
            if data.iloc[i].RSIpivot == 1:
                minimRSI = np.append(minimRSI, data.iloc[i].RSI)
                xxminRSI = np.append(xxminRSI, data.iloc[i].name)
            if data.iloc[i].RSIpivot == 2:
                maximRSI = np.append(maximRSI, data.iloc[i].RSI)
                xxmaxRSI = np.append(xxmaxRSI, data.iloc[i].name)

        slclos, interclos = np.polyfit(xxclos, closp, 1)

        if slclos > 1e-4 and (maximRSI.size < 2 or maxim.size < 2):
            return 0
        if slclos < -1e-4 and (minimRSI.size < 2 or minim.size < 2):
            return 0
        # signal decisions here !!!
        if slclos > 1e-4:
            if maximRSI[-1] < maximRSI[-2] and maxim[-1] > maxim[-2]:
                return "Bull Divergence - Price expected to fall"
        elif slclos < -1e-4:
            if minimRSI[-1] > minimRSI[-2] and minim[-1] < minim[-2]:
                return "Bear Divergence - Price expected to Rise"
        else:
            return "No divergence noticed"

print("graph")
print(df_)
df_["RSI"] = rsiDivergence().myRSI(price = df_)
df_['pivot'] = df_.apply(lambda x: rsiDivergence().pivotid(df_, x.name,5,5), axis=1)
df_['RSIpivot'] = df_.apply(lambda x: rsiDivergence().RSIpivotid(df_, x.name, 5, 5), axis=1)
df_['pointpos'] = df_.apply(lambda row: rsiDivergence().pointpos(row), axis=1)
df_['RSIpointpos'] = df_.apply(lambda row: rsiDivergence().RSIpointpos(row), axis=1)
df_['divSignal'] = df_.apply(lambda row: rsiDivergence().divsignal(df_,row,30), axis=1)

df_['divSignal2'] = df_.apply(lambda row: rsiDivergence().divsignal2(df_,row,30), axis=1)
print("RSI divergence_2 ")
print(df_[["Date","Close","divSignal","divSignal2"]])

'''df_ = df_.dropna()
#df_ = df_.iloc[-27:-10,:]
plt.plot(df_.Date,df_.Close)
plt.xticks(rotation=45)
plt.grid()
plt.show()

print("plt")
df_ = df_[["Date","RSI_30Days","RSI_7Days"]]
df_.set_index("Date",inplace = True)
df_.plot()
plt.grid()
plt.show()
print("30 days mean : {}".format(df_["RSI_30Days"].mean()))
print("30 days mean : {}".format(df_["RSI_7Days"].mean()))
df_ = df_[df_["RSI_30Days"] < df_["RSI_30Days"].mean()]'''