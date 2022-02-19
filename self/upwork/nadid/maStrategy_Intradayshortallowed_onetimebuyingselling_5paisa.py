"""
Moving Averaage Stragegy
- Ankit
python 3.9V
"""
## Import Libraries
import pandas as pd
import logging
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pandas as pd
import yfinance as yf
from  self.fivepaisa.connect import fivepaisa
from self.OptionsStrategy.candle_rankings import candle_rankings
from  self.OptionsStrategy.TechnicalAnalysis_candlestick import recognize_candlestick
desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',30)
pd.set_option('display.max_rows',2000)


class PnLCalculator:
    def __init__(self):
        self.quantity = 0
        self.cost = 0.0
        self.market_value = 0.0
        self.r_pnl = 0.0
        self.average_price = 0.0

    def fill(self, pos_change, exec_price):
        n_pos = pos_change + self.quantity
        direction = np.sign(pos_change)
        prev_direction = np.sign(self.quantity)
        qty_closing = min(abs(self.quantity), abs(pos_change)) * direction if prev_direction != direction else 0
        qty_opening = pos_change if prev_direction == direction else pos_change - qty_closing
        new_cost = self.cost + qty_opening * exec_price
        if self.quantity != 0:
            new_cost += qty_closing * self.cost / self.quantity
            #print(qty_closing)
            self.r_pnl += qty_closing * (self.cost / self.quantity - exec_price)
        self.quantity = n_pos
        self.cost = new_cost

    def update(self, closingprice):
        if self.quantity != 0:
            self.average_price = self.cost / self.quantity
        else:
            self.average_price = 0
        self.market_value = self.quantity * closingprice
        return self.market_value - self.cost

class MvAverageStrategy:
    def fieldvalidations(self,data,list_columns):
        columns = (data.reset_index().columns)
        validationStatus = "Pass"
        for i in columns:
            if i in list_columns:
                pass
            else:
                logging.error("Column {} not expected in file ".format(i))
                validationStatus = "Fail"
                assert "Required column missing"

    def logreturn(self,df,shift): return df

    def ema(self,data,period):
        return data.iloc[-period-1:].ewm(span=period, adjust=False).mean()

    def sma(self,data,period):
        return np.array(data.iloc[-period-1:].rolling(window=period, min_periods=period).mean())[-1]

    def signal(self,mv_t1, mv_t2, previousClosingPrice, currentPrice, delta):
        ##  Assumption_1, no gap opening on closing price and next day opening price.
        Tradingsignal = 0
        liquidatePosition = 0
        if (mv_t1 > mv_t2):
            deltacal = (1 - delta) * float(previousClosingPrice)
            if (currentPrice > (1 - delta) * float(previousClosingPrice)):
                Tradingsignal = 1
                liquidatePosition = 1 # Don't Liquidate position

                return Tradingsignal, liquidatePosition,deltacal
            else:
                Tradingsignal = 1
                liquidatePosition = -1 # Liquidate postion
                return Tradingsignal, liquidatePosition, deltacal

        elif (mv_t1 < mv_t2):
            deltacal = (1 + delta) * float(previousClosingPrice)

            if (currentPrice < (1 + delta) * previousClosingPrice) :
                Tradingsignal = -1
                liquidatePosition = 1 # Don't Liquidate postion
                return Tradingsignal, liquidatePosition,deltacal
            else:
                #print("currentPrice  {} >  {} (1 + delta) * float(previousClosingPrice)".format(currentPrice, (1 + delta) * previousClosingPrice))
                Tradingsignal = -1
                liquidatePosition = -1 # Liquidate postion
                return Tradingsignal, liquidatePosition,deltacal
        else:
            return 0, 1, 0


