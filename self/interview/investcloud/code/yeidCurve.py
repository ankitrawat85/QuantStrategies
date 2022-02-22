'''
1. Yield curve model implementation
2. VAR Calculation
'''


'''
Diable Warning 
'''
import warnings
warnings.filterwarnings('ignore')
## import libraries
import logging
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os
from enum import Enum
import bond_pricing
from pathlib import Path  ## get directory path

## To display number of columns and rows in console
desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',30)
pd.set_option('display.max_rows',2000)

## Root Directory
root_DIR = Path(__file__).parent
dataPath = Path(__file__).parent.parent
logging.debug(msg=f'root directory : {Path(__file__).parent}', stacklevel=4)
print("Root directory : {} ".format(root_DIR))

class params(Enum):
    '''
    Pre defined Varaibles
    '''
    FilePath_Bond_Prices = str(dataPath) + r'/Data/bond_prices.csv'
    FilePath_Bond =  str(dataPath) +r'/Data/bonds.csv'
    FileOutpath = str(dataPath) +r'/result/'
    zeroCouponBondParValue = 100
    Conitnuos = 1
    Discreate = 2
    yearly = 1
    quartly = 4
    bondDivisor = 100
    daysInYear = 360
    shape = [ i for i in np.arange(0.05,3,0.05)]
    estimation_methods_ols =1
    estimation_methods_wls =2
    NelsonSiegel =1
    annually =1
    semianualy =2



class dataParsing:
 def __init__(self,*args,**kwargs):
     pass

 def readCsv(self,filePath ,*args,**kwargs):
     return pd.read_csv(filePath)


 def time_to_expiry(self, Date : pd.DataFrame,Expiry: pd.DataFrame, daysInYear = 360):
     Expiry = pd.to_datetime(Expiry)
     Date = pd.to_datetime(Date)
     return (Expiry - Date).dt.days/daysInYear


class ratesCalculation:
    def __init__(self, *args, **kwargs):
        pass

    def getSpotNelsonSiegel (self,  firstTerm : float , secondTerm : float , thirdTerm  : float ,shape : float , term_to_maturity : float ):
        '''
        :param data:
        :param time_to_expiry:
        :param firstTerm:
        :param secondTerm:
        :param thirdTerm:
        :return:
        '''
        return firstTerm + (secondTerm * ( 1- np.exp(shape *term_to_maturity )) / (shape *term_to_maturity) ) - thirdTerm * np.exp(shape *term_to_maturity)


    def zeroRate(self,price : list = [] , time_to_expiry  : list =  [] , ContinuosOrDiscrete : int = params.Conitnuos, compounding = params.semianualy, faceValue = 100 ):
        ###Zero rate (or spot rate) is the yield-to-maturity of a zero-coupon bond. From the price D(t, T ),
        ###we can calculate the continuously compounded spot rate R(t,T) that is set at t and pays at T.
        try:
            if len (price) > 0 and len (time_to_expiry) > 0 and len (price) == len(time_to_expiry):
                if ContinuosOrDiscrete == 1:
                    logging.info(msg=f'Initiating Continuously compounded Zero rate Calculation......' )
                    zeroRates =  []
                    for price,timeperiod in zip(price,time_to_expiry):
                        spotRate =  -np.log(price/faceValue)/timeperiod
                        zeroRates.append(spotRate)
                    logging.info(msg=f'Continuos Zero Rate calculation computation completed')
                    return zeroRates

                elif ContinuosOrDiscrete == 2:
                    logging.info(msg=f'Initiating Discretely compounded zero rate.....')
                    zeroRates = []
                    for price, timeperiod in enumerate(price, time_to_expiry):
                        spotRate = compounding *[ price ** (-1/(compounding *timeperiod)) -1]
                        zeroRates.append(spotRate)
                    logging.info(msg=f'Completed Continuos Zero Rate calculation')
                    return zeroRates
                else:
                    logging.error(msg=f'Curent function can not calcuate Zero rate based on given input parameter  : {ContinuosOrDiscrete}')
                    assert f"Current function can not calcualate Zero rate based on given input parameter  : {ContinuosOrDiscrete}"

            else:
                raise ValueError  ( 'Either Price or DateDifference list is empty or there length does not match')

        except Exception as e:
            logging.error(msg = {e})
            assert "Zero Rates  calculation failed"

