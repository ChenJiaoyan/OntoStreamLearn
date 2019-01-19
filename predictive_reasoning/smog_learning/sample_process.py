#! /usr/bin/python
exp_id = '1600'

def extractTargets(file_name,file_out):
    f = open(file_name,'r')
    lines = f.readlines()
    f.close()
    targets = []
    for line in lines:
        tmp = line.strip().split(',')
        targets.append(tmp[0] + '\n')
    f = open(file_out,'w')
    f.writelines(targets)
    f.close()

if __name__ == '__main__':
    extractTargets('samples/test_air_'+exp_id+'.txt','samples/targets_'+exp_id+'.txt')

