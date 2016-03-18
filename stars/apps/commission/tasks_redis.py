# -*- coding: utf-8 -*-s
import os, sys
import traceback
import json
import datetime
import django
from django.db import transaction
from oscar.core.loading import get_model

from stars.celery import app


path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path[0:path.rfind('stars')])
os.environ['DJANGO_SETTINGS_MODULE'] = 'stars.settings'
django.setup()
# from stars.apps.commission.views import new_trade_complete
from django_redis import get_redis_connection


CommissionBuy = get_model('commission','CommissionBuy')
CommissionSale = get_model('commission','CommissionSale')

# @app.task()
# def receive_deal(deal_quantity,commission_buy,commission_sale):
#     try:
#         #判断买单卖单未完成数量是否大于交易数量
#         if commission_buy.uncomplete_quantity >= deal_quantity and commission_sale.uncomplete_quantity >= deal_quantity:
#             commission_buy.uncomplete_quantity -= deal_quantity
#             if commission_buy.uncomplete_quantity > 0:
#                 commission_buy.status = 2
#             else:
#                 commission_buy.status = 3
#                 commission_buy.flag = True
#             commission_buy.save()
#             commission_sale.uncomplete_quantity -= deal_quantity
#             if commission_sale.uncomplete_quantity > 0:
#                 commission_sale.status = 2
#             else:
#                 commission_sale.status = 3
#                 commission_sale.flag = True
#             commission_sale.save()
#             new_trade_complete(commission_buy,commission_sale,
#                                        commission_buy.user,commission_sale.user,commission_buy.c_type,commission_sale.unit_price,deal_quantity,commission_buy.quantity)
#     except:
#         traceback.print_exc()
    
@app.task()
def receive_buy(product_id):
    queue_key = u"buy%d"%product_id
    match_buy.apply_async((product_id,),queue=queue_key,routing_key=queue_key)
    
@app.task()
def receive_sale(product_id):
    queue_key = u"sale%d"%product_id
    match_sale.apply_async((product_id,),queue=queue_key,routing_key=queue_key)
    
