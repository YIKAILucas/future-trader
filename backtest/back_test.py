from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime
import datetime as dt
import os
import sys

import backtrader as bt
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar

import config_reader
from backtest import strategies
from backtest.data_feeder import DataFeederAdapter
from path import ROOT_DIR
from strategies import MACD_Strategy, MA_1_0


def kline(data, date):
    kline = (
        Kline()
            .add_xaxis(xaxis_data=date)
            .add_yaxis(
            series_name="",
            y_axis=data["close"],
            itemstyle_opts=opts.ItemStyleOpts(
                color="#ef232a",
                color0="#14b143",
                border_color="#ef232a",
                border_color0="#14b143",
            ),
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值"),
                    opts.MarkPointItem(type_="min", name="最小值"),
                ]
            ),
            markline_opts=opts.MarkLineOpts(
                label_opts=opts.LabelOpts(
                    position="middle", color="blue", font_size=15
                ),
                data=split_data_part(),
                symbol=["circle", "none"],
            ),
        )
            .set_series_opts(
            markarea_opts=opts.MarkAreaOpts(is_silent=True, data=split_data_part())
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="K线周期图表", pos_left="0"),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,
                boundary_gap=False,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
                split_number=20,
                min_="dataMin",
                max_="dataMax",
            ),
            yaxis_opts=opts.AxisOpts(
                is_scale=True, splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="line"),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=False, type_="inside", xaxis_index=[0, 0], range_end=100
                ),
                opts.DataZoomOpts(
                    is_show=True, xaxis_index=[0, 1], pos_top="97%", range_end=100
                ),
                opts.DataZoomOpts(is_show=False, xaxis_index=[0, 2], range_end=100),
            ],
            # 三个图的 axis 连在一块
            # axispointer_opts=opts.AxisPointerOpts(
            #     is_show=True,
            #     link=[{"xAxisIndex": "all"}],
            #     label=opts.LabelOpts(background_color="#777"),
            # ),
        )
    )


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

def data_adapter():
    pass


def run_Backtest(strategy=None, fromdate=None, todate=None):
    # 注意+-，这里最后的pandas要符合backtrader的要求的格式
    # dataframe = DataFeederAdapter.csv_data_feed()

    dataframe= DataFeederAdapter.get_tushare()
    data1 = bt.feeds.PandasData(
        dataname=dataframe,
        fromdate=datetime.datetime(fromdate[0], fromdate[1], fromdate[2]),
        todate=datetime.datetime(todate[0], todate[1], todate[2]),
        timeframe=bt.TimeFrame.Days
        # openinterest=-1,
    )

    data1 = bt.feeds.PandasData(
        dataname=dataframe,
        fromdate=datetime.datetime(year=2015, month=8, day=4),
        todate=datetime.datetime(2018, 10, 4),
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

    cerebro.addstrategy(strategy)

    cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.TimeReturn)
    # cerebro.addobserver(bt.observers.Benchmark)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Days)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

    cerebro.adddata(data1)
    cash = ConfigReader.init_cash
    cerebro.broker.setcash(cash)
    # commision手续费
    # automargin 保证金比例，按一手 0.07 * 5 = 0.35
    # mult 单手吨数
    cerebro.broker.setcommission(commission=5, commtype=bt.CommInfoBase.COMM_FIXED, automargin=0.35, mult=5)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
    cerebro.addwriter(bt.WriterFile, csv=True,out='log.csv')

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    results = cerebro.run()
    protfolio_stats=results[0].analyzers.getbyname('PyFolio')
    returns,positions,transactions,gross_level=protfolio_stats.get_pf_items()
    print(f'returns{returns}')
    print(f'transactions{transactions}')
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # Plot the result
    portvalue = cerebro.broker.getvalue()

    pnl = portvalue - cash
    start = results[0]
    print('夏普比率:', start.analyzers.SharpeRatio.get_analysis())
    print('回撤指标:', start.analyzers.DW.get_analysis())
    print(f'净收益: {round(pnl, 2)}')

    strategies.test_py(MACD_Strategy.xlist,MACD_Strategy.ylist,MACD_Strategy.y2list,MACD_Strategy.y3list,MACD_Strategy.y4list)
    # print(MACD_Strategy.xlist[0])
    # print(MACD_Strategy.ylist[0])
    print(MACD_Strategy.xlist[0:10])
    print(MACD_Strategy.y4list[0:10])

# ddf = get_data('300002.SZ', '20050101')
    # data = Addmoredata(dataname=ddf)
    # df00, df0, df1, df2, df3, df4 = bt,(BollingStrategy, data, startcash=cash, commission=0)

    # show_echarts(df3, 'year_rate', '年化收益%', plot_type='bar')

    cerebro.plot()
    # print(dataframe.head())
    # kline(dataframe,trans_date)


if __name__ == '__main__':
    period_date = {
        'shudder': [((2015, 3, 15), (2018, 3, 15)), ((2011, 8, 29), (2013, 3, 14))],
        'rise': [((2008, 12, 1), (2010, 12, 1)), ((2018, 5, 10), (2018, 6, 1)),
                 ((2016, 4, 1), (2016, 7, 13))],
        'fall': [((2011, 3, 14), (2011, 8, 12)), ((2014, 3, 20), (2016, 4, 1))],
        'total': [((2004, 4, 1), (2020, 1, 1))]
    }
    fromdate1 = period_date['rise'][1][0]
    todate1 = period_date['rise'][1][1]
    fromdate2 = period_date['fall'][1][0]
    todate2 = period_date['fall'][1][1]
    fromdate3 = period_date['shudder'][1][0]
    todate3 = period_date['shudder'][1][1]
    total1 = period_date['total'][0][0]
    total2 = period_date['total'][0][1]

    fromdate4 = period_date['fall'][0][0]
    todate4 = period_date['fall'][0][1]
    ConfigReader = config_reader.ConfigReader()

    # run_Backtest(ConfigReader.init_choose_strategy, fromdate2, todate2)
    run_Backtest(MACD_Strategy, fromdate1, todate1)
    # run_Backtest(MACD_Strategy)
    # run_Backtest(MA_1_0, total1, total2)
    # run_Backtest(MA_1_0, fromdate1, todate1)
    # run_Backtest(Bolling_2_0, fromdate2, todate2)
    # run_Backtest(MACD_Strategy,fromdate1, todate1)
    # time.sleep(2)
    # run_Backtest(fromdate2, todate2)

# t1 = threading.Thread(target=run_Backtest, args=(fromdate1, todate1))
# t2 = threading.Thread(target=run_Backtest, args=(fromdate2, todate2))
# t1.start()
# t2.start()
