#coding=utf-8
import datetime
import os
import sys
import traceback
import json

path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path[0:path.rfind('stars')])
os.environ['DJANGO_SETTINGS_MODULE'] = 'stars.settings'

import django
django.setup()
from django.db.models import Sum
from django.contrib.auth.models import User
from oscar.core.loading import get_model

from stars.apps.commission.models import StockTicker
from django_redis import get_redis_connection



Product = get_model('catalogue', 'product')
CommissionBuy = get_model('commission', 'CommissionBuy')
CommissionBuyBackup = get_model('commission', 'CommissionBuyBackup')
UserMoneyChange = get_model('commission', 'UserMoneyChange')
CommissionSale = get_model('commission', 'CommissionSale')
CommissionSaleBackup = get_model('commission', 'CommissionSaleBackup')
UserProduct = get_model('commission', 'UserProduct')
TradeComplete = get_model('commission', 'TradeComplete')
StockProductConfig = get_model('commission', 'StockProductConfig')
UserAssetDailyReport = get_model('commission', 'UserAssetDailyReport')
UserBalance = get_model('commission', 'UserBalance')
PickupDetail = get_model('commission', 'PickupDetail')
PickupList = get_model('commission', 'PickupList')
ConfirmDeal = get_model('commission', 'ConfirmDeal')
Basket = get_model('basket', 'Basket')
ProductOrder = get_model('commission', 'ProductOrder')
SystemConfig = get_model('commission', 'SystemConfig')

def before_market_open():
    try:
        all_product = Product.objects.filter(is_on_shelves=True,opening_date__lte=datetime.datetime.now().date()).distinct()
        for product in all_product:
            try:
                product_config = StockProductConfig.objects.get(product=product)
                stock_ticker = StockTicker()
                stock_ticker.product = product
                stock_ticker.product_symbol = product.upc
                stock_ticker.product_name = product.get_title()
                all_user_product = UserProduct.objects.filter(product=product)
                if all_user_product:
                    all_user_product_quantity = all_user_product.aggregate(Sum('quantity')).get('quantity__sum')
                    stock_ticker.market_capitalization = "%.2f"%(float(product.strike_price)*float(all_user_product_quantity))
                #计算涨跌，涨幅，昨收
                today = datetime.datetime.now().date()
                last_trade_complete = TradeComplete.objects.filter(product=product).exclude(created_date=today).order_by('-created_datetime')[:1].first()
                if last_trade_complete:
                    closing_price = last_trade_complete.unit_price
                    stock_ticker.closing_price = closing_price
                else:
                    closing_price = float(product_config.opening_price)
                    stock_ticker.closing_price = float(product_config.opening_price)
                stock_ticker.save()
            except:
                traceback.print_exc()
                print product.upc,u"no config"
        all_user = User.objects.all()
        for user in all_user:
            try:
                user_balance = UserBalance.objects.get(user=user)
                today = datetime.datetime.now().date()
                user_asset_daily_report = UserAssetDailyReport()
                user_asset_daily_report.user = user 
                user_asset_daily_report.target_date = today
                user_asset_daily_report.start_balance = user_balance.balance
                user_asset_daily_report.end_balance = user_balance.balance
                user_asset_daily_report.can_use_amount = user_balance.balance
                user_asset_daily_report.can_out_amount = user_balance.balance
                user_asset_daily_report.total = user_balance.balance
                user_asset_daily_report.save()
            except:
                print user
                traceback.print_exc()
        print u'market opend'
        all_open_basket = Basket.objects.filter(status = u'Open')
        for basket in all_open_basket:
            lines = basket.all_lines()
            for line in lines:
                line.refresh_buy_price()
    except:
        traceback.print_exc()
    finally:
        system_config = SystemConfig.objects.first()
        system_config.is_open = True
        system_config.save()
        
        

