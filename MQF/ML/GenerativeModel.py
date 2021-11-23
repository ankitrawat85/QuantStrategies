import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import seaborn as sns; sns.set()
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import datasets, naive_bayes
import matplotlib.pyplot as plt

class GaussianNB():

    def fit(self,x,y):
        n_samples,n_features = x.shape
        self._classes = np.unique(y)
        n_classes = len(self._classes)

        #init mean, median and prior
        self._mean  = np.zeros((n_classes,n_features),dtype = np.float64)
        self._var = np.zeros((n_classes,n_features),dtype=np.float64)
        self._priors  =  np.zeros(n_classes,dtype = np.float64)

        for c in self._classes:
            x_c = x[c==y]
            self._mean[c,:] =  x_c.mean(axis =0)
            self._var[c,:] = x_c.var(axis =0)
            self._priors[c] =  x_c.shape[0] / float(n_samples)

    def predict(self,X):
        y_pred = [self._predit(x) for x in X]
        return y_pred

    def _predit(self,x):
        posteriors = []
        for idx , c in enumerate(self._classes):
            prior = np.log(self._priors[idx])
            class_conditional = np.sum(np.log(self._pdf(idx,x)))
            posterior = prior + class_conditional
            posteriors.append(posterior)
        return self._classes[np.argmax(posteriors)]

    def _pdf(self,class_idx,x):
        mean = self._mean[class_idx]
        var = self._var[class_idx]
        numerator = np.exp(-(x-mean)**2 / (2*var))
        denominator  = np.sqrt(2*np.pi * var)
        return numerator / denominator



def accuracy(y_true,y_pred):
    accuracy = np.sum(y_true == y_pred) / len(y_true)
    return accuracy

## NAIVE BAYES
X,Y = datasets.make_classification(n_samples =1000,n_features=10,n_classes =2,random_state=123)
X_train,X_test,Y_train,Y_test = train_test_split(X,Y,test_size=0.2,random_state=123)
nb = GaussianNB()
nb.fit(X_train,Y_train)
predictions = nb.predict(X_test)
print (accuracy(Y_test,predictions))

## sklearn
GN = naive_bayes.GaussianNB()
GN.fit(X_train,Y_train)
GN.predict(X_test)

print (accuracy(Y_test,GN.predict(X_test)))

print ("Y_test")
print (X_test)


from sklearn.datasets import fetch_20newsgroups
data = fetch_20newsgroups()
data.target_names
categories = ['talk.religion.misc', 'soc.religion.christian', 'sci.space', 'comp.graphics']
train = fetch_20newsgroups(subset='train', categories=categories)
test = fetch_20newsgroups(subset='test', categories=categories)

## covert it into vector


model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(train.data, train.target)
labels = model.predict(test.data)
from sklearn.metrics import confusion_matrix
mat = confusion_matrix(test.target, labels)
sns.heatmap(mat.T, square=True, annot=True, fmt='d', cbar=False,
            xticklabels=train.target_names, yticklabels=train.target_names)
plt.xlabel('true label')
plt.ylabel('predicted label');
plt.show()

from sklearn.datasets import fetch_20newsgroups
data = fetch_20newsgroups()
data.target_names
categories = ['talk.religion.misc', 'soc.religion.christian','sci.space', 'comp.graphics']
train = fetch_20newsgroups(subset='train', categories=categories)
test = fetch_20newsgroups(subset='test', categories=categories)
print(train.data[5])

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(train.data, train.target)
labels = model.predict(test.data)
from sklearn.metrics import confusion_matrix
mat = confusion_matrix(test.target, labels)
sns.heatmap(mat.T, square=True, annot=True, fmt='d', cbar=False,xticklabels=train.target_names, yticklabels=train.target_names)
plt.xlabel('true label')
plt.ylabel('predicted label');

def predict_category(s, train=train, model=model):
    pred = model.predict([s])
    print ("PREDECTIO")
    print (pred[0])
    return train.target_names[pred[0]]

print(predict_category('sending a payload to the ISS'))

#LDAa
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

count_vectorizer = CountVectorizer (min_df = 0.01, max_df =0.5, stop_words = 'English')
x = count_vectorizer.fit_transform(news_article)
vcoab = count_vectorizer.get_feature_names()
n,m  = x.shape
k = 10
lda = LatentDirichletAllocation(n_components=k,random_state=2020)
xtr = lda.fit_transform(x)

topic_words = lda.components_
for j in range(m):
    topic_words[:,j] /= sum(topic_word[:,j])



