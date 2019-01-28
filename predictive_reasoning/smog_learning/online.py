#! /usr/bin/python

import numpy as np
from sklearn import preprocessing
from sklearn import linear_model
from sklearn.metrics import accuracy_score

exp_id = '1603'
AQI = [0,1,2,3,4,5]
AIR = [6,7,8,9,10,11]
METE = [12,13,14,15,16]
F_INDEX = AQI + METE + METE

def loadTargets():
    f = open('samples2/targets.txt','r')
    lines = f.readlines()
    f.close()
    targets = []
    for line in lines:
        targets.append(line.strip())
    return targets

def loadLabels():
    f = open('samples2/labels_'+exp_id+'.txt','r')
    lines = f.readlines()
    f.close()
    labels = {}
    for line in lines:
        tmp = line.strip().split(',')
        labels[tmp[0]] = int(tmp[1])
    return labels

def loadFeatures():
    f = open('samples2/features.txt','r')
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

def genSamples(target,labels,features):
    snaps = labels.keys()
    X,y = [],[]
    for snap in snaps:
        if snap < target and features.has_key(snap):
            f = features[snap]
            if notMissing(f):
                X.append(f)
                y.append(labels[snap])    
    X2,y2=[],[]
    if features.has_key(target) and labels.has_key(target):
        f = features[target]
        if notMissing(f):
            X2.append(f)
            y2.append(labels[target])  
    return np.float64(np.array(X)),np.float64(np.array(y)),np.float64(np.array(X2)),np.float64(np.array(y2))


if __name__ == '__main__':	
    targets = loadTargets()
    labels = loadLabels()
    features = loadFeatures()
    n,m = 0,0
    for target in targets:
        print '-----------' + target + '-----------'
        X,y,X2,y2 = genSamples(target,labels,features)
        if X2.shape[0] == 0:
            continue
        print 'training sample size: ' + str(X.shape[0])
        min_max_scaler = preprocessing.MinMaxScaler() 
        tmp = np.concatenate((X,X2))
        tmp = min_max_scaler.fit_transform(tmp)
        X = tmp[:-1,:]
        X2 = tmp[-1,:]
        clf = linear_model.SGDClassifier(alpha=0.01, n_iter=100,loss='hinge')
        clf.fit(X, y)
        p = clf.predict(X2)
        if p[0]==y2:
            n += 1
        m += 1
        print str(p[0]) + '  ' + str(y2) + '  '+ str(p[0]==y2)
    print 'n: ' + str(n) + '  m: ' + str(m)
    acc = float(n)/float(m) 
    print acc
