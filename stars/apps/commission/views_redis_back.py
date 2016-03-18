# -*- coding: utf-8 -*-s

import datetime
import hashlib
import random
import string
import time
import json
import traceback

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Min, Sum, Max
from django.http.response import HttpResponse, HttpResponseServerError
from oscar.core.loading import get_model
from stars.apps.tradingcenter.forms import CommissionBuyForm, CommissionSaleForm
from stars.apps.tradingcenter.tasks import PushTriggerTest
from django_redis import get_redis_connection
from stars.apps.commission.tasks import receive_buy

Product = get_model('catalogue', 'product')
CommissionSale = get_model('commission', 'CommissionSale')
CommissionBuy = get_model('commission', 'CommissionBuy')
TradeComplete = get_model('commission', 'TradeComplete')
StockTicker = get_model('commission', 'StockTicker')
StockProductConfig = get_model('commission', 'StockProductConfig')
UserMoneyChange = get_model('commission', 'UserMoneyChange')
UserBalance = get_model('commission', 'UserBalance')
UserAssetDailyReport = get_model('commission', 'UserAssetDailyReport')
UserProduct = get_model('commission', 'UserProduct')

@transaction.atomic 
def commission_buy_test(request):
    if request.method == 'POST':
        form = CommissionBuyForm(request.POST)
        try:
            if form.is_valid():
                product_id = request.POST.get('product', '')
                c_type = request.POST.get('c_type', '')
                user = request.user
                if user.is_anonymous():
                    return HttpResponseServerError(u'请登陆')
                product = Product.objects.get(id=product_id)
                unit_price = request.POST.get('price', '')
                quantity = request.POST.get('quantity', '')
                new_commission_buy(product,user,c_type,unit_price,quantity,quantity,1)
                return HttpResponse('OK')
            else:   
                return HttpResponseServerError(u'信息错误')
        except DealException,e:
            return HttpResponseServerError(e.value)
        except:
            traceback.print_exc()
            return HttpResponseServerError(u'购货失败')


@transaction.atomic
def commission_sale_test(request):
    if request.method == 'POST':
        form = CommissionSaleForm(request.POST)
        try:
            if form.is_valid():
                product_id = request.POST.get('product', '')
                c_type = request.POST.get('c_type', '')
                user = request.user
                if user.is_anonymous():
                    return HttpResponseServerError(u'请登陆')
                product = Product.objects.get(id=product_id)
                unit_price = request.POST.get('price', '')
                quantity = request.POST.get('quantity', '')
                new_commissiton_sale(product,user,c_type,unit_price,quantity,quantity,1)
                return HttpResponse('OK')
            else:
                return HttpResponseServerError(u'信息错误')
        except DealException,e:
            return HttpResponseServerError(e.value)
        except:
            traceback.print_exc()
            return HttpResponseServerError(u'出售失败')
        

@transaction.atomic
def factory_commission_sale(request):
    if request.method == 'POST':
        form = CommissionSaleForm(request.POST)
        try:
            if form.is_valid():
                product_id = request.POST.get('product', '')
                c_type = request.POST.get('c_type', '')
                user = request.user
                if user.is_anonymous():
                    return HttpResponseServerError(u'请登陆')
                product = Product.objects.get(id=product_id)
                unit_price = float(request.POST.get('price', ''))
                quantity = request.POST.get('quantity', '')
                try:
                    user_product = UserProduct.objects.get(user=user,product=product,trade_type=2)
                except:
                    user_product = UserProduct(user=user,product=product,trade_type=2)
                user_product.quantity += int(quantity)
                user_product.total_buy_quantity += int(quantity)
                user_product.can_pickup_quantity += int(quantity)
                user_product.overage_unit_price = unit_price
                user_product.total = int(quantity) * float(unit_price)
                user_product.save()
                new_commissiton_sale(product,user,c_type,unit_price,quantity,quantity,1)
                return HttpResponse('OK')
            else:
                return HttpResponseServerError(u'信息错误')
        except DealException,e:
            return HttpResponseServerError(e.value)
        except:
            traceback.print_exc()
            return HttpResponseServerError(u'出售失败')


