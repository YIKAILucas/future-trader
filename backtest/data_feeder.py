# coding=utf-8

# @Author : Lucas
# @Date   : 2020/12/30 5:13 pm
# @Last Modified by:  Lucas
# @Last Modified time:

import pandas as pd
import tushare as ts

ts.set_token('4680f3e9395b06311cf43c1627e3624da1e4d0b4e273caea0206c8ad')
pro = ts.pro_api()
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 100)
pd.set_option('display.max_columns', None)

# df = pro.fut_basic(exchange='CZCE', fut_type='2', fields='ts_code,symbol,name,list_date,delist_date')
# df = pro.fut_daily(ts_code='CU1811.CZCE', start_date='20180101', end_date='20181113')

df = pro.fut_daily(ts_code='CF.ZCE', start_date='20180307', end_date='20180312')
# print(df)
print(df.loc[:, ['pre_close', 'trade_date', 'close', 'open', 'high', 'low']])
