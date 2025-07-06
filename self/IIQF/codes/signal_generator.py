# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 12:36:49 2023

@author: User1
"""

import iiqftalib as ta
import myutils
import sys
import numpy as np
import pandas as pd


def generate_signal_RSI_v1(stockname, ltp, period, long_entry, short_entry, data_path, close = 'Close'):
    # useing the RSI as momentum indicator to participate in the direction
    # in this function we are not considering stop loss, target, exit levels
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
        current_rsi = ta.RSI(data, period)
        
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


def generate_signal_RSI_v1a(data, ltp, period, long_entry, short_entry, close = 'Close'):
    # useing the RSI as momentum indicator to participate in the direction
    # in this function we are not considering stop loss, target, exit levels
    try:
        
        if type(ltp) is str:
            ltp = float(ltp.strip())
        if type(period) is str:
            period = int(period.strip())
        if type(long_entry) is str:
            long_entry = float(long_entry.strip())
        if type(short_entry) is str:
            short_entry = float(short_entry.strip())
        
        if ((data.empty) | (ltp <= 0)  | (period <= 2)  | (long_entry <= 0)  | (long_entry >= 100) | (short_entry <= 0)  | (short_entry >= 100) | (short_entry >= long_entry) ):
            print(sys._getframe().f_code.co_name, 'Invalid parameter values')
            return None
        
        data = data[close]
        data = data.dropna()
        data = np.append(data, ltp)
        data = pd.DataFrame({'Close' : data})
        
        # generate indicator value
        current_rsi = ta.RSI(data, period)
        
        if (current_rsi == None):
            print(sys._getframe().f_code.co_name, 'Error getting RSI value')
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


def generate_signal_RSI_v2(stockname, ltp, period, long_entry, short_entry, buy_target, buy_stoploss, sell_target, sell_stoploss, prev_signal, data_path, close = 'Close'):
    # useing the RSI as momentum indicator to participate in the direction
    # in this function we are considering stop loss, target, exit levels
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
        if type(buy_target) is str:
            buy_target = float(buy_target.strip())
        if type(buy_stoploss) is str:
            buy_stoploss = float(buy_stoploss.strip())
        if type(sell_target) is str:
            sell_target = float(sell_target.strip())
        if type(sell_stoploss) is str:
            sell_stoploss = float(sell_stoploss.strip())
        
        # validate the new para todo
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
        current_rsi = ta.RSI(data, period)
        
        if (current_rsi == None):
            print(sys._getframe().f_code.co_name, 'Error getting RSI value for ' + stockname)
            return None

        if (prev_signal == 0):
            # generate signal based on using the RSI as a trend indicator
            if ((current_rsi > long_entry) & (current_rsi < buy_target) ):
                # buy signal
                signal = 1
            elif ((current_rsi < short_entry) & (current_rsi > sell_target) ):
                # sell signal
                signal = -1
            else:
                # no signal
                signal = 0
        elif (prev_signal == 1):
            # handling stoploss
            if (current_rsi < buy_stoploss):
                signal = 0
            else:
                signal = prev_signal
        elif (prev_signal == -1):
            if (current_rsi > sell_stoploss):
                signal = 0
            else:
                signal = prev_signal
        elif (prev_signal == 1):
            # handling target
            if (current_rsi > buy_target):
                signal = 0
            else:
                signal = prev_signal
        elif (prev_signal == -1):
            if (current_rsi < sell_target):
                signal = 0
            else:
                signal = prev_signal
        
        
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
        current_macd = ta.MACD(data, short_period, long_period)
        
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
        current_macdh = ta.MACD_Histogram(data, short_period, long_period, signal_period)
        
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


 
    

    
        