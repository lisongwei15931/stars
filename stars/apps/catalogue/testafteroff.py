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
django.setup()
 
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue') 
ProductAttribute = get_model('catalogue', 'ProductAttribute') 
ProductGroup = get_model('catalogue', 'ProductGroup') 
attr = ProductAttribute.objects.get(id = 32)
group_attr_value = ProductAttributeValue.objects.filter(attribute=attr)
Province = get_model('address', 'Province')
Product = get_model('catalogue', 'Product')
City = get_model('address', 'City')
# for attr_value in group_attr_value:
#     print attr_value.value_text
product = Product.objects.get(id=151)
# print product.recommended_products.filter().order_by('-browse_num')[:5]
# city = City.objects.get(id=376)
# all_city = []
# all_pickup_addr = product.stock_config_product.distribution_pickup_addr.all()
# for pickup_addr in all_pickup_addr:
#     all_city.append(pickup_addr.city)
# print city in all_city
# print product.stock_config_product.scomm
# print "%.2f"%float(float(50.5)-float(50.5)/100*product.stock_config_product.scomm)
print 1 + 5 * 9







