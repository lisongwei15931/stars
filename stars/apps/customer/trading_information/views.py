# -*- coding: utf-8 -*-
import datetime
import json
import traceback
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.query_utils import Q
from django.http.response import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.template import Context
from rest_framework.views import APIView
from oscar.core.loading import get_model
from stars.apps.tradingcenter.views import is_market_opening
from django.core.urlresolvers import reverse

from stars.apps.commission.views import commission_buy, cancel_commission_change


TradeComplete = get_model('commission', 'TradeComplete')
StockTicker = get_model('commission', 'StockTicker')
Product = get_model('catalogue', 'product')
CommissionBuy = get_model('commission', 'CommissionBuy')
CommissionSale = get_model('commission', 'CommissionSale')
PickupDetail = get_model('commission', 'PickupDetail')
PickupList = get_model('commission', 'PickupList')
UserPickupAddr = get_model('commission', 'UserPickupAddr')
PickupAddr = get_model('commission', 'PickupAddr')
UserPickupCity = get_model('commission', 'UserPickupCity')
ReceivingAddress = get_model('address', 'ReceivingAddress')
PickupStore = get_model('pickup_admin', 'PickupStore')
ProductOrder = get_model('commission', 'ProductOrder')

def trading_infomation(request):
    user = request.user
    all_trade_complete = TradeComplete.objects.filter(Q(commission_buy_user_id=user)|Q(commission_sale_user_id=user))
    keyWords = request.GET.get('keyWords')
    if keyWords:
        key_product = Product.objects.filter(Q(title__contains=keyWords)|Q(upc__contains=keyWords))
        if key_product:
            all_trade_complete = all_trade_complete.filter(product__in=key_product)
        else:
            all_trade_complete=[]
    starttime = request.GET.get('starttime')
    if starttime:
        all_trade_complete = all_trade_complete.filter(created_date__gte=starttime)
    endtime = request.GET.get('endtime')
    if endtime:
        all_trade_complete = all_trade_complete.filter(created_date__lte=endtime)
    is_buy = request.GET.get('buy')
    is_deal = request.GET.get('deal')
    is_sale = request.GET.get('sale')
    filter_set = Q()
    if is_buy:
        filter_set = Q(c_type=1,commission_buy_user_id=user)
    if is_deal:
        filter_set = filter_set|Q(c_type=2,commission_buy_user_id=user)
    if is_sale:
        filter_set = filter_set|Q(commission_sale_user_id=user)
    if filter_set:
        all_trade_complete = all_trade_complete.filter(filter_set)
    order = request.GET.get('order')
    if order:
        all_trade_complete = all_trade_complete.order_by(order)
    paginator = Paginator(all_trade_complete, 20)
    page = request.GET.get('page')
    try:
        all_trade_complete = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        all_trade_complete = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        all_trade_complete = paginator.page(paginator.num_pages)  # 取最后一页的记录

    total = 0
    net_change_total = 0
    for trade_complete in all_trade_complete:
        total += trade_complete.total
        if trade_complete.commission_buy_user_id == user:
            if trade_complete.c_type == 1:
                trade_complete.c_type = '购买'
            elif trade_complete.c_type == 2:
                trade_complete.c_type = '进货'
        else:
            trade_complete.c_type = '出售'
        trade_complete.current_price = trade_complete.product.strike_price
        if trade_complete.c_type == '进货':#如果是进货商品计算增值，增值比例
            net_change = (float(trade_complete.product.strike_price)-trade_complete.unit_price)*trade_complete.quantity
            trade_complete.net_change = net_change
            trade_complete.net_change_rise = "%.2f%%" % ((float(trade_complete.product.strike_price)-trade_complete.unit_price)/trade_complete.unit_price*100)
            net_change_total += net_change
    context = {'all_trade_complete': all_trade_complete,'total':total,
        'net_change_total':net_change_total, 'order':order,'page_title':u'交易记录',
        'frame_id':'trading_information','is_buy':is_buy,'is_deal':is_deal,'is_sale':is_sale}
    return render(request, 'customer/trading_information/trading_information.html', context)


