'''

Technical Indicators  - Algo

'''
import pandas as pd
import matplotlib.pyplot as plt

""""Import libraries"""
import sys
sys.path.append('/Users/myworld/Desktop/smu/Classes/Self/Code/Quant/MQF/self')
from self.commonFunctions.code_dir.datapull import data,dataValidation,graph,stationary,models
from self.commonFunctions.code_dir.utilities import  *

#Download Data
data_start = "2020-01-01"
data_end = "2021-11-24"
df_1 = data().downaloadAllCol("yahoo","INFY.NS", data_start, data_end)
df_1.index =  pd.to_datetime(df_1.index )

#Log-Return
df_1["Daily_Log_Return"]= data.logReturn(df_1["Adj Close"],1)
df_1["Monthly_Log_Return"] = data.logReturn(df_1["Adj Close"],30)
df_1["Monthly_Log_Return"] = data.logReturn(df_1["Adj Close"],30)

##Moving_Avegage
df_1["MovingAverage_25"] = df_1["Daily_Log_Return"].rolling(25).mean()
df_1["MovingAverage_50"] = df_1["Daily_Log_Return"].rolling(50).mean()
df_1["EWAM_25"] = df_1["Daily_Log_Return"].ewm(span=25, adjust=False).mean()
df_1["EWAM_50"] = df_1["Daily_Log_Return"].ewm(span=30, adjust=False).mean()
print (df_1[df_1.index > "2021-10-01"][["Monthly_Log_Return","MovingAverage_25","MovingAverage_50","EWAM_25","EWAM_50"]].tail(50))
df_1[["Monthly_Log_Return","MovingAverage_25","MovingAverage_50","EWAM_25","EWAM_30"]].plot()
plt.show()
