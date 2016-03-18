# -*- coding: utf-8 -*-s

import os
import traceback

from django.contrib.staticfiles.finders import find
from django.db import models
from django.db.models import Sum
from django.db.models.manager import Manager
from django.utils.translation import ugettext_lazy as _
from oscar.apps.catalogue.abstract_models import (AbstractProduct, AbstractCategory, AbstractProductAttribute,
                                                  ProductAttributesContainer as CoreProductAttributesContainer)
from oscar.apps.catalogue.abstract_models import MissingProductImage as mpi
from oscar.apps.catalogue.models import *  # noqa
from oscar.apps.catalogue.models import ProductAttributeValue
from oscar.core.loading import get_model


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
    new_listing = models.BooleanField(default=False, verbose_name=u'新品上市')
    featured_hot = models.BooleanField(default=False, verbose_name=u'主推热卖')
    hot_deals = models.BooleanField(default=False, verbose_name=u'火热促销')
    product_long_image = models.ImageField(upload_to='images/products/%Y/%m/', verbose_name=u'广告长图', blank=True, null=True)
    product_group = models.ForeignKey('ProductGroup', blank=True, null=True, related_name='product_group',
                                 verbose_name=u'产品组')
    
    def __init__(self, *args, **kwargs):
        super(AbstractProduct, self).__init__(*args, **kwargs)
        self.attr = MPProductAttributesContainer(product=self)
    def advertising_long_image(self):
        """
        返回商品的长广告图片地址
        """
        return self.product_long_image

    def get_missing_image(self):
        """
        Returns a missing image object.
        """
        # This class should have a 'name' property so it mimics the Django file
        # field.
        return MissingProductImage()

    def has_focused_by(self, user):
        if user.is_anonymous():
            return False
        return WishLine.objects.filter(wishlist__owner=user, product__pk=self.pk).exists()

    def _get_strike_price(self):
        StockTicker = get_model('commission', 'StockTicker')
        try:
            current_stockticker = StockTicker.objects.filter(product=self).order_by('-created_datetime').first()
            if current_stockticker and current_stockticker.strike_price:
                strike_price = current_stockticker.strike_price
            else:
                TradeComplete = get_model('commission', 'TradeComplete')
                last_trade_complete = TradeComplete.objects.filter(product=self).order_by('-created_datetime')
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
        return strike_price
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
        return "%.2f"%product_price
    product_price = property(_get_product_price)


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


class Category(AbstractCategory):
    product_class = models.ForeignKey(
        'catalogue.ProductClass', null=True, blank=True,
        verbose_name=_(u'分类类属性'), related_name="categories",
        help_text=_(u"选择分类的类属性，绑定分类商品属性值")) 

    def get_child_category(self):
        """
        子类=商品，商品列表显示直接显示商品。
        """
        return self.product_set.filter(is_on_shelves = True)
    
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
 

        
    
class ProductAttribute(AbstractProductAttribute):
    #该属性是否搜索
    search_filter = models.BooleanField(u'是否搜索', default=True,
                                        help_text = u'设置不需要搜索的属性值')
    
    def get_attributes(self):
        search_values = self.searchfilter_set.filter(chose = True).order_by('search_order')
        
        return search_values
    
    
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
    
    def get_products(self):
        group_attr = self.attr.all()
        all_product = []
        for attr in group_attr:
            group_attr_value = ProductAttributeValue.objects.filter(attribute=attr)
            for attr_value in group_attr_value:
                if attr_value.product not in all_product:
                    all_product.append(attr_value.product)
        return all_product
    
    def get_available_list(self):
        has_list = []
        key_list = {}
        all_product = self.get_products()
        group_attr = self.attr.all()
        for one_product in all_product:
            key = "%s_%d_%d#%s_%d_%d"
            replace_str = []
            for attr in group_attr:
                attr_value_hash = hash(ProductAttributeValue.objects.get(attribute=attr,product=one_product).value_text)
                replace_str.append(attr.code)
                replace_str.append(int(attr.id))
                replace_str.append(int(attr_value_hash))
            key = key % tuple(replace_str)
            has_list.append(key)
            key_list[key]=int(one_product.id)
        available_list = {'has_list':has_list,'key_list':key_list} 
        return available_list
    
    
    


