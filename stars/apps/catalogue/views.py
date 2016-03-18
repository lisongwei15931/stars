#coding=utf-8
'''
'''
import json
import traceback
import datetime
from django.conf import settings
from django.contrib import messages
from django.core.paginator import InvalidPage
from django.db.models import Q,Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, get_list_or_404
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView
from oscar.apps.customer import history
from oscar.apps.customer.history import extract
from oscar.core.loading import get_class,get_model

from stars.apps.catalogue.models import Product, Category
from stars.apps.tradingcenter.views import floatformat

from django.http.response import HttpResponse
from .utils import open_close_date
from stars.apps.basket.models import Line

SimpleProductSearchHandler = get_class(
    'catalogue.searchproduct_handlers', 'SimpleProductSearchHandler')
Product = get_model('catalogue', 'product')
ProductGroup = get_model('catalogue', 'ProductGroup')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
Province = get_model('address', 'Province')
City = get_model('address', 'City')
StockTicker = get_model('commission', 'StockTicker')
UserProduct = get_model('commission', 'UserProduct')
StockProductConfig = get_model('commission', 'StockProductConfig')
CommissionBuy = get_model('commission', 'CommissionBuy')
SystemConfig = get_model('commission', 'SystemConfig')

class CustomProductDetailView(CoreProductDetailView):
    template_name = "catalogue/customdetail.html"
    enforce_paths = False
    enforce_parent = False
    ##不显示下架商品
    queryset = Product.objects.filter(is_on_shelves = True,opening_date__lte=datetime.datetime.now().date())

    def get_history_products(self):
        ids = extract(self.request)
        history_products = Product.objects.filter(id__in = ids,opening_date__lte=datetime.datetime.now().date()).order_by('-browse_num')[:7]
        return history_products

    def get_context_data(self, **kwargs):
        ctx = super(CustomProductDetailView, self).get_context_data(**kwargs)
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
        provinces = Province.objects.all()
        ctx['provinces']=provinces
        ctx['history_products'] = self.get_history_products()
        ctx['recommended_products'] = self.get_object().recommended_products.filter(opening_date__lte=datetime.datetime.now().date()).order_by('-browse_num')[:7]
        #查找categorylist
        category_list = Category.objects.filter(depth=1).order_by('path')[:10]
        ctx['category_list'] = category_list
        product = self.get_object()
        product_config = StockProductConfig.objects.get(product=product)
        config_max_num = int(product_config.max_buy_num)
        if self.request.user.is_anonymous():
            max_num = config_max_num
        else:
            line = Line.objects.filter(product=product,basket__owner=self.request.user).exclude(basket__status='Submitted').first()
            if line :
                line_num = line.quantity
            else :
                line_num = 0

            try:
                buy_num = int(UserProduct.objects.get(user=self.request.user,product=product,trade_type=1).quantity)
                all_commission = CommissionBuy.objects.filter(user=self.request.user,product=product,c_type=1,status__in=[1,2])
                commission_num = 0
                for commission in all_commission:
                    commission_num += commission.uncomplete_quantity
                max_buy_num = int(config_max_num-commission_num-buy_num-line_num)
            except UserProduct.DoesNotExist:
                all_commission = CommissionBuy.objects.filter(user=self.request.user,product=product,c_type=1,status__in=[1,2])
                commission_num = 0
                for commission in all_commission:
                    commission_num += commission.uncomplete_quantity
                max_buy_num = int(config_max_num-commission_num-line_num)
            max_num=max_buy_num
        ctx['max_num'] = max_num
        product_group = self.get_object().product_group
        if product_group:
            product_group_attr_count = product_group.attr.count()
            if product_group_attr_count == 2:
                try:
                    first_attr = product_group.attr.all().order_by('index')[0]
                    second_attr = product_group.attr.all().order_by('index')[1]
                    cur_first_attr_value = ProductAttributeValue.objects.get(attribute=first_attr,product=self.get_object()).value_text
                    cur_second_attr_value = ProductAttributeValue.objects.get(attribute=second_attr,product=self.get_object()).value_text
                    first_attr_value_list = product_group.get_first_attr_value_list(cur_second_attr_value)
                    second_attr_value_list = product_group.get_second_attr_value_list(cur_first_attr_value)
                    ctx['first_attr'] = first_attr
                    ctx['second_attr'] = second_attr
                    ctx['cur_first_attr_value'] = cur_first_attr_value
                    ctx['cur_second_attr_value'] = cur_second_attr_value
                    ctx['first_attr_value_list'] = first_attr_value_list
                    ctx['second_attr_value_list'] = second_attr_value_list
                except:
                    traceback.print_exc()
                    return ctx
                return ctx
            elif product_group_attr_count == 1:
                try:
                    first_attr = product_group.attr.all().order_by('index')[0]
                    cur_first_attr_value = ProductAttributeValue.objects.get(attribute=first_attr,product=self.get_object()).value_text
                    first_attr_value_list = product_group.get_single_attr_value_list()
                    ctx['first_attr'] = first_attr
                    ctx['cur_first_attr_value'] = cur_first_attr_value
                    ctx['first_attr_value_list'] = first_attr_value_list
                except:
                    return ctx
                return ctx
            elif product_group_attr_count == 0:
                return ctx
        else:
            return ctx

    ###浏览量+1
    def get(self,request,*args,**kwargs):
        #=======================================================================
        # pk_id = request.path.split('_')[1].split(r'/')[0]
        # print pk_id
        # product = Product.objects.get(pk=pk_id)
        # product.browse_num +=1
        # product.save()
        #=======================================================================
        product = self.get_object()
        product.browse_num +=1
        product.save(update_fields=['browse_num',])

        return super(CustomProductDetailView,self).get(request,*args,**kwargs)


