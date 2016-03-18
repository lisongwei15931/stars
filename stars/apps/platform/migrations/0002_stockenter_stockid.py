# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('platform', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockenter',
            name='stockid',
            field=models.CharField(max_length=25, null=True, verbose_name='\u5546\u5bb6\u5165\u5e93\u5355', blank=True),
        ),
    ]
