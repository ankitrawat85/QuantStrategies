# -*- coding: utf-8 -*-
"""
Created on Sun Feb  5 12:33:33 2023

@author: User1
"""

import sys

def generate_trade(ltp, current_signal, current_qty, prev_signal, capital, max_capital_deploy, buy_margin, sell_margin, pnl_target, pnl_stoploss, mtm_pnl_pct, lot_size, previous_exit_reason ):
    try:

        if type(ltp) is str:
            ltp = float(ltp.strip())
        if type(current_signal) is str:
            current_signal = int(current_signal.strip())
        if type(current_qty) is str:
            current_qty = int(current_qty.strip())
        if type(prev_signal) is str:
            prev_signal = int(prev_signal.strip())
        if type(capital) is str:
            capital = float(capital.strip())
        if type(max_capital_deploy) is str:
            max_capital_deploy = float(max_capital_deploy.strip())
        if type(buy_margin) is str:
            buy_margin = float(buy_margin.strip())
        if type(sell_margin) is str:
            sell_margin = float(sell_margin.strip())
        if type(pnl_target) is str:
            pnl_target = float(pnl_target.strip())
        if type(pnl_stoploss) is str:
            pnl_stoploss = float(pnl_stoploss.strip())
        if type(mtm_pnl_pct) is str:
            mtm_pnl_pct = float(mtm_pnl_pct.strip())
        if type(lot_size) is str:
            lot_size = int(lot_size.strip())
        
        if ((ltp <= 0)  | (current_signal > 1)  | (current_signal < -1)  | (prev_signal > 1)  | (prev_signal < -1)  | (capital <= 0) | (max_capital_deploy <= 0)  | (buy_margin <= 0) | (sell_margin <= 0) | (pnl_target < 0) | (pnl_stoploss < 0) | (lot_size <= 0) ):
            print(sys._getframe().f_code.co_name, 'Invalid parameter values')
            return None, None, None
        
        orderqty = 0
        orderprice = 0.0
        exitreason = ''
        
        if (current_qty == 0):
            # if there are no existing open positions
            
            # check for short signal
            if (current_signal == -1):
                # take a short pos
                orderprice = ltp
                
                margin_blocked = capital * max_capital_deploy
                
                orderqty = -(( margin_blocked // (orderprice * sell_margin)) // lot_size) * lot_size
                
                if (abs(orderqty) < 1):
                    orderprice = 0.0
                
            # check for long signal
            elif (current_signal == 1):
                # take a long pos
                orderprice = ltp
                
                margin_blocked = capital * max_capital_deploy
                
                orderqty = (( margin_blocked // (orderprice * buy_margin)) // lot_size) * lot_size
                
                if (orderqty < 1):
                    orderprice = 0.0
#            else:
                # do nothing / no trade
        else:
            # there are existing open positions
            # check for exit conditions
            
            if (mtm_pnl_pct > pnl_target):
                # if pnl target is hit
                orderprice = ltp
                orderqty = -current_qty
                exitreason = 'TG'
            elif (mtm_pnl_pct < -pnl_stoploss):
                # if pnl Stop Loss is hit
                orderprice = ltp
                orderqty = -current_qty
                exitreason = 'SL'
            elif (current_signal != prev_signal):
                # if signal changed
                orderprice = ltp
                orderqty = -current_qty
                exitreason = 'SC'
#            else:
                # do nothing
                
        return orderqty, orderprice, exitreason
        
    except Exception as errmsg:
        print(errmsg)
        return None, None, None
        








