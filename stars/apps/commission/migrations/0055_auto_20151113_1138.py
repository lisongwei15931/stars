# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0054_auto_20151113_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockproductconfig',
            name='product',
            field=models.ForeignKey(related_name='stock_config_product', verbose_name='\u5546\u54c1', to='catalogue.Product', unique=True),
        ),
        migrations.AlterField(
            model_name='userbalance',
            name='user',
            field=models.ForeignKey(related_name='balance_user', verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL, unique=True),
        ),
    ]
