# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

from stars.apps.customer.finance.ab.common_const import AgriculturalBankTradeConstData


class AgriculturalBankOriginalKey(models.Model):
    """
    农行通信固有密钥
    """
    package = models.CharField(verbose_name=u'包密钥', max_length=128)
    mac = models.CharField(verbose_name=u'mac密钥', max_length=128)
    pin = models.CharField(verbose_name=u'关键域密钥', max_length=128)

    created_time = models.DateTimeField(verbose_name=u'生成时间', auto_now_add=True, editable=False)
    modified_time = models.DateTimeField(verbose_name=u'修改时间', auto_now=True, editable=False)

    class Meta:
        app_label = 'finance'


class AgriculturalBankEncKey(models.Model):
    """
    农行通信加密密钥
    """
    package = models.CharField(verbose_name=u'包密钥', max_length=128)
    mac = models.CharField(verbose_name=u'mac密钥', max_length=128)
    pin = models.CharField(verbose_name=u'关键域密钥', max_length=128)

    expire_time = models.DateTimeField(verbose_name=u'过期时间', editable=False)
    created_time = models.DateTimeField(verbose_name=u'生成时间', auto_now_add=True, editable=False)
    modified_time = models.DateTimeField(verbose_name=u'修改时间', auto_now=True, editable=False)

    class Meta:
        app_label = 'finance'


TRADE_SOURCE_CHOICES = (('B', u'银行'), ('I', u'市场'))
BUSI_TYPE_CHOICES = (('6', u'保证金'), ('7', u'贷款'))
SIGN_EVENT_CHOICES = ((1, u'出金'), (2, u'入金'))

# 农行签约日志
class AbSignInContractLog(models.Model):
    STATUS_CHOICES = ((1, u'成功'), (2, u'失败'), (3, u'未提交'), (4, u'处理中'))
    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(User)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=3)     # 交易状态
    code = models.CharField(max_length=10, default='')
    info = models.CharField(max_length=200, default='', blank=True)

    entrust_way = models.CharField(default='I', max_length=6)   # 委托方式
    trade_source = models.CharField(choices=TRADE_SOURCE_CHOICES, default='I', max_length=6)  # 交易发起方
    inst_serial = models.CharField(unique=True,  default='', blank=True, max_length=60)  # 市场流水号
    serial_no = models.CharField(db_index=True, default='', blank=True,  max_length=60)  # 流水号
    inst_no = models.CharField(default=AgriculturalBankTradeConstData.INST_NO, max_length=30)  # 市场编号
    busi_type = models.CharField(choices=BUSI_TYPE_CHOICES, default=BUSI_TYPE_CHOICES[0][0], max_length=6)    # 业务类别
    money_kind = models.CharField(default='01', max_length=6)  # 币种 01：人民币
    client_no = models.CharField(default='', null=True, blank=True,  max_length=20)
    bank_account = models.CharField(max_length=30)
    inst_func_acc = models.CharField(max_length=30)
    client_name = models.CharField(max_length=30)
    cert_type = models.CharField(default='110001', max_length=10)  # 证件类型
    cert_id = models.CharField(max_length=30)  # 证件
    inst_branch = models.CharField(max_length=30, default=AgriculturalBankTradeConstData.DEFAULT_INST_BRANCH, blank=True)  # 市场营业部编号
    trade_branch = models.CharField(max_length=200, default='', blank=True)  # 交易银行网点

    gender = models.CharField(default='', blank=True, null=True, max_length=4)
    nationality = models.CharField(default='', blank=True, null=True, max_length=20)

    tel_no = models.CharField(default='', blank=True, null=True, max_length=30)
    fax_no = models.CharField(default='', blank=True, null=True, max_length=30)
    mobile = models.CharField(default='', blank=True, null=True, max_length=30)
    email = models.CharField(default='', blank=True, null=True, max_length=50)
    address = models.CharField(default='', blank=True, null=True, max_length=100)
    postcode = models.CharField(default='', blank=True, null=True, max_length=20)

    agent_gender = models.CharField(default='', blank=True, null=True, max_length=4)
    agent_nationality = models.CharField(default='', blank=True, null=True, max_length=20)
    agent_tel_no = models.CharField(default='', blank=True, null=True, max_length=30)
    agent_fax_no = models.CharField(default='', blank=True, null=True, max_length=30)
    agent_mobile = models.CharField(default='', blank=True, null=True, max_length=30)
    agent_email = models.CharField(default='', blank=True, null=True, max_length=50)
    agent_address = models.CharField(default='', blank=True, null=True, max_length=100)
    agent_postcode = models.CharField(default='', blank=True, null=True, max_length=20)


    trade_date = models.DateField(verbose_name=u'交易日期', blank=True, null=True, editable=False)
    trade_time = models.TimeField(verbose_name=u'交易时间', blank=True, null=True, editable=False)

    summary = models.CharField(max_length=1000, blank=True, default='')  # 摘要

    user_comment = models.CharField(max_length=200, blank=True, default='')  # 备注
    sys_comment = models.CharField(max_length=2000, blank=True, default='')  # 备注

    created_time = models.DateTimeField(verbose_name=u'生成时间', auto_now_add=True, editable=False)
    modified_time = models.DateTimeField(verbose_name=u'修改时间', auto_now=True, editable=False)

    class Meta:
        app_label = 'finance'


