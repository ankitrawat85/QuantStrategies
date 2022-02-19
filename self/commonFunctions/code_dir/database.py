import sqlite3
from sqlite3 import Error
import numpy as np
import pandas as pd
import datetime
import time
from datetime import date
from self.OptionsStrategy.NSEDataPull.NseRealtimeData import nseRealTime
from self.OptionsStrategy.optionsvaluation.optionpricing import  Vol
from self.OptionsStrategy.optionsvaluation.optionpricing import optionsGreeks
from self.TechnicalIndicators.techIndicators import  volumeIndicator,trendIndicator
import datetime
import itertools
import traceback
import yfinance as yf
import ta
from datetime import datetime, timezone

import time
from datetime import datetime
from time import time as _time, sleep as _sleep

# datetime object containing current date and time
now = datetime.now()
print("now =", now)

from pathlib import Path  ## get directory path
import matplotlib.pyplot as plt
import os

##  5paisa connection
from  self.fivepaisa.connect import fivepaisa

class Activity:
    def __init__(self):
        self.insert = "insert"
        self.select = "select"

class createtablescripts:
    def __init__(self):
        self.sql_create_optionchain_table = """ CREATE TABLE IF NOT EXISTS optionchain (
                                            Strike_Price int NOT NULL,
                                            Expiry text,
                                            underlying text,
                                            identifier text,
                                            OPEN_INT float,
                                            changeinOpenInterest float,
                                            pchangeinOpenInterest float,
                                            totalTradedVolume float,
                                            lastPrice float,
                                            change float,
                                            pChange float,
                                            totalBuyQuantity int,
                                            totalSellQuantity int,
                                            lib_impliedvolatility float,
                                            bidQty int,
                                            bidprice int,
                                            askQty float,
                                            askPrice float,
                                            Future_Prices float,
                                            Symbol text,
                                            INSTRUMENT text,
                                            Close  float, 
                                            Option_Type text, 
                                            Date datetime NOT NULL,
                                            time_diff int,
                                            impliedvolatility  float,
                                            Delta float,
                                            Gamma float,
                                            Theta float,
                                            Vega float
                                             ); """

        self.sql_create_optionchainratios_table = """ CREATE TABLE IF NOT EXISTS OptionChainRatios (strikePrice, expiryDate, PE_strikePrice, PE_expiryDate, PE_underlying, PE_identifier, PE_openInterest, PE_changeinOpenInterest, PE_pchangeinOpenInterest, PE_totalTradedVolume, PE_impliedVolatility, PE_lastPrice, PE_change, PE_pChange, PE_totalBuyQuantity, PE_totalSellQuantity,
PE_bidQty, PE_bidprice, PE_askQty, PE_askPrice, PE_underlyingValue, CE_strikePrice, CE_expiryDate, CE_underlying, CE_identifier, CE_openInterest, CE_changeinOpenInterest, CE_pchangeinOpenInterest, CE_totalTradedVolume, CE_impliedVolatility, CE_lastPrice, CE_change, CE_pChange,
CE_totalBuyQuantity, CE_totalSellQuantity, CE_bidQty, CE_bidprice, CE_askQty, CE_askPrice, CE_underlyingValue, Symbol, INSTRUMENT, Date text, CE_net_qty, PE_net_qty, PCR_OI, PCR_vol); """

        self.sql_create_option_table = None
        self.sql_create_stock_table = None

        self.sql_create_stockrealtimeData_table = """ CREATE TABLE IF NOT EXISTS dailystockprice (
                                                    Datetime datetime NOT NULL PRIMARY KEY,
                                                    Open float NOT NULL,
                                                    High float NOT NULL,
                                                    Low float NOT NUll,
                                                    Close  float NOT NUll,
                                                    Volume float NOT NULL
                                                     ); """
        self.sql_create_stockpriceindicators_table = """ CREATE TABLE IF NOT EXISTS stockpriceindicators (
                                                    Datetime datetime NOT NULL PRIMARY KEY,
                                                    Open float NOT NULL,
                                                    High float NOT NULL,
                                                    Low float NOT NUll,
                                                    Close  float NOT NUll,
                                                    Volume float NOT NULL,
                                                    SMA_7 float DEFAULT NULL,
                                                    SMA_15 float DEFAULT NULL,SMA_25 float DEFAULT NULL,
                                                    SMA_100 float DEFAULT NULL,
                                                    EMA_7 float DEFAULT NULL,
                                                    EMA_15 float DEFAULT NULL,EMA_25 float DEFAULT NULL,
                                                    EMA_100 float DEFAULT NULL,
                                                    vwap_7 float DEFAULT NULL,
                                                    vwap_15 float DEFAULT NULL,vwap_25 float DEFAULT NULL,
                                                    vwap_100 float DEFAULT NULL,
                                                    rsi_7 float DEFAULT NULL,
                                                    rsi_15 float DEFAULT NULL,
                                                    MACD_25_15 float DEFAULT NULL
                                                     ); """


