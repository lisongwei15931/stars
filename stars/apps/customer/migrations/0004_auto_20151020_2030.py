# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0003_incomelog'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incomelog',
            name='user',
        ),
        migrations.DeleteModel(
            name='IncomeLog',
        ),
    ]
