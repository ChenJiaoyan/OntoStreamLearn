#! /usr/bin/python

import numpy as np
import sys
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

def readSnapshots(file_name):
    f = open(file_name,'r')
    lines = f.readlines()
    f.close()
    snapshots = []
    for line in lines:
        tmp = line.strip().split(',')
        snapshots.append(tmp[0])
    return snapshots 

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

def merge_nomissing(in_d,snapshots):
    n_feas = len(features)
    n_snaps = len(in_d[0])
    out_d = []
    out_snapshots = []
    for i in range(n_snaps):
        if not is_missing(in_d,i):
            out_snapshots.append(snapshots[i])
            v = map(float,in_d[0][i])
            for j in range(1,n_feas):
                v = v + map(float,in_d[j][i])[1:]
            out_d.append(v)
    return np.array(out_d),out_snapshots


def getTestTargets():
    te = []
    for f in features:
        te.append(readFile('samples/test_' + f + '_' + exp_id + '.txt'))
    snapshots = readSnapshots('samples/test_' + features[0] + '_' + exp_id + '.txt')
    return merge_nomissing(te,snapshots)

def merge_nomissing_mapping(in_d,snapshots):
    n_feas = len(features)
    n_snaps = len(in_d[0])
    out = {}
    for i in range(n_snaps):
        if not is_missing(in_d,i):
            v = map(float,in_d[0][i])
            for j in range(1,n_feas):
                v = v + map(float,in_d[j][i])[1:]
            out[snapshots[i]] = v
    return out

def getTrainSamples():
    te = []
    for f in features:
        te.append(readFile('samples/train_' + f + '_' + exp_id + '.txt'))
    snapshots = readSnapshots('samples/train_' + features[0] + '_' + exp_id + '.txt')
    return merge_nomissing_mapping(te,snapshots)


def readConsistentSamples():
    f = open('samples/consistent_train_' + exp_id + '.txt','r')
    lines = f.readlines()
    f.close()
    snap_v = getTrainSamples()
    consistent_samples = {}
    for line in lines:
        tmp = line.strip().split(': ')
        snapshot = tmp[0]
        consistent_snapshots = tmp[1].strip().split(';')
        tr = []
        for s in consistent_snapshots:
            if snap_v.has_key(s):
                tr.append(snap_v[s])
        consistent_samples[snapshot] = np.array(tr)
    return consistent_samples

if __name__ == '__main__':
    te_d,snapshots = getTestTargets()
    Y_test = te_d[:,0]
    min_max_scaler = preprocessing.MinMaxScaler()
    X_test = min_max_scaler.fit_transform(te_d[:,1:])
    consistent_samples = readConsistentSamples()
    Y_test_predict = np.array([])
    for i,snapshot in enumerate(snapshots):
        print snapshot
        tr_d = consistent_samples[snapshot]
        Y_train = tr_d[:,0]
        X_train = min_max_scaler.fit_transform(tr_d[:,1:])
        clf = linear_model.LogisticRegression()
        clf.fit(X_train, Y_train)
        p = clf.predict(X_test[i,:])
        Y_test_predict = np.concatenate((Y_test_predict,p))
    print 'test samples #: ' + str(len(snapshots))

    acc = accuracy_score(Y_test,Y_test_predict)
    print acc

    
