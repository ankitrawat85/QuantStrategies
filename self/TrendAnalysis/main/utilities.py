#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 29 11:42:53 2021

@author: ankitrawat
"""

''' pre Requsite '''
from sklearn import preprocessing
import datetime
import pandas as pd
import pandas_datareader as pdr
import numpy as np
import statsmodels.api as sm
import warnings

import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

## Libraries - Stats Model
import statsmodels.tsa.stattools
from statsmodels.tsa.stattools import adfuller
import statsmodels.tsa.x13
from statsmodels.tsa.x13 import x13_arima_select_order, _find_x12
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import acf, pacf
import statsmodels.graphics.tsaplots as tsaplots

from sklearn import preprocessing

warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt
import statsmodels.tsa.stattools
from statsmodels.tsa.stattools import adfuller
import statsmodels.tsa.x13
from statsmodels.tsa.x13 import x13_arima_select_order, _find_x12
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import acf, pacf
import statsmodels.graphics.tsaplots as tsaplots

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARMA

## Grah
import seaborn as sns
import numpy as np
import scipy.stats as stats
import random
import warnings
import matplotlib.pyplot as plt


print ("hello")