class AllSearchProductView(TemplateView):
    """
    Browse all products in the catalogue
    分页展示所有商品
    """
    context_object_name = "products"
    template_name = 'catalogue/product-list.html'

    def get(self, request, *args, **kwargs):
        try:
            self.search_handler = self.get_search_handler(
                self.request.GET, request.get_full_path(), [])
        except InvalidPage:
            # Redirect to page one.
            messages.error(request, _('The given page number was invalid.'))
            return redirect('catalogue:allproducts')
        return super(AllSearchProductView, self).get(request, *args, **kwargs)

    def get_search_handler(self, *args, **kwargs):
        return SimpleProductSearchHandler(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = {}
        ctx['summary'] = _("All products")
        search_context = self.search_handler.get_search_context_data(
            self.context_object_name)
        ctx.update(search_context)

        pq = Product.objects.filter(is_on_shelves = True,opening_date__lte=datetime.datetime.now().date()).annotate(q=Sum('trade_complete_product__quantity')).order_by('-q')[:7]
        hotproduct = pq
        ctx['hotproduct'] = hotproduct

        history_products = Product.objects.filter(id__in = extract(self.request),opening_date__lte=datetime.datetime.now().date()).order_by('-browse_num')[:7]
        ctx['history_products'] = history_products

        category_list = Category.objects.filter(depth=1).order_by('path')[:10]
        ctx['category_list'] =category_list

        ctx['open_or_close'] = open_close_date()[0]
        ctx['open_close_msg'] = open_close_date()[1]

        return ctx

#===============================================================================
#     def post(self,request,*args,**kwargs):
#         data = request.POST
#         search_q = data.get('q','')
#         qs = Product.objects.filter(is_on_shelves = True)
#         ctx = {}
#         # 查询商品名称 ，编号 ，描述，类别 ，分类，
#         try:
#             if search_q :
#                 qs = qs.filter(Q(title__icontains=search_q)|Q(description__icontains=search_q)
#                                |Q(upc__icontains= search_q)|Q(categories__name__icontains = search_q)
#                                |Q(product_class__name__icontains = search_q)
#                                )
#
#             self.object_list = qs.all()
#         except Exception as e:
#             pass
#
#         ctx = {'products': self.object_list ,}
#         resp = render(request,'catalogue/product-list.html',ctx)
#
#         return resp
#===============================================================================


def get_province_citys(request,pid):
    province = Province.objects.get(id=pid)
    cities = City.objects.filter(province=province)
    all_city_info = []
    for city in cities:
        city_info = [city.id,city.name]
        all_city_info.append(city_info)
    return HttpResponse(json.dumps(all_city_info),content_type = "application/json")

def city_has_product(request):
    pid = request.POST.get('pid')
    cid = request.POST.get('cid')
    product = Product.objects.get(id=pid)
    city = City.objects.get(id=cid)
    all_city = []
    all_pickup_addr = product.stock_config_product.distribution_pickup_addr.all()
    for pickup_addr in all_pickup_addr:
        all_city.append(pickup_addr.city)
    return HttpResponse(city in all_city)











