# -*- coding: utf-8 -*-s
import datetime
import md5
import random
import string
from django.conf import settings
import os,sys
import django
path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path[0:path.rfind('stars')])
os.environ['DJANGO_SETTINGS_MODULE'] = 'stars.settings'
import hashlib
django.setup()
device_id = "text1"
app_secret_key = getattr(settings, 'APP_SECRET_KEY', 'aeb11af7b1750854cb6217cf33e1a5e48826369c1e255c33ff655ff3fc938e')
sign = hashlib.md5(''.join([device_id, app_secret_key, 'lantubaihuo'])).hexdigest()
print sign






