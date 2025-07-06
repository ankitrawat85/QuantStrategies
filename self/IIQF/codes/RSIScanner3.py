# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 11:46:18 2023

@author: User1
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 11:39:45 2023

@author: User1
"""

import sys
import pandas as pd
import time
import datetime

import myutils
import mydateutils
#import brokerAPI
import signal_generator as sg
import trade_generator as tg
import strategy_status as ss
import settings
import scanlist

# user dependent
historical_data_path = 'C:/DATA/NSE/Equity'
scan_interval = 15


# constant for status etc
# todo

# scanlist column constants
slcol_stocksymbol = 0
slcol_stockname = 2
slcol_lotsize = 7


# API constants todo


# dependent on your strategy
starttime = mydateutils.DateTimeFunctions.StrToTime('9:15:0')
stoptime = mydateutils.DateTimeFunctions.StrToTime('15:15:0')


def RSIScanner():
    try:
        
        current_time = mydateutils.DateTimeFunctions.CurrentTime()
        
        if ((current_time < starttime) | (current_time > stoptime)):
            print('Market is closed for the algo')
            return
        
        #######################################
        # broker dependent part of code
        
        # todo some more API para to add
        userid, pasword, accountid = settings.GetAPIPara()
        
        if (userid == None):
            print('Could not read API settings. Exiting algo.')
            return
        
        # todo
        if (ConnectToAPI() == False):
            print('Could not connect to API. Exiting algo.')
            return
        
        lg = LoginAPI()
        if (lg == False):
            print('Could not connect to API. Exiting algo.')
            return
        
        #######################################
        
        ######################################
        
        # strategy dependent
        windowperiod, long_entry, short_entry = settings.GetSignalPara_RSI()
        if (windowperiod == None):
            print('Could not get the signal parameters. Exiting algo.')
            return
        
        # strategy dependent
        capital, max_capital_deploy, buy_margin, sell_margin, pnl_target, pnl_stoploss = settings.GetTradePara()
        if (capital == None):
            print('Could not get the trade parameters. Exiting algo.')
            return
        
        # strategy dependent
        tradescanlist = scanlist.GetScanList('/COMPANIES/IIQF/COURSES/CPAT/2022-Oct/RSIScanList.csv')
        if (tradescanlist == None):
            print('Could not get the scan list. Exiting algo.')
            return
        
        # user dependent
        dfstrategystatus = ss.GetStrategyStatus('/COMPANIES/IIQF/COURSES/CPAT/2022-Oct/RSIStrategyState.csv')
        if (dfstrategystatus == None):
            print('Could not get the scan list. Exiting algo.')
            return
        
        
        stopalgo = False
        
        print('Started algo')
        
        while (current_time < stoptime):
            
            print('Started scanning')
            for stocknum in range(len(tradescanlist)):
                stockname = tradescanlist.iloc[stocknum, slcol_stockname]
                stocksymbol = tradescanlist.iloc[stocknum, slcol_stocksymbol]
                lot_size = tradescanlist.iloc[stocknum, slcol_lotsize]
                mtm_pnl = 0.0
                mtm_pnl_pct = 0.0
                previous_exit_reason = ''
                
                print('Checking : ' + stockname)
                
                is_order_executing = ss.GetOrderExecutionStatus(dfstrategystatus, stocknum)
                
                if (is_order_executing == None):
                    # goto next stock
                    #continue
                    print('Error getting order execution status for ' + stockname)
                    stopalgo = True
                    break
                
                if (is_order_executing == False):
                    # if no orders are pending execution then we process this stock
                    
                    # todo
                    spotltp = api.GetQuote(stocksymbol)
                    
                    if (spotltp == None):
                        # goto next stock
                        #continue
                        print('Error getting live spot price for ' + stockname)
                        stopalgo = True
                        break
                    
                    pos = ss.GetPosition(dfstrategystatus, stocknum)
                    
                    if (pos == 0):
                        # if there are no open positions then check for ENTRY trade
                        
                        current_signal = sg.generate_signal_RSI_v1(stockname, windowperiod, long_entry, short_entry, historical_data_path)
                        
                        if (current_signal == None):
                            # goto next stock
                            print('Error generating signal for ' + stockname)
                            continue
#                            stopalgo = True
#                            break
                        
                        if (current_signal != 0):
                            # if we got a LONG or SHORT signal, take an Entry Trade
                            qty, price, exitreason = tg.generate_trade(spotltp, current_signal, 0, 0, capital, max_capital_deploy, 
                                                                       buy_margin, sell_margin, 0.0, 0.0, 0.0, lot_size, 
                                                                       previous_exit_reason)
                            
                            if (qty == None):
                                # goto next stock
                                print('Error generating trade for ' + stockname)
                                #continue
                                stopalgo = True
                                break
                            
                            if (qty != 0):
                                # todo
                                orderid = api.PlaceOrder(stockname, qty, price)
                                
                                if (orderid == None):
                                    # goto next stock
                                    print('Could not place order for ' + stockname)
                                    continue
#                                    stopalgo = True
#                                    break
                                
                                result = ss.UpdateStatus(dfstrategystatus, stocknum, True, qty, price, 0, 0, 0, orderid, 1, current_signal, '', True)
                                
                                if (result == False):
                                    # goto next stock
                                    #continue
                                    print('Could not update order status for ' + stockname)
                                    stopalgo = True
                                    break
#                            else:
                                # do nothing
                        else:
                            # if we got no signal, don't do anything
                            # do nothing
                            pass
                    else:
                        # if there are open positions then check for exit trade
                        
                        entry_price = ss.GetEntryPrice()
                        entry_signal = ss.GetEntrySignal()
                        
                        mtm_pnl = (spotltp - entry_price) * pos
                        mtm_pnl_pct = ((spotltp - entry_price) / entry_price) * entry_signal
                        
                        current_signal = sg.generate_signal_RSI(stockname, windowperiod)

                        if (current_signal == None):
                            # goto next stock
                            #continue
                            print('Error generating signal for ' + stockname)
                            stopalgo = True
                            break
                        
                        if (current_signal != entry_signal):
                            # if the new signal is different from the entry signal, take an EXIT Trade
                            
                            qty, price, exitreason = tg.generate_trade(spotltp, current_signal, pos, entry_signal, capital, max_capital_deploy, 
                                                                       buy_margin, sell_margin, pnl_target, pnl_stoploss, mtm_pnl_pct, lot_size, previous_exit_reason)
                            
                            if (qty == None):
                                # goto next stock
                                #continue
                                print('Error generating trade for ' + stockname)
                                stopalgo = True
                                break
                            
                            if (qty != 0):
                                # todo
                                orderid = PlaceOrder(stockname, qty, price)
                                
                                if (orderid == None):
                                    # goto next stock
                                    #continue
                                    print('Could not place order for ' + stockname)
                                    stopalgo = True
                                    break
                                
                                result = ss.UpdateStatus(dfstrategystatus, stocknum, False, qty, price, 0, 0, 0, orderid, 1, 0, exitreason, True)
                                
                                if (result == False):
                                    # goto next stock
                                    #continue
                                    print('Could not update order status for ' + stockname)
                                    stopalgo = True
                                    break
                            
                            
                            # todo - if you want to take  reverse position
                            
#                            qty, price = tg.generate_trade(current_signal, pos)
#                            
#                            if (qty == None):
#                                # goto next stock
#                                #continue
#                                print('Error generating trade for ' + stockname)
#                                stopalgo = True
#                                break
#                            
#                            if (qty != 0):
#                                # todo
#                                ord = PlaceOrder(stockname, qty, price)
#                                
#                                if (ord == None):
#                                    # goto next stock
#                                    #continue
#                                    print('Could not place order for ' + stockname)
#                                    stopalgo = True
#                                    break
#                                
#                                result = UpdateStatus()
#                                
#                                if (result == False):
#                                    # goto next stock
#                                    #continue
#                                    print('Could not update order status for ' + stockname)
#                                    stopalgo = True
#                                    break
                            
                            
                        else:
                            # todo - merge this and the previous condition
                            # if the entry signal is still continuing, we hold position
                            # check for PnL based exit (target or stoploss)
                            qty, price, exitreason = tg.generate_trade(spotltp, current_signal, pos, entry_signal, capital, max_capital_deploy, 
                                                                       buy_margin, sell_margin, pnl_target, pnl_stoploss, mtm_pnl_pct, lot_size, previous_exit_reason)
                    
                            if (qty == None):
                                # goto next stock
                                #continue
                                print('Error generating trade for ' + stockname)
                                stopalgo = True
                                break
                            
                            if (qty != 0):
                                # todo
                                ord = PlaceOrder(stockname, qty, price)
                                
                                if (ord == None):
                                    # goto next stock
                                    #continue
                                    print('Could not place order for ' + stockname)
                                    stopalgo = True
                                    break
                                
                                result = UpdateStatus()
                                
                                if (result == False):
                                    # goto next stock
                                    #continue
                                    print('Could not update order status for ' + stockname)
                                    stopalgo = True
                                    break
#                            else:
                                # if order qty =0 then do nothing
                    
                    
                else:
                    # if an order is pending execution then we check its status from the API
                    
                    # this is less efficient way ... get all the status details in a single function call, - todo later

                    is_entry_trade = ss.IsEntryTrade(dfstrategystatus, stocknum)
                    
                    orderid = ss.GetOrderID(dfstrategystatus, stocknum, is_entry_trade)
                    
                    # get the status from the API
                    filledqty, tradeprice, isorderexecuting = api.GetOrderStatus(orderid)
                    
                    if (filledqty == None):
                        # goto next stock
                        continue
                    
                    qty = ss.GetOrderQty(dfstrategystatus, stocknum, is_entry_trade)
                    
                    result = ss.UpdateStatus(dfstrategystatus, stocknum, is_entry_trade, qty, 0, 0, filledqty, tradeprice, 0, isorderexecuting, 0, '', False)
                    
            
            # end of the for loop - goto the next stock
                    
            print('Ended scan')
            # end of the for loop
            
            # write the strategy status dataframe back to disk file
            myutils.write_dataframe(dfstrategystatus)
            
            if (stopalgo == True):
                print('Some error has forced the algo to stop')
                break
            
            current_time = mydateutils.DateTimeFunctions.CurrentTime()
            
            if (current_time > stoptime):
                break
            
            time.sleep(scan_interval * 60)
            
        # end of the while loop
        
        # algo has exited the while loop
        
        print('Algo stopped for the day')
        
    except Exception as errmsg:
        print(errmsg)
    


RSIScanner()



