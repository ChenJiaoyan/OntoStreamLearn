import datetime
import os
import csv
import sys
from collections import Counter

import tensorflow as tf
import pandas as pd
import numpy as np
from os.path import join
import settings.parameters as para
from TransE import getStock
import xlrd

# path_data = join(para.DATA_INPUT_DIRECTORY, "data_stocks.csv")
# f = open(path_data)
# df = pd.read_csv(f)
# data = df.values
# f.close()
"""生成stock和index差分数据文件"""
# data_difference = []
# data_difference.append([0] * (len(data[0]) - 2))
#
# filepath = join(para.DATA_INPUT_DIRECTORY, "dataDifference_stocks.csv")
# output_file = open(filepath, 'a', -1, 'UTF-8')
# output_file.write(str(data_difference[0]) + "\n")
# print(data_difference[0])
# for i in range(len(data) - 1):
#     a = data[i+1, 1:-1]
#     b = data[i, 1:-1]
#     data_difference.append([x-y for x, y in zip(a, b)])
#     output_file.write(str(data_difference[i+1]) + "\n")
#     print(i + 1)
#     # print(data_difference[i+1])
def difference(path_data):
    f = open(path_data)
    df = pd.read_csv(f)
    data = df.values
    f.close()
    data_difference = []
    data_difference.append([0] * (len(data[0]) - 2))
    for i in range(len(data) - 1):
        a = data[i+1, 1:-1]
        b = data[i, 1:-1]
        data_difference.append([x-y for x, y in zip(a, b)])
    return data_difference

def get_simple_stock_name(path_data):
    names = getStock(path_data)
    names_1 = []
    for name in names:
        name_1 = name.split(".")[1]
        names_1.append(name_1)
    return names_1

def company_info(path_company):
    # path_company = join(para.DATA_INPUT_DIRECTORY, "List of S&P 500 companies.xls")
    data_c = xlrd.open_workbook(path_company)
    table = data_c.sheets()[0]
    nrows = table.nrows  # 行数
    ncols = table.ncols  # 列数
    names_stock = []
    security = []
    sector = []
    subInd = []
    city = []
    country = []
    names = get_simple_stock_name(join(para.DATA_INPUT_DIRECTORY, "data_stocks.csv"))
    for name in names:
        for i in range(1, nrows):
            rowValues = table.row_values(i)  # 某一行数据
            if rowValues[0] == name:
                names_stock.append(rowValues[0])
                security.append(rowValues[1])
                sector.append(rowValues[3])
                subInd.append(rowValues[4])
                address = rowValues[5]
                s = str(address).split(", ")
                city.append(s[0])
                country.append(s[1])
                pos = 1
                break
            else:
                pos = 0
        if pos == 0:
            names_stock.append(name)
            security.append("")
            sector.append("")
            subInd.append("")
            city.append("")
            country.append("")
    return names_stock, security, sector, subInd, city, country

def remove_empty(lst):
    for s in lst:
        if s == '' or s == "":
            lst.remove(s)
    for s in lst:
        if s == '' or s == "":
            lst.remove(s)
    return lst
def set_e(path_company):
    names_stock, security, sector, subInd, city, country = company_info(path_company)
    security = remove_empty(security)
    sector = remove_empty(sector)
    subInd = remove_empty(subInd)
    city = remove_empty(city)
    country = remove_empty(country)
    return list(set(security)), list(set(sector)), list(set(subInd)), list(set(city)), list(set(country))

