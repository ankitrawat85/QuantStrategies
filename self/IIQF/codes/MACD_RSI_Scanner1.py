# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 11:39:45 2023

@author: User1
"""

import time

import myutils
import mydateutils
from kiteconnect import KiteConnect
import signal_generator_ta as sg
import trade_generator as tg
import strategy_status as ss
import settings
import scanlist
import numpy as np
import api_wrapper


# user dependent
historical_data_path = 'C:/DATA/NSE/Equity'
scan_interval = 10


# constant for status etc

# scanlist column constants
slcol_fut_symbol = 0
slcol_fut_trdsymbol = 1
slcol_stockname = 2
slcol_optiontype = 3
slcol_insttype = 4
slcol_strikeprice = 5
slcol_expiry = 6
slcol_lotsize = 7
slcol_fut_exchange = 8
slcol_spot_symbol = 9
slcol_spot_trdsymbol = 10
slcol_spot_exchange = 11


# order status column constants
tscol_tradeprice = 12
tscol_filledqty = 13
tscol_pendingqty = 14
tscol_cancellledqty = 15
tscol_status = 19
tscol_status_message = 20


# dependent on your strategy
starttime = mydateutils.DateTimeFunctions.StrToTime('9:15:0')
stoptime = mydateutils.DateTimeFunctions.StrToTime('15:15:0')


def GetOrderStatus(api, order_id):
    # this function is very mch broker API dependent
    # MUST BE coded as per the API
    try:
        order_state_history = api.order_history(order_id)
        
        s = order_state_history[len(order_state_history) - 1]
        
        status = [s['exchange'], s['tradingsymbol'], s['instrument_token'], s['order_type'], s['validity'], s['product'], s['variety'], s['transaction_type'],s['quantity'],s['disclosed_quantity'],s['price'],s['trigger_price'],s['average_price'],s['filled_quantity'],s['pending_quantity'],s['cancelled_quantity'],s['order_id'],s['exchange_order_id'],s['placed_by'],s['status'],s['status_message'],s['status_message_raw'],str(s['order_timestamp']),str(s['exchange_timestamp']),str(s['exchange_update_timestamp']), s['tag'] ]
        
        return status
    except:
        return None
   
    
def generate_signal(stockname, ltp, rsi_period, rsi_long_entry, rsi_short_entry, macd_short_period, macd_long_period, macd_long_entry, macd_short_entry, data_path, close = 'Close', conditon = 'AND'):
    
    rsi_signal = sg.generate_signal_RSI_v1(stockname, ltp, rsi_period, rsi_long_entry, rsi_short_entry, historical_data_path)
    
    macd_signal = sg.generate_signal_MACD_v1(stockname, ltp, macd_short_period, macd_long_period, macd_long_entry, macd_short_entry, historical_data_path)
    
    signal = 0
    
    if (conditon == 'AND'):
        # # AND operator
        if ((rsi_signal == 1) & (macd_signal == 1)):
            signal = 1
        elif ((rsi_signal == -1) & (macd_signal == -1)):
            signal = -1
        else:
            signal = 0
    else:
        # OR operator
        if ((rsi_signal == 1) | (macd_signal == 1)):
            signal = 1
        elif ((rsi_signal == -1) | (macd_signal == -1)):
            signal = -1
        else:
            signal = 0
    
    return signal


def MACD_RSI_Scanner():
    try:
        
        current_time = mydateutils.DateTimeFunctions.CurrentTime()
        
        if ((current_time < starttime) | (current_time > stoptime)):
            print('Market is closed for the algo')
            return
        
        #######################################
        # broker dependent part of code
        
        # get the manual login process part done and put the access_code in the settings file
        
        userid, password, api_key, api_secret, request_token, acountid = settings.GetAPIPara()
        
        request_token = input('Request Token :')
        
        if type(api_key) == str:
            if (api_key == ''):
                print('Could not read API settings. Exiting algo.')
                return
        else:
            pass
        
#        if ( (userid == None) | (np.isnan(userid)) | (api_key == None) | (np.isnan(api_key)) | (api_secret == None) | (np.isnan(api_secret)) | (request_token == None) | (np.isnan(request_token))):
#            print('Could not read API settings. Exiting algo.')
#            return
        
        api = KiteConnect(api_key=api_key)
        
        try:
            access_token = api.generate_session(request_token, api_secret)["access_token"]
            api.set_access_token(access_token)
        except:
            return
        
        
        #######################################
        
        ######################################
        
        # strategy dependent
        rsi_windowperiod, rsi_long_entry, rsi_short_entry = settings.GetSignalPara_RSI()
        macd_short_period, macd_long_period, macd_long_entry, macd_short_entry = settings.GetSignalPara_MACD()
        
        if (rsi_windowperiod == None):
            print('Could not get the RSI signal parameters. Exiting algo.')
            return
        
        if (macd_short_period == None):
            print('Could not get the MACD signal parameters. Exiting algo.')
            return
        
        # strategy dependent
        capital, max_capital_deploy, buy_margin, sell_margin, pnl_target, pnl_stoploss = settings.GetTradePara()
        if (capital == None):
            print('Could not get the trade parameters. Exiting algo.')
            return
        
        # strategy dependent
        tradescanlist = scanlist.GetScanList('/COMPANIES/IIQF/COURSES/CPAT/2022-Oct/MACDScanList.csv')
        if (tradescanlist.empty):
            print('Could not get the scan list. Exiting algo.')
            return
        
        # user dependent
        dfstrategystatus = ss.GetStrategyStatus('/COMPANIES/IIQF/COURSES/CPAT/2022-Oct/MACD_RSI_StrategyState.csv')
        if (dfstrategystatus.empty):
            print('Could not get the scan list. Exiting algo.')
            return
        
        
        stopalgo = False
        
        print('Started algo')
        
        while (current_time < stoptime):
            
            print('Started scanning')
            for stocknum in range(len(tradescanlist)):
                fut_exchange = tradescanlist.iloc[stocknum, slcol_fut_exchange]
                stockname = tradescanlist.iloc[stocknum, slcol_stockname]
                fut_trdsymbol = tradescanlist.iloc[stocknum, slcol_fut_trdsymbol]
                fut_symbol = tradescanlist.iloc[stocknum, slcol_fut_symbol]
                
                spot_trdsymbol = tradescanlist.iloc[stocknum, slcol_spot_trdsymbol]
                spot_symbol = tradescanlist.iloc[stocknum, slcol_spot_symbol]
                spot_exchange = tradescanlist.iloc[stocknum, slcol_spot_exchange]
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
                    
                    spotltp = api_wrapper.get_ltp(spot_exchange, spot_trdsymbol, spot_symbol, 'ZERODHA', api)
                    
                    if (spotltp == None):
                        # goto next stock
                        #continue
                        print('Error getting live spot price for ' + stockname)
                        stopalgo = True
                        break
                    
                    pos = ss.GetPosition(dfstrategystatus, stocknum)
                    
                    if (pos == 0):
                        # if there are no open positions then check for ENTRY trade
                        
                        current_signal = generate_signal(stockname, spotltp, rsi_windowperiod, rsi_long_entry, rsi_short_entry, macd_short_period, macd_long_period, macd_long_entry, macd_short_entry, historical_data_path)
                        
                        if (current_signal == None):
                            # goto next stock
                            print('Error generating signal for ' + stockname)
                            continue
#                            stopalgo = True
#                            break
                        
                        if (current_signal != 0):
                            # if we got a LONG or SHORT signal, take an Entry Trade
                            
                            futltp = api_wrapper.get_ltp(fut_exchange, fut_trdsymbol, fut_symbol, 'ZERODHA', api)
                            
                            qty, price, exitreason = tg.generate_trade(futltp, current_signal, 0, 0, capital, max_capital_deploy, 
                                                                       buy_margin, sell_margin, 0.0, 0.0, 0.0, lot_size, 
                                                                       previous_exit_reason)
                            
                            
                            if (qty == None):
                                # goto next stock
                                print('Error generating trade for ' + stockname)
                                #continue
                                stopalgo = True
                                break
                            
                            if (qty != 0):
                                if (qty > 0):
                                    orderid = api_wrapper.place_order(fut_exchange, fut_trdsymbol, fut_symbol, "BUY", 'DAY', 'LIMIT', False, False, qty, price, 'regular', 'ZERODHA', api)
                                else:
                                    orderid = api_wrapper.place_order(fut_exchange, fut_trdsymbol, fut_symbol, "SELL", 'DAY', 'LIMIT', False, False, -qty, price, 'regular', 'ZERODHA', api)
                                
                                if (orderid == ''):
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
                        
                        entry_price = ss.GetEntryPrice(dfstrategystatus, stocknum)
                        entry_signal = ss.GetEntrySignal(dfstrategystatus, stocknum)

                        futltp = api_wrapper.get_ltp(fut_exchange, fut_trdsymbol, fut_symbol, 'ZERODHA', api)
                        
                        # todo - in case of partial exit proper mtm pl calcultaion needs to be done
                        mtm_pnl = (futltp - entry_price) * pos
                        mtm_pnl_pct = ((futltp - entry_price) / entry_price) * entry_signal
                        
                        print('MTM PL on ' + fut_trdsymbol + ' : ' + '{:.2f}'.format(mtm_pnl))
                        print('MTM PL % on ' + fut_trdsymbol + ' : ' + '{:.2f}%'.format(mtm_pnl_pct * 100))
                        
                        current_signal = generate_signal(stockname, spotltp, rsi_windowperiod, rsi_long_entry, rsi_short_entry, macd_short_period, macd_long_period, macd_long_entry, macd_short_entry, historical_data_path)
                        
                        if (current_signal == None):
                            # goto next stock
                            #continue
                            print('Error generating signal for ' + stockname)
                            stopalgo = True
                            break
                        
                        # todo - in case of partial exit proper exit QTY calcultaion needs to be done
                        qty, price, exitreason = tg.generate_trade(futltp, current_signal, pos, entry_signal, capital, max_capital_deploy, 
                                                                   buy_margin, sell_margin, pnl_target, pnl_stoploss, mtm_pnl_pct, lot_size, previous_exit_reason)
                        
                        if (qty == None):
                            # goto next stock
                            #continue
                            print('Error generating trade for ' + stockname)
                            stopalgo = True
                            break

                        if (qty != 0):
                            # if current signal changes or 
                            # cPnL based exit (target or stoploss) has hit
                            
                            if (qty > 0):
                                orderid = api_wrapper.place_order(fut_exchange, fut_trdsymbol, fut_symbol, "BUY", 'DAY', 'LIMIT', False, False, qty, price, 'regular', 'ZERODHA', api)
                            else:
                                orderid = api_wrapper.place_order(fut_exchange, fut_trdsymbol, fut_symbol, "SELL", 'DAY', 'LIMIT', False, False, -qty, price, 'regular', 'ZERODHA', api)
                            
                            if (orderid == ''):
                                # goto next stock
                                print('Could not place order for ' + stockname)
                                continue
#                                stopalgo = True
#                                break
                            
                            result = ss.UpdateStatus(dfstrategystatus, stocknum, False, qty, price, 0, 0, 0, orderid, 1, 0, exitreason, True)
                            
                            if (result == False):
                                # goto next stock
                                #continue
                                print('Could not update order status for ' + stockname)
                                stopalgo = True
                                break
#                        else:
#                            # if the entry signal is still continuing, we hold position
#                            # if order qty =0 then do nothing
#                            pass
                    
                else:
                    # if an order is pending execution then we check its status from the API
                    # we are NOT doing MTM PL for partial executed orders
                    
                    # this is less efficient way ... get all the status details in a single function call, - todo later
                    
                    is_entry_trade = ss.IsEntryTrade(dfstrategystatus, stocknum)
                    
                    orderid = ss.GetOrderID(dfstrategystatus, stocknum, is_entry_trade)
                    
                    qty = ss.GetOrderQty(dfstrategystatus, stocknum, is_entry_trade)
                    
                    # get the status from the API
                    order_status = api_wrapper.get_order_status(orderid, 'ZERODHA', api)
                    
                    if (len(order_status) == 0):
                        # goto next stock
                        continue
                    
                    tradeprice = order_status[tscol_tradeprice]
                    filledqty = order_status[tscol_filledqty]
                    orderstatus = order_status[tscol_status].upper()
                    
                    if (qty < 0):
                        filledqty = (-filledqty)
                    
                    if ((orderstatus == 'REJECTED') | (orderstatus == 'CANCELLED') | (orderstatus == 'COMPLETE')):
                        isorderexecuting = False
                    
                    result = ss.UpdateStatus(dfstrategystatus, stocknum, is_entry_trade, qty, 0, 0, filledqty, tradeprice, 0, isorderexecuting, 0, '', False)
                    
            
                #end of is executing check 
                
            # end of the for loop - goto the next stock
                    
            print('Ended scan')
            # end of the for loop
            
            # write the strategy status dataframe back to disk file
            myutils.write_dataframe('/COMPANIES/IIQF/COURSES/CPAT/2022-Oct/MACD_RSI_StrategyState.csv', dfstrategystatus)
            
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
    


MACD_RSI_Scanner()