class Portfolio:
    def __init__(self, file, T1: int, T2: int, field: str,returnshift,SellMaxPercentChange,SellpriceChangeBarrier,BuyMaxPercentChange,BuypriceChangeBarrier,maxstocks:int,qtylot:int = 50 ,totalcash = 100000,delta =0.02,):
        print("inside")
        self.df_ = file.reset_index()
        '''
        ## yahoo finance trade
        if "Datetime" in self.df_.columns:
            print("inside Datetime")
            self.readtime = data['Datetime'].dt.strftime('%Y-%m-%d')
            self.df_.Datetime = pd.to_datetime(self.df_.Datetime)
            self.df_.set_index("Datetime",inplace=True)
        else:
            self.readtime = data['Date'].dt.strftime('%Y-%m-%d')
            self.df_.Datetime = pd.to_datetime(self.df_.Date)
            self.df_.set_index("Date",inplace=True)

        '''
        self.list_columns = ["Datetime", "Open", "High", "Low", "Close","Volume"]
        self.T1 = T1
        self.T2 = T2
        self.field = field
        self.returnshift = 1
        self.Tradingsignal = 0
        # 1 = buy , -1 sell , 0 = Neutral
        self.liquidatePosition = -1

        # 1 = Don't Liquidate postion , -1 = Liquidate postion
        self.row = self.T2
        self.totalCash = totalcash
        self.portfolioStocksPosition = 0
        self.PreviousClosingPrice = self.df_.iloc[self.T2 - 1].Close
        print("inside-5")
        self.CurrentOpenPrice = self.df_.iloc[self.T2].Open
        self.delta = delta
        self.maxstocks = maxstocks
        print("inside-2")
        self.portfolio = pd.DataFrame(np.zeros([1, 4]), columns=["transactionprice", "Quantity", "PNL", "MTM"])
        self.qtylot = qtylot
        self.BuypriceChangeBarrier = BuypriceChangeBarrier
        self.SellpriceChangeBarrier = SellpriceChangeBarrier
        self.BuyMaxPercentChange = BuyMaxPercentChange
        self.SellMaxPercentChange = SellMaxPercentChange
        print("INIT loading finish ")

    def mastrategy(self):
        print("Trigger mastrategy *******")
        ## Data Columns Validations
        ''' Disabled field validation for now  '''
        '''
        MvAverageStrategy().fieldvalidations(self.df_,self.list_columns)
        logging.info("Field Validation Completed")
        assert self.T1 < self.T2, "T1 is less than T2"
        '''
        ## Log Return -  Not part of strategy
        #self.df_["Daily_Log_Return"] = MvAverageStrategy().logreturn(df = self.df_[self.field],shift =self.returnshift)
        #self.df_ = self.df_.dropna()
        self.df_["mvAverageStrategy_T1"] =  np.NAN
        self.df_["mvAverageStrategy_T2"] = np.NAN
        self.df_["trading_signal"] = np.NAN
        self.df_["liquidatePosition"] = np.NAN
        self.df_["deltacal"] = np.NAN
        self.df_["Stock_BUY_Sell"] = np.NAN
        self.tradingPrice = np.NAN

        while self.row+1 < len(self.df_):
            #print("Row : {} ".format(self.df_.iloc[self.row+1,1]))
            #print("Moving average ")
            self.df_['mvAverageStrategy_T1'].iat[self.row+1] = MvAverageStrategy().sma(self.df_.iloc[:self.row]["Close"], self.T1)
            self.df_['mvAverageStrategy_T2'].iat[self.row+1] = MvAverageStrategy().sma(self.df_.iloc[:self.row]["Close"], self.T2)
            self.CurrentOpenPrice = self.df_.iloc[self.row].Open
            self.CurrentClosePrice = self.df_.iloc[self.row].Close
            #print("Moving average  of  T1  {} and  T2  {}".format(self.df_['mvAverageStrategy_T1'].iat[self.row+1],self.df_['mvAverageStrategy_T2'].iat[self.row+1]))
            ## Trading Signal
            trading_signal, liquidatePosition, deltacal = MvAverageStrategy().signal(
                self.df_.iloc[self.row+1]["mvAverageStrategy_T1"],
                self.df_.iloc[self.row+1]["mvAverageStrategy_T2"],
                self.df_.iloc[self.row]["Close"],
                self.df_.iloc[self.row+1]["Open"],
                self.delta)

            self.df_["trading_signal"].iat[self.row+1] = trading_signal
            self.df_["liquidatePosition"].iat[self.row + 1] = liquidatePosition
            self.df_["deltacal"].iat[self.row + 1] = deltacal

            if (trading_signal == 1):
                #print(abs(np.sum(self.df_["Stock_BUY_Sell"])))
                if (liquidatePosition == 1):  # Dont liquidate
                    ## buy share

                   # print(self.maxstocks,(np.sum(self.df_["Stock_BUY_Sell"])),trading_signal)
                    if (np.sign(np.sum(self.df_["Stock_BUY_Sell"])) > 0):

                        if ((self.df_["Close"].iloc[self.row + 1] - self.tradingPrice) / self.tradingPrice) < ( self.BuypriceChangeBarrier):
                            self.df_["Stock_BUY_Sell"].iat[self.row + 1] = -np.sum(self.df_["Stock_BUY_Sell"])

                        elif ((self.df_["Close"].iloc[self.row + 1] - self.tradingPrice) / self.tradingPrice) > ( self.BuyMaxPercentChange):
                            self.df_["Stock_BUY_Sell"].iat[self.row + 1] = -np.sum(self.df_["Stock_BUY_Sell"])
                            #print("Buy percentage target met ")
                        else:
                            self.df_["Stock_BUY_Sell"].iat[self.row + 1] = 0

                    elif ((np.sign(np.sum(self.df_["Stock_BUY_Sell"])) == 0 )):
                        self.df_["Stock_BUY_Sell"].iat[self.row + 1] = trading_signal * self.qtylot
                        self.tradingPrice = self.df_["Close"].iloc[self.row + 1]

                    else:
                        self.df_["Stock_BUY_Sell"].iat[self.row + 1] = -np.sum(
                            self.df_["Stock_BUY_Sell"]) + trading_signal * self.qtylot
                        self.tradingPrice = self.df_["Close"].iloc[self.row + 1]
                else:
                    if np.sum(self.df_["Stock_BUY_Sell"].iloc[:self.row]) > 0:
                        self.df_["Stock_BUY_Sell"].iat[self.row + 1] = np.sum(self.df_["Stock_BUY_Sell"]) * liquidatePosition

                    elif np.sum(self.df_["Stock_BUY_Sell"].iloc[:self.row]) < 0:
                        self.df_["Stock_BUY_Sell"].iat[self.row + 1] = np.sum(
                            self.df_["Stock_BUY_Sell"].iloc[:self.row + 1]) * liquidatePosition
                    else:
                        self.df_["Stock_BUY_Sell"].iat[self.row + 1] = 0
            else:
                #print("Trading Signal Sell ")
                if (liquidatePosition == 1):  # Dont liquidate

                    if (np.sign(np.sum(self.df_["Stock_BUY_Sell"])) < 0 ):
                        if ((self.tradingPrice - self.df_["Close"].iloc[self.row + 1]) /self.tradingPrice < self.SellpriceChangeBarrier):

                            self.df_["Stock_BUY_Sell"].iat[self.row + 1] = -np.sum(self.df_["Stock_BUY_Sell"])

                        elif ((self.tradingPrice - self.df_["Close"].iloc[self.row + 1]) /self.tradingPrice > self.SellMaxPercentChange):

                            self.df_["Stock_BUY_Sell"].iat[self.row + 1] = -np.sum(self.df_["Stock_BUY_Sell"])

                        else:
                            self.df_["Stock_BUY_Sell"].iat[self.row + 1] = 0

                    elif ((np.sign(np.sum(self.df_["Stock_BUY_Sell"])) == 0 )):
                        self.df_["Stock_BUY_Sell"].iat[self.row + 1] = trading_signal * self.qtylot
                        self.tradingPrice = self.df_["Close"].iloc[self.row + 1]
                    else:
                        self.df_["Stock_BUY_Sell"].iat[self.row + 1] = -np.sum(self.df_["Stock_BUY_Sell"]) + trading_signal * self.qtylot
                        self.tradingPrice = self.df_["Close"].iloc[self.row + 1]

                else:
                    if np.sum(self.df_["Stock_BUY_Sell"].iloc[:self.row]) > 0:
                        self.df_["Stock_BUY_Sell"].iat[self.row + 1] = np.sum(
                            np.sum(self.df_["Stock_BUY_Sell"])) * liquidatePosition

                    elif np.sum(self.df_["Stock_BUY_Sell"].iloc[:self.row]) < 0:
                        self.df_["Stock_BUY_Sell"].iat[self.row + 1] = np.sum(
                            self.df_["Stock_BUY_Sell"].iloc[:self.row + 1]) * liquidatePosition
                    else:
                        self.df_["Stock_BUY_Sell"].iat[self.row + 1] = 0

            self.row +=1

        self.df_.to_csv("mainData.csv")
        quantities = np.array(self.df_["Stock_BUY_Sell"].iloc[self.T2+1:])
        exec_prices = np.array(self.df_["Close"].iloc[self.T2+1:])
        closing_prices = np.array(self.df_["Close"].iloc[self.T2 + 1:])
        pnls = []
        pos = PnLCalculator()
        profitandloss = []
        for (p, e,r) in zip(quantities, exec_prices,closing_prices):
            pos.fill(p, e)
            u_pnl = pos.update(r)
            profitandloss.append([pos.quantity, pos.r_pnl, u_pnl, pos.average_price])
            pnls.append(u_pnl + pos.r_pnl)

        pnl = pd.DataFrame(profitandloss,columns=["Position","Realised_PNL","MTM","AvgPrc"],index=self.df_.iloc[self.T2+1:].index)
        self.df_.index = pd.to_datetime(self.df_.index)
        pnl.index = pd.to_datetime(pnl.index)
        df_pnl = pd.merge(self.df_, pnl, how='inner', left_index=True, right_index=True)
        df_pnl = df_pnl.drop("Close",axis =1 )
        pnl = df_pnl[["Realised_PNL","MTM"]].tail(1)


        df_pnl.to_csv("masterFileGenerated.csv")
        #print("Total PNL on last Date : {} ".format(pnl.sum(axis=1)))
        df_pnl["Realised_PNL"].to_csv("Realised_PNL.csv")
        plt.plot(df_pnl.Datetime,df_pnl.Realised_PNL, label = "Cummulative PNL")
        plt.title("Cummulative_PNL_maxstocks_"+ str(self.maxstocks))
        plt.xlabel("Datetime")
        plt.ylabel("PNL")
        #plt.savefig("Cummulative_PNL_maxstocks_" + str(self.maxstocks) + ".png")
        #plt.show()
        return df_pnl

