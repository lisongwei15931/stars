# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0051_auto_20151112_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockproductconfig',
            name='self_pick_or_express',
            field=models.IntegerField(default=1, verbose_name='\u81ea\u63d0\u6216\u7269\u6d41', choices=[(1, b'\xe8\x87\xaa\xe6\x8f\x90'), (2, b'\xe7\x89\xa9\xe6\xb5\x81')]),
        ),
    ]
