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
        self.con_list = config.sections()
        self.moving = config.getint('strategy', 'moving')
        self.cash = config.getint('init', 'cash')
        self.size = config.getint('trade', 'size')

        self.s_window = config.getint('DoubleMA', 'short_window')
        self.l_window = config.getint('DoubleMA', 'long_window')
