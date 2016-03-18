# -*- coding: utf-8 -*-s

import os
import traceback
from django.db import models
from django.contrib.staticfiles.finders import find
from django.db.models.manager import Manager
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum
from oscar.apps.catalogue.abstract_models import (AbstractProduct,AbstractCategory,AbstractProductAttribute,
                                                  ProductAttributesContainer as CoreProductAttributesContainer)
from django.utils import timezone
from oscar.core.loading import get_model

from oscar.apps.catalogue.abstract_models import MissingProductImage as mpi
from oscar.core.compat import get_user_model


User = get_user_model()
WishLine = get_model('wishlists', 'Line')

class MissingProductImage(mpi):
    def symlink_missing_image(self, media_file_path):
        import platform
        if platform.system() in ['Windows']:
            static_file_path = find('oscar/img/%s' % self.name)
            if static_file_path is not None:
                if not os.path.exists(media_file_path):
                    open(media_file_path, "wb").write(open(static_file_path, "rb").read())
        else:
            return super(MissingProductImage, self).symlink_missing_image(self, media_file_path)


class MPProductAttributesContainer(CoreProductAttributesContainer):
    def __getattr__(self, name):
        if not name.startswith('_') and not self.initialised:
            values = self.get_values().select_related('attribute')
            for v in values:
                if isinstance(v.value, Manager):
                    setattr(self, v.attribute.code, v.value.all())
                else:
                    setattr(self, v.attribute.code, v.value)
            self.initialised = True
            return getattr(self, name)
        raise AttributeError(
            _("%(obj)s has no attribute named '%(attr)s'") % {
                'obj': self.product.get_product_class(), 'attr': name})


