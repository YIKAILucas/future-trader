from abc import abstractmethod

import backtrader as bt

import config_reader
from backtest.Mydecorator import show_reason_and_mode
from backtest.StateMachine import BaseMachine

ConfigReader = config_reader.ConfigReader()


class BaseStrategy(bt.Strategy):
    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))
            print(f'当前持仓{self.getposition().size}')
        # print(f'self.lines.mid->{self.lines.mid[0]}---self.sma->{self.sma[0]}')

    def stop(self):
        pass

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

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

    def init_model(self):
        self.state_machine = BaseMachine()
        self.s_model = self.state_machine.strategy_model
        self.reason = ''
        print(self.s_model.state)

    def next(self):
        # self.s_model.count = 0
        print(f'每天现金{self.broker.getcash()}  每天收盘{self.dataclose[0]}  每天净值{self.broker.getvalue()}')
        self.choose_state()
        self.handle()

    @abstractmethod
    def choose_state(self):
        pass

    @abstractmethod
    def handle(self):
        pass

    def state_enter_callback(self):
        print(f'进入{self.s_model.state} 原因->{self.reason}')
        if self.s_model.state == 'fall' or self.prev == 'fall':
            self.my_close()

    def state_exit_callback(self):
        print(f'退出{self.s_model.state}', end=' ')
        self.prev = self.s_model.state


class TripleFallenStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()

    def notify(self, order):
        super().__init__()

    def handle(self):
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

    def choose_state(self):
        pass


class BollingStrategy_1_0(BaseStrategy):
    # 自定义参数，每次买入1手
    params = (('size', ConfigReader.size), ('maperiod', ConfigReader.moving), ('printlog', True))

    def __init__(self):
        super().__init__()
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.order = None
        self.buyprice = None
        self.buycomm = None
        ##使用自带的indicators中自带的函数计算出支撑线和压力线，period设置周期，默认是20
        self.lines.top = bt.indicators.BollingerBands(self.datas[0], period=self.p.maperiod).top
        self.lines.mid = bt.indicators.BollingerBands(self.datas[0], period=self.p.maperiod).mid
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.p.maperiod)
        # self.lines.ma = self.lines.ma
        self.lines.bot = bt.indicators.BollingerBands(self.datas[0], period=self.p.maperiod).bot
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

    def handle(self):
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

    def choose_state(self):
        pass


class Bolling_2_0(BollingStrategy_1_0):
    def my_close(self):
        print('关仓')
        self.close()

    def __init__(self):
        super().__init__()
        self.change_count = 0
        # 初始状态机
        self.init_model()
        # 持仓信号
        self.reason = ''

    # def change_state(self, state):
    #     def wrapper():
    #         if self.signal != state:
    #             self.signal = state
    #             print('改变状态')
    #         else:
    #             print('保持状态')
    #
    #     return wrapper
    @show_reason_and_mode
    def choose_state(self):
        # 1. 布林线喇叭开口
        now_boll_gap = self.lines.top - self.lines.bot
        pre_boll_gap = self.lines.top[-10] - self.lines.bot[-10]
        if now_boll_gap >= 1.5 * pre_boll_gap:
            self.reason = '布林线喇叭开口'
            if self.s_model.is_rise() is False:
                self.s_model.to_rise(bt=self)

        # 2. 高频触及上轨
        if self.dataclose > self.lines.top[0] and self.dataclose[-1] > self.lines.top[-1] and self.dataclose[-2] > \
                self.lines.top[-2]:
            self.reason = '高频触及上轨'
            if self.s_model.is_rise() is False:
                self.s_model.to_rise(bt=self)

        # 1. 跌破中轨
        if self.datalow < self.lines.mid[0]:
            self.reason = '跌破中轨'
            if self.s_model.is_normal() is False:
                self.s_model.to_normal(bt=self)

        # 2. 跌幅超过3%
        # (现价-上一个交易日收盘价）/上一个交易日收盘价*100%
        scope = (self.dataclose - self.dataclose[-1]) / self.dataclose[-1]
        if scope < -0.03:
            self.reason = '跌幅超过3'
            if self.s_model.is_normal() is False:
                self.s_model.to_normal(bt=self)

        # 3. 布林线收口
        now_boll_gap = self.lines.top - self.lines.bot
        pre_boll_gap = self.lines.top[-5] - self.lines.bot[-5]
        if pre_boll_gap >= 1.5 * now_boll_gap:
            self.reason = '布林线收口'
            if self.s_model.is_normal() is False:
                self.s_model.to_normal(bt=self)

        if self.down_in_10days():
            if self.s_model.is_fall() is False:
                self.s_model.to_fall(bt=self)
                # my_close(self)
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
        """
        不同状态不同交易策略 'normal', 'rise', 'fall', 'shudder', 'asleep'
        normal状态
        1. 下轨买入
        2. 上轨平仓
        3. 当天不会平仓
        
        rise状态
        1. 每天买进1手

        fall状态
        1. 平仓，每天卖一手空单
        """

        if self.s_model.is_normal():
            if self.datalow <= self.lines.bot[0]:
                self.order = self.buy(size=self.params.size)
                return
            if self.datahigh > self.lines.top[0]:
                self.order = self.close()
                return

        elif self.s_model.is_rise():
            self.order = self.buy(size=self.params.size)
        elif self.s_model.is_fall():
            self.order = self.sell(size=1)
        elif self.s_model.is_shudder():
            pass
        elif self.s_model.is_asleep():
            pass

    def next(self):
        super(Bolling_2_0, self).next()


class DoubleMA(BaseStrategy):
    params = (('s_window', ConfigReader.short_window), ('l_window', ConfigReader.long_window), ('printlog', True))

    def __init__(self):
        super().__init__()
        self.short_ma = bt.indicators.SMA(self.datas[0].close, period=self.params.s_window)
        self.long_ma = bt.indicators.SMA(self.datas[0].close, period=self.p.l_window)

    def choose_state(self):
        pass

    def handle(self):
        size = self.getposition(self.datas[0]).size
        # 做多
        if self.short_ma[-1] < self.long_ma[-1] and self.short_ma[0] > self.long_ma[0]:
            # 开仓
            # self.order_target_value(self.datas[0], target=50000)
            self.buy(size=1)
            # 平多
        if self.short_ma[-1] > self.long_ma[-1] and self.short_ma[0] < self.long_ma[0]:
            self.close(self.datas[0])


class MACD_Strategy(BaseStrategy):
    """
    MACD 策略
    """
    params = (('p1', 12), ('p2', 26), ('size', ConfigReader.size), ('maperiod', ConfigReader.moving),
              ('printlog', True))

    def __init__(self):
        super().__init__()
        self.ema = bt.ind.EMA(self.data, period=self.p.p1, )
        self.lines.macdhist = bt.ind.MACDHisto(self.dataclose,
                                               period_me1=self.p.p1,
                                               period_me2=self.p.p2,
                                               )

        self.signal = self.lines.macdhist - self.lines.macdhist.lines.histo

    def choose_state(self):
        pass

    def handle(self):
        # 当MACD柱大于0（红柱）时买入
        # print(f'fuck {self.lines.macdhist[0] - self.signal[0]}')
        # print(f'fuck {self.signal[0]}')
        if self.lines.macdhist[0] < 0:
            # if self.lines.macdhist[0] - self.signal[0] < 0:
            # self.order = self.buy(size=1)
            self.order = self.sell(size=1)
        else:
            self.close()

        #
        # if self.macdhist[0] > 0:
        #     self.order = self.buy(size=1)
        #     print('买入')
        # else:
        #     self.close()
