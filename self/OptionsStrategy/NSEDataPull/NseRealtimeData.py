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
nse=Nse()


class nseRealTime():
       def indexOptions(self,index,option_expiry):
              ns_  = nse.get_quote(index,Segment.OPT,option_expiry)
              df_ = nse.option_chain(index,option_expiry)
              print(df_)
              #df_ = nse.option_chain(index,datetime.date(2021, 12, 30))
              Call_ = df_
              Call_["Symbol"] = index
              Call_["INSTRUMENT"] = "OPTIDX"
              Call_["Close"] =  (Call_["CE.bidprice"] + Call_["CE.askPrice"])/2
              Call_["Option Type"] = "CE"
              print(Call_.columns)
              Call_ = Call_.rename(columns={"expiryDate":"Expiry","CE.strikePrice":"Strike Price","CE.underlyingValue":"Future_Prices","PE.changeinOpenInterest":"OPEN_INT","CE.impliedVolatility":"lib_impliedVolatility"})
              Call_ = Call_[["Symbol","INSTRUMENT","Close","Option Type","Expiry","Strike Price","Future_Prices","OPEN_INT","lib_impliedVolatility"]]
              Put_ = df_
              Put_["Symbol"] = "NIFTY"
              Put_["INSTRUMENT"] = "OPTIDX"
              Put_["Close"] =  (Put_["PE.bidprice"] + Put_["PE.askPrice"])/2
              Put_["Option Type"] = "PE"
              Put_ = Put_.rename(columns={"expiryDate":"Expiry","CE.strikePrice":"Strike Price","CE.underlyingValue":"Future_Prices","PE.changeinOpenInterest":"OPEN_INT","PE.impliedVolatility":"lib_impliedVolatility"})
              Put_ = Put_[["Symbol","INSTRUMENT","Close","Option Type","Expiry","Strike Price","Future_Prices","OPEN_INT","lib_impliedVolatility"]]
              df = pd.concat([Put_, Call_])
              today = date.today()
              df = pd.concat([Put_,Call_])
              df["Date"] = today.strftime("%d-%m-%Y")
              df["Date"] = pd.to_datetime(df["Date"])
              return df

if __name__ == "__main__":
       df_ = nseRealTime().indexOptions("NIFTY",datetime.date(2021, 12, 30))
       print(df_)
       df_.to_csv("realtimeData.csv")
