# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0003_receivingaddress'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='lat',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u7eac\u5ea6', blank=True),
        ),
        migrations.AddField(
            model_name='city',
            name='lng',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u7ecf\u5ea6', blank=True),
        ),
        migrations.AddField(
            model_name='district',
            name='lat',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u7eac\u5ea6', blank=True),
        ),
        migrations.AddField(
            model_name='district',
            name='lng',
            field=models.FloatField(default=0, max_length=15, null=True, verbose_name='\u7ecf\u5ea6', blank=True),
        ),
    ]
