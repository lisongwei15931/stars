# -*- coding: utf-8 -*-s

import datetime
import json
import traceback

from django.db.models.query_utils import Q
from django.db.models import Sum
from django.http.response import HttpResponse, HttpResponseServerError, \
    HttpResponseRedirect
from django.shortcuts import render
from oscar.core.loading import get_model

from stars.apps.commission.views import new_commission_buy, new_commissiton_sale, DealException
from stars.apps.tradingcenter.forms import CommissionBuyForm, CommissionSaleForm
from stars.apps.tradingcenter.tasks import PushTriggerTest


StockTicker = get_model('commission', 'StockTicker')
StockProductConfig = get_model('commission', 'StockProductConfig')
UserProduct = get_model('commission', 'UserProduct')
UserBalance = get_model('commission', 'UserBalance')
Category = get_model('catalogue', 'Category')
Product = get_model('catalogue', 'Product')
SelfPick = get_model('tradingcenter', 'SelfPick')
CommissionBuy = get_model('commission', 'CommissionBuy')
SystemConfig = get_model('commission', 'SystemConfig')
TradeComplete = get_model('commission', 'TradeComplete')

def trading_center_index(request):
    today = datetime.datetime.now().date()
    commission_buy_form = CommissionBuyForm()
    commission_sale_form = CommissionSaleForm()
    all_category = Category.objects.filter(depth=1)
    system_config = SystemConfig.objects.first()
    open_time = system_config.bank_start_time.strftime('%H:%M')
    close_time = system_config.bank_end_time.strftime('%H:%M')
    if is_market_opening():
        open_close_msg = u"开市(当日%s-%s)"%(open_time,close_time)
        open_or_close = True
    else:
        open_close_msg = u"闭市(%s-次日%s)"%(close_time,open_time)
        open_or_close = False
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
    if request.user.is_anonymous():
        user_balance = ''
    else:
        try:
            user_balance = UserBalance.objects.get(user=request.user)
        except:
            user_balance = ''
    context = {"commission_buy_form":commission_buy_form,"commission_sale_form":commission_sale_form,"user_balance":user_balance,"categorys":all_category,"open_close_msg":open_close_msg,"open_or_close":open_or_close,
               "total_num":total_num,"total_price":total_price}
    return render(request, 'tradingcenter/tradingcenter.html', context)


def floatformat(float):
    if float:
        try:
            return "%.2f" % float
        except:
            return float
    else:
        return float


def trading_center_data(request):
    try:
        today = datetime.datetime.now().date()
        data_list = []
        keyWords = request.GET.get('keyWords')
        category_id = request.GET.get('category')
        products = ""
        if category_id == "all":
            products = Product.objects.filter(is_on_shelves = True,opening_date__lte=datetime.datetime.now().date())
        elif not category_id:
            products = Product.objects.filter(is_on_shelves = True,opening_date__lte=datetime.datetime.now().date())
        else:
            category = Category.objects.get(id=category_id)
            products = category.get_category_products()
            
        if keyWords:
            stock_ticker_list = StockTicker.objects.filter(product__in=products).filter(created_date=today).filter(Q(product_name__icontains=keyWords)|Q(product_symbol__icontains=keyWords))
        else:
            stock_ticker_list = StockTicker.objects.filter(product__in=products).filter(created_date=today)
        for stock_ticker in stock_ticker_list:
            try:
                product_config = StockProductConfig.objects.get(product=stock_ticker.product)
                one_data = {
                    "id":stock_ticker.product.id,
                    "URL":stock_ticker.product.get_absolute_url(),
                    "product_symbol":stock_ticker.product_symbol,
                    "product_name":stock_ticker.product_name,
                    "strike_price":floatformat(stock_ticker.strike_price),
                    "net_change":floatformat(stock_ticker.net_change),
                    "net_change_rise":floatformat(stock_ticker.net_change_rise),
                    "bid_price":floatformat(stock_ticker.bid_price),
                    "ask_price":floatformat(stock_ticker.ask_price),
                    "bid_vol":stock_ticker.bid_vol,
                    "ask_vol":stock_ticker.ask_vol,
                    "opening_price":floatformat(stock_ticker.opening_price),
                    "closing_price":floatformat(stock_ticker.closing_price),
                    "high":floatformat(stock_ticker.high),
                    "low":floatformat(stock_ticker.low),
                    "volume":stock_ticker.volume,
                    "total":floatformat(stock_ticker.total),
        #             "holdings":stock_holdings,
        #             "average_cost":floatformat(stock_average_cost),
        #             "stock_right":stock_right,
                    "market_capitalization":floatformat(stock_ticker.market_capitalization)
                }
                data_list.append(one_data)
            except:
                pass
        data = {"rows":data_list}
        return HttpResponse(json.dumps(data),content_type = "application/json")
    except:
        traceback.print_exc()
        
        
