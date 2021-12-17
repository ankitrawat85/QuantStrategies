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

    def sma(self,data,period):
        return data.iloc[-period-1:].rolling(window=period, min_periods=period).mean()[-1]

    def signal(self,mv_t1, mv_t2, previousClosingPrice, currentPrice, delta):
        ##  Assumption_1, no gap opening on closing price and next day opening price.
        Tradingsignal = 0
        liquidatePosition = 0
        #print("signal")
        #print(mv_t1, mv_t2, previousClosingPrice, currentPrice, delta)
        if (mv_t1 > mv_t2):
            #print ( "mv_t1 {} > mv_t1 {}".format(mv_t1,mv_t2))
            deltacal = (1 - delta) * float(previousClosingPrice)
            if (currentPrice > (1 - delta) * float(previousClosingPrice)):
                #print(" currentPrice  {} >  {} delta".format(currentPrice, deltacal))
                Tradingsignal = 1
                liquidatePosition = 1 # Don't Liquidate position

                return Tradingsignal, liquidatePosition,deltacal
            else:
                #print("currentPrice  {} < {} (1 - delta) * (previousClosingPrice)".format(currentPrice, (1 - delta) * previousClosingPrice))
                Tradingsignal = 1
                liquidatePosition = -1 # Liquidate postion
                return Tradingsignal, liquidatePosition, deltacal

        elif (mv_t1 < mv_t2):
            #print("mv_t1 {} < mv_t1 {}".format(mv_t1, mv_t2))
            deltacal = (1 + delta) * float(previousClosingPrice)
            #print(currentPrice,previousClosingPrice,deltacal)
            if (currentPrice < (1 + delta) * previousClosingPrice) :
                Tradingsignal = -1
                liquidatePosition = 1 # Don't Liquidate postion
                return Tradingsignal, liquidatePosition,deltacal
            else:
                #print("currentPrice  {} >  {} (1 + delta) * float(previousClosingPrice)".format(currentPrice, (1 + delta) * previousClosingPrice))
                Tradingsignal = -1
                liquidatePosition = -1 # Liquidate postion
                return Tradingsignal, liquidatePosition,deltacal


