# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 10:03:34 2023

@author: Abhijit Biswas
"""

import time
import datetime as dt
import sys

# import our Python Wrapper for Zerodha REST API
import zerodha

#import my libs
import myutils
from mydateutils import DateTimeFunctions as dtf

#import associated libs
import pt_SignalParams as sp
import pt_signal_generators as sg
import pt_TradeParams as tp
import pt_generate_trade as gen_trade
import api_settings
import pt_strategy_status as ss


# column numbers of the PairsTradingScanList.csv file
tslcol_stocksymbolname1 = 0
tslcol_futtrdsymbolname1 = 1
tslcol_futtrdsymbol1 = 2
tslcol_expirydate1 = 3
tslcol_lotsize1 = 4
tslcol_stocksymbolname2 = 5
tslcol_futtrdsymbolname2 = 6
tslcol_futtrdsymbol2 = 7
tslcol_expirydate2 = 8
tslcol_lotsize2 = 9


# column numbers of strategy state file
sscol_symbolLeg1 = 0
sscol_trdsymbolLeg1 = 1
sscol_symbolnameLeg1 = 2
sscol_EntryOrderQtyLeg1 = 3
sscol_EntryOrderPriceLeg1 = 4
sscol_EntryModifiedPriceLeg1 = 5
sscol_EntryFilledQtyLeg1 = 6
sscol_EntryBalanceQtyLeg1 = 7
sscol_EntryPriceLeg1 = 8
sscol_EntryOrderIDLeg1 = 9
sscol_EntryExecutingLeg1 = 10
sscol_EntrySignalLeg1 = 11
sscol_ExitOrderQtyLeg1 = 12
sscol_ExitOrderPriceLeg1 = 13
sscol_ExitModifiedPriceLeg1 = 14
sscol_ExitFilledQtyLeg1 = 15
sscol_ExitBalanceQtyLeg1 = 16
sscol_ExitPriceLeg1 = 17
sscol_ExitOrderIDLeg1 = 18
sscol_ExitExecutingLeg1 = 19
sscol_ExitReasonLeg1 = 20

sscol_symbolLeg2 = 21
sscol_trdsymbolLeg2 = 22
sscol_symbolnameLeg2 = 23
sscol_EntryOrderQtyLeg2 = 24
sscol_EntryOrderPriceLeg2 = 25
sscol_EntryModifiedPriceLeg2 = 26
sscol_EntryFilledQtyLeg2 = 27
sscol_EntryBalanceQtyLeg2 = 28
sscol_EntryPriceLeg2 = 29
sscol_EntryOrderIDLeg2 = 30
sscol_EntryExecutingLeg2 = 31
sscol_ExitOrderQtyLeg2 = 32
sscol_ExitOrderPriceLeg2 = 33
sscol_ExitModifiedPriceLeg2 = 34
sscol_ExitFilledQtyLeg2 = 35
sscol_ExitBalanceQtyLeg2 = 36
sscol_ExitPriceLeg2 = 37
sscol_ExitOrderIDLeg2 = 38
sscol_ExitExecutingLeg2 = 39

# Zerodha API Order Status Constants
col_orderstatus = 24
col_orderstatusmessage = 25


# global variables

scan_frequency = 15
SignalParaFile = "SignalPara.csv"
TradeParaFile = "TradePara.csv"
ScanListFile = "ScanList.csv"
StrategyStateFile = "StrategyState.csv"
Hist_data_path  = '/YahooData/'

# broker dependent
masters_data_file = '/Brokers/Zerodha/Masters/NSE_FUT.csv'
# get from broker after registering the application
api_key = ''
api_secret = ''
userid = ''
pswd = ''
access_token = ''
spot_exchange = "NSE"
fo_exchange = "NSE"
segment = 'NFO'
order_duration = "DAY" # GTD or IOC
product = 'NRML'

errctr = 0
maxerrcnt = 3

#modify_tolerance = 0.001 # 0.1%
#cancel_tolerance = 0.005 # 0.5%

# todo later
# roll over of open futures positions


# dependent on your strategy
starttime = dtf.StrToTime('9:15:0')
stoptime = dtf.StrToTime('15:15:0')


def connecttoapi(userid, pswd, api_key, api_secret, access_token, access_token_date):
    try:
        
        if (access_token_date != dtf.CurrentDateStr()):
            request_token = ''
            # todo later - get the request token from inside python
            request_token = input('Request Token :')
            
            if (request_token == ''):
                print('request_token not found. Exiting algo.')
                return False
            
            access_token = zerodha.get_access_token(api_key, api_secret, request_token, True)
            if (access_token == None):
                print('ERROR: access_token not found. Exiting algo.')
                return False
            elif (access_token == ''):
                print('ERROR: access_token not found. Exiting algo.')
                return False
            
            api_settings.SaveAPIPara(userid, pswd, api_key, api_secret, access_token, dtf.CurrentDateStr())
        
        return True
    
    except Exception as ex:
        print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return False
    
#    api = KiteConnect(api_key=api_key)
#    
#    try:
#        access_token = api.generate_session(request_token, api_secret)["access_token"]
#        api.set_access_token(access_token)
#        return True
#    except:
#        return False


def GetLTP(api_key, access_token, exchange, segment, tradesymbol):
    # broker dependent
    
    try:
        quote = zerodha.get_quote(api_key, access_token, exchange, segment, tradesymbol)
        ltp = quote[6]
        
        return ltp
    except Exception as ex:
        print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return 0

def GetOrderStatus(api_key, access_token, order_id):
    # this function is very mch broker API dependent
    # MUST BE coded as per the API
    try:
        status = zerodha.get_order_status(api_key, access_token, order_id)
        
        return status
    except:
        return None

def GetOrderStatusMessage(api_key, access_token, order_id):
    # this function is very mch broker API dependent
    # MUST BE coded as per the API
    try:
        status = zerodha.get_order_status(api_key, access_token, order_id)[col_orderstatusmessage]
        
        return status
    except Exception as ex:
        print(sys._getframe().f_code.co_name, 'exception: ', ex)
        return None


def Scanner():
    
    try:
        
        current_time = dtf.CurrentTime()
        
        if ((current_time < starttime) | (current_time > stoptime)):
            print('Market is closed for the algo')
            return
        
        #######################################
        # broker dependent part of code
        
        # get the manual login process part done and put the access_token in the settings file
        
        userid, password, api_key, api_secret, access_token, access_token_date = api_settings.GetAPIPara()
#        if ( (userid == None) | (np.isnan(userid)) | (api_key == None) | (np.isnan(api_key)) | (api_secret == None) | (np.isnan(api_secret)) | (request_token == None) | (np.isnan(request_token))):
#            print('Could not read API settings. Exiting algo.')
#            return
        
        if type(api_key) == str:
            if (api_key == ''):
                print('Could not read API settings. Exiting algo.')
                return False
        else:
            print('Could not read API settings. Exiting algo.')
            return False
        
        masterdata = myutils.read_dataframe(masters_data_file)
        if (masterdata.empty):
            print("Masters data file not found")
            return
        
        # user dependent
        # get the strategy states
        strategy_state = ss.ReadStrategyStatusFile(StrategyStateFile)
        if (strategy_state.empty):
            print('Strategy State file not found. Exiting algo.')
            return
        
        # get all the signal parameters
        short_window, long_window, long_entry, long_exit, long_stoploss, short_entry, short_exit, short_stoploss = sp.GetSignalPara_PairsTrading(SignalParaFile)
        if (long_entry == None):
            print("Signal parameters file not found")
            return
        
        # get all the trade parameters
        capital_allocated, max_capital_to_deploy, buy_margin, sell_margin, target, stoploss, trading_cost = tp.GetTradePara(TradeParaFile)
        if (capital_allocated == None):
            print("Trade parameters file not found")
            return
        
        # get the stock list file to scan through
        scan_list = myutils.read_dataframe(ScanListFile)
        if (scan_list.empty):
            print("Scan list file not found")
            return
        
        
        #######################################
        # broker dependent part of code
        
        #######################################
        # connect to the API
        if (connecttoapi(userid, pswd, api_key, api_secret, access_token, access_token_date) == False):
            return
        
        print("Starting algo system")
        
        stopalgo = False
        errctr = 0
        
        # scan the market every specfied time interval, check the prices of the stocks in the scan list and check for signals
        while (dt.datetime.now().time() < stoptime):
            print("Starting scan")
            
            for pairnum in range(len(scan_list)):
                stockname1 = scan_list.iloc[pairnum, tslcol_stocksymbolname1]
                stockname2 = scan_list.iloc[pairnum, tslcol_stocksymbolname2]
                
                print("Checking pair :" + stockname1 + '/' + stockname2)
                
                # VERY IMPORTANT TODO
                # Of we are not stopping algo on error in placing orders, then we must check the individual legs
                # for order executing and order placement failure and make provisions for re-placement of failed orders
                is_order_executing = ss.IsOrderExecuting(strategy_state, pairnum)
                
                if (is_order_executing == False):
                    # no open orders are pending execution on this pair
                    
                    nearestexpfuttrdsymbol1 = scan_list.iloc[pairnum, tslcol_futtrdsymbol1]
                    lot_size1 = scan_list.iloc[pairnum, tslcol_lotsize1]
                    
                    nearestexpfuttrdsymbol2 = scan_list.iloc[pairnum, tslcol_futtrdsymbol2]
                    lot_size2 = scan_list.iloc[pairnum, tslcol_lotsize2]
                    
                    # call the API to get the nearest expiry futures price of stock 1
                    nearestexpiryfuturesprice1 = GetLTP(api_key, access_token, fo_exchange, 'FNO', nearestexpfuttrdsymbol1)
                    if (nearestexpiryfuturesprice1 == None):
                        # todo maybe raise some alert for the user
                        print("Error occured in getting futures LTP for " + stockname1 + ". Algo stopped by system.")
                        stopalgo = True
                        break
                    elif (nearestexpiryfuturesprice1 == 0):
                        # todo maybe raise some alert for the user
                        print("Error occured in getting futures LTP for " + stockname1)
                        errctr = errctr + 1
                        if (errctr > maxerrcnt):
                            print("Algo stopped by system")
                            stopalgo = True
                        break
                    
                    nearestexpiryfuturesprice1 = float(nearestexpiryfuturesprice1)
                    
                    # call the API to get the nearest expiry futures price of stock 2
                    nearestexpiryfuturesprice2 = GetLTP(api_key, access_token, fo_exchange, 'FNO', nearestexpfuttrdsymbol2)
                    if (nearestexpiryfuturesprice2 == None):
                        # todo maybe raise some alert for the user
                        print("Error occured in getting futures LTP for " + stockname2 + ". Algo stopped by system.")
                        stopalgo = True
                        break
                    elif (nearestexpiryfuturesprice2 == 0):
                        # todo maybe raise some alert for the user
                        print("Error occured in getting futures LTP for " + stockname2)
                        errctr = errctr + 1
                        if (errctr > maxerrcnt):
                            print("Algo stopped by system")
                            stopalgo = True
                        break
                    
                    nearestexpiryfuturesprice2 = float(nearestexpiryfuturesprice2)
                    print(nearestexpiryfuturesprice1, nearestexpiryfuturesprice2)
                    
                    
                    spotprice1 = myutils.read_stock_data(stockname1, Hist_data_path)
                    if (spotprice1.empty):
                        print('Historical price not found for: ' + stockname1)
                        break
                    
                    spotprice2 = myutils.read_stock_data(stockname2, Hist_data_path)
                    if (spotprice2.empty):
                        print('Historical price not found for: ' + stockname2)
                        break
                    
                    current_pos_leg1 = ss.GetPosition(strategy_state, pairnum, 1)
                    current_pos_leg2 = ss.GetPosition(strategy_state, pairnum, 2)
                    
                    # generate signal
                    current_signal = sg.generate_signal(spotprice1, spotprice2, current_pos_leg1, short_window, long_window, long_entry, long_exit, long_stoploss, short_entry, short_exit, short_stoploss)
                    if (current_signal == None):
                        # either stop the algo or you might continue with other stocks
                        # todo maybe raise some alert for the user
                        print("Error occured in generating signal for pair : " + stockname1 + '/' + stockname2 + ". Algo stopped by system.")
                        stopalgo = True
                        break
                    
                    print("Signal: " + str(current_signal))
                    
                    prev_signal = ss.GetPreviousSignal(strategy_state, pairnum)
                    
                    if ((current_pos_leg1 != 0) or (current_pos_leg2 != 0)):
                        leg1ltp = GetLTP(api_key, access_token, fo_exchange, 'FNO', nearestexpfuttrdsymbol1)
                        leg2ltp = GetLTP(api_key, access_token, fo_exchange, 'FNO', nearestexpfuttrdsymbol2)
                        
                        entryprice1 =  ss.GetEntryPrice(strategy_state, pairnum, 1)
                        entryprice2 =  ss.GetEntryPrice(strategy_state, pairnum, 2)
                        
                        # this does not capture the PL on the exited qty
                        # todo later - this must be altered to take into account 
                        # booked PL of partially executed order
                        mtmleg1 = (leg1ltp - entryprice1) * current_pos_leg1
                        mtmleg2 = (leg2ltp - entryprice2) * current_pos_leg2
                        
                        mtm_pl = mtmleg1 + mtmleg2
                        
                        isentrytrade = False
                    else:
                        mtm_pl = 0
                        isentrytrade = True
                        
                    if ((current_signal != 0) or (current_pos_leg1 != 0) or (current_pos_leg2 != 0)):
                        # if we have a signal
                        
                        prev_exit_reason = ss.GetPreviousExitReason(strategy_state, pairnum)
                        
                        # generate a trade
                        orderqty1, orderqty2, orderprice1, orderprice2, exitreason = gen_trade.GenerateTrade(nearestexpiryfuturesprice1, nearestexpiryfuturesprice2, lot_size1, lot_size2, current_pos_leg1, current_pos_leg2, current_signal, prev_signal, capital_allocated, max_capital_to_deploy, buy_margin, sell_margin,  target, stoploss, mtm_pl, prev_exit_reason)
                        
                        # Place the order to the Exchange
                        if ((orderqty1 > 0) or (-orderqty2 > 0)) :
                            # Place a LONG order on the pair
                            
                            # we are placing trades on both the legs simultaneously, later on we can fire the less liquid leg 1st
                            # and then check its completion and fire the more liquid leg after the less liquid leg leg has gone through
                            if (orderqty1 > 0) :
                                trdsymbol1 = nearestexpfuttrdsymbol1
                                
                                # API Call to place the order
                                orderid1 = zerodha.place_order(api_key, access_token, fo_exchange, 'FNO', trdsymbol1, 'BUY', "LIMIT", orderqty1, orderprice1, product, order_duration, order_variety='REGULAR', printerrormessage = True)
                                if (orderid1 == None):
                                    # print("Error occured in placing order for " + spotsymbol + ". Algo stopped by system.")
                                    # stopalgo = True
                                    # break
                                    print("BUY order for " + trdsymbol1 + " could not be placed.")
                                    # VERY IMPORTANT TODO
                                    # check if last order on this leg failed, then place the order on this leg again
                                    errctr = errctr + 1
                                    if (errctr > maxerrcnt):
                                        stopalgo = True
                                    break
                                    
                                if (orderid1 != ''):
                                    print("Order placed successfully. BUY order for " + trdsymbol1 + " qty:" + str(orderqty1) + " @ " + str(orderprice1) + " orderid: " + orderid1)
                                    
                                    # update the status file
                                    st = ss.UpdateStatus(isentrytrade, pairnum, 1, orderqty1, orderprice1, 0, 0, 0, orderid1, 1, current_signal, exitreason, strategy_state, True)
                                    
                                    if (st == False):
                                        print("Error occured in saving status " + trdsymbol1 + ". Algo stopped by system.")
                                        stopalgo = True
                                        break
                                else:
                                    print("BUY order for " + trdsymbol1 + " could not be placed.")
                                    # check if last order on this leg failed, then place the order on this leg again
                                    errctr = errctr + 1
                                    if (errctr > maxerrcnt):
                                        stopalgo = True
                                    break
                                
                            if (orderqty2 < 0) :
                                trdsymbol2 = nearestexpfuttrdsymbol2
                                
                                # API Call to place the order
                                orderid2 = zerodha.place_order(api_key, access_token, fo_exchange, 'FNO', trdsymbol2, 'SELL', "LIMIT", abs(orderqty2), orderprice2, product, order_duration, order_variety='REGULAR', printerrormessage = True)
                                if (orderid2 == None):
                                    # print("Error occured in placing order for " + spotsymbol + ". Algo stopped by system.")
                                    # stopalgo = True
                                    # break
                                    print("SELL order for " + trdsymbol2 + " could not be placed.")
                                    # VERY IMPORTANT TODO
                                    # check if last order on this leg failed, then place the order on this leg again
                                    errctr = errctr + 1
                                    if (errctr > maxerrcnt):
                                        stopalgo = True
                                    break
                                
                                if (orderid2 != ''):
                                    print("Order placed successfully. SELL order for " + trdsymbol2 + " qty:" + str(orderqty2) + " @ " + str(orderprice2) + " orderid: " + orderid2)
                                    
                                    # update the status file
                                    st = ss.UpdateStatus(isentrytrade, pairnum, 2, orderqty2, orderprice2, 0, 0, 0, orderid2, 2, current_signal, exitreason, strategy_state, True)
                                    
                                    if (st == False):
                                        print("Error occured in saving status " + trdsymbol2 + ". Algo stopped by system.")
                                        stopalgo = True
                                        break
                                else:
                                    print("SELL order for " + trdsymbol2 + " could not be placed.")
                                    # check if last order on this leg failed, then place the order on this leg again
                                    errctr = errctr + 1
                                    if (errctr > maxerrcnt):
                                        stopalgo = True
                                    break
                                
                        elif ((orderqty1 < 0) or (orderqty2 < 0)) :
                            # Place a SHORT order on the pair
                            
                            if (orderqty1 < 0) :
                                trdsymbol1 = nearestexpfuttrdsymbol1
                                
                                # API Call to place the order
                                orderid1 = zerodha.place_order(api_key, access_token, fo_exchange, 'FNO', trdsymbol1, 'SELL', "LIMIT", abs(orderqty1), orderprice1, product, order_duration, order_variety='REGULAR', printerrormessage = True)
                                if (orderid1 == None):
                                    # print("Error occured in placing order for " + spotsymbol + ". Algo stopped by system.")
                                    # stopalgo = True
                                    # break
                                    print("SELL order for " + trdsymbol1 + " could not be placed.")
                                    # VERY IMPORTANT TODO
                                    # check if last order on this leg failed, then place the order on this leg again
                                    errctr = errctr + 1
                                    if (errctr > maxerrcnt):
                                        stopalgo = True
                                    break
                                    
                                if (orderid1 != ''):
                                    print("Order placed successfully. SELL order for " + trdsymbol1 + " qty:" + str(orderqty1) + " @ " + str(orderprice1) + " orderid: " + orderid1)
                                    
                                    # update the status file
                                    st = ss.UpdateStatus(isentrytrade, pairnum, 1, orderqty1, orderprice1, 0, 0, 0, orderid1, 1, current_signal, exitreason, strategy_state, True)
                                    
                                    if (st == False):
                                        print("Error occured in saving status " + trdsymbol1 + ". Algo stopped by system.")
                                        stopalgo = True
                                        break
                                else:
                                    print("SELL order for " + trdsymbol1 + " could not be placed.")
                                    # check if last order on this leg failed, then place the order on this leg again
                                    errctr = errctr + 1
                                    if (errctr > maxerrcnt):
                                        stopalgo = True
                                    break
                                
                            if (orderqty2 > 0) :
                                trdsymbol2 = nearestexpfuttrdsymbol2
                                
                                # API Call to place the order
                                orderid2 = zerodha.place_order(api_key, access_token, fo_exchange, 'FNO', trdsymbol2, 'BUY', "LIMIT", orderqty2, orderprice2, product, order_duration, order_variety='REGULAR', printerrormessage = True)
                                if (orderid2 == None):
                                    # print("Error occured in placing order for " + spotsymbol + ". Algo stopped by system.")
                                    # stopalgo = True
                                    # break
                                    print("BUY order for " + trdsymbol2 + " could not be placed.")
                                    # VERY IMPORTANT TODO
                                    # check if last order on this leg failed, then place the order on this leg again
                                    errctr = errctr + 1
                                    if (errctr > maxerrcnt):
                                        stopalgo = True
                                    break
                                
                                if (orderid2 != ''):
                                    print("Order placed successfully. BUY order for " + trdsymbol2 + " qty:" + str(orderqty2) + " @ " + str(orderprice2) + " orderid: " + orderid2)
                                    
                                    # update the status file
                                    st = ss.UpdateStatus(isentrytrade, pairnum, 2, orderqty2, orderprice2, 0, 0, 0, orderid2, 2, current_signal, exitreason, strategy_state, True)
                                    
                                    if (st == False):
                                        print("Error occured in saving status " + trdsymbol2 + ". Algo stopped by system.")
                                        stopalgo = True
                                        break
                                else:
                                    print("BUY order for " + trdsymbol2 + " could not be placed.")
                                    # check if last order on this leg failed, then place the order on this leg again
                                    errctr = errctr + 1
                                    if (errctr > maxerrcnt):
                                        stopalgo = True
                                    break
                                
                        #else:
                            # no trade was generated, do nothing
                            #pass
                            
                    #else:
                        # no signal was generated, do nothing
                        # pass
                        
                else:
                    # if an order is already pending execution on this stock, 
                    # then check its status and update the status file
                    
                    # VERY IMPORTANT TODO
                    # if one of the legs is completed and the other leg is rejected/cancelled, then
                    # appropriate position reversal is to be done
                    
                    if isentrytrade:
                        # leg 1
                        if (strategy_state.iloc[pairnum, sscol_EntryExecutingLeg1].value == 1):
                            orderid = str(strategy_state.iloc[pairnum, sscol_EntryOrderIDLeg1])
                            trdsymbol = strategy_state.iloc[pairnum, sscol_trdsymbolLeg1]
                            
                            # query / poll the API for the status of this order
                            orderstatus = GetOrderStatus(api_key, access_token, orderid)
                            
                            if (orderstatus == None):
                                # if we dont get a revert from the API on the order status we go to process the next stock
                                continue
                                
                            sgn = strategy_state.iloc[pairnum, sscol_EntrySignalLeg1]
                            
                            # the following code is broker API specific, different brokers would have different
                            # keys and status values
                            
                            # Broker dependent
                            # update the status file with the order status
                            if (orderstatus[col_orderstatusmessage] == 'complete'):
                                st = ss.UpdateStatus(isentrytrade, pairnum, 1, None, None, None, sgn * int(orderstatus['FilledShares']) , orderstatus['AvgPrice'], None, 0, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                            elif (orderstatus[col_orderstatusmessage] == 'cancelled'):
                                st = ss.UpdateStatus(isentrytrade, pairnum, 1, None, None, None, sgn * int(orderstatus['FilledShares']) , orderstatus['AvgPrice'], None, 0, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                            elif (orderstatus[col_orderstatusmessage] == 'rejected'):
                                st = ss.UpdateStatus(isentrytrade, pairnum, 1, None, None, None, 0 , 0, None, 0, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                            elif (orderstatus[col_orderstatusmessage] == 'open'):
                                st = ss.UpdateStatus(isentrytrade, pairnum, 1, None, None, None, sgn * int(orderstatus['FilledShares']) , orderstatus['AvgPrice'], None, 1, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                                
                                # todo
                                # add code for order modification                    
                                
                        # leg 2
                        if (strategy_state.iloc[pairnum, sscol_EntryExecutingLeg2].value == 1):
                            orderid = str(strategy_state.iloc[pairnum, sscol_EntryOrderIDLeg2])
                            trdsymbol = strategy_state.iloc[pairnum, sscol_trdsymbolLeg2]
                            
                            # query / poll the API for the status of this order
                            orderstatus = GetOrderStatus(api_key, access_token, orderid)
                            
                            if (orderstatus == None):
                                # if we dont get a revert from the API on the order status we go to process the next stock
                                continue
                                
                            sgn = strategy_state.iloc[pairnum, sscol_EntrySignalLeg1]
                            
                            # update the status file with the order status
                            if (orderstatus[col_orderstatusmessage] == 'complete'):
                                st = ss.UpdateStatus(isentrytrade, pairnum, 2, None, None, None, sgn * int(orderstatus['FilledShares']) , orderstatus['AvgPrice'], None, 0, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                            elif (orderstatus[col_orderstatusmessage] == 'cancelled'):
                                st = ss.UpdateStatus(isentrytrade, pairnum, 2, None, None, None, sgn * int(orderstatus['FilledShares']) , orderstatus['AvgPrice'], None, 0, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                            elif (orderstatus[col_orderstatusmessage] == 'rejected'):
                                st = ss.UpdateStatus(isentrytrade, pairnum, 2, None, None, None, 0 , 0, None, 0, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                            elif (orderstatus[col_orderstatusmessage] == 'open'):
                                st = ss.UpdateStatus(isentrytrade, pairnum, 2, None, None, None, sgn * int(orderstatus['FilledShares']) , orderstatus['AvgPrice'], None, 1, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                                
                                # todo
                                # add code for order modification                    
                                
                    else:
                        # EXIT TRADE
                        
                        # todo exit position code
                        
                        # leg 1
                        if (strategy_state.iloc[pairnum, sscol_ExitExecutingLeg1].value == 1):
                            orderid = str(strategy_state.iloc[pairnum, sscol_ExitOrderIDLeg1])
                            trdsymbol = strategy_state.iloc[pairnum, sscol_trdsymbolLeg1]
                            
                            # query / poll the API for the status of this order
                            orderstatus = GetOrderStatus(api_key, access_token, orderid)
                            
                            if (orderstatus == None):
                                # if we dont get a revert from the API on the order status we go to process the next stock
                                continue
                                
                            sgn = -strategy_state.iloc[pairnum, sscol_EntrySignalLeg1]
                            
                            # update the status file with the order status
                            # the message constants are broker dependent
                            if (orderstatus[col_orderstatusmessage] == 'complete'):
                                st = ss.UpdateStatus(isentrytrade, pairnum, 1, None, None, None, sgn * int(orderstatus['FilledShares']) , orderstatus['AvgPrice'], None, 0, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                            elif (orderstatus[col_orderstatusmessage] == 'cancelled'):
                                st = ss.UpdateStatus(isentrytrade, pairnum, 1, None, None, None, sgn * int(orderstatus['FilledShares']) , orderstatus['AvgPrice'], None, 0, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                            elif (orderstatus[col_orderstatusmessage] == 'rejected'):
                                st = ss.UpdateStatus(isentrytrade, pairnum, 1, None, None, None, 0 , 0, None, 0, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                            elif (orderstatus[col_orderstatusmessage] == 'open'):
                                st = ss.updatestatusfile(isentrytrade, pairnum, 1, None, None, None, sgn * int(orderstatus['FilledShares']) , orderstatus['AvgPrice'], None, 1, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                                
                                # todo
                                # add code for order modification                    
                                
                        # leg 2
                        if (strategy_state.iloc[pairnum, sscol_ExitExecutingLeg2].value == 1):
                            orderid = str(strategy_state.iloc[pairnum, sscol_ExitOrderIDLeg2])
                            trdsymbol = strategy_state.iloc[pairnum, sscol_trdsymbolLeg2]
                            
                            # query / poll the API for the status of this order
                            orderstatus = GetOrderStatus(api_key, access_token, orderid)
                            
                            if (orderstatus == None):
                                # if we dont get a revert from the API on the order status we go to process the next stock
                                continue
                                
                            sgn = -strategy_state.iloc[pairnum, sscol_EntrySignalLeg1]
                            
                            # update the status file with the order status
                            if (orderstatus[col_orderstatusmessage] == 'complete'):
                                st = ss.UpdateStatus(isentrytrade, pairnum, 2, None, None, None, sgn * int(orderstatus['FilledShares']) , orderstatus['AvgPrice'], None, 0, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                            elif (orderstatus[col_orderstatusmessage] == 'cancelled'):
                                st = ss.UpdateStatus(isentrytrade, pairnum, 2, None, None, None, sgn * int(orderstatus['FilledShares']) , orderstatus['AvgPrice'], None, 0, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                            elif (orderstatus[col_orderstatusmessage] == 'rejected'):
                                st = ss.UpdateStatus(isentrytrade, pairnum, 2, None, None, None, 0 , 0, None, 0, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                            elif (orderstatus[col_orderstatusmessage] == 'open'):
                                st = ss.UpdateStatus(isentrytrade, pairnum, 2, None, None, None, sgn * int(orderstatus['FilledShares']) , orderstatus['AvgPrice'], None, 1, None, exitreason, strategy_state, False)
                                
                                if (st == False):
                                    print("Error occured in saving status " + trdsymbol + ". Algo stopped by system.")
                                    stopalgo = True
                                    break
                                
                                # todo
                                # add code for order modification                    
            
                # if there is a hard stop on the algo, we exit the inner for loop
                if (stopalgo == True):
                    print('Some error has forced the algo to stop\n')
                    break
                
            # end of the for loop through the scanlist 
            # goto process the next stock pair
            
            # write the strategy state file to disk
            ss.SaveStatus(StrategyStateFile, strategy_state)
            
            print('Scan completed\n')
            
            # if there is a hard stop on the algo, we exit the outer while loop
            if (stopalgo == True):
                print('Some error has forced the algo to stop\n')
                break
            
            print('Waiting for next scan\n')
            time.sleep(scan_frequency * 60)
            
            
        # end of the while loop running the scan through the day  
        # we stop for the day
        
        print('Algo stopped for the day')
    
    except Exception as ex:
        print(sys._getframe().f_code.co_name, 'exception: ', ex)
        
Scanner()


        
