# -*- coding: utf-8 -*-

from stars.apps.customer.safety.common_const import Const


class _AliPayConfig(Const):
    PID = '2088121434357637'  # PID
    SELLER_ID = PID
    SELLER_EMAIL = ''
    INPUT_CHARSET = 'utf-8'
    SIGN_TYPE = 'MD5'

    ALI_PAY_GATEWAY_NEW = "https://mapi.alipay.com/gateway.do?"

    # IP = '139.129.131.153'
    #
    MD5_KEY = '7cmy7dn2tvglqiuppj5yh15o8jcjni4m'

    MY_RSA_PRIVATE_KEY = '-----BEGIN RSA PRIVATE KEY-----\n' \
                     + 'MIICXAIBAAKBgQCpiRqHEqp9ESeiIh76wwP0HzNLlVcObyMiRAFzuF49YXKiiDMB\n' \
                     + '4oUi2fK8yM15XUuP11OkK7BwPGm0jL7LGIUYsvLMqH2FM87ufM39dxrbFcZE+W/r\n' \
                     + 'YLYWzdWnWhcdEIo4nj2ztEd5J7vv9ZA2OVG4JOhGj0cL6T2nCx4gdqxaGwIDAQAB\n' \
                     + 'AoGAYpyE+Zw53pVj4ELIkkNswUqEo6oyAQtT/FJiJdVPu5Q7AZ8HTEld92+eaYDD\n' \
                     + 'Q5yonvo4hH2FG0OImKRlNe0FPO3YdnzpZYpLBAC1g+N2dpZULJrIcr5uJnSNWOnK\n' \
                     + '2apkrHSuIgNmHPyHwu9vmFxuH/wD4iK8JqnLi8dh7elKQcECQQDcoJHP9C2fr+lP\n' \
                     + 'SpODKyQlbYKKX1MgkFr6Rmf6RWLHeFiUlvWsHcODVt9tSE7hAoGvRywUfSEGUH8/\n' \
                     + 'COBFLlDvAkEAxLeGuSltJruxqfvxLB31SA+sd6B8snfmd0m+jB3+eycaskbn0diV\n' \
                     + 'A2cOVcMmf6V3Lw/zYIdXv0q1BVDL216xlQJAVN1q2RvqxMcMrpRYI5dfown5sbIz\n' \
                     + 'Lo54gFa+vjUcZu/y2s0qmNcmEopDDS1IMiMdsUdmPEdZga1LFPscEWBcfwJAArIJ\n' \
                     + 'FIxuxHMZ8hxTp6kZbU1ZraHzU3a1H7lQ9RaMIB/fC8ZQ8t0m3Y8R8TblViZsRabQ\n' \
                     + 'TOhN2X8qj9IVmQHpKQJBAIc0QDK/qKTi3e8rN6DJ5OVzrGkzxE/l8A5aFbZR1WeZ\n' \
                     + 'DAB0MBbHeuYkPAzOeovbACEjIe7VezMfg7uaH7wtIdo=\n' \
                     + '-----END RSA PRIVATE KEY-----'
    MY_RSA_PUBLIC_KEY = '-----BEGIN PUBLIC KEY-----\n' \
                     + 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCpiRqHEqp9ESeiIh76wwP0HzNL\n' \
                     + 'lVcObyMiRAFzuF49YXKiiDMB4oUi2fK8yM15XUuP11OkK7BwPGm0jL7LGIUYsvLM\n' \
                     + 'qH2FM87ufM39dxrbFcZE+W/rYLYWzdWnWhcdEIo4nj2ztEd5J7vv9ZA2OVG4JOhG\n' \
                     + 'j0cL6T2nCx4gdqxaGwIDAQAB\n' \
                     + '-----END PUBLIC KEY-----\n'


    ALI_RSA_PUBLIC_KEY = '-----BEGIN PUBLIC KEY-----\n' \
                         + 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCnxj/9qwVfgoUh/y2W89L6BkRA\n' \
                         + 'FljhNhgPdyPuBV64bfQNN1PjbCzkIM6qRdKBoLPXmKKMiFYnkd6rAoprih3/PrQE\n' \
                         + 'B/VsW8OoM8fxn67UDYuyBTqA23MML9q1+ilIZwBC2AQ2UBVOrFXfFl75p6/B5Ksi\n' \
                         + 'NG9zpgmLCUYuLkxpLQIDAQAB\n' \
                         + '-----END PUBLIC KEY-----'
    # MD5_KEY = 'xxxxxxxxxxxxxxxxxxxxxxx'
    #
    # TRADE_EXPIRE_MINITUS = 5

    # finance-wx-result-notification
    NOTIFY_URL = 'http://www.ltbh365.com/' + 'accounts/fin/ali/pay/result/notification/'
    RETURN_URL = 'http://www.ltbh365.com/' + 'accounts/fin/ali/pay/result/return/'
    ERROR_NOTIFY_URL = 'http://www.ltbh365.com/' + 'accounts/fin/ali/pay/result/error/notification/'


