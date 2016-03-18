#coding=utf-8
import os
import sys
import threading
from time import sleep
import traceback
import datetime
import django
from django.db import transaction
from oscar.core.loading import get_model

path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path[0:path.rfind('stars')])
os.environ['DJANGO_SETTINGS_MODULE'] = 'stars.settings'

django.setup()
from stars.apps.commission.tasks import receive_deal



CommissionBuy = get_model('commission', 'CommissionBuy')
CommissionSale = get_model('commission', 'CommissionSale')
SystemConfig = get_model('commission', 'SystemConfig')
ConfirmDeal = get_model('commission', 'ConfirmDeal')

def match_deal_buy():
    system_config = SystemConfig.objects.first()
    if system_config.is_open and system_config.auto_open:
        try:
            with transaction.atomic():
                #按照时间排序获取所有未处理未成交买单
                a = datetime.datetime.now()
                all_buy_commission = CommissionBuy.objects.filter(flag=False).exclude(status__in=[3,4]).order_by('created_datetime')
                if all_buy_commission:
                    for buy_commission in all_buy_commission:
                        deal_product=buy_commission.product
                        b = datetime.datetime.now()
                        print '确定撮合商品',b-a
                        #获得此产品所有未成交买单，按照价格类型时间排序
                        commission_buy_list = CommissionBuy.objects.filter(product=deal_product).exclude(status__in=[3,4]).order_by('-unit_price','c_type','created_datetime')
                        c = datetime.datetime.now()
                        print '获得未成交买单',c-b
                        for commission_buy in commission_buy_list:
                            #获得最高买价
                            max_price = commission_buy.unit_price
                            #获取售价低于最高买价的所有未成交卖单按照价格时间排序
                            commission_sale_list = CommissionSale.objects.filter(product=deal_product,unit_price__lte=max_price).exclude(status__in=[3,4]).order_by('unit_price','created_datetime')
                            d = datetime.datetime.now()
                            print '获取所有未成交卖单',d-c
                            if not commission_sale_list:
                                for commission_buy in commission_buy_list:
                                    commission_buy.flag = True
                                    commission_buy.save()
                                break
                            else:
                                #确定购买数量
                                if commission_buy.status == 1:
                                    buy_quantity = commission_buy.quantity
                                elif commission_buy.status == 2:
                                    buy_quantity = commission_buy.uncomplete_quantity
                                for commission_sale in commission_sale_list:
                                    #确定可出售数量
                                    if commission_sale.status == 1:
                                        sale_quantity = commission_sale.quantity
                                    elif commission_sale.status == 2:
                                        sale_quantity = commission_sale.uncomplete_quantity
                                    #确定交易数量
                                    if buy_quantity > sale_quantity:
                                        deal_quantity = sale_quantity
                                        buy_quantity -= sale_quantity
                                        confirm_deal(deal_quantity,commission_buy.commission_no,commission_sale.commission_no)
                                    else:
                                        deal_quantity = buy_quantity
                                        confirm_deal(deal_quantity,commission_buy.commission_no,commission_sale.commission_no)
                                        break
                            from django.db import connection
                            for sql in connection.queries:
                                print sql['sql'],';'
        except:
            traceback.print_exc()
                    
@transaction.atomic()                    
def confirm_deal(deal_quantity,commission_buy_id,commission_sale_id):
    print '确认'
    e = datetime.datetime.now()
    confirm_deal = ConfirmDeal()
    confirm_deal.commission_buy_id = commission_buy_id
    confirm_deal.commission_sale_id = commission_sale_id
    try:
        confirm_deal.save()
        f = datetime.datetime.now()
        print '确认交易',f-e
        receive_deal(deal_quantity,commission_buy_id,commission_sale_id,"")
        from django.db import connection
        for sql in connection.queries:
            print sql['sql'],';'
    except:
        print 'err'
    
class MatchDealBuy(threading.Thread):
    def run(self):
        try:
            match_deal_buy()
        except:
            traceback.print_exc()
            sleep(2)
            self.run()
                
t1 = MatchDealBuy()
t1.start()
