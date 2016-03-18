# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0081_auto_20151222_1020'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderinfo',
            name='order_pickup_detail',
            field=models.ForeignKey(related_name='order_pickup_detail', verbose_name='\u63d0\u8d27\u5355\u8be6\u7ec6', blank=True, to='commission.PickupDetail', null=True),
        ),
    ]
