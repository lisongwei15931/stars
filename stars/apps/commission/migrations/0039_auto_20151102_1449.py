# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0038_auto_20151031_1436'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockproductconfig',
            name='max_num',
            field=models.IntegerField(default=0, null=True, verbose_name='\u7528\u6237\u6301\u6709\u603b\u91cf', blank=True),
        ),
        migrations.AddField(
            model_name='stockproductconfig',
            name='pickup_addr',
            field=models.ManyToManyField(to='commission.PickupAddr'),
        ),
        migrations.AddField(
            model_name='stockproductconfig',
            name='sale_num',
            field=models.IntegerField(default=0, null=True, verbose_name='\u53d1\u552e\u91cf', blank=True),
        ),
    ]