def order_manage(request):
    user = request.user
    all_order = ProductOrder.objects.filter(user=user).order_by('-created_datetime')
    starttime = request.GET.get('starttime')
    if starttime:
        all_order = all_order.filter(created_datetime__gte=starttime)
    endtime = request.GET.get('endtime')
    if endtime:
        all_order = all_order.filter(created_datetime__lte=endtime)
    order = request.GET.get('order')
    if order:
        all_order = all_order.order_by(order)
    paginator = Paginator(all_order, 20)
    page = request.GET.get('page')
    try:
        all_order = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        all_order = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        all_order = paginator.page(paginator.num_pages)  # 取最后一页的记录
        
    for product_order in all_order:
        if product_order.pickup_type == 1:
            product_order.pickup_type='自提'
        elif product_order.pickup_type == 2:
            product_order.pickup_type='物流' 
        STATUS_CHOICES = ((0, u'未支付'), (1, u'支付中'), (2, u'支付成功'),
                      (3, u'支付失败'), (4, u'已关闭'), (5, u'已撤销'), (6, u'未发货'), (7, u'已发货'), (8, u'部分提货'), (9, u'已提货'))
        status_id = product_order.status
        product_order.status = STATUS_CHOICES[status_id][1]
        if product_order.effective == False:
            product_order.status = u"已取消"
    context = {'all_order': all_order,'page_title':u'订单管理','order':order,'frame_id':'order_manage'}
    return render(request, 'customer/trading_information/order_manage.html', context)


def order_detail(request):
    order_id = request.GET.get('order_id', '')
    if order_id:
        try:
            product_order = ProductOrder.objects.get(id=order_id)
            all_info = product_order.order_info.all()
            PICKUP_DETAIL_STATUS = (
                (1,'未提货'),
                (2,'已提货'),
                (3,'已驳回'),
                (4,'未发货'),
                (5,'已发货'),
                (6,'已评价'),
            )
            if product_order.status==2:
                for info in all_info:
                    status_id = int(info.order_pickup_detail.status) - 1
                    info.status = PICKUP_DETAIL_STATUS[status_id][1]
            else:
                STATUS_CHOICES = ((0, u'未支付'), (1, u'支付中'), (2, u'支付成功'),
                      (3, u'支付失败'), (4, u'已关闭'), (5, u'已撤销'), (6, u'未发货'), (7, u'已发货'), (8, u'部分提货'), (9, u'已提货'))
                status_id = product_order.status
                for info in all_info:
                    info.status = STATUS_CHOICES[status_id][1]
            current_template = get_template('customer/trading_information/partials/all_order_detail.html')
            context = {'all_info':all_info,'order':product_order}
            content_html = current_template.render(Context(context))
            payload = {'content_html': content_html, 'success': True}
            return HttpResponse(json.dumps(payload), content_type="application/json")
        except:
            traceback.print_exc()
            current_template = get_template('customer/trading_information/partials/all_order_detail.html')
            context = {'err_msg':'订单详情查询出错'}
            content_html = current_template.render(Context(context))
            payload = {'content_html': content_html, 'success': True}
            return HttpResponse(json.dumps(payload), content_type="application/json")
    else:
        return ""


