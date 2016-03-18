# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pickup_admin', '0007_auto_20151120_1648'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeincomeapply',
            name='applyid',
            field=models.CharField(max_length=30, null=True, verbose_name='\u8d27\u5355\u7f16\u53f7', blank=True),
        ),
        migrations.AddField(
            model_name='storeincomeapply',
            name='in_quantity',
            field=models.IntegerField(null=True, verbose_name='\u5165\u5e93\u6570\u91cf', blank=True),
        ),
        migrations.AlterField(
            model_name='storeincomeapply',
            name='c_quantity',
            field=models.IntegerField(null=True, verbose_name='\u53d1\u8d27\u4ef6\u6570', blank=True),
        ),
        migrations.AlterField(
            model_name='storeincomeapply',
            name='quantity',
            field=models.IntegerField(null=True, verbose_name='\u53d1\u8d27\u6570\u91cf', blank=True),
        ),
    ]