# def before_market_open_redis():
#     try:
#         con = get_redis_connection("default")
#         all_stock_ticker = StockTicker.objects.all()
#         #新建redis行情
#         for one_stock_ticker in all_stock_ticker:
#             stock_ticker = object_to_dict(one_stock_ticker)
#             stock_ticker['created_date'] = stock_ticker['created_date'].strftime('%Y-%m-%d')
#             stock_ticker['created_datetime'] = stock_ticker['created_datetime'].strftime('%Y-%m-%d %H:%M:%S')
#             stock_ticker['modified_datetime'] = stock_ticker['modified_datetime'].strftime('%Y-%m-%d %H:%M:%S')
#             stock_ticker = json.dumps(stock_ticker)
#             st_key = "st:%d"%float(one_stock_ticker.product_id)
#             con.set(st_key,stock_ticker)
#             #新建redis产品最高价和最低价
#             high_price_key = "high:price:%d"%float(one_stock_ticker.product_id)
#             low_price_key = "low:price:%d"%float(one_stock_ticker.product_id)
#             con.set(high_price_key,0)
#             con.set(low_price_key,0)
#             #新建redis产品配置表
#             product_config = StockProductConfig.objects.get(product=one_stock_ticker.product)
#             product_config = object_to_dict(product_config)
#             product_config['created_date'] = product_config['created_date'].strftime('%Y-%m-%d')
#             product_config['created_time'] = product_config['created_time'].strftime('%H:%M:%S')
#             product_config['modified_date'] = product_config['modified_date'].strftime('%Y-%m-%d')
#             product_config['modified_time'] = product_config['modified_time'].strftime('%H:%M:%S')
#             product_config = json.dumps(product_config)
#             product_config_key = "product:config:%d"%float(one_stock_ticker.product_id)
#             con.set(product_config_key,product_config)
#         #新建redis余额
#         all_user_balance = UserBalance.objects.all()
#         for one_user_balance in all_user_balance:
#             user_balance = object_to_dict(one_user_balance)
#             user_balance['created_date'] = user_balance['created_date'].strftime('%Y-%m-%d')
#             user_balance['created_time'] = user_balance['created_time'].strftime('%H:%M:%S')
#             user_balance['modified_date'] = user_balance['modified_date'].strftime('%Y-%m-%d')
#             user_balance['modified_time'] = user_balance['modified_time'].strftime('%H:%M:%S')
#             user_balance = json.dumps(user_balance)
#             ub_key = "ub:%d"%one_user_balance.user_id
#             con.set(ub_key,user_balance)
#         #新建redis日报
#         all_daily_report = UserAssetDailyReport.objects.all()
#         for one_daily_report in all_daily_report:
#             daily_report = object_to_dict(one_daily_report)
#             daily_report['target_date'] = daily_report['target_date'].strftime('%Y-%m-%d')
#             daily_report['created_date'] = daily_report['created_date'].strftime('%Y-%m-%d')
#             daily_report['created_time'] = daily_report['created_time'].strftime('%H:%M:%S')
#             daily_report['modified_date'] = daily_report['modified_date'].strftime('%Y-%m-%d')
#             daily_report['modified_time'] = daily_report['modified_time'].strftime('%H:%M:%S')
#             daily_report = json.dumps(daily_report)
#             ud_key = "ud:%d"%one_daily_report.user_id
#             con.set(ud_key,daily_report)
#         #新建redis成交信息
#         all_trade_complete = TradeComplete.objects.all()
#         for one_trade_complete in all_trade_complete:
#             trade_complete = object_to_dict(one_trade_complete)
#             trade_complete['created_date'] = trade_complete['created_date'].strftime('%Y-%m-%d')
#             trade_complete['created_datetime'] = trade_complete['created_datetime'].strftime('%Y-%m-%d %H:%M:%S')
#             trade_complete['modified_datetime'] = trade_complete['modified_datetime'].strftime('%Y-%m-%d %H:%M:%S')
#             trade_complete = json.dumps(trade_complete)
#             trade_key = "trade:%d:%d"%(float(one_trade_complete.commission_buy_no),float(one_trade_complete.commission_sale_no))
#             con.set(trade_key,trade_complete)
#             buy_trade_set_key = "trade:%d"%one_trade_complete.commission_buy_user_id_id
#             sale_trade_set_key = "trade:%d"%one_trade_complete.commission_sale_user_id_id
#             con.sadd(buy_trade_set_key,trade_key)
#             con.set(sale_trade_set_key,trade_key)
#         #新建redis用户资产变化
#         all_user_money_change = UserMoneyChange.objects.all()
#         for one_user_money_change in all_user_money_change:
#             user_money_change = object_to_dict(one_user_money_change)
#             user_money_change['created_date'] = user_money_change['created_date'].strftime('%Y-%m-%d')
#             user_money_change['created_time'] = user_money_change['created_time'].strftime('%H:%M:%S')
#             user_money_change['modified_date'] = user_money_change['modified_date'].strftime('%Y-%m-%d')
#             user_money_change['modified_time'] = user_money_change['modified_time'].strftime('%H:%M:%S')
#             user_money_change = json.dumps(user_money_change)
#             umc_key = "umc:%d"%float(one_user_money_change.user_id)
#             con.set(umc_key,user_money_change)
#             umc_set_key = "umc_set:%d"%float(one_user_money_change.user_id)
#             con.sadd(umc_set_key,umc_key)
#         #新建redis用户持有
#         all_user_product = UserProduct.objects.all()
#         for one_user_product in all_user_product:
#             user_product = object_to_dict(one_user_product)
#             user_product['created_date'] = user_product['created_date'].strftime('%Y-%m-%d')
#             user_product['created_time'] = user_product['created_time'].strftime('%H:%M:%S')
#             user_product['modified_date'] = user_product['modified_date'].strftime('%Y-%m-%d')
#             user_product['modified_time'] = user_product['modified_time'].strftime('%H:%M:%S')
#             user_product = json.dumps(user_product)
#             up_key = "up:%d:%d:%d"%(float(one_user_product.user_id),float(one_user_product.user_id),float(one_user_product.trade_type))
#             con.set(up_key,user_product)
#             up_set_key = "up_set:%d"%float(one_user_product.user_id)
#             con.sadd(up_set_key,up_key)
#         #新建redis成交量，成交额
#         con.set("total_num",0)
#         con.set("total_price",0)
#         
#             
#     except:
#         traceback.print_exc()


