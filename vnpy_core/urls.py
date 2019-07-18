# -*- coding: utf-8 -*-
"""
时间:
文件名:
描述:

@author: jiangyuexi1992@qq.com
"""

from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'^vnpy_core/$', vnpy_core_views),
    url(r'^login/$', login_views),
    url(r'^login/index/$', login_views),
    url(r'^login/check_user/$', check_user_views),
    url(r'^login/account_info.html', account_info_views),
    url(r'^login/sub_protocolConfig.html$', sub_protocolConfig_views),
    url(r'^login/sub_equipInfo.html$', sub_equipInfo_views),
    url(r'^login/sub_equipStatus.html$', sub_equipStatus_views),
    url(r'^login/sub_RS232.html$', sub_RS232_views),
    url(r'^login/sub_RS485.html$', sub_RS485_views),
    url(r'^login/sub_CAN.html$', sub_CAN_views),
    url(r'^login/sub_web.html$', sub_web_views),
    url(r'^login/sub_userManage.html$', sub_userManage_views),
    url(r'^login/sub_changepwd.html$', sub_changepwd_views),
    url(r'^login/sub_index.html$', sub_index_views),
    url(r'^login/trade_operation.html$', trade_operation_views),
    # url(r'^account_info/commit_apikey/$', commit_apikey_views),

    url(r'^login/sub_protocolConfig$', sub_protocolConfig_views),
    url(r'^logout/$',logout_views),
    url(r'^login/api_key/$',api_key_views),
    url(r'^login/balance/$', balance_views),
    url(r'^fetch_my_trades/$', fetch_my_trades_views),
    url(r'^create_order/$', create_order_views),
    url(r'^cancel_order/$', cancel_order_views),
    url(r'^fetch_orders/$', fetch_orders_views),
    url(r'^fetch_open_orders/$', fetch_open_orders_views),




]