class database:

    def __init__(self,database = "default",**kwargs):
        self.data = None
        self.database = database
        self.activity = None

    def create_connection(db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)

        return conn

    def create_table(self, conn, create_table_sql):
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
            print("Table Created")
        except Error as e:
            print(e)

    def insertOptionChain(self,conn, task):
        sql = ''' INSERT INTO Optionchain(Strike_Price, Expiry, underlying, identifier, OPEN_INT, changeinOpenInterest, pchangeinOpenInterest,
        totalTradedVolume, lastPrice, change,
        pChange, totalBuyQuantity, totalSellQuantity,lib_impliedvolatility, bidQty, bidprice,
        askQty, askPrice, Future_Prices, Symbol, INSTRUMENT, Close, Option_Type, Date, time_diff, impliedvolatility, Delta, Gamma, Theta, Vega) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        try:
            cur = conn.cursor()
            print("inside insertoptinchain1_1")
            cur.execute(sql, task)
            conn.commit()
        except Exception as e:
            print("Failed to insert")
            print(str(e))
            traceback.print_exc()

        return cur.lastrowid

    def insertOptionChainRatios(self,conn,task):
        sql = ''' INSERT INTO OptionChainRatios(strikePrice, expiryDate, PE_strikePrice, PE_expiryDate, PE_underlying, PE_identifier, PE_openInterest, PE_changeinOpenInterest, PE_pchangeinOpenInterest, PE_totalTradedVolume, PE_impliedVolatility, PE_lastPrice, PE_change, PE_pChange, PE_totalBuyQuantity, PE_totalSellQuantity,
        PE_bidQty, PE_bidprice, PE_askQty, PE_askPrice, PE_underlyingValue, CE_strikePrice, CE_expiryDate, CE_underlying, CE_identifier, CE_openInterest, CE_changeinOpenInterest, CE_pchangeinOpenInterest, CE_totalTradedVolume, CE_impliedVolatility, CE_lastPrice, CE_change, CE_pChange,
        CE_totalBuyQuantity, CE_totalSellQuantity, CE_bidQty, CE_bidprice, CE_askQty, CE_askPrice, CE_underlyingValue, Symbol, INSTRUMENT, Date, CE_net_qty, PE_net_qty, PCR_OI, PCR_vol) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, task)
        conn.commit()
        return cur.lastrowid

    def insertOptionData(conn, task):
        sql = ''' INSERT INTO Optionchain(
                  Strike_Price,Expiry,underlying,identifier,OPEN_INT,changeinOpenInterest,pchangeinOpenInterest,
                  totalTradedVolume,lib_impliedVolatility,lastPrice,change, 
                  pChange, totalBuyQuantity, totalSellQuantity, bidQty, bidprice,
                  askQty,askPrice,Future_Prices,Symbol,INSTRUMENT,Close,Option_Type,Date) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, task)
        conn.commit()
        return cur.lastrowid

    def insertstock(self,conn, task):
        sql = ''' INSERT INTO Optionchain(
                  Strike_Price,Expiry,underlying,identifier,OPEN_INT,changeinOpenInterest,pchangeinOpenInterest,
                  totalTradedVolume,lib_impliedVolatility,lastPrice,change, 
                  pChange, totalBuyQuantity, totalSellQuantity, bidQty, bidprice,
                  askQty,askPrice,Future_Prices,Symbol,INSTRUMENT,Close,Option_Type,Date) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, task)
        conn.commit()
        return cur.lastrowid

    def insertstockrealtime(self,conn, task):
        sql = '''INSERT INTO dailystockprice (Datetime,Open,High,Low,Close,Volume) VALUES(?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, task)
        conn.commit()
        return cur.lastrowid

    def insertstockindicators(self,conn, task):
        sql = '''INSERT INTO stockpriceindicators (Datetime,Open,High,Low,Close,Volume,SMA_7,SMA_15,SMA_25,SMA_100,
        EMA_7,EMA_15,EMA_25,EMA_100,vwap_7,vwap_15,vwap_25,vwap_100,rsi_7,rsi_15,MACD_25_15) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, task)
        conn.commit()
        return cur.lastrowid

    def create_connection(self):
        conn = None
        # database = r"trading.db"
        try:
            conn = sqlite3.connect(self.database)
            print("Connection setup to {}".format(self.database))
            return conn
        except Error as e:
            print(e)
        return conn

    def CreatDatabase(self):
        conn = None
        #database = r"trading.db"
        try:
            conn = sqlite3.connect(self.database)
            print("Database Created")
        except Error as e:
            print(e)

    def CreatTable(self, conn, create_table_sql):
        print("Create table")
        if conn is not None:
            print(conn)
            # create projects table
            print("Inside CreatTable")
            print(create_table_sql)
            database(self.database).create_table(conn, create_table_sql)
        else:
            print("Error! cannot create the database connection.")

    def select_all_tasks(self,conn,query):
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            print(row)
        return rows

    def addcolumn(self,conn,tablename,column):
        conn = sqlite3.connect(self.database)
        columnadd = '''ALTER TABLE {tableName} ADD COLUMN column default  NUll;'''
        if conn is not None:
            conn.execute(columnadd)
            conn.commit()
        else:
            print("Error! cannot create the database connection.")



