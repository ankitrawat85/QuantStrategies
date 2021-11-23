import pandas as pd
import pandas_datareader as pdr
import numpy as np
import statsmodels.api as sm
import warnings
import yfinance as yf
import keras
import tensorflow as tf
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf,plot_pacf
## Import my set of set of functions
from functions import test_stationarity,Stockreturn


##  Version verification
print(tf.__version__)
print(keras.__version__)
##

# 1. Data Download - Stock - 20 years - Daily : Open, Close, High , Low , Volume
data_start = "1994-01-01"
data_end = "2021-04-30"
df =yf.download("MSFT", data_start, data_end)
df_ = df.copy()

"""2.Make Data Stationary """
# 1. Log return - rolling 22 days
df_ = df_.pct_change(periods=30).dropna(axis=0)

""" 3. Time series is stationarity  : ADF test"""
test_stationarity(df_, 'Close')

"""4.Test Collinearity between lagged terms using ACF and PCF """
N, M = 5, 5
fig, ax = plt.subplots(2,2,figsize=(N,M))
plot_acf(df_.Close,lags =10, title="AutoCorrelation",ax=ax[0][0])
plot_pacf(df_.Close,lags =10, title="Partial AutoCorrelation",ax=ax[0][1])
plt.show()