def after_market_off():
    try:
        all_buy_commission = CommissionBuy.objects.all()
        for commission_buy in all_buy_commission:
            commission_buy_backup = CommissionBuyBackup()
            commission_buy_backup.product = commission_buy.product
            commission_buy_backup.user = commission_buy.user
            commission_buy_backup.c_type = commission_buy.c_type
            commission_buy_backup.unit_price = commission_buy.unit_price
            commission_buy_backup.quantity = commission_buy.quantity
            commission_buy_backup.uncomplete_quantity = commission_buy.uncomplete_quantity
            commission_buy_backup.status = commission_buy.status
            commission_buy_backup.created_datetime = commission_buy.created_datetime
            commission_buy_backup.modified_datetime = commission_buy.modified_datetime
            commission_buy_backup.save()
            if commission_buy.status in [1,2]:
                # 用户资产变化
                user_money_change = UserMoneyChange()
                user_money_change.user = commission_buy.user
                user_money_change.trade_type = 14
                user_money_change.status = 2
                cancel_price = float(commission_buy.uncomplete_quantity) * float(commission_buy.unit_price)
                user_money_change.price = cancel_price
                user_money_change.product = commission_buy.product
                user_money_change.commission_buy_no = commission_buy.id
                user_money_change.commission_buy_unit_price = commission_buy.unit_price
                user_money_change.commission_buy_quantity = commission_buy.quantity
                user_money_change.cancel_quantity = commission_buy.uncomplete_quantity
                user_money_change.cancel_unit_price = commission_buy.unit_price
                user_money_change.custom_save()
            #闭市撤单返回进货权
            if commission_buy.c_type == 2:
                user_product = UserProduct.objects.get_or_create(user=commission_buy.user,product=commission_buy.product,trade_type=1)[0]
                user_product.quote_quantity += float(commission_buy.quantity)
                user_product.save()
            commission_buy.delete()
        all_sale_commission = CommissionSale.objects.all()
        for commission_sale in all_sale_commission:
            commission_sale_backup = CommissionSaleBackup()
            commission_sale_backup.product = commission_sale.product
            commission_sale_backup.user = commission_sale.user
            commission_sale_backup.c_type = commission_sale.c_type
            commission_sale_backup.unit_price = commission_sale.unit_price
            commission_sale_backup.quantity = commission_sale.quantity
            commission_sale_backup.uncomplete_quantity = commission_sale.uncomplete_quantity
            commission_sale_backup.status = commission_sale.status
            commission_sale_backup.created_datetime = commission_sale.created_datetime
            commission_sale_backup.modified_datetime = commission_sale.modified_datetime
            commission_sale_backup.save()
            if commission_sale.status in [1,2]:
                user_product = UserProduct.objects.get(user=commission_sale.user,product=commission_sale.product,trade_type=2)
                user_product.can_pickup_quantity += int(commission_sale.uncomplete_quantity)
                user_product.total_sale_quantity -= int(commission_sale.uncomplete_quantity)
                user_product.total += int(commission_sale.uncomplete_quantity) * float(user_product.overage_unit_price)
                user_product.save()
            commission_sale.delete()
        all_order = ProductOrder.objects.filter(status=1)
        for order in all_order:
            order.effective = False
            order.save()
        print u'marker off'
    except:
        traceback.print_exc()
    finally:
        system_config = SystemConfig.objects.first()
        system_config.is_open = False
        system_config.save()
        
def do_truncate_database():
    try:
        all_buy_commission = CommissionBuy.objects.all()
        all_buy_commission.delete()
        all_sale_commission = CommissionSale.objects.all()
        all_sale_commission.delete()
        all_trade_complete = TradeComplete.objects.all()
        all_trade_complete.delete()
        all_pickup_detail = PickupDetail.objects.all()
        all_pickup_detail.delete()
        all_pickup_list = PickupList.objects.all()
        all_pickup_list.delete()
#         all_user_balance = UserBalance.objects.all()
#         for user_balance in all_user_balance:
#             user_balance.balance=0
#             user_balance.locked=0
#             user_balance.save()
        all_user_product = UserProduct.objects.all()
        all_user_product.delete()
        all_user_money_change = UserMoneyChange.objects.all()
        all_user_money_change.delete()
        all_user_daily_report = UserAssetDailyReport.objects.all()
        all_user_daily_report.delete()
        confirm_deal = ConfirmDeal.objects.all()
        confirm_deal.delete()
        all_stock_ticker = StockTicker.objects.all()
        all_stock_ticker.delete()
        print u"truncate success"
    except: 
        traceback.print_exc()
        
