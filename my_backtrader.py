import backtrader as bt
import datetime
import pandas as pd
import numpy as np
import os, sys
from strategies import *

cerebro = bt.Cerebro()

# 给原始数据设置起止时间参数，并添加给Cerebro引擎
data = bt.feeds.YahooFinanceCSVData(
    dataname='TSLA.csv',
    fromdate=datetime.datetime(2016, 1, 1),
    todate=datetime.datetime(2017, 12, 25))
# 样本外数据的参数设置如下
# fromdate=datetime.datetime(2018, 1, 1),
# todate=datetime.datetime(2019, 12, 25))

cerebro.adddata(data)

# 给Cerebro引擎添加策略
cerebro.addstrategy(MyStrategy)

# 默认头寸大小
cerebro.addsizer(bt.sizers.SizerFix, stake=3)

if __name__ == '__main__':
    # 运行Cerebro引擎
    start_portfolio_value = cerebro.broker.getvalue()

    cerebro.run()

    end_portfolio_value = cerebro.broker.getvalue()
    pnl = end_portfolio_value - start_portfolio_value
    print('Starting Portfolio Value: %.2f' % start_portfolio_value)
    print('Final Portfolio Value: %.2f' % end_portfolio_value)
    print('PnL: %.2f' % pnl)
