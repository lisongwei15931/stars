# -*- coding: utf-8 -*-s

import datetime
import hashlib
import traceback
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import F
from django.db.models import Sum
from django.utils import timezone
from oscar.core.loading import get_model

from stars.apps.address.models import Province, City , District
from stars.apps.tradingcenter.tasks import PushTriggerTest


Product = get_model('catalogue', 'Product')
Category = get_model('catalogue','Category')
ReceivingAddress = get_model('address', 'ReceivingAddress')
pusher_trigger = PushTriggerTest()

COMMISSION_BUY_TYPE = (
        (1, '购买'),
        (2, '进货'),
    )
COMMISSION_SALE_TYPE = (
        (1, '出售'),
    )
TRADE_COMPLETE_TYPE = (
        (1, '购买'),
        (2, '进货'),
    )
SELF_PICK_OR_EXPRESS = (
        (1,'仅自提'),
        (2,'仅物流'),
        (3,'自提和物流'),
    )
COMMISSION_STATUS_CHOICES = (
        (1,'待成交'),
        (2,'部分成交'),
        (3,'成交'),
        (4,'撤单')
    )
COMMCAL_TYPEDATA_CHOICES = (
        (1,'定量'),
        (2,'比例')
    )
UD_STY_CHOICES = (
        (1,'定量'),
        (2,'比例')
    )
MONEY_CHANGE_TRADE_TYPE = (
        (1,'充值'),
        (2,'提现'),
        (3,'购买冻结'),
        (4,'购买解冻'),
        (5,'购买成交'),
        (6,'进货冻结'),
        (7,'进货解冻'),
        (8,'进货成交'),
        (9,'出售'),
        (10,'提货冻结'),
        (11,'提货驳回'),
        (12,'提货完成'),
        (13,'撤单'),
        (14,'闭市撤单'),
        (15,'手续费'),
    )
MONEY_CHANGE_STATUS = (
        (1,'进行中'),
        (2,'成功'),
        (3,'失败'),
    )
PICKUP_TYPE = (
        (1,'自提'),
        (2,'物流'),
    )
PICKUP_ADDR_TYPE = (
        (1,'自提'),
        (2,'自提点代运'),
        (3,'厂商发货'),
    )
PICKUP_DETAIL_STATUS = (
        (1,'未提货'),
        (2,'已提货'),
        (3,'已驳回'),
        (4,'未发货'),
        (5,'已发货'),
        (6,'已评价'),
    )
DEAL_FEE_TYPE = (
        (1, '购买'),
        (2, '出售'),
    )


class SystemConfig(models.Model):
    is_open = models.BooleanField(default=True, verbose_name=u'是否开市')
    auto_open = models.BooleanField(default=False, verbose_name=u'自动开市')
    bank_start_time = models.TimeField(verbose_name=u'银行开始时间')
    bank_end_time = models.TimeField(verbose_name=u'银行关闭时间')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'系统配置表'


class PickupAddr(models.Model):
    staff = models.ManyToManyField(
        User, related_name="pickup_addr_staff",
        blank=True, verbose_name=u'工作人员')
    category = models.CharField(max_length=1000, verbose_name=u'类型')
    name = models.CharField(max_length=200, verbose_name=u'名字')
    addr = models.CharField(default='', blank=True, null=True, max_length=200, verbose_name=u'地址')
    tel = models.CharField(max_length=30, verbose_name=u'电话')
    contact = models.CharField(default='', blank=True, null=True, max_length=200, verbose_name=u'联系人')
    province = models.ForeignKey(Province, blank=True, null=True, related_name='pickup_addr_province',
                                 verbose_name=u'省')
    city = models.ForeignKey(City, blank=True, null=True, related_name='pickup_addr_city',
                                 verbose_name=u'城市')
    district = models.ForeignKey(District,blank=True,null=True,related_name='pickup_addr_district',
                                 verbose_name=u'区/县')
    lat = models.FloatField(default=0, blank=True, null=True, max_length=15, verbose_name=u'纬度')
    lng = models.FloatField(default=0, blank=True, null=True, max_length=15, verbose_name=u'经度')
    desc = models.CharField(default='', blank=True, null=True, max_length=1000, verbose_name=u'备注')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'提货点表'

    def __unicode__(self):
            return self.name


