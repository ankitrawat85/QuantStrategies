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
sys.path.append('/Users/myworld/Desktop/smu/Classes/Self/Code/Quant/QR')
from self.commonFunctions.code_dir.datapull import data,dataValidation,graph,stationary,models
class Test_PortfolioAnalysis():

    def __init__(self,*args,**kargs):
        self.nse50 = "https://en.wikipedia.org/wiki/NIFTY_50"
        self.datasite = "yahoo"
        print (self.nse50)

    def processing(self):
        '''Nifty 50 List - Wikipidia '''
        df_ = pd.read_html(self.nse50)[1]
        df_ = df_.iloc[:,1:3]
        df_nse50 = df_[df_["Sector"] == "Information Technology"]["Symbol"]
        print ("after removing banking -->")
        print (df_nse50)
        '''Data pull for list of stocks'''
        data_start = "2010-01-01"
        data_end  = "2021-11-21"
        stock_list  = pd.DataFrame(df_nse50).stack().values
        x = stock_list + ".NS"
        df_ = data().downloadData(self.datasite,stock_list + ".NS", data_start, data_end,"Close")
        return df_


x  = Test_PortfolioAnalysis().processing()
df_ = pd.DataFrame(x)
df_.to_csv("data.csv")
print (df_.head(10))
#df_HI = df_[["HDFCBANK","ICICIBANK"]].dropna(axis =0)
#print (df_HI)
#print (df_.dropna(axis =0))
LOOKBACK_PERIOD_ANNUAL = 252

# 1
'''print ("Daily Return")
daily_ret = df_.pct_change()
print (daily_ret.tail(20))
print (daily_ret.tail(20).dropna(axis =0).plot())
plt.show()'''

# 2

print ("Monthly Return")
monthly_ret = df_.pct_change(periods=30).dropna(axis =0)
#monthly_ret = monthly_ret[monthly_ret.index.year == 2021]
df_spread = pd.DataFrame()
print (monthly_ret)
for i in monthly_ret.columns:
    for j in monthly_ret.columns :
        if (i == j):
            pass
        else:
            df_2 = pd.DataFrame()
            df_2["Spread"] = (monthly_ret[i]/ monthly_ret[j]) - 1
            column_name  = i +"_"+j
            df_2[column_name] = df_2["Spread"].apply(lambda x: np.square(x))
            df_spread = pd.concat([df_spread,df_2[column_name]],axis =1)




print ("Spread between different stocks : ")
monthly_ret.index = pd.to_datetime(monthly_ret.index)
monthly_ret = monthly_ret.resample('M').last()
#df_spread.plot()
#plt.show()
print(monthly_ret.mean(axis=0).sort_values())
print ("Correlation ")
monthly_ret = monthly_ret.corr().unstack().sort_values()
monthly_ret = monthly_ret[monthly_ret > 0.9]
print("Return :-> ")
print(monthly_ret)

df_spread.index = pd.to_datetime(df_spread.index)
df_spread = df_spread.resample('M').last()
#df_spread.plot()
#plt.show()
print(df_spread.mean(axis=0).sort_values())
print ("Correlation ")
corr_df = df_spread.corr().unstack().sort_values()
corr_df = corr_df[corr_df > 0.9]
#print(corr_df.head(50))
print(corr_df)
#sns.heatmap(corr_df,annot = True)
#lt.show()
df_spread[["HCLTECH_TECHM","TCS_TECHM","TECHM_TCS","INFY_TCS","TCS_INFY","TECHM_INFY","HCLTECH_INFY","TCS_INFY","HCLTECH_INFY","TECHM_INFY"]].plot()
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



