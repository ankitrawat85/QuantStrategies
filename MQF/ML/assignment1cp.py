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
import numpy as np
import pandas as pd
desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',30)
from datetime import datetime
import matplotlib.pyplot as plt
import warnings
from pandas.core.common import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

'''
Import data 
'''
from sklearn.datasets import load_boston
bikes = pd.read_csv("/Users/ankitrawat/Desktop/smu/Classes/Term5/ML/Assignment/bike_sharing.csv")
num_row = bikes.shape[0]
print(num_row)

'''split data'''
np.random.seed(2021)
train = np.random.choice([True, False], num_row, replace = True, p = [0.5, 0.5])

y1 =bikes['registered']
y = y1.values
#y_train, y_test = y[train], y[~train]

selected_cols = ['season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed']
x = bikes[selected_cols].values
x1 = bikes[selected_cols]

''' dummies   '''
'''   Creation of Dummy Variables   '''
#season, weekday and weathersit?
season =pd.get_dummies(x1 ["season"],"season_")
x1 = pd.concat([x1 ,season], axis =1)
weekday =pd.get_dummies(x1 ["weekday"],"weekday_")
x1 = pd.concat([x1 ,weekday], axis =1)
#print (x1 ["weathersit"].unique)

x1 ['weathersit_=_1'] = (1 * (x1 ['weathersit'] == 1))
x1 ['weathersit_>=_2'] = (1 * (x1 ['weathersit'] >= 2))
x1 ['weathersit_>=_3'] = (1 * (x1 ['weathersit'] >= 3))
#x1 .reset_index(inplace = True)

from datetime import date
num_row = len(x1)
days = np.zeros(num_row)
for i in  range(len(days)):
    date_format = "%Y-%m-%d"
    d = "01"
    m = "01"
    Current_date = datetime.strptime(bikes["dteday"].iloc[i],date_format)
    d0 = date(Current_date.year,Current_date.month , Current_date.day)
    Current_date_year = Current_date.strftime("%Y")
    starting_Date = str(Current_date_year)+"-"+m+"-"+d
    starting_Date_year = datetime.strptime( starting_Date ,date_format)
    d1 = date(starting_Date_year.year,starting_Date_year.month , starting_Date_year.day)
    days[i] = abs(Current_date - starting_Date_year).days +1

x1['days'] = days
#print (pd.concat([bikes["hr"],bikes['registered']], axis =1).reset_index()[["hr","registered"]].groupby("hr").sum().sort_values(["registered"]))
peak_hour = pd.concat([bikes["hr"],bikes['registered']], axis =1).reset_index()[["hr","registered"]].groupby("hr").sum().sort_values(["registered"], ascending=False).index[0]
print ("peak hour {} ".format(peak_hour))

hr_diff = np.zeros((num_row, 2))
for i in  range(len(days)):

    hr_diff[i, 0] = peak_hour - bikes["hr"].iloc[i]
    hr_diff[i, 1] = peak_hour - bikes["hr"].iloc[i]


x1["hr_diff_x"] = hr_diff[:,0]
x1["hr_diff_y"] = hr_diff[:,1]
# build x5 as the cell above
# build a regression model with x5_train after normalization

'''normalization'''
from sklearn import preprocessing
train = np.random.choice([True, False], num_row, replace = True, p = [0.5, 0.5])
x_train, x_test = x1.iloc[train,:], x1.iloc[~train,:]
x_test = x_test.reset_index().drop(columns =  "index")
x_train = x_train.reset_index().drop(columns =  "index")

y_train, y_test = y1[train], y1[~train]
y_train = y_train.reset_index().drop(columns = {"index"})
y_test = y_test.reset_index().drop(columns = {"index"})

#print("x_train {} and x_test {}  and y_train {} and y_test {}".format(x_train.shape,x_test.shape,y_train.shape,y_test.shape))

'''
temp,atemp,hum,windspeed
'''
col =  {"temp","atemp","hum","windspeed","hr_diff_x","hr_diff_y"}
print ("train shape")
min_max_scaler = preprocessing.MinMaxScaler()

train = pd.DataFrame(min_max_scaler.fit_transform(x_train[col].values),columns= col)
test = pd.DataFrame(min_max_scaler.transform(x_train[col].values),columns= col)

x_train = pd.concat([x_train.drop(columns = col),train],axis =1)
x_test = pd.concat([x_test.drop(columns = col),test],axis =1)

#print (x_test)
#conside_col = {'season', 'yr', 'hr', 'holiday', 'weekday', 'workingday', 'weathersit', 'season__1', 'season__2', 'season__3', 'season__4', 'weekday__0', 'weekday__1', 'weekday__2', 'weekday__3', 'weekday__4', 'weekday__5', 'weekday__6', 'weathersit_=_1', 'weathersit_>=_2', 'weathersit_>=_3', 'days', 'hr_diff_y',
      # 'atemp', 'windspeed', 'hum', 'temp', 'hr_diff_x'}
