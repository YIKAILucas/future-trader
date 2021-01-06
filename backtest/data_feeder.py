# coding=utf-8

# @Author : Lucas
# @Date   : 2020/12/30 5:13 pm
# @Last Modified by:  Lucas
# @Last Modified time:

import datetime as dt

import pandas as pd
import tushare as ts

from backtest.path import ROOT_DIR


def dmy2ymd(dmy):
    # 把dmy格式的字符串转化成ymd格式的字符串
    dmy = str(dmy).split()[0]
    # print(dmy)
    if dmy == 'NaT':
        return None
    d = dt.datetime.strptime(dmy, '%Y-%m-%d')
    d = d.date()
    # ymd = d.strftime('%Y-%m-%d')

    return d


def dmy2ymd2(dmy):
    # 把dmy格式的字符串转化成ymd格式的字符串
    dmy = str(dmy).split()[0]
    # print(dmy)
    if dmy == 'NaT':
        return None
    d = dt.datetime.strptime(dmy, '%Y%m%d')
    d = d.date()
    # ymd = d.strftime('%Y-%m-%d')

    return d


class DataFeederAdapter(object):
    def __init__(self):
        pass

    @staticmethod
    def get_tushare() -> pd.DataFrame:
        ts.set_token('4680f3e9395b06311cf43c1627e3624da1e4d0b4e273caea0206c8ad')
        pro = ts.pro_api()
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 100)
        pd.set_option('display.max_columns', None)

        # df = pro.fut_basic(exchange='CZCE', fut_type='2', fields='ts_code,symbol,name,list_date,delist_date')
        # df = pro.fut_daily(ts_code='CU1811.CZCE', start_date='20180101', end_date='20181113')

        df: pd.DataFrame = pro.fut_daily(ts_code='CF.ZCE', start_date='20140307', end_date='20181012')
        # print(df)
        # print(df.loc[:, ['pre_close', 'trade_date', 'close', 'open', 'high', 'low']])
        trans_date = [dmy2ymd2(d) for d in df['trade_date']]

        df['date'] = trans_date
        # df['vol'].rename(['volume'],inplace=True)

        df.rename(columns={'vol':'volume'},inplace=True)

        # df.apply(lambda df.loc[:,[;date]]=1)

        # df.set_index(['date'], inplace=True)
        df = df[['date', 'open', 'close', 'high', 'low', 'volume']]
        df.sort_values(by=['date'], ascending=True, inplace=True)
        df.to_csv('cc.csv', index=False)

        dataframe = pd.read_csv('cc.csv', parse_dates=True, index_col=[0])

        return dataframe.loc[:, ['open', 'close', 'high', 'low', 'volume']]

    @staticmethod
    def csv_data_feed() -> pd.DataFrame:
        dataframe = pd.read_csv(ROOT_DIR + '/boll.csv', encoding='utf-8_sig', parse_dates=True)
        dataframe.dropna()
        trans_date = [dmy2ymd(d) for d in dataframe['日期']]

        dataframe['date'] = trans_date
        # print(dataframe.shape)
        dataframe['openinterest'] = 0
        dataframe['volume'] = [0] * dataframe.shape[0]

        dataframe.rename(columns={'开盘价(元)': 'open', '收盘价(元)': 'close', '最高价(元)': 'high', '最低价(元)': 'low'},
                         inplace=True)

        dataframe = dataframe[['date', 'open', 'close', 'high', 'low', 'volume']]

        dataframe.to_csv('cdata.csv', index=False)

        dataframe = pd.read_csv('cdata.csv', parse_dates=True, index_col=[0])

        # print(dataframe.info())
        # print(dataframe.describe())
        # print(dataframe.head())

        return dataframe


if __name__ == '__main__':
    d1 = DataFeederAdapter.get_tushare()
    d2 = DataFeederAdapter.csv_data_feed()

    print(d1.head())
    print('-----------------')
    print(d2.head())

    print(d1.info())
    print(d2.info())
