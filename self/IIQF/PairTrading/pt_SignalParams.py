
import myutils


def GetSignalPara_PairsTrading(SignalParaFile):
    try:
        data = myutils.read_dataframe(SignalParaFile)
        
        if (len(data) == 0):
            return None, None, None, None, None, None, None, None
        
        short_window = data['ShortWindow'][0]
        long_window = data['LongWindow'][0]
        long_entry = data['LongEntry'][0]
        long_exit = data['LongExit'][0]
        long_stoploss = data['LongStopLoss'][0]
        short_entry = data['ShortEntry'][0]
        short_exit = data['ShortExit'][0]
        short_stoploss = data['ShortStopLoss'][0]

        return int(short_window), int(long_window), float(long_entry), float(long_exit), float(long_stoploss), float(short_entry), float(short_exit), float(short_stoploss) 
    
    except:
        print("error")
        return None, None, None, None, None, None, None, None
    
    