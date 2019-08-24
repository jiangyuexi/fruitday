from time import sleep

import logging

from vnpy.event import EventEngine
from vnpy.gateway.bitmex import BitmexGateway
from vnpy.gateway.bitmex1 import BitmexGateway as BitmexGateway1
from vnpy.gateway.bitmex2 import BitmexGateway as BitmexGateway2
from vnpy.gateway.bitmex3 import BitmexGateway as BitmexGateway3
from vnpy.gateway.bitmex4 import BitmexGateway as BitmexGateway4
from vnpy.gateway.bitmex5 import BitmexGateway as BitmexGateway5
from vnpy.gateway.bitmex6 import BitmexGateway as BitmexGateway6
from vnpy.gateway.bitmex7 import BitmexGateway as BitmexGateway7

from vnpy.trader.constant import Exchange

from vnpy.trader.engine import MainEngine

# from vnpy.gateway.futu import FutuGateway
# from vnpy.gateway.ib import IbGateway
# from vnpy.gateway.ctp import CtpGateway
# from vnpy.gateway.femas import FemasGateway
# from vnpy.gateway.tiger import TigerGateway
# from vnpy.gateway.oes import OesGateway
# from vnpy.gateway.okex import OkexGateway
from vnpy.gateway.huobi import HuobiGateway
# from vnpy.gateway.bitfinex import BitfinexGateway
# from vnpy.gateway.onetoken import OnetokenGateway
# from vnpy.gateway.okexf import OkexfGateway
# from vnpy.gateway.xtp import XtpGateway
# from vnpy.gateway.hbdm import HbdmGateway


from vnpy.app.data_recorder import DataRecorderApp

from vnpy.trader.noui.no_widget import ConnectNoDialog


def main():
    """"""
    # 创建 QApplication  对象 并进行初始化

    # 事件引擎
    event_engine = EventEngine()
    # 把事件引擎附加到主引擎里
    main_engine = MainEngine(event_engine)

    main_engine.add_gateway(BitmexGateway)
    main_engine.add_gateway(BitmexGateway1)
    main_engine.add_gateway(BitmexGateway2)
    main_engine.add_gateway(BitmexGateway3)
    main_engine.add_gateway(BitmexGateway4)
    # main_engine.add_gateway(BitmexGateway5)
    # main_engine.add_gateway(BitmexGateway6)
    # main_engine.add_gateway(BitmexGateway7)

    sleep(1)
    # 把 app 保存到 apps 和 engines 里
    main_engine.add_app(DataRecorderApp)
    # 获取所有交易通道
    gateway_names = main_engine.get_all_gateway_names()
    for name in gateway_names:
        # 连接火币平台
        connect = ConnectNoDialog(main_engine=main_engine, gateway_name=name)
        connect.connect()
        sleep(6)
    while True:
        # 一天
        sleep(24 * 60 * 60)


if __name__ == "__main__":
    main()
