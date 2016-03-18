# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0006_auto_20151019_1352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pickupaddr',
            name='contact',
            field=models.CharField(default=b'', max_length=200, null=True, verbose_name='\u8054\u7cfb\u4eba', blank=True),
        ),
        migrations.AlterField(
            model_name='pickupaddr',
            name='name',
            field=models.CharField(max_length=200, verbose_name='\u540d\u5b57'),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='ower',
            field=models.CharField(default=b'', max_length=30, null=True, verbose_name='\u53d1\u884c\u4ea4\u6613\u5546', blank=True),
        ),
        migrations.AlterField(
            model_name='userpickupaddr',
            name='name',
            field=models.CharField(default=b'', max_length=200, null=True, verbose_name='\u540d\u5b57', blank=True),
        ),
    ]
