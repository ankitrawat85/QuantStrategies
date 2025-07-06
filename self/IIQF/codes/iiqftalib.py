# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 12:13:37 2023

@author: User1
"""

import sys

# later - todo - optimize code for speed

def RSI(data, period = 14, close = 'Close'):
    try:
        if type(period) is str:
            period = int(period.strip())
            
        if (len(data) <= period):
            print(sys._getframe().f_code.co_name, 'Insufficient data')
            return None
        
        if (period < 2):
            print(sys._getframe().f_code.co_name, 'Invalid parameter values.')
            return None
        
        data = data[-(period + 1): ]
        
        data['change'] = data[close].diff()
        
        data['gain'] = data['change']
        data.loc[data['gain'] < 0, ['gain']] = 0.0
        
        data['loss'] = data['change']
        data.loc[data['loss'] > 0, ['loss']] = 0.0
        
        avg_gain = data['gain'].mean()
        avg_loss = abs(data['loss'].mean())
        
        if (avg_loss == 0.0):
            RSI = 100.0
        else:
            RS = avg_gain / avg_loss
            RSI = 100.0 - (100.0 / (1.0 + RS) )
        
        return RSI
        
    except Exception as errmsg:
        print(sys._getframe().f_code.co_name, errmsg)
        return None

def MACD(data, short_period = 12, long_period = 26, close = 'Close'):
    try:
        
        if type(short_period) is str:
            short_period = int(short_period.strip())
            
        if type(long_period) is str:
            long_period = int(long_period.strip())
            
        if (len(data) <= long_period):
            print(sys._getframe().f_code.co_name, 'Insufficient data')
            return None
        
        if ((short_period < 2) | (long_period <= short_period) ):
            print(sys._getframe().f_code.co_name, 'Invalid parameter values.')
            return None
        
        data = data[-long_period:]
        
#        data['Short_MA'] = data[close].rolling(window = short_period).mean()
#        data['Long_MA'] = data[close].rolling(window = long_period).mean()
        
        data['Short_MA'] = data[close].ewm(span = short_period).mean()
        data['Long_MA'] = data[close].ewm(span = long_period).mean()
        
        # this will be slow
#        data['MACD'] = data['Short_MA'] - data['Long_MA']
#        
#        MACD = float(data['MACD'].iloc[-1])
        
        Short_MA = float(data['Short_MA'].iloc[-1])
        Long_MA = float(data['Long_MA'].iloc[-1])
        MACD = Short_MA - Long_MA
        
        return MACD
        
    except Exception as errmsg:
        print(sys._getframe().f_code.co_name, errmsg)
        return None
    

def MACD_Histogram(data, short_period = 12, long_period = 26, signal_period = 9, close = 'Close'):
    try:
        
        if type(short_period) is str:
            short_period = int(short_period.strip())
            
        if type(long_period) is str:
            long_period = int(long_period.strip())
            
        if type(signal_period) is str:
            signal_period = int(signal_period.strip())
            
        if (len(data) < (long_period + signal_period - 1) ):
            print(sys._getframe().f_code.co_name, 'Insufficient data')
            return None
        
        if ((short_period < 2) | (long_period <= short_period) | (signal_period < 2) ):
            print(sys._getframe().f_code.co_name, 'Invalid parameter values.')
            return None
        
        data = data[-(long_period + signal_period - 1) : ]
        
#        data['Short_MA'] = data[close].rolling(window = short_period).mean()
#        data['Long_MA'] = data[close].rolling(window = long_period).mean()
        
        data['Short_MA'] = data[close].ewm(span = short_period).mean()
        data['Long_MA'] = data[close].ewm(span = long_period).mean()
        data['MACD'] = data['Short_MA'] - data['Long_MA']
        
        data['Signal'] = data['MACD'].ewm(span = signal_period).mean()
        
        # this will be slow
#        data['MACD_Histogram'] = data['MACD'] - data['Signal']
#        MACD_Histogram = float(data['MACD_Histogram'].iloc[-1])
        
        MACD = float(data['MACD'].iloc[-1])
        Signal = float(data['Signal'].iloc[-1])
        MACD_Histogram = MACD - Signal
        
        return MACD_Histogram
        
    except Exception as errmsg:
        print(sys._getframe().f_code.co_name, errmsg)
        return None
