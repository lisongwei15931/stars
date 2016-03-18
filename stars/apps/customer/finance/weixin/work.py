# -*- coding: utf-8 -*-
import logging

from stars.apps.customer.finance.weixin.common_const import WxNativePaymentConstData


def place_order_to_weixin(total_fee):
    # total_fee = commission_buy.quantity * quantity.price

    appid = WxNativePaymentConstData.APP_ID
    mch_id = WxNativePaymentConstData.MCH_ID
    device_info = WxNativePaymentConstData.DEVICE_INFO