# 农行解约日志
class AbRescindContractLog(models.Model):
    STATUS_CHOICES = ((1, u'成功'), (2, u'失败'), (3, u'未提交'), (4, u'处理中'))
    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(User)

    entrust_way = models.CharField(default='', max_length=6)   # 委托方式
    trade_source = models.CharField(choices=TRADE_SOURCE_CHOICES, max_length=6)  # 交易发起方
    inst_serial = models.CharField(unique=True,  default='', blank=True, max_length=60)  # 市场流水号
    serial_no = models.CharField(db_index=True, default='', blank=True,  max_length=60)  # 流水号
    inst_no = models.CharField(default=AgriculturalBankTradeConstData.INST_NO, max_length=30)  # 市场编号
    busi_type = models.CharField(choices=BUSI_TYPE_CHOICES, default=BUSI_TYPE_CHOICES[0][0], max_length=6)    # 业务类别
    money_kind = models.CharField(default='01', max_length=6)  # 币种 01：人民币
    client_no = models.CharField(default='', max_length=20)
    bank_account = models.CharField(max_length=30)
    inst_func_acc = models.CharField(max_length=30)
    client_name = models.CharField(max_length=30)
    cert_type = models.CharField(default='110001', max_length=10)  # 证件类型
    cert_id = models.CharField(max_length=30)  # 证件
    inst_branch = models.CharField(max_length=30, default='', blank=True)  # 市场营业部编号
    trade_branch = models.CharField(max_length=200, default='', blank=True)  # 交易银行网点

    status = models.SmallIntegerField(choices=STATUS_CHOICES)     # 交易状态
    summary = models.CharField(max_length=1000, blank=True, default='')  # 摘要

    code = models.CharField(max_length=10, default='')
    info = models.CharField(max_length=200, default='', blank=True)

    user_comment = models.CharField(max_length=200, blank=True, default='')  # 备注
    sys_comment = models.CharField(max_length=2000, blank=True, default='')  # 备注

    created_time = models.DateTimeField(verbose_name=u'生成时间', auto_now_add=True, editable=False)
    modified_time = models.DateTimeField(verbose_name=u'修改时间', auto_now=True, editable=False)

    class Meta:
        app_label = 'finance'


