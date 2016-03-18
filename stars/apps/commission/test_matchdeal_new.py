# -*- coding: utf-8 -*-s
import datetime
import json
import md5
import random
import string
from time import sleep
import traceback

import django
django.setup()
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import IntegrityError
from django.db.models import F
from django.db.models import Max
from django.db.models import Min, Sum, Max
from django.db.models.lookups import IsNull
from django.db.models.query_utils import Q
from django_redis import get_redis_connection
from oscar.core.loading import get_model



from stars.apps.commission.views import object_to_dict
 
CommissionSale = get_model('commission', 'CommissionSale')
CommissionBuy = get_model('commission', 'CommissionBuy')
CommissionBuyBackup = get_model('commission', 'CommissionBuyBackup')
TradeComplete = get_model('commission', 'TradeComplete')
StockTicker = get_model('commission', 'StockTicker')
Product = get_model('catalogue', 'product')
UserProduct = get_model('commission', 'UserProduct') 
Category = get_model('catalogue', 'Category')
UserBalance = get_model('commission', 'UserBalance') 
ConfirmDeal = get_model('commission', 'ConfirmDeal') 
UserAssetDailyReport = get_model('commission', 'UserAssetDailyReport') 
UserMoneyChange = get_model('commission', 'UserMoneyChange') 
user=User.objects.get(id=11)
#按照时间排序获取所有未处理未成交买单
# all_buy_commission = CommissionBuy.objects.filter(flag=False).exclude(status__in=[3,4]).order_by('created_datetime')
# print all_buy_commission
#获得此产品所有未成交买单，按照价格类型时间排序
# commission_buy_list = CommissionBuy.objects.exclude(status__in=[3,4]).order_by('-unit_price')
# for c in commission_buy_list:
#     print c.unit_price
#测试+
# print 'vw'
# ub = UserBalance.objects.get(id=38)
# ub.balance -= 24
# print ub.balance
#测试queryset delete()
# cc = CommissionBuy.objects.all()
# print cc
# cc.delete()
# print cc
# user.delete(user[0])
# print user
#测试时间减法
# a = datetime.datetime.now()
# sleep(0.1)
# b = datetime.datetime.now()
# print b - a
#测试sql
# all_buy_commission = CommissionBuy.objects.filter(flag=False).exclude(status__in=[3,4]).order_by('created_datetime')
# print all_buy_commission
# from django.db import connection
# print connection.queries
#测试django-redis
# cache.set('lisongwei',2)
# cache.set('lisongwei',2)
# ss = cache.get("lisongwei")
con = get_redis_connection("default")
# con.zadd('myset',1,'buy:2:1:1')
# print con.zrevrange('myset',0,-1)[0]
#获取ID
# print con.zrevrange('buyset',0,0)[0].split(":")[3]
#获取买单信息
# con.set("g46",'{"ni":4}')
# print json.loads(con.get("buy:5392"))['unit_price']
# all_commission_sale_id = con.zrangebyscore('myset','(0','6.4')
# for commission_sale_id in all_commission_sale_id:
#     print commission_sale_id.split(":")
#测试修改redis数据
# ss = json.loads(con.get("buy:1"))
# print ss
# ss['product'] = 15
# print ss
# con.set("buy:1",json.dumps(ss))
#测试json
# ss = {"id":1}
# print json.dumps(ss)
#测试datetime to json
# now = datetime.datetime.now()
# print now
# nowstr = now.strftime('%Y-%m-%d %H:%M:%S')
# ss = {"id":nowstr}
# print json.dumps(ss)
#测试获取最高买价
# max_key = con.zrevrange("myset",0,0)[0]
# print max_key
# max_score = con.zscore("myset",max_key)
# print max_score
#测试redis空集合
# es = con.zrange("my",0,0)[0]
# print es
#测试dict
# ss = {}
# ss['key']=5
# print ss
# print json.dumps(ss)
#测试最大ID
# while True:
#     max_umc_id = int(con.get('umc:max')) + 1
#     print max_umc_id
#     umc_max = con.get("umc:%d"%max_umc_id)
#     if umc_max:
#         con.set('umc:max',max_umc_id)
#     else:
#         break
# print umc_max
#测试while
# i = 1
# while True:
#     print i
#     i += 1
#     if i > 5:
#         break
#测试json加减
# ub = {"price":12}
# ub['price'] += 13
# print ub
#测试添加行情
# st = StockTicker.objects.get(id=911)
# tt = object_to_dict(st)
# tt['created_date'] = tt['created_date'].strftime('%Y-%m-%d')
# tt['created_datetime'] = tt['created_datetime'].strftime('%Y-%m-%d %H:%M:%S')
# tt['modified_datetime'] = tt['modified_datetime'].strftime('%Y-%m-%d %H:%M:%S')
# print json.dumps(tt)
# con.set("st:1",json.dumps(tt))
#测试获取行情
# tt = json.loads(con.get("st:1"))
# print tt
# if not tt['opening_price']:
#     print 'sdfsdf'
# print tt['strike_price']
# tt['strike_price'] = str(98.8)
# con.set("st:1",json.dumps(tt))
# print float(98.8) == tt['strike_price']

