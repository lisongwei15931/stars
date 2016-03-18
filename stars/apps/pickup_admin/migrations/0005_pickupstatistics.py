# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0056_auto_20151113_1416'),
        ('catalogue', '0013_productattribute_index'),
        ('pickup_admin', '0004_auto_20151116_1442'),
    ]

    operations = [
        migrations.CreateModel(
            name='PickupStatistics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(null=True, verbose_name='\u6570\u91cf', blank=True)),
                ('pickup_type', models.IntegerField(default=1, verbose_name='\u63d0\u8d27\u7c7b\u578b', choices=[(b'1', b'\xe8\x87\xaa\xe6\x8f\x90'), (b'2', b'\xe8\x87\xaa\xe6\x8f\x90\xe7\x82\xb9\xe4\xbb\xa3\xe8\xbf\x90')])),
                ('pickup_addr', models.ForeignKey(verbose_name='\u63d0\u8d27\u70b9', to='commission.PickupAddr')),
                ('product', models.ForeignKey(verbose_name='\u5546\u54c1', to='catalogue.Product')),
            ],
            options={
                'verbose_name': '\u63d0\u8d27\u7edf\u8ba1\u8868',
                'verbose_name_plural': '\u63d0\u8d27\u7edf\u8ba1\u8868',
            },
        ),
    ]
