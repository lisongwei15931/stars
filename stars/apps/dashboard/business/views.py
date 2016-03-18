#coding=utf-8

import datetime
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404, render_to_response
from django_tables2 import SingleTableMixin
from oscar.core.loading import get_class, get_model
from stars.apps.dashboard.business.tables import (StoreInCommApplyTable,Pickup_ApplyDashboard,
                                                  Product_QuotationDashboard,BusinessPickupStoreTable,
                                                  PickupOutStoreTable,BusinessProductTable,BusinessSaleTable,
                                                  BusinessProfitTable,BusinessBalanceTable,ExpressSendTable,
                                                  ProductTable, BusinessStockEnterDealTable,TraderProductTable)
from stars.apps.dashboard.business.forms import (StoreInComeForm,SearchStoreInComeForm,BusinessProductForm,
                                                 SearchProductApplyForm,SearchBusinessStoreForm,SearchBusinessInProductForm,
                                                 SearchOutStoreForm,SearchSaleForm,SearchBusinessForm,SearchPickProductForm,
                                                 BusinessLoginForm, TraderLoginForm, ProductSearchForm, ProductTraderForm,
                                                 SearchBusinessStockEnterDealForm, BusinessStockEnterDealForm,
                                                 StoreInComeDealForm,PartnerUserSearchForm,ExpressSendForm)
from stars.apps.commission.models import PickupDetail,StockTicker,PickupAddr,TradeComplete,UserMoneyChange
from stars.apps.pickup_admin.models import StoreInComeApply,PickupStore
from django.db.models import Sum, Case, When, Q, F, FloatField
from django.db.models.functions import Coalesce
import xlwt
import re
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from oscar.views import sort_queryset
from oscar.core.compat import get_user_model
import json

StockEnter = get_model('platform','StockEnter')
Partner = get_model('partner','Partner')
StockRecord = get_model('partner', 'StockRecord')
Product = get_model('catalogue','Product')
UserProduct = get_model('commission','UserProduct')


def get_pickupaddr(request):
    product = request.GET.get('product')
    if request.is_ajax():
        pickaddr = PickupAddr.objects.filter(stock_config_pickup_addr__product__id=product).values('id','name')
        return HttpResponse(json.dumps(list(pickaddr)),content_type='application/json',status=200)

