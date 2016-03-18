# -*- coding: utf-8 -*-s

from django.db import models

from django.contrib.auth.models import User
from oscar.core.loading import get_model

from stars.apps.address.models import Province, City
from stars.apps.commission.models import StockProductConfig


Product = get_model('catalogue', 'Product')


PICKUP_TYPE = (
    (1, '购买'),
    (2, '进货'),
    (3, '全部'),
)


class PickupProvisionalRecord(models.Model):
    user = models.ForeignKey(User, verbose_name=u'用户')
    product = models.ForeignKey(Product, verbose_name=u'商品')
    quantity = models.IntegerField(default=1, verbose_name=u'提货数量')
    max_quantity = models.IntegerField(verbose_name=u'货物余量')
    available = models.BooleanField(default=False, verbose_name=u'是否可用')
    pickup_type = models.IntegerField(default=1,
                                      choices=PICKUP_TYPE, verbose_name=u'提货类型')

    def _get_pickup_price(self):
        try:
            current_product_config = StockProductConfig.objects.filter(product=self.product)[0]
            pickup_price = current_product_config.pickup_price
        except:
            pickup_price = 0
        return pickup_price
    pickup_price = property(_get_pickup_price)

    def _get_express_price(self):
        try:
            current_product_config = StockProductConfig.objects.filter(product=self.product)[0]
            express_price = current_product_config.express_price
        except:
            express_price = 0
        return express_price
    express_price = property(_get_express_price)

    class Meta:
        verbose_name = verbose_name_plural = u'提货临时记录'
        unique_together = ('user', 'product')

    def __unicode__(self):
        return self.user.username
