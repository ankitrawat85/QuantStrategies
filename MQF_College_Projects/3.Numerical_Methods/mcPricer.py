import math
import numpy as np

def mcPricer(mkt, trade, models, nPaths):
    assetNames = trade.assetNames() # get all the assets involved for the payoff
    C = mkt.Correlation(assetNames, models) # get correlation matrix from the market
    numFactors = C.size() # get total number of factors (brownians)
    L = np.linalg.cholesky(C) # cholesky decomposition
    dts = [] # get simulation time steps
    for a in assetNames:
        dts.append(models[a].GetTimeSteps(trade.AllDates()))
    dts = np.unique(dts)
    sum, hsquare, nT = 0, 0, dts.size()
    for i in range(nPaths):
        # generate independent bronian increments,
        for j in range(numFactors):
            brownians[j] = np.random.normal(0, 1, nT)
        brownians = np.matmul(L, brownians) # correlate them using L
        bidx, fobs = 0, dict() # fobs is a dict from asset name to observable,
        # each observable if a function from t to the observation price
        for k in assetNames.size():
            # pass the brownians to the model to generate the observation functions
            model = models[assetNames[k]]
            nF = model.NumberOfFactors()
            bs = brownians.project(bidx, bidx + nF)
            fobs[assetNames[k]] = model.Diffuse(dts, bs)
            bidx += nF
        # call the payoff function to obtain the discounted cashflows
        h = trade.DiscountedMCPayoff(fobs)
        sum += h
        hsquare += h*h
    pv = sum / nPaths
    se = math.sqrt((hsquare/nPaths - pv*pv)/nPaths)
    return pv, se

