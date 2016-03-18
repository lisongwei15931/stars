# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0062_auto_20151128_1149'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockproductconfig',
            name='opening_date',
        ),
    ]
