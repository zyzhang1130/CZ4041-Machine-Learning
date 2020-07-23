# -*- coding: utf-8 -*-
"""Copy of Copy of Categorical Feature Encoding Challenge Take 5.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OtVT1M-5HnrS7wlErphOK8JVRLEeUkLv

# Imports
"""

!pip install category_encoders

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
!wget -O ./train.csv --no-check-certificate "https://docs.google.com/uc?export=download&id=113cuCNN0cPPxvB2003MaZ5cmSL8O4VIK"

# Test data
!wget -O ./test.csv --no-check-certificate "https://docs.google.com/uc?export=download&id=1aKVGUejm5PNBroaJg2r9up6SGyy58bJb"

original_train=pd.read_csv('train.csv',delimiter=',') 
original_train.head()

original_test=pd.read_csv('test.csv',delimiter=',') 
original_test.head()

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
"""

complete_data = original_train.append(original_test, sort=False)
num_train = len(original_train)
complete_data.head()

train = complete_data.drop(columns="target")
train.info()

"""# Binary Features

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
train = train.drop(columns="id")
train.head()

"""# Nominal Features (Low Cardinality)"""

column_trans = make_column_transformer((OneHotEncoder(sparse=False),['nom_0','nom_1','nom_2','nom_3','nom_4']),remainder='passthrough')
train_after_low_car_nom = column_trans.fit_transform(train)

pd.DataFrame(train_after_low_car_nom).head()

"""# Nominal Features (High Cardinality)"""

train_after_low_car_nom = pd.DataFrame(train_after_low_car_nom)
train_after_high_car_nom = pd.get_dummies(train_after_low_car_nom, columns=train_after_low_car_nom.columns, drop_first=True, sparse=True)

"""# Encoding Results"""

train = train_after_high_car_nom
train.info()

X_train = train[:num_train]
y_train = original_train['target'].values

X_test = train[num_train:]

print("X_train: ", X_train.shape[0])
print("y_train: ", y_train.shape[0])
print("X_test: ", X_test.shape[0])

X_train = X_train.sparse.to_coo().tocsr()
X_test = X_test.sparse.to_coo().tocsr()

"""# Make Prediction"""

from sklearn.ensemble import StackingClassifier
base_learners  = [
    # ('1_1',AdaBoostClassifier()),
    # ('1_2',GaussianNB()),
    #('1_1',MLPClassifier(alpha=1, max_iter=1000)),
    ('1_2',LogisticRegression(C=0.123456789, solver="lbfgs", max_iter=5000)),
    ('1_4', KNeighborsClassifier(n_neighbors=7,weights='distance'))
    # ('1_5', DecisionTreeClassifier(max_depth=9)),   
    # ('1_6', RandomForestClassifier(max_depth=12, n_estimators=13, max_features=11)),
    ]
stack_clf = StackingClassifier(estimators=base_learners,
                          final_estimator=LogisticRegression(C=0.123456789, solver="lbfgs", max_iter=5000),  
                          cv=10)
# stack_clf.fit(xtrain, ytrain)
# stack_acc=stack_clf.score(xtest, ytest)
# print('stack_acc',stack_acc)
print('1')
score=cross_validate(stack_clf, X_train, y_train, cv=3, scoring="roc_auc")["test_score"].mean()
print(f"{score:.6f}")

stack_clf.fit(X_train, y_train)

pred=stack_clf.predict_proba(X_test)[:,1]

pd.DataFrame({"id": original_test["id"], "target": pred}).to_csv("stacking_submission.csv", index=False)

from sklearn.ensemble import VotingClassifier
base_learners  = [
    # ('1_1',AdaBoostClassifier()),
    # ('1_2',GaussianNB()),
    #('1_1',MLPClassifier(alpha=1, max_iter=1000)),
    ('1_2',LogisticRegression(C=0.123456789, solver="lbfgs", max_iter=5000)),
    ('1_4', KNeighborsClassifier(n_neighbors=7,weights='distance'))
    # ('1_5', DecisionTreeClassifier(max_depth=9)),   
    # ('1_6', RandomForestClassifier(max_depth=12, n_estimators=13, max_features=11)),
    ]
