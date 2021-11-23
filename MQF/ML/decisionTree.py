''' Import ML libraries'''
from sklearn import tree
from sklearn.preprocessing import LabelEncoder

lecompany = LabelEncoder()
inputs["company_n"] = lecompany.fit_transform(inputs["company_"])


model = tree.DecisionTreeClassifier()
model.fit(inputs,target)