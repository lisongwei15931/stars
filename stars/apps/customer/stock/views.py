# -*- coding: utf-8 -*-

import json

from django.db.models.query_utils import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Sum
from django.template.loader import get_template
from django.template import Context
from django.core.urlresolvers import reverse

from stars.apps.customer.receiving_address.forms import ReceivingAddressForm
from stars.apps.customer.stock.models import PickupProvisionalRecord
from stars.apps.catalogue.models import Product
from stars.apps.address.models import ReceivingAddress
from stars.apps.commission.models import (TradeComplete, StockTicker,
    StockProductConfig, PickupDetail, UserProduct, UserBalance, UserPickupAddr,
    PickupDetail, PickupList, UserMoneyChange, PickupAddr, UserPickupCity)
from stars.apps.pickup_admin.models import PickupStore
from stars.apps.address.models import Province, City, ReceivingAddress
from stars.apps.tradingcenter.tasks import PushTriggerTest
from stars.apps.tradingcenter.views import is_market_opening


def stock(request):
    user = request.user

    stock_list = []
    buy_list = []
    search_keyword = request.GET.get('search_keyword', '')
    search_buy = request.GET.get('search_buy', '')
    search_stock = request.GET.get('search_stock', '')

    stock_buy_list = UserProduct.objects.filter(user=user).exclude(quantity=0)
    if search_keyword:
        stock_buy_list = stock_buy_list.filter(Q(product__title__icontains=search_keyword)|Q(product__upc__icontains=search_keyword)).distinct()
    if search_buy and not search_stock:
        stock_buy_list = stock_buy_list.filter(trade_type=1)
    if search_stock and not search_buy:
        stock_buy_list = stock_buy_list.filter(trade_type=2)

    # order
    sort_key = request.GET.get('sort_key', '')
    order = request.GET.get('order', '')
    if sort_key == 'product_name':
        if order == 'descending':
            stock_buy_list = stock_buy_list.order_by('product__slug')
        else:
            order = 'ascending'
            stock_buy_list = stock_buy_list.order_by('-product__slug')
    elif sort_key == 'strike_price':
        if order == 'descending':
            stock_buy_list = sorted(stock_buy_list, key=lambda x: x.strike_price)
        else:
            order = 'ascending'
            stock_buy_list = sorted(stock_buy_list, key=lambda x: x.strike_price, reverse=True)
    else:
        order = 'descending'
        sort_key = 'product_name'
        stock_buy_list = stock_buy_list.order_by('product__title')
    data_number = len(stock_buy_list)

    # page
    paginator = Paginator(stock_buy_list, 20)
    page = request.GET.get('page')
    try:
        stock_buy_list = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        stock_buy_list = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        stock_buy_list = paginator.page(paginator.num_pages)  # 取最后一页的记录
    # total added value one page
    total_added_value = 0
    for one_list in stock_buy_list.object_list:
        if one_list.trade_type == 2:
            total_added_value += one_list.added_value
    # link_key
    order_extra_link_key = ''
    page_extra_link_key = ''
    if sort_key:
        sort_key_link = '&sort_key=%s' % sort_key
        page_extra_link_key += sort_key_link
    else:
        sort_key_link = ''
    if order:
        order_link = '&order=%s' % order
        page_extra_link_key += order_link
    else:
        order_link = ''
    if page:
        page_link = '&page=%s' % page
        order_extra_link_key += page_link
    else:
        page_link = ''
    if search_keyword:
        search_keyword_link = '&search_keyword=%s' % search_keyword
        order_extra_link_key += search_keyword_link
        page_extra_link_key += search_keyword_link
    else:
        search_keyword_link = ''
    if search_buy:
        search_buy_link = '&search_buy=%s' % search_buy
        order_extra_link_key += search_buy_link
        page_extra_link_key += search_buy_link
    else:
        search_buy_link = ''
    if search_stock:
        search_stock_link = '&search_stock=%s' % search_stock
        order_extra_link_key += search_stock_link
        page_extra_link_key += search_stock_link
    else:
        search_stock_link = ''
    context = {'frame_id': 'stock',
               'stock_buy_list': stock_buy_list,
               'sort_key': sort_key,
               'order': order,
               'page': page,
               'search_keyword': search_keyword,
               'search_buy': search_buy,
               'search_stock': search_stock,
               'order_extra_link_key': order_extra_link_key,
               'page_extra_link_key': page_extra_link_key,
               'total_added_value': total_added_value,
               'data_number': data_number}
    return render(request, 'customer/stock/stock.html', context)


