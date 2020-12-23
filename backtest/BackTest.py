from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime
import datetime as dt
import os
import sys

import backtrader as bt
import pandas as pd
from pyecharts.charts import Line, Bar

import config_reader
from strategies import Bolling_2_0


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


def show_echarts(data, v, title, plot_type='line', zoom=False):
    att = data.index
    try:
        attr = att.strftime('%Y%m%d')
    except:
        attr = att
    if plot_type == 'line':
        p = Line(title)
        p.add_xaxis('', attr,
                    is_symbol_show=False, line_width=2,
                    is_datazoom_show=zoom, is_splitline_show=True)
        p.add_yaxis(list(data[v].round(2)))
    else:
        p = Bar(title)
        p.add('', attr, [int(i * 1000) / 10 for i in list(data[v])],
              is_label_show=True,
              is_datazoom_show=zoom, is_splitline_show=True)
    return p


def run_Backtest(fromdate=None, todate=None):
    # 注意+-，这里最后的pandas要符合backtrader的要求的格式
    dataframe = pd.read_csv('./backtest/boll.csv', encoding='utf-8_sig', parse_dates=True)
    dataframe.dropna()
    trans_date = [dmy2ymd(d) for d in dataframe['日期']]

    dataframe['date'] = trans_date
    print(dataframe.shape)
    dataframe['openinterest'] = 0
    dataframe['volume'] = [0] * dataframe.shape[0]

    dataframe.rename(columns={'开盘价(元)': 'open', '收盘价(元)': 'close', '最高价(元)': 'high', '最低价(元)': 'low'},
                     inplace=True)

    dataframe = dataframe[['date', 'open', 'close', 'high', 'low', 'volume']]

    dataframe.to_csv('cdata.csv', index=False)

    dataframe = pd.read_csv('cdata.csv', parse_dates=True, index_col=[0])
    print(dataframe.info())
    print(dataframe.describe())

    print(dataframe.head())

    print(dataframe)
    data1 = bt.feeds.PandasData(
        dataname=dataframe,
        fromdate=datetime.datetime(fromdate[0], fromdate[1], fromdate[2]),
        todate=datetime.datetime(todate[0], todate[1], todate[2]),
        # volume=-1,
        timeframe=bt.TimeFrame.Days
        # openinterest=-1,
    )
    # data1 = bt.feeds.GenericCSVData(
    #     dataname="./cdata.csv",
    #     # datetime=0,
    #     # timeframe=bt.TimeFrame.Days,
    #     # compression=1,
    #     fromdate=datetime.datetime(fromdate1[0], fromdate1[1], fromdate1[2]),
    #     todate=datetime.datetime(todate1[0], todate1[1], todate1[2]),
    #     open=1,
    #     close=2,
    #     high=3,
    #     low=4,
    #     dtformat="%Y-%m-%d"
    #     # volume=-1,
    #     # openinterest=-1,
    # )
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'cdata.csv')

    # 是否当天交易，当天交易->未来函数
    # 默认false
    cerebro = bt.Cerebro(cheat_on_open=False)

    # cerebro.addstrategy(TestStrategy)
    # cerebro.addstrategy(BollingStrategy_1_0)

    cerebro.addstrategy(Bolling_2_0)

    cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.TimeReturn)
    # cerebro.addobserver(bt.observers.Benchmark)
    # cerebro.addobserver(bt.observers.TimeReturn)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Days)

    cerebro.adddata(data1)
    cash = ConfigReader.cash
    cerebro.broker.setcash(cash)

    cerebro.broker.setcommission(commission=0.0, commtype=bt.CommInfoBase.COMM_FIXED, automargin=0.35, mult=5)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    results = cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # Plot the result
    portvalue = cerebro.broker.getvalue()

    pnl = portvalue - cash
    start = results[0]
    print('夏普比率:', start.analyzers.SharpeRatio.get_analysis())
    print('回撤指标:', start.analyzers.DW.get_analysis())
    print(f'净收益: {round(pnl, 2)}')

    # ddf = get_data('300002.SZ', '20050101')
    # data = Addmoredata(dataname=ddf)
    # df00, df0, df1, df2, df3, df4 = bt,(BollingStrategy, data, startcash=cash, commission=0)

    # show_echarts(df3, 'year_rate', '年化收益%', plot_type='bar')

    cerebro.plot(
        # style = 'candlestick',
    )


if __name__ == '__main__':
    period_date = {
        'shudder': [((2015, 3, 15), (2018, 3, 15)), ((2011, 8, 29), (2013, 3, 14))],
        'rise': [((2008, 12, 1), (2010, 12, 1)), ((2018, 5, 10), (2018, 6, 1)),
                 ((2016, 4, 1), (2016, 7, 13))],
        'fall': [((2011, 3, 14), (2011, 8, 12)), ((2014, 3, 20), (2016, 4, 1))]
    }
    fromdate1 = period_date['rise'][0][0]
    todate1 = period_date['rise'][0][1]
    fromdate2 = period_date['shudder'][1][0]
    todate2 = period_date['shudder'][1][1]

    ConfigReader = config_reader.ConfigReader()
    print(ConfigReader.cash)

    run_Backtest(fromdate1, todate1)
    # run_Backtest(fromdate2, todate2)
    # time.sleep(2)
    # run_Backtest(fromdate2, todate2)

# t1 = threading.Thread(target=run_Backtest, args=(fromdate1, todate1))
# t2 = threading.Thread(target=run_Backtest, args=(fromdate2, todate2))
# t1.start()
# t2.start()
