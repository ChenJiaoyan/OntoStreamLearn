#coding=utf-8

import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from matplotlib.pylab import rcParams
import datetime
from os.path import join
import KBPA_StockPrediction.settings.parameters as para

rcParams['figure.figsize'] = 15, 6
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima_model import ARIMA


def test_stationarity(timeseries):
    # 决定起伏统计
    rolmean = pd.rolling_mean(timeseries, window=12) # 平均数
    rolstd = pd.rolling_std(timeseries, window=12) # 偏离原始值多少
    # 画出起伏统计
    orig = plt.plot(timeseries, color='blue', label='Original')
    mean = plt.plot(rolmean, color='red', label='Rolling Mean')
    std = plt.plot(rolstd, color='black', label='Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show(block=False)
    # 进行df测试
    print('Result of Dickry-Fuller test')
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic', 'p-value', '#Lags Used', 'Number of observations Used'])
    for key, value in dftest[4].items():
        dfoutput['Critical value(%s)' % key] = value
    print(dfoutput)

def arima_pred(datapath):
    f = open(datapath)
    df = pd.read_csv(f, encoding='utf-8', index_col='DATE')
    data = df.values
    f.close()
    ts = df['INDEX']
    # plt.plot(ts)
    # plt.show()
    # test_stationarity(ts)
    # plt.show()

    ##estimating##

    ts_log = np.log(ts)
    moving_avg = pd.rolling_mean(ts_log, 391)
    # plt.plot(moving_avg)
    # plt.plot(moving_avg,color='red')
    # plt.show()
    ts_log_moving_avg_diff = ts_log - moving_avg
    # print ts_log_moving_avg_diff.head(12)
    ts_log_moving_avg_diff.dropna(inplace=True)
    # test_stationarity(ts_log_moving_avg_diff)
    # plt.show()
    ##diffrencing##
    ts_log_diff = ts_log - ts_log.shift()
    ts_log_diff.dropna(inplace=True)

    # test_stationarity(ts_log_decompose)
    # plt.show()
    ##预测##

    '''
    #确定参数
    lag_acf = acf(ts_log_diff,nlags=20)
    lag_pacf = pacf(ts_log_diff,nlags=20,method='ols')
    #q的获取:ACF图中曲线第一次穿过上置信区间.这里q取2
    plt.subplot(121)
    plt.plot(lag_acf)
    plt.axhline(y=0,linestyle='--',color='gray')
    plt.axhline(y=-1.96/np.sqrt(len(ts_log_diff)),linestyle='--',color='gray')#lowwer置信区间
    plt.axhline(y=1.96/np.sqrt(len(ts_log_diff)),linestyle='--',color='gray')#upper置信区间
    plt.title('Autocorrelation Function')
    #p的获取:PACF图中曲线第一次穿过上置信区间.这里p取2
    plt.subplot(122)
    plt.plot(lag_pacf)
    plt.axhline(y=0,linestyle='--',color='gray')
    plt.axhline(y=-1.96/np.sqrt(len(ts_log_diff)),linestyle='--',color='gray')
    plt.axhline(y=1.96/np.sqrt(len(ts_log_diff)),linestyle='--',color='gray')
    plt.title('Partial Autocorrelation Function')
    plt.tight_layout()
    plt.show()
    '''

    '''
    #AR model
    model = ARIMA(ts_log,order=(2,1,0))
    result_AR = model.fit(disp=-1)
    plt.plot(ts_log_diff)
    plt.plot(result_AR.fittedvalues,color='red')
    plt.title('RSS:%.4f'%sum(result_AR.fittedvalues-ts_log_diff)**2)
    plt.show()
    '''

    '''
    #MA model
    model = ARIMA(ts_log,order=(0,1,2))
    result_MA=model.fit(disp=-1)
    plt.plot(ts_log_diff)
    plt.plot(result_MA.fittedvalues,color='red')
    plt.title('RSS:%.4f'%sum(result_MA.fittedvalues-ts_log_diff)**2)
    plt.show()
    '''

    # ARIMA 将两个结合起来  效果更好
    model = ARIMA(ts_log, order=(2, 1, 2))
    result_ARIMA = model.fit(disp=-1)
    # plt.plot(ts_log_diff)
    # plt.plot(result_ARIMA.fittedvalues, color='red')
    # plt.title('RSS:%.4f' % sum(result_ARIMA.fittedvalues-ts_log_diff)**2)
    # plt.show()

    predictions_ARIMA_diff = pd.Series(result_ARIMA.fittedvalues, copy=True)
    # print predictions_ARIMA_diff.head()# 发现数据是没有第一行的,因为有1的延迟

    predictions_ARIMA_diff_cumsum = predictions_ARIMA_diff.cumsum()
    # print predictions_ARIMA_diff_cumsum.head()

    predictions_ARIMA_log = pd.Series(ts_log.ix[0], index=ts_log.index)
    predictions_ARIMA_log = predictions_ARIMA_log.add(predictions_ARIMA_diff_cumsum, fill_value=0)
    # print predictions_ARIMA_log.head()

    predictions_ARIMA = np.exp(predictions_ARIMA_log)
    plt.plot(ts)
    plt.plot(predictions_ARIMA)
    plt.title('RMSE: %.4f' % np.sqrt(sum((predictions_ARIMA-ts)**2)/len(ts)))
    plt.show()
    rmse = np.sqrt(sum((predictions_ARIMA - ts) ** 2) / len(ts))
    mae = sum(abs(predictions_ARIMA - ts)) / len(ts)
    mape = sum(abs(predictions_ARIMA - ts) / ts) / len(ts)
    return predictions_ARIMA, rmse, mae, mape

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    datapath = join(para.DATA_INPUT_DIRECTORY, "data_stocks.csv")
    predictions_ARIMA, rmse, mae, mape = arima_pred(datapath)
    print(predictions_ARIMA)
    print("rmse, mae, mape: ", rmse, mae, mape)
    exection_time = (datetime.datetime.now() - start_time).total_seconds()

    # arima_file = open(join(para.DATA_OUTPUT_DIRECTORY, "ARIMA.txt"), "w")
    # for v in predictions_ARIMA:
    #     arima_file.write(str(v) + "\n")
    # arima_file.close()

    print("execution time: ", exection_time, "seconds")
