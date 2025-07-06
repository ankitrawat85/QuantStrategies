# -*- coding: utf-8 -*-
"""
Created on Sun Feb  5 12:22:16 2023

@author: User1
"""

import ta
import myutils
import sys
import numpy as np
import pandas as pd


def generate_signal_RSI(stockname, ltp, period, long_entry, short_entry, data_path, close = 'Close'):
    try:
        stockname = stockname.strip()
        
        if type(ltp) is str:
            ltp = float(ltp.strip())
        if type(period) is str:
            period = int(period.strip())
        if type(long_entry) is str:
            long_entry = float(long_entry.strip())
        if type(short_entry) is str:
            short_entry = float(short_entry.strip())
        
        if ((stockname == '') | (ltp <= 0)  | (period <= 2)  | (long_entry <= 0)  | (long_entry >= 100) | (short_entry <= 0)  | (short_entry >= 100) | (short_entry >= long_entry) ):
            print(sys._getframe().f_code.co_name, 'Invalid parameter values')
            return None
        
        data = myutils.read_dataframe(data_path + '/' + stockname + '.csv')
        
        if (data.empty):
            print(sys._getframe().f_code.co_name, 'Data not found for ' + stockname)
            return None
        
        data = data[close]
        data = data.dropna()
        data = np.append(data, ltp)
        data = pd.DataFrame({'Close' : data})
        
        # generate indicator value
        current_rsi = ta.momentum.rsi(data, period)[-1]
        
        if (current_rsi == None):
            print(sys._getframe().f_code.co_name, 'Error getting RSI value for ' + stockname)
            return None
        
        # generate signal based on using the RSI as a trend indicator
        if (current_rsi > long_entry):
            # buy signal
            signal = 1
        elif (current_rsi < short_entry):
            # sell signal
            signal = -1
        else:
            # no signal
            signal = 0
        
        return signal
        
    except Exception as errmsg:
        print(sys._getframe().f_code.co_name, errmsg)
        return None


def generate_signal_MACD_v1(stockname, ltp, short_period, long_period, long_entry, short_entry, data_path, close = 'Close'):
    # in this function we are not considering stop loss, target, exit levels
    try:
        stockname = stockname.strip()
        
        if type(ltp) is str:
            ltp = float(ltp.strip())
        if type(short_period) is str:
            short_period = int(short_period.strip())
        if type(long_period) is str:
            long_period = int(long_period.strip())
        if type(long_entry) is str:
            long_entry = float(long_entry.strip())
        if type(short_entry) is str:
            short_entry = float(short_entry.strip())
        
        if ((stockname == '') | (ltp <= 0)  | (short_period <= 2)  | (long_period <= short_period)  | (long_entry <= 0)  | (long_entry >= 100) | (short_entry <= 0)  | (short_entry >= 100) | (short_entry >= long_entry) ):
            print(sys._getframe().f_code.co_name, 'Invalid parameter values')
            return None
        
        data = myutils.read_dataframe(data_path + '/' + stockname + '.csv')
        
        if (data.empty):
            print(sys._getframe().f_code.co_name, 'Data not found for ' + stockname)
            return None
        
        data = data[close]
        data = data.dropna()
        data = np.append(data, ltp)
        data = pd.DataFrame({'Close' : data})
        
        # generate indicator value
        current_macd = ta.trend.macd(data, n_fast = short_period, n_slow = long_period)[-1]
        
        if (current_macd == None):
            print(sys._getframe().f_code.co_name, 'Error getting MACD value for ' + stockname)
            return None
        
        # generate signal based on using the MACD
        if (current_macd > long_entry):
            # buy signal
            signal = 1
        elif (current_macd < short_entry):
            # sell signal
            signal = -1
        else:
            # no signal
            signal = 0
        
        return signal
        
    except Exception as errmsg:
        print(sys._getframe().f_code.co_name, errmsg)
        return None


