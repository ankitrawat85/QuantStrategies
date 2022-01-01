import pandas as pd
import yfinance as yf
import cufflinks as cf
from plotly.offline import iplot, init_notebook_mode
init_notebook_mode()
desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',30)
df  = yf.download(tickers='^NSEI', period='1wk', interval='1m')
print(df)