def trigger(db,ticker,expiry,instrument):
        ## SQL Steps
        instance = database(database=db)
        ## Create Database
        instance.CreatDatabase()

        ## Create Connection
        conn = instance.create_connection()
        ## Create Table
        instance.CreatTable(conn, createtablescripts().sql_create_optionchain_table)
        ## Create Insert Data
        RealTimeOption = nseRealTime().OptionChain(ticker, option_expiry=expiry,instrument=instrument)
        print("RealTimeOption")
        print(RealTimeOption.head(10))
        RealTimeOption = RealTimeOption[RealTimeOption["OPEN_INT"] != 0]
        RealTimeOption = RealTimeOption.dropna(axis=0)
        data_ = RealTimeOption
        data_ = data_.rename(columns = {"Strike Price" : "Strike_Price","Future Prices":"Future_Prices","Option Type":"Option_Type"})

        ##  Volatility and Greeks calculation
        print('Greeks calculation')
        data_["time_diff"] = optionsGreeks().time_to_expiry(data_[["Expiry", "Date"]])["time_diff"]
        print(data_.columns)
        print(data_.dtypes)
        data_["impliedvolatility"] = data_["lib_impliedvolatility"]
        '''
        data_["impliedvolatility"] = \
            optionsGreeks().implied_volatility_options(
                data_[["Strike_Price", "Future_Prices", "Close", "time_diff", "Option_Type","lib_impliedvolatility"]])[
                "impliedvolatility"]
        '''


        data_["Delta"] = \
            optionsGreeks().delta_options(
                data_[["Strike_Price", "Future_Prices", "Close", "time_diff", "Option_Type", "impliedvolatility"]])[
                "delta"]

        data_["Gamma"] = \
            optionsGreeks().gamma_options(
                data_[["Strike_Price", "Future_Prices", "Close", "time_diff", "Option_Type", "impliedvolatility", "Delta"]])[
                "gamma"]

        data_["Theta"] = \
            optionsGreeks().theta_options(
                data_[["Strike_Price", "Future_Prices", "Close", "time_diff", "Option_Type", "impliedvolatility"]])[
                "theta"]

        data_["Vega"] = \
            optionsGreeks().vega_options(
                data_[["Strike_Price", "Future_Prices", "Close", "time_diff", "Option_Type", "impliedvolatility"]])[
                "vega"]

        #
        data_["Date"] = data_["Date"].astype('object')
        # data_ = data_.drop('Date',axis =1)
        datetemp = str(data_.iat[0, 23])
        data_.iloc[:, 23] = datetemp
        task1 = data_.values
        print("task Length")
        print(len(task1))
        print("Output showing data ")
        print(data_.head(10))
        print(data_.columns)
        print(len(data_.columns))
        print("inserting Data")
        for i in range(0,len(task1)):
            print(task1[i])
            instance.insertOptionChain(conn,task1[i])

        print(data_.head(10))
        ## select Statement
        instance = database(database="NSEStock.db")
        conn = instance.create_connection()
        ## Create Database
        print("Data ouptut from sql")
        df = pd.read_sql_query("select * FROM optionchain", conn)
        print(df)



