# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0011_product_product_long_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StockEnter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(null=True, verbose_name='\u6570\u91cf', blank=True)),
                ('number', models.IntegerField(null=True, verbose_name='\u4ef6\u91cf', blank=True)),
                ('desc', models.CharField(default=b'', max_length=1000, null=True, verbose_name='\u5907\u6ce8', blank=True)),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_datetime', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4', db_index=True)),
                ('product', models.ForeignKey(related_name='stock_enter_product', verbose_name='\u5546\u54c1', to='catalogue.Product')),
                ('user', models.ForeignKey(related_name='stock_enter_user', verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u5e93\u8f6c\u4ea4\u6613\u8868',
                'verbose_name_plural': '\u5e93\u8f6c\u4ea4\u6613\u8868',
            },
        ),
    ]
