# -*- coding: utf-8 -*-
"""
时间:
文件名:
描述:

@author: jiangyuexi1992@qq.com
"""
import ccxt

# 单例类
import time


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

    def convert_serialize_object_to_str(self, serialize_object: str):
        """
        serialize object  转换成 json 字符串
        :param serialize_object:  str 格式的 serialize object
        :return: str 格式的 json字符串
        """
        serialize_object = serialize_object.replace("+", " ")
        serialize_object = serialize_object.replace("%7B", chr(0x7B))
        serialize_object = serialize_object.replace("%7D", chr(0x7D))
        serialize_object = serialize_object.replace("%22", chr(0x22))
        serialize_object = serialize_object.replace("%3A", chr(0x3A))
        serialize_object = serialize_object.replace("%2C", chr(0x2C))
        serialize_object = serialize_object.replace("%5B", chr(0x5B))
        serialize_object = serialize_object.replace("%5D", chr(0x5D))
        return serialize_object

    def get_symbols(self,gateway):
        """
        获取市场交易对
        :param gateway: 交易所对象
        :return: 一个交易所的所有交易对
        """
        # 获取市场交易对
        gateway.load_markets()
        symbols = gateway.symbols
        print(gateway.symbols)  # 打印市场交易对
        return symbols

    def get_history_ohlcv(self, gateway, symbol, since_time):
        """
        获取历史ohlcv 数据
        :param gateway: 交易所对象
        :param symbol:  交易对
        :param since_time: 开始时间
        :return: 返回 list   开高低收 成交量
        """

        # 请求的candles个数 12小时 的 1min k 个数
        limit = 24 * 60 / 2

        returns = gateway.fetch_ohlcv(symbol=symbol, timeframe="1m",
                                      limit=limit, since=since_time)
        return returns


