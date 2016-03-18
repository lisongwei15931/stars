# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('address', '0003_receivingaddress'),
        ('commission', '0020_usermoneychange_parent_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='PickupList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pickup_no', models.CharField(max_length=15, null=True, verbose_name='\u63d0\u8d27\u7f16\u53f7', blank=True)),
                ('pickup_type', models.IntegerField(verbose_name='\u63d0\u8d27\u7c7b\u578b', choices=[(1, b'\xe8\x87\xaa\xe6\x8f\x90'), (2, b'\xe7\x89\xa9\xe6\xb5\x81')])),
                ('status', models.IntegerField(verbose_name='\u72b6\u6001', choices=[(1, b'\xe6\x9c\xaa\xe6\x8f\x90\xe8\xb4\xa7'), (2, b'\xe5\xb7\xb2\xe6\x8f\x90\xe8\xb4\xa7'), (3, b'\xe5\xb7\xb2\xe9\xa9\xb3\xe5\x9b\x9e')])),
                ('pickup_fee', models.FloatField(null=True, verbose_name='\u63d0\u8d27\u8d39\u7528', blank=True)),
                ('express_fee', models.FloatField(null=True, verbose_name='\u5feb\u9012\u8d39\u7528', blank=True)),
                ('refuse_desc', models.CharField(default=b'', max_length=1000, null=True, verbose_name='\u9a73\u56de\u539f\u56e0', blank=True)),
                ('deal_datetime', models.DateTimeField(null=True, verbose_name='\u529e\u7406\u65e5\u671f', blank=True)),
                ('created_date', models.DateField(auto_now_add=True, verbose_name='\u521b\u5efa\u65e5\u671f')),
                ('created_time', models.TimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_date', models.DateField(auto_now=True, verbose_name='\u4fee\u6539\u65e5\u671f')),
                ('modified_time', models.TimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('user', models.ForeignKey(related_name='pickup_list_user', verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
                ('user_address_id', models.ForeignKey(related_name='pickup_detail_user_addr', verbose_name='\u7528\u6237\u6536\u4ef6\u5730\u5740', blank=True, to='address.ReceivingAddress', null=True)),
                ('user_picked_id', models.ForeignKey(related_name='pickup_detail_pickup_addr', verbose_name='\u7528\u6237\u81ea\u63d0\u70b9', blank=True, to='commission.UserPickupAddr', null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='pickupdetail',
            name='deal_datetime',
        ),
        migrations.RemoveField(
            model_name='pickupdetail',
            name='pickup_no',
        ),
        migrations.RemoveField(
            model_name='pickupdetail',
            name='pickup_type',
        ),
        migrations.RemoveField(
            model_name='pickupdetail',
            name='refuse_desc',
        ),
        migrations.RemoveField(
            model_name='pickupdetail',
            name='status',
        ),
        migrations.RemoveField(
            model_name='pickupdetail',
            name='trade_no',
        ),
        migrations.RemoveField(
            model_name='pickupdetail',
            name='user',
        ),
        migrations.RemoveField(
            model_name='pickupdetail',
            name='user_address_id',
        ),
        migrations.RemoveField(
            model_name='pickupdetail',
            name='user_picked_id',
        ),
        migrations.RemoveField(
            model_name='usermoneychange',
            name='unlock_quantity',
        ),
        migrations.AddField(
            model_name='pickupdetail',
            name='pickup_list_id',
            field=models.ForeignKey(related_name='pickup_lists_id', default=1, verbose_name='\u63d0\u8d27\u5355id', to='commission.PickupList'),
            preserve_default=False,
        ),
    ]
