#! /usr/bin/python
# coding=utf-8

import os

if not os.getcwd().endswith('codes'):
    os.chdir('codes')

import sys
import csv
import random
from datetime import datetime

DIR = '../samples'


def get_KBs_Changes(city, cutting_time):
    KBs = []
    Changes = []
    file_name = os.path.join(DIR, city + '_Labels.csv')
    with open(file_name) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            t = datetime.strptime('%s:00:00Z' % row['KB'], '%Y-%m-%dT%H:%M:%SZ')
            if t < cutting_time:
                KBs.append(row['KB'])
                Changes.append(row['Change1'])
    return KBs, Changes


def intra_head_tail_pos(KBs, Changes, rate, step=2):
    intra_pairs = []
    l = int(len(KBs) * rate)
    print 'l: %d' % l
    for i in range(0, l, step):
        if i % 100 == 0:
            print 'i: %d' % i
        for j in range(i + 1, l, step):
            if Changes[i] != 'NaN' and Changes[j] != 'NaN' and Changes[i] == Changes[j]:
                intra_pairs.append([KBs[i], KBs[j]])
    return intra_pairs


def intra_head_tail_neg(KBs, Changes, rate, step=2):
    intra_pairs = []
    l = int(len(KBs) * rate)
    print 'l: %d' % l
    for i in range(0, l, step):
        if i % 100 == 0:
            print 'i: %d' % i
        for j in range(i + 1, l, step):
            if Changes[i] != 'NaN' and Changes[j] != 'NaN' and Changes[i] != Changes[j]:
                intra_pairs.append([KBs[i], KBs[j]])
    return intra_pairs


def inter_head_tail_pos(h_KBs, h_Changes, t_KBs, t_Changes, rate, step=2):
    inter_pairs = []
    l = int(len(h_KBs) * rate)
    print 'l: %d' % l
    for i in range(0, l, step):
        if i % 100 == 0:
            print 'i: %d' % i
        for j in range(0, l, step):
            if h_Changes[i] != 'NaN' and t_Changes[j] != 'NaN' and h_Changes[i] == t_Changes[j]:
                inter_pairs.append([h_KBs[i], t_KBs[j]])
    return inter_pairs


def inter_head_tail_neg(h_KBs, h_Changes, t_KBs, t_Changes, rate, step=2):
    inter_pairs = []
    l = int(len(h_KBs) * rate)
    print 'l: %d' % l
    for i in range(0, l, step):
        if i % 100 == 0:
            print 'i: %d' % i
        for j in range(0, l, step):
            if h_Changes[i] != 'NaN' and t_Changes[j] != 'NaN' and h_Changes[i] != t_Changes[j]:
                inter_pairs.append([h_KBs[i], t_KBs[j]])
    return inter_pairs


if __name__ == '__main__':

    # if len(sys.argv) != 4:
    #    sys.stderr.write("usage: python Samples.py type train_rate step\n")
    #    sys.exit(1)
    # s_type = sys.argv[1]
    # train_rate = float(sys.argv[2])
    # step = int(sys.argv[3])

    s_type = 'BJ-HZ'
    #s_type = 'BJ'
    #s_type = 'HZ'
    train_rate = 1.0
    cutting_time = datetime.strptime('2014-12-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')

    step = 5

    # type
    # 'BJ': head-tail from BJ
    # 'HZ': head-tail from HZ
    # 'BJ-HZ': head from BJ, tail from HZ
    # train_rate: top percentage of the KBs

    pairs_pos = []
    pairs_neg = []

    if s_type == 'BJ' or s_type == 'HZ':
        KBs, Changes = get_KBs_Changes(city=s_type, cutting_time=cutting_time)

        pairs_pos.append(['head', 'tail'])
        tmp_pos = intra_head_tail_pos(KBs=KBs, Changes=Changes, rate=train_rate, step=step)
        n_pos = len(tmp_pos)
        pairs_pos += random.sample(tmp_pos, n_pos)

        pairs_neg.append(['head', 'tail'])
        tmp_neg = intra_head_tail_neg(KBs=KBs, Changes=Changes, rate=train_rate, step=step)
        pairs_neg += random.sample(tmp_neg, n_pos)

    if s_type == 'BJ-HZ':
        BJ_KBs, BJ_Changes = get_KBs_Changes(city='BJ', cutting_time=cutting_time)
        HZ_KBs, HZ_Changes = get_KBs_Changes(city='HZ', cutting_time=cutting_time)

        pairs_pos.append(['head', 'tail'])
        tmp_pos = inter_head_tail_pos(h_KBs=BJ_KBs, h_Changes=BJ_Changes, t_KBs=HZ_KBs, t_Changes=HZ_Changes,
                                      rate=train_rate, step=step)
        n_pos = len(tmp_pos)
        pairs_pos += random.sample(tmp_pos, n_pos)

        pairs_neg.append(['head', 'tail'])
        tmp_neg = inter_head_tail_neg(h_KBs=BJ_KBs, h_Changes=BJ_Changes, t_KBs=HZ_KBs, t_Changes=HZ_Changes,
                                      rate=train_rate, step=step)
        n_neg = len(tmp_neg)
        pairs_neg += random.sample(tmp_neg, n_pos)

    print 'write ...'
    f = open(os.path.join(DIR, s_type + '_Pairs_Pos.csv'), 'wb')
    writer = csv.writer(f)
    writer.writerows(pairs_pos)
    f.close()
    f = open(os.path.join(DIR, s_type + '_Pairs_Neg.csv'), 'wb')
    writer = csv.writer(f)
    writer.writerows(pairs_neg)
    f.close()
    print 'finished'
