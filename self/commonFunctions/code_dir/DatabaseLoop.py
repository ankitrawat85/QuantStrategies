import time
from datetime import datetime
from time import time as _time, sleep as _sleep
from self.commonFunctions.code_dir import database
# datetime object containing current date and time
now = datetime.now()
from pynse import *

nse = Nse()
df_  = nse.market_status()['marketState']
print(df_[0]["marketStatusMessage"])
print("now =", now)
date = datetime.strptime("2021-12-31 18:11:10", '%Y-%m-%d %H:%M:%S')
while datetime.now() <  date:
    print(datetime.now())
    try :
        #database.trigger()
        database.OptionChainRatios()
    except:
        print ("Failed data ")

    time.sleep(60)
print("Trading Day End")





