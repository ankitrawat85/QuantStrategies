# Import datetime
from datetime import date
# Import datetime
from datetime import date
# Import get_history function from nsepy module
from nsepy import get_history
# Import get_history function from nsepy module
# Data manipulation
import numpy as np
import pandas as pd
import datetime
# To calculate Greeks
import mibian
import scipy


# For Plotting
import matplotlib.pyplot as plt

## personal code import
from self.OptionsStrategy.optionsvaluation.optionpricing import volatility

import warnings
warnings.simplefilter("ignore")

class DispersionStrategy():

    def __init__(self):
        pass

    def datapulloptions(self):

        BankNifty_Opt = get_history(symbol="BANKNIFTY",
                                    start=date(2021,11, 1),
                                    end=date(2021,11, 28),
                                    futures=False,
                                    index=True,
                                    expiry_date=date(2021,12,30),
                                    option_type='CE',
                                    strike_price=36000,
                                    )

        BankNifty_Opt.to_csv("BankNifty_Opt.csv")
        return DispersionStrategy().time_to_expiry(BankNifty_Opt.reset_index())

    def datapullfuture(self):
        nifty_fut = get_history(symbol='BANKNIFTY',
                                start=date(2021,11,1),
                                end=date(2021,11,29),
                                futures=True,
                                index=True,
                                expiry_date=date(2021,12,30))

        nifty_fut.to_csv("future.csv")
        return nifty_fut


    def time_to_expiry(self,opt):
        opt['time_diff'] = (opt.Expiry - opt.Date).dt.days
       #opt['time_diff'] = (opt.Expiry - opt.Date).dt.days / 365
        return opt

    def atm_strike_price(self,opt):
        opt['strike_distance'] = np.abs(opt.futures_price - opt['Strike Price'])
        df = opt.groupby(['Date'])['strike_distance'].min().to_frame()
        df.index.column = 0
        opt = pd.merge(opt, df)
        opt = opt[(np.abs(opt.futures_price - opt['Strike Price'])
                   == opt.strike_distance)]
        opt = opt.drop('strike_distance', 1)
        opt = opt.drop_duplicates(subset=['Date', 'Expiry', 'Option Type'])
        return  opt

    def daily_pnl(self,opt, full_opt):
        opt['next_day_close'] = np.nan
        opt.sort_values('Date', inplace=True, ascending=True)
        print("inside PNL ")
        print(opt)
        opt.to_csv("pnl1.csv")
        for i in range(0, len(opt) - 2):
            print(i)
            strike_price = opt.iloc[i]['Strike Price']
            trade_date = opt.iloc[i]['Date']
            print(trade_date)
            print(opt[(opt.Date > trade_date)])
            print("out")
            try:
                next_trading_date = opt[(opt.Date > trade_date)
                                        & (opt.Date <= trade_date + datetime.timedelta(days=20)
                                           )].iloc[0]['Date']
                print(next_trading_date)
            except:
                pass
            option_type = opt.iloc[i]['Option Type']

            if opt.iloc[i]['time_diff'] != 0:
                opt.iloc[i, opt.columns.get_loc('next_day_close')] = \
                full_opt[(full_opt['Strike Price'] == strike_price) &
                         (full_opt['Date'] == next_trading_date) &
                         (full_opt['Option Type']
                          == option_type)
                         ].iloc[0]['Close']
            else:
                # This is done because on expiry day the next day price doesn't exists
                opt.iloc[i, opt.columns.get_loc(
                    'next_day_close')] = opt.iloc[i]['Close']

        opt['daily_straddle_pnl'] = opt.next_day_close - opt.Close
        return opt

    def implied_volatility_options(self,opt):
        opt['impliedvolatility'] = np.nan
        #opt = opt.iloc[:3]
        opt.loc[(opt.time_diff == 0), 'time_diff'] = 0.0000001
        for i in range(0, len(opt)):
            if opt.iloc[i]['Option Type'] == 'CE':
                opt.iloc[i, opt.columns.get_loc('impliedvolatility')] = mibian.BS([opt.iloc[i]['futures_price'],
                                                                    opt.iloc[i]['Strike Price'],
                                                                    0,
                                                                    opt.iloc[i]['time_diff']],
                                                                   callPrice=opt.iloc[i]['Close']
                                                                   ).impliedVolatility
            else:
                opt.iloc[i, opt.columns.get_loc('impliedvolatility')] = mibian.BS([opt.iloc[i]['futures_price'],
                                                                    opt.iloc[i]['Strike Price'],
                                                                    0,
                                                                    opt.iloc[i]['time_diff']],
                                                                   putPrice=opt.iloc[i]['Close']
                                                                   ).impliedVolatility
        return opt

    def delta_options(self,opt):
        opt['delta'] = np.nan

        #opt = opt.iloc[:3]
        for i in range(0, len(opt)):
            if opt.iloc[i]['Option Type'] == 'CE':
                opt.iloc[i, opt.columns.get_loc('delta')] = mibian.BS([opt.iloc[i]['futures_price'],
                                                                       opt.iloc[i]['Strike Price'],
                                                                       0,
                                                                       opt.iloc[i]['time_diff']],
                                                                      volatility=opt.iloc[i]['impliedvolatility']
                                                                      ).callDelta
            else:
                opt.iloc[i, opt.columns.get_loc('delta')] = mibian.BS([opt.iloc[i]['futures_price'],
                                                                       opt.iloc[i]['Strike Price'],
                                                                       0,
                                                                       opt.iloc[i]['time_diff']],
                                                                      volatility=opt.iloc[i]['impliedvolatility']
                                                                      ).putDelta
        return opt

    def gamma_options(self, opt):
        opt['gamma'] = np.nan
        # opt = opt.iloc[:3]
        for i in range(0, len(opt)):
            if opt.iloc[i]['Option Type'] == 'CE':
                opt.iloc[i, opt.columns.get_loc('gamma')] = mibian.BS([opt.iloc[i]['futures_price'],
                                                                       opt.iloc[i]['Strike Price'],
                                                                       0,
                                                                       opt.iloc[i]['time_diff']],
                                                                      volatility=opt.iloc[i]['impliedvolatility']
                                                                      ).gamma
            else:
                opt.iloc[i, opt.columns.get_loc('gamma')] = mibian.BS([opt.iloc[i]['futures_price'],
                                                                       opt.iloc[i]['Strike Price'],
                                                                       0,
                                                                       opt.iloc[i]['time_diff']],
                                                                      volatility=opt.iloc[i]['impliedvolatility']
                                                                      ).gamma
        return opt
    def theta_options(self, opt):
        opt['theta'] = np.nan
        # opt = opt.iloc[:3]
        for i in range(0, len(opt)):
            if opt.iloc[i]['Option Type'] == 'CE':
                opt.iloc[i, opt.columns.get_loc('theta')] = mibian.BS([opt.iloc[i]['futures_price'],
                                                                       opt.iloc[i]['Strike Price'],
                                                                       0,
                                                                       opt.iloc[i]['time_diff']],
                                                                      volatility=opt.iloc[i]['impliedvolatility']
                                                                      ).putTheta
            else:
                opt.iloc[i, opt.columns.get_loc('theta')] = mibian.BS([opt.iloc[i]['futures_price'],
                                                                       opt.iloc[i]['Strike Price'],
                                                                       0,
                                                                       opt.iloc[i]['time_diff']],
                                                                      volatility=opt.iloc[i]['impliedvolatility']
                                                                      ).callTheta
        return opt
    def vega_options(self, opt):
        opt['vega'] = np.nan
        for i in range(0, len(opt)):
            if opt.iloc[i]['Option Type'] == 'CE':
                opt.iloc[i, opt.columns.get_loc('vega')] = mibian.BS([opt.iloc[i]['futures_price'],
                                                                       opt.iloc[i]['Strike Price'],
                                                                       0,
                                                                       opt.iloc[i]['time_diff']],
                                                                      volatility=opt.iloc[i]['impliedvolatility']
                                                                      ).vega
            else:
                opt.iloc[i, opt.columns.get_loc('vega')] = mibian.BS([opt.iloc[i]['futures_price'],
                                                                       opt.iloc[i]['Strike Price'],
                                                                       0,
                                                                       opt.iloc[i]['time_diff']],
                                                                      volatility=opt.iloc[i]['impliedvolatility']
                                                                      ).vega
        return opt



    def implied_dirty_correlation(self,index,const1,const1_wt,const2,const2_wt,const3,const3_wt,const4,const4_wt,const5,const5_wt):
        print("correlation--->")
        index_IV = index.groupby(['Date'])['impliedvolatility'].mean().to_frame()
        const1_IV = const1.groupby(['Date'])['impliedvolatility'].mean().to_frame()
        print(const1_IV)
        const2_IV = const2.groupby(['Date'])['impliedvolatility'].mean().to_frame()
        print(const2_IV)
        const3_IV = const3.groupby(['Date'])['impliedvolatility'].mean().to_frame()
        print(const3_IV)
        const4_IV = const4.groupby(['Date'])['impliedvolatility'].mean().to_frame()
        print(const4_IV)
        const5_IV = const5.groupby(['Date'])['impliedvolatility'].mean().to_frame()
        print(const5_IV)
        print("cor finish")


        weighted_average_constituents_vol = const1_IV * const1_wt \
                                            + const2_IV * const2_wt \
                                            +  const3_IV * const3_wt \
                                            +  const4_IV * const4_wt \
                                            +  const5_IV * const5_wt


        return (index_IV / weighted_average_constituents_vol) ** 2

