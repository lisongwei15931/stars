# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0040_auto_20151102_1457'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockproductconfig',
            name='ower',
        ),
    ]
