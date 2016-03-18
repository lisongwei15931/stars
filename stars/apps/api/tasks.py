# -*- coding: utf-8 -*-s

import sys
import time
import datetime
import random
import urllib, urllib2
import json
import thread
from optparse                   import OptionParser
from celery                     import Celery


#BASE_URL = "http://ltbh365.com/"
BASE_URL = "http://192.168.1.133:8000/"
API_URL = "%sapi" % BASE_URL

USER_LIST = ["user_001", "user_002", "user_003", "user_004", "user_005",
    "user_006", "user_007", "user_008", "user_009", "user_010", "user_011",
    "user_012", "user_013", "user_014", "user_015", "user_016", "user_017",
    "user_018", "user_019", "user_020"]

USER_LIST = ["user_20000"]

PASSWORD = "111111"

SALE_ACCOUNT = "timdoct"
SALE_PASSWORD = "198243"

TOKENS = {}
PRODUCT_IDS = []
PRODUCT_DATA = {}
USER_PRODUCT = {}

REGISTER_USER_ID_START = 1

celery = Celery('tasks', broker='redis://localhost:6379/1')

def main_reigster(prefix, count):
    start = time.time()
    print "register %d users start......"% count

    global REGISTER_USER_ID_START

    for item in range(16533, count):
        start_item = time.time()
        username = "%s_%d" % (prefix, REGISTER_USER_ID_START + item)
        password = PASSWORD
        mobile_phone = random.choice(['139','188','185','136','158','151'])+"".join(random.choice("0123456789") for i in range(8))
        email = "%s@ltbh365.com" % username

        msg = register(username, password, mobile_phone, email, item)
        end_item = time.time()

        print "%d: register %s: %s, speed %.03f seconds" % (item, username, msg, (end_item - start_item))

    end = time.time()
    print "随机注册 end, run time is %.03f seconds ......"% ((end-start))

def register(username, password, mobile_phone, email, intloop):
    try:
        params = {'username': username, "password":password, "mobile_phone":mobile_phone, "email":email}
        post_data = urllib.urlencode(params);
        result = json.loads(get_post_response("%s/register/"%API_URL, post_data))
        return result.get("msg", "")
    except Exception, e:
        print e

    return "error"

@celery.task
def main():
    #----------- login ----------------------
    start = time.time()
    print "login %d users start......"% len(USER_LIST)

    # 商家用户登陆
    try:
        login(SALE_ACCOUNT, SALE_PASSWORD)
    except Exception,e:
        print e

    # 普通用户登陆
    for item in USER_LIST:
        try:
            if login(item, PASSWORD):
                pass
                #recharge(item, 1000)
        except Exception,e:
            print e

    end = time.time()
    print "login %d users end, run time is %.03f seconds ......"% (len(USER_LIST), (end-start))

    #----------- 获取商品ID & 商品信息 ----------------------
    start = time.time()
    print "获取商品ID & 商品信息 start......"

    p_ids = get_all_product_ids()
    if not p_ids:
        print "获取商品列表为空"
        return

    #p_ids = p_ids[10:]
    # 241 绿酷润滑油
    #p_ids = [p_ids[11]]
    p_ids = ['151']

    for item in p_ids:
        get_a_product_info(item)

    end = time.time()
    print "获取商品ID & 商品信息 end, run time is %.03f seconds ......"% ((end-start))

    #----------- 随机购买 ----------------------
    start = time.time()
    print "随机购买 start......"

    for item in range(1, 10000):
        random_user = random.choice(USER_LIST)
        random_pro_id = str(random.choice(p_ids))
        if not PRODUCT_DATA.has_key(random_pro_id):continue
        random_pro_data = PRODUCT_DATA[random_pro_id]
        #获取用户持有数据
        get_user_product(random_user, random_pro_id)

        #用户进货权
        r_quote = 0

        #用户持有量
        r_user_ower_num = 0

        if USER_PRODUCT.has_key(random_user) and USER_PRODUCT[random_user].has_key(random_pro_id):
            r_quote = USER_PRODUCT[random_user][random_pro_id]['quote_quantity']
            r_user_ower_num = USER_PRODUCT[random_user][random_pro_id]['quantity']

        #商品最大购买量
        r_max_num = random_pro_data['max_buy_num']
        #单次最大购买量
        r_once_max_num = random_pro_data['once_max_num']

        #随机购买量
        random_buy_quantity_0 = random.randrange(1, r_once_max_num)
        if r_max_num - r_user_ower_num > r_once_max_num:
            random_buy_quantity_0 = random.randrange(1, (r_max_num - r_user_ower_num))

        #昨收价
        r_closing_price = random_pro_data['closing_price']
        #开盘价
        r_opening_price = random_pro_data['opening_price']
        #最新价
        r_strike_price = random_pro_data['strike_price']
        #价格涨幅区间
        r_up_price = random_pro_data['ud_up_range']
        r_down_range = random_pro_data['ud_down_range']

        if r_opening_price > 0:
            r_min_price = float(r_opening_price) - r_down_range
            r_max_price = float(r_opening_price) + r_up_price
        else:
            r_min_price = float(r_closing_price) - r_down_range
            r_max_price = float(r_closing_price) + r_up_price

        r_random_buy_price = randrange_float(r_min_price, r_max_price, 0.01)
        #demo
        r_random_buy_price = r_max_price

        #用户余额
        r_balance = get_balance(random_user)
        if r_balance < 10:
            r_balance = recharge(random_user, 1000)
        r_max_can_buy = int(r_balance / r_random_buy_price)

        if r_max_can_buy > 0:
            r_random_buy_quantity = random.randrange(0, r_max_can_buy)
        else:
            r_random_buy_quantity = 0

        #随机卖价格和卖量
        # if r_opening_price > 0:
        #     r_min_sell_price = r_opening_price
        # else:
        if random.choice(range(1, 10)) > 2 and r_opening_price > 0:
            r_random_sell_price = randrange_float(r_opening_price, r_max_price, 0.01)
        elif r_opening_price == 0 :
            r_random_sell_price = randrange_float(r_closing_price, r_max_price, 0.01)
        else:
            r_random_sell_price = randrange_float(r_min_price, r_max_price, 0.01)

        #demo
        r_random_sell_price = r_min_price

        #print "min:%s, max:%s, buy:%s, sell:%s, close:%s, open:%s"%(
        #    str(r_min_price), str(r_max_price), str(r_random_buy_price), str(r_random_sell_price),
        #    str(r_closing_price), str(r_opening_price))

        r_random_sell_quantity = 10#random.randrange(1, r_random_buy_quantity + 30)

        if r_random_buy_quantity > 0:
            # 购买
            buy(random_user, random_pro_id, random_pro_data['product_name'], 1, 1, r_random_buy_price, 2, item)
            # 进货
            #buy(random_user, random_pro_id, random_pro_data['product_name'], 2, r_random_buy_quantity, r_random_buy_price, 2, item)

        # 卖
        sell(SALE_ACCOUNT, random_pro_id, random_pro_data['product_name'], 1, r_random_sell_quantity, r_random_sell_price, 2, item)

        #更新产品行情信息
        get_a_product_info(random_pro_id)
        #更新用户持有信息
        get_user_product(random_user, random_pro_id)

        #break;

    end = time.time()
    print "随机购买 end, run time is %.03f seconds ......"% ((end-start))


