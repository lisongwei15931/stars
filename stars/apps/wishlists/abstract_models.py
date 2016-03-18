import hashlib
import random
from django.utils import six

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from django.core.urlresolvers import reverse

from oscar.core.compat import AUTH_USER_MODEL

@python_2_unicode_compatible
class AbstractLine(models.Model):
    """
    One entry in a wish list. Similar to order lines or basket lines.
    """
    wishlist = models.ForeignKey('wishlists.WishList', related_name='lines',
                                 verbose_name=_('Wish List'))
    product = models.ForeignKey(
        'catalogue.Product', verbose_name=_('Product'),
        related_name='wishlists_lines', on_delete=models.SET_NULL,
        blank=True, null=True)
    # quantity = models.PositiveIntegerField(_('Quantity'), default=1)
    #: Store the title in case product gets deleted
    title = models.CharField(pgettext_lazy(u"Product title", u"Title"), max_length=255)

    def __str__(self):
        return u'%sx %s on %s' % (self.title, self.wishlist.name)

    def get_title(self):
        if self.product:
            return self.product.get_title()
        else:
            return self.title

    class Meta:
        abstract = True
        app_label = 'wishlists'
        unique_together = (('wishlist', 'product'), )
        verbose_name = _('Wish list line')
