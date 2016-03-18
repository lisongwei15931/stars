# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalogue', '0015_auto_20151130_1715'),
        ('commission', '0065_auto_20151130_1919'),
    ]

    operations = [
        migrations.CreateModel(
            name='DealFeeCollect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('buy_deal_fee', models.FloatField(default=0, null=True, verbose_name='\u4e70\u624b\u7eed\u8d39', blank=True)),
                ('sale_deal_fee', models.FloatField(default=0, null=True, verbose_name='\u5356\u624b\u7eed\u8d39', blank=True)),
                ('created_date', models.DateField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_datetime', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4', db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='DealFeeDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deal_fee_type', models.IntegerField(verbose_name='\u624b\u7eed\u8d39\u7c7b\u578b', choices=[(1, b'\xe8\xb4\xad\xe4\xb9\xb0'), (2, b'\xe5\x87\xba\xe5\x94\xae')])),
                ('deal_fee', models.FloatField(default=0, null=True, verbose_name='\u624b\u7eed\u8d39', blank=True)),
                ('created_date', models.DateField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_datetime', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4', db_index=True)),
                ('buy_user', models.ForeignKey(related_name='deal_fee_buy_user', verbose_name='\u4e70\u5bb6', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(related_name='deal_fee_product', verbose_name='\u5546\u54c1', blank=True, to='catalogue.Product', null=True)),
                ('sale_user', models.ForeignKey(related_name='deal_fee_sale_user', verbose_name='\u5356\u5bb6', to=settings.AUTH_USER_MODEL)),
                ('trade_complete', models.ForeignKey(related_name='deal_fee_trade_complete', verbose_name='\u6210\u4ea4\u5355', blank=True, to='commission.TradeComplete', null=True)),
            ],
        ),
    ]
