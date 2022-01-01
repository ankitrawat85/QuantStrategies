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
        return data.iloc[-period-1:].rolling(window=period, min_periods=period).mean()[-1]

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
        self.df_ = pd.read_csv(file)
        ## yahoo finance trade
        '''
        data = yf.download(tickers='SBIN.NS', period='3m', interval='5m')
        data = data[["Open", "High", "Low", "Close", "Adj Close", "Volume"]]
        data = data.reset_index()
        '''
        if "Datetime" in self.df_.columns:
            print("inside Datetime")
            self.readtime = data['Datetime'].dt.strftime('%Y-%m-%d')
            self.df_.Datetime = pd.to_datetime(self.df_.Datetime)
            self.df_.set_index("Datetime",inplace=True)
        else:
            self.readtime = data['Date'].dt.strftime('%Y-%m-%d')
            self.df_.Datetime = pd.to_datetime(self.df_.Date)
            self.df_.set_index("Date",inplace=True)


        #self.readtime = data['Datetime'].dt.strftime('%Y-%m-%d')
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
        self.qtylot = qtylot
        self.BuypriceChangeBarrier = BuypriceChangeBarrier
        self.SellpriceChangeBarrier = SellpriceChangeBarrier
        self.BuyMaxPercentChange = BuyMaxPercentChange
        self.SellMaxPercentChange = SellMaxPercentChange

    def mastrategy(self):
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

        self.tradingPrice = np.NAN

        while self.row+1 < len(self.df_):
            self.df_['mvAverageStrategy_T1'].iat[self.row+1] = MvAverageStrategy().sma(self.df_.iloc[:self.row]["Daily_Log_Return"], self.T1)
            self.df_['mvAverageStrategy_T2'].iat[self.row+1] = MvAverageStrategy().sma(self.df_.iloc[:self.row]["Daily_Log_Return"], self.T2)
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

            if (trading_signal == 1):

                #print(abs(np.sum(self.df_["Stock_BUY_Sell"])))
                if (liquidatePosition == 1):  # Dont liquidate
                    ## buy share

                   # print(self.maxstocks,(np.sum(self.df_["Stock_BUY_Sell"])),trading_signal)
                    if (np.sign(np.sum(self.df_["Stock_BUY_Sell"])) > 0 ):

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
        pnldf_pnl = df_pnl.drop("Daily_Log_Return",axis =1 )
        pnl = df_pnl[["Realised_PNL","MTM"]].tail(1)


        df_pnl.to_csv("masterFileGenerated.csv")
        #print(df_pnl.columns)
        #print(df_pnl[["Open","High","Low","Close","trading_signal" ,"liquidatePosition","Position","Realised_PNL"]].tail(5))
        print("Total PNL on last Date : {} ".format(pnl.sum(axis=1)))
        print("Total number of transactions :  {} ".format(len(df_pnl)))
        df_pnl["Realised_PNL"].to_csv("Realised_PNL.csv")
        df_pnl[["Realised_PNL"]].plot()
        plt.title("Cummulative_PNL_maxstocks_"+ str(self.maxstocks))
        plt.xlabel("Date")
        plt.ylabel("PNL")
        plt.savefig("Cummulative_PNL_maxstocks_" + str(self.maxstocks) + ".png")
        plt.show()

if __name__ == "__main__":
    data = yf.download(tickers='INFY.NS', period='1wk', interval='1m', progress=False)
    data = data[["Open", "High", "Low", "Close", "Adj Close", "Volume"]]
    data = data[data["Volume"] != 0]
    data = data.reset_index()
    data.to_csv("realtime.csv")
    data =data.rename(columns = {"index":"Date"})
    data.to_csv("realtime.csv")
    data_csv = "realtime.csv"
    '''
    strat1 = Portfolio(file=data_csv, T1=10, T2=30, field="Close", returnshift=1, totalcash=10000000, delta=0.01,
                        maxstocks=500,qtylot=50,BuypriceChangeBarrier=-0.01,BuyMaxPercentChange=0.06,SellpriceChangeBarrier=-0.01,
                       SellMaxPercentChange=0.06)

    strat1.mastrategy()
    '''

    ## Daily Strategy - Working

    strat2 = Portfolio(file=data_csv, T1=10, T2=30, field="Close", returnshift=1, totalcash=10000000, delta=0.02,
                        maxstocks=300,qtylot=300,BuypriceChangeBarrier=-0.01,BuyMaxPercentChange=0.04,SellpriceChangeBarrier=-0.01,
                       SellMaxPercentChange=0.04)

    strat2.mastrategy()

    '''
    ## intraday strategy - working
    #info_ = pd.DataFrame(columns={"BuypriceChangeBarrier,delta,txn,"})
    for i in np.arange(-0.001,-0.01,-0.001):
        print("******Start***************************")
        print("Value of BuypriceChangeBarrier :  {} ".format(i))
        for Delta in np.arange(0.02,0.0001,-0.001):
            print("Value of Delta :  {} ".format(Delta))
            intradayStrategy = Portfolio(file=data_csv, T1=10, T2=30, field="Close", returnshift=1, totalcash=10000000, delta=Delta,
                                maxstocks=200,qtylot=200,BuypriceChangeBarrier=i,BuyMaxPercentChange=0.03,SellpriceChangeBarrier=-0.001,
                               SellMaxPercentChange=0.03)
            intradayStrategy.mastrategy()
    '''

    '''
    strat3 = Portfolio(file=data_csv, T1=10, T2=20, field="Close", returnshift=1, totalcash=10000000, delta=0.02,
                        maxstocks=100,qtylot=50,BuypriceChangeBarrier=-0.01,BuyMaxPercentChange=0.06,SellpriceChangeBarrier=-0.01,
                       SellMaxPercentChange=0.06)

    strat3.mastrategy()

    strat4 = Portfolio(file=data_csv, T1=10, T2=20, field="Close", returnshift=1, totalcash=10000000, delta=0.02,
                        maxstocks=100,qtylot=50,BuypriceChangeBarrier=-0.01,BuyMaxPercentChange=0.02,SellpriceChangeBarrier=-0.01,
                       SellMaxPercentChange=0.04)

    strat4.mastrategy()


    strat5 = Portfolio(file=data_csv, T1=10, T2=20, field="Close", returnshift=1, totalcash=10000000, delta=0.03,
                        maxstocks=100,qtylot=50,BuypriceChangeBarrier=-0.01,BuyMaxPercentChange=0.03,SellpriceChangeBarrier=-0.01,
                       SellMaxPercentChange=0.03)
    strat5.mastrategy()
   '''

## Completed
