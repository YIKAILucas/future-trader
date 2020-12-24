# coding=utf-8

# @Author : Lucas
# @Date   : 2020/12/24 9:28 am
# @Last Modified by:  Lucas
# @Last Modified time:
from transitions import Machine

from backtest.config_reader import singleton


@singleton
class Matter(object):
    def __init__(self):
        self.a = 1

    def print_self(self):
        print(id(self))

    pass


@singleton
class BaseMachine(object):
    """
    策略状态机
    """
    strategy_states = ['normal', 'rise', 'fall', 'shudder', 'asleep']

    # matter = None
    @property
    def strategy_model(self):
        return self._strategy_model

    @strategy_model.setter
    def strategy_model(self, value):
        pass

    @property
    def strategy_machine(self):
        return self._strategy_machine

    @strategy_machine.setter
    def strategy_machine(self, value):
        pass

    def __init__(self):
        self._strategy_model = Matter()
        self._strategy_machine = Machine(model=self._strategy_model, states=self.strategy_states,
                                         initial='normal')

@singleton
class RiskMachine(object):
    """
    风险控制机
    """
    pass


if __name__ == '__main__':
    state_machine = BaseMachine()
    print(state_machine.strategy_model.a)
    print(state_machine.strategy_model.state)
    state_machine.strategy_model.to_rise()
    print(state_machine.strategy_model.state)
    #
    # # Test
    # print(matter.state)  # solid
    # matter.to_solid()
    # print(matter.state)
    # matter.to_plasma()
    # print(matter.state)