##  Data formating from csv
    def process(self,df_merge):
    #def process(self,ce,pe,future):
        '''df_optins_ce  = pd.read_csv(ce)
        df_optins_pe  = pd.read_csv(pe)
        df_future  = pd.read_csv(future)
        df_future = df_future.rename(columns= {"Close" : "futures_price"})
        df_ = pd.concat([df_optins_ce,df_optins_pe])
        #df_ = df_.sort_values(["Date","Option Type"])
        df_.Date  = pd.to_datetime(df_.Date)
        df_.Expiry = pd.to_datetime(df_.Expiry)
        df_1 = df_[["Date","Expiry","Option Type","Strike Price","Close"]]
        df_1.Date  = pd.to_datetime(df_1.Date)
        df_f = df_future[["Date","futures_price"]]
        df_f.Date  = pd.to_datetime(df_f.Date)
        df_merge = df_.merge(df_f,left_on="Date",right_on="Date")
        #print(df_merge)
        df_merge.to_csv("df_merge.csv")'''

        df_merge.Date = pd.to_datetime(df_merge.Date)
        df_merge.Expiry = pd.to_datetime(df_merge.Expiry)
        banknifty = DispersionStrategy().time_to_expiry(df_merge)
        full_BankNifty_opt = banknifty
        print("Initial Setup -->")
        #rint(banknifty)
        #BankNifty_Opt = volatility("SABR", banknifty)
        print("SABR volatility ----> ")
        #BankNifty_Opt = DispersionStrategy().delta_options(banknifty)
        BankNifty_Opt = DispersionStrategy().atm_strike_price(banknifty)
        print("atm done")
        BankNifty_Opt = DispersionStrategy().implied_volatility_options(BankNifty_Opt)
        print("implied vol done")
        ## Delta
        BankNifty_Opt = DispersionStrategy().delta_options(BankNifty_Opt)
        print("delta done")
        BankNifty_Opt = DispersionStrategy().theta_options(BankNifty_Opt)
        print("theta done")
        BankNifty_Opt = DispersionStrategy().gamma_options(BankNifty_Opt)
        print("gamma done")
        BankNifty_Opt = DispersionStrategy().vega_options(BankNifty_Opt)
        print("vega done")
        BankNifty_Opt = DispersionStrategy().daily_pnl(BankNifty_Opt, full_BankNifty_opt)
        print("PNL done")
        return BankNifty_Opt

    def trading_signal(self,df,expiry_df):
        df.index.column = 0
        lookback = 10
        # Moving Average
        df['moving_average'] = df['implied_correlation'].rolling(lookback).mean()
        # Moving Standard Deviation
        df['moving_std_dev'] = df['implied_correlation'].rolling(lookback).std()

        df['upper_band'] = df.moving_average + 0.5 * df.moving_std_dev
        df['lower_band'] = df.moving_average - 0.5 * df.moving_std_dev

        df['long_entry'] = df.implied_correlation < df.lower_band
        df['long_exit'] = df.implied_correlation >= df.moving_average

        df['short_entry'] = df.implied_correlation > df.upper_band
        df['short_exit'] = df.implied_correlation <= df.moving_average

        df['positions_long'] = np.nan
        df.loc[df.long_entry, 'positions_long'] = 1
        df.loc[df.long_exit, 'positions_long'] = 0

        expiry_dates = expiry_df.Expiry.unique()
        df.loc[df.index.isin(expiry_dates), 'positions_short'] = 0

        df['positions_short'] = np.nan
        df.loc[df.short_entry, 'positions_short'] = -1
        df.loc[df.short_exit, 'positions_short'] = 0

        df.loc[df.index.isin(expiry_dates), 'positions_short'] = 0

        df = df.fillna(method='ffill')

        df['positions'] = df.positions_long + df.positions_short
        df[["moving_average","implied_correlation"]].plot()
        plt.show()
        return df

    def strategy_pnl(self,opt, df):
        opt = pd.merge(opt, df[['positions']], left_on='Date',
                       right_index=True, how='left')
        opt['strategy_pnl'] = opt.positions * opt.daily_straddle_pnl
        return opt

