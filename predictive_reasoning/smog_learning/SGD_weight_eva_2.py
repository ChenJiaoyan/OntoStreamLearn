#! /usr/bin/python

import numpy as np
import sys
from sklearn import preprocessing
from sklearn import linear_model
from sklearn.metrics import accuracy_score

correlation_type = ['0','1','2','3','01','02','03','12','13','23','012','013','023','123','0123']

exp_id = '010'
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
        te.append(readFile('samples/test_' + f + '_' + exp_id  + '.txt'))
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
    g = open("different_correlation/consistent_weight_" + exp_id + "_" + correlation_type[int(sys.argv[1])] + ".txt",'r')
    lines1 = g.readlines()
    g.close
    snap_v = getTrainSamples()
    consistent_samples = {}
    consistent_weights = {}
    for i,line in enumerate(lines):
        tmp = line.strip().split(': ')
        snapshot = tmp[0]
        consistent_snapshots = tmp[1].strip().split(';')
        tmp1 = lines1[i].strip().split(": ")
        weights = tmp1[1].strip().split(";")
        tr = []
        t_weight = []
        for j,s in enumerate(consistent_snapshots):
            if snap_v.has_key(s):
                tr.append(snap_v[s])
                t_weight.append(float(weights[j]))
        consistent_samples[snapshot] = np.array(tr)
        consistent_weights[snapshot] = np.array(t_weight)
    return consistent_samples,consistent_weights

if __name__ == '__main__':	
    print "dealing with ", sys.argv[1],sys.argv[2],"...."
    threshold = float(sys.argv[2]) / 100
    te_d,snapshots = getTestTargets()
    Y_test = te_d[:,0]
    min_max_scaler = preprocessing.MinMaxScaler()
    X_test = min_max_scaler.fit_transform(te_d[:,1:])
    consistent_samples,consistent_weights = readConsistentSamples()
    Y_test_predict = np.array([])
    for i,snapshot in enumerate(snapshots):
        #print snapshot
        tr_d = consistent_samples[snapshot]
        Y_train = tr_d[:,0]
        X_train = min_max_scaler.fit_transform(tr_d[:,1:])
        weights = consistent_weights[snapshot]
        #weights = np.ones(len(consistent_weights[snapshot])) #different kinds of weight function
        weights[weights < threshold] = 0      
        #weights[weights >= 0.8] = 1
        #weights = np.exp(weights)
        #weights[weights < threshold] = 0
        #weights[weights >= threshold] = np.exp(weights[weights >= threshold])
        clf = linear_model.SGDClassifier(alpha=0.01, n_iter=100,loss='log')
        clf.fit(X_train, Y_train,sample_weight = weights)
        p = clf.predict(X_test[i,:])
        Y_test_predict = np.concatenate((Y_test_predict,p))
    #print 'test samples #: ' + str(len(snapshots))

    fres = open("different_correlation/result3.txt","a+")
    acc = accuracy_score(Y_test,Y_test_predict)
    fres.write("type:"+ correlation_type[int(sys.argv[1])] + "  " + "threshold:" + str(threshold) +'\n')
    fres.write(str(acc)+'\n')
    fres.close()
    print "type:",correlation_type[int(sys.argv[1])],"  ","threshold:",threshold
    print acc
    
    