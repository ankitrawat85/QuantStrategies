# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 11:57:49 2020

@author: User1
"""

import pandas as pd
import ta

# read data
df = pd.read_csv('C:/DATA/NSE/Equity/NIFTY.csv')

# convert the Date column from string datatype to datetime datatype
df['Date'] = pd.to_datetime(df['Date'])

# set the Date column as the index column
df = df.set_index(keys='Date')

# add columns for all the various indicators all together (the default values of the parameters of each indicator gets used in this case
df1 = ta.add_all_ta_features(df, open='Open', high='High', low='Low', close='Close', volume='Turnover (Rs. Cr)', fillna=True  )


# to add indicator with non default parameter values

# create the object for the required indicator
rsi = ta.momentum.rsi(close = df['Close'])
# use the object to add the indicator values as a column to the dataframe, if needed
df['RSI'] = rsi

# create the object for the required indicator
bb_indicator = ta.volatility.BollingerBands(close = df['Close'], n = 50, ndev = 2)

# use the object to add different indicator columns to the dataframe, if needed
df['bb_avg'] = bb_indicator.bollinger_mavg()
df['bb_high'] = bb_indicator.bollinger_hband()

# create the object for the required indicator
macd = ta.trend.MACD(close = df['Close'], n_slow = 18, n_fast = 5, n_sign = 7, fillna=True)

# use the object to add different indicator columns to the dataframe, if needed
df['MACD'] = macd.macd()
df['MACD_signal'] = macd.macd_signal()
df['MACD_hist'] = macd.macd_diff()


# another stock example
data = pd.read_csv('C:/DATA/NSE/Equity/ACC.csv')
data['Date'] = pd.to_datetime(data['Date'])
data = data.set_index(keys='Date')

rsi = ta.momentum.rsi(close = data['Close'], n = 9)
data['RSI'] = rsi