def commission_buy(request):
    user = User.objects.get(id=1)
    product = Product.objects.get(id=11)
    c_type = 2
    unit_price = 2.5
    quantity = 2
    uncomplete_quantity = 5
    commission_buy = new_commission_buy(product,user,c_type,unit_price,quantity,quantity,1)


def commission_sale(request): 
    user = User.objects.get(id=1)
    product = Product.objects.get(id=1)
    unit_price = 66
    quantity = 10
    uncomplete_quantity = 10   
    commission_sale = new_commissiton_sale(product,user,unit_price,quantity,quantity,1)


class DealException(Exception):
    def __init__(self, value):
        self.value = value
            
@transaction.atomic        
def new_commission_buy(product,user,c_type,unit_price,quantity,uncomplete_quantity,status):
    user_balance = UserBalance.objects.get(user=user)
    total = int(quantity) * float(unit_price)
    try:
        product_config = StockProductConfig.objects.get(product=product)
        max_buy_num = int(product_config.max_buy_num)
        max_deal_num = int(product_config.max_deal_num)
    except:
        raise DealException(u'商品未配置')
    if int(c_type) == 1:
        try:
            buy_num = int(UserProduct.objects.get(user=user,product=product,trade_type=1).quantity)
            can_buy_num = int(max_buy_num-buy_num)
            if can_buy_num<int(quantity):
                raise DealException(u'超出最大购买数量')
            all_commission = CommissionBuy.objects.filter(user=user,product=product,c_type=1,status__in=[1,2])
            commission_num = 0
            for commission in all_commission:
                commission_num += commission.uncomplete_quantity
            can_commission_num = int(max_buy_num-commission_num-buy_num)
            if can_commission_num<int(quantity):
                raise DealException(u'委托数量超出最大购买数量')
        except UserProduct.DoesNotExist:
            if max_buy_num < int(quantity):
                raise DealException(u'超出最大购买数量')
            all_commission = CommissionBuy.objects.filter(user=user,product=product,c_type=1,status__in=[1,2])
            commission_num = 0
            for commission in all_commission:
                commission_num += commission.uncomplete_quantity
            can_commission_num = int(max_buy_num-commission_num)
            if can_commission_num<int(quantity):
                raise DealException(u'委托数量超出最大购买数量')
    if int(c_type) == 2:
        try:
            deal_num = int(UserProduct.objects.get(user=user,product=product,trade_type=2).quantity)
            can_deal_num = int(max_deal_num - deal_num)
            if can_deal_num < int(quantity):
                raise DealException(u'超出最大进货数量')
            all_commission = CommissionBuy.objects.filter(user=user,product=product,c_type=2,status__in=[1,2])
            commission_num = 0
            for commission in all_commission:
                commission_num += commission.uncomplete_quantity
            can_commission_num = int(max_deal_num-commission_num-deal_num)
            if can_commission_num<int(quantity):
                raise DealException(u'委托数量超出最大进货数量')
        except UserProduct.DoesNotExist:
            if max_deal_num < int(quantity):
                raise DealException(u'超出最大进货数量')
            all_commission = CommissionBuy.objects.filter(user=user,product=product,c_type=2,status__in=[1,2])
            commission_num = 0
            for commission in all_commission:
                commission_num += commission.uncomplete_quantity
            can_commission_num = int(max_deal_num-commission_num)
            if can_commission_num<int(quantity):
                raise DealException(u'委托数量超出最大进货数量')
        try:
            user_product = UserProduct.objects.get(user=user,product=product,trade_type=1)
            if int(user_product.quote_quantity) < int(quantity):
                raise DealException(u'进货权不足')
        except UserProduct.DoesNotExist:
            raise DealException(u'无进货权')
    if float(user_balance.balance) >= total:
        now = datetime.datetime.now()
        commission_buy = CommissionBuy()
        commission_buy.product = product
        commission_buy.user = user
        commission_buy.c_type = c_type
        commission_buy.unit_price = unit_price
        commission_buy.quantity = quantity
        commission_buy.uncomplete_quantity = uncomplete_quantity
        commission_buy.status = status
        commission_buy.save()
        #更新行情
        update_stock_ticker(product)
        #资产变化
        buy_freezing_money(commission_buy)
        try:
            con = get_redis_connection("default")
            #买表添加数据
            key = u"buy:%d"%commission_buy.id
            value = {"product":product.id,"user":user.id,"c_type":c_type,"unit_price":float(unit_price),"quantity":quantity,"uncomplete_quantity":uncomplete_quantity,"status":status}
            con.set(key,json.dumps(value))
            #买表队列添加数据
            zkey = u"buy:%d:%d:%d"%(4,int(1764918578609-int(round(time.time()*1000))),int(commission_buy.id))
            zname = u"buyset%d"%product.id
            con.zadd(zname,int(unit_price),zkey)
            #更新行情
            update_stock_ticker_redis(product)
            #资产变化
            buy_freezing_money_redis(key,user.id,c_type,unit_price,quantity)
            #通知celery开始循环相应买表队列
            receive_buy.delay(product.id)
        except:
            traceback.print_exc()