data_  = pd.read_csv("futuredatamerge.csv")
print(data_.columns)
data_.rename(columns = {"Future_Prices":"futures_price"}, inplace = True )
print ("Processing  started ->")
df_sbin = DispersionStrategy().process(data_[data_["Symbol"] =="SBIN"])
df_index = DispersionStrategy().process(data_[data_["Symbol"] =="BANKNIFTY"])
df_hdfc = DispersionStrategy().process(data_[data_["Symbol"] =="HDFCBANK"])
df_icici = DispersionStrategy().process(data_[data_["Symbol"] =="ICICIBANK"])
df_axis = DispersionStrategy().process(data_[data_["Symbol"] =="AXISBANK"])
print(data_[data_["Symbol"] =="SBIN"])
df_sbin = DispersionStrategy().process(data_[data_["Symbol"] =="SBIN"])
print(data_[data_["Symbol"] =="AXISBANK"])
df_kotak = DispersionStrategy().process(data_[data_["Symbol"] =="AXISBANK"])


'''  
print ("Index started ->")
df_index = DispersionStrategy().process("OPTIDX_BANKNIFTY_CE.csv","OPTIDX_BANKNIFTY_PE.csv","index_future.csv")
print(df_index.head(2))
print ("HDFC started ->")
df_hdfc = DispersionStrategy().process("OPTSTK_HDFCBANK_CE.csv","OPTSTK_HDFCBANK_PE.csv","FUTSTK_HDFCBANK.csv")
print(pd.DataFrame(df_hdfc).to_csv("hdfc_final.csv"))
print(df_hdfc.head(2))
print ("kotak started ->")
df_kotak = DispersionStrategy().process("OPTSTK_KOTAKBANK_CE.csv","OPTSTK_KOTAKBANK_PE.csv","FUTSTK_KOTAKBANK.csv")
print(df_kotak.head(2))
print ("axis started ->")
df_axis = DispersionStrategy().process("OPTSTK_AXISBANK_CE.csv","OPTSTK_AXISBANK_PE.csv","FUTSTK_AXISBANK.csv")
print(df_axis.head(2))
print ("SBIN started ->")
df_sbin = DispersionStrategy().process("OPTSTK_SBIN_CE.csv","OPTSTK_SBIN_PE.csv","FUTSTK_SBIN.csv")
print(df_sbin.head(2))
print ("ICICI started ->")
df_icici = DispersionStrategy().process("OPTSTK_ICICIBANK_CE.csv","OPTSTK_ICICIBANK_PE.csv","ICICIBANK_future.csv")
print(df_icici.head(2))

'''

