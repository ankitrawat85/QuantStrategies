from sklearn.preprocessing import LabelEncoder
from sklearn  import tree

## personal files

## System Libraries

## Graph
import numpy as np
import random
import warnings
import pandas as pd
import sys
'''System Path configuration'''
sys.path.append('/Users/ankitrawat/Desktop/smu/Classes/Self/Code/Quant/venv/commonFunctions')

'''Import personal libraries '''

''' Import ML libraries'''
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn import linear_model,metrics
from sklearn import preprocessing
from sklearn import model_selection
from pandas import read_csv
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import validation_curve
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import  Ridge,Lasso, ElasticNet
from sklearn.metrics import mean_squared_error

'''Graph '''
import matplotlib.pyplot as plt


'''Stock Download Class '''
class stockData():

    def __init__(self,*args,**kargs):
        self.nse50 = "https://en.wikipedia.org/wiki/NIFTY_50"
        self.datasite = "yahoo"
        print (self.nse50)

    def processing(self,field):
        '''Directory Path'''
        sys.path.append('/Users/ankitrawat/Desktop/smu/Classes/Self/Code/Quant/venv/commonFunctions')
        from datapull import data, stationary,models
        #print (os.path.abspath(__file__))

        '''Nifty 50 List - Wikipidia '''
        df_ = pd.read_html(self.nse50)[1]
        df_ = df_.iloc[:,1:3]
        df_nse50 = df_[df_["Sector"] == "Banking"]["Symbol"]
        print ("after removing banking -->")
        print (df_nse50)
        '''Data pull for list of stocks'''
        data_start = "2010-01-01"
        data_end  = "2021-04-30"
        stock_list  = pd.DataFrame(df_nse50).stack().values
        print (stock_list)
        df_ = data().downloadData(self.datasite,stock_list, data_start, data_end,field)
        return df_


'''Step1 : Stock download '''
df_Close = pd.DataFrame((stockData().processing("Close")["SBIN"])).rename( columns = {"SBIN" : "Close"})
df_Open = pd.DataFrame((stockData().processing("Open")["SBIN"])).rename( columns = {"SBIN" : "Open"})
df_High = pd.DataFrame((stockData().processing("High")["SBIN"])).rename( columns = {"SBIN" : "High"})

df_  = pd.concat([df_Open,df_High,df_Close], axis =1)
df_ = df_.pct_change(periods=30).dropna().resample('M').mean()
print (df_)

''' inputs and Output  '''
x =  df_[["Open"]].values
y = df_["Close"].values

'''
Linear regresiion 
'''
regr = linear_model.LinearRegression()
regr.fit(x,y)
print (regr.coef_)
print (regr.intercept_)

''' To check variance 
Total Sum of square = ( y - y.mean ) **2 
Explained sum of square  = ( y.predict - y.mean ) **2
resudial sum of square  - ( y.predict - y ) **2 
'''
print (" SSR : {}, ESS : {}, RSS : {}".format(np.sum((y  - np.mean(y))**2),np.sum((regr.predict(x) - np.mean(y))**2), np.sum((regr.predict(x) - y)**2)))

''' R Square '''
print ("R Square : {}".format(regr.score(x,y)))
print ( "R Square using formula : {}".format(np.sum((y  - np.mean(y))**2) /np.sum((regr.predict(x) - np.mean(y))**2)))

'''Metrics '''
y_predit = regr.predict(x)
print ("explained_variance_score  : ".format(metrics.explained_variance_score(y,y_predit)))
print ("mean_absolute_error  : ".format(metrics.mean_absolute_error(y,y_predit)))
print ("mean_squared_error  : ".format(metrics.mean_squared_error(y,y_predit)))

y = pd.DataFrame(y)
print (y)
y_predit = pd.DataFrame(y_predit)
print (y_predit)
plt.scatter(y_predit,y)
#plt.show()

'''Graph'''
plt.scatter(df_["Open"],df_["Close"])
print ("mins")
min_x = df_["Open"].min()
max_x = df_["Open"].max()
difference  = ( max_x -  min_x  )/200
print (min_x,max_x,difference)
print(np.arange(min_x,max_x,difference).reshape(200,1))
lx = np.arange(min_x,max_x,difference).reshape(200,1)
print ("predict")
print (regr.predict(lx))
plt.plot(lx,regr.predict(lx), color = 'red', linewidth =3 )
#plt.show()

'''

polynomial Processing 

'''
#from sklearn import preprocessing
#from sklearn import model_selection

x =  df_[["Open","High"]].values
y = df_["Close"].values

from pandas import read_csv
from sklearn.linear_model import LinearRegression
from mlxtend.evaluate import bias_variance_decomp


## Polynomial
bias_variance = pd.DataFrame( columns= {"variance","bias"})
bias_variance1 = pd.DataFrame()
for i in np.arange(1,12,1):
   #print (i)
    x = df_[["Open", "High"]].values
    y = df_["Close"].values
    ploy2 = preprocessing.PolynomialFeatures(degree=i, interaction_only=True)
    x2 = ploy2.fit_transform(x)
    '''Data Split'''
    print (x.shape)
    x2_train,x2_test,y2_train,y2_test = model_selection.train_test_split(x2,y,test_size=0.2)
    ## linear regression Model and predection
    regr2 = linear_model.LinearRegression()
    regr2.fit(x2_train,y2_train)
    regr2
    Prediction = regr2.predict(x2_test)
    print ("regr scrore  %.6f" % regr2.score(x2_test,y2_test))
    Variance = np.var(Prediction) # Where Prediction is a vector variable obtained post the # predict() function of any Classifier.
    print ("Variance : {} ".format(Variance))
    SSE = np.mean((Variance - y2_test)** 2) # Where Y is your dependent variable. # SSE : Sum of squared errors.
    print ("SSE : {} ".format(SSE))
    Bias = SSE - Variance
    print ("Bias :  {} ".format(Bias))
    x = pd.DataFrame([Variance,Bias]).transpose()
    print (x)
    mse, bias, var = bias_variance_decomp( regr2 , x2_train, y2_train, x2_test, y2_test, loss='mse', num_rounds=200, random_seed=1)
    s = pd.DataFrame([var, bias]).transpose()
    print ("SSSSSS")
    print (s)
    bias_variance_code = bias_variance1.append(s)
    bias_variance = bias_variance.append(x)

