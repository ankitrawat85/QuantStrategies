# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 12:29:35 2023

@author: User1
"""

import sys
import myutils


# contants for status file

sscol_symbol = 0
sscol_trdsymbol = 1
sscol_symbolname = 2
sscol_entry_orderqty = 3
sscol_entry_orderprice = 4
sscol_entry_modifiedprice = 5
sscol_entry_filledqty = 6
sscol_entry_balanceqty = 7
sscol_entry_price = 8
sscol_entry_orderid = 9
sscol_entry_executing = 10
sscol_entry_signal = 11

sscol_exit_orderqty = 12
sscol_exit_orderprice = 13
sscol_exit_modifiedprice = 14
sscol_exit_filledqty = 15
sscol_exit_balanceqty = 16
sscol_exit_price = 17
sscol_exit_orderid = 18
sscol_exit_executing = 19
sscol_exit_reason = 20


def UpdateStatus(dfStrategyStatus, stocknum, isentrytrade, orderqty, orderprice, modifiedprice, filledqty, tradeprice, orderid, 
                 isorderexecuting, signal, exitreason, isneworder = True):
    
    try:
        # todo the parameter validations
#        if (dfStrategyStatus == None):
#            return False
        
        
        if (isentrytrade):
            # entry side status
            if (isneworder):
                dfStrategyStatus.iloc[stocknum, sscol_entry_orderqty] = orderqty
                dfStrategyStatus.iloc[stocknum, sscol_entry_orderprice] = orderprice
                dfStrategyStatus.iloc[stocknum, sscol_entry_orderid] = orderid
                dfStrategyStatus.iloc[stocknum, sscol_entry_signal] = signal
            else:
                dfStrategyStatus.iloc[stocknum, sscol_entry_modifiedprice] = modifiedprice
            
            dfStrategyStatus.iloc[stocknum, sscol_entry_filledqty] = filledqty
            dfStrategyStatus.iloc[stocknum, sscol_entry_balanceqty] = orderqty - filledqty
            dfStrategyStatus.iloc[stocknum, sscol_entry_price] = tradeprice
            dfStrategyStatus.iloc[stocknum, sscol_entry_executing] = isorderexecuting
            
        else:
            # exit side status
            if (isneworder):
                dfStrategyStatus.iloc[stocknum, sscol_exit_orderqty] = orderqty
                dfStrategyStatus.iloc[stocknum, sscol_exit_orderprice] = orderprice
                dfStrategyStatus.iloc[stocknum, sscol_exit_orderid] = orderid
                dfStrategyStatus.iloc[stocknum, sscol_exit_reason] = exitreason
            else:
                dfStrategyStatus.iloc[stocknum, sscol_exit_modifiedprice] = modifiedprice
            
            dfStrategyStatus.iloc[stocknum, sscol_exit_filledqty] = filledqty
            dfStrategyStatus.iloc[stocknum, sscol_exit_balanceqty] = orderqty - filledqty
            dfStrategyStatus.iloc[stocknum, sscol_exit_price] = tradeprice
            dfStrategyStatus.iloc[stocknum, sscol_exit_executing] = isorderexecuting
        
        return True
    except Exception as errmsg:
        print(errmsg)
        return False
    

def GetStrategyStatus(strategyfilename):
    return myutils.read_dataframe(strategyfilename)

def GetOrderExecutionStatus(dfStrategyStatus, stocknum):
    try:
        if ((dfStrategyStatus.iloc[stocknum, sscol_entry_executing] == 1) | (dfStrategyStatus.iloc[stocknum, sscol_exit_executing] == 1)):
            return True
        else:
            return False
    except Exception as errmsg:
        print(errmsg)
        return None

def GetOrderID(dfStrategyStatus, stocknum, isentrytrade):
    try:
        if isentrytrade:
            return dfStrategyStatus.iloc[stocknum, sscol_entry_orderid]
        else:
            return dfStrategyStatus.iloc[stocknum, sscol_exit_orderid]
    except Exception as errmsg:
        print(errmsg)
        return None

def GetOrderQty(dfStrategyStatus, stocknum, isentrytrade):
    try:
        if isentrytrade:
            return dfStrategyStatus.iloc[stocknum, sscol_entry_orderqty]
        else:
            return dfStrategyStatus.iloc[stocknum, sscol_exit_orderqty]
    except Exception as errmsg:
        print(errmsg)
        return None
    
def IsEntryTrade(dfStrategyStatus, stocknum):
    try:
        if (dfStrategyStatus.iloc[stocknum, sscol_entry_executing] == 1):
            return True
        elif (dfStrategyStatus.iloc[stocknum, sscol_exit_executing] == 1):
            return False
        else:
            return None
    except Exception as errmsg:
        print(errmsg)
        return None
    
def GetPosition(dfStrategyStatus, stocknum):
    try:
        return dfStrategyStatus.iloc[stocknum, sscol_entry_filledqty] + dfStrategyStatus.iloc[stocknum, sscol_exit_filledqty]
    except Exception as errmsg:
        print(errmsg)
        return None

def GetEntryPrice(dfStrategyStatus, stocknum):
    try:
        return dfStrategyStatus.iloc[stocknum, sscol_entry_price]
    except Exception as errmsg:
        print(errmsg)
        return None

def GetEntrySignal(dfStrategyStatus, stocknum):
    try:
        return dfStrategyStatus.iloc[stocknum, sscol_entry_signal]
    except Exception as errmsg:
        print(errmsg)
        return None
            
            
            