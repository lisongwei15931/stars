# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0048_auto_20151110_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commissionbuy',
            name='commission_no',
            field=models.CharField(unique=True, max_length=255, verbose_name='\u59d4\u6258\u7f16\u53f7'),
        ),
        migrations.AlterField(
            model_name='commissionbuybackup',
            name='commission_no',
            field=models.CharField(max_length=255, verbose_name='\u59d4\u6258\u7f16\u53f7'),
        ),
        migrations.AlterField(
            model_name='commissionsale',
            name='commission_no',
            field=models.CharField(unique=True, max_length=255, verbose_name='\u59d4\u6258\u7f16\u53f7'),
        ),
        migrations.AlterField(
            model_name='commissionsalebackup',
            name='commission_no',
            field=models.CharField(max_length=255, verbose_name='\u59d4\u6258\u7f16\u53f7'),
        ),
        migrations.AlterField(
            model_name='pickupdetail',
            name='logistics_company',
            field=models.CharField(max_length=255, null=True, verbose_name='\u7269\u6d41\u516c\u53f8', blank=True),
        ),
        migrations.AlterField(
            model_name='pickupdetail',
            name='user_address',
            field=models.CharField(max_length=255, null=True, verbose_name='\u7528\u6237\u6536\u4ef6\u5730\u5740', blank=True),
        ),
        migrations.AlterField(
            model_name='pickuplist',
            name='logistics_company',
            field=models.CharField(max_length=255, null=True, verbose_name='\u7269\u6d41\u516c\u53f8', blank=True),
        ),
        migrations.AlterField(
            model_name='stockticker',
            name='product_name',
            field=models.CharField(max_length=255, verbose_name='\u5546\u54c1\u540d\u79f0'),
        ),
        migrations.AlterField(
            model_name='stockticker',
            name='product_symbol',
            field=models.CharField(max_length=255, verbose_name='\u5546\u54c1\u4ee3\u7801'),
        ),
        migrations.AlterField(
            model_name='tradecomplete',
            name='commission_buy_no',
            field=models.CharField(max_length=255, verbose_name='\u59d4\u6258\u4e70\u7f16\u53f7'),
        ),
        migrations.AlterField(
            model_name='tradecomplete',
            name='commission_sale_no',
            field=models.CharField(max_length=255, verbose_name='\u59d4\u6258\u5356\u7f16\u53f7'),
        ),
        migrations.AlterField(
            model_name='tradecomplete',
            name='trade_no',
            field=models.CharField(unique=True, max_length=255, verbose_name='\u6210\u4ea4\u7f16\u53f7'),
        ),
        migrations.AlterField(
            model_name='userbank',
            name='bank_account',
            field=models.CharField(max_length=255, verbose_name='\u94f6\u884c\u8d26\u53f7'),
        ),
        migrations.AlterField(
            model_name='userbank',
            name='bank_name',
            field=models.CharField(max_length=255, verbose_name='\u94f6\u884c\u540d'),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='commission_buy_no',
            field=models.CharField(max_length=255, null=True, verbose_name='\u59d4\u6258\u4e70\u7f16\u53f7', blank=True),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='commission_sale_no',
            field=models.CharField(max_length=255, null=True, verbose_name='\u59d4\u6258\u5356\u7f16\u53f7', blank=True),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='money_bank',
            field=models.CharField(max_length=255, null=True, verbose_name='\u94f6\u884c', blank=True),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='pickup_detail_id',
            field=models.CharField(max_length=255, null=True, verbose_name='\u63d0\u8d27\u660e\u7ec6ID', blank=True),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='price',
            field=models.FloatField(max_length=255, verbose_name='\u4ef7\u683c'),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='trade_no',
            field=models.CharField(max_length=255, null=True, verbose_name='\u6210\u4ea4\u7f16\u53f7', blank=True),
        ),
    ]
