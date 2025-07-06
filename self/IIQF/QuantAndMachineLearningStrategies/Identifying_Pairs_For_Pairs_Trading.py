#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


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


def getGBM(dt = 0.01, num = 100, alpha = 0.0,  volatility = 0.01, S0 = 1):
    list_gbm_y = []
    list_gbm_y.append(S0)
    for i in range(1, num):
        r = np.random.normal(0, 1)
        S = list_gbm_y[i-1]
        dS = alpha*S*dt + volatility*S*r*np.sqrt(dt)
        list_gbm_y.append(S + dS)
    return(np.linspace(0.0, dt*(num-1), num), list_gbm_y)


# In[4]:


#list_gbm_x1, list_gbm_y1 = getGBM(dt = 0.01, num = 5000, alpha = 0.01,  volatility = 0.25, S0 = 2)
#list_gbm_x2, list_gbm_y2 = getGBM(dt = 0.01, num = 5000, alpha = 0.01,  volatility = 0.25, S0 = 2)


no_of_stocks = 500
trading_time_frame = 5000
df_stock_data = pd.DataFrame(columns = list(range(trading_time_frame)))

for _ in range(no_of_stocks):
    stock_volatility = np.random.uniform(0.1, 0.7)
    stock_alpha = np.random.uniform(-0.01, 0.01)
    _, list_gbm_y1 = getGBM(dt = 0.01, num = trading_time_frame, alpha = stock_alpha,  
                            volatility = stock_volatility, S0 = 2)
    df_stock_data.loc[len(df_stock_data.index)] = list_gbm_y1
    #df_stock_data.append(list_gbm_y1)

    


# In[5]:


# Find the return of the stock
list_returns = list(df_stock_data.pct_change(axis = 1).mean(axis = 1))
list_volatility = list(df_stock_data.pct_change(axis = 1).std(axis = 1))
print(list_returns)
print(list_volatility)


# In[6]:


df_stock_properties = pd.DataFrame()
df_stock_properties["returns"] = list_returns
df_stock_properties["volatility"] = list_volatility
df_stock_properties


# In[7]:


scale = StandardScaler().fit(df_stock_properties)

scaled_data = pd.DataFrame(scale.fit_transform(df_stock_properties), columns = df_stock_properties.columns)


# In[8]:


scaled_data


# In[9]:


print(f"Mean of columns ---->\n {df_stock_properties.mean(axis=0)}")
print(f"Std deviation of columns ---->\n {df_stock_properties.std(axis=0)}")


# In[10]:


#scaled_data.mean(axis=0), scaled_data.std(axis=0)
print(f"Mean of columns ---->\n {scaled_data.mean(axis=0)}")
print(f"Std deviation of columns ---->\n {scaled_data.std(axis=0)}")


# In[11]:


# Use K-means clustering
from sklearn.cluster import KMeans
from sklearn import metrics


# In[12]:


X = scaled_data

K = range(1, 15)
distortions = []

for k in K:
    kmeans = KMeans(n_clusters = k)
    kmeans.fit(X)
    distortions.append(kmeans.inertia_)
    


# In[13]:


fig = plt.figure(figsize = (15, 5))
plt.plot(K, distortions, 'bx-')
plt.xlabel("Values of K")
plt.ylabel("Distortions")
plt.title("Elbow Method")
plt.grid(True)


# In[14]:


K = range(2, 15)
silhouette = []

for k in K:
    kmeans = KMeans(n_clusters = k, random_state = 42, n_init = 10, init = "random")
    kmeans.fit(X)
    silhouette.append(silhouette_score(X, kmeans.labels_))
    
# Plot the results
fig = plt.figure(figsize = (15, 5))
plt.plot(K, silhouette, 'bx-')
plt.xlabel("Values of K")
plt.ylabel("Silhouette score")
plt.title("Silhouette Method")
plt.grid()


# In[18]:


c = 6
# Fit the model
k_means = KMeans(random_state = 42, n_clusters = c)
k_means.fit(X)
prediction = k_means.predict(X)


# In[19]:


# Plot the results
centroids = k_means.cluster_centers_
fig = plt.figure(figsize=(8, 5))
ax = fig.add_subplot(111)
scatter = ax.scatter(X.iloc[:,0], X.iloc[:,1], c=k_means.labels_, cmap="rainbow", label=X.index)
ax.set_title("K-means clustering analysis Reults")
ax.set_xlabel("Mean Return")
ax.set_ylabel("Volatility")
plt.colorbar(scatter)
plt.plot(centroids[:, 0], centroids[:, 1], 'sg', markersize=10)
plt.grid("True")


# In[22]:


clustered_series = pd.Series(index=X.index, data=k_means.labels_.flatten())
clustered_series_all = pd.Series(index = X.index, data=k_means.labels_.flatten())
clustered_series = clustered_series[clustered_series != -1]
plt.figure(figsize=(12,8))
plt.barh(range(len(clustered_series.value_counts())), clustered_series.value_counts())
plt.title("Clusters")
plt.xlabel("Stocks per cluster")
plt.ylabel("Cluster Number")


# In[23]:


from sklearn.cluster import AgglomerativeClustering
import scipy.cluster.hierarchy as sch


# In[25]:


plt.figure(figsize=(15, 10))
plt.title("Dendograms")
dend = sch.dendrogram(sch.linkage(X, method = "ward"))


# In[27]:


plt.figure(figsize=(15, 10))
plt.title("Dendrogram")
dend = sch.dendrogram(sch.linkage(X, method="ward"))
plt.axhline(y=13.5, color="purple", linestyle="--")


# In[ ]:




