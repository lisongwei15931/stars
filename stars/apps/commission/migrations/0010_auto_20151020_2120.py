# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0009_auto_20151019_1818'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commissionbuy',
            name='uncomplete_quantity',
            field=models.IntegerField(default=0, null=True, verbose_name='\u672a\u5b8c\u6210\u6570\u91cf', blank=True),
        ),
    ]
