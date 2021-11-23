import os
import sys

import pandas as pd
sys.path.append('/Users/ankitrawat/Desktop/smu/Classes/Self/Code/Quant/venv/commonFunctions')
## import all libraries

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import pypfopt
from pypfopt.black_litterman import BlackLittermanModel

import seaborn as sns

'''Import personal libraries '''
from commonFunctions import data, models, datapull
from commonFunctions import normalization

class Test_PortfolioAnalysis():

    def __init__(self,*args,**kargs):
        self.nse50 = "https://en.wikipedia.org/wiki/NIFTY_50"
        self.datasite = "yahoo"
        print (self.nse50)

    def processing(self):
        '''Directory Path'''
        #sys.path.append('/Users/ankitrawat/Desktop/smu/Classes/Self/Code/Quant/venv/commonFunctions')
        #print (os.path.abspath(__file__))

        '''Nifty 50 List - Wikipidia '''
        df_ = pd.read_html(self.nse50)[1]
        df_ = df_.iloc[:,1:3]
        df_nse50 = df_[df_["Sector"] == "Banking"]["Symbol"]
        print ("after removing banking -->")
        print (df_nse50)
        '''Data pull for list of stocks'''
        data_start = "2010-01-01"
        data_end  = "2021-04-30"
        stock_list  = pd.DataFrame(df_nse50).stack().values
        print (stock_list)
        df_ = data().downloadData(self.datasite,stock_list, data_start, data_end,"Close")
        return df_

#x  = Test_PortfolioAnalysis().processing()
#df_ = pd.DataFrame(x)

# Download stock data then export as CSV
import yfinance as yf

'''Import personal libraries '''
from commonFunctions import data, dataValidation
from pandas_datareader import data
import pandas as pd
import yfinance as yf


class Test_PortfolioAnalysis():

    def __init__(self,*args,**kargs):
        self.nse50 = "https://en.wikipedia.org/wiki/NIFTY_50"
        self.datasite = "yahoofinancial"
        print (self.nse50)

    def processing(self):
        '''Nifty 50 List - Wikipidia '''
        df_ = pd.read_html(self.nse50)[1]
        df_ = df_.iloc[:,1:3]
        df_nse50 = df_[df_["Sector"] == "Banking"]["Symbol"]
        print ("after removing banking -->")
        print (df_nse50)
        '''Data pull for list of stocks'''
        data_start = "2010-01-01"
        data_end  = "2021-04-30"
        stock_list  = pd.DataFrame(df_nse50).stack().values
        print (stock_list)
        df_ = datapull().downloadData(self.datasite,stock_list, data_start, data_end,"Close")
        return df_

"""x  = Test_PortfolioAnalysis().processing()
df_ = pd.DataFrame(x)
print(x)"""

data_start = "2010-01-01"
data_end = "2021-04-30"
df_ = datapull().downloadData("yahoofinancial",["^NSEI"], data_start, data_end,"Close")
print
