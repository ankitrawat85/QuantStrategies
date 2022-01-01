import time
from datetime import datetime
from time import time as _time, sleep as _sleep
from self.commonFunctions.code_dir import database
# datetime object containing current date and time
now = datetime.now()
from pynse import *
from datetime import date
nse = Nse()
df_  = nse.market_status()['marketState']
print(df_[0]["marketStatusMessage"])
print("now =", now)
now_ = datetime.strptime("2022-01-06 18:11:10", '%Y-%m-%d %H:%M:%S')
expiry = date(2022, 1, 6)
while datetime.now() <  now_:
    print(datetime.now())
    try :
       # database.trigger(database=r"NSEStockData.db",ticker="NIFTY",expiry=date(2021, 12, 30),instrument="OPTIDX")
        database.OptionChainRatios(ticker="NIFTY",expiry= expiry,instrument="OPTIDX",db=r"NSEStockData.db")
    except:
        print ("Failed data ")

    print("Thread Sleep")
    time.sleep(180)
    print("Next Run")
print("Trading Day End")





