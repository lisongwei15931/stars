# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0004_auto_20151111_1645'),
        ('commission', '0087_productorder_pickup_addr'),
    ]

    operations = [
        migrations.AddField(
            model_name='productorder',
            name='receive_addr',
            field=models.ForeignKey(related_name='order_receive_addr', verbose_name='\u6536\u8d27\u5730\u5740', blank=True, to='address.ReceivingAddress', null=True),
        ),
    ]
