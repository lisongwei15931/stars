# -*- coding: utf-8 -*-

from datetime import *

from django.db import transaction
import django.utils.timezone

from stars.apps.commission.models import ProductOrder
from stars.apps.customer.finance.alipay.ali_pay_api import AliPayApi
from stars.apps.customer.finance.alipay.alipay_config import AliPayConfig
from stars.apps.customer.finance.alipay.log import ali_pay_log as logging
from stars.apps.customer.finance.alipay.utils import makeSign, checkSign
from stars.apps.customer.finance.models import AliPaymentTradeOrder, AliPaymentBill
from stars.apps.customer.finance.utils import notify_order_pay_success


class AliPayRequest(object):
    __REMAINING_SECONDS = 600

    def __get_or_create_trade(self, product_order, *args, **kwargs):
        """
        生成支付宝支付单
        :return:
        """
        try:
            trade = AliPaymentTradeOrder.objects.get(order_no=product_order.order_no)
            return trade
        except AliPaymentTradeOrder.DoesNotExist:
            pass

        now = django.utils.timezone.now()
        out_trade_no = AliPayApi.generate_out_trade_no(product_order.user_id)
        trade = AliPaymentTradeOrder(
                                    out_trade_no=out_trade_no,
                                    order_no=product_order.order_no,
                                    uid=product_order.user_id,
                                    seller_id=AliPayConfig.SELLER_ID,
                                    total_fee=product_order.amount,
                                    subject=product_order.description,
                                    body=product_order.detail,
                                    start_time=now,
                                    it_b_pay=str(self.__REMAINING_SECONDS/60) + 'm'
                                    )

        trade.save(force_insert=True)
        return trade

    def __create_trade(self, product_order, pay_service_type, *args, **kwargs):
        """
        生成支付宝支付单
        :return:
        """
        now = django.utils.timezone.now()
        out_trade_no = AliPayApi.generate_out_trade_no(product_order.user_id)
        trade = AliPaymentTradeOrder(
                                    out_trade_no=out_trade_no,
                                    pay_service_type=pay_service_type,
                                    order_no=product_order.order_no,
                                    uid=product_order.user_id,
                                    seller_id=AliPayConfig.SELLER_ID,
                                    total_fee=product_order.amount,
                                    subject=product_order.description,
                                    body=product_order.detail,
                                    start_time=now,
                                    it_b_pay=str(self.__REMAINING_SECONDS/60) + 'm',
                                    )
        if pay_service_type == 'direct_pay':
            trade.pay_service_type = 'directPay'
        elif pay_service_type == 'bank_pay':
            trade.pay_service_type = 'bankPay'
        elif pay_service_type == 'mobile':
            trade.pay_service_type = 'mobile'
        else:
            raise ValueError
        trade.save(force_insert=True)
        return trade

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

    def create_form_input_value(self, trade, pay_service_type, bank_code='', sign_type='md5'):
        # total_fee = commission_buy.quantity * quantity.price

        m = {}
        ali_service = {'direct_pay': 'create_direct_pay_by_user', 'bank_pay': 'create_direct_pay_by_user', 'mobile': 'mobile.securitypay.pay'}
        m['service'] =ali_service[pay_service_type]
        m['partner'] = AliPayConfig.PID
        m['_input_charset'] = AliPayConfig.INPUT_CHARSET
        m['notify_url'] = AliPayConfig.NOTIFY_URL
        if pay_service_type in ('bank_pay', 'direct_pay'):
            m['return_url'] = AliPayConfig.RETURN_URL
            m['error_notify_url'] = AliPayConfig.ERROR_NOTIFY_URL
            m['anti_phishing_key'] = AliPayApi.query_timestamp()     # 防钓鱼时间戳  通过时间戳查询接口获取的加密支付宝系统时间戳。
        m['out_trade_no'] = trade.out_trade_no   # 商户网站唯一订单号
        m['subject'] = trade.subject if trade.subject else u'蓝图商品'   # 商品名称 商品的标题/交易标题/订单标题/订单关键字等。最长为128个汉字。
        m['payment_type'] = trade.payment_type   # 支付类型 1（商品购买）。
        m['total_fee'] = trade.total_fee   # 该笔订单的资金总额，单位为RMB-Yuan。取值范围为[0.01，100000000.00]，精确到小数点后两位。
        m['seller_id'] = trade.seller_id
        m['body'] = trade.body         # 商品描述  对一笔交易的具体描述信息。(1000)

        m['it_b_pay'] = trade.it_b_pay          # 超时时间  设置未付款交易的超时时间，一旦超时，该笔交易就会自动被关闭。
                                    #取值范围：1m～15d。m-分钟，h-小时，d-天，1c-当天（1c-当天的情况下，无论交易何时创建，都在0点关闭）。
                                    #该参数数值不接受小数点，如1.5h，可转换为90m。
        if pay_service_type == 'bank_pay':
            m['paymethod'] = 'bankPay'
            m['defaultbank'] = bank_code
        elif pay_service_type == 'direct_pay':
            m['qr_pay_mode'] = ''              #  扫码支付方式  2：订单码-跳转模式
        else:
            pass
        if pay_service_type == 'mobile':
            m_t = {k: u'"{}"'.format(v) for k,v in m.items()}
            # for k, v in m.items():
            #     if isinstance(v, unicode):
            #         m[k] = u'"{}"'.format(v)
            #     else:
            #         m[k] = u'"{}"'.format(v)
        else:
            m_t = m
        m['sign'], sign_string = makeSign(m_t, sign_type)
        m['sign_type'] = sign_type

        if pay_service_type in ('bank_pay', 'direct_pay'):
            action = '{gateway}_input_charset={charset}'.format(gateway=AliPayConfig.ALI_PAY_GATEWAY_NEW,
                                                                   charset=AliPayConfig.INPUT_CHARSET)
            return {'action': action, 'params': m}
        else:
            return {'action': '', 'params': m, 'sign_string': sign_string}

    def get(self, order_no, user, pay_service_type, sign_type='MD5', bank_code=''):
        """

        :param order_no: 市场订单号
        :param user: user,用于检索订单条件
        :param pay_service_type: 支付业务类型。即时到账，网银支付,移动支付等
        :param bank_code: pay_service_type为网银支付时为默认银行代码，其他类型无意义
        :param sign_type: 加密类型
        :return: dict  'pay_status'：0，未支付；1：已支付。
                        'form': 'actions': form action
                                params：input value，key:name;value:value.
        """
        # ①不存在----记录，
        # ②已经撤单---记录   ---- 购买不能撤单
        ctx = {}
        try:
            # order_no = '123'
            if not order_no or pay_service_type not in ('direct_pay', 'bank_pay', 'mobile'):
                raise ValueError
            # 根据订单号取订单
            with transaction.atomic():
                product_order = ProductOrder.objects.select_for_update().get(order_no=order_no, user=user)
                # ③已经支付---不做处理
                if self.has_payed(product_order):
                    ctx['pay_status'] = 1
                    return ctx
                # ④支付中
                # elif self.is_paying(product_order):
                #     return HttpResponseBadRequest(u'订单支付进行中')
                # ⑤未支付----修改交易单状态，记录，通知
                else:
                    pass
        except (KeyError, ValueError):
            return ValueError(u'缺少订单号')
        except ProductOrder.DoesNotExist as e:
            logging.exception(e)
            return ValueError(u'订单不存在')

        # 生成交易单
        ali_trade_order = None
        for ele in AliPaymentTradeOrder.objects.filter(order_no=product_order.order_no):

            if ele.order_status == 10:    #预支付中，查询订单状态
                r = self.query_and_set_order(ele)
            else:
                r = ele

            if r and r.order_status in [3,9]:  # 已经支付
                notify_order_pay_success(product_order)
                ctx['pay_status'] = 1
                return ctx
            elif r and r.pay_service_type == pay_service_type:
                ali_trade_order = r

        ctx['bank_code'] = bank_code
        ctx['pay_status'] = 0
        if not ali_trade_order:
            ali_trade_order = self.__create_trade(product_order, pay_service_type, bank_code=bank_code)

        # ali_trade_order = self.__get_or_create_trade(product_order, pay_service_type)
        # if ali_trade_order.order_status in (0,1,2):
        #     pass
        # elif ali_trade_order.order_status == 10:    #预支付中，查询订单状态
        #     r = self.query_and_set_order(ali_trade_order)
        #     if not r:
        #         ali_trade_order = r
        #
        # if ali_trade_order.order_status in (3,9):  # 已经支付
        #     notify_order_pay_success(product_order)
        #     ctx['pay_status'] = 1
        #     return ctx
        # else:
        #     ctx['pay_status'] = 0

        ctx['form'] = self.create_form_input_value(ali_trade_order, pay_service_type, bank_code, sign_type)

        return ctx

    @classmethod
    def query_and_set_order(cls, trade):
        if trade.transaction_id:
            resp_data = AliPayApi.query_single_trade({'transaction_id': trade.transaction_id})
        else:
            resp_data = AliPayApi.query_single_trade({'out_trade_no': trade.trade_no})
        if resp_data['is_success'] == 'T':

            if checkSign(resp_data) != 0:
                logging.error('from ali pay single order query: sign error: ' + trade.trade_no)
                logging.error(resp_data)
                return None

            trade.transaction_id = resp_data['trade_no']
            trade.gmt_create = resp_data['gmt_create']
            if 'gmt_payment' in resp_data:
                trade.gmt_payment = resp_data['gmt_payment']
            if 'gmt_last_modified_time' in resp_data:
                trade.gmt_last_modified_time = resp_data['gmt_last_modified_time']
            if 'time_out' in resp_data:
                trade.time_out = resp_data['time_out']
            if 'gmt_close' in resp_data:
                trade.gmt_close = resp_data['gmt_close']
            if 'time_out_type' in resp_data:
                trade.time_out_type = resp_data['time_out_type']

            if 'bank_seq_no' in resp_data:
                trade.bank_seq_no = resp_data['bank_seq_no']

            trade.ali_result_code = resp_data['result_code']
            trade.ali_err_code = resp_data.get('error', '')
            trade.ali_trade_status = resp_data.get('trade_status', '')
            if trade.ali_trade_status == 'TRADE_SUCCESS':   # 支付成功
                trade.order_status = 3
            with transaction.atomic():  # 支付成功
                if trade.order_status in (3,9) and trade.is_order_over is False:
                    trade.ali_response = resp_data
                    trade.is_order_over = True
                    trade.save(force_update=True)
                    # 通知订单支付成功
                    product_order = ProductOrder.objects.select_for_update().get(order_no=trade.order_no)
                    # product_order.status = 2
                    # product_order.pay_type = 2
                    notify_order_pay_success(product_order)
                else:
                    trade.save(force_update=True)
            return trade
        else:
            return None


