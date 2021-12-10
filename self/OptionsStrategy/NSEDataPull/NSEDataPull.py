import pandas as pd
#from pynse import *
from nsepy import get_history
from datetime import date
import numpy as np
import datetime as dt
#nse=Nse()
'''d = pd.DataFrame()

c = dt.date(2020,6,15)
x = nse.bhavcopy_fno(c)
x = pd.DataFrame(x).reset_index()
Y =  ["AXISBANK","BANKNIFTY","HDFCBANK","ICICIBANK","SBIN"]
df_2 = x[x["SYMBOL"].isin(Y)]

c = dt.date(2020,6,16)
x = nse.bhavcopy_fno(c)
x = pd.DataFrame(x).reset_index()
Y =  ["AXISBANK","BANKNIFTY","HDFCBANK","ICICIBANK","SBIN"]
df_1 = x[x["SYMBOL"].isin(Y)]
print(df_1)
con = pd.concat([df_2,df_1]).reset_index()
print(con)
#print(nse.market_status())
#nse.info('SBIN')
#print(nse.get_quote('TCS', segment=Segment.FUT, expiry=dt.date( 2020, 6, 30 )))
#x= nse.get_quote('HDFC', segment=Segment.OPT, optionType=OptionType.PE, strike=1800.)
#print(nse.option_chain('INFY'))
#print(nse.option_chain('infy',expiry=dt.date(2021,12,30)))
#nse.get_hist('NIFTY 50', from_date=dt.date(2020,1,1),to_date=dt.date(2020,6,26))

from datetime import datetime

# now = datetime.now() # current date and time

'''
from datetime import datetime

now = datetime.now() # current date and time

year = now.strftime("%Y")
print("year:", year)

month = now.strftime("%m")
print("month:", month)

day = now.strftime("%d")
print("day:", day)

time = now.strftime("%H:%M:%S")
data_ = pd.DataFrame()
for k in np.arange(dt.date(2021,9,1),dt.date(2021,12,7)) :
    k = pd.to_datetime(k)
    year = k.strftime("%Y")
    month = k.strftime("%m")
    date = k.strftime("%d")
    try:
        _date = dt.date(int(year), int(month), int(date))
        print(_date)
        df_ = nse.bhavcopy_fno(_date)
        df_ = pd.DataFrame(df_).reset_index()
        Y = ["AXISBANK", "BANKNIFTY", "HDFCBANK", "ICICIBANK", "SBIN","KOTAKBANK"]
        df_ = df_[df_["SYMBOL"].isin(Y)]
        expiry_dates = df_[df_["SYMBOL"] == "AXISBANK"].EXPIRY_DT.unique()
        expiry_date = [str(i).split("T")[0] for i in expiry_dates]
        df_ = df_[df_["EXPIRY_DT"].isin(expiry_date)]
        data_ = pd.concat([data_,df_])
        print(data_)
    except:
        print("fail")
        print(date)

print("Finish...")
data_.to_csv("consolidted.csv")

df_ = pd.read_csv("consolidted.csv")

df_ = df_[["SYMBOL","INSTRUMENT","EXPIRY_DT","STRIKE_PR","OPTION_TYP","OPEN",
                     "HIGH","LOW","CLOSE","SETTLE_PR","CONTRACTS","VAL_INLAKH","OPEN_INT",
                     "CHG_IN_OI","TIMESTAMP"]]
df_["Future_Prices"] = np.nan
futuredatamerge_ = pd.DataFrame()
for time in df_["TIMESTAMP"].unique():
    print("insde")
    for i in df_["SYMBOL"].unique():
        temp_ = df_[(df_["SYMBOL"] == i) & (df_["TIMESTAMP"] == time)]
        for expiry in temp_["EXPIRY_DT"].unique():
            print(expiry)
            print("FUTIDX")
            print(temp_[(temp_["EXPIRY_DT"] == expiry) & (temp_["INSTRUMENT"] == "FUTIDX" )]["CLOSE"])
            print("FUTSTK")
            print(temp_[(temp_["EXPIRY_DT"] == expiry) & (temp_["INSTRUMENT"] == "FUTSTK")]["CLOSE"])
            close_futureindex = temp_[(temp_["EXPIRY_DT"] == expiry) & (temp_["INSTRUMENT"] == "FUTIDX" )]["CLOSE"]
            close_futurestock = temp_[(temp_["EXPIRY_DT"] == expiry) & (temp_["INSTRUMENT"] == "FUTSTK")]["CLOSE"]

            try:
                print("dsfsfsfdsfsf->")
                print(np.array(close_futurestock)[0])
                temp_.loc[(temp_["EXPIRY_DT"] == expiry) & (
                            temp_["INSTRUMENT"] == "OPTSTK"), "Future_Prices"] = np.array(close_futurestock)[0]
            except:
                pass
            try:
                print("****->")
                print(np.array(close_futureindex)[0])
                temp_.loc[(temp_["EXPIRY_DT"] == expiry) & (temp_["INSTRUMENT"] == "OPTIDX"), "Future_Prices"] = np.array(close_futureindex)[0]
            except:
                pass

            print("Stock option")
            print(temp_.loc[(temp_["EXPIRY_DT"] == expiry) & (temp_["INSTRUMENT"] == "OPTSTK"),:])
            print("index option")
            print(temp_.loc[(temp_["EXPIRY_DT"] == expiry) & (temp_["INSTRUMENT"] == "OPTIDX"),:])
            print("end")
            futuredatamerge_ = pd.concat([futuredatamerge_,temp_])
            print(futuredatamerge_)

print("final")
print(futuredatamerge_)
futuredatamerge_ = futuredatamerge_[["SYMBOL","INSTRUMENT","EXPIRY_DT","STRIKE_PR","OPTION_TYP","OPEN",
                     "HIGH","LOW","CLOSE","SETTLE_PR","CONTRACTS","VAL_INLAKH","OPEN_INT",
                     "CHG_IN_OI","TIMESTAMP","Future_Prices"]]
futuredatamerge_ = futuredatamerge_.drop_duplicates(keep = 'first')
futuredatamerge_ = futuredatamerge_.dropna()
futuredatamerge_.to_csv("futuredatamerge.csv")
futuredatamerge_ = futuredatamerge_.rename(columns = {"SYMBOL" : "Symbol","TIMESTAMP" : "Date","EXPIRY_DT":"Expiry","OPTION_TYP":"Option Type","STRIKE_PR":"Strike Price","OPEN":"Open","HIGH":"High","LOW":"Low","CLOSE":"Close"})
futuredatamerge_.to_csv("futuredatamerge.csv")
print(futuredatamerge_.columns)