if __name__ == "__main__":
    instance = fivepaisa().connection()
    instance.login()
    data = instance.historical_data('N', 'C', 1594, '1m', '2022-01-04', '2022-01-05')
    print(data.set_index("Datetime"))
    print("Dataextracted : Length : {}".format(len(data)))
    '''
    Best  Result (1d) :   BuypriceChangeBarrier = -0.001, maxProftBarrier = 0.009 delta = 0.01
    '''
    ## Daily Strategy - Working
    BuypriceChangeBarrier = -0.021
    maxProftBarrier = 0.007
    delta = 0.01
    intradayStrategy = Portfolio(file=data, T1=10, T2=30, field="Close", returnshift=1, totalcash=10000000,
                                 delta=delta,
                                 maxstocks=300, qtylot=300, BuypriceChangeBarrier=BuypriceChangeBarrier,
                                 BuyMaxPercentChange=maxProftBarrier,
                                 SellpriceChangeBarrier=BuypriceChangeBarrier,
                                 SellMaxPercentChange=maxProftBarrier)
    output_ = intradayStrategy.mastrategy()
    techCandleStickPatterns = recognize_candlestick(data)
    print("CandleSticksPattern :")
    print(techCandleStickPatterns)
    print("BuypriceChangeBarrier : {} and maxProftBarrier {} and delta {}".format(BuypriceChangeBarrier,maxProftBarrier,delta))
    print("total number of Tranactions :  {}".format(len(output_[output_["Stock_BUY_Sell"] != 0])))
    print("Total Brokerage  :  {}".format(len(output_[output_["Stock_BUY_Sell"] != 0]) * 47.20))
    print("Total_Profit : {}".format(np.array(output_[["Realised_PNL","MTM"]].tail(1).sum(axis=1))[0]))

    ###  Parameter calibration
