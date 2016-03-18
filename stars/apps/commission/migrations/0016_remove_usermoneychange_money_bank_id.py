# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0015_auto_20151023_1120'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usermoneychange',
            name='money_bank_id',
        ),
    ]
