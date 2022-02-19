'''
Different Strategies Pay off
'''
## Import self code
#from self.OptionsStrategy.StrategyPayOff.binomial import  *

## Import Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
import math

class OptionsStrategiesPayoff:
    def __init__(self):
        self.buy = -1
        self.sell = 1

    def bullcallspread(self,kwargs):
        print("**Strategy : BULL CALL SPREAD :Buy - ITM : Lower Strike Price | Sell - OTM  - Higher Strike Price")
        callSpread = OptionsStrategiesPayoff().sell * kwargs["OTMStrike"] + kwargs["ITMStrike"] * OptionsStrategiesPayoff().buy
        maxLoss =  OptionsStrategiesPayoff().sell* kwargs["OTMStrikeCE"]+kwargs["ITMStrikeCE"] * OptionsStrategiesPayoff().buy
        maxprofit =  callSpread+ maxLoss
        print ("callSpread :  {} ,maxLoss  :  {} , maxprofit : {} ".format(callSpread,maxLoss,maxprofit))

    def bullputspread(self,kwargs):
        print(" Strategy : BULL PUT SPREAD :Sell -ITM : HIGHER STRIKE PRICE |  Buy OTM  put with LOWER STRIKE PRICE")
        callSpread = OptionsStrategiesPayoff().buy * kwargs["OTMStrike"] + kwargs["ITMStrike"] * OptionsStrategiesPayoff().sell
        maxLoss =  OptionsStrategiesPayoff().buy* kwargs["OTMStrikePE"]+kwargs["ITMStrikePE"] * OptionsStrategiesPayoff().sell
        maxprofit = callSpread + maxLoss
        print ("callSpread :  {} ,maxLoss  :  {} , maxprofit : {} ".format(callSpread,maxLoss,maxprofit))


    def bearcallspread(self,kwargs):
        print("** Strategy : bearcallspread : Bear Call SPREAD :Sell -ITM : Lower STRIKE PRICE |  Long  OTM  Higher STRIKE PRICE")
        callSpread = OptionsStrategiesPayoff().buy * kwargs["OTMStrike"] + kwargs["ITMStrike"] * OptionsStrategiesPayoff().sell
        maxLoss = OptionsStrategiesPayoff().buy * kwargs["OTMStrikeCE"] + kwargs["ITMStrikeCE"] * OptionsStrategiesPayoff().sell
        maxprofit = callSpread + maxLoss
        print("callSpread :  {} ,maxLoss  :  {} , maxprofit : {} ".format(callSpread, maxLoss, maxprofit))

    def bearputspread(self,kwargs):
        print("** Strategy : BEAR PUT SPREAD :SHORT ITM : Put with LOWER STRIKE PRICE |  LONG call OTM  with HIGHER STRIKE PRICE")
        callSpread = OptionsStrategiesPayoff().sell * kwargs["OTMStrike"] + kwargs["ITMStrike"] * OptionsStrategiesPayoff().buy
        maxLoss = OptionsStrategiesPayoff().buy * kwargs["OTMStrikePE"] + kwargs["ITMStrikePE"] * OptionsStrategiesPayoff().sell
        print(OptionsStrategiesPayoff().sell * kwargs["OTMStrikePE"] , kwargs["ITMStrikePE"] * OptionsStrategiesPayoff().buy)
        maxprofit = callSpread + maxLoss
        print("callSpread :  {} ,maxLoss  :  {} , maxprofit : {} ".format(callSpread, maxLoss, maxprofit))


    def callRatiobackSpread(self,kwargs):
        print("** Strategy : Bullish - callRatiobackSpread :SHORT 1 ITM : call with Lower STRIKE PRICE |  LONG 2 call OTM  with HIGHER STRIKE PRICE")
        callSpread =  OptionsStrategiesPayoff().buy * kwargs["OTMStrike"] + kwargs["ITMStrike"] * OptionsStrategiesPayoff().sell
        maximumprofit = 2 * OptionsStrategiesPayoff().buy * kwargs["OTMStrikeCE"] + kwargs["ITMStrikeCE"] * OptionsStrategiesPayoff().sell
        maxLoss = callSpread + maximumprofit
        print("callSpread :  {} ,maxLoss  :  {} , maxprofit : {} ".format(callSpread, maxLoss, maximumprofit))


    def putRatiobackSpread(self,kwargs):
        print("** Strategy : Very Bearish : putRatiobackSpread  :SHORT 1 ITM : Put with Higher  STRIKE PRICE |  LONG 2 put  OTM  with LOWER STRIKE PRICE")
        callSpread =  OptionsStrategiesPayoff().sell * kwargs["OTMStrike"] + kwargs["ITMStrike"] * OptionsStrategiesPayoff().buy
        maxprofit =   2* kwargs["ITMStrikePE"] * OptionsStrategiesPayoff().buy + OptionsStrategiesPayoff().sell * kwargs["OTMStrikePE"]
        maxloss = -callSpread + maxprofit
        print(" callSpread :  {} ,maxLoss  :  {} , maxprofit : {} ".format(callSpread,maxloss,maxprofit))

    def longstrandle(self,kwargs):
        print("** Strategy -longstrandle : uncertain : LONG Call  and Long Put of same Strike Price")
        maxLoss =  kwargs["ATMStrikeCE"] + kwargs["ATMStrikePE"]
        print(" maxLoss - ATM :  {} and  maxprofit  : unlimited ".format(maxLoss))
        print(" maxLoss  - OTM :  {} and  maxprofit : unlimited ".format( kwargs["OTMStrikeCE"] + kwargs["OTMStrikePE"] ))
        print(" maxLoss  -ITM :  {} and  maxprofit : unlimited ".format( kwargs["ITMStrikeCE"] + kwargs["ITMStrikePE"]))




    def shortstrandle(self,kwargs):
        print("**Strategy - shortstrandle : not much movement : short Call  and short Put of same Strike Price")
        maxLoss = OptionsStrategiesPayoff().buy * kwargs["ATMStrikeCE"] + kwargs["ATMStrikePE"] * OptionsStrategiesPayoff().buy
        print(" maxprofit at ATM  :  {} and maxLoss : unlimited  ".format(maxLoss))
        print(" maxprofit at OTM  :  {} and maxLoss : unlimited  ".format( OptionsStrategiesPayoff().buy * kwargs["OTMStrikeCE"] + kwargs["OTMStrikeCE"] * OptionsStrategiesPayoff().buy))
        print(" maxprofit at ITM  :  {} and maxLoss : unlimited  ".format( OptionsStrategiesPayoff().buy * kwargs["ITMStrikeCE"] + kwargs["ITMStrikeCE"] * OptionsStrategiesPayoff().buy))

    def butterfly(self,*args,kwargs):
        pass

    def longstrangle(self,kwargs):
        print("** Strategy - longstrangle : Uncertain   :Long  1 OTM  : Call with Higher  STRIKE PRICE |  LONG 1 Call OTM  with LOWER STRIKE PRICE")
        maxLoss = OptionsStrategiesPayoff().buy * kwargs["OTMStrikeCE"] + kwargs["ITMStrikePE"] * OptionsStrategiesPayoff().buy
        print(" maxLoss  :  {} , maxprofit : {} ".format(maxLoss, "Unlimited"))

    def shortstrangle(self,kwargs):
        print("** Strategy - shortstrangle: Not Much movement : short  1 OTM  : Call with Higher  STRIKE PRICE |  short 1 PUT OTM  with LOWER STRIKE PRICE")
        maxLoss = OptionsStrategiesPayoff().sell * kwargs["OTMStrikeCE"] + kwargs["ITMStrikePE"] * OptionsStrategiesPayoff().sell
        print(" Maxprofit  :  {} , MaxpLoss : {} ".format(maxLoss, "Unlimited"))