@app.task()
def match_buy(product_id):
    con = get_redis_connection("default")
    zbuy_name = u"buyset%d"%product_id
    zsale_name = u"saleset%d"%product_id
    #获取买单队列里第一条买单id
    commission_buy_key = con.zrevrange(zbuy_name,0,0)[0]
    commission_buy_id = commission_buy_key.split(":")[3]
    #获取买单信息
    buy_key = u"buy:%d"%commission_buy_id
    commission_buy = json.loads(con.get(buy_key))
    price = commission_buy['unit_price']
    #确定购买数量
    if commission_buy['status'] == 1:
        buy_quantity = commission_buy['quantity']
    elif commission_buy['status'] == 2:
        buy_quantity = commission_buy['uncomplete_quantity']
    #获取价格低于买价的所有卖单ID
    all_commission_sale_id = con.zrangebyscore(zsale_name,'(0',float(price))
    for commission_sale_key in all_commission_sale_id:
        commission_sale_id = commission_sale_key.split(":")[3]
        sale_key =  u"sale:%d"%commission_sale_id
        #获取卖单信息
        commission_sale = json.loads(con.get(sale_key))
    #开始撮合
        #确定可出售数量
        if commission_sale['status'] == 1:
            sale_quantity = commission_sale['quantity']
        elif commission_sale['status'] == 2:
            sale_quantity = commission_sale['uncomplete_quantity']
        #确定交易数量
        if buy_quantity > sale_quantity:
            deal_quantity = sale_quantity
            buy_quantity -= sale_quantity
            #修改买单状态和未完成数量
            commission_buy['uncomplete_quantity'] -= deal_quantity
            commission_buy['status'] = 2
            #修改卖单状态和未完成数量，并在卖单序列里删除此卖单
            commission_sale['status'] = 3
            commission_sale['uncomplete_quantity'] = 0
            con.zrem(zsale_name,commission_sale_key)
            #完成集合里添加数据
            sale_complete_set_key = "complete:%d"%float(commission_sale['user'])
            con.sadd(sale_complete_set_key,sale_key)
            #未完成集合里删除数据
            sale_uncomplete_set_key = "uncomplete:%d"%float(commission_sale['user'])
            con.srem(sale_uncomplete_set_key,sale_key)
        elif buy_quantity == sale_quantity:
            deal_quantity = buy_quantity
            buy_quantity = 0
            #修改卖单状态和未完成数量，并在卖单序列里删除此卖单
            commission_sale['status'] = 3
            commission_sale['uncomplete_quantity'] = 0
            con.zrem(zsale_name,commission_sale_key)
            #修改买单状态和未完成数量，并在买单序列里删除此买单
            commission_buy['uncomplete_quantity'] = 0
            commission_buy['status'] = 3
            con.zrem(zbuy_name,commission_buy_key)
            #完成集合里添加数据
            buy_complete_set_key = "complete:%d"%float(commission_buy['user'])
            sale_complete_set_key = "complete:%d"%float(commission_sale['user'])
            con.sadd(buy_complete_set_key,buy_key)
            con.sadd(sale_complete_set_key,sale_key)
            #未完成集合里删除数据
            buy_uncomplete_set_key = "uncomplete:%d"%float(commission_buy['user'])
            sale_uncomplete_set_key = "uncomplete:%d"%float(commission_sale['user'])
            con.srem(buy_uncomplete_set_key,buy_key)
            con.srem(sale_uncomplete_set_key,sale_key)
            break
        else:
            deal_quantity = buy_quantity
            buy_quantity = 0 
            #修改买单状态和未完成数量，并在买单序列里删除此买单
            commission_buy['uncomplete_quantity'] = 0
            commission_buy['status'] = 3
            con.zrem(zbuy_name,commission_buy_key)
            #修改卖单状态和未完成数量
            commission_sale['status'] = 2
            commission_sale['uncomplete_quantity'] -= deal_quantity
            #完成集合里添加数据
            buy_complete_set_key = "complete:%d"%float(commission_buy['user'])
            con.sadd(buy_complete_set_key,buy_key)
            #未完成集合里删除数据
            buy_uncomplete_set_key = "uncomplete:%d"%float(commission_buy['user'])
            con.srem(buy_uncomplete_set_key,buy_key)
            break
        con.set(buy_key,json.dumps(commission_buy))
        con.set(sale_key,json.dumps(commission_sale))
        #生成成交表信息
        trade_key = "trade:%d:%d"%(commission_buy_id,commission_sale_id)
        total = "%.2f"%(float(deal_quantity)*float(commission_sale['unit_price']))
        now = datetime.datetime.now()
        nowstr = now.strftime('%Y-%m-%d %H:%M:%S')
        trade_value = {"product":product_id,"commission_buy_no":commission_buy_id,"commission_sale_no":commission_sale_id,
                       "commission_buy_user_id":commission_buy['user'],"commission_sale_user_id":commission_sale['user'],
                       "c_type":commission_buy['c_type'],"unit_price":commission_sale['unit_price'],
                       "quantity":deal_quantity,"total":total,
                       "commission_quantity":commission_buy['quantity'],"can_pickup_quantity":deal_quantity,
                       "created_datetime":nowstr
                       }
        con.set(trade_key,json.dumps(trade_value))
        buy_trade_set_key = "trade:%d"%float(commission_buy['user'])
        sale_trade_set_key = "trade:%d"%float(commission_sale['user'])
        con.sadd(buy_trade_set_key,trade_key)
        con.sadd(sale_trade_set_key,trade_key)
        #更新产品最高价和最低价
        high_price_key = "high:price:%d"%product_id
        low_price_key = "low:price:%d"%product_id
        high_price = con.get(high_price_key)
        low_price = con.get(low_price_key)
        if high_price < commission_sale['unit_price']:
            con.set(high_price_key,commission_sale['unit_price'])
        if low_price > commission_sale['unit_price']:
            con.set(low_price_key,commission_sale['unit_price'])
        #处理资金变化
        deal_money_change_redis(commission_buy['user'],commission_sale['user'],commission_buy['c_type'],commission_buy['unit_price'],commission_sale['unit_price'],
                                commission_buy['quantity'],commission_sale['quantity'],deal_quantity,product_id,commission_buy_id,commission_sale_id,trade_key)
        #更行行情
        trade_update_stock_ticker(trade_value)
        

