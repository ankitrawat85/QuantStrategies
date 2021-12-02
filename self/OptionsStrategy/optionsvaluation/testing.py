import pandas as pd
desired_width = 320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns', 20)
import numpy as np
from scipy.optimize import least_squares
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
    beta =0.8
    for i, vol in enumerate(vols):
        err += (vol - SABR(F, strikes[i], T,
                           x[0], beta, x[1], x[2]))**2

    return err


df_date = pd.read_csv("sabrsigma.csv",header=0)
#df.Date = pd.to_datetime(df.Date)
#df.sort_values(by="Date", inplace = True)
#df.to_csv("sabrsigma.csv")
#df_date = df[df["Date"] == "2021-01-11"]
#df_date['sabrsigma_1'] = df_date.apply(lambda x : SABR(810.7, x['Strike Price'], 0.980556, 0.665595, 0.8, -0.670819, 0.197296), axis = 1)
#df_date['sabrsigma_2'] = df_date.apply(lambda x : SABR(x["futures_price"], x['Strike Price'], x["time_diff"], x["alpha"], x["Beta"] ,x["rho"], x["nu"]), axis = 1)

initialGuess = [0.02, 0.2, 0.1]
res = least_squares(lambda x: sabrcalibration(x,df_date["Strike Price"],df_date["impliedvolatility"],810.7,0.980556),initialGuess)
alpha = res.x[0]
rho = res.x[1]
nu = res.x[2]
beta = 0.8
df_date['sabrsigma_new'] = df_date.apply(lambda x : SABR(x["futures_price"], x['Strike Price'], x["time_diff"], alpha, beta, rho, nu), axis = 1)
print(df_date)
print('Calibrated SABR model parameters: alpha = %.3f, beta = %.1f, rho = %.3f, nu = %.3f' % (alpha, beta, rho, nu))
df_date.to_csv("final.csv")
import matplotlib.pylab as plt
plt.figure(figsize = (12, 7))
plt.scatter(df_date['Strike Price'],df_date['impliedvolatility'], alpha = 0.8, c = 'g' ,marker = 's', label = 'Market')
plt.plot(df_date['Strike Price'], df_date['sabrsigma'], '--r', linewidth = 3, label = 'SABR model')
plt.ylabel('Implied Vol', fontsize = 20)
plt.xlabel('Strike', fontsize = 20)
plt.ylim(0.2, 0.4)
plt.legend(fontsize = 16);
plt.show()

