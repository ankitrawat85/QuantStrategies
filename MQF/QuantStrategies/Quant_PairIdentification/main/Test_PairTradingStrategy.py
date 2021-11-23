## personal files

## System Libraries
import os

## Graph
import pandas as pd
import sys
'''System Path configuration'''
print (os.path.abspath(__file__))
sys.path.append('/Users/ankitrawat/Desktop/smu/Classes/Self/Code/Quant/venv/commonFunctions')

'''Import personal libraries '''
from commonFunctions import data, dataValidation

''' Import ML libraries'''
from sklearn import linear_model
from statsmodels.tsa.stattools import coint
'''Graph '''
import matplotlib.pyplot as plt

'''

Pair trading is generally  dollar neutral so that it can be ineffective irrespective of market 
dollar neutral : long / short position based on hedge ration ( Beta )
A zero beta portfolio can be constructed over a set of stocks S1, S2, ...Sn, by choosing weights such that:
coint : Engle-Granger Approach   

'''

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
        df_ = data().downloadData(self.datasite,stock_list, data_start, data_end,"Close")
        print(df_)
        return df_



x  = Test_PortfolioAnalysis().processing()
df_ = pd.DataFrame(x)
LOOKBACK_PERIOD_ANNUAL = 252
'''
# 1
print ("Daily Return")
daily_ret = df_.pct_change()
print (daily_ret.dropna(axis =0).plot())
plt.show()
'''
# 2
print ("Monthly Return")
monthly_ret = df_.pct_change(periods=30).dropna(axis =0)
print(monthly_ret.index.year)
monthly_ret = monthly_ret[monthly_ret.index.year == 2021]
df_spread = pd.DataFrame()
for i in monthly_ret.columns:
    for j in monthly_ret.columns :
        if (i == j):
            pass
        else:
            df_2 = pd.DataFrame()
            df_2["Spread"] = (monthly_ret[i]/ monthly_ret[j]) - 1
            print (df_2)
            column_name  = i +"_"+j
            df_2[column_name] = df_2["Spread"].apply(lambda x: np.square(x))
            df_spread = pd.concat([df_spread,df_2[column_name]],axis =1)
            print (df_2)


''''
pair Trading -  Distance Methodology 
'''

print ("pair Trading -  Distance Methodology  ")
print(df_spread.mean(axis=0).sort_values())
print(df_spread["ICICIBANK_SBIN"])
x = data().dataNormalization(df_spread["ICICIBANK_SBIN"],3,1)
print(pd.DataFrame(x))
'''
Trading rule 
if z > 2 : We short 1/b worth of stock 2 and buy 1 dollar of stock 1 when spread moves above +2
if z < -2 : If the spread drops below -2, we buy 1 dollar worth of stock 2 and short b dollars of stock 1.
Close position if it retunr to 0 
'''

''''
pair Trading -  Distance Methodology with Correlation
'''

corr_df = df_spread.corr().unstack().sort_values()
corr_df = corr_df[corr_df > 0.9]
print("correlation-")
print(corr_df.sort_values(ascending=False))
##sns.heatmap(corr_df,annot = True)
#lt.show()
#print(df_spread[["ICICIBANK_SBIN","AXISBANK_SBIN","HDFCBANK_SBIN","KOTAKBANK_SBIN",""]].plot())
#print (monthly_ret.dropna().head(10))
#print ("Spread mean : {}".format(monthly_ret.dropna()["spread_square"].mean()))
#monthly_ret[monthly_ret.index.year == 2021].dropna(axis =0).plot()
#monthly_ret.dropna(axis = 0, inplace = True)
#monthly_ret[monthly_ret.index.year == 2021]["spread_square"].plot()
plt.show()
#3
'''
print ("Annually Return")
Annually_ret = df_.pct_change(periods=252)
#print (Annually_ret.dropna(axis =0).plot())
Annually_ret[Annually_ret.index.year == 2021].dropna(axis =0).plot()
plt.show()
'''
'''
sd_window = 30
print ("rolling monthly standard  Deviations")
rolling_std = daily_ret.rolling(sd_window).std() * np.sqrt(252)
print (rolling_std.dropna(axis =0).plot())
plt.show()
'''
'''

Pairtrading - cointegration 
1. take two variabes , their difference should be stationary
'''
import statsmodels.api as sm
import numpy as np


##1 . log return - Monthly
df_logReturn =  data().logReturn(df_,30).dropna()
#df_logReturn = pd.DataFrame(df_logReturn).resample('M').mean()
df_logReturn = df_logReturn[["SBIN","ICICIBANK"]]
print ("Monthly")
print (df_logReturn)

##2. Regresision using linear stats package and sklear package
## Linear Regression
# stats models
Y = df_logReturn["SBIN"]
X = df_logReturn["ICICIBANK"]
X = sm.add_constant(X)
model = sm.OLS(Y,X)
results = model.fit()
print("results----->")
print(results.summary())
print(results.params[0])
print(results.params[1])

#2 sklearn
regr = linear_model.LinearRegression()
df_ = df_[["ICICIBANK","SBIN"]]
regr.fit(np.array(df_logReturn["ICICIBANK"]).reshape(-1,1),np.array(df_logReturn["SBIN"]))
print("regr coefficient : {}".format(regr.coef_))
print("regr intercept : {}".format(regr.intercept_))
df_logReturn["intercept"] = regr.intercept_


#### residual
df_logReturn["diff"] = df_logReturn["SBIN"] -   regr.coef_ * df_logReturn["ICICIBANK"]
#df_logReturn["diff"] = df_logReturn["SBIN"] -   results.params[1] * df_logReturn["ICICIBANK"]
df_logReturn = df_logReturn.dropna()

## ADF test
p_value =  dataValidation().Dickey_Fuller_test(df_logReturn["diff"])
print (p_value)
cut_off = 0.01
if p_value[1] < cut_off:
    print ("Time Series is  stationary")
    print (" Mean {} and Variance {} ".format(df_logReturn["diff"].mean(),df_logReturn["diff"].var()))
else:
    print ("Time series is not stationary")

## test co-integration
print(coint(df_logReturn["SBIN"],df_logReturn["ICICIBANK"]))
print (df_logReturn)

## Spread normalization - Command to normalize - z scrore
###df_logReturn["Normalized"] = df_logReturn["diff"].apply(lambda x : (x - df_logReturn["diff"].mean())/df_logReturn["diff"].std())
df_logReturn["Normalized_lib"] = data().dataNormalization(df_logReturn["diff"],3,1)

'''
Trading rule 
if z > 2 : We short 1/b worth of stock 2 and buy 1 dollar of stock 1 when spread moves above +2
if z < -2 : If the spread drops below -2, we buy 1 dollar worth of stock 2 and short b dollars of stock 1.
Close position if it retunr to 0 
'''

print (df_logReturn[df_logReturn["Normalized_lib"] == 0])
df_logReturn["Normalized_lib"].plot()
plt.show()

''''''
