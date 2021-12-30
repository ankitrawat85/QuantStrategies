import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',20)
pd.set_option('display.max_rows',6000)

df_ = yf.download('ITC.NS',
                      start='2010-01-01',
                      end='2021-12-01',
                      progress=False,
)
df_["Pct_change"] = df_["Adj Close"].pct_change(periods=1)
df_["moving_Avg"] = df_["Pct_change"].rolling(10).mean()
df_["weekday"] =  df_.index.weekday
df_.reset_index(inplace = True )
import numpy as np
appl_ = df_[df_["weekday"] == 3].groupby([df_.Date.dt.year, df_.Date.dt.month]).last()

pct_change =  0.018

print("greater than 0.0377 ")
appl_  = appl_[["Date","Pct_change"]]
plt.plot(appl_[appl_["Pct_change"] >= pct_change]["Date"],appl_[appl_["Pct_change"] >= pct_change]["Pct_change"])
plt.show()
print(appl_[appl_["Pct_change"] >=pct_change])
print ("total count : {}".format(len(appl_[appl_["Pct_change"] >=pct_change])))