class Product(AbstractProduct):
    browse_num = models.BigIntegerField(default=0, verbose_name=u'浏览次数')
    is_on_shelves = models.BooleanField(default=True, verbose_name=u'是否上架')
    selection_reputation = models.BooleanField(default=False, verbose_name=u'口碑甄选')
    opening_date = models.DateField(default=timezone.now, verbose_name=u'上市时间')
    new_listing = models.BooleanField(default=False, verbose_name=u'新品上市')
    featured_hot = models.BooleanField(default=False, verbose_name=u'主推热卖')
    hot_deals = models.BooleanField(default=False, verbose_name=u'火热促销')
    product_long_image = models.ImageField(upload_to='images/products/%Y/%m/', verbose_name=u'广告长图', blank=True, null=True)
    product_group = models.ForeignKey('ProductGroup', blank=True, null=True, related_name='product_group',
                                 verbose_name=u'产品组')
    trader = models.ForeignKey(User, blank=True, null=True, related_name='trader',
                                verbose_name=u'交易员')
    is_associate = models.BooleanField(default=False, verbose_name=u'是否关联')

    def __init__(self, *args, **kwargs):
        super(AbstractProduct, self).__init__(*args, **kwargs)
        self.attr = MPProductAttributesContainer(product=self)

    def primary_image_url(self):
        img = self.primary_image()
        if isinstance(img, ProductImage):
            return img.original
        elif isinstance(img, dict):
            return img['original']
        else:
            return ''

    def advertising_long_image(self):
        """
        返回商品的长广告图片地址
        """
        return self.product_long_image

    # 详情页中显示的当前价格
    def current_price_for_display(self):
        p = self.stockrecords.first()
        if p:
            return p.price_retail
        else:
            return ''

    # def get_missing_image(self):
    #     """
    #     Returns a missing image object.
    #     """
    #     # This class should have a 'name' property so it mimics the Django file
    #     # field.
    #     return MissingProductImage()

    def has_focused_by(self, user):
        if user.is_anonymous():
            return False
        return WishLine.objects.filter(wishlist__owner=user, product__pk=self.pk).exists()

    def _can_pickup(self):
        can_pickup = True
        try:
            StockProductConfig = get_model('commission', 'StockProductConfig')
            current_product_config = StockProductConfig.objects.get(product=self)
            if current_product_config.self_pick_or_express == 2:
                can_pickup = False
        except:
            can_pickup = True
        return can_pickup
    can_pickup = property(_can_pickup)

    def _get_strike_price(self):
        StockTicker = get_model('commission', 'StockTicker')
        try:
            current_stockticker = StockTicker.objects.filter(product=self).order_by('-created_datetime').first()
            if current_stockticker and current_stockticker.strike_price:
                strike_price = current_stockticker.strike_price
            else:
                TradeComplete = get_model('commission', 'TradeComplete')
                last_trade_complete = TradeComplete.objects.filter(product=self).order_by('-created_datetime')[:1]
                if last_trade_complete:
                    strike_price = last_trade_complete[0].unit_price
                else:
                    StockProductConfig = get_model('commission', 'StockProductConfig')
                    try:
                        current_product_config = StockProductConfig.objects.get(product=self)
                        strike_price = current_product_config.opening_price
                    except:
                        strike_price = 99999999
        except:
            traceback.print_exc()
            strike_price = 99999999
        return float("%.2f"%strike_price)
    strike_price = property(_get_strike_price)

    def _get_product_price(self):
        StockTicker = get_model('commission', 'StockTicker')
        try:
            current_stockticker = StockTicker.objects.filter(product=self).order_by('-created_datetime').first()
            if current_stockticker and current_stockticker.strike_price:
                product_price = current_stockticker.strike_price
            else:
                TradeComplete = get_model('commission', 'TradeComplete')
                StockProductConfig = get_model('commission', 'StockProductConfig')
                last_trade_complete = TradeComplete.objects.filter(product=self).order_by('-created_datetime')
                current_product_config = StockProductConfig.objects.get(product=self)
                if last_trade_complete:
                    product_price = float(last_trade_complete[0].unit_price)*(1+float(current_product_config.ud_up_range))
                else:
                    try:
                        product_price = float(current_product_config.opening_price)*(1+float(current_product_config.ud_up_range))
                    except:
                        product_price = 99999999
        except:
            traceback.print_exc()
            product_price = 99999999
        return float("%.2f"%product_price)
    product_price = property(_get_product_price)

    def _get_buy_price(self):
        SystemConfig = get_model('commission', 'SystemConfig')
        system_config = SystemConfig.objects.first()
        buy_price_rate = system_config.buy_price_rate
        StockTicker = get_model('commission', 'StockTicker')
        try:
            current_stockticker = StockTicker.objects.filter(product=self).order_by('-created_datetime').first()
            if current_stockticker and current_stockticker.closing_price:
                buy_price = float(current_stockticker.closing_price)*float(buy_price_rate)
            else:
                TradeComplete = get_model('commission', 'TradeComplete')
                StockProductConfig = get_model('commission', 'StockProductConfig')
                last_trade_complete = TradeComplete.objects.filter(product=self).order_by('-created_datetime')
                current_product_config = StockProductConfig.objects.get(product=self)
                if last_trade_complete:
                    buy_price = float(last_trade_complete[0].unit_price)*float(buy_price_rate)
                else:
                    try:
                        buy_price = float(current_product_config.opening_price)*float(buy_price_rate)
                    except:
                        buy_price = 99999999
        except:
            traceback.print_exc()
            buy_price = 99999999
        return float("%.2f"%buy_price)
    buy_price = property(_get_buy_price)

    def _get_volume(self):
        TradeComplete = get_model('commission', 'TradeComplete')
        try:
            volume = TradeComplete.objects.filter(product=self).aggregate(Sum('quantity')).get('quantity__sum')
            if not volume:
                volume = 0
        except:
            traceback.print_exc()
            volume = 0
        return volume
    volume = property(_get_volume)

    def _get_quote(self):
        StockProductConfig = get_model('commission', 'StockProductConfig')
        try:
            current_product_config = StockProductConfig.objects.filter(product=self)[0]
            quote = current_product_config.quote
        except:
            quote = 0
        return quote
    quote = property(_get_quote)

    def _get_min_snum(self):
        StockProductConfig = get_model('commission', 'StockProductConfig')
        try:
            current_product_config = StockProductConfig.objects.filter(product=self)[0]
            min_snum = current_product_config.min_snum
        except:
            min_snum = 0
        return min_snum
    min_snum = property(_get_min_snum)

    def _get_min_bnum(self):
        StockProductConfig = get_model('commission', 'StockProductConfig')
        try:
            current_product_config = StockProductConfig.objects.filter(product=self)[0]
            min_bnum = current_product_config.min_bnum
        except:
            min_bnum = 0
        return min_bnum
    min_bnum = property(_get_min_bnum)

    def _get_up_down_range(self):
        StockProductConfig = get_model('commission', 'StockProductConfig')
        try:
            current_product_config = StockProductConfig.objects.filter(product=self)[0]
            up_down_range = current_product_config.up_down_range
        except:
            up_down_range = 0
        return up_down_range
    up_down_range = property(_get_up_down_range)

    def _get_up_up_range(self):
        StockProductConfig = get_model('commission', 'StockProductConfig')
        try:
            current_product_config = StockProductConfig.objects.filter(product=self)[0]
            up_up_range = current_product_config.up_up_range
        except:
            up_up_range = 0
        return up_up_range
    up_up_range = property(_get_up_up_range)

    def _get_sale_num(self):
        StockProductConfig = get_model('commission', 'StockProductConfig')
        try:
            current_product_config = StockProductConfig.objects.filter(product=self)[0]
            sale_num = current_product_config.sale_num
        except:
            sale_num = 0
        return sale_num
    sale_num = property(_get_sale_num)

    def _get_express_price(self):
        StockProductConfig = get_model('commission', 'StockProductConfig')
        try:
            current_product_config = StockProductConfig.objects.filter(product=self)[0]
            express_price = current_product_config.express_price
        except:
            express_price = 0
        return express_price
    express_price = property(_get_express_price)

    def _get_pickup_price(self):
        StockProductConfig = get_model('commission', 'StockProductConfig')
        try:
            current_product_config = StockProductConfig.objects.filter(product=self)[0]
            pickup_price = current_product_config.pickup_price
        except:
            pickup_price = 0
        return pickup_price
    pickup_price = property(_get_pickup_price)

    def _get_max_num(self):
        StockProductConfig = get_model('commission', 'StockProductConfig')
        try:
            current_product_config = StockProductConfig.objects.filter(product=self)[0]
            max_num = current_product_config.max_num
        except:
            max_num = 0
        return max_num
    max_num = property(_get_max_num)

    def _get_once_max_num(self):
        StockProductConfig = get_model('commission', 'StockProductConfig')
        try:
            current_product_config = StockProductConfig.objects.filter(product=self)[0]
            once_max_num = current_product_config.once_max_num
        except:
            once_max_num = 0
        return once_max_num
    once_max_num = property(_get_once_max_num)

    def _get_opening_price(self):
        StockProductConfig = get_model('commission', 'StockProductConfig')
        try:
            current_product_config = StockProductConfig.objects.filter(product=self)[0]
            opening_price = current_product_config.opening_price
        except:
            opening_price = 0
        return opening_price
    opening_price = property(_get_opening_price)

    def _get_max_deal_num(self):
        StockProductConfig = get_model('commission', 'StockProductConfig')
        try:
            current_product_config = StockProductConfig.objects.filter(product=self)[0]
            max_deal_num = current_product_config.max_deal_num
        except:
            max_deal_num = 0
        return max_deal_num
    max_deal_num = property(_get_max_deal_num)

    def _get_max_buy_num(self):
        StockProductConfig = get_model('commission', 'StockProductConfig')
        try:
            current_product_config = StockProductConfig.objects.filter(product=self)[0]
            max_buy_num = current_product_config.max_buy_num
        except:
            max_buy_num = 0
        return max_buy_num
    max_buy_num = property(_get_max_buy_num)

    def _price_range(self):
        StockTicker = get_model('commission', 'StockTicker')
        product_config = self.stock_config_product
        try:
            current_stockticker = StockTicker.objects.filter(product=self).order_by('-created_datetime').first()
            if current_stockticker and current_stockticker.closing_price:
                product_price = current_stockticker.closing_price
            else:
                product_price = product_config.opening_price
        except:
            traceback.print_exc()
            product_price = 99999999
        max_price = "%.2f"%(float(product_price)*(1+float(product_config.ud_up_range)))
        min_price = "%.2f"%(float(product_price)*(1-float(product_config.ud_down_range)))
        product_price_range = [min_price,max_price]
        return product_price_range
    price_range = property(_price_range)

    def get_max_canbuy_num(self,user):
        from stars.apps.commission.models import StockProductConfig,UserProduct,CommissionBuy
        product_config = StockProductConfig.objects.get(product=self)
        if product_config.max_buy_num :
            config_max_num = int(product_config.max_buy_num)
        else :
            config_max_num = 0

        if not user:
            max_num = config_max_num
        else:
            try:
                buy_num = int(UserProduct.objects.get(user=user,product=self,trade_type=1).quantity)
                all_commission = CommissionBuy.objects.filter(user=user,product=self,c_type=1,status__in=[1,2])
                commission_num = 0
                for commission in all_commission:
                    commission_num += commission.uncomplete_quantity
                max_buy_num = int(config_max_num-commission_num-buy_num)
            except UserProduct.DoesNotExist:
                all_commission = CommissionBuy.objects.filter(user=user,product=self,c_type=1,status__in=[1,2])
                commission_num = 0
                for commission in all_commission:
                    commission_num += commission.uncomplete_quantity
                max_buy_num = int(config_max_num-commission_num)

            if max_buy_num >0 :
                max_num=max_buy_num
            else :
                max_num = 0
        return max_num
    
    def _image_url_or_none(self):
        try:
            img_url = self.primary_image().original.url
        except:
            img_url = ""
        return img_url
    img_url_or_none = property(_image_url_or_none)

    def save(self, *args, **kwargs):
        if self.trader:
            self.is_associate = True
        else:
            self.is_associate = False
        super(Product, self).save(*args, **kwargs)


