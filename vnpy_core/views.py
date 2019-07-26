import datetime
import json

import logging
import pickle

import time
from pandas import DataFrame, Series
import pandas as pd
import numpy as np
import bitmex
from django.contrib.auth.hashers import make_password, check_password
from django.db import DatabaseError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

import ccxt

from vnpy_core.models import User, Min1
from .view_utils import View_utils
# 存放 通道 对象
g_gateways = {}
# 工具类 单例
g_view_utils = View_utils()
# cookie的保留时间
COOKIE_EXPIRES_TIME = 60*60*24*365
# 一天的时间间隔
ONEDAY = 1512489600000 - 1512403200000

@csrf_exempt
def vnpy_core_views(request):
    if "POST" == request.method:
        body = json.loads(request.body)
        exchange = body["exchange"]

    msg = {"exchange": exchange}

    return HttpResponse(json.dumps(msg))



@csrf_exempt
def api_key_views(request):
    """
        api 账户接入
    :param request: 
    :return: 
    """
    if "POST" == request.method:
        # 把 body 里的数据取出来，转换成json格式
        data = request.body.decode()

        body = json.loads(data)

        exchange = body["exchange"]
        ccxt_class_name = g_view_utils.get_exchange_class(str_exchange=exchange)
        api_keys = body["Keys"]
        gateway_name = body["gateway_name"]

        for api_key in api_keys:
            # 建立一个对象
            if api_key["账户"] not in g_gateways:
                setting = api_key
                gateway = g_view_utils.create_gateway_obj(exchange=exchange, setting=setting)
                g_gateways[api_key["账户"]] = gateway

    else:
        pass

    msg = {"账户": [k for k in g_gateways.keys()]}
    response = HttpResponse(json.dumps(msg))
    # 返回cookies
    response.set_cookie("user_ids", msg["账户"], expires=COOKIE_EXPIRES_TIME)
    return response


@csrf_exempt
def balance_views(request):
    """
    账户余额查询
    :param request: 
    :return: 
    """
    if "POST" == request.method:
        body = json.loads(request.body)
        exchange = body["exchange"]
        ccxt_class_name = g_view_utils.get_exchange_class(str_exchange=exchange)
        gateway_name = body["gateway_name"]
        user_id = body["user_id"]

        balances = []
        for k, gateway in g_gateways.items():
            # 现在只支持bitmex， 后面可以在此处扩展
            if isinstance(gateway, ccxt_class_name) and k == user_id:
                balance = gateway.fetch_balance()
                balances.append(balance)

        msg = {"账户": user_id, "balances": balances}

        return HttpResponse(json.dumps(msg))


@csrf_exempt
def fetch_ohlcv_views(request):
    """
    获取市场价格
    :param request: 
    :return: 
    """
    if "POST" == request.method:
        body = json.loads(request.body)
        exchange = body["exchange"]
        ccxt_class_name = g_view_utils.get_exchange_class(str_exchange=exchange)
        gateway_name = body["gateway_name"]
        user_id = body["user_id"]
        symbol = body["symbol"]
        timeframe = body["timeframe"]

        for k, gateway in g_gateways.items():
            # 现在只支持bitmex， 后面可以在此处扩展
            if isinstance(gateway, ccxt_class_name) and k == user_id:
                # 请求的candles个数
                limit = 5
                #  当前时间
                current_time = int(time.time() // 60 * 60 * 1000)  # 毫秒
                print(current_time)

                # 获取请求开始的时间
                since_time = current_time - limit * 60 * 1000
                returns = gateway.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit, since=since_time)

        msg = {"user_id": user_id, "markets": returns}

        return HttpResponse(json.dumps(msg))


@csrf_exempt
def fetch_ticks_views(request):
    """
    获取市场价格
    :param request: 
    :return: 
    """
    if "POST" == request.method:
        body = json.loads(request.body)
        exchange = body["exchange"]
        ccxt_class_name = g_view_utils.get_exchange_class(str_exchange=exchange)
        gateway_name = body["gateway_name"]
        user_id = body["user_id"]
        symbol = body["symbol"]
        returns = None
        for k, gateway in g_gateways.items():
            # 现在只支持bitmex， 后面可以在此处扩展
            if isinstance(gateway, ccxt_class_name) and k == user_id:

                returns = gateway.fetch_ticker(symbol=symbol)

        msg = {"user_id": user_id, "ticks": returns}

        return HttpResponse(json.dumps(msg))


