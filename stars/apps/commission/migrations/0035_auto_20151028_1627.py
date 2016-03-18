# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0034_auto_20151028_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commissionbuy',
            name='c_type',
            field=models.IntegerField(verbose_name='\u7c7b\u578b', choices=[(1, b'\xe8\xb4\xad\xe4\xb9\xb0'), (2, b'\xe8\xbf\x9b\xe8\xb4\xa7')]),
        ),
        migrations.AlterField(
            model_name='commissionbuybackup',
            name='c_type',
            field=models.IntegerField(verbose_name='\u7c7b\u578b', choices=[(1, b'\xe8\xb4\xad\xe4\xb9\xb0'), (2, b'\xe8\xbf\x9b\xe8\xb4\xa7')]),
        ),
        migrations.AlterField(
            model_name='tradecomplete',
            name='c_type',
            field=models.IntegerField(verbose_name='\u7c7b\u578b', choices=[(1, b'\xe8\xb4\xad\xe4\xb9\xb0'), (2, b'\xe8\xbf\x9b\xe8\xb4\xa7')]),
        ),
        migrations.AlterField(
            model_name='userproduct',
            name='trade_type',
            field=models.IntegerField(verbose_name='\u7c7b\u578b', choices=[(1, b'\xe8\xb4\xad\xe4\xb9\xb0'), (2, b'\xe8\xbf\x9b\xe8\xb4\xa7')]),
        ),
    ]
