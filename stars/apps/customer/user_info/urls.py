# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from stars.apps.customer.user_info.views import UserInfoView

urlpatterns = (
      url(r'^$',
        login_required(UserInfoView.as_view()),
        name='user_info'),

)

