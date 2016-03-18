# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('commission', '0047_auto_20151106_1916'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickupdetail',
            name='deal_datetime',
            field=models.DateTimeField(null=True, verbose_name='\u529e\u7406\u65e5\u671f', blank=True),
        ),
        migrations.AddField(
            model_name='pickupdetail',
            name='deal_user',
            field=models.ForeignKey(related_name='pikcup_deal_user', verbose_name='\u529e\u7406\u4eba', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='pickupdetail',
            name='express_fee',
            field=models.FloatField(null=True, verbose_name='\u5feb\u9012\u8d39\u7528', blank=True),
        ),
        migrations.AddField(
            model_name='pickupdetail',
            name='logistics_company',
            field=models.CharField(max_length=128, null=True, verbose_name='\u7269\u6d41\u516c\u53f8', blank=True),
        ),
        migrations.AddField(
            model_name='pickupdetail',
            name='logistics_date',
            field=models.DateTimeField(null=True, verbose_name='\u53d1\u8d27\u65e5\u671f', blank=True),
        ),
        migrations.AddField(
            model_name='pickupdetail',
            name='pickup_addr',
            field=models.ForeignKey(verbose_name='\u81ea\u63d0\u70b9', blank=True, to='commission.PickupAddr', null=True),
        ),
        migrations.AddField(
            model_name='pickupdetail',
            name='pickup_captcha',
            field=models.CharField(max_length=16, null=True, verbose_name='\u63d0\u8d27\u9a8c\u8bc1\u7801', blank=True),
        ),
        migrations.AddField(
            model_name='pickupdetail',
            name='pickup_type',
            field=models.IntegerField(default=1, verbose_name='\u63d0\u8d27\u7c7b\u578b', choices=[(1, b'\xe8\x87\xaa\xe6\x8f\x90'), (2, b'\xe8\x87\xaa\xe6\x8f\x90\xe7\x82\xb9\xe4\xbb\xa3\xe8\xbf\x90'), (3, b'\xe5\x8e\x82\xe5\x95\x86\xe5\x8f\x91\xe8\xb4\xa7')]),
        ),
        migrations.AddField(
            model_name='pickupdetail',
            name='refuse_desc',
            field=models.CharField(default=b'', max_length=1000, null=True, verbose_name='\u9a73\u56de\u539f\u56e0', blank=True),
        ),
        migrations.AddField(
            model_name='pickupdetail',
            name='status',
            field=models.IntegerField(default=4, verbose_name='\u72b6\u6001', choices=[(1, b'\xe6\x9c\xaa\xe6\x8f\x90\xe8\xb4\xa7'), (2, b'\xe5\xb7\xb2\xe6\x8f\x90\xe8\xb4\xa7'), (3, b'\xe5\xb7\xb2\xe9\xa9\xb3\xe5\x9b\x9e'), (4, b'\xe6\x9c\xaa\xe5\x8f\x91\xe8\xb4\xa7'), (5, b'\xe5\xb7\xb2\xe5\x8f\x91\xe8\xb4\xa7'), (6, b'\xe5\xb7\xb2\xe8\xaf\x84\xe4\xbb\xb7')]),
        ),
        migrations.AddField(
            model_name='pickupdetail',
            name='user_address',
            field=models.CharField(max_length=256, null=True, verbose_name='\u7528\u6237\u6536\u4ef6\u5730\u5740', blank=True),
        ),
        migrations.AlterField(
            model_name='pickuplist',
            name='status',
            field=models.IntegerField(verbose_name='\u72b6\u6001', choices=[(1, b'\xe6\x9c\xaa\xe6\x8f\x90\xe8\xb4\xa7'), (2, b'\xe5\xb7\xb2\xe6\x8f\x90\xe8\xb4\xa7'), (3, b'\xe5\xb7\xb2\xe9\xa9\xb3\xe5\x9b\x9e'), (4, b'\xe6\x9c\xaa\xe5\x8f\x91\xe8\xb4\xa7'), (5, b'\xe5\xb7\xb2\xe5\x8f\x91\xe8\xb4\xa7'), (6, b'\xe5\xb7\xb2\xe8\xaf\x84\xe4\xbb\xb7')]),
        ),
    ]
