#! /usr/bin/python
# coding=utf-8

import numpy as np
from sklearn import linear_model
from sklearn import preprocessing
from sklearn import tree
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import math


def baseline_evaluation(model_name, tr_d, te_d):
    min_max_scaler = preprocessing.MinMaxScaler()
    Y_train = tr_d[:, 0]
    Y_test = te_d[:, 0]
    tr_l = tr_d.shape[0]
    te_l = te_d.shape[0]
    tmp_d = np.concatenate((tr_d[:, 1:], te_d[:, 1:]))
    tmp_d2 = min_max_scaler.fit_transform(tmp_d)
    X_train = tmp_d2[0:tr_l, :]
    X_test = tmp_d2[tr_l:(tr_l + te_l), :]
    if model_name == 'LogisticRegression':
        clf = linear_model.LogisticRegression()
    elif model_name == 'RandomForest':
        clf = RandomForestClassifier(n_estimators=20)
    elif model_name == 'DecisionTree':
        clf = tree.DecisionTreeClassifier()
    elif model_name == 'AdaBoost':
        clf = AdaBoostClassifier(n_estimators=10)
    elif model_name == 'SGD':
        clf = linear_model.SGDClassifier(loss='log')
    else:
        clf = linear_model.LogisticRegression()
    clf.fit(X_train, Y_train)
    Y_test_predict = clf.predict(X_test)

    acc = accuracy_score(Y_test, Y_test_predict)
    print acc


def base_predict(model_name, tr_d, te_d):
    min_max_scaler = preprocessing.MinMaxScaler()
    Y_train = tr_d[:, 0]

    tr_l = tr_d.shape[0]
    te_l = te_d.shape[0]
    tmp_d = np.concatenate((tr_d[:, 1:], te_d[:, 1:]))
    tmp_d2 = min_max_scaler.fit_transform(tmp_d)
    X_train = tmp_d2[0:tr_l, :]
    X_test = tmp_d2[tr_l:(tr_l + te_l), :]

    if model_name == 'LogisticRegression':
        clf = linear_model.LogisticRegression()
    elif model_name == 'RandomForest':
        clf = RandomForestClassifier(n_estimators=20)
    elif model_name == 'DecisionTree':
        clf = tree.DecisionTreeClassifier()
    elif model_name == 'AdaBoost':
        clf = AdaBoostClassifier(n_estimators=10)
    elif model_name == 'SGD':
        clf = linear_model.SGDClassifier(loss='log')
    else:
        clf = linear_model.LogisticRegression()
    clf.fit(X_train, Y_train)
    Y_test_predict = clf.predict(X_test)

    return Y_test_predict


def WBOE_Inter_Consistent(train_S, test_T, train_S_WBOE, test_T_WBOE, model_name, alpha):
    test_num = 0
    true_num = 0
    cols = test_T.shape[1]
    for i, t in enumerate(test_T):

        t_WBOE = test_T_WBOE[i]
        weight_S = WBOE_weights(t_WBOE=t_WBOE, S_WBOE=train_S_WBOE)

        train_S_cons = train_S[np.where(weight_S >= alpha)[0]]
        train = train_S_cons
        if np.min(train[:, 0]) == np.max(train[:, 0]):
            continue

        predict = base_predict(model_name, train, t.reshape((1, cols)))
        test_num += 1

        if predict[0] == t[0]:
            true_num += 1

        if i % 50 == 0:
            print 'test #: %d' % i
            print 'train_S_cons #: %d, predict: %d, truth: %d' % (train_S_cons.shape[0], int(predict[0]), int(t[0]))
            print 'true_num: %d,  Acc: %f' % (true_num, (float(true_num) / float(i + 1)))
            print '---------------------------------------'

    print 'test_num: %d' % test_num
    print 'Acc: %f' % (float(true_num) / float(test_num))


def WBOE_Intra_Consistent(train_T, test_T, train_T_WBOE, test_T_WBOE, model_name, alpha):
    test_num = 0
    true_num = 0
    cols = test_T.shape[1]
    for i, t in enumerate(test_T):

        t_WBOE = test_T_WBOE[i]
        weight_T = WBOE_weights(t_WBOE=t_WBOE, S_WBOE=train_T_WBOE)

        train_T_cons = train_T[np.where(weight_T >= alpha)[0]]
        train = train_T_cons
        if np.min(train[:, 0]) == np.max(train[:, 0]):
            continue

        predict = base_predict(model_name, train, t.reshape((1, cols)))
        test_num += 1

        if predict[0] == t[0]:
            true_num += 1

        if i % 50 == 0:
            print 'test #: %d' % i
            print 'train_T_cons #: %d, predict: %d, truth: %d' % (train_T_cons.shape[0], int(predict[0]), int(t[0]))
            print 'true_num: %d,  Acc: %f' % (true_num, (float(true_num) / float(i + 1)))
            print '---------------------------------------'

    print 'test_num: %d' % test_num
    print 'Acc: %f' % (float(true_num) / float(test_num))


def WBOE_Inter_Intra_Consistent(train_S, train_T, test_T, train_S_WBOE, train_T_WBOE, test_T_WBOE_S, test_T_WBOE_T,
                                model_name, alpha):
    test_num = 0
    true_num = 0
    cols = test_T.shape[1]
    for i, t in enumerate(test_T):

        t_WBOE_s = test_T_WBOE_S[i]
        weight_S = WBOE_weights(t_WBOE=t_WBOE_s, S_WBOE=train_S_WBOE)
        train_S_cons = train_S[np.where(weight_S >= alpha)[0]]

        t_WBOE_t = test_T_WBOE_T[i]
        weight_T = WBOE_weights(t_WBOE=t_WBOE_t, S_WBOE=train_T_WBOE)
        train_T_cons = train_T[np.where(weight_T >= alpha)[0]]

        train = np.concatenate((train_S_cons, train_T_cons))

        if np.min(train[:, 0]) == np.max(train[:, 0]):
            continue

        predict = base_predict(model_name, train, t.reshape((1, cols)))
        test_num += 1

        if predict[0] == t[0]:
            true_num += 1

        if i % 50 == 0:
            print 'test #: %d' % i
            print 'train_S_cons #: %d, train_T_cons #: %d, predict: %d, truth: %d' % (
                train_S_cons.shape[0], train_T_cons.shape[0], int(predict[0]), int(t[0]))
            print 'true_num: %d,  Acc: %f' % (true_num, (float(true_num) / float(i + 1)))
            print '---------------------------------------'

    print 'test_num: %d' % test_num
    print 'Acc: %f' % (float(true_num) / float(test_num))


def WBOE_weights(t_WBOE, S_WBOE):
    l = t_WBOE.shape[0]
    n = S_WBOE.shape[0]
    weights = np.zeros((n, 1))
    for i in range(n):
        tmp = 0
        for j in range(l):
            tmp += t_WBOE[j] * S_WBOE[i, j]
        w = math.sqrt(tmp)
        weights[i] = w
    w_max = np.max(weights)
    w_min = np.min(weights)
    n_weights = (weights - w_min) / (w_max - w_min)
    return n_weights
