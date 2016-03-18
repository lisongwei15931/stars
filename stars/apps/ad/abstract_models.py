# encoding: utf-8

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse


@python_2_unicode_compatible
class AbstractRollingAd(models.Model):
    """
    轮播广告
    """
    POSTION_CHOICES=(('home_ad', '主页轮播'),
                     ('home_ad_1', '主页新品'),
                     ('home_ad_2', '主页口碑'),
                     ('home_ad_3', '主页主推'),
                     ('home_ad_4', '主页火热'),
                     ('mobile_home_carousel', u'移动端主页轮播'),
                     ('other', '其他'))
    id = models.AutoField(primary_key=True)
    title = models.CharField(_('标题'.decode('utf-8')), max_length=128)
    link_url = models.CharField(_('链接地址'.decode('utf-8')), max_length=128)
    position = models.CharField(_('广告位置'.decode('utf-8')), choices=POSTION_CHOICES, max_length=30)
    image = models.ImageField(_("Image"), upload_to=settings.OSCAR_IMAGE_FOLDER, max_length=255)
    description = models.TextField(_('Description'), default='', max_length=255)
    order_num = models.PositiveIntegerField(_('顺序号'.decode('utf-8')), default=0)
    valid = models.BooleanField(_('启用'.decode('utf-8')), default=True)


    class Meta:
        abstract = True
        app_label = 'ad'
        ordering = ['order_num', 'id']
        verbose_name = _('Rolling advertisement')


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Our URL scheme means we have to look up the category's ancestors. As
        that is a bit more expensive, we cache the generated URL. That is
        safe even for a stale cache, as the default implementation of
        ProductCategoryView does the lookup via primary key anyway. But if
        you change that logic, you'll have to reconsider the caching
        approach.
        """
        cache_key = 'ROLLING_AD_URL_%s' % self.pk
        url = cache.get(cache_key)
        if not url:
            url = reverse(
                'dashboard:ad-rolling_ad-detail',
                kwargs={'pk': self.pk})
            cache.set(cache_key, url)
        return url