# 农行出入金日志
class AbRechargeWithdrawLog(models.Model):
    STATUS_CHOICES = ((1, u'成功'), (2, u'失败'))
    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(User)

    entrust_way = models.CharField(default='', max_length=6)   # 委托方式
    trade_source = models.CharField(choices=TRADE_SOURCE_CHOICES, max_length=6)  # 交易发起方
    inst_serial = models.CharField(unique=True,  default='', blank=True, max_length=60)  # 市场流水号
    host_serial = models.CharField(default='', blank=True, max_length=60)  #主机流水号  银行响应报文
    serial_no = models.CharField(db_index=True, default='', blank=True, max_length=60)  # 流水号
    inst_no = models.CharField(default=AgriculturalBankTradeConstData.INST_NO, max_length=30)  # 市场编号
    busi_type = models.CharField(choices=BUSI_TYPE_CHOICES, default=BUSI_TYPE_CHOICES[0][0], max_length=6)    # 业务类别
    money_kind = models.CharField(default='01', max_length=6)  # 币种 01：人民币
    client_no = models.CharField(default='',  max_length=20)
    bank_account = models.CharField(max_length=30, default='')
    inst_func_acc = models.CharField(max_length=30)  # 市场资金帐号
    settle_acc = models.CharField(max_length=30, default='')  # 市场结算账号

    transfer_amount = models.DecimalField(max_digits=30, decimal_places=5)   # 转账金额
    enable_bala = models.CharField(default='',  max_length=30)  # 可用余额 银行响应
    client_name = models.CharField(max_length=30)
    trade_branch = models.CharField(max_length=200, default='', blank=True)  # 交易银行网点

    cash_ex_code = models.CharField(default='2', max_length=10)  #汇钞标志  2:钞 1：汇

    money_usage = models.CharField(max_length=200, default='', blank=True) # 款项用途
    money_usage_info = models.CharField(max_length=200, default='', blank=True) # 款项用途描述

    taster = models.CharField(max_length=200, default='', blank=True) # 审批人
    broker = models.CharField(max_length=200, default='', blank=True) # 经办人
    inst_ratifier = models.CharField(max_length=200, default='', blank=True) # 市场审批人

    event = models.SmallIntegerField(choices=SIGN_EVENT_CHOICES)  # 出金或入金
    status = models.SmallIntegerField(choices=STATUS_CHOICES)     # 交易状态
    code = models.CharField(max_length=10, default='')
    info = models.CharField(max_length=200, default='', blank=True)

    summary = models.CharField(max_length=200, default='', blank=True)  # 摘要

    user_comment = models.CharField(max_length=200, blank=True, default='')  # 备注
    sys_comment = models.CharField(max_length=2000, blank=True, default='')  # 备注

    trade_date = models.DateField(verbose_name=u'交易日期', blank=True, null=True, editable=False)
    trade_time = models.TimeField(verbose_name=u'交易时间', blank=True, null=True, editable=False)

    created_time = models.DateTimeField(verbose_name=u'生成时间', auto_now_add=True, editable=False)
    modified_time = models.DateTimeField(verbose_name=u'修改时间', auto_now=True, editable=False)

    class Meta:
        app_label = 'finance'


