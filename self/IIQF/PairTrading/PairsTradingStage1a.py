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
import mydatautils

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


