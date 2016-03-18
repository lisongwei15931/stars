# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0011_product_product_long_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('commission', '0045_auto_20151106_1042'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoreInComeApply',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('product', models.CharField(max_length=100, verbose_name='\u5546\u54c1\u7f16\u53f7')),
                ('c_quantity', models.IntegerField(default=1, verbose_name='\u4ef6\u6570')),
                ('quantity', models.IntegerField(default=1, verbose_name='\u6570\u91cf')),
                ('product_band', models.CharField(max_length=100, null=True, verbose_name='\u54c1\u724c', blank=True)),
                ('plan_income_date', models.DateField(verbose_name='\u8ba1\u5212\u5165\u5e93\u65e5\u671f')),
                ('apply_date', models.DateField(auto_now_add=True, verbose_name='\u7533\u8bf7\u65e5\u671f')),
                ('tel', models.CharField(max_length=100, null=True, verbose_name='\u8054\u7cfb\u7535\u8bdd', blank=True)),
                ('desc', models.CharField(max_length=300, null=True, verbose_name='\u9644\u5c5e\u8bf4\u660e', blank=True)),
                ('status', models.CharField(default=b'1', max_length=2, verbose_name='\u6279\u590d\u72b6\u6001', choices=[(b'1', '\u672a\u5ba1\u6838'), (b'2', b'\xe5\xb7\xb2\xe9\xa9\xb3\xe5\x9b\x9e'), (b'3', '\u4ed3\u5e93\u5df2\u5ba1\u6838'), (b'4', '\u5df2\u5165\u5e93')])),
                ('deal_datetime', models.DateTimeField(null=True, verbose_name='\u6279\u590d\u65f6\u95f4', blank=True)),
                ('refuse_desc', models.CharField(max_length=300, verbose_name='\u9a73\u56de\u539f\u56e0')),
                ('create_datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_datetime', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('category', models.ForeignKey(related_name='category_store', verbose_name='\u5546\u54c1\u5927\u7c7b', to='catalogue.Category')),
                ('deal_user_id', models.ForeignKey(related_name='user_deal', verbose_name='\u6279\u590d\u4eba', to=settings.AUTH_USER_MODEL)),
                ('pickup', models.ManyToManyField(related_name='pickupaddr_store', verbose_name='\u81ea\u63d0\u70b9', to='commission.PickupAddr')),
                ('user', models.ForeignKey(related_name='user_store', verbose_name='\u5546\u5bb6\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u5165\u5e93\u7533\u8bf7\u6279\u590d\u8868',
                'verbose_name_plural': '\u5165\u5e93\u7533\u8bf7\u6279\u590d\u8868',
            },
        ),
    ]
