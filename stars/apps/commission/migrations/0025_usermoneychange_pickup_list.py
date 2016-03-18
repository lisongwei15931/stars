# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0024_auto_20151024_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermoneychange',
            name='pickup_list',
            field=models.ForeignKey(verbose_name='\u63d0\u8d27\u5355', blank=True, to='commission.PickupList', null=True),
        ),
    ]
