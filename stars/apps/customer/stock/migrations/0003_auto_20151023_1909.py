# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0002_auto_20151022_1042'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickupprovisionalrecord',
            name='pickup_type',
            field=models.IntegerField(default=1, verbose_name='\u63d0\u8d27\u7c7b\u578b', choices=[(1, b'\xe6\xb6\x88\xe8\xb4\xb9'), (2, b'\xe8\xbf\x9b\xe8\xb4\xa7'), (3, b'\xe5\x85\xa8\xe9\x83\xa8')]),
        ),
        migrations.AlterField(
            model_name='pickupprovisionalrecord',
            name='quantity',
            field=models.IntegerField(default=1, verbose_name='\u63d0\u8d27\u6570\u91cf'),
        ),
    ]