class UserPickupAddr(models.Model):
    user = models.ForeignKey(User, related_name='user_pickup_addr_user', db_index=True,
                             verbose_name=u'用户')
    pickup_addr = models.ForeignKey(PickupAddr, related_name='user_pickup_addr',
                             verbose_name=u'自提点')
    is_default = models.BooleanField(default=False, verbose_name=u'是否默认')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'用户自提点表'

    def __unicode__(self):
            return self.user.username

    def save(self, *args, **kwargs):
        try:
            current_address = UserPickupAddr.objects.filter(user=self.user)
            current_address.get(is_default=True)
            if current_address and (self.is_default is True):
                current_address.update(is_default=False)
        except UserPickupAddr.DoesNotExist:
            pass
        except UserPickupAddr.MultipleObjectsReturned:
            current_address.exclude(id=self.id).update(is_default=False)
            self.is_default = True
        finally:
            super(UserPickupAddr, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_default:
            try:
                current_address = UserPickupAddr.objects.filter(user=self.user)
                if len(current_address) > 1:
                    new_default_address = current_address.exclude(id=self.id)[0]
                    new_default_address.is_default = True
                    new_default_address.save()
            except:
                pass
        super(UserPickupAddr, self).delete(*args, **kwargs)

class PickupList(models.Model):
    user = models.ForeignKey(User, related_name='pickup_list_user', db_index=True,
                             verbose_name=u'用户')
    pickup_no = models.CharField(blank=True, null=True, max_length=15, verbose_name=u'提货单号')
    pickup_type = models.IntegerField(choices=PICKUP_TYPE, verbose_name=u'提货类型')
    status = models.IntegerField(choices=PICKUP_DETAIL_STATUS, verbose_name=u'状态')
    # quantity = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'提货数量')
    pickup_fee = models.FloatField(blank=True, null=True, verbose_name=u'提货费用')
    express_fee = models.FloatField(blank=True, null=True, verbose_name=u'快递费用')
    user_picked_addr = models.ForeignKey(UserPickupAddr, blank=True, null=True, related_name='pickup_detail_pickup_addr',
                             verbose_name=u'用户自提点')
    user_address = models.ForeignKey(ReceivingAddress, blank=True, null=True, related_name='pickup_detail_user_addr',
                             verbose_name=u'用户收件地址')
    pickup_captcha = models.CharField(max_length=16, verbose_name=u'提货验证码')
    logistics_company = models.CharField(max_length=255, blank=True, null=True, verbose_name=u'物流公司')
    refuse_desc = models.CharField(blank=True, null=True, default='', max_length=1000, verbose_name=u'驳回原因')
    deal_datetime = models.DateTimeField(blank=True, null=True, verbose_name=u'办理日期')
    logistics_date = models.DateTimeField(blank=True, null=True, verbose_name=u'发货日期')
    deal_user = models.ForeignKey(User, related_name='deal_user', blank=True,
                                  null=True, verbose_name=u'办理人')
    created_date = models.DateField(auto_now_add=True, verbose_name=u'创建日期')
    created_time = models.TimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_date = models.DateField(auto_now=True, verbose_name=u'修改日期')
    modified_time = models.TimeField(auto_now=True, verbose_name=u'修改时间')


    class Meta:
        verbose_name = verbose_name_plural = u'提货单表'

    def __unicode__(self):
        return self.pickup_no

    def custom_save(self, *args, **kwargs):
        super(PickupList, self).save(*args, **kwargs)
        self.pickup_no = "P%08.f"%self.id
        self.pickup_captcha = str(hash(datetime.datetime.now()))[1:9]
        self.save()


class CommissionBuy(models.Model):
    commission_no = models.CharField(max_length=255, unique=True,
                                    verbose_name=u'委托编号')
    product = models.ForeignKey(Product, related_name='commission_buy_product', db_index=True,
                                 verbose_name=u'商品')
    user = models.ForeignKey(User, related_name='commission_buy_user',
                             verbose_name=u'用户')
    c_type = models.IntegerField(choices=COMMISSION_BUY_TYPE, verbose_name=u'类型')
    unit_price = models.FloatField(blank=True, null=True, db_index=True, verbose_name=u'单价')
    quantity = models.IntegerField(blank=True, null=True, verbose_name=u'数量')
    uncomplete_quantity = models.IntegerField(default=0, blank=True, null=True,
                                              verbose_name=u'未完成数量')
    status = models.IntegerField(choices=COMMISSION_STATUS_CHOICES, db_index=True, verbose_name=u'状态')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(auto_now=True, db_index=True,
                                             verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'委托买表'

    def __unicode__(self):
            return self.commission_no

    def custom_save(self, *args, **kwargs):
        super(CommissionBuy, self).save(*args, **kwargs)
        self.commission_no = "B%08.f"%self.id
        self.save()

class CommissionSale(models.Model):
    commission_no = models.CharField(max_length=255, unique=True,
                                    verbose_name=u'委托编号')
    product = models.ForeignKey(Product, related_name='commission_sale_product', db_index=True,
                                 verbose_name=u'商品')
    user = models.ForeignKey(User, related_name='commission_sale_user',
                             verbose_name=u'用户')
    c_type = models.IntegerField(choices=COMMISSION_SALE_TYPE,
        default=1, verbose_name=u'类型')
    unit_price = models.FloatField(blank=True, null=True, db_index=True, verbose_name=u'单价')
    quantity = models.IntegerField(blank=True, null=True, verbose_name=u'数量')
    uncomplete_quantity = models.IntegerField(blank=True, null=True,
                                              verbose_name=u'未完成数量')
    status = models.IntegerField(choices=COMMISSION_STATUS_CHOICES, db_index=True, verbose_name=u'状态')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(auto_now=True, db_index=True,
                                             verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'委托卖表'

    def __unicode__(self):
            return self.commission_no

    def custom_save(self, *args, **kwargs):
        super(CommissionSale, self).save(*args, **kwargs)
        self.commission_no = "S%08.f"%self.id
        self.save()

class TradeComplete(models.Model):
    trade_no = models.CharField(max_length=255, unique=True,
                                    verbose_name=u'成交编号')
    product = models.ForeignKey(Product, related_name='trade_complete_product', db_index=True,
                                verbose_name=u'商品')
    commission_buy_no = models.CharField(max_length=255, verbose_name=u'委托买编号')
    commission_sale_no = models.CharField(max_length=255, verbose_name=u'委托卖编号')
    commission_buy_user_id = models.ForeignKey(User, related_name='trade_complete_buy_user',
                             verbose_name=u'买方')
    commission_sale_user_id  = models.ForeignKey(User, related_name='trade_complete_sale_user',
                             verbose_name=u'卖方')
    c_type = models.IntegerField(choices=TRADE_COMPLETE_TYPE, verbose_name=u'类型',db_index=True)
    unit_price = models.FloatField(blank=True, null=True, verbose_name=u'成交单价')
    quantity = models.IntegerField(blank=True, null=True, verbose_name=u'成交数量')
    total = models.FloatField(blank=True, null=True, verbose_name=u'成交金额')
    commission_quantity = models.IntegerField(blank=True, null=True, verbose_name=u'委托数量')
    can_pickup_quantity = models.IntegerField(blank=True, null=True, verbose_name=u'可提取数量')
    created_date = models.DateField(auto_now_add=True, db_index=True, verbose_name=u'创建日期')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(auto_now=True, db_index=True,
                                             verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'成交表'

    def __unicode__(self):
            return self.trade_no

    def custom_save(self, *args, **kwargs):
        super(TradeComplete, self).save(*args, **kwargs)
        self.trade_no = "T%08.f"%self.id
        self.save()


class StockTicker(models.Model):
    product = models.ForeignKey(Product, related_name='stock_ticker_product', db_index=True,
                                verbose_name=u'商品')
    product_symbol = models.CharField(max_length=255, verbose_name=u'商品代码')
    product_name = models.CharField(max_length=255, verbose_name=u'商品名称')
    strike_price = models.FloatField(blank=True, null=True, verbose_name=u'成交价')
    net_change = models.FloatField(blank=True, null=True, verbose_name=u'涨跌')
    net_change_rise = models.FloatField(blank=True, null=True, verbose_name=u'涨跌幅')
    bid_price = models.FloatField(blank=True, null=True, verbose_name=u'买价')
    ask_price = models.FloatField(blank=True, null=True, verbose_name=u'卖价')
    bid_vol = models.IntegerField(blank=True, null=True, verbose_name=u'买量')
    ask_vol = models.IntegerField(blank=True, null=True, verbose_name=u'卖量')
    opening_price = models.FloatField(blank=True, null=True, verbose_name=u'开盘')
    closing_price = models.FloatField(blank=True, null=True, verbose_name=u'昨收')
    high = models.FloatField(blank=True, null=True, verbose_name=u'最高价')
    low = models.FloatField(blank=True, null=True, verbose_name=u'最低价')
    volume = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'成交量')
    total = models.FloatField(blank=True, null=True, verbose_name=u'成交金额')
    market_capitalization = models.FloatField(default=0, blank=True, null=True, max_length=15, verbose_name=u'市值')
    created_date = models.DateField(auto_now_add=True, db_index=True, verbose_name=u'创建日期')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(auto_now=True, db_index=True,
                                             verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'行情表'
        unique_together = ('product', 'created_date')

    def __unicode__(self):
            return self.product.get_title()


class CommissionBuyBackup(models.Model):
    commission_no = models.CharField(max_length=255, verbose_name=u'委托编号')
    product = models.ForeignKey(Product, related_name='commission_buy_buckup_product', db_index=True,
                                 verbose_name=u'商品')
    user = models.ForeignKey(User, related_name='commission_buy_buckup_user',
                             verbose_name=u'用户')
    c_type = models.IntegerField(choices=COMMISSION_BUY_TYPE, verbose_name=u'类型')
    unit_price = models.FloatField(blank=True, null=True, db_index=True, verbose_name=u'单价')
    quantity = models.IntegerField(blank=True, null=True, verbose_name=u'数量')
    uncomplete_quantity = models.IntegerField(blank=True, null=True,
                                              verbose_name=u'未完成数量')
    status = models.IntegerField(choices=COMMISSION_STATUS_CHOICES, db_index=True, verbose_name=u'状态')
    created_datetime = models.DateTimeField(verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(db_index=True, verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'委托买备份表'

    def __unicode__(self):
            return self.commission_no


class CommissionSaleBackup(models.Model):
    commission_no = models.CharField(max_length=255, verbose_name=u'委托编号')
    product = models.ForeignKey(Product, related_name='commission_sale_buckup_product', db_index=True,
                                 verbose_name=u'商品')
    user = models.ForeignKey(User, related_name='commission_sale_buckup_user',
                             verbose_name=u'用户')
    c_type = models.IntegerField(choices=COMMISSION_SALE_TYPE,
        default=1, verbose_name=u'类型')
    unit_price = models.FloatField(blank=True, null=True, db_index=True, verbose_name=u'单价')
    quantity = models.IntegerField(blank=True, null=True, verbose_name=u'数量')
    uncomplete_quantity = models.IntegerField(blank=True, null=True,
                                              verbose_name=u'未完成数量')
    status = models.IntegerField(choices=COMMISSION_STATUS_CHOICES, db_index=True, verbose_name=u'状态')
    created_datetime = models.DateTimeField(verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(db_index=True, verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'委托卖备份表'

    def __unicode__(self):
            return self.commission_no


class StockProductConfig(models.Model):
    product = models.OneToOneField(Product, related_name='stock_config_product',db_index=True,
                                verbose_name=u'商品')
    quote = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'进货权')
    max_buy_num = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'最大购买量')
    max_deal_num = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'最大进货量')
    self_pick_or_express = models.IntegerField(choices=SELF_PICK_OR_EXPRESS,default=1, verbose_name=u'自提或物流')
    max_num = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'用户持有总量')
    sale_num = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'发售量')
    opening_price = models.FloatField(default=0, blank=True, null=True, verbose_name=u'上市价格')
    trade_unit = models.CharField(default='',blank=True, null=True, max_length=15, verbose_name=u'交易单位')
    hold_users_limit = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'持有人数上限')
    min_pickup_num = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'最小提货量')
    min_price = models.FloatField(default=0, blank=True, null=True, verbose_name=u'最小变动价位')
    min_price_deddigit = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'小数位')
    min_bnum = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'最小买申报单位')
    min_snum = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'最小卖申报单位')
    once_max_num = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'单笔最大下单量')
    safefee_rate = models.FloatField(default=0, blank=True, null=True, verbose_name=u'日保险费标准')
    st_unit = models.CharField(default='', blank=True, null=True, max_length=15, verbose_name=u'仓储费计费单位')
    strate = models.FloatField(default=0, blank=True, null=True, verbose_name=u'仓储费率')
    pickup_bait = models.FloatField(default=0, blank=True, null=True, verbose_name=u'提取保障金(%)')
    pickup_rate = models.FloatField(default=0, blank=True, null=True, verbose_name=u'提货手续费')
    pack_rate = models.FloatField(default=0, blank=True, null=True, verbose_name=u'包装费率')
    depositfee_rate = models.FloatField(default=0, blank=True, null=True, verbose_name=u'托管费')
    mark_level = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'行情档位')
    close_price_time = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'收盘价计算时间')
    max_inc_rate = models.FloatField(default=0, blank=True, null=True, verbose_name=u'最大增持比例')
    max_dec_rate = models.FloatField(default=0, blank=True, null=True, verbose_name=u'最大减持比例')
    commcal_typedata = models.IntegerField(default=0, choices=COMMCAL_TYPEDATA_CHOICES, verbose_name=u'交易手续费类型')
    ud_sty = models.IntegerField(default=0, choices=UD_STY_CHOICES, verbose_name=u'涨跌计算类型')
    ud_up_range = models.FloatField(default=0, blank=True, null=True, max_length=15, verbose_name=u'涨幅参数')
    ud_down_range = models.FloatField(default=0, blank=True, null=True, max_length=15, verbose_name=u'跌幅参数')
    bcomm = models.FloatField(default=0, blank=True, null=True, max_length=15, verbose_name=u'买手续费参数')
    scomm = models.FloatField(default=0, blank=True, null=True, max_length=15, verbose_name=u'卖手续费参数')
    delay_fee_rate = models.FloatField(default=0, blank=True, null=True, max_length=15, verbose_name=u'延期补偿费率')
    youhuirage = models.FloatField(default=0, blank=True, null=True, max_length=15, verbose_name=u'待返比例')
    interest = models.FloatField(default=0, blank=True, null=True,max_length=15, verbose_name=u'委托费率')
    ower = models.ForeignKey(User, blank=True, null=True, related_name='stock_config_ower',verbose_name=u'发行交易商')
    market_capitalization = models.FloatField(default=0, blank=True, null=True, max_length=15, verbose_name=u'市值')
    pickup_price = models.FloatField(default=0, blank=True, null=True, verbose_name=u'提货费用')
    pickup_addr = models.ManyToManyField(PickupAddr, blank=True, related_name='stock_config_pickup_addr', verbose_name=u'提货点仓库')
    distribution_pickup_addr = models.ManyToManyField(PickupAddr, blank=True, related_name='stock_config_distribution_pickup_addr', verbose_name=u'铺货提货点仓库')
    checked_user = models.CharField(default='', blank=True, null=True, max_length=15, verbose_name=u'审批者')
    is_checked = models.BooleanField(default=False, verbose_name=u'是否审批')
    is_enable = models.BooleanField(default=False, verbose_name=u'是否上市')
    t_n = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'T+N参数')
    today_max_seal_num = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'当日最大卖量')
    desc = models.CharField(default='', blank=True, null=True, max_length=1000, verbose_name=u'备注')
    express_price = models.FloatField(default=0, blank=True, null=True, max_length=15, verbose_name=u'快递费用')
    created_date = models.DateField(auto_now_add=True, db_index=True, verbose_name=u'创建日期', )
    created_time = models.TimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_date = models.DateField(auto_now=True, verbose_name=u'修改日期')
    modified_time = models.TimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'商品配置表'

    def __unicode__(self):
            return self.product.title


