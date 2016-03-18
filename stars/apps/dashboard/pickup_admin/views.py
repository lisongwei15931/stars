# -*- coding: utf-8 -*-s

import datetime

from django_tables2 import SingleTableMixin

from django.contrib import messages
from django.shortcuts import render
from django.db.models import F
from django.db.models.query_utils import Q
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, UpdateView, ListView, DeleteView, CreateView, FormView
from django.contrib.auth import login as auth_login, logout as auth_logout

from oscar.core.loading import get_class, get_classes, get_model

(PickupStoreTable, PickupDetailTable, PickupDetailDealTable,
    StoreInComeApplyTable, StoreInComeTable,
    PickupStatisticsTable) = get_classes('dashboard.pickup_admin.tables',
        ('PickupStoreTable', 'PickupDetailTable', 'PickupDetailDealTable',
         'StoreInComeApplyTable', 'StoreInComeTable', 'PickupStatisticsTable'))

(PickupStoreSearchForm, PickupDetailSearchForm, StoreInComeApplySearchForm,
    StoreInComeApplyForm, StoreInComeSearchForm, StoreInComeForm,
    PickupDetailForm, PickupStatisticsSearchForm, LoginForm) = get_classes('dashboard.pickup_admin.forms',
        ('PickupStoreSearchForm', 'PickupDetailSearchForm',
        'StoreInComeApplySearchForm', 'StoreInComeApplyForm',
        'StoreInComeSearchForm', 'StoreInComeForm', 'PickupDetailForm',
        'PickupStatisticsSearchForm', 'LoginForm'))

PickupStore = get_model('pickup_admin', 'PickupStore')
StoreInCome = get_model('pickup_admin', 'StoreInCome')
StoreInComeApply = get_model('pickup_admin', 'StoreInComeApply')
PickupStatistics = get_model('pickup_admin', 'PickupStatistics')
PickupAddr = get_model('commission', 'PickupAddr')
PickupDetail = get_model('commission', 'PickupDetail')
PickupList = get_model('commission', 'PickupList')
TradeComplete = get_model('commission', 'TradeComplete')
UserProduct = get_model('commission', 'UserProduct')
UserMoneyChange = get_model('commission', 'UserMoneyChange')


