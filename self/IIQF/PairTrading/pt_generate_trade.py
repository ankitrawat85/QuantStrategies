# -*- coding: utf-8 -*-
"""
Created on Sat Oct  9 09:46:41 2022

@author: User1
"""

import sys

def GenerateTrade(ltpleg1, ltpleg2, lot_size1, lot_size2, current_qty_leg1, current_qty_leg2, current_signal, prev_signal, capital, max_capital_to_deploy, buy_margin, sell_margin, pnl_target, pnl_stoploss, mtm_pl, prev_exit_reason = "", reverse_pos_on_exit = False):
    
    # maybe todo later
    # take the expiry date of options and also how many days prior to expiry to exit and exit postions accordingly
    try:
        
        # todo
        # validate all the input parameters
        if (ltpleg1 <= 0 or capital <= 0 or max_capital_to_deploy <= 0 or buy_margin <= 0 or sell_margin <= 0):
            return 0, 0, 0.0, 0.0, ""
        
        # prev_exit_reason : SL # may be later todo TG or SC
#        if ((prev_exit_reason == "SL") and (current_signal == prev_signal)):
#            return 0, 0, 0.0, 0.0, ""
        
        orderqty1 = 0
        orderqty2 = 0
        orderprice1 = 0.0
        orderprice2 = 0.0
        exitreason = ''
        
        if ((current_qty_leg1 == 0) & (current_qty_leg2 == 0)) :
            # if there is no existing open position
            # generate entry trades
            
            margin_blocked = capital * max_capital_to_deploy
            
            # check for short signal
            if (current_signal == -1):
                # take a fresh short pos
                orderprice1 = ltpleg1
                orderprice2 = ltpleg2
                
                orderqty1 = (margin_blocked / 2) // (ltpleg1 * sell_margin)
                orderqty1 = -int(orderqty1 / lot_size1) * lot_size1
                
                orderqty2 = (margin_blocked / 2) // (ltpleg2 * buy_margin)
                orderqty2 = int(orderqty2 / lot_size2) * lot_size2

                if (-orderqty1 < 1):
                    orderqty1 = 0
                    orderqty2 = 0
            
                if (orderqty2 < 1):
                    orderqty2 = 0
                    orderqty1 = 0
            
            # check for long signal
            elif (current_signal == 1):
                # take a fresh long pos
                orderprice1 = ltpleg1
                orderprice2 = ltpleg2
                
                orderqty1 = (margin_blocked / 2) // (ltpleg1 * buy_margin)
                orderqty1 = int(orderqty1 / lot_size1) * lot_size1
                
                orderqty2 = (margin_blocked / 2) // (ltpleg2 * sell_margin)
                orderqty2 = -int(orderqty2 / lot_size2) * lot_size2

                if (orderqty1 < 1):
                    orderqty1 = 0
                    orderqty2 = 0
            
                if (-orderqty2 < 1):
                    orderqty2 = 0
                    orderqty1 = 0
                
            # else if there is no signal
            # else:
                # do nothing
        
        elif ((current_qty_leg1 != 0) | (current_qty_leg2 != 0)) :
            # if there is existing open position 
            # then check for exit conditions
            
#            if (mtm_pl > pnl_target):
#                orderprice1 = ltpleg1
#                orderprice2 = ltpleg2
#                orderqty1 = -current_qty_leg1
#                orderqty2 = -current_qty_leg2
#                exitreason = "TG"
#            elif (mtm_pl < -pnl_stoploss):
#                orderprice1 = ltpleg1
#                orderprice2 = ltpleg2
#                orderqty1 = -current_qty_leg1
#                orderqty2 = -current_qty_leg2
#                exitreason = "SL"
#            elif (current_signal != prev_signal):
#                orderprice1 = ltpleg1
#                orderprice2 = ltpleg2
#                orderqty1 = -current_qty_leg1
#                orderqty2 = -current_qty_leg2
#                exitreason = "SC"

            if ((current_signal != 0) & (current_signal != prev_signal)):
                orderprice1 = ltpleg1
                orderprice2 = ltpleg2
                orderqty1 = -current_qty_leg1
                orderqty2 = -current_qty_leg2
                exitreason = "SC"
                
        return orderqty1, orderqty2, orderprice1, orderprice2, exitreason

    except Exception as ex:
        print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return 0, 0, 0.0, 0.0, ""
           