#         receive_buy.delay(product.id)
    else:
        raise DealException(u'余额不足')

@transaction.atomic
def new_commissiton_sale(product,user,c_type,unit_price,quantity,uncomplete_quantity,status):
    try:
        user_product = UserProduct.objects.get(user=user,product=product,trade_type=2)
        if int(user_product.can_sale_quantity) < int(quantity):
            raise DealException(u'余量不足')
    except UserProduct.DoesNotExist:
        raise DealException(u'未进货')
    now = datetime.datetime.now()
    commission_sale = CommissionSale()
    commission_sale.product = product
    commission_sale.user = user
    commission_sale.c_type = 1
    commission_sale.unit_price = unit_price
    commission_sale.quantity = quantity
    commission_sale.uncomplete_quantity = uncomplete_quantity
    commission_sale.status = status
    commission_sale.save()
    #更新行情
    update_stock_ticker(product)
    #持有变化
    sale_user_product_change(commission_sale)

    
    
#更新行情    
@transaction.atomic  
def update_stock_ticker(product):
    today = datetime.datetime.now().date()
    pusher_trigger = PushTriggerTest()
    stock_ticker = StockTicker.objects.filter(product=product,created_date=today).first()
    msg = []
    high_price = TradeComplete.objects.filter(product=product,created_date=today).aggregate(Max('unit_price')).get('unit_price__max')
    low_price = TradeComplete.objects.filter(product=product,created_date=today).aggregate(Min('unit_price')).get('unit_price__min')
    max_commission_buy_price = CommissionBuy.objects.filter(product=product).exclude(status__in=[3,4]).aggregate(Max('unit_price')).get('unit_price__max')
    min_commission_sale_price = CommissionSale.objects.filter(product=product).exclude(status__in=[3,4]).aggregate(Min('unit_price')).get('unit_price__min')
    if max_commission_buy_price:
        uncomplete_buy_num = CommissionBuy.objects.filter(product=product,unit_price=max_commission_buy_price).exclude(status__in=[3,4]).aggregate(Sum('uncomplete_quantity')).get('uncomplete_quantity__sum')
        stock_ticker.bid_vol = uncomplete_buy_num
        msg.append([product.id,'bid_vol',uncomplete_buy_num])
        if stock_ticker.bid_price != max_commission_buy_price:
            stock_ticker.bid_price = max_commission_buy_price
            msg.append([product.id,'bid_price',"%.2f"%max_commission_buy_price])
    else:
        stock_ticker.bid_vol = None
        stock_ticker.bid_price = None
        msg.append([product.id,'bid_vol',u'-'])
        msg.append([product.id,'bid_price',u'-'])
    if min_commission_sale_price:
        uncomplete_sale_num = CommissionSale.objects.filter(product=product,unit_price=min_commission_sale_price).exclude(status__in=[3,4]).aggregate(Sum('uncomplete_quantity')).get('uncomplete_quantity__sum')    
        stock_ticker.ask_vol = uncomplete_sale_num
        msg.append([product.id,'ask_vol',uncomplete_sale_num])
        if stock_ticker.ask_price != min_commission_sale_price:
            stock_ticker.ask_price = min_commission_sale_price
            msg.append([product.id,'ask_price',"%.2f"%min_commission_sale_price])
    else:
        stock_ticker.ask_vol = None
        stock_ticker.ask_price = None
        msg.append([product.id,'ask_vol',u'-'])
        msg.append([product.id,'ask_price',u'-'])
    
    if stock_ticker.high != high_price:
        stock_ticker.high = high_price
        msg.append([product.id,'high',"%.2f"%high_price])
    if stock_ticker.low != low_price:
        stock_ticker.low = low_price
        msg.append([product.id,'low',"%.2f"%low_price])
    stock_ticker.save()
