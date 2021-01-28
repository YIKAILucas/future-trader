# coding=utf-8

# @Author : Lucas
# @Date   : 2021/1/28 8:29 AM
# @Last Modified by:  Lucas
# @Last Modified time:
import datetime

import backtrader as bt
from backtrader_plotting import Bokeh

from backtest.data_feeder import DataFeederAdapter


class TestStrategy(bt.Strategy):
    params = (
        ('buydate', 21),
        ('holdtime', 6),
    )

    def next(self):
        if len(self.data) == self.p.buydate:
            self.buy(self.datas[0], size=None)

        if len(self.data) == self.p.buydate + self.p.holdtime:
            self.sell(self.datas[0], size=None)


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    cerebro.addstrategy(TestStrategy, buydate=3)
    future_data = bt.feeds.PandasData(
        dataname=DataFeederAdapter.get_tushare(),
        fromdate=datetime.datetime(2020, 6, 1),

        todate=datetime.datetime(2021, 1, 28),
        timeframe=bt.TimeFrame.Days,
        # dtformat=('%d-%m-%Y %H:%M'),
        # dtformat="%Y-%m-%d"
        # openinterest=-1,
    )
    cerebro.adddata(future_data)

    cerebro.run()

    b = Bokeh(style='bar', plot_mode='single')
    cerebro.plot(b)
