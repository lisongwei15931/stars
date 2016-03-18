# -*- coding: utf-8 -*-s
import os, sys
import django

from stars.celery import app
import datetime
import random
import string
import traceback

from django.db import transaction
from django.db.models import Min, Sum, Max
from oscar.core.loading import get_model
from django.contrib.auth.models import User
from stars.apps.tradingcenter.tasks import PushTriggerTest


path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path[0:path.rfind('stars')])
os.environ['DJANGO_SETTINGS_MODULE'] = 'stars.settings'
django.setup()



CommissionBuy = get_model('commission','CommissionBuy')
CommissionSale = get_model('commission','CommissionSale')
TradeComplete = get_model('commission', 'TradeComplete')
StockTicker = get_model('commission', 'StockTicker')
StockProductConfig = get_model('commission', 'StockProductConfig')
UserMoneyChange = get_model('commission', 'UserMoneyChange')
SystemConfig = get_model('commission', 'SystemConfig')

#成交后买方解冻资产并减少余额，卖方增加余额
@transaction.atomic
def deal_money_change_task(trade_complete,commission_buy,commission_sale):
    buy_user = trade_complete.commission_buy_user_id
    sale_user = trade_complete.commission_sale_user_id
    system_config = SystemConfig.objects.get(id=1)
    platform_user = User.objects.get(username=system_config.platform_user)
    #第三方支付只增加卖方余额并收取手续费
    if trade_complete.order and trade_complete.order.pay_type==2:
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
        #手续费转给平台用户
        user_money_change = UserMoneyChange()
        user_money_change.user = platform_user
        user_money_change.status = 2
        user_money_change.trade_type = 21
        deal_fee = "%.2f"%float(float(trade_complete.total)/100*trade_complete.product.stock_config_product.scomm)
        user_money_change.price = float(deal_fee)
        user_money_change.product = trade_complete.product
        user_money_change.trade_no = trade_complete.id
        user_money_change.trade_unit_price = trade_complete.unit_price
        user_money_change.trade_quantity = trade_complete.quantity
        user_money_change.custom_save()
    else:
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
        #如果是购买成交
        if trade_complete.order:
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
            user_money_change.price = float(commission_buy.unit_price) * float(trade_complete.quantity)
            user_money_change.product = trade_complete.product
            user_money_change.commission_buy_no = trade_complete.commission_buy_no
            user_money_change.commission_sale_no = trade_complete.commission_sale_no
            user_money_change.commission_buy_unit_price = commission_buy.unit_price
            user_money_change.commission_sale_unit_price = commission_sale.unit_price
            user_money_change.commission_buy_quantity = commission_buy.quantity
            user_money_change.commission_sale_quantity = commission_sale.quantity
            user_money_change.trade_no = trade_complete.id
            user_money_change.trade_unit_price = float(commission_buy.unit_price)
            user_money_change.trade_quantity = trade_complete.quantity
            user_money_change.custom_save()
            extra_price = float(commission_buy.unit_price) - float(trade_complete.unit_price)
            order_extra_change = UserMoneyChange()
            order_extra_change.user = platform_user
            order_extra_change.trade_type = 20
            order_extra_change.status = 2
            order_extra_change.price = extra_price
            order_extra_change.order_no = trade_complete.order.order_no
            order_extra_change.custom_save()
        #进货成交
        else:
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
        #手续费转给平台用户
        user_money_change = UserMoneyChange()
        user_money_change.user = platform_user
        user_money_change.status = 2
        user_money_change.trade_type = 21
        deal_fee = "%.2f"%float(float(trade_complete.total)/100*trade_complete.product.stock_config_product.scomm)
        user_money_change.price = float(deal_fee)
        user_money_change.product = trade_complete.product
        user_money_change.trade_no = trade_complete.id
        user_money_change.trade_unit_price = trade_complete.unit_price
        user_money_change.trade_quantity = trade_complete.quantity
        user_money_change.custom_save()

