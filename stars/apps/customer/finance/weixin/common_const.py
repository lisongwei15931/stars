# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from stars.apps.customer.safety.common_const import Const


class _WxPaymentConstData(Const):

    TRADE_EXPIRE_SECONDS = 5*60

    # finance-wx-result-notification
    NOTIFY_URL = 'http://www.ltbh365.com/' + 'accounts/fin/wx/pay/result/notification/'
    # NOTIFY_URL = 'https://www.ltbh365.com:8293/' + 'accounts/fin/pay/result/notification/'  # reverse('customers:finance-wx-result-notification')

    REPORT_LEVEL = 0


    UnifiedOrderErrorCodeMsg = {
            'NOAUTH': u'商户无此接口权限',  #‘
            'NOTENOUGH': u'余额不足',  #
            'ORDERPAID': u'商户订单已支付',  #商户订单已支付，无需重复操作
            'ORDERCLOSED': u'订单已关闭 ', #当前订单已关闭，无法支付  # 当前订单已关闭，请重新下单
            'SYSTEMERROR': u'系统错误 ', #  系统超时   # 系统异常，请用相同参数重新调用
            'APPID_NOT_EXIST': u'APPID不存在',  # 参数中缺少APPID
            'MCHID_NOT_EXIST': u'MCHID不存在',  # 参数中缺少MCHID
            'APPID_MCHID_NOT_MATCH': u'appid和mch_id不匹配',  #
            'LACK_PARAMS': u'缺少参数',  #
            'OUT_TRADE_NO_USED': u'商户订单号重复',
            'SIGNERROR': u'签名错误',
            'XML_FORMAT_ERROR': u'XML格式错误 ',
            'REQUIRE_POST_METHOD': u'请使用post方法 ',
            'POST_DATA_EMPTY': u'post数据为空 ',
            'NOT_UTF8': u'编码格式错误',  # 请使用NOT_UTF8编码格式
    }

    OrderQueryErrorCodeMsg = {
            'ORDERNOTEXIST ': u'此交易订单号不存在',  #该API只能查提交支付交易返回成功的订单，请商户检查需要查询的订单号是否正确
            'SYSTEMERROR': u'系统错误',  # 后台系统返回错误 	系统异常，请再调用发起查询
    }

    OrderQueryTradeState = {
        'SUCCESS': u'支付成功',  #
        'REFUND': u'转入退款',  #
        'NOTPAY': u'未支付',  #
        'CLOSED': u'已关闭 ',  #
        'REVOKED': u'已撤销（刷卡支付） ',  #
        'USERPAYING': u'用户支付',  #
        'PAYERROR': u'支付失败(其他原因，如银行返回失败)',  #
    }

    CloseOrderErrorCodeMsg = {
            'ORDERPAID': u'订单已支付',  # 订单已支付，不能发起关单 	订单已支付，不能发起关单，请当作已支付的正常交易
            'SYSTEMERROR': u'系统错误',  #系统错误 	系统异常，请重新调用该API
            'ORDERNOTEXIST': u'订单不存在',  #订单系统不存在此订单 	不需要关单，当作未提交的支付的订单
            'ORDERCLOSED': u'订单已关闭 ', #订单已关闭，无法重复关闭 	订单已关闭，无需继续调用
            'SYSTEMERROR': u'系统错误 ', #  系统错误 	系统异常，请重新调用该API
            'SIGNERROR': u'签名错误',
            'XML_FORMAT_ERROR': u'XML格式错误 ',
            'REQUIRE_POST_METHOD': u'请使用post方法 ',
    }

    CloseOrderErrorCodeMsg = {
            'ORDERPAID': u'订单已支付',  # 订单已支付，不能发起关单 	订单已支付，不能发起关单，请当作已支付的正常交易
            'SYSTEMERROR': u'系统错误',  #系统错误 	系统异常，请重新调用该API
            'ORDERNOTEXIST': u'订单不存在',  #订单系统不存在此订单 	不需要关单，当作未提交的支付的订单
            'ORDERCLOSED': u'订单已关闭 ', #订单已关闭，无法重复关闭 	订单已关闭，无需继续调用
            'SYSTEMERROR': u'系统错误 ', #  系统错误 	系统异常，请重新调用该API
            'SIGNERROR': u'签名错误',
            'XML_FORMAT_ERROR': u'XML格式错误 ',
            'REQUIRE_POST_METHOD': u'请使用post方法 ',
    }

    RefundErrorCodeMsg = {
            'INVALID_TRANSACTIONID': u'无效transaction_id',  # 请求参数未按指引进行填写 	请求参数错误，检查原交易号是否存在或发起支付交易接口返回失败
            'PARAM_ERROR': u'参数错误',  #
            'SYSTEMERROR': u'系统错误 ', #  系统超时   # 系统异常，请用相同参数重新调用
            'APPID_NOT_EXIST': u'APPID不存在',  # 参数中缺少APPID
            'MCHID_NOT_EXIST': u'MCHID不存在',  # 参数中缺少MCHID
            'APPID_MCHID_NOT_MATCH': u'appid和mch_id不匹配',  #
            'SIGNERROR': u'签名错误',
            'XML_FORMAT_ERROR': u'XML格式错误 ',
            'REQUIRE_POST_METHOD': u'请使用post方法 ',
    }

    RefundQueryErrorCodeMsg = {
            'INVALID_TRANSACTIONID': u'无效transaction_id',  # 请求参数未按指引进行填写 	请求参数错误，检查原交易号是否存在或发起支付交易接口返回失败
            'PARAM_ERROR': u'参数错误',  #
            'SYSTEMERROR': u'系统错误 ', #  系统超时   # 系统异常，请用相同参数重新调用
            'APPID_NOT_EXIST': u'APPID不存在',  # 参数中缺少APPID
            'MCHID_NOT_EXIST': u'MCHID不存在',  # 参数中缺少MCHID
            'APPID_MCHID_NOT_MATCH': u'appid和mch_id不匹配',  #
            'SIGNERROR': u'签名错误',
            'XML_FORMAT_ERROR': u'XML格式错误 ',
            'REQUIRE_POST_METHOD': u'请使用post方法 ',
    }

    DownloadBillErrorCodeMsg = {
            'INVALID_TRANSACTIONID': u'无效transaction_id',  # 请求参数未按指引进行填写 	请求参数错误，检查原交易号是否存在或发起支付交易接口返回失败
            'PARAM_ERROR': u'参数错误',  #
            'SYSTEMERROR': u'系统错误 ', #  系统超时   # 系统异常，请用相同参数重新调用
    }


class _WxNativePaymentConstData(_WxPaymentConstData):
    APP_ID = 'wxdbbb627996d8d6ee'  # AppId
    MCH_ID = '1289634301'  # 商户号
    DEVICE_INFO = 'WEB'
    IP = '139.129.131.153'

    API_KEY = 'VhSX1X1DHXKm0VZYA3O4H7whYnhvJThf'

WxNativePaymentConstData = _WxNativePaymentConstData()