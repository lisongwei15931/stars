# -*- coding: utf-8 -*-


from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from stars.apps.customer.trading_information.views import trading_infomation, \
    today_trading, today_untrading, cancel_order, pickup_detail, \
    pickup_detail_update, cancel_commission, PickupDetailListView, \
    order_manage, order_detail

urlpatterns = (
      url(r'^$', login_required(trading_infomation), name='trading_information'),
      url(r'^order-manage$', login_required(order_manage), name='order_manage'),
      url(r'^order-detail/$', login_required(order_detail), name='order_detail'),
      url(r'^today-trading$', login_required(today_trading), name='today_trading'),
      url(r'^today-untrading$', login_required(today_untrading), name='today_untrading'),
      url(r'^cancel-order$', login_required(cancel_order), name='cancel_order'),
      url(r'^pickup-detail/$', login_required(pickup_detail), name='pickup_detail'),
      url(r'^pickup-detail/update/(?P<pickup_list_id>\d+)/$', login_required(pickup_detail_update), name='pickup_detail_update'),
      url(r'^pickup-detail/list/(?P<pk>\d+)/$', login_required(PickupDetailListView.as_view()), name='pickup_detail-list'),
      url(r'^cancel-commission$', login_required(cancel_commission), name='cancel_commission'),
)

