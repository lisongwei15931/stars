# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0043_auto_20151103_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockproductconfig',
            name='pickup_addr',
            field=models.ManyToManyField(to='commission.PickupAddr', verbose_name='\u63d0\u8d27\u70b9\u4ed3\u5e93', blank=True),
        ),
    ]
