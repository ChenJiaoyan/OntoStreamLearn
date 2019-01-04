# -*- coding: utf-8 -*-
"""Form the dataset."""
from os.path import join

import pandas as pd
import numpy as np
import KBPA_StockPrediction.settings.parameters as para
import KBPA_StockPrediction.utils.splitData as split_data
import inspect

from KBPA_StockPrediction.data.stock.BagOfEntailment import BOE
from KBPA_StockPrediction.data.TransE import getStockAttention, getStock_IndexVectorDistance, getStock
from KBPA_StockPrediction.data.tweets.conceptExt import form_wordVec, getTimestamps, getDateTime
from KBPA_StockPrediction.data.stock.BagOfEntailment import difference


def prepare_data(path_data):
    """load the raw data from the directory and adjust the data for a model."""
    """prepare data for the model."""
    discrete_X = []
    discrete_y = []
    continous_X = []
    continous_y = []
    """LSTM用的是data_stocks.csv的数据
        CNN用的是tweet的数据
    """
    """
    以下的注释是ijcai中实验的版本
    """
    f = open(path_data)
    df = pd.read_csv(f)
    data = df.values
    f.close()
    names = getStock(join(para.DATA_INPUT_DIRECTORY, "data_stocks.csv"))
    time = data[:, 0]
    index_value = data[:, 1]
    stock_value = data[:, 2:-1]

    """用CNN，处理的data是wordVec_Form.json & data_stocks.csv
        data就是load data_stocks.csv的结果
    """
    continous_X = []
    continous_y = []
    x_tweets = []
    # y_difference = data[:, 1]
    d_wordVec_form = form_wordVec(join(para.SEMI_RESULT_DIRECTORY, "sentences.json"))
    for key in d_wordVec_form.keys():
        # if key[6:10] != "7-03":
        if key != "2017-07-03":
            x_tweets.append(np.transpose(np.array(d_wordVec_form[key])).tolist())
        # x_tweets.append(np.transpose(np.array(d_wordVec_form[key])).tolist())

    continous_X = x_tweets

    # """continous_y等于整点时候S&P 500的值，9:30, 10:00, 11:00……16:00"""
    # splits_byHour = []
    # list_begin = [0, 30, 90, 150, 210, 270, 330, 390]
    # for i in range(63):
    #     for j in list_begin:
    #         splits_byHour.append(391 * i + j)
    # for i in range(5):
    #     splits_byHour.append(63 * 391 + list_begin[i])
    # for i in range(42):
    #     for j in list_begin:
    #         splits_byHour.append(63 * 391 + 210 + 391 * i + j)
    # for i in range(len(splits_byHour)):
    #     # continous_y.append(y_difference[i])
    #     continous_y.append(data[:, 1][i])

    if para.WEIGHT == 1:
        base = "<http://urbankg.org/ontology/StockIndex/"
        list_stock = getStock_IndexVectorDistance(join(para.SEMI_RESULT_DIRECTORY, "stock_indexDistance.txt"))
        stockattention_list = getStockAttention(list_stock)
        for i in range(len(names)):
            # print(stock_value[:, i])
            stock_value[:, i] *= stockattention_list[base + names[i] + ">"]
            # print(stock_value[:, i])

    """用LSTM，处理的是data_stocks.csv，data就是load data_stocks.csv的结果"""
    """还会加入entailment vector"""
    if para.BOE == 1:
        path_company = join(para.DATA_INPUT_DIRECTORY, "List of S&P 500 companies.xls")
        difference_index = []
        d = difference(path_data)
        for i in range(len(d)):
            difference_index.append(d[i][0])
        boe_sector, _, _, _, boe = BOE(path_data, path_company, difference_index)
        input_data = []
        for i in range(len(boe)):
            input_data.append(list(stock_value[i]) + list(boe[i]))

    discrete_X = []
    discrete_y = []

    index_difference = []
    index_difference.append(0)
    for i in range(len(index_value) - 1):
        index_difference.append("%.1f" % (index_value[i + 1] - index_value[i]))

    splits = []
    for i in range(64):
        splits.append(i * 391)

    splits.append(63 * 391 + 211)

    for i in range(42):
        splits.append(63 * 391 + 211 + (i + 1) * 391)

    # splits_rand = []
    # for i in range(20):
    #     splits_rand.append(np.random.randint(1, 60))
    # for i in range(len(splits_rand)):
    #     discrete_X.append(stock_value[splits[i]: splits[i + 1]])
    #     # discrete_X.append(input_data[splits[i]: splits[i + 1]])
    #     discrete_y.append(index_value[splits[i]: splits[i + 1]])
    #     continous_X.append(stock_value[splits[i]: splits[i + 1]])
    #     # continous_X.append(input_data[splits[i]: splits[i + 1]])
    #     continous_y.append(index_value[splits[i]: splits[i + 1]])
    #     # continous_y.append(index_difference[splits[i]: splits[i + 1]])
    #     # continous_y = np.array(continous_y).astype(float).tolist()

    for i in range(len(splits) - 1):
        if i == 63:
            continue
        # continous_X.append(stock_value[splits[i]: splits[i + 1]])
        # continous_y.append(index_difference[splits[i]: splits[i + 1]])
        # continous_y.append(y_difference[splits[i]: splits[i + 1]])
        if para.BOE != 1:
            discrete_X.append(stock_value[splits[i]: splits[i + 1]])
        else:
            discrete_X.append(input_data[splits[i]: splits[i + 1]])
        discrete_y.append(index_value[splits[i]: splits[i + 1]])

        # continous_y.append(index_value[splits[i]: splits[i + 1]])
        continous_y.append(index_difference[splits[i]: splits[i + 1]])
        continous_y = np.array(continous_y).astype(float).tolist()

    # f = open(path_data)
    # df = pd.read_csv(f)
    # data = df.values
    # f.close()
    # index_value = data[:, 1]
    # stock_value = data[:, 2:-1]
    # names = getStock(path_data)
    # if para.WEIGHT == 1:
    #     base = "<http://urbankg.org/ontology/StockIndex/"
    #     list_stock = getStock_IndexVectorDistance(join(para.SEMI_RESULT_DIRECTORY, "stock_indexDistance.txt"))
    #     stockattention_list = getStockAttention(list_stock)
    #     for i in range(len(names)):
    #         # print(stock_value[:, i])
    #         stock_value[:, i] *= stockattention_list[base + names[i] + ">"]
    #         # print(stock_value[:, i])
    # if para.BOE == 1:
    #     path_company = join(para.DATA_INPUT_DIRECTORY, "List of S&P 500 companies.xls")
    #     difference_index = []
    #     d = difference(path_data)
    #     for i in range(len(d)):
    #         difference_index.append(d[i][0])
    #     boe_sector, _, _, _, boe = BOE(path_data, path_company, difference_index)
    #     input_data = []
    #     for i in range(len(boe)):
    #         input_data.append(list(stock_value[i]) + list(boe[i]))
    # splits = []
    # for i in range(1, 64):
    #     splits.append(i * 391 - 1)
    # splits.append(63 * 391 + 211 - 1)
    # for i in range(42):
    #     splits.append(63 * 391 + 211 + (i + 1) * 391 - 1)
    #
    # index_value_daily = []
    # stock_value_daily = []
    # for i in range(len(splits)):
    #     if para.BOE != 1:
    #         stock_value_daily.append([stock_value[splits[i], :]])
    #     else:
    #         stock_value_daily.append(input_data[splits[i], :])
    #     index_value_daily.append(index_value[splits[i]])
    # stock_value_daily = np.array(stock_value_daily).astype(float).tolist()
    # discrete_X = stock_value_daily
    # discrete_y = index_value_daily
    # """用CNN，处理的data是wordVec_Form.json & data_stocks.csv
    #     data就是load data_stocks.csv的结果
    # """
    # x_tweets = []
    # d_wordVec_form = form_wordVec(join(para.SEMI_RESULT_DIRECTORY, "sentences.json"))
    # for key in d_wordVec_form.keys():
    #     # if key != "2017-07-03":
    #     #     x_tweets.append(np.transpose(np.array(d_wordVec_form[key])).tolist())
    #     x_tweets.append(np.transpose(np.array(d_wordVec_form[key])).tolist())
    # continous_X = x_tweets
    # index_difference_daily = []
    # index_difference_daily.append(0)
    # for i in range(len(splits) - 1):
    #     index_difference_daily.append("%.1f" % (index_value[splits[i + 1]] - index_value[splits[i]]))
    # continous_y = index_difference_daily

    return continous_X, continous_y, discrete_X, discrete_y