class PickupStoreListView(SingleTableMixin, TemplateView):
    template_name = 'dashboard/pickup_admin/pickup_store_list.html'
    paginate_by = 20
    # context_object_name = 'pickup_store_list'
    form_class = PickupStoreSearchForm
    table_class = PickupStoreTable
    context_table_name = 'pickup_store_list'

    '''
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            if (self.get_paginate_by(self.object_list) is not None
                and hasattr(self.object_list, 'exists')):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
                        % {'class_name': self.__class__.__name__})
        context = self.get_context_data()
        return self.render_to_response(context)
    def get_table(self, **kwargs):
        if 'recently_edited' in self.request.GET:
            kwargs.update(dict(orderable=False))

        table = super(PickupStoreListView, self).get_table(**kwargs)
        # table.caption = self.get_description(self.form)
        return table
    '''

    def get_table_pagination(self):
        return dict(per_page=20)

    def get_queryset(self):
        if self.request.user.userprofile.role == 'dashboard_admin':
            queryset = PickupStore.objects.all()
        else:
            current_pickupaddr = PickupAddr.objects.filter(staff=self.request.user)
            queryset = PickupStore.objects.filter(pickup_addr__in=current_pickupaddr).distinct()
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

        return queryset

    def get_context_data(self, **kwargs):
        context = super(PickupStoreListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context


class PickupApplyListView(SingleTableMixin, TemplateView):
    template_name = 'dashboard/pickup_admin/pickup_apply_list.html'
    paginate_by = 20
    form_class = PickupDetailSearchForm
    table_class = PickupDetailTable
    context_table_name = 'pickup_apply_list'

    def get_table_pagination(self):
        return dict(per_page=20)

    def get_queryset(self):
        if self.request.user.userprofile.role == 'dashboard_admin':
            queryset = PickupDetail.objects.filter(pickup_type__in=[1, 2], status__in=[2, 3, 5, 6]).order_by('status')
        else:
            current_pickupaddr = PickupAddr.objects.filter(staff=self.request.user)
            queryset = PickupDetail.objects.filter(pickup_addr__in=current_pickupaddr, status__in=[2, 3, 5, 6]).order_by('status').distinct()
        queryset = self.apply_search(queryset)
        return queryset

    def apply_search(self, queryset):
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('pickup_list'):
            qs_match = queryset.filter(pickup_list_id__pickup_no=data['pickup_list'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(pickup_list_id__pickup_no__icontains=data['pickup_list'])

        if data.get('pickup_captcha'):
            qs_match = queryset.filter(pickup_captcha=data['pickup_captcha'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(pickup_captcha__icontains=data['pickup_captcha'])

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
        context = super(PickupApplyListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context


class StoreInComeApplyListView(SingleTableMixin, TemplateView):
    template_name = 'dashboard/pickup_admin/store_income_apply_list.html'
    paginate_by = 20
    form_class = StoreInComeApplySearchForm
    table_class = StoreInComeApplyTable
    context_table_name = 'store_income_apply_list'

    def get_table_pagination(self):
        return dict(per_page=20)

    def get_queryset(self):
        if self.request.user.userprofile.role == 'dashboard_admin':
            queryset = StoreInComeApply.objects.all().order_by('status')
        else:
            current_pickupaddr = PickupAddr.objects.filter(staff=self.request.user)
            queryset = StoreInComeApply.objects.filter(pickup_addr__in=current_pickupaddr).distinct()
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
            qs_match = queryset.filter(isp__name=data['isp'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(isp__name__icontains=data['isp'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(StoreInComeApplyListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context


class StoreInComeApplyUpdateView(UpdateView):

    template_name = 'dashboard/pickup_admin/store_income_apply.html'
    model = StoreInComeApply
    context_object_name = 'store_income_apply'
    form_class = StoreInComeApplyForm

    def __init__(self, *args, **kwargs):
        super(StoreInComeApplyUpdateView, self).__init__(*args, **kwargs)
        self.success_url = reverse('dashboard:store-income-apply-list')

    def get_context_data(self, **kwargs):
        context = super(StoreInComeApplyUpdateView, self).get_context_data(**kwargs)
        context['today'] = datetime.datetime.today()
        return context

    def form_valid(self, form):
        self.object = form.save()
        if self.object.damaged_quantity == 0 and self.object.lose_quantity == 0:
            self.object.status = '4'
        else:
            self.object.status = '1'
        self.object.deal_user = self.request.user
        self.object.deal_datetime = datetime.datetime.now()
        self.object.save()
        if self.object.status == '4':
            current_pickup_store = PickupStore.objects.get_or_create(pickup_addr=self.object.pickup_addr,
                                                                     product=self.object.product)[0]
            current_pickup_store.quantity = current_pickup_store.quantity + self.object.in_quantity
            current_pickup_store.save()

        return HttpResponseRedirect(self.get_success_url())


class StoreInComeListView(SingleTableMixin, TemplateView):
    template_name = 'dashboard/pickup_admin/store_income_list.html'
    paginate_by = 20
    form_class = StoreInComeSearchForm
    table_class = StoreInComeTable
    context_table_name = 'store_income_list'

    def get_table_pagination(self):
        return dict(per_page=20)

    def get_queryset(self):
        if self.request.user.userprofile.role == 'dashboard_admin':
            queryset = StoreInCome.objects.all().order_by('status')
        else:
            current_pickupaddr = PickupAddr.objects.filter(staff=self.request.user)
            queryset = StoreInCome.objects.filter(pickup_addr__in=current_pickupaddr).distinct()
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
            qs_match = queryset.filter(isp__name=data['isp'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(isp__name__icontains=data['isp'])

        return queryset

        return queryset

    def get_context_data(self, **kwargs):
        context = super(StoreInComeListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context


class StoreInComeUpdateView(UpdateView):

    template_name = 'dashboard/pickup_admin/store_income_update.html'
    model = StoreInCome
    context_object_name = 'store_income'
    form_class = StoreInComeForm

    def __init__(self, *args, **kwargs):
        super(StoreInComeUpdateView, self).__init__(*args, **kwargs)
        self.success_url = reverse('dashboard:store-income-list')

    def get_context_data(self, **kwargs):
        context = super(StoreInComeUpdateView, self).get_context_data(**kwargs)
        context['today'] = datetime.datetime.today()
        return context
    '''
    def form_valid(self, form):
        self.object = form.save()
        self.object.deal_user = self.request.user
        self.object.deal_datetime = datetime.datetime.now()
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())
    '''


class StoreInComeCreateView(CreateView):
    template_name = 'dashboard/pickup_admin/store_income_create.html'
    model = StoreInCome
    context_object_name = 'store_income'
    form_class = StoreInComeForm

    def __init__(self, *args, **kwargs):
        super(StoreInComeCreateView, self).__init__(*args, **kwargs)
        self.success_url = reverse('dashboard:store-income-list')

    def get_context_data(self, **kwargs):
        context = super(StoreInComeCreateView, self).get_context_data(**kwargs)
        context['today'] = datetime.datetime.today()
        return context


class PickupApplyPickupListView(SingleTableMixin, TemplateView):
    template_name = 'dashboard/pickup_admin/pickup_apply_pickup_list.html'
    paginate_by = 20
    form_class = PickupDetailSearchForm
    table_class = PickupDetailDealTable
    context_table_name = 'pickup_apply_pickup_list'

    def get_table_pagination(self):
        return dict(per_page=20)

    def get_queryset(self):
        if self.request.user.userprofile.role == 'dashboard_admin':
            # queryset = PickupDetail.objects.filter(pickup_type=1, status__in=[1, 4]).order_by('pickup_list_id')
            queryset = PickupDetail.objects.filter(pickup_type=1).order_by('pickup_list_id')
        else:
            current_pickupaddr = PickupAddr.objects.filter(staff=self.request.user)
            queryset = PickupDetail.objects.filter(pickup_addr__in=current_pickupaddr, pickup_type=1).distinct()
        queryset = self.apply_search(queryset)
        return queryset

    def apply_search(self, queryset):
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('pickup_list'):
            qs_match = queryset.filter(pickup_list_id__pickup_no=data['pickup_list'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(pickup_list_id__pickup_no__icontains=data['pickup_list'])

        if data.get('pickup_captcha'):
            qs_match = queryset.filter(pickup_captcha=data['pickup_captcha'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(pickup_captcha__icontains=data['pickup_captcha'])

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
        context = super(PickupApplyPickupListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context


class PickupOutcomeDealView(UpdateView):

    template_name = 'dashboard/pickup_admin/pickup_outcome_deal.html'
    model = PickupDetail
    context_object_name = 'pickup_detail'
    form_class = PickupDetailForm

    def __init__(self, *args, **kwargs):
        super(PickupOutcomeDealView, self).__init__(*args, **kwargs)
        self.success_url = reverse('dashboard:pickup-apply-pickup-list')

    def get_context_data(self, **kwargs):
        context = super(PickupOutcomeDealView, self).get_context_data(**kwargs)
        context['today'] = datetime.datetime.today()
        context['status'] = self.object.status
        return context

    def get_form_kwargs(self):
        kwargs = super(PickupOutcomeDealView, self).get_form_kwargs()
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
        if self.object.status == 2:
            # pickup stone change
            current_pickup_store = PickupStore.objects.get_or_create(pickup_addr=self.object.pickup_addr,
                                                                     product=self.object.product)[0]
            current_pickup_store.locked_quantity = current_pickup_store.locked_quantity - self.object.quantity
            current_pickup_store.save()
            # pickup statistics change
            current_pickup_statistics = PickupStatistics.objects.get_or_create(pickup_addr=self.object.pickup_addr,
                                                                               product=self.object.product,
                                                                               pickup_type='1')[0]
            current_pickup_statistics.quantity = current_pickup_statistics.quantity + self.object.quantity
            current_pickup_statistics.save()

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
            # Pickup Store change
            current_pickup_store = PickupStore.objects.get_or_create(pickup_addr=self.object.pickup_addr,
                                                                     product=self.object.product)[0]
            current_pickup_store.quantity = current_pickup_store.quantity + self.object.quantity
            current_pickup_store.locked_quantity = current_pickup_store.locked_quantity - self.object.quantity
            current_pickup_store.save()

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


class PickupApplyExpressListView(SingleTableMixin, TemplateView):
    template_name = 'dashboard/pickup_admin/pickup_apply_express_list.html'
    paginate_by = 20
    form_class = PickupDetailSearchForm
    table_class = PickupDetailDealTable
    context_table_name = 'pickup_apply_express_list'

    def get_table_pagination(self):
        return dict(per_page=20)

    def get_queryset(self):
        if self.request.user.userprofile.role == 'dashboard_admin':
            queryset = PickupDetail.objects.filter(pickup_type=2, status=4).order_by('pickup_list_id')
        else:
            current_pickupaddr = PickupAddr.objects.filter(staff=self.request.user)
            queryset = PickupDetail.objects.filter(pickup_type=2, status=4, pickup_addr__in=current_pickupaddr).distinct()
        queryset = self.apply_search(queryset)
        return queryset

    def apply_search(self, queryset):
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('pickup_list'):
            qs_match = queryset.filter(pickup_list_id__pickup_no=data['pickup_list'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(pickup_list_id__pickup_no__icontains=data['pickup_list'])

        if data.get('pickup_captcha'):
            qs_match = queryset.filter(pickup_captcha=data['pickup_captcha'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(pickup_captcha__icontains=data['pickup_captcha'])

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
        context = super(PickupApplyExpressListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context


class ExpressOutcomeDealView(UpdateView):

    template_name = 'dashboard/pickup_admin/express_outcome_deal.html'
    model = PickupDetail
    context_object_name = 'pickup_detail'
    form_class = PickupDetailForm

    def __init__(self, *args, **kwargs):
        super(ExpressOutcomeDealView, self).__init__(*args, **kwargs)
        self.success_url = reverse('dashboard:pickup-apply-pickup-list')

    def get_context_data(self, **kwargs):
        context = super(ExpressOutcomeDealView, self).get_context_data(**kwargs)
        context['today'] = datetime.datetime.today()
        return context

    def get_form_kwargs(self):
        kwargs = super(ExpressOutcomeDealView, self).get_form_kwargs()
        kwargs['deal_type'] = 'express'
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        self.object.deal_datetime = datetime.datetime.now()
        self.object.save()
        if self.object.status == 5:
            # pickup stone change
            current_pickup_store = PickupStore.objects.get_or_create(pickup_addr=self.object.pickup_addr,
                                                                     product=self.object.product)[0]
            current_pickup_store.locked_quantity = current_pickup_store.locked_quantity - self.object.quantity
            current_pickup_store.save()
            # pickup statistics change
            current_pickup_statistics = PickupStatistics.objects.get_or_create(pickup_addr=self.object.pickup_addr,
                                                                               product=self.object.product,
                                                                               pickup_type='1')[0]
            current_pickup_statistics.quantity = current_pickup_statistics.quantity + self.object.quantity
            current_pickup_statistics.save()
        elif self.object.status == 3:
            # pickup stone change
            current_pickup_store = PickupStore.objects.get_or_create(pickup_addr=self.object.pickup_addr,
                                                                     product=self.object.product)[0]
            current_pickup_store.quantity = current_pickup_store.quantity + self.object.quantity
            current_pickup_store.locked_quantity = current_pickup_store.locked_quantity - self.object.quantity
            current_pickup_store.save()

        return HttpResponseRedirect(self.get_success_url())


class PickupStatisticsListView(SingleTableMixin, TemplateView):
    template_name = 'dashboard/pickup_admin/pickup_statistics_list.html'
    paginate_by = 20
    form_class = PickupStatisticsSearchForm
    table_class = PickupStatisticsTable
    context_table_name = 'pickup_statistics_list'

    def get_table_pagination(self):
        return dict(per_page=20)

    def get_queryset(self):
        if self.request.user.userprofile.role == 'dashboard_admin':
            queryset = PickupStatistics.objects.all().order_by('status')
        else:
            current_pickupaddr = PickupAddr.objects.filter(staff=self.request.user)
            queryset = PickupStatistics.objects.filter(pickup_addr__in=current_pickupaddr).distinct()
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

        return queryset

    def get_context_data(self, **kwargs):
        context = super(PickupStatisticsListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context


class LoginView(FormView):
    template_name = 'dashboard/pickup_admin/login.html'
    form_class = LoginForm
    success_url = '/dashboard/pickup-admin/pickup-apply-list/'

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        response = HttpResponseRedirect(self.get_success_url())
        # response.set_cookie('logged_user', self.request.user.username, max_age=60*60)
        return response
