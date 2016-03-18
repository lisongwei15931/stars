# -*- coding: utf-8 -*-


from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from stars.apps.customer.stock.views import (stock, pickup_set, pickup_apply,
                                             add_pickup_addr, add_receiving_addr,
                                             pickup_store_check,
                                             pickup_quantity_set, pickup_success)


urlpatterns = (
      url(r'^$', login_required(stock), name='stock'),
      url(r'^pickup-set/$', login_required(pickup_set), name='pickup_set'),
      url(r'^pickup-quantity-set/$', login_required(pickup_quantity_set), name='pickup_quantity_set'),
      url(r'^pickup-store-check/$', login_required(pickup_store_check), name='pickup_store_check'),
      url(r'^pickup-apply/$', login_required(pickup_apply), name='pickup_apply'),
      url(r'^add-pickup-addr/$', login_required(add_pickup_addr), name='add_pickup_addr'),
      url(r'^add-receiving-addr/$', login_required(add_receiving_addr), name='add_receiving_addr'),
      url(r'^pickup-success/(?P<pickup_list_id>\d+)$', login_required(pickup_success), name='pickup_success'),
)

