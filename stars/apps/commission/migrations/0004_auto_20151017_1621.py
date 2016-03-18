# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0003_auto_20151017_1515'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userbank',
            name='id_card_no',
        ),
        migrations.RemoveField(
            model_name='userbank',
            name='user_name',
        ),
        migrations.AlterField(
            model_name='pickupaddr',
            name='addr',
            field=models.CharField(default=b'', max_length=200, null=True, verbose_name='\u5730\u5740', blank=True),
        ),
        migrations.AlterField(
            model_name='pickupaddr',
            name='city',
            field=models.ForeignKey(related_name='pickup_addr_city', verbose_name='\u57ce\u5e02', blank=True, to='address.City', null=True),
        ),
        migrations.AlterField(
            model_name='pickupaddr',
            name='contact',
            field=models.CharField(default=b'', max_length=30, null=True, verbose_name='\u8054\u7cfb\u4eba', blank=True),
        ),
        migrations.AlterField(
            model_name='pickupaddr',
            name='desc',
            field=models.CharField(default=b'', max_length=1000, null=True, verbose_name='\u5907\u6ce8', blank=True),
        ),
        migrations.AlterField(
            model_name='pickupaddr',
            name='lat',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u7eac\u5ea6', blank=True),
        ),
        migrations.AlterField(
            model_name='pickupaddr',
            name='lng',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u7ecf\u5ea6', blank=True),
        ),
        migrations.AlterField(
            model_name='pickupaddr',
            name='province',
            field=models.ForeignKey(related_name='pickup_addr_province', verbose_name='\u7701', blank=True, to='address.Province', null=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='bcomm',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u4e70\u624b\u7eed\u8d39\u53c2\u6570', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='checked_user',
            field=models.CharField(default=b'', max_length=15, null=True, verbose_name='\u5ba1\u6279\u8005', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='close_price_time',
            field=models.IntegerField(default=0, null=True, verbose_name='\u6536\u76d8\u4ef7\u8ba1\u7b97\u65f6\u95f4', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='commcal_typedata',
            field=models.IntegerField(default=0, verbose_name='\u4ea4\u6613\u624b\u7eed\u8d39\u7c7b\u578b', choices=[(1, b'\xe5\xae\x9a\xe9\x87\x8f'), (2, b'\xe6\xaf\x94\xe4\xbe\x8b')]),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='delay_fee_rate',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u5ef6\u671f\u8865\u507f\u8d39\u7387', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='depositfee_rate',
            field=models.FloatField(default=0, null=True, verbose_name='\u6258\u7ba1\u8d39', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='desc',
            field=models.CharField(default=b'', max_length=1000, null=True, verbose_name='\u5907\u6ce8', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='hold_users_limit',
            field=models.IntegerField(default=0, null=True, verbose_name='\u6301\u6709\u4eba\u6570\u4e0a\u9650', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='interest',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u59d4\u6258\u8d39\u7387', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='mark_level',
            field=models.IntegerField(default=0, null=True, verbose_name='\u884c\u60c5\u6863\u4f4d', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='market_capitalization',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u5e02\u503c', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='max_dec_rate',
            field=models.FloatField(default=0, null=True, verbose_name='\u6700\u5927\u51cf\u6301\u6bd4\u4f8b', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='max_inc_rate',
            field=models.FloatField(default=0, null=True, verbose_name='\u6700\u5927\u589e\u6301\u6bd4\u4f8b', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='min_bnum',
            field=models.IntegerField(default=0, null=True, verbose_name='\u6700\u5c0f\u4e70\u7533\u62a5\u5355\u4f4d', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='min_pickup_num',
            field=models.IntegerField(default=0, null=True, verbose_name='\u6700\u5c0f\u63d0\u8d27\u91cf', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='min_price',
            field=models.FloatField(default=0, null=True, verbose_name='\u6700\u5c0f\u53d8\u52a8\u4ef7\u4f4d', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='min_price_deddigit',
            field=models.IntegerField(default=0, null=True, verbose_name='\u5c0f\u6570\u4f4d', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='min_snum',
            field=models.IntegerField(default=0, null=True, verbose_name='\u6700\u5c0f\u5356\u7533\u62a5\u5355\u4f4d', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='once_max_num',
            field=models.IntegerField(default=0, null=True, verbose_name='\u5355\u7b14\u6700\u5927\u4e0b\u5355\u91cf', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='opening_date',
            field=models.DateField(default=django.utils.timezone.now, null=True, verbose_name='\u4e0a\u5e02\u65f6\u95f4', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='opening_price',
            field=models.FloatField(default=0, null=True, verbose_name='\u4e0a\u5e02\u4ef7\u683c', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='ower',
            field=models.CharField(default=b'', max_length=15, null=True, verbose_name='\u53d1\u884c\u4ea4\u6613\u5546', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='pickup_bait',
            field=models.FloatField(default=0, null=True, verbose_name='\u63d0\u53d6\u4fdd\u969c\u91d1(%)', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='pickup_price',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u63d0\u8d27\u8d39\u7528', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='quote',
            field=models.IntegerField(default=0, null=True, verbose_name='\u8fdb\u8d27\u6743', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='safefee_rate',
            field=models.FloatField(default=0, null=True, verbose_name='\u65e5\u4fdd\u9669\u8d39\u6807\u51c6', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='scomm',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u5356\u624b\u7eed\u8d39\u53c2\u6570', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='st_unit',
            field=models.CharField(default=b'', max_length=15, null=True, verbose_name='\u4ed3\u50a8\u8d39\u8ba1\u8d39\u5355\u4f4d', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='strate',
            field=models.FloatField(default=0, null=True, verbose_name='\u4ed3\u50a8\u8d39\u7387', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='trade_unit',
            field=models.CharField(default=b'', max_length=15, null=True, verbose_name='\u4ea4\u6613\u5355\u4f4d', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='ud_down_range',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u8dcc\u5e45\u53c2\u6570', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='ud_sty',
            field=models.IntegerField(default=0, verbose_name='\u6da8\u8dcc\u8ba1\u7b97\u7c7b\u578b', choices=[(1, b'\xe5\xae\x9a\xe9\x87\x8f'), (2, b'\xe6\xaf\x94\xe4\xbe\x8b')]),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='ud_up_range',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u6da8\u5e45\u53c2\u6570', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='youhuirage',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u5f85\u8fd4\u6bd4\u4f8b', blank=True),
        ),
        migrations.AlterField(
            model_name='userbalance',
            name='balance',
            field=models.FloatField(default=0, max_length=30, null=True, verbose_name='\u4f59\u989d', blank=True),
        ),
        migrations.AlterField(
            model_name='userbalance',
            name='desc',
            field=models.CharField(default=b'', max_length=1000, null=True, verbose_name='\u5907\u6ce8', blank=True),
        ),
        migrations.AlterField(
            model_name='userbalance',
            name='locked',
            field=models.FloatField(default=0, max_length=30, null=True, verbose_name='\u51bb\u7ed3', blank=True),
        ),
        migrations.AlterField(
            model_name='userbank',
            name='desc',
            field=models.CharField(default=b'', max_length=1000, verbose_name='\u5907\u6ce8'),
        ),
        migrations.AlterField(
            model_name='userbank',
            name='tel',
            field=models.CharField(max_length=30, null=True, verbose_name='\u7535\u8bdd', blank=True),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='commission_buy_no',
            field=models.CharField(max_length=15, null=True, verbose_name='\u59d4\u6258\u4e70\u7f16\u53f7', blank=True),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='commission_sale_no',
            field=models.CharField(max_length=15, null=True, verbose_name='\u59d4\u6258\u5356\u7f16\u53f7', blank=True),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='commission_unit_price',
            field=models.FloatField(max_length=15, null=True, verbose_name='\u59d4\u6258\u4e70\u4ef7\u683c', blank=True),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='desc',
            field=models.CharField(default=b'', max_length=1000, null=True, verbose_name='\u5907\u6ce8', blank=True),
        ),
        migrations.AlterField(
            model_name='usermoneychange',
            name='product',
            field=models.ForeignKey(related_name='money_change_product', verbose_name='\u5546\u54c1', blank=True, to='catalogue.Product', null=True),
        ),
        migrations.AlterField(
            model_name='userpickupaddr',
            name='id_card_no',
            field=models.CharField(default=b'', max_length=30, null=True, verbose_name='\u8eab\u4efd\u8bc1', blank=True),
        ),
        migrations.AlterField(
            model_name='userpickupaddr',
            name='name',
            field=models.CharField(default=b'', max_length=15, null=True, verbose_name='\u540d\u5b57', blank=True),
        ),
        migrations.AlterField(
            model_name='userpickupaddr',
            name='plate_number',
            field=models.CharField(default=b'', max_length=30, null=True, verbose_name='\u8f66\u724c\u53f7', blank=True),
        ),
    ]
