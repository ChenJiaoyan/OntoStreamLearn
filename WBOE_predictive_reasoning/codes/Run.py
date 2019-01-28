#! /usr/bin/python
# coding=utf-8

import os
import sys

if not os.getcwd().endswith('codes'):
    os.chdir('codes')

from datetime import datetime
import numpy as np
import csv
import random

import Evaluation
import BagOfEntailments

t_start = datetime.strptime('2013-05-22T09:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
t_end = datetime.strptime('2015-02-04T14:00:00Z', '%Y-%m-%dT%H:%M:%SZ')

DIR = '../samples'


def mete_summary_2_float(summary):
    if 'breezy' in summary.lower():
        return 0
    elif 'clear' in summary.lower():
        return 1
    elif 'dry' in summary.lower():
        return 2
    elif 'foggy' in summary.lower():
        return 3
    elif 'humid' in summary.lower():
        return 4
    elif 'mostly cloudy' in summary.lower():
        return 5
    elif 'overcast' in summary.lower():
        return 6
    elif 'partly cloudy' in summary.lower():
        return 7
    else:
        return 8


def read_attribute(file_name, cols, t1, t2):
    d = []
    with open(os.path.join(DIR, file_name)) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            t = datetime.strptime('%s:00:00Z' % row['KB'], '%Y-%m-%dT%H:%M:%SZ')
            if t1 <= t < t2:
                line = []
                for col in cols:
                    if col.startswith('summary'):
                        line.append(float(mete_summary_2_float(row[col])))
                    else:
                        line.append(float(row[col]))
                d.append(line)
    return np.array(d)


def load_samples(t1, t2, f_types, feas, city, f_hours):
    if f_hours == 6:
        label = 'Label1'
    elif f_hours == 12:
        label = 'Label2'
    else:
        label = 'Label3'
    s = read_attribute('%s_Labels.csv' % city, [label], t1, t2)
    for ft in f_types:
        cols = feas[ft]
        d = read_attribute('%s_%s.csv' % (city, ft), cols, t1, t2)
        s = np.concatenate((s, d), axis=1)
    return s


def load_BOEs(t1, t2, city):
    d = []
    file_name = os.path.join(DIR, '%s_BOE.csv' % city)
    with open(file_name) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            line = []
            t = datetime.strptime('%s:00:00Z' % row['KB'], '%Y-%m-%dT%H:%M:%SZ')
            if t1 <= t < t2:
                for exp in BagOfEntailments.Exps:
                    line.append(float(row[exp]))
                d.append(line)
    return np.array(d)


def stack_sample_window(d):
    size = d.shape[0]
    X = np.zeros((size - n_steps + 1, n_steps, n_input))
    Y = np.zeros((size - n_steps + 1, n_classes))
    dd = np.zeros((size - n_steps + 1, 1 + n_steps * n_input))
    n = 0
    for i in range(size - n_steps + 1):
        y = d[i + n_steps - 1, 0]
        x = d[i:(i + n_steps), 1:]
        if not np.isnan(y) and np.count_nonzero(np.isnan(x)) <= n_steps * n_input * max_missing_rate:
            X[n] = np.nan_to_num(x)
            Y[n, int(y)] = 1
            dd[n, 0] = y
            dd[n, 1:] = X[n].reshape(1, n_steps * n_input)
            n += 1

    return X[0:n], Y[0:n], dd[0:n]


def rm_incomplete_samples(dat, boe):
    l = dat.shape[0]
    n = 0
    X = np.zeros((l, f_num))
    Y = np.zeros((l, n_classes))
    dd = np.zeros((l, f_num + 1))
    bb = np.zeros(boe.shape)
    for i in range(l):
        y = dat[i, 0]
        x = dat[i, 1:]
        b = boe[i]
        if not np.isnan(y) and np.count_nonzero(np.isnan(x)) <= f_num * max_missing_rate and -1 not in b:
            X[n] = np.nan_to_num(x)
            Y[n, int(y)] = 1
            dd[n, 1:] = np.nan_to_num(x)
            dd[n, 0] = y
            bb[n] = b
            n += 1

    return X[0:n], Y[0:n], dd[0:n], bb[0:n]


if __name__ == '__main__':
    feature_types = ['0_AQI', '0_Air', '0_Mete']
    features = {'0_AQI': ['AQI-0',
                          'AQI-1',
                          'AQI-2',
                          'AQI-3',
                          'AQI-4',
                          'AQI-5'],
                '0_Air': ['pm2_5-0', 'pm10-0', 'o3-0', 'no2-0', 'so2-0', 'co-0', 'primary_pollutant_code-0',
                          'pm2_5-1', 'pm10-1', 'o3-1', 'no2-1', 'so2-1', 'co-1', 'primary_pollutant_code-1',
                          'pm2_5-2', 'pm10-2', 'o3-2', 'no2-2', 'so2-2', 'co-2', 'primary_pollutant_code-2',
                          'pm2_5-3', 'pm10-3', 'o3-3', 'no2-3', 'so2-3', 'co-3', 'primary_pollutant_code-3',
                          'pm2_5-4', 'pm10-4', 'o3-4', 'no2-4', 'so2-4', 'co-4', 'primary_pollutant_code-4',
                          'pm2_5-5', 'pm10-5', 'o3-5', 'no2-5', 'so2-5', 'co-5', 'primary_pollutant_code-5',
                          ],
                '0_Mete': ['temperature-0', 'dewPoint-0', 'visibility-0', 'humidity-0', 'cloudCover-0', 'pressure-0',
                           'windSpeed-0', 'windBearing-0', 'summary-0',
                           'temperature-1', 'dewPoint-1', 'visibility-1', 'humidity-1', 'cloudCover-1', 'pressure-1',
                           'windSpeed-1', 'windBearing-1', 'summary-1',
                           'temperature-2', 'dewPoint-2', 'visibility-2', 'humidity-2', 'cloudCover-2', 'pressure-2',
                           'windSpeed-2', 'windBearing-2', 'summary-2',
                           'temperature-3', 'dewPoint-3', 'visibility-3', 'humidity-3', 'cloudCover-3', 'pressure-3',
                           'windSpeed-3', 'windBearing-3', 'summary-3',
                           'temperature-4', 'dewPoint-4', 'visibility-4', 'humidity-4', 'cloudCover-4', 'pressure-4',
                           'windSpeed-4', 'windBearing-4', 'summary-4',
                           'temperature-5', 'dewPoint-5', 'visibility-5', 'humidity-5', 'cloudCover-5', 'pressure-5',
                           'windSpeed-5', 'windBearing-5', 'summary-5',
                           ]
                }

    n_classes = 6
    n_steps = 6
    max_missing_rate = 0.2
    n_input = 17
    f_num = n_input * n_steps

    cutting_time = datetime.strptime('2014-12-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
    forecasting_hours = 6

    print 'load samples and BOEs ...'
    train_BJ0 = load_samples(t_start, cutting_time, feature_types, features, 'BJ', forecasting_hours)
    train_BJ0_BOE = load_BOEs(t_start, cutting_time, 'BJ')
    train_HZ0 = load_samples(t_start, cutting_time, feature_types, features, 'HZ', forecasting_hours)
    train_HZ0_BOE = load_BOEs(t_start, cutting_time, 'HZ')
    test_HZ0 = load_samples(cutting_time, t_end, feature_types, features, 'HZ', forecasting_hours)
    test_HZ0_BOE = load_BOEs(cutting_time, t_end, 'HZ')
    print 'train_BJ0: (%d, %d), train_HZ0: (%d, %d), test_HZ0: (%d, %d)' % (
        train_BJ0.shape + train_HZ0.shape + test_HZ0.shape)

    print 'stacking and remove missing...'
    train_HZ_X, train_HZ_Y, tr_HZ, tr_HZ_BOE = rm_incomplete_samples(train_HZ0, train_HZ0_BOE)
    train_BJ_X, train_BJ_Y, tr_BJ, tr_BJ_BOE = rm_incomplete_samples(train_BJ0, train_BJ0_BOE)
    test_HZ_X, test_HZ_Y, te_HZ, te_HZ_BOE = rm_incomplete_samples(test_HZ0, test_HZ0_BOE)

    print 'tr_HZ: (%d, %d), train_BJ: (%d, %d), te_HZ: (%d, %d)' % (
        tr_HZ.shape + tr_BJ.shape + te_HZ.shape)

    train_HZ_size = train_HZ_X.shape[0]
    train_BJ_size = train_BJ_X.shape[0]

    print 'shuffling ...'
    index = range(train_HZ_size)
    random.shuffle(index)
    train_HZ_X, train_HZ_Y, tr_HZ, tr_HZ_BOE = train_HZ_X[index], train_HZ_Y[index], tr_HZ[index], tr_HZ_BOE[index]
    index = range(train_BJ_size)
    random.shuffle(index)
    train_BJ_X, train_BJ_Y, tr_BJ, tr_BJ_BOE = train_BJ_X[index], train_BJ_Y[index], tr_BJ[index], tr_BJ_BOE[index]

    # print 'evaluate with basic methods ...'
    # train = np.concatenate((tr_BJ, tr_HZ))
    # train = tr_BJ
    # train = tr_HZ
    # Evaluation.baseline_evaluation('DecisionTree', train, te_HZ)

    # print 'evaluate with OWL spatial transfer methods ...'
    # Evaluation.WBOE_Transfer(train_S=tr_BJ, test_T=te_HZ, train_S_WBOE=tr_BJ_WBOE, test_T_WBOE=te_HZ_WBOE,
    #                         model_name='LogisticRegression', alpha=0.9)
    # print 'evaluate with OWL temporal drift methods ...'
    # Evaluation.WBOE_Drift(train_T=tr_HZ, test_T=te_HZ, train_T_WBOE=tr_HZ_WBOE, test_T_WBOE=te_HZ_WBOE,
    #                         model_name='LogisticRegression', alpha=0.01)
    # print 'evaluate with OWL drift and transfer methods ...'
    # Evaluation.WBOE_Transfer_Drift(train_S=tr_BJ, train_T=tr_HZ, test_T=te_HZ, train_S_WBOE=tr_BJ_WBOE,
    #                              train_T_WBOE=tr_HZ_WBOE, test_T_WBOE=te_HZ_WBOE, model_name='LogisticRegression',
    #                              alpha=0.8)

    basic_classifiers = ['LogisticRegression', 'SGD', 'AdaBoost', 'DecisionTree', 'RandomForest']
    alphas = [0.95, 0.9, 0.85, 0.8]
    for c in basic_classifiers:
        print '#### %s Spatial Transfer ####' % c
        train = tr_BJ
        Evaluation.baseline_evaluation(c, train, te_HZ)
        W = np.loadtxt(os.path.join(DIR, 'BJ-HZ_Exps_Weights.txt'))
        tr_BJ_WBOE = tr_BJ_BOE * W
        te_HZ_WBOE = te_HZ_BOE * W
        for a in alphas:
            print '-- alpha = %f --' % a
            Evaluation.WBOE_Inter_Consistent(train_S=tr_BJ, test_T=te_HZ, train_S_WBOE=tr_BJ_WBOE,
                                             test_T_WBOE=te_HZ_WBOE, model_name=c, alpha=a)

        print '#### %s Temporal Drift ####' % c
        train = tr_HZ
        Evaluation.baseline_evaluation(c, train, te_HZ)
        W = np.loadtxt(os.path.join(DIR, 'HZ_Exps_Weights.txt'))
        tr_HZ_WBOE = tr_HZ_BOE * W
        te_HZ_WBOE = te_HZ_BOE * W
        for a in alphas:
            print '-- alpha = %f --' % a
            Evaluation.WBOE_Intra_Consistent(train_T=tr_HZ, test_T=te_HZ, train_T_WBOE=tr_HZ_WBOE, test_T_WBOE=te_HZ_WBOE,
                                  model_name=c, alpha=a)

        print '#### %s Spatial Transfer & Temporal Drift ####' % c
        train = np.concatenate((tr_BJ, tr_HZ))
        Evaluation.baseline_evaluation(c, train, te_HZ)
        W_HZ = np.loadtxt(os.path.join(DIR, 'HZ_Exps_Weights.txt'))
        W_BJ_HZ = np.loadtxt(os.path.join(DIR, 'BJ-HZ_Exps_Weights.txt'))
        tr_HZ_WBOE = tr_HZ_BOE * W_HZ
        te_HZ_WBOE_HZ = te_HZ_BOE * W_HZ
        tr_BJ_WBOE = tr_BJ_BOE * W_BJ_HZ
        te_HZ_WBOE_BJ_HZ = te_HZ_BOE * W_BJ_HZ
        for a in alphas:
            print '-- alpha = %f --' % a
            Evaluation.WBOE_Inter_Intra_Consistent(train_S=tr_BJ, train_T=tr_HZ, test_T=te_HZ, train_S_WBOE=tr_BJ_WBOE,
                                           train_T_WBOE=tr_HZ_WBOE, test_T_WBOE_S=te_HZ_WBOE_BJ_HZ,
                                           test_T_WBOE_T=te_HZ_WBOE_HZ, model_name=c, alpha=a)
