import backtrader.sizers
import pandas as pd
import yfinance as yf
from datetime import datetime
import backtrader as bt
import backtrader.analyzers as btanalyzer
from  self.tradingSetup.Strategy.BBand_Strategy import BBand_Strategy
from  self.tradingSetup.Strategy.SmaStrategy import SmaSignal
from  self.tradingSetup.Strategy.Rsi import RsiSignalStrategy
import datetime
class backtestBackTrader():
    ## Create instance
    def __init__(self):
        pass

    def BackTrader(self,data,brokercash,strategy):
        cerebro = bt.Cerebro(stdstats=False, cheat_on_open=True)
        cerebro.addstrategy(BBand_Strategy)
        cerebro.adddata(data)
        cerebro.broker.setcash(10000000000.0)
        cerebro.broker.setcommission(commission=0.001)
        cerebro.addobserver(bt.observers.BuySell)
        cerebro.addobserver(bt.observers.Value)
        cerebro.addsizer(backtrader.sizers.PercentSizer, percents=95)
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='time_return')
        cerebro.addanalyzer(btanalyzer.SharpeRatio, _name="sharpe")
        cerebro.addanalyzer(btanalyzer.Transactions, _name="tran")
        cerebro.addanalyzer(btanalyzer.TradeAnalyzer, _name="Trade")

        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        backtest_result = cerebro.run()
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
        print(backtest_result[0].analyzers.sharpe.get_analysis())
        #print(backtest_result[0].analyzers.tran.get_analysis())
        #print(backtest_result[0].analyzers.Trade.get_analysis())
        cerebro.plot(iplot=True, volume=False)
        #print(backtest_result[0].analyzers.returns.get_analysis())
        returns_dict = backtest_result[0].analyzers.time_return.get_analysis()
        returns_df = pd.DataFrame(list(returns_dict.items()),
                                  columns=['report_date', 'return']) \
            .set_index('report_date')
        returns_df.plot(title='Portfolio returns')

if __name__ == "__main__":
    data = bt.feeds.YahooFinanceData(
        dataname='AAPL',
        fromdate=datetime.datetime(2020, 1, 1),
        todate=datetime.datetime(2021, 12, 31)
    )
    df = yf.download('^NSEI',
                     start='2021-01-01',
                     end='2021-12-31',
                     progress=False)
    df.rename(columns= {"Open":"Open","High":"high","Low":"low","Close":"close","Volume":"volume"}, inplace= True)
    data1 = bt.feeds.PandasData(dataname=df)
    backtestBackTrader().BackTrader(data = data1,brokercash = 100000000,strategy=RsiSignalStrategy)