def generate_signal_MACD_Histogram_v1(stockname, ltp, short_period, long_period, signal_period, long_entry, short_entry, data_path, close = 'Close'):
    # in this function we are not considering stop loss, target, exit levels
    try:
        stockname = stockname.strip()
        
        if type(ltp) is str:
            ltp = float(ltp.strip())
        if type(short_period) is str:
            short_period = int(short_period.strip())
        if type(long_period) is str:
            long_period = int(long_period.strip())
        if type(signal_period) is str:
            signal_period = int(signal_period.strip())
        if type(long_entry) is str:
            long_entry = float(long_entry.strip())
        if type(short_entry) is str:
            short_entry = float(short_entry.strip())
        
        if ((stockname == '') | (ltp <= 0)  | (short_period <= 2)  | (long_period <= short_period)  | (signal_period <= 2)  | (long_entry <= 0)  | (long_entry >= 100) | (short_entry <= 0)  | (short_entry >= 100) | (short_entry >= long_entry) ):
            print(sys._getframe().f_code.co_name, 'Invalid parameter values')
            return None
        
        data = myutils.read_dataframe(data_path + '/' + stockname + '.csv')
        
        if (data.empty):
            print(sys._getframe().f_code.co_name, 'Data not found for ' + stockname)
            return None
        
        data = data[close]
        data = data.dropna()
        data = np.append(data, ltp)
        data = pd.DataFrame({'Close' : data})
        
        # generate indicator value
        current_macdh = ta.trend.macd_diff(data, n_fast = short_period, n_slow = long_period, n_sign = signal_period)[-1]
        
        if (current_macdh == None):
            print(sys._getframe().f_code.co_name, 'Error getting MACDH value for ' + stockname)
            return None
        
        # generate signal based on using the MACDH
        if (current_macdh > long_entry):
            # buy signal
            signal = 1
        elif (current_macdh < short_entry):
            # sell signal
            signal = -1
        else:
            # no signal
            signal = 0
        
        return signal
        
    except Exception as errmsg:
        print(sys._getframe().f_code.co_name, errmsg)
        return None


def generate_signal_bollingerband(stockname, ltp, period, std_dev, long_entry, short_entry, data_path, close = 'Close'):
    try:
        stockname = stockname.strip()
        
        if type(ltp) is str:
            ltp = float(ltp.strip())
        if type(period) is str:
            period = int(period.strip())
        if type(long_entry) is str:
            long_entry = float(long_entry.strip())
        if type(short_entry) is str:
            short_entry = float(short_entry.strip())
        
        if ((stockname == '') | (ltp <= 0)  | (period <= 2)  | (long_entry <= 0)  | (long_entry >= 100) | (short_entry <= 0)  | (short_entry >= 100) | (short_entry >= long_entry) ):
            print(sys._getframe().f_code.co_name, 'Invalid parameter values')
            return None
        
        data = myutils.read_dataframe(data_path + '/' + stockname + '.csv')
        
        if (data.empty):
            print(sys._getframe().f_code.co_name, 'Data not found for ' + stockname)
            return None
        
        data = data[close]
        data = data.dropna()
        data = np.append(data, ltp)
        data = pd.DataFrame({'Close' : data})
        
        # generate indicator value
        bb_indicator = ta.volatility.BollingerBands(data, n = period, ndev = std_dev)
        
        # use the object to add different indicator columns to the dataframe, if needed
        data['bb_avg'] = bb_indicator.bollinger_mavg()
        data['bb_high'] = bb_indicator.bollinger_hband()
        
        # todo
        
        
        if (bb_indicator == None):
            print(sys._getframe().f_code.co_name, 'Error getting RSI value for ' + stockname)
            return None
        
        # generate signal based on using the RSI as a trend indicator
        if (current_rsi > long_entry):
            # buy signal
            signal = 1
        elif (current_rsi < short_entry):
            # sell signal
            signal = -1
        else:
            # no signal
            signal = 0
        
        return signal
        
    except Exception as errmsg:
        print(sys._getframe().f_code.co_name, errmsg)
        return None


 
    

    
        