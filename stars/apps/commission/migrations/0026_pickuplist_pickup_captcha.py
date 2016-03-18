# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0025_usermoneychange_pickup_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickuplist',
            name='pickup_captcha',
            field=models.CharField(default='11111111', max_length=16, verbose_name='\u63d0\u8d27\u9a8c\u8bc1\u7801'),
            preserve_default=False,
        ),
    ]