def trading_center_buy_right_data(request):
    try:
        user = request.user 
        user_buy_right_products = UserProduct.objects.filter(user=user,trade_type=1,quote_quantity__gt=0)
        products = []
        for right_product in user_buy_right_products:
            if right_product.product.is_on_shelves:
                products.append(right_product.product)
        today = datetime.datetime.now().date()
        data_list = []
        keyWords = request.GET.get('keyWords')
        category_id = request.GET.get('category')
        if category_id and category_id is not "all":
            category = Category.objects.get(id=category_id)
            category_products = category.get_category_products()
            products = list(set(products).intersection(set(category_products)))
            
        if keyWords:
            stock_ticker_list = StockTicker.objects.filter(product__in=products).filter(created_date=today).filter(Q(product_name__icontains=keyWords)|Q(product_symbol__icontains=keyWords))
        else:
            stock_ticker_list = StockTicker.objects.filter(product__in=products).filter(created_date=today)
        for stock_ticker in stock_ticker_list:
            product_config = StockProductConfig.objects.get(product=stock_ticker.product)
            one_data = {
                "id":stock_ticker.product.id,
                "URL":stock_ticker.product.get_absolute_url(),
                "product_symbol":stock_ticker.product_symbol,
                "product_name":stock_ticker.product_name,
                "strike_price":floatformat(stock_ticker.strike_price),
                "net_change":floatformat(stock_ticker.net_change),
                "net_change_rise":floatformat(stock_ticker.net_change_rise),
                "bid_price":floatformat(stock_ticker.bid_price),
                "ask_price":floatformat(stock_ticker.ask_price),
                "bid_vol":stock_ticker.bid_vol,
                "ask_vol":stock_ticker.ask_vol,
                "opening_price":floatformat(stock_ticker.opening_price),
                "closing_price":floatformat(stock_ticker.closing_price),
                "high":floatformat(stock_ticker.high),
                "low":floatformat(stock_ticker.low),
                "volume":stock_ticker.volume,
                "total":floatformat(stock_ticker.total),
                "market_capitalization":floatformat(product_config.market_capitalization)
            }
            data_list.append(one_data)
        data = {"rows":data_list}
        return HttpResponse(json.dumps(data),content_type = "application/json")
    except:
        traceback.print_exc()


def trading_center_sale_right_data(request):
    try:
        user = request.user 
        user_buy_right_products = UserProduct.objects.filter(user=user,trade_type=2)
        products = []
        for right_product in user_buy_right_products:
            if right_product.can_sale_quantity>0 and right_product.product.is_on_shelves:
                products.append(right_product.product)
        today = datetime.datetime.now().date()
        data_list = []
        keyWords = request.GET.get('keyWords')
        category_id = request.GET.get('category')
        if category_id and category_id is not "all":
            category = Category.objects.get(id=category_id)
            category_products = category.get_category_products()
            products = list(set(products).intersection(set(category_products)))
            
        if keyWords:
            stock_ticker_list = StockTicker.objects.filter(product__in=products).filter(created_date=today).filter(Q(product_name__icontains=keyWords)|Q(product_symbol__icontains=keyWords))
        else:
            stock_ticker_list = StockTicker.objects.filter(product__in=products).filter(created_date=today)
        for stock_ticker in stock_ticker_list:
            product_config = StockProductConfig.objects.get(product=stock_ticker.product)
            one_data = {
                "id":stock_ticker.product.id,
                "URL":stock_ticker.product.get_absolute_url(),
                "product_symbol":stock_ticker.product_symbol,
                "product_name":stock_ticker.product_name,
                "strike_price":floatformat(stock_ticker.strike_price),
                "net_change":floatformat(stock_ticker.net_change),
                "net_change_rise":floatformat(stock_ticker.net_change_rise),
                "bid_price":floatformat(stock_ticker.bid_price),
                "ask_price":floatformat(stock_ticker.ask_price),
                "bid_vol":stock_ticker.bid_vol,
                "ask_vol":stock_ticker.ask_vol,
                "opening_price":floatformat(stock_ticker.opening_price),
                "closing_price":floatformat(stock_ticker.closing_price),
                "high":floatformat(stock_ticker.high),
                "low":floatformat(stock_ticker.low),
                "volume":stock_ticker.volume,
                "total":floatformat(stock_ticker.total),
                "market_capitalization":floatformat(product_config.market_capitalization)
            }
            data_list.append(one_data)
        data = {"rows":data_list}
        return HttpResponse(json.dumps(data),content_type = "application/json")
    except:
        traceback.print_exc()


