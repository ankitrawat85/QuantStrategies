import sys
sys.path.append('/Users/ankitrawat/Desktop/smu/Classes/Self/vstudio/Quant/venv/TSMOM/main')
from datapull import data,dataValidation,graph,stationary,models
import os
## Grah
import seaborn as sns
import numpy as np
import scipy.stats as stats
import random
import warnings
import matplotlib.pyplot as plt

'''Directory Path'''
#print ("os.path.abspath(__file__))

'''Data Download'''
df_ = data().downloadData("yahoo","SBIN.NS","2010-01-01","2021-04-30") 

''' Return'''

df_["Close_return"] = data().logReturn(df_["Close"])
dataValidation = dataValidation()
print(dataValidation.Dickey_Fuller_test(df_["Close_return"].dropna()))


'''Graph - Trend Analysis'''
decompose_result=  stationary().seasonal_decompose(df_["Close_return"].dropna(),12)
df_trend = decompose_result.trend
df_season = decompose_result.seasonal
df_residual = decompose_result.resid
Qtr_1 = [1,2,3]
Qtr_2 = [1,2,3]
Qtr_3 = [1,2,3]
Qtr_4 = [10,11,12]
yearlist = [2013]
N, M = 10, 10
fig, ax = plt.subplots(2,2,figsize=(N,M))

## Trend Analysis 
df_trend[(df_trend.index.year == 2014) & (df_trend.index.quarter == 1)].dropna().reset_index()["trend"].plot(label = "2014-Q1", legend = True,ax=ax[0][0])
df_trend[(df_trend.index.year  == 2014) & (df_trend.index.quarter == 2)].dropna().reset_index()["trend"].plot(label = "2014-Q2",legend = True,ax=ax[0][1])
df_trend[(df_trend.index.year  == 2014) & (df_trend.index.quarter == 3)].dropna().reset_index()["trend"].plot(label = "2014-Q3",legend = True,ax=ax[1][0])
df_trend[(df_trend.index.year  == 2014) & (df_trend.index.quarter == 4)].dropna().reset_index()["trend"].plot(label = "2014-Q4",legend = True,ax=ax[1][1])
df_trend[(df_trend.index.year == 2015) & (df_trend.index.quarter == 1)].dropna().reset_index()["trend"].plot(label = "2015-Q1", legend = True,ax=ax[0][0])
df_trend[(df_trend.index.year  == 2015) & (df_trend.index.quarter == 2)].dropna().reset_index()["trend"].plot(label = "2015-Q2",legend = True,ax=ax[0][1])
df_trend[(df_trend.index.year  == 2015) & (df_trend.index.quarter == 3)].dropna().reset_index()["trend"].plot(label = "2015-Q3",legend = True,ax=ax[1][0])
df_trend[(df_trend.index.year  == 2015) & (df_trend.index.quarter == 4)].dropna().reset_index()["trend"].plot(label = "2015-Q4",legend = True,ax=ax[1][1])
df_trend[(df_trend.index.year  == 2016) & (df_trend.index.quarter == 2)].dropna().reset_index()["trend"].plot(label = "2016-Q1",legend = True,ax=ax[0][0])
df_trend[(df_trend.index.year  == 2016) & (df_trend.index.quarter == 3)].dropna().reset_index()["trend"].plot(label = "2016-Q2",legend = True,ax=ax[0][1])
df_trend[(df_trend.index.year  == 2016) & (df_trend.index.quarter == 4)].dropna().reset_index()["trend"].plot(label = "2016-Q3",legend = True,ax=ax[1][0])
df_trend[(df_trend.index.year  == 2016) & (df_trend.index.quarter == 2)].dropna().reset_index()["trend"].plot(label = "2016-Q4",legend = True,ax=ax[1][1])
df_trend[(df_trend.index.year  == 2017) & (df_trend.index.quarter == 3)].dropna().reset_index()["trend"].plot(label = "2017-Q1",legend = True,ax=ax[0][0])
df_trend[(df_trend.index.year  == 2017) & (df_trend.index.quarter == 4)].dropna().reset_index()["trend"].plot(label = "2017-Q2",legend = True,ax=ax[0][1])
df_trend[(df_trend.index.year  == 2017) & (df_trend.index.quarter == 2)].dropna().reset_index()["trend"].plot(label = "2017-Q3",legend = True,ax=ax[1][0])
df_trend[(df_trend.index.year  == 2017) & (df_trend.index.quarter == 4)].dropna().reset_index()["trend"].plot(label = "2017-Q4",legend = True,ax=ax[1][1])
plt.show()


'''Graph - SEASONAL Analysis'''
decompose_result= stationary().seasonal_decompose(df_["Close_return"].dropna(),12)
df_season = decompose_result.trend
df_season = decompose_result.seasonal
df_residual = decompose_result.resid
Qtr_1 = [1,2,3]
Qtr_2 = [1,2,3]
Qtr_3 = [1,2,3]
Qtr_4 = [10,11,12]
yearlist = [2013]
N, M = 10, 10
fig, ax = plt.subplots(2,2,figsize=(N,M))
df_season[(df_season.index.year == 2014) & (df_season.index.quarter == 1)].dropna().reset_index()["seasonal"].plot(label = "2014-Q1", legend = True,ax=ax[0][0])
df_season[(df_season.index.year  == 2014) & (df_season.index.quarter == 2)].dropna().reset_index()["seasonal"].plot(label = "2014-Q2",legend = True,ax=ax[0][1])
df_season[(df_season.index.year  == 2014) & (df_season.index.quarter == 3)].dropna().reset_index()["seasonal"].plot(label = "2014-Q3",legend = True,ax=ax[1][0])
df_season[(df_season.index.year  == 2014) & (df_season.index.quarter == 4)].dropna().reset_index()["seasonal"].plot(label = "2014-Q4",legend = True,ax=ax[1][1])
df_season[(df_season.index.year == 2015) & (df_season.index.quarter == 1)].dropna().reset_index()["seasonal"].plot(label = "2015-Q1", legend = True,ax=ax[0][0])
df_season[(df_season.index.year  == 2015) & (df_season.index.quarter == 2)].dropna().reset_index()["seasonal"].plot(label = "2015-Q2",legend = True,ax=ax[0][1])
df_season[(df_season.index.year  == 2015) & (df_season.index.quarter == 3)].dropna().reset_index()["seasonal"].plot(label = "2015-Q3",legend = True,ax=ax[1][0])
df_season[(df_season.index.year  == 2015) & (df_season.index.quarter == 4)].dropna().reset_index()["seasonal"].plot(label = "2015-Q4",legend = True,ax=ax[1][1])
plt.show()