#     pusher_trigger.pushupdate.delay(pusher_trigger,msg)


#买卖更新redis行情    
@transaction.atomic  
def update_stock_ticker_redis(product):
    pusher_trigger = PushTriggerTest()
    con = get_redis_connection("default")
    st_key = "st:%d"%product.id
    stock_ticker = json.loads(con.get(st_key))
    zbuy_name = u"buyset%d"%product.id
    zsale_name = u"saleset%d"%product.id
    msg = []
    high_price_key = "high:price:%d"%product.id
    low_price_key = "low:price:%d"%product.id
    high_price = con.get(high_price_key)
    low_price = con.get(low_price_key)
    try:
        max_buy_price_commission_key = con.zrevrange(zbuy_name,0,0)[0]
        max_commission_buy_price = con.zscore(zbuy_name,max_buy_price_commission_key)
    except:
        max_commission_buy_price = None
    try:
        min_sale_price_commission_key = con.zrange(zsale_name,0,0)[0]
        min_commission_sale_price = con.zscore(zsale_name,min_sale_price_commission_key)
    except:
        min_commission_sale_price = None
    if max_commission_buy_price:
        bid_vol = con.zcount(zbuy_name,max_commission_buy_price,max_commission_buy_price)
        stock_ticker['bid_vol'] = bid_vol
        msg.append([product.id,'bid_vol',bid_vol])
        if stock_ticker['bid_price'] != max_commission_buy_price:
            stock_ticker['bid_price'] = max_commission_buy_price
            msg.append([product.id,'bid_price',"%.2f"%max_commission_buy_price])
    else:
        stock_ticker['bid_vol'] = None
        stock_ticker['bid_price'] = None
        msg.append([product.id,'bid_vol',u'-'])
        msg.append([product.id,'bid_price',u'-'])
    if min_commission_sale_price:
        ask_vol = con.zcount(zsale_name,min_commission_sale_price,min_commission_sale_price)
        stock_ticker['ask_vol'] = ask_vol
        msg.append([product.id,'ask_vol',ask_vol])
        if stock_ticker['ask_price'] != min_commission_sale_price:
            stock_ticker['ask_price'] = min_commission_sale_price
            msg.append([product.id,'ask_price',"%.2f"%min_commission_sale_price])
    else:
        stock_ticker['ask_vol'] = None
        stock_ticker['ask_price'] = None
        msg.append([product.id,'ask_vol',u'-'])
        msg.append([product.id,'ask_price',u'-'])
    
    if stock_ticker['high'] != high_price:
        stock_ticker['high'] = high_price
        msg.append([product.id,'high',"%.2f"%high_price])
    if stock_ticker['low'] != low_price:
        stock_ticker['low'] = low_price
        msg.append([product.id,'low',"%.2f"%low_price])
    con.set(st_key,json.dumps(stock_ticker))
#     pusher_trigger.pushupdate.delay(pusher_trigger,msg)


#成交更新redis行情    
# @transaction.atomic  
# def update_stock_ticker_redis(product):
#进货或购买冻结资产 
@transaction.atomic
def buy_freezing_money(commission_buy):
    # 资产变化
    user_money_change = UserMoneyChange()
    user_money_change.user = commission_buy.user
    if int(commission_buy.c_type) == 1:
        user_money_change.trade_type = 3
    elif int(commission_buy.c_type) == 2:
        user_money_change.trade_type = 6
    user_money_change.status = 2
    freezing_money = float(commission_buy.quantity)*float(commission_buy.unit_price)
    user_money_change.price = freezing_money
    user_money_change.product = commission_buy.product
    user_money_change.commission_buy_no = commission_buy.id
    user_money_change.commission_buy_unit_price = commission_buy.unit_price
    user_money_change.commission_buy_quantity = commission_buy.quantity
    user_money_change.custom_save()

