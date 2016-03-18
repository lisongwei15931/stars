# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('address', '0002_auto_20151015_2042'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReceivingAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('consignee', models.CharField(max_length=64, verbose_name='\u6536\u8d27\u4eba')),
                ('address', models.CharField(max_length=255, verbose_name='\u8be6\u7ec6\u5730\u5740')),
                ('mobile_phone', models.CharField(max_length=15, verbose_name='\u624b\u673a\u53f7\u7801')),
                ('telephone', models.CharField(max_length=15, null=True, verbose_name='\u56fa\u5b9a\u7535\u8bdd', blank=True)),
                ('email', models.EmailField(max_length=254, null=True, verbose_name='\u90ae\u7bb1', blank=True)),
                ('is_default', models.BooleanField(default=False, verbose_name='\u662f\u5426\u4e3a\u9ed8\u8ba4\u5730\u5740')),
                ('city', models.ForeignKey(verbose_name='\u6240\u5c5e\u57ce\u5e02', to='address.City')),
                ('district', models.ForeignKey(verbose_name='\u6240\u5c5e\u533a', to='address.District')),
                ('province', models.ForeignKey(verbose_name='\u6240\u5c5e\u7701', to='address.Province')),
                ('user', models.ForeignKey(verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u6536\u8d27\u5730\u5740',
                'verbose_name_plural': '\u6536\u8d27\u5730\u5740',
            },
        ),
    ]