@app.task()
def match_sale(product_id):
    con = get_redis_connection("default")
    zbuy_name = u"buyset%d"%product_id
    zsale_name = u"saleset%d"%product_id
    #获取卖单队列里第一条卖单id
    commission_sale_key = con.zrange(zsale_name,0,0)[0]
    commission_sale_id = commission_sale_key.split(":")[3]
    #获取卖单信息
    sale_key = u"sale:%d"%commission_sale_id
    commission_sale = json.loads(con.get(sale_key))
    price = commission_sale['unit_price']
    #确定出售数量
    if commission_sale['status'] == 1:
        sale_quantity = commission_sale['quantity']
    elif commission_sale['status'] == 2:
        sale_quantity = commission_sale['uncomplete_quantity']
    #获取价格高于卖价的所有买单ID
    all_commission_buy_id = con.zrangebyscore(zsale_name,float(price),99999999)
    for commission_buy_key in all_commission_buy_id:
        commission_buy_id = commission_buy_key.split(":")[3]
        buy_key =  u"buy:%d"%commission_buy_id
        #获取卖单信息
        commission_buy = json.loads(con.get(buy_key))
    #开始撮合
        #确定可购买数量
        if commission_buy['status'] == 1:
            buy_quantity = commission_sale['quantity']
        elif commission_buy['status'] == 2:
            buy_quantity = commission_sale['uncomplete_quantity']
        #确定交易数量
        if sale_quantity > buy_quantity:
            deal_quantity = buy_quantity
            sale_quantity -= buy_quantity
            #修改卖单状态和未完成数量
            commission_sale['uncomplete_quantity'] -= deal_quantity
            commission_sale['status'] = 2
            #修改买单状态和未完成数量，并在买单序列里删除此买单
            commission_buy['status'] = 3
            commission_buy['uncomplete_quantity'] = 0
            con.zrem(zbuy_name,commission_buy_key)
            #完成集合里添加数据
            buy_complete_set_key = "complete:%d"%float(commission_buy['user'])
            con.sadd(buy_complete_set_key,buy_key)
            #未完成集合里删除数据
            buy_uncomplete_set_key = "uncomplete:%d"%float(commission_buy['user'])
            con.sadd(buy_complete_set_key,buy_key)
        elif sale_quantity == buy_quantity:
            deal_quantity = sale_quantity
            sale_quantity = 0 
            #修改卖单状态和未完成数量，并在卖单序列里删除此卖单
            commission_sale['uncomplete_quantity'] = 0
            commission_sale['status'] = 3
            con.zrem(zsale_name,commission_sale_key)
            #修改买单状态和未完成数量,并在买单序列里删除此买单
            commission_buy['status'] = 3
            commission_buy['uncomplete_quantity'] = 0
            con.zrem(zbuy_name,commission_buy_key)
            #完成集合里添加数据
            buy_complete_set_key = "complete:%d"%float(commission_buy['user'])
            sale_complete_set_key = "complete:%d"%float(commission_sale['user'])
            con.sadd(buy_complete_set_key,buy_key)
            con.sadd(sale_complete_set_key,sale_key)
            #未完成集合里删除数据
            buy_uncomplete_set_key = "uncomplete:%d"%float(commission_buy['user'])
            sale_uncomplete_set_key = "uncomplete:%d"%float(commission_sale['user'])
            con.srem(buy_uncomplete_set_key,buy_key)
            con.srem(sale_uncomplete_set_key,sale_key)
            break
        else:
            deal_quantity = sale_quantity
            sale_quantity = 0 
            #修改卖单状态和未完成数量，并在卖单序列里删除此卖单
            commission_sale['uncomplete_quantity'] = 0
            commission_sale['status'] = 3
            con.zrem(zsale_name,commission_sale_key)
            #修改买单状态和未完成数量
            commission_buy['status'] = 2
            commission_buy['uncomplete_quantity'] -= deal_quantity
            #完成集合里添加数据
            sale_complete_set_key = "complete:%d"%float(commission_sale['user'])
            con.sadd(sale_complete_set_key,sale_key)
            #未完成集合里删除数据
            sale_uncomplete_set_key = "uncomplete:%d"%float(commission_sale['user'])
            con.srem(sale_uncomplete_set_key,sale_key)
            break
        con.set(buy_key,json.dumps(commission_buy))
        con.set(sale_key,json.dumps(commission_sale))
        #生成成交表信息
        trade_key = "trade:%d:%d"%(commission_buy_id,commission_sale_id)
        total = "%.2f"%(float(deal_quantity)*float(commission_sale['unit_price']))
        now = datetime.datetime.now()
        nowstr = now.strftime('%Y-%m-%d %H:%M:%S')
        trade_value = {"product":product_id,"commission_buy_no":commission_buy_id,"commission_sale_no":commission_sale_id,
                       "commission_buy_user_id":commission_buy['user'],"commission_sale_user_id":commission_sale['user'],
                       "c_type":commission_buy['c_type'],"unit_price":commission_sale['unit_price'],
                       "quantity":deal_quantity,"total":total,
                       "commission_quantity":commission_buy['quantity'],"can_pickup_quantity":deal_quantity,
                       "created_datetime":nowstr
                       }
        con.set(trade_key,json.dumps(trade_value))
        buy_trade_set_key = "trade:%d"%float(commission_buy['user'])
        sale_trade_set_key = "trade:%d"%float(commission_sale['user'])
        con.sadd(buy_trade_set_key,trade_key)
        con.sadd(sale_trade_set_key,trade_key)
        #更新产品最高价和最低价
        high_price_key = "high:price:%d"%product_id
        low_price_key = "low:price:%d"%product_id
        high_price = con.get(high_price_key)
        low_price = con.get(low_price_key)
        if high_price < commission_sale['unit_price']:
            con.set(high_price_key,commission_sale['unit_price'])
        if low_price > commission_sale['unit_price']:
            con.set(low_price_key,commission_sale['unit_price'])
        #处理资金变化
        deal_money_change_redis(commission_buy['user'],commission_sale['user'],commission_buy['c_type'],commission_buy['unit_price'],commission_sale['unit_price'],
                                commission_buy['quantity'],commission_sale['quantity'],deal_quantity,product_id,commission_buy_id,commission_sale_id,trade_key)
        #更行行情
        trade_update_stock_ticker(trade_value)
        
        
        
    
    
