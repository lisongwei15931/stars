# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalogue', '0008_auto_20150924_1125'),
        ('commission', '0012_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAssetDailyReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('target_date', models.DateField(null=True, verbose_name='\u65e5\u671f', blank=True)),
                ('start_balance', models.FloatField(null=True, verbose_name='\u671f\u521d\u8d44\u91d1', blank=True)),
                ('income', models.FloatField(null=True, verbose_name='\u5f53\u65e5\u6536\u5165', blank=True)),
                ('expenditure', models.FloatField(null=True, verbose_name='\u5f53\u65e5\u652f\u51fa', blank=True)),
                ('end_balance', models.FloatField(null=True, verbose_name='\u671f\u672b\u8d44\u91d1', blank=True)),
                ('locked', models.FloatField(null=True, verbose_name='\u51bb\u7ed3\u8d44\u91d1', blank=True)),
                ('can_use_amount', models.FloatField(null=True, verbose_name='\u53ef\u7528\u8d44\u91d1', blank=True)),
                ('can_out_amount', models.FloatField(null=True, verbose_name='\u53ef\u51fa\u8d44\u91d1', blank=True)),
                ('profit_loss', models.FloatField(null=True, verbose_name='\u6d6e\u52a8\u76c8\u4e8f', blank=True)),
                ('market_catitalization', models.FloatField(null=True, verbose_name='\u6700\u65b0\u5e02\u503c', blank=True)),
                ('total', models.FloatField(null=True, verbose_name='\u8d44\u4ea7\u603b\u503c', blank=True)),
                ('created_date', models.DateField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('created_time', models.TimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_date', models.DateField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f')),
                ('modified_time', models.TimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('user', models.ForeignKey(related_name='daily_report_user', verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u7528\u6237\u8d44\u4ea7\u65e5\u62a5\u8868',
                'verbose_name_plural': '\u7528\u6237\u8d44\u4ea7\u65e5\u62a5\u8868',
            },
        ),
        migrations.CreateModel(
            name='UserProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trade_type', models.IntegerField(verbose_name='\u7c7b\u578b', choices=[(1, b'\xe6\xb6\x88\xe8\xb4\xb9'), (2, b'\xe8\xbf\x9b\xe8\xb4\xa7')])),
                ('quantity', models.IntegerField(default=0, null=True, verbose_name='\u4f59\u91cf', blank=True)),
                ('can_sale_quantity', models.IntegerField(default=0, null=True, verbose_name='\u53ef\u5356\u91cf', blank=True)),
                ('can_pickup_quantity', models.IntegerField(default=0, null=True, verbose_name='\u53ef\u63d0\u91cf', blank=True)),
                ('overage_unit_price', models.FloatField(null=True, verbose_name='\u5747\u4ef7', blank=True)),
                ('need_repayment_quantity', models.FloatField(null=True, verbose_name='\u9700\u8981\u8fd8\u6b3e\u6570\u91cf', blank=True)),
                ('need_repayment_amount', models.FloatField(null=True, verbose_name='\u9700\u8981\u8fd8\u6b3e\u91d1\u989d', blank=True)),
                ('quote_quantity', models.IntegerField(default=0, null=True, verbose_name='\u5269\u4f59\u8fdb\u8d27\u6743', blank=True)),
                ('created_date', models.DateField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('created_time', models.TimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_date', models.DateField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f')),
                ('modified_time', models.TimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('product', models.ForeignKey(related_name='user_product_product', verbose_name='\u5546\u54c1', blank=True, to='catalogue.Product', null=True)),
                ('user', models.ForeignKey(related_name='user_product_user', verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u7528\u6237\u6301\u6709\u8868',
                'verbose_name_plural': '\u7528\u6237\u6301\u6709\u8868',
            },
        ),
        migrations.RenameField(
            model_name='usermoneychange',
            old_name='commission_unit_price',
            new_name='commission_buy_unit_price',
        ),
        migrations.RemoveField(
            model_name='commissionbuy',
            name='user_picked_id',
        ),
        migrations.RemoveField(
            model_name='commissionbuybackup',
            name='user_picked_id',
        ),
        migrations.RemoveField(
            model_name='stockticker',
            name='market_capitalization',
        ),
        migrations.RemoveField(
            model_name='userpickupaddr',
            name='id_card_no',
        ),
        migrations.RemoveField(
            model_name='userpickupaddr',
            name='name',
        ),
        migrations.RemoveField(
            model_name='userpickupaddr',
            name='plate_number',
        ),
        migrations.RemoveField(
            model_name='userpickupaddr',
            name='tel',
        ),
        migrations.AddField(
            model_name='pickupaddr',
            name='category',
            field=models.CharField(default='', max_length=1000, verbose_name='\u7c7b\u578b'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stockproductconfig',
            name='pickup_price',
            field=models.FloatField(default=0, null=True, verbose_name='\u63d0\u8d27\u8d39\u7528', blank=True),
        ),
        migrations.AddField(
            model_name='tradecomplete',
            name='can_pickup_quantity',
            field=models.IntegerField(null=True, verbose_name='\u53ef\u63d0\u53d6\u6570\u91cf', blank=True),
        ),
        migrations.AddField(
            model_name='usermoneychange',
            name='cancel_quantity',
            field=models.FloatField(max_length=15, null=True, verbose_name='\u64a4\u5355\u6570\u91cf', blank=True),
        ),
        migrations.AddField(
            model_name='usermoneychange',
            name='cancel_unit_price',
            field=models.FloatField(null=True, verbose_name='\u64a4\u5355\u5355\u4ef7', blank=True),
        ),
        migrations.AddField(
            model_name='usermoneychange',
            name='commission_buy_quantity',
            field=models.IntegerField(null=True, verbose_name='\u59d4\u6258\u4e70\u6570\u91cf', blank=True),
        ),
        migrations.AddField(
            model_name='usermoneychange',
            name='commission_sale_quantity',
            field=models.IntegerField(null=True, verbose_name='\u59d4\u6258\u5356\u6570\u91cf', blank=True),
        ),
        migrations.AddField(
            model_name='usermoneychange',
            name='commission_sale_unit_price',
            field=models.FloatField(max_length=15, null=True, verbose_name='\u59d4\u6258\u5356\u4ef7\u683c', blank=True),
        ),
        migrations.AddField(
            model_name='usermoneychange',
            name='pickup_amount',
            field=models.FloatField(null=True, verbose_name='\u63d0\u8d27\u4ef7\u683c', blank=True),
        ),
        migrations.AddField(
            model_name='usermoneychange',
            name='unlock_quantity',
            field=models.FloatField(max_length=15, null=True, verbose_name='\u89e3\u51bb\u6570\u91cf', blank=True),
        ),
        migrations.AddField(
            model_name='userpickupaddr',
            name='is_default',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u9ed8\u8ba4'),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='status',
            field=models.IntegerField(db_index=True, verbose_name='\u72b6\u6001', choices=[(1, b'\xe8\xbf\x9b\xe8\xa1\x8c\xe4\xb8\xad'), (2, b'\xe6\x88\x90\xe5\x8a\x9f'), (3, b'\xe5\xa4\xb1\xe8\xb4\xa5')]),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='trade_type',
            field=models.IntegerField(db_index=True, verbose_name='\u7c7b\u578b', choices=[(1, b'\xe5\x85\x85\xe5\x80\xbc'), (2, b'\xe4\xbd\x93\xe7\x8e\xb0'), (3, b'\xe8\xb4\xad\xe4\xb9\xb0\xe5\x86\xbb\xe7\xbb\x93'), (4, b'\xe8\xb4\xad\xe4\xb9\xb0\xe8\xa7\xa3\xe5\x86\xbb'), (5, b'\xe8\xb4\xad\xe4\xb9\xb0\xe6\x88\x90\xe4\xba\xa4'), (6, b'\xe8\xbf\x9b\xe8\xb4\xa7\xe5\x86\xbb\xe7\xbb\x93'), (7, b'\xe8\xbf\x9b\xe8\xb4\xa7\xe8\xa7\xa3\xe5\x86\xbb'), (8, b'\xe8\xbf\x9b\xe8\xb4\xa7\xe6\x88\x90\xe4\xba\xa4'), (9, b'\xe5\x87\xba\xe5\x94\xae'), (10, b'\xe6\x8f\x90\xe8\xb4\xa7\xe5\x86\xbb\xe7\xbb\x93'), (11, b'\xe6\x8f\x90\xe8\xb4\xa7\xe9\xa9\xb3\xe5\x9b\x9e'), (12, b'\xe6\x8f\x90\xe8\xb4\xa7\xe5\xae\x8c\xe6\x88\x90'), (13, b'\xe6\x92\xa4\xe5\x8d\x95')]),
        ),
    ]
