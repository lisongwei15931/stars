# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0004_auto_20151111_1645'),
        ('catalogue', '0013_productattribute_index'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('commission', '0056_auto_20151113_1416'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPickupCity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('city_name', models.CharField(default=b'', max_length=100, null=True, verbose_name='\u57ce\u5e02\u540d\u79f0', blank=True)),
                ('city', models.ForeignKey(related_name='pickup_city', verbose_name='\u57ce\u5e02', blank=True, to='address.City', null=True)),
                ('product', models.ForeignKey(related_name='pickup_city_product', verbose_name='\u5546\u54c1', blank=True, to='catalogue.Product', null=True)),
                ('user', models.ForeignKey(related_name='pickup_city_user', verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='stockproductconfig',
            name='distribution_pickup_addr',
            field=models.ManyToManyField(related_name='stock_config_distribution_pickup_addr', verbose_name='\u94fa\u8d27\u63d0\u8d27\u70b9\u4ed3\u5e93', to='commission.PickupAddr', blank=True),
        ),
        migrations.AlterField(
            model_name='stockproductconfig',
            name='pickup_addr',
            field=models.ManyToManyField(related_name='stock_config_pickup_addr', verbose_name='\u63d0\u8d27\u70b9\u4ed3\u5e93', to='commission.PickupAddr', blank=True),
        ),
    ]
