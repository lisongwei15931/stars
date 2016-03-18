# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

import ab.urls
import alipay.urls
import weixin.urls
from stars.apps.customer.finance.views import PayResultView

urlpatterns = (
    url(r'^ab/', include(ab.urls)),
    url(r'^wx/', include(weixin.urls)),
    url(r'^ali/', include(alipay.urls)),
    url(r'^pay/result/(?P<order_pk>\d+)/$', login_required(PayResultView.as_view()), name='finance-pay-result'),

)


