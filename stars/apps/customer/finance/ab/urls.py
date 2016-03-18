# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from stars.apps.customer.finance.ab.ab_server import start_ab_server
from stars.apps.customer.finance.ab.views import AbSignInOutContractHomeView, AbSignInContractView, \
    AbRescindContractView, MobileVerificationCodeForRescindAbBankView, RechargeView, WithDrawView

start_ab_server()

urlpatterns = (
      url(r'^$',
          login_required(AbSignInOutContractHomeView.as_view()),
          name='finance-ab-sign_in_out_home'),
      url(r'^signIn/$',
          login_required(AbSignInContractView.as_view()),
          name='finance-ab-sign_in_contract'),
      url(r'^rescind/$',
          login_required(AbRescindContractView.as_view()),
          name='finance-ab-rescind_contract'),
      url(r'^rescind/vcode/$',
          login_required(MobileVerificationCodeForRescindAbBankView.as_view()),
          name='finance-ab-rescind_contract_vcode'),

      url(r'^recharge/$',
        login_required(RechargeView.as_view()),
        name='finance-ab-recharge'),
      url(r'^withdraw/$',
        login_required(WithDrawView.as_view()),
        name='finance-ab-withdraw'),

      # url(r'^signIn/successful$',
      #     login_required(AbSignInOutContractHomeView.as_view()),
      #     name='finance-ab-sign_in_contract'),
)