class yieldCurveFitting:
    def __init__(self, *args, **kwargs, ):
        pass

    def NelsonSiegelModel(self, expectedYield : list  , term_to_maturity : list  ,a : float = None, b : float = None, c : float=None,shape : float = None, estimation_methods = None ):
        '''
        :param a: long term
        :param b: short term  + long term
        :param c: medium term
        :param shape:      # λ affects the fitting power of the model for different segments of the curve.
        :param term_to_maturity:
        '''
        if estimation_methods == 1:
            secondTerm = [(1 - np.exp(shape * timePeriod)) / (shape * timePeriod) for timePeriod in term_to_maturity]
            thirdTerm = [-np.exp(shape * timePeriod) for timePeriod in term_to_maturity]
            X = np.array([secondTerm, thirdTerm]).T
            X = sm.add_constant(X)
            y = expectedYield
            res = sm.OLS(y, X).fit()
            return (res.params[0] ,res.params[1],res.params[2], res.rsquared , res.mse_resid)


class simulation:
    def __init__(self, *args, **kwargs, ):
        pass

    def nelsonSeigal(self,yield_curve : pd.DataFrame,tenor : pd.DataFrame,columns : list , parameterCalibration : int , shape : list ):
        logging.info(msg="Initiating NS method ......")
        if parameterCalibration == 1: # SpotRate Calculation for different Lambda values using Nelson Siegel Model
            output_parameters = pd.DataFrame(columns=["lambda", "a_lst", "b_lst", "c_lst", "rsquared_lst","rmse"], index=yield_curve.index)
            output_NS = pd.DataFrame(columns=yield_curve.columns, index=yield_curve.index)
            for yield_row, tenor_row in zip(yield_curve.iterrows(), tenor.iterrows()):
                lambda_lst, a_lst, b_lst, c_lst, rsquared_lst , rsme_lst = [], [], [], [], [], []
                for i in shape:
                    firstTerm, SecondTerm, thirdTerm, rSquare ,rsme = yieldCurveFitting().NelsonSiegelModel(expectedYield=yield_row[1], term_to_maturity=tenor_row[1],
                        estimation_methods=params.estimation_methods_ols.value, shape=i)
                    lambda_lst.append(i), a_lst.append(firstTerm), b_lst.append(SecondTerm), c_lst.append(
                        thirdTerm), rsquared_lst.append(rSquare), rsme_lst.append(rsme)

                # locate the highest rsquared index
                idx = rsquared_lst.index(max(rsquared_lst))

                # assign to params_df
                output_parameters.loc[yield_row[0], :] = [lambda_lst[idx], a_lst[idx], b_lst[idx], c_lst[idx],
                                                          rsquared_lst[idx],rsme_lst[idx]]
                output_NS.loc[yield_row[0], :] = [
                    ratesCalculation().getSpotNelsonSiegel(firstTerm=a_lst[idx], secondTerm=b_lst[idx],
                                                           thirdTerm=c_lst[idx], shape=lambda_lst[idx], term_to_maturity=i) for i in tenor_row[1]]
            logging.info(msg="NS method calibration commpleted")
            logging.info(msg=f'Set of output paramters post NS  : \n  {output_parameters.head(5)})')
            logging.info(msg=f'Set of predicted yield paramters post NS  : \n  {output_NS.head(5)})')
            return output_parameters , output_NS

