# -*- coding: utf-8 -*-s

import datetime
import hashlib
import os
import random
import re
import time
import traceback

import requests
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.files import File
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.shortcuts import render
from django.utils.timezone import now
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from oscar.core.loading import get_model
from stars.apps.accounts.forms import local_mobile_phone_validator
from stars.apps.accounts.models import UserProfile, Captcha
from stars.apps.ad.models import RollingAd
from stars.apps.address.models import ReceivingAddress
from stars.apps.api.models import App
from stars.apps.commission.models import (StockProductConfig, UserProduct, UserBalance, UserAssetDailyReport, StockTicker)
from stars.apps.commission.views import commission_buy_test, commission_sale_test, factory_commission_sale
from stars.apps.commission.views import new_commission_buy, new_commissiton_sale
from stars.apps.customer.finance.ab.views import RechargeView
from stars.apps.public.send_message import send_message

Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
Basket = get_model('basket', 'Basket')
Line = get_model('basket', 'Line')
CommissionBuy = get_model('commission', 'CommissionBuy')
Partner = get_model('partner', 'Partner')
ProductOrder = get_model('commission', 'ProductOrder')
OrderInfo = get_model('commission', 'OrderInfo')
SystemConfig = get_model('commission', 'SystemConfig')
app_secret_key = getattr(settings, 'APP_SECRET_KEY', 'aeb11af7b1750854cb6217cf33e1a5e48826369c1e255c33ff655ff3fc938e')
WishLine = get_model('wishlists', 'Line')


# 验证sign
def check_sign(request):
    device_id = request.data.get('device_id', '')
    sign = request.data.get('sign', '')
    if device_id and sign:
        correct_sign = hashlib.md5(''.join([device_id, app_secret_key, 'lantubaihuo'])).hexdigest()
        if sign == correct_sign:
            return (True, 199, u'签名正确')
        else:
            return (False, 102, u'签名错误')
    return (False, 104, u'缺少关键参数')


# 验证是否开市
def check_market_opening():
    system_config = SystemConfig.objects.first()
    is_opening = system_config.is_open
    if is_opening:
        return (True, 199, u'系统开市')
    else:
        return (False, 116, u'系统已闭市，请在开市时操作')


# 验证密码
def check_password(password):
    if re.search(r'^(?![^a-zA-Z]+$)(?!\D+$).{6,15}$', password):
        return True
    else:
        return False


# 分页
def paging(total_data_number, page_nubmer, data_number):
    max_page_number = (int(total_data_number) + int(data_number) - 1) / int(data_number)

    if (int(page_nubmer)-1) >= max_page_number:
        current_page_number = max_page_number
    else:
        current_page_number = int(page_nubmer) - 1
    # current_page_number = page_nubmer
    start_data_number = current_page_number * int(data_number)
    end_data_number = start_data_number + int(data_number)
    total_page = max_page_number
    if total_data_number == 0:
        total_page = 0
        current_page_number = 0
    return (current_page_number, start_data_number, end_data_number, total_page)