def today_trading(request):
    user = request.user
    today = datetime.datetime.now().date()
    all_trade_complete = TradeComplete.objects.filter(Q(commission_buy_user_id=user)|Q(commission_sale_user_id=user),created_date=today)
    keyWords = request.GET.get('keyWords')
    if keyWords:
        key_product = Product.objects.filter(Q(title__contains=keyWords)|Q(upc__contains=keyWords))
        if key_product:
            all_trade_complete = all_trade_complete.filter(product__in=key_product)
        else:
            all_trade_complete=[]
    starttime = request.GET.get('starttime')
    if starttime:
        all_trade_complete = all_trade_complete.filter(created_date__gte=starttime)
    endtime = request.GET.get('endtime')
    if endtime:
        all_trade_complete = all_trade_complete.filter(created_date__lte=endtime)
    is_buy = request.GET.get('buy')
    is_deal = request.GET.get('deal')
    is_sale = request.GET.get('sale')
    filter_set = Q()
    if is_buy:
        filter_set = Q(c_type=1,commission_buy_user_id=user)
    if is_deal:
        filter_set = filter_set|Q(c_type=2,commission_buy_user_id=user)
    if is_sale:
        filter_set = filter_set|Q(commission_sale_user_id=user)
    if filter_set:
        all_trade_complete = all_trade_complete.filter(filter_set)
    order = request.GET.get('order')
    if order:
        all_trade_complete = all_trade_complete.order_by(order)
    paginator = Paginator(all_trade_complete, 20)
    page = request.GET.get('page')
    try:
        all_trade_complete = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        all_trade_complete = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        all_trade_complete = paginator.page(paginator.num_pages)  # 取最后一页的记录

    total = 0
    net_change_total = 0
    for trade_complete in all_trade_complete:
        total += trade_complete.total
        if trade_complete.commission_buy_user_id == user:
            if trade_complete.c_type == 1:
                trade_complete.c_type = '购买'
            elif trade_complete.c_type == 2:
                trade_complete.c_type = '进货'
        else:
            trade_complete.c_type = '出售'
        trade_complete.current_price = trade_complete.product.strike_price
        if trade_complete.c_type == '进货':#如果是进货商品计算增值，增值比例
            net_change = (float(trade_complete.product.strike_price)-trade_complete.unit_price)*trade_complete.quantity
            trade_complete.net_change = net_change
            trade_complete.net_change_rise = "%.2f%%" % ((float(trade_complete.product.strike_price)-trade_complete.unit_price)/trade_complete.unit_price*100)
            net_change_total += net_change
    context = {'all_trade_complete': all_trade_complete,'total':total,
        'net_change_total':net_change_total,'order':order,'page_title':u'当天成交',
        'frame_id':'today_trading','is_buy':is_buy,'is_deal':is_deal,'is_sale':is_sale}
    return render(request, 'customer/trading_information/trading_information.html', context)


def today_untrading(request):
    user = request.user
    today = datetime.datetime.now().date()
    keyWords = request.GET.get('keyWords')
    commission_buy_list = CommissionBuy.objects.filter(user=user,status__in=[1,2],created_datetime__year=today.year,created_datetime__month=today.month,created_datetime__day=today.day)
    commission_sale_list =CommissionSale.objects.filter(user=user,status__in=[1,2],created_datetime__year=today.year,created_datetime__month=today.month,created_datetime__day=today.day)
    if keyWords:
        key_product = Product.objects.filter(Q(title__contains=keyWords)|Q(upc__contains=keyWords))
        if key_product:
            commission_buy_list = commission_buy_list.filter(product__in=key_product)
            commission_sale_list = commission_sale_list.filter(product__in=key_product)
        else:
            commission_buy_list = CommissionBuy.objects.none()
            commission_sale_list = CommissionSale.objects.none()
    is_buy = request.GET.get('buy')
    is_deal = request.GET.get('deal')
    is_sale = request.GET.get('sale')
    filter_set = Q()
    sale_list_backup = commission_sale_list
    if is_buy:
        filter_set = Q(c_type=1)
        commission_sale_list = []
    if is_deal:
        filter_set = filter_set|Q(c_type=2)
        commission_sale_list = []
    commission_buy_list = commission_buy_list.filter(filter_set)
    if is_sale:
        commission_sale_list = sale_list_backup
    if is_sale and not is_buy and not is_deal:
        commission_buy_list = []
    complete_num = 0
    freezing_money_num = 0
    commission_list = []
    for commission_buy in commission_buy_list:
        if commission_buy.c_type == 1:
            c_type = u'购买'
        elif commission_buy.c_type == 2:
            c_type = u'进货'
        complete_quantity = commission_buy.quantity - commission_buy.uncomplete_quantity
        freezing_money = commission_buy.uncomplete_quantity*commission_buy.unit_price
        complete_num += complete_quantity
        freezing_money_num += freezing_money
        if commission_buy.status == 1:
            status = u'待成交'
        elif commission_buy.status == 2:
            status = u'部分成交'
        commission = {'id':commission_buy.id,
                      'type':'buy',
                      'commission_no':commission_buy.commission_no,
                      'commission_datetime':commission_buy.created_datetime,
                      'upc':commission_buy.product.upc,
                      'product_name':commission_buy.product.title,
                      'c_type':c_type,
                      'price':commission_buy.unit_price,
                      'quantity':commission_buy.quantity,
                      'complete_quantity':complete_quantity,
                      'freezing_money':freezing_money,
                      'freezing_fee':u'-',
                      'status':status
                      }
        commission_list.append(commission)
    for commission_sale in commission_sale_list:
        c_type = u'出售'
        complete_quantity = commission_sale.quantity - commission_sale.uncomplete_quantity
        complete_num += complete_quantity
        freezing_money = u'-'
        if commission_sale.status == 1:
            status = u'待成交'
        elif commission_sale.status == 2:
            status = u'部分成交'
        commission = {'id':commission_sale.id,
                      'type':'sale',
                      'commission_no':commission_sale.commission_no,
                      'commission_datetime':commission_sale.created_datetime,
                      'upc':commission_sale.product.upc,
                      'product_name':commission_sale.product.title,
                      'c_type':c_type,
                      'price':commission_sale.unit_price,
                      'quantity':commission_sale.quantity,
                      'complete_quantity':complete_quantity,
                      'freezing_money':freezing_money,
                      'freezing_fee':u'-',
                      'status':status
                      }
        commission_list.append(commission)
    order = str(request.GET.get('order',''))
    if order:
        order_by = order
        reverse = False
        if order_by.startswith('-'):
            order_by = order_by.replace('-', '')
            reverse = True
        commission_list = sorted(commission_list, key=lambda x:x[order_by], reverse=reverse)
    paginator = Paginator(commission_list, 20)
    page = request.GET.get('page')
    try:
        commission_list = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        commission_list = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        commission_list = paginator.page(paginator.num_pages)  # 取最后一页的记录

    context = {'page_title':u'当天未成交','commission_list':commission_list,'order':order,
        'complete_num':complete_num,'freezing_money_num':freezing_money_num,
        'frame_id':'today_untrading','is_buy':is_buy,'is_deal':is_deal,'is_sale':is_sale}
    return render(request, 'customer/trading_information/today_untrading.html', context)