class AliPayDownloadBill(object):

    __MUST_ITEMS = ('income', 'outcome','balance', 'trans_ date', 'sub_tr ans_code_msg')
    __NOT_MUST_ITEMS = ('total_fee', 'trade_refund_amount','merchant_out_order_no', 'trans_out_order_no',
                        'partner_id', 'trans_code_msg',
                        'bank_name', 'bank_account_no', 'bank_account_name', 'memo', 'buyer_account',
                        'seller_account', 'seller_fullname', 'currency', 'deposit_bank_no', 'goods_title',
                        'iw_account_log_id', 'trans_account', 'other_account_email', 'other_account_fullname',
                        'other_user_id', 'service_fee', 'service_fee_ratio', 'sign_product_name', 'rate'
                        )

    def download(self, bill_date):
        """
        下载对账单,保存到数据库
        :param bill_date: 账单日期，格式：YYYYMMDD
        :return:
        """
        start_time = datetime.strptime(bill_date, '%Y%m%d')
        end_time = start_time + timedelta(days=1)

        try:
            bills = []

            # 向支付宝查询
            for rs in AliPayApi.query_trade(gmt_start_time=start_time, gmt_end_time=end_time):
                for r in rs:
                    bill = AliPaymentBill()
                    bill.transaction_id = r.get('trade_no', '')
                    for ele in self.__MUST_ITEMS:
                        setattr(bill,ele, r[ele])

                    for ele in self.__NOT_MUST_ITEMS:
                        if r.get(ele) is not None and r.get(ele) != '':
                            setattr(bill,ele, r[ele])
                    bills.append(bill)

            if bills:
                AliPaymentBill.objects.bulk_create(bills)

            return len(bills)

        except Exception as e:
            logging.exception(e)
            return -1