# 充值
class APIRechargeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            data = {'transfer_amount': request.data['amount'],
                    'bank_account_pwd': request.data.get('bank_account_pwd', ''),  # 必须
                    'trade_pwd': request.data.get('trade_pwd', ''),  #对公账户必须
                    }
            RechargeView().recharge_core(request.user, data)
            return Response({'msg': 'success', 'balance': RechargeView().get_recharge(request.user)})
        except:
            return Response({'msg': 'failed'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            return Response({'msg': 'success', 'balance': RechargeView().get_recharge(request.user)})
        except:
            return Response({'msg': 'failed'}, status=status.HTTP_400_BAD_REQUEST)

# 购买 & 进货
class APIBuyView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        response = commission_buy_test(request)
        if response.status_code == 200:
            return Response({'msg': 'success', 'errcode':0, 'balance': RechargeView().get_recharge(request.user)})
        else:
            return Response({'msg': response.content, 'errcode':1})


# 出售
class APISellView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        response = commission_sale_test(request)
        if response.status_code == 200:
            return Response({'msg': 'success', 'errcode':0, 'balance': RechargeView().get_recharge(request.user)})
        else:
            return Response({'msg': response.content, 'errcode':1})

# 出售
class APIFactorySellView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        response = factory_commission_sale(request)
        if response.status_code == 200:
            return Response({'msg': 'success', 'balance': RechargeView().get_recharge(request.user)})
        else:
            return Response({'msg': response.content}, status=status.HTTP_400_BAD_REQUEST)

# 提货
class APIPickupView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        response = factory_commission_sale(request)
        if response.status_code == 200:
            return Response({'msg': 'success', 'balance': RechargeView().get_recharge(request.user)})
        else:
            return Response({'msg': response.content}, status=status.HTTP_400_BAD_REQUEST)

# 获取某商品行情信息
class APIProductStockView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            today = datetime.datetime.now().date()
            product_id = request.POST.get("product_id", "").strip().replace(" ", "")
            product_config = StockProductConfig.objects.get(product_id=product_id)
            ticker = StockTicker.objects.filter(product_id=product_id).filter(created_date=today)

            if ticker:
                ticker = ticker[0]
                data = {
                    "id":ticker.product.id,
                    "product_symbol":ticker.product_symbol,
                    "product_name":ticker.product_name,
                    "strike_price":floatformat(ticker.strike_price),
                    "net_change":floatformat(ticker.net_change),
                    "net_change_rise":floatformat(ticker.net_change_rise),
                    "bid_price":floatformat(ticker.bid_price),
                    "ask_price":floatformat(ticker.ask_price),
                    "bid_vol":ticker.bid_vol,
                    "ask_vol":ticker.ask_vol,
                    "opening_price":floatformat(ticker.opening_price),
                    "closing_price":floatformat(ticker.closing_price),
                    "high":floatformat(ticker.high),
                    "low":floatformat(ticker.low),
                    "volume":ticker.volume,
                    "total":floatformat(ticker.total),
                    "market_capitalization":floatformat(product_config.market_capitalization),
                    "quote": product_config.quote,
                    "max_buy_num":product_config.max_buy_num,
                    "max_deal_num":product_config.max_deal_num,
                    "max_num":product_config.max_num,
                    "opening_price":product_config.opening_price,
                    "min_price":product_config.min_price,
                    "min_bnum":product_config.min_bnum,
                    "min_snum":product_config.min_snum,
                    "once_max_num":product_config.once_max_num,
                    "ud_up_range":product_config.ud_up_range,
                    "ud_down_range":product_config.ud_down_range
                }

                return Response({'msg': 'success', 'data': data})

            else:
                return Response({'msg': 'failed, no ticker'})

        except Exception, e:
            return Response({'msg': str(e)}, status=500)

# 获取所有商品ID
class APIProductIdsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:

            products = Product.objects.filter(is_on_shelves = True,opening_date__lte=datetime.datetime.now().date()).values_list('id', flat=True)

            return Response({'msg': 'success', 'data': products})

        except Exception, e:
            return Response({'msg': str(e)}, status=500)

# 获取持有的商品
class APIUserProductView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            product_id=request.POST.get("product_id", "").replace(" ", "")
            products = UserProduct.objects.filter(user=request.user, product_id=product_id, trade_type='1')

            data = {}
            data[product_id] = {}

            if products:
                data[product_id]['quantity'] = products[0].quantity
                data[product_id]['can_pickup_quantity'] = products[0].can_pickup_quantity
                data[product_id]['overage_unit_price'] = products[0].overage_unit_price
                data[product_id]['quote_quantity'] = products[0].quote_quantity
                data[product_id]['total'] = products[0].total

                return Response({'errcode':0, 'msg': 'success', 'data': data})

        except Exception, e:
            return Response({'msg': str(e), 'errcode':1})

        return Response({'msg': 'success', 'data': {}})

# 获取app版本信息
class APIGetappversionView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        result = {}
        try:
            current_version = request.data.get('ver', '')
            operaing_system = request.data.get('device', '')
            if current_version and operaing_system in ['1', '2']:
                latest_app = App.objects.filter(operaing_system=operaing_system).order_by('-version').first()
                if latest_app:
                    if latest_app.version > current_version:
                        if latest_app.need_forced_update:
                            update_ver = '2'
                        else:
                            update_ver = '1'
                        version = latest_app.version
                    else:
                        update_ver = '3'
                        version = current_version
                    http_host = request.get_host()
                    download_url = ''.join(['http://', http_host, latest_app.app_file.url])
                    description = latest_app.description
                else:
                    update_ver = '1'
                    version = current_version
                    download_url = ''
                    description = ''
                sign = app_secret_key
                result['code'] = 199
                result['msg'] = u'获取版本信息成功。'
                # result['update_ver'] = update_ver
                version_info = {}
                version_info['version'] = version
                version_info['update_ver'] = update_ver
                version_info['download_url'] = download_url
                version_info['description'] = description
                version_info['sign'] = sign
                result['version_info'] = version_info
            else:
                result['code'] = 212
                result['msg'] = u'没有获取到手机当前APP的版本号或操作系统类型。'
            return Response(result)
        except Exception, e:
            return Response({'msg': u'没有获取到手机当前APP的版本号或操作系统类型。', 'code': 212})


# 注册前获取验证码
class APIGetsmscodeView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        result = {}
        (check_sign_result, check_code, check_msg) = check_sign(request)
        if not check_sign_result:
            result['code'] = check_code
            result['msg'] = check_msg
            return Response(result)
        try:
            mobile = request.POST.get('mobile', '')
            if not local_mobile_phone_validator(mobile):
                msg = u'手机号码不合法。'
                result['code'] = 234
                result['msg'] = msg
            else:
                try:
                    userprofile = UserProfile.objects.get(mobile_phone=mobile)
                    msg = u'此号码已经被注册。'
                    result['code'] = 233
                    result['msg'] = msg
                except UserProfile.DoesNotExist:
                    new_captcha = random.randint(100000, 999999)
                    current_captcha = Captcha.objects.get_or_create(recipient=mobile)[0]
                    current_captcha.captcha = new_captcha
                    current_captcha.deadline_time = datetime.datetime.now() + datetime.timedelta(minutes=10)
                    current_captcha.save()
                    send_content = u'您的验证码是：%s。请不要把验证码泄露给其他人。' % str(new_captcha)
                    if mobile:
                        (response_code, response_msg) = send_message(mobile, send_content)
                        if response_code == '2':
                            result['code'] = 199
                            result['msg'] = u'发送成功'
                            result['validity_time'] = '600'
                        else:
                            result['code'] = 232
                            result['msg'] = u'发送失败'
                    '''
                    result['code'] = 199
                    result['msg'] = u'发送成功'
                    result['validity_time'] = '600'
                    '''
            return Response(result)
        except Exception, e:
            return Response({'msg': u'发送失败', 'code': 232})


# 测试token
class APITestTokenView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        result = {}
        result['code'] = 231
        result['msg'] = u'成功'
        return Response(result)

# 注册
class APIRegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        result = {}
        (check_sign_result, check_code, check_msg) = check_sign(request)
        if not check_sign_result:
            result['code'] = check_code
            result['msg'] = check_msg
            return Response(result)
        try:
            password = request.POST.get('password', '')
            mobile = request.POST.get('mobile', '')
            introducer = request.POST.get('introducer', '')
            verify_code = request.POST.get('verify_code', '')
            if password and mobile and verify_code:
                if not local_mobile_phone_validator(mobile):
                    msg = u'手机号码不合法。'
                    result['code'] = 234
                    result['msg'] = msg
                    return Response(result)
                if not check_password(password):
                    result['code'] = 243
                    result['msg'] = u'密码不符合要求。'
                    return Response(result)
                if User.objects.filter(username=mobile).count() != 0:
                    result['code'] = 233
                    result['msg'] = u'此号码已经被注册。'
                    return Response(result)
                try:
                    userprofile = UserProfile.objects.get(mobile_phone=mobile)
                    result['code'] = 233
                    result['msg'] = u'此号码已经被注册。'
                except UserProfile.DoesNotExist:
                    try:
                        current_mobile_captcha = Captcha.objects.get(recipient=mobile)
                        if current_mobile_captcha.deadline_time < now():
                            result['code'] = 235
                            result['msg'] = u'验证码已过期。'
                            return Response(result)
                        if current_mobile_captcha.captcha != verify_code:
                            result['code'] = 237
                            result['msg'] = u'验证码不正确。'
                        else:
                            new_user = User.objects.create(username=mobile, password=make_password(password))
                            user_balance = UserBalance.objects.create(user=new_user)
                            today = datetime.datetime.now().date()
                            user_asset_daily_report = UserAssetDailyReport.objects.create(user=new_user,
                                                                                          target_date=today)
                            try:
                                current_userprofile = new_user.userprofile
                                current_userprofile.mobile_phone = mobile
                                current_userprofile.introducer = introducer
                            except UserProfile.DoesNotExist:
                                current_userprofile = UserProfile.objects.create(user=new_user, mobile_phone=mobile)
                            if request.META.has_key('HTTP_X_FORWARDED_FOR'):
                                current_ip =  request.META['HTTP_X_FORWARDED_FOR']
                            else:
                                current_ip = request.META['REMOTE_ADDR']
                            current_userprofile.register_ip = current_ip
                            current_userprofile.save()
                            result['code'] = 199
                            result['msg'] = u'注册成功。'
                    except Captcha.DoesNotExist:
                        result['code'] = 237
                        result['msg'] = u'验证码不正确。'
            return Response(result)
        except Exception, e:
            print e
            return Response({'msg': u'注册失败', 'code': 236})


# 登录
class APILoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        result = {}
        (check_sign_result, check_code, check_msg) = check_sign(request)
        if not check_sign_result:
            result['code'] = check_code
            result['msg'] = check_msg
            return Response(result)
        try:
            username = request.data.get('username', '')
            password = request.data.get('password', '')
            # login
            try:
                if not User.objects.filter(username=username).exists():
                    up = UserProfile.objects.get(mobile_phone=username)
                    username = up.user.username
                user = authenticate(username=username, password=password)

                if user:
                    login(request, user)
                    # get_token
                    http_host = request.get_host()
                    path_url = reverse('api:api_auth')
                    get_token_url = ''.join(['http://', http_host, path_url])
                    get_toekn_params = {'username': username, 'password': password}
                    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
                    res = requests.post(get_token_url, data=get_toekn_params, headers=headers)
                    token_json = res.json()
                    if token_json.has_key('token'):
                        token = token_json.get('token')     # token
                        try:
                            current_userprofile = user.userprofile
                        except UserProfile.DoesNotExist:
                            current_userprofile = UserProfile.objects.create(user=user)
                        if request.META.has_key('HTTP_X_FORWARDED_FOR'):
                            current_ip =  request.META['HTTP_X_FORWARDED_FOR']
                        else:
                            current_ip = request.META['REMOTE_ADDR']
                        current_userprofile.register_ip = current_ip
                        current_userprofile.save()

                        mobile = current_userprofile.mobile_phone
                        uid = current_userprofile.uid
                        nickname = current_userprofile.nickname
                        sex = current_userprofile.sex
                        try:
                            avatar = ''.join(['http://', http_host, current_userprofile.avatar.url])
                        except ValueError:
                            avatar = ''
                        email = user.email
                        if current_userprofile.birthday:
                            birthday = current_userprofile.birthday.strftime('%Y%m%d')
                        else:
                            birthday = ''
                        userinfo = {'username': username,
                                    'uid': uid,
                                    'nickname': nickname,
                                    'mobile': mobile,
                                    'sex': sex,
                                    'avatar': avatar,
                                    'email': email,
                                    'birthday': birthday,
                                    'token': token}
                        result['code'] = 199
                        result['msg'] = u'用户登录成功'
                        result['userinfo'] = userinfo
                    else:
                        result['code'] = 223
                        result['msg'] = u'密码错误'
                else:
                    result['code'] = 223
                    result['msg'] = u'密码错误'
            except UserProfile.DoesNotExist:
                result['code'] = 222
                result['msg'] = u'用户名或手机号不存在'
            return Response(result)
        except Exception, e:
            print e
            return Response({'msg': str(e), 'errcode':1})


# 获取图片验证码
class APIGetimgverifycodeView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        result = {}
        (check_sign_result, check_code, check_msg) = check_sign(request)
        if not check_sign_result:
            result['code'] = check_code
            result['msg'] = check_msg
            return Response(result)
        try:
            mobile = request.POST.get('mobile', '')
            if not local_mobile_phone_validator(mobile):
                msg = u'手机号码不合法。'
                result['code'] = 234
                result['msg'] = msg
                return Response(result)
            else:
                try:
                    userprofile = UserProfile.objects.get(mobile_phone=mobile)
                    current_key = CaptchaStore.generate_key()
                    image_url = captcha_image_url(current_key)
                    http_host = request.get_host()
                    img = ''.join(['http://', http_host, image_url])
                    current_store = CaptchaStore.objects.get(hashkey=current_key)
                    img_value = current_store.challenge

                    result['code'] = 199
                    result['msg'] = u'获取图片验证码成功'
                    result['img'] = img
                    result['imgvalue'] = img_value
                except UserProfile.DoesNotExist:
                    result['code'] = 240
                    result['msg'] = u'不存在使用这个手机号的用户'
            return Response(result)
        except Exception, e:
            return Response({'msg': u'获取图片验证码失败', 'code': 238})


# 忘记密码，发送手机短信验证码
class APIFindpwdView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        result = {}
        (check_sign_result, check_code, check_msg) = check_sign(request)
        if not check_sign_result:
            result['code'] = check_code
            result['msg'] = check_msg
            return Response(result)
        try:
            mobile = request.POST.get('mobile', '')
            if not local_mobile_phone_validator(mobile):
                msg = u'手机号码不合法。'
                result['code'] = 234
                result['msg'] = msg
                return Response(result)
            else:
                try:
                    userprofile = UserProfile.objects.get(mobile_phone=mobile)
                    new_captcha = random.randint(100000, 999999)
                    current_captcha = Captcha.objects.get_or_create(recipient=mobile)[0]
                    current_captcha.captcha = new_captcha
                    current_captcha.deadline_time = datetime.datetime.now() + datetime.timedelta(minutes=10)
                    current_captcha.save()
                    send_content = u'您的验证码是：%s。请不要把验证码泄露给其他人。' % str(new_captcha)
                    (response_code, response_msg) = send_message(mobile, send_content)
                    if response_code == '2':
                        result['code'] = 199
                        result['msg'] = u'状态正常，发送验证码到%s' % mobile
                    else:
                        result['code'] = 239
                        result['msg'] = u'发送失败'
                except UserProfile.DoesNotExist:
                    result['code'] = 240
                    result['msg'] = u'不存在使用这个手机号的用户'
            return Response(result)
        except Exception, e:
            return Response({'msg': str(e), 'errcode':1})


# 重置密码
class APIResetpwdView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        result = {}
        (check_sign_result, check_code, check_msg) = check_sign(request)
        if not check_sign_result:
            result['code'] = check_code
            result['msg'] = check_msg
            return Response(result)
        try:
            mobile = request.POST.get('mobile', '')
            new_password = request.POST.get('newpwd', '')
            re_password = request.POST.get('repwd', '')
            captcha = request.POST.get('captcha', '')
            if not local_mobile_phone_validator(mobile):
                msg = u'手机号码不合法。'
                result['code'] = 234
                result['msg'] = msg
                return Response(result)
            if new_password and re_password and captcha:
                try:
                    if new_password != re_password:
                        result['code'] = 241
                        result['msg'] = u'两次输入的密码不一致。'
                        return Response(result)
                    if not check_password(new_password):
                        result['code'] = 243
                        result['msg'] = u'密码不符合要求。'
                        return Response(result)

                    userprofile = UserProfile.objects.get(mobile_phone=mobile)
                    try:
                        current_mobile_captcha = Captcha.objects.get(recipient=mobile)
                        if current_mobile_captcha.captcha != captcha:
                            result['code'] = 237
                            result['msg'] = u'验证码不正确。'
                            return Response(result)
                        if current_mobile_captcha.deadline_time < now():
                            result['code'] = 235
                            result['msg'] = u'验证码已过期。'
                            return Response(result)
                        else:
                            current_user = userprofile.user
                            password = make_password(new_password)
                            current_user.password = password
                            current_user.save()
                            result['code'] = 199
                            result['msg'] = u'重置密码成功。'
                    except Captcha.DoesNotExist:
                        result['code'] = 237
                        result['msg'] = u'验证码不正确。'
                        return Response(result)
                except UserProfile.DoesNotExist:
                    result['code'] = 240
                    result['msg'] = u'不存在使用这个手机号的用户'
            else:
                result['code'] = 104
                result['msg'] = u'缺少关键参数'
            return Response(result)
        except Exception, e:
            return Response({'msg': u'重置密码异常', 'code': 242})


# 修改头像
class APIUpdateavatarView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        result = {}
        try:
            uid = request.POST.get('uid', '')
            avatar = request.FILES.get('img', '')
            if uid and avatar:
                try:
                    userprofile = UserProfile.objects.get(uid=uid)

                    avatar_path = os.path.join(settings.MEDIA_ROOT, settings.AVATAR_ROOT)
                    avatar_name = avatar.name

                    current_avatar = open(os.path.join(avatar_path, avatar_name), 'wb+')
                    for chunk in avatar.chunks():
                        current_avatar.write(chunk)
                    userprofile.avatar = File(current_avatar)
                    userprofile.save()
                    current_avatar.close()
                    http_host = request.get_host()
                    imgurl = ''.join(['http://', http_host, userprofile.avatar.url])

                    result['code'] = 199
                    result['msg'] = u'更新头像成功。'
                    result['imgurl'] = imgurl
                except UserProfile.DoesNotExist:
                    result['code'] = 251
                    result['msg'] = u'不存在这个uid'
            else:
                result['code'] = 104
                result['msg'] = u'缺少关键参数'
            return Response(result)
        except Exception, e:
            return Response({'msg': u'更新头像失败', 'code': 252})


# 验证用户名唯一性
class APICheckusernameView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        result = {}
        (check_sign_result, check_code, check_msg) = check_sign(request)
        if not check_sign_result:
            result['code'] = check_code
            result['msg'] = check_msg
            return Response(result)
        try:
            user = request.user
            uid = request.POST.get('uid', '')
            username = request.POST.get('username', '')
            if uid and username:
                try:
                    userprofile = UserProfile.objects.get(uid=uid)
                except UserProfile.DoesNotExist:
                    result['code'] = 251
                    result['msg'] = u'不存在这个uid'
                    return Response(result)

                if User.objects.filter(username=username).exclude(pk=user.pk).exists() \
                   or UserProfile.objects.filter(mobile_phone=username).exclude(user=user).exists():
                    result['code'] = 256
                    result['msg'] = u'该用户名已经被注册过了。'
                else:
                    result['code'] = 199
                    result['msg'] = u'该用户名可用。'
            else:
                result['code'] = 104
                result['msg'] = u'缺少关键参数'
            return Response(result)
        except Exception, e:
            return Response({'msg': str(e), 'errcode':1})


# 修改用户名
class APIUpdateusernameView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        result = {}
        (check_sign_result, check_code, check_msg) = check_sign(request)
        if not check_sign_result:
            result['code'] = check_code
            result['msg'] = check_msg
            return Response(result)
        try:
            user = request.user

            uid = request.POST.get('uid', '')
            username = request.POST.get('username', '')
            if uid and username:
                try:
                    userprofile = user.userprofile
                    if userprofile.username_checked:
                        result['code'] = 257
                        result['msg'] = u'该用户的用户名已经被修改过了'
                        return Response(result)
                except UserProfile.DoesNotExist:
                    result['code'] = 251
                    result['msg'] = u'不存在这个uid'
                    return Response(result)

                if User.objects.filter(username=username).exclude(pk=user.pk).exists() \
                   or UserProfile.objects.filter(mobile_phone=username).exclude(user=user).exists():
                    result['code'] = 256
                    result['msg'] = u'该用户名已经被注册过了。'
                else:
                    current_user = userprofile.user
                    current_user.username = username
                    current_user.save()
                    userprofile.username_checked = True
                    userprofile.save()
                    result['code'] = 199
                    result['msg'] = u'更新用户名成功。'
            else:
                result['code'] = 104
                result['msg'] = u'缺少关键参数'
            return Response(result)
        except Exception, e:
            return Response({'msg': str(e), 'errcode':1})


# 首页最上：移动端轮播广告
class APIGetmaininfolistView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        result = {}
        try:
            current_mobile_carousel_ads = RollingAd.objects.filter(position='mobile_home_carousel',
                                                                    valid=True).order_by('order_num')
            if current_mobile_carousel_ads.count() > 5:
                current_mobile_carousel_ads = current_mobile_carousel_ads[:5]

            http_host = request.get_host()
            bannerimg = [{'image_url': ''.join(['http://', http_host, ad.image.url]), 'link_id': ad.link_url}
                    for ad in current_mobile_carousel_ads]
            mobile_home_url = reverse('mobile:mobile_home')
            body_url = ''.join(['http://', http_host, mobile_home_url])

            refresh_time = str(int(time.time()))

            result['code'] = 199
            result['msg'] = u'获取首页列表信息成功'
            result['bannerimg'] = bannerimg
            result['body'] = body_url
            result['refresh_time'] = refresh_time
            return Response(result)
        except Exception, e:
            return Response({'msg': u'获取首页列表信息失败', 'code': 311})


# 首页最下：推荐商品
class APIGetmoreproductlistView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        result = {}
        try:
            page_number = request.POST.get('page_number', 1)
            data_number = request.POST.get('data_number', 20)
            try:
                page_number = int(page_number)
                data_number = int(data_number)
            except ValueError:
                result['code'] = 313
                result['msg'] = u'分页参数异常。'
                return Response(result)
            if (page_number <= 0) or (data_number <= 0):
                result['code'] = 313
                result['msg'] = u'分页参数异常。'
                return Response(result)
            product_list = Product.objects.filter(is_on_shelves=True,opening_date__lte=datetime.datetime.now().date()).annotate(q=Sum('trade_complete_product__quantity')).order_by('-q')[:100]
            total_data_number = len(product_list)
            (current_page_number, start_data_number, end_data_number, total_page) = paging(total_data_number,
                                                                                page_number,
                                                                                data_number)
            current_product_list = product_list[start_data_number: end_data_number]
            http_host = request.get_host()
            datalist = []
            for product in current_product_list:
                if isinstance(product.primary_image(), dict):
                    imgurl = ''
                else:
                    imgurl = ''.join(['http://', http_host, product.primary_image().original.url])
                datalist.append({'imgurl': imgurl,
                                'product_id': product.id,
                                'product_name': product.title,
                                'price': product.buy_price})

            nowtime = str(int(time.time()))

            if end_data_number >= len(product_list):
                result['code'] = 314
                result['msg'] = u'已经是最后一页了。'
            else:
                result['code'] = 199
                result['msg'] = u'首页加载更多成功'
            result['current_page'] = current_page_number + 1
            result['total_page'] = total_page
            result['nowtime'] = nowtime
            result['datalist'] = datalist
            return Response(result)
        except Exception, e:
            return Response({'msg': u'首页加载更多异常', 'code':1})


# 商品详情
class APIGetproductdetailView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (permissions.AllowAny,)

    def post(self, request, product_id):
        result = {}
        try:
            current_product = Product.objects.get(id=product_id)
            product_upc = current_product.upc
            product_name = current_product.title
            images = current_product.images.all()
            http_host = request.get_host()
            username = request.POST.get('username','')
            img_url = [''.join(['http://', http_host, image.original.url]) for image in images]
            introduce = ''
            price = current_product.buy_price
            market_price = current_product.stockrecords.first().price_retail
            volume = current_product.volume

            today = datetime.datetime.now().date()
            current_stock_ticker = StockTicker.objects.get_or_create(product=current_product,
                                                                     created_date=today,
                                                                     product_symbol=current_product.upc,
                                                                     product_name=current_product.title)[0]
            high_price = current_stock_ticker.high
            low_price = current_stock_ticker.low

            current_stock_product_config = StockProductConfig.objects.get_or_create(product=current_product)[0]
            max_buy_num = current_stock_product_config.max_buy_num
            min_buy_num = 0
            if current_stock_product_config.self_pick_or_express in [1, 3]:
                pickup = 1
            else:
                pickup = 0
            is_new = 0
            on_sale = 0
            sale_service = ''
            reviews = ''
            product_detail = ''.join(['http://', http_host, '/api/product_description/%s/'%product_id])

            # attributes
            current_product_group = current_product.product_group
            if current_product_group:
                product_group_attr_count = current_product_group.attr.count()
                if product_group_attr_count == 2:
                    try:
                        attribute_first = current_product_group.attr.all().order_by('index')[0]
                        attribute_second = current_product_group.attr.all().order_by('index')[1]
                        cur_first_attr_value = ProductAttributeValue.objects.get(attribute=attribute_first, product=current_product).value_text
                        cur_second_attr_value = ProductAttributeValue.objects.get(attribute=attribute_second, product=current_product).value_text
                        attribute_first_values = current_product_group.get_first_attr_value_list_mobile(cur_second_attr_value)
                        attribute_second_values = current_product_group.get_second_attr_value_list_mobile(cur_first_attr_value)
                        available_attribute_first_values = [{"text":value.get('text', ''),"id":value.get('id','')} for value in attribute_first_values]
                        available_attribute_second_values = [{"text":value.get('text', ''),"id":value.get('id','')} for value in attribute_second_values if value.get('has', '') == 'true']
                        attribute_first_name = attribute_first.name
                        attribute_second_name = attribute_second.name
                    except:
                        attribute_first_name = ''
                        attribute_first_values = []
                        attribute_second_name = ''
                        attribute_second_values = []
                elif product_group_attr_count == 1:
                    try:
                        attribute_first = current_product_group.attr.all().order_by('index')[0]
                        cur_first_attr_value = ProductAttributeValue.objects.get(attribute=attribute_first,product=current_product).value_text
                        attribute_first_values = current_product_group.get_single_attr_value_list()
                        attribute_first_name = attribute_first.name
                        available_attribute_first_values = [{"text":value.get('text', ''),"id":value.get('id','')} for value in attribute_first_values]
                        attribute_second = ''
                        attribute_second_name = ''
                        available_attribute_second_values = []
                    except:
                        attribute_first_name = ''
                        available_attribute_first_values = []
                        attribute_second_name = ''
                        available_attribute_second_values = []
                else:
                    attribute_first_name = ''
                    available_attribute_first_values = []
                    attribute_second_name = ''
                    available_attribute_second_values = []
            else:
                attribute_first_name = ''
                available_attribute_first_values = []
                attribute_second_name = ''
                available_attribute_second_values = []

            user = None
            if username:
                user = User.objects.get(username=username)
                current_basket = Basket.objects.get_or_create(owner=user, status='Open',)[0]
                basket_num = sum([line.quantity for line in current_basket.all_lines()])
            else:
                basket_num = 0

            if request.user and request.user.id is not None and WishLine.objects.filter(wishlist__owner=request.user, product__pk=product_id).exists():
                user_focused = '1'
            else:
                user_focused = '0'
            detail = {'product_id': product_id,
                      'product_upc': product_upc,
                      'product_name': product_name,
                      'img_url': img_url,
                      'introduce': introduce,
                      'price': price,
                      'market_price': market_price,
                      'volume': volume,
                      'high_price': high_price,
                      'low_price': low_price,
                      'max_buy_num': max_buy_num,
                      'min_buy_num': min_buy_num,
                      'pickup': pickup,
                      'is_new': is_new,
                      'on_sale': on_sale,
                      'attribute_first_name': attribute_first_name,
                      'attribute_first_values': available_attribute_first_values,
                      'attribute_second_name': attribute_second_name,
                      'attribute_second_values': available_attribute_second_values,
                      'sale_service': sale_service,
                      'reviews': reviews,
                      'product_detail': product_detail,
                      'basket_num':basket_num,
                      'user_focused': user_focused,
            }
            result['code'] = 199
            result['msg'] = u'获取商品详细信息成功。'
            result['detail'] = detail
            return Response(result)

        except Product.DoesNotExist:
            result['code'] = 321
            result['msg'] = u'该商品不存在'
            return Response(result)

        except Exception, e:
            traceback.print_exc()
            return Response({'msg': u'获取商品详细信息异常。', 'code':1})


# 获取产品分类
class APIGetcategoryView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        result = {}
        http_host = request.get_host()
        try:
            secondary_category_list = Category.objects.filter(depth=2)
            datalist = []
            for secondary_category in secondary_category_list:
                children = []
                for three_tier_category in secondary_category.get_children():
                    try:
                        image = ''.join(['http://', http_host, three_tier_category.image.url])
                    except ValueError:
                        image = ''
                    child = {'category_id': three_tier_category.id,
                                  'category_name': three_tier_category.name,'image':image}
                    children.append(child)
                onedata = {'category_id': secondary_category.id,
                         'category_name': secondary_category.name,
                         'children': children
                        }
                datalist.append(onedata)
            result['code'] = 199
            result['msg'] = u'获取商品分类成功'
            result['datalist'] = datalist
            return Response(result)
        except Exception, e:
            return Response({'msg': u'获取商品分类失败', 'code': 341})


# 购物车
# 把商品添加到购物车
class APIAddtobasketView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, product_id):
        result = {}
        try:
            current_product = Product.objects.get(id=product_id)
            num = request.POST.get('num','')
            user = request.user
            current_basket = Basket.objects.get_or_create(owner=user, status='Open',)[0]
            lf = current_basket._create_line_reference(product=current_product,stockrecord=current_product.stockrecords.first(),options=None)
            try:
                current_line = Line.objects.get(basket=current_basket, product=current_product, stockrecord=current_product.stockrecords.first(), line_reference=lf)
                current_line.quantity += int(num)
                current_line.save()
            except:
                current_line = Line.objects.get_or_create(basket=current_basket, product=current_product, quantity=num, stockrecord=current_product.stockrecords.first(),line_reference=lf)[0]
            result['code'] = 199
            result['msg'] = u'添加商品到购物车成功'
            result['basket_num'] = sum([line.quantity for line in request.basket.all_lines()])
            return Response(result)
        except Product.DoesNotExist:
            result['code'] = 321
            result['msg'] = u'该商品不存在'
            return Response(result)
        except Exception:
            traceback.print_exc()
            result['code'] = 411
            result['msg'] = u'添加商品到购物车失败'
            return Response(result)


#查询购物车详情
class APIGetBasketView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        result = {}
        (check_sign_result, check_code, check_msg) = check_sign(request)
        if not check_sign_result:
            result['code'] = check_code
            result['msg'] = check_msg
            return Response(result)
        try:
            user = request.user
            page_number = request.POST.get('page_number', 1)
            data_number = request.POST.get('data_number', 20)
            current_basket = Basket.objects.get_or_create(owner=user, status='Open',)[0]
            lines = current_basket.lines.all()
            result['code'] = 199
            result['msg']=u'查询购物车成功'
            product_list = []
            for line in lines:
                try:
                    image = line.product.images.first().original.url
                except:
                    image = ""
                product_info = {"product_id":line.product.id,"product_symbol":line.product.upc,"product_name":line.product.get_title(),"imgurl":image,
                                "price":line.buy_price,"market_price":line.product.stockrecords.first().price_retail,"order_num":line.quantity}
                current_product_group = line.product.product_group
                if current_product_group:
                    product_group_attr_count = current_product_group.attr.count()
                    if product_group_attr_count == 2:
                        try:
                            attribute_first = current_product_group.attr.all().order_by('index')[0]
                            attribute_second = current_product_group.attr.all().order_by('index')[1]
                            cur_first_attr_value = ProductAttributeValue.objects.get(attribute=attribute_first, product=line.product).value_text
                            cur_second_attr_value = ProductAttributeValue.objects.get(attribute=attribute_second, product=line.product).value_text
                            attribute_first_name = attribute_first.name
                            attribute_second_name = attribute_second.name
                            product_info["attr1"] = attribute_first_name
                            product_info["attr1value"] = cur_first_attr_value
                            product_info["attr2"] = attribute_second_name
                            product_info["attr2value"] = cur_second_attr_value
                        except:
                            product_info["attr1"] = ""
                            product_info["attr1value"] = ""
                            product_info["attr2"] = ""
                            product_info["attr2value"] = ""
                    elif product_group_attr_count == 1:
                        try:
                            attribute_first = current_product_group.attr.all().order_by('index')[0]
                            cur_first_attr_value = ProductAttributeValue.objects.get(attribute=attribute_first,product=line.product).value_text
                            attribute_first_name = attribute_first.name
                            product_info["attr1"] = attribute_first_name
                            product_info["attr1value"] = cur_first_attr_value
                        except:
                            product_info["attr1"] = ""
                            product_info["attr1value"] = ""
                product_list.append(product_info)
            total_data_number = len(product_list)
            (current_page_number, start_data_number, end_data_number, total_page) = paging(total_data_number,
                                                                                page_number,
                                                                                data_number)
            current_product_list = product_list[start_data_number: end_data_number]
            
            result['current_page'] = current_page_number + 1
            result['total_page'] = total_page
            result['product_list']=current_product_list
            return Response(result)
        except Exception:
            traceback.print_exc()
            result['code'] = 421
            result['msg'] = u'查询购物车失败'
            return Response(result)


#删除购物车内商品
class APIDelCartProductView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        result = {}
        content = request.POST.get('content', '')
        try:
            user = request.user
            current_basket = Basket.objects.get_or_create(owner=user, status='Open',)[0]
            try:
                id_list = content.split(",")
                for one_product_id in id_list:
                    current_basket.lines.filter(product_id=int(one_product_id))[0].delete()
                result['code'] = 199
                result['msg'] = u'删除购物车商品成功'
                return Response(result)
            except:
                result['code'] = 432
                result['msg'] = u'删除内容错误'
                return Response(result) 
        except Exception:
            result['code'] = 431
            result['msg'] = u'删除购物车商品失败'
            return Response(result) 
        

#修改购物车内商品数量
class APIUpdateCartNumView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        result = {}
        try:
            product_id = request.POST.get('product_id', '')
            ordernum = int(request.POST.get('ordernum', ''))
            if ordernum < 1:
                result['code'] = 442
                result['msg'] = u'数量小于1'
                return Response(result)
            user = request.user
            product = Product.objects.get(id=product_id)
            current_basket = Basket.objects.get_or_create(owner=user, status='Open',)[0]
            line = current_basket.lines.filter(product=product)[0]
            line.quantity = ordernum
            line.save()
            result['code'] = 199
            result['msg'] = u'修改购物车成功'
            return Response(result)
        except Product.DoesNotExist:
            result['code'] = 443
            result['msg'] = u'该商品不存在'
            return Response(result)
        except Exception:
            result['code'] = 441
            result['msg'] = u'修改购物车失败'
            return Response(result) 


#商品进货
class APITradeInView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        result = {}
        (check_sign_result, check_code, check_msg) = check_sign(request)
        if not check_sign_result:
            result['code'] = check_code
            result['msg'] = check_msg
            return Response(result)
        try:
            product_id = request.POST.get('product_id', '')
            ordernum = int(request.POST.get('ordernum', ''))
            order_price = float(request.POST.get('order_price', ''))
            if ordernum < 1:
                result['code'] = 462
                result['msg'] = u'进货委托数量错误'
                return Response(result)
            user = request.user
            product = Product.objects.get(id=product_id)
            new_commission_buy(product,user,2,order_price,ordernum,ordernum,1)
            result['code'] = 199
            result['msg'] = u'进货委托成功'
            return Response(result)
        except Product.DoesNotExist:
            result['code'] = 463
            result['msg'] = u'该商品不存在'
            return Response(result)
        except Exception:
            traceback.print_exc()
            result['code'] = 461
            result['msg'] = u'进货委托失败'
            return Response(result) 


#商品出售
class APITradeOutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        result = {}
        (check_sign_result, check_code, check_msg) = check_sign(request)
        if not check_sign_result:
            result['code'] = check_code
            result['msg'] = check_msg
            return Response(result)
        try:
            product_id = request.POST.get('product_id', '')
            ordernum = int(request.POST.get('ordernum', ''))
            order_price = float(request.POST.get('order_price', ''))
            if ordernum < 1:
                result['code'] = 472
                result['msg'] = u'出售委托数量错误'
                return Response(result)
            user = request.user
            product = Product.objects.get(id=product_id)
            new_commissiton_sale(product,user,1,order_price,ordernum,ordernum,1)
            result['code'] = 199
            result['msg'] = u'出售委托成功'
            return Response(result)
        except Exception:
            traceback.print_exc()
            result['code'] = 471
            result['msg'] = u'进货委托失败'
            return Response(result) 
        

#批量查询
class APIBatchQueryView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        result = {}
        try:
            page_number = request.POST.get('page_number', 1)
            data_number = request.POST.get('data_number', 20)
            content = request.POST.get('content', '')
            id_list = content.split(",")
            result['code'] = 199
            result['msg']=u'批量查询成功'
            product_list = []
            for one_product_id in id_list:
                try:
                    product = Product.objects.get(id=one_product_id)
                    try:
                        image = product.images.first().original.url
                    except:
                        image = ""
                    product_info = {"product_id":product.id,"product_symbol":product.upc,"product_name":product.get_title(),"imgurl":image,
                                    "price":product.buy_price,"market_price":product.stockrecords.first().price_retail}
                    current_product_group = product.product_group
                    if current_product_group:
                        product_group_attr_count = current_product_group.attr.count()
                        if product_group_attr_count == 2:
                            try:
                                attribute_first = current_product_group.attr.all().order_by('index')[0]
                                attribute_second = current_product_group.attr.all().order_by('index')[1]
                                cur_first_attr_value = ProductAttributeValue.objects.get(attribute=attribute_first, product=product).value_text
                                cur_second_attr_value = ProductAttributeValue.objects.get(attribute=attribute_second, product=product).value_text
                                attribute_first_name = attribute_first.name
                                attribute_second_name = attribute_second.name
                                product_info["attr1"] = attribute_first_name
                                product_info["attr1value"] = cur_first_attr_value
                                product_info["attr2"] = attribute_second_name
                                product_info["attr2value"] = cur_second_attr_value
                            except:
                                product_info["attr1"] = ""
                                product_info["attr1value"] = ""
                                product_info["attr2"] = ""
                                product_info["attr2value"] = ""
                        elif product_group_attr_count == 1:
                            try:
                                attribute_first = current_product_group.attr.all().order_by('index')[0]
                                cur_first_attr_value = ProductAttributeValue.objects.get(attribute=attribute_first,product=product).value_text
                                attribute_first_name = attribute_first.name
                                product_info["attr1"] = attribute_first_name
                                product_info["attr1value"] = cur_first_attr_value
                            except:
                                product_info["attr1"] = ""
                                product_info["attr1value"] = ""
                    product_list.append(product_info)
                except Product.DoesNotExist:
                    pass
            total_data_number = len(id_list)
            (current_page_number, start_data_number, end_data_number, total_page) = paging(total_data_number,
                                                                                page_number,
                                                                                data_number)
            current_product_list = product_list[start_data_number: end_data_number]
            
            result['current_page'] = current_page_number + 1
            result['total_page'] = total_page
            result['product_list']=current_product_list
            return Response(result)
        except Exception:
            traceback.print_exc()
            result['code'] = 451
            result['msg'] = u'批量查询失败'
            return Response(result)
        

class APIBatchAddtobasketView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        result = {}
        try:
            content = request.data.get("content","")
            user = request.user
            current_basket = Basket.objects.get_or_create(owner=user, status='Open',)[0]
            for info in content:
                try:
                    current_product = Product.objects.get(id=info["id"])
                except Product.DoesNotExist:
                    result['code'] = 462
                    result['msg'] = u'商品不存在'
                    return Response(result)
                lf = current_basket._create_line_reference(product=current_product,stockrecord=current_product.stockrecords.first(),options=None)
                num = int(info["num"])
                try:
                    current_line = Line.objects.get(basket=current_basket, product=current_product, stockrecord=current_product.stockrecords.first(), line_reference=lf)
                    current_line.quantity += int(num)
                    current_line.save()
                except:
                    current_line = Line.objects.get_or_create(basket=current_basket, product=current_product, quantity=num, stockrecord=current_product.stockrecords.first(),line_reference=lf)[0]
            result['code'] = 199
            result['msg'] = u'批量添加商品到购物车成功'
            result['basket_num'] = sum([line.quantity for line in request.basket.all_lines()])
            return Response(result)
        except Exception:
            traceback.print_exc()
            result['code'] = 461
            result['msg'] = u'批量添加商品到购物车失败'
            return Response(result)



#规格选择            
class APIGetprobyattrView(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    
    def get(self, request, product_id):
        result = {}
        try:
            current_product = Product.objects.get(id=product_id)
            product_name = current_product.title
            img_url = current_product.primary_image().original.url
            price = current_product.buy_price
            product_price = current_product.product_price
            price_range = current_product.price_range
            unit_quote = current_product.quote
            product_config = current_product.stock_config_product
            config_max_num = int(product_config.max_deal_num)
            current_product_group = current_product.product_group
            attribute_first_name = ""
            attribute_second_name = ""
            cur_first_attr_value = ""
            cur_second_attr_value = ""
            available_attribute_first_values = ""
            available_attribute_second_values  = ""
            if current_product_group:
                product_group_attr_count = current_product_group.attr.count()
                if product_group_attr_count == 2:
                    try:
                        attribute_first = current_product_group.attr.all().order_by('index')[0]
                        attribute_second = current_product_group.attr.all().order_by('index')[1]
                        cur_first_attr_value = ProductAttributeValue.objects.get(attribute=attribute_first, product=current_product).value_text
                        cur_second_attr_value = ProductAttributeValue.objects.get(attribute=attribute_second, product=current_product).value_text
                        attribute_first_name = attribute_first.name
                        attribute_second_name = attribute_second.name
                        attribute_first_values = current_product_group.get_first_attr_value_list_mobile(cur_second_attr_value)
                        attribute_second_values = current_product_group.get_second_attr_value_list_mobile(cur_first_attr_value)
                        available_attribute_first_values = [{"text":value.get('text', ''),"id":value.get('id','')} for value in attribute_first_values]
                        available_attribute_second_values = [{"text":value.get('text', ''),"id":value.get('id','')} for value in attribute_second_values if value.get('has', '') == 'true']
                    except:
                        raise
                elif product_group_attr_count == 1:
                    try:
                        attribute_first = current_product_group.attr.all().order_by('index')[0]
                        cur_first_attr_value = ProductAttributeValue.objects.get(attribute=attribute_first,product=current_product).value_text
                        attribute_first_name = attribute_first.name
                        attribute_first_values = current_product_group.get_single_attr_value_list()
                        available_attribute_first_values = [{"text":value.get('text', ''),"id":value.get('id','')} for value in attribute_first_values]
                        attribute_second_name = ""
                        cur_second_attr_value = ""
                        available_attribute_second_values  = ""
                    except:
                        raise
            result['code'] = 199
            result['msg'] = u'成功'
            result['product_name'] = product_name
            result['img_url'] = img_url
            result['price'] = price
            result['product_price'] = product_price
            result['price_high'] = price_range[0]
            result['price_low'] = price_range[1]
            result['unit_quote'] = unit_quote
            result['max_deal_num'] = config_max_num
            result['attribute_first_name'] = attribute_first_name
            result['attribute_second_name'] = attribute_second_name
            result['cur_first_attr_value'] = cur_first_attr_value
            result['cur_second_attr_value'] = cur_second_attr_value
            result['attribute_first_values'] = available_attribute_first_values
            result['attribute_second_values'] = available_attribute_second_values
            return Response(result)
        except Product.DoesNotExist:
            result['code'] = 332
            result['msg'] = u'该商品不存在'
            return Response(result)
        except Exception:
            traceback.print_exc()
            result['code'] = 331
            result['msg'] = u'获取商品id规格失败'
            return Response(result)
    def post(self, request, product_id):
        result = {}
        try:
            current_product = Product.objects.get(id=product_id)
            product_name = current_product.title
            img_url = current_product.primary_image().original.url
            price = current_product.buy_price
            product_price = current_product.product_price
            price_range = current_product.price_range
            unit_quote = current_product.quote
            user = request.user
            product_config = current_product.stock_config_product
            config_max_num = int(product_config.max_deal_num)
            try:
                quote_quantity = int(UserProduct.objects.get(user=user,product=current_product,trade_type=1).quote_quantity)
            except UserProduct.DoesNotExist:
                quote_quantity = 0
            try:
                buy_num = int(UserProduct.objects.get(user=user,product=current_product,trade_type=2).quantity)
                all_commission = CommissionBuy.objects.filter(user=user,product=current_product,c_type=2,status__in=[1,2])
                commission_num = 0
                for commission in all_commission:
                    commission_num += commission.uncomplete_quantity
                max_buy_num = int(config_max_num-commission_num-buy_num)
            except UserProduct.DoesNotExist:
                all_commission = CommissionBuy.objects.filter(user=user,product=current_product,c_type=2,status__in=[1,2])
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
            current_product_group = current_product.product_group
            attribute_first_name = ""
            attribute_second_name = ""
            cur_first_attr_value = ""
            cur_second_attr_value = ""
            available_attribute_first_values = ""
            available_attribute_second_values  = ""
            if current_product_group:
                product_group_attr_count = current_product_group.attr.count()
                if product_group_attr_count == 2:
                    try:
                        attribute_first = current_product_group.attr.all().order_by('index')[0]
                        attribute_second = current_product_group.attr.all().order_by('index')[1]
                        cur_first_attr_value = ProductAttributeValue.objects.get(attribute=attribute_first, product=current_product).value_text
                        cur_second_attr_value = ProductAttributeValue.objects.get(attribute=attribute_second, product=current_product).value_text
                        attribute_first_name = attribute_first.name
                        attribute_second_name = attribute_second.name
                        attribute_first_values = current_product_group.get_first_attr_value_list_mobile(cur_second_attr_value)
                        attribute_second_values = current_product_group.get_second_attr_value_list_mobile(cur_first_attr_value)
                        available_attribute_first_values = [{"text":value.get('text', ''),"id":value.get('id','')} for value in attribute_first_values]
                        available_attribute_second_values = [{"text":value.get('text', ''),"id":value.get('id','')} for value in attribute_second_values if value.get('has', '') == 'true']
                    except:
                        raise
                elif product_group_attr_count == 1:
                    try:
                        attribute_first = current_product_group.attr.all().order_by('index')[0]
                        cur_first_attr_value = ProductAttributeValue.objects.get(attribute=attribute_first,product=current_product).value_text
                        attribute_first_name = attribute_first.name
                        attribute_first_values = current_product_group.get_single_attr_value_list()
                        available_attribute_first_values = [{"text":value.get('text', ''),"id":value.get('id','')} for value in attribute_first_values]
                        attribute_second_name = ""
                        cur_second_attr_value = ""
                        available_attribute_second_values  = ""
                    except:
                        raise
            result['code'] = 199
            result['msg'] = u'成功'
            result['product_name'] = product_name
            result['img_url'] = img_url
            result['price'] = price
            result['product_price'] = product_price
            result['price_high'] = price_range[0]
            result['price_low'] = price_range[1]
            result['unit_quote'] = unit_quote
            result['max_deal_num'] = max_deal_num
            result['attribute_first_name'] = attribute_first_name
            result['attribute_second_name'] = attribute_second_name
            result['cur_first_attr_value'] = cur_first_attr_value
            result['cur_second_attr_value'] = cur_second_attr_value
            result['attribute_first_values'] = available_attribute_first_values
            result['attribute_second_values'] = available_attribute_second_values
            return Response(result)
        except Product.DoesNotExist:
            result['code'] = 332
            result['msg'] = u'该商品不存在'
            return Response(result)
        except Exception:
            traceback.print_exc()
            result['code'] = 331
            result['msg'] = u'获取商品id规格失败'
            return Response(result)
        

#提交订单            
class APICommitCartView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        result = {}
        (check_sign_result, check_code, check_msg) = check_sign(request)
        if not check_sign_result:
            result['code'] = check_code
            result['msg'] = check_msg 
            return Response(result)
        (is_opening, check_code, check_msg) = check_market_opening()
        if not is_opening:
            result['code'] = check_code
            result['msg'] = check_msg 
            return Response(result)
        try:
            current_basket = request.basket
            all_lines = current_basket.lines.all()
            current_user = request.user
            current_address_list = ReceivingAddress.objects.filter(user=current_user).order_by('-is_default')[:1]
            if current_address_list:
                current_address = current_address_list[0]
                address = "%s %s %s"%(current_address.province.name,current_address.city.name,current_address.address)
                address_info = {"id":current_address.id,"consignee":current_address.consignee,"mobile_phone":current_address.mobile_phone,"address":address,"is_default":current_address.is_default}
            else:
                address_info = ""
            current_product_list = Product.objects.filter(id__in=all_lines.values_list('product', flat=True))
            current_partner_list = Partner.objects.filter(id__in=current_product_list.values_list('stockrecords__partner'))
            total_pickup_price = 0
            total_express_price = 0
            total_product_price = 0
            pickup_type = request.POST.get('pickup_type', 'express')
            if pickup_type == 'express':
                product_info = []
                for partner in current_partner_list:
                    products = current_product_list.filter(stockrecords__partner=partner)
                    lines = all_lines.filter(product__in=products)
                    product_list = []
                    for product in products:
                        product_group = product.product_group
                        if product_group:
                            product_group_attr_count = product_group.attr.count()
                            if product_group_attr_count == 2:
                                first_attr = product_group.attr.all().order_by('index')[0]
                                second_attr = product_group.attr.all().order_by('index')[1]
                                first_attr_name = first_attr.name
                                second_attr_name = second_attr.name
                                cur_first_attr_value = ProductAttributeValue.objects.get(attribute=first_attr,product=product).value_text
                                cur_second_attr_value = ProductAttributeValue.objects.get(attribute=second_attr,product=product).value_text
                            elif product_group_attr_count == 1:
                                first_attr = product_group.attr.all().order_by('index')[0]
                                first_attr_name = first_attr.name
                                second_attr_name = ""
                                cur_first_attr_value = ProductAttributeValue.objects.get(attribute=first_attr,product=product).value_text
                                cur_second_attr_value = ""
                        else:
                            first_attr_name = ""
                            second_attr_name = ""
                            cur_first_attr_value = ""
                            cur_second_attr_value = ""
                        line = all_lines.get(product=product)
                        try:
                            image = line.product.images.first().original.url
                        except:
                            image = ""
                        one_product_info = {"name":product.title,"attribute_first_name":first_attr_name,"attribute_second_name":second_attr_name,
                                        "price":product.buy_price,"pickup_price":product.pickup_price,"quantity":line.quantity,
                                        "cur_first_attr_value":cur_first_attr_value,"cur_second_attr_value":cur_second_attr_value,'image':image}
                        product_list.append(one_product_info)
                    express_price = sum([line.product.express_price * line.quantity for line in lines])
                    total_express_price += express_price
                    pickup_price = sum([line.product.pickup_price * line.quantity for line in lines])
                    total_pickup_price += pickup_price
                    product_price = sum([line.total_price for line in lines])
                    total_product_price += product_price
                    partner_product = {"partner":partner.name,"products":product_list,"express_price":express_price,"pickup_price":pickup_price,"product_price":product_price}
                    product_info.append(partner_product) 
                total_price = total_pickup_price + total_express_price + total_product_price
                context = {"code":199,"product_info":product_info,"total_price":total_price,"total_express_price":total_express_price,
                           "total_pickup_price":total_pickup_price,"default_address":address_info,"total_product_price":total_product_price}
                return Response(context)
        except:
            traceback.print_exc()
            context = {"code":481,"msg":u"创立订单失败"}
            return Response(context)


#生成订单            
class APICommitOrderView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        result = {}
        (check_sign_result, check_code, check_msg) = check_sign(request)
        if not check_sign_result:
            result['code'] = check_code
            result['msg'] = check_msg 
            return Response(result)
        (is_opening, check_code, check_msg) = check_market_opening()
        if not is_opening:
            result['code'] = check_code
            result['msg'] = check_msg 
            return Response(result)
        try:
            current_basket = request.basket
            all_lines = current_basket.lines.all()
            current_user = request.user
            receiving_address_id = request.POST.get('receiving_address_id', '')
            current_receiving_address = ReceivingAddress.objects.get(id=receiving_address_id)
            pickup_type = request.POST.get('pickup_type', 'express')
            if pickup_type == "selfpickup":
                pass
            elif pickup_type == "express":
                current_product_list = Product.objects.filter(id__in=all_lines.values_list('product', flat=True))
                current_partner_list = Partner.objects.filter(id__in=current_product_list.values_list('stockrecords__partner'))
                partner_line_list = []
                total_pickup_price = 0
                total_express_price = 0
                total_product_price = 0
                for partner in current_partner_list:
                    products = current_product_list.filter(stockrecords__partner=partner)
                    lines = all_lines.filter(product__in=products)
                    pickup_price = sum([line.product.pickup_price * line.quantity for line in lines])
                    total_pickup_price += pickup_price
                    express_price = sum([line.product.express_price * line.quantity for line in lines])
                    total_express_price += express_price
                    product_price = sum([line.total_price for line in lines])
                    total_product_price += product_price
                    partner_line = {'partner': partner,
                                    'lines': lines,
                                    'pickup_price': pickup_price,
                                    'express_price': express_price}
                    partner_line_list.append(partner_line)
                total_price = total_pickup_price + total_express_price + total_product_price
                product_order = ProductOrder()
                product_order.user=current_user
                product_order.amount=total_price
                product_order.pickup_type=2
                product_order.status=0
                product_order.province=current_receiving_address.province
                product_order.city=current_receiving_address.city
                product_order.addr=current_receiving_address.address
                product_order.receive_addr = current_receiving_address
                product_order.product_price = total_product_price
                product_order.express_fee = total_express_price
                product_order.pickup_fee = total_pickup_price
                product_names = [product.title for product in current_product_list]
                product_order.detail = " ".join(product_names)
                product_order.custom_save()
                for current_product in current_product_list:
                    line = all_lines.get(product=current_product)
                    OrderInfo.objects.create(product_order=product_order,product=current_product,product_num=line.quantity,price=line.buy_price)
                current_basket.submit()
            context = {"code":199,"msg":u"生成订单成功","order_no":product_order.order_no}
            return Response(context)
        except:
            traceback.print_exc()
            context = {"code":491,"msg":u"生成订单失败"}
            return Response(context)


#订单列表            
class APIGetOrdersView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        result = {}
        try:
            result = {}
            user = request.user
            page_number = request.POST.get('page_number', 1)
            data_number = request.POST.get('data_number', 20)
            status_id = int(request.POST.get('status_id', 0))
            try:
                page_number = int(page_number)
                data_number = int(data_number)
            except ValueError:
                result['code'] = 662
                result['msg'] = u'分页参数异常'
                return Response(result)
            if (page_number <= 0) or (data_number <= 0):
                result['code'] = 662
                result['msg'] = u'分页参数异常。'
                return Response(result)
            all_order = ProductOrder.objects.filter(user=user).order_by('-created_datetime')
            if status_id == 1:
                all_order = all_order.filter(status__in=[0,1,3]).filter(effective=True)
            if status_id == 2:
                all_order = all_order.filter(status__in=[2,6,7]).filter(effective=True)
            total_data_number = len(all_order)
            (current_page_number, start_data_number, end_data_number, total_page) = paging(total_data_number,
                                                                                page_number,
                                                                                data_number)
            current_order_list = all_order[start_data_number: end_data_number]
            datalist = []
            for order in current_order_list:
                STATUS_CHOICES = ((0, u'未支付'), (1, u'支付中'), (2, u'支付成功'),
                      (3, u'支付失败'), (4, u'已关闭'), (5, u'已撤销'), (6, u'未发货'), (7, u'已发货'), (8, u'部分提货'), (9, u'已提货'))
                order_status_id = order.status
                order_status_name = STATUS_CHOICES[order_status_id][1]
                if order.effective == False:
                    order_status_id = 5
                    order_status_name = u"已撤消"
                all_info = order.order_info.all()
                img_list = [info.product.img_url_or_none for info in all_info]
                product_num = sum([info.product_num for info in all_info])
                order_info = {"order_id":order.id,"order_no":order.order_no,"order_status_id":order_status_id,"order_status_name":order_status_name,"detail":order.detail,"amount":order.amount,"img_list":img_list,"product_num":product_num}
                datalist.append(order_info)
            result['code'] = 199
            result['msg'] = u'获取我的订单成功'
            result['current_page'] = current_page_number + 1
            result['total_page'] = total_page
            result['order_list'] = datalist
            return Response(result)
        except:
            traceback.print_exc()
            result['code'] = 661
            result['msg'] = u"获取我的订单失败"
            return Response(result)
        
    
#订单详情         
class APIGetOrderDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, order_id):
        result = {}
        try:
            order = ProductOrder.objects.get(id=order_id)
            STATUS_CHOICES = ((0, u'未支付'), (1, u'支付中'), (2, u'支付成功'),
                  (3, u'支付失败'), (4, u'已关闭'), (5, u'已撤销'), (6, u'未发货'), (7, u'已发货'), (8, u'部分提货'), (9, u'已提货'))
            order_status_id = order.status
            order_status_name = STATUS_CHOICES[order_status_id][1]
            if order.effective == False:
                order_status_id = 5
                order_status_name = u"已撤消"
            if order.pickup_type == 1:
                pickup_type_name = u"自提"
            elif order.pickup_type == 2:
                pickup_type_name = u"物流"
            datalist = []
            all_info = order.order_info.all()
            for info in all_info:
                product = info.product
                product_group = product.product_group
                if product_group:
                    product_group_attr_count = product_group.attr.count()
                    if product_group_attr_count == 2:
                        first_attr = product_group.attr.all().order_by('index')[0]
                        second_attr = product_group.attr.all().order_by('index')[1]
                        first_attr_name = first_attr.name
                        second_attr_name = second_attr.name
                        cur_first_attr_value = ProductAttributeValue.objects.get(attribute=first_attr,product=product).value_text
                        cur_second_attr_value = ProductAttributeValue.objects.get(attribute=second_attr,product=product).value_text
                    elif product_group_attr_count == 1:
                        first_attr = product_group.attr.all().order_by('index')[0]
                        first_attr_name = first_attr.name
                        second_attr_name = ""
                        cur_first_attr_value = ProductAttributeValue.objects.get(attribute=first_attr,product=product).value_text
                        cur_second_attr_value = ""
                else:
                    first_attr_name = ""
                    second_attr_name = ""
                    cur_first_attr_value = ""
                    cur_second_attr_value = ""
                try:
                    img_url = product.primary_image().original.url
                except:
                    img_url = ""
                one_product_info = {"product_upc":product.upc,"product_name":product.title,"attribute_first_name":first_attr_name,
                                    "attribute_second_name":second_attr_name,"cur_first_attr_value":cur_first_attr_value,
                                    "cur_second_attr_value":cur_second_attr_value,"price":info.price,"order_num":info.product_num,
                                    "img_url":img_url}
                datalist.append(one_product_info)
            order_info = {"order_no":order.order_no,"order_status_id":order_status_id,"order_status_name":order_status_name,"addr":order.receive_addr.address,"province":order.receive_addr.province.name,"city":order.receive_addr.city.name,"district":order.receive_addr.district.name,
                          "consignee":order.receive_addr.consignee,"mobile_phone":order.receive_addr.mobile_phone,"email":order.receive_addr.email,"pickup_type_id":order.pickup_type,"pickup_type_name":pickup_type_name,"amount":order.amount,"product_price":order.product_price,"express_fee":order.express_fee,"pickup_fee":order.pickup_fee,"datalist":datalist}
            result['code'] = 199
            result['msg'] = u'获取订单成功'
            result['order_info'] = order_info
            return Response(result)
        except ProductOrder.DoesNotExist:
            result['code'] = 663
            result['msg'] = u'订单不存在'
            return Response(result)
        except:
            traceback.print_exc()
            result['code'] = 662
            result['msg'] = u'获取订单失败'
            return Response(result)
        
        
#取消订单     
class APICancelOrderView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, order_id):
        result = {}
        try:
            order = ProductOrder.objects.get(id=order_id)
            order.effective = False
            order.save()
            result['code'] = 199
            result['msg'] = u'取消订单成功'
            return Response(result)
        except ProductOrder.DoesNotExist:
            result['code'] = 663
            result['msg'] = u'订单不存在'
            return Response(result)
        except:
            traceback.print_exc()
            result['code'] = 662
            result['msg'] = u'取消订单失败'
            return Response(result)
        

