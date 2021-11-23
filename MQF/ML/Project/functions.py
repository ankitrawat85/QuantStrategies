import yfinance as yf
import keras
import tensorflow as tf
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf,plot_pacf
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import acf, pacf
import numpy as np

def test_stationarity(df, ts):
    # Determing rolling statistics
    rolmean = df[ts].rolling(window=12, center=False).mean()
    rolstd = df[ts].rolling(window=12, center=False).std()
    # Plot rolling statistics:
    orig = plt.plot(df[ts], color='blue', label='Original')
    mean = plt.plot(rolmean, color='red', label='Rolling Mean')
    std = plt.plot(rolstd, color='black', label='Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation for %s' % (ts))
    plt.xticks(rotation=45)
    plt.show(block=False)
    plt.close()

    # Perform Dickey-Fuller test:
    # Null Hypothesis (H_0): time series is not stationary
    # Alternate Hypothesis (H_1): time series is stationary

    print('Results of Dickey-Fuller Test:')
    dftest = adfuller(df[ts], autolag='AIC')  # add kpss
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic', 'p-value', '# Lags Used', 'Number of Observations Used'])

    for key, value in dftest[4].items():
        dfoutput['Critical Value (%s)' % key] = value
    print(dfoutput)

    if (dfoutput[0] < 0.05) :
        print("\n Time Series Stationary for P value 0.05 ")
    else:
        print ("\n Time Series Stationary for P value 0.05")

    return dfoutput


def acf(self, data, lags, alpha, title):
    return plot_acf(data, lags=lags, zero=False, alpha=alpha, title=title)

def pacf(self, data, lags, alpha, title):
    return plot_pacf(data, lags=lags, zero=False, alpha=alpha, title=title)

class Stockreturn:
    def logReturn(self,data,ChangeDuration):
            return np.log(data) - np.log(data.shift(ChangeDuration))

    def Pct_changeReturn(self, data,pctChangeDuration):
                return data.pct_change(periods=pctChangeDuration).dropna(axis=0)