def pickup_set(request):
    user = request.user
    current_pprs = PickupProvisionalRecord.objects.filter(user=user)     # ppr is short of PickupProvisionalRecord
    current_pprs.update(available=False, quantity=1)

    user_product_id_list = request.GET.getlist('user_product_id_list[]')
    if user_product_id_list:
        current_user_product_list = UserProduct.objects.filter(id__in=user_product_id_list)
        for user_product in current_user_product_list:
            try:
                current_ppr = PickupProvisionalRecord.objects.get(user=user, product=user_product.product)
                if current_ppr.available:
                    current_ppr.max_quantity += user_product.quantity
                    current_ppr.pickup_type = 3
                else:
                    current_ppr.max_quantity = user_product.quantity
                    current_ppr.pickup_type = user_product.trade_type
                    current_ppr.available = True
                current_ppr.save()
            except PickupProvisionalRecord.DoesNotExist:
                current_ppr = PickupProvisionalRecord.objects.create(user=user,
                                                                     product=user_product.product,
                                                                     max_quantity=user_product.quantity,
                                                                     pickup_type=user_product.trade_type,
                                                                     available=True)
        result = {'result': True}
    else:
        result = {'result': False}
    return HttpResponse(json.dumps(result), content_type='application/json', status=200)


def pickup_quantity_set(request):
    record_id = request.GET.get('record_id', '')
    pickup_quantity = request.GET.get('pickup_quantity', '')
    if record_id and pickup_quantity:
        try:
            current_ppr = PickupProvisionalRecord.objects.get(id=record_id)
            current_ppr.quantity = int(pickup_quantity)
            current_ppr.save()
        except:
            pass
        result = {'result': True}
    else:
        result = {'result': False}
    return HttpResponse(json.dumps(result), content_type='application/json', status=200)


def pickup_store_check(request):
    pickup_type = request.GET.get('pickup_type', '')
    if pickup_type == '2':
        result = {'result': True}
    else:
        pickup_address_id = request.GET.get('pickup_address_id', '')
        if pickup_type and pickup_address_id:
            user = request.user
            try:
                current_pickup_addr = UserPickupAddr.objects.get(id=pickup_address_id).pickup_addr
                current_pprs = PickupProvisionalRecord.objects.filter(user=user, available=True)     # ppr is short of PickupProvisionalRecord
                product_and_quantity = current_pprs.values_list('product', 'quantity')
                available = True
                for (current_product_id, current_quantity) in product_and_quantity:
                    try:
                        aa=PickupStore.objects.get(pickup_addr=current_pickup_addr,
                                                product_id=current_product_id,
                                                quantity__gte=current_quantity)
                    except PickupStore.DoesNotExist:
                        available = False
                        break
                if available:
                    result = {'result': True}
            except UserPickupAddr.DoesNotExist:
                result = {'result': False}
        else:
            result = {'result': False}
    return HttpResponse(json.dumps(result), content_type='application/json', status=200)


