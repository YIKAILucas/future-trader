from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime
import os
import sys

import backtrader as bt
from pyecharts import options as opts
from pyecharts.charts import Kline
from rich import print

import config_reader
from backtest import strategies
from backtest.data_feeder import DataFeederAdapter
from strategies import MACD_Strategy, MA_1_0, Bolling_2_0


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


def run_backtest(dataframe, strategy=[], fromdate=None, todate=None):
    # dataframe要符合backtrader的要求的格式 open,close,high,low,volume
    future_data = bt.feeds.PandasData(
        dataname=dataframe,
        fromdate=datetime.datetime(fromdate[0], fromdate[1], fromdate[2]),
        todate=datetime.datetime(todate[0], todate[1], todate[2]),
        timeframe=bt.TimeFrame.Days,
        # dtformat=('%d-%m-%Y %H:%M'),
        # dtformat="%Y-%m-%d"
        # openinterest=-1,
    )
    future_data2 = bt.feeds.PandasData(
        dataname=dataframe,
        fromdate=datetime.datetime(2014, 9, 1),
        todate=datetime.datetime(2018, 9, 1),
        timeframe=bt.TimeFrame.Days,
        # dtformat=('%d-%m-%Y %H:%M'),
        # dtformat="%Y-%m-%d"
        # openinterest=-1,
    )

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'cdata.csv')

    # 是否当天交易, 默认false
    cerebro = bt.Cerebro(cheat_on_open=False)
    for s in strategy:
        cerebro.addstrategy(s)
    # cerebro.addstrategy(strategy[0])
    cerebro.addobserver(bt.observers.DrawDown)
    # cerebro.addobserver(bt.observers.Benchmark)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Days)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
    # 添加结果回写
    cerebro.addwriter(bt.WriterFile, csv=True, out='log.csv')

    cerebro.adddata(future_data)
    # cerebro.adddata(future_data2)
    cash = ConfigReader.init_cash
    cerebro.broker.setcash(cash)
    # commision手续费
    # automargin 保证金比例，按一手 0.07 * 5 = 0.35
    # mult 单手吨数
    cerebro.broker.setcommission(stocklike=False, commission=5, commtype=bt.CommInfoBase.COMM_FIXED, automargin=0.35,
                                 mult=5)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    # TODO 后续用于pyecharts
    protfolio_stats = results[0].analyzers.getbyname('PyFolio')
    returns, positions, transactions, gross_level = protfolio_stats.get_pf_items()
    print(f'returns{returns}')
    print(f'transactions{transactions}')
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue(lever=True))
    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - cash
    start = results[0]
    print('夏普比率:', start.analyzers.SharpeRatio.get_analysis())
    print('回撤指标:', start.analyzers.DW.get_analysis())
    print(f'净收益: {round(pnl, 2)}')

    strategies.show_pyecharts(MACD_Strategy.xlist, MACD_Strategy.ylist, MACD_Strategy.y2list, MACD_Strategy.y3list,
                              MACD_Strategy.y4list)
    print(MACD_Strategy.xlist[0:10])
    print(MACD_Strategy.y4list[0:10])

    # 此处修改了源码
    figs = cerebro.plot(show=False)
    # 保存结果图片
    save_path = 'generated/'
    for index, fig in enumerate(figs):
        for f in fig:
            filepath = f'{save_path}{strategy[index].__name__}-->{str(datetime.datetime.today())}.png'
            f.set_size_inches(19.2, 10.8)
            f.savefig(filepath)
            # oss_uploader.upload_pic(filepath)


if __name__ == '__main__':
    period_date = {
        'shudder': [((2015, 3, 15), (2018, 3, 15)), ((2011, 8, 29), (2013, 3, 14))],
        'rise': [((2008, 12, 1), (2010, 12, 1)), ((2018, 5, 10), (2018, 6, 1)),
                 ((2016, 4, 1), (2016, 7, 13))],
        'fall': [((2011, 3, 14), (2011, 8, 12)), ((2014, 3, 20), (2016, 4, 1))],
        'total': [((2004, 4, 1), (2020, 1, 1))]
    }
    fromdate1 = period_date['rise'][0][0]
    todate1 = period_date['rise'][0][1]
    fromdate2 = period_date['fall'][1][0]
    todate2 = period_date['fall'][1][1]
    fromdate3 = period_date['shudder'][1][0]
    todate3 = period_date['shudder'][1][1]
    total1 = period_date['total'][0][0]
    total2 = period_date['total'][0][1]

    fromdate4 = period_date['fall'][0][0]
    todate4 = period_date['fall'][0][1]
    ConfigReader = config_reader.ConfigReader()

    dataframe_online = DataFeederAdapter.get_tushare()
    # dataframe_csv = DataFeederAdapter.csv_data_feed()
    # print(dataframe_online)
    # print('---------')
    # print(dataframe_csv)

    real_start = (2020, 9, 1)
    today = datetime.datetime.today().date()
    date_list = str(today).split('-')

    real_end = tuple(int(i) for i in date_list)

    fuck_start = (2014, 9, 5)
    fuck_end = (2018, 1, 7)
    # TODO 通过配置文件选择策略和周期
    # run_Backtest(ConfigReader.init_choose_strategy, fromdate2, todate2)
    strategy_list = [MA_1_0, MACD_Strategy, Bolling_2_0]
    # run_backtest(dataframe_online, strategy_list, real_start, real_end)
    period_list = []
    period_list.append((real_start, real_end))
    # period_list.append((fuck_start, fuck_end))
    # time.sleep(5)
    for p in period_list:
        run_backtest(dataframe_online, strategy_list, p[0], p[1])
