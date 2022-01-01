import sqlite3
from sqlite3 import Error


''''
What is the Put Call Ratio?

Put/Call ratio (PCR) is a popular derivative indicator, specifically designed to help traders gauge the overall sentiment (mood) of the market. 
The ratio is calculated either on the basis of options trading volumes or on the basis of the open interest for a particular period. 
If the ratio is more than 1, it means that more puts have been traded during the day and if it is less than 1, it means more calls have been traded. 
The PCR can be calculated for the options segment as a whole, which includes individual stocks as well as indices.

If PCR = 0.8 : Market Bottom up 
if PCR - 1.7 : Market will crash 
if PCR : 1< 1.7 : bullish 
take 1000 point up and down 

High PCR - Volume  : Bearish 

Increase in volume of put / call  volume indicate   brearish 
'''
import matplotlib.pyplot as plt
from self.commonFunctions.code_dir.database import *

con = sqlite3.connect(r"/Users/myworld/Desktop/smu/Classes/Self/Code/Quant/QR/self/commonFunctions/code_dir/NSEStockData.db")
cursor = con.cursor()

#df = pd.read_sql_query("select * from OptionChainRatios where PE_expiryDate = '06-Jan-2022' ;",con)
df = pd.read_sql_query("select * from OptionChainRatios where PE_expiryDate = '06-Jan-2022' and strikePrice > 16000  and strikePrice < 19000;",con)

'''df_ = df[df["strikePrice"] == 17400][["Date", "PCR_OI" ,"PCR_vol"]]
df_["moving_average_PCR_OI"] =  df_["PCR_OI"].rolling(8).mean()
df_["moving_average_PCR_vol"] =  df_["PCR_vol"].rolling(8).mean()
df_["PCR_OI_pct_change"] =  df_["PCR_OI"].pct_change(1)
df_["PCR_vol_pct_change"] =  df_["PCR_vol"].pct_change(1)
df_["PCR_vol_Sentiments"] = df_["moving_average_PCR_vol"].apply(lambda x : "Bullish" if x > 1 else ( "Bearish" if x < 0.60  else  "Neutral") )
df_["PCR_OI_Sentiments"] = df_["moving_average_PCR_OI"].apply(lambda x : "Bullish" if x > 1 else ( "Bearish" if x < 0.60  else  "Neutral") )
print("Strike Price : -  {}".format(17400))
df_.set_index("Date",inplace = True)
df_ = df_.dropna()
print(df_)
df_["moving_average_PCR_OI"].plot( color = 'black')
W@w    ## Buy
    if df_["PCR_OI"].values[i] > 1:
        plt.plot(df_.index.values[i],df_["PCR_OI"].values[i],'g.')
    elif df_["PCR_OI"].values[i] < 1:
        plt.plot(df_.index.values[i], df_["PCR_OI"].values[i], 'r.')
    else:
        plt.plot(df_.index.values[i], df_["PCR_OI"].values[i], 'b.')

plt.title("PCR_OI indicator signal - 17300")
plt.show()
df_["moving_average_PCR_vol"].plot( color = 'black')
for i in range(len(df_)):
    ## Buy
    if df_["PCR_vol"].values[i] > 1:
        plt.plot(df_.index.values[i],df_["PCR_vol"].values[i],'g.')
    elif df_["PCR_vol"].values[i] < 1:
        plt.plot(df_.index.values[i], df_["PCR_vol"].values[i], 'r.')
    else:
        plt.plot(df_.index.values[i], df_["PCR_vol"].values[i], 'b.')

plt.title("PCR_vol indicator signal - 17300")
plt.show()
'''

'''

Co-orelation between PCR ratio and price 

'''

##  PCR ratio of all the stikes in a given range    §

df_allstrike = df[["Date","strikePrice","Symbol","PE_openInterest","CE_openInterest","CE_totalTradedVolume","PE_totalTradedVolume"]]
df_allstrike = df_allstrike[df_allstrike["Symbol"] == "NIFTY"].groupby("Date").sum()
df_allstrike["PCR_OI"] =  df_allstrike["PE_openInterest"] / df_allstrike["CE_openInterest"]
df_allstrike["PCR_vol"] =  df_allstrike["PE_totalTradedVolume"] / df_allstrike["CE_totalTradedVolume"]

df_allstrike["moving_average_PCR_OI"] =  df_allstrike["PCR_OI"].rolling(8).mean()
df_allstrike["moving_average_PCR_vol"] =  df_allstrike["PCR_vol"].rolling(8).mean()
df_allstrike["PCR_OI_pct_change"] =  df_allstrike["PCR_OI"].pct_change(1)
df_allstrike["PCR_vol_pct_change"] =  df_allstrike["PCR_vol"].pct_change(1)
df_allstrike["PCR_vol_Sentiments"] = df_allstrike["moving_average_PCR_vol"].apply(lambda x : "Bullish" if x > 1 else ( "Bearish" if x < 0.60  else  "Neutral") )
df_allstrike["PCR_OI_Sentiments"] = df_allstrike["moving_average_PCR_OI"].apply(lambda x : "Bullish" if x > 1 else ( "Bearish" if x < 0.60  else  "Neutral") )
print("Strike Price : -  {}".format(17400))
#df_allstrike.set_index("Date",inplace = True)
df_allstrike = df_allstrike.dropna()
df_allstrike["moving_average_PCR_OI"].plot( color = 'black')
for i in range(len(df_allstrike)):
    ## Buy
    if df_allstrike["PCR_OI"].values[i] > 1:
        plt.plot(df_allstrike.index.values[i],df_allstrike["PCR_OI"].values[i],'g.')
    elif df_allstrike["PCR_OI"].values[i] < 1:
        plt.plot(df_allstrike.index.values[i], df_allstrike["PCR_OI"].values[i], 'r.')
    else:
        plt.plot(df_allstrike.index.values[i], df_allstrike["PCR_OI"].values[i], 'b.')

plt.title("PCR_OI indicator signal - between  Strike Range")
plt.show()
df_allstrike["moving_average_PCR_vol"].plot( color = 'black')
for i in range(len(df_allstrike)):
    ## Buy
    if df_allstrike["PCR_vol"].values[i] > 1:
        plt.plot(df_allstrike.index.values[i],df_allstrike["PCR_vol"].values[i],'g.')
    elif df_allstrike["PCR_vol"].values[i] < 1:
        plt.plot(df_allstrike.index.values[i], df_allstrike["PCR_vol"].values[i], 'r.')
    else:
        plt.plot(df_allstrike.index.values[i], df_allstrike["PCR_vol"].values[i], 'b.')

plt.title("PCR_vol indicator signal   between  Strike Range")
plt.show()

print(df_allstrike.drop(columns = {"strikePrice","PE_openInterest",  "CE_openInterest" , "CE_totalTradedVolume" , "PE_totalTradedVolume"}))


