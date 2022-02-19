'''

Back Testing -  RSI and MV

'''

import backtrader.sizers
import pandas as pd
import yfinance as yf
import backtrader as bt
import backtrader.analyzers as btanalyzer

from self.tradingSetup.backtrader.Strategy.oldrsi import oldrsi
from self.tradingSetup.backtrader.Strategy.RSI import rsi
from self.tradingSetup.backtrader.Strategy.mvav import mvav
from self.tradingSetup.backtrader.code.analyzer import strategyParamAnalysis

desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',30)
pd.set_option('display.max_rows',2000)
import numpy as np

class GenericCSV(bt.feeds.GenericCSVData):

        lines = ('pivot', 'RSIpivot','divsignal')

        params = (('pivot', 7),
                  ('RSIpivot', 8),('divsignal', 9))

class backtestBackTrader():
    ## Create instance
    def __init__(self):
        pass

    def BackTrader(self,data):
        cerebro = bt.Cerebro(stdstats=False, cheat_on_open=True)
        #cerebro.addstrategy(mvav)
        #cerebro.addstrategy(RsiSignalStrategy)


        '''Working RSI'''
        #cerebro.optstrategy(oldrsi,Sell_stop_loss=np.arange(0.01,0.001,-0.008),RSI_long=np.arange(20,30,3),RSI_short=np.arange(5,15,3), devfactor = np.arange(0.02,0.001,-0.005),profit_mult=np.arange(2,0.01,-0.05))
        #cerebro.optstrategy(oldrsi, RSI_veryshort=1, Sell_stop_loss=0.01,RSI_long=20,RSI_Divegence=5, RSI_short=8,devfactor=0.02, profit_mult=2)

        '''working of MV'''
        cerebro.optstrategy(mvav, fast=8, slow=20,Sell_stop_loss=0.1,devfactor = 0.02, profit_mult= 2)

        #cerebro.optstrategy(mvav, fast=range(8,15,3), slow=range(20,40,5),Sell_stop_loss=np.arange(0.1,0.001,-0.005),devfactor = np.arange(0.02,0.001,-0.005), profit_mult= np.arange(0.5,2,0.05))
        #cerebro.optstrategy(mvav, fast=range(8,15,3), slow=range(20,40,5) , Sell_stop_loss = 0.001,devfactor = 0.02, profit_mult= 2)

        '''ADD Data '''
        cerebro.adddata(data)
        cerebro.broker.setcash(100000000.0)
        cerebro.broker.setcommission(commission=0.000000001)


        '''ADD Observer '''
        cerebro.addobserver(bt.observers.BuySell)
        cerebro.addobserver(bt.observers.Value)
        cerebro.addsizer(backtrader.sizers.PercentSizer, percents=100)
        cerebro.addsizer(bt.sizers.PercentSizer, percents=10)

        '''ADD Analyzer '''
        cerebro.addanalyzer(btanalyzer.SharpeRatio, _name="sharpe")
        cerebro.addanalyzer(btanalyzer.DrawDown, _name="drawdown")
        cerebro.addanalyzer(btanalyzer.Transactions, _name="tran")
        cerebro.addanalyzer(btanalyzer.TradeAnalyzer, _name="Trade")
        cerebro.addanalyzer(btanalyzer.Returns, _name="returns")
        cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame)
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")

        '''Live Graph '''
        #cerebro.addanalyzer(BacktraderPlottingLive, address="*", port=8888)
        backtest_result = cerebro.run(maxcpus=1,stdstats=False, runonce=False,safediv = False)

        '''Output - RSI / MV  '''
        #output_ = strategyParamAnalysis().rsi(backtest_result)
        output_ = strategyParamAnalysis().mv(backtest_result)
        print(output_)

         #print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
      #  print(backtest_result[0].analyzers.sharpe.get_analysis())
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

    ## Download data from Yahoo
    '''
    df = yf.download('INFY.NS',period='12mo', interval='1d', progress=False)
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index(df["Date"])
    '''
    df = yf.download(tickers='INFY.NS', period='1mo', interval='5m', progress=False)
    df = df.iloc[0:900,:]
    df = df.reset_index()
    df.rename(columns={"Datetime": "Date"}, inplace=True)
    df.Date =  pd.to_datetime(df.Date)
    df['Date'] = df['Date'].dt.tz_localize(None)
    df = df.set_index("Date")
    df = df.rename(columns = {'Open':open,'High':'high','Low':'low','Close':'close'})
    print(df.index)
    print("initial input")

    print(len(df))
    df["pivot"] = np.nan
    df["RSIpivot"] = np.nan
    df["divsignal"] = np.nan
    #df = df[["Open","High","Low","Close","Adj Close","Volume","pivot","RSIpivot","divsignal"]]
    print(df.head(10))
    df.to_csv("backtest_backtrader.csv")
    data1 = GenericCSV(dataname="backtest_backtrader.csv")
    #data1 = bt.feeds.PandasData(dataname=df)
    backtestBackTrader().BackTrader(data=data1)

    ## Connect to 5 Paisa  ##

    '''
    instance = fivepaisa().connection()
    instance.login()
    data = instance.historical_data('N', 'C', 1594, '1d', '2020-09-01', '2020-11-01')
    print(data)
    data["Datetime"] = pd.to_datetime(data["Datetime"])
    #data["Datetime"] = data["Datetime"].dt.date
    data = data.set_index(data["Datetime"])
    #data = data[["Open","High","Low","Close","Volume"]]
    print(data.tail(40))
    print(data.dtypes)
    print(len(data))
    data1 = bt.feeds.PandasData(dataname=data)
    backtestBackTrader().BackTrader(data = data1)
    '''