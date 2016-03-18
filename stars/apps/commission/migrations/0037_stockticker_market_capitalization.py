# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0036_auto_20151028_2035'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockticker',
            name='market_capitalization',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u5e02\u503c', blank=True),
        ),
    ]
