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

    def RSIpivotid(self,df1,rsicolumn, l, n1, n2):  # n1 n2 before and after candle l
        if l - n1 < 0 or l + n2 >= len(df1):
            return 0

        pividlow = 1
        pividhigh = 1
        for i in range(l - n1, l + n2 + 1):
            print(df1[rsicolumn][l],df1[rsicolumn][i])
            if (df1[rsicolumn][l] > df1[rsicolumn][i]):
                pividlow = 0
            if (df1[rsicolumn][l] < df1[rsicolumn][i]):
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

    def RSIpointpos(self,data,rsicolumn):  ## this function for visualization and not mandatory for calcualtion
        if data['RSIpivot'] == 1:
            return data[rsicolumn] - 1
        elif data['RSIpivot'] == 2:
            return data[rsicolumn] + 1
        else:
            return np.nan

    def divsignal(self,data,row, nbackcandles,rsicolumn):
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
            print(i)
            if data.iloc[i].pivot == 1:
                minim = np.append(minim, data.iloc[i].Low)
                xxmin = np.append(xxmin, i)  # could be i instead df.iloc[i].name
            if data.iloc[i].pivot == 2:
                maxim = np.append(maxim, data.iloc[i].High)
                xxmax = np.append(xxmax, i)  # df.iloc[i].name
            if data.iloc[i].RSIpivot == 1:
                minimRSI = np.append(minimRSI, data[rsicolumn].iloc[i])
                xxminRSI = np.append(xxminRSI, data.iloc[i].name)
            if data.iloc[i].RSIpivot == 2:
                print(data.columns)
                print(data[rsicolumn])
                maximRSI = np.append(maximRSI, data[rsicolumn].iloc[i])
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

    def divsignal2(self,data,row,nbackcandles,rsicolumn):
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
                minimRSI = np.append(minimRSI, data[rsicolumn].iloc[i])
                xxminRSI = np.append(xxminRSI, data.iloc[i].name)
            if data.iloc[i].RSIpivot == 2:
                maximRSI = np.append(maximRSI, data[rsicolumn].iloc[i])
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


    def rsiDivergenceindicator(self,data,rsicolumn,candleduration_before,candleduration_after,nbackcandles):
        #df_["RSI"] = rsiDivergence().myRSI(price = df_)
        data =data.reset_index()
        data['pivot'] = data.apply(lambda x: rsiDivergence().pivotid(data, x.name,candleduration_before,candleduration_after), axis=1)

        data['RSIpivot'] = data.apply(lambda x: rsiDivergence().RSIpivotid(data,rsicolumn, x.name, candleduration_before, candleduration_after), axis=1)

        data['pointpos'] = data.apply(lambda row: rsiDivergence().pointpos(row), axis=1)

        #df_['RSIpointpos'] = df_.apply(lambda row: rsiDivergence().RSIpointpos(row,rsicolumn), axis=1)
        data['divSignal'] = data.apply(lambda row: rsiDivergence().divsignal(data,row,nbackcandles,rsicolumn), axis=1)

        data['divSignal2'] = data.apply(lambda row: rsiDivergence().divsignal2(data, row,nbackcandles,rsicolumn), axis=1)
        return data

        #print("RSI divergence_2 ")
        #print(df_[["Date","Close","divSignal","divSignal2"]])