def BOE(path_data, path_company, difference_index):
    data_difference = difference(path_data)
    names_stock, security, sector, subInd, city, country = company_info(path_company)
    set_security, set_sector, set_subInd, set_city, set_country = set_e(path_company)
    # print(len(set_sector), len(set_subInd), len(set_city), len(set_country)) # 11 120 242 50
    len_row = len(data_difference)
    # boe_security = [[0 for col in range(len(set_security))] for row in range(len_row)]
    boe_sector = [[0 for col in range(len(set_sector))] for row in range(len_row)]
    boe_subInd = [[0 for col in range(len(set_subInd))] for row in range(len_row)]
    boe_city = [[0 for col in range(len(set_city))] for row in range(len_row)]
    boe_country = [[0 for col in range(len(set_country))] for row in range(len_row)]
    # boe = [[0 for col in range(len(set_city) + len(set_city) + len(set_subInd) + len(set_sector))] for row in range(len_row)]
    boe = []
    for i in range(len(data_difference)):
        list_security = []
        list_sector = []
        list_subInd = []
        list_city = []
        list_country = []
        # for j in range(len(data_difference[i][1:-1])):
        for j in range(len(names_stock)):
            if round(data_difference[i][j], 1) == round(difference_index[i], 1):
                # list_security.append(security[j])
                if sector[j] != '':
                    list_sector.append(sector[j])
                if subInd[j] != '':
                    list_subInd.append(subInd[j])
                if city[j] != '':
                    list_city.append(city[j])
                if country[j] != '':
                    list_country.append(country[j])
        # security_count = Counter(list_security)
        sector_count = Counter(list_sector)
        subInd_count = Counter(list_subInd)
        city_count = Counter(list_city)
        country_count = Counter(list_country)
        # boe_security[i][set_security.index(security_count.most_common(1)[0][0])] = 1
        boe_sector[i][set_sector.index(sector_count.most_common(1)[0][0])] = 1
        boe_subInd[i][set_subInd.index(subInd_count.most_common(1)[0][0])] = 1
        boe_city[i][set_city.index(city_count.most_common(1)[0][0])] = 1
        boe_country[i][set_country.index(country_count.most_common(1)[0][0])] = 1
        # boe[i] = boe_sector[i] + boe_subInd[i] + boe_city[i] + boe_country[i]
        boe.append(boe_sector[i] + boe_subInd[i] + boe_city[i] + boe_country[i])
        # print(len(boe_sector[i]), len(boe_subInd[i]), len(boe_city[i]), len(boe_country[i]), len(boe[i]))

        # boe_security[i] = ratio_in_boe(security_count, set_security)
        # boe_sector[i] = ratio_in_boe(sector_count, set_sector)
        # boe_subInd[i] = ratio_in_boe(subInd_count, set_subInd)
        # boe_city[i] = ratio_in_boe(city_count, set_city)
        # boe_country[i] = ratio_in_boe(country_count, set_country)
        print(i)
        # print(boe_sector[i])
    return boe_sector, boe_subInd, boe_city, boe_country, boe

def ratio_in_boe(count_s, set_s):
    r = []
    s = count_s.most_common(len(set_s))
    # print(len(set_s), len(s))
    for i in range(len(s)):
        r.append(s[i][1])
    return list(softmax(r))

def softmax(x):
    return np.exp(x) / np.sum(np.exp(x), axis=0)

if __name__ == '__main__':
    print("come on")
    path_company = join(para.DATA_INPUT_DIRECTORY, "List of S&P 500 companies.xls")
    path_data = join(para.DATA_INPUT_DIRECTORY, "data_stocks.csv")
    difference_index = []
    d = difference(path_data)
    for i in range(len(d)):
        difference_index.append(d[i][0])
    # boe_sector, boe_subInd, boe_city, boe_country, boe = BOE(path_data, path_company, difference_index)
    # print(len(boe), len(boe[0]))
    names_stock, security, sector, subInd, city, country = company_info(path_company)
    set_security, set_sector, set_subInd, set_city, set_country = set_e(path_company)
    sector_count = Counter(sector)
    subInd_count = Counter(subInd)
    city_count = Counter(city)
    country_count = Counter(country)
    # print(sector_count.most_common(10))
    # print(subInd_count.most_common(10))
    # print(city_count.most_common(10))
    # print(country_count.most_common(10))
    # print(set_security)
    # print(set_sector)
    # print(set_subInd)
    # print(set_city)
    # print(set_country)