# -*- coding: utf-8 -*-
import socket
from datetime import datetime, timedelta
import time

import django.utils.timezone
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from stars.apps.api.common.views import CommonPermissionAPIView
from stars.apps.api.error_result import err_result, ERROR_PARAM, SYSTEM_ERR_CODE, DOES_NOT_EXIST_CODE, SUCCESS_CODE
from stars.apps.api.finance.wx.WxPayApi import WxAndroidPayApi, WxIosPayApi
from stars.apps.api.finance.wx.common_const import WxAndroidPaymentConstData, WxIosPaymentConstData, \
    WxMobilePaymentConstData
from stars.apps.commission.models import ProductOrder
from stars.apps.customer.finance.models import WxPaymentTradeOrder
from stars.apps.customer.finance.utils import notify_order_pay_success
from stars.apps.customer.finance.weixin.log import wx_pay_log as logging
from stars.apps.customer.finance.weixin.notify import Notify
from stars.apps.customer.finance.weixin.utils import checkSign
from stars.apps.customer.finance.weixin.wx_pay_api import WxNativePayApi


class AppWxPaymentView(CommonPermissionAPIView):

    __HAS_PAYED = '640'
    __REMAINING_SECONDS = WxMobilePaymentConstData.TRADE_EXPIRE_SECONDS
    __DEVICE_INFO = ''
    __TRADE_TYPE = 'APP'

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
                                    total_fee=1, #int(product_order.amount * 100),
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
    def __unified_order(self, wx_api, trade_order, open_id=''):
        m = {}
        # 必需
        m['body'] = trade_order.body if trade_order.body else u'蓝图商品'   # 商品或支付单简要描述
        m['out_trade_no'] = trade_order.trade_no  # 商户系统内部的订单号,32个字符内、可包含字母
        m['total_fee'] = trade_order.total_fee  # 总金额，整数。交易金额默认为人民币交易，接口中参数支付金额单位为【分】，参数值不能带小数。对账单中的交易金额单位为【元】
        m['trade_type'] = 'APP'
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
        result = wx_api.unified_order(m)
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

    @classmethod
    def __isValidIp(cls, address):
        try:
            socket.inet_aton(address)
            return True
        except:
            return False

    def post(self, request, data_format=None, *args, **kwargs):
        user = request.user
        data = request.data

        # ①不存在----记录，
        # ②已经撤单---记录   ---- 购买不能撤单
        try:
            order_no = data['order_no']
            # order_no = '123'
            if not order_no:
                raise ValueError

            wx_config = {'android': WxAndroidPaymentConstData, 'ios': WxIosPaymentConstData}[data['os_type']]
            wx_api = {'android': WxAndroidPayApi, 'ios': WxIosPayApi}[data['os_type']]

            spbill_create_ip = data.get('ip', wx_config.IP)

            if self.__isValidIp(spbill_create_ip) is False:
                raise ValueError()
        except (KeyError, ValueError):
            return Response(err_result(ERROR_PARAM, u'参数错误').msg)

        try:

            with transaction.atomic():
                # 根据订单号取订单
                product_order = ProductOrder.objects.select_for_update().get(order_no=order_no, user=user)
                # ③已经支付---不做处理
                if self.has_payed(product_order):
                    return Response(err_result(self.__HAS_PAYED, u'订单已支付').msg)
                # ④支付中
                # elif self.is_paying(product_order):
                #     return HttpResponseBadRequest(u'订单支付进行中')
                # ⑤未支付----修改交易单状态，记录，通知
                # 生成交易单
                wx_trade_order = self.__get_or_create_trade(product_order,
                                                            appid=wx_config.APP_ID,
                                                            mch_id=wx_config.MCH_ID,
                                                            spbill_create_ip=wx_config.IP)
                wx_trade_order = WxPaymentTradeOrder.objects.select_for_update().get(pk=wx_trade_order.pk)

                now = datetime.today() if wx_trade_order.time_expire.tzinfo is None else django.utils.timezone.now()
                if wx_trade_order.order_status == 9 or (wx_trade_order.order_status in (0,1,4) and (not wx_trade_order.code_url or wx_trade_order.time_expire+timedelta(minutes=2) < now)):
                    try:
                        if wx_trade_order.time_expire <= now:
                            wx_trade_order.start_time = django.utils.timezone.now()
                            wx_trade_order.time_expire = wx_trade_order.start_time + timedelta(seconds=self.__REMAINING_SECONDS)
                            wx_trade_order.code_url = ''
                            wx_trade_order.save()
                        # 调用统一下单api
                        fromWxData = self.__unified_order(wx_api, wx_trade_order)

                        wx_trade_order.wx_return_code = fromWxData['return_code']
                        wx_trade_order.wx_return_msg = fromWxData['return_msg']
                        wx_trade_order.wx_response = fromWxData
                        if fromWxData['return_code'] == 'SUCCESS':  #通信成功
                            if not fromWxData.get("appid") or not fromWxData.get("mch_id"):
                                raise Exception(message='统一下单失败，返回值缺少必要参数')
                            if fromWxData['result_code'] == 'SUCCESS':
                                wx_trade_order.order_status = 2
                                wx_trade_order.wx_prepay_id = fromWxData.get('prepay_id', '')
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
                        return Response(err_result(SYSTEM_ERR_CODE,  u'统一下单失败').msg)

                elif wx_trade_order.order_status == 2: #预支付中，查询订单状态
                    r = AppWxOrderQueryPayStatusView.query_and_set_order(wx_api, wx_trade_order)
                    if r:
                        wx_trade_order = r

                if wx_trade_order.order_status == 3:  # 已经支付
                    notify_order_pay_success(product_order)
                    return Response(err_result(self.__HAS_PAYED, u'订单已支付').msg)
                elif wx_trade_order.order_status == 9:
                    return Response(err_result(SYSTEM_ERR_CODE, u'统一下单失败').msg)
                else:
                    m = err_result(SUCCESS_CODE, u'统一下单成功').msg
                    m['data'] = {'prepayid': wx_trade_order.wx_prepay_id, 'appid': wx_trade_order.appid, 'partnerid': wx_trade_order.mch_id,
                    'package': 'Sign=WXPay',
                    'noncestr': wx_api.generate_nonce_str(),
                    'timestamp': int(time.time())}
                    m['data']['sign'] = wx_api.makeSign(m['data'])
                    return Response(m)

        except ProductOrder.DoesNotExist as e:
            logging.exception(e)
            return Response(err_result(DOES_NOT_EXIST_CODE, u'订单不存在').msg)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'统一下单失败').msg)


