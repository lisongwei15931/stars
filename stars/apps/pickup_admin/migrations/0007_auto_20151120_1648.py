# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pickup_admin', '0006_auto_20151116_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storeincomeapply',
            name='damaged_quantity',
            field=models.IntegerField(default=0, null=True, verbose_name='\u7834\u635f\u6570\u91cf', blank=True),
        ),
        migrations.AlterField(
            model_name='storeincomeapply',
            name='lose_quantity',
            field=models.IntegerField(default=0, null=True, verbose_name='\u4e22\u5931\u6570\u91cf', blank=True),
        ),
    ]