v_clf = VotingClassifier(estimators=base_learners,voting='soft')

score=cross_validate(v_clf, X_train, y_train, cv=3, scoring="roc_auc")["test_score"].mean()
print(f"{score:.6f}")

v_clf.fit(X_train, y_train)

pred=v_clf.predict_proba(X_test)[:,1]

pd.DataFrame({"id": original_test["id"], "target": pred}).to_csv("voting_submission.csv", index=False)

"""## Logistic Regression"""

clf=LogisticRegression(C=0.123456789, solver="lbfgs", max_iter=5000)  # MODEL

clf.fit(X_train, y_train)

pred=clf.predict_proba(X_test)[:,1]

pd.DataFrame({"id": original_test["id"], "target": pred}).to_csv("logistic_regression_submission.csv", index=False)

score=cross_validate(clf, X_train, y_train, cv=3, scoring="roc_auc")["test_score"].mean()
print(f"{score:.6f}")

"""## Decision Tree"""

from sklearn.tree import DecisionTreeClassifier
clf= DecisionTreeClassifier(max_depth=5)  # MODEL

clf.fit(X_train, y_train)

pred=clf.predict_proba(X_test)[:,1]

pd.DataFrame({"id": original_test["id"], "target": pred}).to_csv("DecisionTree_submission.csv", index=False)

score=cross_validate(clf, X_train, y_train, cv=3, scoring="roc_auc")["test_score"].mean()
print(f"{score:.6f}")

"""## AdaBoost Classifier"""

adaClf = AdaBoostClassifier()

adaClf.fit(X_train, y_train)

pred = adaClf.predict_proba(X_test)[:,1]

pd.DataFrame({"id": original_test["id"], "target": pred}).to_csv("adaboost_submission.csv", index=False)

score=cross_validate(adaClf, X_train, y_train, cv=3, scoring="roc_auc")["test_score"].mean()
print(f"{score:.6f}")

"""## Random Forest Classifier"""

adaClf = RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1)

adaClf.fit(X_train, y_train)

pred = adaClf.predict_proba(X_test)[:,1]

pd.DataFrame({"id": original_test["id"], "target": pred}).to_csv("RandomForest_submission.csv", index=False)

score=cross_validate(adaClf, X_train, y_train, cv=3, scoring="roc_auc")["test_score"].mean()
print(f"{score:.6f}")

"""## MLP classifier"""

clf=  MLPClassifier(alpha=1, max_iter=1000)  # MODEL

clf.fit(X_train, y_train)

pred=clf.predict_proba(X_test)[:,1]

pd.DataFrame({"id": original_test["id"], "target": pred}).to_csv("logistic_regression_submission.csv", index=False)

score=cross_validate(clf, X_train, y_train, cv=3, scoring="roc_auc")["test_score"].mean()
print(f"{score:.6f}")

"""## KNeighborsClassifier"""

clf=  KNeighborsClassifier(n_neighbors=7,weights='distance')  # MODEL

#clf.fit(X_train, y_train)

#pred=clf.predict_proba(X_test)[:,1]

#pd.DataFrame({"id": original_test["id"], "target": pred}).to_csv("KNeighborsClassifier_submission.csv", index=False)

score=cross_validate(clf, X_train, y_train, cv=3, scoring="roc_auc")["test_score"].mean()
print(f"{score:.6f}")

"""## BaggingClassifier"""

from sklearn.ensemble import BaggingClassifier
from sklearn.linear_model import LogisticRegression

clf=  LogisticRegression(C=0.123456789, solver="lbfgs", max_iter=5000)  # MODEL

clf.fit(X, YY)

pred=clf.predict_proba(X_test2)[:,1]

pd.DataFrame({"id": X_test2["id"], "target": pred}).to_csv("logistic_regression_submission.csv", index=False)

score=cross_validate(clf, X_train, y_train, cv=3, scoring="roc_auc")["test_score"].mean()
print(f"{score:.6f}")