print("Corelation---->")
df_corr = DispersionStrategy().implied_dirty_correlation(df_index,df_hdfc,0.333,df_kotak,0.173,df_kotak,0.123,df_sbin,0.102,df_icici,0.08)
print("corr->")
print(df_corr)
df_corr = df_corr.rename(columns={'impliedvolatility': 'implied_correlation'})
df_corr.plot()
plt.grid()
plt.show()
print("Trading Signal .......generation")
df_trading_signal = DispersionStrategy().trading_signal(df_corr,df_hdfc)
df_index = DispersionStrategy().strategy_pnl(df_index, df_trading_signal)
df_trading_signal.positions *= -1
df_trading_signal.to_csv("df_trading_signal.csv")
df_hdfc = DispersionStrategy().strategy_pnl(df_hdfc, df_trading_signal)
df_kotak = DispersionStrategy().strategy_pnl(df_kotak, df_trading_signal)
df_axis = DispersionStrategy().strategy_pnl(df_axis, df_trading_signal)
df_sbin = DispersionStrategy().strategy_pnl(df_sbin, df_trading_signal)
df_icici = DispersionStrategy().strategy_pnl(df_icici, df_trading_signal)

index_Ret = df_index.groupby(['Date'])['strategy_pnl'].sum().to_frame()
HDFCBANK_Ret = df_hdfc.groupby(['Date'])['strategy_pnl'].sum().to_frame()
kotak_Ret = df_kotak.groupby(['Date'])['strategy_pnl'].sum().to_frame()
axis_Ret = df_axis.groupby(['Date'])['strategy_pnl'].sum().to_frame()
SBIN_Ret = df_sbin.groupby(['Date'])['strategy_pnl'].sum().to_frame()
icici_Ret = df_icici.groupby(['Date'])['strategy_pnl'].sum().to_frame()
index_Ret.tail()
print ("Weightage .....")

