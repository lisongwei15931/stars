# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0033_systemconfig_auto_open'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemconfig',
            name='is_open',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u5f00\u5e02'),
        ),
    ]
