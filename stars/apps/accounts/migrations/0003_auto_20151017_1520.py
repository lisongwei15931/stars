# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile_audit_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='created_date',
            field=models.DateField(default=datetime.datetime(2015, 10, 17, 7, 20, 29, 137000, tzinfo=utc), auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f', db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='created_time',
            field=models.TimeField(default=datetime.datetime(2015, 10, 17, 7, 20, 46, 379000, tzinfo=utc), verbose_name='\u521b\u5efa\u65f6\u95f4', auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='desc',
            field=models.CharField(max_length=1000, null=True, verbose_name='\u5907\u6ce8', blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='modified_date',
            field=models.DateField(default=datetime.datetime(2015, 10, 17, 7, 20, 48, 546000, tzinfo=utc), verbose_name='\u4fee\u6539\u65e5\u671f', auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='modified_time',
            field=models.TimeField(default=datetime.datetime(2015, 10, 17, 7, 20, 50, 137000, tzinfo=utc), verbose_name='\u4fee\u6539\u65f6\u95f4', auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='pay_pwd',
            field=models.CharField(max_length=128, null=True, verbose_name='\u652f\u4ed8\u5bc6\u7801', blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='pickup_pwd',
            field=models.CharField(max_length=128, null=True, verbose_name='\u63d0\u8d27\u5bc6\u7801', blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='audit_status',
            field=models.BooleanField(default=False, verbose_name='\u5ba1\u6838\u901a\u8fc7\u72b6\u6001'),
        ),
    ]
