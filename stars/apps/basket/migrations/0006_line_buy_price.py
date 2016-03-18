# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basket', '0005_auto_20150604_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='line',
            name='buy_price',
            field=models.DecimalField(null=True, verbose_name='\u4e70\u5165\u4ef7', max_digits=12, decimal_places=2, blank=True),
        ),
    ]