def login(username, pwd):
    try:
        global TOKENS

        params = {'username': username, "password":pwd}
        post_data = urllib.urlencode(params);
        result = json.loads(get_post_response("%s/auth/"%API_URL, post_data))
        if result.has_key('token'):
            TOKENS[username] = result['token']

            return True

    except Exception,e:
        print e

    return False

def recharge(username, amount):
    try:
        if not TOKENS.has_key(username): print "充值失败, 没有token"

        params = {'amount': amount}
        post_data = urllib.urlencode(params);
        result = json.loads(get_post_response("%s/recharge/"%API_URL, post_data, TOKENS[username]))

        print "%s balance: %d"%(username, result.get("balance", 0))

        return result.get("balance", 0)

    except Exception,e:
        print e

    return 0

def buy(username, product_id, product_name, c_type, quantity, price, status, intloop=0):
    try:
        if not TOKENS.has_key(username): print "购买失败, 没有token"

        params = {'product': product_id, 'c_type': c_type, 'quantity': quantity, 'price':price}
        post_data = urllib.urlencode(params);
        result = json.loads(get_post_response("%s/buy/"%API_URL, post_data, TOKENS[username]))

        if result.get("errcode") == 0:
            if c_type == 1:
                print u"%d  %s: 购买 %s, 数量 %s, 价格 %s, 结果 %s"%(intloop, username, product_name, quantity, price, result.get("msg", ""))
            elif c_type == 2:
                print u"%d  %s: 进货 %s, 数量 %s, 价格 %s, 结果 %s"%(intloop, username, product_name, quantity, price, result.get("msg", ""))
        else:
            print result.get("msg", "")

    except Exception,e:
        raise
        print e

def sell(username, product_id, product_name, c_type, quantity, price, status, intloop=0):
    try:
        if not TOKENS.has_key(username): print "购买失败, 没有token"

        params = {'product': product_id, 'c_type': c_type, 'quantity': quantity, 'price':price}
        post_data = urllib.urlencode(params);
        result = json.loads(get_post_response("%s/factory/sell/"%API_URL, post_data, TOKENS[username]))

        if result.get("errcode") == 0:
            if c_type == 1:
                print u"%d  %s: 购买 %s, 数量 %s, 价格 %s, 结果 %s"%(intloop, username, product_name, quantity, price, result.get("msg", ""))
            elif c_type == 2:
                print u"%d  %s: 进货 %s, 数量 %s, 价格 %s, 结果 %s"%(intloop, username, product_name, quantity, price, result.get("msg", ""))
        else:
            print result.get("msg", "")

    except Exception,e:
        raise
        print e

