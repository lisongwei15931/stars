# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0037_stockticker_market_capitalization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pickuplist',
            name='pickup_no',
            field=models.CharField(max_length=15, null=True, verbose_name='\u63d0\u8d27\u5355\u53f7', blank=True),
        ),
    ]
