# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0086_auto_20151224_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='productorder',
            name='pickup_addr',
            field=models.ForeignKey(related_name='order_pickup_addr', verbose_name='\u8ba2\u5355\u63d0\u8d27\u70b9', blank=True, to='commission.PickupAddr', null=True),
        ),
    ]
