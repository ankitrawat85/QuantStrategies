from sklearn.preprocessing import LabelEncoder
from sklearn  import tree

## personal files

## System Libraries
import sys
import os

## Graph
import seaborn as sns
import numpy as np
import scipy.stats as stats
import random
import warnings
import matplotlib.pyplot as plt
import pandas as pd
import sys
'''System Path configuration'''
print (os.path.abspath(__file__))
sys.path.append('/Users/ankitrawat/Desktop/smu/Classes/Self/Code/Quant/venv/commonFunctions')
'''Import personal libraries '''
from commonFunctions import data, dataValidation, graph, stationary, models
from commonFunctions import normalization
from commonFunctions import StatFunction
from commonFunctions import models


''' Import ML libraries'''
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn import linear_model,metrics
from sklearn import preprocessing
from sklearn import model_selection
from pandas import read_csv
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from mlxtend.evaluate import bias_variance_decomp
from sklearn.model_selection import validation_curve
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import  Ridge,Lasso, ElasticNet
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.stattools import adfuller, coint
'''Graph '''
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

class Test_PortfolioAnalysis():

    def __init__(self,*args,**kargs):
        self.nse50 = "https://en.wikipedia.org/wiki/NIFTY_50"
        self.datasite = "yahoo"
        print (self.nse50)

    def processing(self):
        '''Nifty 50 List - Wikipidia '''
        df_ = pd.read_html(self.nse50)[1]
        df_ = df_.iloc[:,1:3]
        df_nse50 = df_[df_["Sector"] == "Banking"]["Symbol"]
        print ("after removing banking -->")
        print (df_nse50)
        '''Data pull for list of stocks'''
        data_start = "2010-01-01"
        data_end  = "2021-04-30"
        stock_list  = pd.DataFrame(df_nse50).stack().values
        print (stock_list)
        df_ = data().downloadData(self.datasite,stock_list, data_start, data_end,"High")
        return df_


import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
from scipy.signal import find_peaks
import statsmodels.api as sm

print ("Daily Return")
df_ = Test_PortfolioAnalysis().processing()
print ("df_......")


#print (df_["AXISBANK"])
df_ = StatFunction().logReturn(df_,1).dropna(axis =0)
df_ = pd.DataFrame(df_["AXISBANK"]).resample('M').sum()
df_.head(24).plot()
plt.show(

)

print (df_.head(10))
for i in np.arange(1,80,1):
    x = "lag_" +str(i)
    df_[x] = df_["AXISBANK"].shift(i, axis=0)

print (df_.dropna(axis =0))
df_lag =  df_.dropna(axis =0)
print(df_lag.iloc[:,-1])

Y = df_lag.iloc[:,-1]
x = df_lag.iloc[:,0:50]
X = sm.add_constant(x)
model = sm.OLS(Y,X)
results = model.fit()
print (results.summary())
print (results.params)
c = pd.DataFrame(results.params).reset_index().drop(columns="index",axis =1).iloc[1:]


x = c.index
y = c.values
fig, ax = plt.subplots()
ax.plot(x,y)
start, end = ax.get_xlim()
ax.xaxis.set_ticks(np.arange(0,50,12))
plt.show()

#X =   models().AR(df_,70)
#print(X.summary())

""" indicators"""
x_less  = argrelextrema(df_["AXISBANK"].values, np.less)
x_high  = argrelextrema(df_["AXISBANK"].values, np.greater)
print("argrelxtrema : {} ".format(x_less))
print("argrelxtrema high: {} ".format(x_high))
print (df_["AXISBANK"])
list_x = pd.DataFrame(x_less)
df_x_less = pd.DataFrame(x_less)
df_x_high = pd.DataFrame(x_high)
print (df_["AXISBANK"].iloc[1,])
print (df_["AXISBANK"].index[1])

'''

'''
import math

## Trading Strategy - Head and Sholder ##

class Interval:
    def __init__(self, start, end):
        assert start <= end
        self.start = start
        self.end  = end
    def __contains__(self, number):   # this dunder method lets you use 'in'
        return self.start <= number < self.end

for index, item in enumerate(df_x_high.transpose().values):
    if ( (item+3) < df_x_less.shape[1]):
        E1 = df_.iloc[item,0].values

        z = df_x_less.values[0][index]
        E2 = df_["AXISBANK"].iloc[z,]

        z = df_x_high.values[0][index+1]
        E3 = df_["AXISBANK"].iloc[z,]

        z = df_x_less.values[0][index+1]
        E4 = df_["AXISBANK"].iloc[z,]

        z = df_x_high.values[0][index+2]
        E5 = df_["AXISBANK"].iloc[z,]
        interval1 = Interval(((E1 + E5)/2) * -1.50, ((E1 + E5)/2) * 1.50)
        interval2 = Interval(((E1 + E5) / 2) * -1.50, ((E2 + E4) / 2) * 1.50)

        if ( E3 > E1 and E3 > E5 and E1 in interval1 and E2 in interval1 and E2 in interval2 and E4 in interval2 ):
            print("Head and Shoulder")
            print ("At Index {} ,  E1 maxima at row {} , Local minima E2 : {} , Local Maxima E3  :  {} , Local Mimima E4 : {}  & E5  :{} ".format(df_["AXISBANK"].index[item],E1,E2,E3,E4,E5))

        if ( E1 < E3 and E3 < E5 and E2 > E4 ):
            print("BROADNING TOPS - BTOPS")
            print ("At Index {} ,  E1 maxima at row {} , Local minima E2 : {} , Local Maxima E3  :  {} , Local Mimima E4 : {}  & E5  :{} ".format(df_["AXISBANK"].index[item],E1,E2,E3,E4,E5))

        if ( E1 > E3 and E3 > E5 and E2 < E4 ):
            print("Triangular  TOPS - TOPS")
            print ("At Index {} ,  E1 maxima at row {} , Local minima E2 : {} , Local Maxima E3  :  {} , Local Mimima E4 : {}  & E5  :{} ".format(df_["AXISBANK"].index[item],E1,E2,E3,E4,E5))


    else:
        break