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
pd.set_option('display.max_columns',20)
from datetime import datetime
import matplotlib.pyplot as plt
'''
Import data 
'''
from sklearn.datasets import load_boston
df_  = pd.read_csv("/Users/ankitrawat/Desktop/smu/Classes/Term5/ML/Assignment/bike_sharing.csv")
df_.set_index("dteday", inplace = True)
x = df_.iloc[:,1:12]
y = df_.iloc[:,-1]

'''   '''


'''Split Data'''
x2_train,x2_test,y2_train,y2_test = model_selection.train_test_split(x,y,test_size=0.7)
#print (x2_train['yr'])

df_nor_test = x2_test.copy()
df_nor_train = x2_train.copy()

'''Normalization -- temp , atemp and hum '''
df_1  = x2_test.copy()
df_2  = x2_train.copy()

class normal():
    def normalization(self,df_):
        for i in pd.DataFrame(df_).columns:
            if (  str(i).upper() == str("workingday").upper()):
                df_[i] = df_[i].astype("bool")


            elif ( str(i).lower() in ["temp","atemp","hum"] ):
                df_[i] = df_[i].astype("float64")
                df_[i] = preprocessing.minmax_scale(df_[i], axis=0)

            elif (str(i).lower() in ["weathersit","hr"]):
                df_[i] = df_[i].astype("int64")

            else:
                df_[i] = df_[i].astype("category")


        return df_

df_test = normal().normalization(x2_test.copy())
df_train = normal().normalization(x2_train.copy())


'''   Creation of Dummy Variables   '''
#print (df_test["season"].unique())
#print (df_test["weekday"].unique())
#print (df_test["weathersit"].unique())
season =pd.get_dummies(df_test["season"],"season_")
df_test = pd.concat([df_test,season], axis =1)
weekday =pd.get_dummies(df_test["weekday"],"weekday_")
df_test = pd.concat([df_test,weekday], axis =1)
print (df_test["weathersit"].unique)
#season, weekday and weathersit?
df_test['weathersit_=_1'] = (1 * (df_test['weathersit'] == 1))
df_test['weathersit_>=_2'] = (1 * (df_test['weathersit'] >= 2))
df_test['weathersit_>=_3'] = (1 * (df_test['weathersit'] >= 3))
df_test.reset_index(inplace = True)
#print(df_test["dteday"].iloc[1] - df_test["dteday"].iloc[2])
#df_test["dteday"] =  pd.to_datetime(df_test["dteday"])
#print(datetime.strftime(df_test["dteday"].iloc[1], '%d-%B-%y'))
#print(datetime.strftime(df_test["dteday"].iloc[2], '%d-%B-%y'))

from datetime import date

days = np.zeros(len(df_test))
delta = np.zeros(len(df_test))
for i in  range(len(days)):
    date_format = "%Y-%m-%d"
    d = "01"
    m = "01"
    Current_date = datetime.strptime(df_test["dteday"].iloc[i],date_format)
    d0 = date(Current_date.year,Current_date.month , Current_date.day)
    Current_date_year = Current_date.strftime("%Y")
    starting_Date = str(Current_date_year)+"-"+m+"-"+d
    starting_Date_year = datetime.strptime( starting_Date ,date_format)
    d1 = date(starting_Date_year.year,starting_Date_year.month , starting_Date_year.day)
    delta[i] = abs(d1 - d0).days +1
    days[i] = abs(Current_date - starting_Date_year).days +1

df_test['days'] = days
#df_test['delta'] = delta
#print(df_test[df_test["days"] > 365])

'''

Peak hour 

'''
print (df_test)
df_1_cnt = pd.concat([x2_train["hr"],y2_train], axis =1).reset_index()[["hr","cnt"]].groupby("hr").sum().sort_values(["cnt"], ascending=False).index[0]
print (df_1_cnt)

hr_diff = np.zeros((len(days), 2))
for i in  range(len(days)):

    hr_diff[i, 0] = df_1_cnt - df_test["hr"].iloc[i]
    hr_diff[i, 1] = df_1_cnt - df_test["hr"].iloc[i]

df_test["hr_diff_x"] = hr_diff[:,0]
df_test["hr_diff_y"] = hr_diff[:,1]

print(df_test.head(10))
# build x5 as the cell above
# build a regression model with x5_train after normalization