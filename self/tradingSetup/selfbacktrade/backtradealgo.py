'''

It comtain backtrading algo. This is main file connecting all trading parametrs

'''
import backtrader.sizers
import pandas as pd
import yfinance as yf
import backtrader as bt
import backtrader.analyzers as btanalyzer
from enum import Enum
import numpy as np
from self.TechnicalIndicators.techIndicators import  volumeIndicator,trendIndicator
import pandas as pd
import talib as ta
import pandas_ta as pta

## SQL
import sqlite3
from sqlite3 import Error
from pathlib import Path  ## get directory path
import matplotlib.pyplot as plt
from self.commonFunctions.code_dir.database import database  as datainsert

desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',30)
pd.set_option('display.max_rows',2000)

## log
import logging

##Dataimport
from  self.fivepaisa.connect import fivepaisa

## 5paisa - order booking
from py5paisa.order import Order, OrderType, AHPlaced

## indicator
from ta.volatility import BollingerBands,AverageTrueRange
from ta.momentum import StochasticOscillator, RSIIndicator
from ta.volume import VolumePriceTrendIndicator
from ta.trend import  ADXIndicator

class datalist(Enum):
    buy = 1
    sell = -1
    yahoo = 1
    fivepaisa = 2
    database =3
    liquidate = -1
    realtime =   1# realtime data
    historical = 2 # historical data

    ## 5paisa
    fivepaisaNSE = 'N'
    fivepaisacash = 'C'
    fivepaisaDerivative ='D'
    fivepaisascriptcodeCash = 1594
    fivepaisascriptcodePut = 45580
    fivepaisascriptcodeCall = 45578
    fivepaisawindow = '15m'
    fivepaisastarttime = '2022-01-17'
    fivepaisaendtime = '2022-02-01'
    fivepaisaBuy = 'B'
    fivepaisaSell ='S'
    fivepaisaQuantity = 50
    fivepaisaIntradayTrue = "True"
    fivepaisaIntradayFalse = "False"
    fivepaisaioc_orderTrue = "True"
    fivepaisaioc_orderFalse = "False"
    fivepaisaAhplacedTrue = "Y"
    fivepaisaAhplacedFalse = "N"
    fivepaisaTicker = "INFY"
    fivePaisaCurrentCallOptionPrice = 0
    fivePaisaCurrentPutOptionPrice = 0
    fivepaisaPosition = 0
    fivepaisaPaperTrading = 1
    fivepaisaDerivativeScriptSymbolCE = [{"Exch": "N", "ExchType": "D", "Symbol": "NIFTY 03 Feb 2022 CE 17500.00", "Expiry": "20210201",
                  "StrikePrice": "17500", "OptionType": "CE"}]
    fivepaisaDerivativeScriptSymbolPE = [{"Exch": "N", "ExchType": "D", "Symbol": "NIFTY 03 Feb 2022 PE 17500.00", "Expiry": "20210201",
                  "StrikePrice": "17500", "OptionType": "PE"}]


