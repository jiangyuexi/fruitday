# encoding: UTF-8
"""
"""

import hashlib
import hmac
import sys
import time
from copy import copy
from datetime import datetime, timedelta
from threading import Lock
from urllib.parse import urlencode

import peewee
from requests import ConnectionError

from vnpy.api.rest import Request, RestClient
from vnpy.api.websocket import WebsocketClient
from vnpy.trader.constant import (
    Direction,
    Exchange,
    OrderType,
    Product,
    Status,
    Offset,
    Interval
)
from vnpy.trader.gateway import BaseGateway
from vnpy.trader.object import (
    TickData,
    OrderData,
    TradeData,
    PositionData,
    AccountData,
    ContractData,
    BarData,
    OrderRequest,
    CancelRequest,
    SubscribeRequest,
    HistoryRequest,
    SubscribeRequest1Min)

REST_HOST = "https://www.bitmex.com/api/v1"
WEBSOCKET_HOST = "wss://www.bitmex.com/realtime"

TESTNET_REST_HOST = "https://testnet.bitmex.com/api/v1"
TESTNET_WEBSOCKET_HOST = "wss://testnet.bitmex.com/realtime"

STATUS_BITMEX2VT = {
    "New": Status.NOTTRADED,
    "Partially filled": Status.PARTTRADED,
    "Filled": Status.ALLTRADED,
    "Canceled": Status.CANCELLED,
    "Rejected": Status.REJECTED,
}

DIRECTION_VT2BITMEX = {Direction.LONG: "Buy", Direction.SHORT: "Sell"}
DIRECTION_BITMEX2VT = {v: k for k, v in DIRECTION_VT2BITMEX.items()}

ORDERTYPE_VT2BITMEX = {
    OrderType.LIMIT: "Limit",
    OrderType.MARKET: "Market",
    OrderType.STOP: "Stop",
    # OrderType.LIMITIFTOUCHED: "LimitIfTouched",
    # OrderType.MARKETIFTOUCHED: "MarketIfTouched"
}
ORDERTYPE_BITMEX2VT = {v: k for k, v in ORDERTYPE_VT2BITMEX.items()}

INTERVAL_VT2BITMEX = {
    Interval.MINUTE: "1m",
    Interval.HOUR: "1h",
    Interval.DAILY: "1d",
}

TIMEDELTA_MAP = {
    Interval.MINUTE: timedelta(minutes=1),
    Interval.HOUR: timedelta(hours=1),
    Interval.DAILY: timedelta(days=1),
}


class BitmexGateway(BaseGateway):
    """
    VN Trader Gateway for BitMEX connection.
    """

    default_setting = {
        "ID": "",
        "Secret": "",
        "会话数": 3,
        "账户" : "",
        "服务器": "TESTNET",
        "代理地址": "",
        "代理端口": "",
    }

    exchanges = [Exchange.BITMEX3]

    def __init__(self, event_engine):
        """Constructor"""
        super(BitmexGateway, self).__init__(event_engine, "BITMEX3")

        self.rest_api = BitmexRestApi(self)
        self.ws_api = BitmexWebsocketApi(self)

    def connect(self, setting: dict):
        """"""
        key = setting["ID"]
        secret = setting["Secret"]
        user_id = setting["账户"]
        session_number = setting["会话数"]
        server = setting["服务器"]
        proxy_host = setting["代理地址"]
        proxy_port = setting["代理端口"]

        if proxy_port.isdigit():
            proxy_port = int(proxy_port)
        else:
            proxy_port = 0

        self.rest_api.connect(key, secret, session_number,
                              server, proxy_host, proxy_port)

        self.ws_api.connect(key, secret, user_id, server, proxy_host, proxy_port)
        # websocket will push all account status on connected, including asset, position and orders.

    def subscribe(self, req: SubscribeRequest):
        """"""
        self.ws_api.subscribe(req)

    def subscribe1min(self, req: SubscribeRequest1Min):
        """"""
        self.ws_api.subscribe1min(req)

    def send_order(self, req: OrderRequest):
        """"""
        return self.rest_api.send_order(req)

    def cancel_order(self, req: CancelRequest):
        """"""
        self.rest_api.cancel_order(req)

    def query_account(self):
        """"""
        pass

    def query_position(self):
        """"""
        pass

    def query_history(self, req: HistoryRequest):
        """"""
        return self.rest_api.query_history(req)

    def close(self):
        """"""
        self.rest_api.stop()
        self.ws_api.stop()


