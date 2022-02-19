import backtrader as bt
import datetime
import pandas as pd
import csv
import io
class mvav(bt.Strategy):
    params = (('period', 20),('devfactor', 0.005),('fast', 10),('slow',20),('lot',300),('Sell_stop_loss',0.001),('profit_mult',2))
    def __init__(self):
        # keep track of close price in the series
        self.data_close = self.datas[0].close
        self.data_open = self.datas[0].open
        # keep track of pending orders/buy price/buy commission
        self.order = None
        self.price = None
        self.comm = None
        self.trades = io.StringIO()
        self.trades_writer = csv.writer(self.trades)
        self.earlyclosure = 0
        self.previousSignal = 0

        ## Moving Average
        print("self.params.fast : {} {}".format(self.params.fast,self.params.slow) )
        print("Data : ".format(self.datas[0]))
        self.ma_short = bt.ind.SMA(period=self.params.fast)  # fast moving average
        self.MA_long = bt.ind.SMA(period=self.params.slow)  # slow moving average
        #self.signal = bt.ind.CrossOver(self.ma_short,self.MA_long )
        self.long_deltacal = (1 - self.p.devfactor) * float(self.data_close[-1])
        self.short_deltacal = (1 + self.p.devfactor) * float(self.data_close[-1])

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
        if self.order:
            return

        def liquidate_1(mv_t1, mv_t2,delta):
            Tradingsignal = 0
            liquidatePosition = 0
            if (mv_t1 > mv_t2):
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

            elif (mv_t1 < mv_t2):

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
        if self.p.fast < self.p.slow:
            Tradingsignal, liquidatePosition, deltacal = liquidate_1(self.ma_short, self.MA_long, self.p.devfactor)
            print("Details")
            print(self.position.size, self.price, self.data_close[0],self.data_close[-1], self.p.Sell_stop_loss)
            if not self.position:
                print(Tradingsignal,self.previousSignal)
                if (Tradingsignal == 1) & (liquidatePosition == 1) & (self.previousSignal != Tradingsignal) :
                        print("inside")
                        self.log(
                            f'BUY CREATED --- Size: {self.p.lot}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
                        # self.buy(size=size)
                        self.order = self.buy(size=self.p.lot,price=self.data.close[0],exectype=bt.Order.Limit)
                        print(self.position.size, self.price, self.data_close[0],self.data_close[-1], self.p.Sell_stop_loss)
                        #self.previousSignal = Tradingsignal
                        #self.earlyclosure = 0

                elif (Tradingsignal == -1) & (liquidatePosition == 1) & (self.previousSignal != Tradingsignal):
                        self.log(
                            f'SELL CREATED --- Size: {self.p.lot}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
                        self.order = self.sell(size=self.p.lot,price=self.data.close[0],exectype=bt.Order.Limit)
                        print(self.position.size, self.price, self.data_close[0],self.data_close[-1], self.p.Sell_stop_loss)
                        #self.previousSignal = Tradingsignal
                        #self.earlyclosure = 0
            else:
                if (liquidatePosition ==-1):
                    self.log(f'CLOSE CREATE - liquidate position : {self.data_close[0]:2f}')
                    self.order = self.close(exectype=bt.Order.Market,price=self.data.close[0])
                    #self.earlyclosure = 1

                elif ((self.position.size < 0 ) and (self.data_close >= self.price * (1.0 + (self.p.Sell_stop_loss)))):
                    self.order = self.close(exectype=bt.Order.Limit,price=self.data.close)
                    self.log(f'CLOSE CREATE - Loss : {self.data_close[0]:2f}, position : {self.position.size} , limit : {self.price * (1.0 + (self.p.Sell_stop_loss))}')
                    #self.earlyclosure =1

                elif ((self.position.size < 0 ) and (self.data_close < self.price * (1.0 - self.p.profit_mult *(self.p.Sell_stop_loss)))):
                    self.order = self.close(price=self.data.close,exectype=bt.Order.Limit)
                    self.log(f'CLOSE CREATE - profit: {self.data_close[0]:2f}, position : {self.position.size} , limit : {self.price * (1.0 - self.p.profit_mult *(self.p.Sell_stop_loss))}')
                    #self.earlyclosure = 1
                elif ((self.position.size > 0) and (self.data_close < self.price * (1.0 - (self.p.Sell_stop_loss)))):
                    self.order = self.close(exectype=bt.Order.Limit,price = self.price * (1.0 - (self.p.Sell_stop_loss)))
                    self.log(f'CLOSE CREATE - loss : {self.data_close[0]:2f}, position : {self.position.size} , limit : {self.price * (1.0 - (self.p.Sell_stop_loss))}')
                    #self.earlyclosure = 1
                elif ((self.position.size > 0) and self.data_close > self.price * (1.0 + self.p.profit_mult * (self.p.Sell_stop_loss))):
                    self.order = self.close(exectype=bt.Order.Limit,price=self.data.close[0])
                    self.log(f'CLOSE CREATE - profit: {self.data_close[0]:2f}, position : {self.position.size} , limit : {self.price * (1.0 + self.p.profit_mult * (self.p.Sell_stop_loss))}')
                    #self.earlyclosure = 1
        else:
            print("Doest fit")