class Portfolio:
    def __init__(self, file, T1: int, T2: int, field: str, returnshift=1,totalcash = 100000,delta =0.02,maxstocks: int = 10):
        self.df_ = pd.read_csv(file, index_col="Date", infer_datetime_format=True)
        self.list_columns = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
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
        self.CurrentOpenPrice = self.df_.iloc[self.T2].Open
        self.delta = delta
        self.maxstocks = maxstocks
        self.portfolio = pd.DataFrame(np.zeros([1, 4]), columns=["transactionprice", "Quantity", "PNL", "MTM"])

    def mastrategy(self):
        print("Moving Average Strategy calcualtion Started")
        ## Data Columns Validations
        MvAverageStrategy().fieldvalidations(self.df_,self.list_columns)
        logging.info("Field Validation Completed")
        assert self.T1 < self.T2, "T1 is less than T2"

        ## Log Return
        self.df_["Daily_Log_Return"] = MvAverageStrategy().logreturn(df = self.df_[self.field],shift =self.returnshift)
        self.df_ = self.df_.dropna()
        self.df_["mvAverageStrategy_T1"] =  np.NAN
        self.df_["mvAverageStrategy_T2"] = np.NAN
        self.df_["trading_signal"] = np.NAN
        self.df_["liquidatePosition"] = np.NAN
        self.df_["deltacal"] = np.NAN
        self.df_["Stock_BUY_Sell"] = np.NAN

        while self.row+1 < len(self.df_):
            #print(self.row+1)
            self.df_['mvAverageStrategy_T1'].iat[self.row+1] = MvAverageStrategy().sma(self.df_.iloc[:self.row]["Daily_Log_Return"], self.T1)
            self.df_['mvAverageStrategy_T2'].iat[self.row+1] = MvAverageStrategy().sma(self.df_.iloc[:self.row]["Daily_Log_Return"], self.T2)
            #print("Validate")
            self.CurrentOpenPrice = self.df_.iloc[self.row].Open

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
            #print("Trading Signal {} and LiquidatePostion {}".format(trading_signal,liquidatePosition))
            #liquidatePosition = 1 # Don't Liquidate postion

            #print ("Sing ------->")
            #print(np.sign(np.sum(self.df_["Stock_BUY_Sell"])))
            if (trading_signal == 1):
                if (liquidatePosition == 1):  # Dont liquidate
                    ## buy share
                    if (self.maxstocks - abs(np.sum(self.df_["Stock_BUY_Sell"])) > trading_signal):
                        assert self.totalCash > self.CurrentOpenPrice * 100, " Short of Cash Balance hence can't buy shares"
                        self.df_["Stock_BUY_Sell"].iat[self.row+1] = trading_signal
                    elif (np.sign(np.sum(self.df_["Stock_BUY_Sell"])) < 0):
                        self.df_["Stock_BUY_Sell"].iat[self.row + 1] = -(np.sum(self.df_["Stock_BUY_Sell"])+self.maxstocks)

                    else:
                        self.df_["Stock_BUY_Sell"].iat[self.row + 1] = -(self.maxstocks - np.sum(self.df_["Stock_BUY_Sell"]))

                else:
                    if np.sum(self.df_["Stock_BUY_Sell"].iloc[:self.row]) > 0:
                        self.df_["Stock_BUY_Sell"].iat[self.row + 1] = np.sum(self.df_["Stock_BUY_Sell"].iloc[:self.row+1]) * liquidatePosition
                    else:
                        self.df_["Stock_BUY_Sell"].iat[self.row + 1] = 0

            else:
                if trading_signal == -1:                         ## Sell share
                    if (liquidatePosition == 1):
                        if (self.maxstocks - abs(np.sum(self.df_["Stock_BUY_Sell"])) > abs(trading_signal)):
                            if (np.sum(self.df_["Stock_BUY_Sell"]) > 0 ):
                                self.df_["Stock_BUY_Sell"].iat[self.row+1] = trading_signal
                            else:
                                self.df_["Stock_BUY_Sell"].iat[self.row + 1] = 0

                        elif (np.sign(np.sum(self.df_["Stock_BUY_Sell"])) < 0):
                                self.df_["Stock_BUY_Sell"].iat[self.row + 1] = -(np.sum(self.df_["Stock_BUY_Sell"])+self.maxstocks)
                        else:
                            self.df_["Stock_BUY_Sell"].iat[self.row + 1] = -(self.maxstocks - np.sum(self.df_["Stock_BUY_Sell"]))

                    else:
                        if np.sum(self.df_["Stock_BUY_Sell"].iloc[:self.row]) < 0:
                            self.portfolio.append([self.CurrentOpenPrice, np.sum(self.portfolio["Quantity"]), 0, 0])
                            self.df_["Stock_BUY_Sell"].iat[self.row + 1] = np.sum(self.df_["Stock_BUY_Sell"].iloc[:self.row+1]) * liquidatePosition
                        else:
                            self.df_["Stock_BUY_Sell"].iat[self.row + 1] = 0

            self.row +=1

        #self.df_.to_csv("mainData.csv")

        quantities = np.array(self.df_["Stock_BUY_Sell"].iloc[self.T2+1:])
        exec_prices = np.array(self.df_["Open"].iloc[self.T2+1:])
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
        df_pnl = df_pnl.drop("Daily_Log_Return",axis =1 )
        print(df_pnl)
        df_pnl.to_csv("masterFileGenerated.csv")
        df_pnl["Realised_PNL"].to_csv("Realised_PNL.csv")
        df_pnl[["Realised_PNL"]].plot()
        plt.title("Cummulative_PNL_maxstocks_"+ str(self.maxstocks))
        plt.xlabel("Date")
        plt.ylabel("PNL")
        plt.savefig("Cummulative_PNL_maxstocks_" + str(self.maxstocks) + ".png")
        plt.show()

        print ("Moving Average Strategy calcualtion Completed")
if __name__ == "__main__":
    strat1 = Portfolio(file="SPY.csv",T1= 10,T2=30, field="Close",returnshift= 1,totalcash=10000000,delta=0.02,maxstocks =30)
    #strat2 = Portfolio(file="SPY.csv", T1=10, T2=30, field="Close", returnshift=1, totalcash=10000000, delta=0.02,
                  #    maxstocks=1000)
    #strat3 = Portfolio(file="SPY.csv", T1=10, T2=30, field="Close", returnshift=1, totalcash=10000000, delta=0.02,
                   #   maxstocks=20)
    strat1.mastrategy()
    #strat2.mastrategy()
    #strat3.mastrategy()

## Completed