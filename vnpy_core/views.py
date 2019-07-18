import json

import logging
import pickle

from django.contrib.auth.hashers import make_password, check_password
from django.db import DatabaseError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

import ccxt

from vnpy_core.models import User
from .view_utils import View_utils
# 存放 通道 对象
g_gateways = {}
# 工具类
g_view_utils = View_utils()

COOKIE_EXPIRES_TIME = 60*60*24*365

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
        user_name = body["账户"]

        balances = []
        for k, gateway in g_gateways.items():
            # 现在只支持bitmex， 后面可以在此处扩展
            if isinstance(gateway, ccxt_class_name) and k == user_name:
                balance = gateway.fetch_balance()
                balances.append(balance)

        msg = {"账户": user_name, "balances": balances}

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
        user_name = body["账户"]

        fetch_my_trades = []
        for k, gateway in g_gateways.items():
            if isinstance(gateway, ccxt_class_name) and k == user_name:
                my_trades = gateway.fetch_my_trades(symbol=symbol)
                fetch_my_trades.append(my_trades)

        msg = {"user_name": user_name, "获取现有仓位和方向": fetch_my_trades}
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

    :param request:
    :return:
    """
    if request.method == "GET":
        return render(request, "login.html")
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
                resp.set_cookie("UserName", find_user[0].user_name, COOKIE_EXPIRES_TIME)
                resp.set_cookie("PassWord", find_user[0].user_pass_word, COOKIE_EXPIRES_TIME)
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
        if request.session['user_name']:
            del request.session['user_id']
            del request.session['user_name']
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


def commit_apikey_views(request):
    """
    
    :param request: 
    :return: 
    """

    return redirect('/api_key/')