#我的          
class APIGetMyselfView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            current_user = request.user
            try:
                current_userprofile = current_user.userprofile
            except UserProfile.DoesNotExist:
                current_userprofile = UserProfile.objects.create(user=current_user)
            nickname = current_userprofile.nickname
            if not nickname:
                nickname = current_user.username
            try:
                http_host = request.get_host()
                avatar = ''.join(['http://', http_host, current_userprofile.avatar.url])
            except ValueError:
                avatar = ''
            is_verified = True if hasattr(current_user, 'userprofile') and current_user.userprofile.audit_status else False
            user_order = ProductOrder.objects.filter(user=current_user)
            if user_order:
                has_order = True
                wait_pay = user_order.filter(status=0).count()
                wait_receive = user_order.filter(status__in=[2,6,7,8]).count()
                wait_evaluate = user_order.filter(status=9).count()
            else:
                has_order = False
                wait_pay = 0
                wait_receive = 0
                wait_evaluate = 0
            context = {"code":199,"nickname":nickname,"avatar":avatar,"is_verified":is_verified,
                       "has_order":has_order,"wait_pay":wait_pay,"wait_receive":wait_receive,"wait_evaluate":wait_evaluate}
            return Response(context)
        except:
            traceback.print_exc()
            context = {"code":671,"msg":u"获取我的失败"}
            return Response(context)


def product_description(request,pid):
    product = Product.objects.get(id=pid)
    description = product.description
    context = {"description":description}
    return render(request, 'catalogue/product_description.html', context)            
        
        
def floatformat(flt):
    if flt:
        try:
            return "%.2f" % flt
        except:
            return flt
    else:
        return flt

# class UserSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User  # 定义关联的 Model
#         fields = ('id', 'username')  # 指定返回的 fields

# class RechargeSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = UserMoneyChange
#         fields = ('id', 'user', 'trade_type', 'status', 'price')

#     def restore_object(self, attrs, instance=None):
#         """
#         创建或更新一个snippet实例, 返回该snippet实例

#         如果不定义该function, 则反序列化时将返回一个包括所有field的dict
#         """
#         if instance:
#             # 更新已存在的snippet实例
#             instance.title = attrs.get('title', instance.title)
#             instance.code = attrs.get('code', instance.code)
#             instance.linenos = attrs.get('linenos', instance.linenos)
#             instance.language = attrs.get('language', instance.language)
#             instance.style = attrs.get('style', instance.style)
#             return instance

#         # Create new instance
#         return Snippet(**attrs)