class orderbookingDetails:

    infy_buy_derivaitive = Order(order_type='B', exchange='N', exchange_segment='D', scrip_code=119118, quantity=300,
                         price=datalist.fivePaisaCurrentCallOptionPrice , is_intraday=True, ioc_order=True, ahplaced='Y')

    infy_sell_derivaitive = Order(order_type='S', exchange='N', exchange_segment='D', scrip_code=119118, quantity=300,
                         price=datalist.fivePaisaCurrentCallOptionPrice, is_intraday=True, ioc_order=True, ahplaced='Y')

    infy_cancel_derivaitive = Order(order_type='S', exchange='N', exchange_segment='D', scrip_code=119118, quantity=300,
                         price=datalist.fivePaisaCurrentCallOptionPrice, is_intraday=True, ioc_order=True, ahplaced='Y')

    orderbooking_derivaitive_buy_Call = Order(order_type=datalist.fivepaisaSell.value, exchange=datalist.fivepaisaNSE.value,
                         exchange_segment=datalist.fivepaisaDerivative.value,
                         scrip_code=datalist.fivepaisascriptcodeCall.value,
                         quantity=datalist.fivepaisaQuantity.value, price=datalist.fivePaisaCurrentCallOptionPrice,
                         is_intraday=datalist.fivepaisaIntradayFalse.value,
                         ioc_order=datalist.fivepaisaioc_orderTrue.value, ahplaced=datalist.fivepaisaAhplacedTrue.value)

    orderbooking_derivaitive_infy_buy_Put = Order(order_type=datalist.fivepaisaSell.value, exchange=datalist.fivepaisaNSE.value,
                         exchange_segment=datalist.fivepaisaDerivative.value,
                         scrip_code=datalist.fivepaisascriptcodePut.value,
                         quantity=datalist.fivepaisaQuantity.value, price=datalist.fivePaisaCurrentCallOptionPrice,
                         is_intraday=datalist.fivepaisaIntradayFalse.value,
                         ioc_order=datalist.fivepaisaioc_orderTrue.value, ahplaced=datalist.fivepaisaAhplacedTrue.value)

class tradingStragegy:

    def __init__(self):
        pass

    def movingAverageCrossOver(self,*args,**kwargs):
        pass

    def rsiOverboughtOversold(self,*args,**kwargs):
        pass

    def macd(self,*args,**kwargs):
        pass

    def tradingSignal(self,*args,**kwargs):
        logging.log(msg="generating trading Signal",level=1)
        print(f' Generating Trading Signal')
        print(kwargs["data"]["SMA_100"])

        ## Moving Average
        tradingSignal = 0
        print(kwargs["data"])
        print(kwargs["data"]["SMA_15"])
        print(kwargs["data"]["SMA_100"])
        print(kwargs["data"]["Close"])
        print(kwargs["data"]["SMA_15"])
        ## Buy Signal
        if ((kwargs["data"]["SMA_25"][2] > kwargs["data"]["SMA_100"][2]) &(kwargs["data"]["Close"][2] > kwargs["data"]["SMA_7"][2])):
            if (kwargs["data"]["Close"][1] > kwargs["data"]["SMA_7"][2]):
                if (kwargs["data"]["Close"][0] > kwargs["data"]["SMA_7"][2]):
                    tradingSignal = 1
        ## Sell Signal
        elif ((kwargs["data"]["SMA_25"][2] < kwargs["data"]["SMA_100"][2]) & (kwargs["data"]["Close"][2] < kwargs["data"]["SMA_7"][2])):
                if (kwargs["data"]["Close"][1] < kwargs["data"]["SMA_7"][2]):
                    if (kwargs["data"]["Close"][0] < kwargs["data"]["SMA_7"][2]):
                        tradingSignal = -1

        return tradingSignal

        ## macd

        ## macd

        pass


