import backtrader as bt
import datetime
import pandas as pd
import csv
import io
class mvav(bt.Strategy):
    params = (('period', 20),('devfactor', 0.005),('fast', 10),('slow',20),('lot',300),('Sell_stop_loss',-0.001),('Buy_stop_loss',-0.001),('Sell_max_profit',0.02),('Buy_max_profit',0.04))

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

        ## Moving Average
        self.ma_short = bt.ind.SMA(period=self.p.fast)  # fast moving average
        self.MA_long = bt.ind.SMA(period=self.p.slow)  # slow moving average
        #self.signal = bt.ind.CrossOver(self.ma_short,self.MA_long )


        self.long_deltacal = (1 - self.p.devfactor) * float(self.data_close[-1])
        self.short_deltacal = (1 + self.p.devfactor) * float(self.data_close[-1])

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


    def next_open(self):
        def liquidate(signal):
            ##  Assumption_1, no gap opening on closing price and next day opening price.
            liquidatePosition = 0
            if (signal > 0):
                deltacal = (1 - self.p.devfactor) * float(self.data_close[-1])
                if (self.data_close[0] > deltacal):
                    # Don't Liquidate position
                    return 1
                else:
                    # Liquidate postion
                    return -1

            elif (signal < 0):
                deltacal = (1 + self.p.devfactor) * float(self.data_close[-1])
                if (self.data_close[0] < self.short_deltacal):
                    # Don't Liquidate postion
                    return 1
                else:
                    # Liquidate postion
                    return -1
            else:
                return 0
        #
        if not self.position:
            #print("signal : {}".format(self.signal[0]))
            if self.ma_short > self.MA_long:
                if (liquidate(1) > 0):
                    self.log(
                        f'BUY CREATED --- Size: {self.p.lot}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
                    # self.buy(size=size)
                    self.buy(size=self.p.lot)

            elif self.ma_short < self.MA_long:
                if (liquidate(-1) > 0):
                    self.log(
                        f'SELL CREATED --- Size: {self.p.lot}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
                    # self.buy(size=size)
                    self.sell(size=self.p.lot)
                    print(self.position.size,self.price,self.data_close[0],self.p.Sell_stop_loss,self.p.Buy_stop_loss)

        elif (liquidate(-1) < 0 or liquidate(1) < 0 ):
            print("liquidate position")
            self.log(f'CLOSE CREATE : {self.data_close[0]:2f}')
            self.order = self.close()
            self.order.executed.price = self.data_close[0]

        elif self.ma_short > self.MA_long and self.position.size < 0:
            self.log(
                f'BUY CREATED --- Size: {2*self.p.lot}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
            # self.buy(size=size)
            self.buy(size=2*self.p.lot)

        elif self.ma_short < self.MA_long and self.position.size > 0:
            self.log(
                f'SELL CREATED --- Size: {2 * self.p.lot}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
            # self.buy(size=size)
            self.sell(size=2 * self.p.lot)

        elif (self.position.size < 0 and ((self.price - self.data_close[0])/self.price) < self.p.Sell_stop_loss) or (self.position.size > 0 and ((self.data_close[0] -self.price)/self.price) < self.p.Buy_stop_loss):
            print("closing because of loss")
            self.log(f'CLOSE CREATE : {self.data_close[0]:2f}')
            self.order = self.close()
            self.order.executed.price = self.data_close[0]

        elif (self.position.size < 0 and ((self.price - self.data_close[0])/(self.price) > self.p.Sell_max_profit)) or (self.position.size > 0 and ((self.data_close[0] -self.price)/(self.price) > self.p.Buy_max_profit)):
            print("Booking profit")
            print(self.data_close[0],self.price, self.p.Buy_max_profit)
            self.log(f'CLOSE CREATE : {self.data_close[0]:2f}')
            self.order = self.close()
            self.order.executed.price = self.data_close[0]