@csrf_exempt
def fetch_history_ohlcv_views(request):
    """
    获取市场价格 60天
    :param request: 
    :return: 
    """
    if "POST" == request.method:
        body = json.loads(request.body)
        exchange = body["exchange"]
        ccxt_class_name = g_view_utils.get_exchange_class(str_exchange=exchange)
        gateway_name = body["gateway_name"]
        user_id = body["user_id"]
        symbol = body["symbol"]
        timeframe = body["timeframe"]

        # 1 开始时间
        a = "2019-05-20 00:00:00"
        # a = start_date + " 00:00:00"
        # 将其转换为时间数组
        timeArray = time.strptime(a, "%Y-%m-%d %H:%M:%S")
        start_timeStamp = int(time.mktime(timeArray)) * 1000

        for k, gateway in g_gateways.items():
            # 现在只支持bitmex， 后面可以在此处扩展
            if isinstance(gateway, ccxt_class_name) and k == user_id:
                for i in range(31 * 2):
                    time.sleep(3)
                    start_timeStamp += i * ONEDAY / 2
                    lst = g_view_utils.get_history_ohlcv(gateway=gateway,symbol=symbol,since_time=start_timeStamp)
                    for o in lst:
                        Min1(min1_timestamp=o[0], min1_open=o[1], min1_high=o[2],
                             min1_low=o[3], min1_close=o[4], min1_volume=o[5]).save();

        msg = {"user_id": user_id, "markets": "OK"}

        return HttpResponse(json.dumps(msg))


@csrf_exempt
def fetch_my_trades_views(request):
    """
    获取现有仓位和方向
    :param request: 
    :return: 
    """
    if "POST" == request.method:
        body = json.loads(request.body)
        exchange = body["exchange"]
        ccxt_class_name = g_view_utils.get_exchange_class(str_exchange=exchange)
        gateway_name = body["gateway_name"]
        symbol = body["symbol"]
        user_id = body["user_id"]

        result = None
        for k, gateway in g_gateways.items():
            if isinstance(gateway, ccxt_class_name) and k == user_id:
                # my_trades = gateway.fetch_my_trades(symbol=symbol)
                result = gateway.client.Position.Position_get(filter=json.dumps({'symbol': 'XBTUSD'})).result()[0][0]
                result["currentTimestamp"] = str(result["currentTimestamp"])
                result["openingTimestamp"] = str(result["openingTimestamp"])
                result["timestamp"] = str(result["timestamp"])

        msg = {"user_id": user_id, "position": result}
        return HttpResponse(json.dumps(msg))


