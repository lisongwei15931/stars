# -*- coding: utf-8 -*-s

import django
from django.contrib.auth.models import User
from oscar.core.loading import get_model

django.setup()
Product = get_model('catalogue', 'Product')
SelfPick = get_model('tradingcenter', 'SelfPick') 
 
user = User.objects.get(id=1)
product = Product.objects.get(id=143)
# ss = SelfPick.objects.get_or_create(user=user)[0]
# ss.product.add(product)
# ss.product.remove(product)
# print ss.product.filter(is_on_shelves=True)
print product.price_range