def normalize_labels(labels):
    """normalize the labels.

    normalize the index value, make them in the range of -1 and 1.
    choose the normalization method mentioned below:
    (x - x_min) / (x_max - x_min) + x_min
    """
    max_labels = []
    min_labels = []
    for i in range(len(labels)):
        max_labels.append(np.max(labels[i], axis=0))
        min_labels.append(np.min(labels[i], axis=0))
        labels[i] = 1.0 * (labels[i] - min_labels[i]) / (max_labels[i] - min_labels[i])
    return labels, {"max_labels": max_labels, "min_labels": min_labels}


def normalize_data(data):
    """normalize the dataset."""
    train_data, train_labels = data["train_data"], data["train_labels"]
    val_data, val_labels = data["validation_data"], data["validation_labels"]
    test_data, test_labels = data["test_data"], data["test_labels"]

    train_labels, mapping = normalize_labels(train_labels)
    for i in range(len(val_labels)):
        val_labels[i] = (val_labels[i] - mapping["min_labels"][i]) / (
            mapping["max_labels"][i] - mapping["min_labels"][i])
    for i in range(len(test_labels)):
        test_labels[i] = (test_labels[i] - mapping["min_labels"][i]) / (
            mapping["max_labels"][i] - mapping["min_labels"][i])
    return train_data, train_labels, \
        val_data, val_labels, \
        test_data, test_labels, mapping


def init_data(dataset, model):
    """define parameters and prepare data."""
    # define path.
    path_data = join(para.DATA_INPUT_DIRECTORY, dataset)

    # form the data.
    print("load the dataset and form the dataset...")
    continous_X, continous_y, discrete_X, discrete_y = prepare_data(path_data)

    if inspect.isclass(model):
        if model.__name__ not in para.MIXTURE_MODELS:
            if model.__name__ in para.CONTINUOUS_MODELS:
                print("load data for continous model.")
                X, y = continous_X, continous_y
            else:
                print("load data for discrete model.")
                X, y = discrete_X, discrete_y
        else:
            print("load data for mixture model.")
            X = np.array(zip(continous_X, discrete_X))
            y = np.array(continous_y)
    else:
        print("load data for baseline model.")
        discrete_X = np.array(discrete_X).reshape((len(discrete_X), -1))
        continous_X = np.array(continous_X)
        X = np.hstack((continous_X, discrete_X))
        y = continous_y

    # split the dataset to train, validation, and test.
    print("split the dataset into train, validation, and test...")
    data = split_data.split_data(X, y)
    print("stat:: train/validation/test split: {}/{}/{}".format(
        data["train_data"].shape,
        data["validation_data"].shape,
        data["test_data"].shape))
    return data
