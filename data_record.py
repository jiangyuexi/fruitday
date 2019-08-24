# -*- coding: utf-8 -*-
"""
时间: 2019年8月9日17:13:33
文件名:
描述:
  抓取数据存放到 db.sqlite3
@author: jiangyuexi1992@qq.com
"""
import json
import time

import bitmex
import sqlite3


class RecordOpenInterest(object):
    """
    未平仓合约 数据采集
    """

    def __init__(self):
        # 引入bitmex官方的对象
        setting = {
            "apiKey": "RvaWeVuSBpQIFPZBrSdcd7YK",
            "secret": "bvsWqi7homc8wJsoT59uVGBgou54ifdoRDF6Irh2qDEiwFEZ",
            "role": "master",
            "会话数": 3,
            "账户": "jiangyuexi1992@qq.com",
            "代理地址": "",
            "代理端口": ""
        }
        self.client = bitmex.bitmex(test=False, api_key=setting["apiKey"], api_secret=setting["secret"])
        self.conn = sqlite3.connect('./db.sqlite3')

    def __del__(self):
        """
        析构函数，释放 数据库对象
        :return: 
        """
        print("释放 数据库对象")
        self.conn.close()

    def convert_datetime2timestamp(self, datetime):
        """
        （datetime 类型 ）把日期 转换成 时间戳    单位s
        :param date: (2016-05-05 20:28:54)
        :return: 时间戳 s
        """
        # 转为时间戳
        timeStamp = int(time.mktime(datetime.timetuple()))
        return timeStamp

    def data_record(self):
        """
        获取一条实时数据 （未平仓合约）
        :return: 
        """
        results = self.client.Instrument.\
        Instrument_get(symbol="XBTUSD", columns="""["openInterest", "markPrice"]""").result()[0][0]

        _r = [self.convert_datetime2timestamp(results["timestamp"]) * 1000,
              results["symbol"], results["openInterest"], results["markPrice"]]

        return _r

    def inster_openInterest(self, timestamp, symbol, openInterest, markPrice):
        """
        往 openInterest 表里插入一条数据
        :param timestamp: 时间戳  ms
        :param symbol: 交易品种
        :param openInterest: 未成交合约价值 （USD）
        :param markPrice: 标记价格（USD）
        :return: 
        """
        c = self.conn.cursor()

        c.execute(f"""INSERT INTO "main"."openInterest" ("timestamp", "symbol", "openInterest", "markPrice") \
                    VALUES ('{timestamp}', '{symbol}', {openInterest}, {markPrice})""")

        self.conn.commit()

if __name__ == '__main__':
    recordOpenInterest = RecordOpenInterest()

    while True:
        lst_instrument = recordOpenInterest.data_record()
        recordOpenInterest.inster_openInterest(*lst_instrument)
        time.sleep(3 * 60)

