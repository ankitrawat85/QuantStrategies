import sys
import os
import yfinance as yf
## Graph
import seaborn as sns
import numpy as np
import scipy.stats as stats
import random
import warnings
import matplotlib.pyplot as plt
import pandas as pd
import sys
data_start = "2021-1-01"
data_end = "2021-12-17"
df_stock = yf.download("INFY.NS", data_start, data_end)
#print(df_stock)
df_stock.to_csv("infy.csv")

#data = yf.download(tickers='infy.ns', period='3mo', interval='1d')
#Print data
#print(data.head(10))
#data.to_csv("infy.csv")