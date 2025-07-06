# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 14:53:15 2023

@author: User1
"""

import numpy as np
import sys


def backtest(parameters, price1, price2, init_capital, max_capital_deploy, buy_margin, 
             sell_margin, fixedcapital = False):
    
    # the max_capital_deploy, buy_margin, sell_margin should all be in decimals not percentages
    
    try:
        
        long_entry = parameters[0]
        long_exit = parameters[1]
        long_stoploss = parameters[2]
        short_entry = parameters[3]
        short_exit = parameters[4]
        short_stoploss = parameters[5]
        short_period = int(parameters[6])
        long_period = int(parameters[7])
        
        if (init_capital <= 0 or max_capital_deploy <= 0 or buy_margin <= 0 or sell_margin <= 0):
            return 0, [], []
        
        signal_score = GenerateZScore(price1, price2, short_period, long_period)
        
        price1 = price1[long_period - 1:]
        price2 = price2[long_period - 1:]
        
        # simulate trading
        
        capital = init_capital
        qty1 = 0
        qty2 = 0
        entry_price1 = 0
        entry_price2 = 0
        pos = 0  # 0 - hold/no position, -1 - short, +1 - long
        margin_blocked = 0
        
        trade_pnl = []
        mtm_pnl = []
        
        for i in range(len(signal_score)):
            
            if (capital <= 0):
                break
            
            if (pos == 0):
                # if there is no existing open positions
                
                # check for short signal
                if (signal_score[i] > short_entry and signal_score[i] < short_stoploss):
                    # take a short pos
                    
                    pos = -1
                    
                    entry_price1 = price1[i]
                    entry_price2 = price2[i]
                    
                    margin_blocked = capital * max_capital_deploy
                    
                    qty1 = -(margin_blocked / 2) // (entry_price1 * sell_margin)
                    qty2 = (margin_blocked / 2) // (entry_price2 * buy_margin)
                    
                    if (-qty1 < 1 or qty2 < 1 ):
                        pos = 0
                        qty1 = 0
                        qty2 = 0
                        # break
     
                # else check for long sigal
                elif (signal_score[i] < long_entry and signal_score[i] > long_stoploss):
                    # take a long pos
                    
                    pos = 1
                    
                    entry_price1 = price1[i]
                    entry_price2 = price2[i]
                    
                    margin_blocked = capital * max_capital_deploy
                    
                    qty1 = (margin_blocked / 2) // (entry_price1 * buy_margin)
                    qty2 = -(margin_blocked / 2) // (entry_price2 * sell_margin)
                    
                    if (qty1 < 1 or -qty2 < 1 ):
                        pos = 0
                        qty1 = 0
                        qty2 = 0
                        # break
                
                # else if there is no signal
                #else:
                    # do nothing
                        
            elif (pos < 0):
                # if there is an existing open short position 
                # then check for exit conditions
                
                if (signal_score[i] < short_exit):
                    # target is hit, exit the position i.e. buy back the stock1 and sell back the stock2
                    
                    pnl = qty1 * (price1[i] - entry_price1) + qty2 * (price2[i] - entry_price2)
                    
                    trade_pnl = np.append(trade_pnl, pnl)
                    mtm_pnl = np.append(mtm_pnl, pnl)
                    
                    if not (fixedcapital):
                        capital = capital + pnl
                    
                    # release the margin and all others
                    margin_blocked = 0
                    qty1 = 0
                    qty2 = 0
                    pos = 0
                    entry_price1 = 0
                    entry_price2 = 0
                    
                elif (signal_score[i] > short_stoploss):
                    # stoploss is hit, exit the position i.e. buy back the stock1 and sell back the stock2
                    
                    pnl = qty1 * (price1[i] - entry_price1) + qty2 * (price2[i] - entry_price2)
                    
                    trade_pnl = np.append(trade_pnl, pnl)
                    mtm_pnl = np.append(mtm_pnl, pnl)
                    
                    if not (fixedcapital):
                        capital = capital + pnl
                    
                    # release the margin and all others
                    margin_blocked = 0
                    qty1 = 0
                    qty2 = 0
                    pos = 0
                    entry_price1 = 0
                    entry_price2 = 0
                    
                else:
                    # neither target nor stoploss is hit, hold the position 
                    
                    pnl = qty1 * (price1[i] - entry_price1) + qty2 * (price2[i] - entry_price2)
                    
                    mtm_pnl = np.append(mtm_pnl, pnl)
                    
                    # todo later
    #                if (-pnl > stoploss or pnl > target):
    #                    trade_pnl = np.append(trade_pnl, pnl)
    #                    
    #                    if not (fixedcapital):
    #                        capital = capital + pnl
    #                    
    #                    # release the margin and all others
    #                    margin_blocked = 0
    #                    qty1 = 0
    #                    qty2 = 0
    #                    pos = 0
#                        entry_price1 = 0
#                        entry_price2 = 0
    #                #else:
    #                # do nothing
                    
            elif (pos > 0):
                # if there is an existing open long position then check for exit conditions
                
                if (signal_score[i] > long_exit):
                    # target is hit, exit the position i.e. sell back the stock1 and buy back the stock2
                    
                    pnl = qty1 * (price1[i] - entry_price1) + qty2 * (price2[i] - entry_price2)
                    
                    trade_pnl = np.append(trade_pnl, pnl)
                    mtm_pnl = np.append(mtm_pnl, pnl)
                    
                    if not (fixedcapital):
                        capital = capital + pnl
                    
                    # release the margin and all others
                    margin_blocked = 0
                    qty1 = 0
                    qty2 = 0
                    pos = 0
                    entry_price1 = 0
                    entry_price2 = 0
                    
                elif (signal_score[i] < long_stoploss):
                    # stoploss is hit, exit the position i.e. sell back the stock1 and buy back the stock2
                    
                    pnl = qty1 * (price1[i] - entry_price1) + qty2 * (price2[i] - entry_price2)
                    
                    trade_pnl = np.append(trade_pnl, pnl)
                    mtm_pnl = np.append(mtm_pnl, pnl)
                    
                    if not (fixedcapital):
                        capital = capital + pnl
                    
                    # release the margin and all others
                    margin_blocked = 0
                    qty1 = 0
                    qty2 = 0
                    pos = 0
                    entry_price1 = 0
                    entry_price2 = 0
                    
                else:
                    # neither target nor stoploss is hit, hold the position 
                    
                    pnl = qty1 * (price1[i] - entry_price1) + qty2 * (price2[i] - entry_price2)
                    
                    mtm_pnl = np.append(mtm_pnl, pnl)
                    
                    # todo later
    #                if (-pnl > stoploss or pnl > target):
    #                    trade_pnl = np.append(trade_pnl, pnl)
    #                    
    #                    if not (fixedcapital):
    #                        capital = capital + pnl
    #                    
    #                    # release the margin and all others
    #                    margin_blocked = 0
    #                    qty1 = 0
    #                    qty2 = 0
    #                    pos = 0
    #                    entry_price1 = 0
    #                    entry_price2 = 0
    #                #else:
    #                # do nothing
    
        return capital, trade_pnl, mtm_pnl
    except Exception as ex:
        print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return 0, [], []
            

def GenerateZScore(price1, price2, short_period, long_period):
    try:
        ratio = price1 / price2
        short_moving_avg = ratio.rolling(window = short_period).mean()
        long_moving_avg = ratio.rolling(window = long_period).mean()
        long_moving_sd = ratio.rolling(window = long_period).std()
        moving_window_z_score = (short_moving_avg - long_moving_avg) / long_moving_sd
        
        # drop the top rows containing NaN
        moving_window_z_score = moving_window_z_score.dropna()
        
        return moving_window_z_score
    except Exception as ex:
        print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return []