class AppWxOrderQueryPayStatusView(APIView, Notify):
    """
    微信订单查询
    根据查询结果和本地订单状态，更新本地订单状态
    """

    __wx_pay_trade_status = {
        'PAYERROR': 1,
        'SUCCESS': 3,
        'NOTPAY': 4,
        'CLOSED': 5,
        'REVOKED': 6,
        'USERPAYING': 7,
        'REFUND': 8
    }
    __HAS_PAYED = '640'
    __PAY_FAILED = '641'
    __NO_PAY = '642'
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
        user = request.user

        try:
            wx_api = {'android': WxAndroidPayApi, 'ios': WxIosPayApi}[data['os_type']]

            if data.get('trade_no'):
                trade = WxPaymentTradeOrder.objects.get(trade_no=data.get('trade_no'), user=user)
            elif data.get('transaction_id'):
                trade = WxPaymentTradeOrder.objects.get(transaction_id=data.get('transaction_id'), user=user)
            elif data.get('product_order_no'):
                trade = WxPaymentTradeOrder.objects.get(product_id=data.get('product_order_no'), user=user)
            else:
                return Response(err_result(ERROR_PARAM, u'参数错误').msg)

            if trade.order_status == 3:
                return Response(err_result(self.__HAS_PAYED, u'支付完成'))

            with transaction.atomic():
                trade = WxPaymentTradeOrder.objects.select_for_update().get(pk=trade.pk)

                self.query_and_set_order(wx_api=wx_api, trade=trade)

            if trade.order_status == 3:
                return Response(err_result(self.__HAS_PAYED, u'支付完成'))
            elif trade.order_status == 1:
                return Response(err_result(self.__PAY_FAILED, u'支付失败'))
            else:
                return Response(err_result(self.__NO_PAY, u'未支付'))

        except WxPaymentTradeOrder.DoesNotExist as e:
            logging.exception(e)
            return Response(err_result(DOES_NOT_EXIST_CODE, u'订单不存在'))
        except ProductOrder.DoesNotExist as e:
            logging.exception(e)
            return Response(err_result(DOES_NOT_EXIST_CODE, u'订单不存在'))
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'订单查询失败').msg)

    @classmethod
    def query_and_set_order(cls, wx_api, trade):
        if trade.transaction_id:
            fromWxData = wx_api.order_query({'transaction_id': trade.transaction_id})
        else:
            fromWxData = wx_api.order_query({'out_trade_no': trade.trade_no})
        if fromWxData['return_code'] == 'SUCCESS':

            if fromWxData["result_code"] == "SUCCESS":
                if checkSign(fromWxData) == 0:

                    trade.order_status = cls.__wx_pay_trade_status.get(fromWxData['trade_state'], 1)

                    trade.trade_status_desc = fromWxData.get('trade_state_desc', '')
                    if not trade.transaction_id and 'transatcion_id' in fromWxData:
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
                    notify_order_pay_success(product_order)

                trade.save(force_update=True)
            return trade
        else:
            return None
