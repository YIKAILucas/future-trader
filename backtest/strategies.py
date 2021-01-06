from abc import abstractmethod

import backtrader as bt
from pyecharts.globals import ThemeType

import config_reader
from backtest.Mydecorator import show_reason_and_mode
from backtest.state_machine import BaseMachine

ConfigReader = config_reader.ConfigReader()


class BaseStrategy(bt.Strategy):
    params = (('size', ConfigReader.trade_size), ('printlog', True))

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
            print(f'手续费{order.executed.comm}')

            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    @abstractmethod
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

    def init_model(self):
        self.state_machine = BaseMachine()
        self.s_model = self.state_machine.strategy_model
        self.reason = ''
        self.prev = ''
        print(self.s_model.state)

    def my_close(self):
        print('关仓')
        self.close()

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
            self.close()

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
    params = (('size', ConfigReader.trade_size), ('maperiod', ConfigReader.Boll_moving), ('printlog', True))

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
        if now_boll_gap >= 1.5 * pre_boll_gap and self.dataclose < self.lines.mid[0]:
            self.reason = '布林线喇叭开口,且低于中轨'
            if not self.s_model.is_rise():
                self.s_model.to_rise(bt=self)

                self.state_machine.add_state('rise')
                return

                # 2. 高频触及上轨
        if self.dataclose > self.lines.top[0] and self.dataclose[-1] > self.lines.top[-1] and self.dataclose[-2] > \
                self.lines.top[-2]:
            self.reason = '高频3次触及上轨'
            if self.s_model.is_rise() is False:
                self.s_model.to_rise(bt=self)
                return

                # 1. 跌破中轨
        if self.datalow < self.lines.mid[0]:
            self.reason = '跌破中轨'
            if self.s_model.is_normal() is False:
                self.s_model.to_normal(bt=self)
                return

                # 2. 跌幅超过3%
        # (现价-上一个交易日收盘价）/上一个交易日收盘价*100%
        scope = (self.dataclose - self.dataclose[-1]) / self.dataclose[-1]
        if scope < -0.03:
            self.reason = '跌幅超过3'
            if self.s_model.is_normal() is False:
                self.s_model.to_normal(bt=self)
                return

                # 3. 布林线收口
        now_boll_gap = self.lines.top - self.lines.bot
        pre_boll_gap = self.lines.top[-5] - self.lines.bot[-5]
        if pre_boll_gap >= 1.5 * now_boll_gap:
            self.reason = '布林线收口'
            if self.s_model.is_normal() is False:
                self.s_model.to_normal(bt=self)
                return

        if self.down_in_10days():
            if self.s_model.is_fall() is False:
                self.s_model.to_fall(bt=self)
                # my_close(self)
            else:
                print('已经是fall模式了')
            return


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
    params = (('s_window', ConfigReader.DoubleMA_short_window), ('l_window', ConfigReader.DoubleMA_long_window),
              ('printlog', True))

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


import pyecharts.options as opts
from pyecharts.charts import Line, Bar, Page


def test_py(xdata, ydata, cdata, y3, y4):
    line = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.MACARONS))
            .set_global_opts(
            datazoom_opts=[opts.DataZoomOpts()],
            tooltip_opts=opts.TooltipOpts(is_show=True),
            # xaxis_opts=opts.AxisOpts(type_="time"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ))
            .add_xaxis(xdata)
            .add_yaxis(
            series_name="EMA",
            y_axis=ydata,
            symbol='',
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=True),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
            .add_yaxis(
            series_name="期价",
            y_axis=cdata,
            symbol='',
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=True),
            tooltip_opts=opts.TooltipOpts(is_show=True),

        )
            .add_yaxis(
            series_name="持仓量",
            y_axis=y4,
            yaxis_index=1,

            # markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="min")]),
            symbol="emptyCircle",
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=True),
            tooltip_opts=opts.TooltipOpts(is_show=True),

           areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
        )
            .extend_axis(
            yaxis=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(formatter="{value} 手"),
            )
        )

    )
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS))
            .add_xaxis(xdata)
            .add_yaxis(
            series_name="macd柱",
            y_axis=y3,
            label_opts=opts.LabelOpts(is_show=False)
            #         label_opts=opts.LabelOpts(is_show=True),
        )
            #     .extend_axis(
            #         yaxis=opts.AxisOpts(
            #             axislabel_opts=opts.LabelOpts(formatter="{value} °C"), interval=5
            #         )
            .set_global_opts(title_opts=opts.TitleOpts(title="macd"),
                             xaxis_opts=opts.AxisOpts(type_='time'),
                             yaxis_opts=opts.AxisOpts(
                                 axistick_opts=opts.AxisTickOpts(is_show=False),
                                 splitline_opts=opts.SplitLineOpts(is_show=True),
                             ),
                             )
    )
    # line.overlap(bar)

    # page = Page(layout=Page.SimplePageLayout)
    # page.add(line)
    # page.add(bar)
    # page.render('fuck.html')
    line.render('fuck.html')