class UserBank(models.Model):
    user = models.ForeignKey(User, related_name='bank_user', db_index=True,
                             verbose_name=u'用户')
    bank_name = models.CharField(max_length=255, verbose_name=u'银行名')
    bank_account = models.CharField(max_length=255, verbose_name=u'银行账号')
    tel = models.CharField(blank=True, null=True, max_length=30, verbose_name=u'电话')
    is_enable = models.BooleanField(default=False, verbose_name=u'是否启用')
    desc = models.CharField(default='', max_length=1000, verbose_name=u'备注')
    client_no = models.CharField(default='', max_length=100, verbose_name=u'银行客户号')
    is_rescinded = models.BooleanField(default=False, verbose_name=u'是否解约')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'用户银行卡表'

    def __unicode__(self):
            return self.user.username


class UserMoneyChange(models.Model):
    user = models.ForeignKey(User, related_name='money_chanage_user', db_index=True,
                             verbose_name=u'用户')
    trade_type = models.IntegerField(choices=MONEY_CHANGE_TRADE_TYPE, db_index=True, verbose_name=u'类型')
    status = models.IntegerField(choices=MONEY_CHANGE_STATUS, db_index=True, verbose_name=u'状态')
    price = models.FloatField(max_length=255, verbose_name=u'价格')
    product = models.ForeignKey(Product, blank=True, null=True, related_name='money_change_product', db_index=True,
                                verbose_name=u'商品')
    pickup_list = models.ForeignKey(PickupList, blank=True, null=True, verbose_name=u'提货单')
    parent_id = models.ForeignKey('self', blank=True, null=True, related_name='parent_money_chanage', verbose_name=u'父id')
    commission_buy_no = models.CharField(blank=True, null=True, max_length=255, verbose_name=u'委托买编号')
    commission_sale_no = models.CharField(blank=True, null=True, max_length=255, verbose_name=u'委托卖编号')
    commission_buy_unit_price = models.FloatField(blank=True, null=True, max_length=15, verbose_name=u'委托买价格')
    commission_sale_unit_price = models.FloatField(blank=True, null=True, max_length=15, verbose_name=u'委托卖价格')
    commission_buy_quantity = models.IntegerField(blank=True, null=True, verbose_name=u'委托买数量')
    commission_sale_quantity =models.IntegerField(blank=True, null=True, verbose_name=u'委托卖数量')
    trade_no = models.CharField(blank=True, null=True, max_length=255, verbose_name=u'成交编号')
    trade_unit_price = models.FloatField(blank=True, null=True, verbose_name=u'成交价格')
    trade_quantity = models.FloatField(blank=True, null=True, max_length=15, verbose_name=u'成交数量')
    cancel_quantity = models.FloatField(blank=True, null=True, max_length=15, verbose_name=u'撤单数量')
    cancel_unit_price = models.FloatField(blank=True, null=True, verbose_name=u'撤单单价')
    pickup_detail_id = models.CharField(blank=True, null=True, max_length=255, verbose_name=u'提货明细ID')
    pickup_amount = models.FloatField(blank=True, null=True, verbose_name=u'提货价格')
    money_bank_id = models.ForeignKey(UserBank, blank=True, null=True, related_name='money_chanage_bank', verbose_name=u'银行ID')
    money_bank = models.CharField(blank=True, null=True, max_length=255, verbose_name=u'银行')
    desc = models.CharField(default='', blank=True, null=True, max_length=1000, verbose_name=u'备注')
    created_date = models.DateField(auto_now_add=True, db_index=True, verbose_name=u'创建日期')
    created_time = models.TimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_date = models.DateField(auto_now=True, verbose_name=u'修改日期')
    modified_time = models.TimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'用户资产变化表'

    def __unicode__(self):
            return self.user.username
    @transaction.atomic
    def custom_save(self, *args, **kwargs):
        super(UserMoneyChange, self).save(*args, **kwargs)
        freezing_money = self.price
        today = datetime.datetime.today().date()
        #进货买货冻结
        if self.trade_type in [3,6]:
            # 余额变化
            user_balance = UserBalance.objects.get_or_create(user=self.user)[0]
            user_balance.balance = F('balance') - freezing_money
            user_balance.locked = F('locked') + freezing_money
            user_balance.save()
            #资产日报
            daily_report = UserAssetDailyReport.objects.get_or_create(user=self.user,target_date=today)[0]
            daily_report.locked = F('locked') + freezing_money
            daily_report.can_use_amount = F('can_use_amount') - freezing_money
            daily_report.end_balance = F('end_balance') - freezing_money
            daily_report.can_out_amount = F('can_out_amount') - freezing_money
            daily_report.save()
            if self.trade_type==6:
                user_product = UserProduct.objects.get_or_create(user=self.user,product=self.product,trade_type=1)[0]
                user_product.quote_quantity = F('quote_quantity') - float(self.commission_buy_quantity)
                user_product.save()
        #进货购买解冻
        elif self.trade_type in [4,7]:
            # 余额变化
            user_balance = UserBalance.objects.get_or_create(user=self.user)[0]
            user_balance.balance = F('balance') + freezing_money
            user_balance.locked = F('locked') - freezing_money
            user_balance.save()
            #资产日报
            daily_report = UserAssetDailyReport.objects.get_or_create(user=self.user,target_date=today)[0]
            daily_report.locked = F('locked') - freezing_money
            daily_report.can_use_amount = F('can_use_amount') + freezing_money
            daily_report.end_balance = F('end_balance') + freezing_money
            daily_report.can_out_amount = F('can_out_amount') + freezing_money
            daily_report.save()
        #进货购买成交
        elif self.trade_type in [5,8]:
            # 余额变化
            user_balance = UserBalance.objects.get_or_create(user=self.user)[0]
            user_balance.balance = F('balance') - freezing_money
            user_balance.save()
            #资产日报
            daily_report = UserAssetDailyReport.objects.get_or_create(user=self.user,target_date=today)[0]
            daily_report.expenditure = F('expenditure') + freezing_money
            daily_report.total = F('total') - freezing_money
            daily_report.can_use_amount = F('can_use_amount') - freezing_money
            daily_report.end_balance = F('end_balance') - freezing_money
            daily_report.can_out_amount = F('can_out_amount') - freezing_money
            daily_report.save()
            #用户持有
            if self.trade_type==5:
                product_config = StockProductConfig.objects.get_or_create(product=self.product)[0]
                user_product = UserProduct.objects.get_or_create(user=self.user,product=self.product,trade_type=1)[0]
                user_product.quote_quantity = F('quote_quantity') + self.trade_quantity*product_config.quote
            elif self.trade_type==8:
                user_product = UserProduct.objects.get_or_create(user=self.user,product=self.product,trade_type=2)[0]
                user_product.total_buy_quantity = F('total_buy_quantity') + self.trade_quantity
            print self.price,'@#!#$^@^#$^#$$#@'
            user_product.total = F('total') + self.price
            user_product.quantity = F('quantity') + self.trade_quantity
            user_product.can_pickup_quantity = F('can_pickup_quantity') + self.trade_quantity
            user_product.overage_unit_price = (F('total') + self.price)/F('quantity')
