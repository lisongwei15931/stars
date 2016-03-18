# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalogue', '0008_auto_20150924_1125'),
        ('commission', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommissionBuyBackup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('commission_no', models.CharField(unique=True, max_length=15, verbose_name='\u59d4\u6258\u7f16\u53f7')),
                ('c_type', models.IntegerField(verbose_name='\u7c7b\u578b', choices=[(1, b'\xe6\xb6\x88\xe8\xb4\xb9'), (2, b'\xe8\xbf\x9b\xe8\xb4\xa7')])),
                ('unit_price', models.FloatField(null=True, verbose_name='\u5355\u4ef7', blank=True)),
                ('quantity', models.IntegerField(null=True, verbose_name='\u6570\u91cf', blank=True)),
                ('uncomplete_quantity', models.IntegerField(null=True, verbose_name='\u672a\u5b8c\u6210\u6570\u91cf', blank=True)),
                ('status', models.IntegerField(verbose_name='\u72b6\u6001', choices=[(1, b'\xe5\xbe\x85\xe6\x88\x90\xe4\xba\xa4'), (2, b'\xe9\x83\xa8\xe5\x88\x86\xe6\x88\x90\xe4\xba\xa4'), (3, b'\xe6\x88\x90\xe4\xba\xa4')])),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_datetime', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4', db_index=True)),
                ('product', models.ForeignKey(related_name='commission_buy_buckup_product', verbose_name='\u5546\u54c1', to='catalogue.Product')),
                ('user', models.ForeignKey(related_name='commission_buy_buckup_user', verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u59d4\u6258\u4e70\u5907\u4efd\u8868',
                'verbose_name_plural': '\u59d4\u6258\u4e70\u5907\u4efd\u8868',
            },
        ),
        migrations.RemoveField(
            model_name='commissionbuybuckup',
            name='product',
        ),
        migrations.RemoveField(
            model_name='commissionbuybuckup',
            name='user',
        ),
        migrations.DeleteModel(
            name='CommissionBuyBuckup',
        ),
    ]
