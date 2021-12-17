# Data manipulation
import numpy as np
import pandas as pd
import datetime
# To calculate Greeks
import mibian
import scipy

# For Plotting
import matplotlib.pyplot as plt

import pandas as pd
import yfinance as yf
import talib


import numpy as np
from candle_rankings import candle_rankings

from itertools import compress



import pandas_ta as pta
from finta import TA

## another library for technical analysis
import ta
from ta.volatility import BollingerBands,AverageTrueRange
plt.style.use("seaborn")
plt.rcParams["figure.figsize"] = [14, 8]

desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',30)
from plotly.offline import plot
import plotly.graph_objs as go
import pandas as pd

df = yf.download("INFY.NS",
                 start="2020-01-01",
                 end="2020-12-31")



bb_indicator = BollingerBands(df["Adj Close"])
df["MA10"] = talib.MA(df["Adj Close"],timeperiod = 10)
df["MA20"] = talib.MA(df["Adj Close"],timeperiod = 50)
df["RSI14"] = talib.RSI(df["Adj Close"],timeperiod = 14)
df["ATR"] = talib.ATR(df["High"],df["Low"],df["Adj Close"],timeperiod = 14)
bb_indicator = BollingerBands(df["Adj Close"])
df["upperBand"] = bb_indicator.bollinger_hband_indicator()
df["lowerBand"] = bb_indicator.bollinger_lband_indicator()
df["moving_average"] = bb_indicator.bollinger_mavg()
print(df.dropna())