# 农行出入金流水
class AbRechargeWithdrawHistory(models.Model):
    STATUS_CHOICES = ((1, u'成功'), (2, u'失败'))
    id = models.AutoField(primary_key=True)

    inst_no = models.CharField(default=AgriculturalBankTradeConstData.INST_NO, max_length=30)  # 市场编号
    client_no = models.CharField(default='', max_length=20)
    client_name = models.CharField(max_length=30)
    bank_account = models.CharField(max_length=30)

    inst_func_acc = models.CharField(max_length=30)
    user = models.ForeignKey(User)

    trans_code = models.CharField(max_length=30)  # =交易码
    trans_name = models.CharField(max_length=30)  # 交易名称

    occur_balance = models.DecimalField(max_digits=30, decimal_places=5)   # 发生金额

    trade_date = models.DateField(blank=True, null=True)   # 交易日期
    trade_time = models.TimeField(blank=True, null=True)   # 交易时间

    status = models.SmallIntegerField(choices=STATUS_CHOICES)     # 出入金状态

    inst_serial = models.CharField(db_index=True, default='', blank=True, max_length=60)  # 市场流水号
    serial_no = models.CharField(db_index=True, default='', blank=True,  max_length=60)  # 流水号

    cash_ex_code = models.CharField(default='2', max_length=10)  #汇钞标志  2:钞 1：汇

    entrust_way = models.CharField(default='', max_length=6)   # 委托方式
    busi_type = models.CharField(choices=BUSI_TYPE_CHOICES, default=BUSI_TYPE_CHOICES[0][0], max_length=6)    # 业务类别
    money_kind = models.CharField(default='01', max_length=6)  # 币种 01：人民币
    err_msg= models.CharField(max_length=120, blank=True, default='')  # 错误信息

    comment = models.CharField(max_length=200, blank=True, default='')  # 备注

    created_time = models.DateTimeField(verbose_name=u'生成时间', auto_now_add=True, editable=False)
    modified_time = models.DateTimeField(verbose_name=u'修改时间', auto_now=True, editable=False)

    class Meta:
        app_label = 'finance'


# 银行对账单
class AbBankStatement(models.Model):
    id = models.AutoField(primary_key=True)

    trans_date = models.DateField(verbose_name=u'交易日期', editable=False)
    trans_time = models.TimeField(verbose_name=u'交易时间', blank=True, null=True, editable=False)
    bank_account = models.CharField(max_length=30, default='')
    source_side = models.CharField(choices=TRADE_SOURCE_CHOICES, blank=True, null=True, max_length=6)
    trans_code = models.CharField(max_length=20)  # 交易码

    serial_no  = models.CharField(db_index=True, max_length=60)  # 流水号
    inst_serial = models.CharField(unique=True,  default='', blank=True, max_length=60)  # 市场流水号

    amount = models.DecimalField(max_digits=30, decimal_places=5)   # 转账金额
    client_no = models.CharField(max_length=20)
    inst_no = models.CharField(max_length=30)  # 市场编号
    busi_type = models.CharField(choices=BUSI_TYPE_CHOICES, default=BUSI_TYPE_CHOICES[0][0], max_length=6)    # 业务类别
    money_kind = models.CharField(default='01', max_length=6)  # 币种 01：人民币
    inst_func_acc = models.CharField(max_length=30)  # 市场资金帐号
    user_id = models.IntegerField()  # 用户id

    charge = models.DecimalField(max_digits=30, decimal_places=5)   # 手续费

    reserve1 = models.CharField(default='',  max_length=300)
    reserve2 = models.CharField(default='',  max_length=300)

    created_time = models.DateTimeField(verbose_name=u'生成时间', auto_now_add=True, editable=False)
    modified_time = models.DateTimeField(verbose_name=u'修改时间', auto_now=True, editable=False)

    class Meta:
        app_label = 'finance'


# 农行出入金错误数据
class AbRechargeWithdrawErrorStatus(models.Model):
    STATUS_CHOICES = ((1, u'银行成功市场失败'), (2, u'银行失败市场成功'), (3, u'银行市场金额不匹配'))
    RESULT_CHOICES = ((1, u'未处理'), (2, u'处理中'), (3, u'已修正'))

    id = models.AutoField(primary_key=True)

    status = models.IntegerField(choices=STATUS_CHOICES)
    bank_statement = models.ForeignKey(AbBankStatement,on_delete= models.PROTECT, blank=True, null=True)
    market_statement = models.ForeignKey(AbRechargeWithdrawLog, on_delete=models.PROTECT, blank=True, null=True)

    result = models.IntegerField(choices=RESULT_CHOICES, default=1)
    fixed_user = models.CharField(default='', max_length=20)
    fixed_event = models.CharField(default='', max_length=20)
    fixed_comment = models.CharField(default='', max_length=500)
    fixed_time = models.DateTimeField(verbose_name=u'修正时间',null=True, blank=True,  editable=False)

    created_time = models.DateTimeField(verbose_name=u'生成时间', auto_now_add=True, editable=False)
    modified_time = models.DateTimeField(verbose_name=u'修改时间', auto_now=True, editable=False)

    class Meta:
        app_label = 'finance'


