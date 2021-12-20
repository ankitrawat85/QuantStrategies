import pandas as pd
import yfinance as yf
import cufflinks as cf
from plotly.offline import iplot, init_notebook_mode
init_notebook_mode()
desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',30)
df_twtr = yf.download('TWTR',
                                   start='2018-01-01',
                                   end='2018-12-31',
                                   progress=False,
                                   auto_adjust=True)
qf = cf.QuantFig(df_twtr, title="Twitter's Stock Price",
                             legend='top', name='TWTR')
#Interval required 5 minutes
data = yf.download(tickers='INFY.NS', period='3mo', interval='1h')
data = data[["Open","High","Low","Close","Adj Close","Volume"]]
print(data)