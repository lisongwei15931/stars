# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0021_auto_20151024_1120'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproduct',
            name='total',
            field=models.FloatField(null=True, verbose_name='\u603b\u989d', blank=True),
        ),
    ]
