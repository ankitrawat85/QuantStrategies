"""
Moving Averaage Stragegy

"""
## Import Libraries
import pandas as pd
import logging
import numpy as np

class mvAverageStrategy:
    def  fieldValidations(df_,list_columns):
        columns  = list(df_.reset_index)
        validationStatus = "Pass"
        for i in columns:
            if i in list_columns:
                pass
            else:
                logging.error("Column {i} not available in file ".format(i))
                validationStatus = "Fail"
                assert "Required column missing"


    def logreturn(df,ReturnShift):
        def logReturn(self):
            return pd.DataFrame(np.log(df) - np.log(self.df.shift(ReturnShift)))


    def sma(data,period): return data.rolling(window=period, min_periods=period)

    def signal(mv_t1,mv_t2,previousClosingPrice,currentPrice,delta):
            ##  Assumption_1, no gap opening on closing price and next day opening price.
            if (mv_t1  > mv_t2 ) :
                    if ( currentPrice > (1- delta) * previousClosingPrice):
                        Tradingsignal = 1
                        liquidatePosition = 0
                    else:
                        Tradingsignal = 1
                        liquidatePosition = 1

            elif (mv_t1<  mv_t2) :
                  if (currentPrice < (1 + delta) * previousClosingPrice):
                      Tradingsignal = -1
                      liquidatePosition = 0
                  else:
                      Tradingsignal = -1
                      liquidatePosition = 1

            return Tradingsignal,liquidatePosition


class portfolio:
    def __init__(self, file, T1: int, T2: int, field: str, dailyReturn=1):
        self.df_ = pd.read_csv(file,index_col="Date",infer_datetime_format=True)
        self.list_columns = ("Date", "Open", "High", "Low", "Close", "AdjClose", "Volume")
        self.T1 = T1
        self.T2 = T2
        self.field = field
        self.ReturnShift = 1
        self.Tradingsignal = 0
        # 1 = buy , -1 sell , 0 = Neutral
        self.liquidatePosition = -1
        # 1 = Yes , -1 = No
        self.row = self.T2 +1
        self.totalCash = 10000
        self.portfolioStocksPosition = 0
        self.MTM =0
        self.PNL =0
        self.PreviousClosingPrice = self.df_.iloc[self.T2-1].Close
        self.CurrentOpenPrice = self.df_.iloc[self.T2].Open
        self.delta = 0.02
        self.portfolio =  pd.DataFrame(np.zeros([1,4]),columns=["transactionprice","portfolioStocksPosition", "PNL", "MTM"])

    def maStrategy(self):
    ## Data Columns Validations
       mvAverageStrategy().fieldValidations(self.df_,self.list_columns)
       assert self.T1 < self.T2 ,"T1 is less than T2"

    ## Log Return
       self.df_["Daily_Log_Return"] = mvAverageStrategy.logreturn(self.df_[self.field],self.ReturnShift)

       for self.row in len(self.df_):
           self.df_.iloc[self.row]["mvAverageStrategy_T1"] = mvAverageStrategy.sma(self.df_.iloc[:self.row]["Daily_Log_Return"],self.T1)
           self.df_.iloc[self.row]["mvAverageStrategy_T2"] = mvAverageStrategy.sma(self.df_.iloc[:self.row]["Daily_Log_Return"],self.T2)
           self.CurrentOpenPrice = self.df_.iloc[self.row].Open

           ## Trading Signal
           trading_signal,liquidatePosition = mvAverageStrategy.signal(self.df_.iloc[self.row]["mvAverageStrategy_T1"],self.df_.iloc[self.row]["mvAverageStrategy_T2"],
                                    self.PreviousClosingPrice,self.CurrentOpenPrice,self.delta)


           if (trading_signal == 1):
               if (liquidatePosition == 0 ):
                   ## buy share
                   assert self.totalCash > self.CurrentOpenPrice * 100, "Short of Cash Balance hence can't buy shares"
                   self.portfolio = 
                   self.portfolio.append(self.CurrentOpenPrice,trading_signal)
                   self.portfolioStocksPosition +=1
                   ## stock purchased on current open price
                   self.portfolio = self.portfolioStocksPosition * self.CurrentOpenPrice




           else:
















