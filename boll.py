from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import random
from pprint import pprint

import matplotlib
import numpy
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib import pyplot as plt
from pyecharts.faker import Faker
from pyecharts.globals import ThemeType
from pyecharts.render import make_snapshot, snapshot

import backtrader as bt

window_size = 20
open_price = '开盘价(元)'
highest = '最高价(元)'
lowest = '最低价(元)'
close_price = '收盘价(元)'
balance = '结算价'
turnover = '成交额(百万)'
volume = '成交量'
position = '持仓量'

import datetime as dt
from pyecharts.charts import Line, Scatter, EffectScatter, Bar
import pyecharts.options as opts


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


def dec_buy(low, high, down, mid):
    if low < down:
        return 1
    return 0


def dec_sell(data: pd.DataFrame, low, high, down, mid):
    if high > mid and data['买'] == 0:
        return -1
    return 0


# flag: buy,sell
# prev: 昨日成本 dn：当天低轨线数值 pos：当天多单数
def cal_cost(buy, sell, prev_cost, dn, pos):
    if buy == 1:
        # 买进
        return prev_cost + dn, pos + 1
    if sell == -1:
        # 平仓
        return 0, 0
    else:
        return prev_cost, pos


col_n = ['买', '平', lowest, 'MA', 'DN', 'cost', 'newcost', 'position', 'profit']


def trs(a):
    if a['calculate'] != 0 and a['平'] == -1:
        return -1
    else:
        return 0


def calculate_profit(data: pd.DataFrame):
    data['买'] = data.apply(lambda x: dec_buy(x[lowest], x[highest], x['DN'], x['MA']), axis=1)
    data['平'] = data.apply(lambda x: dec_sell(x, x[lowest], x[highest], x['DN'], x['MA']), axis=1)
    data['cost'] = pd.Series([0] * data.shape[0], name='cost')

    temp = data['cost'].tolist()
    sell_list = data['平'].tolist()
    dn = data['DN'].tolist()
    buy = data['买'].tolist()
    position = [0] * len(temp)
    for index, t in enumerate(temp):
        if index == 0:
            continue
        new, pos = cal_cost(buy[index], sell_list[index], temp[index - 1], dn[index], position[index - 1])
        temp[index] = new
        position[index] = pos

    data['newcost'] = temp
    data['position'] = position
    data['calculate'] = data['position'].shift(1)

    # data['平'].apply(lambda x: x['平']=0 if x['calculate']==0 else x['平']=x['平'],axis=1)
    data['平'] = data.apply(trs, axis=1)

    data['profit'] = np.divide(data[close_price] * data['position'], data['newcost'] * 0.07) - 1
    # data['profit'] = np.divide(data[close_price] * data['position'] - data['newcost'] * 0.07, data['newcost'] * 0.07)

    # print(pd.DataFrame(data, columns=col_n)[150:200])
    # print(data['profit'].mean())
    # print(data['newcost'].max())
    # print(data['position'].max())
    display_plot(data)
    data.drop(['diff', 'sum', 'calculate', 'cost'], axis=1, inplace=True)
    data.rename(columns={'newcost': 'cost'}, inplace=True)
    data.to_csv("backtest/KTick.csv", encoding='utf-8')
    # test_out = pd.read_excel('boll.xlsx',index_col=[3])
    # print(test_out.head())

    print(f"平仓总数：{abs(data['平'].sum())}")
    print(f"买进总数：{abs(data['买'].sum())}")


def number_trunc(num):
    ceiling_num = 10 ** (len(str(num)) - 1)

    return np.ceil(np.divide(num, ceiling_num))


def str_new_line(stri: str) -> str:
    return np.round(stri.value, 2)