class OptionsStrategiesRecommendation():
    def  osrecom(self,*args,**kargs):

        for key,values in kargs.items():
            kargs[key] = np.array(values)

        print("--------------------------------------------------------------------------------------------------------------------------------")
        print ("  ITM_Strike  {} and  PE_Premium   {}  and CE_Premium: {} ".format(kargs["ITMStrike"],kargs["ITMStrikePE"],kargs["ITMStrikeCE"]))
        print("  ATM_Strike {}   and  PE_Premium   {}  and CE_Premium: {}  ".format(kargs["ATMStrike"],kargs["ATMStrikePE"],kargs["ATMStrikeCE"]))
        print("  OTM_Strike {}   and  PE_Premium   {}  and CE_Premium: {}  ".format(kargs["OTMStrike"],kargs["OTMStrikePE"],kargs["OTMStrikeCE"]))
        print("-------------------------------------------xxxxxxxxxxxxxxxxxxxxxxxxxxx-----------------------------------------------------------")

        if (kargs["MarketView"]  ==  MarketView.moderately_bullish):
            print(MarketView.moderately_bullish)
            if (kargs["expectation"] == MarketView.expectation_Reduce_Cost):
                OptionsStrategiesPayoff().bullcallspread(kargs)

            if(kargs["expectation"] == MarketView.expectation_floor_to_downside ):
                OptionsStrategiesPayoff().bullputspread(kargs)

        elif (kargs["MarketView"]  ==  MarketView.moderately_bearish):
            if (kargs["expectation"] == MarketView.expectation_Reduce_Cost):
                OptionsStrategiesPayoff().bearcallspread(kargs)

            elif (kargs["expectation"] == MarketView.expectation_floor_to_downside):
                OptionsStrategiesPayoff().bearputspread(kargs)


        elif (kargs["MarketView"] == MarketView.very_bullish):
            OptionsStrategiesPayoff().callRatiobackSpread(kargs)

        elif (kargs["MarketView"] == MarketView.very_bearish):
            OptionsStrategiesPayoff().putRatiobackSpread(kargs)

        elif (kargs["MarketView"] == MarketView.uncertain):
            OptionsStrategiesPayoff().longstrandle(kargs)
            OptionsStrategiesPayoff().longstrangle(kargs)

        elif (kargs["MarketView"] == MarketView.rangebound):
            OptionsStrategiesPayoff().shortstrandle(kargs)
            OptionsStrategiesPayoff().shortstrangle(kargs)
            #OptionsStrategiesPayoff().butterfly(kargs)

        elif (kargs["HighestDelta"] == MarketView.HighestDelta):
             print("Inisde highest Delta")
             strikeDelta = pd.DataFrame(kargs["data"])
             print(strikeDelta)
             return strikeDelta.iloc[strikeDelta[strikeDelta.columns[-1]].idxmax()]

        elif (kargs["deltahedge"] == MarketView.deltahedge):
            print("inside delta hedge ")
            df_ = pd.DataFrame(kargs["data"])
            print(df_.iloc[:,-1].sum())
            netDelta =  df_.iloc[:,-1].sum()
            return netDelta

