# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0077_productorder'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemconfig',
            name='buy_price_rate',
            field=models.FloatField(default=1, verbose_name='\u8d2d\u4e70\u8d39\u7387'),
        ),
    ]