def trading_center_new_product_data(request):
    try:
        today = datetime.datetime.now().date()
        start_day = today + datetime.timedelta(days=-7)
        products = Product.objects.filter(opening_date__range=[start_day,today])
        data_list = []
        keyWords = request.GET.get('keyWords')
        category_id = request.GET.get('category')
        if category_id and category_id is not "all":
            category = Category.objects.get(id=category_id)
            category_products = category.get_category_products()
            products = list(set(products).intersection(set(category_products)))
            
        if keyWords:
            stock_ticker_list = StockTicker.objects.filter(product__in=products).filter(created_date=today).filter(Q(product_name__icontains=keyWords)|Q(product_symbol__icontains=keyWords))
        else:
            stock_ticker_list = StockTicker.objects.filter(product__in=products).filter(created_date=today)
        for stock_ticker in stock_ticker_list:
            product_config = StockProductConfig.objects.get(product=stock_ticker.product)
            one_data = {
                "id":stock_ticker.product.id,
                "URL":stock_ticker.product.get_absolute_url(),
                "product_symbol":stock_ticker.product_symbol,
                "product_name":stock_ticker.product_name,
                "strike_price":floatformat(stock_ticker.strike_price),
                "net_change":floatformat(stock_ticker.net_change),
                "net_change_rise":floatformat(stock_ticker.net_change_rise),
                "bid_price":floatformat(stock_ticker.bid_price),
                "ask_price":floatformat(stock_ticker.ask_price),
                "bid_vol":stock_ticker.bid_vol,
                "ask_vol":stock_ticker.ask_vol,
                "opening_price":floatformat(stock_ticker.opening_price),
                "closing_price":floatformat(stock_ticker.closing_price),
                "high":floatformat(stock_ticker.high),
                "low":floatformat(stock_ticker.low),
                "volume":stock_ticker.volume,
                "total":floatformat(stock_ticker.total),
                "market_capitalization":floatformat(product_config.market_capitalization)
            }
            data_list.append(one_data)
        data = {"rows":data_list}
        return HttpResponse(json.dumps(data),content_type = "application/json")
    except:
        traceback.print_exc()
        
        
def trading_center_self_pick_data(request):
    try:
        today = datetime.datetime.now().date()
        self_pick = SelfPick.objects.get_or_create(user=request.user)[0]
        products = self_pick.product.filter(is_on_shelves=True)
        
        data_list = []
        keyWords = request.GET.get('keyWords')
        category_id = request.GET.get('category')
        if category_id and category_id is not "all":
            category = Category.objects.get(id=category_id)
            category_products = category.get_category_products()
            products = list(set(products).intersection(set(category_products)))
            
        if keyWords:
            stock_ticker_list = StockTicker.objects.filter(product__in=products).filter(created_date=today).filter(Q(product_name__icontains=keyWords)|Q(product_symbol__icontains=keyWords))
        else:
            stock_ticker_list = StockTicker.objects.filter(product__in=products).filter(created_date=today)
        for stock_ticker in stock_ticker_list:
            product_config = StockProductConfig.objects.get(product=stock_ticker.product)
            one_data = {
                "id":stock_ticker.product.id,
                "URL":stock_ticker.product.get_absolute_url(),
                "product_symbol":stock_ticker.product_symbol,
                "product_name":stock_ticker.product_name,
                "strike_price":floatformat(stock_ticker.strike_price),
                "net_change":floatformat(stock_ticker.net_change),
                "net_change_rise":floatformat(stock_ticker.net_change_rise),
                "bid_price":floatformat(stock_ticker.bid_price),
                "ask_price":floatformat(stock_ticker.ask_price),
                "bid_vol":stock_ticker.bid_vol,
                "ask_vol":stock_ticker.ask_vol,
                "opening_price":floatformat(stock_ticker.opening_price),
                "closing_price":floatformat(stock_ticker.closing_price),
                "high":floatformat(stock_ticker.high),
                "low":floatformat(stock_ticker.low),
                "volume":stock_ticker.volume,
                "total":floatformat(stock_ticker.total),
                "market_capitalization":floatformat(product_config.market_capitalization)
            }
            data_list.append(one_data)
        data = {"rows":data_list}
        return HttpResponse(json.dumps(data),content_type = "application/json")
    except:
        traceback.print_exc()
        

