# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalogue', '0008_auto_20150924_1125'),
    ]

    operations = [
        migrations.CreateModel(
            name='PickupProvisionalRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(verbose_name='\u63d0\u8d27\u6570\u91cf')),
                ('max_quantity', models.IntegerField(verbose_name='\u8d27\u7269\u4f59\u91cf')),
                ('product', models.ForeignKey(verbose_name='\u5546\u54c1', to='catalogue.Product')),
                ('user', models.ForeignKey(verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u63d0\u8d27\u4e34\u65f6\u8bb0\u5f55',
                'verbose_name_plural': '\u63d0\u8d27\u4e34\u65f6\u8bb0\u5f55',
            },
        ),
    ]
