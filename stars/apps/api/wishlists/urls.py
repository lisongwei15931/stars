# -*- coding: utf-8 -*-
from django.conf.urls import url

from stars.apps.api.wishlists.views import AppMyFavProduct, AppMyFavListView

urlpatterns = (
    url(r'^list/$', AppMyFavListView.as_view(), name='api-myfav-list'),
    url(r'product/(?P<product_pk>\d+)/$',  AppMyFavProduct.as_view(), name='api-myfav-product'),
)

