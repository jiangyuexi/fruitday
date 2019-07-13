# -*- coding: utf-8 -*-
"""
时间:
文件名:
描述:

@author: jiangyuexi1992@qq.com
"""
import ccxt

# 单例类
class View_utils(object):
    """
     views.py 里的基础函数
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def create_gateway_obj(self, exchange, setting):
        """
        创建gateway对象
        :param exchange: 交易所
        :param setting: 配置信息
        :return: 交易所对象
        """
        if "BITMEX" == exchange:
            bitmex = ccxt.bitmex(setting)
            # 设置为测试服务器
            bitmex.urls["api"] = bitmex.urls["test"]
            bitmex.urls["www"] = bitmex.urls["test"]
            return bitmex
        else:
            pass

    def get_exchange_class(self, str_exchange):
        """
        根据交易所名字获取 ccxt 里交易所类名
        :param str_exchange: 
        :return: 
        """
        if "BITMEX" == str_exchange:
            return ccxt.bitmex
        elif "ZB" == str_exchange:
            return ccxt.zb

