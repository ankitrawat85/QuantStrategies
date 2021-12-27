import sqlite3
from sqlite3 import Error
import numpy as np
import pandas as pd

from self.OptionsStrategy.NSEDataPull.NseRealtimeData import nseRealTime
from self.OptionsStrategy.optionsvaluation.optionpricing import  Vol
from self.OptionsStrategy.optionsvaluation.optionpricing import optionsGreeks
import datetime
import itertools

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
                                            lib_impliedVolatility float,
                                            lastPrice float,
                                            change float,
                                            pChange float,
                                            totalBuyQuantity int,
                                            totalSellQuantity int,
                                            bidQty int,
                                            bidprice int,
                                            askQty float,
                                            askPrice float,
                                            Future_Prices float,
                                            Symbol text,
                                            INSTRUMENT text,
                                            Close  float, 
                                            Option_Type text, Date datetime NOT NULL,
                                            impliedvolatility  float,
                                            Delta float,
                                            Gamma float,
                                            Theta float,
                                            Vega float,
                                            time_diff float
                                             ); """
        self.sql_create_option_table = None
        self.sql_create_stock_table = None


class database:

    def __init__(self, database):
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
        sql = ''' INSERT INTO Optionchain(
                  Strike_Price,Expiry,underlying,identifier,OPEN_INT,changeinOpenInterest,pchangeinOpenInterest,
                  totalTradedVolume,lib_impliedVolatility,lastPrice,change, 
                  pChange, totalBuyQuantity, totalSellQuantity, bidQty, bidprice,
                  askQty,askPrice,Future_Prices,Symbol,INSTRUMENT,Close,Option_Type,Date,time_diff,impliedvolatility,Delta,Gamma,Theta,Vega) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
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

    def insertstock(conn, task):
        sql = ''' INSERT INTO Optionchain(
                  Strike_Price,Expiry,underlying,identifier,OPEN_INT,changeinOpenInterest,pchangeinOpenInterest,
                  totalTradedVolume,lib_impliedVolatility,lastPrice,change, 
                  pChange, totalBuyQuantity, totalSellQuantity, bidQty, bidprice,
                  askQty,askPrice,Future_Prices,Symbol,INSTRUMENT,Close,Option_Type,Date) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
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
        # create tables
        if conn is not None:
            print(conn)
            # create projects table
            print("Inside CreatTable")
            print(createtablescripts().sql_create_option_table)
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

if __name__ == '__main__':

    RealTimeOption = nseRealTime().OptionChain("INFY", option_expiry=datetime.date(2021, 12, 30),instrument="OPIDX")
    RealTimeOption = RealTimeOption[RealTimeOption["OPEN_INT"] != 0]
    RealTimeOption = RealTimeOption.dropna(axis=0)
    data_ = RealTimeOption
    data_ = data_.rename(columns = {"Strike Price" : "Strike_Price","Future Prices":"Future_Prices","Option Type":"Option_Type"})


    ##  Volatility and Greeks calculation
    data_["time_diff"] = optionsGreeks().time_to_expiry(data_[["Expiry", "Date"]])["time_diff"]
    data_["impliedvolatility"] = \
        optionsGreeks().implied_volatility_options(
            data_[["Strike_Price", "Future_Prices", "Close", "time_diff", "Option_Type"]])[
            "impliedvolatility"]


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
    print(data_.columns)

    data_["Date"] = data_["Date"].astype('object')
    # data_ = data_.drop('Date',axis =1)
    datetemp = str(data_.iat[0, 23])
    data_.iloc[:, 23] = datetemp
    task1 = data_.values
    print("task Length")
    print(len(task1))
   
    ## SQL Steps
    instance = database(database="StockTrading.db")
    ## Create Database
    instance.CreatDatabase()

    ## Create Connection
    conn = instance.create_connection()
    ## Create Table
    instance.CreatTable(conn, createtablescripts().sql_create_optionchain_table)
    ## Create Insert Data
    
    for i in range(0,len(task1)):
        print(i)
        instance.insertOptionChain(conn,task1[i])


    ## select Statement
    #instance = database(database="StockTrading9.db")
    #conn = instance.create_connection()
    ## Create Database
    df = pd.read_sql_query("select Date,Expiry,Strike_Price,identifier,Open_int,lib_impliedVolatility,impliedvolatility,Delta,Gamma,Theta,Vega,Option_Type,time_diff,Future_Prices,Close FROM optionchain", conn)
    print(df)
