# coding=utf-8

# @Author : Lucas
# @Date   : 2020/12/22 5:18 pm
# @Last Modified by:  Lucas
# @Last Modified time:
import functools
from configparser import ConfigParser


def singleton(cls):
    cls.__new_original__ = cls.__new__

    @functools.wraps(cls.__new__)
    def singleton_new(cls, *args, **kwargs):
        it = cls.__dict__.get('__it__')
        if it is not None:
            return it

        cls.__it__ = it = cls.__new_original__(cls, *args, **kwargs)
        it.__init_original__(*args, **kwargs)
        return it

    cls.__new__ = singleton_new
    cls.__init_original__ = cls.__init__
    cls.__init__ = object.__init__
    return cls


@singleton
class ConfigReader(object):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self):
        self.load_config()

    def load_config(self):
        config = ConfigParser()
        config.read('./backtest/config.ini')
        sections = config.sections()
        for sec in sections:
            print(sec)
            for item in config.items(sec):
                exec(f'self.{item[0]}={item[1]}')


if __name__ == '__main__':
    config = ConfigParser()
    config.read('./config.ini')

    sections = config.sections()
    for sec in sections:
        print(sec)
        for i in config.items(sec):
            print(i)
            exec(f'{i[0]}={i[1]}')
