# -*- coding: utf-8 -*-s
import datetime
import md5
import random
import string

import django
from django.contrib.auth.models import User
from django.db.models import Max
from oscar.core.loading import get_model
from django.db.models.lookups import IsNull
from django.db.models import Min, Sum, Max
from django.db.models.query_utils import Q
from django.db.models import F
django.setup()
 
CommissionSale = get_model('commission', 'CommissionSale')
CommissionBuy = get_model('commission', 'CommissionBuy')
CommissionBuyBackup = get_model('commission', 'CommissionBuyBackup')
TradeComplete = get_model('commission', 'TradeComplete')
StockTicker = get_model('commission', 'StockTicker')
Product = get_model('catalogue', 'product')
UserProduct = get_model('commission', 'UserProduct') 
Category = get_model('catalogue', 'Category')
UserBalance = get_model('commission', 'UserBalance') 
# user=User.objects.get(id=11)
keyWords = u"BZ"
# all_cate = Category.objects.filter(depth=1)
# for cate in all_cate:
#     print cate
#     print cate.get_category_products()
# today = datetime.datetime.now().date()
# d = 5-1
# d3 = today + datetime.timedelta(days=-d)
# dd = TradeComplete.objects.filter(created_date__range=(d3,today))
# print dd

# udp = UserProduct.objects.get(id=55)
# udp.total = F('total') + 1
# udp.save()
# print 'fwefeew'
user = User.objects.get(id=13)
# product = Product.objects.get(id=2)
# user_product = UserProduct.objects.get_or_create(user=user,product=product,trade_type=1)[0]
# user_product.quantity = 1
# user_product.total = 1
# user_product.overage_unit_price = 1

# user_product.quantity = F('quantity') + 5
# user_product.overage_unit_price = (F('total') + 1)/F('quantity')
# user_product.total = F('quantity') * ((F('total') + 1)/F('quantity'))
# user_product.custom_save()


# user_product.total = F('total') + 1
# user_product.quantity = F('quantity') + 1
# user_product.overage_unit_price = F('total')/F('quantity')
# user_product.custom_save()
ub = UserBalance()
ub.user=user
ub.save()
from django.db import connection
for sql in connection.queries:
    print sql['sql'],';'

# 
# ub = UserBalance.objects.get(id=38)
# print ub.balance

# print Product.objects.filter(opening_date__lte=datetime.datetime.now().date())





