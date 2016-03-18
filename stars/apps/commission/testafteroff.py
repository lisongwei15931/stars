# -*- coding: utf-8 -*-s
import datetime
import md5
import random
import string
import traceback

import django
from django.contrib.auth.models import User
from django.db.models import F
from django.db.models import Max
from django.db.models import Min, Sum, Max
from django.db.models.lookups import IsNull
from django.db.models.query_utils import Q
from oscar.apps.dashboard.menu import create_menu
from oscar.core.loading import get_model
from django.conf import settings

django.setup()
 
all_nodes = create_menu(settings.OSCAR_DASHBOARD_NAVIGATION)
visible_nodes = []
for node in all_nodes:
    user = User.objects.get(id=1)
    filtered_node = node.filter(user)
    print node.label,filtered_node