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
        self.reason = ''
        self.a = 0
        self.prev = ''

    def print_self(self):
        print(id(self))

    def on_exit(self, reason, bt):
        print(f'退出{self.state}', end=' ')
        self.prev = self.state

    def on_enter(self, reason, bt):
        self.a += 1
        print(f'进入{self.state}', end=' ')
        print(f'原因->{reason}')
        if self.state == 'fall':
            bt.my_close()

        self.prev = ''


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
                                         initial='normal', before_state_change='on_exit',
                                         after_state_change='on_enter', auto_transitions=True)
        # self._strategy_machine.add_transition('to_normal', '*', 'normal')
        # self._strategy_machine.add_transition('to_rise', '*', 'rise')
        # self._strategy_machine.add_transition('to_fall', '*', 'fall')
        # self._strategy_machine.add_transition('to_shudder', '*', 'shudder')
        # self._strategy_machine.add_transition('to_asleep', '*', 'asleep')

        # self._strategy_machine.on_enter_gas('say_hello')


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