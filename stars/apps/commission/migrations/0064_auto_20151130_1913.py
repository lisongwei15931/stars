# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0063_remove_stockproductconfig_opening_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userproduct',
            name='can_sale_quantity',
        ),
        migrations.AddField(
            model_name='userproduct',
            name='total_buy_quantity',
            field=models.FloatField(default=0, null=True, verbose_name='\u603b\u8fdb\u8d27\u91cf', blank=True),
        ),
        migrations.AddField(
            model_name='userproduct',
            name='total_pickup_quantity',
            field=models.FloatField(default=0, null=True, verbose_name='\u603b\u63d0\u8d27\u91cf', blank=True),
        ),
        migrations.AddField(
            model_name='userproduct',
            name='total_sale_quantity',
            field=models.FloatField(default=0, null=True, verbose_name='\u603b\u5356\u91cf', blank=True),
        ),
        migrations.AlterField(
            model_name='tradecomplete',
            name='c_type',
            field=models.IntegerField(db_index=True, verbose_name='\u7c7b\u578b', choices=[(1, b'\xe8\xb4\xad\xe4\xb9\xb0'), (2, b'\xe8\xbf\x9b\xe8\xb4\xa7')]),
        ),
    ]
