# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0023_auto_20151024_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userproduct',
            name='total',
            field=models.FloatField(default=0, null=True, verbose_name='\u603b\u989d', blank=True),
        ),
    ]
