# -*- coding: utf-8 -*-
"""Categorical Feature Encoding Challenge Take 2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PKGbOIwimDCYZu0-9ExyjIorCwqEaPTl

# Imports
"""

import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, OneHotEncoder
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.compose import make_column_transformer
from sklearn.pipeline import make_pipeline

import pandas as pd

from collections import Counter
import time
import string
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, OneHotEncoder
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.compose import make_column_transformer
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_validate

import pandas as pd

import category_encoders as ce

from collections import Counter
import time
import string

"""# Data"""

# Train data
# !wget -O ./train.csv --no-check-certificate "https://docs.google.com/uc?export=download&id=113cuCNN0cPPxvB2003MaZ5cmSL8O4VIK"

# Test data
# !wget -O ./test.csv --no-check-certificate "https://docs.google.com/uc?export=download&id=1aKVGUejm5PNBroaJg2r9up6SGyy58bJb"

train=pd.read_csv('train.csv',delimiter=',') 
train.head()

"""The data essentially looks like this:

|    | Name   | dtypes | Missing | Uniques |
|----|--------|--------|---------|---------|
| 0  | id     | int64  | 0       | 300000  |
| 1  | bin_0  | int64  | 0       | 2       |
| 2  | bin_1  | int64  | 0       | 2       |
| 3  | bin_2  | int64  | 0       | 2       |
| 4  | bin_3  | object | 0       | 2       |
| 5  | bin_4  | object | 0       | 2       |
| 6  | nom_0  | object | 0       | 3       |
| 7  | nom_1  | object | 0       | 6       |
| 8  | nom_2  | object | 0       | 6       |
| 9  | nom_3  | object | 0       | 6       |
| 10 | nom_4  | object | 0       | 4       |
| 11 | nom_5  | object | 0       | 222     |
| 12 | nom_6  | object | 0       | 522     |
| 13 | nom_7  | object | 0       | 1220    |
| 14 | nom_8  | object | 0       | 2215    |
| 15 | nom_9  | object | 0       | 11981   |
| 16 | ord_0  | int64  | 0       | 3       |
| 17 | ord_1  | object | 0       | 5       |
| 18 | ord_2  | object | 0       | 6       |
| 19 | ord_3  | object | 0       | 15      |
| 20 | ord_4  | object | 0       | 26      |
| 21 | ord_5  | object | 0       | 192     |
| 22 | day    | int64  | 0       | 7       |
| 23 | month  | int64  | 0       | 12      |
| 24 | target | int64  | 0       | 2       |

# Binary Features

bin_0, bin_1 and bin_2 have dtypes of int64 so we don't do anything about them. However, we have to encode bin_3 and bin_4 by simply mapping them to 0's and 1's.
"""

bin3_map = {'T': 1, 'F': 0}

bin4_map = {'Y': 1, 'N': 0}

train['bin_3'] = train['bin_3'].map(bin3_map)
train['bin_4'] = train['bin_4'].map(bin4_map)

"""# Ordinal Features (with <100 uniques)

ord_0 has numerical values, so we skip it. ord_1, ord_2, ord_3 and ord_4 have significantly fewer uniques than ord_5, so we simply map them to numerical values. ord_5 is handled separately in the next section.
"""

ord1_map = {'Novice': 1, 'Contributor': 2,
               'Expert': 3, 'Master': 4, 'Grandmaster': 5}

ord2_map = {'Freezing': 1, 'Cold': 2,
               'Warm': 3, 'Hot': 4, 'Boiling Hot': 5, 'Lava Hot': 6}

ord3_map = {'a': 1, 'b': 2,
               'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8,
               'i': 9, 'j': 10, 'k': 11, 'l': 12,'m': 13, 'n': 14, 'o': 15}

ord4_map = {'A': 1, 'B': 2,
               'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
               'I': 9, 'J': 10, 'K': 11, 'L': 12,'M': 13, 'N': 14, 'O': 15,'P': 16, 'Q': 17,
               'R': 18, 'S': 19, 'T': 20, 'U': 21, 'V': 22, 'W': 23,
               'X': 24, 'Y': 25, 'Z': 26}


train['ord_1'] = train['ord_1'].map(ord1_map)
train['ord_2'] = train['ord_2'].map(ord2_map)
train['ord_3'] = train['ord_3'].map(ord3_map)
train['ord_4'] = train['ord_4'].map(ord4_map)

"""# Ordinal Features (with >100 uniques)"""

def getASCII(letter):
    return string.ascii_letters.find(letter) + 1

train['ord_5_left'] = train['ord_5'].apply(lambda x: getASCII(x[0]))
train['ord_5_right'] = train['ord_5'].apply(lambda x: getASCII(x[1]))

train = train.drop(columns="ord_5")
train.head()

"""# Cyclical Features

day and month are cyclical in nature, so we can do the following:
"""

train['dy_sin'] = np.sin((train['day']-1)*(2.*np.pi/7))
train['dy_cos'] = np.cos((train['day']-1)*(2.*np.pi/7))
train['mnth_sin'] = np.sin((train['month']-1)*(2.*np.pi/12))
train['mnth_cos'] = np.cos((train['month']-1)*(2.*np.pi/12))

train = train.drop(columns="day")
train = train.drop(columns="month")
train.head()


"""# Nominal Features (Low Cardinality)"""

column_trans = make_column_transformer((OneHotEncoder(sparse=False),['nom_0','nom_1','nom_2','nom_3','nom_4']),remainder='passthrough')
train_after_low_car_nom = column_trans.fit_transform(train)

pd.DataFrame(train_after_low_car_nom).head()

"""# Nominal Features (High Cardinality)"""

hashing_encoder = ce.HashingEncoder(cols=[30, 31, 32, 33, 34])
train_after_high_car_nom = hashing_encoder.fit_transform(train_after_low_car_nom)

pd.DataFrame(train_after_high_car_nom).head()



"""# Training"""

train = train.drop(columns="nom_5")
train = train.drop(columns="nom_6")
train = train.drop(columns="nom_7")
train = train.drop(columns="nom_8")
train = train.drop(columns="nom_9")
train = train.drop(columns="id")
target=train['target']
train = train.drop(columns="target")
train['target']=target

train.info()

data=column_trans.fit_transform(train)
n = data.shape[0]
m=int(0.8*n)

train=data[:m,:]
test=data[m:-1,:]

X_train=train[:,:-1]
y_train=train[:,-1]

X_test=test[:,:-1]
y_test=test[:,-1]

names = ["Nearest Neighbors", "Linear SVM", "RBF SVM", "Gaussian Process",
          "Decision Tree", "Random Forest", "Neural Net", "AdaBoost",
          "Naive Bayes", "QDA"]


classifiers = [
    KNeighborsClassifier(3),
    SVC(kernel="linear", C=0.025),
    SVC(gamma=2, C=1),
    GaussianProcessClassifier(1.0 * RBF(1.0)),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    MLPClassifier(alpha=1, max_iter=1000),
    AdaBoostClassifier(),
    GaussianNB(),
    QuadraticDiscriminantAnalysis()]


s=[]

# iterate over classifiers
for name, clf in zip(names, classifiers):
    print(name)
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    print(score)
    s.append(score)