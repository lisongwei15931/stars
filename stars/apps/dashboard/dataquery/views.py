#coding=utf-8

from django.views import generic
from django_tables2 import SingleTableMixin
from itertools import chain
from django.db.models import F, Sum, Avg
from datetime import datetime,timedelta


from stars.apps.commission.models import CommissionBuy,CommissionSale,TradeComplete,UserProduct,UserAssetDailyReport
from stars.apps.dashboard.dataquery.tables import (CommissionQueryTable,TradeCompleteQueryTable,
                                                   HoldProductQueryTable,StoreProductQueryTable,
                                                   StoreProductQueryAllTable,CapitalQueryTable)
from stars.apps.dashboard.dataquery.forms import (CommissionQuerySearchForm,CommissionQueryAllSearchForm,
                                                  TradecompleteQuerySearchForm,TradecompleteQueryAllSearchForm,
                                                  HoldProductSearchForm,UserSearchForm,CapitalSearchForm)

class CommissionQueryListView(SingleTableMixin, generic.TemplateView):
    '''
    #当日委托查询
    '''
    template_name = 'dashboard/dataquery/commission_query_list.html'
    form_class = CommissionQuerySearchForm
    table_class = CommissionQueryTable
    context_table_name = 'commission_query_list'

    def get_queryset(self):
        today = datetime.today().date()
        queryset_buy = CommissionBuy.objects.filter(created_datetime__gte=today)
        queryset_sale = CommissionSale.objects.filter(created_datetime__gte=today)

        queryset_buy = self.apply_search(queryset_buy,flag=True)
        queryset_sale = self.apply_search(queryset_sale)
        queryset = chain(queryset_buy,queryset_sale)
        return queryset

    def apply_search(self, queryset,flag=False):
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

        if data.get('isp'):
            qs_match = queryset.filter(product__stockrecords__partner__name=data['isp'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__stockrecords__partner__name__icontains=data['isp'])

        if data.get('commission_no'):
            if flag:
                sql = '''
                SELECT b.* FROM commission_commissionbuy b
                WHERE CONCAT('B',LPAD(id,8,'0')) = %(buy_no)s
                AND b.created_datetime >= CURDATE()'''
                queryset = queryset.raw(sql, {'buy_no': data['commission_no']})
            else:
                sql = '''
                SELECT s.* FROM commission_commissionsale s
                WHERE CONCAT('S',LPAD(id,8,'0')) = %(buy_no)s
                AND b.created_datetime >= CURDATE() '''
                queryset = queryset.raw(sql, {'buy_no': data['commission_no']})
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CommissionQueryListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

class CommissionQueryAllListView(SingleTableMixin, generic.TemplateView):
    '''
    #历史委托查询
    '''
    template_name = 'dashboard/dataquery/commission_query_list.html'
    form_class = CommissionQueryAllSearchForm
    table_class = CommissionQueryTable
    context_table_name = 'commission_query_list'

    def get_queryset(self):
        queryset_buy = CommissionBuy.objects.all()
        queryset_sale = CommissionSale.objects.all()

        queryset_buy = self.apply_search(queryset_buy,flag=True)
        queryset_sale = self.apply_search(queryset_sale)
        queryset = chain(queryset_buy,queryset_sale)
        return queryset

    def apply_search(self, queryset,flag=False):
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

        if data.get('isp'):
            qs_match = queryset.filter(product__stockrecords__partner__name=data['isp'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__stockrecords__partner__name__icontains=data['isp'])

        if data.get('begin_date'):
            queryset = queryset.filter(created_datetime__gte=data['begin_date'])
        if data.get('end_date'):
            queryset = queryset.filter(created_datetime__lte=data['end_date'])

        if data.get('commission_no'):
            if flag:
                sql = '''
                SELECT b.* FROM commission_commissionbuy b
                WHERE CONCAT('B',LPAD(id,8,'0')) = %(buy_no)s'''
                queryset = queryset.raw(sql, {'buy_no': data['commission_no']})
            else:
                sql = '''
                SELECT s.* FROM commission_commissionsale s
                WHERE CONCAT('S',LPAD(id,8,'0')) = %(buy_no)s'''
                queryset = queryset.raw(sql, {'buy_no': data['commission_no']})
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CommissionQueryAllListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

class TradeCompleteQueryListView(SingleTableMixin, generic.TemplateView):
    '''
    #当日成交查询
    '''
    template_name = 'dashboard/dataquery/tradecomplate_query_list.html'
    form_class = TradecompleteQuerySearchForm
    table_class = TradeCompleteQueryTable
    context_table_name = 'tradecomplate_query_list'

    def get_queryset(self):
        today = datetime.today().date()
        queryset = TradeComplete.objects.filter(created_datetime__gte=today)
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

        if data.get('isp'):
            qs_match = queryset.filter(product__stockrecords__partner__name=data['isp'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__stockrecords__partner__name__icontains=data['isp'])

        if data.get('trade_no'):
            qs_match = queryset.filter(trade_no=data['trade_no'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(trade_no__icontains=data['trade_no'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(TradeCompleteQueryListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

class TradeCompleteQueryAllListView(SingleTableMixin, generic.TemplateView):
    '''
    #历史成交查询
    '''
    template_name = 'dashboard/dataquery/tradecomplate_query_list.html'
    form_class = TradecompleteQueryAllSearchForm
    table_class = TradeCompleteQueryTable
    context_table_name = 'tradecomplate_query_list'

    def get_queryset(self):
        queryset = TradeComplete.objects.all()
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

        if data.get('isp'):
            qs_match = queryset.filter(product__stockrecords__partner__name=data['isp'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__stockrecords__partner__name__icontains=data['isp'])

        if data.get('begin_date'):
            queryset = queryset.filter(created_datetime__gte=data['begin_date'])
        if data.get('end_date'):
            queryset = queryset.filter(created_datetime__lte=data['end_date'])

        if data.get('trade_no'):
            qs_match = queryset.filter(trade_no=data['trade_no'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(trade_no__icontains=data['trade_no'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(TradeCompleteQueryAllListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

class HoldProductListView(SingleTableMixin, generic.TemplateView):
    '''
    #当日持有查询
    '''
    template_name = 'dashboard/dataquery/hold_product_list.html'
    form_class = HoldProductSearchForm
    table_class = HoldProductQueryTable
    context_table_name = 'hold_product_list'

    def get_queryset(self):
        today = datetime.today().date()
        queryset = UserProduct.objects.filter(created_date__gte=today)
        queryset = self.apply_search(queryset).values('product', 'created_date').\
            annotate(unit_price=Avg('overage_unit_price'), quantity=Sum('quantity'), can_pickup=Sum('can_pickup_quantity'),\
            pickup=Sum('total_pickup_quantity'))

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

        if data.get('isp'):
            qs_match = queryset.filter(product__stockrecords__partner__name=data['isp'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__stockrecords__partner__name__icontains=data['isp'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(HoldProductListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

class StoreProductListView(SingleTableMixin, generic.TemplateView):
    '''
    #当日存货查询
    '''
    template_name = 'dashboard/dataquery/store_product_list.html'
    form_class = HoldProductSearchForm
    table_class = StoreProductQueryTable
    context_table_name = 'store_product_list'

    def get_queryset(self):
        today = datetime.today().date()
        queryset = UserProduct.objects.filter(created_date__gte=today)
        queryset = self.apply_search(queryset).values('product', 'created_date').\
            annotate(unit_price=Avg('overage_unit_price'), quantity=Sum('quantity'), can_pickup=Sum('can_pickup_quantity'),\
            pickup=Sum('total_pickup_quantity'))

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

        if data.get('isp'):
            qs_match = queryset.filter(product__stockrecords__partner__name=data['isp'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__stockrecords__partner__name__icontains=data['isp'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(StoreProductListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

class StoreProductAllListView(SingleTableMixin, generic.TemplateView):
    '''
    #统计所有存货查询
    '''
    template_name = 'dashboard/dataquery/store_product_list.html'
    form_class = HoldProductSearchForm
    table_class = StoreProductQueryAllTable
    context_table_name = 'store_product_list'

    def get_queryset(self):
        queryset = UserProduct.objects.all()
        queryset = self.apply_search(queryset).values('product').\
            annotate(unit_price=Avg('overage_unit_price'), quantity=Sum('quantity'), can_pickup=Sum('can_pickup_quantity'),\
            buy=Sum('total_buy_quantity'), sale=Sum('total_sale_quantity'), pickup=Sum('total_pickup_quantity'))

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

        if data.get('isp'):
            qs_match = queryset.filter(product__stockrecords__partner__name=data['isp'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(product__stockrecords__partner__name__icontains=data['isp'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(StoreProductAllListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context


class CapitalQueryListView(SingleTableMixin, generic.TemplateView):
    '''
    # 当日资金查询
    '''
    template_name = 'dashboard/dataquery/capital_query_list.html'
    form_class = UserSearchForm
    table_class = CapitalQueryTable
    context_table_name = 'capital_list'

    def get_queryset(self):
        today = datetime.today().date()
        queryset = UserAssetDailyReport.objects.filter(target_date__gte=today)
        queryset = self.apply_search(queryset)
        return queryset

    def get_table(self, **kwargs):
        table = super(CapitalQueryListView,self).get_table(**kwargs)
        table.caption = u'当日资金查询'
        return table

    def apply_search(self, queryset):
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return queryset
        data = self.form.cleaned_data

        if data.get('user'):
            qs_match = queryset.filter(user__username=data['user'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(user__username__icontains=data['user'])

        if data.get('role'):
            qs_match = queryset.filter(user__userprofile__role=data['role'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(user__userprofile__role__icontains=data['role'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(CapitalQueryListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

class CapitalQueryAllListView(SingleTableMixin, generic.TemplateView):
    '''
    # 历史资金查询
    '''
    template_name = 'dashboard/dataquery/capital_query_list.html'
    form_class = CapitalSearchForm
    table_class = CapitalQueryTable
    context_table_name = 'capital_list'

    def get_queryset(self):
        queryset = UserAssetDailyReport.objects.all()
        queryset = self.apply_search(queryset)
        return queryset

    def get_table(self, **kwargs):
        table = super(CapitalQueryAllListView,self).get_table(**kwargs)
        table.caption = u'历史资金查询'
        return table

    def apply_search(self, queryset):
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return queryset
        data = self.form.cleaned_data

        if data.get('user'):
            qs_match = queryset.filter(user__username=data['user'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(user__username__icontains=data['user'])

        if data.get('role'):
            qs_match = queryset.filter(user__userprofile__role=data['role'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(user__userprofile__role__icontains=data['role'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(CapitalQueryAllListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context