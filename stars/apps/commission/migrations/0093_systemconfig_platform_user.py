# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0092_auto_20160108_1101'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemconfig',
            name='platform_user',
            field=models.CharField(default='stars', max_length=30, verbose_name='\u5e73\u53f0\u8d26\u6237\u7528\u6237\u540d'),
            preserve_default=False,
        ),
    ]
