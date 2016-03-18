# -*- coding: utf-8 -*-
import base64
import logging

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

from stars.apps.api.common.views import CommonPermissionAPIView
from stars.apps.api.error_result import err_result, ERROR_PARAM, SYSTEM_ERR_CODE, SUCCESS_CODE, DOES_NOT_EXIST_CODE
from stars.apps.commission.models import ProductOrder
from stars.apps.customer.finance.alipay.work import AliPayRequest
from stars.apps.customer.finance.models import AliPaymentTradeOrder


class AppAliPaymentView(CommonPermissionAPIView):

    __HAS_PAYED = '640'


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

            os_type = data['os_type']

            if os_type not in ('android', 'ios'):
                raise ValueError()

        except (KeyError, ValueError):
            return Response(err_result(ERROR_PARAM, u'参数错误').msg)

        try:
            r = AliPayRequest().get(order_no=order_no, user=user, pay_service_type='mobile', sign_type='RSA')
            m = err_result(SUCCESS_CODE, u'订单生成成功').msg
            m['data'] = r['form']['params']
            m['data']['sign'] = m['data']['sign']
            m['sign_string'] = r['form']['sign_string']
            if isinstance(m['sign_string'], str):
                m['sign_string'] = m['sign_string'].decode('utf-8')

            return Response(m)
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'订单生成失败').msg)


class AppAliOrderQueryPayStatusView(CommonPermissionAPIView):
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
            if data.get('out_trade_no'):
                trade = AliPaymentTradeOrder.objects.get(trade_no=data.get('out_trade_no'), user=user)
            elif data.get('order_no'):
                trade = AliPaymentTradeOrder.objects.get(order_no=data.get('order_no'), user=user)
            else:
                return Response(err_result(ERROR_PARAM, u'参数错误').msg)

            if trade.order_status == 3:
                return Response(err_result(self.__HAS_PAYED, u'支付完成'))

            with transaction.atomic():
                trade = AliPaymentTradeOrder.objects.select_for_update().get(pk=trade.pk)

                AliPayRequest.query_and_set_order(trade=trade)

            if trade.order_status == 3:
                return Response(err_result(self.__HAS_PAYED, u'支付完成'))
            elif trade.order_status == 1:
                return Response(err_result(self.__PAY_FAILED, u'支付失败'))
            else:
                return Response(err_result(self.__NO_PAY, u'未支付'))

        except AliPaymentTradeOrder.DoesNotExist as e:
            logging.exception(e)
            return Response(err_result(DOES_NOT_EXIST_CODE, u'订单不存在'))
        except ProductOrder.DoesNotExist as e:
            logging.exception(e)
            return Response(err_result(DOES_NOT_EXIST_CODE, u'订单不存在'))
        except Exception as e:
            logging.exception(e)
            return Response(err_result(SYSTEM_ERR_CODE, u'订单查询失败').msg)




