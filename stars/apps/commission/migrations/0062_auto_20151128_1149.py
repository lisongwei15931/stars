# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0061_auto_20151127_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockproductconfig',
            name='t_n',
            field=models.IntegerField(default=0, null=True, verbose_name='T+N\u53c2\u6570', blank=True),
        ),
        migrations.AddField(
            model_name='stockproductconfig',
            name='today_max_seal_num',
            field=models.IntegerField(default=0, null=True, verbose_name='\u5f53\u65e5\u6700\u5927\u5356\u91cf', blank=True),
        ),
    ]
