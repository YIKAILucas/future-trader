# coding=utf-8

# @Author : Lucas
# @Date   : 2020/12/24 4:04 pm
# @Last Modified by:  Lucas
# @Last Modified time:


class Mydecorator(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            print('')
            func(*args, **kwargs)

        return wrapper


def log_change(func):
    def wrapper(self):
        print('')


def show_reason_and_mode(func):
    def wrapper(self):
        pre_state = self.s_model.state
        func(self)
        if pre_state == self.s_model.state:
            print(f'保持状态{self.s_model.state}')
        else:
            pass
            # print(f'切换原因->{self.reason}')

    return wrapper
