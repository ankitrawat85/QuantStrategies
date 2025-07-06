
import myutils


def GetTradePara(TradeParaFile):
    try:
        data = myutils.read_dataframe(TradeParaFile)
        
        if (len(data) == 0):
            return None, None, None, None, None, None, None
        
        capital_allocated = data['CapitalAllocated'][0]
        max_capital_to_deploy = data['MaxCapitalToDeploy'][0]
        buy_margin = data['BuyMargin'][0]
        sell_margin = data['SellMargin'][0]
        target = data['Target'][0]
        stoploss = data['StopLoss'][0]
        trading_cost = data['TradingCost'][0]
        
        return float(capital_allocated), float(max_capital_to_deploy), float(buy_margin), float(sell_margin), float(target), float(stoploss), float(trading_cost) 
    
    except:
        print("error")
        return None, None, None, None, None, None, None