class MACD_Strategy(BaseStrategy):
    """
    MACD 策略
    """
    params = (('p1', 12), ('p2', 26), ('size', ConfigReader.trade_size),
              ('printlog', True))
    xlist = []
    ylist = []
    y2list = []
    y3list = []
    y4list = []

    def __init__(self):
        super().__init__()
        self.ema = bt.ind.EMA(self.data, period=self.p.p1, )
        # MACD_Strategy.ylist=self.ema

        # test_py(self.data.datetime.date(),self.data.datetime.date()

        self.lines.macdhist = bt.ind.MACDHisto(self.dataclose,
                                               period_me1=self.p.p1,
                                               period_me2=self.p.p2,
                                               )

        self.signal = self.lines.macdhist - self.lines.macdhist.lines.histo
        super().init_model()

    def choose_state(self):
        pass
        if self.lines.macdhist[0] < 0:
            if self.s_model.is_fall() is False:
                self.s_model.to_fall(self)
        else:
            if self.s_model.is_normal() is False:
                self.s_model.to_normal(self)

    def handle(self):
        self.show_me()
        # MACD_Strategy.ylist.append(self.ema[0])
        # 当MACD柱大于0（红柱）时买入
        # print(f'fuck {self.lines.macdhist[0] - self.signal[0]}')
        # print(f'fuck {self.signal[0]}')
        if self.s_model.is_normal():
            # if self.lines.macdhist[0] > 0:
            if self.lines.macdhist[0] - self.signal[0] > 0:
                self.order = self.buy(size=1)
            else:
                self.close()
        elif self.s_model.is_fall():
            # if self.lines.macdhist[0] < 0:
            if self.lines.macdhist[0] - self.signal[0] < 0:
                self.order = self.sell(size=1)
            else:
                self.close()

        # if self.macdhist[0] > 0:
        #     self.order = self.buy(size=1)
        #     print('买入')
        # else:
        #     self.close()

    def show_me(self):
        MACD_Strategy.xlist.append(self.data.datetime.date())
        MACD_Strategy.ylist.append(self.ema[0])
        MACD_Strategy.y2list.append(self.dataclose[0])
        MACD_Strategy.y3list.append(self.lines.macdhist[0])
        MACD_Strategy.y4list.append(self.getposition().size)


class MA_1_0(BaseStrategy):
    params = (('p1', 12), ('p2', 26), ('size', ConfigReader.trade_size),
              ('printlog', True))
    def choose_state(self):
        if self.lines.macdhist[0] < 0:
            pass
            # if self.s_model.is_fall() is False:
            #     self.s_model.to_fall(self)
        else:
            if self.s_model.is_normal() is False:
                self.s_model.to_normal(self)
        pass

    def __init__(self):
        super(MA_1_0, self).__init__()
        self.sma_5 = bt.ind.SimpleMovingAverage(self.dataclose, period=ConfigReader.MA_line_5)
        self.sma_10 = bt.ind.SimpleMovingAverage(self.dataclose, period=ConfigReader.MA_line_10)
        self.sma_20 = bt.ind.SimpleMovingAverage(self.dataclose, period=ConfigReader.MA_line_20)
        self.sma_40 = bt.ind.SimpleMovingAverage(self.dataclose, period=ConfigReader.MA_line_40)
        self.lines.macdhist = bt.ind.MACDHisto(self.dataclose,
                                               period_me1=self.p.p1,
                                               period_me2=self.p.p2,
                                               )

        self.signal = self.lines.macdhist - self.lines.macdhist.lines.histo
        super().init_model()
        # self.sma_60 = bt.ind.SimpleMovingAverage(self.dataclose, period=ConfigReader.MA_line_60)

    def handle(self):
        print(f'第一次{self.dataclose[-20]}')
        if self.is_twined():
            print(f'缠绕状态不交易')
            return

        if self.s_model.is_normal():
            # if self.lines.macdhist[0] > 0:
            if self.sma_5[-1] < self.sma_40[-1] and self.sma_5[0] > self.sma_40[0]:
            # if self.sma_5[0] > self.sma_40[0]:
                self.buy(size=1)
            if self.sma_5[-1] > self.sma_40[-1] and self.sma_5[0] < self.sma_40[0]:
            # if self.sma_5[0] < self.sma_40[0]:
                self.close()
        elif self.s_model.is_fall():
            if self.sma_5[-1] < self.sma_40[-1] and self.sma_5[0] < self.sma_40[0]:
            # if self.sma_5[0] < self.sma_40[0]:
                self.buy(size=1)
            if self.sma_5[-1] > self.sma_40[-1] and self.sma_5[0] > self.sma_40[0]:
            # if self.sma_5[0] > self.sma_40[0]:
                self.close()

    def is_twined(self) -> bool:
        count = 0
        for i in range(0, -20, -1):
            if MA_1_0.is_crossed(self.sma_5[i], self.sma_40[i], self.sma_5[i - 1], self.sma_40[i - 1]):
                count += 1
        print(f'缠绕次数{count}')
        if count >= 4:
            return True

    @staticmethod
    def is_crossed(a1, b1, a2, b2) -> bool:
        if (a1 < b1 and a2 > b2) or (a1 > b1 and a2 < b2):
            return True
        return False