def pickup_apply(request):
    if not is_market_opening():
        return render(request, 'tradingcenter/market_closed_error.html', {"msg": u"已闭市,请在开市时操作"})
    user = request.user
    receiving_address_status = request.GET.get('receiving_address', '')
    record_list = PickupProvisionalRecord.objects.filter(user=user, available=True).order_by('product__title')
    can_pickup = True
    '''
    for record in record_list:
        if not record.product.can_pickup:
            can_pickup = False
            break
    if receiving_address_status or (not can_pickup):
        receiving_address_status = True
    '''
    current_pprs = PickupProvisionalRecord.objects.filter(user=user, available=True)     # ppr is short of PickupProvisionalRecord
    if current_pprs:
        current_ppr = current_pprs[0]
        current_product = current_ppr.product
        try:
            citys = UserPickupCity.objects.get(user=user, product=current_product).city.all()
            available_pickup_addr_list = PickupAddr.objects.filter(city__in=citys,
                                                                   stock_config_distribution_pickup_addr__product=current_product)
            for pickup_addr in available_pickup_addr_list:
                UserPickupAddr.objects.get_or_create(user=user, pickup_addr=pickup_addr)
        except:
            available_pickup_addr_list = []
    else:
        return redirect('customer:stock')
    if receiving_address_status or (not available_pickup_addr_list):
        receiving_address_status = True
    receiving_address_list = ReceivingAddress.objects.filter(user=user).order_by('-is_default')
    user_pickup_addr_list = UserPickupAddr.objects.filter(user=user,
                                                          pickup_addr__in=available_pickup_addr_list).order_by('-is_default')
    pickup_addr_list = user_pickup_addr_list
    record_quantity = record_list.count()

    '''
    product_ids = record_list.values_list('product', flat=True)
    user_pickup_addr_list = UserPickupAddr.objects.filter(user=user).order_by('-is_default')
    first_available_pickup_addr_ids = [user_pickup_addr.pickup_addr.id for user_pickup_addr in user_pickup_addr_list
        if PickupStore.objects.filter(pickup_addr=user_pickup_addr.pickup_addr, product_id__in=product_ids).count() == record_quantity]

    final_available_pickup_addr_ids = []
    product_and_quantity = record_list.values_list('product', 'quantity')
    for pickup_addr_id in first_available_pickup_addr_ids:
        available = True
        for (current_product_id, current_quantity) in product_and_quantity:
            try:
                PickupStore.objects.get(pickup_addr_id=pickup_addr_id,
                                        product_id=current_product_id,
                                        quantity__gte=current_quantity)
            except PickupStore.DoesNotExist:
                available = False
                break
        if available:
            final_available_pickup_addr_ids.append(pickup_addr_id)
    pickup_addr_list = user_pickup_addr_list.filter(pickup_addr__id__in=final_available_pickup_addr_ids)
    '''

    if request.is_ajax():
        current_template = get_template('customer/stock/partials/pickup_apply_left.html')
        context = {'record_list': record_list,
                   'record_quantity': record_quantity,
                   'receiving_address_list': receiving_address_list,
                   'pickup_address_list': pickup_addr_list,
                   'receiving_address_status': receiving_address_status}
        content_html = current_template.render(Context(context))
        payload = {'content_html': content_html, 'success': True}
        return HttpResponse(json.dumps(payload), content_type="application/json")

    if not record_quantity:
        return redirect('customer:stock')
    user_balance = UserBalance.objects.get_or_create(user=user)[0]
    current_user_balance = user_balance.balance
    if request.method == 'POST':
        pickup_type = request.POST.get('pickup_type', '')
        receiving_address_id = request.POST.get('receiving_address_id', '')
        pickup_address_id = request.POST.get('pickup_address_id', '')
        pickup_price_value = request.POST.get('pickup_price_value', 0)
        express_price_value = request.POST.get('express_price_value', 0)
        if pickup_type and (pickup_address_id or receiving_address_id):
            # generate PickupList
            if pickup_type == '1':
                new_pickuplist = PickupList.objects.create(user=user, pickup_type=1, status=4,
                                                        user_picked_addr_id=pickup_address_id,
                                                        pickup_fee=float(pickup_price_value),
                                                        express_fee=0)
                pickup_total_price = float(pickup_price_value)
            else:
                '''
                if user_pickup_addr_list:
                    current_user_pickup_addr = UserPickupAddr.objects.get(user=user, is_default=True)
                    current_pickup_addr = current_user_pickup_addr.pickup_addr
                else:
                    current_city = ReceivingAddress.objects.get(id=receiving_address_id).city
                    current_city_addrs = PickupAddr.objects.filter(city=current_city)
                    if current_city_addrs:
                        current_pickup_addr = current_city_addrs[0]
                    else:
                        current_province = ReceivingAddress.objects.get(id=receiving_address_id).province
                        current_province_addrs = PickupAddr.objects.filter(province=current_province)
                        if current_province_addrs:
                            current_pickup_addr = current_province_addrs[0]
                        else:
                            all_pickup_addrs = PickupAddr.objects.all()
                            if all_pickup_addrs:
                                current_pickup_addr = current_province_addrs[0]
                            else:
                                current_pickup_addr = ''
                if user_pickup_addr_list:
                    new_pickuplist = PickupList.objects.create(user=user, pickup_type=2, status=4,
                                                            user_picked_addr=current_user_pickup_addr,
                                                            user_address_id=receiving_address_id,
                                                            pickup_fee=float(pickup_price_value),
                                                            express_fee=float(express_price_value))
                else:
                    new_pickuplist = PickupList.objects.create(user=user, pickup_type=2, status=4,
                                                            user_address_id=receiving_address_id,
                                                            pickup_fee=float(pickup_price_value),
                                                            express_fee=float(express_price_value))
                '''
                new_pickuplist = PickupList.objects.create(user=user, pickup_type=2, status=4,
                                                        user_address_id=receiving_address_id,
                                                        pickup_fee=float(pickup_price_value),
                                                        express_fee=float(express_price_value))
                pickup_total_price = float(pickup_price_value) + float(express_price_value)
            new_pickuplist.custom_save()
            for ppr in current_pprs:
                if pickup_type == '1':
                    current_pd = PickupDetail.objects.create(pickup_list_id=new_pickuplist,
                                                             pickup_addr=new_pickuplist.user_picked_addr.pickup_addr,
                                                             express_fee=0, pickup_type=1, status=4,
                                                             trade_type=ppr.pickup_type,
                                                             pickup_captcha=new_pickuplist.pickup_captcha,
                                                             product=ppr.product,
                                                             quantity=ppr.quantity,
                                                             pickup_fee=ppr.pickup_price*ppr.quantity)
                    current_pickup_store = PickupStore.objects.get_or_create(pickup_addr=new_pickuplist.user_picked_addr.pickup_addr,
                                                                             product=ppr.product)[0]
                    current_pickup_store.quantity = current_pickup_store.quantity - ppr.quantity
                    current_pickup_store.locked_quantity = current_pickup_store.locked_quantity + ppr.quantity
                    current_pickup_store.save()
                else:
                    user_address = ReceivingAddress.objects.get(id=receiving_address_id)
                    user_address_str = ''.join([user_address.province.name,
                                                user_address.city.name,
                                                user_address.district.name, user_address.address])
                    consignee = user_address.consignee
                    mobile_phone = user_address.mobile_phone
                    '''
                    if ppr.product.can_pickup and current_pickup_addr:
                        current_pd = PickupDetail.objects.create(pickup_list_id=new_pickuplist,
                                                                 pickup_addr=current_pickup_addr,
                                                                 user_address=user_address_str,
                                                                 consignee=consignee, mobile_phone=mobile_phone,
                                                                 express_fee=0, pickup_type=2, status=4,
                                                                 pickup_captcha=new_pickuplist.pickup_captcha,
                                                                 product=ppr.product,
                                                                 quantity=ppr.quantity,
                                                                 pickup_fee=ppr.pickup_price*ppr.quantity)
                        current_pickup_store = PickupStore.objects.get_or_create(pickup_addr=current_pickup_addr,
                                                                                 product=ppr.product)[0]
                        current_pickup_store.quantity = current_pickup_store.quantity - ppr.quantity
                        current_pickup_store.locked_quantity = current_pickup_store.locked_quantity + ppr.quantity
                        current_pickup_store.save()
                    else:
                    '''
                    current_pd = PickupDetail.objects.create(pickup_list_id=new_pickuplist,
                                                             express_fee=0, pickup_type=3, status=4,
                                                             trade_type=ppr.pickup_type,
                                                             user_address=user_address_str,
                                                             consignee=consignee, mobile_phone=mobile_phone,
                                                             pickup_captcha=new_pickuplist.pickup_captcha,
                                                             product=ppr.product,
                                                             quantity=ppr.quantity,
                                                             pickup_fee=ppr.pickup_price*ppr.quantity)

                # user product change
                if ppr.pickup_type in [1, 2]:
                    try:
                        user_product = UserProduct.objects.get(user=user, product=ppr.product, trade_type=ppr.pickup_type)
                        if ppr.pickup_type == 2:
                            user_product.total_pickup_quantity += ppr.quantity
                        user_product.can_pickup_quantity -= ppr.quantity
                        user_product.quantity -= ppr.quantity

                        pickup_quantity = ppr.quantity
                        current_tc_list = list(TradeComplete.objects.filter(commission_buy_user_id=user, product=ppr.product, c_type=str(ppr.pickup_type)).exclude(can_pickup_quantity=0).order_by('created_datetime')) # tc is short for TradeComplete
                        for i in xrange(len(current_tc_list)):
                            current_tc = current_tc_list[i]
                            if pickup_quantity > current_tc.can_pickup_quantity:
                                pickup_quantity -= current_tc.can_pickup_quantity
                                current_tc.can_pickup_quantity = 0
                                current_tc.save()
                                if i == len(current_tc_list) - 1:
                                    user_product.overage_unit_price = 0
                                    break
                            else:
                                current_tc.can_pickup_quantity -= pickup_quantity
                                current_tc.save()
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
                        user_product.save()
                    except:
                        continue
                else:
                    try:
                        user_product_buy = UserProduct.objects.get(user=user, product=ppr.product, trade_type=1)
                        if user_product_buy.quantity < ppr.quantity:
                            user_product_stock = UserProduct.objects.get(user=user, product=ppr.product, trade_type=2)
                            user_product_buy.can_pickup_quantity = 0
                            user_product_buy.quantity = 0
                            user_product_buy.save()

                            different_quantity = ppr.quantity-user_product_buy.quantity
                            user_product_stock.total_pickup_quantity += different_quantity
                            user_product_stock.can_pickup_quantity -= different_quantity
                            user_product_stock.quantity -= different_quantity

                            current_tc_list = list(TradeComplete.objects.filter(commission_buy_user_id=user, product=ppr.product, c_type='2').exclude(can_pickup_quantity=0).order_by('created_datetime')) # tc is short for TradeComplete
                            for i in xrange(len(current_tc_list)):
                                current_tc = current_tc_list[i]
                                if pickup_quantity > current_tc.can_pickup_quantity:
                                    pickup_quantity -= current_tc.can_pickup_quantity
                                    current_tc.can_pickup_quantity = 0
                                    current_tc.save()
                                    if i == len(current_tc_list) - 1:
                                        user_product_buy.overage_unit_price = 0
                                        break
                                else:
                                    current_tc.can_pickup_quantity -= pickup_quantity
                                    current_tc.save()
                                    if i == len(current_tc_list) - 1:
                                        user_product_buy.overage_unit_price = current_tc.unit_price
                                    else:
                                        total_price = 0
                                        total_quantity = 0
                                        for tc in current_tc_list[i:]:
                                            total_price += tc.unit_price * tc.can_pickup_quantity
                                            total_quantity += tc.can_pickup_quantity
                                        user_product_buy.overage_unit_price = total_price / total_quantity
                                    break

                            user_product_stock.save()
                        else:
                            user_product_buy.can_pickup_quantity -= ppr.quantity
                            user_product_buy.quantity -= ppr.quantity

                            pickup_quantity = ppr.quantity
                            current_tc_list = list(TradeComplete.objects.filter(commission_buy_user_id=user, product=ppr.product, c_type='1').exclude(can_pickup_quantity=0).order_by('created_datetime')) # tc is short for TradeComplete
                            for i in xrange(len(current_tc_list)):
                                current_tc = current_tc_list[i]
                                if pickup_quantity > current_tc.can_pickup_quantity:
                                    pickup_quantity -= current_tc.can_pickup_quantity
                                    current_tc.can_pickup_quantity = 0
                                    current_tc.save()
                                    if i == len(current_tc_list) - 1:
                                        user_product_buy.overage_unit_price = 0
                                        break
                                else:
                                    current_tc.can_pickup_quantity -= pickup_quantity
                                    current_tc.save()
                                    if i == len(current_tc_list) - 1:
                                        user_product_buy.overage_unit_price = current_tc.unit_price
                                    else:
                                        total_price = 0
                                        total_quantity = 1
                                        for tc in current_tc_list[i:]:
                                            total_price += tc.unit_price * tc.can_pickup_quantity
                                            total_quantity += tc.can_pickup_quantity
                                        user_product_buy.overage_unit_price = total_price / total_quantity
                                    break
                            user_product_buy.save()
                    except:
                        continue
            # user money change
            user_money_change = UserMoneyChange()
            user_money_change.user = user
            user_money_change.status = 2
            user_money_change.trade_type = 10
            user_money_change.price = pickup_total_price
            user_money_change.pickup_amount = pickup_total_price
            user_money_change.pickup_list = new_pickuplist
            user_money_change.custom_save()

            current_pprs.update(available=False)

            return redirect('customer:pickup_success', new_pickuplist.id)
        else:
            return HttpResponse('Error!')

    context = {'record_list': record_list,
               'record_quantity': record_quantity,
               'receiving_address_list': receiving_address_list,
               'pickup_address_list': pickup_addr_list,
               'can_pickup': can_pickup,
               'receiving_address_status': receiving_address_status,
               'user_balance': current_user_balance}
    return render(request, 'customer/stock/pickup_apply.html', context)


