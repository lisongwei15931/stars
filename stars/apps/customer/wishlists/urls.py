# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from oscar.core.loading import get_class
from stars.apps.customer.wishlists.views import MyFavRemoveProductListView

fav_add_product_view = get_class('customer.wishlists.views', 'MyFavAddProduct')
fav_list_view = get_class('customer.wishlists.views', 'MyFavListView')
fav_remove_product_view = get_class('customer.wishlists.views', 'MyFavRemoveProduct')

urlpatterns = (
    url(r'^$',
        login_required(fav_list_view.as_view()),
        name='myfav-list'),
    url(r'products/(?P<product_pk>\d+)/add/$',
        login_required(fav_add_product_view.as_view()),
        name='myfav-add-product'),

    url(r'products/(?P<product_pk>\d+)/delete/$',
        login_required(fav_remove_product_view.as_view()),
        name='myfav-remove-product'),

    url(r'products/delete/$',
        login_required(MyFavRemoveProductListView.as_view()),
        name='myfav-remove-product-list'),
)

