import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.decomposition import PCA
import pandas as pd
from sklearn.preprocessing import StandardScaler
plt.style.use('ggplot')
# Load the data
iris = datasets.load_iris()
X = iris.data
y = iris.target
# Z-score the features
scaler = StandardScaler()
scaler.fit(X)
X = scaler.transform(X)
# The PCA model
pca = PCA(n_components=1) # estimate only 2 PCs
X_new = pca.fit_transform(X) # project the original data into the PCA space

print(pca.explained_variance_ratio_)
# array([0.72962445, 0.22850762])

print(abs( pca.components_ ))