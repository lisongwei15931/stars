#coding=utf-8
import os
import sys


path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path[0:path.rfind('stars')])
os.environ['DJANGO_SETTINGS_MODULE'] = 'stars.settings'

import django
django.setup()

from stars.apps.commission.market_config import before_market_open
from stars.apps.customer.finance.ab.work import ab_start_trade
        
before_market_open()
ab_start_trade()