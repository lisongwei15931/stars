# -*- coding: utf-8 -*-s

class FinanceException(Exception):
    def __init__(self, flag, msgs, *args, **kwargs):
        self.flag = id
        self.msgs = msgs
        # super(self.__class__, self).__init__(flag, msgs, *args, **kwargs)


class FinanceSysException(FinanceException):
    def __init__(self, flag, msgs,*args, **kwargs):
        super(self.__class__, self).__init__(id, msgs,*args, **kwargs)


class FinanceTradeException(FinanceException):
    def __init__(self, flag, msgs, *args, **kwargs):
        super(self.__class__, self).__init__(flag, msgs, *args, **kwargs)


class WxException(FinanceException):
    ERROR_PARAM = 1
    ERROR_XML_FORMAT = 2
    ERROR_SIGN = 3
    def __init__(self, flag, msg, *args, **kwargs):
        self.flag = flag
        self.msgs = [msg]
        super(self.__class__, self).__init__(flag, [msg], *args, **kwargs)

class AliPayException(FinanceException):
    ERROR_PARAM = 1
    ERROR_XML_FORMAT = 2
    ERROR_SIGN = 3
    FAILED_NOTIFY_ID = 4
    def __init__(self, flag, msg, *args, **kwargs):
        self.flag = flag
        self.msgs = [msg]
        super(self.__class__, self).__init__(flag, [msg], *args, **kwargs)