def display_plot(data: pd.DataFrame):
    # TODO 日期转换
    # trans_date = pd.to_datetime(data['日期'], format='%Y-%m-%d')
    # print(trans_date.values)
    trans_date = [dmy2ymd(d) for d in data['日期']]
    # print(trans_date)
    line_ma = Line() \
        .add_xaxis(trans_date) \
        .add_yaxis('MA', data['MA'], color='RGB(237,125,49)') \
        .add_yaxis('UP', data['UP'], color='RGB(165,165,165)') \
        .add_yaxis('DN', data['DN'], color='RGB(255,192,0)') \
        .add_yaxis('收盘价', data[close_price], color='RGB(91,155,213)') \
        .set_global_opts(title_opts=opts.TitleOpts(title='Bolling')) \
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False),
                         linestyle_opts=opts.LineStyleOpts(width=1.6, curve=2))
    # 布尔索引 remove成本为0，没有持仓的数据
    new_data = data.drop(index=data['newcost'][data['newcost'] == 0].index)

    data["returns"] = np.log(data[close_price] / data[close_price].shift(1))
    # data["strategy"] = data["signal"].shift(1) * data["returns"]

    # df[(800 < df["Count_AnimalName"]) & (df["Count_AnimalName"] < 1000)]
    new_data.to_csv('test.csv', encoding='utf-8_sig')

    # return
    # 分位数
    ll = range(2, 11, 2)
    ll = np.dot(ll, 0.1)

    # max_cost = new_data['newcost'].max()
    print(ll)
    # index_max_occ = new_data[balance].idxmax()
    #
    # data.
    # max_occ = new_data.iloc(index_max_occ)

    # yy = number_trunc(max_cost)
    # print(max_occ, yy)
    new_data['资金占用'] = np.round(new_data[balance] * new_data['position'] * 5 * 0.07)
    li = []
    li.append(new_data['资金占用'].quantile(i) for i in ll)
    print(li)
    # print(new_data['资金占用'].quantile(1))
    # new_data['资金占用'].quantile()

    # print(data[data['newcost']==0])
    trans_date = [dmy2ymd(d) for d in new_data['日期']]
    line_occ = EffectScatter(init_opts=opts.InitOpts(theme=ThemeType.WALDEN)) \
        .add_xaxis(trans_date) \
        .add_yaxis('资金占用',
                   new_data['资金占用'],
                   symbol_size=3, color='RGB(237,125,49)') \
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False)) \
        .set_global_opts(title_opts=opts.TitleOpts(title='资金占用'))

    line_position = Line() \
        .add_xaxis(trans_date) \
        .add_yaxis('持仓量', data['position'], is_smooth=True) \
        .set_global_opts(title_opts=opts.TitleOpts(title='持仓手数')) \
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False),
                         linestyle_opts=opts.LineStyleOpts(width=1.6, curve=2)) \
        .render('position.html')

    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add_xaxis(trans_date)
            .add_yaxis("持仓量", data['position'], stack="stack1", category_gap="50%")
            .set_series_opts(
            label_opts=opts.LabelOpts(
                position="right",
            )
        )
            .render("stack_bar_percent.html")
    )

    # c = (Bar()
    #      .add_xaxis(trans_date)
    #      .add_yaxis("商家B", new_data['position'], stack="stack1")
    #      .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    #      .set_global_opts(title_opts=opts.TitleOpts(title="Bar-堆叠数据（部分）"))
    #      .render("bar_stack1.html"))
    # Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT)) \
    #     .add_xaxis(trans_date) \
    #     .add_yaxis('持仓量', new_data['position']) \
    #     .set_global_opts(title_opts=opts.TitleOpts(title='持仓手数')) \
    #     .set_series_opts(label_opts=opts.LabelOpts(is_show=True)).render('bar.html')

    # new_data=data.dropna(subset=['profit'])
    # data.dropna(subset=['profit'], inplace=True)
    # new_data = data.drop(index=data['newcost'][data['newcost'] == 0].index)
    trans_date = [dmy2ymd(d) for d in new_data['日期']]
    line_profit = Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, bg_color='rgba(255,255,255,1)')) \
        .add_xaxis(trans_date) \
        .add_yaxis('profit', new_data['profit'],
                   markpoint_opts=opts.MarkPointOpts(
                       label_opts=opts.LabelOpts(is_show=False,
                                                 color='auto',
                                                 ),
                       data=[opts.MarkPointItem(
                           type_='max',
                           name='最大值',
                           symbol_size=[10, 10],
                           symbol='circle',
                           # coord=maxAnd,
                       ), opts.MarkPointItem(
                           type_='min',
                           name='最小值',
                           symbol_size=[10, 10],
                           symbol='circle',

                           # coord=[100, 20],
                       )
                       ]

                   ),
                   label_opts=opts.LabelOpts(position="inside", color="RGB(237,125,49)", is_show=False)) \
        .set_global_opts(title_opts=opts.TitleOpts(title='收益率')) \
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))

    line_ma.render('ma.html')
    line_profit.render('profit.html')
    # make_snapshot(snapshot, line_ma.render(), "Funnel.png")


if __name__ == '__main__':
    data = pd.read_excel('zhengmian.xlsx')
    # remove null
    data = data.dropna(subset=['日期'])

    data['MA'] = data[close_price].rolling(window=window_size, min_periods=1, axis=0).mean()

    # C-MA的平方
    data['diff'] = np.square(data[close_price] - data['MA'])
    # MD= data.apply(lambda x: x[close_price] + 2 * x['col2'], axis=1)
    data['sum'] = data['diff'].rolling(window=window_size, min_periods=1, axis=0).sum()
    # FIXME 自写
    # data['STD'] = np.sqrt(data['diff'].rolling(window=window, min_periods=1, axis=0).sum() / window)
    data['std'] = data[close_price].rolling(window=window_size, min_periods=1).std(ddof=0)
    data['UP'] = data['MA'] + 2 * data['std']
    data['DN'] = data['MA'] - 2 * data['std']

    print(data.loc[20:40, ['diff', 'sum', 'std']])

    # remove 结算价为0
    data = data[data[balance] > 0]
    calculate_profit(data)

    cerebro = bt.Cerebro()

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.broker.setcash(100000.0)

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
