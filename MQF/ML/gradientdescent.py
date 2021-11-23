'''
Here we will be learning gradient descent
types : batch and stochastic
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn import model_selection
from pandas import read_csv
from sklearn.model_selection import train_test_split

x_data = np.array([160, 171, 182, 180, 154]).reshape((5, 1))
x_mean = np.mean(x_data)
y_data = np.array([178, 179, 182, 187, 154]).reshape((5, 1))
y_mean = np.mean(y_data)
n = len(x_data)
import warnings
warnings.filterwarnings("ignore")
from sklearn.datasets import load_boston
from random import seed
from random import randrange
from csv import reader
from math import sqrt
from sklearn import preprocessing
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prettytable import PrettyTable
from sklearn.linear_model import SGDRegressor
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
'''
class testRegression():
    b0 = 0
    b1 = 0
    y_pred = 0
    error = 0
    alpha = 0.00001
    epoch  = 2

    def fit(self, X, Y):
        Covariance = 0
        Variance = 0
        for i in range(n):
            Covariance += (x_data[i] - x_mean) * (y_data[i] - y_mean)
            Variance += (x_data[i] - x_mean) ** 2
        self.b1 = Covariance / Variance
        self.b0 = y_mean - (self.b1 * x_mean)
        return self.b0, self.b1

    def loss_function(self,xi):
        self.y_pred = self.b0 + (self.b1 * xi)
        self.error = (y_mean - self.y_pred)
        sse = np.square(self.error)
        mse = np.mean(sse)
        return mse

    def loss_optimizer(self, Xi):
        print(Xi)
        for i in range(self.epoch):
            print ("epoch {} ".format( i))
            derivative_b1 = (-2 / n) * np.sum(Xi * self.error)
            derivative_b0 = (-2 / n) * np.sum(self.error)
            self.b1 = self.b1 - self.alpha * derivative_b1
            self.b0 = self.b0 - self.alpha * derivative_b0
        return self.b0, self.b1

model = testRegression()
print(model.fit(x_data, y_data))
print(model.loss_function(x_data))
print(model.loss_optimizer(x_data))
print(model.loss_function(x_data))

model1 = LinearRegression()
print(model1.fit(x_data, y_data))
print(model1.intercept_)
print(model1.coef_)
'''
def gradent_regressor(X, y, learning_rate=0.2, n_epochs=500, k=40):
    w = np.random.randn(1, 13)  # Randomly initializing weights
    b = 0  # Random intercept value
    epoch = 1
    X_tr  = X.values
    y_tr = y.values
    w = np.array([np.zeros(13)])
    y_pred = []
    while epoch <= n_epochs:
        #y_pred = []
        Lw = w
        Lb = b
        #print (np.array(X).shape[0])
        for i in range (1,np.array(X).shape[0],1):
            #print(np.dot(X_tr[i],w.T))
            #print (y_tr[i] - np.dot(X_tr[i], w.T))
            Lw = (-2 / (np.array(X).shape[0]) * X_tr[i]) * (y_tr[i] - np.dot(X_tr[i], w.T) - b)
            Lb = (-2 / (np.array(X).shape[0])) * (y_tr[i] - np.dot(X_tr[i], w.T) - b)

        w = w - learning_rate * Lw
        b = b - learning_rate * Lb
        epoch = epoch +1


    y_predicted = np.dot(X_tr, w.T)
    y_pred.append(y_predicted)
    #print(len(y_predicted))
    #print (len(y_pred))
    #print (len(y_tr))
    loss = mean_squared_error(y_predicted,y_tr)
    #print ("EPoch : {} and lostss : {}".format(epoch,loss))
    #print (w)
    #print(b)
    return w,b,epoch,loss


X = load_boston().data
Y = load_boston().target
# split the data set into train and test
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=0)
scaler = preprocessing.StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
X_train = pd.DataFrame(data = X_train, columns=load_boston().feature_names)
X_train['Price'] = list(y_train)
X_test = pd.DataFrame(data = X_test, columns=load_boston().feature_names)
X_test['Price'] = list(y_test)
gradent_regressor(X_test.iloc[:, 0:13],X_test["Price"] )


def sgd_regressor(X, y, learning_rate=0.2, n_epochs=1000, k=40):
    w = np.random.randn(1, 13)  # Randomly initializing weights
    b = np.random.randn(1, 1)  # Random intercept value

    epoch = 1

    while epoch <= n_epochs:

        temp = X.sample(k)

        X_tr = temp.iloc[:, 0:13].values
        y_tr = temp.iloc[:, -1].values

        Lw = w
        Lb = b

        loss = 0
        y_pred = []
        sq_loss = []

        for i in range(k):
            Lw = (-2 / k * X_tr[i]) * (y_tr[i] - np.dot(X_tr[i], w.T) - b)
            Lb = (-2 / k) * (y_tr[i] - np.dot(X_tr[i], w.T) - b)

            w = w - learning_rate * Lw
            b = b - learning_rate * Lb

            y_predicted = np.dot(X_tr[i], w.T)
            y_pred.append(y_predicted)

        loss = mean_squared_error(y_pred, y_tr)

        #print("Epoch: %d, Loss: %.3f" % (epoch, loss))
        epoch += 1
        learning_rate = learning_rate / 1.02

    return w, b

X = load_boston().data
Y = load_boston().target
# split the data set into train and test
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=0)
scaler = preprocessing.StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
X_train = pd.DataFrame(data = X_train, columns=load_boston().feature_names)
X_train['Price'] = list(y_train)
X_test = pd.DataFrame(data = X_test, columns=load_boston().feature_names)
X_test['Price'] = list(y_test)
#gradent_regressor(X_test.iloc[:, 0:13],X_test["Price"] )

def predict(x,w,b):
    y_pred=[]
    for i in range(len(x)):
        temp_ = x
        X_test = temp_.iloc[:,0:13].values
        y = np.asscalar(np.dot(w,X_test[i])+b)
        y_pred.append(y)
    return np.array(y_pred)



'''Gradient'''
w,b,epoch,loss = gradent_regressor(X_test.iloc[:, 0:13],X_test["Price"] )
print ("Gradient")
print(w)
print(b)
print(loss)
'''stochastic gradient'''
w,b = sgd_regressor(X_train,y_train)
print("stochastic gradient")
#y_pred_customsgd = predict(X_test,w,b)
#print(y_pred_customsgd)
print(w)
print(b)

'''
Gradient decent 

'''
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import sklearn.datasets as dt
from sklearn.model_selection import train_test_split


def gradient_descent(max_iterations, threshold, w_init,
                     obj_func, grad_func, extra_param=[],
                     learning_rate=0.05, momentum=0.8):
    w = w_init
    w_history = w
    f_history = obj_func(w, extra_param)
    delta_w = np.zeros(w.shape)
    i = 0
    diff = 1.0e10

    while i < max_iterations and diff > threshold:
        delta_w = -learning_rate * grad_func(w, extra_param) + momentum * delta_w
        w = w + delta_w

        # store the history of w and f
        w_history = np.vstack((w_history, w))
        f_history = np.vstack((f_history, obj_func(w, extra_param)))

        # update iteration number and diff between successive values
        # of objective function
        i += 1
        diff = np.absolute(f_history[-1] - f_history[-2])

    return w_history, f_history


from sklearn.linear_model import SGDRegressor
reg = SGDRegressor(max_iter=1000 , tol=1e-3)
reg.fit(x5_train, y_train)