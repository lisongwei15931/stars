# -*- coding: utf-8 -*-
import hashlib
import random
import string
from datetime import *

import httplib2

from stars.apps.customer.finance.finance_exception import WxException
from stars.apps.customer.finance.weixin.common_const import WxNativePaymentConstData
from stars.apps.customer.finance.weixin.utils import makeXml, make_dict_from_xml, to_url_params, makeSign

from stars.apps.customer.finance.weixin.log import wx_pay_log as logging

def get_prepay_short_url(product_id):
    """
    根据product_id生成是微信扫描支付模式一URL
    :param product_id: 订单号
    :return: url
    """
    #生成长地址
    long_url = WxPayApi.get_pre_pay_url(product_id)

    try:
        #获取短地址
        result = WxPayApi.get_short_url({'long_url': long_url}, time_out=3)

        if result['return_code'] == 'SUCCESS' and result['result_code'] == 'SUCCESS' and result.get('short_url'):
            return result.get('short_url')
        else:
            logging.exception('获取微信short url失败')
            logging.exception(result)
    except Exception as e:
        logging.exception(e)
    # 生成短地址失败是返回长地址
    return long_url


class WxPayApi(object):

    WX_PAYMENT_CONFIG = None

    @classmethod
    def makeSign(cls, m, api_key=None):
        ks = m.keys()
        ks.sort()
        ls = []
        for k in ks:
            if m[k] not in (None, ''):
                if isinstance(m[k], unicode):
                    ls.append('{k}={v}'.format(k=k, v=m[k].encode('utf8')))
                else:
                    ls.append('{k}={v}'.format(k=k, v=m[k]))

        # ls = ['{k}={v}'.format(k=k, v=m[k]) for k in ks if m[k] not in (None, '')]
        s = '&'.join(ls)
        if not api_key:
            api_key = cls.WX_PAYMENT_CONFIG.API_KEY
        stringSignTemp="{s}&key={api_key}".format(s=s, api_key=api_key)
        return hashlib.md5(stringSignTemp).hexdigest().upper()


    @classmethod
    def app_id(cls):
        raise NotImplemented()

    @classmethod
    def mch_id(cls):
        raise NotImplemented

    @classmethod
    def generate_timestamp(cls):
        """
        生成时间戳，标准北京时间，时区为东八区，自1970年1月1日 0点0分0秒以来的秒数
        :return: 时间戳
        """
        ts = datetime.utcnow() - datetime(1970, 1, 1, 0, 0, 0, 0)
        return int(ts)

    @classmethod
    def generate_nonce_str(cls):
        """
        生成随机串，随机串包含字母或数字
        :return: 随机串
        """
        return ''.join(random.sample(string.letters+string.digits, 32))

    @classmethod
    def generate_out_trade_no(cls, user_id):
        """
        生成订单号
        :param user_id: 用户id
        :return: 订单号
        """
        s = 'wx'+'{:0<18}'.format(datetime.now().strftime('%Y%m%d%H%M%S%f')[2:20])+''.join(random.sample(string.letters, 3))+'{:0>9}'.format(user_id)[:9]
        assert(len(s) == 32)
        return s

    @classmethod
    def get_pre_pay_url(cls, product_id):
        """
        生成扫描支付模式一URL
        :param product_id: 商品id或订单号
        :return: 模式一URL
        """
        data = {}
        data['appid'] = cls.WX_PAYMENT_CONFIG.APP_ID if not data.get('app_id') else data.get('app_id') 
        data['mch_id'] = cls.WX_PAYMENT_CONFIG.MCH_ID if not data.get('mch_id') else data.get('mch_id')
        data['user_ip'] = cls.WX_PAYMENT_CONFIG.IP if not data.get('user_ip') else data.get('user_ip')
        data['time'] = datetime.today().strftime('%Y%m%d%H%M%S')  #商户上报时间
        data['nonce_str'] = WxPayApi.generate_nonce_str() #随机字符串
        data['product_id'] = product_id
        data['sign'] = makeSign(data)   #签名

        url = "weixin://wxpay/bizpayurl?" + to_url_params(data)

        return url

    @classmethod
    def get_short_url(cls, data, time_out=6):
        """
        转换短链接
        该接口主要用于扫码原生支付模式一中的二维码链接转成短链接(weixin://wxpay/s/XXXXXX)，
        减小二维码数据量，提升扫描速度和精确度。
        :param data: 提交给转换短连接API的参数
        :param time_out: 接口超时时间
        :return: 成功时返回，其他抛异常
        """

        url = "https://api.mch.weixin.qq.com/tools/shorturl"
        # 检测必填参数
        if not data.get("long_url"):
            raise WxException(WxException.ERROR_PARAM, "需要转换的URL，签名用原串，传输需URL encode！")
        data['appid'] = cls.WX_PAYMENT_CONFIG.APP_ID if not data.get('app_id') else data.get('app_id') 
        data['mch_id'] = cls.WX_PAYMENT_CONFIG.MCH_ID if not data.get('mch_id') else data.get('mch_id')
        data['nonce_str'] = WxPayApi.generate_nonce_str() #随机字符串
        data['sign'] = makeSign(data)   #签名
        req_body = makeXml(data)

        start = datetime.now()  #请求开始时间

        h = httplib2.Http(".cache", timeout=time_out)
        resp, content = h.request(url, "POST", body=req_body, headers={'content-type': 'text/xml'})

        result = make_dict_from_xml(content)

        timeCost = int((datetime.now() - start).total_seconds())

        cls.report_cost_time(url, timeCost, result) # 测速上报

        return result

    @classmethod
    def report(cls, data, time_out=1):
        """

        :param data: 提交给测速上报接口的参数
        :param time_out: 测速上报接口超时时间
        :return: 成功时返回测速上报接口返回的结果, 失败：异常
        """
        url = "https://api.mch.weixin.qq.com/payitil/report"

        must_params = {
                        'interface_url': u'接口URL，缺少必填参数interface_url！',
                        'return_code': u'返回状态码，缺少必填参数return_code！',
                        'result_code': u'业务结果，缺少必填参数result_code！',
                        'user_ip': u'访问接口IP，缺少必填参数user_ip！',
                        'execute_time_': u'接口耗时，缺少必填参数execute_time_！',
                       }
        absence = set(must_params.keys()) - set(data.keys())

        if absence:
            raise WxException(WxException.ERROR_PARAM, must_params[absence.pop()])

        data['appid'] = cls.WX_PAYMENT_CONFIG.APP_ID if not data.get('app_id') else data.get('app_id') 
        data['mch_id'] = cls.WX_PAYMENT_CONFIG.MCH_ID if not data.get('mch_id') else data.get('mch_id')
        data['user_ip'] = cls.WX_PAYMENT_CONFIG.IP if not data.get('user_ip') else data.get('user_ip')
        data['time'] = datetime.today().strftime('%Y%m%d%H%M%S')  #商户上报时间
        data['nonce_str'] = WxPayApi.generate_nonce_str() #随机字符串
        data['sign'] = makeSign(data)   #签名
        req_body = makeXml(data)

        try:
            h = httplib2.Http(".cache", timeout=time_out)
            resp, content = h.request(url, "POST", body=req_body, headers={'content-type': 'text/xml'})

            return make_dict_from_xml(content)
        except:
            return {}

    @classmethod
    def report_cost_time(cls, interface_url, timeCost, input_data):
        """
        测速上报
        :param interface_url: 接口URL
        :param timeCost: 接口耗时
        :param data: 参数数组
        :return:
        """
        # 如果不需要进行上报
        if cls.WX_PAYMENT_CONFIG.REPORT_LEVEL == 0:
            return

        # 如果仅失败上报
        if cls.WX_PAYMENT_CONFIG.REPORT_LEVEL == 1 \
                and input_data.get("return_code", '') == "SUCCESS" \
                and input_data.get("result_code", '') == "SUCCESS":
            return

        # 上报逻辑
        s = ["return_code", 'return_msg', 'result_code', 'err_code', 'err_code_des', 'out_trade_no', 'device_info']
        data = {k:input_data[k] for k in s if k in input_data}
        data["interface_url"] = interface_url
        data["execute_time_"] = timeCost

        try:
            WxPayApi.report(data)
        except Exception as e:
            pass

    @classmethod
    def unified_order(cls, input_data, time_out=6):
        """
        统一下单
        :param input_data: 提交给统一下单API的参数
        :param time_out: 超时时间
        :return: 成功时返回，其他抛异常
        """
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        must_params = {
                        'out_trade_no': u'缺少统一支付接口必填参数out_trade_no！',
                        'body': u'缺少统一支付接口必填参数body',
                        'total_fee': u'缺少统一支付接口必填参数total_fee',
                        'trade_type': u'缺少统一支付接口必填参数trade_type',
                        'product_id': u'统一支付接口中，缺少必填参数product_id！trade_type为JSAPI时，product_id为必填参数！',
                       }
        absence = set(must_params.keys()) - set(input_data.keys())

        if absence:
            raise WxException(WxException.ERROR_PARAM, must_params[absence.pop()])
             # 检测必填参数

        # 异步通知url未设置，则使用配置文件中的url
        if not input_data.get(''):
            input_data['notify_url'] = cls.WX_PAYMENT_CONFIG.NOTIFY_URL # 异步通知url

        data = input_data
        data['appid'] = cls.WX_PAYMENT_CONFIG.APP_ID if not data.get('app_id') else data.get('app_id') 
        data['mch_id'] = cls.WX_PAYMENT_CONFIG.MCH_ID if not data.get('mch_id') else data.get('mch_id')
        data['nonce_str'] = WxPayApi.generate_nonce_str() #随机字符串
        data['sign'] = makeSign(data, cls.WX_PAYMENT_CONFIG.API_KEY)   #签名
        req_body = makeXml(data)
        if isinstance(req_body, unicode):
            req_body = req_body.encode('utf-8')

        start = datetime.now()
        h = httplib2.Http(".cache", timeout=time_out)
        resp, content = h.request(url, "POST", body=req_body, headers={'content-type': 'text/xml'})

        result = make_dict_from_xml(content)
    
        timeCost = int((datetime.now() - start).total_seconds())

        cls.report_cost_time(url, timeCost, result) # 测速上报

        return result
        
    @classmethod
    def order_query(cls, input_data, time_out=6):
        """
        查询订单
        :param input_data: 提交给查询订单API的参数
        :param time_out: 超时时间
        :return: 成功时返回订单查询结果，其他抛异常
        """
        url = "https://api.mch.weixin.qq.com/pay/orderquery"
         # 检测必填参数
        if not input_data.get("out_trade_no") and not input_data.get("transaction_id"):
            raise WxException(WxException.ERROR_PARAM, "订单查询接口中，out_trade_no、transaction_id至少填一个！")

        data = input_data
        data['appid'] = cls.WX_PAYMENT_CONFIG.APP_ID if not data.get('app_id') else data.get('app_id') 
        data['mch_id'] = cls.WX_PAYMENT_CONFIG.MCH_ID if not data.get('mch_id') else data.get('mch_id')
        data['nonce_str'] = WxPayApi.generate_nonce_str() #随机字符串
        data['sign'] = makeSign(data)   #签名

        req_body = makeXml(data)

        start = datetime.now()
        h = httplib2.Http(".cache", timeout=time_out)
        resp, content = h.request(url, "POST", body=req_body, headers={'content-type': 'text/xml'})

        result = make_dict_from_xml(content)

        timeCost = int((datetime.now() - start).total_seconds())

        cls.report_cost_time(url, timeCost, result) # 测速上报

        return result

    @classmethod
    def reverse(cls, input_data, time_out=6):
        """
        撤销订单API接口
        :param input_data: 提交给撤销订单API接口的参数，out_trade_no和transaction_id必填一个
        :param time_out: 接口超时时间
        :return: 成功时返回API调用结果，其他抛异常
        """
        url = "https://api.mch.weixin.qq.com/secapi/pay/reverse"
         # 检测必填参数
        if not input_data.get("out_trade_no") and not input_data.get("transaction_id"):
            raise WxException(WxException.ERROR_PARAM, "撤销订单接口中，out_trade_no、transaction_id至少填一个！")

        data = input_data
        data['appid'] = cls.WX_PAYMENT_CONFIG.APP_ID if not data.get('app_id') else data.get('app_id') 
        data['mch_id'] = cls.WX_PAYMENT_CONFIG.MCH_ID if not data.get('mch_id') else data.get('mch_id')
        data['nonce_str'] = WxPayApi.generate_nonce_str() #随机字符串
        data['sign'] = makeSign(data)   #签名
        
        req_body = makeXml(data)

        start = datetime.now()
        h = httplib2.Http(".cache", timeout=time_out)
        resp, content = h.request(url, "POST", body=req_body, headers={'content-type': 'text/xml'})

        result =  make_dict_from_xml(content)

        timeCost = int((datetime.now() - start).total_seconds())

        cls.report_cost_time(url, timeCost, result) # 测速上报

        return result

    @classmethod
    def refund(cls, input_data, time_out=6):
        """
        申请退款
        :param input_data: 提交给申请退款API的参数
        :param time_out: 超时时间
        :return: 成功时返回接口调用结果，其他抛异常
        """
        url = "https://api.mch.weixin.qq.com/secapi/pay/refund"
         # 检测必填参数
        if not input_data.get("out_trade_no") and not input_data.get("transaction_id"):
            raise WxException(WxException.ERROR_PARAM, "退款申请接口中，out_trade_no、transaction_id至少填一个！")
        elif not input_data.get("out_refund_no"):
            raise WxException(WxException.ERROR_PARAM, "退款申请接口中，缺少必填参数out_refund_no！")
        elif input_data.get("total_fee"):
            raise WxException(WxException.ERROR_PARAM, "退款申请接口中，缺少必填参数total_fee！")
        elif input_data.get("refund_fee"):
            raise WxException(WxException.ERROR_PARAM, "退款申请接口中，缺少必填参数refund_fee！")
        elif input_data.get("op_user_id"):
            raise WxException(WxException.ERROR_PARAM, "退款申请接口中，缺少必填参数op_user_id！")
        

        data = input_data
        data['appid'] = cls.WX_PAYMENT_CONFIG.APP_ID if not data.get('app_id') else data.get('app_id') 
        data['mch_id'] = cls.WX_PAYMENT_CONFIG.MCH_ID if not data.get('mch_id') else data.get('mch_id')
        data['nonce_str'] = WxPayApi.generate_nonce_str() #随机字符串
        data['sign'] = makeSign(data)   #签名

        req_body = makeXml(data)

        start = datetime.now()
        h = httplib2.Http(".cache", timeout=time_out)
        resp, content = h.request(url, "POST", body=req_body, headers={'content-type': 'text/xml'})

        result =  make_dict_from_xml(content)

        timeCost = int((datetime.now() - start).total_seconds())

        cls.report_cost_time(url, timeCost, result) # 测速上报

        return result

    @classmethod
    def refund_query(cls, input_data, time_out=6):
        """
        * 查询退款
        * 提交退款申请后，通过该接口查询退款状态。退款有一定延时，
        * 用零钱支付的退款20分钟内到账，银行卡支付的退款3个工作日后重新查询退款状态。
        * out_refund_no、out_trade_no、transaction_id、refund_id四个参数必填一个
        :param input_data: 提交给查询退款API的参数
        :param time_out: 接口超时时间
        :return: 成功时返回，其他抛异常
        """
        url = "https://api.mch.weixin.qq.com/pay/refundquery"
         # 检测必填参数
        if not input_data.get("out_refund_no") and not input_data.get("out_trade_no")\
                and not input_data.get("transaction_id") and not input_data.get("refund_id"):

            raise WxException(WxException.ERROR_PARAM, "退款查询接口中，out_refund_no、out_trade_no、transaction_id、refund_id四个参数必填一个！")


        data = input_data
        data['appid'] = cls.WX_PAYMENT_CONFIG.APP_ID if not data.get('app_id') else data.get('app_id') 
        data['mch_id'] = cls.WX_PAYMENT_CONFIG.MCH_ID if not data.get('mch_id') else data.get('mch_id')
        data['nonce_str'] = WxPayApi.generate_nonce_str() #随机字符串
        data['sign'] = makeSign(data)   #签名

        req_body = makeXml(data)

        start = datetime.now()
        h = httplib2.Http(".cache", timeout=time_out)
        resp, content = h.request(url, "POST", body=req_body, headers={'content-type': 'text/xml'})

        result =  make_dict_from_xml(content)

        timeCost = int((datetime.now() - start).total_seconds())

        cls.report_cost_time(url, timeCost, result) # 测速上报

        return result

    @classmethod
    def download_bill(cls, input_data, time_out=6):
        """
        下载对账单
        :param input_data: 提交给下载对账单API的参数
        :param time_out: 接口超时时间
        :return: 成功时返回，其他抛异常
        """
        
        url = "https://api.mch.weixin.qq.com/pay/downloadbill"
         # 检测必填参数
        if not input_data.get("bill_date"):

            raise WxException(WxException.ERROR_PARAM, "对账单接口中，缺少必填参数bill_date！")


        data = input_data
        data['appid'] = cls.WX_PAYMENT_CONFIG.APP_ID if not data.get('app_id') else data.get('app_id') 
        data['mch_id'] = cls.WX_PAYMENT_CONFIG.MCH_ID if not data.get('mch_id') else data.get('mch_id')
        data['nonce_str'] = WxPayApi.generate_nonce_str() #随机字符串
        data['sign'] = makeSign(data)   #签名

        req_body = makeXml(data)

        h = httplib2.Http(".cache", timeout=time_out)
        resp, content = h.request(url, "POST", body=req_body, headers={'content-type': 'text/xml'})

        # 若接口调用失败会返回xml格式的结果
        if content.startswith('<xml>'):
            return make_dict_from_xml(content)
        # 接口调用成功则返回非xml格式的数据
        else:
            return content

    @classmethod
    def close_order(cls, input_data, time_out=6):
        """
        关闭订单
        :param input_data: 提交给关闭订单API的参数
        :param time_out: 接口超时时间
        :return: 成功时返回，其他抛异常
        """
        url = "https://api.mch.weixin.qq.com/pay/closeorder"
        # 检测必填参数
        if not input_data.get("out_trade_no"):
            raise WxException(WxException.ERROR_PARAM, "关闭订单接口中，out_trade_no必填！")

        data = input_data
        data['appid'] = cls.WX_PAYMENT_CONFIG.APP_ID if not data.get('app_id') else data.get('app_id') 
        data['mch_id'] = cls.WX_PAYMENT_CONFIG.MCH_ID if not data.get('mch_id') else data.get('mch_id')
        data['nonce_str'] = WxPayApi.generate_nonce_str() #随机字符串
        data['sign'] = makeSign(data)   #签名

        req_body = makeXml(data)

        start = datetime.now()
        h = httplib2.Http(".cache", timeout=time_out)
        resp, content = h.request(url, "POST", body=req_body, headers={'content-type': 'text/xml'})

        result = make_dict_from_xml(content)

        timeCost = int((datetime.now() - start).total_seconds())

        cls.report_cost_time(url, timeCost, result)    # 测速上报

        return result


class WxNativePayApi(WxPayApi):
    WX_PAYMENT_CONFIG = WxNativePaymentConstData
