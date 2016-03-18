# -*- coding: utf-8 -*-s

import datetime
import hashlib
import random
import string
import traceback

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Min, Sum, Max
from django.http.response import HttpResponse, HttpResponseServerError
from oscar.core.loading import get_model

from stars.apps.tradingcenter.forms import CommissionBuyForm, CommissionSaleForm


Product = get_model('catalogue', 'product')
StockEnter = get_model('platform', 'StockEnter')
UserProduct = get_model('commission', 'UserProduct')


@transaction.atomic 
def stock_enter(request):
    if request.method == 'POST':
        try:
            product_id = request.POST.get('product', '')
            user = request.user
            product = Product.objects.get(id=product_id)
            quantity = request.POST.get('quantity', '')
            desc = request.POST.get('desc', '')
            stock_enter = StockEnter()
            stock_enter.product = product
            stock_enter.quantity = quantity
            stock_enter.user = user
            stock_enter.desc = desc
            stock_enter.save()
            try:
                user_product = UserProduct.objects.get(user=user,product=product,trade_type=2)
            except:
                user_product = UserProduct(user=user,product=product,trade_type=2)
            user_product.quantity += int(quantity)
            user_product.total_buy_quantity += int(quantity)
            user_product.can_pickup_quantity += int(quantity)
            user_product.total += int(quantity) * float(user_product.overage_unit_price)
            user_product.save()
            return HttpResponse('OK')
        except:
            return HttpResponseServerError(u'信息错误')