class WxPaymentTradeOrder(models.Model):
    """
    微信支付订单
    """

    STATUS_CHOICES = ((0, u'进行中'), (1, u'支付失败'), (2, u'预支付中'), (3, u'支付成功'),
                      (4, u'未支付'), (5, u'已关闭'), (6, u'已撤销'), (7, u'用户支付中'), (8, u'转入退款'),
                      (9, u'统一下单失败'))
    SOURCE_TYPE_CHOICES = (('0', '网页扫码支付'), ('1', 'android'), ('2', 'ios'))

    trade_no = models.CharField(max_length=32, primary_key=True)
    uid = models.IntegerField()
    product_id = models.CharField(max_length=100)   # 平台订单号
    device_info = models.CharField(max_length=100, default='WEB')

    body = models.CharField(max_length=40, blank=True, default='')
    detail = models.CharField(max_length=300, blank=True, default='')
    attach = models.CharField(max_length=150, blank=True, default='')   # 附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据

    transaction_id = models.CharField(max_length=100, default='')  # 微信支付订单号
    total_fee = models.IntegerField()   #分
    spbill_create_ip = models.CharField(max_length=30, default='')  # 终端ip

    start_time = models.DateTimeField()
    time_expire = models.DateTimeField()  # 订单失效时间
    end_time = models.DateTimeField(blank=True, null=True)  # 支付完成时间
    trade_type = models.CharField(max_length=10, default='NATIVE')  # JSAPI，NATIVE，APP
    limit_pay = models.CharField(max_length=10, blank=True, default='no_credit')  # 指定支付方式.no_credit--指定不能使用信用卡支付
    openid = models.CharField(max_length=10, blank=True, default='')  # 用户标识 trade_type=JSAPI，此参数必传，用户在商户appid下的唯一标识

    is_order_over = models.BooleanField(default=False)  #商品订单是否已经完成
    order_status = models.SmallIntegerField(default=0, choices=STATUS_CHOICES)   # 订单状态
    order_status_desc = models.CharField(max_length=200, default='')   # 交易状态描述,对当前查询订单状态的描述和下一步操作的指引

    original_source = models.SmallIntegerField(choices=SOURCE_TYPE_CHOICES)
    appid = models.CharField(max_length=32)
    mch_id = models.CharField(max_length=32)

    wx_return_code = models.CharField(max_length=16, blank=True, null=True, default='')
    wx_return_msg = models.CharField(max_length=200, blank=True, null=True, default='')
    wx_result_code = models.CharField(max_length=16, blank=True, null=True, default='')
    wx_err_code = models.CharField(max_length=100, blank=True, null=True, default='')
    wx_err_code_des = models.CharField(max_length=200, blank=True, null=True, default='')

    # 微信生成的预支付回话标识，用于后续接口调用中使用，该值有效期为2小时
    wx_prepay_id = models.CharField(max_length=70, blank=True, null=True, default='')
    # trade_type为NATIVE时有返回，可将该参数值生成二维码展示出来进行扫码支付
    code_url = models.CharField(max_length=70, blank=True, null=True, default='')
    code_url_img_path = models.CharField(max_length=300, blank=True, null=True, default='')
    code_url_img_url = models.CharField(max_length=300, blank=True, null=True, default='')

    wx_response = models.CharField(max_length=1000, blank=True, null=True, default='')

    comment = models.CharField(max_length=600, default='')

    creation_time = models.DateTimeField(auto_now_add=True)
    modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'finance'