'''    total_  = pd.DataFrame(columns = ["BuypriceChangeBarrier","maxProftBarrier","delta","Total_Profit","Total_Brokerrage","Total_Transactions"])
    for BuypriceChangeBarrier in np.arange(-0.001, -0.1, -0.01):
        SellpriceChangeBarrier= BuypriceChangeBarrier
        for delta in  np.arange(0.02,0.005,-0.001):
            print("*******Value of BuypriceChangeBarrier {}     :  {} ".format(BuypriceChangeBarrier,delta))
            for maxproft in np.arange(0.01,0.001,-0.001):
                intradayStrategy = Portfolio(file=data, T1=10, T2=30, field="Close", returnshift=1, totalcash=10000000,
                                                     delta=delta,
                                                     maxstocks=300, qtylot=300, BuypriceChangeBarrier=BuypriceChangeBarrier, BuyMaxPercentChange=maxproft,
                                                     SellpriceChangeBarrier=SellpriceChangeBarrier,
                                                     SellMaxPercentChange=maxproft)
                output_ = intradayStrategy.mastrategy()
                total_= total_.append({"BuypriceChangeBarrier":BuypriceChangeBarrier,"maxProftBarrier":maxproft,
                               "delta":delta,"Total_Profit":np.array(output_[["Realised_PNL","MTM"]].tail(1).sum(axis=1))[0],
                               "Total_Brokerrage":len(output_[output_["Stock_BUY_Sell"] != 0]) * 50 ,
                                "Total_Transactions":len(output_[output_["Stock_BUY_Sell"] != 0])},ignore_index=True)
                print("DataOutput")
                print(total_.tail(2))

    print("Parameter comparision:")
    print(total_.head(1))
    total_.to_csv("parametercomparision.csv")'''



## Completed
