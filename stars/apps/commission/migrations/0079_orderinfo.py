# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0017_product_is_associate'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('commission', '0078_systemconfig_buy_price_rate'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('product_num', models.IntegerField(default=0, verbose_name='\u5546\u54c1\u6570\u91cf')),
                ('price', models.FloatField(default=0, verbose_name='\u8ba2\u5355\u5546\u54c1\u4ef7\u683c')),
                ('product', models.ForeignKey(related_name='order_product', verbose_name='\u5546\u54c1', to='catalogue.Product')),
                ('product_order', models.ForeignKey(related_name='order_info', verbose_name='\u8ba2\u5355\u53f7', to='commission.ProductOrder')),
                ('user', models.ForeignKey(related_name='order_user', verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u8ba2\u5355\u4fe1\u606f',
                'verbose_name_plural': '\u8ba2\u5355\u4fe1\u606f',
            },
        ),
    ]
