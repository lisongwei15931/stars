# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('commission', '0076_usermoneychange_market_trade_serial_no'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_no', models.CharField(unique=True, max_length=32)),
                ('amount', models.DecimalField(verbose_name='\u603b\u4ef7', max_digits=15, decimal_places=2)),
                ('description', models.CharField(max_length=200, verbose_name='\u5546\u54c1\u63cf\u8ff0')),
                ('detail', models.CharField(default=b'', max_length=500, verbose_name='\u5546\u54c1\u8be6\u60c5', blank=True)),
                ('trade_type', models.SmallIntegerField(default=1, choices=[(1, '\u8d2d\u4e70'), (2, '\u8fdb\u8d27'), (3, '\u51fa\u552e')])),
                ('status', models.SmallIntegerField(choices=[(0, '\u672a\u652f\u4ed8'), (1, '\u652f\u4ed8\u4e2d'), (2, '\u652f\u4ed8\u6210\u529f'), (3, '\u652f\u4ed8\u5931\u8d25'), (4, '\u5df2\u5173\u95ed'), (5, '\u5df2\u64a4\u9500')])),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_datetime', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
