import pandas as pd
from pynse import *
from nsepy import get_history
import numpy as np
import datetime as dt
import datetime
import pandas as pd
from datetime import date

import numpy as np
desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',20)
pd.set_option('display.max_rows',300)
nse=Nse()
class nseRealTime():

       def stock(self,ticker):
              return pd.DataFrame(nse.get_quote(ticker))


       def Future(self,ticker,segment,expiry):
              dataframe_ = nse.get_quote(ticker, segment=segment, expiry=expiry)
              data_ = {}
              for key, values in dataframe_.items():
                     data_[key] = [values]
              return pd.DataFrame(data_)



       def SpecificStrikeOption(self,ticker,segment,optionType,strike):
                     dataframe_ = nse.get_quote(ticker, segment=segment, optionType=optionType, strike=strike)
                     data_ = {}
                     for key,values in dataframe_.items():
                            data_[key] = [values]
                     return pd.DataFrame(data_)


       def OptionChain(self,ticker,instrument,option_expiry):
              ns_  = nse.get_quote(ticker,Segment.OPT,option_expiry)
              df_ = nse.option_chain(ticker,option_expiry)
              Call_ = df_.copy(deep=True)
              Put_ = df_.copy(deep=True)
              list_CE = [col for col in df_.columns if col.startswith('CE')]
              list_PE = [col for col in df_.columns if col.startswith('PE')]
              Call_ = Call_[list_CE]
              Put_ = Put_[list_PE]
              print("CE--")
              print("--------------------------")
              for i in Call_.columns:
                     Call_.rename( columns= {i: str(i).replace("CE.","")},inplace = True)

              for i in Put_.columns:
                     Put_.rename( columns= {i: str(i).replace("PE.","")},inplace = True)

              Put_["Symbol"] = ticker
              Put_["INSTRUMENT"] = instrument
              Put_["Close"] =  (Put_["bidprice"] + Put_["askPrice"])/2
              Put_["Option Type"] = "PE"

              Call_["Symbol"] = ticker
              Call_["INSTRUMENT"] = instrument
              Call_["Close"] =  (Call_["bidprice"] + Call_["askPrice"])/2
              Call_["Option Type"] = "CE"
              #Call_ = Call_[["Symbol","Close","Option Type","Expiry","Strike Price","Future_Prices","OPEN_INT","lib_impliedVolatility"]]
              #Put_ = Put_[["Symbol","Close","Option Type","Expiry","Strike Price","Future_Prices","OPEN_INT","lib_impliedVolatility"]]
              df_callPut = pd.concat([Put_, Call_])
              from datetime import datetime
              dateTimeObj = datetime.now()
              today = dateTimeObj.strftime("%d-%m-%Y %H:%M:%S")
              print("Date_ {}".format(today))
              df_callPut["Date"] = today
              df_callPut["Date"] = pd.to_datetime(df_callPut["Date"])
              #df_callPut["Date"] = today.strftime("%d-%m-%Y")
              #df_callPut["Date"] = pd.to_datetime(df_callPut["Date"])
              df_callPut = df_callPut.rename(
                     columns={"expiryDate": "Expiry", "strikePrice": "Strike Price", "underlyingValue": "Future_Prices",
                              "openInterest": "OPEN_INT", "impliedVolatility": "lib_impliedVolatility"})

              return df_callPut

if __name__ == "__main__":

       ''' Stock Real time data'''
       print("Stock Real Time Data ")
       stock_ = nseRealTime().stock("INFY")
       stock_ = pd.DataFrame.from_dict(stock_)
       stock_ = stock_.reset_index()
       print(stock_)


       '''Options Real Time Data'''
       print("Real Time Data of specific Strike Price Option")
       SpecificStrikeOption = nseRealTime().SpecificStrikeOption('INFY',segment=Segment.OPT, optionType=OptionType.PE, strike=1800)
       print(SpecificStrikeOption)


       '''Option Chain  Real time data '''
       print("ption Chain  Real time data of specific expiry")
       RealTimeOption = nseRealTime().OptionChain("NIFTY",option_expiry=datetime.date(2021, 12, 30),instrument="OPIDX")
       print("RealTimeOption")
       print(RealTimeOption.columns)
       RealTimeOption = RealTimeOption[RealTimeOption["OPEN_INT"] != 0]
       print(RealTimeOption )
       RealTimeOption.to_csv("realtimeData2.csv")


       '''Future Real Time Data'''
       print("Future Real Time Data")
       Future_ = nseRealTime().Future('INFY', segment=Segment.FUT, expiry=dt.date(2021,12,30))
       print(pd.DataFrame.from_dict(Future_))
