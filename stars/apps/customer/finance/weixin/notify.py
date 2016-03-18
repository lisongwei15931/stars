# -*- coding: utf-8 -*-s

from django.http import HttpResponse

from stars.apps.customer.finance.finance_exception import WxException
from stars.apps.customer.finance.weixin.utils import checkSign, make_dict_from_xml

from stars.apps.customer.finance.weixin.log import wx_pay_log as logging


class Notify(object):
    """
    回调处理基类
    """
    def get_notify_data(self, request):
        """
        接收从微信支付后台发送过来的数据并验证签名
        :return: 微信支付后台返回的数据
        """

        # 接收从微信后台POST过来的数据
        logging.debug('in notify start ######################## ')
        try:
            fromWxData = make_dict_from_xml(request.body)
            logging.debug('in notify : notify request.body ok  ######################## ')
            if fromWxData["return_code"] == "SUCCESS":
                if checkSign(fromWxData) != 0:
                    raise WxException(WxException.ERROR_SIGN, u'签名错误')
            return fromWxData
        except WxException as e:
            logging.error('from weixin notification: sign error: ' + request.body)
            data = '<xml><return_code><![CDATA[FAIL]]></return_code>' \
                   '<return_msg><![CDATA[{}]]></return_msg></xml>'.format('.'.join(e.msgs))
            return HttpResponse(data, content_type='text/xml')

