#! /usr/bin/python

import pymongo
import datetime
import sys
import os
import demjson

URL_BASE = 'https://api.darksky.net/forecast/2a2c39759294b5816dd83e16e7905446'    #chen00217@gmail.com
#URL_BASE = 'https://api.darksky.net/forecast/5b6c49f3bff8993dd11829fd6bc456cd'    #jiaoyanchen.zju@gmail.com
#URL_BASE = 'https://api.darksky.net/forecast/79c34ee1dde5a9c972d08418d346e369'    #jiaoyan4ai@gmail.com
#URL_BASE = 'https://api.darksky.net/forecast/88e6aafdfabf501f6eca471a24bd28ae'    #jiaoyanchen@zju.edu.cn
#URL_BASE = 'https://api.darksky.net/forecast/6e62fa14bcb43dca3276296e47a6bcd1'    #j.chen@uni-heidelberg.de
#URL_BASE = 'https://api.darksky.net/forecast/78c86982feb0d2ba6a55b43a933ecb90'    #tt149@uni-heidelberg.de
TMP_FILE = '/tmp/mydata.json'


def callAPI(my_url):
    os.system('wget ' + my_url + ' -O ' + TMP_FILE)
    f = open(TMP_FILE, 'r')
    result = f.readline()
    f.close()
    return result


if __name__ == '__main__':
    if len(sys.argv) != 7:
        sys.stderr.write("usage: python forecastio.py lat lon start_day end_day position city\n")
        sys.exit(1)
    lat = sys.argv[1]
    lon = sys.argv[2]
    tmp = sys.argv[3].split('-')
    start_day = datetime.date(int(tmp[0]), int(tmp[1]), int(tmp[2]))
    tmp = sys.argv[4].split('-')
    end_day = datetime.date(int(tmp[0]), int(tmp[1]), int(tmp[2]))
    position_name = sys.argv[5]
    c_name = sys.argv[6]
    print 'Collect data for ' + c_name + ' day by day'
    client = pymongo.MongoClient('127.0.0.1')
    client.forecastio.authenticate("john","12345gis")
    db = client.forecastio
    c = db[c_name]
    day_i = start_day
    while day_i.isoformat() <= end_day.isoformat():
        my_url = URL_BASE + '/' + lat + ',' + lon + ',' + day_i.isoformat() + 'T00:00:00'
        print day_i.isoformat()
        result = callAPI(my_url)
        result = result[0] + '"position":"' + position_name + '",' + '"date":"' + day_i.isoformat() + '",' \
                 + result[1:len(result)]
        text = demjson.decode(result)
        c.insert(text)
        day_i = day_i + datetime.timedelta(1)
    client.close()
    print 'finished!'