class WxPaymentBill(models.Model):
    TRADE_TYPE_CHOICES = (('0', '网页扫码支付'), ('1', 'android'), ('2', 'ios'))
    BILL_TYPE_CHOICES = (('ALL', u'返回当日所有订单信息，默认值'), ('SUCCESS',u'返回当日成功支付的订单'),
    ('REFUND',u'返回当日退款订单'), ('REVOKED', u'已撤销的订单'))

    trade_no = models.CharField(max_length=32, primary_key=True)                                    #商户订单号
    wx_transaction_id = models.CharField(max_length=100, default='')                           #微信订单号

    bill_type = models.CharField(choices=BILL_TYPE_CHOICES, max_length=10)  #订单类型

    trade_time = models.DateTimeField()                                  #交易时间
    mch_id = models.CharField(max_length=32)                                      #商户号
    sub_mch_id = models.CharField(max_length=32, default='')                        #子商户号
    appid = models.CharField(max_length=32)                                         #公众账号ID
    device_no = models.CharField(max_length=32, default='')                                   #设备号
    open_id = models.CharField(max_length=128, default='')                                     #用户标识,用户在商户appid下的唯一标识
    trade_type = models.CharField(max_length=32, default='')                                  #交易类型
    trade_status = models.CharField(max_length=30)                                #交易状态
    bank_type = models.CharField(max_length=30)                              #付款银行
    fee_type = models.CharField(max_length=30)                               #货币种类
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)                                #总金额
    coupon_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)                           #代金券或立减优惠金额
    refund_request_time = models.DateTimeField(blank=True, null=True)                         #退款申请时间
    refund_success_time = models.DateTimeField(blank=True, null=True)                         #退款成功时间
    wx_refund_no = models.CharField(max_length=32, default='')                               #微信退款单号
    mch_refund_no = models.CharField(max_length=28, default='')                               #商户退款单号
    refund_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)                                  #退款金额
    refund_coupon_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)                         #代金券或立减优惠退款金额
    refund_type = models.CharField(max_length=50, default='')                                 #退款类型
    refund_status = models.CharField(max_length=50, default='')                               #退款状态
    trade_name = models.CharField(max_length=200, default='')                                  #商品名称
    trade_attach = models.CharField(max_length=200, default='')                                #商户数据包
    service_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)                   #手续费
    rate = models.CharField(max_length=20, default='')                                        #费率

    creation_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'finance'


