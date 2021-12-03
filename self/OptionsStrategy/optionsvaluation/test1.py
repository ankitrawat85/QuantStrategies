import pandas as pd
import numpy as np
desired_width = 320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns', 20)

import mibian
def implied_volatility_options(opt):
    opt['IV'] = np.nan
    opt = opt.iloc[:3]
    opt.loc[(opt.time_to_expiry == 0), 'time_to_expiry'] = 0.0000001
    for i in range(0, len(opt)):
        if opt.iloc[i]['Option Type'] == 'CE':
            opt.iloc[i, opt.columns.get_loc('IV')] = mibian.BS([opt.iloc[i]['futures_price'],
                                                                opt.iloc[i]['Strike Price'],
                                                                0,
                                                                opt.iloc[i]['time_to_expiry']],
                                                               callPrice=opt.iloc[i]['Close']
                                                               ).impliedVolatility
        else:
            opt.iloc[i, opt.columns.get_loc('IV')] = mibian.BS([opt.iloc[i]['futures_price'],
                                                                opt.iloc[i]['Strike Price'],
                                                                0,
                                                                opt.iloc[i]['time_to_expiry']],
                                                               putPrice=opt.iloc[i]['Close']
                                                               ).impliedVolatility
    return opt


def time_to_expiry(opt):
    opt['time_to_expiry'] = (opt.Expiry - opt.Date).dt.days
    return opt

def implied_volatility_options(opt):
    opt['IV'] = np.nan
    opt.loc[(opt.time_to_expiry == 0), 'time_to_expiry'] = 0.0000001
    for i in range(0, len(opt)):
        if opt.iloc[i]['Option Type'] == 'CE':
            opt.iloc[i, opt.columns.get_loc('IV')] = mibian.BS([opt.iloc[i]['futures_price'],
                                                                opt.iloc[i]['Strike Price'],
                                                                0,
                                                                opt.iloc[i]['time_to_expiry']],
                                                               callPrice=opt.iloc[i]['Close']
                                                               ).impliedVolatility
        else:
            opt.iloc[i, opt.columns.get_loc('IV')] = mibian.BS([opt.iloc[i]['futures_price'],
                                                                opt.iloc[i]['Strike Price'],
                                                                0,
                                                                opt.iloc[i]['time_to_expiry']],
                                                               putPrice=opt.iloc[i]['Close']
                                                               ).impliedVolatility
    return opt

BankNifty_Opt = pd.read_csv("df_merge.csv")
print('Data load')
print(BankNifty_Opt)
BankNifty_Opt["Expiry"]= pd.to_datetime(BankNifty_Opt["Expiry"],format = '%d/%m/%Y')
BankNifty_Opt["Date"]= pd.to_datetime(BankNifty_Opt["Date"],format = '%d/%m/%y')
print(BankNifty_Opt)
BankNifty_Opt = BankNifty_Opt[BankNifty_Opt["Date"]=="2021-11-01"]
BankNifty_Opt  = time_to_expiry(BankNifty_Opt)
print(BankNifty_Opt)
print(BankNifty_Opt[BankNifty_Opt["Date"]=="2021-11-1"])
BankNifty_Opt = BankNifty_Opt[BankNifty_Opt["Date"]=="2021-11-1"]

put_df_option = BankNifty_Opt[(BankNifty_Opt["Strike Price"] <= BankNifty_Opt["futures_price"]) & (BankNifty_Opt["Option Type"] == "PE")]
put_df_option= implied_volatility_options(put_df_option)
put_df_option = put_df_option[["Date","Expiry","Option Type","Strike Price","Open","High","Low","Settle Price","Close","futures_price","time_to_expiry","IV"]]
print(put_df_option)

call_df_option = BankNifty_Opt[(BankNifty_Opt["Strike Price"] >= BankNifty_Opt["futures_price"]) & (BankNifty_Opt["Option Type"] == "CE")]
call_df_option= implied_volatility_options(call_df_option)
call_df_option = call_df_option[["Date","Expiry","Option Type","Strike Price","Open","High","Low","Close","Settle Price","futures_price","time_to_expiry","IV"]]
print(call_df_option)

import matplotlib.pyplot as plt
df = pd.concat([put_df_option[["Date","Expiry","Strike Price","IV"]],call_df_option[["Expiry","Strike Price","IV"]]])
#df["IV"] = df["IV"]/100
c = df .sort_values(by = "Strike Price")
print(c)
plt.scatter(c['Strike Price'], c ['IV'], alpha=0.8, c='g', marker='s', label='Market')
plt.show()

