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
CommissionBuy = get_model('commission', 'CommissionBuy')
today = datetime.datetime.now().date()
user = User.objects.get(id=1)
Product = get_model('catalogue', 'product')
ProductOrder = get_model('commission', 'ProductOrder')
# commission_buy_list = CommissionBuy.objects.filter(user=user,status__in=[1,2],created_datetime__year=today.year,created_datetime__month=today.month)
# print commission_buy_list
# starttime = "2016-01-11"
# po = ProductOrder.objects.filter(created_datetime__gt=starttime)
# for p in po:
#     print p.created_datetime
    
STATUS_CHOICES = ((0, u'未支付'), (1, u'支付中'), (2, u'支付成功'),
                      (3, u'支付失败'), (4, u'已关闭'), (5, u'已撤销'), (6, u'未发货'), (7, u'已发货'), (8, u'部分提货'), (9, u'已提货'))
iii = 5
print STATUS_CHOICES[iii][1]



