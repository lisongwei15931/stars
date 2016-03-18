#coding=utf-8
import os
import sys
import threading
from time import sleep
import traceback

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

def match_deal_sale():
    system_config = SystemConfig.objects.first()
    if system_config.is_open and system_config.auto_open:
        #按照时间排序获取所有未处理未成交卖单
        all_sale_commission = CommissionSale.objects.filter(flag=False).exclude(status__in=[3,4]).order_by('created_datetime')
        if all_sale_commission:
            for sale_commission in all_sale_commission:
                deal_product=sale_commission.product
                
                #获得此产品所有未成交卖单，按照价格类型时间排序
                commission_sale_list = CommissionSale.objects.filter(product=deal_product).exclude(status__in=[3,4]).order_by('unit_price','c_type','created_datetime')
                
                for commission_sale in commission_sale_list:
                    #获得最低卖价
                    min_price = commission_sale.unit_price
                    #获取售价高于最低卖价的所有未成交买单按照价格时间排序
                    commission_buy_list = CommissionBuy.objects.filter(product=deal_product,unit_price__gte=min_price).exclude(status__in=[3,4]).order_by('-unit_price','created_datetime')
                    #若有没有相应买单则所有卖单设置为处理过
                    if not commission_buy_list:
                        for commission_sale in all_sale_commission:
                            commission_sale.flag = True
                            commission_sale.save()
                        break
                    else:
                        #确定出售数量
                        if commission_sale.status == 1:
                            sale_quantity = commission_sale.quantity
                        elif commission_sale.status == 2:
                            sale_quantity = commission_sale.uncomplete_quantity
                        for commission_buy in commission_buy_list:
                            #确定购买数量
                            if commission_buy.status == 1:
                                buy_quantity = commission_buy.quantity
                            elif commission_buy.status == 2:
                                buy_quantity = commission_buy.uncomplete_quantity
                            #确定交易数量
                            if sale_quantity > buy_quantity:
                                deal_quantity = buy_quantity
                                sale_quantity -= buy_quantity
                                try:
                                    confirm_deal(deal_quantity,commission_buy,commission_sale)
                                except:
                                    traceback.print_exc()
                                    break
                            else:
                                deal_quantity = sale_quantity
                                try:
                                    confirm_deal(deal_quantity,commission_buy,commission_sale)
                                except:
                                    traceback.print_exc()
                                    break
                                break


def confirm_deal(deal_quantity,commission_buy,commission_sale):
    confirm_deal = ConfirmDeal()
    confirm_deal.commission_buy_id = commission_buy.id
    confirm_deal.commission_sale_id = commission_sale.id
    try:
        confirm_deal.save()
        receive_deal.delay(deal_quantity,commission_buy,commission_sale,"")
    except:
        raise                    
                    
    
class MatchDealSale(threading.Thread):
    def run(self):
        try:
            while True:
                sleep(0.2)
                match_deal_sale()
        except:
            traceback.print_exc()
            sleep(2)
            self.run()
                
t1 = MatchDealSale()
t1.start()
