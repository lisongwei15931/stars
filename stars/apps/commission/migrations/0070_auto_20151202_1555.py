# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0069_auto_20151202_1528'),
    ]

    operations = [
        migrations.AddField(
            model_name='commissionbuy',
            name='flag',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u88ab\u5904\u7406'),
        ),
        migrations.AddField(
            model_name='commissionsale',
            name='flag',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u88ab\u5904\u7406'),
        ),
    ]
