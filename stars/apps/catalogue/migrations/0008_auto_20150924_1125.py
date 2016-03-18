# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0007_auto_20150923_1742'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='featured_hot',
            field=models.BooleanField(default=False, verbose_name='\u4e3b\u63a8\u70ed\u5356'),
        ),
        migrations.AddField(
            model_name='product',
            name='hot_deals',
            field=models.BooleanField(default=False, verbose_name='\u706b\u70ed\u4fc3\u9500'),
        ),
        migrations.AddField(
            model_name='product',
            name='new_listing',
            field=models.BooleanField(default=False, verbose_name='\u65b0\u54c1\u4e0a\u5e02'),
        ),
        migrations.AddField(
            model_name='product',
            name='selection_reputation',
            field=models.BooleanField(default=False, verbose_name='\u53e3\u7891\u7504\u9009'),
        ),
    ]
