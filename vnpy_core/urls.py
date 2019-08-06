# -*- coding: utf-8 -*-
"""
时间:
文件名:
描述:

@author: jiangyuexi1992@qq.com
"""

from django.conf.urls import url

from vnpy_core.okex_views import OkexViews
from .views import *



urlpatterns = [
    url(r'^vnpy_core/$', vnpy_core_views),
    url(r'^login/$', login_views),
    url(r'^login/index/$', login_views),
    url(r'^login/check_user/$', check_user_views),
    url(r'^login/account_info.html', account_info_views),
    url(r'^login/sub_index.html$', sub_index_views),
    url(r'^login/trade_operation.html$', trade_operation_views),
    url(r'^login/candlestick-brush.html$', candlestick_brush_views),
    url(r'^login/candlestick_sh.html$', sub_candlestick1_views),
    url(r'^login/line-simple.html$', line_simple_views),
    url(r'^login/spot_futures_brush.html$', spot_futures_brush_views),



    url(r'^logout/$',logout_views),
    url(r'^login/api_key/$',api_key_views),
    url(r'^login/balance/$', balance_views),
    url(r'^login/get_symbols/$', get_symbols_views),
    url(r'^login/fetch_ohlcv/$', fetch_ohlcv_views),
    url(r'^login/fetch_ticks/$', fetch_ticks_views),
    url(r'^login/fetch_history_ohlcv/$', fetch_history_ohlcv_views),
    url(r'^login/fetch_history_founding_rates/$', fetch_history_founding_rates_views),
    url(r'^login/fetch_my_trades/$', fetch_my_trades_views),
    url(r'^login/get_history_founding_rate/$', get_history_founding_rate_views),
    url(r'^login/candles/$', candles_views),
    url(r'^login/get_candles_founding_rates/$', get_candles_founding_rates_views),
    url(r'^login/create_order/$', create_order_views),
    url(r'^login/create_orders/$', create_orders_views),
    url(r'^login/create_orders_close/$', create_orders_close_views),
    url(r'^login/cancel_order/$', cancel_order_views),
    url(r'^login/fetch_orders/$', fetch_orders_views),
    url(r'^login/fetch_open_orders/$', fetch_open_orders_views),

    url(r'^login/okex_api_key/$', OkexViews.api_key_views),
    url(r'^login/okex_fetch_history_ohlcv/$', OkexViews.fetch_history_ohlcv_views),




]