"""# Grid Search"""

y_train.shape

# Commented out IPython magic to ensure Python compatibility.
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression


X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2)

tuned_parameters = [{'C': [0.01,0.1,1], 'solver':['liblinear','lbfgs'],
                     'max_iter':[1000,2000]},

                    ]


print()

clf = GridSearchCV(
    LogisticRegression(), tuned_parameters, scoring='accuracy', cv=3
)
clf.fit(X_train, y_train)

print("Best parameters set found on development set:")
print()
print(clf.best_params_)
print()
print("Grid scores on development set:")
print()
means = clf.cv_results_['mean_test_score']
stds = clf.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, clf.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"
#           % (mean, std * 2, params))
print()

print("Detailed classification report:")
print()
print("The model is trained on the full development set.")
print("The scores are computed on the full evaluation set.")
print()
y_true, y_pred = y_test, clf.predict(X_test)
print(classification_report(y_true, y_pred))
print()

# Commented out IPython magic to ensure Python compatibility.
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression


X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2)

tuned_parameters = [{'C': [0.11, 0.12, 0.13], 'solver':['lbfgs'],
                     'max_iter':[750,800,850]},

                    ]


print()

clf = GridSearchCV(
    LogisticRegression(), tuned_parameters, scoring='accuracy', cv=3
)
clf.fit(X_train, y_train)

print("Best parameters set found on development set:")
print()
print(clf.best_params_)
print()
print("Grid scores on development set:")
print()
means = clf.cv_results_['mean_test_score']
stds = clf.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, clf.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"
#           % (mean, std * 2, params))
print()

print("Detailed classification report:")
print()
print("The model is trained on the full development set.")
print("The scores are computed on the full evaluation set.")
print()
y_true, y_pred = y_test, clf.predict(X_test)
print(classification_report(y_true, y_pred))
print()

import pickle
with open('X_train.pickle', 'wb') as f:
    pickle.dump(X_train, f)
with open('y_train.pickle', 'wb') as f:
    pickle.dump(y_train, f)
with open('X_test.pickle', 'wb') as f:
    pickle.dump(X_test, f)

# Commented out IPython magic to ensure Python compatibility.
from sklearn.model_selection import train_test_split
import pickle
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier

X,YY,X_test2 = pickle.load( open( "data.pickle", "rb" ) )
X_train, X_test, y_train, y_test = train_test_split(
    X, YY, test_size=0.2, random_state=0)

tuned_parameters = [{'n_neighbors': [1, 10, 20],
                     'weights': ['uniform', 'distance']}
                    ]

scores = ['precision', 'recall']

print()

clf = GridSearchCV(
    KNeighborsClassifier(), tuned_parameters, scoring='accuracy', cv=3
)
clf.fit(X_train, y_train)

print("Best parameters set found on development set:")
print()
print(clf.best_params_)
print()
print("Grid scores on development set:")
print()
means = clf.cv_results_['mean_test_score']
stds = clf.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, clf.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"
#           % (mean, std * 2, params))
print()

print("Detailed classification report:")
print()
print("The model is trained on the full development set.")
print("The scores are computed on the full evaluation set.")
print()
y_true, y_pred = y_test, clf.predict(X_test)
print(classification_report(y_true, y_pred))
print()

# Commented out IPython magic to ensure Python compatibility.
from sklearn.model_selection import train_test_split
import pickle
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier

X,YY,X_test2 = pickle.load( open( "data.pickle", "rb" ) )
X_train, X_test, y_train, y_test = train_test_split(
    X, YY, test_size=0.2, random_state=0)

tuned_parameters = [{'learning_rate': [1.0, 10.0, 20.0],
                     'n_estimators': [30, 40, 50, 60]}
                    ]

scores = ['precision', 'recall']


print()

clf = GridSearchCV(
    AdaBoostClassifier(), tuned_parameters, scoring='accuracy', cv=3
)
clf.fit(X_train, y_train)

