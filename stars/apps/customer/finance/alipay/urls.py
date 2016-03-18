# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from stars.apps.customer.finance.alipay.views import  AliPayResultNotificationView, \
     AliPayResultReturnView, AliPayResultErrorNotificationView, TestHomeView, AliPayView

urlpatterns = (

    url(r'^pay/result/notification/$',
      login_required(AliPayResultNotificationView.as_view()),
      name='finance-alipay-result-notification'),
    url(r'^pay/result/return/$',
      login_required(AliPayResultReturnView.as_view()),
      name='finance-alipay-return'),
    url(r'^pay/result/error/notification/$',
      login_required(AliPayResultErrorNotificationView.as_view()),
      name='finance-alipay-result-error-notification'),

    url(r'^pay/$',
      login_required(AliPayView.as_view()),
      name='finance-alipay-pay'),

    url(r'^pay/test/$',
      login_required(TestHomeView.as_view()),
      name='finance-alipay-test'),
    #   login_required(AliPayOrderQueryPayStatusView.as_view()),
    #   name='finance-alipay-order-query'),

    # url(r'^bill/download/$',
    #   login_required(AliPayDownloadBillView.as_view()),
    #   name='finance-alipay-bill-download'),
)
