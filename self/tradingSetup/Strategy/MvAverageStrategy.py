import backtrader as bt
import datetime
import pandas as pd
import csv
import io
class MvAverageStrategy(bt.Strategy):
    params = (('period', 20),
              ('devfactor', 2.0),('MA_short', 20),('MA_long', 20),('lot',300))

    def __init__(self):
        print("inside init")
        # keep track of close price in the series
        self.data_close = self.datas[0].close
        self.data_open = self.datas[0].open
        print("open up")
        # keep track of pending orders/buy price/buy commission
        self.order = None
        self.price = None
        self.comm = None
        self.trades = io.StringIO()
        self.trades_writer = csv.writer(self.trades)
        self.liquidatePosition = 0

        ## Moving Average
        self.ma_short = bt.indicators.SMA(period=self.p.MA_short)
        self.MA_long = bt.indicators.SMA(period=self.p.MA_long)
        self.buy_signal = bt.ind.CrossOver(self.ma_short,
                                           self.MA_long )
        self.sell_signal = bt.ind.CrossOver(self.MA_long ,
                                            self.ma_short)
    def liquidate(self,signal):
        ##  Assumption_1, no gap opening on closing price and next day opening price.
        liquidatePosition = 0
        if (signal > 1):
            deltacal = (1 - self.p.devfactor) * float(self.data_close[-1])
            if (self.data_close[0] > deltacal):
                 # Don't Liquidate position
                return  1
            else:
                 # Liquidate postion
                return  -1

        elif (signal < 0):
            deltacal = (1 + self.p.devfactor) * float(self.data_close[-1])
            if (self.data_close[0] < deltacal) :
                #Don't Liquidate postion
                return 1
            else:
                # Liquidate postion
                return  -1
        else:
            return  0


    def log(self, txt):
        dt = self.datas[0].datetime.date(0).isoformat()
        print(f'{dt}, {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
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


    def next_open(self):
        liquidate = MvAverageStrategy().liquidate(self.buy_signal)
        if  self.position == 0:
            if (self.buy_signal > 0 and liquidate > 0):
                print(self.buy_signal,liquidate)
                self.log(
                    f'BUY CREATED --- Size: {self.p.lot}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
                #self.buy(size=size)
                self.buy(size=self.p.lot)

            elif (self.sell_signal < 0 and liquidate > 0):
                self.log(
                    f'SELL CREATED --- Size: {self.p.lot}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
                # self.buy(size=size)
                self.buy(size=self.p.lot)

        elif self.position > 0:
            if (self.sell_signal < 0 and liquidate > 0):
                self.log(
                    f'SELL CREATED --- Size: {2*self.p.lot}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
                # self.buy(size=size)
                self.sell(size=self.p.lot)

            if (self.buy_signal > 0 and liquidate < 0):
                self.log(f'SELL CREATED --- Size: {self.position.size}')
                self.sell(size=self.position.size)

        elif self.position < 0:
            if (self.buy_signal < 0 and liquidate > 0):
                self.log(
                    f'BUY CREATED --- Size: {2 * self.p.lot}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
                # self.buy(size=size)
                self.sell(size=self.p.lot)

            elif (self.sell_signal > 0 and liquidate < 0):
                self.log(f'SELL CREATED --- Size: {self.position.size}')
                self.sell(size=self.position.size)