#             user_product.need_repayment_quantity
#             user_product.need_repayment_amount
            user_product.save()
        #出售成功
        elif self.trade_type == 9:
            # 余额变化
            user_balance = UserBalance.objects.get_or_create(user=self.user)[0]
            user_balance.balance = F('balance') + freezing_money
            user_balance.save()
            #资产日报
            daily_report = UserAssetDailyReport.objects.get_or_create(user=self.user,target_date=today)[0]
            daily_report.income = F('income') + freezing_money
            daily_report.end_balance = F('end_balance') + freezing_money
            daily_report.can_use_amount = F('can_use_amount') + freezing_money
            daily_report.can_out_amount = F('can_out_amount') + freezing_money
            daily_report.total = F('total') + freezing_money
            daily_report.save()
            #产品余量减少
            user_product = UserProduct.objects.get_or_create(user=self.user,product=self.product,trade_type=2)[0]
            user_product.quantity = F('quantity') - self.trade_quantity
            user_product.save()
        #卖手续费
        elif self.trade_type == 15:
            # 余额变化
            user_balance = UserBalance.objects.get_or_create(user=self.user)[0]
            user_balance.balance =F('balance') - self.price
            user_balance.save()
            #资产日报
            daily_report = UserAssetDailyReport.objects.get_or_create(user=self.user,target_date=today)[0]
            daily_report.can_use_amount = F('can_use_amount') - self.price
            daily_report.end_balance = F('end_balance') - self.price
            daily_report.can_out_amount = F('can_out_amount') - self.price
            daily_report.save()
        #撤单
        elif self.trade_type in [13,14]:
            # 余额变化
            user_balance = UserBalance.objects.get_or_create(user=self.user)[0]
            user_balance.balance = F('balance') + self.price
            user_balance.locked = F('locked') - self.price
            user_balance.save()
            #资产日报
            daily_report = UserAssetDailyReport.objects.get_or_create(user=self.user,target_date=today)[0]
            daily_report.locked = F('locked') - self.price
            daily_report.can_use_amount = F('can_use_amount') + self.price
            daily_report.end_balance = F('end_balance') + self.price
            daily_report.can_out_amount = F('can_out_amount') + self.price
            daily_report.save()

        # 提货冻结
        elif self.trade_type in [10]:
            # 余额变化
            user_balance = UserBalance.objects.get_or_create(user=self.user)[0]
            user_balance.balance = F('balance') - freezing_money
            user_balance.locked = F('locked') + freezing_money
            user_balance.save()
            #资产日报
            (daily_report, created) = UserAssetDailyReport.objects.get_or_create(user=self.user,target_date=today)
            if created:
                daily_report.locked = freezing_money
                daily_report.total = freezing_money
                daily_report.can_use_amount = freezing_money
                daily_report.end_balance = freezing_money
                daily_report.can_out_amount = freezing_money
            else:
                daily_report.locked = F('locked') + freezing_money
                daily_report.total = F('total') - freezing_money
                daily_report.can_use_amount = F('can_use_amount') - freezing_money
                daily_report.end_balance = F('end_balance') - freezing_money
                daily_report.can_out_amount = F('can_out_amount') - freezing_money
            daily_report.save()
            #用户持有，无法在这里做

        # 充值 by lwj 20151026
        elif self.trade_type == 1 and self.status == 2:
            num = self.price
            # 余额变化
            user_balance = UserBalance.objects.get(user=self.user)
            user_balance.balance = F('balance') + num
            user_balance.save()
            #资产日报
            daily_report = UserAssetDailyReport.objects.get_or_create(user=self.user,target_date=today)[0]
            daily_report.income = F('income') + num
            daily_report.can_use_amount = F('can_use_amount') + num
            daily_report.can_out_amount = F('can_out_amount') + num
            daily_report.total = F('total') + num
            daily_report.end_balance = F('end_balance') + num
            daily_report.save()

        # 提现 by lzy 20151104
        elif self.trade_type == 2:
            num = self.price
            # 余额变化
            user_balance = UserBalance.objects.get(user=self.user)
            user_balance.balance = F('balance') - num
            user_balance.save()
            #资产日报
            daily_report = UserAssetDailyReport.objects.get_or_create(user=self.user,target_date=today)[0]
            daily_report.expenditure = F('expenditure') + num
            daily_report.can_use_amount = F('can_use_amount') - num
            daily_report.can_out_amount = F('can_out_amount') - num
            daily_report.total = F('total') - num
            daily_report.end_balance = F('end_balance') - num
            daily_report.save()


