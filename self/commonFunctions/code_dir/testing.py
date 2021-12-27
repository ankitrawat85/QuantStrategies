from scipy.optimize import brentq
from scipy.stats import norm
from math import log, sqrt, exp


def Black76LognormalCall(S, K, r, sigma, T):
    d1 = (log(S/K)+(r+sigma**2/2)*T) / (sigma*sqrt(T))
    d2 = d1 - sigma*sqrt(T)
    return S*norm.cdf(d1) - K*exp(-r*T)*norm.cdf(d2)

def impliedCallVolatility(S, K, r, price, T):
    impliedVol = brentq(lambda x: price -
                        Black76LognormalCall(S, K, r, x, T),
                        1e-6, 4)

    print(impliedVol)

    return impliedVol
impliedCallVolatility(1863.4,1800,0.0,66.525,0.008)
