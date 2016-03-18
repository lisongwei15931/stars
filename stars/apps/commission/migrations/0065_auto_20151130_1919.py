# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0064_auto_20151130_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userproduct',
            name='total_buy_quantity',
            field=models.IntegerField(default=0, null=True, verbose_name='\u603b\u8fdb\u8d27\u91cf', blank=True),
        ),
        migrations.AlterField(
            model_name='userproduct',
            name='total_pickup_quantity',
            field=models.IntegerField(default=0, null=True, verbose_name='\u603b\u63d0\u8d27\u91cf', blank=True),
        ),
        migrations.AlterField(
            model_name='userproduct',
            name='total_sale_quantity',
            field=models.IntegerField(default=0, null=True, verbose_name='\u603b\u5356\u91cf', blank=True),
        ),
    ]
