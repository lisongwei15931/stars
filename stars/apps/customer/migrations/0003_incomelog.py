# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customer', '0002_auto_20150924_1441'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncomeLog',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('amount', models.IntegerField(verbose_name='\u91d1\u989d')),
                ('event', models.IntegerField(verbose_name='\u7c7b\u578b', choices=[(1, '\u5145\u503c'), (2, '\u63d0\u73b0')])),
                ('status', models.IntegerField(default=0, verbose_name='\u72b6\u6001', choices=[(0, '\u4ea4\u6613\u4e2d'), (1, '\u4ea4\u6613\u6210\u529f'), (2, '\u4ea4\u6613\u5931\u8d25')])),
                ('to', models.IntegerField(default=-1, verbose_name='\u5bf9\u65b9')),
                ('to_desc', models.CharField(default=b'', max_length=100)),
                ('comment', models.CharField(default=b'', max_length=200)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='\u751f\u6210\u65f6\u95f4')),
                ('modified_time', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('user', models.ForeignKey(verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
