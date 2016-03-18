# -*- coding: utf-8 -*-s
import os

import cStringIO

from datetime import *
from dateutil import parser
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.utils._os import abspathu

from stars import settings
from stars.apps.tradingcenter.views import is_market_opening
from stars.apps.basket.views import order_success


def notify_order_pay_success(order):
    order.status = 2
    order.pay_type = 2
    order.effective = True
    order.save()
    order_success(order)


def need_market_opening(func):
    def wrapper(*args, **kwargs):
        if not is_market_opening():
            tpl = 'tradingcenter/market_closed_error.html'
            return render(args[1], tpl, {"msg": u"已闭市,请在开市时操作"})
        else:
            return func(*args, **kwargs)

    return wrapper


class FinanceFileSystemStorage(FileSystemStorage):
    def __init__(self, the_day, location=None, inst='ab', file_permissions_mode=None,
            directory_permissions_mode=None):
        if location is None:
            location = settings.FINANCE_ROOT
        if inst is not None:
            location =  os.path.join(location, inst)

        if isinstance(the_day, str):
            the_day = parser.parse(the_day)
        elif not isinstance(the_day, (datetime, date)):
            raise ValueError

        location = os.path.join(location, the_day.strftime('%Y%m%d'))

        self.base_location = location
        self.location = abspathu(self.base_location)
        self.file_permissions_mode = (None
        )
        self.directory_permissions_mode = (None
        )

        self.name = ''

    def save(self, name, content, max_length=None):
        if isinstance(content, (str, unicode)):
            s = cStringIO.StringIO()
            s.write(content)
            return super(self.__class__, self).save(name, s, max_length)
        self.name =  super(self.__class__, self).save(name, content, max_length)
        return self.name

    def url(self, name):
        return None

    def get_path(self):
        return super(self.__class__, self).path(self.name)