class UserBalance(models.Model):
    user = models.OneToOneField(User, related_name='balance_user', db_index=True,
                             verbose_name=u'用户')
    balance = models.FloatField(default=0, blank=True, null=True, max_length=30, verbose_name=u'余额')
    locked = models.FloatField(default=0, blank=True, null=True, max_length=30, verbose_name=u'冻结')
    desc = models.CharField(default='', blank=True, null=True, max_length=1000, verbose_name=u'备注')
    created_date = models.DateField(auto_now_add=True, db_index=True, verbose_name=u'创建日期')
    created_time = models.TimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_date = models.DateField(auto_now=True, verbose_name=u'修改日期')
    modified_time = models.TimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'用户余额表'

    def __unicode__(self):
            return self.user.username

    def save(self, *args, **kwargs):
        super(UserBalance, self).save(*args, **kwargs)
#         from stars.apps.tradingcenter.views import push_user_money
#         push_user_money(self.user)


class PickupDetail(models.Model):
    pickup_list_id = models.ForeignKey(PickupList, related_name='pickup_lists_id', db_index=True,
                                verbose_name=u'提货单id')
    product = models.ForeignKey(Product, blank=True, null=True, related_name='pickup_detail_product', db_index=True,
                                verbose_name=u'商品')
    quantity = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'提货数量')
    unit_price = models.FloatField(blank=True, null=True, verbose_name=u'单价')
    pickup_fee = models.FloatField(blank=True, null=True, verbose_name=u'提货费用')
    pickup_type = models.IntegerField(choices=PICKUP_ADDR_TYPE, default=1, verbose_name=u'提货类型')
    status = models.IntegerField(default=4, choices=PICKUP_DETAIL_STATUS, verbose_name=u'状态')
    express_fee = models.FloatField(blank=True, null=True, verbose_name=u'快递费用')
    pickup_addr = models.ForeignKey(PickupAddr, blank=True, null=True, verbose_name=u'自提点')
    user_address = models.CharField(max_length=255, blank=True, null=True, verbose_name=u'用户收件地址')
    consignee = models.CharField(max_length=64, blank=True, null=True, verbose_name=u'收货人')
    mobile_phone = models.CharField(max_length=15,  blank=True, null=True, verbose_name=u'手机号码')
    pickup_captcha = models.CharField(max_length=16, blank=True, null=True, verbose_name=u'提货验证码')
    logistics_company = models.CharField(max_length=255, blank=True, null=True, verbose_name=u'物流公司')
    refuse_desc = models.CharField(blank=True, null=True, default='', max_length=1000, verbose_name=u'驳回原因')
    deal_datetime = models.DateTimeField(blank=True, null=True, verbose_name=u'办理日期')
    logistics_date = models.DateTimeField(blank=True, null=True, verbose_name=u'发货日期')
    deal_user = models.ForeignKey(User, related_name='pikcup_deal_user', blank=True,
                                  null=True, verbose_name=u'办理人')
    created_date = models.DateField(auto_now_add=True, verbose_name=u'创建日期')
    created_time = models.TimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_date = models.DateField(auto_now=True, verbose_name=u'修改日期')
    modified_time = models.TimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'提货明细表'

    def __unicode__(self):
        return self.product.title

    def save(self, *args, **kwargs):
        super(PickupDetail, self).save(*args, **kwargs)
        if self.status in [1, 3, 5]:
            self.pickup_list_id.status = self.status
            self.pickup_list_id.save()
        if self.status in [2, 6]:
            current_pickup_list = self.pickup_list_id
            all_pickup_detail = current_pickup_list.pickup_lists_id.all()
            if [self.status] == list(set(all_pickup_detail.values_list('status', flat=True))):
                current_pickup_list.status = self.status
                current_pickup_list.save()


