# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0075_pickupdetail_logistics_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermoneychange',
            name='market_trade_serial_no',
            field=models.CharField(max_length=100, null=True, verbose_name='\u5145\u503c\u63d0\u73b0\u5e02\u573a\u6d41\u6c34\u53f7', blank=True),
        ),
    ]