class AliPaymentTradeOrder(models.Model):
    """
    支付宝支付订单
    """
    STATUS_CHOICES = ((0, u'进行中'), (1, u'支付失败'), (2, u'预支付中'), (3, u'交易成功，且可对该交易做操作，如：多级分润、退款等'),
                      (9, u'交易成功且结束，不可再做任何操作'),
                      (10, u'等待卖家收款（买家付款后，如果卖家账号被冻结）'),
                      (101, u'转入退款'),(102, u'退款成功'),(103, u'退款关闭'),
        )
    PAY_SERVICE_TYPE = (('direct_pay', u'即时到账'), ('bank_pay', u'网银支付'))
    # 5:在指定时间段内未支付时关闭的交易；在交易完成全额退款成功时关闭的交易。

    # SOURCE_TYPE_CHOICES = (('0', '网页扫码支付'), ('1', 'android'), ('2', 'ios'))

    out_trade_no = models.CharField(max_length=32, primary_key=True)
    uid = models.IntegerField()
    order_no = models.CharField(max_length=100)   # 平台订单号

    payment_type = models.CharField(max_length=4, default='1')      # 支付类型

    pay_service_type = models.CharField(choices=PAY_SERVICE_TYPE, max_length=20)  # 业务类型


    seller_id = models.CharField(max_length=16)
    seller_email = models.CharField(max_length=100)
    seller_account_name = models.CharField(max_length=100)

    subject = models.CharField(max_length=40, blank=True, default='')
    body = models.CharField(max_length=300, blank=True, default='')

    # anti_phishing_key=
    extra_common_param = models.CharField(max_length=100, blank=True, default='')   #公用回传参数
    extend_param = models.CharField(max_length=100, blank=True, default='')   #公用业务扩展参数.用于商户的特定业务信息的传递，只有商户与支付宝约定了传递此参数且约定了参数含义，此参数才有效。
    it_b_pay = models.CharField(max_length=10, blank=True, default='')  # 超时时间

    total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)       # 元

    #以下是支付宝通知信息
    notify_id = models.CharField(max_length=100, blank=True, default='')  # 通知校验ID
    notify_time = models.CharField(max_length=30, blank=True, default='')  # 通知时间
    notify_type = models.CharField(max_length=30, blank=True, default='')  # 通知时间

    gmt_create = models.DateTimeField(blank=True, null=True)  # 交易生成时间
    gmt_payment = models.DateTimeField(blank=True, null=True)  # 交易付款时间
    gmt_close = models.DateTimeField(blank=True, null=True)  # 交易关闭时间
    gmt_last_modified_time = models.DateTimeField(blank=True, null=True)  # 交易最后一次修改时间
    time_out = models.DateTimeField(blank=True, null=True)  # 主超时时间
    time_out_type = models.CharField(max_length=30, blank=True, default='')  # 主超时时间类型

    bank_seq_no = models.CharField(max_length=70, blank=True, default='')  # 网银流水号。只有开通了纯网关和伪网关的商户，才返回该参数。


    refund_status = models.CharField(max_length=30, blank=True, default='')  # 退款状态
    gmt_refund = models.DateTimeField(blank=True, null=True)  # 退款时间
    refund_total_fee = models.IntegerField(default=0)  # 退款累计金额

    buyer_id = models.CharField(max_length=30, blank=True, default='')  # 买家支付宝账户号
    buyer_email = models.CharField(max_length=100, blank=True, default='')  #买家支付宝账号

    agent_user_id = models.CharField(max_length=30, blank=True, default='')  # 信用支付购票员的代理人ID

    transaction_id = models.CharField(max_length=100, default='')  # 支付宝支付订单号

    start_time = models.DateTimeField()

    ali_service = models.CharField(max_length=50, default='create_direct_pay_by_user', blank=True)  # 支付宝支付服务
    is_order_over = models.BooleanField(default=False)  #商品订单是否已经完成
    order_status = models.SmallIntegerField(default=0, choices=STATUS_CHOICES)   # 订单状态

    ali_return_code = models.CharField(max_length=16, blank=True, null=True, default='')
    ali_return_msg = models.CharField(max_length=200, blank=True, null=True, default='')
    ali_result_code = models.CharField(max_length=16, blank=True, null=True, default='')
    ali_err_code = models.CharField(max_length=100, blank=True, null=True, default='')
    ali_err_code_des = models.CharField(max_length=200, blank=True, null=True, default='')
    ali_trade_status = models.CharField(max_length=100, blank=True, default='')

    ali_response = models.CharField(max_length=1000, blank=True, null=True, default='')

    comment = models.CharField(max_length=600, default='')

    creation_time = models.DateTimeField(auto_now_add=True)
    modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'finance'


