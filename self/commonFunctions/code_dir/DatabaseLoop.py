import time
from datetime import datetime
from time import time as _time, sleep as _sleep
from self.commonFunctions.code_dir import database
# datetime object containing current date and time
now = datetime.now()
from pynse import *
from datetime import date
from pathlib import Path  ## get directory path
import matplotlib.pyplot as plt
import os
##  5paisa connection
from  self.fivepaisa.connect import fivepaisa

nse = Nse()
df_  = nse.market_status()['marketState']
#print(df_[0]["marketStatusMessage"])
print("now =", now)
now_ = datetime.strptime("2022-01-18 18:11:10", '%Y-%m-%d %H:%M:%S')
expiry = date(2022,2, 4)
##  Database  -> pull data from NSe
while datetime.now() >  now_:
    print(datetime.now())
    try :
        database.trigger(db=r"NSEStock.db",ticker="NIFTY",expiry=date(2022,2, 4),instrument="OPTIDX")
        database.OptionChainRatios(ticker="NIFTY",expiry= expiry,instrument="OPTIDX",db=r"NSEStock.db")
    except:
        print ("Failed data ")

    print("Thread Sleep")
    time.sleep(30)
    print("Next Run")
print("Trading Day End")

## 5 Paisa

print(Path(__file__).parent.parent )
path = Path(__file__).parent.parent.parent
path = str(path) + "/Database/stockdata1.db"
print(path)

## SQL Steps
instance = database.database(database=path)
conn = instance.create_connection()

## 5paisa login
client = fivepaisa().connection()
client.login()
print("5paisa login")
while datetime.now() <  now_:
    print(datetime.now())
    try :
        database.InsertstockpriceDailyFivePaisa(ticker ='INFY', Exchange='N', ExchType='C',conn=conn,fivepaisainst=client)
    except Exception as e:
        print ("Failed data : {}".format(print(e)))

    try :
        database.insertTechnicalIndicatorData(ticker ='INFY', Exchange='N', ExchType='C',conn=conn,fivepaisainst=client,selecttablename='dailystockprice',selectColumNname='Datetime',SelectTotalRows=100)
    except Exception as e:
        print ("Failed data : {}".format(print(e)))

    print("Thread Sleep")
    time.sleep(60)
    print("Next Run")
print("Trading Day End")





