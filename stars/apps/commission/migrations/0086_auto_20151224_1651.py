# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0085_auto_20151223_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commissionbuy',
            name='time_value',
            field=models.BigIntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='commissionsale',
            name='time_value',
            field=models.BigIntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='stockticker',
            name='time_value',
            field=models.BigIntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='userassetdailyreport',
            name='time_value',
            field=models.BigIntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='userbalance',
            name='time_value',
            field=models.BigIntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='userproduct',
            name='time_value',
            field=models.BigIntegerField(default=0, null=True, blank=True),
        ),
    ]
