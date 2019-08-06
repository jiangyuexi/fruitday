# -*- coding: utf-8 -*-
"""
时间:
文件名:
描述:

@author: jiangyuexi1992@qq.com
"""
import json

import ccxt
import time
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from vnpy_core.view_utils import g_view_utils


class OkexViews(object):
    """
    Okex的rest api 接口  单例类
    """
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
            构造函数，定义类成员变量
        """
        # 币币：spot  的 api信息
        passphrase_spot = "guosizheng"
        apiKey_spot = "b89f9235-9515-4fc6-86d6-9370ce323be2"
        secretKey_spot = "4DABB62298D3642F334D4D686AEB96D3"
        # ccxt 币币对象
        self.obj_spot = g_view_utils.create_gateway_obj(exchange="OKEX", setting=None)
        self.obj_spot.apiKey = apiKey_spot
        self.obj_spot.secret = secretKey_spot
        self.obj_spot.passphrase = passphrase_spot
        # ##################################################################################

        # 合约 futures  的 api信息
        passphrase_futures = "mengyu513"
        apiKey_futures = "f511c9c6-dc43-4e67-900d-98d2d9c9e936"
        secretKey_futures = "D79566F2AEC59A329B00604A8D90515F"

        # ccxt 交割合约对象
        self.obj_futures = g_view_utils.create_gateway_obj(exchange="OKEX", setting=None)
        self.obj_futures.apiKey = passphrase_futures
        self.obj_futures.secret = apiKey_futures
        self.obj_futures.passphrase = secretKey_futures

    @staticmethod
    @csrf_exempt
    def api_key_views(request):
        """
        okex api 接入
        :param request: 
        :return: 
        """
        if "POST" != request.method:
            return HttpResponse(json.dumps({"msg": "get method"}))

        okex_instance.obj_spot.load_markets()
        okex_instance.obj_futures.load_markets()
        msg = {"msg": "okex api ok!!"}

        return HttpResponse(json.dumps(msg))

    @staticmethod
    @csrf_exempt
    def fetch_history_ohlcv_views(request):
        """
        获取市场价格 n天
        :param request: 
        :return: 
        """
        # 每个用户唯一登录
        # if not g_view_utils.check_sessionid(request):
        #     return HttpResponse(json.dumps({"msg": "已经在其它地方登录"}))

        if "POST" == request.method:
            # body = json.loads(request.body)
            symbol = "BTC/USDT"
            symbol_futures = "BTC-USD-190927"
            timeframe = "1d"

            # 1 开始时间
            a = "2018-10-20 00:00:00"
            # a = start_date + " 00:00:00"
            # 将其转换为时间数组
            timeArray = time.strptime(a, "%Y-%m-%d %H:%M:%S")
            start_timeStamp = int(time.mktime(timeArray)) * 1000
            # 现货 一天的 开高低收
            spot_ohlcv_1d = okex_instance.obj_spot.fetch_ohlcv(symbol, timeframe=timeframe, limit=90)
            for o in spot_ohlcv_1d:
                o[0] = g_view_utils.custom_time(o[0]//1000)
            # 期货 一天的 开高低收
            futures_ohlcv_1d = okex_instance.obj_futures.fetch_ohlcv(symbol_futures, timeframe=timeframe, limit=90)
            for o in futures_ohlcv_1d:
                o[0] = g_view_utils.custom_time(o[0]//1000)
            # 期货除以现货
            futures_spot = []
            for o1, o2 in zip(futures_ohlcv_1d, spot_ohlcv_1d):
                if o1[0] == o2[0]:
                    futures_spot.append([o1[0], (float(o1[4])/float(o2[4]) - 1.0) * 100.0])
            lst_len = 0
            if (len(spot_ohlcv_1d) == len(futures_ohlcv_1d)) and (len(spot_ohlcv_1d) == len(futures_spot)):
                lst_len = len(spot_ohlcv_1d)

            msg = {"spot_ohlcv_1d": spot_ohlcv_1d, "futures_ohlcv_1d": futures_ohlcv_1d,
                   "futures_spot": futures_spot, "lst_len": lst_len}
            return HttpResponse(json.dumps(msg))


# okex views 单例对象
okex_instance = OkexViews()