#当天撤单
def cancel_order(request):
    user = request.user
    today = datetime.datetime.now().date()
    keyWords = request.GET.get('keyWords')
    commission_buy_list = CommissionBuy.objects.filter(user=user,status=4,created_datetime__year=today.year,created_datetime__month=today.month,created_datetime__day=today.day)
    commission_sale_list =CommissionSale.objects.filter(user=user,status=4,created_datetime__year=today.year,created_datetime__month=today.month,created_datetime__day=today.day)
    if keyWords:
        key_product = Product.objects.filter(Q(title__contains=keyWords)|Q(upc__contains=keyWords))
        if key_product:
            commission_buy_list = commission_buy_list.filter(product__in=key_product)
            commission_sale_list = commission_sale_list.filter(product__in=key_product)
        else:
            commission_buy_list = CommissionBuy.objects.none()
            commission_sale_list = CommissionSale.objects.none()
    is_buy = request.GET.get('buy')
    is_deal = request.GET.get('deal')
    is_sale = request.GET.get('sale')
    filter_set = Q()
    sale_list_backup = commission_sale_list
    if is_buy:
        filter_set = Q(c_type=1)
        commission_sale_list = []
    if is_deal:
        filter_set = filter_set|Q(c_type=2)
        commission_sale_list = []
    commission_buy_list = commission_buy_list.filter(filter_set)
    if is_sale:
        commission_sale_list = sale_list_backup
    if is_sale and not is_buy and not is_deal:
        commission_buy_list = []
    commission_list = []
    complete_num = 0
    for commission_buy in commission_buy_list:
        if commission_buy.c_type == 1:
            c_type = u'购买'
        elif commission_buy.c_type == 2:
            c_type = u'进货'
        complete_quantity = commission_buy.quantity - commission_buy.uncomplete_quantity
        complete_num += complete_quantity
        commission = {'commission_no':commission_buy.commission_no,
                      'commission_datetime':commission_buy.created_datetime,
                      'upc':commission_buy.product.upc,
                      'product_name':commission_buy.product.title,
                      'c_type':c_type,
                      'price':commission_buy.unit_price,
                      'quantity':commission_buy.quantity,
                      'complete_quantity':complete_quantity,
                      'cancel_datetime':commission_buy.modified_datetime,
                      }
        commission_list.append(commission)
    for commission_sale in commission_sale_list:
        c_type = u'出售'
        complete_quantity = commission_sale.quantity - commission_sale.uncomplete_quantity
        complete_num += complete_quantity
        commission = {'commission_no':commission_sale.commission_no,
                      'commission_datetime':commission_sale.created_datetime,
                      'upc':commission_sale.product.upc,
                      'product_name':commission_sale.product.title,
                      'c_type':c_type,
                      'price':commission_sale.unit_price,
                      'quantity':commission_sale.quantity,
                      'complete_quantity':complete_quantity,
                      'cancel_datetime':commission_sale.modified_datetime,
                      }
        commission_list.append(commission)
    order = str(request.GET.get('order',''))
    if order:
        order_by = order
        reverse = False
        if order_by.startswith('-'):
            order_by = order_by.replace('-', '')
            reverse = True
        commission_list = sorted(commission_list, key=lambda x:x[order_by], reverse=reverse)
    paginator = Paginator(commission_list, 20)
    page = request.GET.get('page')
    try:
        commission_list = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        commission_list = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        commission_list = paginator.page(paginator.num_pages)  # 取最后一页的记录
    context = {'page_title':u'当天撤单','commission_list':commission_list,
        'order':order,'complete_num':complete_num,
        'frame_id':'cancel_order','is_buy':is_buy,'is_deal':is_deal,'is_sale':is_sale}
    return render(request, 'customer/trading_information/cancel_order.html', context)


