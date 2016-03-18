# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0084_tradecomplete_trade_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='commissionbuy',
            name='time_value',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='commissionsale',
            name='time_value',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='stockticker',
            name='time_value',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userassetdailyreport',
            name='time_value',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userbalance',
            name='time_value',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userproduct',
            name='time_value',
            field=models.BigIntegerField(null=True, blank=True),
        ),
    ]
