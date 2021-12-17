'''
1. Calculate Greeks
2. Calculate Black scholes implied volatility
3. Calculate SABR  Volaitliy
'''
import pandas as pd
import matplotlib.pyplot as plt
from self.OptionsStrategy.options_DispersionStrategy import DispersionStrategy
import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq
import matplotlib.pylab as plt
import datetime as dt
from scipy.optimize import least_squares
beta = 0.8
def SABR(F, K, T, alpha, beta, rho, nu):
    X = K
    # if K is at-the-money-forward
    if abs(F - K) < 1e-12:
        numer1 = (((1 - beta)**2)/24)*alpha*alpha/(F**(2 - 2*beta))
        numer2 = 0.25*rho*beta*nu*alpha/(F**(1 - beta))
        numer3 = ((2 - 3*rho*rho)/24)*nu*nu
        VolAtm = alpha*(1 + (numer1 + numer2 + numer3)*T)/(F**(1-beta))
        sabrsigma = VolAtm
    else:
        z = (nu/alpha)*((F*X)**(0.5*(1-beta)))*np.log(F/X)
        zhi = np.log((((1 - 2*rho*z + z*z)**0.5) + z - rho)/(1 - rho))
        numer1 = (((1 - beta)**2)/24)*((alpha*alpha)/((F*X)**(1 - beta)))
        numer2 = 0.25*rho*beta*nu*alpha/((F*X)**((1 - beta)/2))
        numer3 = ((2 - 3*rho*rho)/24)*nu*nu
        numer = alpha*(1 + (numer1 + numer2 + numer3)*T)*z
        denom1 = ((1 - beta)**2/24)*(np.log(F/X))**2
        denom2 = (((1 - beta)**4)/1920)*((np.log(F/X))**4)
        denom = ((F*X)**((1 - beta)/2))*(1 + denom1 + denom2)*zhi
        sabrsigma = numer/denom

    return sabrsigma

def sabrcalibration(x, strikes, vols, F, T):
    err = 0.0
    for i, vol in enumerate(vols):
        err += (vol - SABR(F, strikes[i], T,
                           x[0], beta, x[1], x[2]))**2

    return err


def time_to_expiry(opt):
    opt.Expiry = pd.to_datetime(opt.Expiry)
    opt.Date = pd.to_datetime(opt.Date)
    opt['time_diff']= (opt.Expiry - opt.Date).dt.days
    return opt

def VolGreeksProcessing(df_):
    final_ = pd.DataFrame()
    data_ = df_
    data_.Expiry = pd.to_datetime(data_.Expiry)
    data_.Date = pd.to_datetime(data_.Date)
    data_ = data_.rename(columns = {"Future_Prices":"futures_price"})
    data_ = DispersionStrategy().time_to_expiry(data_)
    data_ = data_[data_["OPEN_INT"] != 0]
    for col in data_["Symbol"].unique():
        data_symbol  = data_ [data_["Symbol"] == col]
        print(data_symbol)
        for i in data_symbol["Expiry"].unique():
            i = str(i).split('T')[0]
            print(i,col)
            for tradedate in data_symbol[data_symbol["Expiry"] == i]["Date"].unique():
                print(i,col,tradedate)
                tradedate = str(tradedate).split('T')[0]
                banknifty = data_symbol[(data_symbol["Expiry"] == i )& (data_symbol["Date"] == tradedate)]
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
                print("Nifty_Opt____")
                print(Nifty_Opt["Date"])
                print(Nifty_Opt["Date"].unique())
                tradedate = str(tradedate).split('T')[0]
                print("Trade Date ->")
                output = Nifty_Opt[Nifty_Opt["Date"] == tradedate]
                output = output.reset_index()
                print("Start-->>")
                print(output)
                initialGuess = [0.02, 0.2, 0.1]
                future_price = np.array(output["futures_price"])[0]
                time_diff = np.array(output["time_diff"])[0]
                print(time_diff)
                print("Future price : {} and time diff {}".format(future_price,time_diff))
                res = least_squares(lambda x: sabrcalibration(x,
                                                                  output['Strike Price'],
                                                                  output['impliedvolatility'],future_price,
                                                                  time_diff),
                                        initialGuess)
                alpha = res.x[0]
                rho = res.x[1]
                nu = res.x[2]
                print('Calibrated SABR model parameters: alpha = %.3f, beta = %.1f, rho = %.3f, nu = %.3f' % (alpha, beta, rho, nu))
                print ("Output ")
                print(output)
                output['sabrsigma'] = output.apply(lambda x : SABR(future_price, x['Strike Price'], time_diff, alpha, beta, rho, nu), axis = 1)
                print(output[["Strike Price","impliedvolatility","sabrsigma"]])
                plt.figure(figsize = (12, 7))
                plt.scatter(output['Strike Price'],output['impliedvolatility'], alpha = 0.8, c = 'g' ,marker = 's', label = 'Market')
                plt.plot(output['Strike Price'], output['sabrsigma'], '--r', linewidth = 3, label = 'SABR model')
                plt.ylabel(time_diff, fontsize = 20)
                plt.xlabel(tradedate, fontsize = 20)
                plt.legend(fontsize = 16);
                plt.show()
                final_ = pd.concat([final_,output])
                print(final_)
                print("inside final")
    return final_

if __name__ == "__main__":
    data  = pd.read_csv("futuredatamerge_nov.csv")
    df_ = VolGreeksProcessing(data)
    df_.to_csv("SABR_final.csv")