def get_balance(username):
    try:
        if not TOKENS.has_key(username): print "获取余额失败, 没有token"

        result = json.loads(get_response("%s/recharge/"%API_URL, TOKENS[username]))

        return result.get("balance", 0)

    except Exception,e:
        print e

    return 0

def get_user_product(username, product_id):
    try:
        if not TOKENS.has_key(username): print "获取持有失败, 没有token"
        global USER_PRODUCT

        params = {'product_id': product_id}
        post_data = urllib.urlencode(params);
        result = json.loads(get_post_response("%s/user/product/"%API_URL, post_data, TOKENS[TOKENS.keys()[0]]))

        data = result.get("data", None)
        if data:
            if not USER_PRODUCT.has_key(username):
                USER_PRODUCT[username] = {}

            USER_PRODUCT[username]= data
        else:
            print u'%s'%result.get("msg", "")

    except Exception,e:
        print e

def get_a_product_info(product_id):
    try:
        if not TOKENS: print "获取商品信息失败, 没有token"
        global PRODUCT_DATA

        params = {'product_id': product_id}
        post_data = urllib.urlencode(params);
        result = json.loads(get_post_response("%s/product/stock/"%API_URL, post_data, TOKENS[TOKENS.keys()[0]]))

        data = result.get("data", None)
        if data:
            PRODUCT_DATA[str(product_id)] = data

    except Exception,e:
        print e


def get_all_product_ids():
    try:
        if not TOKENS: print "失败, 没有token"

        params = {}
        post_data = urllib.urlencode(params);
        result = json.loads(get_post_response("%s/product/ids/"%API_URL, post_data, TOKENS[TOKENS.keys()[0]]))

        global PRODUCT_IDS
        PRODUCT_IDS = result['data']

        return PRODUCT_IDS

    except Exception,e:
        print e

    return []

def clear():
    try:
        if not TOKENS: print "失败, 没有token"

        params = {}
        post_data = urllib.urlencode(params);
        result = get_post_response("%s/tradingcenter/truncate-database/"%BASE_URL, post_data, TOKENS[TOKENS.keys()[0]])

        print result

    except Exception,e:
        print e


def get_post_response(url, post_data=None, token=None):
    try:
        req = urllib2.Request(url, post_data);
        req.add_header('User-Agent', "firefox");
        req.add_header('Content-Type', 'application/x-www-form-urlencoded');
        req.add_header('Cache-Control', 'no-cache');
        req.add_header('Accept', '*/*');
        req.add_header('Connection', 'Keep-Alive');
        req.add_header('Authorization', "JWT %s" %token)
        resp = urllib2.urlopen(req);

        ret = resp.read()

        return ret
    except Exception, e:
        print e

    return "{}"

def get_response(url, token=None):
    try:
        req = urllib2.Request(url);
        req.add_header('User-Agent', "firefox");
        req.add_header('Content-Type', 'application/x-www-form-urlencoded');
        req.add_header('Cache-Control', 'no-cache');
        req.add_header('Accept', '*/*');
        req.add_header('Connection', 'Keep-Alive');
        req.add_header('Authorization', "JWT %s" %token)
        resp = urllib2.urlopen(req);

        ret = resp.read()

        return ret
    except Exception, e:
        print e

    return "{}"

def randrange_float(start, stop, step):
    return random.randint(0, int((stop - start) / step)) * step + start



#-------------------------------------------------------------------
# parse_command_line_options -
#-------------------------------------------------------------------

def parse_command_line_options():
    usage = "usage: test.py [options]\n-i: "
    op = OptionParser(usage=usage)
    op.add_option('-m', '--main', help='main', action='store_true')
    op.add_option('-t', '--registers', help='registers', action='store_true')
    op.add_option('-r', '--register', help='register', action='store_true')
    op.add_option('-p', '--pids', help='pids', action='store_true')
    return op

if __name__ == "__main__":                      # if is the current module
    main()
    #register("timdoct", "198243", "13877765555", "timdoct@example.com", 1)
#     op = parse_command_line_options()
#     options, args = op.parse_args(sys.argv[1:])
# 
#     if options.main:
#         try:
#             for item in range(0, int(args[0])):
#                 main.delay()
#         except:
#             raise
# 
#     if options.registers:
#         main_reigster("user", 20000)
# 
#     if options.register:
#         register("user_20000", "111111", "13877765556", "user_20000@example.com", 1)
# 
#     if options.pids:
#         login("user_001", "111111")
#         get_all_product_ids()
#         print PRODUCT_IDS[:len(PRODUCT_IDS)-10]
