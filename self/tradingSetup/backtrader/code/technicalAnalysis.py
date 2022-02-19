import pandas as pd
import yfinance as yf
from datetime import datetime
import backtrader as bt
import backtrader.analyzers as btanalyzer
position =0


class SmaSignal(bt.Signal):
    params = (('period', 20),)

    def __init__(self):
        self.lines.signal = self.data -bt.ind.SMA(period=self.p.period)

cerebro = bt.Cerebro()
df = yf.download('AAPL',start='2000-01-01',end='2010-12-31',progress=False)
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)
cerebro.broker.setcash(1000.0)
cerebro.add_signal(bt.SIGNAL_LONG, SmaSignal)
cerebro.addobserver(bt.observers.BuySell)
cerebro.addobserver(bt.observers.Value)
cerebro.addanalyzer(btanalyzer.SharpeRatio , _name = "sharpe")
cerebro.addanalyzer(btanalyzer.Transactions , _name = "tran")
cerebro.addanalyzer(btanalyzer.TradeAnalyzer , _name = "Trade")

print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')
back = cerebro.run()
print(f'Final Portfolio Value: {cerebro.broker.getvalue():.2f}')
print(back[0].analyzers.sharpe.get_analysis())
print(back[0].analyzers.tran.get_analysis())
print(back[0].analyzers.Trade.get_analysis())
cerebro.plot()



