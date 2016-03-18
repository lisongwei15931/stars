# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from stars.apps.commission.models import ProductOrder
from stars.apps.customer.finance.alipay.log import ali_pay_log as logging
from stars.apps.customer.finance.alipay.notify import Notify
from stars.apps.customer.finance.alipay.work import AliPayRequest
from stars.apps.customer.finance.finance_exception import AliPayException
from stars.apps.customer.finance.models import AliPaymentTradeOrder
from stars.apps.customer.finance.utils import notify_order_pay_success
from stars.apps.customer.finance.views import PayResultView


class TestHomeView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        data = request.GET
        order_no = data['order_no']

        pay_service_type = data['pay_type']
        if pay_service_type not in {'direct_pay', 'bank_pay'}:
            raise ValueError
        if pay_service_type == 'bank_pay' and not data.get('bank_code', ''):
            raise ValueError

        tpl = 'customer/finance/ali/pay/test.html'
        ctx = AliPayRequest().get(order_no, user, pay_service_type, sign_type='MD5', bank_code=data.get('bank_code', ''))
        url = ctx['form']['action']+'&' + '&'.join(u'{}={}'.format(k,v) for k,v in ctx['form']['params'].items())
        # url = url.encode('utf8')

        # return render(request, tpl, ctx)
        return redirect(url)


class AliPayView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        data = request.GET
        order_no = data['order_no']

        pay_service_type = data.get('pay_type', 'direct_pay')
        if pay_service_type not in {'direct_pay', 'bank_pay'}:
            raise ValueError
        if pay_service_type == 'bank_pay' and not data.get('bank_code', ''):
            raise ValueError

        ctx = AliPayRequest().get(order_no, user, pay_service_type, sign_type='MD5', bank_code=data.get('bank_code', ''))
        url = ctx['form']['action']+'&' + '&'.join(u'{}={}'.format(k,v) for k,v in ctx['form']['params'].items())
        return redirect(url)