def multiple_deal(request):
    if not is_market_opening():
        return HttpResponseServerError(u'已闭市,请在开始时操作')
    try:
        buy_info = request.POST.getlist('buy_info[]')
        user=request.user
        response_msg = {"status":"suc","msg":[]}
        err_msg = []
        for info in buy_info:
            info_list = info.split(',')
            product_id = info_list[0]
            price = info_list[1]
            deal_num = info_list[2]
            product = Product.objects.get(id=product_id)
            product_config = product.stock_config_product
            config_max_num = int(product_config.max_deal_num)
            if request.GET.get('type') == "buy":
                try:
                    quote_quantity = int(UserProduct.objects.get(user=user,product=product,trade_type=1).quote_quantity)
                except UserProduct.DoesNotExist:
                    quote_quantity = 0
                try:
                    buy_num = int(UserProduct.objects.get(user=user,product=product,trade_type=2).quantity)
                    all_commission = CommissionBuy.objects.filter(user=user,product=product,c_type=2,status__in=[1,2])
                    commission_num = 0
                    for commission in all_commission:
                        commission_num += commission.uncomplete_quantity
                    max_buy_num = int(config_max_num-commission_num-buy_num)
                except UserProduct.DoesNotExist:
                    all_commission = CommissionBuy.objects.filter(user=user,product=product,c_type=2,status__in=[1,2])
                    commission_num = 0
                    for commission in all_commission:
                        commission_num += commission.uncomplete_quantity
                    max_buy_num = int(config_max_num-commission_num)
                if quote_quantity < max_buy_num:
                    max_deal_num = quote_quantity
                elif quote_quantity > max_buy_num:
                    max_deal_num = max_buy_num
                else:
                    max_deal_num=0
            elif request.GET.get('type') == "sale":
                try:
                    max_deal_num = UserProduct.objects.get(user=user,product=product,trade_type=2).can_sale_quantity
                except:
                    max_deal_num = 0
            msg = [product.get_title()]
            if int(deal_num) > int(max_deal_num):
                msg_str = (u'数量错误,最大交易数量为:%d')%max_deal_num
                msg.append(msg_str)
            min_price = float(product.price_range[0])
            max_price = float(product.price_range[1])
            if float(price)<min_price or float(price)>max_price:
                msg_str = (u'价格错误,价格区间:%.2f~%.2f')%(min_price,max_price)
                msg.append(msg_str)
            if len(msg)>1:
                msg = ' '.join(msg)
                err_msg.append(msg)
        if len(err_msg)>0:
            response_msg['status'] = u"err"
            response_msg['msg'] = err_msg
        elif len(err_msg)==0:
            for info in buy_info:
                info_list = info.split(',')
                product_id = info_list[0]
                price = info_list[1]
                deal_num = info_list[2]
                product = Product.objects.get(id=product_id)
                if int(deal_num) > 0:
                    if request.GET.get('type') == "buy":
                        new_commission_buy(product,user,2,price,deal_num,deal_num,1)
                    elif request.GET.get('type') == "sale":
                        new_commissiton_sale(product,user,1,price,deal_num,deal_num,1)
        return HttpResponse(json.dumps(response_msg),content_type = "application/json")
    except DealException,e:
        traceback.print_exc()
        return HttpResponseServerError(e.value)


def redirect_to_buy(request,pid):
    product = Product.objects.get(id=pid)
    return HttpResponseRedirect(product.get_absolute_url())
    

def add_self_pick(request):
    user=request.user
    self_pick = SelfPick.objects.get_or_create(user=user)[0]
    products = request.POST.getlist('products[]')
    for product_id in products:
        product = Product.objects.get(id=product_id)
        self_pick.product.add(product)
    return HttpResponse('ok')


def remove_self_pick(request):
    user=request.user
    self_pick = SelfPick.objects.get_or_create(user=user)[0]
    products = request.POST.getlist('products[]')
    for product_id in products:
        product = Product.objects.get(id=product_id)
        self_pick.product.remove(product)
    return HttpResponse('ok')