class BitmexRestApi(RestClient):
    """
    BitMEX REST API
    """

    def __init__(self, gateway: BaseGateway):
        """"""
        super(BitmexRestApi, self).__init__()

        self.gateway = gateway
        self.gateway_name = gateway.gateway_name

        self.key = ""
        self.secret = ""

        self.order_count = 1_000_000
        self.order_count_lock = Lock()

        self.connect_time = 0

    def sign(self, request):
        """
        Generate BitMEX signature.
        """
        # Sign
        expires = int(time.time() + 30)

        if request.params:
            query = urlencode(request.params)
            path = request.path + "?" + query
        else:
            path = request.path

        if request.data:
            request.data = urlencode(request.data)
        else:
            request.data = ""

        msg = request.method + "/api/v1" + path + str(expires) + request.data
        signature = hmac.new(
            self.secret, msg.encode(), digestmod=hashlib.sha256
        ).hexdigest()

        # Add headers
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "api-key": self.key,
            "api-expires": str(expires),
            "api-signature": signature,
        }

        request.headers = headers
        return request

    def connect(
        self,
        key: str,
        secret: str,
        session_number: int,
        server: str,
        proxy_host: str,
        proxy_port: int,
    ):
        """
        Initialize connection to REST server.
        """
        self.key = key
        self.secret = secret.encode()

        self.connect_time = (
            int(datetime.now().strftime("%y%m%d%H%M%S")) * self.order_count
        )

        if server == "REAL":
            self.init(REST_HOST, proxy_host, proxy_port)
        else:
            self.init(TESTNET_REST_HOST, proxy_host, proxy_port)

        self.start(session_number)

        self.gateway.write_log("REST API启动成功")

    def _new_order_id(self):
        with self.order_count_lock:
            self.order_count += 1
            return self.order_count

    def send_order(self, req: OrderRequest):
        """"""
        orderid = str(self.connect_time + self._new_order_id())

        data = {
            "symbol": req.symbol,
            "side": DIRECTION_VT2BITMEX[req.direction],
            "ordType": ORDERTYPE_VT2BITMEX[req.type],
            "orderQty": int(req.volume),
            "clOrdID": orderid,
        }

        inst = []   # Order special instructions

        # Only add price for limit order.
        if req.type == OrderType.LIMIT:
            data["price"] = req.price
        elif req.type == OrderType.STOP:
            data["stopPx"] = req.price
            inst.append("LastPrice")

        # Check for close order
        if req.offset == Offset.CLOSE:
            inst.append("ReduceOnly")

        # Generate execInst
        if inst:
            data["execInst"] = ",".join(inst)

        order = req.create_order_data(orderid, self.gateway_name)

        self.add_request(
            "POST",
            "/order",
            callback=self.on_send_order,
            data=data,
            extra=order,
            on_failed=self.on_send_order_failed,
            on_error=self.on_send_order_error,
        )

        self.gateway.on_order(order)
        return order.vt_orderid

    def cancel_order(self, req: CancelRequest):
        """"""
        orderid = req.orderid

        if orderid.isdigit():
            params = {"clOrdID": orderid}
        else:
            params = {"orderID": orderid}

        self.add_request(
            "DELETE",
            "/order",
            callback=self.on_cancel_order,
            params=params,
            on_error=self.on_cancel_order_error,
        )

    def query_history(self, req: HistoryRequest):
        """"""
        history = []
        count = 750
        start_time = req.start.isoformat()

        while True:
            # Create query params
            params = {
                "binSize": INTERVAL_VT2BITMEX[req.interval],
                "symbol": req.symbol,
                "count": count,
                "startTime": start_time
            }

            # Add end time if specified
            if req.end:
                params["endTime"] = req.end.isoformat()

            # Get response from server
            resp = self.request(
                "GET",
                "/trade/bucketed",
                params=params
            )

            # Break if request failed with other status code
            if resp.status_code // 100 != 2:
                msg = f"获取历史数据失败，状态码：{resp.status_code}，信息：{resp.text}"
                self.gateway.write_log(msg)
                break
            else:
                data = resp.json()
                if not data:
                    msg = f"获取历史数据为空，开始时间：{start_time}，数量：{count}"
                    break

                for d in data:
                    dt = datetime.strptime(
                        d["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    bar = BarData(
                        symbol=req.symbol,
                        exchange=req.exchange,
                        datetime=dt,
                        interval=req.interval,
                        volume=d["volume"],
                        open_price=d["open"],
                        high_price=d["high"],
                        low_price=d["low"],
                        close_price=d["close"],
                        gateway_name=self.gateway_name
                    )
                    history.append(bar)

                begin = data[0]["timestamp"]
                end = data[-1]["timestamp"]
                msg = f"获取历史数据成功，{req.symbol} - {req.interval.value}，{begin} - {end}"
                self.gateway.write_log(msg)

                # Break if total data count less than 750 (latest date collected)
                if len(data) < 750:
                    break

                # Update start time
                start_time = bar.datetime + TIMEDELTA_MAP[req.interval]

        return history

    def on_send_order_failed(self, status_code: str, request: Request):
        """
        Callback when sending order failed on server.
        """
        order = request.extra
        order.status = Status.REJECTED
        self.gateway.on_order(order)

        msg = f"委托失败，状态码：{status_code}，信息：{request.response.text}"
        self.gateway.write_log(msg)

    def on_send_order_error(
        self, exception_type: type, exception_value: Exception, tb, request: Request
    ):
        """
        Callback when sending order caused exception.
        """
        order = request.extra
        order.status = Status.REJECTED
        self.gateway.on_order(order)

        # Record exception if not ConnectionError
        if not issubclass(exception_type, ConnectionError):
            self.on_error(exception_type, exception_value, tb, request)

    def on_send_order(self, data, request):
        """Websocket will push a new order status"""
        pass

    def on_cancel_order_error(
        self, exception_type: type, exception_value: Exception, tb, request: Request
    ):
        """
        Callback when cancelling order failed on server.
        """
        # Record exception if not ConnectionError
        if not issubclass(exception_type, ConnectionError):
            self.on_error(exception_type, exception_value, tb, request)

    def on_cancel_order(self, data, request):
        """Websocket will push a new order status"""
        pass

    def on_failed(self, status_code: int, request: Request):
        """
        Callback to handle request failed.
        """
        msg = f"请求失败，状态码：{status_code}，信息：{request.response.text}"
        self.gateway.write_log(msg)

    def on_error(
        self, exception_type: type, exception_value: Exception, tb, request: Request
    ):
        """
        Callback to handler request exception.
        """
        msg = f"触发异常，状态码：{exception_type}，信息：{exception_value}"
        self.gateway.write_log(msg)

        sys.stderr.write(
            self.exception_detail(exception_type, exception_value, tb, request)
        )


class BitmexWebsocketApi(WebsocketClient):
    """"""

    def __init__(self, gateway):
        """"""
        super(BitmexWebsocketApi, self).__init__()

        self.gateway = gateway
        self.gateway_name = gateway.gateway_name

        self.key = ""
        self.secret = ""
        self.user_id = ""

        self.callbacks = {
            "trade": self.on_tick,
            "orderBook10": self.on_depth,
            "execution": self.on_trade,
            "order": self.on_order,
            "position": self.on_position,
            "margin": self.on_account,
            "instrument": self.on_contract,
        }

        self.ticks = {}
        self.bars = {}
        self.accounts = {}
        self.orders = {}
        self.trades = set()

    def connect(
        self, key: str, secret: str, user_id: str, server: str, proxy_host: str, proxy_port: int
    ):
        """"""
        self.key = key
        self.secret = secret.encode()
        self.user_id = user_id

        if server == "REAL":
            self.init(WEBSOCKET_HOST, proxy_host, proxy_port)
        else:
            self.init(TESTNET_WEBSOCKET_HOST, proxy_host, proxy_port)

        self.start()

    def subscribe(self, req: SubscribeRequest):
        """
        Subscribe to tick data upate.
        """
        tick = TickData(
            symbol=req.symbol,
            exchange=req.exchange,
            timestamp=0.0,
            name=req.symbol,
            datetime=datetime.now(),
            gateway_name=self.gateway_name,
        )
        self.ticks[req.symbol] = tick

    def subscribe1min(self, req: SubscribeRequest1Min):
        """
        订阅 1min bar 数据
        :param req: 
        :return: 
        """
        """
        min1bar = BarData(
            symbol=req.symbol,
            exchange=req.exchange,
            datetime=datetime.now(),
            interval=Interval.MINUTE,
            gateway_name=self.gateway_name,
        )
        """

        return None

    def on_connected(self):
        """"""
        self.gateway.write_log("Websocket API连接成功")
        self.authenticate()

    def on_disconnected(self):
        """"""
        self.gateway.write_log("Websocket API连接断开")

    def on_packet(self, packet: dict):
        """"""
        if "error" in packet:
            self.gateway.write_log("Websocket API报错：%s" % packet["error"])

            if "not valid" in packet["error"]:
                self.active = False

        elif "request" in packet:
            req = packet["request"]
            success = packet["success"]

            if success:
                if req["op"] == "authKey":
                    self.gateway.write_log("Websocket API验证授权成功")
                    self.subscribe_topic()

        elif "table" in packet:
            name = packet["table"]
            callback = self.callbacks[name]

            if isinstance(packet["data"], list):
                for d in packet["data"]:
                    callback(d)
            else:
                callback(packet["data"])

    def on_error(self, exception_type: type, exception_value: Exception, tb):
        """"""
        msg = f"触发异常，状态码：{exception_type}，信息：{exception_value}"
        self.gateway.write_log(msg)

        sys.stderr.write(self.exception_detail(
            exception_type, exception_value, tb))

    def authenticate(self):
        """
        Authenticate websockey connection to subscribe private topic.
        """
        expires = int(time.time())
        method = "GET"
        path = "/realtime"
        msg = method + path + str(expires)
        signature = hmac.new(
            self.secret, msg.encode(), digestmod=hashlib.sha256
        ).hexdigest()

        req = {"op": "authKey", "args": [self.key, expires, signature]}
        self.send_packet(req)

    def subscribe_topic(self):
        """
        Subscribe to all private topics.
        """
        req = {
            "op": "subscribe",
            "args": [
                "instrument",
                "trade",
                "orderBook10",
                "execution",
                "order",
                "position",
                "margin",
            ],
        }
        self.send_packet(req)

    def on_tick(self, d):
        """"""
        symbol = d["symbol"]
        tick = self.ticks.get(symbol, None)
        if not tick:
            return

        tick.last_price = d["price"]
        tick.datetime = datetime.strptime(
            "1992-12-20", "%Y-%m-%d")
        # 备注名
        user_id = self.user_id
        position_list = Position.select().where(Position.position_user_id == user_id)
        count = 0
        for _ in position_list:
            count += 1

        if count:
            # 如果存在记录就，填充价格
            t = Position().get(Position.position_user_id == user_id)  # 实例化表的类型
            t.position_lastprice = tick.last_price
            t.save()
        else:
            pass

        # self.gateway.on_tick(copy(tick))

    def on_depth(self, d):
        """"""
        return
        symbol = d["symbol"]
        tick = self.ticks.get(symbol, None)
        if not tick:
            return

        for n, buf in enumerate(d["bids"][:5]):
            price, volume = buf
            tick.__setattr__("bid_price_%s" % (n + 1), price)
            tick.__setattr__("bid_volume_%s" % (n + 1), volume)

        for n, buf in enumerate(d["asks"][:5]):
            price, volume = buf
            tick.__setattr__("ask_price_%s" % (n + 1), price)
            tick.__setattr__("ask_volume_%s" % (n + 1), volume)

        tick.datetime = datetime.strptime(
            d["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
        # self.gateway.on_tick(copy(tick))

    def on_trade(self, d):
        """"""
        # Filter trade update with no trade volume and side (funding)
        if not d["lastQty"] or not d["side"]:
            return

        # print("trade")
        # print(d)

        tradeid = d["execID"]
        if tradeid in self.trades:
            return
        self.trades.add(tradeid)

        if d["clOrdID"]:
            orderid = d["clOrdID"]
        else:
            orderid = d["orderID"]

        trade = TradeData(
            symbol=d["symbol"],
            exchange=Exchange.BITMEX,
            orderid=orderid,
            tradeid=tradeid,
            direction=DIRECTION_BITMEX2VT[d["side"]],
            price=d["lastPx"],
            volume=d["lastQty"],
            time=d["timestamp"][11:19],
            gateway_name=self.gateway_name,
        )

        self.gateway.on_trade(trade)

    def on_order(self, d):
        """"""
        if "ordStatus" not in d:
            return

        # print("order")
        # print(d)

        sysid = d["orderID"]
        order = self.orders.get(sysid, None)
        if not order:
            if d["clOrdID"]:
                orderid = d["clOrdID"]
            else:
                orderid = sysid

            # time = d["timestamp"][11:19]

            order = OrderData(
                symbol=d["symbol"],
                exchange=Exchange.BITMEX,
                type=ORDERTYPE_BITMEX2VT[d["ordType"]],
                orderid=orderid,
                direction=DIRECTION_BITMEX2VT[d["side"]],
                price=d["price"],
                volume=d["orderQty"],
                time=d["timestamp"][11:19],
                gateway_name=self.gateway_name,
            )
            self.orders[sysid] = order

        order.traded = d.get("cumQty", order.traded)
        order.status = STATUS_BITMEX2VT.get(d["ordStatus"], order.status)

        self.gateway.on_order(copy(order))

    def on_position(self, d):
        """"""
        if ('markPrice' not in d.keys()) or ('lastPrice' not in d.keys()):
            return

        accountid = str(d["account"])
        # 备注名
        user_id = self.user_id

        position_list = Position.select().where(Position.position_user_id == user_id, Position.position_accountid == accountid)
        count = 0
        for _ in position_list:
            count += 1

        if count:
            if 'avgEntryPrice' in d.keys():
                # 有开仓价
                # 记录存在， update
                t = Position().get(Position.position_user_id == user_id, Position.position_accountid == accountid)  # 实例化表的类型
                t.position_currentqty = d["currentQty"]
                t.position_liqprice = d["liquidationPrice"]
                t.position_markprice = d["markPrice"]
                # t.position_lastprice = d["lastPrice"]
                t.position_avgentryprice = d["avgEntryPrice"]
                t.save()
            else:
                t = Position().get(Position.position_user_id == user_id, Position.position_accountid == accountid)  # 实例化表的类型
                t.position_currentqty = d["currentQty"]
                t.position_liqprice = d["liquidationPrice"]
                t.position_markprice = d["markPrice"]
                # t.position_lastprice = d["lastPrice"]
                t.save()
        else:
            #记录不存在, instert
            # 插入数据
            if 'avgEntryPrice' in d.keys():
                # 有开仓价
                o_position = Position().insert(
                    position_user_id=user_id,
                    position_accountid=accountid,
                    position_symbol=d["symbol"],
                    position_currentqty=d["currentQty"],
                    position_liqprice=d["liquidationPrice"],
                    position_markprice=d["markPrice"],
                    # position_lastprice=d["lastPrice"],
                    position_avgentryprice=d["avgEntryPrice"]
                )
            else:
                # 无开仓价
                o_position = Position().insert(
                    position_user_id=user_id,
                    position_accountid=accountid,
                    position_symbol=d["symbol"],
                    position_currentqty=d["currentQty"],
                    position_liqprice=d["liquidationPrice"],
                    position_markprice=d["markPrice"],
                    # position_lastprice=d["lastPrice"]
                )

            o_position.execute()  # 执行
            # self.gateway.on_position(position)

    def on_account(self, d):
        """
        处理账号资金信息 可以用资金，冻结资金，总资金
        :param d: 
        :return: 
        """
        accountid = str(d["account"])
        account = self.accounts.get(accountid, None)
        if not account:
            account = AccountData(accountid=accountid,
                                  gateway_name=self.gateway_name)
            self.accounts[accountid] = account
        # 总金额（xbt）
        account.balance = float(d.get("marginBalance", account.balance))/1000000000
        # 可用xbt
        account.available = float(d.get("availableMargin", account.available))/1000000000
        # 冻结 xbt
        account.frozen = account.balance - account.available
        # 备注名
        user_id = self.user_id
        # 删除数据
        o_money = Money.delete().where(Money.money_user_id == user_id, Money.money_accountid == accountid)
        o_money.execute()  # 执行指令
        # 插入数据库
        o_money = Money().insert(
            money_user_id=user_id,
            money_balance=account.balance,
            money_available=account.available,
            money_frozen=account.frozen,
            money_accountid=accountid

        )
        o_money.execute()  # 执行
        # self.gateway.on_account(copy(account))

    def on_contract(self, d):
        """"""
        if "tickSize" not in d:
            return

        if not d["lotSize"]:
            return
        # print("交易对")
        # print(d)

        contract = ContractData(
            symbol=d["symbol"],
            exchange=Exchange.BITMEX,
            name=d["symbol"],
            product=Product.FUTURES,
            pricetick=d["tickSize"],
            size=d["lotSize"],
            stop_supported=True,
            net_position=True,
            history_data=True,
            gateway_name=self.gateway_name,
        )

        self.gateway.on_contract(contract)


#建立链接
# connect = peewee.SqliteDatabase("/home/jiangyx/fruitday/db.sqlite3") #运行该程序后就能在当前目录下创建“test.db”数据库

settings = {'host': '47.244.240.38', 'password': '123456', 'port': 3306, 'user': 'root'}
connect = peewee.MySQLDatabase("fruitday",**settings)

class Money(peewee.Model):
    money_user_id = peewee.CharField(max_length=255)  # This field type is a guess.
    money_balance = peewee.FloatField()
    money_available = peewee.FloatField()
    money_frozen = peewee.FloatField()
    money_accountid = peewee.CharField(primary_key=True, max_length=255)  # This field type is a guess.

    class Meta:
        database = connect


class Position(peewee.Model):
    position_user_id = peewee.CharField(max_length=255)  # This field type is a guess.
    position_accountid = peewee.CharField(primary_key=True, max_length=255)  # This field type is a guess.
    position_symbol = peewee.CharField(max_length=255)  # This field type is a guess.
    position_currentqty = peewee.FloatField(db_column='position_currentQty')  # Field name made lowercase.
    position_liqprice = peewee.FloatField(db_column='position_liqPrice')  # Field name made lowercase.
    position_markprice = peewee.FloatField(db_column='position_markPrice')  # Field name made lowercase.
    position_lastprice = peewee.FloatField(db_column='position_lastPrice')  # Field name made lowercase.
    position_avgentryprice = peewee.FloatField(db_column='position_avgEntryPrice')

    class Meta:
        database = connect


