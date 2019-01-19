#! /usr/bin/python

import numpy as np
from sklearn import preprocessing
from sklearn import linear_model
from sklearn.metrics import accuracy_score
import sys

exp_id = '1600'
C_INDEX = 6
THETA = 0.8
G = 'g2'
LOSS = 'log'

AQI = [0,1,2,3,4,5]
AIR = [6,7,8,9,10,11]
METE = [12,13,14,15,16]
F_INDEX = AQI + AIR + METE

def loadTargets():
    f = open('samples/targets.txt','r')
    lines = f.readlines()
    f.close()
    targets = []
    for line in lines:
        targets.append(line.strip())
    return targets

def loadLabels():
    f = open('samples/labels.txt','r')
    lines = f.readlines()
    f.close()
    labels = {}
    for line in lines:
        tmp = line.strip().split(',')
        labels[tmp[0]] = int(tmp[1])
    return labels

def loadFeatures():
    f = open('samples/features_' + exp_id + '.txt','r')
    lines = f.readlines()
    f.close()
    features = {}
    for line in lines:
        tmp = line.strip().split(',')
        features[tmp[0]] = np.array(tmp[1:])[F_INDEX]
    return features

def notMissing(f):
    i1 = np.where(f=='-1')
    i2 = np.where(f=='0')
    i3 = np.where(f=='0.0')
    if float(i1[0].shape[0]+i2[0].shape[0]+i3[0].shape[0])/float(len(F_INDEX)) < 0.25:
        return True 
    else:
        return False 

def loadWeights(target):
    weights = {}
    f = open('samples/consistent.txt','r')
    line = f.readline()
    while(line.startswith(target)==False):
        line = f.readline()
    line = line.strip()
    line = line[0:len(line)-1]
    tmp = line.split(': ')[1].split(';')
    for item in tmp:
        tmp2 = item.split(':')
        weights[tmp2[0]] = float(tmp2[1].split(',')[C_INDEX])
    f.close()
    return weights

def genSamples(target,labels,features):
    weights = loadWeights(target)
    snaps = labels.keys()
    X,y,w = [],[],[]
    for snap in snaps:
        if snap < target:
            f = features[snap]
            if notMissing(f):
                X.append(f)
                y.append(labels[snap])    
                w.append(weights[snap])
    X2,y2=[],[]
    f = features[target]
    if notMissing(f):
        X2.append(f)
        y2.append(labels[target])  
    return np.float64(np.array(X)),np.float64(np.array(y)),np.float64(np.array(X2)),np.float64(np.array(y2)),np.float64(np.array(w))


if __name__ == '__main__':	
    targets = loadTargets()
    labels = loadLabels()
    features = loadFeatures()
    n,m = 0,0
    for target in targets:
        print '-----------' + target + '-----------'
        X,y,X2,y2,w = genSamples(target,labels,features)
        if X2.shape[0] == 0:
            continue
        print X.shape
        min_max_scaler = preprocessing.MinMaxScaler() 
        tmp = np.concatenate((X,X2))
        tmp = min_max_scaler.fit_transform(tmp)
        X = tmp[:-1,:]
        X2 = tmp[-1,:]
        clf = linear_model.SGDClassifier(alpha=0.01, n_iter=100,loss=LOSS)
        
        if G == 'g1':
            w[np.where(w>=THETA)] = 1
            w[np.where(w<THETA)] = 0
        elif G == 'g2':
            w[np.where(w<THETA)] = 0
        else:
            w[np.where(w>=THETA)] = np.exp(w[np.where(w>=THETA)])
            w[np.where(w<THETA)] = 0

        print 'training sample size: ' + str(np.where(w>0)[0].shape[0])

        clf.fit(X, y, sample_weight = w)
        p = clf.predict(X2)
        if p[0]==y2:
            n += 1
        m += 1
        print str(p[0]) + '  ' + str(y2) + '  '+ str(p[0]==y2)
    print 'n:' + str(n) + '  m:'+str(m)
    acc = float(n)/float(m) 
    print acc