conside_col = { 'yr', 'holiday', 'workingday', 'season__1', 'season__2', 'season__3', 'season__4', 'weekday__0', 'weekday__1', 'weekday__2', 'weekday__3', 'weekday__4', 'weekday__5', 'weekday__6', 'weathersit_=_1', 'weathersit_>=_2', 'weathersit_>=_3', 'days', 'hr_diff_y','atemp', 'windspeed', 'hum', 'temp', 'hr_diff_x'}

#conside_col = {'season__1','season__2','season__3','season__4','holiday','workingday','weekday__0','weathersit_>=_3','weathersit_>=_2','weathersit_=_1','hr_diff_y','hr_diff_x','hum','temp'}
#conside_col = {'season__1','season__2','season__3','season__4','yr','holiday','workingday','weathersit_>=_3','hr_diff_y','hum','temp'}
#conside_col =  {"temp","atemp","hum","windspeed","hr_diff_x","hr_diff_y"}
x_train1 = x_train[conside_col]
class normal():
    def normalization(self,df_):
        for i in pd.DataFrame(df_).columns:
            if (  str(i).lower() in ["season__1","season__2","season__3","season__4",'weekday__2',"weekday__0","holiday","weathersit_=_1","weathersit_>=_3","weathersit_>=_2","weekday__1"]):
                df_[i] = df_[i].astype("bool")  *1


            elif ( str(i).lower() in ["temp","atemp","hum"] ):
                df_[i] = df_[i].astype("float64")

            elif (str(i).lower() in ["hr_diff_y","hr","hr_diff_x"]):
                df_[i] = df_[i].astype("float64")

            else:
                df_[i] = df_[i].astype("category")


        return df_

x_train1 = normal().normalization(x_train1)
df_ = pd.DataFrame(x_train1).drop(columns = {"weathersit_>=_3","days","season__2","windspeed","weathersit_>=_2","season__3","hr_diff_y","season__1","weathersit_=_1","weekday__6","weekday__2","weekday__3","weekday__1","atemp","holiday","weekday__5","weekday__4","weekday__0"})
#R squared :  0.3213846269236058
print(df_.head(10))
'''
from sklearn.decomposition import PCA
pca = PCA(n_components = 7)
x_train3 = pca.fit_transform(df_)

# hr_diff_x,hum
# Calculate the variance explained by priciple components
print('Variance of each component:', pca.explained_variance_ratio_)
print('\n Total Variance Explained:', round(sum(list(pca.explained_variance_ratio_))*100, 2))
loading = pca.components_.T
df_loadings  = pd.DataFrame(loading,columns = ['PC-1','PC-2','PC-3','PC-4','PC-5','PC-6','PC-7'], index = df_.columns).abs().sum(axis=1)
print (df_loadings)
# R squared :  0.33599117593721006
'''

#df_ = pd.DataFrame(x_train1).drop(columns = {"season__1","hr_diff_y","weathersit_=_1","season__3","weekday__6","weekday__2","weekday__3","weathersit_>=_2","windspeed","weekday__1","season__2","atemp","days","holiday","weekday__5","weekday__4","weekday__0"})
#regr2 = linear_model.LinearRegression()
regr2 = linear_model.Lasso(alpha = 0.1)
#regr2 = linear_model.Ridge(alpha =0.3)
regr2.fit(df_,y_train)
print("R squared :  {} ".format( regr2.score(df_,y_train)))
print ("co efficient :",regr2.coef_)


from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
degree=2
polyreg=make_pipeline(PolynomialFeatures(degree),linear_model.Lasso(alpha = 0.1))
polyreg.fit(df_, y_train)
print (polyreg.n_features_in_)
score = polyreg.score(df_, y_train)
print("R-squared poly:", score)
x  = PolynomialFeatures(degree)
x.n_features_in_

import statsmodels.api as sm
#print(pd.DataFrame(x_train3).drop(columns = {9,11}))
model = sm.OLS(y_train, df_)
results = model.fit()
print(results.summary())




'''
print ("List of features has highest impact : ")
print(pd.DataFrame(pca.components_,columns=x_train1.columns,index = ['PC-1','PC-2','PC-3','PC-4','PC-5','PC-6']).abs().sum(axis=0))
print("original shape:   ", x_train1.shape)
print("transformed shape:", x_train3.shape)

loading = pca.components_.T
df_loadings  = pd.DataFrame(loading,columns = ['PC-1','PC-2','PC-3','PC-4','PC-5','PC-6'], index = x_train1.columns)

print (df_loadings)


conside_col =  {"season__3","yr","season__2","season__1","workingday","days"}
conside_col =  {"season__3","yr","season__2","season__1","workingday","days"}

#print ("Explained Variance : {}".format(explained_variance))
z = x_train[conside_col]
print (pd.DataFrame(z))
print (pd.DataFrame(z).dtypes)

regr2 = linear_model.LinearRegression()
regr2.fit(pd.DataFrame(z),y_train)
print("R squared :  {} ".format( regr2.score(pd.DataFrame(z),y_train)))
'''