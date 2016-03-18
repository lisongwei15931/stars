# -*- coding: utf-8 -*-s

from stars.apps.customer.finance.alipay.ali_pay_api import AliPayApi
from stars.apps.customer.finance.finance_exception import AliPayException
from stars.apps.customer.finance.alipay.utils import checkSign

from stars.apps.customer.finance.alipay.log import ali_pay_log as logging


class Notify(object):
    """
    回调处理基类
    """
    def get_notify_data_and_verify(self, resp_data):
        """
        接收从支付宝支付后台发送过来的数据并验证签名
        :return: 支付宝支付后台返回的数据
        """

        # 接收从支付宝后台传来的数据
        if checkSign(resp_data) != 0:
            logging.error('from ali pay notification: sign error: ' + str(resp_data))
            raise AliPayException(AliPayException.ERROR_SIGN, u'签名错误')
        notify_id = resp_data.get('notify_id')
        if not notify_id or not AliPayApi.verify_notification(notify_id):
            logging.error('from ali pay notification: notify_id error: ' + str(resp_data))
            raise AliPayException(AliPayException.FAILED_NOTIFY_ID, u'notify_id无效')
        return resp_data