def weightage_strategy_pnl():
    HDFCBANK_Wt = 0.333
    HDFCBANK_Lot_Size = 500
    ICICIBANK_Wt = 0.173
    ICICIBANK_Lot_Size = 2500
    KOTAKBANK_Wt = 0.123
    KOTAKBANK_Lot_Size = 800
    SBIN_Wt = 0.102
    SBIN_Lot_Size = 3000
    AXISBANK_Wt = 0.08
    AXISBANK_Lot_Size = 1200
    BankNifty_Wt = 1.0
    BankNifty_Lot_Size = 40
    ###
    strategy_pnl = HDFCBANK_Ret.strategy_pnl * HDFCBANK_Lot_Size * HDFCBANK_Wt + \
        SBIN_Ret.strategy_pnl * SBIN_Lot_Size * SBIN_Wt + \
        axis_Ret.strategy_pnl * AXISBANK_Lot_Size * AXISBANK_Wt + \
        kotak_Ret.strategy_pnl * KOTAKBANK_Lot_Size * KOTAKBANK_Wt + \
        icici_Ret.strategy_pnl * ICICIBANK_Lot_Size * ICICIBANK_Wt + \
        index_Ret.strategy_pnl * BankNifty_Lot_Size * BankNifty_Wt

    print(strategy_pnl.to_csv("final_PNL.csv"))
    print(strategy_pnl)
    return strategy_pnl.cumsum().shift(1)

print("Plot generation....")
weightage_strategy_pnl().plot(figsize=(10, 5))
plt.ylabel("Strategy PnL")
plt.show()
# completed