def OptionChainRatios(ticker,expiry,instrument,db):
    print("Fetching Data ")
    print(ticker,expiry,instrument,db)
    ## SQL Steps
    instance = database(database=db)
    print("1")
    ## Create Database
    instance.CreatDatabase()
    print("2")
    ## Create Connection
    conn = instance.create_connection()
    ## Create Table
    instance.CreatTable(conn, createtablescripts().sql_create_optionchainratios_table)
    print("3")
    ## Create Insert Data
    print(ticker, expiry, instrument)
    RealTimeOption = nseRealTime().OptionChainRatios(ticker, option_expiry=date(2022,1,6), instrument=instrument)
    print(RealTimeOption)
    RealTimeOption["Date"] = RealTimeOption["Date"].astype('object')
    # data_ = data_.drop('Date',axis =1)
    datetemp = str(RealTimeOption.iat[0, 42])
    RealTimeOption.iloc[:, 42] = datetemp
    print("task Length")
    print(len(RealTimeOption))
    RealTimeOption = RealTimeOption[RealTimeOption["PE.openInterest"] != 0]
    RealTimeOption = RealTimeOption.values
    print(RealTimeOption)
    print("inserting Data")
    for i in range(0, len(RealTimeOption)):
        print("Inserting Data {}".format(i))
        instance.insertOptionChainRatios(conn, RealTimeOption[i])

