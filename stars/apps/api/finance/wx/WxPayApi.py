from stars.apps.api.finance.wx.common_const import WxAndroidPaymentConstData, WxIosPaymentConstData
from stars.apps.customer.finance.weixin.wx_pay_api import WxPayApi


class WxAndroidPayApi(WxPayApi):
    WX_PAYMENT_CONFIG = WxAndroidPaymentConstData

class WxIosPayApi(WxPayApi):
    WX_PAYMENT_CONFIG = WxIosPaymentConstData