class MarketView(Enum):
        neutral = 0
        moderately_bullish = 1
        very_bullish = 2
        moderately_bearish = -1
        very_bearish = -2
        uncertain = 3
        rangebound = 4
        HighestDelta = 5
        expectation_Reduce_Cost = 1
        expectation_floor_to_downside = 2
        deltahedge = 6

if __name__ == "__main__":
    deltahedge = MarketView.deltahedge
    MarketView = MarketView.neutral
    expectation = np.nan
    HighestDelta = np.nan
    StrikeRange = np.arange(17000,18000,50),
    ATMStrike = 1680,
    ATMStrikeCE = 61,
    ATMStrikePE = 50,
    ITMStrike = 1660,
    ITMStrikePE = 41,
    ITMStrikeCE = 72,
    OTMStrike = 1760,
    OTMStrikeCE = 27,
    OTMStrikePE = 94,
    OTMStrike_2 = 1800,
    OTMStrikeCE_2 = 17,
    OTMStrikePE_2 = 126,
    data = pd.DataFrame( {"Strike":[1,2,3,4,5,6],"Premium":[1,2,6,4,3,5]})

    #new_delta_ =  OptionsStrategiesRecommendation().osrecom(HighestDelta = np.nan ,MarketView = MarketView, deltahedge = deltahedge, data= data)
    #Highest_delta = OptionsStrategiesRecommendation().osrecom(HighestDelta=5, MarketView=np.nan,deltahedge=np.nan, data=data)


    Highest_delta = OptionsStrategiesRecommendation().osrecom(MarketView=MarketView.rangebound,StrikeRange =StrikeRange,
                                                              ATMStrike=ATMStrike,ATMStrikeCE=ATMStrikeCE,
                                                              ATMStrikePE=ATMStrikePE,ITMStrike=ITMStrike,
                                                              ITMStrikePE =ITMStrikePE,ITMStrikeCE=ITMStrikeCE,
                                                              OTMStrike=OTMStrike,OTMStrikeCE=OTMStrikeCE,OTMStrikePE=OTMStrikePE,
                                                              OTMStrike_2 = OTMStrike_2, OTMStrikeCE_2 = OTMStrikeCE_2, OTMStrikePE_2 = OTMStrikePE_2
                                                              )

    moderately_bullish_CE = OptionsStrategiesRecommendation().osrecom(MarketView=MarketView.moderately_bullish, StrikeRange=StrikeRange,
                                                              ATMStrike=ATMStrike, ATMStrikeCE=ATMStrikeCE,
                                                              ATMStrikePE=ATMStrikePE, ITMStrike=ITMStrike,
                                                              ITMStrikePE=ITMStrikePE, ITMStrikeCE=ITMStrikeCE,
                                                              OTMStrike=OTMStrike, OTMStrikeCE=OTMStrikeCE,
                                                              OTMStrikePE=OTMStrikePE,expectation=MarketView.expectation_Reduce_Cost)

    moderately_bullish_PE = OptionsStrategiesRecommendation().osrecom(MarketView=MarketView.moderately_bullish, StrikeRange=StrikeRange,
                                                              ATMStrike=ATMStrike, ATMStrikeCE=ATMStrikeCE,
                                                              ATMStrikePE=ATMStrikePE, ITMStrike=ITMStrike,
                                                              ITMStrikePE=ITMStrikePE, ITMStrikeCE=ITMStrikeCE,
                                                              OTMStrike=OTMStrike, OTMStrikeCE=OTMStrikeCE,
                                                              OTMStrikePE=OTMStrikePE,expectation=MarketView.expectation_floor_to_downside)


    moderately_bearish_CE = OptionsStrategiesRecommendation().osrecom(MarketView=MarketView.moderately_bearish, StrikeRange=StrikeRange,
                                                              ATMStrike=ATMStrike, ATMStrikeCE=ATMStrikeCE,
                                                              ATMStrikePE=ATMStrikePE, ITMStrike=ITMStrike,
                                                              ITMStrikePE=ITMStrikePE, ITMStrikeCE=ITMStrikeCE,
                                                              OTMStrike=OTMStrike, OTMStrikeCE=OTMStrikeCE,
                                                              OTMStrikePE=OTMStrikePE,expectation=MarketView.expectation_Reduce_Cost)

    moderately_bearish_PE = OptionsStrategiesRecommendation().osrecom(MarketView=MarketView.moderately_bearish, StrikeRange=StrikeRange,
                                                              ATMStrike=ATMStrike, ATMStrikeCE=ATMStrikeCE,
                                                              ATMStrikePE=ATMStrikePE, ITMStrike=ITMStrike,
                                                              ITMStrikePE=ITMStrikePE, ITMStrikeCE=ITMStrikeCE,
                                                              OTMStrike=OTMStrike, OTMStrikeCE=OTMStrikeCE,
                                                              OTMStrikePE=OTMStrikePE,expectation=MarketView.expectation_floor_to_downside)


    very_bullish_callRatiobackSpread = OptionsStrategiesRecommendation().osrecom(MarketView=MarketView.very_bullish, StrikeRange=StrikeRange,
                                                              ATMStrike=ATMStrike, ATMStrikeCE=ATMStrikeCE,
                                                              ATMStrikePE=ATMStrikePE, ITMStrike=ITMStrike,
                                                              ITMStrikePE=ITMStrikePE, ITMStrikeCE=ITMStrikeCE,
                                                              OTMStrike=OTMStrike, OTMStrikeCE=OTMStrikeCE,
                                                              OTMStrikePE=OTMStrikePE,expectation=MarketView.expectation_floor_to_downside)

    very_bearish_outRatiobackSpread = OptionsStrategiesRecommendation().osrecom(MarketView=MarketView.very_bearish, StrikeRange=StrikeRange,
                                                              ATMStrike=ATMStrike, ATMStrikeCE=ATMStrikeCE,
                                                              ATMStrikePE=ATMStrikePE, ITMStrike=ITMStrike,
                                                              ITMStrikePE=ITMStrikePE, ITMStrikeCE=ITMStrikeCE,
                                                              OTMStrike=OTMStrike, OTMStrikeCE=OTMStrikeCE,
                                                              OTMStrikePE=OTMStrikePE,expectation=MarketView.expectation_floor_to_downside)

    uncertain = OptionsStrategiesRecommendation().osrecom(MarketView=MarketView.uncertain, StrikeRange=StrikeRange,
                                                              ATMStrike=ATMStrike, ATMStrikeCE=ATMStrikeCE,
                                                              ATMStrikePE=ATMStrikePE, ITMStrike=ITMStrike,
                                                              ITMStrikePE=ITMStrikePE, ITMStrikeCE=ITMStrikeCE,
                                                              OTMStrike=OTMStrike, OTMStrikeCE=OTMStrikeCE,
                                                              OTMStrikePE=OTMStrikePE,expectation=MarketView.expectation_floor_to_downside,
                                                              OTMStrike_2 = OTMStrike_2, OTMStrikeCE_2 = OTMStrikeCE_2, OTMStrikePE_2 = OTMStrikePE_2
                                                               )

    rangebound  = OptionsStrategiesRecommendation().osrecom(MarketView=MarketView.rangebound, StrikeRange=StrikeRange,
                                                              ATMStrike=ATMStrike, ATMStrikeCE=ATMStrikeCE,
                                                              ATMStrikePE=ATMStrikePE, ITMStrike=ITMStrike,
                                                              ITMStrikePE=ITMStrikePE, ITMStrikeCE=ITMStrikeCE,
                                                              OTMStrike=OTMStrike, OTMStrikeCE=OTMStrikeCE,
                                                              OTMStrikePE=OTMStrikePE,expectation=MarketView.expectation_floor_to_downside,
                                                              OTMStrike_2 = OTMStrike_2, OTMStrikeCE_2 = OTMStrikeCE_2, OTMStrikePE_2 = OTMStrikePE_2)


