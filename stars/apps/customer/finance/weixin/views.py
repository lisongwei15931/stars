# -*- coding: utf-8 -*-
import hashlib
import os
import uuid
from datetime import datetime, timedelta

import django.utils.timezone
import qrcode
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.generic import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from stars import settings
from stars.apps.commission.models import ProductOrder
from stars.apps.customer.finance.models import WxPaymentBill, WxPaymentTradeOrder
from stars.apps.customer.finance.utils import notify_order_pay_success
from stars.apps.customer.finance.weixin.common_const import WxNativePaymentConstData
from stars.apps.customer.finance.weixin.notify import Notify
from stars.apps.customer.finance.weixin.utils import checkSign
from stars.apps.customer.finance.weixin.wx_pay_api import WxNativePayApi

from stars.apps.customer.finance.weixin.log import wx_pay_log as logging

def generate_qrcode(data):
    """

    :param data:
    :return: url,路径
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image()
    m = hashlib.md5()
    m.update(uuid.uuid4().bytes)
    file_name = m.hexdigest()+'.png'
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    img.save(file_path)
    return settings.MEDIA_URL+file_name, file_path


class WxPayHomeView(View):

    __optional_items = {'gender', 'tel_no', 'fax_no', 'mobile', 'post_code', 'address', 'email'}
    __REMAINING_SECONDS = WxNativePaymentConstData.TRADE_EXPIRE_SECONDS
    __TRADE_TYPE = 'NATIVE'
    __DEVICE_INFO = 'WEB'

    def __get_or_create_trade(self, product_order, *args, **kwargs):
        """
        生成微信支付单
        :return:
        """
        try:
            trade = WxPaymentTradeOrder.objects.get(product_id=product_order.order_no)
            return trade
        except WxPaymentTradeOrder.DoesNotExist:
            pass

        now = django.utils.timezone.now()
        expire_time = now + timedelta(seconds=self.__REMAINING_SECONDS)
        trade_no = WxNativePayApi.generate_out_trade_no(product_order.user_id)
        trade = WxPaymentTradeOrder(appid=kwargs['appid'],
                                    mch_id=kwargs['mch_id'],
                                    trade_no=trade_no,
                                    product_id=product_order.order_no,
                                    uid=product_order.user_id,
                                    total_fee=int(product_order.amount * 100),
                                    device_info=self.__DEVICE_INFO,
                                    body=product_order.description if product_order.description else u'蓝图商品',
                                    detail=product_order.detail,
                                    spbill_create_ip=kwargs['spbill_create_ip'],
                                    start_time=now,
                                    time_expire=expire_time,
                                    trade_type=self.__TRADE_TYPE,
                                    original_source=0
                                    )

        trade.save(force_insert=True)
        return trade

    # 统一下单
    def __unified_order(self, trade_order, open_id=''):
        m = {}
        # 必需
        m['body'] = trade_order.body if trade_order.body else u'蓝图商品'   # 商品或支付单简要描述
        m['out_trade_no'] = trade_order.trade_no  # 商户系统内部的订单号,32个字符内、可包含字母
        m['total_fee'] = trade_order.total_fee  # 总金额，整数。交易金额默认为人民币交易，接口中参数支付金额单位为【分】，参数值不能带小数。对账单中的交易金额单位为【元】
        m['trade_type'] = 'NATIVE'
        m['spbill_create_ip'] = trade_order.spbill_create_ip

        # 非必要
        m['device_info'] = trade_order.device_info  # 终端设备号(门店号或收银设备ID)，注意：PC网页或公众号内支付请传"WEB"
        m['detail'] = trade_order.detail  # 商品名称明细列表
        m['attach'] = ''  # 附加数据，在查询trade_orderAPI和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据
        m['fee_type'] = 'CNY'
        m['time_start'] = django.utils.timezone.localtime(trade_order.start_time).strftime('%Y%m%d%H%M%S')  # 订单生成时间，格式为yyyyMMddHHmmss
        m['time_expire'] = django.utils.timezone.localtime(trade_order.time_expire).strftime('%Y%m%d%H%M%S')  # 订单失效时间，格式为yyyyMMddHHmmss。最短失效时间间隔必须大于5分钟
        m['product_id'] = trade_order.product_id  # trade_type=NATIVE，此参数必传。此id为二维码中包含的商品ID，商户自行定义。
        # m['openid'] =   # String(128)  trade_type=JSAPI，此参数必传，用户在商户appid下的唯一标识。下单前需要调用【网页授权获取用户信息】接口获取到用户的Openid。
        m['limit_pay'] = 'no_credit'

        # 签名
        result = WxNativePayApi.unified_order(m)
        return result

    def has_payed(self, product_order):
        """
        订单是否已经支付
        :return:
        """
        return product_order.has_payed()

    def is_paying(self, product_order):
        """
        订单是否支付中
        :return:
        """
        return product_order.is_paying()

    def get(self, request, data_format=None, *args, **kwargs):
        # user = request.user
        data = request.GET
        if data_format == 'json' or data.get('data_format') == 'json':
            is_json = True
        else:
            is_json = False

        # ①不存在----记录，
        # ②已经撤单---记录   ---- 购买不能撤单
        try:
            order_no = data['order_no']
            # order_no = '123'
            if not order_no:
                raise ValueError
        except (KeyError, ValueError):
            return HttpResponseBadRequest(u'缺少订单号')

        try:

            with transaction.atomic():
                # 根据订单号取订单
                product_order = ProductOrder.objects.select_for_update().get(order_no=order_no)
                # ③已经支付---不做处理
                if self.has_payed(product_order):
                    if is_json:
                        return JsonResponse({'msg': u'订单已支付', 'code': 1,})
                    else:
                        return HttpResponseBadRequest(u'订单已支付')
                # ④支付中
                # elif self.is_paying(product_order):
                #     return HttpResponseBadRequest(u'订单支付进行中')
                # ⑤未支付----修改交易单状态，记录，通知
                # 生成交易单
                wx_trade_order = self.__get_or_create_trade(product_order,
                                                            appid=WxNativePaymentConstData.APP_ID,
                                                            mch_id=WxNativePaymentConstData.MCH_ID,
                                                            spbill_create_ip=WxNativePaymentConstData.IP)
                wx_trade_order = WxPaymentTradeOrder.objects.select_for_update().get(pk=wx_trade_order.pk)

                now = datetime.today() if wx_trade_order.time_expire.tzinfo is None else django.utils.timezone.now()
                if wx_trade_order.order_status==9 or (wx_trade_order.order_status in (0,1,4) and (not wx_trade_order.code_url or wx_trade_order.time_expire < now)):
                    try:
                        if wx_trade_order.time_expire <= now:
                            wx_trade_order.start_time = django.utils.timezone.now()
                            wx_trade_order.time_expire = wx_trade_order.start_time + timedelta(seconds=self.__REMAINING_SECONDS)
                            wx_trade_order.code_url = ''
                            wx_trade_order.save()
                        # 调用统一下单api
                        fromWxData = self.__unified_order(wx_trade_order)

                        wx_trade_order.wx_return_code = fromWxData['return_code']
                        wx_trade_order.wx_return_msg = fromWxData['return_msg']
                        wx_trade_order.wx_response = fromWxData
                        if fromWxData['return_code'] == 'SUCCESS':  #通信成功 #交易成功
                            if not fromWxData.get("appid") or not fromWxData.get("mch_id") or not fromWxData.get("code_url"):
                                raise Exception(message='统一下单失败，返回值缺少必要参数')
                            if fromWxData['result_code'] == 'SUCCESS':
                                wx_trade_order.order_status = 2
                                wx_trade_order.wx_prepay_id = fromWxData.get('prepay_id', '')
                                wx_trade_order.code_url = fromWxData.get('code_url')
                                # product_order.status = 2
                                product_order.pay_type = 2
                                product_order.save()
                            else:
                                wx_trade_order.order_status = 9

                            wx_trade_order.wx_result_code = fromWxData['result_code']
                            wx_trade_order.wx_err_code = fromWxData.get('err_code', '')
                            wx_trade_order.wx_err_code_des = fromWxData.get('err_code_des', '')
                        else:
                            wx_trade_order.order_status = 9

                        wx_trade_order.save()
                    except Exception as e:
                        logging.exception(u'统一下单失败 :' + e.message)
                        wx_trade_order.comment = u'统一下单失败'
                        wx_trade_order.order_status = 9
                        wx_trade_order.save()
                        if is_json:
                            return JsonResponse({'msg': u'二维码生成失败', 'code': -1,})
                        else:
                            return HttpResponse(u'二维码生成失败')

                    if not wx_trade_order.code_url or wx_trade_order.order_status == 9:
                        if wx_trade_order.wx_err_code in ['ORDERPAID', 'ORDERCLOSED', 'OUT_TRADE_NO_USED']:
                            return HttpResponse(WxNativePaymentConstData.UnifiedOrderErrorCodeMsg[wx_trade_order.wx_err_code])
                        else:
                            logging.exception('统一下单失败')
                            if is_json:
                                return JsonResponse({'msg': u'二维码生成失败', 'code': -1,})
                            else:
                                return HttpResponse(u'二维码生成失败')
                elif wx_trade_order.order_status == 2: #预支付中，查询订单状态
                    r = WxOrderQueryPayStatusView.query_and_set_order(wx_trade_order)
                    if r:
                        wx_trade_order = r

                if wx_trade_order.order_status == 3:  # 已经支付
                    notify_order_pay_success(product_order)
                    if is_json:
                        return JsonResponse({'msg': u'已经支付', 'code': 1,})
                    else:
                        return HttpResponse(u'已经支付')

                ctx = {'msg': '', 'code': 0,}
                ctx['order_no'] = order_no
                ctx['price'] = product_order.amount
                now = datetime.today() if wx_trade_order.time_expire.tzinfo is None else django.utils.timezone.now()
                ctx['remaining_seconds'] = (wx_trade_order.time_expire-now).seconds
                if ctx['remaining_seconds']<0:
                    ctx['remaining_seconds'] = 0
                if not wx_trade_order.code_url_img_url or wx_trade_order.time_expire >= django.utils.timezone.now() or not os.path.exists(wx_trade_order.code_url_img_path):
                    prepay_url = wx_trade_order.code_url
                    wx_trade_order.code_url_img_url, wx_trade_order.code_url_img_path = generate_qrcode(prepay_url)
                    wx_trade_order.save()

            ctx['qr_code_url'] = wx_trade_order.code_url_img_url

            tpl = 'customer/finance/wx/pay/pay_home.html'

            if is_json:
                return JsonResponse(ctx)
            else:
                return render(request, tpl, ctx)
        except ProductOrder.DoesNotExist:
            if is_json:
                return JsonResponse({'msg': u'订单不存在', 'code': -2,})
            else:
                return HttpResponseBadRequest(u'订单不存在')


# class WxPrePayNotificationView(APIView, Notify):
#     __success_data = '<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml> '
#
#     def __create_order(self, product_order):
#         """
#         生成微信支付单
#         :return:
#         """
#         #TODO
#         pass
#
#     def __echo_prepay_id(self, prepay_id):
#         """
#         商户后台系统将prepay_id返回给微信支付系统。
#         :return:
#         """
#         m = {}
#         m["return_code"] = "SUCCESS"
#         m["return_msg"] = "OK"
#         m['appid'] = WxNativePaymentConstData.APP_ID
#         m['mch_id'] = WxNativePaymentConstData.MCH_ID
#         m["nonce_str"] = WxNativePayApi.generate_nonce_str()
#         m["prepay_id"] = prepay_id
#         m["result_code"] = "SUCCESS"
#         m["err_code_des"] = "OK"
#         m["sign"] = makeSign(m)
#         content = makeXml(m)
#         return HttpResponse(content, content_type='text/xml')
#
#     def __get_product_order(self, order_id):
#         # FIXME
#         return object()
#
#     @staticmethod
#     def __getExpireTime():
#         return (datetime.now()+timedelta(hours=2)).strftime('%Y%m%d%H%M%S')
#
#     # 统一下单
#     def __unified_order(self, product_order, out_trade_no, open_id=''):
#         m = {}
#         # 必需
#         m['body'] = product_order.descript    # 商品或支付单简要描述
#         m['out_trade_no'] = out_trade_no  # 商户系统内部的订单号,32个字符内、可包含字母
#         m['total_fee'] = product_order.total_fee  # 总金额，整数。交易金额默认为人民币交易，接口中参数支付金额单位为【分】，参数值不能带小数。对账单中的交易金额单位为【元】
#         m['trade_type'] = 'NATIVE'
#
#         # 非必要
#         m['device_info'] = WxNativePaymentConstData.DEVICE_INFO  # 终端设备号(门店号或收银设备ID)，注意：PC网页或公众号内支付请传"WEB"
#         m['detail'] = product_order.detail  # 商品名称明细列表
#         m['attach'] = ''  # 附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据
#         m['fee_type'] = 'CNY'
#         m['time_start'] = datetime.today().strftime('%Y%m%d%H%M%S')  # 订单生成时间，格式为yyyyMMddHHmmss
#         m['time_expire'] = WxPrePayNotificationView.__getExpireTime()  # 订单失效时间，格式为yyyyMMddHHmmss。最短失效时间间隔必须大于5分钟
#         m['product_id'] = product_order.id  # trade_type=NATIVE，此参数必传。此id为二维码中包含的商品ID，商户自行定义。
#         # m['openid'] =   # String(128)  trade_type=JSAPI，此参数必传，用户在商户appid下的唯一标识。下单前需要调用【网页授权获取用户信息】接口获取到用户的Openid。
#         m['limit_pay'] = 'no_credit'
#
#         # 签名
#         result = WxNativePayApi.unified_order(m)
#         return result
#
#     def post(self, request, format=None):
#         """
#         微信支付系统收到客户端请求，发起对商户后台系统支付回调URL的调用。调用请求将带productid和用户的openid等参数，
#         并要求商户系统返回交易会话标识（prepay_id）
#         :param format:
#         :return:
#         """
#         notify_data = self.get_notify_data(request)
#         if isinstance(notify_data, HttpResponse):
#             return notify_data
#         elif notify_data["return_code"] != "SUCCESS":
#             return HttpResponse('<xml><return_code><![CDATA[FAIL]]></return_code>'
#                                 '<return_msg><![CDATA[]]></return_msg></xml>', content_type='text/xml')
#         order_id = notify_data.get('product_id')
#         if not order_id:
#             return HttpResponse('<xml><return_code><![CDATA[FAIL]]></return_code>'
#                                 '<return_msg><![CDATA[回调数据异常,缺少必要的product_id参数]]></return_msg></xml>',
#                                 content_type='text/xml')
#
#         product_order = self.__get_product_order(order_id)
#
#         # ①不存在----记录，
#         if not product_order:
#             # TODO
#             pass
#
#         # ②已经撤单---记录   ---- 购买不能撤单
#         # ③已经支付---不做处理
#         # ④未支付----修改交易单状态，记录，通知
#
#         # TODO
#         # 生成交易单
#         wx_trade_order = self.__create_order(product_order)
#
#         try:
#             # 调用统一下单api
#             r = self.__unified_order(product_order, out_trade_no='')
#             if not r.get("appid") or not r.get("mch_id") or not r.get("prepay_id"):
#                 raise Exception(message='统一下单失败，返回值缺少必要参数')
#
#             return self.__echo_prepay_id(r.get('prepay_id'))
#
#         except Exception as e:
#             logging.exception('统一下单失败 :' + e.message)
#             return HttpResponse('<xml><return_code><![CDATA[FAIL]]></return_code>'
#                                 '<return_msg>![CDATA[统一下单失败]]</return_msg></xml>',
#                                 content_type='text/xml')



