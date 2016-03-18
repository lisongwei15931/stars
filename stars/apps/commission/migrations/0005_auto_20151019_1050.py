# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalogue', '0008_auto_20150924_1125'),
        ('address', '0003_receivingaddress'),
        ('commission', '0004_auto_20151017_1621'),
    ]

    operations = [
        migrations.CreateModel(
            name='PickupDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pickup_no', models.CharField(max_length=15, null=True, verbose_name='\u63d0\u8d27\u7f16\u53f7', blank=True)),
                ('trade_no', models.CharField(max_length=15, null=True, verbose_name='\u6210\u4ea4\u7f16\u53f7', blank=True)),
                ('pickup_type', models.IntegerField(verbose_name='\u63d0\u8d27\u7c7b\u578b', choices=[(1, b'\xe8\x87\xaa\xe6\x8f\x90'), (2, b'\xe7\x89\xa9\xe6\xb5\x81')])),
                ('status', models.IntegerField(verbose_name='\u72b6\u6001', choices=[(1, b'\xe6\x9c\xaa\xe5\x8f\x91\xe8\xb4\xa7'), (2, b'\xe5\xb7\xb2\xe5\x8f\x91\xe8\xb4\xa7'), (3, b'\xe5\xb7\xb2\xe9\xa9\xb3\xe5\x9b\x9e')])),
                ('quantity', models.IntegerField(default=0, null=True, verbose_name='\u63d0\u8d27\u6570\u91cf', blank=True)),
                ('unit_price', models.FloatField(null=True, verbose_name='\u5355\u4ef7', blank=True)),
                ('pickup_fee', models.FloatField(null=True, verbose_name='\u63d0\u8d27\u8d39\u7528', blank=True)),
                ('refuse_desc', models.CharField(default=b'', max_length=1000, null=True, verbose_name='\u9a73\u56de\u539f\u56e0', blank=True)),
                ('deal_datetime', models.DateTimeField(null=True, verbose_name='\u529e\u7406\u65e5\u671f', blank=True)),
                ('created_date', models.DateField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('created_time', models.TimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_date', models.DateField(auto_now_add=True, verbose_name='\u4fee\u6539\u65e5\u671f')),
                ('modified_time', models.TimeField(auto_now_add=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('product', models.ForeignKey(related_name='pickup_detail_product', verbose_name='\u5546\u54c1', blank=True, to='catalogue.Product', null=True)),
                ('user', models.ForeignKey(related_name='pickup_detail_user', verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
                ('user_address_id', models.ForeignKey(related_name='pickup_detail_user_addr', verbose_name='\u7528\u6237\u6536\u4ef6\u5730\u5740', blank=True, to='address.ReceivingAddress', null=True)),
                ('user_picked_id', models.ForeignKey(related_name='pickup_detail_pickup_addr', verbose_name='\u7528\u6237\u81ea\u63d0\u70b9', blank=True, to='commission.UserPickupAddr', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='commissionbuy',
            name='user_picked_id',
            field=models.ForeignKey(related_name='commission_buy_pickup_addr', verbose_name='\u81ea\u63d0\u70b9', blank=True, to='commission.UserPickupAddr', null=True),
        ),
        migrations.AddField(
            model_name='commissionbuybackup',
            name='user_picked_id',
            field=models.ForeignKey(related_name='commission_buy_backup_pickup_addr', verbose_name='\u81ea\u63d0\u70b9', blank=True, to='commission.UserPickupAddr', null=True),
        ),
    ]
