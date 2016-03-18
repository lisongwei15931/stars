# -*- coding: utf-8 -*-s

import datetime
import json
import random

from django.http.response import HttpResponse
from django.shortcuts import render_to_response, get_list_or_404
from django.template.context import RequestContext
from django.views.generic.base import TemplateView
from django.views import generic
from django.db.models import Sum, Max, Min
from oscar.apps.promotions.views import HomeView as CoreHomeView
from oscar.core.loading import get_model, get_class
from stars.apps.catalogue.utils import open_close_date

ProductSearchForm = get_class('dashboard.catalogue.forms','ProductSearchForm')
Product = get_model('catalogue', 'product')
Category = get_model('catalogue', 'category')
get_product_search_handler_class = get_class(
    'catalogue.search_handlers', 'get_product_search_handler_class')
ProductAttribute = get_model('catalogue', 'ProductAttribute')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
RollingAd = get_model('ad', 'RollingAd')
StockTicker = get_model('commission', 'StockTicker')
TradeComplete = get_model('commission', 'TradeComplete')
StockProductConfig = get_model('commission', 'StockProductConfig')
CommissionBuy = get_model('commission', 'CommissionBuy')
CommissionSale = get_model('commission', 'CommissionSale')
FlatPage = get_model('staticpages', 'FlatPageNew')
SystemConfig = get_model('commission', 'SystemConfig')

class HomeView(CoreHomeView):
    template_name = 'promotions/home.html'
    
    def get_context_data(self, **kwargs):
        ctx = super(HomeView, self).get_context_data(**kwargs)
        
        system_config = SystemConfig.objects.first()
        now = datetime.datetime.now().time()
        open_time = system_config.bank_start_time.strftime('%H:%M')
        close_time = system_config.bank_end_time.strftime('%H:%M')
        if system_config.bank_start_time < now and now < system_config.bank_end_time:
            open_close_msg = u"开市(当日%s-%s)"%(open_time,close_time)
            ctx['open_or_close'] = True
        else:
            open_close_msg = u"闭市(%s-次日%s)"%(close_time,open_time)
            ctx['open_or_close'] = False
        ctx['open_close_msg'] = open_close_msg
        ad_product_list = Product.objects.filter(new_listing=True,is_on_shelves=True,opening_date__lte=datetime.datetime.now().date() ).exclude(product_long_image='').exclude(product_long_image__isnull=True).distinct().order_by('-date_updated')
        ad_product = ad_product_list.first()
        new_product_list = []
        hotdeals_product_list = []
        if ad_product:
            new_product_list = Product.objects.filter(new_listing=True,is_on_shelves=True,opening_date__lte=datetime.datetime.now().date()).exclude(id=ad_product.id).order_by('-date_updated')[:8]
        else:
            new_product_list = Product.objects.filter(new_listing=True,is_on_shelves=True,opening_date__lte=datetime.datetime.now().date()).order_by('-date_updated')[:8]
        hotdeals_product = Product.objects.filter(hot_deals= True,is_on_shelves=True,opening_date__lte=datetime.datetime.now().date()).exclude(product_long_image='').exclude(product_long_image__isnull=True).distinct().order_by('-date_updated').first()
        if hotdeals_product:
            hotdeals_product_list = Product.objects.filter(hot_deals = True,is_on_shelves = True,opening_date__lte=datetime.datetime.now().date()).exclude(pk = hotdeals_product.pk).order_by('-date_updated')[:8]
        else:
            hotdeals_product_list = Product.objects.filter(hot_deals = True,is_on_shelves = True,opening_date__lte=datetime.datetime.now().date()).order_by('-date_updated')[:8]
        ##shuiji
        reputation_list = Product.objects.filter(selection_reputation = True,is_on_shelves = True,opening_date__lte=datetime.datetime.now().date()).order_by('-date_updated')[:11]

        #主推热卖  by lwj start
        p = Product.objects.filter(featured_hot=True,is_on_shelves=True,opening_date__lte=datetime.datetime.now().date()).exclude(product_long_image='').exclude(product_long_image__isnull=True).order_by('-date_updated').first()
        ctx['highly_recommended_product_first'] = p
        f = Product.objects.filter(featured_hot=True,is_on_shelves=True,opening_date__lte=datetime.datetime.now().date())
        if p:
            f = f.exclude(pk=p.pk)
        f = f.order_by('-date_updated')[:8]
        ctx['highly_recommended_product_list'] = f
        ##主推热卖  end

        #新品上市消息
        ctx['news_product'] = FlatPage.objects.filter(category=3).order_by('-created_datetime')[:7]
        #购物须知
        ctx['buy_know'] = FlatPage.objects.filter(category=4).order_by('-created_datetime')[:5]
        #公告
        ctx['notice'] = FlatPage.objects.filter(category=2).order_by('-created_datetime')[:5]

        category_list = Category.objects.filter(depth=1).order_by('path')[:10]
        
        ctx['hotdeals_product'] = hotdeals_product
        ctx['hotdeals_product_list'] = hotdeals_product_list
        ctx['new_product_list'] = new_product_list
        ctx['ad_product'] = ad_product

        ctx['reputation_list'] = reputation_list
        ctx['category_list'] = category_list
        ad_list = RollingAd.objects.filter(valid=True)
        ctx['rolling_ad_list'] = ad_list.filter(position='home_ad') # 轮播广告 by lwj 修改：包括页面其它广告
        ctx['index_ad_list'] = ad_list.filter(position = 'home_ad_1').order_by('order_num')#首页广告
        ctx['koubei_ad_list'] = ad_list.filter(position = 'home_ad_2').first()
        ctx['zhutui_ad_list'] = ad_list.filter(position = 'home_ad_3').first()
        ctx['huore_ad_list'] = ad_list.filter(position = 'home_ad_4').first()
        
        now_time = datetime.datetime.today()
        ctx['now_hour'] = now_time.hour
        ctx['now_minute'] = now_time.minute
        
        return ctx


