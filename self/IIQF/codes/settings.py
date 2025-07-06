
import myutils

def GetAPIPara():
    try:
        # todo some more API para to add
        data = myutils.read_dataframe('Settings.csv')
        
        if (len(data) == 0):
            return None, None, None, None, None, None
        
        userid = data['UserID'][0]
        password = data['Password'][0]
        api_key = data['APIKey'][0]
        api_secret = data['APISecret'][0]
        request_token = data['RequestToken'][0]
        acountid = data['AccountID'][0]
        
        return userid, password, api_key, api_secret, request_token, acountid
    
    except Exception as errmsg:
        print(errmsg)
        return None, None, None, None, None, None, None

def GetTradePara():
    try:
        data = myutils.read_dataframe('Settings.csv')
        
        if (len(data) == 0):
            return None, None, None, None, None, None
        
        capital_allocated = data['Capital'][0]
        max_capital_to_deploy = data['MaxDeploy'][0]
        buy_margin = data['BuyMargin'][0]
        sell_margin = data['SellMargin'][0]
        target = data['PLTarget'][0]
        stoploss = data['PLStoploss'][0]
#        trading_cost = data['TradingCost'][0]

        return float(capital_allocated), float(max_capital_to_deploy), float(buy_margin), float(sell_margin), float(target), float(stoploss)
    
    except Exception as errmsg:
        print(errmsg)
        return None, None, None, None, None, None
    
    
def GetSignalPara_RSI():
    try:
        data = myutils.read_dataframe('Settings.csv')
        
        if (len(data) == 0):
            return None, None, None
        
        period = data['RSIPeriod'][0]
        long_entry = data['RSILongEntry'][0]
        short_entry = data['RSIShortEntry'][0]
        
        return int(period), int(long_entry), int(short_entry) 
    
    except Exception as errmsg:
        print(errmsg)
        return None, None, None

    
def GetSignalPara_MACD():
    try:
        data = myutils.read_dataframe('Settings.csv')
        
        if (len(data) == 0):
            return None, None, None, None
        
        short_period = data['MACDShortPeriod'][0]
        long_period = data['MACDLongPeriod'][0]
        long_entry = data['MACDLongEntry'][0]
        short_entry = data['MACDShortEntry'][0]
        
        return int(short_period), int(long_period), int(long_entry), int(short_entry) 
        
    except Exception as errmsg:
        print(errmsg)
        return None, None, None, None
    
def GetSignalPara_MACDHistogram():
    try:
        data = myutils.read_dataframe('Settings.csv')
        
        if (len(data) == 0):
            return None, None, None, None, None
        
        short_period = data['MACDShortPeriod'][0]
        long_period = data['MACDLongPeriod'][0]
        signal_period = data['MACDSignalPeriod'][0]
        long_entry = data['MACDLongEntry'][0]
        short_entry = data['MACDShortEntry'][0]
        
        return int(short_period), int(long_period), int(signal_period), int(long_entry), int(short_entry) 
        
    except Exception as errmsg:
        print(errmsg)
        return None, None, None, None, None