class UserProduct(models.Model):
    user = models.ForeignKey(User, related_name='user_product_user', db_index=True,
                             verbose_name=u'用户')
    product = models.ForeignKey(Product, blank=True, null=True, related_name='user_product_product', db_index=True,
                                verbose_name=u'商品')
    trade_type = models.IntegerField(choices=COMMISSION_BUY_TYPE, verbose_name=u'类型')
    quantity = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'余量')
    can_pickup_quantity = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'可提量')
    overage_unit_price = models.FloatField(default=0, blank=True, null=True, verbose_name=u'均价')
    need_repayment_quantity = models.FloatField(blank=True, null=True, verbose_name=u'需要还款数量')
    need_repayment_amount = models.FloatField(blank=True, null=True, verbose_name=u'需要还款金额')
    quote_quantity = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'剩余进货权')
    total = models.FloatField(default=0, blank=True, null=True, verbose_name=u'总额')
    total_buy_quantity = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'总进货量')
    total_sale_quantity = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'总卖量')
    total_pickup_quantity = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'总提货量')
    created_date = models.DateField(auto_now_add=True, verbose_name=u'创建日期')
    created_time = models.TimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_date = models.DateField(auto_now=True, verbose_name=u'修改日期')
    modified_time = models.TimeField(auto_now=True, verbose_name=u'修改时间')

    def _get_strike_price(self):
        try:
            strike_price = float(self.product.strike_price)
        except:
            strike_price = 0
        return strike_price
    strike_price = property(_get_strike_price)

    def _get_total_price(self):
        try:
            total_price = F('quantity') * F('overage_unit_price')
            print total_price
        except:
            total_price = 0
        print 'return'
        return total_price
    total_price = property(_get_total_price)

    def _get_market_price(self):
        try:
            market_price = self.quantity * self.strike_price
        except:
            market_price = 0
        return market_price
    market_price = property(_get_market_price)

    def _get_added_value(self):
        try:
            added_value = self.market_price - self.total_price
        except:
            added_value = 0
        return added_value
    added_value = property(_get_added_value)

    def _get_added_value_ratio(self):
        try:
            added_value_ratio = round((self.added_value / self.total_price * 100), 2)
        except:
            added_value_ratio = round(0, 2)
        return added_value_ratio
    added_value_ratio = property(_get_added_value_ratio)
    
    def _can_sale_quantity(self):
        try:
            t_n = int(self.product.stock_config_product.t_n)-1
            today = datetime.datetime.now().date()
            start_day = today + datetime.timedelta(days=-t_n)
            try:
                can_not_sale_quantity = int(TradeComplete.objects.filter(c_type=2,commission_buy_user_id=self.user,product=self.product,created_date__range=(start_day,today)).aggregate(Sum('quantity')).get('quantity__sum'))
            except:
                can_not_sale_quantity = 0
            can_sale_quantity = int(self.total_buy_quantity) - can_not_sale_quantity - int(self.total_sale_quantity) - int(self.total_pickup_quantity)
        except:
            traceback.print_exc()
            can_sale_quantity = 0
        return can_sale_quantity
    can_sale_quantity = property(_can_sale_quantity)

    class Meta:
        verbose_name = verbose_name_plural = u'用户持有表'
        unique_together = ('user', 'product','trade_type')

    def __unicode__(self):
        return self.user.username


