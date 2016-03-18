# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0013_productattribute_index'),
        ('tradingcenter', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='selfpick',
            name='product',
        ),
        migrations.AddField(
            model_name='selfpick',
            name='product',
            field=models.ManyToManyField(related_name='self_pick_product', verbose_name='\u5546\u54c1', to='catalogue.Product'),
        ),
        migrations.AlterField(
            model_name='selfpick',
            name='user',
            field=models.OneToOneField(related_name='self_pick_user', verbose_name='\u7528\u6237', to=settings.AUTH_USER_MODEL),
        ),
    ]
