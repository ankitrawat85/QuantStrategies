import time
from datetime import datetime
from time import time as _time, sleep as _sleep
from self.commonFunctions.code_dir import databasetesting
# datetime object containing current date and time
now = datetime.now()

print("now =", now)
date = datetime.strptime("2021-12-27 18:11:10", '%Y-%m-%d %H:%M:%S')
while date > datetime.now():
    print(datetime.now())
    try :
        databasetesting.trigger()
    except:
        print ("Failed data ")

    time.sleep(1800)