class UserAssetDailyReport(models.Model):
    user = models.ForeignKey(User, related_name='daily_report_user', db_index=True,
                             verbose_name=u'用户')
    target_date = models.DateField(blank=True, null=True,verbose_name=u'日期')
    start_balance = models.FloatField(default=0, blank=True, null=True, verbose_name=u'期初资金')
    income = models.FloatField(default=0, blank=True, null=True, verbose_name=u'当日收入')
    expenditure = models.FloatField(default=0, blank=True, null=True, verbose_name=u'当日支出')
    end_balance = models.FloatField(default=0, blank=True, null=True, verbose_name=u'期末资金')
    locked = models.FloatField(default=0, blank=True, null=True, verbose_name=u'冻结资金')
    can_use_amount = models.FloatField(default=0, blank=True, null=True, verbose_name=u'可用资金')
    can_out_amount = models.FloatField(default=0, blank=True, null=True, verbose_name=u'可出资金')
    profit_loss = models.FloatField(default=0, blank=True, null=True, verbose_name=u'浮动盈亏')
    market_capitalization = models.FloatField(default=0, blank=True, null=True, verbose_name=u'最新市值')
    total = models.FloatField(default=0, blank=True, null=True, verbose_name=u'资产总值')
    created_date = models.DateField(auto_now_add=True, verbose_name=u'创建日期')
    created_time = models.TimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_date = models.DateField(auto_now=True, verbose_name=u'修改日期')
    modified_time = models.TimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta:
        verbose_name = verbose_name_plural = u'用户资产日报表'
        unique_together = ('user', 'target_date')


    def __unicode__(self):
            return self.user.username