def stockpriceDailyYahoo(ticker, db,period = '1wk',interval = '1m'):
        print("Fetching Data ")
        print(ticker, db)
        ## SQL Steps
        instance = database(database=db)
        print("1")
        ## Create Database
        instance.CreatDatabase()
        print("2")
        ## Create Connection
        conn = instance.create_connection()
        ## Create Table
        instance.CreatTable(conn, createtablescripts().sql_create_stockrealtimeData_table)
        instance.CreatTable(conn, createtablescripts().sql_create_stockpriceindicators_table)
        print("3")

        ## Create Insert Data
        print(ticker)
        data = yf.download(tickers=ticker, period=period, interval=interval, progress=False)
        data = data.reset_index()
        try:
            data = data[["Datetime","Open", "High", "Low", "Close", "Adj Close", "Volume"]]
            print(data.head(10))
            print(data.dtypes)
            #data["Datetime"] =  data["Datetime"].replace(tzinfo=None)
            #print(data.head(10))
            data["Datetime"] = data["Datetime"].astype('object')
            print(data.head(10))
            print(data.dtypes)
            data["Datetime"] = data["Datetime"].apply(lambda x : str(x))
            print(data.head(10))
        except:
            data = data[["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]]
            data["Date"] = data["Date"].astype('object')
        # data_ = data_.drop('Date',axis =1)

        data = data[data["Volume"] != 0]
        print(data)
        data = data.values
        print("inserting Data")

        for i in range(0, len(data)):
            print("Inserting Data {}".format(i))
            print(data[i])
            try:
                instance.insertstockrealtime(conn,data[i])
            except:
                print("Error on entry : {}".format(data[i]))


def InsertstockpriceDailyFivePaisa(ticker, Exchange ='N', ExchType='C', *args,**kwargs):
    #print("Fetching Data ")
    #print(ticker, db)
    ## SQL Steps
    #instance = database(database=db)
    print("1")
    conn = kwargs['conn']
    ## Create Database
    #instance.CreatDatabase()
    print("2")
    ## Create Connection
    ## Create Table
    #instance.CreatTable(conn, createtablescripts().sql_create_stockrealtimeData_table)
    #instance.CreatTable(conn, createtablescripts().sql_create_stockpriceindicators_table)
    print("3")
    ## Create Insert Data
    client = kwargs['fivepaisainst']
    req_list_ = [{"Exch": Exchange, "ExchType": ExchType, "Symbol":ticker}]
    df_ = client.fetch_market_feed(req_list_)
    df_ = df_["Data"]
    df_ = pd.DataFrame.from_dict([df_[-1]])
    data = df_[["Time","PClose","High","Low","LastRate","TotalQty"]]
    try:
        database(database='hello').insertstockrealtime(conn, data.iloc[-1,:].values)
    except Exception as e:
        print(e)
    return data

def InsertstockpriceHistoricalFivePaisa(ticker, Exchange ='N', ExchType='C', *args,**kwargs):
    conn = kwargs['conn']
    ## Create Insert Data
    client = kwargs['fivepaisainst']
    req_list_ = [{"Exch": Exchange, "ExchType": ExchType, "Symbol":ticker}]
    df_ = client.fetch_market_feed(req_list_)
    df_ = client.historical_data(kwargs['exchange'],kwargs['market'],kwargs['scriptcode'],kwargs['timelag'],kwargs['startime'],kwargs['endtime'])
    print(df_)
    try:
        database(database='hello').insertstockrealtime(conn, df_.iloc[-1,:].values)
    except Exception as e:
        print(e)
    return df_



def  insertTechnicalIndicatorData(**kwargs):
    cursor=kwargs['conn'].cursor()
    query = 'SELECT * FROM dailystockprice ORDER BY rowid  DESC LIMIT 100'
    #query = "select * from " + kwargs['selecttablename'] + " ORDER BY  rowid  DESC LIMIT " + str(kwargs['SelectTotalRows']) + ";"
    print(query)
    data_ = pd.read_sql_query(query, kwargs['conn'])
    data_ = data_.iloc[::-1]
    print(data_)
    if len(data_) >= int(kwargs['SelectTotalRows']):
        close = data_["Close"]
        ##  Simple Moving Average
        SMA_100 = trendIndicator().SMA(close, window=100)
        SMA_100 = SMA_100.iloc[-1]
        SMA_15 = trendIndicator().SMA(close.iloc[-16:-1], window=15)
        SMA_15 = SMA_15.iloc[-1]
        SMA_7 = trendIndicator().SMA(close.iloc[-8:-1], window=7)
        SMA_7 = SMA_7.iloc[-1]

        ## Exponential Moving average
        EMA_100 = trendIndicator().expMA(close, window=100)
        EMA_100 = EMA_100.iloc[-1]
        EMA_15 = trendIndicator().expMA(close.iloc[-16:-1], window=15)
        EMA_15 = EMA_15.iloc[-1]
        EMA_7 = trendIndicator().expMA(close.iloc[-8:-1], window=7)
        EMA_7 = EMA_7.iloc[-1]

        ## VWAP indicator
        vwap_7 = volumeIndicator().vwap(data_, 7, intraday=True)
        vwap_7 = vwap_7.iloc[-1]
        vwap_15 = volumeIndicator().vwap(data_, 15, intraday=True)
        vwap_15 = vwap_15.iloc[-1]
        vwap_100 = volumeIndicator().vwap(data_, 100, intraday=True)
        vwap_100 = vwap_100.iloc[-1]

        ## RSI
        rsi_7 = ta.RSI(close, timeperiod=7)
        print(rsi_7.iloc[-1])
        rsi_7 = rsi_7.iloc[-1]
        rsi_15 = ta.RSI(close, timeperiod=15)
        print(rsi_15.iloc[-1])
        rsi_15 = rsi_15.iloc[-1]
        # rsi_100 = ta.RSI(close, timeperiod=105)
        # print(rsi_100)
        # print(rsi_100.iloc[-1])
        x = data_.values
        x = x[-1]
        x = np.append(x, [SMA_7, SMA_15, SMA_100, EMA_7, EMA_15, EMA_100, vwap_7, vwap_15, vwap_100, rsi_7, rsi_15])
        database.insertstockindicators(kwargs['con'],x)
    else:
        print("total rows less than 100")

if __name__ == "__main__":
    print(Path(__file__).parent.parent )
    path = Path(__file__).parent.parent.parent
    path = str(path) + "/Database/stockdata1.db"
    print(path)
    instance = database(database=path)
    conn = instance.create_connection()

    ##Create table
    conn = database().create_table(conn,createtablescripts().sql_create_stockpriceindicators_table)
    ## 5paisa login
    client = fivepaisa().connection()
    client.login()
    NSE = 'N'
    cash = 'C'
    scriptcode = 1594
    window = '10m'
    starttime = '2021-12-15',
    endtime = '2022-01-15'

    InsertstockpriceHistoricalFivePaisa(ticker='INFY', Exchange='N', ExchType='C', conn=conn, fivepaisainst=client,
                                          selecttablename='dailystockprice', selectColumNname='Datetime',
                                          SelectTotalRows=100,startime=starttime,endtime=endtime)

    #data = stockpriceDailyFivePaisa(ticker="INFY",db=path)
    #instance = database(database=db)
    #instance.insertstockrealtime(conn, data.iloc[-1,:].values)
    print("Insert Completed")

