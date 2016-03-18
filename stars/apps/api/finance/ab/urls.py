# -*- coding: utf-8 -*-

from django.conf.urls import url

from stars.apps.api.finance.ab.views import AppAbSignInContractView, AppAbRescindContractView, AppAbRechargeView, \
    AppAbWithdrawView

urlpatterns = (
        url(r'^sign_in/$', AppAbSignInContractView.as_view(), name='api_fin-ab-sign_in'),

        url(r'^sign_out/$', AppAbRescindContractView.as_view(), name='api_fin-ab-sign_out'),

        url(r'^recharge/$', AppAbRechargeView.as_view(), name='api_fin-ab-recharge'),
        url(r'^withdraw/$', AppAbWithdrawView.as_view(), name='api_fin-ab-withdraw'),
)