class WxOrderQueryPayStatusView(APIView, Notify):
    """
    微信订单查询
    根据查询结果和本地订单状态，更新本地订单状态
    """
    __success_data = '<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml> '

    __wx_pay_trade_status = {
        'PAYERROR': 1,
        'SUCCESS': 3,
        'NOTPAY': 4,
        'CLOSED': 5,
        'REVOKED': 6,
        'USERPAYING': 7,
        'REFUND': 8
    }

    # @staticmethod
    # def __get_product_order(order_no):
    #     product_order = ProductOrder.objects.get(order_no=order_no)
    #     return product_order

    def get(self, request, format=None):
        """
        接收微信支付后台发送的支付结果并对订单有效性进行验证，将验证结果反馈给微信支付后台
        根据支付结果修改交易单，通知订单状态发生改变
        :param format:
        :return:
        """
        data = request.GET

        try:
            if data.get('trade_no'):
                trade = WxPaymentTradeOrder.objects.get(trade_no=data.get('trade_no'))
            elif data.get('transaction_id'):
                trade = WxPaymentTradeOrder.objects.get(transaction_id=data.get('transaction_id'))
            elif data.get('product_order_no'):
                trade = WxPaymentTradeOrder.objects.get(product_id=data.get('product_order_no'))
            else:
                return HttpResponseBadRequest('缺少必要的参数')

            if trade.uid != request.user.id:
                return HttpResponseBadRequest('没有权限')

            if not trade.order_status in (0, 2):
                return Response({'order':  trade, 'ret_status':  {'status': 0, 'msg': u'成功'}}, status=status.HTTP_200_OK)

            with transaction.atomic():
                trade = WxPaymentTradeOrder.objects.select_for_update().get(pk=trade.pk)

                self.query_and_set_order(trade)

        except WxPaymentTradeOrder.DoesNotExist as e:
            logging.exception(e)
            return HttpResponse('订单不存在')
        except ProductOrder.DoesNotExist as e:
            logging.exception(e)
            return HttpResponse(u'订单不存在')
        except Exception as e:
            logging.exception(e)
            return HttpResponse(u'查询失败', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def query_and_set_order(trade):
        if trade.transaction_id:
            fromWxData = WxNativePayApi.order_query({'transaction_id': trade.transaction_id})
        else:
            fromWxData = WxNativePayApi.order_query({'out_trade_no': trade.trade_no})
        if fromWxData['return_code'] == 'SUCCESS':

            if fromWxData["result_code"] == "SUCCESS":
                if checkSign(fromWxData) == 0:

                    trade.order_status = WxOrderQueryPayStatusView.__wx_pay_trade_status.get(fromWxData['trade_state'], 1)

                    trade.trade_status_desc = fromWxData.get('trade_state_desc', '')
                    if not trade.transaction_id and 'transaction_id' in fromWxData:
                        trade.transaction_id = fromWxData['transaction_id']
                else:
                    logging.error('from weixin order query: sign error: ' + trade.trade_no)
                    logging.error(fromWxData)
                    return None
            else:
                trade.order_status = 1

            if fromWxData.get('time_end'):
                trade.end_time = datetime.strptime(fromWxData['time_end'], '%Y%m%d%H%M%S')
            trade.wx_result_code = fromWxData['result_code']
            trade.wx_err_code = fromWxData.get('err_code', '')
            trade.wx_err_code_des = fromWxData.get('err_code_des', '')

            with transaction.atomic():  # 支付成功
                if trade.order_status == 3 and trade.is_order_over is False:
                    trade.wx_response = fromWxData
                    trade.is_order_over = True
                    # 通知订单支付成功
                    product_order = ProductOrder.objects.select_for_update().get(order_no=trade.product_id)
                    # product_order.status = 2
                    # product_order.pay_type = 2
                    # product_order.save()
                    notify_order_pay_success(product_order)

                trade.save(force_update=True)
            return trade
        else:
            return None


class WxPayResultNotificationView(APIView, Notify):
    """
    支付结果通知回调处理类
    负责接收微信支付后台发送的支付结果并对订单有效性进行验证，将验证结果反馈给微信支付后台
    """
    __success_data = '<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml> '

    # 查询订单
    def __query_order(self, transaction_id):
        data = {"transaction_id": transaction_id}
        res = WxNativePayApi.order_query(data)
        if (res.get("return_code") == "SUCCESS" and res.get("result_code") == "SUCCESS"):
            return True
        else:
            return False


    def post(self, request, format=None):
        """
        接收微信支付后台发送的支付结果并对订单有效性进行验证，将验证结果反馈给微信支付后台
        根据支付结果修改交易单，通知订单状态发生改变
        :param format:
        :return:
        """

        try:
            logging.info(request.data)

            notify_data = self.get_notify_data(request.data)
            if isinstance(notify_data, HttpResponse):
                return notify_data

            transaction_id = notify_data.get('transaction_id')
            if not transaction_id:
                return HttpResponse('<xml><return_code><![CDATA[FAIL]]></return_code>'
                                    '<return_msg><![CDATA[支付结果中微信订单号不存在]]></return_msg></xml>')
            elif self.__query_order(transaction_id) == False:
                logging.error(u'订单查询失败' + str(notify_data))
                return HttpResponse('<xml><return_code><![CDATA[FAIL]]></return_code>'
                                    '<return_msg><![CDATA[订单查询失败]]></return_msg></xml>')

            if notify_data["return_code"] != "SUCCESS":
                data = '<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[通信失败]]></return_msg></xml>'
                return HttpResponse(data)

            trade_no = notify_data.get('out_trade_no')
            if not trade_no:
                logging.error(u'订单通知失败，缺少必要参数out_trade_no : ' + str(notify_data))
                return HttpResponse('<xml><return_code><![CDATA[FAIL]]></return_code>'
                                '<return_msg><![CDATA[缺少必要的参数：out_trade_no]]></return_msg></xml>')

            need_notify_order_success = False
            with transaction.atomic():
                trade = WxPaymentTradeOrder.objects.select_for_update().get(trade_no=trade_no)

                if trade.order_status not in (0, 2):
                    # 已经处理过，直接返回成功接收
                    return Response(data=self.__success_data, status=status.HTTP_200_OK)

                product_order = ProductOrder.objects.select_for_update().get(order_no=trade.product_id)
                trade.transaction_id = notify_data.get('transaction_id')
                if not trade.prepay_id and notify_data.get('prepay_id'):
                    trade.prepay_id = notify_data.get('prepay_id')
                if notify_data['result_code'] == 'SUCCESS':
                    trade.order_status = 3
                    product_order.status = 2
                    product_order.pay_type = 2
                else:
                    trade.order_status = 1
                    product_order.status = 3
                if notify_data.get('time_end'):
                    trade.end_time = datetime.strptime(notify_data['time_end'], '%Y%m%d%H%M%S')
                trade.wx_result_code = notify_data['result_code']
                trade.wx_err_code = notify_data.get('err_code', '')
                trade.wx_err_code_des = notify_data.get('err_code_des', '')
                trade.wx_response = notify_data

                if trade.order_status == 3 and trade.is_order_over is False:
                    trade.is_order_over = True
                    need_notify_order_success = True

                trade.save(force_update=True)
                product_order.save()

            if need_notify_order_success:
                # 通知订单支付成功
                notify_order_pay_success(product_order)
            content = '<xml><return_code><![CDATA[SUCCESS]]></return_code></xml>'
            return HttpResponse(content)
        except WxPaymentTradeOrder.DoesNotExist as e:
            logging.exception(e)
            return HttpResponse('<xml><return_code><![CDATA[FAIL]]></return_code>'
                                '<return_msg><![CDATA[该订单号不存在]]></return_msg></xml>')
        except ProductOrder.DoesNotExist as e:
            logging.exception(e)
            return HttpResponse('<xml><return_code><![CDATA[FAIL]]></return_code>'
                                '<return_msg><![CDATA[该订单不存在]]></return_msg></xml>')
        except Exception as e:
            logging.exception(e)
            return HttpResponse(body='<xml><return_code><![CDATA[FAIL]]></return_code><return_msg></return_msg></xml>', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WxDownloadBillView(APIView):
    """
    1、微信侧未成功下单的交易不会出现在对账单中。支付成功后撤销的交易会出现在对账单中，跟原支付单订单号一致，bill_type为REVOKED；
    2、微信在次日9点启动生成前一天的对账单，建议商户10点后再获取；
    3、对账单中涉及金额的字段单位为“元”。
    """

    # 当日所有订单
    # 交易时间,公众账号ID,商户号,子商户号,设备号,微信订单号,商户订单号,用户标识,交易类型,交易状态,付款银行,货币种类,总金额,代金券或立减优惠金额,
    ## 微信退款单号,商户退款单号,退款金额,代金券或立减优惠退款金额，退款类型，退款状态,
    # 商品名称,商户数据包,手续费,费率
    __ALL_BILL_HEAD = ['trade_time', 'appid', 'mch_id', 'sub_mch_id', 'device_no', 'wx_transaction_id', 'trade_no',
                           'open_id', 'trade_type', 'trade_status', 'bank_type', 'fee_type', 'total_fee', 'coupon_fee',
                            'wx_refund_no', 'mch_refund_no', 'refund_fee', 'refund_coupon_fee', 'refund_type', 'refund_status',
                          'trade_name', 'trade_attach', 'service_charges', 'rate']
    # 当日成功支付的订单
    # 交易时间,公众账号ID,商户号,子商户号,设备号,微信订单号,商户订单号,
    # 用户标识,交易类型,交易状态,付款银行,货币种类,总金额,代金券或立减优惠金额,
    ##
    #  商品名称,商户数据包,手续费,费率
    __SUCCESS_BILL_HEAD = ['trade_time', 'appid', 'mch_id', 'sub_mch_id', 'device_no', 'wx_transaction_id', 'trade_no',
                           'open_id', 'trade_type', 'trade_status', 'bank_type', 'fee_type', 'total_fee', 'coupon_fee',
                           'trade_name', 'trade_attach', 'service_charges', 'rate']

    # 当日退款的订单
    # 交易时间,公众账号ID,商户号,子商户号,设备号,微信订单号,商户订单号,用户标识,交易类型,交易状态,付款银行,货币种类,总金额,代金券或立减优惠金额,
    ## 退款申请时间,退款成功时间,微信退款单号,商户退款单号,退款金额,代金券或立减优惠退款金额,退款类型,退款状态,
    # 商品名称,商户数据包,手续费,费率
    __REFUND_BILL_HEAD = ['trade_time', 'appid', 'mch_id', 'sub_mch_id', 'device_no', 'wx_transaction_id', 'trade_no',
                           'open_id', 'trade_type', 'trade_status', 'bank_type', 'fee_type', 'total_fee', 'coupon_fee',
                            'refund_request_time', 'refund_success_time', 'wx_refund_no', 'mch_refund_no', 'refund_fee',
                          'refund_coupon_fee', 'refund_type', 'refund_status',
                          'trade_name', 'trade_attach', 'service_charges', 'rate']

    __HEAD = [u'交易时间',u'公众账号ID',u'商户号',u'子商户号',u'设备号',u'微信订单号',u'商户订单号',u'用户标识',u'交易类型',u'交易状态',u'付款银行',u'货币种类',u'总金额',u'代金券或立减优惠金额',u'退款申请时间',u'退款成功时间',u'微信退款单号',u'商户退款单号',u'退款金额',u'代金券或立减优惠退款金额',u'退款类型',u'退款状态',u'商品名称',u'商户数据包',u'手续费',u'费率']
    __COL_NAME = ['trade_time', 'appid', 'mch_id', 'sub_mch_id', 'device_no', 'wx_transaction_id', 'trade_no',
                           'open_id', 'trade_type', 'trade_status', 'bank_type', 'fee_type', 'total_fee', 'coupon_fee',
                            'refund_request_time', 'refund_success_time', 'wx_refund_no', 'mch_refund_no', 'refund_fee',
                          'refund_coupon_fee', 'refund_type', 'refund_status',
                          'trade_name', 'trade_attach', 'service_charges', 'rate']

    #已撤销的订单

    __BILL_HAED_COL_NAME = dict(zip(__HEAD, __COL_NAME))

    def get(self, request, format=None):
        """
        下载对账单
        :param format:
        :return: '成功’：0;'没有权限.',1;"参数错误.",-2;4:订单不存在.
        """
        try:
            bill_date = request.GET['bill_date']
            datetime.strptime(bill_date, '%Y%m%d')
            bill_type = request.GET.get('bill_type','ALL')
            if bill_type not in ['ALL', 'SUCCESS', 'REFUND', 'REVOKE']:
                raise ValueError
        except (KeyError, ValueError):
            return HttpResponseBadRequest(u'缺少必要的参数')

        # ALL，返回当日所有订单信息，默认值
        # SUCCESS，返回当日成功支付的订单
        # REFUND，返回当日退款订单
        # REVOKED，已撤销的订单
        bill_type = 'ALL'
        if bill_type == 'ALL':
            bill_types = ['SUCCESS', 'REFUND']  # 没有REVOKED类型下载
        else:
            bill_types = [bill_type]

        try:

            bills = []
            for bill_type in bill_types:
                params = {}
                params['bill_date'] = bill_date
                params['bill_type'] = bill_type

                # 向微信查询
                r = WxNativePayApi.download_bill(params)
                if isinstance(r, dict):
                    if r.get('return_msg') == 'No Bill Exist':
                        continue
                        # return HttpResponse(u'当天没有指定类型的对账单.')
                    else:
                        logging.exception(u'下载对账单({})失败：'.format(bill_type) + str(r))
                        return HttpResponse(u'下载对账单错误.', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                content = r.decode('utf-8')

                ls = content.splitlines()
                if len(ls) >= 4:
                    ls.pop()
                    ls.pop()
                    head = ls.pop(0)
                    head = head.split()
                    col_name = []
                    for item in head:
                        if self.__BILL_HAED_COL_NAME.get(item) and hasattr(WxPaymentBill, item):
                            col_name.append(self.__BILL_HAED_COL_NAME.get(item))

                    for l in ls:
                        bill = WxPaymentBill()
                        items = dict(zip(col_name, l.split(',`')))
                        for p in items.items():
                            setattr(bill, p[0], p[1])
                        bills.append(bill)

            if bills:
                WxPaymentBill.objects.bulk_create(bills)

                return HttpResponse(u'下载成功')
            else:
                return HttpResponse(u'当天没有指定类型的对账单.')

        except Exception as e:
            logging.exception(e)
            return HttpResponse(u'下载对账单错误.', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
