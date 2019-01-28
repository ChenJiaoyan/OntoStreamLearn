#! /usr/bin/python
# coding=utf-8

import os
import csv
from datetime import datetime

Air_Exps = ['Air_Good', 'Air_Moderate', 'Air_Unhealthy', 'Air_Veryunhealthy', 'Air_Hazardous', 'Air_Emergent']
Wea_Exps = ['Wea_Breezy', 'Wea_Clear', 'Wea_Dry', 'Wea_Foggy', 'Wea_Humid', 'Wea_MostlyCloudy', 'Wea_Overcast',
            'Wea_PartlyCloudy', 'Wea_Windy']

Win_Exps = ['Win_Calm', 'Win_LightAir', 'Win_LightBreeze', 'Win_GentleBreeze', 'Win_ModerateBreeze', 'Win_FreshBreeze',
            'Win_StrongBreeze', 'Win_HighWindAndLarger']
Clo_Exps = ['Clo_Sunny', 'Clo_PartlyCloudy', 'Clo_MostlyCloudy', 'Clo_Cloudy']
Hum_Exps = ['Hum_Low', 'Hum_Middle', 'Hum_High']

Hou_Exps = ['RushHour_Morning', 'RushHour_Afternoon', 'RushHour_None']
Day_Exps = ['Weekend', 'Weekday']

Spa_Exps = ['Pol_DownWind_NE', 'Pol_DownWind_NW', 'Pol_DownWind_SW', 'Pol_DownWind_SE']

Exps = Air_Exps + Wea_Exps + Win_Exps + Clo_Exps + Hum_Exps + Hou_Exps + Day_Exps + Spa_Exps
Exps_order = [Air_Exps, Wea_Exps, Win_Exps, Clo_Exps, Hum_Exps, Hou_Exps, Day_Exps, Spa_Exps]

DIR = '../samples'


def get_KBs(city):
    KBs = []
    file_name = os.path.join(DIR, city + '_Labels.csv')
    with open(file_name) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            KBs.append(row['KB'])
    return KBs


def get_AirBOE(city):
    AirBOE = []
    file_name = os.path.join(DIR, city + '_0_AQI.csv')
    with open(file_name) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            if row['AQI-0'] == 'NaN' or int(row['AQI-0']) == 0:
                boe = [-1] * len(Air_Exps)
            else:
                aqi = int(row['AQI-0'])
                boe = [0] * len(Air_Exps)
                if aqi <= 50:
                    boe[0] = 1
                elif aqi <= 100:
                    boe[1] = 1
                elif aqi <= 150:
                    boe[2] = 1
                elif aqi <= 200:
                    boe[3] = 1
                elif aqi <= 300:
                    boe[4] = 1
                else:
                    boe[5] = 1
            AirBOE.append(boe)
    return AirBOE


def get_WeaBOE(city):
    WeaBOE = []
    file_name = os.path.join(DIR, city + '_0_Mete.csv')
    with open(file_name) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            summary = row['summary-0']
            if summary == 'NaN':
                boe = [-1] * len(Wea_Exps)
            else:
                boe = [0] * len(Wea_Exps)
                if 'breezy' in summary.lower():
                    boe[0] = 1
                elif 'clear' in summary.lower():
                    boe[1] = 1
                elif 'dry' in summary.lower():
                    boe[2] = 1
                elif 'foggy' in summary.lower():
                    boe[3] = 1
                elif 'humid' in summary.lower():
                    boe[4] = 1
                elif 'mostly cloudy' in summary.lower():
                    boe[5] = 1
                elif 'overcast' in summary.lower():
                    boe[6] = 1
                elif 'partly cloudy' in summary.lower():
                    boe[7] = 1
                else:
                    boe[8] = 1
            WeaBOE.append(boe)
    return WeaBOE


def get_WinBOE(city):
    WinBOE = []
    file_name = os.path.join(DIR, city + '_0_Mete.csv')
    with open(file_name) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            windSpeed = row['windSpeed-0']
            if windSpeed == 'NaN':
                boe = [-1] * len(Win_Exps)
            else:
                boe = [0] * len(Win_Exps)
                s = float(windSpeed)
                if s < 1.1:
                    boe[0] = 1
                elif s < 5.5:
                    boe[1] = 1
                elif s < 11.9:
                    boe[2] = 1
                elif s < 19.7:
                    boe[3] = 1
                elif s < 28.7:
                    boe[4] = 1
                elif s < 38.8:
                    boe[5] = 1
                elif s < 49.9:
                    boe[6] = 1
                else:
                    boe[7] = 1
            WinBOE.append(boe)
    return WinBOE


def get_CloBOE(city):
    CloBOE = []
    file_name = os.path.join(DIR, city + '_0_Mete.csv')
    with open(file_name) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            cloudCover = row['cloudCover-0']
            if cloudCover == 'NaN':
                boe = [-1] * len(Clo_Exps)
            else:
                boe = [0] * len(Clo_Exps)
                c = float(cloudCover)
                if c < 0.2:
                    boe[0] = 1
                elif c < 0.5:
                    boe[1] = 1
                elif c < 0.8:
                    boe[2] = 1
                else:
                    boe[3] = 1
            CloBOE.append(boe)
    return CloBOE


