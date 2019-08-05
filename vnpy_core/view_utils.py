# -*- coding: utf-8 -*-
"""
时间:
文件名:
描述:  单例 工具类

@author: jiangyuexi1992@qq.com
"""
import json

import bitmex
import ccxt

# 单例类
import time

import logging
from django.db import DatabaseError
from django.http import HttpResponse

from vnpy_core.models import DjangoSession


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
            # _bitmex 避免和 bitmex 模块重名，所以加下划线区分
            _bitmex = ccxt.bitmex(setting)
            # 设置为测试服务器
            _bitmex.urls["api"] = _bitmex.urls["test"]
            _bitmex.urls["www"] = _bitmex.urls["test"]
            # 引入bitmex官方的对象
            _bitmex.client = bitmex.bitmex(test=True, api_key=setting["apiKey"], api_secret=setting["secret"])
            return _bitmex
        elif "OKEX" == exchange:
            obj_okex = ccxt.okex3()
            return obj_okex
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

    def get_history_ohlcv(self, gateway, timeframe, symbol, since_time):
        """
        获取历史ohlcv 数据
        :param gateway: 交易所对象
        :param symbol:  交易对
        :param since_time: 开始时间
        :return: 返回 list   开高低收 成交量
        """
        return  None
        # 请求的candles个数 12小时 的 1min k 个数
        limit = 24 * 60 / 2

        returns = gateway.fetch_ohlcv(symbol=symbol, timeframe=timeframe,
                                      limit=limit, since=since_time)
        return returns

    def custom_time(self, timestamp):
        """
        时间戳转换成日期和时间
        :param timestamp: 
        :return: 
        """
        # 转换成localtime
        time_local = time.localtime(timestamp)
        # 转换成新的时间格式(2016-05-05 20:28:54)
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        return dt

    def check_sessionid(self, request):
        """
            检查sessionid 是否是最新的
        :param request: 
        :return:  是：True 否：false
        """
        cookie_sessionid = request.COOKIES["sessionid"]

        try:
            sessions = DjangoSession.objects.filter(session_key=cookie_sessionid)
        except DatabaseError as e:
            logging.warning(e)
            return HttpResponse(json.dumps({'return': '数据库错误'}))

        for session in sessions:
            session

        if sessions:

            return True
        else:
            return False

# 工具类 单例
g_view_utils = View_utils()