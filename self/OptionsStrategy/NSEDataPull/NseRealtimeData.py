import pandas as pd
from pynse import *
from nsepy import get_history
from datetime import date
import numpy as np
import datetime as dt
from datetime import date
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
              return nse.get_quote(ticker, segment=segment, expiry=expiry)



       def Option(self,ticker,segment,optionType,strike):
              return nse.get_quote(ticker, segment=segment, optionType=optionType, strike=strike)


       def OptionChain(self,ticker,option_expiry):
              ns_  = nse.get_quote(ticker,Segment.OPT,option_expiry)
              df_ = nse.option_chain(ticker,option_expiry)
              print(df_)
              #df_ = nse.option_chain(index,datetime.date(2021, 12, 30))
              Call_ = df_
              Call_["Symbol"] = ticker
              Call_["INSTRUMENT"] = "OPTIDX"
              Call_["Close"] =  (Call_["CE.bidprice"] + Call_["CE.askPrice"])/2
              Call_["Option Type"] = "CE"
              print(Call_.columns)
              Call_ = Call_.rename(columns={"expiryDate":"Expiry","CE.strikePrice":"Strike Price","CE.underlyingValue":"Future_Prices","PE.changeinOpenInterest":"OPEN_INT","CE.impliedVolatility":"lib_impliedVolatility"})
              Call_ = Call_[["Symbol","Close","Option Type","Expiry","Strike Price","Future_Prices","OPEN_INT","lib_impliedVolatility"]]
              Put_ = df_
              Put_["Symbol"] = ticker
              Put_["INSTRUMENT"] = "OPTIDX"
              Put_["Close"] =  (Put_["PE.bidprice"] + Put_["PE.askPrice"])/2
              Put_["Option Type"] = "PE"
              Put_ = Put_.rename(columns={"expiryDate":"Expiry","CE.strikePrice":"Strike Price","CE.underlyingValue":"Future_Prices","PE.changeinOpenInterest":"OPEN_INT","PE.impliedVolatility":"lib_impliedVolatility"})
              Put_ = Put_[["Symbol","Close","Option Type","Expiry","Strike Price","Future_Prices","OPEN_INT","lib_impliedVolatility"]]
              df = pd.concat([Put_, Call_])
              today = date.today()
              df = pd.concat([Put_,Call_])
              df["Date"] = today.strftime("%d-%m-%Y")
              df["Date"] = pd.to_datetime(df["Date"])
              return df

if __name__ == "__main__":

       ## Stock Real time data

       stock_ = nseRealTime().stock("INFY")
       stock_ = pd.DataFrame.from_dict(stock_)
       print(stock_.columns)
       print(stock_[["open","close","lastPrice"]])
       '''
       ## Options Real Time Data
       opt_ = nseRealTime().Option('INFY',segment=Segment.OPT, optionType=OptionType.PE, strike=1800.)
       print((opt_))
       print("convert to dataframe ")
       print(pd.DataFrame.from_dict(opt_))

       ##  Future Real Time Data
       Future_ = nseRealTime().Future('INFY', segment=Segment.FUT, expiry=dt.date(2021,12,30))
       print(pd.DataFrame.from_dict(Future_))

       #print(nse.market_status())
       df_ = nseRealTime().OptionChain("INFY",datetime.date(2021, 12, 30))
       df_ = df_.dropna()
       df_ = df_[df_["OPEN_INT"] != 0]
       print(df_ )
       df_.to_csv("realtimeData.csv")

       print(nse.market_status())
       df_ = nseRealTime().OptionChain("INFY",datetime.date(2021, 12, 30))
       df_ = df_.dropna()
       df_ = df_[df_["OPEN_INT"] != 0]
       print(df_ )
       df_.to_csv("realtimeData.csv")
       '''


