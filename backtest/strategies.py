import backtrader as bt

import config_reader

ConfigReader = config_reader.ConfigReader()


class TripleFallenStrategy(bt.Strategy):
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


class BollingStrategy_1_0(bt.Strategy):
    # 自定义参数，每次买入1手
    params = (('size', ConfigReader.size), ('maperiod', ConfigReader.moving), ('printlog', True))

    def __init__(self):
        self.dataclose = self.datas[0].close

        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.order = None
        self.buyprice = None
        self.buycomm = None
        ##使用自带的indicators中自带的函数计算出支撑线和压力线，period设置周期，默认是20
        self.lines.top = bt.indicators.BollingerBands(self.datas[0], period=self.params.maperiod).top
        self.lines.mid = bt.indicators.BollingerBands(self.datas[0], period=self.params.maperiod).mid
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)
        # self.lines.ma = self.lines.ma
        self.lines.bot = bt.indicators.BollingerBands(self.datas[0], period=self.params.maperiod).bot
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
                pass
                # 执行卖出
                # self.order = self.sell(size=self.params.size)
                # 全部平仓
                self.order = self.close()


class Bolling_2_0(BollingStrategy_1_0):
    def __init__(self):
        super().__init__()
        # 持仓信号
        self.signal = False

    def normal_mode(self):
        if self.datalow <= self.lines.bot[0]:
            # 下轨买入
            self.order = self.buy(size=self.params.size)
            # 当天不会平仓
            return
        if self.datahigh > self.lines.top[0]:
            # 上轨平仓
            self.order = self.close()
            return

    def hold_mode(self):
        self.order = self.buy(size=self.params.size)
        pass

    def choose_mode(self):
        # TODO 喇叭口
        # if
        # 高频触及上轨
        if self.dataclose > self.lines.top[0] and self.dataclose[-1] > self.lines.top[-1] and self.dataclose[-2] > \
                self.lines.top[-2]:
            self.signal = True
        # 判断是否结束持仓模式
        # 1. 跌破中轨
        if self.datalow < self.lines.mid[0]:
            self.signal = False
            # self.order = self.close()

        # 2. 跌幅超过10%
        # (现价-上一个交易日收盘价）/上一个交易日收盘价*100%
        scope = (self.dataclose - self.dataclose[-1]) / self.dataclose[-1]
        print(f'scope{scope}')
        if scope < -0.01:
            print('test')
            self.signal = False
            # self.order = self.close()

    def next(self):
        print(f'每天现金{self.broker.getcash()}  每天收盘{self.dataclose[0]}  每天净值{self.broker.getvalue()}')

        # 持仓模式
        if self.signal:
            self.hold_mode()
        else:
            self.normal_mode()
