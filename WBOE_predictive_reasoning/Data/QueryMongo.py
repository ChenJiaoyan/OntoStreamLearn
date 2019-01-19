#! /usr/bin/python
# coding=utf-8

from pymongo import MongoClient
from datetime import datetime
import pytz


def queryMongoMete(city_name, station_name):
    tz = pytz.timezone('Asia/Shanghai')
    t_mete = {}
    client = MongoClient('localhost', 27017)
    client.admin.authenticate("root_read_only", "urbankg666")
    db = client.forecastio
    col = db[city_name]
    for doc in col.find({'position': station_name}):
        for mete in doc['hourly']['data']:
            t_ = datetime.fromtimestamp(mete['time'], tz)
            t_ = datetime.strptime(t_.strftime("%Y-%m-%dT%H:%M:%SZ"), '%Y-%m-%dT%H:%M:%SZ')
            if not t_mete.has_key(t_):
                t_mete[t_] = mete
    client.close()
    return t_mete


def queryMongoAir(station_code):
    t_air = {}
    client = MongoClient('localhost', 27017)
    client.admin.authenticate("root_read_only", "urbankg666")
    db = client.Air
    col = db['Stations']
    for doc in col.find({'station_code': station_code}):
        t_str = doc['time_point']
        t_ = datetime.strptime(t_str, '%Y-%m-%dT%H:%M:%SZ')
        air = {'pm2_5': doc['pm2_5'], 'pm10': doc['pm10'], 'o3': doc['o3'], 'no2': doc['no2'], 'so2': doc['so2'],
               'co': doc['co'], 'primary_pollutant': doc['primary_pollutant']}
        if not t_air.has_key(t_) or t_air[t_]['pm2_5'] + t_air[t_]['pm10'] == 0:
            t_air[t_] = air
    client.close()
    return t_air


def queryMongoAQI(station_code):
    t_aqi = {}
    client = MongoClient('localhost', 27017)
    client.admin.authenticate("root_read_only", "urbankg666")
    db = client.Air
    col = db['Stations']
    for doc in col.find({'station_code': station_code}):
        t_str = doc['time_point']
        t_ = datetime.strptime(t_str, '%Y-%m-%dT%H:%M:%SZ')
        aqi = doc['aqi']
        if not t_aqi.has_key(t_) or t_aqi[t_] == 0:
            t_aqi[t_] = aqi
    client.close()
    return t_aqi
