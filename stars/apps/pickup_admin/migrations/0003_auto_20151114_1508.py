# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pickup_admin', '0002_auto_20151111_1412'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickupstore',
            name='locked_quantity',
            field=models.IntegerField(default=0, null=True, verbose_name='\u51bb\u7ed3\u6570\u91cf', blank=True),
        ),
        migrations.AlterField(
            model_name='pickupstore',
            name='quantity',
            field=models.IntegerField(default=0, null=True, verbose_name='\u6570\u91cf', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='pickupstore',
            unique_together=set([('pickup_addr', 'product')]),
        ),
    ]
