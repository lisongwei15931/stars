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
            name='CommissionBuy',
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
                ('product', models.ForeignKey(related_name='commission_buy_product', verbose_name='\u5546\u54c1', to='catalogue.Product')),
                ('user', models.ForeignKey(related_name='commission_buy_user', verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u59d4\u6258\u4e70\u8868',
                'verbose_name_plural': '\u59d4\u6258\u4e70\u8868',
            },
        ),
        migrations.CreateModel(
            name='CommissionBuyBuckup',
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
        migrations.CreateModel(
            name='CommissionSale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('commission_no', models.CharField(unique=True, max_length=15, verbose_name='\u59d4\u6258\u7f16\u53f7')),
                ('c_type', models.IntegerField(default=3, verbose_name='\u7c7b\u578b', choices=[(1, b'\xe5\x87\xba\xe5\x94\xae')])),
                ('unit_price', models.FloatField(null=True, verbose_name='\u5355\u4ef7', blank=True)),
                ('quantity', models.IntegerField(null=True, verbose_name='\u6570\u91cf', blank=True)),
                ('uncomplete_quantity', models.IntegerField(null=True, verbose_name='\u672a\u5b8c\u6210\u6570\u91cf', blank=True)),
                ('status', models.IntegerField(verbose_name='\u72b6\u6001', choices=[(1, b'\xe5\xbe\x85\xe6\x88\x90\xe4\xba\xa4'), (2, b'\xe9\x83\xa8\xe5\x88\x86\xe6\x88\x90\xe4\xba\xa4'), (3, b'\xe6\x88\x90\xe4\xba\xa4')])),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_datetime', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4', db_index=True)),
                ('product', models.ForeignKey(related_name='commission_sale_product', verbose_name='\u5546\u54c1', to='catalogue.Product')),
                ('user', models.ForeignKey(related_name='commission_sale_user', verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u59d4\u6258\u5356\u8868',
                'verbose_name_plural': '\u59d4\u6258\u5356\u8868',
            },
        ),
        migrations.CreateModel(
            name='CommissionSaleBackup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('commission_no', models.CharField(unique=True, max_length=15, verbose_name='\u59d4\u6258\u7f16\u53f7')),
                ('c_type', models.IntegerField(default=3, verbose_name='\u7c7b\u578b', choices=[(1, b'\xe5\x87\xba\xe5\x94\xae')])),
                ('unit_price', models.FloatField(null=True, verbose_name='\u5355\u4ef7', blank=True)),
                ('quantity', models.IntegerField(null=True, verbose_name='\u6570\u91cf', blank=True)),
                ('uncomplete_quantity', models.IntegerField(null=True, verbose_name='\u672a\u5b8c\u6210\u6570\u91cf', blank=True)),
                ('status', models.IntegerField(verbose_name='\u72b6\u6001', choices=[(1, b'\xe5\xbe\x85\xe6\x88\x90\xe4\xba\xa4'), (2, b'\xe9\x83\xa8\xe5\x88\x86\xe6\x88\x90\xe4\xba\xa4'), (3, b'\xe6\x88\x90\xe4\xba\xa4')])),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_datetime', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4', db_index=True)),
                ('product', models.ForeignKey(related_name='commission_sale_buckup_product', verbose_name='\u5546\u54c1', to='catalogue.Product')),
                ('user', models.ForeignKey(related_name='commission_sale_buckup_user', verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u59d4\u6258\u5356\u5907\u4efd\u8868',
                'verbose_name_plural': '\u59d4\u6258\u5356\u5907\u4efd\u8868',
            },
        ),
        migrations.CreateModel(
            name='StockTicker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('product_symbol', models.CharField(max_length=15, verbose_name='\u5546\u54c1\u4ee3\u7801')),
                ('product_name', models.CharField(max_length=15, verbose_name='\u5546\u54c1\u540d\u79f0')),
                ('strike_price', models.FloatField(null=True, verbose_name='\u6210\u4ea4\u4ef7', blank=True)),
                ('net_change', models.FloatField(null=True, verbose_name='\u6da8\u8dcc', blank=True)),
                ('net_change_rise', models.FloatField(null=True, verbose_name='\u6da8\u8dcc\u5e45', blank=True)),
                ('bid_price', models.FloatField(null=True, verbose_name='\u4e70\u4ef7', blank=True)),
                ('ask_price', models.FloatField(null=True, verbose_name='\u5356\u4ef7', blank=True)),
                ('bid_vol', models.IntegerField(null=True, verbose_name='\u4e70\u91cf', blank=True)),
                ('ask_vol', models.IntegerField(null=True, verbose_name='\u5356\u91cf', blank=True)),
                ('opening_price', models.FloatField(null=True, verbose_name='\u5f00\u76d8', blank=True)),
                ('closing_price', models.FloatField(null=True, verbose_name='\u6628\u6536', blank=True)),
                ('high', models.FloatField(null=True, verbose_name='\u6700\u9ad8\u4ef7', blank=True)),
                ('low', models.FloatField(null=True, verbose_name='\u6700\u4f4e\u4ef7', blank=True)),
                ('volume', models.IntegerField(null=True, verbose_name='\u6210\u4ea4\u91cf', blank=True)),
                ('total', models.FloatField(null=True, verbose_name='\u6210\u4ea4\u91d1\u989d', blank=True)),
                ('market_capitalization', models.FloatField(null=True, verbose_name='\u5e02\u503c', blank=True)),
                ('created_date', models.DateField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_datetime', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4', db_index=True)),
                ('product', models.ForeignKey(related_name='stock_ticker_product', verbose_name='\u5546\u54c1', to='catalogue.Product')),
            ],
            options={
                'verbose_name': '\u884c\u60c5\u8868',
                'verbose_name_plural': '\u884c\u60c5\u8868',
            },
        ),
        migrations.CreateModel(
            name='TradeComplete',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trade_no', models.CharField(unique=True, max_length=15, verbose_name='\u6210\u4ea4\u7f16\u53f7')),
                ('commission_buy_no', models.CharField(max_length=15, verbose_name='\u59d4\u6258\u4e70\u7f16\u53f7')),
                ('commission_sale_no', models.CharField(max_length=15, verbose_name='\u59d4\u6258\u5356\u7f16\u53f7')),
                ('c_type', models.IntegerField(verbose_name='\u7c7b\u578b', choices=[(1, b'\xe6\xb6\x88\xe8\xb4\xb9'), (2, b'\xe4\xba\xa4\xe6\x98\x93')])),
                ('unit_price', models.FloatField(null=True, verbose_name='\u6210\u4ea4\u5355\u4ef7', blank=True)),
                ('quantity', models.IntegerField(null=True, verbose_name='\u6210\u4ea4\u6570\u91cf', blank=True)),
                ('total', models.FloatField(null=True, verbose_name='\u6210\u4ea4\u91d1\u989d', blank=True)),
                ('commission_quantity', models.IntegerField(null=True, verbose_name='\u59d4\u6258\u6570\u91cf', blank=True)),
                ('created_date', models.DateField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_datetime', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4', db_index=True)),
                ('commission_buy_user_id', models.ForeignKey(related_name='trade_complete_buy_user', verbose_name='\u4e70\u65b9', to=settings.AUTH_USER_MODEL)),
                ('commission_sale_user_id', models.ForeignKey(related_name='trade_complete_sale_user', verbose_name='\u5356\u65b9', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(related_name='trade_complete_product', verbose_name='\u5546\u54c1', to='catalogue.Product')),
            ],
            options={
                'verbose_name': '\u6210\u4ea4\u8868',
                'verbose_name_plural': '\u6210\u4ea4\u8868',
            },
        ),
    ]
