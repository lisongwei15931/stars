# -*- coding: utf-8 -*-s

from django.db import models

# from oscar.apps.basket.models import Line as CoreLine
from oscar.apps.basket.abstract_models import AbstractLine


class Line(AbstractLine):
    buy_price = models.DecimalField(verbose_name=u'买入价',
            decimal_places=2, max_digits=12, blank=True, null=True)

    @property
    def quote(self):
        quote = self.product.quote * self.quantity
        return quote

    @property
    def total_price(self):
        try:
            total_price = float(self.buy_price * self.quantity)
        except:
            total_price = 0
        return total_price

    def save(self, *args, **kwargs):
        if not self.buy_price:
            self.buy_price = self.product.buy_price
        return super(Line, self).save(*args, **kwargs)
    
    def refresh_buy_price(self):
        self.buy_price = self.product.buy_price
        super(Line, self).save()


from oscar.apps.basket.models import *  # noqa