class _AliPayConstData(Const):
    CommonErrorCodeMsg = {
            'ILLEGAL_SIGN': '签名不正确',
            'ILLEGAL_DYN_MD5_KEY': '动态密钥信息错误',
            'ILLEGAL_ENCRYPT': '加密不正确',
            'ILLEGAL_ARGUMENT': '参数不正确',
            'ILLEGAL_SERVICE': '接口名称不正确',
            'ILLEGAL_PARTNER': '合作伙伴ID不正确',
            'ILLEGAL_EXTERFACE': '接口配置不正确',
            'ILLEGAL_PARTNER_EXTERFACE': '合作伙伴接口信息不正确',
            'ILLEGAL_SECURITY_PROFILE': '未找到匹配的密钥配置',
            'ILLEGAL_AGENT': '代理ID不正确',
            'ILLEGAL_SIGN_TYPE': '签名类型不正确',
            'ILLEGAL_CHARSET': '字符集不合法',
            'ILLEGAL_CLIENT_IP': '客户端IP地址无权访问服务',
            'ILLEGAL_DIGEST_TYPE': '摘要类型不正确',
            'ILLEGAL_DIGEST': '文件摘要不正确',
            'ILLEGAL_FILE_FORMAT': '文件格式不正确',
            'ILLEGAL_ENCODING': '不支持该编码类型',
            'ILLEGAL_REQUEST_REFERER': '防钓鱼检查不支持该请求来源',
            'ILLEGAL_ANTI_PHISHING_KEY': '防钓鱼检查非法时间戳参数',
            'ANTI_PHISHING_KEY_TIMEOUT': '防钓鱼检查时间戳超时',
            'ILLEGAL_EXTER_INVOKE_IP': '防钓鱼检查非法调用IP',
            'ILLEGAL_NUMBER_FORMAT': '数字格式不合法',
            'ILLEGAL_INTEGER_FORMAT': 'Int类型格式不合法',
            'ILLEGAL_MONEY_FORMAT': '金额格式不合法',
            'ILLEGAL_DATA_FORMAT': '日期格式错误',
            'REGEXP_MATCH_FAIL': '正则表达式匹配失败',
            'ILLEGAL_LENGTH': '参数值长度不合法',
            'PARAMTER_IS_NULL': '参数值为空',
            'HAS_NO_PRIVILEGE': '无权访问',
            'SYSTEM_ERROR': '支付宝系统错误',
            'SESSION_TIMEOUT': 'session超时',
            'ILLEGAL_TARGET_SERVICE': '错误的target_service',
            'ILLEGAL_ACCESS_SWITCH_SYSTEM': 'partner不允许访问该类型的系统',
            'ILLEGAL_SWITCH_SYSTEM': '切换系统异常',
            'EXTERFACE_IS_CLOSED': '接口已关闭',
    }

    # 即时到账业务错误码
    DirectPayErrorCodeMsg = {
        'SELLER_NOT_IN_SPECIFIED_SELLERS': '抱歉，该收款账户不是指定的收款账户，请确认参数是否正确或咨询您的客户经理。',
        'TRADE_SELLER_NOT_MATCH': '抱歉，该笔交易的卖家已不存在，请联系正确的卖家重新创建交易进行付款。',
        'TRADE_BUYER_NOT_MATCH': '抱歉，您本次支付使用的账户与原先的不一致，请使用原来的账户，或重新创建交易付款。',
        'ILLEGAL_FEE_PARAM': '抱歉，金额传递错误，请确认参数是否正确或咨询您的客户经理。',
        'SUBJECT_MUST_NOT_BE_NULL': '商品名不能为空。',
        'TRADE_PRICE_NOT_MATCH': '抱歉，该商品的交易单价与原先的不一致，请重新创建交易付款。',
        'TRADE_QUANTITY_NOT_MATCH': '抱歉，该商品的购买数量与原先的不一致，请重新创建交易付款。',
        'TRADE_TOTALFEE_NOT_MATCH': '抱歉，该商品的交易金额与原先的不一致，请重新创建交易付款。',
        'TRADE_NOT_ALLOWED_PAY': '抱歉，您不能进行本次支付，请查看该交易是否已超时或已被关闭等。',
        'DIRECT_PAY_WITHOUT_CERT_CLOSE': '未开通非证书余额支付，无法完成支付。',
        'FAIL_CREATE_CASHIER_PAY_ORDER': '抱歉，系统异常，无法创建本次收银台支付订单，请稍后再试。',
        'ILLEGAL_EXTRA_COMMON_PARAM': '抱歉，接口通用回传参数格式不正确，请联系您的商户。',
        'ILLEGAL_PAYMENT_TYPE': '抱歉，接口传递的Payment_type参数错误，请联系您的商户。',
        'NOT_SUPPORT_GATEWAY': '抱歉，商户网关配置出错，请联系您的商户。',
        'BUYER_SELLER_EQUAL': '抱歉，买家和卖家不能是同一个账户。',
        'SELLER_NOT_EXIST': '抱歉，卖家账户经验证不存在，请联系您的商户。',
        'ILLEGAL_ARGUMENT': '抱歉，商户传递的接口参数错误，请联系您的商户。',
        'TRADE_NOT_FOUND': '根据交易号无法找到交易。',
        'TRADE_GOOD_INFO_NOT_FOUND': '根据交易号无法找到交易详情。',
        'BUYER_EMAIL_ID_MUST_NULL': '抱歉，该笔交易的买家账户必须为空，请联系您的商户。',
        'PRODUCT_NOT_ALLOWED': '您未开通此产品，暂时无法使用本服务。',
        'ROYALTY_RECEIVER_NOT_IN_SPECIFIED_ACCOUNTS': '抱歉，分润账号不是指定的分润账户，请确保该分润账户已签署分润协议。',
        'ROYALTY_LENGTH_ERROR': '抱歉，分润信息过长，不能超过1000个字符，请检查后重新集成。',
        'DEFAULT_BANK_INVALID': '您传递的默认网银参数不在规定的范围内。',
        'DIS_NOT_SIGN_PROTOCOL': '抱歉，您的分销商没有与支付宝签约，请联系您的商户。',
        'SELF_TIMEOUT_NOT_SUPPORT': '抱歉，商户没有开通自定义超时权限，请联系您的商户。',
        'ILLEGAL_OUTTIME_ARGUMENT': '抱歉，自定义超时时间设置错误，请联系您的商户。',
        'EBANK_CERDIT_GW_RULE_NOT_OPEN': '信用卡未签约（签约到期）或者接口参数未指定开通信用卡支付。',
        'DIRECTIONAL_PAY_FORBIDDEN': '付款受限，请确保收款方有权进行收款。',
        'SELLER_ENABLE_STATUS_FORBID': '卖家状态不正常。',
        'ROYALTY_SELLER_ENABLE_STATUS_FORBID': '抱歉，卖家暂时无法进行收款操作，请联系您的商户。',
        'ROYALTY_SELLER_NOT_CERTIFY': '抱歉，卖家尚未通过认证，不能进行收款，请联系您的商户。',
        'ROYALTY_FORAMT_ERROR': '抱歉，接口传递的分润参数格式错误，请检查后重新集成。',
        'ROYALTY_TYPE_ERROR': '抱歉，接口传递的分润类型错误，请检查后重新集成。',
        'ROYALTY_RECEIVE_EMAIL_NOT_EXIST': '抱歉，分润账户经验证不存在，请联系您的商户。',
        'ROYALTY_RECEIVE_EMAIL_NOT_CERTIFY': '抱歉，分润账户经验证未通过人行验证，请联系您的商户。',
        'ROYALTY_PAY_EMAIL_NOT_EXIST': '抱歉，分润付款账户经验证不存在，请联系您的商户。',
        'TAOBAO_ANTI_PHISHING_CHECK_FAIL': '抱歉，无法付款! 该笔交易可能存在风险，如果您确定本次交易没有问题，请1个小时后再付款。',
        'SUBJECT_HAS_FORBIDDENWORD': '抱歉，无法付款! 请联系商户修改商品名称，再重新购买。',
        'PAY_CHECK_FAIL': '抱歉，付款失败! 该笔交易可能存在风险。',
        'BODY_HAS_FORBIDDENWORD': '抱歉，无法付款! 请联系商户修改商品描述，再重新购买。',
        'NEED_CTU_CHECK_PARAMETER_ERROR': '抱歉，您传递的商户可信任参数权限参数错误。',
        'NEED_CTU_CHECK_NOT_ALLOWED': '抱歉，商户没有可信任参数校验的权限。',
        'BUYER_NOT_EXIST': '抱歉，买家账户经验证不存在。',
        'HAS_NO_PRIVILEGE': '你的当前访问记录丢失，请返回商户网站重新发起付款。',
        'EVOUCHER_ID_NOT_EXIST': '抱歉，商户传递的消费券交易公共业务扩展参数中凭证号不存在，请联系您的商家。',
        'NAVIGATION_INCOME_OF_ROYALTY_ACCOUNT': '分润账户入不敷出',
    }

    # 交易状态
    TradeState = {
             'WAIT_BUYER_PAY': '交易创建，等待买家付款。',
            'TRADE_CLOSED': '在指定时间段内未支付时关闭的交易；',
            '': '在交易完成全额退款成功时关闭的交易。',
            'TRADE_SUCCESS': '交易成功，且可对该交易做操作，如：多级分润、退款等。',
            'TRADE_PENDING': '等待卖家收款（买家付款后，如果卖家账号被冻结）。',
            'TRADE_FINISHED': '交易成功且结束，即不可再做任何操作。',
    }
    RequestErrorCodeMsg = {
        'SELLER_NOT_IN_SPECIFIED_SELLERS': '传入的收款账户不是指定的收款账户',
        'TRADE_SELLER_NOT_MATCH': '卖家账户与交易中不一致',
        'ILLEGAL_FEE_PARAM': '金额传递混乱',
        'SUBJECT_MUST_NOT_BE_NULL': '商品名不能为空',
        'TRADE_PRICE_NOT_MATCH': '单价与交易中不一致',
        'TRADE_QUANTITY_NOT_MATCH': '购买数量与交易中不一致',
        'TRADE_TOTALFEE_NOT_MATCH': '交易金额与交易中不一致',
        'ILLEGAL_EXTRA_COMMON_PARAM': '非法的接口通用回传参数',
        'ILLEGAL_PAYMENT_TYPE': '错误的Payment_type参数',
        'NOT_SUPPORT_GATEWAY': '错误的supportGateway参数',
        'SELLER_NOT_EXIST': '卖家不存在',
        'ILLEGAL_ARGUMENT': '参数不正确',
        'BUYER_EMAIL_ID_MUST_NULL': '买家email必须为空',
        'PRODUCT_NOT_ALLOWED': '产品不允许访问',
        'ROYALTY_RECEIVER_NOT_IN_SPECIFIED_ACCOUNTS': '提成账号不在预先设置的账号中',
        'ROYALTY_LENGTH_ERROR': '提成信息说明长度不能超过1000个字符，请检查后重新集成',
        'ILLEGAL_EXTER_INVOKE_IP': '防钓鱼检查非法调用IP',
        'DEFAULT_BANK_INVALID': '网银参数不合法',
        'DIS_NOT_SIGN_PROTOCOL': '分销商没有签约',
        'SELF_TIMEOUT_NOT_SUPPORT': '不支持超时',
        'ILLEGAL_OUTTIME_ARGUMENT': '超时时间设置错误',
        'EBANK_CERDIT_GW_RULE_NOT_OPEN': '信用卡未签约（签约到期）或者接口参数未指定开通信用卡支付',
        'DIRECTIONAL_PAY_FORBIDDEN': '付款受限，请确保收款方有权进行收款',
        'SELLER_ENABLE_STATUS_FORBID': '卖家状态不正常',
        'ROYALTY_SELLER_ENABLE_STATUS_FORBID': '分润方状态不正常',
        'ROYALTY_SELLER_NOT_CERTIFY': '有提成情况下，卖家未通过认证',
        'ROYALTY_FORAMT_ERROR': '提成信息错误，请检查后重新集成',
        'ROYALTY_TYPE_ERROR': '提成类型不支持，请检查后重新集成',
        'ROYALTY_RECEIVE_EMAIL_NOT_EXIST': '提成收款帐户不存在',
        'ROYALTY_PAY_EMAIL_NOT_EXIST': '提成付款帐户不存在',
        'SUBJECT_HAS_FORBIDDENWORD': '商品名称包含违禁词',
        'BODY_HAS_FORBIDDENWORD': '商品描述包含违禁词',
        'MOTO_EXPRESS_TOTAL_AMOUNT_EXCEED': '交易金额超过快捷支付前置限额',
        'MOTO_EXPRESS_PARTNER_NOT_SIGN_PROTOCOL': '商户未开通快捷支付',
        'EBANK_VISA_GW_RULE_NOT_OPEN': '商户未签约外卡收单产品（或者签约到期）或者本次交易金额小于1元',
        'ROYALTY_RECEIVE_EMAIL_NOT_CERTIFY': '提成收款帐户不存在',
        'NEED_CTU_CHECK_PARAMETER_ERROR': '商户可信任参数权限参数校验失败',
        'NEED_CTU_CHECK_NOT_ALLOWED': '商户没有可信任参数校验的权限',
        'UNKNOWN_PRODUCT_NAME': '系统异常，无法获取产品线信息，请稍后再试',
        'TOKEN_LEN_TOO_LONG TOKEN': '长度超过限制，最多40位',
    }

AliPayConfig = _AliPayConfig()
AliPayConstData = _AliPayConstData()