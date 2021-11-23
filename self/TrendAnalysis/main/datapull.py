import pandas as pd
import numpy as np
from pandas_datareader import data
from sklearn import preprocessing
import yfinance as yf
from sklearn import preprocessing
import datetime
import pandas as pd
import pandas_datareader as pdr
import numpy as np
import statsmodels.api as sm
import warnings

import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

## Libraries - Stats Model
import statsmodels.tsa.stattools
from statsmodels.tsa.stattools import adfuller
import statsmodels.tsa.x13
from statsmodels.tsa.x13 import x13_arima_select_order, _find_x12
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import acf, pacf
import statsmodels.graphics.tsaplots as tsaplots

from sklearn import preprocessing

warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt
import statsmodels.tsa.stattools
from statsmodels.tsa.stattools import adfuller
import statsmodels.tsa.x13
from statsmodels.tsa.x13 import x13_arima_select_order, _find_x12
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import acf, pacf
import statsmodels.graphics.tsaplots as tsaplots

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARMA

## Grah
import seaborn as sns
import numpy as np
import scipy.stats as stats
import random
import warnings
import matplotlib.pyplot as plt



class  data():
    
    def __init__(self):
        
        self.scale = 1
        self.MinMaxScaler = 2
        self.normalize = 3
        self.StandardScaler = 4
        self.fit_transform = 1
    
    def downloadData(self,source ,stock,start,end,col :list):
        
        if (str(source).lower() == "yahoo"):
            df_sbin = yf.download(stock, start, end)
            return df_sbin[col]
        else:
            print ("source is not in the configured list")
    
    def logReturn(self,data):
        return np.log(data) - np.log(data.shift(1))
    
    def dataNormalization(self,data,logic,fit_transform):
        print ("inside denormalization")
        print (data.head(5))
        
        if (logic == self.scale):
            if (fit_transform == self.fit_transform):
                return pd.DataFrame(preprocessing.scale.fit_transform(data), columns = pd.DataFrame(data).columns)
            else:
                return pd.DataFrame(preprocessing.scale(data), columns = pd.DataFrame(data).columns)

        
        elif (logic == self.MinMaxScaler):
            if (fit_transform == self.fit_transform):
                print ("inside MinMaxScaler-p----------")
                return pd.DataFrame(preprocessing.MinMaxScaler.fit_transform(data), columns = data.columns)
            else:
                print (data)
                return pd.DataFrame(preprocessing.MinMaxScaler(data), columns = pd.DataFrame(data).columns)
       
        
        elif (logic == self.normalize):
            if (fit_transform == self.fit_transform):
                 print ("inside normalize-p----------")
                 return pd.DataFrame(preprocessing.normalize.fit_transform(data), columns = pd.DataFrame(data).columns)
            else:
                 return pd.DataFrame(preprocessing.normalize(data), columns = pd.DataFrame(data).columns)
                 
        
        elif (logic == self.StandardScaler):
            if (fit_transform == self.fit_transform):
                return pd.DataFrame(preprocessing.StandardScaler.fit_transform(data), columns = pd.DataFrame(data).columns)
            else:
                return pd.DataFrame(preprocessing.StandardScaler(data), columns = pd.DataFrame(data).columns)
        else:
            print ("Value not found")
        
        
class dataValidation():
    def Dickey_Fuller_test(self,data):
        return adfuller(data)
    
class graph():
    
    def acf(self,data,lags,alpha,title):
        return plot_acf(data,lags =lags,zero = False,alpha = alpha,title=title)
    
    def pacf(self,data,lags,alpha,title):
        return plot_pacf(data,lags =lags,zero = False,alpha = alpha,title=title)

class stationary():
     def seasonal_decompose(self,data,freq):
         return seasonal_decompose(data, freq=freq)

class models():
    
    def AR(self,data,p):
        return sm.tsa.ARMA(data, (p,0)).fit(disp=-1)
    
    def MA(self,data,q):
        return sm.tsa.ARMA(data, (0,q)).fit(disp=-1)
    
    def ARMA(self,data,p,q):
        return sm.tsa.ARMA(data, (p,q)).fit(disp=-1)

import os
print (os.path.abspath(__file__))