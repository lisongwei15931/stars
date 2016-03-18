#coding=utf-8
'''
'''
from django.conf import settings
from django.contrib import messages
from django.core.paginator import InvalidPage
from django.shortcuts import get_object_or_404, redirect, get_list_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView
from oscar.apps.customer import history
from oscar.apps.customer.history import extract
from oscar.core.loading import get_class,get_model

from stars.apps.catalogue.models import Product, Category
from django.db.models import Q
from django.shortcuts import render

SimpleProductSearchHandler = get_class(
    'catalogue.searchproduct_handlers', 'SimpleProductSearchHandler')
Product = get_model('catalogue', 'product')
ProductGroup = get_model('catalogue', 'ProductGroup')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')

class CustomProductDetailView(CoreProductDetailView):
    template_name = "catalogue/customdetail.html"
    enforce_paths = False
    enforce_parent = False
    ##不显示下架商品
    queryset = Product.objects.filter(is_on_shelves = True)
    
    def get_history_products(self):
        ids = extract(self.request)
        history_products = Product.objects.filter(id__in = ids).order_by('-browse_num')[:7]
        return history_products
    
    def get_context_data(self, **kwargs):
        ctx = super(CustomProductDetailView, self).get_context_data(**kwargs)
        ctx['history_products'] = self.get_history_products()
        #查找categorylist
        category_list = Category.objects.filter(depth=1).order_by('id')[:10]
        ctx['category_list'] = category_list
        ctx['attr'] = self.get_product_group_value()
        
        product_group = self.get_object().product_group;
        
        group_attr = product_group.attr.all()
        cur_attr = ""
        for attr in group_attr:
            attr_value = ProductAttributeValue.objects.get(attribute=attr,product=self.get_object())
            cur_str = "%s_%s_%s," % (str(attr.code),str(attr.id),str(attr_value.id))
            cur_attr += cur_str
        ctx['cur_attr'] = str(cur_attr)
        return ctx
    
    def get_product_group_value(self):
        
        product_group = self.get_object().product_group;
        group_attr = product_group.attr.all()
        cur_list = []
        for attr in group_attr:
            attr_value_hash = hash(ProductAttributeValue.objects.get(attribute=attr,product=self.get_object()).value_text)
            cur_str = "%s_%s_%s" % (str(attr.code),str(attr.id),str(attr_value_hash))
            cur_list.append(cur_str) 
            
        all_product = []
        value_text_list = []
        for attr in group_attr:
            group_attr_value = ProductAttributeValue.objects.filter(attribute=attr)
#             in_value_list = []
#             value_list = []
#             product_attr_value = ProductAttributeValue.objects.filter(product=self.get_object())
            
            for attr_value in group_attr_value:
                attr_value_hash = hash(attr_value.value_text)
                value_str = "%s_%s_%s" % (str(attr.code),str(attr.id),str(attr_value_hash))
                if value_str not in value_text_list:
                    value_text_list.append(value_str)
                    for cur_value in cur_list:
                        has_value = "%s#%s" % (cur_value,value_str)
                        cur_value
                    
                if attr_value.product not in all_product:
                    all_product.append(attr_value.product)
                if not attr_value.value_text in in_value_list:
                    in_value_list.append(attr_value.value_text)
                    if attr_value in product_attr_value:
                        value_list.append({'value_text':attr_value.value_text,'href':attr_value.product.get_absolute_url(),'has':'true','id':attr_value.id})
                    else:
                        value_list.append({'value_text':attr_value.value_text,'href':attr_value.product.get_absolute_url(),'has':'false'}) 
            attr.value = value_list
        return group_attr
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
        product.save()
         
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
        
        hotproduct = get_list_or_404(Product.objects.order_by('-date_updated'),hot_deals=True,is_on_shelves = True)[:7]
        ctx['hotproduct'] = hotproduct
        
        history_products = history.get(self.request)
        ctx['history_products'] = history_products
        
        category_list = Category.objects.filter(depth=1).order_by('id')[:10]
        ctx['category_list'] =category_list
        
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
        
        
        
        
        


    
    
    
    
    
    