class SearchView(TemplateView):
    template_name = 'promotions/search_form.html'

class TodayNewView(TemplateView):
    template_name = 'promotions/today_new_product.html'
    
    def get_context_data(self, **kwargs):
        ctx = super(TodayNewView, self).get_context_data(**kwargs)
        
        category_list = Category.objects.filter(depth=1).order_by('path')[:10]
        ctx['category_list'] =category_list
        ctx['open_or_close'] = open_close_date()[0]
        ctx['open_close_msg'] = open_close_date()[1]
        return ctx

#包括 新品上市,购物须知,公告
class NewsProductView(generic.ListView):
    template_name = 'promotions/news_product.html'
    paginate_by = 50
    context_object_name = 'news_list'

    def get_queryset(self):
        queryset = FlatPage.objects.all()
        self.flag = self.request.GET.get('flag','3')

        if self.flag == '3':
            queryset = queryset.filter(category=3).order_by('-created_datetime')
        if self.flag == '4':
            queryset = queryset.filter(category=4).order_by('-created_datetime')
        if self.flag == '2':
            queryset = queryset.filter(category=2).order_by('-created_datetime')

        return queryset


    def get_context_data(self, **kwargs):
        ctx = super(NewsProductView, self).get_context_data(**kwargs)
        ctx['flag'] = self.flag

        return ctx
 

class NewsProductDetailView(TemplateView):
    template_name = 'promotions/news_product_detail.html'   

    def get_context_data(self, **kwargs):
        ctx = super(NewsProductDetailView, self).get_context_data(**kwargs)

        try:
            #新品上市消息,购物须知,公告
            ctx['news_product_detail'] = FlatPage.objects.get(pk=kwargs.get("pk"))
        except:
            pass
        return ctx
    
def tend_view(request,pid):
    chartdata = []
    jsondata = {}
    tradedata = []
    product = Product.objects.get(id=pid)
    today = datetime.datetime.now().date()
    start_day = today + datetime.timedelta(days=-13)
    all_stock_ticker = StockTicker.objects.filter(product=product,created_date__range=(start_day,today)).order_by('created_date')
    today_high_price = TradeComplete.objects.filter(product=product,created_date=today).aggregate(Max('unit_price')).get('unit_price__max')
    today_low_price = TradeComplete.objects.filter(product=product,created_date=today).aggregate(Min('unit_price')).get('unit_price__min')
    max_commission_buy_price = CommissionBuy.objects.filter(product=product).exclude(status__in=[3,4]).aggregate(Max('unit_price')).get('unit_price__max')
    min_commission_sale_price = CommissionSale.objects.filter(product=product).exclude(status__in=[3,4]).aggregate(Min('unit_price')).get('unit_price__min')
    high_price_uncomplete_buy_num = CommissionBuy.objects.filter(product=product,unit_price=max_commission_buy_price).exclude(status__in=[3,4]).aggregate(Sum('uncomplete_quantity')).get('uncomplete_quantity__sum')
    low_price_uncomplete_sale_num = CommissionSale.objects.filter(product=product,unit_price=min_commission_sale_price).exclude(status__in=[3,4]).aggregate(Sum('uncomplete_quantity')).get('uncomplete_quantity__sum')
    commission_data = {"high_price":today_high_price,"low_price":today_low_price,"commission_buy_price":max_commission_buy_price,"commission_sale_price":min_commission_sale_price,"commission_buy_num":high_price_uncomplete_buy_num,"commission_sale_num":low_price_uncomplete_sale_num}
    
    for stock_ticker in all_stock_ticker:
        name = stock_ticker.created_date.strftime("%Y-%m-%d") 
        trade_complete_num = TradeComplete.objects.filter(product=product,created_date=stock_ticker.created_date).aggregate(Sum('quantity')).get('quantity__sum')
        trade_data = [name,trade_complete_num]
        tradedata.append(trade_data)
        if stock_ticker.strike_price:
            price = float(stock_ticker.strike_price)
            high_price = stock_ticker.high
            low_price = stock_ticker.low
        else:
            last_trade_complete = TradeComplete.objects.filter(product=product,created_date__lte=stock_ticker.created_date).order_by('-created_datetime')[:1].first()
            if last_trade_complete:
                price = float(last_trade_complete.unit_price)
                high_price = float(last_trade_complete.unit_price)
                low_price = float(last_trade_complete.unit_price)
            else:
                product_config = StockProductConfig.objects.get(product=product)
                price = float(product_config.opening_price)
                high_price = float(product_config.opening_price)
                low_price = float(product_config.opening_price)
        onedata = [name,price]
        chartdata.append(onedata)
        jsondata[name] = {"max":high_price,"min":low_price,"price":price}
    data = {"chartdata":chartdata,"jsondata":jsondata,"tradedata":tradedata,"commission_data":commission_data}
    return HttpResponse(json.dumps(data),content_type = "application/json")


#品牌汇
class BrandGatherView(TemplateView):
    template_name = 'promotions/brand_gather.html'
    
    def get_context_data(self, **kwargs):
        ctx = super(BrandGatherView, self).get_context_data(**kwargs)
        
        product_list = Product.objects.filter(is_on_shelves=True,opening_date__lte=datetime.datetime.now().date())[:20]
        category_list = Category.objects.filter(depth=1).order_by('path')[:10]
        ctx['product_list'] = product_list
        ctx['category_list'] =category_list
        ctx['open_or_close'] = open_close_date()[0]
        ctx['open_close_msg'] = open_close_date()[1]
        return ctx
    