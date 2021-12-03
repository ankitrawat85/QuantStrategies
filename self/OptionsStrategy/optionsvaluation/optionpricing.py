import matplotlib.pyplot
import pandas as pd
from scipy.stats import norm
from math import log, sqrt, exp
import scipy.optimize as op
import numpy as np
import mibian
import pandas as pd
from scipy.optimize import least_squares
import numpy as np
import matplotlib.pyplot as plt
desired_width = 320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns', 30)
import matplotlib.pyplot as plt
from datetime import datetime,date

class OptionPricing:

    def Black76LognormalCall(self,S, K, r, sigma, T):
        d1 = (log(S/K)+(r+sigma**2/2)*T) / (sigma*sqrt(T))
        d2 = d1 - sigma*sqrt(T)
        return S*norm.cdf(d1) - K*exp(-r*T)*norm.cdf(d2)

    def BlackScholesCall(self,S, K, r, sigma, T):
        d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

    def BlackScholesPut(self,S, K, r, sigma, T):
        d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


class Vol:
    def __init__(self,spotprice,Strike, riskfreerate, price, T):
        self.strike = Strike
        self.riskfreerate = riskfreerate
        self.price = price
        self.timeperiod = T
        self.spotprice = spotprice

    def implied_volatility_options(self, opt):
        opt['impliedvolatility'] = np.nan
        #opt["time_diff"] = opt["time_diff"]  * 365
        #opt.loc[(opt.time_diff == 0), 'time_diff'] = 0.0000001
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

    def impliedPutVol(self,model):
        impliedVolput = 0
        if (model == "BlackScholes"):
            #print(self.price, self.spotprice, self.strike, self.riskfreerate, self.timeperiod)
            impliedVolput = op.brentq(lambda x: self.price -OptionPricing().BlackScholesPut(self.spotprice, self.strike, self.riskfreerate, x, self.timeperiod),1e-6, 2)
        return impliedVolput

    def impliedCallVol(self, model):
        if (model == "BlackScholes"):
            #print(self.price,self.spotprice, self.strike, self.riskfreerate, self.timeperiod)
            impliedVolcall = op.brentq(lambda x: self.price -
                                          OptionPricing().BlackScholesCall(self.spotprice, self.strike, self.riskfreerate, x, self.timeperiod),1e-6, 2)
            return impliedVolcall

    def SABR(self,F, K, T, alpha, beta, rho, nu):
        X = K
        # if K is at-the-money-forward
        if abs(F - K) < 1e-12:
            numer1 = (((1 - beta) ** 2) / 24) * alpha * alpha / (F ** (2 - 2 * beta))
            numer2 = 0.25 * rho * beta * nu * alpha / (F ** (1 - beta))
            numer3 = ((2 - 3 * rho * rho) / 24) * nu * nu
            VolAtm = alpha * (1 + (numer1 + numer2 + numer3) * T) / (F ** (1 - beta))
            sabrsigma = VolAtm
        else:
            z = (nu / alpha) * ((F * X) ** (0.5 * (1 - beta))) * np.log(F / X)
            zhi = np.log((((1 - 2 * rho * z + z * z) ** 0.5) + z - rho) / (1 - rho))
            numer1 = (((1 - beta) ** 2) / 24) * ((alpha * alpha) / ((F * X) ** (1 - beta)))
            numer2 = 0.25 * rho * beta * nu * alpha / ((F * X) ** ((1 - beta) / 2))
            numer3 = ((2 - 3 * rho * rho) / 24) * nu * nu
            numer = alpha * (1 + (numer1 + numer2 + numer3) * T) * z
            denom1 = ((1 - beta) ** 2 / 24) * (np.log(F / X)) ** 2
            denom2 = (((1 - beta) ** 4) / 1920) * ((np.log(F / X)) ** 4)
            denom = ((F * X) ** ((1 - beta) / 2)) * (1 + denom1 + denom2) * zhi
            sabrsigma = numer / denom

        return sabrsigma

    def sabrcalibration(self,x, strikes, vols, F, T):
        err = 0.0
        beta = 0.8
        r = Vol(spotprice=100, Strike=100, riskfreerate=0.04, price=10, T=12 / 360)
        for i, vo in enumerate(vols):
            err += (vo - r.SABR(F,np.array(strikes)[i],T,x[0], beta, x[1], x[2])) ** 2

        return err

    #def sabrvolatility(self,data):
    def sabrvolatility(self,data:"df_merge.csv"):
        ## optins data
        #df_  = pd.read_csv(data)
        df_ = data
        #df_.drop("Unnamed: 0",axis =1, inplace = True)

        #df_["Expiry"]= pd.to_datetime(df_["Expiry"],format = '%d/%m/%Y')
        #df_["Date"]= pd.to_datetime(df_["Date"],format = '%d/%m/%y')
        #df_ = df_[df_["Date"] == "2021-11-01"]
        #df_["time_diff"]  = ((df_["Expiry"] - df_["Date"]).dt.days)
        df_.to_csv("main.csv")
        #print("Main--")
        #print(df_)

        '''
        df_  = pd.read_csv("google.csv")
        #df_.drop("Unnamed: 0",axis =1, inplace = True)
        df_["Expiry"]= pd.to_datetime(df_["Expiry"],format = '%Y%m%d')
        df_["Date"]= pd.to_datetime(df_["Date"],format = '%Y%m%d')
        df_["time_diff"]  = ((df_["Expiry"] - df_["Date"]).dt.days)/365
        df_.to_csv("main.csv")
        '''
        #print(df_)
        ## stike price > future pricde
        put_df_option = df_[(df_["Strike Price"] <= df_["futures_price"]) & (df_["Option Type"] == "PE")]
        call_df_option = df_[(df_["Strike Price"] >= df_["futures_price"]) & (df_["Option Type"] == "CE")]
        #put_df_option = put_df_option[["Date","Expiry","Option Type","Settle Price","Strike Price","time_diff","futures_price"]]
        #call_df_option = call_df_option[["Date","Expiry","Option Type","Settle Price","Strike Price","time_diff","futures_price"]]
        put_df_option.to_csv("put.csv")
        call_df_option.to_csv("call.csv")
        put_df_option.reset_index(inplace = True)
        call_df_option.reset_index(inplace = True)
        ## Through Library
        """
        call_df_option = Vol(spotprice =call_df_option["futures_price"],Strike=call_df_option["Strike Price"], riskfreerate=0.0, price=put_df_option["futures_price"], T=put_df_option["time_diff"]).implied_volatility_options(call_df_option)
        #print(call_df_option)
        put_df_option = Vol(spotprice =put_df_option["futures_price"],Strike=put_df_option["Strike Price"], riskfreerate=0.0, price=put_df_option["futures_price"], T=put_df_option["time_diff"]).implied_volatility_options(put_df_option)
        #print(put_df_option)
        """
        ## thorugh my code
        print("Implied calcualtion-->")
        call_df_option["impliedvolatility"] = call_df_option.apply(lambda x : Vol(spotprice =x["futures_price"],Strike=x["Strike Price"], riskfreerate=0, price=x["Close"], T=x["time_diff"]).impliedCallVol(model="BlackScholes"),axis =1)
        #print(call_df_option)
        put_df_option["impliedvolatility"] = put_df_option.apply(lambda x : Vol(spotprice =x["futures_price"],Strike=x["Strike Price"], riskfreerate=0, price=x["Close"], T=x["time_diff"]).impliedPutVol(model="BlackScholes"),axis =1)
        #print(put_df_option)

        df = pd.concat([call_df_option,put_df_option]).reset_index().sort_values(by = "Strike Price")
        #df = df["impliedvolatility"]"""
        df.to_csv("putcall.csv")
        #print("Cal 3")
        r =  Vol(spotprice =100,Strike=100, riskfreerate=0.04, price=10, T=12/360)
        df["alpha"] = np.NAN
        df["rho"] = np.NAN
        df["nu"] = np.NAN
        df["Beta"] = 0.8
        df["sabrsigma"] = np.nan
        #df.reset_index(inplace = True)
        print("SABR CALCULATION--------------------------->")
        #print(df["Date"].unique())
        for i in df["Date"].unique():
            alpha, rho, nu = 0.02, 0.2, 0.1
            initialGuess = [alpha, rho, nu]
            i = str(i).split('T')[0]
            df_SABR = df[df["Date"] == i]
            #print("DB_SABR-->")
            res = least_squares(lambda x: r.sabrcalibration(x,df_SABR['Strike Price'], df_SABR['impliedvolatility'],np.array(df_SABR["futures_price"])[0],np.array(df_SABR["time_diff"])[0]),initialGuess)
            df[df["Date"] == i] = df[df["Date"] == i].assign(alpha=res.x[0],rho=res.x[1],nu=res.x[2])
            #print('Calibrated SABR model parameters: alpha = %.3f, beta = %.1f, rho = %.3f, nu = %.3f' % (res.x[0], 0.8, res.x[1], res.x[2]))
            df[df["Date"] == i] = df[df["Date"] == i].assign(sabrsigma=df.apply(
                lambda x: r.SABR(np.array(x["futures_price"]), x['Strike Price'], x["time_diff"],
                                 x["alpha"], x["Beta"], x["rho"], x["nu"]), axis=1))
            df_plot = df[df["Date"] == i][["Strike Price", "impliedvolatility", "sabrsigma"]].sort_values(
                by="Strike Price")
            #df_plot = df_plot.sort_values(by = "Strike Price")
            #plt.figure(figsize=(12, 7))
            #plt.scatter(df_plot['Strike Price'], df_plot['impliedvolatility'], alpha=0.8, c='g', marker='s', label='Market')
            #plt.plot(df_plot['Strike Price'], df_plot['sabrsigma'], '--r', linewidth=3, label='SABR model')
            #plt.ylabel('Implied Vol', fontsize=20)
            #lt.xlabel('Strike', fontsize=20)
            #plt.legend(fontsize=16);
            #plt.show()

        df.to_csv("sabrsigma.csv")
        return df

def volatility(vol,df_):
    if (str(vol) ==  "SABR"):
        r =  Vol(spotprice =100,Strike=100, riskfreerate=0.04, price=10, T=12/360)
        #print(df_.dtypes)
        r.sabrvolatility(df_)
        #r.sabrvolatility("google.csv")
        #r.sabrvolatility("df_merge_test.csv")
        return r.sabrvolatility(df_)



if __name__ == "__main__":
    volatility("SABR",1)