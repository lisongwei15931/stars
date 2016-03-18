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
from stars.apps.commission.tasks import new_trade_complete_task




CommissionBuy = get_model('commission', 'CommissionBuy')
CommissionSale = get_model('commission', 'CommissionSale')
SystemConfig = get_model('commission', 'SystemConfig')
def match_deal():
    system_config = SystemConfig.objects.first()
    if system_config.is_open and system_config.auto_open:
        #按照时间排序获取所有未成交买单
        all_buy_commission = CommissionBuy.objects.exclude(status__in=[3,4]).order_by('created_datetime')
        if all_buy_commission:
            for buy_commission in all_buy_commission:
                deal_product=buy_commission.product
                #获得此产品所有未成交买单，按照价格类型时间排序
                #commission_buy_list = CommissionBuy.objects.filter(product=deal_product).exclude(status__in=[3,4]).order_by('c_type','quantity','created_datetime')
                commission_buy_list = CommissionBuy.objects.filter(product=deal_product).exclude(status__in=[3,4]).order_by('-unit_price','c_type','created_datetime')
                for commission_buy in commission_buy_list:
                    #确定需要交易数量
                    if commission_buy.status == 1:
                        uncomplete_quantity = commission_buy.quantity
                    elif commission_buy.status == 2:
                        uncomplete_quantity = commission_buy.uncomplete_quantity
                    #获取此产品所有售价低于买价的未成交埋单按照价格排序
                    commission_sale_list = CommissionSale.objects.filter(product=deal_product,unit_price__lte=commission_buy.unit_price).exclude(status__in=[3,4]).order_by('unit_price','created_datetime')
                    #如果当前没有卖单不继续循环，进行下一个商品（避免循环中突然出现买单导致交易顺序错误问题）
                    if not commission_sale_list:
                        break
                    #匹配成功开始交易逻辑
                    if commission_sale_list:
                        for commission_sale in commission_sale_list:
                            #确定可出售数量
                            if commission_sale.status == 1:
                                sale_quantity = commission_sale.quantity
                            elif commission_sale.status == 2:
                                sale_quantity = commission_sale.uncomplete_quantity
                            #如果买量大于卖量结束卖单，买单部分成交并继续
                            if uncomplete_quantity > sale_quantity:
                                uncomplete_quantity = uncomplete_quantity - sale_quantity
                                commission_sale.uncomplete_quantity = 0
                                commission_sale.status = 3
                                commission_sale.save()
                                commission_buy.uncomplete_quantity = uncomplete_quantity
                                commission_buy.status = 2
                                commission_buy.save()
                                new_trade_complete_task(deal_product,commission_buy,commission_sale,
                                       commission_buy.user,commission_sale.user,commission_buy.c_type,commission_sale.unit_price,sale_quantity,commission_buy.quantity,"")
                            #如果买量小于卖量结束买单，卖单部分成交
                            elif uncomplete_quantity < sale_quantity:
                                if commission_sale.status == 1:
                                    commission_sale.uncomplete_quantity = commission_sale.quantity - uncomplete_quantity
                                elif commission_sale.status == 2:
                                    commission_sale.uncomplete_quantity = commission_sale.uncomplete_quantity - uncomplete_quantity
                                commission_sale.status = 2
                                commission_sale.save()
                                commission_buy.uncomplete_quantity = 0
                                commission_buy.status = 3
                                commission_buy.save()
                                new_trade_complete_task(deal_product,commission_buy,commission_sale,
                                       commission_buy.user,commission_sale.user,commission_buy.c_type,commission_sale.unit_price,uncomplete_quantity,commission_buy.quantity,"")
                                uncomplete_quantity = 0
                                break
                            #如果买量等于卖量，结束买单和卖单
                            elif uncomplete_quantity == sale_quantity:
                                commission_buy.uncomplete_quantity = 0
                                commission_buy.status = 3
                                commission_buy.save()
                                commission_sale.uncomplete_quantity = 0
                                commission_sale.status = 3
                                commission_sale.save()
                                new_trade_complete_task(deal_product,commission_buy,commission_sale,
                                       commission_buy.user,commission_sale.user,commission_buy.c_type,commission_sale.unit_price,uncomplete_quantity,commission_buy.quantity,"")
                                uncomplete_quantity = 0
                                break 
                        #如果所有卖单循环完毕还有未成交数量，买单设为部分成交
                        if uncomplete_quantity > 0 and uncomplete_quantity != commission_buy.quantity:
                            commission_buy.uncomplete_quantity = uncomplete_quantity
                            commission_buy.status = 2
                            commission_buy.save()
class MatchDeal(threading.Thread):
    def run(self):
        try:
            while True:
                sleep(0.5)
                with transaction.atomic():
                    match_deal()
        except:
            traceback.print_exc()
            sleep(2)
            self.run()
                
t1 = MatchDeal()
t1.start()