class Category(AbstractCategory):
    product_class = models.ForeignKey(
        'catalogue.ProductClass', null=True, blank=True,
        verbose_name=_(u'分类类属性'), related_name="categories",
        help_text=_(u"选择分类的类属性，绑定分类商品属性值"))

    def get_child_category(self):
        """
        子类=商品，商品列表显示直接显示商品。
        """
        return self.product_set.filter(is_on_shelves=True)

    def get_product_class(self):
        """
        得到分类的商品类属性
        """
        p_class = self.product_class
        try:
            p_attributes = p_class.attributes.filter(search_filter = True)
        except:
            p_attributes = None

        return p_attributes

    def get_category_products(self):
        products = []
        for product in self.product_set.filter(is_on_shelves=True):
            products.append(product)
        if self.has_children():
            for child in self.get_children():
                for product in child.product_set.filter(is_on_shelves=True):
                    products.append(product)
                if child.has_children():
                    for c in child.get_children():
                        for product in c.product_set.filter(is_on_shelves=True):
                            products.append(product)
        return products


class ProductAttribute(AbstractProductAttribute):
    #该属性是否搜索
    search_filter = models.BooleanField(u'是否搜索', default=True,
                                        help_text = u'设置不需要搜索的属性值')
    index = models.IntegerField(blank=True, null=True, verbose_name=u'排序')

    def get_attributes(self):
        search_values = self.searchfilter_set.filter(chose = True).order_by('search_order')

        return search_values
    def __unicode__(self):
            return "%s %s" % (self.name,self.code)


