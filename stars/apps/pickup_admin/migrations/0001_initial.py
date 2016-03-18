# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0003_auto_20150604_1450'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('commission', '0045_auto_20151106_1042'),
        ('catalogue', '0011_product_product_long_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='PickupStore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(null=True, verbose_name='\u6570\u91cf', blank=True)),
                ('desc', models.CharField(max_length=256, null=True, verbose_name='\u5907\u6ce8', blank=True)),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_datetime', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('pickup_addr', models.ForeignKey(verbose_name='\u63d0\u8d27\u70b9', to='commission.PickupAddr')),
                ('product', models.ForeignKey(verbose_name='\u5546\u54c1', to='catalogue.Product')),
            ],
            options={
                'verbose_name': '\u5e93\u5b58\u8868',
                'verbose_name_plural': '\u5e93\u5b58\u8868',
            },
        ),
        migrations.CreateModel(
            name='StoreInCome',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('c_quantity', models.IntegerField(null=True, verbose_name='\u4ef6\u6570', blank=True)),
                ('quantity', models.IntegerField(null=True, verbose_name='\u6570\u91cf', blank=True)),
                ('product_brand', models.CharField(max_length=128, null=True, verbose_name='\u5546\u54c1\u54c1\u724c', blank=True)),
                ('product_company', models.CharField(max_length=128, null=True, verbose_name='\u5546\u54c1\u751f\u4ea7\u5382\u5bb6', blank=True)),
                ('place_of_origin', models.CharField(max_length=128, null=True, verbose_name='\u5546\u54c1\u4ea7\u5730', blank=True)),
                ('producttion_date', models.DateField(null=True, verbose_name='\u5546\u54c1\u751f\u4ea7\u65e5\u671f', blank=True)),
                ('warehouse_rental_start_time', models.DateField(null=True, verbose_name='\u4ed3\u79df\u5f00\u59cb\u65e5\u671f', blank=True)),
                ('place', models.CharField(max_length=32, null=True, verbose_name='\u5e93\u4f4d', blank=True)),
                ('les_space', models.CharField(max_length=32, null=True, verbose_name='\u4ed3\u4f4d', blank=True)),
                ('inspect_orig', models.CharField(max_length=128, null=True, verbose_name='\u68c0\u6d4b\u673a\u6784', blank=True)),
                ('inspect_cert', models.CharField(max_length=64, null=True, verbose_name='\u8d28\u68c0\u8bc1\u4e66\u7f16\u53f7', blank=True)),
                ('inspect_expert', models.CharField(max_length=64, null=True, verbose_name='\u8d28\u68c0\u4e13\u5bb6', blank=True)),
                ('vouch_company', models.CharField(max_length=128, null=True, verbose_name='\u4fdd\u9669\u516c\u53f8', blank=True)),
                ('desc', models.CharField(max_length=256, null=True, verbose_name='\u5907\u6ce8', blank=True)),
                ('income_date', models.DateField(auto_now_add=True, verbose_name='\u5165\u5e93\u65e5\u671f')),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_datetime', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('isp', models.ForeignKey(verbose_name='\u4ea4\u6613\u5546', to='partner.Partner')),
                ('pickup_addr', models.ForeignKey(verbose_name='\u63d0\u8d27\u70b9', to='commission.PickupAddr')),
                ('product', models.ForeignKey(verbose_name='\u5546\u54c1', to='catalogue.Product')),
            ],
            options={
                'verbose_name': '\u4ed3\u5e93\u5165\u5e93\u8868',
                'verbose_name_plural': '\u4ed3\u5e93\u5165\u5e93\u8868',
            },
        ),
        migrations.CreateModel(
            name='StoreInComeApply',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('c_quantity', models.IntegerField(null=True, verbose_name='\u4ef6\u6570', blank=True)),
                ('quantity', models.IntegerField(null=True, verbose_name='\u6570\u91cf', blank=True)),
                ('product_brand', models.CharField(max_length=128, null=True, verbose_name='\u5546\u54c1\u54c1\u724c', blank=True)),
                ('plan_income_date', models.DateField(null=True, verbose_name='\u8ba1\u5212\u5165\u5e93\u65e5\u671f', blank=True)),
                ('apply_date', models.DateField(null=True, verbose_name='\u7533\u8bf7\u65e5\u671f', blank=True)),
                ('telephone', models.CharField(max_length=32, verbose_name='\u8054\u7cfb\u7535\u8bdd')),
                ('desc', models.CharField(max_length=256, null=True, verbose_name='\u5907\u6ce8', blank=True)),
                ('status', models.CharField(default=b'1', max_length=16, verbose_name='\u6279\u590d\u72b6\u6001', choices=[(b'1', '\u672a\u5ba1\u6838'), (b'2', '\u5df2\u9a73\u56de'), (b'3', '\u4ed3\u5e93\u5df2\u5ba1\u6838'), (b'4', '\u5df2\u5165\u5e93')])),
                ('deal_datetime', models.DateTimeField(null=True, verbose_name='\u6279\u590d\u65f6\u95f4', blank=True)),
                ('refuse_desc', models.CharField(max_length=256, null=True, verbose_name='\u9a73\u56de\u539f\u56e0', blank=True)),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_datetime', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('deal_user', models.ForeignKey(verbose_name='\u6279\u590d\u4eba', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('isp', models.ForeignKey(verbose_name='\u4ea4\u6613\u5546', to='partner.Partner')),
                ('pickup_addr', models.ForeignKey(verbose_name='\u63d0\u8d27\u70b9', to='commission.PickupAddr')),
                ('product', models.ForeignKey(verbose_name='\u5546\u54c1', to='catalogue.Product')),
            ],
            options={
                'verbose_name': '\u5165\u5e93\u7533\u8bf7\u6279\u590d\u8868',
                'verbose_name_plural': '\u5165\u5e93\u7533\u8bf7\u6279\u590d\u8868',
            },
        ),
    ]
