# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0030_auto_20151027_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commissionbuybackup',
            name='created_datetime',
            field=models.DateTimeField(verbose_name='\u521b\u5efa\u65f6\u95f4'),
        ),
        migrations.AlterField(
            model_name='commissionbuybackup',
            name='modified_datetime',
            field=models.DateTimeField(verbose_name='\u4fee\u6539\u65f6\u95f4', db_index=True),
        ),
        migrations.AlterField(
            model_name='commissionsale',
            name='c_type',
            field=models.IntegerField(default=1, verbose_name='\u7c7b\u578b', choices=[(1, b'\xe5\x87\xba\xe5\x94\xae')]),
        ),
        migrations.AlterField(
            model_name='commissionsalebackup',
            name='c_type',
            field=models.IntegerField(default=1, verbose_name='\u7c7b\u578b', choices=[(1, b'\xe5\x87\xba\xe5\x94\xae')]),
        ),
        migrations.AlterField(
            model_name='commissionsalebackup',
            name='created_datetime',
            field=models.DateTimeField(verbose_name='\u521b\u5efa\u65f6\u95f4'),
        ),
        migrations.AlterField(
            model_name='commissionsalebackup',
            name='modified_datetime',
            field=models.DateTimeField(verbose_name='\u4fee\u6539\u65f6\u95f4', db_index=True),
        ),
    ]
