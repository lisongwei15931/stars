# -*- coding: utf-8 -*-s
from django.contrib.auth.models import User
from django.db import models
from oscar.core.loading import get_model
from datetime import date


Product = get_model('catalogue', 'Product')

ENTER_STATUS = (
    ('1', u'待审核'), ('2', u'已驳回'), ('3', u'已通过')
)


class StockEnter(models.Model):
    stockid = models.CharField(u'商家入库单',blank=True,null=True,max_length=25)
    user = models.ForeignKey(User, related_name='stock_enter_user', db_index=True,
                             verbose_name=u'用户')
    product = models.ForeignKey(Product, related_name='stock_enter_product', db_index=True,
                                 verbose_name=u'商品')
    quantity = models.IntegerField(blank=True, null=True, verbose_name=u'数量')
    number = models.IntegerField(blank=True, null=True, verbose_name=u'件量')
    desc = models.CharField(default='', blank=True, null=True, max_length=1000, verbose_name=u'备注')
    status = models.CharField(max_length=16, default='1', choices=ENTER_STATUS, verbose_name=u'状态')
    refuse_desc = models.CharField(max_length=256, blank=True, null=True,
                                   verbose_name=u'驳回原因')
    deal_datetime = models.DateTimeField(blank=True, null=True, verbose_name=u'批复时间')
    deal_user = models.ForeignKey(User, blank=True, null=True, verbose_name=u'批复人')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(auto_now=True, db_index=True,
                                             verbose_name=u'修改时间')
    class Meta:
        verbose_name = verbose_name_plural = u'库转交易表'

    def __unicode__(self):
            return self.user.username

    def stocksave(self,*args,**kwargs):
        super(StockEnter,self).save(*args,**kwargs)
        current_date = date.today().strftime('%Y%m%d')
        self.stockid = '%s%08.d'%(current_date,self.id)
        self.save()

