import backtrader as bt

import config_reader
from backtest.StateMachine import BaseMachine

ConfigReader = config_reader.ConfigReader()


class Mydecorate(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            print("__call__", self.name)
            print()
            func(*args, **kwargs)

        return wrapper


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


def show_reason_and_mode(func):
    def wrapper(self):
        pre_state = self.signal
        func(self)
        state = self.signal
        if pre_state != state:
            if state is True:
                self.state_machine.strategy_model.to_rise()
            else:
                self.state_machine.strategy_model.to_normal()
            print(f'切换状态{pre_state}->{self.signal} 原因: {self.reason}')
        else:
            print(f'保持状态{self.signal}')

    return wrapper


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

        # TODO 初始状态机，考虑初始的位置放这里好不好
        self.state_machine = BaseMachine()
        self.s_model = self.state_machine.strategy_model
        print(self.s_model.state)
        # state_machine.strategy_model.to_rise()
        # print(state_machine.strategy_model.state)
        # 持仓信号
        self.signal = False
        self.reason = ''

    def change_state(self, state):
        def wrapper():
            if self.signal != state:
                self.signal = state
                print('改变状态')
            else:
                print('保持状态')

        return wrapper

    @show_reason_and_mode
    def choose_state(self):
        # 1. 布林线喇叭开口
        now_boll_gap = self.lines.top - self.lines.bot
        pre_boll_gap = self.lines.top[-10] - self.lines.bot[-10]
        if now_boll_gap >= 1.5 * pre_boll_gap:
            self.signal = True
            self.reason = '布林线喇叭开口'
            if self.s_model.is_rise() is False:
                self.s_model.to_rise()

        # 2. 高频触及上轨
        if self.dataclose > self.lines.top[0] and self.dataclose[-1] > self.lines.top[-1] and self.dataclose[-2] > \
                self.lines.top[-2]:
            self.signal = True
            self.reason = '高频触及上轨'
            if self.s_model.is_rise() is False:
                print('torise')
                self.s_model.to_rise()

        # 1. 跌破中轨
        if self.datalow < self.lines.mid[0]:
            self.signal = False
            self.reason = '跌破中轨'
            if self.s_model.is_normal() is False:
                self.s_model.to_normal()

        # 2. 跌幅超过3%
        # (现价-上一个交易日收盘价）/上一个交易日收盘价*100%
        scope = (self.dataclose - self.dataclose[-1]) / self.dataclose[-1]
        print(f'scope{scope}')
        if scope < -0.03:
            self.signal = False
            self.reason = '跌幅超过3'
            if self.s_model.is_normal() is False:
                self.s_model.to_normal()

        # 3. 布林线收口
        now_boll_gap = self.lines.top - self.lines.bot
        pre_boll_gap = self.lines.top[-5] - self.lines.bot[-5]
        if pre_boll_gap >= 1.5 * now_boll_gap:
            self.signal = False
            self.reason = '布林线收口'
            if self.s_model.is_normal() is False:
                self.s_model.to_normal()

        if self.down_in_10days():
            if self.s_model.is_fall() is False:
                print('进入fall')
                self.s_model.to_fall()
                print('关仓')
                self.close()
                print(self.position)
            else:
                print('已经是fall模式了')

    def down_in_10days(self) -> bool:
        count = 0
        for i in range(0, -10, -1):
            if self.datalow[i] <= self.lines.bot[i]:
                count += 1
        if count >= 3:
            return True
        else:
            return False

    def handle(self):
        # 'normal', 'rise', 'fall', 'shudder', 'asleep'
        if self.s_model.is_normal():
            if self.datalow <= self.lines.bot[0]:
                # 下轨买入
                self.order = self.buy(size=self.params.size)
            # 当天不会平仓
            if self.datahigh > self.lines.top[0]:
                # 上轨平仓
                self.order = self.close()
        elif self.s_model.is_rise():
            self.order = self.buy(size=self.params.size)
            """
            下跌状态策略
            """
        elif self.s_model.is_fall():
            # self.order = self.close()
            self.order = self.sell(size=1)

        elif self.s_model.is_shudder():
            pass
        elif self.s_model.is_asleep():
            pass

    def next(self):
        print(f'每天现金{self.broker.getcash()}  每天收盘{self.dataclose[0]}  每天净值{self.broker.getvalue()}')
        self.choose_state()

        self.handle()
