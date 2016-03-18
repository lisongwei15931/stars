# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0007_auto_20151019_1432'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockproductconfig',
            name='pickup_price',
        ),
        migrations.AlterField(
            model_name='pickupdetail',
            name='status',
            field=models.IntegerField(verbose_name='\u72b6\u6001', choices=[(1, b'\xe6\x9c\xaa\xe6\x8f\x90\xe8\xb4\xa7'), (2, b'\xe5\xb7\xb2\xe6\x8f\x90\xe8\xb4\xa7'), (3, b'\xe5\xb7\xb2\xe9\xa9\xb3\xe5\x9b\x9e')]),
        ),
    ]
