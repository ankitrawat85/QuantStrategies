import math
import time

import backtrader as bt
import datetime
import pandas as pd
import csv
import io
import ta
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np


class oldrsi(bt.Strategy):
    params = (('RSI_Divegence',5),('RSI_long',10),('RSI_short',7),('RSI_veryshort',1),('period', 20),('devfactor', 0.005),('lot',300),('Sell_stop_loss',0.001),('profit_mult',2))
    def __init__(self):
        # keep track of close price in the series
        self.data_close = self.datas[0].close
        self.data_open = self.datas[0].open
        self.data_high = self.datas[0].high
        self.data_pivot = self.datas[0].pivot
        self.data_RSIpivot = self.datas[0].RSIpivot
        self.data_divsignal= self.datas[0].divsignal

        print("countdown1")
        print(len(self.datas[0].close))
        print((self.datas[0].close[0]))
        print("countdown_finish1")

        # keep track of pending orders/buy price/buy commission
        self.order = None
        self.price = None
        self.comm = None
        self.trades = io.StringIO()
        self.trades_writer = csv.writer(self.trades)
        #self.p.Sell_stop_loss = self.p.Buy_stop_loss
        self.earlyclosure = 0
        self.previousSignal = 0

        ##  RSI
        self.RSI_long =  bt.indicators.RSI_EMA(self.data_close,period=self.p.RSI_long, safediv = True)
        self.RSI_short = bt.indicators.RSI_EMA(self.data_close,period=self.p.RSI_short,safediv = True)
        self.RSI_Divegence = bt.indicators.RSI_EMA(self.data_close,period=self.p.RSI_Divegence,safediv = True)
        self.Buy_signal = bt.ind.CrossOver(self.RSI_short, self.RSI_long)
        #self.RSI_veryshory = ta.momentum.rsi(self.data_close[0], window=self.p.RSI_veryshory)

        ## Price change Restriction
        self.long_deltacal = (1 - self.p.devfactor) * float(self.data_close[-1])
        self.short_deltacal = (1 + self.p.devfactor) * float(self.data_close[-1])
        print("countdown")
        print(len(self.datas[0].close))
        print((self.datas[0].close[0]))
        print("countdown_finish")


    def log(self, txt):
        dt = self.datas[0].datetime.date(0).isoformat()
        print(f'{dt}, {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            self.log('ORDER SUBMITTED')
            self.order = order
            return

        if order.status in [order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            self.log('ORDER ACCEPTED')
            self.order = order
            return

        if order.status in [order.Expired]:
            self.log('BUY EXPIRED')

        elif order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED --- Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Commission: {order.executed.comm:.2f}'
                )
                self.price = order.executed.price
                self.comm = order.executed.comm
                print("Order Execute price {}".format(self.price))
            else:
                self.log(
                    f'SELL EXECUTED --- Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Commission: {order.executed.comm:.2f}'
                )
                self.price = order.executed.price
                self.comm = order.executed.comm

        elif order.status in [order.Canceled, order.Margin,order.Rejected]:
            if order.status == order.Canceled:
                self.log(f'{order.status}: Order failed because of Canceled')
            elif order.status == order.Margin:
                self.log(f'{order.status}: Order failed because of  Margin')
            elif order.status == order.Rejected:
                self.log(f'{order.status}: Order failed because of Rejected')
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(f'OPERATION RESULT --- Gross: {trade.pnl:.2f}, Net: {trade.pnlcomm:.2f}')

    def notify_store(self, msg, *args, **kwargs):
        print('*' * 5, 'STORE NOTIF:', msg)


    def next(self):
        print("inside next")
        print('RSI long :  {}'.format(self.RSI_long))
        print('Close range  : {}'.format(self.data.close.get(size=10, ago=-1)))
        print('close : {}'.format((self.datas[0].close[0])))
        print('length : {}'.format(len(self.datas[0].close)))

        if self.order:
            return

        def myRSI(df, n=10):
                print("inside RSI")
                print(df)
                delta = df['Close'].diff()
                dUp, dDown = delta.copy(), delta.copy()
                dUp[dUp < 0] = 0
                dDown[dDown > 0] = 0

                RolUp = dUp.rolling(window=n).mean()
                RolDown = dDown.rolling(window=n).mean().abs()
                RS = RolUp / RolDown
                rsi = 100.0 - (100.0 / (1.0 + RS))
                return rsi


        def pivotid(length, n1, n2):  # n1 n2 before and after candle l
                print("inside pivot")

                if length < n1+n2:
                    return 0

                pividlow = 1
                pividhigh = 1
                print(length,n1,n2,n1+n2)
                for i in range(0,n1+n2):
                    print(i,self.datas[0].low[0],self.datas[0].low[-i])
                    if (self.datas[0].low[0] >  self.datas[0].low[-i]):
                        pividlow = 0
                    if (self.datas[0].high[0]<  self.datas[0].high[-i]):
                        pividhigh = 0
                print("pividlow")
                print(pividlow,pividhigh)
                if pividlow and pividhigh:
                    print("return 3")
                    return 3
                elif pividlow:
                    print("return 1")
                    return 1
                elif pividhigh:
                    print("return 2")
                    return 2
                else:
                    print("return 0")
                    return 0

        def RSIpivotid(length, n1, n2):  # n1 n2 before and after candle l
                if length < n1+n2:
                    return 0

                pividlow = 1
                pividhigh = 1
                print("RSIpivotid")
                print(length, n1, n2, n1 + n2)
                for i in range(0,n1+n2):
                    print("RSI_long")
                    print(self.RSI_Divegence[0])
                    print("Low")
                    print(self.data.low.get(size=n1 + n2, ago=-1))
                    print("high")
                    print(self.data.high.get(size=n1 + n2, ago=-1))
                    print( i,self.RSI_Divegence[0], self.RSI_Divegence[-i])
                    if (self.RSI_Divegence >  self.RSI_Divegence[-i]):
                        pividlow = 0
                    if (self.RSI_Divegence<  self.RSI_Divegence[-i]):
                        pividhigh = 0
                print(pividlow,pividhigh)
                print("RSIpivotid")
                if pividhigh > 1:
                    print("High pividhigh -----------------------------------")
                if pividlow and pividhigh:
                    return 3
                elif pividlow:
                    return 1
                elif pividhigh:
                    return 2
                else:
                    return 0

        def divsignal(row):
                print("inside divsignal {}".format(row))
                #backcandles = nbackcandles
                candleid = int(len(self.datas[0].close))
                print(candleid)
                print("sleep")


                maxim = np.array([])
                minim = np.array([])
                xxmin = np.array([])
                xxmax = np.array([])

                maximRSI = np.array([])
                minimRSI = np.array([])
                xxminRSI = np.array([])
                xxmaxRSI = np.array([])
                print(self.data.pivot.get(size=100, ago=0))
                for i in range(-10, 0):
                    print(i)
                    print(self.datas[0].pivot[i])
                    if math.isnan(self.datas[0].pivot[i]):
                        self.datas[0].pivot[i] = pivotid(len(self.data.close)+i, 5, 5)
                        self.datas[0].RSIpivot[i] = RSIpivotid(len(self.data.close)+i, 5, 5)
                        #self.datas[0].divsignal[i] = divsignal(len(self.data.close)+i)
                        print("is Null")
                    print(i,self.datas[0].pivot[i],self.datas[0].low[i],self.datas[0].RSIpivot[i],self.RSI_Divegence[i])
                    ##
                    if self.datas[0].pivot[i] == 1:
                        print("Print inside pivot 1")
                        minim = np.append(minim, self.datas[0].low[i])
                        xxmin = np.append(xxmin, i)  # could be i instead df.iloc[i].name

                    if self.datas[0].pivot[i] == 2:
                        print("Print inside pivot 2")
                        maxim = np.append(maxim, self.datas[0].high[i])
                        xxmax = np.append(xxmax, i)  # df.iloc[i].name

                    ##
                    if self.datas[0].RSIpivot[i] == 1:
                        print("Print inside RSIpivot 1".format(len(self.datas[0].RSIpivot)))
                        minimRSI = np.append(minimRSI, self.RSI_Divegence[i])
                        xxminRSI = np.append(xxminRSI,i)
                        print(minimRSI,xxminRSI)
                    if self.datas[0].RSIpivot[i] == 2:
                        print("Print inside RSIpivot 2")
                        maximRSI = np.append(minimRSI, self.RSI_Divegence[i])
                        xxmaxRSI = np.append(xxminRSI,i)
                        print(maximRSI, xxmaxRSI)
                print("minimax")
                print(maxim,xxmax,minim,xxmin)
                print("RSIminmax")
                print(maximRSI,xxmaxRSI,minimRSI,xxminRSI)
                print(maxim.size,minim.size,maximRSI.size,minimRSI.size)
                if maxim.size < 2 or minim.size < 2 or maximRSI.size < 2 or minimRSI.size < 2:
                    return 0

                slmin, intercmin = np.polyfit(xxmin, minim, 1)
                slmax, intercmax = np.polyfit(xxmax, maxim, 1)
                slminRSI, intercminRSI = np.polyfit(xxminRSI, minimRSI, 1)
                slmaxRSI, intercmaxRSI = np.polyfit(xxmaxRSI, maximRSI, 1)
                ## slmin > 0 and slmax > 0  ->  price uptream but slmaxRSI - Downtrend
                if slmin > 1e-4 and slmax > 1e-4 and slmaxRSI < -0.1:
                    print("divsignal -1")
                    #time.sleep(30)
                    return -1
                   #return "Bull Divergence - Price expected to fall"  ## Divergence expected here . Uptrend going to fall
                elif slmin < -1e-4 and slmax < -1e-4 and slminRSI > 0.1:
                    print("divsignal 1")
                   # time.sleep(30)
                    return 1
                   # return "Bear Divergence - Price expected to Rise"  ## Divergence expected here . Uptrend going to fall
                else:
                    print("divsignal 0")
                    #time.sleep(30)
                    return 0
        print("Pivot")
        print(self.datas[0].close[0])
        print("RSI******New")
        #print(self.data.pivot.get(size=40 ,ago=-1))
        #print(self.data.RSIpivot.get(size=40, ago=-1))
        #print(self.data.divsignal.get(size=1000, ago=-1))
        if (self.datas[0].divsignal[0] > 1):
            print("*******Hello*************")
        #time.sleep(10)
        def liquidate(long, short,delta):
            Tradingsignal = 0
            liquidatePosition = 0
            if (short > long):
                deltacal = (1 - delta) * float(self.data_close[-1])
                if (self.data_close[0] > (1 - delta) * float(self.data_close[-1])):
                    Tradingsignal = 1
                    liquidatePosition = 1  # Don't Liquidate position
                    print("Tradingsignal {}, liquidatePosition {}, deltacal {}, previoclose : {}".format(Tradingsignal, liquidatePosition, deltacal,self.data_close[-1]))
                    return Tradingsignal, liquidatePosition, deltacal
                else:
                    Tradingsignal = 1
                    liquidatePosition = -1  # Liquidate postion
                    print("Tradingsignal {}, liquidatePosition {}, deltacal {}, previoclose : {}".format(Tradingsignal,
                                                                                                         liquidatePosition,
                                                                                                         deltacal,
                                                                                  self.data_close[
                                                                                                             -1]))

                    return Tradingsignal, liquidatePosition, deltacal

            elif (short < long):

                deltacal = (1 + delta) * float(self.data_close[-1])

                if (self.data_close[0] < (1 + delta) * self.data_close[-1]):
                    Tradingsignal = -1
                    liquidatePosition = 1  # Don't Liquidate postion
                    print("Tradingsignal {}, liquidatePosition {}, deltacal {}, previoclose : {}".format(Tradingsignal,
                                                                                                         liquidatePosition,
                                                                                                         deltacal,
                                                                                                         self.data_close[
                                                                                                             -1]))
                    return Tradingsignal, liquidatePosition, deltacal
                else:
                    Tradingsignal = -1
                    liquidatePosition = -1  # Liquidate postion
                    print("Tradingsignal {}, liquidatePosition {}, deltacal {}".format(Tradingsignal, liquidatePosition,
                                                                                       deltacal))

                    return Tradingsignal, liquidatePosition, deltacal
            else:
                return 0, 1, 0
        #
        if self.p.RSI_long > self.p.RSI_short:
            Tradingsignal, liquidatePosition, deltacal = liquidate(self.RSI_long,self.RSI_short, self.p.devfactor)
            if not self.position:
                ##
                #self.datas[0].pivot[0] = pivotid(len(self.data.close), 5, 5)
                #self.datas[0].RSIpivot[0] = RSIpivotid(len(self.data.close), 5, 5)
                self.datas[0].divsignal[0] = divsignal(len(self.data.close))
                print("not position -------")
                print(self.datas[0].pivot[0],self.datas[0].RSIpivot[0], self.datas[0].divsignal[0])
                ##
                print(Tradingsignal,self.previousSignal,self.datas[0].divsignal[0],len(self.datas[0].divsignal),self.datas[0].close[0])
                print(Tradingsignal)
                print(liquidatePosition)
                print(self.previousSignal)
                print(self.datas[0].divsignal[0])

                if ((Tradingsignal == 1) & (liquidatePosition == 1) & (self.previousSignal != Tradingsignal) ) :
                        print("buy created")
                        self.log(
                            f'BUY CREATED --- Size: {self.p.lot}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
                        # self.buy(size=size)
                        self.order = self.buy(size=self.p.lot,price=self.data.close[0],exectype=bt.Order.Limit)
                        print(self.position.size, self.price, self.data_close[0],self.data_close[-1], self.p.Sell_stop_loss)
                        #self.previousSignal = Tradingsignal
                        #self.earlyclosure = 0

                elif (Tradingsignal == -1) & (liquidatePosition == 1) & (self.previousSignal != Tradingsignal) :
                        print("&&&")

                        self.log(
                            f'SELL CREATED --- Size: {self.p.lot}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
                        self.order = self.sell(size=self.p.lot,price=self.data.close[0],exectype=bt.Order.Limit)
                        print(self.position.size, self.price, self.data_close[0],self.data_close[-1], self.p.Sell_stop_loss)
                        #self.previousSignal = Tradingsignal
                        #self.earlyclosure = 0
                else:
                    print("finish")
            else:
                print('inside else')
                if (liquidatePosition ==-1):
                    self.log(f'CLOSE CREATE - liquidate position : {self.data_close[0]:2f}')
                    self.order = self.close(exectype=bt.Order.Market,price=self.data.close[0])
                    #self.earlyclosure = 1

                elif ((self.position.size < 0 ) and (self.data_close >= self.price * (1.0 + (self.p.Sell_stop_loss)))):
                    self.order = self.close(exectype=bt.Order.Limit,price=self.data.close)
                    self.log(f'CLOSE CREATE - Loss : {self.data_close[0]:2f}, position : {self.position.size} , limit : {self.price * (1.0 + (self.p.Sell_stop_loss))}')
                    #self.earlyclosure =1

                elif ((self.position.size < 0 ) and (self.data_close <= self.price * (1.0 - self.p.profit_mult *(self.p.Sell_stop_loss)))):
                    self.order = self.close(price=self.data.close,exectype=bt.Order.Limit)
                    self.log(f'CLOSE CREATE - profit: {self.data_close[0]:2f}, position : {self.position.size} , limit : {self.price * (1.0 - self.p.profit_mult *(self.p.Sell_stop_loss))}')
                    #self.earlyclosure = 1

                elif ((self.position.size > 0) and (self.data_close <= self.price * (1.0 - (self.p.Sell_stop_loss)))):
                    self.order = self.close(exectype=bt.Order.Limit,price = self.price * (1.0 - (self.p.Sell_stop_loss)))
                    self.log(f'CLOSE CREATE - loss : {self.data_close[0]:2f}, position : {self.position.size} , limit : {self.price * (1.0 - (self.p.Sell_stop_loss))}')
                    #self.earlyclosure = 1

                elif ((self.position.size > 0) and self.data_close > self.price * (1.0 + self.p.profit_mult * (self.p.Sell_stop_loss))):
                    self.order = self.close(exectype=bt.Order.Limit,price=self.data.close[0])
                    self.log(f'CLOSE CREATE - profit: {self.data_close[0]:2f}, position : {self.position.size} , limit : {self.price * (1.0 + self.p.profit_mult * (self.p.Sell_stop_loss))}')
                    #self.earlyclosure = 1
        else:
            print("Doest fit")