def get_HumBOE(city):
    HumBOE = []
    file_name = os.path.join(DIR, city + '_0_Mete.csv')
    with open(file_name) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            humidity = row['humidity-0']
            if humidity == 'NaN':
                boe = [-1] * len(Hum_Exps)
            else:
                boe = [0] * len(Hum_Exps)
                h = float(humidity)
                if h < 0.4:
                    boe[0] = 1
                elif h < 0.7:
                    boe[1] = 1
                else:
                    boe[2] = 1
            HumBOE.append(boe)
    return HumBOE


def get_HouBOE_DayBOE(city):
    HouBOE = []
    DayBOE = []
    file_name = os.path.join(DIR, city + '_Labels.csv')
    with open(file_name) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            dt = datetime.strptime(row['KB'], '%Y-%m-%dT%H')
            h_boe = [0] * len(Hou_Exps)
            if 7 <= dt.hour < 10:
                h_boe[0] = 1
            elif 17 <= dt.hour < 20:
                h_boe[1] = 1
            else:
                h_boe[2] = 1
            HouBOE.append(h_boe)

            d_boe = [0] * len(Day_Exps)
            if 5 <= dt.weekday() <= 6:
                d_boe[0] = 1
            else:
                d_boe[1] = 1
            DayBOE.append(d_boe)

    return HouBOE, DayBOE


def read_col(file_name, col_name, col_type):
    res = []
    with open(file_name) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            item = row[col_name]
            if col_type == 'int' and item != 'NaN':
                item = int(item)
            if col_type == 'float' and item != 'NaN':
                item = float(item)
            res.append(item)
    return res


def get_SpaBOE(city):
    SpaBOE = []
    AQI, WinB, WinS = [], [], []
    for i in range(5):
        AQI.append(read_col(os.path.join(DIR, city + "_" + str(i) + "_AQI.csv"), 'AQI-0', 'int'))
        WinB.append(read_col(os.path.join(DIR, city + "_" + str(i) + "_Mete.csv"), 'windBearing-0', 'int'))
        WinS.append(read_col(os.path.join(DIR, city + "_" + str(i) + "_Mete.csv"), 'windSpeed-0', 'float'))

    for i, aqi0 in enumerate(AQI[0]):
        if aqi0 == 'NaN' or aqi0 == 0:
            boe = [-1] * len(Spa_Exps)
        else:
            boe = [0] * len(Spa_Exps)
            if AQI[1][i] == 'NaN' or AQI[1][i] == 0 or WinS[1][i] == 'NaN':
                boe[0] = -1
            else:
                if AQI[1][i] - aqi0 >= 50 and WinS[1][i] >= 1.1 and 0 < WinB[1][i] < 90:
                    boe[0] = 1

            if AQI[2][i] == 'NaN' or AQI[2][i] == 0 or WinS[2][i] == 'NaN':
                boe[1] = -1
            else:
                if AQI[2][i] - aqi0 >= 50 and WinS[2][i] >= 1.1 and 270 < WinB[2][i] < 360:
                    boe[1] = 1

            if AQI[3][i] == 'NaN' or AQI[3][i] == 0 or WinS[3][i] == 'NaN':
                boe[2] = -1
            else:
                if AQI[3][i] - aqi0 >= 50 and WinS[3][i] >= 1.1 and 180 < WinB[3][i] < 270:
                    boe[2] = 1

            if AQI[4][i] == 'NaN' or AQI[4][i] == 0 or WinS[4][i] == 'NaN':
                boe[3] = -1
            else:
                if AQI[4][i] - aqi0 >= 50 and WinS[4][i] >= 1.1 and 90 < WinB[4][i] < 180:
                    boe[3] = 1

        SpaBOE.append(boe)

    return SpaBOE


if __name__ == '__main__':
    CITY = 'BJ'
    rows = [['KB'] + Exps]

    print 'KBs ...'
    KBs = get_KBs(city=CITY)

    print 'Air BOE ...'
    Air_BOE = get_AirBOE(city=CITY)

    print 'Wea BOE ...'
    Wea_BOE = get_WeaBOE(city=CITY)

    print 'Win BOE ...'
    Win_BOE = get_WinBOE(city=CITY)

    print 'Clo BOE ...'
    Clo_BOE = get_CloBOE(city=CITY)

    print 'Hum BOE ...'
    Hum_BOE = get_HumBOE(city=CITY)

    print 'Hou Day BOE ...'
    Hou_BOE, Day_BOE = get_HouBOE_DayBOE(city=CITY)

    print 'Spa BOE ...'
    Spa_BOE = get_SpaBOE(city=CITY)

    for i, KB in enumerate(KBs):
        boe = Air_BOE[i] + Wea_BOE[i] + Win_BOE[i] + Clo_BOE[i] + Hum_BOE[i] + Hou_BOE[i] + Day_BOE[i] + Spa_BOE[i]
        row = [KB] + boe
        rows.append(row)

    print 'write ...'
    f = open(os.path.join(DIR, CITY + '_BOE.csv'), 'wb')
    writer = csv.writer(f)
    writer.writerows(rows)
    f.close()

    print 'finished'
