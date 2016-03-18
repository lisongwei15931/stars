# -*- coding: utf-8 -*-

from stars.apps.customer.finance.weixin.common_const import _WxPaymentConstData


class _WxMobilePaymentConstData(_WxPaymentConstData):
    APP_ID = 'wx201ef332f9af3324'  # AppId
    MCH_ID = '1310550501'  # 商户号
    DEVICE_INFO = 'WEB'
    IP = '139.129.131.153'

    API_KEY = 'phvQJKf9d3ElYkGjYr7kG1i8Niw06849' #'ea64ffe5888f979336400e7920c03244'

WxMobilePaymentConstData = _WxMobilePaymentConstData()

class _WxAndroidPaymentConstData(_WxMobilePaymentConstData):
    pass
    # APP_ID = 'wx201ef332f9af3324'  # AppId
    # MCH_ID = '1289634301'  # 商户号
    #
    # API_KEY = 'ea64ffe5888f979336400e7920c03244'

WxAndroidPaymentConstData = _WxAndroidPaymentConstData()

class _WxIosPaymentConstData(_WxMobilePaymentConstData):
    pass
    # APP_ID = 'wx201ef332f9af3324'  # AppId
    # MCH_ID = '1289634301'  # 商户号
    #
    # API_KEY = 'ea64ffe5888f979336400e7920c03244'

WxIosPaymentConstData = _WxIosPaymentConstData()