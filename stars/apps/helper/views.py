# -*- coding: utf-8 -*-s

import datetime
import json

from django.http.response import HttpResponse
from django.shortcuts import render

def helper_index(request):
    help = request.GET.get('help','zc')
    return render(request, 'helper/helper.html', locals())