class AliPayResultReturnView(APIView, Notify):
    """
    支付结果同步通知回调处理类
    负责接收支付宝支付后台发送的支付结果并对订单有效性进行验证，将验证结果反馈给前台页面
    """

    def get(self, request, format=None):
        """
        接收支付宝支付后台发送的支付结果并对订单有效性进行验证，将验证结果反馈给前台页面
        根据支付结果修改交易单，通知订单状态发生改变
        :param format:
        :return:
        """

        try:
            logging.info(request.GET)

            notify_data = self.get_notify_data_and_verify(request.GET)

            transaction_id = notify_data.get('trade_no')
            if not transaction_id:
                return HttpResponse('failed')

            out_trade_no = notify_data.get('out_trade_no')
            if not out_trade_no:
                return HttpResponse(u'需要out_trade_no')
            need_notify_order_success = False
            with transaction.atomic():
                trade = AliPaymentTradeOrder.objects.select_for_update().get(out_trade_no=out_trade_no)

                if trade.order_status in (3, 9):
                    # 已经处理过，直接返回成功接收
                    return Response('success')

                product_order = ProductOrder.objects.select_for_update().get(order_no=trade.order_no)

                trade.notify_id = notify_data['notify_id']
                trade.notify_type = notify_data['notify_type']
                trade.notify_time = notify_data['notify_time']

                trade.transaction_id = notify_data.get('trade_no')

                if 'gmt_create' in notify_data:
                    trade.gmt_create = notify_data['gmt_create']
                if 'gmt_payment' in notify_data:
                    trade.gmt_payment = notify_data['gmt_payment']
                if 'gmt_close' in notify_data:
                    trade.gmt_close = notify_data['gmt_close']

                if 'bank_seq_no' in notify_data:
                    trade.bank_seq_no = notify_data['bank_seq_no']

                trade.ali_result_code = notify_data.get('result_code', '')
                trade.ali_err_code = notify_data.get('error', '')
                trade.ali_trade_status = notify_data.get('trade_status', '')
                if trade.ali_trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
                    trade.order_status = 3
                    need_notify_order_success = True
                    product_order.status = 2
                    product_order.pay_type = 2
                else:
                    trade.order_status = 1
                    product_order.status = 3

                trade.ali_response = notify_data
                trade.is_order_over = True
                trade.save(force_update=True)
                product_order.save()

            if need_notify_order_success:
                # 通知订单支付成功
                notify_order_pay_success(product_order)

            # ctx = {}
            # tpl = ''
            #PayResultView
            # return render(request, tpl, ctx)
            # return PayResultView.render_result(request, order_pk=product_order.pk)
            url = reverse('customer:finance-pay-result', kwargs={'order_pk': product_order.pk})
            return redirect(url)
        except AliPayException as e:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        except AliPaymentTradeOrder.DoesNotExist as e:
            logging.exception(e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        except ProductOrder.DoesNotExist as e:
            logging.exception(e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.exception(e)
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AliPayResultErrorNotificationView(View):
    """
    支付错误信息异步通知回调处理类
    负责接收支付宝支付后台发送的支付错误并对订单有效性进行验证，将验证结果反馈给支付宝支付后台
    """

    def post(self, request, format=None):
        """
        接收支付宝支付后台发送的支付结果并对订单有效性进行验证，将验证结果反馈给支付宝支付后台
        根据支付结果修改交易单
        :param format:
        :return:
        """
        try:
            logging.info(request.POST)
            notify_data = self.get_notify_data_and_verify(request.POST)

            out_trade_no = notify_data.get('out_trade_no')
            if not out_trade_no:
                return HttpResponse(u'需要out_trade_no')
            with transaction.atomic():
                trade = AliPaymentTradeOrder.objects.select_for_update().get(out_trade_no=out_trade_no)

                if trade.ali_trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
                    # 已经处理过，直接返回成功接收
                    return Response('success')

                product_order = ProductOrder.objects.select_for_update().get(order_no=trade.order_no)

                trade.order_status = 1
                trade.is_order_over = False
                trade.ali_err_code = notify_data.get('error', '')

                trade.ali_response = notify_data

                trade.save(force_update=True)

                if product_order.status in (0, 1):
                    product_order.status = 3
                product_order.save()

            url = reverse('customer:finance-pay-result', kwargs={'order_pk': product_order.pk})
            return redirect(url)
        except AliPayException as e:
            return HttpResponse('failed')

        except AliPaymentTradeOrder.DoesNotExist as e:
            logging.exception(e)
            return HttpResponse('failed>')
        except ProductOrder.DoesNotExist as e:
            logging.exception(e)
            return HttpResponse('failed')
        except Exception as e:
            logging.exception(e)
            return HttpResponse(body='failed')


class AliPayResultNotificationView(APIView, Notify):
    """
    支付结果异步通知回调处理类
    负责接收支付宝支付后台发送的支付结果并对订单有效性进行验证，将验证结果反馈给支付宝支付后台
    """

    def post(self, request, format=None):
        """
        接收支付宝支付后台发送的支付结果并对订单有效性进行验证，将验证结果反馈给支付宝支付后台
        根据支付结果修改交易单，通知订单状态发生改变
        :param format:
        :return:
        """

        try:
            logging.info(request.data)

            notify_data = self.get_notify_data_and_verify(request.data)

            transaction_id = notify_data.get('trade_no')
            if not transaction_id:
                return HttpResponse('failed')

            out_trade_no = notify_data.get('out_trade_no')
            if not out_trade_no:
                return HttpResponse(u'需要out_trade_no')
            need_notify_order_success = False
            product_order = None
            with transaction.atomic():
                trade = AliPaymentTradeOrder.objects.select_for_update().get(out_trade_no=out_trade_no)

                if trade.order_status in (3, 9):
                    # 已经处理过，直接返回成功接收
                    return Response('success')

                product_order = ProductOrder.objects.select_for_update().get(order_no=trade.order_no)

                trade.notify_id = notify_data['notify_id']
                trade.notify_type = notify_data['notify_type']
                trade.notify_time = notify_data['notify_time']

                trade.transaction_id = notify_data.get('trade_no')

                if 'gmt_create' in notify_data:
                    trade.gmt_create = notify_data['gmt_create']
                if 'gmt_payment' in notify_data:
                    trade.gmt_payment = notify_data['gmt_payment']
                if 'gmt_close' in notify_data:
                    trade.gmt_close = notify_data['gmt_close']

                if 'bank_seq_no' in notify_data:
                    trade.bank_seq_no = notify_data['bank_seq_no']

                trade.ali_result_code = notify_data.get('result_code', '')
                trade.ali_err_code = notify_data.get('error', '')
                trade.ali_trade_status = notify_data.get('trade_status', '')
                if trade.ali_trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
                    trade.order_status = 3
                    need_notify_order_success = True
                    product_order.status = 2
                    product_order.pay_type = 2
                else:
                    trade.order_status = 1
                    product_order.status = 3

                trade.ali_response = notify_data
                trade.is_order_over = True
                trade.save(force_update=True)
                product_order.save()

            if need_notify_order_success:
                # 通知订单支付成功
                notify_order_pay_success(product_order)

            content = 'success'
            return HttpResponse(content)
        except AliPayException as e:
            return HttpResponse('failed')

        except AliPaymentTradeOrder.DoesNotExist as e:
            logging.exception(e)
            return HttpResponse('failed>')
        except ProductOrder.DoesNotExist as e:
            logging.exception(e)
            return HttpResponse('failed')
        except Exception as e:
            logging.exception(e)
            return HttpResponse(body='failed')
