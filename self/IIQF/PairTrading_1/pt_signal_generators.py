# -*- coding: utf-8 -*-
"""
Created on Sat Oct  9 09:45:42 2021

@author: User1
"""

import sys

def generate_signal(price1, price2, pos, short_period, long_period, long_entry, long_exit, long_stoploss, short_entry, short_exit, short_stoploss):
    try:
        if (short_period <= 0 or long_period <= short_period or short_entry <= 0 or short_exit < 0 or short_stoploss <= short_entry or long_entry <= 0 or long_exit < 0 or long_stoploss <= long_entry):
            return None
        
        ratio = price1 / price2
        short_moving_avg = ratio[-short_period:].mean()
        long_moving_avg = ratio[-long_period:].mean()
        long_moving_sd = ratio[-long_period:].std()
        moving_window_z_score = ((short_moving_avg - long_moving_avg) / long_moving_sd)[0]
        
        if (pos == 0):
            # check for short entry signal
            if ((moving_window_z_score > short_entry) and (moving_window_z_score < short_stoploss)):
                # generate a short signal
                signal = -1
                
            # check for long entry signal
            elif ((moving_window_z_score < -long_entry) and (moving_window_z_score > -long_stoploss)):
                # generate a long signal
                signal = 1
            
            # if there is no signal
            else:
                signal = 0
        
        elif (pos < 0):
            # if there is an existing short pos then check for exit or stoploss
            
            if ((moving_window_z_score < short_exit) or (moving_window_z_score > short_stoploss)):
                # target is hit or stoploss is hit, generate an exit short signal
                signal = 1
            else:
                # generate a hold signal
                signal = 0
        elif (pos > 0):
            # if there is an existing long pos then check for exit or stoploss
            
            if ((moving_window_z_score > -long_exit) or (moving_window_z_score < -long_stoploss)):
                # target is hit or stoploss is hit, generate an exit short signal
                signal = -1
            else:
                # generate a hold signal
                signal = 0
        
        return signal
    except Exception as ex:
        print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return None