class ProductListView(SingleTableMixin, generic.TemplateView):
    template_name = 'dashboard/business/product_list.html'
    paginate_by = 20
    form_class = ProductSearchForm
    table_class = ProductTable
    context_table_name = 'product_list'

    def get_table_pagination(self):
        return dict(per_page=20)

    def get_queryset(self):
        queryset = Product.objects.filter(stockrecords__partner__users=self.request.user)
        queryset = self.apply_search(queryset)
        return queryset

    def apply_search(self, queryset):
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('product'):
            qs_match = queryset.filter(product__title=data['product'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__title__icontains=data['product'])

        if data.get('upc'):
            qs_match = queryset.filter(product__upc=data['upc'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__upc__icontains=data['upc'])

        if data.get('trader'):
            qs_match = queryset.filter(trader__usernamename=data['trader'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(trader__username__icontains=data['trader'])

        if data.get('associate_status'):
            associate_status = data['associate_status']
            if associate_status == '2':
                queryset = queryset.filter(is_associate=True)
            elif associate_status == '3':
                queryset = queryset.filter(is_associate=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context


class ProductTraderUpdateView(generic.UpdateView):

    template_name = 'dashboard/business/product_trader_update.html'
    model = Product
    context_object_name = 'product'
    form_class = ProductTraderForm

    def __init__(self, *args, **kwargs):
        super(ProductTraderUpdateView, self).__init__(*args, **kwargs)
        self.success_url = reverse('dashboard:business-product-list')


class StroeInComeListView(SingleTableMixin,  generic.TemplateView):
    template_name = 'dashboard/business/storeincomapply_list.html'
    model = StoreInComeApply
    context_object_name = 'storeincome'
    table_class = StoreInCommApplyTable
    context_table_name = 'storeincome_tab'
    form_class = SearchStoreInComeForm

    def get_table(self, **kwargs):
        table = super(StroeInComeListView, self).get_table(**kwargs)
        table.caption = u'商家申请入库信息'
        return table

    def get_queryset(self):
        try:
            user = self.request.user
            queryset = StoreInComeApply.objects.filter(product__stockrecords__partner__users=user)
        except:
            queryset = []
        queryset = self.apply_search(queryset)
        return queryset


    def apply_search(self, queryset):
        """
        Filter the queryset and set the description according to the search
        parameters given
        """
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('product'):
            qs_match = queryset.filter(product__title=data['product'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__title__icontains=data['product'])

        if data.get('upc'):
            qs_match = queryset.filter(product__upc=data['upc'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__upc__icontains=data['upc'])

        if data.get('status'):
            qs_match = queryset.filter(status=data['status'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(status__icontains=data['status'])

        if data.get('pickup_addr'):
            qs_match = queryset.filter(pickup_addr__name=data['pickup_addr'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(pickup_addr__name__icontains=data['pickup_addr'])


        return queryset

    def get_context_data(self, *args, **kwargs):
        ctx = super(StroeInComeListView, self).get_context_data(*args, **kwargs)
        ctx['form']=self.form_class
        return ctx

class StroeInComeCreateView(generic.CreateView):
    template_name = 'dashboard/business/storeincomapply_create_update.html'
    model = StoreInComeApply
    form_class = StoreInComeForm
    context_object_name = 'storeincome'
    success_url = reverse_lazy('dashboard:storeincome-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.applysave()
        return super(StroeInComeCreateView, self).form_valid(form)

    #===========================================================================
    # def get(self, request, *args, **kwargs):
    #     self.object = None
    #     user = self.request.user
    #     # partner
    #     isp = Partner.objects.filter(users=user).last()
    #     p_ids= StockRecord.objects.filter(partner=isp)
    #     product = Product.objects.filter(stockrecords__in = p_ids)
    #     self.form_class.base_fields['product'].queryset = product
    #     return super(StroeInComeCreateView, self).get(request, *args, **kwargs)
    #===========================================================================
    def get_form_class(self):
        form_class = super(StroeInComeCreateView,self).get_form_class()
        #form_class.base_fields['pickup_addr'].queryset = PickupAddr.objects.none()
        user = self.request.user
        product = Product.objects.filter(stockrecords__partner__users=user,opening_date__lte=datetime.datetime.now().date())
        form_class.base_fields['product'].queryset = product
        return form_class
         
    def get_title(self):
        return _(u"增加新的入库申请")

    def get_success_url(self):
        messages.success(self.request, _(u"新的商品 : '%s' 入库单已创建") % self.object.product)
        return super(StroeInComeCreateView, self).get_success_url()

    def get_context_data(self, *args, **kwargs):
        ctx = super(StroeInComeCreateView, self).get_context_data(*args, **kwargs)
        user = self.request.user
        isp = Partner.objects.filter(users=user).first()
        #product = []
        if isp is not None:
            ctx['isp']=isp.id
            #p_ids= StockRecord.objects.filter(partner=isp)
            #product = Product.objects.filter(stockrecords__in = p_ids,opening_date__lte=datetime.datetime.now().date())
        #self.form_class.base_fields['product'].queryset = product
        #self.form_class.base_fields['pickup_addr'].queryset = PickupAddr.objects.none()
        #ctx['form']=self.form_class
        return ctx


class StoreIncomeDealView(generic.UpdateView):
    template_name = 'dashboard/business/business_storeincome_deal.html'
    model = StoreInComeApply
    form_class = StoreInComeDealForm
    success_url = reverse_lazy('dashboard:storeincome-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.deal_user = self.request.user
        self.object.save()
        if self.object.status == '4':
            current_pickup_store = PickupStore.objects.get_or_create(pickup_addr=self.object.pickup_addr,
                                                                     product=self.object.product)[0]
            current_pickup_store.quantity = current_pickup_store.quantity + self.object.in_quantity
            current_pickup_store.save()
        return HttpResponseRedirect(self.get_success_url())


class StroeInComeUpdateView(generic.UpdateView):
    template_name = 'dashboard/business/storeincomapply_create_update.html'
    model = StoreInComeApply
    form_class = StoreInComeForm
    context_object_name = 'storeincome'
    success_url = reverse_lazy('dashboard:storeincome-list')

    def get_title(self):
        return _(u"编辑入库申请")

    def form_valid(self, form):
        self.object = form.save(commit = False)
        #self.object.user = self.request.user
        self.object.applysave()
        return super(StroeInComeUpdateView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        ctx = super(StroeInComeUpdateView, self).get_context_data(*args, **kwargs)
        ctx['status'] = self.object.status
        user = self.request.user
        isp = Partner.objects.filter(users=user).last()
        product = []
        if isp is not None:
            ctx['isp']=isp.id
            p_ids= StockRecord.objects.filter(partner=isp)
            product = Product.objects.filter(stockrecords__in = p_ids,opening_date__lte=datetime.datetime.now().date())
        self.form_class.base_fields['product'].queryset = product
        ctx['form']=self.form_class(instance=self.object)
        return ctx

class StroeInComeDeleteView(generic.DeleteView):
    template_name = 'dashboard/business/storeincomapply_delete.html'
    model = StoreInComeApply

    def get_context_data(self, *args, **kwargs):
        ctx = super(StroeInComeDeleteView, self).get_context_data(*args, **kwargs)
        ctx['del_product'] = _(u"删除商品: '%s'") % self.object.product
        ctx['status'] = self.object.status
        return ctx

    def get_success_url(self):
        messages.info(self.request, _(u"成功删除"))
        return reverse("dashboard:storeincome-list")


class Pickup_ApplyListView(SingleTableMixin,generic.ListView):
    template_name = 'dashboard/business/pickup_apply_list.html'
    model = PickupDetail
    context_object_name = 'pickup_apply'
    table_class = Pickup_ApplyDashboard
    context_table_name = 'pickup_apply_tab'
    form_class = SearchPickProductForm

    def get_queryset(self):
        user = self.request.user
        queryset = super(Pickup_ApplyListView,self).get_queryset()
        if user.userprofile.role == 'dashboard_admin':
            queryset = queryset
        else:
            queryset = queryset.filter(stockrecords__partner__users=user,opening_date__lte=datetime.datetime.now().date())
        queryset = self.apply_search(queryset)
        return queryset


    def apply_search(self, queryset):
        """
        Filter the queryset and set the description according to the search
        parameters given
        """
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('product'):
            qs_match = queryset.filter(product__title=data['product'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__title__icontains=data['product'])

        if data.get('upc'):
            qs_match = queryset.filter(product__upc=data['upc'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__upc__icontains=data['upc'])

        if data.get('pickid'):
            qs_match = queryset.filter(pickup_list_id__pickup_no=data['pickid'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(pickup_list_id__pickup_no__icontains=data['pickid'])

        return queryset


    def get_table(self, **kwargs):
        table = super(Pickup_ApplyListView, self).get_table(**kwargs)
        table.caption = u'申请提货信息'
        return table

    def get_context_data(self, *args, **kwargs):
        ctx = super(Pickup_ApplyListView, self).get_context_data(*args, **kwargs)
        ctx['form']=self.form_class
        return ctx

class Product_QuotationListView(SingleTableMixin,generic.ListView):
    template_name = 'dashboard/business/product_quotation_list.html'
    model = StockTicker
    context_object_name = 'Product_Quotation'
    table_class = Product_QuotationDashboard
    context_table_name = 'Product_Quotation_tab'
    form_class = SearchProductApplyForm

    def get_queryset(self):
        queryset = super(Product_QuotationListView,self).get_queryset()
        user = self.ruquest.user
        queryset = queryset.filter(stockrecords__partner__users=user,opening_date__lte=datetime.datetime.now().date())
        queryset = self.apply_search(queryset)
        return queryset


    def get_table(self, **kwargs):
        table = super(Product_QuotationListView, self).get_table(**kwargs)
        table.caption = u'商品行情信息'
        return table

    def apply_search(self, queryset):
        """
        Filter the queryset and set the description according to the search
        parameters given
        """
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('product'):
            qs_match = queryset.filter(product__title=data['product'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__title__icontains=data['product'])

        if data.get('upc'):
            qs_match = queryset.filter(product__upc=data['upc'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__upc__icontains=data['upc'])

        return queryset

    def get_context_data(self, *args, **kwargs):
        ctx = super(Product_QuotationListView, self).get_context_data(*args, **kwargs)
        ctx['form']=self.form_class
        return ctx


class BusinessPickupStoreListView(SingleTableMixin, generic.TemplateView):
    template_name = 'dashboard/business/business_pickup_store_list.html'
    form_class = SearchBusinessStoreForm
    table_class = BusinessPickupStoreTable
    context_table_name = 'pickup_store_list'

    def get_queryset(self):
        user = self.request.user
        if user.userprofile.role == 'dashboard_admin':
            queryset = PickupStore.objects.all()
        else:
            business_products = Product.objects.filter(stockrecords__partner__users=user,opening_date__lte=datetime.datetime.now().date())
            queryset = PickupStore.objects.filter(product__in=business_products).distinct()
        queryset = self.apply_search(queryset)
        return queryset

    def apply_search(self, queryset):
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('product'):
            qs_match = queryset.filter(product__title=data['product'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__title__icontains=data['product'])

        if data.get('upc'):
            qs_match = queryset.filter(product__upc=data['upc'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__upc__icontains=data['upc'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(BusinessPickupStoreListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context


class PickupOutStoreListView(SingleTableMixin,generic.TemplateView):
    template_name = 'dashboard/business/pickup_outstore_list.html'
    form_class = SearchOutStoreForm
    table_class = PickupOutStoreTable
    context_table_name = 'pickup_apply_express_list'

    def get_queryset(self):
        user = self.request.user
        if user.userprofile.role == 'dashboard_admin':
            queryset = PickupDetail.objects.filter(status=2).values('product','product__title','product__upc','pickup_addr__name','pickup_type','status').annotate(quantity=Coalesce(Sum('quantity'),0))
        else:
            current_products = Product.objects.filter(stockrecords__partner__users=user,opening_date__lte=datetime.datetime.now().date())
            queryset = PickupDetail.objects.filter(status=2,product__in=current_products).values('product','product__title','product__upc','pickup_addr__name','pickup_type','status').annotate(quantity=Coalesce(Sum('quantity'),0))
        queryset = self.apply_search(queryset)
        return queryset

    def apply_search(self, queryset):
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('product'):
            qs_match = queryset.filter(product__title=data['product'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__title__icontains=data['product'])

        if data.get('upc'):
            qs_match = queryset.filter(product__upc=data['upc'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__upc__icontains=data['upc'])

        if data.get('pickup_addr'):
            qs_match = queryset.filter(pickup_addr__name=data['pickup_addr'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(pickup_addr__name__icontains=data['pickup_addr'])

        if data.get('status'):
            qs_match = queryset.filter(pickup_type=data['status'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(pickup_type__icontains=data['status'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(PickupOutStoreListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context


class BusinessProductListView(SingleTableMixin,generic.TemplateView):
    template_name = 'dashboard/business/business_product_list.html'
    form_class = SearchBusinessInProductForm
    table_class = BusinessProductTable
    context_table_name = 'business_product_list'

    def get(self,request,*args,**kwargs):
        context = self.get_context_data(**kwargs)

        if not request.GET.get('download'):
            return self.render_to_response(context)

        file = xlwt.Workbook()
        table = file.add_sheet('sheet1',cell_overwrite_ok=True)

        font0 = xlwt.Font()
        font0.name = 'Times New Roman'
        font0.colour_index = 2
        font0.bold = True
        style0 = xlwt.XFStyle()
        style0.font = font0

        caption = self.table_class.caption
        table.write(0,0,caption,style0)

        for k,v in enumerate(self.table_class.base_columns.values()):
            #table.write(1,2,b,)
            table.write(1,k,v.verbose_name)
        for i,v in enumerate(self.get_table_data()):
            table.write(2+i,0,v.stockid)
            table.write(2+i,1,v.user.userprofile.uid)
            table.write(2+i,2,v.user.partners.first().name)
            table.write(2+i,3,v.product.title)
            table.write(2+i,4,v.product.upc)
            table.write(2+i,5,v.product.stock_config_product.opening_price)
            table.write(2+i,6,v.number)
            table.write(2+i,7,v.quantity)

        fname = ur'%s.xls'%(caption,)

        agent=request.META.get('HTTP_USER_AGENT')
        if agent and re.search('MSIE',agent):
            response =HttpResponse(content_type="application/vnd.ms-excel") #解决ie不能下载的问题
            response['Content-Disposition'] ='attachment; filename=%s' %(fname.encode('utf-8'),) #解决文件名乱码/不显示的问题
        else:
            response = HttpResponse(content_type="application/ms-excel")
            response['Content-Disposition'] ='attachment; filename=%s' %(fname.encode('utf-8'),) #

        file.save(response)
        return response

    def get_queryset(self):
        user = self.request.user
        queryset = StockEnter.objects.filter(user=user)
        queryset = self.apply_search(queryset)
        return queryset

    def apply_search(self, queryset):
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('product'):
            qs_match = queryset.filter(product__title=data['product'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__title__icontains=data['product'])

        if data.get('upc'):
            qs_match = queryset.filter(product__upc=data['upc'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__upc__icontains=data['upc'])

        if data.get('status'):
            queryset = queryset.filter(status=data['status'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(BusinessProductListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

class BusinessProductCreateView(generic.CreateView):
    template_name = 'dashboard/business/business_product_create_update.html'
    model = StockEnter
    form_class = BusinessProductForm
    success_url = reverse_lazy('dashboard:business-product-store-list')

    def get_form_class(self):
        form_class = super(BusinessProductCreateView,self).get_form_class()
        user = self.request.user
        product = Product.objects.filter(trader=user,opening_date__lte=datetime.datetime.now().date())
        form_class.base_fields['product'].queryset = product
        return form_class
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.stocksave()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        # messages.success(self.request, _(u"新的商品 : '%s' 已入库") % self.object.product)
        return super(BusinessProductCreateView, self).get_success_url()

    def get_title(self):
        return _(u"增加商品入库")

    def get_context_data(self, *args, **kwargs):
        ctx = super(BusinessProductCreateView, self).get_context_data(*args, **kwargs)        
        return ctx

class BusinessProductUpdateView(generic.UpdateView):
    template_name = 'dashboard/business/business_product_create_update.html'
    model = StockEnter
    form_class = BusinessProductForm
    #context_object_name = ''
    success_url = reverse_lazy('dashboard:business-product-list')

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user
        self.object.stocksave()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, _(u"入库商品 : '%s' 已编辑") % self.object.product)
        return super(BusinessProductUpdateView, self).get_success_url()

    def get_title(self):
        return _(u"编辑商品入库")

    def get_context_data(self, *args, **kwargs):
        ctx = super(BusinessProductUpdateView, self).get_context_data(*args, **kwargs)
        user = self.request.user
        isp = Partner.objects.filter(users=user).first()
        product = []
        if isp is not None:
            p_ids= StockRecord.objects.filter(partner=isp)
            product = Product.objects.filter(stockrecords__in = p_ids,opening_date__lte=datetime.datetime.now().date())
        self.form_class.base_fields['product'].queryset = product
        ctx['form']=self.form_class(instance=self.object)
        return ctx

class BusinessProductDeleteView(generic.DeleteView):
    template_name = 'dashboard/business/business_product_delete.html'
    model = StockEnter

    def get_context_data(self, *args, **kwargs):
        ctx = super(BusinessProductDeleteView, self).get_context_data(*args, **kwargs)
        ctx['del_product'] = _(u"删除入库商品: '%s'") % self.object.product
        return ctx

    def get_success_url(self):
        messages.info(self.request, _(u"成功删除"))
        return reverse("dashboard:business-product-list")


class BusinessStockEnterDealListView(SingleTableMixin,generic.TemplateView):
    template_name = 'dashboard/business/business_stockenter_deal_list.html'
    form_class = SearchBusinessStockEnterDealForm
    table_class = BusinessStockEnterDealTable
    context_table_name = 'business_stockenter_deal_list'

    def get(self,request,*args,**kwargs):
        context = self.get_context_data(**kwargs)

        if not request.GET.get('download'):
            return self.render_to_response(context)

        file = xlwt.Workbook()
        table = file.add_sheet('sheet1',cell_overwrite_ok=True)

        font0 = xlwt.Font()
        font0.name = 'Times New Roman'
        font0.colour_index = 2
        font0.bold = True
        style0 = xlwt.XFStyle()
        style0.font = font0

        caption = self.table_class.caption
        table.write(0,0,caption,style0)

        for k,v in enumerate(self.table_class.base_columns.values()):
            #table.write(1,2,b,)
            table.write(1,k,v.verbose_name)
        for i,v in enumerate(self.get_table_data()):
            table.write(2+i,0,v.stockid)
            table.write(2+i,1,v.user.userprofile.uid)
            table.write(2+i,2,v.user.partners.first().name)
            table.write(2+i,3,v.product.title)
            table.write(2+i,4,v.product.upc)
            table.write(2+i,5,v.product.stock_config_product.opening_price)
            table.write(2+i,6,v.number)
            table.write(2+i,7,v.quantity)

        fname = ur'%s.xls'%(caption,)

        agent=request.META.get('HTTP_USER_AGENT')
        if agent and re.search('MSIE',agent):
            response =HttpResponse(content_type="application/vnd.ms-excel") #解决ie不能下载的问题
            response['Content-Disposition'] ='attachment; filename=%s' %(fname.encode('utf-8'),) #解决文件名乱码/不显示的问题
        else:
            response = HttpResponse(content_type="application/ms-excel")
            response['Content-Disposition'] ='attachment; filename=%s' %(fname.encode('utf-8'),) #

        file.save(response)
        return response

    def get_queryset(self):
        user = self.request.user
        try:
            member_unit = Partner.objects.filter(users=user).first()
            queryset = StockEnter.objects.filter(product__stockrecords__partner=member_unit).distinct()
            queryset = self.apply_search(queryset)
        except:
            queryset = []
        return queryset

    def apply_search(self, queryset):
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('product'):
            qs_match = queryset.filter(product__title=data['product'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__title__icontains=data['product'])

        if data.get('upc'):
            qs_match = queryset.filter(product__upc=data['upc'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__upc__icontains=data['upc'])

        if data.get('user'):
            qs_match = queryset.filter(user__username=data['user'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(user__username__icontains=data['user'])

        if data.get('status'):
            queryset = queryset.filter(status=data['status'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(BusinessStockEnterDealListView, self).get_context_data(**kwargs)
        context['form'] = self.form_class
        return context


class BusinessStockEnterDealView(generic.UpdateView):
    template_name = 'dashboard/business/business_stockenter_deal.html'
    model = StockEnter
    form_class = BusinessStockEnterDealForm
    success_url = reverse_lazy('dashboard:business-stockenter-deal-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.deal_user = self.request.user
        self.object.deal_datetime = datetime.datetime.now()
        self.object.stocksave()
        if self.object.status == '3':
            user_product = UserProduct.objects.get_or_create(user=self.object.user, product=self.object.product,trade_type=2)[0]
            user_product.quantity = F('quantity') + self.object.quantity
            user_product.custom_save()
        return HttpResponseRedirect(self.get_success_url())


class BusinessSaleListView(SingleTableMixin,generic.TemplateView):
    template_name = 'dashboard/business/business_sale_list.html'
    form_class = SearchSaleForm
    table_class = BusinessSaleTable
    context_table_name = 'business_sale_list'

    def get_queryset(self):
        user = self.request.user
        all_user = Partner.objects.values_list('users',flat=True)
        if user.userprofile.role == 'dashboard_admin':
            queryset = TradeComplete.objects.filter(commission_sale_user_id__in =all_user)
        else:
            product = Product.objects.filter(stockrecords__partner__users=user,opening_date__lte=datetime.datetime.now().date())
            queryset = TradeComplete.objects.filter(product__in=product,commission_sale_user_id=user)
        queryset = self.apply_search(queryset)
        return queryset

    def apply_search(self, queryset):
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data
        if data.get('product'):
            qs_match = queryset.filter(product__title=data['product'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__title__icontains=data['product'])

        if data.get('upc'):
            qs_match = queryset.filter(product__upc=data['upc'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__upc__icontains=data['upc'])

        if data.get('status'):
            qs_match = queryset.filter(c_type=data['status'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(c_type__icontains=data['status'])

        if data.get('isp'):
            qs_match = queryset.filter(commission_sale_user_id__partners__name=data['isp'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(commission_sale_user_id__partners__name__icontains=data['isp'])

        if data.get('begin_date'):
            queryset = queryset.filter(created_date__gte=data['begin_date'])

        if data.get('end_date'):
            queryset = queryset.filter(created_date__lte=data['end_date'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(BusinessSaleListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

class BusinessProfitListView(SingleTableMixin,generic.TemplateView):
    template_name = 'dashboard/business/business_profit_list.html'
    form_class = SearchBusinessForm
    table_class = BusinessProfitTable
    context_table_name = 'business_profit_list'

    sql1 = '''select a.id,a.commission_sale_user_id_id,
            a.title,a.upc,a.isp,a.quantity,a.avgprice,a.sales,
            a.profit,a.created_date,
            au.username isp_user from
            (select s.id,e.commission_sale_user_id_id,p.title ,p.upc,s.name isp,
            sum(e.quantity) as quantity,
            round(sum(e.total)/sum(e.quantity),2) as avgprice,
            sum(e.total) as sales,'''
    sql2 = '''
            sum(e.total)-sum(e.quantity)*f.opening_price as profit,
           '''
    sql3 = '''max(e.created_date) as created_date
            from  commission_tradecomplete e
            left join
            partner_stockrecord d
            on d.product_id = e.product_id
            left join
            commission_stockproductconfig f
            on f.product_id = e.product_id
            left join
            partner_partner s
            on d.partner_id = s.id
            left join
            catalogue_product p
            on e.product_id = p.id '''
    sql4= '''
            group by p.title,p.upc,e.commission_sale_user_id_id) a
            join
            partner_partner_users u
            on u.user_id = a.commission_sale_user_id_id
            and u.partner_id = a.id
            left join
            auth_user au
            on u.user_id = au.id '''


    def get_queryset(self):
        user = self.request.user
        sql = self.apply_search()
        if user.userprofile.role == 'dashboard_admin':
            queryset = TradeComplete.objects.raw(sql)
        else:
            sql = sql+' and u.user_id = %(user_id)s'
            queryset = TradeComplete.objects.raw(sql,{'user_id':user.id})
        return queryset

    def apply_search(self):
        self.form = self.form_class(self.request.GET)

        a_sql = '''
         where a.title like %(product)s and a.upc like %(upc)s
        and a.isp like %(business)s
        '''

        sql_par ={'product':'%(product)s',
                  'upc':'%(upc)s',
                  'business':'%(business)s',
                  }

        if not self.form.is_valid():
            return ''

        data = self.form.cleaned_data
        if data.get('product'):
            sql_par['product']= "'%%"+data['product']+"%%'"
        else:
            sql_par['product']="'%%'"

        if data.get('upc'):
            sql_par['upc']="'%%"+data['upc']+"%%'"
        else:
            sql_par['upc']="'%%'"

        if data.get('business'):
            sql_par['business']="'%%"+data['business']+"%%'"
        else:
            sql_par['business']="'%%'"

        if data.get('begin_date'):
            sql_3_1 = '''
            where e.created_date >= '%s'
            '''%(data['begin_date'])
        else:
            sql_3_1 = ''' where e.created_date >= '2002-01-01' '''

        if data.get('end_date'):
            sql_3_2 = '''
            and e.created_date <= '%s'
            '''%(data['end_date'])
        else:
            sql_3_2 = ''

        if data.get('price'):
            self.sql2 = '''sum(e.total)-sum(e.quantity)*%d as profit,'''%(data['price'])
        else :
            pass

        a_sql = a_sql%(sql_par)

        sql = self.sql1+self.sql2+self.sql3+sql_3_1+sql_3_2+self.sql4+a_sql
        print '----'
        print sql
        return sql

    def get_context_data(self, **kwargs):
        context = super(BusinessProfitListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

class BusinessBalanceListView(SingleTableMixin,generic.TemplateView):
    template_name = 'dashboard/business/business_balance_list.html'
    #form_class = SearchSaleForm
    table_class = BusinessBalanceTable
    context_table_name = 'business_balance_list'

    def get_queryset(self):
        user = self.request.user
        if user.userprofile.role == 'dashboard_admin':
            sql = '''
            select a.id,partner_id,user_id,sales,profit,balance,can_pickup_balance,
            p.name isp ,u.username isp_user from
           (select c.id,s.partner_id,u.user_id,
            sum(c.total) as sales ,
            sum(c.total)-f.opening_price*sum(c.quantity) as profit ,
            sum(c.total) as balance,
            sum(c.quantity)*min(c.unit_price) as can_pickup_balance
            from
            partner_stockrecord s
            join
            commission_tradecomplete c
            on s.product_id = c.product_id
            join
            commission_stockproductconfig f
            on f.product_id = s.product_id
            join
            partner_partner_users u
            on u.user_id = c.commission_sale_user_id_id
            and u.partner_id = s.partner_id
            group by s.partner_id,u.user_id)a
            left join
            partner_partner p
            on a.partner_id = p.id
            left join
            auth_user u
            on a.user_id = u.id ;
            '''
            queryset = TradeComplete.objects.raw(sql);
        else:
            sql = '''
            select a.id,partner_id,user_id,sales,profit,balance,can_pickup_balance
            ,p.name isp,u.username isp_user from
           (select c.id,s.partner_id,u.user_id,
            sum(c.total) as sales ,
            sum(c.total)-f.opening_price*sum(c.quantity) as profit ,
            sum(c.total) as balance,
            sum(c.quantity)*min(c.unit_price) as can_pickup_balance
            from
            partner_stockrecord s
            join
            commission_tradecomplete c
            on s.product_id = c.product_id
            join
            commission_stockproductconfig f
            on f.product_id = s.product_id
            join
            partner_partner_users u
            on u.user_id = c.commission_sale_user_id_id
            and u.partner_id = s.partner_id
            group by s.partner_id,u.user_id)a
            left join
            partner_partner p
            on a.partner_id = p.id
            left join
            auth_user u
            on a.user_id = u.id
            where a.user_id = %(user_id)s
            '''
            queryset = TradeComplete.objects.raw(sql,{'user_id':user.id});

        queryset = self.apply_search(queryset)
        return queryset

    def apply_search(self, queryset):
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BusinessBalanceListView, self).get_context_data(**kwargs)
        #context['form'] = self.form
        return context


class BusinessLoginView(generic.FormView):
    template_name = 'dashboard/business/login.html'
    form_class = BusinessLoginForm
    success_url = '/dashboard/business/storeincome/list/'

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        response = HttpResponseRedirect(self.get_success_url())
        return response


class TraderLoginView(generic.FormView):
    template_name = 'dashboard/business/trader_login.html'
    form_class = TraderLoginForm
    success_url = reverse_lazy('dashboard:business-product-store-list')

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        response = HttpResponseRedirect(self.get_success_url())
        return response

class PartnerUserListView(generic.ListView):
    model = get_user_model()
    context_object_name = 'users'
    template_name = 'dashboard/business/partner_list.html'
    form_class = PartnerUserSearchForm

    def get_queryset(self):
        user = self.request.user
        qs = self.model._default_manager.filter(partners__users=user)        
        qs = sort_queryset(qs, self.request, ['user.userprofile.role'])

        self.description = u'会员单位用户'

        # We track whether the queryset is filtered to determine whether we
        # show the search form 'reset' button.
        self.is_filtered = False
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return qs

        data = self.form.cleaned_data

        if data['userrole']:
            if data['userrole']=='extra_role':
                qs = qs.filter(userprofile__role__in=['ISP','dashboard_admin','warehouse_staff'])
            else :
                qs = qs.filter(userprofile__role__icontains=data['userrole'])
            self.description = u"查询 '%s'" % data['userrole']
            self.is_filtered = True

        return qs

    def get_context_data(self, **kwargs):
        ctx = super(PartnerUserListView, self).get_context_data(**kwargs)
        ctx['queryset_description'] = self.description
        ctx['form'] = self.form
        ctx['is_filtered'] = self.is_filtered
        ctx['partner'] = get_object_or_404(Partner,users=self.request.user)
        return ctx

class ExpressSendListView(SingleTableMixin,generic.TemplateView):
    template_name = 'dashboard/business/express_send_list.html'
    form_class = SearchPickProductForm
    table_class = ExpressSendTable
    context_table_name = 'express_send_list'
    
    def get_queryset(self):
        if self.request.user.userprofile.role == 'dashboard_admin':
            queryset = PickupDetail.objects.filter(pickup_type=3).order_by('pickup_list_id')
        else:
            queryset = PickupDetail.objects.filter(product__stockrecords__partner__users=self.request.user, pickup_type=3).distinct()
        queryset = self.apply_search(queryset)
        return queryset

    def apply_search(self, queryset):
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('pickid'):
            qs_match = queryset.filter(pickup_list_id__pickup_no=data['pickid'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(pickup_list_id__pickup_no__icontains=data['pickup_list'])

        if data.get('product'):
            qs_match = queryset.filter(product__title=data['product'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__title__icontains=data['product'])

        if data.get('upc'):
            qs_match = queryset.filter(product__upc=data['upc'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__upc__icontains=data['upc'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(ExpressSendListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

class ExpressSendDealView(generic.UpdateView):
    template_name = 'dashboard/business/express_send_deal.html'
    model = PickupDetail
    context_object_name = 'express_send'
    form_class = ExpressSendForm

    def __init__(self, *args, **kwargs):
        super(ExpressSendDealView, self).__init__(*args, **kwargs)
        self.success_url = reverse('dashboard:express-send-list')

    def get_context_data(self, **kwargs):
        context = super(ExpressSendDealView, self).get_context_data(**kwargs)
        context['today'] = datetime.datetime.today()
        return context

    def get_form_kwargs(self):
        kwargs = super(ExpressSendDealView, self).get_form_kwargs()
        if self.object.pickup_type == 1:
            kwargs['deal_type'] = 'pickup'
        else:
            kwargs['deal_type'] = 'express'
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        self.object.deal_datetime = datetime.datetime.now()
        self.object.deal_user = self.request.user
        self.object.save()
        if self.object.status == 5:
            # user money change
            pickup_total_price = float(self.object.pickup_fee) + float(self.object.express_fee)
            user_money_change = UserMoneyChange()
            user_money_change.user = self.object.pickup_list_id.user
            user_money_change.status = 2
            user_money_change.trade_type = 12
            user_money_change.price = pickup_total_price
            user_money_change.pickup_amount = pickup_total_price
            user_money_change.pickup_list = self.object.pickup_list_id
            user_money_change.custom_save()

        elif self.object.status == 3:
 
            # UserProduct and TradeComplete change
            user_product = UserProduct.objects.get(user=self.object.pickup_list_id.user, product=self.object.product, trade_type=self.object.trade_type)
            user_product.total_pickup_quantity -= self.object.quantity
            user_product.can_pickup_quantity += self.object.quantity
            user_product.quantity += self.object.quantity

            pickup_quantity = self.object.quantity
            current_tc_list = list(TradeComplete.objects.filter(
                Q(commission_buy_user_id=self.object.pickup_list_id.user, product=self.object.product, c_type=self.object.trade_type, can_pickup_quantity=0)|
                Q(commission_buy_user_id=self.object.pickup_list_id.user, product=self.object.product, c_type=self.object.trade_type, can_pickup_quantity__gt=0, quantity__gt=F('can_pickup_quantity'))).order_by('-created_datetime')) # tc is short for TradeComplete
            for i in xrange(len(current_tc_list)):
                current_tc = current_tc_list[i]
                if pickup_quantity > (current_tc.quantity - current_tc.can_pickup_quantity):
                    pickup_quantity -= (current_tc.quantity - current_tc.can_pickup_quantity)
                    current_tc.can_pickup_quantity = current_tc.quantity
                    current_tc.save()
                else:
                    current_tc.can_pickup_quantity += pickup_quantity
                    current_tc.save()
                    break
                    if i == len(current_tc_list) - 1:
                        user_product.overage_unit_price = current_tc.unit_price
                    else:
                        total_price = 0
                        total_quantity = 0
                        for tc in current_tc_list[i:]:
                            total_price += tc.unit_price * tc.can_pickup_quantity
                            total_quantity += tc.can_pickup_quantity
                        user_product.overage_unit_price = total_price / total_quantity
                    break
            stock_tc_list = TradeComplete.objects.filter(
                commission_buy_user_id=self.object.pickup_list_id.user, product=self.object.product, c_type=self.object.trade_type, can_pickup_quantity__gt=0)
            total_price = 0
            total_quantity = 0
            for tc in stock_tc_list:
                total_price += tc.unit_price * tc.can_pickup_quantity
                total_quantity += tc.can_pickup_quantity
            user_product.overage_unit_price = total_price / total_quantity
            user_product.save()

            # user money change
            pickup_total_price = float(self.object.pickup_fee) + float(self.object.express_fee)
            user_money_change = UserMoneyChange()
            user_money_change.user = self.object.pickup_list_id.user
            user_money_change.status = 2
            user_money_change.trade_type = 11
            user_money_change.price = pickup_total_price
            user_money_change.pickup_amount = pickup_total_price
            user_money_change.pickup_list = self.object.pickup_list_id
            user_money_change.custom_save()

        return HttpResponseRedirect(self.get_success_url())

class TraderProductListView(SingleTableMixin, generic.TemplateView):
    template_name = 'dashboard/business/trader_product_list.html'
    paginate_by = 20
    form_class = SearchProductApplyForm
    table_class = TraderProductTable
    context_table_name = 'product_list'

    def get_table_pagination(self):
        return dict(per_page=20)

    def get_queryset(self):
        queryset = Product.objects.filter(trader=self.request.user)
        queryset = self.apply_search(queryset)
        return queryset

    def apply_search(self, queryset):
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('product'):
            qs_match = queryset.filter(product__title=data['product'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__title__icontains=data['product'])

        if data.get('upc'):
            qs_match = queryset.filter(product__upc=data['upc'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__upc__icontains=data['upc'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(TraderProductListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context
    
class TraderSaleListView(SingleTableMixin,generic.TemplateView):
    template_name = 'dashboard/business/trader_sale_list.html'
    form_class = SearchSaleForm
    table_class = BusinessSaleTable
    context_table_name = 'trader_sale_list'

    def get_queryset(self):
        user = self.request.user
        if user.userprofile.role == 'trader':
            queryset = TradeComplete.objects.filter(commission_sale_user_id=user)
        else :
            queryset = TradeComplete.objects.none()
        queryset = self.apply_search(queryset)
        return queryset

    def apply_search(self, queryset):
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return queryset
        data = self.form.cleaned_data

        if data.get('product'):
            qs_match = queryset.filter(product__title=data['product'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__title__icontains=data['product'])

        if data.get('upc'):
            qs_match = queryset.filter(product__upc=data['upc'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__upc__icontains=data['upc'])

        if data.get('status'):
            qs_match = queryset.filter(c_type=data['status'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(c_type__icontains=data['status'])

        if data.get('isp'):
            qs_match = queryset.filter(commission_sale_user_id__partners__name=data['isp'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(commission_sale_user_id__partners__name__icontains=data['isp'])

        if data.get('begin_date'):
            queryset = queryset.filter(created_date__gte=data['begin_date'])

        if data.get('end_date'):
            queryset = queryset.filter(created_date__lte=data['end_date'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(TraderSaleListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context
