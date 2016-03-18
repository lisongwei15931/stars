# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0050_auto_20151112_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockproductconfig',
            name='max_buy_num',
            field=models.IntegerField(default=0, null=True, verbose_name='\u6700\u5927\u8d2d\u4e70\u91cf', blank=True),
        ),
        migrations.AddField(
            model_name='stockproductconfig',
            name='max_deal_num',
            field=models.IntegerField(default=0, null=True, verbose_name='\u6700\u5927\u8fdb\u8d27\u91cf', blank=True),
        ),
    ]
