'''
Gamma Sclaping Strategy
--
et's determine the data and the steps required to implement this strategy.
ATM strike price
Buy a straddle (Long ATM Call + Long ATM Put)
Delta of the straddle
Gamma scalping strategy 6. Nifty rises: the straddle position gets positive Delta (adjustment: sell Nifty futures) 6. Nifty falls: the straddle position gets negative Delta (adjustment: buy Nifty futures)
Let's get started!!!
'''
import pandas as pd
import matplotlib.pyplot as plt
from self.OptionsStrategy.options_DispersionStrategy import DispersionStrategy
def time_to_expiry(opt):
    opt.Expiry = pd.to_datetime(opt.Expiry)
    opt.Date = pd.to_datetime(opt.Date)
    opt['time_diff']= (opt.Expiry - opt.Date).dt.days
    return opt

data_ = pd.read_csv("futuredatamerge1.csv")
data_.Expiry = pd.to_datetime(data_.Expiry)
data_.Date = pd.to_datetime(data_.Date)
data_ = data_.rename(columns = {"Future_Prices":"futures_price"})
data_  = data_ [data_["Symbol"] == "BANKNIFTY"]
banknifty = DispersionStrategy().time_to_expiry(data_)
banknifty = banknifty[banknifty["OPEN_INT"] != 0]
print(banknifty["Expiry"].unique())
banknifty = banknifty[banknifty["Expiry"] == "2022-01-27"]
#banknifty = banknifty[banknifty["Date"] == "2021-10-1"]

full_BankNifty_opt = banknifty
BankNifty_Opt = DispersionStrategy().atm_strike_price(banknifty)
atm_strike_price = BankNifty_Opt[BankNifty_Opt["Date"] == min(BankNifty_Opt.Date)]["Strike Price"]
atm_strike_price = (atm_strike_price.head(1).values[0])
print ("ATM strike price :  {}".format(atm_strike_price))
##
put_df_option = full_BankNifty_opt[(full_BankNifty_opt["Strike Price"] <= atm_strike_price) & (full_BankNifty_opt["Option Type"] == "PE")]
call_df_option = full_BankNifty_opt[(full_BankNifty_opt["Strike Price"] >= atm_strike_price) & (full_BankNifty_opt["Option Type"] == "CE")]
Nifty_Opt = pd.concat([put_df_option,call_df_option])
print(Nifty_Opt)
##
#Nifty_Opt = full_BankNifty_opt[full_BankNifty_opt['Strike Price'] == atm_strike_price]
Nifty_Opt = DispersionStrategy().implied_volatility_options(Nifty_Opt)
## Delta
Nifty_Opt = DispersionStrategy().delta_options(Nifty_Opt)
print("delta done")
Nifty_Opt = DispersionStrategy().theta_options(Nifty_Opt)
print("theta done")
Nifty_Opt = DispersionStrategy().gamma_options(Nifty_Opt)
print("gamma done")
Nifty_Opt = DispersionStrategy().vega_options(Nifty_Opt)
print("vega done")
print(Nifty_Opt[Nifty_Opt["Date"] == "2021-12-09"])
x = Nifty_Opt[Nifty_Opt["Date"] == "2021-12-09"]
plt.scatter(x ['Strike Price'],x ['impliedvolatility'], alpha=0.8, c='g', marker='s', label='Market')
plt.show()
'''Nifty_Lot_Size = 75
Nifty_delta = Nifty_Opt.groupby(['Date'])['delta'].sum().to_frame() * Nifty_Lot_Size
Nifty_delta.plot(figsize=(10,5))
plt.show()

def daily_pnl(opt):
    opt['daily_pnl'] = opt.Close - opt.Close.shift(1)
    print("insude")
    print( opt['daily_pnl'])
    return opt

Nifty_CE = Nifty_Opt[Nifty_Opt['Option Type'] == 'CE'][['Date','Close']]
Nifty_PE = Nifty_Opt[Nifty_Opt['Option Type'] == 'PE'][['Date','Close']]

Nifty_PE = Nifty_PE.set_index('Date')
Nifty_CE = Nifty_CE.set_index('Date')

Nifty_CE = daily_pnl(Nifty_CE)
Nifty_PE = daily_pnl(Nifty_PE)

Nifty_CE.daily_pnl = Nifty_CE.daily_pnl * Nifty_Lot_Size
Nifty_PE.daily_pnl = Nifty_PE.daily_pnl * Nifty_Lot_Size

straddle_pnl = Nifty_CE.daily_pnl + Nifty_PE.daily_pnl
straddle_pnl.cumsum().plot(figsize=(10,5))
plt.ylabel("Straddle PnL")
plt.show()
print("Strandle PNL  {}".format(straddle_pnl))

Nifty_Fut = Nifty_Opt.groupby(['Date'])['futures_price'].mean().to_frame()
Nifty_Fut = Nifty_Fut.rename(columns={'futures_price': 'Close'})
Nifty_Fut['quantity'] = -Nifty_delta // 5 * 5
Nifty_Fut = daily_pnl(Nifty_Fut)
Nifty_Fut.daily_pnl = Nifty_Fut.daily_pnl * Nifty_Fut.quantity.shift(1)
Nifty_Fut.daily_pnl.cumsum().plot(figsize=(10,5))
plt.ylabel("Nifty futures PnL")
plt.show()


strategy_pnl = Nifty_CE.daily_pnl + Nifty_PE.daily_pnl + Nifty_Fut.daily_pnl
strategy_pnl.cumsum().plot(figsize=(10,5))
plt.ylabel("Strategy PnL")
plt.grid()
plt.show()
'''