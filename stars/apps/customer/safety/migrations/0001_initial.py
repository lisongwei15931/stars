# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MailVerificationCode',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('code', models.CharField(max_length=40)),
                ('type', models.IntegerField(verbose_name='\u7c7b\u578b', choices=[(1, '\u7ed1\u5b9a\u90ae\u7bb1\u9a8c\u8bc1'), (2, '\u4fee\u6539\u90ae\u7bb1\u9a8c\u8bc1'), (3, '\u89e3\u7ed1\u90ae\u7bb1\u9a8c\u8bc1')])),
                ('status', models.IntegerField(default=0, verbose_name='\u72b6\u6001', choices=[(0, '\u6709\u6548'), (1, '\u4f7f\u7528'), (2, '\u5931\u6548')])),
                ('data', models.CharField(default=b'', max_length=100)),
                ('comment', models.CharField(default=b'', max_length=200)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='\u751f\u6210\u65f6\u95f4')),
                ('expired_time', models.DateTimeField(verbose_name='\u8fc7\u671f\u65f6\u95f4', editable=False)),
                ('modified_time', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('user', models.ForeignKey(verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SmsVerificationCode',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('code', models.CharField(max_length=10)),
                ('type', models.IntegerField(verbose_name='\u7c7b\u578b', choices=[(1, '\u4fee\u6539\u624b\u673a\u53f7\u7801'), (2, '\u4fee\u6539\u767b\u5f55\u5bc6\u7801'), (3, '\u4fee\u6539\u652f\u4ed8\u5bc6\u7801'), (4, '\u4fee\u6539\u90ae\u7bb1')])),
                ('status', models.IntegerField(default=0, verbose_name='\u72b6\u6001', choices=[(0, '\u6709\u6548'), (1, '\u4f7f\u7528'), (2, '\u5931\u6548')])),
                ('data', models.CharField(default=b'', max_length=100)),
                ('comment', models.CharField(default=b'', max_length=200)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='\u751f\u6210\u65f6\u95f4')),
                ('expired_time', models.DateTimeField(verbose_name='\u8fc7\u671f\u65f6\u95f4', editable=False)),
                ('modified_time', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('user', models.ForeignKey(verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
