# -*- coding: utf-8 -*-s
import datetime
import md5
import random
import string
import os,sys
import django
path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path[0:path.rfind('stars')])
os.environ['DJANGO_SETTINGS_MODULE'] = 'stars.settings'
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
user=User.objects.get(id=11)
keyWords = u"BZ"

# user = User.objects.get(id=11)
# product = Product.objects.get(id=151)
# user_product = UserProduct.objects.get_or_create(user=user,product=product,trade_type=1)[0]
# user_product.total += 1
# user_product.quantity += 1
# user_product.can_pickup_quantity += 1
# user_product.overage_unit_price = float(user_product.total/user_product.quantity)
#             user_product.need_repayment_quantity
#             user_product.need_repayment_amount
# user_product.custom_save()
ss = ['sdf','vsd']
print " ".join(ss)
print hash("实木组装摇椅")






