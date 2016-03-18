# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0059_auto_20151120_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockproductconfig',
            name='self_pick_or_express',
            field=models.IntegerField(default=1, verbose_name='\u81ea\u63d0\u6216\u7269\u6d41', choices=[(1, b'\xe4\xbb\x85\xe8\x87\xaa\xe6\x8f\x90'), (2, b'\xe4\xbb\x85\xe7\x89\xa9\xe6\xb5\x81'), (3, b'\xe8\x87\xaa\xe6\x8f\x90\xe5\x92\x8c\xe7\x89\xa9\xe6\xb5\x81')]),
        ),
    ]
