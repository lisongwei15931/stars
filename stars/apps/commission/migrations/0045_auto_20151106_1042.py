# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('commission', '0044_auto_20151103_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickupaddr',
            name='staff',
            field=models.ManyToManyField(related_name='pickup_addr_staff', verbose_name='\u5de5\u4f5c\u4eba\u5458', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='pickuplist',
            name='deal_user',
            field=models.ForeignKey(related_name='deal_user', verbose_name='\u529e\u7406\u4eba', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='pickuplist',
            name='logistics_company',
            field=models.CharField(max_length=128, null=True, verbose_name='\u7269\u6d41\u516c\u53f8', blank=True),
        ),
        migrations.AddField(
            model_name='pickuplist',
            name='logistics_date',
            field=models.DateTimeField(null=True, verbose_name='\u53d1\u8d27\u65e5\u671f', blank=True),
        ),
        migrations.AlterField(
            model_name='pickuplist',
            name='status',
            field=models.IntegerField(verbose_name='\u72b6\u6001', choices=[(1, b'\xe6\x9c\xaa\xe6\x8f\x90\xe8\xb4\xa7'), (2, b'\xe5\xb7\xb2\xe6\x8f\x90\xe8\xb4\xa7'), (3, b'\xe5\xb7\xb2\xe9\xa9\xb3\xe5\x9b\x9e'), (4, b'\xe6\x9c\xaa\xe5\x8f\x91\xe8\xb4\xa7'), (5, b'\xe5\xb7\xb2\xe5\x8f\x91\xe8\xb4\xa7')]),
        ),
    ]
