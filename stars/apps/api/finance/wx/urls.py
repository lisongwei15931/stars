# -*- coding: utf-8 -*-

from django.conf.urls import url

from stars.apps.api.finance.wx.views import AppWxPaymentView, AppWxOrderQueryPayStatusView

urlpatterns = (
    url(r'^payment/order/$', AppWxPaymentView.as_view(), name='api_fin-wx-payment_order'),
    url(r'^payment/result/$', AppWxOrderQueryPayStatusView.as_view(), name='api_fin-wx-payment_result'),
)

