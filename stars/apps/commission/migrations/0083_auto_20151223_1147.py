# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0082_orderinfo_order_pickup_detail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockticker',
            name='total',
            field=models.FloatField(default=0, null=True, verbose_name='\u6210\u4ea4\u91d1\u989d', blank=True),
        ),
    ]
