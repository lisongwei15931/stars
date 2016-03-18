# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0052_stockproductconfig_self_pick_or_express'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickupdetail',
            name='consignee',
            field=models.CharField(max_length=64, null=True, verbose_name='\u6536\u8d27\u4eba', blank=True),
        ),
        migrations.AddField(
            model_name='pickupdetail',
            name='mobile_phone',
            field=models.CharField(max_length=15, null=True, verbose_name='\u624b\u673a\u53f7\u7801', blank=True),
        ),
    ]