def add_pickup_addr(request):
    user = request.user
    user_pickup_address_list = UserPickupAddr.objects.filter(user=user)
    exclude_pickup_address_ids = user_pickup_address_list.values_list('pickup_addr')
    if request.is_ajax():
        province_id = request.GET.get('province_id', '')
        city_id = request.GET.get('city_id', '')
        if province_id and (not city_id):
            if province_id != 'all':
                try:
                    all_pickup_address_list = PickupAddr.objects.exclude(id__in=exclude_pickup_address_ids)
                    all_province_ids = all_pickup_address_list.values_list('province', flat=True)
                    province_list = Province.objects.filter(id__in=all_province_ids)

                    current_province = Province.objects.get(id=province_id)
                    pickup_address_list = PickupAddr.objects.filter(province=current_province).exclude(id__in=exclude_pickup_address_ids)
                    city_ids = pickup_address_list.values_list('city', flat=True)
                    city_list = City.objects.filter(id__in=city_ids)
                    current_template = get_template('customer/stock/partials/add_pickup_addr_content.html')
                    context = {'pickup_address_list': pickup_address_list,
                            'province_list': province_list,
                            'city_list': city_list,
                            'current_province_id': current_province.id,
                            'current_city': 'all',}
                    content_html = current_template.render(Context(context))
                    payload = {'content_html': content_html, 'success': True}
                    return HttpResponse(json.dumps(payload), content_type="application/json")
                except:
                    pass
            else:
                pickup_address_list = PickupAddr.objects.exclude(id__in=exclude_pickup_address_ids)

                province_ids = pickup_address_list.values_list('province', flat=True)
                province_list = Province.objects.filter(id__in=province_ids)
                city_list = []
                current_template = get_template('customer/stock/partials/add_pickup_addr_content.html')
                context = {'pickup_address_list': pickup_address_list,
                        'province_list': province_list,
                        'city_list': city_list,
                        'current_province_id': 'all',
                        'current_city_id': 'all',}
                content_html = current_template.render(Context(context))
                payload = {'content_html': content_html, 'success': True}
                return HttpResponse(json.dumps(payload), content_type="application/json")

        if city_id:
            if city_id != 'all':
                try:
                    all_pickup_address_list = PickupAddr.objects.exclude(id__in=exclude_pickup_address_ids)
                    all_province_ids = all_pickup_address_list.values_list('province', flat=True)
                    province_list = Province.objects.filter(id__in=all_province_ids)

                    current_city = City.objects.get(id=city_id)
                    current_province = current_city.province
                    pickup_address_list = PickupAddr.objects.filter(city=current_city).exclude(id__in=exclude_pickup_address_ids)

                    city_ids = all_pickup_address_list.filter(province=current_province).values_list('city', flat=True)
                    city_list = City.objects.filter(id__in=city_ids)

                    current_template = get_template('customer/stock/partials/add_pickup_addr_content.html')
                    context = {'pickup_address_list': pickup_address_list,
                            'province_list': province_list,
                            'city_list': city_list,
                            'current_province_id': current_province.id,
                            'current_city_id': current_city.id,}
                    content_html = current_template.render(Context(context))
                    payload = {'content_html': content_html, 'success': True}
                    return HttpResponse(json.dumps(payload), content_type="application/json")
                except:
                    pass
            else:
                all_pickup_address_list = PickupAddr.objects.exclude(id__in=exclude_pickup_address_ids)
                all_province_ids = all_pickup_address_list.values_list('province', flat=True)
                province_list = Province.objects.filter(id__in=all_province_ids)

                current_province = Province.objects.get(id=province_id)
                pickup_address_list = PickupAddr.objects.filter(province=current_province).exclude(id__in=exclude_pickup_address_ids)
                city_ids = pickup_address_list.values_list('city', flat=True)
                city_list = City.objects.filter(id__in=city_ids)
                current_template = get_template('customer/stock/partials/add_pickup_addr_content.html')
                context = {'pickup_address_list': pickup_address_list,
                        'province_list': province_list,
                        'city_list': city_list,
                        'current_province_id': current_province.id,
                        'current_city': 'all',}
                content_html = current_template.render(Context(context))
                payload = {'content_html': content_html, 'success': True}
                return HttpResponse(json.dumps(payload), content_type="application/json")

    pickup_address_list = PickupAddr.objects.exclude(id__in=exclude_pickup_address_ids)

    province_ids = pickup_address_list.values_list('province', flat=True)
    province_list = Province.objects.filter(id__in=province_ids)
    city_list = []

    context = {'pickup_address_list': pickup_address_list,
               'province_list': province_list,
               'city_list': city_list,
               'current_province_id': 'all',
               'current_city_id': 'all',}
    if request.method == 'POST':
        added_pickup_addr_id = request.POST.get('pickup_address_id', '')
        if added_pickup_addr_id:
            try:
                current_pickup_addr = PickupAddr.objects.get(id=added_pickup_addr_id)
                new_pickup_addr = UserPickupAddr.objects.get_or_create(user=user, pickup_addr=current_pickup_addr)[0]
                new_pickup_addr.is_default = True
                new_pickup_addr.save()
            except:
                pass
        return redirect('customer:pickup_apply')
    return render(request, 'customer/stock/add_pickup_addr.html', context)


def add_receiving_addr(request):
    user = request.user
    if request.method == 'POST':
        form = ReceivingAddressForm(request.POST)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = user
            new_address.save()
            return redirect(''.join([reverse('customer:pickup_apply'), '?receiving_address=1']))
    else:
        form = ReceivingAddressForm()
    context = {'form': form,}
    return render(request, 'customer/stock/add_receiving_addr.html', context)


def pickup_success(request, pickup_list_id):
    try:
        current_product_list = PickupList.objects.get(id=pickup_list_id)
        if current_product_list.pickup_type == 1:
            captcha = current_product_list.pickup_captcha
        else:
            captcha = ''
    except:
        captcha = ''
    context = {'captcha': captcha}
    return render(request, 'customer/stock/pickup_success.html', context)