print("Best parameters set found on development set:")
print()
print(clf.best_params_)
print()
print("Grid scores on development set:")
print()
means = clf.cv_results_['mean_test_score']
stds = clf.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, clf.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"
#           % (mean, std * 2, params))
print()

print("Detailed classification report:")
print()
print("The model is trained on the full development set.")
print("The scores are computed on the full evaluation set.")
print()
y_true, y_pred = y_test, clf.predict(X_test)
print(classification_report(y_true, y_pred))
print()

# Commented out IPython magic to ensure Python compatibility.
from sklearn.model_selection import train_test_split
import pickle
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.metrics import accuracy_score

X,YY,X_test2 = pickle.load( open( "data.pickle", "rb" ) )
X_train, X_test, y_train, y_test = train_test_split(
    X, YY, test_size=0.2, random_state=0)

tuned_parameters = [{'learning_rate': [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 2.0, 3.0],
                     'n_estimators': [60,70, 80]}
                    ]

scores = ['precision', 'recall']


print()

clf = GridSearchCV(
    AdaBoostClassifier(), tuned_parameters, scoring='accuracy', cv=3
)
clf.fit(X_train, y_train)

print("Best parameters set found on development set:")
print()
print(clf.best_params_)
print()
print("Grid scores on development set:")
print()
means = clf.cv_results_['mean_test_score']
stds = clf.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, clf.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"
#           % (mean, std * 2, params))
print()

print("Detailed classification report:")
print()
print("The model is trained on the full development set.")
print("The scores are computed on the full evaluation set.")
print()
y_true, y_pred = y_test, clf.predict(X_test)
print(classification_report(y_true, y_pred))
print()

# Commented out IPython magic to ensure Python compatibility.
from sklearn.model_selection import train_test_split
import pickle
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.metrics import accuracy_score
from sklearn.ensemble import BaggingClassifier
from sklearn.linear_model import LogisticRegression

X,YY,X_test2 = pickle.load( open( "data.pickle", "rb" ) )
X_train, X_test, y_train, y_test = train_test_split(
    X, YY, test_size=0.2, random_state=0)

tuned_parameters = [{'learning_rate': [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 2.0, 3.0],
                     'n_estimators': [60,70, 80]}
                    ]

scores = ['precision', 'recall']


print()

clf = GridSearchCV(
    AdaBoostClassifier(), tuned_parameters, scoring='accuracy', cv=3
)
clf.fit(X_train, y_train)

print("Best parameters set found on development set:")
print()
print(clf.best_params_)
print()
print("Grid scores on development set:")
print()
means = clf.cv_results_['mean_test_score']
stds = clf.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, clf.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"
#           % (mean, std * 2, params))
print()

print("Detailed classification report:")
print()
print("The model is trained on the full development set.")
print("The scores are computed on the full evaluation set.")
print()
y_true, y_pred = y_test, clf.predict(X_test)
print(classification_report(y_true, y_pred))
print()

"""## XGBoost Classifier"""

from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV
model = XGBClassifier(learning_rate =0.1,
 n_estimators=1000,
 max_depth=10,
 min_child_weight=3,
 gamma=0,
 subsample=0.8,
 colsample_bytree=0.8,
 objective= 'binary:logistic',
 nthread=4,
 scale_pos_weight=1,
 seed=27)

param_test1 = {
 'max_depth':range(3,10,2),
 'min_child_weight':range(1,6,2)
}
gsearch1 = GridSearchCV(estimator = XGBClassifier( learning_rate =0.1, n_estimators=140, max_depth=5,
 min_child_weight=1, gamma=0, subsample=0.8, colsample_bytree=0.8,
 objective= 'binary:logistic', nthread=4, scale_pos_weight=1, seed=27), 
 param_grid = param_test1, scoring='roc_auc',n_jobs=4,iid=False, cv=5)
gsearch1.fit(X_train,y_train)
print('coss validation results',gsearch1.cv_results_ )
print()
print('best parameters',gsearch1.best_params_)
print()
print('best score',gsearch1.best_score_)