bias_variance =  bias_variance.reset_index()[[0,1]].rename(columns = {0:"Variance",1:"Bias"})
print ("bias_variance")
print (bias_variance)
print ("bias_variance1")
print (bias_variance)

#from sklearn.model_selection import validation_curve
#from sklearn.pipeline import make_pipeline
#from sklearn.linear_model import LinearRegression
#from sklearn.preprocessing import PolynomialFeatures
degrees = np.arange(1, 21)
x = df_[["Open", "High"]].values
y = df_["Close"].values
model = make_pipeline(PolynomialFeatures(), LinearRegression())

# The parameter to vary is the "degrees" on the pipeline step
# "polynomialfeatures"
train_scores, validation_scores = validation_curve(
                 model, x, y,
                 param_name='polynomialfeatures__degree',
                 param_range=degrees)

# Plot the mean train error and validation error across folds
plt.figure(figsize=(6, 4))
plt.plot(degrees, validation_scores.mean(axis=1), lw=2,
         label='cross-validation')
plt.plot(degrees, train_scores.mean(axis=1), lw=2, label='training')

plt.legend(loc='best')
plt.xlabel('degree of fit')
plt.ylabel('explained variance')
plt.title('Validation curve')
plt.tight_layout()
plt.show()

''''
RiRidge,Lasso, ElasticNetdge 

'''
##from sklearn.linear_model import  Ridge,Lasso, ElasticNet
##from sklearn.metrics import mean_squared_error
df_ridge  = Ridge()
df_lasso = Lasso()
df_ElasticNet =  ElasticNet()
x = df_[["Open", "High"]].values
y = df_["Close"].values
x2_train,x2_test,y2_train,y2_test = model_selection.train_test_split(x,y,test_size=0.2)
df_ridge.fit(x2_train,y2_train)
y_pred =  df_ridge.predict(x2_test)
c =  np.sqrt(mean_squared_error(y2_test,y_pred))
print (c)
print (df_ridge.score(x2_test, y2_test))
df_lasso.fit(x2_train,y2_train)
print(df_lasso.score(x2_test, y2_test))
y_pred =  df_lasso.predict(x2_test)
c =  np.sqrt(mean_squared_error(y2_test,y_pred))

df_ElasticNet.fit(x2_train,y2_train)
print(df_ElasticNet.score(x2_test, y2_test))
y_pred =  df_ElasticNet.predict(x2_test)
c =  np.sqrt(mean_squared_error(y2_test,y_pred))

print(c)

'''
OLS, GRADIENT 

MSE 

'''
print(x)

''''
hr_diff = np.zeros((num_row, 2))
'''
for i in range(num_row):
    hr_diff[i, 0] = # calculate the difference in hours from a peak hour
    hr_diff[i, 1] = # calculate the difference in hours from a peak hour

'''
for i in  range(len(days)):
    hr_diff[i, 0] = peak_hour - bikes["hr"].iloc[i]
    hr_diff[i, 1] = peak_hour - bikes["hr"].iloc[i]


bikes["hr_diff_x"] = hr_diff[:,0]
bikes["hr_diff_y"] = hr_diff[:,1]


#selected_cols = [ 'yr', 'mnth', 'hr', 'holiday', 'workingday', 'temp', 'atemp', 'hum', 'windspeed','hr_diff_x','hr_diff_y']
selected_cols = ['yr','hum','mnth','workingday','hr_diff_x','temp']
x5 = bikes[selected_cols].values
x5_train, x5_test = x5[train,:], x5[~train,:]
x5_train = min_max_scaler.fit_transform(x5_train)
x5_test = min_max_scaler.transform(x5_test)



from sklearn.linear_model import SGDRegressor
reg = SGDRegressor(max_iter=7000 ,alpha = 0.0000000008, tol=1e-3,penalty="l2")
reg.fit(x5_train, y_train)

score = reg.score(x5_train, y_train)
print("R-squared:", score)

''''''
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
degree=2
polyreg=make_pipeline(PolynomialFeatures(degree),linear_model.Lasso(alpha = 0.1))
polyreg.fit(x5_train, y_train)
score = polyreg.score(x5_train, y_train)
print("R-squared:", score)



from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

poly_reg = PolynomialFeatures(degree=2)
poly_x_inliers = poly_reg.fit_transform(x5_train)

regressor = LinearRegression()
regressor.fit(poly_x_inliers, y_train)

reg1 = linear_model.Lasso(alpha = 0.1)
reg1.fit(poly_x_inliers, y_train)
print ("linear model lasso")
print(reg1.score(poly_x_inliers, y_train))
print(reg1.coef_)

import statsmodels.api as sm
model = sm.OLS(y_train,poly_x_inliers)
results = model.fit()
print(results.summary())


'''
lasso = linear_model.Lasso(alpha = 1)
lasso.fit(x5_train, y_train)
print('alpha:', 1.0)
print('R2 score:', lasso.score(x5_test, y_test))
for i in range(len(selected_cols)):
    print(selected_cols[i], '\t',i, lasso.coef_[i])
'''
    


# build x5 as the cell above
# build a regression model with x5_train after normalization

'''

from statsmodels.nonparametric import kernel_regression
kernel_regression