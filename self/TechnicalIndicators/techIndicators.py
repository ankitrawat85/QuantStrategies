'''

Technical Indicators  - Algo

'''
import pandas as pd
import matplotlib.pyplot as plt
import ta.momentum
import ta.trend
import ta.volume
import ta.trend
""""Import libraries"""
import sys
sys.path.append('/Users/myworld/Desktop/smu/Classes/Self/Code/Quant/MQF/self')


class volumeIndicator:
    def vwap(self,df,window : int,intraday = False):
        '''
        vwap mainly used for intraday
         used to calculate dataframe
         : param window : total number of days to calculate
        '''
        print(ta.volume.volume_weighted_average_price(high=df["High"],low=df["Low"],close=df["Close"],volume=df["Volume"],window = window))
        return ta.volume.volume_weighted_average_price(high=df["High"],low=df["Low"],close=df["Close"],volume=df["Volume"],window = window)


class trendIndicator:

    def SMA(self, df,window):
        '''

         Simple moving average

        '''
        #df["SMA_"+str(window)] = ta.trend.SMAIndicator(df,window).sma_indicator()
        print(ta.trend.SMAIndicator(df,window).sma_indicator())
        return ta.trend.SMAIndicator(df,window).sma_indicator()

    def expMA(self,df,window):
        '''

        exponential moving average

        '''
        print(ta.trend.EMAIndicator(df, window).ema_indicator())
        return ta.trend.EMAIndicator(df, window).ema_indicator()