class basicTechnicalIndicators:

    def technicalIndicators(self,historicaldata):
        close = historicaldata["Close"]

        ##  Simple Moving Average
        SMA_100 = trendIndicator().SMA(close, window=100)
        SMA_100 = SMA_100.iloc[-1]
        SMA_15 = trendIndicator().SMA(close.iloc[-16:-1], window=15)
        SMA_15 = SMA_15.iloc[-1]
        SMA_25 = trendIndicator().SMA(close.iloc[-100:-1], window=26)
        SMA_25 = SMA_25.iloc[-1]
        SMA_7 = trendIndicator().SMA(close.iloc[-8:-1], window=7)
        SMA_7 = SMA_7.iloc[-1]

        ## Exponential Moving average
        EMA_100 = trendIndicator().expMA(close, window=100)
        EMA_100 = EMA_100.iloc[-1]
        EMA_25 = trendIndicator().expMA(close.iloc[-100:-1], window=26)
        EMA_25 = EMA_25.iloc[-1]
        EMA_15 = trendIndicator().expMA(close.iloc[-16:-1], window=15)
        EMA_15 = EMA_15.iloc[-1]
        EMA_7 = trendIndicator().expMA(close.iloc[-8:-1], window=7)
        EMA_7 = EMA_7.iloc[-1]

        ## VWAP indicator
        vwap_7 = volumeIndicator().vwap(historicaldata, 7, intraday=True)
        vwap_7 = vwap_7.iloc[-1]
        vwap_15 = volumeIndicator().vwap(historicaldata, 15, intraday=True)
        vwap_15 = vwap_15.iloc[-1]
        vwap_25 = volumeIndicator().vwap(historicaldata, 25, intraday=True)
        vwap_25 = vwap_25.iloc[-1]
        vwap_100 = volumeIndicator().vwap(historicaldata, 100, intraday=True)
        vwap_100 = vwap_100.iloc[-1]

        ## RSI
        rsi_7 = ta.RSI(close, timeperiod=7)
        print(rsi_7.iloc[-1])
        rsi_7 = rsi_7.iloc[-1]
        rsi_15 = ta.RSI(close, timeperiod=15)
        print(rsi_15.iloc[-1])
        rsi_15 = rsi_15.iloc[-1]
        # rsi_100 = ta.RSI(close, timeperiod=105)
        # print(rsi_100)vmap_7
        # print(rsi_100.iloc[-1])
        x = historicaldata.values
        x = x[-1]
        print("technidicator")
        print(x)

        ## MACD Signal
        MACD_25_15 = EMA_25 - EMA_15

        ## ADX
        '''
        the market is trending in the direction of the greater DMI line if it is above 25. 
        If it is below 25, it suggests that the trend is weak or range bound. 
        If the ADX comes from 15 to 23, a trend could be developing. 
        If the ADX goes from 32 to 25, the trend may be coming to an end.
        '''
        print(historicaldata.iloc[-15:-1])
        adx_ = pta.adx(historicaldata["High"].iloc[-15:-1], historicaldata["Low"].iloc[-15:-1], historicaldata["Close"].iloc[-15:-1], length=7)
        print(adx_.iloc[-1,-6:].values)
        vpt_ = VolumePriceTrendIndicator(close=historicaldata["Close"].iloc[-15:-1], volume=historicaldata["Volume"].iloc[-15:-1]).volume_price_trend().pct_change()
        print(vpt_)
        '''
        Price is rising and volume is rising and/or above average = bullish market; the uptrend is being supported by market participants.
        r Price is rising and volume is falling or below average = a warning sign that a top or consolidation of trend is near.
        r Price is falling and volume is rising or above average = bearish market; the downtrend is being supported by market participants.
        r Price is falling and volume is falling or below average = a warning of a bottom or a consolidation of the trend is near.
        '''
        x = np.append(x,
                  [SMA_7, SMA_15, SMA_25, SMA_100, EMA_7, EMA_15, EMA_25, EMA_100, vwap_7, vwap_25, vwap_15, vwap_100,
                   rsi_7, rsi_15, MACD_25_15])
        print(x)
        x = np.append(x, [adx_.iloc[-1,-6:].values])
        print(x)
        print(type(vpt_))
        print(vpt_.iloc[-1])
        x = np.append(x, [vpt_.iloc[-1]])
        print(x)

        print(np.append(x, [SMA_7, SMA_15,SMA_25, SMA_100, EMA_7, EMA_15,EMA_25, EMA_100, vwap_7,vwap_25, vwap_15, vwap_100, rsi_7, rsi_15,MACD_25_15]))
        return np.append(x, [SMA_7, SMA_15,SMA_25, SMA_100, EMA_7, EMA_15,EMA_25, EMA_100, vwap_7,vwap_25, vwap_15, vwap_100, rsi_7, rsi_15,MACD_25_15])



