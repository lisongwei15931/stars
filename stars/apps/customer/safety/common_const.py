# -*- coding: utf-8 -*-
from datetime import timedelta


class ConstError(Exception):
    pass


class Const(object):
    __dict__ = ()

    def __setattr__(self, k, v):
        raise ConstError


class _CommonEmailData(Const):
    UPDATE_MAIL_VERIFICATION_CODE_EXPIRED_TIME = timedelta(hours=24)
    SMS_VERIFICATION_CODE_EXPIRED_TIME = timedelta(minutes=3)

CommonEmailData = _CommonEmailData()