REPLAY_STATS=(
              ('1',u'未审核'),('2','已驳回'),('3',u'仓库已审核'),('4',u'已入库')
              )
class StoreInComeApply(models.Model):
    pickup = models.ManyToManyField(PickupAddr,related_name='pickupaddr_store',verbose_name=u'自提点')
    user = models.ForeignKey(User, related_name='user_store', db_index=True,
                            verbose_name=u'商家用户')
    #手工输入商品upc
    product = models.CharField(u'商品编号',max_length=100,)
    category = models.ForeignKey(Category,related_name='category_store',blank=True,null=True,verbose_name=u'商品大类')
    c_quantity = models.IntegerField(u'件数',default=1,)
    quantity = models.IntegerField(u'数量',default=1,)
    product_band = models.CharField(u'品牌',max_length=100,blank=True,null=True,)
    plan_income_date = models.DateField(u'计划入库日期',blank=True,null=True)
    apply_date = models.DateField(u'申请日期',auto_now_add=True,)
    tel = models.CharField(u'联系电话',max_length=100,blank=True,null=True,)
    desc = models.CharField(u'附属说明',max_length=300,blank=True,null=True,)
    status = models.CharField(u'批复状态',choices=REPLAY_STATS,default='1',max_length=2)
    deal_datetime = models.DateTimeField(u'批复时间',blank=True,null=True,)
    deal_user_id = models.ForeignKey(User, related_name='user_deal',
                             verbose_name=u'批复人',blank=True,null=True)
    refuse_desc = models.CharField(u'驳回原因',max_length=300,blank=True,null=True)
    create_datetime = models.DateTimeField(u'创建时间',auto_now_add=True,)
    modified_datetime = models.DateTimeField(u'修改时间',auto_now=True, )


    class Meta :
        verbose_name = verbose_name_plural = u'入库申请批复表'

    def __unicode__(self):
        return u'%s入库申请'%(self.product)


class UserPickupCity(models.Model):
    user = models.ForeignKey(User, related_name='pickup_city_user', db_index=True,
                             verbose_name=u'用户')
    product = models.ForeignKey(Product, blank=True, null=True, related_name='pickup_city_product', db_index=True,
                                verbose_name=u'商品')
    city = models.ManyToManyField(
        City, related_name="pickup_city",
        blank=True, verbose_name=u'城市')

    class Meta :
        verbose_name = verbose_name_plural = u'用户提货城市表'

    def __unicode__(self):
        return self.user.username
    

class DealFeeCollect(models.Model):
    buy_deal_fee = models.FloatField(default=0, blank=True, null=True, verbose_name=u'买手续费')
    sale_deal_fee = models.FloatField(default=0, blank=True, null=True, verbose_name=u'卖手续费')
    created_date = models.DateField(auto_now_add=True, verbose_name=u'创建日期')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(auto_now=True, db_index=True,
                                             verbose_name=u'修改时间')

class DealFeeDetail(models.Model):
    buy_user = models.ForeignKey(User, related_name='deal_fee_buy_user', db_index=True,
                            verbose_name=u'买家')
    sale_user = models.ForeignKey(User, related_name='deal_fee_sale_user', db_index=True,
                            verbose_name=u'卖家')
    product = models.ForeignKey(Product, blank=True, null=True, related_name='deal_fee_product', db_index=True,
                                verbose_name=u'商品')
    deal_fee_type = models.IntegerField(choices=DEAL_FEE_TYPE, verbose_name=u'手续费类型')
    deal_fee = models.FloatField(default=0, blank=True, null=True, verbose_name=u'手续费')
    trade_complete = models.ForeignKey(TradeComplete,blank=True, null=True, related_name='deal_fee_trade_complete', db_index=True,
                                verbose_name=u'成交单')
    created_date = models.DateField(auto_now_add=True, verbose_name=u'创建日期')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    modified_datetime = models.DateTimeField(auto_now=True, db_index=True,
                                             verbose_name=u'修改时间')

