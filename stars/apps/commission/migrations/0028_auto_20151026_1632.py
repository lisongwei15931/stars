# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0027_auto_20151026_1012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userassetdailyreport',
            name='can_out_amount',
            field=models.FloatField(default=0, null=True, verbose_name='\u53ef\u51fa\u8d44\u91d1', blank=True),
        ),
        migrations.AlterField(
            model_name='userassetdailyreport',
            name='can_use_amount',
            field=models.FloatField(default=0, null=True, verbose_name='\u53ef\u7528\u8d44\u91d1', blank=True),
        ),
        migrations.AlterField(
            model_name='userassetdailyreport',
            name='end_balance',
            field=models.FloatField(default=0, null=True, verbose_name='\u671f\u672b\u8d44\u91d1', blank=True),
        ),
        migrations.AlterField(
            model_name='userassetdailyreport',
            name='expenditure',
            field=models.FloatField(default=0, null=True, verbose_name='\u5f53\u65e5\u652f\u51fa', blank=True),
        ),
        migrations.AlterField(
            model_name='userassetdailyreport',
            name='income',
            field=models.FloatField(default=0, null=True, verbose_name='\u5f53\u65e5\u6536\u5165', blank=True),
        ),
        migrations.AlterField(
            model_name='userassetdailyreport',
            name='locked',
            field=models.FloatField(default=0, null=True, verbose_name='\u51bb\u7ed3\u8d44\u91d1', blank=True),
        ),
        migrations.AlterField(
            model_name='userassetdailyreport',
            name='market_capitalization',
            field=models.FloatField(default=0, null=True, verbose_name='\u6700\u65b0\u5e02\u503c', blank=True),
        ),
        migrations.AlterField(
            model_name='userassetdailyreport',
            name='profit_loss',
            field=models.FloatField(default=0, null=True, verbose_name='\u6d6e\u52a8\u76c8\u4e8f', blank=True),
        ),
        migrations.AlterField(
            model_name='userassetdailyreport',
            name='start_balance',
            field=models.FloatField(default=0, null=True, verbose_name='\u671f\u521d\u8d44\u91d1', blank=True),
        ),
        migrations.AlterField(
            model_name='userassetdailyreport',
            name='total',
            field=models.FloatField(default=0, null=True, verbose_name='\u8d44\u4ea7\u603b\u503c', blank=True),
        ),
    ]
