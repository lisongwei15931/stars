# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from stars.apps.customer.finance.weixin.views import WxPayHomeView, WxPayResultNotificationView, \
    WxOrderQueryPayStatusView, WxDownloadBillView

urlpatterns = (
      # url(r'^$',
      #     login_required(AbSignInOutContractHomeView.as_view()),
      #     name='finance-wx-pay'),
    url(r'^pay/$',
      login_required(WxPayHomeView.as_view()),
      name='finance-wx-pay_home'),
    url(r'^pay/result/notification/$',
      login_required(WxPayResultNotificationView.as_view()),
      name='finance-wx-result-notification'),

    url(r'^order/query/$',
      login_required(WxOrderQueryPayStatusView.as_view()),
      name='finance-wx-order-query'),

    url(r'^bill/download/$',
      login_required(WxDownloadBillView.as_view()),
      name='finance-wx-bill-download'),
)
