#coding=utf-8
import datetime
import os
import sys

path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path[0:path.rfind('stars')])
os.environ['DJANGO_SETTINGS_MODULE'] = 'stars.settings'

import django
django.setup()

from stars.apps.commission.market_config import after_market_off
from stars.apps.customer.finance.ab.work import ab_end_trade




        
after_market_off()
ab_end_trade()