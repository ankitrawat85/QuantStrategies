from scipy.stats import norm
from math import log, sqrt, exp
import scipy.optimize as op
import numpy as np

class OptionPricing:
    def Black76LognormalCall(S, K, r, sigma, T):
        d1 = (log(S/K)+(r+sigma**2/2)*T) / (sigma*sqrt(T))
        d2 = d1 - sigma*sqrt(T)
        return S*norm.cdf(d1) - K*exp(-r*T)*norm.cdf(d2)

    def BlackScholesCall(S, K, r, sigma, T):
        d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

    def BlackScholesPut(S, K, r, sigma, T):
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

    def Black76LognormalCall(self,S, K, r, sigma, T):
        d1 = (log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * sqrt(T))
        d2 = d1 - sigma * sqrt(T)
        return S * norm.cdf(d1) - K * exp(-r * T) * norm.cdf(d2)

    def impliedCallVol(self,model):
        if (model == "Black76Lognormal"):
            impliedVol = op.brentq(lambda x: self.price -
                                          Vol.Black76LognormalCall(self,self.spotprice, self.strike, self.riskfreerate, x, self.timeperiod),
                                1e-6, 1)
        return impliedVol

x = Vol(spotprice =40,Strike=60, riskfreerate=0.01, price=0.12, T=0.25)
print(x.impliedCallVol(model="Black76Lognormal"))


