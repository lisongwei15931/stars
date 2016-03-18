# -*- coding: utf-8 -*-


from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from stars.apps.customer.receiving_address.views import (receiving_address,
    receiving_address_add, receiving_address_update, receiving_address_set_default,
    receiving_address_delete, get_location)


urlpatterns = (
      url(r'^$', login_required(receiving_address), name='receiving_address'),
      url(r'^add/$', login_required(receiving_address_add),
          name='receiving_address_add'),
      url(r'^update/(?P<receiving_address_id>\d+)$',
          login_required(receiving_address_update), name='receiving_address_update'),
      url(r'^set-default/(?P<receiving_address_id>\d+)$',
          login_required(receiving_address_set_default),
          name='receiving_address_set_default'),
      url(r'^delete/(?P<receiving_address_id>\d+)$',
          login_required(receiving_address_delete), name='receiving_address_delete'),
      url(r'^get-location/$', login_required(get_location), name='get_location'),
)