#进货或购买冻结资产 redis
@transaction.atomic
def buy_freezing_money_redis(key,user,c_type,unit_price,quantity):
    # 资产变化
    user_money_change = {}
    user_money_change['user'] = user
    if int(c_type) == 1:
        user_money_change['trade_type'] = 3
    elif int(c_type) == 2:
        user_money_change['trade_type'] = 6
    user_money_change['status'] = 2
    freezing_money = float(commission_buy.quantity)*float(commission_buy.unit_price)
    user_money_change['price'] = freezing_money
    user_money_change['product'] = commission_buy.product
    user_money_change.commission_buy_no = commission_buy.id
    user_money_change.commission_buy_unit_price = commission_buy.unit_price
    user_money_change.commission_buy_quantity = commission_buy.quantity
    user_money_change.custom_save()
    

#成交后买方解冻资产并减少余额，卖方增加余额
@transaction.atomic
def deal_money_change(trade_complete,commission_buy,commission_sale):
    buy_user = trade_complete.commission_buy_user_id
    sale_user = trade_complete.commission_sale_user_id
    #首先解冻买方冻结资产归还给余额
    user_money_change = UserMoneyChange()
    user_money_change.user = buy_user
    if int(trade_complete.c_type) == 1:
        parent_money_change = UserMoneyChange.objects.filter(user=buy_user,product=trade_complete.product,trade_type=3,commission_buy_no=trade_complete.commission_buy_no).first()
        user_money_change.parent_id = parent_money_change
        user_money_change.trade_type = 4
    elif int(trade_complete.c_type) == 2:
        parent_money_change = UserMoneyChange.objects.filter(user=buy_user,product=trade_complete.product,trade_type=6,commission_buy_no=trade_complete.commission_buy_no).first()
        user_money_change.parent_id = parent_money_change
        user_money_change.trade_type = 7
    user_money_change.status = 2
    user_money_change.price = float(commission_buy.unit_price) * float(trade_complete.quantity)
    user_money_change.product = trade_complete.product
    user_money_change.commission_buy_no = trade_complete.commission_buy_no
    user_money_change.commission_sale_no = trade_complete.commission_sale_no
    user_money_change.commission_buy_unit_price = commission_buy.unit_price
    user_money_change.commission_sale_unit_price = commission_sale.unit_price
    user_money_change.commission_buy_quantity = commission_buy.quantity
    user_money_change.commission_sale_quantity = commission_sale.quantity
    user_money_change.trade_no = trade_complete.id
    user_money_change.trade_unit_price = trade_complete.unit_price
    user_money_change.trade_quantity = trade_complete.quantity
    user_money_change.custom_save()
    #买方余额减少
    user_money_change = UserMoneyChange()
    user_money_change.user = buy_user
    if int(trade_complete.c_type) == 1:
        user_money_change.trade_type = 5
        parent_money_change = UserMoneyChange.objects.filter(user=buy_user,product=trade_complete.product,trade_type=3,commission_buy_no=trade_complete.commission_buy_no).first()
        user_money_change.parent_id = parent_money_change
    elif int(trade_complete.c_type) == 2:
        user_money_change.trade_type = 8
        parent_money_change = UserMoneyChange.objects.filter(user=buy_user,product=trade_complete.product,trade_type=6,commission_buy_no=trade_complete.commission_buy_no).first()
        user_money_change.parent_id = parent_money_change
    user_money_change.status = 2
    user_money_change.price = float(trade_complete.unit_price) * float(trade_complete.quantity)
    user_money_change.product = trade_complete.product
    user_money_change.commission_buy_no = trade_complete.commission_buy_no
    user_money_change.commission_sale_no = trade_complete.commission_sale_no
    user_money_change.commission_buy_unit_price = commission_buy.unit_price
    user_money_change.commission_sale_unit_price = commission_sale.unit_price
    user_money_change.commission_buy_quantity = commission_buy.quantity
    user_money_change.commission_sale_quantity = commission_sale.quantity
    user_money_change.trade_no = trade_complete.id
    user_money_change.trade_unit_price = trade_complete.unit_price
    user_money_change.trade_quantity = trade_complete.quantity
    user_money_change.custom_save()
    #卖方余额增加
    user_money_change = UserMoneyChange()
    user_money_change.user = sale_user
    user_money_change.status = 2
    user_money_change.trade_type = 9
    user_money_change.price = float(trade_complete.unit_price) * float(trade_complete.quantity)
    user_money_change.product = trade_complete.product
    user_money_change.commission_buy_no = trade_complete.commission_buy_no
    user_money_change.commission_sale_no = trade_complete.commission_sale_no
    user_money_change.commission_buy_unit_price = commission_buy.unit_price
    user_money_change.commission_sale_unit_price = commission_sale.unit_price
    user_money_change.commission_buy_quantity = commission_buy.quantity
    user_money_change.commission_sale_quantity = commission_sale.quantity
    user_money_change.trade_no = trade_complete.id
    user_money_change.trade_unit_price = trade_complete.unit_price
    user_money_change.trade_quantity = trade_complete.quantity
    user_money_change.custom_save()
    #收取卖方卖手续费
    user_money_change = UserMoneyChange()
    user_money_change.user = sale_user
    user_money_change.status = 2
    user_money_change.trade_type = 15
    deal_fee = "%.2f"%float(float(trade_complete.total)/100*trade_complete.product.stock_config_product.scomm)
    user_money_change.price = float(deal_fee)
    user_money_change.product = trade_complete.product
    user_money_change.trade_no = trade_complete.id
    user_money_change.trade_unit_price = trade_complete.unit_price
    user_money_change.trade_quantity = trade_complete.quantity
    user_money_change.custom_save()