# con.set('total_num',"45万")
# print con.get('total_num')
#测试生成redis行情
# stocke = StockTicker.objects.get(id=916)
# vv = object_to_dict(stocke)
# vv['created_date'] = vv['created_date'].strftime('%Y-%m-%d')
# vv['created_datetime'] = vv['created_datetime'].strftime('%Y-%m-%d %H:%M:%S')
# vv['modified_datetime'] = vv['modified_datetime'].strftime('%Y-%m-%d %H:%M:%S')
# ss = json.dumps(vv)
# print vv
# print ss
# st_key = "st:%d"%stocke.product_id
# con.set(st_key,ss)
#测试生成redis余额
# one_user_balance = UserBalance.objects.get(id=38)
# user_balance = object_to_dict(one_user_balance)
# print user_balance
# user_balance['created_date'] = user_balance['created_date'].strftime('%Y-%m-%d')
# user_balance['created_time'] = user_balance['created_time'].strftime('%H:%M:%S')
# user_balance['modified_date'] = user_balance['modified_date'].strftime('%Y-%m-%d')
# user_balance['modified_time'] = user_balance['modified_time'].strftime('%H:%M:%S')
# user_balance = json.dumps(user_balance)
# print user_balance
#测试生成redis日报
# one_daily_report  = UserAssetDailyReport.objects.get(id=1063)
# daily_report = object_to_dict(one_daily_report)
# print daily_report
# daily_report['target_date'] = daily_report['target_date'].strftime('%Y-%m-%d')
# daily_report['created_date'] = daily_report['created_date'].strftime('%Y-%m-%d')
# daily_report['created_time'] = daily_report['created_time'].strftime('%H:%M:%S')
# daily_report['modified_date'] = daily_report['modified_date'].strftime('%Y-%m-%d')
# daily_report['modified_time'] = daily_report['modified_time'].strftime('%H:%M:%S')
# daily_report = json.dumps(daily_report)
# print daily_report
#测试生成redis成交信息
# one_trade_complete = TradeComplete.objects.get()
# trade_complete = object_to_dict(one_trade_complete)
# print trade_complete
# trade_complete['created_date'] = trade_complete['created_date'].strftime('%Y-%m-%d')
# trade_complete['created_datetime'] = trade_complete['created_datetime'].strftime('%Y-%m-%d %H:%M:%S')
# trade_complete['modified_datetime'] = trade_complete['modified_datetime'].strftime('%Y-%m-%d %H:%M:%S')
# trade_complete = json.dumps(trade_complete)
# print trade_complete
# print one_trade_complete.commission_buy_user_id_id
#测试生成redis用户资产变化
one_user_money_change = UserMoneyChange.objects.get(id=1)
user_money_chanage = object_to_dict(one_user_money_change)
print user_money_chanage
user_money_chanage['created_date'] = user_money_chanage['created_date'].strftime('%Y-%m-%d')
user_money_chanage['created_time'] = user_money_chanage['created_time'].strftime('%H:%M:%S')
user_money_chanage['modified_date'] = user_money_chanage['modified_date'].strftime('%Y-%m-%d')
user_money_chanage['modified_time'] = user_money_chanage['modified_time'].strftime('%H:%M:%S')
user_money_chanage = json.dumps(user_money_chanage)
print user_money_chanage






