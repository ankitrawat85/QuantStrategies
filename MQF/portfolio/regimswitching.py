## personal files

## System Libraries
import os

## Graph
import pandas as pd
import sys
from pandas_datareader.data import DataReader
'''System Path configuration'''
print (os.path.abspath(__file__))
sys.path.append('/Users/ankitrawat/Desktop/smu/Classes/Self/Code/Quant/venv/commonFunctions')
'''Import personal libraries '''
from commonFunctions import data

''' Import ML libraries'''
'''Graph '''


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
import statsmodels.api as sm

print ("Daily Return")
df_ = Test_PortfolioAnalysis().processing()
print ("df_......")
print(df_)

# NBER recessions

from datetime import datetime
usrec = DataReader('USREC', 'fred', start=datetime(1947, 1, 1), end=datetime(2013, 4, 1))

# Get the RGNP data to replicate Hamilton
dta = pd.read_stata('https://www.stata-press.com/data/r14/rgnp.dta').iloc[1:]
dta.index = pd.DatetimeIndex(dta.date, freq='QS')
dta_hamilton = dta.rgnp

# Plot the data
dta_hamilton.plot(title='Growth rate of Real GNP', figsize=(12,3))

# Fit the model
mod_hamilton = sm.tsa.MarkovAutoregression(dta_hamilton, k_regimes=2, order=4, switching_ar=False)
res_hamilton = mod_hamilton.fit()
print(res_hamilton.summary())
fig, axes = plt.subplots(2, figsize=(7,7))
ax = axes[0]
ax.plot(res_hamilton.filtered_marginal_probabilities[0])
ax.fill_between(usrec.index, 0, 1, where=usrec['USREC'].values, color='k', alpha=0.1)
ax.set_xlim(dta_hamilton.index[4], dta_hamilton.index[-1])
ax.set(title='Filtered probability of recession')

ax = axes[1]
ax.plot(res_hamilton.smoothed_marginal_probabilities[0])
ax.fill_between(usrec.index, 0, 1, where=usrec['USREC'].values, color='k', alpha=0.1)
ax.set_xlim(dta_hamilton.index[4], dta_hamilton.index[-1])
ax.set(title='Smoothed probability of recession')

fig.tight_layout()


"""

Additional code from analytics vidya for nse 

"""

import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt

#nifty = pd.read_csv('book3.csv', index_col=0, parse_dates=True) #Get nifty prices
#nifty = pd.read_csv('nifty.csv', index_col=0, parse_dates=True) #Get nifty prices
nifty_ret = df_["AXISBANK"].resample('W').last().pct_change().dropna() #Get weekly returns
nifty_ret.plot(title='Excess returns', figsize=(12, 3)) #Plot the dataset

## series stationary
print(adfuller(nifty_ret.dropna()))

#Fit the model
mod_kns = sm.tsa.MarkovRegression(nifty_ret.dropna(), k_regimes=3, trend='nc', switching_variance=True)
res_kns = mod_kns.fit()
res_kns.summary()
print(res_kns.summary())

fig, axes = plt.subplots(3, figsize=(10,7),ax = axes[0])
ax.plot(res_kns.smoothed_marginal_probabilities[0])
ax.set(title='Smoothed probability of a low-variance regime for stock returns',ax = axes[1])
ax.plot(res_kns.smoothed_marginal_probabilities[1])
ax.set(title='Smoothed probability of a medium-variance regime for stock returns',ax = axes[2])
ax.plot(res_kns.smoothed_marginal_probabilities[2])
ax.set(title='Smoothed probability of a high-variance regime for stock returns')

fig.tight_layout()
print (plt.show())