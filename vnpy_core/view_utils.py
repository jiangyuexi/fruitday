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

import datetime
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
        elif "BITMEX_REAL" == exchange:
            # bitmex实盘对象
            # _bitmex 避免和 bitmex 模块重名，所以加下划线区分
            _bitmex = ccxt.bitmex(setting)

            # 引入bitmex官方的对象
            _bitmex.client = bitmex.bitmex(test=False, api_key=setting["apiKey"], api_secret=setting["secret"])
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
        elif "BITMEX_REAL" == str_exchange:
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


    def convert_time(self, timestamp):
        """
        时间戳转换成日期和时间 str类型 单位 s
        :param timestamp: 
        :return: 
        """
        # 转换成localtime
        time_local = time.localtime(timestamp)
        # 转换成新的时间格式(2016-05-05 20:28:54)
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        return dt

    def convert_date(self, timestamp):
        """
        时间戳转换成日期  单位 s
        :param timestamp: 
        :return: 
        """
        # 转换成localtime
        time_local = time.localtime(timestamp)
        # 转换成新的时间格式(2016-05-05 20:28:54)
        dt = time.strftime("%Y-%m-%d", time_local)
        return dt

    def convert_datetime(self, timestamp):
        """
        时间戳转换成日期 datetime类型 单位 s
        :param timestamp: 
        :return: datetime类型 的日期和时间
        """
        # 转换成localtime
        time_local = time.localtime(timestamp)
        # str  to   datetime
        dt_datetime = datetime.datetime(time_local.tm_year, time_local.tm_mon, time_local.tm_mday, time_local.tm_hour,
                                        time_local.tm_hour, time_local.tm_min, time_local.tm_sec)
        return dt_datetime

    def convert_date2timestamp(self, date):
        """
        str    把日期(2016-05-05 20:28:54) 转换成 时间戳    单位s
        :param date: (2016-05-05 20:28:54)
        :return: 时间戳 s
        """
        # 转为时间数组
        timeArray = time.strptime(date, "%Y-%m-%d %H:%M:%S")
        # 转为时间戳
        timeStamp = int(time.mktime(timeArray))
        return timeStamp

    def convert_date2timeArray(self, date):
        """
        str    把日期(2016-05-05 20:28:54) 转换成 timeArray    
        :param date: (2016-05-05 20:28:54)
        :return: datatime
        """
        # 转为时间数组
        timeArray = time.strptime(date, "%Y-%m-%d %H:%M:%S")
        return timeArray

    def convert_datetime2timestamp(self, datetime):
        """
        （datetime 类型 ）把日期 转换成 时间戳    单位s
        :param date: (2016-05-05 20:28:54)
        :return: 时间戳 s
        """
        # 转为时间戳
        timeStamp = int(time.mktime(datetime.timetuple()))
        return timeStamp

    def check_2_time(self, t1, t2, interval=3600):
        """
        校验两个时间是否相差一个小时
        :param t1: 时间戳1 前
        :param t2: 时间戳2 后
        :param interval: 时间间隔 （sec）
        :return:  True:相差1小时；False: not
        """
        if 0 == t1:
            # 只有一条时间戳，返回True
            return True

        if interval == (t2 - t1):
            # 一小时有 3600 sec
            return True
        else:
            return False

    def check_is_series(self, t_list, interval=3600):
        """
        检查一组时间是否连续， interval 时间间隔 （sec）
        :param t_list:  一组时间戳  （sec）
        :param interval: 时间间隔 （sec）
        :return: True:连续；False: 不连续
        """
        t1 = 0
        for t in t_list:
            ret = self.check_2_time(t1=t1, t2=t, interval=interval)
            if not ret:
                return False
            t1 = t
        return True

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

    def barGenerator(self, little_bars_lst):
        """
        根据小的bar 合并为一根bar
        :param little_bar_lst:  小的bar   [[1564502400000	9670.5	10000.0	9632.5	9757.0	15979043.0], 
                                            [1564502400000	9670.5	10000.0	9632.5	9757.0	15979043.0],[], [], []]   
        :return: 一根bar
        """
        # 时间戳
        timestamp = little_bars_lst[0][0]
        # open price
        open = little_bars_lst[0][1]
        highs = []
        lows = []
        # close price
        close = little_bars_lst[-1][4]
        vols = []
        for little_bar in little_bars_lst:
            highs.append(little_bar[2])
            lows.append(little_bar[3])
            vols.append(little_bar[5])
        # high price
        high = max(highs)
        # low price
        low = min(lows)
        # 成交量
        vol = sum(vols)
        return [timestamp, open, high, low, close, vol]





# 工具类 单例
g_view_utils = View_utils()