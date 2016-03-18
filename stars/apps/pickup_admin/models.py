# -*- coding: utf-8 -*-s


from django.db import models
from django.contrib.auth.models import User

from oscar.apps.partner.models import Partner

from stars.apps.commission.models import PickupAddr
from stars.apps.catalogue.models import Product


APPLY_STATUS = (
    ('0',u'待入库'),
    ('1', u'未审核'), ('2', u'已驳回'),
    ('4', u'已入库')
)

PICKUP_ADDR_TYPE = (
    ('1','自提'),
    ('2','自提点代运'),
)

class StoreInCome(models.Model):
    pickup_addr = models.ForeignKey(PickupAddr, verbose_name=u'提货点')
    isp = models.ForeignKey(Partner, verbose_name=u'交易商')
    product = models.ForeignKey(Product, verbose_name=u'商品')
    c_quantity = models.IntegerField(blank=True, null=True, verbose_name=u'件数')
    quantity = models.IntegerField(blank=True, null=True, verbose_name=u'数量')
    product_brand = models.CharField(max_length=128, blank=True, null=True,
                                     verbose_name=u'商品品牌')
    product_company = models.CharField(max_length=128, blank=True, null=True,
                                       verbose_name=u'商品生产厂家')
    place_of_origin = models.CharField(max_length=128, blank=True, null=True,
                                       verbose_name=u'商品产地')
    producttion_date = models.DateField(blank=True, null=True,
                                        verbose_name=u'商品生产日期')
    warehouse_rental_start_time = models.DateField(blank=True, null=True,
                                    verbose_name=u'仓租开始日期')
    place = models.CharField(max_length=32, blank=True, null=True,
                             verbose_name=u'库位')
    les_space = models.CharField(max_length=32, blank=True, null=True,
                                 verbose_name=u'仓位')
    inspect_orig = models.CharField(max_length=128, blank=True, null=True,
                                    verbose_name=u'检测机构')
    inspect_cert = models.CharField(max_length=64, blank=True, null=True,
                                    verbose_name=u'质检证书编号')
    inspect_expert = models.CharField(max_length=64, blank=True, null=True,
                                      verbose_name=u'质检专家')
    vouch_company = models.CharField(max_length=128, blank=True, null=True,
                                     verbose_name=u'保险公司')
    desc = models.CharField(max_length=256, blank=True, null=True,
                            verbose_name=u'备注')
    income_date = models.DateField(auto_now_add=True, verbose_name=u'入库日期')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'仓库入库表'


class PickupStore(models.Model):
    pickup_addr = models.ForeignKey(PickupAddr, verbose_name=u'提货点')
    product = models.ForeignKey(Product, verbose_name=u'商品')
    quantity = models.IntegerField(default=0, blank=True, null=True,
                                   verbose_name=u'数量')
    locked_quantity = models.IntegerField(default=0, blank=True, null=True,
                                          verbose_name=u'冻结数量')
    desc = models.CharField(max_length=256, blank=True, null=True,
                            verbose_name=u'备注')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta:
        unique_together = ('pickup_addr', 'product')
        verbose_name = verbose_name_plural = u'库存表'


class StoreInComeApply(models.Model):
    applyid = models.CharField(u'货单编号',blank=True,null=True,max_length=30)
    pickup_addr = models.ForeignKey(PickupAddr, verbose_name=u'提货点')
    isp = models.ForeignKey(Partner, verbose_name=u'交易商')
    product = models.ForeignKey(Product, verbose_name=u'商品')
    c_quantity = models.IntegerField(blank=True, null=True, verbose_name=u'发货件数')
    quantity = models.IntegerField(blank=True, null=True, verbose_name=u'发货数量')
    damaged_quantity = models.IntegerField(default=0, blank=True, null=True,verbose_name = u'破损数量')
    lose_quantity = models.IntegerField(default=0, blank=True, null=True,verbose_name=u'丢失数量')
    in_quantity = models.IntegerField(blank=True, null=True, verbose_name=u'入库数量')
    product_brand = models.CharField(max_length=128, blank=True, null=True,
                                     verbose_name=u'商品品牌')
    plan_income_date = models.DateField(blank=True, null=True,
                                        verbose_name=u'计划入库日期')
    apply_date = models.DateField(auto_now_add=True,blank=True, null=True,
                                  verbose_name=u'申请日期')
    telephone = models.CharField(max_length=32, verbose_name=u'联系电话')
    desc = models.CharField(max_length=256, blank=True, null=True,
                            verbose_name=u'备注')
    status = models.CharField(max_length=16, default='0', choices=APPLY_STATUS, verbose_name=u'批复状态')
    deal_datetime = models.DateTimeField(blank=True, null=True, verbose_name=u'批复时间')
    deal_user = models.ForeignKey(User, blank=True, null=True, verbose_name=u'批复人')
    refuse_desc = models.CharField(max_length=256, blank=True, null=True,
                                   verbose_name=u'驳回原因')

    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')

    def _income_quantity(self):
        try:
            income_quantity = self.quantity - self.damaged_quantity - self.lose_quantity
            return income_quantity
        except:
            return 0
    income_quantity = property(_income_quantity)

    class Meta:
        verbose_name = verbose_name_plural = u'入库申请批复表'

    def applysave(self, *args, **kwargs):
        super(StoreInComeApply, self).save(*args, **kwargs)
        self.applyid = "AP%08.d"%self.id
        self.save()

    def save(self, *args, **kwargs):
        if self.quantity:
            self.in_quantity = self.quantity - self.damaged_quantity - self.lose_quantity
        super(StoreInComeApply, self).save(*args, **kwargs)


class PickupStatistics(models.Model):
    pickup_addr = models.ForeignKey(PickupAddr, verbose_name=u'提货点')
    product = models.ForeignKey(Product, verbose_name=u'商品')
    quantity = models.IntegerField(blank=True, null=True, verbose_name=u'数量', default=0)
    pickup_type = models.IntegerField(choices=PICKUP_ADDR_TYPE, default='1', verbose_name=u'提货类型')

    class Meta:
        verbose_name = verbose_name_plural = u'提货统计表'
        unique_together = ('pickup_addr', 'product', 'pickup_type')
