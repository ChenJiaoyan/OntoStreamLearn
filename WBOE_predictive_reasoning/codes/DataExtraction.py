#! /usr/bin/python
# coding=utf-8

import os
if not os.getcwd().endswith('codes'):
    os.chdir('codes')

import csv
import sys

from datetime import datetime
from datetime import timedelta

sys.path.append("../Data")
import QueryMongo

# 6 hours
DELTA = 6

# directory
DIR = '../Samples2/'

# Window size
WIN = 6

# Stations in Beijing
BJ_Stations = ['1011A', '1008A', '1010A', '1012A', '1005A']
BJ_Station_Names = ['Aotizhongxin', 'Shunyixincheng', 'Changping', 'Gucheng', 'Nongzhanguan']

# Stations in Hangzhou
HZ_Stations = ['1228A', '1226A', '1230A', '1227A', '1223A']
HZ_Station_Names = ['Hangzhounongda', 'Xiasha', 'Hemuxiaoxue', 'Wolongqiao', 'Binjiang']

# starting/ending time
t_start = datetime.strptime('2013-05-22T09:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
t_end = datetime.strptime('2015-02-04T14:00:00Z', '%Y-%m-%dT%H:%M:%SZ')


def feature_aqi_window(station_code, win_size):
    t_aqi = QueryMongo.queryMongoAQI(station_code)
    rows = []
    header = ['KB']
    for w_cur in range(win_size):
        header.append('AQI-%d' % w_cur)
    rows.append(header)
    t_cur = t_start
    while t_cur <= t_end:
        kb = t_cur.strftime('%Y-%m-%dT%H')
        feature = [kb]
        for w_cur in range(win_size):
            t_win = t_cur - timedelta(hours=w_cur)
            item = t_aqi[t_win] if t_aqi.has_key(t_win) else 'NaN'
            feature.append(item)
        rows.append(feature)
        t_cur += timedelta(hours=1)
    return rows


def feature_air_window(station_code, win_size):
    t_air = QueryMongo.queryMongoAir(station_code)
    header = ['KB']
    air_items = ['pm2_5', 'pm10', 'o3', 'no2', 'so2', 'co', 'primary_pollutant_code']
    for w_cur in range(win_size):
        for air_item in air_items:
            header.append('%s-%d' % (air_item, w_cur))
    rows = [header]
    t_cur = t_start
    while t_cur <= t_end:
        kb = t_cur.strftime('%Y-%m-%dT%H')
        feature = [kb]
        for w_cur in range(win_size):
            t_win = t_cur - timedelta(hours=w_cur)

            if not t_air.has_key(t_win):
                feature += ['NaN'] * len(air_item)
            else:
                air = t_air[t_win]
                feature += [air['pm2_5'], air['pm10'], air['o3'], air['no2'], air['so2'], air['co']]
                pm = air['primary_pollutant']
                if pm == None:
                    feature += [0]
                elif 'PM2.5' in pm and 'PM10' in pm:
                    feature += [1]
                elif 'PM2.5' in pm:
                    feature += [2]
                elif 'PM10' in pm:
                    feature += [3]
                elif unicode('臭氧', 'utf-8') in pm:
                    feature += [4]
                elif unicode('二氧化氮', 'utf-8') in pm:
                    feature += [5]
                else:
                    feature += [0]

        rows.append(feature)
        t_cur += timedelta(hours=1)

    return rows


def feature_mete_window(city_name, station_name, win_size):
    t_mete = QueryMongo.queryMongoMete(city_name, station_name)
    header = ['KB']
    mete_items = ['temperature', 'dewPoint', 'visibility', 'humidity', 'cloudCover',
                  'pressure', 'windSpeed', 'windBearing', 'precipType', 'icon', 'summary']
    for w_cur in range(win_size):
        for mete_item in mete_items:
            header.append('%s-%d' % (mete_item, w_cur))
    rows = [header]
    t_cur = t_start
    while t_cur <= t_end:
        kb = t_cur.strftime('%Y-%m-%dT%H')
        feature = [kb]
        for w_cur in range(win_size):
            t_win = t_cur - timedelta(hours=w_cur)

            if not t_mete.has_key(t_win):
                feature += ['NaN'] * len(mete_items)
            elif t_mete.has_key(t_win - timedelta(hours=1)) and t_mete.has_key(t_win + timedelta(hours=1)):
                mete = t_mete[t_win]
                mete_before = t_mete[t_win - timedelta(hours=1)]
                mete_after = t_mete[t_win + timedelta(hours=1)]
                for item in mete_items[0:-3]:
                    if mete.has_key(item):
                        feature.append(mete[item])
                    elif mete_before.has_key(item) and mete_after.has_key(item):
                        feature.append((mete_before[item] + mete_after[item]) / 2)
                    else:
                        feature.append('NaN')
                for item in mete_items[-3:]:
                    feature.append(mete[item] if mete.has_key(item) else 'NaN')
            else:
                mete = t_mete[t_win]
                for item in mete_items:
                    feature.append(mete[item] if mete.has_key(item) else 'NaN')

        rows.append(feature)
        t_cur += timedelta(hours=1)

    return rows


if __name__ == '__main__':

    if len(sys.argv) != 2:
        sys.stderr.write("usage: python DataExtraction.py type \n")
        sys.exit(1)

    fea_type = sys.argv[1]

    if fea_type == 'AQI':
        print '##################  AQI ##################'
        for i, station in enumerate(BJ_Stations):
            print 'city: Beijing, station: %s, station_i: %d' % (station, i)
            f = open(os.path.join(DIR, 'BJ_' + str(i) + '_AQI.csv'), 'wb')
            writer = csv.writer(f)
            rows = feature_aqi_window(station_code=station, win_size=WIN)
            writer.writerows(rows)
            f.close()
        for i, station in enumerate(HZ_Stations):
            print 'city: Hangzhou, station: %s, station_i: %d' % (station, i)
            f = open(os.path.join(DIR, 'HZ_' + str(i) + '_AQI.csv'), 'wb')
            writer = csv.writer(f)
            rows = feature_aqi_window(station_code=station, win_size=WIN)
            writer.writerows(rows)
            f.close()

    if fea_type == 'Air':
        print '##################  Air ##################'
        for i, station in enumerate(BJ_Stations):
            print 'city: Beijing, station: %s, station_i: %d' % (station, i)
            f = open(os.path.join(DIR, 'BJ_' + str(i) + '_Air.csv'), 'wb')
            writer = csv.writer(f)
            rows = feature_air_window(station_code=station, win_size=WIN)
            writer.writerows(rows)
            f.close()
        for i, station in enumerate(HZ_Stations):
            print 'city: Hangzhou, station: %s, station_i: %d' % (station, i)
            f = open(os.path.join(DIR, 'HZ_' + str(i) + '_Air.csv'), 'wb')
            writer = csv.writer(f)
            rows = feature_air_window(station_code=station, win_size=WIN)
            writer.writerows(rows)
            f.close()

    if fea_type == 'Mete':
        print '##################  Mete ##################'
        for i, station_name in enumerate(BJ_Station_Names):
            print 'city: Beijing, station_name: %s, station_i: %d' % (station_name, i)
            f = open(os.path.join(DIR, 'BJ_' + str(i) + '_Mete.csv'), 'wb')
            writer = csv.writer(f)
            rows = feature_mete_window(city_name='Beijing', station_name=station_name, win_size=WIN)
            writer.writerows(rows)
            f.close()
        for i, station_name in enumerate(HZ_Station_Names):
            print 'city: Hangzhou, station_name: %s, station_i: %d' % (station_name, i)
            f = open(os.path.join(DIR, 'HZ_' + str(i) + '_Mete.csv'), 'wb')
            writer = csv.writer(f)
            rows = feature_mete_window(city_name='Hangzhou', station_name=station_name, win_size=WIN)
            writer.writerows(rows)
            f.close()
