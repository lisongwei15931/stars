# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0003_receivingaddress'),
        ('commission', '0009_auto_20151019_1818'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickupaddr',
            name='district',
            field=models.ForeignKey(related_name='pickup_addr_district', verbose_name='\u533a/\u53bf', blank=True, to='address.District', null=True),
        ),
    ]