@transaction.atomic
def new_trade_complete_task(commission_buy,commission_sale,
                       commission_buy_user,commission_sale_user,c_type,unit_price,quantity,commission_quantity,order):
    trade_no = ''.join(random.sample(string.ascii_letters + string.digits, 15))
    trade_complete = TradeComplete()
    trade_complete.trade_no = trade_no
    product = commission_buy.product
    trade_complete.product = product
    if order:
        trade_complete.order = order
    trade_complete.commission_buy_no = commission_buy.id
    trade_complete.commission_sale_no = commission_sale.id
    trade_complete.commission_buy_user_id = commission_buy_user
    trade_complete.commission_sale_user_id = commission_sale_user
    trade_complete.c_type = c_type
    trade_complete.unit_price = unit_price
    trade_complete.quantity = quantity
    trade_complete.total = unit_price * quantity
    trade_complete.commission_quantity = commission_quantity
    trade_complete.can_pickup_quantity = quantity
    trade_complete.save()
    #资产变化
    deal_money_change_task(trade_complete,commission_buy,commission_sale)
    #开始修改行情表 
    today = datetime.datetime.now().date()
    stock_ticker = StockTicker.objects.filter(product=product,created_date=today).first()
    pusher_trigger = PushTriggerTest()
    if stock_ticker:
        msg = []
        if not stock_ticker.opening_price:
            stock_ticker.opening_price = unit_price
            msg.append([product.id,'opening_price',unit_price])
        if unit_price != stock_ticker.strike_price:
            stock_ticker.strike_price = unit_price
            net_change = float("%.2f" % (unit_price - stock_ticker.closing_price))
            if float(stock_ticker.closing_price) == 0:
                net_change_rise = net_change
            else:
                net_change_rise = float("%.2f" % (net_change/stock_ticker.closing_price*100))
            stock_ticker.net_change = net_change
            stock_ticker.net_change_rise = net_change_rise
            msg.append([product.id,'strike_price',"%.2f"%unit_price])
            msg.append([product.id,'net_change',net_change])
            msg.append([product.id,'net_change_rise',net_change_rise])
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
        high_price = TradeComplete.objects.filter(product=product,created_date=today).aggregate(Max('unit_price')).get('unit_price__max')
        low_price = TradeComplete.objects.filter(product=product,created_date=today).aggregate(Min('unit_price')).get('unit_price__min')
        volume = TradeComplete.objects.filter(product=product,created_date=today).aggregate(Sum('quantity')).get('quantity__sum')
        total = TradeComplete.objects.filter(product=product,created_date=today).aggregate(Sum('total')).get('total__sum')
        if stock_ticker.high != high_price:
            stock_ticker.high = high_price
            msg.append([product.id,'high',"%.2f"%high_price])
        if stock_ticker.low != low_price:
            stock_ticker.low = low_price
            msg.append([product.id,'low',"%.2f"%low_price])
        if stock_ticker.volume != volume:
            stock_ticker.volume = volume
            msg.append([product.id,'volume',volume])
        if stock_ticker.total != total:
            stock_ticker.total = total
            msg.append([product.id,'total',"%.2f"%total])
        stock_ticker.save()
        total_num = TradeComplete.objects.filter(created_date=today).aggregate(Sum('quantity')).get('quantity__sum')
        total_price = TradeComplete.objects.filter(created_date=today).aggregate(Sum('total')).get('total__sum')
        if not total_num:
            total_num=0
        if not total_price:
            total_price = 0
        elif float(total_price) >= 10000:
            total_price = u"%.2f万"%(float(total_price)/10000)
        elif float(total_price) < 10000:
            total_price = u"%.2f"%float(total_price)
        msg.append(["","total_num",total_num])
        msg.append(["","total_price",total_price])
        pusher_trigger.pushupdate.delay(pusher_trigger,msg)
    else:
        stock_ticker = StockTicker()
        stock_ticker.product = product
        stock_ticker.product_symbol = product.upc
        stock_ticker.product_name = product.get_title()
        stock_ticker.strike_price = unit_price
        max_commission_buy_price = CommissionBuy.objects.filter(product=product).exclude(status__in=[3,4]).aggregate(Max('unit_price')).get('unit_price__max')
        min_commission_sale_price = CommissionSale.objects.filter(product=product).exclude(status__in=[3,4]).aggregate(Min('unit_price')).get('unit_price__min')
        stock_ticker.bid_price = max_commission_buy_price
        stock_ticker.ask_price = min_commission_sale_price
        uncomplete_buy_num = CommissionBuy.objects.filter(product=product).exclude(status__in=[3,4]).aggregate(Sum('uncomplete_quantity')).get('uncomplete_quantity__sum')
        uncomplete_sale_num = CommissionSale.objects.filter(product=product).exclude(status__in=[3,4]).aggregate(Sum('uncomplete_quantity')).get('uncomplete_quantity__sum')    
        stock_ticker.bid_vol = uncomplete_buy_num
        stock_ticker.ask_vol = uncomplete_sale_num
        stock_ticker.opening_price = unit_price
        stock_ticker.high = unit_price
        stock_ticker.low = unit_price
        stock_ticker.volume = quantity
        total = float("%.2f"%(quantity*unit_price))
        stock_ticker.total = total
        product_config = StockProductConfig.objects.filter(product=product).first()
        market_capitalization = product_config.market_capitalization
        stock_ticker.market_capitalization = market_capitalization
        #计算涨跌，涨幅，昨收
        last_trade_complete = TradeComplete.objects.filter(product=product).exclude(created_date=today).order_by('-created_datetime')[:1].first()
        if last_trade_complete:
            closing_price = last_trade_complete.unit_price
            stock_ticker.closing_price = closing_price
            net_change = unit_price - closing_price
            net_change_rise = float("%.2f"%(net_change/closing_price*100))
            stock_ticker.net_change = net_change
            stock_ticker.net_change_rise = net_change_rise
        else:
            closing_price = 0
            stock_ticker.closing_price = 0
            net_change = 0
            net_change_rise = 0
            stock_ticker.net_change = net_change
            stock_ticker.net_change_rise = net_change_rise
        stock_ticker.save()
        msg = {
            "id":product.id,
            "product_symbol":product.upc,
            "product_name":product.get_title(),
            "strike_price":unit_price,
            "net_change":net_change,
            "net_change_rise":net_change_rise,
            "bid_price":max_commission_buy_price,
            "ask_price":min_commission_sale_price,
            "bid_vol":uncomplete_buy_num,
            "ask_vol":uncomplete_sale_num,
            "opening_price":unit_price,
            "closing_price":closing_price,
            "high":unit_price,
            "low":unit_price,
            "volume":quantity,
            "total":total,
            "holdings":"0",
            "average_cost":"0",
            "stock_right":"0",
            "market_capitalization":market_capitalization
        }
        pusher_trigger.pushadd.delay(pusher_trigger,msg)

@app.task()
def receive_deal(deal_quantity,commission_buy,commission_sale,order):
    try:
        #判断买单卖单未完成数量是否大于交易数量
        if commission_buy.uncomplete_quantity >= deal_quantity and commission_sale.uncomplete_quantity >= deal_quantity:
            commission_buy.uncomplete_quantity -= deal_quantity
            if commission_buy.uncomplete_quantity > 0:
                commission_buy.status = 2
            else:
                commission_buy.status = 3
            commission_buy.save()
            commission_sale.uncomplete_quantity -= deal_quantity
            if commission_sale.uncomplete_quantity > 0:
                commission_sale.status = 2
            else:
                commission_sale.status = 3
            commission_sale.save()
            new_trade_complete_task(commission_buy,commission_sale,
                                       commission_buy.user,commission_sale.user,commission_buy.c_type,commission_sale.unit_price,deal_quantity,commission_buy.quantity,order)
    except:
        traceback.print_exc()

@app.task()
def tt(x, y):
    return x + y