@csrf_exempt
def candles_views(request):
    """
    获取1min k线历史数据
    :param request: 
    :return: 
    """
    if "POST" != request.method:
        return

    try:
        # 查询数据库
        candles = Min1.objects.filter()
    except DatabaseError as e:
        logging.warning(e)
        return HttpResponse(json.dumps({'return': '数据库错误'}))

    history_price = []
    for candle in candles:

        # ['2015/12/31', '3570.47', '3539.18', '-33.69', '-0.94%', '3538.35', '3580.6', '176963664', '25403106', '-']
        # [   "时间"，       “开”，  “关”    “？”，  “？”，   “低”，  “高”，  “？”，     “？”，   '_']
        timeYMD = g_view_utils.custom_time(candle.min1_timestamp // 1000)
        _temp = \
            [timeYMD, candle.min1_open, candle.min1_close, '?', '?',
             candle.min1_low, candle.min1_high, '?', candle.min1_volume, '_']
        history_price.append(_temp)

    msg = {"user_name": "", "return": history_price}

    return HttpResponse(json.dumps(msg))


@csrf_exempt
def get_candles_views(request):
    """
    获取 k线历史数据
    :param request: 
    :return: 
    """
    if "POST" != request.method:
        return

    body = json.loads(request.body)
    exchange = body["exchange"]
    ccxt_class_name = g_view_utils.get_exchange_class(str_exchange=exchange)
    gateway_name = body["gateway_name"]
    user_id = body["user_id"]
    symbol = body["symbol"]
    timeframe = body["timeframe"]
    limit = body["limit"]

    # 1 开始时间
    a = "2019-07-05 00:00:00"
    # a = start_date + " 00:00:00"
    # 将其转换为时间数组
    timeArray = time.strptime(a, "%Y-%m-%d %H:%M:%S")
    start_timeStamp = time.time() * 1000 - ONEDAY * 20
    history_price = []
    candles = []
    for k, gateway in g_gateways.items():
        # 现在只支持bitmex， 后面可以在此处扩展
        if isinstance(gateway, ccxt_class_name) and k == user_id:
            # 行情信息
            candles = gateway.fetch_ohlcv(symbol=symbol, timeframe=timeframe,
                                limit=limit, since=start_timeStamp)

            for candle in candles:
                # ['2015/12/31', '3570.47', '3539.18', '-33.69', '-0.94%', '3538.35', '3580.6', '176963664', '25403106', '-']
                # [   "时间"，       “开”，  “关”    “？”，  “？”，   “低”，  “高”，  “？”，     “？”，   '_']
                timeYMD = g_view_utils.custom_time(candle[0] // 1000)
                _temp = \
                    [timeYMD, candle[1], candle[4], '?', '?',
                     candle[3], candle[2], '?', candle[5], '_']
                history_price.append(_temp)

            # 历史费率
            result = gateway.client.Funding.Funding_get(symbol="XBTUSD", reverse=True, count=20*3
                                                        ).result()[0]
            result.reverse()
            # 连续的时间
            timestamps = [str(result[0]["timestamp"] + datetime.timedelta(hours=8 + i))[0:-6] \
                          for i in range(20 *3 * 8)]

            founding_rates = []
            for r in result:
                r["timestamp"] = str(r["timestamp"] + datetime.timedelta(hours=8))[0:-6]
                r["fundingInterval"] = str(r["fundingInterval"])[0:-6]
                _tmp = [r["timestamp"], r["symbol"],
                        r["fundingInterval"], r["fundingRate"], r["fundingRateDaily"]]
                founding_rates.append(_tmp)


    df_founding_rates = DataFrame(founding_rates,
                                  columns=["timestamp", "symbol", "fundingInterval",
                                         "fundingRate", "fundingRateDaily"])
    df_history_price = DataFrame(history_price,
                                 columns=['timestamp', 'open', 'close', 'v1',
                                        'v2', 'low', 'high', 'v3', 'vol', 'v4'])
    # 合并d1 和df_founding_rates
    d1 = DataFrame(timestamps, columns=['timestamp'])

    pd_datas = pd.merge(d1, df_founding_rates, on=['timestamp'], how='left').fillna(1100001)
    # left jion
    pd_datas_inner = pd.merge(df_history_price, pd_datas, on=["timestamp"], how='inner')

    msg = {"user_id": user_id, "return": pd_datas_inner.values.tolist()}

    return HttpResponse(json.dumps(msg))


@csrf_exempt
def fetch_orders_views(request):
    """
    现有某个品种所有订单
    :param request: 
    :return: 
    """
    if "POST" == request.method:
        body = json.loads(request.body)
        exchange = body["exchange"]
        ccxt_class_name = g_view_utils.get_exchange_class(str_exchange=exchange)
        gateway_name = body["gateway_name"]
        symbol = body["symbol"]
        user_name = body["账户"]

        returns = []
        for k, gateway in g_gateways.items():
            if isinstance(gateway, ccxt_class_name) and k == user_name:
                ret = gateway.fetch_orders(symbol=symbol)
                returns.append(ret)

        msg = {"user_name": user_name, "现有某个品种所有订单": returns}
        return HttpResponse(json.dumps(msg))


@csrf_exempt
def fetch_open_orders_views(request):
    """
    现有某个品种所有订单
    :param request: 
    :return: 
    """
    if "POST" == request.method:
        body = json.loads(request.body)
        exchange = body["exchange"]
        ccxt_class_name = g_view_utils.get_exchange_class(str_exchange=exchange)
        gateway_name = body["gateway_name"]
        symbol = body["symbol"]
        user_name = body["账户"]

        returns = []
        for k, gateway in g_gateways.items():
            if isinstance(gateway, ccxt_class_name) and k == user_name:
                ret = gateway.fetch_open_orders(symbol=symbol)
                returns.append(ret)

        msg = {"user_name": user_name, "现有某个品种所有open订单": returns}
        return HttpResponse(json.dumps(msg))


@csrf_exempt
def create_order_views(request):
    """
        下单
    :param request: 
    :return: 
    """
    if "POST" == request.method:
        body = json.loads(request.body)
        exchange = body["exchange"]
        ccxt_class_name = g_view_utils.get_exchange_class(str_exchange=exchange)
        gateway_name = body["gateway_name"]
        user_name = body["账户"]
        params = body["params"]
        if "market" == params["type"]:
            price =None
        else:
            price = params["price"]

        create_orders = []
        for k, gateway in g_gateways.items():
            if isinstance(gateway, ccxt_class_name) and k == user_name:
                orders = gateway.create_order(symbol=params["symbol"],
                                              type=params["type"],
                                              side=params["side"],
                                              amount=params["amount"],
                                              price=price
                                              )
                create_orders.append(orders)

        msg = {"user_name": user_name, "create_orders": create_orders}
        return HttpResponse(json.dumps(msg))


@csrf_exempt
def cancel_order_views(request):
    """
    撤单
    :param request: 
    :return: 
    """
    if "POST" == request.method:
        body = json.loads(request.body)
        exchange = body["exchange"]
        ccxt_class_name = g_view_utils.get_exchange_class(str_exchange=exchange)
        gateway_name = body["gateway_name"]
        user_name = body["账户"]
        ids = body["ids"]

        returns = []
        for k, gateway in g_gateways.items():
            if isinstance(gateway, ccxt_class_name) and k == user_name:
                for id in ids:
                    ret = gateway.cancel_order(id=id)
                    returns.append(ret)

        msg = {"user_name": user_name, "returns": returns}
        return HttpResponse(json.dumps(msg))


@csrf_exempt
def check_user_views(request):
    """

    :param request:
    :return:
    """
    if request.method == "GET":
        return JsonResponse({"msg": "GET"})
    elif request.method == "POST":
        UserName = request.POST["UserName"]

        # to do
        ret = User.objects.filter(user_name=UserName)
        if ret:
            if UserName == ret[0].user_name:
                # 用户名存在
                return JsonResponse({"msg": "exsit"})
            else:
                # 用户名不存在
                return JsonResponse({"msg": "not_exsit"})
        else:
            # 用户名不存在
            return JsonResponse({"msg": "not_exsit"})


@csrf_exempt
def login_views(request):
    """
    用户登录
    :param request:
    :return:
    """
    if request.method == "GET":
        # 每次在登录的时候，都要去cookie中获取username的值。
        UserName = request.COOKIES.get('UserName', '')
        return render(request, "login.html", {'UserName': UserName})
    elif request.method == "POST":
        print("COOKIES", request.COOKIES)
        '''
        cookies {'sessionid': 'wdwllf0numkxii9e69ljmpy1vzamu2o1', 
            'csrftoken': 'h57XzcWUMXnIdyPtB7gPzanh9IFl7BN27w2kSFlPnLzMwM4em5H5YcgDomBmcyxF'}
        '''
        print("SESSION", request.session)
        UserName = request.POST["UserName"]
        PassWord = request.POST["PassWord"]

        try:
            # 查询数据库
            find_user = User.objects.filter(user_name=UserName)
        except DatabaseError as e:
            logging.warning(e)
            return HttpResponse(json.dumps({'return': '数据库错误'}))

        # 判断用户是否存在
        if not find_user:
            return HttpResponse(json.dumps({'return': '用户不存在'}))

        # to do
        if find_user:
            if UserName == find_user[0].user_name and PassWord == find_user[0].user_pass_word:
                resp = render(request, "index.html")
                # 设置cookies
                resp.set_cookie("UserName", find_user[0].user_name, COOKIE_EXPIRES_TIME)
                # resp.set_cookie("PassWord", find_user[0].user_pass_word, COOKIE_EXPIRES_TIME)
                # 设置sessions
                request.session['UserName'] = find_user[0].user_name
                request.session["UserPermission"] = find_user[0].user_permission
                return resp
            else:
                return JsonResponse({"msg": "用户或密码错误！", "dsf":"dsfsd", "dfsdsd":4325435})
        else:
            err_msg = "登录失败！！"
            # return HttpResponse(json.dumps({"msg": err_msg}), content_type='application/json')
            # return JsonResponse({"msg": err_msg})
            return render(request, "login.html")


def logout_views(request):
    try:
        request.session.flush()
    except KeyError as e:
        logging.warning(e)
    return redirect('/index/')


def sub_index_views(request):
    """

    :param request:
    :return:
    """
    return render(request, "sub_index.html")


def account_info_views(request):
    """
    
    :param request: 
    :return: 
    """
    if request.method == "GET":
        return render(request, "account_info.html")


@csrf_exempt
def sub_protocolConfig_views(request):
    """

    :param request:
    :return:
    """
    if request.method == "GET":
        return render(request, "sub_protocolConfig.html")
    elif request.method == "POST":
        # $.post('sub_protocolConfig', {"FileName": "sub_protocolConfig.html", "method": "send_get"}, function(data)
        FileName = request.POST["FileName"]
        if FileName == "sub_protocolConfig.html":
            # 这里进行数据库查询操作


            # 假数据，测试

            return JsonResponse({"msg": [
                (1002001, "eth0", 1001001, "网络通信"),
                (1002002, "CAN0", 1001002, "CAN通信"),
                (1002003, "tty/mxc0", 1001003, "232通信"),
                (1002004, "tty/mxc1", 1001004, "485通信"),

            ]})




def sub_equipInfo_views(request):
    """

    :param request:
    :return:
    """
    return render(request, "sub_equipInfo.html")


def sub_equipStatus_views(request):
    """

    :param request:
    :return:
    """
    return render(request, "sub_equipStatus.html")


def sub_RS232_views(request):
    """

    :param request:
    :return:
    """
    return render(request, "sub_RS232.html")


def sub_RS485_views(request):
    """

    :param request:
    :return:
    """
    return render(request, "sub_RS485.html")


def sub_CAN_views(request):
    """

    :param request:
    :return:
    """
    return render(request, "sub_CAN.html")


def sub_web_views(request):
    """

    :param request:
    :return:
    """
    return render(request, "sub_web.html")


def sub_userManage_views(request):
    """

    :param request:
    :return:
    """
    return render(request, "sub_userManage.html")


def sub_changepwd_views(request):
    """

    :param request:
    :return:
    """
    return render(request, "sub_changepwd.html")


def trade_operation_views(request):
    """
    
    :param request: 
    :return: 
    """
    return  render(request, "trade_operation.html")


def sub_candlestick_views(request):
    """
    显示行情
    :param request:
    :return:
    """
    return render(request, "candlestick-brush.html")


def line_simple_views(request):
    """
    历史费率
    :param request:
    :return:
    """
    return render(request, "line-simple.html")


def sub_candlestick1_views(request):
    """
    显示行情
    :param request:
    :return:
    """
    return render(request, "candlestick_sh.html")



def commit_apikey_views(request):
    """
    
    :param request: 
    :return: 
    """

    return redirect('/api_key/')


@csrf_exempt
def get_symbols_views(request):
    """
    获取交易所的所有交易对
    :param request: 
    :return: 
    """
    if "POST" == request.method:
        body = json.loads(request.body)
        exchange = body["exchange"]
        ccxt_class_name = g_view_utils.get_exchange_class(str_exchange=exchange)
        gateway_name = body["gateway_name"]
        user_id = body["user_id"]

        for k, gateway in g_gateways.items():
            if isinstance(gateway, ccxt_class_name) and k == user_id:
                returns = g_view_utils.get_symbols(gateway=gateway)

        msg = {"user_id": user_id, "symbols": returns}
        return HttpResponse(json.dumps(msg))


@csrf_exempt
def get_history_founding_rate_views(request):
    """
    获取历史费率
    :param request: 
    :return: 
    """
    if "POST" != request.method:
        return None

    body = json.loads(request.body)
    exchange = body["exchange"]
    ccxt_class_name = g_view_utils.get_exchange_class(str_exchange=exchange)
    gateway_name = body["gateway_name"]
    symbol = body["symbol"]
    user_id = body["user_id"]
    reverse = body["reverse"]
    count = body["count"]

    result = None
    founding_rates = []
    for k, gateway in g_gateways.items():
        if isinstance(gateway, ccxt_class_name) and k == user_id:

            # api_response = api_instance.funding_get(symbol=symbol, filter=filter, columns=columns, count=count,
            #                                         start=start, reverse=reverse, start_time=start_time,
            #                                         end_time=end_time)
            result = gateway.client.Funding.Funding_get(symbol=symbol, reverse=reverse,count=count
                                                        ).result()[0]
            result.reverse()
            # 连续的时间
            timestamps = [str( result[0]["timestamp"] + datetime.timedelta(hours=8 + i))[0:-6] \
                          for i in range(count * 8)]

            for r in result:
                r["timestamp"] = str( r["timestamp"] + datetime.timedelta(hours=8))[0:-6]
                r["fundingInterval"] = str( r["fundingInterval"])[0:-6]
                _tmp =[r["timestamp"], r["symbol"],
                       r["fundingInterval"], r["fundingRate"], r["fundingRateDaily"]]
                founding_rates.append(_tmp)

    d1 = DataFrame(timestamps)
    d2 = DataFrame(founding_rates)
    # 合并d1 和d2
    pd_datas = pd.merge(d1, d2, on=0, how='left').fillna(0)
    # merge将df4和df5按apts列合并,left表示以df4为基准,注意合并DataFrame里cars列名字变化
    msg = {"user_id": user_id, "founding_rate": pd_datas.values.tolist()}
    return HttpResponse(json.dumps(msg))


