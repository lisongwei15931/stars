# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0035_auto_20151028_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockticker',
            name='volume',
            field=models.IntegerField(default=0, null=True, verbose_name='\u6210\u4ea4\u91cf', blank=True),
        ),
    ]
