# -*- coding: utf-8 -*-s


from django.contrib.auth.models import User
from oscar.core.loading import get_model
from django.db import models


Product = get_model('catalogue', 'Product')


class SelfPick(models.Model):
    user = models.OneToOneField(User, related_name='self_pick_user', db_index=True,
                             verbose_name=u'用户')
    product = models.ManyToManyField(Product,related_name='self_pick_product',verbose_name=u'商品')
    class Meta:
        verbose_name = verbose_name_plural = u'自选列表'

    def __unicode__(self):
            return self.user.username
