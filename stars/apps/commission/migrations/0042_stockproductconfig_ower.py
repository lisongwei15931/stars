# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('commission', '0041_remove_stockproductconfig_ower'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockproductconfig',
            name='ower',
            field=models.ForeignKey(related_name='stock_config_ower', verbose_name='\u53d1\u884c\u4ea4\u6613\u5546', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
