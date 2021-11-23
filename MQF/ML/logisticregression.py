import pandas as pd
import numpy as np

class logiscticregression():

    def __init__(self,lr = 0.01 , n_iters = 3000):
        self.lr = lr
        self.n_iters = n_iters
        self.weight = none
        self.bias = none

    def fit (self,X,Y):
        n_samples,n_features = X.shape
        self.weight = np.zeros(n_features)
        self.bias = 0

        ## gradient descent
        for _ in range (self.n_iters):
            linear_model = np.dot(X,self.weight) * self.bias
            y_predicted = self._sigmoid(linear_model)
            dw = (1/n_samples) * np.dot(X.T,(y_predicted-Y))
            db = (1/n_samples) * np.sum(y_predicted-Y)
            self.weight -= dw  *  self.lr
            self.bias -= db * self.lr

    def predict (self,X):
        linear_model = np.dot(X, self.weight) * self.bias
        y_predicted = self._sigmoid(linear_model)
        y_predicted_cls = [ 1 if i >0.5 else 0 for i in y_predicted ]
        return y_predicted_cls

    def _sigmoid(self,x):
        return (1/(1 + np.exp(-x)))

