# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from oscar.core.compat import AUTH_USER_MODEL
from oscar.apps.wishlists.abstract_models import AbstractWishList

class WishList(AbstractWishList):
    # owner = models.OneToOneField(AUTH_USER_MODEL, related_name='wishlists',
    #                       verbose_name=_('Owner'))
    # name = models.CharField(verbose_name=_('Name'), default=u'我的关注',
    #                         max_length=255)

    def __str__(self):
        return u"%s's Wish List '%s'" % (self.owner, u'我的关注')

    def save(self, *args, **kwargs):
        if not self.pk or kwargs.get('force_insert', False):
            self.key = self.owner.pk
            self.name = u'我的关注'
        super(self.__class__, self).save(*args, **kwargs)

    def add(self, product):
        """
        Add a product to this wishlist
        """
        lines = self.lines.filter(product=product)
        if len(lines) == 0:
            self.lines.create(
                product=product, title=product.get_title())
        else:
            line = lines[0]
            line.save()



from oscar.apps.wishlists.abstract_models import AbstractLine

class Line(AbstractLine):
    date_created = models.DateTimeField(verbose_name=_(u'收藏时间'), auto_now_add=True, editable=False)

    class Meta:
        verbose_name = _(u'我的关注')


from oscar.apps.wishlists.models import *