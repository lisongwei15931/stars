#coding=utf-8
import os
import sys
path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path[0:path.rfind('stars')])
os.environ['DJANGO_SETTINGS_MODULE'] = 'stars.settings'

import django
django.setup()

from stars.apps.commission.market_config import before_market_open_redis





before_market_open_redis()
