#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.model_selection import train_test_split


# In[2]:


def getBrownian(dt = 0.01, num = 10000):
    list_brownian = []
    list_brownian_x = []
    list_brownian.append(0)
    list_brownian_x.append(0)
    for i in range(1, num):
        r = np.random.normal(0, np.sqrt(dt))
        print("r = ", r)
        list_brownian.append(r + list_brownian[i-1])
        list_brownian_x.append(dt + list_brownian_x[i-1])
    return(list_brownian_x, list_brownian)


# In[3]:


list_x, list_y = getBrownian(dt = 1, num = 5)


# In[4]:


list_x, list_y


# In[5]:


plt.plot(list_x, list_y)
plt.grid()


# In[6]:


def getGBM(dt = 0.01, num = 100, alpha = 0.0,  volatility = 0.01, S0 = 1):
    list_gbm_y = []
    list_gbm_y.append(S0)
    for i in range(1, num):
        r = np.random.normal(0, 1)
        S = list_gbm_y[i-1]
        dS = alpha*S*dt + volatility*S*r*np.sqrt(dt)
        list_gbm_y.append(S + dS)
    return(np.linspace(0.0, dt*(num-1), num), list_gbm_y)


# In[7]:


list_gbm_x, list_gbm_y = getGBM(dt = 0.01, num = 1000, alpha = 0.1,  volatility = 0.5, S0 = 2)


# In[8]:


plt.plot(list_gbm_x, list_gbm_y)
plt.grid()


# In[9]:


len(list_gbm_x), len(list_gbm_y)


# In[10]:


def getGBM_Correlated(dt = 0.01, num = 100, alpha = 0.0,  volatility = 0.01, S0 = 1, list_std_normal=0):
    list_gbm_y = []
    list_gbm_y.append(S0)
    for i in range(1, num):
        r = list_std_normal[i-1]
        S = list_gbm_y[i-1]
        dS = alpha*S*dt + volatility*S*r*np.sqrt(dt)
        list_gbm_y.append(S + dS)
    return(np.linspace(0.0, dt*(num-1), num), list_gbm_y)


# In[11]:


num_points = 10000
mean = [0, 0]
cov = [[1, 0.5], [0.5, 1]]  # diagonal covariance
std_normal1, std_normal2 = np.random.multivariate_normal(mean, cov, num_points).T


# In[12]:


list_gbm_x1, list_gbm_y1 = getGBM_Correlated(dt = 0.01, alpha=0.1, num = num_points, volatility = 0.1,
                                  S0 = 1, list_std_normal = std_normal1)
#list_gbm_x2, list_gbm_y2 = getGBM_Correlated(dt = 0.01, alpha=0.1, num = num_points, volatility = 0.25,
#                                  S0 = 1, list_std_normal = std_normal2)


# In[13]:


plt.plot(list_gbm_x1, list_gbm_y1)
#plt.plot(list_gbm_x2, list_gbm_y2, color = 'r')
plt.grid()


# In[14]:


PriceSeries1 = list_gbm_y1


# In[15]:


def get_macd_data(data, short_window=20, long_window=50, signal_window=12):
    """
    Get SMA, LMA, MACD, signal_line

    parameters
    -----------------------------
    short_window: short moving average size
    long_window: long moving average size
    signal_window: moving average size for signal line
    Output:
    Data frame with price, SMA, LMA, MACD, signal_line
    SMA: short moving average
    LMA: long moving average
    MACD: SMA - LMA
    signal_line: moving average of MACD
    """
    macd_data = data.copy()
    macd_data['SMA'] = macd_data['price'].rolling(window = short_window, min_periods=2,center=False).mean()
    macd_data['LMA'] = macd_data['price'].rolling(window = long_window, min_periods=2,center=False).mean()
    macd_data["MACD"] = macd_data['SMA'] - macd_data['LMA']
    macd_data['signal_line'] = macd_data['MACD'].rolling(window = signal_window, min_periods=2, center=False).mean()
    return macd_data


# In[16]:


df_stock = pd.DataFrame()
df_stock["Price"] = PriceSeries1
#df_stock


# In[17]:


df_stock['ema5'] = df_stock['Price'].ewm(span=5, adjust=False).mean()
df_stock['ema10'] = df_stock['Price'].ewm(span=10, adjust=False).mean()
df_stock['ema15'] = df_stock['Price'].ewm(span=15, adjust=False).mean()

df_stock['ema25'] = df_stock['Price'].ewm(span=25, adjust=False).mean()
df_stock['ema100'] = df_stock['Price'].ewm(span=100, adjust=False).mean()

df_stock['ema150'] = df_stock['Price'].ewm(span=150, adjust=False).mean()
df_stock['ema250'] = df_stock['Price'].ewm(span=250, adjust=False).mean()

df_stock['diff5_10'] = df_stock['ema5'] - df_stock['ema10']
df_stock['signal5_10'] = df_stock['diff5_10'].ewm(span=9, adjust=False).mean()

df_stock['diff5_15'] = df_stock['ema5'] - df_stock['ema15']
df_stock['signal5_15'] = df_stock['diff5_15'].ewm(span=9, adjust=False).mean()


df_stock['diff5_25'] = df_stock['ema5'] - df_stock['ema25']
df_stock['signal5_25'] = df_stock['diff5_25'].ewm(span=9, adjust=False).mean()

df_stock['diff25_100'] = df_stock['ema25'] - df_stock['ema100']
df_stock['signal25_100'] = df_stock['diff25_100'].ewm(span=9, adjust=False).mean()

df_stock['diff250_150'] = df_stock['ema150'] - df_stock['ema250']
df_stock['signal250_150'] = df_stock['diff250_150'].ewm(span=9, adjust=False).mean()

df_stock['sma'] = df_stock["Price"].rolling(window=10).mean()

df_stock['sma_shifted'] = df_stock['sma'].shift(-10)
df_stock['signal'] = df_stock['sma_shifted'] - df_stock["Price"]
df_stock['signal_sign'] = np.sign(df_stock['signal'])


# In[18]:


df_stock.head(10)


# In[19]:


plt.plot(list_gbm_x1, df_stock["Price"], list_gbm_x1, df_stock["ema250"], list_gbm_x1, df_stock["Price"]-df_stock["ema250"])
#plt.plot(df_stock["ema"], color = 'r')
plt.grid()


# In[20]:


df_stock.dropna(how='any', inplace = True)
df_stock


# In[21]:


from sklearn import svm
y = np.array(df_stock["signal_sign"])


# In[22]:


df_stock['sma'] = df_stock["Price"].rolling(window=10).mean()

df_stock['sma_shifted'] = df_stock['sma'].shift(-10)
df_stock['signal'] = df_stock['sma_shifted'] - df_stock["Price"]
df_stock['signal_sign'] = np.sign(df_stock['signal'])


# In[23]:


X = df_stock.drop(['signal_sign', 'sma_shifted', 'signal', 'sma'], axis=1).values


# In[24]:


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# In[25]:


clf1 = svm.SVC(kernel='linear') # Linear Kernel

clf = svm.SVC(gamma='auto') # Gaussian Kernel
clf.fit(X_train, y_train)
y_pred_train = clf.predict(X_train)
y_pred_test = clf.predict(X_test)


# In[26]:


print("Accuracy(Train):",metrics.accuracy_score(y_train, y_pred_train))
print("Accuracy(Test):",metrics.accuracy_score(y_test, y_pred_test))


# In[ ]:




