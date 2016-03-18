# -*- coding: utf-8 -*-
from django.conf.urls import url

from stars.apps.api.finance.ali.views import AppAliPaymentView, AppAliOrderQueryPayStatusView

urlpatterns = (
    url(r'^payment/order/$', AppAliPaymentView.as_view(), name='api_fin-ali-payment_order'),
    url(r'^payment/result/$', AppAliOrderQueryPayStatusView.as_view(), name='api_fin-ali-payment_result'),
)