class SearchFilter(models.Model):
    value_choise = (('>',u'以上'),('<',u'以下'))
    attribute = models.ForeignKey(
        'catalogue.ProductAttribute', verbose_name=_("Attribute"))
    search_value = models.CharField(u'搜索值',blank= True ,null = True,max_length=120,
                                    help_text = u'区间值设置成 eg:30度-40度')
    value_range = models.CharField(u'选择范围',blank = True , null = True ,choices=value_choise,max_length=120,
                                   help_text = u'不是范围的属性值为空')
    search_order = models.IntegerField(u'搜索值排列顺序',blank = True ,null = True )
    chose = models.BooleanField(u'选择该搜索值',default=True)

    class Meta :
        app_label = 'catalogue'
        ordering = ['attribute']
        verbose_name = u'搜索属性配置'
        verbose_name_plural = u'搜索属性配置'


class ProductGroup(models.Model):
    name = models.CharField(max_length=200, verbose_name=u'名字')
    attr = models.ManyToManyField(
        ProductAttribute, related_name="product_group_attr",
        blank=True, verbose_name=u'产品组属性')

    class Meta :
        app_label = 'catalogue'
        verbose_name = u'产品组'
        verbose_name_plural = u'产品组'

    def __unicode__(self):
            return self.name
    #如果产品组只有一个属性，获取属性列表
    def get_single_attr_value_list(self):
        first_attr = self.attr.all().order_by('index')[0]
        group_attr_value = ProductAttributeValue.objects.filter(attribute=first_attr)
        group_attr_list = []
        for attr_value in group_attr_value:
            list_value = {"text":attr_value.value_text,"href":attr_value.product.get_absolute_url(),"id":attr_value.product.id}
            group_attr_list.append(list_value)
        return group_attr_list
    #如果产品组有两个属性，获取主属性列表
    def get_first_attr_value_list(self,second_attr_value):
        key_list = self.get_available_list()
        first_attr = self.attr.all().order_by('index')[0]
        group_attr_value = ProductAttributeValue.objects.filter(attribute=first_attr)
        first_attr_in_list = []#用来去重
        first_attr_value_list = []
        for attr_value in group_attr_value:
            if attr_value.value_text not in first_attr_in_list:
                first_attr_hash = hash(attr_value.value_text)
                second_attr_hash = hash(second_attr_value)
                key = "%d#%d" % (first_attr_hash,second_attr_hash)
                try:
                    href = key_list[key]
                except:
                    href = attr_value.product.get_absolute_url()
                first_attr_value = {"text":attr_value.value_text,"href":href,"id":attr_value.product.id}
                first_attr_value_list.append(first_attr_value)
                first_attr_in_list.append(attr_value.value_text)
        return first_attr_value_list
    #如果产品组有两个属性，获取主属性列表--移动端
    def get_first_attr_value_list_mobile(self,second_attr_value):
        key_list = self.get_available_list_mobile()
        first_attr = self.attr.all().order_by('index')[0]
        group_attr_value = ProductAttributeValue.objects.filter(attribute=first_attr)
        first_attr_in_list = []#用来去重
        first_attr_value_list = []
        for attr_value in group_attr_value:
            if attr_value.value_text not in first_attr_in_list:
                first_attr_hash = hash(attr_value.value_text)
                second_attr_hash = hash(second_attr_value)
                key = "%d#%d" % (first_attr_hash,second_attr_hash)
                try:
                    pid = key_list[key]
                except:
                    pid = attr_value.product.id
                first_attr_value = {"text":attr_value.value_text,"id":pid}
                first_attr_value_list.append(first_attr_value)
                first_attr_in_list.append(attr_value.value_text)
        return first_attr_value_list
    #如果产品组有两个属性，获取副属性列表
    def get_second_attr_value_list(self,first_attr_value):
        key_list = self.get_available_list()
        first_attr = self.attr.all().order_by('index')[0]
        second_attr = self.attr.all().order_by('index')[1]
        group_attr_value = ProductAttributeValue.objects.filter(attribute=second_attr)
        attr_value_list = ProductAttributeValue.objects.filter(attribute=first_attr,value_text=first_attr_value)
        #获取副属性全部选项
        second_attr_in_list = []#用来去重
        second_attr_value_list = []
        for attr_value in group_attr_value:
            if attr_value.value_text not in second_attr_in_list:
                first_attr_hash = hash(first_attr_value)
                second_attr_hash = hash(attr_value.value_text)
                key = "%d#%d" % (first_attr_hash,second_attr_hash)
                try:
                    href = key_list[key]
                except:
                    href = ""
                second_attr_value = {"text":attr_value.value_text,"href":href,"id":attr_value.product.id}
                second_attr_value_list.append(second_attr_value)
                second_attr_in_list.append(attr_value.value_text)
        #判断副属性是否可以点击
        has_list = []
        for attr_value in attr_value_list:
            attr_value = ProductAttributeValue.objects.get(product=attr_value.product,attribute=second_attr).value_text
            if attr_value not in has_list:
                has_list.append(attr_value)
        second_list = []
        for second_attr_value in second_attr_value_list:
            if second_attr_value['text'] in has_list:
                one_attr = {"text":second_attr_value['text'],"has":"true","href":second_attr_value['href'],"id":second_attr_value['id']}
                second_list.append(one_attr)
            else:
                one_attr = {"text":second_attr_value['text'],"has":"","id":second_attr_value['id']}
                second_list.append(one_attr)
        return second_list
    #如果产品组有两个属性，获取副属性列表--移动端
    def get_second_attr_value_list_mobile(self,first_attr_value):
        key_list = self.get_available_list_mobile()
        first_attr = self.attr.all().order_by('index')[0]
        second_attr = self.attr.all().order_by('index')[1]
        group_attr_value = ProductAttributeValue.objects.filter(attribute=second_attr)
        attr_value_list = ProductAttributeValue.objects.filter(attribute=first_attr,value_text=first_attr_value)
        #获取副属性全部选项
        second_attr_in_list = []#用来去重
        second_attr_value_list = []
        for attr_value in group_attr_value:
            if attr_value.value_text not in second_attr_in_list:
                first_attr_hash = hash(first_attr_value)
                second_attr_hash = hash(attr_value.value_text)
                key = "%d#%d" % (first_attr_hash,second_attr_hash)
                try:
                    pid = key_list[key]
                except:
                    pid = ""
                second_attr_value = {"text":attr_value.value_text,"id":pid}
                second_attr_value_list.append(second_attr_value)
                second_attr_in_list.append(attr_value.value_text)
        #判断副属性是否可以点击
        has_list = []
        for attr_value in attr_value_list:
            attr_value = ProductAttributeValue.objects.get(product=attr_value.product,attribute=second_attr).value_text
            if attr_value not in has_list:
                has_list.append(attr_value)
        second_list = []
        for second_attr_value in second_attr_value_list:
            if second_attr_value['text'] in has_list:
                one_attr = {"text":second_attr_value['text'],"has":"true","id":second_attr_value['id']}
                second_list.append(one_attr)
            else:
                one_attr = {"text":second_attr_value['text'],"has":"","id":second_attr_value['id']}
                second_list.append(one_attr)
        return second_list