def pickup_detail(request):
    user = request.user
    all_order = ProductOrder.objects.filter(user=user)
    order_pickup_list = []
    for order in all_order:
        if order.pickup_list:
            order_pickup_list.append(int(order.pickup_list.id))
        else:
            pass
    pickup_list = PickupList.objects.filter(user=user).exclude(id__in=order_pickup_list)
    if request.is_ajax():
        #import ipdb;ipdb.set_trace()
        pickup_list_id = request.GET.get('pickup_list_id', '')
        if pickup_list_id:
            try:
                current_pickup_list = PickupList.objects.get(id=pickup_list_id)
                all_pickup_detail = current_pickup_list.pickup_lists_id.all()
                current_template = get_template('customer/trading_information/partials/all_pickup_detail.html')
                context = {'all_pickup_detail': all_pickup_detail}
                content_html = current_template.render(Context(context))
                payload = {'content_html': content_html, 'success': True}
                return HttpResponse(json.dumps(payload), content_type="application/json")
            except:
                pass
    starttime = request.GET.get('starttime')
    if starttime:
        pickup_list = pickup_list.filter(created_date__gte=starttime)
    endtime = request.GET.get('endtime')
    if endtime:
        pickup_list = pickup_list.filter(created_date__lte=endtime)
    selfpick = request.GET.get('selfpick')
    filter_set = Q()
    if selfpick:
        filter_set = Q(pickup_type=1)
    express = request.GET.get('express')
    if express:
        filter_set = filter_set|Q(pickup_type=2)
    pickup_list = pickup_list.filter(filter_set)
    order = str(request.GET.get('order',''))
    if order:
        pickup_list = pickup_list.order_by(order)
    pickup_fee_total = 0
    for pickup_detail in pickup_list:
        pickup_fee_total += pickup_detail.pickup_fee
    paginator = Paginator(pickup_list, 20)
    page = request.GET.get('page')
    try:
        pickup_list = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        pickup_list = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        pickup_list = paginator.page(paginator.num_pages)  # 取最后一页的记录
    context = {'page_title':u'提货单','pickup_list':pickup_list,'order':order,'pickup_fee_total':pickup_fee_total,
               'frame_id': 'pickup_detail','selfpick':selfpick,'express':express}
    return render(request, 'customer/trading_information/pickup_detail.html', context)


