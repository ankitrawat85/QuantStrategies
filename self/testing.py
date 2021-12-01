import math
import numpy as np


# one step binomial
from enum import Enum
import math

class optionRiskFreePortfolio:

    def __init__(self,spotprice,strike,upwardMovement,downwardMovment,timeperiod,riskfreerate):
        self.strike = strike
        self.upwardMovement = upwardMovement
        self.downwardMovment  = downwardMovment
        self.delta = 0
        self.riskfreerate =  riskfreerate
        self.timeperiod = timeperiod
        self.spotprice = spotprice

    def deltaNuetralPortfolio(self):
        portfolio_up  = self.upwardMovement * self.delta - (self.strike - self.upwardMovement)
        return ((self.upwardMovement - self.strike) / ( self.upwardMovement - self.downwardMovment ))

    def optionvalue(self):
        delta = self.deltaNuetralPortfolio()
        print(delta)
        print(self.upwardMovement * delta -  (self.upwardMovement-self.strike))
        present_value = (self.upwardMovement * delta -  (self.upwardMovement-self.strike)) \
                        * np.exp(-self.riskfreerate * self.timeperiod)

        CalloptionValue  = self.spotprice * delta - present_value

        print(CalloptionValue)





class PayoffType(Enum):
    Call = 0
    Put = 1
    BinaryCall = 2
    BinaryPut = 3

def oneStepBinomial(S, r, u, d, optType, K, T):
    #p = (math.exp(r * T) - d) / (u-d)
    p = (math.exp(r * T) - d) / (u-d)
    return math.exp(-r*T) * (p*max(S*u-K, 0) + (1-p) * max(S*d-K, 0))

print(oneStepBinomial(S=1700, r=0.10, u=1.20, d=0.80, optType=0, K=110, T=0.25))
test  = optionRiskFreePortfolio(spotprice = 100,strike =110,upwardMovement=120,downwardMovment=80,timeperiod = 0.25,riskfreerate = 0.10)
test.optionvalue()