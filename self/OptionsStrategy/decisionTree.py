import numpy as np
import pandas as pd

# Machine learning
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score

# Plot
import matplotlib.pyplot as plt

df_ = pd.read_csv('hdfc_final.csv')
df_.head()
predictors = df_[['impliedvolatility', 'delta', 'gamma', 'theta', 'vega']]
print(predictors)
target = np.where(df_.LTP.shift(-1) > df_.LTP, 1, -1)
print(target)
# Number of days to train algo
t = 20
# Train dataset
predictors_train = predictors[:t]
target_train = target[:t]
# Test dataset
predictors_test = predictors[t:]
target_test = target[t:]

cls = DecisionTreeClassifier(
    max_depth=6, min_samples_split=2, max_leaf_nodes=8)
cls.fit(predictors_train, target_train)

accuracy_train = accuracy_score(target_train, cls.predict(predictors_train))
accuracy_test = accuracy_score(target_test, cls.predict(predictors_test))

print('\nTrain Accuracy:{: .2f}%'.format(accuracy_train*100))
print('Test Accuracy:{: .2f}%'.format(accuracy_test*100))

df_['Predicted_Signal'] = cls.predict(predictors)

# Calculate the returns
# LTP is the last traded price
df_['Return'] = (df_.LTP.shift(-1) / df_.LTP)-1
df_['Strategy_return'] = df_.Return * df_.Predicted_Signal
df_.Strategy_return.iloc[t:].cumsum().plot(figsize=(10, 5))
plt.xlabel("Days (Test Data)")
plt.ylabel("Strategy Returns (%)")
plt.show()