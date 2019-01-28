#! /usr/bin/python
import numpy as np
from sklearn import preprocessing
from sklearn import linear_model
from sklearn.metrics import accuracy_score

exp_id = '003'
features = ['air','mete']

def readFile(file_name):
    f = open(file_name,'r')
    lines = f.readlines()
    f.close()
    d = []
    for line in lines:
        tmp = line.strip().split(',')
        d.append(tmp[2:])
    return d

def is_missing(d,i):
    n_feas = len(features)
    miss_tag = False
    for j in range(n_feas):
        if features[j] == 'air':
            if d[j][i][1:].count('0') >= 4:
                miss_tag = True
        if features[j] == 'mete':
            if d[j][i][1:].count('-1') >= 4:
                miss_tag = True
    return miss_tag

def merge_nomissing(in_d):
    n_feas = len(features)
    n_snaps = len(in_d[0])
    out_d = []
    for i in range(n_snaps):
        if not is_missing(in_d,i):
            v = map(float,in_d[0][i])
            for j in range(1,n_feas):
                v = v + map(float,in_d[j][i])[1:]
            out_d.append(v)
    return np.array(out_d)

def getSamples():
    tr = []
    te = []
    for f in features:
        tr.append(readFile('samples/train_' + f + '_' + exp_id + '.txt'))
        te.append(readFile('samples/test_' + f + '_' + exp_id + '.txt'))
    return merge_nomissing(tr),merge_nomissing(te)

if __name__ == '__main__':
    print 'generate samples ...'
    tr_d,te_d = getSamples()
    print 'train samples: ' + str(tr_d.shape)
    print 'test samples: ' + str(te_d.shape)
    Y_train = tr_d[:,0]
    Y_test = te_d[:,0]
    print 'preprocess ...'
    min_max_scaler = preprocessing.MinMaxScaler()
    print 'train and test ...'
    X_train = min_max_scaler.fit_transform(tr_d[:,1:])
    X_test = min_max_scaler.fit_transform(te_d[:,1:])
    clf = linear_model.LogisticRegression()
    clf.fit(X_train, Y_train)
    Y_test_predict = clf.predict(X_test)
    acc = accuracy_score(Y_test,Y_test_predict)
    print acc
    