def get_selected_products_info(request):
    request_type = request.GET.get('type')
    if not is_market_opening():
        return HttpResponseServerError(u'已闭市,请在开始时操作')
    if request.user.is_anonymous():
        return HttpResponseServerError(u'请登陆')
    try:
        user = request.user
        products = request.POST.getlist('products[]')
        product_info = []
        for product_id in products:
            today = datetime.datetime.now().date()
            product = Product.objects.get(id=product_id)
            product_config = product.stock_config_product
            config_max_num = int(product_config.max_deal_num)
            stock_ticker = StockTicker.objects.filter(product=product).filter(created_date=today)[0]
            if stock_ticker.strike_price:
                strike_price = floatformat(stock_ticker.strike_price)
            else:
                strike_price = "-"
            try:
                quote_quantity = int(UserProduct.objects.get(user=user,product=product,trade_type=1).quote_quantity)
            except UserProduct.DoesNotExist:
                quote_quantity = 0
            if request_type == "buy":
                try:
                    buy_num = int(UserProduct.objects.get(user=user,product=product,trade_type=2).quantity)
                    all_commission = CommissionBuy.objects.filter(user=user,product=product,c_type=2,status__in=[1,2])
                    commission_num = 0
                    for commission in all_commission:
                        commission_num += commission.uncomplete_quantity
                    max_buy_num = int(config_max_num-commission_num-buy_num)
                except UserProduct.DoesNotExist:
                    all_commission = CommissionBuy.objects.filter(user=user,product=product,c_type=2,status__in=[1,2])
                    commission_num = 0
                    for commission in all_commission:
                        commission_num += commission.uncomplete_quantity
                    max_buy_num = int(config_max_num-commission_num)
                if quote_quantity < max_buy_num:
                    max_deal_num = quote_quantity
                elif quote_quantity > max_buy_num:
                    max_deal_num = max_buy_num
                else:
                    max_deal_num=quote_quantity
            elif request_type == "sale":
                try:
                    max_deal_num = UserProduct.objects.get(user=user,product=product,trade_type=2).can_sale_quantity
                except:
                    max_deal_num = 0
            try:
                image_url = product.primary_image().original.url
            except:
                image_url = ""
            try:
                user_product = UserProduct.objects.get(user=user,trade_type=2,product=product)
                hold_quantity = user_product.quantity
                overage_unit_price = user_product.overage_unit_price
                increase = "%.2f"%((float(product.strike_price)-float(user_product.overage_unit_price))*int(user_product.quantity))
            except:
                hold_quantity = 0
                overage_unit_price = 0
                increase = 0
            info = {"id":product.id,"upc":product.upc,"name":product.get_title(),"strike_price":strike_price,"product_price":product.product_price,"product_url":product.get_absolute_url(),
                    "price_range":product.price_range,"max_buy_num":max_deal_num,"quote":product.quote,"bid_price":floatformat(stock_ticker.bid_price),"ask_price":floatformat(stock_ticker.ask_price),
                    "net_change":floatformat(stock_ticker.net_change),"net_change_rise":floatformat(stock_ticker.net_change_rise),"closing_price":floatformat(stock_ticker.closing_price),
                    "primary_image":image_url,"hold_quantity":hold_quantity,"overage_unit_price":"%.2f"%overage_unit_price,"quote_quantity":quote_quantity,"increase":increase}
            product_info.append(info)
        return HttpResponse(json.dumps(product_info),content_type = "application/json")
    except:
        traceback.print_exc()


def push_user_money(user):
    user_balance = "%.2f" % float(UserBalance.objects.get(user=user).balance)
    pusher_trigger = PushTriggerTest()
    pusher_trigger.pushmoney.delay(pusher_trigger,[int(user.id),user_balance])

def truncate_database(request):
    try:
        from stars.apps.commission.market_config import do_truncate_database, \
    before_market_open
        do_truncate_database()
        before_market_open()
        return HttpResponse(u'重置成功')
    except:
        return HttpResponse(u'重置失败，请联系管理员')


def receive_data(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        password = request.POST.get('num', '')
    return HttpResponse('OK')

def is_market_opening():
    system_config = SystemConfig.objects.first()
    now = datetime.datetime.now().time()
    if system_config.bank_start_time <= now and now <= system_config.bank_end_time:
        return True
    else:
        return False
    
def market_closed(request):
    context = {"msg":'已闭市,请在开市时操作'}
    return render(request, 'tradingcenter/market_closed_error.html', context)