def pickup_detail_update(request, pickup_list_id):
    if not is_market_opening():
        return render(request, 'tradingcenter/market_closed_error.html', {"msg": u"已闭市,请在开市时操作"})
    user = request.user
    try:
        current_pickup_list = PickupList.objects.get(id=pickup_list_id)
    except:
        return redirect('customer:pickup_detail')
    all_pickup_detail = current_pickup_list.pickup_lists_id.all()
    pickup_type = current_pickup_list.pickup_type
    if pickup_type == 1:
        current_detail = all_pickup_detail[0]
        current_product = current_detail.product
        try:
            citys = UserPickupCity.objects.get(user=user, product=current_product).city.all()
            available_pickup_addr_list = PickupAddr.objects.filter(city__in=citys,
                                                                   stock_config_distribution_pickup_addr__product=current_product)
            for pickup_addr in available_pickup_addr_list:
                UserPickupAddr.objects.get_or_create(user=user, pickup_addr=pickup_addr)
        except:
            available_pickup_addr_list = []
        all_user_pickup_addr = list(UserPickupAddr.objects.filter(user=user,
            pickup_addr__in=available_pickup_addr_list).exclude(id=current_pickup_list.user_picked_addr.id))
        # all_user_pickup_addr = list(UserPickupAddr.objects.filter(user=user).exclude(id=current_pickup_list.user_picked_addr.id))
        current_user_pickup_addr = list(UserPickupAddr.objects.filter(id=current_pickup_list.user_picked_addr.id))
        current_user_pickup_addr.extend(all_user_pickup_addr)
        all_user_pickup_addr = current_user_pickup_addr

        change_list = all_user_pickup_addr
    else:
        all_user_receiving_address = ReceivingAddress.objects.filter(user=user).exclude(id=current_pickup_list.user_address.id)
        current_user_receiving_address = list(ReceivingAddress.objects.filter(id=current_pickup_list.user_address.id))
        current_user_receiving_address.extend(all_user_receiving_address)
        all_user_receiving_address = current_user_receiving_address

        change_list = all_user_receiving_address
    if request.method == 'POST':
        if pickup_type == 1:
            pickup_address_id = request.POST.get('pickup_address_id', '')
            current_user_pickup_addr = UserPickupAddr.objects.get(id=pickup_address_id)
            old_pickup_addr = current_pickup_list.user_picked_addr.pickup_addr
            for pickup_detail in all_pickup_detail:
                pickup_detail.pickup_addr = current_user_pickup_addr.pickup_addr
                pickup_detail.save()
                current_pickup_list.user_picked_addr = current_user_pickup_addr
                current_pickup_list.save()

                old_pickup_store = PickupStore.objects.get_or_create(pickup_addr=old_pickup_addr,
                                                                     product=pickup_detail.product)[0]
                old_pickup_store.locked_quantity = old_pickup_store.locked_quantity - pickup_detail.quantity
                old_pickup_store.quantity = old_pickup_store.quantity + pickup_detail.quantity
                old_pickup_store.save()

                new_pickup_store = PickupStore.objects.get_or_create(pickup_addr=current_user_pickup_addr.pickup_addr,
                                                                     product=pickup_detail.product)[0]
                new_pickup_store.locked_quantity = new_pickup_store.locked_quantity + pickup_detail.quantity
                new_pickup_store.quantity = new_pickup_store.quantity - pickup_detail.quantity
                new_pickup_store.save()
        else:
            receiving_address_id = request.POST.get('receiving_address_id', '')
            current_user_receiving_address = ReceivingAddress.objects.get(id=receiving_address_id)
            current_pickup_list.user_address_id = current_user_receiving_address
            current_pickup_list.save()
            user_address_str = ''.join([current_user_receiving_address.province.name,
                                        current_user_receiving_address.city.name,
                                        current_user_receiving_address.district.name,
                                        current_user_receiving_address.address])
            all_pickup_detail.update(user_address=user_address_str)
        return redirect('customer:pickup_detail')

    context = {'all_pickup_detail': all_pickup_detail,
               'pickup_type': pickup_type,
               'current_pickup_list': current_pickup_list,
               'change_list': change_list}
    return render(request, 'customer/trading_information/pickup_detail_update.html', context)


def cancel_commission(request):
    if not is_market_opening():
        return HttpResponseServerError(u'已闭市,请在开始时操作')
    commission_ids = request.POST.get('cancel_list')
    commission_ids = json.loads(commission_ids)
    if commission_ids:
        for commission_id in commission_ids:
            if commission_id['type'] == u'buy':
                commission = CommissionBuy.objects.filter(id=commission_id['id']).first()
                if commission:
                    commission.status = 4
                    commission.save()
                    cancel_commission_change(commission)
            elif commission_id['type'] == u'sale':
                commission = CommissionSale.objects.filter(id=commission_id['id']).first()
                if commission:
                    commission.status = 4
                    commission.save()
                    cancel_commission_change(commission)
    return HttpResponse('ok')


class PickupDetailListView(APIView):
    def get(self, request, *args, **kwargs):
        m = {'frame_id': 'pickup_detail'}
        data = request.GET
        tpl = 'customer/trading_information/pickup_detail_list.html'
        pk = kwargs['pk']

        data = PickupDetail.objects.filter(pickup_list_id_id=pk)
        m['pickup_detail_list'] = data

        return render(request, tpl, m)
