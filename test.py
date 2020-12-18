from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime
import datetime as dt
import os
import sys
import time

import backtrader as bt
import pandas as pd
# Create a Strategy
from pyecharts.charts import Line, Bar


class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        # To keep track of pending orders
        self.order = None

    def notify(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        # Write down: no pending order
        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] < self.dataclose[-1]:
                # current close less than previous close

                if self.dataclose[-1] < self.dataclose[-2]:
                    # previous close less than the previous close

                    # BUY, BUY, BUY!!! (with default parameters)
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])

                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy()

        else:

            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


class BollingStrategy(bt.Strategy):
    # 自定义参数，每次买入1手
    params = (('size', 1), ('maperiod', 20), ('printlog', True))

    def __init__(self):
        self.dataclose = self.datas[0].close

        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.order = None
        self.buyprice = None
        self.buycomm = None
        ##使用自带的indicators中自带的函数计算出支撑线和压力线，period设置周期，默认是20
        self.lines.top = bt.indicators.BollingerBands(self.datas[0], period=20).top
        self.lines.mid = bt.indicators.BollingerBands(self.datas[0], period=20).mid
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=20)
        # self.lines.ma = self.lines.ma
        self.lines.bot = bt.indicators.BollingerBands(self.datas[0], period=20).bot
        # 指标
        # bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
        #                                     subplot=True)
        # bt.indicators.StochasticSlow(self.datas[0])
        # bt.indicators.MACDHisto(self.datas[0])
        # rsi = bt.indicators.RSI(self.datas[0])
        # bt.indicators.SmoothedMovingAverage(rsi, period=10)
        # bt.indicators.ATR(self.datas[0], plot=False)

        # bt.indicators.MaxDrawDown(self.datas[0])
        # self.lines.bot = bt.indicators.

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))
            print(f'当前持仓{self.getposition().size}')
        # print(f'self.lines.mid->{self.lines.mid[0]}---self.sma->{self.sma[0]}')

    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.maperiod, self.broker.getvalue()), doprint=True)

    def notify_order(self, order):
        print(f'订单去向')

    def notify(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next_open(self):
        print(f'每天现金{self.broker.getcash()}')
        print(f'每天收盘{self.dataclose[0]}')
        print(f'每天净值{self.broker.getvalue()}')
        # 没有持仓
        if not self.position:
            if self.datalow <= self.lines.bot[0]:
                # 执行买入
                self.order = self.buy(size=self.params.size)
                # self.order = self.buy(price=self.dataclose, size=self.params.size)
                # return
        # 有持仓
        else:
            if self.datalow <= self.lines.bot[0]:
                # 执行买入
                self.order = self.buy(size=self.params.size)
                # self.order = self.buy(price=self.dataclose,size=self.params.size)
                return

            if self.datahigh > self.lines.mid[0] or self.datahigh > self.lines.top[0]:
                # 执行卖出
                # self.order = self.sell(size=self.params.size)
                # 全部平仓
                self.order = self.close()

    def next(self):
        print(f'每天现金{self.broker.getcash()}  每天收盘{self.dataclose[0]}  每天净值{self.broker.getvalue()}')
        # 没有持仓
        if not self.position:
            if self.datalow <= self.lines.bot[0]:
                # 执行买入
                self.order = self.buy(size=self.params.size)
                # self.order = self.buy(price=self.dataclose, size=self.params.size)
                # return
        # 有持仓
        else:
            if self.datalow <= self.lines.bot[0]:
                # 执行买入
                self.order = self.buy(size=self.params.size)
                # self.order = self.buy(price=self.dataclose,size=self.params.size)
                return

            if self.datahigh > self.lines.mid[0] or self.datahigh > self.lines.top[0]:
                # 执行卖出
                # self.order = self.sell(size=self.params.size)
                # 全部平仓
                self.order = self.close()


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
    dataframe = pd.read_csv('boll.csv', encoding='utf-8_sig', parse_dates=True)
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
    datapath = os.path.join(modpath, './cdata.csv')

    # 是否当天交易，当天交易->未来函数
    cerebro = bt.Cerebro(cheat_on_open=True)


    # cerebro.addstrategy(TestStrategy)
    cerebro.addstrategy(BollingStrategy)
    cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.TimeReturn)
    # cerebro.addobserver(bt.observers.Benchmark)
    # cerebro.addobserver(bt.observers.TimeReturn)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Days)


    cerebro.adddata(data1)
    cash = 50000.0
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
    # 打印结果
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


import threading

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
    # run_Backtest(fromdate2, todate2)
    run_Backtest(fromdate2, todate2)
    # time.sleep(2)
    # run_Backtest(fromdate2, todate2)

# t1 = threading.Thread(target=run_Backtest, args=(fromdate1, todate1))
    # t2 = threading.Thread(target=run_Backtest, args=(fromdate2, todate2))
    # t1.start()
    # t2.start()