class bondPricing:

    def __init__(self):
        pass

    def zero_curve_bond_price(self,faceValue = 100,Maturity : float = 0, ytm =0, couponPerecentageAnnually : float =0 , frequency : int = 1 , callibration = None,*args,**kwargs):
        logging.info(msg=f'Bond price calculation initiated.....')
        if callibration == 1:
            logging.info(msg=f'NS calibration')
            self.spotRate = kwargs["spotRate"]
            self.time_to_expiry = kwargs["time_to_expiry"]
            output_parameters, output_NS = simulation().nelsonSeigal(yield_curve=pd.DataFrame(self.spotRate).transpose() , tenor=pd.DataFrame(self.time_to_expiry).transpose(),
                                                                     columns=self.time_to_expiry,
                                                                     parameterCalibration=1, shape=params.shape.value)
        logging.info(msg=f'Best fit param: {output_parameters["lambda"].values[0]}')
        logging.info(msg=f'a: {output_parameters["a_lst"].values},b : {output_parameters["b_lst"].values},c : {output_parameters["c_lst"].values}, lambda : {output_parameters["lambda"].values[0]}')

        self.deltaPeriod = 1/frequency
        self.totalCashFlowPeriods = Maturity/self.deltaPeriod

        bondPrice =  pd.DataFrame(columns=["TimePeriod","SpotRate","CouponRate","cashflow","discountFactor","presentValue"])

        bondValue = []

        for i in  np.arange(self.deltaPeriod ,Maturity+self.deltaPeriod,self.deltaPeriod):
            if i > Maturity:
                break
            spotRate = ratesCalculation().getSpotNelsonSiegel(firstTerm=output_parameters["a_lst"].values,secondTerm=output_parameters["b_lst"].values,
                                                              thirdTerm=output_parameters["c_lst"].values,shape=output_parameters["lambda"].values[0],term_to_maturity=i)
            discountFactor = np.exp(-spotRate[0]*i)
            if i == Maturity:
                cashflow = ((couponPerecentageAnnually / 100) * faceValue) / frequency + faceValue
            else:
                cashflow = ((couponPerecentageAnnually / 100) * faceValue) / frequency

            presentValue = cashflow * discountFactor
            bondValue.append([i,spotRate[0],couponPerecentageAnnually,cashflow,discountFactor,presentValue])
        logging.info(msg=f'Bond price calculation completed')
        logging.info (msg = f'{pd.DataFrame(bondValue,columns=["TimePeriod","SpotRate","CouponRate","cashflow","discountFactor","presentValue"])}')
        return pd.DataFrame(bondValue,columns=["TimePeriod","SpotRate","CouponRate","cashflow","discountFactor","presentValue"])