class backtestBackTrader(basicTechnicalIndicators):
    def __init__(self):

        ## Database connectivity
        print(Path(__file__).parent.parent.parent)
        path = Path(__file__).parent.parent.parent
        self.stockdata = str(path) + "/Database/stockdata1.db"
        self.con = sqlite3.connect(self.stockdata)

        ## stats sotred
        self.lastClosingPrice = 0
        self.position = {'ScripCode':0}
        self.orderstatus = None
        self.currentStockprice = None
        self.currentStockOptionCallPrice = None
        self.currentStockOptionPutPrice = None

        ## risk management parameters
        self.positionlimit =300
        self.dailylosslimit = 0
        self.maxlosttlimit =0

        # windows

        ## signal
        self.buy = 1
        self.sell = -1
        self.tradingSignal =-1
        self.liquidate = 0
        self.closePosition =0
        self.liveorder = {'ScripCode':0}

        ## 5 paisa connectivity
        print("Connection")
        self.fivePaisaConnection =  fivepaisa().connection()
        self.fivePaisaConnection.login()
        print("setup")

    def datafetch(self,source,timeframe,*args,**kwargs):
        try:
            if source == 1: # yahoo
                if timeframe == 1:  ## realtime data fetch
                    #logging.DEBUG("inside yahoo datafetch")
                    print(kwargs["tickers"],kwargs["period"],kwargs["interval"])
                    df_ = yf.download(tickers=kwargs["tickers"], period=kwargs["period"], interval=kwargs["interval"], progress=False)
                    df_ = df_[["Open", "High", "Low", "Close", "Adj Close", "Volume"]]
                    df_ = df_[df_["Volume"] != 0]
                    logging.log(msg="Datafetched from yahoo",level=1)
                    return df_

                elif timeframe == 2: ## historical data
                    logging.error(f" Source {source} and timeframe {timeframe} selected is not configured ")

                else:
                    logging.error(f"Input Data timeframe  is not not correct for source {source}")
                    assert f"Input Data timeframe  is not not correct for source {source}"


            elif source == 2: # 5 Paisa
                if timeframe == 1:  ## realtime
                    req_list_ = [ {"Exch": kwargs['exchange'], "ExchType": kwargs['ExchType'], "Symbol": kwargs['ticker']}]
                    df_ = self.fivePaisaConnection.fetch_market_feed(req_list_)
                    df_ = df_["Data"]
                    df_ = pd.DataFrame.from_dict([df_[-1]])
                    print(df_)
                    data = df_[["Time", "PClose", "High", "Low", "LastRate", "TotalQty"]]
                    return df_
                    #datainsert().insertstockrealtime(self.con, data.iloc[-1, :].values)


                elif timeframe == 2: ## historical
                    logging.info(f" Source {source} and timeframe {timeframe} selected ")
                    # historical_data(<Exchange>,<Exchange Type>,<Scrip Code>,<Time Frame>,<From Data>,<To Date>)

                    df = self.fivePaisaConnection.historical_data('N', 'C', 1594, '15m', '2022-01-01', '2022-01-28')
                    print(df)

                    # Note : TimeFrame Should be from this list ['1m','5m','10m','15m','30m','60m','1d']
                    print(kwargs['exchange'],kwargs['market'],kwargs['scriptcode'],
                                                             kwargs['timelag'],kwargs['startime'],kwargs['endtime'])
                    output_ = self.fivePaisaConnection.historical_data(kwargs['exchange'],kwargs['market'],kwargs['scriptcode'],
                                                             kwargs['timelag'],kwargs['startime'],kwargs['endtime'])
                    return output_

                else:
                    logging.error(f"Input Data timeframe  is not not correct for source {source}")
                    assert f"Input Data timeframe  is not not correct for source {source}"

            elif source == 3: # database
                if timeframe == 1:
                    pass

                elif timeframe == 2:
                    database = kwargs["tablename"]
                    logging.log(msg = f"Database source is {database}",level=1)
                    return pd.read_sql_query("select * from "+database+";", self.con)
                else:
                    pass

            else:
                logging.error("Input Data source is not not correct")
                assert "source it not defined"

        except Exception as e:
            logging.error(msg =f' Failed to get details  {e}')


    def databasefetchAllData(self,database,column):
        cursor = self.con.cursor()
        data = pd.read_sql_query("select {column} from {database} ;", self.con)
        return data

    def databasefetchLastRows(self,tablename,columnname,totalrows):
        cursor = self.con.cursor()
        query = "select * from "+tablename+" ORDER BY "+columnname+" DESC LIMIT "+str(totalrows)+";"
        return  pd.read_sql_query(query, self.con)

    def databasefetchTopRows(self,tablename,columnname,totalrows):
        cursor = self.con.cursor()
        query = "select * from " + tablename + " ORDER BY " + columnname + " LIMIT " + str(totalrows) + ";"
        return  pd.read_sql_query(query, self.con)

    def databseinsert(self,**kwargs):
        try:
            print(kwargs["data"])
            print(len(kwargs["data"]))
            instance = datainsert(database=self.stockdata)
            instance.insertstockindicators(self.con,kwargs["data"])

        except Exception as e:
            logging.error(msg=f' Error while inserting technical indicators data in database : {e}')
            assert "Error while inserting technical indicators data in database"

    def tradingsignal(self,strategies : list):
        pass

    def orderBook(self,*args,**kwargs):  ## Get details of order placed
        try:
            return self.fivePaisaConnection.order_book()

        except Exception as e:
            logging.error(msg = f' Error message while fetching order booking : {e}')
            assert "Failed to get order booking details"

    def tradebook(self,*args,**kwargs):
        try:
            return self.fivePaisaConnection.get_tradebook()
        except Exception as e:
                logging.error(msg=f' Error message while fetching Trade bookings : {e}')
                assert "Failed to get trade book details"


    def Position(self,*args,**kwargs):
        try:
            return self.fivePaisaConnection.positions()

        except Exception as e:
            logging.error(msg=f' Error message while fetching position : {e}')
            assert "Failed to get position details"

    def holding(self,*args,**kwargs):
        try:
            return self.fivePaisaConnection.holdings()

        except Exception as e:
            logging.error(msg=f' Error message while fetching position : {e}')
            assert "Failed to get position details"


    def orderBooking(self,*args,**kwargs):
        try:
            orderbooking_ = self.fivePaisaConnection.place_order(kwargs["order"])
            return orderbooking_
        except Exception as e:
            logging.error(msg=f' Error message booking order  : {e}')
            assert "Failed to book order"

    def orderCancellation(self,*args,**kwargs):
        try:
            return self.fivePaisaConnection.cancel_order(kwargs["Exchange"],kwargs["Exchange_Segment"],kwargs["ExchOrderID"])
        except Exception as e:
            logging.error(msg=f' Error message booking order  : {e}')
            assert "Failed to book order"

    def positionClose(self,*args,**kwargs):
        try:
            if kwargs["Position"] > 0 :
                ordersell = self.orderBooking(order=Order(order_type=datalist.fivepaisaSell.value, exchange=datalist.fivepaisaNSE.value,
                         exchange_segment=datalist.fivepaisaDerivative.value,
                         scrip_code=datalist.fivepaisascriptcodeCall.value,
                         quantity=datalist.fivepaisaQuantity.value,
                         is_intraday=datalist.fivepaisaIntradayFalse.value,
                         ioc_order=datalist.fivepaisaioc_orderTrue.value, ahplaced=datalist.fivepaisaAhplacedFalse.value))

            elif kwargs["Position"] < 0:
                pass

        except Exception as e:
            logging.error(msg=f' failed to close the position : {e}')
            assert "failed to close the position"



    def riskManagement(self):
        pass


    def profitAndLoss(self):
        pass


    def main(self):

        req_list_ = [

            {
                "Exch": "N",
                "ExchType": "D",
                "ScripCode": 119111,
                "BrokerOrderId": "625069999"
            }]
        # Fetches the order status
        print(self.fivePaisaConnection.fetch_order_status(req_list_)["OrdStatusResLst"])


        ## 1. Cancel all exisintng orders before starting

        ## 2. Fetch Historical  Price
        historical = self.datafetch(datalist.fivepaisa.value, datalist.historical.value, exchange='N', market='C',
                                      scriptcode=datalist.fivepaisascriptcodeCash.value, database='db',
                                      startime= datalist.fivepaisastarttime.value,endtime = datalist.fivepaisaendtime.value,
                                      timelag = datalist.fivepaisawindow.value
                                      )
        historical = historical.iloc[-150:-1,:]

        ## 3. Technical indicators
        tech_ = self.technicalIndicators(historical)
        print(tech_)

        ## 4. insert data in Database
        self.databseinsert(data=tech_)

        ## Moving Average Trading Strategy
        previousvalue = self.databasefetchLastRows(columnname="Datetime", totalrows=3, tablename="stockpriceindicators")
        movingAverageTradingSignal = tradingStragegy().tradingSignal(data = previousvalue)

        ## Fetch Current Stock Cash Price
        self.currentStockprice = self.datafetch(datalist.fivepaisa.value, datalist.realtime.value, exchange='N', ExchType='C',
                                      ticker=datalist.fivepaisaTicker, database='db')

        ## Fetch Current Stock Derivative Put Price
        #self.currentStockOptionPutPrice = self.fivePaisaConnection.fetch_market_feed(datalist.fivePaisaCurrentPutOptionPrice)

        ## Fetch Current Stock Derivative Call  Price
        #self.currentStockOptionCallPrice = self.fivePaisaConnection.fetch_market_feed(datalist.fivePaisaCurrentCallOptionPrice)


        ## 3.other Validations - RiskManagement -> total loss exceed
        pos_ = self.Position()
        print(pos_)
        hold_ = self.holding()
        print(hold_)

        ## 4.OrderBookPosition
        orderbook = self.orderBook()
        count = 0
        for i in orderbook:
            if str(i["OrderStatus"]).__contains__("Pending") & (count == 1):
                self.liveorder = i
                count == 1
            else:
                logging.error(msg="multiple live orders. kindly handle outside")
                assert f"multiple live orders. kindly handle outside :  {i}"
                count == 0


        print(f'Live order : {self.liveorder}')

        ## 5. position
        self.fivepaisaPosition = 0 if len(self.Position()) == 0 else 1
        print(self.fivepaisaPosition)

        ## 6.Strategies and trading signal

        ## 6. Consolidate Signal


        ## 7. Order booking
        if ( datalist.buy  == self.tradingSignal):
            if ( self.liveorder["ScripCode"] == datalist.fivepaisascriptcodePut.value):
                self.order = self.orderCancellation(Exchange='N',Exchange_Segment='D',ExchOrderID=self.liveorder["ExchOrderID"])

            elif ( self.liveorder["ScripCode"] == datalist.fivepaisascriptcodeCall.value):
                pass

            else:
                if self.position["ScripCode"] == datalist.fivepaisascriptcodeCall.value:
                    pass

                elif self.position["ScripCode"] == datalist.fivepaisascriptcodePut.value:
                    self.order = self.orderBooking(order=Order(order_type=datalist.fivepaisaSell.value, exchange=datalist.fivepaisaNSE.value,
                         exchange_segment=datalist.fivepaisaDerivative.value,
                         scrip_code=datalist.fivepaisascriptcodePut.value,
                         quantity=datalist.fivepaisaQuantity.value,
                         is_intraday=datalist.fivepaisaIntradayFalse.value,
                         ioc_order=datalist.fivepaisaioc_orderTrue.value, ahplaced=datalist.fivepaisaAhplacedTrue.value))


                elif self.position == 0:
                    self.order = self.orderBooking(order=
                                    Order(order_type=datalist.fivepaisaBuy.value,
                                    exchange=datalist.fivepaisaNSE.value,
                                    exchange_segment=datalist.fivepaisaDerivative.value,
                                    scrip_code=datalist.fivepaisascriptcodePut.value,
                                    quantity=datalist.fivepaisaQuantity.value,
                                    is_intraday=datalist.fivepaisaIntradayFalse.value,
                                    ioc_order=datalist.fivepaisaioc_orderTrue.value,
                                    ahplaced=datalist.fivepaisaAhplacedTrue.value))

        #elif (self.tradingSignal == datalist.buy) &(self.position <= 0):
        elif ( datalist.sell.value  == self.tradingSignal):
            if (self.liveorder["ScripCode"] == datalist.fivepaisascriptcodeCall.value):
                self.order = self.orderCancellation(Exchange='N', Exchange_Segment='D',
                                                    ExchOrderID=self.liveorder["ExchOrderID"])
                if self.order["Message"] != "Success":
                    logging.error(
                        msg=f'Order Cancellation Failed -- order: {self.liveorder},message: {self.order["Message"] },Details :{self.order}')


            elif (self.liveorder["ScripCode"] == datalist.fivepaisascriptcodePut.value):
                pass

            else:
                if self.position["ScripCode"] == datalist.fivepaisascriptcodePut.value:
                    pass

                elif self.position["ScripCode"] == datalist.fivepaisascriptcodeCall.value:
                    self.order = self.orderBooking(order=Order(order_type=datalist.fivepaisaSell.value, exchange=datalist.fivepaisaNSE.value,
                                    exchange_segment=datalist.fivepaisaDerivative.value,
                                    scrip_code=datalist.fivepaisascriptcodeCall.value,
                                    quantity=datalist.fivepaisaQuantity.value,
                                    is_intraday=datalist.fivepaisaIntradayFalse.value,
                                    ioc_order=datalist.fivepaisaioc_orderTrue.value,
                                    ahplaced=datalist.fivepaisaAhplacedTrue.value))


                elif self.fivepaisaPosition == 0:
                    self.order = self.orderBooking(order=Order(order_type=datalist.fivepaisaBuy.value,
                                                         exchange=datalist.fivepaisaNSE.value,
                                                         exchange_segment=datalist.fivepaisaDerivative.value,
                                                         scrip_code=datalist.fivepaisascriptcodePut.value,
                                                         quantity=datalist.fivepaisaQuantity.value,
                                                         is_intraday=datalist.fivepaisaIntradayFalse.value,
                                                         ioc_order=datalist.fivepaisaioc_orderFalse.value,price=1,
                                                         ahplaced=datalist.fivepaisaAhplacedFalse.value))
                    print(self.order)
                    if self.order['Message'] == "Success":
                        logging.info(
                            msg=f'BUY PUT  CREATED -- Size: {datalist.fivepaisaQuantity.value},OrderDetails: {self.order}')
                    else:
                            logging.error(
                                msg=f'BUY PUT order creation failed  Failed -- details: {self.order}')

        ##Trade status
        req_list = [
            {
                "Exch": "N",
                "ExchType": "C",
                "ScripCode": 20374,
                "ExchOrderID": "1000000015310807"
            }]
        # Fetches the trade details
        print(self.fivePaisaConnection.fetch_trade_info(req_list))

        req_list_ = [

            {
                "Exch": "N",
                "ExchOrderID":"625069999"
            }]
        # Fetches the order status
        print(self.fivePaisaConnection.fetch_order_status(req_list_))
        print(self.fivePaisaConnection.fetch_order_status(req_list_)["OrdStatusResLst"])

        ## Order Book
        orderStatus =  self.orderBook()

        #Previous closing price from stock indicators colums
        previousvalue = self.databasefetchLastRows(columnname ="Datetime",totalrows =1,tablename="stockpriceindicators")

        ## Fetch latest price
        currentprice = self.datafetch(datalist.fivepaisa.value,datalist.realtime.value,exchange='N',ExchType='C',ticker='INFY',database = 'db')
        #currentprice = self.datafetch(datalist.fivepaisa.value,datalist.historical.value,exchange='N',market='C',scriptcode=1594,timelag='1m',startime='2022-01-04',endtime='2022-01-04')
        print(currentprice)

        ## trigger different strategies to get trading signal

        ## verify existing pending order book for a given script, if have position , cancel it

        ## verify if any existing order in order staus
        pass


