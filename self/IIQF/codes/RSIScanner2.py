# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 11:50:09 2023

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

# user dependent
historical_data_path = 'C:/DATA/NSE/Equity'
scan_interval = 5


# constant for status etc
# todo

# scanlist column constants
slcol_stockname = 0
slcol_stocksymbol = 1



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
        # todo later
        username, pasword = GetAPISettings()
        
        # todo
        # check if we got settings else exit
        
        if (ConnectToAPI() == False):
            print('Could not connect to API. Exiting algo.')
            return
        
        lg = LoginAPI()
        
        # todo  check if login was successful else exit
        
        
        #######################################
        
        ######################################
        # strategy dependent
        
        # todo
        capital, max_capital_deploy = GetTradePara()
        
        # todo
        windowperiod = GetSignalPara()
        
        # todo
        tradescanlist = GetScanList()
        
        # todo
        strategystatus = ss.GetStrategyStatus()
        
        stopalgo = False
        
        print('Started algo')
        
        while (current_time < stoptime):
            print('Started scanning')
            
            for stocknum in range(len(tradescanlist)):
                stockname = tradescanlist.iloc[stocknum, slcol_stockname]
                stocksymbol = tradescanlist.iloc[stocknum, slcol_stocksymbol]
                
                
                print('Checking : ' + stockname)
                
                is_order_executing = GetOrderExecutionStatus(stocknum)
                
                if (is_order_executing == False):
                    # if no orders are pending execution then we process this stock
                    
                    # todo
                    spotltp = GetQuote(stocksymbol)
                    
                    if (spotltp == None):
                        # goto next stock
                        #continue
                        print('Error getting live spot price for ' + stockname)
                        stopalgo = True
                        break
                    
                    pos = GetPosition(stocknum)
                    
                    if (pos == 0):
                        # if there are no open positions then check for ENTRY trade
                        
                        # todo
                        current_signal = sg.generate_signal_RSI(stockname, windowperiod)
                        
                        if (current_signal == None):
                            # goto next stock
                            #continue
                            print('Error generating signal for ' + stockname)
                            stopalgo = True
                            break
                        
                        if (current_signal != 0):
                            # if we got a LONG or SHORT signal, take an Entry Trade
                            # todo
                            qty, price = tg.generate_trade(current_signal, pos)
                            
                            if (qty == None):
                                # goto next stock
                                #continue
                                print('Error generating signal for ' + stockname)
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
                        else:
                            # if we got no signal, don't do anything
                            # do nothing
                            pass
                    else:
                        # if there are open positions then check for exit trade
                        
                        entry_signal = GetEntryStatus()
                        
                        # todo
                        current_signal = sg.generate_signal_RSI(stockname, windowperiod)

                        if (current_signal == None):
                            # goto next stock
                            #continue
                            print('Error generating signal for ' + stockname)
                            stopalgo = True
                            break
                        
                        if (current_signal != entry_signal):
                            # if the new signal is different from the entry signal, take an EXIT Trade
                            # todo
                            
                            if (current_signal == 0):
                                # square off
                                qty = -pos
                                price = spotltp
                            else:
                                qty, price = tg.generate_trade(current_signal, pos)
                                
                                qty = qty - pos
                                
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
                            
                            
                        else:
                            # if the entry signal is still continuing, we hold position
                            # do nothing
                            pass
                    
                    
                else:
                    # if an order is pending exectuion then we check its status from the API
                    
                    ordstatus = GetOrderStatus()
                    if (ordstatus == None):
                        # goto next stock
                        continue
                    
                    UpdateStatus()
                    
                    
                    
        
        time.sleep(scan_interval * 60)
        
        
        
        
        
        
        
        
    except Exception as errmsg:
        print(errmsg)
    
    
    
    
    
    








