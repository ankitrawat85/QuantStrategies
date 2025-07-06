# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 12:01:28 2020

@author: Abhijit Biswas
"""

import pandas as pd
import numpy as np
import ta
import PerformanceAnalysis as pa

import csv
from scipy import optimize
 


stockslist = pd.read_csv('StocksList.csv')
stocknames = stockslist.iloc[:,0]

data = pd.read_csv('C:/DATA/NSE/Equity/NIFTY.csv')

data1 = data[['Date']]

for stock in stocknames:
    data_stock = pd.read_csv('C:/DATA/NSE/Equity/' + stock + '.csv')
    if (len(data_stock)) > 1500:
        data_stock = data_stock[['Date','Close']]
        data_stock = data_stock.rename(columns = {'Close' : stock})
        data1 = pd.merge(data1, data_stock, on = 'Date')

data1 = data1.set_index('Date')

data2 = data1.iloc[:,:].fillna(method = 'ffill')


# backtest function to generate signals and trades

def backtest(parameters, data, stock, period, init_capital, max_capital_deploy, buy_margin, sell_margin, fixedcapital = False):
    
    # the max_capital_deploy, buy_margin, sell_margin should all be in decimals not percentages
    
    short_entry = parameters[0]
    long_entry = parameters[1]
    pnl_target = parameters[2]
    pnl_stoploss = parameters[3]
    
#    short_exit = parameters[4]
#    long_exit = parameters[5]
#    short_stoploss = parameters[6]
#    long_stoploss = parameters[7]
    
    
    if (init_capital <= 0 or max_capital_deploy <=0 or buy_margin <=0 or sell_margin <= 0):
        return 0, 0, 0
    
    price = pd.DataFrame(data[stock])
    price['RSI'] = ta.momentum.rsi(close = data[stock], n = period)
    price = price.dropna()
    price.loc[price['RSI'] > long_entry, ['Signal']] = 1
    price.loc[price['RSI'] < short_entry, ['Signal']] = -1
    
    # simulate trading
    
    capital = init_capital
    qty = 0
    entry_price = 0
    pos = 0  # 0 - hold/no position, -1 - short, +1 - long
    margin_blocked = 0
    
    trade_pnl = []
    mtm_pnl = []
    
    for i in range(len(price)):
        
        if (capital <= 0):
            break
        
        if (pos == 0):
            # if there is no existing open positions
            
            # check for short signal
            if (price['Signal'][i] == -1):
                # take a short pos
                
                pos = -1
                entry_price = price.iloc[i, 0]
                margin_blocked = capital * max_capital_deploy
                qty = -margin_blocked // (entry_price * sell_margin)
                if (-qty < 1 ):
                    pos = 0
                    qty = 0
                    # break
 
            # else check for long sigal
            elif (price['Signal'][i] == 1):
                # take a long pos
                
                pos = 1
                entry_price = price.iloc[i, 0]
                margin_blocked = capital * max_capital_deploy
                qty = margin_blocked // (entry_price * buy_margin)
                if (qty < 1 ):
                    pos = 0
                    qty = 0
                    # break
            
            # else if there is no signal
            #else:
                # do nothing
                    
        elif (pos < 0):
            # if there is an existing open short position then check for exit conditions
            
            pnl = qty * (price.iloc[i, 0] - entry_price)
            pnl_pct = (price.iloc[i, 0] - entry_price) / entry_price
            mtm_pnl = np.append(mtm_pnl, pnl)
            
            if ((price['Signal'][i] != -1) | (pnl_pct > pnl_target) | (pnl_pct < -pnl_stoploss)):
                # if signal changes or target is hit or stoploss is hit, exit the position 
                
                trade_pnl = np.append(trade_pnl, pnl)
                
                if not (fixedcapital):
                    capital = capital + pnl
                
                # release the margin and all others
                margin_blocked = 0
                qty = 0
                pos = 0
                entry_price = 0
                
#            else:
#                # neither target nor stoploss is hit, hold the position 
#               # do nothing
                
        elif (pos > 0):
            # if there is an existing open long position then check for exit conditions
            
            pnl = qty * (price.iloc[i, 0] - entry_price)
            pnl_pct = (price.iloc[i, 0] - entry_price) / entry_price
            mtm_pnl = np.append(mtm_pnl, pnl)
            
            if ((price['Signal'][i] != 1) | (pnl_pct > pnl_target) | (pnl_pct < -pnl_stoploss)):
                # if signal changes or target is hit or stoploss is hit, exit the position 
                
                trade_pnl = np.append(trade_pnl, pnl)
                
                if not (fixedcapital):
                    capital = capital + pnl
                
                # release the margin and all others
                margin_blocked = 0
                qty = 0
                pos = 0
                entry_price = 0
                
#            else:
#                # neither target nor stoploss is hit, hold the position 
#               # do nothing

    return capital, trade_pnl, mtm_pnl


init_capital  = 100000
max_capital_deploy = 0.8
buy_margin = 0.2
sell_margin = 0.2
fixedcapital= True
mindatapoints = 5
ismaximize = True
riskfree_rate = 0.001
totaltimeyears = 6
objective = 'SharpeRatio'
ismaximize = True

parameters = np.zeros(4)
parameters[0] = 30
parameters[1] = 60
parameters[2] = 0.02
parameters[3] = 0.02

data=data2
stock = 'ACC'
period = 14 


cap, trdpnl, mtmpnl = backtest(parameters, data, stock, period, init_capital, max_capital_deploy, buy_margin, sell_margin)




def objfunc(parameters, objective, data, stock, period, init_capital, max_capital_deploy, buy_margin, sell_margin, riskfree_rate, totaltimeyears, fixedcapital = False, mindatapoints = 5, ismaximize = False):
    #if you want to maximize sharpe ratio, then this function should return -sharp ratio
    
    #if you want to maximize hit ratio, then this function should return -hit ratio
    
    #if you want to minimize maxdd, then this function should return max dd
    
    finalcap, trdpnl, mtmpnl =  backtest(parameters, data, stock, period, init_capital, max_capital_deploy, buy_margin, sell_margin, fixedcapital)    

    result = pa.performance_statistic(objective, init_capital, mtmpnl, riskfree_rate, totaltimeyears, fixedcapital, mindatapoints)
    
    if (ismaximize):
        return -result
    else:
        return result
    

# define a set of functions that implement the constraints on the parameters (optimisable variables)

def shortentrylowerlimit(parameters):
    return parameters[0]

def shortentryupperlimit(parameters):
    return (100 - parameters[0])

def longentrylowerlimit(parameters):
    return parameters[1]

def longentryupperlimit(parameters):
    return (100 - parameters[1])

def longentrygreaterthanshortentry(parameters):
    return (parameters[1] - parameters[0])

def pnltargetlowerlimit(parameters):
    return parameters[2]

def pnlstoplosslowerlimit(parameters):
    return parameters[3]


# define dictionary items for each of the constraints and the functions that implement those constraints
    
cons1 = {'type' : 'ineq', 'fun' : shortentrylowerlimit}
cons2 = {'type' : 'ineq', 'fun' : shortentryupperlimit}
cons3 = {'type' : 'ineq', 'fun' : longentrylowerlimit}
cons4 = {'type' : 'ineq', 'fun' : longentryupperlimit}
cons5 = {'type' : 'ineq', 'fun' : longentrygreaterthanshortentry}
cons6 = {'type' : 'ineq', 'fun' : pnltargetlowerlimit}
cons7 = {'type' : 'ineq', 'fun' : pnlstoplosslowerlimit}


conslist = [cons1, cons2, cons3, cons4, cons5, cons6, cons7]


nonopt_parameters = (objective, data, stock, period, init_capital, max_capital_deploy, buy_margin, sell_margin, fixedcapital, mindatapoints, ismaximize)

res = optimize.minimize(objfunc, parameters, args = (nonopt_parameters), constraints = conslist, method = 'SLSQP', options = {'maxiter' : 100} )






   
    
    
    
    
            
    
    
    
    
    















