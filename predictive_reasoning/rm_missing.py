#! /usr/bin/python
import re

def rm_missing_base(pattern, in_file, out_file):
    f = open(in_file,'r')
    lines = f.readlines()
    f.close()
    results = []
    for line in lines:
        if pattern not in line:
            results.append(line)
    f = open(out_file,'w')
    f.writelines(results)
    f.close()

def rm_missing_consistent(pattern, in_file, out_file):
    f = open(in_file,'r')
    lines = f.readlines()
    f.close()
    results = []
    for line in lines:
        tmp = line.strip().split(': ')
        s = tmp[0] + ': '
        tmp2 = tmp[1].split(';')
        for item in tmp2[:-1]:
            if pattern not in item:
                s = s + item + ';'
        results.append(s+'\n')
    f = open(out_file,'w')
    f.writelines(results)
    f.close()


if __name__ == '__main__':
    rm_missing_base('0,0,0,0,0,0,0','samples/train_air_002.txt','samples/train_no_missing.txt')
    rm_missing_base('0,0,0,0,0,0,0','samples/test_air_002.txt','samples/test_no_missing.txt')
#    rm_missing_consistent('0,0,0,0,0,0,0','samples/consistent_train_001.txt','samples/consistent_train_no_missing.txt')

