# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0055_auto_20151113_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockproductconfig',
            name='product',
            field=models.OneToOneField(related_name='stock_config_product', verbose_name='\u5546\u54c1', to='catalogue.Product'),
        ),
        migrations.AlterField(
            model_name='userbalance',
            name='user',
            field=models.OneToOneField(related_name='balance_user', verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL),
        ),
    ]
