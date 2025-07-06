# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 08:44:04 2023

@author: User1
"""

import myutils

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


def UpdateStatus(isentrytrade, stocknum, leg, orderqty, orderprice, modifiedprice, filledqty, tradeprice, orderid, isorderexecuting, signal, exitreason, strategy_state, neworder = True):
    # todo
    # reset the row after exit
    
    try:

        if isentrytrade:
            # entry trade
            if neworder:
                if (leg == 1):
                    strategy_state.iloc[stocknum, sscol_EntryOrderQtyLeg1] = orderqty
                    strategy_state.iloc[stocknum, sscol_EntryOrderPriceLeg1] = orderprice
                    strategy_state.iloc[stocknum, sscol_EntryOrderIDLeg1] = orderid
                    strategy_state.iloc[stocknum, sscol_EntrySignalLeg1] = signal
                else:
                    strategy_state.iloc[stocknum, sscol_EntryOrderQtyLeg2] = orderqty
                    strategy_state.iloc[stocknum, sscol_EntryOrderPriceLeg2] = orderprice
                    strategy_state.iloc[stocknum, sscol_EntryOrderIDLeg2] = orderid
            
            if (leg == 1):
                strategy_state.iloc[stocknum, sscol_EntryModifiedPriceLeg1] = modifiedprice
                strategy_state.iloc[stocknum, sscol_EntryFilledQtyLeg1] = filledqty
                strategy_state.iloc[stocknum, sscol_EntryBalanceQtyLeg1] = orderqty - filledqty
                strategy_state.iloc[stocknum, sscol_EntryPriceLeg1] = tradeprice
                strategy_state.iloc[stocknum, sscol_EntryExecutingLeg1] = isorderexecuting
            else:
                strategy_state.iloc[stocknum, sscol_EntryModifiedPriceLeg2] = modifiedprice
                strategy_state.iloc[stocknum, sscol_EntryFilledQtyLeg2] = filledqty
                strategy_state.iloc[stocknum, sscol_EntryBalanceQtyLeg2] = orderqty - filledqty
                strategy_state.iloc[stocknum, sscol_EntryPriceLeg2] = tradeprice
                strategy_state.iloc[stocknum, sscol_EntryExecutingLeg2] = isorderexecuting
        else:
            # exit trade
            if neworder:
                if (leg == 1):
                    strategy_state.iloc[stocknum, sscol_ExitOrderQtyLeg1] = orderqty
                    strategy_state.iloc[stocknum, sscol_ExitOrderPriceLeg1] = orderprice
                    strategy_state.iloc[stocknum, sscol_ExitOrderIDLeg1] = orderid
                else:
                    strategy_state.iloc[stocknum, sscol_ExitOrderQtyLeg2] = orderqty
                    strategy_state.iloc[stocknum, sscol_ExitOrderPriceLeg2] = orderprice
                    strategy_state.iloc[stocknum, sscol_ExitOrderIDLeg2] = orderid
            
            if (leg == 1):
                strategy_state.iloc[stocknum, sscol_ExitModifiedPriceLeg1] = modifiedprice
                strategy_state.iloc[stocknum, sscol_ExitFilledQtyLeg1] = filledqty
                strategy_state.iloc[stocknum, sscol_ExitBalanceQtyLeg1] = orderqty - filledqty
                strategy_state.iloc[stocknum, sscol_ExitPriceLeg1] = tradeprice
                strategy_state.iloc[stocknum, sscol_ExitExecutingLeg1] = isorderexecuting
            else:
                strategy_state.iloc[stocknum, sscol_ExitModifiedPriceLeg2] = modifiedprice
                strategy_state.iloc[stocknum, sscol_ExitFilledQtyLeg2] = filledqty
                strategy_state.iloc[stocknum, sscol_ExitBalanceQtyLeg2] = orderqty - filledqty
                strategy_state.iloc[stocknum, sscol_ExitPriceLeg2] = tradeprice
                strategy_state.iloc[stocknum, sscol_ExitExecutingLeg2] = isorderexecuting

        return True
    except:
        return False

def ReadStrategyStatusFile(strategyfilename):
    return myutils.read_dataframe(strategyfilename)

def IsOrderExecuting(strategy_state, pairnum):
    try:
        s = strategy_state.iloc[pairnum, sscol_EntryExecutingLeg1] + strategy_state.iloc[pairnum, sscol_ExitExecutingLeg1] + strategy_state.iloc[pairnum, sscol_EntryExecutingLeg2] + strategy_state.iloc[pairnum, sscol_ExitExecutingLeg2]
        
        if (s != 0):
            return True
        else:
            return False
    except Exception as errmsg:
        print(errmsg)
        return None


def GetPosition(strategy_state, pairnum, legnum):
    try:
        if legnum == 1:
            pos = strategy_state.iloc[pairnum, sscol_EntryFilledQtyLeg1] + strategy_state.iloc[pairnum, sscol_ExitFilledQtyLeg1]
        else:
            pos = strategy_state.iloc[pairnum, sscol_EntryFilledQtyLeg2] + strategy_state.iloc[pairnum, sscol_ExitFilledQtyLeg2]
        
        return pos
    except:
      return None

def GetEntryPrice(strategy_state, pairnum, legnum):
    try:
        if legnum == 1:
            price = strategy_state.iloc[pairnum, sscol_EntryPriceLeg1] 
        else:
            price = strategy_state.iloc[pairnum, sscol_EntryPriceLeg2] 
        
        return price
    except:
      return None

def GetPreviousSignal(strategy_state, pairnum):
    try:
        return strategy_state.iloc[pairnum, sscol_EntrySignalLeg1]        
    except:
      return None

def GetPreviousExitReason(strategy_state, pairnum):
    try:
        return strategy_state.iloc[pairnum, sscol_ExitReasonLeg1]       
    except:
      return None

def SaveStatus(strategyfilename, strategy_state):
    try:
        myutils.write_dataframe(strategyfilename, strategy_state)
    except:
      return None


