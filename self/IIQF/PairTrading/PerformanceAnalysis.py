# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 10:27:26 2020

@author: User1
"""
# todo sterling ratio

import numpy as np

def calculate_maxdraw_down(init_capital, pnls, fixedcapital = False):
    no_of_rets = len(pnls)
    
    if (no_of_rets < 2):
        return 0
    
    if (fixedcapital):
        cumul_ret = pnls / init_capital
        for i in range(1, no_of_rets):
            cumul_ret[i] = (1 + cumul_ret[i-1]) * (1 + cumul_ret[i]) - 1
    else:
        cumul_ret = np.cumsum(pnls)
        cumul_ret = cumul_ret / init_capital
    
    high_watermark = cumul_ret[0]
    max_dd = 0.0
    
    for i in range(no_of_rets):
        if (cumul_ret[i] > high_watermark):
            high_watermark = cumul_ret[i]
        
        dd = (cumul_ret[i] + 1) / (high_watermark + 1) - 1
        
        if (dd < max_dd):
            max_dd = dd
    
    return max_dd


def all_performance_statistics(init_capital, pnls, riskfree_rate, totaltimeyears, fixedcapital = False, mindatapoints = 5):
    # note that if we call this function with trade-wise PL we get trade-wise stats
    # and if we call this function with MTM PL we get MTM stats and hence the 
    # word "trade" must be interpreted accordingly as per MTM period
    
    if (init_capital <= 0 or len(pnls) < mindatapoints or mindatapoints < 2 ):
        return 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    
    if (fixedcapital):
        ret = pnls / init_capital
        cumul_ret = pnls / init_capital
        for i in range(1, len(pnls)):
            cumul_ret[i] = (1 + cumul_ret[i-1]) * (1 + cumul_ret[i]) - 1
    else:
        cumul_pnls = np.cumsum(pnls)
        cumul_ret = cumul_pnls / init_capital
        capital = init_capital + cumul_pnls
        capital = np.append(init_capital, capital)
        ret = pnls / capital[0:-1]

    profit_trades = ret[ret > 0]
    no_of_profit_trades = len(profit_trades)
    
    if (no_of_profit_trades > 0):
        max_profit_per_trade = max(profit_trades)
        avg_profit_per_trade = profit_trades.mean()
    else:
        max_profit_per_trade = 0.0
        avg_profit_per_trade = 0.0
    

    loss_trades = ret[ret < 0]
    no_of_loss_trades = len(loss_trades)
    
    if (no_of_loss_trades > 0):
        max_loss_per_trade = max(loss_trades)
        avg_loss_per_trade = loss_trades.mean()
    else:
        max_loss_per_trade = 0.0
        avg_loss_per_trade = 0.0
    
    

    no_of_trades = len(ret)
    sum_of_ret = sum(ret)
    avg_ret_per_trade = sum_of_ret / no_of_trades
    
    hit_ratio = (no_of_trades - no_of_loss_trades) / no_of_trades
    
    max_draw_down = calculate_maxdraw_down(init_capital, pnls, fixedcapital)
    
    sdret = ret.std()
    
    # Sharpe Ratio
    if (sdret > 0):
        sharpe_ratio = (avg_ret_per_trade - riskfree_rate) / sdret
    else:
        if (avg_ret_per_trade > 0):
            sharpe_ratio = 1000000.0
        elif (avg_ret_per_trade < 0):
            sharpe_ratio = -1000000.0
        else:
            sharpe_ratio = 0.0
    
    cagr = ((1 + cumul_ret) ** (1 / totaltimeyears)) -1
    
    # CALMAR Ratio
    # special case of the MAR ratio ... last 36 periods
    if (abs(max_draw_down) > 0):
        calmar_ratio = cagr / abs(max_draw_down)
    else:
        calmar_ratio = 0
#        if (cagr > 0):
#            calmar_ratio = 1000000.0
#        elif (cagr < 0):
#            calmar_ratio = -1000000.0
#        else:
#            calmar_ratio = 0.0
    
    # Sterling ratio
    #sterling_ratio = (avg_ret_per_trade - riskfree_rate) / avg_drawdown
    
    consecutiveloss_ctr = 0
    maxconsecutiveloss_ctr = 0
    
    for i in range(no_of_trades):
        if (ret[i] >= 0):
            consecutiveloss_ctr = 0
        else:
            consecutiveloss_ctr += 1
            if (consecutiveloss_ctr > maxconsecutiveloss_ctr):
                maxconsecutiveloss_ctr =  consecutiveloss_ctr
    
    
    
    return no_of_trades, no_of_profit_trades, no_of_loss_trades, max_draw_down, hit_ratio, avg_ret_per_trade, \
            avg_profit_per_trade, avg_loss_per_trade, max_profit_per_trade, max_loss_per_trade, \
            maxconsecutiveloss_ctr, sdret, sharpe_ratio, calmar_ratio
            


def performance_statistic(statistic, init_capital, pnls, riskfree_rate, totaltimeyears, fixedcapital = False, mindatapoints = 5):
    
    if (init_capital <= 0 or len(pnls) < mindatapoints or mindatapoints < 2 ):
        return 0
    
    if (fixedcapital):
        ret = pnls / init_capital
        cumul_ret = pnls / init_capital
        for i in range(1, len(pnls)):
            cumul_ret[i] = (1 + cumul_ret[i-1]) * (1 + cumul_ret[i]) - 1
    else:
        cumul_pnls = np.cumsum(pnls)
        cumul_ret = cumul_pnls / init_capital
        capital = init_capital + cumul_pnls
        capital = np.append(init_capital, capital)
        ret = pnls / capital[0:-1]
    
    
    if (statistic == 'NoOfProfitTrades'):    
        profit_trades = ret[ret > 0]
        no_of_profit_trades = len(profit_trades)
        return no_of_profit_trades
    
    
    if (statistic == 'MaxProfitPerTrades'):    
        profit_trades = ret[ret > 0]
        no_of_profit_trades = len(profit_trades)
        if (no_of_profit_trades > 0):
            max_profit_per_trade = max(profit_trades)
        else:
            max_profit_per_trade = 0.0
        return max_profit_per_trade
    
    
    if (statistic == 'AvgProfitPerTrades'):    
        profit_trades = ret[ret > 0]
        no_of_profit_trades = len(profit_trades)
        if (no_of_profit_trades > 0):
            avg_profit_per_trade = profit_trades.mean()
        else:
            avg_profit_per_trade = 0.0
        return avg_profit_per_trade
    

    
    if (statistic == 'NoOfLossTrades'):    
        loss_trades = ret[ret < 0]
        no_of_loss_trades = len(loss_trades)
        return no_of_loss_trades
    
    if (statistic == 'MaxLossPerTrades'):    
        loss_trades = ret[ret < 0]
        no_of_loss_trades = len(loss_trades)
        if (no_of_loss_trades > 0):
            max_loss_per_trade = max(loss_trades)
        else:
            max_loss_per_trade = 0.0
        return max_loss_per_trade
    
    if (statistic == 'AvgLossPerTrades'):    
        profit_trades = ret[ret > 0]
        no_of_profit_trades = len(profit_trades)
        if (no_of_profit_trades > 0):
            avg_loss_per_trade = loss_trades.mean()
        else:
            avg_loss_per_trade = 0.0
        return avg_loss_per_trade    
    
    
    if (statistic == 'AvgReturnPerTrades'):    
        no_of_trades = len(ret)
        sum_of_ret = sum(ret)
        avg_ret_per_trade = sum_of_ret / no_of_trades
        return avg_ret_per_trade
    
    if (statistic == 'HitRatio'):
        no_of_trades = len(ret)
        loss_trades = ret[ret < 0]
        no_of_loss_trades = len(loss_trades)
        hit_ratio = (no_of_trades - no_of_loss_trades) / no_of_trades
        return hit_ratio
    
    
    if (statistic == 'MaxDrawDown'):
        max_draw_down = calculate_maxdraw_down(init_capital, pnls, fixedcapital)
        return max_draw_down

#    if (statistic == 'SterlingRatio'):
#        no_of_trades = len(ret)
#        sum_of_ret = sum(ret)
#        avg_ret_per_trade = sum_of_ret / no_of_trades
#        max_draw_down, avg_drawdown = calculate_maxdraw_down(init_capital, pnls, fixedcapital)
#        sterling_ratio = (avg_ret_per_trade - riskfree_rate) / avg_drawdown
#        return sterling_ratio

        # Sharpe Ratio
    if (statistic == 'SharpeRatio'):
        no_of_trades = len(ret)
        sum_of_ret = sum(ret)
        avg_ret_per_trade = sum_of_ret / no_of_trades
        sdret = ret.std()
        
        if (sdret > 0):
            sharpe_ratio = (avg_ret_per_trade - riskfree_rate) / sdret
        else:
            if (avg_ret_per_trade > 0):
                sharpe_ratio = 1000000.0
            elif (avg_ret_per_trade < 0):
                sharpe_ratio = -1000000.0
            else:
                sharpe_ratio = 0.0
        return sharpe_ratio


    if (statistic == 'CAGR'):
        cagr = ((1 + cumul_ret) ** (1 / totaltimeyears)) -1
        return cagr
    
    if (statistic == 'CalmarRatio'):
        # CALMAR Ratio
        # special case of the MAR ratio ... last 36 periods
        cagr = ((1 + cumul_ret) ** (1 / totaltimeyears)) -1
        max_draw_down = calculate_maxdraw_down(init_capital, pnls, fixedcapital)
        if (abs(max_draw_down) > 0):
            calmar_ratio = cagr / abs(max_draw_down)
        else:
            if (cagr > 0):
                calmar_ratio = 1000000.0
            elif (cagr < 0):
                calmar_ratio = -1000000.0
            else:
                calmar_ratio = 0.0
        return calmar_ratio
    
    
    if (statistic == 'MaxConsecutiveLoss'):
        no_of_trades = len(ret)
        consecutiveloss_ctr = 0
        maxconsecutiveloss_ctr = 0
        
        for i in range(no_of_trades):
            if (ret[i] >= 0):
                consecutiveloss_ctr = 0
            else:
                consecutiveloss_ctr += 1
                if (consecutiveloss_ctr > maxconsecutiveloss_ctr):
                    maxconsecutiveloss_ctr =  consecutiveloss_ctr
    
        return maxconsecutiveloss_ctr
    



