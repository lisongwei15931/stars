# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0031_auto_20151027_1551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userproduct',
            name='overage_unit_price',
            field=models.FloatField(default=0, null=True, verbose_name='\u5747\u4ef7', blank=True),
        ),
    ]