class AliPaymentBill(models.Model):

    # 交易金额单位为元
    trans_date = models.DateTimeField()    # 交易付款时间	例子：	订单的付款时间（非订单创建时间）。格式为yyyy-MM-ddHH:mm:ss。
    transaction_id = models.CharField(max_length=70, default='', db_index=True)    # 支付宝交易号	例子：	支付宝交易号。 对应支付宝trade_no。同一订单号，支付、退款会有不同交易号
    merchant_out_order_no = models.CharField(max_length=70, default='',  db_index=True)    # 商户订单号	例子：	商户订单号。
    trans_out_order_no = models.CharField(max_length=70, default='', db_index=True)    # 订单号	例子：	订单号。
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)     # 交易总金额	例子：	交易总金额。

    trade_refund_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)     # 累积退款金额	例子：	累积退款金额。

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)     # 余额
    income = models.DecimalField(max_digits=10, decimal_places=2, default=0)     # 收入金额	例子：	收入金额。
    outcome = models.DecimalField(max_digits=10, decimal_places=2, default=0)     # 支出金额	例子：	支出金额。

    partner_id = models.CharField(max_length=40, default='')    # 合作者身份ID	例子：	创建交易的合作者身份ID。支付宝账号对应的支付宝唯一用户号，以2088开头的纯16位数字。

    sub_trans_code_msg = models.CharField(max_length=30, default='')    # 子业务类型	例子：	子业务类型代码，取值范围参见“7.4子业务类型列表”中的“含义”。
    trans_code_msg = models.CharField(max_length=100, blank=True,  default='')    # 业务类型	例子：	业务类型。取值范围：z转账z收费z充值z提现z退票z在线支付

    bank_name = models.CharField(max_length=50, default='')    # 银行名称	例子：	银行名称。
    bank_account_no = models.CharField(max_length=40, default='')    # 银行账号	例子：	银行账号。
    bank_account_name = models.CharField(max_length=40, default='')    # 银行账户名字	例子：	银行账户名字。
    memo = models.CharField(max_length=200, default='')    # 备注	例子：	备注信息。
    buyer_account = models.CharField(max_length=60, default='')    # 买家支付宝人民币资金账号	例子：	买家支付宝人民币资金账号（user_id+0156）
    seller_account = models.CharField(max_length=60, default='')    # 卖家支付宝人民币资金账号	例子：	卖家支付宝人民币资金账号（user_id+0156）。
    seller_fullname = models.CharField(max_length=60, default='')    # 卖家姓名	例子：	卖家姓名。
    currency = models.CharField(max_length=10, default='')    # 货币代码	例子：	156（人民币）
    deposit_bank_no = models.CharField(max_length=100, default='')    # 充值网银流水号	例子：	充值网银流水号。
    goods_title = models.CharField(max_length=200, default='')    # 商品名称	例子：	商品名称。
    iw_account_log_id = models.CharField(max_length=100, default='')    # 账务序列号	例子：	支付宝账务序列号。
    trans_account = models.CharField(max_length=100, default='')    # 账务本方支付宝人民币资金账号	例子：	账务本方支付宝人民币资金账号（user_id+0156）。
    other_account_email = models.CharField(max_length=100, default='')    # 账务对方邮箱	例子：	账务对方邮箱。
    other_account_fullname = models.CharField(max_length=100, default='')    # 账务对方全称	例子：	账务对方全称。
    other_user_id = models.CharField(max_length=100, default='')    # 账务对方支付宝用户号	例子：	账务对方支付宝用户号。

    service_fee = models.CharField(max_length=100, default='')    # 交易服务费	例子：	在特定的交易中使用，目前主要用于COD买家服务费（表示物流商向买家收取的费用，卖家创建交易时设置）等。注意：该参数不表示支付宝收费。
    service_fee_ratio = models.CharField(max_length=20, default='')    # 交易服务费率	例子：	交易服务费所占比例，在特定的交易中使用，目前主要用于COD买家服务费费率（卖家创建交易时设置）。注意：该参数不表示支付宝收费费率。


    sign_product_name = models.CharField(max_length=128, default='')    # 签约产品	例子：	签约产品，此字段取值会展示商户与支付宝实际签约的产品信息，接口联调之前可咨询支付宝技术人员，会根据签约情况提供相应的签约产品取值，如：高级即时到账、机票即时到账、wap快捷支付等。
    rate = models.CharField(max_length=20, default='')    # 费率	例子：	该笔业务所对应的支付宝收费费率。

    creation_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'finance'
