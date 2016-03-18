#coding=utf-8
import os
import sys
path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path[0:path.rfind('stars')])
os.environ['DJANGO_SETTINGS_MODULE'] = 'stars.settings'

import django
django.setup()

from stars.apps.commission.market_config import do_truncate_database, \
    before_market_open





        
do_truncate_database()
before_market_open()
