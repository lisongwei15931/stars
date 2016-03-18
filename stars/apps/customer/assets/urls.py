# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from oscar.core.loading import get_class
from stars.apps.customer.assets.bank_card_views import BankCardListView, AddBankCardView
from stars.apps.customer.assets.views import get_user_income

assets_view = get_class('customer.assets.views', 'AssetsView')


urlpatterns = (
      url(r'^$',
        login_required(assets_view.as_view()),
        name='assets'),
      url(r'^bankcard/$',
        login_required(BankCardListView.as_view()),
        name='assets-bank_card_list'),
      url(r'^bankcard/add/$',
        login_required(AddBankCardView.as_view()),
        name='assets-add_bank_card'),

      url(r'^getuserincome/$',get_user_income,name = 'getuserincome'),

)

