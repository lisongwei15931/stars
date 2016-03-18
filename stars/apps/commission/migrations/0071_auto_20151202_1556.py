# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0070_auto_20151202_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commissionbuy',
            name='flag',
            field=models.BooleanField(default=False, db_index=True, verbose_name='\u662f\u5426\u88ab\u5904\u7406'),
        ),
        migrations.AlterField(
            model_name='commissionsale',
            name='flag',
            field=models.BooleanField(default=False, db_index=True, verbose_name='\u662f\u5426\u88ab\u5904\u7406'),
        ),
    ]
