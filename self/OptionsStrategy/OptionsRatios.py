import sqlite3
from sqlite3 import Error


''''
What is the Put Call Ratio?

Put/Call ratio (PCR) is a popular derivative indicator, specifically designed to help traders gauge the overall sentiment (mood) of the market. 
The ratio is calculated either on the basis of options trading volumes or on the basis of the open interest for a particular period. 
If the ratio is more than 1, it means that more puts have been traded during the day and if it is less than 1, it means more calls have been traded. 
The PCR can be calculated for the options segment as a whole, which includes individual stocks as well as indices.

'''
import matplotlib.pyplot as plt
from self.commonFunctions.code_dir.database import *
con = sqlite3.connect(r"/Users/myworld/Desktop/smu/Classes/Self/Code/Quant/QR/self/commonFunctions/code_dir/NSEStockData.db")
cursor = con.cursor()
df = pd.read_sql_query("select * from OptionChainRatios;",con)
df_1 = df[["Date","strikePrice","CE_net_qty", "PE_net_qty", "PCR_OI", "PCR_vol"]][df["strikePrice"] == 17300]
df_2 = df[["Date","strikePrice","CE_net_qty", "PE_net_qty", "PCR_OI", "PCR_vol"]][df["strikePrice"] == 17200]
plt.plot(df_1["Date"],df_1["PCR_OI"], color = 'red')
plt.plot(df_1["Date"],df_1["PCR_vol"], color = 'green')
plt.xticks(df["Date"], rotation='vertical')
plt.title("df_1_17300")
plt.show()
plt.plot(df_2["Date"],df_2["PCR_OI"], color = 'purple')
plt.plot(df_2["Date"],df_2["PCR_vol"], color = 'black')
plt.xticks(df["Date"], rotation='vertical')
plt.title("df_1_17200")
plt.show()