#用户挂卖单用户持有减少
@transaction.atomic    
def sale_user_product_change(commission_sale):
    user_product = UserProduct.objects.get(user=commission_sale.user,product=commission_sale.product,trade_type=2)
    user_product.can_pickup_quantity -= int(commission_sale.quantity)
    user_product.total_sale_quantity += int(commission_sale.quantity)
    user_product.total -= int(commission_sale.quantity) * float(user_product.overage_unit_price)
    user_product.custom_save()
    
    
#撤单用户资产变化
@transaction.atomic 
def cancel_commission_change(commission):
    try:
        #撤销买单
        if isinstance(commission,CommissionBuy):
            # 资产变化
            user_money_change = UserMoneyChange()
            user_money_change.user = commission.user
            user_money_change.trade_type = 13
            user_money_change.status = 2
            cancel_price = float(commission.uncomplete_quantity) * float(commission.unit_price)
            user_money_change.price = cancel_price
            user_money_change.product = commission.product
            user_money_change.commission_buy_no = commission.id
            user_money_change.commission_buy_unit_price = commission.unit_price
            user_money_change.commission_buy_quantity = commission.quantity
            user_money_change.cancel_quantity = commission.uncomplete_quantity
            user_money_change.cancel_unit_price = commission.unit_price
            user_money_change.custom_save()
            #撤销进货买单，返回用户进货权
            if commission.c_type == 2:
                user_product = UserProduct.objects.get_or_create(user=commission.user,product=commission.product,trade_type=1)[0]
                user_product.quote_quantity += float(commission.quantity)
                user_product.save()
            update_stock_ticker(commission.product)
        #撤销卖单
        elif isinstance(commission,CommissionSale):
            user_product = UserProduct.objects.get(user=commission.user,product=commission.product,trade_type=2)
            user_product.total_sale_quantity -= int(commission.uncomplete_quantity)
            user_product.can_pickup_quantity += int(commission.uncomplete_quantity)
            user_product.total += int(commission.uncomplete_quantity) * float(user_product.overage_unit_price)
            user_product.save()
            update_stock_ticker(commission.product)
    except:
        traceback.print_exc()
        

            
            
        