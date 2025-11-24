# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 12:20:58 2023

@author: User1
"""

import pandas as pd
import yahoo
import sys

def ReadAllStocksDataFromDisk(DataFolder, StockList, MinDataPoints = 500):
    try:
        Stocknames = StockList.iloc[:,0]
        StockIndustries = StockList.iloc[:,1]
        
        niftydates = pd.read_csv(DataFolder + '/NIFTY.CSV')
        
        all_price_data = niftydates[['Date']]
        
        Stocknames1 = []
        StockIndustries1 = []
        
        j = 0
        for Stockname in Stocknames:
            stock_price_data = pd.read_csv(DataFolder + '/' + Stockname + '.CSV')
            if (len(stock_price_data) > MinDataPoints):
                stock_price_data = stock_price_data[['Date','Close']]
                stock_price_data = stock_price_data.rename(columns = {'Close' : Stockname})
                all_price_data = pd.merge(all_price_data, stock_price_data, on = 'Date')
                Stocknames1.append(Stockname)
                StockIndustries1.append(StockIndustries[j])
            j = j + 1
        
        
        all_price_data = all_price_data.set_index('Date')
        
        all_price_data = all_price_data.iloc[:,:].fillna(method = 'ffill')
        
        return all_price_data, Stocknames1, StockIndustries1
    except Exception as ex:
        print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return pd.DataFrame(), [], []
    
def ReadStockDataFromDisk(DataFolder, Stockname):
    try:
        stock_price_data = pd.read_csv(DataFolder + '/' + Stockname + '.CSV')
        stock_price_data = stock_price_data[['Date','Close']]
        stock_price_data['Date'] = pd.to_datetime(stock_price_data['Date'])
        stock_price_data = stock_price_data.set_index(keys='Date')
        return stock_price_data
    except Exception as ex:
        print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return pd.DataFrame()
#
#
#def ReadAllStocksDataFromYahoo(StockList, StartDate, EndDate, MinDataPoints = 500):
#    try:
#        Stocknames = StockList.iloc[:,0]
#        StockIndustries = StockList.iloc[:,1]
#        
#        niftyprices = yahoo.GetHistoricalClosePrices('NIFTY', interval = '1d', startdate = StartDate, enddate = EndDate)
#        
#        all_price_data = pd.DataFrame(niftyprices.index)
#        
#        Stocknames1 = []
#        StockIndustries1 = []
#        
#        j = 0
#        for Stockname in Stocknames:
#            stock_price_data = yahoo.GetHistoricalClosePrices(Stockname, interval = '1d', startdate = StartDate, enddate = EndDate)
#            
#            if (len(stock_price_data) > MinDataPoints):
#                stock_price_data = stock_price_data.rename(columns = {'Close' : Stockname})
#                all_price_data = pd.merge(all_price_data, stock_price_data, on = 'Date')
#                Stocknames1.append(Stockname)
#                StockIndustries1.append(StockIndustries[j])
#            j = j + 1
#        
#        
#        all_price_data = all_price_data.set_index('Date')
#        
#        all_price_data = all_price_data.iloc[:,:].fillna(method = 'ffill')
#        
#        return all_price_data, Stocknames1, StockIndustries1
#    except Exception as ex:
#        print(sys._getframe().f_code.co_name, 'exception: ', ex)
#        return pd.DataFrame(), [], []
#    
#def ReadStockDataFromYahoo(Stockname, StartDate, EndDate):
#    try:
#        stock_price_data = yahoo.GetHistoricalClosePrices(Stockname, interval = '1d', startdate = StartDate, enddate = EndDate)
#        return stock_price_data
#    except Exception as ex:
#        print(sys._getframe().f_code.co_name, 'exception: ', ex)
#        return pd.DataFrame()