#     def get_has_list(self,first_attr_value):
#         first_attr = self.attr.all().order_by('index')[0]
#         second_attr = self.attr.all().order_by('index')[1]
#         attr_value_list = ProductAttributeValue.objects.filter(attribute=first_attr,value_text=first_attr_value)
#         has_list = []
#         for attr_value in attr_value_list:
#             second_attr_value = ProductAttributeValue.objects.get(product=attr_value.product,attribute=second_attr).value_text
#             if second_attr_value not in has_list:
#                 has_list.append(second_attr_value)
#         return has_list
    #获取产品组内所有产品
    def get_products(self):
        group_attr = self.attr.all()
        all_product = []
        for attr in group_attr:
            group_attr_value = ProductAttributeValue.objects.filter(attribute=attr)
            for attr_value in group_attr_value:
                if attr_value.product not in all_product:
                    all_product.append(attr_value.product)
        return all_product
    #获取当前产品组可用列表
    def get_available_list(self):
        key_list = {}
        all_product = self.get_products()
        first_attr = self.attr.all().order_by('index')[0]
        second_attr = self.attr.all().order_by('index')[1]
        for one_product in all_product:
            first_attr_hash = hash(ProductAttributeValue.objects.get(attribute=first_attr,product=one_product).value_text)
            second_attr_hash = hash(ProductAttributeValue.objects.get(attribute=second_attr,product=one_product).value_text)
            key = "%d#%d"
            key = key % (first_attr_hash,second_attr_hash)
            key_list[key]=one_product.get_absolute_url()
        return key_list
    #获取当前产品组可用列表
    def get_available_list_mobile(self):
        key_list = {}
        all_product = self.get_products()
        first_attr = self.attr.all().order_by('index')[0]
        second_attr = self.attr.all().order_by('index')[1]
        for one_product in all_product:
            first_attr_hash = hash(ProductAttributeValue.objects.get(attribute=first_attr,product=one_product).value_text)
            second_attr_hash = hash(ProductAttributeValue.objects.get(attribute=second_attr,product=one_product).value_text)
            key = "%d#%d"
            key = key % (first_attr_hash,second_attr_hash)
            key_list[key]=one_product.id
        return key_list

from oscar.apps.catalogue.models import *  # noqa