class Var:

    def __init__(self):
        pass

    def linearMethod_delta_noramal(self, yieldR : list , maturity : list , signifiance_Level =  0.05 ,freq = 2 ,corelation = 0.5, coupon  = [] , weightage = [] , Dailyvolatility = [], TotalInvestment =100, undiversifiedVar = "Yes"):
        '''
        Calculate  VAR based on change in Linear method - Change Modified duration - with one basis point change in yield
        considering all bonds has same maturity
        as of now code only can handle a portfolio of  two bonds only
        '''
        dura = []
        for ytm,cpn,mat in zip(yieldR,coupon,maturity):
            currentPrice = bond_pricing.bond_price(mat=mat,freq=freq, cpn=cpn, yld=ytm,face=1)
            Price_lowerYield = bond_pricing.bond_price(mat=mat, freq=freq, cpn=cpn, yld=ytm-0.01, face=1)
            Price_higherYield = bond_pricing.bond_price(mat=mat, freq=freq, cpn=cpn, yld=ytm+0.01, face=1)
            effectiveDuration = (Price_lowerYield - Price_higherYield) / ( 2 * 0.01 * currentPrice)
            #modified_duration = bond_pricing.bond_duration(mat=mat,freq=freq, cpn=cpn, yld=ytm, modified=True,face=100)
            dura.append(effectiveDuration)


        duration = np.array([dura])
        weightage = np.array([weightage])
        dailyvolatility = np.array([Dailyvolatility])
        z =  2.33 if signifiance_Level == 0.05 else logging.error(msg="Significance level value not available")

        Var_Daily_percent =  duration * weightage * dailyvolatility * z
        Var_yearly_percent = duration * weightage * dailyvolatility * np.sqrt(365) * z

        if undiversifiedVar == "Yes":  ## correlation =1
            PortfolioVar = Var_Daily_percent * TotalInvestment
            portfolioYearly = Var_yearly_percent * TotalInvestment
            logging.info(msg = f"daily portfolio VAR  using Delta appraoch: { np.sum(PortfolioVar)}")
            logging.info(msg=f" Yearly portfolio VAR Delta appraoch : {np.sum(portfolioYearly)}")
            return PortfolioVar,portfolioYearly

        else:
            PortfolioVar = np.sqrt(Var_Daily_percent[0]**2 + Var_Daily_percent[1]**2 + 2 * Var_Daily_percent * corelation) * TotalInvestment
            logging.info(msg=f"daily portfolio VAR : {PortfolioVar}")
            PortfolioVarYearly = np.sqrt(Var_yearly_percent[0] ** 2 + Var_yearly_percent[1] ** 2 + 2 * Var_yearly_percent * corelation) * TotalInvestment
            logging.info(msg=f"Yearly portfolio VAR : {PortfolioVarYearly}")
            return PortfolioVar, PortfolioVarYearly


    def nonLinearMethod_delta_gamma_noramal(self, yieldR : list , maturity : list , signifiance_Level =  0.05 ,freq = 2 ,corelation = 0.5, coupon  = [] , weightage = [] , Dailyvolatility = [], TotalInvestment =100, undiversifiedVar = "Yes"):
        dura = []
        convex = []
        var = []
        z = 2.33 if signifiance_Level == 0.05 else logging.error(msg="Significance level value not available")
        for ytm, cpn, mat,vol in zip(yieldR, coupon, maturity,Dailyvolatility):
            currentPrice = bond_pricing.bond_price(mat=mat, freq=freq, cpn=cpn, yld=ytm, face=1)
            Price_lowerYield = bond_pricing.bond_price(mat=mat, freq=freq, cpn=cpn, yld=ytm - 0.01, face=1)
            Price_higherYield = bond_pricing.bond_price(mat=mat, freq=freq, cpn=cpn, yld=ytm + 0.01, face=1)
            convexity = (Price_lowerYield + Price_higherYield - 2* currentPrice) / (currentPrice* 0.01 ** 2)
            effectiveDuration = (Price_lowerYield - Price_higherYield) / (2 * 0.01 * currentPrice)
            dura.append(effectiveDuration)
            convex.append(convexity)
            _var = currentPrice * vol * z
            var.append(_var)
        Total_Delta_Componenet = -1 * np.array([dura]) * np.array([var])
        Total_Gamma_Component = 0.5 *  np.array([convex]) * np.array([np.square(var)])

        VAR = np.array([Total_Delta_Componenet]) + np.array([Total_Gamma_Component])

        prtfolioVar =  np.array([VAR]) * np.array([weightage]) * TotalInvestment
        logging.info(msg = f' Daily Portfolio Var using delta Gamma Appraoch  : {np.sum(prtfolioVar)} ')
        return prtfolioVar

    def fullValualtionMethod(self, yieldR : list , maturity : list , signifiance_Level =  0.05 ,freq = 2 ,corelation = 0.5, coupon  = [] , weightage = [] , Dailyvolatility = [], TotalInvestment =100, undiversifiedVar = "Yes"):
        '''
        Re-Price the bond assuming a shock of :  Z * daily volatility
        '''
        dura = []
        convex = []
        var = []
        z = 2.33 if signifiance_Level == 0.05 else logging.error(msg="Significance level value not available")
        shock =  z * np.array([Dailyvolatility])
        shockYield = np.array([yieldR]) - np.array([shock])
        for ytm, cpn, mat,shockyld in zip(yieldR, coupon, maturity,shockYield):
            currentPrice = bond_pricing.bond_price(mat=mat, freq=freq, cpn=cpn, yld=ytm, face=1)
            modifiedPrice = bond_pricing.bond_price(mat=mat, freq=freq, cpn=cpn, yld=shockyld , face=1)
            var.append([currentPrice - modifiedPrice ])

        portfolioVar = np.array([var]) * np.array([weightage]) * TotalInvestment
        logging.info(f'Portfolio VAR based on full revaluation method :  {np.sum(portfolioVar)}')
        return portfolioVar


    def fullValualtionMethod_HistoricalSimulation(self):
        pass