if __name__ == "__main__":
    connectionsetp = backtestBackTrader()
    connectionsetp.main()


    ## instance creation

    backtestesting = backtestBackTrader()
    '''
    ##  fetch realtime data form yahoo
    ##backtestesting  = backtestesting.datafetch(datalist.yahoo.value,datalist.realtime.value,tickers="INFY.NS",period="1wk",interval="1m")
    #print(backtestesting)

    ##  fetch realtime data form database
    ##print(backtestesting.databseinsert())
    #dailystockprice = backtestesting.datafetch(datalist.database.value,datalist.historical.value,tablename = "dailystockprice")
    #dailystockprice = backtestesting.databasefetchLastRows(columnname ="Datetime",totalrows =21,
                                             #  tablename="dailystockprice")
    for i in np.arange(105,200,1):
        print(i)
        
        dailystockprice = backtestesting.databasefetchLastRows(columnname ="Datetime",totalrows =i,
                                                   tablename="dailystockprice")
        print(dailystockprice)
        close = dailystockprice["Close"]

        ##  Simple Moving Average
        SMA_100 = trendIndicator().SMA(close,window=100)
        SMA_100 = SMA_100.iloc[-1]
        SMA_15 = trendIndicator().SMA(close.iloc[-16:-1], window=15)
        SMA_15 = SMA_15.iloc[-1]
        SMA_7 = trendIndicator().SMA(close.iloc[-8:-1], window=7)
        SMA_7 = SMA_7.iloc[-1]

        ## Exponential Moving average
        EMA_100 = trendIndicator().expMA(close,window=100)
        EMA_100 = EMA_100.iloc[-1]
        EMA_15 = trendIndicator().expMA(close.iloc[-16:-1], window=15)
        EMA_15 = EMA_15.iloc[-1]
        EMA_7 = trendIndicator().expMA(close.iloc[-8:-1], window=7)
        EMA_7 = EMA_7.iloc[-1]

        ## VWAP indicator
        vwap_7 = volumeIndicator().vwap(dailystockprice,7,intraday=True)
        vwap_7 = vwap_7.iloc[-1]
        vwap_15 = volumeIndicator().vwap(dailystockprice,15,intraday=True)
        vwap_15 = vwap_15.iloc[-1]
        vwap_100 = volumeIndicator().vwap(dailystockprice,100,intraday=True)
        vwap_100 = vwap_100.iloc[-1]

        ## RSI
        rsi_7 = ta.RSI(close, timeperiod=7)
        print(rsi_7.iloc[-1])
        rsi_7 = rsi_7.iloc[-1]
        rsi_15 = ta.RSI(close, timeperiod=15)
        print(rsi_15.iloc[-1])
        rsi_15 = rsi_15.iloc[-1]
        #rsi_100 = ta.RSI(close, timeperiod=105)
        #print(rsi_100)
        #print(rsi_100.iloc[-1])
        x = dailystockprice.values
        x = x[-1]
        x = np.append(x,[SMA_7,SMA_15,SMA_100,EMA_7,EMA_15,EMA_100,vwap_7,vwap_15,vwap_100,rsi_7,rsi_15])
        print(x)
        backtestesting.databseinsert(data =x)
        '''



