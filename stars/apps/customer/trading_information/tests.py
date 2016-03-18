# -*- coding: utf-8 -*-s
import django 
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.test import TestCase
from oscar.core.loading import get_model
from wx.lib.calendar import BusCalDays
from wx import SASH_BOTTOM
import datetime

# Create your tests here.
django.setup()
TradeComplete = get_model('commission', 'TradeComplete')
PickupList = get_model('commission', 'PickupList')
pc = PickupList.objects.get(id=2)
print pc.order_pickup_list.all()