def main():
    ## Enable loggin - INFO level
    logging.basicConfig(filename='std.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.warning('This message will get logged on to a file')
    logging.getLogger().setLevel(logging.INFO)
    logging.info('Started')
    ## Tasks
    ### 1 - Parse input data
    #--------------------------
    ##   Data Parsing -> Read data from csv
    df_Bond_Prices = dataParsing().readCsv(filePath=params.FilePath_Bond_Prices.value)
    df_Bond_Prices['Date'] = pd.to_datetime(df_Bond_Prices['Date'])
    df_Bond_Prices = dataParsing().readCsv(filePath=params.FilePath_Bond_Prices.value)
    df_Bond_Prices['Date'] = pd.to_datetime(df_Bond_Prices['Date'])
    logging.info( msg = f'Bond Prices : \n { df_Bond_Prices[df_Bond_Prices.BondId ==1].head(5)}')
    df_Bonds = dataParsing().readCsv(filePath=params.FilePath_Bond.value)
    df_Bonds['MaturityDate'] = pd.to_datetime(df_Bonds['MaturityDate'])
    logging.info(msg=f'Bond Details : \n {df_Bonds.head(5)}')


    ## Merge dataframe df_Bond_Prices & df_Bonds
    df_ = df_Bond_Prices.merge(df_Bonds,on='BondId',how='left')
    logging.info(msg=f'Dataframe Merged : \n {df_.head(5)}')

    ## Date Difference Calculation - in year:
    df_["time_to_expiry"] = dataParsing().time_to_expiry(Date=df_["Date"],Expiry=df_["MaturityDate"])
    logging.info(msg=f'Time to Expiry calculation  : \n {df_.head(5)}')

    ### 2 - Calculate zero rates
    ## Spot Rate Calculation
    #------------------------------------------------------------------
    df_["SpotRate"]= ratesCalculation().zeroRate(price = df_['Price'].values,time_to_expiry=df_['time_to_expiry'].values,ContinuosOrDiscrete=params.Conitnuos.value, faceValue=params.bondDivisor.value)
    logging.info(msg=f' Continuously compounded Spot Rate   : \n {df_.head(5)}')
    yield_curve = df_.pivot(index='Date', columns='BondId', values='SpotRate')
    logging.info(msg = f'Yield Curve  : \n {yield_curve.head(5)}')

    tenor = df_.pivot(index='Date', columns='BondId', values='time_to_expiry')
    logging.info(msg=f"Tenor  : \n {tenor.head(5)}")

    ### 3 - Fit yield curve model
    #-----------------------------------------------------------------------------
    ## SpotRate Calculation for different Lambda values using Nelson Siegel Model -->  NS paramters based on  highest RSquared Value
    output_parameters, output_NS = simulation().nelsonSeigal(yield_curve=yield_curve,tenor=tenor,columns=yield_curve.columns,parameterCalibration=params.NelsonSiegel.value,shape=params.shape.value)

    ## Graph -  Original Spot Rate and Predicted Values
    plt.figure(figsize=(10, 6))
    plt.title(f' Yield Curve :  Actual Spot Rates vs. NS Spot Rates ')
    plt.plot(yield_curve.columns.values,yield_curve.iloc[:1].T.values, label='Actual')
    plt.plot(yield_curve.columns.values,output_NS.loc[yield_curve.index[:1]].T.values,'--', label='Model')
    plt.ylabel('Zero Rates')
    plt.xlabel('Different Maturities')
    plt.legend()
    plt.savefig(params.FileOutpath.value + "/ActaulVsNSYieldCurve.png")
    plt.show()

    ## Stats Comparision
    stats = output_NS - yield_curve
    stats.max(axis =1).values
    stats.min(axis=1).values
    stats.std(axis=1).values
    statsOutput = pd.DataFrame([stats.max(axis =1).values,stats.min(axis=1).values,stats.std(axis=1).values,output_parameters["rsquared_lst"].values,output_parameters["lambda"].values]).T
    statsOutput.columns = ["Max","Min","Std","rsquared_lst","lambda"]
    logging.info(msg=f'Stat output based on comparision btween actual vs predicted spot rates  : \n {statsOutput.head(5)}')

    ## CSV file generation
    logging.info(msg="Calibration completed")
    output_parameters.to_csv(params.FileOutpath.value+"/investcloud_NS_paramters.csv")
    logging.info("investcloud_NS_paramters.csv file generated sucessfully")
    output_NS.to_csv(params.FileOutpath.value+"investcloud_NS_predicted_spot.csv")
    logging.info("investcloud_NS_predicted_spot.csvfile generated sucessfully")
    statsOutput.to_csv(params.FileOutpath.value + "/investcloud_NSActualPreredictedStatsComp.csv")
    logging.info("investcloud_NSActualPreredictedStatsComp.csv generated sucessfully")
    logging.info('Completed')

    ### 4 - Simulate prices of artificial bonds
    ## Bond  Price  Calculation
    col = ['Date','spotRate']
    dummyRates = [[0.5,0.0150],[1,0.0215],[1.5,0.0253],[2,0.0294],[2.5,0.031],[3,0.0362]]
    data=pd.DataFrame(dummyRates, columns=col)
    bondPrice = bondPricing().zero_curve_bond_price(faceValue=100,Maturity=3,couponPerecentageAnnually=4,frequency=params.semianualy.value,callibration=params.NelsonSiegel.value,
                                        spotRate=data['spotRate'].values,time_to_expiry=data['Date'].values)

    logging.info(msg=f'Bond cash flow  : \n {bondPrice}')
    bondPrice.to_csv(params.FileOutpath.value+"/bond_pricing.csv")
    logging.info (msg="Details of bond price cash flow saved in spreadsheet : bond_pricing.csv")
    logging.info(msg=f' Present Price  of Bond based on NS method : {bondPrice["presentValue"].sum()}')

    ## 5 sketch how you would calculate risk measures such as VaR of (portfolios of) bonds
    ## Portfolio VAR Calculation
    Var().linearMethod_delta_noramal(yieldR=[0.08, 0.08], maturity=[5, 8], corelation=0.7, coupon=[0.04, 0.04],
                                    weightage=[0.70, 0.30], Dailyvolatility=[0.01, 0.01],undiversifiedVar="Yes")
    Var().nonLinearMethod_delta_gamma_noramal(yieldR=[0.08, 0.08], maturity=[5, 8], corelation=0.7, coupon=[0.04, 0.04],
                                     weightage=[0.70, 0.30], Dailyvolatility=[0.01, 0.01])

    Var().fullValualtionMethod(yieldR=[0.08, 0.08], maturity=[5, 8], corelation=0.7, coupon=[0.04, 0.04],
                                     weightage=[0.70, 0.30], Dailyvolatility=[0.01, 0.01])

if __name__ == "__main__":
    main()