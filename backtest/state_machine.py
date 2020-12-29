# coding=utf-8

# @Author : Lucas
# @Date   : 2020/12/24 9:28 am
# @Last Modified by:  Lucas
# @Last Modified time:
from queue import PriorityQueue

from transitions import Machine

from backtest.config_reader import singleton


@singleton
class BaseModel(object):
    def __init__(self):
        self.reason = ''
        self.count = 0
        self.prev = ''

    def print_self(self):
        print(id(self))

    def on_exit(self, bt):
        bt.state_exit_callback()
        # pass

    def on_enter(self, bt):
        bt.state_enter_callback()
        pass


@singleton
class BaseMachine(object):
    """
    策略状态机
    """
    strategy_states = [(1, 'normal'), (2, 'rise'), (3, 'fall'), (4, 'shudder'), (5, 'asleep')]

    def get_state(self):
        state_l = []
        for i in self.strategy_states:
            state_l.append(i[1])
        return state_l
        pass

    def add_queue(self, state):
        self.q.put_nowait(state)

    def get_item(self):
        next_item = None
        if not self.q.empty():
            next_item = self.q.get_nowait()
            print(f'pop出的状态{next_item}')
            self.q.task_done()
        # clear queue
        while not self.q.empty():
            self.q.get_nowait()

        return next_item

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
        self._strategy_model = BaseModel()
        self.q = PriorityQueue()
        self._strategy_machine = Machine(model=self._strategy_model, states=self.get_state(),
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
    print(state_machine.strategy_model.state)
    state_machine.strategy_model.to_rise()
    print(state_machine.strategy_model.state)
    state_machine.next_state()

    #
    # # Test
    # print(matter.state)  # solid
    # matter.to_solid()
    # print(matter.state)
    # matter.to_plasma()
    # print(matter.state)
