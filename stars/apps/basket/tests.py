# -*- coding: utf-8 -*-s
import datetime
import md5
import random
import string
import os,sys
import django

from django.template.defaultfilters import pprint
path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path[0:path.rfind('stars')])
os.environ['DJANGO_SETTINGS_MODULE'] = 'stars.settings'
from django.contrib.auth.models import User
from django.db.models import Max
from oscar.core.loading import get_model
from django.db.models.lookups import IsNull
from django.db.models import Min, Sum, Max
from django.db.models.query_utils import Q
from django.db.models import F
from django.conf import settings
import hashlib
django.setup()
 
device_id = "C2685765-6BE5-4CE2-9F02-5D325044C7C8"
app_secret_key = getattr(settings, 'APP_SECRET_KEY', 'aeb11af7b1750854cb6217cf33e1a5e48826369c1e255c33ff655ff3fc938e')
correct_sign = hashlib.md5(''.join([device_id, app_secret_key, 'lantubaihuo'])).hexdigest()
print correct_sign
