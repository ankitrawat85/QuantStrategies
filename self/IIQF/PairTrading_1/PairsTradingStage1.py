# -*- coding: utf-8 -*-
"""
Created on Sat Oct  2 09:01:18 2021

@author: User1
"""

import pandas as pd
import numpy as np
import statsmodels.tsa.stattools as ts
import matplotlib.pyplot as plt
import csv
from scipy import optimize
import mydatautils
import BackTestPairTrade
import PerformanceAnalysis as pa

def get_cointegrated_pairs(pricedata, StockIndustries, trnd):
    n = pricedata.shape[1]
    
    p_values_matrix = np.ones((n,n))
    
    keys = pricedata.keys()
    
    verygoodpairs = []
    goodpairs = []
    
    for i in range(n):
        p1 = pricedata[keys[i]]
        
        for j in range(i+1, n):
            
            if (StockIndustries[i] == StockIndustries[j]):
                p2 = pricedata[keys[j]]
                
                rslt = ts.coint(p1, p2, trend = trnd)
                
                pvalue = rslt[1]
                
                p_values_matrix[i, j] = pvalue
                
                if (pvalue < 0.01):
                    verygoodpairs.append((keys[i], keys[j]))
                
                if (pvalue < 0.05):
                    goodpairs.append((keys[i], keys[j]))
    
    return p_values_matrix, goodpairs, verygoodpairs


StockList = pd.read_csv('StocksList.csv')

# read prices data files from disk
hist_price_folder = '/Data/NSE/Equity'
data, stocknames, stockindustries = mydatautils.ReadAllStocksDataFromDisk(hist_price_folder, StockList)

## read prices from yahoo
#data, stocknames, stockindustries = mydatautils.ReadAllStocksDataFromYahoo(StockList, StartDate = '2021-01-01', EndDate = '2023-07-03')


# 3 years cointegrated - nc
pvalues, goodpairs, verygoodpairs = get_cointegrated_pairs(data, stockindustries, 'nc')

# save the pairs
myfile = open('VeryGoodPairs_nc.csv', 'w')
with myfile:
    writer = csv.writer(myfile, lineterminator = '\n')
    writer.writerows([['Stock1', 'Stock2']])
    writer.writerows(verygoodpairs)
    
myfile.close()

myfile = open('GoodPairs_nc.csv', 'w')
with myfile:
    writer = csv.writer(myfile, lineterminator = '\n')
    writer.writerows([['Stock1', 'Stock2']])
    writer.writerows(goodpairs)
    
myfile.close()


# 3 years cointegrated - c
pvaluesc, goodpairsc, verygoodpairsc = get_cointegrated_pairs(data, stockindustries, 'c')

# save the pairs
myfile = open('VeryGoodPairs_c.csv', 'w')
with myfile:
    writer = csv.writer(myfile, lineterminator = '\n')
    writer.writerows([['Stock1', 'Stock2']])
    writer.writerows(verygoodpairsc)
    
myfile.close()

myfile = open('GoodPairs_c.csv', 'w')
with myfile:
    writer = csv.writer(myfile, lineterminator = '\n')
    writer.writerows([['Stock1', 'Stock2']])
    writer.writerows(goodpairsc)
    
myfile.close()




# 2 years conintegrated
pvalues2, goodpairs2, verygoodpairs2 = get_cointegrated_pairs(data.iloc[-500:,:], stockindustries, 'nc')

# 1 years conintegrated
pvalues1, goodpairs1, verygoodpairs1 = get_cointegrated_pairs(data.iloc[-250:,:], stockindustries, 'nc')

n = len(verygoodpairs)

x = [i for i in range(len(data))]

for i in range(n):
    p1 = data[verygoodpairs[i][0]]
    p2 = data[verygoodpairs[i][1]]
    ratio = p1/p2
    plt.plot(x, ratio)
    plt.show()


short_period = 3
long_period = 60

i=0
for i in range(n):
    p1 = data[verygoodpairs[i][0]]
    p2 = data[verygoodpairs[i][1]]
    ratio = p1/p2
    
    short_moving_avg = ratio.rolling(window = short_period).mean()
    long_moving_avg = ratio.rolling(window = long_period).mean()
    long_moving_sd = ratio.rolling(window = long_period).std()
    moving_window_z_score = (short_moving_avg - long_moving_avg) / long_moving_sd

    plt.plot(x, moving_window_z_score)
    plt.show()
    print(verygoodpairs[i][0], verygoodpairs[i][1])


p1 = data['HDFC']
p2 = data['HDFCBANK']

initcap  = 1000000
maxcap = 0.8
bm = 0.2
sm = 0.2
para = np.zeros(8)
para[0] = -1.5
para[1] = -0.1
para[2] = -2.5
para[3] = 1.5
para[4] = 0.1
para[5] = 2.5
para[6] = 3
para[7] = 60


i=4
p1 = data[verygoodpairs[i][0]]
p2 = data[verygoodpairs[i][1]]

short_period = int(para[6])
long_period = int(para[7])

ratio = p1/p2
short_moving_avg = ratio.rolling(window = short_period).mean()
long_moving_avg = ratio.rolling(window = long_period).mean()
long_moving_sd = ratio.rolling(window = long_period).std()
moving_window_z_score = (short_moving_avg - long_moving_avg) / long_moving_sd
ratio.plot()
moving_window_z_score.plot()


plt.plot(x, moving_window_z_score)
plt.show()

cap, trdpnl, mtmpnl = BackTestPairTrade.backtest(para, p1, p2, initcap, maxcap, bm, sm)
print(verygoodpairs[i][0], verygoodpairs[i][1])
print('Final Capital: ', cap)
print('Rtn: ', (cap - initcap) / initcap)
print('Max Loss MTM: ', min(trdpnl))
print('Max Loss Trd: ', min(mtmpnl))

print('MaxDD (MTM) ', pa.calculate_maxdraw_down(initcap, mtmpnl))
print('MaxDD (Trd) ', pa.calculate_maxdraw_down(initcap, trdpnl))


pa.all_performance_statistics(initcap, mtmpnl, 0.05, 2.5)


# ==================================================================

# read the pairs list

    # loop through the list
for in range():
    # read the prices data
    #p1=
    #p2=
    
    # run the back tester
    cap, trdpnl, mtmpnl = BackTestPairTrade.backtest(para, p1, p2, initcap, maxcap, bm, sm)
    
    # run the PA with the MTM Pnl
    no_of_trades, no_of_profit_trades, no_of_loss_trades, max_draw_down, hit_ratio, avg_ret_per_trade, \
            avg_profit_per_trade, avg_loss_per_trade, max_profit_per_trade, max_loss_per_trade, \
            maxconsecutiveloss_ctr, sdret, sharpe_ratio, calmar_ratio = all_performance_statistics(init_capital, mtmpnl, riskfree_rate, totaltimeyears, fixedcapital, mindatapoints)
    
    # run the PA with the Tradewiese Pnl
    no_of_trades, no_of_profit_trades, no_of_loss_trades, max_draw_down, hit_ratio, avg_ret_per_trade, \
            avg_profit_per_trade, avg_loss_per_trade, max_profit_per_trade, max_loss_per_trade, \
            maxconsecutiveloss_ctr, sdret, sharpe_ratio, calmar_ratio =  all_performance_statistics(init_capital, trdpnl, riskfree_rate, totaltimeyears, fixedcapital, mindatapoints)
    
    # print the stats
    



